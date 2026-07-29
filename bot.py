import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🤖 Multi AI Bot запущен!\n\n"
        "Напиши мне сообщение."
    )


async def chat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text

    await update.message.reply_text(
        f"Ты написал:\n\n{text}\n\n"
        "✅ Telegram-бот работает."
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
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    port = int(
        os.environ.get(
            "PORT",
            "10000"
        )
    )

    hostname = os.environ.get(
        "RENDER_EXTERNAL_HOSTNAME"
    )

    if not hostname:
        raise RuntimeError(
            "RENDER_EXTERNAL_HOSTNAME не найден"
        )

    webhook_url = (
        f"https://{hostname}/telegram"
    )

    print(
        f"Starting webhook: {webhook_url}"
    )

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="telegram",
        webhook_url=webhook_url
    )


if __name__ == "__main__":
    main()
