from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ModuleSnapshot:
    text: Optional[Dict] = None
    speech: Optional[Dict] = None
    face: Optional[Dict] = None
    screen: Optional[Dict] = None


def synthesize(snapshot: ModuleSnapshot) -> Dict:
    """
    Optimized and more accurate wellness score synthesis.
    Uses weighted averaging and better validation for accurate predictions.
    """
    # Start with neutral baseline (50 = neutral, not 65)
    base_score = 50.0
    weighted_scores = []
    weights = []
    status_notes: List[str] = []
    severity_points = 0
    data_quality = 0  # Track how much valid data we have

    # Text analysis (weight: 30%)
    if snapshot.text and snapshot.text.get("label") and snapshot.text.get("label") != "UNKNOWN":
        text_label = snapshot.text.get("label", "").upper()
        text_score = float(snapshot.text.get("score", 0.5))
        
        # More accurate scoring: positive = higher, negative = lower
        if text_label == "POSITIVE":
            text_wellness = 50 + (text_score * 30)  # 50-80 range
        else:  # NEGATIVE
            text_wellness = 50 - (text_score * 30)  # 20-50 range
        
        weighted_scores.append(text_wellness)
        weights.append(0.30)
        data_quality += 1
        
        # Add insights only if meaningful
        insights = snapshot.text.get("insights", [])
        if insights:
            status_notes.extend(insights[:2])  # Limit to 2 insights
        
        # Check for harmful content
        if snapshot.text.get("harmful_hits"):
            severity_points += 2
            status_notes.append("⚠️ Harmful content detected in text.")
        
        # Mood-based severity
        mood = snapshot.text.get("mood", "")
        if mood in {"sad", "stressed"}:
            severity_points += 1

    # Speech analysis (weight: 25%)
    if snapshot.speech and snapshot.speech.get("emotion"):
        emotion = snapshot.speech.get("emotion", "unknown")
        
        # Process speech if it's not "unknown" or "waiting"
        if emotion not in {"unknown", "waiting", None}:
            data_quality += 1
            
            # More nuanced emotion scoring
            emotion_scores = {
                "calm": 65,
                "excited": 70,
                "sad": 35,  # Balanced for accurate detection
                "anxious": 30,  # Balanced
                "unknown": 50,
                "waiting": 50,
            }
            speech_wellness = emotion_scores.get(emotion, 50)
            
            weighted_scores.append(speech_wellness)
            weights.append(0.25)
            
            # Add severity if emotion is negative
            if emotion in {"sad", "anxious"}:
                severity_points += 1
                status_notes.append(f"Voice tone indicates {emotion}.")
            elif emotion == "excited":
                status_notes.append("Voice tone appears positive.")

    # Face analysis (weight: 25%)
    if snapshot.face and snapshot.face.get("dominant_emotion") and snapshot.face.get("dominant_emotion") != "unknown":
        confidence = float(snapshot.face.get("confidence", 0))
        dominant = snapshot.face.get("dominant_emotion", "neutral")
        
        # Only use if confidence is reasonable (lowered threshold to 0.2 for better detection)
        if confidence > 0.2:
            data_quality += 1
            
            # Emotion-based scoring
            face_scores = {
                "happy": 70,
                "neutral": 55,
                "sad": 35,  # Balanced score for sad
                "angry": 25,
                "fear": 30,
                "surprise": 60,
                "disgust": 40,
            }
            face_wellness = face_scores.get(dominant, 50)
            
            # Weight by confidence - more confident = more impact
            face_wellness = 50 + (face_wellness - 50) * min(confidence, 1.0)
            
            weighted_scores.append(face_wellness)
            weights.append(0.25)
            
            # Severity points based on emotion and confidence
            if dominant == "sad":
                if confidence > 0.5:
                    # Confident sad expression
                    severity_points += 2
                    status_notes.append(f"⚠️ Sad facial expression detected (confidence: {confidence:.1%}).")
                else:
                    # Less confident sad
                    severity_points += 1
                    status_notes.append(f"Facial expression appears sad (confidence: {confidence:.1%}).")
            elif dominant in {"angry", "fear"}:
                if confidence > 0.5:
                    severity_points += 2
                    status_notes.append(f"⚠️ {dominant.capitalize()} facial expression detected.")
                else:
                    severity_points += 1
            elif confidence > 0.5:  # Note confident detections
                if dominant not in {"neutral", "unknown"}:
                    status_notes.append(f"Facial expression: {dominant}.")

    # Screen analysis (weight: 20%, counts as data quality)
    if snapshot.screen:
        screen_status = snapshot.screen.get("status", "")
        hits = snapshot.screen.get("harmful_hits", [])
        screen_text = snapshot.screen.get("text", "")
        
        # Count screen as data quality if it has been processed (not just throttled/initializing)
        if screen_status in {"ok", "error", "timeout"}:
            data_quality += 1
        
        if hits:
            # Harmful content detected
            weighted_scores.append(30)  # Low score for harmful content
            weights.append(0.20)
            severity_points += 2
            status_notes.append("⚠️ Potentially harmful content on screen.")
        elif screen_status == "ok":
            # Screen is fine, neutral contribution
            weighted_scores.append(50)
            weights.append(0.10)  # Lower weight if no issues
            # Note if text was found (for debugging)
            if screen_text and len(screen_text) > 10:
                status_notes.append("Screen content analyzed.")

    # Calculate weighted average score
    if weighted_scores and weights:
        # Normalize weights to sum to 1.0
        total_weight = sum(weights)
        if total_weight > 0:
            normalized_weights = [w / total_weight for w in weights]
            score = sum(ws * nw for ws, nw in zip(weighted_scores, normalized_weights))
            
            # If we have very limited data, slightly adjust toward neutral
            # But don't over-adjust - still respect the data we have
            if data_quality == 1:
                # Only one data source - slight adjustment (10% toward neutral)
                score = 50 + (score - 50) * 0.9
            elif data_quality == 2:
                # Two data sources - minimal adjustment (5% toward neutral)
                score = 50 + (score - 50) * 0.95
            # If 3+ data sources, use score as-is (full confidence)
        else:
            score = base_score
    else:
        # No valid data, return neutral (not low score)
        score = base_score
        status_notes.append("Insufficient data for accurate assessment.")
        # Don't add severity points if no data
        severity_points = 0

    # Clamp score to valid range
    score = max(0.0, min(100.0, round(score, 1)))

    # Balanced risk level calculation
    # Triggers high risk when there's genuine concern, but not too sensitive
    # Works properly with all data types (speech, screen, face, text)
    
    # Use balanced thresholds that work with any data combination
    # More accurate thresholds based on data quality
    if data_quality == 0:
        # No data - default to low risk
        risk_level = "low"
    elif severity_points >= 4 or score < 20:
        risk_level = "critical"
    elif severity_points >= 3 or (severity_points >= 2 and score < 40) or score < 30:
        # High risk: 3+ severity points OR (2 severity + low score) OR very low score
        risk_level = "high"
    elif severity_points >= 2 or (severity_points >= 1 and score < 50) or score < 45:
        # Medium risk: 2+ severity points OR (1 severity + moderate score) OR moderate-low score
        risk_level = "medium"
    else:
        risk_level = "low"

    # Overall state based on score and risk
    # More balanced - don't overreact to single indicators
    if risk_level == "critical" or score < 25:
        overall = "high_anxiety"
    elif risk_level == "high" or (score < 40 and severity_points >= 2):
        # High risk only if both low score AND multiple indicators
        overall = "moderate_stress"
    elif risk_level == "medium" or score < 55:
        overall = "steady"
    elif score < 75:
        overall = "steady"
    else:
        overall = "calm"

    # Limit notes to prevent overload (max 4)
    status_notes = status_notes[:4]

    result = {
        "score": score,
        "overall_state": overall,
        "risk_level": risk_level,
        "notes": status_notes,
        "actions": _recommended_actions(overall, risk_level),
    }
    
    # Debug: Log final result
    # print(f"Synthesize result: score={score}, risk={risk_level}, state={overall}, data_quality={data_quality}")
    
    return result


