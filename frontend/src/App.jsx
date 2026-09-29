import { useState, useEffect } from "react";
import {
  Sprout,
  Satellite,
  CloudSun,
  Bot,
  ArrowRight,
} from "lucide-react";

import Dashboard from "./pages/Dashboard";
import FarmSetup from "./pages/FarmSetup";

import ChatModal from "./components/ChatModal";
import DiseaseModal from "./components/DiseaseModal";
import WeatherModal from "./components/WeatherModal";
import SatelliteModal from "./components/SatelliteModal";
import AdvisoryModal from "./components/AdvisoryModal";
import CropDoctorModal from "./components/CropDoctorModal";
import FarmerProfileModal from "./components/FarmerProfileModal";
import RegenerativeModal from "./components/RegenerativeModal";
import VoiceAssistantModal from "./components/VoiceAssistantModal";
import LanguageSelector from "./components/LanguageSelector";
import { useLanguage } from "./context/LanguageContext";

import "./index.css";
import "./App.css";

// Default initial farm profile for immediate testing
const DEFAULT_FARM_DATA = {
  location: "Haldia, West Bengal",
  crop: "Rice",
  area: "2.5",
  soil: "Alluvial Soil",
  irrigation: "Canal",
};

// Default initial farmer profile
const DEFAULT_FARMER_PROFILE = {
  name: "Ramesh Kumar",
  phone: "+91 98321 45678",
  location: "Haldia, West Bengal",
  experienceYears: "14",
  farmerType: "Small & Marginal Farmer",
  avatarType: "emoji", // "emoji" or "image"
  avatarEmoji: "👨‍🌾",
  avatarImage: null,
  kisanId: "KISAN-WB-7842",
  bio: "Third-generation paddy farmer focusing on sustainable soil health, high-efficiency canal irrigation, and AI-driven precision crop protection.",
};

