# Detailed Logging System

## Overview

Every pipeline run now generates **extremely detailed logs** to help identify exactly where errors occur. All logs are visible in:
1. **Terminal** (server console)
2. **Frontend UI** (live streaming)
3. **Log Files** (`output/logs/{session_id}/`)

---

## Log Levels

The system now has 7 log levels:

| Level | Emoji | Purpose | Example |
|-------|-------|---------|---------|
| **VERBOSE** | ▸ | Extra detailed step-by-step operations | "Uploading video to Gemini File API" |
| **DEBUG** | · | Low-level debugging info | "Parsing JSON response" |
| **INFO** | ℹ | Important status updates | "Starting Gemini video analysis" |
| **SUCCESS** | ✓ | Successful completion | "Analysis complete" |
| **PROGRESS** | → | Progress updates | "Scene 1: 50% [processing]" |
| **WARNING** | ⚠ | Non-critical issues | "Scene took longer than expected" |
| **ERROR** | ✗ | Critical failures | "Sora API request failed" |

---

## What Gets Logged

### Stage 1: Gemini Analysis (2-3 min)

**Start:**
```
ℹ Starting Gemini video analysis
  {
    "video_path": "/path/to/video.mp4"
  }

▸ Uploading video to Gemini File API
```

**During:**
```
▸ Video analysis completed
  {
    "analysis_path": "output/analysis/analysis_20251012_182746.json"
  }
```

**Completion:**
```
▸ Detected 3 scenes in video
  {
    "scenes": 3,
    "path": "output/analysis/analysis_20251012_182746.json",
    "duration": 35,
    "spokesperson_length": 387
  }

▸ Scene 1: 00:00-00:12 - Hook
  {
    "timestamp": "00:00-00:12",
    "duration": 12,
    "purpose": "Hook"
  }

▸ Scene 2: 00:12-00:24 - Problem agitation
  {
    "timestamp": "00:12-00:24",
    "duration": 12,
    "purpose": "Problem agitation"
  }

▸ Scene 3: 00:24-00:35 - Solution/CTA
  {
    "timestamp": "00:24-00:35",
    "duration": 11,
    "purpose": "Solution/CTA"
  }

✓ Stage completed: analysis
```

**If Error:**
```
✗ Gemini analysis failed: <error message>
  {
    "error": "Connection timeout",
    "error_type": "TimeoutError",
    "video_path": "/path/to/video.mp4"
  }
```

---

### Stage 2: Variant Generation (instant)

**Start:**
```
ℹ Stage started: variants

▸ Generating aggression level variations
  {
    "requested_variants": ["medium"]
  }
```

**During:**
```
▸ Filtered variants: 4 → 1
  {
    "requested": ["medium"],
    "generated": ["medium"]
  }

▸ Variant: Medium (Professional Balanced)
  {
    "level": "medium",
    "scenes": 3
  }
```

**Completion:**
```
✓ Stage completed: variants
  {
    "count": 1,
    "levels": ["medium"]
  }
```

---

### Stage 3: Prompt Building (instant)

**Start:**
```
ℹ Stage started: prompts

▸ Building advanced Sora prompts with timestamp segmentation
```

**During:**
```
▸ Building prompts for Medium (Professional Balanced)
  {
    "variant_level": "medium",
    "num_scenes": 3
  }

▸ Scene 1 prompt ready
  {
    "scene": 1,
    "timestamp": "00:00-00:12",
    "prompt_length": 847,
    "preview": "[00:00-00:04] Medium shot: Character: A female in her early-to-mid 20s..."
  }

▸ Scene 2 prompt ready
  {
    "scene": 2,
    "timestamp": "00:12-00:24",
    "prompt_length": 823,
    "preview": "[00:12-00:16] Close-up: Character continues direct address..."
  }

▸ Scene 3 prompt ready
  {
    "scene": 3,
    "timestamp": "00:24-00:35",
    "prompt_length": 791,
    "preview": "[00:24-00:28] Medium close-up: Final call to action..."
  }
```

**Completion:**
```
✓ Stage completed: prompts
  {
    "total_scenes": 3,
    "variants": ["medium"]
  }
```

---

### Stage 4: Sora Generation (3-5 min) - MOST DETAILED

**Start:**
```
ℹ Stage started: generation
  total_items: 3

ℹ Starting Sora generation: 3 scenes across 1 variants
  {
    "total_scenes": 3,
    "variants": ["medium"]
  }

▸ Starting medium variant generation
  {
    "variant": "medium",
    "scenes": 3,
    "method": "parallel"
  }
```

