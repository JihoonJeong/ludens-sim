"""Environment 테스트 — 공간 이동, 게시판, 용량 제한"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from games.white_room.environment import Environment


@pytest.fixture
def env():
    return Environment({
        "plaza": {"capacity": 12, "visibility": "public"},
        "market": {"capacity": 12, "visibility": "public"},
        "alley_a": {"capacity": 4, "visibility": "members_only"},
        "alley_b": {"capacity": 4, "visibility": "members_only"},
        "alley_c": {"capacity": 4, "visibility": "members_only"},
    })


class TestPlacement:

    def test_place_agent(self, env):
        assert env.place_agent("agent_01", "plaza") is True
        assert "agent_01" in env.get_agents_at("plaza")

    def test_place_duplicate(self, env):
        env.place_agent("agent_01", "plaza")
        env.place_agent("agent_01", "plaza")
        assert env.get_agents_at("plaza").count("agent_01") == 1

    def test_place_invalid_location(self, env):
        assert env.place_agent("agent_01", "heaven") is False

    def test_capacity_limit(self, env):
        for i in range(4):
            assert env.place_agent(f"a{i}", "alley_a") is True
        assert env.place_agent("a4", "alley_a") is False


class TestMovement:

    def test_move_agent(self, env):
        env.place_agent("agent_01", "plaza")
        assert env.move_agent("agent_01", "plaza", "market") is True
        assert "agent_01" not in env.get_agents_at("plaza")
        assert "agent_01" in env.get_agents_at("market")

    def test_move_to_full_space(self, env):
        for i in range(4):
            env.place_agent(f"a{i}", "alley_a")
        env.place_agent("mover", "plaza")
        assert env.move_agent("mover", "plaza", "alley_a") is False
        assert "mover" in env.get_agents_at("plaza")

    def test_move_to_invalid(self, env):
        env.place_agent("agent_01", "plaza")
        assert env.move_agent("agent_01", "plaza", "heaven") is False


class TestBillboard:

    def test_post_billboard(self, env):
        env.post_billboard("Hello world", "architect_01", duration=2)
        assert env.get_billboard() == "Hello world"

    def test_billboard_expires(self, env):
        env.post_billboard("Notice", "architect_01", duration=2)
        env.tick_billboard()
        assert env.get_billboard() == "Notice"  # 1 epoch remaining
        env.tick_billboard()
        assert env.get_billboard() is None  # expired

    def test_billboard_info(self, env):
        env.post_billboard("Msg", "arch_01", duration=3)
        info = env.get_billboard_info()
        assert info["message"] == "Msg"
        assert info["poster"] == "arch_01"
        assert info["remaining"] == 3

    def test_no_billboard(self, env):
        assert env.get_billboard() is None


class TestTaxRate:

    def test_default_tax(self, env):
        assert env.tax_rate == 0.1

    def test_set_tax_clamped(self, env):
        env.set_tax_rate(0.5)
        assert env.tax_rate == 0.3  # max 30%
        env.set_tax_rate(-0.1)
        assert env.tax_rate == 0.0  # min 0%
        env.set_tax_rate(0.2)
        assert env.tax_rate == 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
