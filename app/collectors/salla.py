from __future__ import annotations

import logging
from typing import List, Dict, Any

import requests

logger = logging.getLogger(__name__)


class SallaCollector:
    API_URL = "https://api.salla.dev/admin/v2/store/reviews"

    def __init__(self, token: str | None = None):
        self.token = token

    def fetch_reviews(self, identifier: str, method: str = "api") -> List[Dict[str, Any]]:
        if method == "api":
            return self._fetch_via_api()
        if method == "scrape":
            return self._fetch_via_scrape(identifier)
        raise ValueError("Unsupported method for Salla reviews")

    def _fetch_via_api(self) -> List[Dict[str, Any]]:
        if not self.token:
            logger.warning("Salla API token missing; returning sample reviews")
            return self._sample_reviews()

        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.get(self.API_URL, headers=headers, timeout=20)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.error("Salla API error: %s", exc)
            return self._sample_reviews()

        reviews = data.get("data", [])
        formatted = []
        for review in reviews:
            formatted.append({
                "author": review.get("customer", {}).get("name", "عميل سلة"),
                "rating": review.get("rating"),
                "text": review.get("comment", ""),
                "time": review.get("created_at", "")
            })
        return formatted or self._sample_reviews()

    def _fetch_via_scrape(self, url: str) -> List[Dict[str, Any]]:
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Salla scraping error: %s", exc)
            return self._sample_reviews()

        reviews: List[Dict[str, Any]] = []
        try:
            for line in response.text.splitlines():
                if "review" in line.lower():
                    reviews.append({
                        "author": "عميل سلة",
                        "rating": None,
                        "text": line.strip(),
                        "time": ""
                    })
        except Exception as exc:  # pragma: no cover
            logger.debug("Failed parsing scraped data: %s", exc)

        return reviews or self._sample_reviews()

    @staticmethod
    def _sample_reviews() -> List[Dict[str, Any]]:
        return [
            {
                "author": "عبدالله",
                "rating": 4,
                "text": "تجربة شراء سلسة وخدمة عملاء سريعة.",
                "time": "2024-05-01"
            },
            {
                "author": "Lama",
                "rating": 2,
                "text": "التغليف كان سيئاً ووصل الطلب متأخراً.",
                "time": "2024-04-22"
            },
        ]
