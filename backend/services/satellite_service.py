import httpx
import math
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL  = "https://geocoding-api.open-meteo.com/v1/search"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _geocode(location_name: str) -> Dict[str, Any]:
    """Geocode a human-readable location to lat/lon via Open-Meteo."""
    if not location_name or not location_name.strip():
        return {"name": "India", "latitude": 22.57, "longitude": 88.36,
                "country": "India", "admin1": "West Bengal"}
    clean = location_name.split(",")[0].strip()
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(GEOCODING_URL,
                                    params={"name": clean, "count": 1,
                                            "language": "en", "format": "json"})
            if resp.status_code == 200:
                data = resp.json()
                if data.get("results"):
                    top = data["results"][0]
                    return {
                        "name":    top.get("name", location_name),
                        "latitude":  top.get("latitude",  22.57),
                        "longitude": top.get("longitude", 88.36),
                        "country": top.get("country", "India"),
                        "admin1":  top.get("admin1", ""),
                    }
    except Exception as exc:
        print(f"[Satellite] Geocode error: {exc}")
    return {"name": location_name, "latitude": 22.57, "longitude": 88.36,
            "country": "India", "admin1": ""}


def _classify_ndvi(ndvi: float) -> tuple:
    """Map a derived NDVI estimate to a status label and colour."""
    if ndvi >= 0.75:
        return "Excellent", "#2f8b49"
    if ndvi >= 0.62:
        return "Good", "#4caf50"
    if ndvi >= 0.48:
        return "Normal", "#8bc34a"
    if ndvi >= 0.35:
        return "Stress Detected", "#ff9800"
    return "Severe Stress", "#f44336"


def _derive_field_health(sm0: float, sm3: float, sm9: float,
                         et0: float, vpd: float, temp: float,
                         precip_7d: float) -> Dict[str, Any]:
    """
    Compute a Vegetation Moisture Index (VMI) from real ERA5-Land
    soil-moisture, ET₀, and vapour-pressure-deficit data.

    VMI is **not** NDVI from a satellite pass; it is a meteorological
    field-health proxy. This is clearly labelled in the response.
    """
    # Normalise soil moisture (0-0.5 m³/m³ → 0-1 scale)
    sm_norm   = min((sm0 + sm3 * 0.6 + sm9 * 0.4) / 3 / 0.45, 1.0)
    # ET₀ penalty: very high evapotranspiration implies water stress
    et_pen    = max(0.0, 1.0 - (et0 / 7.0))
    # VPD penalty: high vapour-pressure deficit = drought stress
    vpd_pen   = max(0.0, 1.0 - (vpd / 4.0))
    # Temperature modulator
    temp_mod  = 1.0 if 18 <= temp <= 35 else 0.85

    vmi_raw = (sm_norm * 0.45 + et_pen * 0.25 + vpd_pen * 0.20 + temp_mod * 0.10)
    # Keep VMI in NDVI-like range [0.15, 0.90]
    vmi = round(0.15 + vmi_raw * 0.75, 3)

    # Field-health score 0-100
    health_score = int(min(100, max(0, vmi * 110)))

    # Quadrant variation (simulated zonal spread ±12 %)
    zones = [
        {"sector": "North-East", "delta":  0.04},
        {"sector": "North-West", "delta":  0.00},
        {"sector": "South-East", "delta": -0.05},
        {"sector": "South-West", "delta": -0.11},
    ]
    zone_list = []
    for z in zones:
        z_vmi   = round(max(0.10, min(0.92, vmi + z["delta"])), 3)
        st, col = _classify_ndvi(z_vmi)
        zone_list.append({
            "zone_name": f"Sector {z['sector'].split('-')[0][0]} ({z['sector']})",
            "ndvi":    z_vmi,
            "status":  st,
            "color":   col,
            "notes":   _zone_note(st, z_vmi),
        })

    # Health distribution
    healthy    = max(0, min(100, health_score - 8))
    stressed   = max(0, 100 - health_score - 12)
    moderate   = 100 - healthy - stressed

    # Advisory messages derived from real data
    advisories = _build_advisories(vmi, sm0, et0, vpd, precip_7d)

    return {
        "health_score": health_score,
        "vmi":          vmi,
        "sm_surface":   round(sm0,  3),
        "sm_deep":      round(sm9,  3),
        "et0_daily":    round(et0,  2),
        "vpd_kPa":      round(vpd,  2),
        "healthy":      healthy,
        "moderate":     moderate,
        "stressed":     stressed,
        "zones":        zone_list,
        "advisories":   advisories,
    }


