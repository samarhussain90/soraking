# Product Requirements Document (PRD)
## AI Director Ad Generation System

**Version:** 1.0  
**Date:** October 2025  
**Purpose:** System specification for AI agent replication  
**Author:** Soraking Team

---

## 1. Executive Summary

### 1.1 System Purpose
The AI Director Ad Generation System transforms winning social media ads into multiple high-converting variants with different aggression levels. The system uses a dual-AI approach combining OpenAI GPT-4o for creative scene generation and Google Gemini 2.5 for video analysis, outputting production-ready videos via Sora 2 Pro.

### 1.2 Key Capabilities
- **AI-Driven Scene Generation**: OpenAI acts as "Ad Director" to create dynamic scene specifications
- **Conversion Optimization**: Marketing validator ensures ads follow best practices
- **Character Consistency**: Prevents Sora hallucination by enforcing B-roll-only in middle scenes
- **Dynamic Text Extraction**: Automatically extracts prices, CTAs, and power words from scripts
- **Multi-Variant Generation**: Creates 4 variants (soft, medium, aggressive, ultra) simultaneously

### 1.3 Technology Stack
- **Video Analysis**: Google Gemini 2.5 Flash
- **Scene Generation**: OpenAI GPT-4o
- **Video Synthesis**: Sora 2 Pro (1792x1024, 12s clips)
- **Backend**: Python 3.12, Flask
- **Frontend**: HTML/CSS/JavaScript with WebSocket
- **APIs**: OpenAI, Google Generative AI, Sora

---

## 2. Problem Statement

### 2.1 Core Challenge
Creating scroll-stopping social media ads that convert requires:
- Understanding what makes an ad perform
- Adapting content to different audience sensitivities (aggression levels)
- Maintaining visual consistency (preventing face hallucination)
- Synchronizing audio, text, and visual elements

### 2.2 Previous Approach Issues
**Template-Based System (Deprecated)**:
- Hardcoded text patterns: `"$120"` extracted via regex, no context
- Static audio presets: Same 140 BPM for all aggressive ads
- Fixed visual patterns: Camera moves had placeholders like `{move}`
- Required manual updates for new verticals
- Character consistency issues: Spokesperson in every scene caused hallucination

### 2.3 Solution Requirements
- **Dynamic Generation**: AI determines text, audio, visuals from script context
- **Intelligent Extraction**: "I was paying $120..." → "$120 A MONTH?!" (adds urgency)
- **Conversion Focus**: Marketing analysis scores and optimizes each ad
- **Technical Compliance**: Ensures Sora 2 Pro compatibility (character limits, scene structure)

---

## 3. Solution Architecture

### 3.1 System Overview

```
┌─────────────┐
│ Upload Video│
│   (MP4)     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  STEP 1: Video Analysis (Gemini 2.5)                │
│  - Extracts script, scenes, spokesperson            │
│  - Detects vertical (auto/health/finance)           │
│  - Identifies key moments                           │
│  Output: analysis.json                              │
└──────┬──────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  STEP 2: Variant Generation                         │
│  - Creates 4 aggression levels                      │
│  - Modifies emotions, pacing per variant            │
│  Output: 4 variant specs                            │
└──────┬──────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  STEP 3: AI Director (OpenAI GPT-4o)                │
│  - Generates complete scene structures              │
│  - Extracts text from script dynamically            │
│  - Designs audio (voiceover, music, SFX)            │
│  - Creates visual progressions                      │
│  Output: director_scenes.json                       │
└──────┬──────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  STEP 4: Marketing Validator (OpenAI GPT-4o)        │
│  - Fixes character consistency (B-roll scenes 2-4)  │
│  - Scores conversion potential (1-10)               │
│  - Optimizes text overlays                          │
│  Output: refined_scenes.json                        │
└──────┬──────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  STEP 5: Prompt Composition                         │
│  - Converts AI scenes to Sora format                │
│  - Validates prompt length (<2000 chars)            │
│  Output: sora_prompts.json                          │
└──────┬──────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  STEP 6: Video Generation (Sora 2 Pro)              │
│  - Generates each scene (parallel)                  │
│  - 12 seconds per scene                             │
│  Output: scene_01.mp4, scene_02.mp4...              │
└──────┬──────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  STEP 7: Assembly                                   │
│  - Combines scenes into final videos                │
│  Output: final_soft.mp4, final_medium.mp4...        │
└──────┬──────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│  4 Final    │
│  Video Ads  │
└─────────────┘
```

### 3.2 Key Innovation: Dual-AI Approach
1. **AI Director (Creative)**: OpenAI generates unique scene specifications
2. **Marketing Validator (Optimization)**: OpenAI validates and refines for conversions

This ensures both creativity and quality control.

---

## 4. Core Components

### 4.1 Component Overview

| Component | File | Purpose | Input | Output |
|-----------|------|---------|-------|--------|
| **GeminiVideoAnalyzer** | `modules/gemini_analyzer.py` | Analyzes video content | Video file | analysis.json |
| **AggressionVariantGenerator** | `modules/aggression_variants.py` | Creates variants | Analysis | 4 variant specs |
| **AdDirector** | `modules/ad_director.py` | Generates scene structures | Analysis + variant | Scene specs |
| **MarketingValidator** | `modules/marketing_validator.py` | Optimizes & validates | Scene specs | Refined scenes |
| **SoraPromptComposer** | `modules/sora_prompt_composer.py` | Formats for Sora | Refined scenes | Sora prompts |
| **PromptValidator** | `modules/prompt_validator.py` | Technical checks | Prompts | Validation report |
| **SoraClient** | `modules/sora_client.py` | Generates videos | Prompts | Video files |
| **VideoAssembler** | `modules/video_assembler.py` | Combines scenes | Scene videos | Final videos |
| **AdEvaluator** | `modules/ad_evaluator.py` | Quality scoring | Final videos | Scores |

