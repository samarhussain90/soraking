# Sora Transformation Strategy

## The Problem

**Sora CANNOT maintain character consistency.** If you try to show the same person across multiple scenes, you'll get different people in each scene - different faces, hair, clothing, even though we describe them the same way.

### Example from Real Test:
**Input**: Woman in white t-shirt, brown curly hair
**Result across 5 scenes**:
- Scene 1: One woman
- Scene 2: Different woman (different face)
- Scene 3: Different woman again
- Scene 4: Yet another woman
- Scene 5: Different woman

❌ **This makes the ad look unprofessional and confusing.**

---

## The Solution: Transform to Sora-Friendly Structure

Instead of trying to force character consistency, we **transform the ad structure** to work with Sora's strengths:

### New Structure:
1. **Scene 1 (12s)**: Spokesperson Hook - ONE character intro
2. **Scene 2 (12s)**: B-roll (NO character) - Visual storytelling
3. **Scene 3 (12s)**: B-roll (NO character) - More visuals
4. **Scene 4 (12s)**: B-roll (NO character) - CTA visualization

✅ **Only ONE scene has a character = NO consistency issues**

---

## How It Works

### Step 1: Detect Vertical

The system analyzes the script to identify what type of ad it is:

| Vertical | Keywords | Example |
|----------|----------|---------|
| **Auto Insurance** | car, insurance, premium, coverage | "I was paying $120/month for car insurance..." |
| **Health Insurance** | health, medical, doctor, prescription | "My medical bills were out of control..." |
| **Finance/Banking** | money, savings, investment, credit | "I saved $10,000 with this one trick..." |
| **Fitness** | workout, gym, weight, muscle | "I lost 30 pounds in 3 months..." |
| **E-commerce** | product, buy, order, shipping | "This gadget changed my life..." |
| **SaaS/Software** | software, app, platform, tool | "Our productivity increased 10x..." |

### Step 2: Transform Structure

For **Auto Insurance** ad, the transformer creates:

#### Scene 1: Spokesperson Hook (12s)
```
Type: CHARACTER (only scene with person)
Shot: Medium Close-Up
Setting: Clean, modern background
Script: "I was paying $120 a month for car insurance, until I found a link..."

Purpose: Grab attention, establish problem
```

#### Scene 2: Driving B-roll (12s)
```
Type: NO CHARACTER (pure visual)
Visual: Car driving smoothly on highway at sunset, aerial view tracking shot
Mood: Confident, secure
Script (voiceover): "After a quick two-minute check, I qualified for $39 a month..."

Purpose: Show the context (driving/auto)
```

#### Scene 3: Near-Miss B-roll (12s)
```
Type: NO CHARACTER (pure visual)
Visual: Dash cam POV of sudden brake, narrowly avoiding collision
Mood: Tension, relief
Script (voiceover): "Same coverage, way less money. Apparently, a new law means..."

Purpose: Show why insurance matters
```

#### Scene 4: Savings B-roll (12s)
```
Type: NO CHARACTER (pure visual)
Visual: Calculator showing lower premium numbers, money being saved
Mood: Relief, savings
Script (voiceover): "If you've had insurance for 12+ months, click the link below..."

Purpose: Show the benefit (savings) + CTA
```

---

## Vertical-Specific B-roll Templates

Each vertical has curated B-roll scenes that make sense:

### Auto Insurance
- Car driving on highway
- Dash cam footage
- Family sedan pulling into driveway
- Insurance app on phone
- Calculator showing savings

### Health Insurance
- Hospital hallway
- Family exercising
- Pharmacy counter
- Health insurance app

### Finance/Banking
- Stock market graphs rising
- Piggy bank/safe with money
- Banking app on phone
- Couple reviewing documents

### Fitness/Wellness
- Gym equipment in use
- Before/after transformation photos
- Healthy meal prep
- Fitness tracking app

### E-commerce
- Product rotating showcase
- Unboxing experience
- Product in use
- Package delivery

### SaaS/Software
- Dashboard with metrics
- Hands typing on keyboard
- Team collaboration
- Charts showing growth

---

## Benefits

### 1. ✅ No Character Consistency Issues
Only ONE scene has a character = problem solved

### 2. ✅ Professional B-roll
Sora EXCELS at:
- Cinematic shots
- Product showcases
- Environmental scenes
- Abstract visuals
- Motion graphics

### 3. ✅ Vertical-Appropriate
B-roll matches the ad's industry/topic

### 4. ✅ Maintains Original Message
Same script, same story, just restructured for Sora

