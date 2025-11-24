from typing import Optional

from flask import Blueprint, jsonify, request
from openai import OpenAI, OpenAIError

from app.config import settings
from app.database import log_alert, log_interaction
from app.models.behavior_synthesis import ModuleSnapshot, synthesize
from app.models.facial_expression import analyze_facial_expression
from app.models.screen_ocr import analyze_screen_content
from app.models.speech_emotion import analyze_speech_emotion
from app.models.text_sentiment import analyze_text_sentiment
from app.utils.microphone import decode_base64_audio
import time

main = Blueprint("main", __name__, url_prefix="/api/v1")

# Screen OCR throttling - only process every 20 seconds to prevent system overload (reduced from 30 for better responsiveness)
_last_screen_ocr_time = 0
_SCREEN_OCR_INTERVAL = 10  # seconds between screen OCR processing (optimized for faster updates)


def _openai_client() -> Optional[OpenAI]:
    """Initialize OpenAI client if API key is available."""
    api_key = settings.openai_api_key
    if not api_key or api_key == "replace_with_openai_api_key" or api_key.strip() == "":
        print("⚠️ OpenAI API key not configured. Wellness Companion will not work.")
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        print(f"⚠️ Error initializing OpenAI client: {e}")
        return None


@main.route("/text", methods=["POST"])
def text_analysis():
    payload = request.get_json(force=True)
    text = payload.get("text", "")
    result = analyze_text_sentiment(text)
    log_interaction("text", {"text": text, "result": result})
    return jsonify(result)


@main.route("/audio", methods=["POST"])
def audio_analysis():
    payload = request.get_json(force=True)
    audio_b64 = payload.get("audio")
    if not audio_b64:
        return jsonify({"error": "audio field required"}), 400
    signal, sr = decode_base64_audio(audio_b64)
    if signal.size == 0:
        return jsonify({"warning": "Unable to decode audio blob; try using a different browser."}), 400
    result = analyze_speech_emotion(signal, sr)
    log_interaction("audio", {"result": result})
    return jsonify(result)


@main.route("/vision", methods=["POST"])
def vision_analysis():
    payload = request.get_json(force=True)
    frame = payload.get("frame")
    if not frame:
        return jsonify({"error": "frame field required"}), 400
    result = analyze_facial_expression(frame)
    log_interaction("vision", {"result": result})
    return jsonify(result)


@main.route("/screen", methods=["POST"])
def screen_analysis():
    payload = request.get_json(force=True)
    frame = payload.get("frame")
    if not frame:
        return jsonify({"error": "frame field required"}), 400
    result = analyze_screen_content(frame)
    log_interaction("screen", {"result": result})
    if result.get("harmful_hits"):
        log_alert("high", "Harmful screen content", {"hits": result["harmful_hits"]})
    return jsonify(result)


