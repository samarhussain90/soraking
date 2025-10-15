# Quick Start Guide

## System Ready ✓

All tests passed! Your Ad Cloner platform is fully operational.

## Usage

### 1. Quick Test (Analyze Only)

Test the Gemini analyzer without generating videos:

```bash
python cli.py dragon_video.mp4 --analyze-only
```

This will:
- Upload video to Gemini 2.5
- Extract complete breakdown
- Save analysis to `output/analysis/`
- Takes ~2-3 minutes
- No Sora credits used

### 2. Generate One Variant

Generate just one aggression level to test the full pipeline:

```bash
python cli.py dragon_video.mp4 --variants soft
```

This will:
- Analyze video
- Generate Soft variation (4 scenes)
- Assemble final ad
- Takes ~15-20 minutes
- Uses ~$1.50 in Sora credits

### 3. Full Pipeline (All 4 Variants)

Generate all 4 aggression variations:

```bash
python cli.py dragon_video.mp4
```

This will:
- Analyze video with Gemini
- Generate 4 variants in parallel:
  - Soft (calm, educational)
  - Medium (professional, balanced)
  - Aggressive (urgent, intense)
  - Ultra (confrontational, explosive)
- Assemble 4 complete ads
- Takes ~20-25 minutes
- Uses ~$6-11 in Sora credits

## Expected Output

After completion, check `output/` directory:

```
output/
├── analysis/
│   └── analysis_YYYYMMDD_HHMMSS.json    # Gemini breakdown
├── videos/
│   ├── soft/
│   │   ├── scene_01.mp4
│   │   ├── scene_02.mp4
│   │   ├── scene_03.mp4
│   │   ├── scene_04.mp4
│   │   └── final_soft.mp4               # Complete ad
│   ├── medium/
│   │   └── final_medium.mp4
│   ├── aggressive/
│   │   └── final_aggressive.mp4
│   └── ultra/
│       └── final_ultra.mp4
└── results.json                         # Summary
```

## What to Expect

### Stage 1: Analysis (2-3 min)
```
[1/5] Analyzing video with Gemini 2.5...
Uploading video: dragon_video.mp4
Upload complete: files/abc123
...
Video ready
Analyzing video with Gemini 2.5...
Analysis complete!
✓ Analysis complete: output/analysis/analysis_20250112_123456.json

Spokesperson: Male, early 30s, professional attire...
```

### Stage 2: Variants (instant)
```
[2/5] Generating aggression variants...
✓ Generated 4 variants
  - Soft/Consultative
  - Medium/Professional
  - Aggressive/Urgent
  - Ultra-Aggressive/Disruptive
```

### Stage 3: Prompts (instant)
```
[3/5] Building Sora prompts...
✓ Soft/Consultative: 4 scenes
✓ Medium/Professional: 4 scenes
✓ Aggressive/Urgent: 4 scenes
✓ Ultra-Aggressive/Disruptive: 4 scenes
```

### Stage 4: Generation (15-20 min)
```
[4/5] Generating videos with Sora...
Total scenes to generate: 16
This will take approximately 15-20 minutes...

======================================================================
GENERATING VARIANT: SOFT
Scenes: 4
======================================================================

Starting Scene 1...
✓ Job created: video_abc123
...
✓ All 4 jobs started. Monitoring progress...

--- Progress Update ---
Pending: 4 | Completed: 0
  Scene 1: 25% [in_progress]
  Scene 2: 10% [in_progress]
  Scene 3: 5% [queued]
  Scene 4: 0% [queued]
...
```

### Stage 5: Assembly (1-2 min)
```
[5/5] Assembling final ads...
Stitching 4 scenes...
✓ Stitched video: output/videos/final_soft.mp4
✓ SOFT: output/videos/final_soft.mp4
...
```

## Next Steps

### 1. Review Analysis

```bash
cat output/analysis/*.json | jq .
```

Look at:
- Spokesperson description (used for character consistency)
- Scene breakdown (how it's structured)
- Why it works (marketing insights)

### 2. Test Individual Modules

```bash
# Test Gemini analyzer
cd modules
python gemini_analyzer.py

# Test prompt builder
python sora_prompt_builder.py

# Test Sora client (generates 1 scene)
python sora_client.py
```

### 3. Deploy and Test

Upload all 4 variants to your ad platform (Meta, TikTok, etc.) and A/B test which aggression level performs best for your audience.

## Troubleshooting

### "Video processing failed"
- Check video format (MP4 recommended)
- Try smaller file (<100MB)
- Verify Gemini API quota

### "Job failed" during Sora generation
- Check OpenAI API quota
- Verify Sora access is enabled
- Try with fewer variants (`--variants soft`)

### "ffmpeg error"
```bash
# Reinstall ffmpeg
brew reinstall ffmpeg
```

### Out of memory
- Close other applications
- Use `--variants soft` to generate one at a time

## Cost Management

To minimize costs during testing:

1. **Start with --analyze-only** (free, just uses Gemini)
2. **Generate one variant** to test pipeline
3. **Full batch** once confident

Estimated costs:
- Analysis only: $0.05
- 1 variant (4 scenes): ~$1.50
- All 4 variants (16 scenes): ~$6-11

## Tips

1. **Use shorter ads** for testing (30-48s = 3-4 scenes)
2. **Test soft variant first** (usually best starting point)
3. **Keep original video** for comparison
4. **Save analysis JSON** to regenerate variants later without re-analyzing

## Ready to Go!

Try your first analysis:

```bash
python cli.py dragon_video.mp4 --analyze-only
```

This will show you exactly what Gemini extracts from the video without using any Sora credits.
