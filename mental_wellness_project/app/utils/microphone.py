import base64
import io
import logging
import wave
from typing import Tuple

import numpy as np
import soundfile as sf

logger = logging.getLogger(__name__)

DEFAULT_SR = 16000


def _to_mono(data: np.ndarray) -> np.ndarray:
    if data.ndim > 1:
        return np.mean(data, axis=1)
    return data


def _resample_if_needed(signal: np.ndarray, sr: int, target_sr: int) -> Tuple[np.ndarray, int]:
    if sr == target_sr or not signal.size:
        return signal, sr

    import librosa

    resampled = librosa.resample(signal, orig_sr=sr, target_sr=target_sr)
    return resampled, target_sr


def _decode_with_wave(audio_bytes: bytes) -> Tuple[np.ndarray, int]:
    """Decode WAV using Python's built-in wave module (no external dependencies)."""
    wav_file = wave.open(io.BytesIO(audio_bytes), 'rb')
    num_channels = wav_file.getnchannels()
    sample_width = wav_file.getsampwidth()
    sample_rate = wav_file.getframerate()
    frames = wav_file.readframes(-1)
    wav_file.close()
    
    # Convert bytes to numpy array based on sample width
    if sample_width == 1:
        dtype = np.uint8
        sound_info = np.frombuffer(frames, dtype=dtype).astype(np.float32) / 128.0 - 1.0
    elif sample_width == 2:
        dtype = np.int16
        sound_info = np.frombuffer(frames, dtype=dtype).astype(np.float32) / 32768.0
    elif sample_width == 4:
        dtype = np.int32
        sound_info = np.frombuffer(frames, dtype=dtype).astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")
    
    # Handle stereo to mono conversion
    if num_channels > 1:
        # Reshape and convert to mono
        sound_info = sound_info.reshape(-1, num_channels)
        sound_info = _to_mono(sound_info)
    
    return sound_info, sample_rate


def _decode_with_soundfile(audio_bytes: bytes) -> Tuple[np.ndarray, int]:
    """Decode audio using soundfile (handles WAV and other formats, no FFmpeg needed for WAV)."""
    data, sr = sf.read(io.BytesIO(audio_bytes))
    return _to_mono(data), sr


def decode_base64_audio(audio_b64: str, target_sr: int = DEFAULT_SR) -> Tuple[np.ndarray, int]:
    """
    Decode base64-encoded WAV audio (converted from WebM/OGG in browser).
    Uses cloud-friendly libraries that don't require FFmpeg.
    Returns a mono numpy array. If decoding fails, returns empty signal.
    """

    if not audio_b64:
        return np.array([]), target_sr

    if "," in audio_b64:
        audio_b64 = audio_b64.split(",")[1]

    try:
        audio_bytes = base64.b64decode(audio_b64)
    except Exception as e:
        logger.error(f"Failed to decode base64 audio: {e}")
        return np.array([]), target_sr

    # Try decoders in order: soundfile (most reliable), then wave (built-in)
    # Both work with WAV files and don't need FFmpeg
    decoders = [
        _decode_with_soundfile,  # Best for WAV files, handles various formats
        _decode_with_wave,  # Built-in Python module, no dependencies
    ]
    
    for decoder in decoders:
        try:
            data, sr = decoder(audio_bytes)
            if data.size > 0:  # Only return if we got actual data
                data, sr = _resample_if_needed(data, sr, target_sr)
                logger.debug("Audio decoded successfully via %s: %d samples at %d Hz", decoder.__name__, len(data), sr)
                return data, sr
        except Exception as exc:
            logger.warning("Audio decode failed via %s: %s", decoder.__name__, str(exc)[:100])
            continue

    logger.error("All audio decoders failed. Make sure frontend converts audio to WAV format before sending.")
    return np.array([]), target_sr
