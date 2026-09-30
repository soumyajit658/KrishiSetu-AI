import io
import re
import base64
from typing import Dict, Any, Optional, List, Tuple
from gtts import gTTS
import httpx
from config import get_gemini_api_key

CROP_NAMES_LOCAL = {
    "Rice": {"bn": "ধান", "hi": "धान", "en": "Rice"},
    "Wheat": {"bn": "গম", "hi": "गेहूं", "en": "Wheat"},
    "Potato": {"bn": "আলু", "hi": "आलू", "en": "Potato"},
    "Tomato": {"bn": "টমেটো", "hi": "टमाटर", "en": "Tomato"},
    "Maize": {"bn": "ভুট্টা", "hi": "मक्का", "en": "Maize"},
    "Mustard": {"bn": "সরিষা", "hi": "सरसों", "en": "Mustard"},
    "Chilli": {"bn": "লঙ্কা", "hi": "मिर्च", "en": "Chilli"},
    "Cotton": {"bn": "তুলা", "hi": "कपास", "en": "Cotton"},
    "Vegetables": {"bn": "শাকসবজি", "hi": "सब्जियों", "en": "Vegetables"},
}

def get_local_crop(crop_name: str, lang: str) -> str:
    crop_info = CROP_NAMES_LOCAL.get(crop_name)
    if crop_info and lang in crop_info:
        return crop_info[lang]
    return crop_name or ("ধান" if lang == "bn" else ("फसल" if lang == "hi" else "Crop"))


# Comprehensive Linguistic & Phonetic Language Detector
BENGALI_PHRASES = [
    "ki korbo", "ki vabe", "kivabe", "dhaner pata", "pani kobe", "agami kal", "agamikal", 
    "jol debo", "jol deya", "sar debo", "poka legeche", "daag hoyeche", "ki sar debo", 
    "dhaner rog", "alu chash", "sorisa chash", "fosol nosto"
]

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

HINDI_PHRASES = [
    "kya karu", "kya kare", "kya karein", "kya karna", "kaise kare", "kese kare", 
    "kab dena", "kab de", "pani dena", "pani kab", "kab pani", "pani kab dale", 
    "khad kab", "kya dale", "kaun si dawa", "konsi dawa", "kaun sa spray", "kya chhidkaw kare",
    "peela pad raha", "peeli ho rahi", "peele ho rahe", "peela pan", "fasal me", "fasal mein", 
    "khet me", "khet mein", "kisan bhai", "kya hoga", "kaise bachaye", "dawa batao", 
    "dawai bataiye", "kitna dale", "kitni matra", "keeda lag gaya", "sundi ka attack",
    "agli fasal", "baad me kya", "barish aane wali", "barish hone par", "sinchai kab kare",
    "patto par", "patte par", "sukha pad", "paani kab lagaye", "dawa kaun si", "upchar bataiye"
]

HINDI_KEYWORDS = {
    # Pronouns & Interrogatives
    "meri", "mera", "mere", "apna", "apni", "apne", "humara", "humari", "humare", "mujhe", 
    "hume", "isse", "isme", "ispe", "usme", "uspe", "kya", "kyun", "kyu", "kaise", "kese", 
    "kab", "kaha", "kahan", "kitna", "kitni", "kitne", "kaun", "koun", "kaunsa", "kaunsi", "kaunse",
    # Verbs & Auxiliaries
    "hai", "hain", "ho", "hoon", "tha", "the", "thi", "hoga", "hogi", "honge", "kare", 
    "karen", "karein", "karna", "karu", "karun", "karega", "karegi", "karenge", "karta", 
    "karti", "karte", "dena", "dale", "dalen", "dalna", "lagaye", "lagana", "chahiye", 
    "chaiye", "chahie", "cheiya", "batao", "bataiye", "boliye", "bolo", "samjhao", "dekho",
    # Prepositions & Connectors
    "ka", "ki", "ke", "ko", "se", "me", "mein", "main", "par", "pe", "aur", "ya", 
    "nahi", "nahin", "mat", "bhi", "toh", "to", "tak", "liye", "wala", "wali", "wale",
    # Agronomic Terms
    "fasal", "faslo", "khet", "kheti", "kheto", "kisan", "kisano", "mitti", "zameen", 
    "gehu", "gehun", "dhan", "chawal", "makka", "sarso", "sarson", "aloo", "alu", "tamatar", 
    "mirch", "kapas", "ganna", "pyaaz", "lahsun", "pani", "paani", "sinchai", "sinchayi", 
    "khad", "dawa", "dawai", "chhidkaw", "chhidkao", "peela", "peeli", "peele", "peelapan", 
    "kala", "kali", "kale", "safed", "sukha", "sukh", "patte", "patti", "pattiya", "pattiyan", 
    "paudha", "paudhe", "podha", "podhe", "tana", "jad", "fal", "keeda", "keede", "keedo", 
    "kit", "kito", "sundi", "illii", "illi", "mahu", "barish", "barsat", "badal", "mausam", 
    "hawa", "dhoop", "garmi", "sardi", "beej", "buwai", "ropai", "katai", "kharpatwar", 
    "gobar", "urvarak", "nami", "upchar", "ilaaj", "fayda", "nuksan", "rog", "dhabba", "dhabbe"
}

