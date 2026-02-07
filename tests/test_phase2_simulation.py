"""Phase 2 시뮬레이션 통합 테스트 — v0.5 (8 agents, 4 personas)"""

import sys
import json
import shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from games.white_room.simulation import (
    WhiteRoomSimulation, _can_perform_action_phase2,
)


@pytest.fixture
def phase2_config(tmp_path):
    """Phase 2 테스트용 config (persona_on=True, 8 agents)"""
    import yaml
    config = {
        "simulation": {
            "name": "test_phase2",
            "total_epochs": 5,
            "random_seed": 42,
            "language": "ko",
        },
        "game_mode": {
            "phase": 2,
            "energy_frozen": True,
            "energy_visible": False,
            "market_shadow": False,
            "whisper_leak": False,
            "persona_on": True,
            "neutral_actions": True,
        },
        "default_adapter": "mock",
        "default_model": "mock",
        "spaces": {
            "plaza": {"capacity": 8, "visibility": "public"},
            "market": {"capacity": 8, "visibility": "public"},
            "alley": {"capacity": 8, "visibility": "members_only"},
        },
        "agents": [
            {"id": "archivist_01", "persona": "archivist", "home": "plaza"},
            {"id": "archivist_02", "persona": "archivist", "home": "plaza"},
            {"id": "observer_01", "persona": "observer", "home": "plaza"},
            {"id": "observer_02", "persona": "observer", "home": "plaza"},
            {"id": "merchant_01", "persona": "merchant", "home": "market"},
            {"id": "merchant_02", "persona": "merchant", "home": "market"},
            {"id": "jester_01", "persona": "jester", "home": "alley"},
            {"id": "jester_02", "persona": "jester", "home": "alley"},
        ],
    }
    config_path = tmp_path / "phase2_test.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f)
    return str(config_path)


@pytest.fixture
def phase2_nopersona_config(tmp_path):
    """Phase 2 테스트용 config (persona_on=False, 8 agents)"""
    import yaml
    config = {
        "simulation": {
            "name": "test_phase2_nopersona",
            "total_epochs": 3,
            "random_seed": 42,
            "language": "ko",
        },
        "game_mode": {
            "phase": 2,
            "energy_frozen": True,
            "energy_visible": False,
            "market_shadow": False,
            "whisper_leak": False,
            "persona_on": False,
            "neutral_actions": True,
        },
        "default_adapter": "mock",
        "default_model": "mock",
        "spaces": {
            "plaza": {"capacity": 8, "visibility": "public"},
            "market": {"capacity": 8, "visibility": "public"},
            "alley": {"capacity": 8, "visibility": "members_only"},
        },
        "agents": [
            {"id": "agent_01", "persona": "citizen", "home": "plaza"},
            {"id": "agent_02", "persona": "citizen", "home": "plaza"},
            {"id": "agent_03", "persona": "citizen", "home": "plaza"},
            {"id": "agent_04", "persona": "citizen", "home": "market"},
            {"id": "agent_05", "persona": "citizen", "home": "market"},
            {"id": "agent_06", "persona": "citizen", "home": "market"},
            {"id": "agent_07", "persona": "citizen", "home": "alley"},
            {"id": "agent_08", "persona": "citizen", "home": "alley"},
        ],
    }
    config_path = tmp_path / "phase2_nopersona.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f)
    return str(config_path)


class TestPhase2ActionValidation:

    def test_speak_anywhere(self):
        assert _can_perform_action_phase2("speak", "plaza")
        assert _can_perform_action_phase2("speak", "market")
        assert _can_perform_action_phase2("speak", "alley")

    def test_trade_only_market(self):
        assert _can_perform_action_phase2("trade", "market")
        assert not _can_perform_action_phase2("trade", "plaza")
        assert not _can_perform_action_phase2("trade", "alley")

    def test_whisper_only_alley(self):
        assert _can_perform_action_phase2("whisper", "alley")
        assert not _can_perform_action_phase2("whisper", "plaza")
        assert not _can_perform_action_phase2("whisper", "market")

    def test_support_anywhere(self):
        assert _can_perform_action_phase2("support", "plaza")
        assert _can_perform_action_phase2("support", "market")
        assert _can_perform_action_phase2("support", "alley")

    def test_move_anywhere(self):
        assert _can_perform_action_phase2("move", "plaza")

    def test_idle_anywhere(self):
        assert _can_perform_action_phase2("idle", "plaza")

    def test_no_architect_skills(self):
        assert not _can_perform_action_phase2("build_billboard", "plaza")
        assert not _can_perform_action_phase2("adjust_tax", "plaza")
        assert not _can_perform_action_phase2("grant_subsidy", "plaza")

    def test_unknown_action(self):
        assert not _can_perform_action_phase2("fly", "plaza")


