"""
Prompt Validator
Validates Sora prompts before API submission
"""
from typing import Dict, List, Tuple
import re


class PromptValidator:
    """Validates prompts for common issues before sending to Sora"""
    
    # Sora 2 Pro limitations
    MAX_PROMPT_LENGTH = 2000  # Sora 2 Pro prompt length limit (increased from base Sora)
    MAX_CHARACTER_DESC = 150  # Character description should be concise
    MAX_TEXT_OVERLAYS = 5  # Maximum text overlays per scene for readability
    MAX_AUDIO_CUES = 10  # Maximum audio cues per scene
    
    # Contradictory emotion pairs
    CONTRADICTORY_EMOTIONS = [
        ('frustrated', 'excited'),
        ('calm', 'explosive'),
        ('gentle', 'confrontational'),
        ('relaxed', 'urgent'),
        ('thoughtful', 'impulsive')
    ]
    
    # Required elements for character scenes
    CHARACTER_REQUIRED = [
        'camera',
        'duration',
        'style'
    ]
    
    # Forbidden words in B-roll (people references)
    BROLL_FORBIDDEN = [
        'person', 'people', 'man', 'woman', 'face', 'character',
        'spokesperson', 'actor', 'he ', 'she ', 'human', 'individual'
    ]

    def __init__(self):
        self.warnings = []
        self.errors = []

    def validate_prompt(self, prompt: str, scene_info: Dict) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a single prompt
        
        Args:
            prompt: The prompt text
            scene_info: Scene metadata (has_character, purpose, etc.)
        
        Returns:
            Tuple of (is_valid, warnings, errors)
        """
        self.warnings = []
        self.errors = []
        
        # Check length
        self._check_length(prompt)
        
        # Check for contradictory emotions
        self._check_emotions(prompt)
        
        # Check structure based on type
        if scene_info.get('has_character', True):
            self._validate_character_prompt(prompt)
        else:
            self._validate_broll_prompt(prompt)
        
        # Check for required elements
        self._check_required_elements(prompt, scene_info)
        
        # Sora 2 Pro specific checks
        self._check_text_overlays(prompt)
        self._check_audio_timing(prompt)
        self._check_shot_transitions(prompt)
        
        # No errors = valid
        is_valid = len(self.errors) == 0
        
        return is_valid, self.warnings.copy(), self.errors.copy()

    def _check_length(self, prompt: str):
        """Check if prompt is within length limits"""
        length = len(prompt)
        
        if length > self.MAX_PROMPT_LENGTH:
            self.errors.append(
                f"Prompt too long: {length} chars (max: {self.MAX_PROMPT_LENGTH}). "
                "Condense descriptions."
            )
        elif length > self.MAX_PROMPT_LENGTH * 0.8:
            self.warnings.append(
                f"Prompt near limit: {length} chars (max: {self.MAX_PROMPT_LENGTH}). "
                "Consider condensing."
            )

    def _check_emotions(self, prompt: str):
        """Check for contradictory emotions"""
        prompt_lower = prompt.lower()
        
        for emotion1, emotion2 in self.CONTRADICTORY_EMOTIONS:
            if emotion1 in prompt_lower and emotion2 in prompt_lower:
                self.errors.append(
                    f"Contradictory emotions detected: '{emotion1}' and '{emotion2}'. "
                    "Use single coherent emotion."
                )

    def _validate_character_prompt(self, prompt: str):
        """Validate character scene prompt"""
        # Check for character description
        if not any(indicator in prompt.lower() for indicator in ['female', 'male', 'person', 'age']):
            self.warnings.append("No clear character description found. Add age, gender, key traits.")
        
        # Check for camera direction
        if not any(word in prompt.lower() for word in ['camera', 'shot', 'dolly', 'push', 'pan']):
            self.warnings.append("No camera direction specified. Add camera movement for visual interest.")
        
        # Check for script/voiceover
        if '"' not in prompt:
            self.warnings.append("No quoted script found. Include dialogue for clarity.")

    def _validate_broll_prompt(self, prompt: str):
        """Validate B-roll scene prompt"""
        # Check for forbidden people references
        prompt_lower = prompt.lower()
        found_people_refs = []
        
        for forbidden in self.BROLL_FORBIDDEN:
            if forbidden in prompt_lower:
                found_people_refs.append(forbidden)
        
        if found_people_refs:
            self.errors.append(
                f"B-roll contains people references: {', '.join(found_people_refs)}. "
                "B-roll must have NO people visible (Sora limitation)."
            )
        
        # Check for visual storytelling
        if not any(word in prompt_lower for word in ['visual', 'show', 'reveal', 'camera', 'footage']):
            self.warnings.append("Limited visual storytelling. Add more cinematic description.")

    def _check_required_elements(self, prompt: str, scene_info: Dict):
        """Check for required structural elements"""
        prompt_lower = prompt.lower()
        
        # Duration
        if 'duration' not in prompt_lower and '12 second' not in prompt_lower:
            self.warnings.append("No duration specified. Add 'Duration: 12 seconds'.")
        
        # Style
        if 'style' not in prompt_lower:
            self.warnings.append("No style specified. Add visual style description.")
        
        # Quality
        if 'quality' not in prompt_lower and '4k' not in prompt_lower:
            self.warnings.append("No quality specified. Add '4K' or quality descriptor.")

    def _check_text_overlays(self, prompt: str):
        """Check text overlay count and formatting (Sora 2 Pro)"""
        # Count text overlay instructions
        text_count = prompt.lower().count('text ')
        text_count += prompt.lower().count('overlay')
        text_count += len(re.findall(r'at \d+:\d+.*?:.*?".*?"', prompt, re.IGNORECASE))
        
        if text_count > self.MAX_TEXT_OVERLAYS:
            self.errors.append(
                f"Too many text overlays: {text_count} (max: {self.MAX_TEXT_OVERLAYS}). "
                "Reduce text for readability."
            )
        
        # Check for proper text timing format
        text_timings = re.findall(r'at (\d+:\d+)', prompt, re.IGNORECASE)
        for timing in text_timings:
            parts = timing.split(':')
            if len(parts) == 2:
                mins, secs = int(parts[0]), int(parts[1])
                if mins > 0 or secs > 12:
                    self.errors.append(
                        f"Invalid text timing: {timing}. Must be within 0:00-0:12 range."
                    )

    def _check_audio_timing(self, prompt: str):
        """Check audio cues don't overlap (Sora 2 Pro)"""
        # Extract all audio timings
        audio_timings = re.findall(r'(?:at|from|start) (\d+:\d+)', prompt, re.IGNORECASE)
        
        if len(audio_timings) > self.MAX_AUDIO_CUES:
            self.warnings.append(
                f"Many audio cues: {len(audio_timings)}. May sound cluttered."
            )
        
        # Check for realistic timing (simplified check)
        times = []
        for timing in audio_timings:
            parts = timing.split(':')
            if len(parts) == 2:
                mins, secs = int(parts[0]), int(parts[1])
                total_secs = mins * 60 + secs
                times.append(total_secs)
        
        # Check for very close timings (< 1 second apart)
        times.sort()
        for i in range(len(times) - 1):
            if times[i+1] - times[i] < 1:
                self.warnings.append(
                    f"Audio cues very close together ({times[i]}s and {times[i+1]}s). "
                    "May sound rushed."
                )

    def _check_shot_transitions(self, prompt: str):
        """Check shot transitions are logical (Sora 2 Pro)"""
        # Look for jarring transitions
        jarring_patterns = [
            (r'extreme close-up.*extreme close-up', 'Two extreme close-ups in sequence'),
            (r'whip pan.*whip pan', 'Multiple whip pans in sequence'),
            (r'crash zoom.*crash zoom', 'Multiple crash zooms in sequence')
        ]
        
        prompt_lower = prompt.lower()
        for pattern, warning_msg in jarring_patterns:
            if re.search(pattern, prompt_lower):
                self.warnings.append(
                    f"Potentially jarring transition: {warning_msg}. "
                    "Vary shot types for better flow."
                )

    def validate_all_prompts(self, prompts: List[Dict]) -> Dict:
        """
        Validate all prompts for a variant
        
        Args:
            prompts: List of prompt dictionaries
        
        Returns:
            Validation report dictionary
        """
        report = {
            'total_prompts': len(prompts),
            'valid': 0,
            'invalid': 0,
            'warnings_count': 0,
            'errors_count': 0,
            'scene_reports': []
        }
        
        for i, prompt_data in enumerate(prompts, 1):
            prompt = prompt_data.get('prompt', '')
            scene_info = {
                'has_character': prompt_data.get('has_character', True),
                'purpose': prompt_data.get('purpose', '')
            }
            
            is_valid, warnings, errors = self.validate_prompt(prompt, scene_info)
            
            scene_report = {
                'scene_number': i,
                'valid': is_valid,
                'warnings': warnings,
                'errors': errors,
                'prompt_length': len(prompt)
            }
            
            report['scene_reports'].append(scene_report)
            
            if is_valid:
                report['valid'] += 1
            else:
                report['invalid'] += 1
            
            report['warnings_count'] += len(warnings)
            report['errors_count'] += len(errors)
        
        return report

    def print_report(self, report: Dict):
        """Print validation report in human-readable format"""
        print("\n" + "="*70)
        print("PROMPT VALIDATION REPORT")
        print("="*70)
        print(f"\nTotal Prompts: {report['total_prompts']}")
        print(f"✓ Valid: {report['valid']}")
        print(f"✗ Invalid: {report['invalid']}")
        print(f"⚠ Total Warnings: {report['warnings_count']}")
        print(f"✗ Total Errors: {report['errors_count']}")
        
        for scene_report in report['scene_reports']:
            scene_num = scene_report['scene_number']
            status = "✓ VALID" if scene_report['valid'] else "✗ INVALID"
            
            print(f"\n--- Scene {scene_num} [{status}] ---")
            print(f"Prompt Length: {scene_report['prompt_length']} chars")
            
            if scene_report['warnings']:
                print("\n⚠ Warnings:")
                for warning in scene_report['warnings']:
                    print(f"  - {warning}")
            
            if scene_report['errors']:
                print("\n✗ Errors:")
                for error in scene_report['errors']:
                    print(f"  - {error}")
        
        print("\n" + "="*70)


# Test function
if __name__ == "__main__":
    validator = PromptValidator()
    
    # Test bad prompt
    bad_prompt = """A person with frustrated, explosive, confrontational emotion speaking.
    
    The person is in a room. They talk about insurance."""
    
    # Test good prompt
    good_prompt = """Female, 25, brown hair, white tee, home office.

Confident delivery: "I was paying $120 a month..."

Steady camera dolly-in. Direct eye contact.

Style: UGC testimonial
Quality: 4K
Duration: 12 seconds"""

    print("Testing BAD prompt:")
    is_valid, warnings, errors = validator.validate_prompt(
        bad_prompt,
        {'has_character': True, 'purpose': 'hook'}
    )
    print(f"Valid: {is_valid}")
    print(f"Warnings: {warnings}")
    print(f"Errors: {errors}")
    
    print("\n" + "="*70 + "\n")
    
    print("Testing GOOD prompt:")
    is_valid, warnings, errors = validator.validate_prompt(
        good_prompt,
        {'has_character': True, 'purpose': 'hook'}
    )
    print(f"Valid: {is_valid}")
    print(f"Warnings: {warnings}")
    print(f"Errors: {errors}")

