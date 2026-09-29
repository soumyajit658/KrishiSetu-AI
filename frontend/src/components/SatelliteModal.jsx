import { useState, useEffect } from "react";
import {
  Satellite,
  Activity,
  Layers,
  CheckCircle2,
  AlertTriangle,
  X,
  RefreshCw,
  Eye,
  Info,
  Droplets,
  Thermometer,
  Wind,
  AlertCircle,
} from "lucide-react";
import { api } from "../services/api";
import { useLanguage } from "../context/LanguageContext";

function SatelliteModal({ isOpen, onClose, farmData }) {
  const { t, translateCrop } = useLanguage();
  const [data, setData]           = useState(null);
  const [loading, setLoading]     = useState(false);
  const [selectedZone, setSelectedZone] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchSatellite();
    }
  }, [isOpen, farmData?.location, farmData?.crop]);

  const fetchSatellite = async () => {
    setLoading(true);
    try {
      const res = await api.getSatelliteData(
        farmData?.location,
        farmData?.crop,
        farmData?.area
      );
      setData(res);
      if (res?.zones?.length > 0) {
        setSelectedZone(res.zones[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  // Determine health score colour
  const scoreColor = (score) => {
    if (score >= 75) return "#2f8b49";
    if (score >= 55) return "#8bc34a";
    if (score >= 40) return "#ff9800";
    return "#f44336";
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container satellite-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="modal-header-brand">
            <div className="modal-icon-badge satellite">
              <Satellite size={22} />
            </div>
            <div>
              <h3>{t("modals.satellite.title")}</h3>
              <p className="modal-subtext">
                {t("modals.satellite.subtext")} •{" "}
                {translateCrop(farmData?.crop) || farmData?.crop || "Farm"} ({farmData?.area || 2}{" "}
                {t("common.acres")})
              </p>
            </div>
          </div>
          <div className="modal-header-actions">
            <button className="refresh-btn" onClick={fetchSatellite} disabled={loading} title="Refresh data">
              <RefreshCw size={16} className={loading ? "spinning" : ""} />
            </button>
            <button className="close-btn" onClick={onClose}>
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="modal-body">
          {loading && !data ? (
            <div className="loading-state">
              <RefreshCw size={24} className="spinning" />
              <span>{t("modals.satellite.calibrating")}</span>
            </div>
          ) : data ? (
            <>
              {/* Data source banner */}
              {data.data_disclaimer && (
                <div className="sat-data-source-banner">
                  <Info size={13} />
                  <span>
                    <strong>Data:</strong> {data.satellite_source || "ERA5-Land Reanalysis"} •{" "}
                    {data.last_pass_date || "Real-time"}
                  </span>
                </div>
              )}

              {/* ── Field Health Score ── */}
              {data.field_health_score !== undefined && (
                <div className="sat-health-score-row">
                  <div className="sat-health-score-circle"
                    style={{ borderColor: scoreColor(data.field_health_score) }}>
                    <strong style={{ color: scoreColor(data.field_health_score) }}>
                      {data.field_health_score}
                    </strong>
                    <small>/100</small>
                  </div>
                  <div>
                    <div className="sat-health-label">Field Health Score</div>
                    <div className="sat-health-status"
                      style={{ color: scoreColor(data.field_health_score) }}>
                      {data.health_status}
                    </div>
                    <small className="sat-index-label">
                      {data.index_label || "Vegetation Moisture Index (VMI)"}
                    </small>
                  </div>
                </div>
              )}

              {/* Top Metrics Row */}
              <div className="satellite-metrics-strip">
                <div className="sat-metric-box primary">
                  <span className="sat-label">
                    {data.index_label ? "VMI Score" : t("modals.satellite.avgNdvi")}
                  </span>
                  <div className="sat-val-row">
                    <strong className="sat-val">{data.average_ndvi}</strong>
                    <span className="sat-status-badge good">{data.health_status}</span>
                  </div>
                  <small>
                    {data.index_label || "Vegetation index"} • scale 0.0–1.0
                  </small>
                </div>

                {/* Soil Moisture */}
                {data.soil_moisture_surface_m3m3 !== undefined ? (
                  <div className="sat-metric-box">
                    <span className="sat-label">
                      <Droplets size={13} /> Surface Soil Moisture
                    </span>
                    <div className="sat-val-row">
                      <strong className="sat-val">
                        {(data.soil_moisture_surface_m3m3 * 100).toFixed(1)}%
                      </strong>
                    </div>
                    <small>{data.moisture_stress_index}</small>
                  </div>
                ) : (
                  <div className="sat-metric-box">
                    <span className="sat-label">{t("modals.satellite.canopyCover")}</span>
                    <div className="sat-val-row">
                      <strong className="sat-val">{data.canopy_cover_percentage}%</strong>
                    </div>
                    <small>{t("modals.satellite.canopyDesc")}</small>
                  </div>
                )}

                {/* ET0 or Moisture Stress */}
                {data.et0_mm_per_day !== undefined ? (
                  <div className="sat-metric-box">
                    <span className="sat-label">
                      <Wind size={13} /> ET₀ (Evapotranspiration)
                    </span>
                    <div className="sat-val-row">
                      <strong className="sat-val">{data.et0_mm_per_day} mm/day</strong>
                    </div>
                    <small>
                      VPD: {data.vapour_pressure_deficit_kPa} kPa •{" "}
                      Rain 7d: {data.precip_last_7d_mm} mm
                    </small>
                  </div>
                ) : (
                  <div className="sat-metric-box">
                    <span className="sat-label">{t("modals.satellite.moistureStress")}</span>
                    <div className="sat-val-row">
                      <strong className="sat-val">{t("modals.satellite.adequate")}</strong>
                    </div>
                    <small>{t("modals.satellite.moistureDesc")}</small>
                  </div>
                )}
              </div>

              {/* Visual Field Grid & Sector Inspector */}
              <div className="field-map-section">
                <div className="field-visual-col">
                  <h4>
                    <Layers size={17} /> {t("modals.satellite.sectorMap")}
                  </h4>
                  <div className="field-grid-visual">
                    {data.zones?.map((zone, idx) => (
                      <div
                        key={idx}
                        className={`field-sector-quadrant ${
                          selectedZone?.zone_name === zone.zone_name ? "active" : ""
                        }`}
                        style={{
                          backgroundColor: `${zone.color}22`,
                          borderColor: zone.color,
                        }}
                        onClick={() => setSelectedZone(zone)}
                      >
                        <div className="quadrant-header">
                          <strong>{zone.zone_name.split("(")[0]}</strong>
                          <span
                            className="ndvi-pill"
                            style={{ backgroundColor: zone.color, color: "#fff" }}
                          >
                            VMI {zone.ndvi}
                          </span>
                        </div>
                        <span className="sector-status">{zone.status}</span>
                      </div>
                    ))}
                  </div>
                  <span className="field-hint">{t("modals.satellite.clickHint")}</span>
                </div>

                {/* Selected Sector Details */}
                <div className="sector-detail-col">
                  {selectedZone && (
                    <div className="sector-inspector-card">
                      <div className="inspector-header">
                        <Eye size={18} />
                        <h4>{selectedZone.zone_name}</h4>
                      </div>
                      <div className="inspector-row">
                        <span>Vegetation Moisture Index</span>
                        <strong>{selectedZone.ndvi}</strong>
                      </div>
                      <div className="inspector-row">
                        <span>Canopy Condition</span>
                        <strong style={{ color: selectedZone.color }}>
                          {selectedZone.status}
                        </strong>
                      </div>
                      <div className="inspector-notes">
                        <Info size={15} />
                        <p>{selectedZone.notes}</p>
                      </div>
                    </div>
                  )}

                  {/* Distribution breakdown */}
                  <div className="biomass-breakdown-card">
                    <h4>{t("modals.satellite.biomassDist")}</h4>
                    <div className="distribution-bar">
                      <div
                        className="bar-segment healthy"
                        style={{ width: `${data.health_distribution?.healthy_dense}%` }}
                        title="High Moisture Zones"
                      ></div>
                      <div
                        className="bar-segment moderate"
                        style={{ width: `${data.health_distribution?.moderate_canopy}%` }}
                        title="Moderate Moisture"
                      ></div>
                      <div
                        className="bar-segment stressed"
                        style={{ width: `${data.health_distribution?.stressed_deficient}%` }}
                        title="Low Moisture / Stress"
                      ></div>
                    </div>
                    <div className="legend-row">
                      <span>🟢 {t("modals.satellite.dense")}: {data.health_distribution?.healthy_dense}%</span>
                      <span>🟡 {t("modals.satellite.moderate")}: {data.health_distribution?.moderate_canopy}%</span>
                      <span>🔴 {t("modals.satellite.stressed")}: {data.health_distribution?.stressed_deficient}%</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Advisories */}
              <div className="sat-advisories-card">
                <h4>
                  <Activity size={17} /> {t("modals.satellite.fieldActions")}
                </h4>
                <ul>
                  {data.satellite_advisory?.map((adv, idx) => (
                    <li key={idx}>{adv}</li>
                  ))}
                </ul>
              </div>

              {/* Disclaimer */}
              {data.data_disclaimer && (
                <div className="sat-disclaimer">
                  <AlertCircle size={13} />
                  <small>{data.data_disclaimer}</small>
                </div>
              )}
            </>
          ) : (
            <div className="error-banner">{t("modals.satellite.error")}</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SatelliteModal;
