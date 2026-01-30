# 游戏动作映射快速切换指南 / Quick Game Switching Guide

本文档演示如何为不同游戏快速创建和切换动作配置。

This document demonstrates how to quickly create and switch action configurations for different games.

---

## 场景1：为原神创建新配置 / Scenario 1: Create Config for Genshin Impact

### 步骤 / Steps

1. **复制现有配置作为模板** / Copy existing config as template

```bash
# 复制鸣潮配置
cp config/game_actions.json config/game_actions_genshin.json
```

2. **修改游戏基本信息** / Modify game basic info

打开 `config/game_actions_genshin.json`，修改：

```json
{
  "game_name": "原神 / Genshin Impact",
  "game_version": "4.0",
  "description": "原神游戏动作配置"
}
```

3. **调整动作列表** / Adjust action list

原神可能需要添加/删除/修改某些动作：

#### 添加新动作：滑翔 / Add new action: Glide

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

#### 删除动作：螺旋飞跃 / Remove action: Helix Leap

找到 `HELIX_LEAP` 动作，删除整个对象。然后重新编号所有后续动作的 `id`。

#### 修改按键：原神用空格键冲刺 / Modify key: Genshin uses space for sprint

```json
{
  "id": 11,
  "name": "SLIDE",
  "display_name_zh": "冲刺",
  "display_name_en": "Sprint",
  "category": "movement_skill",
  "keys": [["shift", "shift_l"]],  // 原来是ctrl，改为shift
  "gamepad": "RB",
  "description": "冲刺移动"
}
```

4. **验证配置** / Validate config

```bash
conda activate Ai-Gameplay-Bot
python scripts/validate_actions_config.py config/game_actions_genshin.json
```

5. **使用新配置启动** / Launch with new config

```bash
# 方式1：环境变量 / Method 1: Environment variable
$env:GAME_ACTIONS_CONFIG = "config/game_actions_genshin.json"
python scripts/gameplay_recorder.py --process GenshinImpact.exe

# 方式2：在代码中指定 / Method 2: Specify in code
# 见下方Python示例
```

---

## 场景2：切换游戏配置 / Scenario 2: Switch Game Configuration

### 方法A：环境变量 / Method A: Environment Variable

**Windows PowerShell:**
```powershell
# 设置配置文件
$env:GAME_ACTIONS_CONFIG = "config/game_actions_genshin.json"

# 启动服务
python deployment/deploy_transformer.py

# 或录制
python scripts/gameplay_recorder.py --process GenshinImpact.exe
```

**Linux/macOS:**
```bash
# 设置配置文件
export GAME_ACTIONS_CONFIG="config/game_actions_genshin.json"

# 启动服务
python deployment/deploy_transformer.py
```

### 方法B：代码中指定 / Method B: Specify in Code

```python
from scripts.input_mapping import get_action_mapper, reload_action_mapper

# 首次加载
mapper = get_action_mapper("config/game_actions_genshin.json")
mapper.execute_action("GLIDE")

# 切换到另一个游戏
mapper = reload_action_mapper("config/game_actions_starrail.json")
mapper.execute_action("ULTIMATE_SKILL")
```

---

## 场景3：原神完整配置示例 / Scenario 3: Complete Genshin Config Example

参考 `config/game_actions_genshin.json`（需手动创建）：

