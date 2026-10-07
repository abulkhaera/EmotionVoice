"""Fish Audio emotional TTS web app. Key lives in .env, never sent to browser."""
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory, Response

BASE = Path(__file__).parent
load_dotenv(BASE / ".env")

API_KEY = os.getenv("FISH_API_KEY", "").strip()
DEFAULT_VOICE = os.getenv("DEFAULT_VOICE_ID", "").strip()
DEFAULT_MODEL = os.getenv("FISH_MODEL", "s2.1-pro-free").strip()
PORT = int(os.getenv("PORT", "5000"))
API = "https://api.fish.audio"

MODELS = ["s2.1-pro-free", "s2.1-pro", "s2-pro", "s1", "drama-3-preview"]
LANGS = {"en", "id", "zh", "ja", "ko", "ar"}
FORMATS = {"mp3": "audio/mpeg", "wav": "audio/wav", "opus": "audio/ogg"}

OUT = BASE / "output"
OUT.mkdir(exist_ok=True)

app = Flask(__name__, static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 60 * 1024 * 1024  # 60 MB upload cap

AUDIO_EXT = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".webm", ".aac"}


def auth():
    return {"Authorization": f"Bearer {API_KEY}"}


def clamp(v, lo, hi, default):
    try:
        return max(lo, min(hi, float(v)))
    except (TypeError, ValueError):
        return default


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/config")
def config():
    return jsonify(
        has_key=bool(API_KEY),
        default_voice=DEFAULT_VOICE,
        default_model=DEFAULT_MODEL if DEFAULT_MODEL in MODELS else "s2.1-pro-free",
        models=MODELS,
    )


@app.get("/api/voices")
def voices():
    if not API_KEY:
        return jsonify(error="FISH_API_KEY missing in .env"), 500
    params = {
        "page_size": 20,
        "sort_by": "score",
        "self": "true" if request.args.get("mine") == "1" else "false",
    }
    q = request.args.get("q", "").strip()
    if q:
        params["title"] = q
    lang = request.args.get("lang", "").strip()
    if lang in LANGS:
        params["language"] = lang
    try:
        r = requests.get(f"{API}/model", headers=auth(), params=params, timeout=20)
    except requests.RequestException as e:
        return jsonify(error=f"Network error: {e}"), 502
    if r.status_code != 200:
        return jsonify(error=f"Fish Audio {r.status_code}: {r.text[:300]}"), r.status_code
    items = [
        {
            "id": m.get("_id"),
            "title": m.get("title", ""),
            "langs": m.get("languages", []),
            "cover": m.get("cover_image", ""),
        }
        for m in r.json().get("items", [])
    ]
    return jsonify(items=items)


@app.post("/api/clone")
def clone():
    """Make private voice model from user audio. fast mode = ready now."""
    if not API_KEY:
        return jsonify(error="FISH_API_KEY missing in .env"), 500
    if request.form.get("consent") != "1":
        return jsonify(error="Confirm voice is yours or you have permission."), 400
    title = (request.form.get("title") or "").strip()[:80]
    if not title:
        return jsonify(error="Give the voice a name."), 400
    files = [f for f in request.files.getlist("voices") if f and f.filename]
    if not files:
        return jsonify(error="Add at least one audio file."), 400
    if len(files) > 20:
        return jsonify(error="Max 20 files."), 400
    bad = [f.filename for f in files if Path(f.filename).suffix.lower() not in AUDIO_EXT]
    if bad:
        return jsonify(error="Not audio: " + ", ".join(bad)), 400

    data = [
        ("type", "tts"),
        ("title", title),
        ("train_mode", "fast"),
        ("visibility", "private"),
        ("enhance_audio_quality", "true" if request.form.get("enhance") == "1" else "false"),
    ]
    lang = request.form.get("lang", "")
    if lang in LANGS:
        data.append(("tags", lang))
    transcript = (request.form.get("transcript") or "").strip()
    if transcript and len(files) == 1:  # else Fish runs ASR itself
        data.append(("texts", transcript))

    upload = [
        ("voices", (f.filename, f.read(), f.mimetype or "application/octet-stream"))
        for f in files
    ]
    try:
        r = requests.post(f"{API}/model", headers=auth(), data=data, files=upload, timeout=300)
    except requests.RequestException as e:
        return jsonify(error=f"Network error: {e}"), 502
    if r.status_code not in (200, 201):
        msg = r.text[:400]
        try:
            msg = r.json().get("message", msg)
        except ValueError:
            pass
        return jsonify(error=f"Fish Audio {r.status_code}: {msg}"), r.status_code
    m = r.json()
    return jsonify(id=m.get("_id"), title=m.get("title", title), state=m.get("state"))


@app.errorhandler(413)
def too_big(_):
    return jsonify(error="Upload too big (60 MB max)."), 413


@app.post("/api/tts")
def tts():
    if not API_KEY:
        return jsonify(error="FISH_API_KEY missing in .env"), 500
    d = request.get_json(force=True) or {}
    text = (d.get("text") or "").strip()
    if not text:
        return jsonify(error="Text is empty"), 400
    if len(text) > 5000:
        return jsonify(error="Text too long (max 5000 chars)"), 400

    model = d.get("model") if d.get("model") in MODELS else DEFAULT_MODEL
    fmt = d.get("format") if d.get("format") in FORMATS else "mp3"
    voice = (d.get("voice_id") or DEFAULT_VOICE or "").strip()

    body = {
        "text": text,
        "format": fmt,
        "temperature": clamp(d.get("temperature"), 0, 1, 0.7),
        "top_p": clamp(d.get("top_p"), 0, 1, 0.7),
        "prosody": {
            "speed": clamp(d.get("speed"), 0.5, 2.0, 1.0),
            "volume": clamp(d.get("volume"), -20, 20, 0),
        },
        "latency": "normal",
        "normalize": True,
    }
    if voice:
        body["reference_id"] = voice

    headers = {**auth(), "Content-Type": "application/json", "model": model}
    try:
        r = requests.post(f"{API}/v1/tts", headers=headers, json=body, timeout=180)
    except requests.RequestException as e:
        return jsonify(error=f"Network error: {e}"), 502

    if r.status_code != 200:
        msg = r.text[:400]
        try:
            msg = r.json().get("message", msg)
        except ValueError:
            pass
        hint = {
            401: " (bad API key?)",
            402: " (no credits / plan limit)",
            429: " (rate limited, wait a bit)",
        }.get(r.status_code, "")
        return jsonify(error=f"Fish Audio {r.status_code}: {msg}{hint}"), r.status_code

    name = f"voice_{time.strftime('%Y%m%d_%H%M%S')}.{fmt}"
    (OUT / name).write_bytes(r.content)
    return Response(
        r.content,
        mimetype=FORMATS[fmt],
        headers={"X-File-Name": name},
    )


if __name__ == "__main__":
    if not API_KEY:
        print("WARNING: FISH_API_KEY not set. Edit .env first.")
    print(f"Open http://127.0.0.1:{PORT}")
    app.run(host="127.0.0.1", port=PORT, debug=False)
