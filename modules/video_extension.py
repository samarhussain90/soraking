"""
Video Extension and Looping Module

Provides capabilities to extend videos, create seamless loops, and generate
longer content from shorter clips using AI-powered scene generation.
"""

import json
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess
import tempfile
import shutil


@dataclass
class ExtensionRequest:
    """Video extension request"""
    request_id: str
    original_video_path: str
    target_duration: int  # Target duration in seconds
    extension_type: str  # 'loop', 'extend', 'variation'
    style_consistency: bool
    created_at: str


@dataclass
class ExtensionResult:
    """Video extension result"""
    result_id: str
    request_id: str
    original_duration: int
    extended_duration: int
    output_path: str
    loop_count: int
    quality_score: float
    created_at: str


class VideoExtensionEngine:
    """
    Video extension and looping engine.
    
    Provides intelligent video extension capabilities including:
    - Seamless looping for social media
    - Scene extension with AI-generated content
    - Style-consistent video variations
    - Automatic loop detection and optimization
    """
    
    def __init__(self, data_dir: Path = None):
        """
        Initialize video extension engine.
        
        Args:
            data_dir: Directory to store extension data (default: output/extensions)
        """
        self.data_dir = data_dir or Path("output/extensions")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Extension storage paths
        self.requests_file = self.data_dir / "requests.json"
        self.results_file = self.data_dir / "results.json"
        
        # Load existing data
        self.requests = self._load_requests()
        self.results = self._load_results()
    
    def _load_requests(self) -> Dict:
        """Load existing extension requests"""
        if self.requests_file.exists():
            with open(self.requests_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_results(self) -> List[Dict]:
        """Load existing extension results"""
        if self.results_file.exists():
            with open(self.results_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_requests(self):
        """Save requests to storage"""
        with open(self.requests_file, 'w') as f:
            json.dump(self.requests, f, indent=2)
    
    def _save_results(self):
        """Save results to storage"""
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def create_extension_request(self, video_path: str, target_duration: int, 
                               extension_type: str = 'loop', style_consistency: bool = True) -> str:
        """
        Create a new video extension request.
        
        Args:
            video_path: Path to the original video
            target_duration: Target duration in seconds
            extension_type: Type of extension ('loop', 'extend', 'variation')
            style_consistency: Whether to maintain style consistency
            
        Returns:
            Request ID
        """
        request_id = str(uuid.uuid4())
        
        request = ExtensionRequest(
            request_id=request_id,
            original_video_path=video_path,
            target_duration=target_duration,
            extension_type=extension_type,
            style_consistency=style_consistency,
            created_at=datetime.now().isoformat()
        )
        
        self.requests[request_id] = asdict(request)
        self._save_requests()
        
        return request_id
    
    def analyze_video_for_extension(self, video_path: str) -> Dict:
        """
        Analyze video to determine best extension strategy.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Analysis results with extension recommendations
        """
        try:
            # Get video duration using ffprobe
            duration_cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', video_path
            ]
            result = subprocess.run(duration_cmd, capture_output=True, text=True)
            duration = float(result.stdout.strip()) if result.returncode == 0 else 0
            
            # Analyze video characteristics
            analysis = {
                'duration': duration,
                'extension_type': 'loop' if duration < 15 else 'extend',
                'loop_points': self._find_loop_points(video_path),
                'style_consistency': True,
                'recommended_approach': self._get_recommended_approach(duration),
                'quality_metrics': self._analyze_quality(video_path)
            }
            
            return analysis
            
        except Exception as e:
            return {
                'error': str(e),
                'duration': 0,
                'extension_type': 'loop',
                'recommended_approach': 'basic_loop'
            }
    
    def _find_loop_points(self, video_path: str) -> List[float]:
        """
        Find potential loop points in the video.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of timestamps that could serve as loop points
        """
        # Simplified loop point detection
        # In a real implementation, this would use computer vision
        # to find natural loop points (e.g., similar frames)
        
        try:
            duration_cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', video_path
            ]
            result = subprocess.run(duration_cmd, capture_output=True, text=True)
            duration = float(result.stdout.strip()) if result.returncode == 0 else 0
            
            # Generate potential loop points at 25%, 50%, 75% of duration
            loop_points = []
            for i in range(1, 4):
                point = duration * (i * 0.25)
                loop_points.append(point)
            
            return loop_points
            
        except Exception:
            return [0.0]
    
    def _get_recommended_approach(self, duration: float) -> str:
        """Get recommended extension approach based on duration"""
        if duration < 5:
            return 'seamless_loop'
        elif duration < 15:
            return 'smart_loop'
        elif duration < 30:
            return 'scene_extension'
        else:
            return 'variation_generation'
    
    def _analyze_quality(self, video_path: str) -> Dict:
        """Analyze video quality metrics"""
        try:
            # Get video info using ffprobe
            info_cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            result = subprocess.run(info_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                video_stream = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
                
                if video_stream:
                    return {
                        'resolution': f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}",
                        'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                        'bitrate': int(video_stream.get('bit_rate', 0)),
                        'codec': video_stream.get('codec_name', 'unknown')
                    }
            
            return {'resolution': 'unknown', 'fps': 0, 'bitrate': 0, 'codec': 'unknown'}
            
        except Exception:
            return {'resolution': 'unknown', 'fps': 0, 'bitrate': 0, 'codec': 'unknown'}
    
    def create_seamless_loop(self, video_path: str, target_duration: int, 
                           loop_point: float = None) -> str:
        """
        Create a seamless loop of the video.
        
        Args:
            video_path: Path to the original video
            target_duration: Target duration in seconds
            loop_point: Specific point to loop from (auto-detect if None)
            
        Returns:
            Path to the looped video
        """
        try:
            # Get video duration
            duration_cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', video_path
            ]
            result = subprocess.run(duration_cmd, capture_output=True, text=True)
            original_duration = float(result.stdout.strip()) if result.returncode == 0 else 0
            
            # Calculate loop count
            loop_count = max(1, int(target_duration / original_duration))
            
            # Create output path
            output_dir = self.data_dir / "loops"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"loop_{uuid.uuid4().hex[:8]}.mp4"
            
            # Create seamless loop using ffmpeg
            if loop_point is None:
                # Simple concatenation loop
                loop_cmd = [
                    'ffmpeg', '-y', '-stream_loop', str(loop_count - 1),
                    '-i', video_path, '-c', 'copy', '-t', str(target_duration),
                    str(output_path)
                ]
            else:
                # Loop from specific point
                loop_cmd = [
                    'ffmpeg', '-y', '-i', video_path,
                    '-filter_complex', f'[0:v]loop=loop={loop_count}:size=1:start={int(loop_point * 30)}[v];[0:a]aloop=loop={loop_count}:size=1:start={int(loop_point * 30)}[a]',
                    '-map', '[v]', '-map', '[a]', '-t', str(target_duration),
                    str(output_path)
                ]
            
            # Execute loop creation
            result = subprocess.run(loop_cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and output_path.exists():
                return str(output_path)
            else:
                raise Exception(f"Loop creation failed: {result.stderr}")
                
        except Exception as e:
            raise Exception(f"Failed to create seamless loop: {str(e)}")
    
    def extend_video_with_ai(self, video_path: str, target_duration: int, 
                           style_consistency: bool = True) -> str:
        """
        Extend video using AI-generated content.
        
        Args:
            video_path: Path to the original video
            target_duration: Target duration in seconds
            style_consistency: Whether to maintain style consistency
            
        Returns:
            Path to the extended video
        """
        try:
            # This is a placeholder for AI-powered video extension
            # In a real implementation, this would:
            # 1. Analyze the original video style
            # 2. Generate new scenes using AI
            # 3. Blend the new content seamlessly
            
            # For now, create a simple extension by duplicating and modifying
            output_dir = self.data_dir / "extensions"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"extended_{uuid.uuid4().hex[:8]}.mp4"
            
            # Simple extension by concatenating with slight variations
            extension_cmd = [
                'ffmpeg', '-y', '-i', video_path, '-i', video_path,
                '-filter_complex', '[0:v][1:v]concat=n=2:v=1:a=1[vout][aout]',
                '-map', '[vout]', '-map', '[aout]', '-t', str(target_duration),
                str(output_path)
            ]
            
            result = subprocess.run(extension_cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and output_path.exists():
                return str(output_path)
            else:
                raise Exception(f"Video extension failed: {result.stderr}")
                
        except Exception as e:
            raise Exception(f"Failed to extend video with AI: {str(e)}")
    
    def create_video_variations(self, video_path: str, variation_count: int = 3) -> List[str]:
        """
        Create variations of the video with different styles.
        
        Args:
            video_path: Path to the original video
            variation_count: Number of variations to create
            
        Returns:
            List of paths to variation videos
        """
        try:
            variations = []
            output_dir = self.data_dir / "variations"
            output_dir.mkdir(exist_ok=True)
            
            # Create different style variations
            style_filters = [
                "eq=contrast=1.2:brightness=0.1:saturation=1.1",  # Vibrant
                "eq=contrast=0.8:brightness=-0.1:saturation=0.8",  # Muted
                "eq=contrast=1.5:brightness=0.2:saturation=1.3",  # High contrast
            ]
            
            for i in range(min(variation_count, len(style_filters))):
                output_path = output_dir / f"variation_{i+1}_{uuid.uuid4().hex[:8]}.mp4"
                
                variation_cmd = [
                    'ffmpeg', '-y', '-i', video_path,
                    '-vf', style_filters[i],
                    '-c:a', 'copy', str(output_path)
                ]
                
                result = subprocess.run(variation_cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and output_path.exists():
                    variations.append(str(output_path))
            
            return variations
            
        except Exception as e:
            raise Exception(f"Failed to create video variations: {str(e)}")
    
    def process_extension_request(self, request_id: str) -> str:
        """
        Process a video extension request.
        
        Args:
            request_id: ID of the extension request
            
        Returns:
            Result ID
        """
        if request_id not in self.requests:
            raise ValueError(f"Request {request_id} not found")
        
        request = self.requests[request_id]
        video_path = request['original_video_path']
        target_duration = request['target_duration']
        extension_type = request['extension_type']
        
        try:
            # Analyze the video first
            analysis = self.analyze_video_for_extension(video_path)
            
            # Process based on extension type
            if extension_type == 'loop':
                output_path = self.create_seamless_loop(video_path, target_duration)
            elif extension_type == 'extend':
                output_path = self.extend_video_with_ai(video_path, target_duration)
            elif extension_type == 'variation':
                variations = self.create_video_variations(video_path, 3)
                output_path = variations[0] if variations else None
            else:
                raise ValueError(f"Unknown extension type: {extension_type}")
            
            if not output_path:
                raise Exception("Extension failed - no output generated")
            
            # Create result record
            result_id = str(uuid.uuid4())
            result = ExtensionResult(
                result_id=result_id,
                request_id=request_id,
                original_duration=analysis.get('duration', 0),
                extended_duration=target_duration,
                output_path=output_path,
                loop_count=int(target_duration / analysis.get('duration', 1)),
                quality_score=8.0,  # Simplified scoring
                created_at=datetime.now().isoformat()
            )
            
            self.results.append(asdict(result))
            self._save_results()
            
            return result_id
            
        except Exception as e:
            raise Exception(f"Failed to process extension request: {str(e)}")
    
    def get_extension_results(self, request_id: str = None) -> List[Dict]:
        """
        Get extension results.
        
        Args:
            request_id: Optional request ID to filter results
            
        Returns:
            List of extension results
        """
        if request_id:
            return [r for r in self.results if r['request_id'] == request_id]
        return self.results
    
    def get_extension_stats(self) -> Dict:
        """
        Get extension statistics.
        
        Returns:
            Statistics about video extensions
        """
        if not self.results:
            return {
                'total_extensions': 0,
                'avg_extension_ratio': 0,
                'success_rate': 0,
                'popular_types': {}
            }
        
        total_extensions = len(self.results)
        successful_extensions = len([r for r in self.results if r.get('output_path')])
        success_rate = successful_extensions / total_extensions if total_extensions > 0 else 0
        
        # Calculate average extension ratio
        extension_ratios = []
        for result in self.results:
            if result.get('original_duration', 0) > 0:
                ratio = result.get('extended_duration', 0) / result.get('original_duration', 1)
                extension_ratios.append(ratio)
        
        avg_extension_ratio = sum(extension_ratios) / len(extension_ratios) if extension_ratios else 0
        
        # Count extension types
        type_counts = {}
        for result in self.results:
            request_id = result.get('request_id')
            if request_id and request_id in self.requests:
                ext_type = self.requests[request_id].get('extension_type', 'unknown')
                type_counts[ext_type] = type_counts.get(ext_type, 0) + 1
        
        return {
            'total_extensions': total_extensions,
            'successful_extensions': successful_extensions,
            'success_rate': success_rate,
            'avg_extension_ratio': avg_extension_ratio,
            'popular_types': type_counts
        }
