"""
Ad Evaluator
Analyzes and rates the quality of generated ads
"""
import json
from typing import Dict
from pathlib import Path
from modules.gemini_analyzer import GeminiVideoAnalyzer
import google.generativeai as genai
from config import Config


class AdEvaluator:
    """Evaluates generated ads and provides quality ratings"""

    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.analyzer = GeminiVideoAnalyzer()

    def evaluate_generated_ad(self, video_path: str, original_analysis: Dict, prompts_used: list) -> Dict:
        """
        Evaluate a generated ad video

        Args:
            video_path: Path to generated video
            original_analysis: Original video analysis
            prompts_used: List of Sora prompts that were used

        Returns:
            Evaluation dictionary with ratings and feedback
        """
        print(f"\n{'='*70}")
        print("EVALUATING GENERATED AD")
        print(f"{'='*70}\n")

        # Analyze the generated video
        print("▸ Analyzing generated video with Gemini...")
        try:
            generated_analysis = self.analyzer.analyze_video(video_path)
            print("✓ Generated video analyzed")
        except Exception as e:
            print(f"✗ Failed to analyze generated video: {e}")
            generated_analysis = None

        # Compare to original
        evaluation = {
            'video_path': video_path,
            'original_analysis': original_analysis,
            'generated_analysis': generated_analysis,
            'prompts_used': prompts_used,
            'comparison': {},
            'ratings': {},
            'recommendations': []
        }

        if generated_analysis:
            # Compare key aspects
            evaluation['comparison'] = self._compare_ads(original_analysis, generated_analysis)

            # Rate the generated ad
            evaluation['ratings'] = self._rate_ad(generated_analysis, prompts_used)

            # Generate recommendations
            evaluation['recommendations'] = self._generate_recommendations(
                original_analysis,
                generated_analysis,
                prompts_used
            )

        return evaluation

    def _compare_ads(self, original: Dict, generated: Dict) -> Dict:
        """Compare original and generated ads"""
        comparison = {}

        # Compare script/message
        orig_script = original.get('script', {}).get('full_transcript', '')
        gen_script = generated.get('script', {}).get('full_transcript', '')

        comparison['script_similarity'] = self._calculate_similarity(orig_script, gen_script)
        comparison['original_script'] = orig_script
        comparison['generated_script'] = gen_script

        # Compare vertical/topic
        orig_vertical = original.get('vertical', 'unknown')
        comparison['original_vertical'] = orig_vertical

        # Detect generated vertical from script
        gen_script_lower = gen_script.lower()
        if any(word in gen_script_lower for word in ['insurance', 'car insurance', 'premium']):
            gen_vertical = 'auto_insurance'
        elif any(word in gen_script_lower for word in ['health', 'medical', 'doctor']):
            gen_vertical = 'health_insurance'
        else:
            gen_vertical = 'unknown'

        comparison['generated_vertical'] = gen_vertical
        comparison['vertical_match'] = orig_vertical == gen_vertical

        # Compare scene count
        comparison['original_scenes'] = len(original.get('scene_breakdown', []))
        comparison['generated_scenes'] = len(generated.get('scene_breakdown', []))

        # Compare character presence
        orig_has_character = any(
            scene.get('has_character', True)
            for scene in original.get('scene_breakdown', [])
        )
        gen_spokesperson = generated.get('spokesperson', {})
        gen_has_character = gen_spokesperson.get('total_screen_time_seconds', 0) > 0

        comparison['original_has_characters'] = orig_has_character
        comparison['generated_has_characters'] = gen_has_character

        return comparison

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate rough similarity between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _rate_ad(self, analysis: Dict, prompts: list) -> Dict:
        """Rate the generated ad on multiple criteria"""
        ratings = {}

        # Visual quality (based on description detail)
        visual_style = analysis.get('visual_style', {})
        ratings['visual_quality'] = self._rate_visual_quality(visual_style)

        # Message clarity
        script = analysis.get('script', {}).get('full_transcript', '')
        ratings['message_clarity'] = self._rate_message_clarity(script)

        # Pacing
        pacing = analysis.get('pacing', {})
        ratings['pacing'] = self._rate_pacing(pacing)

        # Storytelling
        storytelling = analysis.get('storytelling', {})
        ratings['storytelling'] = self._rate_storytelling(storytelling)

        # Overall predicted performance
        ratings['overall_score'] = sum(ratings.values()) / len(ratings)
        ratings['predicted_performance'] = self._predict_performance(ratings['overall_score'])

        return ratings

    def _rate_visual_quality(self, visual_style: Dict) -> float:
        """Rate visual quality 0-10"""
        score = 5.0  # Base score

        if visual_style.get('lighting_style'):
            score += 1.5
        if visual_style.get('color_palette') and len(visual_style['color_palette']) > 2:
            score += 1.5
        if visual_style.get('cinematography'):
            score += 2.0

        return min(score, 10.0)

    def _rate_message_clarity(self, script: str) -> float:
        """Rate message clarity 0-10"""
        if not script:
            return 0.0

        score = 5.0

        # Check for key elements
        if any(word in script.lower() for word in ['save', 'money', 'free', 'fast', 'easy']):
            score += 2.0
        if '$' in script:  # Has specific pricing
            score += 1.5
        if len(script.split()) > 50:  # Substantial content
            score += 1.5

        return min(score, 10.0)

    def _rate_pacing(self, pacing: Dict) -> float:
        """Rate pacing 0-10"""
        score = 5.0

        tempo = pacing.get('overall_tempo', '').lower()
        if 'fast' in tempo or 'energetic' in tempo:
            score += 2.5

        energy_curve = pacing.get('energy_curve', '')
        if energy_curve:
            score += 2.5

        return min(score, 10.0)

    def _rate_storytelling(self, storytelling: Dict) -> float:
        """Rate storytelling 0-10"""
        score = 5.0

        if storytelling.get('framework'):
            score += 2.0
        if storytelling.get('emotional_arc') and len(storytelling['emotional_arc']) > 2:
            score += 2.0
        if storytelling.get('urgency_tactics'):
            score += 1.0

        return min(score, 10.0)

    def _predict_performance(self, overall_score: float) -> str:
        """Predict ad performance based on score"""
        if overall_score >= 8.5:
            return "EXCELLENT - High conversion potential"
        elif overall_score >= 7.0:
            return "GOOD - Should perform well"
        elif overall_score >= 5.5:
            return "MODERATE - May need optimization"
        else:
            return "POOR - Needs significant improvement"

    def _generate_recommendations(self, original: Dict, generated: Dict, prompts: list) -> list:
        """Generate improvement recommendations"""
        recommendations = []

        # Check vertical match
        orig_vertical = original.get('vertical', 'unknown')
        gen_script = generated.get('script', {}).get('full_transcript', '').lower()

        # Check if generated content matches original vertical
        vertical_keywords = {
            'auto_insurance': ['insurance', 'car', 'driving', 'premium', 'coverage'],
            'health_insurance': ['health', 'medical', 'doctor', 'prescription'],
            'finance': ['money', 'savings', 'investment', 'bank']
        }

        expected_keywords = vertical_keywords.get(orig_vertical, [])
        keywords_found = sum(1 for kw in expected_keywords if kw in gen_script)

        if keywords_found < len(expected_keywords) / 2:
            recommendations.append({
                'severity': 'HIGH',
                'issue': 'Content does not match original vertical',
                'details': f"Expected {orig_vertical} content but generated video lacks key terms",
                'fix': "Strengthen vertical-specific keywords in B-roll prompts"
            })

        # Check for character consistency
        gen_scenes = generated.get('scene_breakdown', [])
        if len(gen_scenes) > 1:
            char_scenes = [s for s in gen_scenes if 'character' in str(s).lower() or 'person' in str(s).lower()]
            if len(char_scenes) > 1:
                recommendations.append({
                    'severity': 'MEDIUM',
                    'issue': 'Multiple character scenes detected',
                    'details': f"Found {len(char_scenes)} scenes with characters",
                    'fix': "Use transformation to limit to 1 character scene + B-roll only"
                })

        # Check pacing
        pacing = generated.get('pacing', {})
        if pacing.get('overall_tempo', '').lower() == 'slow':
            recommendations.append({
                'severity': 'MEDIUM',
                'issue': 'Pacing too slow',
                'details': "Slow pacing may lose viewer attention",
                'fix': "Use 'aggressive' or 'ultra' variant for faster pacing"
            })

        return recommendations

    def save_evaluation_report(self, evaluation: Dict, output_path: str):
        """Save comprehensive evaluation report"""
        with open(output_path, 'w') as f:
            json.dump(evaluation, f, indent=2)

        # Also create a human-readable summary
        summary_path = output_path.replace('.json', '_summary.txt')
        with open(summary_path, 'w') as f:
            f.write("="*70 + "\n")
            f.write("AD EVALUATION REPORT\n")
            f.write("="*70 + "\n\n")

            # Ratings
            f.write("RATINGS:\n")
            f.write("-" * 70 + "\n")
            ratings = evaluation.get('ratings', {})
            for key, value in ratings.items():
                if key != 'predicted_performance':
                    f.write(f"{key.replace('_', ' ').title()}: {value:.1f}/10\n")
            f.write(f"\nOverall Score: {ratings.get('overall_score', 0):.1f}/10\n")
            f.write(f"Predicted Performance: {ratings.get('predicted_performance', 'Unknown')}\n")

            # Comparison
            f.write("\n\nCOMPARISON TO ORIGINAL:\n")
            f.write("-" * 70 + "\n")
            comparison = evaluation.get('comparison', {})
            f.write(f"Original Vertical: {comparison.get('original_vertical', 'Unknown')}\n")
            f.write(f"Generated Vertical: {comparison.get('generated_vertical', 'Unknown')}\n")
            f.write(f"Vertical Match: {'✓ YES' if comparison.get('vertical_match') else '✗ NO'}\n")
            f.write(f"Scene Count: {comparison.get('original_scenes', 0)} → {comparison.get('generated_scenes', 0)}\n")

            # Recommendations
            f.write("\n\nRECOMMENDATIONS:\n")
            f.write("-" * 70 + "\n")
            recommendations = evaluation.get('recommendations', [])
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    f.write(f"\n{i}. [{rec['severity']}] {rec['issue']}\n")
                    f.write(f"   Details: {rec['details']}\n")
                    f.write(f"   Fix: {rec['fix']}\n")
            else:
                f.write("No major issues detected. Ad looks good!\n")

        print(f"\n✓ Evaluation saved to: {output_path}")
        print(f"✓ Summary saved to: {summary_path}")
