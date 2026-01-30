"""
Configuration Module for AI Gameplay Bot
配置模块 - AI游戏机器人的集中配置管理
Centralized configuration management
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables / 加载环境变量
load_dotenv()

# Base directory / 基础目录
BASE_DIR = Path(__file__).parent

# Environment / 环境配置
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # 开发/生产环境
DEBUG = ENVIRONMENT == 'development'  # 调试模式

# Logging / 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # 日志级别
LOG_DIR = BASE_DIR / 'logs'  # 日志目录
LOG_DIR.mkdir(exist_ok=True)

# Service Ports / 服务端口
NN_PORT = int(os.getenv('NN_PORT', 5000))  # 神经网络服务端口
TRANSFORMER_PORT = int(os.getenv('TRANSFORMER_PORT', 5001))  # Transformer服务端口
CONTROL_PORT = int(os.getenv('CONTROL_PORT', 8000))  # 控制后端端口

# Model Paths / 模型路径
MODELS_DIR = BASE_DIR / 'models'
TRANSFORMER_MODEL_PATH = MODELS_DIR / 'transformer' / 'transformer_model.pth'  # Transformer基础模型
TRANSFORMER_FINETUNED_PATH = MODELS_DIR / 'transformer' / 'transformer_model_finetuned.pth'  # 微调模型

# Data Paths / 数据路径
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'  # 原始游戏数据
PROCESSED_DATA_DIR = DATA_DIR / 'processed'  # 处理后的特征数据
FEEDBACK_DIR = BASE_DIR / 'feedback'  # 用户反馈数据
RESULTS_DIR = BASE_DIR / 'results'  # 模型输出结果

# Model Configuration / 模型配置
TRANSFORMER_CONFIG = {
    'input_dim': 128,  # 输入维度（128维特征向量）
    'num_classes': 10,  # 动作类别数（10个游戏操作）
    'num_heads': 4,  # 多头注意力头数
    'num_layers': 3,  # Transformer编码器层数
    'hidden_dim': 256,  # 隐藏层维度
    'sequence_length': 10  # 输入序列长度（连续10帧）
}

# Training Configuration / 训练配置
TRAINING_CONFIG = {
    'batch_size': 32,  # 批大小
    'num_epochs': 50,  # 训练轮次
    'learning_rate': 0.001,  # 学习率
    'val_split': 0.2,  # 验证集比例
    'early_stopping_patience': 10  # 早停耐心值
}

# Action Mapping
ACTION_MAPPING = {
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

# Reverse mapping (action name to index)
ACTION_NAME_TO_INDEX = {v: k for k, v in ACTION_MAPPING.items()}

# Validate ACTION_MAPPING consistency
def validate_action_mapping():
    """验证 ACTION_MAPPING 的一致性和完整性"""
    # 检查索引连续性
    indices = sorted(ACTION_MAPPING.keys())
    expected = list(range(len(ACTION_MAPPING)))
    assert indices == expected, f"Action indices not continuous: expected {expected}, got {indices}"
    
    # 检查重复值
    values = list(ACTION_MAPPING.values())
    assert len(values) == len(set(values)), f"Duplicate action names found in ACTION_MAPPING"
    
    # 检查反向映射一致性
    for idx, name in ACTION_MAPPING.items():
        assert ACTION_NAME_TO_INDEX[name] == idx, f"Inconsistent mapping for '{name}': {idx} != {ACTION_NAME_TO_INDEX[name]}"
    
    print(f"✓ ACTION_MAPPING validated: {len(ACTION_MAPPING)} actions (0-{len(ACTION_MAPPING)-1})")

# 执行验证
try:
    validate_action_mapping()
except AssertionError as e:
    print(f"⚠️ ACTION_MAPPING validation failed: {e}")

# API Configuration
API_CONFIG = {
    'timeout': 30,
    'max_retries': 3,
    'backoff_factor': 0.3
}

# Monitoring
ENABLE_MONITORING = os.getenv('ENABLE_MONITORING', 'false').lower() == 'true'
METRICS_PORT = int(os.getenv('METRICS_PORT', 9090))

# Feature flags
FEATURE_FLAGS = {
    'enable_caching': True,
    'enable_metrics': ENABLE_MONITORING,
    'enable_debug_mode': DEBUG,
    'enable_profiling': False
}


def get_model_path(model_type='transformer', finetuned=True):
    """
    Get the path to a model file.

    Args:
        model_type (str): 'transformer' (only type supported)
        finetuned (bool): Whether to get finetuned or base model

    Returns:
        Path: Path to the model file
    """
    if model_type == 'transformer':
        return TRANSFORMER_FINETUNED_PATH if finetuned else TRANSFORMER_MODEL_PATH
    else:
        raise ValueError(f"Only 'transformer' model type is supported. Got: {model_type}")


def get_action_name(action_index):
    """
    Get action name from index.

    Args:
        action_index (int): Action index

    Returns:
        str: Action name
    """
    return ACTION_MAPPING.get(action_index, f"unknown_action_{action_index}")


def get_action_index(action_name):
    """
    Get action index from name.

    Args:
        action_name (str): Action name

    Returns:
        int: Action index or None if not found
    """
    return ACTION_NAME_TO_INDEX.get(action_name.lower())


class Config:
    """Configuration class for easy access to all settings."""

    def __init__(self):
        self.environment = ENVIRONMENT
        self.debug = DEBUG
        self.log_level = LOG_LEVEL
        self.nn_port = NN_PORT
        self.transformer_port = TRANSFORMER_PORT
        self.control_port = CONTROL_PORT

    def __repr__(self):
        return f"Config(environment='{self.environment}', debug={self.debug})"


# Global config instance
config = Config()
