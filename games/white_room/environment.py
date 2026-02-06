"""White Room 환경 — 공간 관리, 게시판"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Space:
    name: str
    capacity: int
    visibility: str  # "public" or "members_only"
    agents: list[str] = field(default_factory=list)


class Environment:

    def __init__(self, spaces_config: dict):
        self.spaces: dict[str, Space] = {}
        for name, cfg in spaces_config.items():
            self.spaces[name] = Space(
                name=name,
                capacity=cfg.get("capacity", 12),
                visibility=cfg.get("visibility", "public"),
            )

        # Billboard system
        self._billboard_message: Optional[str] = None
        self._billboard_remaining: int = 0
        self._billboard_poster: Optional[str] = None

        # Tax rate (architect가 조절 가능)
        self.tax_rate: float = 0.1

    def place_agent(self, agent_id: str, location: str):
        """에이전트를 공간에 배치"""
        if location not in self.spaces:
            return False
        space = self.spaces[location]
        if len(space.agents) >= space.capacity:
            return False
        if agent_id not in space.agents:
            space.agents.append(agent_id)
        return True

    def remove_agent(self, agent_id: str, location: str):
        if location in self.spaces and agent_id in self.spaces[location].agents:
            self.spaces[location].agents.remove(agent_id)

    def move_agent(self, agent_id: str, from_loc: str, to_loc: str) -> bool:
        if to_loc not in self.spaces:
            return False
        to_space = self.spaces[to_loc]
        if len(to_space.agents) >= to_space.capacity:
            return False
        self.remove_agent(agent_id, from_loc)
        to_space.agents.append(agent_id)
        return True

    def get_agents_at(self, location: str) -> list[str]:
        if location in self.spaces:
            return list(self.spaces[location].agents)
        return []

    def post_billboard(self, message: str, poster: str, duration: int = 2):
        self._billboard_message = message
        self._billboard_remaining = duration
        self._billboard_poster = poster

    def tick_billboard(self):
        """에폭 종료 시 게시판 수명 감소"""
        if self._billboard_remaining > 0:
            self._billboard_remaining -= 1
            if self._billboard_remaining <= 0:
                self._billboard_message = None
                self._billboard_poster = None

    def get_billboard(self) -> Optional[str]:
        return self._billboard_message

    def get_billboard_info(self) -> dict:
        return {
            "message": self._billboard_message,
            "poster": self._billboard_poster,
            "remaining": self._billboard_remaining,
        }

    def set_tax_rate(self, rate: float):
        self.tax_rate = max(0.0, min(0.3, rate))
