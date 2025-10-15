# Comprehensive Logging System

## Overview

The Ad Cloner now includes **comprehensive logging** of every step in the pipeline, including:

1. ✅ **Original video analysis** (detailed Gemini output)
2. ✅ **Vertical detection and transformation** (how the ad structure changes)
3. ✅ **All Sora prompts** (exact prompts sent to Sora API - FULL text)
4. ✅ **Generated video evaluation** (Gemini analysis + quality rating)
5. ✅ **Comparison report** (original vs generated)

---

## Files Generated Per Run

For each ad cloning session, you'll get these files in `output/analysis/`:

### 1. `analysis_TIMESTAMP.json`
**Contains**: Complete Gemini analysis of the **original input video**

```json
{
  "video_metadata": {
    "duration_seconds": 35,
    "aspect_ratio": "9:16"
  },
  "spokesperson": {
    "physical_description": "...",
    "speaking_style": "..."
  },
  "script": {
    "full_transcript": "I was paying $120 a month for car insurance...",
    "call_to_action": "..."
  },
  "scene_breakdown": [...],
  "storytelling": {...},
  "vertical": "auto_insurance",
  "vertical_name": "Auto Insurance",
  "transformed": true
}
```

### 2. `sora_prompts_analysis_TIMESTAMP.json`
**Contains**: **ALL Sora prompts** that were sent to the API for each variant

```json
{
  "aggressive": [
    {
      "scene_number": 1,
      "timestamp": "00:00-00:12",
      "purpose": "Hook - grab attention",
      "prompt": "[00:00-00:04] Medium Close-Up: Character: A female in her early to mid-20s with long, wavy, medium-brown hair...\n\n[FULL PROMPT TEXT HERE - hundreds of characters]\n\nCinematography: eye-level, smooth movement\nMood: professional, medium energy..."
    },
    {
      "scene_number": 2,
      "timestamp": "00:12-00:24",
      "purpose": "Show the problem/context visually",
      "prompt": "[00:00-00:04] Car driving smoothly on highway at sunset, aerial view tracking shot\n\n[FULL B-ROLL PROMPT HERE]..."
    }
  ]
}
```

### 3. `evaluation_VARIANT.json`
**Contains**: Evaluation report for each generated variant

```json
{
  "video_path": "output/videos/final_aggressive.mp4",
  "original_analysis": {...},
  "generated_analysis": {
    "script": {...},
    "spokesperson": {...},
    "storytelling": {...}
  },
  "comparison": {
    "original_vertical": "auto_insurance",
    "generated_vertical": "auto_insurance",
    "vertical_match": true,
    "original_scenes": 3,
    "generated_scenes": 3,
    "original_has_characters": true,
    "generated_has_characters": false
  },
  "ratings": {
    "visual_quality": 8.5,
    "message_clarity": 7.0,
    "pacing": 8.0,
    "storytelling": 7.5,
    "overall_score": 7.8,
    "predicted_performance": "GOOD - Should perform well"
  },
  "recommendations": [
    {
      "severity": "HIGH",
      "issue": "Content does not match original vertical",
      "details": "Expected auto_insurance content but generated video lacks key terms",
      "fix": "Strengthen vertical-specific keywords in B-roll prompts"
    }
  ]
}
```

### 4. `evaluation_VARIANT_summary.txt`
**Contains**: Human-readable summary

```
======================================================================
AD EVALUATION REPORT
======================================================================

RATINGS:
----------------------------------------------------------------------
Visual Quality: 8.5/10
Message Clarity: 7.0/10
Pacing: 8.0/10
Storytelling: 7.5/10

Overall Score: 7.8/10
Predicted Performance: GOOD - Should perform well

COMPARISON TO ORIGINAL:
----------------------------------------------------------------------
Original Vertical: auto_insurance
Generated Vertical: unknown
Vertical Match: ✗ NO
Scene Count: 5 → 3

RECOMMENDATIONS:
----------------------------------------------------------------------

1. [HIGH] Content does not match original vertical
   Details: Expected auto_insurance content but generated video lacks key terms
   Fix: Strengthen vertical-specific keywords in B-roll prompts
```

---

## Real-Time Logs (WebSocket)

During generation, the frontend shows real-time logs including:

### Analysis Stage
```
ℹ Starting Gemini video analysis
▸ Uploading video to Gemini File API
▸ Video analysis completed
▸ Detected 5 scenes in video
✓ Stage completed: analysis
```

### Transformation Stage
```
ℹ Detecting ad vertical and transforming structure
▸ Vertical detected: Auto Insurance
  {
    "vertical": "auto_insurance",
    "vertical_name": "Auto Insurance"
  }
▸ Scene 1: CHARACTER - spokesperson_hook
  {
    "scene": 1,
    "type": "spokesperson_hook",
    "has_character": true,
    "duration": 12
  }
▸ Scene 2: B-ROLL - problem_broll
  {
    "scene": 2,
    "type": "problem_broll",
    "has_character": false,
    "duration": 12,
    "broll_type": "driving",
    "visual_description": "Car driving smoothly on highway at sunset"
  }
```

