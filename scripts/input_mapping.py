"""
Input Mapping Module
Maps predicted actions to keyboard/mouse inputs for game control

动作配置从 config/game_actions.json 加载，支持快速切换不同游戏的按键映射。
Action configuration loaded from config/game_actions.json, supports quick switching between different games.
"""

import json
import os
import time
import platform
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置文件路径 / Config file path
DEFAULT_CONFIG_PATH = "config/game_actions.json"
_config_cache: Optional[Dict[str, Any]] = None


def load_actions_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载游戏动作配置文件 / Load game actions configuration file
    
    Args:
        config_path: 配置文件路径，默认为 config/game_actions.json
                    Config file path, defaults to config/game_actions.json
    
    Returns:
        配置字典 / Configuration dictionary
    """
    global _config_cache
    
    # 优先使用环境变量指定的配置 / Prioritize environment variable
    if config_path is None:
        config_path = os.environ.get("GAME_ACTIONS_CONFIG", DEFAULT_CONFIG_PATH)
    
    # 使用缓存避免重复加载 / Use cache to avoid repeated loading
    if _config_cache is not None and _config_cache.get("_path") == config_path:
        return _config_cache
    
    # 确定配置文件绝对路径 / Determine absolute config path
    if not Path(config_path).is_absolute():
        # 相对于项目根目录 / Relative to project root
        project_root = Path(__file__).parent.parent
        config_path = str(project_root / config_path)
    
    # 加载配置 / Load configuration
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 验证必填字段 / Validate required fields
        if "actions" not in config:
            raise ValueError("配置文件缺少 'actions' 字段 / Config missing 'actions' field")
        
        # 缓存配置 / Cache configuration
        config["_path"] = config_path
        _config_cache = config
        
        game_name = config.get("game_name", "Unknown")
        action_count = len(config["actions"])
        logger.info(f"✅ 加载配置 / Loaded config: {game_name} ({action_count} actions) from {config_path}")
        
        return config
        
    except FileNotFoundError:
        logger.error(f"❌ 配置文件不存在 / Config file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"❌ 配置文件JSON格式错误 / Config JSON parse error: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ 加载配置失败 / Failed to load config: {e}")
        raise


def get_action_type_enum(config_path: Optional[str] = None) -> type:
    """
    动态生成 ActionType 枚举类 / Dynamically generate ActionType enum class
    
    Args:
        config_path: 配置文件路径 / Config file path
    
    Returns:
        ActionType 枚举类 / ActionType enum class
    """
    config = load_actions_config(config_path)
    
    # 从配置生成枚举成员 / Generate enum members from config
    enum_members = {}
    for action in config["actions"]:
        action_name = action["name"]
        enum_members[action_name] = action_name
    
    # 动态创建枚举类 / Dynamically create enum class
    ActionType = Enum("ActionType", enum_members)
    ActionType.__doc__ = f"动作类型枚举 (共{len(enum_members)}个动作) / Action Type Enum ({len(enum_members)} actions)"
    
    return ActionType


# 动态生成默认的 ActionType / Dynamically generate default ActionType
ActionType = get_action_type_enum()


class KeyboardController:
    """
    Abstract keyboard controller that handles keyboard input simulation.
    Platform-specific implementations should be created based on the OS.
    """

    def __init__(self):
        self.os_type = platform.system()
        self.active_keys = set()
        logger.info(f"Initialized KeyboardController for {self.os_type}")

    def _normalize_key(self, key):
        """
        Normalize key representation for keyboard input.

        Args:
            key: Key to normalize (str or tuple)

        Returns:
            str: Normalized key name for keyboard input
        """
        if isinstance(key, tuple) and len(key) >= 1:
            key_type = key[0]
            key_value = key[1] if len(key) > 1 else None

            if key_type in ("control", "ctrl"):
                return "ctrl"
            if key_type == "shift":
                return "shift"
            if key_type == "alt":
                return "alt"

            return key_value or key_type

        return key

    def press_key(self, key):
        """
        Press a key or mouse button.

        Args:
            key: Key to press (str) or tuple for mouse events like ('mouse', 'left')
        """
        try:
            if isinstance(key, tuple) and key[0] == 'mouse':
                # Handle mouse input
                self._handle_mouse_press(key[1])
            else:
                # Handle keyboard input
                normalized_key = self._normalize_key(key)
                if self.os_type == "Windows":
                    self._press_key_windows(normalized_key)
                elif self.os_type == "Linux":
                    self._press_key_linux(normalized_key)
                elif self.os_type == "Darwin":  # macOS
                    self._press_key_mac(normalized_key)
            self.active_keys.add(normalized_key if not (isinstance(key, tuple) and key[0] == 'mouse') else key)
            logger.debug(f"Pressed key: {key}")
        except Exception as e:
            logger.error(f"Error pressing key {key}: {e}")

    def release_key(self, key):
        """
        Release a key or mouse button.

        Args:
            key: Key to release (str) or tuple for mouse events
        """
        try:
            if isinstance(key, tuple) and key[0] == 'mouse':
                # Handle mouse input
                self._handle_mouse_release(key[1])
            else:
                # Handle keyboard input
                normalized_key = self._normalize_key(key)
                if self.os_type == "Windows":
                    self._release_key_windows(normalized_key)
                elif self.os_type == "Linux":
                    self._release_key_linux(normalized_key)
                elif self.os_type == "Darwin":
                    self._release_key_mac(normalized_key)
            self.active_keys.discard(normalized_key if not (isinstance(key, tuple) and key[0] == 'mouse') else key)
            logger.debug(f"Released key: {key}")
        except Exception as e:
            logger.error(f"Error releasing key {key}: {e}")

    def release_all_keys(self):
        """Release all currently pressed keys."""
        for key in list(self.active_keys):
            self.release_key(key)

    def _press_key_windows(self, key: str):
        """Windows-specific key press implementation."""
        try:
            import win32api
            import win32con
            key_code = self._get_windows_keycode(key)
            win32api.keybd_event(key_code, 0, 0, 0)
        except ImportError:
            logger.warning("win32api not available. Install pywin32 for Windows support.")

    def _release_key_windows(self, key: str):
        """Windows-specific key release implementation."""
        try:
            import win32api
            import win32con
            key_code = self._get_windows_keycode(key)
            win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        except ImportError:
            logger.warning("win32api not available. Install pywin32 for Windows support.")

    def _press_key_linux(self, key: str):
        """Linux-specific key press implementation."""
        try:
            from pynput.keyboard import Controller, Key
            controller = Controller()
            controller.press(key)
        except ImportError:
            logger.warning("pynput not available. Install pynput for Linux support.")

    def _release_key_linux(self, key: str):
        """Linux-specific key release implementation."""
        try:
            from pynput.keyboard import Controller, Key
            controller = Controller()
            controller.release(key)
        except ImportError:
            logger.warning("pynput not available. Install pynput for Linux support.")

    def _press_key_mac(self, key: str):
        """macOS-specific key press implementation."""
        try:
            from pynput.keyboard import Controller, Key
            controller = Controller()
            controller.press(key)
        except ImportError:
            logger.warning("pynput not available. Install pynput for macOS support.")

    def _release_key_mac(self, key: str):
        """macOS-specific key release implementation."""
        try:
            from pynput.keyboard import Controller, Key
            controller = Controller()
            controller.release(key)
        except ImportError:
            logger.warning("pynput not available. Install pynput for macOS support.")

    def _get_windows_keycode(self, key: str) -> int:
        """
        Get Windows virtual key code for a given key.

        Args:
            key (str): Key name

        Returns:
            int: Virtual key code
        """
        key_map = {
            'w': 0x57, 'a': 0x41, 's': 0x53, 'd': 0x44,
            'space': 0x20, 'shift': 0x10, 'ctrl': 0x11,
            'shift_l': 0x10, 'shift_r': 0x10,
            'ctrl_l': 0x11, 'ctrl_r': 0x11,
            'alt': 0x12, 'alt_l': 0x12, 'alt_r': 0x12,
            'e': 0x45, 'E': 0x45, 'f': 0x46, 'q': 0x51, 'Q': 0x51, 'r': 0x52, 'R': 0x52,
            'tab': 0x09, 'esc': 0x1B, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
            'left': 0x25, 'up': 0x26, 'right': 0x27, 'down': 0x28,
            'x': 0x58, 'X': 0x58, 'z': 0x5a, 'Z': 0x5a,
            'v': 0x56, 'V': 0x56, 'j': 0x4a, 'J': 0x4a, 'p': 0x50, 'P': 0x50,
            'b': 0x42, 'B': 0x42, 'c': 0x43, 'C': 0x43, 'm': 0x4d, 'M': 0x4d, 'l': 0x4c, 'L': 0x4c
        }
        return key_map.get(key, 0x00)
    
    def _handle_mouse_press(self, button: str):
        """
        Handle mouse button press and scroll.

        Args:
            button (str): Mouse button ('left', 'right', 'middle'), 
                         motion ('motion_x', 'motion_y'),
                         or scroll ('scroll_up', 'scroll_down')
        """
        try:
            from pynput.mouse import Controller, Button
            mouse = Controller()
            if button == 'left':
                logger.debug("Mouse left button press")
            elif button == 'right':
                logger.debug("Mouse right button press")
            elif button == 'middle':
                logger.debug("Mouse middle button press")
            elif button == 'motion_x':
                logger.debug("Mouse motion X detected")
            elif button == 'motion_y':
                logger.debug("Mouse motion Y detected")
            elif button == 'scroll_up':
                logger.debug("Mouse scroll up")
                mouse.scroll(0, 1)  # Scroll up
            elif button == 'scroll_down':
                logger.debug("Mouse scroll down")
                mouse.scroll(0, -1)  # Scroll down
        except ImportError:
            logger.warning("pynput not available. Install pynput for mouse support.")
    
    def _handle_mouse_release(self, button: str):
        """
        Handle mouse button release.

        Args:
            button (str): Mouse button ('left', 'right', 'middle'), 
                         motion, or scroll
        """
        try:
            from pynput.mouse import Controller, Button
            mouse = Controller()
            if button == 'left':
                logger.debug("Mouse left button release")
            elif button == 'right':
                logger.debug("Mouse right button release")
            elif button == 'middle':
                logger.debug("Mouse middle button release")
            elif button in ('scroll_up', 'scroll_down'):
                logger.debug("Mouse scroll action completed")
                # Scroll actions don't need release
        except ImportError:
            logger.warning("pynput not available. Install pynput for mouse support.")


class ActionMapper:
    """
    Maps predicted action indices to keyboard/mouse inputs.
    动作映射器，支持从配置文件加载 / Supports loading from config file
    """

    def __init__(self, config_path: Optional[str] = None, custom_mapping: Optional[Dict] = None):
        """
        Initialize ActionMapper with configuration file or custom mapping.

        Args:
            config_path: 配置文件路径 / Config file path (default: config/game_actions.json)
            custom_mapping: 自定义映射（优先于配置文件）/ Custom mapping (overrides config file)
        """
        self.controller = KeyboardController()
        self.config_path = config_path
        
        # 优先使用自定义映射，否则从配置加载 / Use custom mapping first, otherwise load from config
        if custom_mapping is not None:
            self.action_mapping = custom_mapping
            self.actions_config = None
            logger.info("ActionMapper initialized with custom mapping")
        else:
            self.actions_config = load_actions_config(config_path)
            self.action_mapping = self._build_mapping_from_config()
            game_name = self.actions_config.get("game_name", "Unknown")
            logger.info(f"ActionMapper initialized for: {game_name}")
        
        self.last_action = None
        self.action_duration = 0.1  # Default action duration in seconds

    def _build_mapping_from_config(self) -> Dict[str, List]:
        """
        从配置文件构建动作映射 / Build action mapping from config file

        Returns:
            dict: 动作名称到按键列表的映射 / Mapping of action names to key lists
        """
        mapping = {}
        
        for action in self.actions_config["actions"]:
            action_name = action["name"]
            keys = action.get("keys", [])
            
            # 转换按键格式 / Convert key format
            converted_keys = []
            for key in keys:
                if isinstance(key, list):
                    # 复合按键如 ["mouse", "left"] 转为元组 / Convert compound keys to tuple
                    converted_keys.append(tuple(key))
                else:
                    # 普通按键保持字符串 / Keep normal keys as string
                    converted_keys.append(key)
            
            mapping[action_name] = converted_keys
        
        return mapping
    
    def get_action_count(self) -> int:
        """
        获取动作总数 / Get total number of actions
        
        Returns:
            int: 动作数量 / Number of actions
        """
        if self.actions_config:
            return len(self.actions_config["actions"])
        return len(self.action_mapping)
    
    def get_action_name_by_id(self, action_id: int) -> Optional[str]:
        """
        根据动作ID获取动作名称 / Get action name by ID
        
        Args:
            action_id: 动作索引 / Action index
            
        Returns:
            str: 动作名称，如果ID无效则返回None / Action name, or None if ID invalid
        """
        if self.actions_config:
            for action in self.actions_config["actions"]:
                if action["id"] == action_id:
                    return action["name"]
        return None
    
    def get_action_info(self, action_name: str) -> Optional[Dict[str, Any]]:
        """
        获取动作的完整信息 / Get full information for an action
        
        Args:
            action_name: 动作名称 / Action name
            
        Returns:
            dict: 动作信息（包含显示名称、分类等）/ Action info (display names, category, etc.)
        """
        if self.actions_config:
            for action in self.actions_config["actions"]:
                if action["name"] == action_name:
                    return action
        return None

    def execute_action(self, action_name: str, duration: Optional[float] = None):
        """
        Execute an action by pressing the corresponding keys.

        Args:
            action_name (str): Name of the action to execute
            duration (float, optional): Duration to hold the keys (seconds)
        """
        if action_name not in self.action_mapping:
            logger.warning(f"Unknown action: {action_name}")
            return

        # Release previous action keys
        if self.last_action is not None and self.last_action in self.action_mapping:
            for key in self.action_mapping[self.last_action]:
                self.controller.release_key(key)

        # Execute new action
        keys = self.action_mapping[action_name]

        logger.info(f"Executing action: {action_name}")

        for key in keys:
            self.controller.press_key(key)

        # Hold keys for specified duration
        if duration is not None:
            time.sleep(duration)
            for key in keys:
                self.controller.release_key(key)
        else:
            # Store current action for release in next iteration
            self.last_action = action_name

    def execute_action_sequence(self, action_sequence: List[str], duration_per_action: float = 0.1):
        """
        Execute a sequence of actions.

        Args:
            action_sequence (list): List of action names to execute
            duration_per_action (float): Duration for each action in seconds
        """
        logger.info(f"Executing action sequence of length {len(action_sequence)}")

        for action in action_sequence:
            self.execute_action(action, duration=duration_per_action)
            time.sleep(0.05)  # Small delay between actions

        self.controller.release_all_keys()

    def stop_all_actions(self):
        """Stop all current actions and release all keys."""
        logger.info("Stopping all actions")
        self.controller.release_all_keys()
        self.last_action = None

    def update_mapping(self, new_mapping: Dict[int, List[str]]):
        """
        Update the action-to-key mapping.

        Args:
            new_mapping (dict): New mapping configuration
        """
        self.action_mapping.update(new_mapping)
        logger.info("Action mapping updated")

    def get_action_name(self, action_name: str) -> str:
        """
        Validate and get the name of an action.

        Args:
            action_name (str): Action name

        Returns:
            str: Action name if valid, else UNKNOWN
        """
        if action_name in self.action_mapping:
            return action_name
        return "UNKNOWN"

# ACTION 映射（匹配你的 22 类）
# =============================================================================
# 便捷函数 / Convenience Functions
# =============================================================================

def get_action_mapper(config_path: Optional[str] = None) -> ActionMapper:
    """
    获取全局ActionMapper实例（单例模式）/ Get global ActionMapper instance (singleton)
    
    Args:
        config_path: 配置文件路径 / Config file path
    
    Returns:
        ActionMapper: 动作映射器实例 / Action mapper instance
    """
    global _action_mapper
    
    if _action_mapper is None:
        _action_mapper = ActionMapper(config_path=config_path)
    
    return _action_mapper


def reload_action_mapper(config_path: Optional[str] = None) -> ActionMapper:
    """
    重新加载ActionMapper（用于切换游戏配置）/ Reload ActionMapper (for switching game config)
    
    Args:
        config_path: 新的配置文件路径 / New config file path
    
    Returns:
        ActionMapper: 新的动作映射器实例 / New action mapper instance
    """
    global _action_mapper, _config_cache
    
    # 清除缓存 / Clear cache
    _config_cache = None
    _action_mapper = ActionMapper(config_path=config_path)
    
    return _action_mapper


# 全局单例实例 / Global singleton instance
_action_mapper: Optional[ActionMapper] = None


# =============================================================================
# 向后兼容 / Backward Compatibility
# =============================================================================

# 保留旧的ACTION_MAPPING字典以兼容现有代码 / Keep old ACTION_MAPPING dict for compatibility
# 注意：此字典从配置文件动态生成 / Note: This dict is dynamically generated from config
try:
    _temp_config = load_actions_config()
    ACTION_MAPPING: Dict[str, List] = {}
    for action in _temp_config["actions"]:
        keys = []
        for key in action.get("keys", []):
            if isinstance(key, list):
                keys.append(tuple(key))
            else:
                keys.append(key)
        ACTION_MAPPING[action["name"]] = keys
    del _temp_config
except Exception as e:
    logger.warning(f"⚠️ 无法加载配置文件，使用空映射 / Failed to load config, using empty mapping: {e}")
    ACTION_MAPPING = {}



def get_action_mapper(config: Optional[Dict] = None) -> ActionMapper:
    """
    Get or create the global ActionMapper instance.

    Args:
        config (dict, optional): Custom action-to-key mapping

    Returns:
        ActionMapper: The global action mapper instance
    """
    global _action_mapper
    if _action_mapper is None:
        _action_mapper = ActionMapper(config)
    return _action_mapper


def main():
    """
    Test the input mapping functionality.
    """
    print("Testing Input Mapping...")

    mapper = get_action_mapper()

    # Test individual actions
    print("\nTesting individual actions:")
    for action in ActionType:
        print(f"  - {action.value}")
        mapper.execute_action(action.value, duration=0.2)
        time.sleep(0.3)

    # Test action sequence
    print("\nTesting action sequence:")
    sequence = [
        ActionType.MOVE_FORWARD.value,
        ActionType.TURN_RIGHT.value,
        ActionType.JUMP.value,
        ActionType.MELEE_ATTACK.value
    ]
    mapper.execute_action_sequence(sequence, duration_per_action=0.2)

    # Stop all actions
    mapper.stop_all_actions()
    print("\nTesting completed!")


if __name__ == "__main__":
    main()
