# 模型改进完整指南

本指南帮助你系统性地改进AI游戏机器人模型，解决当前的类别不平衡问题。

## 📊 当前问题分析

根据测试结果，模型存在严重的类别不平衡问题：

- **动作0（无动作）**: 16,881个样本 (98.7%) → 100%准确率 ✓
- **动作4（近战攻击）**: 73个样本 (0.4%) → 0%准确率 ✗
- **动作5（远程攻击）**: 149个样本 (0.9%) → 0%准确率 ✗

**根本原因**：模型学会了"总是预测无动作"来最大化准确率。

---

## 🎯 改进方案（按优先级）

### 方案1：数据增强 + 类别权重（推荐）

**优点**：快速实现，效果好
**时间**：1-2小时

#### 步骤：

1. **对战斗动作进行数据增强**
   ```bash
   conda activate Ai-Gameplay-Bot
   python scripts/augment_minority_classes.py \
     --input "data/processed/transformer_dataset.csv" \
     --output "data/processed/transformer_dataset_augmented.csv" \
     --target-actions 4 5 \
     --target-samples 1000
   ```

   这将为动作4和5各生成约1000个增强样本。

2. **使用类别权重训练**
   ```bash
   python models/transformer/transformer_training.py \
     --dataset "data/processed/transformer_dataset_augmented.csv" \
     --epochs 100 \
     --num-classes 25 \
     --use-class-weights \
     --early-stopping 15
   ```

   参数说明：
   - `--use-class-weights`：自动计算并应用类别权重
   - `--early-stopping 15`：如果15个epoch内验证损失不改善，自动停止

3. **测试新模型**
   ```bash
   python scripts/test_model.py \
     --model "models/transformer/transformer_model.pth" \
     --dataset "data/processed/transformer_dataset_test.csv" \
     --full-eval
   ```

   **期望结果**：
   - 动作4和5的准确率 >60%
   - 整体准确率可能降低到90-95%（这是正常的）

---

### 方案2：录制更多战斗场景（质量最佳）

**优点**：真实数据，泛化能力强
**时间**：4-8小时（取决于录制数量）

#### 步骤：

1. **专门录制战斗场景**

   创建专门的战斗session：
   ```bash
   python scripts/gameplay_recorder.py --session "combat_focused_melee"
   ```

   **录制策略**：
   - 专注于近战战斗场景（动作4）
   - 每个视频保持高频率使用攻击动作
   - 录制不同敌人、不同环境的战斗
   - **目标**：录制至少15-20个专注于战斗的视频

2. **录制远程攻击场景**
   ```bash
   python scripts/gameplay_recorder.py --session "combat_focused_ranged"
   ```

   **录制策略**：
   - 专注于远程攻击场景（动作5）
   - 录制至少10-15个视频

3. **处理新录制的视频**

   a. 生成标注：
   ```bash
   python scripts/annotate_gameplay.py \
     --recordings-dir "recordings" \
     --output-dir "data/raw/annotations"
   ```

   b. 提取帧并匹配标注：
   ```bash
   python scripts/prepare_training_data.py \
     --videos-dir "recordings" \
     --annotations-dir "data/raw/annotations" \
     --output-dir "data/processed" \
     --skip-frames 3
   ```

   c. 构建完整数据集：
   ```bash
   python scripts/build_transformer_dataset.py \
     --dataset-csv-dir "data/processed" \
     --output-csv "data/processed/transformer_dataset_full.csv" \
     --test-size 1000
   ```

4. **使用完整数据集训练**
   ```bash
   python models/transformer/transformer_training.py \
     --dataset "data/processed/transformer_dataset_full.csv" \
     --epochs 100 \
     --num-classes 25 \
     --use-class-weights \
     --early-stopping 15
   ```

---

### 方案3：组合方案（最佳效果）

结合录制新数据和数据增强：

1. 录制5-10个战斗视频
2. 处理视频生成数据集
3. 对战斗动作进行数据增强
4. 使用类别权重训练

---

## 📈 训练监控

### 训练过程中观察：

```
Epoch 1/100
Train Loss: 2.8543, Train Accuracy: 45.23%
Val Loss: 2.6234, Val Accuracy: 52.34%
✓ Model saved (best val_loss: 2.6234)

Epoch 2/100
Train Loss: 1.9234, Train Accuracy: 62.45%
Val Loss: 1.8123, Val Accuracy: 65.23%
✓ Model saved (best val_loss: 1.8123)

...

Epoch 45/100
Train Loss: 0.2341, Train Accuracy: 92.34%
Val Loss: 0.3421, Val Accuracy: 89.23%
No improvement (5/15)
```

