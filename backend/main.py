from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import httpx

from config import PORT, HOST, get_gemini_api_key, set_gemini_api_key
from services.weather_service import get_farm_weather
from services.disease_service import diagnose_crop_disease
from services.ai_agent_service import generate_ai_response, CROP_AGRONOMY_DATA, SOIL_KNOWLEDGE, IRRIGATION_KNOWLEDGE
from services.satellite_service import get_satellite_crop_insights
from services.crop_doctor_service import analyze_crop_multi_images
from services.field_analysis_service import analyze_field_health
from services.regenerative_service import get_regenerative_advisory
from services.voice_service import process_voice_query
import database

app = FastAPI(
    title="KrishiSetu AI Backend API",
    description=(
        "Comprehensive agricultural AI intelligence — live weather, "
        "ERA5-Land soil-moisture field indices, leaf disease diagnosis, "
        "Crop Doctor multi-image analysis, regenerative farming advisory, "
        "and Google Gemini-powered agronomy chat."
    ),
    version="2.0.0",
)

# Enable CORS for frontend Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────────────────────────
# Pydantic Request Models
# ──────────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str
    farm_data: Optional[Dict[str, Any]] = None
    history: Optional[List[Dict[str, str]]] = None
    analysis_context: Optional[Dict[str, Any]] = None
    language: Optional[str] = "en"

class GeminiKeyRequest(BaseModel):
    api_key: str

class AdvisoryRequest(BaseModel):
    crop: str
    soil: str
    area: Optional[float] = 1.0
    irrigation: Optional[str] = "Tube Well"

class RegenerativeRequest(BaseModel):
    crop: str
    soil: str
    location: Optional[str] = "India"
    area: Optional[float] = 2.0
    irrigation: Optional[str] = "Canal"
    weather_summary: Optional[str] = None
    language: Optional[str] = "en"

class VoiceRequest(BaseModel):
    query: str
    language: Optional[str] = "auto"
    farm_data: Optional[Dict[str, Any]] = None
    field_context: Optional[Dict[str, Any]] = None
    conversation_history: Optional[List[Dict[str, str]]] = None

# ──────────────────────────────────────────────────────────────────────────────
# Health / Status
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "status": "online",
        "app": "KrishiSetu AI Agricultural Intelligence Engine",
        "version": "2.0.0",
    }

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "KrishiSetu AI"}

@app.get("/api/ai/status")
def get_ai_status():
    """Check whether Gemini Generative AI is active or the Expert System is running."""
    api_key = get_gemini_api_key()
    has_key = bool(api_key and len(api_key) > 5)
    masked  = (f"{api_key[:4]}...{api_key[-4:]}" if has_key and len(api_key) > 8
               else ("Configured" if has_key else None))
    return {
        "gemini_configured": has_key,
        "engine": "Gemini 1.5/2.0 Flash (Live AI)" if has_key else "KrishiSetu Expert Engine (Offline Heuristics)",
        "key_preview": masked,
    }

# ──────────────────────────────────────────────────────────────────────────────
# Gemini Key Management
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/api/settings/gemini-key")
async def update_gemini_key(req: GeminiKeyRequest):
    """Save and verify a Gemini API Key dynamically."""
    new_key = (req.api_key or "").strip()
    if not new_key:
        set_gemini_api_key("")
        return {
            "status": "cleared",
            "gemini_configured": False,
            "message": "Gemini API Key removed. KrishiSetu is now using the built-in Expert Agronomy Engine.",
        }

    models_to_test = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    verified, last_err = False, ""

    async with httpx.AsyncClient(timeout=12.0) as client:
        for model in models_to_test:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={new_key}"
            try:
                resp = await client.post(url, json={
                    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}],
                    "generationConfig": {"maxOutputTokens": 5},
                })
                if resp.status_code == 200:
                    verified = True
                    break
                else:
                    try:
                        last_err = resp.json().get("error", {}).get("message", f"HTTP {resp.status_code}")
                    except Exception:
                        last_err = f"HTTP {resp.status_code}: {resp.text[:100]}"
            except Exception as exc:
                last_err = str(exc)

    if not verified:
        raise HTTPException(
            status_code=400,
            detail=f"Gemini API verification failed. {last_err or 'Please verify your API key and network connection.'}",
        )

    set_gemini_api_key(new_key)
    return {
        "status": "success",
        "gemini_configured": True,
        "message": "Gemini API Key verified and saved successfully! Generative AI is now active.",
    }

