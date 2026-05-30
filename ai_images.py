"""Rasm olish (BEPUL):
- AI generatsiya  -> Pollinations.ai (kalit kerak emas, Flux modeli)
- Web qidiruv     -> Pexels API (bepul kalit)
"""
import io
import urllib.parse

import requests
from PIL import Image

import config

_POLLINATIONS = "https://image.pollinations.ai/prompt/"
_PEXELS = "https://api.pexels.com/v1/search"


def generate_ai_image(prompt: str) -> bytes | None:
    """Pollinations orqali mavzuga mos AI rasm yaratadi (PNG/JPEG baytlar)."""
    try:
        encoded = urllib.parse.quote(prompt[:900])
        url = f"{_POLLINATIONS}{encoded}"
        params = {
            "width": 1024,
            "height": 1024,
            "model": config.POLLINATIONS_MODEL,
            "nologo": "true",
            "safe": "true",
        }
        r = requests.get(url, params=params, timeout=120)
        r.raise_for_status()
        if _looks_like_image(r.content):
            return r.content
    except Exception as e:
        print(f"[ai_image/pollinations] xato: {e}")
    return None


def fetch_web_image(query: str) -> bytes | None:
    """Pexels orqali mavzuga mos professional rasm topadi."""
    config.require("PEXELS_API_KEY", config.PEXELS_API_KEY)
    try:
        headers = {"Authorization": config.PEXELS_API_KEY}
        params = {"query": query, "per_page": 5, "orientation": "landscape"}
        r = requests.get(_PEXELS, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        photos = r.json().get("photos", [])
        for p in photos:
            src = p.get("src", {})
            link = src.get("large2x") or src.get("large") or src.get("original")
            if not link:
                continue
            data = _download(link)
            if data and _looks_like_image(data):
                return data
    except Exception as e:
        print(f"[web_image/pexels] xato: {e}")
    return None


def _download(url: str) -> bytes | None:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (SlideBot)"}
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        return r.content
    except Exception:
        return None


def _looks_like_image(data: bytes) -> bool:
    try:
        Image.open(io.BytesIO(data)).verify()
        return True
    except Exception:
        return False


def normalize_to_png(data: bytes) -> bytes | None:
    """Har qanday formatdagi rasmni python-pptx uchun PNG ga aylantiradi."""
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
        out = io.BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()
    except Exception:
        return None
