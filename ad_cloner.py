"""
Ad Cloner - Main Orchestrator
Combines all modules to clone ads with aggression variations
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from config import Config
from modules.gemini_analyzer import GeminiVideoAnalyzer
from modules.sora_transformer import SoraAdTransformer
from modules.aggression_variants import AggressionVariantGenerator
from modules.ad_director import AdDirector  # AI-driven scene generation
from modules.marketing_validator import MarketingValidator  # Conversion optimization
from modules.sora_prompt_composer import SoraPromptComposer
from modules.sora_client import SoraClient
from modules.video_assembler import VideoAssembler
from modules.ad_evaluator import AdEvaluator
from modules.prompt_validator import PromptValidator


class AdCloner:
    """Main orchestrator for ad cloning pipeline"""

    def __init__(self, logger=None):
        """Initialize all components"""
        print("Initializing Ad Cloner...")
        Config.validate_api_keys()

        self.analyzer = GeminiVideoAnalyzer()
        self.transformer = SoraAdTransformer()  # Transform ads for Sora
        self.variant_generator = AggressionVariantGenerator()
        self.ad_director = AdDirector()  # AI-driven scene generation with OpenAI
        self.marketing_validator = MarketingValidator()  # Validate & optimize for conversions
        self.prompt_composer = SoraPromptComposer()  # Converts AI scenes to Sora prompts
        self.prompt_validator = PromptValidator()  # Validate before API calls
        self.sora_client = SoraClient()
        self.assembler = VideoAssembler()
        self.evaluator = AdEvaluator()  # Evaluate generated ads
        self.logger = logger  # Optional logger for web interface

        print("✓ All systems ready\n")

    def _normalize_spokesperson(self, analysis: Dict) -> Dict:
        """
        Normalize spokesperson data - handle both dict and list formats

        Gemini sometimes returns spokesperson as a list (when multiple people),
        sometimes as a dict (when one person). We normalize to always use the first/primary person.
        """
        spokesperson = analysis.get('spokesperson', {})

        # If it's a list, take the first spokesperson
        if isinstance(spokesperson, list):
            if len(spokesperson) > 0:
                return spokesperson[0]
            else:
                return {}
        # If it's already a dict, use it
        elif isinstance(spokesperson, dict):
            return spokesperson
        # Fallback to empty dict
        else:
            return {}

    def clone_ad(self, video_path: str, variants: Optional[List[str]] = None) -> Dict:
        """
        Complete ad cloning pipeline

        Args:
            video_path: Path to winning ad video
            variants: Optional list of variant levels to generate
                     (default: all 4 - soft, medium, aggressive, ultra)

        Returns:
            Results dictionary with all generated ads
        """
        start_time = time.time()

        print("="*70)
        print("AD CLONER PIPELINE")
        print("="*70)
        print(f"Input Video: {video_path}\n")

        # STEP 1: Analyze video with Gemini
        print("\n[1/5] Analyzing video with Gemini 2.5...")
        if self.logger:
            from modules.logger import LogLevel
            self.logger.start_stage('analysis')
            self.logger.log(LogLevel.INFO, "Starting Gemini video analysis", {'video_path': video_path})
            self.logger.log(LogLevel.VERBOSE, "Uploading video to Gemini File API", {})

        try:
            analysis, analysis_path = self.analyzer.analyze_and_save(video_path)
            print(f"✓ Analysis complete: {analysis_path}")

            if self.logger:
                self.logger.log(LogLevel.VERBOSE, "Video analysis completed", {'analysis_path': analysis_path})

            # Extract spokesperson description (normalize list/dict formats)
            spokesperson = self._normalize_spokesperson(analysis)
            spokesperson_desc = spokesperson.get('physical_description', 'person')
            print(f"\nSpokesperson: {spokesperson_desc[:100]}...")

            if self.logger:
                num_scenes = len(analysis.get('scene_breakdown', []))
                scene_info = {
                    'scenes': num_scenes,
                    'path': analysis_path,
                    'duration': analysis.get('video_metadata', {}).get('duration_seconds', 0),
                    'spokesperson_length': len(spokesperson_desc)
                }
                self.logger.log(LogLevel.VERBOSE, f"Detected {num_scenes} scenes in video", scene_info)

                # Log each scene
                for i, scene in enumerate(analysis.get('scene_breakdown', []), 1):
                    self.logger.log(LogLevel.VERBOSE, f"Scene {i}: {scene.get('timestamp')} - {scene.get('purpose')}", {
                        'timestamp': scene.get('timestamp'),
                        'duration': scene.get('duration_seconds'),
                        'purpose': scene.get('purpose')
                    })

                self.logger.complete_stage('analysis', scene_info)

        except Exception as e:
            if self.logger:
                self.logger.log(LogLevel.ERROR, f"Gemini analysis failed: {str(e)}", {
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'video_path': video_path
                })
                self.logger.fail_stage('analysis', str(e))
            raise

        # STEP 1.5: Transform to Sora-friendly structure
        print("\n[1.5/5] Transforming ad structure for Sora...")
        if self.logger:
            self.logger.log(LogLevel.INFO, "Detecting ad vertical and transforming structure", {})

        try:
            # Detect vertical
            vertical = self.transformer.detect_vertical(analysis)
            vertical_name = vertical.replace('_', ' ').title()

            print(f"✓ Detected vertical: {vertical_name}")

            if self.logger:
                self.logger.log(LogLevel.VERBOSE, f"Vertical detected: {vertical_name}", {
                    'vertical': vertical,
                    'vertical_name': vertical_name
                })

            # Transform structure
            transformed_scenes = self.transformer.transform_to_sora_structure(analysis, vertical)

            print(f"✓ Transformed to Sora-friendly structure:")
            print(f"  - {sum(1 for s in transformed_scenes if s.get('has_character'))} character scene(s)")
            print(f"  - {sum(1 for s in transformed_scenes if not s.get('has_character'))} B-roll scene(s)")

            if self.logger:
                for scene in transformed_scenes:
                    scene_type = "CHARACTER" if scene.get('has_character') else "B-ROLL"
                    self.logger.log(LogLevel.VERBOSE, f"Scene {scene['scene_number']}: {scene_type} - {scene['type']}", {
                        'scene': scene['scene_number'],
                        'type': scene['type'],
                        'has_character': scene.get('has_character', False),
                        'duration': scene['duration_seconds']
                    })

            # Replace original scene_breakdown with transformed scenes
            analysis['scene_breakdown'] = transformed_scenes
            analysis['vertical'] = vertical
            analysis['vertical_name'] = vertical_name
            analysis['transformed'] = True

        except Exception as e:
            if self.logger:
                self.logger.log(LogLevel.ERROR, f"Transformation failed: {str(e)}", {
                    'error': str(e),
                    'error_type': type(e).__name__
                })
            # Continue with original analysis if transformation fails
            print(f"⚠ Transformation failed, using original structure: {str(e)}")

        # STEP 2: Generate aggression variants
        print("\n[2/5] Generating aggression variants...")
        if self.logger:
            self.logger.start_stage('variants')
            self.logger.log(LogLevel.VERBOSE, "Generating aggression level variations", {
                'requested_variants': variants if variants else 'all'
            })

        try:
            all_variants = self.variant_generator.generate_variants(analysis)

            # Filter variants if specified
            if variants:
                original_count = len(all_variants)
                all_variants = [v for v in all_variants if v['variant_level'] in variants]
                if self.logger:
                    self.logger.log(LogLevel.VERBOSE, f"Filtered variants: {original_count} → {len(all_variants)}", {
                        'requested': variants,
                        'generated': [v['variant_level'] for v in all_variants]
                    })

            print(f"✓ Generated {len(all_variants)} variants")
            for v in all_variants:
                print(f"  - {v['variant_name']}")
                if self.logger:
                    self.logger.log(LogLevel.VERBOSE, f"Variant: {v['variant_name']}", {
                        'level': v['variant_level'],
                        'scenes': len(v.get('modified_scenes', []))
                    })

            if self.logger:
                self.logger.complete_stage('variants', {
                    'count': len(all_variants),
                    'levels': [v['variant_level'] for v in all_variants]
                })

        except Exception as e:
            if self.logger:
                self.logger.log(LogLevel.ERROR, f"Variant generation failed: {str(e)}", {
                    'error': str(e),
                    'error_type': type(e).__name__
                })
                self.logger.fail_stage('variants', str(e))
            raise

        # STEP 3: Build Sora prompts from transformer scenes (DIRECT - no AI Director)
        print("\n[3/5] Building Sora prompts from extreme hooks...")
        if self.logger:
            self.logger.start_stage('prompts')
            self.logger.log(LogLevel.VERBOSE, "Building prompts directly from transformer scenes (extreme hooks)", {})

        try:
            from modules.sora_prompt_builder import SoraPromptBuilder
            prompt_builder = SoraPromptBuilder()

            variant_prompts = {}

            for variant in all_variants:
                if self.logger:
                    self.logger.log(LogLevel.VERBOSE, f"Building prompts for {variant['variant_name']}", {
                        'variant_level': variant['variant_level'],
                        'num_scenes': len(variant.get('modified_scenes', []))
                    })

                # Build prompts DIRECTLY from transformer scenes (with extreme hooks)
                print(f"  🎬 Building {variant['variant_name']} prompts...")

                # Extract spokesperson and script from analysis (normalize spokesperson format)
                spokesperson = self._normalize_spokesperson(analysis)
                spokesperson_desc = spokesperson.get('physical_description', 'person')
                full_script = analysis.get('script', {}).get('full_transcript', '')

                # Build prompts using SoraPromptBuilder (handles extreme hooks + actors)
                composed_prompts = prompt_builder.build_all_scene_prompts(
                    variant,
                    spokesperson_desc,
                    full_script
                )
                
                # VALIDATE prompts before storing
                validation_report = self.prompt_validator.validate_all_prompts(composed_prompts)
                
                if validation_report['errors_count'] > 0:
                    print(f"⚠ Warning: {validation_report['errors_count']} validation errors found")
                    if self.logger:
                        self.logger.log(LogLevel.WARNING, f"Prompt validation found {validation_report['errors_count']} errors", {
                            'variant': variant['variant_level'],
                            'errors': validation_report['errors_count'],
                            'warnings': validation_report['warnings_count']
                        })
                
                # Show validation warnings in console
                if validation_report['warnings_count'] > 0:
                    print(f"  ⚡ {validation_report['warnings_count']} optimization suggestions")
                
                variant_prompts[variant['variant_level']] = composed_prompts
                print(f"✓ {variant['variant_name']}: {len(composed_prompts)} scenes (audio + text + effects)")

                # Log AI-generated prompts for debugging
                if self.logger:
                    for i, prompt_data in enumerate(composed_prompts, 1):
                        self.logger.log(LogLevel.VERBOSE, f"  Scene {i} AI-generated prompt ready", {
                            'scene': i,
                            'timestamp': prompt_data.get('timestamp'),
                            'prompt_length': len(prompt_data['prompt']),
                            'full_prompt': prompt_data['prompt'],  # Log FULL prompt
                            'scene_type': prompt_data.get('scene_type'),
                            'purpose': prompt_data.get('purpose'),
                            'has_audio': prompt_data.get('has_audio'),
                            'has_text': prompt_data.get('has_text'),
                            'text_count': prompt_data.get('text_count', 0),
                            'composition_method': 'extreme_hooks_direct'
                        })

            # Save all prompts to file for detailed inspection
            prompts_file = Path(analysis_path).parent / f"sora_prompts_{Path(analysis_path).stem}.json"
            with open(prompts_file, 'w') as f:
                json.dump(variant_prompts, f, indent=2)
            print(f"✓ All prompts saved to: {prompts_file}")

            if self.logger:
                total_scenes = sum(len(p) for p in variant_prompts.values())
                self.logger.complete_stage('prompts', {
                    'total_scenes': total_scenes,
                    'variants': list(variant_prompts.keys()),
                    'prompts_file': str(prompts_file),
                    'composition_type': 'extreme_hooks_direct',
                    'features': ['extreme_hooks', 'transformer_scenes', 'audio', 'text_overlays', 'visual_progression'],
                    'validated': True
                })

        except Exception as e:
            if self.logger:
                self.logger.log(LogLevel.ERROR, f"Prompt composition failed: {str(e)}", {
                    'error': str(e),
                    'error_type': type(e).__name__
                })
                self.logger.fail_stage('prompts', str(e))
            raise

        # STEP 4: Generate videos with Sora (parallel)
        print("\n[4/5] Generating videos with Sora...")
        print(f"Total scenes to generate: {sum(len(p) for p in variant_prompts.values())}")
        print(f"This will take approximately 15-20 minutes...\n")

        if self.logger:
            total_scenes = sum(len(p) for p in variant_prompts.values())
            self.logger.start_stage('generation', total_scenes)
            self.logger.log(LogLevel.INFO, f"Starting Sora generation: {total_scenes} scenes across {len(variant_prompts)} variants", {
                'total_scenes': total_scenes,
                'variants': list(variant_prompts.keys())
            })

        try:
            generated_variants = {}

            for variant_level, prompts in variant_prompts.items():
                if self.logger:
                    self.logger.track_variant(variant_level, 'generating')
                    self.logger.log(LogLevel.VERBOSE, f"Starting {variant_level} variant generation", {
                        'variant': variant_level,
                        'scenes': len(prompts),
                        'method': 'parallel'
                    })

                try:
                    result = self.sora_client.generate_variant_parallel(prompts, variant_level)
                    generated_variants[variant_level] = result

                    if self.logger:
                        status = 'completed' if result['success'] else 'failed'
                        self.logger.track_variant(variant_level, status, result)
                        self.logger.log(LogLevel.VERBOSE, f"Variant {variant_level} generation {status}", {
                            'variant': variant_level,
                            'success': result['success'],
                            'scenes_completed': len(result.get('scenes', []))
                        })

                except Exception as e:
                    if self.logger:
                        self.logger.log(LogLevel.ERROR, f"Sora generation failed for {variant_level}: {str(e)}", {
                            'variant': variant_level,
                            'error': str(e),
                            'error_type': type(e).__name__
                        })
                        self.logger.track_variant(variant_level, 'failed', {'error': str(e)})
                    generated_variants[variant_level] = {'success': False, 'error': str(e)}

            if self.logger:
                successful = sum(1 for v in generated_variants.values() if v.get('success'))
                self.logger.complete_stage('generation', {
                    'total_variants': len(generated_variants),
                    'successful': successful,
                    'failed': len(generated_variants) - successful
                })

        except Exception as e:
            if self.logger:
                self.logger.log(LogLevel.ERROR, f"Generation stage failed: {str(e)}", {
                    'error': str(e),
                    'error_type': type(e).__name__
                })
                self.logger.fail_stage('generation', str(e))
            raise

        # STEP 5: Assemble final videos
        print("\n[5/5] Assembling final ads...")
        if self.logger:
            self.logger.start_stage('assembly')

        final_ads = {}

        for variant_level, variant_result in generated_variants.items():
            if variant_result['success']:
                try:
                    final_path = self.assembler.assemble_variant(variant_result)
                    final_ads[variant_level] = final_path
                    print(f"✓ {variant_level.UPPER()}: {final_path}")
                except Exception as e:
                    print(f"✗ Failed to assemble {variant_level}: {e}")
            else:
                print(f"✗ Skipping {variant_level} (generation failed)")

        if self.logger:
            self.logger.complete_stage('assembly', {'videos': len(final_ads)})

        # STEP 6: Evaluate generated ads (NEW)
        print("\n[6/6] Evaluating generated ads...")
        evaluations = {}

        for variant_level, video_path in final_ads.items():
            try:
                print(f"\n▸ Evaluating {variant_level} variant...")

                # Get the prompts used for this variant
                prompts_used = variant_prompts.get(variant_level, [])

                # Evaluate
                evaluation = self.evaluator.evaluate_generated_ad(
                    video_path,
                    analysis,
                    prompts_used
                )

                evaluations[variant_level] = evaluation

                # Save evaluation report
                eval_path = Path(analysis_path).parent / f"evaluation_{variant_level}.json"
                self.evaluator.save_evaluation_report(evaluation, str(eval_path))

                # Print ratings
                ratings = evaluation.get('ratings', {})
                print(f"  Overall Score: {ratings.get('overall_score', 0):.1f}/10")
                print(f"  Prediction: {ratings.get('predicted_performance', 'Unknown')}")

                if self.logger:
                    self.logger.log(LogLevel.INFO, f"Evaluated {variant_level}: {ratings.get('overall_score', 0):.1f}/10", {
                        'variant': variant_level,
                        'score': ratings.get('overall_score', 0),
                        'prediction': ratings.get('predicted_performance', 'Unknown'),
                        'eval_path': str(eval_path)
                    })

            except Exception as e:
                print(f"  ✗ Evaluation failed: {e}")
                if self.logger:
                    self.logger.log(LogLevel.WARNING, f"Evaluation failed for {variant_level}: {str(e)}", {
                        'variant': variant_level,
                        'error': str(e)
                    })

        # Summary
        elapsed = time.time() - start_time
        print("\n" + "="*70)
        print("PIPELINE COMPLETE")
        print("="*70)
        print(f"Time elapsed: {elapsed/60:.1f} minutes")
        print(f"Ads generated: {len(final_ads)}")
        print("\nFinal ads:")
        for level, path in final_ads.items():
            score = evaluations.get(level, {}).get('ratings', {}).get('overall_score', 0)
            print(f"  {level.upper()}: {path} (Score: {score:.1f}/10)")

        return {
            'analysis_path': analysis_path,
            'variants_generated': list(final_ads.keys()),
            'final_ads': final_ads,
            'evaluations': evaluations,
            'elapsed_time': elapsed
        }


# Main execution
if __name__ == "__main__":
    import sys

    cloner = AdCloner()

    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = input("Enter path to winning ad video: ")

    # Optional: specify which variants to generate
    variant_choice = input("\nGenerate all variants? (y/n, default=y): ").lower()

    if variant_choice == 'n':
        print("\nAvailable variants:")
        print("  1. soft - Calm, educational")
        print("  2. medium - Professional, balanced")
        print("  3. aggressive - Urgent, intense")
        print("  4. ultra - Confrontational, disruptive")
        selected = input("Enter comma-separated numbers (e.g., 1,3): ")
        variant_map = ['soft', 'medium', 'aggressive', 'ultra']
        variants = [variant_map[int(i)-1] for i in selected.split(',') if i.strip().isdigit()]
    else:
        variants = None

    # Run pipeline
    results = cloner.clone_ad(video_path, variants)

    # Save results
    results_path = Config.OUTPUT_DIR / 'results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {results_path}")