# ──────────────────────────────────────────────────────────────────────────────
# Weather
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/api/weather")
async def fetch_weather(location: str = "Haldia, West Bengal"):
    """Fetch live weather metrics and 7-day agricultural forecast."""
    return await get_farm_weather(location)

# ──────────────────────────────────────────────────────────────────────────────
# AI Chat
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/api/ai/chat")
async def chat_with_agronomist(req: ChatRequest):
    """Chat with the KrishiSetu AI Farm Advisor, optionally grounded in recent analysis."""
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        context = req.analysis_context
        if not context:
            q_lower = req.query.lower()
            wants_report = any(w in q_lower for w in [
                "my report", "my scan", "previous scan", "last diagnosis",
                "doctor report", "field check report", "recent scan", "latest check", "last test",
            ])
            if wants_report:
                try:
                    latest = database.get_latest_analysis()
                    if latest:
                        context = latest
                except Exception as db_err:
                    print(f"[KrishiSetu AI] db latest analysis error: {db_err}")

        reply = await generate_ai_response(
            query=req.query,
            farm_data=req.farm_data,
            history=req.history,
            analysis_context=context,
            language=req.language or "en",
        )
        return {"response": reply}
    except Exception as exc:
        print(f"[KrishiSetu AI] Chat endpoint error: {exc}")
        # Safe agronomic fallback response
        crop = (req.farm_data or {}).get("crop", "crop")
        return {
            "response": (
                f"### 🌾 KrishiSetu AI Farm Advisory\n\n"
                f"Regarding your query on **{crop}**:\n\n"
                f"- **Scouting & Observation**: Inspect your field's leaves and root zones early morning for any signs of stress.\n"
                f"- **Balanced Care**: Ensure proper soil drainage and maintain balanced NPK ratios.\n"
                f"- **Instant Plant Diagnosis**: You can use the **Crop Doctor** or **Check Crop** tool on your dashboard to upload a photo for an immediate visual diagnosis!"
            )
        }

# ──────────────────────────────────────────────────────────────────────────────
# KrishiSetu Voice — Regional Voice Assistant
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/api/voice/process")
async def handle_voice_query(req: VoiceRequest):
    """
    KrishiSetu Voice:
    Processes farmer spoken query in regional languages (Bengali, Hindi, English),
    incorporates live farm, weather, soil moisture, and remote sensing data,
    and returns localized speech text + base64 spoken MP3 audio.
    """
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Voice query cannot be empty.")
    
    # Ground in latest doctor analysis if not provided explicitly
    field_ctx = req.field_context or {}
    if "primary_issue" not in field_ctx:
        try:
            latest = database.get_latest_analysis()
            if latest:
                field_ctx["primary_issue"] = latest.get("primary_issue")
                field_ctx["latest_diagnosis"] = latest.get("primary_issue")
        except Exception:
            pass

    try:
        result = await process_voice_query(
            query=req.query,
            requested_language=req.language or "auto",
            farm_data=req.farm_data,
            field_context=field_ctx,
            conversation_history=req.conversation_history
        )
        return result
    except Exception as exc:
        print(f"[KrishiSetu Voice Endpoint Error]: {exc}")
        return {
            "query": req.query,
            "language": req.language or "en",
            "language_name": "English",
            "response_text": "Please check your field surface moisture and inspect for early pest symptoms. Consult your local agricultural officer for specific advice.",
            "clean_speech_text": "Please check your field surface moisture and inspect for early pest symptoms.",
            "audio_base64": None,
            "has_audio": False,
            "context_applied": {}
        }
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/api/disease/detect")
async def detect_leaf_disease(
    image: UploadFile = File(...),
    crop: Optional[str] = Form(None),
):
    """Analyze single crop leaf image for disease diagnosis and remedies."""
    try:
        contents = await image.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        return await diagnose_crop_disease(contents, crop_hint=crop)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Image processing error: {str(exc)}")

