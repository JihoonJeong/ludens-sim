"""Latin Square / Cyclic Balance YAML 자동 생성 — v0.5

Phase 2 (14 configs):
  Set A: Persona On,  KO, 4×4 Latin Square (4 runs)
  Set B: Persona On,  EN, 4×4 Latin Square (4 runs)
  Set C: Persona Off, KO, [3,3,2] Cyclic Balance (3 runs)
  Set D: Persona Off, EN, [3,3,2] Cyclic Balance (3 runs)

Phase 1 (24 configs):
  4 models × 2 languages × 3 runs = 24 Homogeneous runs

Usage:
  python scripts/generate_latin_square.py [--phase1] [--phase2]
"""

import argparse
import yaml
from pathlib import Path


# --- Model definitions ---

DEFAULT_MODELS = ["exaone", "mistral", "haiku", "flash"]

MODEL_ADAPTERS = {
    "exaone": ("ollama", "exaone3.5:7.8b"),
    "mistral": ("ollama", "mistral"),
    "haiku": ("anthropic", "claude-haiku-4-5-20251001"),
    "flash": ("google", "gemini-3-flash-preview"),
    "gpt4omini": ("openai", "gpt-4o-mini"),
}

# --- Phase 2 Persona On: 4×4 Latin Square (spec §2-D) ---

PERSONAS = ["archivist", "observer", "merchant", "jester"]
PERSONA_HOMES = {
    "archivist": "plaza",
    "observer": "plaza",
    "merchant": "market",
    "jester": "alley",
}

# [Run][Persona_idx] -> (model_a, model_b)
# Exactly matches spec §2-D table
LATIN_SQUARE_4x4 = [
    # Run 1
    [("exaone", "mistral"), ("haiku", "flash"), ("exaone", "mistral"), ("haiku", "flash")],
    # Run 2
    [("haiku", "flash"), ("exaone", "mistral"), ("haiku", "flash"), ("exaone", "mistral")],
    # Run 3
    [("mistral", "haiku"), ("flash", "exaone"), ("flash", "exaone"), ("mistral", "haiku")],
    # Run 4
    [("flash", "exaone"), ("mistral", "haiku"), ("mistral", "haiku"), ("flash", "exaone")],
]

# --- Phase 2 Persona Off: [3,3,2] Cyclic Balance (spec §2-D) ---

LOCATIONS = ["plaza", "market", "alley"]

# [Run] -> {location: [models]}
CYCLIC_BALANCE = [
    # Run 1
    {"plaza": ["exaone", "mistral", "haiku"], "market": ["flash", "exaone", "mistral"], "alley": ["haiku", "flash"]},
    # Run 2
    {"plaza": ["flash", "haiku", "exaone"], "market": ["mistral", "flash", "haiku"], "alley": ["exaone", "mistral"]},
    # Run 3
    {"plaza": ["mistral", "flash", "haiku"], "market": ["exaone", "haiku", "flash"], "alley": ["mistral", "exaone"]},
]

# --- Phase 1 agent template ---

PHASE1_AGENTS = [
    {"id": "influencer_01", "persona": "influencer", "home": "plaza"},
    {"id": "influencer_02", "persona": "influencer", "home": "plaza"},
    {"id": "archivist_01", "persona": "archivist", "home": "plaza"},
    {"id": "archivist_02", "persona": "archivist", "home": "market"},
    {"id": "merchant_01", "persona": "merchant", "home": "market"},
    {"id": "merchant_02", "persona": "merchant", "home": "market"},
    {"id": "jester_01", "persona": "jester", "home": "alley_a"},
    {"id": "jester_02", "persona": "jester", "home": "alley_b"},
    {"id": "citizen_01", "persona": "citizen", "home": "plaza"},
    {"id": "citizen_02", "persona": "citizen", "home": "plaza"},
    {"id": "observer_01", "persona": "observer", "home": "plaza"},
    {"id": "architect_01", "persona": "architect", "home": "plaza"},
]


def _resolve_model(model_name: str) -> tuple[str, str]:
    """Return (adapter_type, model_id) for a model name."""
    return MODEL_ADAPTERS.get(model_name, ("mock", "mock"))


def _make_phase2_base_config(set_name: str, run: int, lang: str, persona_on: bool) -> dict:
    return {
        "simulation": {
            "name": f"phase2_{set_name}_run{run}",
            "total_epochs": 130,
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
            "plaza": {"capacity": 8, "visibility": "public"},
            "market": {"capacity": 8, "visibility": "public"},
            "alley": {"capacity": 8, "visibility": "members_only"},
        },
    }


def generate_set_a_b(lang: str) -> list[dict]:
    """Set A/B: Persona On, 4×4 Latin Square (Model × Persona)"""
    set_name = "A" if lang == "ko" else "B"
    configs = []

    for run_idx, run_assignments in enumerate(LATIN_SQUARE_4x4):
        run = run_idx + 1
        config = _make_phase2_base_config(set_name, run, lang, persona_on=True)
        agents = []

        for persona_idx, persona in enumerate(PERSONAS):
            model_a, model_b = run_assignments[persona_idx]
            adapter_a, model_name_a = _resolve_model(model_a)
            adapter_b, model_name_b = _resolve_model(model_b)
            home = PERSONA_HOMES[persona]

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


def generate_set_c_d(lang: str) -> list[dict]:
    """Set C/D: Persona Off, [3,3,2] Cyclic Balance (Model × Location)"""
    set_name = "C" if lang == "ko" else "D"
    configs = []

    for run_idx, run_layout in enumerate(CYCLIC_BALANCE):
        run = run_idx + 1
        config = _make_phase2_base_config(set_name, run, lang, persona_on=False)
        agents = []
        agent_num = 1

        for location in LOCATIONS:
            models = run_layout[location]
            for model_name in models:
                adapter, model_id = _resolve_model(model_name)
                agents.append({
                    "id": f"agent_{agent_num:02d}",
                    "persona": "citizen",
                    "home": location,
                    "adapter": adapter,
                    "model": model_id,
                })
                agent_num += 1

        config["agents"] = agents
        configs.append(config)

    return configs


