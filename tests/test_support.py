"""Support 추적 시스템 테스트"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from games.white_room.systems.support import SupportTracker


@pytest.fixture
def tracker():
    t = SupportTracker()
    t.add_support(1, "A", "B")
    t.add_support(1, "A", "B")
    t.add_support(2, "B", "A")
    t.add_support(3, "C", "A")
    return t


class TestCounting:

    def test_count_received(self, tracker):
        assert tracker.count_received("B") == 2
        assert tracker.count_received("A") == 2  # from B and C

    def test_count_given(self, tracker):
        assert tracker.count_given("A") == 2
        assert tracker.count_given("B") == 1
        assert tracker.count_given("C") == 1


class TestRelationships:

    def test_get_supporters(self, tracker):
        supporters = tracker.get_supporters("B")
        assert "A" in supporters

    def test_get_supported_by(self, tracker):
        supported = tracker.get_supported_by("A")
        assert "B" in supported

    def test_mutual_support(self, tracker):
        mutual = tracker.get_mutual_supporters("A")
        assert "B" in mutual  # A→B, B→A
        assert "C" not in mutual

    def test_top_supporters(self, tracker):
        top = tracker.get_top_supporters("B", limit=3)
        assert top[0] == ("A", 2)


class TestContextBuilding:

    def test_context_ko(self, tracker):
        ctx = tracker.build_support_context("A", "ko")
        assert "받은 지지: 2회" in ctx
        assert "보낸 지지: 2회" in ctx

    def test_context_en(self, tracker):
        ctx = tracker.build_support_context("A", "en")
        assert "Received: 2" in ctx
        assert "Given: 2" in ctx

    def test_empty_context(self):
        t = SupportTracker()
        ctx = t.build_support_context("nobody", "ko")
        assert "0회" in ctx


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