# ──────────────────────────────────────────────────────────────────────────────
# AI Crop & Field Doctor
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/api/doctor/analyze-crop")
async def doctor_analyze_crop(
    images: List[UploadFile] = File(...),
    crop: Optional[str] = Form(None),
    field_context: Optional[str] = Form(None),
):
    """
    Multi-image crop health & pathology analysis:
    - Analyses 1–5 photos (leaf, leaf back, stem, fruit, whole plant)
    - Validates image quality (blur, lighting, framing)
    - Returns comprehensive diagnosis, causes, remedies, and confidence
    - Saves report to SQLite database
    """
    try:
        images_bytes = [b for f in images if len(b := await f.read()) > 0]
        if not images_bytes:
            raise HTTPException(status_code=400, detail="No valid images uploaded.")

        parsed_context = None
        if field_context:
            try:
                parsed_context = json.loads(field_context)
            except Exception:
                parsed_context = None

        result = await analyze_crop_multi_images(
            images_bytes=images_bytes,
            crop_hint=crop,
            field_context=parsed_context,
        )

        if result.get("quality_passed", True):
            record_id = database.save_analysis_record({
                "analysis_type":    "crop",
                "crop_name":        result.get("crop_name", crop or "Crop"),
                "variety":          result.get("variety", ""),
                "growth_stage":     result.get("growth_stage", ""),
                "overall_health":   result.get("overall_health_status", "Healthy"),
                "health_score":     result.get("overall_health_score", 80),
                "health_confidence": result.get("health_confidence", "MEDIUM"),
                "primary_issue":    result.get("primary_issue", "None"),
                "severity":         result.get("severity", "Low"),
                "issue_confidence": result.get("issue_confidence", 85),
                "symptoms":         result.get("symptoms", []),
                "causes":           result.get("possible_causes", []),
                "recommendations":  result.get("recommended_actions", []),
                "soil_condition":   parsed_context.get("soil", {}) if parsed_context else {},
                "image_count":      len(images_bytes),
                "quality_passed":   True,
                "quality_notes":    f"Quality score: {result.get('quality_score', 85)}%",
            })
            result["saved_report_id"] = record_id

        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Crop Doctor processing error: {str(exc)}")


@app.post("/api/doctor/analyze-field")
async def doctor_analyze_field(
    image:         Optional[UploadFile] = File(None),
    gps_lat:       Optional[float]  = Form(None),
    gps_lon:       Optional[float]  = Form(None),
    location_name: Optional[str]    = Form(None),
    crop:          Optional[str]    = Form("Rice"),
    area:          Optional[float]  = Form(2.0),
    soil_type:     Optional[str]    = Form("Alluvial Soil"),
):
    """
    Field and land condition analysis with live weather and ERA5-Land data.
    """
    try:
        img_bytes = None
        if image:
            img_bytes = await image.read()

        result = await analyze_field_health(
            image_bytes=img_bytes,
            gps_lat=gps_lat,
            gps_lon=gps_lon,
            location_name=location_name,
            crop=crop,
            area=area,
            soil_type=soil_type,
        )

        record_id = database.save_analysis_record({
            "analysis_type":    "field",
            "crop_name":        crop,
            "overall_health":   result.get("overall_field_status", "Normal"),
            "health_score":     result.get("field_health_score", 80),
            "health_confidence": result.get("confidence_level", "HIGH"),
            "primary_issue":    result.get("overall_field_status", "None"),
            "severity":         "Moderate" if result.get("field_health_score", 80) < 75 else "Low",
            "issue_confidence": 85,
            "symptoms":         result.get("risk_factors", []),
            "causes":           [],
            "recommendations":  result.get("recommended_actions", []),
            "soil_condition":   result.get("visual_field_estimations", {}),
            "weather_context":  result.get("weather_summary", {}),
            "satellite_context": result.get("satellite_summary", {}),
            "field_name":       result.get("field_name", "My Field"),
            "gps_lat":          gps_lat,
            "gps_lon":          gps_lon,
            "image_count":      1 if img_bytes else 0,
            "quality_passed":   result.get("quality_passed", True),
            "quality_notes":    f"Quality score: {result.get('quality_score', 85)}%",
        })
        result["saved_report_id"] = record_id
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Field Doctor processing error: {str(exc)}")


