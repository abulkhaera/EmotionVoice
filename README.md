# EmotionVoice

Turn text into **emotional, expressive speech** — and clone your own voice — with the [Fish Audio](https://fish.audio) API.
A small local web app plus a CLI. One double-click to start on Windows.

```
[excited] We finally did it!
[sighing] It took so long though.
[whispering] Don't tell anyone yet.
```

↑ Type that, press **Generate**, hear three different emotions in one clip.

---

## Features

- **60+ emotion & delivery tags** — happy, sad, sarcastic, nostalgic, whispering, shouting, laughing, sighing, pauses… One click inserts a tag at the cursor. S2 models also accept free-form cues like `[slightly nervous but hopeful]`.
- **6 languages, native voices** — English, Bahasa Indonesia, Mandarin, Japanese, Korean, Arabic. Picking a language filters the voice library to native speakers; Arabic switches the editor to right-to-left.
- **Clone your own voice** — upload clips or record straight from the mic (converted to WAV in the browser). Voices are saved **private** in your Fish Audio account and ready instantly.
- **Voice library search** — browse public voices or only your own.
- **Fine control** — model, format (mp3 / wav / opus), speed, volume, expressiveness, diversity.
- **History & auto-save** — every take plays in the page and is saved to `output/`.
- **CLI for scripts and AI agents** — `voice_cli.py` returns clean JSON. Includes a ready-made Claude skill (`SKILL.md`).
- **Key stays private** — your API key lives in `.env` on the local server and is never sent to the browser.

## Quick start (Windows)

1. Install **Python 3.10+** from [python.org](https://www.python.org/downloads/) — tick **"Add python.exe to PATH"**.
2. Get an API key at [fish.audio/app/api-keys](https://fish.audio/app/api-keys/).
3. Double-click **`start.bat`**. On first run it creates `.env` and opens it in Notepad.
4. Paste your key after `FISH_API_KEY=`, save, close.
5. Double-click **`start.bat`** again. It sets up a virtual env, installs packages, and opens **http://127.0.0.1:5000**.

### macOS / Linux

```bash
cp .env.example .env          # then add your key
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py                 # open http://127.0.0.1:5000
```

## Configuration (`.env`)

| Variable | Default | What it does |
|---|---|---|
| `FISH_API_KEY` | — | **Required.** Your Fish Audio API key. |
| `FISH_MODEL` | `s2.1-pro-free` | Default model: `s2.1-pro-free`, `s2.1-pro`, `s2-pro`, `s1`, `drama-3-preview`. |
| `DEFAULT_VOICE_ID` | blank | Voice used when none is picked. Blank = Fish default voice. |
| `PORT` | `5000` | Local port. |

## Writing emotional scripts

Put a cue at the **start of a sentence**. Combine up to three.

```
[happy] What a beautiful day!
[sad][whispering] I miss you so much.
This is [emphasis] really important. [break] Okay?
[laughing] Ha ha, you got me.
```

| Type | Examples |
|---|---|
| Emotions | `happy` `sad` `angry` `excited` `calm` `nervous` `confident` `sarcastic` `hopeful` `nostalgic` `determined` … |
| Tone | `whispering` `shouting` `screaming` `soft tone` `in a hurry tone` `emphasis` |
| Sounds | `laughing` `chuckling` `sighing` `sobbing` `gasping` `panting` `yawning` `clear throat` |
| Pauses | `break` `long-break` |

**Syntax depends on the model:** S2 family uses `[brackets]`; legacy S1 uses `(parentheses)` with a fixed tag set. The app converts tags automatically when you switch models.

## Languages

Fish Audio detects the language from the text — there is no language flag, and **the app does not translate**. To get fluent speech:

1. Write the script in the target language.
2. Pick a **native voice** for that language (the Language dropdown filters for you). An English voice reading Japanese will sound accented.

Emotion tags stay in English inside any language. S1 does not support Indonesian; use an S2 model.

## Clone your voice

Open **Add my voice** in the sidebar.

- Upload 1–20 clips, or press **Record**. Best results: **10–30 s per clip, one speaker, quiet room, no music.**
- Optional transcript (single clip only). Leave blank to auto-transcribe.
- Tick the permission box — only clone voices that are yours or that you have consent to use.

A voice keeps the accent of the language it was recorded in. For fluent output in several languages, record a clip in each and create one voice per language.

## CLI

Start the server first, then:

```bash
python voice_cli.py config
python voice_cli.py voices --lang id
python voice_cli.py voices --mine
python voice_cli.py tts --file script.txt --voice <voice_id> --out out/intro.mp3
python voice_cli.py clone --title "My voice" --audio a.wav b.wav --lang id --consent
```

All commands print JSON. Use `--file` (UTF-8) for Arabic, Chinese, Japanese, or Korean text — the Windows console mangles those when passed with `--text`.

## Use with Claude

`SKILL.md` teaches Claude to run the app through the CLI: check the server, write a tagged script, pick a native voice, generate, and report the file path. `CLAUDE.md` points Claude Code at it automatically when it opens this folder.

This needs a Claude with a shell on the same machine (Claude Code, or the Claude desktop app with this folder connected). A cloud-only session cannot reach `127.0.0.1` on your PC.

## Project structure

```
app.py            Flask server — proxies Fish Audio, keeps the key server-side
static/index.html Web UI (single file, no build step)
voice_cli.py      Command-line client for the local server
start.bat         Windows launcher (venv, install, open browser)
SKILL.md          Claude skill for driving the app
CLAUDE.md         Pointer for Claude Code
.env.example      Config template
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Python not found` | Reinstall Python with "Add to PATH" ticked. |
| `401` | Wrong API key — check `.env`, restart. |
| `402` | Out of credits — switch to `s2.1-pro-free`. |
| `429` | Rate limited — wait and retry. |
| Tag is read out loud | Wrong syntax for the model: S2 `[ ]`, S1 `( )`. |
| Mic blocked | Allow microphone access for `127.0.0.1` in the browser. |
| Port in use | Change `PORT` in `.env`. |

## Responsible use

Don't use cloned or celebrity voices to deceive, impersonate, or mislead. Get consent before cloning anyone's voice, and follow Fish Audio's terms of service and the laws where you live.

## Credits

Built on the [Fish Audio API](https://docs.fish.audio). Not affiliated with Fish Audio.
