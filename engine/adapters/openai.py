"""OpenAI GPT LLM 어댑터"""

import os
from typing import Optional

from .base import BaseLLMAdapter, LLMResponse


class OpenAIAdapter(BaseLLMAdapter):

    def __init__(
        self,
        model: str = "gpt-5-nano",
        api_key: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(model, **kwargs)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")

    def generate(self, prompt: str, max_tokens: int = 16000) -> LLMResponse:
        if not self.api_key:
            return LLMResponse(
                thought="OPENAI_API_KEY not set",
                action="idle",
                success=False,
                error="API 키 없음",
            )

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            params = {
                "model": self.model,
                "max_completion_tokens": max_tokens,
                "response_format": {"type": "json_object"},
                "messages": [{"role": "user", "content": prompt}],
            }
            # GPT-5 and o-series models don't support temperature
            if not any(x in self.model for x in ["gpt-5", "o1", "o3", "o4"]):
                params["temperature"] = 0.7
            response = client.chat.completions.create(**params)
            raw_text = response.choices[0].message.content or ""
            if not raw_text:
                return LLMResponse(
                    thought="빈 응답 (토큰 부족 가능)",
                    action="idle",
                    success=False,
                    error=f"Empty response, finish_reason={response.choices[0].finish_reason}",
                )
            return self.parse_response(raw_text)

        except ImportError:
            return LLMResponse(
                thought="openai 패키지 미설치",
                action="idle",
                success=False,
                error="pip install openai",
            )
        except Exception as e:
            return LLMResponse(
                thought=f"OpenAI API 오류: {e}",
                action="idle",
                success=False,
                error=str(e),
            )
