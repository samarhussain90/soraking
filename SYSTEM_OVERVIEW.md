# 🎬 Ad Cloner Platform - AI Director System

## 🚀 Quick Start

```bash
# Start the server
python server.py

# Open browser
http://localhost:3000

# Upload video → AI generates unique ads automatically
```

---

## 🏗️ System Architecture

### Pipeline Flow:
```
1. 📹 Upload Video
        ↓
2. 🔍 Gemini Analysis (script, vertical, moments)
        ↓
3. 🔄 Variant Generation (soft/medium/aggressive/ultra)
        ↓
4. 🤖 AI Director (OpenAI generates scene structure)
        ↓
5. 📝 Prompt Composer (converts to Sora format)
        ↓
6. ✅ Validation (check limits & quality)
        ↓
7. 🎥 Sora 2 Pro (generates videos)
        ↓
8. 🎬 Assembly (combine scenes)
        ↓
9. 📊 Evaluation (quality score)
```

---

## 🤖 AI Director (NEW!)

**What it does:**
- Analyzes Gemini's video breakdown
- Uses OpenAI GPT-4o to generate complete scene specs
- **No hardcoded text, audio, or visual patterns**
- Fully dynamic and adaptive

**What it generates:**

### 1. Visual Layer
- Shot progressions (3-4 shots per 12s scene)
- Camera movements (whip pan, zoom, dolly, static)
- Lighting transitions (dramatic → warm)
- Focus techniques (shallow depth, sharp)

### 2. Audio Layer
- **Voiceover**: Exact script from analysis, tone, pace, emotion
- **Music**: Genre, BPM (75-175), intensity curve
- **SFX**: Precise timing (button clicks, whoosh, cash register)
- **Drops**: Beat-synced with visual reveals

### 3. Text Overlays
- **Extracted from script** (not hardcoded!)
  - Prices: "$120 a month" → "$120 A MONTH?!"
  - CTAs: "Click below" → "CHECK IF YOU QUALIFY"
  - Questions: Auto-generated hooks
- Timing, position, font, size, color, animation
- Synced with voiceover mentions

### 4. Sync Points
- Text appears when price mentioned
- SFX on key moments (reveals, clicks)
- Music drops with visual peaks

---

## 📁 Key Files

### Core Modules:
- `modules/ad_director.py` - **AI Director with OpenAI**
- `modules/sora_prompt_composer.py` - AI scenes → Sora prompts
- `modules/gemini_analyzer.py` - Video analysis with Gemini
- `modules/sora_client.py` - Sora 2 Pro API client
- `ad_cloner.py` - Main orchestrator

### Config:
- `config.py` - Sora 2 Pro settings (1792x1024, audio enabled)
- `.env` - API keys (OpenAI, Gemini)

### Frontend:
- `server.py` - Flask server with WebSocket
- `frontend/index.html` - Web interface
- `frontend/app.js` - Real-time updates

---

## 🎯 Aggression Levels

| Level | BPM | Energy | Text Style | Camera |
|-------|-----|--------|------------|--------|
| **Soft** | 75-95 | Calm, friendly | Gentle fades | Slow push-ins |
| **Medium** | 110-130 | Engaging, upbeat | Smooth pops | Steady dolly |
| **Aggressive** | 135-150 | Urgent, intense | Bold crashes | Fast whip pans |
| **Ultra** | 155-175 | Explosive, extreme | Massive reveals | Crash zooms |

---

## 📊 Example Output

### Input Script:
> "I was paying $120 a month for car insurance until I found a link that changed everything. After a quick two-minute check, I qualified for $39 a month."

### AI Director Generates:

**Scene 1 (Hook):**
```
Visual: Medium close-up → quick whip pan → frustrated close-up zoom
Audio: Urgent voice, 140 BPM electronic, cash register SFX at 0:03
Text: "$120 A MONTH?!" (Impact, 130pt, red, crash-in at 0:02)
```

**Scene 2 (Solution):**
```
Visual: Phone screen tilt → finger tap → price reveal zoom
Audio: Confident voice, 145 BPM, button click + success chime
Text: "ONLY $39/MONTH" (green, pop) + "CHECK IF YOU QUALIFY" (yellow, slide)
```

