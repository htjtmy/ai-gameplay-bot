"""
数据增强工具 - 针对少数类别进行图像增强

对战斗动作（动作4和5）等少数类别进行数据增强，包括：
- 随机旋转
- 亮度调整
- 对比度调整
- 高斯噪声
- 水平翻转

Usage:
    python scripts/augment_minority_classes.py --input "data/processed/transformer_dataset.csv" --output "data/processed/transformer_dataset_augmented.csv" --target-actions 4 5 --target-samples 1000
"""

import pandas as pd
import numpy as np
import cv2
import argparse
import logging
from pathlib import Path
from tqdm import tqdm
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageAugmenter:
    """图像增强器"""
    
    def __init__(self, augmentation_types=None):
        """
        初始化增强器
        
        Args:
            augmentation_types: 增强类型列表，默认使用所有类型
        """
        if augmentation_types is None:
            augmentation_types = ['rotate', 'brightness', 'contrast', 'noise', 'flip']
        
        self.augmentation_types = augmentation_types
    
    def load_image(self, image_path):
        """加载图像（支持中文路径）"""
        img_array = np.fromfile(str(image_path), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return img
    
    def save_image(self, image, output_path):
        """保存图像（支持中文路径）"""
        success, encoded_image = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if success:
            encoded_image.tofile(str(output_path))
            return True
        return False
    
    def rotate(self, image, angle=None):
        """随机旋转"""
        if angle is None:
            angle = random.uniform(-15, 15)
        
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (width, height))
        return rotated
    
    def adjust_brightness(self, image, factor=None):
        """调整亮度"""
        if factor is None:
            factor = random.uniform(0.7, 1.3)
        
        adjusted = cv2.convertScaleAbs(image, alpha=factor, beta=0)
        return adjusted
    
    def adjust_contrast(self, image, factor=None):
        """调整对比度"""
        if factor is None:
            factor = random.uniform(0.7, 1.3)
        
        adjusted = cv2.convertScaleAbs(image, alpha=factor, beta=128 * (1 - factor))
        return adjusted
    
    def add_noise(self, image, std=None):
        """添加高斯噪声"""
        if std is None:
            std = random.uniform(5, 15)
        
        noise = np.random.normal(0, std, image.shape).astype(np.uint8)
        noisy = cv2.add(image, noise)
        return noisy
    
    def flip(self, image, direction=None):
        """翻转图像"""
        if direction is None:
            direction = random.choice([0, 1])  # 0=垂直，1=水平
        
        flipped = cv2.flip(image, direction)
        return flipped
    
    def augment(self, image, num_augmentations=1):
        """
        对图像进行增强
        
        Args:
            image: 输入图像
            num_augmentations: 生成的增强图像数量
        
        Returns:
            增强后的图像列表
        """
        augmented_images = []
        
        for _ in range(num_augmentations):
            aug_image = image.copy()
            
            # 随机选择1-3个增强操作
            num_ops = random.randint(1, 3)
            ops = random.sample(self.augmentation_types, num_ops)
            
            for op in ops:
                if op == 'rotate':
                    aug_image = self.rotate(aug_image)
                elif op == 'brightness':
                    aug_image = self.adjust_brightness(aug_image)
                elif op == 'contrast':
                    aug_image = self.adjust_contrast(aug_image)
                elif op == 'noise':
                    aug_image = self.add_noise(aug_image)
                elif op == 'flip':
                    aug_image = self.flip(aug_image)
            
            augmented_images.append(aug_image)
        
        return augmented_images


