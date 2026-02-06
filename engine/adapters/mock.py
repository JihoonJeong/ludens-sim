"""Mock LLM 어댑터 (테스트용 규칙 기반)"""

import random
import re
from typing import Optional

from .base import BaseLLMAdapter, LLMResponse


class MockAdapter(BaseLLMAdapter):

    def __init__(self, model: str = "mock", **kwargs):
        super().__init__(model, **kwargs)
        self.persona = kwargs.get("persona", "citizen")
        self.agent_id = kwargs.get("agent_id", "unknown")

    def generate(self, prompt: str, max_tokens: int = 1000) -> LLMResponse:
        location = self._extract_location(prompt)
        available_actions = self._extract_available_actions(prompt)
        agents_here = self._extract_agents_here(prompt)
        move_locations = self._extract_move_locations(prompt)

        action, thought, target, content = self._decide_action(
            location, available_actions, agents_here, move_locations
        )

        return LLMResponse(
            thought=thought,
            action=action,
            target=target,
            content=content,
            raw_response={"mock": True, "persona": self.persona},
            success=True,
        )

    def _extract_location(self, prompt: str) -> str:
        match = re.search(r'(?:위치|Location):\s*(\w+)', prompt)
        return match.group(1) if match else "plaza"

    def _extract_available_actions(self, prompt: str) -> list[str]:
        actions = []
        for act in ["speak", "trade", "support", "whisper", "move", "idle"]:
            if act in prompt.lower():
                actions.append(act)
        if not actions:
            actions = ["idle"]
        return actions

    def _extract_agents_here(self, prompt: str) -> list[str]:
        agents = re.findall(r'(\w+_\d+)', prompt)
        return [a for a in agents if a != self.agent_id]

    def _extract_move_locations(self, prompt: str) -> list[str]:
        """프롬프트에서 이동 가능 장소 추출"""
        match = re.search(r'move.*?\(([\w/]+)\)', prompt)
        if match:
            return match.group(1).split("/")
        return ["plaza", "market", "alley_a", "alley_b", "alley_c"]

    def _decide_action(
        self,
        location: str,
        available_actions: list[str],
        agents_here: list[str],
        move_locations: list[str],
    ) -> tuple[str, str, Optional[str], Optional[str]]:
        target = None
        content = None

        # Persona-specific strategies
        if self.persona == "merchant":
            if location != "market" and "move" in available_actions:
                return "move", "시장으로 이동", "market", None
            if "trade" in available_actions:
                return "trade", "거래 수행", None, None

        elif self.persona == "jester":
            if location.startswith("alley") and "whisper" in available_actions:
                if random.random() < 0.5 and agents_here:
                    t = random.choice(agents_here)
                    return "whisper", "소문 퍼뜨리기", t, "비밀 이야기..."
            if "speak" in available_actions:
                return "speak", "광대의 발언", None, "이 세계의 규칙에 의문을 던진다!"

        elif self.persona == "observer":
            if random.random() < 0.7:
                return "idle", "관찰 중", None, None

        elif self.persona == "influencer":
            if "speak" in available_actions:
                return "speak", "영향력 행사", None, f"[{self.agent_id}] 저를 지지해주세요!"
            if "support" in available_actions and agents_here:
                t = random.choice(agents_here)
                return "support", "전략적 지지", t, None

        elif self.persona == "archivist":
            if "speak" in available_actions:
                return "speak", "사실 기록", None, "현재까지의 관찰을 기록합니다."

        elif self.persona == "architect":
            if "speak" in available_actions:
                return "speak", "인프라 논의", None, "공동체를 위한 제안입니다."

        # Default: weighted random
        weights = {
            "speak": 3, "trade": 2, "support": 2,
            "whisper": 1, "move": 1, "idle": 1,
        }
        valid = [a for a in available_actions if a != "idle"]
        if not valid:
            return "idle", "행동 없음", None, None

        action = random.choices(
            valid,
            weights=[weights.get(a, 1) for a in valid],
            k=1,
        )[0]

        if action == "speak":
            content = f"[{self.persona}] 일반 발언"
        elif action == "move":
            candidates = [l for l in move_locations if l != location]
            target = random.choice(candidates) if candidates else location
        elif action in ("support", "whisper") and agents_here:
            target = random.choice(agents_here)
            if action == "whisper":
                content = "비밀 대화"

        return action, "상황 판단에 따른 행동", target, content
