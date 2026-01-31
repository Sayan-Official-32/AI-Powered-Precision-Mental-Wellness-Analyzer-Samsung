## AI-Powered Precision Mental Wellness Analyzer (AIP-MWA)

A multimodal Flask application that monitors text, speech, facial expressions, and real-time screen content to estimate a live wellness score, deliver personalized recommendations, and trigger emergency nudges when harmful or risky signals are detected.

### Features
- **Text Analysis:** Transformer sentiment, harmful keyword scanning, and reflective insights.
- **Speech Emotion Recognition:** Audio energy, pitch, tempo features to infer arousal/sadness/anxiety.
- **Facial Expression Recognition:** FER (MT-CNN) model to read dominant emotions from webcam frames.
- **Screen Guardian:** OCR-based scanner that warns whenever the displayed content contains harmful keywords.
- **Behavioral Synthesis Engine:** Fuses every modality into a 0–100 wellness score + action plan.
- **AI Companion:** GPT-powered conversational coach for text or voice-style chats.

### Project Structure
```
mental_wellness_project/
├── app/
│   ├── __init__.py            # Flask factory + CORS + static serving
│   ├── config.py              # Settings + API keys + behavioral thresholds
│   ├── database.py            # SQLite setup + logging helpers
│   ├── models/                # ML modules (text, speech, face, screen, synthesis)
│   ├── routes.py              # REST API (text/audio/vision/screen/monitor/companion)
│   └── utils/                 # Media decoding helpers
├── frontend/                  # Static HTML/CSS/JS single page
├── requirements.txt
└── run.py
```

### Getting Started
1. **Install system prerequisites**
   - Python 3.9+
   - Tesseract OCR (required for `pytesseract`)
2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
3. **Configure API keys**
   - Create a `.env` file in `mental_wellness_project/` with:
     ```
     OPENAI_API_KEY=sk-your-openai-key
     HUGGINGFACEHUB_API_TOKEN=optional_if_using_hf_hub
     ```
   - Alternatively, open `app/config.py` and replace `openai_api_key` default with your OpenAI key. The project expects an **OpenAI platform key** (https://platform.openai.com/) for the `/api/v1/companion` route that powers the conversational AI. No other API keys are mandatory—the NLP/speech/vision pipelines run locally.
4. **Run the backend**
   ```bash
   cd mental_wellness_project
   flask --app run run
   ```
   Then open `http://127.0.0.1:5000` in your browser.

### Browser Permissions & Privacy
- The monitoring dashboard prompts for microphone, camera, and screen capture permissions.
- Streams are sent to your local Flask server only; data isn’t persisted beyond charting unless an alert is logged in SQLite for auditing.
- Disable monitoring with the “Stop Monitoring” button at any time.

### Extending / Future Work
- Replace heuristic speech features with a fine-tuned SER network.
- Swap FER with a custom MediaPipe model for on-device efficiency.
- Add wearable integrations and a mobile companion app.
- Expand risk governance (bias, consent logging, anomaly detection).

### Troubleshooting
- **OpenAI errors:** Ensure the key is valid and has access to the `gpt-4o-mini` model.
- **OCR blank:** Verify Tesseract is installed and added to PATH.
- **Permission errors:** Browsers require HTTPS for screen capture in production—use localhost for dev.

