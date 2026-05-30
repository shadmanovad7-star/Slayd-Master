"""Konfiguratsiya — barcha sozlamalar .env dan o'qiladi (BEPUL to'plam)."""
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# --- Matn: Google Gemini (BEPUL tier) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# --- AI rasm: Pollinations (kalit kerak emas) ---
POLLINATIONS_MODEL = os.getenv("POLLINATIONS_MODEL", "flux")

# --- Web rasm: Pexels (BEPUL kalit) ---
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# Tasdiqlash stikeri (ixtiyoriy). Bo'sh bo'lsa istalgan stiker tasdiq bo'ladi.
CONFIRM_STICKER_ID = os.getenv("CONFIRM_STICKER_ID", "").strip()

# Slayd soni chegaralari
MIN_SLIDES = 10
MAX_SLIDES = 30


def require(name: str, value: str):
    if not value:
        raise RuntimeError(f"{name} .env faylida ko'rsatilmagan!")
