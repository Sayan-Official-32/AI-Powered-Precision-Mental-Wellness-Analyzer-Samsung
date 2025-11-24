# Performance Issues & Solutions

## Why Your Laptop Hangs

Your backend is running **extremely resource-intensive operations** that overload your system:

### Main Problems:

1. **Screen OCR Every 5 Seconds** ⚠️ **CRITICAL**
   - EasyOCR/Tesseract processes full-screen images every 5 seconds
   - OCR is one of the most CPU/memory-intensive operations
   - Each screen capture can be 1920x1080+ pixels
   - **Solution**: Increase interval to 15-30 seconds, or disable screen OCR

2. **Multiple Heavy ML Models Loaded**
   - PyTorch transformers (text sentiment)
   - FER (facial expression recognition)
   - EasyOCR (screen text recognition)
   - OpenCV DNN models
   - All loaded in memory simultaneously
   - **Solution**: Lazy loading, model caching, or disable unused features

3. **High-Frequency Monitoring**
   - Camera frames processed every 5 seconds
   - Audio processing with librosa (CPU-intensive)
   - Facial detection on every frame
   - **Solution**: Increase interval to 10-15 seconds

4. **Large Image Processing**
   - Full-resolution camera frames (can be 1920x1080)
   - Full-screen captures sent to backend
   - No compression before sending
   - **Solution**: Resize/compress images before sending

5. **No Resource Throttling**
   - All operations run simultaneously
   - No queue or rate limiting
   - **Solution**: Add processing delays and queues

## Solutions Implemented

### 1. Increased Monitoring Interval
- Changed from 5 seconds to **15 seconds** (3x less frequent)
- Reduces CPU load by ~66%

### 2. Image Compression
- Added automatic image resizing before sending to backend
- Camera frames: max 640x480
- Screen captures: max 1280x720
- Reduces data transfer and processing time

### 3. Screen OCR Throttling
- Screen OCR now runs every **30 seconds** instead of every 15 seconds
- Can be completely disabled if needed

### 4. Optimized Processing
- Added timeouts for heavy operations
- Better error handling to prevent hangs
- Graceful degradation if models fail

## Quick Fixes You Can Apply

### Option 1: Disable Screen OCR (Fastest Fix)
Edit `frontend/app.js` line 122:
```javascript
// Change from:
monitorInterval = setInterval(pushMonitorSnapshot, 5000);

// To:
monitorInterval = setInterval(pushMonitorSnapshot, 30000); // 30 seconds
```

And disable screen capture in `app/routes.py` by commenting out screen analysis.

### Option 2: Use Lower Resolution
The code now automatically resizes images, but you can make it even smaller.

### Option 3: Disable Unused Features
- If you don't need facial recognition, disable it
- If you don't need speech analysis, disable it
- Only enable what you actually use

## System Requirements

**Minimum Recommended:**
- CPU: 4+ cores
- RAM: 8GB+ (16GB recommended)
- GPU: Optional but helps with ML models

**If your laptop has less:**
- Disable screen OCR completely
- Increase all intervals to 30+ seconds
- Use only text sentiment analysis (lightest feature)

## Monitoring Resource Usage

To check what's using resources:
1. Open Task Manager (Ctrl+Shift+Esc)
2. Look for Python processes
3. Check CPU and Memory usage
4. If Python is using >80% CPU, reduce monitoring frequency

## Emergency: If Laptop Freezes

1. **Force Stop**: Press Ctrl+C in the terminal running the backend
2. **Task Manager**: End Python processes if needed
3. **Restart**: Reboot if completely frozen
4. **Disable Features**: Edit code to disable heavy features before restarting

