import re
from threading import Lock
from typing import Dict, List, Optional

import numpy as np
import pytesseract
from pytesseract import TesseractNotFoundError

from app.config import settings
from app.utils.screen_capture import decode_base64_screen

_easyocr_reader = None
_easyocr_available = None  # None = not checked, True = available, False = unavailable
_easyocr_lock = Lock()  # Thread-safe initialization lock
_easyocr_initializing = False  # Flag to prevent multiple initializations
_tesseract_warning_shown = False  # Only show Tesseract warning once


def _check_easyocr_available():
    """Check if EasyOCR can be imported (doesn't initialize the reader)"""
    global _easyocr_available
    if _easyocr_available is not None:
        return _easyocr_available
    try:
        import easyocr
        _easyocr_available = True
        return True
    except ImportError:
        _easyocr_available = False
        return False
    except Exception:
        _easyocr_available = False
        return False


def is_easyocr_initializing():
    """Check if EasyOCR is currently initializing (public function)"""
    global _easyocr_initializing
    return _easyocr_initializing


def _preprocess_image_for_ocr(image):
    """Preprocess image to improve OCR accuracy"""
    try:
        import cv2
        
        # Convert PIL to numpy array if needed
        if hasattr(image, 'size'):
            img_array = np.array(image)
        else:
            img_array = image
        
        # Convert to grayscale if color
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Apply sharpening
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        # Convert back to PIL Image
        from PIL import Image
        return Image.fromarray(sharpened)
    except Exception as e:
        print(f"Image preprocessing error: {e}, using original image")
        return image