ENGLISH_PHRASES = [
    "should i", "what should", "how to", "how can i", "is it", "when should", 
    "can i", "do i need", "there is", "there are", "my crop is", "why are", 
    "please tell me", "how much should", "what is the", "good morning", "tell me about"
]

ENGLISH_KEYWORDS = {
    "what", "when", "how", "why", "which", "where", "who", "should", "could", "would",
    "will", "shall", "does", "doesnt", "dont", "please", "help", "problem", "solution",
    "because", "tomorrow", "yesterday", "morning", "evening", "today", "tonight",
    "leaves", "turning", "yellowing", "infection", "symptoms", "advice", "suggestion",
    "recommend", "recommendation", "farmers", "farming", "agriculture", "harvesting"
}


def detect_spoken_language(text: str, default_lang: str = "en") -> str:
    """
    Bulletproof Multilingual Language Detector for Regional Indian Speech:
    1. Direct Unicode Script analysis:
       - Devanagari (\u0900-\u097F) -> 100% Hindi ('hi').
       - Bengali (\u0980-\u09FF) -> 100% Bengali ('bn').
    2. Deep Lexical & Phrase Frequency for Romanized Hinglish vs Banglish vs English.
    """
    if not text or not text.strip():
        return default_lang if default_lang in ["bn", "hi", "en"] else "en"
    
    clean_t = text.strip()
    
    # 1. Direct Unicode Script Matching (Highest Precision)
    if re.search(r'[\u0900-\u097F]', clean_t):
        return "hi"
        
    if re.search(r'[\u0980-\u09FF]', clean_t):
        return "bn"
    
    # 2. Phonetic & Lexical token analysis for Romanized text
    tokens = re.findall(r'[a-zA-Z]+', clean_t.lower())
    if not tokens:
        return default_lang if default_lang in ["bn", "hi", "en"] else "en"
        
    t_lower = clean_t.lower()
    
    bn_score = 0.0
    hi_score = 0.0
    en_score = 0.0
    
    # Check multi-word phrase patterns
    for phrase in HINDI_PHRASES:
        if phrase in t_lower:
            hi_score += 4.5

    for phrase in BENGALI_PHRASES:
        if phrase in t_lower:
            bn_score += 4.5
            
    for phrase in ENGLISH_PHRASES:
        if phrase in t_lower:
            en_score += 4.5

    for tok in tokens:
        if tok in HINDI_KEYWORDS:
            hi_score += 1.8
        if tok in BENGALI_KEYWORDS:
            bn_score += 1.8
        if tok in ENGLISH_KEYWORDS:
            en_score += 1.2

    # Decisive language categorization
    if hi_score >= 1.5 and hi_score >= bn_score and hi_score >= en_score:
        return "hi"
    if bn_score >= 1.5 and bn_score > hi_score and bn_score >= en_score:
        return "bn"
    if en_score >= 2.0 and en_score > hi_score and en_score > bn_score:
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
    cleaned = re.sub(r'[-•*]\s+', ' ', cleaned)
    
    # Remove emoji and symbols that distort audio synthesis
    cleaned = re.sub(r'[⚠️🚨💡🔍🌾🐛💧🌱📋🧪🏛️•~^|/\\()\[\]{}]', ' ', cleaned)
    
    if lang == "bn":
        cleaned = cleaned.replace("NPK", " এন পি কে ")
        cleaned = cleaned.replace("pH", " পি এইচ ")
        cleaned = cleaned.replace("NDVI", " এন ডি ভি আই ")
        cleaned = cleaned.replace("Urea", " ইউরিয়া ")
        cleaned = cleaned.replace("DAP", " ডি এ পি ")
        cleaned = cleaned.replace("MOP", " পটাশ ")
        cleaned = cleaned.replace("Mancozeb", " ম্যানকোজেব ")
        cleaned = cleaned.replace("Saaf", " সাফ ")
        cleaned = cleaned.replace("Cartap", " কার্টাপ ")
        cleaned = cleaned.replace("Chlorantraniliprole", " কোরাজন ")
        cleaned = cleaned.replace("Trichoderma", " ট্রাইকোডার্মা ")
        cleaned = cleaned.replace("m³/m³", " ঘনমিটার ")
        cleaned = cleaned.replace("kg/ha", " কেজি প্রতি হেক্টরে ")
        cleaned = cleaned.replace("g/L", " গ্রাম প্রতি লিটারে ")
        cleaned = cleaned.replace("ml/L", " মিলি প্রতি লিটারে ")
        cleaned = cleaned.replace("°C", " ডিগ্রি সেলসিয়াস ")
        cleaned = cleaned.replace("%", " শতাংশ ")
        cleaned = cleaned.replace("2.5", " আড়াই ")
        cleaned = cleaned.replace("0.5", " অর্ধেক ")
    elif lang == "hi":
        cleaned = cleaned.replace("NPK", " एन पी के ")
        cleaned = cleaned.replace("pH", " पी एच ")
        cleaned = cleaned.replace("NDVI", " एन डी वी आई ")
        cleaned = cleaned.replace("Urea", " यूरिया ")
        cleaned = cleaned.replace("DAP", " डी ए पी ")
        cleaned = cleaned.replace("MOP", " पोटाश ")
        cleaned = cleaned.replace("Mancozeb", " मैनकोजेब ")
        cleaned = cleaned.replace("Saaf", " साफ ")
        cleaned = cleaned.replace("Cartap", " कार्टाप ")
        cleaned = cleaned.replace("Chlorantraniliprole", " कोराजन ")
        cleaned = cleaned.replace("Trichoderma", " ट्राइकोडर्मा ")
        cleaned = cleaned.replace("m³/m³", " घनमीटर ")
        cleaned = cleaned.replace("kg/ha", " किलोग्राम प्रति हेक्टेयर ")
        cleaned = cleaned.replace("g/L", " ग्राम प्रति लीटर ")
        cleaned = cleaned.replace("ml/L", " मिली प्रति लीटर ")
        cleaned = cleaned.replace("°C", " डिग्री सेल्सियस ")
        cleaned = cleaned.replace("%", " प्रतिशत ")
        cleaned = cleaned.replace("2.5", " ढाई ")
        cleaned = cleaned.replace("0.5", " आधा ")
    else:
        cleaned = cleaned.replace("NPK", "N-P-K")
        cleaned = cleaned.replace("pH", "p-H")
        cleaned = cleaned.replace("kg/ha", " kilograms per hectare ")
        cleaned = cleaned.replace("g/L", " grams per liter ")
        cleaned = cleaned.replace("ml/L", " milliliters per liter ")
        cleaned = cleaned.replace("°C", " degrees celsius ")
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
    models = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-flash-latest", "gemini-2.5-flash-lite"]
    
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
    is_rain_inquiry = any(w in q_lower for w in ["rain", "raining", "বৃষ্টি", "বারিশ", "बारिश", "बरसात", "weather", "আবহাওয়া", "मौसम", "বাদল", "আঁধি", "মেঘ", "barish", "barsat", "brishti", "abohawa", "mausam"])
    is_fertilizer_or_spray = any(w in q_lower for w in ["fertilizer", "urea", "spray", "khad", "সার", "স্প্রে", "ইউরিয়া", "ডিএপি", "পটাশ", "खाद", "दवा", "छिड़काव", "यूरिया", "डीएपी", "पोटाश", "dap", "potash", "chhidkaw", "sar", "dawa"])
    
    if is_rain_inquiry and is_fertilizer_or_spray:
        if lang == "bn":
            return f"আগামীকাল বৃষ্টির সম্ভাবনা থাকলে জমিতে কোনো ইউরিয়া সার বা কীটনাশক স্প্রে করবেন না। বৃষ্টির জলে সার ধুয়ে অপচয় হবে। আকাশ পরিষ্কার হলে এবং জল নামলে তবেই সার প্রয়োগ করুন।"
        elif lang == "hi":
            return f"यदि कल बारिश की संभावना है तो खेत में यूरिया या कीटनाशक स्प्रे बिल्कुल न करें। बारिश के पानी से खाद बहकर बर्बाद हो जाएगी। मौसम साफ होने के बाद ही छिड़काव करें।"
        else:
            return f"Do not apply Urea or chemical sprays if rain is expected tomorrow. Rainwater will wash away nutrients and cause nitrogen runoff. Wait until clear weather returns."

    if is_rain_inquiry:
        if lang == "bn":
            return f"আপনার {location} অঞ্চলে বর্তমানে {weather_summary}। বৃষ্টির সম্ভাবনা প্রায় {rain_chance} শতাংশ। বৃষ্টির আগে জমিতে নিকাশি নালা পরিষ্কার রাখুন যাতে জল জমতে না পারে।"
        elif lang == "hi":
            return f"आपके {location} क्षेत्र में अभी {weather_summary} है। बारिश की संभावना {rain_chance} प्रतिशत है। खेत में जल निकासी की व्यवस्था दुरुस्त रखें ताकि जलभराव न हो।"
        else:
            return f"Current weather in {location} is {weather_summary} with a {rain_chance}% chance of rain. Ensure field drainage channels are open to prevent water stagnation."

    # 2. IRRIGATION & WATER MANAGEMENT ("पानी कब दें", "পানি", "सिंचाई", "জল দেব", "water", "irrigate")
    if any(w in q_lower for w in ["water", "irrigate", "irrigation", "पानी", "सिंचाई", "সেচ", "জল", "পানি কখন", "pani", "paani", "sinchai", "sinchayi", "sech", "jol debo", "pani kab", "pani dena", "kab pani", "pani kab kab", "jal"]):
        is_wet = soil_moisture and ("wet" in soil_moisture.lower() or "humid" in soil_moisture.lower() or "adequate" in soil_moisture.lower())
        if is_wet or rain_chance > 50:
            if lang == "bn":
                return f"আপনার {location} অঞ্চলের মাটিতে বর্তমানে পর্যাপ্ত আর্দ্রতা রয়েছে এবং বৃষ্টির সম্ভাবনা {rain_chance}%। আজ নতুন করে সেচ দেওয়ার প্রয়োজন নেই, অতিরিক্ত জলে শিকড় পচে যেতে পারে।"
            elif lang == "hi":
                return f"आपके खेत की मिट्टी में अभी पर्याप्त नमी है और बारिश की संभावना {rain_chance}% है। अभी {crop_disp} में अतिरिक्त पानी न दें, ताकि जड़ गलन न हो। शाम को खेत देखकर ही हल्की सिंचाई करें।"
            else:
                return f"Your soil in {location} currently has adequate moisture with {rain_chance}% rain forecast. Do not irrigate today to avoid waterlogging."
        else:
            if lang == "bn":
                return f"মাটির উপরিভাগ পরীক্ষা করে দেখুন। যদি {crop_disp} গাছের গোড়ায় মাটি শুষ্ক থাকে, তবে বিকেলে হালকা সেচ দিন। খেয়াল রাখবেন যেন জমিতে জল দীর্ঘক্ষণ জমে না থাকে।"
            elif lang == "hi":
                return f"{crop_disp} में जब ऊपरी 2 इंच मिट्टी सूखी लगे तभी पानी दें। फूल आने और दाना भरते समय पानी की कमी न होने दें। आज शाम खेत में हल्की सिंचाई कर सकते हैं।"
            else:
                return f"Check your field surface. If topsoil is dry around your {crop_disp}, apply a light irrigation this evening without flooding."

    # 3. CROP ROTATION & POST-HARVEST ("What crop to grow after rice / wheat?")
    if any(w in q_lower for w in ["after", "rotate", "rotation", "পর", "পরে", "পরবর্তী", "বাদ", "बाद", "अगली फसल", "next crop", "পরের ফসল", "baad", "agli fasal", "porer fosol"]):
        if "rice" in crop.lower() or "ধান" in q_lower or "dhan" in q_lower:
            if lang == "bn":
                return f"ধান কাটার পর জমিতে সরিষা, আলু, ডাল জাতীয় ফসল যেমন মসুর বা খেসারি, অথবা গম চাষ করা সবচেয়ে লাভজনক। ডাল চাষ করলে মাটিতে প্রাকৃতিকভাবে নাইট্রোজেন যুক্ত হয় এবং জমির উর্বরতা বাড়ে।"
            elif lang == "hi":
                return f"धान की कटाई के बाद आप गेहूं, सरसों, चना, मटर या आलू लगा सकते हैं। दलहनी फसलें उगाने से मिट्टी में प्राकृतिक नाइट्रोजन बढ़ती है और जमीन उपजाऊ बनती है।"
            else:
                return f"After harvesting Rice, planting Mustard, Potato, Chickpea, Lentil, or Wheat is ideal. Growing legumes naturally replenishes soil nitrogen and breaks pest cycles."
        elif "wheat" in crop.lower() or "গম" in q_lower or "gehu" in q_lower:
            if lang == "bn":
                return f"গম তোলার পর জমিতে সবুজ সার হিসেবে ধইঞ্চা বা মুগ ডাল চাষ করুন। এতে পরবর্তী আমন ধানের ফলন অনেক ভালো হয়।"
            elif lang == "hi":
                return f"गेहूं की कटाई के बाद हरी खाद के लिए ढैंचा या मूंग लगाएं। इससे अगली फसल के लिए जमीन में भरपूर जीवांश कार्बन बढ़ता है।"
            else:
                return f"After Wheat, sow green manure like Sesbania (Dhaincha) or summer Mung bean to boost soil organic carbon before the next Kharif season."
        else:
            if lang == "bn":
                return f"{crop_disp} তোলার পর জমিতে ডালশস্য বা তৈলবীজ চাষ করা সবচেয়ে উপযোগী। এতে মাটির উর্বরতা বজায় থাকে।"
            elif lang == "hi":
                return f"{crop_disp} के बाद दलहनी या तिलहनी फसलें लगाना सबसे उपयुक्त रहता है, जिससे मिट्टी की उर्वरता बनी रहे।"
            else:
                return f"Following {crop_disp} with a leguminous pulse or oilseed crop improves soil structure and nutrient balance."

    # 4. LEAF SPOTS & FUNGAL BLIGHT ("Brown spots", "Black spots", "দাগ", "धब्बे", "blight")
    if any(w in q_lower for w in ["spot", "spots", "brown", "black", "দাগ", "ধাব্বা", "ধব্বে", "धब्बे", "धब्बा", "ब्लाइट", "blight", "rust", "মরিচা", "দাগযুক্ত", "ঝলসানো", "dhabba", "dhabbe", "daag"]):
        if lang == "bn":
            return f"{crop_disp} গাছের পাতায় বাদামী বা কালো দাগ সাধারণত ছত্রাকজনিত ব্লাইট বা ব্রাউন স্পট রোগ। আক্রান্ত পাতা সরিয়ে ফেলুন এবং ম্যানকোজেব বা সাফ প্রতি লিটার জলে দুই গ্রাম গুলে স্প্রে করুন। জমিতে অতিরিক্ত ইউরিয়া দেওয়া বন্ধ রাখুন।"
        elif lang == "hi":
            return f"{crop_disp} की पत्तियों पर भूरे या काले धब्बे कवक जनित ब्लाइट या टिक्का रोग के लक्षण हो सकते हैं। बचाव के लिए साफ या मैंकोजेब 2 ग्राम प्रति लीटर पानी में मिलाकर छिड़कें और अतिरिक्त यूरिया न डालें।"
        else:
            return f"Dark or brown spots on {crop_disp} leaves typically indicate fungal leaf spot or blight. Prune severely infected foliage and spray Mancozeb or Saaf at 2 grams per liter, avoiding excess nitrogen."

    # 5. YELLOW LEAVES & CHLOROSIS ("পাতা হলুদ", "पत्तियां पीली", "yellow leaves")
    if any(w in q_lower for w in ["yellow", "peela", "peeli", "peele", "holud", "পিলা", "হলুদ", "पीला", "पीली", "पीले", "पीलापन", "chlorosis", "ফ্যাকাশে"]):
        if lang == "bn":
            return f"{crop_disp} গাছের পাতা হলুদ হওয়ার প্রধান কারণ নাইট্রোজেন বা জিংকের ঘাটতি, অথবা অতিরিক্ত জল জমে শিকড় শ্বাসরুদ্ধ হওয়া। জমিতে জল জমলে নিকাশ করুন এবং প্রতি লিটার জলে পনেরো গ্রাম ইউরিয়া ও দুই গ্রাম চিলেটেড জিংক মিশিয়ে স্প্রে করুন।"
        elif lang == "hi":
            return f"{crop_disp} में पत्तियां पीली पड़ना मुख्य रूप से नाइट्रोजन या जिंक की कमी अथवा जलभराव का संकेत है। खेत से अतिरिक्त पानी निकालें और 15 ग्राम यूरिया तथा 2 ग्राम चिलेटेड जिंक प्रति लीटर पानी में मिलाकर स्प्रे करें।"
        else:
            return f"Leaf yellowing in {crop_disp} typically stems from Nitrogen or Zinc deficiency, or root waterlogging. Ensure soil drains well and apply a foliar spray of 1.5% Urea with 2g/L Chelated Zinc."

    # 6. FERTILIZER & NPK NUTRITION ("সার", "ইউরিয়া", "खाद", "यूरिया", "fertilizer", "dap", "potash")
    if any(w in q_lower for w in ["fertilizer", "urea", "dap", "potash", "khad", "npk", "खाद", "সার", "यूरिया", "पोटाश", "সার প্রয়োগ", "khad kab", "yuriya"]):
        if lang == "bn":
            return f"{crop_disp} ফসলের জন্য জমিতে পর্যাপ্ত আর্দ্রতা থাকা অবস্থায় ইউরিয়া, ডিএপি ও পটাশ সুষম অনুপাতে দিন। ইউরিয়া একবারে না দিয়ে দুই থেকে তিন কিস্তিতে দিলে গাছ সবচেয়ে বেশি পুষ্টি গ্রহণ করতে পারে।"
        elif lang == "hi":
            return f"{crop_disp} में खाद हमेशा मिट्टी में पर्याप्त नमी होने पर ही दें। यूरिया को एक साथ न डालकर दो से तीन बार में बाँटकर देना अधिक फायदेमंद है। सूखी जमीन में यूरिया कभी न डालें।"
        else:
            return f"Apply balanced NPK fertilizers for {crop_disp} only when soil has adequate moisture. Splitting Urea into 2 to 3 split doses boosts nitrogen use efficiency significantly."

    # 7. PESTS, INSECTS & BORERS ("পোকা", "কীট", "कीट", "मरोड़", "pest", "borer", "worm")
    if any(w in q_lower for w in ["pest", "insect", "worm", "borer", "aphid", "কীট", "কীড়া", "পোকা", "মাজরা", "কীটপতঙ্গ", "कीट", "कीड़ा", "माहू", "सुंडी", "keeda", "keede", "poka"]):
        if lang == "bn":
            return f"{crop_disp} ফসলে পোকার আক্রমণ রুখতে প্রথমে নিম তেল প্রতি লিটার জলে তিন মিলি মিশিয়ে সকালে স্প্রে করুন। মাজরা পোকার প্রকোপ থাকলে জমিতে ফেরোমোন ফাঁদ লাগান এবং প্রয়োজনে কার্টাপ বা কোরাজন ব্যবহার করুন।"
        elif lang == "hi":
            return f"{crop_disp} में कीटों से बचाव के लिए नीम तेल 3 मिली प्रति लीटर पानी में मिलाकर छिड़कें। तना छेदक या सुंडी का प्रकोप अधिक होने पर फेरोमोन ट्रैप लगाएं और कोराजन का छिड़काव करें।"
        else:
            return f"For pest defense on {crop_disp}, start with cold-pressed Neem Oil at 3 ml per liter. For stem borers or caterpillars, install pheromone traps and apply Chlorantraniliprole under guidance."

    # 8. SOWING & SEED TREATMENT ("বীজ", "বপন", "বুওয়াই", "बीज", "बुवाई", "seed", "sow")
    if any(w in q_lower for w in ["sow", "sowing", "seed", "বপন", "বীজ", "বোনার", "বুওয়াই", "बुवाई", "बीज", "বিহন"]):
        if lang == "bn":
            return f"{crop_disp} বোনার আগে ট্রাইকোডার্মা প্রতি কেজি বীজে পাঁচ গ্রাম অথবা কার্বেনডাজিম দিয়ে বীজ শোধন করা বাধ্যতামূলক। এতে চারা ধসা ও শিকড় পচা রোগ থেকে শতভাগ রক্ষা পাওয়া যায়।"
        elif lang == "hi":
            return f"{crop_disp} की बुवाई से पहले बीजोपचार अवश्य करें। ट्राइकोडर्मा 5 ग्राम प्रति किलो या कार्बेंडाजिम से बीज शोधन करने से जमाव अच्छा होता है और फफूंद से सुरक्षा मिलती है।"
        else:
            return f"Always treat seeds of {crop_disp} with Trichoderma (5g/kg) or Carbendazim before sowing to prevent seed-borne damping off and seedling blight."

    # 9. WEED CONTROL & MULCHING ("আগাছা", "ঘাস", "खरपतवार", "weed", "weeds")
    if any(w in q_lower for w in ["weed", "weeds", "আগাছা", "ঘাস", "খরपतवार", "खरपतवार"]):
        if lang == "bn":
            return f"চারা লাগানোর বিশ থেকে পঁচিশ দিনের মধ্যে প্রথম নিড়ানি দেওয়া অত্যন্ত জরুরি। গাছের গোড়ায় শুকনো খড়ের মালচিং দিলে আগাছার উপদ্রব অনেকটাই কমে এবং মাটির রস সংরক্ষিত থাকে।"
        elif lang == "hi":
            return f"बुवाई के 20 से 25 दिन बाद पहली निराई-गुड़ाई अवश्य करें। खरपतवार फसलों की खुराक और पानी खींच लेते हैं। जैविक नियंत्रण के लिए पुआल की मल्चिंग अपनाएं।"
        else:
            return f"Keep the critical 20 to 30 day window weed-free through manual hoeing or straw mulching to prevent moisture and nutrient competition."

    # 10. SOIL HEALTH, PH & ORGANIC CARBON ("মাটি", "মাটির স্বাস্থ্য", "pH", "मिट्टी", "soil")
    if any(w in q_lower for w in ["soil", "ph", "carbon", "মাটি", "অম্ল", "উর্বরতা", "मिट्टी", "उर्वरता", "কার্বন"]):
        if lang == "bn":
            return f"{soil}-র উর্বরতা ও জৈব কার্বন বাড়াতে প্রতি একরে ৫-৮ টন গোবর সার বা কেঁচো সার ব্যবহার করুন। প্রতি দুই-তিন বছর অন্তর ধইঞ্চা চাষ করে মাটিতে মিশিয়ে দিলে মাটির স্বাস্থ্য দারুণ থাকে।"
        elif lang == "hi":
            return f"{soil} में जैविक कार्बन बढ़ाने के लिए गोबर की खाद या वर्मीकम्पोस्ट का प्रयोग करें। हरी खाद के लिए ढैंचा बोकर मिट्टी में मिलाने से जमीन की ताकत दोगुनी होती है।"
        else:
            return f"Incorporate well-rotted farmyard manure or vermicompost into {soil} to enhance microbial activity and organic carbon levels."

    # 11. CONVERSATIONAL FOLLOW-UP ("কতটা?", "কতটুকু?", "কোন ওষুধ?", "how much?", "dose")
    if any(w in q_lower for w in ["how much", "dose", "কতটা", "কতটুকু", "কোন ওষুধ", "কি ওষুধ", "কত বার", "কতটুকু দেব", "কত গ্রাম", "কত মিলি", "कितना", "कितनी मात्रा", "कौन सी दवा", "कब डाले"]):
        if lang == "bn":
            return f"তরল স্প্রে করার ক্ষেত্রে প্রতি লিটার জলে দুই থেকে তিন মিলিলিটার, এবং দ্রবণীয় পাউডারের ক্ষেত্রে প্রতি লিটার জলে দেড় থেকে দুই গ্রাম গুলে সকালে বা বিকেলে সমানভাবে স্প্রে করুন।"
        elif lang == "hi":
            return f"तरल कीटनाशक 2 से 3 मिली प्रति लीटर पानी में और घुलनशील पाउडर 2 ग्राम प्रति लीटर पानी में घोलकर सुबह या शाम फसल पर समान रूप से छिड़कें।"
        else:
            return f"Use 2 to 3 ml per liter for liquid concentrates, or 1.5 to 2 grams per liter for wettable powders, applied early in the morning or late evening."

    # 12. DYNAMIC GENERAL AGRONOMY
    if lang == "bn":
        return f"{crop_disp} ফসলে কোনো অস্বাভাবিক লক্ষণ বা পোকার আক্রমণ দেখলে সকালে জমি পর্যবেক্ষণ করুন। প্রয়োজনে আমাদের ক্রপ ডক্টর টুলে পাতার ছবি তুলে পরীক্ষা করুন এবং স্থানীয় কৃষি আধিকারিকের পরামর্শ নিন।"
    elif lang == "hi":
        return f"{crop_disp} की फसल में किसी भी असामान्य लक्षण के लिए सुबह के समय खेत का निरीक्षण करें। तुरंत पहचान के लिए हमारे क्रॉप डॉक्टर टूल से फोटो जांचें।"
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
        "bn": "Bengali (বাংলা)",
        "hi": "Hindi (हिन्दी)",
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
    weather_summary = f"{temp}°C, {condition}, Rain Chance: {rain_chance}%"
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
1. TARGET SPOKEN LANGUAGE: {target_lang_name} (Code: '{language}').
   - IF QUERY IS IN HINDI OR TARGET IS HINDI ('hi'): You MUST reply 100% in natural, respectful, conversational Hindi in pure Devanagari script (हिन्दी). Even if the farmer wrote or spoke in Romanized Hinglish (e.g. 'kya kare', 'fasal me khad', 'peela pad raha'), your spoken answer MUST be in authentic Devanagari Hindi. Start with "नमस्ते किसान भाई," when appropriate.
   - IF QUERY IS IN BENGALI OR TARGET IS BENGALI ('bn'): You MUST reply 100% in natural Bengali in Bengali script (বাংলা). Start with "নমস্কার কৃষক বন্ধু," when appropriate.
   - IF QUERY IS IN ENGLISH ('en'): You MUST reply in clear, simple spoken English.
   NEVER reply in English if the farmer asked in Hindi, Hinglish, Bengali, or Banglish!
2. SPOKEN PACING: Keep responses concise (2 to 4 sentences, under 45 words) so it sounds natural when spoken aloud.
3. CONVERSATIONAL & DIRECT: Directly answer the farmer's specific question (e.g., yellow leaves, fertilizer before rain, watering, pest control, crop rotation).
4. NO MARKDOWN: Never use markdown symbols, asterisks, hashes, lists, bullet points, numbers, or formulas. Output clean plain spoken text only.
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
    else:
        # Re-sync language accurately from generated text script
        if re.search(r'[\u0900-\u097F]', spoken_response):
            language = "hi"
            target_lang_name = "Hindi (हिन्दी)"
        elif re.search(r'[\u0980-\u09FF]', spoken_response):
            language = "bn"
            target_lang_name = "Bengali (বাংলা)"

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