class TestPhase2Init:

    def test_agents_count(self, phase2_config):
        sim = WhiteRoomSimulation(phase2_config)
        assert len(sim.agents) == 8

    def test_phase_flag(self, phase2_config):
        sim = WhiteRoomSimulation(phase2_config)
        assert sim.phase == 2

    def test_persona_on_flag(self, phase2_config):
        sim = WhiteRoomSimulation(phase2_config)
        assert sim.persona_on is True

    def test_neutral_actions_flag(self, phase2_config):
        sim = WhiteRoomSimulation(phase2_config)
        assert sim.neutral_actions is True

    def test_whisper_leak_disabled(self, phase2_config):
        sim = WhiteRoomSimulation(phase2_config)
        assert sim.whisper_system.enabled is False

    def test_three_spaces(self, phase2_config):
        sim = WhiteRoomSimulation(phase2_config)
        assert "plaza" in sim.environment.spaces
        assert "market" in sim.environment.spaces
        assert "alley" in sim.environment.spaces
        assert "alley_a" not in sim.environment.spaces

    def test_agent_locations(self, phase2_config):
        sim = WhiteRoomSimulation(phase2_config)
        for agent in sim.agents:
            assert agent.location in ["plaza", "market", "alley"]


class TestPhase2Run:

    @pytest.fixture
    def sim(self, phase2_config):
        sim = WhiteRoomSimulation(phase2_config)
        sim.run()
        return sim

    def test_run_completes(self, sim):
        assert len(sim.action_log) == 5 * 8  # 5 epochs × 8 agents

    def test_energy_unchanged(self, sim):
        for agent in sim.agents:
            assert agent.energy == 100

    def test_log_files_created(self, sim):
        assert sim.logger.action_log_path.exists()
        assert sim.logger.epoch_log_path.exists()

    def test_action_log_has_phase2_fields(self, sim):
        with open(sim.logger.action_log_path, encoding="utf-8") as f:
            first_line = json.loads(f.readline())
        assert "persona_condition" in first_line
        assert "constraint_level" in first_line
        assert "home_location" in first_line
        assert "resource_effect" in first_line
        assert "null_effect" in first_line

    def test_persona_condition_with_persona(self, sim):
        with open(sim.logger.action_log_path, encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                assert entry["persona_condition"] == "with_persona"

    def test_constraint_levels_correct(self, sim):
        with open(sim.logger.action_log_path, encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                persona = entry["persona"]
                expected = {
                    "archivist": "high_active",
                    "observer": "high_passive",
                    "merchant": "mid",
                    "jester": "low",
                }
                assert entry["constraint_level"] == expected.get(persona, "none")

    def test_home_location_logged(self, sim):
        with open(sim.logger.action_log_path, encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                assert entry["home_location"] in ["plaza", "market", "alley"]

    def test_null_effect_on_trade(self, sim):
        with open(sim.logger.action_log_path, encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                if entry["action_type"] == "trade":
                    assert entry["null_effect"] is True
                    assert entry["resource_effect"] == 0

    def test_null_effect_on_support(self, sim):
        with open(sim.logger.action_log_path, encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                if entry["action_type"] == "support":
                    assert entry["null_effect"] is True

    def test_no_shadow_mode_field(self, sim):
        """Phase 2 should not have shadow_mode field"""
        with open(sim.logger.action_log_path, encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                assert "shadow_mode" not in entry

    def test_epoch_summary_phase2(self, sim):
        with open(sim.logger.epoch_log_path, encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) == 5
        first = json.loads(lines[0])
        assert first["phase"] == 2
        assert first["persona_on"] is True

    def test_cleanup(self, sim):
        shutil.rmtree(sim.logger.run_dir)


class TestPhase2NoPersona:

    @pytest.fixture
    def sim(self, phase2_nopersona_config):
        sim = WhiteRoomSimulation(phase2_nopersona_config)
        sim.run()
        return sim

    def test_persona_off(self, sim):
        assert sim.persona_on is False

    def test_persona_condition_logged(self, sim):
        with open(sim.logger.action_log_path, encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                assert entry["persona_condition"] == "no_persona"

    def test_constraint_level_none(self, sim):
        with open(sim.logger.action_log_path, encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                assert entry["constraint_level"] == "none"

    def test_cleanup(self, sim):
        shutil.rmtree(sim.logger.run_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
