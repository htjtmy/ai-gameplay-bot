#!/usr/bin/env python3
"""查看当前按键配置 / View Current Key Bindings"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from input_mapping import load_actions_config

def show_key_bindings():
    """显示所有按键配置 / Show all key bindings"""
    config = load_actions_config()
    
    config_name = config.get('config_name', '')
    config_title = f" - {config_name}" if config_name else ""
    
    print(f"\n🎮 游戏：{config['game_name']}{config_title}")
    print(f"📊 版本：{config.get('game_version', 'N/A')}")
    print(f"🔢 动作总数：{len(config['actions'])}")
    print("\n" + "=" * 80)
    print(f"{'ID':<4} {'动作名称':<20} {'中文':<12} {'按键':<25} {'手柄':<15}")
    print("=" * 80)
    
    # 按分类显示
    categories = {}
    for action in config['actions']:
        cat = action.get('category', 'other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(action)
    
    cat_names = config.get('categories', {})
    
    for cat_key, actions in sorted(categories.items()):
        cat_info = cat_names.get(cat_key, {})
        cat_name = cat_info.get('name_zh', cat_key)
        print(f"\n📁 {cat_name} ({cat_key})")
        print("-" * 80)
        
        for action in sorted(actions, key=lambda x: x['id']):
            action_id = action['id']
            name = action['name']
            display_zh = action.get('display_name_zh', '')
            keys = action.get('keys', [])
            gamepad = action.get('gamepad', '')
            
            # 格式化按键显示
            keys_str = ', '.join([
                str(k) if isinstance(k, str) else f"{k[0]}:{k[1]}"
                for k in keys
            ])
            
            print(f"{action_id:<4} {name:<20} {display_zh:<12} {keys_str:<25} {gamepad:<15}")
    
    print("\n" + "=" * 80)
    print("💡 提示：编辑 config/game_actions.json 可修改按键配置")
    print("💡 Tip: Edit config/game_actions.json to modify key bindings\n")

if __name__ == "__main__":
    show_key_bindings()
