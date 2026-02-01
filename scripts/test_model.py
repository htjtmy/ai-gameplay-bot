"""
测试训练好的Transformer模型

This script:
1. 加载训练好的模型
2. 测试模型预测功能
3. 评估模型在测试数据上的表现

Usage:
    python scripts/test_model.py --model "models/transformer/transformer_model.pth"
"""

import torch
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.transformer.transformer_model import GameplayTransformer


def load_model(model_path, input_size, output_size, num_heads=4, hidden_size=256, num_layers=3, device='cuda'):
    """加载训练好的模型"""
    logger.info(f"加载模型: {model_path}")
    logger.info(f"参数: input_size={input_size}, output_size={output_size}, num_heads={num_heads}, hidden_size={hidden_size}, num_layers={num_layers}")
    
    # 创建模型
    model = GameplayTransformer(
        input_size=input_size,
        output_size=output_size,
        num_heads=num_heads,
        hidden_size=hidden_size,
        num_layers=num_layers
    )
    
    # 加载权重
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model = model.to(device)
    model.eval()
    
    logger.info("✅ 模型加载成功")
    return model


def test_model_prediction(model, dataset_path, num_samples=10, device='cuda'):
    """测试模型预测"""
    logger.info(f"\n测试模型预测（{num_samples}个样本）...")
    
    # 加载数据集
    df = pd.read_csv(dataset_path)
    logger.info(f"数据集大小: {len(df)}")
    
    # 随机抽取样本
    samples = df.sample(n=min(num_samples, len(df)))
    
    # 分离特征和标签
    feature_cols = [col for col in df.columns if col.startswith('feature_')]
    X = samples[feature_cols].values.astype(np.float32)
    y_true = samples['action'].values
    
    # 转换为tensor
    X_tensor = torch.tensor(X, dtype=torch.float32).to(device)
    
    # 预测
    with torch.no_grad():
        outputs = model(X_tensor)
        _, predicted = torch.max(outputs, 1)
        predicted = predicted.cpu().numpy()
    
    # 显示结果
    logger.info("\n预测结果:")
    logger.info(f"{'样本':<6} {'真实动作':<10} {'预测动作':<10} {'置信度':<10} {'正确':<6}")
    logger.info("-" * 50)
    
    correct = 0
    for i in range(len(samples)):
        true_action = y_true[i]
        pred_action = predicted[i]
        confidence = torch.softmax(outputs[i], dim=0)[pred_action].item()
        is_correct = true_action == pred_action
        
        if is_correct:
            correct += 1
        
        status = "✓" if is_correct else "✗"
        logger.info(f"{i+1:<6} {true_action:<10} {pred_action:<10} {confidence*100:>6.2f}%   {status:<6}")
    
    accuracy = correct / len(samples) * 100
    logger.info(f"\n准确率: {correct}/{len(samples)} = {accuracy:.2f}%")
    
    return accuracy


def evaluate_model(model, dataset_path, batch_size=32, device='cuda'):
    """在整个数据集上评估模型"""
    logger.info(f"\n在完整数据集上评估模型...")
    
    # 加载数据集
    df = pd.read_csv(dataset_path)
    
    # 分离特征和标签
    feature_cols = [col for col in df.columns if col.startswith('feature_')]
    X = df[feature_cols].values.astype(np.float32)
    y_true = df['action'].values
    
    # 批量预测
    all_predictions = []
    num_batches = (len(X) + batch_size - 1) // batch_size
    
    logger.info(f"处理 {num_batches} 个批次...")
    
    with torch.no_grad():
        for i in range(0, len(X), batch_size):
            batch_X = torch.tensor(X[i:i+batch_size], dtype=torch.float32).to(device)
            outputs = model(batch_X)
            _, predicted = torch.max(outputs, 1)
            all_predictions.extend(predicted.cpu().numpy())
    
    # 计算准确率
    all_predictions = np.array(all_predictions)
    correct = (all_predictions == y_true).sum()
    total = len(y_true)
    accuracy = correct / total * 100
    
    logger.info(f"✅ 总体准确率: {correct}/{total} = {accuracy:.2f}%")
    
    # 按动作类别统计
    logger.info("\n各动作类别准确率:")
    unique_actions = np.unique(y_true)
    for action in unique_actions:
        mask = y_true == action
        action_correct = (all_predictions[mask] == y_true[mask]).sum()
        action_total = mask.sum()
        action_acc = action_correct / action_total * 100
        logger.info(f"  动作 {action}: {action_correct}/{action_total} = {action_acc:.2f}%")
    
    return accuracy


def main():
    parser = argparse.ArgumentParser(description='测试Transformer模型')
    parser.add_argument('--model', default='models/transformer/transformer_model.pth', help='模型路径')
    parser.add_argument('--dataset', default='data/processed/transformer_dataset_test.csv', help='测试数据集路径')
    parser.add_argument('--full-eval', action='store_true', help='在完整数据集上评估')
    parser.add_argument('--num-samples', type=int, default=10, help='测试样本数')
    parser.add_argument('--input-size', type=int, default=12288, help='输入特征维度')
    parser.add_argument('--output-size', type=int, default=25, help='输出类别数')
    parser.add_argument('--num-heads', type=int, default=4, help='注意力头数')
    parser.add_argument('--hidden-size', type=int, default=256, help='隐藏层大小')
    parser.add_argument('--num-layers', type=int, default=3, help='Transformer层数')
    
    args = parser.parse_args()
    
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"使用设备: {device}")
    
    # 加载模型
    model = load_model(
        args.model,
        args.input_size,
        args.output_size,
        args.num_heads,
        args.hidden_size,
        args.num_layers,
        device
    )
    
    # 测试预测
    test_model_prediction(model, args.dataset, args.num_samples, device)
    
    # 完整评估（如果指定）
    if args.full_eval:
        evaluate_model(model, args.dataset, device=device)


if __name__ == "__main__":
    main()
