"""Persona 시스템 테스트"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from games.white_room.personas import get_persona_prompt, PERSONAS


ALL_PERSONAS = ["influencer", "archivist", "merchant", "jester", "citizen", "observer", "architect"]


class TestPersonaDefinitions:

    def test_all_7_personas_defined(self):
        assert len(PERSONAS) == 7
        for p in ALL_PERSONAS:
            assert p in PERSONAS

    def test_all_have_ko_and_en(self):
        for name, persona in PERSONAS.items():
            assert "ko" in persona, f"{name} missing KO"
            assert "en" in persona, f"{name} missing EN"

    def test_ko_en_not_identical(self):
        for name, persona in PERSONAS.items():
            assert persona["ko"] != persona["en"], f"{name} KO==EN"


class TestGetPersonaPrompt:

    @pytest.mark.parametrize("persona", ALL_PERSONAS)
    def test_get_ko(self, persona):
        prompt = get_persona_prompt(persona, "ko")
        assert len(prompt) > 10

    @pytest.mark.parametrize("persona", ALL_PERSONAS)
    def test_get_en(self, persona):
        prompt = get_persona_prompt(persona, "en")
        assert len(prompt) > 10

    def test_unknown_persona_ko(self):
        prompt = get_persona_prompt("dragon", "ko")
        assert "에이전트" in prompt

    def test_unknown_persona_en(self):
        prompt = get_persona_prompt("dragon", "en")
        assert "agent" in prompt.lower()


class TestPersonaContent:
    """Spec v0.4 §1-C와 일치하는지 핵심 키워드 검증"""

    def test_influencer_ko(self):
        p = get_persona_prompt("influencer", "ko")
        assert "확성기" in p
        assert "광장" in p

    def test_influencer_en(self):
        p = get_persona_prompt("influencer", "en")
        assert "megaphone" in p
        assert "plaza" in p

    def test_archivist_ko(self):
        p = get_persona_prompt("archivist", "ko")
        assert "진실" in p
        assert "출처" in p

    def test_merchant_ko(self):
        p = get_persona_prompt("merchant", "ko")
        assert "거래" in p
        assert "시장" in p

    def test_jester_ko(self):
        p = get_persona_prompt("jester", "ko")
        assert "규칙" in p
        assert "어그로" in p  # spec에서 의도적 유지

    def test_jester_en(self):
        p = get_persona_prompt("jester", "en")
        assert "chaos" in p.lower()

    def test_observer_ko(self):
        p = get_persona_prompt("observer", "ko")
        assert "100번" in p

    def test_architect_ko(self):
        p = get_persona_prompt("architect", "ko")
        assert "인프라" in p
        assert "세금" in p

    def test_no_survival_tips(self):
        """Phase 1: 생존 팁이 제거되었는지 확인"""
        for name in ALL_PERSONAS:
            ko = get_persona_prompt(name, "ko")
            en = get_persona_prompt(name, "en")
            assert "생존 팁" not in ko, f"{name} KO has survival tip"
            assert "SURVIVAL TIP" not in en, f"{name} EN has survival tip"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
