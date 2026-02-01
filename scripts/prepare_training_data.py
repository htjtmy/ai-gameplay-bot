"""
准备训练数据 - 从录制视频提取帧并与标注配对

This script:
1. 从视频中提取帧（可选采样率）
2. 读取对应的标注文件
3. 生成训练集 CSV：帧路径 + 动作ID
4. 可选：提取图像特征向量

Usage:
    python scripts/prepare_training_data.py --video-dir "data/raw/gameplay_videos" --output "data/processed"
"""

import cv2
import json
import argparse
import pandas as pd
from pathlib import Path
import logging
import numpy as np
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_frames_from_video(video_path, output_dir, frame_skip=1, max_frames=None):
    """
    从视频提取帧
    
    Args:
        video_path: 视频文件路径
        output_dir: 输出目录
        frame_skip: 跳帧数（1=每帧，2=每2帧取1帧）
        max_frames: 最大提取帧数
    
    Returns:
        提取的帧数
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        logger.error(f"无法打开视频: {video_path}")
        return 0
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    logger.info(f"视频: {video_path.name}")
    logger.info(f"总帧数: {total_frames}, FPS: {fps}")
    
    frame_count = 0
    saved_count = 0
    
    pbar = tqdm(total=min(total_frames, max_frames or total_frames), desc="提取帧")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 跳帧
        if frame_count % frame_skip == 0:
            frame_path = output_dir / f"frame_{frame_count:06d}.jpg"
            # 压缩质量设置为85以节省空间
            cv2.imwrite(str(frame_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            saved_count += 1
            
            if max_frames and saved_count >= max_frames:
                break
        
        frame_count += 1
        pbar.update(1)
    
    pbar.close()
    cap.release()
    
    logger.info(f"提取了 {saved_count}/{frame_count} 帧")
    return saved_count


def match_frames_with_annotations(frames_dir, annotations_path, frame_skip=1):
    """
    将提取的帧与标注配对
    
    Args:
        frames_dir: 帧目录
        annotations_path: 标注CSV路径
        frame_skip: 跳帧数（需与提取帧时一致）
    
    Returns:
        DataFrame: frame_path, action_id
    """
    frames_dir = Path(frames_dir)
    
    # 读取标注
    annotations = pd.read_csv(annotations_path)
    
    # 构建数据集
    dataset = []
    
    for _, row in annotations.iterrows():
        frame_num = int(row['frame'])
        
        # 只处理被提取的帧
        if frame_num % frame_skip != 0:
            continue
        
        frame_path = frames_dir / f"frame_{frame_num:06d}.jpg"
        
        if frame_path.exists():
            dataset.append({
                'frame_path': str(frame_path.relative_to(Path.cwd())),
                'action_id': int(row['action_id']),
                'timestamp_ms': int(row['timestamp_ms']),
                'frame': int(frame_num)
            })
    
    return pd.DataFrame(dataset)


def process_recording(recording_dir, output_base_dir, frame_skip=2, max_frames_per_video=None):
    """
    处理单个录制会话
    
    Args:
        recording_dir: 录制目录
        output_base_dir: 输出基础目录
        frame_skip: 跳帧数
        max_frames_per_video: 每个视频最大提取帧数
    
    Returns:
        处理的视频数
    """
    recording_dir = Path(recording_dir)
    output_base_dir = Path(output_base_dir)
    
    # 查找视频和标注文件
    video_files = list(recording_dir.glob("gameplay*.mp4"))
    
    if not video_files:
        logger.warning(f"未找到视频文件: {recording_dir}")
        return 0
    
    processed = 0
    all_datasets = []
    
    for video_path in video_files:
        # 查找对应的标注文件
        timestamp = video_path.stem.replace("gameplay_", "")
        if timestamp == "gameplay":
            timestamp = ""
        
        if timestamp:
            annotations_path = recording_dir / f"annotations_{timestamp}.csv"
        else:
            annotations_path = recording_dir / "annotations.csv"
        
        # 兼容旧格式
        if not annotations_path.exists():
            annotations_path = recording_dir / "inputs.csv"
        
        if not annotations_path.exists():
            logger.warning(f"未找到标注文件: {annotations_path}")
            continue
        
        logger.info(f"\n{'='*60}")
        logger.info(f"处理: {video_path.relative_to(Path.cwd())}")
        
        # 创建输出目录
        relative_path = recording_dir.relative_to(Path("data/raw/gameplay_videos"))
        frames_output_dir = output_base_dir / "frames" / relative_path / timestamp
        
        # 提取帧
        saved_frames = extract_frames_from_video(
            video_path,
            frames_output_dir,
            frame_skip=frame_skip,
            max_frames=max_frames_per_video
        )
        
        if saved_frames == 0:
            continue
        
        # 配对标注
        logger.info("配对标注...")
        dataset = match_frames_with_annotations(
            frames_output_dir,
            annotations_path,
            frame_skip=frame_skip
        )
        
        logger.info(f"生成了 {len(dataset)} 条训练样本")
        
        # 统计动作分布
        action_counts = dataset['action_id'].value_counts().sort_index()
        logger.info(f"动作分布: {dict(action_counts.head(10))}")
        
        all_datasets.append(dataset)
        processed += 1
    
    # 合并所有数据集
    if all_datasets:
        combined_dataset = pd.concat(all_datasets, ignore_index=True)
        
        # 保存合并的数据集
        session_name = recording_dir.relative_to(Path("data/raw/gameplay_videos"))
        output_csv = output_base_dir / "datasets" / f"{str(session_name).replace(chr(92), '_')}_dataset.csv"
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        
        combined_dataset.to_csv(output_csv, index=False, encoding='utf-8')
        logger.info(f"\n保存数据集: {output_csv}")
        logger.info(f"总样本数: {len(combined_dataset)}")
    
    return processed


def main():
    parser = argparse.ArgumentParser(
        description="准备训练数据：提取视频帧并与标注配对",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理单个录制会话
  python scripts/prepare_training_data.py --video-dir "data/raw/gameplay_videos/护送/委托_妮弗尔夫人" --output "data/processed"
  
  # 批量处理（每2帧取1帧）
  python scripts/prepare_training_data.py --video-dir "data/raw/gameplay_videos" --output "data/processed" --frame-skip 2 --recursive
  
  # 快速测试（每个视频最多1000帧）
  python scripts/prepare_training_data.py --video-dir "data/raw/gameplay_videos" --output "data/processed" --frame-skip 5 --max-frames 1000 --recursive
        """
    )
    
    parser.add_argument(
        "--video-dir",
        required=True,
        help="录制视频的目录"
    )
    parser.add_argument(
        "--output",
        default="data/processed",
        help="输出目录（默认: data/processed）"
    )
    parser.add_argument(
        "--frame-skip",
        type=int,
        default=2,
        help="跳帧数（1=每帧，2=每2帧取1帧，默认: 2）"
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        help="每个视频最大提取帧数（用于快速测试）"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="递归处理所有子目录"
    )
    
    args = parser.parse_args()
    
    video_dir = Path(args.video_dir)
    
    if args.recursive:
        # 查找所有包含视频的目录
        all_dirs = set()
        for video_file in video_dir.rglob("gameplay*.mp4"):
            all_dirs.add(video_file.parent)
        
        logger.info(f"找到 {len(all_dirs)} 个录制目录")
        
        total_processed = 0
        for directory in sorted(all_dirs):
            try:
                processed = process_recording(
                    directory,
                    args.output,
                    frame_skip=args.frame_skip,
                    max_frames_per_video=args.max_frames
                )
                total_processed += processed
            except Exception as e:
                logger.error(f"处理 {directory} 时出错: {e}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"总共处理了 {total_processed} 个视频")
    else:
        process_recording(
            video_dir,
            args.output,
            frame_skip=args.frame_skip,
            max_frames_per_video=args.max_frames
        )


if __name__ == "__main__":
    main()
