from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter(tags=["Spiritual Guidance"])

@router.get("/spiritual-guidance")
async def get_spiritual_guidance(sign: str):
    valid_signs = [
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
    ]
    sign_lower = sign.lower()
    if sign_lower not in valid_signs:
        raise HTTPException(status_code=400, detail="Invalid zodiac sign")
        
    url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={sign_lower}&day=today"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            json_resp = response.json()
            data = json_resp.get("data", {})
            
            # The new API only gives the horoscope text and date. 
            # We generate the lucky attributes deterministically so the UI cards still look authentic.
            import datetime
            import hashlib
            
            today_date = datetime.date.today()
            today_str = today_date.strftime("%Y-%m-%d")
            seed_str = f"{sign_lower}-{today_str}"
            hash_val = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
            
            colors = ["Gold", "Silver", "Crimson", "Navy Blue", "Emerald", "Saffron", "White", "Violet"]
            moods = ["Peaceful", "Radiant", "Grounded", "Inspired", "Serene", "Joyful", "Reflective", "Empowered"]
            times = ["06:00 AM - 08:00 AM", "10:00 AM - 12:00 PM", "02:00 PM - 04:00 PM", "06:00 PM - 08:00 PM"]
            
            # Standard Vedic Rahu Kaal mapping based on weekday (0 = Monday, 6 = Sunday)
            rahu_kaal_map = {
                0: "07:30 AM - 09:00 AM",
                1: "03:00 PM - 04:30 PM",
                2: "12:00 PM - 01:30 PM",
                3: "01:30 PM - 03:00 PM",
                4: "10:30 AM - 12:00 PM",
                5: "09:00 AM - 10:30 AM",
                6: "04:30 PM - 06:00 PM"
            }
            rahu_kaal_timing = rahu_kaal_map.get(today_date.weekday(), "Unknown")
            
            import re
            
            raw_description = data.get("horoscope", "The stars are quiet today.")
            # Keep only the first 2 sentences for a crisp, clear message
            sentences = re.split(r'(?<=[.!?]) +', raw_description.strip())
            crisp_description = " ".join(sentences[:2]) if sentences else raw_description

            return {
                "current_date": data.get("date", "Today"),
                "description": crisp_description,
                "lucky_number": str((hash_val % 9) + 1),
                "lucky_time": times[hash_val % len(times)],
                "color": colors[hash_val % len(colors)],
                "mood": moods[hash_val % len(moods)],
                "rahu_kaal": rahu_kaal_timing,
                "sign": sign.capitalize()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
