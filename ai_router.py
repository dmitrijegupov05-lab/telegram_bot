import os
import httpx
from openai import AsyncOpenAI
from google import genai


class AIRouter:

    def __init__(self):

        self.openai = None
        self.deepseek = None
        self.gemini = None

        if os.getenv("OPENAI_API_KEY"):
            self.openai = AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )

        if os.getenv("DEEPSEEK_API_KEY"):
            self.deepseek = AsyncOpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com"
            )

        if os.getenv("GEMINI_API_KEY"):
            self.gemini = genai.Client(
                api_key=os.getenv("GEMINI_API_KEY")
            )

        self.ollama_url = os.getenv(
            "OLLAMA_URL",
            "http://127.0.0.1:11434"
        )

    async def ask(self, model, prompt):

        # GPT
        if model == "gpt":

            if not self.openai:
                return "❌ GPT API key не настроен."

            response = await self.openai.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-5"),
                input=prompt
            )

            return response.output_text

        # DeepSeek API
        if model == "deepseek":

            if not self.deepseek:
                return "❌ DeepSeek API key не настроен."

            response = await self.deepseek.chat.completions.create(
                model=os.getenv(
                    "DEEPSEEK_MODEL",
                    "deepseek-v4-flash"
                ),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.choices[0].message.content

        # Gemini
        if model == "gemini":

            if not self.gemini:
                return "❌ Gemini API key не настроен."

            response = await self.gemini.aio.models.generate_content(
                model=os.getenv(
                    "GEMINI_MODEL",
                    "gemini-3.6-flash"
                ),
                contents=prompt
            )

            return response.text

        # LOCAL MODELS
        local_models = {
            "qwen": "qwen3:8b",
            "gemma": "gemma3:4b",
            "deepseek_local": "deepseek-r1:8b",
            "mistral": "mistral-small3.1"
        }

        if model in local_models:

            return await self.ask_ollama(
                local_models[model],
                prompt
            )

        return "❌ Неизвестная модель."

    async def ask_ollama(self, model, prompt):

        try:

            async with httpx.AsyncClient(
                timeout=300
            ) as client:

                response = await client.post(
                    f"{self.ollama_url}/api/chat",

                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "stream": False
                    }
                )

                response.raise_for_status()

                data = response.json()

                return data["message"]["content"]

        except Exception as e:

            return f"❌ Ollama error: {e}"
