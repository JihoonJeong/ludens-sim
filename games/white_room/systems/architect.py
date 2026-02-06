"""Architect 전용 스킬 시스템"""

from typing import Optional


class ArchitectSystem:

    def __init__(
        self,
        billboard_cost: int = 10,
        tax_adjust_cost: int = 5,
        min_tax_rate: float = 0.0,
        max_tax_rate: float = 0.3,
    ):
        self.billboard_cost = billboard_cost
        self.tax_adjust_cost = tax_adjust_cost
        self.min_tax_rate = min_tax_rate
        self.max_tax_rate = max_tax_rate

    def build_billboard(
        self,
        agent_energy: int,
        message: str,
        frozen: bool = False,
    ) -> tuple[bool, dict]:
        """
        광장에 공지 게시.
        Returns: (success, result_dict)
        """
        if not frozen and agent_energy < self.billboard_cost:
            return False, {"error": "insufficient_energy"}

        return True, {
            "message": message,
            "cost": self.billboard_cost,
            "duration": 2,
        }

    def adjust_tax(
        self,
        agent_energy: int,
        new_rate: float,
        frozen: bool = False,
    ) -> tuple[bool, dict]:
        """세율 조정 (0~30%)"""
        if not frozen and agent_energy < self.tax_adjust_cost:
            return False, {"error": "insufficient_energy"}

        clamped_rate = max(self.min_tax_rate, min(self.max_tax_rate, new_rate))

        return True, {
            "new_rate": clamped_rate,
            "cost": self.tax_adjust_cost,
        }

    def grant_subsidy(
        self,
        treasury_balance: float,
        amount: float,
        target_id: str,
    ) -> tuple[bool, dict]:
        """공공자금에서 보조금 지급"""
        if treasury_balance < amount:
            return False, {"error": "insufficient_treasury"}

        return True, {
            "target": target_id,
            "amount": amount,
        }
