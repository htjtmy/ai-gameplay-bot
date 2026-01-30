"""
Unit tests for Input Mapping Module
测试动作映射模块（从配置文件加载）/ Test action mapping module (loaded from config)
"""

import pytest
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from input_mapping import ActionType, ActionMapper, get_action_mapper, load_actions_config


def load_expected_actions():
    """从配置文件加载预期的动作列表 / Load expected actions from config file"""
    try:
        config = load_actions_config()
        return [action["name"] for action in config["actions"]]
    except Exception as e:
        pytest.fail(f"无法加载配置文件 / Failed to load config: {e}")


class TestActionType:
    """Test ActionType enum."""

    def test_action_types_exist(self):
        """测试所有配置中的动作类型都存在于枚举中 / Test all configured action types exist in enum"""
        expected_actions = load_expected_actions()

        for action in expected_actions:
            assert hasattr(ActionType, action), f"动作不存在 / Action missing: {action}"

    def test_action_values(self):
        """Test that action values are strings."""
        assert ActionType.MOVE_FORWARD.value == "MOVE_FORWARD"
        assert ActionType.MELEE_ATTACK.value == "MELEE_ATTACK"
        # 不再测试 QUIT_CHALLENGE，因为它已从配置中移除 / No longer test QUIT_CHALLENGE as it's removed


class TestActionMapper:
    """Test ActionMapper class."""

    def test_mapper_initialization(self):
        """Test that ActionMapper initializes correctly."""
        mapper = ActionMapper()
        assert mapper is not None
        assert mapper.action_mapping is not None
        assert len(mapper.action_mapping) > 0

    def test_default_mapping(self):
        """测试默认映射包含配置中所有动作类型 / Test default mapping contains all configured action types"""
        mapper = ActionMapper()
        for action_type in ActionType:
            assert action_type.value in mapper.action_mapping

    def test_custom_mapping(self):
        """Test initialization with custom mapping."""
        custom_map = {"MOVE_FORWARD": ['custom_key']}
        mapper = ActionMapper(config=custom_map)
        assert mapper.action_mapping["MOVE_FORWARD"] == ['custom_key']

    def test_get_action_name(self):
        """Test validating action name."""
        mapper = ActionMapper()

        name = mapper.get_action_name("MELEE_ATTACK")
        assert name == 'MELEE_ATTACK'

        name = mapper.get_action_name("INVALID_ACTION")
        assert name == 'UNKNOWN'

    def test_update_mapping(self):
        """Test updating action mapping."""
        mapper = ActionMapper()
        new_mapping = {"JUMP": ['space', 'shift']}
        mapper.update_mapping(new_mapping)

        assert mapper.action_mapping["JUMP"] == ['space', 'shift']


class TestGlobalActionMapper:
    """Test global action mapper instance."""

    def test_get_action_mapper_singleton(self):
        """Test that get_action_mapper returns same instance."""
        mapper1 = get_action_mapper()
        mapper2 = get_action_mapper()

        assert mapper1 is mapper2


if __name__ == '__main__':
    pytest.main([__file__])
