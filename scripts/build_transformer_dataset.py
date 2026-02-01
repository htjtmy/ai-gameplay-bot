"""
构建Transformer训练数据集 - 从图像帧提取特征并生成训练CSV

This script:
1. 读取所有数据集CSV（帧路径 + 动作ID）
2. 从图像中提取特征向量
3. 生成Transformer训练所需的CSV格式（特征列 + action列）

Usage:
    python scripts/build_transformer_dataset.py --input "data/processed/datasets/*.csv" --output "data/processed/transformer_dataset.csv"
"""

import cv2
import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import logging
from tqdm import tqdm
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_image_features(image_path, target_size=(84, 84)):
    """
    从图像提取特征向量
    
    Args:
        image_path: 图像路径
        target_size: 目标尺寸
    
    Returns:
        扁平化的特征向量
    """
    try:
        # OpenCV中文路径问题，使用numpy加载
        img_array = np.fromfile(str(image_path), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.warning(f"无法读取图像: {image_path}")
            return np.zeros(target_size[0] * target_size[1] * 3, dtype=np.float32)
        
        # 调整大小
        img = cv2.resize(img, target_size)
        
        # 归一化到 [0, 1]
        img = img.astype(np.float32) / 255.0
        
        # 扁平化
        features = img.flatten()
        
        return features
    
    except Exception as e:
        logger.error(f"提取特征失败 {image_path}: {e}")
        return np.zeros(target_size[0] * target_size[1] * 3, dtype=np.float32)


def build_dataset(dataset_paths, output_path, target_size=(84, 84), max_samples=None):
    """
    构建Transformer训练数据集
    
    Args:
        dataset_paths: 数据集CSV路径列表（或glob模式）
        output_path: 输出CSV路径
        target_size: 图像目标尺寸
        max_samples: 最大样本数（用于测试）
    """
    # 收集所有CSV文件
    if isinstance(dataset_paths, str):
        csv_files = glob.glob(dataset_paths)
    else:
        csv_files = dataset_paths
    
    logger.info(f"找到 {len(csv_files)} 个数据集文件")
    
    # 读取所有数据集
    all_data = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        all_data.append(df)
        logger.info(f"加载 {Path(csv_file).name}: {len(df)} 条样本")
    
    combined_df = pd.concat(all_data, ignore_index=True)
    logger.info(f"总样本数: {len(combined_df)}")
    
    # 限制样本数（如果指定）
    if max_samples and len(combined_df) > max_samples:
        logger.info(f"限制样本数到 {max_samples}")
        combined_df = combined_df.sample(n=max_samples, random_state=42)
    
    # 统计动作分布
    action_dist = combined_df['action_id'].value_counts().sort_index()
    logger.info(f"动作分布:\n{action_dist}")
    
    # 提取特征
    feature_dim = target_size[0] * target_size[1] * 3
    logger.info(f"特征维度: {feature_dim}")
    
    features_list = []
    actions_list = []
    
    logger.info("开始提取图像特征...")
    for idx, row in tqdm(combined_df.iterrows(), total=len(combined_df), desc="提取特征"):
        frame_path = Path(row['frame_path'])
        action_id = int(row['action_id'])
        
        # 提取特征
        features = extract_image_features(frame_path, target_size)
        
        features_list.append(features)
        actions_list.append(action_id)
    
    # 构建DataFrame
    logger.info("构建特征DataFrame...")
    features_array = np.array(features_list)
    
    # 创建列名：feature_0, feature_1, ..., feature_N, action
    feature_columns = [f'feature_{i}' for i in range(feature_dim)]
    
    # 构建DataFrame
    df_features = pd.DataFrame(features_array, columns=feature_columns)
    df_features['action'] = actions_list
    
    # 保存
    logger.info(f"保存到: {output_path}")
    df_features.to_csv(output_path, index=False)
    
    logger.info(f"数据集构建完成！")
    logger.info(f"形状: {df_features.shape}")
    logger.info(f"动作分布:\n{df_features['action'].value_counts().sort_index()}")
    
    return df_features


def main():
    parser = argparse.ArgumentParser(
        description="构建Transformer训练数据集",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 构建完整数据集
  python scripts/build_transformer_dataset.py --input "data/processed/datasets/*.csv" --output "data/processed/transformer_dataset.csv"
  
  # 快速测试（只用1000个样本）
  python scripts/build_transformer_dataset.py --input "data/processed/datasets/*.csv" --output "data/processed/transformer_dataset_test.csv" --max-samples 1000
  
  # 指定图像尺寸
  python scripts/build_transformer_dataset.py --input "data/processed/datasets/*.csv" --output "data/processed/transformer_dataset.csv" --image-size 64
        """
    )
    
    parser.add_argument(
        "--input",
        required=True,
        help="输入数据集CSV路径（支持glob模式，如 'data/processed/datasets/*.csv'）"
    )
    parser.add_argument(
        "--output",
        default="data/processed/transformer_dataset.csv",
        help="输出CSV路径（默认: data/processed/transformer_dataset.csv）"
    )
    parser.add_argument(
        "--image-size",
        type=int,
        default=84,
        help="图像目标尺寸（默认: 84x84）"
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        help="最大样本数（用于快速测试）"
    )
    
    args = parser.parse_args()
    
    target_size = (args.image_size, args.image_size)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    build_dataset(
        args.input,
        output_path,
        target_size=target_size,
        max_samples=args.max_samples
    )


if __name__ == "__main__":
    main()
