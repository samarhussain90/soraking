"""
Test Hook Generation for Debt Vertical
Shows what GPT generates and the final Sora prompt
"""
from modules.sora_transformer import SoraAdTransformer
from modules.sora_prompt_builder import SoraPromptBuilder
import json

# Mock analysis for a debt relief ad
mock_debt_analysis = {
    'video_metadata': {
        'duration_seconds': 36,
        'aspect_ratio': '9:16'
    },
    'spokesperson': {
        'physical_description': 'Male, 35-40, casual business attire',
        'speaking_style': 'Urgent and helpful'
    },
    'script': {
        'full_transcript': 'Are you drowning in credit card debt? Minimum payments not making a dent? There\'s a new federal program that could cut your debt in half. Thousands have already qualified. One simple call could save you tens of thousands. Don\'t wait - this program has limited spots.',
        'call_to_action': 'Call now to see if you qualify'
    },
    'storytelling': {
        'problem_presented': 'Overwhelming credit card debt with high interest rates',
        'solution_offered': 'Federal debt relief program that cuts debt in half',
        'framework': 'Problem-Agitate-Solution'
    }
}

print("=" * 80)
print("TESTING: DEBT VERTICAL HOOK GENERATION")
print("=" * 80)
print()

# Initialize transformer
print("🔧 Initializing transformer with OpenAI...")
transformer = SoraAdTransformer()

# Detect vertical
vertical = transformer.detect_vertical(mock_debt_analysis)
print(f"✓ Detected vertical: {vertical}")
print()

# Generate custom hooks using GPT
print("🤖 Generating custom extreme hooks with GPT...")
print("-" * 80)
custom_hooks = transformer._generate_custom_hooks_with_gpt(mock_debt_analysis, vertical)

print(f"\n✓ Generated {len(custom_hooks)} custom hooks:\n")
for i, hook in enumerate(custom_hooks, 1):
    print(f"\n{'='*80}")
    print(f"HOOK #{i}: {hook['name']}")
    print(f"{'='*80}")
    print(f"\nVISUAL: {hook['visual']}")
    print(f"\nCAMERA: {hook['camera']}")
    print(f"EMOTION: {hook['emotion']}")
    print(f"\nTEXT OVERLAY: \"{hook['text_overlay']}\"")
    print(f"\nBEAT BREAKDOWN: {hook['beat_breakdown']}")
    print(f"AUDIO: {hook['audio']}")
    print(f"LIGHTING: {hook['lighting']}")

# Now build the actual Sora prompt for the first hook
print("\n" + "=" * 80)
print("BUILDING SORA PROMPT FOR HOOK #1")
print("=" * 80)

# Create a mock scene using the first hook
selected_hook = custom_hooks[0]
hook_scene = {
    'scene_number': 1,
    'timestamp': '00:00-00:12',
    'duration_seconds': 12,
    'type': 'extreme_hook',
    'purpose': 'Extreme visual hook - grab attention with shock value',
    'has_character': False,
    'vertical': vertical,
    'scenario_name': selected_hook['name'],
    'visual_description': selected_hook['visual'],
    'camera_movement': selected_hook['camera'],
    'emotion': selected_hook['emotion'],
    'text_overlay': selected_hook['text_overlay'],
    'beat_breakdown': selected_hook['beat_breakdown'],
    'audio_design': selected_hook['audio'],
    'lighting': selected_hook['lighting'],
    'scenario_type': selected_hook.get('type', 'shock_and_relief')
}

# Mock variant data
mock_variant = {
    'variant_level': 'aggressive'
}

# Build the Sora prompt
prompt_builder = SoraPromptBuilder()
sora_prompt = prompt_builder._build_hook_scenario_prompt(
    hook_scene,
    mock_variant,
    mock_debt_analysis['script']['full_transcript']
)

print("\n📝 FINAL SORA PROMPT:")
print("-" * 80)
print(sora_prompt)
print("-" * 80)

print("\n✅ Test complete!")
