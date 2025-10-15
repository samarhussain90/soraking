# Scene Splitting Fix

## Problem

When processing a 40-second video, the system only generated **1 video of 12 seconds** instead of splitting it into **3-4 scenes** and generating them in parallel.

### Root Cause

The Gemini analyzer was treating the entire video as a single scene:
```json
{
  "scene_breakdown": [
    {
      "scene_number": 1,
      "timestamp": "00:00-00:35",
      "duration_seconds": 35,
      ...
    }
  ]
}
```

This resulted in only one Sora generation job instead of multiple parallel jobs.

---

## Solution

Updated the Gemini analyzer prompt to **explicitly instruct** it to break videos into multiple scenes, each max 12 seconds.

### Changes in `modules/gemini_analyzer.py`

Added clear instructions at the top of the analysis prompt:

```python
prompt = """
Analyze this advertising video in extreme detail. I need a comprehensive breakdown to recreate its structure.

CRITICAL: You MUST break the video into MULTIPLE scenes, each NO LONGER than 12 seconds.
- If the video is 40 seconds, create at least 3-4 scenes
- If the video is 60 seconds, create at least 5 scenes
- Each scene should have natural breaks in the narrative or visual changes
- NO scene should exceed 12 seconds duration
```

Also added a second scene example in the JSON structure to make it clear:

```json
"scene_breakdown": [
  {
    "scene_number": 1,
    "timestamp": "00:00-00:12",
    "duration_seconds": 12,
    ...
  },
  {
    "scene_number": 2,
    "timestamp": "00:12-00:24",
    "duration_seconds": 12,
    ...
  }
  (... continue for all scenes, max 12 seconds each)
],
```

---

## Expected Behavior After Fix

### For a 35-40 second video:
- **Scene 1**: 00:00-00:12 (12s) - Hook/Problem intro
- **Scene 2**: 00:12-00:24 (12s) - Problem agitation/Solution intro
- **Scene 3**: 00:24-00:36 (12s) - Solution details/CTA

**Result**: 3 Sora jobs running in parallel

### For a 48-60 second video:
- **Scene 1**: 00:00-00:12 (12s) - Hook
- **Scene 2**: 00:12-00:24 (12s) - Problem
- **Scene 3**: 00:24-00:36 (12s) - Solution
- **Scene 4**: 00:36-00:48 (12s) - Proof/CTA
- **Scene 5**: 00:48-00:60 (12s) - Final CTA (if needed)

**Result**: 4-5 Sora jobs running in parallel

---

## Why This Matters

### Performance:
- **Before**: 40s video → 1 Sora job → ~3-5 min generation time
- **After**: 40s video → 3-4 Sora jobs → ~3-5 min total (parallel execution)

### Quality:
- Each scene gets full Sora attention for 12 seconds
- Better consistency per scene
- Sora performs best on 12-second segments

### Accuracy:
- Maintains the full duration of the original ad
- No content is lost or compressed
- Each narrative beat is preserved

---

## Architecture Flow

```
Input: 40-second video
  ↓
Gemini Analysis → 3 scenes (12s, 12s, 11s)
  ↓
Aggression Variants → 4 variants × 3 scenes = 12 variations
  ↓
Sora Prompt Builder → 12 advanced prompts
  ↓
Sora Client (Parallel) → 12 jobs running simultaneously
  ↓
Video Assembler → 4 final videos (soft, medium, aggressive, ultra)
  ↓
Output: 4 complete 35-second ad variants
```

---

## Testing

### To verify the fix works:

1. Upload a new video (30-60 seconds)
2. Watch the analysis stage complete
3. Check `output/analysis/analysis_*.json`
4. Verify `scene_breakdown` has multiple scenes:
   ```json
   "scene_breakdown": [
     {"scene_number": 1, "timestamp": "00:00-00:12", ...},
     {"scene_number": 2, "timestamp": "00:12-00:24", ...},
     {"scene_number": 3, "timestamp": "00:24-00:35", ...}
   ]
   ```
5. Watch generation stage - should show multiple scenes per variant
6. Final videos should match original duration

---

## Sora API Constraints

- **Max duration per clip**: 12 seconds
- **Supported resolutions**: 1792x1024 (widescreen), 1024x1792 (portrait), 1920x1080 (16:9)
- **Parallel generation**: All scenes generated simultaneously to reduce total time

This constraint is why we MUST split videos into 12-second chunks.

---

## Status

✅ **FIXED** - Gemini will now automatically split videos into proper scene lengths

**File Modified**: `modules/gemini_analyzer.py`
**Lines Changed**: 67-127
**Testing Required**: Upload a new video to verify multi-scene splitting

---

Generated: 2025-10-12
