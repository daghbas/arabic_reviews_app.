from __future__ import annotations

import logging
from typing import List, Dict, Any

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - dependency optional at runtime
    genai = None

logger = logging.getLogger(__name__)


class GeminiService:
    MODEL_NAME = "gemini-1.5-pro-latest"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        if api_key and genai:
            genai.configure(api_key=api_key)
        elif not genai:
            logger.warning("google-generativeai package not installed; falling back to sample response")

    def analyze_reviews(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not self.api_key or not genai:
            return self._sample_analysis(reviews)

        prompt = self._build_prompt(reviews)
        try:
            model = genai.GenerativeModel(self.MODEL_NAME)
            response = model.generate_content(prompt)
            text = response.text if hasattr(response, "text") else str(response)
            return self._parse_response(text)
        except Exception as exc:  # pragma: no cover - network code
            logger.error("Gemini API error: %s", exc)
            return self._sample_analysis(reviews)

    @staticmethod
    def _build_prompt(reviews: List[Dict[str, Any]]) -> str:
        lines = [
            "أنت محلل نصوص متخصص في تقييم مراجعات العملاء باللهجة السعودية.",
            "حلل المراجعات التالية وأعد تقريراً منظمًا يتضمن: المشاعر العامة (إيجابي/سلبي/محايد)،", \
            "أهم المواضيع المتكررة، الكيانات المذكورة، والجوانب الرئيسية (مثل السعر، الخدمة، الجودة).",
            "أعد النتيجة في صيغة JSON مع المفاتيح: sentiment، topics (قائمة)، entities (قائمة)، aspects (قائمة)، summary (نص قصير).",
            "المراجعات:",
        ]
        for review in reviews:
            lines.append(f"- {review.get('text', '').strip()}")
        return "\n".join(lines)

    @staticmethod
    def _parse_response(text: str) -> Dict[str, Any]:
        import json

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.debug("Gemini response not JSON; wrapping into summary")
            return {
                "sentiment": "mixed",
                "topics": [],
                "entities": [],
                "aspects": [],
                "summary": text.strip(),
            }

    @staticmethod
    def _sample_analysis(reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        joined = " ".join(r.get("text", "") for r in reviews)
        sentiment = "positive" if "ممتاز" in joined or "جميل" in joined else "mixed"
        return {
            "sentiment": sentiment,
            "topics": ["الخدمة", "الأسعار"],
            "entities": ["المتجر", "الموظفون"],
            "aspects": [
                {"name": "service", "description": "تعليقات حول سرعة الاستجابة وجودة الخدمة."},
                {"name": "pricing", "description": "انطباعات عن مناسبة الأسعار."},
            ],
            "summary": "المراجعات تشير إلى رضا جيد عن الخدمة مع ملاحظات على الأسعار.",
        }
