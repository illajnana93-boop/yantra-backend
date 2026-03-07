"""
Sri Shyam Yantra – FastAPI Backend
Entry point: starts the app with CORS, mounts chat and order routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.chat   import router as chat_router
from routes.orders import router as orders_router
from routes.avatar import router as avatar_router
from routes.guidance import router as guidance_router
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="Sri Shyam Yantra API",
    description="Backend for the Sri Shyam Yantra spiritual e-commerce platform.",
    version="1.0.0",
)

# ── Static Files ─────────────────────────────────────────────────────────────
# Mount static folder to serve generated videos and Guruji images
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow the Vite dev server and any production frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://yantra-voer.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(chat_router)
app.include_router(orders_router)
app.include_router(avatar_router)
app.include_router(guidance_router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "🙏 Jai Shri Shyam – Sri Shyam Yantra API is running."}
