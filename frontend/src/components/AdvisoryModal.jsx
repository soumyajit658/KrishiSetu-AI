import { useState, useEffect } from "react";
import {
  Leaf,
  Calendar,
  CheckCircle,
  X,
  RefreshCw,
  Sparkles,
  Sprout,
} from "lucide-react";
import { api } from "../services/api";
import { useLanguage } from "../context/LanguageContext";

function AdvisoryModal({ isOpen, onClose, farmData }) {
  const { t, translateCrop, translateSoil, translateIrrigation } = useLanguage();
  const [advisory, setAdvisory] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchAdvisory();
    }
  }, [isOpen, farmData?.crop, farmData?.soil]);

  const fetchAdvisory = async () => {
    setLoading(true);
    try {
      const res = await api.getCropAdvisory(
        farmData?.crop || "Rice",
        farmData?.soil || "Alluvial Soil",
        farmData?.area || 1,
        farmData?.irrigation || "Tube Well"
      );
      setAdvisory(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container advisory-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="modal-header-brand">
            <div className="modal-icon-badge advisory">
              <Leaf size={22} />
            </div>
            <div>
              <h3>{t("modals.advisory.title")}</h3>
              <p className="modal-subtext">
                {t("modals.advisory.subtext")} • {translateCrop(farmData?.crop) || farmData?.crop || "Rice"} ({translateSoil(farmData?.soil) || farmData?.soil || "Alluvial Soil"})
              </p>
            </div>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {loading && !advisory ? (
            <div className="loading-state">
              <RefreshCw size={24} className="spinning" />
              <span>{t("modals.advisory.loading")}</span>
            </div>
          ) : advisory ? (
            <>
              {/* Profile banner */}
              <div className="advisory-summary-card">
                <div className="advisory-pill">
                  <Sprout size={16} /> {t("modals.advisory.mainCrop")}: <strong>{translateCrop(advisory.crop) || advisory.crop}</strong>
                </div>
                <div className="advisory-pill">
                  🌱 {t("modals.advisory.soil")}: <strong>{translateSoil(advisory.soil) || advisory.soil}</strong>
                </div>
                <div className="advisory-pill">
                  💧 {t("modals.advisory.irrigation")}: <strong>{translateIrrigation(farmData?.irrigation) || farmData?.irrigation || "Standard"}</strong>
                </div>
              </div>

              {/* Growth Timeline */}
              <div className="timeline-section">
                <h4>
                  <Calendar size={18} /> {t("modals.advisory.growthStages")}
                </h4>
                <div className="stages-timeline">
                  {advisory.growth_stages?.map((stage, idx) => (
                    <div key={idx} className="timeline-stage-card">
                      <div className="stage-marker">
                        <span className="stage-num">{idx + 1}</span>
                        {idx < advisory.growth_stages.length - 1 && (
                          <div className="stage-line"></div>
                        )}
                      </div>
                      <div className="stage-content">
                        <div className="stage-header">
                          <h5>{stage.stage}</h5>
                          {stage.duration && (
                            <span className="duration-tag">{stage.duration}</span>
                          )}
                        </div>
                        <ul className="stage-actions-list">
                          {stage.key_actions?.map((act, actIdx) => (
                            <li key={actIdx}>
                              <CheckCircle size={15} className="bullet-icon" />
                              <span>{act}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Strategic Tips */}
              {advisory.recommendations && (
                <div className="strategic-tips-card">
                  <h4>
                    <Sparkles size={16} /> {t("modals.advisory.recommendations")}
                  </h4>
                  <ul>
                    {advisory.recommendations.map((tip, idx) => (
                      <li key={idx}>{tip}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          ) : (
            <div className="error-banner">{t("modals.advisory.error")}</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AdvisoryModal;
