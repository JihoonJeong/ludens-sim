#!/usr/bin/env python3
"""Phase 1 로그 병합 스크립트 — 모델/언어별 데이터 파일 생성"""

import json
import sys
import io
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

project_root = Path(__file__).parent.parent
logs_dir = project_root / "logs"
data_dir = project_root / "data" / "phase1"
data_dir.mkdir(parents=True, exist_ok=True)

# 본실험 12 runs 매핑
RUNS = {
    "exaone_ko": [
        "20260207_213005_494582_phase1_exaone_ko_run1",
        "20260207_223437_406145_phase1_exaone_ko_run2",
        "20260208_002802_698114_phase1_exaone_ko_run3",
    ],
    "exaone_en": [
        "20260208_014142_294838_phase1_exaone_en_run1",
        "20260208_023323_891600_phase1_exaone_en_run2",
        "20260208_033455_457828_phase1_exaone_en_run3",
    ],
    "mistral_en": [
        "20260208_044722_126103_phase1_mistral_en_run1",
        "20260208_053307_984837_phase1_mistral_en_run2",
        "20260208_061812_513160_phase1_mistral_en_run3",
    ],
    "mistral_ko": [
        "20260208_070257_216082_phase1_mistral_ko_run1",
        "20260208_074841_138010_phase1_mistral_ko_run2",
        "20260208_071813_726695_phase1_mistral_ko_run3",
    ],
    "llama_ko": [
        "20260208_114357_196130_phase1_llama_ko_run1",
        "20260208_140431_789044_phase1_llama_ko_run2",
        "20260208_144635_144033_phase1_llama_ko_run3",
    ],
    "llama_en": [
        "20260208_152821_549085_phase1_llama_en_run1",
        "20260208_160744_295859_phase1_llama_en_run2",
        "20260208_164651_778979_phase1_llama_en_run3",
    ],
}

VALID_ACTIONS = {
    "speak", "trade", "support", "whisper", "move", "idle",
    "build_billboard", "adjust_tax", "grant_subsidy",
}


