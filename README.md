<div align="center">

# 🎮 二重螺旋 AI 游戏机器人
### 配置驱动的智能游戏自动化平台

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PyTorch-2.0-red?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch">
  <img src="https://img.shields.io/badge/Flask-API-green?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/htjtmy/ai-gameplay-bot?style=social" alt="Stars">
  <img src="https://img.shields.io/github/forks/htjtmy/ai-gameplay-bot?style=social" alt="Forks">
  <img src="https://img.shields.io/github/issues/htjtmy/ai-gameplay-bot" alt="Issues">
  <img src="https://img.shields.io/github/last-commit/htjtmy/ai-gameplay-bot" alt="Last Commit">
</p>

**为《二重螺旋》游戏定制的AI自动化平台**
*配置驱动 • 快速切换 • 中文支持*

[🚀 快速开始](#-快速开始) • [📚 文档](#-文档) • [🎯 特性](#-特性) • [🔧 配置系统](#-配置系统)

---

</div>

## 🌟 项目概述
![](assets/2025-12-30-01-54-05.png)

本项目是为《二重螺旋》游戏定制的AI自动化平台，基于 [ruslanmv/ai-gameplay-bot](https://github.com/ruslanmv/ai-gameplay-bot) 进行深度改进。

### ✨ 主要改进

- **🎯 配置驱动架构**：通过JSON配置文件快速切换不同游戏的按键映射
- **🇨🇳 完整中文支持**：支持中文文件名、路径和界面
- **🎮 23个动作映射**：包括移动、战斗、技能、界面操作等
- **⌨️ 灵活按键配置**：支持鼠标、键盘、组合键等多种输入
- **🎥 游戏录制功能**：支持录制游戏画面和输入序列
- **🛠️ 配置验证工具**：自动检查配置文件的正确性

本项目在原有AI训练框架基础上，重构了动作映射系统，使其更易于定制和维护。

### 🎯 Why Choose AI Gameplay Bot?

<table>
<tr>
<td width="33%" align="center">
  <h3>🚀 Performance</h3>
  <p>Sub-100ms latency with neural network models. Handle 1000+ requests/second with horizontal scaling.</p>
</td>
<td width="33%" align="center">
  <h3>🛡️ Enterprise-Ready</h3>
  <p>Production-grade logging, monitoring, health checks, and comprehensive error handling.</p>
</td>
<td width="33%" align="center">
  <h3>🧠 State-of-the-Art AI</h3>
  <p>Dual-model architecture: Fast NN & Context-aware Transformers. Reinforcement learning ready.</p>
</td>
</tr>
</table>

---

## 🎓 How It Works

The core idea mimics how humans learn to play games:
1. **👀 Observation**: Watch expert players on YouTube/Twitch to understand strategies
2. **🎯 Action Mapping**: Deduce inputs (keypresses, mouse movements) from observed actions
3. **🧠 Training**: Train ML models (Neural Networks & Transformers) on mapped data
4. **🚀 Self-Improvement**: Enhance gameplay through Reinforcement Learning

---

## ✨ Features

### 🎯 核心特性

<table>
<tr>
<td width="33%" align="center">
  <h3>⚙️ 配置驱动</h3>
  <p>通过JSON配置文件管理所有动作映射，无需修改代码即可切换游戏。</p>
</td>
<td width="33%" align="center">
  <h3>🇨🇳 中文支持</h3>
  <p>完整支持中文文件名、路径和界面，适配国产游戏。</p>
</td>
<td width="33%" align="center">
  <h3>🎮 灵活映射</h3>
  <p>23个可配置动作，支持键盘、鼠标、组合键等多种输入方式。</p>
</td>
</tr>
</table>

---

## 📋 功能列表

### 🎯 核心功能

- **⚙️ 配置驱动架构**
  - 📝 **JSON配置文件**：所有动作定义集中管理
  - 🔄 **快速切换**：通过环境变量或参数切换不同游戏配置
  - ✅ **配置验证**：内置验证工具检查配置正确性
  - 📊 **按键查看**：可视化查看所有按键绑定

- **🎮 游戏录制与训练**
  - 🎥 **游戏录制**：录制游戏画面和玩家输入序列
  - 📹 **中文文件名**：支持中文会话名称和分类
  - ⌨️ **F8停止键**：自定义停止录制快捷键
  - 🧠 **AI训练**：基于录制数据训练神经网络模型

- **🤖 AI模型系统**
  - ⚡ **神经网络**：快速响应（<100ms延迟）
  - 🧠 **Transformer**：上下文感知的序列决策
  - 🔄 **热切换**：无需停机即可切换模型

- **🔌 RESTful API**
  - 📡 高性能Flask后端
  - 🔐 健康检查端点
  - 📝 完整的API文档
  - 🌐 支持CORS跨域
  - 📉 Detailed performance reports

### 🛠️ Production Features

```
✅ Comprehensive Logging      ✅ Error Tracking & Monitoring
✅ Health Check Endpoints      ✅ Graceful Shutdown Handling
✅ Environment Configuration   ✅ Docker Support (Coming Soon)
✅ Automated Testing          ✅ CI/CD Ready
✅ Horizontal Scaling         ✅ Model Versioning
✅ Real-time Metrics          ✅ Performance Profiling
```

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 4GB RAM 最低（推荐8GB）
- CUDA GPU（可选，用于训练）
- Windows/Linux/macOS

### ⚡ 安装步骤

```bash
# 克隆仓库
git clone https://github.com/htjtmy/ai-gameplay-bot.git
cd ai-gameplay-bot

# 创建conda环境（推荐）
conda create -n Ai-Gameplay-Bot python=3.8
conda activate Ai-Gameplay-Bot

# 安装依赖
pip install -r requirements.txt
```

### 🎮 配置与使用

#### 1. 查看按键配置

```bash
# 查看当前游戏的按键配置
python scripts/show_key_bindings.py

# 验证配置文件
python scripts/validate_actions_config.py config/game_actions.json
```

#### 2. 录制游戏数据

```bash
# 启动游戏录制（指定游戏进程）
python scripts/gameplay_recorder.py --process MuMuNxDevice.exe --session "测试会话" --category "训练"

# 按F8停止录制
```

#### 3. 启动控制后端

```bash
# 使用make启动（需要先安装make）
conda install -y -c conda-forge make
make run-control

# 或直接运行
python deployment/control_backend.py
```

**完成！** 🎉 控制后端运行在 `http://localhost:8000`

---

## 🔧 配置系统

本项目采用配置驱动架构，所有动作映射集中在 `config/game_actions.json`。

### 查看配置

```bash
# 可视化查看按键配置
python scripts/show_key_bindings.py
```

### 修改配置

直接编辑 `config/game_actions.json`：

```json
{
  "game_name": "二重螺旋",
  "actions": [
    {
      "id": 0,
      "name": "MOVE_FORWARD",
      "display_name_zh": "前进",
      "keys": ["w"],
      "gamepad": "LS_UP"
    }
  ]
}
```

### 切换游戏

1. 复制配置文件：`cp config/game_actions.json config/game_actions_other.json`
2. 修改新配置
3. 使用环境变量切换：
   ```bash
   $env:GAME_ACTIONS_CONFIG = "config/game_actions_other.json"
   python scripts/gameplay_recorder.py
   ```

详细说明见 [配置系统文档](CONFIG_DRIVEN_SYSTEM.md)

---

## 📚 文档

### 📖 完整指南

| 文档 | 说明 |
|----------|-------------|
| [**📘 配置系统**](CONFIG_DRIVEN_SYSTEM.md) | 配置驱动架构完整说明 |
| [**📗 游戏切换指南**](config/GAME_SWITCHING_GUIDE.md) | 如何快速切换不同游戏配置 |
| [**📙 配置文档**](config/README.md) | JSON配置文件格式和最佳实践 |
| [**📕 API文档**](docs/API.md) | REST API完整参考 |
| [**📓 数据格式**](data/README.md) | 数据集格式说明 |

### 🎯 Quick References

<details>
<summary><b>🔧 Common Commands (Makefile)</b></summary>

```bash
make help              # Show all available commands
make setup             # Complete project setup
make data              # Generate sample data
make train-all         # Train both models
make test              # Run tests
make test-coverage     # Run tests with coverage
make run-control       # Start control backend
make stop              # Stop all services
make clean             # Clean temporary files
```
</details>

<details>
<summary><b>🐍 Python API Usage</b></summary>

```python
import requests

# Predict action using Neural Network
state = [0.5] * 128  # Your game state features
response = requests.post(
    "http://localhost:5000/predict",
    json={"state": state}
)
action = response.json()["action"]
print(f"Predicted action: {action}")

# Switch active model
requests.post(
    "http://localhost:8000/api/set_active_model",
    json={"model": "transformer"}
)
```
</details>

<details>
<summary><b>🌐 JavaScript API Usage</b></summary>

```javascript
// Predict action
const state = Array(128).fill(0.5);
const response = await fetch('http://localhost:5000/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ state })
});
const data = await response.json();
console.log('Action:', data.action);
```
</details>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Dashboard                      │
│         (Real-time monitoring & control panel)               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Control Backend API                        │
│              (Service orchestration & management)            │
└──────────┬───────────────────────────────────┬──────────────┘
           │                                   │
           ▼                                   ▼
┌──────────────────────┐           ┌──────────────────────┐
│   Neural Network     │           │    Transformer       │
│   Prediction API     │           │   Prediction API     │
│   (Port 5000)        │           │   (Port 5001)        │
└──────────────────────┘           └──────────────────────┘
           │                                   │
           └───────────────┬───────────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │   Game State Input     │
              │   (128-dim features)   │
              └────────────────────────┘
```

---

## 📦 Project Structure

```
ai-gameplay-bot/
├── 🎨 frontend/              # Web-based control panel
├── 🚀 deployment/            # Production deployment scripts
│   ├── deploy_nn.py          # Neural network API
│   ├── deploy_transformer.py # Transformer API
│   └── control_backend.py    # Service orchestration
├── 🧠 models/                # AI model implementations
│   ├── neural_network/       # NN architecture & training
│   └── transformer/          # Transformer architecture
├── 📊 scripts/               # Data processing utilities
├── 🧪 tests/                 # Comprehensive test suite
├── 📈 evaluation/            # Performance analytics
├── 📚 data/                  # Datasets and annotations
└── 📖 docs/                  # Documentation
```

---

## 💼 Enterprise Solutions

### 🏢 Production Deployment

```bash
# Production mode with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 deployment.control_backend:app

# With supervisor for process management
supervisorctl start ai-gameplay-bot

# Docker deployment (coming soon)
docker-compose up -d
```

### 📊 Monitoring & Observability

- **Logging**: Rotating logs with multiple severity levels
- **Metrics**: Prometheus-compatible metrics endpoint
- **Health Checks**: Built-in health check endpoints
- **Alerts**: Integration-ready for PagerDuty, Slack, etc.

### 🔒 Security Features

- Environment-based configuration
- API key authentication (roadmap)
- Rate limiting support
- Input validation and sanitization
- HTTPS/TLS ready

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage report
make test-coverage

# Performance testing
python evaluation/real_time_tests.py
```

### 📈 Test Coverage

- ✅ Unit tests for all models
- ✅ Integration tests for APIs
- ✅ Performance benchmarking
- ✅ Load testing utilities

---

## 🎓 Training Custom Models

### Neural Network Model

```bash
python models/neural_network/nn_training.py
```

**Configuration**:
- Input: 128-dimensional feature vectors
- Architecture: 3 hidden layers with batch normalization
- Output: 10 action classes
- Training time: ~10 minutes on GPU

### Transformer Model

```bash
python models/transformer/transformer_training.py
```

**Configuration**:
- Sequence length: 10 frames
- Attention heads: 4
- Transformer layers: 3
- Training time: ~20 minutes on GPU

---

## 🎯 Use Cases

<table>
<tr>
<td>

### 🎮 Gaming
- Automated gameplay testing
- Bot development
- Game AI research
- QA automation

</td>
<td>

### 🔬 Research
- Reinforcement learning
- Imitation learning
- Behavioral cloning
- Multi-agent systems

</td>
<td>

### 💼 Enterprise
- Game testing at scale
- Performance benchmarking
- AI model comparison
- Production ML deployment

</td>
</tr>
</table>

---

## 🔄 Roadmap

- [ ] 🐳 Docker & Kubernetes deployment
- [ ] 📊 Grafana dashboards
- [ ] 🔐 API key authentication
- [ ] 🌐 WebSocket support for real-time streaming
- [ ] 🎯 Pre-trained models for popular games
- [ ] 📱 Mobile app for remote control
- [ ] 🤖 Multi-agent coordination
- [ ] 🧩 Plugin system for game integrations

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

```bash
# Fork the repository
# Create your feature branch
git checkout -b feature/AmazingFeature

# Commit your changes
git commit -m 'Add some AmazingFeature'

# Push to the branch
git push origin feature/AmazingFeature

# Open a Pull Request
```

---

## 📄 License

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

基于 [ruslanmv/ai-gameplay-bot](https://github.com/ruslanmv/ai-gameplay-bot) 改进。

---

## 🌐 社区与支持

<div align="center">

### 💬 获取帮助

[![GitHub Issues](https://img.shields.io/badge/GitHub-Issues-red?style=for-the-badge&logo=github&logoColor=white)](https://github.com/htjtmy/ai-gameplay-bot/issues)
[![GitHub Discussions](https://img.shields.io/badge/GitHub-Discussions-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/htjtmy/ai-gameplay-bot/discussions)

### 🙏 致谢

感谢 [Ruslan Magana Vsevolodovna](https://github.com/ruslanmv) 创建的原始项目。

本项目针对《二重螺旋》游戏进行深度定制和改进。

</div>

---

## 📊 项目统计

<div align="center">

![GitHub repo size](https://img.shields.io/github/repo-size/htjtmy/ai-gameplay-bot?style=flat-square)
![GitHub code size](https://img.shields.io/github/languages/code-size/htjtmy/ai-gameplay-bot?style=flat-square)
![GitHub top language](https://img.shields.io/github/languages/top/htjtmy/ai-gameplay-bot?style=flat-square)

</div>

---

<div align="center">

### ⭐ 如果觉得有用，请给个星标！

**分享爱心：** 如果这个项目帮助了你，请给它一个星标 ⭐ 并分享给其他人！

<sub>为《二重螺旋》玩家社区打造 🎮</sub>

</div>
