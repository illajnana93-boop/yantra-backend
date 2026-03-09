from fastapi import APIRouter, HTTPException, Header
import httpx
import asyncio
import os
from datetime import datetime
from pydantic import BaseModel
from supabase import create_client, Client

router = APIRouter(tags=["Kundli"])

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# ── Prokerala ─────────────────────────────────────────────────────────────────
PROKERALA_CLIENT_ID     = os.getenv("PROKERALA_CLIENT_ID")
PROKERALA_CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET")

class KundliRequest(BaseModel):
    dob: str        # YYYY-MM-DD
    tob: str        # HH:mm
    pob: str        # Place name
    latitude: float
    longitude: float

async def get_prokerala_token() -> str:
    """Get OAuth token from Prokerala. Raises HTTPException on failure."""
    if not PROKERALA_CLIENT_ID or not PROKERALA_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="Prokerala credentials not configured on server.")
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.prokerala.com/token",
                data={
                    "grant_type":    "client_credentials",
                    "client_id":     PROKERALA_CLIENT_ID,
                    "client_secret": PROKERALA_CLIENT_SECRET,
                }
            )
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            if token:
                return token
        print(f"❌ Prokerala token error ({resp.status_code}): {resp.text}")
        raise HTTPException(status_code=503, detail=f"Prokerala token failed: {resp.text}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Prokerala connection failed: {str(e)}")

# ── POST /generate-kundli ──────────────────────────────────────────────────────
@router.post("/generate-kundli")
async def generate_kundli(req: KundliRequest, user_id: str = Header(...)):
    print(f"\n🔮 Generate Kundli for user={user_id}")
    print(f"   dob={req.dob}, tob={req.tob}, lat={req.latitude}, lon={req.longitude}")

    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured on server.")

    # 1. Return existing record if already generated
    try:
        existing = supabase.table("kundlis").select("*").eq("user_id", user_id).execute()
        if existing.data:
            print("✅ Returning cached Kundli from DB")
            return {"message": "Kundli already exists", "data": existing.data[0]["data"]}
    except Exception as e:
        print(f"❌ DB read error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # 2. Get Prokerala Token (strict – no fallback)
    token = await get_prokerala_token()

    # 3. Call both Prokerala endpoints in parallel
    datetime_str = f"{req.dob}T{req.tob}:00+05:30"
    params = {
        "datetime":    datetime_str,
        "coordinates": f"{req.latitude},{req.longitude}",
        "ayanamsa":    1,
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            headers = {"Authorization": f"Bearer {token}"}
            kundli_task   = client.get("https://api.prokerala.com/v2/astrology/kundli",             headers=headers, params=params)
            panchang_task = client.get("https://api.prokerala.com/v2/astrology/panchang/advanced",  headers=headers, params=params)
            kundli_res, panchang_res = await asyncio.gather(kundli_task, panchang_task)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Prokerala request failed: {str(e)}")

    # 4. Validate Kundli response (strict – no mock)
    if kundli_res.status_code != 200:
        print(f"❌ Prokerala Kundli {kundli_res.status_code}: {kundli_res.text}")
        raise HTTPException(
            status_code=503,
            detail=f"Prokerala Kundli API error ({kundli_res.status_code}). Please try again later."
        )

    kundli_raw  = kundli_res.json().get("data", {})
    panchang_raw = panchang_res.json().get("data", {}) if panchang_res.status_code == 200 else {}

    if panchang_res.status_code != 200:
        print(f"⚠️ Prokerala Panchang {panchang_res.status_code}: {panchang_res.text}")

    # 5. Extract meaningful fields from Prokerala response
    nakshatra_details = kundli_raw.get("nakshatra_details", {})
    final_data = {
        # Core identity
        "zodiac":     nakshatra_details.get("zodiac", {}).get("name", ""),        # e.g. "Scorpio"
        "moon_sign":  nakshatra_details.get("chandra_rasi", {}).get("name", ""),  # e.g. "Vrischika"
        "sun_sign":   nakshatra_details.get("soorya_rasi", {}).get("name", ""),   # e.g. "Tula"
        "nakshatra":  nakshatra_details.get("nakshatra", {}).get("name", ""),     # e.g. "Anuradha"
        "nakshatra_pada": nakshatra_details.get("nakshatra", {}).get("pada", ""),
        "nakshatra_lord": nakshatra_details.get("nakshatra", {}).get("lord", {}).get("name", ""),
        "additional_info": nakshatra_details.get("additional_info", {}),

        # Dosha and yoga
        "mangal_dosha": kundli_raw.get("mangal_dosha", {}),
        "yoga_details": kundli_raw.get("yoga_details", []),

        # Full Panchang for today
        "panchang": {
            "vaara":               panchang_raw.get("vaara", {}),
            "day":                 panchang_raw.get("day", {}),
            "nakshatra":           panchang_raw.get("nakshatra", []),
            "tithi":               panchang_raw.get("tithi", []),
            "karana":              panchang_raw.get("karana", []),
            "yoga":                panchang_raw.get("yoga", []),
            "sunrise":             panchang_raw.get("sunrise", ""),
            "sunset":              panchang_raw.get("sunset", ""),
            "moonrise":            panchang_raw.get("moonrise", ""),
            "moonset":             panchang_raw.get("moonset", ""),
            "auspicious_period":   panchang_raw.get("auspicious_period", []),
            "inauspicious_period": panchang_raw.get("inauspicious_period", []),
        },
    }

    print(f"✅ Zodiac: {final_data['zodiac']}, Nakshatra: {final_data['nakshatra']}")

    # 6. Save to Supabase — try full schema first, fallback to minimal
    full_row = {
        "user_id":   user_id,
        "dob":       req.dob,
        "tob":       req.tob,
        "pob":       req.pob,
        "latitude":  req.latitude,
        "longitude": req.longitude,
        "data":      final_data,
    }
    try:
        supabase.table("kundlis").insert(full_row).execute()
        print("✅ Saved to DB (full schema)")
    except Exception as e:
        err_str = str(e)
        print(f"⚠️  Full insert failed: {err_str}")
        # Fallback: only user_id + data (works if columns haven't been migrated yet)
        if "PGRST204" in err_str or "column" in err_str.lower():
            print("🔄 Retrying with minimal schema (user_id + data only)...")
            try:
                supabase.table("kundlis").insert({
                    "user_id": user_id,
                    "data": final_data,
                }).execute()
                print("✅ Saved to DB (minimal schema — run ALTER TABLE to add columns)")
            except Exception as e2:
                print(f"❌ Minimal insert also failed: {e2}")
                raise HTTPException(status_code=500, detail=f"Failed to save Kundli: {str(e2)}")
        else:
            raise HTTPException(status_code=500, detail=f"Failed to save Kundli: {err_str}")


    return {"message": "Kundli generated successfully", "data": final_data}


# ── GET /user-kundli ──────────────────────────────────────────────────────────
@router.get("/user-kundli")
async def get_user_kundli(user_id: str = Header(...)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured.")
    try:
        result = supabase.table("kundlis").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /today-panchang ───────────────────────────────────────────────────────
@router.get("/today-panchang")
async def get_today_panchang(lat: float, lon: float):
    token = await get_prokerala_token()
    now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+05:30")
    params = {"datetime": now_str, "coordinates": f"{lat},{lon}", "ayanamsa": 1}

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "https://api.prokerala.com/v2/astrology/panchang/advanced",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=503, detail="Panchang fetch failed")
    return resp.json().get("data", {})
