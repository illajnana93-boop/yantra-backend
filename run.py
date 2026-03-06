"""
Backend startup helper – loads .env then starts Uvicorn.
Run with: python run.py
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    print("🙏 Jai Shri Shyam – Starting Sri Shyam Yantra Backend...")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,   # hot-reload on file changes during development
        log_level="info",
    )
