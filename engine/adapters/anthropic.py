"""Anthropic Claude LLM 어댑터"""

import os
from typing import Optional

from .base import BaseLLMAdapter, LLMResponse


class AnthropicAdapter(BaseLLMAdapter):

    def __init__(
        self,
        model: str = "claude-sonnet-4-5-20250929",
        api_key: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(model, **kwargs)
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.max_tokens = kwargs.get("max_tokens", 1000)

    def generate(self, prompt: str, max_tokens: int = 1000,
                 system_prompt: str | None = None) -> LLMResponse:
        if not self.api_key:
            return LLMResponse(
                thought="ANTHROPIC_API_KEY not set",
                action="idle",
                success=False,
                error="API 키 없음",
            )

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)
            create_kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system_prompt:
                create_kwargs["system"] = system_prompt
            message = client.messages.create(**create_kwargs)
            raw_text = message.content[0].text
            return self.parse_response(raw_text)

        except ImportError:
            return LLMResponse(
                thought="anthropic 패키지 미설치",
                action="idle",
                success=False,
                error="pip install anthropic",
            )
        except Exception as e:
            return LLMResponse(
                thought=f"Claude API 오류: {e}",
                action="idle",
                success=False,
                error=str(e),
            )
