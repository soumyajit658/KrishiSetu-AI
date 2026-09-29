import { useState, useEffect } from "react";
import {
  CloudSun,
  Droplets,
  Wind,
  MapPin,
  X,
  RefreshCw,
  AlertCircle,
  Calendar,
  Thermometer,
} from "lucide-react";
import { api } from "../services/api";
import { useLanguage } from "../context/LanguageContext";

function WeatherModal({ isOpen, onClose, farmData }) {
  const { t, language } = useLanguage();
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchWeather();
    }
  }, [isOpen, farmData?.location]);

  const fetchWeather = async () => {
    setLoading(true);
    try {
      const data = await api.getWeather(farmData?.location || "Haldia, West Bengal");
      setWeather(data);
    } catch (err) {
      console.error("Failed to load weather:", err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container weather-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="modal-header-brand">
            <div className="modal-icon-badge weather">
              <CloudSun size={22} />
            </div>
            <div>
              <h3>{t("modals.weather.title")}</h3>
              <p className="modal-subtext">
                {t("modals.weather.subtext")} ({farmData?.location || "India"})
              </p>
            </div>
          </div>
          <button className="close-btn" onClick={onClose} title={t("common.close")}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {loading && !weather ? (
            <div className="loading-state">
              <RefreshCw size={24} className="spinning" />
              <span>{t("common.loading")}</span>
            </div>
          ) : weather ? (
            <>
              {/* Main Weather Hero Card */}
              <div className="weather-hero-card">
                <div className="weather-main-left">
                  <div className="weather-big-icon">{weather.icon || "🌤️"}</div>
                  <div>
                    <div className="temperature-row">
                      <span className="current-temp">{Math.round(weather.temperature)}°C</span>
                      <span className="weather-condition">{weather.condition}</span>
                    </div>
                    <p className="weather-location-label">
                      <MapPin size={15} /> {weather.location}
                      {weather.admin ? `, ${weather.admin}` : ""}
                    </p>
                  </div>
                </div>

                <div className="weather-stats-grid">
                  <div className="weather-stat-item">
                    <Droplets size={18} className="stat-icon blue" />
                    <div>
                      <small>{t("modals.weather.humidity")}</small>
                      <strong>{weather.humidity}%</strong>
                    </div>
                  </div>
                  <div className="weather-stat-item">
                    <Wind size={18} className="stat-icon teal" />
                    <div>
                      <small>{t("modals.weather.windSpeed")}</small>
                      <strong>{weather.wind_speed} km/h</strong>
                    </div>
                  </div>
                  <div className="weather-stat-item">
                    <Thermometer size={18} className="stat-icon orange" />
                    <div>
                      <small>{language === "hi" ? "महसूस तापमान" : language === "bn" ? "অনুভূত তাপমাত্রা" : "Feels Like"}</small>
                      <strong>{Math.round(weather.feels_like || weather.temperature)}°C</strong>
                    </div>
                  </div>
                  <div className="weather-stat-item">
                    <CloudSun size={18} className="stat-icon amber" />
                    <div>
                      <small>{language === "hi" ? "वर्षा" : language === "bn" ? "বৃষ্টিপাত" : "Precipitation"}</small>
                      <strong>{weather.precipitation || 0} mm</strong>
                    </div>
                  </div>
                </div>
              </div>

              {/* Farm Spraying & Field Advisories */}
              <div className="advisories-section">
                <h4>
                  <AlertCircle size={17} /> {t("modals.weather.advisories")}
                </h4>
                <div className="advisory-cards-list">
                  {weather.advisories?.map((item, idx) => (
                    <div key={idx} className="advisory-item-card">
                      <p>{item}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* 7-Day Forecast */}
              <div className="forecast-section">
                <h4>
                  <Calendar size={17} /> {t("modals.weather.forecast7Day")}
                </h4>
                <div className="forecast-scroll-strip">
                  {weather.forecast?.map((day, idx) => (
                    <div key={idx} className="forecast-day-card">
                      <span className="forecast-day-date">
                        {idx === 0 
                          ? (language === "hi" ? "आज" : language === "bn" ? "আজ" : "Today") 
                          : idx === 1 
                          ? (language === "hi" ? "कल" : language === "bn" ? "আগামীকাল" : "Tomorrow") 
                          : day.date.slice(5)}
                      </span>
                      <span className="forecast-icon">{day.icon || "🌤️"}</span>
                      <div className="forecast-temps">
                        <strong>{Math.round(day.max_temp)}°</strong>
                        <small>{Math.round(day.min_temp)}°</small>
                      </div>
                      <span className="rain-chance">
                        💧 {day.rain_chance || 0}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="error-banner">Could not retrieve live weather.</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default WeatherModal;
