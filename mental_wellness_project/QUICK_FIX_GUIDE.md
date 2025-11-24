# Quick Fix Guide - System Performance Issues

## ✅ What I Fixed

### 1. **Reduced Monitoring Frequency**
- **Before**: Every 5 seconds
- **After**: Every 15 seconds
- **Impact**: 66% reduction in processing load

### 2. **Image Compression**
- **Before**: Full resolution images (1920x1080+)
- **After**: 
  - Camera: Max 640x480
  - Screen: Max 1280x720
  - JPEG compression (85% quality)
- **Impact**: ~75% reduction in image size and processing time

### 3. **Screen OCR Throttling**
- **Before**: OCR on every monitoring cycle (every 5 seconds)
- **After**: OCR only every 30 seconds
- **Impact**: 83% reduction in OCR processing (most CPU-intensive operation)

## 🚀 How to Use

1. **Restart your backend** - The changes are already in place
2. **Test the system** - It should run much smoother now
3. **Monitor Task Manager** - Check if CPU usage is lower

## ⚠️ If Still Having Issues

### Option 1: Disable Screen OCR Completely
Edit `app/routes.py` and comment out the screen analysis section (around line 109-147).

### Option 2: Increase Intervals Further
Edit `frontend/app.js` line 122:
```javascript
// Change to 30 seconds or more
monitorInterval = setInterval(pushMonitorSnapshot, 30000);
```

Edit `app/routes.py` line 17:
```python
_SCREEN_OCR_INTERVAL = 60  # Change to 60 seconds or more
```

### Option 3: Disable Heavy Features
- **Disable facial recognition**: Comment out face analysis in routes.py
- **Disable speech analysis**: Comment out audio analysis in routes.py
- **Keep only text sentiment**: Lightest feature, uses minimal resources

## 📊 Expected Performance

**Before fixes:**
- CPU: 80-100% (system hangs)
- Memory: High usage
- Screen: Laggy/frozen

**After fixes:**
- CPU: 30-50% (normal operation)
- Memory: Moderate usage
- Screen: Smooth operation

## 🔧 Additional Tips

1. **Close other heavy applications** while running the backend
2. **Use a modern browser** (Chrome, Edge, Firefox)
3. **Check system resources** in Task Manager before starting
4. **Start with minimal features** and add more as needed

## 🆘 Emergency: If System Freezes

1. Press `Ctrl+C` in the terminal to stop the backend
2. Open Task Manager (`Ctrl+Shift+Esc`)
3. End all Python processes
4. Restart your computer if needed
5. Before restarting backend, disable heavy features first

