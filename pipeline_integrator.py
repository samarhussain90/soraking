"""
Pipeline Integrator - Wraps existing pipeline with generation history tracking
"""
import logging
from typing import List, Dict, Any, Optional

from generation_manager import GenerationManager
from video_storage_manager import VideoStorageManager
from config import Config

logger = logging.getLogger(__name__)

class PipelineIntegrator:
    """
    Integrates generation history tracking into the existing pipeline
    Wraps around AdCloner to save all data to database and download videos
    """

    def __init__(self):
        self.gen_manager = GenerationManager()
        self.video_manager = VideoStorageManager()

    def start_generation(
        self,
        source_video_url: str,
        source_video_type: str,
        variant_types: List[str],
        cost_estimate: float
    ) -> str:
        """
        Create generation record at start of pipeline

        Returns:
            generation_id (UUID string)
        """
        try:
            generation = self.gen_manager.create_generation(
                source_video_url=source_video_url,
                source_video_type=source_video_type,
                variant_types=variant_types,
                cost_estimate=cost_estimate
            )

            generation_id = generation['id']
            logger.info(f"Started generation {generation_id}")

            # Create variant records
            for variant_type in variant_types:
                self.gen_manager.create_variant(
                    generation_id=generation_id,
                    variant_type=variant_type,
                    total_scenes=4
                )

            # Update status to processing
            self.gen_manager.update_generation_status(generation_id, 'processing')

            return generation_id

        except Exception as e:
            logger.error(f"Error starting generation: {e}")
            raise

    def save_analysis_metadata(
        self,
        generation_id: str,
        analysis: Dict[str, Any]
    ):
        """Save video analysis metadata"""
        try:
            self.gen_manager.save_metadata(
                generation_id=generation_id,
                original_analysis=analysis
            )
            logger.info(f"Saved analysis metadata for {generation_id}")
        except Exception as e:
            logger.error(f"Error saving analysis metadata: {e}")

    def save_transformation_metadata(
        self,
        generation_id: str,
        transformation: Dict[str, Any]
    ):
        """Save transformation metadata"""
        try:
            self.gen_manager.save_metadata(
                generation_id=generation_id,
                transformation_data=transformation
            )
            logger.info(f"Saved transformation metadata for {generation_id}")
        except Exception as e:
            logger.error(f"Error saving transformation metadata: {e}")

    def save_prompts_metadata(
        self,
        generation_id: str,
        prompts: Dict[str, Any]
    ):
        """Save Sora prompts metadata"""
        try:
            self.gen_manager.save_metadata(
                generation_id=generation_id,
                prompts_data=prompts
            )
            logger.info(f"Saved prompts metadata for {generation_id}")
        except Exception as e:
            logger.error(f"Error saving prompts metadata: {e}")

    def save_evaluation_metadata(
        self,
        generation_id: str,
        evaluation: Dict[str, Any]
    ):
        """Save evaluation metadata"""
        try:
            self.gen_manager.save_metadata(
                generation_id=generation_id,
                evaluation_data=evaluation
            )
            logger.info(f"Saved evaluation metadata for {generation_id}")
        except Exception as e:
            logger.error(f"Error saving evaluation metadata: {e}")

    def create_scene_records(
        self,
        generation_id: str,
        variant_type: str,
        prompts: List[str]
    ) -> List[str]:
        """
        Create scene records for a variant

        Returns:
            List of scene IDs
        """
        try:
            # Get variant ID
            generation = self.gen_manager.get_generation(generation_id)
            variant_id = None

            for variant in generation.get('variants', []):
                if variant['variant_type'] == variant_type:
                    variant_id = variant['id']
                    break

            if not variant_id:
                raise Exception(f"Variant {variant_type} not found in generation {generation_id}")

            # Create scene records
            scene_ids = []
            for i, prompt in enumerate(prompts, 1):
                scene = self.gen_manager.create_scene(
                    variant_id=variant_id,
                    scene_number=i,
                    sora_prompt=prompt
                )
                scene_ids.append(scene['id'])

            logger.info(f"Created {len(scene_ids)} scene records for variant {variant_type}")
            return scene_ids

        except Exception as e:
            logger.error(f"Error creating scene records: {e}")
            raise

    def process_sora_video(
        self,
        scene_id: str,
        sora_video_id: str,
        sora_content_url: str,
        generation_id: str,
        variant_type: str,
        scene_number: int
    ):
        """
        Download Sora video and save to Spaces
        Updates scene record with video URLs and metadata
        """
        try:
            # Update scene with Sora video ID
            self.gen_manager.update_scene(
                scene_id=scene_id,
                sora_video_id=sora_video_id,
                sora_status='completed',
                status='processing'
            )

            # Download and store video
            logger.info(f"Processing video for scene {scene_id}")

            video_url, thumbnail_url, metadata = self.video_manager.process_and_store_video(
                sora_content_url=sora_content_url,
                openai_api_key=Config.OPENAI_API_KEY,
                generation_id=generation_id,
                variant_type=variant_type,
                scene_number=scene_number
            )

            if not video_url:
                raise Exception("Failed to download and store video")

            # Update scene with video data
            self.gen_manager.update_scene(
                scene_id=scene_id,
                video_url=video_url,
                thumbnail_url=thumbnail_url,
                duration=metadata.get('duration'),
                resolution=metadata.get('resolution'),
                file_size=metadata.get('file_size'),
                status='completed'
            )

            logger.info(f"Scene {scene_id} video saved: {video_url}")

            # Update variant progress
            self._update_variant_progress(scene_id)

        except Exception as e:
            logger.error(f"Error processing Sora video: {e}")
            # Update scene status to failed
            self.gen_manager.update_scene(
                scene_id=scene_id,
                status='failed',
                error_message=str(e)
            )
            raise

    def _update_variant_progress(self, scene_id: str):
        """Update variant progress after scene completion"""
        try:
            # Get scene to find variant
            scenes = self.gen_manager.supabase.table('scenes').select('variant_id').eq('id', scene_id).execute()
            if not scenes.data:
                return

            variant_id = scenes.data[0]['variant_id']

            # Count completed scenes
            completed = self.gen_manager.supabase.table('scenes').select('id').eq('variant_id', variant_id).eq('status', 'completed').execute()
            scenes_completed = len(completed.data) if completed.data else 0

            # Get total scenes
            variant_data = self.gen_manager.supabase.table('variants').select('total_scenes').eq('id', variant_id).execute()
            total_scenes = variant_data.data[0]['total_scenes'] if variant_data.data else 4

            # Update variant
            if scenes_completed >= total_scenes:
                self.gen_manager.update_variant_status(variant_id, 'completed', scenes_completed)
                logger.info(f"Variant {variant_id} completed")
            else:
                self.gen_manager.update_variant_status(variant_id, 'processing', scenes_completed)

            # Check if all variants completed
            self._check_generation_completion(variant_id)

        except Exception as e:
            logger.error(f"Error updating variant progress: {e}")

    def _check_generation_completion(self, variant_id: str):
        """Check if all variants are complete and update generation status"""
        try:
            # Get generation ID
            variant = self.gen_manager.supabase.table('variants').select('generation_id').eq('id', variant_id).execute()
            if not variant.data:
                return

            generation_id = variant.data[0]['generation_id']

            # Get all variants
            all_variants = self.gen_manager.supabase.table('variants').select('status').eq('generation_id', generation_id).execute()

            if not all_variants.data:
                return

            # Check if all completed
            all_completed = all(v['status'] == 'completed' for v in all_variants.data)

            if all_completed:
                self.gen_manager.update_generation_status(generation_id, 'completed')
                logger.info(f"Generation {generation_id} completed")

        except Exception as e:
            logger.error(f"Error checking generation completion: {e}")

    def mark_generation_failed(
        self,
        generation_id: str,
        error_message: str
    ):
        """Mark generation as failed"""
        try:
            self.gen_manager.update_generation_status(
                generation_id=generation_id,
                status='failed',
                error_message=error_message
            )
            logger.info(f"Generation {generation_id} marked as failed")
        except Exception as e:
            logger.error(f"Error marking generation as failed: {e}")
