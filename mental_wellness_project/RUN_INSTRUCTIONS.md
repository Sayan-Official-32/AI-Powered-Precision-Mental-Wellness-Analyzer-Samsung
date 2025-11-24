# How to Run the Mental Wellness Project

## Prerequisites

1. **Python 3.9 or higher** - Check with: `python --version`
2. **Tesseract OCR** (for screen content analysis)
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install and add to PATH
   - Verify: `tesseract --version`

## Step-by-Step Setup

### 1. Navigate to Project Directory
```powershell
cd mental_wellness_project
```

### 2. Create Virtual Environment
```powershell
python -m venv .venv
```

### 3. Activate Virtual Environment
```powershell
.venv\Scripts\activate
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

**Note:** This may take several minutes as it installs PyTorch, transformers, and other ML libraries.

### 5. (Optional) Configure OpenAI API Key
If you want to use the AI Companion feature, create a `.env` file in the `mental_wellness_project` folder:

```
OPENAI_API_KEY=sk-your-openai-key-here
```

Or edit `app/config.py` and replace the default API key.

**Note:** The project works without OpenAI - only the companion chat feature requires it.

### 6. Run the Application

**Option A: Using Python directly (Recommended)**
```powershell
python run.py
```

**Option B: Using Flask CLI**
```powershell
flask --app run run
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 7. Open in Browser
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

## First Run Notes

- On the first run, the OpenCV DNN face detector models will be automatically downloaded (this may take a minute)
- The models will be saved in the `models/` directory
- The database file (`mental_wellness.db`) will be created automatically

## Using the Application

1. **Grant Permissions:** The browser will ask for:
   - Camera access (for facial expression detection)
   - Microphone access (for speech emotion recognition)
   - Screen capture permission (for screen content analysis)

2. **Start Monitoring:** Click "Start Monitoring" to begin real-time analysis

3. **Features Available:**
   - Text sentiment analysis
   - Speech emotion recognition
   - Facial expression detection (now with enhanced OpenCV preprocessing!)
   - Screen content scanning
   - Wellness score calculation
   - AI Companion chat (if API key is configured)

## Troubleshooting

### Port Already in Use
If port 5000 is busy, edit `run.py` and change:
```python
app.run(debug=True, port=5001)  # Use different port
```

### Tesseract Not Found
- Make sure Tesseract is installed and in your PATH
- Or set the path in code if needed

### Module Import Errors
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

### OpenCV DNN Model Download Issues
- Check internet connection
- Models will be downloaded on first use
- If download fails, the code will fall back to the original FER detector

## Stopping the Server

Press `Ctrl+C` in the terminal to stop the Flask server.

