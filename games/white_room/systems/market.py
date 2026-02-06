"""시장 시스템 — MarketPool + Treasury"""

from dataclasses import dataclass, field
from typing import Optional


class MarketPool:
    """시장 에너지 풀 — 에폭마다 에너지 생성, 거래자에게 분배"""

    def __init__(self, spawn_per_epoch: int = 25, min_presence_reward: int = 2):
        self.spawn_per_epoch = spawn_per_epoch
        self.min_presence_reward = min_presence_reward
        self.epoch_trades: dict[int, dict[str, int]] = {}  # epoch -> {agent_id: trade_count}

    def record_trade(self, epoch: int, agent_id: str):
        if epoch not in self.epoch_trades:
            self.epoch_trades[epoch] = {}
        self.epoch_trades[epoch][agent_id] = self.epoch_trades[epoch].get(agent_id, 0) + 1

    def get_trade_count(self, epoch: int) -> int:
        return sum(self.epoch_trades.get(epoch, {}).values())

    def distribute_pool(
        self,
        epoch: int,
        market_agent_ids: list[str],
        tax_rate: float = 0.1,
    ) -> dict:
        """
        시장 풀 분배. activity_weighted 방식.
        Returns: {
            "distribution": {agent_id: amount},
            "total_pool": int,
            "tax_collected": float,
            "trades": {agent_id: count},
        }
        """
        trades = self.epoch_trades.get(epoch, {})
        total_pool = self.spawn_per_epoch
        distribution = {}
        tax_collected = 0.0

        if not market_agent_ids:
            return {
                "distribution": {},
                "total_pool": total_pool,
                "tax_collected": 0.0,
                "trades": trades,
            }

        # 비거래자 최소 보상
        non_traders = [a for a in market_agent_ids if a not in trades]
        trader_ids = [a for a in market_agent_ids if a in trades]

        min_reward_total = len(non_traders) * self.min_presence_reward
        remaining_pool = max(0, total_pool - min_reward_total)

        for agent_id in non_traders:
            distribution[agent_id] = self.min_presence_reward

        # 거래자 비례 분배
        if trader_ids:
            total_trades = sum(trades[a] for a in trader_ids)
            for agent_id in trader_ids:
                share = (trades[agent_id] / total_trades) * remaining_pool
                # 세금 차감
                tax = share * tax_rate
                tax_collected += tax
                distribution[agent_id] = int(share - tax)

        return {
            "distribution": distribution,
            "total_pool": total_pool,
            "tax_collected": tax_collected,
            "trades": dict(trades),
        }


class Treasury:
    """공공자금"""

    def __init__(self, initial: float = 0, overflow_threshold: float = 100):
        self.balance = initial
        self.overflow_threshold = overflow_threshold

    def collect_tax(self, amount: float):
        self.balance += amount

    def grant_subsidy(self, amount: float) -> bool:
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

    def check_overflow(self) -> float:
        """overflow_threshold 초과분 반환 (풀로 환류용)"""
        if self.balance > self.overflow_threshold:
            overflow = self.balance - self.overflow_threshold
            self.balance = self.overflow_threshold
            return overflow
        return 0.0
