import io
import re
import base64
from typing import Dict, Any, Optional, List, Tuple
from gtts import gTTS
import httpx
from config import get_gemini_api_key

CROP_NAMES_LOCAL = {
    "Rice": {"bn": "à¦§à¦¾à¦¨", "hi": "à¤§à¤¾à¤¨", "en": "Rice"},
    "Wheat": {"bn": "à¦—à¦®", "hi": "à¤—à¥‡à¤¹à¥‚à¤‚", "en": "Wheat"},
    "Potato": {"bn": "à¦†à¦²à§", "hi": "à¤†à¤²à¥‚", "en": "Potato"},
    "Tomato": {"bn": "à¦Ÿà¦®à§‡à¦Ÿà§‹", "hi": "à¤Ÿà¤®à¤¾à¤Ÿà¤°", "en": "Tomato"},
    "Maize": {"bn": "à¦­à§à¦Ÿà§à¦Ÿà¦¾", "hi": "à¤®à¤•à¥à¤•à¤¾", "en": "Maize"},
    "Mustard": {"bn": "à¦¸à¦°à¦¿à¦·à¦¾", "hi": "à¤¸à¤°à¤¸à¥‹à¤‚", "en": "Mustard"},
    "Chilli": {"bn": "à¦²à¦™à§à¦•à¦¾", "hi": "à¤®à¤¿à¤°à¥à¤š", "en": "Chilli"},
    "Cotton": {"bn": "à¦¤à§à¦²à¦¾", "hi": "à¤•à¤ªà¤¾à¤¸", "en": "Cotton"},
    "Vegetables": {"bn": "à¦¶à¦¾à¦•à¦¸à¦¬à¦œà¦¿", "hi": "à¤¸à¤¬à¥à¤œà¤¿à¤¯à¥‹à¤‚", "en": "Vegetables"},
}

def get_local_crop(crop_name: str, lang: str) -> str:
    crop_info = CROP_NAMES_LOCAL.get(crop_name)
    if crop_info and lang in crop_info:
        return crop_info[lang]
    return crop_name or ("à¦§à¦¾à¦¨" if lang == "bn" else ("à¤«à¤¸à¤²" if lang == "hi" else "Crop"))


# Comprehensive Linguistic & Phonetic Language Detector
BENGALI_KEYWORDS = {
    "amar", "amader", "dhaner", "dhane", "dhan", "pata", "patagulo", "patay", "paata", 
    "holud", "ki korbo", "korbo", "kore", "kora", "shorisa", "alu", "chash", 
    "jol", "brishti", "agami", "agami-kal", "agamikal", "rog", "poka", "pokar", "sar", 
    "debo", "deoya", "uchit", "shukno", "jomite", "jomi", "kobe", "kemon", "kivabe", 
    "ki vabe", "achhe", "ache", "hobe", "shuru", "sesh", "krishi", "chas", "sasya", 
    "akromon", "bepar", "karon", "upaay", "upay", "sech", "daag", "dhabba", "dosa", 
    "potash", "yuriya", "dap", "khoti", "fosol", "fosoler", "chara", "beej", "shodhon",
    "bopon", "ghas", "agacha", "muriya", "shekor", "khobor", "abohawa", "abohawar", "bolun", "shunchen"
}

HINDI_KEYWORDS = {
    "meri", "mera", "mere", "fasal", "faslo", "gehu", "dhan", "kya karu", "kya kare", 
    "peela", "peeli", "peele", "pani", "paani", "khad", "kisan", "keede", "keeda", "keedo", 
    "barish", "barsat", "kab", "sinchai", "sinchayi", "dhabbe", "dhabba", "rog", "kitna", "kitni", 
    "dena", "chahiye", "chaiye", "cheiya", "chahie", "hoga", "hogi", "kaise", "kare", "kheto", "khet", "patte", 
    "pattiya", "patto", "dawa", "dawai", "chhidkaw", "upar", "mausam", "kisan", "upchar", 
    "beej", "buwai", "kharpatwar", "sukha", "gala", "jad", "gobar", "urvarak", "main", "mein", "me", "karna", "batao", "bataiye"
}

ENGLISH_KEYWORDS = {
    "my", "the", "is", "are", "crop", "crops", "rice", "wheat", "potato", "tomato", 
    "leaves", "leaf", "yellow", "yellowing", "water", "irrigate", "irrigation", 
    "fertilizer", "fertilizers", "soil", "rain", "raining", "tomorrow", "spots", 
    "brown", "should", "what", "when", "how", "spray", "pest", "pests", "insect", 
    "insects", "disease", "harvest", "yield", "urea", "dose", "dosage", "grow", "after", "give", "much"
}


def detect_spoken_language(text: str, default_lang: str = "en") -> str:
    """
    State-of-the-Art Language Detection for Regional Indian Speech:
    1. Direct Unicode Script analysis (Bengali \u0980-\u09FF, Devanagari \u0900-\u097F).
    2. Transliteration & Phonetic Keyword Frequency (Banglish vs Hinglish vs English).
    """
    if not text or not text.strip():
        return default_lang if default_lang in ["bn", "hi", "en"] else "en"
    
    clean_t = text.strip()
    
    # 1. Unicode Script Matching
    if re.search(r'[\u0980-\u09FF]', clean_t):
        return "bn"
    
    if re.search(r'[\u0900-\u097F]', clean_t):
        return "hi"
    
    # 2. Phonetic & Lexical token analysis for Romanized text
    tokens = re.findall(r'[a-zA-Z]+', clean_t.lower())
    if not tokens:
        return default_lang if default_lang in ["bn", "hi", "en"] else "en"
        
    t_lower = clean_t.lower()
    
    bn_score = 0
    hi_score = 0
    en_score = 0
    
    # Check key multi-word phrases first
    for phrase in ["ki korbo", "ki vabe", "kivabe", "dhaner pata", "pani kobe", "agami kal", "agamikal", "jol debo"]:
        if phrase in t_lower:
            bn_score += 4.0
                
    for phrase in ["kya karu", "kya kare", "kab dena", "kab de", "pani dena", "pani kab", "kese kare", "kaise kare", "fasal me", "fasal main", "cheiya", "chaiye"]:
        if phrase in t_lower:
            hi_score += 4.0

    for tok in tokens:
        if tok in BENGALI_KEYWORDS:
            bn_score += 1.5
        if tok in HINDI_KEYWORDS:
            hi_score += 1.5
        if tok in ENGLISH_KEYWORDS:
            en_score += 1.0

    if bn_score > hi_score and bn_score > en_score and bn_score >= 1.0:
        return "bn"
    if hi_score > bn_score and hi_score > en_score and hi_score >= 1.0:
        return "hi"
    if en_score >= 1.0 and en_score > bn_score and en_score > hi_score:
        return "en"
        
    if default_lang in ["bn", "hi", "en"]:
        return default_lang
    return "hi" if hi_score > 0 else "en"


def clean_text_for_speech(text: str, lang: str = "en") -> str:
    """
    Format text into natural, spoken conversational phonetics for TTS.
    Converts symbols, English acronyms, and units into authentic spoken phonetics
    so regional TTS models pronounce them smoothly without robotic artifacts.
    """
    if not text:
        return ""
        
    cleaned = text
    # Remove markdown headers, bold, italics, links, bullets
    cleaned = re.sub(r'#+\s*', '', cleaned)
    cleaned = re.sub(r'\*{1,3}', '', cleaned)
    cleaned = re.sub(r'`{1,3}', '', cleaned)
    cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)
    cleaned = re.sub(r'[-â€¢*]\s+', ' ', cleaned)
    
    # Remove emoji and symbols that distort audio synthesis
    cleaned = re.sub(r'[âš ï¸ðŸš¨ðŸ’¡ðŸ”ðŸŒ¾ðŸ›ðŸ’§ðŸŒ±ðŸ“‹ðŸ§ªðŸ›ï¸â€¢~^|/\\()\[\]{}]', ' ', cleaned)
    
    if lang == "bn":
        cleaned = cleaned.replace("NPK", " à¦à¦¨ à¦ªà¦¿ à¦•à§‡ ")
        cleaned = cleaned.replace("pH", " à¦ªà¦¿ à¦à¦‡à¦š ")
        cleaned = cleaned.replace("NDVI", " à¦à¦¨ à¦¡à¦¿ à¦­à¦¿ à¦†à¦‡ ")
        cleaned = cleaned.replace("Urea", " à¦‡à¦‰à¦°à¦¿à¦¯à¦¼à¦¾ ")
        cleaned = cleaned.replace("DAP", " à¦¡à¦¿ à¦ à¦ªà¦¿ ")
        cleaned = cleaned.replace("MOP", " à¦ªà¦Ÿà¦¾à¦¶ ")
        cleaned = cleaned.replace("Mancozeb", " à¦®à§à¦¯à¦¾à¦¨à¦•à§‹à¦œà§‡à¦¬ ")
        cleaned = cleaned.replace("Saaf", " à¦¸à¦¾à¦« ")
        cleaned = cleaned.replace("Cartap", " à¦•à¦¾à¦°à§à¦Ÿà¦¾à¦ª ")
        cleaned = cleaned.replace("Chlorantraniliprole", " à¦•à§‹à¦°à¦¾à¦œà¦¨ ")
        cleaned = cleaned.replace("Trichoderma", " à¦Ÿà§à¦°à¦¾à¦‡à¦•à§‹à¦¡à¦¾à¦°à§à¦®à¦¾ ")
        cleaned = cleaned.replace("mÂ³/mÂ³", " à¦˜à¦¨à¦®à¦¿à¦Ÿà¦¾à¦° ")
        cleaned = cleaned.replace("kg/ha", " à¦•à§‡à¦œà¦¿ à¦ªà§à¦°à¦¤à¦¿ à¦¹à§‡à¦•à§à¦Ÿà¦°à§‡ ")
        cleaned = cleaned.replace("g/L", " à¦—à§à¦°à¦¾à¦® à¦ªà§à¦°à¦¤à¦¿ à¦²à¦¿à¦Ÿà¦¾à¦°à§‡ ")
        cleaned = cleaned.replace("ml/L", " à¦®à¦¿à¦²à¦¿ à¦ªà§à¦°à¦¤à¦¿ à¦²à¦¿à¦Ÿà¦¾à¦°à§‡ ")
        cleaned = cleaned.replace("Â°C", " à¦¡à¦¿à¦—à§à¦°à¦¿ à¦¸à§‡à¦²à¦¸à¦¿à¦¯à¦¼à¦¾à¦¸ ")
        cleaned = cleaned.replace("%", " à¦¶à¦¤à¦¾à¦‚à¦¶ ")
        cleaned = cleaned.replace("2.5", " à¦†à¦¡à¦¼à¦¾à¦‡ ")
        cleaned = cleaned.replace("0.5", " à¦…à¦°à§à¦§à§‡à¦• ")
    elif lang == "hi":
        cleaned = cleaned.replace("NPK", " à¤à¤¨ à¤ªà¥€ à¤•à¥‡ ")
        cleaned = cleaned.replace("pH", " à¤ªà¥€ à¤à¤š ")
        cleaned = cleaned.replace("NDVI", " à¤à¤¨ à¤¡à¥€ à¤µà¥€ à¤†à¤ˆ ")
        cleaned = cleaned.replace("Urea", " à¤¯à¥‚à¤°à¤¿à¤¯à¤¾ ")
        cleaned = cleaned.replace("DAP", " à¤¡à¥€ à¤ à¤ªà¥€ ")
        cleaned = cleaned.replace("MOP", " à¤ªà¥‹à¤Ÿà¤¾à¤¶ ")
        cleaned = cleaned.replace("Mancozeb", " à¤®à¥ˆà¤¨à¤•à¥‹à¤œà¥‡à¤¬ ")
        cleaned = cleaned.replace("Saaf", " à¤¸à¤¾à¤« ")
        cleaned = cleaned.replace("Cartap", " à¤•à¤¾à¤°à¥à¤Ÿà¤¾à¤ª ")
        cleaned = cleaned.replace("Chlorantraniliprole", " à¤•à¥‹à¤°à¤¾à¤œà¤¨ ")
        cleaned = cleaned.replace("Trichoderma", " à¤Ÿà¥à¤°à¤¾à¤‡à¤•à¥‹à¤¡à¤°à¥à¤®à¤¾ ")
        cleaned = cleaned.replace("mÂ³/mÂ³", " à¤˜à¤¨à¤®à¥€à¤Ÿà¤° ")
        cleaned = cleaned.replace("kg/ha", " à¤•à¤¿à¤²à¥‹à¤—à¥à¤°à¤¾à¤® à¤ªà¥à¤°à¤¤à¤¿ à¤¹à¥‡à¤•à¥à¤Ÿà¥‡à¤¯à¤° ")
        cleaned = cleaned.replace("g/L", " à¤—à¥à¤°à¤¾à¤® à¤ªà¥à¤°à¤¤à¤¿ à¤²à¥€à¤Ÿà¤° ")
        cleaned = cleaned.replace("ml/L", " à¤®à¤¿à¤²à¥€ à¤ªà¥à¤°à¤¤à¤¿ à¤²à¥€à¤Ÿà¤° ")
        cleaned = cleaned.replace("Â°C", " à¤¡à¤¿à¤—à¥à¤°à¥€ à¤¸à¥‡à¤²à¥à¤¸à¤¿à¤¯à¤¸ ")
        cleaned = cleaned.replace("%", " à¤ªà¥à¤°à¤¤à¤¿à¤¶à¤¤ ")
        cleaned = cleaned.replace("2.5", " à¤¢à¤¾à¤ˆ ")
        cleaned = cleaned.replace("0.5", " à¤†à¤§à¤¾ ")
    else:
        cleaned = cleaned.replace("NPK", "N-P-K")
        cleaned = cleaned.replace("pH", "p-H")
        cleaned = cleaned.replace("kg/ha", " kilograms per hectare ")
        cleaned = cleaned.replace("g/L", " grams per liter ")
        cleaned = cleaned.replace("ml/L", " milliliters per liter ")
        cleaned = cleaned.replace("Â°C", " degrees celsius ")
        cleaned = cleaned.replace("%", " percent ")
        
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def synthesize_speech_base64(text: str, lang: str = "en") -> Optional[str]:
    """
    Convert text to natural spoken MP3 audio base64 using Google Text-to-Speech (gTTS).
    Matches the regional Indian dialect for Bengali (bn), Hindi (hi), or Indian English (en-IN).
    """
    try:
        clean_text = clean_text_for_speech(text, lang=lang)
        if not clean_text:
            return None
        
        # Keep spoken answers concise so audio loads with sub-second latency
        if len(clean_text) > 380:
            clean_text = clean_text[:380].rsplit('.', 1)[0]
            if not clean_text.endswith('.'):
                clean_text += '.'
            
        gtts_lang = "bn" if lang == "bn" else ("hi" if lang == "hi" else "en")
        tld = "co.in" if lang == "en" else "com"
        
        tts = gTTS(text=clean_text, lang=gtts_lang, tld=tld, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_b64 = base64.b64encode(fp.read()).decode("utf-8")
        return audio_b64
    except Exception as e:
        print(f"[KrishiSetu Voice TTS] Synthesis warning: {e}")
        return None


async def query_gemini_for_voice(
    api_key: str,
    system_prompt: str,
    user_query: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Optional[str]:
    """Call Google Gemini Generative AI models with context and conversation turns."""
    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    
    contents = []
    # Add recent conversation turns for conversational follow-ups
    if conversation_history:
        for msg in conversation_history[-4:]:
            role = "user" if msg.get("role") == "user" else "model"
            txt = (msg.get("content") or "").strip()
            if txt:
                contents.append({"role": role, "parts": [{"text": txt}]})
                
    # Ensure proper turn alternation
    if contents and contents[-1]["role"] == "user":
        contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        
    contents.append({"role": "user", "parts": [{"text": user_query}]})
    
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 320
        }
    }
    
    async with httpx.AsyncClient(timeout=12.0) as client:
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            try:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            res_text = parts[0]["text"].strip()
                            if res_text:
                                return res_text
                elif resp.status_code == 400:
                    # Fallback payload format
                    merged_contents = [
                        {"role": "user", "parts": [{"text": f"Instruction:\n{system_prompt}\n\nFarmer Query:\n{user_query}"}]}
                    ]
                    resp2 = await client.post(url, json={"contents": merged_contents, "generationConfig": {"temperature": 0.4, "maxOutputTokens": 320}})
                    if resp2.status_code == 200:
                        data2 = resp2.json()
                        candidates = data2.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                return parts[0]["text"].strip()
            except Exception:
                continue
    return None


