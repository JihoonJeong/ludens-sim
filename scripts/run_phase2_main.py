#!/usr/bin/env python3
"""Phase 2 본실험 배치 — 14 runs 순차 실행"""

import subprocess
import sys
import io
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

project_root = Path(__file__).parent.parent
config_dir = project_root / "games" / "white_room" / "config" / "phase2" / "main"
logs_dir = project_root / "logs"
python = str(project_root / ".venv" / "Scripts" / "python.exe")
run_script = str(project_root / "scripts" / "run_simulation.py")

# 실행 순서 (v0.3 §5.4)
RUN_ORDER = [
    # Baseline KO
    "p2_base_ko_01", "p2_base_ko_02", "p2_base_ko_03",
    # Baseline EN
    "p2_base_en_01", "p2_base_en_02", "p2_base_en_03",
    # Experimental KO (Latin Square 1~4)
    "p2_exp_r1_ko", "p2_exp_r2_ko", "p2_exp_r3_ko", "p2_exp_r4_ko",
    # Experimental EN (Latin Square 1~4)
    "p2_exp_r1_en", "p2_exp_r2_en", "p2_exp_r3_en", "p2_exp_r4_en",
]


def is_run_completed(run_id: str) -> bool:
    """logs/ 에 해당 run_id를 포함하는 디렉토리가 있으면 완료로 간주"""
    for d in logs_dir.iterdir():
        if d.is_dir() and run_id in d.name:
            sim_log = d / "simulation_log.jsonl"
            if sim_log.exists() and sim_log.stat().st_size > 0:
                return True
    return False


def main():
    print("=== Phase 2 Main Experiment — 14 Runs ===\n")

    completed = 0
    skipped = 0
    failed = 0
    total = len(RUN_ORDER)

    for i, run_id in enumerate(RUN_ORDER, 1):
        config_path = config_dir / f"{run_id}.yaml"
        if not config_path.exists():
            print(f"[{i}/{total}] {run_id}: CONFIG NOT FOUND — {config_path}")
            failed += 1
            continue

        if is_run_completed(run_id):
            print(f"[{i}/{total}] {run_id}: SKIP (already completed)")
            skipped += 1
            continue

        print(f"\n[{i}/{total}] {run_id}: STARTING...")
        start = time.time()

        try:
            result = subprocess.run(
                [python, run_script, "--config", str(config_path)],
                cwd=str(project_root),
                timeout=3600 * 4,  # 4시간 타임아웃
                errors="replace",
            )
            elapsed = time.time() - start

            if result.returncode == 0:
                print(f"[{i}/{total}] {run_id}: DONE ({elapsed/60:.1f} min)")
                completed += 1
            else:
                print(f"[{i}/{total}] {run_id}: FAILED (exit code {result.returncode}, {elapsed/60:.1f} min)")
                failed += 1

        except subprocess.TimeoutExpired:
            elapsed = time.time() - start
            print(f"[{i}/{total}] {run_id}: TIMEOUT ({elapsed/60:.1f} min)")
            failed += 1

        except Exception as e:
            print(f"[{i}/{total}] {run_id}: ERROR — {e}")
            failed += 1

    print(f"\n=== Summary ===")
    print(f"Completed: {completed}, Skipped: {skipped}, Failed: {failed}, Total: {total}")


if __name__ == "__main__":
    main()
