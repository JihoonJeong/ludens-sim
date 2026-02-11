#!/usr/bin/env python3
"""Phase 1 v0.3 본실험 로그 병합 — 5모델 30 runs 전체 병합 + 통합 summary"""

import json
import sys
import io
import re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

project_root = Path(__file__).parent.parent
logs_dir = project_root / "logs"
data_dir = project_root / "data" / "phase1"
data_dir.mkdir(parents=True, exist_ok=True)

VALID_ACTIONS = {
    "speak", "trade", "support", "whisper", "move", "idle",
    "build_billboard", "adjust_tax", "grant_subsidy",
}

MODEL_DISPLAY = {
    "exaone": "EXAONE 3.5 7.8B",
    "mistral": "Mistral 7B",
    "llama": "Llama 3.1 8B",
    "flash": "Gemini 2.0 Flash",
    "gpt4o": "GPT-4o-mini",
}

MODEL_ORDER = ["exaone", "mistral", "llama", "flash", "gpt4o"]

# Auto-discover v0.3 Phase 1 runs from logs/
# Format: 20260211_084925_239968_p1_flash_ko_01
RUN_PATTERN = re.compile(r"^\d{8}_\d{6}_\d+_p1_(\w+)_(ko|en)_(\d+)$")


def discover_runs():
    """Auto-discover all Phase 1 v0.3 runs, grouped by model_lang."""
    groups = defaultdict(list)
    for d in sorted(logs_dir.iterdir()):
        if not d.is_dir():
            continue
        m = RUN_PATTERN.match(d.name)
        if not m:
            continue
        model, lang, run_num = m.group(1), m.group(2), m.group(3)
        sim_log = d / "simulation_log.jsonl"
        if sim_log.exists() and sim_log.stat().st_size > 0:
            group_key = f"{model}_{lang}"
            groups[group_key].append({
                "dir": d.name,
                "model": model,
                "lang": lang,
                "run_num": int(run_num),
                "run_label": f"run{run_num}",
            })
    # Sort runs within each group
    for key in groups:
        groups[key].sort(key=lambda x: x["run_num"])
    return dict(groups)


def analyze_run(log_path):
    """단일 run 분석"""
    actions = Counter()
    personas = Counter()
    total = 0
    success = 0
    parse_ok = 0
    malformed = 0

    with open(log_path, encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            total += 1
            actions[entry["action_type"]] += 1
            if entry.get("persona"):
                personas[entry["persona"]] += 1
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
        "persona_dist": dict(personas),
    }


