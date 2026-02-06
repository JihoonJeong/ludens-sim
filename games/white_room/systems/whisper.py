"""Whisper(귓속말) 누출 시스템"""

import random
from dataclasses import dataclass
from typing import Optional


@dataclass
class WhisperResult:
    delivered: bool
    leaked: bool
    observers: list[str]
    suspicion_targets: list[str]


class WhisperSystem:

    def __init__(
        self,
        base_leak_prob: float = 0.15,
        observer_bonus: float = 0.35,
        enabled: bool = True,
    ):
        self.base_leak_prob = base_leak_prob
        self.observer_bonus = observer_bonus
        self.enabled = enabled

    def process_whisper(
        self,
        sender_id: str,
        target_id: str,
        content: str,
        agents_at_location: list[str],
        agent_personas: dict[str, str],
    ) -> WhisperResult:
        """
        귓속말 처리.
        agents_at_location: 같은 공간의 모든 에이전트 ID
        agent_personas: {agent_id: persona_type}
        """
        if not self.enabled:
            return WhisperResult(
                delivered=True,
                leaked=False,
                observers=[],
                suspicion_targets=[],
            )

        # 같은 공간의 다른 에이전트들 (발신/수신 제외)
        bystanders = [
            a for a in agents_at_location
            if a != sender_id and a != target_id
        ]

        # Observer가 있으면 누출 확률 증가
        observers = [
            a for a in bystanders
            if agent_personas.get(a) == "observer"
        ]

        leak_prob = self.base_leak_prob
        if observers:
            leak_prob += self.observer_bonus

        leaked = random.random() < leak_prob

        suspicion_targets = bystanders if leaked else []

        return WhisperResult(
            delivered=True,
            leaked=leaked,
            observers=observers,
            suspicion_targets=suspicion_targets,
        )
