import asyncio
from services.rag_service import rag_service
from services.gemini_service import gemini_service
import os
from dotenv import load_dotenv

load_dotenv()

async def test_full_rag_fallback():
    question = "Shyam Yantra ke kya laabh hain?"
    print(f"❓ Question: {question}")
    
    # 1. Test RAG
    context = rag_service.get_relevant_context(question, k=2)
    print(f"📚 Context found ({len(context)} chars)")
    
    # 2. Test Gemini (Expected to fail and use context)
    try:
        res = gemini_service.generate_answer(question, context)
        print(f"🙏 Guruji Response:\n{res}")
    except Exception as e:
        print(f"❌ Crash: {e}")

if __name__ == "__main__":
    asyncio.run(test_full_rag_fallback())
