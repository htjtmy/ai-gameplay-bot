# 🚀 开始使用 - 个人游戏训练

## 三分钟快速上手

### 第一步：打开终端

```powershell
# 进入项目目录
cd d:\Users\Source\Ai-Gameplay-Bot

# 激活环境
conda activate Ai-Gameplay-Bot
```

### 第二步：验证安装

```bash
# 检查所有依赖是否正确
python test_personal_training.py
```

预期输出：✓ 所有检查通过！

### 第三步：开始训练

```bash
# 一条命令完成整个流程
python scripts/quick_start_training.py all
```

**就这样！** 脚本会：
1. ▶️ 启动屏幕录制
2. ⏹️ 等你玩游戏（按 Q 停止）
3. 📹 自动提取视频帧
4. 🎯 自动识别游戏操作
5. 🧠 自动训练 AI 模型
6. ✅ 完成！

---

## 更多选项

### 分步运行

```bash
# 1️⃣ 只录制
python scripts/quick_start_training.py record --session my_game

# 2️⃣ 只处理数据
python scripts/quick_start_training.py process --latest

# 3️⃣ 只训练
python scripts/quick_start_training.py train

# 4️⃣ 只部署
python scripts/quick_start_training.py deploy
```

### 自定义参数

```bash
# 自定义屏幕区域（1920x1080）
python scripts/quick_start_training.py record --screen 0 0 1920 1080

# 给会话起个名字
python scripts/quick_start_training.py record --session my_awesome_game

# 加速处理（跳过每 5 帧中的 4 帧）
python scripts/quick_start_training.py process --latest --skip 5
```

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| 👉 **QUICK_START_PERSONAL.md** | **快速参考**（最常用） |
| 📘 **PERSONAL_TRAINING_GUIDE.md** | 完整详细教程 |
| 📕 **PERSONAL_TRAINING_README.md** | 项目功能介绍 |
| ✅ **test_personal_training.py** | 依赖检查工具 |

---

## 🎮 游戏操作支持

系统自动识别以下操作：

**移动** - W/A/S/D  
**转向** - Q/E  
**战斗** - 左键/右键/C/X/空格/Shift/Ctrl  
**交互** - F/I/M/P/T  
**其他** - R、鼠标移动  

共 **27 个** 不同的动作。

---

## ❓ 常见问题

**Q: 录制时屏幕黑屏？**  
A: 调整屏幕区域：`--screen 0 0 1920 1080`

**Q: 没有记录到操作？**  
A: 确保命令行窗口最小化，不要在最前面

**Q: 训练很慢？**  
A: 使用 `--skip 2` 或 `--skip 5` 加速

**Q: 更多帮助？**  
A: 查看 [PERSONAL_TRAINING_GUIDE.md](PERSONAL_TRAINING_GUIDE.md)

---

## 🎯 下一步

✅ 验证安装  
→ 📹 录制游戏  
→ 🤖 训练模型  
→ 🌐 部署服务  
→ 🎉 完成！

---

**准备好了吗？** 

```bash
python scripts/quick_start_training.py all
```