@app.get("/api/doctor/history")
def get_doctor_history(limit: int = 25):
    return {"history": database.get_recent_analyses(limit=limit)}


@app.post("/api/doctor/history/sync")
def sync_offline_history(records: List[Dict[str, Any]]):
    synced_ids = []
    for rec in records:
        try:
            if isinstance(rec.get("id"), int) and rec.get("id") > 0:
                continue
            synced_ids.append(database.save_analysis_record(rec))
        except Exception as exc:
            print(f"Error syncing offline record: {exc}")
    return {"status": "ok", "synced_count": len(synced_ids), "synced_ids": synced_ids}


@app.delete("/api/doctor/history/{record_id}")
def delete_doctor_record(record_id: int):
    return {"success": database.delete_analysis_record(record_id), "id": record_id}


@app.delete("/api/doctor/history")
def clear_all_doctor_records():
    database.clear_all_analyses()
    return {"success": True, "message": "All diagnostic records cleared."}


@app.get("/api/doctor/latest")
def get_latest_doctor_report():
    return {"latest": database.get_latest_analysis()}

# ──────────────────────────────────────────────────────────────────────────────
# Satellite / Field Intelligence  (now async → real ERA5-Land data)
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/api/satellite")
async def fetch_satellite_data(
    location: Optional[str]   = None,
    crop:     Optional[str]   = None,
    area:     Optional[float] = None,
):
    """
    Retrieve ERA5-Land soil-moisture field health indices.
    Returns a Vegetation Moisture Index (VMI) derived from real
    Open-Meteo reanalysis data — clearly labelled as a meteorological
    proxy, not a true satellite NDVI image.
    """
    return await get_satellite_crop_insights(location, crop, area)

# ──────────────────────────────────────────────────────────────────────────────
# Crop Advisory  (now crop-specific using CROP_AGRONOMY_DATA)
# ──────────────────────────────────────────────────────────────────────────────

