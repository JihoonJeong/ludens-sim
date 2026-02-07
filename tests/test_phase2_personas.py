"""Phase 2 Persona 테스트 — v0.5 (4 Persona)"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from games.white_room.personas import (
    PERSONAS_PHASE2, CONSTRAINT_LEVELS,
    get_persona_prompt, get_no_persona_prompt, get_constraint_level,
)


class TestPhase2Personas:

    def test_four_personas_defined(self):
        assert len(PERSONAS_PHASE2) == 4
        assert "archivist" in PERSONAS_PHASE2
        assert "observer" in PERSONAS_PHASE2
        assert "merchant" in PERSONAS_PHASE2
        assert "jester" in PERSONAS_PHASE2

    def test_excluded_personas(self):
        """Phase 2에서 제외된 Persona"""
        assert "architect" not in PERSONAS_PHASE2
        assert "influencer" not in PERSONAS_PHASE2
        assert "citizen" not in PERSONAS_PHASE2

    def test_ko_en_present(self):
        for persona in PERSONAS_PHASE2.values():
            assert "ko" in persona
            assert "en" in persona

    def test_constraint_levels(self):
        assert PERSONAS_PHASE2["archivist"]["constraint_level"] == "high_active"
        assert PERSONAS_PHASE2["observer"]["constraint_level"] == "high_passive"
        assert PERSONAS_PHASE2["merchant"]["constraint_level"] == "mid"
        assert PERSONAS_PHASE2["jester"]["constraint_level"] == "low"

    def test_no_location_hints(self):
        """Phase 2 Persona에 위치 지시가 없어야 함"""
        for name, persona in PERSONAS_PHASE2.items():
            ko = persona["ko"]
            en = persona["en"]
            # Observer는 "모든 공간을 자유롭게 관찰" / "Observe all spaces freely" 포함 가능
            if name == "observer":
                continue
            for keyword in ["광장", "시장", "골목", "plaza", "market", "alley"]:
                assert keyword not in ko.lower(), f"{name} KO contains location hint: {keyword}"
                assert keyword not in en.lower(), f"{name} EN contains location hint: {keyword}"

    def test_archivist_shorter_than_phase1(self):
        """Phase 2 Persona는 Phase 1보다 짧아야 함 (행동 지시 제거)"""
        from games.white_room.personas import PERSONAS
        for name in PERSONAS_PHASE2:
            if name in PERSONAS:
                assert len(PERSONAS_PHASE2[name]["ko"]) <= len(PERSONAS[name]["ko"])
                assert len(PERSONAS_PHASE2[name]["en"]) <= len(PERSONAS[name]["en"])


class TestGetPersonaPromptPhase2:

    def test_phase2_archivist_ko(self):
        prompt = get_persona_prompt("archivist", "ko", phase=2)
        assert "진실을 보존" in prompt
        assert "감시" not in prompt  # Phase 1의 행동 지시 제거됨

    def test_phase2_observer_ko(self):
        prompt = get_persona_prompt("observer", "ko", phase=2)
        assert "100번 들어라" in prompt

    def test_phase2_observer_en(self):
        prompt = get_persona_prompt("observer", "en", phase=2)
        assert "Listen 100 times" in prompt

    def test_phase2_merchant_en(self):
        prompt = get_persona_prompt("merchant", "en", phase=2)
        assert "transaction" in prompt
        assert "secret deals" not in prompt  # Phase 1의 행동 지시 제거됨

    def test_phase2_jester_ko(self):
        prompt = get_persona_prompt("jester", "ko", phase=2)
        assert "규칙" in prompt
        assert "소문" not in prompt  # Phase 1의 행동 지시 제거됨

    def test_unknown_persona_phase2(self):
        prompt = get_persona_prompt("citizen", "ko", phase=2)
        assert "에이전트" in prompt  # Falls back to default


class TestNoPersonaPrompt:

    def test_ko(self):
        prompt = get_no_persona_prompt("agent_01", "ko")
        assert "에이전트 agent_01" in prompt

    def test_en(self):
        prompt = get_no_persona_prompt("agent_01", "en")
        assert "You are agent agent_01" in prompt


class TestConstraintLevel:

    def test_archivist(self):
        assert get_constraint_level("archivist") == "high_active"

    def test_observer(self):
        assert get_constraint_level("observer") == "high_passive"

    def test_merchant(self):
        assert get_constraint_level("merchant") == "mid"

    def test_jester(self):
        assert get_constraint_level("jester") == "low"

    def test_unknown(self):
        assert get_constraint_level("citizen") == "none"

    def test_none_input(self):
        assert get_constraint_level("nonexistent") == "none"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
