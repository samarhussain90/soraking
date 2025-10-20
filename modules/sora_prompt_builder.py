"""
Sora Prompt Builder - OPTIMIZED FOR CONVERSIONS
Builds concise, cinematic prompts with proven UGC formulas
"""
from typing import Dict, List
import re


class SoraPromptBuilder:
    """Builds high-converting Sora 2 prompts with cinematic storytelling"""

    def __init__(self):
        # Pattern interrupts for character scenes
        self.pattern_interrupts = {
            'auto_insurance': [
                'Phone screen showing ${amount}/month bill notification',
                'Insurance renewal letter landing on desk',
                'Calculator showing yearly cost total',
                'Frustrated expression checking phone bill'
            ],
            'health_insurance': [
                'Medical bill stack on counter',
                'Prescription cost receipt close-up',
                'Health insurance card being held up'
            ],
            'finance': [
                'Bank app showing savings balance',
                'Credit score notification on phone',
                'Investment portfolio chart rising'
            ],
            'default': [
                'Phone notification appearing',
                'Document being revealed',
                'Expressive reaction shot'
            ]
        }

    def build_scene_prompt(self, scene: Dict, variant: Dict, spokesperson_description: str, full_script: str) -> str:
        """
        Build a single scene prompt

        Args:
            scene: Scene dictionary from transformation
            variant: Variant configuration
            spokesperson_description: Full spokesperson description from Gemini
            full_script: COMPLETE script/transcript from original ad

        Returns:
            Complete Sora prompt string
        """
        # Check scene type - RESTORE ORIGINAL CHARACTER SCENES
        scene_type = scene.get('type', 'character')

        # CHARACTER SCENES (restored original approach)
        if scene.get('has_character', True):
            return self._build_character_prompt(scene, variant, spokesperson_description, full_script)
        # B-ROLL SCENES (fallback)
        else:
            return self._build_broll_prompt(scene, variant, full_script)

    def _build_character_prompt(self, scene: Dict, variant: Dict, spokesperson_desc: str, script: str) -> str:
        """
        Build ORIGINAL character scene with detailed prompt structure

        Formula: DETAILED VISUAL + CHARACTER + MESSAGE + TECHNICAL SPECS
        """
        # Extract essentials
        vertical = scene.get('vertical', 'default')
        emotion = scene.get('emotion', 'confident')
        aggression = variant.get('variant_level', 'medium')

        # Use original script (restore original approach)
        actor_script = script
        print(f"  ✓ Using original script for Scene {scene.get('scene_number')}")

        # Get character description
        char_desc = spokesperson_desc

        # Get scene details
        setting = scene.get('setting', 'modern home office, soft lighting')
        shot_type = scene.get('shot_type', 'medium close-up')
        camera_angle = scene.get('camera_angle', 'eye-level')
        camera_movement = scene.get('camera_movement', 'dynamic push-in')
        lighting = scene.get('lighting', 'dramatic, bold shadows')
        visual_elements = scene.get('visual_elements', [])
        visual_direction = scene.get('visual_direction', '')

        # Build DETAILED prompt like the original
        prompt_parts = []

        # 1. VISUAL SETUP
        prompt_parts.append(f"{shot_type.upper()}: {char_desc}, {setting}.")
        
        # 2. CAMERA WORK
        prompt_parts.append(f"{camera_movement.capitalize()} camera, {camera_angle} angle.")
        
        # 3. LIGHTING
        prompt_parts.append(f"{lighting.capitalize()} lighting.")
        
        # 4. CHARACTER SPEAKING
        prompt_parts.append(f'\n{emotion.capitalize()} tone: "{actor_script}"')
        
        # 5. VISUAL ELEMENTS
        if visual_elements:
            elements_str = ', '.join(visual_elements)
            prompt_parts.append(f'\nVisual elements: {elements_str}.')
        
        # 6. VISUAL DIRECTION
        if visual_direction:
            prompt_parts.append(f'\nVisual direction: {visual_direction}.')
        
        # 7. TECHNICAL SPECS
        prompt_parts.append(f'\nEye contact with camera. Natural gestures. UGC testimonial style.')
        prompt_parts.append(f'4K resolution, cinematic quality, 12 seconds.')

        prompt = ''.join(prompt_parts)

        return prompt

    def _build_hook_scenario_prompt(self, scene: Dict, variant: Dict, script: str) -> str:
        """
        Build EXTREME HOOK SCENARIO prompt with detailed visual storytelling

        Formula: VISUAL DRAMA (0-12s) with precise timing, camera work, and audio
        Uses beat_breakdown for exact timing
        NO PEOPLE - Pure visual shock value
        """
        # Extract scenario details
        visual = scene.get('visual_description', '')
        camera = scene.get('camera_movement', 'Smooth cinematic movement')
        emotion = scene.get('emotion', 'shock')
        text_overlay = scene.get('text_overlay', '')
        beat_breakdown = scene.get('beat_breakdown', '')
        audio = scene.get('audio_design', 'Dramatic sound design')
        lighting = scene.get('lighting', 'Cinematic lighting')
        scenario_name = scene.get('scenario_name', 'Hook')
        aggression = variant.get('variant_level', 'medium')

        # Adjust intensity based on aggression level
        intensity_modifiers = {
            'soft': 'Smooth and controlled',
            'medium': 'Dynamic and impactful',
            'aggressive': 'Intense and visceral',
            'ultra': 'Extreme high-impact'
        }
        intensity = intensity_modifiers.get(aggression, 'Dynamic and impactful')

        # Build ULTRA-DETAILED prompt for maximum visual impact
        prompt = f"""EXTREME VISUAL HOOK: {visual}

NO PEOPLE. Environment and object-focused cinematography only.

CAMERA: {camera}. {intensity} movement.

TIMING: {beat_breakdown}

LIGHTING: {lighting}. Cinematic color grading.

AUDIO DESIGN: {audio}. Build tension to impact.

TEXT OVERLAY (appears mid-scene): "{text_overlay}"

EMOTION: {emotion}. Maximum visual impact.

SHOT STYLE: Cinematic commercial. High production value. Dramatic reveals.

4K cinematic. 12 seconds. {scenario_name}."""

        return prompt

    def _build_broll_prompt(self, scene: Dict, variant: Dict, script: str) -> str:
        """
        Build cinematic B-roll with visual storytelling
        
        Formula: ESTABLISHING (0-3s) → METAPHOR (3-8s) → PAYOFF (8-12s)
        """
        # Get B-roll details
        visual_desc = scene.get('visual_description', 'cinematic footage')
        broll_type = scene.get('broll_type', 'generic')
        mood = scene.get('mood', 'professional')
        aggression = variant.get('variant_level', 'medium')
        
        # Camera style based on aggression
        camera_styles = {
            'soft': 'Smooth glides',
            'medium': 'Steady tracking',
            'aggressive': 'Dynamic shots',
            'ultra': 'Intense rushes'
        }
        camera_style = camera_styles.get(aggression, 'Steady')
        
        # Build CONCISE cinematic B-roll prompt
        # Note: Avoid using forbidden words (person, face, character) even in instructions
        prompt = f"""{visual_desc}

Environment-only shots. {broll_type} visuals: vehicles, objects, documents, settings.

{camera_style}. Mood: {mood}. Cinematic grade.

Voiceover: "{script}"

Symbolic storytelling through objects/environment only.

4K cinematic. 12s."""

        return prompt

    def _condense_character(self, full_description: str) -> str:
        """
        Condense character description to essentials (<80 chars)
        
        Extract: age, gender, key visual traits, clothing
        """
        desc_lower = full_description.lower()
        
        # Extract age
        age_match = re.search(r'(\d+)[-\s]?(to|-)?\s?(\d+)?', full_description)
        if age_match:
            age = age_match.group(1) if not age_match.group(3) else f"{age_match.group(1)}-{age_match.group(3)}"
        else:
            # Try to extract age descriptors
            if 'early to mid-20' in desc_lower or '20s' in desc_lower:
                age = '25'
            elif 'early 30' in desc_lower or '30s' in desc_lower:
                age = '30'
            else:
                age = '30'
        
        # Extract gender
        if 'female' in desc_lower or 'woman' in desc_lower:
            gender = 'female'
        elif 'male' in desc_lower or 'man' in desc_lower:
            gender = 'male'
        else:
            gender = 'person'
        
        # Extract hair
        hair = ''
        if 'brown hair' in desc_lower:
            hair = 'brown hair'
        elif 'blonde' in desc_lower or 'blond' in desc_lower:
            hair = 'blonde hair'
        elif 'black hair' in desc_lower:
            hair = 'black hair'
        elif 'wavy' in desc_lower:
            hair = 'wavy hair'
        elif 'curly' in desc_lower:
            hair = 'curly hair'
        
        # Extract clothing
        clothing = ''
        if 'white t-shirt' in desc_lower or 'white tee' in desc_lower:
            clothing = 'white tee'
        elif 'casual' in desc_lower:
            clothing = 'casual outfit'
        
        # Construct concise description
        parts = [gender, age]
        if hair:
            parts.append(hair)
        if clothing:
            parts.append(clothing)
        
        return ', '.join(parts)

    def build_all_scene_prompts(self, variant: Dict, spokesperson_description: str, full_script: str) -> List[Dict]:
        """
        Build prompts for all scenes in a variant

        Args:
            variant: Variant dictionary with modified_scenes
            spokesperson_description: Spokesperson description from analysis
            full_script: Complete script/transcript

        Returns:
            List of dictionaries with scene info and prompt
        """
        prompts = []
        scenes = variant['modified_scenes']
        
        # Split script intelligently by scene purposes
        script_parts = self._split_script_intelligently(full_script, scenes)

        for i, scene in enumerate(scenes):
            # Get appropriate script segment
            script_segment = script_parts[i] if i < len(script_parts) else full_script
            
            # Build prompt
            prompt = self.build_scene_prompt(
                scene,
                variant,
                spokesperson_description,
                script_segment
            )

            prompts.append({
                'scene_number': scene.get('scene_number'),
                'timestamp': scene.get('timestamp'),
                'purpose': scene.get('purpose'),
                'prompt': prompt,
                'script_segment': script_segment,
                'has_character': scene.get('has_character', True)
            })

        return prompts

    def _split_script_intelligently(self, script: str, scenes: List[Dict]) -> List[str]:
        """
        Split script by scene purposes (hook, problem, solution, CTA)
        
        Aligns script segments with narrative beats
        """
        # Split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', script.strip())
        
        if len(scenes) == 1:
            # For Scene 1 only, extract just the opening hook (first 1-2 sentences)
            sentences = re.split(r'(?<=[.!?])\s+', script.strip())
            # Take only the first 1-2 sentences for the hook
            hook_sentences = sentences[:2] if len(sentences) >= 2 else sentences[:1]
            return [' '.join(hook_sentences)]
        
        # Map scene purposes to script segments
        parts = []
        scene_purposes = [s.get('purpose', '') for s in scenes]
        
        # Distribute sentences based on purpose
        sentences_per_scene = len(sentences) // len(scenes)
        remainder = len(sentences) % len(scenes)
        
        idx = 0
        for i, purpose in enumerate(scene_purposes):
            # Allocate more sentences to hook and CTA scenes
            if 'hook' in purpose.lower() or 'cta' in purpose.lower():
                count = sentences_per_scene + 1
            else:
                count = sentences_per_scene
            
            # Add remainder to early scenes
            if i < remainder:
                count += 1
            
            scene_sentences = sentences[idx:idx+count]
            parts.append(' '.join(scene_sentences))
            idx += count
        
        # Handle any remaining sentences
        if idx < len(sentences):
            parts[-1] += ' ' + ' '.join(sentences[idx:])
        
        return parts

    def format_for_sora_api(self, prompt_data: Dict) -> Dict:
        """Format prompt data for Sora API call"""
        from config import Config

        return {
            'model': Config.SORA_MODEL,
            'prompt': prompt_data['prompt'],
            'size': Config.SORA_RESOLUTION,
            'seconds': Config.SORA_DURATION
        }
