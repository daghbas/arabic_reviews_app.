import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    SALLA_TOKEN = os.getenv("SALLA_TOKEN")
    SAMPLE_MODE = not all([GEMINI_API_KEY, GOOGLE_API_KEY, SALLA_TOKEN])
