import { useState, useRef } from "react";
import {
  User,
  UserCheck,
  Camera,
  Upload,
  Phone,
  MapPin,
  Calendar,
  Award,
  Check,
  CheckCircle,
  Edit2,
  Sprout,
  ShieldCheck,
  FileText,
  X,
  ArrowRight,
  Sparkles,
  Info,
  Trash2,
} from "lucide-react";
import { useLanguage } from "../context/LanguageContext";

const PRESET_AVATARS = [
  { id: "farmer-male", emoji: "👨‍🌾", label: "Farmer (Male)" },
  { id: "farmer-female", emoji: "👩‍🌾", label: "Farmer (Female)" },
  { id: "farmer-neutral", emoji: "🧑‍🌾", label: "Young Grower" },
  { id: "paddy", emoji: "🌾", label: "Paddy Crop" },
  { id: "tractor", emoji: "🚜", label: "Tractor" },
  { id: "sprout", emoji: "🌱", label: "Seedling" },
];

function FarmerProfileModal({
  isOpen,
  onClose,
  farmerProfile,
  onUpdateProfile,
  farmData,
  onSetupFarm,
}) {
  const { t, translateCrop, translateSoil, translateIrrigation } = useLanguage();

  const [activeTab, setActiveTab] = useState("overview"); // "overview" | "edit"
  const [showAvatarPicker, setShowAvatarPicker] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const fileInputRef = useRef(null);

  // Form state for editing profile
  const [formData, setFormData] = useState({
    name: farmerProfile?.name || "Ramesh Kumar",
    phone: farmerProfile?.phone || "+91 98321 45678",
    location: farmerProfile?.location || farmData?.location || "Haldia, West Bengal",
    experienceYears: farmerProfile?.experienceYears || "14",
    farmerType: farmerProfile?.farmerType || "Small & Marginal Farmer",
    bio:
      farmerProfile?.bio ||
      "Third-generation paddy farmer focusing on sustainable soil health, high-efficiency canal irrigation, and AI-driven precision crop protection.",
  });

  if (!isOpen) return null;

  // Handle text input changes
  const handleInputChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // Handle preset emoji avatar selection
  const handleSelectEmoji = (emoji) => {
    const updated = {
      ...farmerProfile,
      avatarType: "emoji",
      avatarEmoji: emoji,
      avatarImage: null,
    };
    onUpdateProfile(updated);
    setShowAvatarPicker(false);
  };

  // Handle uploading custom photo
  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 2 * 1024 * 1024) {
      alert("Please upload a photo smaller than 2 MB.");
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result;
      const updated = {
        ...farmerProfile,
        avatarType: "image",
        avatarImage: dataUrl,
      };
      onUpdateProfile(updated);
      setShowAvatarPicker(false);
    };
    reader.readAsDataURL(file);
  };

  // Handle removing custom photo
  const handleRemovePhoto = () => {
    const updated = {
      ...farmerProfile,
      avatarType: "emoji",
      avatarEmoji: "👨‍🌾",
      avatarImage: null,
    };
    onUpdateProfile(updated);
  };

  // Save changes from Edit tab
  const handleSaveProfile = (e) => {
    e.preventDefault();
    const updated = {
      ...farmerProfile,
      ...formData,
    };
    onUpdateProfile(updated);
    setSaveSuccess(true);
    setTimeout(() => {
      setSaveSuccess(false);
      setActiveTab("overview");
    }, 1200);
  };

  const cropName = farmData?.crop ? translateCrop(farmData.crop) : "Rice (Paddy)";

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-container farmer-profile-modal"
        onClick={(e) => e.stopPropagation()}
      >
        {/* ================= MODAL HEADER ================= */}
        <div className="modal-header">
          <div className="modal-header-brand">
            <div className="modal-icon-badge profile-badge">
              <UserCheck size={22} />
            </div>
            <div>
              <h3>Farmer Profile & Identity</h3>
              <p className="modal-subtext">
                Government Kisan ID, personal details & agricultural credentials
              </p>
            </div>
          </div>
          <button className="close-btn" onClick={onClose} aria-label="Close modal">
            <X size={20} />
          </button>
        </div>

        {/* ================= MODAL BODY ================= */}
        <div className="modal-body profile-modal-body">
          {/* ================= HERO PROFILE CARD ================= */}
          <div className="profile-hero-card">
            <div className="profile-avatar-wrapper">
              <div
                className="profile-large-avatar"
                onClick={() => setShowAvatarPicker(!showAvatarPicker)}
                title="Click to change profile picture / avatar"
              >
                {farmerProfile?.avatarType === "image" && farmerProfile?.avatarImage ? (
                  <img
                    src={farmerProfile.avatarImage}
                    alt={farmerProfile.name}
                    className="avatar-uploaded-img"
                  />
                ) : (
                  <span className="avatar-emoji-display">
                    {farmerProfile?.avatarEmoji || "👨‍🌾"}
                  </span>
                )}
                <div className="avatar-camera-btn">
                  <Camera size={14} />
                </div>
              </div>

              {/* AVATAR PICKER POPUP */}
              {showAvatarPicker && (
                <div className="avatar-picker-dropdown">
                  <div className="picker-header">
                    <span>Choose Avatar or Photo</span>
                    <button
                      type="button"
                      className="picker-close-btn"
                      onClick={() => setShowAvatarPicker(false)}
                    >
                      <X size={14} />
                    </button>
                  </div>

                  <div className="preset-emojis-row">
                    {PRESET_AVATARS.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        className={`preset-emoji-btn ${
                          farmerProfile?.avatarEmoji === item.emoji &&
                          farmerProfile?.avatarType === "emoji"
                            ? "selected"
                            : ""
                        }`}
                        onClick={() => handleSelectEmoji(item.emoji)}
                        title={item.label}
                      >
                        {item.emoji}
                      </button>
                    ))}
                  </div>

                  <div className="picker-actions-divider">
                    <span>or upload custom picture</span>
                  </div>

                  <div className="picker-actions-row">
                    <button
                      type="button"
                      className="upload-photo-btn"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <Upload size={14} />
                      <span>Upload Photo</span>
                    </button>
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileUpload}
                      accept="image/*"
                      style={{ display: "none" }}
                    />

                    {farmerProfile?.avatarImage && (
                      <button
                        type="button"
                        className="remove-photo-btn"
                        onClick={handleRemovePhoto}
                        title="Remove uploaded picture and use avatar"
                      >
                        <Trash2 size={14} />
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="profile-hero-meta">
              <div className="hero-name-row">
                <h2>{farmerProfile?.name || "Ramesh Kumar"}</h2>
                <span className="kisan-verified-badge" title="Official Government Kisan Identity">
                  <ShieldCheck size={14} />
                  <span>Kisan ID: {farmerProfile?.kisanId || "KISAN-WB-7842"}</span>
                </span>
              </div>
              <p className="hero-role-sub">
                🌾 {cropName} Specialist &bull; 📍 {farmerProfile?.location || farmData?.location || "Haldia, West Bengal"}
              </p>

              <div className="profile-tags-row">
                <span className="profile-tag category">
                  <User size={12} /> {farmerProfile?.farmerType || "Small & Marginal Farmer"}
                </span>
                <span className="profile-tag experience">
                  <Award size={12} /> {farmerProfile?.experienceYears || "14"} Years Experience
                </span>
                <span className="profile-tag verified">
                  <CheckCircle size={12} /> PM-KISAN Verified
                </span>
              </div>
            </div>
          </div>

          {/* ================= NAVIGATION TABS ================= */}
          <div className="profile-tabs-header">
            <button
              type="button"
              className={`profile-tab-btn ${activeTab === "overview" ? "active" : ""}`}
              onClick={() => setActiveTab("overview")}
            >
              <FileText size={16} />
              <span>Overview & Credentials</span>
            </button>
            <button
              type="button"
              className={`profile-tab-btn ${activeTab === "edit" ? "active" : ""}`}
              onClick={() => setActiveTab("edit")}
            >
              <Edit2 size={16} />
              <span>Edit Details</span>
            </button>
          </div>

          {/* ================= TAB 1: OVERVIEW ================= */}
          {activeTab === "overview" && (
            <div className="profile-tab-content overview-tab">
              {/* STATS TILES */}
              <div className="profile-stats-grid">
                <div className="profile-stat-box">
                  <div className="stat-icon-circle green">
                    <Sprout size={18} />
                  </div>
                  <div>
                    <small>Cultivated Land</small>
                    <strong>{farmData?.area || 2.5} Acres</strong>
                  </div>
                </div>

                <div className="profile-stat-box">
                  <div className="stat-icon-circle amber">
                    <Calendar size={18} />
                  </div>
                  <div>
                    <small>Farming Experience</small>
                    <strong>{farmerProfile?.experienceYears || 14} Years</strong>
                  </div>
                </div>

                <div className="profile-stat-box">
                  <div className="stat-icon-circle blue">
                    <Sparkles size={18} />
                  </div>
                  <div>
                    <small>Current Crop</small>
                    <strong>{cropName}</strong>
                  </div>
                </div>

                <div className="profile-stat-box">
                  <div className="stat-icon-circle teal">
                    <ShieldCheck size={18} />
                  </div>
                  <div>
                    <small>Soil Type</small>
                    <strong>{translateSoil(farmData?.soil || "Alluvial Soil")}</strong>
                  </div>
                </div>
              </div>

              {/* FARMER BIO & NOTES */}
              <div className="profile-section-card">
                <div className="section-card-title">
                  <Info size={16} />
                  <h4>Farmer Field Note & Goals</h4>
                </div>
                <p className="profile-bio-text">
                  {farmerProfile?.bio ||
                    "Third-generation paddy farmer focusing on sustainable soil health, high-efficiency canal irrigation, and AI-driven precision crop protection."}
                </p>
              </div>

              {/* PERSONAL & CONTACT DETAILS */}
              <div className="profile-details-grid">
                <div className="profile-section-card">
                  <div className="section-card-title">
                    <Phone size={16} />
                    <h4>Contact & Registration</h4>
                  </div>
                  <div className="info-key-val-list">
                    <div className="info-row">
                      <span className="info-key">Full Name</span>
                      <strong className="info-val">{farmerProfile?.name || "Ramesh Kumar"}</strong>
                    </div>
                    <div className="info-row">
                      <span className="info-key">Mobile Phone</span>
                      <strong className="info-val">{farmerProfile?.phone || "+91 98321 45678"}</strong>
                    </div>
                    <div className="info-row">
                      <span className="info-key">Farm Location</span>
                      <strong className="info-val">
                        {farmerProfile?.location || farmData?.location || "Haldia, West Bengal"}
                      </strong>
                    </div>
                    <div className="info-row">
                      <span className="info-key">Farmer Category</span>
                      <strong className="info-val">
                        {farmerProfile?.farmerType || "Small & Marginal Farmer"}
                      </strong>
                    </div>
                  </div>
                </div>

                {/* GOVERNMENT SCHEMES & WELFARE */}
                <div className="profile-section-card">
                  <div className="section-card-title">
                    <Award size={16} />
                    <h4>Government Schemes & Direct Benefits</h4>
                  </div>
                  <div className="schemes-list">
                    <div className="scheme-item">
                      <div className="scheme-status-dot active"></div>
                      <div>
                        <strong>PM-KISAN Samman Nidhi</strong>
                        <small>₹6,000 / year &bull; Active DBT Beneficiary</small>
                      </div>
                    </div>

                    <div className="scheme-item">
                      <div className="scheme-status-dot active"></div>
                      <div>
                        <strong>Kisan Credit Card (KCC)</strong>
                        <small>Linked &bull; Low-interest crop credit authorized</small>
                      </div>
                    </div>

                    <div className="scheme-item">
                      <div className="scheme-status-dot active"></div>
                      <div>
                        <strong>Soil Health Card</strong>
                        <small>Updated March 2026 &bull; Optimal NPK & Micronutrients</small>
                      </div>
                    </div>

                    <div className="scheme-item">
                      <div className="scheme-status-dot active"></div>
                      <div>
                        <strong>PM Fasal Bima (Crop Insurance)</strong>
                        <small>Enrolled &bull; Comprehensive Kharif season coverage</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* QUICK ACTIONS ROW */}
              <div className="profile-footer-actions">
                <button
                  type="button"
                  className="profile-btn secondary"
                  onClick={onSetupFarm}
                >
                  <Sprout size={16} />
                  <span>Update Farm Land & Soil Details</span>
                  <ArrowRight size={15} />
                </button>

                <button
                  type="button"
                  className="profile-btn primary"
                  onClick={() => setActiveTab("edit")}
                >
                  <Edit2 size={16} />
                  <span>Edit Profile Information</span>
                </button>
              </div>
            </div>
          )}

          {/* ================= TAB 2: EDIT PROFILE ================= */}
          {activeTab === "edit" && (
            <form className="profile-tab-content edit-tab" onSubmit={handleSaveProfile}>
              {saveSuccess && (
                <div className="profile-save-banner">
                  <CheckCircle size={18} />
                  <span>Farmer profile saved successfully! Updating dashboard...</span>
                </div>
              )}

              <div className="edit-form-grid">
                <div className="form-group">
                  <label htmlFor="farmerName">Full Name</label>
                  <input
                    id="farmerName"
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleInputChange("name", e.target.value)}
                    placeholder="Enter farmer name"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="farmerPhone">Mobile Phone (+91)</label>
                  <input
                    id="farmerPhone"
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => handleInputChange("phone", e.target.value)}
                    placeholder="+91 98321 45678"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="farmerLocation">Village / Block / District</label>
                  <input
                    id="farmerLocation"
                    type="text"
                    value={formData.location}
                    onChange={(e) => handleInputChange("location", e.target.value)}
                    placeholder="e.g. Haldia, West Bengal"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="farmerExperience">Farming Experience (Years)</label>
                  <input
                    id="farmerExperience"
                    type="number"
                    min="1"
                    max="80"
                    value={formData.experienceYears}
                    onChange={(e) => handleInputChange("experienceYears", e.target.value)}
                    placeholder="14"
                    required
                  />
                </div>

                <div className="form-group full-width">
                  <label htmlFor="farmerType">Farmer Category / Holding Size</label>
                  <select
                    id="farmerType"
                    value={formData.farmerType}
                    onChange={(e) => handleInputChange("farmerType", e.target.value)}
                  >
                    <option value="Small & Marginal Farmer">Small & Marginal Farmer (up to 2 Hectares)</option>
                    <option value="Medium Farmer">Medium Farmer (2 to 10 Hectares)</option>
                    <option value="Large Commercial Grower">Large Commercial Grower (10+ Hectares)</option>
                    <option value="Organic Certified Producer">Organic Certified Producer</option>
                  </select>
                </div>

                <div className="form-group full-width">
                  <label htmlFor="farmerBio">Farmer Bio & Farming Focus</label>
                  <textarea
                    id="farmerBio"
                    rows="3"
                    value={formData.bio}
                    onChange={(e) => handleInputChange("bio", e.target.value)}
                    placeholder="Describe your farming methods, crop priorities, and experience..."
                  />
                </div>
              </div>

              <div className="edit-form-footer">
                <button
                  type="button"
                  className="profile-btn secondary"
                  onClick={() => setActiveTab("overview")}
                >
                  Cancel
                </button>

                <button type="submit" className="profile-btn primary">
                  <Check size={16} />
                  <span>Save Changes</span>
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export default FarmerProfileModal;