# Crop-specific growth calendars (complete, non-generic)
CROP_GROWTH_CALENDARS: Dict[str, List[Dict]] = {
    "Rice": [
        {"stage": "1. Nursery & Sowing (Days 1–20)",
         "duration": "Days 1–20",
         "key_actions": [
             "Seed treatment: soak seeds in Carbendazim (2 g/kg) or Trichoderma viride (5 g/kg) for 24 h.",
             "Raise nursery on puddled beds; seed rate 12–15 kg/acre (transplanted) or 6 kg/acre (SRI).",
             "Apply 50% N + 100% P + 50% K as basal fertiliser at transplanting.",
         ]},
        {"stage": "2. Vegetative & Active Tillering (Days 21–45)",
         "duration": "Days 21–45",
         "key_actions": [
             "1st Nitrogen top-dress (33% Urea) at active tillering — 20–25 DAT.",
             "Maintain 2–3 cm shallow water layer; do not let field dry out.",
             "Scout for brown planthopper (BPH) near the base and leaf-folder larvae.",
         ]},
        {"stage": "3. Panicle Initiation & Flowering (Days 46–80)",
         "duration": "Days 46–80",
         "key_actions": [
             "2nd Nitrogen top-dress (33% Urea) + remaining Potash at panicle initiation.",
             "Maintain 5 cm water during flowering — CRITICAL: water stress causes empty grains.",
             "Spray preventive bio-fungicide (Pseudomonas/Trichoderma) if humidity > 80%.",
         ]},
        {"stage": "4. Grain Filling & Harvest (Days 81–120)",
         "duration": "Days 81–120",
         "key_actions": [
             "Withdraw irrigation 10–12 days before harvest to allow soil to consolidate.",
             "Harvest when 85% of panicles show straw-golden colour; grain moisture 20–22%.",
             "Sun-dry grain to < 14% moisture before storage; treat bags with Neem leaves.",
         ]},
    ],
    "Wheat": [
        {"stage": "1. Sowing & Germination (Days 1–21)",
         "duration": "Days 1–21",
         "key_actions": [
             "Sow Nov 1–20 at 40–45 kg/acre in rows 20–22 cm apart, depth 4–5 cm.",
             "Basal fertiliser: 100% P + 100% K + 33% N at sowing.",
             "Seed treatment: Carboxin + Thiram (Vitavax Power) @ 2.5 g/kg seed.",
         ]},
        {"stage": "2. CRI & Tillering (Days 22–50)",
         "duration": "Days 22–50",
         "key_actions": [
             "1st irrigation at Crown Root Initiation (CRI) — 21 DAS — MOST CRITICAL.",
             "Apply 33% Nitrogen (Urea) after 1st irrigation.",
             "Monitor for yellow rust (linear yellow pustules on leaves) and aphids.",
         ]},
        {"stage": "3. Jointing & Flowering (Days 51–85)",
         "duration": "Days 51–85",
         "key_actions": [
             "2nd irrigation at jointing (45–50 DAS); 3rd at late jointing (65 DAS).",
             "Apply remaining 33% Nitrogen at jointing stage.",
             "Spray Propiconazole 25% EC @ 1 ml/L at first rust sign.",
         ]},
        {"stage": "4. Grain Fill & Maturity (Days 86–120)",
         "duration": "Days 86–120",
         "key_actions": [
             "4th irrigation at milking stage (85 DAS) and 5th at dough stage (100 DAS).",
             "Harvest when leaves are golden and grain moisture is 14–18%.",
             "Thrash and sun-dry immediately to 12% moisture for safe storage.",
         ]},
    ],
    "Maize": [
        {"stage": "1. Sowing & Emergence (Days 1–15)",
         "duration": "Days 1–15",
         "key_actions": [
             "Kharif: June–July; Rabi: Oct–Nov. Seed rate: 8–10 kg/acre hybrids.",
             "Basal: 33% N + 100% P + 100% K at sowing; row spacing 60 cm × 20 cm.",
             "Seed treat with Thiram + Carbendazim @ 3 g/kg; sow on ridges to prevent waterlogging.",
         ]},
        {"stage": "2. Vegetative (Knee-High) Stage (Days 16–45)",
         "duration": "Days 16–45",
         "key_actions": [
             "1st Nitrogen top-dress (33% Urea) at knee-high stage (30–35 DAS).",
             "Check whorls for Fall Armyworm (pinholes + frass) — spray Chlorantraniliprole @ 0.4 ml/L.",
             "First earthing-up to strengthen root anchorage.",
         ]},
        {"stage": "3. Tasselling & Silking (Days 46–70)",
         "duration": "Days 46–70",
         "key_actions": [
             "2nd Nitrogen top-dress (33% Urea) at tasselling.",
             "Ensure uninterrupted irrigation — water stress now causes kernel abortion.",
             "Do NOT spray insecticides during silk emergence (disrupts pollination).",
         ]},
        {"stage": "4. Grain Filling & Harvest (Days 71–100)",
         "duration": "Days 71–100",
         "key_actions": [
             "Harvest at black-layer formation (physiological maturity) — grain moisture 28–32%.",
             "Dry grain artificially or on tarpaulin to 12–14% before shelling.",
             "Store maize with 1 kg Neem leaves per 100 kg grain to deter weevils.",
         ]},
    ],
    "Potato": [
        {"stage": "1. Planting & Emergence (Days 1–25)",
         "duration": "Days 1–25",
         "key_actions": [
             "Plant certified seed tubers (30–50 g) in Oct–Nov in furrows 30–45 cm apart.",
             "Treat tubers with Mancozeb (2.5 g/L) or Boric Acid (3%) for 30 min before planting.",
             "Apply full P + K + 50% N as basal fertiliser at planting.",
         ]},
        {"stage": "2. Vegetative Growth & Earthing Up (Days 26–55)",
         "duration": "Days 26–55",
         "key_actions": [
             "Earthing-up at 30–35 days to prevent tuber greening and exposure.",
             "Apply remaining 50% Nitrogen top-dress at earthing-up.",
             "Monitor for Late Blight (dark water-soaked lesions): spray Mancozeb 75% WP @ 2.5 g/L.",
         ]},
        {"stage": "3. Tuber Bulking (Days 56–90)",
         "duration": "Days 56–90",
         "key_actions": [
             "Maintain consistent furrow irrigation — alternating wet-dry stresses cause hollow hearts.",
             "Foliar spray of Potassium Nitrate (13:0:45 @ 10 g/L) at 55 and 70 DAS increases tuber size.",
             "If early blight (target-board rings) appears, spray Chlorothalonil @ 2 g/L.",
         ]},
        {"stage": "4. De-haulming & Harvest (Days 91–120)",
         "duration": "Days 91–120",
         "key_actions": [
             "De-haulm (cut foliage) 10–14 days before harvest to harden skin.",
             "Stop irrigation 10 days before digging.",
             "Harvest in cool hours; cure tubers in dark at 12–14°C to seal skin.",
         ]},
    ],
    "Cotton": [
        {"stage": "1. Sowing & Seedling (Days 1–30)",
         "duration": "Days 1–30",
         "key_actions": [
             "Sow April–May; spacing 90 × 60 cm for hybrids.",
             "Basal: 33% N + 100% P + 100% K. Apply Zinc Sulfate @ 10 kg/acre if deficient.",
             "Install pink bollworm pheromone traps (5/acre) from day 1.",
         ]},
        {"stage": "2. Square Formation & Vegetative (Days 31–70)",
         "duration": "Days 31–70",
         "key_actions": [
             "2nd N top-dress at square (bud) formation — 45 DAS.",
             "Scout twice a week for jassids, thrips, and whitefly. Spray Neem oil @ 2.5 ml/L.",
             "Foliar spray Magnesium Sulfate (1%) + Boron (0.2%) to prevent leaf reddening.",
         ]},
        {"stage": "3. Flowering & Boll Development (Days 71–120)",
         "duration": "Days 71–120",
         "key_actions": [
             "3rd N top-dress at peak boll development.",
             "Avoid water stress during flowering — causes square/boll shedding.",
             "Spray Emamectin Benzoate @ 0.5 g/L for bollworm if trap counts > 8/trap/night.",
         ]},
        {"stage": "4. Boll Opening & Harvest (Days 121–180)",
         "duration": "Days 121–180",
         "key_actions": [
             "Harvest when 60–65% bolls have opened; pick in morning to reduce fibre moisture.",
             "Do not irrigate during picking — wet cotton grades down.",
             "Destroy crop residue after last picking to break bollworm cycle.",
         ]},
    ],
    "Mustard": [
        {"stage": "1. Sowing (Days 1–15)",
         "duration": "Days 1–15",
         "key_actions": [
             "Optimal sowing Oct 10–25; seed rate 1.5–2 kg/acre.",
             "Basal: 50% N + 100% P + 100% K + full Sulfur (Bentonite Sulfur 10 kg/acre).",
             "Pre-sowing irrigation to ensure good germination moisture.",
         ]},
        {"stage": "2. Vegetative & Rosette (Days 16–40)",
         "duration": "Days 16–40",
         "key_actions": [
             "1st irrigation at rosette stage (30 DAS).",
             "Apply remaining 50% N top-dress after 1st irrigation.",
             "Spray Dimethoate 30% EC @ 1.5 ml/L against mustard aphid.",
         ]},
        {"stage": "3. Flowering & Pod Formation (Days 41–75)",
         "duration": "Days 41–75",
         "key_actions": [
             "2nd irrigation at siliqua (pod) development — CRITICAL for oil yield.",
             "Avoid insecticide sprays during full bloom (honeybee pollination period).",
             "Monitor for White Rust blisters; spray Metalaxyl + Mancozeb @ 2 g/L if needed.",
         ]},
        {"stage": "4. Maturity & Harvest (Days 76–100)",
         "duration": "Days 76–100",
         "key_actions": [
             "Harvest when 75–80% pods turn straw-brown and seeds rattle.",
             "Swath and sun-dry for 3–5 days before threshing.",
             "Dry seeds to < 8% moisture for safe storage; avoid mixing with wet material.",
         ]},
    ],
    "Tomato": [
        {"stage": "1. Nursery & Transplanting (Days 1–30)",
         "duration": "Days 1–30",
         "key_actions": [
             "Raise seedlings in pro-trays with coco-peat + vermicompost for 25–30 days.",
             "Transplant in July–Aug or Jan–Feb; spacing 60 × 45 cm.",
             "Apply FYM (8–10 t/acre) + basal NPK 100:60:80 kg/ha before transplanting.",
         ]},
        {"stage": "2. Vegetative Growth (Days 31–50)",
         "duration": "Days 31–50",
         "key_actions": [
             "Install yellow sticky traps (15/acre) for whitefly monitoring.",
             "1st Nitrogen split (30%) at 30 DAT.",
             "Stake plants at 35 cm height; mulch soil with paddy straw to reduce splash.",
         ]},
        {"stage": "3. Flowering & Fruit Set (Days 51–75)",
         "duration": "Days 51–75",
         "key_actions": [
             "2nd N split (30%) at flowering; spray Calcium Nitrate @ 5 g/L to prevent Blossom End Rot.",
             "Switch to drip fertigation — avoid wetting leaves to reduce fungal risk.",
             "Spray Chlorothalonil @ 2 g/L to control Early Blight.",
         ]},
        {"stage": "4. Fruit Development & Harvest (Days 76–120)",
         "duration": "Days 76–120",
         "key_actions": [
             "3rd N split (40%) at fruit bulking; maintain consistent drip moisture.",
             "Harvest when 50–60% of fruit surface shows pink-red colour for distant markets.",
             "Post-harvest: cull diseased fruits immediately to prevent storage rot.",
         ]},
    ],
    "Vegetables": [
        {"stage": "1. Bed Preparation & Sowing/Transplanting (Days 1–20)",
         "duration": "Days 1–20",
         "key_actions": [
             "Incorporate 8–10 t/acre FYM or 2 t/acre vermicompost before sowing.",
             "Apply balanced NPK 19:19:19 @ 5 g/L foliar spray at 15 and 30 days.",
             "Raise seedlings in pro-trays for better root establishment.",
         ]},
        {"stage": "2. Vegetative Growth (Days 21–45)",
         "duration": "Days 21–45",
         "key_actions": [
             "Light, regular irrigations — avoid waterlogging.",
             "Spray Neem Oil (10,000 ppm) @ 2.5 ml/L for aphids and whiteflies.",
             "Apply Trichoderma soil drench @ 5 g/L if damping-off is noticed.",
         ]},
        {"stage": "3. Flowering & Fruiting (Days 46–75)",
         "duration": "Days 46–75",
         "key_actions": [
             "Switch to K-rich fertiliser (0:52:34 MKP @ 5 g/L) to support fruit development.",
             "Spray Calcium Nitrate foliar (5 g/L) to improve cell strength and shelf life.",
             "Monitor for Fruit Borer (Helicoverpa) — install pheromone traps 5/acre.",
         ]},
        {"stage": "4. Harvest & Post-Harvest (Days 76–100+)",
         "duration": "Days 76–100+",
         "key_actions": [
             "Harvest at physiological maturity; harvest in early morning to retain turgidity.",
             "Pre-cool produce in shade before transport; avoid bruising.",
             "Record yield data — compare with previous season to track soil health progress.",
         ]},
    ],
    "Chilli": [
        {"stage": "1. Nursery & Transplanting (Days 1–40)",
         "duration": "Days 1–40",
         "key_actions": [
             "Transplant 35–40 day old seedlings in July–Aug or Jan–Feb.",
             "Apply FYM 8 t/acre + basal NPK 60:60:60 kg/ha before transplanting.",
             "Install yellow sticky traps at transplanting to monitor vector insects.",
         ]},
        {"stage": "2. Vegetative Growth (Days 41–70)",
         "duration": "Days 41–70",
         "key_actions": [
             "1st N split at 30 DAT; spray Neem Oil 2.5 ml/L for thrips/mites.",
             "Upward leaf curl = Thrips (spray Fipronil 5% SC @ 1.5 ml/L).",
             "Downward curl = Mites (spray Wettable Sulfur 3 g/L).",
         ]},
        {"stage": "3. Flowering & Fruit Set (Days 71–100)",
         "duration": "Days 71–100",
         "key_actions": [
             "2nd N + K split; spray Boron @ 0.5 g/L to improve pollination.",
             "Spray Azoxystrobin @ 1 ml/L if Anthracnose (sunken dark fruit spots) appears.",
             "Avoid water stress at flowering — causes blossom drop.",
         ]},
        {"stage": "4. Fruit Ripening & Harvest (Days 101–150)",
         "duration": "Days 101–150",
         "key_actions": [
             "Harvest green or red chillies depending on market preference.",
             "Sun-dry red chillies to 8–10% moisture; sort and grade before storage.",
             "Apply copper spray as final protective treatment before storage curing.",
         ]},
    ],
}

