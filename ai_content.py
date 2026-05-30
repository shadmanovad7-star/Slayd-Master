"""Matn (kontent) generatsiyasi — Google Gemini (BEPUL tier) orqali, REST API.

Har bir prezentatsiya quyidagi JSON strukturada saqlanadi:
{
  "title": "...",
  "subtitle": "...",
  "slides": [
     {"title": "...", "bullets": ["...", "..."],
      "image_query": "qisqa web qidiruv so'rovi (ingliz tilida)",
      "image_prompt": "AI rasm uchun batafsil prompt (ingliz tilida)"}
  ]
}
"""
import json
import requests

import config

_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

_LANG_NAME = {"uz": "o'zbek", "ru": "русском"}


def _system_prompt(lang: str) -> str:
    lang_name = _LANG_NAME.get(lang, "o'zbek")
    return (
        f"Sen professional prezentatsiya tuzuvchisan. Slaydlar matnini {lang_name} tilida yozasan. "
        "Javobni FAQAT to'g'ri JSON ko'rinishida qaytar (izoh, markdown yoki ortiqcha matnsiz). "
        "JSON sxemasi:\n"
        '{"title": str, "subtitle": str, "slides": [ '
        '{"title": str, "bullets": [str, ...], "image_query": str, "image_prompt": str} ]}\n'
        "Qoidalar:\n"
        "- slides massivida ANIQ so'ralgan songa teng slayd bo'lsin.\n"
        "- Birinchi slayd — kirish/sarlavha, oxirgi slayd — xulosa.\n"
        "- Har bir slaydda 3-5 ta qisqa, tushunarli bullet bo'lsin.\n"
        "- 'image_query' va 'image_prompt' HAR DOIM ingliz tilida bo'lsin.\n"
        "- Ma'lumot ideal, aniq va mavzuga to'liq mos bo'lsin."
    )


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    return json.loads(text)


def _call(system: str, user: str) -> dict:
    config.require("GEMINI_API_KEY", config.GEMINI_API_KEY)
    url = _URL.format(model=config.GEMINI_MODEL)
    body = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json",
        },
    }
    r = requests.post(url, params={"key": config.GEMINI_API_KEY}, json=body, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"Gemini xatosi {r.status_code}: {r.text[:300]}")
    data = r.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"Gemini bo'sh javob qaytardi: {str(data)[:300]}")
    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts)
    return _extract_json(text)


def generate_content(topic: str, slides: int, lang: str) -> dict:
    user = (
        f"Mavzu: «{topic}».\n"
        f"Slaydlar soni: {slides} ta.\n"
        "Shu mavzuda to'liq prezentatsiya kontentini yarat."
    )
    return _normalize(_call(_system_prompt(lang), user), slides)


def modify_content(current: dict, instruction: str, slides: int, lang: str) -> dict:
    user = (
        "Quyidagi prezentatsiya kontenti bor (JSON):\n"
        f"{json.dumps(current, ensure_ascii=False)}\n\n"
        f"Foydalanuvchi so'rovi: «{instruction}».\n"
        f"Shu so'rovga ko'ra kontentni o'zgartir. Slaydlar soni {slides} ta bo'lsin."
    )
    return _normalize(_call(_system_prompt(lang), user), slides)


def shorten_content(current: dict, slides: int, lang: str) -> dict:
    user = (
        "Quyidagi kontentni QISQARTIR — bulletlarni soddalashtir va kamaytir, "
        "lekin mavzu mohiyati saqlansin (JSON):\n"
        f"{json.dumps(current, ensure_ascii=False)}\n\n"
        f"Slaydlar soni {slides} ta bo'lsin."
    )
    return _normalize(_call(_system_prompt(lang), user), slides)


def expand_content(current: dict, slides: int, lang: str) -> dict:
    user = (
        "Quyidagi kontentni KENGAYTIR — har bir slaydga ko'proq va chuqurroq "
        "ma'lumot qo'sh (JSON):\n"
        f"{json.dumps(current, ensure_ascii=False)}\n\n"
        f"Slaydlar soni {slides} ta bo'lsin."
    )
    return _normalize(_call(_system_prompt(lang), user), slides)


def _normalize(data: dict, slides: int) -> dict:
    data.setdefault("title", "Presentation")
    data.setdefault("subtitle", "")
    sl = data.get("slides", [])
    if not isinstance(sl, list):
        sl = []
    fixed = []
    for s in sl:
        if not isinstance(s, dict):
            continue
        fixed.append({
            "title": str(s.get("title", "")).strip() or "Slide",
            "bullets": [str(b).strip() for b in s.get("bullets", []) if str(b).strip()],
            "image_query": str(s.get("image_query", data["title"])).strip(),
            "image_prompt": str(s.get("image_prompt", data["title"])).strip(),
        })
    data["slides"] = fixed
    return data


def build_preview(data: dict, max_chars: int = 3000) -> str:
    lines = [f"📌 {data.get('title', '')}"]
    if data.get("subtitle"):
        lines.append(f"   {data['subtitle']}")
    lines.append("")
    for i, s in enumerate(data.get("slides", []), 1):
        lines.append(f"{i}. {s['title']}")
        for b in s["bullets"][:5]:
            lines.append(f"   • {b}")
    text = "\n".join(lines)
    if len(text) > max_chars:
        text = text[:max_chars - 20].rstrip() + "\n… (davomi PPTX da)"
    return text
