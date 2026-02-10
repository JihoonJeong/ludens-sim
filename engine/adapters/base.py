"""LLM 어댑터 추상 클래스"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import json
import re


@dataclass
class LLMResponse:
    """LLM 응답 구조"""
    thought: str
    action: str
    target: Optional[str] = None
    content: Optional[str] = None
    raw_response: dict = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None

    def to_action_dict(self) -> dict:
        action_dict = {"type": self.action}
        if self.target:
            action_dict["target"] = self.target
        if self.content:
            action_dict["content"] = self.content
        return action_dict


class BaseLLMAdapter(ABC):
    """LLM 어댑터 추상 클래스"""

    def __init__(self, model: str, **kwargs):
        self.model = model
        self.config = kwargs

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 1000,
                 system_prompt: str | None = None) -> LLMResponse:
        pass

    def parse_response(self, raw_text: str) -> LLMResponse:
        try:
            text = raw_text
            # Strip markdown code fences (```json ... ``` or ``` ... ```)
            fence_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
            if fence_match:
                text = fence_match.group(1)
            # Find outermost JSON object using brace balancing
            json_str = self._extract_json_object(text)
            if json_str:
                data = json.loads(json_str)
                return LLMResponse(
                    thought=data.get("thought", ""),
                    action=data.get("action", "idle"),
                    target=data.get("target"),
                    content=data.get("message") or data.get("content"),
                    raw_response={"text": raw_text, "parsed": data},
                    success=True,
                )
        except json.JSONDecodeError:
            pass

        return LLMResponse(
            thought="응답 파싱 실패",
            action="idle",
            raw_response={"text": raw_text},
            success=False,
            error="JSON 파싱 실패",
        )

    @staticmethod
    def _extract_json_object(text: str) -> Optional[str]:
        """Extract outermost JSON object using brace balancing."""
        start = text.find('{')
        if start == -1:
            return None
        depth = 0
        in_string = False
        escape_next = False
        for i in range(start, len(text)):
            c = text[i]
            if escape_next:
                escape_next = False
                continue
            if c == '\\' and in_string:
                escape_next = True
                continue
            if c == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        return None

    def validate_action(self, response: LLMResponse, valid_actions: list[str]) -> LLMResponse:
        if response.action not in valid_actions:
            response.action = "idle"
            response.error = f"유효하지 않은 액션: {response.action}"
        return response

    @property
    def name(self) -> str:
        return self.__class__.__name__