```json
{
  "game_name": "原神 / Genshin Impact",
  "game_version": "4.0",
  "description": "原神游戏动作配置",
  "actions": [
    {"id": 0, "name": "MOVE_FORWARD", "display_name_zh": "前进", "display_name_en": "Move Forward", "category": "movement", "keys": ["w"], "gamepad": "LS_UP"},
    {"id": 1, "name": "MOVE_BACKWARD", "display_name_zh": "后退", "display_name_en": "Move Backward", "category": "movement", "keys": ["s"], "gamepad": "LS_DOWN"},
    {"id": 2, "name": "MOVE_LEFT", "display_name_zh": "左移", "display_name_en": "Move Left", "category": "movement", "keys": ["a"], "gamepad": "LS_LEFT"},
    {"id": 3, "name": "MOVE_RIGHT", "display_name_zh": "右移", "display_name_en": "Move Right", "category": "movement", "keys": ["d"], "gamepad": "LS_RIGHT"},
    {"id": 4, "name": "NORMAL_ATTACK", "display_name_zh": "普通攻击", "display_name_en": "Normal Attack", "category": "combat", "keys": [["mouse", "left"]], "gamepad": "X"},
    {"id": 5, "name": "CHARGED_ATTACK", "display_name_zh": "重击", "display_name_en": "Charged Attack", "category": "combat", "keys": [["mouse", "right"]], "gamepad": "RT"},
    {"id": 6, "name": "ELEMENTAL_SKILL", "display_name_zh": "元素战技", "display_name_en": "Elemental Skill", "category": "combat", "keys": ["e"], "gamepad": "RB"},
    {"id": 7, "name": "ELEMENTAL_BURST", "display_name_zh": "元素爆发", "display_name_en": "Elemental Burst", "category": "combat", "keys": ["q"], "gamepad": "LB"},
    {"id": 8, "name": "JUMP", "display_name_zh": "跳跃", "display_name_en": "Jump", "category": "movement_skill", "keys": ["space"], "gamepad": "A"},
    {"id": 9, "name": "SPRINT", "display_name_zh": "冲刺", "display_name_en": "Sprint", "category": "movement_skill", "keys": [["shift", "shift_l"]], "gamepad": "RB"},
    {"id": 10, "name": "GLIDE", "display_name_zh": "滑翔", "display_name_en": "Glide", "category": "movement_skill", "keys": ["x"], "gamepad": "LB+A"},
    {"id": 11, "name": "CLIMB", "display_name_zh": "攀爬", "display_name_en": "Climb", "category": "movement_skill", "keys": ["space"], "gamepad": "A"},
    {"id": 12, "name": "INTERACT", "display_name_zh": "互动", "display_name_en": "Interact", "category": "interaction", "keys": ["f"], "gamepad": "Y"},
    {"id": 13, "name": "MAP", "display_name_zh": "地图", "display_name_en": "Map", "category": "ui", "keys": ["m"], "gamepad": "VIEW"},
    {"id": 14, "name": "BAG", "display_name_zh": "背包", "display_name_en": "Bag", "category": "ui", "keys": ["b"], "gamepad": "DPAD_LEFT"},
    {"id": 15, "name": "CHARACTER", "display_name_zh": "角色", "display_name_en": "Character", "category": "ui", "keys": ["c"], "gamepad": "DPAD_UP"},
    {"id": 16, "name": "PARTY", "display_name_zh": "队伍", "display_name_en": "Party", "category": "ui", "keys": ["l"], "gamepad": "DPAD_RIGHT"},
    {"id": 17, "name": "MENU", "display_name_zh": "菜单", "display_name_en": "Menu", "category": "ui", "keys": ["esc"], "gamepad": "MENU"},
    {"id": 18, "name": "SWITCH_CHAR_1", "display_name_zh": "切换角色1", "display_name_en": "Switch Character 1", "category": "combat", "keys": ["1"], "gamepad": "DPAD_UP"},
    {"id": 19, "name": "SWITCH_CHAR_2", "display_name_zh": "切换角色2", "display_name_en": "Switch Character 2", "category": "combat", "keys": ["2"], "gamepad": "DPAD_RIGHT"},
    {"id": 20, "name": "SWITCH_CHAR_3", "display_name_zh": "切换角色3", "display_name_en": "Switch Character 3", "category": "combat", "keys": ["3"], "gamepad": "DPAD_DOWN"},
    {"id": 21, "name": "SWITCH_CHAR_4", "display_name_zh": "切换角色4", "display_name_en": "Switch Character 4", "category": "combat", "keys": ["4"], "gamepad": "DPAD_LEFT"},
    {"id": 22, "name": "LOOK_X", "display_name_zh": "水平视角", "display_name_en": "Look Horizontal", "category": "camera", "keys": [["mouse", "motion_x"]], "gamepad": "RS_X"},
    {"id": 23, "name": "LOOK_Y", "display_name_zh": "垂直视角", "display_name_en": "Look Vertical", "category": "camera", "keys": [["mouse", "motion_y"]], "gamepad": "RS_Y"}
  ],
  "categories": {
    "movement": {"name_zh": "移动", "name_en": "Movement"},
    "combat": {"name_zh": "战斗", "name_en": "Combat"},
    "movement_skill": {"name_zh": "移动技能", "name_en": "Movement Skills"},
    "interaction": {"name_zh": "互动", "name_en": "Interaction"},
    "ui": {"name_zh": "界面", "name_en": "UI/Menu"},
    "camera": {"name_zh": "视角", "name_en": "Camera"}
  }
}
```

