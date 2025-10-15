#!/usr/bin/env python3
"""
Test the new prompt generation system
"""
import json
from pathlib import Path
from modules.sora_prompt_builder import SoraPromptBuilder
from modules.conversion_optimizer import ConversionOptimizer
from modules.prompt_validator import PromptValidator

def test_prompt_generation():
    """Test the new prompt generation system"""
    
    print("="*70)
    print("TESTING NEW PROMPT GENERATION SYSTEM")
    print("="*70)
    
    # Initialize components
    builder = SoraPromptBuilder()
    optimizer = ConversionOptimizer()
    validator = PromptValidator()
    
    # Create sample scene (character scene for auto insurance hook)
    character_scene = {
        'scene_number': 1,
        'timestamp': '00:00-00:12',
        'duration_seconds': 12,
        'purpose': 'Hook/Problem',
        'has_character': True,
        'vertical': 'auto_insurance',
        'shot_type': 'Medium Shot',
        'setting': 'Modern home office, natural lighting',
        'lighting': 'Soft, even lighting',
        'emotion': 'frustrated',
        'message': 'Introduce problem - paying too much for insurance'
    }
    
    # Create sample B-roll scene
    broll_scene = {
        'scene_number': 2,
        'timestamp': '00:12-00:24',
        'duration_seconds': 12,
        'purpose': 'Problem Agitation',
        'has_character': False,
        'vertical': 'auto_insurance',
        'broll_type': 'problem_visualization',
        'visual_description': 'Car driving on highway, insurance bill visible on dashboard',
        'mood': 'Frustration, concern'
    }
    
    # Sample variant
    variant = {
        'variant_level': 'aggressive',
        'variant_name': 'Aggressive/Urgent',
        'modified_scenes': [character_scene, broll_scene]
    }
    
    # Sample spokesperson description
    spokesperson = "Female in her early to mid-20s with brown wavy hair, white t-shirt, casual appearance"
    
    # Sample script
    script_char = "I was paying $120 a month for car insurance until I found a link that changed everything. After a quick two-minute check, I qualified for $39 a month."
    script_broll = "Same coverage, way less money. Apparently, a new law means drivers insured for over a year could get a lower rate."
    
    print("\n[1/3] BUILDING CHARACTER PROMPT")
    print("-"*70)
    char_prompt = builder._build_character_prompt(character_scene, variant, spokesperson, script_char)
    print(f"Length: {len(char_prompt)} chars")
    print(f"\nPrompt:\n{char_prompt}")
    
    print("\n[2/3] BUILDING B-ROLL PROMPT")
    print("-"*70)
    broll_prompt = builder._build_broll_prompt(broll_scene, variant, script_broll)
    print(f"Length: {len(broll_prompt)} chars")
    print(f"\nPrompt:\n{broll_prompt}")
    
    print("\n[3/3] OPTIMIZING & VALIDATING")
    print("-"*70)
    
    # Optimize character prompt
    optimized_char = optimizer.optimize_prompt(char_prompt, character_scene, variant)
    print(f"\nOptimized Character Prompt Length: {len(optimized_char)} chars")
    
    # Validate character prompt
    is_valid, warnings, errors = validator.validate_prompt(
        optimized_char,
        {'has_character': True, 'purpose': 'Hook/Problem'}
    )
    
    print(f"\n✓ Valid: {is_valid}")
    if warnings:
        print(f"⚠ Warnings: {len(warnings)}")
        for w in warnings:
            print(f"  - {w}")
    if errors:
        print(f"✗ Errors: {len(errors)}")
        for e in errors:
            print(f"  - {e}")
    
    # Validate B-roll prompt
    is_valid_broll, warnings_broll, errors_broll = validator.validate_prompt(
        broll_prompt,
        {'has_character': False, 'purpose': 'Problem'}
    )
    
    print(f"\nB-Roll Valid: {is_valid_broll}")
    if warnings_broll:
        print(f"⚠ Warnings: {len(warnings_broll)}")
    if errors_broll:
        print(f"✗ Errors: {len(errors_broll)}")
        for e in errors_broll:
            print(f"  - {e}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    
    # Success criteria
    success = (
        len(char_prompt) < 500 and  # Should be concise
        len(broll_prompt) < 500 and
        is_valid and  # Should pass validation
        is_valid_broll and
        'frustrated, explosive' not in char_prompt.lower()  # No contradictory emotions
    )
    
    if success:
        print("\n✅ ALL TESTS PASSED!")
        print("- Prompts are concise (< 500 chars)")
        print("- Prompts pass validation")
        print("- No contradictory emotions")
    else:
        print("\n❌ SOME TESTS FAILED")
        if len(char_prompt) >= 500:
            print(f"- Character prompt too long: {len(char_prompt)} chars")
        if len(broll_prompt) >= 500:
            print(f"- B-roll prompt too long: {len(broll_prompt)} chars")
        if not is_valid:
            print("- Character prompt validation failed")
        if not is_valid_broll:
            print("- B-roll prompt validation failed")
    
    return success


if __name__ == "__main__":
    success = test_prompt_generation()
    exit(0 if success else 1)

