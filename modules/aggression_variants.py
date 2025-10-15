"""
Aggression Variation Generator
Generates 4 variations of the same ad with different aggression levels
"""
import json
from pathlib import Path
from typing import Dict, List
from config import Config


class AggressionVariantGenerator:
    """Generates variations of ads with different aggression/energy levels"""

    def __init__(self):
        """Load aggression presets"""
        presets_path = Config.TEMPLATES_DIR / 'aggression_presets.json'
        with open(presets_path, 'r') as f:
            self.presets = json.load(f)

    def generate_variants(self, analysis: Dict) -> List[Dict]:
        """
        Generate 4 aggression variants from analysis

        Args:
            analysis: Gemini analysis dictionary

        Returns:
            List of 4 variant dictionaries
        """
        variants = []

        for level in ['soft', 'medium', 'aggressive', 'ultra']:
            preset = self.presets[level]
            variant = self._create_variant(analysis, level, preset)
            variants.append(variant)

        return variants

    def _create_variant(self, analysis: Dict, level: str, preset: Dict) -> Dict:
        """
        Create a single variant by applying aggression preset to analysis

        Args:
            analysis: Original analysis
            level: Aggression level name
            preset: Preset configuration

        Returns:
            Variant dictionary with modified scenes
        """
        # Copy base analysis
        variant = {
            'variant_level': level,
            'variant_name': preset['name'],
            'variant_description': preset['description'],
            'original_analysis': analysis,
            'modified_scenes': []
        }

        # Modify each scene with aggression parameters
        for scene in analysis.get('scene_breakdown', []):
            modified_scene = self._modify_scene(scene, preset, level)
            variant['modified_scenes'].append(modified_scene)

        # Add global style modifications
        variant['global_style'] = {
            'lighting': preset['lighting'],
            'music': preset['music'],
            'color_palette': preset['color_palette'],
            'transitions': preset['transitions'],
            'energy_level': preset['energy_level']
        }

        return variant

    def _modify_scene(self, scene: Dict, preset: Dict, level: str) -> Dict:
        """
        Modify a single scene with aggression preset

        Args:
            scene: Original scene dictionary
            preset: Aggression preset
            level: Aggression level name (soft, medium, aggressive, ultra)

        Returns:
            Modified scene dictionary
        """
        modified = scene.copy()

        # Apply preset modifications
        modified['aggression_modifiers'] = {
            'lighting': preset['lighting'],
            'tone': preset['tone'],
            'pacing': preset['pacing'],
            'camera_movement': preset['camera_movement'],
            'energy_level': preset['energy_level'],
            'emotion_keywords': preset['emotion_keywords']
        }

        # Modify emotion based on aggression level
        original_emotion = scene.get('emotion', '')
        modified['emotion'] = self._adjust_emotion(original_emotion, preset['emotion_keywords'], level)

        return modified

    def _adjust_emotion(self, original_emotion: str, emotion_keywords: List[str], aggression_level: str = 'medium') -> str:
        """
        Adjust emotion description based on aggression level with coherent mapping

        Args:
            original_emotion: Original emotion from analysis
            emotion_keywords: Keywords for this aggression level
            aggression_level: The aggression level (soft, medium, aggressive, ultra)

        Returns:
            Coherent single emotion phrase (no contradictions)
        """
        # Map base emotions to aggression-appropriate versions
        emotion_map = {
            'soft': {
                'frustrated': 'thoughtfully concerned',
                'excited': 'pleasantly surprised',
                'urgent': 'gently insistent',
                'confident': 'calmly assured',
                'worried': 'quietly concerned',
                'determined': 'steadily focused'
            },
            'medium': {
                'frustrated': 'determined to help',
                'excited': 'confidently enthusiastic',
                'urgent': 'focused and direct',
                'confident': 'professionally assured',
                'worried': 'actively addressing',
                'determined': 'purposefully driven'
            },
            'aggressive': {
                'frustrated': 'fed up and taking action',
                'excited': 'fired up with energy',
                'urgent': 'intensely driven',
                'confident': 'boldly assertive',
                'worried': 'urgently concerned',
                'determined': 'fiercely committed'
            },
            'ultra': {
                'frustrated': 'explosively candid',
                'excited': 'wildly enthusiastic',
                'urgent': 'relentlessly compelling',
                'confident': 'unshakably bold',
                'worried': 'dramatically alarmed',
                'determined': 'unstoppably fierce'
            }
        }
        
        # Extract base emotion from original
        original_lower = original_emotion.lower()
        base_emotion = None
        
        for base in emotion_map.get(aggression_level, {}).keys():
            if base in original_lower:
                base_emotion = base
                break
        
        # Return mapped emotion or use first aggression keyword
        if base_emotion and aggression_level in emotion_map:
            return emotion_map[aggression_level][base_emotion]
        
        # Fallback to primary emotion keyword
        return emotion_keywords[0] if emotion_keywords else 'confident'

    def save_variants(self, variants: List[Dict], base_filename: str = None) -> List[str]:
        """
        Save all variants to JSON files

        Args:
            variants: List of variant dictionaries
            base_filename: Optional base filename

        Returns:
            List of saved file paths
        """
        saved_paths = []

        for variant in variants:
            level = variant['variant_level']
            filename = f"{base_filename}_{level}.json" if base_filename else f"variant_{level}.json"
            filepath = Config.ANALYSIS_DIR / filename

            with open(filepath, 'w') as f:
                json.dump(variant, f, indent=2)

            saved_paths.append(str(filepath))
            print(f"Saved {variant['variant_name']}: {filepath}")

        return saved_paths

    def get_variant_summary(self, variant: Dict) -> str:
        """
        Get a human-readable summary of a variant

        Args:
            variant: Variant dictionary

        Returns:
            Summary string
        """
        return f"""
{variant['variant_name'].upper()}
{'-' * 50}
Description: {variant['variant_description']}
Energy Level: {variant['global_style']['energy_level']}
Lighting: {variant['global_style']['lighting']}
Music: {variant['global_style']['music']}
Scenes: {len(variant['modified_scenes'])}
        """.strip()


# Test function
if __name__ == "__main__":
    from gemini_analyzer import GeminiVideoAnalyzer

    # Example: Load an analysis and generate variants
    analysis_path = input("Enter path to analysis JSON (or press Enter to analyze new video): ")

    if analysis_path and Path(analysis_path).exists():
        with open(analysis_path, 'r') as f:
            analysis = json.load(f)
    else:
        video_path = input("Enter path to video file: ")
        analyzer = GeminiVideoAnalyzer()
        analysis, _ = analyzer.analyze_and_save(video_path)

    # Generate variants
    generator = AggressionVariantGenerator()
    variants = generator.generate_variants(analysis)

    # Print summaries
    print("\n" + "="*50)
    print("GENERATED VARIANTS")
    print("="*50)
    for variant in variants:
        print(generator.get_variant_summary(variant))
        print()

    # Save variants
    saved_paths = generator.save_variants(variants, base_filename="ad_variant")
    print(f"\nSaved {len(saved_paths)} variants")
