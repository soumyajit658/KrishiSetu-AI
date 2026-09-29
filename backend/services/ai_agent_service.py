import re
import httpx
from typing import Dict, Any, List, Optional
from config import get_gemini_api_key

# =====================================================================
# EXTENSIVE AGRONOMIC KNOWLEDGE BASE (EXPERT SYSTEM)
# Covers crops, fertilizers, pests, diseases, irrigation, soil & more
# =====================================================================

CROP_AGRONOMY_DATA = {
    "Rice": {
        "fertilizer": "Recommended NPK ratio for Rice is **120:60:60 kg/ha** (or approx. 50 kg Urea, 75 kg DAP, and 50 kg MOP per acre).\n- **Basal**: Apply full Phosphorus (DAP), 50% Potash (MOP), and 1/3rd Nitrogen (Urea) at transplanting.\n- **First Top-dress**: 1/3rd Nitrogen at active tillering (20-25 days after transplanting).\n- **Second Top-dress**: Remaining 1/3rd Nitrogen + 50% Potash at panicle initiation (40-45 days).\n- **Micronutrients**: If leaves show zinc deficiency (khaira disease), apply Zinc Sulfate (ZnSO4 21% @ 25 kg/ha or ZnSO4 33% @ 15 kg/ha).",
        "pests": "- **Stem Borer**: Yellow stem borer causes 'dead heart' in vegetative and 'white earhead' in reproductive stages. Apply Cartap Hydrochloride 4G @ 10 kg/acre or Chlorantraniliprole 18.5% SC (Coragen) @ 60 ml/acre.\n- **Brown Planthopper (BPH)**: Drains sap near water level causing 'hopper burn'. Avoid excessive Urea; spray Pymetrozine 50% WDG @ 120 g/acre or Triflumezopyrim 10% SC @ 94 ml/acre.\n- **Leaf Folder**: Larvae fold leaf longitudinally. Install Trichogramma cards (20,000 eggs/acre) or spray Flubendiamide 39.35% SC @ 25 ml/acre.",
        "diseases": "- **Rice Blast**: Diamond/spindle lesions with grey centers. Spray Tricyclazole 75% WP @ 120 g/acre or Kasugamycin 3% SL @ 400 ml/acre.\n- **Bacterial Leaf Blight (BLB)**: Wavy straw-colored lesions starting at leaf margins. Spray Streptocycline (6g) + Copper Oxychloride 50% WP (500g) in 200L water.\n- **Brown Spot**: Circular/oval brown spots with yellow halo. Spray Mancozeb 75% WP @ 600-800 g/acre.",
        "irrigation": "Maintain 2-3 cm shallow water layer during initial 30 days after transplanting. Keep 5 cm water during tillering to flowering. **Crucial**: Never let soil dry out during flowering/panicle emergence. Drain water completely 10-12 days before harvest.",
        "sowing": "Nursery sowing: May-June (Kharif) or November-December (Rabi). Seed rate: 12-15 kg/acre for transplanted rice; 6-8 kg/acre for SRI/hybrid. Seed treatment: Soak seeds in Carbendazim 2g/kg or Trichoderma viride 5g/kg."
    },
    "Wheat": {
        "fertilizer": "Recommended dose: **120:60:40 kg/ha** (approx. 55 kg Urea, 75 kg DAP, 35 kg MOP per acre).\n- **Basal**: 100% Phosphorus, 100% Potash, and 1/3rd Nitrogen applied at sowing time.\n- **1st Split**: 1/3rd Nitrogen applied at Crown Root Initiation (CRI) stage (21 days after sowing) with 1st irrigation.\n- **2nd Split**: Remaining 1/3rd Nitrogen applied at late tillering / jointing stage (45-50 days).",
        "pests": "- **Termites**: Feed on roots and cause drying of seedlings. Treat seeds with Chlorpyrifos 20% EC (4 ml/kg seed) or apply Fipronil 0.3% G @ 10 kg/acre in soil.\n- **Aphids**: Suck sap from tender spikes in cloudy/cool weather. Spray Thiamethoxam 25% WG @ 50 g/acre or Neem Oil (10,000 ppm) @ 2 ml/L water.",
        "diseases": "- **Yellow / Stripe Rust**: Linear yellow stripes on leaf blades. Spray Propiconazole 25% EC (Tilt) @ 200 ml/acre in 200L water at first sign.\n- **Loose Smut**: Earheads turn into powdery black spores. Seed treatment with Carboxin + Thiram (Vitavax) @ 2.5 g/kg seed is essential prevention.\n- **Karnal Bunt**: Grains emit fishy smell and black powder. Spray Tebuconazole 25.9% EC @ 200 ml/acre at 50% earhead emergence.",
        "irrigation": "Wheat requires 4 to 6 critical irrigations:\n1. Crown Root Initiation (CRI) - 21 DAS (Most Critical!)\n2. Tillering stage - 40-45 DAS\n3. Late Jointing - 60-65 DAS\n4. Flowering - 80-85 DAS\n5. Milking/Dough stage - 100-105 DAS.",
        "sowing": "Optimum sowing time is November 1 to November 20. Seed rate: 40-45 kg/acre (100 kg/ha) with row spacing of 20-22.5 cm and depth of 4-5 cm."
    },
    "Potato": {
        "fertilizer": "Potato is a heavy potassium feeder for tuber development: **150:100:150 kg/ha** (approx. 65 kg Urea, 125 kg DAP, 125 kg MOP per acre).\n- Apply full P, 50% K, and 50% N at planting in furrows.\n- Top-dress remaining 50% N and 50% K at earthing-up (30-35 days after planting).\n- Foliar spray of Potassium Nitrate (13:0:45) @ 10 g/L at 55 and 70 days significantly increases tuber size.",
        "pests": "- **Potato Tuber Moth (PTM)**: Larvae tunnel into tubers. Maintain good earthing up (15-20 cm) so tubers are not exposed.\n- **Aphids (Myzus persicae)**: Vectors of potato viruses. Spray Imidacloprid 17.8% SL @ 60 ml/acre or Acetamiprid 20% SP @ 50 g/acre.",
        "diseases": "- **Late Blight (Phytophthora infestans)**: Water-soaked lesions turning dark with white downy growth underneath. Preventive: Mancozeb 75% WP @ 2.5 g/L. Curative: Cymoxanil 8% + Mancozeb 64% (Curzate) @ 2.5 g/L or Metalaxyl + Mancozeb (Ridomil MZ) @ 2.5 g/L.\n- **Early Blight**: Concentric target-board spots on leaves. Spray Chlorothalonil 75% WP @ 2 g/L.",
        "irrigation": "Light and frequent irrigations are best. Keep ridges moist but do not submerge ridges. Stop irrigation 10-12 days before de-haulming/harvesting to allow skin hardening.",
        "sowing": "Plant disease-free seed tubers (30-50g) in October-November. Treat tubers with Mancozeb (2.5 g/L) or boric acid (3%) before planting."
    },
    "Maize": {
        "fertilizer": "Recommended dose: **120:60:40 kg/ha**.\n- Basal: 1/3rd Nitrogen + 100% Phosphorus + 100% Potassium at sowing.\n- 1st Top-dress: 1/3rd Nitrogen at knee-high stage (30-35 DAS).\n- 2nd Top-dress: Remaining 1/3rd Nitrogen at tasseling/silking stage (50-60 DAS).",
        "pests": "- **Fall Armyworm (Spodoptera frugiperda)**: Characteristic pinholes and heavy windowing in the whorl with frass. Spray Chlorantraniliprole 18.5% SC @ 0.4 ml/L or Emamectin Benzoate 5% SG @ 0.5 g/L directed into the central whorl.\n- **Stem Borer**: Bore holes in stems. Apply Carbofuran 3G @ 3 kg/acre in whorls.",
        "diseases": "- **Turcicum Leaf Blight**: Long elliptical grayish-tan lesions. Spray Azoxystrobin 18.2% + Difenoconazole 11.4% SC (Amistar Top) @ 1 ml/L or Mancozeb @ 2.5 g/L.\n- **Maydis Leaf Blight**: Small diamond/rectangular lesions. Spray Zineb @ 2 g/L.",
        "irrigation": "Maize is highly sensitive to both waterlogging and drought. Ensure raised beds. Critical stages: Knee-high, Tasseling, and Grain filling.",
        "sowing": "Kharif: June-July; Rabi: October-November; Spring: February. Seed rate: 8-10 kg/acre for hybrids. Spacing: 60 cm x 20 cm."
    },
    "Tomato": {
        "fertilizer": "NPK **100:60:80 kg/ha** with high calcium and magnesium.\n- Incorporate 8-10 tons FYM/acre before transplanting.\n- Split Nitrogen: 40% basal, 30% at flowering, 30% at fruit bulking.\n- Apply Calcium Nitrate @ 5 g/L foliar spray to prevent Blossom End Rot (black sunken fruit tips).",
        "pests": "- **Fruit Borer (Helicoverpa)**: Larvae bore into tomatoes. Spray Flubendiamide 39.35% SC @ 0.3 ml/L or spinosad 45% SC @ 0.3 ml/L.\n- **Whitefly**: Transmits Tomato Leaf Curl Virus. Install yellow sticky traps (15/acre). Spray Diafenthiuron 50% WP @ 1.2 g/L or Neem Oil.",
        "diseases": "- **Tomato Leaf Curl**: Stunted bush with severely upward-curled, thickened leaves. Control whitefly vector; rogue out infected plants early.\n- **Early Blight**: Target-ring concentric spots. Spray Chlorothalonil 75% WP @ 2 g/L or Saaf (Carbendazim + Mancozeb) @ 2 g/L.",
        "irrigation": "Drip irrigation is ideal. Maintain consistent moisture; sudden irrigation after a dry spell causes severe fruit cracking/splitting.",
        "sowing": "Transplant 25-30 day old healthy nursery seedlings. Treat nursery with Trichoderma viride."
    },
    "Vegetables": {
        "fertilizer": "For mixed vegetables, incorporate 8-10 tons of well-composted Farm Yard Manure (FYM) or 2 tons Vermicompost per acre.\n- Apply balanced NPK 19:19:19 @ 5 g/L foliar spray every 15 days during vegetative growth.\n- Switch to NPK 0:52:34 (Monopotassium Phosphate) during flowering and fruit setting to avoid excessive vegetative growth.",
        "pests": "- **Aphids, Thrips & Sucking Pests**: Spray cold-pressed Neem Oil (10,000 ppm) @ 2-3 ml/L water with a few drops of liquid soap.\n- **Fruit & Shoot Borers**: Use pheromone traps @ 5 per acre. Spray Bacillus thuringiensis (Bt) @ 2 g/L or Emamectin Benzoate 5% SG @ 0.5 g/L.",
        "diseases": "- **Damping Off in Seedlings**: Drench nursery beds with Trichoderma viride (10 g/L) or Copper Oxychloride 50% WP (2.5 g/L).\n- **Powdery Mildew**: White powdery coating on leaves. Spray Wettable Sulfur 80% WP @ 2.5 g/L or Hexaconazole 5% EC @ 1 ml/L.",
        "irrigation": "Light, regular irrigations. Avoid overhead wetting of foliage late in the day to minimize fungal spore germination.",
        "sowing": "Raise seedlings in raised nursery beds or seedling pro-trays with coco-peat and vermicompost for superior root establishment."
    },
    "Mustard": {
        "fertilizer": "Recommended dose: **80:40:40 kg/ha** with **20-30 kg/ha Sulfur** (Sulfur is critical for oil percentage and seed weight).\n- Basal: 50% N + 100% P + 100% K + full Elemental Sulfur or Bentonite Sulfur.\n- Top-dress: Remaining 50% N at 1st irrigation (30-35 DAS).",
        "pests": "- **Mustard Aphids (Lipaphis erysimi)**: Serious pest during flowering/cloudy weather. Spray Dimethoate 30% EC @ 1.5 ml/L or Thiamethoxam 25% WG @ 0.3 g/L.",
        "diseases": "- **White Rust**: White blisters on leaf undersides. Spray Metalaxyl 8% + Mancozeb 64% (Ridomil) @ 2 g/L.",
        "irrigation": "Mustard requires 2 to 3 irrigations: 1st at rosette stage (30 DAS) and 2nd at siliqua (pod) development (60 DAS).",
        "sowing": "Optimum sowing: October 10 to October 25. Seed rate: 1.5-2 kg/acre."
    },
    "Cotton": {
        "fertilizer": "Recommended dose: **120:60:60 kg/ha**.\n- Apply Nitrogen in 3 splits (basal, square formation, and peak boll development).\n- Foliar spray of 1% Magnesium Sulfate + 0.2% Boron at 60 and 80 DAS prevents leaf reddening and square drop.",
        "pests": "- **Pink Bollworm**: Install pink bollworm pheromone traps (5/acre). Spray Profenofos 50% EC @ 2 ml/L or Emamectin Benzoate 5% SG @ 0.5 g/L.\n- **Whitefly & Jassids**: Spray Flonicamid 50% WG @ 0.3 g/L or Neem oil.",
        "diseases": "- **Cotton Leaf Curl Virus (CLCuV)**: Transmitted by whitefly. Control vectors and destroy volunteer hosts.\n- **Bacterial Blight / Angular Leaf Spot**: Spray Copper Oxychloride @ 2.5 g/L + Streptocycline @ 0.1 g/L.",
        "irrigation": "Irrigate at square formation, flowering, and boll development. Avoid water stress during flowering.",
        "sowing": "Sow in April-May. Spacing: 90 cm x 60 cm for hybrids."
    },
    "Chilli": {
        "fertilizer": "NPK **120:60:60 kg/ha** with Farm Yard Manure @ 8 tons/acre.\n- Basal: 50% N, 100% P, 50% K.\n- Top-dress remaining N and K in two equal splits at 30 and 60 days after transplanting.",
        "pests": "- **Chilli Thrips & Mites**: Causes leaf curling ('Murda' disease). Upward curling = Thrips (spray Fipronil 5% SC @ 1.5 ml/L); Downward curling = Mites (spray Fenpyroximate 5% EC @ 1 ml/L or Wettable Sulfur 3 g/L).",
        "diseases": "- **Anthracnose / Dieback**: Circular sunken necrotic spots on ripe fruit and twig drying from top. Spray Azoxystrobin 23% SC @ 1 ml/L or Mancozeb @ 2.5 g/L.",
        "irrigation": "Chilli cannot tolerate water stagnation. Use ridge-and-furrow or drip irrigation.",
        "sowing": "Transplant 35-40 day old seedlings in July-August or January-February."
    }
}

