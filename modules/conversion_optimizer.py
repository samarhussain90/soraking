"""
Conversion Optimizer
Adds conversion-focused elements to prompts (pattern interrupts, hooks, urgency cues)
"""
from typing import Dict, List
import random


class ConversionOptimizer:
    """Optimizes prompts for conversion with proven psychological triggers"""
    
    def __init__(self):
        # Pattern interrupts by vertical
        self.pattern_interrupts = {
            'auto_insurance': [
                'Suddenly noticing high insurance bill on phone',
                'Frustrated reaction to renewal letter',
                'Eyes widening at calculator total',
                'Double-take at monthly payment amount'
            ],
            'health_insurance': [
                'Shocked reaction to medical bill',
                'Overwhelmed by prescription costs',
                'Relief finding solution'
            ],
            'finance': [
                'Surprised by bank account notification',
                'Excited discovery on investment app',
                'Relieved finding savings solution'
            ]
        }
        
        # Social proof visual cues
        self.social_proof_cues = [
            'notification showing "thousands qualified"',
            'success counter ticking up',
            'testimonial quotes appearing',
            'check marks appearing next to benefits'
        ]
        
        # Urgency builders for B-roll
        self.urgency_visuals = {
            'time_based': [
                'clock ticking',
                'calendar pages flipping',
                'countdown timer visual'
            ],
            'scarcity': [
                'limited spots remaining indicator',
                'offer expiring soon visual',
                'exclusive access badge'
            ]
        }

    def enhance_character_prompt(self, prompt: str, vertical: str, scene_purpose: str) -> str:
        """
        Add conversion elements to character scene prompt
        
        Args:
            prompt: Base prompt
            vertical: Ad vertical
            scene_purpose: Scene purpose (hook, problem, solution, CTA)
        
        Returns:
            Enhanced prompt with conversion triggers
        """
        enhancements = []
        
        # Hook scenes: Add pattern interrupt
        if 'hook' in scene_purpose.lower():
            interrupts = self.pattern_interrupts.get(vertical, self.pattern_interrupts.get('auto_insurance'))
            enhancements.append(f"Pattern interrupt: {random.choice(interrupts)}")
        
        # CTA scenes: Add urgency cues
        if 'cta' in scene_purpose.lower():
            enhancements.append("Urgency: Leaning forward, pointing gesture toward CTA")
            enhancements.append("Social proof indicator: Subtle notification or counter in background")
        
        # Add enhancements to prompt
        if enhancements:
            enhanced = prompt + "\n\nCONVERSION ELEMENTS:\n" + "\n".join(f"- {e}" for e in enhancements)
            return enhanced
        
        return prompt

    def enhance_broll_prompt(self, prompt: str, scene_purpose: str) -> str:
        """
        Add conversion-focused visual storytelling to B-roll
        
        Args:
            prompt: Base B-roll prompt
            scene_purpose: Scene purpose
        
        Returns:
            Enhanced prompt with conversion visuals
        """
        enhancements = []
        
        # Problem scenes: Show frustration/pain visually
        if 'problem' in scene_purpose.lower():
            enhancements.append("Visual tension: Show before state with subtle distress cues")
            enhancements.append("Color: Desaturated, cooler tones emphasizing problem")
        
        # Solution scenes: Show transformation
        if 'solution' in scene_purpose.lower():
            enhancements.append("Visual transformation: Transition from problem to solution state")
            enhancements.append("Color: Warm, saturated tones showing relief/success")
        
        # CTA scenes: Add urgency
        if 'cta' in scene_purpose.lower():
            urgency = random.choice(self.urgency_visuals['time_based'])
            enhancements.append(f"Urgency visual: {urgency}")
        
        # Add enhancements
        if enhancements:
            enhanced = prompt + "\n\nCONVERSION STORYTELLING:\n" + "\n".join(f"- {e}" for e in enhancements)
            return enhanced
        
        return prompt

    def add_scroll_stopper(self, prompt: str, aggression_level: str) -> str:
        """
        Add unexpected visual moment to break scroll
        
        Args:
            prompt: Base prompt
            aggression_level: Aggression level
        
        Returns:
            Prompt with scroll-stopper element
        """
        scroll_stoppers = {
            'soft': [
                'Unexpected moment of genuine surprise',
                'Authentic spontaneous reaction'
            ],
            'medium': [
                'Dramatic gesture emphasizing key point',
                'Sudden reveal of important information'
            ],
            'aggressive': [
                'Bold, attention-grabbing action',
                'High-energy unexpected movement'
            ],
            'ultra': [
                'Explosive reaction or reveal',
                'Shocking visual contrast'
            ]
        }
        
        stoppers = scroll_stoppers.get(aggression_level, scroll_stoppers['medium'])
        stopper = random.choice(stoppers)
        
        # Insert scroll-stopper into prompt
        enhanced = prompt + f"\n\nSCROLL-STOPPER: {stopper} at key moment to break pattern"
        
        return enhanced

    def optimize_prompt(self, prompt: str, scene: Dict, variant: Dict) -> str:
        """
        Full optimization pipeline for a prompt
        
        Args:
            prompt: Base prompt
            scene: Scene dictionary
            variant: Variant configuration
        
        Returns:
            Fully optimized prompt
        """
        # Get context
        vertical = scene.get('vertical', 'default')
        purpose = scene.get('purpose', '')
        aggression = variant.get('variant_level', 'medium')
        has_character = scene.get('has_character', True)
        
        # Enhance based on type
        if has_character:
            prompt = self.enhance_character_prompt(prompt, vertical, purpose)
        else:
            prompt = self.enhance_broll_prompt(prompt, purpose)
        
        # Add scroll-stopper for aggressive variants
        if aggression in ['aggressive', 'ultra']:
            prompt = self.add_scroll_stopper(prompt, aggression)
        
        return prompt


# Test function
if __name__ == "__main__":
    optimizer = ConversionOptimizer()
    
    # Test character scene
    char_prompt = """Female, 25, brown hair, white tee, home office.
    
Confident delivery: "I was paying $120 a month..."

Steady camera. Direct eye contact."""

    enhanced = optimizer.optimize_prompt(
        char_prompt,
        {'vertical': 'auto_insurance', 'purpose': 'hook', 'has_character': True},
        {'variant_level': 'aggressive'}
    )
    
    print("ENHANCED PROMPT:")
    print(enhanced)

