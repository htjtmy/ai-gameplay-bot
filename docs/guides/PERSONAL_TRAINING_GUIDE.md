# 使用自己录制的视频训练 AI 模型 - 完整指南

## 概述

这个指南将帮助你使用自己录制的游戏视频和实时操作来训练 AI 模型。

### 工作流程

```
1. 录制视频 + 操作
   ↓
2. 提取帧 + 映射操作
   ↓
3. 生成训练数据集
   ↓
4. 训练 Transformer 模型
   ↓
5. 部署服务
```

---

## 第一步：安装依赖

```bash
# 用于屏幕录制和输入监听
pip install pynput mss

# 或者通过 requirements 安装所有依赖
pip install -r requirements.txt
```

---

## 第二步：录制你的游戏操作

### 方式 1：自动录制（推荐）

自动记录屏幕视频和键盘、鼠标操作：

```bash
python scripts/gameplay_recorder.py
```

**选项参数：**

```bash
# 自定义输出目录
python scripts/gameplay_recorder.py --output my_recordings

# 自定义会话名称（默认为时间戳）
python scripts/gameplay_recorder.py --session my_gameplay_001

# 自定义屏幕录制区域 (x, y, width, height)
python scripts/gameplay_recorder.py --screen 0 0 1920 1080

# 组合使用
python scripts/gameplay_recorder.py --output my_recordings --session session_001 --screen 0 0 1920 1080
```

**操作说明：**
- 脚本启动后开始录制
- 按 **Q** 或 **Ctrl+C** 停止录制
- 所有键盘和鼠标操作都会被记录
- 输出结构：
  ```
  data/raw/gameplay_videos/
  └── 20250125_120000/          # 时间戳或自定义名称
      ├── gameplay.mp4          # 录制的视频
      ├── inputs.jsonl          # 所有输入事件（JSON Lines格式）
      └── metadata.json         # 录制元数据
  ```

### 方式 2：手动录制

如果你想使用现有的视频文件：

1. 将视频放到 `data/raw/gameplay_videos/` 目录
2. 手动创建对应的 `inputs.jsonl` 文件（可选）
3. 继续第三步

---

## 第三步：处理录制的数据

将录制的视频和操作转换为训练数据集：

```bash
python scripts/process_gameplay_recording.py --session data/raw/gameplay_videos/20250125_120000
```

**参数选项：**

```bash
# 跳帧（每2帧提取1帧）
python scripts/process_gameplay_recording.py --session ... --skip 2

# 自定义输出目录
python scripts/process_gameplay_recording.py --session ... --output my_datasets
```

**处理过程：**

1. **提取视频帧** - 从视频中逐帧提取（默认1 FPS）
2. **映射操作** - 关联每一帧对应的游戏操作
3. **生成标注** - 创建 `actions.txt` 文件
4. **提取特征** - 从每帧提取 128 维特征向量
5. **创建数据集** - 生成 CSV 训练数据

**输出文件：**

```
data/processed/
├── frames_20250125_120000/          # 提取的视频帧
│   ├── frame_000000.jpg
│   ├── frame_000001.jpg
│   └── ...
├── actions_20250125_120000.txt      # 操作标注（每行一个动作）
├── dataset_20250125_120000.csv      # 训练数据集
└── mapping_20250125_120000.json     # 帧-操作映射
```

---

## 第四步：训练模型

### 选项 1：使用新数据集训练

编辑 `models/transformer/transformer_training.py`，更改数据集路径：

```python
# 改这一行：
DATASET_PATH = "data/processed/dataset_20250125_120000.csv"
```

然后运行训练：

```bash
python models/transformer/transformer_training.py
```

### 选项 2：快速测试

使用 Makefile 命令：

```bash
make train-transformer
```

**训练配置（可修改）：**

```python
BATCH_SIZE = 16          # 批次大小
NUM_EPOCHS = 30          # 训练轮数
LEARNING_RATE = 0.0001   # 学习率
SEQUENCE_LENGTH = 10     # 序列长度
NUM_HEADS = 4            # 注意力头数
NUM_LAYERS = 3           # Transformer层数
```

**监控训练进度：**

- 损失函数会逐步下降
- 验证精度会逐步提升
- 最好的模型会自动保存

---

## 第五步：部署服务

### 启动部署后端

```bash
python deployment/control_backend.py
```

服务启动后：
- **控制后端** 监听 `http://localhost:8000`
- **Transformer 模型** 监听 `http://localhost:5001`

