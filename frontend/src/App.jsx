import { useState } from "react";
import {
  Sprout,
  Satellite,
  CloudSun,
  Bot,
  ArrowRight,
  Globe,
  ChevronDown,
} from "lucide-react";

import Dashboard from "./pages/Dashboard";
import FarmSetup from "./pages/FarmSetup";

import "./index.css";
import "./App.css";

function App() {
  const [showLogin, setShowLogin] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false);
  const [showFarmSetup, setShowFarmSetup] = useState(false);
  const [farmData, setFarmData] = useState(null);


  // =========================
  // DASHBOARD
  // =========================
  if (showFarmSetup) {
  return (
    <FarmSetup
      onBack={() => setShowFarmSetup(false)}
    />
  );
}

if (showFarmSetup) {
  return (
    <FarmSetup
      onBack={() => setShowFarmSetup(false)}
      onSave={(data) => {
        setFarmData(data);
        setShowFarmSetup(false);
        setShowDashboard(true);
      }}
    />
  );
}

  // =========================
  // LOGIN
  // =========================
  if (showLogin) {
    return (
      <div className="login-page">
        <div className="login-card">
          <div className="logo-circle">
            <Sprout size={34} />
          </div>

          <h1>Welcome to KrishiSetu</h1>

          <p className="subtitle">
            Your AI-powered farming companion.
          </p>

          <input
            type="email"
            placeholder="Email address"
          />

          <input
            type="password"
            placeholder="Password"
          />

          <button
            className="primary-btn login-btn"
            onClick={() => setShowDashboard(true)}
          >
            Login
            <ArrowRight size={20} />
          </button>

          <button
            className="back-btn"
            onClick={() => setShowLogin(false)}
          >
            ← Back to Welcome
          </button>
        </div>
      </div>
    );
  }

  // =========================
  // LANDING PAGE
  // =========================
  return (
    <div className="app">

      {/* ================= HEADER ================= */}
      <header className="topbar">

        <div className="brand">
          <div className="brand-icon">
            <Sprout size={28} />
          </div>

          <span>KrishiSetu</span>
        </div>

        <button className="language-btn">
          <Globe size={19} />
          <span>English</span>
          <ChevronDown size={17} />
        </button>

      </header>


      {/* ================= HERO ================= */}
      <main className="hero">

        {/* Background overlay */}
        <div className="hero-overlay"></div>

        {/* LEFT CONTENT */}
        <section className="hero-content">

          <div className="welcome-badge">
            🌾
            <span>Smart farming made simple</span>
          </div>

          <h1>
            Smarter farming.
            <br />
            <span>Better decisions.</span>
          </h1>

          <p>
            KrishiSetu connects farmers with AI-powered
            agricultural guidance using weather, soil,
            satellite insights and crop information.
          </p>


          {/* BUTTONS */}
          <div className="hero-buttons">

            <button
              className="primary-btn"
              onClick={() => setShowDashboard(true)}
            >
              Get Started
              <ArrowRight size={21} />
            </button>

            <button
              className="secondary-btn"
              onClick={() => setShowLogin(true)}
            >
              I already have an account
            </button>

          </div>


          {/* FEATURES */}
          <div className="feature-row">

            <div className="feature-item">
              <Satellite size={24} />
              <span>Satellite Insights</span>
            </div>

            <div className="feature-divider"></div>

            <div className="feature-item">
              <CloudSun size={24} />
              <span>Weather Guidance</span>
            </div>

            <div className="feature-divider"></div>

            <div className="feature-item">
              <Bot size={24} />
              <span>AI Assistance</span>
            </div>

          </div>

        </section>


        {/* ================= FARM CARD ================= */}
        <section className="hero-visual">

          <div className="farm-card">

            {/* Farm icon */}
            <div className="farm-icon">
              🌾
            </div>

            <h2>Your Farm</h2>

            <p>
              Personalized insights for your crops and farm.
            </p>


            {/* WEATHER */}
            <div className="farm-feature">

              <div className="farm-feature-icon">
                🌦️
              </div>

              <div className="farm-feature-text">
                <strong>Weather</strong>
                <span>Live updates</span>
              </div>

              <ArrowRight size={21} />

            </div>


            {/* SATELLITE */}
            <div className="farm-feature">

              <div className="farm-feature-icon">
                🛰️
              </div>

              <div className="farm-feature-text">
                <strong>Satellite</strong>
                <span>Crop insights</span>
              </div>

              <ArrowRight size={21} />

            </div>


            {/* SOIL */}
            <div className="farm-feature">

              <div className="farm-feature-icon">
                🌱
              </div>

              <div className="farm-feature-text">
                <strong>Soil</strong>
                <span>Health data</span>
              </div>

              <ArrowRight size={21} />

            </div>

          </div>

        </section>

      </main>


      {/* ================= FOOTER ================= */}
      <footer>

        <span>
          🌾 KrishiSetu AI
        </span>

        <span>
          Technology for smarter, sustainable farming
        </span>

      </footer>

    </div>
  );
}

export default App;