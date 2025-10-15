"""
Add Active Pipeline Settings to Supabase
Adds OpenAI prompts and transformer configs currently in use
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(str(Path(__file__).parent.parent))

from modules.settings_manager import get_settings_manager

def add_active_settings():
    """Add all active pipeline settings"""
    manager = get_settings_manager()

    print("Adding Active Pipeline Settings to Supabase...\n")

    # 1. OpenAI Prompt: Custom Hook Generator (from sora_transformer.py lines 359-487)
    hook_generator_prompt = """You are a master ad director creating EXTREME VISUAL HOOKS for a {vertical} advertisement.

ORIGINAL AD CONTEXT:
- Script: {script}
- Problem: {problem}
- Solution: {solution}

REFERENCE: Here are PROVEN EXTREME HOOKS that convert like crazy. Study these patterns and apply them to {vertical}:

EXTREME HOOKS - CAR INSURANCE (Pattern: Physical Danger + Slow Motion Drama):
1. "Junkyard Magnet Drop" → Car dangles under crane magnet, swaying ominously. Metal clanks. Magnet releases. Car drops in SLOW MOTION, crashes violently into scrap pile. Dust explodes. Text: "If your car went today, would your insurance pay tomorrow?"

2. "Falling Tree Storm" → Dashcam POV during storm. Massive tree CRACKS and falls toward windshield in slow motion. Crashes down, missing hood by inches. Branches scrape roof. Text: "Coverage you hope you never need—until you do."

3. "Flying Mattress Highway" → Highway dashcam. Truck ahead loses mattress. It lifts like a sail in slow motion, tumbles end-over-end through air. Flies directly at camera, fills entire screen. Text: "Not your fault. Still your problem."

4. "Pothole Explosion" → Dashcam driving. Massive pothole hidden by water. Front tire SLAMS in. Everything shakes violently. Tire explodes. Rim hits pavement sparking. Text: "One hole, $1,200 later. Or zero if you're covered."

EXTREME HOOKS - HEALTH (Pattern: Anxiety Build + Shocking Reveal):
1. "Hospital Bill Stack" → Medical bill on desk. Another bill floats down, lands on top. Then another. Then 5 more. Stack grows taller. Papers sliding off. Final shot: MASSIVE pile covering entire desk, bills falling to floor. Text: "One visit can bury you. Or it won't."

2. "Ambulance Ride POV" → Ceiling POV from gurney inside racing ambulance. Paramedic working overhead. Siren blaring. Red lights flashing. Everything shaking from speed. Medical equipment swaying. Heart monitor beeping FAST. Text: "Hope is not a plan."

PATTERN ANALYSIS - What Makes These Work:
✓ REALISTIC SCENARIOS: Things that could ACTUALLY happen (not CGI metaphors)
✓ PHYSICAL OBJECTS: Real cars, trees, panels, meters - not abstract concepts
✓ SLOW MOTION IMPACT: Key crash/explosion moments stretched for drama
✓ ENVIRONMENTAL CHAOS: Tangible, visceral destruction you can see/hear
✓ SPECIFIC SOUND DESIGN: Exact audio cues (metal clanks, crash boom, tire screech)
✓ NO PEOPLE: Only environments, objects, vehicles, weather, disasters
✓ TEXT OVERLAY: Punchy question/statement that bridges to solution

CRITICAL RULES FOR REALISM - READ CAREFULLY:
❌ BAD (Too Abstract): "Credit card floating on fire" - objects don't float, fire is symbolic
❌ BAD (Too Metaphorical): "Bills turning into chains" - bills don't transform into objects
❌ BAD (Too Surreal): "Debt monster emerging from wallet" - fantasy creatures don't exist
❌ BAD (CGI Effects): "Screen bursting into sparks" - screens crack, they don't explode
❌ BAD (Physics Defying): "House sinking into mud" - houses don't sink like quicksand

