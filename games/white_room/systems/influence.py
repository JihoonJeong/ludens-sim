"""영향력 계급 시스템"""

from typing import Optional


# 기본 tier 설정
DEFAULT_TIERS = [
    {"name": "commoner", "min": 0, "max": 4, "title_ko": "평민", "title_en": "Commoner"},
    {"name": "notable", "min": 5, "max": 9, "title_ko": "유력자", "title_en": "Notable"},
    {"name": "elder", "min": 10, "max": 999, "title_ko": "원로", "title_en": "Elder"},
]


class InfluenceSystem:

    def __init__(self, tiers: Optional[list[dict]] = None):
        self.tiers = tiers or DEFAULT_TIERS

    def get_tier(self, influence: int) -> dict:
        """영향력에 따른 tier 반환"""
        for tier in self.tiers:
            if tier["min"] <= influence <= tier["max"]:
                return tier
        return self.tiers[0]

    def get_rank_name(self, influence: int, lang: str = "ko") -> str:
        tier = self.get_tier(influence)
        return tier[f"title_{lang}"]

    def get_support_multiplier(self, influence: int) -> float:
        """Elder는 support 에너지 ×1.5"""
        tier = self.get_tier(influence)
        return 1.5 if tier["name"] == "elder" else 1.0

    def get_rank_bonus_prompt(self, influence: int, lang: str = "ko") -> str:
        """계급 보너스 프롬프트"""
        tier = self.get_tier(influence)
        if tier["name"] == "notable":
            if lang == "ko":
                return "- 계급 보너스: 발언 가중치 보너스"
            return "- Rank bonus: Speak weight bonus"
        elif tier["name"] == "elder":
            if lang == "ko":
                return "- 계급 보너스: 지지 ×1.5배, 건축가 결정 이의 제기 가능"
            return "- Rank bonus: Support ×1.5, can contest architect decisions"
        return ""
