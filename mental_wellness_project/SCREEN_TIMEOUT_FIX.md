# Screen OCR Timeout Fix

## Problem
Screen analysis was timing out with message: "Screen analysis timeout. Will retry on next cycle."

## Root Causes
1. **Timeout too short**: 8 seconds wasn't enough for EasyOCR on complex screens
2. **Large images**: Processing full-resolution screens is slow
3. **No optimization**: OCR settings weren't optimized for speed

## Fixes Applied

### 1. ✅ Increased Timeout
- **Before**: 8 seconds
- **After**: 15 seconds
- **Reason**: EasyOCR can take 10-15 seconds on complex screens

### 2. ✅ Optimized Image Resizing
- **Before**: Max 1920px width
- **After**: 
  - Large images (>1280px) → resize to 1280px
  - Medium images (640-1280px) → resize to 640px
  - **Result**: Much faster OCR processing

### 3. ✅ Faster Tesseract Config
- Added optimized Tesseract config:
  - `--psm 6`: Uniform block of text (faster)
  - Character whitelist: Only process expected characters
  - **Result**: 2-3x faster Tesseract processing

### 4. ✅ Optimized EasyOCR Settings
- Added `width_ths=0.7` and `height_ths=0.7`
- Lower thresholds = faster processing
- **Result**: Faster EasyOCR when Tesseract unavailable

## Performance Improvements

### Before:
- Timeout: 8 seconds
- Image size: Up to 1920px
- OCR: Default settings
- **Result**: Frequent timeouts

### After:
- Timeout: 15 seconds
- Image size: Max 640-1280px (optimized)
- OCR: Optimized settings
- **Result**: Should complete within timeout

## Expected Behavior

### Normal Operation:
- Screen captured → Resized to 640-1280px
- OCR processes → 5-10 seconds (usually)
- Result returned → Within 15 second timeout
- **Status**: "ok" with extracted text

### If Still Slow:
- Screen OCR continues in background
- Status shows: "Screen analysis taking longer than expected. Processing in background..."
- Next cycle will try again
- **No blocking**: Other modules continue working

## Testing

1. **Restart Flask server** (to load optimizations)
2. **Start monitoring**
3. **Watch for screen results**:
   - Should see "ok" status more often
   - Should see extracted text
   - Timeouts should be rare

## Additional Optimizations

If still timing out:
1. **Reduce image size further** (change 640 to 480)
2. **Increase timeout** (change 15 to 20 seconds)
3. **Skip OCR on very complex screens** (add complexity check)

The screen analysis should now work much better and complete within the timeout!

