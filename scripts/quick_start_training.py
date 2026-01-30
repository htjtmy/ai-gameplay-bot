#!/usr/bin/env python3
"""
快速开始脚本 - 从录制到训练的一体化工具

使用示例：
    python scripts/quick_start_training.py --help
    python scripts/quick_start_training.py record
    python scripts/quick_start_training.py process
    python scripts/quick_start_training.py train
    python scripts/quick_start_training.py all
"""

import argparse
import sys
import os
import json
import subprocess
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QuickStartTrainer:
    """一体化训练工具"""
    
    def __init__(self, session=None):
        self.session = session
        self.root_dir = Path(__file__).parent.parent
        self.recordings_dir = self.root_dir / "data" / "raw" / "gameplay_videos"
        self.processed_dir = self.root_dir / "data" / "processed"
    
    def record(self, screen_area=None, process_name=None, category=None, label=None):
        """第一步：录制游戏"""
        logger.info("="*60)
        logger.info("步骤 1: 录制游戏视频和操作")
        logger.info("="*60)
        
        cmd = [sys.executable, "scripts/gameplay_recorder.py"]
        
        if self.session:
            cmd.extend(["--session", self.session])
        
        if screen_area:
            cmd.extend(["--screen"] + [str(x) for x in screen_area])
        
        if process_name:
            cmd.extend(["--process", process_name])
        
        if category:
            cmd.extend(["--category", category])
        
        if label:
            cmd.extend(["--label", label])
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.root_dir),
                check=False
            )
            
            if result.returncode == 0:
                logger.info("✓ 录制完成")
                return True
            else:
                logger.error("✗ 录制失败")
                return False
        except Exception as e:
            logger.error(f"✗ 录制错误: {e}")
            return False
    
    def find_latest_session(self):
        """查找最新的录制会话"""
        if not self.recordings_dir.exists():
            logger.error("未找到录制目录")
            return None
        
        sessions = sorted([
            d for d in self.recordings_dir.iterdir()
            if d.is_dir() and (d / "gameplay.mp4").exists()
        ])
        
        if not sessions:
            logger.error("未找到任何录制会话")
            return None
        
        return str(sessions[-1])
    
    def process(self, session=None, skip_frames=1):
        """第二步：处理录制数据"""
        logger.info("="*60)
        logger.info("步骤 2: 处理录制数据")
        logger.info("="*60)
        
        target_session = session or self.session or self.find_latest_session()
        
        if not target_session:
            logger.error("✗ 未指定会话，且未找到最新录制")
            return False
        
        cmd = [
            sys.executable,
            "scripts/process_gameplay_recording.py",
            "--session", target_session,
            "--skip", str(skip_frames)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.root_dir),
                check=False
            )
            
            if result.returncode == 0:
                logger.info("✓ 数据处理完成")
                
                # 查找生成的数据集
                session_name = Path(target_session).name
                dataset_file = self.processed_dir / f"dataset_{session_name}.csv"
                
                if dataset_file.exists():
                    logger.info(f"✓ 数据集: {dataset_file}")
                    return str(dataset_file)
                return True
            else:
                logger.error("✗ 数据处理失败")
                return False
        except Exception as e:
            logger.error(f"✗ 处理错误: {e}")
            return False
    
    def train(self, dataset_file=None):
        """第三步：训练模型"""
        logger.info("="*60)
        logger.info("步骤 3: 训练 Transformer 模型")
        logger.info("="*60)
        
        if dataset_file:
            # 更新训练脚本中的数据集路径
            training_script = self.root_dir / "models" / "transformer" / "transformer_training.py"
            
            try:
                with open(training_script, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替换数据集路径
                import re
                new_content = re.sub(
                    r'DATASET_PATH\s*=\s*"[^"]*"',
                    f'DATASET_PATH = "{dataset_file}"',
                    content
                )
                
                with open(training_script, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                logger.info(f"✓ 已更新数据集路径: {dataset_file}")
            except Exception as e:
                logger.warning(f"警告: 无法更新数据集路径: {e}")
        
        cmd = [
            sys.executable,
            "models/transformer/transformer_training.py"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.root_dir),
                check=False
            )
            
            if result.returncode == 0:
                logger.info("✓ 模型训练完成")
                return True
            else:
                logger.error("✗ 模型训练失败")
                return False
        except Exception as e:
            logger.error(f"✗ 训练错误: {e}")
            return False
    
    def deploy(self):
        """第四步（可选）：部署服务"""
        logger.info("="*60)
        logger.info("步骤 4: 部署服务")
        logger.info("="*60)
        
        cmd = [
            sys.executable,
            "deployment/control_backend.py"
        ]
        
        try:
            logger.info("启动服务...")
            logger.info("访问: http://localhost:8000")
            
            subprocess.run(
                cmd,
                cwd=str(self.root_dir),
                check=False
            )
            return True
        except KeyboardInterrupt:
            logger.info("服务已停止")
            return True
        except Exception as e:
            logger.error(f"✗ 部署错误: {e}")
            return False
    
    def run_all(self, skip_frames=1, process_name=None, screen_area=None, category=None, label=None):
        """完整流程：录制 -> 处理 -> 训练 -> 部署"""
        logger.info("\n")
        logger.info("#" * 60)
        logger.info("# AI 游戏机器人 - 完整训练流程")
        logger.info("#" * 60)
        
        # 步骤 1: 录制
        if not self.record(screen_area=screen_area, process_name=process_name, category=category, label=label):
            return False
        
        # 步骤 2: 处理
        dataset_file = self.process(skip_frames=skip_frames)
        if not dataset_file:
            return False
        
        # 步骤 3: 训练
        if not self.train(dataset_file if isinstance(dataset_file, str) else None):
            return False
        
        logger.info("\n")
        logger.info("#" * 60)
        logger.info("# ✓ 训练完成！")
        logger.info("#" * 60)
        logger.info("\n可选: 部署服务")
        logger.info("  python scripts/quick_start_training.py deploy\n")
        
        return True


def main():
    """主程序"""
    parser = argparse.ArgumentParser(
        description="AI 游戏机器人 - 快速训练工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 完整流程（推荐）
  python scripts/quick_start_training.py all

  # 逐步运行
  python scripts/quick_start_training.py record --session my_game
  python scripts/quick_start_training.py process --session my_game
  python scripts/quick_start_training.py train
  python scripts/quick_start_training.py deploy

  # 处理现有录制
  python scripts/quick_start_training.py process --latest
  
  # 自定义屏幕区域
  python scripts/quick_start_training.py record --screen 0 0 1920 1080
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # record 命令
    record_parser = subparsers.add_parser('record', help='录制游戏')
    record_parser.add_argument('--session', help='会话名称')
    record_parser.add_argument('--screen', type=int, nargs=4, metavar=('X', 'Y', 'W', 'H'),
                              help='屏幕区域 (x y width height)')
    record_parser.add_argument('--process', help='进程名，自动匹配窗口并开始录制')
    record_parser.add_argument('--category', help='视频分类（自动创建子目录）')
    record_parser.add_argument('--label', help='视频标签（附加在文件名中）')
    
    # process 命令
    process_parser = subparsers.add_parser('process', help='处理录制数据')
    process_parser.add_argument('--session', help='会话目录')
    process_parser.add_argument('--latest', action='store_true', help='使用最新的录制')
    process_parser.add_argument('--skip', type=int, default=1, help='跳帧数')
    
    # train 命令
    train_parser = subparsers.add_parser('train', help='训练模型')
    train_parser.add_argument('--dataset', help='数据集文件路径')
    
    # deploy 命令
    subparsers.add_parser('deploy', help='部署服务')
    
    # all 命令
    all_parser = subparsers.add_parser('all', help='完整流程')
    all_parser.add_argument('--session', help='会话名称')
    all_parser.add_argument('--skip', type=int, default=1, help='跳帧数')
    all_parser.add_argument('--screen', type=int, nargs=4, metavar=('X', 'Y', 'W', 'H'),
                           help='屏幕区域')
    all_parser.add_argument('--process', help='进程名，自动匹配窗口并开始录制')
    all_parser.add_argument('--category', help='视频分类（自动创建子目录）')
    all_parser.add_argument('--label', help='视频标签（附加在文件名中）')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    trainer = QuickStartTrainer(session=getattr(args, 'session', None))
    
    if args.command == 'record':
        trainer.record(
            screen_area=getattr(args, 'screen', None),
            process_name=getattr(args, 'process', None),
            category=getattr(args, 'category', None),
            label=getattr(args, 'label', None)
        )
    
    elif args.command == 'process':
        session = args.session
        if args.latest:
            session = trainer.find_latest_session()
        trainer.process(session=session, skip_frames=args.skip)
    
    elif args.command == 'train':
        trainer.train(dataset_file=getattr(args, 'dataset', None))
    
    elif args.command == 'deploy':
        trainer.deploy()
    
    elif args.command == 'all':
        success = trainer.run_all(
            skip_frames=args.skip,
            process_name=getattr(args, 'process', None),
            screen_area=getattr(args, 'screen', None),
            category=getattr(args, 'category', None),
            label=getattr(args, 'label', None)
        )
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
