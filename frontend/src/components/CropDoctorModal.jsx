import { useState, useEffect } from "react";
import {
  Stethoscope,
  Upload,
  Camera,
  MapPin,
  CheckCircle2,
  AlertTriangle,
  X,
  Sparkles,
  RefreshCw,
  Leaf,
  Layers,
  Calendar,
  MessageSquare,
  Info,
  Compass,
  FileText,
  ArrowLeft,
  ArrowRight,
  Trash2,
} from "lucide-react";
import { api } from "../services/api";
import { useLanguage } from "../context/LanguageContext";

function CropDoctorModal({ isOpen, onClose, farmData, onOpenChatWithContext }) {
  const { t, translateCrop, translateSoil } = useLanguage();
  const [activeTab, setActiveTab] = useState("crop"); // 'crop' | 'field' | 'history'
  
  // Crop mode state
  const [selectedCropImages, setSelectedCropImages] = useState([]);
  const [cropPreviews, setCropPreviews] = useState([]);
  
  // Field mode state
  const [fieldImage, setFieldImage] = useState(null);
  const [fieldPreview, setFieldPreview] = useState(null);
  const [gpsLocation, setGpsLocation] = useState(null);
  const [gpsLoading, setGpsLoading] = useState(false);
  
  // General state
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [historyList, setHistoryList] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [qualityWarning, setQualityWarning] = useState(null);

  // Load history whenever modal opens or when tab switches to history
  useEffect(() => {
    if (isOpen) {
      loadHistory();
    }
  }, [isOpen, activeTab]);

  if (!isOpen) return null;

  const loadHistory = async () => {
    setHistoryLoading(true);
    try {
      const records = await api.getDoctorHistory(30);
      setHistoryList(records || []);
    } catch (err) {
      console.error("Error loading doctor history:", err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleViewHistoryReport = (record) => {
    setReport(record);
  };

  const handleDeleteHistoryRecord = async (e, recordId) => {
    e.stopPropagation();
    if (window.confirm("Remove this scan from history?")) {
      setHistoryList((prev) => prev.filter((item) => String(item.id) !== String(recordId)));
      await api.deleteDoctorHistoryRecord(recordId);
    }
  };

  const handleClearAllHistory = async () => {
    if (window.confirm("Are you sure you want to clear your entire diagnostic history?")) {
      setHistoryList([]);
      await api.clearDoctorHistory();
    }
  };

  // Switch tabs - always unlocks inputs and clears blocking report if switching to another tab
  const handleTabSwitch = (tab) => {
    setActiveTab(tab);
    setReport(null); // clears report view so user sees inputs immediately
    setQualityWarning(null);
  };

  // Handle multi-image selection for crop
  const handleCropImagesChange = (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;
    
    const combined = [...selectedCropImages, ...files].slice(0, 4); // Max 4 images
    setSelectedCropImages(combined);
    
    const previews = combined.map((f) => URL.createObjectURL(f));
    setCropPreviews(previews);
    setQualityWarning(null);
    setReport(null);
  };

  const removeCropImage = (index) => {
    const newFiles = selectedCropImages.filter((_, i) => i !== index);
    const newPreviews = cropPreviews.filter((_, i) => i !== index);
    setSelectedCropImages(newFiles);
    setCropPreviews(newPreviews);
  };

  // Helper to load test samples
  const loadTestSample = (sampleType) => {
    const canvas = document.createElement("canvas");
    canvas.width = 300;
    canvas.height = 300;
    const ctx = canvas.getContext("2d");
    
    ctx.fillStyle = sampleType === "healthy" ? "#34a853" : "#7d852a";
    ctx.beginPath();
    ctx.ellipse(150, 150, 110, 70, Math.PI / 4, 0, 2 * Math.PI);
    ctx.fill();

    if (sampleType === "blight") {
      ctx.fillStyle = "#3d1e08";
      ctx.beginPath();
      ctx.arc(130, 130, 22, 0, 2 * Math.PI);
      ctx.arc(170, 160, 18, 0, 2 * Math.PI);
      ctx.fill();
    }

    canvas.toBlob((blob) => {
      const file = new File([blob], `${sampleType}_leaf_sample.jpg`, { type: "image/jpeg" });
      setSelectedCropImages([file]);
      setCropPreviews([URL.createObjectURL(file)]);
      setQualityWarning(null);
      setReport(null);
    }, "image/jpeg");
  };

  // Handle GPS location request
  const handleGetGPS = () => {
    if (!navigator.geolocation) {
      alert("GPS Geolocation is not supported by your browser.");
      return;
    }
    setGpsLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setGpsLocation({
          lat: parseFloat(pos.coords.latitude.toFixed(4)),
          lon: parseFloat(pos.coords.longitude.toFixed(4)),
        });
        setGpsLoading(false);
      },
      (err) => {
        console.warn("GPS error:", err);
        setGpsLoading(false);
        // Fallback coordinates for demo
        setGpsLocation({ lat: 22.0667, lon: 88.0667 });
      },
      { timeout: 8000 }
    );
  };

  // Run Crop Analysis
  const handleAnalyzeCrop = async () => {
    if (!selectedCropImages.length) return;
    setLoading(true);
    setQualityWarning(null);

    try {
      const result = await api.analyzeCropDoctor(
        selectedCropImages,
        farmData?.crop || "Tomato",
        {
          soil: farmData?.soil || "Alluvial Soil",
          location: farmData?.location || "Haldia, West Bengal",
        }
      );

      if (result.quality_passed === false) {
        setQualityWarning(result);
      } else {
        setReport(result);
        setHistoryList((prev) => [
          result,
          ...prev.filter((p) => p.id !== result.id && p.id !== result.saved_report_id),
        ]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Run Field Analysis
  const handleAnalyzeField = async () => {
    setLoading(true);
    setQualityWarning(null);

    try {
      const result = await api.analyzeFieldDoctor(
        fieldImage,
        gpsLocation?.lat || 22.0667,
        gpsLocation?.lon || 88.0667,
        farmData?.location || "Haldia, West Bengal",
        farmData?.crop || "Rice",
        farmData?.soil || "Alluvial Soil"
      );

      if (result.quality_passed === false) {
        setQualityWarning(result);
      } else {
        setReport(result);
        setHistoryList((prev) => [
          result,
          ...prev.filter((p) => p.id !== result.id && p.id !== result.saved_report_id),
        ]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const resetAnalysis = () => {
    setReport(null);
    setQualityWarning(null);
    setSelectedCropImages([]);
    setCropPreviews([]);
    setFieldImage(null);
    setFieldPreview(null);
  };

  const handleChatHandoff = () => {
    if (!report) return;
    onClose();
    if (onOpenChatWithContext) {
      onOpenChatWithContext(report);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container doctor-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="modal-header-brand">
            <div className="modal-icon-badge doctor">
              <Stethoscope size={22} />
            </div>
            <div>
              <h3>{t("modals.doctor.title")}</h3>
              <p className="modal-subtext">
                {t("modals.doctor.subtext")}
              </p>
            </div>
          </div>
          <button className="close-btn" onClick={onClose} title="Close window">
            <X size={20} />
          </button>
        </div>

        {/* ALWAYS VISIBLE TAB BAR - Farmers can switch tabs at any time! */}
        <div className="doctor-tab-bar">
          <button
            className={`doc-tab ${activeTab === "crop" && !report ? "active" : ""}`}
            onClick={() => handleTabSwitch("crop")}
            title={report ? "Click to go back and analyze a new crop photo" : ""}
          >
            <Leaf size={16} /> {t("modals.doctor.tabCrop")}
          </button>

          <button
            className={`doc-tab ${activeTab === "field" && !report ? "active" : ""}`}
            onClick={() => handleTabSwitch("field")}
            title={report ? "Click to go back and run a new field analysis" : ""}
          >
            <Layers size={16} /> {t("modals.doctor.tabField")}
          </button>

          <button
            className={`doc-tab ${activeTab === "history" && !report ? "active" : ""}`}
            onClick={() => handleTabSwitch("history")}
            title={report ? "Click to view field history" : ""}
          >
            <Calendar size={16} /> {t("modals.doctor.tabHistory")}
          </button>

          {report && (
            <button
              className="doc-tab report-active-tab active"
              onClick={() => {}}
              title="Currently viewing diagnostic report"
            >
              <FileText size={16} /> {t("modals.doctor.tabReport")}
            </button>
          )}
        </div>

        <div className="modal-body">
          {/* ============================================================== */}
          {/* TAB 1: CROP MULTI-IMAGE ANALYSIS                               */}
          {/* ============================================================== */}
          {activeTab === "crop" && !report && (
            <div className="doctor-upload-container">
              {/* Quality alert banner if previous attempt had issues */}
              {qualityWarning && (
                <div className="quality-alert-banner">
                  <div className="alert-head">
                    <AlertTriangle size={20} />
                    <strong>{t("modals.doctor.insufficientEvidence")}</strong>
                  </div>
                  <p>{qualityWarning.diagnosis_message}</p>
                  <ul>
                    {qualityWarning.guidance_instructions?.map((g, idx) => (
                      <li key={idx}>{g}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="multi-image-uploader">
                <label className="multi-dropzone">
                  <input
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={handleCropImagesChange}
                    style={{ display: "none" }}
                  />
                  <div className="upload-icon-circle doctor">
                    <Camera size={28} />
                  </div>
                  <strong>{t("modals.doctor.uploadPrompt")}</strong>
                  <span>{t("modals.doctor.uploadHint")}</span>
                </label>

                {/* Previews grid */}
                {cropPreviews.length > 0 && (
                  <div className="thumbnail-grid">
                    {cropPreviews.map((src, index) => (
                      <div key={index} className="thumb-item">
                        <img src={src} alt={`Upload ${index + 1}`} />
                        <button
                          className="thumb-remove"
                          onClick={() => removeCropImage(index)}
                          title="Remove photo"
                        >
                          ×
                        </button>
                        <span className="thumb-label">Photo {index + 1}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Sample test buttons */}
                {cropPreviews.length === 0 && (
                  <div className="sample-test-strip">
                    <span>{t("modals.doctor.sampleTest")}</span>
                    <div className="sample-buttons">
                      <button
                        className="sample-btn"
                        onClick={() => loadTestSample("blight")}
                      >
                        {t("modals.doctor.sampleBlight")}
                      </button>
                      <button
                        className="sample-btn"
                        onClick={() => loadTestSample("healthy")}
                      >
                        {t("modals.doctor.sampleHealthy")}
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="modal-actions">
                <button
                  className="primary-btn"
                  disabled={cropPreviews.length === 0 || loading}
                  onClick={handleAnalyzeCrop}
                >
                  {loading ? (
                    <>
                      <RefreshCw size={17} className="spinning" />
                      {t("modals.doctor.diagnosing")} ({selectedCropImages.length})
                    </>
                  ) : (
                    <>
                      <Sparkles size={17} />
                      {t("modals.doctor.diagnoseCropBtn")}
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* ============================================================== */}
          {/* TAB 2: ANALYZE MY FIELD                                        */}
          {/* ============================================================== */}
          {activeTab === "field" && !report && (
            <div className="doctor-upload-container">
              <div className="field-inputs-grid">
                {/* Field Image Uploader */}
                <div className="field-photo-card">
                  <h4>{t("modals.doctor.fieldPhotoTitle")}</h4>
                  <label className="field-dropzone">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => {
                        const file = e.target.files[0];
                        if (file) {
                          setFieldImage(file);
                          setFieldPreview(URL.createObjectURL(file));
                        }
                      }}
                      style={{ display: "none" }}
                    />
                    {fieldPreview ? (
                      <div className="field-preview-wrapper">
                        <img src={fieldPreview} alt="Field preview" className="field-thumb-preview" />
                        <button
                          type="button"
                          className="field-remove-btn"
                          onClick={(e) => {
                            e.preventDefault();
                            setFieldImage(null);
                            setFieldPreview(null);
                          }}
                        >
                          {t("modals.doctor.changePhoto")}
                        </button>
                      </div>
                    ) : (
                      <>
                        <Upload size={26} />
                        <span>{t("modals.doctor.fieldPhotoPrompt")}</span>
                      </>
                    )}
                  </label>
                </div>

                {/* GPS Location Intelligence */}
                <div className="field-geo-card">
                  <h4>{t("modals.doctor.fieldGeoTitle")}</h4>
                  <p className="geo-desc">
                    {t("modals.doctor.fieldGeoDesc")}
                  </p>

                  <div className="gps-action-box">
                    <button
                      type="button"
                      className="gps-btn"
                      onClick={handleGetGPS}
                      disabled={gpsLoading}
                    >
                      <Compass size={17} />
                      {gpsLoading ? t("modals.doctor.acquiringGps") : t("modals.doctor.acquireGps")}
                    </button>

                    {gpsLocation && (
                      <div className="gps-coords-badge">
                        <span>Lat: {gpsLocation.lat}° N</span>
                        <span>Lon: {gpsLocation.lon}° E</span>
                      </div>
                    )}
                  </div>

                  <div className="farm-context-preview">
                    <small>Default Context:</small>
                    <strong>
                      {translateCrop(farmData?.crop) || farmData?.crop || "Rice"} • {translateSoil(farmData?.soil) || farmData?.soil || "Alluvial Soil"} • {farmData?.location || "Haldia"}
                    </strong>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="modal-actions">
                <button
                  className="primary-btn"
                  disabled={loading}
                  onClick={handleAnalyzeField}
                >
                  {loading ? (
                    <>
                      <RefreshCw size={17} className="spinning" />
                      {t("modals.doctor.runningField")}
                    </>
                  ) : (
                    <>
                      <Layers size={17} />
                      {t("modals.doctor.runFieldBtn")}
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* ============================================================== */}
          {/* TAB 3: FIELD HISTORY & TRENDS                                  */}
          {/* ============================================================== */}
          {activeTab === "history" && !report && (
            <div className="history-tab-view">
              <div className="history-header-row">
                <div>
                  <h4>
                    <Calendar size={18} /> {t("modals.doctor.historyTitle")}
                  </h4>
                  <p className="history-sub">
                    {t("modals.doctor.historySub")}
                  </p>
                </div>
                <div className="history-actions-header">
                  <button className="secondary-btn small" onClick={loadHistory} title="Refresh records">
                    <RefreshCw size={14} className={historyLoading ? "spinning" : ""} /> {t("modals.doctor.refresh")}
                  </button>
                  {historyList.length > 0 && (
                    <button className="subtle-btn small danger-text" onClick={handleClearAllHistory} title="Clear all history">
                      <Trash2 size={13} /> Clear All
                    </button>
                  )}
                </div>
              </div>

              {historyLoading && historyList.length === 0 ? (
                <div className="loading-state">
                  <RefreshCw size={24} className="spinning" />
                  <span>{t("common.loading")}</span>
                </div>
              ) : historyList.length === 0 ? (
                <div className="empty-history-box">
                  <FileText size={36} />
                  <strong>{t("modals.doctor.noHistory")}</strong>
                  <span>{t("modals.doctor.noHistorySub")}</span>
                  <div style={{ marginTop: "12px" }}>
                    <button className="primary-btn small" onClick={() => handleTabSwitch("field")}>
                      {t("modals.doctor.analyzeFieldNow")}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="history-timeline-list">
                  {historyList.map((item) => (
                    <div
                      key={item.id}
                      className="history-record-card clickable"
                      onClick={() => handleViewHistoryReport(item)}
                      title="Click to view detailed diagnostic report & remedies"
                    >
                      <div className="history-card-left">
                        <div className="history-meta-top">
                          <span className={`history-type-badge ${item.analysis_type || "crop"}`}>
                            {item.analysis_type === "field" ? "🛰️ Field Analysis" : "📷 Crop Scan"}
                          </span>
                          <span className="history-date">
                            {item.timestamp ? new Date(item.timestamp).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }) : "Recent"}
                          </span>
                        </div>
                        <strong>
                          {translateCrop(item.crop_name) || item.crop_name} {item.field_name ? `• ${item.field_name}` : ""}
                        </strong>
                        <span className="history-issue">{item.primary_issue || item.overall_field_status || "General Check"}</span>
                      </div>
                      <div className="history-card-right">
                        <div className="health-score-pill">
                          <span>{t("modals.doctor.estimatedHealth")}</span>
                          <strong>{item.overall_health_score || item.field_health_score || item.health_score || 80}%</strong>
                        </div>
                        <span className={`status-pill ${item.severity?.toLowerCase() || "moderate"}`}>
                          {item.overall_health_status || item.overall_health || "Stable"}
                        </span>
                        <div className="history-card-actions">
                          <button
                            type="button"
                            className="view-report-link"
                            title="View Full Report"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleViewHistoryReport(item);
                            }}
                          >
                            <ArrowRight size={15} />
                          </button>
                          <button
                            type="button"
                            className="delete-history-btn"
                            title="Delete this record"
                            onClick={(e) => handleDeleteHistoryRecord(e, item.id)}
                          >
                            <Trash2 size={13} />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ============================================================== */}
          {/* REPORT VIEW: UNIFIED AI FARMER REPORT                           */}
          {/* ============================================================== */}
          {report && (
            <div className="farmer-report-view">
              {/* TOP NAVIGATION RETURN BAR - Always visible at top of report! */}
              <div className="report-top-navigation">
                <button
                  className="return-inputs-btn"
                  onClick={() => setReport(null)}
                >
                  <ArrowLeft size={16} />
                  {activeTab === "history" ? "← Back to Diagnostic History" : t("modals.doctor.backToInputs")}
                </button>

                <div className="top-nav-right">
                  <button
                    className="subtle-btn"
                    onClick={() => handleTabSwitch("field")}
                  >
                    <Layers size={14} /> {t("modals.doctor.reanalyzeField")}
                  </button>
                  <button
                    className="subtle-btn"
                    onClick={() => handleTabSwitch("crop")}
                  >
                    <Leaf size={14} /> {t("modals.doctor.checkNewCrop")}
                  </button>
                </div>
              </div>

              {/* Header Status Banner */}
              <div className={`report-status-header ${report.severity?.toLowerCase() || "moderate"}`}>
                <div className="header-status-text">
                  <span className="report-tag">
                    🌱 {report.analysis_type === "field" ? "FIELD OBSERVATION REPORT" : "CROP HEALTH REPORT"}
                  </span>
                  <h2>{report.primary_issue || report.overall_field_status}</h2>
                  <p>
                    Crop: <strong>{translateCrop(report.crop_name) || report.crop_name}</strong>
                    {report.variety ? ` • Variety: ${report.variety}` : ""}
                    {report.growth_stage ? ` • Stage: ${report.growth_stage}` : ""}
                  </p>
                </div>

                <div className="report-health-gauge">
                  <div className="gauge-score">
                    {report.overall_health_score || report.field_health_score || report.health_score || 78}%
                  </div>
                  <small>{t("modals.doctor.estimatedHealth")}</small>
                  <span className="confidence-tag">
                    {report.health_confidence || report.confidence_level || "HIGH"} {t("modals.doctor.confidence")}
                  </span>
                </div>
              </div>

              {/* Disclaimer notice */}
              <div className="estimation-disclaimer-box">
                <Info size={15} />
                <span>
                  <strong>{t("modals.doctor.disclaimerNotice")}</strong> {t("modals.doctor.disclaimerText")}
                </span>
              </div>

              {/* Observed Symptoms & Why Suspected */}
              {(report.symptoms || report.risk_factors) && (report.symptoms || report.risk_factors).length > 0 && (
                <div className="report-card">
                  <h4>
                    <AlertTriangle size={16} /> {t("modals.doctor.symptomsRationale")}
                  </h4>
                  <ul className="symptom-list">
                    {(report.symptoms || report.risk_factors).map((s, idx) => (
                      <li key={idx}>{s}</li>
                    ))}
                  </ul>
                  {report.why_suspected && (
                    <div className="why-suspected-box">
                      <strong>{t("modals.doctor.whySuspected")}</strong>
                      <p>{report.why_suspected}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Visual Estimation vs Measured Data (For Field Mode) */}
              {report.visual_field_estimations && Object.keys(report.visual_field_estimations).length > 0 && (
                <div className="comparison-cards-grid">
                  <div className="report-card visual-est">
                    <h4>{t("modals.doctor.visualEstimations")}</h4>
                    <ul>
                      <li>Surface Dryness: <strong>{report.visual_field_estimations.visual_dryness || "Normal"}</strong></li>
                      <li>Standing Water: <strong>{report.visual_field_estimations.standing_water_detected ? "Detected" : "None observed"}</strong></li>
                      <li>Soil Cracking: <strong>{report.visual_field_estimations.soil_cracking_observed ? "Visible fissures" : "No severe cracking"}</strong></li>
                      <li>Weed Density: <strong>{report.visual_field_estimations.weed_pressure_level || "Low"}</strong></li>
                      <li>Canopy Uniformity: <strong>{report.visual_field_estimations.crop_uniformity || "Uniform Stand"}</strong></li>
                    </ul>
                  </div>

                  {report.verified_measured_data && Object.keys(report.verified_measured_data).length > 0 && (
                    <div className="report-card measured-data">
                      <h4>{t("modals.doctor.verifiedData")}</h4>
                      <ul>
                        {report.verified_measured_data.satellite_ndvi !== undefined && (
                          <li>Sentinel-2 NDVI: <strong>{report.verified_measured_data.satellite_ndvi} (Vegetative Index)</strong></li>
                        )}
                        {report.verified_measured_data.temperature_celsius !== undefined && (
                          <li>Temperature: <strong>{report.verified_measured_data.temperature_celsius}°C</strong></li>
                        )}
                        {report.verified_measured_data.relative_humidity_percent !== undefined && (
                          <li>Relative Humidity: <strong>{report.verified_measured_data.relative_humidity_percent}%</strong></li>
                        )}
                        {report.verified_measured_data.precipitation_mm !== undefined && (
                          <li>Precipitation: <strong>{report.verified_measured_data.precipitation_mm} mm</strong></li>
                        )}
                        {report.verified_measured_data.soil_chemistry_note && (
                          <li className="sensor-note"><small>🧪 {report.verified_measured_data.soil_chemistry_note}</small></li>
                        )}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Recommended Next Steps */}
              {(report.recommended_actions || report.recommendations) && (report.recommended_actions || report.recommendations).length > 0 && (
                <div className="report-card recommendations">
                  <h4>
                    <CheckCircle2 size={16} /> {t("modals.doctor.recommendedActions")}
                  </h4>
                  <ul className="actions-numbered-list">
                    {(report.recommended_actions || report.recommendations).map((act, idx) => (
                      <li key={idx}>
                        <span className="action-number">{idx + 1}</span>
                        <span>{act}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Environmental Context / Satellite */}
              {report.satellite_summary && (
                <div className="report-context-strip">
                  <div className="context-pill">
                    🛰️ Satellite NDVI: <strong>{report.satellite_summary.ndvi}</strong>
                  </div>
                  <div className="context-pill">
                    🌿 Canopy Cover: <strong>{report.satellite_summary.canopy_cover}</strong>
                  </div>
                  <div className="context-pill">
                    🌦️ Weather: <strong>{report.weather_summary?.temp} • {report.weather_summary?.condition}</strong>
                  </div>
                </div>
              )}

              {/* Bottom Actions - Farmer can easily reset, re-analyze or ask AI */}
              <div className="report-footer-actions">
                <button className="secondary-btn" onClick={() => setReport(null)}>
                  <ArrowLeft size={16} /> {activeTab === "history" ? "Back to Field History" : t("common.back")}
                </button>
                <button className="secondary-btn" onClick={resetAnalysis}>
                  <RefreshCw size={16} /> {t("modals.doctor.clearStartNew")}
                </button>
                <button className="primary-btn ai-chat-connect" onClick={handleChatHandoff}>
                  <MessageSquare size={17} />
                  {t("modals.doctor.askAiAboutReport")}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default CropDoctorModal;
