"""
Prints the EXACT structure of auspicious_period from Prokerala so we can fix the parser.
Run: python test_panchang.py
"""
import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.getenv("PROKERALA_CLIENT_ID")
CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET")

LAT = 16.5777179
LON = 82.0032621

async def main():
    # Get token
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post("https://api.prokerala.com/token", data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        })
    token = r.json()["access_token"]
    print("✅ Token OK\n")

    from datetime import datetime
    now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+05:30")
    params = {"datetime": now_str, "coordinates": f"{LAT},{LON}", "ayanamsa": 1}

    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.get(
            "https://api.prokerala.com/v2/astrology/panchang/advanced",
            headers={"Authorization": f"Bearer {token}"},
            params=params
        )
    
    data = r.json().get("data", {})
    
    print("=== AUSPICIOUS PERIOD (first item) ===")
    asp = data.get("auspicious_period", [])
    if asp:
        print(json.dumps(asp[0], indent=2))
        print(f"\nTotal: {len(asp)} items")
    
    print("\n=== INAUSPICIOUS PERIOD (first item) ===")
    inasp = data.get("inauspicious_period", [])
    if inasp:
        print(json.dumps(inasp[0], indent=2))
        print(f"\nTotal: {len(inasp)} items")

    print("\n=== SUNRISE / SUNSET raw values ===")
    print(f"sunrise: {data.get('sunrise')!r}")
    print(f"sunset:  {data.get('sunset')!r}")
    print(f"moonrise:{data.get('moonrise')!r}")
    print(f"moonset: {data.get('moonset')!r}")

asyncio.run(main())
