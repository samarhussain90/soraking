"""
Viral Hook Generator - Main Orchestrator
Generates viral 12-second hooks for any affiliate marketing vertical
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from config import Config
from modules.gemini_analyzer import GeminiVideoAnalyzer
from modules.sora_transformer import SoraAdTransformer
from modules.aggression_variants import AggressionVariantGenerator
from modules.sora_prompt_builder import SoraPromptBuilder
from modules.sora_client import SoraClient
from modules.video_assembler import VideoAssembler
from modules.ad_evaluator import AdEvaluator
from modules.prompt_validator import PromptValidator
from modules.cost_optimizer import CostOptimizer
from modules.utils import normalize_spokesperson
from pipeline_integrator import PipelineIntegrator


class Scene1Generator:
    """Main orchestrator for Scene 1 generation pipeline"""

    def __init__(self, logger=None, spaces_client=None, session_id=None, generation_id=None, integrator=None):
        """
        Initialize all components

        Args:
            logger: Optional logger for web interface
            spaces_client: Optional SpacesClient for cloud uploads
            session_id: Optional session ID for organizing uploads
            generation_id: Optional generation ID for history tracking
            integrator: Optional PipelineIntegrator for saving generation history
        """
        print("Initializing Viral Hook Generator...")
        Config.validate_api_keys()

        self.analyzer = GeminiVideoAnalyzer()
        self.transformer = SoraAdTransformer()  # Transform ads for Sora
        self.variant_generator = AggressionVariantGenerator()
        self.prompt_builder = SoraPromptBuilder()  # Build Sora prompts (active)
        self.prompt_validator = PromptValidator()  # Validate before API calls
        self.sora_client = SoraClient(spaces_client=spaces_client, session_id=session_id)
        self.assembler = VideoAssembler()
        self.evaluator = AdEvaluator()  # Evaluate generated ads
        self.cost_optimizer = CostOptimizer()  # Cost optimization
        self.logger = logger  # Optional logger for web interface
        self.generation_id = generation_id  # Generation ID for history tracking
        self.integrator = integrator  # PipelineIntegrator for saving history

        print("✓ All systems ready\n")

    def generate_scene1(self, video_path: str, aggression_level: str = 'medium', 
                       product_script: str = '', output_dimension: str = '720x1280', 
                       sora_model: str = 'sora-2', motion_description: str = '', 
                       image_script: str = '') -> Dict:
        """
        Complete Scene 1 generation pipeline - SINGLE SCENE

        Args:
            video_path: Path to winning ad video
            aggression_level: Aggression level for the scene (soft, medium, aggressive, ultra)
            product_script: Optional product script for better generation
            output_dimension: Output video dimensions (e.g., '720x1280', '1280x720')
            sora_model: Sora model to use ('sora-2' or 'sora-2-pro')

        Returns:
            Results dictionary with single generated Scene 1
        """
        start_time = time.time()

        print("="*70)
        print("SCENE 1 GENERATOR")
        print("="*70)
        print(f"Input Video: {video_path}\n")

        # STEP 1: Analyze video with Gemini or use script-only mode
        if video_path == 'script-only-mode':
            print("\n[1/4] Using script-only mode...")
            if self.logger:
                from modules.logger import LogLevel
                self.logger.start_stage('analysis')
                self.logger.log(LogLevel.INFO, "Using script-only mode", {'product_script': product_script[:100] + '...'})
            
            # Create a mock analysis for script-only mode
            analysis = {
                'script': product_script,
                'spokesperson': {
                    'physical_description': 'confident person in business attire',
                    'age_range': '25-35',
                    'gender': 'any'
                },
                'scenes': [
                    {
                        'timestamp': '00:00-00:12',
                        'duration': 12,
                        'purpose': 'hook',
                        'description': 'Opening hook scene'
                    }
                ],
                'vertical': 'general',
                'duration': 12
            }
            analysis_path = None
            print(f"✓ Script-only mode ready")
            spokesperson_desc = analysis['spokesperson']['physical_description']
            print(f"\nSpokesperson: {spokesperson_desc}")
        elif video_path.startswith('image-to-video:'):
            print("\n[1/4] Using image-to-video mode...")
            if self.logger:
                from modules.logger import LogLevel
                self.logger.start_stage('analysis')
                self.logger.log(LogLevel.INFO, "Using image-to-video mode", {
                    'image_url': video_path.replace('image-to-video:', ''),
                    'motion_description': motion_description[:100] + '...' if motion_description else ''
                })
            
            # Extract image URL from video_path
            image_url = video_path.replace('image-to-video:', '')
            
            # Create a mock analysis for image-to-video mode
            analysis = {
                'script': image_script or motion_description,
                'spokesperson': {
                    'physical_description': 'animated product or object',
                    'age_range': 'any',
                    'gender': 'any'
                },
                'scenes': [
                    {
                        'timestamp': '00:00-00:12',
                        'duration': 12,
                        'purpose': 'hook',
                        'description': f'Animated image: {motion_description}',
                        'image_url': image_url,
                        'motion_description': motion_description
                    }
                ],
                'vertical': 'general',
                'duration': 12,
                'image_to_video': True
            }
            analysis_path = None
            print(f"✓ Image-to-video mode ready")
            print(f"Image URL: {image_url}")
            print(f"Motion: {motion_description}")
            spokesperson_desc = analysis['spokesperson']['physical_description']
        else:
            print("\n[1/4] Analyzing video with Gemini 2.5...")
            if self.logger:
                from modules.logger import LogLevel
                self.logger.start_stage('analysis')
                self.logger.log(LogLevel.INFO, "Starting Gemini video analysis", {'video_path': video_path})
                self.logger.log(LogLevel.VERBOSE, "Uploading video to Gemini File API", {})

            try:
                analysis, analysis_path = self.analyzer.analyze_and_save(video_path)
                print(f"✓ Analysis complete: {analysis_path}")

                # Save analysis metadata to generation history
                if self.integrator and self.generation_id:
                    self.integrator.save_analysis_metadata(self.generation_id, analysis)

                if self.logger:
                    self.logger.log(LogLevel.VERBOSE, "Video analysis completed", {'analysis_path': analysis_path})

                # Extract spokesperson description (normalize list/dict formats)
                spokesperson = normalize_spokesperson(analysis)
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

            # Save transformation metadata to generation history
            if self.integrator and self.generation_id:
                self.integrator.save_transformation_metadata(self.generation_id, {
                    'vertical': vertical,
                    'vertical_name': vertical_name,
                    'transformed_scenes': transformed_scenes
                })

        except Exception as e:
            if self.logger:
                self.logger.log(LogLevel.ERROR, f"Transformation failed: {str(e)}", {
                    'error': str(e),
                    'error_type': type(e).__name__
                })
            # Continue with original analysis if transformation fails
            print(f"⚠ Transformation failed, using original structure: {str(e)}")

        # STEP 2: Generate single Scene 1 with specified aggression level
        print(f"\n[2/4] Generating {aggression_level} intensity Scene 1...")
        if self.logger:
            self.logger.start_stage('variants')
            self.logger.log(LogLevel.VERBOSE, f"Generating single Scene 1 with {aggression_level} intensity", {
                'aggression_level': aggression_level
            })

        try:
            # Generate single variant with specified aggression level
            all_variants = self.variant_generator.generate_variants(analysis)
            
            # Filter to only the requested aggression level
            target_variant = None
            for v in all_variants:
                if v['variant_level'] == aggression_level:
                    target_variant = v
                    break
            
            if not target_variant:
                # Fallback to medium if requested level not found
                target_variant = next((v for v in all_variants if v['variant_level'] == 'medium'), all_variants[0])
                print(f"⚠ Requested {aggression_level} not found, using {target_variant['variant_level']}")

            all_variants = [target_variant]  # Only one variant

            print(f"✓ Generated {target_variant['variant_name']} Scene 1")
            if self.logger:
                self.logger.log(LogLevel.VERBOSE, f"Single Scene 1: {target_variant['variant_name']}", {
                    'level': target_variant['variant_level'],
                    'scenes': len(target_variant.get('modified_scenes', []))
                })

            if self.logger:
                self.logger.complete_stage('variants', {
                    'count': 1,
                    'level': target_variant['variant_level']
                })

        except Exception as e:
            if self.logger:
                self.logger.log(LogLevel.ERROR, f"Variant generation failed: {str(e)}", {
                    'error': str(e),
                    'error_type': type(e).__name__
                })
                self.logger.fail_stage('variants', str(e))
            raise

        # STEP 3: Build Sora prompts for Scene 1
        print("\n[3/4] Building Sora prompts for Scene 1...")
        if self.logger:
            self.logger.start_stage('prompts')
            self.logger.log(LogLevel.VERBOSE, "Building prompts directly from transformer scenes (enhanced Scene 1)", {})

        try:
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
                spokesperson = normalize_spokesperson(analysis)
                spokesperson_desc = spokesperson.get('physical_description', 'person')
                full_script = analysis.get('script', {}).get('full_transcript', '')

                # Build prompts using SoraPromptBuilder (handles extreme hooks + actors)
                composed_prompts = self.prompt_builder.build_all_scene_prompts(
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

            # Save prompts metadata and create scene records in generation history
            if self.integrator and self.generation_id:
                self.integrator.save_prompts_metadata(self.generation_id, variant_prompts)

                # Create scene records for each variant
                self.variant_scene_ids = {}  # Store scene IDs for later use
                for variant_level, prompts in variant_prompts.items():
                    scene_ids = self.integrator.create_scene_records(
                        self.generation_id,
                        variant_level,
                        [p['prompt'] for p in prompts]
                    )
                    self.variant_scene_ids[variant_level] = scene_ids

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

        # STEP 4: Cost Optimization Analysis
        if Config.ENABLE_COST_OPTIMIZATION:
            print("\n[4/5] Analyzing cost optimization...")
            if self.logger:
                self.logger.log(LogLevel.VERBOSE, "Running cost optimization analysis", {})
            
            try:
                # Analyze all prompts for cost optimization
                all_prompts = []
                for variant_level, prompts in variant_prompts.items():
                    for prompt_data in prompts:
                        all_prompts.append({
                            'prompt': prompt_data['prompt'],
                            'duration_seconds': 12,
                            'variant': variant_level
                        })
                
                # Get cost analysis
                cost_analysis = self.cost_optimizer.batch_optimize(all_prompts)
                
                # Log cost optimization results
                print(f"✓ Cost analysis complete:")
                print(f"  - Optimized cost: ${cost_analysis['optimized_cost']:.2f}")
                print(f"  - Potential savings: ${cost_analysis['potential_savings']:.2f}")
                print(f"  - Sora 2 scenes: {cost_analysis['sora_2_scenes']}")
                print(f"  - Sora 2 Pro scenes: {cost_analysis['sora_2_pro_scenes']}")
                
                if self.logger:
                    self.logger.log(LogLevel.INFO, "Cost optimization analysis complete", {
                        'optimized_cost': cost_analysis['optimized_cost'],
                        'potential_savings': cost_analysis['potential_savings'],
                        'sora_2_scenes': cost_analysis['sora_2_scenes'],
                        'sora_2_pro_scenes': cost_analysis['sora_2_pro_scenes']
                    })
                
                # Check if cost exceeds limit
                if cost_analysis['optimized_cost'] > Config.MAX_COST_PER_GENERATION:
                    print(f"⚠ Cost (${cost_analysis['optimized_cost']:.2f}) exceeds limit (${Config.MAX_COST_PER_GENERATION})")
                    if self.logger:
                        self.logger.log(LogLevel.WARNING, f"Generation cost exceeds limit", {
                            'cost': cost_analysis['optimized_cost'],
                            'limit': Config.MAX_COST_PER_GENERATION
                        })
                
            except Exception as e:
                print(f"⚠ Cost optimization failed: {str(e)}")
                if self.logger:
                    self.logger.log(LogLevel.WARNING, f"Cost optimization failed: {str(e)}", {
                        'error': str(e)
                    })

        # STEP 5: Generate viral hooks with Sora (parallel)
        print(f"\n[{'5' if Config.ENABLE_COST_OPTIMIZATION else '4'}/{'5' if Config.ENABLE_COST_OPTIMIZATION else '4'}] Generating viral hooks with Sora...")
        print(f"Total hooks to generate: {sum(len(p) for p in variant_prompts.values())}")
        print(f"This will take approximately 3-5 minutes (1 hook per variant)...\n")

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
                    # Get image URL for image-to-video mode
                    image_url = None
                    if analysis.get('image_to_video') and analysis.get('scenes'):
                        image_url = analysis['scenes'][0].get('image_url')
                    
                    result = self.sora_client.generate_variant_parallel(prompts, variant_level, sora_model, output_dimension, image_url)
                    generated_variants[variant_level] = result

                    # Process and save videos to Spaces if generation succeeded
                    if result['success'] and self.integrator and self.generation_id:
                        scene_ids = self.variant_scene_ids.get(variant_level, [])
                        scenes = result.get('scenes', [])

                        for idx, scene_data in enumerate(scenes):
                            if idx < len(scene_ids):
                                scene_id = scene_ids[idx]
                                sora_video_id = scene_data.get('video_id')
                                sora_content_url = scene_data.get('content_url')

                                if sora_video_id and sora_content_url:
                                    # Process video: download, generate thumbnail, upload to Spaces
                                    self.integrator.process_sora_video(
                                        scene_id,
                                        sora_video_id,
                                        sora_content_url,
                                        self.generation_id,
                                        variant_level,
                                        idx + 1  # scene_number (1-indexed)
                                    )

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

        # No assembly needed - Single 12s viral hook
        print("\n✓ Viral hook generated successfully!")
        
        # Get the single hook result
        hook_result = None
        for variant_level, variant_result in generated_variants.items():
            if variant_result['success'] and variant_result.get('scenes'):
                hook_result = {
                    'level': variant_level,
                    'path': variant_result['scenes'][0].get('video_path'),
                    'success': True
                }
                print(f"✓ {variant_level.upper()} Hook: {hook_result['path']}")
                break
        
        if not hook_result:
            print("✗ Hook generation failed")
            hook_result = {'success': False, 'error': 'Generation failed'}

        # Skip evaluation for speed - single hook generation
        evaluations = {}

        # Summary
        elapsed = time.time() - start_time
        print("\n" + "="*70)
        print("VIRAL HOOK GENERATION COMPLETE")
        print("="*70)
        print(f"Time elapsed: {elapsed/60:.1f} minutes")
        print(f"Hook generated: {hook_result['level'].upper() if hook_result.get('success') else 'FAILED'}")
        if hook_result.get('success'):
            print(f"  Path: {hook_result['path']}")

        # Mark generation as completed in history
        if self.integrator and self.generation_id:
            try:
                # Calculate actual cost (1 hook * $0.32/second * 12 seconds)
                actual_cost = 1 * Config.SORA_2_PRO_COST_PER_SECOND * 12  # 12 seconds per hook
                self.integrator.gen_manager.update_generation_status(
                    self.generation_id,
                    'completed',
                    actual_cost=actual_cost
                )
                print(f"✓ Generation {self.generation_id[:8]}... marked as completed")
            except Exception as e:
                print(f"⚠ Failed to mark generation as completed: {e}")

        return {
            'analysis_path': analysis_path,
            'hook_result': hook_result,
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
