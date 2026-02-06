"""Adapter Base 테스트 — JSON 파싱, 유효성 검증"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from engine.adapters.base import BaseLLMAdapter, LLMResponse


class ConcreteAdapter(BaseLLMAdapter):
    """테스트용 구체 어댑터"""
    def generate(self, prompt, max_tokens=1000):
        return LLMResponse(thought="test", action="idle")


@pytest.fixture
def adapter():
    return ConcreteAdapter(model="test")


class TestLLMResponse:

    def test_to_action_dict_basic(self):
        r = LLMResponse(thought="t", action="speak")
        d = r.to_action_dict()
        assert d == {"type": "speak"}

    def test_to_action_dict_with_target(self):
        r = LLMResponse(thought="t", action="support", target="agent_01")
        d = r.to_action_dict()
        assert d == {"type": "support", "target": "agent_01"}

    def test_to_action_dict_with_content(self):
        r = LLMResponse(thought="t", action="speak", content="hello")
        d = r.to_action_dict()
        assert d == {"type": "speak", "content": "hello"}


class TestParseResponse:

    def test_valid_json(self, adapter):
        raw = '{"thought": "분석", "action": "trade", "target": null}'
        r = adapter.parse_response(raw)
        assert r.success is True
        assert r.action == "trade"
        assert r.thought == "분석"

    def test_json_with_surrounding_text(self, adapter):
        raw = 'Here is my response:\n{"thought": "ok", "action": "speak", "content": "hello"}\nDone.'
        r = adapter.parse_response(raw)
        assert r.success is True
        assert r.action == "speak"
        assert r.content == "hello"

    def test_invalid_json(self, adapter):
        raw = "I don't know what to do"
        r = adapter.parse_response(raw)
        assert r.success is False
        assert r.action == "idle"

    def test_empty_string(self, adapter):
        r = adapter.parse_response("")
        assert r.success is False
        assert r.action == "idle"

    def test_missing_action_defaults_idle(self, adapter):
        raw = '{"thought": "hmm"}'
        r = adapter.parse_response(raw)
        assert r.action == "idle"

    def test_all_fields(self, adapter):
        raw = '{"thought": "이유", "action": "whisper", "target": "a1", "content": "secret"}'
        r = adapter.parse_response(raw)
        assert r.thought == "이유"
        assert r.action == "whisper"
        assert r.target == "a1"
        assert r.content == "secret"


class TestValidateAction:

    def test_valid_action(self, adapter):
        r = LLMResponse(thought="t", action="speak")
        r = adapter.validate_action(r, ["speak", "trade", "idle"])
        assert r.action == "speak"

    def test_invalid_action_falls_to_idle(self, adapter):
        r = LLMResponse(thought="t", action="fly")
        r = adapter.validate_action(r, ["speak", "trade", "idle"])
        assert r.action == "idle"
        assert r.error is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
