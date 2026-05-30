"""Telegram bot — AI prezentatsiya generatori.

Oqim:
/start → til tanlash → slayd soni (10–30) → mavzu →
ma'lumot ko'rib chiqish (stiker bilan tasdiq / o'zgartirish / qisqartirish / ko'paytirish) →
rasm manbai (AI yoki Web) → tayyor PPTX.
"""
import asyncio
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, constants,
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters,
)

import config
import ai_content
import pptx_builder
from locales import t

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO
)
log = logging.getLogger("slidebot")

# Holatlar
LANG, COUNT, TOPIC, REVIEW, CHANGE_INPUT, IMAGE_SOURCE = range(6)


# ---------- Yordamchilar ----------
def lang_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang:uz"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:ru"),
    ]])


def count_keyboard():
    buttons, row = [], []
    for n in range(config.MIN_SLIDES, config.MAX_SLIDES + 1):
        row.append(InlineKeyboardButton(str(n), callback_data=f"count:{n}"))
        if len(row) == 5:
            buttons.append(row); row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)


def review_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(lang, "btn_change"), callback_data="rev:change")],
        [
            InlineKeyboardButton(t(lang, "btn_shorten"), callback_data="rev:shorten"),
            InlineKeyboardButton(t(lang, "btn_expand"), callback_data="rev:expand"),
        ],
    ])


def image_source_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(lang, "btn_ai_images"), callback_data="img:ai")],
        [InlineKeyboardButton(t(lang, "btn_web_images"), callback_data="img:web")],
    ])


def get_lang(context):
    return context.user_data.get("lang", "uz")


async def send_review(update_or_msg, context):
    """Joriy kontentni preview qilib, ko'rib chiqish tugmalari bilan yuboradi."""
    lang = get_lang(context)
    data = context.user_data["content"]
    preview = ai_content.build_preview(data)
    text = t(lang, "content_caption", n=len(data["slides"]), preview=preview)
    await update_or_msg.reply_text(
        text, reply_markup=review_keyboard(lang),
        parse_mode=constants.ParseMode.MARKDOWN,
    )


