"""
Test AI Director system
"""
import json
from modules.ad_director import AdDirector
from modules.sora_prompt_composer import SoraPromptComposer


def test_ai_director():
    print("=" * 70)
    print("TESTING AI DIRECTOR SYSTEM")
    print("=" * 70)
    
    # Mock Gemini analysis
    mock_analysis = {
        'script': {
            'full_transcript': 'I was paying $120 a month for car insurance until I found a link that changed everything. After a quick two-minute check, I qualified for $39 a month. Same coverage, way less money. Click below to check if you qualify.'
        },
        'vertical': 'auto_insurance',
        'key_moments': [
            {'timestamp': '00:03', 'description': 'frustrated with high price'},
            {'timestamp': '00:07', 'description': 'reveals low price $39'},
            {'timestamp': '00:11', 'description': 'confident recommendation'}
        ],
        'spokesperson': {
            'description': 'female, mid-20s, casual home setting, energetic'
        }
    }
    
    # Mock variant data
    mock_variant = {
        'variant_level': 'aggressive',
        'variant_name': 'Aggressive Variant',
        'modified_scenes': [
            {
                'scene_number': 1,
                'timestamp': '00:00-00:12',
                'type': 'character',
                'emotion': 'frustrated → hopeful',
                'setting': 'modern home',
                'has_character': True
            },
            {
                'scene_number': 2,
                'timestamp': '00:12-00:24',
                'type': 'b-roll',
                'visual_description': 'phone screen with insurance comparison',
                'mood': 'confident',
                'has_character': False
            }
        ]
    }
    
    # Initialize components
    print("\nInitializing AI Director...")
    director = AdDirector()
    composer = SoraPromptComposer()
    
    # Generate scenes with AI Director
    print("\n🎬 AI Director generating scenes...\n")
    try:
        director_scenes = director.generate_scene_structure(
            gemini_analysis=mock_analysis,
            variant_data=mock_variant,
            aggression_level='aggressive'
        )
        
        print(f"\n✅ AI Director generated {len(director_scenes)} scenes")
        print("\nScene Structure:")
        print(json.dumps(director_scenes, indent=2))
        
        # Convert to Sora prompts
        print("\n\n" + "=" * 70)
        print("CONVERTING TO SORA PROMPTS")
        print("=" * 70 + "\n")
        
        sora_prompts = composer.compose_from_director_scenes(director_scenes)
        
        for i, prompt_data in enumerate(sora_prompts, 1):
            print(f"\n{'=' * 70}")
            print(f"SCENE {i}: {prompt_data.get('purpose', 'N/A')}")
            print(f"{'=' * 70}")
            print(f"\nType: {prompt_data.get('scene_type')}")
            print(f"Timestamp: {prompt_data.get('timestamp')}")
            print(f"\nFULL SORA PROMPT:")
            print("-" * 70)
            print(prompt_data['prompt'])
            print("-" * 70)
            print(f"\nFeatures:")
            print(f"  Audio: {'✓' if prompt_data.get('has_audio') else '✗'}")
            print(f"  Text Overlays: {'✓' if prompt_data.get('has_text') else '✗'} ({prompt_data.get('text_count', 0)} overlays)")
            print(f"  Length: {len(prompt_data['prompt'])} characters")
        
        # Save output
        with open('test_ai_director_output.json', 'w') as f:
            json.dump({
                'director_scenes': director_scenes,
                'sora_prompts': sora_prompts
            }, f, indent=2)
        
        print("\n\n" + "=" * 70)
        print("✅ TEST COMPLETE!")
        print("Output saved to: test_ai_director_output.json")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_ai_director()

