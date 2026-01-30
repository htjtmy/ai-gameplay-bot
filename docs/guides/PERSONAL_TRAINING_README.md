# 🎮 AI 游戏机器人 - 个人游戏训练模块

本文档说明如何使用自己录制的游戏视频和操作来训练 AI 模型。

## ✨ 新增功能

### 🎥 实时录制模块
- **自动录制** 屏幕视频和鼠标/键盘操作
- **同步记录** 所有输入事件的时间戳
- **灵活配置** 屏幕捐获区域和会话名称

### 🔄 数据处理管道
- **帧提取** 从视频中逐帧提取图像
- **操作映射** 将键盘/鼠标输入映射到游戏动作
- **特征提取** 从每帧生成 128 维特征向量
- **数据集生成** 自动创建 CSV 格式训练数据

### 🚀 一体化训练工具
- **快速开始** 一条命令完成整个流程
- **分步控制** 可独立运行录制/处理/训练/部署各阶段
- **自动更新** 自动更新训练配置指向正确的数据集

## 📋 快速开始

### 方式 1：一键启动（最简单）

```bash
python scripts/quick_start_training.py all
```

1. 自动启动屏幕录制
2. 按 **Q** 停止
3. 自动处理数据
4. 自动训练模型
5. 完成！

### 方式 2：分步运行（更灵活）

```bash
# 1. 录制游戏（按 Q 停止）
python scripts/quick_start_training.py record --session my_game

# 2. 处理录制的数据
python scripts/quick_start_training.py process --session my_game

# 3. 训练模型
python scripts/quick_start_training.py train

# 4. 部署服务（可选）
python scripts/quick_start_training.py deploy
```

### 方式 3：直接调用脚本

```bash
# 录制
python scripts/gameplay_recorder.py --session my_game --screen 0 0 1920 1080

# 处理
python scripts/process_gameplay_recording.py --session data/raw/gameplay_videos/my_game

# 训练
python models/transformer/transformer_training.py
```

## 🎯 支持的游戏操作（27 个）

### 移动 (6)
- `move_forward` (W)
- `move_backward` (S)
- `move_left` (A)
- `move_right` (D)

### 转向 (2)
- `turn_left` (Q)
- `turn_right` (E)

### 战斗 (8)
- `melee_attack` (左键)
- `ranged_attack` (右键)
- `lock_target` (L)
- `combat_skill` (C)
- `ultimate_skill` (X)
- `jump` (Space)
- `dodge` (Shift)
- `slide` (Ctrl)

### 交互 (6)
- `interact` (F)
- `inventory` (I)
- `map` (M)
- `menu` (P)
- `geniemon` (T)
- `revive` (Q长按)

### 其他 (3)
- `reload` (R)
- `look_x` (鼠标水平移动)
- `look_y` (鼠标竖直移动)

## 📁 文件结构

```
Ai-Gameplay-Bot/
├── scripts/
│   ├── gameplay_recorder.py           # 📹 录制脚本
│   ├── process_gameplay_recording.py  # 🔄 处理脚本
│   └── quick_start_training.py        # 🚀 快速启动
│
├── PERSONAL_TRAINING_GUIDE.md         # 📚 完整指南
├── QUICK_START_PERSONAL.md            # ⚡ 快速参考
└── test_personal_training.py          # ✅ 功能验证
```

## 📊 工作流程

```
游戏操作录制
    ↓
    ├─ gameplay.mp4  (视频)
    └─ inputs.jsonl  (操作日志)
    ↓
数据处理 (frames + actions)
    ↓
    ├─ frames_*.jpg  (提取帧)
    ├─ actions.txt   (操作标注)
    └─ dataset.csv   (训练数据)
    ↓
模型训练 (Transformer)
    ↓
    └─ transformer_best.pth (训练完成)
    ↓
部署服务 & 使用
    ↓
    http://localhost:8000
```

## 🎮 使用场景

### 场景 1：训练特定游戏的自动化
```bash
# 录制你的游戏操作
python scripts/quick_start_training.py record

# AI 学习你的操作风格
python scripts/quick_start_training.py train

# 部署并自动化游戏
python scripts/quick_start_training.py deploy
```

### 场景 2：收集多个玩家的数据
```bash
# 玩家 1
python scripts/quick_start_training.py record --session player1

# 玩家 2
python scripts/quick_start_training.py record --session player2

# 合并数据训练
# (可编辑脚本合并多个数据集)
```

