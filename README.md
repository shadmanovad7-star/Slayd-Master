# 🤖 SlideBot — AI prezentatsiya generatori (Telegram) · BEPUL to'plam

O'zbek va rus tilida ishlaydigan, 10–30 slaydli prezentatsiyalarni AI yordamida
yasab beradigan Telegram bot. **Hammasi bepul** servislar bilan ishlaydi.

## Oqim
1. `/start` → til (🇺🇿/🇷🇺) → slayd soni (10–30) → mavzu
2. Bot ideal matn tayyorlaydi, ko'rsatadi:
   - ✅ to'g'ri kelsa — **stiker** yuboring
   - ✏️ o'zgartirish / ➖ qisqartirish / ➕ ko'paytirish
3. Rasm manbai: 🎨 AI yaratsin (Pollinations) yoki 🌐 Webdan (Pexels)
4. Tayyor `.pptx` faylni yuboradi

## Qaysi servis nima qiladi (hammasi BEPUL)
| Vazifa | Servis | Kalit kerakmi | Narx |
|---|---|---|---|
| Bot | Telegram BotFather | Token | Bepul |
| Matn | Google **Gemini 2.5 Flash** | Bepul kalit | Bepul (free tier) |
| AI rasm | **Pollinations** (Flux) | ❌ kerak emas | Bepul |
| Web rasm | **Pexels** | Bepul kalit | Bepul |

## Kalitlarni qayerdan olish
1. **Telegram token** → Telegramda @BotFather → `/newbot`
2. **Gemini** → https://aistudio.google.com → "Get API key" (karta kerak emas)
3. **Pexels** → https://www.pexels.com/api/ → ro'yxatdan o'ting → API key
4. **Pollinations** → hech narsa shart emas 🎉

## O'rnatish va ishga tushirish
```bash
pip install -r requirements.txt
cp .env.example .env      # kalitlarni to'ldiring
python bot.py
```

## Stiker bilan tasdiqlash
`.env` dagi `CONFIRM_STICKER_ID` bo'sh bo'lsa — **istalgan** stiker tasdiq bo'ladi.
Aniq bitta stikerni majburiy qilmoqchi bo'lsangiz, botga o'sha stikerni yuboring —
u `file_unique_id` ni ko'rsatadi, o'shani `.env` ga yozing.

## Eslatma (limitlar)
- Gemini bepul tier: kuniga ~1500 so'rovgacha (ko'p prezentatsiyaga yetadi).
- Pexels bepul: soatiga 200, oyiga 20 000 so'rovgacha.
- Pollinations: bepul, kalitsiz.

## Fayllar
- `bot.py` — asosiy bot va suhbat oqimi
- `ai_content.py` — Gemini orqali slayd matnlari
- `ai_images.py` — Pollinations (AI rasm) + Pexels (web rasm)
- `pptx_builder.py` — `.pptx` yig'ish
- `locales.py` — uz/ru matnlar
- `config.py` — sozlamalar
