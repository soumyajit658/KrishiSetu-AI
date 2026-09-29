import { useState } from "react";
import {
  ShieldCheck,
  Upload,
  AlertTriangle,
  CheckCircle2,
  X,
  Sparkles,
  RefreshCw,
  Leaf,
  FlaskConical,
  Info,
} from "lucide-react";
import { api } from "../services/api";
import { useLanguage } from "../context/LanguageContext";

function DiseaseModal({ isOpen, onClose, farmData }) {
  const { t, language, translateCrop } = useLanguage();
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [diagnosis, setDiagnosis] = useState(null);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      processSelectedFile(file);
    }
  };

  const processSelectedFile = (file) => {
    setSelectedImage(file);
    setPreviewUrl(URL.createObjectURL(file));
    setDiagnosis(null);
    setError("");
  };

  const loadSample = async (sampleType) => {
    try {
      setLoading(true);
      setError("");
      const canvas = document.createElement("canvas");
      canvas.width = 300;
      canvas.height = 300;
      const ctx = canvas.getContext("2d");
      
      ctx.fillStyle = sampleType === "healthy" ? "#34a853" : "#808b29";
      ctx.beginPath();
      ctx.ellipse(150, 150, 110, 70, Math.PI / 4, 0, 2 * Math.PI);
      ctx.fill();

      if (sampleType === "blight") {
        ctx.fillStyle = "#4a2810";
        ctx.beginPath();
        ctx.arc(130, 130, 22, 0, 2 * Math.PI);
        ctx.arc(170, 160, 18, 0, 2 * Math.PI);
        ctx.arc(140, 180, 14, 0, 2 * Math.PI);
        ctx.fill();
      }

      canvas.toBlob((blob) => {
        const file = new File([blob], `${sampleType}_sample_leaf.jpg`, { type: "image/jpeg" });
        processSelectedFile(file);
        setLoading(false);
      }, "image/jpeg");
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedImage) return;

    setLoading(true);
    setError("");
    try {
      const result = await api.detectDisease(selectedImage, farmData?.crop || "Rice");
      setDiagnosis(result);
    } catch (err) {
      setError("Analysis failed. Please try a clearer leaf photo.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedImage(null);
    setPreviewUrl(null);
    setDiagnosis(null);
    setError("");
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container disease-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="modal-header-brand">
            <div className="modal-icon-badge disease">
              <ShieldCheck size={22} />
            </div>
            <div>
              <h3>{t("modals.disease.title")}</h3>
              <p className="modal-subtext">
                {t("modals.disease.subtext")} ({farmData?.crop ? translateCrop(farmData.crop) : "Crop"})
              </p>
            </div>
          </div>
          <button className="close-btn" onClick={onClose} title={t("common.close")}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {!diagnosis ? (
            <div className="upload-view">
              {/* Drop / Pick Zone */}
              <div className="dropzone-card">
                {previewUrl ? (
                  <div className="preview-container">
                    <img src={previewUrl} alt="Leaf Preview" className="leaf-preview" />
                    {loading && (
                      <div className="radar-scanner">
                        <div className="radar-line"></div>
                        <span className="radar-label">{t("modals.disease.analyzing")}</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <label className="upload-placeholder">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      style={{ display: "none" }}
                    />
                    <div className="upload-icon-circle">
                      <Upload size={32} />
                    </div>
                    <strong>{t("modals.disease.takePhoto")}</strong>
                    <span>(JPG, PNG, WebP)</span>
                  </label>
                )}
              </div>

              {/* Sample test buttons */}
              {!previewUrl && (
                <div className="sample-test-strip">
                  <span>{t("modals.disease.sampleLeaves")}:</span>
                  <div className="sample-buttons">
                    <button
                      className="sample-btn"
                      onClick={() => loadSample("blight")}
                    >
                      🍂 {language === "hi" ? "रोगी पत्ती नमूना" : language === "bn" ? "আক্রান্ত পাতার নমুনা" : "Sample Diseased Leaf"}
                    </button>
                    <button
                      className="sample-btn"
                      onClick={() => loadSample("healthy")}
                    >
                      🌿 {language === "hi" ? "स्वस्थ पत्ती नमूना" : language === "bn" ? "সুস্থ পাতার নমুনা" : "Sample Healthy Leaf"}
                    </button>
                  </div>
                </div>
              )}

              {error && <div className="error-banner">{error}</div>}

              {/* Actions */}
              <div className="modal-actions">
                {previewUrl && !loading && (
                  <>
                    <button className="secondary-btn" onClick={handleReset}>
                      {language === "hi" ? "दूसरी तस्वीर चुनें" : language === "bn" ? "অন্য ছবি বাছুন" : "Choose Another Photo"}
                    </button>
                    <button className="primary-btn" onClick={handleAnalyze}>
                      <Sparkles size={18} />
                      {language === "hi" ? "एआई से जांचें" : language === "bn" ? "এআই দিয়ে পরীক্ষা করুন" : "Analyze with AI"}
                    </button>
                  </>
                )}
              </div>
            </div>
          ) : (
            /* Results View */
            <div className="results-view">
              {/* Summary Banner */}
              <div className={`diagnosis-banner ${diagnosis.severity?.toLowerCase()}`}>
                <div className="banner-left">
                  {diagnosis.severity === "Healthy" ? (
                    <CheckCircle2 size={36} className="status-icon green" />
                  ) : (
                    <AlertTriangle size={36} className="status-icon warning" />
                  )}
                  <div>
                    <span className="crop-tag">
                      {diagnosis.crop_detected ? translateCrop(diagnosis.crop_detected) : (farmData?.crop ? translateCrop(farmData.crop) : "Crop")}
                    </span>
                    <h2>{diagnosis.disease_name}</h2>
                    <p className="pathogen-info">
                      {language === "hi" ? "रोग कारक" : language === "bn" ? "রোগের জীবাণু" : "Pathogen"}: <strong>{diagnosis.pathogen_type || "Biological"}</strong>
                    </p>
                  </div>
                </div>

                <div className="confidence-pill">
                  <span>{t("common.confidence")}</span>
                  <strong>{diagnosis.confidence || 90}%</strong>
                </div>
              </div>

              {/* Observed Symptoms */}
              {diagnosis.symptoms && diagnosis.symptoms.length > 0 && (
                <div className="report-card">
                  <h4>
                    <Info size={16} /> {t("common.symptoms")}
                  </h4>
                  <ul className="symptom-list">
                    {diagnosis.symptoms.map((s, idx) => (
                      <li key={idx}>{s}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="treatments-grid">
                {/* Organic Remedies */}
                <div className="report-card organic">
                  <h4>
                    <Leaf size={16} /> {t("modals.disease.organicTitle")}
                  </h4>
                  <ul>
                    {diagnosis.organic_remedies?.map((r, idx) => (
                      <li key={idx}>{r}</li>
                    ))}
                  </ul>
                </div>

                {/* Chemical Treatments */}
                <div className="report-card chemical">
                  <h4>
                    <FlaskConical size={16} /> {t("modals.disease.chemicalTitle")}
                  </h4>
                  <ul>
                    {diagnosis.chemical_treatments?.map((c, idx) => (
                      <li key={idx}>{c}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Preventive Measures */}
              {diagnosis.preventive_measures && diagnosis.preventive_measures.length > 0 && (
                <div className="report-card preventive">
                  <h4>
                    <ShieldCheck size={16} /> {t("modals.disease.preventiveTitle")}
                  </h4>
                  <ul>
                    {diagnosis.preventive_measures.map((p, idx) => (
                      <li key={idx}>{p}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Buttons */}
              <div className="results-actions">
                <button className="primary-btn" onClick={handleReset}>
                  <RefreshCw size={17} />
                  {language === "hi" ? "नई पत्ती की जांच करें" : language === "bn" ? "নতুন পাতা পরীক্ষা করুন" : "Analyze Another Leaf"}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DiseaseModal;
