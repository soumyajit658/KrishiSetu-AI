import { useState, useEffect, useRef } from "react";
import { 
  Bot, Send, Mic, MicOff, X, Sparkles, User, RefreshCw, 
  AlertCircle, Key, Check, ExternalLink, Trash2 
} from "lucide-react";
import { api } from "../services/api";
import { generateClientChatFallback } from "../services/chatExpertFallback";
import { useLanguage } from "../context/LanguageContext";

// Simple, robust markdown-to-JSX renderer for crisp typography
function FormattedMessage({ content }) {
  if (!content) return null;

  const lines = content.split("\n");
  const elements = [];
  let currentList = [];

  const flushList = (key) => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={`ul-${key}`} className="formatted-list">
          {currentList.map((item, idx) => (
            <li key={idx}>{formatInline(item)}</li>
          ))}
        </ul>
      );
      currentList = [];
    }
  };

  const formatInline = (text) => {
    const parts = [];
    const regex = /(\*\*.*?\*\*|\*.*?\*|`.*?`)/g;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index));
      }
      const raw = match[0];
      if (raw.startsWith("**") && raw.endsWith("**")) {
        parts.push(<strong key={match.index}>{raw.slice(2, -2)}</strong>);
      } else if (raw.startsWith("*") && raw.endsWith("*")) {
        parts.push(<em key={match.index}>{raw.slice(1, -1)}</em>);
      } else if (raw.startsWith("`") && raw.endsWith("`")) {
        parts.push(<code key={match.index} className="inline-code">{raw.slice(1, -1)}</code>);
      }
      lastIndex = match.index + raw.length;
    }
    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }
    return parts.length > 0 ? parts : text;
  };

  lines.forEach((line, index) => {
    const trimmed = line.trim();

    if (trimmed.startsWith("### ")) {
      flushList(index);
      elements.push(<h4 key={index} className="formatted-h4">{formatInline(trimmed.slice(4))}</h4>);
    } else if (trimmed.startsWith("#### ")) {
      flushList(index);
      elements.push(<h5 key={index} className="formatted-h5">{formatInline(trimmed.slice(5))}</h5>);
    } else if (trimmed.startsWith("- ") || trimmed.startsWith("• ") || trimmed.startsWith("* ")) {
      currentList.push(trimmed.slice(2));
    } else if (/^\d+\.\s/.test(trimmed)) {
      flushList(index);
      const dotIndex = trimmed.indexOf(". ");
      elements.push(
        <div key={index} className="formatted-numbered-step">
          <span className="step-num">{trimmed.slice(0, dotIndex + 1)}</span>
          <span className="step-text">{formatInline(trimmed.slice(dotIndex + 2))}</span>
        </div>
      );
    } else if (trimmed === "---") {
      flushList(index);
      elements.push(<hr key={index} className="formatted-divider" />);
    } else if (trimmed.length > 0) {
      flushList(index);
      elements.push(<p key={index} className="formatted-p">{formatInline(trimmed)}</p>);
    } else {
      flushList(index);
    }
  });

  flushList("end");
  return <div className="formatted-message-body">{elements}</div>;
}

