import { createContext, useContext, useState, useEffect } from "react";
import { TRANSLATIONS } from "../utils/translations";

const LanguageContext = createContext();

const SUPPORTED_LANGUAGES = [
  { code: "en", label: "English", native: "English", flag: "🇬🇧" },
  { code: "hi", label: "Hindi", native: "हिन्दी", flag: "🇮🇳" },
  { code: "bn", label: "Bengali", native: "বাংলা", flag: "🇮🇳" },
];

const FARMER_NAME_MAP = {
  "Ramesh Kumar": { bn: "রমেশ কুমার", hi: "रमेश कुमार", en: "Ramesh Kumar" },
  "Ramesh": { bn: "রমেশ", hi: "रमेश", en: "Ramesh" },
  "Kumar": { bn: "কুমার", hi: "कुमार", en: "Kumar" },
  "Farmer": { bn: "কৃষক বন্ধু", hi: "किसान भाई", en: "Farmer" },
  "Kisan": { bn: "কৃষক বন্ধু", hi: "किसान भाई", en: "Kisan" },
  "Suresh Kumar": { bn: "সুরেশ কুমার", hi: "सुरेश कुमार", en: "Suresh Kumar" },
  "Rajesh Kumar": { bn: "রাজেশ কুমার", hi: "राजेश कुमार", en: "Rajesh Kumar" },
  "Amit Kumar": { bn: "অমিত কুমার", hi: "अमित कुमार", en: "Amit Kumar" },
  "Saikat": { bn: "সৈকত", hi: "सैकत", en: "Saikat" },
  "Saikat Kumar": { bn: "সৈকত কুমার", hi: "सैकत कुमार", en: "Saikat Kumar" },
  "Anil Kumar": { bn: "অনিল কুমার", hi: "अनिल कुमार", en: "Anil Kumar" },
};