---

## 场景4：测试新配置 / Scenario 4: Test New Configuration

### 1. 验证配置格式 / Validate config format

```bash
python scripts/validate_actions_config.py config/game_actions_genshin.json
```

### 2. 测试动作映射加载 / Test action mapping loading

```python
from scripts.input_mapping import load_actions_config, ActionMapper

# 加载配置
config = load_actions_config("config/game_actions_genshin.json")
print(f"游戏：{config['game_name']}")
print(f"动作数量：{len(config['actions'])}")

# 创建映射器
mapper = ActionMapper(config_path="config/game_actions_genshin.json")
print(f"映射数量：{mapper.get_action_count()}")

# 查看动作信息
info = mapper.get_action_info("GLIDE")
print(f"动作：{info['display_name_zh']} - {info['description']}")
```

### 3. 测试按键执行 / Test key execution

```python
from scripts.input_mapping import get_action_mapper

mapper = get_action_mapper("config/game_actions_genshin.json")

# 模拟按键（注意：这会真实执行按键！）
# mapper.execute_action("GLIDE", duration=0.1)
# mapper.execute_action("ELEMENTAL_BURST")

print("✅ 按键测试完成")
```

---

## 场景5：在部署中使用 / Scenario 5: Use in Deployment

### Transformer 模型服务 / Transformer Model Service

```bash
# 启动时指定配置
$env:GAME_ACTIONS_CONFIG = "config/game_actions_genshin.json"
python deployment/deploy_transformer.py

# 模型会自动加载对应的动作映射
# The model will automatically load the corresponding action mapping
```

### 实时控制器 / Real-time Controller

```python
# deployment/real_time_controller.py 中使用
from scripts.input_mapping import get_action_mapper

# 加载指定游戏配置
mapper = get_action_mapper("config/game_actions_genshin.json")

# 执行预测的动作
action_id = model.predict(frame)
action_name = mapper.get_action_name_by_id(action_id)
mapper.execute_action(action_name)
```

---

## 常见问题 / FAQ

### Q1: 如何增加动作数量？

A: 在配置文件的 `actions` 数组中添加新动作对象，确保 `id` 连续。然后重新训练模型以匹配新的动作数量。

### Q2: 修改配置后需要重启服务吗？

A: 是的。配置在程序启动时加载，修改后需要重启相关服务。或者使用 `reload_action_mapper()` 函数在代码中重新加载。

### Q3: 可以同时支持多个游戏吗？

A: 可以！创建多个配置文件，通过环境变量或代码参数切换。每个游戏需要独立训练模型。

### Q4: 动作ID必须从0开始吗？

A: 是的。模型输出是基于0的索引，动作ID必须是连续的整数：0, 1, 2, 3, ...

### Q5: 可以用YAML格式吗？

A: 当前只支持JSON。如需YAML支持，需修改 `load_actions_config()` 函数添加YAML解析。

---

## 更多示例 / More Examples

查看 `config/README.md` 获取详细的配置文档和最佳实践。

See `config/README.md` for detailed configuration documentation and best practices.