def merge_group(group_key, runs):
    """모델/언어 그룹 병합"""
    sim_out = data_dir / f"phase1_{group_key}_simulation_log.jsonl"
    epoch_out = data_dir / f"phase1_{group_key}_epoch_summary.jsonl"

    run_stats = []
    model = runs[0]["model"]
    lang = runs[0]["lang"]

    with open(sim_out, "w", encoding="utf-8") as sf, \
         open(epoch_out, "w", encoding="utf-8") as ef:

        for run in runs:
            run_dir = logs_dir / run["dir"]
            run_label = run["run_label"]

            # Merge simulation log
            sim_path = run_dir / "simulation_log.jsonl"
            with open(sim_path, encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    entry["model"] = model
                    entry["language"] = lang
                    entry["run"] = run_label
                    entry["run_id"] = f"p1_{model}_{lang}_{run['run_num']:02d}"
                    sf.write(json.dumps(entry, ensure_ascii=False) + "\n")

            # Merge epoch summary
            epoch_path = run_dir / "epoch_summary.jsonl"
            if epoch_path.exists():
                with open(epoch_path, encoding="utf-8") as f:
                    for line in f:
                        entry = json.loads(line)
                        entry["model"] = model
                        entry["language"] = lang
                        entry["run"] = run_label
                        ef.write(json.dumps(entry, ensure_ascii=False) + "\n")

            # Analyze
            stats = analyze_run(sim_path)
            stats["run"] = run_label
            stats["run_id"] = f"p1_{model}_{lang}_{run['run_num']:02d}"
            run_stats.append(stats)

    return run_stats


def generate_summary(all_stats, groups):
    """통합 Summary Markdown 생성"""
    report_path = data_dir / "phase1_v03_summary.md"

    total_runs = sum(len(v) for v in groups.values())
    total_actions = sum(s["total"] for sl in all_stats.values() for s in sl)
    models_found = sorted(set(k.rsplit("_", 1)[0] for k in groups), key=lambda m: MODEL_ORDER.index(m) if m in MODEL_ORDER else 99)

    with open(report_path, "w", encoding="utf-8") as rpt:
        rpt.write("# White Room Phase 1 — v0.3 Full Results Summary\n\n")
        rpt.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        rpt.write("## Experiment Configuration\n\n")
        rpt.write("- **Phase**: 1 (Empty Agora — shadow mode, energy frozen)\n")
        rpt.write("- **Agents per run**: 12 (homogeneous model per run)\n")
        rpt.write("- **Epochs per run**: 50\n")
        rpt.write("- **Actions per run**: 600 (12 agents x 50 epochs)\n")
        rpt.write(f"- **Models**: {', '.join(MODEL_DISPLAY.get(m, m) for m in models_found)}\n")
        rpt.write("- **Languages**: KO, EN\n")
        rpt.write("- **Runs per condition**: 3 (per model per language)\n")
        rpt.write(f"- **Total**: {total_runs} runs, {total_actions:,} actions\n\n")

        # ---- Model-level summary (averaged across KO+EN) ----
        rpt.write("## Model-Level Summary (averaged across KO+EN)\n\n")
        rpt.write("| Model | Runs | Actions | Parse Success | Action Success | Malformed |\n")
        rpt.write("|-------|------|---------|--------------|---------------|----------|\n")

        model_agg = {}
        for gk, stats_list in all_stats.items():
            model = gk.rsplit("_", 1)[0]
            if model not in model_agg:
                model_agg[model] = {"runs": 0, "total": 0, "parse_ok": 0, "success": 0, "malformed": 0}
            for s in stats_list:
                model_agg[model]["runs"] += 1
                model_agg[model]["total"] += s["total"]
                model_agg[model]["parse_ok"] += s["parse_ok"]
                model_agg[model]["success"] += s["success"]
                model_agg[model]["malformed"] += s["malformed"]

        for model in models_found:
            a = model_agg[model]
            t = a["total"]
            rpt.write(f"| {MODEL_DISPLAY.get(model, model)} | {a['runs']} | {t:,} | "
                      f"{a['parse_ok']/t*100:.1f}% | {a['success']/t*100:.1f}% | {a['malformed']/t*100:.1f}% |\n")

        # Totals row
        tt = sum(a["total"] for a in model_agg.values())
        tp = sum(a["parse_ok"] for a in model_agg.values())
        ts = sum(a["success"] for a in model_agg.values())
        tm = sum(a["malformed"] for a in model_agg.values())
        tr = sum(a["runs"] for a in model_agg.values())
        rpt.write(f"| **Total** | **{tr}** | **{tt:,}** | **{tp/tt*100:.1f}%** | **{ts/tt*100:.1f}%** | **{tm/tt*100:.1f}%** |\n")

        # ---- Breakdown by model + language ----
        rpt.write("\n## Breakdown by Model + Language\n\n")
        rpt.write("| Model | Lang | Parse Success | Action Success | Malformed | Top Actions |\n")
        rpt.write("|-------|------|--------------|---------------|----------|-------------|\n")

        ordered_keys = []
        for model in models_found:
            for lang in ["ko", "en"]:
                key = f"{model}_{lang}"
                if key in all_stats:
                    ordered_keys.append(key)

        for gk in ordered_keys:
            stats_list = all_stats[gk]
            model, lang = gk.rsplit("_", 1)
            t = sum(s["total"] for s in stats_list)
            p = sum(s["parse_ok"] for s in stats_list)
            sc = sum(s["success"] for s in stats_list)
            ml = sum(s["malformed"] for s in stats_list)

            # Aggregate action distribution
            agg_actions = Counter()
            for s in stats_list:
                agg_actions.update(s["action_dist"])
            top3 = agg_actions.most_common(3)
            top_str = ", ".join(f"{k}({v})" for k, v in top3)

            rpt.write(f"| {MODEL_DISPLAY.get(model, model)} | {lang.upper()} | "
                      f"{p/t*100:.1f}% | {sc/t*100:.1f}% | {ml/t*100:.1f}% | {top_str} |\n")

        # ---- Action Distribution ----
        rpt.write("\n## Action Distribution by Model\n\n")
        rpt.write("| Model | speak | trade | support | whisper | move | idle | other |\n")
        rpt.write("|-------|-------|-------|---------|---------|------|------|-------|\n")

        for model in models_found:
            agg = Counter()
            total = 0
            for gk, stats_list in all_stats.items():
                if gk.rsplit("_", 1)[0] == model:
                    for s in stats_list:
                        agg.update(s["action_dist"])
                        total += s["total"]

            core = ["speak", "trade", "support", "whisper", "move", "idle"]
            other = total - sum(agg.get(a, 0) for a in core)

            def pct(count):
                return f"{count/total*100:.1f}%" if total else "0%"

            rpt.write(f"| {MODEL_DISPLAY.get(model, model)} | "
                      + " | ".join(pct(agg.get(a, 0)) for a in core)
                      + f" | {pct(other)} |\n")

        # ---- Per-Run Details ----
        rpt.write("\n## Per-Run Details\n\n")
        for gk in ordered_keys:
            stats_list = all_stats[gk]
            model, lang = gk.rsplit("_", 1)
            rpt.write(f"\n### {MODEL_DISPLAY.get(model, model)} {lang.upper()}\n\n")

            for s in stats_list:
                rpt.write(f"**{s['run_id']}**: {s['total']} actions, "
                          f"parse {s['parse_ok']}/{s['total']} ({s['parse_rate']*100:.1f}%), "
                          f"success {s['success']}/{s['total']} ({s['success_rate']*100:.1f}%), "
                          f"malformed {s['malformed']}\n")

                sorted_actions = sorted(s["action_dist"].items(), key=lambda x: -x[1])
                valid_top = [(k, v) for k, v in sorted_actions if k in VALID_ACTIONS][:5]
                rpt.write("  Actions: " + ", ".join(f"{k}({v})" for k, v in valid_top) + "\n")

                malformed_top = [(k, v) for k, v in sorted_actions if k not in VALID_ACTIONS][:5]
                if malformed_top:
                    rpt.write("  Malformed: " + ", ".join(f"`{k}`({v})" for k, v in malformed_top) + "\n")
                rpt.write("\n")

        # ---- Key Observations (auto-generated) ----
        rpt.write("\n## Key Observations\n\n")

        # Rank models by parse success
        ranked = sorted(model_agg.items(), key=lambda x: x[1]["parse_ok"]/x[1]["total"], reverse=True)
        for i, (model, a) in enumerate(ranked, 1):
            t = a["total"]
            rpt.write(f"{i}. **{MODEL_DISPLAY.get(model, model)}**: "
                      f"parse {a['parse_ok']/t*100:.1f}%, "
                      f"action success {a['success']/t*100:.1f}%, "
                      f"malformed {a['malformed']/t*100:.1f}%\n")

        # KO vs EN comparison
        rpt.write("\n### Language Effect (KO vs EN)\n\n")
        rpt.write("| Model | KO Parse | EN Parse | KO Success | EN Success |\n")
        rpt.write("|-------|----------|----------|------------|------------|\n")
        for model in models_found:
            ko_key = f"{model}_ko"
            en_key = f"{model}_en"
            if ko_key in all_stats and en_key in all_stats:
                ko_t = sum(s["total"] for s in all_stats[ko_key])
                ko_p = sum(s["parse_ok"] for s in all_stats[ko_key])
                ko_s = sum(s["success"] for s in all_stats[ko_key])
                en_t = sum(s["total"] for s in all_stats[en_key])
                en_p = sum(s["parse_ok"] for s in all_stats[en_key])
                en_s = sum(s["success"] for s in all_stats[en_key])
                rpt.write(f"| {MODEL_DISPLAY.get(model, model)} | {ko_p/ko_t*100:.1f}% | {en_p/en_t*100:.1f}% | "
                          f"{ko_s/ko_t*100:.1f}% | {en_s/en_t*100:.1f}% |\n")

    return report_path


def main():
    print("=== Phase 1 v0.3 로그 병합 시작 (5 models, 30 runs) ===\n")

    groups = discover_runs()
    if not groups:
        print("ERROR: No Phase 1 v0.3 runs found in logs/")
        return

    # Show discovered runs
    for gk, runs in sorted(groups.items()):
        print(f"  {gk}: {len(runs)} runs")

    print()

    # Merge each group
    all_stats = {}
    for group_key in sorted(groups.keys()):
        runs = groups[group_key]
        print(f"Merging {group_key} ({len(runs)} runs)...")
        stats = merge_group(group_key, runs)
        all_stats[group_key] = stats

    # Create combined all-in-one files
    print("\nCreating combined files...")
    all_sim = data_dir / "phase1_all_simulation_log.jsonl"
    all_epoch = data_dir / "phase1_all_epoch_summary.jsonl"

    ordered_keys = []
    for model in MODEL_ORDER:
        for lang in ["ko", "en"]:
            key = f"{model}_{lang}"
            if key in groups:
                ordered_keys.append(key)

    with open(all_sim, "w", encoding="utf-8") as sf, \
         open(all_epoch, "w", encoding="utf-8") as ef:
        for gk in ordered_keys:
            sim_part = data_dir / f"phase1_{gk}_simulation_log.jsonl"
            if sim_part.exists():
                with open(sim_part, encoding="utf-8") as f:
                    sf.write(f.read())
            epoch_part = data_dir / f"phase1_{gk}_epoch_summary.jsonl"
            if epoch_part.exists():
                with open(epoch_part, encoding="utf-8") as f:
                    ef.write(f.read())

    # Generate summary
    print("Generating summary report...")
    report_path = generate_summary(all_stats, groups)

    # File listing
    print(f"\nFiles generated in {data_dir}:")
    for f in sorted(data_dir.iterdir()):
        size = f.stat().st_size
        if size > 1024 * 1024:
            print(f"  {f.name}: {size / 1024 / 1024:.1f} MB")
        else:
            print(f"  {f.name}: {size / 1024:.1f} KB")

    # Quick summary
    total_runs = sum(len(v) for v in groups.values())
    total_actions = sum(s["total"] for sl in all_stats.values() for s in sl)
    print(f"\nTotal: {total_runs} runs, {total_actions:,} actions merged.")
    print(f"Summary: {report_path.name}")
    print("Done!")


if __name__ == "__main__":
    main()
