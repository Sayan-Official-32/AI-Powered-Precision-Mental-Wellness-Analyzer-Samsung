// Wait for DOM to be fully loaded before accessing elements
let textBtn, textInput, textResult, chatWindow, chatInput, chatSend, chatVoice;
let voiceStatus, voiceIndicator, voiceText, alertFeed, monitorResult;
let startBtn, stopBtn, cameraStreamEl, screenStreamEl;

let chatHistory = [];
let cameraStream;
let screenStream;
let micStream;
let audioRecorder;
let monitorInterval;
let miniDisplayWindow = null;
let requestingNotificationPermission = false;
let lastAlertSignature = "";
let audioContext;
let pendingAudioData = null; // Store latest audio data for snapshot
let lastSpokenAlert = ""; // Track last spoken alert to avoid repetition
let speechSynthesis = null; // Web Speech API for text-to-speech
let lastRiskLevel = ""; // Track last risk level to detect changes
let alertCooldownUntil = 0; // Timestamp when alert cooldown expires (milliseconds)
const ALERT_COOLDOWN_MS = 30000; // 30 seconds cooldown between alerts
let recognition = null; // Web Speech Recognition API for voice input
let isListening = false; // Track if voice recognition is active

// Initialize when DOM is ready
function initializeApp() {
  console.log("🚀 Initializing app...");
  
  try {
    // Get all DOM elements
    textBtn = document.getElementById("text-btn");
    textInput = document.getElementById("text-input");
    textResult = document.getElementById("text-result");
    chatWindow = document.getElementById("chat-window");
    chatInput = document.getElementById("chat-message");
    chatSend = document.getElementById("chat-send");
    chatVoice = document.getElementById("chat-voice");
    voiceStatus = document.getElementById("voice-status");
    voiceIndicator = document.getElementById("voice-indicator");
    voiceText = document.getElementById("voice-text");
    alertFeed = document.getElementById("alert-feed");
    monitorResult = document.getElementById("monitor-result");
    startBtn = document.getElementById("start-monitor");
    stopBtn = document.getElementById("stop-monitor");
    cameraStreamEl = document.getElementById("camera-stream");
    screenStreamEl = document.getElementById("screen-stream");

    console.log("📋 DOM elements found:", {
      textBtn: !!textBtn,
      textInput: !!textInput,
      chatSend: !!chatSend,
      startBtn: !!startBtn,
      stopBtn: !!stopBtn
    });

    // Check if all required elements exist
    if (!textBtn || !textInput || !chatSend || !startBtn || !stopBtn) {
      console.error("❌ Critical DOM elements not found! Some buttons may not work.");
      console.error("Missing elements:", {
        textBtn: !textBtn,
        textInput: !textInput,
        chatSend: !chatSend,
        startBtn: !startBtn,
        stopBtn: !stopBtn
      });
      alert("Error: Some page elements are missing. Please refresh the page.");
      return;
    }

    // Remove any existing event listeners by cloning and replacing elements
    // This prevents duplicate listeners
    const replaceElement = (oldEl, newEl) => {
      if (oldEl && oldEl.parentNode) {
        oldEl.parentNode.replaceChild(newEl, oldEl);
      }
    };

    // Attach event listeners with null checks and error handling
    if (textBtn) {
      // Remove old listeners by cloning
      const newTextBtn = textBtn.cloneNode(true);
      replaceElement(textBtn, newTextBtn);
      textBtn = newTextBtn;
      
      textBtn.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log("🔵 Analyze Mood button clicked (direct)");
        handleTextAnalysis();
      });
      console.log("✅ Text button listener attached");
    }
    
    if (chatSend) {
      const newChatSend = chatSend.cloneNode(true);
      replaceElement(chatSend, newChatSend);
      chatSend = newChatSend;
      
      chatSend.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log("🔵 Send button clicked (direct)");
        sendChatMessage();
      });
      console.log("✅ Chat send button listener attached");
    }
    
    if (chatInput) {
      chatInput.addEventListener("keyup", function(e) {
        if (e.key === "Enter") {
          e.preventDefault();
          sendChatMessage();
        }
      });
      console.log("✅ Chat input listener attached");
    }
    
    if (chatVoice) {
      const newChatVoice = chatVoice.cloneNode(true);
      replaceElement(chatVoice, newChatVoice);
      chatVoice = newChatVoice;
      
      chatVoice.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log("🔵 Voice button clicked (direct)");
        toggleVoiceInput();
      });
      console.log("✅ Voice button listener attached");
    }
    
    if (startBtn) {
      const newStartBtn = startBtn.cloneNode(true);
      replaceElement(startBtn, newStartBtn);
      startBtn = newStartBtn;
      
      startBtn.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log("🔵 Start Monitoring button clicked (direct)");
        startMonitoring();
      });
      console.log("✅ Start monitor button listener attached");
    }
    
    if (stopBtn) {
      const newStopBtn = stopBtn.cloneNode(true);
      replaceElement(stopBtn, newStopBtn);
      stopBtn = newStopBtn;
      
      stopBtn.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log("🔵 Stop Monitoring button clicked (direct)");
        stopMonitoring();
      });
      console.log("✅ Stop monitor button listener attached");
    }

    // Check browser support
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.warn("⚠️ Browser does not support getUserMedia");
      if (startBtn) startBtn.disabled = true;
    } else if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
      console.warn("⚠️ getUserMedia requires HTTPS or localhost. Current protocol:", location.protocol);
    }

    console.log("✅ All button event listeners initialized successfully!");
    console.log("✅ App initialization complete!");
    
  } catch (error) {
    console.error("❌ Error during app initialization:", error);
    alert("Error initializing app: " + error.message + "\nPlease refresh the page.");
  }
}

// Initialize when DOM is ready - multiple methods for maximum compatibility
function startApp() {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
  } else if (document.readyState === 'interactive' || document.readyState === 'complete') {
    // DOM is already loaded
    initializeApp();
  } else {
    // Fallback: wait a bit and try again
    setTimeout(initializeApp, 100);
  }
}

