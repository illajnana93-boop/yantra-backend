"""
Run this script to test Prokerala API credentials and see the exact response structure.
Usage: python test_prokerala.py
"""
import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.getenv("PROKERALA_CLIENT_ID")
CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET")

# Test birth data (Amalapuram, Andhra Pradesh)
LAT = 16.5777179
LON = 82.0032621
DOB = "2004-11-13"
TOB = "07:32"
DATETIME_STR = f"{DOB}T{TOB}:00+05:30"

async def main():
    print(f"CLIENT_ID     = {CLIENT_ID}")
    print(f"CLIENT_SECRET = {CLIENT_SECRET[:8] if CLIENT_SECRET else 'NOT SET'}...")
    print()

    # 1. Get token
    print("── Step 1: Getting Prokerala token ──────────────────────────────")
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://api.prokerala.com/token",
            data={
                "grant_type":    "client_credentials",
                "client_id":     CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            }
        )
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text[:400]}")
    
    if resp.status_code != 200:
        print("\n❌ Token failed. Check your CLIENT_ID and CLIENT_SECRET in .env")
        return
    
    token = resp.json()["access_token"]
    print(f"✅ Token obtained: {token[:30]}...\n")

    # 2. Call Kundli endpoint
    print("── Step 2: Calling /kundli endpoint ─────────────────────────────")
    params = {
        "datetime":    DATETIME_STR,
        "coordinates": f"{LAT},{LON}",
        "ayanamsa":    1,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            "https://api.prokerala.com/v2/astrology/kundli",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
        )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print("✅ Kundli Response (top-level keys):", list(data.keys()))
        if "data" in data:
            print("data keys:", list(data["data"].keys()) if isinstance(data["data"], dict) else type(data["data"]))
        print("\nFull response (truncated to 2000 chars):")
        print(json.dumps(data, indent=2)[:2000])
    else:
        print(f"❌ Kundli error: {resp.text}")

    # 3. Call Panchang endpoint
    print("\n── Step 3: Calling /panchang/advanced endpoint ───────────────────")
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            "https://api.prokerala.com/v2/astrology/panchang/advanced",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
        )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print("✅ Panchang Response (data keys):", list(data.get("data", {}).keys()))
    else:
        print(f"❌ Panchang error: {resp.text}")

asyncio.run(main())
