from services.gemini_service import gemini_service
import os
from dotenv import load_dotenv

load_dotenv()

print(f"API KEY: {os.getenv('GOOGLE_API_KEY')[:10]}...")
try:
    res = gemini_service.generate_answer("जय श्री श्याम", "कुछ नहीं")
    print(f"RESPONSE: {res}")
except Exception as e:
    print(f"CRASH: {e}")
