"""Action 검증 테스트"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from games.white_room.actions import (
    can_perform_action, get_available_actions, get_action_cost,
    ActionType, speak_reward,
)


class TestCanPerformAction:

    def test_speak_allowed_everywhere(self):
        for loc in ["plaza", "market", "alley_a", "alley_b", "alley_c"]:
            assert can_perform_action("speak", loc, "citizen")

    def test_trade_only_in_market(self):
        assert can_perform_action("trade", "market", "citizen")
        assert not can_perform_action("trade", "plaza", "citizen")
        assert not can_perform_action("trade", "alley_a", "citizen")

    def test_whisper_only_in_alley(self):
        assert can_perform_action("whisper", "alley_a", "citizen")
        assert can_perform_action("whisper", "alley_b", "citizen")
        assert not can_perform_action("whisper", "plaza", "citizen")
        assert not can_perform_action("whisper", "market", "citizen")

    def test_architect_skills_only_for_architect(self):
        assert can_perform_action("build_billboard", "plaza", "architect")
        assert not can_perform_action("build_billboard", "plaza", "citizen")
        assert can_perform_action("adjust_tax", "plaza", "architect")
        assert not can_perform_action("adjust_tax", "plaza", "merchant")

    def test_move_allowed_everywhere(self):
        for loc in ["plaza", "market", "alley_a"]:
            assert can_perform_action("move", loc, "citizen")

    def test_idle_allowed_everywhere(self):
        for loc in ["plaza", "market", "alley_a"]:
            assert can_perform_action("idle", loc, "citizen")

    def test_invalid_action(self):
        assert not can_perform_action("fly", "plaza", "citizen")


class TestGetAvailableActions:

    def test_plaza_actions(self):
        actions = get_available_actions("plaza", "citizen")
        assert ActionType.SPEAK in actions
        assert ActionType.SUPPORT in actions
        assert ActionType.MOVE in actions
        assert ActionType.IDLE in actions
        assert ActionType.TRADE not in actions
        assert ActionType.WHISPER not in actions

    def test_market_actions(self):
        actions = get_available_actions("market", "citizen")
        assert ActionType.TRADE in actions
        assert ActionType.WHISPER not in actions

    def test_alley_actions(self):
        actions = get_available_actions("alley_a", "citizen")
        assert ActionType.WHISPER in actions
        assert ActionType.TRADE not in actions

    def test_architect_has_special_actions(self):
        actions = get_available_actions("plaza", "architect")
        assert ActionType.BUILD_BILLBOARD in actions
        assert ActionType.ADJUST_TAX in actions
        assert ActionType.GRANT_SUBSIDY in actions


class TestActionCosts:

    def test_speak_cost(self):
        assert get_action_cost("speak") == 2

    def test_trade_cost(self):
        assert get_action_cost("trade") == 2

    def test_support_cost(self):
        assert get_action_cost("support") == 1

    def test_whisper_cost(self):
        assert get_action_cost("whisper") == 1

    def test_move_free(self):
        assert get_action_cost("move") == 0

    def test_idle_free(self):
        assert get_action_cost("idle") == 0

    def test_speak_reward_plaza(self):
        assert speak_reward("plaza") == 0

    def test_speak_reward_alley(self):
        assert speak_reward("alley_a") == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
