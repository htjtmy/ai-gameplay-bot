# NO_ACTION 移除问题 - 修复方案

## 核心问题

移除 NO_ACTION 后，系统中有**5 个关键不一致问题**需要修复。

---

## 问题追踪

### 🔴 P0 优先级问题

#### P0-1: dataset_builder.py 默认动作错误

**现状**:
```python
# scripts/dataset_builder.py, 第 78 行
return action_mapping.get(action_str.lower().strip(), 0)
```

**问题**: 未知动作默认映射为 0 (MOVE_FORWARD)，导致训练数据污染

**修复方案**:
```python
def map_action_to_index(action_str):
    action_mapping = {
        # ... 26 个动作 ...
    }
    action = action_str.lower().strip()
    if action not in action_mapping:
        logger.warning(f"Unknown action: {action_str}, skipping this sample")
        return None  # 返回 None，由上层决定处理方式
    return action_mapping[action]
```

**建议**: 改为 **返回 None 或抛出异常**，让上层显式处理

---

#### P0-2: stream_sessions.py ACTION_TO_INDEX 严重不匹配

**现状** (第 34-45 行):
```python
ACTION_TO_INDEX = {
    "move_forward": 0,
    "move_backward": 1,
    ...
    "use_item": 7,
    "open_inventory": 8,
    "cast_spell": 9,  # 只有 10 个动作！
}
```

**问题**: 
- 只定义了 10 个动作，但模型输出 27 个类
- 动作名称与 config.py 完全不同
- 无法处理超过 9 的动作索引

**修复方案A - 同步 ACTION_TO_INDEX**:
```python
# deployment/stream_sessions.py
from config import ACTION_MAPPING, ACTION_NAME_TO_INDEX

ACTION_TO_INDEX = ACTION_NAME_TO_INDEX  # 直接使用 config 中的映射
```

**修复方案B - 创建新的映射**:
```python
ACTION_TO_INDEX = {
    "move_forward": 0,
    "move_backward": 1,
    "turn_left": 2,
    "turn_right": 3,
    "melee_attack": 4,
    "ranged_attack": 5,
    "lock_target": 6,
    "combat_skill": 7,
    "ultimate_skill": 8,
    "jump": 9,
    "slide": 10,
    "dodge": 11,
    "helix_leap": 12,
    "reload": 13,
    "interact": 14,
    "inventory": 15,
    "map": 16,
    "combat": 17,
    "armoury": 18,
    "revive": 19,
    "menu": 20,
    "geniemon": 21,
    "navigate": 22,
    "quests": 23,
    "quit_challenge": 24,
    "look_x": 25,
    "look_y": 26,
}
```

**建议**: 选择**方案A**，从 config.py 导入以保证一致性

---

### 🟠 P1 中等优先级问题

#### P1-1: 未知动作的降级处理

**现状** (第 141 行):
```python
action = data.get("action") or "unknown_action"
```

**问题**: "unknown_action" 不在任何映射中

**修复方案**:
```python
action = data.get("action") or "move_forward"  # 或其他默认有效动作

# 或者添加验证
if action not in ACTION_TO_INDEX and action not in ACTION_MAPPING.values():
    logger.warning(f"Unknown action: {action}, using default: move_forward")
    action = "move_forward"
```

---

#### P1-2: 模型推理时的越界保护

**文件**: `deployment/deploy_transformer.py` (第 189 行)

**现状**:
```python
"action": ACTION_MAPPING.get(action_idx, "UNKNOWN_ACTION"),
```

**改进**:
```python
if 0 <= action_idx < len(ACTION_MAPPING):
    action = ACTION_MAPPING[action_idx]
else:
    logger.error(f"Action index out of bounds: {action_idx}")
    action = ACTION_MAPPING[0]  # 安全的默认值

result = {
    "action": action,
    "action_index": action_idx,
    "confidence": confidence,
}
```

---

#### P1-3: config.py 数据验证

**文件**: `config.py` (第 62-93 行)

**添加验证函数**:
```python
def validate_action_mapping():
    """验证 ACTION_MAPPING 的一致性"""
    # 检查索引连续性
    indices = sorted(ACTION_MAPPING.keys())
    expected = list(range(len(ACTION_MAPPING)))
    assert indices == expected, f"Action indices not continuous: {indices}"
    
    # 检查重复值
    values = list(ACTION_MAPPING.values())
    assert len(values) == len(set(values)), "Duplicate action names"
    
    # 检查反向映射
    reverse = ACTION_NAME_TO_INDEX
    for idx, name in ACTION_MAPPING.items():
        assert reverse[name] == idx, f"Inconsistent mapping for {name}"
    
    print(f"✓ ACTION_MAPPING valid: {len(ACTION_MAPPING)} actions")

# 在模块导入时执行
validate_action_mapping()
```

