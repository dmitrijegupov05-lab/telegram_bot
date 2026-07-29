import os

from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from ai_router import AIRouter


load_dotenv()

TOKEN = os.getenv("8667062654:AAHQf2dWGYSqnUB7Zmv6qqa800iALj_AJl4")

router = AIRouter()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [

        [
            InlineKeyboardButton(
                "🧠 GPT",
                callback_data="gpt"
            )
        ],

        [
            InlineKeyboardButton(
                "🔵 DeepSeek",
                callback_data="deepseek"
            ),

            InlineKeyboardButton(
                "💎 Gemini",
                callback_data="gemini"
            )
        ],

        [
            InlineKeyboardButton(
                "🇨🇳 Qwen3",
                callback_data="qwen"
            ),

            InlineKeyboardButton(
                "💎 Gemma 3",
                callback_data="gemma"
            )
        ],

        [
            InlineKeyboardButton(
                "🧠 DeepSeek R1",
                callback_data="deepseek_local"
            )
        ],

        [
            InlineKeyboardButton(
                "🇫🇷 Mistral",
                callback_data="mistral"
            )
        ]
    ]

    context.user_data["model"] = "qwen"

    await update.message.reply_text(
        "🤖 Multi AI Bot\n\n"
        "Выбери модель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def select_model(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    model = query.data

    context.user_data["model"] = model

    names = {
        "gpt": "🧠 GPT",
        "deepseek": "🔵 DeepSeek",
        "gemini": "💎 Gemini",
        "qwen": "🇨🇳 Qwen3",
        "gemma": "💎 Gemma 3",
        "deepseek_local": "🧠 DeepSeek R1",
        "mistral": "🇫🇷 Mistral"
    }

    await query.edit_message_text(
        f"✅ Выбрано: {names[model]}\n\n"
        "Теперь отправь сообщение."
    )


async def message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    model = context.user_data.get(
        "model",
        "qwen"
    )

    text = update.message.text

    wait = await update.message.reply_text(
        "⏳ Думаю..."
    )

    answer = await router.ask(
        model,
        text
    )

    await wait.edit_text(
        answer[:4096]
    )


def main():

    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN не найден"
        )

    app = (
        Application
        .builder()
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
        CallbackQueryHandler(
            select_model
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message
        )
    )

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
