# 🚀 Quick Start Guide - Sora Native Dynamic Ads

## ⚡ Get Started in 3 Steps

### Step 1: Start the Server
```bash
cd /Users/samarm3/soraking
python server.py
```

### Step 2: Open Your Browser
```
http://localhost:3000
```

### Step 3: Upload & Generate
1. Upload your winning ad video
2. Select variants (or generate all 4)
3. Click "Clone Ad"
4. Watch the magic happen! ✨

---

## 🎯 What You Get

Each ad will have:
- ✅ **Synchronized Audio** (voiceover + music + SFX)
- ✅ **Bold Text Overlays** (prices, hooks, CTAs)
- ✅ **Dynamic Camera** (whip pans, crash zooms, push-ins)
- ✅ **Beat Drops** (synced with key moments)
- ✅ **Professional Polish** (4K, cinematic color grade)

All generated natively by **Sora 2 Pro** - no editing needed!

---

## 📊 Example Output

### Scene Structure (12 seconds):
```
0:00-0:03  EXTREME CLOSE-UP → "$120/MONTH" text crashes in
0:03-0:06  WHIP PAN to speaker → Music starts → Voiceover begins
0:06-0:09  PUSH-IN on speaker → "$39/MONTH" MASSIVE reveal → Cash register SFX
0:09-0:12  FINAL HOLD → "TAP BELOW" CTA fades in → Bass drop
```

### Prompt Features:
- **Visual:** 4-shot progression with dynamic camera
- **Audio:** Complete mix with voiceover, music (140 BPM), SFX
- **Text:** 2-3 overlays per scene, 80-240pt fonts
- **Technical:** 4K, 1792x1024, cinematic audio mix

---

## 🎨 Vertical Styles

### Auto Insurance (Fast & Urgent)
- **Text:** Red/yellow, 240pt prices
- **Camera:** Fast whip pans, crash zooms
- **Audio:** 140-160 BPM electronic, cash register SFX
- **Energy:** High-intensity, explosive

### Health Insurance (Warm & Trustworthy)
- **Text:** Blue/green, softer animations
- **Camera:** Smooth push-ins, steady shots
- **Audio:** 75-95 BPM acoustic, gentle chimes
- **Energy:** Calm, reassuring

### Finance (Professional & Bold)
- **Text:** Gold/navy, sleek slides
- **Camera:** Dramatic zooms, reveals
- **Audio:** 105-145 BPM sophisticated electronic
- **Energy:** Confident, commanding

---

## 📈 Aggression Levels

| Level | BPM | Camera | Text | Vibe |
|-------|-----|---------|------|------|
| **Soft** | 90 | Slow push-ins | Gentle fades | Friendly |
| **Medium** | 120 | Steady dolly | Moderate pops | Engaging |
| **Aggressive** | 140 | Dynamic whips | Bold crashes | Urgent |
| **Ultra** | 160 | Crash zooms | Explosive reveals | Intense |

---

## 🔍 Where to Find Output

### Prompts (JSON):
```
output/analysis/sora_prompts_analysis_*.json
```

### Scene Videos:
```
output/videos/[variant]/scene_01.mp4
output/videos/[variant]/scene_02.mp4
...
```

### Final Assembled Ads:
```
output/videos/final_soft.mp4
output/videos/final_medium.mp4
output/videos/final_aggressive.mp4
output/videos/final_ultra.mp4
```

---

## 🧪 Test Before Production

### Quick Test:
```bash
python test_sora_composer.py
```
Should show prompts with audio + text + camera specs.

### Full Pipeline Test:
```bash
python test_setup.py
```
Validates all systems.

---

## 💡 Pro Tips

1. **Let it analyze first** - Gemini takes 30-60s to analyze
2. **Choose your vertical** - Auto/Health/Finance get custom styles
3. **Start with Medium** - Best balance of energy and polish
4. **Review prompts** - Check JSON output before generating
5. **Sora 2 Pro** - Higher quality, better character consistency

---

## 🆘 Troubleshooting

### Port Already in Use:
```bash
pkill -f "python server.py"
python server.py
```

### Missing API Keys:
Check `.env` file has:
```
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

### Validation Errors:
Check `output/logs/session_*/pipeline.log` for details

---

## 📚 Documentation

- **Full Details:** `FINAL_IMPLEMENTATION_REPORT.md`
- **Implementation:** `IMPLEMENTATION_SUMMARY.md`
- **This Guide:** `QUICK_START_GUIDE.md`

---

## 🎉 You're Ready!

Your ad cloner now generates **professional, high-converting ads** with:
- Big bold text overlays
- Synchronized audio and music
- Dynamic camera movements
- Beat drops and effects

**All powered by Sora 2 Pro's advanced prompting!** 🚀

