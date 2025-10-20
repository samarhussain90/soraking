"""
Generation Manager - Handles database operations for generation history
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
import json

from modules.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

class GenerationManager:
    """Manages generation history in database"""

    def __init__(self):
        self.supabase = get_supabase_client()

    def create_generation(
        self,
        source_video_url: str,
        source_video_type: str,
        variant_types: List[str],
        cost_estimate: float
    ) -> Dict[str, Any]:
        """
        Create a new generation record

        Args:
            source_video_url: URL or path to source video
            source_video_type: 'url', 'upload', or 'file'
            variant_types: List of variant types (e.g., ['soft', 'medium'])
            cost_estimate: Estimated cost in dollars

        Returns:
            Created generation record
        """
        try:
            data = {
                'source_video_url': source_video_url,
                'source_video_type': source_video_type,
                'status': 'pending',
                'total_variants': len(variant_types),
                'variant_types': variant_types,
                'cost_estimate': cost_estimate
            }

            result = self.supabase.table('generations').insert(data).execute()

            if result.data:
                generation = result.data[0]
                logger.info(f"Created generation {generation['id']}")
                return generation
            else:
                raise Exception("Failed to create generation record")

        except Exception as e:
            logger.error(f"Error creating generation: {e}")
            raise

    def update_generation_status(
        self,
        generation_id: str,
        status: str,
        error_message: Optional[str] = None,
        actual_cost: Optional[float] = None
    ) -> Dict[str, Any]:
        """Update generation status"""
        try:
            data = {'status': status}

            if status in ['completed', 'failed']:
                data['completed_at'] = datetime.utcnow().isoformat()

            if error_message:
                data['error_message'] = error_message

            if actual_cost is not None:
                data['actual_cost'] = actual_cost

            result = self.supabase.table('generations').update(data).eq('id', generation_id).execute()

            if result.data:
                logger.info(f"Updated generation {generation_id} to status: {status}")
                return result.data[0]
            else:
                raise Exception(f"Failed to update generation {generation_id}")

        except Exception as e:
            logger.error(f"Error updating generation: {e}")
            raise

    def create_variant(
        self,
        generation_id: str,
        variant_type: str,
        total_scenes: int = 4
    ) -> Dict[str, Any]:
        """Create a new variant record"""
        try:
            data = {
                'generation_id': generation_id,
                'variant_type': variant_type,
                'status': 'pending',
                'scenes_completed': 0,
                'total_scenes': total_scenes
            }

            result = self.supabase.table('variants').insert(data).execute()

            if result.data:
                variant = result.data[0]
                logger.info(f"Created variant {variant['id']} ({variant_type})")
                return variant
            else:
                raise Exception("Failed to create variant record")

        except Exception as e:
            logger.error(f"Error creating variant: {e}")
            raise

    def update_variant_status(
        self,
        variant_id: str,
        status: str,
        scenes_completed: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update variant status and progress"""
        try:
            data = {'status': status}

            if status in ['completed', 'failed']:
                data['completed_at'] = datetime.utcnow().isoformat()

            if scenes_completed is not None:
                data['scenes_completed'] = scenes_completed

            if error_message:
                data['error_message'] = error_message

            result = self.supabase.table('variants').update(data).eq('id', variant_id).execute()

            if result.data:
                logger.info(f"Updated variant {variant_id} to status: {status}")
                return result.data[0]
            else:
                raise Exception(f"Failed to update variant {variant_id}")

        except Exception as e:
            logger.error(f"Error updating variant: {e}")
            raise

    def create_scene(
        self,
        variant_id: str,
        scene_number: int,
        sora_prompt: str
    ) -> Dict[str, Any]:
        """Create a new scene record"""
        try:
            data = {
                'variant_id': variant_id,
                'scene_number': scene_number,
                'sora_prompt': sora_prompt,
                'status': 'pending'
            }

            result = self.supabase.table('scenes').insert(data).execute()

            if result.data:
                scene = result.data[0]
                logger.info(f"Created scene {scene['id']} (scene {scene_number})")
                return scene
            else:
                raise Exception("Failed to create scene record")

        except Exception as e:
            logger.error(f"Error creating scene: {e}")
            raise

    def update_scene(
        self,
        scene_id: str,
        sora_video_id: Optional[str] = None,
        sora_status: Optional[str] = None,
        video_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        duration: Optional[int] = None,
        resolution: Optional[str] = None,
        file_size: Optional[int] = None,
        status: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update scene with video data"""
        try:
            data = {}

            if sora_video_id:
                data['sora_video_id'] = sora_video_id
            if sora_status:
                data['sora_status'] = sora_status
            if video_url:
                data['video_url'] = video_url
            if thumbnail_url:
                data['thumbnail_url'] = thumbnail_url
            if duration is not None:
                data['duration'] = duration
            if resolution:
                data['resolution'] = resolution
            if file_size is not None:
                data['file_size'] = file_size
            if status:
                data['status'] = status
                if status in ['completed', 'failed']:
                    data['completed_at'] = datetime.utcnow().isoformat()
            if error_message:
                data['error_message'] = error_message

            result = self.supabase.table('scenes').update(data).eq('id', scene_id).execute()

            if result.data:
                logger.info(f"Updated scene {scene_id}")
                return result.data[0]
            else:
                raise Exception(f"Failed to update scene {scene_id}")

        except Exception as e:
            logger.error(f"Error updating scene: {e}")
            raise

    def save_metadata(
        self,
        generation_id: str,
        original_analysis: Optional[Dict] = None,
        transformation_data: Optional[Dict] = None,
        prompts_data: Optional[Dict] = None,
        evaluation_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Save generation metadata (analysis, prompts, etc.)"""
        try:
            data = {
                'generation_id': generation_id
            }

            if original_analysis:
                data['original_analysis'] = json.dumps(original_analysis)
            if transformation_data:
                data['transformation_data'] = json.dumps(transformation_data)
            if prompts_data:
                data['prompts_data'] = json.dumps(prompts_data)
            if evaluation_data:
                data['evaluation_data'] = json.dumps(evaluation_data)

            # Check if metadata already exists
            existing = self.supabase.table('generation_metadata').select('id').eq('generation_id', generation_id).execute()

            if existing.data:
                # Update existing
                result = self.supabase.table('generation_metadata').update(data).eq('generation_id', generation_id).execute()
            else:
                # Insert new
                result = self.supabase.table('generation_metadata').insert(data).execute()

            if result.data:
                logger.info(f"Saved metadata for generation {generation_id}")
                return result.data[0]
            else:
                raise Exception("Failed to save metadata")

        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            raise

    def get_generation(self, generation_id: str) -> Optional[Dict[str, Any]]:
        """Get generation by ID with all related data"""
        try:
            result = self.supabase.table('generations').select('*, variants(*, scenes(*)), generation_metadata(*)').eq('id', generation_id).execute()

            if result.data:
                return result.data[0]
            return None

        except Exception as e:
            logger.error(f"Error getting generation: {e}")
            return None

    def list_generations(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all generations with pagination"""
        try:
            query = self.supabase.table('generations').select('*, variants(*)').order('created_at', desc=True).range(offset, offset + limit - 1)

            if status:
                query = query.eq('status', status)

            result = query.execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Error listing generations: {e}")
            return []

    def get_variant_scenes(self, variant_id: str) -> List[Dict[str, Any]]:
        """Get all scenes for a variant"""
        try:
            result = self.supabase.table('scenes').select('*').eq('variant_id', variant_id).order('scene_number').execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Error getting variant scenes: {e}")
            return []

    def delete_generation(self, generation_id: str) -> bool:
        """Delete a generation and all related data (cascades)"""
        try:
            result = self.supabase.table('generations').delete().eq('id', generation_id).execute()

            logger.info(f"Deleted generation {generation_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting generation: {e}")
            return False
