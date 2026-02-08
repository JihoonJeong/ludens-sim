#!/usr/bin/env python3
"""Phase 1 API 모델 배치 실행 — Haiku + Flash (Cody / Mac Lab)

12 runs: Haiku KO/EN × 3 + Flash KO/EN × 3
각 run: 12 에이전트, 50 에폭
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
python = sys.executable

RUNS = [
    # Haiku KO × 3
    "games/white_room/config/phase1/phase1_haiku_ko_run1.yaml",
    "games/white_room/config/phase1/phase1_haiku_ko_run2.yaml",
    "games/white_room/config/phase1/phase1_haiku_ko_run3.yaml",
    # Haiku EN × 3
    "games/white_room/config/phase1/phase1_haiku_en_run1.yaml",
    "games/white_room/config/phase1/phase1_haiku_en_run2.yaml",
    "games/white_room/config/phase1/phase1_haiku_en_run3.yaml",
    # Flash KO × 3
    "games/white_room/config/phase1/phase1_flash_ko_run1.yaml",
    "games/white_room/config/phase1/phase1_flash_ko_run2.yaml",
    "games/white_room/config/phase1/phase1_flash_ko_run3.yaml",
    # Flash EN × 3
    "games/white_room/config/phase1/phase1_flash_en_run1.yaml",
    "games/white_room/config/phase1/phase1_flash_en_run2.yaml",
    "games/white_room/config/phase1/phase1_flash_en_run3.yaml",
]


def main():
    print(f"=== Phase 1 API 배치 시작 (Haiku + Flash): {datetime.now().isoformat()} ===")
    print(f"총 {len(RUNS)} runs, 각 12 agents × 50 epochs = 600 calls/run\n")

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
        )

        elapsed = time.time() - start
        status = "OK" if result.returncode == 0 else "FAIL"
        results.append((config_name, status, elapsed))

        print(f"    {status} ({elapsed:.0f}s)")
        if result.returncode != 0:
            print(f"    ERROR: {result.stderr[:500]}")
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
    fail_count = len(results) - ok_count
    print(f"Total: {ok_count}/{len(results)} OK, {fail_count} FAIL, {total_time:.0f}s ({total_time/60:.1f}m)")


if __name__ == "__main__":
    main()
