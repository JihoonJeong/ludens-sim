"""Google Gemini LLM 어댑터"""

import os
from typing import Optional

from .base import BaseLLMAdapter, LLMResponse


class GoogleAdapter(BaseLLMAdapter):

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        api_key: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(model, **kwargs)
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")

    def generate(self, prompt: str, max_tokens: int = 1000) -> LLMResponse:
        if not self.api_key:
            return LLMResponse(
                thought="GOOGLE_API_KEY not set",
                action="idle",
                success=False,
                error="API 키 없음",
            )

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                ),
            )
            raw_text = response.text
            return self.parse_response(raw_text)

        except ImportError:
            return LLMResponse(
                thought="google-generativeai 패키지 미설치",
                action="idle",
                success=False,
                error="pip install google-generativeai",
            )
        except Exception as e:
            return LLMResponse(
                thought=f"Gemini API 오류: {e}",
                action="idle",
                success=False,
                error=str(e),
            )