# Default fallback for any unregistered crop
_DEFAULT_STAGES = [
    {"stage": "1. Land Preparation & Sowing",
     "duration": "Days 1–20",
     "key_actions": [
         "Bio-seed treatment with Trichoderma viride (5 g/kg) before sowing.",
         "Apply balanced basal NPK as per Soil Health Card recommendation.",
         "Ensure adequate pre-sowing soil moisture.",
     ]},
    {"stage": "2. Vegetative Growth",
     "duration": "Days 21–50",
     "key_actions": [
         "First split Nitrogen top-dress at crop establishment.",
         "Scout for early insect pests and fungal symptoms.",
         "Carry out hand-weeding or mechanical inter-row hoeing.",
     ]},
    {"stage": "3. Flowering & Reproductive Stage",
     "duration": "Days 51–80",
     "key_actions": [
         "Final Nitrogen and Potassium split-dose application.",
         "Maintain critical irrigation — water stress at flowering is highly damaging.",
         "Inspect for pest borers and fungal blight.",
     ]},
    {"stage": "4. Maturity & Harvest",
     "duration": "Days 81–120+",
     "key_actions": [
         "Reduce or stop irrigation 10–14 days before harvest.",
         "Harvest when physiological maturity indicators are met.",
         "Dry produce to safe moisture levels before storage.",
     ]},
]


