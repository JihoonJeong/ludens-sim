#!/usr/bin/env python3
"""Phase 1 본실험 배치 실행 — 12 runs 순차 실행"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
python = sys.executable

RUNS = [
    # EXAONE KO run1, run2 완료 — run3부터 재시작
    "games/white_room/config/phase1/phase1_exaone_ko_run3.yaml",
    # EXAONE EN × 3
    "games/white_room/config/phase1/phase1_exaone_en_run1.yaml",
    "games/white_room/config/phase1/phase1_exaone_en_run2.yaml",
    "games/white_room/config/phase1/phase1_exaone_en_run3.yaml",
    # Mistral EN × 3
    "games/white_room/config/phase1/phase1_mistral_en_run1.yaml",
    "games/white_room/config/phase1/phase1_mistral_en_run2.yaml",
    "games/white_room/config/phase1/phase1_mistral_en_run3.yaml",
    # Mistral KO × 3
    "games/white_room/config/phase1/phase1_mistral_ko_run1.yaml",
    "games/white_room/config/phase1/phase1_mistral_ko_run2.yaml",
    "games/white_room/config/phase1/phase1_mistral_ko_run3.yaml",
]

def main():
    print(f"=== Phase 1 본실험 배치 시작: {datetime.now().isoformat()} ===")
    print(f"총 {len(RUNS)} runs, 각 50 에폭\n")

    results = []
    for i, config in enumerate(RUNS, 1):
        config_name = Path(config).stem
        print(f"--- [{i}/{len(RUNS)}] {config_name} 시작: {datetime.now().strftime('%H:%M:%S')} ---")
        start = time.time()

        result = subprocess.run(
            [python, "scripts/run_simulation.py", "--config", config],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        elapsed = time.time() - start
        status = "OK" if result.returncode == 0 else "FAIL"
        results.append((config_name, status, elapsed))

        print(f"    {status} ({elapsed:.0f}s)")
        if result.returncode != 0:
            print(f"    ERROR: {result.stderr[:200]}")
        print()

    print(f"\n=== 배치 완료: {datetime.now().isoformat()} ===")
    print(f"{'Run':<40} {'Status':<8} {'Time':>8}")
    print("-" * 58)
    total_time = 0
    for name, status, elapsed in results:
        print(f"{name:<40} {status:<8} {elapsed:>7.0f}s")
        total_time += elapsed
    print("-" * 58)
    ok_count = sum(1 for _, s, _ in results if s == "OK")
    print(f"Total: {ok_count}/{len(results)} OK, {total_time:.0f}s ({total_time/3600:.1f}h)")


if __name__ == "__main__":
    main()
