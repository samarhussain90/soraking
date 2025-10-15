"""
Detailed Logging System
Provides comprehensive logging with progress tracking and status updates
"""
import logging
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

from config import Config


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    PROGRESS = "PROGRESS"
    VERBOSE = "VERBOSE"  # Extra detailed logging


class PipelineLogger:
    """Comprehensive pipeline logging with progress tracking"""

    def __init__(self, session_id: Optional[str] = None):
        """Initialize logger"""
        self.session_id = session_id or f"session_{int(time.time())}"
        self.session_start = time.time()

        # Create session log directory
        self.log_dir = Config.LOGS_DIR / self.session_id
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Log files
        self.main_log = self.log_dir / "pipeline.log"
        self.progress_log = self.log_dir / "progress.json"
        self.events_log = self.log_dir / "events.json"

        # Initialize progress tracking
        self.progress = {
            'session_id': self.session_id,
            'started_at': datetime.now().isoformat(),
            'status': 'initializing',
            'current_stage': None,
            'stages': {
                'analysis': {'status': 'pending', 'progress': 0, 'started_at': None, 'completed_at': None},
                'variants': {'status': 'pending', 'progress': 0, 'started_at': None, 'completed_at': None},
                'prompts': {'status': 'pending', 'progress': 0, 'started_at': None, 'completed_at': None},
                'generation': {'status': 'pending', 'progress': 0, 'started_at': None, 'completed_at': None, 'scenes': {}},
                'assembly': {'status': 'pending', 'progress': 0, 'started_at': None, 'completed_at': None}
            },
            'variants': {},
            'errors': [],
            'completed_at': None
        }

        # Event log
        self.events = []

        # Setup file logger
        self._setup_file_logger()

        self.log(LogLevel.INFO, "Pipeline session started", {
            'session_id': self.session_id,
            'log_dir': str(self.log_dir)
        })

    def _setup_file_logger(self):
        """Setup file-based logging"""
        self.file_logger = logging.getLogger(f'pipeline_{self.session_id}')
        self.file_logger.setLevel(logging.DEBUG)

        handler = logging.FileHandler(self.main_log)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)

        self.file_logger.addHandler(handler)

    def log(self, level: LogLevel, message: str, data: Optional[Dict] = None):
        """
        Log a message with optional data

        Args:
            level: Log level
            message: Log message
            data: Optional additional data
        """
        timestamp = datetime.now().isoformat()

        # Create event
        event = {
            'timestamp': timestamp,
            'level': level.value,
            'message': message,
            'data': data or {}
        }

        self.events.append(event)

        # Write to file logger
        log_msg = f"{message}"
        if data:
            log_msg += f" | {json.dumps(data)}"

        if level == LogLevel.ERROR:
            self.file_logger.error(log_msg)
        elif level == LogLevel.WARNING:
            self.file_logger.warning(log_msg)
        elif level == LogLevel.DEBUG:
            self.file_logger.debug(log_msg)
        else:
            self.file_logger.info(log_msg)

        # Console output
        emoji = {
            LogLevel.SUCCESS: "✓",
            LogLevel.ERROR: "✗",
            LogLevel.WARNING: "⚠",
            LogLevel.INFO: "ℹ",
            LogLevel.PROGRESS: "→",
            LogLevel.DEBUG: "·",
            LogLevel.VERBOSE: "▸"
        }.get(level, "•")

        print(f"{emoji} {message}")
        if data and level in [LogLevel.ERROR, LogLevel.WARNING, LogLevel.VERBOSE]:
            print(f"  {json.dumps(data, indent=2)}")

        # Save events
        self._save_events()

    def start_stage(self, stage_name: str, total_items: Optional[int] = None):
        """
        Start a pipeline stage

        Args:
            stage_name: Name of stage (analysis, variants, prompts, generation, assembly)
            total_items: Optional total items for progress tracking
        """
        self.progress['current_stage'] = stage_name
        self.progress['stages'][stage_name]['status'] = 'in_progress'
        self.progress['stages'][stage_name]['started_at'] = datetime.now().isoformat()
        self.progress['stages'][stage_name]['progress'] = 0

        if total_items:
            self.progress['stages'][stage_name]['total_items'] = total_items

        self.log(LogLevel.INFO, f"Stage started: {stage_name}", {
            'stage': stage_name,
            'total_items': total_items
        })

        self._save_progress()

    def update_stage_progress(self, stage_name: str, progress: int, message: Optional[str] = None):
        """
        Update stage progress

        Args:
            stage_name: Stage name
            progress: Progress percentage (0-100)
            message: Optional progress message
        """
        self.progress['stages'][stage_name]['progress'] = progress

        data = {
            'stage': stage_name,
            'progress': progress
        }

        if message:
            data['message'] = message

        self.log(LogLevel.PROGRESS, f"{stage_name}: {progress}%", data)
        self._save_progress()

    def complete_stage(self, stage_name: str, result: Optional[Dict] = None):
        """
        Complete a pipeline stage

        Args:
            stage_name: Stage name
            result: Optional result data
        """
        self.progress['stages'][stage_name]['status'] = 'completed'
        self.progress['stages'][stage_name]['progress'] = 100
        self.progress['stages'][stage_name]['completed_at'] = datetime.now().isoformat()

        if result:
            self.progress['stages'][stage_name]['result'] = result

        self.log(LogLevel.SUCCESS, f"Stage completed: {stage_name}", result)
        self._save_progress()

    def fail_stage(self, stage_name: str, error: str):
        """
        Mark stage as failed

        Args:
            stage_name: Stage name
            error: Error message
        """
        self.progress['stages'][stage_name]['status'] = 'failed'
        self.progress['stages'][stage_name]['error'] = error
        self.progress['errors'].append({
            'stage': stage_name,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })

        self.log(LogLevel.ERROR, f"Stage failed: {stage_name}", {'error': error})
        self._save_progress()

    def track_variant(self, variant_name: str, status: str, data: Optional[Dict] = None):
        """
        Track variant generation

        Args:
            variant_name: Variant name (soft, medium, aggressive, ultra)
            status: Status (generating, completed, failed)
            data: Optional data
        """
        if variant_name not in self.progress['variants']:
            self.progress['variants'][variant_name] = {
                'status': status,
                'started_at': datetime.now().isoformat(),
                'scenes': {}
            }
        else:
            self.progress['variants'][variant_name]['status'] = status

        if data:
            self.progress['variants'][variant_name].update(data)

        if status == 'completed':
            self.progress['variants'][variant_name]['completed_at'] = datetime.now().isoformat()

        self.log(LogLevel.INFO, f"Variant {variant_name}: {status}", data)
        self._save_progress()

    def track_scene(self, variant_name: str, scene_number: int, status: str,
                   progress: Optional[int] = None, job_id: Optional[str] = None):
        """
        Track individual scene generation

        Args:
            variant_name: Variant name
            scene_number: Scene number
            status: Status (queued, in_progress, completed, failed)
            progress: Optional progress percentage
            job_id: Optional Sora job ID
        """
        if variant_name not in self.progress['variants']:
            self.progress['variants'][variant_name] = {'scenes': {}}

        scene_key = f"scene_{scene_number}"

        if scene_key not in self.progress['variants'][variant_name]['scenes']:
            self.progress['variants'][variant_name]['scenes'][scene_key] = {
                'status': status,
                'started_at': datetime.now().isoformat()
            }
        else:
            self.progress['variants'][variant_name]['scenes'][scene_key]['status'] = status

        if progress is not None:
            self.progress['variants'][variant_name]['scenes'][scene_key]['progress'] = progress

        if job_id:
            self.progress['variants'][variant_name]['scenes'][scene_key]['job_id'] = job_id

        if status == 'completed':
            self.progress['variants'][variant_name]['scenes'][scene_key]['completed_at'] = datetime.now().isoformat()

        self._save_progress()

    def complete_pipeline(self, final_results: Dict):
        """
        Mark pipeline as complete

        Args:
            final_results: Final results dictionary
        """
        self.progress['status'] = 'completed'
        self.progress['completed_at'] = datetime.now().isoformat()
        self.progress['final_results'] = final_results

        elapsed = time.time() - self.session_start
        self.progress['elapsed_time'] = elapsed

        self.log(LogLevel.SUCCESS, "Pipeline completed", {
            'elapsed_time': f"{elapsed/60:.1f} minutes",
            'variants_generated': len(final_results.get('final_ads', {}))
        })

        self._save_progress()

    def _save_progress(self):
        """Save progress to JSON file"""
        with open(self.progress_log, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def _save_events(self):
        """Save events to JSON file"""
        with open(self.events_log, 'w') as f:
            json.dump(self.events, f, indent=2)

    def get_progress(self) -> Dict:
        """Get current progress"""
        return self.progress.copy()

    def get_events(self, since: Optional[str] = None) -> List[Dict]:
        """
        Get events, optionally filtered by timestamp

        Args:
            since: ISO timestamp to filter events after

        Returns:
            List of events
        """
        if since:
            return [e for e in self.events if e['timestamp'] > since]
        return self.events.copy()


# Global logger instance
_current_logger: Optional[PipelineLogger] = None


def get_logger(session_id: Optional[str] = None) -> PipelineLogger:
    """Get or create global logger instance"""
    global _current_logger
    if _current_logger is None or session_id:
        _current_logger = PipelineLogger(session_id)
    return _current_logger


# Convenience functions
def log_info(message: str, data: Optional[Dict] = None):
    """Log info message"""
    get_logger().log(LogLevel.INFO, message, data)


def log_success(message: str, data: Optional[Dict] = None):
    """Log success message"""
    get_logger().log(LogLevel.SUCCESS, message, data)


def log_error(message: str, data: Optional[Dict] = None):
    """Log error message"""
    get_logger().log(LogLevel.ERROR, message, data)


# Make LogLevel accessible from logger instance
PipelineLogger.LogLevel = LogLevel


def log_warning(message: str, data: Optional[Dict] = None):
    """Log warning message"""
    get_logger().log(LogLevel.WARNING, message, data)


def log_progress(message: str, progress: int, data: Optional[Dict] = None):
    """Log progress update"""
    data = data or {}
    data['progress'] = progress
    get_logger().log(LogLevel.PROGRESS, message, data)


# Test
if __name__ == "__main__":
    logger = PipelineLogger()

    logger.log(LogLevel.INFO, "Testing logger")
    logger.start_stage('analysis')
    logger.update_stage_progress('analysis', 50, "Analyzing video...")
    logger.complete_stage('analysis', {'frames': 100})

    logger.track_variant('soft', 'generating')
    logger.track_scene('soft', 1, 'in_progress', progress=75)
    logger.track_scene('soft', 1, 'completed')
    logger.track_variant('soft', 'completed', {'video_path': '/path/to/video.mp4'})

    print(f"\nSession logs: {logger.log_dir}")
    print(f"Progress: {logger.progress_log}")
    print(f"Events: {logger.events_log}")
