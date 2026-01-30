#!/usr/bin/env python3
"""
配置验证工具 / Configuration Validation Tool

验证游戏动作配置文件的正确性，确保所有必填字段存在且格式正确。
Validates game action configuration files to ensure all required fields are present and correctly formatted.

Usage:
    python scripts/validate_actions_config.py config/game_actions.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set


class ConfigValidator:
    """配置验证器 / Configuration Validator"""
    
    REQUIRED_ROOT_FIELDS = ["game_name", "actions", "categories"]
    REQUIRED_ACTION_FIELDS = ["id", "name", "display_name_zh", "display_name_en", "category", "keys"]
    VALID_KEY_TYPES = ["mouse", "control", "shift", "alt"]
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.config: Dict[str, Any] = {}
        
    def validate(self) -> bool:
        """执行完整验证 / Perform full validation"""
        print(f"🔍 验证配置文件 / Validating config: {self.config_path}")
        print("=" * 70)
        
        # 1. 检查文件存在
        if not self._check_file_exists():
            return False
            
        # 2. 加载JSON
        if not self._load_json():
            return False
            
        # 3. 验证根字段
        if not self._validate_root_fields():
            return False
            
        # 4. 验证动作列表
        if not self._validate_actions():
            return False
            
        # 5. 验证分类
        if not self._validate_categories():
            return False
            
        # 6. 输出结果
        return self._print_results()
        
    def _check_file_exists(self) -> bool:
        """检查文件是否存在 / Check if file exists"""
        if not self.config_path.exists():
            self.errors.append(f"配置文件不存在 / Config file not found: {self.config_path}")
            return False
        return True
        
    def _load_json(self) -> bool:
        """加载JSON文件 / Load JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print("✅ JSON格式正确 / Valid JSON format")
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON解析错误 / JSON parse error: {e}")
            return False
        except Exception as e:
            self.errors.append(f"读取文件失败 / Failed to read file: {e}")
            return False
            
    def _validate_root_fields(self) -> bool:
        """验证根字段 / Validate root fields"""
        for field in self.REQUIRED_ROOT_FIELDS:
            if field not in self.config:
                self.errors.append(f"缺少必填字段 / Missing required field: '{field}'")
                
        if "game_name" in self.config:
            print(f"📌 游戏名称 / Game: {self.config['game_name']}")
            
        if "game_version" in self.config:
            print(f"📌 版本 / Version: {self.config['game_version']}")
            
        return len(self.errors) == 0
        
    def _validate_actions(self) -> bool:
        """验证动作列表 / Validate actions"""
        actions = self.config.get("actions", [])
        
        if not isinstance(actions, list):
            self.errors.append("'actions' 必须是数组 / 'actions' must be an array")
            return False
            
        if len(actions) == 0:
            self.errors.append("动作列表为空 / Action list is empty")
            return False
            
        print(f"📊 动作总数 / Total actions: {len(actions)}")
        
        # 收集所有ID和名称用于检查唯一性
        action_ids: Set[int] = set()
        action_names: Set[str] = set()
        expected_ids = set(range(len(actions)))
        
        for idx, action in enumerate(actions):
            # 检查必填字段
            for field in self.REQUIRED_ACTION_FIELDS:
                if field not in action:
                    self.errors.append(
                        f"动作 #{idx} 缺少字段 / Action #{idx} missing field: '{field}'"
                    )
                    
            # 验证ID
            action_id = action.get("id")
            if action_id is not None:
                if not isinstance(action_id, int):
                    self.errors.append(
                        f"动作 '{action.get('name', idx)}' 的ID必须是整数 / "
                        f"Action '{action.get('name', idx)}' ID must be integer"
                    )
                elif action_id in action_ids:
                    self.errors.append(
                        f"重复的动作ID / Duplicate action ID: {action_id}"
                    )
                else:
                    action_ids.add(action_id)
                    
            # 验证名称唯一性
            action_name = action.get("name")
            if action_name:
                if action_name in action_names:
                    self.errors.append(
                        f"重复的动作名称 / Duplicate action name: '{action_name}'"
                    )
                else:
                    action_names.add(action_name)
                    
                # 检查命名规范
                if not action_name.isupper() or not action_name.replace("_", "").isalnum():
                    self.warnings.append(
                        f"动作名称建议使用大写+下划线格式 / "
                        f"Action name should use UPPERCASE_WITH_UNDERSCORES: '{action_name}'"
                    )
                    
            # 验证按键格式
            self._validate_keys(action.get("keys", []), action.get("name", f"#{idx}"))
            
            # 验证分类引用
            category = action.get("category")
            if category and category not in self.config.get("categories", {}):
                self.warnings.append(
                    f"动作 '{action.get('name')}' 引用了未定义的分类 / "
                    f"Action '{action.get('name')}' references undefined category: '{category}'"
                )
                
        # 检查ID连续性
        if action_ids != expected_ids:
            missing_ids = expected_ids - action_ids
            if missing_ids:
                self.errors.append(
                    f"动作ID不连续，缺少 / Action IDs not sequential, missing: {sorted(missing_ids)}"
                )
            extra_ids = action_ids - expected_ids
            if extra_ids:
                self.errors.append(
                    f"动作ID超出范围 / Action IDs out of range: {sorted(extra_ids)}"
                )
                
        return len(self.errors) == 0
        
    def _validate_keys(self, keys: Any, action_name: str) -> None:
        """验证按键格式 / Validate key format"""
        if not isinstance(keys, list):
            self.errors.append(
                f"动作 '{action_name}' 的keys必须是数组 / "
                f"Action '{action_name}' keys must be an array"
            )
            return
            
        for key in keys:
            # 字符串按键（如 "w", "space"）
            if isinstance(key, str):
                continue
                
            # 数组按键（如 ["mouse", "left"]）
            elif isinstance(key, list):
                if len(key) != 2:
                    self.errors.append(
                        f"动作 '{action_name}' 的复合按键格式错误，应为[type, value] / "
                        f"Action '{action_name}' compound key format error, should be [type, value]"
                    )
                elif key[0] in self.VALID_KEY_TYPES:
                    pass  # 有效的特殊按键类型
                else:
                    self.warnings.append(
                        f"动作 '{action_name}' 使用了未知的按键类型 / "
                        f"Action '{action_name}' uses unknown key type: '{key[0]}'"
                    )
            else:
                self.errors.append(
                    f"动作 '{action_name}' 的按键格式无效 / "
                    f"Action '{action_name}' invalid key format: {key}"
                )
                
    def _validate_categories(self) -> bool:
        """验证分类定义 / Validate categories"""
        categories = self.config.get("categories", {})
        
        if not isinstance(categories, dict):
            self.errors.append("'categories' 必须是对象 / 'categories' must be an object")
            return False
            
        print(f"📂 分类总数 / Total categories: {len(categories)}")
        
        for cat_key, cat_info in categories.items():
            if not isinstance(cat_info, dict):
                self.errors.append(
                    f"分类 '{cat_key}' 的值必须是对象 / "
                    f"Category '{cat_key}' value must be an object"
                )
                continue
                
            if "name_zh" not in cat_info or "name_en" not in cat_info:
                self.warnings.append(
                    f"分类 '{cat_key}' 建议包含name_zh和name_en字段 / "
                    f"Category '{cat_key}' should include name_zh and name_en fields"
                )
                
        return True
        
    def _print_results(self) -> bool:
        """输出验证结果 / Print validation results"""
        print("=" * 70)
        
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} 个警告 / Warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")
                
        if self.errors:
            print(f"\n❌ {len(self.errors)} 个错误 / Errors:")
            for error in self.errors:
                print(f"  • {error}")
            print("\n❌ 验证失败 / Validation FAILED")
            return False
        else:
            print("\n✅ 验证成功！配置文件格式正确 / Validation PASSED! Config is valid")
            self._print_summary()
            return True
            
    def _print_summary(self) -> None:
        """打印配置摘要 / Print configuration summary"""
        actions = self.config.get("actions", [])
        categories = self.config.get("categories", {})
        
        print("\n📋 配置摘要 / Configuration Summary:")
        print(f"  • 游戏 / Game: {self.config.get('game_name', 'N/A')}")
        print(f"  • 动作总数 / Total Actions: {len(actions)}")
        print(f"  • 分类总数 / Total Categories: {len(categories)}")
        
        # 按分类统计动作数量
        category_counts: Dict[str, int] = {}
        for action in actions:
            cat = action.get("category", "unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1
            
        print("\n  分类分布 / Category Distribution:")
        for cat_key, count in sorted(category_counts.items()):
            cat_name = categories.get(cat_key, {}).get("name_zh", cat_key)
            print(f"    - {cat_name} ({cat_key}): {count}")


def main():
    """主函数 / Main function"""
    if len(sys.argv) < 2:
        print("Usage: python validate_actions_config.py <config_file.json>")
        print("\nExample:")
        print("  python scripts/validate_actions_config.py config/game_actions.json")
        sys.exit(1)
        
    config_path = sys.argv[1]
    validator = ConfigValidator(config_path)
    
    success = validator.validate()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