const INDIAN_NAME_TOKENS = {
  // First Names
  ramesh: { bn: "রমেশ", hi: "रमेश" },
  suresh: { bn: "সুরেশ", hi: "सुरेश" },
  rajesh: { bn: "রাজেশ", hi: "राजेश" },
  mahesh: { bn: "মহেশ", hi: "महेश" },
  dinesh: { bn: "দীনেশ", hi: "दिनेश" },
  naresh: { bn: "নরেশ", hi: "नरेश" },
  ganesh: { bn: "গণেশ", hi: "गणेश" },
  mukesh: { bn: "মুকেশ", hi: "मुकेश" },
  rakesh: { bn: "রাকেশ", hi: "राकेश" },
  anil: { bn: "অনিল", hi: "अनिल" },
  sunil: { bn: "সুনীল", hi: "सुनील" },
  amit: { bn: "অমিত", hi: "अमित" },
  sumit: { bn: "সুমিত", hi: "सुमित" },
  rahul: { bn: "রাহুল", hi: "राहुल" },
  rohit: { bn: "রোহিত", hi: "रोहित" },
  manoj: { bn: "মনোজ", hi: "मनोज" },
  sanjay: { bn: "সঞ্জয়", hi: "संजय" },
  ajay: { bn: "অজয়", hi: "अजय" },
  vijay: { bn: "বিজয়", hi: "विजय" },
  ashok: { bn: "অশোক", hi: "अशोक" },
  deepak: { bn: "দীপক", hi: "दीपक" },
  alok: { bn: "আলোক", hi: "आलोक" },
  saikat: { bn: "সৈকত", hi: "सैकत" },
  sourav: { bn: "সৌরভ", hi: "सौरव" },
  subhash: { bn: "সুভাষ", hi: "सुभाष" },
  prakash: { bn: "প্রকাশ", hi: "प्रकाश" },
  santosh: { bn: "সন্তোষ", hi: "संतोष" },
  gopal: { bn: "গোপাল", hi: "गोपाल" },
  govind: { bn: "গোবিন্দ", hi: "गोविंद" },
  mohan: { bn: "মোহন", hi: "मोहन" },
  sohan: { bn: "সোহন", hi: "सोहन" },
  rohan: { bn: "রোহন", hi: "रोहन" },
  shankar: { bn: "শঙ্কর", hi: "शंकर" },
  shiv: { bn: "শিব", hi: "शिव" },
  hari: { bn: "হরি", hi: "हरि" },
  ram: { bn: "রাম", hi: "राम" },
  chandan: { bn: "চন্দন", hi: "चंदन" },
  kalyan: { bn: "কল্যাণ", hi: "कल्याण" },
  narayan: { bn: "নারায়ণ", hi: "नारायण" },
  shyam: { bn: "শ্যাম", hi: "श्याम" },
  uttam: { bn: "উত্তম", hi: "उत्तम" },
  gautam: { bn: "গৌতম", hi: "गौतम" },
  tarun: { bn: "তরুণ", hi: "तरुण" },
  arun: { bn: "অরুণ", hi: "अरुण" },
  bikash: { bn: "বিকাশ", hi: "विकास" },
  bimal: { bn: "বিমল", hi: "विमल" },
  kamal: { bn: "কমল", hi: "कमल" },
  swapan: { bn: "স্বপন", hi: "स्वपन" },
  tapan: { bn: "তপন", hi: "तपन" },
  ratan: { bn: "রতন", hi: "रतन" },
  partha: { bn: "পার্থ", hi: "পার্থ" },
  tanmoy: { bn: "তন্ময়", hi: "तन्मय" },
  pradip: { bn: "প্রদীপ", hi: "प्रदीप" },
  sandip: { bn: "সন্দীপ", hi: "संदीप" },
  dilip: { bn: "দিলীপ", hi: "दिलीप" },
  raja: { bn: "রাজা", hi: "राजा" },
  farmer: { bn: "কৃষক বন্ধু", hi: "किसान भाई" },
  kisan: { bn: "কৃষক বন্ধু", hi: "किसान भाई" },

  // Surnames
  kumar: { bn: "কুমার", hi: "कुमार" },
  singh: { bn: "সিংহ", hi: "सिंह" },
  sharma: { bn: "শর্মা", hi: "शर्मा" },
  patel: { bn: "প্যাটেল", hi: "पटेल" },
  mondal: { bn: "মন্ডল", hi: "मंडल" },
  mandal: { bn: "মন্ডল", hi: "मंडल" },
  das: { bn: "দাস", hi: "दास" },
  ghosh: { bn: "ঘোষ", hi: "घोष" },
  roy: { bn: "রায়", hi: "राय" },
  ray: { bn: "রায়", hi: "राय" },
  yadav: { bn: "যাদব", hi: "यादव" },
  ali: { bn: "আলী", hi: "अली" },
  khan: { bn: "খান", hi: "खान" },
  babu: { bn: "বাবু", hi: "बाबू" },
  lal: { bn: "লাল", hi: "लाल" },
  mahto: { bn: "মাহাতো", hi: "महतो" },
  choudhury: { bn: "চৌধুরী", hi: "चौधरी" },
  chowdhury: { bn: "চৌধুরী", hi: "चौधरी" },
  prasad: { bn: "প্রসাদ", hi: "प्रसाद" },
  verma: { bn: "বর্মা", hi: "वर्मा" },
  gupta: { bn: "গুপ্ত", hi: "गुप्ता" },
  paul: { bn: "পাল", hi: "पाल" },
  biswas: { bn: "বিশ্বাস", hi: "विश्वास" },
  sen: { bn: "সেন", hi: "सेन" },
  chatterjee: { bn: "চ্যাটার্জী", hi: "चैटर्जी" },
  banerjee: { bn: "ব্যানার্জী", hi: "बैनर्जी" },
  mukherjee: { bn: "মুখার্জী", hi: "मुखर्जी" },
  dutta: { bn: "দত্ত", hi: "दत्ता" },
  saha: { bn: "সাহা", hi: "साहा" },
  bhowmick: { bn: "ভৌমিক", hi: "भौमिक" },
  debnath: { bn: "দেবনাথ", hi: "देवनाथ" },
  barman: { bn: "বর্মন", hi: "बर्मन" },
  majumdar: { bn: "মজুমদার", hi: "मजूमदार" },
  sardar: { bn: "সরদার", hi: "सरदार" },
  naskar: { bn: "নস্কর", hi: "नस्कर" },
  halder: { bn: "হালদার", hi: "हालदार" },
  samanta: { bn: "সামন্ত", hi: "सामंत" },
  adhikari: { bn: "অধিকারী", hi: "अधिकारी" },
  pramanik: { bn: "প্রামাণিক", hi: "प्रमाणिक" },
  bera: { bn: "বেড়া", hi: "बेरा" },
  sasmal: { bn: "সাসমল", hi: "सासमल" },
  giri: { bn: "গিরি", hi: "गिरी" },
  jana: { bn: "জানা", hi: "जाना" },
  maiti: { bn: "মাইতি", hi: "माइती" },
  ghorai: { bn: "ঘোড়াই", hi: "घोराई" },
  patra: { bn: "পাত্র", hi: "पात्रा" },
  khatua: { bn: "খাটুয়া", hi: "खटुआ" },
  devi: { bn: "দেবী", hi: "देवी" },
  rani: { bn: "রানী", hi: "रानी" },
};

