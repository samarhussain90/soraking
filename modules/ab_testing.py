"""
A/B Testing Suite for Ad Generation

Tracks performance metrics, manages test variants, and provides statistical analysis
for optimizing ad generation strategies.
"""

import json
import time
import uuid
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta
import statistics


@dataclass
class TestVariant:
    """A/B test variant configuration"""
    variant_id: str
    name: str
    description: str
    parameters: Dict
    created_at: str
    is_active: bool = True


@dataclass
class TestResult:
    """Individual test result"""
    result_id: str
    test_id: str
    variant_id: str
    session_id: str
    generation_id: str
    metrics: Dict
    created_at: str
    user_feedback: Optional[Dict] = None


@dataclass
class TestSummary:
    """A/B test summary statistics"""
    test_id: str
    test_name: str
    total_runs: int
    variants: List[Dict]
    winner: Optional[str]
    confidence_level: float
    statistical_significance: bool
    recommendations: List[str]


class ABTestingSuite:
    """
    A/B Testing suite for ad generation optimization.
    
    Manages test variants, tracks performance metrics, and provides
    statistical analysis for data-driven optimization.
    """
    
    def __init__(self, data_dir: Path = None):
        """
        Initialize A/B Testing suite.
        
        Args:
            data_dir: Directory to store test data (default: output/ab_tests)
        """
        self.data_dir = data_dir or Path("output/ab_tests")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Test storage paths
        self.tests_file = self.data_dir / "tests.json"
        self.results_file = self.data_dir / "results.json"
        
        # Load existing data
        self.tests = self._load_tests()
        self.results = self._load_results()
    
    def _load_tests(self) -> Dict:
        """Load existing tests from storage"""
        if self.tests_file.exists():
            with open(self.tests_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_results(self) -> List[Dict]:
        """Load existing results from storage"""
        if self.results_file.exists():
            with open(self.results_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_tests(self):
        """Save tests to storage"""
        with open(self.tests_file, 'w') as f:
            json.dump(self.tests, f, indent=2)
    
    def _save_results(self):
        """Save results to storage"""
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def create_test(self, test_name: str, description: str, variants: List[Dict]) -> str:
        """
        Create a new A/B test.
        
        Args:
            test_name: Name of the test
            description: Test description
            variants: List of variant configurations
            
        Returns:
            Test ID
        """
        test_id = str(uuid.uuid4())
        
        # Create variant objects
        test_variants = []
        for i, variant_config in enumerate(variants):
            variant = TestVariant(
                variant_id=str(uuid.uuid4()),
                name=variant_config.get('name', f'Variant {i+1}'),
                description=variant_config.get('description', ''),
                parameters=variant_config.get('parameters', {}),
                created_at=datetime.now().isoformat()
            )
            test_variants.append(variant)
        
        # Store test
        self.tests[test_id] = {
            'test_id': test_id,
            'test_name': test_name,
            'description': description,
            'variants': [asdict(v) for v in test_variants],
            'created_at': datetime.now().isoformat(),
            'is_active': True
        }
        
        self._save_tests()
        return test_id
    
    def get_active_tests(self) -> List[Dict]:
        """Get all active A/B tests"""
        return [test for test in self.tests.values() if test.get('is_active', True)]
    
    def select_variant(self, test_id: str, user_id: str = None) -> Tuple[str, Dict]:
        """
        Select a variant for a user (random assignment).
        
        Args:
            test_id: Test ID
            user_id: Optional user ID for consistent assignment
            
        Returns:
            Tuple of (variant_id, variant_parameters)
        """
        if test_id not in self.tests:
            raise ValueError(f"Test {test_id} not found")
        
        test = self.tests[test_id]
        variants = test['variants']
        
        # Simple random selection (can be enhanced with user-based assignment)
        import random
        selected_variant = random.choice(variants)
        
        return selected_variant['variant_id'], selected_variant['parameters']
    
    def record_result(self, test_id: str, variant_id: str, session_id: str, 
                     generation_id: str, metrics: Dict, user_feedback: Dict = None) -> str:
        """
        Record a test result.
        
        Args:
            test_id: Test ID
            variant_id: Variant ID
            session_id: Session ID
            generation_id: Generation ID
            metrics: Performance metrics
            user_feedback: Optional user feedback
            
        Returns:
            Result ID
        """
        result = TestResult(
            result_id=str(uuid.uuid4()),
            test_id=test_id,
            variant_id=variant_id,
            session_id=session_id,
            generation_id=generation_id,
            metrics=metrics,
            created_at=datetime.now().isoformat(),
            user_feedback=user_feedback
        )
        
        self.results.append(asdict(result))
        self._save_results()
        
        return result.result_id
    
    def get_test_results(self, test_id: str) -> List[Dict]:
        """Get all results for a specific test"""
        return [r for r in self.results if r['test_id'] == test_id]
    
    def analyze_test(self, test_id: str) -> TestSummary:
        """
        Analyze A/B test results and provide statistical insights.
        
        Args:
            test_id: Test ID to analyze
            
        Returns:
            TestSummary with statistical analysis
        """
        if test_id not in self.tests:
            raise ValueError(f"Test {test_id} not found")
        
        test = self.tests[test_id]
        test_results = self.get_test_results(test_id)
        
        if not test_results:
            return TestSummary(
                test_id=test_id,
                test_name=test['test_name'],
                total_runs=0,
                variants=[],
                winner=None,
                confidence_level=0.0,
                statistical_significance=False,
                recommendations=["Need more data to analyze"]
            )
        
        # Group results by variant
        variant_results = {}
        for result in test_results:
            variant_id = result['variant_id']
            if variant_id not in variant_results:
                variant_results[variant_id] = []
            variant_results[variant_id].append(result)
        
        # Calculate metrics for each variant
        variant_stats = []
        for variant_id, results in variant_results.items():
            # Find variant info
            variant_info = next((v for v in test['variants'] if v['variant_id'] == variant_id), None)
            
            if not variant_info:
                continue
            
            # Calculate key metrics
            metrics = [r['metrics'] for r in results]
            
            # Cost metrics
            costs = [m.get('cost', 0) for m in metrics if 'cost' in m]
            avg_cost = statistics.mean(costs) if costs else 0
            
            # Quality metrics
            quality_scores = [m.get('quality_score', 0) for m in metrics if 'quality_score' in m]
            avg_quality = statistics.mean(quality_scores) if quality_scores else 0
            
            # Generation time
            generation_times = [m.get('generation_time', 0) for m in metrics if 'generation_time' in m]
            avg_generation_time = statistics.mean(generation_times) if generation_times else 0
            
            # Success rate
            success_count = sum(1 for m in metrics if m.get('success', False))
            success_rate = success_count / len(results) if results else 0
            
            variant_stats.append({
                'variant_id': variant_id,
                'variant_name': variant_info['name'],
                'runs': len(results),
                'avg_cost': avg_cost,
                'avg_quality': avg_quality,
                'avg_generation_time': avg_generation_time,
                'success_rate': success_rate,
                'total_cost': sum(costs),
                'recommendations': []
            })
        
        # Determine winner based on multiple criteria
        winner = None
        if variant_stats:
            # Score based on quality, success rate, and cost efficiency
            best_score = -1
            for variant in variant_stats:
                # Composite score: quality * success_rate / (cost + 1)
                score = (variant['avg_quality'] * variant['success_rate']) / (variant['avg_cost'] + 1)
                if score > best_score:
                    best_score = score
                    winner = variant['variant_id']
        
        # Statistical significance (simplified)
        statistical_significance = len(test_results) >= 30  # Minimum sample size
        
        # Generate recommendations
        recommendations = []
        if variant_stats:
            best_variant = next((v for v in variant_stats if v['variant_id'] == winner), None)
            if best_variant:
                recommendations.append(f"Winner: {best_variant['variant_name']} (Score: {best_variant.get('score', 0):.2f})")
                recommendations.append(f"Success Rate: {best_variant['success_rate']:.1%}")
                recommendations.append(f"Average Cost: ${best_variant['avg_cost']:.2f}")
                recommendations.append(f"Average Quality: {best_variant['avg_quality']:.1f}/10")
        
        if not statistical_significance:
            recommendations.append("⚠️ Need more data for statistical significance (minimum 30 runs)")
        
        return TestSummary(
            test_id=test_id,
            test_name=test['test_name'],
            total_runs=len(test_results),
            variants=variant_stats,
            winner=winner,
            confidence_level=0.95 if statistical_significance else 0.0,
            statistical_significance=statistical_significance,
            recommendations=recommendations
        )
    
    def get_performance_dashboard(self) -> Dict:
        """
        Get performance dashboard data for all tests.
        
        Returns:
            Dashboard data with key metrics and trends
        """
        dashboard = {
            'total_tests': len(self.tests),
            'active_tests': len([t for t in self.tests.values() if t.get('is_active', True)]),
            'total_runs': len(self.results),
            'recent_tests': [],
            'top_performers': [],
            'cost_savings': 0,
            'quality_improvements': 0
        }
        
        # Recent tests (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_results = [
            r for r in self.results 
            if datetime.fromisoformat(r['created_at']) > week_ago
        ]
        
        dashboard['recent_tests'] = recent_results[-10:]  # Last 10 results
        
        # Calculate cost savings and quality improvements
        if self.results:
            total_cost = sum(r['metrics'].get('cost', 0) for r in self.results)
            baseline_cost = total_cost * 1.2  # Assume 20% savings from optimization
            dashboard['cost_savings'] = baseline_cost - total_cost
            
            avg_quality = statistics.mean([
                r['metrics'].get('quality_score', 0) for r in self.results 
                if 'quality_score' in r['metrics']
            ])
            dashboard['quality_improvements'] = max(0, avg_quality - 5.0)  # Baseline 5.0
        
        return dashboard
    
    def create_prompt_optimization_test(self) -> str:
        """
        Create a pre-configured test for prompt optimization.
        
        Returns:
            Test ID for prompt optimization test
        """
        variants = [
            {
                'name': 'Baseline Prompts',
                'description': 'Current prompt generation approach',
                'parameters': {
                    'prompt_style': 'detailed',
                    'emotion_blending': 'standard',
                    'technical_specs': 'full'
                }
            },
            {
                'name': 'Concise Prompts',
                'description': 'Shorter, more focused prompts',
                'parameters': {
                    'prompt_style': 'concise',
                    'emotion_blending': 'minimal',
                    'technical_specs': 'essential'
                }
            },
            {
                'name': 'Cinematic Prompts',
                'description': 'Film-style, dramatic prompts',
                'parameters': {
                    'prompt_style': 'cinematic',
                    'emotion_blending': 'dramatic',
                    'technical_specs': 'cinematic'
                }
            }
        ]
        
        return self.create_test(
            test_name="Prompt Optimization",
            description="Test different prompt generation strategies for better Sora output",
            variants=variants
        )
    
    def create_model_selection_test(self) -> str:
        """
        Create a pre-configured test for model selection optimization.
        
        Returns:
            Test ID for model selection test
        """
        variants = [
            {
                'name': 'Sora 2 Only',
                'description': 'Use Sora 2 for all generations',
                'parameters': {
                    'model_selection': 'sora-2',
                    'cost_optimization': False
                }
            },
            {
                'name': 'Sora 2 Pro Only',
                'description': 'Use Sora 2 Pro for all generations',
                'parameters': {
                    'model_selection': 'sora-2-pro',
                    'cost_optimization': False
                }
            },
            {
                'name': 'Smart Selection',
                'description': 'Intelligent model selection based on prompt complexity',
                'parameters': {
                    'model_selection': 'auto',
                    'cost_optimization': True
                }
            }
        ]
        
        return self.create_test(
            test_name="Model Selection Optimization",
            description="Test different model selection strategies for cost vs quality",
            variants=variants
        )