@app.post("/api/advisory")
async def generate_crop_advisory(req: AdvisoryRequest):
    """
    Generate crop-specific growth calendar, nutrient schedule, and
    regenerative-aligned recommendations tailored to crop, soil, and irrigation.
    """
    crop      = req.crop  or "Rice"
    soil      = req.soil  or "Alluvial Soil"
    irrigation = req.irrigation or "Tube Well"
    area      = req.area  or 1.0

    # Crop-specific stages
    stages = CROP_GROWTH_CALENDARS.get(crop, _DEFAULT_STAGES)

    # Pull fertiliser and soil data from existing expert KB
    fert_text = CROP_AGRONOMY_DATA.get(crop, {}).get(
        "fertilizer",
        "Apply balanced NPK as per Soil Health Card; supplement with FYM or vermicompost."
    )
    soil_note = SOIL_KNOWLEDGE.get(
        soil,
        "Perform a comprehensive Soil Health Card test at your nearest KVK for exact nutrient status."
    )
    irr_note  = IRRIGATION_KNOWLEDGE.get(irrigation, "")

    return {
        "crop":       crop,
        "soil":       soil,
        "irrigation": irrigation,
        "area_acres": area,
        "growth_stages": stages,
        "fertilizer_plan": fert_text,
        "soil_management": soil_note,
        "irrigation_advice": irr_note,
        "recommendations": [
            f"Rotate {crop} with a leguminous pulse crop every 2–3 seasons to restore soil nitrogen.",
            f"For {soil}, incorporate composted farmyard manure (5–8 t/acre) to sustain microbial health.",
            f"Use the Soil Health Card scheme (free, every 2 years) to calibrate fertiliser doses.",
            "Install 5 pheromone traps per acre from day 1 of crop season for early pest detection.",
            "Adopt split fertiliser applications (3 doses) to improve nitrogen use efficiency by 30–40%.",
        ],
    }

# ──────────────────────────────────────────────────────────────────────────────
# Regenerative Farming Advisory  (NEW)
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/api/regenerative")
async def get_regenerative_farming_advisory(req: RegenerativeRequest):
    """
    AI-powered regenerative farming advisory:
    - Uses Gemini 1.5-Flash when API key is configured.
    - Falls back to comprehensive expert knowledge base.
    Covers cover-cropping, soil biology, carbon sequestration,
    water conservation, and agroforestry practices.
    """
    return await get_regenerative_advisory(
        crop=req.crop or "Rice",
        soil=req.soil or "Alluvial Soil",
        location=req.location or "India",
        area=req.area or 2.0,
        irrigation=req.irrigation or "Canal",
        weather_summary=req.weather_summary,
        language=req.language or "en",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
