# Audio Decoding Fix

## Problem
The microphone audio recording was failing with error:
```
ERROR:app.utils.microphone:All audio decoders failed; returning empty signal.
```

## Solution Applied

### 1. **Improved Backend Audio Decoding**
- Added multiple decoder support (pydub, librosa, soundfile)
- Better WebM/OGG format handling
- Improved error messages

### 2. **Frontend Audio Conversion**
- Better WAV conversion error handling
- Fallback to original format if conversion fails

## Required: Install FFmpeg

**For WebM audio to work, you need FFmpeg installed on your system.**

### Windows Installation:

1. **Download FFmpeg:**
   - Go to: https://www.gyan.dev/ffmpeg/builds/
   - Download "ffmpeg-release-essentials.zip"
   - Or use: https://github.com/BtbN/FFmpeg-Builds/releases

2. **Extract and Add to PATH:**
   - Extract the zip file (e.g., to `C:\ffmpeg`)
   - Add `C:\ffmpeg\bin` to your system PATH:
     - Right-click "This PC" → Properties
     - Advanced System Settings → Environment Variables
     - Edit "Path" under System Variables
     - Add: `C:\ffmpeg\bin`
     - Click OK on all dialogs

3. **Verify Installation:**
   ```powershell
   ffmpeg -version
   ```
   Should show version information.

4. **Restart your terminal/IDE** after adding to PATH

### Alternative: Use Chocolatey (if installed)
```powershell
choco install ffmpeg
```

## After Installing FFmpeg

1. **Restart your backend server**
2. **Test microphone recording** - it should now work!

## If Still Not Working

### Check FFmpeg Installation:
```powershell
ffmpeg -version
```

### Check Python can find FFmpeg:
```python
from pydub import AudioSegment
# This should not error
```

### Test Audio Decoding:
The backend will now try multiple methods:
1. pydub (needs ffmpeg for WebM)
2. librosa (needs ffmpeg for WebM)
3. soundfile (for WAV files)

### Browser Compatibility:
- **Chrome/Edge**: Uses WebM format (needs ffmpeg)
- **Firefox**: Uses OGG format (needs ffmpeg)
- **Safari**: Uses different format

### If FFmpeg is not available:
The frontend will try to convert to WAV, but if that fails, the backend will still try to decode the original format. However, WebM/OGG support is limited without ffmpeg.

## Troubleshooting

1. **"All audio decoders failed"**
   - Install FFmpeg (see above)
   - Restart backend after installation
   - Check browser console for audio conversion errors

2. **"Microphone not available"**
   - Grant microphone permissions in browser
   - Check browser settings

3. **"WAV conversion failed"**
   - This is okay - backend will try to decode original format
   - Make sure FFmpeg is installed for best results

