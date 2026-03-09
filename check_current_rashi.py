import asyncio
import httpx
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("PROKERALA_CLIENT_ID")
CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET")

async def main():
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://api.prokerala.com/token",
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            }
        )
        token = resp.json()["access_token"]
        
        now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+05:30")
        params = {
            "datetime": now_str,
            "coordinates": "16.5777179,82.0032621",
            "ayanamsa": 1
        }
        
        # Calling kundli endpoint for CURRENT time to see current moon sign
        r = await client.get(
            "https://api.prokerala.com/v2/astrology/kundli",
            headers={"Authorization": f"Bearer {token}"},
            params=params
        )
        data = r.json().get("data", {})
        nakshatra_details = data.get("nakshatra_details", {})
        print(f"Current Moon Sign (Today Rashi): {nakshatra_details.get('chandra_rasi', {}).get('name')}")
        print(f"Current Zodiac (Sign): {nakshatra_details.get('zodiac', {}).get('name')}")

if __name__ == "__main__":
    asyncio.run(main())