✅ GOOD (Grounded Reality): "Mailbox overflowing with bills, spilling onto ground" - actually happens
✅ GOOD (Physical Drama): "Tow truck hooking onto car, lifting it up and driving away" - real repossession
✅ GOOD (Natural Event): "Hailstorm denting car hood, windshield cracking" - real weather damage
✅ GOOD (Mechanical Failure): "Solar panel sliding off roof, crashing to ground" - real installation failure
✅ GOOD (Real Transaction): "Credit card getting declined at checkout scanner" - happens every day

THINK: Would this actually happen if you filmed it with a camera? Or would it need CGI/special effects?
- Tow truck taking car = REAL (just film it)
- Bills flying off table = REAL (wind machine)
- Screen exploding into sparks = FAKE (needs VFX)
- House sinking into mud = FAKE (needs CGI)

TASK: Create 3 EXTREME VISUAL HOOK scenarios for {vertical} (12 seconds, NO PEOPLE - environments/objects only).

Your hooks MUST be:
1. REALISTIC - Could actually happen in real life (not CGI metaphors)
2. PHYSICAL - Real objects interacting (cars, buildings, weather, machines)
3. GROUNDED - Tangible scenarios viewers can relate to
4. DRAMATIC - Slow motion, sound design, visceral impact
5. RELEVANT - Directly connected to {vertical} problem from script
6. NO PEOPLE - Only environments, objects, vehicles, natural disasters

For each hook, provide:
- name: Short catchy name
- visual: Detailed 2-3 sentence visual description (NO PEOPLE)
- camera: Camera movement and angles
- emotion: Emotional impact (2-3 words)
- text_overlay: One impactful sentence
- beat_breakdown: Timing breakdown (0-4s, 4-8s, 8-12s)
- audio: Sound design description
- lighting: Lighting style
- type: shock_and_relief, everyday_chaos, extreme_visual, or creative_metaphor

Return ONLY valid JSON in this exact format:
[
  {
    "name": "Hook Name",
    "visual": "Visual description...",
    "camera": "Camera description...",
    "emotion": "emotion words",
    "text_overlay": "Text overlay message",
    "beat_breakdown": "0-4s: ... 4-8s: ... 8-12s: ...",
    "audio": "Audio description",
    "lighting": "Lighting description",
    "type": "shock_and_relief"
  }
]

Generate 3 hooks using different patterns. Make them DRAMATIC and SPECIFIC to {vertical}."""

    print("1. Creating openai_prompt:hook_generator...")
    manager.create_setting(
        category='openai_prompt',
        key='hook_generator',
        value={'prompt': hook_generator_prompt},
        description='GPT prompt for generating custom extreme hooks for verticals without pre-written scenarios'
    )
    print("   ✓ Created\n")

    # 2. OpenAI Prompt: Creative Script Generator (from sora_transformer.py lines 541-606)
    script_generator_prompt = """You are a master ad copywriter creating INNOVATIVE Scene 2 and Scene 3 scripts for a {vertical} advertisement.

ORIGINAL AD CONTEXT:
- Script: {script}
- Problem: {problem}
- Solution: {solution}

CRITICAL: DO NOT just copy the original script. Create NEW, CREATIVE variations!

Scene 1 (already done): Extreme visual hook with NO PEOPLE
Scene 2 (YOU CREATE): Actor delivering SOCIAL PROOF / SOLUTION angle
Scene 3 (YOU CREATE): Actor delivering URGENT CTA

SCENE 2 REQUIREMENTS (12 seconds):
- Actor speaking directly to camera
- Focus on: Social proof, testimonial-style, "I tried this and..."
- Angle options:
  * "I was skeptical until..." (transformation story)
  * "Everyone in my neighborhood switched..." (FOMO)
  * "My [friend/parent/coworker] told me about this..." (word of mouth)
  * "I saved [specific amount] in [timeframe]..." (concrete results)
- Make it conversational, authentic, relatable
- 2-3 sentences max (12 second read)

