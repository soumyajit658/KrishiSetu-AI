import { createContext, useContext, useState, useEffect } from "react";
import { TRANSLATIONS } from "../utils/translations";

const LanguageContext = createContext();

const SUPPORTED_LANGUAGES = [
  { code: "en", label: "English", native: "English", flag: "🇬🇧" },
  { code: "hi", label: "Hindi", native: "हिन्दी", flag: "🇮🇳" },
  { code: "bn", label: "Bengali", native: "বাংলা", flag: "🇮🇳" },
];

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

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        t,
        translateCrop,
        translateSoil,
        translateIrrigation,
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
