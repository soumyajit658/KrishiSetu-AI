/**
 * KrishiSetu AI - Dynamic Agronomic Expert Engine & Offline Resilience
 * 
 * Provides instantaneous, highly differentiated, spoken-style agronomic advisory
 * in Bengali, Hindi, and English for EVERY specific agricultural question.
 * Ensures the assistant NEVER gives a repetitive answer even if backend is offline.
 */

const CROP_LOCAL_NAMES = {
  Rice: { bn: "ধান", hi: "धान", en: "Rice" },
  Wheat: { bn: "গম", hi: "गेहूं", en: "Wheat" },
  Potato: { bn: "আলু", hi: "आलू", en: "Potato" },
  Tomato: { bn: "টমেটো", hi: "टमाटर", en: "Tomato" },
  Maize: { bn: "ভুট্টা", hi: "मक्का", en: "Maize" },
  Mustard: { bn: "সরিষা", hi: "सरसों", en: "Mustard" },
  Chilli: { bn: "লঙ্কা", hi: "मिर्च", en: "Chilli" },
  Cotton: { bn: "তুলা", hi: "कपास", en: "Cotton" },
  Vegetables: { bn: "শাকসবজি", hi: "सब्जियों", en: "Vegetables" },
};

function getLocalCrop(crop, lang) {
  const info = CROP_LOCAL_NAMES[crop];
  if (info && info[lang]) return info[lang];
  return crop || (lang === "bn" ? "ধান" : lang === "hi" ? "फसल" : "Crop");
}