@main.route("/monitor", methods=["POST"])
def monitor():
    try:
        payload = request.get_json(force=True) or {}

        text_result = None
        if payload.get("text"):
            try:
                text_result = analyze_text_sentiment(payload["text"])
                print(f"Text analysis successful: {text_result.get('label', 'unknown')}")
            except Exception as e:
                print(f"Text analysis error: {e}")
                text_result = {"error": str(e), "label": "UNKNOWN", "score": 0.5}
        # Text will be extracted from screen OCR if screen analysis succeeds (handled below)

        # Process speech, face, and screen in parallel for faster response
        import threading
        
        speech_result = None
        face_result = None
        
        # Speech analysis (parallel)
        speech_container = {"result": None, "done": False}
        def process_speech():
            try:
                if payload.get("audio"):
                    signal, sr = decode_base64_audio(payload["audio"])
                    if signal.size > 0:
                        result = analyze_speech_emotion(signal, sr)
                        print(f"Speech analysis successful: {result.get('emotion', 'unknown')}")
                        speech_container["result"] = result
                    else:
                        speech_container["result"] = {"emotion": "unknown", "note": "audio decode failed - no audio data"}
                        print("Speech analysis skipped: empty audio signal")
                else:
                    speech_container["result"] = {"emotion": "waiting", "note": "No audio data received yet"}
            except Exception as e:
                print(f"Speech analysis error: {e}")
                speech_container["result"] = {"emotion": "unknown", "note": f"error: {str(e)[:100]}"}
            finally:
                speech_container["done"] = True
        
        # Face analysis (parallel)
        face_container = {"result": None, "done": False}
        def process_face():
            try:
                if payload.get("frame"):
                    result = analyze_facial_expression(payload["frame"])
                    face_container["result"] = result
                else:
                    face_container["result"] = None
            except Exception as e:
                print(f"Face analysis error: {e}")
                face_container["result"] = {"emotion": "unknown", "confidence": 0.0, "dominant_emotion": "unknown", "error": str(e)}
            finally:
                face_container["done"] = True
        
        # Start speech and face processing in parallel
        threads = []
        if payload.get("audio"):
            t_speech = threading.Thread(target=process_speech, daemon=True)
            t_speech.start()
            threads.append(("speech", t_speech))
        
        if payload.get("frame"):
            t_face = threading.Thread(target=process_face, daemon=True)
            t_face.start()
            threads.append(("face", t_face))
        
        # Wait for speech and face (max 2.5 seconds each for faster response)
        for name, thread in threads:
            thread.join(timeout=2.5)
            if thread.is_alive():
                print(f"⚠️ {name.capitalize()} analysis taking longer than expected, continuing with available data...")
        
        speech_result = speech_container["result"] or {"emotion": "waiting", "note": "No audio data received yet"}
        face_result = face_container["result"]

        screen_result = None
        if payload.get("screen"):
            try:
                # Throttle screen OCR to prevent system overload - only process every 15 seconds (optimized)
                global _last_screen_ocr_time, _SCREEN_OCR_INTERVAL
                current_time = time.time()
                time_since_last_ocr = current_time - _last_screen_ocr_time
                
                # Reduced interval to 10 seconds for better responsiveness
                if time_since_last_ocr < _SCREEN_OCR_INTERVAL:
                    # Don't return cached - process anyway but with shorter timeout for faster response
                    # This ensures screen updates more frequently
                    remaining = int(_SCREEN_OCR_INTERVAL - time_since_last_ocr)
                    # Process with shorter timeout if within throttled period
                    import threading
                    screen_result_container = {"result": None, "done": False, "error": None}
                    
                    def run_screen_ocr_quick():
                        try:
                            result = analyze_screen_content(payload["screen"])
                            screen_result_container["result"] = result
                        except Exception as e:
                            print(f"Screen analysis error: {e}")
                            screen_result_container["error"] = str(e)
                            screen_result_container["result"] = {"text": "", "harmful_hits": [], "status": "error", "error": str(e)[:200]}
                        finally:
                            screen_result_container["done"] = True
                    
                    ocr_thread = threading.Thread(target=run_screen_ocr_quick, daemon=True)
                    ocr_thread.start()
                    ocr_thread.join(timeout=5.0)  # Shorter timeout if throttled
                    
                    if not screen_result_container["done"]:
                        screen_result = {
                            "text": "",
                            "harmful_hits": [],
                            "status": "throttled",
                            "note": f"Screen analysis updating every {_SCREEN_OCR_INTERVAL}s. Next update in {remaining}s."
                        }
                    else:
                        screen_result = screen_result_container["result"] or {"text": "", "harmful_hits": [], "status": "ok", "note": "No text detected on screen"}
                else:
                    # Check if EasyOCR is initializing first - if so, return immediately without processing
                    from app.models.screen_ocr import is_easyocr_initializing
                    
                    if is_easyocr_initializing():
                        # EasyOCR is still initializing (downloading models), return immediately
                        screen_result = {"text": "", "harmful_hits": [], "status": "initializing", "note": "EasyOCR is initializing (first time may take 20-30 seconds). Screen analysis will be available shortly."}
                    else:
                        # Update last OCR time before processing
                        _last_screen_ocr_time = current_time
                        # Process screen OCR with timeout to prevent blocking
                        import threading
                        screen_result_container = {"result": None, "done": False, "error": None}
                        
                        def run_screen_ocr():
                            try:
                                result = analyze_screen_content(payload["screen"])
                                screen_result_container["result"] = result
                            except Exception as e:
                                print(f"Screen analysis error: {e}")
                                screen_result_container["error"] = str(e)
                                screen_result_container["result"] = {"text": "", "harmful_hits": [], "status": "error", "error": str(e)[:200]}
                            finally:
                                screen_result_container["done"] = True
                        
                        ocr_thread = threading.Thread(target=run_screen_ocr, daemon=True)
                        ocr_thread.start()
                        ocr_thread.join(timeout=8.0)  # Reduced to 8 seconds for faster response
                        
                        if not screen_result_container["done"]:
                            # Screen OCR is taking too long - return timeout status but don't fail completely
                            print("Screen OCR timeout - processing took longer than 8 seconds")
                            screen_result = {"text": "", "harmful_hits": [], "status": "timeout", "note": "Screen analysis taking longer than expected. Processing in background..."}
                        elif screen_result_container["error"]:
                            # There was an error during processing
                            screen_result = screen_result_container["result"] or {"text": "", "harmful_hits": [], "status": "error", "error": screen_result_container["error"][:200]}
                        else:
                            screen_result = screen_result_container["result"] or {"text": "", "harmful_hits": [], "status": "ok", "note": "No text detected on screen"}
            except Exception as e:
                print(f"Screen analysis error: {e}")
                screen_result = {"text": "", "harmful_hits": [], "status": "error", "error": str(e)[:200]}

        # Extract text from screen OCR for sentiment analysis if no direct text provided
        # Always try to extract text from screen for better predictions
        if screen_result and not text_result:
            fallback_text = (screen_result.get("text") or "").strip()
            if fallback_text and len(fallback_text) > 10:  # Only analyze if meaningful text
                condensed = " ".join(fallback_text.split())[:512]  # Limit length
                try:
                    text_result = analyze_text_sentiment(condensed)
                    text_result["source"] = "screen_ocr"
                    print(f"✅ Text extracted from screen OCR: {len(condensed)} chars, sentiment: {text_result.get('label', 'unknown')}")
                except Exception as e:
                    print(f"Screen text sentiment error: {e}")
                    text_result = None
            else:
                # No meaningful text from screen, provide neutral result so text module contributes
                if screen_result.get("status") == "ok":
                    text_result = {"label": "NEUTRAL", "score": 0.5, "mood": "neutral", "insights": ["No meaningful text on screen."], "source": "screen_ocr"}
                    print("ℹ️ Screen OCR found no meaningful text, using neutral sentiment.")
        
        # If still no text result, create a default neutral one so synthesis has all modules
        if not text_result:
            text_result = {"label": "NEUTRAL", "score": 0.5, "mood": "neutral", "insights": ["No text input provided."], "source": "default"}
            print("ℹ️ No text data available, using default neutral sentiment.")

        snapshot = ModuleSnapshot(
            text=text_result,
            speech=speech_result,
            face=face_result,
            screen=screen_result,
        )
        
        # Debug: Print snapshot data to verify all modules are working
        print(f"\n📊 ===== MONITOR CYCLE =====")
        print(f"📊 Snapshot data: text={bool(text_result)}, speech={bool(speech_result)}, face={bool(face_result)}, screen={bool(screen_result)}")
        if text_result:
            print(f"  ✅ Text: {text_result.get('label', 'unknown')} (score: {text_result.get('score', 0):.2f}, source: {text_result.get('source', 'direct')})")
        else:
            print(f"  ❌ Text: No data")
        if speech_result:
            emotion = speech_result.get('emotion', 'unknown')
            note = speech_result.get('note', '')
            print(f"  ✅ Speech: {emotion} {f'({note})' if note else ''}")
        else:
            print(f"  ❌ Speech: No data")
        if face_result:
            print(f"  ✅ Face: {face_result.get('dominant_emotion', 'unknown')} (confidence: {face_result.get('confidence', 0):.2f})")
        else:
            print(f"  ❌ Face: No data")
        if screen_result:
            status = screen_result.get('status', 'unknown')
            text_len = len(screen_result.get('text', ''))
            print(f"  ✅ Screen: {status} (text length: {text_len})")
        else:
            print(f"  ❌ Screen: No data")
        
        try:
            synthesis = synthesize(snapshot)
            # Debug: Print synthesis result to verify it's working
            print(f"✅ Synthesis: score={synthesis.get('score'):.1f}, risk={synthesis.get('risk_level')}, state={synthesis.get('overall_state')}")
            print(f"📊 ===== END CYCLE =====\n")
        except Exception as e:
            print(f"Synthesis error: {e}")
            import traceback
            traceback.print_exc()
            synthesis = {
                "score": 50.0,
                "overall_state": "steady",
                "risk_level": "low",
                "notes": [f"Synthesis error: {str(e)}"],
                "actions": ["Check system logs for details"],
            }

        if synthesis.get("risk_level") in {"high", "critical"}:
            try:
                log_alert(synthesis["risk_level"], "Behavior engine flagged elevated risk", synthesis)
            except Exception as e:
                print(f"Alert logging error: {e}")

        try:
            log_interaction(
                "monitor",
                {
                    "modules": {
                        "text": text_result,
                        "speech": speech_result,
                        "face": face_result,
                        "screen": screen_result,
                    },
                    "synthesis": synthesis,
                },
            )
        except Exception as e:
            print(f"Interaction logging error: {e}")

        # Ensure synthesis is always included and properly formatted
        response_data = {
            "synthesis": synthesis,
            "text": text_result,
            "speech": speech_result,
            "face": face_result,
            "screen": screen_result,
        }
        
        # Debug: Print response summary
        print(f"Response: synthesis={bool(synthesis)}, text={bool(text_result)}, speech={bool(speech_result)}, face={bool(face_result)}, screen={bool(screen_result)}")
        if synthesis:
            print(f"  Synthesis details: score={synthesis.get('score')}, risk={synthesis.get('risk_level')}, state={synthesis.get('overall_state')}")
        if synthesis:
            print(f"  Synthesis details: score={synthesis.get('score')}, risk={synthesis.get('risk_level')}, state={synthesis.get('overall_state')}")
        
        return jsonify(response_data)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Monitor endpoint error: {error_trace}")
        # Return a valid response structure even on error so frontend can display it
        return jsonify({
            "text": None,
            "speech": None,
            "face": None,
            "screen": {"status": "error", "error": str(e)[:200]},
            "synthesis": {
                "score": 50.0,
                "overall_state": "steady",
                "risk_level": "low",
                "notes": [f"Analysis error: {str(e)[:100]}"],
                "actions": ["Please check server logs and try again"],
            },
            "error": str(e),
        }), 500