function App() {
  const { t } = useLanguage();
  const [showLogin, setShowLogin] = useState(false);
  const [showDashboard, setShowDashboard] = useState(() => {
    try {
      return (
        window.location.hash === "#dashboard" ||
        window.location.search.includes("dashboard")
      );
    } catch {
      return false;
    }
  });
  const [showFarmSetup, setShowFarmSetup] = useState(false);

  // Active Modals
  const [showChatModal, setShowChatModal]               = useState(false);
  const [showDiseaseModal, setShowDiseaseModal]         = useState(false);
  const [showWeatherModal, setShowWeatherModal]         = useState(false);
  const [showSatelliteModal, setShowSatelliteModal]     = useState(false);
  const [showAdvisoryModal, setShowAdvisoryModal]       = useState(false);
  const [showCropDoctorModal, setShowCropDoctorModal]   = useState(false);
  const [showFarmerProfileModal, setShowFarmerProfileModal] = useState(false);
  const [showRegenerativeModal, setShowRegenerativeModal] = useState(false);
  const [showVoiceModal, setShowVoiceModal]             = useState(false);

  // Latest analysis context to pass to AI Chatbot
  const [latestAnalysis, setLatestAnalysis] = useState(null);

  // Stores the farmer's farm information with localStorage persistence
  const [farmData, setFarmData] = useState(() => {
    try {
      const saved = localStorage.getItem("krishi_farm_data");
      return saved ? JSON.parse(saved) : DEFAULT_FARM_DATA;
    } catch {
      return DEFAULT_FARM_DATA;
    }
  });

  // Stores the farmer's personal profile information with localStorage persistence
  const [farmerProfile, setFarmerProfile] = useState(() => {
    try {
      const saved = localStorage.getItem("krishi_farmer_profile");
      return saved ? JSON.parse(saved) : DEFAULT_FARMER_PROFILE;
    } catch {
      return DEFAULT_FARMER_PROFILE;
    }
  });

  // Save to localStorage whenever farmData updates
  useEffect(() => {
    try {
      localStorage.setItem("krishi_farm_data", JSON.stringify(farmData));
    } catch (e) {
      console.error(e);
    }
  }, [farmData]);

  // Save to localStorage whenever farmerProfile updates
  useEffect(() => {
    try {
      localStorage.setItem("krishi_farmer_profile", JSON.stringify(farmerProfile));
    } catch (e) {
      console.error(e);
    }
  }, [farmerProfile]);

  // =====================================================
  // FARM SETUP VIEW
  // =====================================================
  if (showFarmSetup) {
    return (
      <FarmSetup
        initialData={farmData}
        onBack={() => {
          setShowFarmSetup(false);
          setShowDashboard(true);
        }}
        onSave={(data) => {
          setFarmData(data);
          setShowFarmSetup(false);
          setShowDashboard(true);
        }}
      />
    );
  }

  // =====================================================
  // DASHBOARD VIEW
  // =====================================================
  if (showDashboard) {
    return (
      <>
        <Dashboard
          onGoHome={() => {
            setShowDashboard(false);
            setShowFarmSetup(false);
            setShowLogin(false);
            try {
              window.history.pushState(null, "", window.location.pathname);
            } catch (e) {
              console.error(e);
            }
            window.scrollTo({ top: 0, behavior: "smooth" });
          }}
          onSetupFarm={() => setShowFarmSetup(true)}
          farmData={farmData}
          farmerProfile={farmerProfile}
          onOpenProfile={() => setShowFarmerProfileModal(true)}
          onOpenWeather={() => setShowWeatherModal(true)}
          onOpenDisease={() => setShowDiseaseModal(true)}
          onOpenSatellite={() => setShowSatelliteModal(true)}
          onOpenChat={() => {
            setLatestAnalysis(null);
            setShowChatModal(true);
          }}
          onOpenAdvisory={() => setShowAdvisoryModal(true)}
          onOpenCropDoctor={() => setShowCropDoctorModal(true)}
          onOpenRegenerative={() => setShowRegenerativeModal(true)}
          onOpenVoice={() => setShowVoiceModal(true)}
        />

        {/* Global Action Modals */}
        <FarmerProfileModal
          isOpen={showFarmerProfileModal}
          onClose={() => setShowFarmerProfileModal(false)}
          farmerProfile={farmerProfile}
          onUpdateProfile={setFarmerProfile}
          farmData={farmData}
          onSetupFarm={() => {
            setShowFarmerProfileModal(false);
            setShowFarmSetup(true);
          }}
        />

        <ChatModal
          isOpen={showChatModal}
          onClose={() => setShowChatModal(false)}
          farmData={farmData}
          analysisContext={latestAnalysis}
          onClearContext={() => setLatestAnalysis(null)}
        />

        <CropDoctorModal
          isOpen={showCropDoctorModal}
          onClose={() => setShowCropDoctorModal(false)}
          farmData={farmData}
          onOpenChatWithContext={(report) => {
            setLatestAnalysis(report);
            setShowChatModal(true);
          }}
        />

        <VoiceAssistantModal
          isOpen={showVoiceModal}
          onClose={() => setShowVoiceModal(false)}
          farmData={farmData}
          fieldContext={latestAnalysis}
          onOpenDoctor={() => {
            setShowVoiceModal(false);
            setShowCropDoctorModal(true);
          }}
        />

        <DiseaseModal
          isOpen={showDiseaseModal}
          onClose={() => setShowDiseaseModal(false)}
          farmData={farmData}
        />

        <WeatherModal
          isOpen={showWeatherModal}
          onClose={() => setShowWeatherModal(false)}
          farmData={farmData}
        />

        <SatelliteModal
          isOpen={showSatelliteModal}
          onClose={() => setShowSatelliteModal(false)}
          farmData={farmData}
        />

        <AdvisoryModal
          isOpen={showAdvisoryModal}
          onClose={() => setShowAdvisoryModal(false)}
          farmData={farmData}
        />

        <RegenerativeModal
          isOpen={showRegenerativeModal}
          onClose={() => setShowRegenerativeModal(false)}
          farmData={farmData}
        />
      </>
    );
  }

  // =====================================================
  // LOGIN VIEW
  // =====================================================
  if (showLogin) {
    return (
      <div className="login-page">
        <div className="login-card">
          <div className="logo-circle">
            <Sprout size={34} />
          </div>

          <h1>{t("landing.loginTitle")}</h1>
          <p className="subtitle">{t("landing.loginSubtitle")}</p>

          <input type="email" placeholder={t("landing.emailPlaceholder")} defaultValue="farmer@krishisetu.ai" />
          <input type="password" placeholder={t("landing.passwordPlaceholder")} defaultValue="password123" />

          <button
            className="primary-btn login-btn"
            onClick={() => {
              setShowLogin(false);
              setShowDashboard(true);
            }}
          >
            {t("landing.loginBtn")}
            <ArrowRight size={20} />
          </button>

          <button
            className="back-btn"
            onClick={() => {
              setShowLogin(false);
            }}
          >
            {t("landing.backToWelcome")}
          </button>
        </div>
      </div>
    );
  }

  // =====================================================
  // LANDING PAGE VIEW
  // =====================================================
  return (
    <div className="app">
      {/* HEADER */}
      <header className="topbar">
        <div
          className="brand clickable"
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          role="button"
          tabIndex={0}
          title="KrishiSetu - Return to top"
        >
          <div className="brand-icon">
            <Sprout size={28} className="brand-sprout-icon" />
          </div>
          <div className="brand-text-block">
            <span className="brand-title">
              <span className="brand-name-text">
                Krishi<span className="brand-highlight">Setu</span>
              </span>
              <span className="brand-ai-badge">AI</span>
            </span>
            <span className="brand-tagline">{t("common.brandSub")}</span>
          </div>
        </div>

        {/* Global Language Selector */}
        <LanguageSelector variant="topbar" />
      </header>

      {/* HERO */}
      <main className="hero">
        <div className="hero-overlay"></div>

        {/* LEFT CONTENT */}
        <section className="hero-content">
          <div className="welcome-badge">
            🌾
            <span>{t("landing.welcomeBadge")}</span>
          </div>

          <h1>
            {t("landing.title")}
            <br />
            <span>{t("landing.subtitle")}</span>
          </h1>

          <p>{t("landing.desc")}</p>

          {/* BUTTONS */}
          <div className="hero-buttons">
            <button
              className="primary-btn"
              onClick={() => {
                setShowDashboard(true);
              }}
            >
              {t("landing.getStarted")}
              <ArrowRight size={21} />
            </button>

            <button
              className="secondary-btn"
              onClick={() => {
                setShowLogin(true);
              }}
            >
              {t("landing.haveAccount")}
            </button>
          </div>

          {/* FEATURES */}
          <div className="feature-row">
            <div className="feature-item">
              <Satellite size={24} />
              <span>{t("landing.satelliteInsights")}</span>
            </div>

            <div className="feature-divider"></div>

            <div className="feature-item">
              <CloudSun size={24} />
              <span>{t("landing.weatherGuidance")}</span>
            </div>

            <div className="feature-divider"></div>

            <div className="feature-item">
              <Bot size={24} />
              <span>{t("landing.aiAssistance")}</span>
            </div>
          </div>
        </section>

        {/* RIGHT VISUAL CARD */}
        <section className="hero-visual">
          <div className="farm-card">
            <div className="farm-icon">🌾</div>
            <h2>{t("common.myFarm")}</h2>
            <p>{t("dashboard.welcomeDesc")}</p>

            <div
              className="farm-feature clickable"
              onClick={() => {
                setShowDashboard(true);
                setShowWeatherModal(true);
              }}
            >
              <div className="farm-feature-icon">🌦️</div>
              <div className="farm-feature-text">
                <strong>{t("dashboard.weatherTitle")}</strong>
                <span>{t("landing.weatherGuidance")}</span>
              </div>
              <ArrowRight size={21} />
            </div>

            <div
              className="farm-feature clickable"
              onClick={() => {
                setShowDashboard(true);
                setShowSatelliteModal(true);
              }}
            >
              <div className="farm-feature-icon">🛰️</div>
              <div className="farm-feature-text">
                <strong>{t("dashboard.satelliteTitle")}</strong>
                <span>{t("landing.satelliteInsights")}</span>
              </div>
              <ArrowRight size={21} />
            </div>

            <div
              className="farm-feature clickable"
              onClick={() => {
                setShowDashboard(true);
                setShowDiseaseModal(true);
              }}
            >
              <div className="farm-feature-icon">🔍</div>
              <div className="farm-feature-text">
                <strong>{t("dashboard.leafCheckTitle")}</strong>
                <span>{t("dashboard.leafCheckDesc")}</span>
              </div>
              <ArrowRight size={21} />
            </div>
          </div>
        </section>
      </main>

      {/* FOOTER */}
      <footer>
        <span>{t("dashboard.footerBrand")}</span>
        <span>{t("dashboard.footerTagline")}</span>
      </footer>

      {/* Voice Assistant Modal accessible from Landing Page */}
      <VoiceAssistantModal
        isOpen={showVoiceModal}
        onClose={() => setShowVoiceModal(false)}
        farmData={farmData}
        fieldContext={latestAnalysis}
        onOpenDoctor={() => {
          setShowVoiceModal(false);
          setShowDashboard(true);
          setShowCropDoctorModal(true);
        }}
      />
    </div>
  );
}

export default App;