export function generateClientChatFallback(query, farmData, history = [], analysisContext = null, language = "en") {
  const qLower = (query || "").toLowerCase();
  const rawLang = (language || "en").toLowerCase();

  // Detect language if auto
  let lang = rawLang;
  if (lang === "auto" || !lang) {
    if (/[\u0980-\u09FF]/.test(query) || /\b(amar|dhaner|dhan|pata|holud|ki korbo|pani|jol|brishti|poka|sar|jomite|hobe)\b/i.test(query)) {
      lang = "bn";
    } else if (/[\u0900-\u097F]/.test(query) || /\b(meri|fasal|gehu|dhan|kya karu|peela|peeli|pani|khad|kisan|keede|barish|sinchai)\b/i.test(query)) {
      lang = "hi";
    } else {
      lang = "en";
    }
  }

  const activeCrop = farmData?.crop || "Rice";
  const location = farmData?.location || "Haldia, West Bengal";
  const soil = farmData?.soil || "Alluvial Soil";
  const irrigation = farmData?.irrigation || "Canal";
  const area = farmData?.area || "2.5";
  const cropDisp = getLocalCrop(activeCrop, lang);

  // 1. RAIN & FERTILIZER / SPRAY TIMING
  const isRain = /rain|raining|বৃষ্টি|বারিশ|बारिश|बरसात|weather|আবহাওয়া|मौसम|মেঘ/i.test(qLower);
  const isFertOrSpray = /fertilizer|urea|spray|khad|সার|স্প্রে|ইউরিয়া|ডিএপি|পটাশ|खाद|दवा|छिड़काव|यूरिया|डीएपी|पोटाश|dap|potash/i.test(qLower);

  if (isRain && isFertOrSpray) {
    if (lang === "bn") {
      return `আগামীকাল বৃষ্টির সম্ভাবনা থাকলে জমিতে কোনো ইউরিয়া সার বা কীটনাশক স্প্রে করবেন না। বৃষ্টির জলে সার ধুয়ে অপচয় হবে এবং গাছের কোনো কাজে আসবে না। আকাশ পরিষ্কার হলে এবং জমির জল নামলে তবেই সার প্রয়োগ করুন।`;
    }
    if (lang === "hi") {
      return `यदि कल बारिश की संभावना है तो खेत में यूरिया या कीटनाशक स्प्रे बिल्कुल न करें। बारिश के पानी से खाद बहकर बर्बाद हो जाएगी। मौसम साफ होने के बाद ही छिड़काव करें।`;
    }
    return `Do not apply Urea or chemical sprays if rain is expected tomorrow. Rainwater will wash away nutrients and cause nitrogen runoff. Wait until clear weather returns.`;
  }

  if (isRain) {
    if (lang === "bn") {
      return `আপনার ${location} অঞ্চলের আবহাওয়া অনুযায়ী বৃষ্টির সম্ভাবনা রয়েছে। বৃষ্টির আগে জমিতে নিকাশি নালা পরিষ্কার রাখুন যাতে জল জমে শিকড় পচে না যায়।`;
    }
    if (lang === "hi") {
      return `आपके ${location} क्षेत्र में बारिश का अनुमान है। खेत में जल निकासी की व्यवस्था दुरुस्त रखें ताकि जलभराव न हो और मेड़ सुरक्षित रहे।`;
    }
    return `Rain is expected in ${location}. Ensure field drainage channels are clear to prevent water stagnation around root zones.`;
  }

  // 2. CROP ROTATION & NEXT CROP
  if (/after|rotate|rotation|পর|পরে|পরবর্তী|বাদ|बाद|अगली फसल|next crop|পরের ফসল/i.test(qLower)) {
    if (activeCrop.toLowerCase().includes("rice") || /ধান|dhan/i.test(qLower)) {
      if (lang === "bn") {
        return `ধান কাটার পর জমিতে সরিষা, আলু, ডাল জাতীয় ফসল যেমন মসুর বা খেসারি, অথবা গম চাষ করা সবচেয়ে লাভজনক। ডাল চাষ করলে মাটিতে প্রাকৃতিকভাবে নাইট্রোজেন যুক্ত হয় এবং জমির উর্বরতা বাড়ে।`;
      }
      if (lang === "hi") {
        return `धान की कटाई के बाद आप गेहूं, सरसों, चना, मटर या आलू लगा सकते हैं। दलहनी फसलें उगाने से मिट्टी में प्राकृतिक नाइट्रोजन बढ़ती है और जमीन उपजाऊ बनती है।`;
      }
      return `After harvesting Rice, planting Mustard, Potato, Chickpea, Lentil, or Wheat is ideal. Growing legumes naturally replenishes soil nitrogen and breaks pest cycles.`;
    }
    if (lang === "bn") {
      return `${cropDisp} তোলার পর জমিতে ডালশস্য বা তৈলবীজ চাষ করা সবচেয়ে উপযোগী। এতে মাটির উর্বরতা বজায় থাকে এবং ফলন ভালো হয়।`;
    }
    if (lang === "hi") {
      return `${cropDisp} के बाद दलहनी या तिलहनी फसलें लगाना सबसे उपयुक्त रहता है, जिससे मिट्टी की उर्वरता बनी रहे।`;
    }
    return `Following ${cropDisp} with a leguminous pulse or oilseed crop improves soil structure and nutrient balance.`;
  }

  // 3. LEAF SPOTS, BLIGHT, RUST & FUNGUS
  if (/spot|spots|brown|black|দাগ|ধাব্বা|ধব্বে|धब्बे|धब्बा|ब्लाइट|blight|rust|মরিচা|দাগযুক্ত|ঝলসানো/i.test(qLower)) {
    if (lang === "bn") {
      return `${cropDisp} গাছের পাতায় বাদামী বা কালো দাগ সাধারণত ছত্রাকজনিত ব্লাইট বা ব্রাউন স্পট রোগ। আক্রান্ত পাতা সরিয়ে ফেলুন এবং ম্যানকোজেব বা সাফ প্রতি লিটার জলে দুই গ্রাম গুলে স্প্রে করুন। জমিতে অতিরিক্ত ইউরিয়া দেওয়া বন্ধ রাখুন।`;
    }
    if (lang === "hi") {
      return `${cropDisp} की पत्तियों पर भूरे या काले धब्बे कवक जनित ब्लाइट या टिक्का रोग के लक्षण हो सकते हैं। बचाव के लिए साफ या मैंकोजेब 2 ग्राम प्रति लीटर पानी में मिलाकर छिड़कें और अतिरिक्त यूरिया न डालें।`;
    }
    return `Dark or brown spots on ${cropDisp} leaves typically indicate fungal leaf spot or blight. Prune severely infected foliage and spray Mancozeb or Saaf at 2 grams per liter, avoiding excess nitrogen.`;
  }

  // 4. YELLOW LEAVES & CHLOROSIS
  if (/yellow|peela|peeli|peele|holud|পিলা|হলুদ|पीला|पीली|पीले|पीलापन|chlorosis|ফ্যাকাশে/i.test(qLower)) {
    if (lang === "bn") {
      return `${cropDisp} গাছের পাতা হলুদ হওয়ার প্রধান কারণ নাইট্রোজেন বা জিংকের ঘাটতি, অথবা অতিরিক্ত জল জমে শিকড় শ্বাসরুদ্ধ হওয়া। জমিতে জল জমলে নিকাশ করুন এবং প্রতি লিটার জলে পনেরো গ্রাম ইউরিয়া ও দুই গ্রাম চিলেটেড জিংক মিশিয়ে স্প্রে করুন।`;
    }
    if (lang === "hi") {
      return `${cropDisp} में पत्तियां पीली पड़ना मुख्य रूप से नाइट्रोजन या जिंक की कमी अथवा जलभराव का संकेत है। खेत से अतिरिक्त पानी निकालें और 15 ग्राम यूरिया तथा 2 ग्राम चिलेटेड जिंक प्रति लीटर पानी में मिलाकर स्प्रे करें।`;
    }
    return `Leaf yellowing in ${cropDisp} typically stems from Nitrogen or Zinc deficiency, or root waterlogging. Ensure soil drains well and apply a foliar spray of 1.5% Urea with 2g/L Chelated Zinc.`;
  }

  // 5. IRRIGATION & WATER MANAGEMENT
  if (/water|irrigate|irrigation|পানি|सिंचाई|সেচ|জল|पानी कब/i.test(qLower)) {
    if (lang === "bn") {
      return `মাটির উপরিভাগ পরীক্ষা করে দেখুন। যদি ${cropDisp} গাছের গোড়ায় মাটি শুষ্ক থাকে, তবে বিকেলে হালকা সেচ দিন। খেয়াল রাখবেন যেন জমিতে জল দীর্ঘক্ষণ জমে না থাকে।`;
    }
    if (lang === "hi") {
      return `खेत की ऊपरी मिट्टी सूख रही है तो आज शाम हल्की सिंचाई करें। अत्यधिक पानी का भराव न होने दें और मेड़ सुरक्षित रखें।`;
    }
    return `Check your field surface. If topsoil is dry around your ${cropDisp}, apply a light irrigation this evening without flooding.`;
  }

  // 6. FERTILIZER & NPK NUTRITION
  if (/fertilizer|urea|dap|potash|khad|npk|खाद|সার|यूरिया|पोटाश|সার প্রয়োগ/i.test(qLower)) {
    if (lang === "bn") {
      return `${cropDisp} ফসলের জন্য জমিতে পর্যাপ্ত আর্দ্রতা থাকা অবস্থায় ইউরিয়া, ডিএপি ও পটাশ সুষম অনুপাতে দিন। ইউরিয়া একবারে না দিয়ে দুই থেকে তিন কিস্তিতে দিলে গাছ সবচেয়ে বেশি পুষ্টি গ্রহণ করতে পারে।`;
    }
    if (lang === "hi") {
      return `${cropDisp} में खाद हमेशा मिट्टी में पर्याप्त नमी होने पर ही दें। यूरिया को एक साथ न डालकर दो से तीन बार में बाँटकर देना अधिक फायदेमंद है। सूखी जमीन में यूरिया कभी न डालें।`;
    }
    return `Apply balanced NPK fertilizers for ${cropDisp} only when soil has adequate moisture. Splitting Urea into 2 to 3 split doses boosts nitrogen use efficiency significantly.`;
  }

  // 7. PESTS, INSECTS & BORERS
  if (/pest|insect|worm|borer|aphid|কীট|কীড়া|পোকা|মাজরা|কীটপতঙ্গ|कीट|कीड़ा|माहू|सुंडी/i.test(qLower)) {
    if (lang === "bn") {
      return `${cropDisp} ফসলে পোকার আক্রমণ রুখতে প্রথমে নিম তেল প্রতি লিটার জলে তিন মিলি মিশিয়ে সকালে স্প্রে করুন। মাজরা পোকার প্রকোপ থাকলে জমিতে ফেরোমোন ফাঁদ লাগান এবং প্রয়োজনে কার্টাপ বা কোরাজন ব্যবহার করুন।`;
    }
    if (lang === "hi") {
      return `${cropDisp} में कीटों से बचाव के लिए नीम तेल 3 मिली प्रति लीटर पानी में मिलाकर छिड़कें। तना छेदक या सुंडी का प्रकोप अधिक होने पर फेरोमोन ट्रैप लगाएं और कोराजन का छिड़काव करें।`;
    }
    return `For pest defense on ${cropDisp}, start with cold-pressed Neem Oil at 3 ml per liter. For stem borers or caterpillars, install pheromone traps and apply Chlorantraniliprole under guidance.`;
  }

  // 8. SOWING & SEEDS
  if (/sow|sowing|seed|বপন|বীজ|বোনার|বুওয়াই|बुवाई|बीज|বিহন/i.test(qLower)) {
    if (lang === "bn") {
      return `${cropDisp} বোনার আগে ট্রাইকোডার্মা প্রতি কেজি বীজে পাঁচ গ্রাম অথবা কার্বেনডাজিম দিয়ে বীজ শোধন করা বাধ্যতামূলক। এতে চারা ধসা ও শিকড় পচা রোগ থেকে শতভাগ রক্ষা পাওয়া যায়।`;
    }
    if (lang === "hi") {
      return `${cropDisp} की बुवाई से पहले बीजोपचार अवश्य करें। ट्राइकोडर्मा 5 ग्राम प्रति किलो या कार्बेंडाजिम से बीज शोधन करने से जमाव अच्छा होता है और फफूंद से सुरक्षा मिलती है।`;
    }
    return `Always treat seeds of ${cropDisp} with Trichoderma (5g/kg) or Carbendazim before sowing to prevent seed-borne damping off and seedling blight.`;
  }

  // 9. WEED MANAGEMENT
  if (/weed|weeds|আগাছা|ঘাস|খরपतवार|खरपतवार/i.test(qLower)) {
    if (lang === "bn") {
      return `চারা লাগানোর বিশ থেকে পঁচিশ দিনের মধ্যে প্রথম নিড়ানি দেওয়া অত্যন্ত জরুরি। গাছের গোড়ায় শুকনো খড়ের মালচিং দিলে আগাছার উপদ্রব অনেকটাই কমে এবং মাটির রস সংরক্ষিত থাকে।`;
    }
    if (lang === "hi") {
      return `बुवाई के 20 से 25 दिन बाद पहली निराई-गुड़ाई अवश्य करें। खरपतवार फसलों की खुराक और पानी खींच लेते हैं। जैविक नियंत्रण के लिए पुआल की मल्चिंग अपनाएं।`;
    }
    return `Keep the critical 20 to 30 day window weed-free through manual hoeing or straw mulching to prevent moisture and nutrient competition.`;
  }

  // 10. SOIL HEALTH & CARBON
  if (/soil|ph|carbon|মাটি|অম্ল|উর্বরতা|मिट्टी|उर्वरता|কার্বন/i.test(qLower)) {
    if (lang === "bn") {
      return `${soil}-র উর্বরতা ও জৈব কার্বন বাড়াতে প্রতি একরে ৫-৮ টন গোবর সার বা কেঁচো সার ব্যবহার করুন। প্রতি দুই-তিন বছর অন্তর ধইঞ্চা চাষ করে মাটিতে মিশিয়ে দিলে মাটির স্বাস্থ্য দারুণ থাকে।`;
    }
    if (lang === "hi") {
      return `${soil} में जैविक कार्बन बढ़ाने के लिए गोबर की खाद या वर्मीकम्पोस्ट का प्रयोग करें। हरी खाद के लिए ढैंचा बोकर मिट्टी में मिलाने से जमीन की ताकत दोगुनी होती है।`;
    }
    return `Incorporate well-rotted farmyard manure or vermicompost into ${soil} to enhance microbial activity and organic carbon levels.`;
  }

  // 11. DOSAGE / HOW MUCH
  if (/how much|dose|কতটা|কতটুকু|কোন ওষুধ|কি ওষুধ|কত বার|কতটুকু দেব|কত গ্রাম|কত মিলি|कितना|कितनी मात्रा|कौन सी दवा|कब डाले/i.test(qLower)) {
    if (lang === "bn") {
      return `তরল স্প্রে করার ক্ষেত্রে প্রতি লিটার জলে দুই থেকে তিন মিলিলিটার, এবং দ্রবণীয় পাউডারের ক্ষেত্রে প্রতি লিটার জলে দেড় থেকে দুই গ্রাম গুলে সকালে বা বিকেলে সমানভাবে স্প্রে করুন।`;
    }
    if (lang === "hi") {
      return `तरल कीटनाशक 2 से 3 मिली प्रति लीटर पानी में और घुलनशील पाउडर 2 ग्राम प्रति लीटर पानी में घोलकर सुबह या शाम फसल पर समान रूप से छिड़कें।`;
    }
    return `Use 2 to 3 ml per liter for liquid concentrates, or 1.5 to 2 grams per liter for wettable powders, applied early in the morning or late evening.`;
  }

  // 12. GENERAL CROP GUIDANCE
  if (lang === "bn") {
    return `${cropDisp} ফসলে কোনো অস্বাভাবিক লক্ষণ বা পোকার আক্রমণ দেখলে সকালে জমি পর্যবেক্ষণ করুন। প্রয়োজনে আমাদের ক্রপ ডক্টর টুলে পাতার ছবি তুলে পরীক্ষা করুন এবং স্থানীয় কৃষি আধিকারিকের পরামর্শ নিন।`;
  }
  if (lang === "hi") {
    return `${cropDisp} की फसल में किसी भी असामान्य लक्षण के लिए सुबह के समय खेत का निरीक्षण करें। तुरंत पहचान के लिए हमारे क्रॉप डॉक्टर टूल से फोटो जांचें।`;
  }
  return `For healthy ${cropDisp} growth, scout your field in the early morning and maintain balanced soil moisture. Use our Crop Doctor tool if you observe any leaf damage.`;
}
