"""
Video Storage Manager - Downloads and stores videos to DigitalOcean Spaces
"""
import logging
import os
import hashlib
import subprocess
from datetime import datetime
from typing import Dict, Optional, Tuple
import requests
from pathlib import Path

from modules.spaces_client import SpacesClient

logger = logging.getLogger(__name__)

class VideoStorageManager:
    """Manages video download and storage to DigitalOcean Spaces"""

    def __init__(self):
        self.spaces = SpacesClient()
        self.temp_dir = Path("/tmp/soraking_videos")
        self.temp_dir.mkdir(exist_ok=True)

    def download_sora_video(
        self,
        video_content_url: str,
        openai_api_key: str
    ) -> Optional[str]:
        """
        Download video from Sora API content URL

        Args:
            video_content_url: The content URL from Sora API
            openai_api_key: OpenAI API key for authentication

        Returns:
            Path to downloaded video file, or None if failed
        """
        try:
            logger.info(f"Downloading video from Sora API: {video_content_url}")

            # Create unique filename based on URL hash
            url_hash = hashlib.md5(video_content_url.encode()).hexdigest()[:12]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file = self.temp_dir / f"sora_{timestamp}_{url_hash}.mp4"

            # Download video with authentication
            headers = {
                'Authorization': f'Bearer {openai_api_key}'
            }

            response = requests.get(video_content_url, headers=headers, stream=True, timeout=300)
            response.raise_for_status()

            # Save to temp file
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            file_size = temp_file.stat().st_size
            logger.info(f"Downloaded video: {temp_file} ({file_size / 1024 / 1024:.2f} MB)")

            return str(temp_file)

        except Exception as e:
            logger.error(f"Error downloading Sora video: {e}")
            return None

    def generate_thumbnail(self, video_path: str) -> Optional[str]:
        """
        Generate thumbnail from video using ffmpeg

        Args:
            video_path: Path to video file

        Returns:
            Path to generated thumbnail, or None if failed
        """
        try:
            thumbnail_path = str(Path(video_path).with_suffix('.jpg'))

            # Use ffmpeg to extract frame at 1 second
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', '00:00:01',
                '-vframes', '1',
                '-vf', 'scale=640:-1',  # 640px width, maintain aspect ratio
                '-y',  # Overwrite output
                thumbnail_path
            ]

            subprocess.run(cmd, check=True, capture_output=True)

            logger.info(f"Generated thumbnail: {thumbnail_path}")
            return thumbnail_path

        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return None

    def get_video_metadata(self, video_path: str) -> Dict[str, any]:
        """
        Get video metadata using ffprobe

        Args:
            video_path: Path to video file

        Returns:
            Dict with duration, resolution, file_size
        """
        try:
            # Get duration and resolution using ffprobe
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration:stream=width,height',
                '-of', 'json',
                video_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            data = json.loads(result.stdout)

            duration = int(float(data['format']['duration']))
            width = data['streams'][0]['width']
            height = data['streams'][0]['height']
            resolution = f"{width}x{height}"

            file_size = Path(video_path).stat().st_size

            return {
                'duration': duration,
                'resolution': resolution,
                'file_size': file_size
            }

        except Exception as e:
            logger.error(f"Error getting video metadata: {e}")
            return {
                'duration': None,
                'resolution': None,
                'file_size': Path(video_path).stat().st_size if Path(video_path).exists() else None
            }

    def upload_video_to_spaces(
        self,
        video_path: str,
        generation_id: str,
        variant_type: str,
        scene_number: int
    ) -> Optional[str]:
        """
        Upload video to DigitalOcean Spaces

        Args:
            video_path: Local path to video file
            generation_id: Generation UUID
            variant_type: Variant type (soft, medium, etc.)
            scene_number: Scene number (1-4)

        Returns:
            Public URL to uploaded video, or None if failed
        """
        try:
            # Create organized path: generations/{gen_id}/{variant_type}/scene_{num}.mp4
            filename = f"generations/{generation_id}/{variant_type}/scene_{scene_number}.mp4"

            logger.info(f"Uploading video to Spaces: {filename}")

            # Upload to Spaces
            url = self.spaces.upload_video(video_path, filename)

            if url:
                logger.info(f"Video uploaded successfully: {url}")
                return url
            else:
                logger.error("Failed to upload video to Spaces")
                return None

        except Exception as e:
            logger.error(f"Error uploading video to Spaces: {e}")
            return None

    def upload_thumbnail_to_spaces(
        self,
        thumbnail_path: str,
        generation_id: str,
        variant_type: str,
        scene_number: int
    ) -> Optional[str]:
        """
        Upload thumbnail to DigitalOcean Spaces

        Args:
            thumbnail_path: Local path to thumbnail file
            generation_id: Generation UUID
            variant_type: Variant type
            scene_number: Scene number

        Returns:
            Public URL to uploaded thumbnail, or None if failed
        """
        try:
            filename = f"generations/{generation_id}/{variant_type}/scene_{scene_number}_thumb.jpg"

            logger.info(f"Uploading thumbnail to Spaces: {filename}")

            # Note: upload_video works for images too (ContentType is set by spaces_client)
            url = self.spaces.upload_video(thumbnail_path, filename)

            if url:
                logger.info(f"Thumbnail uploaded successfully: {url}")
                return url
            else:
                logger.error("Failed to upload thumbnail to Spaces")
                return None

        except Exception as e:
            logger.error(f"Error uploading thumbnail to Spaces: {e}")
            return None

    def process_and_store_video(
        self,
        sora_content_url: str,
        openai_api_key: str,
        generation_id: str,
        variant_type: str,
        scene_number: int
    ) -> Tuple[Optional[str], Optional[str], Optional[Dict]]:
        """
        Complete workflow: Download, process, and store video

        Args:
            sora_content_url: Sora API video content URL
            openai_api_key: OpenAI API key
            generation_id: Generation UUID
            variant_type: Variant type
            scene_number: Scene number

        Returns:
            Tuple of (video_url, thumbnail_url, metadata)
        """
        video_path = None
        thumbnail_path = None

        try:
            # Step 1: Download video from Sora
            video_path = self.download_sora_video(sora_content_url, openai_api_key)
            if not video_path:
                return None, None, None

            # Step 2: Get video metadata
            metadata = self.get_video_metadata(video_path)

            # Step 3: Generate thumbnail
            thumbnail_path = self.generate_thumbnail(video_path)

            # Step 4: Upload video to Spaces
            video_url = self.upload_video_to_spaces(
                video_path,
                generation_id,
                variant_type,
                scene_number
            )

            if not video_url:
                return None, None, metadata

            # Step 5: Upload thumbnail to Spaces (if generated)
            thumbnail_url = None
            if thumbnail_path:
                thumbnail_url = self.upload_thumbnail_to_spaces(
                    thumbnail_path,
                    generation_id,
                    variant_type,
                    scene_number
                )

            return video_url, thumbnail_url, metadata

        except Exception as e:
            logger.error(f"Error in process_and_store_video: {e}")
            return None, None, None

        finally:
            # Cleanup temp files
            try:
                if video_path and Path(video_path).exists():
                    Path(video_path).unlink()
                    logger.info(f"Cleaned up temp video: {video_path}")

                if thumbnail_path and Path(thumbnail_path).exists():
                    Path(thumbnail_path).unlink()
                    logger.info(f"Cleaned up temp thumbnail: {thumbnail_path}")
            except Exception as cleanup_error:
                logger.warning(f"Error cleaning up temp files: {cleanup_error}")

    def cleanup_temp_directory(self, max_age_hours: int = 24):
        """Remove old temporary files"""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600

            for file in self.temp_dir.glob("*"):
                if file.is_file():
                    file_age = current_time - file.stat().st_mtime
                    if file_age > max_age_seconds:
                        file.unlink()
                        logger.info(f"Cleaned up old temp file: {file}")

        except Exception as e:
            logger.error(f"Error cleaning temp directory: {e}")
