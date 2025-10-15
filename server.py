"""
Web Server with API and WebSocket Support
Provides REST API and real-time updates for frontend
"""
import os
import json
import threading
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

from config import Config
from ad_cloner import AdCloner
from modules.logger import PipelineLogger, get_logger
from modules.supabase_client import SupabaseClient
from modules.spaces_client import SpacesClient
from modules.settings_manager import get_settings_manager

app = Flask(__name__, static_folder='frontend', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=500 * 1024 * 1024)

# Initialize cloud clients
try:
    supabase_client = SupabaseClient()
    spaces_client = SpacesClient()
    print("✓ Cloud clients initialized (Supabase + Spaces)")
except Exception as e:
    print(f"⚠ Warning: Cloud clients not initialized: {e}")
    print("  → Running in local mode (files will be stored locally)")
    supabase_client = None
    spaces_client = None

# Store active sessions
active_sessions = {}

# Create uploads directory (fallback for local mode)
UPLOAD_FOLDER = Config.OUTPUT_DIR / 'uploads'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Serve frontend"""
    return send_from_directory('frontend', 'index.html')


@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'openai_key_configured': bool(Config.OPENAI_API_KEY),
        'gemini_key_configured': bool(Config.GEMINI_API_KEY)
    })


@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all sessions"""
    sessions = []

    for session_dir in Config.LOGS_DIR.iterdir():
        if session_dir.is_dir():
            progress_file = session_dir / 'progress.json'
            if progress_file.exists():
                with open(progress_file) as f:
                    progress = json.load(f)
                    sessions.append({
                        'session_id': progress['session_id'],
                        'status': progress['status'],
                        'started_at': progress['started_at'],
                        'completed_at': progress.get('completed_at')
                    })

    return jsonify({'sessions': sessions})


