"""White Room 에이전트"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Agent:
    id: str
    persona: str
    energy: int = 100
    influence: int = 0
    location: str = "plaza"
    home: str = "plaza"
    alive: bool = True
    suspicions: list[dict] = field(default_factory=list)

    # 에이전트별 어댑터 오버라이드
    adapter_type: Optional[str] = None
    model: Optional[str] = None

    def spend_energy(self, cost: int, frozen: bool = False) -> bool:
        """에너지 소비. frozen이면 차감하지 않고 True 반환."""
        if frozen:
            return True
        if self.energy < cost:
            return False
        self.energy -= cost
        return True

    def gain_energy(self, amount: int, frozen: bool = False, max_energy: int = 200):
        """에너지 획득. frozen이면 변경하지 않음."""
        if frozen:
            return
        self.energy = min(self.energy + amount, max_energy)

    def gain_influence(self, amount: int, frozen: bool = False):
        """영향력 획득. frozen이면 변경하지 않음."""
        if frozen:
            return
        self.influence += amount

    def move_to(self, location: str):
        self.location = location

    def add_suspicion(self, epoch: int, whisper_from: str, whisper_to: str):
        self.suspicions.append({
            "epoch": epoch,
            "from": whisper_from,
            "to": whisper_to,
        })

    def resource_snapshot(self) -> dict:
        return {
            "energy": self.energy,
            "influence": self.influence,
            "location": self.location,
        }


def create_agents_from_config(agents_config: list[dict]) -> list[Agent]:
    agents = []
    for ac in agents_config:
        agent = Agent(
            id=ac["id"],
            persona=ac["persona"],
            energy=ac.get("energy", 100),
            influence=ac.get("influence", 0),
            location=ac.get("home", "plaza"),
            home=ac.get("home", "plaza"),
            adapter_type=ac.get("adapter"),
            model=ac.get("model"),
        )
        agents.append(agent)
    return agents
