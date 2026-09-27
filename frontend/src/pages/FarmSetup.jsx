import { useState } from "react";

import {
  Sprout,
  MapPin,
  Ruler,
  Droplets,
  ArrowLeft,
  ArrowRight,
} from "lucide-react";

function FarmSetup({ onBack, onSave }) {

  const [farmData, setFarmData] = useState({
    location: "",
    crop: "",
    area: "",
    soil: "",
    irrigation: "",
  });

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
      setError("Please complete all farm details.");
      return;
    }

    // Send data back to App
    onSave(farmData);
  };


  return (
    <div className="farm-setup-page">

      {/* HEADER */}

      <header className="setup-header">

        <button
          className="setup-back"
          onClick={onBack}
        >
          <ArrowLeft size={18} />
          Back to Dashboard
        </button>


        <div className="setup-brand">

          <div className="setup-logo">
            <Sprout size={23} />
          </div>

          <strong>KrishiSetu</strong>

        </div>

      </header>


      {/* MAIN */}

      <main className="setup-main">

        {/* TITLE */}

        <div className="setup-title">

          <span>
            🌾 FARM SETUP
          </span>

          <h1>
            Tell us about your farm
          </h1>

          <p>
            These details help KrishiSetu provide
            personalized farming recommendations.
          </p>

        </div>


        {/* FORM */}

        <form
          className="setup-form-card"
          onSubmit={handleSubmit}
        >

          {/* LOCATION */}

          <div className="form-group">

            <label>
              <MapPin size={17} />
              Farm Location
            </label>

            <input
              type="text"
              name="location"
              value={farmData.location}
              onChange={handleChange}
              placeholder="Enter your village, district or state"
            />

            <small>
              Example: Haldia, West Bengal
            </small>

          </div>


          {/* CROP */}

          <div className="form-group">

            <label>
              <Sprout size={17} />
              Main Crop
            </label>

            <select
              name="crop"
              value={farmData.crop}
              onChange={handleChange}
            >

              <option value="">
                Select your crop
              </option>

              <option value="Rice">
                Rice
              </option>

              <option value="Wheat">
                Wheat
              </option>

              <option value="Maize">
                Maize
              </option>

              <option value="Potato">
                Potato
              </option>

              <option value="Vegetables">
                Vegetables
              </option>

              <option value="Other">
                Other
              </option>

            </select>

          </div>


          {/* FARM AREA */}

          <div className="form-group">

            <label>
              <Ruler size={17} />
              Farm Area
            </label>

            <div className="input-with-unit">

              <input
                type="number"
                name="area"
                value={farmData.area}
                onChange={handleChange}
                placeholder="Enter farm area"
                min="0"
                step="0.01"
              />

              <span>
                acres
              </span>

            </div>

          </div>


          {/* SOIL */}

          <div className="form-group">

            <label>
              <Sprout size={17} />
              Soil Type
            </label>

            <select
              name="soil"
              value={farmData.soil}
              onChange={handleChange}
            >

              <option value="">
                Select soil type
              </option>

              <option value="Alluvial Soil">
                Alluvial Soil
              </option>

              <option value="Loamy Soil">
                Loamy Soil
              </option>

              <option value="Clay Soil">
                Clay Soil
              </option>

              <option value="Sandy Soil">
                Sandy Soil
              </option>

              <option value="Black Soil">
                Black Soil
              </option>

              <option value="Red Soil">
                Red Soil
              </option>

              <option value="Unknown">
                I don't know
              </option>

            </select>

          </div>


          {/* IRRIGATION */}

          <div className="form-group">

            <label>
              <Droplets size={17} />
              Irrigation Method
            </label>

            <select
              name="irrigation"
              value={farmData.irrigation}
              onChange={handleChange}
            >

              <option value="">
                Select irrigation method
              </option>

              <option value="Rainfed">
                Rainfed
              </option>

              <option value="Canal">
                Canal
              </option>

              <option value="Tube Well">
                Tube Well
              </option>

              <option value="Borewell">
                Borewell
              </option>

              <option value="Drip Irrigation">
                Drip Irrigation
              </option>

              <option value="Sprinkler">
                Sprinkler
              </option>

            </select>

          </div>


          {/* ERROR */}

          {error && (
            <div className="form-error">
              ⚠️ {error}
            </div>
          )}


          {/* SAVE */}

          <button
            type="submit"
            className="save-farm-btn"
          >

            Save Farm Details

            <ArrowRight size={19} />

          </button>

        </form>


        {/* INFORMATION */}

        <div className="setup-info">

          <span>🤖</span>

          <div>

            <strong>
              Why do we need this?
            </strong>

            <p>
              KrishiSetu uses your farm information
              together with weather, soil, satellite
              and AI data to generate localized
              agricultural guidance.
            </p>

          </div>

        </div>

      </main>

    </div>
  );
}

export default FarmSetup;