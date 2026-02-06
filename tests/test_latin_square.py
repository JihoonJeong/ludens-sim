"""Latin Square 생성기 테스트"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from scripts.generate_latin_square import (
    generate_set_a_b, generate_set_c_d,
    LATIN_SQUARE_3x3, DEFAULT_MODELS,
)


class TestLatinSquareRotation:

    def test_3x3_rows(self):
        """각 row는 0,1,2의 순열이어야 함"""
        for row in LATIN_SQUARE_3x3:
            assert sorted(row) == [0, 1, 2]

    def test_3x3_columns(self):
        """각 column도 0,1,2의 순열이어야 함"""
        for col in range(3):
            values = [LATIN_SQUARE_3x3[row][col] for row in range(3)]
            assert sorted(values) == [0, 1, 2]


class TestSetAB:

    @pytest.fixture
    def configs_ko(self):
        return generate_set_a_b(DEFAULT_MODELS, "ko")

    @pytest.fixture
    def configs_en(self):
        return generate_set_a_b(DEFAULT_MODELS, "en")

    def test_generates_3_runs(self, configs_ko):
        assert len(configs_ko) == 3

    def test_6_agents_per_run(self, configs_ko):
        for cfg in configs_ko:
            assert len(cfg["agents"]) == 6

    def test_persona_on(self, configs_ko):
        for cfg in configs_ko:
            assert cfg["game_mode"]["persona_on"] is True

    def test_language_ko(self, configs_ko):
        for cfg in configs_ko:
            assert cfg["simulation"]["language"] == "ko"

    def test_language_en(self, configs_en):
        for cfg in configs_en:
            assert cfg["simulation"]["language"] == "en"

    def test_all_personas_present(self, configs_ko):
        for cfg in configs_ko:
            personas = {a["persona"] for a in cfg["agents"]}
            assert personas == {"archivist", "merchant", "jester"}

    def test_two_agents_per_persona(self, configs_ko):
        for cfg in configs_ko:
            from collections import Counter
            counts = Counter(a["persona"] for a in cfg["agents"])
            assert counts["archivist"] == 2
            assert counts["merchant"] == 2
            assert counts["jester"] == 2

    def test_all_models_used(self, configs_ko):
        """Each run uses all 3 models"""
        for cfg in configs_ko:
            models = set()
            for a in cfg["agents"]:
                models.add(a.get("model", "mock"))
            # All 3 models should appear
            assert len(models) == 3

    def test_100_turns(self, configs_ko):
        for cfg in configs_ko:
            assert cfg["simulation"]["total_epochs"] == 100

    def test_phase_2(self, configs_ko):
        for cfg in configs_ko:
            assert cfg["game_mode"]["phase"] == 2


class TestSetCD:

    @pytest.fixture
    def configs_ko(self):
        return generate_set_c_d(DEFAULT_MODELS, "ko")

    def test_generates_3_runs(self, configs_ko):
        assert len(configs_ko) == 3

    def test_6_agents_per_run(self, configs_ko):
        for cfg in configs_ko:
            assert len(cfg["agents"]) == 6

    def test_persona_off(self, configs_ko):
        for cfg in configs_ko:
            assert cfg["game_mode"]["persona_on"] is False

    def test_agent_ids_numbered(self, configs_ko):
        for cfg in configs_ko:
            ids = [a["id"] for a in cfg["agents"]]
            assert ids == ["agent_01", "agent_02", "agent_03", "agent_04", "agent_05", "agent_06"]

    def test_all_locations_used(self, configs_ko):
        """Each run has agents at all 3 locations"""
        for cfg in configs_ko:
            homes = {a["home"] for a in cfg["agents"]}
            assert homes == {"plaza", "market", "alley"}

    def test_two_agents_per_location(self, configs_ko):
        for cfg in configs_ko:
            from collections import Counter
            counts = Counter(a["home"] for a in cfg["agents"])
            assert counts["plaza"] == 2
            assert counts["market"] == 2
            assert counts["alley"] == 2

    def test_model_rotation(self, configs_ko):
        """Models rotate across runs for each location (Latin Square)"""
        # Collect model at plaza for each run
        plaza_models = []
        for cfg in configs_ko:
            plaza_agents = [a for a in cfg["agents"] if a["home"] == "plaza"]
            plaza_models.append(plaza_agents[0].get("model", ""))

        # All runs should have different models at plaza
        assert len(set(plaza_models)) == 3


class TestTotalExperimentScale:

    def test_total_12_configs(self):
        configs = []
        for lang in ["ko", "en"]:
            configs.extend(generate_set_a_b(DEFAULT_MODELS, lang))
            configs.extend(generate_set_c_d(DEFAULT_MODELS, lang))
        assert len(configs) == 12

    def test_total_72_agents(self):
        configs = []
        for lang in ["ko", "en"]:
            configs.extend(generate_set_a_b(DEFAULT_MODELS, lang))
            configs.extend(generate_set_c_d(DEFAULT_MODELS, lang))
        total_agents = sum(len(c["agents"]) for c in configs)
        assert total_agents == 72


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
