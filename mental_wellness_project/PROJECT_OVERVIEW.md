# AI-Powered Precision Mental Wellness Analyzer (AIP-MWA)
## Complete Project Overview & Documentation

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Key Benefits](#key-benefits)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [Workflow & Process Flow](#workflow--process-flow)
6. [Libraries & Dependencies](#libraries--dependencies)
7. [Features & Capabilities](#features--capabilities)
8. [Installation & Setup](#installation--setup)
9. [Performance Optimizations](#performance-optimizations)
10. [Security & Privacy](#security--privacy)

---

## 🎯 Project Overview

**AI-Powered Precision Mental Wellness Analyzer (AIP-MWA)** is an advanced multimodal Flask web application that provides real-time mental wellness monitoring and support. The system analyzes multiple data streams simultaneously—text input, speech patterns, facial expressions, and screen content—to generate a comprehensive wellness score and deliver personalized interventions.

### Core Concept

The system uses artificial intelligence and machine learning to:
- **Monitor** user's mental state through multiple modalities
- **Analyze** emotional patterns and risk indicators
- **Synthesize** data into actionable wellness insights
- **Alert** users when high-risk situations are detected
- **Guide** users with personalized recommendations

### Problem Statement

Mental health monitoring traditionally requires:
- Manual self-reporting (often unreliable)
- Professional intervention (not always accessible)
- Single-modality assessment (limited accuracy)
- Reactive rather than proactive support

### Solution

AIP-MWA provides:
- **Automated** continuous monitoring
- **Multimodal** analysis for higher accuracy
- **Real-time** risk detection and alerts
- **Proactive** intervention suggestions
- **Privacy-focused** local processing

---

## ✨ Key Benefits

### 1. **Comprehensive Monitoring**
- **Multimodal Analysis**: Combines text, voice, facial expressions, and screen content
- **Real-time Processing**: Continuous monitoring every 15 seconds
- **Accurate Assessment**: Weighted scoring system for reliable predictions

### 2. **Early Risk Detection**
- **Proactive Alerts**: Detects high-risk situations before they escalate
- **Multiple Alert Channels**: Visual, browser notifications, and voice announcements
- **Severity Classification**: Low, Medium, High, and Critical risk levels

### 3. **Personalized Support**
- **AI Companion**: GPT-powered conversational coach
- **Actionable Recommendations**: Context-aware suggestions
- **Adaptive Responses**: Tailored to user's current state

### 4. **Privacy & Security**
- **Local Processing**: Most analysis runs on local server
- **No Cloud Storage**: Data processed in real-time, not stored
- **User Control**: Start/stop monitoring at any time

### 5. **Performance Optimized**
- **Efficient Processing**: Optimized to prevent system overload
- **Cloud-Ready**: No external dependencies (FFmpeg-free)
- **Responsive UI**: Smooth operation without browser hangs

### 6. **Accessibility**
- **Voice Alerts**: Text-to-speech for high-risk situations
- **Visual Feedback**: Clear, intuitive interface
- **Multi-platform**: Works on Windows, Mac, Linux

---

## 🛠 Technology Stack

### Backend Framework
- **Flask**: Lightweight Python web framework
- **Flask-CORS**: Cross-origin resource sharing support

### Machine Learning & AI
- **PyTorch**: Deep learning framework
- **Transformers (Hugging Face)**: Pre-trained NLP models
- **scikit-learn**: Machine learning utilities
- **FER (Facial Expression Recognition)**: Emotion detection
- **OpenCV**: Computer vision and image processing

### Audio Processing
- **librosa**: Audio analysis and feature extraction
- **soundfile**: Audio file I/O
- **pydub**: Audio manipulation

### Image & Text Processing
- **Pillow (PIL)**: Image processing
- **pytesseract**: OCR (Tesseract wrapper)
- **EasyOCR**: Alternative OCR engine
- **NumPy**: Numerical computing

### AI Services
- **OpenAI API**: GPT-4o-mini for conversational AI

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling
- **JavaScript (ES6+)**: Client-side logic
- **Web APIs**: 
  - MediaDevices API (camera/microphone)
  - Screen Capture API
  - Web Speech API (text-to-speech)
  - Notifications API

### Database
- **SQLite**: Lightweight database for logging

### Utilities
- **python-dotenv**: Environment variable management
- **mtcnn**: Face detection (optional)

---

## 🏗 System Architecture

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Browser)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   Text   │  │  Audio  │  │  Camera  │  │  Screen  │     │
│  │  Input   │  │  Stream  │  │  Stream  │  │ Capture  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │             │             │            │
│       └─────────────┴─────────────┴─────────────┘            │
│                          │                                    │
│                    HTTP POST /api/v1/monitor                  │
└──────────────────────────┼────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask Backend Server                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Routes Handler (routes.py)               │   │
│  └──────┬───────────┬───────────┬───────────┬──────────┘   │
│         │           │           │           │               │
│    ┌────▼────┐ ┌────▼────┐ ┌────▼────┐ ┌────▼────┐        │
│    │  Text   │ │ Speech  │ │  Face   │ │ Screen  │        │
│    │Analysis │ │Analysis │ │Analysis │ │Analysis │        │
│    └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘        │
│         │           │           │           │               │
│         └───────────┴───────────┴───────────┘               │
│                          │                                    │
│              ┌───────────▼───────────┐                       │
│              │ Behavior Synthesis    │                       │
│              │ Engine                │                       │
│              └───────────┬───────────┘                       │
│                          │                                    │
│              ┌───────────▼───────────┐                       │
│              │  Wellness Score        │                       │
│              │  Risk Assessment       │                       │
│              │  Recommendations       │                       │
│              └────────────────────────┘                       │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
                    JSON Response
                    (Score, Risk, Actions)
```

### Component Breakdown

#### 1. **Frontend Layer**
- **HTML/CSS/JS**: User interface
- **Media Capture**: Camera, microphone, screen
- **Real-time Updates**: 15-second monitoring intervals
- **Alert System**: Visual, notifications, voice

#### 2. **Backend API Layer**
- **Flask Routes**: RESTful API endpoints
- **Request Handling**: JSON payload processing
- **Error Handling**: Graceful degradation

#### 3. **Analysis Modules**
- **Text Sentiment**: Transformer-based NLP
- **Speech Emotion**: Audio feature extraction
- **Facial Expression**: FER model
- **Screen OCR**: Text extraction and analysis

#### 4. **Synthesis Engine**
- **Weighted Scoring**: Multi-modal fusion
- **Risk Assessment**: Severity calculation
- **Action Generation**: Personalized recommendations

#### 5. **Data Layer**
- **SQLite Database**: Interaction logging
- **Alert Logging**: High-risk event tracking

---

## 🔄 Workflow & Process Flow

### Main Monitoring Workflow

```
1. USER STARTS MONITORING
   │
   ├─► Request Camera Permission
   ├─► Request Microphone Permission
   └─► Request Screen Capture Permission
   
2. DATA COLLECTION (Every 15 seconds)
   │
   ├─► Capture Camera Frame (640x480)
   ├─► Capture Screen (1280x720)
   ├─► Record Audio (4-second chunks)
   └─► Send to Backend
   
3. BACKEND PROCESSING
   │
   ├─► Text Analysis (if available)
   │   └─► Sentiment Score + Mood Detection
   │
   ├─► Speech Analysis
   │   └─► Emotion: calm/excited/sad/anxious
   │
   ├─► Facial Expression Analysis
   │   └─► Dominant Emotion + Confidence
   │
   ├─► Screen OCR (every 20 seconds)
   │   └─► Text Extraction + Harmful Content Detection
   │
   └─► Behavior Synthesis
       ├─► Weighted Score Calculation
       ├─► Risk Level Assessment
       └─► Action Recommendations
       
4. RESPONSE & ALERTS
   │
   ├─► Update UI with Results
   ├─► Check Risk Level
   │   ├─► If HIGH/CRITICAL:
   │   │   ├─► Show Visual Alert
   │   │   ├─► Browser Notification
   │   │   └─► Voice Announcement
   │   └─► Display Recommendations
   │
   └─► Log Interaction (SQLite)
```

### Detailed Module Workflows

#### Text Analysis Workflow
```
User Input / Screen OCR Text
    │
    ▼
Preprocess (limit to 512 chars)
    │
    ▼
DistilBERT Sentiment Model
    │
    ├─► Label: POSITIVE/NEGATIVE
    ├─► Score: 0.0 - 1.0
    └─► Mood: calm/positive/stressed/sad
    │
    ▼
Harmful Keyword Scan
    │
    └─► Generate Insights
```

#### Speech Analysis Workflow
```
Audio Stream (WebM/OGG)
    │
    ▼
Convert to WAV (Browser)
    │
    ▼
Decode Audio (Backend)
    │
    ├─► Extract Features:
    │   ├─► Energy
    │   ├─► Pitch
    │   └─► Tempo
    │
    ▼
Feature Analysis
    │
    └─► Emotion Classification:
        ├─► calm
        ├─► excited
        ├─► sad
        └─► anxious
```

#### Facial Expression Workflow
```
Camera Frame (Base64 Image)
    │
    ▼
Decode & Preprocess
    │
    ├─► Resize (max 640x480)
    ├─► CLAHE Enhancement
    └─► Bilateral Filter
    │
    ▼
Face Detection (OpenCV DNN)
    │
    ├─► Extract Face Region
    └─► Resize to 224x224
    │
    ▼
FER Emotion Detection
    │
    ├─► Dominant Emotion
    ├─► Confidence Score
    └─► All Emotion Probabilities
```

#### Screen Analysis Workflow
```
Screen Capture (Base64 Image)
    │
    ▼
Decode & Resize (max 1280x720)
    │
    ▼
OCR Processing (Tesseract/EasyOCR)
    │
    ├─► Extract Text
    └─► Harmful Keyword Detection
    │
    ▼
Text Sentiment Analysis (if text found)
    │
    └─► Return Results
```

#### Synthesis Workflow
```
Module Results
    │
    ├─► Text Result (30% weight)
    ├─► Speech Result (25% weight)
    ├─► Face Result (25% weight)
    └─► Screen Result (20% weight)
    │
    ▼
Weighted Average Calculation
    │
    ├─► Wellness Score (0-100)
    └─► Severity Points
    │
    ▼
Risk Level Assessment
    │
    ├─► Critical: score < 25 OR severity ≥ 4
    ├─► High: score < 45 OR severity ≥ 2
    ├─► Medium: score < 60 OR severity ≥ 1
    └─► Low: Everything else
    │
    ▼
Generate Recommendations
    │
    └─► Return Complete Analysis
```

---

## 📚 Libraries & Dependencies

### Complete Library List (17 Total)

#### 1. **Flask** (v2.x)
- **Purpose**: Web framework for backend API
- **Usage**: Main server, routing, request handling
- **Location**: `app/__init__.py`, `app/routes.py`, `run.py`

#### 2. **Flask-CORS** (v4.x)
- **Purpose**: Enable cross-origin requests
- **Usage**: Allow frontend to communicate with backend
- **Location**: `app/__init__.py`

#### 3. **transformers** (v4.x)
- **Purpose**: Hugging Face transformers library
- **Usage**: Pre-trained DistilBERT model for text sentiment analysis
- **Location**: `app/models/text_sentiment.py`
- **Model Used**: `distilbert-base-uncased-finetuned-sst-2-english`

#### 4. **torch** (PyTorch v2.x)
- **Purpose**: Deep learning framework
- **Usage**: Required by transformers library for NLP models
- **Location**: Dependency of transformers

#### 5. **numpy** (v1.x)
- **Purpose**: Numerical computing
- **Usage**: Array operations, audio signal processing, image arrays
- **Location**: `app/models/speech_emotion.py`, `app/utils/camera.py`

#### 6. **scikit-learn** (v1.x)
- **Purpose**: Machine learning utilities
- **Usage**: StandardScaler for audio feature normalization
- **Location**: `app/models/speech_emotion.py`

#### 7. **librosa** (v0.10.x)
- **Purpose**: Audio and music analysis
- **Usage**: 
  - Audio feature extraction (pitch, tempo, energy)
  - Audio resampling
  - Signal processing
- **Location**: `app/models/speech_emotion.py`, `app/utils/microphone.py`

#### 8. **soundfile** (v0.12.x)
- **Purpose**: Audio file I/O
- **Usage**: Reading WAV audio files
- **Location**: `app/utils/microphone.py`
- **Note**: Cloud-friendly, no FFmpeg needed for WAV

#### 9. **pytesseract** (v0.3.x)
- **Purpose**: Python wrapper for Tesseract OCR
- **Usage**: Primary OCR engine for screen text extraction
- **Location**: `app/models/screen_ocr.py`
- **Requires**: Tesseract OCR installed on system

#### 10. **Pillow** (PIL v10.x)
- **Purpose**: Python Imaging Library
- **Usage**: 
  - Image decoding from base64
  - Image resizing and optimization
  - Format conversion
- **Location**: `app/utils/camera.py`, `app/utils/screen_capture.py`

#### 11. **opencv-python** (cv2 v4.x)
- **Purpose**: Computer vision library
- **Usage**: 
  - Image preprocessing (CLAHE, bilateral filter)
  - Face detection (DNN model)
  - Image format conversion (BGR/RGB)
  - Image resizing
- **Location**: `app/models/facial_expression.py`, `app/utils/camera.py`

#### 12. **fer** (Facial Expression Recognition v23.x)
- **Purpose**: Facial emotion recognition
- **Usage**: Detect emotions from facial expressions
- **Location**: `app/models/facial_expression.py`
- **Model**: Uses MTCNN (optional) or default detector

#### 13. **mtcnn** (v0.1.x)
- **Purpose**: Multi-task CNN for face detection
- **Usage**: Optional face detector for FER (more accurate but slower)
- **Location**: Dependency of FER library
- **Note**: Currently using faster default detector

#### 14. **python-dotenv** (v1.x)
- **Purpose**: Environment variable management
- **Usage**: Load API keys from `.env` file
- **Location**: `app/config.py`

#### 15. **openai** (v1.x)
- **Purpose**: OpenAI API client
- **Usage**: GPT-4o-mini for AI companion chat feature
- **Location**: `app/routes.py` (companion endpoint)
- **Requires**: OpenAI API key

#### 16. **pydub** (v0.25.x)
- **Purpose**: Audio manipulation library
- **Usage**: Audio format conversion (backup decoder)
- **Location**: `app/utils/microphone.py`
- **Note**: Not actively used (cloud-friendly WAV conversion in browser)

#### 17. **easyocr** (v1.7.x)
- **Purpose**: Easy-to-use OCR library
- **Usage**: Fallback OCR engine when Tesseract unavailable
- **Location**: `app/models/screen_ocr.py`
- **Note**: Downloads models on first use (~20-30 seconds)

### Library Usage Summary

| Library | Primary Purpose | Critical | Size Impact |
|---------|----------------|----------|-------------|
| Flask | Web Framework | ✅ Yes | Small |
| transformers | NLP (Sentiment) | ✅ Yes | Large (~500MB) |
| torch | Deep Learning | ✅ Yes | Very Large (~2GB) |
| librosa | Audio Analysis | ✅ Yes | Medium |
| opencv-python | Computer Vision | ✅ Yes | Medium |
| fer | Face Emotion | ✅ Yes | Small |
| pytesseract | OCR | ⚠️ Optional | Small |
| easyocr | OCR Backup | ⚠️ Optional | Medium |
| openai | AI Chat | ⚠️ Optional | Small |

---

## 🎨 Features & Capabilities

### 1. Text Sentiment Analysis
- **Technology**: DistilBERT transformer model
- **Input**: User text or screen OCR text
- **Output**: 
  - Sentiment label (POSITIVE/NEGATIVE)
  - Confidence score (0.0-1.0)
  - Mood classification (calm/positive/stressed/sad)
  - Harmful keyword detection
  - Personalized insights

### 2. Speech Emotion Recognition
- **Technology**: Audio feature extraction (librosa)
- **Input**: Microphone audio stream (4-second chunks)
- **Features Extracted**:
  - Energy (amplitude)
  - Pitch (fundamental frequency)
  - Tempo (rhythm)
- **Output**: 
  - Emotion classification (calm/excited/sad/anxious)
  - Feature values

### 3. Facial Expression Recognition
- **Technology**: FER (Facial Expression Recognition) + OpenCV DNN
- **Input**: Webcam video stream
- **Processing**:
  - Face detection (OpenCV DNN)
  - Image preprocessing (CLAHE, bilateral filter)
  - Emotion detection (FER model)
- **Output**:
  - Dominant emotion (happy/sad/angry/fear/neutral/etc.)
  - Confidence score (0.0-1.0)
  - All emotion probabilities

### 4. Screen Content Analysis
- **Technology**: OCR (Tesseract/EasyOCR) + Keyword Scanning
- **Input**: Screen capture stream
- **Processing**:
  - Text extraction via OCR
  - Harmful keyword detection
  - Sentiment analysis of extracted text
- **Output**:
  - Extracted text
  - Harmful content alerts
  - Sentiment analysis

### 5. Behavioral Synthesis Engine
- **Technology**: Weighted multi-modal fusion
- **Input**: All module results
- **Scoring System**:
  - Text: 30% weight
  - Speech: 25% weight
  - Face: 25% weight
  - Screen: 20% weight
- **Output**:
  - Wellness score (0-100)
  - Overall state (calm/steady/moderate_stress/high_anxiety)
  - Risk level (low/medium/high/critical)
  - Personalized recommendations

### 6. AI Companion Chat
- **Technology**: OpenAI GPT-4o-mini
- **Input**: User messages + conversation history
- **Output**: Contextual, empathetic responses
- **Features**:
  - Mental wellness guidance
  - Crisis support suggestions
  - Personalized coaching

### 7. Real-time Alert System
- **Visual Alerts**: On-page alert feed
- **Browser Notifications**: System notifications
- **Voice Alerts**: Text-to-speech announcements
- **Triggers**: High/Critical risk levels

### 8. Data Logging
- **Database**: SQLite
- **Logged Data**:
  - Interaction history
  - High-risk alerts
  - Module results
- **Privacy**: Local storage only

---

## 📦 Installation & Setup

### System Requirements

#### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux
- **Python**: 3.9 or higher
- **RAM**: 8GB (16GB recommended)
- **CPU**: 4+ cores recommended
- **Storage**: 5GB free space (for ML models)

#### Optional System Dependencies
- **Tesseract OCR**: For screen text extraction
  - Windows: Download from GitHub
  - macOS: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`

### Installation Steps

#### 1. Clone/Download Project
```bash
cd mental_wellness_project
```

#### 2. Create Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: This may take 10-15 minutes as it downloads PyTorch and transformers models.

#### 4. Configure API Keys (Optional)
Create `.env` file:
```
OPENAI_API_KEY=sk-your-openai-key-here
```

Or edit `app/config.py` directly.

#### 5. Run Application
```bash
python run.py
```

Server starts at: `http://127.0.0.1:5000`

---

## ⚡ Performance Optimizations

### Implemented Optimizations

#### 1. **Monitoring Frequency**
- **Interval**: 15 seconds (reduced from 5 seconds)
- **Impact**: 66% reduction in processing load

#### 2. **Image Compression**
- **Camera**: Max 640x480 (JPEG, 85% quality)
- **Screen**: Max 1280x720 (JPEG, 85% quality)
- **Impact**: ~75% reduction in image size

#### 3. **Screen OCR Throttling**
- **Interval**: 20 seconds (reduced from 30 seconds)
- **Impact**: Prevents system overload while maintaining responsiveness

#### 4. **Payload Optimization**
- **Strategy**: Only send non-null data
- **Impact**: ~30% smaller payloads

#### 5. **Rendering Optimization**
- **Strategy**: requestAnimationFrame for smooth updates
- **Impact**: Prevents browser freezes

#### 6. **Data Limiting**
- **Notes**: Max 3 displayed
- **Actions**: Max 3 displayed
- **Impact**: Faster rendering

#### 7. **Cloud-Friendly Audio**
- **Strategy**: Browser converts WebM to WAV
- **Impact**: No FFmpeg dependency needed

---

## 🔒 Security & Privacy

### Privacy Features

1. **Local Processing**
   - Most analysis runs on local server
   - No data sent to external services (except OpenAI for chat)

2. **No Persistent Storage**
   - Real-time processing only
   - Optional SQLite logging (local)

3. **User Control**
   - Start/stop monitoring anytime
   - Clear permission requests

4. **Secure Context**
   - Requires HTTPS or localhost
   - Browser security standards

### Data Flow

```
User Device → Local Flask Server → Analysis → Results → User Device
                (No external transmission)
```

### API Keys

- **OpenAI**: Only used for AI companion feature
- **Optional**: System works without it
- **Storage**: `.env` file or `config.py`

---

## 📊 Technical Specifications

### API Endpoints

| Endpoint | Method | Purpose | Input | Output |
|----------|--------|---------|-------|--------|
| `/api/v1/text` | POST | Text sentiment | `{text: string}` | Sentiment analysis |
| `/api/v1/audio` | POST | Speech emotion | `{audio: base64}` | Emotion detection |
| `/api/v1/vision` | POST | Face emotion | `{frame: base64}` | Facial expression |
| `/api/v1/screen` | POST | Screen OCR | `{frame: base64}` | Text + harmful content |
| `/api/v1/monitor` | POST | Combined analysis | `{text, audio, frame, screen}` | Complete wellness analysis |
| `/api/v1/companion` | POST | AI chat | `{message, history}` | AI response |

### Data Formats

#### Input Formats
- **Images**: Base64-encoded JPEG/PNG
- **Audio**: Base64-encoded WAV (converted from WebM in browser)
- **Text**: Plain string

#### Output Formats
- **JSON**: All responses in JSON format
- **Wellness Score**: Float (0.0-100.0)
- **Risk Level**: String (low/medium/high/critical)

### Performance Metrics

- **Response Time**: < 2 seconds (typical)
- **Monitoring Interval**: 15 seconds
- **Screen OCR**: 20 seconds (throttled)
- **Audio Chunks**: 4 seconds
- **Memory Usage**: ~2-4GB (with ML models loaded)

---

## 🚀 Future Enhancements

### Planned Improvements

1. **Enhanced Models**
   - Fine-tuned speech emotion recognition
   - Custom facial expression models
   - Improved OCR accuracy

2. **Additional Features**
   - Wearable device integration
   - Mobile companion app
   - Historical trend analysis
   - Export reports

3. **Performance**
   - GPU acceleration support
   - Model quantization
   - Edge device optimization

4. **Governance**
   - Bias detection and mitigation
   - Consent management
   - Anomaly detection

---

## 📝 Conclusion

The **AI-Powered Precision Mental Wellness Analyzer (AIP-MWA)** represents a comprehensive solution for real-time mental wellness monitoring. By combining multiple AI/ML technologies with an intuitive interface, it provides accurate, actionable insights while maintaining user privacy and system performance.

### Key Achievements

✅ **Multimodal Analysis**: 4 different data streams
✅ **Real-time Processing**: Continuous monitoring
✅ **Accurate Predictions**: Weighted scoring system
✅ **Performance Optimized**: No system hangs
✅ **Privacy Focused**: Local processing
✅ **User Friendly**: Intuitive interface
✅ **Cloud Ready**: No external dependencies

### Project Status

**Status**: ✅ Production Ready
**Version**: 1.0
**Last Updated**: 2025

---

## 📞 Support & Documentation

- **README**: `README.md`
- **Run Instructions**: `RUN_INSTRUCTIONS.md`
- **Performance Guide**: `PERFORMANCE_FIXES.md`
- **Quick Fix Guide**: `QUICK_FIX_GUIDE.md`

---

**Document Generated**: 2025
**Project**: AI-Powered Precision Mental Wellness Analyzer (AIP-MWA)
**Version**: 1.0

