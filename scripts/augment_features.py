"""
特征空间数据增强工具 - 直接在特征向量上进行增强

对战斗动作（动作4和5）等少数类别直接在特征空间进行数据增强：
- 添加高斯噪声
- 特征缩放
- 特征混合（同类别样本的线性组合）

Usage:
    python scripts/augment_features.py --input "data/processed/transformer_dataset.csv" --output "data/processed/transformer_dataset_augmented.csv" --target-actions 4 5 --target-samples 1000
"""

import pandas as pd
import numpy as np
import argparse
import logging
from tqdm import tqdm
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureAugmenter:
    """特征空间增强器"""
    
    def __init__(self):
        pass
    
    def add_noise(self, features, noise_level=0.02):
        """添加高斯噪声"""
        noise = np.random.normal(0, noise_level, features.shape)
        augmented = features + noise
        # 确保特征值在[0, 1]范围内
        augmented = np.clip(augmented, 0, 1)
        return augmented
    
    def scale_features(self, features, scale_factor=None):
        """特征缩放"""
        if scale_factor is None:
            scale_factor = random.uniform(0.9, 1.1)
        
        augmented = features * scale_factor
        augmented = np.clip(augmented, 0, 1)
        return augmented
    
    def mixup(self, features1, features2, alpha=0.2):
        """混合两个样本的特征"""
        lam = np.random.beta(alpha, alpha)
        augmented = lam * features1 + (1 - lam) * features2
        return augmented
    
    def augment(self, features, other_features_pool=None, num_augmentations=1):
        """
        对特征向量进行增强
        
        Args:
            features: 输入特征向量
            other_features_pool: 同类别的其他特征向量池（用于mixup）
            num_augmentations: 生成的增强样本数量
        
        Returns:
            增强后的特征向量列表
        """
        augmented_features = []
        
        for _ in range(num_augmentations):
            # 随机选择增强方法
            method = random.choice(['noise', 'scale', 'mixup', 'noise_scale'])
            
            if method == 'noise':
                aug = self.add_noise(features, noise_level=random.uniform(0.01, 0.03))
            elif method == 'scale':
                aug = self.scale_features(features, scale_factor=random.uniform(0.9, 1.1))
            elif method == 'noise_scale':
                # 组合噪声和缩放
                aug = self.add_noise(features, noise_level=random.uniform(0.01, 0.02))
                aug = self.scale_features(aug, scale_factor=random.uniform(0.95, 1.05))
            elif method == 'mixup' and other_features_pool is not None and len(other_features_pool) > 0:
                # 随机选择另一个样本进行混合
                other_idx = random.randint(0, len(other_features_pool) - 1)
                aug = self.mixup(features, other_features_pool[other_idx])
            else:
                # 如果mixup不可用，回退到噪声
                aug = self.add_noise(features, noise_level=random.uniform(0.01, 0.03))
            
            augmented_features.append(aug)
        
        return augmented_features


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
    
    # 分离特征和标签
    feature_cols = [col for col in df.columns if col.startswith('feature_')]
    label_col = 'action'
    
    logger.info(f"特征维度: {len(feature_cols)}")
    
    # 分析当前数据分布
    logger.info("\n当前数据分布:")
    action_counts = df[label_col].value_counts().sort_index()
    for action_id, count in action_counts.items():
        percentage = count / len(df) * 100
        logger.info(f"  动作 {action_id}: {count} 个样本 ({percentage:.1f}%)")
    
    # 初始化增强器
    augmenter = FeatureAugmenter()
    
    # 准备新数据列表
    new_rows = []
    
    # 对每个目标动作进行增强
    for action_id in target_actions:
        action_samples = df[df[label_col] == action_id]
        current_count = len(action_samples)
        
        if current_count >= target_samples_per_action:
            logger.info(f"\n动作 {action_id}: 已有 {current_count} 个样本，无需增强")
            continue
        
        needed_samples = target_samples_per_action - current_count
        logger.info(f"\n动作 {action_id}: 需要增强 {needed_samples} 个样本")
        
        # 提取特征向量
        features_array = action_samples[feature_cols].values
        
        # 计算每个原始样本需要生成多少个增强样本
        augmentations_per_sample = needed_samples // current_count + 1
        
        with tqdm(total=needed_samples, desc=f"增强动作 {action_id}") as pbar:
            generated_count = 0
            
            for idx in range(current_count):
                if generated_count >= needed_samples:
                    break
                
                original_features = features_array[idx]
                
                # 生成增强特征
                aug_features_list = augmenter.augment(
                    original_features,
                    other_features_pool=features_array,
                    num_augmentations=augmentations_per_sample
                )
                
                for aug_features in aug_features_list:
                    if generated_count >= needed_samples:
                        break
                    
                    # 创建新行
                    new_row = {label_col: action_id}
                    
                    # 添加特征列
                    for j, col in enumerate(feature_cols):
                        new_row[col] = aug_features[j]
                    
                    new_rows.append(new_row)
                    generated_count += 1
                    pbar.update(1)
        
        logger.info(f"  完成: 生成了 {generated_count} 个增强样本")
    
    # 合并原始数据和增强数据
    if new_rows:
        augmented_df = pd.DataFrame(new_rows)
        # 确保列顺序一致
        augmented_df = augmented_df[df.columns]
        final_df = pd.concat([df, augmented_df], ignore_index=True)
    else:
        final_df = df
    
    # 保存结果
    logger.info(f"\n保存增强后的数据集: {output_csv}")
    final_df.to_csv(output_csv, index=False)
    
    # 显示最终分布
    logger.info("\n增强后数据分布:")
    final_action_counts = final_df[label_col].value_counts().sort_index()
    total_samples = len(final_df)
    for action_id, count in final_action_counts.items():
        percentage = count / total_samples * 100
        logger.info(f"  动作 {action_id}: {count} 个样本 ({percentage:.1f}%)")
    
    logger.info(f"\n总样本数: {len(df)} -> {len(final_df)} (+{len(final_df) - len(df)})")
    
    # 显示改善情况
    if len(target_actions) > 0:
        logger.info("\n类别平衡改善:")
        for action_id in target_actions:
            old_count = action_counts.get(action_id, 0)
            new_count = final_action_counts.get(action_id, 0)
            old_pct = old_count / len(df) * 100
            new_pct = new_count / total_samples * 100
            logger.info(f"  动作 {action_id}: {old_pct:.2f}% -> {new_pct:.2f}% (增加 {new_count - old_count} 个样本)")


def main():
    parser = argparse.ArgumentParser(description='特征空间数据增强工具')
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
