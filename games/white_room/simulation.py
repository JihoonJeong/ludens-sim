"""White Room Simulation — Phase 1 (Empty Agora)"""

import random
import yaml
from pathlib import Path
from typing import Optional

from engine.adapters import create_adapter, BaseLLMAdapter, LLMResponse
from engine.core.logger import SimulationLogger, calculate_gini

from .agent import Agent, create_agents_from_config
from .actions import (
    can_perform_action, get_action_cost, speak_reward,
    ActionType, ALLEY_LOCATIONS, ARCHITECT_ACTIONS,
)
from .context import build_context_phase1, _format_recent_events
from .environment import Environment
from .history import HistoryEngine
from .systems.market import MarketPool, Treasury
from .systems.influence import InfluenceSystem
from .systems.support import SupportTracker
from .systems.whisper import WhisperSystem
from .systems.architect import ArchitectSystem


class WhiteRoomSimulation:

    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        sim_cfg = self.config["simulation"]
        game_cfg = self.config.get("game_mode", {})
        market_cfg = self.config.get("market", {})
        treasury_cfg = self.config.get("treasury", {})
        whisper_cfg = self.config.get("whisper", {})

        # Simulation parameters
        self.name = sim_cfg.get("name", "white_room")
        self.total_epochs = sim_cfg.get("total_epochs", 50)
        self.language = sim_cfg.get("language", "ko")
        seed = sim_cfg.get("random_seed")
        if seed is not None:
            random.seed(seed)

        # Game mode flags
        self.phase = game_cfg.get("phase", 1)
        self.energy_frozen = game_cfg.get("energy_frozen", True)
        self.energy_visible = game_cfg.get("energy_visible", True)
        self.market_shadow = game_cfg.get("market_shadow", True)
        self.whisper_leak_enabled = game_cfg.get("whisper_leak", True)

        # Agents
        self.agents: list[Agent] = create_agents_from_config(self.config["agents"])
        self.agents_by_id: dict[str, Agent] = {a.id: a for a in self.agents}

        # Adapters
        default_adapter_type = self.config.get("default_adapter", "mock")
        default_model = self.config.get("default_model", "mock")
        self.adapters: dict[str, BaseLLMAdapter] = {}
        for agent in self.agents:
            adapter_type = agent.adapter_type or default_adapter_type
            model = agent.model or default_model
            adapter_key = f"{adapter_type}:{model}:{agent.persona}:{agent.id}"
            self.adapters[agent.id] = create_adapter(
                adapter_type,
                model=model,
                persona=agent.persona,
                agent_id=agent.id,
            )

        # Environment
        self.environment = Environment(self.config.get("spaces", {
            "plaza": {"capacity": 12, "visibility": "public"},
            "market": {"capacity": 12, "visibility": "public"},
            "alley_a": {"capacity": 4, "visibility": "members_only"},
            "alley_b": {"capacity": 4, "visibility": "members_only"},
            "alley_c": {"capacity": 4, "visibility": "members_only"},
        }))
        self.environment.tax_rate = market_cfg.get("default_tax_rate", 0.1)

        # Place agents in initial locations
        for agent in self.agents:
            self.environment.place_agent(agent.id, agent.location)

        # Systems
        self.market_pool = MarketPool(
            spawn_per_epoch=market_cfg.get("spawn_per_epoch", 25),
            min_presence_reward=market_cfg.get("min_presence_reward", 2),
        )
        self.treasury = Treasury(
            initial=treasury_cfg.get("initial", 0),
            overflow_threshold=treasury_cfg.get("overflow_threshold", 100),
        )
        self.influence_system = InfluenceSystem()
        self.support_tracker = SupportTracker()
        self.whisper_system = WhisperSystem(
            base_leak_prob=whisper_cfg.get("base_leak_probability", 0.15),
            observer_bonus=whisper_cfg.get("observer_bonus", 0.35),
            enabled=self.whisper_leak_enabled,
        )
        self.architect_system = ArchitectSystem()
        self.history = HistoryEngine()

        # Logger — 프로젝트 루트의 logs/ 디렉토리 사용
        project_root = Path(__file__).parent.parent.parent
        self.logger = SimulationLogger(
            base_dir=str(project_root / "logs"),
            run_name=self.name,
        )
        self.logger.save_config(self.config)

        # Action log (for recent events in prompts)
        self.action_log: list[dict] = []
        self.epoch_trade_count = 0

    def run(self):
        print(f"=== {self.name} 시뮬레이션 시작 ===")
        print(f"Phase: {self.phase}, Epochs: {self.total_epochs}, Language: {self.language}")
        print(f"Energy frozen: {self.energy_frozen}, Market shadow: {self.market_shadow}")
        print(f"Agents: {len(self.agents)}")
        print(f"Log directory: {self.logger.run_dir}")
        print()

        for epoch in range(1, self.total_epochs + 1):
            self.run_epoch(epoch)

        self._finalize()

    def run_epoch(self, epoch: int):
        print(f"--- Epoch {epoch}/{self.total_epochs} ---")
        self.epoch_trade_count = 0
        self.logger.reset_turn_counter()

        # Shuffle agent order each epoch
        agents = list(self.agents)
        random.shuffle(agents)

        for agent in agents:
            self._execute_agent_turn(agent, epoch)

        # Post-epoch: market distribution
        market_agents = self.environment.get_agents_at("market")
        distribution = self.market_pool.distribute_pool(
            epoch, market_agents, self.environment.tax_rate
        )

        if not self.energy_frozen:
            for agent_id, amount in distribution["distribution"].items():
                if agent_id in self.agents_by_id:
                    self.agents_by_id[agent_id].gain_energy(amount)

        # Tax to treasury
        self.treasury.collect_tax(distribution["tax_collected"])

        # Treasury overflow
        overflow = self.treasury.check_overflow()

        # Billboard tick
        self.environment.tick_billboard()

        # Epoch summary
        energy_values = [a.energy for a in self.agents]
        self.logger.log_epoch_summary(
            epoch=epoch,
            agent_count=len(self.agents),
            energy_values=energy_values,
            transaction_count=self.epoch_trade_count,
            treasury=self.treasury.balance,
            billboard=self.environment.get_billboard(),
            extra={
                "market_distribution": distribution,
                "shadow_mode": self.energy_frozen,
                "treasury_overflow": overflow,
            },
        )

    def _execute_agent_turn(self, agent: Agent, epoch: int):
        resources_before = agent.resource_snapshot()

        # Build context
        context = self._build_agent_context(agent, epoch)

        # Get LLM response
        adapter = self.adapters[agent.id]
        response = adapter.generate(context, max_tokens=1000)

        # Execute action
        success, result = self._execute_action(agent, response, epoch)

        resources_after = agent.resource_snapshot()

        # Build log entry
        log_extra = {
            "shadow_mode": self.energy_frozen,
        }
        if "would_have_changed" in result:
            log_extra["would_have_changed"] = result["would_have_changed"]
        if "leaked" in result:
            log_extra["leaked"] = result["leaked"]
        if "new_rate" in result:
            log_extra["new_rate"] = result["new_rate"]

        # Log action
        self.logger.log_action(
            epoch=epoch,
            agent_id=agent.id,
            persona=agent.persona,
            location=agent.location,
            action_type=response.action,
            target=response.target,
            content=response.content,
            thought=response.thought,
            success=success,
            resources_before=resources_before,
            resources_after=resources_after,
            extra=log_extra,
        )

        # Add to action log for recent events
        self.action_log.append({
            "epoch": epoch,
            "agent_id": agent.id,
            "persona": agent.persona,
            "location": agent.location,
            "action_type": response.action,
            "target": response.target,
            "content": response.content,
            "success": success,
            **{k: v for k, v in result.items() if k in ("leaked", "new_rate")},
        })

    def _build_agent_context(self, agent: Agent, epoch: int) -> str:
        # Agents at same location
        agent_ids_here = self.environment.get_agents_at(agent.location)
        agents_here = []
        for aid in agent_ids_here:
            if aid == agent.id:
                continue
            other = self.agents_by_id.get(aid)
            if other:
                rank = self.influence_system.get_rank_name(other.influence, self.language)
                agents_here.append({"id": aid, "rank": rank})

        # Influence rank
        rank_name = self.influence_system.get_rank_name(agent.influence, self.language)
        rank_bonus = self.influence_system.get_rank_bonus_prompt(agent.influence, self.language)

        # Support context
        support_ctx = self.support_tracker.build_support_context(agent.id, self.language)

        # Gini
        energy_values = [a.energy for a in self.agents]
        gini = calculate_gini(energy_values)

        # Historical summary
        hist_summary = self.history.get_summary(max_events=10, lang=self.language)

        # Billboard
        billboard = self.environment.get_billboard()

        return build_context_phase1(
            agent_id=agent.id,
            persona=agent.persona,
            location=agent.location,
            energy=agent.energy,
            influence=agent.influence,
            rank_name=rank_name,
            rank_bonus_prompt=rank_bonus,
            support_context=support_ctx,
            epoch=epoch,
            agent_count=len(self.agents),
            gini=gini,
            tax_rate=self.environment.tax_rate,
            treasury=self.treasury.balance,
            recent_events=self.action_log,
            historical_summary=hist_summary,
            billboard_content=billboard,
            agents_here=agents_here,
            lang=self.language,
        )

    def _execute_action(self, agent: Agent, response: LLMResponse, epoch: int) -> tuple[bool, dict]:
        action = response.action
        target = response.target
        content = response.content

        # Validate action
        if not can_perform_action(action, agent.location, agent.persona):
            return False, {"error": f"invalid_action: {action} at {agent.location}"}

        if action == "speak":
            return self._action_speak(agent, content, epoch)
        elif action == "trade":
            return self._action_trade(agent, epoch)
        elif action == "support":
            return self._action_support(agent, target, epoch)
        elif action == "whisper":
            return self._action_whisper(agent, target, content, epoch)
        elif action == "move":
            return self._action_move(agent, target)
        elif action == "idle":
            return True, {}
        elif action == "build_billboard":
            return self._action_build_billboard(agent, content, epoch)
        elif action == "adjust_tax":
            return self._action_adjust_tax(agent, target, epoch)
        elif action == "grant_subsidy":
            return self._action_grant_subsidy(agent, target, content, epoch)
        else:
            return False, {"error": f"unknown_action: {action}"}

    def _action_speak(self, agent: Agent, content: Optional[str], epoch: int) -> tuple[bool, dict]:
        cost = get_action_cost("speak")
        agent.spend_energy(cost, frozen=self.energy_frozen)

        reward = speak_reward(agent.location)
        if reward > 0:
            agent.gain_energy(reward, frozen=self.energy_frozen)

        result = {"cost": cost, "reward": reward}
        if self.energy_frozen:
            result["would_have_changed"] = -cost + reward

        return True, result

    def _action_trade(self, agent: Agent, epoch: int) -> tuple[bool, dict]:
        cost = get_action_cost("trade")
        gross_reward = 4
        tax = gross_reward * self.environment.tax_rate
        net_reward = gross_reward - tax

        agent.spend_energy(cost, frozen=self.energy_frozen)
        agent.gain_energy(int(net_reward), frozen=self.energy_frozen)

        self.market_pool.record_trade(epoch, agent.id)
        self.epoch_trade_count += 1

        result = {
            "cost": cost,
            "gross_reward": gross_reward,
            "tax": tax,
            "net_reward": net_reward,
            "shadow": self.energy_frozen,
        }
        if self.energy_frozen:
            result["would_have_changed"] = -cost + int(net_reward)

        return True, result

    def _action_support(self, agent: Agent, target_id: Optional[str], epoch: int) -> tuple[bool, dict]:
        if not target_id or target_id not in self.agents_by_id:
            return False, {"error": "invalid_target"}

        target = self.agents_by_id[target_id]
        cost = get_action_cost("support")

        # Elder multiplier
        multiplier = self.influence_system.get_support_multiplier(agent.influence)
        energy_gift = int(2 * multiplier)

        agent.spend_energy(cost, frozen=self.energy_frozen)
        target.gain_energy(energy_gift, frozen=self.energy_frozen)
        target.gain_influence(1, frozen=self.energy_frozen)

        # Track support relationship (always, even if frozen)
        self.support_tracker.add_support(epoch, agent.id, target_id)

        # Check mutual support
        if agent.id in self.support_tracker.get_supported_by(target_id):
            self.history.add_mutual_support(epoch, agent.id, target_id)

        result = {
            "cost": cost,
            "energy_gift": energy_gift,
            "influence_gift": 1,
            "multiplier": multiplier,
        }
        if self.energy_frozen:
            result["would_have_changed"] = {
                "giver": -cost,
                "receiver_energy": energy_gift,
                "receiver_influence": 1,
            }

        return True, result

    def _action_whisper(
        self, agent: Agent, target_id: Optional[str],
        content: Optional[str], epoch: int,
    ) -> tuple[bool, dict]:
        if not target_id or target_id not in self.agents_by_id:
            return False, {"error": "invalid_target"}

        cost = get_action_cost("whisper")
        agent.spend_energy(cost, frozen=self.energy_frozen)

        # Whisper leak
        agents_here = self.environment.get_agents_at(agent.location)
        agent_personas = {a.id: a.persona for a in self.agents}
        whisper_result = self.whisper_system.process_whisper(
            agent.id, target_id, content or "",
            agents_here, agent_personas,
        )

        # Add suspicions
        if whisper_result.leaked:
            for bystander_id in whisper_result.suspicion_targets:
                if bystander_id in self.agents_by_id:
                    self.agents_by_id[bystander_id].add_suspicion(
                        epoch, agent.id, target_id,
                    )
            self.history.add_whisper_leak(epoch, agent.id, target_id)

        result = {
            "cost": cost,
            "leaked": whisper_result.leaked,
            "observers": whisper_result.observers,
        }
        if self.energy_frozen:
            result["would_have_changed"] = -cost

        return True, result

    def _action_move(self, agent: Agent, destination: Optional[str]) -> tuple[bool, dict]:
        if not destination or destination not in self.environment.spaces:
            return False, {"error": f"invalid_destination: {destination}"}

        if destination == agent.location:
            return True, {"already_here": True}

        old_location = agent.location
        moved = self.environment.move_agent(agent.id, old_location, destination)
        if moved:
            agent.move_to(destination)
            return True, {"from": old_location, "to": destination}
        return False, {"error": "space_full"}

    def _action_build_billboard(
        self, agent: Agent, content: Optional[str], epoch: int,
    ) -> tuple[bool, dict]:
        if agent.persona != "architect":
            return False, {"error": "not_architect"}

        success, result = self.architect_system.build_billboard(
            agent.energy, content or "공지", frozen=self.energy_frozen,
        )
        if success:
            agent.spend_energy(result["cost"], frozen=self.energy_frozen)
            self.environment.post_billboard(content or "공지", agent.id, result["duration"])
            self.history.add_billboard(epoch, agent.id, content or "공지")
            if self.energy_frozen:
                result["would_have_changed"] = -result["cost"]

        return success, result

    def _action_adjust_tax(
        self, agent: Agent, target: Optional[str], epoch: int,
    ) -> tuple[bool, dict]:
        if agent.persona != "architect":
            return False, {"error": "not_architect"}

        try:
            new_rate = float(target) if target else self.environment.tax_rate
            # 입력이 퍼센트(예: 15)인지 비율(예: 0.15)인지 판별
            if new_rate > 1:
                new_rate = new_rate / 100.0
        except (ValueError, TypeError):
            return False, {"error": "invalid_rate"}

        old_rate = self.environment.tax_rate
        success, result = self.architect_system.adjust_tax(
            agent.energy, new_rate, frozen=self.energy_frozen,
        )
        if success:
            agent.spend_energy(result["cost"], frozen=self.energy_frozen)
            self.environment.set_tax_rate(result["new_rate"])
            self.history.add_tax_change(epoch, agent.id, old_rate, result["new_rate"])
            if self.energy_frozen:
                result["would_have_changed"] = -result["cost"]

        return success, result

    def _action_grant_subsidy(
        self, agent: Agent, target_id: Optional[str],
        content: Optional[str], epoch: int,
    ) -> tuple[bool, dict]:
        if agent.persona != "architect":
            return False, {"error": "not_architect"}

        if not target_id or target_id not in self.agents_by_id:
            return False, {"error": "invalid_target"}

        try:
            amount = float(content) if content else 10.0
        except (ValueError, TypeError):
            amount = 10.0

        success, result = self.architect_system.grant_subsidy(
            self.treasury.balance, amount, target_id,
        )
        if success:
            self.treasury.grant_subsidy(amount)
            target = self.agents_by_id[target_id]
            target.gain_energy(int(amount), frozen=self.energy_frozen)
            self.history.add_subsidy(epoch, agent.id, target_id, amount)

        return success, result

    def _finalize(self):
        print()
        print(f"=== 시뮬레이션 완료 ===")
        print(f"총 {self.total_epochs} 에폭, {len(self.action_log)} 행동 기록")
        print(f"로그 저장 위치: {self.logger.run_dir}")

        # Final energy distribution
        for agent in sorted(self.agents, key=lambda a: a.energy, reverse=True):
            rank = self.influence_system.get_rank_name(agent.influence, "ko")
            print(f"  {agent.id}: E={agent.energy} I={agent.influence} ({rank})")