def build_dynamic_agronomic_voice_response(
    query: str,
    lang: str,
    crop: str,
    soil: str,
    location: str,
    soil_moisture: Optional[str],
    weather_summary: Optional[str],
    rain_chance: int,
    recent_diagnosis: Optional[str],
    history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Intelligent Dynamic Agronomic Natural Voice Engine.
    Generates distinct, conversational, field-grounded answers in Bengali,
    Hindi, or English for every distinct agricultural question.
    """
    q_lower = query.lower()
    crop_disp = get_local_crop(crop, lang)

    # 1. WEATHER & RAIN + FERTILIZER/SPRAY TIMING
    is_rain_inquiry = any(w in q_lower for w in ["rain", "raining", "à¦¬à§ƒà¦·à§à¦Ÿà¦¿", "à¦¬à¦¾à¦°à¦¿à¦¶", "à¤¬à¤¾à¤°à¤¿à¤¶", "à¤¬à¤°à¤¸à¤¾à¤¤", "weather", "à¦†à¦¬à¦¹à¦¾à¦“à¦¯à¦¼à¦¾", "à¤®à¥Œà¤¸à¤®", "à¦¬à¦¾à¦¦à¦²", "à¦†à¦à¦§à¦¿", "à¦®à§‡à¦˜", "barish", "barsat", "brishti", "abohawa", "mausam"])
    is_fertilizer_or_spray = any(w in q_lower for w in ["fertilizer", "urea", "spray", "khad", "à¦¸à¦¾à¦°", "à¦¸à§à¦ªà§à¦°à§‡", "à¦‡à¦‰à¦°à¦¿à¦¯à¦¼à¦¾", "à¦¡à¦¿à¦à¦ªà¦¿", "à¦ªà¦Ÿà¦¾à¦¶", "à¤–à¤¾à¤¦", "à¤¦à¤µà¤¾", "à¤›à¤¿à¤¡à¤¼à¤•à¤¾à¤µ", "à¤¯à¥‚à¤°à¤¿à¤¯à¤¾", "à¤¡à¥€à¤à¤ªà¥€", "à¤ªà¥‹à¤Ÿà¤¾à¤¶", "dap", "potash", "chhidkaw", "sar", "dawa"])
    
    if is_rain_inquiry and is_fertilizer_or_spray:
        if lang == "bn":
            return f"à¦†à¦—à¦¾à¦®à§€à¦•à¦¾à¦² à¦¬à§ƒà¦·à§à¦Ÿà¦¿à¦° à¦¸à¦®à§à¦­à¦¾à¦¬à¦¨à¦¾ à¦¥à¦¾à¦•à¦²à§‡ à¦œà¦®à¦¿à¦¤à§‡ à¦•à§‹à¦¨à§‹ à¦‡à¦‰à¦°à¦¿à¦¯à¦¼à¦¾ à¦¸à¦¾à¦° à¦¬à¦¾ à¦•à§€à¦Ÿà¦¨à¦¾à¦¶à¦• à¦¸à§à¦ªà§à¦°à§‡ à¦•à¦°à¦¬à§‡à¦¨ à¦¨à¦¾à¥¤ à¦¬à§ƒà¦·à§à¦Ÿà¦¿à¦° à¦œà¦²à§‡ à¦¸à¦¾à¦° à¦§à§à¦¯à¦¼à§‡ à¦…à¦ªà¦šà¦¯à¦¼ à¦¹à¦¬à§‡à¥¤ à¦†à¦•à¦¾à¦¶ à¦ªà¦°à¦¿à¦·à§à¦•à¦¾à¦° à¦¹à¦²à§‡ à¦à¦¬à¦‚ à¦œà¦² à¦¨à¦¾à¦®à¦²à§‡ à¦¤à¦¬à§‡à¦‡ à¦¸à¦¾à¦° à¦ªà§à¦°à¦¯à¦¼à§‹à¦— à¦•à¦°à§à¦¨à¥¤"
        elif lang == "hi":
            return f"à¤¯à¤¦à¤¿ à¤•à¤² à¤¬à¤¾à¤°à¤¿à¤¶ à¤•à¥€ à¤¸à¤‚à¤­à¤¾à¤µà¤¨à¤¾ à¤¹à¥ˆ à¤¤à¥‹ à¤–à¥‡à¤¤ à¤®à¥‡à¤‚ à¤¯à¥‚à¤°à¤¿à¤¯à¤¾ à¤¯à¤¾ à¤•à¥€à¤Ÿà¤¨à¤¾à¤¶à¤• à¤¸à¥à¤ªà¥à¤°à¥‡ à¤¬à¤¿à¤²à¥à¤•à¥à¤² à¤¨ à¤•à¤°à¥‡à¤‚à¥¤ à¤¬à¤¾à¤°à¤¿à¤¶ à¤•à¥‡ à¤ªà¤¾à¤¨à¥€ à¤¸à¥‡ à¤–à¤¾à¤¦ à¤¬à¤¹à¤•à¤° à¤¬à¤°à¥à¤¬à¤¾à¤¦ à¤¹à¥‹ à¤œà¤¾à¤à¤—à¥€à¥¤ à¤®à¥Œà¤¸à¤® à¤¸à¤¾à¤« à¤¹à¥‹à¤¨à¥‡ à¤•à¥‡ à¤¬à¤¾à¤¦ à¤¹à¥€ à¤›à¤¿à¤¡à¤¼à¤•à¤¾à¤µ à¤•à¤°à¥‡à¤‚à¥¤"
        else:
            return f"Do not apply Urea or chemical sprays if rain is expected tomorrow. Rainwater will wash away nutrients and cause nitrogen runoff. Wait until clear weather returns."

    if is_rain_inquiry:
        if lang == "bn":
            return f"à¦†à¦ªà¦¨à¦¾à¦° {location} à¦…à¦žà§à¦šà¦²à§‡ à¦¬à¦°à§à¦¤à¦®à¦¾à¦¨à§‡ {weather_summary}à¥¤ à¦¬à§ƒà¦·à§à¦Ÿà¦¿à¦° à¦¸à¦®à§à¦­à¦¾à¦¬à¦¨à¦¾ à¦ªà§à¦°à¦¾à¦¯à¦¼ {rain_chance} à¦¶à¦¤à¦¾à¦‚à¦¶à¥¤ à¦¬à§ƒà¦·à§à¦Ÿà¦¿à¦° à¦†à¦—à§‡ à¦œà¦®à¦¿à¦¤à§‡ à¦¨à¦¿à¦•à¦¾à¦¶à¦¿ à¦¨à¦¾à¦²à¦¾ à¦ªà¦°à¦¿à¦·à§à¦•à¦¾à¦° à¦°à¦¾à¦–à§à¦¨ à¦¯à¦¾à¦¤à§‡ à¦œà¦² à¦œà¦®à¦¤à§‡ à¦¨à¦¾ à¦ªà¦¾à¦°à§‡à¥¤"
        elif lang == "hi":
            return f"à¤†à¤ªà¤•à¥‡ {location} à¤•à¥à¤·à¥‡à¤¤à¥à¤° à¤®à¥‡à¤‚ à¤…à¤­à¥€ {weather_summary} à¤¹à¥ˆà¥¤ à¤¬à¤¾à¤°à¤¿à¤¶ à¤•à¥€ à¤¸à¤‚à¤­à¤¾à¤µà¤¨à¤¾ {rain_chance} à¤ªà¥à¤°à¤¤à¤¿à¤¶à¤¤ à¤¹à¥ˆà¥¤ à¤–à¥‡à¤¤ à¤®à¥‡à¤‚ à¤œà¤² à¤¨à¤¿à¤•à¤¾à¤¸à¥€ à¤•à¥€ à¤µà¥à¤¯à¤µà¤¸à¥à¤¥à¤¾ à¤¦à¥à¤°à¥à¤¸à¥à¤¤ à¤°à¤–à¥‡à¤‚ à¤¤à¤¾à¤•à¤¿ à¤œà¤²à¤­à¤°à¤¾à¤µ à¤¨ à¤¹à¥‹à¥¤"
        else:
            return f"Current weather in {location} is {weather_summary} with a {rain_chance}% chance of rain. Ensure field drainage channels are open to prevent water stagnation."

    # 2. IRRIGATION & WATER MANAGEMENT ("à¤ªà¤¾à¤¨à¥€ à¤•à¤¬ à¤¦à¥‡à¤‚", "à¦ªà¦¾à¦¨à¦¿", "à¤¸à¤¿à¤‚à¤šà¤¾à¤ˆ", "à¦œà¦² à¦¦à§‡à¦¬", "water", "irrigate")
    if any(w in q_lower for w in ["water", "irrigate", "irrigation", "à¤ªà¤¾à¤¨à¥€", "à¤¸à¤¿à¤‚à¤šà¤¾à¤ˆ", "à¦¸à§‡à¦š", "à¦œà¦²", "à¦ªà¦¾à¦¨à¦¿ à¦•à¦–à¦¨", "pani", "paani", "sinchai", "sinchayi", "sech", "jol debo", "pani kab", "pani dena", "kab pani", "pani kab kab", "jal"]):
        is_wet = soil_moisture and ("wet" in soil_moisture.lower() or "humid" in soil_moisture.lower() or "adequate" in soil_moisture.lower())
        if is_wet or rain_chance > 50:
            if lang == "bn":
                return f"à¦†à¦ªà¦¨à¦¾à¦° {location} à¦…à¦žà§à¦šà¦²à§‡à¦° à¦®à¦¾à¦Ÿà¦¿à¦¤à§‡ à¦¬à¦°à§à¦¤à¦®à¦¾à¦¨à§‡ à¦ªà¦°à§à¦¯à¦¾à¦ªà§à¦¤ à¦†à¦°à§à¦¦à§à¦°à¦¤à¦¾ à¦°à¦¯à¦¼à§‡à¦›à§‡ à¦à¦¬à¦‚ à¦¬à§ƒà¦·à§à¦Ÿà¦¿à¦° à¦¸à¦®à§à¦­à¦¾à¦¬à¦¨à¦¾ {rain_chance}%à¥¤ à¦†à¦œ à¦¨à¦¤à§à¦¨ à¦•à¦°à§‡ à¦¸à§‡à¦š à¦¦à§‡à¦“à¦¯à¦¼à¦¾à¦° à¦ªà§à¦°à¦¯à¦¼à§‹à¦œà¦¨ à¦¨à§‡à¦‡, à¦…à¦¤à¦¿à¦°à¦¿à¦•à§à¦¤ à¦œà¦²à§‡ à¦¶à¦¿à¦•à¦¡à¦¼ à¦ªà¦šà§‡ à¦¯à§‡à¦¤à§‡ à¦ªà¦¾à¦°à§‡à¥¤"
            elif lang == "hi":
                return f"à¤†à¤ªà¤•à¥‡ à¤–à¥‡à¤¤ à¤•à¥€ à¤®à¤¿à¤Ÿà¥à¤Ÿà¥€ à¤®à¥‡à¤‚ à¤…à¤­à¥€ à¤ªà¤°à¥à¤¯à¤¾à¤ªà¥à¤¤ à¤¨à¤®à¥€ à¤¹à¥ˆ à¤”à¤° à¤¬à¤¾à¤°à¤¿à¤¶ à¤•à¥€ à¤¸à¤‚à¤­à¤¾à¤µà¤¨à¤¾ {rain_chance}% à¤¹à¥ˆà¥¤ à¤…à¤­à¥€ {crop_disp} à¤®à¥‡à¤‚ à¤…à¤¤à¤¿à¤°à¤¿à¤•à¥à¤¤ à¤ªà¤¾à¤¨à¥€ à¤¨ à¤¦à¥‡à¤‚, à¤¤à¤¾à¤•à¤¿ à¤œà¤¡à¤¼ à¤—à¤²à¤¨ à¤¨ à¤¹à¥‹à¥¤ à¤¶à¤¾à¤® à¤•à¥‹ à¤–à¥‡à¤¤ à¤¦à¥‡à¤–à¤•à¤° à¤¹à¥€ à¤¹à¤²à¥à¤•à¥€ à¤¸à¤¿à¤‚à¤šà¤¾à¤ˆ à¤•à¤°à¥‡à¤‚à¥¤"
            else:
                return f"Your soil in {location} currently has adequate moisture with {rain_chance}% rain forecast. Do not irrigate today to avoid waterlogging."
        else:
            if lang == "bn":
                return f"à¦®à¦¾à¦Ÿà¦¿à¦° à¦‰à¦ªà¦°à¦¿à¦­à¦¾à¦— à¦ªà¦°à§€à¦•à§à¦·à¦¾ à¦•à¦°à§‡ à¦¦à§‡à¦–à§à¦¨à¥¤ à¦¯à¦¦à¦¿ {crop_disp} à¦—à¦¾à¦›à§‡à¦° à¦—à§‹à¦¡à¦¼à¦¾à¦¯à¦¼ à¦®à¦¾à¦Ÿà¦¿ à¦¶à§à¦·à§à¦• à¦¥à¦¾à¦•à§‡, à¦¤à¦¬à§‡ à¦¬à¦¿à¦•à§‡à¦²à§‡ à¦¹à¦¾à¦²à¦•à¦¾ à¦¸à§‡à¦š à¦¦à¦¿à¦¨à¥¤ à¦–à§‡à¦¯à¦¼à¦¾à¦² à¦°à¦¾à¦–à¦¬à§‡à¦¨ à¦¯à§‡à¦¨ à¦œà¦®à¦¿à¦¤à§‡ à¦œà¦² à¦¦à§€à¦°à§à¦˜à¦•à§à¦·à¦£ à¦œà¦®à§‡ à¦¨à¦¾ à¦¥à¦¾à¦•à§‡à¥¤"
            elif lang == "hi":
                return f"{crop_disp} à¤®à¥‡à¤‚ à¤œà¤¬ à¤Šà¤ªà¤°à¥€ 2 à¤‡à¤‚à¤š à¤®à¤¿à¤Ÿà¥à¤Ÿà¥€ à¤¸à¥‚à¤–à¥€ à¤²à¤—à¥‡ à¤¤à¤­à¥€ à¤ªà¤¾à¤¨à¥€ à¤¦à¥‡à¤‚à¥¤ à¤«à¥‚à¤² à¤†à¤¨à¥‡ à¤”à¤° à¤¦à¤¾à¤¨à¤¾ à¤­à¤°à¤¤à¥‡ à¤¸à¤®à¤¯ à¤ªà¤¾à¤¨à¥€ à¤•à¥€ à¤•à¤®à¥€ à¤¨ à¤¹à¥‹à¤¨à¥‡ à¤¦à¥‡à¤‚à¥¤ à¤†à¤œ à¤¶à¤¾à¤® à¤–à¥‡à¤¤ à¤®à¥‡à¤‚ à¤¹à¤²à¥à¤•à¥€ à¤¸à¤¿à¤‚à¤šà¤¾à¤ˆ à¤•à¤° à¤¸à¤•à¤¤à¥‡ à¤¹à¥ˆà¤‚à¥¤"
            else:
                return f"Check your field surface. If topsoil is dry around your {crop_disp}, apply a light irrigation this evening without flooding."

    # 3. CROP ROTATION & POST-HARVEST ("What crop to grow after rice / wheat?")
    if any(w in q_lower for w in ["after", "rotate", "rotation", "à¦ªà¦°", "à¦ªà¦°à§‡", "à¦ªà¦°à¦¬à¦°à§à¦¤à§€", "à¦¬à¦¾à¦¦", "à¤¬à¤¾à¤¦", "à¤…à¤—à¤²à¥€ à¤«à¤¸à¤²", "next crop", "à¦ªà¦°à§‡à¦° à¦«à¦¸à¦²", "baad", "agli fasal", "porer fosol"]):
        if "rice" in crop.lower() or "à¦§à¦¾à¦¨" in q_lower or "dhan" in q_lower:
            if lang == "bn":
                return f"à¦§à¦¾à¦¨ à¦•à¦¾à¦Ÿà¦¾à¦° à¦ªà¦° à¦œà¦®à¦¿à¦¤à§‡ à¦¸à¦°à¦¿à¦·à¦¾, à¦†à¦²à§, à¦¡à¦¾à¦² à¦œà¦¾à¦¤à§€à¦¯à¦¼ à¦«à¦¸à¦² à¦¯à§‡à¦®à¦¨ à¦®à¦¸à§à¦° à¦¬à¦¾ à¦–à§‡à¦¸à¦¾à¦°à¦¿, à¦…à¦¥à¦¬à¦¾ à¦—à¦® à¦šà¦¾à¦· à¦•à¦°à¦¾ à¦¸à¦¬à¦šà§‡à¦¯à¦¼à§‡ à¦²à¦¾à¦­à¦œà¦¨à¦•à¥¤ à¦¡à¦¾à¦² à¦šà¦¾à¦· à¦•à¦°à¦²à§‡ à¦®à¦¾à¦Ÿà¦¿à¦¤à§‡ à¦ªà§à¦°à¦¾à¦•à§ƒà¦¤à¦¿à¦•à¦­à¦¾à¦¬à§‡ à¦¨à¦¾à¦‡à¦Ÿà§à¦°à§‹à¦œà§‡à¦¨ à¦¯à§à¦•à§à¦¤ à¦¹à¦¯à¦¼ à¦à¦¬à¦‚ à¦œà¦®à¦¿à¦° à¦‰à¦°à§à¦¬à¦°à¦¤à¦¾ à¦¬à¦¾à¦¡à¦¼à§‡à¥¤"
            elif lang == "hi":
                return f"à¤§à¤¾à¤¨ à¤•à¥€ à¤•à¤Ÿà¤¾à¤ˆ à¤•à¥‡ à¤¬à¤¾à¤¦ à¤†à¤ª à¤—à¥‡à¤¹à¥‚à¤‚, à¤¸à¤°à¤¸à¥‹à¤‚, à¤šà¤¨à¤¾, à¤®à¤Ÿà¤° à¤¯à¤¾ à¤†à¤²à¥‚ à¤²à¤—à¤¾ à¤¸à¤•à¤¤à¥‡ à¤¹à¥ˆà¤‚à¥¤ à¤¦à¤²à¤¹à¤¨à¥€ à¤«à¤¸à¤²à¥‡à¤‚ à¤‰à¤—à¤¾à¤¨à¥‡ à¤¸à¥‡ à¤®à¤¿à¤Ÿà¥à¤Ÿà¥€ à¤®à¥‡à¤‚ à¤ªà¥à¤°à¤¾à¤•à¥ƒà¤¤à¤¿à¤• à¤¨à¤¾à¤‡à¤Ÿà¥à¤°à¥‹à¤œà¤¨ à¤¬à¤¢à¤¼à¤¤à¥€ à¤¹à¥ˆ à¤”à¤° à¤œà¤®à¥€à¤¨ à¤‰à¤ªà¤œà¤¾à¤Š à¤¬à¤¨à¤¤à¥€ à¤¹à¥ˆà¥¤"
            else:
                return f"After harvesting Rice, planting Mustard, Potato, Chickpea, Lentil, or Wheat is ideal. Growing legumes naturally replenishes soil nitrogen and breaks pest cycles."
        elif "wheat" in crop.lower() or "à¦—à¦®" in q_lower or "gehu" in q_lower:
            if lang == "bn":
                return f"à¦—à¦® à¦¤à§‹à¦²à¦¾à¦° à¦ªà¦° à¦œà¦®à¦¿à¦¤à§‡ à¦¸à¦¬à§à¦œ à¦¸à¦¾à¦° à¦¹à¦¿à¦¸à§‡à¦¬à§‡ à¦§à¦‡à¦žà§à¦šà¦¾ à¦¬à¦¾ à¦®à§à¦— à¦¡à¦¾à¦² à¦šà¦¾à¦· à¦•à¦°à§à¦¨à¥¤ à¦à¦¤à§‡ à¦ªà¦°à¦¬à¦°à§à¦¤à§€ à¦†à¦®à¦¨ à¦§à¦¾à¦¨à§‡à¦° à¦«à¦²à¦¨ à¦…à¦¨à§‡à¦• à¦­à¦¾à¦²à§‹ à¦¹à¦¯à¦¼à¥¤"
            elif lang == "hi":
                return f"à¤—à¥‡à¤¹à¥‚à¤‚ à¤•à¥€ à¤•à¤Ÿà¤¾à¤ˆ à¤•à¥‡ à¤¬à¤¾à¤¦ à¤¹à¤°à¥€ à¤–à¤¾à¤¦ à¤•à¥‡ à¤²à¤¿à¤ à¤¢à¥ˆà¤‚à¤šà¤¾ à¤¯à¤¾ à¤®à¥‚à¤‚à¤— à¤²à¤—à¤¾à¤à¤‚à¥¤ à¤‡à¤¸à¤¸à¥‡ à¤…à¤—à¤²à¥€ à¤«à¤¸à¤² à¤•à¥‡ à¤²à¤¿à¤ à¤œà¤®à¥€à¤¨ à¤®à¥‡à¤‚ à¤­à¤°à¤ªà¥‚à¤° à¤œà¥€à¤µà¤¾à¤‚à¤¶ à¤•à¤¾à¤°à¥à¤¬à¤¨ à¤¬à¤¢à¤¼à¤¤à¤¾ à¤¹à¥ˆà¥¤"
            else:
                return f"After Wheat, sow green manure like Sesbania (Dhaincha) or summer Mung bean to boost soil organic carbon before the next Kharif season."
        else:
            if lang == "bn":
                return f"{crop_disp} à¦¤à§‹à¦²à¦¾à¦° à¦ªà¦° à¦œà¦®à¦¿à¦¤à§‡ à¦¡à¦¾à¦²à¦¶à¦¸à§à¦¯ à¦¬à¦¾ à¦¤à§ˆà¦²à¦¬à§€à¦œ à¦šà¦¾à¦· à¦•à¦°à¦¾ à¦¸à¦¬à¦šà§‡à¦¯à¦¼à§‡ à¦‰à¦ªà¦¯à§‹à¦—à§€à¥¤ à¦à¦¤à§‡ à¦®à¦¾à¦Ÿà¦¿à¦° à¦‰à¦°à§à¦¬à¦°à¦¤à¦¾ à¦¬à¦œà¦¾à¦¯à¦¼ à¦¥à¦¾à¦•à§‡à¥¤"
            elif lang == "hi":
                return f"{crop_disp} à¤•à¥‡ à¤¬à¤¾à¤¦ à¤¦à¤²à¤¹à¤¨à¥€ à¤¯à¤¾ à¤¤à¤¿à¤²à¤¹à¤¨à¥€ à¤«à¤¸à¤²à¥‡à¤‚ à¤²à¤—à¤¾à¤¨à¤¾ à¤¸à¤¬à¤¸à¥‡ à¤‰à¤ªà¤¯à¥à¤•à¥à¤¤ à¤°à¤¹à¤¤à¤¾ à¤¹à¥ˆ, à¤œà¤¿à¤¸à¤¸à¥‡ à¤®à¤¿à¤Ÿà¥à¤Ÿà¥€ à¤•à¥€ à¤‰à¤°à¥à¤µà¤°à¤¤à¤¾ à¤¬à¤¨à¥€ à¤°à¤¹à¥‡à¥¤"
            else:
                return f"Following {crop_disp} with a leguminous pulse or oilseed crop improves soil structure and nutrient balance."

    # 4. LEAF SPOTS & FUNGAL BLIGHT ("Brown spots", "Black spots", "à¦¦à¦¾à¦—", "à¤§à¤¬à¥à¤¬à¥‡", "blight")
    if any(w in q_lower for w in ["spot", "spots", "brown", "black", "à¦¦à¦¾à¦—", "à¦§à¦¾à¦¬à§à¦¬à¦¾", "à¦§à¦¬à§à¦¬à§‡", "à¤§à¤¬à¥à¤¬à¥‡", "à¤§à¤¬à¥à¤¬à¤¾", "à¤¬à¥à¤²à¤¾à¤‡à¤Ÿ", "blight", "rust", "à¦®à¦°à¦¿à¦šà¦¾", "à¦¦à¦¾à¦—à¦¯à§à¦•à§à¦¤", "à¦à¦²à¦¸à¦¾à¦¨à§‹", "dhabba", "dhabbe", "daag"]):
        if lang == "bn":
            return f"{crop_disp} à¦—à¦¾à¦›à§‡à¦° à¦ªà¦¾à¦¤à¦¾à¦¯à¦¼ à¦¬à¦¾à¦¦à¦¾à¦®à§€ à¦¬à¦¾ à¦•à¦¾à¦²à§‹ à¦¦à¦¾à¦— à¦¸à¦¾à¦§à¦¾à¦°à¦£à¦¤ à¦›à¦¤à§à¦°à¦¾à¦•à¦œà¦¨à¦¿à¦¤ à¦¬à§à¦²à¦¾à¦‡à¦Ÿ à¦¬à¦¾ à¦¬à§à¦°à¦¾à¦‰à¦¨ à¦¸à§à¦ªà¦Ÿ à¦°à§‹à¦—à¥¤ à¦†à¦•à§à¦°à¦¾à¦¨à§à¦¤ à¦ªà¦¾à¦¤à¦¾ à¦¸à¦°à¦¿à¦¯à¦¼à§‡ à¦«à§‡à¦²à§à¦¨ à¦à¦¬à¦‚ à¦®à§à¦¯à¦¾à¦¨à¦•à§‹à¦œà§‡à¦¬ à¦¬à¦¾ à¦¸à¦¾à¦« à¦ªà§à¦°à¦¤à¦¿ à¦²à¦¿à¦Ÿà¦¾à¦° à¦œà¦²à§‡ à¦¦à§à¦‡ à¦—à§à¦°à¦¾à¦® à¦—à§à¦²à§‡ à¦¸à§à¦ªà§à¦°à§‡ à¦•à¦°à§à¦¨à¥¤ à¦œà¦®à¦¿à¦¤à§‡ à¦…à¦¤à¦¿à¦°à¦¿à¦•à§à¦¤ à¦‡à¦‰à¦°à¦¿à¦¯à¦¼à¦¾ à¦¦à§‡à¦“à¦¯à¦¼à¦¾ à¦¬à¦¨à§à¦§ à¦°à¦¾à¦–à§à¦¨à¥¤"
        elif lang == "hi":
            return f"{crop_disp} à¤•à¥€ à¤ªà¤¤à¥à¤¤à¤¿à¤¯à¥‹à¤‚ à¤ªà¤° à¤­à¥‚à¤°à¥‡ à¤¯à¤¾ à¤•à¤¾à¤²à¥‡ à¤§à¤¬à¥à¤¬à¥‡ à¤•à¤µà¤• à¤œà¤¨à¤¿à¤¤ à¤¬à¥à¤²à¤¾à¤‡à¤Ÿ à¤¯à¤¾ à¤Ÿà¤¿à¤•à¥à¤•à¤¾ à¤°à¥‹à¤— à¤•à¥‡ à¤²à¤•à¥à¤·à¤£ à¤¹à¥‹ à¤¸à¤•à¤¤à¥‡ à¤¹à¥ˆà¤‚à¥¤ à¤¬à¤šà¤¾à¤µ à¤•à¥‡ à¤²à¤¿à¤ à¤¸à¤¾à¤« à¤¯à¤¾ à¤®à¥ˆà¤‚à¤•à¥‹à¤œà¥‡à¤¬ 2 à¤—à¥à¤°à¤¾à¤® à¤ªà¥à¤°à¤¤à¤¿ à¤²à¥€à¤Ÿà¤° à¤ªà¤¾à¤¨à¥€ à¤®à¥‡à¤‚ à¤®à¤¿à¤²à¤¾à¤•à¤° à¤›à¤¿à¤¡à¤¼à¤•à¥‡à¤‚ à¤”à¤° à¤…à¤¤à¤¿à¤°à¤¿à¤•à¥à¤¤ à¤¯à¥‚à¤°à¤¿à¤¯à¤¾ à¤¨ à¤¡à¤¾à¤²à¥‡à¤‚à¥¤"
        else:
            return f"Dark or brown spots on {crop_disp} leaves typically indicate fungal leaf spot or blight. Prune severely infected foliage and spray Mancozeb or Saaf at 2 grams per liter, avoiding excess nitrogen."

    # 5. YELLOW LEAVES & CHLOROSIS ("à¦ªà¦¾à¦¤à¦¾ à¦¹à¦²à§à¦¦", "à¤ªà¤¤à¥à¤¤à¤¿à¤¯à¤¾à¤‚ à¤ªà¥€à¤²à¥€", "yellow leaves")
    if any(w in q_lower for w in ["yellow", "peela", "peeli", "peele", "holud", "à¦ªà¦¿à¦²à¦¾", "à¦¹à¦²à§à¦¦", "à¤ªà¥€à¤²à¤¾", "à¤ªà¥€à¤²à¥€", "à¤ªà¥€à¤²à¥‡", "à¤ªà¥€à¤²à¤¾à¤ªà¤¨", "chlorosis", "à¦«à§à¦¯à¦¾à¦•à¦¾à¦¶à§‡"]):
        if lang == "bn":
            return f"{crop_disp} à¦—à¦¾à¦›à§‡à¦° à¦ªà¦¾à¦¤à¦¾ à¦¹à¦²à§à¦¦ à¦¹à¦“à¦¯à¦¼à¦¾à¦° à¦ªà§à¦°à¦§à¦¾à¦¨ à¦•à¦¾à¦°à¦£ à¦¨à¦¾à¦‡à¦Ÿà§à¦°à§‹à¦œà§‡à¦¨ à¦¬à¦¾ à¦œà¦¿à¦‚à¦•à§‡à¦° à¦˜à¦¾à¦Ÿà¦¤à¦¿, à¦…à¦¥à¦¬à¦¾ à¦…à¦¤à¦¿à¦°à¦¿à¦•à§à¦¤ à¦œà¦² à¦œà¦®à§‡ à¦¶à¦¿à¦•à¦¡à¦¼ à¦¶à§à¦¬à¦¾à¦¸à¦°à§à¦¦à§à¦§ à¦¹à¦“à¦¯à¦¼à¦¾à¥¤ à¦œà¦®à¦¿à¦¤à§‡ à¦œà¦² à¦œà¦®à¦²à§‡ à¦¨à¦¿à¦•à¦¾à¦¶ à¦•à¦°à§à¦¨ à¦à¦¬à¦‚ à¦ªà§à¦°à¦¤à¦¿ à¦²à¦¿à¦Ÿà¦¾à¦° à¦œà¦²à§‡ à¦ªà¦¨à§‡à¦°à§‹ à¦—à§à¦°à¦¾à¦® à¦‡à¦‰à¦°à¦¿à¦¯à¦¼à¦¾ à¦“ à¦¦à§à¦‡ à¦—à§à¦°à¦¾à¦® à¦šà¦¿à¦²à§‡à¦Ÿà§‡à¦¡ à¦œà¦¿à¦‚à¦• à¦®à¦¿à¦¶à¦¿à¦¯à¦¼à§‡ à¦¸à§à¦ªà§à¦°à§‡ à¦•à¦°à§à¦¨à¥¤"
        elif lang == "hi":
            return f"{crop_disp} à¤®à¥‡à¤‚ à¤ªà¤¤à¥à¤¤à¤¿à¤¯à¤¾à¤‚ à¤ªà¥€à¤²à¥€ à¤ªà¤¡à¤¼à¤¨à¤¾ à¤®à¥à¤–à¥à¤¯ à¤°à¥‚à¤ª à¤¸à¥‡ à¤¨à¤¾à¤‡à¤Ÿà¥à¤°à¥‹à¤œà¤¨ à¤¯à¤¾ à¤œà¤¿à¤‚à¤• à¤•à¥€ à¤•à¤®à¥€ à¤…à¤¥à¤µà¤¾ à¤œà¤²à¤­à¤°à¤¾à¤µ à¤•à¤¾ à¤¸à¤‚à¤•à¥‡à¤¤ à¤¹à¥ˆà¥¤ à¤–à¥‡à¤¤ à¤¸à¥‡ à¤…à¤¤à¤¿à¤°à¤¿à¤•à¥à¤¤ à¤ªà¤¾à¤¨à¥€ à¤¨à¤¿à¤•à¤¾à¤²à¥‡à¤‚ à¤”à¤° 15 à¤—à¥à¤°à¤¾à¤® à¤¯à¥‚à¤°à¤¿à¤¯à¤¾ à¤¤à¤¥à¤¾ 2 à¤—à¥à¤°à¤¾à¤® à¤šà¤¿à¤²à¥‡à¤Ÿà¥‡à¤¡ à¤œà¤¿à¤‚à¤• à¤ªà¥à¤°à¤¤à¤¿ à¤²à¥€à¤Ÿà¤° à¤ªà¤¾à¤¨à¥€ à¤®à¥‡à¤‚ à¤®à¤¿à¤²à¤¾à¤•à¤° à¤¸à¥à¤ªà¥à¤°à¥‡ à¤•à¤°à¥‡à¤‚à¥¤"
        else:
            return f"Leaf yellowing in {crop_disp} typically stems from Nitrogen or Zinc deficiency, or root waterlogging. Ensure soil drains well and apply a foliar spray of 1.5% Urea with 2g/L Chelated Zinc."

    # 6. FERTILIZER & NPK NUTRITION ("à¦¸à¦¾à¦°", "à¦‡à¦‰à¦°à¦¿à¦¯à¦¼à¦¾", "à¤–à¤¾à¤¦", "à¤¯à¥‚à¤°à¤¿à¤¯à¤¾", "fertilizer", "dap", "potash")
    if any(w in q_lower for w in ["fertilizer", "urea", "dap", "potash", "khad", "npk", "à¤–à¤¾à¤¦", "à¦¸à¦¾à¦°", "à¤¯à¥‚à¤°à¤¿à¤¯à¤¾", "à¤ªà¥‹à¤Ÿà¤¾à¤¶", "à¦¸à¦¾à¦° à¦ªà§à¦°à¦¯à¦¼à§‹à¦—", "khad kab", "yuriya"]):
        if lang == "bn":
            return f"{crop_disp} à¦«à¦¸à¦²à§‡à¦° à¦œà¦¨à§à¦¯ à¦œà¦®à¦¿à¦¤à§‡ à¦ªà¦°à§à¦¯à¦¾à¦ªà§à¦¤ à¦†à¦°à§à¦¦à§à¦°à¦¤à¦¾ à¦¥à¦¾à¦•à¦¾ à¦…à¦¬à¦¸à§à¦¥à¦¾à¦¯à¦¼ à¦‡à¦‰à¦°à¦¿à¦¯à¦¼à¦¾, à¦¡à¦¿à¦à¦ªà¦¿ à¦“ à¦ªà¦Ÿà¦¾à¦¶ à¦¸à§à¦·à¦® à¦…à¦¨à§à¦ªà¦¾à¦¤à§‡ à¦¦à¦¿à¦¨à¥¤ à¦‡à¦‰à¦°à¦¿à¦¯à¦¼à¦¾ à¦à¦•à¦¬à¦¾à¦°à§‡ à¦¨à¦¾ à¦¦à¦¿à¦¯à¦¼à§‡ à¦¦à§à¦‡ à¦¥à§‡à¦•à§‡ à¦¤à¦¿à¦¨ à¦•à¦¿à¦¸à§à¦¤à¦¿à¦¤à§‡ à¦¦à¦¿à¦²à§‡ à¦—à¦¾à¦› à¦¸à¦¬à¦šà§‡à¦¯à¦¼à§‡ à¦¬à§‡à¦¶à¦¿ à¦ªà§à¦·à§à¦Ÿà¦¿ à¦—à§à¦°à¦¹à¦£ à¦•à¦°à¦¤à§‡ à¦ªà¦¾à¦°à§‡à¥¤"
        elif lang == "hi":
            return f"{crop_disp} à¤®à¥‡à¤‚ à¤–à¤¾à¤¦ à¤¹à¤®à¥‡à¤¶à¤¾ à¤®à¤¿à¤Ÿà¥à¤Ÿà¥€ à¤®à¥‡à¤‚ à¤ªà¤°à¥à¤¯à¤¾à¤ªà¥à¤¤ à¤¨à¤®à¥€ à¤¹à¥‹à¤¨à¥‡ à¤ªà¤° à¤¹à¥€ à¤¦à¥‡à¤‚à¥¤ à¤¯à¥‚à¤°à¤¿à¤¯à¤¾ à¤•à¥‹ à¤à¤• à¤¸à¤¾à¤¥ à¤¨ à¤¡à¤¾à¤²à¤•à¤° à¤¦à¥‹ à¤¸à¥‡ à¤¤à¥€à¤¨ à¤¬à¤¾à¤° à¤®à¥‡à¤‚ à¤¬à¤¾à¤à¤Ÿà¤•à¤° à¤¦à¥‡à¤¨à¤¾ à¤…à¤§à¤¿à¤• à¤«à¤¾à¤¯à¤¦à¥‡à¤®à¤‚à¤¦ à¤¹à¥ˆà¥¤ à¤¸à¥‚à¤–à¥€ à¤œà¤®à¥€à¤¨ à¤®à¥‡à¤‚ à¤¯à¥‚à¤°à¤¿à¤¯à¤¾ à¤•à¤­à¥€ à¤¨ à¤¡à¤¾à¤²à¥‡à¤‚à¥¤"
        else:
            return f"Apply balanced NPK fertilizers for {crop_disp} only when soil has adequate moisture. Splitting Urea into 2 to 3 split doses boosts nitrogen use efficiency significantly."

    # 7. PESTS, INSECTS & BORERS ("à¦ªà§‹à¦•à¦¾", "à¦•à§€à¦Ÿ", "à¤•à¥€à¤Ÿ", "à¤®à¤°à¥‹à¤¡à¤¼", "pest", "borer", "worm")
    if any(w in q_lower for w in ["pest", "insect", "worm", "borer", "aphid", "à¦•à§€à¦Ÿ", "à¦•à§€à¦¡à¦¼à¦¾", "à¦ªà§‹à¦•à¦¾", "à¦®à¦¾à¦œà¦°à¦¾", "à¦•à§€à¦Ÿà¦ªà¦¤à¦™à§à¦—", "à¤•à¥€à¤Ÿ", "à¤•à¥€à¤¡à¤¼à¤¾", "à¤®à¤¾à¤¹à¥‚", "à¤¸à¥à¤‚à¤¡à¥€", "keeda", "keede", "poka"]):
        if lang == "bn":
            return f"{crop_disp} à¦«à¦¸à¦²à§‡ à¦ªà§‹à¦•à¦¾à¦° à¦†à¦•à§à¦°à¦®à¦£ à¦°à§à¦–à¦¤à§‡ à¦ªà§à¦°à¦¥à¦®à§‡ à¦¨à¦¿à¦® à¦¤à§‡à¦² à¦ªà§à¦°à¦¤à¦¿ à¦²à¦¿à¦Ÿà¦¾à¦° à¦œà¦²à§‡ à¦¤à¦¿à¦¨ à¦®à¦¿à¦²à¦¿ à¦®à¦¿à¦¶à¦¿à¦¯à¦¼à§‡ à¦¸à¦•à¦¾à¦²à§‡ à¦¸à§à¦ªà§à¦°à§‡ à¦•à¦°à§à¦¨à¥¤ à¦®à¦¾à¦œà¦°à¦¾ à¦ªà§‹à¦•à¦¾à¦° à¦ªà§à¦°à¦•à§‹à¦ª à¦¥à¦¾à¦•à¦²à§‡ à¦œà¦®à¦¿à¦¤à§‡ à¦«à§‡à¦°à§‹à¦®à§‹à¦¨ à¦«à¦¾à¦à¦¦ à¦²à¦¾à¦—à¦¾à¦¨ à¦à¦¬à¦‚ à¦ªà§à¦°à¦¯à¦¼à§‹à¦œà¦¨à§‡ à¦•à¦¾à¦°à§à¦Ÿà¦¾à¦ª à¦¬à¦¾ à¦•à§‹à¦°à¦¾à¦œà¦¨ à¦¬à§à¦¯à¦¬à¦¹à¦¾à¦° à¦•à¦°à§à¦¨à¥¤"
        elif lang == "hi":
            return f"{crop_disp} à¤®à¥‡à¤‚ à¤•à¥€à¤Ÿà¥‹à¤‚ à¤¸à¥‡ à¤¬à¤šà¤¾à¤µ à¤•à¥‡ à¤²à¤¿à¤ à¤¨à¥€à¤® à¤¤à¥‡à¤² 3 à¤®à¤¿à¤²à¥€ à¤ªà¥à¤°à¤¤à¤¿ à¤²à¥€à¤Ÿà¤° à¤ªà¤¾à¤¨à¥€ à¤®à¥‡à¤‚ à¤®à¤¿à¤²à¤¾à¤•à¤° à¤›à¤¿à¤¡à¤¼à¤•à¥‡à¤‚à¥¤ à¤¤à¤¨à¤¾ à¤›à¥‡à¤¦à¤• à¤¯à¤¾ à¤¸à¥à¤‚à¤¡à¥€ à¤•à¤¾ à¤ªà¥à¤°à¤•à¥‹à¤ª à¤…à¤§à¤¿à¤• à¤¹à¥‹à¤¨à¥‡ à¤ªà¤° à¤«à¥‡à¤°à¥‹à¤®à¥‹à¤¨ à¤Ÿà¥à¤°à¥ˆà¤ª à¤²à¤—à¤¾à¤à¤‚ à¤”à¤° à¤•à¥‹à¤°à¤¾à¤œà¤¨ à¤•à¤¾ à¤›à¤¿à¤¡à¤¼à¤•à¤¾à¤µ à¤•à¤°à¥‡à¤‚à¥¤"
                
        else:
            return f"For pest defense on {crop_disp}, start with cold-pressed Neem Oil at 3 ml per liter. For stem borers or caterpillars, install pheromone traps and apply Chlorantraniliprole under guidance."

    # 4. YELLOW LEAVES & CHLOROSIS ("à¦ªà¦¾à¦¤à¦¾ à¦¹à¦²à§à¦¦", "à¤ªà¤¤à¥à¤¤à¤¿à¤¯à¤¾à¤‚ à¤ªà¥€à¤²à¥€", "yellow leaves")
    if any(w in q_lower for w in ["yellow", "peela", "peeli", "peele", "holud", "à¦ªà¦¿à¦²à¦¾", "à¦¹à¦²à§à¦¦", "à¤ªà¥€à¤²à¤¾", "à¤ªà¥€à¤²à¥€", "à¤ªà¥€à¤²à¥‡", "à¤ªà¥€à¤²à¤¾à¤ªà¤¨", "chlorosis", "à¦«à§à¦¯à¦¾à¦•à¦¾à¦¶à§‡"]):
        if lang == "bn":
            return f"{crop_disp} à¦—à¦¾à¦›à§‡à¦° à¦ªà¦¾à¦¤à¦¾ à¦¹à¦²à§à¦¦ à¦¹à¦“à¦¯à¦¼à¦¾à¦° à¦ªà§à¦°à¦§à¦¾à¦¨ à¦•à¦¾à¦°à¦£ à¦¨à¦¾à¦‡à¦Ÿà§à¦°à§‹à¦œà§‡à¦¨ à¦¬à¦¾ à¦œà¦¿à¦‚à¦•à§‡à¦° à¦˜à¦¾à¦Ÿà¦¤à¦¿, à¦…à¦¥à¦¬à¦¾ à¦…à¦¤à¦¿à¦°à¦¿à¦•à§à¦¤ à¦œà¦² à¦œà¦®à§‡ à¦¶à¦¿à¦•à¦¡à¦¼ à¦¶à§à¦¬à¦¾à¦¸à¦°à§à¦¦à§à¦§ à¦¹à¦“à¦¯à¦¼à¦¾à¥¤ à¦œà¦®à¦¿à¦¤à§‡ à¦œà¦² à¦œà¦®à¦²à§‡ à¦¨à¦¿à¦•à¦¾à¦¶ à¦•à¦°à§à¦¨ à¦à¦¬à¦‚ à¦ªà§à¦°à¦¤à¦¿ à¦²à¦¿à¦Ÿà¦¾à¦° à¦œà¦²à§‡ à¦ªà¦¨à§‡à¦°à§‹ à¦—à§à¦°à¦¾à¦® à¦‡à¦‰à¦°à¦¿à¦¯à¦¼à¦¾ à¦“ à¦¦à§à¦‡ à¦—à§à¦°à¦¾à¦® à¦šà¦¿à¦²à§‡à¦Ÿà§‡à¦¡ à¦œà¦¿à¦‚à¦• à¦®à¦¿à¦¶à¦¿à¦¯à¦¼à§‡ à¦¸à§à¦ªà§à¦°à§‡ à¦•à¦°à§à¦¨à¥¤"
        elif lang == "hi":
            return f"{crop_disp} à¤®à¥‡à¤‚ à¤ªà¤¤à¥à¤¤à¤¿à¤¯à¤¾à¤‚ à¤ªà¥€à¤²à¥€ à¤ªà¤¡à¤¼à¤¨à¤¾ à¤®à¥à¤–à¥à¤¯ à¤°à¥‚à¤ª à¤¸à¥‡ à¤¨à¤¾à¤‡à¤Ÿà¥à¤°à¥‹à¤œà¤¨ à¤¯à¤¾ à¤œà¤¿à¤‚à¤• à¤•à¥€ à¤•à¤®à¥€ à¤…à¤¥à¤µà¤¾ à¤œà¤²à¤­à¤°à¤¾à¤µ à¤•à¤¾ à¤¸à¤‚à¤•à¥‡à¤¤ à¤¹à¥ˆà¥¤ à¤–à¥‡à¤¤ à¤¸à¥‡ à¤…à¤¤à¤¿à¤°à¤¿à¤•à¥à¤¤ à¤ªà¤¾à¤¨à¥€ à¤¨à¤¿à¤•à¤¾à¤²à¥‡à¤‚ à¤”à¤° 15 à¤—à¥à¤°à¤¾à¤® à¤¯à¥‚à¤°à¤¿à¤¯à¤¾ à¤¤à¤¥à¤¾ 2 à¤—à¥à¤°à¤¾à¤® à¤šà¤¿à¤²à¥‡à¤Ÿà¥‡à¤¡ à¤œà¤¿à¤‚à¤• à¤ªà¥à¤°à¤¤à¤¿ à¤²à¥€à¤Ÿà¤° à¤ªà¤¾à¤¨à¥€ à¤®à¥‡à¤‚ à¤®à¤¿à¤²à¤¾à¤•à¤° à¤¸à¥à¤ªà¥à¤°à¥‡ à¤•à¤°à¥‡à¤‚à¥¤"
        else:
            return f"Leaf yellowing in {crop_disp} typically stems from Nitrogen or Zinc deficiency, or root waterlogging. Ensure soil drains well and apply a foliar spray of 1.5% Urea with 2g/L Chelated Zinc."

    # 5. IRRIGATION & WATER MANAGEMENT ("à¦¸à§‡à¦š", "à¦œà¦² à¦¦à§‡à¦¬", "à¦ªà¦¾à¦¨à¦¿", "à¤¸à¤¿à¤‚à¤šà¤¾à¤ˆ", "water", "irrigate")
    if any(w in q_lower for w in ["water", "irrigate", "irrigation", "à¦ªà¦¾à¦¨à¦¿", "à¤¸à¤¿à¤‚à¤šà¤¾à¤ˆ", "à¦¸à§‡à¦š", "à¦œà¦²", "à¤ªà¤¾à¤¨à¥€ à¤•à¤¬"]):
        is_wet = soil_moisture and ("wet" in soil_moisture.lower() or "humid" in soil_moisture.lower() or "adequate" in soil_moisture.lower())
        if is_wet or rain_chance > 50:
            if lang == "bn":
                return f"à¦†à¦ªà¦¨à¦¾à¦° {location} à¦…à¦žà§à¦šà¦²à§‡à¦° à¦®à¦¾à¦Ÿà¦¿à¦¤à§‡ à¦¬à¦°à§à¦¤à¦®à¦¾à¦¨à§‡ à¦ªà¦°à§à¦¯à¦¾à¦ªà§à¦¤ à¦†à¦°à§à¦¦à§à¦°à¦¤à¦¾ à¦°à¦¯à¦¼à§‡à¦›à§‡ à¦à¦¬à¦‚ à¦¬à§ƒà¦·à§à¦Ÿà¦¿à¦° à¦¸à¦®à§à¦­à¦¾à¦¬à¦¨à¦¾ {rain_chance}%à¥¤ à¦†à¦œ à¦¨à¦¤à§à¦¨ à¦•à¦°à§‡ à¦¸à§‡à¦š à¦¦à§‡à¦“à¦¯à¦¼à¦¾à¦° à¦ªà§à¦°à¦¯à¦¼à§‹à¦œà¦¨ à¦¨à§‡à¦‡, à¦…à¦¤à¦¿à¦°à¦¿à¦•à§à¦¤ à¦œà¦²à§‡ à¦¶à¦¿à¦•à¦¡à¦¼ à¦ªà¦šà§‡ à¦¯à§‡à¦¤à§‡ à¦ªà¦¾à¦°à§‡à¥¤"
            elif lang == "hi":
                return f"à¤†à¤ªà¤•à¥‡ à¤–à¥‡à¤¤ à¤®à¥‡à¤‚ à¤…à¤­à¥€ à¤ªà¤°à¥à¤¯à¤¾à¤ªà¥à¤¤ à¤¨à¤®à¥€ à¤®à¥Œà¤œà¥‚à¤¦ à¤¹à¥ˆ à¤”à¤° à¤¬à¤¾à¤°à¤¿à¤¶ à¤•à¥€ à¤¸à¤‚à¤­à¤¾à¤µà¤¨à¤¾ {rain_chance}% à¤¹à¥ˆà¥¤ à¤†à¤œ {crop_disp} à¤®à¥‡à¤‚ à¤…à¤¤à¤¿à¤°à¤¿à¤•à¥à¤¤ à¤¸à¤¿à¤‚à¤šà¤¾à¤ˆ à¤¨ à¤•à¤°à¥‡à¤‚, à¤¤à¤¾à¤•à¤¿ à¤œà¤¡à¤¼ à¤—à¤²à¤¨ à¤¸à¥‡ à¤¬à¤šà¤¾à¤µ à¤¹à¥‹ à¤¸à¤•à¥‡à¥¤"
            else:
                return f"Your soil in {location} currently has adequate moisture with {rain_chance}% rain forecast. Do not irrigate today to avoid waterlogging."
        else:
            if lang == "bn":
                return f"à¦®à¦¾à¦Ÿà¦¿à¦° à¦‰à¦ªà¦°à¦¿à¦­à¦¾à¦— à¦ªà¦°à§€à¦•à§à¦·à¦¾ à¦•à¦°à§‡ à¦¦à§‡à¦–à§à¦¨à¥¤ à¦¯à¦¦à¦¿ {crop_disp} à¦—à¦¾à¦›à§‡à¦° à¦—à§‹à¦¡à¦¼à¦¾à¦¯à¦¼ à¦®à¦¾à¦Ÿà¦¿ à¦¶à§à¦·à§à¦• à¦¥à¦¾à¦•à§‡, à¦¤à¦¬à§‡ à¦¬à¦¿à¦•à§‡à¦²à§‡ à¦¹à¦¾à¦²à¦•à¦¾ à¦¸à§‡à¦š à¦¦à¦¿à¦¨à¥¤ à¦–à§‡à¦¯à¦¼à¦¾à¦² à¦°à¦¾à¦–à¦¬à§‡à¦¨ à¦¯à§‡à¦¨ à¦œà¦®à¦¿à¦¤à§‡ à¦œà¦² à¦¦à§€à¦°à§à¦˜à¦•à§à¦·à¦£ à¦œà¦®à§‡ à¦¨à¦¾ à¦¥à¦¾à¦•à§‡à¥¤"
            elif lang == "hi":
                return f"à¤–à¥‡à¤¤ à¤•à¥€ à¤Šà¤ªà¤°à¥€ à¤®à¤¿à¤Ÿà¥à¤Ÿà¥€ à¤¸à¥‚à¤– à¤°à¤¹à¥€ à¤¹à¥ˆ à¤¤à¥‹ à¤†à¤œ à¤¶à¤¾à¤® à¤¹à¤²à¥à¤•à¥€ à¤¸à¤¿à¤‚à¤šà¤¾à¤ˆ à¤•à¤°à¥‡à¤‚à¥¤ à¤…à¤¤à¥à¤¯à¤§à¤¿à¤• à¤ªà¤¾à¤¨à¥€ à¤•à¤¾ à¤­à¤°à¤¾à¤µ à¤¨ à¤¹à¥‹à¤¨à¥‡ à¤¦à¥‡à¤‚ à¤”à¤° à¤®à¥‡à¤¡à¤¼ à¤¸à¥à¤°à¤•à¥à¤·à¤¿à¤¤ à¤°à¤–à¥‡à¤‚à¥¤"
            else:
                return f"Check your field surface. If topsoil is dry around your {crop_disp}, apply a light irrigation this evening without flooding."

    # 6. FERTILIZER & NPK NUTRITION ("à¦¸à¦¾à¦°", "à¦‡à¦‰à¦°à¦¿à¦¯à¦¼à¦¾", "à¤–à¤¾à¤¦", "à¤¯à¥‚à¤°à¤¿à¤¯à¤¾", "fertilizer", "dap", "potash")
    if any(w in q_lower for w in ["fertilizer", "urea", "dap", "potash", "khad", "npk", "à¤–à¤¾à¤¦", "à¦¸à¦¾à¦°", "à¤¯à¥‚à¤°à¤¿à¤¯à¤¾", "à¤ªà¥‹à¤Ÿà¤¾à¤¶", "à¦¸à¦¾à¦° à¦ªà§à¦°à¦¯à¦¼à§‹à¦—"]):
        if lang == "bn":
            return f"{crop_disp} à¦«à¦¸à¦²à§‡à¦° à¦œà¦¨à§à¦¯ à¦œà¦®à¦¿à¦¤à§‡ à¦ªà¦°à§à¦¯à¦¾à¦ªà§à¦¤ à¦†à¦°à§à¦¦à§à¦°à¦¤à¦¾ à¦¥à¦¾à¦•à¦¾ à¦…à¦¬à¦¸à§à¦¥à¦¾à¦¯à¦¼ à¦‡à¦‰à¦°à¦¿à¦¯à¦¼à¦¾, à¦¡à¦¿à¦à¦ªà¦¿ à¦“ à¦ªà¦Ÿà¦¾à¦¶ à¦¸à§à¦·à¦® à¦…à¦¨à§à¦ªà¦¾à¦¤à§‡ à¦¦à¦¿à¦¨à¥¤ à¦‡à¦‰à¦°à¦¿à¦¯à¦¼à¦¾ à¦à¦•à¦¬à¦¾à¦°à§‡ à¦¨à¦¾ à¦¦à¦¿à¦¯à¦¼à§‡ à¦¦à§à¦‡ à¦¥à§‡à¦•à§‡ à¦¤à¦¿à¦¨ à¦•à¦¿à¦¸à§à¦¤à¦¿à¦¤à§‡ à¦¦à¦¿à¦²à§‡ à¦—à¦¾à¦› à¦¸à¦¬à¦šà§‡à¦¯à¦¼à§‡ à¦¬à§‡à¦¶à¦¿ à¦ªà§à¦·à§à¦Ÿà¦¿ à¦—à§à¦°à¦¹à¦£ à¦•à¦°à¦¤à§‡ à¦ªà¦¾à¦°à§‡à¥¤"
        elif lang == "hi":
            return f"{crop_disp} à¤®à¥‡à¤‚ à¤–à¤¾à¤¦ à¤¹à¤®à¥‡à¤¶à¤¾ à¤®à¤¿à¤Ÿà¥à¤Ÿà¥€ à¤®à¥‡à¤‚ à¤ªà¤°à¥à¤¯à¤¾à¤ªà¥à¤¤ à¤¨à¤®à¥€ à¤¹à¥‹à¤¨à¥‡ à¤ªà¤° à¤¹à¥€ à¤¦à¥‡à¤‚à¥¤ à¤¯à¥‚à¤°à¤¿à¤¯à¤¾ à¤•à¥‹ à¤à¤• à¤¸à¤¾à¤¥ à¤¨ à¤¡à¤¾à¤²à¤•à¤° à¤¦à¥‹ à¤¸à¥‡ à¤¤à¥€à¤¨ à¤¬à¤¾à¤° à¤®à¥‡à¤‚ à¤¬à¤¾à¤à¤Ÿà¤•à¤° à¤¦à¥‡à¤¨à¤¾ à¤…à¤§à¤¿à¤• à¤«à¤¾à¤¯à¤¦à¥‡à¤®à¤‚à¤¦ à¤¹à¥ˆà¥¤ à¤¸à¥‚à¤–à¥€ à¤œà¤®à¥€à¤¨ à¤®à¥‡à¤‚ à¤¯à¥‚à¤°à¤¿à¤¯à¤¾ à¤•à¤­à¥€ à¤¨ à¤¡à¤¾à¤²à¥‡à¤‚à¥¤"
        else:
            return f"Apply balanced NPK fertilizers for {crop_disp} only when soil has adequate moisture. Splitting Urea into 2 to 3 split doses boosts nitrogen use efficiency significantly."

    # 7. PESTS, INSECTS & BORERS ("à¦ªà§‹à¦•à¦¾", "à¦•à§€à¦Ÿ", "à¤•à¥€à¤Ÿ", "à¤®à¤°à¥‹à¤¡à¤¼", "pest", "borer", "worm")
    if any(w in q_lower for w in ["pest", "insect", "worm", "borer", "aphid", "à¦•à§€à¦Ÿ", "à¦•à§€à¦¡à¦¼à¦¾", "à¦ªà§‹à¦•à¦¾", "à¦®à¦¾à¦œà¦°à¦¾", "à¦•à§€à¦Ÿà¦ªà¦¤à¦™à§à¦—", "à¤•à¥€à¤Ÿ", "à¤•à¥€à¤¡à¤¼à¤¾", "à¤®à¤¾à¤¹à¥‚", "à¤¸à¥à¤‚à¤¡à¥€"]):
        if lang == "bn":
            return f"{crop_disp} à¦«à¦¸à¦²à§‡ à¦ªà§‹à¦•à¦¾à¦° à¦†à¦•à§à¦°à¦®à¦£ à¦°à§à¦–à¦¤à§‡ à¦ªà§à¦°à¦¥à¦®à§‡ à¦¨à¦¿à¦® à¦¤à§‡à¦² à¦ªà§à¦°à¦¤à¦¿ à¦²à¦¿à¦Ÿà¦¾à¦° à¦œà¦²à§‡ à¦¤à¦¿à¦¨ à¦®à¦¿à¦²à¦¿ à¦®à¦¿à¦¶à¦¿à¦¯à¦¼à§‡ à¦¸à¦•à¦¾à¦²à§‡ à¦¸à§à¦ªà§à¦°à§‡ à¦•à¦°à§à¦¨à¥¤ à¦®à¦¾à¦œà¦°à¦¾ à¦ªà§‹à¦•à¦¾à¦° à¦ªà§à¦°à¦•à§‹à¦ª à¦¥à¦¾à¦•à¦²à§‡ à¦œà¦®à¦¿à¦¤à§‡ à¦«à§‡à¦°à§‹à¦®à§‹à¦¨ à¦«à¦¾à¦à¦¦ à¦²à¦¾à¦—à¦¾à¦¨ à¦à¦¬à¦‚ à¦ªà§à¦°à¦¯à¦¼à§‹à¦œà¦¨à§‡ à¦•à¦¾à¦°à§à¦Ÿà¦¾à¦ª à¦¬à¦¾ à¦•à§‹à¦°à¦¾à¦œà¦¨ à¦¬à§à¦¯à¦¬à¦¹à¦¾à¦° à¦•à¦°à§à¦¨à¥¤"
        elif lang == "hi":
            return f"{crop_disp} à¤®à¥‡à¤‚ à¤•à¥€à¤Ÿà¥‹à¤‚ à¤¸à¥‡ à¤¬à¤šà¤¾à¤µ à¤•à¥‡ à¤²à¤¿à¤ à¤¨à¥€à¤® à¤¤à¥‡à¤² 3 à¤®à¤¿à¤²à¥€ à¤ªà¥à¤°à¤¤à¤¿ à¤²à¥€à¤Ÿà¤° à¤ªà¤¾à¤¨à¥€ à¤®à¥‡à¤‚ à¤®à¤¿à¤²à¤¾à¤•à¤° à¤›à¤¿à¤¡à¤¼à¤•à¥‡à¤‚à¥¤ à¤¤à¤¨à¤¾ à¤›à¥‡à¤¦à¤• à¤¯à¤¾ à¤¸à¥à¤‚à¤¡à¥€ à¤•à¤¾ à¤ªà¥à¤°à¤•à¥‹à¤ª à¤…à¤§à¤¿à¤• à¤¹à¥‹à¤¨à¥‡ à¤ªà¤° à¤«à¥‡à¤°à¥‹à¤®à¥‹à¤¨ à¤Ÿà¥à¤°à¥ˆà¤ª à¤²à¤—à¤¾à¤à¤‚ à¤”à¤° à¤•à¥‹à¤°à¤¾à¤œà¤¨ à¤•à¤¾ à¤›à¤¿à¤¡à¤¼à¤•à¤¾à¤µ à¤•à¤°à¥‡à¤‚à¥¤"
        else:
            return f"For pest defense on {crop_disp}, start with cold-pressed Neem Oil at 3 ml per liter. For stem borers or caterpillars, install pheromone traps and apply Chlorantraniliprole under guidance."

    # 8. SOWING & SEED TREATMENT ("à¦¬à§€à¦œ", "à¦¬à¦ªà¦¨", "à¦¬à§à¦“à¦¯à¦¼à¦¾à¦‡", "à¤¬à¥€à¤œ", "à¤¬à¥à¤µà¤¾à¤ˆ", "seed", "sow")
    if any(w in q_lower for w in ["sow", "sowing", "seed", "à¦¬à¦ªà¦¨", "à¦¬à§€à¦œ", "à¦¬à§‹à¦¨à¦¾à¦°", "à¦¬à§à¦“à¦¯à¦¼à¦¾à¦‡", "à¤¬à¥à¤µà¤¾à¤ˆ", "à¤¬à¥€à¤œ", "à¦¬à¦¿à¦¹à¦¨"]):
        if lang == "bn":
            return f"{crop_disp} à¦¬à§‹à¦¨à¦¾à¦° à¦†à¦—à§‡ à¦Ÿà§à¦°à¦¾à¦‡à¦•à§‹à¦¡à¦¾à¦°à§à¦®à¦¾ à¦ªà§à¦°à¦¤à¦¿ à¦•à§‡à¦œà¦¿ à¦¬à§€à¦œà§‡ à¦ªà¦¾à¦à¦š à¦—à§à¦°à¦¾à¦® à¦…à¦¥à¦¬à¦¾ à¦•à¦¾à¦°à§à¦¬à§‡à¦¨à¦¡à¦¾à¦œà¦¿à¦® à¦¦à¦¿à¦¯à¦¼à§‡ à¦¬à§€à¦œ à¦¶à§‹à¦§à¦¨ à¦•à¦°à¦¾ à¦¬à¦¾à¦§à§à¦¯à¦¤à¦¾à¦®à§‚à¦²à¦•à¥¤ à¦à¦¤à§‡ à¦šà¦¾à¦°à¦¾ à¦§à¦¸à¦¾ à¦“ à¦¶à¦¿à¦•à¦¡à¦¼ à¦ªà¦šà¦¾ à¦°à§‹à¦— à¦¥à§‡à¦•à§‡ à¦¶à¦¤à¦­à¦¾à¦— à¦°à¦•à§à¦·à¦¾ à¦ªà¦¾à¦“à¦¯à¦¼à¦¾ à¦¯à¦¾à¦¯à¦¼à¥¤"
        elif lang == "hi":
            return f"{crop_disp} à¤•à¥€ à¤¬à¥à¤µà¤¾à¤ˆ à¤¸à¥‡ à¤ªà¤¹à¤²à¥‡ à¤¬à¥€à¤œà¥‹à¤ªà¤šà¤¾à¤° à¤…à¤µà¤¶à¥à¤¯ à¤•à¤°à¥‡à¤‚à¥¤ à¤Ÿà¥à¤°à¤¾à¤‡à¤•à¥‹à¤¡à¤°à¥à¤®à¤¾ 5 à¤—à¥à¤°à¤¾à¤® à¤ªà¥à¤°à¤¤à¤¿ à¤•à¤¿à¤²à¥‹ à¤¯à¤¾ à¤•à¤¾à¤°à¥à¤¬à¥‡à¤‚à¤¡à¤¾à¤œà¤¿à¤® à¤¸à¥‡ à¤¬à¥€à¤œ à¤¶à¥‹à¤§à¤¨ à¤•à¤°à¤¨à¥‡ à¤¸à¥‡ à¤œà¤®à¤¾à¤µ à¤…à¤šà¥à¤›à¤¾ à¤¹à¥‹à¤¤à¤¾ à¤¹à¥ˆ à¤”à¤° à¤«à¤«à¥‚à¤‚à¤¦ à¤¸à¥‡ à¤¸à¥à¤°à¤•à¥à¤·à¤¾ à¤®à¤¿à¤²à¤¤à¥€ à¤¹à¥ˆà¥¤"
        else:
            return f"Always treat seeds of {crop_disp} with Trichoderma (5g/kg) or Carbendazim before sowing to prevent seed-borne damping off and seedling blight."

    # 9. WEED CONTROL & MULCHING ("à¦†à¦—à¦¾à¦›à¦¾", "à¦˜à¦¾à¦¸", "à¤–à¤°à¤ªà¤¤à¤µà¤¾à¤°", "weed", "weeds")
    if any(w in q_lower for w in ["weed", "weeds", "à¦†à¦—à¦¾à¦›à¦¾", "à¦˜à¦¾à¦¸", "à¦–à¦°à¤ªà¤¤à¤µà¤¾à¤°", "à¤–à¤°à¤ªà¤¤à¤µà¤¾à¤°"]):
        if lang == "bn":
            return f"à¦šà¦¾à¦°à¦¾ à¦²à¦¾à¦—à¦¾à¦¨à§‹à¦° à¦¬à¦¿à¦¶ à¦¥à§‡à¦•à§‡ à¦ªà¦à¦šà¦¿à¦¶ à¦¦à¦¿à¦¨à§‡à¦° à¦®à¦§à§à¦¯à§‡ à¦ªà§à¦°à¦¥à¦® à¦¨à¦¿à¦¡à¦¼à¦¾à¦¨à¦¿ à¦¦à§‡à¦“à¦¯à¦¼à¦¾ à¦…à¦¤à§à¦¯à¦¨à§à¦¤ à¦œà¦°à§à¦°à¦¿à¥¤ à¦—à¦¾à¦›à§‡à¦° à¦—à§‹à¦¡à¦¼à¦¾à¦¯à¦¼ à¦¶à§à¦•à¦¨à§‹ à¦–à¦¡à¦¼à§‡à¦° à¦®à¦¾à¦²à¦šà¦¿à¦‚ à¦¦à¦¿à¦²à§‡ à¦†à¦—à¦¾à¦›à¦¾à¦° à¦‰à¦ªà¦¦à§à¦°à¦¬ à¦…à¦¨à§‡à¦•à¦Ÿà¦¾à¦‡ à¦•à¦®à§‡ à¦à¦¬à¦‚ à¦®à¦¾à¦Ÿà¦¿à¦° à¦°à¦¸ à¦¸à¦‚à¦°à¦•à§à¦·à¦¿à¦¤ à¦¥à¦¾à¦•à§‡à¥¤"
        elif lang == "hi":
            return f"à¤¬à¥à¤µà¤¾à¤ˆ à¤•à¥‡ 20 à¤¸à¥‡ 25 à¤¦à¤¿à¤¨ à¤¬à¤¾à¤¦ à¤ªà¤¹à¤²à¥€ à¤¨à¤¿à¤°à¤¾à¤ˆ-à¤—à¥à¤¡à¤¼à¤¾à¤ˆ à¤…à¤µà¤¶à¥à¤¯ à¤•à¤°à¥‡à¤‚à¥¤ à¤–à¤°à¤ªà¤¤à¤µà¤¾à¤° à¤«à¤¸à¤²à¥‹à¤‚ à¤•à¥€ à¤–à¥à¤°à¤¾à¤• à¤”à¤° à¤ªà¤¾à¤¨à¥€ à¤–à¥€à¤‚à¤š à¤²à¥‡à¤¤à¥‡ à¤¹à¥ˆà¤‚à¥¤ à¤œà¥ˆà¤µà¤¿à¤• à¤¨à¤¿à¤¯à¤‚à¤¤à¥à¤°à¤£ à¤•à¥‡ à¤²à¤¿à¤ à¤ªà¥à¤†à¤² à¤•à¥€ à¤®à¤²à¥à¤šà¤¿à¤‚à¤— à¤…à¤ªà¤¨à¤¾à¤à¤‚à¥¤"
        else:
            return f"Keep the critical 20 to 30 day window weed-free through manual hoeing or straw mulching to prevent moisture and nutrient competition."

    # 10. SOIL HEALTH, PH & ORGANIC CARBON ("à¦®à¦¾à¦Ÿà¦¿", "à¦®à¦¾à¦Ÿà¦¿à¦° à¦¸à§à¦¬à¦¾à¦¸à§à¦¥à§à¦¯", "pH", "à¤®à¤¿à¤Ÿà¥à¤Ÿà¥€", "soil")
    if any(w in q_lower for w in ["soil", "ph", "carbon", "à¦®à¦¾à¦Ÿà¦¿", "à¦…à¦®à§à¦²", "à¦‰à¦°à§à¦¬à¦°à¦¤à¦¾", "à¤®à¤¿à¤Ÿà¥à¤Ÿà¥€", "à¤‰à¤°à¥à¤µà¤°à¤¤à¤¾", "à¦•à¦¾à¦°à§à¦¬à¦¨"]):
        if lang == "bn":
            return f"{soil}-à¦° à¦‰à¦°à§à¦¬à¦°à¦¤à¦¾ à¦“ à¦œà§ˆà¦¬ à¦•à¦¾à¦°à§à¦¬à¦¨ à¦¬à¦¾à¦¡à¦¼à¦¾à¦¤à§‡ à¦ªà§à¦°à¦¤à¦¿ à¦à¦•à¦°à§‡ à§«-à§® à¦Ÿà¦¨ à¦—à§‹à¦¬à¦° à¦¸à¦¾à¦° à¦¬à¦¾ à¦•à§‡à¦à¦šà§‹ à¦¸à¦¾à¦° à¦¬à§à¦¯à¦¬à¦¹à¦¾à¦° à¦•à¦°à§à¦¨à¥¤ à¦ªà§à¦°à¦¤à¦¿ à¦¦à§à¦‡-à¦¤à¦¿à¦¨ à¦¬à¦›à¦° à¦…à¦¨à§à¦¤à¦° à¦§à¦‡à¦žà§à¦šà¦¾ à¦šà¦¾à¦· à¦•à¦°à§‡ à¦®à¦¾à¦Ÿà¦¿à¦¤à§‡ à¦®à¦¿à¦¶à¦¿à¦¯à¦¼à§‡ à¦¦à¦¿à¦²à§‡ à¦®à¦¾à¦Ÿà¦¿à¦° à¦¸à§à¦¬à¦¾à¦¸à§à¦¥à§à¦¯ à¦¦à¦¾à¦°à§à¦£ à¦¥à¦¾à¦•à§‡à¥¤"
        elif lang == "hi":
            return f"{soil} à¤®à¥‡à¤‚ à¤œà¥ˆà¤µà¤¿à¤• à¤•à¤¾à¤°à¥à¤¬à¤¨ à¤¬à¤¢à¤¼à¤¾à¤¨à¥‡ à¤•à¥‡ à¤²à¤¿à¤ à¤—à¥‹à¤¬à¤° à¤•à¥€ à¤–à¤¾à¤¦ à¤¯à¤¾ à¤µà¤°à¥à¤®à¥€à¤•à¤®à¥à¤ªà¥‹à¤¸à¥à¤Ÿ à¤•à¤¾ à¤ªà¥à¤°à¤¯à¥‹à¤— à¤•à¤°à¥‡à¤‚à¥¤ à¤¹à¤°à¥€ à¤–à¤¾à¤¦ à¤•à¥‡ à¤²à¤¿à¤ à¤¢à¥ˆà¤‚à¤šà¤¾ à¤¬à¥‹à¤•à¤° à¤®à¤¿à¤Ÿà¥à¤Ÿà¥€ à¤®à¥‡à¤‚ à¤®à¤¿à¤²à¤¾à¤¨à¥‡ à¤¸à¥‡ à¤œà¤®à¥€à¤¨ à¤•à¥€ à¤¤à¤¾à¤•à¤¤ à¤¦à¥‹à¤—à¥à¤¨à¥€ à¤¹à¥‹à¤¤à¥€ à¤¹à¥ˆà¥¤"
        else:
            return f"Incorporate well-rotted farmyard manure or vermicompost into {soil} to enhance microbial activity and organic carbon levels."

    # 11. CONVERSATIONAL FOLLOW-UP ("à¦•à¦¤à¦Ÿà¦¾?", "à¦•à¦¤à¦Ÿà§à¦•à§?", "à¦•à§‹à¦¨ à¦“à¦·à§à¦§?", "how much?", "dose")
    if any(w in q_lower for w in ["how much", "dose", "à¦•à¦¤à¦Ÿà¦¾", "à¦•à¦¤à¦Ÿà§à¦•à§", "à¦•à§‹à¦¨ à¦“à¦·à§à¦§", "à¦•à¦¿ à¦“à¦·à§à¦§", "à¦•à¦¤ à¦¬à¦¾à¦°", "à¦•à¦¤à¦Ÿà§à¦•à§ à¦¦à§‡à¦¬", "à¦•à¦¤ à¦—à§à¦°à¦¾à¦®", "à¦•à¦¤ à¦®à¦¿à¦²à¦¿", "à¤•à¤¿à¤¤à¤¨à¤¾", "à¤•à¤¿à¤¤à¤¨à¥€ à¤®à¤¾à¤¤à¥à¤°à¤¾", "à¤•à¥Œà¤¨ à¤¸à¥€ à¤¦à¤µà¤¾", "à¤•à¤¬ à¤¡à¤¾à¤²à¥‡"]):
        if lang == "bn":
            return f"à¦¤à¦°à¦² à¦¸à§à¦ªà§à¦°à§‡ à¦•à¦°à¦¾à¦° à¦•à§à¦·à§‡à¦¤à§à¦°à§‡ à¦ªà§à¦°à¦¤à¦¿ à¦²à¦¿à¦Ÿà¦¾à¦° à¦œà¦²à§‡ à¦¦à§à¦‡ à¦¥à§‡à¦•à§‡ à¦¤à¦¿à¦¨ à¦®à¦¿à¦²à¦¿à¦²à¦¿à¦Ÿà¦¾à¦°, à¦à¦¬à¦‚ à¦¦à§à¦°à¦¬à¦£à§€à¦¯à¦¼ à¦ªà¦¾à¦‰à¦¡à¦¾à¦°à§‡à¦° à¦•à§à¦·à§‡à¦¤à§à¦°à§‡ à¦ªà§à¦°à¦¤à¦¿ à¦²à¦¿à¦Ÿà¦¾à¦° à¦œà¦²à§‡ à¦¦à§‡à¦¡à¦¼ à¦¥à§‡à¦•à§‡ à¦¦à§à¦‡ à¦—à§à¦°à¦¾à¦® à¦—à§à¦²à§‡ à¦¸à¦•à¦¾à¦²à§‡ à¦¬à¦¾ à¦¬à¦¿à¦•à§‡à¦²à§‡ à¦¸à¦®à¦¾à¦¨à¦­à¦¾à¦¬à§‡ à¦¸à§à¦ªà§à¦°à§‡ à¦•à¦°à§à¦¨à¥¤"
        elif lang == "hi":
            return f"à¤¤à¤°à¤² à¤•à¥€à¤Ÿà¤¨à¤¾à¤¶à¤• 2 à¤¸à¥‡ 3 à¤®à¤¿à¤²à¥€ à¤ªà¥à¤°à¤¤à¤¿ à¤²à¥€à¤Ÿà¤° à¤ªà¤¾à¤¨à¥€ à¤®à¥‡à¤‚ à¤”à¤° à¤˜à¥à¤²à¤¨à¤¶à¥€à¤² à¤ªà¤¾à¤‰à¤¡à¤° 2 à¤—à¥à¤°à¤¾à¤® à¤ªà¥à¤°à¤¤à¤¿ à¤²à¥€à¤Ÿà¤° à¤ªà¤¾à¤¨à¥€ à¤®à¥‡à¤‚ à¤˜à¥‹à¤²à¤•à¤° à¤¸à¥à¤¬à¤¹ à¤¯à¤¾ à¤¶à¤¾à¤® à¤«à¤¸à¤² à¤ªà¤° à¤¸à¤®à¤¾à¤¨ à¤°à¥‚à¤ª à¤¸à¥‡ à¤›à¤¿à¤¡à¤¼à¤•à¥‡à¤‚à¥¤"
        else:
            return f"Use 2 to 3 ml per liter for liquid concentrates, or 1.5 to 2 grams per liter for wettable powders, applied early in the morning or late evening."

    # 12. DYNAMIC GENERAL AGRONOMY
    if lang == "bn":
        return f"{crop_disp} à¦«à¦¸à¦²à§‡ à¦•à§‹à¦¨à§‹ à¦…à¦¸à§à¦¬à¦¾à¦­à¦¾à¦¬à¦¿à¦• à¦²à¦•à§à¦·à¦£ à¦¬à¦¾ à¦ªà§‹à¦•à¦¾à¦° à¦†à¦•à§à¦°à¦®à¦£ à¦¦à§‡à¦–à¦²à§‡ à¦¸à¦•à¦¾à¦²à§‡ à¦œà¦®à¦¿ à¦ªà¦°à§à¦¯à¦¬à§‡à¦•à§à¦·à¦£ à¦•à¦°à§à¦¨à¥¤ à¦ªà§à¦°à¦¯à¦¼à§‹à¦œà¦¨à§‡ à¦†à¦®à¦¾à¦¦à§‡à¦° à¦•à§à¦°à¦ª à¦¡à¦•à§à¦Ÿà¦° à¦Ÿà§à¦²à§‡ à¦ªà¦¾à¦¤à¦¾à¦° à¦›à¦¬à¦¿ à¦¤à§à¦²à§‡ à¦ªà¦°à§€à¦•à§à¦·à¦¾ à¦•à¦°à§à¦¨ à¦à¦¬à¦‚ à¦¸à§à¦¥à¦¾à¦¨à§€à¦¯à¦¼ à¦•à§ƒà¦·à¦¿ à¦†à¦§à¦¿à¦•à¦¾à¦°à¦¿à¦•à§‡à¦° à¦ªà¦°à¦¾à¦®à¦°à§à¦¶ à¦¨à¦¿à¦¨à¥¤"
    elif lang == "hi":
        return f"{crop_disp} à¤•à¥€ à¤«à¤¸à¤² à¤®à¥‡à¤‚ à¤•à¤¿à¤¸à¥€ à¤­à¥€ à¤…à¤¸à¤¾à¤®à¤¾à¤¨à¥à¤¯ à¤²à¤•à¥à¤·à¤£ à¤•à¥‡ à¤²à¤¿à¤ à¤¸à¥à¤¬à¤¹ à¤•à¥‡ à¤¸à¤®à¤¯ à¤–à¥‡à¤¤ à¤•à¤¾ à¤¨à¤¿à¤°à¥€à¤•à¥à¤·à¤£ à¤•à¤°à¥‡à¤‚à¥¤ à¤¤à¥à¤°à¤‚à¤¤ à¤ªà¤¹à¤šà¤¾à¤¨ à¤•à¥‡ à¤²à¤¿à¤ à¤¹à¤®à¤¾à¤°à¥‡ à¤•à¥à¤°à¥‰à¤ª à¤¡à¥‰à¤•à¥à¤Ÿà¤° à¤Ÿà¥‚à¤² à¤¸à¥‡ à¤«à¥‹à¤Ÿà¥‹ à¤œà¤¾à¤‚à¤šà¥‡à¤‚à¥¤"
    else:
        return f"For healthy {crop_disp} growth, scout your field in the early morning and maintain balanced soil moisture. Use our Crop Doctor tool if you observe any leaf damage."


async def process_voice_query(
    query: str,
    requested_language: Optional[str] = "auto",
    farm_data: Optional[Dict[str, Any]] = None,
    field_context: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    State-of-the-Art Agricultural Voice AI Pipeline:
    1. Real Spoken Language Detection (Script + Phonetic Heuristics).
    2. Context Extraction (Crop, Stage, Soil, Soil Moisture, Weather, NDVI, Doctor Issue).
    3. Dynamic Gemini Generative AI Inference with safe, concise voice instructions.
    4. Resilient Fallback to Expert Dynamic Agronomic Engine.
    5. Clean Phonetic Text Normalization & Regional Google TTS Synthesis.
    """
    farm = farm_data or {}
    crop = farm.get("crop", "Rice")
    location = farm.get("location", "Haldia, West Bengal")
    soil = farm.get("soil", "Alluvial Soil")
    irrigation = farm.get("irrigation", "Canal")
    area = farm.get("area", "2.5")

    # 1. Determine Language
    detected_lang = detect_spoken_language(query, default_lang="en")
    if requested_language and requested_language not in ["auto", ""]:
        language = requested_language
    else:
        language = detected_lang

    lang_names = {
        "bn": "Bengali (à¦¬à¦¾à¦‚à¦²à¦¾)",
        "hi": "Hindi (à¤¹à¤¿à¤¨à¥à¤¦à¥€)",
        "en": "English"
    }
    target_lang_name = lang_names.get(language, "English")
    detected_lang_name = lang_names.get(detected_lang, "English")

    # 2. Extract live environmental & agricultural intelligence
    ctx = field_context or {}
    soil_moisture = ctx.get("soil_moisture") or ctx.get("soil_condition", {}).get("estimated_soil_moisture") or "Adequate"
    weather = ctx.get("weather") or {}
    temp = weather.get("temperature", 29)
    condition = weather.get("condition", "Partly Cloudy")
    rain_chance = weather.get("precipitation_chance", 25)
    weather_summary = f"{temp}Â°C, {condition}, Rain Chance: {rain_chance}%"
    ndvi_score = ctx.get("ndvi") or ctx.get("satellite_score") or "0.72"
    growth_stage = ctx.get("growth_stage") or "Vegetative"
    doctor_issue = ctx.get("primary_issue") or ctx.get("latest_diagnosis") or None

    gemini_key = get_gemini_api_key()
    spoken_response = None

    # 3. Call Gemini if API Key is configured
    if gemini_key:
        system_prompt = f"""You are "KrishiBandhu(AI)", an expert agricultural voice AI assistant talking directly to an Indian farmer via speaker.

FARMER'S CURRENT AGRICULTURAL CONTEXT:
- Farm Location: {location}
- Crop: {crop} ({area} acres, Stage: {growth_stage})
- Soil Type: {soil}
- Irrigation Method: {irrigation}
- Current Soil Moisture: {soil_moisture}
- Live Weather: {weather_summary}
- Remote Sensing Health (NDVI): {ndvi_score}
{f"- Recent Crop Doctor Report: {doctor_issue}" if doctor_issue else ""}

STRICT AUTOMATIC MULTILINGUAL CONVERSATION RULES:
1. AUTOMATIC LANGUAGE MATCHING: You must understand the farmer's language automatically ({target_lang_name}).
   - If the farmer asks in Hindi (in Devanagari or Hinglish), you MUST reply completely in authentic, natural Hindi.
   - If the farmer asks in Bengali (in Bengali script or Banglish), you MUST reply completely in natural Bengali.
   - If the farmer asks in English, you MUST reply in clear, simple English.
   Never mix languages or translate into an unintended language.
2. SPOKEN PACING: Keep responses concise (2 to 4 sentences, under 45 words) so it sounds natural when spoken aloud.
3. CONVERSATIONAL & DIRECT: Directly answer the farmer's specific question (e.g., yellow leaves, fertilizer before rain, watering, pest control, crop rotation).
4. NO MARKDOWN: Never use markdown symbols, asterisks, hashes, lists, bullet points, numbers, or formulas.
5. AGRICULTURAL SAFETY: Do not invent hazardous chemical dosages. Recommend safe practices."""

        spoken_response = await query_gemini_for_voice(
            api_key=gemini_key,
            system_prompt=system_prompt,
            user_query=query,
            conversation_history=conversation_history
        )

    # 4. Fallback to Dynamic Agronomic Engine if Gemini is offline or rate-limited
    if not spoken_response or not spoken_response.strip():
        spoken_response = build_dynamic_agronomic_voice_response(
            query=query,
            lang=language,
            crop=crop,
            soil=soil,
            location=location,
            soil_moisture=str(soil_moisture),
            weather_summary=weather_summary,
            rain_chance=int(rain_chance) if str(rain_chance).isdigit() else 25,
            recent_diagnosis=doctor_issue,
            history=conversation_history
        )

    # Clean text specifically for human voice synthesis
    clean_speech_text = clean_text_for_speech(spoken_response, lang=language)

    # Synthesize authentic regional voice via Google TTS
    audio_base64 = synthesize_speech_base64(clean_speech_text, lang=language)

    return {
        "query": query,
        "language": language,
        "detected_language": detected_lang,
        "language_name": target_lang_name,
        "detected_language_name": detected_lang_name,
        "response_text": spoken_response,
        "clean_speech_text": clean_speech_text,
        "audio_base64": audio_base64,
        "has_audio": bool(audio_base64),
        "context_applied": {
            "crop": crop,
            "location": location,
            "soil": soil,
            "irrigation": irrigation,
            "soil_moisture": str(soil_moisture),
            "weather": weather_summary,
            "recent_diagnosis": doctor_issue
        }
    }

