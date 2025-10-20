# Video Extension API Endpoints
@app.route('/api/video-extension/create', methods=['POST'])
def create_video_extension():
    """Create a new video extension request"""
    try:
        data = request.json
        video_path = data.get('video_path')
        target_duration = data.get('target_duration')
        extension_type = data.get('extension_type', 'smart')
        style_consistency = data.get('style_consistency', True)
        
        if not video_path or not target_duration:
            return jsonify({'error': 'video_path and target_duration required'}), 400
        
        extension_engine = VideoExtensionEngine()
        request_id = extension_engine.create_extension_request(
            video_path=video_path,
            target_duration=target_duration,
            extension_type=extension_type,
            style_consistency=style_consistency
        )
        
        return jsonify({
            'success': True,
            'request_id': request_id,
            'message': 'Video extension request created'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video-extension/process/<request_id>', methods=['POST'])
def process_video_extension(request_id):
    """Process a video extension request"""
    try:
        extension_engine = VideoExtensionEngine()
        result_id = extension_engine.process_extension_request(request_id)
        
        return jsonify({
            'success': True,
            'result_id': result_id,
            'message': 'Video extension completed'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video-extension/results/<request_id>', methods=['GET'])
def get_extension_results(request_id):
    """Get results for a specific extension request"""
    try:
        extension_engine = VideoExtensionEngine()
        results = extension_engine.get_extension_results(request_id)
        
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video-extension/stats', methods=['GET'])
def get_extension_stats():
    """Get video extension statistics"""
    try:
        extension_engine = VideoExtensionEngine()
        stats = extension_engine.get_extension_stats()
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video-extension/analyze', methods=['POST'])
def analyze_video_for_extension():
    """Analyze video for extension recommendations"""
    try:
        data = request.json
        video_path = data.get('video_path')
        
        if not video_path:
            return jsonify({'error': 'video_path required'}), 400
        
        extension_engine = VideoExtensionEngine()
        analysis = extension_engine.analyze_video_for_extension(video_path)
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