**For Each Scene:**
```
Creating video job... (sora-2-pro, 1792x1024, 12s)
▸ API URL: https://api.openai.com/v1/videos
▸ Prompt length: 847 characters
▸ Sending POST request to Sora API...
▸ Response status code: 200
▸ Response data keys: ['id', 'status', 'model', 'size', 'seconds', 'progress']
✓ Job created: video_abc123xyz
```

**If API Error:**
```
✗ API Error: 400
▸ Response body: {"error": {"message": "Invalid prompt format", "type": "invalid_request_error"}}

✗ Sora API request failed: 400 Bad Request
▸ Error type: HTTPError
▸ Response status: 400
▸ Response body: {"error": {"message": "Invalid prompt format"}}
```

**Completion:**
```
▸ Variant medium generation completed
  {
    "variant": "medium",
    "success": true,
    "scenes_completed": 3
  }

✓ Stage completed: generation
  {
    "total_variants": 1,
    "successful": 1,
    "failed": 0
  }
```

---

### Stage 5: Assembly (10-20s)

**Start:**
```
ℹ Stage started: assembly
```

**During:**
```
▸ Stitching scenes for medium variant
▸ Using ffmpeg to combine 3 clips
▸ Output path: output/videos/medium/final_medium.mp4
```

**Completion:**
```
✓ Stage completed: assembly
  {
    "videos": 1
  }
```

---

## Error Tracking

Every error includes:
- **Error message**: What went wrong
- **Error type**: Exception class name
- **Context**: What was being processed
- **Timestamp**: When it happened
- **Full traceback**: (in log files)

### Example Error Log:

```
✗ Sora generation failed for medium: 401 Unauthorized
  {
    "variant": "medium",
    "error": "401 Unauthorized",
    "error_type": "HTTPError"
  }

✗ API Error: 401
▸ Response body: {"error": {"message": "Invalid API key", "type": "invalid_request_error"}}

✗ Sora API request failed: 401 Client Error: Unauthorized
▸ Error type: HTTPError
▸ Response status: 401
▸ Response body: {"error": {"message": "Invalid API key provided", "type": "invalid_request_error", "code": "invalid_api_key"}}
```

From this log, you can immediately see:
1. ✅ The stage that failed: **Generation**
2. ✅ The variant being processed: **medium**
3. ✅ The exact error: **401 Unauthorized**
4. ✅ The root cause: **Invalid API key**
5. ✅ The error type: **HTTPError**

---

## Log File Locations

Every session creates 3 log files in `output/logs/{session_id}/`:

### 1. `pipeline.log` (Text Format)
Human-readable log with timestamps:
```
2025-10-12 19:20:45 | INFO     | Starting Gemini video analysis | {"video_path": "/path/to/video.mp4"}
2025-10-12 19:20:46 | VERBOSE  | Uploading video to Gemini File API | {}
2025-10-12 19:23:12 | VERBOSE  | Video analysis completed | {"analysis_path": "..."}
...
```

### 2. `progress.json` (State Tracking)
Current pipeline state:
```json
{
  "session_id": "session_1760308013",
  "started_at": "2025-10-12T19:20:45",
  "status": "in_progress",
  "current_stage": "generation",
  "stages": {
    "analysis": {"status": "completed", "progress": 100},
    "variants": {"status": "completed", "progress": 100},
    "prompts": {"status": "completed", "progress": 100},
    "generation": {"status": "in_progress", "progress": 66},
    "assembly": {"status": "pending", "progress": 0}
  },
  "variants": {
    "medium": {
      "status": "generating",
      "scenes": {
        "scene_1": {"status": "completed", "job_id": "video_abc"},
        "scene_2": {"status": "completed", "job_id": "video_def"},
        "scene_3": {"status": "in_progress", "progress": 75}
      }
    }
  },
  "errors": []
}
```

### 3. `events.json` (Complete Event Log)
Every single event with full data:
```json
[
  {
    "timestamp": "2025-10-12T19:20:45.123",
    "level": "INFO",
    "message": "Starting Gemini video analysis",
    "data": {"video_path": "/path/to/video.mp4"}
  },
  {
    "timestamp": "2025-10-12T19:20:46.456",
    "level": "VERBOSE",
    "message": "Uploading video to Gemini File API",
    "data": {}
  },
  ...
]
```

---

## How to Debug With Logs

### Example: Sora API Failure

**Terminal shows:**
```
✗ Sora API request failed: 400 Bad Request
▸ Response status: 400
▸ Response body: {"error": {"message": "Prompt exceeds 2000 characters"}}
```

