from dataclasses import dataclass
from typing import Dict

import librosa
import numpy as np
from sklearn.preprocessing import StandardScaler

from app.utils.microphone import DEFAULT_SR


scaler = StandardScaler()


@dataclass
class SpeechEmotionResult:
    emotion: str
    energy: float
    pitch: float
    tempo: float

    def to_dict(self):
        return {
            "emotion": self.emotion,
            "energy": self.energy,
            "pitch": self.pitch,
            "tempo": self.tempo,
        }


def _extract_features(signal: np.ndarray, sr: int = DEFAULT_SR):
    if not len(signal):
        return 0.0, 0.0, 0.0

    energy = float(np.mean(signal**2))
    pitches, magnitudes = librosa.piptrack(y=signal, sr=sr)
    pitch = float(np.max(pitches[magnitudes > np.median(magnitudes)])) if np.any(magnitudes) else 0.0
    onset_env = librosa.onset.onset_strength(y=signal, sr=sr)
    # Use new librosa API to avoid deprecation warning
    try:
        from librosa.feature import rhythm
        tempo = float(rhythm.tempo(onset_envelope=onset_env, sr=sr)[0]) if onset_env.any() else 0.0
    except (ImportError, AttributeError):
        # Fallback to old API if new one not available
        tempo = float(librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]) if onset_env.any() else 0.0
    return energy, pitch, tempo


def analyze_speech_emotion(signal: np.ndarray, sr: int = DEFAULT_SR) -> Dict:
    energy, pitch, tempo = _extract_features(signal, sr)
    features = np.array([[energy, pitch, tempo]])
    scaled = scaler.fit_transform(features)[0]

    emotion = "calm"
    if scaled[0] > 0.5 or scaled[2] > 0.5:
        emotion = "excited"
    if scaled[0] < -0.2 and scaled[1] < -0.2:
        emotion = "sad"
    if scaled[2] > 1.2:
        emotion = "anxious"

    return SpeechEmotionResult(emotion=emotion, energy=energy, pitch=pitch, tempo=tempo).to_dict()