export function LanguageProvider({ children }) {
  const [language, setLanguageState] = useState(() => {
    try {
      return localStorage.getItem("krishi_language") || "en";
    } catch {
      return "en";
    }
  });

  const setLanguage = (langCode) => {
    if (["en", "hi", "bn"].includes(langCode)) {
      setLanguageState(langCode);
      try {
        localStorage.setItem("krishi_language", langCode);
      } catch (e) {
        console.error("Failed to save language preference:", e);
      }
    }
  };

  useEffect(() => {
    try {
      localStorage.setItem("krishi_language", language);
    } catch (e) {
      console.error(e);
    }
  }, [language]);

  // Translation helper function supporting nested paths like "dashboard.greeting"
  const t = (path, fallback = "") => {
    if (!path) return fallback;
    const activeDict = TRANSLATIONS[language] || TRANSLATIONS.en;
    const fallbackDict = TRANSLATIONS.en;

    const parts = path.split(".");
    let val = activeDict;
    for (const part of parts) {
      if (val && typeof val === "object" && part in val) {
        val = val[part];
      } else {
        val = undefined;
        break;
      }
    }

    if (val !== undefined && typeof val === "string") {
      return val;
    }

    // Try fallback to English dictionary
    let fVal = fallbackDict;
    for (const part of parts) {
      if (fVal && typeof fVal === "object" && part in fVal) {
        fVal = fVal[part];
      } else {
        fVal = undefined;
        break;
      }
    }

    if (fVal !== undefined && typeof fVal === "string") {
      return fVal;
    }

    return fallback || path;
  };

  // Helper translators for dynamic farm profile terms
  const translateCrop = (cropName) => {
    if (!cropName) return "";
    return t(`crops.${cropName}`, cropName);
  };

  const translateSoil = (soilName) => {
    if (!soilName) return "";
    return t(`soils.${soilName}`, soilName);
  };

  const translateIrrigation = (irrigationName) => {
    if (!irrigationName) return "";
    return t(`irrigation.${irrigationName}`, irrigationName);
  };

  // Farmer profile name translation & transliteration (Ramesh Kumar -> রমেশ কুমার / रमेश कुमार)
  const translateFarmerName = (name) => {
    if (!name) return "";
    if (language === "en") return name;

    const trimmed = name.trim();
    if (FARMER_NAME_MAP[trimmed] && FARMER_NAME_MAP[trimmed][language]) {
      return FARMER_NAME_MAP[trimmed][language];
    }

    // Preserve if already in Bengali (\u0980-\u09FF) or Devanagari (\u0900-\u097F)
    if (/[\u0980-\u09FF]/.test(trimmed) && language === "bn") return trimmed;
    if (/[\u0900-\u097F]/.test(trimmed) && language === "hi") return trimmed;

    // Word-by-word token translation
    const words = trimmed.split(/\s+/);
    const translated = words.map((w) => {
      const clean = w.toLowerCase().replace(/[^a-z]/g, "");
      if (INDIAN_NAME_TOKENS[clean] && INDIAN_NAME_TOKENS[clean][language]) {
        return INDIAN_NAME_TOKENS[clean][language];
      }
      return w;
    });

    return translated.join(" ");
  };

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        t,
        translateCrop,
        translateSoil,
        translateIrrigation,
        translateFarmerName,
        supportedLanguages: SUPPORTED_LANGUAGES,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}
