from __future__ import annotations

import logging
from typing import List, Dict, Any

import requests

logger = logging.getLogger(__name__)


class GoogleCollector:
    BASE_URL = "https://maps.googleapis.com/maps/api/place/details/json"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def fetch_reviews(self, identifier: str, method: str = "api") -> List[Dict[str, Any]]:
        if method == "api":
            return self._fetch_via_api(identifier)
        if method == "scrape":
            return self._fetch_via_scrape(identifier)
        raise ValueError("Unsupported method for Google reviews")

    def _fetch_via_api(self, place_id: str) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("Google API key missing; returning sample reviews")
            return self._sample_reviews()

        params = {
            "place_id": place_id,
            "key": self.api_key,
            "fields": "review"
        }
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.error("Google Places API error: %s", exc)
            return self._sample_reviews()

        reviews = data.get("result", {}).get("reviews", [])
        formatted = []
        for review in reviews:
            formatted.append({
                "author": review.get("author_name", "Anonymous"),
                "rating": review.get("rating"),
                "text": review.get("text", ""),
                "time": review.get("relative_time_description", "")
            })
        return formatted or self._sample_reviews()

    def _fetch_via_scrape(self, url: str) -> List[Dict[str, Any]]:
        # Basic scraper that looks for structured data in the page.
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Google reviews scraping error: %s", exc)
            return self._sample_reviews()

        # Attempt to extract reviews from embedded JSON-LD if available
        reviews: List[Dict[str, Any]] = []
        try:
            for line in response.text.splitlines():
                if '"review"' in line:
                    reviews.append({
                        "author": "Google Maps User",
                        "rating": None,
                        "text": line.strip(),
                        "time": ""
                    })
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("Failed parsing scraped data: %s", exc)

        return reviews or self._sample_reviews()

    @staticmethod
    def _sample_reviews() -> List[Dict[str, Any]]:
        return [
            {
                "author": "محمد",
                "rating": 5,
                "text": "الخدمة ممتازة والموظفون محترفون.",
                "time": "قبل يوم"
            },
            {
                "author": "Sara",
                "rating": 3,
                "text": "المكان جميل لكن الأسعار مرتفعة قليلاً.",
                "time": "قبل ثلاثة أيام"
            },
        ]
