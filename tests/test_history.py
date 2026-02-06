"""History Engine 테스트"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from games.white_room.history import HistoryEngine


@pytest.fixture
def history():
    h = HistoryEngine()
    h.add_event(1, "test", "테스트 이벤트 1", "Test event 1", importance=1)
    h.add_tax_change(3, "architect_01", 0.1, 0.2)
    h.add_billboard(5, "architect_01", "공지사항")
    h.add_whisper_leak(7, "jester_01", "merchant_01")
    h.add_mutual_support(10, "influencer_01", "citizen_01")
    return h


class TestEventAdding:

    def test_event_count(self, history):
        assert len(history.events) == 5

    def test_importance_clamped(self):
        h = HistoryEngine()
        h.add_event(1, "test", "t", "t", importance=10)
        assert h.events[0].importance == 5
        h.add_event(1, "test", "t", "t", importance=-1)
        assert h.events[1].importance == 1

    def test_tax_change_agents(self, history):
        tax_event = [e for e in history.events if e.event_type == "tax_change"][0]
        assert "architect_01" in tax_event.agents_involved

    def test_mutual_support_agents(self, history):
        ms = [e for e in history.events if e.event_type == "mutual_support"][0]
        assert "influencer_01" in ms.agents_involved
        assert "citizen_01" in ms.agents_involved


class TestSummary:

    def test_summary_ko(self, history):
        summary = history.get_summary(max_events=10, lang="ko")
        assert "에폭" in summary
        assert "세율" in summary
        assert "누출" in summary

    def test_summary_en(self, history):
        summary = history.get_summary(max_events=10, lang="en")
        assert "Epoch" in summary
        assert "tax rate" in summary
        assert "leaked" in summary

    def test_summary_limit(self, history):
        summary = history.get_summary(max_events=2, lang="ko")
        lines = [l for l in summary.strip().split("\n") if l.startswith("[")]
        assert len(lines) <= 2

    def test_empty_summary_ko(self):
        h = HistoryEngine()
        assert "아직" in h.get_summary(lang="ko")

    def test_empty_summary_en(self):
        h = HistoryEngine()
        assert "No recorded" in h.get_summary(lang="en")

    def test_importance_ordering(self):
        """높은 importance가 우선 선택됨"""
        h = HistoryEngine()
        h.add_event(1, "low", "낮은", "low", importance=1)
        h.add_event(2, "high", "높은", "high", importance=5)
        h.add_event(3, "mid", "중간", "mid", importance=3)
        summary = h.get_summary(max_events=2, lang="ko")
        assert "높은" in summary
        assert "중간" in summary
        assert "낮은" not in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
