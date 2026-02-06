"""Market 시스템 테스트 — shadow mode 포함"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from games.white_room.systems.market import MarketPool, Treasury
from games.white_room.agent import Agent


class TestMarketPool:

    def test_record_trade(self):
        pool = MarketPool()
        pool.record_trade(1, "merchant_01")
        pool.record_trade(1, "merchant_01")
        pool.record_trade(1, "merchant_02")
        assert pool.get_trade_count(1) == 3

    def test_distribute_no_traders(self):
        pool = MarketPool(spawn_per_epoch=25, min_presence_reward=2)
        result = pool.distribute_pool(1, ["agent_a", "agent_b"])
        # 비거래자 최소 보상
        assert result["distribution"]["agent_a"] == 2
        assert result["distribution"]["agent_b"] == 2

    def test_distribute_with_traders(self):
        pool = MarketPool(spawn_per_epoch=25, min_presence_reward=2)
        pool.record_trade(1, "trader_a")
        pool.record_trade(1, "trader_a")
        pool.record_trade(1, "trader_b")

        result = pool.distribute_pool(
            1, ["trader_a", "trader_b", "bystander"], tax_rate=0.1,
        )
        # bystander gets min reward (2)
        assert result["distribution"]["bystander"] == 2
        # traders split remaining 23 by trade count (2:1 ratio), minus 10% tax
        assert result["distribution"]["trader_a"] > result["distribution"]["trader_b"]
        assert result["tax_collected"] > 0

    def test_empty_market(self):
        pool = MarketPool()
        result = pool.distribute_pool(1, [])
        assert result["distribution"] == {}


class TestTreasury:

    def test_collect_tax(self):
        t = Treasury(initial=0)
        t.collect_tax(10.0)
        assert t.balance == 10.0

    def test_grant_subsidy_success(self):
        t = Treasury(initial=50)
        assert t.grant_subsidy(20.0)
        assert t.balance == 30.0

    def test_grant_subsidy_insufficient(self):
        t = Treasury(initial=10)
        assert not t.grant_subsidy(20.0)
        assert t.balance == 10.0

    def test_overflow(self):
        t = Treasury(initial=150, overflow_threshold=100)
        overflow = t.check_overflow()
        assert overflow == 50.0
        assert t.balance == 100.0

    def test_no_overflow(self):
        t = Treasury(initial=50, overflow_threshold=100)
        overflow = t.check_overflow()
        assert overflow == 0.0


class TestShadowMode:
    """에너지 frozen 상태에서 에이전트 에너지가 변하지 않는지 검증"""

    def test_agent_energy_frozen_spend(self):
        agent = Agent(id="test", persona="citizen", energy=100)
        result = agent.spend_energy(10, frozen=True)
        assert result is True
        assert agent.energy == 100  # 변경 없음

    def test_agent_energy_frozen_gain(self):
        agent = Agent(id="test", persona="citizen", energy=100)
        agent.gain_energy(50, frozen=True)
        assert agent.energy == 100  # 변경 없음

    def test_agent_energy_normal_spend(self):
        agent = Agent(id="test", persona="citizen", energy=100)
        result = agent.spend_energy(10, frozen=False)
        assert result is True
        assert agent.energy == 90

    def test_agent_energy_normal_gain(self):
        agent = Agent(id="test", persona="citizen", energy=100)
        agent.gain_energy(50, frozen=False)
        assert agent.energy == 150

    def test_agent_energy_max_cap(self):
        agent = Agent(id="test", persona="citizen", energy=190)
        agent.gain_energy(50, frozen=False, max_energy=200)
        assert agent.energy == 200

    def test_agent_insufficient_energy(self):
        agent = Agent(id="test", persona="citizen", energy=5)
        result = agent.spend_energy(10, frozen=False)
        assert result is False
        assert agent.energy == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
