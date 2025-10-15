"""
Test Marketing Validation Pipeline
"""
import json
from modules.aggression_variants import AggressionVariantGenerator
from modules.ad_director import AdDirector
from modules.marketing_validator import MarketingValidator
from modules.sora_prompt_composer import SoraPromptComposer


def test_full_pipeline():
    print("=" * 70)
    print("TESTING FULL PIPELINE WITH MARKETING VALIDATION")
    print("=" * 70)
    
    # Load existing analysis
    with open('output/analysis/analysis_20251012_203833.json', 'r') as f:
        analysis = json.load(f)
    
    script = analysis.get('script', {}).get('full_transcript', '')
    vertical = analysis.get('vertical', 'auto_insurance')
    
    print(f"\nScript: {script[:100]}...")
    print(f"Vertical: {vertical}\n")
    
    # Generate variants
    variant_gen = AggressionVariantGenerator()
    all_variants = variant_gen.generate_variants(analysis)
    aggressive_variant = next(v for v in all_variants if v['variant_level'] == 'aggressive')
    
    # Step 1: AI Director
    print("=" * 70)
    print("STEP 1: AI DIRECTOR GENERATES SCENES")
    print("=" * 70)
    director = AdDirector()
    director_scenes = director.generate_scene_structure(
        analysis, aggressive_variant, 'aggressive'
    )
    print(f"\n✓ Generated {len(director_scenes)} scenes\n")
    
    # Show what AI Director created
    for i, scene in enumerate(director_scenes, 1):
        scene_type = scene.get('scene_type', 'unknown')
        purpose = scene.get('purpose', 'unknown')
        has_character = 'character' in scene_type
        print(f"Scene {i}: {purpose} ({scene_type}) {'👤 HAS SPOKESPERSON' if has_character else '📹 B-ROLL'}")
    
    # Step 2: Marketing Validation
    print("\n" + "=" * 70)
    print("STEP 2: MARKETING VALIDATOR REFINES SCENES")
    print("=" * 70)
    validator = MarketingValidator()
    validation_result = validator.validate_and_refine(
        director_scenes=director_scenes,
        script=script,
        vertical=vertical
    )
    
    # Show validation results
    print(f"\n📊 CONVERSION SCORE: {validation_result.get('conversion_score', 0)}/10")
    
    if validation_result.get('issues_found'):
        print(f"\n⚠️  ISSUES FIXED:")
        for issue in validation_result['issues_found']:
            print(f"   - {issue}")
    
    if validation_result.get('marketing_analysis'):
        print(f"\n📈 MARKETING ANALYSIS:")
        analysis_data = validation_result['marketing_analysis']
        for key, value in analysis_data.items():
            print(f"   - {key.replace('_', ' ').title()}: {value}")
    
    if validation_result.get('recommendations'):
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in validation_result['recommendations']:
            print(f"   - {rec}")
    
    # Show refined scenes
    refined_scenes = validation_result.get('refined_scenes', director_scenes)
    print(f"\n✓ Refined {len(refined_scenes)} scenes\n")
    
    for i, scene in enumerate(refined_scenes, 1):
        scene_type = scene.get('scene_type', 'unknown')
        purpose = scene.get('purpose', 'unknown')
        changes = scene.get('changes_made', [])
        has_character = 'character' in scene_type
        
        print(f"Scene {i}: {purpose} ({scene_type}) {'👤 SPOKESPERSON' if has_character else '📹 B-ROLL ONLY'}")
        if changes:
            print(f"   Changes: {', '.join(changes)}")
    
    # Step 3: Convert to Sora Prompts
    print("\n" + "=" * 70)
    print("STEP 3: CONVERT TO SORA PROMPTS")
    print("=" * 70)
    composer = SoraPromptComposer()
    sora_prompts = composer.compose_from_director_scenes(refined_scenes)
    
    print(f"\n✓ Generated {len(sora_prompts)} Sora prompts\n")
    
    # Display final prompts
    for i, prompt_data in enumerate(sora_prompts, 1):
        print(f"\n{'=' * 70}")
        print(f"FINAL SCENE {i}: {prompt_data.get('purpose', 'N/A').upper()}")
        print(f"{'=' * 70}")
        print(f"\nType: {prompt_data.get('scene_type')}")
        print(f"\nSora Prompt ({len(prompt_data['prompt'])} chars):")
        print("-" * 70)
        print(prompt_data['prompt'])
        print("-" * 70)
    
    # Save output
    output = {
        'script': script,
        'vertical': vertical,
        'director_scenes': director_scenes,
        'validation_result': validation_result,
        'refined_scenes': refined_scenes,
        'sora_prompts': sora_prompts
    }
    
    with open('test_marketing_validation_output.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 70)
    print("✅ PIPELINE COMPLETE!")
    print("Output saved to: test_marketing_validation_output.json")
    print("=" * 70)
    
    # Summary
    print("\nSUMMARY:")
    print(f"  • Conversion Score: {validation_result.get('conversion_score', 0)}/10")
    print(f"  • Issues Fixed: {len(validation_result.get('issues_found', []))}")
    print(f"  • Scenes: {len(sora_prompts)}")
    print(f"  • Character in Scene 1 Only: {'✓' if refined_scenes[0].get('scene_type') == 'character' else '✗'}")
    print(f"  • B-roll in Scenes 2+: {'✓' if all(s.get('scene_type') != 'character' for s in refined_scenes[1:]) else '✗'}")


if __name__ == '__main__':
    test_full_pipeline()

