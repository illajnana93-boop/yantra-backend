from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    def generate_answer(self, question, context):
        system_prompt = (
            "You are Guruji guiding devotees of Sri Shyam Baba. "
            "IMPORTANT: The devotee might ask questions in English, Hinglish (Hindi in English letters), or Hindi. "
            "You MUST understand their intent, but your response MUST be STRICTLY in Devanagari Hindi script (हिंदी). "
            "Address the user as 'बेटा'. "
            "Maximum 2-3 short sentences. "
            "Calm spiritual guidance tone. "
            "Must end with 'जय श्री श्याम'."
        )
        
        prompt = f"""
{system_prompt}

Knowledge for context:
{context}

Devotee Question:
{question}

Guruji Answer (In Hindi):
"""
        try:
            # Attempt to use Gemini LLM
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"⚠️ Gemini API Error (Quota/Network): {e}")
            
            # Smart Fallback: Use the RAG context directly if LLM fails
            if context and len(context.strip()) > 10:
                # Split into sentences and pick the most relevant ones
                sentences = [s.strip() for s in context.split('।') if s.strip()]
                
                # Try to find sentences that best match the question keywords
                question_words = set(question.lower().split())
                scored = []
                for i, s in enumerate(sentences):
                    score = sum(1 for w in question_words if w in s.lower())
                    scored.append((score, i, s))
                
                # Sort by relevance, pick top 2
                scored.sort(key=lambda x: (-x[0], x[1]))
                top_sentences = [s for _, _, s in scored[:2] if s]
                
                if top_sentences:
                    fallback_text = "। ".join(top_sentences).strip()
                    if not fallback_text.endswith('।'):
                        fallback_text += '।'
                    return f"बेटा, {fallback_text}\n\nजय श्री श्याम।"
            
            # Universal Fallback
            return "बेटा, अभी ध्यान मुद्रा में लीन हूँ। अपनी श्रद्धा बनाए रखें। जय श्री श्याम।"

gemini_service = GeminiService()

async def get_guruji_response_gemini(user_message: str):
    """
    Compatibility wrapper for the new GeminiService.
    """
    from services.rag_service import rag_service
    context = rag_service.get_relevant_context(user_message, k=3)
    
    # Run the synchronous generate_answer in a thread pool to avoid blocking
    import asyncio
    from functools import partial
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, 
        partial(gemini_service.generate_answer, user_message, context)
    )