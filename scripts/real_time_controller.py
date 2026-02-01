"""
实时游戏控制器 - 使用训练好的模型控制游戏

This script:
1. 加载训练好的Transformer模型
2. 实时捕获游戏画面
3. 使用模型预测动作
4. 执行动作控制游戏

Usage:
    python scripts/real_time_controller.py --model "models/transformer/transformer_model.pth" --process "MuMuNxDevice.exe"
"""

import cv2
import torch
import numpy as np
import time
import argparse
import logging
import sys
from pathlib import Path
from collections import deque

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.transformer.transformer_model import GameplayTransformer
from scripts.input_mapping import get_action_mapper
import mss
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealtimeGameController:
    """实时游戏控制器"""
    
    def __init__(self, model_path, config_path="config/game_actions.json", 
                 input_size=12288, output_size=25, image_size=64,
                 num_heads=4, hidden_size=256, num_layers=3,
                 fps=10, confidence_threshold=0.5):
        """
        初始化控制器
        
        Args:
            model_path: 模型路径
            config_path: 游戏动作配置路径
            input_size: 输入特征维度
            output_size: 输出动作数
            image_size: 图像尺寸
            fps: 预测频率（每秒多少次）
            confidence_threshold: 动作执行的置信度阈值
        """
        self.image_size = image_size
        self.fps = fps
        self.confidence_threshold = confidence_threshold
        
        # 设置设备
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"使用设备: {self.device}")
        
        # 加载模型
        logger.info(f"加载模型: {model_path}")
        self.model = GameplayTransformer(
            input_size=input_size,
            output_size=output_size,
            num_heads=num_heads,
            hidden_size=hidden_size,
            num_layers=num_layers
        )
        state_dict = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model = self.model.to(self.device)
        self.model.eval()
        logger.info("✅ 模型加载成功")
        
        # 加载动作映射
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.action_mapping = {action['id']: action['name'] for action in config['actions']}
        logger.info(f"加载了 {len(self.action_mapping)} 个动作")
        
        # 初始化输入映射器
        self.action_mapper = get_action_mapper(config_path)
        
        # 统计信息
        self.frame_count = 0
        self.action_history = deque(maxlen=100)
        self.last_action = None
        self.action_start_time = None
    
    def extract_features(self, screen):
        """从屏幕截图提取特征"""
        # 调整大小
        img = cv2.resize(screen, (self.image_size, self.image_size))
        
        # 归一化
        img = img.astype(np.float32) / 255.0
        
        # 扁平化
        features = img.flatten()
        
        return features
    
    def predict_action(self, features):
        """预测动作"""
        # 转换为tensor
        features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        # 预测
        with torch.no_grad():
            outputs = self.model(features_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            
            action_id = predicted.item()
            confidence_value = confidence.item()
        
        return action_id, confidence_value
    
    def execute_action(self, action_id, confidence):
        """执行动作"""
        if confidence < self.confidence_threshold:
            return False
        
        action_name = self.action_mapping.get(action_id, f"UNKNOWN_{action_id}")
        
        # 如果是同一个动作，不重复执行
        if action_id == self.last_action:
            return False
        
        # 执行动作
        try:
            self.action_mapper.execute_action(action_name)
            self.last_action = action_id
            self.action_start_time = time.time()
            self.action_history.append((action_id, action_name, confidence))
            logger.info(f"执行动作: {action_name} (ID:{action_id}, 置信度:{confidence*100:.1f}%)")
            return True
        except Exception as e:
            logger.error(f"执行动作失败 {action_name}: {e}")
            return False
    
    def run(self, screen_area=None, duration=None):
        """
        运行实时控制
        
        Args:
            screen_area: 屏幕捕获区域 (x, y, width, height)
            duration: 运行时长（秒），None表示无限运行
        """
        if screen_area is None:
            screen_area = (0, 0, 1280, 720)
        
        monitor = {
            "top": screen_area[1],
            "left": screen_area[0],
            "width": screen_area[2],
            "height": screen_area[3]
        }
        
        logger.info("=" * 60)
        logger.info("🎮 实时游戏控制器已启动")
        logger.info(f"屏幕区域: {screen_area}")
        logger.info(f"预测频率: {self.fps} FPS")
        logger.info(f"置信度阈值: {self.confidence_threshold}")
        logger.info("按 Ctrl+C 停止")
        logger.info("=" * 60)
        
        start_time = time.time()
        frame_interval = 1.0 / self.fps
        
        try:
            with mss.mss() as sct:
                while True:
                    loop_start = time.time()
                    
                    # 捕获屏幕
                    screenshot = sct.grab(monitor)
                    frame = np.array(screenshot)[:, :, :3]  # 去除alpha通道
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    # 提取特征
                    features = self.extract_features(frame)
                    
                    # 预测动作
                    action_id, confidence = self.predict_action(features)
                    
                    # 执行动作
                    self.execute_action(action_id, confidence)
                    
                    self.frame_count += 1
                    
                    # 显示统计信息（每100帧）
                    if self.frame_count % 100 == 0:
                        elapsed = time.time() - start_time
                        actual_fps = self.frame_count / elapsed
                        logger.info(f"统计: {self.frame_count} 帧, 实际FPS: {actual_fps:.1f}, 执行动作数: {len(self.action_history)}")
                    
                    # 检查是否达到运行时长
                    if duration and (time.time() - start_time) >= duration:
                        logger.info(f"达到运行时长 {duration} 秒，停止")
                        break
                    
                    # 控制帧率
                    elapsed = time.time() - loop_start
                    sleep_time = max(0, frame_interval - elapsed)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            logger.info("\n用户中断，停止控制")
        
        finally:
            # 显示最终统计
            total_time = time.time() - start_time
            logger.info("\n" + "=" * 60)
            logger.info("控制器已停止")
            logger.info(f"总运行时间: {total_time:.1f} 秒")
            logger.info(f"总帧数: {self.frame_count}")
            logger.info(f"平均FPS: {self.frame_count / total_time:.1f}")
            logger.info(f"执行动作数: {len(self.action_history)}")
            
            # 显示动作统计
            if self.action_history:
                logger.info("\n动作分布:")
                action_counts = {}
                for action_id, action_name, _ in self.action_history:
                    action_counts[action_name] = action_counts.get(action_name, 0) + 1
                
                for action_name, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    logger.info(f"  {action_name}: {count} 次")
            logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='实时游戏控制器')
    parser.add_argument('--model', default='models/transformer/transformer_model.pth', help='模型路径')
    parser.add_argument('--config', default='config/game_actions.json', help='动作配置路径')
    parser.add_argument('--input-size', type=int, default=12288, help='输入特征维度')
    parser.add_argument('--output-size', type=int, default=25, help='输出动作数')
    parser.add_argument('--image-size', type=int, default=64, help='图像尺寸')
    parser.add_argument('--fps', type=int, default=10, help='预测频率（每秒）')
    parser.add_argument('--confidence', type=float, default=0.5, help='动作执行的置信度阈值')
    parser.add_argument('--duration', type=int, help='运行时长（秒）')
    parser.add_argument('--screen', type=int, nargs=4, metavar=('X', 'Y', 'WIDTH', 'HEIGHT'),
                        default=(0, 0, 1280, 720), help='屏幕捕获区域')
    
    args = parser.parse_args()
    
    # 创建控制器
    controller = RealtimeGameController(
        model_path=args.model,
        config_path=args.config,
        input_size=args.input_size,
        output_size=args.output_size,
        image_size=args.image_size,
        fps=args.fps,
        confidence_threshold=args.confidence
    )
    
    # 运行
    controller.run(
        screen_area=tuple(args.screen),
        duration=args.duration
    )


if __name__ == "__main__":
    main()
