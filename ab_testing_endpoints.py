# A/B Testing API Endpoints
@app.route('/api/ab-testing/dashboard', methods=['GET'])
def get_ab_testing_dashboard():
    """Get A/B testing dashboard data"""
    try:
        ab_testing = ABTestingSuite()
        dashboard_data = ab_testing.get_performance_dashboard()
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ab-testing/tests', methods=['GET'])
def get_ab_tests():
    """Get all A/B tests"""
    try:
        ab_testing = ABTestingSuite()
        tests = ab_testing.get_active_tests()
        return jsonify({'tests': tests})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ab-testing/create', methods=['POST'])
def create_ab_test():
    """Create a new A/B test"""
    try:
        data = request.json
        test_name = data.get('test_name')
        description = data.get('description', '')
        variants = data.get('variants', [])
        
        if not test_name or len(variants) < 2:
            return jsonify({'error': 'Test name and at least 2 variants required'}), 400
        
        ab_testing = ABTestingSuite()
        test_id = ab_testing.create_test(test_name, description, variants)
        
        return jsonify({
            'success': True,
            'test_id': test_id,
            'message': 'A/B test created successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ab-testing/<test_id>/results', methods=['GET'])
def get_test_results(test_id):
    """Get results for a specific test"""
    try:
        ab_testing = ABTestingSuite()
        results = ab_testing.get_test_results(test_id)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ab-testing/<test_id>/analyze', methods=['GET'])
def analyze_test(test_id):
    """Analyze A/B test results"""
    try:
        ab_testing = ABTestingSuite()
        analysis = ab_testing.analyze_test(test_id)
        return jsonify(analysis.__dict__)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ab-testing/quick-test/<test_type>', methods=['POST'])
def create_quick_test(test_type):
    """Create a quick pre-configured test"""
    try:
        ab_testing = ABTestingSuite()
        
        if test_type == 'prompt':
            test_id = ab_testing.create_prompt_optimization_test()
        elif test_type == 'model':
            test_id = ab_testing.create_model_selection_test()
        else:
            return jsonify({'error': 'Invalid test type'}), 400
        
        return jsonify({
            'success': True,
            'test_id': test_id,
            'message': f'Quick {test_type} test created successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
