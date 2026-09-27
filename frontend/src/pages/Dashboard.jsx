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
} from "lucide-react";

function Dashboard({ onSetupFarm, farmData }) {
  return (
    <div className="dashboard">

      {/* ================= HEADER ================= */}

      <header className="dashboard-header">

        <div className="dashboard-brand">

          <div className="dashboard-logo">
            <Sprout size={25} />
          </div>

          <div>
            <h2>KrishiSetu</h2>
            <span>AI for smarter farming</span>
          </div>

        </div>

        <div className="farmer-profile">

          <div className="profile-avatar">
            F
          </div>

          <div>
            <strong>Farmer</strong>
            <small>My Farm</small>
          </div>

        </div>

      </header>


      {/* ================= MAIN ================= */}

      <main className="dashboard-main">


        {/* ================= WELCOME ================= */}

        <section className="dashboard-welcome">

          <div className="welcome-text">

            <span className="dashboard-label">
              🌾 FARMER DASHBOARD
            </span>

            <h1>
              Good morning, Farmer 👋
            </h1>

            <p>
              Get simple, AI-powered insights to make
              better decisions for your farm.
            </p>

          </div>


          {/* FARM LOCATION */}

          <div className="location-box">

            <MapPin size={21} />

            <div>

              <small>
                Farm Location
              </small>

              <strong>
                {farmData
                  ? farmData.location
                  : "Not set yet"}
              </strong>

            </div>

          </div>

        </section>



        {/* ================= FARM SETUP / FARM INFORMATION ================= */}

        <section className="farm-setup">


          <div className="setup-icon">
            <MapPin size={27} />
          </div>


          <div className="setup-content">


            {farmData ? (

              <>
                <span>
                  YOUR FARM
                </span>

                <h3>
                  {farmData.crop} Farm
                </h3>

                <p>
                  📍 {farmData.location}
                  &nbsp; • &nbsp;
                  🌱 {farmData.area} acres
                </p>


                <div className="farm-details-row">

                  <span>
                    Soil:{" "}
                    <strong>
                      {farmData.soil}
                    </strong>
                  </span>

                  <span>
                    Irrigation:{" "}
                    <strong>
                      {farmData.irrigation}
                    </strong>
                  </span>

                </div>

              </>

            ) : (

              <>

                <span>
                  GET STARTED
                </span>

                <h3>
                  Set up your farm
                </h3>

                <p>
                  Add your farm location and crop details
                  to receive personalized recommendations.
                </p>

              </>

            )}

          </div>


          {/* SETUP / EDIT BUTTON */}

          <button
            className="setup-btn"
            onClick={onSetupFarm}
          >

            {farmData
              ? "Edit Farm"
              : "Set Up Farm"}

            <ArrowRight size={18} />

          </button>

        </section>



        {/* ================= FARM INSIGHTS ================= */}

        <section className="dashboard-section">

          <div className="section-heading">

            <div>

              <span className="section-label">
                FARM DATA
              </span>

              <h2>
                Farm Insights
              </h2>

              <p>
                Important information for your farm
              </p>

            </div>

          </div>



          <div className="insight-grid">


            {/* ================= WEATHER ================= */}

            <div className="insight-card">

              <div className="insight-icon weather">
                <CloudSun size={26} />
              </div>

              <div className="insight-info">

                <span>
                  Weather
                </span>

                <strong>
                  {farmData
                    ? "Ready for weather data"
                    : "Waiting for location"}
                </strong>

                <small>
                  {farmData
                    ? `Weather for ${farmData.location}`
                    : "Weather data will appear here"}
                </small>

              </div>

              <ArrowRight
                className="card-arrow"
                size={18}
              />

            </div>



            {/* ================= SOIL ================= */}

            <div className="insight-card">

              <div className="insight-icon soil">
                <Droplets size={26} />
              </div>

              <div className="insight-info">

                <span>
                  Soil Health
                </span>

                <strong>
                  {farmData
                    ? farmData.soil
                    : "Not available"}
                </strong>

                <small>
                  {farmData
                    ? "Farm soil information"
                    : "Add your soil information"}
                </small>

              </div>

              <ArrowRight
                className="card-arrow"
                size={18}
              />

            </div>



            {/* ================= SATELLITE ================= */}

            <div className="insight-card">

              <div className="insight-icon satellite">
                <Satellite size={26} />
              </div>

              <div className="insight-info">

                <span>
                  Satellite
                </span>

                <strong>
                  {farmData
                    ? "Farm ready"
                    : "Waiting for farm"}
                </strong>

                <small>
                  {farmData
                    ? `Monitoring ${farmData.crop} fields`
                    : "Crop monitoring will appear here"}
                </small>

              </div>

              <ArrowRight
                className="card-arrow"
                size={18}
              />

            </div>


          </div>

        </section>



        {/* ================= AI ADVISOR ================= */}

        <section className="ai-advisor">


          <div className="ai-icon">
            <Bot size={31} />
          </div>


          <div className="ai-content">

            <span>
              AI FARM ADVISOR
            </span>

            <h2>
              Ask KrishiSetu
            </h2>

            <p>
              Get guidance about crops, diseases,
              weather, soil and farming practices.
            </p>

          </div>


          <button className="ai-button">

            Ask AI

            <ArrowRight size={18} />

          </button>


        </section>



        {/* ================= SMART FARMING TOOLS ================= */}

        <section className="dashboard-section">


          <div className="section-heading">

            <div>

              <span className="section-label">
                FARMING TOOLS
              </span>

              <h2>
                Smart Farming Tools
              </h2>

              <p>
                Tools designed to support your farming decisions
              </p>

            </div>

          </div>



          <div className="tools-grid">


            {/* ================= CROP ADVISORY ================= */}

            <div className="tool-card">

              <div className="tool-icon">
                <Leaf size={25} />
              </div>

              <h3>
                Crop Advisory
              </h3>

              <p>
                Get crop recommendations based on
                soil, weather and farm conditions.
              </p>

              <button>

                Explore

                <ArrowRight size={16} />

              </button>

            </div>



            {/* ================= DISEASE DETECTION ================= */}

            <div className="tool-card">

              <div className="tool-icon">
                <ShieldCheck size={25} />
              </div>

              <h3>
                Disease Detection
              </h3>

              <p>
                Upload a crop image and use AI to
                identify possible crop diseases.
              </p>

              <button>

                Check Crop

                <ArrowRight size={16} />

              </button>

            </div>



            {/* ================= SATELLITE ================= */}

            <div className="tool-card">

              <div className="tool-icon">
                <Satellite size={25} />
              </div>

              <h3>
                Satellite Monitoring
              </h3>

              <p>
                Monitor crop health and changes
                using satellite-based insights.
              </p>

              <button>

                View Farm

                <ArrowRight size={16} />

              </button>

            </div>



            {/* ================= AI ASSISTANT ================= */}

            <div className="tool-card">

              <div className="tool-icon">
                <Bot size={25} />
              </div>

              <h3>
                AI Farm Assistant
              </h3>

              <p>
                Ask questions and receive simple
                farming guidance from AI.
              </p>

              <button>

                Talk to AI

                <ArrowRight size={16} />

              </button>

            </div>


          </div>

        </section>



        {/* ================= FOOTER ================= */}

        <footer className="dashboard-footer">

          <span>
            🌾 KrishiSetu AI
          </span>

          <span>
            Technology for smarter, sustainable farming
          </span>

        </footer>


      </main>

    </div>
  );
}

export default Dashboard;