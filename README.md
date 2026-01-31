🧠 AI-Powered Precision Mental Wellness Analyzer

An AI-driven multimodal mental wellness monitoring system that analyzes text, speech, facial expressions, and screen activity in real time to estimate a user's mental wellness score, detect high-risk behavior, and provide supportive interventions.

This project is designed as an intelligent, privacy-aware wellness assistant suitable for research, academic projects, and prototype healthcare applications.

 How to Run the Project
1. **Install system prerequisites**
   - Python 3.9+
   - Tesseract OCR (required for `pytesseract`)
  
2. **Clone the Repository**
   ```
    git clone <your-repo-link>
    cd mental_wellness_project
   ```
3. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
4. **Configure API keys**
   - Create a `.env` file in `mental_wellness_project/` with:
     ```
     OPENAI_API_KEY=sk-your-openai-key
     HUGGINGFACEHUB_API_TOKEN=optional_if_using_hf_hub
     ```
   - Alternatively, open `app/config.py` and replace `openai_api_key` default with your OpenAI key. The project expects an **OpenAI platform key** (https://platform.openai.com/) for the `/api/v1/companion` route that powers the conversational AI. No other API keys are mandatory—the NLP/speech/vision pipelines run locally.
5. **Run the backend**
   ```bash
   cd mental_wellness_project
   flask --app run run
   ```
   Then open `http://127.0.0.1:5000` in your browser.

📌 Project Overview

The AI-Powered Precision Mental Wellness Analyzer (AIP-MWA) continuously monitors multiple human interaction signals and fuses them into a single wellness prediction pipeline.

It detects:

Emotional distress

Negative sentiment trends

Facial stress indicators

Harmful or risky patterns

And responds with:

Wellness insights

Alerts

Preventive nudges

Emergency recommendations (non-medical)

🎯 Key Features
Feature	Description
📝 Text Sentiment Analysis	Detects emotional tone and harmful keywords
🎙 Speech Emotion Recognition	Analyzes pitch, energy, and tempo from voice
😀 Facial Expression Analysis	Detects stress and emotion via webcam
🖥 Screen OCR Monitoring	Reads on-screen text using OCR
🧠 Behavior Synthesis	Combines all signals into a wellness score
🚨 High-Risk Alerts	Triggers warnings for dangerous patterns
🤖 AI Chatbot	Supportive conversational assistant
📊 Live Wellness Score	Continuous mental health indicator
🏗 Project Architecture
mental_wellness_project/
│
├── app/
│   ├── models/
│   │   ├── text_sentiment.py
│   │   ├── speech_emotion.py
│   │   ├── facial_expression.py
│   │   ├── screen_ocr.py
│   │   └── behavior_synthesis.py
│   │
│   ├── routes.py
│   ├── config.py
│   └── database.py
│
├── run.py
├── requirements.txt
├── PROJECT_OVERVIEW.md
├── RUN_INSTRUCTIONS.md
└── README.md

🧩 Module Description
Module	Purpose
text_sentiment.py	NLP-based emotional & harmful text detection
speech_emotion.py	Audio feature extraction for emotion
facial_expression.py	Face detection & emotion inference
screen_ocr.py	OCR-based screen content monitoring
behavior_synthesis.py	Fuses all predictions into final score
routes.py	Flask API routing
database.py	Session & event logging
🛠 Technologies Used
🔹 Programming & Frameworks

Python 3.10+

Flask – Web framework

HTML / CSS / JavaScript – UI

🔹 Machine Learning & AI

Transformers

Scikit-learn

NumPy

TensorFlow / PyTorch (model-ready)

🔹 Computer Vision & Audio

OpenCV

MediaPipe

Librosa

SpeechRecognition

🔹 OCR & NLP

Tesseract OCR

NLTK

HuggingFace Models

📦 Required Libraries

Install all dependencies using:

pip install -r requirements.txt


Key libraries include:

flask

opencv-python

mediapipe

numpy

librosa

speechrecognition

pytesseract

transformers

torch

scikit-learn

⚙ Operating Procedure (How It Works)

User Interaction Begins

Text input, speech, camera, or screen activity

Signal Processing

Each input is processed independently

AI Model Analysis

Emotion, sentiment, and risk prediction

Behavior Fusion

All outputs combined into a wellness score

Decision Engine

Normal → Feedback

Risky → Alert

Critical → Emergency nudge

🚨 Safety & Ethical Notice

⚠ This system is NOT a medical diagnostic tool.
It is intended for:

Research

Awareness

Early detection

Educational use only

For medical emergencies, users must contact licensed professionals.

🌍 Use Cases

Mental wellness monitoring

Academic AI projects

Human–computer interaction research

Preventive mental health tools

Smart assistant prototypes

📌 Future Enhancements

Mobile app integration

Cloud-based model deployment

Federated learning

Encrypted data storage

Doctor dashboard integration

👨‍💻 Author & Credits

Developed as an AI-powered mental wellness research prototype
Special focus on multimodal intelligence & ethical AI design
