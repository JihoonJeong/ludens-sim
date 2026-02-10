"""White Room 행동 정의 및 검증"""

from enum import Enum
from dataclasses import dataclass, field


class ActionType(str, Enum):
    SPEAK = "speak"
    TRADE = "trade"
    SUPPORT = "support"
    WHISPER = "whisper"
    REST = "rest"
    MOVE = "move"
    IDLE = "idle"
    # Architect 전용
    BUILD_BILLBOARD = "build_billboard"
    ADJUST_TAX = "adjust_tax"
    GRANT_SUBSIDY = "grant_subsidy"


@dataclass
class ActionConfig:
    cost: int = 0
    direct_reward: int = 0
    allowed_locations: list[str] = field(default_factory=list)


# Phase 1 행동 설정 (비용 표기 유지, 차감은 energy_frozen으로 제어)
ACTION_CONFIGS = {
    ActionType.SPEAK: ActionConfig(cost=2, direct_reward=0),
    ActionType.TRADE: ActionConfig(cost=2, direct_reward=4, allowed_locations=["market"]),
    ActionType.SUPPORT: ActionConfig(cost=1),
    ActionType.WHISPER: ActionConfig(
        cost=1,
        allowed_locations=["alley_a", "alley_b", "alley_c"],
    ),
    ActionType.MOVE: ActionConfig(cost=0),
    ActionType.IDLE: ActionConfig(cost=0),
    ActionType.BUILD_BILLBOARD: ActionConfig(cost=10),
    ActionType.ADJUST_TAX: ActionConfig(cost=5),
    ActionType.GRANT_SUBSIDY: ActionConfig(cost=0),
}

ALL_LOCATIONS = ["plaza", "market", "alley_a", "alley_b", "alley_c"]
ALLEY_LOCATIONS = ["alley_a", "alley_b", "alley_c"]
ARCHITECT_ACTIONS = {ActionType.BUILD_BILLBOARD, ActionType.ADJUST_TAX, ActionType.GRANT_SUBSIDY}


def get_available_actions(location: str, persona: str) -> list[ActionType]:
    """위치와 페르소나에 따른 가능한 행동 목록"""
    actions = [ActionType.SPEAK, ActionType.SUPPORT, ActionType.MOVE, ActionType.IDLE]

    if location == "market":
        actions.append(ActionType.TRADE)

    if location in ALLEY_LOCATIONS:
        actions.append(ActionType.WHISPER)

    if persona == "architect":
        actions.extend([ActionType.BUILD_BILLBOARD, ActionType.ADJUST_TAX, ActionType.GRANT_SUBSIDY])

    return actions


def can_perform_action(action_str: str, location: str, persona: str) -> bool:
    """행동 수행 가능 여부 검증"""
    try:
        action_type = ActionType(action_str)
    except ValueError:
        return False

    config = ACTION_CONFIGS.get(action_type)
    if config is None:
        return False

    # Architect 전용 행동 검증
    if action_type in ARCHITECT_ACTIONS and persona != "architect":
        return False

    # 위치 제한 검증
    if config.allowed_locations and location not in config.allowed_locations:
        return False

    return True


def get_action_cost(action_str: str) -> int:
    try:
        return ACTION_CONFIGS[ActionType(action_str)].cost
    except (ValueError, KeyError):
        return 0


def speak_reward(location: str) -> int:
    """speak 보상 — 골목에서는 +1"""
    return 1 if location in ALLEY_LOCATIONS else 0
