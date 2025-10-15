# Detailed Logs Frontend Feature

## Overview

The frontend now includes a **"Detailed Logs" button** that shows comprehensive information about every step of the pipeline in an expandable, easy-to-read format.

---

## What You'll See

### 🔍 Detailed Logs Panel

Located below the "Live Logs" section, this panel contains 4 collapsible sections:

### 1. 📊 **Original Video Analysis**
Shows the complete Gemini analysis of your input video in JSON format:

```json
{
  "video_metadata": {
    "duration_seconds": 35,
    "aspect_ratio": "9:16"
  },
  "spokesperson": {
    "physical_description": "A female in her early to mid-20s...",
    "speaking_style": "Highly energetic, enthusiastic..."
  },
  "script": {
    "full_transcript": "I was paying $120 a month for car insurance...",
    "call_to_action": "Click the link below..."
  },
  "scene_breakdown": [...],
  "storytelling": {...},
  "vertical": "auto_insurance",
  "vertical_name": "Auto Insurance"
}
```

### 2. 🔄 **Ad Transformation**
Shows how your ad was transformed for Sora:

```
Detected Vertical: Auto Insurance

Scene Structure:
- Character scenes: 1
- B-roll scenes: 2

Transformed Scenes:
[
  {
    "scene_number": 1,
    "type": "spokesperson_hook",
    "has_character": true,
    "duration_seconds": 12
  },
  {
    "scene_number": 2,
    "type": "problem_broll",
    "has_character": false,
    "broll_type": "driving",
    "visual_description": "Car driving smoothly on highway..."
  }
]
```

### 3. ✍️ **Sora Prompts (Full Text)**
Shows **EVERY SINGLE WORD** that was sent to the Sora API:

```
======================================================================
VARIANT: MEDIUM
======================================================================

--- Scene 1 ---
Timestamp: 00:00-00:12
Purpose: Hook - grab attention with relatable problem

FULL PROMPT:
[00:00-00:04] Medium Close-Up: Character: A female in her early to mid-20s
with long, wavy, medium-brown hair parted slightly off-center. Her facial
features are symmetrical with large, expressive dark brown eyes...

[COMPLETE 957-CHARACTER PROMPT HERE]

Cinematography: eye-level, smooth movement
Mood: professional, medium energy
...


--- Scene 2 ---
Timestamp: 00:12-00:24
Purpose: Show the problem/context visually

FULL PROMPT:
[00:00-00:04] Car driving smoothly on highway at sunset, aerial view
tracking shot

IMPORTANT: This is B-roll footage. NO people, NO faces, NO characters
should appear in this scene. Only objects, environments, and abstract
visuals related to the topic.

[COMPLETE B-ROLL PROMPT HERE]
...
```

### 4. ⭐ **Final Evaluation & Rating**
Shows Gemini's analysis of the **generated video** with quality scores:

```
OVERALL SCORE: 7.8/10
PREDICTION: GOOD - Should perform well

RATINGS:
- Visual Quality: 8.5/10
- Message Clarity: 7.0/10
- Pacing: 8.0/10
- Storytelling: 7.5/10

COMPARISON:
- Original Vertical: auto_insurance
- Generated Vertical: unknown
- Vertical Match: ✗ NO
- Scene Count: 5 → 3

RECOMMENDATIONS:

1. [HIGH] Content does not match original vertical
   Details: Expected auto_insurance content but generated video lacks key terms
   Fix: Strengthen vertical-specific keywords in B-roll prompts

2. [MEDIUM] Pacing too slow
   Details: Slow pacing may lose viewer attention
   Fix: Use 'aggressive' or 'ultra' variant for faster pacing
```

---

## How to Use

1. **Upload your video** and start cloning
2. **Wait for completion** (the panel appears automatically)
3. **Click "Show Details ▼"** button to expand the panel
4. **Click any section header** to expand/collapse that section
5. **Scroll through** to see all the data

### Button Location

The button appears in the **🔍 Detailed Logs** card header, right-aligned.

---

## What This Helps You Debug

### Problem: Generated video doesn't match vertical

**Step 1**: Check **Original Video Analysis** section
- Look for `"vertical": "auto_insurance"`
- Verify it detected the right vertical

**Step 2**: Check **Sora Prompts** section
- Look at Scene 2 (first B-roll scene)
- Verify it contains auto insurance imagery (e.g., "Car driving on highway")
- Check if the prompt says "NO people, NO faces"

**Step 3**: Check **Final Evaluation** section
- Look at "Vertical Match" - should be ✓ YES
- Read recommendations for specific fixes

### Problem: Character consistency issues

**Step 1**: Check **Ad Transformation** section
- Should show "Character scenes: 1"
- Should show "B-roll scenes: 2 or 3"

**Step 2**: Check **Sora Prompts** section
- Scene 1 should have character description
- Scenes 2-4 should say "NO people, NO faces, NO characters"

### Problem: Sora not following prompts

**Step 1**: Copy the **FULL PROMPT** from **Sora Prompts** section

**Step 2**: Compare to **Final Evaluation** section
- Check "Generated Vertical"
- Read "Generated Analysis" for what Sora actually created

**Step 3**: Adjust prompts if needed based on recommendations

---

## API Endpoint

The detailed logs are fetched from:

```
GET /api/sessions/{session_id}/detailed
```

Returns:
```json
{
  "analysis": { /* Full Gemini analysis */ },
  "transformation": { /* Transformation details */ },
  "prompts": { /* All Sora prompts with full text */ },
  "evaluation": { /* Final evaluation and ratings */ }
}
```

---

## Files Created

The detailed logs pull data from these files:

- `output/analysis/analysis_TIMESTAMP.json` - Original analysis
- `output/analysis/sora_prompts_analysis_TIMESTAMP.json` - All prompts
- `output/analysis/evaluation_VARIANT.json` - Evaluation report

You can also view these files directly on disk!

---

## Summary

✅ **"Show Details" button** in frontend
✅ **4 expandable sections** with all data
✅ **Full Sora prompts** with every character
✅ **Quality ratings** and recommendations
✅ **Auto-loads** when pipeline completes
✅ **Easy to read** formatted JSON and text

**Now you can see EXACTLY what's happening at every step!** 🎬
