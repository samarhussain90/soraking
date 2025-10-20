"""
History API - REST endpoints for generation history and library
"""
from flask import Blueprint, jsonify, request
from generation_manager import GenerationManager

# Create blueprint
history_api = Blueprint('history_api', __name__, url_prefix='/api/history')

# Initialize manager lazily (will be created on first request)
gen_manager = None

def get_gen_manager():
    """Get or create GenerationManager instance"""
    global gen_manager
    if gen_manager is None:
        gen_manager = GenerationManager()
    return gen_manager


@history_api.route('/generations', methods=['GET'])
def list_generations():
    """
    List all generations with pagination

    Query params:
        limit: Number of results (default 50)
        offset: Offset for pagination (default 0)
        status: Filter by status (optional)
    """
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        status = request.args.get('status')

        generations = get_gen_manager().list_generations(
            limit=limit,
            offset=offset,
            status=status
        )

        return jsonify({
            'success': True,
            'generations': generations,
            'count': len(generations)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@history_api.route('/generations/<generation_id>', methods=['GET'])
def get_generation(generation_id):
    """Get detailed generation information"""
    try:
        generation = get_gen_manager().get_generation(generation_id)

        if not generation:
            return jsonify({
                'success': False,
                'error': 'Generation not found'
            }), 404

        return jsonify({
            'success': True,
            'generation': generation
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@history_api.route('/generations/<generation_id>/variants', methods=['GET'])
def get_generation_variants(generation_id):
    """Get all variants for a generation"""
    try:
        generation = get_gen_manager().get_generation(generation_id)

        if not generation:
            return jsonify({
                'success': False,
                'error': 'Generation not found'
            }), 404

        return jsonify({
            'success': True,
            'variants': generation.get('variants', [])
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@history_api.route('/variants/<variant_id>/scenes', methods=['GET'])
def get_variant_scenes(variant_id):
    """Get all scenes for a variant"""
    try:
        scenes = get_gen_manager().get_variant_scenes(variant_id)

        return jsonify({
            'success': True,
            'scenes': scenes
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@history_api.route('/generations/<generation_id>', methods=['DELETE'])
def delete_generation(generation_id):
    """Delete a generation and all related data"""
    try:
        success = get_gen_manager().delete_generation(generation_id)

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to delete generation'
            }), 500

        return jsonify({
            'success': True,
            'message': 'Generation deleted successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@history_api.route('/library', methods=['GET'])
def get_library():
    """
    Get library view - all completed generations with videos

    Query params:
        limit: Number of results (default 20)
        offset: Offset for pagination (default 0)
    """
    try:
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))

        # Get only completed generations
        generations = get_gen_manager().list_generations(
            limit=limit,
            offset=offset,
            status='completed'
        )

        # Format for library view
        library_items = []
        for gen in generations:
            # Count total videos
            total_videos = 0
            for variant in gen.get('variants', []):
                if variant['status'] == 'completed':
                    total_videos += variant.get('scenes_completed', 0)

            library_items.append({
                'id': gen['id'],
                'source_video_url': gen['source_video_url'],
                'created_at': gen['created_at'],
                'completed_at': gen['completed_at'],
                'total_variants': gen['total_variants'],
                'variant_types': gen['variant_types'],
                'total_videos': total_videos,
                'variants': gen.get('variants', [])
            })

        return jsonify({
            'success': True,
            'library': library_items,
            'count': len(library_items)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@history_api.route('/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    try:
        # Get all generations
        all_gens = get_gen_manager().list_generations(limit=1000)

        stats = {
            'total_generations': len(all_gens),
            'completed': len([g for g in all_gens if g['status'] == 'completed']),
            'processing': len([g for g in all_gens if g['status'] == 'processing']),
            'failed': len([g for g in all_gens if g['status'] == 'failed']),
            'total_cost': sum(float(g.get('actual_cost') or 0) for g in all_gens),
            'total_videos': 0
        }

        # Count total videos
        for gen in all_gens:
            for variant in gen.get('variants', []):
                if variant['status'] == 'completed':
                    stats['total_videos'] += variant.get('scenes_completed', 0)

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def register_history_api(app):
    """Register history API blueprint with Flask app"""
    app.register_blueprint(history_api)