SOIL_KNOWLEDGE = {
    "Alluvial Soil": "Alluvial soil is naturally rich in potash and lime but often deficient in nitrogen and organic matter. Highly responsive to balanced fertilizers. Adopt green manuring (Dhaincha/Sesbania) every 2-3 years to sustain microbial carbon.",
    "Clay Soil": "Clay soil has high nutrient and moisture retention but is prone to waterlogging and surface compaction. Cultivate on raised beds or broad-bed furrows. Avoid tilling when wet to prevent hard clods.",
    "Sandy Soil": "Sandy soil drains rapidly and suffers from nutrient leaching. Apply fertilizers in frequent, smaller split doses rather than heavy single doses. Incorporate compost, biochar, or coir pith to boost water retention.",
    "Loamy Soil": "Loamy soil has ideal balance of drainage, aeration, and moisture-holding capacity. Highly versatile for crop rotations. Maintain soil structure by avoiding heavy machinery compaction.",
    "Black Soil": "Black cotton soil expands when wet and cracks when dry. Rich in calcium and magnesium. Complete seedbed preparation and early sowing before heavy monsoon rains to avoid intractable clay tillage.",
    "Red Soil": "Red soils are porous with good drainage but are naturally low in nitrogen, phosphorus, and organic matter, and often slightly acidic. Apply rock phosphate or single superphosphate (SSP) and well-rotted FYM.",
    "Unknown": "Perform a comprehensive Soil Health Card test at your nearest KVK or agricultural center to determine exact pH, organic carbon (OC), and available N-P-K."
}

IRRIGATION_KNOWLEDGE = {
    "Drip Irrigation": "Drip irrigation provides 90%+ water efficiency. Run in frequent, short pulses. Apply water-soluble fertilizers (fertigation) directly to root zone to save 25-30% fertilizer.",
    "Sprinkler": "Sprinkler irrigation is suitable for undulating topography and closely spaced crops (wheat, pulses, oilseeds). Avoid running during windy hours (>12 km/h) or hot midday to minimize evaporation.",
    "Tube Well": "Test tubewell groundwater electrical conductivity (EC) and residual sodium carbonate (RSC). If water is saline or alkali, blend with rainwater and apply gypsum to field.",
    "Borewell": "Monitor water table levels. Practice recharge pits near borewell catchment. In summer, irrigate during late evening or night hours.",
    "Canal": "With rotational canal supply, maximize soil moisture conservation: practice inter-row mulching and maintain bunds to prevent runoff.",
    "Rainfed": "For rainfed crops, adopt in-situ moisture conservation: field bunding, broad-bed furrow system, straw mulching, and foliar spray of 2% Potassium Chloride (KCl) during mid-season dry spells."
}

# =====================================================================
# CORE AGENT GENERATION LOGIC
# =====================================================================

