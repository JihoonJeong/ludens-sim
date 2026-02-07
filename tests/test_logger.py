"""Logger 테스트 — Gini 계수, JSONL 기록"""

import sys
import json
import shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from engine.core.logger import SimulationLogger, calculate_gini


class TestGiniCoefficient:

    def test_perfect_equality(self):
        assert calculate_gini([100, 100, 100, 100]) == 0.0

    def test_perfect_inequality(self):
        gini = calculate_gini([0, 0, 0, 400])
        assert 0.7 < gini <= 1.0  # 4명일 때 최대 0.75

    def test_empty(self):
        assert calculate_gini([]) == 0.0

    def test_all_zero(self):
        assert calculate_gini([0, 0, 0]) == 0.0

    def test_moderate_inequality(self):
        gini = calculate_gini([50, 100, 150, 200])
        assert 0.1 < gini < 0.4

    def test_single_value(self):
        assert calculate_gini([100]) == 0.0


class TestSimulationLogger:

    @pytest.fixture
    def logger(self, tmp_path):
        return SimulationLogger(base_dir=str(tmp_path), run_name="test")

    def test_run_dir_created(self, logger):
        assert logger.run_dir.exists()

    def test_save_config(self, logger):
        logger.save_config({"test": "value"})
        assert logger.config_path.exists()
        data = json.loads(logger.config_path.read_text())
        assert data["test"] == "value"

    def test_log_action(self, logger):
        logger.log_action(
            epoch=1, agent_id="a1", persona="citizen", location="plaza",
            action_type="speak", target=None, content="hello",
            thought="test", success=True,
            resources_before={"energy": 100}, resources_after={"energy": 100},
        )
        assert logger.action_log_path.exists()
        with open(logger.action_log_path, encoding="utf-8") as f:
            entry = json.loads(f.readline())
        assert entry["epoch"] == 1
        assert entry["agent_id"] == "a1"
        assert entry["turn"] == 1

    def test_log_action_with_extra(self, logger):
        logger.log_action(
            epoch=1, agent_id="a1", persona="citizen", location="plaza",
            action_type="trade", target=None, content=None,
            thought="test", success=True,
            resources_before={"energy": 100}, resources_after={"energy": 100},
            extra={"shadow_mode": True, "would_have_changed": -2},
        )
        with open(logger.action_log_path, encoding="utf-8") as f:
            entry = json.loads(f.readline())
        assert entry["shadow_mode"] is True
        assert entry["would_have_changed"] == -2

    def test_log_epoch_summary(self, logger):
        logger.log_epoch_summary(
            epoch=1, agent_count=12,
            energy_values=[100] * 12,
            transaction_count=3, treasury=10.0,
        )
        assert logger.epoch_log_path.exists()
        with open(logger.epoch_log_path, encoding="utf-8") as f:
            entry = json.loads(f.readline())
        assert entry["epoch"] == 1
        assert entry["gini_coefficient"] == 0.0
        assert entry["total_energy"] == 1200

    def test_turn_counter_increments(self, logger):
        for i in range(3):
            logger.log_action(
                epoch=1, agent_id=f"a{i}", persona="citizen", location="plaza",
                action_type="idle", target=None, content=None,
                thought="", success=True,
                resources_before={}, resources_after={},
            )
        with open(logger.action_log_path, encoding="utf-8") as f:
            lines = f.readlines()
        turns = [json.loads(l)["turn"] for l in lines]
        assert turns == [1, 2, 3]

    def test_reset_turn_counter(self, logger):
        logger.log_action(
            epoch=1, agent_id="a1", persona="citizen", location="plaza",
            action_type="idle", target=None, content=None,
            thought="", success=True,
            resources_before={}, resources_after={},
        )
        logger.reset_turn_counter()
        logger.log_action(
            epoch=2, agent_id="a1", persona="citizen", location="plaza",
            action_type="idle", target=None, content=None,
            thought="", success=True,
            resources_before={}, resources_after={},
        )
        with open(logger.action_log_path, encoding="utf-8") as f:
            lines = f.readlines()
        assert json.loads(lines[1])["turn"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
