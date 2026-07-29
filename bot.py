import os
import httpx

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AI_URL = os.getenv("AI_URL")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Multi AI Bot\n\n"
        "Отправь мне сообщение."
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if not AI_URL:
        await update.message.reply_text(
            "AI-сервис пока не настроен."
        )
        return

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                AI_URL,
                json={
                    "message": text
                }
            )

            response.raise_for_status()
            data = response.json()

        answer = data.get(
            "response",
            "AI не вернул ответ."
        )

        await update.message.reply_text(
            answer[:4096]
        )

    except Exception as e:
        await update.message.reply_text(
            f"Ошибка AI: {e}"
        )


def main():
    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN не задан"
        )

    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