### 4.2 Main Orchestrator

**File**: `ad_cloner.py`

**Function**: `clone_ad(video_path, variants)`

**Flow**:
```python
1. analyzer.analyze_video(video_path) → analysis
2. variant_generator.generate_variants(analysis) → 4 variants
3. FOR EACH variant:
   a. ad_director.generate_scene_structure() → scenes
   b. marketing_validator.validate_and_refine() → refined_scenes
   c. prompt_composer.compose_from_director_scenes() → prompts
   d. prompt_validator.validate_all_prompts() → validation
   e. sora_client.generate_videos() → scene videos
4. assembler.assemble_videos() → final videos
5. evaluator.evaluate() → scores
```

---

## 5. Data Flow & Contracts

### 5.1 Gemini Analysis Output

```json
{
  "script": {
    "full_transcript": "I was paying $120 a month...",
    "word_count": 85
  },
  "vertical": "auto_insurance",
  "spokesperson": {
    "description": "female, mid-20s, energetic, casual setting"
  },
  "scenes": [
    {
      "scene_number": 1,
      "timestamp": "00:00-00:06",
      "purpose": "Hook/Problem",
      "visual_description": "...",
      "emotion": "frustrated"
    }
  ],
  "key_moments": [
    {"timestamp": "00:03", "description": "price reveal"}
  ]
}
```

### 5.2 AI Director Scene Structure

```json
{
  "scene_number": 1,
  "timestamp": "00:00-00:12",
  "scene_type": "character",
  "purpose": "hook/problem",
  
  "visual": {
    "shot_progression": [
      {
        "time": "00:00-00:03",
        "shot_type": "medium close-up",
        "subject": "spokesperson looking at bill",
        "camera_move": "push-in",
        "lighting": "dramatic",
        "focus": "sharp"
      }
    ],
    "color_grade": "vibrant",
    "energy_level": "urgent"
  },
  
  "audio": {
    "voiceover": {
      "script": "I was paying $120 a month...",
      "tone": "urgent",
      "pace": "fast",
      "emotion": "frustrated"
    },
    "music": {
      "genre": "electronic",
      "bpm": 140,
      "intensity": "builds",
      "key_moments": ["0:08 climax", "0:11 drop"]
    },
    "sound_effects": [
      {"time": "0:03", "effect": "cash register"},
      {"time": "0:08", "effect": "whoosh"}
    ]
  },
  
  "text_overlays": [
    {
      "text": "$120 A MONTH?!",
      "start": "0:02",
      "end": "0:05",
      "position": "top-center",
      "font": "Impact",
      "size": "130pt",
      "color": "red",
      "animation": "crash-in",
      "outline": "black"
    }
  ],
  
  "sync_points": [
    {"time": "0:03", "event": "text crashes in + SFX"}
  ]
}
```

### 5.3 Marketing Validator Output

```json
{
  "conversion_score": 7,
  "issues_found": [
    "Scene 2 shows spokesperson - change to B-roll phone screen",
    "Text overlay too long - reduce to 5 words max"
  ],
  "marketing_analysis": {
    "hook_strength": "Strong",
    "problem_clarity": "Clear",
    "solution_appeal": "High",
    "urgency_level": "Medium",
    "cta_effectiveness": "Medium"
  },
  "refined_scenes": [
    // Same structure as input, with fixes applied
  ],
  "recommendations": [
    "Add scarcity text like 'Limited Time' to scene 3",
    "Sync bass drop with price reveal at 0:18"
  ]
}
```

### 5.4 Sora Prompt Format

```
[00:00-00:03] MEDIUM CLOSE-UP: spokesperson looking at bill. 
Push-in camera. Dramatic lighting. Sharp focus.

[00:03-00:06] CLOSE-UP: frustrated expression. Zoom-in. 
High-contrast lighting.

AUDIO: urgent voice, fast pace, frustrated emotion. Says: "I was 
paying $120 a month for car insurance until I found a link that 
changed everything." Background music: electronic, 140 BPM, builds. 
0:03 intensifies, 0:08 climax. Sound effect at 0:03: cash register.

TEXT OVERLAYS: At 0:02, crash-in: "$120 A MONTH?!" (Impact, 130pt, 
red with black outline). Fades out at 0:05.

TECHNICAL: 4K resolution, 1792x1024, urgent style, vibrant grade, 
cinematic audio mix.
```

---

## 6. AI Director System (Core Innovation)

### 6.1 Architecture

**Component**: `AdDirector` class in `modules/ad_director.py`

**Model**: OpenAI GPT-4o

**Temperature**: 0.8 (creative but consistent)

**Response Format**: JSON object

### 6.2 System Prompt

The AI Director is instructed to act as an expert ad director specializing in Sora 2 Pro. Key instructions:

