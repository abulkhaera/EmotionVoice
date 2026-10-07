---
name: emotion-voice
description: Make emotional AI speech (mp3/wav) or clone the user's voice with the local EmotionVoice app (Fish Audio). Use when the user asks for a voiceover, narration, spoken audio, TTS, or their own voice, in English, Indonesian, Mandarin, Japanese, Korean or Arabic.
---

# EmotionVoice

Local Flask app over Fish Audio API. Folder: the `fish-voice` folder (has `app.py`, `start.bat`, `voice_cli.py`).
API key lives in `.env`. Never print, read out, or edit `FISH_API_KEY`.

Needs a shell on the user's Windows PC (Claude Code, or desktop app with folder access).
A cloud sandbox cannot reach `127.0.0.1` on the user's PC.

## 1. Make sure server runs

```
python voice_cli.py config
```
- `has_key: true` -> ready.
- "Server not running" -> start it in the background: `start "" cmd /c start.bat` (from the folder), wait ~10 s, check again. First run installs packages; can take a minute.
- `has_key: false` -> ask user to put key in `.env`. Do not ask them to paste the key in chat.

Always run the CLI with the venv python if it exists: `.venv\Scripts\python.exe voice_cli.py ...`

## 2. Write the script

Write text to a UTF-8 file (e.g. `scripts\job.txt`), then pass `--file`.
Do not pass Arabic / Chinese / Japanese / Korean via `--text` on Windows: console encoding breaks it.

Emotion cues (S2 models, default `s2.1-pro-free`): square brackets, at sentence start.
```
[excited] We did it!
[sad][whispering] I miss you.
I [emphasis] really mean it. [break] Okay.
[laughing] Ha ha, that's funny.
```
- Emotions: happy sad angry excited calm nervous confident surprised scared worried frustrated empathetic proud grateful curious sarcastic hopeful nostalgic determined disappointed ...
- Tone: `[whispering] [shouting] [screaming] [soft tone] [in a hurry tone] [emphasis]`
- Sounds: `[laughing] [chuckling] [sighing] [sobbing] [gasping] [panting] [yawning] [clear throat]` — add matching text after (e.g. "Ha ha").
- Pauses: `[break]` `[long-break]`
- Free-form works on S2: `[slightly nervous but hopeful]`.
- Max 3 cues per sentence. One main emotion per sentence. Keep cue tags in English even for other languages.
- S1 model only: use `(happy)` parentheses, fixed tags, no Indonesian.

Language = the language the text is written in. No language flag. The app does NOT translate. Write the script in the target language yourself. For a natural accent, pick a native voice of that language.

## 3. Pick a voice

```
python voice_cli.py voices --lang id
python voice_cli.py voices --lang ja --q narrator
python voice_cli.py voices --mine
```
Langs: en id zh ja ko ar. Use the `id` field as `--voice`.
- Prefer `--mine` voices if the user wants their own voice.
- Avoid voices cloned from real public figures (politicians, celebrities) unless the user clearly asks and the use is plainly parody / non-deceptive.
- No `--voice` = default voice from `.env`, else Fish default.

## 4. Generate

```
python voice_cli.py tts --file scripts\job.txt --voice <id> --out output\job.mp3
```
Options: `--model`, `--format mp3|wav|opus`, `--speed 0.5-2`, `--volume dB`, `--temperature 0-1` (higher = more expressive), `--top_p 0-1`.
Output is JSON: `{"ok": true, "file": "...path..."}`. Tell the user the path. Long scripts (>5000 chars): split into parts, number the files.

## 5. Clone user's voice (only on request)

```
python voice_cli.py clone --title "My voice ID" --audio rec1.wav rec2.wav --lang id --consent
```
- Only pass `--consent` after the user confirms it is their voice or they have permission. Ask if unclear.
- Good input: 10-30 s per clip, one speaker, quiet room, no music. wav/mp3/flac best.
- Returns `{"id": ...}` -> use as `--voice`. Voice is private in their Fish account.
- Voice keeps the accent of the recording language. For fluent Japanese, a Japanese recording works best.

## Errors

| Error | Do |
|---|---|
| Server not running | start `start.bat`, retry once |
| 401 | key bad: ask user to fix `.env`, restart server |
| 402 | out of credits: tell user, suggest `--model s2.1-pro-free` |
| 429 | rate limit: wait 30 s, retry once |
| Tag read out loud | wrong syntax for model: S2 `[ ]`, S1 `( )` |

Do not loop retries. Do not spend credits on test runs the user did not ask for.
