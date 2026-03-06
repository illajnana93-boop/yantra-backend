"""
Orders Route – POST /order · GET /orders (admin)
Stores COD orders in-memory (upgradeable to SQLite via the commented code).
"""

import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException

from models.order_model import OrderRequest, OrderResponse, StoredOrder

router = APIRouter(tags=["Orders"])

# ── In-memory Order Store ─────────────────────────────────────────────────────
# For production, replace with a SQLite / PostgreSQL database.
_orders: List[StoredOrder] = []

# Price lookup
PRICES = {"11g": "₹2,100", "33g": "₹6,000"}


@router.post("/order", response_model=OrderResponse, status_code=201)
async def place_order(request: OrderRequest):
    """
    Accept a Cash on Delivery order.
    Validates input using Pydantic, assigns an order ID, and stores the order.
    """
    # Basic phone validation
    if not request.phone.replace("+", "").replace(" ", "").replace("-", "").isdigit():
        raise HTTPException(status_code=422, detail="Invalid phone number.")

    order_id = f"SY-{uuid.uuid4().hex[:8].upper()}"
    price    = PRICES.get(request.variant, "N/A")
    now      = datetime.now().isoformat()

    stored = StoredOrder(
        order_id=order_id,
        name=request.name,
        phone=request.phone,
        address=request.address,
        variant=request.variant,
        price=price,
        created_at=now,
    )
    _orders.append(stored)

    return OrderResponse(
        message=(
            f"🙏 जय श्री श्याम! आपका ऑर्डर सफलतापूर्ण प्राप्त हुआ।\n"
            f"Order ID: {order_id} | {request.variant} Yantra – {price}\n"
            f"हमारी टीम जल्द ही {request.phone} पर संपर्क करेगी। 🙏"
        ),
        order_id=order_id,
        variant=request.variant,
        price=price,
        created_at=now,
    )


@router.get("/orders", response_model=List[StoredOrder], tags=["Admin"])
async def get_orders():
    """
    Return all stored orders (admin use only – add auth in production).
    """
    return _orders


# ── TTS Stub ──────────────────────────────────────────────────────────────────
@router.post("/tts", tags=["TTS"])
async def text_to_speech(payload: dict):
    """
    TTS structure stub – integrate with ElevenLabs / Google TTS in production.
    Returns a placeholder audio URL.
    """
    text = payload.get("text", "")
    return {
        "audio_url": f"/static/tts/{uuid.uuid4().hex}.mp3",
        "text":      text,
        "note":      "TTS integration pending. Add ElevenLabs or Google TTS API key.",
    }
