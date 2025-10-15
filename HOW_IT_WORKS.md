# How the Ad Cloner Works - Step by Step

## Complete Pipeline Walkthrough

This guide explains every step of the ad cloning process, from video upload to final output.

---

## 📋 Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Step-by-Step Pipeline](#step-by-step-pipeline)
3. [Frontend Flow](#frontend-flow)
4. [Backend Processing](#backend-processing)
5. [File System & Data Flow](#file-system--data-flow)
6. [Real-Time Updates](#real-time-updates)
7. [Detailed Logs System](#detailed-logs-system)

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      USER BROWSER                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Frontend (index.html + app.js)            │  │
│  │  • Upload interface                                  │  │
│  │  • Cost estimator                                    │  │
│  │  • Progress tracking                                 │  │
│  │  • Detailed logs viewer                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↕ ↕ ↕
              (HTTP/REST API + WebSocket)
                           ↕ ↕ ↕
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND SERVER (server.py)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Flask API          │  WebSocket (SocketIO)          │  │
│  │  • /api/upload      │  • Real-time progress         │  │
│  │  • /api/clone       │  • Live logs streaming        │  │
│  │  • /api/sessions    │  • Pipeline events            │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              AD CLONER PIPELINE                      │  │
│  │                                                       │  │
│  │  1. VideoAnalyzer (Gemini) → Analyze input          │  │
│  │  2. SoraTransformer → Transform to Sora structure   │  │
│  │  3. SoraPromptBuilder → Build prompts               │  │
│  │  4. SoraGenerator (OpenAI) → Generate videos        │  │
│  │  5. VideoAssembler (ffmpeg) → Stitch scenes         │  │
│  │  6. AdEvaluator (Gemini) → Rate output             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                     OUTPUT FILES                            │
│  • output/videos/                                           │
│  • output/analysis/                                         │
│  • output/logs/                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Pipeline

### **STEP 1: Video Upload** 📹

**What Happens:**
1. User opens `http://localhost:3000` in browser
2. User either:
   - Enters a video path: `/path/to/video.mp4`
   - OR uploads a file via drag-and-drop/click

**Frontend Process (`frontend/app.js:uploadFile()`):**
```javascript
1. Validate file type (MP4, MOV, AVI, MKV, WEBM)
2. Validate file size (<500MB)
3. Create FormData with video file
4. Send to: POST /api/upload
5. Track upload progress with XHR
6. Update progress bar in real-time
7. Receive response with file path
```

**Backend Process (`server.py:upload_video()`):**
```python
1. Receive file from request
2. Secure filename (prevent path traversal)
3. Add timestamp to avoid conflicts
4. Save to: output/uploads/filename_TIMESTAMP.ext
5. Return file path to frontend
```

**Result:**
- File saved at: `output/uploads/video_1729123456.mp4`
- Path displayed in input field

---

### **STEP 2: Variant Selection & Cost Estimation** 💰

**What Happens:**
User selects variants (checkboxes):
- ☐ Soft (calm energy)
- ☑ Medium (balanced) ← default
- ☐ Aggressive (urgent)
- ☐ Ultra (explosive)

**Cost Calculation (`frontend/app.js:updateCostEstimate()`):**
```javascript
// Example: 1 variant selected (medium)
const SORA_2_COST_PER_SECOND = 0.064;
const SECONDS_PER_SCENE = 12;
const SCENES_PER_VARIANT = 4; // Will be 3 or 4 dynamically

numVariants = 1
totalScenes = 1 × 4 = 4
totalSeconds = 4 × 12 = 48
totalCost = 48 × $0.064 = $3.07

Display: "1 variant × 4 scenes × 12s × $0.064/s = $3.07"
```

**Result:**
- Cost estimate updates in real-time
- Shows "Using Sora 2 (regular) • 80% cheaper than Pro"

---

### **STEP 3: Start Cloning** 🚀

**What Happens:**
User clicks "Start Cloning" button

**Frontend Process (`frontend/app.js:startCloning()`):**
```javascript
1. Get video path from input
2. Get selected variants from checkboxes
3. Disable "Start Cloning" button
4. Send request:
   POST /api/clone
   {
     "video_path": "/path/to/video.mp4",
     "variants": ["medium"]
   }
5. Receive session_id from response
6. Subscribe to WebSocket for real-time updates:
   socket.emit('subscribe', { session_id: 'xxx' })
7. Start polling for progress every 2 seconds
8. Show progress sections
```

**Backend Process (`server.py:start_clone()`):**
```python
1. Receive video_path and variants
2. Create PipelineLogger with unique session_id
3. Create WebSocket-enabled logger for real-time broadcast
4. Store session in active_sessions dict
5. Start pipeline in background thread:
   Thread(target=run_pipeline).start()
6. Return session_id to frontend
```

**Result:**
- Session created with ID: `session_20251012_210000`
- Pipeline starts running in background
- Frontend shows progress sections

---

### **STEP 4: Pipeline Execution** ⚙️

The pipeline runs through 6 stages in a background thread:

---

#### **STAGE 1: Video Analysis** 🔍

**File:** `ad_cloner.py:clone_ad()` → `modules/video_analyzer.py`

**Process:**
```python
1. Upload video to Gemini File API
2. Wait for file processing (~30 seconds)
3. Send analysis prompt to Gemini 2.5 Pro:
   "Analyze this ad video and extract:
    - Spokesperson description
    - Script/transcript
    - Scene breakdown
    - Storytelling structure
    - Vertical (auto_insurance, health_insurance, etc.)"
4. Parse JSON response
5. Save to: output/analysis/analysis_TIMESTAMP.json
```

**Gemini's Output:**
```json
{
  "video_metadata": {
    "duration_seconds": 35,
    "aspect_ratio": "9:16"
  },
  "spokesperson": {
    "physical_description": "Female, early 20s, long brown hair...",
    "speaking_style": "Energetic, enthusiastic..."
  },
  "script": {
    "full_transcript": "I was paying $120 a month...",
    "call_to_action": "Click the link below"
  },
  "scene_breakdown": [
    {
      "scene_number": 1,
      "timestamp": "00:00-00:06",
      "shot_type": "Medium Close-Up",
      "characters": "Spokesperson",
      "message": "Problem statement - high insurance cost"
    }
  ],
  "vertical": "auto_insurance",
  "vertical_name": "Auto Insurance"
}
```

**WebSocket Broadcast:**
```javascript
// Frontend receives:
{
  "event": {
    "level": "info",
    "message": "✓ Video analyzed successfully",
    "data": { "vertical": "auto_insurance" }
  }
}
```

**Files Created:**
- `output/analysis/analysis_20251012_210000.json`

---

#### **STAGE 2: Generate Variants** 🎨

**File:** `modules/sora_transformer.py`

**Process:**
```python
1. Determine scene count based on video duration:
   - If duration < 40s: 3 scenes (36s total)
   - If duration >= 40s: 4 scenes (48s total)

2. For each variant (soft, medium, aggressive, ultra):
   a. Get aggression modifiers:
      - Lighting: soft/natural/dramatic/intense
      - Pacing: slow/steady/fast/rapid
      - Camera movement: gentle/smooth/dynamic/explosive
      - Emotion keywords: calm/engaging/urgent/explosive

   b. Transform scenes:
      Scene 1 (12s): Spokesperson HOOK
        - has_character: true
        - type: "spokesperson_hook"
        - Keep original character description

      Scene 2 (12s): B-roll PROBLEM/CONTEXT
        - has_character: false
        - type: "problem_broll"
        - broll_type: Based on vertical (e.g., "driving" for auto insurance)
        - visual_description: Problem visualization

      Scene 3 (12s): B-roll SOLUTION
        - has_character: false
        - type: "solution_broll"
        - broll_type: Based on vertical
        - visual_description: Solution visualization

      Scene 4 (12s): B-roll CTA (if 4 scenes)
        - has_character: false
        - type: "cta_broll"
        - broll_type: Based on vertical
        - visual_description: Call to action
```

**Example Transformation:**
```json
{
  "variant_name": "medium",
  "variant_level": "medium",
  "modified_scenes": [
    {
      "scene_number": 1,
      "timestamp": "00:00-00:12",
      "has_character": true,
      "type": "spokesperson_hook",
      "shot_type": "Medium Close-Up",
      "characters": "Spokesperson",
      "message": "Hook - grab attention with problem"
    },
    {
      "scene_number": 2,
      "timestamp": "00:12-00:24",
      "has_character": false,
      "type": "problem_broll",
      "broll_type": "driving",
      "visual_description": "Car driving on highway, showing typical insurance scenario"
    }
  ],
  "aggression_modifiers": {
    "lighting": "natural lighting",
    "pacing": "steady pace",
    "camera_movement": "smooth movement",
    "energy_level": "medium",
    "emotion_keywords": ["engaging", "relatable"]
  }
}
```

**Result:**
- 1-4 variant structures created
- Each variant saved to memory for next stage

---

#### **STAGE 3: Build Sora Prompts** ✍️

**File:** `modules/sora_prompt_builder.py`

**Process:**
```python
For each scene in each variant:

IF scene has_character == true:
  1. Divide 12s into 3 segments (4s each)
  2. Build character prompt:

     Segment 1 (00:00-00:04):
       - Shot type + character description
       - Setting and emotion
       - Camera movement starts

     Segment 2 (00:04-00:08):
       - Scene evolution (gradual/transforms/morphs)
       - Camera continues movement
       - Visual elements emphasized

     Segment 3 (00:08-00:12):
       - Emotional peak
       - Camera reaches final position
       - Scene resolves with impact

     Technical Specs:
       - Cinematography details
       - Motion verbs based on aggression
       - Lighting and audio specs

ELSE (B-roll scene):
  1. Divide 12s into 3 segments
  2. Build B-roll prompt with STRONG emphasis:

     [00:00-00:04] {visual_description}

     IMPORTANT: This is B-roll footage. NO people, NO faces,
     NO characters should appear in this scene. Only objects,
     environments, and abstract visuals related to the topic.

     [00:04-00:08] Camera {motion_verb}, revealing more details.
     Continue showing ONLY the environment and objects. NO people visible.

     [00:08-00:12] Final composition achieved.
     Still NO people - maintain focus on objects, settings, and
     visual metaphors related to {broll_type}.

     Content: Pure B-roll - NO PEOPLE, NO FACES, NO CHARACTERS at all
```

**Example Prompt (Character Scene):**
```
[00:00-00:04] Medium Close-Up: Character: A female in her early to mid-20s
with long, wavy, medium-brown hair parted slightly off-center. Her facial
features are symmetrical with large, expressive dark brown eyes, well-defined
eyebrows, a straight nose, and full lips with a natural pink tone. She has
a warm, olive skin tone...

natural lighting. Emotion: concerned. Camera moves slowly, establishing the scene.
I was paying $120 a month for car insurance

[00:04-00:08] The scene transforms into as camera shifts.
steady pace. Visual elements emphasize the transformation.
Expressing frustration about high costs

[00:08-00:12] Emotional peak: engaging, relatable.
Camera moves to final composition. Scene resolves with clear impact.
I was paying $120 a month for car insurance

Cinematography: eye-level, smooth movement
Mood: professional, medium energy
Motion: moves, shifts, pans
Lighting: natural lighting
Audio: ambient sounds, clear voiceover
```

**Example Prompt (B-roll Scene):**
```
[00:00-00:04] Car driving smoothly on highway at sunset, aerial view tracking shot

IMPORTANT: This is B-roll footage. NO people, NO faces, NO characters should
appear in this scene. Only objects, environments, and abstract visuals related
to the topic.

[00:04-00:08] Camera moves, revealing more details. steady, professional camera work.
Mood: professional. Visual storytelling continues with moderate, engaging pacing.

Continue showing ONLY the environment and objects. NO people visible.

[00:08-00:12] Final composition achieved. Scene resolves with clear visual impact.

Still NO people - maintain focus on objects, settings, and visual metaphors
related to driving.

Cinematography: Cinematic, high production value, professional
Camera: steady, professional camera work
Pacing: moderate, engaging pacing
Mood: professional
Lighting: Professional, dramatic where appropriate
Quality: 4K, sharp focus, no blur
Style: Commercial/advertising quality
Content: Pure B-roll - NO PEOPLE, NO FACES, NO CHARACTERS at all
```

**Save All Prompts:**
```python
# Save to file for debugging
prompts_file = "output/analysis/sora_prompts_analysis_20251012_210000.json"
data = {
  "medium": [
    {
      "scene_number": 1,
      "timestamp": "00:00-00:12",
      "purpose": "Hook - grab attention",
      "prompt": "... FULL PROMPT TEXT ..."
    }
  ]
}
json.dump(data, file)
```

**Files Created:**
- `output/analysis/sora_prompts_analysis_20251012_210000.json`

---

#### **STAGE 4: Generate Videos with Sora** 🎬

**File:** `modules/sora_generator.py`

**Process:**
```python
For each variant:
  For each scene:
    1. Format prompt for Sora API:
       {
         "model": "sora-2",
         "prompt": "... full prompt text ...",
         "size": "1280x720",
         "seconds": "12"
       }

    2. Send to OpenAI Sora API:
       POST https://api.openai.com/v1/videos

    3. Receive video_id in response:
       {
         "id": "video_68ec0af621f08191...",
         "status": "queued"
       }

    4. Poll for completion (check every 10s):
       GET https://api.openai.com/v1/videos/{video_id}

       Status progression:
       queued → processing → completed

    5. When completed, download video:
       GET https://api.openai.com/v1/videos/{video_id}/content

    6. Save scene video:
       output/videos/medium/scene_1.mp4
```

**Example API Calls:**

**Step 1: Create video**
```bash
curl -X POST "https://api.openai.com/v1/videos" \
  -H "Authorization: Bearer sk-..." \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sora-2",
    "prompt": "[00:00-00:04] Medium Close-Up...",
    "size": "1280x720",
    "seconds": "12"
  }'

# Response:
{
  "id": "video_68ec0af621f081918be8e78dacbdbe0203bbfb26769ea388",
  "status": "queued",
  "created_at": 1729123456
}
```

**Step 2: Check status (poll every 10s)**
```bash
curl "https://api.openai.com/v1/videos/video_68ec..." \
  -H "Authorization: Bearer sk-..."

# Response (processing):
{
  "id": "video_68ec...",
  "status": "processing",
  "progress": 45
}

# Response (completed):
{
  "id": "video_68ec...",
  "status": "completed",
  "url": "https://..."
}
```

**Step 3: Download video**
```bash
curl -L "https://api.openai.com/v1/videos/video_68ec.../content" \
  -H "Authorization: Bearer sk-..." \
  --output scene_1.mp4
```

**WebSocket Updates:**
```javascript
// Frontend receives real-time updates:
{
  "progress": {
    "stages": {
      "generation": {
        "status": "in_progress",
        "progress": 25
      }
    },
    "variants": {
      "medium": {
        "status": "generating",
        "scenes": {
          "scene_1": { "status": "completed" },
          "scene_2": { "status": "in_progress" },
          "scene_3": { "status": "pending" },
          "scene_4": { "status": "pending" }
        }
      }
    }
  }
}
```

**Files Created:**
- `output/videos/medium/scene_1.mp4`
- `output/videos/medium/scene_2.mp4`
- `output/videos/medium/scene_3.mp4`
- `output/videos/medium/scene_4.mp4`

---

#### **STAGE 5: Assemble Final Video** 🎞️

**File:** `modules/video_assembler.py`

**Process:**
```python
1. Create concat file for ffmpeg:
   concat_file = "output/videos/medium/concat_medium.txt"

   Write:
   file 'scene_1.mp4'
   file 'scene_2.mp4'
   file 'scene_3.mp4'
   file 'scene_4.mp4'

2. Run ffmpeg to stitch videos:
   ffmpeg -f concat \
          -safe 0 \
          -i concat_medium.txt \
          -c copy \
          output/videos/medium/final_medium.mp4

3. Add to results:
   final_ads['medium'] = 'output/videos/medium/final_medium.mp4'
```

**ffmpeg Process:**
- Reads all scene files
- Concatenates without re-encoding (fast)
- Maintains same resolution/codec
- Creates seamless 48-second video (4 × 12s)

**Files Created:**
- `output/videos/medium/final_medium.mp4` (48 seconds)

---

#### **STAGE 6: Evaluate Generated Video** ⭐

**File:** `modules/ad_evaluator.py`

**Process:**
```python
1. Upload final video to Gemini File API
2. Wait for processing
3. Send evaluation prompt to Gemini:
   "Analyze this generated ad video and rate:
    - Visual quality (0-10)
    - Message clarity (0-10)
    - Pacing (0-10)
    - Storytelling (0-10)
    - Overall score
    - Predicted performance

    Compare to original:
    - Vertical match
    - Scene count
    - Character presence

    Provide recommendations for improvement"

4. Parse response and calculate ratings
5. Compare to original analysis:
   - Check if vertical matches
   - Compare scene counts
   - Verify character presence

6. Generate recommendations based on gaps:
   IF vertical doesn't match:
     severity: HIGH
     issue: Content doesn't match vertical
     fix: Strengthen vertical-specific keywords

7. Save evaluation report
```

**Example Evaluation:**
```json
{
  "ratings": {
    "visual_quality": 8.5,
    "message_clarity": 7.0,
    "pacing": 8.0,
    "storytelling": 7.5,
    "overall_score": 7.8,
    "predicted_performance": "GOOD - Should perform well"
  },
  "comparison": {
    "original_vertical": "auto_insurance",
    "generated_vertical": "unknown",
    "vertical_match": false,
    "original_scenes": 5,
    "generated_scenes": 3,
    "character_presence": {
      "original": true,
      "generated": true,
      "match": true
    }
  },
  "recommendations": [
    {
      "severity": "HIGH",
      "issue": "Content does not match original vertical",
      "details": "Expected auto_insurance content but generated video lacks key terms",
      "fix": "Strengthen vertical-specific keywords in B-roll prompts"
    },
    {
      "severity": "MEDIUM",
      "issue": "Pacing too slow",
      "details": "Slow pacing may lose viewer attention",
      "fix": "Use 'aggressive' or 'ultra' variant for faster pacing"
    }
  ]
}
```

**Files Created:**
- `output/analysis/evaluation_medium.json` (full report)
- `output/analysis/evaluation_medium_summary.txt` (human-readable)

---

### **STEP 5: Pipeline Completion** ✅

**What Happens:**
```python
1. Mark pipeline as completed
2. Log final results:
   {
     "status": "completed",
     "elapsed_time": 487.3,
     "variants_generated": ["medium"],
     "final_ads": {
       "medium": "output/videos/medium/final_medium.mp4"
     }
   }

3. Broadcast completion via WebSocket:
   socketio.emit('pipeline_completed', {
     "session_id": "xxx",
     "results": { ... }
   })
```

**Frontend Receives:**
```javascript
socket.on('pipeline_completed', (data) => {
  // Stop polling
  clearInterval(pollInterval);

  // Show results
  showResults(data.results);

  // Load detailed logs
  loadDetailedLogs(currentSessionId);
});
```

---

## Frontend Flow

### **Progress Tracking**

**1. WebSocket Real-Time Updates:**
```javascript
socket.on('progress_update', (data) => {
  // Update stage status
  updateProgress(data.progress);

  // Example data:
  {
    "stages": {
      "analysis": { "status": "completed", "progress": 100 },
      "variants": { "status": "completed", "progress": 100 },
      "prompts": { "status": "completed", "progress": 100 },
      "generation": { "status": "in_progress", "progress": 50 },
      "assembly": { "status": "pending", "progress": 0 }
    },
    "variants": {
      "medium": {
        "status": "generating",
        "scenes": {
          "scene_1": { "status": "completed" },
          "scene_2": { "status": "in_progress" }
        }
      }
    }
  }
});
```

**2. Live Logs Stream:**
```javascript
socket.on('event', (data) => {
  addLog(data.event.level, data.event.message, data.event.data);

  // Example:
  {
    "event": {
      "timestamp": "2025-10-12T21:00:00Z",
      "level": "info",
      "message": "✓ Scene 1 generated successfully",
      "data": {
        "scene": 1,
        "video_id": "video_68ec...",
        "duration": 12
      }
    }
  }
});
```

### **Results Display**

When pipeline completes:
```javascript
function showResults(results) {
  // Display:
  // - Completion status
  // - Time elapsed: 8m 7s
  // - Variants generated: medium
  // - Video players for each variant
  // - File paths

  // Scroll to results
  section.scrollIntoView({ behavior: 'smooth' });
}
```

---

## Detailed Logs System

### **Frontend: Loading Logs**

**Triggered when pipeline completes:**
```javascript
socket.on('pipeline_completed', (data) => {
  loadDetailedLogs(currentSessionId);
});

async function loadDetailedLogs(sessionId) {
  // 1. Fetch from API
  const response = await fetch(`/api/sessions/${sessionId}/detailed`);
  const data = await response.json();

  // 2. Update 4 sections
  updateDetailedLogs(data);
}
```

### **Backend: Serving Logs**

**Endpoint: `GET /api/sessions/<session_id>/detailed`**

```python
def get_detailed_logs(session_id):
    response = {}

    # 1. Load analysis
    analysis_files = Config.ANALYSIS_DIR.glob("analysis_*.json")
    latest_analysis = max(analysis_files, key=lambda p: p.stat().st_mtime)
    response['analysis'] = json.load(latest_analysis)

    # 2. Extract transformation info
    response['transformation'] = {
        'vertical': analysis.get('vertical'),
        'vertical_name': analysis.get('vertical_name'),
        'character_scenes': count_character_scenes(analysis),
        'broll_scenes': count_broll_scenes(analysis),
        'scenes': analysis.get('scene_breakdown')
    }

    # 3. Load Sora prompts
    prompts_files = Config.ANALYSIS_DIR.glob("sora_prompts_*.json")
    latest_prompts = max(prompts_files, key=lambda p: p.stat().st_mtime)
    response['prompts'] = json.load(latest_prompts)

    # 4. Load evaluation
    eval_files = Config.ANALYSIS_DIR.glob("evaluation_*.json")
    latest_eval = max(eval_files, key=lambda p: p.stat().st_mtime)
    response['evaluation'] = json.load(latest_eval)

    return jsonify(response)
```

### **Frontend: Displaying Logs**

**Section 1: Original Video Analysis**
```javascript
if (data.analysis) {
  const analysisEl = document.getElementById('analysis-data');
  analysisEl.textContent = JSON.stringify(data.analysis, null, 2);
}
```
Shows complete Gemini analysis JSON.

**Section 2: Ad Transformation**
```javascript
if (data.transformation) {
  let text = `Detected Vertical: ${data.transformation.vertical_name}\n\n`;
  text += `Scene Structure:\n`;
  text += `- Character scenes: ${data.transformation.character_scenes}\n`;
  text += `- B-roll scenes: ${data.transformation.broll_scenes}\n\n`;
  text += `Transformed Scenes:\n`;
  text += JSON.stringify(data.transformation.scenes, null, 2);

  transformEl.textContent = text;
}
```
Shows vertical detection and scene structure.

**Section 3: Sora Prompts (Full Text)**
```javascript
if (data.prompts) {
  let text = '';

  Object.entries(data.prompts).forEach(([variant, scenes]) => {
    text += `\n${'='.repeat(70)}\n`;
    text += `VARIANT: ${variant.toUpperCase()}\n`;
    text += `${'='.repeat(70)}\n\n`;

    scenes.forEach((scene, idx) => {
      text += `\n--- Scene ${idx + 1} ---\n`;
      text += `Timestamp: ${scene.timestamp}\n`;
      text += `Purpose: ${scene.purpose}\n\n`;
      text += `FULL PROMPT:\n`;
      text += scene.prompt;  // COMPLETE text sent to Sora
      text += `\n\n`;
    });
  });

  promptsEl.textContent = text;
}
```
Shows **EVERY SINGLE WORD** sent to Sora API.

**Section 4: Final Evaluation & Rating**
```javascript
if (data.evaluation) {
  let text = `OVERALL SCORE: ${eval.ratings.overall_score}/10\n`;
  text += `PREDICTION: ${eval.ratings.predicted_performance}\n\n`;

  text += `RATINGS:\n`;
  text += `- Visual Quality: ${eval.ratings.visual_quality}/10\n`;
  text += `- Message Clarity: ${eval.ratings.message_clarity}/10\n`;
  text += `- Pacing: ${eval.ratings.pacing}/10\n`;
  text += `- Storytelling: ${eval.ratings.storytelling}/10\n\n`;

  text += `COMPARISON:\n`;
  text += `- Original Vertical: ${eval.comparison.original_vertical}\n`;
  text += `- Generated Vertical: ${eval.comparison.generated_vertical}\n`;
  text += `- Vertical Match: ${eval.comparison.vertical_match ? '✓ YES' : '✗ NO'}\n\n`;

  if (eval.recommendations) {
    text += `RECOMMENDATIONS:\n`;
    eval.recommendations.forEach((rec, idx) => {
      text += `\n${idx + 1}. [${rec.severity}] ${rec.issue}\n`;
      text += `   Details: ${rec.details}\n`;
      text += `   Fix: ${rec.fix}\n`;
    });
  }

  evalEl.textContent = text;
}
```
Shows quality ratings and actionable recommendations.

---

## File System & Data Flow

### **Directory Structure:**
```
soraking/
├── output/
│   ├── uploads/
│   │   └── video_1729123456.mp4           # Uploaded video
│   ├── analysis/
│   │   ├── analysis_20251012_210000.json  # Gemini analysis
│   │   ├── sora_prompts_analysis_20251012_210000.json  # All prompts
│   │   ├── evaluation_medium.json         # Evaluation report
│   │   └── evaluation_medium_summary.txt  # Human-readable
│   ├── videos/
│   │   └── medium/
│   │       ├── scene_1.mp4                # Sora generated
│   │       ├── scene_2.mp4
│   │       ├── scene_3.mp4
│   │       ├── scene_4.mp4
│   │       ├── concat_medium.txt          # ffmpeg concat file
│   │       └── final_medium.mp4           # Stitched final video
│   └── logs/
│       └── session_20251012_210000/
│           ├── progress.json              # Pipeline progress
│           └── events.json                # All log events
├── frontend/
│   ├── index.html
│   └── app.js
├── modules/
│   ├── video_analyzer.py
│   ├── sora_transformer.py
│   ├── sora_prompt_builder.py
│   ├── sora_generator.py
│   ├── video_assembler.py
│   └── ad_evaluator.py
├── server.py
├── ad_cloner.py
└── config.py
```

### **Data Flow:**
```
User Upload → uploads/video.mp4
     ↓
Gemini Analysis → analysis/analysis_TIMESTAMP.json
     ↓
Transform → In-memory variant structures
     ↓
Build Prompts → analysis/sora_prompts_analysis_TIMESTAMP.json
     ↓
Sora API → videos/medium/scene_X.mp4
     ↓
ffmpeg → videos/medium/final_medium.mp4
     ↓
Gemini Evaluation → analysis/evaluation_medium.json
     ↓
Frontend Display → User sees results + detailed logs
```

---

## Real-Time Updates

### **WebSocket Communication:**

**Backend broadcasts:**
```python
# 1. Event logging
socketio.emit('event', {
    'session_id': session_id,
    'event': {
        'timestamp': '2025-10-12T21:00:00Z',
        'level': 'info',
        'message': '✓ Scene 1 generated',
        'data': { 'scene': 1 }
    }
}, room=session_id)

# 2. Progress updates
socketio.emit('progress_update', {
    'session_id': session_id,
    'progress': {
        'status': 'in_progress',
        'stages': { ... },
        'variants': { ... }
    }
}, room=session_id)

# 3. Completion
socketio.emit('pipeline_completed', {
    'session_id': session_id,
    'results': { ... }
})
```

**Frontend receives and updates UI:**
```javascript
// Live logs
socket.on('event', (data) => {
  addLog(data.event.level, data.event.message);
});

// Progress bars
socket.on('progress_update', (data) => {
  updateProgress(data.progress);
});

// Final results
socket.on('pipeline_completed', (data) => {
  showResults(data.results);
  loadDetailedLogs(currentSessionId);
});
```

---

## Summary

**Complete Flow:**
1. ✅ User uploads video → saved to `uploads/`
2. ✅ Cost estimated based on variants selected
3. ✅ Pipeline starts in background thread
4. ✅ **Stage 1**: Gemini analyzes video → `analysis.json`
5. ✅ **Stage 2**: Transform to variant structures (in memory)
6. ✅ **Stage 3**: Build Sora prompts → `sora_prompts.json`
7. ✅ **Stage 4**: Sora generates scenes → `scene_X.mp4`
8. ✅ **Stage 5**: ffmpeg stitches → `final.mp4`
9. ✅ **Stage 6**: Gemini evaluates → `evaluation.json`
10. ✅ Results displayed with video players
11. ✅ Detailed logs loaded in 4 expandable sections

**Key Features:**
- Real-time progress via WebSocket
- Complete transparency (see every prompt)
- Automatic quality evaluation
- Cost-effective (80% savings with Sora 2)
- Actionable recommendations for improvement

**The entire process is fully automated and provides complete visibility into every step!**