### 场景 3：迭代改进
```bash
# 初始训练
python scripts/quick_start_training.py all

# 录制更多数据
python scripts/quick_start_training.py record --session round2

# 重新训练
python scripts/quick_start_training.py process --session data/raw/gameplay_videos/round2
python scripts/quick_start_training.py train
```

## 🔧 配置参数

### 录制参数
```bash
# 自定义会话名称
--session NAME

# 自定义屏幕捕获区域 (x y width height)
--screen 0 0 1920 1080

# 自定义输出目录
--output /path/to/recordings
```

### 处理参数
```bash
# 跳帧（加快处理）
--skip 2         # 每 2 帧取 1 帧
--skip 5         # 每 5 帧取 1 帧

# 自定义输出目录
--output /path/to/processed
```

### 训练参数

编辑 `models/transformer/transformer_training.py`：

```python
BATCH_SIZE = 16          # 批次大小
NUM_EPOCHS = 30          # 训练轮数
LEARNING_RATE = 0.0001   # 学习率
SEQUENCE_LENGTH = 10     # 序列长度（更长 = 更好的上下文）
NUM_HEADS = 4            # 注意力头数
NUM_LAYERS = 3           # Transformer 层数
```

## 💡 技巧与最佳实践

### 提高数据质量
1. **稳定的帧率** - 以恒定速度录制
2. **清晰的操作** - 明确的输入（避免连续点击）
3. **多样化数据** - 涵盖不同的游戏场景和操作

### 加快处理
```bash
# 使用跳帧
python scripts/quick_start_training.py process --latest --skip 2

# 减少 Transformer 参数
# 编辑 transformer_training.py
NUM_LAYERS = 2        # 减少层数
NUM_HEADS = 2         # 减少头数
SEQUENCE_LENGTH = 5   # 减少序列长度
```

### 扩展数据
```bash
# 使用生成式 AI 增强
python scripts/generative_ai_enrichment.py

# 录制更多数据
python scripts/quick_start_training.py record --session session2
```

## 📈 监控训练

训练时的输出显示：
```
Epoch 1/30
  Loss: 2.345
  Val Accuracy: 45.2%

Epoch 2/30
  Loss: 1.893
  Val Accuracy: 58.7%

...

Best model saved!
```

## 🔍 验证安装

检查所有依赖是否正确安装：

```bash
python test_personal_training.py
```

输出应该显示：
```
✓ 所有检查通过！
```

## 🆘 常见问题

| 问题 | 解决方案 |
|------|--------|
| 录制时屏幕黑屏 | 调整 `--screen` 参数为实际分辨率 |
| 操作未被记录 | 确保命令行窗口不在前台 |
| 模型训练很慢 | 使用 `--skip 2` 或减少 `NUM_LAYERS` |
| 显存不足 | 减少 `BATCH_SIZE` 参数 |
| 模型精度低 | 增加训练数据量或 `NUM_EPOCHS` |

## 📚 更详细的信息

- **完整指南** - 查看 [PERSONAL_TRAINING_GUIDE.md](PERSONAL_TRAINING_GUIDE.md)
- **快速参考** - 查看 [QUICK_START_PERSONAL.md](QUICK_START_PERSONAL.md)
- **脚本帮助** - `python scripts/quick_start_training.py --help`

## 🎓 技术细节

### 架构
- **模型** - Transformer (仅)
- **输入** - 128 维特征向量（从视频帧提取）
- **输出** - 27 个游戏动作之一
- **序列建模** - 考虑 10 帧的历史上下文

### 处理流程
1. **视频解码** - OpenCV 逐帧提取
2. **特征提取** - 灰度化 → 缩放 → 归一化
3. **时间对齐** - 将输入事件映射到最近的帧
4. **数据集创建** - 生成 CSV 格式的训练数据

## 📝 示例命令

```bash
# 一键完整流程
python scripts/quick_start_training.py all

# 只录制（1920x1080 分辨率）
python scripts/quick_start_training.py record --screen 0 0 1920 1080

# 处理最新的录制，跳帧加速
python scripts/quick_start_training.py process --latest --skip 2

# 仅训练
python scripts/quick_start_training.py train

# 部署服务
python scripts/quick_start_training.py deploy
```

## 🚀 下一步

1. ✅ 验证安装：`python test_personal_training.py`
2. 🎮 开始录制：`python scripts/quick_start_training.py all`
3. 📈 监控训练进度
4. 🌐 访问 http://localhost:8000 查看服务
5. 🔄 迭代改进（录制更多数据 → 重新训练）

---

**祝你训练成功！** 🎯

如有问题，请查阅详细指南或检查脚本帮助信息。
