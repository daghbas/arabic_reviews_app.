# Arabic + English Review Analyzer

Bilingual Flask web application that gathers Arabic customer reviews from Google Maps and Salla, sends them directly to Gemini for analysis, and presents the findings with a dark Tailwind UI and Chart.js visualizations.

## Features
- Collect reviews from Google Maps (Place Details API) or Salla using either API access or lightweight scraping fallback.
- Analyze reviews exclusively with Gemini (no manual NLP) for sentiment, topics, entities, and aspects.
- Dark Tailwind CSS theme with Chart.js doughnut visualization.
- Bilingual interface (Arabic / English) with auto language detection via the browser `Accept-Language` header.
- Graceful fallback to bundled sample data whenever API keys or tokens are missing.

## Project Structure
```
├── run.py
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── views.py
│   ├── collectors/
│   │   ├── google.py
│   │   └── salla.py
│   ├── services/
│   │   └── gemini.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   └── analysis.html
│   └── static/
│       └── css/styles.css
├── requirements.txt
└── .env.example
```

## Getting Started
1. **Clone & install dependencies**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   Copy `.env.example` to `.env` and fill in the keys:
   ```bash
   cp .env.example .env
   ```

   - `GEMINI_API_KEY`: Generated from [Google AI Studio](https://aistudio.google.com/app/apikey).
   - `GOOGLE_API_KEY`: Obtain via Google Cloud Console → create a project → enable **Places API** → create an API key.
   - `SALLA_TOKEN`: Sign in to [Salla Developers](https://developers.salla.sa/) → create an app → request the `read:reviews` scope → exchange for an OAuth token.
   - `SECRET_KEY`: Any random string for Flask sessions.

   If any value is missing the application automatically switches to sample mode with bundled demo reviews and sample Gemini analysis.

3. **Run the app**
   ```bash
   python run.py
   ```
   Visit `http://localhost:5000` and choose the source, method, and identifier (Place ID or URL).

## Review Collection Notes
- **Google API**: Requires a Place ID (e.g., from Google Maps URL parameters). The app calls the Place Details API requesting the `review` field.
- **Google Scrape**: Minimal HTML fetch that attempts to read embedded snippets. For production, prefer the official API due to Terms of Service.
- **Salla API**: Uses the Admin v2 endpoint `/store/reviews` and expects a bearer token with `read:reviews`.
- **Salla Scrape**: Simple HTML fallback for public storefront URLs when API access is unavailable.

## Gemini Analysis
All reviews are forwarded exactly as received to Gemini (`gemini-1.5-pro-latest`). The service asks Gemini for a JSON payload summarizing sentiment, topics, entities, and aspects. When the Gemini SDK or API key is not available, a deterministic sample response keeps the UI working offline.

## Localization
Language defaults to Arabic if the browser advertises Arabic in `Accept-Language`. Users can manually switch using the language buttons in the header.

## Security & Environment
- Never commit your real API keys; use `.env`.
- Production deployments should disable `debug=True` in `run.py`.

## Troubleshooting
- **Missing keys**: Ensure `.env` is loaded. The UI displays an amber banner when running in sample mode.
- **Google API quota**: Monitor usage in Google Cloud Console and restrict the key to required APIs.
- **Salla authorization**: Regenerate tokens if you receive 401 errors and confirm the app has the `read:reviews` scope.