// Start the app
startApp();

async function handleTextAnalysis() {
  console.log("🔵 Analyze Mood button clicked");
  
  if (!textInput || !textResult) {
    console.error("❌ Text input or result element not found!");
    alert("Error: Text analysis elements not found. Please refresh the page.");
    return;
  }
  
  const text = textInput.value.trim();
  if (!text) {
    textResult.innerText = "Please write a quick check-in first.";
    return;
  }

  console.log("📝 Analyzing text:", text.substring(0, 50) + "...");
  textResult.innerText = "Analyzing…";
  
  try {
    const res = await fetch("/api/v1/text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    
    const data = await res.json();
    console.log("✅ Text analysis result:", data);
    
    textResult.innerHTML = `
      <strong>Mood:</strong> ${data.mood || data.label}<br/>
      <strong>Confidence:</strong> ${(data.score * 100).toFixed(1)}%<br/>
      <strong>Insights:</strong> ${data.insights?.join(" • ")}
    `;
  } catch (err) {
    console.error("❌ Text analysis error:", err);
    textResult.innerText = `Unable to analyze text right now. Error: ${err.message || "Unknown error"}`;
  }
}

async function sendChatMessage() {
  console.log("🔵 Send button clicked");
  
  if (!chatInput || !chatWindow) {
    console.error("❌ Chat input or window element not found!");
    alert("Error: Chat elements not found. Please refresh the page.");
    return;
  }
  
  const message = chatInput.value.trim();
  if (!message) {
    console.log("⚠️ No message to send");
    return;
  }

  console.log("💬 Sending message:", message.substring(0, 50) + "...");
  appendChatBubble("user", message);
  chatInput.value = "";

  // Show loading indicator
  const loadingBubble = appendChatBubble("ai", "Thinking...");
  loadingBubble.style.opacity = "0.6";

  try {
    const res = await fetch("/api/v1/companion", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        history: chatHistory,
        mode: "text",
      }),
    });
    
    const data = await res.json();
    
    // Remove loading bubble
    loadingBubble.remove();
    
    if (data.error) {
      throw new Error(data.error);
    }
    
    appendChatBubble("ai", data.response);
    chatHistory.push({ role: "user", content: message });
    chatHistory.push({ role: "assistant", content: data.response });
  } catch (err) {
    // Remove loading bubble
    loadingBubble.remove();
    
    // Provide specific error messages based on error type
    let errorMsg = "I cannot connect to the AI companion right now.";
    
    if (err.message) {
      if (err.message.includes("quota") || err.message.includes("Quota")) {
        errorMsg = "⚠️ OpenAI API quota exceeded. Please check your OpenAI account billing and quota limits.";
      } else if (err.message.includes("API key") || err.message.includes("invalid")) {
        errorMsg = "⚠️ Invalid OpenAI API key. Please check your OPENAI_API_KEY configuration.";
      } else if (err.message.includes("rate limit")) {
        errorMsg = "⚠️ Rate limit exceeded. Please wait a moment and try again.";
      } else if (err.message.includes("429")) {
        errorMsg = "⚠️ Too many requests. Please wait a moment and try again.";
      } else {
        errorMsg = `⚠️ ${err.message}`;
      }
    }
    
    appendChatBubble("ai", errorMsg);
    console.error("Chat error:", err);
  }
}

// Voice input functionality
function initVoiceRecognition() {
  if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
    console.warn("Speech recognition not supported in this browser");
    if (chatVoice) {
      chatVoice.style.display = "none";
      chatVoice.disabled = true;
    }
    return null;
  }
  
  try {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const rec = new SpeechRecognition();
    
    rec.continuous = false;
    rec.interimResults = false;
    rec.lang = "en-US";
    
    rec.onstart = () => {
      isListening = true;
      console.log("Voice recognition started");
      if (voiceStatus) voiceStatus.style.display = "block";
      if (voiceIndicator) voiceIndicator.textContent = "🔴";
      if (voiceText) voiceText.textContent = "Listening...";
      if (chatVoice) {
        chatVoice.style.backgroundColor = "#ff4444";
        chatVoice.textContent = "⏹️";
      }
    };
    
    rec.onresult = (event) => {
      if (event.results && event.results.length > 0) {
        const transcript = event.results[0][0].transcript;
        console.log("Voice recognition result:", transcript);
        chatInput.value = transcript;
        // Auto-send the message
        setTimeout(() => {
          sendChatMessage();
        }, 100);
      }
    };
    
    rec.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      isListening = false;
      
      let errorMsg = "Error occurred";
      if (event.error === "no-speech") {
        errorMsg = "No speech detected. Please try again.";
      } else if (event.error === "audio-capture") {
        errorMsg = "Microphone not found. Please check your microphone.";
      } else if (event.error === "not-allowed") {
        errorMsg = "Microphone permission denied. Please allow microphone access.";
      } else {
        errorMsg = `Error: ${event.error}`;
      }
      
      if (voiceText) {
        voiceText.textContent = errorMsg;
        setTimeout(() => {
          if (voiceStatus) voiceStatus.style.display = "none";
        }, 3000);
      }
      
      if (chatVoice) {
        chatVoice.style.backgroundColor = "";
        chatVoice.textContent = "🎤";
      }
    };
    
    rec.onend = () => {
      console.log("Voice recognition ended");
      isListening = false;
      if (voiceStatus) voiceStatus.style.display = "none";
      if (chatVoice) {
        chatVoice.style.backgroundColor = "";
        chatVoice.textContent = "🎤";
      }
    };
    
    return rec;
  } catch (err) {
    console.error("Error initializing voice recognition:", err);
    if (chatVoice) {
      chatVoice.style.display = "none";
      chatVoice.disabled = true;
    }
    return null;
  }
}

