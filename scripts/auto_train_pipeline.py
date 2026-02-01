"""
自动化训练流水线
在用户离开期间自动完成：数据增强 → 训练 → 评估

Usage:
    python scripts/auto_train_pipeline.py
"""

import subprocess
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
import json

# 配置日志
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = log_dir / f"auto_train_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_command(command, description, timeout=None):
    """
    运行命令并记录输出
    
    Args:
        command: 要执行的命令
        description: 命令描述
        timeout: 超时时间（秒），None表示不限制
    
    Returns:
        bool: 是否成功
    """
    logger.info("=" * 80)
    logger.info(f"开始: {description}")
    logger.info(f"命令: {command}")
    logger.info("=" * 80)
    
    start_time = time.time()
    
    try:
        # 在PowerShell中运行，激活conda环境
        full_command = f'conda activate Ai-Gameplay-Bot; {command}'
        
        result = subprocess.run(
            ["powershell", "-Command", full_command],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=timeout
        )
        
        elapsed = time.time() - start_time
        
        # 记录输出
        if result.stdout:
            logger.info(f"标准输出:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"标准错误:\n{result.stderr}")
        
        if result.returncode == 0:
            logger.info(f"✅ 成功完成: {description} (耗时: {elapsed:.1f}秒)")
            return True
        else:
            logger.error(f"❌ 失败: {description} (返回码: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        logger.error(f"⏱️ 超时: {description} (超过 {timeout}秒)")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ 异常: {description} - {str(e)}")
        return False


def main():
    """主流程"""
    pipeline_start = time.time()
    
    logger.info("🚀 自动化训练流水线启动")
    logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"日志文件: {log_file}")
    logger.info("")
    
    # 定义流水线步骤
    steps = []
    
    # ========== 步骤1: 数据增强 ==========
    steps.append({
        'name': '数据增强',
        'command': (
            'python scripts/augment_minority_classes.py '
            '--input "data/processed/transformer_dataset.csv" '
            '--output "data/processed/transformer_dataset_augmented.csv" '
            '--target-actions 4 5 '
            '--target-samples 1000'
        ),
        'timeout': 3600,  # 1小时超时
        'critical': True  # 关键步骤，失败则停止
    })
    
    # ========== 步骤2: 训练模型 ==========
    steps.append({
        'name': '训练模型（使用类别权重）',
        'command': (
            'python models/transformer/transformer_training.py '
            '--dataset "data/processed/transformer_dataset_augmented.csv" '
            '--epochs 100 '
            '--num-classes 25 '
            '--batch-size 16 '
            '--lr 0.0001 '
            '--use-class-weights '
            '--early-stopping 15'
        ),
        'timeout': 28800,  # 8小时超时
        'critical': True
    })
    
    # ========== 步骤3: 评估模型（完整评估）==========
    steps.append({
        'name': '评估模型',
        'command': (
            'python scripts/test_model.py '
            '--model "models/transformer/transformer_model.pth" '
            '--dataset "data/processed/transformer_dataset_test.csv" '
            '--full-eval'
        ),
        'timeout': 600,  # 10分钟超时
        'critical': False
    })
    
    # ========== 步骤4: 备份模型 ==========
    backup_name = f"transformer_model_backup_{timestamp}.pth"
    steps.append({
        'name': '备份模型',
        'command': (
            f'Copy-Item "models/transformer/transformer_model.pth" '
            f'"models/transformer/{backup_name}" -Force'
        ),
        'timeout': 60,
        'critical': False
    })
    
    # 执行所有步骤
    results = []
    for i, step in enumerate(steps, 1):
        logger.info(f"\n\n{'='*80}")
        logger.info(f"步骤 {i}/{len(steps)}: {step['name']}")
        logger.info(f"{'='*80}\n")
        
        success = run_command(
            command=step['command'],
            description=step['name'],
            timeout=step.get('timeout')
        )
        
        results.append({
            'step': step['name'],
            'success': success,
            'critical': step['critical']
        })
        
        if not success and step['critical']:
            logger.error(f"\n❌ 关键步骤失败: {step['name']}")
            logger.error("流水线中止！")
            break
        
        # 步骤之间休息5秒
        if i < len(steps):
            time.sleep(5)
    
    # 生成总结报告
    pipeline_end = time.time()
    total_time = pipeline_end - pipeline_start
    
    logger.info("\n\n" + "="*80)
    logger.info("📊 流水线执行总结")
    logger.info("="*80)
    logger.info(f"开始时间: {datetime.fromtimestamp(pipeline_start).strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"结束时间: {datetime.fromtimestamp(pipeline_end).strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"总耗时: {total_time/3600:.2f} 小时 ({total_time/60:.1f} 分钟)")
    logger.info("")
    
    logger.info("步骤执行结果:")
    for i, result in enumerate(results, 1):
        status = "✅ 成功" if result['success'] else "❌ 失败"
        critical = " [关键]" if result['critical'] else ""
        logger.info(f"  {i}. {result['step']}: {status}{critical}")
    
    # 统计成功率
    total_steps = len(results)
    successful_steps = sum(1 for r in results if r['success'])
    success_rate = successful_steps / total_steps * 100 if total_steps > 0 else 0
    
    logger.info(f"\n成功率: {successful_steps}/{total_steps} ({success_rate:.1f}%)")
    
    # 生成JSON报告
    report = {
        'start_time': datetime.fromtimestamp(pipeline_start).isoformat(),
        'end_time': datetime.fromtimestamp(pipeline_end).isoformat(),
        'total_time_seconds': total_time,
        'total_time_hours': total_time / 3600,
        'steps': results,
        'success_rate': success_rate,
        'log_file': str(log_file)
    }
    
    report_file = log_dir / f"auto_train_report_{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n详细报告已保存到: {report_file}")
    logger.info(f"完整日志已保存到: {log_file}")
    
    # 最终状态
    if successful_steps == total_steps:
        logger.info("\n🎉 所有步骤成功完成！")
        logger.info("\n下一步:")
        logger.info("1. 查看评估结果，确认模型性能")
        logger.info("2. 使用 real_time_controller.py 在游戏中测试")
        logger.info("3. 根据实际表现调整参数")
        return 0
    else:
        logger.warning(f"\n⚠️ 有 {total_steps - successful_steps} 个步骤失败")
        logger.warning("请检查日志文件了解详情")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️ 用户中断流水线")
        sys.exit(2)
    except Exception as e:
        logger.error(f"\n\n❌ 流水线异常: {str(e)}", exc_info=True)
        sys.exit(3)
