"""Ikki tilli matnlar: uz va ru."""

LOCALES = {
    "uz": {
        "choose_lang": "Tilni tanlang / Выберите язык:",
        "lang_set": "✅ Til tanlandi: O'zbekcha",
        "ask_count": "📊 Prezentatsiya necha slayddan iborat bo'lsin?\n\nQuyidagi sonlardan birini tanlang ({mn}–{mx}):",
        "count_set": "✅ Slaydlar soni: {n}",
        "ask_topic": "📝 Prezentatsiya qaysi mavzuda bo'lsin?\n\nMavzuni yozib yuboring:",
        "generating_content": "⏳ «{topic}» mavzusida ma'lumot tayyorlanmoqda...",
        "content_caption": (
            "📄 Tayyorlangan ma'lumot ({n} slayd):\n\n{preview}\n\n"
            "──────────────\n"
            "• Agar ma'lumot to'g'ri kelsa — istalgan *stiker* yuboring ✅\n"
            "• Yoki quyidagi tugmalardan birini tanlang 👇"
        ),
        "btn_change": "✏️ O'zgartirish",
        "btn_shorten": "➖ Qisqartirish",
        "btn_expand": "➕ Ko'paytirish",
        "ask_change": "✏️ Qaysi joylarni o'zgartirish kerakligini yozing:",
        "applying": "⏳ O'zgartirishlar qo'llanmoqda...",
        "shortening": "⏳ Ma'lumot qisqartirilmoqda...",
        "expanding": "⏳ Ma'lumot kengaytirilmoqda...",
        "ask_image_source": "🖼 Rasmlar qayerdan olinsin?",
        "btn_ai_images": "🎨 AI yaratsin",
        "btn_web_images": "🌐 Webdan (Google) olinsin",
        "building_ai": "🎨 AI rasmlar yaratilmoqda va prezentatsiya yig'ilmoqda...\nBu biroz vaqt olishi mumkin.",
        "building_web": "🌐 Web (Google) dan mos rasmlar topilmoqda va prezentatsiya yig'ilmoqda...",
        "done": "✅ Tayyor! Prezentatsiyangiz quyida.",
        "doc_caption": "📎 «{topic}» — {n} slayd",
        "restart_hint": "Yangi prezentatsiya uchun /start buyrug'ini yuboring.",
        "err_generic": "❌ Xatolik yuz berdi: {e}\n/start bilan qayta urinib ko'ring.",
        "confirm_sticker_hint": "Tasdiqlash uchun stiker yuboring yoki tugmani bosing.",
        "not_a_number": "Iltimos, {mn}–{mx} oralig'idagi tugmani tanlang.",
    },
    "ru": {
        "choose_lang": "Tilni tanlang / Выберите язык:",
        "lang_set": "✅ Язык выбран: Русский",
        "ask_count": "📊 Из скольких слайдов будет состоять презентация?\n\nВыберите одно из чисел ({mn}–{mx}):",
        "count_set": "✅ Количество слайдов: {n}",
        "ask_topic": "📝 На какую тему будет презентация?\n\nНапишите тему:",
        "generating_content": "⏳ Готовлю материал по теме «{topic}»...",
        "content_caption": (
            "📄 Подготовленный материал ({n} слайдов):\n\n{preview}\n\n"
            "──────────────\n"
            "• Если материал подходит — отправьте любой *стикер* ✅\n"
            "• Или выберите одну из кнопок ниже 👇"
        ),
        "btn_change": "✏️ Изменить",
        "btn_shorten": "➖ Сократить",
        "btn_expand": "➕ Дополнить",
        "ask_change": "✏️ Напишите, какие места нужно изменить:",
        "applying": "⏳ Применяю изменения...",
        "shortening": "⏳ Сокращаю материал...",
        "expanding": "⏳ Дополняю материал...",
        "ask_image_source": "🖼 Откуда брать изображения?",
        "btn_ai_images": "🎨 Сгенерировать ИИ",
        "btn_web_images": "🌐 Из веба (Google)",
        "building_ai": "🎨 Генерирую изображения ИИ и собираю презентацию...\nЭто может занять время.",
        "building_web": "🌐 Ищу подходящие изображения в вебе (Google) и собираю презентацию...",
        "done": "✅ Готово! Ваша презентация ниже.",
        "doc_caption": "📎 «{topic}» — {n} слайдов",
        "restart_hint": "Для новой презентации отправьте /start.",
        "err_generic": "❌ Произошла ошибка: {e}\nПопробуйте снова через /start.",
        "confirm_sticker_hint": "Отправьте стикер для подтверждения или нажмите кнопку.",
        "not_a_number": "Пожалуйста, выберите кнопку в диапазоне {mn}–{mx}.",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in LOCALES else "uz"
    text = LOCALES[lang].get(key, key)
    return text.format(**kwargs) if kwargs else text