### 使用 Web 界面

打开浏览器访问：
```
http://localhost:8000
```

### API 调用

```bash
# 获取实时预测
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -d '{"frame": "base64_encoded_image"}'

# 检查健康状态
curl http://localhost:5001/health
```

---

## 工作流程示例

完整的从录制到部署的命令序列：

```bash
# 1. 记录时间戳
export SESSION_ID=$(date +"%Y%m%d_%H%M%S")

# 2. 录制游戏（按 Q 停止）
python scripts/gameplay_recorder.py --session $SESSION_ID

# 3. 处理录制数据
python scripts/process_gameplay_recording.py --session data/raw/gameplay_videos/$SESSION_ID

# 4. 更新训练脚本
sed -i "s|DATASET_PATH = .*|DATASET_PATH = \"data/processed/dataset_${SESSION_ID}.csv\"|" \
  models/transformer/transformer_training.py

# 5. 训练模型
python models/transformer/transformer_training.py

# 6. 部署服务
python deployment/control_backend.py
```

---

## 支持的游戏操作

系统自动识别以下操作：

### 移动
- `w` → move_forward
- `a` → move_left
- `s` → move_backward
- `d` → move_right

### 转向
- `q` → turn_left
- `e` → turn_right
- `←/→` → turn_left/right

### 战斗
- 左键点击 → melee_attack
- 右键点击 → ranged_attack
- `c` → combat_skill
- `x` → ultimate_skill
- `r` → reload
- `space` → jump
- `shift` → dodge
- `ctrl` → slide

### 交互
- `f` → interact
- `i` → inventory
- `m` → map
- `p` → menu
- `l` → lock_target
- `t` → geniemon
- `q` (长按) → revive

### 相机/视角
- 鼠标移动 → look_x, look_y

---

## 常见问题

### Q: 录制时屏幕黑屏怎么办？

**A:** 检查屏幕区域参数：
```bash
python scripts/gameplay_recorder.py --screen 0 0 1920 1080
```

调整为你的实际分辨率。

### Q: 操作没有被记录

**A:** 确保：
1. 命令行窗口不在前台
2. 按的键在支持列表中
3. 检查 `inputs.jsonl` 文件是否有内容

### Q: 训练很慢

**A:** 
- 跳帧处理：`--skip 2` 或 `--skip 5`
- 减少序列长度：`SEQUENCE_LENGTH = 5`
- 使用 GPU：确保 CUDA 可用

### Q: 如何修改操作映射？

**A:** 编辑 `scripts/process_gameplay_recording.py` 中的 `INPUT_TO_ACTION_MAP`：

```python
INPUT_TO_ACTION_MAP = {
    'w': 'move_forward',
    'your_key': 'your_action',
    ...
}
```

---

## 数据增强（可选）

录制数据量较少时，可用生成式 AI 增强：

```bash
python scripts/generative_ai_enrichment.py
```

这会生成合成数据增加训练集大小。

---

## 目录结构

```
Ai-Gameplay-Bot/
├── scripts/
│   ├── gameplay_recorder.py              # 录制脚本
│   ├── process_gameplay_recording.py     # 处理脚本
│   ├── video_processing.py               # 视频处理
│   ├── dataset_builder.py                # 数据集构建
│   └── ...
├── models/
│   └── transformer/
│       ├── transformer_training.py       # 训练脚本
│       ├── transformer_model.py          # 模型定义
│       └── transformer_finetune.py       # 微调脚本
├── deployment/
│   ├── control_backend.py                # 部署后端
│   ├── deploy_transformer.py             # Transformer 服务
│   ├── real_time_controller.py           # 实时控制器
│   └── ...
└── data/
    ├── raw/
    │   ├── gameplay_videos/              # 录制的视频
    │   └── annotations/                  # 手动标注
    └── processed/
        ├── frames_*/                     # 提取的帧
        ├── dataset_*.csv                 # 训练数据集
        └── ...
```

---

## 下一步

1. **微调模型** - 使用 `transformer_finetune.py` 优化特定任务
2. **评估性能** - 运行 `evaluation/real_time_tests.py` 测试
3. **收集用户反馈** - 使用 `evaluation/feedback_iteration.py` 改进
4. **扩展数据** - 录制更多游戏场景训练更鲁棒的模型

---

## 获取帮助

查看相关脚本的帮助信息：

```bash
python scripts/gameplay_recorder.py --help
python scripts/process_gameplay_recording.py --help
python models/transformer/transformer_training.py --help
```