def generate_phase1_homogeneous(lang: str, runs: int = 3) -> list[dict]:
    """Phase 1 Homogeneous: 동일 모델 12명 × runs"""
    configs = []

    for model_name in DEFAULT_MODELS:
        adapter, model_id = _resolve_model(model_name)

        for run in range(1, runs + 1):
            config = {
                "simulation": {
                    "name": f"phase1_{model_name}_{lang}_run{run}",
                    "total_epochs": 50,
                    "random_seed": None,
                    "language": lang,
                },
                "game_mode": {
                    "phase": 1,
                    "energy_frozen": True,
                    "energy_visible": True,
                    "market_shadow": True,
                    "whisper_leak": True,
                },
                "default_adapter": adapter,
                "default_model": model_id,
                "spaces": {
                    "plaza": {"capacity": 12, "visibility": "public"},
                    "market": {"capacity": 12, "visibility": "public"},
                    "alley_a": {"capacity": 4, "visibility": "members_only"},
                    "alley_b": {"capacity": 4, "visibility": "members_only"},
                    "alley_c": {"capacity": 4, "visibility": "members_only"},
                },
                "resources": {
                    "energy": {"initial": 100, "max": 200},
                    "influence": {"initial": 0},
                },
                "market": {
                    "spawn_per_epoch": 25,
                    "min_presence_reward": 2,
                    "default_tax_rate": 0.1,
                },
                "treasury": {
                    "initial": 0,
                    "overflow_threshold": 100,
                },
                "whisper": {
                    "base_leak_probability": 0.15,
                    "observer_bonus": 0.35,
                },
                "agents": [dict(a) for a in PHASE1_AGENTS],
            }
            configs.append(config)

    return configs


def _write_configs(configs: list[dict], output_dir: Path, prefix: str, set_name: str = ""):
    """Write configs to YAML files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for i, cfg in enumerate(configs):
        if set_name:
            filename = f"set_{set_name.lower()}_run{i + 1}.yaml"
        else:
            filename = f"{prefix}.yaml"
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        print(f"  Generated: {filepath}")


def generate_phase2(output_dir: str):
    """Generate all Phase 2 configs (14 total)."""
    out = Path(output_dir)
    print("=== Phase 2 YAML Generation ===")

    all_configs = []

    # Set A (Persona On, KO) + Set B (Persona On, EN)
    for lang in ["ko", "en"]:
        set_name = "A" if lang == "ko" else "B"
        configs = generate_set_a_b(lang)
        _write_configs(configs, out, "", set_name)
        all_configs.extend(configs)

    # Set C (Persona Off, KO) + Set D (Persona Off, EN)
    for lang in ["ko", "en"]:
        set_name = "C" if lang == "ko" else "D"
        configs = generate_set_c_d(lang)
        _write_configs(configs, out, "", set_name)
        all_configs.extend(configs)

    print(f"\nPhase 2 Total: {len(all_configs)} configs in {out}")
    _print_summary(all_configs)
    return all_configs


def generate_phase1(output_dir: str):
    """Generate all Phase 1 configs (24 total)."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    print("=== Phase 1 YAML Generation ===")

    all_configs = []
    for lang in ["ko", "en"]:
        configs = generate_phase1_homogeneous(lang)
        for cfg in configs:
            name = cfg["simulation"]["name"]
            filepath = out / f"{name}.yaml"
            with open(filepath, "w", encoding="utf-8") as f:
                yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            print(f"  Generated: {filepath}")
        all_configs.extend(configs)

    print(f"\nPhase 1 Total: {len(all_configs)} configs in {out}")
    return all_configs


def _print_summary(configs: list[dict]):
    """Print summary of generated configs."""
    print("\n=== Summary ===")
    for cfg in configs:
        name = cfg["simulation"]["name"]
        lang = cfg["simulation"]["language"]
        persona = "ON" if cfg["game_mode"].get("persona_on", True) else "OFF"
        n_agents = len(cfg["agents"])
        epochs = cfg["simulation"]["total_epochs"]
        print(f"  {name} [{lang}] persona={persona} agents={n_agents} epochs={epochs}")


def main():
    parser = argparse.ArgumentParser(description="Generate experiment configs (v0.5)")
    parser.add_argument(
        "--phase2", action="store_true", default=False,
        help="Generate Phase 2 configs (14 YAMLs)",
    )
    parser.add_argument(
        "--phase1", action="store_true", default=False,
        help="Generate Phase 1 Homogeneous configs (24 YAMLs)",
    )
    parser.add_argument(
        "--all", action="store_true", default=False,
        help="Generate both Phase 1 and Phase 2 configs",
    )
    parser.add_argument(
        "--output-dir-phase2",
        default="games/white_room/config/phase2",
        help="Output directory for Phase 2 YAML files",
    )
    parser.add_argument(
        "--output-dir-phase1",
        default="games/white_room/config/phase1",
        help="Output directory for Phase 1 YAML files",
    )
    args = parser.parse_args()

    if args.all:
        args.phase1 = True
        args.phase2 = True

    if not args.phase1 and not args.phase2:
        # Default: generate both
        args.phase1 = True
        args.phase2 = True

    if args.phase2:
        generate_phase2(args.output_dir_phase2)
        print()

    if args.phase1:
        generate_phase1(args.output_dir_phase1)


if __name__ == "__main__":
    main()
