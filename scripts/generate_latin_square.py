"""Latin Square YAML 자동 생성 — Phase 2 (spec §2-D)

4 Sets × 3 runs = 12 configs 생성:
  Set A: Persona On,  KO, Model×Persona Latin Square
  Set B: Persona On,  EN, Model×Persona Latin Square
  Set C: Persona Off, KO, Model×Location Latin Square
  Set D: Persona Off, EN, Model×Location Latin Square

Usage:
  python scripts/generate_latin_square.py [--output-dir OUTPUT_DIR] [--models M1 M2 M3]
"""

import argparse
import yaml
from pathlib import Path


# Latin Square rotation for 3 models × 3 roles
# Each run rotates the model assignment
LATIN_SQUARE_3x3 = [
    [0, 1, 2],  # Run 1: model0→role0, model1→role1, model2→role2
    [1, 2, 0],  # Run 2: model1→role0, model2→role1, model0→role2
    [2, 0, 1],  # Run 3: model2→role0, model0→role1, model1→role2
]

PERSONAS = ["archivist", "merchant", "jester"]
LOCATIONS = ["plaza", "market", "alley"]

# Default adapter/model mapping
DEFAULT_MODELS = ["exaone", "mistral", "haiku"]
MODEL_ADAPTERS = {
    "exaone": ("ollama", "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct"),
    "mistral": ("ollama", "mistral"),
    "haiku": ("anthropic", "claude-haiku-4-5-20251001"),
}


def make_base_config(set_name: str, run: int, lang: str, persona_on: bool) -> dict:
    return {
        "simulation": {
            "name": f"phase2_{set_name}_run{run}",
            "total_epochs": 100,
            "random_seed": None,
            "language": lang,
        },
        "game_mode": {
            "phase": 2,
            "energy_frozen": True,
            "energy_visible": False,
            "market_shadow": False,
            "whisper_leak": False,
            "persona_on": persona_on,
            "neutral_actions": True,
        },
        "default_adapter": "mock",
        "default_model": "mock",
        "spaces": {
            "plaza": {"capacity": 6, "visibility": "public"},
            "market": {"capacity": 6, "visibility": "public"},
            "alley": {"capacity": 6, "visibility": "members_only"},
        },
    }


def generate_set_a_b(models: list[str], lang: str) -> list[dict]:
    """Set A/B: Persona On, Model × Persona Latin Square"""
    set_name = "A" if lang == "ko" else "B"
    configs = []

    for run_idx, rotation in enumerate(LATIN_SQUARE_3x3):
        run = run_idx + 1
        config = make_base_config(set_name, run, lang, persona_on=True)
        agents = []

        for persona_idx, persona in enumerate(PERSONAS):
            # Each persona gets 2 agents from different models
            model_a = models[rotation[persona_idx]]
            model_b = models[rotation[(persona_idx + 1) % 3]]
            adapter_a, model_name_a = MODEL_ADAPTERS.get(model_a, ("mock", "mock"))
            adapter_b, model_name_b = MODEL_ADAPTERS.get(model_b, ("mock", "mock"))

            # Home location based on persona default
            home = {"archivist": "plaza", "merchant": "market", "jester": "alley"}[persona]

            agents.append({
                "id": f"{persona}_01",
                "persona": persona,
                "home": home,
                "adapter": adapter_a,
                "model": model_name_a,
            })
            agents.append({
                "id": f"{persona}_02",
                "persona": persona,
                "home": home,
                "adapter": adapter_b,
                "model": model_name_b,
            })

        config["agents"] = agents
        configs.append(config)

    return configs


def generate_set_c_d(models: list[str], lang: str) -> list[dict]:
    """Set C/D: Persona Off, Model × Location Latin Square"""
    set_name = "C" if lang == "ko" else "D"
    configs = []

    for run_idx, rotation in enumerate(LATIN_SQUARE_3x3):
        run = run_idx + 1
        config = make_base_config(set_name, run, lang, persona_on=False)
        agents = []

        for loc_idx, location in enumerate(LOCATIONS):
            model = models[rotation[loc_idx]]
            adapter, model_name = MODEL_ADAPTERS.get(model, ("mock", "mock"))

            agents.append({
                "id": f"agent_{loc_idx * 2 + 1:02d}",
                "persona": "citizen",  # No persona — citizen as placeholder
                "home": location,
                "adapter": adapter,
                "model": model_name,
            })
            agents.append({
                "id": f"agent_{loc_idx * 2 + 2:02d}",
                "persona": "citizen",
                "home": location,
                "adapter": adapter,
                "model": model_name,
            })

        config["agents"] = agents
        configs.append(config)

    return configs


def main():
    parser = argparse.ArgumentParser(description="Generate Phase 2 Latin Square configs")
    parser.add_argument(
        "--output-dir",
        default="games/white_room/config/phase2",
        help="Output directory for generated YAML files",
    )
    parser.add_argument(
        "--models",
        nargs=3,
        default=DEFAULT_MODELS,
        help="Three model names (default: exaone mistral haiku)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_configs = []

    # Set A (Persona On, KO) + Set B (Persona On, EN)
    for lang in ["ko", "en"]:
        configs = generate_set_a_b(args.models, lang)
        set_name = "A" if lang == "ko" else "B"
        for i, cfg in enumerate(configs):
            filename = f"set_{set_name.lower()}_run{i+1}.yaml"
            filepath = output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            print(f"Generated: {filepath}")
            all_configs.append(cfg)

    # Set C (Persona Off, KO) + Set D (Persona Off, EN)
    for lang in ["ko", "en"]:
        configs = generate_set_c_d(args.models, lang)
        set_name = "C" if lang == "ko" else "D"
        for i, cfg in enumerate(configs):
            filename = f"set_{set_name.lower()}_run{i+1}.yaml"
            filepath = output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            print(f"Generated: {filepath}")
            all_configs.append(cfg)

    print(f"\nTotal: {len(all_configs)} configs generated in {output_dir}")

    # Summary
    print("\n=== Latin Square Summary ===")
    for cfg in all_configs:
        name = cfg["simulation"]["name"]
        lang = cfg["simulation"]["language"]
        persona = "ON" if cfg["game_mode"]["persona_on"] else "OFF"
        agent_ids = [a["id"] for a in cfg["agents"]]
        print(f"  {name} [{lang}] persona={persona}: {agent_ids}")


if __name__ == "__main__":
    main()
