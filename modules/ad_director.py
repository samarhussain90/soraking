"""
AI Ad Director
Uses OpenAI to dynamically generate scene structures and Sora prompts based on Gemini analysis
"""
from openai import OpenAI
from typing import Dict, List
import json
from config import Config


class AdDirector:
    """AI-powered ad director that creates dynamic scene prompts"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = "gpt-4o"  # Use GPT-4o for best reasoning
    
    def generate_scene_structure(
        self,
        gemini_analysis: Dict,
        variant_data: Dict,
        aggression_level: str
    ) -> List[Dict]:
        """
        Use OpenAI as Ad Director to create dynamic scene structure
        
        Args:
            gemini_analysis: Full Gemini video analysis
            variant_data: Variant-specific scene modifications
            aggression_level: soft/medium/aggressive/ultra
            
        Returns:
            List of scene dictionaries with visual, audio, and text specs
        """
        # Extract key info from Gemini analysis
        script = gemini_analysis.get('script', {}).get('full_transcript', '')
        vertical = gemini_analysis.get('vertical', 'general')
        key_moments = gemini_analysis.get('key_moments', [])
        spokesperson = gemini_analysis.get('spokesperson', {}).get('description', '')
        
        # Build director prompt
        director_prompt = self._build_director_prompt(
            script=script,
            vertical=vertical,
            key_moments=key_moments,
            spokesperson=spokesperson,
            variant_scenes=variant_data.get('modified_scenes', []),
            aggression=aggression_level
        )
        
        # Call OpenAI as Ad Director
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self._get_director_system_prompt()
                },
                {
                    "role": "user",
                    "content": director_prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.8  # Creative but consistent
        )
        
        # Parse scenes from response
        result = json.loads(response.choices[0].message.content)
        scenes = result.get('scenes', [])
        
        print(f"  🎬 Ad Director generated {len(scenes)} dynamic scenes")
        
        return scenes
    
    def _get_director_system_prompt(self) -> str:
        """System prompt for Ad Director mode"""
        return """You are an expert Ad Director specializing in high-converting social media ads for Sora 2 Pro.

Your job: Transform video analysis into COMPLETE scene specifications with:
- **Visual storytelling** (camera angles, movements, lighting, composition)
- **Audio design** (voiceover tone, music genre/BPM, sound effects with timing)
- **Text overlays** (exact text, timing, position, style, animation)
- **Beat synchronization** (sync audio drops with visual moments and text reveals)

Each scene must be 12 seconds with a clear arc: HOOK → BUILD → PEAK → RESOLVE.

Output JSON format:
{
  "scenes": [
    {
      "scene_number": 1,
      "timestamp": "00:00-00:12",
      "scene_type": "character" or "b-roll",
      "purpose": "hook/problem/solution/cta",
      
      "visual": {
        "shot_progression": [
          {
            "time": "00:00-00:03",
            "shot_type": "extreme close-up",
            "subject": "description",
            "camera_move": "push-in/whip pan/static/etc",
            "lighting": "high-contrast/warm/dramatic",
            "focus": "sharp/shallow depth"
          }
        ],
        "color_grade": "vibrant/cinematic/natural",
        "energy_level": "urgent/calm/energetic"
      },
      
      "audio": {
        "voiceover": {
          "script": "exact words spoken",
          "tone": "urgent/calm/excited",
          "pace": "fast/medium/slow",
          "emotion": "frustrated/hopeful/confident"
        },
        "music": {
          "genre": "electronic/acoustic/ambient",
          "bpm": 90-160,
          "intensity": "builds/steady/drops",
          "key_moments": ["0:08 climax", "0:11 bass drop"]
        },
        "sound_effects": [
          {"time": "0:03", "effect": "whoosh"},
          {"time": "0:08", "effect": "cha-ching"}
        ]
      },
      
      "text_overlays": [
        {
          "text": "EXACT TEXT IN CAPS",
          "start": "0:02",
          "end": "0:05",
          "position": "top-center/center/lower-third",
          "font": "Bebas Neue/Montserrat Black/Impact",
          "size": "80pt-240pt",
          "color": "red/yellow/white",
          "animation": "crash-in/pop/slide/fade",
          "outline": "black/none"
        }
      ],
      
      "sync_points": [
        {"time": "0:03", "event": "music starts + text pops in"},
        {"time": "0:08", "event": "price reveal + SFX + camera push"}
      ]
    }
  ],
  "overall_strategy": "brief explanation of ad flow"
}

Rules:
1. Extract prices, questions, and CTAs from the script for text overlays
2. Match visual energy to aggression level (soft=90 BPM/calm, ultra=160 BPM/intense)
3. Sync text reveals with audio beats (price appears when mentioned)
4. Use 3-5 text overlays max per scene for readability
5. First scene = character hook, remaining = B-roll or testimonial
6. Make it CONVERSION-FOCUSED: price reveals, urgency, clear CTAs
"""
    
    def _build_director_prompt(
        self,
        script: str,
        vertical: str,
        key_moments: List,
        spokesperson: str,
        variant_scenes: List[Dict],
        aggression: str
    ) -> str:
        """Build the user prompt for the Ad Director"""
        
        # Map aggression to specs
        aggression_specs = {
            'soft': {'bpm_range': '75-95', 'energy': 'calm and friendly', 'text_style': 'gentle fades'},
            'medium': {'bpm_range': '110-130', 'energy': 'engaging and upbeat', 'text_style': 'smooth pops'},
            'aggressive': {'bpm_range': '135-150', 'energy': 'urgent and intense', 'text_style': 'bold crashes'},
            'ultra': {'bpm_range': '155-175', 'energy': 'explosive and extreme', 'text_style': 'massive reveals'}
        }
        
        specs = aggression_specs.get(aggression, aggression_specs['medium'])
        
        prompt = f"""Create a {aggression.upper()} variant ad for {vertical} insurance.

**SCRIPT:**
{script}

**SPOKESPERSON:**
{spokesperson}

**KEY MOMENTS FROM ANALYSIS:**
{json.dumps(key_moments, indent=2) if key_moments else 'No specific moments marked'}

**VARIANT SCENES (from transformer):**
{json.dumps(variant_scenes, indent=2)}

**AGGRESSION SPECS:**
- Energy: {specs['energy']}
- Music BPM: {specs['bpm_range']}
- Text Style: {specs['text_style']}

**YOUR TASK:**
Generate {len(variant_scenes)} complete scenes (12 seconds each) with:

1. **Dynamic Visuals**: Multi-shot progressions, camera moves, lighting shifts
2. **Complete Audio**: Voiceover script (from the transcript), music (genre/BPM/intensity), SFX timing
3. **Bold Text Overlays**: Extract prices, questions, CTAs from script
4. **Perfect Sync**: Text appears when mentioned, SFX on key moments, drops on reveals

Make it scroll-stopping and conversion-focused. Output valid JSON.
"""
        
        return prompt