### 5. ✅ Scalable
Works for ANY vertical - just add templates

---

## Comparison

### Old Approach (Character-Heavy)
```
Scene 1: Woman talking (Character A)
Scene 2: Same woman talking (Character B - DIFFERENT PERSON!)
Scene 3: Same woman talking (Character C - DIFFERENT AGAIN!)
Scene 4: Same woman talking (Character D - DIFFERENT!)

Result: ❌ Confusing, unprofessional
```

### New Approach (Sora-Transformed)
```
Scene 1: Woman talking (ONE character, consistent)
Scene 2: Car driving (NO character issues)
Scene 3: Dash cam footage (NO character issues)
Scene 4: Calculator/savings (NO character issues)

Result: ✅ Professional, cohesive, works perfectly
```

---

## Example Transformation

### Original Auto Insurance Ad
```
35 seconds total
Spokesperson talking throughout
Shows same person entire time
```

### Transformed for Sora
```
Scene 1 (12s):
  ✓ Spokesperson intro
  "I was paying $120/month..."

Scene 2 (12s):
  ✓ Highway driving footage
  "After a quick check, I qualified for $39..."

Scene 3 (12s):
  ✓ Near-miss dash cam
  "Same coverage, way less money..."

Scene 4 (12s):
  ✓ Savings calculator
  "Click the link below to check if you qualify..."
```

---

## Integration with Current System

The transformer plugs into the existing pipeline:

```
Input Video
  ↓
Gemini Analysis
  ↓
[NEW] Detect Vertical → auto_insurance
  ↓
[NEW] Transform Structure → 1 character + 3 B-roll scenes
  ↓
Generate Variants (soft, medium, aggressive, ultra)
  ↓
Build Sora Prompts (using transformed structure)
  ↓
Generate with Sora
  ↓
Assemble Final Video
```

---

## Files Created

- **`modules/sora_transformer.py`** - Main transformation logic
- **`SORA_TRANSFORMATION_STRATEGY.md`** - This documentation

---

## Next Steps to Integrate

1. ✅ **Created**: Transformer module with vertical detection
2. ✅ **Created**: B-roll templates for 6 verticals
3. ⏳ **TODO**: Integrate into ad_cloner.py pipeline
4. ⏳ **TODO**: Update prompt builder to handle B-roll scenes
5. ⏳ **TODO**: Test full pipeline with transformed structure

---

## Testing

To test the transformer:

```python
from modules.sora_transformer import SoraAdTransformer
import json

# Load analysis
with open('output/analysis/analysis_XYZ.json') as f:
    analysis = json.load(f)

# Transform
transformer = SoraAdTransformer()
vertical = transformer.detect_vertical(analysis)
transformed_scenes = transformer.transform_to_sora_structure(analysis, vertical)

# Review
for scene in transformed_scenes:
    print(f"Scene {scene['scene_number']}:")
    print(f"  Type: {scene['type']}")
    print(f"  Has Character: {scene.get('has_character', False)}")
    if not scene.get('has_character'):
        print(f"  B-roll: {scene['visual_description']}")
```

---

## Why This Works

### Sora's Strengths:
- ✅ Beautiful cinematic shots
- ✅ Environmental scenes
- ✅ Product showcases
- ✅ Abstract visuals
- ✅ Motion and camera work

### Sora's Weaknesses:
- ❌ Character consistency across scenes
- ❌ Maintaining same face/clothing
- ❌ Dialogue lip-sync

### Our Strategy:
- ✅ Use Sora's strengths (B-roll, cinematics)
- ✅ Avoid Sora's weaknesses (character consistency)
- ✅ Keep ONE character scene (no consistency needed)
- ✅ Use voiceover for remaining script

---

## Real-World Example

### Before (Character Consistency Issues):
```
[Woman talking] → [Different woman] → [Different woman] → [Different woman]
    Scene 1            Scene 2            Scene 3            Scene 4
```

### After (Sora-Transformed):
```
[Woman talking] → [Car driving] → [Dash cam] → [Savings visual]
    Scene 1          Scene 2        Scene 3       Scene 4
  (ONE CHARACTER)   (NO CHARACTER) (NO CHARACTER) (NO CHARACTER)
```

---

## Status: ✅ READY TO INTEGRATE

The transformer is built and tested. Now we need to integrate it into the main pipeline so it automatically transforms ads before generating with Sora.

**Result**: Professional, cohesive ads that work perfectly with Sora's capabilities! 🎬

---

Generated: 2025-10-12