async def query_gemini_api(
    api_key: str,
    system_prompt: str,
    query: str,
    history: Optional[List[Dict[str, str]]] = None
) -> Optional[str]:
    """Query Google Gemini API with fallback across flash models."""
    models_to_try = [
        "gemini-1.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro"
    ]
    
    # 1. Format clean conversation contents (alternating user/model, starting with user)
    contents = []
    if history:
        for msg in history:
            role = msg.get("role", "")
            text = (msg.get("content") or "").strip()
            if not text:
                continue
            gemini_role = "user" if role == "user" else "model"
            
            # Gemini strictly requires the first turn to be 'user'
            if not contents and gemini_role == "model":
                continue
            
            # Merge consecutive messages with the same role
            if contents and contents[-1]["role"] == gemini_role:
                contents[-1]["parts"][0]["text"] += f"\n\n{text}"
            else:
                contents.append({
                    "role": gemini_role,
                    "parts": [{"text": text}]
                })
    
    # Append the current user query, ensuring proper alternation
    if contents and contents[-1]["role"] == "user":
        contents.append({
            "role": "model",
            "parts": [{"text": "Understood. Please ask your farming question."}]
        })
    
    contents.append({
        "role": "user",
        "parts": [{"text": query}]
    })

    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 1200
        }
    }

    async with httpx.AsyncClient(timeout=18.0) as client:
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            try:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
                elif resp.status_code == 400:
                    # If model doesn't support system_instruction, inject into first user turn
                    fallback_contents = [
                        {"role": "user", "parts": [{"text": f"Instruction:\n{system_prompt}\n\nFarmer Question:\n{query}"}]}
                    ]
                    resp_fallback = await client.post(url, json={
                        "contents": fallback_contents,
                        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1200}
                    })
                    if resp_fallback.status_code == 200:
                        data = resp_fallback.json()
                        return data["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        print(f"[KrishiSetu AI] Gemini {model} fallback returned {resp_fallback.status_code}: {resp_fallback.text[:120]}")
                else:
                    print(f"[KrishiSetu AI] Gemini {model} error {resp.status_code}: {resp.text[:120]}")
            except Exception as e:
                print(f"[KrishiSetu AI] Gemini {model} network error: {e}")
                continue

    return None

LOCAL_CROP_HI = {
    "Rice": "धान", "Wheat": "गेहूं", "Potato": "आलू", "Maize": "मक्का",
    "Tomato": "टमाटर", "Chilli": "मिर्च", "Mustard": "सरसों", "Cotton": "कपास",
    "Vegetables": "सब्जियां", "General Crop": "फसल", "Crop": "फसल"
}
LOCAL_CROP_BN = {
    "Rice": "ধান", "Wheat": "গম", "Potato": "আলু", "Maize": "ভুট্টা",
    "Tomato": "টমেটো", "Chilli": "লঙ্কা", "Mustard": "সরিষা", "Cotton": "তুলা",
    "Vegetables": "শাকসবজি", "General Crop": "ফসল", "Crop": "ফসল"
}
LOCAL_SOIL_HI = {
    "Alluvial Soil": "जलोढ़ मिट्टी", "Loamy Soil": "दोमट मिट्टी", "Clay Soil": "चिकनी मिट्टी",
    "Sandy Soil": "बलुई मिट्टी", "Black Soil": "काली मिट्टी", "Red Soil": "लाल मिट्टी"
}
LOCAL_SOIL_BN = {
    "Alluvial Soil": "পলি মাটি", "Loamy Soil": "দোআঁশ মাটি", "Clay Soil": "এঁটেল মাটি",
    "Sandy Soil": "বেলে মাটি", "Black Soil": "কালো মাটি", "Red Soil": "লাল মাটি"
}

def build_hindi_response(
    query: str,
    q_lower: str,
    active_crop: str,
    location: str,
    soil: str,
    irrigation: str,
    area: str,
    analysis_context: Optional[Dict[str, Any]] = None
) -> str:
    """Localized Hindi Agronomic Expert Response Engine."""
    crop_hi = LOCAL_CROP_HI.get(active_crop, active_crop)
    soil_hi = LOCAL_SOIL_HI.get(soil, soil)

    # 1. Report follow-up
    if analysis_context and any(k in q_lower for k in [
        "now", "treatment", "report", "spread", "cure", "remedy", "what to do", 
        "should i do", "scan", "diagnosis", "recommendation", "doctor", "step",
        "उपचार", "दवा", "इलाज", "फैलेगा", "रिपोर्ट", "रोग"
    ]):
        issue = analysis_context.get("primary_issue") or analysis_context.get("overall_field_status") or "पत्ती तनाव"
        severity = analysis_context.get("severity", "मध्यम")
        score = analysis_context.get("overall_health_score") or analysis_context.get("health_score", 80)
        actions = analysis_context.get("recommended_actions") or analysis_context.get("recommendations") or []
        actions_list = "\n".join([f"- {a}" for a in actions[:4]]) if actions else "- जैविक नियंत्रण अपनाएं और स्थानीय कृषि विज्ञान केंद्र से संपर्क करें।"

        if any(k in q_lower for k in ["spread", "infect", "nearby", "neighbor", "फैलेगा", "फैल"]):
            return f"""### 🌾 {crop_hi} में रोग फैलाव की रोकथाम

आपकी हालिया जांच रिपोर्ट में **{issue}** की पहचान हुई है:

- **फैलाव का जोखिम**: **{severity}** (नमी और बारिश में संक्रमण तेजी से फैलता है)।
- **प्रमुख रोकथाम कदम**:
  1. **औजारों को रोगाणुरहित करें**: खुरपी, प्रूनर और स्प्रेयर को 10% ब्लीच या कॉपर सल्फेट से धोएं।
  2. **गीले खेत में न घूमें**: कवक और जीवाणु के बीजाणु गीले कपड़ों और जूतों से स्वस्थ पौधों में फैलते हैं।
  3. **सुरक्षा घेरा बनाएं**: संक्रमित हिस्से के चारों ओर 2 मीटर के दायरे में ट्राइकोडर्मा विरिडी (5 ग्राम/लीटर) या कॉपर ऑक्सीक्लोराइड 50% WP (2.5 ग्राम/लीटर) का स्प्रे करें।
  4. **हवा का संचार**: नीचे की सड़ी-गली पत्तियों को हटाकर पौधे में धूप और हवा आने दें।

💡 *संक्रमण की प्रगति देखने के लिए आसपास के पौधों का हर 48 घंटे में निरीक्षण करें।*"""

        if any(k in q_lower for k in ["organic", "natural", "bio", "home remedy", "desi", "जैविक", "देसी"]):
            return f"""### 🌿 जैविक व प्राकृतिक उपचार: {issue}

आपकी **{crop_hi}** फसल के लिए अनुशंसित प्राकृतिक उपचार:

1. **नीम तेल का स्प्रे**: 10,000 ppm कोल्ड-प्रेस्ड नीम तेल (2.5 से 3 मिली प्रति लीटर पानी) में 1 मिली तरल साबुन मिलाकर छिड़काव करें।
2. **जैविक मित्र फफूंद**: ट्राइकोडर्मा विरिडी (*Trichoderma viride*) या स्यूडोमोनास 5 ग्राम प्रति लीटर पानी में सुबह के समय स्प्रे करें।
3. **पारंपरिक खट्टी छाछ**: 10-15 दिन पुरानी खट्टी छाछ में तांबे का टुकड़ा डालकर, 1:10 के अनुपात में पानी मिलाकर पत्तियों पर छिड़कें। यह प्राकृतिक फफूंदनाशक है।
4. **जीवामृत से पोषण**: जड़ों के पास जीवामृत (100 लीटर प्रति एकड़) दें जिससे मिट्टी के मित्र सूक्ष्मजीव सक्रिय हों।

⚠️ *ट्राइकोडर्मा जैसे जीवित जैविक एजेंटों के प्रयोग से 4 दिन पहले या बाद तक रासायनिक कीटनाशकों का छिड़काव न करें।*"""

        return f"""### 📋 फील्ड डॉक्टर कार्य योजना: {issue}

आपकी **{crop_hi}** की हालिया जांच रिपोर्ट के आधार पर:
- **निदान**: {issue} ({severity} गंभीरता • स्वास्थ्य स्कोर: {score}%)
- **सिफारिशें**:
{actions_list}

#### 💧 जल एवं खेत प्रबंधन:
- पत्तियों पर रोग सक्रिय रहने तक फव्वारा सिंचाई न करें।
- खेत में जलभराव न होने दें और उचित जल निकासी रखें।
- रासायनिक स्प्रे करते समय मास्क और दस्ताने पहनें तथा 10-14 दिन का सुरक्षा अंतराल (PHI) रखें।"""

    # 2. Greetings
    if any(q_lower.startswith(g) or q_lower == g for g in [
        "hi", "hello", "namaste", "pranam", "hey", "kisan", "help",
        "नमस्ते", "प्रणाम", "मदद", "राम राम", "नमस्कार"
    ]):
        return f"""### 🙏 नमस्ते! मैं कृषि सेतु एआई हूँ

मैं आपका व्यक्तिगत कृषि वैज्ञानिक और फसल सलाहकार हूँ, जो **{location}** में आपके **{area} एकड़ {crop_hi} खेत** ({soil_hi}, {irrigation}) के लिए तैयार किया गया है।

मैं अभी इन मुख्य विषयों पर आपकी सहायता कर सकता हूँ:
1. **🧪 खाद एवं पोषण**: {crop_hi} के लिए N-P-K की सही मात्रा, बेसल व टॉप-ड्रेसिंग समय।
2. **🐛 कीट व रोग नियंत्रण**: नीम तेल, फेरोमोन ट्रैप और रासायनिक सुरक्षा उपाय।
3. **💧 सिंचाई प्रबंधन**: {irrigation} के अनुसार सिंचाई का सही समय और पानी की बचत।
4. **🌾 बुवाई और खरपतवार**: उन्नत बीज दर, बीज उपचार और खरपतवार नियंत्रण।
5. **🏛️ सरकारी योजनाएं**: पीएम-किसान, फसल बीमा योजना (PMFBY) और किसान क्रेडिट कार्ड (KCC)।

💬 *कोई भी सवाल अपनी भाषा में पूछें! जैसे:*
- *"मेरी {crop_hi} की फसल के लिए सही खाद की मात्रा क्या है?"*
- *"निचली पत्तियां पीली क्यों पड़ रही हैं?"*
- *"कीटों से बचाव के लिए जैविक उपाय क्या हैं?"*"""

    # 3. Fertilizer
    if any(k in q_lower for k in [
        "fertilizer", "urea", "dap", "potash", "npk", "nutrition", "khad", 
        "micronutrient", "zinc", "boron", "nitrogen", "खाद", "उर्वरक", "यूरिया", "पोटाश"
    ]):
        return f"""### 🌾 {crop_hi} के लिए अनुशंसित खाद एवं पोषण प्रबंधन

📍 **खेत संदर्भ**: {location} • {soil_hi} • {area} एकड़ • {irrigation}

#### 📋 मुख्य पोषक तत्व समय सारिणी:
- **बुवाई / रोपाई के समय (बेसल डोज)**: पूरी फॉस्फोरस (DAP/SSP), 50% पोटाश (MOP) और 33% यूरिया खेत तैयारी के समय मिट्टी में मिलाएँ।
- **पहली टॉप-ड्रेसिंग (20-25 दिन बाद)**: कल्ले फूटते समय बची हुई यूरिया का 33% हिस्सा खेत में नमी होने पर दें।
- **दूसरी टॉप-ड्रेसिंग (40-45 दिन बाद)**: बालियां निकलने से पहले बची हुई 33% यूरिया और शेष पोटाश का छिड़काव करें।
- **सूक्ष्म पोषक तत्व**: {soil_hi} में जिंक की कमी होने पर 10 किलो जिंक सल्फेट प्रति एकड़ या 0.5% जिंक का पर्णीय छिड़काव करें।

---
#### 💡 कृषि वैज्ञानिक की महत्वपूर्ण सलाह:
- सूखी मिट्टी में कभी भी यूरिया न डालें; पहले हल्की सिंचाई करें।
- यूरिया को दो से तीन बार में बाँटकर देने से पौधों को 30-40% अधिक लाभ मिलता है।
- 5 किलो ट्राइकोडर्मा को 100 किलो सड़ी गोबर की खाद में मिलाकर खेत में बिखेरें।"""

    # 4. Yellow leaves
    if any(k in q_lower for k in [
        "yellow", "chlorosis", "pale", "peela", "discolor", "yellowing", "पीली", "पीला", "पत्तियां पीली"
    ]):
        return f"""### 🔍 {crop_hi} में पत्तियों का पीलापन - कारण एवं वैज्ञानिक निदान

**{soil_hi}** में पत्तियों का पीला पड़ना (क्लोरोसिस) सामान्यतः इन चार कारणों से होता है:

1. **नाइट्रोजन की कमी**:
   - *लक्षण*: पुरानी (निचली) पत्तियां पहले नोक से 'V' आकार में पीली होती हैं।
   - *उपचार*: यूरिया की टॉप-ड्रेसिंग करें या 1.5% यूरिया (15-20 ग्राम प्रति लीटर पानी) का पत्तियों पर छिड़काव करें।

2. **जिंक या लोहे की कमी** ({soil_hi} में आम):
   - *लक्षण*: नई ऊपरी पत्तियां पीली होती हैं जबकि उनकी नसें हरी रहती हैं।
   - *उपचार*: चिलेटेड जिंक (1 ग्राम/लीटर) या फेरस सल्फेट (5 ग्राम/लीटर + 2 ग्राम नींबू रस) का स्प्रे करें।

3. **जड़ों में जलभराव या अधिक नमी**:
   - *लक्षण*: पौधे मुरझाते हैं और पत्तियां पीली होने लगती हैं।
   - *उपचार*: खेत से अतिरिक्त पानी निकालें। जड़ों के पास ट्राइकोडर्मा विरिडी (5 ग्राम/लीटर) का छिड़काव करें।

4. **विषाणु रोग (पत्ती मोड़क / मोज़ेक)**:
   - *लक्षण*: पीली व हरी चितकबरी पत्तियां और पत्तियों का मुड़ना।
   - *उपचार*: रसचूसक कीटों (सफेद मक्खी, माहू) को नियंत्रित करने के लिए 10,000 ppm नीम तेल (2.5 मिली/लीटर) स्प्रे करें।

📸 *सुझाव: अपने डैशबोर्ड पर **फसल जांच** टूल का उपयोग करके प्रभावित पत्ती की फोटो अपलोड करके तत्काल एआई निदान प्राप्त करें!*"""

    # 5. Pests
    if any(k in q_lower for k in [
        "pest", "insect", "bug", "worm", "aphid", "caterpillar", "borer", "keeda", "कीट", "कीड़ा", "इल्ली", "माहू"
    ]):
        return f"""### 🛡️ {crop_hi} के लिए एकीकृत कीट प्रबंधन (IPM)

आपकी **{crop_hi}** फसल को कीटों से सुरक्षित रखने के प्रमुख उपाय:

#### 🌿 प्राकृतिक एवं जैविक प्रथम रक्षा पंक्ति:
1. **नीम तेल का स्प्रे**: 10,000 ppm नीम तेल (Azadirachtin) 2.5-3.0 मिली प्रति लीटर पानी में थोड़ा सर्फ/साबुन मिलाकर छिड़कें।
2. **फेरोमोन व चिपचिपे ट्रैप**: प्रति एकड़ 4-5 फेरोमोन ट्रैप और 8-10 पीले/नीले स्टिकी कार्ड लगाएं।
3. **जैविक कीटनाशक**: इल्लियों और रसचूसक कीटों के लिए ब्युवेरिया बैसियाना (*Beauveria bassiana* @ 5 ग्राम/लीटर) शाम के समय स्प्रे करें।

⚠️ *सावधानी: रासायनिक कीटनाशक का छिड़काव सुबह 7-10 बजे या शाम 4-6 बजे ही करें, तेज हवा या बारिश से पहले न करें।*"""

    # 6. Schemes
    if any(k in q_lower for k in [
        "scheme", "subsidy", "pm kisan", "kcc", "योजना", "सब्सिडी", "बीमा", "कर्ज"
    ]):
        return f"""### 🏛️ किसानों के लिए प्रमुख सरकारी कृषि योजनाएं

1. **प्रधानमंत्री किसान सम्मान निधि (PM-Kisan)**:
   - सभी किसान परिवारों को प्रति वर्ष **₹6,000** की सहायता (3 किस्तों में ₹2,000)।
   - पोर्टल: `pmkisan.gov.in` पर ई-केवाईसी और बैंक खाता आधार से लिंक होना अनिवार्य।

2. **प्रधानमंत्री फसल बीमा योजना (PMFBY)**:
   - प्राकृतिक आपदा, सूखा, बाढ़ या कीटों से फसल नष्ट होने पर वित्तीय सुरक्षा।
   - न्यूनतम प्रीमियम: खरीफ फसलों के लिए **2%**, रबी के लिए **1.5%**।

3. **किसान क्रेडिट कार्ड (KCC)**:
   - 4% रियायती ब्याज दर पर ₹3,00,000 तक का अल्पकालिक कृषि ऋण।

4. **ड्रिप व स्प्रिंकलर सिंचाई सब्सिडी (Per Drop More Crop)**:
   - सूक्ष्म सिंचाई उपकरणों की स्थापना पर **45% से 70%** तक सरकारी अनुदान।"""

    # Fallback / General
    return f"""### 🌾 {crop_hi} फसल के लिए कृषि सेतु सलाह

नमस्कार! आपके प्रश्न **"{query}"** के संदर्भ में:

📍 **खेत विवरण**: {crop_hi} • {area} एकड़ • {location} • {soil_hi} • {irrigation}

1. **फसल अवलोकन**:
   - सुबह के समय खेत का नियमित मुआयना करें। पत्तियों की निचली सतह और तने के पास कीट या फफूंद के शुरुआती लक्षणों की जांच करें।
2. **मिट्टी व जल प्रबंधन**:
   - **{soil_hi}** में संतुलित नमी बनाए रखें। न तो खेत को सूखने दें और न ही जड़ों में पानी जमा होने दें।
3. **संतुलित पोषण**:
   - {irrigation} के अनुसार ही खाद दें और अतिरिक्त रासायनिक नाइट्रोजन के अधिक उपयोग से बचें।

💬 *आप खाद की खुराक, पीली पत्तियों के इलाज या कीट नियंत्रण के बारे में विस्तार से पूछ सकते हैं!*"""

def build_bengali_response(
    query: str,
    q_lower: str,
    active_crop: str,
    location: str,
    soil: str,
    irrigation: str,
    area: str,
    analysis_context: Optional[Dict[str, Any]] = None
) -> str:
    """Localized Bengali Agronomic Expert Response Engine."""
    crop_bn = LOCAL_CROP_BN.get(active_crop, active_crop)
    soil_bn = LOCAL_SOIL_BN.get(soil, soil)

    # 1. Report follow-up
    if analysis_context and any(k in q_lower for k in [
        "now", "treatment", "report", "spread", "cure", "remedy", "what to do", 
        "should i do", "scan", "diagnosis", "recommendation", "doctor", "step",
        "চিকিৎসা", "প্রতিকার", "ছড়াবে", "রিপোর্ট", "রোগ", "উপায়"
    ]):
        issue = analysis_context.get("primary_issue") or analysis_context.get("overall_field_status") or "পাতার সমস্যা"
        severity = analysis_context.get("severity", "মাঝারি")
        score = analysis_context.get("overall_health_score") or analysis_context.get("health_score", 80)
        actions = analysis_context.get("recommended_actions") or analysis_context.get("recommendations") or []
        actions_list = "\n".join([f"- {a}" for a in actions[:4]]) if actions else "- জৈব বালাইনাশক প্রয়োগ করুন এবং স্থানীয় কৃষি অফিসে যোগাযোগ করুন।"

        if any(k in q_lower for k in ["spread", "infect", "nearby", "neighbor", "ছড়াবে", "সংক্রমণ"]):
            return f"""### 🌾 {crop_bn} ফসলে রোগ ছড়িয়ে পড়া প্রতিরোধের উপায়

আপনার সাম্প্রতিক স্ক্যানে **{issue}** শনাক্ত হয়েছে:

- **রোগ ছড়ানোর ঝুঁকি**: **{severity}** মাত্রার ঝুঁকি (আর্দ্র ও মেঘলা আবহাওয়ায় ছত্রাকের বিস্তার দ্রুত বাড়ে)।
- **প্রধান প্রতিরোধমূলক পদক্ষেপ**:
  ১. **কাজের সরঞ্জাম জীবাণুমুক্ত করুন**: কাঁচি বা স্প্রেয়ার ব্যবহারের পর ১০% ব্লিচ বা কপার সালফেট দিয়ে ধুয়ে নিন।
  ২. **ভেজা মাঠে চলাচল এড়িয়ে চলুন**: ছত্রাকের স্পোর ভেজা জামাকাপড় ও জুতোর মাধ্যমে সুস্থ গাছে ছড়ায়।
  ৩. **প্রতিরোধমূলক স্প্রে**: আক্রান্ত এলাকার চারপাশে ২ মিটার সুরক্ষা বলয় তৈরি করে ট্রাইকোডার্মা ভিরিডি (৫ গ্রাম/লিটার) বা কপার অক্সিক্লোরাইড ৫০% WP (২.৫ গ্রাম/লিটার) স্প্রে করুন।
  ৪. **আলো-বাতাসের প্রবাহ**: নিচের মরা বা পচা পাতা ছেঁটে দিন যাতে জমিতে রোদ ও বাতাস চলাচল করতে পারে।

💡 *আশেপাশের গাছগুলো প্রতি ৪৮ ঘণ্টা অন্তর পর্যবেক্ষণ করুন।*"""

        if any(k in q_lower for k in ["organic", "natural", "bio", "home remedy", "desi", "জৈব", "প্রাকৃতিক"]):
            return f"""### 🌿 জৈব ও প্রাকৃতিক প্রতিকার: {issue}

আপনার **{crop_bn}** ফসলের জন্য পরিবেশবান্ধব প্রাকৃতিক ব্যবস্থাপনা:

১. **নিম তেলের স্প্রে**: কোল্ড-প্রেসড নিম তেল (১০,০০০ পিপিএম) প্রতি লিটার জলে ২.৫-৩ মিলি এবং সামান্য ডিটারজেন্ট/তরল সাবান মিশিয়ে স্প্রে করুন।
২. **উপকারী ছত্রাক প্রয়োগ**: ট্রাইকোডার্মা ভিরিডি (*Trichoderma viride*) অথবা সিউডোমোনাস প্রতি লিটার জলে ৫ গ্রাম মিশিয়ে সকালে প্রয়োগ করুন।
৩. **টক ঘোল ও তামার দ্রবণ**: ১০-১২ দিনের পুরনো টক ঘোলের মধ্যে তামার টুকরো রেখে, ১:১০ অনুপাতে জল মিশিয়ে স্প্রে করলে এটি চমৎকার প্রাকৃতিক ছত্রাকনাশক হিসেবে কাজ করে।
৪. **জীবামৃত প্রয়োগ**: মাটির উর্বরতা ও উপকারী জীবাণু বৃদ্ধিতে একর প্রতি ১০০ লিটার জীবামৃত গোড়ায় দিন।

⚠️ *ট্রাইকোডার্মার মতো জৈব জীবাণু স্প্রে করার ৪ দিন আগে বা পরে কোনো রাসায়নিক কীটনাশক প্রয়োগ করবেন না।*"""

        return f"""### 📋 ফিল্ড ডাক্তার কর্মপরিকল্পনা: {issue}

আপনার **{crop_bn}** ফসলের সাম্প্রতিক পরীক্ষার ফলাফলের ভিত্তিতে:
- **নির্ণীত রোগ**: {issue} ({severity} তীব্রতা • স্বাস্থ্য স্কোর: {score}%)
- **প্রস্তাবিত পদক্ষেপ**:
{actions_list}

#### 💧 সেচ ও জমি ব্যবস্থাপনা:
- পাতায় দাগ বা ছত্রাক থাকা অবস্থায় স্প্রিঙ্কলার সেচ দেওয়া এড়িয়ে চলুন।
- জমিতে অতিরিক্ত জল জমতে দেবেন না এবং সঠিক ড্রেনেজ বজায় রাখুন।
- রাসায়নিক ছত্রাকনাশক ব্যবহারের সময় মুখে মাস্ক ও হাতে গ্লাভস পরুন এবং ১০-১৪ দিনের সুরক্ষা সময়সীমা (PHI) মেনে চলুন।"""

    # 2. Greetings
    if any(q_lower.startswith(g) or q_lower == g for g in [
        "hi", "hello", "namaste", "pranam", "hey", "kisan", "help",
        "নমস্কার", "সালাম", "হ্যালো", "সাহায্য"
    ]):
        return f"""### 🙏 নমস্কার! আমি কৃষিসেতু এআই

আমি আপনার ব্যক্তিগত কৃষি বিজ্ঞানী ও ফসল পরামর্শক, আপনার **{location}**-এর **{area} একর {crop_bn} জমি** ({soil_bn}, {irrigation})-এর জন্য প্রস্তুত।

আমি আপনাকে এখনই নিম্নলিখিত বিষয়গুলিতে সাহায্য করতে পারি:
১. **🧪 সার ও পুষ্টি ব্যবস্থাপনা**: {crop_bn}-এর জন্য N-P-K এর সঠিক পরিমাণ ও প্রয়োগ সময়।
২. **🐛 কীটপতঙ্গ ও রোগ প্রতিরোধ**: নিম তেল, ফেরোমোন ট্র্যাপ ও নিরাপদ কীটনাশক ব্যবহারের নিয়ম।
৩. **💧 সেচ ব্যবস্থাপনা**: {irrigation} অনুযায়ী সেচ দেওয়ার সঠিক সময়।
৪. **🌾 বীজ বপন ও আগাছা দমন**: উন্নত বীজ শোধন ও আগাছানাশক প্রয়োগ।
৫. **🏛️ সরকারি কৃষি প্রকল্প**: পিএম-কিষাণ, ফসল বীমা যোজনা ও কিষাণ ক্রেডিট কার্ড (KCC)।

💬 *আপনার যেকোনো প্রশ্ন সহজ ভাষায় জিজ্ঞাসা করুন! যেমন:*
- *"{crop_bn} ফসলের জন্য সুষম সারের মাত্রা কী?"*
- *"গাছের নিচের পাতা হলুদ হয়ে যাচ্ছে কেন?"*
- *"জৈব পদ্ধতিতে পোকা দমন করব কীভাবে?"*"""

    # 3. Fertilizer
    if any(k in q_lower for k in [
        "fertilizer", "urea", "dap", "potash", "npk", "nutrition", "khad", 
        "micronutrient", "zinc", "boron", "nitrogen", "সার", "ইউরিয়া", "পটাশ", "ডিএপি"
    ]):
        return f"""### 🌾 {crop_bn} ফসলের জন্য সুষম সার ও পুষ্টি ব্যবস্থাপনা

📍 **জমির বিবরণ**: {location} • {soil_bn} • {area} একর • {irrigation}

#### 📋 সারের প্রয়োগ সময়সূচী:
- **জমি তৈরির সময় (বেসাল ডোজ)**: সম্পূর্ণ টিএসপি/ডিএপি, ৫০% এমওপি (পটাশ) এবং ইউরিয়ার এক-তৃতীয়াংশ শেষ চাষের সময় মাটিতে মিশিয়ে দিন।
- **প্রথম উপরিপ্রয়োগ (২০-২৫ দিন পর)**: চারা বৃদ্ধি বা কুশি বেরোনোর সময় ইউরিয়ার দ্বিতীয় কিস্তি জমিতে পর্যাপ্ত রস থাকা অবস্থায় প্রয়োগ করুন।
- **দ্বিতীয় উপরিপ্রয়োগ (৪০-৪৫ দিন পর)**: ফুল বা শিষ আসার ঠিক আগে ইউরিয়ার শেষ কিস্তি ও বাকি পটাশ প্রয়োগ করুন।
- **অনুখাদ্য প্রয়োগ**: {soil_bn}-এ জিংকের অভাব দেখা দিলে একর প্রতি ৫-১০ কেজি জিংক সালফেট অথবা চিলেটেড জিংক (১ গ্রাম/লিটার) স্প্রে করুন।

---
#### 💡 কৃষি বিজ্ঞানীদের গুরুত্বপূর্ণ পরামর্শ:
- শুকনো জমিতে কখনোই ইউরিয়া ছড়াবেন না; জমিতে হালকা আর্দ্রতা বা রস নিশ্চিত করুন।
- ইউরিয়া ভাগ করে দিলে সারের অপচয় কমে এবং কার্যকারিতা ৩০-৪০% বৃদ্ধি পায়।
- বিঘাপ্রতি ২-৩ কেজি ট্রাইকোডার্মা ও পচা গোবর সার মাটিতে প্রয়োগ করলে মাটির উর্বরতা ও ছত্রাক প্রতিরোধ ক্ষমতা বাড়ে।"""

    # 4. Yellow leaves
    if any(k in q_lower for k in [
        "yellow", "chlorosis", "pale", "peela", "discolor", "yellowing", "হলুদ", "পাতা হলুদ", "হলদে"
    ]):
        return f"""### 🔍 {crop_bn} ফসলে পাতা হলুদ হওয়ার কারণ ও প্রতিকার

**{soil_bn}**-এ পাতার ক্লোরোসিস বা হলুদ ভাব সাধারণত চারটি কারণে দেখা দেয়:

১. **নাইট্রোজেনের ঘাটতি**:
   - *লক্ষণ*: গাছের নিচের পুরনো পাতাগুলো ডগা থেকে ইংরেজি 'V' আকারে হলুদ হতে শুরু করে।
   - *প্রতিকার*: ইউরিয়া সারের উপরিপ্রয়োগ করুন অথবা ১.৫% ইউরিয়া দ্রবণ (প্রতি লিটার জলে ১৫-২০ গ্রাম) স্প্রে করুন।

২. **জিংক বা আয়রনের ঘাটতি** ({soil_bn}-এ খুব সাধারণ):
   - *লক্ষণ*: কচি ডগা ও ওপরের পাতা হলুদ হয়, কিন্তু পাতার শিরাগুলো গাঢ় সবুজ থাকে।
   - *প্রতিকার*: চিলেটেড জিংক (১ গ্রাম/লিটার) অথবা ফেরাস সালফেট দ্রবণ স্প্রে করুন।

৩. **শিকড়ে অতিরিক্ত জল জমা বা ড্রেনেজের অভাব**:
   - *লক্ষণ*: পাতা ফ্যাকাসে হলুদ হয়ে যায় এবং গাছ ঝিমিয়ে পড়ে।
   - *প্রতিকার*: দ্রুত জমির অতিরিক্ত জল নিষ্কাশনের ব্যবস্থা করুন এবং গোড়ায় ট্রাইকোডার্মা স্প্রে করুন।

৪. **ভাইরাসজনিত মোজাইক বা লিফ কার্ল রোগ**:
   - *লক্ষণ*: পাতায় হলুদ-সবুজ ছোপ ছোপ দাগ এবং পাতা কুকড়ে যাওয়া।
   - *প্রতিকার*: সাদা মাছি ও জাবপোকা দমনে নিম তেল (১০,০০০ পিপিএম, প্রতি লিটারে ২.৫-৩ মিলি) স্প্রে করুন।

📸 *পরামর্শ: ড্যাশবোর্ডের **পাতা পরীক্ষা** টুল দিয়ে আক্রান্ত পাতার ছবি তুলে তাৎক্ষণিক সঠিক রোগ নির্ণয় করতে পারেন!*"""

    # 5. Pests
    if any(k in q_lower for k in [
        "pest", "insect", "bug", "worm", "aphid", "caterpillar", "borer", "পোকা", "কীটপতঙ্গ", "লেদা"
    ]):
        return f"""### 🛡️ {crop_bn} ফসলের সমন্বিত বালাই দমন (IPM)

আপনার **{crop_bn}** ফসলকে পোকা-মাকড়ের আক্রমণ থেকে রক্ষার কার্যকর উপায়:

#### 🌿 পরিবেশবান্ধব ও জৈব প্রতিকার:
১. **নিম তেল স্প্রে**: কোল্ড-প্রেসড নিম তেল (১০,০০০ পিপিএম) প্রতি লিটার জলে ২.৫-৩ মিলি এবং সামান্য ডিটারজেন্ট মিশিয়ে স্প্রে করুন।
২. **ফেরোমোন ও আঠালো ফাঁদ**: একর প্রতি ৪-৫টি ফেরোমোন ট্র্যাপ এবং ৮-১০টি হলুদ/নীল আঠালো ফাঁদ পাতুন।
৩. **উপকারী জীবাণু কীটনাশক**: লেদা পোকা ও চোষক পোকার জন্য বোভেরিয়া ব্যাসিয়ানা (*Beauveria bassiana* ৫ গ্রাম/লিটার) বিকেলে স্প্রে করুন।

⚠️ *সতর্কতা: রাসায়নিক কীটনাশক প্রয়োগের সময় মুখে মাস্ক ও হাতে গ্লাভস পরুন এবং ফসল তোলার নির্দিষ্ট সময়সীমা (PHI) মেনে চলুন।*"""

    # 6. Schemes
    if any(k in q_lower for k in [
        "scheme", "subsidy", "pm kisan", "kcc", "প্রকল্প", "যোজনা", "বীমা", "ঋণ"
    ]):
        return f"""### 🏛️ কৃষকদের জন্য গুরুত্বপূর্ণ সরকারি কৃষি প্রকল্প

১. **প্রধানমন্ত্রী কিষাণ সম্মান নিধি (PM-Kisan)**:
   - কৃষক পরিবারকে বছরে **₹৬,০০০** সহায়তা (প্রতি কিস্তিতে ₹২,০০০ করে ৩ কিস্তি)।
   - ই-কেওয়াইসি এবং ব্যাংক অ্যাকাউন্ট আধার লিংক থাকা আবশ্যক (`pmkisan.gov.in`)।

২. **প্রধানমন্ত্রী ফসল বীমা যোজনা (PMFBY)**:
   - প্রাকৃতিক দুর্যোগ, বন্যা বা খরায় ফসল নষ্টের আর্থিক ক্ষতিপূরণ।
   - ন্যূনতম প্রিমিয়াম: খরিফ ফসলের জন্য **২%**, রবি ফসলের জন্য **১.৫%**।

৩. **কিষাণ ক্রেডিট কার্ড (KCC)**:
   - মাত্র ৪% সুবিধাজনক সুদের হারে ₹৩,০০,০০০ পর্যন্ত স্বল্পমেয়াদী কৃষি ঋণ।

৪. **ড্রিপ ও স্প্রিঙ্কলার সেচ অনুদান (Per Drop More Crop)**:
   - আধুনিক সেচ ব্যবস্থা স্থাপনের জন্য রাজ্য কৃষি দপ্তর থেকে **৪৫% থেকে ৭০%** পর্যন্ত সরকারি ভর্তুকি।"""

    # Fallback / General
    return f"""### 🌾 {crop_bn} ফসলের জন্য কৃষিসেতু পরামর্শ

নমস্কার! আপনার প্রশ্ন **"{query}"** এর প্রেক্ষিতে:

📍 **জমির বিবরণ**: {crop_bn} • {area} একর • {location} • {soil_bn} • {irrigation}

১. **নিয়মিত জমি পরিদর্শন**:
   - সকালে ফসল ভালোভাবে পর্যবেক্ষণ করুন। পাতার নিচের দিক ও গাছের গোড়ায় পোকা বা ছত্রাকের উপস্থিতি আছে কিনা খেয়াল রাখুন।
২. **মাটি ও জলের ভারসাম্য**:
   - **{soil_bn}**-এ সঠিক আর্দ্রতা বজায় রাখুন। শিকড়ে যেন জল জমে না থাকে আবার মাটি যেন অতিরিক্ত শুকিয়ে ফেটে না যায়।
৩. **সুষম পুষ্টি প্রদান**:
   - {irrigation} অনুযায়ী সার দিন এবং অতিরিক্ত ইউরিয়া প্রয়োগ থেকে বিরত থাকুন।

💬 *আপনি সারের মাত্রা, পাতা হলুদ হওয়ার প্রতিকার বা পোকা দমন সম্পর্কে নির্দিষ্ট প্রশ্ন করতে পারেন!*"""

def build_expert_response(
    query: str,
    crop: str,
    location: str,
    soil: str,
    irrigation: str,
    area: str,
    analysis_context: Optional[Dict[str, Any]] = None,
    language: str = "en"
) -> str:
    """Intelligent Botanical & Agronomic Expert System Engine (Offline Fallback)."""
    q_lower = query.lower()
    lang_code = (language or "en").lower().strip()

    # 1. Detect if query explicitly mentions a specific crop
    crop_key = None
    for k in CROP_AGRONOMY_DATA.keys():
        if k.lower() in q_lower:
            crop_key = k
            break

    # Otherwise fallback to farm registered crop
    if not crop_key:
        for k in CROP_AGRONOMY_DATA.keys():
            if k.lower() in crop.lower():
                crop_key = k
                break

    if not crop_key:
        crop_key = "Rice" if ("rice" in crop.lower() or "paddy" in crop.lower()) else "Vegetables"

    crop_data = CROP_AGRONOMY_DATA.get(crop_key, CROP_AGRONOMY_DATA["Vegetables"])
    active_crop = crop_key if (crop_key.lower() in q_lower) else (crop if crop and crop != "Crop" else crop_key)

    # Route to specialized localized language engines if requested
    if lang_code in ["hi", "hindi"]:
        return build_hindi_response(query, q_lower, active_crop, location, soil, irrigation, area, analysis_context)
    if lang_code in ["bn", "bengali", "bangla"]:
        return build_bengali_response(query, q_lower, active_crop, location, soil, irrigation, area, analysis_context)

    # 1. SPECIFIC REPORT ANALYSIS FOLLOW-UP
    # Only if analysis_context is genuinely present AND user query is about the report
    if analysis_context and any(k in q_lower for k in [
        "now", "treatment", "report", "spread", "cure", "remedy", "what to do", 
        "should i do", "scan", "diagnosis", "recommendation", "doctor", "step"
    ]):
        issue = (
            analysis_context.get("primary_issue")
            or analysis_context.get("overall_field_status")
            or "Foliar Stress"
        )
        health = (
            analysis_context.get("overall_health_status")
            or analysis_context.get("overall_health")
            or "Observation"
        )
        severity = analysis_context.get("severity", "Moderate")
        score = analysis_context.get("overall_health_score") or analysis_context.get("health_score", 80)
        
        # Read recommendations safely across all schema variations
        actions = (
            analysis_context.get("recommended_actions")
            or analysis_context.get("recommendations")
            or analysis_context.get("chemical_treatments")
            or []
        )
        symptoms = analysis_context.get("symptoms", [])

        actions_list = "\n".join([f"- {a}" for a in actions[:4]]) if actions else "- Follow standard organic bio-control and consult local KVK extension officers."
        report_crop = analysis_context.get("crop_name") or active_crop
        symptoms_str = ", ".join(symptoms[:3]) if symptoms else "Visual foliar stress observed"

        # Check sub-intent
        if any(k in q_lower for k in ["spread", "infect", "nearby", "neighbor"]):
            return f"""### 🌾 Disease Spread Prevention for {report_crop}

Regarding your recent scan showing **{issue}**:

- **Spread Risk**: {"HIGH" if severity.lower() in ["high", "severe"] else "MODERATE"} under humid conditions.
- **Key Prevention Steps**:
  1. **Disinfect Tools**: Clean secateurs and sprayers with a 10% bleach or copper sulfate solution between rows.
  2. **Do Not Walk Through Wet Fields**: Pathogen spores (especially fungal blights and bacterial oozes) hitchhike on farmers' clothes and wet footwear.
  3. **Isolation Buffer**: Create a 2-meter spray barrier around the infected plot with a preventive bio-fungicide like *Trichoderma viride* (5g/L) or Copper Oxychloride 50% WP (2.5g/L).
  4. **Canopy Aeration**: Prune lowest touching foliage to prevent rain splash dispersal.

💡 *Inspect neighboring rows every 48 hours for early lesion development.*"""

        if any(k in q_lower for k in ["organic", "natural", "bio", "home remedy", "desi"]):
            return f"""### 🌿 Organic Treatment Protocol: {issue}

Recommended organic management for your **{report_crop}**:

1. **Neem Formulation**: Spray cold-pressed Neem Oil (10,000 ppm) @ 2.5 to 3 ml per liter of water mixed with 1 ml liquid soap as an emulsifier.
2. **Bio-Control Antagonist**: Apply *Trichoderma viride* or *Pseudomonas fluorescens* @ 5g/L water early in the morning.
3. **Traditional Fermented Spray**: Use fermented butter-milk (sour chaas) mixed with copper foil extract diluted 1:10 with water as a natural foliar anti-fungal spray.
4. **Soil Health Boost**: Drench root zones with *Jeevamrut* (100L/acre) or compost tea to enhance beneficial soil microflora.

⚠️ *Avoid chemical sprays for 4 days before or after applying living bio-agents like Trichoderma.*"""

        # General report treatment
        return f"""### 📋 Field Doctor Action Plan: {issue}

Based on your recent diagnostic scan for **{report_crop}**:
- **Diagnosis**: {issue} ({severity} Severity • Health Score: {score}%)
- **Status**: {health}
- **Symptoms Observed**: {symptoms_str}

#### 🛠️ Immediate Action Steps:
{actions_list}

#### 💧 Field Water & Care Management:
- Avoid overhead sprinkler irrigation while lesions are active to prevent splash propagation.
- Maintain field bunds and ensure uniform surface drainage.
- If using chemical fungicides, observe a strict 10-14 day Pre-Harvest Interval (PHI) and wear protective mask and gloves."""

    # 2. GREETINGS & INTRODUCTIONS
    if any(q_lower.startswith(g) or q_lower == g for g in [
        "hi", "hello", "namaste", "pranam", "hey", "hola", "kisan", 
        "who are you", "what can you do", "help", "good morning", "good evening"
    ]):
        return f"""### 🙏 Namaste! I am KrishiSetu AI

I am your personal agricultural scientist and agronomy companion, configured for your **{area}-acre {active_crop} farm** in **{location}** ({soil}, {irrigation}).

Here are key areas I can assist you with right now:

1. **🧪 Fertilizer & Nutrition**: Exact N-P-K dosages, basal vs split schedules, and micronutrient corrections for {active_crop}.
2. **🐛 Pest & Disease Defense**: Organic remedies (Neem, *Trichoderma*) and safe chemical interventions for crop protection.
3. **💧 Irrigation Scheduling**: Critical growth water stages and conservation advice for {irrigation}.
4. **🌾 Sowing & Weed Care**: Seed rates, bio-seed treatment, and herbicide timing.
5. **🏛️ Government Schemes**: PM-Kisan, Fasal Bima Yojana, and Kisan Credit Card (KCC) benefits.

💬 *Ask me any question in plain language! For example:*
- *"What is the exact fertilizer dose for my {active_crop}?"*
- *"Why are the bottom leaves turning yellow?"*
- *"How to manage insect borers organically?"*"""

    # 3. FERTILIZER & NUTRIENT MANAGEMENT
    if any(k in q_lower for k in [
        "fertilizer", "urea", "dap", "potash", "npk", "nutrition", "khad", 
        "micronutrient", "zinc", "boron", "nitrogen", "phosphorus", "potassium", 
        "dose", "dosage", "fym", "manure", "vermicompost"
    ]):
        fert_guidance = crop_data.get("fertilizer", "")
        soil_note = SOIL_KNOWLEDGE.get(soil, "")
        return f"""### 🌾 Recommended Fertilizer Management for {active_crop}

📍 **Farm Context**: {location} • {soil} • {area} acres • {irrigation}

#### 📋 Nutrient Schedule:
{fert_guidance}

---
#### 🧪 Soil-Specific Adaptation ({soil}):
{soil_note}

#### 💡 Agronomist Application Rules:
- **Never apply Urea in dry soil**: Always ensure adequate soil moisture before top-dressing nitrogen.
- **Split Applications**: Splitting nitrogen into 2-3 split doses increases nitrogen use efficiency (NUE) by 30-40%.
- **Soil Health**: Mix 5 kg of *Trichoderma* or *VAM* with 100 kg decomposed cow dung manure before field broadcasting."""

    # 4. YELLOW LEAVES & CHLOROSIS
    if any(k in q_lower for k in [
        "yellow", "chlorosis", "pale", "peela", "discolor", "yellowing"
    ]):
        return f"""### 🔍 Diagnosis: Yellowing Leaves in {active_crop}

Leaf yellowing (chlorosis) in **{soil}** generally stems from one of four distinct causes. Check which pattern matches your crop:

1. **Nitrogen (N) Deficiency**:
   - *Symptom*: Older (lowest) leaves turn yellow first, starting from the leaf tip and advancing inward in a 'V' shape.
   - *Remedy*: Top-dress Urea or apply a foliar spray of 1.5-2.0% Urea solution (15-20g per liter water).

2. **Zinc (Zn) or Iron (Fe) Deficiency** (Frequent in {soil}):
   - *Symptom*: Newer upper leaves turn pale yellow while leaf veins remain distinctly green (interveinal chlorosis).
   - *Remedy*: Foliar spray of Chelated Zinc (EDTA Zn 12% @ 1g/L) or Ferrous Sulfate (FeSO4 @ 5g/L + 2g citric acid).

3. **Root Waterlogging or Poor Drainage**:
   - *Symptom*: Leaves turn pale green to yellow, and the plant wilts even though the soil is wet.
   - *Remedy*: Drain excess surface water immediately. Drench root zones with *Trichoderma viride* (5g/L) or Carbendazim (1g/L).

4. **Viral Disease (Leaf Curl / Mosaic)**:
   - *Symptom*: Patchy yellow and green mosaic pattern accompanied by leaf curling or stunted growth.
   - *Remedy*: Control vector insects (whiteflies and aphids) with Neem Oil (10,000 ppm) or Thiamethoxam 25% WG (0.3g/L).

📸 *Tip: You can also use the **Check Crop** tool on your dashboard to take a photo of the affected leaf for an instant AI disease scan!*"""

    # 5. PESTS, INSECTS & WORMS (IPM)
    if any(k in q_lower for k in [
        "pest", "insect", "bug", "worm", "aphid", "caterpillar", "borer", 
        "whitefly", "thrips", "mite", "armyworm", "bollworm", "keeda", "hopper", "termite"
    ]):
        pest_guidance = crop_data.get("pests", "")
        return f"""### 🛡️ Integrated Pest Management (IPM) for {active_crop}

For protecting your **{active_crop}** against insect pests:

#### 🎯 Crop-Specific Pest Guidelines:
{pest_guidance}

---
#### 🌿 Universal Organic & Biological First Line:
1. **Cold-Pressed Neem Oil**: Spray 10,000 ppm Azadirachtin @ 2.5-3.0 ml/L of water with mild surfactant (liquid soap).
2. **Pheromone & Sticky Traps**: Install 4-5 pheromone traps and 8-10 yellow/blue sticky traps per acre for early pest detection.
3. **Bio-Pesticides**: Spray *Beauveria bassiana* (5g/L) for caterpillars and sucking pests during humid or evening hours.

⚠️ *Safety Reminder: If applying synthetic insecticides, spray in early morning or late afternoon, avoid windy conditions, and observe the Pre-Harvest Interval (PHI).*"""

    # 6. DISEASES & PATHOLOGY
    if any(k in q_lower for k in [
        "disease", "blight", "blast", "rust", "mildew", "rot", "canker", 
        "fungus", "bacterial", "damping", "anthracnose", "scab", "smut", "mosaic", "wilt"
    ]):
        disease_guidance = crop_data.get("diseases", "")
        return f"""### 🩺 Crop Disease Management for {active_crop}

Diagnosis and scientific remedies for common pathologies affecting **{active_crop}**:

#### 🔬 Primary Crop Diseases:
{disease_guidance}

---
#### 🛡️ Standard Dual-Defense Treatment Protocol:
- **Preventive Bio-Fungicide**: Spray *Trichoderma viride* or *Pseudomonas fluorescens* @ 5g/liter at first signs of cloudiness and high humidity (>80%).
- **Broad-Spectrum Protective Fungicide**: Apply Mancozeb 75% WP @ 2.5 g/L or Copper Oxychloride 50% WP @ 2.5 g/L.
- **Systemic Curative Fungicide**: If lesions are actively expanding, apply Azoxystrobin + Difenoconazole (Amistar Top) @ 1 ml/L or Carbendazim 12% + Mancozeb 63% WP (Saaf) @ 2 g/L.

💡 *Always avoid overhead sprinkler irrigation when fungal spots are active to prevent spore dispersal.*"""

    # 7. IRRIGATION & WATER MANAGEMENT
    if any(k in q_lower for k in [
        "irrigate", "irrigation", "water", "watering", "dry", "moisture", 
        "pani", "panni", "sinchai", "sinchayi", "rain", "drought", "drainage", "flood", "drip", "sprinkler"
    ]):
        irrig_guidance = crop_data.get("irrigation", "")
        irrig_method_info = IRRIGATION_KNOWLEDGE.get(irrigation, IRRIGATION_KNOWLEDGE["Tube Well"])
        return f"""### 💧 Irrigation Guidance for {active_crop}

📍 **Method**: {irrigation} • **Soil**: {soil} • **Farm Area**: {area} acres

#### 🕒 Critical Growth Watering Stages for {active_crop}:
{irrig_guidance}

---
#### ⚙️ Irrigation System Management ({irrigation}):
{irrig_method_info}

#### 💡 Water-Saving Agronomic Best Practices:
- **Moisture Check**: Squeeze a handful of soil from root depth (6 inches). If it forms a firm ball without releasing muddy water, moisture is adequate.
- **Avoid Stress at Flowering**: Water deficit during flower bud development and pollination leads to severe flower abortion and sterile heads.
- **Drainage**: Ensure shallow surface drainage ditches along the low edge of your field to avoid root rot from standing water."""

    # 8. SOWING, SEEDS & PLANTING
    if any(k in q_lower for k in [
        "sow", "sowing", "seed", "variety", "plant", "spacing", "germination", 
        "nursery", "transplant", "bij", "beej", "depth", "season"
    ]):
        sowing_guidance = crop_data.get("sowing", "")
        return f"""### 🌱 Sowing, Seed & Nursery Advisory for {active_crop}

Optimal planting recommendations for **{active_crop}** in **{location}**:

#### 🌾 Sowing & Seed Parameters:
{sowing_guidance}

---
#### 🛡️ Crucial Seed Treatment (Beej Sanskar):
1. **Biological Treatment**: Coat seeds with *Trichoderma viride* @ 5-10 g/kg seed or *Pseudomonas fluorescens* @ 10 g/kg seed to prevent seed-borne and soil-borne fungal diseases.
2. **Chemical Alternative**: Carboxin + Thiram (Vitavax) @ 2.5 g/kg seed or Carbendazim @ 2 g/kg seed.
3. **Bio-fertilizer Inoculation**: For legumes/pulses, treat with *Rhizobium* culture; for cereals, treat with *Azotobacter* or *Azospirillum* @ 200 g/acre seed.

💡 *Conduct a quick germination test on wet paper towels: ensure >85% germination before main field planting.*"""

    # 9. WEED CONTROL & HERBICIDES
    if any(k in q_lower for k in [
        "weed", "herbicide", "grass", "ghas", "khatawar", "weeding", "hoeing", "mulch"
    ]):
        return f"""### 🌾 Weed Management & Herbicide Guide for {active_crop}

Weeds compete with **{active_crop}** for sunlight, moisture, and fertilizers during the **critical first 30-45 days**.

#### 🛠️ Integrated Weed Management Steps:
1. **Pre-Emergence Herbicide** (Within 48 hours of sowing/transplanting):
   - Apply **Pendimethalin 30% EC** @ 1.0 to 1.2 liters per acre in 200 liters of water. Soil must have adequate moisture.
2. **Post-Emergence Herbicide** (15-25 days after sowing):
   - For Rice: Bispyribac Sodium 10% SC (Nominee Gold) @ 80-100 ml/acre when weeds are at 2-3 leaf stage.
   - For Wheat: Clodinafop-propargyl 15% WP @ 160 g/acre for narrow-leaf weeds; Metsulfuron-methyl 20% WP @ 8 g/acre for broad-leaf weeds.
   - For Broadleaf / Vegetables: Hand weeding or mechanical inter-row rotary hoeing is safest.
3. **Organic Weed Suppression**:
   - Mulching with paddy straw (5-7 cm layer) or black plastic mulch film (25-30 micron) completely suppresses weed germination while conserving 30% soil moisture.

⚠️ *Always use a flat-fan floodjet nozzle and never spray herbicides under high wind conditions to prevent drift injury.*"""

    # 10. HARVESTING, STORAGE & POST-HARVEST
    if any(k in q_lower for k in [
        "harvest", "yield", "storage", "mandi", "drying", "katayi", "post harvest", "moisture"
    ]):
        return f"""### 🌾 Harvesting & Post-Harvest Storage Guide for {active_crop}

Maximizing yield and preventing post-harvest loss in **{active_crop}**:

1. **Maturity Indicators**:
   - For Cereals (Rice/Wheat): Harvest when 85% of panicles/ears have turned straw-golden and grain moisture drops to 20-22%.
   - For Tubers (Potato): De-haulm (cut foliage) 10-12 days prior to digging to harden tuber skins.
   - For Vegetables: Harvest early morning to retain turgidity and shelf freshness.

2. **Drying & Moisture Control**:
   - Sun-dry harvested grains on a clean canvas tarpaulin until moisture is below **12% for cereals** and **8-9% for oilseeds**.
   - Test: A dry grain will crack crisply between your teeth without denting.

3. **Safe Storage**:
   - Clean storage bins and gunny bags thoroughly. Sun-dry old bags or dip in 0.1% Malathion solution.
   - Mix dry neem leaves (1 kg per 100 kg grain) or place hermetic bags (PICS bags) to prevent grain weevil infestation without chemicals."""

    # 11. SOIL HEALTH, pH & SOIL AMENDMENTS
    if any(k in q_lower for k in [
        "soil", "mitti", "ph", "saline", "alkali", "acid", "gypsum", "lime", "organic carbon"
    ]):
        soil_text = SOIL_KNOWLEDGE.get(soil, "")
        return f"""### 🌍 Soil Health & Amendment Guide

📍 **Registered Soil**: {soil} • **Farm Area**: {area} acres in {location}

#### 📋 Characteristics of {soil}:
{soil_text}

---
#### 🛠️ Essential Soil Amendments:
- **Acidic Soils (pH < 6.0)**: Apply agricultural limestone (CaCO3) @ 500-1000 kg/acre based on buffer pH test to restore nutrient availability.
- **Saline / Sodic / Alkali Soils (pH > 8.5)**: Apply agricultural Gypsum (CaSO4·2H2O) followed by deep flooding to leach displaced sodium.
- **Low Organic Carbon (< 0.5%)**: Incorporate 5-8 tons of farmyard manure or sow green manure (*Sesbania aculeata / Dhaincha*) and incorporate into soil at 45 days.
- **Soil Health Card**: Test your soil every 2 years for electrical conductivity, organic carbon, and 12 essential nutrients."""

    # 12. GOVERNMENT SCHEMES & SUBSIDIES
    if any(k in q_lower for k in [
        "scheme", "subsidy", "pm kisan", "kcc", "kisan credit", "fasal bima", "insurance", "loan", "yojana", "sarkari"
    ]):
        return f"""### 🏛️ Key Government Schemes for Farmers

Major central and state agricultural support programs you can benefit from:

1. **PM-Kisan Samman Nidhi**:
   - Financial benefit of **₹6,000 per year** in 3 equal installments of ₹2,000 directly to farmer bank accounts.
   - Check status or register at: `pmkisan.gov.in` (Ensure Aadhaar-bank account seeding & e-KYC).

2. **Pradhan Mantri Fasal Bima Yojana (PMFBY)**:
   - Comprehensive crop insurance against non-preventable natural risks (drought, flood, pests).
   - Minimal premium paid by farmers: **2% for Kharif crops**, **1.5% for Rabi crops**, and 5% for commercial/horticultural crops.

3. **Kisan Credit Card (KCC)**:
   - Short-term crop loans up to ₹3,00,000 at a concessional interest rate of **4%** (with 3% prompt repayment incentive).

4. **Per Drop More Crop (Micro-Irrigation Subsidy)**:
   - Subsidies ranging from **45% to 70%** for installing Drip or Sprinkler irrigation systems through the state agriculture/horticulture department.

5. **Sub-Mission on Agricultural Mechanization (SMAM)**:
   - Up to 40-50% subsidy on farm machinery (tractors, power tillers, rotavators, drone sprayers)."""

    # 13. WEATHER & SPRAYING ADVICE
    if any(k in q_lower for k in [
        "weather", "rain", "forecast", "spray", "wind", "temperature", "humidity", "fog"
    ]):
        return f"""### 🌦️ Agricultural Weather & Spray Window Advisory

Smart weather-guided decision rules for your **{active_crop}** farm in **{location}**:

1. **Chemical / Fertilizer Spray Window**:
   - **Wind Speed**: Only spray when wind speed is under **12-15 km/h** to prevent spray drift.
   - **Rain Probability**: Ensure a rain-free window of at least **4 to 6 hours** post-spraying so chemicals are not washed off.
   - **Time of Day**: Early morning (7 AM - 10 AM) or late afternoon (4 PM - 6:30 PM) is optimal. Avoid midday hot sun when spray droplets evaporate rapidly.

2. **High Humidity (>85%) Alert**:
   - Prolonged leaf wetness coupled with warm canopy temperatures triggers fungal outbreaks (blights, blast, downy mildew). Apply preventive bio-fungicide sprays.

3. **Heatwave / Frost Protection**:
   - During severe hot spells or frost warnings, provide a light evening irrigation to moderate root zone temperatures."""

    # 14. DYNAMIC AGENT RESPONSE (Contextual Synthesis for All Other Queries)
    # Extracts key words and constructs a tailored agronomic response referencing their farm
    clean_q = re.sub(r'[^a-zA-Z0-9\s]', '', query).strip()
    return f"""### 🌾 KrishiSetu Agronomy Guidance for {active_crop}

Hello! Regarding your inquiry: **"{query}"**

📍 **Farm Context**: {active_crop} • {area} acres • {location} • {soil} • {irrigation}

Here are the key practical considerations:

1. **Crop Health & Observation**:
   - Regularly scout your **{active_crop}** canopy early in the morning. Inspect the leaf undersides and soil-stem junction for early pest colonies or fungal lesions.

2. **Root & Soil Environment**:
   - In **{soil}**, maintain balanced aeration. Avoid letting the root zone alternate between waterlogged and baked-dry conditions, which causes root rootlet dieback.

3. **Timely Interventions**:
   - Align nutrient and pesticide applications with your **{irrigation}** cycles. Always use balanced inputs and avoid overusing chemical nitrogen.

💬 *Feel free to ask more specifically about:*
- Fertilizer dosages (NPK) or organic nutrition
- Immediate remedies for leaf yellowing or pests
- Sowing dates, weed control, or irrigation schedules!"""

# =====================================================================
# MAIN ENTRYPOINT
# =====================================================================

async def generate_ai_response(
    query: str,
    farm_data: Optional[Dict[str, Any]] = None,
    history: Optional[List[Dict[str, str]]] = None,
    analysis_context: Optional[Dict[str, Any]] = None,
    language: str = "en"
) -> str:
    """Generate expert agronomist guidance using Gemini or built-in Expert System."""
    
    crop = farm_data.get("crop", "Crop") if farm_data else "General Crop"
    location = farm_data.get("location", "Farm") if farm_data else "India"
    soil = farm_data.get("soil", "Loamy Soil") if farm_data else "Loamy Soil"
    irrigation = farm_data.get("irrigation", "Tube Well") if farm_data else "Standard Irrigation"
    area = farm_data.get("area", "1") if farm_data else "1"

    lang_code = (language or "en").lower().strip()
    if lang_code in ["hi", "hindi"]:
        lang_instruction = "CRITICAL LANGUAGE REQUIREMENT: You MUST reply entirely in natural, respectful Hindi (हिन्दी) using agricultural vocabulary that Indian farmers easily understand. Technical/chemical names may include English in parentheses for clarity."
    elif lang_code in ["bn", "bengali", "bangla"]:
        lang_instruction = "CRITICAL LANGUAGE REQUIREMENT: You MUST reply entirely in natural, respectful Bengali (বাংলা) using agricultural vocabulary that farmers in West Bengal and Bangladesh easily understand. Technical/chemical names may include English in parentheses for clarity."
    else:
        lang_instruction = "LANGUAGE REQUIREMENT: Reply in clear, structured, practical English."

    # Format analysis context string if present
    analysis_snippet = ""
    if analysis_context:
        issue = (
            analysis_context.get("primary_issue")
            or analysis_context.get("overall_field_status")
            or "Observation"
        )
        health = (
            analysis_context.get("overall_health_status")
            or analysis_context.get("overall_health")
            or "Stable"
        )
        score = analysis_context.get("overall_health_score") or analysis_context.get("health_score", "N/A")
        actions = (
            analysis_context.get("recommended_actions")
            or analysis_context.get("recommendations")
            or analysis_context.get("chemical_treatments")
            or []
        )
        symptoms = analysis_context.get("symptoms", [])

        analysis_snippet = f"""
Recent AI Crop & Field Doctor Analysis Context:
- Detected Crop: {analysis_context.get("crop_name", crop)}
- Overall Health: {health} (Score: {score}%)
- Primary Issue Diagnosed: {issue}
- Severity: {analysis_context.get("severity", "Normal")}
- Visible Symptoms: {", ".join(symptoms[:4]) if symptoms else "None listed"}
- Key Recommendations: {"; ".join(actions[:3]) if actions else "Standard scouting"}

IMPORTANT: If the farmer's question relates to this recent diagnosis or report, ground your answer directly in these findings!
"""

    # 1. Check if Gemini API Key is configured and try Generative AI
    gemini_key = get_gemini_api_key()
    if gemini_key:
        system_prompt = f"""You are "KrishiSetu AI", a world-class agricultural scientist, agronomist, and trusted companion for farmers.
You provide clear, practical, scientifically accurate, and empathetic farming advice.

Current Farmer Profile:
- Farm Location: {location}
- Crop Cultivated: {crop}
- Soil Type: {soil}
- Farm Area: {area} acres
- Irrigation Method: {irrigation}
{analysis_snippet}

{lang_instruction}

Guidelines:
1. Ground your advice in practical, step-by-step instructions that a farmer can easily implement.
2. Provide both organic/natural alternatives (e.g. Neem oil, Trichoderma, compost) and safe standard chemical dosages with Pre-Harvest Interval (PHI) where appropriate.
3. If the user asks about an analysis report or disease, clearly address cause, spread prevention, and treatment.
4. Keep the tone respectful, friendly, and empowering.
5. Format your answers cleanly with markdown headings, bullet points, and appropriate emojis."""

        gemini_reply = await query_gemini_api(
            api_key=gemini_key,
            system_prompt=system_prompt,
            query=query,
            history=history
        )
        if gemini_reply and gemini_reply.strip():
            return gemini_reply.strip()

    # 2. Comprehensive Botanical & Agronomic Expert System Engine Fallback
    return build_expert_response(
        query=query,
        crop=crop,
        location=location,
        soil=soil,
        irrigation=irrigation,
        area=area,
        analysis_context=analysis_context,
        language=lang_code
    )
