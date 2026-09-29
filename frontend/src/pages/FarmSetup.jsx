import { useState } from "react";
import {
  Sprout,
  MapPin,
  Ruler,
  Droplets,
  ArrowLeft,
  ArrowRight,
} from "lucide-react";
import { useLanguage } from "../context/LanguageContext";
import LanguageSelector from "../components/LanguageSelector";

function FarmSetup({ onBack, onSave, initialData }) {
  const { t } = useLanguage();

  const [farmData, setFarmData] = useState(
    initialData || {
      location: "",
      crop: "",
      area: "",
      soil: "",
      irrigation: "",
    }
  );

  const [error, setError] = useState("");

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFarmData((previousData) => ({
      ...previousData,
      [name]: value,
    }));
    setError("");
  };

  // Save farm details
  const handleSubmit = (e) => {
    e.preventDefault();

    // Check required fields
    if (
      !farmData.location ||
      !farmData.crop ||
      !farmData.area ||
      !farmData.soil ||
      !farmData.irrigation
    ) {
      setError(t("farmSetup.errorRequired"));
      return;
    }

    // Send data back to App
    onSave(farmData);
  };

  return (
    <div className="farm-setup-page">
      {/* HEADER */}
      <header className="setup-header">
        <button className="setup-back" onClick={onBack}>
          <ArrowLeft size={18} />
          {t("farmSetup.backToDashboard")}
        </button>

        <div
          className="setup-header-center clickable"
          onClick={() => {
            window.scrollTo({ top: 0, behavior: "smooth" });
            onBack();
          }}
          role="button"
          tabIndex={0}
          title="Return to starting page"
        >
          <div className="setup-brand">
            <div className="setup-logo">
              <Sprout size={23} className="brand-sprout-icon" />
            </div>
            <strong>
              Krishi<span className="brand-highlight">Setu</span>
            </strong>
          </div>
        </div>

        <div className="setup-header-right">
          <LanguageSelector variant="compact" />
        </div>
      </header>

      {/* MAIN */}
      <main className="setup-main">
        {/* TITLE */}
        <div className="setup-title">
          <span>{t("farmSetup.badge")}</span>
          <h1>{t("farmSetup.title")}</h1>
          <p>{t("farmSetup.subtitle")}</p>
        </div>

        {/* FORM */}
        <form className="setup-form-card" onSubmit={handleSubmit}>
          {/* LOCATION */}
          <div className="form-group">
            <label>
              <MapPin size={17} />
              {t("farmSetup.locationLabel")}
            </label>
            <input
              type="text"
              name="location"
              value={farmData.location}
              onChange={handleChange}
              placeholder={t("farmSetup.locationPlaceholder")}
            />
            <small>{t("farmSetup.locationExample")}</small>
          </div>

          {/* MAIN CROP */}
          <div className="form-group">
            <label>
              <Sprout size={17} />
              {t("farmSetup.cropLabel")}
            </label>
            <select name="crop" value={farmData.crop} onChange={handleChange}>
              <option value="">{t("farmSetup.cropPlaceholder")}</option>
              <option value="Rice">{t("crops.Rice")}</option>
              <option value="Wheat">{t("crops.Wheat")}</option>
              <option value="Maize">{t("crops.Maize")}</option>
              <option value="Potato">{t("crops.Potato")}</option>
              <option value="Vegetables">{t("crops.Vegetables")}</option>
              <option value="Mustard">{t("crops.Mustard")}</option>
              <option value="Cotton">{t("crops.Cotton")}</option>
              <option value="Chilli">{t("crops.Chilli")}</option>
              <option value="Other">{t("crops.Other")}</option>
            </select>
          </div>

          {/* FARM AREA */}
          <div className="form-group">
            <label>
              <Ruler size={17} />
              {t("farmSetup.areaLabel")}
            </label>
            <div className="input-with-unit">
              <input
                type="number"
                name="area"
                value={farmData.area}
                onChange={handleChange}
                placeholder={t("farmSetup.areaPlaceholder")}
                min="0"
                step="0.01"
              />
              <span>{t("common.acres")}</span>
            </div>
          </div>

          {/* SOIL */}
          <div className="form-group">
            <label>
              <Sprout size={17} />
              {t("farmSetup.soilLabel")}
            </label>
            <select name="soil" value={farmData.soil} onChange={handleChange}>
              <option value="">{t("farmSetup.soilPlaceholder")}</option>
              <option value="Alluvial Soil">{t("soils.Alluvial Soil")}</option>
              <option value="Loamy Soil">{t("soils.Loamy Soil")}</option>
              <option value="Clay Soil">{t("soils.Clay Soil")}</option>
              <option value="Sandy Soil">{t("soils.Sandy Soil")}</option>
              <option value="Black Soil">{t("soils.Black Soil")}</option>
              <option value="Red Soil">{t("soils.Red Soil")}</option>
              <option value="Unknown">{t("soils.Unknown")}</option>
            </select>
          </div>

          {/* IRRIGATION */}
          <div className="form-group">
            <label>
              <Droplets size={17} />
              {t("farmSetup.irrigationLabel")}
            </label>
            <select
              name="irrigation"
              value={farmData.irrigation}
              onChange={handleChange}
            >
              <option value="">{t("farmSetup.irrigationPlaceholder")}</option>
              <option value="Rainfed">{t("irrigation.Rainfed")}</option>
              <option value="Canal">{t("irrigation.Canal")}</option>
              <option value="Tube Well">{t("irrigation.Tube Well")}</option>
              <option value="Borewell">{t("irrigation.Borewell")}</option>
              <option value="Drip Irrigation">{t("irrigation.Drip Irrigation")}</option>
              <option value="Sprinkler">{t("irrigation.Sprinkler")}</option>
            </select>
          </div>

          {/* ERROR MESSAGE */}
          {error && <p className="form-error">{error}</p>}

          {/* SUBMIT BUTTON */}
          <button type="submit" className="primary-btn setup-submit-btn">
            {t("farmSetup.saveBtn")}
            <ArrowRight size={19} />
          </button>
        </form>
      </main>
    </div>
  );
}

export default FarmSetup;