### 好的训练迹象：

✓ 训练和验证损失都在下降
✓ 训练准确率在85-95%之间
✓ 验证准确率接近训练准确率（差距<5%）
✓ 早停在40-60个epoch触发

### 坏的训练迹象：

✗ 验证损失上升但训练损失下降（过拟合）
✗ 训练准确率98%+但验证准确率<80%（严重过拟合）
✗ 损失不下降（学习率太大或数据有问题）

---

## 🧪 模型评估标准

使用test_model.py评估时：

### 最低标准（可部署）：
- 动作0: >95%
- 动作4: >60%
- 动作5: >60%
- 其他常用动作: >70%

### 良好标准：
- 动作0: >98%
- 动作4: >75%
- 动作5: >75%
- 其他常用动作: >80%

### 优秀标准：
- 所有动作: >85%

---

## 🎮 实际游戏测试

训练完成后，在真实游戏中测试：

```bash
python scripts/real_time_controller.py \
  --model "models/transformer/transformer_model.pth" \
  --fps 10 \
  --confidence 0.6 \
  --duration 300 \
  --screen 0 0 1280 720
```

参数说明：
- `--fps 10`：每秒预测10次
- `--confidence 0.6`：置信度阈值60%（可根据表现调整）
- `--duration 300`：测试5分钟
- `--screen 0 0 1280 720`：捕获区域（根据游戏窗口调整）

### 观察指标：

1. **动作分布**：是否只执行动作0？
2. **战斗表现**：遇到敌人时是否攻击？
3. **响应速度**：动作执行是否及时？
4. **准确性**：执行的动作是否合理？

---

## 📝 完整工作流程时间表

### 快速方案（1-2小时）：
1. 数据增强（15分钟）
2. 使用类别权重训练（45分钟）
3. 模型测试（10分钟）
4. 游戏测试（15分钟）

### 标准方案（4-6小时）：
1. 录制10个战斗视频（2小时）
2. 处理视频生成数据（30分钟）
3. 数据增强（15分钟）
4. 使用类别权重训练（1小时）
5. 模型测试（10分钟）
6. 游戏测试和调整（1小时）

### 完整方案（1-2天）：
1. 录制30-40个战斗视频（4-6小时）
2. 处理视频生成数据（1小时）
3. 数据分析和增强（1小时）
4. 多次训练和调优（3-4小时）
5. 充分测试和调整（2-3小时）

---

## 🔍 故障排除

### 问题：数据增强后训练速度很慢
**解决**：减少target-samples参数，先尝试500个样本

### 问题：训练时显存不足
**解决**：减小batch-size，例如从16改为8

### 问题：模型在测试集上表现很好，但游戏中表现差
**原因**：训练数据和实际游戏场景分布不一致
**解决**：录制更多样化的游戏场景

### 问题：战斗动作准确率仍然很低（<40%）
**解决**：
1. 检查战斗样本是否真的增加了
2. 尝试增加class_weights中战斗动作的权重
3. 录制更多高质量的战斗场景

---

## 📊 数据集质量检查

训练前检查数据集分布：

```python
import pandas as pd

df = pd.read_csv("data/processed/transformer_dataset_augmented.csv")
action_counts = df['action'].value_counts().sort_index()

print("数据集分布:")
for action_id, count in action_counts.items():
    percentage = count / len(df) * 100
    print(f"动作 {action_id}: {count:5d} 个样本 ({percentage:5.2f}%)")
    
# 理想分布：没有任何类别超过30%
```

---

## 🎯 下一步建议

基于你有充足时间，我建议：

### 第1天（录制数据）：
1. ✅ 早上：录制15个近战战斗视频（动作4）
2. ✅ 下午：录制10个远程战斗视频（动作5）
3. ✅ 晚上：处理所有视频生成数据集

### 第2天（训练和测试）：
1. ✅ 早上：数据增强 + 第一轮训练
2. ✅ 下午：评估模型，调整参数，第二轮训练
3. ✅ 晚上：游戏测试，记录问题

### 第3天（优化）：
1. ✅ 根据测试结果调整
2. ✅ 最终训练
3. ✅ 充分测试

---

你想从哪个方案开始？我建议：

**如果想快速看到效果**：先运行数据增强 + 类别权重训练（方案1）
**如果想要最佳质量**：花时间录制更多战斗场景（方案2）
**如果时间充足**：组合方案，分3天完成

需要我帮你启动哪个方案？