def _recommended_actions(overall_state: str, risk_level: str = "low") -> List[str]:
    """
    Return recommended actions based on state and risk level.
    Optimized to return 2-3 most relevant actions.
    """
    # High risk actions (priority)
    if risk_level in {"critical", "high"}:
        return [
            "Take a moment to breathe deeply - 4 seconds in, 4 seconds out.",
            "Step away from the screen and do a quick physical stretch.",
            "Consider reaching out to a trusted friend or support resource.",
        ]
    
    # State-based actions
    mapping = {
        "high_anxiety": [
            "Try the 4-7-8 breathing technique: breathe in 4, hold 7, out 8.",
            "Take a short walk or move your body for 2-3 minutes.",
            "Focus on 5 things you can see, 4 you can touch, 3 you can hear.",
        ],
        "moderate_stress": [
            "Take a 2-minute break: stretch, hydrate, or step outside.",
            "Write down 3 things you're grateful for right now.",
            "Switch to a lighter task or listen to calming music.",
        ],
        "steady": [
            "Keep doing what works—acknowledge your current state.",
            "Take a moment to appreciate your self-awareness.",
        ],
        "calm": [
            "Acknowledge this moment of calm.",
            "Note what helped you feel this way today.",
        ],
    }
    
    actions = mapping.get(overall_state, ["Take 3 deep breaths and check in with yourself."])
    
    # Limit to 2-3 actions to prevent overload
    return actions[:3]

