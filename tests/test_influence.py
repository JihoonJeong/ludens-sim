"""Influence 계급 시스템 테스트"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from games.white_room.systems.influence import InfluenceSystem


@pytest.fixture
def inf():
    return InfluenceSystem()


class TestTiers:

    def test_commoner(self, inf):
        tier = inf.get_tier(0)
        assert tier["name"] == "commoner"
        tier = inf.get_tier(4)
        assert tier["name"] == "commoner"

    def test_notable(self, inf):
        tier = inf.get_tier(5)
        assert tier["name"] == "notable"
        tier = inf.get_tier(9)
        assert tier["name"] == "notable"

    def test_elder(self, inf):
        tier = inf.get_tier(10)
        assert tier["name"] == "elder"
        tier = inf.get_tier(50)
        assert tier["name"] == "elder"


class TestRankName:

    def test_ko(self, inf):
        assert inf.get_rank_name(0, "ko") == "평민"
        assert inf.get_rank_name(5, "ko") == "유력자"
        assert inf.get_rank_name(10, "ko") == "원로"

    def test_en(self, inf):
        assert inf.get_rank_name(0, "en") == "Commoner"
        assert inf.get_rank_name(5, "en") == "Notable"
        assert inf.get_rank_name(10, "en") == "Elder"


class TestSupportMultiplier:

    def test_commoner_no_bonus(self, inf):
        assert inf.get_support_multiplier(3) == 1.0

    def test_notable_no_bonus(self, inf):
        assert inf.get_support_multiplier(7) == 1.0

    def test_elder_bonus(self, inf):
        assert inf.get_support_multiplier(10) == 1.5
        assert inf.get_support_multiplier(20) == 1.5


class TestRankBonusPrompt:

    def test_commoner_empty(self, inf):
        assert inf.get_rank_bonus_prompt(2, "ko") == ""

    def test_notable_ko(self, inf):
        prompt = inf.get_rank_bonus_prompt(5, "ko")
        assert "발언 가중치" in prompt

    def test_notable_en(self, inf):
        prompt = inf.get_rank_bonus_prompt(5, "en")
        assert "Speak weight" in prompt

    def test_elder_ko(self, inf):
        prompt = inf.get_rank_bonus_prompt(10, "ko")
        assert "×1.5" in prompt
        assert "이의 제기" in prompt

    def test_elder_en(self, inf):
        prompt = inf.get_rank_bonus_prompt(10, "en")
        assert "1.5" in prompt
        assert "contest" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
