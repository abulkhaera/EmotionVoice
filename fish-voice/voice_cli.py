"""CLI for EmotionVoice local server. Made for Claude / scripts.

Server must run first (start.bat). Examples:
  python voice_cli.py config
  python voice_cli.py voices --lang id --q narrator
  python voice_cli.py voices --mine
  python voice_cli.py tts --file script.txt --voice <id> --lang id
  python voice_cli.py tts --text "[happy] Hello!" --out hello.mp3
  python voice_cli.py clone --title "My voice" --audio a.wav b.wav --consent
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE = Path(__file__).parent
load_dotenv(BASE / ".env")
URL = f"http://127.0.0.1:{os.getenv('PORT', '5000')}"

# UTF-8 out so Arabic / CJK print fine on Windows console
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def die(msg, code=1):
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False))
    sys.exit(code)


def call(method, path, **kw):
    try:
        r = requests.request(method, URL + path, timeout=kw.pop("timeout", 300), **kw)
    except requests.ConnectionError:
        die(f"Server not running at {URL}. Run start.bat first.")
    if not r.ok:
        try:
            die(r.json().get("error", r.text))
        except ValueError:
            die(f"HTTP {r.status_code}: {r.text[:300]}")
    return r


def out(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def cmd_config(a):
    out(call("GET", "/api/config").json())


def cmd_voices(a):
    p = {"q": a.q or "", "lang": a.lang or "", "mine": "1" if a.mine else "0"}
    out(call("GET", "/api/voices", params=p).json()["items"])


def cmd_tts(a):
    if a.file:
        text = Path(a.file).read_text(encoding="utf-8")
    elif a.text:
        text = a.text
    else:
        die("Give --text or --file")
    body = {
        "text": text, "voice_id": a.voice or "", "model": a.model or "",
        "format": a.format, "speed": a.speed, "volume": a.volume,
        "temperature": a.temperature, "top_p": a.top_p,
    }
    r = call("POST", "/api/tts", json=body)
    saved = BASE / "output" / r.headers.get("X-File-Name", f"voice.{a.format}")
    final = saved
    if a.out:
        final = Path(a.out).resolve()
        final.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(saved, final)
    out({"ok": True, "file": str(final), "bytes": len(r.content)})


def cmd_clone(a):
    if not a.consent:
        die("Need --consent: confirm voice is yours or you have permission.")
    files = []
    for p in a.audio:
        p = Path(p)
        if not p.is_file():
            die(f"No file: {p}")
        files.append(("voices", (p.name, p.read_bytes())))
    data = {
        "title": a.title, "consent": "1", "lang": a.lang or "",
        "enhance": "0" if a.no_enhance else "1", "transcript": a.transcript or "",
    }
    out(call("POST", "/api/clone", data=data, files=files).json())


def main():
    ap = argparse.ArgumentParser(description="EmotionVoice CLI")
    sp = ap.add_subparsers(dest="cmd", required=True)

    sp.add_parser("config", help="show key status, models, default voice")

    v = sp.add_parser("voices", help="search voices")
    v.add_argument("--q", help="title keyword")
    v.add_argument("--lang", choices=["en", "id", "zh", "ja", "ko", "ar"])
    v.add_argument("--mine", action="store_true", help="only my voices")

    t = sp.add_parser("tts", help="make speech")
    t.add_argument("--text")
    t.add_argument("--file", help="UTF-8 text file (best for non-English)")
    t.add_argument("--voice", help="voice id (reference_id)")
    t.add_argument("--model", help="s2.1-pro-free | s2.1-pro | s2-pro | s1 | drama-3-preview")
    t.add_argument("--format", default="mp3", choices=["mp3", "wav", "opus"])
    t.add_argument("--speed", type=float, default=1.0)
    t.add_argument("--volume", type=float, default=0)
    t.add_argument("--temperature", type=float, default=0.7)
    t.add_argument("--top_p", type=float, default=0.7)
    t.add_argument("--out", help="copy result to this path")

    c = sp.add_parser("clone", help="make voice from my audio")
    c.add_argument("--title", required=True)
    c.add_argument("--audio", nargs="+", required=True)
    c.add_argument("--transcript", help="exact words (1 clip only)")
    c.add_argument("--lang", choices=["en", "id", "zh", "ja", "ko", "ar"])
    c.add_argument("--no-enhance", action="store_true")
    c.add_argument("--consent", action="store_true")

    a = ap.parse_args()
    {"config": cmd_config, "voices": cmd_voices, "tts": cmd_tts, "clone": cmd_clone}[a.cmd](a)


if __name__ == "__main__":
    main()
