"""
OpenAI Service – Calls the OpenAI Chat Completions API with Guruji's system prompt.
Reads the API key from the OPENAI_API_KEY environment variable.
"""

import os
from openai import AsyncOpenAI

# ── System Prompt ────────────────────────────────────────────────────────────
GURUJI_SYSTEM_PROMPT = """
You are Guruji of Sri Shyam Yantra.
Speak calmly, spiritually and softly.
Answer in simple Hindi or Telugu mixed with devotion.
Keep tone blessing style.

If asked about the product, always mention:
  - 11 grams – ₹2100
  - 33 grams – ₹6000
  - Cash on Delivery only across all of India.

Do not discuss politics.
Do not answer unrelated technical questions.
Keep responses short, peaceful, and full of blessings.
Always end your response with a short blessing like "जय श्री श्याम 🙏" or "ॐ नमः शिवाय 🙏".
"""

# ── Client (lazy-initialized) ─────────────────────────────────────────────────
_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY environment variable is not set. "
                "Please add it to your .env file or system environment."
            )
        _client = AsyncOpenAI(api_key=api_key)
    return _client


async def get_guruji_response(user_message: str) -> str:
    """
    Send user_message to the OpenAI API with Guruji's system prompt
    and return the assistant reply text.
    """
    client = _get_client()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",           # affordable, fast model
        messages=[
            {"role": "system",  "content": GURUJI_SYSTEM_PROMPT.strip()},
            {"role": "user",    "content": user_message},
        ],
        max_tokens=300,
        temperature=0.8,
    )
    return response.choices[0].message.content or "🙏 जय श्री श्याम"