def augment_dataset(input_csv, output_csv, target_actions, target_samples_per_action):
    """
    对数据集进行增强
    
    Args:
        input_csv: 输入数据集CSV
        output_csv: 输出数据集CSV
        target_actions: 需要增强的动作ID列表
        target_samples_per_action: 每个动作的目标样本数
    """
    logger.info(f"加载数据集: {input_csv}")
    df = pd.read_csv(input_csv)
    
    # 分析当前数据分布
    logger.info("\n当前数据分布:")
    action_counts = df['action'].value_counts().sort_index()
    for action_id, count in action_counts.items():
        logger.info(f"  动作 {action_id}: {count} 个样本")
    
    # 初始化增强器
    augmenter = ImageAugmenter()
    
    # 准备输出目录
    output_dir = Path(output_csv).parent / "augmented_frames"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # 复制原始数据
    augmented_data = df.copy()
    new_rows = []
    
    # 对每个目标动作进行增强
    for action_id in target_actions:
        action_samples = df[df['action'] == action_id]
        current_count = len(action_samples)
        
        if current_count >= target_samples_per_action:
            logger.info(f"\n动作 {action_id}: 已有 {current_count} 个样本，无需增强")
            continue
        
        needed_samples = target_samples_per_action - current_count
        logger.info(f"\n动作 {action_id}: 需要增强 {needed_samples} 个样本")
        
        # 计算每个原始样本需要生成多少个增强样本
        augmentations_per_sample = needed_samples // current_count + 1
        
        with tqdm(total=needed_samples, desc=f"增强动作 {action_id}") as pbar:
            generated_count = 0
            
            for idx, row in action_samples.iterrows():
                if generated_count >= needed_samples:
                    break
                
                # 加载原始图像
                try:
                    original_image = augmenter.load_image(row['frame_path'])
                except Exception as e:
                    logger.warning(f"无法加载图像 {row['frame_path']}: {e}")
                    continue
                
                # 生成增强图像
                aug_images = augmenter.augment(original_image, augmentations_per_sample)
                
                for i, aug_img in enumerate(aug_images):
                    if generated_count >= needed_samples:
                        break
                    
                    # 保存增强图像
                    aug_filename = f"action_{action_id}_aug_{idx}_{i}.jpg"
                    aug_path = output_dir / aug_filename
                    
                    if augmenter.save_image(aug_img, aug_path):
                        # 提取特征（与原始处理相同）
                        img_resized = cv2.resize(aug_img, (64, 64))
                        features = img_resized.flatten().astype(np.float32) / 255.0
                        
                        # 创建新行
                        new_row = {'frame_path': str(aug_path), 'action': action_id}
                        
                        # 添加特征列
                        for j, feature in enumerate(features):
                            new_row[f'feature_{j}'] = feature
                        
                        new_rows.append(new_row)
                        generated_count += 1
                        pbar.update(1)
        
        logger.info(f"  完成: 生成了 {generated_count} 个增强样本")
    
    # 合并原始数据和增强数据
    if new_rows:
        augmented_df = pd.DataFrame(new_rows)
        final_df = pd.concat([augmented_data, augmented_df], ignore_index=True)
    else:
        final_df = augmented_data
    
    # 保存结果
    logger.info(f"\n保存增强后的数据集: {output_csv}")
    final_df.to_csv(output_csv, index=False)
    
    # 显示最终分布
    logger.info("\n增强后数据分布:")
    final_action_counts = final_df['action'].value_counts().sort_index()
    for action_id, count in final_action_counts.items():
        logger.info(f"  动作 {action_id}: {count} 个样本")
    
    logger.info(f"\n总样本数: {len(df)} -> {len(final_df)} (+{len(final_df) - len(df)})")


def main():
    parser = argparse.ArgumentParser(description='数据增强工具')
    parser.add_argument('--input', required=True, help='输入数据集CSV')
    parser.add_argument('--output', required=True, help='输出数据集CSV')
    parser.add_argument('--target-actions', type=int, nargs='+', default=[4, 5], 
                        help='需要增强的动作ID')
    parser.add_argument('--target-samples', type=int, default=1000,
                        help='每个动作的目标样本数')
    
    args = parser.parse_args()
    
    augment_dataset(
        input_csv=args.input,
        output_csv=args.output,
        target_actions=args.target_actions,
        target_samples_per_action=args.target_samples
    )
    
    logger.info("\n✅ 数据增强完成！")


if __name__ == "__main__":
    main()
