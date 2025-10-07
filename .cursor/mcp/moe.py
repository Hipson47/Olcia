import yaml
import re
import random
from typing import Dict, List, Any, Optional
from pathlib import Path


class MoERouter:
    """Mixture of Experts router with preselect→rank→run_experts→aggregate pipeline."""

    def __init__(self, config_path: str):
        """Initialize router with configuration from YAML file."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)['moe']

        self.router_config = self.config['router']
        self.experts = {expert['id']: expert for expert in self.config['experts']}
        self.routing_rules = self.config['routing_rules']

    def _extract_features(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract routing features from goal and context."""
        features = {}

        # File extension detection (simplified - would need actual file context)
        features['file_ext'] = 'py'  # Default assumption

        # Goal keyword analysis
        goal_lower = goal.lower()
        features['goal_keywords'] = goal_lower

        # RAG requirement detection
        features['requires_rag'] = any(word in goal_lower for word in ['research', 'evidence', 'cite', 'docs', 'knowledge'])

        # Safety risk assessment
        features['safety_risk'] = any(word in goal_lower for word in ['security', 'auth', 'secret', 'encrypt', 'dangerous'])

        # Test presence (simplified)
        features['test_presence'] = any(word in goal_lower for word in ['test', 'spec', 'assert', 'tdd'])

        return features

    def _preselect_experts(self, features: Dict[str, Any]) -> List[str]:
        """Preselect experts based on routing rules."""
        selected = set()

        for rule in self.routing_rules:
            condition = rule['if']
            pick_list = rule['pick']

            # Simple condition evaluation (would need more sophisticated parser in production)
            if self._evaluate_condition(condition, features):
                selected.update(pick_list)

        return list(selected) if selected else ['coder']  # Default fallback

    def _evaluate_condition(self, condition: str, features: Dict[str, Any]) -> bool:
        """Simple condition evaluator for routing rules."""
        # Handle regex matches
        regex_match = re.search(r'(\w+)\s*~=\s*/([^/]+)/i?', condition)
        if regex_match:
            var_name, pattern = regex_match.groups()
            if var_name in features:
                return bool(re.search(pattern, features[var_name], re.IGNORECASE))

        # Handle equality
        if '==' in condition:
            var_name, value = condition.split('==')
            var_name = var_name.strip()
            value = value.strip().strip("'\"")
            return str(features.get(var_name, '')).lower() == value.lower()

        # Handle array membership
        if ' in ' in condition:
            var_name, values_str = condition.split(' in ')
            var_name = var_name.strip()
            values_str = values_str.strip()
            if values_str.startswith('[') and values_str.endswith(']'):
                values = [v.strip().strip("'\"") for v in values_str[1:-1].split(',')]
                return features.get(var_name, '') in values

        # Handle keyword matching (simplified)
        if 'goal_keywords' in condition and '~=' in condition:
            return self._evaluate_condition(condition.replace('goal_keywords', 'goal_keywords'), features)

        return False

    def _rank_experts(self, candidates: List[str], features: Dict[str, Any]) -> List[tuple[str, float]]:
        """Rank experts by relevance score."""
        ranked = []
        for expert_id in candidates:
            if expert_id not in self.experts:
                continue

            expert = self.experts[expert_id]
            score = 0.0

            # Feature matching scoring
            if features.get('requires_rag') and 'rag' in expert['tools']:
                score += 0.3
            if features.get('safety_risk') and 'secrets_scan' in expert['strengths']:
                score += 0.3
            if features.get('test_presence') and 'tdd' in expert['strengths']:
                score += 0.2

            # Keyword relevance
            goal_keywords = features.get('goal_keywords', '')
            for strength in expert['strengths']:
                if strength in goal_keywords:
                    score += 0.2

            ranked.append((expert_id, min(score + 0.1, 1.0)))  # Minimum 0.1 score

        # Sort by score descending, take top_k
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:self.router_config['top_k']]

    def _run_experts(self, ranked_experts: List[tuple[str, float]], goal: str) -> List[Dict[str, Any]]:
        """Simulate running experts (placeholder for actual expert execution)."""
        results = []
        for expert_id, confidence in ranked_experts:
            # Simulate expert response with varying confidence
            result = {
                'expert_id': expert_id,
                'confidence': confidence + random.uniform(-0.1, 0.1),  # Add some variance
                'response': f"Expert {expert_id} analysis for: {goal}",
                'tools_used': self.experts[expert_id]['tools'],
                'strengths_applied': self.experts[expert_id]['strengths']
            }
            results.append(result)

            # Early stopping if confidence is high enough
            if result['confidence'] >= self.router_config['early_stop_confidence']:
                break

        return results

    def _aggregate_results(self, expert_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate expert results using confidence-weighted voting."""
        if not expert_results:
            return {'final_decision': 'no_experts_available', 'confidence': 0.0}

        # Confidence-weighted voting
        total_weight = sum(result['confidence'] for result in expert_results)
        vote_distribution = {}

        for result in expert_results:
            weight = result['confidence'] / total_weight if total_weight > 0 else 1.0
            for strength in result['strengths_applied']:
                vote_distribution[strength] = vote_distribution.get(strength, 0) + weight

        # Determine winning approach
        winning_strength = max(vote_distribution.items(), key=lambda x: x[1])

        return {
            'chosen_experts': [r['expert_id'] for r in expert_results],
            'vote_distribution': vote_distribution,
            'winning_approach': winning_strength[0],
            'final_confidence': winning_strength[1],
            'expert_results': expert_results
        }

    def route_task(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main routing pipeline: preselect → rank → run_experts → aggregate."""
        # Extract features
        features = self._extract_features(goal, context)

        # Preselect candidates
        candidates = self._preselect_experts(features)

        # Rank experts
        ranked_experts = self._rank_experts(candidates, features)

        # Run experts (simulated)
        expert_results = self._run_experts(ranked_experts, goal)

        # Aggregate results
        final_result = self._aggregate_results(expert_results)

        return {
            'goal': goal,
            'features': features,
            'candidates': candidates,
            'ranked_experts': ranked_experts,
            **final_result
        }