- Transform analysis into complete scene specifications
- Include visual (camera, lighting), audio (voiceover, music, SFX), text overlays
- Each scene is 12 seconds with arc: HOOK → BUILD → PEAK → RESOLVE
- Extract text dynamically from script (not hardcoded patterns)
- Sync audio beats with visual moments and text reveals

### 6.3 User Prompt Structure

```python
prompt = f"""
Create a {aggression} variant ad for {vertical} insurance.

SCRIPT: {script}
SPOKESPERSON: {spokesperson}
KEY MOMENTS: {key_moments}
VARIANT SCENES: {variant_scenes}

AGGRESSION SPECS:
- Energy: {energy}
- Music BPM: {bpm_range}
- Text Style: {text_style}

Generate {num_scenes} complete scenes with:
1. Dynamic Visuals: Multi-shot progressions
2. Complete Audio: Voiceover + music + SFX
3. Bold Text Overlays: Extract from script
4. Perfect Sync: Text appears when mentioned

Output valid JSON.
"""
```

### 6.4 Dynamic Text Extraction

**Old Approach** (Template):
```
regex: \$\d+ → ["$120", "$39"]
```

**New Approach** (AI Director):
```
Script: "I was paying $120 a month..."
AI: "$120 A MONTH?!" (adds question for engagement)

Script: "qualified for $39 a month"  
AI: "ONLY $39/MONTH" (adds emphasis)
```

AI understands context and creates compelling overlays.

### 6.5 Aggression Scaling

| Level | BPM | Energy | Text Style | Camera |
|-------|-----|--------|------------|--------|
| Soft | 75-95 | Calm, friendly | Gentle fades | Slow push-ins |
| Medium | 110-130 | Engaging | Smooth pops | Steady dolly |
| Aggressive | 135-150 | Urgent | Bold crashes | Fast whip pans |
| Ultra | 155-175 | Explosive | Massive reveals | Crash zooms |

---

## 7. Marketing Validator (Quality Gate)

### 7.1 Purpose

The Marketing Validator is the second AI pass that:
1. **Ensures Character Consistency**: Forces B-roll in scenes 2-4 to prevent Sora hallucination
2. **Optimizes for Conversions**: Scores ads on marketing effectiveness
3. **Fixes Common Issues**: Text too long, missing urgency, weak CTAs

### 7.2 Character Consistency Rules

**Critical for Sora 2 Pro**:

- **Scene 1**: ✅ Spokesperson allowed (establishes character)
- **Scenes 2-4**: ❌ B-ROLL ONLY (phones, screens, products, documents)
  - Prevents Sora from generating inconsistent faces
  - Environment-only shots
- **Scene 5 (CTA)**: ✅ Optional spokesperson (can show for final CTA)

**Example Fix**:
```
BEFORE: Scene 2 shows "spokesperson smiling"
AFTER: Scene 2 shows "phone screen displaying $39/month"
```

### 7.3 Conversion Checklist

The validator scores ads on:

1. **Hook Strength**: Does scene 1 grab attention in 3 seconds?
2. **Problem Clarity**: Is the pain point relatable?
3. **Solution Appeal**: Is the benefit obvious and compelling?
4. **Urgency Level**: Does it create FOMO or time pressure?
5. **CTA Effectiveness**: Is the action crystal clear?

**Score**: 1-10 (7+ is considered good)

### 7.4 Text Overlay Optimization

**Rules**:
- Max 5 words per overlay (scannable)
- Prices must be HUGE and bold (120pt-240pt)
- Questions create engagement
- CTAs are directive ("CLICK NOW" not "you can click")

**Example Refinement**:
```
BEFORE: "Click the link below to check if you qualify for savings"
AFTER: "CLICK BELOW" (scene 5, 3 words)
```

### 7.5 Output Format

```json
{
  "conversion_score": 7,
  "issues_found": ["list of problems"],
  "marketing_analysis": {
    "hook_strength": "Strong/Medium/Weak",
    "problem_clarity": "Clear/Unclear",
    "solution_appeal": "High/Medium/Low",
    "urgency_level": "High/Medium/Low",
    "cta_effectiveness": "Strong/Medium/Weak"
  },
  "refined_scenes": [/* fixed scenes */],
  "recommendations": ["list of suggestions"]
}
```

---

## 8. Configuration Requirements

### 8.1 Environment Variables (.env)

```bash
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
PORT=3000
```

### 8.2 Sora Settings (config.py)

```python
SORA_MODEL = 'sora-2-pro'
SORA_RESOLUTION = '1792x1024'  # Higher resolution
SORA_DURATION = '12'  # Seconds per scene
SORA_2_PRO_COST_PER_SECOND = 0.32  # Pricing
```

**Why Sora 2 Pro?**
- Better character consistency
- Supports 1792x1024 resolution
- Native audio generation capabilities
- Improved prompt adherence

### 8.3 Directory Structure

```
soraking/
├── config.py
├── ad_cloner.py
├── server.py
├── modules/
│   ├── gemini_analyzer.py
│   ├── aggression_variants.py
│   ├── ad_director.py
│   ├── marketing_validator.py
│   ├── sora_prompt_composer.py
│   ├── prompt_validator.py
│   ├── sora_client.py
│   ├── video_assembler.py
│   └── ad_evaluator.py
├── frontend/
│   ├── index.html
│   └── app.js
├── output/
│   ├── analysis/
│   ├── videos/
│   │   ├── soft/
│   │   ├── medium/
│   │   ├── aggressive/
│   │   └── ultra/
│   └── logs/
└── requirements.txt
```