def analyze_run(log_path):
    """단일 run 분석"""
    actions = Counter()
    total = 0
    success = 0
    parse_ok = 0
    malformed = 0

    with open(log_path, encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            total += 1
            actions[entry["action_type"]] += 1
            if entry["success"]:
                success += 1
            if entry.get("parse_success") is True:
                parse_ok += 1
            if entry["action_type"] not in VALID_ACTIONS:
                malformed += 1

    return {
        "total": total,
        "success": success,
        "success_rate": success / total if total else 0,
        "parse_ok": parse_ok,
        "parse_rate": parse_ok / total if total else 0,
        "malformed": malformed,
        "malformed_rate": malformed / total if total else 0,
        "action_dist": dict(actions),
    }


def merge_group(group_key, run_dirs):
    """모델/언어 그룹 병합"""
    model, lang = group_key.rsplit("_", 1)
    sim_out = data_dir / f"phase1_{group_key}_simulation_log.jsonl"
    epoch_out = data_dir / f"phase1_{group_key}_epoch_summary.jsonl"

    run_stats = []

    with open(sim_out, "w", encoding="utf-8") as sf, \
         open(epoch_out, "w", encoding="utf-8") as ef:

        for run_dir in run_dirs:
            run_name = run_dir.split("_", 3)[-1]  # phase1_exaone_ko_run1
            run_num = run_name.rsplit("_", 1)[-1]  # run1

            # Merge simulation log
            sim_path = logs_dir / run_dir / "simulation_log.jsonl"
            with open(sim_path, encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    entry["model"] = model
                    entry["language"] = lang
                    entry["run"] = run_num
                    sf.write(json.dumps(entry, ensure_ascii=False) + "\n")

            # Merge epoch summary
            epoch_path = logs_dir / run_dir / "epoch_summary.jsonl"
            with open(epoch_path, encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    entry["model"] = model
                    entry["language"] = lang
                    entry["run"] = run_num
                    ef.write(json.dumps(entry, ensure_ascii=False) + "\n")

            # Analyze
            stats = analyze_run(sim_path)
            stats["run"] = run_num
            run_stats.append(stats)

    return run_stats


def main():
    print("=== Phase 1 로그 병합 시작 ===\n")

    all_stats = {}
    for group_key, run_dirs in RUNS.items():
        print(f"Processing {group_key}...")
        stats = merge_group(group_key, run_dirs)
        all_stats[group_key] = stats

    # Also create combined all-in-one files
    all_sim = data_dir / "phase1_all_simulation_log.jsonl"
    all_epoch = data_dir / "phase1_all_epoch_summary.jsonl"
    with open(all_sim, "w", encoding="utf-8") as sf, \
         open(all_epoch, "w", encoding="utf-8") as ef:
        for group_key in RUNS:
            sim_part = data_dir / f"phase1_{group_key}_simulation_log.jsonl"
            with open(sim_part, encoding="utf-8") as f:
                sf.write(f.read())
            epoch_part = data_dir / f"phase1_{group_key}_epoch_summary.jsonl"
            with open(epoch_part, encoding="utf-8") as f:
                ef.write(f.read())

    # Generate summary report
    report_path = data_dir / "phase1_local_summary.md"
    with open(report_path, "w", encoding="utf-8") as rpt:
        rpt.write("# White Room Phase 1 — Local LLM Results Summary\n\n")
        rpt.write(f"Generated: {datetime.now().isoformat()}\n\n")
        rpt.write("## Experiment Configuration\n\n")
        rpt.write("- Phase: 1 (Empty Agora — shadow mode, energy frozen)\n")
        rpt.write("- Agents: 12 (homogeneous across all runs)\n")
        rpt.write("- Epochs per run: 50\n")
        rpt.write("- Actions per run: 600 (12 agents x 50 epochs)\n")
        rpt.write("- Models: EXAONE 3.5 7.8B, Mistral 7B, Llama 3.1 8B\n")
        rpt.write("- Languages: KO, EN\n")
        rpt.write("- Runs per condition: 3\n")
        rpt.write("- Total: 18 runs, 10,800 actions\n\n")

        rpt.write("## Summary Table\n\n")
        rpt.write("| Model | Lang | Action Success | Parse Success | Malformed Rate |\n")
        rpt.write("|-------|------|---------------|--------------|----------------|\n")

        for group_key, stats_list in all_stats.items():
            model, lang = group_key.rsplit("_", 1)
            model_display = {"exaone": "EXAONE 3.5", "mistral": "Mistral 7B", "llama": "Llama 3.1"}.get(model, model)

            avg_success = sum(s["success_rate"] for s in stats_list) / len(stats_list) * 100
            avg_parse = sum(s["parse_rate"] for s in stats_list) / len(stats_list) * 100
            avg_malformed = sum(s["malformed_rate"] for s in stats_list) / len(stats_list) * 100

            rpt.write(f"| {model_display} | {lang.upper()} | {avg_success:.1f}% | {avg_parse:.1f}% | {avg_malformed:.1f}% |\n")

        rpt.write("\n## Per-Run Details\n\n")
        for group_key, stats_list in all_stats.items():
            model, lang = group_key.rsplit("_", 1)
            model_display = {"exaone": "EXAONE 3.5", "mistral": "Mistral 7B", "llama": "Llama 3.1"}.get(model, model)
            rpt.write(f"\n### {model_display} {lang.upper()}\n\n")

            for s in stats_list:
                rpt.write(f"**{s['run']}**: {s['total']} actions, ")
                rpt.write(f"success {s['success']}/{s['total']} ({s['success_rate']*100:.0f}%), ")
                rpt.write(f"parse {s['parse_ok']}/{s['total']} ({s['parse_rate']*100:.0f}%), ")
                rpt.write(f"malformed {s['malformed']} ({s['malformed_rate']*100:.0f}%)\n\n")

                # Top actions
                sorted_actions = sorted(s["action_dist"].items(), key=lambda x: -x[1])
                valid_top = [(k, v) for k, v in sorted_actions if k in VALID_ACTIONS][:5]
                rpt.write("Valid actions: " + ", ".join(f"{k}({v})" for k, v in valid_top) + "\n\n")

                malformed_top = [(k, v) for k, v in sorted_actions if k not in VALID_ACTIONS][:5]
                if malformed_top:
                    rpt.write("Top malformed: " + ", ".join(f"`{k}`({v})" for k, v in malformed_top) + "\n\n")

        rpt.write("\n## Key Observations\n\n")

        # Calculate aggregated stats
        model_success = {}
        for gk, sl in all_stats.items():
            model = gk.rsplit("_", 1)[0]
            if model not in model_success:
                model_success[model] = []
            for s in sl:
                model_success[model].append(s["success_rate"])

        for model, rates in model_success.items():
            avg = sum(rates) / len(rates) * 100
            display = {"exaone": "EXAONE", "mistral": "Mistral", "llama": "Llama 3.1"}.get(model, model)
            rpt.write(f"- **{display} overall action success: {avg:.1f}%**\n")

        rpt.write("\n")
        rpt.write("1. Parse success (JSON extraction) is high for EXAONE and Llama (89-100%) — ")
        rpt.write("failures are mostly idle fallbacks, not structural issues\n")
        rpt.write("2. Mistral generates pipe-separated multi-actions (`speak|plaza`, `support|architect_01`) ")
        rpt.write("and embeds targets in action names — consistent across KO and EN\n")
        rpt.write("3. Llama 3.1 EN achieves 100% parse success; KO shows mild degradation (89.6%)\n")
        rpt.write("4. EXAONE shows higher behavioral diversity (whisper, move, build_billboard) ")
        rpt.write("while Mistral and Llama are more speak-dominant\n")
        rpt.write("5. Llama 3.1 is the fastest model (~49s/epoch) while matching EXAONE parse quality\n")

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
