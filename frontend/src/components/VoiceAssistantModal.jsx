import { useState, useEffect, useRef } from "react";
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Square,
  RotateCcw,
  X,
  Sparkles,
  CloudSun,
  Droplets,
  Sprout,
  AlertCircle,
  Check,
  Pause,
  Play,
  ArrowRight,
  HelpCircle,
  Radio,
  RefreshCw,
  Cpu,
  AudioWaveform,
  Languages,
} from "lucide-react";
import { api } from "../services/api";
import { useLanguage } from "../context/LanguageContext";

const QUICK_VOICE_QUESTIONS = {
  bn: [
    { text: "আমার ধানের পাতাগুলো হলুদ হয়ে যাচ্ছে, আমি কী করব?", label: "🌾 পাতা হলুদ হচ্ছে কেন?" },
    { text: "আজ কি আমার জমিতে সেচ দেওয়া উচিত?", label: "💧 আজ জমিতে জল দেব?" },
    { text: "আগামীকাল বৃষ্টি হলে কি সার প্রয়োগ করা ঠিক হবে?", label: "🌧️ বৃষ্টির আগে সার দেব?" },
    { text: "ধান কাটার পর জমিতে কোন ফসল লাগানো লাভজনক?", label: "🌱 ধানের পর কোন ফসল?" },
    { text: "গাছের পাতায় বাদামী দাগ হয়েছে, কী স্প্রে করব?", label: "🍂 পাতার বাদামী দাগ?" },
    { text: "ফসলে পোকার আক্রমণ রুখতে কী স্প্রে করব?", label: "🐛 পোকা দমনের উপায়?" },
  ],
  hi: [
    { text: "मेरी फसल में पत्तियां पीली पड़ रही हैं, क्या करूं?", label: "🌾 पत्तियां पीली क्यों हैं?" },
    { text: "क्या आज मुझे अपने खेत में पानी देना चाहिए?", label: "💧 आज सिंचाई करें या नहीं?" },
    { text: "अगर कल बारिश होगी तो क्या यूरिया डालना चाहिए?", label: "🌧️ बारिश से पहले खाद?" },
    { text: "धान के बाद कौन सी फसल लगाना सबसे अच्छा रहेगा?", label: "🌱 अगली फसल कौन सी?" },
    { text: "पत्तियों पर भूरे धब्बे हैं, कौन सी दवा छिड़कें?", label: "🍂 पत्तियों पर भूरे धब्बे?" },
    { text: "कीटों और सुंडी से बचाव के लिए क्या छिड़काव करें?", label: "🐛 कीट नियंत्रण के उपाय?" },
  ],
  en: [
    { text: "Leaves on my crop are turning yellow, what should I do?", label: "🌾 Why leaves yellow?" },
    { text: "Should I irrigate or water my crop today?", label: "💧 Should I water today?" },
    { text: "It is going to rain tomorrow, should I apply fertilizer?", label: "🌧️ Fertilize before rain?" },
    { text: "What crop should I grow after harvesting rice?", label: "🌱 Crop after rice?" },
    { text: "There are brown spots on my leaves, how to treat it?", label: "🍂 Brown spots remedy" },
    { text: "How to protect my crop from insect pests organically?", label: "🐛 Organic pest remedy" },
  ],
};

