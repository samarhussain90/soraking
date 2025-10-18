"""
Sora Client - Parallel Video Generation
Handles async Sora API calls, progress monitoring, and video downloads
"""
import time
import asyncio
import requests
from typing import Dict, List, Optional
from pathlib import Path
from openai import OpenAI

from config import Config


class SoraClient:
    """Client for interacting with Sora API via direct REST calls"""

    def __init__(self, spaces_client=None, session_id=None):
        """
        Initialize OpenAI client and REST session

        Args:
            spaces_client: Optional SpacesClient for cloud uploads
            session_id: Optional session ID for organizing uploads
        """
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.api_key = Config.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1/videos"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.spaces_client = spaces_client
        self.session_id = session_id

    def create_video(self, prompt: str, **kwargs) -> Dict:
        """
        Create a single video generation job

        Args:
            prompt: Sora prompt
            **kwargs: Additional parameters (model, size, seconds)

        Returns:
            Job dictionary with id and status
        """
        params = {
            'model': kwargs.get('model', Config.SORA_MODEL),
            'prompt': prompt,
            'size': kwargs.get('size', Config.SORA_RESOLUTION),
            'seconds': kwargs.get('seconds', Config.SORA_DURATION)
        }

        print(f"Creating video job... ({params['model']}, {params['size']}, {params['seconds']}s)")
        print(f"▸ API URL: {self.base_url}")
        print(f"▸ Prompt length: {len(prompt)} characters")

        try:
            # Direct REST API call
            print(f"▸ Sending POST request to Sora API...")
            response = requests.post(self.base_url, headers=self.headers, json=params, timeout=30)

            print(f"▸ Response status code: {response.status_code}")

            if response.status_code != 200:
                print(f"✗ API Error: {response.status_code}")
                print(f"▸ Response body: {response.text[:500]}")

            response.raise_for_status()
            data = response.json()

            print(f"▸ Response data keys: {list(data.keys())}")

            job = {
                'id': data.get('id'),
                'status': data.get('status', 'queued'),
                'model': data.get('model'),
                'size': data.get('size'),
                'seconds': data.get('seconds'),
                'progress': data.get('progress', 0),
                'created_at': data.get('created_at', int(time.time()))
            }

            print(f"✓ Job created: {job['id']}")
            return job

        except requests.exceptions.RequestException as e:
            print(f"✗ Sora API request failed: {str(e)}")
            print(f"▸ Error type: {type(e).__name__}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"▸ Response status: {e.response.status_code}")
                print(f"▸ Response body: {e.response.text[:500]}")
            raise

    def get_video_status(self, video_id: str) -> Dict:
        """
        Get status of a video generation job

        Args:
            video_id: Video job ID

        Returns:
            Status dictionary
        """
        # Direct REST API call
        response = requests.get(f"{self.base_url}/{video_id}", headers=self.headers)
        response.raise_for_status()
        data = response.json()

        return {
            'id': data.get('id'),
            'status': data.get('status', 'processing'),
            'progress': data.get('progress', 0),
            'model': data.get('model'),
            'completed_at': data.get('completed_at'),
            'error': data.get('error')
        }

    def wait_for_completion(self, video_id: str, poll_interval: int = 15) -> Dict:
        """
        Poll until video is complete

        Args:
            video_id: Video job ID
            poll_interval: Seconds between polls

        Returns:
            Final status dictionary
        """
        print(f"Monitoring job {video_id}...")

        while True:
            status = self.get_video_status(video_id)

            if status['status'] == 'completed':
                print(f"✓ Job {video_id} completed!")
                return status
            elif status['status'] == 'failed':
                print(f"✗ Job {video_id} failed: {status.get('error')}")
                return status
            else:
                progress = status.get('progress', 0)
                print(f"  Progress: {progress}% [{status['status']}]")
                time.sleep(poll_interval)

    def download_video(self, video_id: str, output_path: Optional[str] = None) -> Dict:
        """
        Download completed video and optionally upload to Spaces

        Args:
            video_id: Video job ID
            output_path: Optional custom output path

        Returns:
            Dict with local_path and cloud_url (if uploaded)
        """
        if output_path is None:
            output_path = Config.VIDEOS_DIR / f"{video_id}.mp4"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Downloading video {video_id}...")

        # Download content via REST API
        download_headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(f"{self.base_url}/{video_id}/content", headers=download_headers, stream=True)
        response.raise_for_status()

        # Save to file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"✓ Saved to: {output_path}")

        # Upload to Spaces if client available
        cloud_url = None
        if self.spaces_client and self.session_id:
            try:
                print(f"  Uploading to Spaces...")
                cloud_url = self.spaces_client.upload_session_video(
                    self.session_id,
                    str(output_path),
                    'generated'
                )
                print(f"  ✓ Uploaded: {cloud_url}")
            except Exception as e:
                print(f"  ⚠ Spaces upload failed: {e}")

        return {
            'local_path': str(output_path),
            'cloud_url': cloud_url
        }

    def generate_scene(self, scene_prompt_data: Dict, output_dir: Optional[Path] = None) -> Dict:
        """
        Generate a single scene from prompt data

        Args:
            scene_prompt_data: Dictionary with scene info and prompt
            output_dir: Optional output directory

        Returns:
            Result dictionary with video path
        """
        prompt = scene_prompt_data['prompt']
        scene_number = scene_prompt_data.get('scene_number', 1)

        # Create job
        job = self.create_video(prompt)

        # Wait for completion
        result = self.wait_for_completion(job['id'])

        if result['status'] == 'completed':
            # Download video
            filename = f"scene_{scene_number:02d}_{job['id']}.mp4"
            if output_dir:
                output_path = output_dir / filename
            else:
                output_path = Config.VIDEOS_DIR / filename

            download_result = self.download_video(job['id'], str(output_path))

            return {
                'scene_number': scene_number,
                'job_id': job['id'],
                'status': 'completed',
                'video_path': download_result['local_path'],
                'cloud_url': download_result.get('cloud_url')
            }
        else:
            return {
                'scene_number': scene_number,
                'job_id': job['id'],
                'status': 'failed',
                'error': result.get('error')
            }

    def generate_variant_parallel(self, scene_prompts: List[Dict], variant_name: str) -> Dict:
        """
        Generate all scenes for a variant in parallel

        Args:
            scene_prompts: List of scene prompt dictionaries
            variant_name: Name of variant (e.g., "soft", "aggressive")

        Returns:
            Dictionary with all scene results
        """
        print(f"\n{'='*70}")
        print(f"GENERATING VARIANT: {variant_name.upper()}")
        print(f"Scenes: {len(scene_prompts)}")
        print(f"{'='*70}\n")

        # Create output directory for this variant
        variant_dir = Config.VIDEOS_DIR / variant_name
        variant_dir.mkdir(parents=True, exist_ok=True)

        # Start all jobs
        jobs = []
        for scene_data in scene_prompts:
            print(f"\nStarting Scene {scene_data.get('scene_number')}...")
            job = self.create_video(scene_data['prompt'])
            jobs.append({
                'job_id': job['id'],
                'scene_number': scene_data.get('scene_number'),
                'scene_data': scene_data
            })

        print(f"\n✓ All {len(jobs)} jobs started. Monitoring progress...")

        # Monitor all jobs
        completed_videos = []
        pending_jobs = jobs.copy()

        while pending_jobs:
            print(f"\n--- Progress Update ---")
            print(f"Pending: {len(pending_jobs)} | Completed: {len(completed_videos)}")

            for job in pending_jobs[:]:  # Copy list to modify during iteration
                status = self.get_video_status(job['job_id'])

                if status['status'] == 'completed':
                    print(f"  Scene {job['scene_number']}: COMPLETED ✓")

                    # Download video
                    filename = f"scene_{job['scene_number']:02d}.mp4"
                    download_result = self.download_video(
                        job['job_id'],
                        str(variant_dir / filename)
                    )

                    completed_videos.append({
                        'scene_number': job['scene_number'],
                        'video_path': download_result['local_path'],
                        'cloud_url': download_result.get('cloud_url'),
                        'job_id': job['job_id']
                    })

                    pending_jobs.remove(job)

                elif status['status'] == 'failed':
                    print(f"  Scene {job['scene_number']}: FAILED ✗")
                    completed_videos.append({
                        'scene_number': job['scene_number'],
                        'status': 'failed',
                        'error': status.get('error')
                    })
                    pending_jobs.remove(job)

                else:
                    progress = status.get('progress', 0)
                    print(f"  Scene {job['scene_number']}: {progress}% [{status['status']}]")

            if pending_jobs:
                time.sleep(15)  # Poll every 15 seconds

        # Sort by scene number
        completed_videos.sort(key=lambda x: x['scene_number'])

        print(f"\n{'='*70}")
        print(f"VARIANT COMPLETE: {variant_name.upper()}")
        print(f"Generated {len(completed_videos)} scenes")
        print(f"{'='*70}\n")

        return {
            'variant_name': variant_name,
            'variant_dir': str(variant_dir),
            'scenes': completed_videos,
            'total_scenes': len(completed_videos),
            'success': all(v.get('status') != 'failed' for v in completed_videos)
        }


# Test function
if __name__ == "__main__":
    import json

    # Test with a simple prompt
    client = SoraClient()

    test_prompt = """
    [00:00-00:04] Close-up: Professional woman, early 30s, in modern office.
    Warm natural lighting. She looks directly at camera with confident expression.

    [00:04-00:08] Camera slowly pushes in. She leans forward slightly,
    building rapport with viewer. Lighting stays consistent.

    [00:08-00:12] Her expression shifts to concerned. Text overlay appears.
    Camera holds steady.

    Cinematography: 35mm, professional, direct address
    Mood: Relatable, building trust
    """

    scene_data = {
        'scene_number': 1,
        'prompt': test_prompt
    }

    print("Testing Sora client...")
    result = client.generate_scene(scene_data)
    print(json.dumps(result, indent=2))
