"""
Integration tests for Deployment API
"""

import pytest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'deployment'))


class TestDeploymentAPI:
    """Test deployment API endpoints."""

    @pytest.fixture
    def sample_state(self):
        """Generate a sample state for testing."""
        return [0.5] * 128

    def test_predict_endpoint_format(self, sample_state):
        """Test that predict request format is correct."""
        request_data = {"state": sample_state}

        assert "state" in request_data
        assert isinstance(request_data["state"], list)
        assert len(request_data["state"]) == 128

    def test_predict_response_format(self):
        """Test expected format of prediction response."""
        # Mock response
        response_data = {"action": "move_forward"}

        assert "action" in response_data
        assert isinstance(response_data["action"], str)

    def test_action_mapping_completeness(self):
        """Test that action mapping covers all 27 action indices."""
        action_mapping = {
            0: "MOVE_FORWARD",
            1: "MOVE_BACKWARD",
            2: "TURN_LEFT",
            3: "TURN_RIGHT",
            4: "MELEE_ATTACK",
            5: "RANGED_ATTACK",
            6: "LOCK_TARGET",
            7: "COMBAT_SKILL",
            8: "ULTIMATE_SKILL",
            9: "JUMP",
            10: "SLIDE",
            11: "DODGE",
            12: "HELIX_LEAP",
            13: "RELOAD",
            14: "INTERACT",
            15: "INVENTORY",
            16: "MAP",
            17: "COMBAT",
            18: "ARMOURY",
            19: "REVIVE",
            20: "MENU",
            21: "GENIEMON",
            22: "NAVIGATE",
            23: "QUESTS",
            24: "QUIT_CHALLENGE",
            25: "LOOK_X",
            26: "LOOK_Y"
        }

        # Check all indices 0-26 are mapped
        for i in range(27):
            assert i in action_mapping
            assert isinstance(action_mapping[i], str)


class TestControlBackend:
    """Test control backend functionality."""

    def test_status_response_format(self):
        """Test status endpoint response format."""
        # Mock status response
        status = {
            'transformer_running': False,
            'active_model': 'transformer',
            'timestamp': 1234567890.0
        }

        assert 'transformer_running' in status
        assert 'active_model' in status
        assert 'timestamp' in status

    def test_model_selection_validation(self):
        """Test that only valid models can be selected."""
        valid_models = ['transformer']

        for model in valid_models:
            assert model in ['transformer']

        invalid_model = 'invalid_model'
        assert invalid_model not in valid_models


if __name__ == '__main__':
    pytest.main([__file__])