SCENE 3 REQUIREMENTS (12 seconds):
- Actor speaking directly to camera
- Focus on: URGENT call to action
- Angle options:
  * Deadline urgency: "Ends midnight tonight..."
  * Scarcity: "Only 47 spots left in [area]..."
  * Fear of missing out: "Don't be the last one on your block..."
  * Easy action: "One 5-minute call. That's it."
  * Risk reversal: "Free quote. No commitment. See for yourself."
- Create urgency + lower friction
- End with clear action step
- 2-3 sentences max (12 second read)

EXAMPLES OF GOOD SCENE 2 SCRIPTS:
- "I ignored it for months. Then my neighbor showed me his bill — $40/month. Mine was still $240. I switched the next day."
- "My daughter kept telling me to check. Finally I did. Saved $1,800 this year. Wish I'd done it sooner."
- "Everyone on my street has solar now. I was the holdout. Not anymore."

EXAMPLES OF GOOD SCENE 3 SCRIPTS:
- "This offer ends at midnight. Don't wait like I did. One call, five minutes. That's all it takes."
- "They're only taking 50 new customers this month. I got in just in time. You still can too."
- "Free quote. No salesperson showing up. Just see your savings. What are you waiting for?"

Return ONLY valid JSON in this exact format:
[
  {
    "scene_number": 2,
    "purpose": "social_proof",
    "script": "Actor's spoken words for Scene 2...",
    "visual_direction": "Brief visual note (e.g., 'Confident, nodding', 'Showing phone with app')",
    "emotion": "emotion keywords"
  },
  {
    "scene_number": 3,
    "purpose": "urgent_cta",
    "script": "Actor's spoken words for Scene 3...",
    "visual_direction": "Brief visual note (e.g., 'Pointing at camera', 'Holding up fingers for countdown')",
    "emotion": "emotion keywords"
  }
]

