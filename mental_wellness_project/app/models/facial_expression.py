import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.request import urlretrieve

import cv2
import numpy as np
from fer import FER

from app.utils.camera import decode_base64_image

# Get base directory (project root)
BASE_DIR = Path(__file__).resolve().parents[2]
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

# OpenCV DNN Face Detector model files
DNN_PROTO = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
DNN_MODEL = "https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
DNN_PROTO_PATH = MODELS_DIR / "deploy.prototxt"
DNN_MODEL_PATH = MODELS_DIR / "res10_300x300_ssd_iter_140000.caffemodel"


@lru_cache(maxsize=1)
def _fer_detector():
    # Use mtcnn=False for faster processing, mtcnn=True is more accurate but slower
    # For real-time monitoring, speed is more important
    return FER(mtcnn=False)


@lru_cache(maxsize=1)
def _opencv_dnn_face_detector():
    """Initialize OpenCV DNN face detector with downloaded models."""
    # Download model files if they don't exist
    if not DNN_PROTO_PATH.exists():
        try:
            print(f"Downloading OpenCV DNN face detector prototxt...")
            urlretrieve(DNN_PROTO, str(DNN_PROTO_PATH))
            print(f"Downloaded to {DNN_PROTO_PATH}")
        except Exception as e:
            print(f"Warning: Could not download DNN prototxt: {e}")
            return None
    
    if not DNN_MODEL_PATH.exists():
        try:
            print(f"Downloading OpenCV DNN face detector model (this may take a minute)...")
            urlretrieve(DNN_MODEL, str(DNN_MODEL_PATH))
            print(f"Downloaded to {DNN_MODEL_PATH}")
        except Exception as e:
            print(f"Warning: Could not download DNN model: {e}")
            return None
    
    try:
        net = cv2.dnn.readNetFromCaffe(str(DNN_PROTO_PATH), str(DNN_MODEL_PATH))
        return net
    except Exception as e:
        print(f"Warning: Could not load OpenCV DNN face detector: {e}")
        return None


def _preprocess_image(frame: np.ndarray) -> Optional[np.ndarray]:
    """Apply OpenCV preprocessing to improve face detection accuracy."""
    try:
        # Validate input
        if frame is None or frame.size == 0:
            return None
        if len(frame.shape) != 3 or frame.shape[2] != 3:
            return None
        
        # Simplified preprocessing for better speed and accuracy
        # Too much processing can actually reduce accuracy
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) for better contrast
        # This helps with varying lighting conditions
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        # Light denoising - too much blur reduces emotion detection accuracy
        filtered = cv2.bilateralFilter(enhanced_bgr, 5, 50, 50)
        
        return filtered
    except Exception as e:
        print(f"Image preprocessing error: {e}")
        return None


def _detect_face_opencv_dnn(frame: np.ndarray, net) -> Optional[Tuple[int, int, int, int]]:
    """Detect face using OpenCV DNN face detector. Returns (x, y, w, h) or None."""
    if net is None:
        return None
    
    try:
        h, w = frame.shape[:2]
        if h < 48 or w < 48:
            return None
        
        # Resize frame to 300x300 for DNN (required input size)
        # Use INTER_AREA for downscaling to maintain quality
        resized = cv2.resize(frame, (300, 300), interpolation=cv2.INTER_AREA)
        
        # Create blob from image for DNN
        # Mean subtraction: [104, 117, 123] for BGR channels
        blob = cv2.dnn.blobFromImage(
            resized,
            1.0,  # Scale factor
            (300, 300),  # Spatial size
            [104, 117, 123],  # Mean subtraction values for BGR
            swapRB=False,  # Keep BGR format
            crop=False
        )
        
        net.setInput(blob)
        detections = net.forward()
        
        # Find the best face detection (highest confidence)
        best_confidence = 0.6  # Increased threshold for better accuracy
        best_box = None
        
        for i in range(detections.shape[2]):
            confidence = float(detections[0, 0, i, 2])
            
            if confidence > best_confidence:
                best_confidence = confidence
                
                # Get bounding box coordinates (normalized 0-1)
                box = detections[0, 0, i, 3:7]
                x1_norm, y1_norm, x2_norm, y2_norm = box
                
                # Convert to pixel coordinates
                x1 = int(x1_norm * w)
                y1 = int(y1_norm * h)
                x2 = int(x2_norm * w)
                y2 = int(y2_norm * h)
                
                # Ensure coordinates are within image bounds
                x1 = max(0, min(x1, w - 1))
                y1 = max(0, min(y1, h - 1))
                x2 = max(x1 + 1, min(x2, w))
                y2 = max(y1 + 1, min(y2, h))
                
                # Validate box dimensions
                box_w = x2 - x1
                box_h = y2 - y1
                if box_w >= 48 and box_h >= 48:  # Minimum face size
                    best_box = (x1, y1, box_w, box_h)
        
        return best_box
    except Exception as e:
        print(f"OpenCV DNN face detection error: {e}")
        return None