# ---------- Handlerlar ----------
WELCOME = (
    "🎨 *Slayd Master* — AI prezentatsiya generatori\n"
    "🎨 *Slayd Master* — генератор презентаций на ИИ\n\n"
    "Men siz bergan mavzuda 10–30 slaydli tayyor prezentatsiya yasab beraman.\n"
    "Я создам готовую презентацию из 10–30 слайдов по вашей теме.\n"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(WELCOME, parse_mode=constants.ParseMode.MARKDOWN)
    await update.message.reply_text(t("uz", "choose_lang"), reply_markup=lang_keyboard())
    return LANG


async def on_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split(":")[1]
    context.user_data["lang"] = lang
    await q.edit_message_text(t(lang, "lang_set"))
    await q.message.reply_text(
        t(lang, "ask_count", mn=config.MIN_SLIDES, mx=config.MAX_SLIDES),
        reply_markup=count_keyboard(),
    )
    return COUNT


async def on_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = get_lang(context)
    n = int(q.data.split(":")[1])
    context.user_data["count"] = n
    await q.edit_message_text(t(lang, "count_set", n=n))
    await q.message.reply_text(t(lang, "ask_topic"))
    return TOPIC


async def on_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    topic = update.message.text.strip()
    context.user_data["topic"] = topic
    await update.message.reply_text(t(lang, "generating_content", topic=topic))
    try:
        data = await asyncio.to_thread(
            ai_content.generate_content, topic, context.user_data["count"], lang
        )
        context.user_data["content"] = data
        await send_review(update.message, context)
        return REVIEW
    except Exception as e:
        log.exception("content gen failed")
        await update.message.reply_text(t(lang, "err_generic", e=e))
        return ConversationHandler.END


async def on_review_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """O'zgartirish / qisqartirish / ko'paytirish tugmalari."""
    q = update.callback_query
    await q.answer()
    lang = get_lang(context)
    action = q.data.split(":")[1]
    n = context.user_data["count"]
    data = context.user_data["content"]

    if action == "change":
        await q.message.reply_text(t(lang, "ask_change"))
        return CHANGE_INPUT

    try:
        if action == "shorten":
            await q.message.reply_text(t(lang, "shortening"))
            data = await asyncio.to_thread(ai_content.shorten_content, data, n, lang)
        elif action == "expand":
            await q.message.reply_text(t(lang, "expanding"))
            data = await asyncio.to_thread(ai_content.expand_content, data, n, lang)
        context.user_data["content"] = data
        await send_review(q.message, context)
        return REVIEW
    except Exception as e:
        log.exception("modify failed")
        await q.message.reply_text(t(lang, "err_generic", e=e))
        return REVIEW


async def on_change_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    instruction = update.message.text.strip()
    n = context.user_data["count"]
    data = context.user_data["content"]
    await update.message.reply_text(t(lang, "applying"))
    try:
        data = await asyncio.to_thread(
            ai_content.modify_content, data, instruction, n, lang
        )
        context.user_data["content"] = data
        await send_review(update.message, context)
        return REVIEW
    except Exception as e:
        log.exception("change failed")
        await update.message.reply_text(t(lang, "err_generic", e=e))
        return REVIEW


async def on_sticker_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stiker = tasdiq → rasm manbaini so'rash."""
    lang = get_lang(context)
    if config.CONFIRM_STICKER_ID:
        sticker = update.message.sticker
        if not sticker or sticker.file_unique_id != config.CONFIRM_STICKER_ID:
            # kerakli stiker emas — eslatma
            sid = sticker.file_unique_id if sticker else "?"
            await update.message.reply_text(
                t(lang, "confirm_sticker_hint") + f"\n(file_unique_id: {sid})"
            )
            return REVIEW
    await update.message.reply_text(
        t(lang, "ask_image_source"), reply_markup=image_source_keyboard(lang)
    )
    return IMAGE_SOURCE


async def on_image_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = get_lang(context)
    source = q.data.split(":")[1]  # ai | web
    topic = context.user_data["topic"]
    data = context.user_data["content"]

    await q.edit_message_text(
        t(lang, "building_ai" if source == "ai" else "building_web")
    )
    try:
        path = await asyncio.to_thread(
            pptx_builder.build_presentation, data, source, topic
        )
        await q.message.reply_text(t(lang, "done"))
        with open(path, "rb") as f:
            await q.message.reply_document(
                document=f,
                filename=f"{topic[:40]}.pptx",
                caption=t(lang, "doc_caption", topic=topic, n=len(data["slides"])),
            )
        await q.message.reply_text(t(lang, "restart_hint"))
    except Exception as e:
        log.exception("build failed")
        await q.message.reply_text(t(lang, "err_generic", e=e))
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(t(get_lang(context), "restart_hint"))
    return ConversationHandler.END


def build_app() -> Application:
    config.require("TELEGRAM_BOT_TOKEN", config.TELEGRAM_BOT_TOKEN)
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG: [CallbackQueryHandler(on_lang, pattern=r"^lang:")],
            COUNT: [CallbackQueryHandler(on_count, pattern=r"^count:")],
            TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, on_topic)],
            REVIEW: [
                MessageHandler(filters.Sticker.ALL, on_sticker_confirm),
                CallbackQueryHandler(on_review_action, pattern=r"^rev:"),
            ],
            CHANGE_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_change_text)
            ],
            IMAGE_SOURCE: [CallbackQueryHandler(on_image_source, pattern=r"^img:")],
        },
        fallbacks=[CommandHandler("start", start), CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    app.add_handler(conv)
    return app


class _Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Slayd Master is running")

    def log_message(self, *args):
        pass


def _keep_alive():
    port = int(os.getenv("PORT", "8000"))
    HTTPServer(("0.0.0.0", port), _Health).serve_forever()


def main():
    threading.Thread(target=_keep_alive, daemon=True).start()
    app = build_app()
    log.info("Bot ishga tushdi. Ctrl+C bilan to'xtating.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
