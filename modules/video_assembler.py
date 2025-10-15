"""
Video Assembler
Stitches multiple scene videos into final ads using ffmpeg
"""
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

from config import Config


class VideoAssembler:
    """Assembles scene videos into complete ads"""

    def __init__(self):
        """Check if ffmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            self.ffmpeg_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("WARNING: ffmpeg not found. Install with: brew install ffmpeg")
            self.ffmpeg_available = False

    def stitch_scenes(self, scene_videos: List[str], output_path: str) -> str:
        """
        Stitch multiple scene videos into one

        Args:
            scene_videos: List of paths to scene videos (in order)
            output_path: Path for final video

        Returns:
            Path to stitched video
        """
        if not self.ffmpeg_available:
            raise RuntimeError("ffmpeg is required for video assembly")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create concat file
        concat_file = output_path.parent / "concat_list.txt"
        with open(concat_file, 'w') as f:
            for video_path in scene_videos:
                f.write(f"file '{Path(video_path).absolute()}'\n")

        # Stitch with ffmpeg
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            '-y',  # Overwrite output file
            str(output_path)
        ]

        print(f"Stitching {len(scene_videos)} scenes...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")

        # Clean up concat file
        concat_file.unlink()

        print(f"✓ Stitched video: {output_path}")
        return str(output_path)

    def assemble_variant(self, variant_result: Dict, output_filename: Optional[str] = None) -> str:
        """
        Assemble all scenes from a variant result into final ad

        Args:
            variant_result: Result dictionary from SoraClient.generate_variant_parallel
            output_filename: Optional custom output filename

        Returns:
            Path to final assembled video
        """
        variant_name = variant_result['variant_name']
        scenes = variant_result['scenes']

        # Extract video paths (only successful scenes)
        video_paths = [
            scene['video_path']
            for scene in scenes
            if 'video_path' in scene
        ]

        if not video_paths:
            raise ValueError("No completed videos to assemble")

        # Sort by scene number to ensure correct order
        video_paths.sort()

        # Create output path
        if output_filename:
            output_path = Config.VIDEOS_DIR / output_filename
        else:
            output_path = Config.VIDEOS_DIR / f"final_{variant_name}.mp4"

        # Stitch scenes
        final_path = self.stitch_scenes(video_paths, str(output_path))

        return final_path

    def add_audio_overlay(self, video_path: str, audio_path: str, output_path: Optional[str] = None) -> str:
        """
        Add audio/voiceover to video

        Args:
            video_path: Path to video
            audio_path: Path to audio file
            output_path: Optional output path

        Returns:
            Path to video with audio
        """
        if not self.ffmpeg_available:
            raise RuntimeError("ffmpeg is required")

        if output_path is None:
            video_path_obj = Path(video_path)
            output_path = video_path_obj.parent / f"{video_path_obj.stem}_with_audio.mp4"

        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-y',
            str(output_path)
        ]

        print(f"Adding audio overlay...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")

        print(f"✓ Audio added: {output_path}")
        return str(output_path)


# Test function
if __name__ == "__main__":
    assembler = VideoAssembler()

    # Test stitching (requires actual video files)
    test_videos = input("Enter comma-separated paths to test videos (or press Enter to skip): ")

    if test_videos:
        video_paths = [p.strip() for p in test_videos.split(',')]
        output = Config.VIDEOS_DIR / "test_stitched.mp4"

        result = assembler.stitch_scenes(video_paths, str(output))
        print(f"\nTest complete: {result}")
    else:
        print("Skipping test - no videos provided")