@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details"""
    session_dir = Config.LOGS_DIR / session_id

    if not session_dir.exists():
        return jsonify({'error': 'Session not found'}), 404

    progress_file = session_dir / 'progress.json'
    events_file = session_dir / 'events.json'

    response = {}

    if progress_file.exists():
        with open(progress_file) as f:
            response['progress'] = json.load(f)

    if events_file.exists():
        with open(events_file) as f:
            events = json.load(f)
            # Get last 100 events
            response['events'] = events[-100:]

    return jsonify(response)


@app.route('/api/sessions/<session_id>/events', methods=['GET'])
def get_session_events(session_id):
    """Get session events with optional filtering"""
    session_dir = Config.LOGS_DIR / session_id
    events_file = session_dir / 'events.json'

    if not events_file.exists():
        return jsonify({'error': 'Session not found'}), 404

    with open(events_file) as f:
        events = json.load(f)

    # Filter by timestamp if provided
    since = request.args.get('since')
    if since:
        events = [e for e in events if e['timestamp'] > since]

    return jsonify({'events': events})


@app.route('/api/sessions/<session_id>/detailed', methods=['GET'])
def get_detailed_logs(session_id):
    """Get detailed logs including analysis, prompts, and evaluation"""
    response = {}

    # Load analysis (from analysis directory)
    analysis_files = list(Config.ANALYSIS_DIR.glob(f"analysis_*.json"))
    if analysis_files:
        latest_analysis = max(analysis_files, key=lambda p: p.stat().st_mtime)
        with open(latest_analysis) as f:
            response['analysis'] = json.load(f)

            # Extract transformation info
            if 'vertical' in response['analysis']:
                response['transformation'] = {
                    'vertical': response['analysis'].get('vertical'),
                    'vertical_name': response['analysis'].get('vertical_name'),
                    'character_scenes': sum(1 for s in response['analysis'].get('scene_breakdown', [])
                                          if s.get('has_character')),
                    'broll_scenes': sum(1 for s in response['analysis'].get('scene_breakdown', [])
                                      if not s.get('has_character')),
                    'scenes': response['analysis'].get('scene_breakdown', [])
                }

    # Load Sora prompts
    prompts_files = list(Config.ANALYSIS_DIR.glob(f"sora_prompts_*.json"))
    if prompts_files:
        latest_prompts = max(prompts_files, key=lambda p: p.stat().st_mtime)
        with open(latest_prompts) as f:
            response['prompts'] = json.load(f)

    # Load evaluation
    eval_files = list(Config.ANALYSIS_DIR.glob(f"evaluation_*.json"))
    if eval_files:
        latest_eval = max(eval_files, key=lambda p: p.stat().st_mtime)
        with open(latest_eval) as f:
            response['evaluation'] = json.load(f)

    return jsonify(response)


@app.route('/api/clone', methods=['POST'])
def start_clone():
    """Start ad cloning pipeline"""
    data = request.json

    video_path = data.get('video_path')
    variants = data.get('variants')  # Optional list like ['soft', 'aggressive']

    if not video_path:
        return jsonify({'error': 'video_path required'}), 400

    # Create session
    logger = PipelineLogger()
    session_id = logger.session_id

    # Create Supabase session if available
    if supabase_client:
        try:
            supabase_client.create_session(
                session_id,
                video_path,
                variants or ['soft', 'medium', 'aggressive', 'ultra']
            )
            supabase_client.log_event(
                session_id,
                'info',
                'Pipeline session created',
                {'video_path': video_path, 'variants': variants}
            )
        except Exception as e:
            print(f"⚠ Supabase session creation failed: {e}")

    # Store in active sessions
    active_sessions[session_id] = {
        'logger': logger,
        'status': 'starting'
    }

    # Create a wrapper logger that broadcasts to WebSocket and Supabase
    class WebSocketLogger(PipelineLogger):
        def log(self, level, message, data=None):
            # Call parent log method
            super().log(level, message, data)

            # Log to Supabase if available
            if supabase_client:
                try:
                    supabase_client.log_event(
                        session_id,
                        level.value.lower(),
                        message,
                        data
                    )
                except Exception as e:
                    print(f"⚠ Supabase log failed: {e}")

            # Broadcast to WebSocket
            socketio.emit('event', {
                'session_id': session_id,
                'event': {
                    'timestamp': self.events[-1]['timestamp'],
                    'level': level.value,
                    'message': message,
                    'data': data or {}
                }
            }, room=session_id)

        def _save_progress(self):
            # Call parent save
            super()._save_progress()
            # Broadcast progress update
            socketio.emit('progress_update', {
                'session_id': session_id,
                'progress': self.progress
            }, room=session_id)

    # Replace logger with WebSocket-enabled version
    ws_logger = WebSocketLogger(session_id)
    active_sessions[session_id]['logger'] = ws_logger

    # Run pipeline in background thread
    def run_pipeline():
        try:
            # Emit start event
            socketio.emit('pipeline_started', {
                'session_id': session_id
            })

            # Initialize cloner with WebSocket logger
            cloner = AdCloner(logger=ws_logger)

            # Run pipeline (logger integrated)
            results = cloner.clone_ad(video_path, variants)

            # Log completion
            ws_logger.complete_pipeline(results)

            # Update session
            active_sessions[session_id]['status'] = 'completed'
            active_sessions[session_id]['results'] = results

            # Update Supabase session status
            if supabase_client:
                try:
                    supabase_client.update_session_status(session_id, 'completed')
                except Exception as e:
                    print(f"⚠ Supabase status update failed: {e}")

            # Emit completion
            socketio.emit('pipeline_completed', {
                'session_id': session_id,
                'results': results
            })

        except Exception as e:
            logger.log(logger.LogLevel.ERROR, f"Pipeline failed: {str(e)}")
            active_sessions[session_id]['status'] = 'failed'
            active_sessions[session_id]['error'] = str(e)

            # Update Supabase session status
            if supabase_client:
                try:
                    supabase_client.update_session_status(session_id, 'failed', str(e))
                except Exception as e2:
                    print(f"⚠ Supabase status update failed: {e2}")

            socketio.emit('pipeline_failed', {
                'session_id': session_id,
                'error': str(e)
            })

    thread = threading.Thread(target=run_pipeline)
    thread.daemon = True
    thread.start()

    return jsonify({
        'session_id': session_id,
        'status': 'started',
        'log_dir': str(logger.log_dir)
    })


@app.route('/api/sessions/<session_id>/videos', methods=['GET'])
def list_session_videos(session_id):
    """List videos generated for a session"""
    videos_dir = Config.VIDEOS_DIR

    videos = []
    for variant_dir in videos_dir.iterdir():
        if variant_dir.is_dir():
            final_video = variant_dir / f"final_{variant_dir.name}.mp4"
            if final_video.exists():
                videos.append({
                    'variant': variant_dir.name,
                    'path': str(final_video),
                    'size_mb': final_video.stat().st_size / (1024 * 1024)
                })

    return jsonify({'videos': videos})


@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Upload video file to cloud storage"""
    # Check if file is in request
    if 'video' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['video']

    # Check if filename is empty
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Check file extension
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400

    try:
        # Secure the filename
        filename = secure_filename(file.filename)

        # Add timestamp to avoid conflicts
        import time
        timestamp = int(time.time())
        name, ext = filename.rsplit('.', 1)
        filename = f"{name}_{timestamp}.{ext}"

        # Save file temporarily
        temp_filepath = UPLOAD_FOLDER / filename
        file.save(str(temp_filepath))

        # Get file info
        file_size = temp_filepath.stat().st_size
        file_size_mb = file_size / (1024 * 1024)

        # Upload to cloud if available
        cloud_url = None
        if spaces_client:
            try:
                # Create session ID for organization
                session_id = f"upload_{timestamp}"
                cloud_url = spaces_client.upload_session_video(
                    session_id,
                    str(temp_filepath),
                    'upload'
                )
                print(f"✓ Uploaded to Spaces: {cloud_url}")
            except Exception as e:
                print(f"⚠ Spaces upload failed: {e}")
                # Continue with local file

        # Save to Supabase if available
        if supabase_client and cloud_url:
            try:
                session_id = f"upload_{timestamp}"
                supabase_client.save_video(
                    session_id,
                    filename,
                    cloud_url,
                    file_size_mb
                )
            except Exception as e:
                print(f"⚠ Supabase save failed: {e}")

        return jsonify({
            'success': True,
            'filename': filename,
            'path': cloud_url if cloud_url else str(temp_filepath),
            'cloud_url': cloud_url,
            'local_path': str(temp_filepath),
            'size_mb': round(file_size_mb, 2)
        })

    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to Ad Cloner'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print(f"Client disconnected: {request.sid}")


