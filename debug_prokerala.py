import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv('.env')

CLIENT_ID = os.getenv("PROKERALA_CLIENT_ID")
CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET")

async def test_prokerala():
    print(f"Testing with ID: {CLIENT_ID[:5]}...")
    
    async with httpx.AsyncClient() as client:
        # 1. Get Token
        resp = await client.post(
            "https://api.prokerala.com/token",
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            }
        )
        if resp.status_code != 200:
            print(f"Token failed: {resp.text}")
            return
        
        token = resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "datetime": "2026-03-10T17:20:00+05:30",
            "coordinates": "28.6139,77.2090", # Delhi
            "ayanamsa": 1
        }
        
        # 2. Test Advanced Panchang
        print("\nTesting Advanced Panchang...")
        r_adv = await client.get("https://api.prokerala.com/v2/astrology/panchang/advanced", headers=headers, params=params)
        print(f"Advanced Status: {r_adv.status_code}")
        if r_adv.status_code != 200:
            print(f"Advanced Error: {r_adv.text}")
            
        # 3. Test Standard Panchang
        print("\nTesting Standard Panchang...")
        r_std = await client.get("https://api.prokerala.com/v2/astrology/panchang", headers=headers, params=params)
        print(f"Standard Status: {r_std.status_code}")
        if r_std.status_code != 200:
            print(f"Standard Error: {r_std.text}")

        # 4. Test Kundli
        print("\nTesting Kundli...")
        r_kn = await client.get("https://api.prokerala.com/v2/astrology/kundli", headers=headers, params=params)
        print(f"Kundli Status: {r_kn.status_code}")

if __name__ == "__main__":
    asyncio.run(test_prokerala())