### 8.4 Dependencies (requirements.txt)

```
flask>=2.3.0
flask-socketio>=5.3.0
python-socketio>=5.9.0
openai>=1.3.0
google-generativeai>=0.3.0
python-dotenv>=1.0.0
opencv-python>=4.8.0
moviepy>=1.0.3
```

---

## 9. Implementation Guide

### 9.1 Setup Steps

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**
   ```bash
   cp .env.example .env
   # Edit .env with your keys
   ```

3. **Initialize Directory Structure**
   ```bash
   mkdir -p output/analysis output/videos output/logs
   ```

4. **Start Server**
   ```bash
   python server.py
   # Opens http://localhost:3000
   ```

### 9.2 Module Implementation Order

**Phase 1: Foundation**
1. `config.py` - Configuration management
2. `modules/gemini_analyzer.py` - Video analysis
3. `modules/aggression_variants.py` - Variant generation

**Phase 2: Core Innovation**
4. `modules/ad_director.py` - AI Director (OpenAI scene generation)
5. `modules/marketing_validator.py` - Conversion optimization

**Phase 3: Prompt Pipeline**
6. `modules/sora_prompt_composer.py` - Format converter
7. `modules/prompt_validator.py` - Technical validation

**Phase 4: Video Generation**
8. `modules/sora_client.py` - Sora API integration
9. `modules/video_assembler.py` - Scene combination
10. `modules/ad_evaluator.py` - Quality scoring

**Phase 5: Integration**
11. `ad_cloner.py` - Main orchestrator
12. `server.py` - Flask web server
13. `frontend/` - Web interface

### 9.3 Key Implementation Details

#### 9.3.1 AdDirector Implementation

```python
class AdDirector:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = "gpt-4o"
    
    def generate_scene_structure(
        self, gemini_analysis, variant_data, aggression_level
    ):
        # Build system prompt (expert ad director)
        system_prompt = self._get_director_system_prompt()
        
        # Build user prompt from analysis
        user_prompt = self._build_director_prompt(
            script=gemini_analysis['script']['full_transcript'],
            vertical=gemini_analysis['vertical'],
            spokesperson=gemini_analysis['spokesperson']['description'],
            variant_scenes=variant_data['modified_scenes'],
            aggression=aggression_level
        )
        
        # Call OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.8
        )
        
        # Parse scenes
        result = json.loads(response.choices[0].message.content)
        return result['scenes']
```

#### 9.3.2 MarketingValidator Implementation

```python
class MarketingValidator:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = "gpt-4o"
    
    def validate_and_refine(
        self, director_scenes, script, vertical
    ):
        # Build validation prompt
        validation_prompt = f"""
        Validate these scenes:
        - Scene 1: Spokesperson OK
        - Scenes 2-4: B-roll ONLY (no people)
        - Scene 5: Optional spokesperson
        
        SCENES: {json.dumps(director_scenes)}
        SCRIPT: {script}
        
        Fix character issues and optimize for conversions.
        """
        
        # Call OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": validation_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3  # Lower for consistency
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
```

#### 9.3.3 SoraPromptComposer Implementation

```python
class SoraPromptComposer:
    def compose_from_director_scenes(self, director_scenes):
        prompts = []
        
        for scene in director_scenes:
            # Format visual layer
            visual = self._format_visual_layer(scene['visual'])
            
            # Format audio layer
            audio = self._format_audio_layer(scene['audio'])
            
            # Format text layer
            text = self._format_text_layer(scene['text_overlays'])
            
            # Combine into Sora format
            prompt = f"""
{visual}

AUDIO: {audio}

TEXT OVERLAYS: {text}

TECHNICAL: 4K resolution, 1792x1024, {scene['visual']['energy_level']} style, 
{scene['visual']['color_grade']} grade, cinematic audio mix.
"""
            
            prompts.append({
                'scene_number': scene['scene_number'],
                'prompt': prompt,
                'has_audio': bool(scene.get('audio')),
                'has_text': bool(scene.get('text_overlays'))
            })
        
        return prompts
```

---

## 10. Testing Strategy

### 10.1 Unit Tests

**Test Each Module**:

```python
# test_ad_director.py
def test_scene_generation():
    director = AdDirector()
    scenes = director.generate_scene_structure(
        mock_analysis, mock_variant, 'aggressive'
    )
    assert len(scenes) > 0
    assert scenes[0]['scene_type'] in ['character', 'b-roll']
    assert 'visual' in scenes[0]
    assert 'audio' in scenes[0]
```

```python
# test_marketing_validator.py
def test_character_consistency():
    validator = MarketingValidator()
    result = validator.validate_and_refine(
        mock_scenes, mock_script, 'auto_insurance'
    )
    # Scene 1 should be character
    assert result['refined_scenes'][0]['scene_type'] == 'character'
    # Scenes 2-4 should be b-roll
    for scene in result['refined_scenes'][1:4]:
        assert scene['scene_type'] == 'b-roll'
```

### 10.2 Integration Test

```python
# test_full_pipeline.py
def test_complete_pipeline():
    cloner = AdCloner()
    result = cloner.clone_ad('test_video.mp4', ['aggressive'])
    
    # Check outputs
    assert Path('output/analysis/analysis_*.json').exists()
    assert Path('output/videos/aggressive/scene_01.mp4').exists()
    assert Path('output/videos/final_aggressive.mp4').exists()
    
    # Validate structure
    with open('output/analysis/sora_prompts_*.json') as f:
        prompts = json.load(f)
        assert len(prompts['aggressive']) > 0
```

