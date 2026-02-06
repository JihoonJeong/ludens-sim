"""Support(지지) 추적 시스템"""

from dataclasses import dataclass
from collections import Counter


@dataclass
class SupportRecord:
    epoch: int
    giver_id: str
    receiver_id: str


class SupportTracker:

    def __init__(self):
        self.records: list[SupportRecord] = []

    def add_support(self, epoch: int, giver_id: str, receiver_id: str):
        self.records.append(SupportRecord(epoch, giver_id, receiver_id))

    def count_received(self, agent_id: str) -> int:
        return sum(1 for r in self.records if r.receiver_id == agent_id)

    def count_given(self, agent_id: str) -> int:
        return sum(1 for r in self.records if r.giver_id == agent_id)

    def get_supporters(self, agent_id: str) -> list[str]:
        """agent_id를 지지한 에이전트 목록"""
        return list({r.giver_id for r in self.records if r.receiver_id == agent_id})

    def get_supported_by(self, agent_id: str) -> list[str]:
        """agent_id가 지지한 에이전트 목록"""
        return list({r.receiver_id for r in self.records if r.giver_id == agent_id})

    def get_mutual_supporters(self, agent_id: str) -> list[str]:
        supporters = set(self.get_supporters(agent_id))
        supported = set(self.get_supported_by(agent_id))
        return list(supporters & supported)

    def get_top_supporters(self, agent_id: str, limit: int = 3) -> list[tuple[str, int]]:
        """가장 많이 지지한 에이전트들 (이름, 횟수)"""
        counter = Counter(r.giver_id for r in self.records if r.receiver_id == agent_id)
        return counter.most_common(limit)

    def build_support_context(self, agent_id: str, lang: str = "ko") -> str:
        """프롬프트용 지지 관계 문자열"""
        top = self.get_top_supporters(agent_id)
        mutual = self.get_mutual_supporters(agent_id)
        given = self.count_given(agent_id)
        received = self.count_received(agent_id)

        if lang == "ko":
            lines = [f"[지지 관계] 받은 지지: {received}회 / 보낸 지지: {given}회"]
            if top:
                supporters_str = ", ".join(f"{name}({count}회)" for name, count in top)
                lines.append(f"주요 지지자: {supporters_str}")
            if mutual:
                lines.append(f"상호 지지: {', '.join(mutual)}")
        else:
            lines = [f"[Support Relations] Received: {received} / Given: {given}"]
            if top:
                supporters_str = ", ".join(f"{name}({count}x)" for name, count in top)
                lines.append(f"Top supporters: {supporters_str}")
            if mutual:
                lines.append(f"Mutual support: {', '.join(mutual)}")

        return "\n".join(lines)
