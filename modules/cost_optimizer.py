"""
Cost Optimizer Module

Intelligently selects the most cost-effective Sora model while maintaining quality.
Analyzes prompt complexity and recommends optimal model selection.
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CostAnalysis:
    """Cost analysis result"""
    recommended_model: str
    estimated_cost: float
    cost_savings: float
    complexity_score: int
    reasoning: str


class CostOptimizer:
    """
    Intelligent cost optimization for Sora model selection.
    
    Analyzes prompt complexity and recommends the most cost-effective model
    while maintaining quality standards.
    """
    
    def __init__(self):
        # Model pricing (per second)
        self.SORA_2_COST = 0.064
        self.SORA_2_PRO_COST = 0.08
        
        # Complexity thresholds
        self.SIMPLE_THRESHOLD = 3
        self.MEDIUM_THRESHOLD = 6
        self.COMPLEX_THRESHOLD = 9
        
        # Quality requirements mapping
        self.QUALITY_REQUIREMENTS = {
            'basic': 'sora-2',
            'standard': 'sora-2',
            'high': 'sora-2-pro',
            'premium': 'sora-2-pro'
        }
    
    def analyze_prompt_complexity(self, prompt: str) -> int:
        """
        Analyze prompt complexity and return score (1-10).
        
        Higher scores indicate more complex prompts that benefit from Sora 2 Pro.
        """
        complexity_score = 0
        
        # Length factor (longer prompts = more complex)
        word_count = len(prompt.split())
        if word_count > 200:
            complexity_score += 3
        elif word_count > 100:
            complexity_score += 2
        elif word_count > 50:
            complexity_score += 1
        
        # Technical complexity indicators
        technical_terms = [
            'cinematic', '4K', 'professional', 'commercial', 'high-end',
            'dramatic', 'epic', 'sophisticated', 'premium', 'luxury',
            'complex', 'intricate', 'detailed', 'precise', 'advanced'
        ]
        
        for term in technical_terms:
            if term.lower() in prompt.lower():
                complexity_score += 1
        
        # Visual complexity indicators
        visual_indicators = [
            'multiple characters', 'crowd', 'ensemble', 'group',
            'complex lighting', 'dramatic shadows', 'cinematic lighting',
            'special effects', 'visual effects', 'motion graphics',
            'text overlays', 'animations', 'transitions'
        ]
        
        for indicator in visual_indicators:
            if indicator.lower() in prompt.lower():
                complexity_score += 1
        
        # Camera work complexity
        camera_terms = [
            'crane shot', 'dolly', 'tracking', 'steadicam', 'gimbal',
            'complex movement', 'smooth motion', 'cinematic movement',
            'dynamic', 'fluid', 'seamless'
        ]
        
        for term in camera_terms:
            if term.lower() in prompt.lower():
                complexity_score += 1
        
        # Character consistency requirements
        if 'same character' in prompt.lower() or 'consistent character' in prompt.lower():
            complexity_score += 2
        
        # Audio complexity
        if 'audio' in prompt.lower() or 'sound' in prompt.lower():
            complexity_score += 1
        
        # Text overlay complexity
        if 'text overlay' in prompt.lower() or 'text on screen' in prompt.lower():
            complexity_score += 1
        
        return min(complexity_score, 10)  # Cap at 10
    
    def recommend_model(self, prompt: str, quality_requirement: str = 'standard') -> CostAnalysis:
        """
        Recommend the optimal Sora model based on prompt complexity and quality requirements.
        
        Args:
            prompt: The Sora prompt to analyze
            quality_requirement: 'basic', 'standard', 'high', or 'premium'
        
        Returns:
            CostAnalysis with recommendation and reasoning
        """
        complexity_score = self.analyze_prompt_complexity(prompt)
        
        # Base recommendation on complexity
        if complexity_score >= self.COMPLEX_THRESHOLD:
            recommended_model = 'sora-2-pro'
            reasoning = f"Complex prompt (score: {complexity_score}) requires Sora 2 Pro for best results"
        elif complexity_score >= self.MEDIUM_THRESHOLD:
            # Check quality requirement for medium complexity
            if quality_requirement in ['high', 'premium']:
                recommended_model = 'sora-2-pro'
                reasoning = f"Medium complexity (score: {complexity_score}) with {quality_requirement} quality requirement"
            else:
                recommended_model = 'sora-2'
                reasoning = f"Medium complexity (score: {complexity_score}) suitable for Sora 2"
        else:
            recommended_model = 'sora-2'
            reasoning = f"Simple prompt (score: {complexity_score}) works well with Sora 2"
        
        # Override based on quality requirement
        if quality_requirement in ['high', 'premium'] and recommended_model == 'sora-2':
            recommended_model = 'sora-2-pro'
            reasoning += f" (upgraded for {quality_requirement} quality requirement)"
        
        # Calculate costs
        duration = 12  # Default 12 seconds
        sora_2_cost = duration * self.SORA_2_COST
        sora_2_pro_cost = duration * self.SORA_2_PRO_COST
        
        if recommended_model == 'sora-2':
            estimated_cost = sora_2_cost
            cost_savings = sora_2_pro_cost - sora_2_cost
        else:
            estimated_cost = sora_2_pro_cost
            cost_savings = 0
        
        return CostAnalysis(
            recommended_model=recommended_model,
            estimated_cost=estimated_cost,
            cost_savings=cost_savings,
            complexity_score=complexity_score,
            reasoning=reasoning
        )
    
    def estimate_cost(self, scenes: List[Dict], model: str = None) -> Dict:
        """
        Estimate total cost for multiple scenes.
        
        Args:
            scenes: List of scene dictionaries with prompts
            model: Specific model to use, or None for auto-selection
        
        Returns:
            Dictionary with cost breakdown
        """
        total_cost = 0
        cost_breakdown = []
        total_savings = 0
        
        for i, scene in enumerate(scenes):
            prompt = scene.get('prompt', '')
            duration = scene.get('duration_seconds', 12)
            
            if model:
                # Use specified model
                if model == 'sora-2':
                    scene_cost = duration * self.SORA_2_COST
                else:
                    scene_cost = duration * self.SORA_2_PRO_COST
                savings = 0
            else:
                # Auto-select model
                analysis = self.recommend_model(prompt)
                scene_cost = analysis.estimated_cost
                savings = analysis.cost_savings
                model = analysis.recommended_model
            
            total_cost += scene_cost
            total_savings += savings
            
            cost_breakdown.append({
                'scene': i + 1,
                'model': model,
                'duration': duration,
                'cost': scene_cost,
                'savings': savings
            })
        
        return {
            'total_cost': total_cost,
            'total_savings': total_savings,
            'scenes_count': len(scenes),
            'breakdown': cost_breakdown,
            'recommendation': f"Total: ${total_cost:.2f}" + (f" (Saved: ${total_savings:.2f})" if total_savings > 0 else "")
        }
    
    def batch_optimize(self, scenes: List[Dict]) -> Dict:
        """
        Optimize multiple scenes for cost efficiency.
        
        Groups similar scenes and recommends batch processing strategies.
        """
        # Analyze each scene
        analyses = []
        for scene in scenes:
            prompt = scene.get('prompt', '')
            analysis = self.recommend_model(prompt)
            analyses.append({
                'scene': scene,
                'analysis': analysis
            })
        
        # Group by recommended model
        sora_2_scenes = [a for a in analyses if a['analysis'].recommended_model == 'sora-2']
        sora_2_pro_scenes = [a for a in analyses if a['analysis'].recommended_model == 'sora-2-pro']
        
        # Calculate batch savings
        total_sora_2_cost = sum(a['analysis'].estimated_cost for a in sora_2_scenes)
        total_sora_2_pro_cost = sum(a['analysis'].estimated_cost for a in sora_2_pro_scenes)
        total_cost = total_sora_2_cost + total_sora_2_pro_cost
        
        # Calculate potential savings if all scenes used Sora 2 Pro
        all_sora_2_pro_cost = sum(
            scene.get('duration_seconds', 12) * self.SORA_2_PRO_COST 
            for scene in scenes
        )
        potential_savings = all_sora_2_pro_cost - total_cost
        
        return {
            'optimized_cost': total_cost,
            'potential_savings': potential_savings,
            'sora_2_scenes': len(sora_2_scenes),
            'sora_2_pro_scenes': len(sora_2_pro_scenes),
            'recommendations': [
                f"Use Sora 2 for {len(sora_2_scenes)} simple scenes",
                f"Use Sora 2 Pro for {len(sora_2_pro_scenes)} complex scenes",
                f"Total savings: ${potential_savings:.2f} vs all Sora 2 Pro"
            ]
        }
    
    def get_cost_comparison(self, prompt: str, duration: int = 12) -> Dict:
        """
        Get detailed cost comparison for a single prompt.
        """
        analysis = self.recommend_model(prompt)
        
        sora_2_cost = duration * self.SORA_2_COST
        sora_2_pro_cost = duration * self.SORA_2_PRO_COST
        
        return {
            'prompt_preview': prompt[:100] + '...' if len(prompt) > 100 else prompt,
            'duration': duration,
            'complexity_score': analysis.complexity_score,
            'recommended_model': analysis.recommended_model,
            'sora_2_cost': sora_2_cost,
            'sora_2_pro_cost': sora_2_pro_cost,
            'recommended_cost': analysis.estimated_cost,
            'savings': analysis.cost_savings,
            'reasoning': analysis.reasoning
        }