---

## 修复步骤（优先级顺序）

### 第一步：统一 ACTION_TO_INDEX
```python
# deployment/stream_sessions.py
# 在文件顶部添加
from config import ACTION_MAPPING, ACTION_NAME_TO_INDEX

# 删除旧的 ACTION_TO_INDEX = { ... }
# 使用：
ACTION_TO_INDEX = ACTION_NAME_TO_INDEX
```

### 第二步：修复默认动作处理
```python
# scripts/dataset_builder.py
def map_action_to_index(action_str):
    action_mapping = {...}
    action = action_str.lower().strip()
    
    if action not in action_mapping:
        logger.error(f"Unknown action: '{action}'")
        raise ValueError(f"Unknown action: {action_str}")
    
    return action_mapping[action]
```

### 第三步：添加验证
```python
# config.py
validate_action_mapping()
```

### 第四步：安全的默认值处理
```python
# deployment/stream_sessions.py
action = data.get("action", "move_forward")  # 显式默认值
if action not in ACTION_TO_INDEX:
    logger.warning(f"Invalid action: {action}")
    action = "move_forward"
```

---

## 快速修复脚本

```bash
# 1. 检查数据集中的动作分布
python3 << 'EOF'
import pandas as pd
from collections import Counter

# 加载所有数据集
datasets = []
# ... 加载逻辑 ...

# 统计
all_actions = [action for dataset in datasets for action in dataset['action']]
counter = Counter(all_actions)
print("Action distribution:")
for action, count in counter.most_common():
    print(f"  {action}: {count}")

# 检查未知动作
known_actions = set(config.ACTION_MAPPING.values())
unknown = set(all_actions) - known_actions
if unknown:
    print(f"\n⚠️  Unknown actions found: {unknown}")
EOF

# 2. 验证模型输出层
python3 << 'EOF'
from models.transformer.transformer_model import GameplayTransformer
from config import OUTPUT_SIZE

model = GameplayTransformer(
    input_size=128,
    num_heads=4,
    hidden_size=64,
    num_layers=2,
    output_size=OUTPUT_SIZE
)

print(f"Model output layer size: {model.fc.out_features}")
print(f"Expected ACTION_MAPPING size: {len(config.ACTION_MAPPING)}")
assert model.fc.out_features == len(config.ACTION_MAPPING), "Size mismatch!"
print("✓ Model configuration consistent")
EOF

# 3. 检查映射一致性
python3 << 'EOF'
from config import ACTION_MAPPING, ACTION_NAME_TO_INDEX
from deployment.stream_sessions import ACTION_TO_INDEX

print(f"config.ACTION_MAPPING: {len(ACTION_MAPPING)} actions")
print(f"config.ACTION_NAME_TO_INDEX: {len(ACTION_NAME_TO_INDEX)} actions")
print(f"stream_sessions.ACTION_TO_INDEX: {len(ACTION_TO_INDEX)} actions")

# 检查是否一致
assert ACTION_NAME_TO_INDEX == ACTION_TO_INDEX, "Mapping mismatch!"
print("✓ All mappings consistent")
EOF
```

---

## 风险清单

- [ ] **数据集兼容性**: 检查旧数据是否包含 NO_ACTION
- [ ] **模型版本**: 确认现有模型是为 27 类还是 28 类训练的
- [ ] **流式处理**: 验证 stream_sessions.py 能否正确处理所有 27 个动作
- [ ] **测试用例**: 更新所有单元测试中的 ACTION_MAPPING 假设
- [ ] **导出/导入**: 检查模型保存时是否记录了 ACTION_MAPPING 版本

---

## 一键修复方案

**如果要快速修复，按以下顺序执行**:

1. ✅ 更新 `stream_sessions.py` 的 ACTION_TO_INDEX
2. ✅ 修改 `dataset_builder.py` 的默认动作处理
3. ✅ 在 `config.py` 添加验证函数
4. ✅ 运行验证脚本确认一致性
5. ✅ 运行现有测试确保兼容性

---

## 补充：是否考虑恢复 NO_ACTION？

| 方案 | 优点 | 缺点 |
|------|------|------|
| **保持 27 类** | 减少模型复杂度 | ⚠️ 需要解决默认值问题 |
| **恢复为 28 类** | ✅ 语义清晰，兼容旧数据 | ⚠️ 需要重新训练 |

**建议**: 如果没有大量旧数据依赖，保持 27 类即可。但务必**解决上述 5 个关键问题**。
