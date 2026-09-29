# 🌾 KrishiSetu-AI (कृषि सेतु)

> **Technology for smarter, sustainable farming.**
> AI-powered agricultural intelligence, real-time meteorology, satellite NDVI crop monitoring, and automated plant disease detection.

---

## 🌟 Key Features

1. **🤖 AI Farm Advisor Agent ("Ask KrishiSetu")**:
   - Conversational agronomist grounded in the farmer's registered crop, soil type, and location.
   - Built-in agricultural expert knowledge base for fertilizers (NPK doses), pests, and irrigation.
   - Integrated with Google Gemini API for advanced generative reasoning.
   - **Voice Input / Speech-to-Text**: Farmers can speak queries directly using the microphone button.

2. **🍃 AI Crop Disease Detection ("Check Crop")**:
   - Instant leaf photo analysis with radar scanning animation.
   - Diagnoses pathogens (fungal, bacterial, viral, nutrient deficiencies).
   - Generates actionable reports: Severity level, confidence rating, **organic remedies** (Neem oil, *Trichoderma*, bio-control), and **recommended chemical treatments**.
   - Includes one-click sample diseased/healthy leaves for instant testing.

3. **🌦️ Real-Time Agricultural Weather**:
   - Geocoded to the farmer's location using Open-Meteo (100% free, no API key needed).
   - Temperature, humidity, wind speed, and precipitation alerts.
   - Practical field advisories (e.g. spray windows, rain alerts, fungal disease risks).
   - 7-day agricultural forecast strip.

4. **🛰️ Satellite Field Monitoring (Sentinel-2 NDVI)**:
   - High-resolution multi-spectral vegetation indices.
   - Interactive 4-quadrant field sector map (inspect NDVI and crop stand by sector).
   - Canopy cover and root-zone moisture stress analytics.

5. **🌱 Crop Advisory & Growth Lifecycle**:
   - Stage-by-stage growth timeline (Sowing ➔ Tillering ➔ Flowering ➔ Harvesting).
   - Customized nutrient split applications and irrigation schedules.

6. **🌐 Multilingual Readiness**:
   - Instant language switching between **English**, **हिन्दी (Hindi)**, and **বাংলা (Bengali)**.

---

## 🏗️ System Architecture

```text
KrishiSetu-AI/
├── backend/
│   ├── config.py                 # Environment & configuration settings
│   ├── main.py                   # FastAPI application & REST endpoints
│   ├── requirements.txt          # Python dependencies
│   ├── services/
│   │   ├── ai_agent_service.py   # AI Agronomist Agent & Knowledge Base
│   │   ├── disease_service.py    # Leaf pathology diagnosis engine
│   │   ├── satellite_service.py  # Satellite NDVI analytics & zonal mapping
│   │   └── weather_service.py    # Open-Meteo live weather & spray advisories
├── frontend/
│   ├── src/
│   │   ├── components/           # Interactive Modals (Chat, Disease, Weather, Satellite, Advisory)
│   │   ├── pages/                # Dashboard.jsx & FarmSetup.jsx
│   │   ├── services/api.js       # Centralized Axios API client with fallbacks
│   │   ├── App.jsx               # Application controller & state machine
│   │   ├── App.css               # Nature-inspired agricultural design system
│   │   └── index.css             # Base styles & typography
```

---

## 🚀 Running the Application Locally

### 1. Start the Backend API Server
```bash
# In the project root:
.\venv\Scripts\python -m uvicorn main:app --host 127.0.0.1 --port 8000 --app-dir backend
```
*Backend runs at: `http://127.0.0.1:8000` (API docs at `http://127.0.0.1:8000/docs`)*

### 2. Start the Frontend Development Server
```bash
cd frontend
npm run dev
```
*Frontend runs at: `http://localhost:5173/`*

---

## 🔑 Configuration (Optional)
To enable Google Gemini Generative AI, copy `backend/.env.example` to `backend/.env` and add your key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Note: If no key is set, KrishiSetu AI runs smoothly using its built-in agronomic expert heuristics!)*
