"""
Sora Ad Transformer - MULTIPLE ACTORS STRATEGY
Generates ads with DIFFERENT people in each scene (testimonial style)
"""
import json
from typing import Dict, List
from pathlib import Path
from modules.utils import normalize_spokesperson


class SoraAdTransformer:
    """Transforms ads using EXTREME HOOKS + multiple actors"""

    # EXTREME HOOK SCENARIOS by vertical (Scene 1 only - NO PEOPLE)
    # These create SHOCK VALUE and grab attention immediately
    HOOK_SCENARIOS = {
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
                'visual': 'Bird\'s eye view of crowded parking lot. SUV door swings open hard, hits adjacent car. That car\'s alarm goes off, startles driver who backs into another car. Chain reaction of 4-5 cars bumping, alarms blaring, people running.',
                'camera': 'Drone overhead shot, smooth tracking of chaos spreading',
                'emotion': 'chaos, anxiety, overwhelming',
                'text_overlay': 'Accidents don\'t ask permission.',
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
            },
            {
                'name': 'Highway Brake Check Tension',
                'visual': 'Dashcam POV on highway. Car ahead suddenly brake checks hard. Red brake lights fill screen. Driver slams brakes, tires screech. Car behind you can\'t stop - you see them in rearview mirror getting closer. Everyone stops inches apart. Hearts pounding moment.',
                'camera': 'Fixed dashcam front view, quick glance at rearview mirror insert',
                'emotion': 'extreme tension, relief, adrenaline',
                'text_overlay': 'You can\'t predict it. But you can protect it.',
                'beat_breakdown': '0-2s: Normal driving. 2-6s: Brake lights, screeching. 6-12s: Close call, stopped.',
                'audio': 'Engine hum, sudden brake squeal, heavy breathing, silence',
                'lighting': 'Bright highway, harsh brake light red glow',
                'type': 'shock_and_relief'
            },
            {
                'name': 'Car Wash Malfunction Flood',
                'visual': 'Interior car POV during automated car wash. Brushes spinning normally, soap covering windows. Suddenly water pressure spikes - water BURSTS through window seals, flooding the interior. Dashboard, seats soaking. Hands trying to stop it.',
                'camera': 'Interior POV from dashboard, water spray hitting camera, chaotic',
                'emotion': 'surprise, panic, helplessness',
                'text_overlay': 'Comprehensive covers more than you think.',
                'beat_breakdown': '0-4s: Normal wash cycle. 4-7s: Pressure spike. 7-12s: Flooding chaos.',
                'audio': 'Brushes whirring, water spraying, sudden burst, splashing',
                'lighting': 'Colorful soap rainbow, harsh fluorescent wash lights',
                'type': 'everyday_chaos'
            },
            {
                'name': 'Deer Dash Night Vision',
                'visual': 'Night dashcam with infrared. Dark forest road, headlights cutting through darkness. Suddenly eyes reflect in the distance. Deer leaps across road in slow motion, massive antlers silhouetted. Car swerves hard, barely misses. Freeze frame on deer mid-air.',
                'camera': 'Night vision dashcam, slow-motion deer jump, freeze frame',
                'emotion': 'fear, adrenaline, close call',
                'text_overlay': 'Could your policy handle this?',
                'beat_breakdown': '0-4s: Dark driving. 4-8s: Eyes appear, deer jumps. 8-12s: Swerve and freeze.',
                'audio': 'Engine, crickets, sudden hooves, tire screech, heartbeat',
                'lighting': 'Night vision green, headlight beams, eye reflections',
                'type': 'shock_and_relief'
            },
            {
                'name': 'Pothole Explosion',
                'visual': 'Dashcam driving on city street. Massive pothole appears suddenly (hidden by water). Front tire SLAMS into it. Everything shakes violently - camera, dashboard, mirrors. Tire explodes. Rim hits pavement sparking. Car limps to side of road.',
                'camera': 'Dashcam with violent shake effect, close-up of tire damage',
                'emotion': 'sudden impact, frustration, costly damage',
                'text_overlay': 'One hole, $1,200 later. Or zero if you\'re covered.',
                'beat_breakdown': '0-3s: Normal driving. 3-5s: Pothole impact. 5-12s: Shaking, damage, aftermath.',
                'audio': 'Driving sounds, massive BANG, metal scraping, deflating tire hiss',
                'lighting': 'Overcast city, harsh street lighting',
                'type': 'everyday_chaos'
            },
            {
                'name': 'Flying Mattress Highway',
                'visual': 'Highway dashcam. Truck ahead with mattress in bed. Wind catches mattress, it lifts off like a sail in slow motion. Mattress tumbles through air end-over-end. Cars swerving. Mattress flies directly at camera, fills entire screen.',
                'camera': 'Dashcam POV, slow-motion mattress flight, extreme close-up',
                'emotion': 'absurd danger, WTF moment, near miss',
                'text_overlay': 'Not your fault. Still your problem.',
                'beat_breakdown': '0-4s: Following truck. 4-8s: Mattress lifts off. 8-12s: Tumbling toward camera.',
                'audio': 'Highway driving, wind gust, fabric flapping, tires screeching, horn',
                'lighting': 'Bright sunny highway, blue sky contrast',
                'type': 'extreme_visual'
            },
            {
                'name': 'Reverse Time Accident',
                'visual': 'Starts with heavily dented car in driveway - crumpled bumper, broken headlight. Video plays in REVERSE. Dent pops out, glass reforms, car becomes pristine and perfect. Everything rewinds to before the accident.',
                'camera': 'Static shot, reverse time effect, smooth morphing',
                'emotion': 'regret, wishful thinking, hope',
                'text_overlay': 'Wish it worked like this? We\'ll get you close.',
                'beat_breakdown': '0-5s: Damaged car. 5-10s: Reverse effect. 10-12s: Perfect car reveal.',
                'audio': 'Reverse audio effects, glass reforming (backwards), magical chime',
                'lighting': 'Suburban driveway, natural lighting, cinematic color grade',
                'type': 'creative_metaphor'
            }
        ],
        'health_insurance': [
            {
                'name': 'Hospital Bill Stack Growing',
                'visual': 'Medical bill on desk. Another bill floats down and lands on top. Then another. Then 5 more. Stack grows taller and taller. Papers start sliding off. Final shot: massive pile of bills covering entire desk, some falling to floor.',
                'camera': 'Top-down shot of desk, bills falling in slow motion, final zoom out',
                'emotion': 'stress, financial anxiety, overwhelming',
                'text_overlay': 'One visit can bury you. Or it won\'t.',
                'beat_breakdown': '0-4s: First few bills. 4-8s: Avalanche of bills. 8-12s: Massive pile reveal.',
                'audio': 'Paper rustling, bills hitting desk (getting louder), avalanche of paper',
                'lighting': 'Office fluorescent, stark and cold',
                'type': 'shock_and_relief'
            },
            {
                'name': 'Ambulance Ride POV',
                'visual': 'Ceiling POV from gurney inside ambulance. Paramedic working overhead. Siren blaring. Lights flashing red. Everything shaking from speed. Medical equipment swaying. Heart monitor beeping fast. Tunnel vision effect.',
                'camera': 'Looking up from patient perspective, shaky, disorienting',
                'emotion': 'fear, emergency, life or death',
                'text_overlay': 'Hope is not a plan.',
                'beat_breakdown': '0-3s: Loaded into ambulance. 3-9s: Speeding, medical work. 9-12s: Arrival.',
                'audio': 'Sirens wailing, heart monitor beeping, paramedic radio, engine roaring',
                'lighting': 'Harsh medical lights, red emergency flashing',
                'type': 'extreme_visual'
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
            },
            {
                'name': 'Before After Mirror Shock',
                'visual': 'Person standing in front of mirror at gym. Reflection shows them out of shape. They blink. Reflection suddenly changes to fit, muscular version. Blink again - back to current. Blink - fit version. Reality vs. possibility.',
                'camera': 'Mirror POV, smooth transitions between reflections',
                'emotion': 'aspiration, possibility, transformation',
                'text_overlay': '90 days is all it takes.',
                'beat_breakdown': '0-3s: Current reflection. 3-8s: Alternating visions. 8-12s: Final decision.',
                'audio': 'Gym ambience, heartbeat, magical whoosh on transitions',
                'lighting': 'Gym mirror lighting, dramatic when showing fit version',
                'type': 'creative_metaphor'
            }
        ]
    }

    # Location pools by vertical (for Scenes 2-3 only now)
    LOCATION_POOLS = {
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

    # Camera angle pools for variety
    CAMERA_ANGLES = [
        'Phone mounted at eye level, intimate selfie-style angle',
        'Webcam angle from laptop, professional but approachable',
        'Phone held at arm\'s length, casual vlog style',
        'Tripod setup, slightly off-center for authenticity',
        'Over-the-shoulder perspective transitioning to direct camera'
    ]

    def __init__(self):
        """Initialize with OpenAI client for custom hook generation"""
        from openai import OpenAI
        from config import Config
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def _generate_dynamic_actors(self, analysis: Dict, vertical: str) -> List[Dict]:
        """
        Generate actor profiles dynamically based on original ad analysis

        Args:
            analysis: Original ad analysis with spokesperson info
            vertical: Detected vertical

        Returns:
            List of 3 actor profiles tailored to the ad
        """
        # Extract target demographic hints from analysis (normalize spokesperson format)
        original_spokesperson = normalize_spokesperson(analysis)
        original_age = original_spokesperson.get('age_range', '30-40')
        script = analysis.get('script', {}).get('full_transcript', '').lower()

        # Determine target age range based on content and vertical
        if any(word in script for word in ['student', 'college', 'gen-z', 'tiktok', 'young']):
            base_age = 25
        elif any(word in script for word in ['retire', 'senior', 'medicare', 'experienced']):
            base_age = 55
        elif vertical in ['finance', 'auto_insurance']:
            base_age = 35  # Primary earning/buying age
        else:
            base_age = 30  # Default

        # Generate 3 diverse actors around target demographic
        import random

        actors = []
        age_ranges = [
            (base_age - 5, base_age),      # Slightly younger
            (base_age, base_age + 10),     # Core demographic
            (base_age + 10, base_age + 20) # Slightly older
        ]

        genders = ['female', 'male', 'female']  # Mix for diversity
        random.shuffle(genders)

        emotions = [
            'frustrated then excited',
            'confident and reassuring',
            'urgent but helpful'
        ]

        purposes = [
            'Hook - establish relatable problem',
            'Social proof - solution works for real people',
            'Call to action - create urgency to act'
        ]

        styles = {
            'female': ['casual trendy style', 'smart casual style', 'professional but approachable style'],
            'male': ['business casual attire', 'casual professional style', 'smart casual look']
        }

        for i, (age_min, age_max) in enumerate(age_ranges):
            gender = genders[i]
            age_display = f"{age_min}s" if age_min % 10 == 0 else f"{age_min}-{age_max}"

            actor = {
                'age': age_display,
                'age_range': (age_min, age_max),
                'gender': gender,
                'description': f"{'Woman' if gender == 'female' else 'Man'} aged {age_min}-{age_max}, {random.choice(styles[gender])}, relatable and authentic",
                'emotion': emotions[i],
                'purpose': purposes[i]
            }
            actors.append(actor)

        return actors

    def _generate_custom_hooks_with_gpt(self, analysis: Dict, vertical: str) -> List[Dict]:
        """
        Generate custom extreme hooks using GPT for verticals without pre-written scenarios

        Args:
            analysis: Original ad analysis
            vertical: Detected vertical

        Returns:
            List of 3-5 extreme hook scenarios specific to this ad
        """
        script = analysis.get('script', {}).get('full_transcript', '')
        problem = analysis.get('storytelling', {}).get('problem_presented', '')
        solution = analysis.get('storytelling', {}).get('solution_offered', '')

        prompt = f"""You are a master ad director creating EXTREME VISUAL HOOKS for a {vertical} advertisement.

ORIGINAL AD CONTEXT:
- Script: {script[:500]}...
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

EXTREME HOOKS - SOLAR/ENERGY (Pattern: Environmental Failure + System Breakdown):
1. "Solar Panel Roof Crash" → Suburban house roof. OLD solar panels rusted and cracked. Wind gust hits. First panel BREAKS LOOSE, slides down roof in slow motion. Crashes to ground shattering. Second panel follows. Third. Domino effect. Glass exploding everywhere. Text: "Old tech failing. Your bill still rising."

2. "Electric Meter Explosion" → Close-up of old electric meter spinning. Numbers ticking up. Spinning faster. FASTER. Smoke starts coming from meter. Sparks fly. Meter glows RED HOT. Numbers blur into $$$. Glass cracks. EXPLOSION of sparks. Text: "Stop feeding the grid. Start owning it."

3. "Neighborhood Blackout Cascade" → Aerial drone shot of suburban neighborhood at dusk. One house goes DARK. Then the house next to it. Then three more. Spreading like a virus. Entire street goes black - except ONE house with lights on. Camera zooms to that house: solar panels glowing on roof. Text: "When theirs went out, mine stayed on."

EXTREME HOOKS - DEBT/FINANCE (Pattern: Real Financial Consequences):
1. "Repo Truck Arrival" → Quiet suburban driveway at dawn. Tow truck backs up beeping. Hooks onto car. Car lifts up off ground. Wheels dangling. Neighbors' porch lights turn on. Car dragged away leaving empty driveway and oil stain. Text: "Miss one payment. Lose everything."

2. "Mailbox Explosion" → Close-up of mailbox. Mailman stuffs bills inside. More bills. Mailbox BULGING. Door won't close. Bills start FALLING out onto ground. Pile growing. Wind scatters them across lawn. Red FINAL NOTICE envelopes everywhere. Text: "How many can you ignore?"

3. "Credit Card Declined Cascade" → Store checkout scanner. Card gets SWIPED. Screen shows DECLINED. Card tries second slot - DECLINED. Third attempt - DECLINED. Cards pile up on counter - Visa, Mastercard, Amex - all maxed out. Receipt printer prints $0.00. Text: "When they all say no."

4. "Foreclosure Sign Install" → Real estate sign post being hammered into front lawn. BANK OWNED sign goes up. Family photos visible through window. Moving boxes stacked. For Sale sign gets added. Realtor lock box on door. Text: "Don't let it get here."

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

FOLLOW THESE PROVEN PATTERNS (adapt to {vertical}):
PATTERN A - MECHANICAL FAILURE: "Equipment/object breaking down with dramatic consequences"
- Solar panel breaking loose and crashing
- Car lifted by tow truck and driven away
- Electric meter smoking and sparking

PATTERN B - ACCUMULATION/OVERFLOW: "Things piling up until they overflow/collapse"
- Mailbox stuffed with bills overflowing onto ground
- Hospital bills stacking up and falling off desk
- Multiple credit cards piling up at checkout (all declined)

PATTERN C - WEATHER/NATURAL EVENT: "Real weather causing visible damage"
- Hailstorm denting car hood
- Storm knocking tree onto car
- Wind scattering bills across yard

PATTERN D - REAL-WORLD TRANSACTION: "Actual business transaction going wrong"
- For Sale sign being installed on lawn
- Card declined at checkout counter
- Meter reader marking "past due" notice

DO NOT CREATE: Avalanches of bills, tornadoes of cards, things on fire (unless actual fire), CGI explosions, fantasy scenarios

Think: "Could I film this with a camera and practical effects? No CGI?"

For each hook, provide:
- name: Short catchy name (like "Electric Bill Shock" for solar)
- visual: Detailed 2-3 sentence visual description (NO PEOPLE)
- camera: Camera movement and angles
- emotion: Emotional impact (2-3 words)
- text_overlay: One impactful sentence that appears mid-scene (use patterns from examples)
- beat_breakdown: Timing breakdown (0-4s, 4-8s, 8-12s)
- audio: Sound design description
- lighting: Lighting style
- type: shock_and_relief, everyday_chaos, extreme_visual, or creative_metaphor

Return ONLY valid JSON in this exact format:
[
  {{
    "name": "Hook Name",
    "visual": "Visual description...",
    "camera": "Camera description...",
    "emotion": "emotion words",
    "text_overlay": "Text overlay message",
    "beat_breakdown": "0-4s: ... 4-8s: ... 8-12s: ...",
    "audio": "Audio description",
    "lighting": "Lighting description",
    "type": "shock_and_relief"
  }}
]

Generate 3 hooks using different patterns (shock, money, urgency, or curiosity). Make them DRAMATIC and SPECIFIC to {vertical}."""

        print(f"  🤖 Generating custom extreme hooks for {vertical} using GPT...")

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert ad director creating dramatic visual hooks. Return ONLY valid JSON, no other text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )

            response_text = response.choices[0].message.content.strip()

            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]

            import json
            custom_hooks = json.loads(response_text.strip())

            print(f"  ✓ Generated {len(custom_hooks)} custom hooks: {[h['name'] for h in custom_hooks]}")
            return custom_hooks

        except Exception as e:
            print(f"  ⚠ Custom hook generation failed: {e}")
            print(f"  Falling back to auto_insurance hooks")
            # Fallback to auto_insurance if GPT fails
            return self.HOOK_SCENARIOS['auto_insurance'][:3]

    def _generate_creative_actor_scenes(self, analysis: Dict, vertical: str) -> List[Dict]:
        """
        Generate CREATIVE Scene 2 & 3 scripts using GPT - NOT just copying the original ad

        Args:
            analysis: Original ad analysis
            vertical: Detected vertical

        Returns:
            List of 2 creative actor scene scripts (Scene 2: Social Proof, Scene 3: CTA)
        """
        script = analysis.get('script', {}).get('full_transcript', '')
        problem = analysis.get('storytelling', {}).get('problem_presented', '')
        solution = analysis.get('storytelling', {}).get('solution_offered', '')

        prompt = f"""You are a master ad copywriter creating INNOVATIVE Scene 2 and Scene 3 scripts for a {vertical} advertisement.

ORIGINAL AD CONTEXT:
- Script: {script[:500]}...
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
  {{
    "scene_number": 2,
    "purpose": "social_proof",
    "script": "Actor's spoken words for Scene 2...",
    "visual_direction": "Brief visual note (e.g., 'Confident, nodding', 'Showing phone with app')",
    "emotion": "emotion keywords"
  }},
  {{
    "scene_number": 3,
    "purpose": "urgent_cta",
    "script": "Actor's spoken words for Scene 3...",
    "visual_direction": "Brief visual note (e.g., 'Pointing at camera', 'Holding up fingers for countdown')",
    "emotion": "emotion keywords"
  }}
]

Generate Scene 2 and Scene 3 scripts. Make them CREATIVE and DIFFERENT from the original ad!"""

        print(f"  🎬 Generating creative Scene 2-3 scripts using GPT...")

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert ad copywriter creating innovative scene scripts. Return ONLY valid JSON, no other text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,  # Higher creativity
                max_tokens=1000
            )

            response_text = response.choices[0].message.content.strip()

            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]

            import json
            creative_scenes = json.loads(response_text.strip())

            print(f"  ✓ Generated creative scripts for Scene 2 (Social Proof) and Scene 3 (CTA)")
            return creative_scenes

        except Exception as e:
            print(f"  ⚠ Creative scene generation failed: {e}")
            # Fallback to generic scripts
            return [
                {
                    "scene_number": 2,
                    "purpose": "social_proof",
                    "script": "I was paying way too much. Then I found this. Saved over $2,000 this year. Couldn't believe I waited so long.",
                    "visual_direction": "Confident, relieved expression",
                    "emotion": "relief, satisfaction"
                },
                {
                    "scene_number": 3,
                    "purpose": "urgent_cta",
                    "script": "This week only. Free quote in 5 minutes. No catch. Just see your savings. Do it now before it's too late.",
                    "visual_direction": "Urgent, pointing at camera",
                    "emotion": "urgency, helpful"
                }
            ]

    def detect_vertical(self, analysis: Dict) -> str:
        """Detect the ad vertical from analysis"""
        script = analysis.get('script', {}).get('full_transcript', '').lower()

        # Check solar/energy FIRST (most specific)
        if any(word in script for word in ['solar', 'panel', 'electric bill', 'electricity', 'power bill', 'energy']):
            return 'solar'
        elif any(word in script for word in ['insurance', 'car insurance', 'auto insurance', 'premium', 'coverage']):
            return 'auto_insurance'
        elif any(word in script for word in ['health', 'medical', 'doctor', 'prescription', 'medicare']):
            return 'health_insurance'
        elif any(word in script for word in ['money', 'bank', 'savings', 'investment', 'credit']):
            return 'finance'
        elif any(word in script for word in ['fitness', 'workout', 'gym', 'weight']):
            return 'fitness'
        elif any(word in script for word in ['product', 'buy', 'order', 'shipping']):
            return 'ecommerce'
        elif any(word in script for word in ['software', 'app', 'platform', 'tool']):
            return 'saas'
        else:
            return 'ecommerce'

    def transform_to_sora_structure(self, analysis: Dict, vertical: str, variant_level: str = 'medium') -> List[Dict]:
        """
        Transform ad into SCENE 1 GENERATOR structure

        SCENE 1 STRATEGY: Only Scene 1 = Enhanced visual scene with better prompts
        - Scene 1 (12s): Enhanced visual scene with improved prompting
        - Focus on high-quality Scene 1 generation with better prompt structure

        Scene 1 uses enhanced scenarios with improved prompt generation.
        Focus on high-quality Scene 1 generation only.
        """
        import random

        script = analysis.get('script', {}).get('full_transcript', '')
        video_duration = analysis.get('video_metadata', {}).get('duration_seconds', 40)

        # Get enhanced scenarios for this vertical
        if vertical in self.HOOK_SCENARIOS:
            # Use pre-written scenarios for verticals with existing scenarios
            scenarios = self.HOOK_SCENARIOS[vertical]
            selected_scenario = random.choice(scenarios)
            print(f"  ✓ Using pre-written scenario: {selected_scenario['name']}")
        else:
            # Generate custom scenarios using GPT for verticals without pre-written scenarios
            print(f"  ⚡ No pre-written scenarios for {vertical}, generating custom scenarios...")
            custom_scenarios = self._generate_custom_hooks_with_gpt(analysis, vertical)
            selected_scenario = random.choice(custom_scenarios)
            print(f"  ✓ Selected custom scenario: {selected_scenario['name']}")

        transformed_scenes = []

        # SCENE 1: ENHANCED VISUAL SCENE - SCENE 1 GENERATOR
        scene_1 = {
            'scene_number': 1,
            'timestamp': '00:00-00:12',
            'duration_seconds': 12,
            'type': 'enhanced_scene',
            'purpose': 'High-quality visual scene with improved prompting',
            'has_character': False,  # Focus on visual storytelling
            'vertical': vertical,

            # Enhanced scenario details
            'scenario_name': selected_scenario['name'],
            'visual_description': selected_scenario['visual'],
            'camera_movement': selected_scenario['camera'],
            'emotion': selected_scenario['emotion'],
            'text_overlay': selected_scenario['text_overlay'],
            'beat_breakdown': selected_scenario['beat_breakdown'],
            'audio_design': selected_scenario['audio'],
            'lighting': selected_scenario['lighting'],
            'scenario_type': selected_scenario['type'],

            # Enhanced prompt structure for better generation
            'shot_type': 'Dynamic - see camera_movement',
            'camera_angle': 'Dynamic - see camera_movement',
            'setting': selected_scenario['visual'],
            'message': selected_scenario['text_overlay'],
            
            # Enhanced prompt elements for better Sora generation
            'enhanced_prompting': True,
            'cinematic_style': 'High production value, commercial quality',
            'visual_effects': 'Natural lighting, realistic physics, authentic movement',
            'audio_enhancement': 'Layered sound design, spatial audio, realistic acoustics'
        }
        transformed_scenes.append(scene_1)

        return transformed_scenes

    def _extract_script_segment(self, full_script: str, start_pct: float, end_pct: float) -> str:
        """Extract a segment of the script by percentage"""
        words = full_script.split()
        total_words = len(words)

        start_idx = int(total_words * start_pct)
        end_idx = int(total_words * end_pct)

        segment = ' '.join(words[start_idx:end_idx])
        return segment

    def create_transformation_report(self, analysis: Dict, transformed_scenes: List[Dict], vertical: str) -> Dict:
        """Create a detailed report of the transformation"""
        hook_scenes = [s for s in transformed_scenes if not s.get('has_character', True)]
        actor_scenes = [s for s in transformed_scenes if s.get('has_character', False)]

        return {
            'original_structure': {
                'scenes': len(analysis.get('scene_breakdown', [])),
                'duration': analysis.get('video_metadata', {}).get('duration_seconds', 0),
                'framework': analysis.get('storytelling', {}).get('framework', 'Unknown')
            },
            'detected_vertical': vertical,
            'transformed_structure': {
                'scenes': len(transformed_scenes),
                'duration': sum(s['duration_seconds'] for s in transformed_scenes),
                'strategy': 'Extreme Hooks + Actors',
                'hook_scenes': len(hook_scenes),
                'actor_scenes': len(actor_scenes),
                'actors_used': len(actor_scenes)
            },
            'transformation_strategy': 'EXTREME HOOKS: Scene 1 = Shock-value visual (NO PEOPLE), Scenes 2-3 = Actors (Social Proof + CTA)',
            'hook_scenario': transformed_scenes[0].get('scenario_name', 'Unknown') if transformed_scenes else None,
            'scenes': transformed_scenes
        }