function ChatModal({ isOpen, onClose, farmData, analysisContext, onClearContext }) {
  const { t, language, translateCrop, translateSoil } = useLanguage();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const chatEndRef = useRef(null);

  // Gemini API Key State & Status
  const [aiStatus, setAiStatus] = useState(null);
  const [showKeyConfig, setShowKeyConfig] = useState(false);
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [keySaving, setKeySaving] = useState(false);
  const [keyMsg, setKeyMsg] = useState(null);

  // Fetch AI engine status on modal open
  useEffect(() => {
    if (isOpen) {
      fetchStatus();
    }
  }, [isOpen]);

  const fetchStatus = async () => {
    try {
      const status = await api.getAIStatus();
      setAiStatus(status);
    } catch (e) {
      console.error(e);
    }
  };

  const cropName = farmData?.crop ? translateCrop(farmData.crop) : (farmData?.crop || "Crop");
  const soilName = farmData?.soil ? translateSoil(farmData.soil) : "Loamy Soil";

  // Initialize opening message based on whether analysisContext is provided and current language
  useEffect(() => {
    if (analysisContext) {
      const issue = analysisContext.primary_issue || analysisContext.overall_field_status || "Observation";
      const status = analysisContext.overall_health_status || analysisContext.overall_health || "Stable";
      let greeting = `Hello! 🌾 I've loaded your latest **Crop & Field Doctor** report for **${analysisContext.crop_name || cropName}**:\n\n• **Diagnosed Issue**: ${issue}\n• **Status**: ${status}\n\nAsk me anything about immediate treatments, organic bio-sprays, disease spread prevention, or irrigation!`;
      if (language === "hi") {
        greeting = `नमस्ते! 🌾 मैंने आपकी **${analysisContext.crop_name || cropName}** फसल की नवीनतम **फसल डॉक्टर रिपोर्ट** लोड कर ली है:\n\n• **पहचाना गया रोग**: ${issue}\n• **स्वास्थ्य स्थिति**: ${status}\n\nतुरंत उपचार, जैविक स्प्रे, रोग फैलने से रोकने या सिंचाई के बारे में मुझसे कोई भी प्रश्न पूछें!`;
      } else if (language === "bn") {
        greeting = `নমস্কার! 🌾 আমি আপনার **${analysisContext.crop_name || cropName}** ফসলের সর্বশেষ **ক্রপ ডক্টর রিপোর্ট** সংযুক্ত করেছি:\n\n• **শনাক্ত সমস্যা**: ${issue}\n• **স্বাস্থ্য পরিস্থিতি**: ${status}\n\nতাৎক্ষণিক প্রতিকার, জৈব স্প্রে, রোগ বিস্তার রোধ বা সেচ সংক্রান্ত যেকোনো প্রশ্ন করতে পারেন!`;
      }
      setMessages([{ role: "assistant", content: greeting }]);
    } else {
      let greeting = `Hello! I'm **KrishiSetu AI**, your personal farm agronomist companion. 🌾\n\nI can help you with fertilizer NPK schedules, leaf yellowing, pest remedies, irrigation timing, or sowing tips for your **${cropName}**. What would you like to know today?`;
      if (language === "hi") {
        greeting = `नमस्ते! मैं हूँ **कृषि सेतु एआई**, आपका व्यक्तिगत कृषि वैज्ञानिक साथी। 🌾\n\nमैं आपकी **${cropName}** फसल के लिए खाद-उर्वरक (NPK), पत्तियों का पीलापन, कीट नियंत्रण, सिंचाई समय या बुवाई संबंधी हर सवाल का जवाब दे सकता हूँ। आज आप क्या जानना चाहते हैं?`;
      } else if (language === "bn") {
        greeting = `নমস্কার! আমি **কৃষিসেতু এআই**, আপনার ব্যক্তিগত কৃষি পরামর্শদাতা সঙ্গী। 🌾\n\nআমি আপনার **${cropName}** ফসলের জন্য সুষম সার প্রয়োগ, হলুদ পাতা নিরাময়, পোকা দমন, সেচের সময় বা বীজ বপন সংক্রান্ত যেকোনো বিষয়ে সাহায্য করতে পারি। আজ আপনি কী জানতে চান?`;
      }
      setMessages([{ role: "assistant", content: greeting }]);
    }
  }, [analysisContext, isOpen, language]);

  // Suggested quick prompts in active language
  const quickPrompts = analysisContext
    ? [
        t("chat.quickPrompts.treatment"),
        t("chat.quickPrompts.spread"),
        t("chat.quickPrompts.organic"),
        t("chat.quickPrompts.watering"),
      ]
    : [
        t("chat.quickPrompts.fertilizer"),
        t("chat.quickPrompts.yellow"),
        t("chat.quickPrompts.irrigate"),
        t("chat.quickPrompts.pests"),
        t("chat.quickPrompts.sowing"),
        t("chat.quickPrompts.schemes"),
      ];

  useEffect(() => {
    if (isOpen) {
      chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen, loading]);

  if (!isOpen) return null;

  // Speech Recognition (Web Speech API)
  const toggleSpeechRecognition = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Voice input is not supported in this browser. Please use Chrome or Edge.");
      return;
    }

    if (isListening) {
      setIsListening(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = language === "hi" ? "hi-IN" : language === "bn" ? "bn-IN" : "en-IN";
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => setIsListening(true);
      recognition.onend = () => setIsListening(false);
      recognition.onerror = () => setIsListening(false);

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput((prev) => (prev ? `${prev} ${transcript}` : transcript));
      };

      recognition.start();
    } catch (err) {
      console.error("Speech recognition error:", err);
      setIsListening(false);
    }
  };

  const handleSend = async (textToSend) => {
    const messageText = typeof textToSend === "string" ? textToSend : input;
    if (!messageText.trim() || loading) return;

    const userMessage = { role: "user", content: messageText };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const historyToSend = messages
        .filter((_, idx) => idx > 0)
        .slice(-6);

      const reply = await api.chatWithAI(messageText, farmData, historyToSend, analysisContext, language);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch (error) {
      console.warn("ChatModal handleSend error, using instant fallback:", error);
      const fallbackReply = generateClientChatFallback(messageText, farmData, [], analysisContext, language);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: fallbackReply,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveKey = async () => {
    if (!apiKeyInput.trim()) return;
    setKeySaving(true);
    setKeyMsg(null);
    try {
      const res = await api.saveGeminiKey(apiKeyInput.trim());
      setKeyMsg({ type: "success", text: res.message || "Gemini API Key verified and saved!" });
      setApiKeyInput("");
      await fetchStatus();
      setTimeout(() => setShowKeyConfig(false), 2000);
    } catch (err) {
      const detail = err.response?.data?.detail || "Could not verify Gemini API Key. Please check the key.";
      setKeyMsg({ type: "error", text: detail });
    } finally {
      setKeySaving(false);
    }
  };

  const handleClearKey = async () => {
    setKeySaving(true);
    setKeyMsg(null);
    try {
      const res = await api.saveGeminiKey("");
      setKeyMsg({ type: "success", text: res.message || "Key removed. Using Expert System." });
      setApiKeyInput("");
      await fetchStatus();
    } catch (err) {
      setKeyMsg({ type: "error", text: "Failed to clear key." });
    } finally {
      setKeySaving(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container chat-modal" onClick={(e) => e.stopPropagation()}>
        
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-header-brand">
            <div className="modal-icon-badge ai">
              <Bot size={22} />
            </div>
            <div>
              <div className="header-title-row">
                <h3>{t("chat.title")}</h3>
                {aiStatus?.gemini_configured ? (
                  <button 
                    className="ai-engine-badge live" 
                    onClick={() => setShowKeyConfig(!showKeyConfig)}
                    title="Gemini Generative AI is active. Click to manage key."
                  >
                    <Sparkles size={11} />
                    <span>{t("chat.liveAi")}</span>
                    <Key size={10} className="badge-key-icon" />
                  </button>
                ) : (
                  <button 
                    className="ai-engine-badge expert" 
                    onClick={() => setShowKeyConfig(!showKeyConfig)}
                    title="Running on built-in Agronomic Expert Engine. Click to connect a Gemini API key."
                  >
                    <span className="badge-dot"></span>
                    <span>{t("chat.expertSystem")}</span>
                    <span className="badge-action">{t("chat.connectKey")}</span>
                  </button>
                )}
              </div>
              <p className="modal-subtext">
                {t("chat.subtext")}: {cropName} • {soilName} • {farmData?.location || "India"}
              </p>
            </div>
          </div>
          <button className="close-btn" onClick={onClose} title={t("common.close")}>
            <X size={20} />
          </button>
        </div>

        {/* Gemini Key Config Panel */}
        {showKeyConfig && (
          <div className="gemini-key-panel">
            <div className="key-panel-header">
              <div className="key-panel-title">
                <Key size={16} />
                <span>{t("chat.apiKeyConfig")}</span>
              </div>
              <button className="close-mini-btn" onClick={() => setShowKeyConfig(false)} title="Close panel" aria-label="Close panel">
                <X size={15} />
              </button>
            </div>
            <p className="key-panel-desc">
              {t("chat.apiKeyDesc")} 
              {" "}<a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer">
                {t("chat.getFreeKey")} <ExternalLink size={12} style={{ display: "inline", verticalAlign: "middle" }} />
              </a>
            </p>
            <div className="key-input-row">
              <input
                type="password"
                placeholder={aiStatus?.key_preview ? `Current: ${aiStatus.key_preview}` : t("chat.keyPlaceholder")}
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                disabled={keySaving}
              />
              <button 
                className="save-key-btn" 
                onClick={handleSaveKey} 
                disabled={keySaving || !apiKeyInput.trim()}
              >
                {keySaving ? <RefreshCw size={14} className="spinning" /> : <Check size={14} />}
                <span>{keySaving ? t("chat.testing") : t("chat.verifyAndSave")}</span>
              </button>
              {aiStatus?.gemini_configured && (
                <button 
                  className="clear-key-btn" 
                  onClick={handleClearKey} 
                  disabled={keySaving}
                  title="Remove Key"
                >
                  <Trash2 size={15} />
                </button>
              )}
            </div>
            {keyMsg && (
              <div className={`key-msg ${keyMsg.type}`}>
                {keyMsg.type === "success" ? <Check size={14} /> : <AlertCircle size={14} />}
                <span>{keyMsg.text}</span>
              </div>
            )}
          </div>
        )}

        {/* Context banner if analysisContext is loaded */}
        {analysisContext && (
          <div className="active-context-banner">
            <div className="active-context-text">
              <AlertCircle size={15} />
              <span>
                <strong>{t("chat.activeReport")}:</strong> {analysisContext.crop_name || cropName} • {analysisContext.primary_issue || "Observation"} ({analysisContext.severity || "Reported"})
              </span>
            </div>
            {onClearContext && (
              <button 
                className="clear-context-btn" 
                onClick={onClearContext} 
                title="Clear report context to ask general farm questions"
              >
                <X size={13} />
                <span>{t("chat.generalChat")}</span>
              </button>
            )}
          </div>
        )}

        {/* Quick prompt chips */}
        <div className="quick-prompts-bar">
          <Sparkles size={14} className="sparkle-icon" />
          <div className="chips-scroller">
            {quickPrompts.map((prompt, idx) => (
              <button
                key={idx}
                className="chip-btn"
                onClick={() => handleSend(prompt)}
                disabled={loading}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Message Area */}
        <div className="chat-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-bubble-row ${msg.role}`}>
              <div className="avatar-circle">
                {msg.role === "assistant" ? <Bot size={18} /> : <User size={18} />}
              </div>
              <div className="chat-bubble">
                {msg.role === "assistant" ? (
                  <FormattedMessage content={msg.content} />
                ) : (
                  <div className="message-content" style={{ whiteSpace: "pre-line" }}>
                    {msg.content}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="chat-bubble-row assistant">
              <div className="avatar-circle">
                <Bot size={18} />
              </div>
              <div className="chat-bubble typing-bubble">
                <RefreshCw size={16} className="spinning" />
                <span>{t("chat.analyzing")}</span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Bar */}
        <form
          className="chat-input-form"
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
        >
          <button
            type="button"
            className={`voice-btn ${isListening ? "active" : ""}`}
            onClick={toggleSpeechRecognition}
            title={isListening ? "Listening... click to stop" : "Speak your question"}
          >
            {isListening ? <MicOff size={19} /> : <Mic size={19} />}
          </button>

          <input
            type="text"
            placeholder={
              isListening
                ? t("chat.inputListening")
                : analysisContext
                ? t("chat.reportInputPlaceholder")
                : t("chat.inputPlaceholder")
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />

          <button
            type="submit"
            className="send-btn"
            disabled={!input.trim() || loading}
            title={t("chat.send")}
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatModal;
