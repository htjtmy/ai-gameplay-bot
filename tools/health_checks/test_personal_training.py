#!/usr/bin/env python3
"""
验证个人训练功能是否正确安装

运行: python test_personal_training.py
"""

import sys
import os
from pathlib import Path

def check_file_exists(path, name):
    """检查文件是否存在"""
    if Path(path).exists():
        print(f"  ✓ {name}")
        return True
    else:
        print(f"  ✗ {name} - 未找到")
        return False

def check_import(module_name):
    """检查模块是否可导入"""
    try:
        __import__(module_name)
        print(f"  ✓ {module_name}")
        return True
    except ImportError as e:
        print(f"  ✗ {module_name} - {e}")
        return False

def main():
    print("="*60)
    print("AI 游戏机器人 - 个人训练功能验证")
    print("="*60)
    
    # Resolve repo root: tools/health_checks -> tools -> repo root
    root_dir = Path(__file__).resolve().parents[2]
    all_ok = True
    
    # 检查脚本文件
    print("\n📝 检查脚本文件...")
    scripts = [
        ("scripts/gameplay_recorder.py", "录制脚本"),
        ("scripts/process_gameplay_recording.py", "处理脚本"),
        ("scripts/quick_start_training.py", "快速启动脚本"),
    ]
    
    for script, name in scripts:
        all_ok &= check_file_exists(root_dir / script, name)
    
    # 检查文档
    print("\n📚 检查文档...")
    docs = [
        ("PERSONAL_TRAINING_GUIDE.md", "完整指南"),
        ("QUICK_START_PERSONAL.md", "快速参考"),
    ]
    
    for doc, name in docs:
        all_ok &= check_file_exists(root_dir / doc, name)
    
    # 检查必需的 Python 模块
    print("\n📦 检查 Python 依赖...")
    modules = [
        ("cv2", "OpenCV"),
        ("pynput", "输入监听 (pynput)"),
        ("mss", "屏幕捕获 (mss)"),
        ("pandas", "数据处理"),
        ("numpy", "数值计算"),
        ("torch", "PyTorch"),
    ]
    
    for module, name in modules:
        all_ok &= check_import(module)
    
    # 检查数据目录
    print("\n📂 检查数据目录...")
    dirs = [
        ("data/raw/gameplay_videos", "原始录制目录"),
        ("data/processed", "处理后数据目录"),
        ("models/transformer", "Transformer 模型目录"),
        ("deployment", "部署目录"),
    ]
    
    for dir_path, name in dirs:
        if (root_dir / dir_path).exists():
            print(f"  ✓ {name}")
        else:
            print(f"  ⚠ {name} - 不存在（将在需要时创建）")
    
    # 最终结果
    print("\n" + "="*60)
    if all_ok:
        print("✓ 所有检查通过！")
        print("\n开始使用:")
        print("  1. 快速开始: python scripts/quick_start_training.py all")
        print("  2. 或查看: QUICK_START_PERSONAL.md")
        print("  3. 详细指南: PERSONAL_TRAINING_GUIDE.md")
    else:
        print("✗ 部分检查失败，请安装缺失的依赖")
        print("\n安装依赖:")
        print("  pip install -r requirements.txt")
    print("="*60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
