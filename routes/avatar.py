from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
import os
import uuid
import edge_tts
from datetime import datetime, timedelta
from services.gemini_service import get_guruji_response_gemini
from services.voice_service import voice_service

import traceback

router = APIRouter(tags=["Avatar"])

class TalkRequest(BaseModel):
    message: str

class TalkResponse(BaseModel):
    reply: str
    audio_url: str

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static", "audio")

# Ensure directory exists
os.makedirs(STATIC_DIR, exist_ok=True)

# Helper to clean old audio files
def clean_old_audio():
    if not os.path.exists(STATIC_DIR):
        return
    now = datetime.now()
    for filename in os.listdir(STATIC_DIR):
        if filename.startswith("guruji_voice_") and filename.endswith(".mp3"):
            file_path = os.path.join(STATIC_DIR, filename)
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if now - file_time > timedelta(hours=1):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error checking/deleting file {filename}: {e}")

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer_text: str
    audio_url: str
    avatar: str

@router.post("/ask-guruji", response_model=AskResponse)
async def ask_guruji(request: AskRequest, background_tasks: BackgroundTasks, req: Request):
    """
    RAG-based conversational endpoint for the Guruji Avatar.
    Returns synthesized text and audio URL.
    """
    background_tasks.add_task(clean_old_audio)
    
    try:
        # Step 1: Get Guruji's Spiritual Response (RAG + Gemini)
        print(f"--- GURUJI IS THINKING: {request.question} ---")
        answer_text = await get_guruji_response_gemini(request.question)
        
        # Step 2: Synthesis
        session_id = str(uuid.uuid4())[:12]
        audio_filename = f"guruji_response_{session_id}.wav"
        audio_path = os.path.join(STATIC_DIR, audio_filename)
        
        # Fast track: use edge-tts directly (instantaneous)
        print(f"🎙️ Generating fast voice for: {answer_text[:50]}...")
        audio_filename = f"guruji_response_{session_id}.mp3"
        audio_path = os.path.join(STATIC_DIR, audio_filename)
        
        communicate = edge_tts.Communicate(answer_text, "hi-IN-MadhurNeural")
        await communicate.save(audio_path)
        print(f"✅ Fast audio saved: {audio_filename}")
        
        print(f"🚀 Returning response to client")

        full_audio_url = str(req.base_url) + f"static/audio/{audio_filename}"
        return AskResponse(
            answer_text=answer_text,
            audio_url=full_audio_url,
            avatar="guruji"
        )

    except Exception as e:
        print(f"ERROR IN ASK-GURUJI:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Guruji is currently in deep meditation: {str(e)}")

@router.post("/talk-to-guruji", response_model=TalkResponse)
async def talk_to_guruji(request: TalkRequest, background_tasks: BackgroundTasks, req: Request):
    """ Endpoint for chat responses with Guruji's cloned voice. """
    background_tasks.add_task(clean_old_audio)
    try:
        reply = await get_guruji_response_gemini(request.message)
        session_id = str(uuid.uuid4())[:8]
        audio_filename = f"guruji_response_{session_id}.wav"
        audio_path = os.path.join(STATIC_DIR, audio_filename)

        print(f"🎙️ [talk-to-guruji] Generating fast voice for: {reply[:50]}...")
        audio_filename = f"guruji_response_{session_id}.mp3"
        audio_path = os.path.join(STATIC_DIR, audio_filename)
        
        communicate = edge_tts.Communicate(reply, "hi-IN-MadhurNeural")
        await communicate.save(audio_path)
        print(f"✅ [talk-to-guruji] Fast audio saved: {audio_filename}")
        
        full_audio_url = str(req.base_url) + f"static/audio/{audio_filename}"
        return TalkResponse(reply=reply, audio_url=full_audio_url)
    except Exception as e:
        print(f"ERROR in talk-to-guruji: {e}")
        raise HTTPException(status_code=500, detail=str(e))