@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to session updates"""
    session_id = data.get('session_id')
    print(f"Client {request.sid} subscribed to {session_id}")
    # Join room for this session
    from flask_socketio import join_room
    join_room(session_id)


def broadcast_progress(session_id: str, progress: dict):
    """Broadcast progress update to all subscribed clients"""
    socketio.emit('progress_update', {
        'session_id': session_id,
        'progress': progress
    }, room=session_id)


def broadcast_event(session_id: str, event: dict):
    """Broadcast event to all subscribed clients"""
    socketio.emit('event', {
        'session_id': session_id,
        'event': event
    }, room=session_id)


# Settings Management Endpoints

@app.route('/settings')
def settings_page():
    """Serve settings page"""
    return send_from_directory('frontend', 'settings.html')


@app.route('/api/settings', methods=['GET'])
def get_all_settings():
    """Get all settings"""
    try:
        settings_manager = get_settings_manager()
        settings = settings_manager.get_all_settings()
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/<category>', methods=['GET'])
def get_settings_by_category(category):
    """Get all settings for a category"""
    try:
        settings_manager = get_settings_manager()
        settings = settings_manager.get_settings_by_category(category)
        return jsonify({
            'success': True,
            'category': category,
            'settings': settings
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/<category>/<key>', methods=['GET'])
def get_setting(category, key):
    """Get a specific setting"""
    try:
        settings_manager = get_settings_manager()
        setting = settings_manager.get_setting(category, key, use_cache=False)

        if setting:
            return jsonify({
                'success': True,
                'setting': setting
            })
        else:
            return jsonify({'error': 'Setting not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/<category>/<key>', methods=['PUT'])
def update_setting(category, key):
    """Update a setting"""
    try:
        data = request.json
        value = data.get('value')
        description = data.get('description')

        if value is None:
            return jsonify({'error': 'value required'}), 400

        settings_manager = get_settings_manager()
        success = settings_manager.update_setting(category, key, value, description)

        if success:
            return jsonify({
                'success': True,
                'message': f'Setting {category}:{key} updated'
            })
        else:
            return jsonify({'error': 'Update failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/<category>/<key>', methods=['POST'])
def create_setting(category, key):
    """Create a new setting"""
    try:
        data = request.json
        value = data.get('value')
        description = data.get('description')

        if value is None:
            return jsonify({'error': 'value required'}), 400

        settings_manager = get_settings_manager()
        success = settings_manager.create_setting(category, key, value, description)

        if success:
            return jsonify({
                'success': True,
                'message': f'Setting {category}:{key} created'
            })
        else:
            return jsonify({'error': 'Creation failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/<category>/<key>', methods=['DELETE'])
def delete_setting(category, key):
    """Delete a setting"""
    try:
        settings_manager = get_settings_manager()
        success = settings_manager.delete_setting(category, key)

        if success:
            return jsonify({
                'success': True,
                'message': f'Setting {category}:{key} deleted'
            })
        else:
            return jsonify({'error': 'Deletion failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/cache/clear', methods=['POST'])
def clear_settings_cache():
    """Clear settings cache"""
    try:
        settings_manager = get_settings_manager()
        settings_manager.clear_cache()
        return jsonify({
            'success': True,
            'message': 'Cache cleared'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("="*70)
    print("AD CLONER WEB SERVER")
    print("="*70)
    print(f"\nServer starting on http://localhost:{Config.PORT}")
    print(f"API available at http://localhost:{Config.PORT}/api")
    print(f"\nPress Ctrl+C to stop\n")

    socketio.run(app, host='0.0.0.0', port=Config.PORT, debug=True, allow_unsafe_werkzeug=True)

@app.route('/api/preview', methods=['POST'])
def preview_prompts():
    """Generate prompts for preview (without sending to Sora)"""
    data = request.json
    video_path = data.get('video_path')
    variants = data.get('variants', ['medium'])

    if not video_path:
        return jsonify({'error': 'video_path required'}), 400

    try:
        from ad_cloner import AdCloner
        
        cloner = AdCloner()
        
        # Step 1: Analyze
        analysis, analysis_path = cloner.analyzer.analyze_and_save(video_path)
        
        # Step 2: Transform
        vertical = cloner.transformer.detect_vertical(analysis)
        transformed_scenes = cloner.transformer.transform_to_sora_structure(analysis, vertical)
        analysis['scene_breakdown'] = transformed_scenes
        
        # Step 3: Generate variants
        all_variants = cloner.variant_generator.generate_variants(analysis)
        if variants:
            all_variants = [v for v in all_variants if v['variant_level'] in variants]

        # Step 4: Build prompts (but DON'T send to Sora)
        # Normalize spokesperson (handle list/dict formats)
        spokesperson = analysis.get('spokesperson', {})
        if isinstance(spokesperson, list) and len(spokesperson) > 0:
            spokesperson = spokesperson[0]
        elif not isinstance(spokesperson, dict):
            spokesperson = {}
        spokesperson_desc = spokesperson.get('physical_description', '')
        full_script = analysis.get('script', {}).get('full_transcript', '')
        
        variant_prompts = {}
        for variant in all_variants:
            prompts = cloner.prompt_builder.build_all_scene_prompts(variant, spokesperson_desc, full_script)
            variant_prompts[variant['variant_level']] = prompts
        
        # Save for later use
        import json
        preview_file = Path(analysis_path).parent / 'preview_prompts.json'
        with open(preview_file, 'w') as f:
            json.dump({
                'analysis_path': analysis_path,
                'video_path': video_path,
                'variants': variants,
                'prompts': variant_prompts
            }, f, indent=2)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'vertical': vertical,
            'prompts': variant_prompts,
            'preview_file': str(preview_file)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate', methods=['POST'])
def generate_from_preview():
    """Generate videos from previewed prompts"""
    data = request.json
    preview_file = data.get('preview_file')
    
    if not preview_file:
        return jsonify({'error': 'preview_file required'}), 400
    
    try:
        # Load preview
        import json
        with open(preview_file) as f:
            preview_data = json.load(f)
        
        # Create session for tracking
        from modules.logger import PipelineLogger
        logger = PipelineLogger()
        session_id = logger.session_id
        
        # Start generation in background
        def run_generation():
            from ad_cloner import AdCloner
            cloner = AdCloner(logger=logger)
            
            # Load analysis
            with open(preview_data['analysis_path']) as f:
                analysis = json.load(f)
            
            # Run from step 4 onwards (generation)
            prompts = preview_data['prompts']
            
            # TODO: Continue from here with Sora generation
            # This would be the same as ad_cloner.py steps 4-6
            
        import threading
        thread = threading.Thread(target=run_generation)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Generation started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

