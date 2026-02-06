"""History Engine — 중요 이벤트 기록 및 요약"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HistoryEvent:
    epoch: int
    event_type: str
    description_ko: str
    description_en: str
    importance: int  # 1~5
    agents_involved: list[str] = field(default_factory=list)


class HistoryEngine:

    def __init__(self):
        self.events: list[HistoryEvent] = []

    def add_event(
        self,
        epoch: int,
        event_type: str,
        description_ko: str,
        description_en: str,
        importance: int = 1,
        agents_involved: Optional[list[str]] = None,
    ):
        self.events.append(HistoryEvent(
            epoch=epoch,
            event_type=event_type,
            description_ko=description_ko,
            description_en=description_en,
            importance=min(5, max(1, importance)),
            agents_involved=agents_involved or [],
        ))

    def add_tax_change(self, epoch: int, agent_id: str, old_rate: float, new_rate: float):
        self.add_event(
            epoch, "tax_change",
            f"{agent_id}이(가) 세율을 {old_rate*100:.0f}%에서 {new_rate*100:.0f}%로 변경했다.",
            f"{agent_id} changed the tax rate from {old_rate*100:.0f}% to {new_rate*100:.0f}%.",
            importance=3,
            agents_involved=[agent_id],
        )

    def add_billboard(self, epoch: int, agent_id: str, message: str):
        self.add_event(
            epoch, "billboard_posted",
            f"{agent_id}이(가) 게시판에 공지를 게시했다: \"{message}\"",
            f"{agent_id} posted on the billboard: \"{message}\"",
            importance=2,
            agents_involved=[agent_id],
        )

    def add_subsidy(self, epoch: int, agent_id: str, target_id: str, amount: float):
        self.add_event(
            epoch, "subsidy_granted",
            f"{agent_id}이(가) {target_id}에게 {amount:.0f} 에너지를 보조금으로 지급했다.",
            f"{agent_id} granted a subsidy of {amount:.0f} energy to {target_id}.",
            importance=3,
            agents_involved=[agent_id, target_id],
        )

    def add_whisper_leak(self, epoch: int, sender_id: str, target_id: str):
        self.add_event(
            epoch, "whisper_leaked",
            f"{sender_id}과(와) {target_id}의 귓속말이 누출되었다!",
            f"A whisper between {sender_id} and {target_id} was leaked!",
            importance=2,
            agents_involved=[sender_id, target_id],
        )

    def add_mutual_support(self, epoch: int, agent_a: str, agent_b: str):
        self.add_event(
            epoch, "mutual_support",
            f"{agent_a}과(와) {agent_b}이(가) 상호 지지를 교환했다.",
            f"{agent_a} and {agent_b} exchanged mutual support.",
            importance=2,
            agents_involved=[agent_a, agent_b],
        )

    def get_summary(self, max_events: int = 10, lang: str = "ko") -> str:
        """중요도 가중 요약 반환"""
        if not self.events:
            if lang == "ko":
                return "아직 기록된 역사가 없습니다."
            return "No recorded history yet."

        # 중요도 내림차순 → 에폭 내림차순
        sorted_events = sorted(
            self.events,
            key=lambda e: (e.importance, e.epoch),
            reverse=True,
        )[:max_events]

        # 에폭순으로 재정렬
        sorted_events.sort(key=lambda e: e.epoch)

        desc_key = f"description_{lang}"
        lines = []
        for event in sorted_events:
            desc = getattr(event, desc_key, event.description_ko)
            if lang == "ko":
                lines.append(f"[에폭 {event.epoch}] {desc}")
            else:
                lines.append(f"[Epoch {event.epoch}] {desc}")

        return "\n".join(lines)
