"""시뮬레이션 로거 — JSONL 기반"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


def calculate_gini(values: list[float]) -> float:
    """지니 계수 계산 (0=완전 평등, 1=완전 불평등)"""
    if not values:
        return 0.0
    n = len(values)
    total = sum(values)
    if total == 0:
        return 0.0
    sorted_vals = sorted(values)
    gini_sum = sum((2 * (i + 1) - n - 1) * v for i, v in enumerate(sorted_vals))
    return gini_sum / (n * total)


class SimulationLogger:

    def __init__(self, base_dir: str = "logs", run_name: Optional[str] = None):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        run_name = run_name or "run"
        self.run_dir = Path(base_dir) / f"{timestamp}_{run_name}"
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.action_log_path = self.run_dir / "simulation_log.jsonl"
        self.epoch_log_path = self.run_dir / "epoch_summary.jsonl"
        self.config_path = self.run_dir / "config_snapshot.json"

        self._turn_counter = 0

    def save_config(self, config: dict):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def log_action(
        self,
        epoch: int,
        agent_id: str,
        persona: str,
        location: str,
        action_type: str,
        target: Optional[str],
        content: Optional[str],
        thought: str,
        success: bool,
        resources_before: dict,
        resources_after: dict,
        extra: Optional[dict] = None,
        *,
        v03: bool = False,
    ):
        self._turn_counter += 1
        if v03:
            # v0.3 스키마: 필드명 변경
            entry = {
                "epoch": epoch,
                "turn": self._turn_counter,
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id,
                "persona": persona,
                "location": location,
                "action_type": action_type,
                "action_target": target,
                "action_content": content,
                "thought": thought,
                "action_success": success,
            }
        else:
            # 파일럿/레거시 스키마
            entry = {
                "epoch": epoch,
                "turn": self._turn_counter,
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id,
                "persona": persona,
                "location": location,
                "action_type": action_type,
                "target": target,
                "content": content,
                "thought": thought,
                "success": success,
                "resources_before": resources_before,
                "resources_after": resources_after,
            }
        if extra:
            entry.update(extra)

        self._append_jsonl(self.action_log_path, entry)

    def save_run_meta(self, meta: dict):
        """Run 메타데이터 저장 (v0.3 §4.2)"""
        meta_path = self.run_dir / "run_meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    def log_epoch_summary(
        self,
        epoch: int,
        agent_count: int,
        energy_values: list[float],
        transaction_count: int,
        treasury: float,
        billboard: Optional[str] = None,
        notable_events: Optional[list[str]] = None,
        extra: Optional[dict] = None,
    ):
        entry = {
            "epoch": epoch,
            "timestamp": datetime.now().isoformat(),
            "agent_count": agent_count,
            "total_energy": sum(energy_values),
            "gini_coefficient": calculate_gini(energy_values),
            "transaction_count": transaction_count,
            "treasury": treasury,
            "billboard_active": billboard,
            "notable_events": notable_events or [],
        }
        if extra:
            entry.update(extra)

        self._append_jsonl(self.epoch_log_path, entry)

    def reset_turn_counter(self):
        self._turn_counter = 0

    def _append_jsonl(self, path: Path, entry: dict):
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
