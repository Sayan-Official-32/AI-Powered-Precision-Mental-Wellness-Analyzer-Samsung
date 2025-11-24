from functools import lru_cache
from typing import Dict

from transformers import pipeline

from app.config import settings


@lru_cache(maxsize=1)
def _sentiment_model():
    return pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
    )


def analyze_text_sentiment(text: str) -> Dict:
    if not text.strip():
        return {
            "label": "NEUTRAL",
            "score": 0.0,
            "mood": "neutral",
            "insights": ["Share a bit more so I can understand how you feel."],
        }

    result = _sentiment_model()(text[:512])[0]
    label = result["label"]
    score = float(result["score"])

    if label.lower() == "positive":
        mood = "calm" if score > 0.8 else "positive"
    else:
        mood = "stressed" if score > 0.8 else "sad"

    harmful_hits = [
        keyword for keyword in settings.harmful_keywords if keyword.lower() in text.lower()
    ]

    return {
        "label": label,
        "score": score,
        "mood": mood,
        "harmful_hits": harmful_hits,
        "insights": _text_insights(text, mood, harmful_hits),
    }


def _text_insights(text: str, mood: str, harmful_hits):
    insights = []
    if harmful_hits:
        insights.append(
            "Your text mentions potentially harmful themes. Consider contacting a trusted person."
        )
    if mood in {"sad", "stressed"}:
        insights.append("Try reframing negative thoughts and take a short break.")
    if not insights:
        insights.append("Keep reflecting on your feelings—you are doing great.")
    return insights