function toggleVoiceInput() {
  console.log("Voice button clicked, isListening:", isListening);
  
  if (!recognition) {
    console.log("Initializing voice recognition...");
    recognition = initVoiceRecognition();
    if (!recognition) {
      alert("Speech recognition is not supported in your browser. Please use Chrome, Edge, or another browser that supports Web Speech API.");
      return;
    }
  }
  
  if (isListening) {
    console.log("Stopping voice recognition...");
    try {
      recognition.stop();
    } catch (err) {
      console.error("Error stopping recognition:", err);
      isListening = false;
      if (chatVoice) {
        chatVoice.style.backgroundColor = "";
        chatVoice.textContent = "🎤";
      }
    }
  } else {
    console.log("Starting voice recognition...");
    try {
      recognition.start();
    } catch (err) {
      console.error("Error starting voice recognition:", err);
      if (err.message && err.message.includes("already started")) {
        // Recognition is already running, just update UI
        isListening = true;
        if (voiceStatus) voiceStatus.style.display = "block";
        if (voiceIndicator) voiceIndicator.textContent = "🔴";
        if (voiceText) voiceText.textContent = "Listening...";
        if (chatVoice) {
          chatVoice.style.backgroundColor = "#ff4444";
          chatVoice.textContent = "⏹️";
        }
      } else {
        if (voiceText) {
          voiceText.textContent = "Error starting recognition. Please try again.";
          if (voiceStatus) voiceStatus.style.display = "block";
          setTimeout(() => {
            if (voiceStatus) voiceStatus.style.display = "none";
          }, 3000);
        }
      }
    }
  }
}

