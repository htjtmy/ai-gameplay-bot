# 游戏动作配置 / Game Actions Configuration

## 概述 / Overview

此目录包含游戏动作映射的配置文件。通过修改配置文件，可以快速适配不同游戏的按键和动作系统。

This directory contains configuration files for game action mappings. By modifying the config files, you can quickly adapt to different games' key bindings and action systems.

## 文件说明 / Files

### `game_actions.json`
主配置文件，定义所有游戏动作、按键映射和分类信息。

Main configuration file defining all game actions, key mappings, and categories.

## 配置结构 / Configuration Structure

```json
{
  "game_name": "游戏名称",
  "game_version": "版本号",
  "description": "配置描述",
  "actions": [
    {
      "id": 0,                          // 动作索引（必须从0开始连续）
      "name": "ACTION_NAME",            // 动作名称（大写+下划线）
      "display_name_zh": "中文名",      // 中文显示名称
      "display_name_en": "English Name", // 英文显示名称
      "category": "category_key",       // 分类标识
      "keys": ["key"],                  // 按键列表
      "gamepad": "BUTTON",              // 手柄按键
      "description": "描述"             // 动作描述
    }
  ],
  "categories": {
    "category_key": {
      "name_zh": "中文分类名",
      "name_en": "English Category",
      "description": "分类描述"
    }
  }
}
```

## 按键格式 / Key Format

### 键盘按键 / Keyboard Keys
```json
"keys": ["w"]                    // 单个按键
"keys": ["space"]                // 特殊键名
"keys": ["esc"]                  // ESC键
```

### 鼠标操作 / Mouse Operations
```json
"keys": [["mouse", "left"]]      // 鼠标左键
"keys": [["mouse", "right"]]     // 鼠标右键
"keys": [["mouse", "middle"]]    // 鼠标中键
"keys": [["mouse", "motion_x"]]  // 鼠标X轴移动
"keys": [["mouse", "motion_y"]]  // 鼠标Y轴移动
```

### 组合键 / Key Combinations
```json
"keys": [["control", "ctrl_l"]]  // Ctrl键（使用control类型）
"keys": [["shift", "shift_l"]]   // Shift键（使用shift类型）
```

## 快速开始 / Quick Start

### 1. 为新游戏创建配置 / Create Config for New Game

```bash
# 复制现有配置作为模板
cp config/game_actions.json config/game_actions_new_game.json

# 编辑新配置
code config/game_actions_new_game.json
```

### 2. 修改游戏信息 / Modify Game Info

```json
{
  "game_name": "原神 / Genshin Impact",
  "game_version": "4.0",
  "description": "原神游戏动作配置"
}
```

### 3. 调整动作列表 / Adjust Action List

#### 添加新动作 / Add New Action
```json
{
  "id": 22,
  "name": "GLIDE",
  "display_name_zh": "滑翔",
  "display_name_en": "Glide",
  "category": "movement_skill",
  "keys": ["x"],
  "gamepad": "LB+A",
  "description": "展开风之翼滑翔"
}
```

#### 删除动作 / Remove Action
直接删除对应的动作对象，然后重新调整所有后续动作的 `id` 确保连续。

Simply remove the action object, then renumber all subsequent action `id`s to ensure continuity.

#### 修改按键 / Modify Key Binding
```json
{
  "id": 10,
  "name": "JUMP",
  "keys": ["space"],  // 改为其他键，如 ["x"]
  // ...
}
```

### 4. 使用配置 / Use Configuration

```python
from scripts.input_mapping import load_actions_config, get_action_mapper

# 加载配置
config = load_actions_config("config/game_actions.json")

# 获取动作映射器
mapper = get_action_mapper("config/game_actions.json")

# 执行动作
mapper.execute_action("JUMP")
```

### 5. 切换游戏配置 / Switch Game Configuration

通过环境变量指定配置文件：

Specify config file via environment variable:

```bash
# Windows PowerShell
$env:GAME_ACTIONS_CONFIG = "config/game_actions_genshin.json"
python scripts/gameplay_recorder.py --process GenshinImpact.exe

# Linux/macOS
export GAME_ACTIONS_CONFIG="config/game_actions_genshin.json"
python scripts/gameplay_recorder.py --process genshin_impact
```

或在代码中直接指定 / Or specify directly in code:

```python
from scripts.input_mapping import get_action_mapper

mapper = get_action_mapper("config/game_actions_genshin.json")
```

## 配置验证 / Configuration Validation

运行验证脚本检查配置正确性：

Run validation script to check configuration correctness:

```bash
python scripts/validate_actions_config.py config/game_actions.json
```

验证项目包括 / Validation checks include:
- ✅ 动作ID连续性（0, 1, 2, ...）
- ✅ 动作名称唯一性
- ✅ 按键格式正确性
- ✅ 分类引用有效性
- ✅ 必填字段完整性

## 最佳实践 / Best Practices

1. **保持ID连续** / Keep IDs Sequential
   - 动作ID必须从0开始连续，模型输出依赖这个顺序
   - Action IDs must be sequential starting from 0, model output depends on this order

2. **命名规范** / Naming Convention
   - 动作名称使用大写+下划线：`MOVE_FORWARD`
   - Use uppercase with underscores: `MOVE_FORWARD`

3. **版本控制** / Version Control
   - 为不同游戏创建独立配置文件
   - 在文件名中包含游戏名：`game_actions_<game_name>.json`
   - Create separate config files for different games
   - Include game name in filename: `game_actions_<game_name>.json`

4. **文档化** / Documentation
   - 为每个动作添加清晰的中英文描述
   - 记录手柄映射以便多平台支持
   - Add clear bilingual descriptions for each action
   - Document gamepad mappings for multi-platform support

5. **向后兼容** / Backward Compatibility
   - 修改配置时保存旧版本
   - 考虑模型重训练的影响
   - Save old versions when modifying config
   - Consider impact on model retraining

## 示例配置 / Example Configurations

### 原神 / Genshin Impact
```bash
config/game_actions_genshin.json
```

### 崩坏：星穹铁道 / Honkai: Star Rail
```bash
config/game_actions_starrail.json
```

### 鸣潮 / Wuthering Waves (当前默认)
```bash
config/game_actions.json
```

## 故障排除 / Troubleshooting

### 问题：动作数量不匹配 / Issue: Action Count Mismatch
```
Error: Model expects 22 actions but config has 25
```

**解决方案 / Solution:**
1. 检查配置文件中的动作数量
2. 确认模型的 OUTPUT_SIZE 配置
3. 重新训练模型或调整配置以匹配

### 问题：按键无效 / Issue: Invalid Key
```
Error: Key 'mouse_left' not recognized
```

**解决方案 / Solution:**
使用正确的按键格式：`["mouse", "left"]` 而不是 `"mouse_left"`

Use correct key format: `["mouse", "left"]` instead of `"mouse_left"`

## 相关文件 / Related Files

- `scripts/input_mapping.py` - 动作映射加载和执行
- `scripts/validate_actions_config.py` - 配置验证工具
- `deployment/deploy_transformer.py` - 模型部署（使用配置）
- `tests/test_input_mapping.py` - 单元测试

## 更多帮助 / More Help

参考主项目文档：[../README.md](../README.md)

Refer to main project documentation: [../README.md](../README.md)
