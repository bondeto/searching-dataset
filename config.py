"""
Configuration module for Dataset Searcher.
Loads API keys and settings from .env or environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# --- Kaggle ---
KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME", "")
KAGGLE_KEY = os.getenv("KAGGLE_KEY", "")

# --- HuggingFace ---
HF_TOKEN = os.getenv("HF_TOKEN", "")

# --- Cache ---
CACHE_DIR = BASE_DIR / ".cache"
CACHE_DIR.mkdir(exist_ok=True)
CACHE_TTL_SECONDS = 3600  # 1 hour

# --- HTTP ---
HTTP_TIMEOUT = 20.0
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# --- Output ---
EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(exist_ok=True)

# --- Sources ---
ENABLED_SOURCES = ["kaggle", "huggingface", "openml", "uci", "dataportal"]