def _clean_ocr_text(text: str) -> str:
    """Clean and filter OCR text to remove garbled characters and improve readability"""
    if not text:
        return ""
    
    # Remove common OCR garbage patterns
    # Remove lines with too many random characters (likely OCR errors)
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Count readable characters (letters, numbers, spaces, punctuation)
        readable_chars = sum(1 for c in line if c.isalnum() or c in ' .,!?;:()[]{}\'"-+=@#$%&*')
        total_chars = len(line)
        
        # Skip lines that are mostly unreadable (less than 60% readable)
        if total_chars > 0 and readable_chars / total_chars < 0.6:
            continue
        
        # Remove lines that are too short and contain mostly random characters
        if len(line) < 3:
            continue
        
        # Remove common OCR error patterns
        # Remove lines with too many consecutive consonants (likely OCR errors)
        consecutive_consonants = max(
            (len(match.group()) for match in re.finditer(r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]{5,}', line)),
            default=0
        )
        if consecutive_consonants > 5:
            continue
        
        # Clean up the line
        # Remove excessive whitespace
        line = re.sub(r'\s+', ' ', line)
        # Remove leading/trailing special characters
        line = line.strip('.,!?;:()[]{}\'"-+=@#$%&*')
        
        if len(line) >= 3:  # Only keep lines with at least 3 characters
            cleaned_lines.append(line)
    
    # Join cleaned lines
    cleaned_text = '\n'.join(cleaned_lines)
    
    # Remove excessive newlines
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    # Final cleanup: remove lines that are mostly numbers with random letters
    final_lines = []
    for line in cleaned_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        # Skip lines that are mostly numbers with few words
        words = line.split()
        if len(words) < 2 and any(len(w) > 10 for w in words):
            # Likely a garbled number/string
            continue
        final_lines.append(line)
    
    return '\n'.join(final_lines).strip()


def _ensure_easyocr_reader():
    global _easyocr_reader, _easyocr_initializing
    
    # Fast path: already initialized
    if _easyocr_reader is not None:
        if _easyocr_reader is False:
            return False
        return _easyocr_reader
    
    # Thread-safe initialization
    with _easyocr_lock:
        # Double-check after acquiring lock
        if _easyocr_reader is not None:
            return _easyocr_reader if _easyocr_reader is not False else False
        
        # Check if another thread is already initializing
        if _easyocr_initializing:
            # Don't block - return None to indicate initialization in progress
            # The caller will handle this gracefully
            return None
        
        # Start initialization
        _easyocr_initializing = True
        try:
            import easyocr
            print("Initializing EasyOCR (first time may take 20-30 seconds to download models)...")
            _easyocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
            print("EasyOCR initialized successfully!")
            return _easyocr_reader
        except ImportError as e:
            print(f"EasyOCR not installed. Run: pip install easyocr. Error: {e}")
            _easyocr_reader = False
            return False
        except Exception as exc:
            print(f"EasyOCR initialization failed: {exc}")
            import traceback
            traceback.print_exc()
            _easyocr_reader = False
            return False
        finally:
            _easyocr_initializing = False


def _easyocr_text(image, min_confidence: float = 0.3) -> Optional[str]:
    """
    Returns:
        str: Extracted text (may be empty string if no text found)
        None: Error occurred (OCR unavailable, failed, or still initializing)
    """
    reader = _ensure_easyocr_reader()
    if reader is None or reader is False:
        return None
    try:
        # Convert PIL Image to numpy array (image is already resized in analyze_screen_content)
        if hasattr(image, 'size'):
            img_array = np.array(image)
        else:
            img_array = image
        
        # Use detail=1 to get confidence scores, then filter by confidence
        result = reader.readtext(
            img_array, 
            detail=1,  # detail=1 returns (bbox, text, confidence)
            paragraph=False,  # Don't merge into paragraphs yet
            allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,!?;:()[]{}\'"-+=@#$%&*',
            width_ths=0.7,
            height_ths=0.7,
        )
        
        # Filter by confidence and extract text
        filtered_texts = []
        for detection in result:
            bbox, text, confidence = detection
            # Only keep text with confidence above threshold
            if confidence >= min_confidence and text.strip():
                filtered_texts.append(text.strip())
        
        text = "\n".join(filtered_texts).strip()
        
        # Clean the text to remove garbled characters
        text = _clean_ocr_text(text)
        
        return text  # Return empty string if no text found (this is valid)
    except Exception as exc:
        print(f"EasyOCR read error: {exc}")
        import traceback
        traceback.print_exc()
        return None  # Return None only on actual error


def analyze_screen_content(image_b64: str) -> Dict:
    global _tesseract_warning_shown, _easyocr_initializing
    try:
        if not image_b64:
            return {"text": "", "harmful_hits": [], "status": "no_frame"}

        screenshot = decode_base64_screen(image_b64)
        if screenshot is None:
            return {"text": "", "harmful_hits": [], "status": "no_frame"}
        
        # Validate and resize image dimensions for faster processing
        try:
            width, height = screenshot.size
            if width == 0 or height == 0:
                return {"text": "", "harmful_hits": [], "status": "error", "error": "Invalid image dimensions"}
            
            # Resize large images to speed up OCR (max 1280px width for faster processing)
            # Smaller images = faster OCR while maintaining readability
            if width > 1280:
                scale = 1280 / width
                new_width = 1280
                new_height = int(height * scale)
                from PIL import Image
                screenshot = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"Resized screen image from {width}x{height} to {new_width}x{new_height} for faster OCR")
            elif width > 640 and width <= 1280:
                # Medium size - resize to 640 for even faster processing
                scale = 640 / width
                new_width = 640
                new_height = int(height * scale)
                from PIL import Image
                screenshot = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"Resized screen image from {width}x{height} to {new_width}x{new_height} for faster OCR")
            
            # Preprocess image to improve OCR accuracy
            screenshot = _preprocess_image_for_ocr(screenshot)
        except Exception as e:
            print(f"Image validation/resize error: {e}")
            return {"text": "", "harmful_hits": [], "status": "error", "error": f"Image processing failed: {str(e)[:100]}"}

        # Quick check: if EasyOCR is initializing, return immediately to avoid blocking
        if _easyocr_initializing:
            return {
                "text": "",
                "harmful_hits": [],
                "status": "initializing",
                "note": "EasyOCR is initializing (first time may take 20-30 seconds). Please wait...",
            }

        text = ""
        ocr_method = "none"
        
        # Try Tesseract first (faster than EasyOCR)
        try:
            # Use optimized Tesseract config for better accuracy
            # --psm 6: Uniform block of text (good for screen content)
            # --oem 3: Default OCR Engine Mode (LSTM + Legacy)
            text = pytesseract.image_to_string(
                screenshot, 
                config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,!?;:()[]{}\'"-+=@#$%&*'
            )
            # Clean the text to remove garbled characters
            text = _clean_ocr_text(text)
            ocr_method = "tesseract"
        except TesseractNotFoundError:
            if not _tesseract_warning_shown:
                print("Tesseract not found, using EasyOCR fallback...")
                _tesseract_warning_shown = True
            # First check if EasyOCR can be imported
            if not _check_easyocr_available():
                return {
                    "text": "",
                    "harmful_hits": [],
                    "status": "unavailable",
                    "note": "OCR not available. Install Tesseract (see README) or run: pip install easyocr",
                }
            # Check if EasyOCR reader can be initialized
            reader = _ensure_easyocr_reader()
            if reader is None:
                # Still initializing
                return {
                    "text": "",
                    "harmful_hits": [],
                    "status": "initializing",
                    "note": "EasyOCR is initializing (first time may take 20-30 seconds). Please wait...",
                }
            if reader is False:
                # EasyOCR failed to initialize
                return {
                    "text": "",
                    "harmful_hits": [],
                    "status": "unavailable",
                    "note": "EasyOCR failed to initialize. Check server logs. First run may take time to download models.",
                }
            # Try EasyOCR fallback
            text = _easyocr_text(screenshot)
            if text is None:
                # EasyOCR failed to read (error occurred)
                return {
                    "text": "",
                    "harmful_hits": [],
                    "status": "unavailable",
                    "note": "EasyOCR failed to process image. Check server logs for details.",
                }
            # text is a string (may be empty if no text found - that's OK)
            ocr_method = "easyocr"
        except Exception as ocr_err:
            if not _tesseract_warning_shown:
                print(f"Tesseract OCR error: {ocr_err}, using EasyOCR fallback...")
                _tesseract_warning_shown = True
            if not _check_easyocr_available():
                return {
                    "text": "",
                    "harmful_hits": [],
                    "status": "unavailable",
                    "note": f"OCR unavailable. Tesseract error: {str(ocr_err)[:100]}. Install EasyOCR: pip install easyocr",
                }
            reader = _ensure_easyocr_reader()
            if reader is None:
                return {
                    "text": "",
                    "harmful_hits": [],
                    "status": "initializing",
                    "note": "EasyOCR is initializing (first time may take 20-30 seconds). Please wait...",
                }
            if reader is False:
                return {
                    "text": "",
                    "harmful_hits": [],
                    "status": "unavailable",
                    "note": f"OCR unavailable. Tesseract error: {str(ocr_err)[:100]}. EasyOCR failed to initialize.",
                }
            text = _easyocr_text(screenshot)
            if text is None:
                print(f"Both OCR methods failed. Tesseract error: {ocr_err}")
                return {
                    "text": "",
                    "harmful_hits": [],
                    "status": "unavailable",
                    "note": f"OCR unavailable. Error: {str(ocr_err)[:100]}",
                }
            # text is a string (may be empty if no text found - that's OK)
            ocr_method = "easyocr"

        # Only return text if it's meaningful (not just garbled characters)
        if text and len(text.strip()) > 0:
            # Additional validation: check if text contains at least some readable words
            words = text.split()
            readable_words = [w for w in words if any(c.isalpha() for c in w) and len(w) >= 2]
            
            if len(readable_words) == 0:
                # No readable words found, likely all garbled
                text = ""
                status = "no_text"
            else:
                status = "ok"
        else:
            status = "no_text"
        
        harmful_hits: List[str] = [
            keyword for keyword in settings.harmful_keywords if keyword.lower() in text.lower()
        ] if text else []

        return {
            "text": text if text else "",
            "harmful_hits": harmful_hits,
            "status": status,
            "ocr_method": ocr_method,
        }
    except Exception as e:
        print(f"Screen OCR analysis error: {e}")
        import traceback
        traceback.print_exc()
        return {"text": "", "harmful_hits": [], "status": "error", "error": str(e)}
