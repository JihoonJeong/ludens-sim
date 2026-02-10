#!/usr/bin/env python3
"""v0.3 본실험 YAML config 생성기 — Phase 2 (14개) + Phase 1 로컬 (12개)"""

import yaml
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

project_root = Path(__file__).parent.parent

# ============================================================
# Phase 2 — 14 runs (6 baseline + 8 experimental)
# ============================================================

# 모델 슬롯 (v0.3 §1.2)
PHASE2_MODELS = [
    ("A1", "ollama", "exaone3.5:7.8b"),
    ("A2", "ollama", "exaone3.5:7.8b"),
    ("A3", "ollama", "mistral:7b"),
    ("A4", "ollama", "mistral:7b"),
    ("A5", "google", "gemini-2.0-flash"),
    ("A6", "google", "gemini-2.0-flash"),
    ("A7", "ollama", "llama3.1:8b"),
    ("A8", "ollama", "llama3.1:8b"),
    ("A9", "openai", "gpt-4o-mini"),
    ("A10", "openai", "gpt-4o-mini"),
]

# 초기 위치 (v0.3 §1.3)
PHASE2_HOMES = {
    "A1": "market", "A2": "market", "A3": "market", "A4": "market",
    "A5": "plaza", "A6": "plaza", "A7": "plaza",
    "A8": "alley", "A9": "alley", "A10": "alley",
}

# Latin Square (v0.3 §1.2) — 모델별 Persona 로테이션
# 각 모델은 2 에이전트 → 둘 다 동일 Persona
LATIN_SQUARE = {
    # run: {model_pair: persona}
    1: {"exaone": "observer", "mistral": "citizen", "flash": "merchant", "llama": "jester", "gpt4o": "observer"},
    2: {"exaone": "citizen", "mistral": "merchant", "flash": "jester", "llama": "observer", "gpt4o": "citizen"},
    3: {"exaone": "merchant", "mistral": "jester", "flash": "observer", "llama": "citizen", "gpt4o": "merchant"},
    4: {"exaone": "jester", "mistral": "observer", "flash": "citizen", "llama": "merchant", "gpt4o": "jester"},
}

DOMINANT_MOODS = {1: "observer", 2: "citizen", 3: "merchant", 4: "jester"}

MODEL_GROUP = {
    "A1": "exaone", "A2": "exaone",
    "A3": "mistral", "A4": "mistral",
    "A5": "flash", "A6": "flash",
    "A7": "llama", "A8": "llama",
    "A9": "gpt4o", "A10": "gpt4o",
}


def make_phase2_config(run_id, lang, condition, latin_run=None, dominant_mood=None):
    """Phase 2 YAML config 생성"""
    persona_on = condition == "experimental"
    agents = []
    for aid, adapter, model in PHASE2_MODELS:
        if persona_on and latin_run:
            group = MODEL_GROUP[aid]
            persona = LATIN_SQUARE[latin_run][group]
        else:
            persona = "off"
        agents.append({
            "id": aid,
            "persona": persona,
            "home": PHASE2_HOMES[aid],
            "adapter": adapter,
            "model": model,
        })

    config = {
        "simulation": {
            "name": run_id,
            "run_id": run_id,
            "total_epochs": 150,
            "random_seed": None,
            "language": lang,
        },
        "game_mode": {
            "phase": 2,
            "condition": condition,
            "latin_square_run": latin_run,
            "dominant_mood": dominant_mood,
            "energy_frozen": True,
            "energy_visible": False,
            "market_shadow": False,
            "whisper_leak": False,
            "persona_on": persona_on,
            "neutral_actions": True,
        },
        "agents": agents,
    }
    return config


def generate_phase2_configs():
    """Phase 2 14개 config 생성"""
    out_dir = project_root / "games" / "white_room" / "config" / "phase2" / "main"
    out_dir.mkdir(parents=True, exist_ok=True)

    configs = []

    # Baseline (6 runs: KO×3 + EN×3)
    for lang in ["ko", "en"]:
        for i in range(1, 4):
            run_id = f"p2_base_{lang}_{i:02d}"
            cfg = make_phase2_config(run_id, lang, "baseline")
            configs.append((run_id, cfg))

    # Experimental (8 runs: 4 Latin Square × 2 languages)
    for latin_run in range(1, 5):
        mood = DOMINANT_MOODS[latin_run]
        for lang in ["ko", "en"]:
            run_id = f"p2_exp_r{latin_run}_{lang}"
            cfg = make_phase2_config(run_id, lang, "experimental", latin_run, mood)
            configs.append((run_id, cfg))

    for run_id, cfg in configs:
        path = out_dir / f"{run_id}.yaml"
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        print(f"  {path.name}")

    return len(configs)


# ============================================================
# Phase 1 — 12 runs (EXAONE 6 + Mistral 6)
# ============================================================

# Stage 1 Persona 배치 (12 agents)
PHASE1_PERSONAS = [
    "influencer", "archivist", "merchant", "jester",
    "citizen", "citizen", "observer", "observer",
    "citizen", "citizen", "citizen", "architect",
]

PHASE1_HOMES = [
    "plaza", "plaza", "market", "market",
    "plaza", "alley_a", "alley_a", "alley_b",
    "alley_b", "alley_c", "alley_c", "market",
]


def make_phase1_config(run_id, lang, model_name, adapter="ollama"):
    """Phase 1 YAML config 생성"""
    agents = []
    for i in range(12):
        aid = f"agent_{i+1:02d}"
        agents.append({
            "id": aid,
            "persona": PHASE1_PERSONAS[i],
            "home": PHASE1_HOMES[i],
            "adapter": adapter,
            "model": model_name,
        })

    config = {
        "simulation": {
            "name": run_id,
            "run_id": run_id,
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
        "agents": agents,
    }
    return config


def generate_phase1_configs():
    """Phase 1 로컬 12개 config 생성"""
    out_dir = project_root / "games" / "white_room" / "config" / "phase1" / "main"
    out_dir.mkdir(parents=True, exist_ok=True)

    configs = []
    for model_key, model_name in [("exaone", "exaone3.5:7.8b"), ("mistral", "mistral:7b")]:
        for lang in ["ko", "en"]:
            for i in range(1, 4):
                run_id = f"p1_{model_key}_{lang}_{i:02d}"
                cfg = make_phase1_config(run_id, lang, model_name)
                configs.append((run_id, cfg))

    for run_id, cfg in configs:
        path = out_dir / f"{run_id}.yaml"
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        print(f"  {path.name}")

    return len(configs)


if __name__ == "__main__":
    print("=== v0.3 Config Generator ===\n")

    print("Phase 2 (14 configs):")
    n2 = generate_phase2_configs()

    print(f"\nPhase 1 Local (12 configs):")
    n1 = generate_phase1_configs()

    print(f"\nTotal: {n1 + n2} configs generated.")