### Prompts Stage
```
▸ Building prompts for Aggressive Variant
  Scene 1 prompt ready
  {
    "scene": 1,
    "timestamp": "00:00-00:12",
    "prompt_length": 957,
    "full_prompt": "[00:00-00:04] Medium Close-Up: Character: A female...",
    "scene_type": "spokesperson_hook",
    "has_character": true
  }

  Scene 2 prompt ready
  {
    "scene": 2,
    "timestamp": "00:12-00:24",
    "prompt_length": 543,
    "full_prompt": "[00:00-00:04] Car driving smoothly on highway...",
    "scene_type": "problem_broll",
    "has_character": false,
    "broll_type": "driving",
    "visual_description": "Car driving smoothly on highway at sunset, aerial view tracking shot"
  }
```

---

## Terminal Output

When running from terminal, you'll see:

```
======================================================================
AD CLONER PIPELINE
======================================================================
Input Video: output/videos/lastedit.mp4

[1/5] Analyzing video with Gemini 2.5...
✓ Analysis complete: output/analysis/analysis_20251012_203833.json

Spokesperson: A female in her early to mid-20s with long, wavy, medium-brown...

[1.5/5] Transforming ad structure for Sora...
✓ Detected vertical: Auto Insurance
✓ Transformed to Sora-friendly structure:
  - 1 character scene(s)
  - 2 B-roll scene(s)

[2/5] Generating aggression variants...
✓ Generated 1 variants
  - Aggressive Variant

[3/5] Building Sora prompts...
✓ Aggressive Variant: 3 scenes
✓ All prompts saved to: output/analysis/sora_prompts_analysis_20251012_203833.json

[4/5] Generating videos with Sora...
Total scenes to generate: 3

[5/5] Assembling final ads...
✓ AGGRESSIVE: output/videos/final_aggressive.mp4

[6/6] Evaluating generated ads...

▸ Evaluating aggressive variant...

======================================================================
EVALUATING GENERATED AD
======================================================================

▸ Analyzing generated video with Gemini...
✓ Generated video analyzed
  Overall Score: 7.8/10
  Prediction: GOOD - Should perform well

✓ Evaluation saved to: output/analysis/evaluation_aggressive.json
✓ Summary saved to: output/analysis/evaluation_aggressive_summary.txt

======================================================================
PIPELINE COMPLETE
======================================================================
Time elapsed: 18.5 minutes
Ads generated: 1

Final ads:
  AGGRESSIVE: output/videos/final_aggressive.mp4 (Score: 7.8/10)
```

---

## How to Debug Issues

### Issue: Generated video doesn't match vertical

1. **Check original analysis**:
   ```bash
   cat output/analysis/analysis_TIMESTAMP.json | grep -A 5 "vertical"
   ```

2. **Check Sora prompts**:
   ```bash
   cat output/analysis/sora_prompts_analysis_TIMESTAMP.json | jq '.aggressive[1].prompt' -r
   ```
   Look for Scene 2 (first B-roll scene) and verify it contains auto insurance imagery

3. **Check evaluation report**:
   ```bash
   cat output/analysis/evaluation_aggressive_summary.txt
   ```
   Look for "Vertical Match" - should be ✓ YES

### Issue: Character consistency problems

1. **Check transformation**:
   ```bash
   cat output/analysis/analysis_TIMESTAMP.json | jq '.scene_breakdown[] | {scene_number, has_character, type}'
   ```
   Should show only ONE scene with `"has_character": true`

2. **Check prompts**:
   ```bash
   cat output/analysis/sora_prompts_analysis_TIMESTAMP.json | jq '.aggressive[] | {scene_number, has_character: (.prompt | contains("Character:"))}'
   ```

### Issue: Sora not following prompts

1. **Check full prompt text**:
   ```bash
   cat output/analysis/sora_prompts_analysis_TIMESTAMP.json | jq '.aggressive[1].prompt' -r
   ```

2. **Compare to evaluation**:
   ```bash
   cat output/analysis/evaluation_aggressive.json | jq '.generated_analysis.script.full_transcript' -r
   ```

---

## Summary

✅ **Original Analysis**: `analysis_TIMESTAMP.json`
✅ **All Prompts**: `sora_prompts_analysis_TIMESTAMP.json`
✅ **Generated Analysis**: In `evaluation_VARIANT.json`
✅ **Quality Rating**: `evaluation_VARIANT_summary.txt`
✅ **Real-time Logs**: WebSocket + terminal output

**Everything is now logged in detail so you can debug exactly what went wrong!**
