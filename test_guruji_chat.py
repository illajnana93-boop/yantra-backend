import asyncio
from services.gemini_service import get_guruji_response_gemini
from services.rag_service import rag_service
import os
from dotenv import load_dotenv

load_dotenv()

async def test_chat():
    print("=" * 60)
    print("Sri Shyam Yantra - Production Chat Test")
    print("=" * 60)
    
    # Initialize RAG first
    print("\n[Step 1] Initializing Search Index...")
    rag_service.load_local_knowledge()
    
    # User question
    query = "श्याम यंत्र को कहाँ रखना चाहिए?"
    
    print(f"\n[Step 2] Sending Question to Guruji: {query}")
    print("Please wait, checking for available spiritual channel (Gemini Models)...")
    
    try:
        response = await get_guruji_response_gemini(query)
        
        print("\n" + "-" * 40)
        print("GURUJI ANSWER:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
        print("\n✓ Chat Test Successful!")
        
    except Exception as e:
        print(f"\n✗ Test Failed Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())