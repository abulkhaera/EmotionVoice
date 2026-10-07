# EmotionVoice

Small local web app. Text -> emotional speech with Fish Audio.

## Run (Windows)
1. Install Python 3.10+ (tick "Add to PATH").
2. Double-click `start.bat`. First time it makes `.env` and opens Notepad.
3. Paste key from https://fish.audio/app/api-keys/ into `FISH_API_KEY=`. Save.
4. Double-click `start.bat` again. Browser opens at http://127.0.0.1:5000

## Use
- Click emotion chips to drop tags at cursor.
- S2 models: `[happy] text`, free-form cues OK (`[slightly nervous]`).
- S1 model: `(happy) text`, fixed tags only. Switching model converts tags.
- Pick voice from search, or paste a voice ID.
- Audio plays in page and saves to `output/`.

## Languages
Pick language -> voice list shows native voices. Type script in that language.
English, Bahasa Indonesia, Mandarin, Japanese, Korean, Arabic. S1 has no Indonesian.

## My voice
Open "Add my voice". Upload clips or record mic (10-30 s, quiet room).
Tick permission box. Create. Voice saved private in your Fish account.

## Notes
- Key stays in `.env` on server side. Not sent to browser.
- Do not share or commit `.env`.
- Server binds 127.0.0.1 only (local use).