**Immediate fix:**
1. Open `output/logs/{session_id}/events.json`
2. Search for "Scene X prompt ready"
3. Check `"prompt_length"` field
4. If >2000, need to shorten prompts in `sora_prompt_builder.py`

---

### Example: Gemini Analysis Stuck

**Terminal shows:**
```
ℹ Starting Gemini video analysis
▸ Uploading video to Gemini File API
... (nothing for 5+ minutes)
```

**Debugging steps:**
1. Check `progress.json` → `stages.analysis.status` = "in_progress"
2. Check `events.json` → Last event was "Uploading video"
3. **Conclusion**: Video upload is taking too long
4. **Fix**: Check file size, network connection, or Gemini API quota

---

### Example: Assembly Fails

**Terminal shows:**
```
✗ Failed to assemble medium: ffmpeg not found
```

**Immediate fix:**
```bash
# Install ffmpeg
brew install ffmpeg  # macOS
apt-get install ffmpeg  # Linux
```

---

## Frontend Display

All logs are visible in the **Live Logs** section of the frontend:

```
▸ Uploading video to Gemini File API
▸ Video analysis completed
  {
    "analysis_path": "output/analysis/..."
  }
▸ Detected 3 scenes in video
  {
    "scenes": 3,
    "duration": 35
  }
▸ Scene 1: 00:00-00:12 - Hook
▸ Scene 2: 00:12-00:24 - Problem
▸ Scene 3: 00:24-00:35 - Solution
✓ Stage completed: analysis
```

The logs scroll automatically and are color-coded:
- 🟦 VERBOSE/DEBUG - Blue
- ⚪ INFO - White
- 🟢 SUCCESS - Green
- 🟡 WARNING - Yellow
- 🔴 ERROR - Red

---

## Benefits

### 1. **Instant Error Identification**
See exactly where the pipeline failed, not just "something went wrong"

### 2. **API Debugging**
Full request/response details for every Sora API call

### 3. **Performance Tracking**
See how long each stage takes:
```
Analysis: 2m 45s
Variants: 0.1s
Prompts: 0.2s
Generation: 4m 23s
Assembly: 18s
TOTAL: 7m 26s
```

### 4. **Reproducibility**
Can replay exactly what happened by reading event logs

### 5. **Remote Monitoring**
Check progress from anywhere via `progress.json` API endpoint

---

## Example Full Run Log

```
═══════════════════════════════════════════════════════════════════
AD CLONER PIPELINE
═══════════════════════════════════════════════════════════════════

[1/5] Analyzing video with Gemini 2.5...
ℹ Starting Gemini video analysis
▸ Uploading video to Gemini File API
▸ Video analysis completed
▸ Detected 3 scenes in video
▸ Scene 1: 00:00-00:12 - Hook
▸ Scene 2: 00:12-00:24 - Problem agitation
▸ Scene 3: 00:24-00:35 - Solution/CTA
✓ Stage completed: analysis

[2/5] Generating aggression variants...
ℹ Stage started: variants
▸ Generating aggression level variations
▸ Filtered variants: 4 → 1
▸ Variant: Medium (Professional Balanced)
✓ Stage completed: variants

[3/5] Building Sora prompts...
ℹ Stage started: prompts
▸ Building advanced Sora prompts
▸ Building prompts for Medium
▸ Scene 1 prompt ready (847 chars)
▸ Scene 2 prompt ready (823 chars)
▸ Scene 3 prompt ready (791 chars)
✓ Stage completed: prompts

[4/5] Generating videos with Sora...
ℹ Starting Sora generation: 3 scenes
▸ Starting medium variant generation
▸ API URL: https://api.openai.com/v1/videos
▸ Sending POST request (Scene 1)...
✓ Job created: video_abc123
▸ Sending POST request (Scene 2)...
✓ Job created: video_def456
▸ Sending POST request (Scene 3)...
✓ Job created: video_ghi789
→ Scene 1: 25% [processing]
→ Scene 2: 30% [processing]
→ Scene 3: 20% [processing]
...
✓ Scene 1: completed
✓ Scene 2: completed
✓ Scene 3: completed
✓ Stage completed: generation

[5/5] Assembling final ads...
ℹ Stage started: assembly
▸ Stitching 3 scenes
✓ Stage completed: assembly

═══════════════════════════════════════════════════════════════════
PIPELINE COMPLETE
Time elapsed: 7.4 minutes
Ads generated: 1
═══════════════════════════════════════════════════════════════════
```

---

## Status: ✅ ENABLED

Detailed logging is now active on the server.

**Test it**: Upload a video and watch the logs stream in real-time! 📊

---

Generated: 2025-10-12
