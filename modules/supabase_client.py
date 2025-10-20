"""
Supabase Client for Ad Cloner
Handles all database operations
"""
import os
from typing import Dict, List, Optional
from datetime import datetime
import json
from supabase import create_client, Client


class SupabaseClient:
    """Wrapper for Supabase operations"""

    def __init__(self):
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_ANON_KEY')

        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

        self.client: Client = create_client(url, key)

    # Session operations
    def create_session(self, session_id: str, video_path: str, variants: List[str]) -> Dict:
        """Create a new pipeline session"""
        data = {
            'session_id': session_id,
            'status': 'started',
            'video_path': video_path,
            'variants': variants,
            'started_at': datetime.now().isoformat()
        }

        result = self.client.table('sessions').insert(data).execute()
        return result.data[0] if result.data else {}

    def update_session_status(self, session_id: str, status: str, error: Optional[str] = None):
        """Update session status"""
        data = {'status': status, 'updated_at': datetime.now().isoformat()}

        if status == 'completed':
            data['completed_at'] = datetime.now().isoformat()

        if error:
            data['error'] = error

        self.client.table('sessions').update(data).eq('session_id', session_id).execute()

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        result = self.client.table('sessions').select('*').eq('session_id', session_id).execute()
        return result.data[0] if result.data else None

    def list_sessions(self, limit: int = 50) -> List[Dict]:
        """List recent sessions"""
        result = self.client.table('sessions').select('*').order('created_at', desc=True).limit(limit).execute()
        return result.data if result.data else []

    # Video operations
    def save_video(self, session_id: str, filename: str, file_path: str, file_size_mb: float) -> Dict:
        """Save uploaded video metadata"""
        data = {
            'session_id': session_id,
            'filename': filename,
            'file_path': file_path,
            'file_size_mb': file_size_mb,
            'uploaded_at': datetime.now().isoformat()
        }

        result = self.client.table('videos').insert(data).execute()
        return result.data[0] if result.data else {}

    # Analysis operations
    def save_analysis(self, session_id: str, analysis: Dict) -> Dict:
        """Save Gemini analysis results"""
        data = {
            'session_id': session_id,
            'vertical': analysis.get('vertical'),
            'vertical_name': analysis.get('vertical_name'),
            'full_analysis': analysis,
            'created_at': datetime.now().isoformat()
        }

        result = self.client.table('analyses').insert(data).execute()
        return result.data[0] if result.data else {}

    def get_analysis(self, session_id: str) -> Optional[Dict]:
        """Get analysis for session"""
        result = self.client.table('analyses').select('*').eq('session_id', session_id).execute()
        return result.data[0] if result.data else None

    # Prompt operations
    def save_prompts(self, session_id: str, variant_level: str, prompts: List[Dict]):
        """Save Sora prompts for a variant"""
        data = []
        for prompt in prompts:
            data.append({
                'session_id': session_id,
                'variant_level': variant_level,
                'scene_number': prompt.get('scene_number'),
                'scene_type': prompt.get('purpose'),
                'prompt_text': prompt.get('prompt'),
                'script_segment': prompt.get('script_segment'),
                'has_character': prompt.get('has_character', False)
            })

        if data:
            self.client.table('prompts').insert(data).execute()

    def get_prompts(self, session_id: str, variant_level: Optional[str] = None) -> List[Dict]:
        """Get prompts for session"""
        query = self.client.table('prompts').select('*').eq('session_id', session_id)

        if variant_level:
            query = query.eq('variant_level', variant_level)

        result = query.order('scene_number').execute()
        return result.data if result.data else []

    # Generated video operations
    def save_generated_video(
        self,
        session_id: str,
        variant_level: str,
        scene_number: int,
        sora_video_id: str,
        video_url: str
    ) -> Dict:
        """Save generated video metadata"""
        data = {
            'session_id': session_id,
            'variant_level': variant_level,
            'scene_number': scene_number,
            'sora_video_id': sora_video_id,
            'video_url': video_url,
            'status': 'generating',
            'created_at': datetime.now().isoformat()
        }

        result = self.client.table('generated_videos').insert(data).execute()
        return result.data[0] if result.data else {}

    def update_generated_video_status(
        self,
        sora_video_id: str,
        status: str,
        file_path: Optional[str] = None
    ):
        """Update generated video status"""
        data = {'status': status}

        if status == 'completed':
            data['completed_at'] = datetime.now().isoformat()

        if file_path:
            data['file_path'] = file_path

        self.client.table('generated_videos').update(data).eq('sora_video_id', sora_video_id).execute()

    def get_generated_videos(self, session_id: str) -> List[Dict]:
        """Get all generated videos for session"""
        result = self.client.table('generated_videos').select('*').eq('session_id', session_id).execute()
        return result.data if result.data else []

    # Event logging
    def log_event(self, session_id: str, level: str, message: str, data: Optional[Dict] = None):
        """Log a pipeline event"""
        event_data = {
            'session_id': session_id,
            'level': level,
            'message': message,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }

        self.client.table('events').insert(event_data).execute()

    def get_events(self, session_id: str, limit: int = 100) -> List[Dict]:
        """Get events for session"""
        result = self.client.table('events').select('*').eq('session_id', session_id).order('timestamp', desc=True).limit(limit).execute()
        return result.data if result.data else []


# Helper function for direct Supabase client access (used by GenerationManager)
def get_supabase_client() -> Client:
    """Get raw Supabase client for direct table operations"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

    return create_client(url, key)