### 10.3 Validation Tests

```python
# test_validation_rules.py
def test_character_consistency_rule():
    """Ensure scenes 2-4 have no spokesperson"""
    scenes = load_test_output('refined_scenes.json')
    for i, scene in enumerate(scenes):
        if 1 < i < 4:  # Scenes 2-4 (0-indexed as 1-3)
            assert 'spokesperson' not in scene['visual']['subject'].lower()
            assert scene['scene_type'] == 'b-roll'

def test_text_overlay_length():
    """Ensure text overlays are 5 words or less"""
    scenes = load_test_output('refined_scenes.json')
    for scene in scenes:
        for overlay in scene.get('text_overlays', []):
            word_count = len(overlay['text'].split())
            assert word_count <= 5, f"Text too long: {overlay['text']}"

def test_prompt_length():
    """Ensure Sora prompts are under 2000 characters"""
    prompts = load_test_output('sora_prompts.json')
    for prompt in prompts:
        assert len(prompt['prompt']) < 2000
```

### 10.4 Output Verification

```bash
# Run test and verify structure
python test_marketing_validation.py

# Check output:
# 1. Conversion score: 7+/10
# 2. Scene 1: character
# 3. Scenes 2-4: b-roll only
# 4. All prompts < 2000 chars
# 5. Text overlays extracted from script
```

---

## 11. Success Metrics

### 11.1 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Conversion Score | 7+/10 | Marketing validator output |
| Character Consistency | 100% | Scene 1 only has spokesperson |
| Prompt Length | <2000 chars | All prompts within Sora limit |
| Text Extraction Accuracy | 100% | Prices/CTAs correctly extracted |
| Generation Time | 15-20 min | Time for 4 variants |

### 11.2 Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Scene Count | 4-5 per variant | Based on video length |
| Validation Pass Rate | 95%+ | Prompts passing technical validation |
| B-roll Compliance | 100% | Scenes 2-4 have no people |
| Text Overlay Count | 2-3 per scene | Optimal readability |

### 11.3 Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cost per Variant | ~$200 | Sora 2 Pro: 5 scenes × 12s × $0.32/s |
| Production Time | <25 min | Full pipeline completion |
| Manual Intervention | 0% | Fully automated generation |

---

## 12. API Integration

### 12.1 OpenAI API (GPT-4o)

#### 12.1.1 AI Director Call

**Purpose**: Generate scene structures dynamically

**Endpoint**: `https://api.openai.com/v1/chat/completions`

**Authentication**: Bearer token in headers

**Request**:
```python
import openai
from openai import OpenAI

client = OpenAI(api_key='sk-...')

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": """You are an expert Ad Director specializing in 
            high-converting social media ads for Sora 2 Pro.
            
            Your job: Transform video analysis into COMPLETE scene 
            specifications with:
            - Visual storytelling (camera, lighting, composition)
            - Audio design (voiceover, music, SFX timing)
            - Text overlays (exact text, timing, style, animation)
            - Beat synchronization
            
            Each scene is 12 seconds with arc: HOOK → BUILD → PEAK → RESOLVE.
            
            Output JSON format: { "scenes": [...] }"""
        },
        {
            "role": "user",
            "content": f"""Create a {aggression} variant ad for {vertical}.
            
            SCRIPT: {script}
            SPOKESPERSON: {spokesperson}
            KEY MOMENTS: {key_moments}
            VARIANT SCENES: {variant_scenes}
            
            AGGRESSION SPECS:
            - Energy: {energy}
            - Music BPM: {bpm_range}
            - Text Style: {text_style}
            
            Generate {num_scenes} complete scenes with dynamic visuals, 
            audio, and text overlays. Output valid JSON."""
        }
    ],
    response_format={"type": "json_object"},
    temperature=0.8  # Creative but consistent
)

# Parse response
result = json.loads(response.choices[0].message.content)
scenes = result['scenes']
```

**Response Format**:
```json
{
  "scenes": [
    {
      "scene_number": 1,
      "timestamp": "00:00-00:12",
      "scene_type": "character",
      "purpose": "hook/problem",
      "visual": {
        "shot_progression": [
          {
            "time": "00:00-00:03",
            "shot_type": "medium close-up",
            "subject": "spokesperson looking at bill",
            "camera_move": "push-in",
            "lighting": "dramatic",
            "focus": "sharp"
          }
        ],
        "color_grade": "vibrant",
        "energy_level": "urgent"
      },
      "audio": {
        "voiceover": {
          "script": "I was paying $120 a month...",
          "tone": "urgent",
          "pace": "fast",
          "emotion": "frustrated"
        },
        "music": {
          "genre": "electronic",
          "bpm": 140,
          "intensity": "builds",
          "key_moments": ["0:08 climax", "0:11 drop"]
        },
        "sound_effects": [
          {"time": "0:03", "effect": "cash register"}
        ]
      },
      "text_overlays": [
        {
          "text": "$120 A MONTH?!",
          "start": "0:02",
          "end": "0:05",
          "position": "top-center",
          "font": "Impact",
          "size": "130pt",
          "color": "red",
          "animation": "crash-in",
          "outline": "black"
        }
      ],
      "sync_points": [
        {"time": "0:03", "event": "text crashes in + SFX"}
      ]
    }
  ]
}
```

