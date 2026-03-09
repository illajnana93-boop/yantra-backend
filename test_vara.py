import asyncio, httpx, json, os
from dotenv import load_dotenv
load_dotenv()

async def main():
    async with httpx.AsyncClient() as c:
        r = await c.post('https://api.prokerala.com/token', data={'grant_type': 'client_credentials', 'client_id': os.getenv('PROKERALA_CLIENT_ID'), 'client_secret': os.getenv('PROKERALA_CLIENT_SECRET')})
        t = r.json()['access_token']
        from datetime import datetime
        r = await c.get('https://api.prokerala.com/v2/astrology/panchang/advanced', headers={'Authorization': f'Bearer {t}'}, params={'ayanamsa': 1, 'coordinates': '16.57,82.00', 'datetime': datetime.now().isoformat()})
        data = r.json().get('data', {})
        print("KEYS:", data.keys())
        for k in data.keys():
            if 'var' in k.lower() or 'day' in k.lower() or 'week' in k.lower():
                print(f"{k}: {data[k]}")

asyncio.run(main())