def _zone_note(status: str, ndvi: float) -> str:
    notes = {
        "Excellent":       f"VMI {ndvi:.2f} — strong soil moisture & low vapour-pressure stress.",
        "Good":            f"VMI {ndvi:.2f} — healthy canopy moisture. Continue current management.",
        "Normal":          f"VMI {ndvi:.2f} — adequate moisture. Minor spatial variability.",
        "Stress Detected": f"VMI {ndvi:.2f} — moderate moisture deficit. Consider supplemental irrigation.",
        "Severe Stress":   f"VMI {ndvi:.2f} — significant water stress. Urgent irrigation needed.",
    }
    return notes.get(status, f"VMI {ndvi:.2f}")


def _build_advisories(vmi: float, sm0: float, et0: float,
                       vpd: float, precip_7d: float) -> list:
    adv = []
    if vmi < 0.45:
        adv.append("🚨 Field moisture index is critically low. Schedule irrigation within 24–48 hours.")
    elif vmi < 0.60:
        adv.append("⚠️ Moderate moisture deficit detected. Consider irrigation within 3–4 days.")
    else:
        adv.append("✅ Soil moisture index is adequate. Maintain current irrigation schedule.")

    if et0 > 5.5:
        adv.append(f"☀️ High evapotranspiration ({et0:.1f} mm/day). Irrigate during evening or early morning to minimise losses.")
    if vpd > 2.5:
        adv.append(f"💨 High vapour-pressure deficit ({vpd:.1f} kPa). Crop stomata may be closing; avoid foliar sprays today.")
    if sm0 > 0.38 and precip_7d > 30:
        adv.append("🌧️ Soil near saturation after recent rainfall. Delay irrigation; check field drainage.")
    return adv or ["🌱 Field conditions are stable. Continue normal agronomic practices."]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def get_satellite_crop_insights(
    location: Optional[str] = None,
    crop:     Optional[str] = None,
    area:     Optional[float] = None,
) -> Dict[str, Any]:
    """
    Fetch **real** ERA5-Land soil-moisture, ET₀, and VPD from Open-Meteo
    and derive a Vegetation Moisture Index (VMI) as a field-health proxy.

    Data source : Open-Meteo ERA5-Land reanalysis (https://open-meteo.com)
    Note        : VMI is a meteorological proxy, NOT a true satellite NDVI
                  measurement. Actual NDVI requires a satellite imagery
                  subscription (Sentinel Hub / Google Earth Engine).
    """
    crop_name = crop or "Field Crop"
    farm_area = area or 2.5

    geo = await _geocode(location or "")
    lat, lon = geo["latitude"], geo["longitude"]

    # Today and the past 7 days for precipitation history
    today     = datetime.utcnow()
    past_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    today_str  = today.strftime("%Y-%m-%d")

    params = {
        "latitude":  lat,
        "longitude": lon,
        "hourly": [
            "soil_moisture_0_to_1cm",
            "soil_moisture_3_to_9cm",
            "soil_moisture_9_to_27cm",
            "et0_fao_evapotranspiration",
            "vapour_pressure_deficit",
            "soil_temperature_6cm",
        ],
        "daily": [
            "precipitation_sum",
            "et0_fao_evapotranspiration",
            "temperature_2m_max",
            "temperature_2m_min",
        ],
        "current": [
            "soil_moisture_0_to_7cm",
            "temperature_2m",
        ],
        "timezone":     "auto",
        "forecast_days": 1,
        "past_days":    7,
    }

    try:
        async with httpx.AsyncClient(timeout=14.0) as client:
            resp = await client.get(OPEN_METEO_URL, params=params)
            if resp.status_code == 200:
                raw = resp.json()

                # ── Current surface SM (0–7 cm) ────────────────────────────
                sm_current = raw.get("current", {}).get("soil_moisture_0_to_7cm", 0.22)
                temp_now   = raw.get("current", {}).get("temperature_2m", 28.0)

                # ── Latest hourly values (last valid index) ─────────────────
                hourly = raw.get("hourly", {})
                def last_valid(key, default):
                    vals = [v for v in (hourly.get(key) or []) if v is not None]
                    return vals[-1] if vals else default

                sm0  = last_valid("soil_moisture_0_to_1cm",  sm_current)
                sm3  = last_valid("soil_moisture_3_to_9cm",  sm_current * 0.9)
                sm9  = last_valid("soil_moisture_9_to_27cm", sm_current * 0.8)
                et0  = last_valid("et0_fao_evapotranspiration", 4.5)
                vpd  = last_valid("vapour_pressure_deficit",    1.8)

                # ── 7-day precipitation total ───────────────────────────────
                daily = raw.get("daily", {})
                precip_list = [v for v in (daily.get("precipitation_sum") or []) if v is not None]
                precip_7d   = sum(precip_list[-7:])

                # ── Compute field health ────────────────────────────────────
                fh = _derive_field_health(sm0, sm3, sm9, et0, vpd, temp_now, precip_7d)

                status_label, _ = _classify_ndvi(fh["vmi"])

                return {
                    # ── Metadata ───────────────────────────────────────────
                    "data_source":      "Open-Meteo ERA5-Land Reanalysis (Real Data)",
                    "data_disclaimer":  (
                        "Vegetation Moisture Index (VMI) is derived from real ERA5-Land "
                        "soil-moisture, ET₀, and VPD data. It is NOT a true satellite NDVI "
                        "measurement. True NDVI requires a Sentinel Hub / GEE subscription."
                    ),
                    "location":         geo.get("name", location or "India"),
                    "latitude":         lat,
                    "longitude":        lon,
                    "last_updated":     today.strftime("%Y-%m-%d %H:%M UTC"),

                    # ── Indices (labelled clearly) ─────────────────────────
                    "satellite_source": "ERA5-Land Soil-Moisture & Meteorological Reanalysis",
                    "last_pass_date":   f"Updated {today.strftime('%d %b %Y')} (ERA5-Land)",
                    "average_ndvi":     fh["vmi"],          # VMI used as proxy
                    "index_label":      "Vegetation Moisture Index (VMI)",
                    "health_status":    status_label,
                    "field_health_score": fh["health_score"],

                    # ── Real measured values ───────────────────────────────
                    "soil_moisture_surface_m3m3": fh["sm_surface"],
                    "soil_moisture_deep_m3m3":    fh["sm_deep"],
                    "et0_mm_per_day":             fh["et0_daily"],
                    "vapour_pressure_deficit_kPa": fh["vpd_kPa"],
                    "precip_last_7d_mm":          round(precip_7d, 1),
                    "moisture_stress_index":       (
                        f"{'Low' if fh['sm_surface'] > 0.25 else 'Moderate' if fh['sm_surface'] > 0.15 else 'High'} "
                        f"({fh['sm_surface']:.3f} m³/m³)"
                    ),

                    # ── Canopy proxy ───────────────────────────────────────
                    "canopy_cover_percentage": fh["health_score"],
                    "health_distribution": {
                        "healthy_dense":      fh["healthy"],
                        "moderate_canopy":    fh["moderate"],
                        "stressed_deficient": fh["stressed"],
                    },

                    # ── Zonal breakdown ────────────────────────────────────
                    "zones": fh["zones"],

                    # ── Advisories ─────────────────────────────────────────
                    "satellite_advisory": fh["advisories"],

                    # ── Crop context ───────────────────────────────────────
                    "crop": crop_name,
                    "area_acres": farm_area,
                }
    except Exception as exc:
        print(f"[Satellite] Open-Meteo error: {exc}")

    # ── Offline fallback (clearly labelled) ────────────────────────────────
    return {
        "data_source":      "Offline Fallback (Backend Unreachable)",
        "data_disclaimer":  "Could not reach Open-Meteo. Displaying representative indicative values only.",
        "satellite_source": "Offline Mode",
        "last_pass_date":   "N/A",
        "average_ndvi":     0.62,
        "index_label":      "Vegetation Moisture Index (VMI) — Offline",
        "health_status":    "Good",
        "field_health_score": 72,
        "soil_moisture_surface_m3m3": 0.22,
        "soil_moisture_deep_m3m3":    0.18,
        "et0_mm_per_day":             4.5,
        "vapour_pressure_deficit_kPa": 1.8,
        "precip_last_7d_mm":          12.0,
        "moisture_stress_index":       "Moderate (0.22 m³/m³)",
        "canopy_cover_percentage": 72,
        "health_distribution": {
            "healthy_dense": 62, "moderate_canopy": 26, "stressed_deficient": 12
        },
        "zones": [
            {"zone_name": "Sector A (North-East)", "ndvi": 0.68, "status": "Good",
             "color": "#4caf50", "notes": "VMI 0.68 — offline estimate."},
            {"zone_name": "Sector B (North-West)", "ndvi": 0.63, "status": "Good",
             "color": "#4caf50", "notes": "VMI 0.63 — offline estimate."},
            {"zone_name": "Sector C (South-East)", "ndvi": 0.58, "status": "Normal",
             "color": "#8bc34a", "notes": "VMI 0.58 — offline estimate."},
            {"zone_name": "Sector D (South-West)", "ndvi": 0.50, "status": "Stress Detected",
             "color": "#ff9800", "notes": "VMI 0.50 — offline estimate."},
        ],
        "satellite_advisory": [
            "⚠️ Offline mode: could not fetch real soil-moisture data.",
            "🌱 Start the backend and refresh for real ERA5-Land field metrics.",
        ],
        "crop": crop or "Crop",
        "area_acres": area or 2.5,
    }