**Rate Limits**: 10,000 TPM (tokens per minute), 500 RPM (requests per minute)

**Cost**: ~$0.03 per scene generation (input + output tokens)

#### 12.1.2 Marketing Validator Call

**Purpose**: Validate and refine scenes for conversions

**Endpoint**: Same as AI Director (`https://api.openai.com/v1/chat/completions`)

**Request**:
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": """You are a Marketing Expert and Technical Validator 
            for Sora 2 Pro video ads.
            
            Your mission: Analyze AI-generated ad scenes and optimize for:
            1. CONVERSION RATE - Make ads that convert
            2. CHARACTER CONSISTENCY - Prevent Sora hallucination
            3. TECHNICAL COMPLIANCE - Sora 2 Pro compatibility
            
            CRITICAL RULES:
            - Scene 1 ONLY: Spokesperson can appear
            - Scenes 2-4+: MUST be B-roll (no people, no faces)
            - Scene 5 (CTA): Optional spokesperson
            
            Output JSON with refined_scenes and marketing_analysis."""
        },
        {
            "role": "user",
            "content": f"""Validate and optimize these scenes:
            
            SCRIPT: {script}
            VERTICAL: {vertical}
            SCENES: {json.dumps(director_scenes)}
            
            Fix character consistency issues (B-roll scenes 2-4).
            Optimize text for conversion.
            Ensure perfect audio/visual sync.
            
            Return JSON with analysis and refined scenes."""
        }
    ],
    response_format={"type": "json_object"},
    temperature=0.3  # Lower for consistency
)

result = json.loads(response.choices[0].message.content)
```

**Response Format**:
```json
{
  "conversion_score": 7,
  "issues_found": [
    "Scene 2 shows spokesperson - change to B-roll phone screen",
    "Text overlay too long - reduce to 5 words max"
  ],
  "marketing_analysis": {
    "hook_strength": "Strong",
    "problem_clarity": "Clear",
    "solution_appeal": "High",
    "urgency_level": "Medium",
    "cta_effectiveness": "Medium"
  },
  "refined_scenes": [
    // Same structure as input, with fixes applied
  ],
  "recommendations": [
    "Add scarcity text like 'Limited Time' to scene 3"
  ]
}
```

### 12.2 Google Gemini API (2.5 Flash)

#### 12.2.1 Video Analysis Call

**Purpose**: Extract script, scenes, spokesperson from video

**Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`

**Authentication**: API key in URL parameter

**Setup**:
```python
import google.generativeai as genai

genai.configure(api_key='AIza...')
model = genai.GenerativeModel('gemini-2.5-flash')
```

**Upload Video**:
```python
# Upload video file to Gemini
video_file = genai.upload_file(path='video.mp4')
print(f"Upload complete: {video_file.name}")

# Wait for video to be ready
while video_file.state.name == "PROCESSING":
    time.sleep(5)
    video_file = genai.get_file(video_file.name)

print(f"Video ready: {video_file.uri}")
```

**Analysis Request**:
```python
prompt = """Analyze this video ad and extract:

1. Full transcript (word-for-word)
2. Scene breakdown with timestamps
3. Spokesperson description (detailed physical appearance)
4. Ad vertical (auto_insurance, health_insurance, finance, etc.)
5. Key moments (price reveals, CTAs, emotional shifts)
6. Marketing psychology (why it works)

Output JSON format:
{
  "script": {
    "full_transcript": "...",
    "word_count": 85
  },
  "vertical": "auto_insurance",
  "spokesperson": {
    "description": "female, mid-20s, wavy brown hair, energetic, casual home setting"
  },
  "scenes": [
    {
      "scene_number": 1,
      "timestamp": "00:00-00:06",
      "purpose": "Hook/Problem",
      "visual_description": "...",
      "emotion": "frustrated"
    }
  ],
  "key_moments": [
    {"timestamp": "00:03", "description": "price reveal $120"}
  ],
  "ad_structure": {
    "hook": "...",
    "problem_presented": "...",
    "solution_offered": "...",
    "proof_elements": ["..."],
    "urgency_tactics": ["..."]
  },
  "why_it_works": ["..."]
}