function appendChatBubble(sender, text) {
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${sender}`;
  bubble.innerText = text;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return bubble; // Return bubble element for removal/updates
}

async function startMonitoring() {
  console.log("🔵 Start Monitoring button clicked");
  
  if (!startBtn || !stopBtn || !cameraStreamEl || !screenStreamEl) {
    console.error("❌ Monitor elements not found!");
    alert("Error: Monitor elements not found. Please refresh the page.");
    return;
  }
  
  try {
    console.log("🚀 Starting monitoring...");
    // Clean up any existing streams first (ensures fresh permission request)
    if (cameraStream) {
      cameraStream.getTracks().forEach(t => {
        t.stop();
        t.enabled = false;
      });
      cameraStream = null;
    }
    if (micStream) {
      micStream.getTracks().forEach(t => {
        t.stop();
        t.enabled = false;
      });
      micStream = null;
    }
    if (screenStream) {
      screenStream.getTracks().forEach(t => {
        t.stop();
        t.enabled = false;
      });
      screenStream = null;
    }
    
    // Clear video elements
    if (cameraStreamEl) cameraStreamEl.srcObject = null;
    if (screenStreamEl) screenStreamEl.srcObject = null;
    
    // Check current permission status (for information only)
    try {
      const cameraPermission = await navigator.permissions.query({ name: 'camera' });
      const microphonePermission = await navigator.permissions.query({ name: 'microphone' });
      console.log("Camera permission status:", cameraPermission.state);
      console.log("Microphone permission status:", microphonePermission.state);
      
      // If permissions are already granted, browser may auto-grant without prompt
      // To force prompt, user needs to reset permissions in browser settings
      if (cameraPermission.state === 'granted' || microphonePermission.state === 'granted') {
        console.log("Note: Browser may auto-grant permissions. To see prompt again, reset permissions in browser settings.");
      }
    } catch (permErr) {
      // Permission query not supported in all browsers, that's okay
      console.log("Permission query not available, proceeding with request...");
    }
    
    // Request camera and microphone together - browsers handle this better
    // Browser will prompt if permission not granted, or auto-grant if previously granted
    console.log("Requesting camera and microphone permissions...");
    const mediaStream = await navigator.mediaDevices.getUserMedia({ 
      video: true, 
      audio: true 
    });
    
    // Separate camera and microphone streams
    cameraStream = new MediaStream(mediaStream.getVideoTracks());
    micStream = new MediaStream(mediaStream.getAudioTracks());
    
    // Check if we actually got microphone access
    if (micStream.getAudioTracks().length === 0) {
      console.warn("Microphone permission denied or not available");
      alert("Microphone access is required for speech emotion analysis. Please grant microphone permission and try again.");
      // Try to get just camera if microphone fails
      try {
        cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
      } catch (camErr) {
        console.error("Camera access failed:", camErr);
        throw new Error("Camera access denied");
      }
    } else {
      console.log("Microphone access granted!");
    }
    
    cameraStreamEl.srcObject = cameraStream;
    cameraStreamEl.play().catch(() => {});

    // Request screen capture (this always prompts, but we ensure it's fresh)
    console.log("Requesting screen capture permission (fresh request)...");
    screenStream = await navigator.mediaDevices.getDisplayMedia({ 
      video: true,
      audio: false  // Screen capture audio not needed
    });
    screenStreamEl.srcObject = screenStream;
    screenStreamEl.play().catch(() => {});

    // Setup audio recorder with microphone stream
    if (micStream && micStream.getAudioTracks().length > 0) {
      setupAudioRecorder(micStream);
    } else {
      console.warn("No microphone available - speech analysis will be skipped");
    }

    requestNotificationPermission();
    
    // Initialize speech synthesis voices (load them)
    if ("speechSynthesis" in window) {
      const synth = window.speechSynthesis;
      // Voices may not be loaded immediately, so load them
      const loadVoices = () => {
        const voices = synth.getVoices();
        console.log(`✅ Loaded ${voices.length} speech synthesis voices`);
        if (voices.length > 0) {
          console.log("Available voices:", voices.map(v => v.name).slice(0, 5).join(", "));
        }
      };
      loadVoices();
      // Some browsers load voices asynchronously
      if (synth.onvoiceschanged !== undefined) {
        synth.onvoiceschanged = loadVoices;
      }
      // Also try loading after a delay
      setTimeout(loadVoices, 1000);
    }
    
    // Open mini display popup (only once, don't reopen if already open)
    if (!miniDisplayWindow || miniDisplayWindow.closed) {
      openMiniDisplay();
    }

    // Start monitoring immediately, then every 10 seconds (optimized for responsiveness)
    pushMonitorSnapshot();
    // Reduced to 10 seconds for faster updates and better responsiveness
    monitorInterval = setInterval(pushMonitorSnapshot, 10000);
    startBtn.disabled = true;
    stopBtn.disabled = false;
    
    console.log("Monitoring started successfully!");
  } catch (err) {
    console.error("Error starting monitoring:", err);
    let errorMessage = "Failed to start monitoring. ";
    
    if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
      errorMessage += "Please allow camera, microphone, and screen permissions in your browser settings and try again.";
    } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
      errorMessage += "Camera or microphone not found. Please connect a camera/microphone and try again.";
    } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
      errorMessage += "Camera or microphone is being used by another application. Please close other apps and try again.";
    } else {
      errorMessage += `Error: ${err.message || "Unknown error"}`;
    }
    
    alert(errorMessage);
    
    // Reset button states
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }
}

function stopMonitoring() {
  startBtn.disabled = false;
  stopBtn.disabled = true;

  // Stop monitoring interval
  if (monitorInterval) {
    clearInterval(monitorInterval);
    monitorInterval = null;
  }
  
  // Stop audio recorder
  if (audioRecorder && audioRecorder.state !== "inactive") {
    audioRecorder.stop();
    audioRecorder = null;
  }
  
  // Stop and remove ALL tracks from streams (this forces re-requesting permissions next time)
  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => {
      track.stop();
      track.enabled = false;
    });
    cameraStream = null;
  }
  
  if (screenStream) {
    screenStream.getTracks().forEach((track) => {
      track.stop();
      track.enabled = false;
    });
    screenStream = null;
  }
  
  if (micStream) {
    micStream.getTracks().forEach((track) => {
      track.stop();
      track.enabled = false;
    });
    micStream = null;
  }
  
  // Clear video element sources (important for forcing fresh permissions)
  if (cameraStreamEl) {
    cameraStreamEl.srcObject = null;
    cameraStreamEl.pause();
  }
  
  if (screenStreamEl) {
    screenStreamEl.srcObject = null;
    screenStreamEl.pause();
  }
  
  monitorResult.innerText = "Monitoring stopped. Permissions will be requested again next time.";
  
  // Close mini display
  if (miniDisplayWindow && !miniDisplayWindow.closed) {
    miniDisplayWindow.close();
    miniDisplayWindow = null;
  }
  
  console.log("All streams stopped. Permissions will be requested fresh next time.");
}

function setupAudioRecorder(stream) {
  if (!stream || !stream.getAudioTracks().length) {
    console.warn("No audio track available; monitor will skip speech analysis.");
    return;
  }

  // Check if audio tracks are enabled
  const audioTracks = stream.getAudioTracks();
  const enabledTracks = audioTracks.filter(track => track.enabled && track.readyState === 'live');
  
  if (enabledTracks.length === 0) {
    console.warn("No enabled audio tracks available; monitor will skip speech analysis.");
    return;
  }

  console.log(`Setting up audio recorder with ${enabledTracks.length} audio track(s)`);

  try {
    // Try to use the best available MIME type
    let mimeType = "audio/webm";
    const supportedTypes = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus",
      "audio/ogg"
    ];
    
    for (const type of supportedTypes) {
      if (MediaRecorder.isTypeSupported(type)) {
        mimeType = type;
        break;
      }
    }
    
    console.log(`Using audio MIME type: ${mimeType}`);
    audioRecorder = new MediaRecorder(stream, { mimeType: mimeType });
    
  audioRecorder.ondataavailable = async (event) => {
    if (event.data && event.data.size > 0) {
      console.log(`Audio data received: ${event.data.size} bytes, type: ${event.data.type}`);
      try {
        const audio64 = await blobToBase64(event.data);
        // Store latest audio data for next snapshot
        if (audio64) {
          pendingAudioData = audio64;
          console.log("Audio data stored, will be included in next snapshot");
        } else {
          console.warn("Skipping audio - WAV conversion failed");
        }
      } catch (err) {
        console.error("Error processing audio data:", err);
      }
    }
  };
    
    audioRecorder.onerror = (event) => {
      console.error("MediaRecorder error:", event.error);
    };
    
    audioRecorder.onstart = () => {
      console.log("Audio recorder started");
    };
    
    audioRecorder.onstop = () => {
      console.log("Audio recorder stopped");
    };
    
    // Start recording with 4 second chunks
    audioRecorder.start(4000);
    console.log("Audio recorder started successfully");
  } catch (err) {
    console.error("MediaRecorder setup failed:", err);
    console.warn("Speech analysis will be unavailable");
  }
}

async function pushMonitorSnapshot(overrides = {}) {
  // Capture frames efficiently
  const frame = captureFrame(cameraStreamEl);
  const screen = captureFrame(screenStreamEl);

  // Always try to process even if one stream is missing (better for screen detection)
  if (!frame && !screen && !pendingAudioData) {
    monitorResult.innerHTML = "<em>Waiting for data streams...</em>";
    return;
  }

  // Update UI efficiently (non-blocking)
  requestAnimationFrame(() => {
    monitorResult.innerHTML = "<em>Analyzing...</em>";
  });

  // Include pending audio data if available
  const audioData = overrides.audio || pendingAudioData;
  
  // Optimize payload - always send screen if available (important for detection)
  const payload = {};
  if (frame) payload.frame = frame;
  if (screen) payload.screen = screen;  // Always include screen if available
  if (audioData) payload.audio = audioData;
  
  // Clear pending audio after using it (will be refreshed by next audio chunk)
  if (audioData === pendingAudioData) {
    pendingAudioData = null;
  }
  
  // Send request asynchronously
  sendMonitorRequest(payload);
}

async function sendMonitorRequest(payload) {
  // Reduced logging for performance

  try {
    const res = await fetch("/api/v1/monitor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    
    if (!res.ok) {
      // Try to get error details, but don't fail completely
      const errorData = await res.json().catch(() => ({}));
      console.error("Monitor request failed:", res.status, errorData);
      
      // Show a partial result with error message
      renderMonitorResult({
        synthesis: {
          score: 50.0,
          overall_state: "steady",
          risk_level: "low",
          notes: [`Server error: ${res.status}. Some modules may not be available.`],
          actions: ["Please check your connection and try again."],
        },
        text: null,
        speech: null,
        face: null,
        screen: { status: "error", error: `HTTP ${res.status}` },
      });
      return;
    }
    
    const data = await res.json();
    
    // Ensure screen data is always included in response
    if (!data.screen && payload.screen) {
      data.screen = { status: "processing", note: "Screen analysis in progress..." };
    }
    
    // Ensure we always have a synthesis object
    if (!data.synthesis) {
      console.warn("No synthesis data in response, creating default");
      data.synthesis = {
        score: 50.0,
        overall_state: "steady",
        risk_level: "low",
        notes: ["Analysis incomplete - some modules may have failed"],
        actions: ["Please try again"],
      };
    }
    
    // Render result using requestAnimationFrame for smooth UI updates
    requestAnimationFrame(() => {
      renderMonitorResult(data);
    });
  } catch (err) {
    console.error("Monitor error:", err);
    // Show a graceful error message instead of just "Failed to analyze"
    monitorResult.innerHTML = `
      <div class="monitor-summary">
        <h3>Connection Error</h3>
        <p><strong>Status:</strong> Unable to connect to analysis server</p>
        <p><strong>Error:</strong> ${err.message || "Network or server error"}</p>
        <p><em>Please check that the server is running and try again.</em></p>
      </div>
    `;
  }
}

function renderMonitorResult(data) {
  const { synthesis, text, speech, face, screen } = data;
  
  if (!synthesis) {
    monitorResult.innerHTML = "<em>No analysis data received. Check backend logs.</em>";
    return;
  }

  // Optimized rendering - use document fragments for better performance
  const fragment = document.createDocumentFragment();
  const container = document.createElement("div");
  
  // Build HTML more efficiently
  const score = synthesis.score?.toFixed(1) ?? "—";
  const state = synthesis.overall_state || "—";
  const risk = synthesis.risk_level || "—";
  
  let html = `
    <div class="monitor-summary">
      <h3>Overall Wellness</h3>
      <p><strong>Score:</strong> ${score} / 100</p>
      <p><strong>State:</strong> <span class="state-${state}">${state}</span></p>
      <p><strong>Risk Level:</strong> <span class="risk-${risk}">${risk}</span></p>
    </div>
    
    <div class="monitor-modules">
      <h4>Module Results:</h4>
      <ul>
        <li><strong>Text:</strong> ${text ? formatTextSummary(text) : "—"}</li>
        <li><strong>Speech:</strong> ${speech ? (speech.emotion || "waiting") : "—"}</li>
        <li><strong>Face:</strong> ${face ? (face.dominant_emotion || "detecting...") : "—"}</li>
        <li><strong>Screen:</strong> ${summarizeScreen(screen)}</li>
      </ul>
    </div>
  `;

  // Limit notes display (max 3 for performance)
  if (synthesis.notes && synthesis.notes.length > 0) {
    const notes = synthesis.notes.slice(0, 3).join(" • ");
    html += `<div class="monitor-notes"><strong>Notes:</strong> ${notes}</div>`;
  }

  // Limit actions display (max 3 for performance)
  if (synthesis.actions && synthesis.actions.length > 0) {
    const actions = synthesis.actions.slice(0, 3).map(a => `<li>${a}</li>`).join("");
    html += `<div class="monitor-actions"><strong>Recommended Actions:</strong><ul>${actions}</ul></div>`;
  }

  // Use requestAnimationFrame for smooth rendering
  requestAnimationFrame(() => {
    monitorResult.innerHTML = html;
  });

  // Check if risk level changed or cooldown expired
  const currentRiskLevel = synthesis?.risk_level || "low";
  const riskLevelChanged = currentRiskLevel !== lastRiskLevel;
  const cooldownExpired = Date.now() > alertCooldownUntil;
  const shouldAlert = riskLevelChanged && cooldownExpired && ["high", "critical"].includes(currentRiskLevel);
  
  if (synthesis && ["high", "critical"].includes(synthesis.risk_level)) {
    alertFeed.innerHTML = `
      <div class="chat-bubble ai alert-${synthesis.risk_level}">
        <strong>🚨 ${synthesis.risk_level.toUpperCase()} ALERT:</strong><br/>
        ${synthesis.notes?.join(" ") || "Elevated risk detected"}
      </div>
    `;
    
    // Only show notification and speak if risk level changed and cooldown expired
    if (shouldAlert) {
      // Update tracking
      lastRiskLevel = currentRiskLevel;
      alertCooldownUntil = Date.now() + ALERT_COOLDOWN_MS;
      
      // Show notification (always, not just when page is hidden)
      showHighRiskNotification(
        `${synthesis.risk_level.toUpperCase()} Alert`,
        synthesis.notes?.join(" ") || "Elevated mental health risk detected.",
        synthesis.actions || []
      );
      
      // Speak the alert and suggestions (only once)
      speakHighRiskAlert(synthesis);
    }
  } else if (synthesis.risk_level === "medium") {
    // Reset risk level tracking when risk decreases
    if (lastRiskLevel !== "medium") {
      lastRiskLevel = "medium";
    }
    alertFeed.innerHTML = `
      <div class="chat-bubble ai alert-medium">
        <strong>⚠️ Moderate Alert:</strong><br/>
        ${synthesis.notes?.join(" ") || "Some concerns detected"}
      </div>
    `;
    // No notification for medium alerts
  } else {
    // Reset risk level tracking when no risk
    if (lastRiskLevel !== "low") {
      lastRiskLevel = "low";
    }
    alertFeed.innerHTML = "<div class=\"chat-bubble ai\">No alerts yet.</div>";
  }
  
  // Update mini display popup
  updateMiniDisplay(data);
}

function captureFrame(videoEl) {
  if (!videoEl || videoEl.readyState < 2 || videoEl.videoWidth === 0 || videoEl.videoHeight === 0) {
    return null;
  }
  try {
    const canvas = document.createElement("canvas");
    // Resize images to reduce processing load and prevent system hangs
    // Camera frames: max 640x480 (good for face detection)
    // Screen captures: max 1280x720 (good for OCR while reducing load)
    const isScreenCapture = videoEl.id === "screen-stream";
    const maxWidth = isScreenCapture ? 1280 : 640;
    const maxHeight = isScreenCapture ? 720 : 480;
    
    const sourceWidth = videoEl.videoWidth || 640;
    const sourceHeight = videoEl.videoHeight || 360;
    
    // Calculate scaled dimensions maintaining aspect ratio
    let canvasWidth = sourceWidth;
    let canvasHeight = sourceHeight;
    
    if (sourceWidth > maxWidth || sourceHeight > maxHeight) {
      const scale = Math.min(maxWidth / sourceWidth, maxHeight / sourceHeight);
      canvasWidth = Math.floor(sourceWidth * scale);
      canvasHeight = Math.floor(sourceHeight * scale);
    }
    
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
    
    // Use JPEG with quality 0.85 to reduce size further (PNG is much larger)
    return canvas.toDataURL("image/jpeg", 0.85);
  } catch (err) {
    console.warn("Frame capture error:", err);
    return null;
  }
}

async function blobToBase64(blob) {
  if (blob?.type?.startsWith("audio/")) {
    try {
      // Always convert WebM/OGG to WAV for cloud-friendly backend (no FFmpeg needed)
      const wavBlob = await convertAudioBlobToWav(blob);
      return await blobToDataURL(wavBlob);
    } catch (err) {
      console.error("WAV conversion failed:", err);
      // If conversion fails, return empty to skip audio analysis
      // This ensures backend only receives WAV format
      return null;
    }
  }
  return await blobToDataURL(blob);
}

function blobToDataURL(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

function requestNotificationPermission() {
  if (!("Notification" in window)) {
    return;
  }
  if (Notification.permission === "default" && !requestingNotificationPermission) {
    requestingNotificationPermission = true;
    Notification.requestPermission().finally(() => {
      requestingNotificationPermission = false;
    });
  }
}

function maybeShowNotification(title, body) {
  if (!("Notification" in window)) {
    return;
  }
  if (Notification.permission !== "granted") {
    return;
  }
  const signature = `${title}-${body}`;
  if (signature === lastAlertSignature) {
    return;
  }
  lastAlertSignature = signature;

  // Only show notification when page is hidden (minimized)
  if (document.hidden) {
    new Notification(title, {
      body,
      icon: "/favicon.ico",
      tag: "wellness-alert",
    });
  }
}

function showHighRiskNotification(title, body, actions = []) {
  // Always show notification for high risk alerts, even when page is visible
  if (!("Notification" in window)) {
    console.warn("Browser notifications not supported");
    return;
  }
  
  if (Notification.permission !== "granted") {
    // Request permission if not granted
    requestNotificationPermission();
    return;
  }
  
  // Use simpler signature based on risk level only (not full body which may change)
  const signature = title; // Just use title (e.g., "HIGH ALERT" or "CRITICAL ALERT")
  if (signature === lastAlertSignature) {
    console.log("Notification already shown for this risk level, skipping");
    return; // Don't show duplicate notifications
  }
  lastAlertSignature = signature;

  // Create notification with actions
  const notificationBody = actions.length > 0 
    ? `${body}\n\nSuggested actions:\n${actions.slice(0, 2).join("\n")}`
    : body;
  
  const notification = new Notification(title, {
    body: notificationBody,
    icon: "/favicon.ico",
    tag: "wellness-high-alert",
    requireInteraction: true, // Keep notification visible until user interacts
    badge: "/favicon.ico",
  });
  
  // Close notification after 10 seconds
  setTimeout(() => {
    notification.close();
  }, 10000);
  
  // Handle notification click
  notification.onclick = () => {
    window.focus();
    notification.close();
  };
  
  console.log("High risk notification shown:", title);
}

function speakHighRiskAlert(synthesis) {
  // Use Web Speech API for text-to-speech
  if (!("speechSynthesis" in window)) {
    console.warn("Text-to-speech not supported in this browser");
    return;
  }
  
  // Initialize speech synthesis
  const synth = window.speechSynthesis;
  
  // Use simpler key based on risk level only (not notes which may change)
  const alertKey = synthesis.risk_level;
  if (alertKey === lastSpokenAlert) {
    console.log("Alert already spoken for this risk level, skipping");
    return; // Already spoke this alert
  }
  lastSpokenAlert = alertKey;
  
  // Cancel any ongoing speech before starting new one
  if (synth.speaking) {
    synth.cancel();
    // Wait a bit for cancellation to complete
    setTimeout(() => {
      speakAlert(synthesis, synth);
    }, 200);
    return;
  }
  
  // Speak the alert
  speakAlert(synthesis, synth);
}

function speakAlert(synthesis, synth) {
  // Build the speech message
  const riskLevel = synthesis.risk_level.toUpperCase();
  const notes = synthesis.notes?.join(". ") || "Elevated risk detected";
  const actions = synthesis.actions || [];
  
  // Create speech messages
  const messages = [
    `High alert. ${riskLevel} risk detected.`,
    notes,
  ];
  
  // Add suggestions if available
  if (actions.length > 0) {
    messages.push("Here are some suggestions to reduce the risk:");
    // Speak first 2-3 actions
    actions.slice(0, 3).forEach((action, index) => {
      messages.push(`Suggestion ${index + 1}: ${action}`);
    });
  }
  
  // Combine all messages
  const fullMessage = messages.join(". ");
  
  console.log("Preparing to speak:", fullMessage);
  
  // Create speech utterance
  const utterance = new SpeechSynthesisUtterance(fullMessage);
  
  // Configure speech
  utterance.rate = 0.9; // Slightly slower for clarity
  utterance.pitch = 1.0;
  utterance.volume = 1.0;
  utterance.lang = "en-US";
  
  // Load voices and select best one
  const loadVoice = () => {
    const voices = synth.getVoices();
    console.log(`Available voices: ${voices.length}`);
    
    // Try to use a more natural voice if available
    const preferredVoices = voices.filter(v => 
      v.lang.startsWith("en") && (
        v.name.includes("Google") || 
        v.name.includes("Microsoft") || 
        v.name.includes("Natural") ||
        v.name.includes("Zira") ||
        v.name.includes("Samantha")
      )
    );
    
    if (preferredVoices.length > 0) {
      utterance.voice = preferredVoices[0];
      console.log("Using voice:", preferredVoices[0].name);
    } else if (voices.length > 0) {
      // Use first English voice
      const englishVoices = voices.filter(v => v.lang.startsWith("en"));
      if (englishVoices.length > 0) {
        utterance.voice = englishVoices[0];
        console.log("Using voice:", englishVoices[0].name);
      }
    }
    
    // Event handlers
    utterance.onstart = () => {
      console.log("✅ Speech started:", fullMessage);
    };
    
    utterance.onerror = (event) => {
      console.error("❌ Speech synthesis error:", event.error, event);
    };
    
    utterance.onend = () => {
      console.log("✅ Finished speaking alert");
    };
    
    // Speak the alert
    try {
      synth.speak(utterance);
      console.log("🎤 Text-to-speech initiated");
    } catch (error) {
      console.error("❌ Error starting speech:", error);
    }
  };
  
  // Load voices (may need to wait for them to load)
  const voices = synth.getVoices();
  if (voices.length > 0) {
    loadVoice();
  } else {
    // Voices not loaded yet, wait for them
    console.log("Waiting for voices to load...");
    synth.onvoiceschanged = () => {
      console.log("Voices loaded");
      loadVoice();
    };
    // Fallback: try after a short delay
    setTimeout(() => {
      if (synth.getVoices().length > 0) {
        loadVoice();
      } else {
        console.warn("No voices available, using default");
        utterance.onstart = () => console.log("✅ Speech started (default voice)");
        utterance.onerror = (e) => console.error("❌ Speech error:", e);
        synth.speak(utterance);
      }
    }, 500);
  }
}

function openMiniDisplay() {
  // Don't reopen if window already exists and is open
  if (miniDisplayWindow && !miniDisplayWindow.closed) {
    miniDisplayWindow.focus();
    return;
  }
  
  const width = 400;
  const height = 500;
  const left = screen.width - width - 20;
  const top = 20;
  
  try {
    miniDisplayWindow = window.open(
      "",
      "wellnessMiniDisplay",
      `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
    );
    
    if (!miniDisplayWindow) {
      console.warn("Popup blocked! Please allow popups for this site to see the mini display.");
      return;
    }
    
    // Prevent the window from being reopened when minimized
    miniDisplayWindow.addEventListener("beforeunload", () => {
      // Window is closing, but don't set to null here as it might just be minimized
    });
  } catch (err) {
    console.error("Error opening mini display:", err);
  }
  
  miniDisplayWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Wellness Monitor</title>
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
          font-family: Arial, sans-serif;
          background: #0f172a;
          color: #f8fafc;
          padding: 15px;
          font-size: 13px;
        }
        .header {
          background: #1e293b;
          padding: 10px;
          border-radius: 8px;
          margin-bottom: 10px;
          text-align: center;
        }
        .header h2 {
          font-size: 16px;
          color: #22d3ee;
        }
        .content {
          background: #1e293b;
          padding: 12px;
          border-radius: 8px;
          min-height: 300px;
        }
        .score {
          font-size: 24px;
          font-weight: bold;
          text-align: center;
          margin: 10px 0;
        }
        .state {
          text-align: center;
          padding: 8px;
          border-radius: 6px;
          margin: 8px 0;
          font-weight: 600;
        }
        .state-calm { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        .state-steady { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
        .state-moderate_stress { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
        .state-high_anxiety { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
        .risk {
          text-align: center;
          padding: 6px;
          border-radius: 6px;
          margin: 8px 0;
          font-weight: 600;
        }
        .risk-low { color: #10b981; }
        .risk-medium { color: #f59e0b; }
        .risk-high { color: #ef4444; }
        .risk-critical { color: #dc2626; background: rgba(220, 38, 38, 0.2); }
        .modules {
          margin-top: 15px;
          font-size: 12px;
        }
        .modules ul {
          list-style: none;
          padding: 0;
        }
        .modules li {
          padding: 4px 0;
          border-bottom: 1px solid #334155;
        }
        .alert {
          background: rgba(239, 68, 68, 0.2);
          border-left: 3px solid #ef4444;
          padding: 8px;
          margin-top: 10px;
          border-radius: 4px;
          font-size: 11px;
        }
      </style>
    </head>
    <body>
      <div class="header">
        <h2>🧠 Wellness Monitor</h2>
      </div>
      <div class="content" id="mini-content">
        <p style="text-align: center; color: #94a3b8;">Waiting for data...</p>
      </div>
    </body>
    </html>
  `);
  
  miniDisplayWindow.document.close();
}

function updateMiniDisplay(data) {
  // Check if window exists and is not closed
  if (!miniDisplayWindow) {
    return;
  }
  
  try {
    // Check if window is closed (this might throw an error if window was closed)
    if (miniDisplayWindow.closed) {
      miniDisplayWindow = null;
      return;
    }
    
    const { synthesis, text, speech, face, screen } = data;
    const content = miniDisplayWindow.document.getElementById("mini-content");
    
    if (!content) {
      console.warn("Mini display content element not found");
      return;
    }
    
    if (!synthesis) {
      content.innerHTML = "<p style='text-align: center; color: #94a3b8;'>No data available</p>";
      return;
    }
  
    let html = `
      <div class="score">${synthesis.score?.toFixed(1) ?? "—"} / 100</div>
      <div class="state state-${synthesis.overall_state}">${synthesis.overall_state || "—"}</div>
      <div class="risk risk-${synthesis.risk_level}">Risk: ${synthesis.risk_level || "—"}</div>
      
      <div class="modules">
        <ul>
          <li><strong>Text:</strong> ${text ? formatTextSummary(text) : "—"}</li>
          <li><strong>Speech:</strong> ${speech ? (speech.emotion || "—") : "—"}</li>
          <li><strong>Face:</strong> ${face ? (face.dominant_emotion || face.emotion || "detecting...") : "—"}</li>
          <li><strong>Screen:</strong> ${summarizeScreen(screen)}</li>
        </ul>
      </div>
    `;
    
    if (synthesis.actions && synthesis.actions.length > 0) {
      html += `<div style="margin-top: 10px; font-size: 11px;"><strong>Actions:</strong><br/>${synthesis.actions.slice(0, 2).join("<br/>")}</div>`;
    }
    
    if (["high", "critical"].includes(synthesis.risk_level)) {
      html += `<div class="alert"><strong>🚨 ALERT:</strong><br/>${synthesis.notes?.join(" ") || "High risk detected"}</div>`;
    }
    
    content.innerHTML = html;
  } catch (err) {
    console.error("Error updating mini display:", err);
  }
}

function formatTextSummary(textResult) {
  if (!textResult) return "—";
  const base = textResult.mood || textResult.label || "—";
  if (textResult.source === "screen_ocr") {
    return `${base} (screen OCR)`;
  }
  return base;
}

function summarizeScreen(screenResult) {
  if (!screenResult) return "—";
  if (screenResult.status === "error") {
    return `Error: ${screenResult.error || "analysis failed"}`;
  }
  if (screenResult.status === "initializing") {
    return screenResult.note || "Initializing OCR...";
  }
  if (screenResult.status === "timeout") {
    return screenResult.note || "Screen analysis timeout";
  }
  if (screenResult.status === "unavailable") {
    return screenResult.note || "OCR not available";
  }
  if (screenResult.status === "no_frame") {
    return "Waiting for screen signal…";
  }
  if (screenResult.harmful_hits?.length) {
    return `⚠️ ${screenResult.harmful_hits.length} alert(s): ${screenResult.harmful_hits.join(", ")}`;
  }
  const preview = (screenResult.text || "").replace(/\s+/g, " ").trim();
  return preview ? `${preview.slice(0, 90)}${preview.length > 90 ? "…" : ""}` : "No readable text";
}

async function convertAudioBlobToWav(blob) {
  try {
    const arrayBuffer = await blob.arrayBuffer();
    audioContext = audioContext || new (window.AudioContext || window.webkitAudioContext)();
    
    // Decode audio data
    const decoded = await decodeWithAudioContext(audioContext, arrayBuffer);
    
    // Validate decoded audio
    if (!decoded || decoded.length === 0) {
      throw new Error("Decoded audio is empty");
    }
    
    // Convert to WAV
    const wavBuffer = audioBufferToWav(decoded);
    if (!wavBuffer || wavBuffer.byteLength === 0) {
      throw new Error("WAV buffer is empty");
    }
    
    return new Blob([wavBuffer], { type: "audio/wav" });
  } catch (error) {
    console.error("Error converting audio to WAV:", error);
    throw error; // Re-throw to be caught by caller
  }
}

function decodeWithAudioContext(context, arrayBuffer) {
  return new Promise((resolve, reject) => {
    context.decodeAudioData(
      arrayBuffer.slice(0),
      (buffer) => resolve(buffer),
      (err) => reject(err)
    );
  });
}

function audioBufferToWav(audioBuffer) {
  const numChannels = audioBuffer.numberOfChannels;
  const sampleRate = audioBuffer.sampleRate;
  const channelData = [];
  for (let i = 0; i < numChannels; i++) {
    channelData.push(audioBuffer.getChannelData(i));
  }
  const interleaved = interleaveChannels(channelData);
  const buffer = new ArrayBuffer(44 + interleaved.length * 2);
  const view = new DataView(buffer);
  let offset = 0;

  const writeString = (str) => {
    for (let i = 0; i < str.length; i++) {
      view.setUint8(offset++, str.charCodeAt(i));
    }
  };

  writeString("RIFF");
  view.setUint32(offset, 36 + interleaved.length * 2, true);
  offset += 4;
  writeString("WAVE");
  writeString("fmt ");
  view.setUint32(offset, 16, true);
  offset += 4;
  view.setUint16(offset, 1, true);
  offset += 2;
  view.setUint16(offset, numChannels, true);
  offset += 2;
  view.setUint32(offset, sampleRate, true);
  offset += 4;
  view.setUint32(offset, sampleRate * numChannels * 2, true);
  offset += 4;
  view.setUint16(offset, numChannels * 2, true);
  offset += 2;
  view.setUint16(offset, 16, true);
  offset += 2;
  writeString("data");
  view.setUint32(offset, interleaved.length * 2, true);
  offset += 4;

  floatTo16BitPCM(view, offset, interleaved);
  return buffer;
}

function interleaveChannels(channels) {
  if (channels.length === 1) {
    return channels[0];
  }
  const length = channels[0].length;
  const result = new Float32Array(length * channels.length);
  let index = 0;
  for (let i = 0; i < length; i++) {
    for (let c = 0; c < channels.length; c++) {
      result[index++] = channels[c][i];
    }
  }
  return result;
}

function floatTo16BitPCM(view, offset, input) 
{
  for (let i = 0; i < input.length; i++, offset += 2) 
    {
    let s = Math.max(-1, Math.min(1, input[i]));
    s = s < 0 ? s * 0x8000 : s * 0x7fff;
    view.setInt16(offset, s, true);
  }
}