@main.route("/companion", methods=["POST"])
def companion():
    """Wellness Companion chatbot endpoint - supports text and voice input."""
    try:
        payload = request.get_json(force=True) or {}
        message = payload.get("message", "").strip()
        history = payload.get("history", [])
        mode = payload.get("mode", "text")

        if not message:
            return jsonify({"error": "message is required"}), 400

        client = _openai_client()
        if client is None:
            return jsonify({
                "error": "OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file or environment variables."
            }), 500

        system_prompt = (
            "You are AIP-MWA, an empathetic AI mental wellness guide. "
            "Offer concise, actionable suggestions, remind users you are not a substitute for a doctor, "
            "and encourage professional help when risk appears high. "
            "Keep responses brief (2-3 sentences) and supportive."
        )
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=300,
                temperature=0.7,
            )
            response = completion.choices[0].message.content
        except OpenAIError as exc:
            error_msg = str(exc)
            print(f"OpenAI API error: {error_msg}")
            
            # Provide user-friendly error messages
            if "429" in error_msg or "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
                return jsonify({
                    "error": "OpenAI API quota exceeded. Please check your OpenAI account billing and quota limits. The chatbot requires a valid API key with available credits."
                }), 500
            elif "401" in error_msg or "invalid" in error_msg.lower() or "api key" in error_msg.lower():
                return jsonify({
                    "error": "Invalid OpenAI API key. Please check your OPENAI_API_KEY in your .env file or environment variables."
                }), 500
            elif "rate limit" in error_msg.lower():
                return jsonify({
                    "error": "OpenAI API rate limit exceeded. Please wait a moment and try again."
                }), 500
            else:
                return jsonify({
                    "error": f"AI service error: {error_msg}"
                }), 500
        except Exception as exc:
            print(f"Unexpected error in OpenAI call: {exc}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Unexpected error: {str(exc)}"}), 500

        log_interaction("companion", {"message": message, "response": response, "mode": mode})
        return jsonify({"response": response})
    except Exception as e:
        print(f"Companion endpoint error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500
