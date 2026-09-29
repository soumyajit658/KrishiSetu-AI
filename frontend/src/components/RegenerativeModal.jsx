import { useState, useEffect, useRef } from "react";
import {
  Leaf,
  Recycle,
  Droplets,
  TreePine,
  Wind,
  RefreshCw,
  X,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Sun,
  AlertCircle,
  CheckCircle2,
  FlaskConical,
} from "lucide-react";
import { api } from "../services/api";
import { useLanguage } from "../context/LanguageContext";

// ── Section Accordion ─────────────────────────────────────────────────────────
function Section({ icon, title, items, color = "#4caf50", defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  if (!items || items.length === 0) return null;
  return (
    <div className="regen-section">
      <button
        className={`regen-section-header regen-color-${color.replace("#", "")}`}
        onClick={() => setOpen((o) => !o)}
        style={{ borderLeft: `4px solid ${color}` }}
      >
        <span className="regen-section-title">
          {icon}
          <strong>{title}</strong>
        </span>
        {open ? <ChevronUp size={17} /> : <ChevronDown size={17} />}
      </button>
      {open && (
        <ul className="regen-section-list">
          {items.map((item, i) => (
            <li key={i} className="regen-section-item">
              <CheckCircle2 size={14} className="regen-bullet" style={{ color }} />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ── Benefit Card ──────────────────────────────────────────────────────────────
function BenefitCard({ label, value, icon }) {
  return (
    <div className="regen-benefit-card">
      <div className="regen-benefit-icon">{icon}</div>
      <div>
        <div className="regen-benefit-label">{label}</div>
        <div className="regen-benefit-value">{value}</div>
      </div>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────
function RegenerativeModal({ isOpen, onClose, farmData }) {
  const { t, translateCrop, translateSoil } = useLanguage();
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const abortRef              = useRef(null);

  useEffect(() => {
    if (isOpen) fetchAdvisory();
    return () => {
      if (abortRef.current) abortRef.current.abort();
    };
  }, [isOpen, farmData?.crop, farmData?.soil, farmData?.location]);

  const fetchAdvisory = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getRegenerativeAdvisory({
        crop:      farmData?.crop      || "Rice",
        soil:      farmData?.soil      || "Alluvial Soil",
        location:  farmData?.location  || "India",
        area:      parseFloat(farmData?.area || 2),
        irrigation: farmData?.irrigation || "Canal",
      });
      setData(res);
    } catch (err) {
      console.error(err);
      setError("Could not fetch regenerative advisory. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const crop = translateCrop(farmData?.crop) || farmData?.crop || "Your Crop";
  const soil = translateSoil(farmData?.soil) || farmData?.soil || "Your Soil";

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-container regen-modal"
        onClick={(e) => e.stopPropagation()}
      >
        {/* ── Header ── */}
        <div className="modal-header">
          <div className="modal-header-brand">
            <div className="modal-icon-badge regen">
              <Recycle size={22} />
            </div>
            <div>
              <h3>Regenerative Farming Advisory</h3>
              <p className="modal-subtext">
                Soil-health, carbon & biodiversity practices •{" "}
                <strong>{crop}</strong> on <strong>{soil}</strong>
              </p>
            </div>
          </div>
          <div className="modal-header-actions">
            <button
              className="refresh-btn"
              onClick={fetchAdvisory}
              disabled={loading}
              title="Refresh advisory"
            >
              <RefreshCw size={16} className={loading ? "spinning" : ""} />
            </button>
            <button className="close-btn" onClick={onClose}>
              <X size={20} />
            </button>
          </div>
        </div>

        {/* ── Body ── */}
        <div className="modal-body">
          {loading && !data ? (
            <div className="loading-state">
              <RefreshCw size={24} className="spinning" />
              <span>Generating regenerative farming plan…</span>
            </div>
          ) : error ? (
            <div className="error-banner">
              <AlertCircle size={18} />
              {error}
            </div>
          ) : data ? (
            <>
              {/* Source badge */}
              <div className="regen-source-badge">
                {data.source?.includes("Gemini") ? (
                  <><Sparkles size={13} /> AI-generated by Google Gemini</>
                ) : (
                  <><FlaskConical size={13} /> KrishiSetu Expert Knowledge Base</>
                )}
              </div>

              {/* Summary */}
              {data.summary && (
                <div className="regen-summary-card">
                  <p>{data.summary}</p>
                </div>
              )}

              {/* Quick Wins */}
              {data.quick_wins?.length > 0 && (
                <div className="regen-quickwins">
                  <h4><Sparkles size={15} /> Quick Wins — Start This Season</h4>
                  <div className="regen-quickwins-grid">
                    {data.quick_wins.map((win, i) => (
                      <div key={i} className="regen-quickwin-item">
                        <span className="regen-qw-num">{i + 1}</span>
                        <span>{win}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Accordion Sections */}
              <div className="regen-sections">
                <Section
                  icon={<Leaf size={15} />}
                  title="Cover Crops & Green Manures"
                  items={data.cover_crops_green_manures}
                  color="#4caf50"
                  defaultOpen
                />
                <Section
                  icon={<FlaskConical size={15} />}
                  title="Soil Biology & Organic Matter"
                  items={data.soil_biology_practices}
                  color="#795548"
                />
                <Section
                  icon={<Droplets size={15} />}
                  title="Water Conservation"
                  items={data.water_conservation}
                  color="#1976d2"
                />
                <Section
                  icon={<RefreshCw size={15} />}
                  title="Crop Rotation Plan"
                  items={
                    typeof data.crop_rotation_plan === "string"
                      ? [data.crop_rotation_plan]
                      : data.crop_rotation_plan
                  }
                  color="#9c27b0"
                />
                <Section
                  icon={<TreePine size={15} />}
                  title="Agroforestry & Biodiversity"
                  items={data.agroforestry_biodiversity}
                  color="#2e7d32"
                />
                <Section
                  icon={<Wind size={15} />}
                  title="Carbon Sequestration"
                  items={data.carbon_sequestration}
                  color="#607d8b"
                />
                <Section
                  icon={<Sun size={15} />}
                  title="Soil Health Targets"
                  items={data.soil_health_targets}
                  color="#ff8f00"
                />
              </div>

              {/* Expected Benefits */}
              {data.expected_benefits && (
                <div className="regen-benefits-section">
                  <h4>Expected Benefits with Full Practice Adoption</h4>
                  <div className="regen-benefits-grid">
                    {data.expected_benefits.soil_organic_carbon_gain && (
                      <BenefitCard
                        icon="🌱"
                        label="Soil Organic Carbon"
                        value={data.expected_benefits.soil_organic_carbon_gain}
                      />
                    )}
                    {data.expected_benefits.water_savings && (
                      <BenefitCard
                        icon="💧"
                        label="Water Savings"
                        value={data.expected_benefits.water_savings}
                      />
                    )}
                    {data.expected_benefits.input_cost_reduction && (
                      <BenefitCard
                        icon="₹"
                        label="Input Cost Reduction"
                        value={data.expected_benefits.input_cost_reduction}
                      />
                    )}
                    {data.expected_benefits.biodiversity_index && (
                      <BenefitCard
                        icon="🦋"
                        label="Biodiversity Index"
                        value={data.expected_benefits.biodiversity_index}
                      />
                    )}
                    {data.expected_benefits.carbon_credits && (
                      <BenefitCard
                        icon="🏅"
                        label="Carbon Credits"
                        value={data.expected_benefits.carbon_credits}
                      />
                    )}
                  </div>
                </div>
              )}

              {/* Disclaimer */}
              {data.disclaimer && (
                <div className="regen-disclaimer">
                  <AlertCircle size={14} />
                  <small>{data.disclaimer}</small>
                </div>
              )}
            </>
          ) : (
            <div className="error-banner">No advisory data available.</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default RegenerativeModal;
