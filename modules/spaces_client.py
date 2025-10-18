"""
DigitalOcean Spaces Storage Client
S3-compatible storage for videos and media
"""
import os
import boto3
from pathlib import Path
from typing import Optional
from botocore.client import Config
from datetime import datetime


class SpacesClient:
    """Wrapper for DigitalOcean Spaces operations (S3-compatible)"""

    def __init__(self, region: str = 'nyc3'):
        """
        Initialize Spaces client

        Args:
            region: DigitalOcean region (nyc3, sfo3, ams3, sgp1)
        """
        access_key = os.getenv('DO_SPACES_ACCESS_KEY')
        secret_key = os.getenv('DO_SPACES_SECRET_KEY')
        bucket_name = os.getenv('DO_SPACES_BUCKET', 'soraking-videos')

        if not access_key or not secret_key:
            raise ValueError("DO_SPACES_ACCESS_KEY and DO_SPACES_SECRET_KEY must be set")

        self.region = region
        self.bucket_name = bucket_name
        self.endpoint_url = f'https://{region}.digitaloceanspaces.com'
        # Use direct endpoint URL instead of CDN (CDN may require explicit enablement)
        self.public_url = f'https://{bucket_name}.{region}.digitaloceanspaces.com'

        # Initialize S3 client
        self.client = boto3.client(
            's3',
            region_name=region,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )

        # Ensure bucket exists
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except:
            # Bucket doesn't exist, create it
            self.client.create_bucket(Bucket=self.bucket_name)
            # Make bucket publicly readable (for video playback)
            self.client.put_bucket_cors(
                Bucket=self.bucket_name,
                CORSConfiguration={
                    'CORSRules': [{
                        'AllowedOrigins': ['*'],
                        'AllowedMethods': ['GET', 'HEAD'],
                        'AllowedHeaders': ['*'],
                        'MaxAgeSeconds': 3000
                    }]
                }
            )

    def upload_video(
        self,
        local_path: str,
        remote_path: str,
        make_public: bool = True
    ) -> str:
        """
        Upload video to Spaces

        Args:
            local_path: Local file path
            remote_path: Remote path in bucket (e.g., 'uploads/video.mp4')
            make_public: Make file publicly accessible

        Returns:
            Public URL of uploaded file
        """
        extra_args = {
            'ContentType': 'video/mp4'
        }

        if make_public:
            extra_args['ACL'] = 'public-read'

        # Upload file
        self.client.upload_file(
            local_path,
            self.bucket_name,
            remote_path,
            ExtraArgs=extra_args
        )

        # Return public URL
        return f"{self.public_url}/{remote_path}"

    def download_video(
        self,
        remote_path: str,
        local_path: str
    ):
        """
        Download video from Spaces

        Args:
            remote_path: Remote path in bucket
            local_path: Local destination path
        """
        # Ensure local directory exists
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)

        # Download file
        self.client.download_file(
            self.bucket_name,
            remote_path,
            local_path
        )

    def delete_video(self, remote_path: str):
        """Delete video from Spaces"""
        self.client.delete_object(
            Bucket=self.bucket_name,
            Key=remote_path
        )

    def list_videos(self, prefix: str = '') -> list:
        """
        List videos in Spaces

        Args:
            prefix: Filter by prefix (e.g., 'session_123/')

        Returns:
            List of file keys
        """
        response = self.client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=prefix
        )

        if 'Contents' not in response:
            return []

        return [obj['Key'] for obj in response['Contents']]

    def get_public_url(self, remote_path: str) -> str:
        """Get public URL for a file"""
        return f"{self.public_url}/{remote_path}"

    def generate_presigned_url(
        self,
        remote_path: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate temporary presigned URL

        Args:
            remote_path: Remote file path
            expiration: URL expiration in seconds

        Returns:
            Presigned URL
        """
        return self.client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': remote_path
            },
            ExpiresIn=expiration
        )

    def upload_session_video(
        self,
        session_id: str,
        local_path: str,
        video_type: str = 'upload'
    ) -> str:
        """
        Upload video for a session with organized structure

        Args:
            session_id: Pipeline session ID
            local_path: Local file path
            video_type: Type (upload, generated, final)

        Returns:
            Public URL
        """
        # Generate organized path
        filename = Path(local_path).name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        remote_path = f"sessions/{session_id}/{video_type}/{timestamp}_{filename}"

        return self.upload_video(local_path, remote_path)

    def list_session_videos(self, session_id: str) -> dict:
        """
        List all videos for a session

        Returns:
            Dict with upload, generated, and final video lists
        """
        prefix = f"sessions/{session_id}/"
        all_files = self.list_videos(prefix)

        return {
            'uploads': [f for f in all_files if '/upload/' in f],
            'generated': [f for f in all_files if '/generated/' in f],
            'final': [f for f in all_files if '/final/' in f]
        }

    def list_session_files(self, session_id: str) -> list:
        """
        List all files for a session with detailed information

        Args:
            session_id: Pipeline session ID

        Returns:
            List of dicts with file info (path, url, size)
        """
        prefix = f"sessions/{session_id}/"

        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            if 'Contents' not in response:
                return []

            files = []
            for obj in response['Contents']:
                file_path = obj['Key']
                files.append({
                    'path': file_path,
                    'url': self.get_public_url(file_path),
                    'size': obj.get('Size', 0),
                    'last_modified': obj.get('LastModified')
                })

            return files

        except Exception as e:
            print(f"Error listing session files: {e}")
            return []
