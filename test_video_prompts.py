"""
Test: Generate AI Director prompts for a specific video
"""
import json
from pathlib import Path
from modules.gemini_analyzer import GeminiVideoAnalyzer
from modules.sora_transformer import SoraAdTransformer
from modules.aggression_variants import AggressionVariantGenerator
from modules.ad_director import AdDirector
from modules.sora_prompt_composer import SoraPromptComposer


def test_video_prompts(video_path: str, variant: str = 'aggressive'):
    print("=" * 70)
    print(f"TESTING AI DIRECTOR PROMPTS FOR: {video_path}")
    print("=" * 70)
    
    # Check if analysis already exists
    video_name = Path(video_path).stem
    analysis_file = f"output/analysis/analysis_{video_name}.json"
    
    if Path(analysis_file).exists():
        print(f"\n✓ Found existing analysis: {analysis_file}")
        with open(analysis_file, 'r') as f:
            analysis = json.load(f)
    else:
        print(f"\n🔍 Analyzing video with Gemini...")
        analyzer = GeminiVideoAnalyzer()
        analysis = analyzer.analyze_video(video_path)
        
        # Save analysis
        Path("output/analysis").mkdir(parents=True, exist_ok=True)
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"✓ Analysis saved to: {analysis_file}")
    
    # Transform for Sora
    print(f"\n🔄 Transforming ad structure for Sora...")
    transformer = SoraAdTransformer()
    analysis = transformer.transform_ad(analysis)
    
    # Generate variants
    print(f"\n📊 Generating aggression variants...")
    variant_gen = AggressionVariantGenerator()
    all_variants = variant_gen.generate_variants(analysis)
    
    # Get requested variant
    selected_variant = next((v for v in all_variants if v['variant_level'] == variant), all_variants[0])
    print(f"✓ Selected variant: {selected_variant['variant_name']}")
    
    # Use AI Director
    print(f"\n🎬 AI Director generating scenes...")
    director = AdDirector()
    director_scenes = director.generate_scene_structure(
        gemini_analysis=analysis,
        variant_data=selected_variant,
        aggression_level=variant
    )
    
    print(f"\n✓ AI Director generated {len(director_scenes)} scenes")
    
    # Convert to Sora prompts
    print(f"\n📝 Converting to Sora prompts...")
    composer = SoraPromptComposer()
    sora_prompts = composer.compose_from_director_scenes(director_scenes)
    
    # Display results
    print("\n" + "=" * 70)
    print("GENERATED SORA PROMPTS")
    print("=" * 70)
    
    for i, prompt_data in enumerate(sora_prompts, 1):
        print(f"\n{'=' * 70}")
        print(f"SCENE {i}: {prompt_data.get('purpose', 'N/A').upper()}")
        print(f"{'=' * 70}")
        print(f"\nType: {prompt_data.get('scene_type')}")
        print(f"Timestamp: {prompt_data.get('timestamp')}")
        print(f"\nFULL SORA PROMPT:")
        print("-" * 70)
        print(prompt_data['prompt'])
        print("-" * 70)
        print(f"\nMetadata:")
        print(f"  • Audio: {'✓' if prompt_data.get('has_audio') else '✗'}")
        print(f"  • Text Overlays: {'✓' if prompt_data.get('has_text') else '✗'} ({prompt_data.get('text_count', 0)} overlays)")
        print(f"  • Length: {len(prompt_data['prompt'])} characters")
    
    # Save output
    output_file = f"test_prompts_{video_name}_{variant}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'video': video_path,
            'variant': variant,
            'script': analysis.get('script', {}).get('full_transcript', ''),
            'vertical': analysis.get('vertical', 'unknown'),
            'director_scenes': director_scenes,
            'sora_prompts': sora_prompts
        }, f, indent=2)
    
    print("\n\n" + "=" * 70)
    print(f"✅ TEST COMPLETE!")
    print(f"Output saved to: {output_file}")
    print("=" * 70 + "\n")
    
    # Show summary
    print("SUMMARY:")
    print(f"  • Video: {video_path}")
    print(f"  • Variant: {variant}")
    print(f"  • Vertical: {analysis.get('vertical', 'unknown')}")
    print(f"  • Script: {analysis.get('script', {}).get('full_transcript', '')[:100]}...")
    print(f"  • Scenes: {len(sora_prompts)}")
    print(f"  • Total prompt length: {sum(len(p['prompt']) for p in sora_prompts)} characters")


if __name__ == '__main__':
    import sys
    
    video_path = sys.argv[1] if len(sys.argv) > 1 else '__pycache__/autoad.mp4'
    variant = sys.argv[2] if len(sys.argv) > 2 else 'aggressive'
    
    test_video_prompts(video_path, variant)

