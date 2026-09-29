import { useState, useRef, useEffect } from "react";
import { Globe, ChevronDown, Check } from "lucide-react";
import { useLanguage } from "../context/LanguageContext";

function LanguageSelector({ variant = "standard", align = "right" }) {
  const { language, setLanguage, supportedLanguages } = useLanguage();
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const currentLang = supportedLanguages.find((l) => l.code === language) || supportedLanguages[0];

  return (
    <div className={`lang-selector-wrapper lang-variant-${variant}`} ref={containerRef}>
      <button
        type="button"
        className="language-btn"
        onClick={() => setOpen(!open)}
        title="Change Language / भाषा बदलें / ভাষা পরিবর্তন করুন"
        aria-label="Change Language"
      >
        <Globe size={18} className="globe-icon" />
        <span className="lang-label">{currentLang.native}</span>
        <ChevronDown size={14} className={`chevron-icon ${open ? "rotated" : ""}`} />
      </button>

      {open && (
        <div className={`language-dropdown-menu align-${align}`}>
          <div className="lang-menu-header">Select Language / भाषा चुनें</div>
          {supportedLanguages.map((lang) => (
            <button
              key={lang.code}
              type="button"
              className={`lang-option-item ${language === lang.code ? "active" : ""}`}
              onClick={() => {
                setLanguage(lang.code);
                setOpen(false);
              }}
            >
              <div className="lang-option-text">
                <span className="lang-native-name">{lang.native}</span>
                <span className="lang-eng-name">({lang.label})</span>
              </div>
              {language === lang.code && <Check size={15} className="lang-check" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default LanguageSelector;
