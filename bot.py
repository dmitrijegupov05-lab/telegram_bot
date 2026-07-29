import os

from openai import AsyncOpenAI

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


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")


if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN не задан")

if not GROQ_KEY:
    raise RuntimeError("GROQ_API_KEY не задан")


client = AsyncOpenAI(
    api_key=GROQ_KEY,
    base_url="https://api.groq.com/openai/v1"
)


MODELS = {
    "gpt20": {
        "name": "⚡ GPT-OSS 20B",
        "id": "openai/gpt-oss-20b"
    },

    "gpt120": {
        "name": "🧠 GPT-OSS 120B",
        "id": "openai/gpt-oss-120b"
    },

    "qwen": {
        "name": "🇨🇳 Qwen3.6 27B",
        "id": "qwen/qwen3.6-27b"
    }
}


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [
        [
            InlineKeyboardButton(
                "⚡ GPT-OSS 20B",
                callback_data="model:gpt20"
            )
        ],

        [
            InlineKeyboardButton(
                "🧠 GPT-OSS 120B",
                callback_data="model:gpt120"
            )
        ],

        [
            InlineKeyboardButton(
                "🇨🇳 Qwen3.6 27B",
                callback_data="model:qwen"
            )
        ]
    ]

    context.user_data["model"] = "gpt20"

    await update.message.reply_text(
        "🤖 MULTI AI BOT\n\n"
        "Выбери модель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def choose_model(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    model_key = query.data.split(":")[1]

    context.user_data["model"] = model_key

    model = MODELS[model_key]

    await query.edit_message_text(
        f"✅ Выбрано:\n\n"
        f"{model['name']}\n\n"
        "Теперь отправь сообщение."
    )


async def chat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    model_key = context.user_data.get(
        "model",
        "gpt20"
    )

    model = MODELS[model_key]

    wait = await update.message.reply_text(
        "⏳ Думаю..."
    )

    try:

        response = await client.chat.completions.create(

            model=model["id"],

            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты полезный AI-ассистент "
                        "в Telegram. "
                        "Отвечай на языке пользователя."
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ],

            temperature=0.7,

            max_tokens=2048
        )

        answer = response.choices[0].message.content

        await wait.delete()

        # Telegram ограничивает одно сообщение
        # примерно 4096 символами.

        for i in range(
            0,
            len(answer),
            4000
        ):

            await update.message.reply_text(
                answer[i:i + 4000]
            )

    except Exception as e:

        await wait.edit_text(
            "❌ Ошибка AI:\n\n"
            f"{str(e)[:1500]}"
        )


def main():

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
            choose_model,
            pattern=r"^model:"
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
