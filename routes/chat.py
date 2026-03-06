"""
Chat Route – POST /chat
Receives a user message and returns Guruji's AI response.
Falls back to a devotional message if OpenAI is unavailable.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.gemini_service import get_guruji_response_gemini

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User's question")


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Receive a user question and return Guruji's spiritual response using Gemini AI.
    If the API key is not configured, a fallback devotional message is returned.
    """
    try:
        reply = await get_guruji_response_gemini(request.message)
    except EnvironmentError as e:
        # API key not set – return a calm fallback
        reply = (
            "जय श्री श्याम 🙏\n\n"
            "गुरुजी अभी उपलब्ध नहीं हैं। कृपया सीधे संपर्क करें:\n"
            "📞 हमारी टीम से बात करने के लिए कॉल करें।\n\n"
            "ॐ नमः शिवाय 🙏"
        )
    except Exception:
        reply = (
            "क्षमा करें पुत्र 🙏\n"
            "अभी सर्वर से जुड़ नहीं पा रहे। थोड़ी देर बाद प्रयास करें।\n"
            "जय श्री श्याम 🙏"
        )
    return ChatResponse(reply=reply)
