"""
Marketing Validator & Prompt Refiner
Validates and optimizes AI Director scenes for conversions and Sora compatibility
"""
from openai import OpenAI
from typing import Dict, List
import json
from config import Config


class MarketingValidator:
    """Validates and refines prompts for conversions and technical requirements"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = "gpt-4o"
    
    def validate_and_refine(
        self,
        director_scenes: List[Dict],
        script: str,
        vertical: str
    ) -> Dict:
        """
        Validate and refine AI Director scenes for:
        1. Character consistency (no spokesperson in scenes 2-4)
        2. Conversion optimization (marketing analysis)
        3. Sora compatibility
        
        Args:
            director_scenes: Scenes from AI Director
            script: Original video script
            vertical: Ad vertical (auto_insurance, etc.)
            
        Returns:
            Dict with refined_scenes and analysis
        """
        
        validation_prompt = self._build_validation_prompt(
            director_scenes, script, vertical
        )
        
        print("  🔍 Marketing Validator analyzing scenes...")
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self._get_validator_system_prompt()
                },
                {
                    "role": "user",
                    "content": validation_prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3  # Lower temp for consistency
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Log findings
        if result.get('issues_found'):
            print(f"  ⚠️  Found {len(result['issues_found'])} issues to fix")
            for issue in result['issues_found']:
                print(f"     - {issue}")
        
        if result.get('conversion_score'):
            print(f"  📊 Conversion Score: {result['conversion_score']}/10")
        
        print(f"  ✅ Refined {len(result.get('refined_scenes', []))} scenes")
        
        return result
    
    def _get_validator_system_prompt(self) -> str:
        """System prompt for marketing validation"""
        return """You are a Marketing Expert and Technical Validator for Sora 2 Pro video ads.

Your mission: Analyze AI-generated ad scenes and optimize for:
1. **CONVERSION RATE** - Make ads that actually convert
2. **CHARACTER CONSISTENCY** - Prevent Sora hallucination issues
3. **TECHNICAL COMPLIANCE** - Ensure Sora 2 Pro compatibility

CRITICAL RULES:
1. **Scene 1 ONLY**: Spokesperson/character can appear
2. **Scenes 2-4+**: MUST be B-roll (no people, no faces, no spokesperson)
   - Environment shots only (phones, websites, UI, products)
   - This prevents Sora from hallucinating different faces
3. **Scene 5 (CTA)**: Can optionally show spokesperson OR keep as B-roll

CONVERSION OPTIMIZATION CHECKLIST:
✅ Hook grabs attention in first 3 seconds
✅ Problem is relatable and urgent
✅ Solution is clear and specific
✅ Social proof or credibility included
✅ Scarcity/urgency creates FOMO
✅ CTA is crystal clear and actionable
✅ Visual hierarchy guides eye to key info
✅ Text overlays are scannable (5 words max)
✅ Pricing shown prominently (before/after)
✅ Beat drops sync with key reveals

TECHNICAL REQUIREMENTS:
- Prompts under 2000 characters
- 3-5 text overlays max per scene
- Clear camera moves (no vague terms)
- Specific lighting descriptions
- Audio timing is realistic

OUTPUT FORMAT:
{
  "conversion_score": 1-10,
  "issues_found": [
    "Scene 2 shows spokesperson - change to B-roll phone screen",
    "Text overlay too long - reduce to 4 words max",
    "Missing urgency in CTA"
  ],
  "marketing_analysis": {
    "hook_strength": "Strong/Medium/Weak",
    "problem_clarity": "Clear/Unclear",
    "solution_appeal": "High/Medium/Low",
    "urgency_level": "High/Medium/Low",
    "cta_effectiveness": "Strong/Medium/Weak"
  },
  "refined_scenes": [
    {
      // Same structure as input, but with fixes applied
      "scene_number": 1,
      "changes_made": ["removed spokesperson from scene 2", "shortened text overlay"],
      // ... rest of scene data
    }
  ],
  "recommendations": [
    "Add scarcity text like 'Limited Time' to scene 3",
    "Sync bass drop with price reveal at 0:18"
  ]
}
"""
    
    def _build_validation_prompt(
        self,
        director_scenes: List[Dict],
        script: str,
        vertical: str
    ) -> str:
        """Build validation prompt"""
        
        return f"""Validate and optimize these AI-generated ad scenes.

**SCRIPT:**
{script}

**VERTICAL:** {vertical}

**AI DIRECTOR SCENES:**
{json.dumps(director_scenes, indent=2)}

**YOUR TASKS:**

1. **CHARACTER CONSISTENCY CHECK:**
   - Scene 1: ✅ Can show spokesperson/character
   - Scenes 2-4: ❌ MUST be B-roll ONLY (no people!)
     * Change any people shots to: phones, screens, websites, products, environments
   - Scene 5 (CTA): Either B-roll OR quick spokesperson (optional)

2. **CONVERSION OPTIMIZATION:**
   - Hook: Does scene 1 grab attention immediately?
   - Problem: Is the pain point clear and relatable?
   - Solution: Is the benefit obvious and compelling?
   - Urgency: Does it create FOMO or time pressure?
   - CTA: Is the action crystal clear?

3. **TEXT OVERLAY AUDIT:**
   - Max 5 words per overlay (scannable)
   - Prices must be HUGE and bold
   - Questions create engagement
   - CTAs are directive ("CLICK NOW", not "you can click")

4. **BEAT SYNC CHECK:**
   - Text appears when mentioned in voiceover
   - SFX on key moments (reveals, buttons)
   - Music drops with visual peaks

**REFINE THE SCENES:**
- Fix character consistency issues (B-roll scenes 2-4)
- Optimize text for conversion
- Ensure perfect audio/visual sync
- Make it scroll-stopping

Return JSON with your analysis and refined scenes.
"""

