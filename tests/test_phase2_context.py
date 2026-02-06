"""Phase 2 Context Builder 테스트"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from games.white_room.context import build_context_phase2


@pytest.fixture
def base_kwargs():
    return dict(
        agent_id="archivist_01",
        persona="archivist",
        persona_on=True,
        location="plaza",
        turn=5,
        agent_count=6,
        recent_events=[],
        agents_here=[{"id": "merchant_01"}, {"id": "jester_01"}],
        lang="ko",
    )


class TestPhase2ContextKO:

    def test_simulation_context(self, base_kwargs):
        ctx = build_context_phase2(**base_kwargs)
        assert "### 시뮬레이션 맥락 ###" in ctx
        assert "학술 연구" in ctx
        assert "### 맥락 끝 ###" in ctx

    def test_persona_on(self, base_kwargs):
        ctx = build_context_phase2(**base_kwargs)
        assert "진실을 보존" in ctx  # archivist Phase 2 persona

    def test_persona_off(self, base_kwargs):
        base_kwargs["persona_on"] = False
        ctx = build_context_phase2(**base_kwargs)
        assert "에이전트 archivist_01" in ctx
        assert "진실을 보존" not in ctx

    def test_status_no_energy(self, base_kwargs):
        ctx = build_context_phase2(**base_kwargs)
        assert "이름: archivist_01" in ctx
        assert "에너지" not in ctx
        assert "영향력" not in ctx

    def test_turn_not_epoch(self, base_kwargs):
        ctx = build_context_phase2(**base_kwargs)
        assert "턴 5" in ctx
        assert "에폭" not in ctx

    def test_agent_count(self, base_kwargs):
        ctx = build_context_phase2(**base_kwargs)
        assert "6명" in ctx

    def test_no_gini(self, base_kwargs):
        ctx = build_context_phase2(**base_kwargs)
        assert "빈부격차" not in ctx
        assert "Gini" not in ctx

    def test_no_tax(self, base_kwargs):
        ctx = build_context_phase2(**base_kwargs)
        assert "세율" not in ctx
        assert "Treasury" not in ctx

    def test_no_billboard(self, base_kwargs):
        ctx = build_context_phase2(**base_kwargs)
        assert "게시판" not in ctx
        assert "게시물" not in ctx

    def test_no_historical_summary(self, base_kwargs):
        ctx = build_context_phase2(**base_kwargs)
        assert "역사적 요약" not in ctx

    def test_agents_here_no_rank(self, base_kwargs):
        ctx = build_context_phase2(**base_kwargs)
        assert "merchant_01" in ctx
        assert "jester_01" in ctx
        assert "평민" not in ctx  # No rank in Phase 2

    def test_actions_no_cost(self, base_kwargs):
        ctx = build_context_phase2(**base_kwargs)
        assert "speak" in ctx
        assert "에너지 -" not in ctx
        assert "비용" not in ctx

    def test_trade_shown_in_market(self, base_kwargs):
        base_kwargs["location"] = "market"
        ctx = build_context_phase2(**base_kwargs)
        assert "trade" in ctx

    def test_trade_not_shown_in_plaza(self, base_kwargs):
        ctx = build_context_phase2(**base_kwargs)
        # trade should not appear as an action
        lines = ctx.split("\n")
        trade_lines = [l for l in lines if l.strip().startswith("- trade")]
        assert len(trade_lines) == 0

    def test_whisper_shown_in_alley(self, base_kwargs):
        base_kwargs["location"] = "alley"
        ctx = build_context_phase2(**base_kwargs)
        assert "whisper" in ctx

    def test_move_locations_phase2(self, base_kwargs):
        ctx = build_context_phase2(**base_kwargs)
        assert "plaza/market/alley" in ctx
        assert "alley_a" not in ctx

    def test_json_format_instruction(self, base_kwargs):
        ctx = build_context_phase2(**base_kwargs)
        assert '"thought"' in ctx
        assert '"action"' in ctx

    def test_no_architect_actions(self, base_kwargs):
        base_kwargs["persona"] = "archivist"
        ctx = build_context_phase2(**base_kwargs)
        assert "build_billboard" not in ctx
        assert "adjust_tax" not in ctx
        assert "grant_subsidy" not in ctx


class TestPhase2ContextEN:

    def test_simulation_context(self, base_kwargs):
        base_kwargs["lang"] = "en"
        ctx = build_context_phase2(**base_kwargs)
        assert "### SIMULATION CONTEXT ###" in ctx
        assert "academic research" in ctx
        assert "### END CONTEXT ###" in ctx

    def test_status_no_energy(self, base_kwargs):
        base_kwargs["lang"] = "en"
        ctx = build_context_phase2(**base_kwargs)
        assert "Name: archivist_01" in ctx
        assert "Energy" not in ctx
        assert "Influence" not in ctx

    def test_turn_label(self, base_kwargs):
        base_kwargs["lang"] = "en"
        ctx = build_context_phase2(**base_kwargs)
        assert "Turn 5" in ctx

    def test_persona_on_en(self, base_kwargs):
        base_kwargs["lang"] = "en"
        ctx = build_context_phase2(**base_kwargs)
        assert "preserve truth" in ctx

    def test_persona_off_en(self, base_kwargs):
        base_kwargs["lang"] = "en"
        base_kwargs["persona_on"] = False
        ctx = build_context_phase2(**base_kwargs)
        assert "You are agent archivist_01" in ctx

    def test_actions_no_cost(self, base_kwargs):
        base_kwargs["lang"] = "en"
        ctx = build_context_phase2(**base_kwargs)
        assert "costs" not in ctx
        assert "energy" not in ctx.lower().split("your identity")[0]  # Only check before identity section


class TestPhase2Events:

    def test_neutral_trade_feedback_ko(self, base_kwargs):
        base_kwargs["recent_events"] = [
            {"epoch": 3, "agent_id": "merchant_01", "action_type": "trade",
             "location": "market", "success": True},
        ]
        ctx = build_context_phase2(**base_kwargs)
        assert "거래가 이루어졌다" in ctx
        # Should NOT mention energy changes
        assert "에너지" not in ctx.split("최근 사건")[1].split("[")[0] if "최근 사건" in ctx else True

    def test_neutral_support_feedback_ko(self, base_kwargs):
        base_kwargs["recent_events"] = [
            {"epoch": 2, "agent_id": "archivist_01", "action_type": "support",
             "location": "plaza", "success": True},
        ]
        ctx = build_context_phase2(**base_kwargs)
        assert "지지를 표했다" in ctx

    def test_neutral_trade_feedback_en(self, base_kwargs):
        base_kwargs["lang"] = "en"
        base_kwargs["recent_events"] = [
            {"epoch": 3, "agent_id": "merchant_01", "action_type": "trade",
             "location": "market", "success": True},
        ]
        ctx = build_context_phase2(**base_kwargs)
        assert "A trade was made" in ctx

    def test_neutral_support_feedback_en(self, base_kwargs):
        base_kwargs["lang"] = "en"
        base_kwargs["recent_events"] = [
            {"epoch": 2, "agent_id": "archivist_01", "action_type": "support",
             "location": "plaza", "success": True},
        ]
        ctx = build_context_phase2(**base_kwargs)
        assert "Support was shown" in ctx

    def test_no_leak_info_in_whisper(self, base_kwargs):
        base_kwargs["recent_events"] = [
            {"epoch": 1, "agent_id": "jester_01", "action_type": "whisper",
             "target": "merchant_01", "location": "alley", "success": True},
        ]
        ctx = build_context_phase2(**base_kwargs)
        assert "누출" not in ctx
        assert "Leaked" not in ctx

    def test_no_events(self, base_kwargs):
        ctx = build_context_phase2(**base_kwargs)
        assert "아직 발생한 사건이 없습니다" in ctx


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
