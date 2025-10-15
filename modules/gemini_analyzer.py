"""
Gemini 2.5 Video Analyzer
Analyzes winning ads and extracts complete breakdown
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import google.generativeai as genai

from config import Config


class GeminiVideoAnalyzer:
    """Analyzes video ads using Gemini 2.5 Pro"""

    def __init__(self):
        """Initialize Gemini client"""
        # Disable discovery cache to prevent stale API schema errors
        import os
        os.environ['GOOGLE_API_USE_CLIENT_CERTIFICATE'] = 'false'

        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)

    def upload_video(self, video_path: str):
        """
        Upload video to Gemini File API using REST API directly

        Args:
            video_path: Path to video file or YouTube URL

        Returns:
            Uploaded file object
        """
        print(f"Uploading video: {video_path}")

        # Use REST API directly to bypass discovery cache bug
        import requests
        import mimetypes
        from pathlib import Path

        # Get file info
        file_path = Path(video_path)
        mime_type = mimetypes.guess_type(video_path)[0] or 'video/mp4'
        file_size = file_path.stat().st_size

        # Upload using REST API
        headers = {
            'X-Goog-Upload-Protocol': 'resumable',
            'X-Goog-Upload-Command': 'start',
            'X-Goog-Upload-Header-Content-Length': str(file_size),
            'X-Goog-Upload-Header-Content-Type': mime_type,
            'Content-Type': 'application/json',
        }

        # Start upload session
        start_url = f'https://generativelanguage.googleapis.com/upload/v1beta/files?key={Config.GEMINI_API_KEY}'
        metadata = {
            'file': {
                'display_name': file_path.name
            }
        }

        response = requests.post(start_url, headers=headers, json=metadata)
        if response.status_code != 200:
            raise ValueError(f"Upload start failed: {response.status_code} - {response.text}")

        upload_url = response.headers.get('X-Goog-Upload-URL')
        if not upload_url:
            raise ValueError("No upload URL returned")

        # Upload file content
        with open(video_path, 'rb') as f:
            file_data = f.read()

        upload_headers = {
            'Content-Length': str(file_size),
            'X-Goog-Upload-Offset': '0',
            'X-Goog-Upload-Command': 'upload, finalize',
        }

        upload_response = requests.post(upload_url, headers=upload_headers, data=file_data)
        if upload_response.status_code not in [200, 201]:
            raise ValueError(f"Upload failed: {upload_response.status_code} - {upload_response.text}")

        file_info = upload_response.json().get('file', {})
        file_name = file_info.get('name')

        print(f"Upload complete: {file_name}")

        # Wait for processing using REST API
        while True:
            check_url = f'https://generativelanguage.googleapis.com/v1beta/{file_name}?key={Config.GEMINI_API_KEY}'
            check_response = requests.get(check_url)

            if check_response.status_code != 200:
                raise ValueError(f"Status check failed: {check_response.status_code}")

            file_data = check_response.json()
            state = file_data.get('state', 'UNKNOWN')

            if state == 'ACTIVE':
                print(f"\nVideo ready: {file_data.get('uri')}")
                # Convert to genai file object for compatibility
                video_file = genai.get_file(file_name)
                return video_file
            elif state == 'FAILED':
                raise ValueError(f"Video processing failed")
            else:
                print(".", end="", flush=True)
                time.sleep(2)

    def analyze_video(self, video_path: str) -> Dict:
        """
        Comprehensive video analysis using Gemini 2.5

        Args:
            video_path: Path to video file

        Returns:
            Complete analysis dictionary
        """
        # Upload video
        video_file = self.upload_video(video_path)

        # Comprehensive analysis prompt
        prompt = """
        Analyze this advertising video in extreme detail. I need a comprehensive breakdown to recreate its structure.

        CRITICAL: You MUST break the video into MULTIPLE scenes, each NO LONGER than 12 seconds.
        - If the video is 40 seconds, create at least 3-4 scenes
        - If the video is 60 seconds, create at least 5 scenes
        - Each scene should have natural breaks in the narrative or visual changes
        - NO scene should exceed 12 seconds duration

        Provide a JSON response with the following structure:

        {
          "video_metadata": {
            "duration_seconds": <number>,
            "estimated_fps": <number>,
            "aspect_ratio": "<ratio>"
          },

          "spokesperson": {
            "physical_description": "<detailed appearance: age, gender, hair, facial features, body type, clothing style>",
            "speaking_style": "<tone, pace, energy, mannerisms>",
            "presence_timestamps": ["<start>-<end>", ...],
            "total_screen_time_seconds": <number>
          },

          "script": {
            "full_transcript": "<complete word-for-word script>",
            "key_phrases": ["<impactful phrases>"],
            "call_to_action": "<CTA text>"
          },

          "scene_breakdown": [
            {
              "scene_number": 1,
              "timestamp": "00:00-00:12",
              "duration_seconds": 12,
              "purpose": "<hook/problem/solution/proof/cta>",
              "shot_type": "<wide/medium/close-up/extreme-close-up>",
              "camera_angle": "<eye-level/high-angle/low-angle>",
              "camera_movement": "<static/pan/tilt/zoom/dolly>",
              "characters": "<who appears>",
              "setting": "<location description>",
              "lighting": "<style and mood>",
              "visual_elements": ["<text overlays>", "<graphics>", "<transitions>"],
              "message": "<what this scene communicates>",
              "emotion": "<emotional tone>"
            },
            {
              "scene_number": 2,
              "timestamp": "00:12-00:24",
              "duration_seconds": 12,
              "purpose": "<next narrative beat>",
              "shot_type": "<shot type>",
              "camera_angle": "<angle>",
              "camera_movement": "<movement>",
              "characters": "<who appears>",
              "setting": "<location>",
              "lighting": "<style>",
              "visual_elements": ["<elements>"],
              "message": "<message>",
              "emotion": "<emotion>"
            }
            (... continue for all scenes, max 12 seconds each)
          ],

          "visual_style": {
            "color_palette": ["<hex codes or descriptions>"],
            "lighting_style": "<overall lighting approach>",
            "cinematography": "<visual aesthetic>",
            "text_overlays": ["<key text elements>"],
            "graphics_style": "<type of graphics used>",
            "brand_elements": ["<logos>", "<colors>"]
          },

          "pacing": {
            "overall_tempo": "<fast/medium/slow>",
            "scene_durations": [<seconds per scene>],
            "energy_curve": "<how energy changes throughout>",
            "music_description": "<background music style>",
            "voice_pacing": "<delivery speed and rhythm>"
          },

          "storytelling": {
            "framework": "<PAS/BAB/Hero's Journey/Three-Act/etc>",
            "emotional_arc": ["<emotion 1>", "<emotion 2>", ...],
            "hook_strategy": "<how it grabs attention>",
            "problem_presented": "<pain point addressed>",
            "solution_offered": "<how product helps>",
            "proof_elements": ["<social proof>", "<testimonials>", "<data>"],
            "urgency_tactics": ["<limited time>", "<scarcity>"]
          },

          "why_it_works": [
            "<insight 1: why this element is effective>",
            "<insight 2: specific technique used>",
            "<insight 3: psychological trigger>"
          ]
        }

        Be extremely detailed in the physical description of the spokesperson - I need to be able to recreate their appearance accurately.
        Include exact timestamps for everything.
        Analyze what makes this ad effective from a marketing psychology perspective.
        """

        print("Analyzing video with Gemini 2.5...")
        response = self.model.generate_content(
            [video_file, prompt],
            generation_config=genai.GenerationConfig(
                temperature=0.2,  # Low temperature for consistency
            )
        )

        print("Analysis complete!")

        # Parse JSON response
        try:
            # Extract JSON from response
            response_text = response.text

            # Find JSON in response (might be wrapped in markdown)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]

            analysis = json.loads(response_text.strip())

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON, saving raw response")
            analysis = {
                "raw_response": response.text,
                "error": str(e)
            }

        return analysis

    def save_analysis(self, analysis: Dict, output_path: Optional[str] = None) -> str:
        """
        Save analysis to JSON file

        Args:
            analysis: Analysis dictionary
            output_path: Optional custom output path

        Returns:
            Path to saved file
        """
        if output_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = Config.ANALYSIS_DIR / f"analysis_{timestamp}.json"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"Analysis saved to: {output_path}")
        return str(output_path)

    def analyze_and_save(self, video_path: str) -> tuple[Dict, str]:
        """
        Convenience method to analyze and save in one call

        Returns:
            Tuple of (analysis dict, save path)
        """
        analysis = self.analyze_video(video_path)
        save_path = self.save_analysis(analysis)
        return analysis, save_path


# Test function
if __name__ == "__main__":
    analyzer = GeminiVideoAnalyzer()

    # Example usage
    video_path = input("Enter path to video file: ")
    analysis, path = analyzer.analyze_and_save(video_path)

    print("\n" + "="*50)
    print("ANALYSIS COMPLETE")
    print("="*50)
    print(f"\nSpokesperson: {analysis.get('spokesperson', {}).get('physical_description', 'N/A')}")
    print(f"\nFramework: {analysis.get('storytelling', {}).get('framework', 'N/A')}")
    print(f"\nScenes: {len(analysis.get('scene_breakdown', []))}")
    print(f"\nSaved to: {path}")