### Sora Prompt (Scene 1):
```
[00:00-00:03] MEDIUM CLOSE-UP: female spokesperson looking at a bill. 
Quick whip pan to face camera. Dramatic lighting. Sharp focus.

[00:03-00:06] CLOSE-UP: spokesperson's frustrated expression. 
Slow zoom-in camera. High-contrast lighting. Shallow depth focus.

AUDIO: urgent voice, fast pace, frustrated emotion. Says: "I was paying 
$120 a month for car insurance until I found a link that changed everything." 
Background music: electronic, 140 BPM, builds. 0:03 beat intensifies, 
0:08 climax. Sound effect at 0:03: cash register cha-ching.

TEXT OVERLAYS: At 0:02, crash-in: "$120 A MONTH?!" (Impact, 130pt, red 
with black outline). Fades out at 0:05.

TECHNICAL: 4K resolution, 1792x1024, urgent style, vibrant grade, 
cinematic audio mix.
```

**Length: 852 characters** ✅ Under 2000 limit

---

## 🧪 Testing

### Test AI Director Only:
```bash
python test_ai_director.py
# → Generates 2 scenes
# → Shows visual/audio/text specs
# → Saves to test_ai_director_output.json
```

### Test Full Pipeline:
```bash
python server.py
# Open http://localhost:3000
# Upload: autoad.mp4 (or any video)
# → Gemini analyzes (30-60s)
# → AI Director generates scenes
# → Sora creates videos (~15-20min)
# → Review output/videos/
```

---

## 📂 Output Structure

```
output/
├── analysis/
│   ├── analysis_*.json          # Gemini analysis
│   └── sora_prompts_*.json      # AI-generated prompts
├── videos/
│   ├── soft/scene_*.mp4
│   ├── medium/scene_*.mp4
│   ├── aggressive/scene_*.mp4
│   ├── ultra/scene_*.mp4
│   ├── final_soft.mp4
│   ├── final_medium.mp4
│   ├── final_aggressive.mp4
│   └── final_ultra.mp4
└── logs/
    └── session_*/
        ├── events.json
        └── progress.json
```

---

## 🔧 Configuration

### Sora 2 Pro Settings (`config.py`):
```python
SORA_MODEL = 'sora-2-pro'          # Better quality, character consistency
SORA_RESOLUTION = '1792x1024'       # Higher resolution
SORA_DURATION = '12'                # 12s per scene
AUDIO_ENABLED = True                # Generate audio in prompts
```

### AI Director Settings:
```python
# In ad_director.py
model = "gpt-4o"                    # Best reasoning model
temperature = 0.8                   # Creative but consistent
response_format = {"type": "json"}  # Structured output
```

---

## 🎯 Supported Verticals

- **Auto Insurance**: Red/yellow, urgent, fast cuts, cash register SFX
- **Health Insurance**: Blue/green, calm, smooth transitions, gentle chimes
- **Finance**: Gold/navy, professional, dramatic zooms, success tones
- **General**: Adaptive based on script content

**AI Director auto-detects vertical from Gemini analysis!**

---

## 🚨 Troubleshooting

### Port 3000 in use:
```bash
pkill -f "python server.py"
python server.py
```

### API Keys missing:
Check `.env` has:
```
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
```

### Validation errors:
- Check `output/logs/session_*/events.json`
- Prompts are auto-validated (max 2000 chars)
- AI Director respects limits

---

## 📚 Documentation

- **`AI_DIRECTOR_SUMMARY.md`** - Technical deep dive
- **`BEFORE_AFTER.md`** - Template vs AI comparison
- **`SYSTEM_OVERVIEW.md`** - This file (quick reference)
- **`QUICK_START_GUIDE.md`** - Original Sora 2 Pro guide

---

## ✅ Key Advantages

1. **Fully Dynamic** - No hardcoded text, audio, or visuals
2. **Intelligent** - AI understands context and extracts meaning
3. **Adaptive** - Works with any script/vertical automatically
4. **Conversion-Focused** - AI knows what makes ads work
5. **Scalable** - Add new verticals → AI adapts instantly
6. **Future-Proof** - OpenAI improves → system improves

---

## 🎉 Result

**You have a fully AI-driven ad generation platform that:**
- ✅ Analyzes videos with Gemini
- ✅ Generates unique scenes with OpenAI
- ✅ Creates dynamic text/audio/visual
- ✅ Produces Sora 2 Pro videos
- ✅ **Zero hardcoding, 100% adaptive**

**Upload any ad → Get scroll-stopping variants automatically!** 🚀