// Client-side real-time script & phonetics detector
function detectClientLanguage(text, defaultLang = "en") {
  if (!text || !text.trim()) return defaultLang;
  const str = text.trim();
  
  // 1. Bengali Unicode block (\u0980-\u09FF)
  if (/[\u0980-\u09FF]/.test(str)) return "bn";
  
  // 2. Devanagari Unicode block (\u0900-\u097F)
  if (/[\u0900-\u097F]/.test(str)) return "hi";

  const lower = str.toLowerCase();

  // 3. Multi-word phrase matching
  const hiPhrases = /kya karu|kya kare|kya dale|kaise kare|kab dena|pani kab|khad kab|kaun si|konsi dawa|peela pad|peeli ho|keeda lag|fasal me|khet me|kisan bhai|kya upaye|rog laga/i;
  const bnPhrases = /ki korbo|ki vabe|kivabe|dhaner pata|pani kobe|agami kal|jol debo|sar debo|poka legeche|patay daag|rog legeche/i;
  const enPhrases = /should i|what should|how to|when should|can i|do i need|my crop is|crop health/i;

  let hiScore = hiPhrases.test(lower) ? 5.0 : 0;
  let bnScore = bnPhrases.test(lower) ? 5.0 : 0;
  let enScore = enPhrases.test(lower) ? 5.0 : 0;

  // 4. Token & Keyword scoring
  const hiMatches = lower.match(/\b(meri|mera|mere|fasal|faslo|gehu|dhan|kya|karu|kare|karna|peela|peeli|peele|pani|paani|khad|kisan|keede|keeda|sundi|barish|sinchai|sinchayi|kab|kitna|kitni|dena|dale|chahiye|chaiye|cheiya|main|mein|me|hai|hain|khet|dawa|dawai|chhidkaw|beej|buwai|mitti|upchar|batao|bataiye|namaste|namaskar|namaskaar|dhanyawad|shukriya|patte|pattiya|rog)\b/g);
  const bnMatches = lower.match(/\b(amar|amader|dhaner|dhane|dhan|pata|patagulo|patay|holud|ki|korbo|kore|kora|shorisa|alu|chash|pani|jol|brishti|agami|agamikal|rog|poka|sar|debo|uchit|jomite|jomi|kobe|kemon|kivabe|achhe|ache|hobe|sesh|fosol|chara|beej|sech|daag)\b/g);
  const enMatches = lower.match(/\b(tomorrow|yesterday|yellowing|infection|symptoms|advice|suggestion|recommend|harvesting|irrigate|fertilizer|spray|pesticide|fungicide)\b/g);

  if (hiMatches) hiScore += hiMatches.length * 1.8;
  if (bnMatches) bnScore += bnMatches.length * 1.8;
  if (enMatches) enScore += enMatches.length * 1.2;

  if (hiScore >= 1.5 && hiScore >= bnScore && hiScore >= enScore) return "hi";
  if (bnScore >= 1.5 && bnScore > hiScore && bnScore >= enScore) return "bn";
  if (enScore >= 2.0 && enScore > hiScore && enScore > bnScore) return "en";
  if (hiScore > 0) return "hi";

  return defaultLang;
}

const LANGUAGE_LABELS = {
  bn: "Bengali (বাংলা)",
  hi: "Hindi (हिन्दी)",
  en: "English",
};

// Best Natural Voice Finder for Web Speech Synthesis
function getBestVoiceForLang(lang) {
  if (!("speechSynthesis" in window)) return null;
  const voices = window.speechSynthesis.getVoices();
  if (!voices || voices.length === 0) return null;

  if (lang === "bn") {
    return (
      voices.find((v) => v.name.includes("Google") && (v.lang.startsWith("bn") || v.name.toLowerCase().includes("bengali") || v.name.toLowerCase().includes("bangla"))) ||
      voices.find((v) => v.name.includes("Natural") && v.lang.startsWith("bn")) ||
      voices.find((v) => v.lang.startsWith("bn") || v.lang === "bn-IN" || v.lang === "bn_IN" || v.lang === "bn_BD") ||
      null
    );
  }

  if (lang === "hi") {
    return (
      voices.find((v) => v.name.includes("Google") && (v.lang.startsWith("hi") || v.name.toLowerCase().includes("hindi"))) ||
      voices.find((v) => v.name.includes("Natural") && v.lang.startsWith("hi")) ||
      voices.find((v) => v.lang.startsWith("hi") || v.lang === "hi-IN" || v.lang === "hi_IN") ||
      null
    );
  }

  return (
    voices.find((v) => v.name.includes("Natural") && (v.lang.startsWith("en-IN") || v.lang === "en-IN")) ||
    voices.find((v) => v.name.includes("Google") && v.lang.startsWith("en")) ||
    voices.find((v) => v.lang.startsWith("en-IN")) ||
    voices.find((v) => v.lang.startsWith("en")) ||
    null
  );
}

