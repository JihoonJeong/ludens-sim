#!/usr/bin/env python3
"""Phase 2 파일럿 로그 병합 — Persona Off/On, KO/EN 별 통합 데이터 생성"""

import json
import sys
import io
from pathlib import Path
from collections import Counter
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

project_root = Path(__file__).parent.parent
logs_dir = project_root / "logs"
data_dir = project_root / "data" / "phase2_pilot"
data_dir.mkdir(parents=True, exist_ok=True)

# Run 매핑 — condition_lang: [run_dirs]
RUNS = {
    # Persona Off (10 agents, all citizen, no persona prompt)
    "nopersona_ko": [
        "20260208_191943_549125_pilot_phase2_nopersona_ko",
        "20260208_231137_225186_pilot_phase2_nopersona_ko",
        "20260209_013215_419085_pilot_phase2_nopersona_ko",
    ],
    "nopersona_en": [
        "20260209_035108_060618_pilot_phase2_nopersona_en",
        "20260209_054440_890544_pilot_phase2_nopersona_en",
    ],
    # Persona On (10 agents, 5 personas × 2)
    "persona_ko": [
        "20260209_174056_623666_pilot_phase2_persona_ko",
        "20260209_200610_497200_pilot_phase2_persona_ko",
        "20260209_222445_083807_pilot_phase2_persona_ko",
    ],
    "persona_en": [
        "20260210_004253_212660_pilot_phase2_persona_en",
        "20260210_024454_259810_pilot_phase2_persona_en",
    ],
}

AGENT_MODEL = {
    "agent_01": "exaone3.5:7.8b",
    "agent_02": "exaone3.5:7.8b",
    "agent_03": "mistral:7b",
    "agent_04": "mistral:7b",
    "agent_05": "llama3.1:8b",
    "agent_06": "llama3.1:8b",
    "agent_07": "gemini-2.0-flash",
    "agent_08": "gemini-2.0-flash",
    "agent_09": "gpt-4o-mini",
    "agent_10": "gpt-4o-mini",
}

AGENT_ADAPTER = {
    "agent_01": "ollama", "agent_02": "ollama",
    "agent_03": "ollama", "agent_04": "ollama",
    "agent_05": "ollama", "agent_06": "ollama",
    "agent_07": "google", "agent_08": "google",
    "agent_09": "openai", "agent_10": "openai",
}

PHASE2_VALID_ACTIONS = {"speak", "trade", "rest", "move"}


