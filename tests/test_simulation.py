"""시뮬레이션 통합 테스트 — mock adapter, 5에폭"""

import sys
import json
import tempfile
import shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from games.white_room.simulation import WhiteRoomSimulation


@pytest.fixture
def config_path():
    return str(Path(__file__).parent.parent / "games" / "white_room" / "config" / "phase1_default.yaml")


@pytest.fixture
def short_simulation(config_path):
    """5에폭 시뮬레이션"""
    sim = WhiteRoomSimulation(config_path)
    sim.total_epochs = 5
    return sim


class TestSimulationInit:

    def test_agents_created(self, short_simulation):
        assert len(short_simulation.agents) == 12

    def test_agent_energy_initial(self, short_simulation):
        for agent in short_simulation.agents:
            assert agent.energy == 100

    def test_agent_locations(self, short_simulation):
        agents_by_id = short_simulation.agents_by_id
        assert agents_by_id["influencer_01"].location == "plaza"
        assert agents_by_id["merchant_01"].location == "market"
        assert agents_by_id["jester_01"].location == "alley_a"

    def test_energy_frozen(self, short_simulation):
        assert short_simulation.energy_frozen is True

    def test_adapters_created(self, short_simulation):
        assert len(short_simulation.adapters) == 12


class TestSimulationRun:

    def test_run_5_epochs(self, short_simulation):
        short_simulation.run()
        # Action log should have entries
        assert len(short_simulation.action_log) > 0

    def test_energy_stays_frozen(self, short_simulation):
        short_simulation.run()
        for agent in short_simulation.agents:
            assert agent.energy == 100, f"{agent.id} energy changed to {agent.energy}"

    def test_log_files_created(self, short_simulation):
        short_simulation.run()
        assert short_simulation.logger.action_log_path.exists()
        assert short_simulation.logger.epoch_log_path.exists()
        assert short_simulation.logger.config_path.exists()

    def test_action_log_format(self, short_simulation):
        short_simulation.run()
        with open(short_simulation.logger.action_log_path, "r", encoding="utf-8") as f:
            first_line = f.readline()
            entry = json.loads(first_line)
            assert "epoch" in entry
            assert "agent_id" in entry
            assert "action_type" in entry
            assert "resources_before" in entry
            assert "resources_after" in entry

    def test_epoch_summary_format(self, short_simulation):
        short_simulation.run()
        with open(short_simulation.logger.epoch_log_path, "r", encoding="utf-8") as f:
            first_line = f.readline()
            entry = json.loads(first_line)
            assert "epoch" in entry
            assert "agent_count" in entry
            assert "gini_coefficient" in entry

    def test_shadow_mode_logged(self, short_simulation):
        short_simulation.run()
        with open(short_simulation.logger.action_log_path, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                assert entry.get("shadow_mode") is True

    def test_epoch_count_correct(self, short_simulation):
        short_simulation.run()
        with open(short_simulation.logger.epoch_log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 5  # 5 epochs


class TestSimulationCleanup:

    def test_cleanup_logs(self, short_simulation):
        """테스트 후 로그 디렉토리 정리"""
        short_simulation.run()
        log_dir = short_simulation.logger.run_dir
        assert log_dir.exists()
        # 로그 디렉토리 삭제
        shutil.rmtree(log_dir)
        assert not log_dir.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
