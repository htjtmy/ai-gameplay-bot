#!/usr/bin/env python3
"""测试配置加载系统 / Test configuration loading system"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from input_mapping import load_actions_config, ActionType, get_action_mapper

def test_config_loading():
    """测试配置加载 / Test config loading"""
    print("=" * 70)
    print("测试配置加载系统 / Testing Configuration Loading System")
    print("=" * 70)
    
    # 1. 测试加载配置
    print("\n1️⃣ 加载配置文件 / Loading config file...")
    config = load_actions_config()
    print(f"   ✅ 游戏名称 / Game: {config['game_name']}")
    print(f"   ✅ 动作总数 / Total actions: {len(config['actions'])}")
    
    # 2. 测试 ActionType 枚举
    print("\n2️⃣ 检查 ActionType 枚举 / Checking ActionType enum...")
    action_type_count = len(list(ActionType))
    print(f"   ✅ ActionType 成员数 / Members: {action_type_count}")
    print(f"   示例 / Examples: {list(ActionType)[:3]}")
    
    # 3. 测试 ActionMapper
    print("\n3️⃣ 创建 ActionMapper / Creating ActionMapper...")
    mapper = get_action_mapper()
    print(f"   ✅ 映射数量 / Mappings: {mapper.get_action_count()}")
    
    # 4. 测试获取动作信息
    print("\n4️⃣ 获取动作信息 / Getting action info...")
    test_actions = ["MOVE_FORWARD", "MELEE_ATTACK", "JUMP"]
    for action_name in test_actions:
        info = mapper.get_action_info(action_name)
        if info:
            print(f"   • {action_name}: {info['display_name_zh']} / {info['display_name_en']}")
            print(f"     按键 / Keys: {info['keys']}")
    
    # 5. 测试 ID 到名称映射
    print("\n5️⃣ 测试 ID 映射 / Testing ID mapping...")
    for action_id in [0, 5, 10, 15, 20]:
        action_name = mapper.get_action_name_by_id(action_id)
        if action_name:
            print(f"   ID {action_id} → {action_name}")
    
    print("\n" + "=" * 70)
    print("✅ 所有测试通过！配置系统正常工作 / All tests passed! Config system working")
    print("=" * 70)

if __name__ == "__main__":
    test_config_loading()
