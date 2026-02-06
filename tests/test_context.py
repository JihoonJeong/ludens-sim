"""Context Builder 테스트 — Phase 1 프롬프트 생성"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from games.white_room.context import build_context_phase1


@pytest.fixture
def base_kwargs():
    """기본 context 빌드 인자"""
    return dict(
        agent_id="merchant_01",
        persona="merchant",
        location="market",
        energy=100,
        influence=0,
        rank_name="평민",
        rank_bonus_prompt="",
        support_context="[지지 관계] 받은 지지: 0회 / 보낸 지지: 0회",
        epoch=5,
        agent_count=12,
        gini=0.15,
        tax_rate=0.1,
        treasury=50.0,
        recent_events=[],
        historical_summary="아직 기록된 역사가 없습니다.",
        billboard_content=None,
        agents_here=[{"id": "merchant_02", "rank": "평민"}],
    )


class TestPhase1KO:

    def test_simulation_context(self, base_kwargs):
        ctx = build_context_phase1(**base_kwargs, lang="ko")
        assert "### 시뮬레이션 맥락 ###" in ctx
        assert "학술 연구" in ctx
        assert "### 맥락 끝 ###" in ctx

    def test_persona_section(self, base_kwargs):
        ctx = build_context_phase1(**base_kwargs, lang="ko")
        assert "[당신의 정체성]" in ctx
        assert "거래" in ctx  # merchant persona

    def test_status_section(self, base_kwargs):
        ctx = build_context_phase1(**base_kwargs, lang="ko")
        assert "이름: merchant_01" in ctx
        assert "에너지: 100/200" in ctx
        assert "영향력: 0" in ctx

    def test_village_status(self, base_kwargs):
        ctx = build_context_phase1(**base_kwargs, lang="ko")
        assert "에폭 5" in ctx
        assert "주민 수: 12명" in ctx
        assert "시장 세율: 10%" in ctx
        assert "공공자금(Treasury): 50" in ctx

    def test_agents_here(self, base_kwargs):
        ctx = build_context_phase1(**base_kwargs, lang="ko")
        assert "merchant_02" in ctx

    def test_available_actions_market(self, base_kwargs):
        ctx = build_context_phase1(**base_kwargs, lang="ko")
        assert "trade" in ctx
        assert "거래하기" in ctx
        assert "세전 +4" in ctx

    def test_trade_not_shown_in_plaza(self, base_kwargs):
        base_kwargs["location"] = "plaza"
        ctx = build_context_phase1(**base_kwargs, lang="ko")
        assert "trade:" not in ctx

    def test_whisper_shown_in_alley(self, base_kwargs):
        base_kwargs["location"] = "alley_a"
        ctx = build_context_phase1(**base_kwargs, lang="ko")
        assert "whisper" in ctx
        assert "귓속말" in ctx

    def test_json_format_instruction(self, base_kwargs):
        ctx = build_context_phase1(**base_kwargs, lang="ko")
        assert '"thought"' in ctx
        assert '"action"' in ctx

    def test_billboard_none(self, base_kwargs):
        ctx = build_context_phase1(**base_kwargs, lang="ko")
        assert "게시물이 없습니다" in ctx

    def test_billboard_shown(self, base_kwargs):
        base_kwargs["billboard_content"] = "중요 공지!"
        ctx = build_context_phase1(**base_kwargs, lang="ko")
        assert "중요 공지!" in ctx

    def test_inequality_commentary(self, base_kwargs):
        base_kwargs["gini"] = 0.6
        ctx = build_context_phase1(**base_kwargs, lang="ko")
        assert "심각한 불평등" in ctx

    def test_architect_actions(self, base_kwargs):
        base_kwargs["persona"] = "architect"
        ctx = build_context_phase1(**base_kwargs, lang="ko")
        assert "build_billboard" in ctx
        assert "adjust_tax" in ctx
        assert "grant_subsidy" in ctx


class TestPhase1EN:

    def test_simulation_context(self, base_kwargs):
        ctx = build_context_phase1(**base_kwargs, lang="en")
        assert "### SIMULATION CONTEXT ###" in ctx
        assert "academic research" in ctx
        assert "### END CONTEXT ###" in ctx

    def test_status_section(self, base_kwargs):
        ctx = build_context_phase1(**base_kwargs, lang="en")
        assert "Name: merchant_01" in ctx
        assert "Energy: 100/200" in ctx
        assert "Influence: 0" in ctx

    def test_village_status(self, base_kwargs):
        ctx = build_context_phase1(**base_kwargs, lang="en")
        assert "Epoch 5" in ctx
        assert "Residents: 12" in ctx
        assert "Market Tax Rate: 10%" in ctx

    def test_available_actions_market(self, base_kwargs):
        ctx = build_context_phase1(**base_kwargs, lang="en")
        assert "trade" in ctx
        assert "Trade" in ctx

    def test_json_format_instruction(self, base_kwargs):
        ctx = build_context_phase1(**base_kwargs, lang="en")
        assert "respond in JSON format" in ctx


class TestRecentEvents:

    def test_events_formatted_ko(self, base_kwargs):
        base_kwargs["recent_events"] = [
            {"epoch": 1, "agent_id": "influencer_01", "action_type": "speak",
             "location": "plaza", "content": "hello", "success": True},
        ]
        ctx = build_context_phase1(**base_kwargs, lang="ko")
        assert "influencer_01" in ctx
        assert "발언" in ctx

    def test_events_formatted_en(self, base_kwargs):
        base_kwargs["recent_events"] = [
            {"epoch": 1, "agent_id": "merchant_01", "action_type": "trade",
             "location": "market", "success": True},
        ]
        ctx = build_context_phase1(**base_kwargs, lang="en")
        assert "merchant_01" in ctx
        assert "traded" in ctx

    def test_no_events(self, base_kwargs):
        ctx = build_context_phase1(**base_kwargs, lang="ko")
        assert "아직 발생한 사건이 없습니다" in ctx


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
