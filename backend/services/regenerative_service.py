"""
regenerative_service.py
-----------------------
Provides AI-powered regenerative farming recommendations for KrishiSetu.

When a Gemini API key is available, generates localised, crop-and-soil-
specific regenerative guidance via Gemini 1.5-Flash.

When no key is available, falls back to a comprehensive expert knowledge
base covering cover-cropping, soil biology, carbon sequestration,
water harvesting, and biodiversity practices tailored to Indian farming.
"""

import httpx
import json
from typing import Dict, Any, Optional
from config import get_gemini_api_key


# ─────────────────────────────────────────────────────────────────────────────
# EXPERT KNOWLEDGE BASE  (used as fallback and as Gemini seed context)
# ─────────────────────────────────────────────────────────────────────────────

REGEN_PRACTICES = {
    # ── Cover crops / green manures ──────────────────────────────────────────
    "cover_crops": {
        "Rice":    ["Dhaincha (Sesbania aculeata) — incorporate at 45 days, fixes 60-80 kg N/ha.",
                    "Cowpea intercropped in bunds; cut and mulch into paddy field before transplanting.",
                    "Azolla biofertiliser floating culture between rice rows — fixes N and suppresses weeds."],
        "Wheat":   ["Berseem clover sown after wheat harvest as summer fallow cover.",
                    "Lentil or chickpea in rotation — reduces cereal-disease build-up.",
                    "Buckwheat as short-duration cover to mobilise phosphorus."],
        "Maize":   ["Cowpea intercropping (paired-row) for nitrogen fixation and soil cover.",
                    "Winter radish as deep-rooting cover to break compaction after kharif maize.",
                    "Sunhemp (Crotalaria juncea) — rapid biomass, excellent green manure."],
        "Potato":  ["Mustard or toria as preceding cover crop to reduce nematode loads.",
                    "Oats sown after potato to prevent weed flush and add organic matter.",
                    "Fenugreek (methi) as border crop — improves micro-climate."],
        "Cotton":  ["Moth bean / cluster bean intercropped in cotton furrows.",
                    "Dhaincha as summer green manure before cotton sowing.",
                    "Jowar sown on field borders as barrier against sucking pests."],
        "Default": ["Sow a quick-growing legume cover (cowpea, cluster bean, or sunhemp) in the off-season.",
                    "Maintain living mulch in inter-rows where crop canopy allows.",
                    "Plant Sesbania (Dhaincha) and chop-and-drop before next crop season."],
    },

    # ── Soil biology & organic matter ────────────────────────────────────────
    "soil_biology": [
        "Apply well-composted Farm Yard Manure (FYM) 5–8 tonnes/acre every season.",
        "Use Trichoderma viride (soil drench 5 g/L) + Pseudomonas fluorescens (5 g/L) to activate soil micro-biome.",
        "Vermicompost (2 tonnes/acre) raises soil organic carbon (SOC) by 0.1–0.2% over 2–3 seasons.",
        "Jeevamrit / Panchagavya root drench (100 L/acre) — activates indigenous soil bacteria.",
        "Avoid soil inversion tillage deeper than 10 cm to preserve fungal hyphal networks.",
        "Apply biochar (1–2 tonnes/acre once every 3–5 years) — long-term carbon sink; raises CEC by 15–30%.",
    ],

    # ── Water conservation ───────────────────────────────────────────────────
    "water_conservation": {
        "Alluvial Soil":  ["Broad-bed furrow (BBF) system to channel excess runoff into recharge pits.",
                           "Straw mulching (5–7 cm) between rows cuts evaporation by 30%."],
        "Sandy Soil":     ["Biochar incorporation improves water-holding capacity.",
                           "Deep-rooted cover crops (radish, sunflower) open soil pores for infiltration."],
        "Clay Soil":      ["Sub-soiling every 3–4 years prevents waterlogging and anaerobic zones.",
                           "Raised-bed planting protects root zone from saturation."],
        "Black Soil":     ["Tie-ridge or broad-bed system reduces runoff on heavy clay soils.",
                           "Leave previous crop residue standing 15 cm high to slow runoff velocity."],
        "Default":        ["Construct field bunds and micro-catchment pits to harvest rainwater.",
                           "Mulch with 4–6 cm of dry crop residue between rows to cut soil moisture loss."],
    },

    # ── Crop rotation & diversity ─────────────────────────────────────────────
    "rotation": {
        "Rice":    "Rice → Lentil (rabi) → Sesbania green manure → Rice (break blast cycle, restore N).",
        "Wheat":   "Wheat → Cowpea/Maize (kharif) → Mustard → Wheat (diversify root exudates).",
        "Maize":   "Maize → Chickpea → Sunflower → Maize (reduces fall-armyworm pressure).",
        "Potato":  "Potato → Berseem/Oats → Wheat or Rice → Potato (breaks nematode cycle every 3 years).",
        "Mustard": "Mustard → Rice or Maize → Lentil → Mustard (alternating brassica gaps).",
        "Cotton":  "Cotton → Wheat/Chickpea → Cluster Bean → Cotton (reduces pink bollworm carryover).",
        "Default": "Alternate cereal → legume → oilseed → cereal rotation every 3 seasons.",
    },

    # ── Agroforestry / biodiversity ──────────────────────────────────────────
    "agroforestry": [
        "Plant Moringa (drumstick) or Neem trees on field bunds — provide bio-pesticide leaves and shade.",
        "Pigeon pea (tur/arhar) as boundary crop — nitrogen-fixing shrub, reduces border weed colonisation.",
        "Melia dubia or Subabool (Leucaena) on one bund row — provides fodder, shade, and wood in 3 years.",
        "Maintain at least 1% of farm area as wildflower / native grass strip to attract pollinators and predatory insects.",
        "Plant vetiver grass on field edges — deep roots prevent erosion and recharge groundwater.",
    ],

    # ── Carbon sequestration ─────────────────────────────────────────────────
    "carbon": [
        "Each tonne of compost applied sequesters ~0.3 tonne CO₂-equivalent in stable humus.",
        "No-till or minimum-till practice can sequester 0.2–0.4 tonne C/ha/year.",
        "Crop residue incorporation (instead of burning) adds ~150–200 kg organic C/ha/season.",
        "Biochar amendment is the most stable carbon input — 85–90% of carbon remains for centuries.",
        "Enrol in PM-PRANAM or state-level carbon credit programmes (coming 2025–27) for residue management.",
    ],

    # ── Soil health card alignment ────────────────────────────────────────────
    "soil_health": [
        "Get a free Soil Health Card (SHC) at your nearest KVK every 2 years — test N, P, K, pH, OC, and micronutrients.",
        "Target soil organic carbon (SOC) > 0.75% for good structural stability.",
        "If soil pH < 6.0 — apply agricultural limestone (500–1000 kg/acre) to raise to 6.5–7.0.",
        "If soil pH > 8.5 — apply gypsum (CaSO₄) 400 kg/acre and deep leach to displace sodium.",
        "Avoid burning crop residue — a single stubble fire destroys 90% of soil surface micro-organisms.",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPER — build expert fallback response
# ─────────────────────────────────────────────────────────────────────────────

def build_regen_expert_response(
    crop: str,
    soil: str,
    location: str,
    area: float,
    irrigation: str,
) -> Dict[str, Any]:
    """Return a structured regenerative-farming advisory from the expert KB."""
    crop_key  = crop  if crop  in REGEN_PRACTICES["cover_crops"]  else "Default"
    soil_key  = soil  if soil  in REGEN_PRACTICES["water_conservation"] else "Default"
    rot_text  = REGEN_PRACTICES["rotation"].get(crop, REGEN_PRACTICES["rotation"]["Default"])

    return {
        "source":   "KrishiSetu Regenerative Farming Expert System",
        "crop":     crop,
        "soil":     soil,
        "location": location,
        "area_acres": area,

        "summary": (
            f"Regenerative practices for {crop} on {area} acres of {soil} in {location}. "
            "These recommendations aim to improve soil health, sequester carbon, "
            "conserve water, and reduce dependence on synthetic inputs."
        ),

        "cover_crops_green_manures": REGEN_PRACTICES["cover_crops"].get(crop_key, REGEN_PRACTICES["cover_crops"]["Default"]),

        "soil_biology_practices":    REGEN_PRACTICES["soil_biology"],

        "water_conservation":        REGEN_PRACTICES["water_conservation"].get(soil_key, REGEN_PRACTICES["water_conservation"]["Default"]),

        "crop_rotation_plan":        rot_text,

        "agroforestry_biodiversity": REGEN_PRACTICES["agroforestry"],

        "carbon_sequestration":      REGEN_PRACTICES["carbon"],

        "soil_health_targets":       REGEN_PRACTICES["soil_health"],

        "quick_wins": [
            f"Stop burning crop residue after {crop} harvest — incorporate it instead.",
            f"Apply Jeevamrit (fermented cow-dung + urine blend) 100 L/acre monthly.",
            f"Reduce chemical nitrogen by 20–25% and compensate with Azotobacter bio-fertiliser.",
            f"Set up one on-farm compost pit using kitchen waste + crop residue + cow-dung.",
        ],

        "expected_benefits": {
            "soil_organic_carbon_gain": "+0.1–0.2% SOC per season with full practice adoption",
            "water_savings":            "15–35% reduction in irrigation requirement within 2 seasons",
            "input_cost_reduction":     "₹2,000–5,000/acre/season from reduced chemical inputs",
            "biodiversity_index":       "Expected 20–40% rise in beneficial insect populations",
            "carbon_credits":           "Eligible for state carbon credit pilot programmes (verify with local KVK)",
        },

        "disclaimer": (
            "These are science-based advisory recommendations. Consult your local "
            "Krishi Vigyan Kendra (KVK) for soil-test-specific and region-specific validation."
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# GEMINI CALL
# ─────────────────────────────────────────────────────────────────────────────

async def _gemini_regen_advisory(
    api_key: str,
    crop: str,
    soil: str,
    location: str,
    area: float,
    irrigation: str,
    weather_summary: Optional[str] = None,
    language: str = "en",
) -> Optional[Dict[str, Any]]:
    """
    Ask Gemini 1.5-Flash to generate a structured JSON regenerative
    farming advisory for the farmer's specific profile.
    """
    lang_instr = {
        "hi": "Respond entirely in natural Hindi (हिन्दी).",
        "bn": "Respond entirely in natural Bengali (বাংলা).",
    }.get(language, "Respond in clear, practical English.")

    weather_ctx = f"\nCurrent weather context: {weather_summary}" if weather_summary else ""

    system_prompt = f"""You are an expert in regenerative agriculture and sustainable farming.
{lang_instr}

Farmer Profile:
- Crop: {crop}
- Soil: {soil}
- Location: {location}
- Farm Area: {area} acres
- Irrigation: {irrigation}{weather_ctx}

Generate a comprehensive regenerative farming advisory as a JSON object with these keys:
{{
  "summary": "2-sentence overview",
  "cover_crops_green_manures": ["practice 1", "practice 2", "practice 3"],
  "soil_biology_practices":    ["practice 1", "practice 2", "practice 3"],
  "water_conservation":        ["practice 1", "practice 2"],
  "crop_rotation_plan":        "Full 3-year rotation plan",
  "agroforestry_biodiversity": ["practice 1", "practice 2"],
  "carbon_sequestration":      ["practice 1", "practice 2"],
  "soil_health_targets":       ["target 1", "target 2"],
  "quick_wins":                ["win 1", "win 2", "win 3", "win 4"],
  "expected_benefits": {{
    "soil_organic_carbon_gain": "...",
    "water_savings":            "...",
    "input_cost_reduction":     "...",
    "biodiversity_index":       "..."
  }},
  "disclaimer": "Advisory note"
}}

Tailor every recommendation to the farmer's specific crop, soil type, location in India, and irrigation method.
Do NOT return generic text — be specific to {crop} grown in {soil} in {location}.
Return ONLY the JSON object, no markdown fences."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": system_prompt}]}],
        "generationConfig": {"temperature": 0.35, "maxOutputTokens": 1500,
                              "response_mime_type": "application/json"},
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                cleaned = text.replace("```json", "").replace("```", "").strip()
                result = json.loads(cleaned)
                result["source"]   = "Google Gemini 1.5-Flash Generative AI"
                result["crop"]     = crop
                result["soil"]     = soil
                result["location"] = location
                result["area_acres"] = area
                return result
    except Exception as exc:
        print(f"[Regen] Gemini call error: {exc}")
    return None


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

async def get_regenerative_advisory(
    crop: str = "Rice",
    soil: str = "Alluvial Soil",
    location: str = "India",
    area: float = 2.0,
    irrigation: str = "Canal",
    weather_summary: Optional[str] = None,
    language: str = "en",
) -> Dict[str, Any]:
    """
    Return a regenerative farming advisory.
    Tries Gemini first; falls back to the expert KB.
    """
    api_key = get_gemini_api_key()
    if api_key:
        gemini_result = await _gemini_regen_advisory(
            api_key, crop, soil, location, area, irrigation,
            weather_summary, language,
        )
        if gemini_result:
            return gemini_result

    return build_regen_expert_response(crop, soil, location, area, irrigation)
