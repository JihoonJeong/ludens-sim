"""Whisper 누출 시스템 테스트"""

import sys
import random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from games.white_room.systems.whisper import WhisperSystem


class TestWhisperDelivery:

    def test_basic_delivery(self):
        ws = WhisperSystem(base_leak_prob=0.0)
        result = ws.process_whisper(
            "sender", "target", "secret",
            ["sender", "target", "bystander"],
            {"sender": "jester", "target": "citizen", "bystander": "citizen"},
        )
        assert result.delivered is True
        assert result.leaked is False

    def test_disabled_system(self):
        ws = WhisperSystem(enabled=False)
        result = ws.process_whisper(
            "sender", "target", "secret",
            ["sender", "target", "bystander"],
            {"sender": "jester", "target": "citizen", "bystander": "citizen"},
        )
        assert result.delivered is True
        assert result.leaked is False
        assert result.observers == []


class TestLeakProbability:

    def test_guaranteed_leak(self):
        ws = WhisperSystem(base_leak_prob=1.0)
        result = ws.process_whisper(
            "sender", "target", "secret",
            ["sender", "target", "bystander"],
            {"sender": "jester", "target": "citizen", "bystander": "citizen"},
        )
        assert result.leaked is True
        assert "bystander" in result.suspicion_targets

    def test_no_leak(self):
        ws = WhisperSystem(base_leak_prob=0.0)
        result = ws.process_whisper(
            "sender", "target", "secret",
            ["sender", "target", "bystander"],
            {"sender": "jester", "target": "citizen", "bystander": "citizen"},
        )
        assert result.leaked is False
        assert result.suspicion_targets == []


class TestObserverBonus:

    def test_observer_increases_leak_prob(self):
        """Observer가 있으면 base 0.15 + bonus 0.35 = 0.50"""
        ws = WhisperSystem(base_leak_prob=0.15, observer_bonus=0.35)
        random.seed(42)

        # 100번 시도하여 통계적 검증
        leak_count = 0
        for _ in range(1000):
            result = ws.process_whisper(
                "sender", "target", "secret",
                ["sender", "target", "observer_01"],
                {"sender": "jester", "target": "citizen", "observer_01": "observer"},
            )
            if result.leaked:
                leak_count += 1

        # 50% ± 5% 범위 (p=0.50, 1000 trials)
        assert 400 < leak_count < 600, f"Leak rate: {leak_count/1000:.2f}"

    def test_observer_detected(self):
        ws = WhisperSystem(base_leak_prob=1.0, observer_bonus=0.35)
        result = ws.process_whisper(
            "sender", "target", "secret",
            ["sender", "target", "observer_01"],
            {"sender": "jester", "target": "citizen", "observer_01": "observer"},
        )
        assert "observer_01" in result.observers

    def test_no_bystanders_no_leak(self):
        """목격자가 없으면 누출돼도 suspicion 대상 없음"""
        ws = WhisperSystem(base_leak_prob=1.0)
        result = ws.process_whisper(
            "sender", "target", "secret",
            ["sender", "target"],
            {"sender": "jester", "target": "citizen"},
        )
        assert result.leaked is True
        assert result.suspicion_targets == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
