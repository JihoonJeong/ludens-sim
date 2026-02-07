"""Latin Square / Cyclic Balance 생성기 테스트 — v0.5"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from collections import Counter
from scripts.generate_latin_square import (
    generate_set_a_b, generate_set_c_d, generate_phase1_homogeneous,
    LATIN_SQUARE_4x4, CYCLIC_BALANCE, DEFAULT_MODELS, MODEL_ADAPTERS,
    PERSONAS, PERSONA_HOMES, LOCATIONS,
)


class TestLatinSquare4x4Structure:

    def test_4_runs(self):
        assert len(LATIN_SQUARE_4x4) == 4

    def test_4_personas_per_run(self):
        for run in LATIN_SQUARE_4x4:
            assert len(run) == 4

    def test_each_model_appears_twice_per_run(self):
        """Run 내 균형: 각 모델 2회"""
        for run in LATIN_SQUARE_4x4:
            all_models = []
            for model_a, model_b in run:
                all_models.extend([model_a, model_b])
            counts = Counter(all_models)
            for model in DEFAULT_MODELS:
                assert counts[model] == 2, f"Model {model} appears {counts[model]} times, expected 2"

    def test_each_model_per_persona_across_runs(self):
        """Set 내 균형: 각 모델이 각 Persona에 정확히 2회"""
        for persona_idx in range(4):
            model_counts = Counter()
            for run in LATIN_SQUARE_4x4:
                model_a, model_b = run[persona_idx]
                model_counts[model_a] += 1
                model_counts[model_b] += 1
            for model in DEFAULT_MODELS:
                assert model_counts[model] == 2, \
                    f"Persona {persona_idx}: model {model} appears {model_counts[model]} times"


class TestCyclicBalanceStructure:

    def test_3_runs(self):
        assert len(CYCLIC_BALANCE) == 3

    def test_8_agents_per_run(self):
        for run in CYCLIC_BALANCE:
            total = sum(len(models) for models in run.values())
            assert total == 8

    def test_332_distribution(self):
        """Each run has [3,3,2] distribution"""
        for run in CYCLIC_BALANCE:
            sizes = sorted([len(run[loc]) for loc in LOCATIONS])
            assert sizes == [2, 3, 3]

    def test_each_model_appears_2_per_run(self):
        """Run 내 균형: 각 모델 정확히 2회"""
        for run in CYCLIC_BALANCE:
            all_models = []
            for loc in LOCATIONS:
                all_models.extend(run[loc])
            counts = Counter(all_models)
            for model in DEFAULT_MODELS:
                assert counts[model] == 2, \
                    f"Model {model} appears {counts[model]} times in run, expected 2"

    def test_each_model_6_total_across_runs(self):
        """3 runs 합계: 각 모델 총 6회 (24 slots / 4 models)"""
        total_counts = Counter()
        for run in CYCLIC_BALANCE:
            for loc in LOCATIONS:
                for model in run[loc]:
                    total_counts[model] += 1
        for model in DEFAULT_MODELS:
            assert total_counts[model] == 6, \
                f"Model {model} total {total_counts[model]}, expected 6"

    def test_each_model_present_in_all_locations(self):
        """각 모델이 모든 장소에 최소 1회 이상"""
        for location in LOCATIONS:
            models_seen = set()
            for run in CYCLIC_BALANCE:
                for model in run[location]:
                    models_seen.add(model)
            assert models_seen == set(DEFAULT_MODELS), \
                f"Location {location}: missing models {set(DEFAULT_MODELS) - models_seen}"


class TestSetAB:

    @pytest.fixture
    def configs_ko(self):
        return generate_set_a_b("ko")

    @pytest.fixture
    def configs_en(self):
        return generate_set_a_b("en")

    def test_generates_4_runs(self, configs_ko):
        assert len(configs_ko) == 4

    def test_8_agents_per_run(self, configs_ko):
        for cfg in configs_ko:
            assert len(cfg["agents"]) == 8

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
            assert personas == {"archivist", "observer", "merchant", "jester"}

    def test_two_agents_per_persona(self, configs_ko):
        for cfg in configs_ko:
            counts = Counter(a["persona"] for a in cfg["agents"])
            for persona in PERSONAS:
                assert counts[persona] == 2

    def test_all_4_models_used(self, configs_ko):
        """Each run uses all 4 models"""
        for cfg in configs_ko:
            models = set()
            for a in cfg["agents"]:
                # Resolve model name back from adapter model ID
                for name, (adapter, model_id) in MODEL_ADAPTERS.items():
                    if a.get("model") == model_id and a.get("adapter") == adapter:
                        models.add(name)
            assert len(models) == 4

    def test_130_turns(self, configs_ko):
        for cfg in configs_ko:
            assert cfg["simulation"]["total_epochs"] == 130

    def test_phase_2(self, configs_ko):
        for cfg in configs_ko:
            assert cfg["game_mode"]["phase"] == 2

    def test_capacity_8(self, configs_ko):
        for cfg in configs_ko:
            for space in cfg["spaces"].values():
                assert space["capacity"] == 8

    def test_persona_homes(self, configs_ko):
        """Agents should be placed at their persona's home location"""
        for cfg in configs_ko:
            for agent in cfg["agents"]:
                expected_home = PERSONA_HOMES[agent["persona"]]
                assert agent["home"] == expected_home