Be extremely detailed. Include exact timestamps."""

response = model.generate_content(
    [video_file, prompt],
    generation_config=genai.GenerationConfig(
        temperature=0.2  # Low for consistency
    )
)

# Parse JSON from response
response_text = response.text
if "```json" in response_text:
    json_start = response_text.find("```json") + 7
    json_end = response_text.find("```", json_start)
    response_text = response_text[json_start:json_end]

analysis = json.loads(response_text.strip())
```

**Response Format**:
```json
{
  "script": {
    "full_transcript": "I was paying $120 a month for car insurance...",
    "word_count": 85
  },
  "vertical": "auto_insurance",
  "spokesperson": {
    "gender": "female",
    "age": "mid-20s",
    "description": "female, mid-20s, wavy brown hair, wearing casual white t-shirt, energetic and conversational tone, sitting in modern home office with natural lighting from window behind"
  },
  "scenes": [
    {
      "scene_number": 1,
      "timestamp": "00:00-00:06",
      "duration": 6,
      "purpose": "Hook/Problem",
      "visual_description": "Close-up of spokesperson looking frustrated at phone",
      "audio_description": "Voiceover about high insurance costs",
      "emotion": "frustrated",
      "key_elements": ["insurance bill visible", "concerned expression"]
    }
  ],
  "key_moments": [
    {
      "timestamp": "00:03",
      "description": "Shows $120/month on screen",
      "significance": "Establishes the problem"
    }
  ],
  "ad_structure": {
    "hook": "Relatable problem of overpaying for insurance",
    "problem_presented": "Paying $120/month for car insurance",
    "solution_offered": "New link/tool that reduced to $39/month",
    "proof_elements": ["Personal testimonial", "Specific price comparison"],
    "urgency_tactics": ["Limited knowledge", "New law revelation"]
  },
  "why_it_works": [
    "Immediate price comparison creates strong contrast",
    "Personal story builds trust and relatability",
    "Urgency created by 'new law' information"
  ]
}
```

**Rate Limits**: 60 requests per minute

**Cost**: Free tier available, paid tier ~$0.02 per video analysis

### 12.3 Sora API (2 Pro)

#### 12.3.1 Create Video Job

**Purpose**: Generate video from prompt

**Endpoint**: `https://api.openai.com/v1/videos`

**Authentication**: Bearer token in headers

**Request**:
```python
import requests

api_key = 'sk-...'
base_url = 'https://api.openai.com/v1/videos'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

params = {
    'model': 'sora-2-pro',
    'prompt': """[00:00-00:03] MEDIUM CLOSE-UP: spokesperson looking at bill. 
    Push-in camera. Dramatic lighting. Sharp focus.
    
    AUDIO: urgent voice, fast pace, frustrated emotion. Says: "I was 
    paying $120 a month for car insurance until I found a link that 
    changed everything." Background music: electronic, 140 BPM, builds.
    
    TEXT OVERLAYS: At 0:02, crash-in: "$120 A MONTH?!" (Impact, 130pt, 
    red with black outline). Fades out at 0:05.
    
    TECHNICAL: 4K resolution, 1792x1024, urgent style, vibrant grade, 
    cinematic audio mix.""",
    'size': '1792x1024',
    'seconds': '12'
}

response = requests.post(base_url, headers=headers, json=params, timeout=30)
response.raise_for_status()
data = response.json()

job_id = data['id']
status = data['status']  # 'queued' or 'processing'
print(f"Job created: {job_id}, Status: {status}")
```

**Response**:
```json
{
  "id": "vid_abc123",
  "status": "queued",
  "model": "sora-2-pro",
  "size": "1792x1024",
  "seconds": "12",
  "progress": 0,
  "created_at": 1697500000
}
```

#### 12.3.2 Check Video Status

**Purpose**: Poll for completion

**Endpoint**: `https://api.openai.com/v1/videos/{video_id}`

**Request**:
```python
video_id = 'vid_abc123'
response = requests.get(f"{base_url}/{video_id}", headers=headers)
response.raise_for_status()
status_data = response.json()

print(f"Status: {status_data['status']}")
print(f"Progress: {status_data.get('progress', 0)}%")
```

**Response**:
```json
{
  "id": "vid_abc123",
  "status": "completed",
  "progress": 100,
  "model": "sora-2-pro",
  "completed_at": 1697501200,
  "download_url": "https://cdn.openai.com/videos/vid_abc123.mp4"
}
```

**Status Values**:
- `queued`: Waiting to start
- `processing`: Currently generating (progress 0-99%)
- `completed`: Ready to download
- `failed`: Error occurred

#### 12.3.3 Download Video

**Purpose**: Retrieve generated video

**Request**:
```python
download_url = status_data['download_url']
video_response = requests.get(download_url, headers=headers, stream=True)
video_response.raise_for_status()

output_path = 'scene_01.mp4'
with open(output_path, 'wb') as f:
    for chunk in video_response.iter_content(chunk_size=8192):
        f.write(chunk)

print(f"Video saved to: {output_path}")
```

#### 12.3.4 Polling Strategy

**Implementation**:
```python
def wait_for_completion(video_id, poll_interval=15):
    """Poll until video is complete"""
    print(f"Monitoring job {video_id}...")
    
    while True:
        response = requests.get(
            f"{base_url}/{video_id}", 
            headers=headers
        )
        status_data = response.json()
        
        if status_data['status'] == 'completed':
            print(f"✓ Job {video_id} completed!")
            return status_data
        elif status_data['status'] == 'failed':
            print(f"✗ Job {video_id} failed: {status_data.get('error')}")
            raise Exception(f"Video generation failed")
        else:
            progress = status_data.get('progress', 0)
            print(f"  Progress: {progress}% [{status_data['status']}]")
            time.sleep(poll_interval)
```

**Recommended Poll Interval**: 15 seconds

**Typical Generation Time**: 
- 12-second clip: ~2-3 minutes
- Full ad (5 scenes): ~15-20 minutes

### 12.4 Rate Limits & Costs

#### 12.4.1 OpenAI (GPT-4o)

| Resource | Limit |
|----------|-------|
| Tokens Per Minute | 10,000 TPM |
| Requests Per Minute | 500 RPM |
| Cost (Input) | $2.50 / 1M tokens |
| Cost (Output) | $10.00 / 1M tokens |

**Estimated Cost per Ad**:
- AI Director: ~$0.15 (4 variants × $0.03/scene × 5 scenes / 4)
- Marketing Validator: ~$0.10 (4 variants × $0.025)
- **Total**: ~$0.25 per complete ad generation

#### 12.4.2 Google Gemini (2.5 Flash)

| Resource | Limit |
|----------|-------|
| Requests Per Minute | 60 RPM |
| Video Upload Size | 2GB max |
| Cost (Free Tier) | 15 requests/min |
| Cost (Paid) | $0.02 per analysis |

**Estimated Cost**: $0.02 per video analysis

#### 12.4.3 Sora (2 Pro)

| Resource | Cost |
|----------|------|
| Cost Per Second | $0.32/second |
| Resolution | 1792x1024 (max) |
| Duration | 12 seconds (max) |

**Estimated Cost per Ad**:
- 1 scene: 12s × $0.32 = $3.84
- 5 scenes: 5 × $3.84 = $19.20
- 4 variants: 4 × $19.20 = **$76.80**

**Total Cost per Complete Ad**: ~$77 (Sora dominates costs)

### 12.5 Error Handling

#### 12.5.1 OpenAI Errors

```python
from openai import OpenAI, RateLimitError, APIError

try:
    response = client.chat.completions.create(...)
except RateLimitError as e:
    print(f"Rate limit hit: {e}")
    # Wait and retry with exponential backoff
    time.sleep(60)
except APIError as e:
    print(f"API error: {e}")
    # Log and notify
```

#### 12.5.2 Gemini Errors

```python
try:
    response = model.generate_content(...)
except Exception as e:
    if "quota" in str(e).lower():
        print("Quota exceeded")
    elif "timeout" in str(e).lower():
        print("Request timed out - video too large")
    else:
        print(f"Gemini error: {e}")
```

#### 12.5.3 Sora Errors

```python
try:
    response = requests.post(base_url, headers=headers, json=params)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if response.status_code == 429:
        print("Rate limit exceeded")
    elif response.status_code == 400:
        print("Invalid prompt - check length and format")
    elif response.status_code == 500:
        print("Sora service error")
    raise
```

### 12.6 Best Practices

1. **Batching**: Generate multiple scenes in parallel (not sequential)
2. **Retry Logic**: Exponential backoff for rate limits
3. **Timeout Handling**: Set reasonable timeouts (30s for requests, 15s polls)
4. **Prompt Caching**: Cache AI Director/Validator prompts to reduce tokens
5. **Progress Tracking**: Update UI with real-time status from all APIs
6. **Cost Monitoring**: Log token usage and video generation times

---

## 13. Appendix

### 13.1 Example Prompts

#### AI Director System Prompt (Excerpt)
```
You are an expert Ad Director specializing in high-converting social 
media ads for Sora 2 Pro.

Your job: Transform video analysis into COMPLETE scene specifications with:
- Visual storytelling (camera angles, movements, lighting)
- Audio design (voiceover tone, music genre/BPM, SFX timing)
- Text overlays (exact text, timing, position, style, animation)
- Beat synchronization (sync drops with moments and text reveals)

Each scene must be 12 seconds with arc: HOOK → BUILD → PEAK → RESOLVE.
```

#### Marketing Validator System Prompt (Excerpt)
```
You are a Marketing Expert and Technical Validator for Sora 2 Pro video ads.

Your mission: Analyze AI-generated ad scenes and optimize for:
1. CONVERSION RATE - Make ads that actually convert
2. CHARACTER CONSISTENCY - Prevent Sora hallucination issues
3. TECHNICAL COMPLIANCE - Ensure Sora 2 Pro compatibility

CRITICAL RULES:
1. Scene 1 ONLY: Spokesperson/character can appear
2. Scenes 2-4+: MUST be B-roll (no people, no faces)
3. Scene 5 (CTA): Optional spokesperson OR B-roll
```

### 13.2 Sample Output

**Input Video**: Auto insurance ad, 35 seconds

**Output**:
- 4 variants generated (soft, medium, aggressive, ultra)
- Each variant: 5 scenes × 12s = 60s video
- Conversion scores: Soft (6/10), Medium (7/10), Aggressive (7/10), Ultra (8/10)
- Character consistency: 100% (scene 1 only)
- Text overlays: Dynamically extracted ("$120 A MONTH?!", "$39 A MONTH", "CLICK BELOW")

### 13.3 Troubleshooting

**Issue**: Gemini analysis timeout
**Solution**: Video too large. Compress or split into segments.

**Issue**: Sora generation fails
**Solution**: Check prompt length (<2000 chars) and validation report.

**Issue**: Character hallucination in scene 3
**Solution**: Marketing validator should catch this. If not, review scene_type enforcement.

**Issue**: Text overlays not appearing
**Solution**: Check AI Director output - ensure text_overlays array is populated.

---

## 14. Conclusion

The AI Director Ad Generation System represents a complete reimagining of ad production using dual-AI architecture. By combining OpenAI's creative capabilities with structured validation, the system produces high-quality, conversion-optimized video ads at scale.

**Key Differentiators**:
1. **Fully Dynamic**: No hardcoded templates or patterns
2. **AI-Powered**: OpenAI handles both generation and validation
3. **Conversion-Focused**: Marketing analysis ensures quality
4. **Technically Sound**: Prevents Sora hallucination issues

**Replication Guidance**:
Follow the implementation order (Section 9.2), adhere to the data contracts (Section 5), and ensure both AI Director and Marketing Validator are properly configured with their system prompts.

---

**End of PRD**