def _extract_face_region(frame: np.ndarray, face_box: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
    """Extract and normalize face region from frame."""
    x, y, w, h = face_box
    
    # Validate face box dimensions
    if w <= 0 or h <= 0:
        return None
    
    # Add padding around face
    padding = 20
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(frame.shape[1] - x, w + 2 * padding)
    h = min(frame.shape[0] - y, h + 2 * padding)
    
    # Validate again after padding
    if w <= 0 or h <= 0 or x >= frame.shape[1] or y >= frame.shape[0]:
        return None
    
    face_roi = frame[y:y+h, x:x+w]
    
    # Validate extracted region
    if face_roi.size == 0:
        return None
    
    # Ensure RGB format (FER expects RGB, OpenCV uses BGR)
    if len(face_roi.shape) == 2:
        # Grayscale - convert to RGB
        face_roi = cv2.cvtColor(face_roi, cv2.COLOR_GRAY2RGB)
    elif len(face_roi.shape) == 3 and face_roi.shape[2] == 3:
        # BGR to RGB conversion
        face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
    elif len(face_roi.shape) == 3 and face_roi.shape[2] == 4:
        # RGBA to RGB
        face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGRA2RGB)
    
    # Resize to a standard size for better emotion detection
    # Ensure minimum size for FER (needs at least 48x48)
    try:
        h, w = face_roi.shape[:2]
        if w < 48 or h < 48:
            # Too small, resize up
            scale = 48 / min(w, h)
            new_w = max(48, int(w * scale))
            new_h = max(48, int(h * scale))
            face_roi = cv2.resize(face_roi, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        elif w > 640 or h > 640:
            # Too large, resize down
            scale = 640 / max(w, h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            face_roi = cv2.resize(face_roi, (new_w, new_h), interpolation=cv2.INTER_AREA)
        else:
            # Good size, resize to standard 224x224 for consistency
            face_roi = cv2.resize(face_roi, (224, 224), interpolation=cv2.INTER_AREA)
    except Exception as e:
        print(f"Face region resize error: {e}")
        return None
    
    # Final validation - ensure it's RGB (3 channels)
    if len(face_roi.shape) != 3 or face_roi.shape[2] != 3:
        return None
    
    return face_roi


def analyze_facial_expression(image_b64: str) -> Dict:
    try:
        if not image_b64:
            return {"emotion": "unknown", "confidence": 0.0, "dominant_emotion": "unknown", "note": "no_frame"}
        
        frame = decode_base64_image(image_b64)
        if frame is None:
            return {"emotion": "unknown", "confidence": 0.0, "dominant_emotion": "unknown", "note": "decode_failed"}

        # Resize frame if too large for better performance
        height, width = frame.shape[:2]
        
        # Validate initial frame dimensions
        if width < 48 or height < 48:
            return {"emotion": "unknown", "confidence": 0.0, "dominant_emotion": "unknown", "note": "frame_too_small"}
        if width > 2000 or height > 2000:
            return {"emotion": "unknown", "confidence": 0.0, "dominant_emotion": "unknown", "note": "frame_too_large"}
        
        # Resize if too large (but keep reasonable size for accuracy)
        if width > 640 or height > 480:
            scale = min(640 / width, 480 / height)
            new_width = max(96, int(width * scale))  # Ensure minimum 96px
            new_height = max(96, int(height * scale))
            try:
                frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            except Exception as e:
                print(f"Frame resize error: {e}")
                return {"emotion": "unknown", "confidence": 0.0, "dominant_emotion": "unknown", "note": "resize_failed"}

        # Apply OpenCV preprocessing for better accuracy
        preprocessed_frame = _preprocess_image(frame)
        
        # If preprocessing failed, use original frame
        if preprocessed_frame is None:
            preprocessed_frame = frame
        
        # Try OpenCV DNN face detector first (more accurate)
        dnn_net = _opencv_dnn_face_detector()
        face_box = None
        detection_frame = None
        
        if preprocessed_frame is not None:
            if dnn_net is not None:
                try:
                    face_box = _detect_face_opencv_dnn(preprocessed_frame, dnn_net)
                    
                    # Use the face region if detected
                    if face_box:
                        face_roi = _extract_face_region(preprocessed_frame, face_box)
                        if face_roi is not None:
                            detection_frame = face_roi
                            print(f"Face detected using OpenCV DNN: {face_box}")
                except Exception as e:
                    print(f"OpenCV DNN face detection error: {e}, falling back to full frame")
                    face_box = None
            
            # Fallback to preprocessed frame if face extraction failed
            # FER can work on full frame too, so this is fine
            if detection_frame is None:
                detection_frame = preprocessed_frame
                if face_box is None:
                    print("Using full frame for emotion detection (face detection not available or failed)")

        # Validate frame before processing
        def validate_frame(img):
            """Validate frame dimensions and format before FER processing"""
            if img is None:
                return False
            h, w = img.shape[:2]
            # FER requires minimum dimensions
            if w < 48 or h < 48:
                return False
            if w > 2000 or h > 2000:
                return False
            # Ensure it's a valid numpy array
            if not isinstance(img, np.ndarray):
                return False
            # Ensure it has 3 channels (BGR/RGB)
            if len(img.shape) != 3 or img.shape[2] != 3:
                return False
            return True
        
        # Normalize frame to standard size for FER (FER works best with 48-640px)
        def normalize_frame(img):
            """Normalize frame to safe dimensions for FER"""
            try:
                h, w = img.shape[:2]
                # Resize if too small or too large
                if w < 96 or h < 96:
                    # Too small, resize up
                    scale = 96 / min(w, h)
                    new_w = max(96, int(w * scale))
                    new_h = max(96, int(h * scale))
                    img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
                elif w > 640 or h > 480:
                    # Too large, resize down
                    scale = min(640 / w, 480 / h)
                    new_w = max(96, int(w * scale))
                    new_h = max(96, int(h * scale))
                    img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
                return img
            except Exception as e:
                print(f"Frame normalization error: {e}")
                return img  # Return original if normalization fails
        
        # Use FER for emotion detection - use faster MTCNN=False for better performance
        detector = _fer_detector()
        
        # Ensure frame is in correct format for FER (RGB, uint8, 3 channels)
        def prepare_frame_for_fer(img):
            """Prepare frame for FER model - ensure correct format"""
            try:
                if img is None:
                    return None
                
                # Ensure it's a numpy array
                if not isinstance(img, np.ndarray):
                    return None
                
                # Check dimensions and convert to RGB
                if len(img.shape) == 2:
                    # Grayscale - convert to RGB
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
                elif len(img.shape) == 3:
                    # Check channels
                    if img.shape[2] == 3:
                        # Check if it's already RGB or BGR
                        # OpenCV uses BGR, FER expects RGB
                        # Convert BGR to RGB (safe to do even if already RGB)
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    elif img.shape[2] == 4:
                        # RGBA - convert to RGB
                        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                
                # Ensure uint8 format
                if img.dtype != np.uint8:
                    img = (img * 255).astype(np.uint8) if img.max() <= 1.0 else img.astype(np.uint8)
                
                # Ensure minimum size (FER needs at least 48x48)
                h, w = img.shape[:2]
                if w < 48 or h < 48:
                    scale = 48 / min(w, h)
                    new_w = max(48, int(w * scale))
                    new_h = max(48, int(h * scale))
                    img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
                
                return img
            except Exception as e:
                print(f"Frame preparation error: {e}")
                return None
        
        # Try detection on the best frame we have
        results = None
        if validate_frame(detection_frame):
            try:
                normalized_frame = normalize_frame(detection_frame.copy())
                fer_frame = prepare_frame_for_fer(normalized_frame)
                if fer_frame is not None:
                    # Validate frame format before passing to FER
                    if len(fer_frame.shape) == 3 and fer_frame.shape[2] == 3:
                        # Suppress tensor warnings from FER library
                        import warnings
                        with warnings.catch_warnings():
                            warnings.filterwarnings("ignore", category=UserWarning)
                            results = detector.detect_emotions(fer_frame)
                    else:
                        print(f"Invalid frame format for FER: shape={fer_frame.shape}")
            except Exception as e:
                # Suppress tensor shape warnings - they're handled by format conversion
                error_msg = str(e).lower()
                if "input_1" not in error_msg and "tensor" not in error_msg:
                    print(f"FER detection error on processed frame: {e}")
                results = None
        
        # Fallback to original frame if detection failed
        if not results or len(results) == 0:
            if validate_frame(frame):
                try:
                    normalized_frame = normalize_frame(frame.copy())
                    fer_frame = prepare_frame_for_fer(normalized_frame)
                    if fer_frame is not None:
                        # Validate frame format before passing to FER
                        if len(fer_frame.shape) == 3 and fer_frame.shape[2] == 3:
                            # Suppress tensor warnings from FER library
                            import warnings
                            with warnings.catch_warnings():
                                warnings.filterwarnings("ignore", category=UserWarning)
                                results = detector.detect_emotions(fer_frame)
                        else:
                            print(f"Invalid frame format for FER: shape={fer_frame.shape}")
                except Exception as e:
                    # Suppress tensor shape warnings - they're handled by format conversion
                    error_msg = str(e).lower()
                    if "input_1" not in error_msg and "tensor" not in error_msg:
                        print(f"FER detection error on original frame: {e}")
                    results = None
        
        if not results or len(results) == 0:
            return {"emotion": "unknown", "confidence": 0.0, "dominant_emotion": "unknown", "note": "no_face_detected"}

        # Get the first detected face (usually the most prominent)
        face_emotions = results[0].get("emotions", {})
        if not face_emotions:
            return {"emotion": "unknown", "confidence": 0.0, "dominant_emotion": "unknown", "note": "no_emotions"}

        top = max(face_emotions.items(), key=lambda item: item[1])
        dominant_emotion, confidence = top

        # Only return if confidence is above threshold (lowered from 0.1 to 0.05 for better detection)
        if confidence < 0.05:
            return {"emotion": "unknown", "confidence": float(confidence), "dominant_emotion": "unknown", "note": "low_confidence"}
        
        # Improve emotion accuracy by checking if confidence is reasonable
        # If the top emotion has very low confidence, try to get a better reading
        if confidence < 0.3:
            # Get top 2 emotions to see if there's a close second
            sorted_emotions = sorted(face_emotions.items(), key=lambda item: item[1], reverse=True)
            if len(sorted_emotions) > 1:
                second_emotion, second_conf = sorted_emotions[1]
                # If second emotion is close, the detection might be uncertain
                if abs(confidence - second_conf) < 0.1:
                    # Use the more neutral/common emotion if confidence is close
                    if "neutral" in face_emotions:
                        dominant_emotion = "neutral"
                        confidence = face_emotions["neutral"]
                    elif "happy" in face_emotions and face_emotions["happy"] > 0.2:
                        dominant_emotion = "happy"
                        confidence = face_emotions["happy"]

        return {
            "emotion": dominant_emotion,
            "confidence": float(confidence),
            "dominant_emotion": dominant_emotion,
            "note": "detected"
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Facial expression analysis error: {error_trace}")
        return {"emotion": "unknown", "confidence": 0.0, "dominant_emotion": "unknown", "error": str(e)}