class TestSetCD:

    @pytest.fixture
    def configs_ko(self):
        return generate_set_c_d("ko")

    def test_generates_3_runs(self, configs_ko):
        assert len(configs_ko) == 3

    def test_8_agents_per_run(self, configs_ko):
        for cfg in configs_ko:
            assert len(cfg["agents"]) == 8

    def test_persona_off(self, configs_ko):
        for cfg in configs_ko:
            assert cfg["game_mode"]["persona_on"] is False

    def test_agent_ids_numbered(self, configs_ko):
        for cfg in configs_ko:
            ids = [a["id"] for a in cfg["agents"]]
            assert ids == [f"agent_{i:02d}" for i in range(1, 9)]

    def test_all_locations_used(self, configs_ko):
        for cfg in configs_ko:
            homes = {a["home"] for a in cfg["agents"]}
            assert homes == {"plaza", "market", "alley"}

    def test_332_distribution(self, configs_ko):
        for cfg in configs_ko:
            counts = Counter(a["home"] for a in cfg["agents"])
            sizes = sorted(counts.values())
            assert sizes == [2, 3, 3]

    def test_130_turns(self, configs_ko):
        for cfg in configs_ko:
            assert cfg["simulation"]["total_epochs"] == 130


class TestPhase1Homogeneous:

    @pytest.fixture
    def configs_ko(self):
        return generate_phase1_homogeneous("ko")

    def test_generates_12_runs(self, configs_ko):
        """4 models × 3 runs = 12"""
        assert len(configs_ko) == 12

    def test_12_agents_per_run(self, configs_ko):
        for cfg in configs_ko:
            assert len(cfg["agents"]) == 12

    def test_50_epochs(self, configs_ko):
        for cfg in configs_ko:
            assert cfg["simulation"]["total_epochs"] == 50

    def test_phase_1(self, configs_ko):
        for cfg in configs_ko:
            assert cfg["game_mode"]["phase"] == 1

    def test_energy_frozen(self, configs_ko):
        for cfg in configs_ko:
            assert cfg["game_mode"]["energy_frozen"] is True

    def test_market_shadow(self, configs_ko):
        for cfg in configs_ko:
            assert cfg["game_mode"]["market_shadow"] is True

    def test_homogeneous_model(self, configs_ko):
        """All agents in a run use the same model (via default_adapter/default_model)"""
        for cfg in configs_ko:
            # Agents don't have per-agent adapter fields; they use default
            for agent in cfg["agents"]:
                assert "adapter" not in agent
                assert "model" not in agent

    def test_all_4_models_covered(self, configs_ko):
        adapters = {cfg["default_adapter"] for cfg in configs_ko}
        models = {cfg["default_model"] for cfg in configs_ko}
        # Should cover ollama + anthropic + google
        assert "ollama" in adapters
        assert "anthropic" in adapters
        assert "google" in adapters


class TestTotalExperimentScale:

    def test_total_14_phase2_configs(self):
        configs = []
        for lang in ["ko", "en"]:
            configs.extend(generate_set_a_b(lang))
            configs.extend(generate_set_c_d(lang))
        assert len(configs) == 14

    def test_total_112_phase2_agents(self):
        configs = []
        for lang in ["ko", "en"]:
            configs.extend(generate_set_a_b(lang))
            configs.extend(generate_set_c_d(lang))
        total_agents = sum(len(c["agents"]) for c in configs)
        assert total_agents == 112

    def test_total_24_phase1_configs(self):
        configs = []
        for lang in ["ko", "en"]:
            configs.extend(generate_phase1_homogeneous(lang))
        assert len(configs) == 24

    def test_total_288_phase1_agents(self):
        configs = []
        for lang in ["ko", "en"]:
            configs.extend(generate_phase1_homogeneous(lang))
        total_agents = sum(len(c["agents"]) for c in configs)
        assert total_agents == 288

    def test_grand_total_38_runs_400_agents(self):
        """spec §6: 38 runs / 400 agents"""
        all_configs = []
        for lang in ["ko", "en"]:
            all_configs.extend(generate_set_a_b(lang))
            all_configs.extend(generate_set_c_d(lang))
            all_configs.extend(generate_phase1_homogeneous(lang))
        assert len(all_configs) == 38
        total_agents = sum(len(c["agents"]) for c in all_configs)
        assert total_agents == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
