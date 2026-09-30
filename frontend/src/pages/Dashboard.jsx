import { useState, useEffect } from "react";
import {
  CloudSun,
  Droplets,
  Satellite,
  Bot,
  Sprout,
  MapPin,
  Leaf,
  ShieldCheck,
  ArrowRight,
  Sparkles,
  Stethoscope,
  Camera,
  Layers,
  Recycle,
  Mic,
  Volume2,
} from "lucide-react";
import { api } from "../services/api";
import { useLanguage } from "../context/LanguageContext";
import LanguageSelector from "../components/LanguageSelector";

function Dashboard({
  onGoHome,
  onSetupFarm,
  farmData,
  farmerProfile,
  onOpenProfile,
  onOpenWeather,
  onOpenDisease,
  onOpenSatellite,
  onOpenChat,
  onOpenAdvisory,
  onOpenCropDoctor,
  onOpenRegenerative,
  onOpenVoice,
}) {
  const { t, language, translateCrop, translateSoil, translateIrrigation, translateFarmerName } = useLanguage();
  const [liveWeather, setLiveWeather] = useState(null);

  // Auto-fetch live weather preview for dashboard header card
  useEffect(() => {
    let isMounted = true;
    const loadWeatherPreview = async () => {
      try {
        const data = await api.getWeather(farmData?.location || "Haldia, West Bengal");
        if (isMounted) {
          setLiveWeather(data);
        }
      } catch (err) {
        console.error(err);
      }
    };
    loadWeatherPreview();
    return () => {
      isMounted = false;
    };
  }, [farmData?.location]);

  const cropName = farmData?.crop ? translateCrop(farmData.crop) : "";
  const rawFarmerName = farmerProfile?.name || t("common.farmer");
  const farmerDisplayName = translateFarmerName(rawFarmerName);

  return (
    <div className="dashboard">
      {/* ================= HEADER ================= */}
      <header className="dashboard-header">
        <div
          className="dashboard-brand clickable"
          onClick={onGoHome}
          role="button"
          tabIndex={0}
          title="Return to starting page / मुख्य पृष्ठ पर जाएं"
        >
          <div className="dashboard-logo">
            <Sprout size={25} className="brand-sprout-icon" />
          </div>
          <div className="brand-text-block">
            <h2>
              <span className="brand-name-text">
                Krishi<span className="brand-highlight">Setu</span>
              </span>
              <span className="brand-ai-badge">AI</span>
            </h2>
            <span className="brand-subtext">{t("common.brandSub")}</span>
          </div>
        </div>

        <div className="dashboard-header-right">
          <LanguageSelector variant="dashboard" />
          <div
            className="farmer-profile clickable"
            onClick={onOpenProfile}
            role="button"
            tabIndex={0}
            title="Click to view & edit Farmer Profile"
          >
            <div className="profile-avatar">
              {farmerProfile?.avatarType === "image" && farmerProfile?.avatarImage ? (
                <img
                  src={farmerProfile.avatarImage}
                  alt={farmerDisplayName}
                  className="profile-avatar-thumb"
                />
              ) : (
                <span className="profile-avatar-emoji">
                  {farmerProfile?.avatarEmoji || "👨‍🌾"}
                </span>
              )}
            </div>
            <div>
              <strong>{farmerDisplayName}</strong>
              <small>{cropName ? `${cropName} ${t("common.grower")}` : t("common.myFarm")}</small>
            </div>
          </div>
        </div>
      </header>

      {/* ================= MAIN ================= */}
      <main className="dashboard-main">
        {/* ================= WELCOME ================= */}
        <section className="dashboard-welcome">
          <div className="welcome-text">
            <span className="dashboard-label">{t("dashboard.controlCenter")}</span>
            <h1>
              {farmerProfile?.name
                ? `${t("dashboard.greetingPrefix", "Good day")}, ${farmerDisplayName} 👋`
                : t("dashboard.greeting")}
            </h1>
            <p>{t("dashboard.welcomeDesc")}</p>
          </div>

          {/* FARM LOCATION */}
          <div className="location-box" onClick={onOpenWeather} role="button" title="View detailed weather forecast">
            <MapPin size={21} />
            <div>
              <small>{t("dashboard.farmLocation")}</small>
              <strong>
                {farmData?.location ? farmData.location : "Haldia, West Bengal"}
              </strong>
            </div>
            {liveWeather && (
              <span className="quick-temp-badge">
                {liveWeather.icon} {Math.round(liveWeather.temperature)}°C
              </span>
            )}
          </div>
        </section>

        {/* ================= FARM SETUP / INFORMATION ================= */}
        <section className="farm-setup">
          <div className="setup-icon">
            <Sprout size={27} />
          </div>

          <div className="setup-content">
            {farmData ? (
              <>
                <span>{t("dashboard.registeredProfile")}</span>
                <h3>{cropName ? `${cropName} ${t("dashboard.cropFarm")}` : `${t("common.myFarm")}`}</h3>
                <p>
                  📍 {farmData.location || t("dashboard.notSet")} &nbsp; • &nbsp; 🌱 {farmData.area || 1} {t("common.acres")}
                </p>

                <div className="farm-details-row">
                  <span>
                    {t("dashboard.soil")}: <strong>{translateSoil(farmData.soil || "Loamy Soil")}</strong>
                  </span>
                  <span>
                    {t("dashboard.irrigation")}: <strong>{translateIrrigation(farmData.irrigation || "Tube Well")}</strong>
                  </span>
                </div>
              </>
            ) : (
              <>
                <span>{t("landing.getStarted")}</span>
                <h3>{t("dashboard.setUpFarm")}</h3>
                <p>{t("dashboard.setUpFarmDesc")}</p>
              </>
            )}
          </div>

          {/* SETUP / EDIT BUTTON */}
          <button className="setup-btn" onClick={onSetupFarm}>
            {farmData ? t("dashboard.editFarm") : t("dashboard.setUpFarm")}
            <ArrowRight size={18} />
          </button>
        </section>

        {/* ================= AI CROP & FIELD DOCTOR HERO CARD ================= */}
        <section className="doctor-hero-banner clickable" onClick={onOpenCropDoctor} role="button">
          <div className="doctor-hero-content">
            <div className="doctor-badge-row">
              <Stethoscope size={16} />
              <span>{t("dashboard.doctorHeroBadge")}</span>
            </div>
            <h2>{t("dashboard.doctorHeroTitle")}</h2>
            <p>{t("dashboard.doctorHeroDesc")}</p>
            <div className="doctor-feature-pills">
              <span><Camera size={13} /> {t("dashboard.pillPhotos")}</span>
              <span><Layers size={13} /> {t("dashboard.pillLand")}</span>
              <span><Satellite size={13} /> {t("dashboard.pillSat")}</span>
              <span><Bot size={13} /> {t("dashboard.pillChat")}</span>
            </div>
          </div>
          <button className="doctor-hero-btn" onClick={onOpenCropDoctor}>
            {t("dashboard.launchDoctor")}
            <ArrowRight size={18} />
          </button>
        </section>

        {/* ================= KRISHIBANDHU(AI) VOICE HERO BANNER ================= */}
        <section className="voice-hero-banner clickable" onClick={onOpenVoice} role="button">
          <div className="voice-hero-content">
            <div className="voice-hero-badge-row">
              <Mic size={14} />
              <span>🎙️ KrishiBandhu(AI) • আঞ্চলিক ভয়েস • क्षेत्रीय वॉयस</span>
            </div>
            <h2>
              {language === "bn"
                ? "মুখে বলুন, কৃশিবন্ধু(AI) আপনার ভাষায় উত্তর দেবে 🌾"
                : language === "hi"
                ? "अपनी भाषा में बोलें, कृषिबंधु(AI) आवाज में सलाह देगा 🌾"
                : "Speak Naturally. KrishiBandhu(AI) Speaks Back 🌾"}
            </h2>
            <p>
              {language === "bn"
                ? "কৃষকদের জন্য স্বয়ংক্রিয় ভয়েস সহকারী। বাংলা, হিন্দি বা ইংরেজিতে মুখে জিজ্ঞাসা করুন এবং কণ্ঠস্বরে উত্তর শুনুন।"
                : language === "hi"
                ? "किसानों के लिए ऑटो वॉयस असिस्टेंट। हिन्दी, বাংলা या English में बोलकर पूछें और तुरंत आवाज में सलाह पाएं।"
                : "AI voice assistant for farmers. Tap and speak in Hindi, Bengali, or English — KrishiBandhu(AI) automatically understands and speaks back."}
            </p>
            <div className="voice-lang-preview-pills">
              <span>🌐 Auto Detect</span>
              <span>हिन्दी</span>
              <span>বাংলা</span>
              <span>English</span>
              <span>🔊 Spoken Voice</span>
            </div>
          </div>
          <button className="voice-hero-btn" onClick={onOpenVoice}>
            <Mic size={18} />
            {language === "bn" ? "ভয়েস শুরু করুন" : language === "hi" ? "बोलना शुरू करें" : "Start Voice"}
            <ArrowRight size={18} />
          </button>
        </section>

        {/* ================= FARM INSIGHTS ================= */}
        <section className="dashboard-section">
          <div className="section-heading">
            <div>
              <span className="section-label">{t("dashboard.liveObservation")}</span>
              <h2>{t("dashboard.farmInsights")}</h2>
              <p>{t("dashboard.farmInsightsDesc")}</p>
            </div>
          </div>

          <div className="insight-grid">
            {/* ================= WEATHER CARD ================= */}
            <div className="insight-card clickable" onClick={onOpenWeather} role="button">
              <div className="insight-icon weather">
                <CloudSun size={26} />
              </div>
              <div className="insight-info">
                <span>{t("dashboard.weatherTitle")}</span>
                <strong>
                  {liveWeather
                    ? `${Math.round(liveWeather.temperature)}°C • ${liveWeather.condition}`
                    : t("dashboard.weatherReady")}
                </strong>
                <small>
                  {liveWeather
                    ? `Humidity: ${liveWeather.humidity}% • Wind: ${liveWeather.wind_speed} km/h`
                    : t("dashboard.weatherSub")}
                </small>
              </div>
              <ArrowRight className="card-arrow" size={18} />
            </div>

            {/* ================= SOIL CARD ================= */}
            <div className="insight-card clickable" onClick={onOpenAdvisory} role="button">
              <div className="insight-icon soil">
                <Droplets size={26} />
              </div>
              <div className="insight-info">
                <span>{t("dashboard.soilTitle")}</span>
                <strong>{translateSoil(farmData?.soil || "Alluvial Soil")}</strong>
                <small>{t("dashboard.soilSub")}</small>
              </div>
              <ArrowRight className="card-arrow" size={18} />
            </div>

            {/* ================= SATELLITE CARD ================= */}
            <div className="insight-card clickable" onClick={onOpenSatellite} role="button">
              <div className="insight-icon satellite">
                <Satellite size={26} />
              </div>
              <div className="insight-info">
                <span>{t("dashboard.satelliteTitle")}</span>
                <strong>{t("dashboard.satelliteHealthy")}</strong>
                <small>{t("dashboard.satelliteSub")}</small>
              </div>
              <ArrowRight className="card-arrow" size={18} />
            </div>
          </div>
        </section>

        {/* ================= AI ADVISOR BANNER ================= */}
        <section className="ai-advisor">
          <div className="ai-icon">
            <Bot size={31} />
          </div>

          <div className="ai-content">
            <div className="ai-badge-row">
              <Sparkles size={14} />
              <span>{t("dashboard.aiAdvisorBadge")}</span>
            </div>
            <h2>{t("dashboard.askKrishiSetu")}</h2>
            <p>{t("dashboard.aiAdvisorDesc")}</p>
          </div>

          <button className="ai-button" onClick={onOpenChat}>
            {t("dashboard.askAiBtn")}
            <ArrowRight size={18} />
          </button>
        </section>

        {/* ================= SMART FARMING TOOLS ================= */}
        <section className="dashboard-section">
          <div className="section-heading">
            <div>
              <span className="section-label">{t("dashboard.toolkitBadge")}</span>
              <h2>{t("dashboard.smartToolsTitle")}</h2>
              <p>{t("dashboard.smartToolsDesc")}</p>
            </div>
          </div>

          <div className="tools-grid">
            {/* ================= CROP DOCTOR ================= */}
            <div className="tool-card">
              <div className="tool-icon">
                <Stethoscope size={25} />
              </div>
              <h3>{t("dashboard.doctorCardTitle")}</h3>
              <p>{t("dashboard.doctorCardDesc")}</p>
              <button onClick={onOpenCropDoctor}>
                {t("dashboard.openDoctorBtn")}
                <ArrowRight size={16} />
              </button>
            </div>

            {/* ================= QUICK DISEASE DETECTION ================= */}
            <div className="tool-card">
              <div className="tool-icon disease-icon">
                <ShieldCheck size={25} />
              </div>
              <h3>{t("dashboard.leafCheckTitle")}</h3>
              <p>{t("dashboard.leafCheckDesc")}</p>
              <button onClick={onOpenDisease}>
                {t("dashboard.quickCheckBtn")}
                <ArrowRight size={16} />
              </button>
            </div>

            {/* ================= SATELLITE MONITORING ================= */}
            <div className="tool-card">
              <div className="tool-icon">
                <Satellite size={25} />
              </div>
              <h3>{t("dashboard.satelliteToolTitle")}</h3>
              <p>{t("dashboard.satelliteToolDesc")}</p>
              <button onClick={onOpenSatellite}>
                {t("dashboard.viewFieldMapBtn")}
                <ArrowRight size={16} />
              </button>
            </div>

            {/* ================= CROP ADVISORY ================= */}
            <div className="tool-card">
              <div className="tool-icon">
                <Leaf size={25} />
              </div>
              <h3>{t("dashboard.advisoryToolTitle")}</h3>
              <p>{t("dashboard.advisoryToolDesc")}</p>
              <button onClick={onOpenAdvisory}>
                {t("dashboard.exploreAdvisoryBtn")}
                <ArrowRight size={16} />
              </button>
            </div>

            {/* ================= REGENERATIVE FARMING ================= */}
            <div className="tool-card regen-tool-card">
              <div className="tool-icon regen-icon">
                <Recycle size={25} />
              </div>
              <h3>Regenerative Farming</h3>
              <p>Cover crops, carbon sequestration, soil biology &amp; water conservation practices.</p>
              <button onClick={onOpenRegenerative}>
                View Regen Plan
                <ArrowRight size={16} />
              </button>
            </div>

            {/* ================= KRISHIBANDHU(AI) VOICE TOOL CARD ================= */}
            <div className="tool-card voice-tool-card" style={{ borderColor: "rgba(46,125,50,0.3)" }}>
              <div className="tool-icon" style={{ background: "#e8f5e9", color: "#2e7d32" }}>
                <Mic size={25} />
              </div>
              <h3>KrishiBandhu(AI) Voice</h3>
              <p>
                {language === "bn"
                  ? "স্বয়ংক্রিয় ভয়েস সহকারী। মুখে জিজ্ঞাসা করুন এবং বাংলায় অডিও শুনুন।"
                  : language === "hi"
                  ? "ऑटोमैटिक वॉयस असिस्टेंट। बोलकर पूछें और आवाज में सलाह सुनें।"
                  : "Speak naturally in Hindi, Bengali, or English and hear spoken advice."}
              </p>
              <button onClick={onOpenVoice}>
                {language === "bn" ? "ভয়েস শুরু করুন" : language === "hi" ? "बोलें" : "Launch Voice"}
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </section>

        {/* ================= FOOTER ================= */}
        <footer className="dashboard-footer">
          <span>{t("dashboard.footerBrand")}</span>
          <span>{t("dashboard.footerTagline")}</span>
        </footer>
      </main>

      {/* Floating KrishiBandhu(AI) Voice Button for Instant 1-Tap Access */}
      <button
        className="floating-voice-btn"
        onClick={onOpenVoice}
        title="KrishiBandhu(AI) Voice — Speak in your language"
        aria-label="Start KrishiBandhu Voice Assistant"
      >
        <div className="floating-voice-icon-box">
          <Mic size={18} />
        </div>
        <div className="floating-voice-text">
          <span className="floating-voice-title">🎙️ KrishiBandhu(AI)</span>
          <span className="floating-voice-sub">
            {language === "bn" ? "মুখে বলুন" : language === "hi" ? "बोलकर पूछें" : "Speak to AI"}
          </span>
        </div>
      </button>
    </div>
  );
}

export default Dashboard;