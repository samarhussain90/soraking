"""
Test script to verify Sora Prompt Composer
"""
import json
from modules.sora_prompt_composer import SoraPromptComposer

# Mock data
mock_variant = {
    'variant_level': 'aggressive',
    'variant_name': 'Aggressive/Urgent',
    'modified_scenes': [
        {
            'scene_number': 1,
            'timestamp': '00:00-00:12',
            'type': 'actor_hook',
            'purpose': 'Hook with problem',
            'has_character': True,
            'vertical': 'auto_insurance',
            'emotion': 'frustrated',
            'setting': 'modern home office',
            'actor_profile': {
                'description': 'female, mid-20s, wavy hair'
            }
        },
        {
            'scene_number': 2,
            'timestamp': '00:12-00:24',
            'type': 'broll_solution',
            'purpose': 'Show solution',
            'has_character': False,
            'vertical': 'auto_insurance',
            'visual_description': 'Phone screen showing low rate',
            'broll_type': 'solution',
            'mood': 'hopeful'
        }
    ]
}

mock_script = "I was paying $120 a month for car insurance until I found a link that changed everything. After a quick two-minute check, I qualified for $39 a month. Same coverage, way less money. Click below to check if you qualify."

mock_spokesperson = "A female in her early to mid-20s with wavy brown hair, wearing a white t-shirt."

print("="*70)
print("TESTING SORA PROMPT COMPOSER")
print("="*70)

# Initialize composer
composer = SoraPromptComposer()

# Compose prompts
print("\nComposing prompts...")
prompts = composer.compose_full_scene_prompts(
    variant=mock_variant,
    spokesperson=mock_spokesperson,
    script=mock_script,
    vertical='auto_insurance',
    aggression='aggressive'
)

print(f"\n✓ Generated {len(prompts)} scene prompts\n")

# Display prompts
for i, prompt_data in enumerate(prompts, 1):
    print(f"\n{'='*70}")
    print(f"SCENE {i}: {prompt_data['purpose']}")
    print(f"{'='*70}")
    print(f"\nType: {'CHARACTER' if prompt_data['has_character'] else 'B-ROLL'}")
    print(f"Timestamp: {prompt_data['timestamp']}")
    print(f"\nFULL PROMPT:")
    print("-"*70)
    print(prompt_data['prompt'])
    print("-"*70)
    
    # Check features
    has_audio = 'AUDIO:' in prompt_data['prompt']
    has_text = 'TEXT' in prompt_data['prompt']
    has_camera = any(word in prompt_data['prompt'] for word in ['CLOSE-UP', 'PAN', 'ZOOM', 'PUSH'])
    
    print(f"\nFeatures:")
    print(f"  Audio: {'✓' if has_audio else '✗'}")
    print(f"  Text Overlays: {'✓' if has_text else '✗'}")
    print(f"  Dynamic Camera: {'✓' if has_camera else '✗'}")
    print(f"  Length: {len(prompt_data['prompt'])} characters")

# Save to file
output_file = 'test_composer_output.json'
with open(output_file, 'w') as f:
    json.dump(prompts, f, indent=2)

print(f"\n{'='*70}")
print(f"✅ TEST COMPLETE!")
print(f"Output saved to: {output_file}")
print(f"{'='*70}\n")

