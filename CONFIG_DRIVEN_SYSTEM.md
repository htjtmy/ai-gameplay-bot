# 配置驱动的动作映射系统 / Configuration-Driven Action Mapping System

## 🎮 概述 / Overview

本系统通过**配置文件**管理游戏动作映射，无需修改代码即可快速适配不同游戏的按键和动作系统。

This system manages game action mappings through **configuration files**, enabling quick adaptation to different games' key bindings and action systems without code changes.

---

## ✨ 核心特性 / Key Features

- ✅ **配置驱动** / Configuration-Driven: 所有动作定义集中在JSON配置文件
- ✅ **快速切换** / Quick Switching: 通过环境变量或代码参数切换不同游戏
- ✅ **自动同步** / Auto Synchronization: 所有模块从同一配置源读取，无需手动同步
- ✅ **动态生成** / Dynamic Generation: ActionType枚举和映射字典自动从配置生成
- ✅ **配置验证** / Config Validation: 内置验证工具检查配置正确性
- ✅ **向后兼容** / Backward Compatible: 保留旧代码的兼容性

---

## 📁 文件结构 / File Structure

```
config/
  ├── game_actions.json           # 主配置文件（鸣潮）
  ├── README.md                   # 配置文档
  └── GAME_SWITCHING_GUIDE.md     # 游戏切换指南

scripts/
  ├── input_mapping.py            # 动作映射模块（从配置加载）
  └── validate_actions_config.py  # 配置验证工具

deployment/
  └── deploy_transformer.py       # Transformer服务（从配置加载）

tests/
  ├── test_input_mapping.py       # 单元测试（从配置加载）
  └── test_config_loading.py      # 配置加载测试
```

---

## 🚀 快速开始 / Quick Start

### 1. 查看当前配置 / View Current Config

```bash
conda activate Ai-Gameplay-Bot
python scripts/validate_actions_config.py config/game_actions.json
```

**输出 / Output:**
```
✅ 验证成功！配置文件格式正确
  • 游戏 / Game: 鸣潮 / Wuthering Waves
  • 动作总数 / Total Actions: 22
  • 分类总数 / Total Categories: 6
```

### 2. 为新游戏创建配置 / Create Config for New Game

```bash
# 复制模板
cp config/game_actions.json config/game_actions_your_game.json

# 编辑配置
code config/game_actions_your_game.json
```

**修改内容 / Modify:**
- `game_name`: 游戏名称
- `actions`: 添加/删除/修改动作
- 确保 `id` 从0开始连续

### 3. 验证新配置 / Validate New Config

```bash
python scripts/validate_actions_config.py config/game_actions_your_game.json
```

### 4. 使用新配置 / Use New Config

#### 方法A：环境变量 / Method A: Environment Variable

```powershell
# Windows PowerShell
$env:GAME_ACTIONS_CONFIG = "config/game_actions_your_game.json"
python deployment/deploy_transformer.py
```

```bash
# Linux/macOS
export GAME_ACTIONS_CONFIG="config/game_actions_your_game.json"
python deployment/deploy_transformer.py
```

#### 方法B：代码中指定 / Method B: In Code

```python
from scripts.input_mapping import get_action_mapper

# 加载指定配置
mapper = get_action_mapper("config/game_actions_your_game.json")
mapper.execute_action("JUMP")
```

---

## 📝 配置文件格式 / Config File Format

### 基本结构 / Basic Structure

```json
{
  "game_name": "游戏名称 / Game Name",
  "game_version": "版本号 / Version",
  "description": "描述 / Description",
  "actions": [
    {
      "id": 0,
      "name": "ACTION_NAME",
      "display_name_zh": "中文名",
      "display_name_en": "English Name",
      "category": "category_key",
      "keys": ["key"],
      "gamepad": "BUTTON",
      "description": "描述"
    }
  ],
  "categories": {
    "category_key": {
      "name_zh": "分类中文名",
      "name_en": "Category English Name",
      "description": "分类描述"
    }
  }
}
```

### 按键格式 / Key Formats

```json
// 普通按键 / Normal keys
"keys": ["w"]
"keys": ["space"]
"keys": ["esc"]

// 鼠标操作 / Mouse operations
"keys": [["mouse", "left"]]
"keys": [["mouse", "right"]]
"keys": [["mouse", "middle"]]
"keys": [["mouse", "motion_x"]]
"keys": [["mouse", "motion_y"]]

// 修饰键 / Modifier keys
"keys": [["control", "ctrl_l"]]
"keys": [["shift", "shift_l"]]
```

---

## 🛠️ API 使用 / API Usage

### 加载配置 / Load Configuration

```python
from scripts.input_mapping import load_actions_config

# 加载默认配置
config = load_actions_config()

# 加载指定配置
config = load_actions_config("config/game_actions_genshin.json")

# 通过环境变量加载
os.environ["GAME_ACTIONS_CONFIG"] = "config/game_actions_your_game.json"
config = load_actions_config()
```

### 获取动作映射器 / Get Action Mapper

```python
from scripts.input_mapping import get_action_mapper, reload_action_mapper

# 获取全局单例（首次调用时创建）
mapper = get_action_mapper()

# 指定配置文件
mapper = get_action_mapper("config/game_actions_genshin.json")

# 切换配置（重新加载）
mapper = reload_action_mapper("config/game_actions_starrail.json")
```

### 执行动作 / Execute Actions

```python
# 执行动作（按名称）
mapper.execute_action("JUMP")
mapper.execute_action("MELEE_ATTACK", duration=0.2)

# 根据ID获取动作名称
action_id = 5
action_name = mapper.get_action_name_by_id(action_id)
if action_name:
    mapper.execute_action(action_name)
```

