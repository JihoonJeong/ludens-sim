"""White Room Simulation — Phase 1 (Empty Agora) + Phase 2 (Enriched Neutral)"""

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
from .context import (
    build_context_phase1, build_context_phase2,
    build_system_prompt_v03, build_turn_prompt_v03,
)
from .personas import get_constraint_level
from .environment import Environment
from .history import HistoryEngine
from .systems.market import MarketPool, Treasury
from .systems.influence import InfluenceSystem
from .systems.support import SupportTracker
from .systems.whisper import WhisperSystem
from .systems.architect import ArchitectSystem

# Phase 2 action validation — speak/trade/rest/move only
PHASE2_VALID_ACTIONS = {"speak", "trade", "rest", "move"}


def _can_perform_action_phase2(action_str: str, location: str) -> bool:
    """Phase 2 행동 검증 — speak/trade/rest/move, trade는 market에서만"""
    if action_str not in PHASE2_VALID_ACTIONS:
        return False
    if action_str == "trade" and location != "market":
        return False
    return True


def _is_valid_phase2_action(action_str: str) -> bool:
    """v0.3: action 문법 유효성만 확인 (위치 제약 무시)"""
    return action_str in PHASE2_VALID_ACTIONS


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
        self.persona_on = game_cfg.get("persona_on", True)
        self.neutral_actions = game_cfg.get("neutral_actions", False)

        # v0.3 본실험 필드
        self.run_id = sim_cfg.get("run_id", self.name)
        self.condition = game_cfg.get("condition")  # "baseline" / "experimental"
        self.latin_square_run = game_cfg.get("latin_square_run")
        self.dominant_mood = game_cfg.get("dominant_mood")
        self.use_v03 = self.condition is not None  # v0.3 config이면 자동 활성화

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
            self.adapters[agent.id] = create_adapter(
                adapter_type,
                model=model,
                persona=agent.persona,
                agent_id=agent.id,
            )

        # Environment — Phase 2 uses 3 spaces (plaza/market/alley)
        if self.phase == 2:
            default_spaces = {
                "plaza": {"capacity": 10, "visibility": "public"},
                "market": {"capacity": 10, "visibility": "public"},
                "alley": {"capacity": 10, "visibility": "members_only"},
            }
        else:
            default_spaces = {
                "plaza": {"capacity": 12, "visibility": "public"},
                "market": {"capacity": 12, "visibility": "public"},
                "alley_a": {"capacity": 4, "visibility": "members_only"},
                "alley_b": {"capacity": 4, "visibility": "members_only"},
                "alley_c": {"capacity": 4, "visibility": "members_only"},
            }
        self.environment = Environment(self.config.get("spaces", default_spaces))
        self.environment.tax_rate = market_cfg.get("default_tax_rate", 0.1)

        # Place agents in initial locations
        for agent in self.agents:
            self.environment.place_agent(agent.id, agent.location)

        # Systems — all initialized, Phase 2 disables whisper leak
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
            enabled=self.whisper_leak_enabled if self.phase != 2 else False,
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

        # v0.3 system prompt cache (에이전트별, run 동안 불변)
        self._system_prompts: dict[str, str] = {}
        if self.use_v03 and self.phase == 2:
            for agent in self.agents:
                self._system_prompts[agent.id] = build_system_prompt_v03(
                    persona=agent.persona,
                    persona_on=self.persona_on,
                    agent_name=agent.id,
                    lang=self.language,
                )

    def run(self):
        phase_label = f"Phase {self.phase}"
        print(f"=== {self.name} 시뮬레이션 시작 ({phase_label}) ===")
        print(f"Epochs: {self.total_epochs}, Language: {self.language}")
        if self.phase == 1:
            print(f"Energy frozen: {self.energy_frozen}, Market shadow: {self.market_shadow}")
        else:
            print(f"Persona: {'ON' if self.persona_on else 'OFF'}, Neutral actions: {self.neutral_actions}")
        print(f"Agents: {len(self.agents)}")
        print(f"Log directory: {self.logger.run_dir}")
        print()

        # v0.3: run_meta.json 저장
        if self.use_v03:
            from datetime import datetime
            self._run_start_time = datetime.now().isoformat()
            self.logger.save_run_meta({
                "run_id": self.run_id,
                "phase": self.phase,
                "condition": self.condition,
                "latin_square_run": self.latin_square_run,
                "dominant_mood": self.dominant_mood,
                "language": self.language,
                "agent_count": len(self.agents),
                "turn_count": self.total_epochs,
                "model_list": sorted(set(
                    a.model for a in self.agents if a.model
                )),
                "persona_assignment": {
                    a.id: a.persona for a in self.agents
                },
                "initial_locations": {
                    a.id: a.home for a in self.agents
                },
                "system_prompts": self._system_prompts,
                "prompt_version": "v0.3",
                "start_time": self._run_start_time,
            })

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

        if self.phase == 2:
            # Phase 2: no market distribution, no treasury, no billboard
            self.logger.log_epoch_summary(
                epoch=epoch,
                agent_count=len(self.agents),
                energy_values=[0] * len(self.agents),
                transaction_count=self.epoch_trade_count,
                treasury=0,
                extra={
                    "phase": 2,
                    "persona_on": self.persona_on,
                    "neutral_actions": self.neutral_actions,
                },
            )
            return

        # Phase 1: market distribution
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
        if self.use_v03 and self.phase == 2:
            return self._execute_agent_turn_v03(agent, epoch)

        resources_before = agent.resource_snapshot()

        # Build context
        context = self._build_agent_context(agent, epoch)

        # Get LLM response
        adapter = self.adapters[agent.id]
        response = adapter.generate(context, max_tokens=2000)

        # Execute action
        success, result = self._execute_action(agent, response, epoch)

        resources_after = agent.resource_snapshot()

        # Build log entry
        log_extra = {}
        # Parse quality metrics (Theo §3: Shell Compatibility 언어 차원 데이터)
        log_extra["parse_success"] = response.success
        log_extra["raw_action"] = response.action
        if self.phase == 1:
            log_extra["shadow_mode"] = self.energy_frozen
            if "would_have_changed" in result:
                log_extra["would_have_changed"] = result["would_have_changed"]
        if "leaked" in result:
            log_extra["leaked"] = result["leaked"]
        if "new_rate" in result:
            log_extra["new_rate"] = result["new_rate"]

        # Phase 2 extra logging (spec §4-C) — 파일럿 코드패스
        if self.phase == 2:
            log_extra["persona_condition"] = "with_persona" if self.persona_on else "no_persona"
            log_extra["constraint_level"] = get_constraint_level(agent.persona) if self.persona_on else "none"
            log_extra["home_location"] = agent.home
            log_extra["resource_effect"] = result.get("resource_effect", 0)
            log_extra["null_effect"] = result.get("null_effect", False)

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

    def _execute_agent_turn_v03(self, agent: Agent, epoch: int):
        """v0.3 본실험 에이전트 턴 — System/Turn 분리, 에러 분류, 재시도"""
        adapter = self.adapters[agent.id]
        system_prompt = self._system_prompts.get(agent.id, "")

        # Build turn prompt
        agent_ids_here = self.environment.get_agents_at(agent.location)
        agents_here = []
        for aid in agent_ids_here:
            if aid == agent.id:
                continue
            other = self.agents_by_id.get(aid)
            if other:
                agents_here.append({"id": aid, "persona": other.persona})

        turn_prompt = build_turn_prompt_v03(
            agent_id=agent.id,
            location=agent.location,
            turn=epoch,
            agents_here=agents_here,
            recent_events=self.action_log,
            persona_on=self.persona_on,
            lang=self.language,
        )

        # LLM 호출 + 재시도 로직
        response = adapter.generate(turn_prompt, max_tokens=2000, system_prompt=system_prompt)
        retried = False

        # 에러 분류 및 재시도 (v0.3 §5.2)
        if not response.success:
            error_str = (response.error or "").lower()
            if "시간 초과" in error_str or "timeout" in error_str:
                error_type = "timeout"
            else:
                error_type = "parse_error"

            # 재시도 1회
            response = adapter.generate(turn_prompt, max_tokens=2000, system_prompt=system_prompt)
            retried = True

            if not response.success:
                # 재시도 실패 — 최종 에러 기록
                self._log_v03_action(
                    agent, epoch, error_type, response, turn_prompt,
                    success=False, result={}, retried=True,
                )
                self._append_action_log_v03(agent, epoch, error_type, response)
                return

        # JSON 파싱 성공 — action 유효성 확인
        action = response.action
        if not _is_valid_phase2_action(action):
            # 유효하지 않은 action
            self._log_v03_action(
                agent, epoch, "invalid", response, turn_prompt,
                success=False, result={"raw_action": action}, retried=retried,
            )
            self._append_action_log_v03(agent, epoch, "invalid", response)
            return

        # 유효한 action — 실행
        target = response.target if isinstance(response.target, str) else None
        content = response.content if isinstance(response.content, str) else None
        success, result = self._execute_action_phase2_v03(agent, action, target, content, epoch)

        self._log_v03_action(
            agent, epoch, action, response, turn_prompt,
            success=success, result=result, retried=retried,
        )
        self._append_action_log_v03(agent, epoch, action, response, success=success)

    def _execute_action_phase2_v03(
        self, agent: Agent, action: str, target: Optional[str],
        content: Optional[str], epoch: int,
    ) -> tuple[bool, dict]:
        """v0.3 Phase 2 action execution — trade 시장 밖 시도 허용"""
        if action == "speak":
            return True, {"resource_effect": 0, "null_effect": False}
        elif action == "trade":
            if agent.location != "market":
                # 시장 밖 trade 시도 — 유효 시도이나 실패 (Luca 추가 B)
                return False, {"error": "not_at_market", "resource_effect": 0, "null_effect": True}
            self.epoch_trade_count += 1
            return True, {"resource_effect": 0, "null_effect": True}
        elif action == "rest":
            return True, {"resource_effect": 0, "null_effect": False}
        elif action == "move":
            success, move_result = self._action_move(agent, target)
            move_result["resource_effect"] = 0
            move_result["null_effect"] = False
            return success, move_result
        else:
            return False, {"error": f"unknown_action: {action}"}

    def _log_v03_action(
        self, agent: Agent, epoch: int, action_type: str,
        response: LLMResponse, turn_prompt: str,
        success: bool, result: dict, retried: bool,
    ):
        """v0.3 로깅"""
        raw_text = ""
        if response.raw_response:
            raw_text = response.raw_response.get("text", "")

        log_extra = {
            "run_id": self.run_id,
            "phase": self.phase,
            "condition": self.condition,
            "latin_square_run": self.latin_square_run,
            "dominant_mood": self.dominant_mood,
            "language": self.language,
            "model": agent.model or "",
            "adapter": agent.adapter_type or "",
            "persona_condition": "with_persona" if self.persona_on else "no_persona",
            "constraint_level": get_constraint_level(agent.persona) if self.persona_on else "none",
            "home_location": agent.home,
            "parse_success": response.success,
            "raw_action": response.action,
            "retried": retried,
            "turn_prompt_sent": turn_prompt,
            "response_raw": raw_text,
            "resource_effect": result.get("resource_effect", 0),
            "null_effect": result.get("null_effect", False),
        }
        if "error" in result:
            log_extra["error_detail"] = result["error"]

        self.logger.log_action(
            epoch=epoch,
            agent_id=agent.id,
            persona=agent.persona,
            location=agent.location,
            action_type=action_type,
            target=response.target,
            content=response.content,
            thought=response.thought,
            success=success,
            resources_before={},
            resources_after={},
            extra=log_extra,
            v03=True,
        )

    def _append_action_log_v03(
        self, agent: Agent, epoch: int, action_type: str,
        response: LLMResponse, success: bool = False,
    ):
        """v0.3 action_log 엔트리 (이벤트 포맷용)"""
        target_persona = None
        target = response.target if isinstance(response.target, str) else None
        if target and target in self.agents_by_id:
            target_persona = self.agents_by_id[target].persona

        self.action_log.append({
            "epoch": epoch,
            "agent_id": agent.id,
            "persona": agent.persona,
            "location": agent.location,
            "action_type": action_type,
            "target": target,
            "target_persona": target_persona,
            "content": response.content,
            "success": success,
        })

    def _build_agent_context(self, agent: Agent, epoch: int) -> str:
        if self.phase == 2:
            return self._build_agent_context_phase2(agent, epoch)

        # Phase 1 context
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

    def _build_agent_context_phase2(self, agent: Agent, epoch: int) -> str:
        """Phase 2 컨텍스트 — 간소화 (에너지/영향력/시장/게시판 없음)"""
        agent_ids_here = self.environment.get_agents_at(agent.location)
        agents_here = [
            {"id": aid}
            for aid in agent_ids_here
            if aid != agent.id
        ]

        return build_context_phase2(
            agent_id=agent.id,
            persona=agent.persona,
            persona_on=self.persona_on,
            location=agent.location,
            turn=epoch,
            agent_count=len(self.agents),
            recent_events=self.action_log,
            agents_here=agents_here,
            lang=self.language,
        )

    def _execute_action(self, agent: Agent, response: LLMResponse, epoch: int) -> tuple[bool, dict]:
        action = response.action
        target = response.target if isinstance(response.target, str) else None
        content = response.content

        if self.phase == 2:
            return self._execute_action_phase2(agent, action, target, content, epoch)

        # Phase 1 action validation
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

    def _execute_action_phase2(
        self, agent: Agent, action: str, target: Optional[str],
        content: Optional[str], epoch: int,
    ) -> tuple[bool, dict]:
        """Phase 2 action execution — neutral actions, no resource effects"""
        if not _can_perform_action_phase2(action, agent.location):
            return False, {"error": f"invalid_action: {action} at {agent.location}"}

        if action == "speak":
            return True, {"resource_effect": 0, "null_effect": False}
        elif action == "trade":
            self.epoch_trade_count += 1
            return True, {"resource_effect": 0, "null_effect": True}
        elif action == "rest":
            return True, {"resource_effect": 0, "null_effect": False}
        elif action == "move":
            success, move_result = self._action_move(agent, target)
            move_result["resource_effect"] = 0
            move_result["null_effect"] = False
            return success, move_result
        else:
            return False, {"error": f"unknown_action: {action}"}

    # --- Phase 1 action handlers ---

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
        # v0.3: run_meta.json에 end_time 추가
        if self.use_v03:
            from datetime import datetime
            import json
            meta_path = self.logger.run_dir / "run_meta.json"
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                meta["end_time"] = datetime.now().isoformat()
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(meta, f, ensure_ascii=False, indent=2)

        print()
        print(f"=== 시뮬레이션 완료 ===")
        print(f"총 {self.total_epochs} 에폭, {len(self.action_log)} 행동 기록")
        print(f"로그 저장 위치: {self.logger.run_dir}")

        if self.phase == 1:
            for agent in sorted(self.agents, key=lambda a: a.energy, reverse=True):
                rank = self.influence_system.get_rank_name(agent.influence, "ko")
                print(f"  {agent.id}: E={agent.energy} I={agent.influence} ({rank})")
        else:
            for agent in sorted(self.agents, key=lambda a: a.id):
                print(f"  {agent.id}: persona={agent.persona} home={agent.home}")