function VoiceAssistantModal({ isOpen, onClose, farmData, fieldContext, onOpenDoctor }) {
  const { language: appLanguage, translateCrop, translateSoil } = useLanguage();

  // Real automatically detected language: 'bn' | 'hi' | 'en'
  const [detectedLang, setDetectedLang] = useState(() => {
    return appLanguage === "bn" ? "bn" : appLanguage === "hi" ? "hi" : "en";
  });

  // Explicit voice language mode: 'auto' | 'hi' | 'bn' | 'en'
  const [voiceLangMode, setVoiceLangMode] = useState("auto");

  const handleSetLanguageMode = (mode) => {
    setVoiceLangMode(mode);
    if (mode !== "auto") {
      setDetectedLang(mode);
    }
  };

  // Explicit real state machine: 'idle' | 'listening' | 'processing' | 'thinking' | 'speaking' | 'finished' | 'error'
  const [voiceState, setVoiceState] = useState("idle");
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [micSupported, setMicSupported] = useState(true);

  // Conversational history
  const [conversationHistory, setConversationHistory] = useState([]);

  const recognitionRef = useRef(null);
  const silenceTimerRef = useRef(null);
  const audioPlayerRef = useRef(null);
  const isProcessingRef = useRef(false);

  // Pre-load voices on mount
  useEffect(() => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.getVoices();
      window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices();
      };
    }
  }, []);

  // Sync default modal language with app language if app changes or modal opens
  useEffect(() => {
    const validLang = appLanguage === "bn" || appLanguage === "hi" || appLanguage === "en" ? appLanguage : "en";
    if (voiceLangMode === "auto") {
      setDetectedLang(validLang);
    }
  }, [appLanguage, isOpen, voiceLangMode]);

  // Clean up audio & recognition when closing
  useEffect(() => {
    if (!isOpen) {
      stopAllVoiceActivity();
      setVoiceState("idle");
      setTranscript("");
      setResponse(null);
      setErrorMessage(null);
      isProcessingRef.current = false;
    }
  }, [isOpen]);

  const stopAllAudio = () => {
    if (audioPlayerRef.current) {
      try {
        audioPlayerRef.current.pause();
        audioPlayerRef.current.currentTime = 0;
      } catch (e) {
        /* ignore */
      }
    }
    if ("speechSynthesis" in window) {
      try {
        window.speechSynthesis.cancel();
      } catch (e) {
        /* ignore */
      }
    }
    setIsPlayingAudio(false);
  };

  const stopAllVoiceActivity = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch (e) {
        /* ignore */
      }
    }
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
    }
    stopAllAudio();
  };

  // 1. Start Listening
  const startListening = () => {
    stopAllVoiceActivity();
    isProcessingRef.current = false;
    setErrorMessage(null);
    setResponse(null);
    setTranscript("");

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setMicSupported(false);
      setErrorMessage(
        detectedLang === "bn"
          ? "আপনার ব্রাউজারে ভয়েস রেকর্ডিং সমর্থিত নয়। অনুগ্রহ করে নিচের সাজেস্টেড প্রশ্নে ট্যাপ করুন।"
          : detectedLang === "hi"
          ? "आपके ब्राउज़र में वॉयस इनपुट समर्थित नहीं है। कृपया नीचे दिए गए प्रश्नों पर टैप करें।"
          : "Voice input is not supported in this browser. Please tap any quick question below."
      );
      setVoiceState("error");
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;

      let langTag = "hi-IN";
      if (voiceLangMode === "hi") {
        langTag = "hi-IN";
      } else if (voiceLangMode === "bn") {
        langTag = "bn-IN";
      } else if (voiceLangMode === "en") {
        langTag = "en-IN";
      } else {
        if (detectedLang === "bn") langTag = "bn-IN";
        else if (detectedLang === "hi") langTag = "hi-IN";
        else if (detectedLang === "en") langTag = "en-IN";
        else langTag = "hi-IN";
      }
      recognition.lang = langTag;
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setVoiceState("listening");
      };

      recognition.onresult = (event) => {
        let currentTranscript = "";
        for (let i = 0; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript;
        }
        setTranscript(currentTranscript);

        // Instant automatic language recognition on live speech if in auto mode
        if (currentTranscript.trim() && voiceLangMode === "auto") {
          const liveDetected = detectClientLanguage(currentTranscript, detectedLang);
          setDetectedLang(liveDetected);
        }

        // Auto-submit after 2.0s of silence
        if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
        silenceTimerRef.current = setTimeout(() => {
          if (currentTranscript.trim() && !isProcessingRef.current) {
            stopListeningAndProcess(currentTranscript);
          }
        }, 2000);
      };

      recognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        if (event.error === "not-allowed" || event.error === "permission-denied") {
          setErrorMessage(
            detectedLang === "bn"
              ? "মাইক্রোফোন অনুমতি দেওয়া হয়নি। অনুগ্রহ করে ব্রাউজার সেটিংসে মাইক্রোফোন অনুমতি দিন।"
              : detectedLang === "hi"
              ? "माइक्रोफ़ोन की अनुमति नहीं मिली। कृपया ब्राउज़र सेटिंग्स में माइक्रोफ़ोन की अनुमति दें।"
              : "Microphone permission was denied. Please allow microphone access in your browser."
          );
          setVoiceState("error");
        } else if (event.error === "no-speech") {
          // Keep active
        } else {
          setErrorMessage(
            detectedLang === "bn"
              ? "কথা স্পষ্ট শোনা যায়নি। অনুগ্রহ করে আবার বলুন বা নিচে ট্যাপ করুন।"
              : detectedLang === "hi"
              ? "आवाज स्पष्ट नहीं सुनाई दी। कृपया पुनः बोलें या नीचे दिए सवाल चुनें।"
              : "Could not clearly understand speech. Please try speaking again."
          );
          setVoiceState("error");
        }
      };

      recognition.onend = () => {
        if (voiceState === "listening" && transcript.trim() && !isProcessingRef.current) {
          stopListeningAndProcess(transcript);
        }
      };

      recognition.start();
    } catch (err) {
      console.error("Speech recognition start failed:", err);
      setErrorMessage("Could not access microphone. Please check permissions and try again.");
      setVoiceState("error");
    }
  };

  // 2. Stop Listening -> Processing -> Thinking -> Backend Request
  const stopListeningAndProcess = async (textToProcess) => {
    if (isProcessingRef.current) return;
    isProcessingRef.current = true;

    if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        /* ignore */
      }
    }

    const query = (textToProcess || transcript || "").trim();
    if (!query) {
      setVoiceState("idle");
      isProcessingRef.current = false;
      return;
    }

    // Step 1: Processing state (audio finalized & transcribing)
    setVoiceState("processing");

    // Automatically detect or sync language
    const targetLang = voiceLangMode !== "auto" ? voiceLangMode : detectClientLanguage(query, detectedLang);
    setDetectedLang(targetLang);

    // Step 2: Transition to Understanding/Thinking while sending to backend
    setTimeout(async () => {
      setVoiceState("thinking");

      try {
        const result = await api.processVoice(
          query,
          voiceLangMode !== "auto" ? voiceLangMode : "auto", // Explicit mode or auto
          farmData,
          fieldContext,
          conversationHistory
        );

        if (result?.detected_language && voiceLangMode === "auto") {
          setDetectedLang(result.detected_language);
        }

        setResponse(result);

        // Update conversational history
        setConversationHistory((prev) => [
          ...prev.slice(-3),
          { role: "user", content: query },
          { role: "model", content: result.clean_speech_text || result.response_text || "" },
        ]);

        // Step 3: Trigger Speaking (Audio Playback)
        playVoiceAudio(result);
      } catch (err) {
        console.error("Voice process error:", err);
        setErrorMessage("Service is temporarily busy. Please tap try again.");
        setVoiceState("error");
      } finally {
        isProcessingRef.current = false;
      }
    }, 400);
  };

  // 3. Spoken Audio Playback (Speaking -> Finished)
  const playVoiceAudio = (voiceResult) => {
    stopAllAudio();

    // Strategy 1: Google TTS Base64 Audio Stream
    if (voiceResult?.audio_base64) {
      try {
        const audioSrc = `data:audio/mp3;base64,${voiceResult.audio_base64}`;
        const audio = new Audio(audioSrc);
        audio.volume = 1.0;
        audioPlayerRef.current = audio;

        audio.onplay = () => {
          setVoiceState("speaking");
          setIsPlayingAudio(true);
        };

        audio.onended = () => {
          setVoiceState("finished");
          setIsPlayingAudio(false);
        };

        audio.onerror = () => {
          console.warn("Base64 audio play error, falling back to speech synthesis");
          playSpeechSynthesisFallback(voiceResult);
        };

        const playPromise = audio.play();
        if (playPromise !== undefined) {
          playPromise.catch((err) => {
            console.warn("Audio autoplay blocked by browser, using speech synthesis fallback:", err);
            playSpeechSynthesisFallback(voiceResult);
          });
        }
        return;
      } catch (audioErr) {
        console.warn("Audio element init failed:", audioErr);
      }
    }

    // Strategy 2: Web Speech Synthesis API Fallback
    playSpeechSynthesisFallback(voiceResult);
  };

  const playSpeechSynthesisFallback = (voiceResult) => {
    if (!("speechSynthesis" in window)) {
      setVoiceState("finished");
      return;
    }

    try {
      window.speechSynthesis.cancel();
      const textToSpeak = voiceResult?.clean_speech_text || voiceResult?.response_text || "";
      if (!textToSpeak) {
        setVoiceState("finished");
        return;
      }

      const resLang = voiceResult?.language || detectedLang || "en";
      const bestVoice = getBestVoiceForLang(resLang);

      const sanitized = textToSpeak
        .replace(/[#*`_~⚠️🚨💡🔍🌾🐛💧🌱📋🧪🏛️•-]/g, " ")
        .replace(/\s+/g, " ")
        .trim();

      const utterance = new SpeechSynthesisUtterance(sanitized);

      if (resLang === "bn") {
        utterance.lang = "bn-IN";
      } else if (resLang === "hi") {
        utterance.lang = "hi-IN";
      } else {
        utterance.lang = "en-IN";
      }

      if (bestVoice) {
        utterance.voice = bestVoice;
      }

      utterance.volume = 1.0;
      utterance.rate = 0.94;
      utterance.pitch = 1.0;

      utterance.onstart = () => {
        setVoiceState("speaking");
        setIsPlayingAudio(true);
      };

      utterance.onended = () => {
        setVoiceState("finished");
        setIsPlayingAudio(false);
      };

      utterance.onerror = () => {
        setVoiceState("finished");
        setIsPlayingAudio(false);
      };

      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.warn("SpeechSynthesis error:", e);
      setVoiceState("finished");
      setIsPlayingAudio(false);
    }
  };

  // Handler: Stop Audio Immediately -> Finished
  const handleStopAudio = () => {
    stopAllAudio();
    setVoiceState("finished");
  };

  // Handler: Replay Audio from Start -> Speaking
  const handleReplayAudio = () => {
    if (response) {
      playVoiceAudio(response);
    }
  };

  // Handler: Try Again -> Reset & Start Listening
  const handleTryAgain = () => {
    stopAllVoiceActivity();
    setResponse(null);
    setTranscript("");
    startListening();
  };

  const handleQuickQuestionTap = (item) => {
    setTranscript(item.text);
    stopListeningAndProcess(item.text);
  };

  if (!isOpen) return null;

  const currentCrop = farmData?.crop ? translateCrop(farmData.crop) : (farmData?.crop || "Crop");
  const currentLocation = farmData?.location || "India";
  const quickList = QUICK_VOICE_QUESTIONS[detectedLang] || QUICK_VOICE_QUESTIONS.en;
  const detectedLanguageDisplayName = LANGUAGE_LABELS[detectedLang] || "Auto Detected";

  // State Stepper config
  const stateSteps = [
    { key: "idle", label: detectedLang === "bn" ? "অপেক্ষা" : detectedLang === "hi" ? "तैयार" : "Idle" },
    { key: "listening", label: detectedLang === "bn" ? "শুনছি" : detectedLang === "hi" ? "सुन रहे हैं" : "Listening" },
    { key: "processing", label: detectedLang === "bn" ? "প্রসেসিং" : detectedLang === "hi" ? "प्रोसेसिंग" : "Processing" },
    { key: "thinking", label: detectedLang === "bn" ? "বিশ্লেষণ" : detectedLang === "hi" ? "सोच रहा है" : "Thinking" },
    { key: "speaking", label: detectedLang === "bn" ? "বলছে" : detectedLang === "hi" ? "बोल रहा है" : "Speaking" },
    { key: "finished", label: detectedLang === "bn" ? "সম্পন্ন" : detectedLang === "hi" ? "पूर्ण" : "Finished" },
  ];

  return (
    <div className="modal-backdrop voice-modal-backdrop" onClick={onClose}>
      <div
        className="modal-card voice-assistant-card"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        {/* ================= HEADER ================= */}
        <div className="voice-modal-header">
          <div className="voice-header-left">
            <div className="voice-logo-badge">
              <Mic size={22} className="voice-logo-icon" />
            </div>
            <div>
              <div className="voice-title-row">
                <h3>KrishiBandhu(AI)</h3>
                <span className="voice-ai-chip">Voice AI</span>
                {detectedLang && (
                  <span className="live-lang-badge">
                    <span className="detected-dot"></span>
                    {detectedLanguageDisplayName}
                  </span>
                )}
              </div>
              <p className="voice-subtitle">
                {detectedLang === "bn"
                  ? "মুখে যেকোনো ভাষায় বলুন, কৃশিবন্ধু(AI) স্বয়ংক্রিয়ভাবে বুঝে কণ্ঠস্বরে উত্তর দেবে"
                  : detectedLang === "hi"
                  ? "किसी भी भाषा में बोलें, कृषिबंधु(AI) स्वतः समझकर उसी भाषा में आवाज में उत्तर देगा"
                  : "Speak in Hindi, Bengali, or English — KrishiBandhu(AI) auto-detects and speaks back"}
              </p>
            </div>
          </div>

          <button className="close-btn modal-close-btn" onClick={onClose} aria-label="Close KrishiBandhu Voice" title="Close">
            <X size={20} />
          </button>
        </div>

        {/* ================= LANGUAGE SELECTOR BAR ================= */}
        <div className="voice-lang-bar">
          <div className="lang-bar-title">
            <Languages size={16} />
            <span>
              {detectedLang === "bn"
                ? "ভাষা নির্বাচন (ভয়েস মোড):"
                : detectedLang === "hi"
                ? "भाषा चुनें (वॉयस मोड):"
                : "Voice Language Mode:"}
            </span>
          </div>
          <div className="lang-bar-options">
            <button
              type="button"
              className={`voice-lang-btn ${voiceLangMode === "auto" ? "active" : ""}`}
              onClick={() => handleSetLanguageMode("auto")}
              title="Automatically detect whether you speak Hindi, Bengali, or English"
            >
              <span className="mode-badge">Auto</span>
              <span>{LANGUAGE_LABELS[detectedLang] || "Auto Detect"}</span>
            </button>
            <button
              type="button"
              className={`voice-lang-btn ${voiceLangMode === "hi" ? "active" : ""}`}
              onClick={() => handleSetLanguageMode("hi")}
              title="Force Hindi (हिन्दी) recognition"
            >
              🇮🇳 हिन्दी (Hindi)
            </button>
            <button
              type="button"
              className={`voice-lang-btn ${voiceLangMode === "bn" ? "active" : ""}`}
              onClick={() => handleSetLanguageMode("bn")}
              title="Force Bengali (বাংলা) recognition"
            >
              বাংলা (Bengali)
            </button>
            <button
              type="button"
              className={`voice-lang-btn ${voiceLangMode === "en" ? "active" : ""}`}
              onClick={() => handleSetLanguageMode("en")}
              title="Force English recognition"
            >
              English
            </button>
          </div>
        </div>

        {/* ================= REAL STATE STEPPER BAR ================= */}
        <div className="voice-state-stepper-container">
          <div className="voice-stepper-bar">
            {stateSteps.map((step, idx) => {
              const isActive = voiceState === step.key;
              const isPast =
                (voiceState === "listening" && idx < 1) ||
                (voiceState === "processing" && idx < 2) ||
                (voiceState === "thinking" && idx < 3) ||
                (voiceState === "speaking" && idx < 4) ||
                (voiceState === "finished" && idx < 5);

              return (
                <div
                  key={step.key}
                  className={`stepper-node ${isActive ? "active" : ""} ${isPast ? "passed" : ""}`}
                >
                  <span className="step-dot"></span>
                  <span className="step-text">{step.label}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* ================= LIVE FARM CONTEXT BANNER ================= */}
        <div className="voice-context-pillbar">
          <div className="ctx-item">
            <Sprout size={14} />
            <span>{currentCrop}</span>
          </div>
          <div className="ctx-item">
            <span>📍 {currentLocation}</span>
          </div>
          <div className="ctx-item">
            <Droplets size={14} />
            <span>{translateSoil(farmData?.soil || "Alluvial Soil")}</span>
          </div>
          {fieldContext?.primary_issue && (
            <div className="ctx-item ctx-alert">
              <span>⚠️ {fieldContext.primary_issue}</span>
            </div>
          )}
        </div>

        {/* ================= MAIN INTERACTION STAGE ================= */}
        <div className="voice-interaction-stage">
          {/* 1. IDLE STATE */}
          {voiceState === "idle" && (
            <div className="voice-state-view idle-view">
              <button
                className="voice-big-mic-btn idle-pulse"
                onClick={startListening}
                title="Tap to speak with KrishiBandhu(AI)"
              >
                <div className="mic-inner-circle">
                  <Mic size={48} />
                </div>
                <div className="mic-wave-ring ring-1"></div>
                <div className="mic-wave-ring ring-2"></div>
              </button>

              <div className="voice-state-prompt">
                <h2>
                  {detectedLang === "bn"
                    ? "ভয়েস শুরু করতে মাইকে ট্যাপ করুন"
                    : detectedLang === "hi"
                    ? "बोलने के लिए माइक दबाएं"
                    : "Tap Microphone to Speak"}
                </h2>
                <p>
                  {detectedLang === "bn"
                    ? "আপনার ধানের পাতা, সেচ, সার, রোগ বা পরবর্তী ফসল সম্পর্কে বাংলা, হিন্দি বা ইংরেজিতে মুখে বলুন"
                    : detectedLang === "hi"
                    ? "अपनी फसल की सिंचाई, खाद, पत्तियों का पीलापन या कीट के बारे में हिन्दी, বাংলা या English में बोलें"
                    : "Ask anything about watering, fertilizers, yellow leaves, or pest protection in Hindi, Bengali, or English"}
                </p>
              </div>
            </div>
          )}

          {/* 2. LISTENING STATE (Microphone Listening Animation) */}
          {voiceState === "listening" && (
            <div className="voice-state-view listening-view">
              <button
                className="voice-big-mic-btn active-recording"
                onClick={() => stopListeningAndProcess()}
                title="Tap when finished speaking"
              >
                <div className="mic-inner-circle recording">
                  <Mic size={48} />
                </div>
                <div className="mic-wave-ring active-ring-1"></div>
                <div className="mic-wave-ring active-ring-2"></div>
                <div className="mic-wave-ring active-ring-3"></div>
              </button>

              <div className="voice-listening-status">
                <div className="status-badge-row">
                  <span className="live-rec-badge">
                    <span className="red-pulse-dot"></span>
                    {detectedLang === "bn" ? "শুনছি..." : detectedLang === "hi" ? "सुन रहे हैं..." : "Listening..."}
                  </span>
                  <span className="detected-lang-pill-mini">
                    {detectedLanguageDisplayName}
                  </span>
                </div>

                {/* Live Current Transcript */}
                <div className="live-speech-box">
                  <p className="live-speech-text">
                    {transcript || (
                      <span className="placeholder-text">
                        {detectedLang === "bn"
                          ? "আপনার প্রশ্নটি পরিষ্কারভাবে বলুন..."
                          : detectedLang === "hi"
                          ? "अपना सवाल साफ आवाज में बोलें..."
                          : "Speak your question clearly now..."}
                      </span>
                    )}
                  </p>
                </div>

                <button
                  className="voice-finish-btn"
                  onClick={() => stopListeningAndProcess()}
                >
                  <Check size={18} />
                  {detectedLang === "bn" ? "বলা শেষ হয়েছে" : detectedLang === "hi" ? "बोल लिया (पूरा हुआ)" : "Finish Speaking"}
                </button>
              </div>
            </div>
          )}

          {/* 3. PROCESSING STATE (Subtle Processing Indicator) */}
          {voiceState === "processing" && (
            <div className="voice-state-view processing-view">
              <div className="voice-subtle-indicator">
                <div className="subtle-spinner"></div>
                <Radio size={24} className="subtle-pulse-icon" />
              </div>

              <div className="voice-processing-text">
                <h3>
                  {detectedLang === "bn"
                    ? "ভয়েস প্রসেসিং ও টেক্সট রূপান্তর..."
                    : detectedLang === "hi"
                    ? "आवाज रूपांतरित व प्रोसेस हो रही है..."
                    : "Processing voice input..."}
                </h3>
                {transcript && (
                  <div className="current-transcript-strip">
                    <span className="transcript-label">
                      {detectedLang === "bn" ? "আপনার প্রশ্ন:" : detectedLang === "hi" ? "आपका सवाल:" : "Transcript:"}
                    </span>
                    <p className="user-query-preview">"{transcript}"</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 4. UNDERSTANDING / THINKING STATE */}
          {voiceState === "thinking" && (
            <div className="voice-state-view thinking-view">
              <div className="voice-thinking-spinner">
                <div className="spinner-core">
                  <Sparkles size={32} className="sparkle-spin" />
                </div>
                <div className="radar-ripple ripple-1"></div>
                <div className="radar-ripple ripple-2"></div>
              </div>

              <div className="voice-processing-text">
                <h3>
                  {detectedLang === "bn"
                    ? "মাঠ, মাটি ও আবহাওয়ার তথ্য বিশ্লেষণ করা হচ্ছে..."
                    : detectedLang === "hi"
                    ? "खेत, मौसम व मिट्टी की जांच हो रही है..."
                    : "KrishiBandhu(AI) is analyzing your query..."}
                </h3>
                {transcript && (
                  <div className="current-transcript-strip">
                    <span className="transcript-label">
                      {detectedLang === "bn" ? "আপনার প্রশ্ন:" : detectedLang === "hi" ? "आपका सवाल:" : "Transcript:"}
                    </span>
                    <p className="user-query-preview">"{transcript}"</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 5. SPEAKING STATE & 6. FINISHED STATE */}
          {(voiceState === "speaking" || voiceState === "finished") && response && (
            <div className="voice-state-view speaking-view">
              {/* Spoken Equalizer / Waveform Animation */}
              <div className="equalizer-banner">
                <div className={`audio-equalizer ${voiceState === "speaking" ? "animating" : "paused"}`}>
                  <span className="eq-bar bar-1"></span>
                  <span className="eq-bar bar-2"></span>
                  <span className="eq-bar bar-3"></span>
                  <span className="eq-bar bar-4"></span>
                  <span className="eq-bar bar-5"></span>
                  <span className="eq-bar bar-6"></span>
                  <span className="eq-bar bar-7"></span>
                  <span className="eq-bar bar-8"></span>
                </div>

                <span className="equalizer-status-text">
                  {voiceState === "speaking"
                    ? detectedLang === "bn"
                      ? "🔊 কৃশিবন্ধু(AI) উত্তর দিচ্ছে..."
                      : detectedLang === "hi"
                      ? "🔊 कृषिबंधु(AI) बोल रहा है..."
                      : "🔊 KrishiBandhu(AI) is speaking..."
                    : detectedLang === "bn"
                    ? "✓ উত্তর প্রদান সম্পন্ন"
                    : detectedLang === "hi"
                    ? "✓ उत्तर पूरा हुआ"
                    : "✓ Spoken answer finished"}
                </span>

                <div className="equalizer-controls">
                  {voiceState === "speaking" ? (
                    <button
                      className="eq-btn stop-action-btn"
                      onClick={handleStopAudio}
                      title="Stop Audio"
                      aria-label="Stop Audio"
                    >
                      <Square size={16} fill="currentColor" />
                    </button>
                  ) : (
                    <button
                      className="eq-btn"
                      onClick={handleReplayAudio}
                      title="Replay Audio"
                      aria-label="Replay Audio"
                    >
                      <Play size={16} fill="currentColor" />
                    </button>
                  )}
                </div>
              </div>

              {/* Current Transcript Box with Detected Language */}
              <div className="voice-farmer-query-box">
                <div className="query-box-top">
                  <span className="query-label">
                    {detectedLang === "bn" ? "আপনার প্রশ্ন (Transcript):" : detectedLang === "hi" ? "आपका सवाल (Transcript):" : "Current Transcript:"}
                  </span>
                  <span className="lang-tag-pill">{response.language_name || detectedLanguageDisplayName}</span>
                </div>
                <p className="query-text">"{response.query || transcript}"</p>
              </div>

              {/* AI Response Card */}
              <div className="voice-response-card">
                <div className="response-header">
                  <div className="response-title-group">
                    <Sprout size={18} className="response-icon" />
                    <strong>
                      {detectedLang === "bn"
                        ? "কৃশিবন্ধু(AI) পরামর্শ"
                        : detectedLang === "hi"
                        ? "कृषिबंधु(AI) सलाह"
                        : "KrishiBandhu(AI) Advisory"}
                    </strong>
                  </div>
                  <span className="voice-status-chip">
                    {voiceState === "speaking" ? "Speaking" : "Finished"}
                  </span>
                </div>

                <div className="response-body-text">
                  <p>{response.response_text}</p>
                </div>

                {/* Grounding Context Footer */}
                {response.context_applied && (
                  <div className="response-grounding-footer">
                    <span>
                      🌱 {response.context_applied.crop} • 📍 {response.context_applied.location}
                      {response.context_applied.weather && ` • 🌦️ ${response.context_applied.weather}`}
                    </span>
                  </div>
                )}
              </div>

              {/* Real Action Buttons: Replay | Stop | Try Again */}
              <div className="voice-action-buttons">
                <button
                  className="voice-btn-action replay-btn"
                  onClick={handleReplayAudio}
                  title="Replay Spoken Response"
                >
                  <RotateCcw size={18} />
                  <span>
                    {detectedLang === "bn" ? "Replay (আবার শুনুন)" : detectedLang === "hi" ? "Replay (फिर से सुनें)" : "Replay"}
                  </span>
                </button>

                {voiceState === "speaking" && (
                  <button
                    className="voice-btn-action stop-btn"
                    onClick={handleStopAudio}
                    title="Stop Audio Playback"
                  >
                    <Square size={16} fill="currentColor" />
                    <span>
                      {detectedLang === "bn" ? "Stop (থামুন)" : detectedLang === "hi" ? "Stop (रोकें)" : "Stop"}
                    </span>
                  </button>
                )}

                <button
                  className="voice-btn-action try-again-btn"
                  onClick={handleTryAgain}
                  title="Ask a New Question"
                >
                  <Mic size={18} />
                  <span>
                    {detectedLang === "bn" ? "Try Again (নতুন প্রশ্ন)" : detectedLang === "hi" ? "Try Again (दोबारा पूछें)" : "Try Again"}
                  </span>
                </button>
              </div>
            </div>
          )}

          {/* 7. ERROR STATE */}
          {voiceState === "error" && (
            <div className="voice-state-view error-view">
              <div className="error-icon-circle">
                <AlertCircle size={40} />
              </div>

              <h3>
                {detectedLang === "bn"
                  ? "দুঃখিত, সমস্যা হয়েছে"
                  : detectedLang === "hi"
                  ? "माफ़ कीजिए, कोई त्रुटি हुई"
                  : "Voice Notice"}
              </h3>
              <p className="error-desc">{errorMessage || "Could not process voice query."}</p>

              <div className="error-actions">
                <button className="primary-btn retry-btn" onClick={handleTryAgain}>
                  <RotateCcw size={18} />
                  {detectedLang === "bn" ? "Try Again (আবার চেষ্টা করুন)" : detectedLang === "hi" ? "Try Again (दोबारा बोलें)" : "Try Again"}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* ================= QUICK TAP VOICE STARTERS ================= */}
        <div className="voice-quick-starters-section">
          <div className="quick-starters-label">
            <Sparkles size={14} />
            <span>
              {detectedLang === "bn"
                ? "বা নিচের প্রশ্নে ১-ট্যাপ করে সরাসরি ভয়েস শুনুন:"
                : detectedLang === "hi"
                ? "या नीचे दिए सवाल पर 1-टैप करके आवाज सुनें:"
                : "Or tap any quick starter question below:"}
            </span>
          </div>

          <div className="quick-starters-grid">
            {quickList.map((item, idx) => (
              <button
                key={idx}
                className="quick-voice-chip"
                onClick={() => handleQuickQuestionTap(item)}
                disabled={voiceState === "processing" || voiceState === "thinking"}
              >
                <span>{item.label}</span>
                <ArrowRight size={14} className="chip-arrow" />
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default VoiceAssistantModal;
