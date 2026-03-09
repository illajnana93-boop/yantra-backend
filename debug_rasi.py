import asyncio
import httpx
import os
import json
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
        
        # Current time in Delhi (placeholder coordinates)
        params = {
            "datetime": "2026-03-09T22:30:00+05:30",
            "coordinates": "28.6139,77.2090",
            "ayanamsa": 1
        }
        
        r = await client.get(
            "https://api.prokerala.com/v2/astrology/panchang/advanced",
            headers={"Authorization": f"Bearer {token}"},
            params=params
        )
        data = r.json().get("data", {})
        
        print("Panchang Data Keys:", list(data.keys()))
        
        # Check specific locations for Rasi
        print("\nChecking common rasi locations:")
        print(f"rasi: {data.get('rasi')}")
        print(f"moon_sign: {data.get('moon_sign')}")
        print(f"day.moon_sign: {data.get('day', {}).get('moon_sign') if isinstance(data.get('day'), dict) else 'N/A'}")
        
        # Let's look at the first Nakshatra to see if it mentions Rasi
        naks = data.get('nakshatra', [])
        if naks:
            print(f"\nFirst Nakshatra sample: {json.dumps(naks[0], indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