def merge_group(group_key, run_dirs):
    """그룹별 병합 (e.g., nopersona_ko, persona_en)"""
    sim_out = data_dir / f"phase2_pilot_{group_key}_simulation_log.jsonl"
    epoch_out = data_dir / f"phase2_pilot_{group_key}_epoch_summary.jsonl"

    condition = "no_persona" if "nopersona" in group_key else "with_persona"
    lang = group_key.rsplit("_", 1)[-1]

    run_stats = []

    with open(sim_out, "w", encoding="utf-8") as sf, \
         open(epoch_out, "w", encoding="utf-8") as ef:

        for i, run_dir in enumerate(run_dirs, 1):
            run_label = f"run{i}"

            sim_path = logs_dir / run_dir / "simulation_log.jsonl"
            total = parse_ok = malformed = 0
            actions = Counter()

            with open(sim_path, encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    entry["language"] = lang
                    entry["run"] = run_label
                    entry["condition"] = condition
                    entry["model"] = AGENT_MODEL.get(entry["agent_id"], "unknown")
                    entry["adapter"] = AGENT_ADAPTER.get(entry["agent_id"], "unknown")
                    sf.write(json.dumps(entry, ensure_ascii=False) + "\n")

                    total += 1
                    actions[entry["action_type"]] += 1
                    if entry.get("parse_success") is True:
                        parse_ok += 1
                    if entry["action_type"] not in PHASE2_VALID_ACTIONS:
                        malformed += 1

            epoch_path = logs_dir / run_dir / "epoch_summary.jsonl"
            with open(epoch_path, encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    entry["language"] = lang
                    entry["run"] = run_label
                    entry["condition"] = condition
                    ef.write(json.dumps(entry, ensure_ascii=False) + "\n")

            run_stats.append({
                "run": run_label,
                "dir": run_dir,
                "total": total,
                "parse_ok": parse_ok,
                "parse_rate": parse_ok / total if total else 0,
                "malformed": malformed,
                "malformed_rate": malformed / total if total else 0,
                "action_dist": dict(actions),
            })

    return run_stats


def main():
    print("=== Phase 2 Pilot 로그 병합 시작 ===\n")

    all_stats = {}
    for group_key, run_dirs in RUNS.items():
        print(f"Processing {group_key} ({len(run_dirs)} runs)...")
        stats = merge_group(group_key, run_dirs)
        all_stats[group_key] = stats

    # Combined files by language (nopersona + persona merged)
    for lang in ["ko", "en"]:
        lang_sim = data_dir / f"phase2_pilot_{lang}_simulation_log.jsonl"
        lang_epoch = data_dir / f"phase2_pilot_{lang}_epoch_summary.jsonl"
        with open(lang_sim, "w", encoding="utf-8") as sf, \
             open(lang_epoch, "w", encoding="utf-8") as ef:
            for cond in ["nopersona", "persona"]:
                key = f"{cond}_{lang}"
                if key not in RUNS:
                    continue
                part_sim = data_dir / f"phase2_pilot_{key}_simulation_log.jsonl"
                with open(part_sim, encoding="utf-8") as f:
                    sf.write(f.read())
                part_epoch = data_dir / f"phase2_pilot_{key}_epoch_summary.jsonl"
                with open(part_epoch, encoding="utf-8") as f:
                    ef.write(f.read())

    # Combined all-in-one
    all_sim = data_dir / "phase2_pilot_all_simulation_log.jsonl"
    all_epoch = data_dir / "phase2_pilot_all_epoch_summary.jsonl"
    with open(all_sim, "w", encoding="utf-8") as sf, \
         open(all_epoch, "w", encoding="utf-8") as ef:
        for lang in ["ko", "en"]:
            lang_sim = data_dir / f"phase2_pilot_{lang}_simulation_log.jsonl"
            with open(lang_sim, encoding="utf-8") as f:
                sf.write(f.read())
            lang_epoch = data_dir / f"phase2_pilot_{lang}_epoch_summary.jsonl"
            with open(lang_epoch, encoding="utf-8") as f:
                ef.write(f.read())

    # Print summary
    print()
    grand_total = 0
    grand_parse = 0
    for group_key, stats_list in all_stats.items():
        print(f"--- {group_key} ---")
        for s in stats_list:
            grand_total += s["total"]
            grand_parse += s["parse_ok"]
            top = sorted(s["action_dist"].items(), key=lambda x: -x[1])[:5]
            top_str = ", ".join(f"{k}({v})" for k, v in top)
            print(f"  {s['run']}: {s['total']} actions, "
                  f"parse {s['parse_ok']}/{s['total']} ({s['parse_rate']*100:.1f}%), "
                  f"malformed {s['malformed']} ({s['malformed_rate']*100:.1f}%)")
            print(f"    actions: {top_str}")
        print()

    print(f"Grand total: {grand_total} actions, "
          f"parse {grand_parse}/{grand_total} ({grand_parse/grand_total*100:.1f}%)")

    print(f"\nFiles generated in {data_dir}:")
    for f in sorted(data_dir.iterdir()):
        size = f.stat().st_size
        if size > 1024 * 1024:
            print(f"  {f.name}: {size / 1024 / 1024:.1f} MB")
        else:
            print(f"  {f.name}: {size / 1024:.1f} KB")

    print("\nDone!")


if __name__ == "__main__":
    main()
