# Arabic + English Review Analyzer

A bilingual Flask 3.0 application that blends Gemini-powered review intelligence with a reusable authentication stack. Collect Arabic reviews from Google Maps and Salla, analyse them directly with Gemini, and explore the results within a dark Tailwind interface that now ships with email verification, password resets, and role-aware dashboards.

## Features
- 🔐 **Reusable authentication system** with registration, login via username/email, email verification, forgot/reset password flows, profile management, and account deletion.
- 🧑‍🤝‍🧑 **Role-based routing** for standard users and administrators, including an admin console for adding, deleting, and filtering users by role.
- 🌐 **Bilingual experience** (Arabic / English) with per-user language preferences and ready hooks for future locales.
- 🧭 **Review collection** from Google Maps and Salla through API or scraping fallbacks, with sample datasets when credentials are missing.
- 🤖 **Gemini-only analysis** that sends raw reviews straight to Gemini to extract sentiment, topics, entities, aspects, and summaries.
- 🎨 **Dark Tailwind UI + Chart.js** visualisation for sentiment alongside responsive layouts for auth, dashboards, and analytics views.

## Project Structure
```
├── run.py
├── app/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── collectors/
│   │   ├── google.py
│   │   └── salla.py
│   ├── config.py
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── extensions.py
│   ├── models.py
│   ├── services/
│   │   ├── email.py
│   │   ├── gemini.py
│   │   └── tokens.py
│   ├── templates/
│   │   ├── analysis.html
│   │   ├── auth/
│   │   ├── base.html
│   │   ├── dashboard/
│   │   └── index.html
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
   Copy `.env.example` to `.env` and update the values:
   ```bash
   cp .env.example .env
   ```

   | Variable | Description |
   | --- | --- |
   | `GEMINI_API_KEY` | Create via [Google AI Studio](https://aistudio.google.com/app/apikey). |
   | `GOOGLE_API_KEY` | Google Cloud Console → enable **Places API** → generate API key. |
   | `SALLA_TOKEN` | [Salla Developers](https://developers.salla.sa/) → create app → request `read:reviews` scope → exchange for OAuth token. |
   | `SECRET_KEY` / `SECURITY_TOKEN_SALT` | Random strings for Flask session + token signing. |
   | `DATABASE_URL` | SQLite connection string. Defaults to `sqlite:///instance/app.db`. |
   | `DEFAULT_ADMIN_*` | Bootstrap admin credentials created on first launch—change after login. |
   | `MAIL_*` | SMTP configuration for verification and password reset emails. Leave blank to log email links to the console while prototyping. |

   > Missing API keys? The platform automatically switches to sample mode with offline-friendly data.

3. **Run database + server**
   ```bash
   python run.py
   ```
   Browse to `http://localhost:5000`. You will be redirected to the authentication flow. After signing in you can:
   - Visit `/dashboard/home` for the standard user experience.
   - Visit `/dashboard/admin` (admin role only) to manage accounts.
   - Launch the bilingual review analyser from the “Launch review analyzer” button.

## Authentication Workflow
- **Sign up** collects username, email, password, and confirmation. A verification email is dispatched with a single-click activation button.
- **Sign in** accepts either the username or email paired with the password. Unverified users are redirected to a resend-verification screen.
- **Email verification** page reminds users to check the inbox or spam folder and includes a resend action.
- **Forgot password** sends a reset email with a one-hour token. The reset link opens a form to set a new password and returns the user to sign in.
- **Profile management** exposes user metadata, language preference, change password modal (forces re-login), and secure account deletion (password confirmation required).
- **Admin console** lists all users in a searchable, filterable table with one-click delete (except self) and quick creation of additional roles ready for future expansion.

All templates are dark-themed, mobile responsive, and ready for translation. Locale changes currently support English and Arabic and can be extended via the profile page dropdown.

## Review Collection Notes
- **Google API**: Requires a Place ID (e.g., gleaned from Google Maps URL parameters). Calls the Place Details API requesting the `review` field.
- **Google Scrape**: Lightweight HTML fetch for sandboxing. For production, prefer the official API to comply with Google Terms of Service.
- **Salla API**: Uses the Admin v2 endpoint `/store/reviews` and expects a bearer token with `read:reviews`.
- **Salla Scrape**: Simple HTML fallback for public storefront URLs when API access is unavailable.

## Gemini Analysis
Reviews are forwarded verbatim to Gemini (`gemini-1.5-pro-latest`). The response is requested in JSON for sentiment, topics, entities, aspects, and summaries. When the Gemini SDK or API key is missing, a deterministic offline response keeps the UI functional.

## Localization & Extensibility
- Automatic language detection still respects the browser’s `Accept-Language`, while authenticated users can override the preference in their profile.
- Templates and configuration are structured so that additional locales can be dropped in with minimal plumbing.

## Troubleshooting
- **Email links not arriving**: Verify SMTP credentials. When `MAIL_SERVER` is unset the app logs verification and reset URLs to the console so flows are still testable.
- **Admin account**: Update the default admin credentials immediately after first login via the profile change password modal.
- **SQLite file**: Stored under `instance/app.db`. Delete it to reset the environment.
- **Sample mode banner**: Indicates that one or more API keys are missing; analytics will use bundled data.

## Testing
To ensure imports compile:
```bash
python -m compileall app run.py
```
