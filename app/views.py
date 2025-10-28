from __future__ import annotations

import logging
from flask import Blueprint, render_template, request, current_app

from .collectors.google import GoogleCollector
from .collectors.salla import SallaCollector
from .services.gemini import GeminiService

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)


LANG_STRINGS = {
    "ar": {
        "title": "تحليل مراجعات العملاء",
        "description": "اختر المصدر وطريقة الجمع ثم ابدأ التحليل باستخدام Gemini.",
        "source_label": "المصدر",
        "source_google": "خرائط Google",
        "source_salla": "سلة",
        "method_label": "الطريقة",
        "method_api": "واجهة برمجة التطبيقات",
        "method_scrape": "استخلاص من الصفحة",
        "identifier_label": "معرّف المكان أو الرابط",
        "submit": "ابدأ التحليل",
        "missing_keys": "المفاتيح مفقودة، سيتم استخدام بيانات تجريبية.",
        "analysis_title": "نتائج التحليل",
        "sentiment": "المشاعر",
        "topics": "المواضيع",
        "entities": "الكيانات",
        "aspects": "الجوانب",
        "summary": "الملخص",
        "chart_sentiment": "تحليل المشاعر",
        "no_reviews": "لم يتم العثور على مراجعات، تم استخدام بيانات تجريبية.",
    },
    "en": {
        "title": "Customer Review Analysis",
        "description": "Choose the source and collection method, then analyze with Gemini.",
        "source_label": "Source",
        "source_google": "Google Maps",
        "source_salla": "Salla",
        "method_label": "Method",
        "method_api": "API",
        "method_scrape": "Scrape",
        "identifier_label": "Place ID or URL",
        "submit": "Analyze",
        "missing_keys": "API keys missing; sample data will be used.",
        "analysis_title": "Analysis Results",
        "sentiment": "Sentiment",
        "topics": "Topics",
        "entities": "Entities",
        "aspects": "Aspects",
        "summary": "Summary",
        "chart_sentiment": "Sentiment Analysis",
        "no_reviews": "No reviews found; sample data used.",
    },
}


def get_language() -> str:
    lang = request.args.get("lang")
    if lang in LANG_STRINGS:
        return lang
    header = request.headers.get("Accept-Language", "").lower()
    if "ar" in header:
        return "ar"
    return "en"


@main_bp.route("/")
def index():
    lang = get_language()
    texts = LANG_STRINGS[lang]
    sample_mode = current_app.config.get("SAMPLE_MODE", False)
    return render_template("index.html", texts=texts, sample_mode=sample_mode, lang=lang)


@main_bp.route("/analyze", methods=["POST"])
def analyze():
    lang = get_language()
    texts = LANG_STRINGS[lang]

    source = request.form.get("source", "google")
    method = request.form.get("method", "api")
    identifier = request.form.get("identifier", "")

    google_collector = GoogleCollector(current_app.config.get("GOOGLE_API_KEY"))
    salla_collector = SallaCollector(current_app.config.get("SALLA_TOKEN"))

    if source == "google":
        reviews = google_collector.fetch_reviews(identifier or "ChIJN1t_tDeuEmsRUsoyG83frY4", method)
    else:
        reviews = salla_collector.fetch_reviews(identifier, method)

    if not reviews:
        logger.info("No reviews retrieved; falling back to samples")
        reviews = google_collector._sample_reviews() if source == "google" else salla_collector._sample_reviews()

    gemini = GeminiService(current_app.config.get("GEMINI_API_KEY"))
    analysis = gemini.analyze_reviews(reviews)

    return render_template(
        "analysis.html",
        texts=texts,
        reviews=reviews,
        analysis=analysis,
        sample_mode=current_app.config.get("SAMPLE_MODE", False),
        lang=lang,
    )