### 查询动作信息 / Query Action Info

```python
# 获取动作详细信息
info = mapper.get_action_info("JUMP")
print(f"中文名: {info['display_name_zh']}")
print(f"英文名: {info['display_name_en']}")
print(f"分类: {info['category']}")
print(f"按键: {info['keys']}")
print(f"描述: {info['description']}")

# 获取动作总数
count = mapper.get_action_count()
print(f"动作总数: {count}")
```

### 使用 ActionType 枚举 / Use ActionType Enum

```python
from scripts.input_mapping import ActionType

# ActionType 自动从配置生成
print(ActionType.MOVE_FORWARD)  # <ActionType.MOVE_FORWARD: 'MOVE_FORWARD'>
print(ActionType.JUMP.value)    # "JUMP"

# 遍历所有动作
for action in ActionType:
    print(action.name, action.value)
```

---

## 🔧 模块集成 / Module Integration

### Transformer 部署服务 / Transformer Deployment

[deploy_transformer.py](deployment/deploy_transformer.py) 自动从配置加载：

```python
# 自动从配置加载动作映射
ACTION_MAPPING = load_action_mapping_from_config()
OUTPUT_SIZE = len(ACTION_MAPPING)  # 输出类别数自动匹配

# Flask端点返回动作名称
action_name = ACTION_MAPPING.get(predicted_id, "UNKNOWN")
```

### 游戏录制 / Gameplay Recording

[gameplay_recorder.py](scripts/gameplay_recorder.py) 使用配置：

```python
from input_mapping import get_action_mapper

mapper = get_action_mapper()
# 录制时使用最新配置的动作
```

### 实时控制 / Real-time Control

```python
from scripts.input_mapping import get_action_mapper

mapper = get_action_mapper()

# 模型预测
action_id = model.predict(frame)

# 执行动作
action_name = mapper.get_action_name_by_id(action_id)
if action_name:
    mapper.execute_action(action_name)
```

---

## 📚 更多文档 / More Documentation

- **配置详细说明**: [config/README.md](config/README.md)
- **游戏切换指南**: [config/GAME_SWITCHING_GUIDE.md](config/GAME_SWITCHING_GUIDE.md)
- **配置验证工具**: `python scripts/validate_actions_config.py --help`

---

## 🎯 使用场景 / Use Cases

### 场景1：添加新动作

1. 编辑 `config/game_actions.json`
2. 在 `actions` 数组末尾添加新动作
3. 设置 `id` 为当前最大ID + 1
4. 验证配置：`python scripts/validate_actions_config.py config/game_actions.json`
5. 重启服务或调用 `reload_action_mapper()`

### 场景2：修改按键

1. 在配置文件中找到对应动作
2. 修改 `keys` 字段
3. 验证配置
4. 重启服务

### 场景3：切换游戏

1. 创建新游戏配置文件
2. 设置环境变量：`$env:GAME_ACTIONS_CONFIG = "config/game_actions_new_game.json"`
3. 启动服务或录制工具

### 场景4：减少动作数量

1. 从配置文件删除不需要的动作
2. **重新编号所有后续动作的 `id`** 确保连续（重要！）
3. 验证配置
4. 重新训练模型以匹配新的动作数量

---

## ⚠️ 注意事项 / Important Notes

1. **ID 必须连续**: 动作ID必须从0开始，连续递增：0, 1, 2, 3, ...
2. **模型匹配**: 修改动作数量后，需要重新训练模型以匹配新的 `OUTPUT_SIZE`
3. **重启服务**: 修改配置后需要重启相关服务才能生效
4. **验证配置**: 每次修改后运行验证工具确保格式正确
5. **备份配置**: 修改前备份原配置文件

---

## 🐛 故障排除 / Troubleshooting

### 问题1：配置文件不存在

```
❌ 配置文件不存在 / Config file not found: config/game_actions.json
```

**解决方案**: 检查文件路径，确保配置文件存在且路径正确。

### 问题2：动作数量不匹配

```
Error: Model expects 22 actions but config has 25
```

**解决方案**: 
1. 检查配置文件中的动作数量
2. 更新模型的 `OUTPUT_SIZE` 或调整配置动作数量
3. 重新训练模型

### 问题3：ID不连续

```
❌ 动作ID不连续，缺少 / Action IDs not sequential, missing: [5, 8]
```

**解决方案**: 检查配置文件，确保所有动作ID从0开始连续。删除动作后需要重新编号。

### 问题4：按键格式错误

```
❌ 动作 'JUMP' 的按键格式无效 / Action 'JUMP' invalid key format
```

**解决方案**: 
- 单个按键使用字符串：`"keys": ["w"]`
- 复合按键使用数组：`"keys": [["mouse", "left"]]`

---

## 📊 测试 / Testing

### 验证配置文件

```bash
python scripts/validate_actions_config.py config/game_actions.json
```

### 测试配置加载

```bash
python tests/test_config_loading.py
```

### 运行单元测试

```bash
pytest tests/test_input_mapping.py -v
```

---

## 🎉 总结 / Summary

通过配置驱动的架构，您现在可以：

- ✅ 无需修改代码，仅编辑JSON配置即可切换游戏
- ✅ 快速添加/删除/修改动作映射
- ✅ 所有模块自动同步，无需手动更新多个文件
- ✅ 内置验证工具确保配置正确性
- ✅ 保持代码简洁，配置集中管理

**开始使用**: 查看 [config/GAME_SWITCHING_GUIDE.md](config/GAME_SWITCHING_GUIDE.md) 了解详细步骤！