Generate Scene 2 and Scene 3 scripts. Make them CREATIVE and DIFFERENT from the original ad!"""

    print("2. Creating openai_prompt:scene_script_generator...")
    manager.create_setting(
        category='openai_prompt',
        key='scene_script_generator',
        value={'prompt': script_generator_prompt},
        description='GPT prompt for generating creative Scene 2-3 scripts (social proof + CTA)'
    )
    print("   ✓ Created\n")

    # 3. Transformer: Hook Scenarios (from sora_transformer.py lines 15-187)
    hook_scenarios = {
        'auto_insurance': [
            {
                'name': 'Junkyard Magnet Drop',
                'visual': 'A car dangles under a massive crane magnet in a junkyard, swaying ominously. Metal clanks echo. Camera tilts up showing the height, then the magnet releases. Car drops in slow motion, crashes violently into pile of scrap metal. Dust and debris explode.',
                'camera': 'Wide establishing shot of junkyard, tilt up to dangling car, slow-motion drop, impact close-up',
                'emotion': 'shock, tension, relief',
                'text_overlay': 'If your car went today, would your insurance pay tomorrow?',
                'beat_breakdown': '0-4s: Car dangles and sways. 4-8s: Release and fall begins. 8-12s: Impact and aftermath.',
                'audio': 'Metal creaking, wind, cables releasing, crash boom, silence',
                'lighting': 'Dramatic overcast sky, harsh industrial lighting',
                'type': 'shock_and_relief'
            },
            {
                'name': 'Falling Tree Storm',
                'visual': 'Dashcam POV during heavy storm. Windshield wipers going full speed. Suddenly a massive tree cracks and falls toward the windshield in slow motion. It crashes down, missing the hood by mere inches. Branches scrape the roof.',
                'camera': 'Fixed dashcam POV, slight shake from wind, slow-motion tree fall',
                'emotion': 'fear, near-miss relief',
                'text_overlay': 'Coverage you hope you never need—until you do.',
                'beat_breakdown': '0-3s: Driving in storm. 3-7s: Tree cracking sound. 7-12s: Tree falling and near-miss.',
                'audio': 'Heavy rain, wipers, tree crack, crash, gasping breath',
                'lighting': 'Dark storm clouds, lightning flash illuminates tree',
                'type': 'shock_and_relief'
            },
            {
                'name': 'Parking Lot Domino Chaos',
                'visual': "Bird's eye view of crowded parking lot. SUV door swings open hard, hits adjacent car. That car's alarm goes off, startles driver who backs into another car. Chain reaction of 4-5 cars bumping, alarms blaring, people running.",
                'camera': 'Drone overhead shot, smooth tracking of chaos spreading',
                'emotion': 'chaos, anxiety, overwhelming',
                'text_overlay': "Accidents don't ask permission.",
                'beat_breakdown': '0-3s: Peaceful parking lot. 3-6s: Door swing impact. 6-12s: Domino effect unfolds.',
                'audio': 'Peaceful ambient, door slam, first alarm, multiple alarms layering, shouting',
                'lighting': 'Bright daytime, harsh parking lot concrete',
                'type': 'everyday_chaos'
            },
            {
                'name': 'Runaway Shopping Cart Tesla',
                'visual': 'Supermarket parking lot. Shopping cart sits on slight incline. Wind gust pushes it. Cart slowly rolls, gaining speed downhill. Camera follows cart racing faster and faster. SLAM into parked Tesla. Owner walks out of store, sees it, gasps and freezes.',
                'camera': 'Wide shot establishing incline, tracking shot following cart, close-up of impact, reaction shot',
                'emotion': 'anticipation, impact shock, dread',
                'text_overlay': 'One slip, one claim, one call away.',
                'beat_breakdown': '0-3s: Cart starts rolling. 3-8s: Cart gains speed. 8-10s: Impact. 10-12s: Owner reaction.',
                'audio': 'Cart wheels rattling, wind, speed whoosh, metal crash, gasp',
                'lighting': 'Sunny parking lot, clean bright aesthetic',
                'type': 'shock_and_relief'
            }
        ],
        'health_insurance': [
            {
                'name': 'Hospital Bill Stack Growing',
                'visual': 'Medical bill on desk. Another bill floats down and lands on top. Then another. Then 5 more. Stack grows taller and taller. Papers start sliding off. Final shot: massive pile of bills covering entire desk, some falling to floor.',
                'camera': 'Top-down shot of desk, bills falling in slow motion, final zoom out',
                'emotion': 'stress, financial anxiety, overwhelming',
                'text_overlay': "One visit can bury you. Or it won't.",
                'beat_breakdown': '0-4s: First few bills. 4-8s: Avalanche of bills. 8-12s: Massive pile reveal.',
                'audio': 'Paper rustling, bills hitting desk (getting louder), avalanche of paper',
                'lighting': 'Office fluorescent, stark and cold',
                'type': 'shock_and_relief'
            },
            {
                'name': 'Prescription Counter Shock',
                'visual': 'Person at pharmacy counter. Pharmacist scans prescription. Cash register display shows amount: $1,247.00. Camera zooms into the number. Person\'s hand trembles reaching for wallet. They pull out empty wallet. Freeze on shocked face.',
                'camera': 'Over-shoulder at counter, close-up of display, reaction shot',
                'emotion': 'shock, financial panic, helpless',
                'text_overlay': '$1,247 for one month. Or $25.',
                'beat_breakdown': '0-4s: Normal pickup. 4-7s: Price reveal. 7-12s: Shock and realization.',
                'audio': 'Pharmacy ambient, beep of scanner, cash register ding, gasp',
                'lighting': 'Bright pharmacy fluorescent, sterile white',
                'type': 'everyday_chaos'
            }
        ],
        'fitness': [
            {
                'name': 'Gym Membership Burning Money',
                'visual': 'Gym membership card on table. $50 bill next to it. Hands holding lighter. Card gets swiped (transaction sound). $50 bill LIGHTS ON FIRE and burns. Another swipe, another bill burns. Montage of burning money each month. Pile of ash grows.',
                'camera': 'Top-down product shot, close-up of fire, ash pile reveal',
                'emotion': 'waste, regret, financial loss',
                'text_overlay': '$600/year. Burned. Never went.',
                'beat_breakdown': '0-4s: Setup. 4-8s: Montage of burning. 8-12s: Ash pile and regret.',
                'audio': 'Card swipe beep, lighter flick, fire crackling, repeated monthly',
                'lighting': 'Dramatic dark background, fire glow',
                'type': 'creative_metaphor'
            }
        ]
    }

    print("3. Creating transformer:hook_scenarios...")
    manager.create_setting(
        category='transformer',
        key='hook_scenarios',
        value=hook_scenarios,
        description='Pre-written extreme hook scenarios by vertical (auto_insurance, health_insurance, fitness)'
    )
    print("   ✓ Created\n")

    # 4. Transformer: Location Pools (from sora_transformer.py lines 189-233)
    location_pools = {
        'auto_insurance': [
            'Inside a modern car, driver seat, parked in bright daylight',
            'At a gas station, standing next to car, casual outdoor setting',
            'Inside a car repair shop, cars in background',
            'Home driveway, standing next to car, suburban setting',
            'Inside dealership showroom, new cars visible in background'
        ],
        'health_insurance': [
            'Modern medical office waiting room, clean and professional',
            'Pharmacy counter, medicine shelves in background',
            'Home kitchen, healthy lifestyle setting',
            'Doctor office, professional but warm setting',
            'Gym or fitness center, health-conscious environment'
        ],
        'finance': [
            'Home office with laptop, financial documents visible',
            'Coffee shop with laptop, casual professional setting',
            'Modern bank interior, professional atmosphere',
            'Home living room, comfortable and relatable',
            'Co-working space, modern professional environment'
        ],
        'fitness': [
            'Home workout space, exercise equipment visible',
            'Gym locker room, casual athletic setting',
            'Outdoor park, active lifestyle environment',
            'Kitchen preparing healthy meal, wellness focus',
            'Yoga studio or fitness class setting'
        ],
        'ecommerce': [
            'Inside bright supermarket or retail store, shopping',
            'Home living room with product, unboxing setting',
            'Outside storefront, shopping bags in hand',
            'Home office desk with product, review setup',
            'Kitchen or bedroom using product, lifestyle shot'
        ],
        'saas': [
            'Professional home office, laptop and monitors visible',
            'Modern office space, tech company vibe',
            'Coffee shop with laptop, remote work setting',
            'Co-working space, startup atmosphere',
            'Home desk setup, productivity focused'
        ]
    }

    print("4. Creating transformer:location_pools...")
    manager.create_setting(
        category='transformer',
        key='location_pools',
        value=location_pools,
        description='Location settings for actor scenes by vertical'
    )
    print("   ✓ Created\n")

    # 5. Transformer: Camera Angles (from sora_transformer.py lines 235-242)
    camera_angles = [
        'Phone mounted at eye level, intimate selfie-style angle',
        'Webcam angle from laptop, professional but approachable',
        'Phone held at arm\'s length, casual vlog style',
        'Tripod setup, slightly off-center for authenticity',
        'Over-the-shoulder perspective transitioning to direct camera'
    ]

    print("5. Creating transformer:camera_angles...")
    manager.create_setting(
        category='transformer',
        key='camera_angles',
        value={'angles': camera_angles},
        description='Camera angle presets for actor scene variety'
    )
    print("   ✓ Created\n")

    # 6. Transformer: Pattern Interrupts (from sora_prompt_builder.py lines 13-36)
    pattern_interrupts = {
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

    print("6. Creating transformer:pattern_interrupts...")
    manager.create_setting(
        category='transformer',
        key='pattern_interrupts',
        value=pattern_interrupts,
        description='Pattern interrupt visuals for character scene hooks by vertical'
    )
    print("   ✓ Created\n")

    print("="*70)
    print("✅ All 6 active pipeline settings added successfully!")
    print("="*70)

if __name__ == "__main__":
    add_active_settings()
