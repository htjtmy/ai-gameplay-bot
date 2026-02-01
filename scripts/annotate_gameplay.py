"""
Gameplay Annotation Tool - 将录制的输入转换为动作标注

This script:
1. 读取 inputs.jsonl（录制的原始输入）
2. 根据 game_actions.json 配置，将输入映射到动作
3. 生成帧级别的动作标注 CSV
4. 为每一帧指定当前执行的动作ID

Usage:
    python scripts/annotate_gameplay.py --video-dir "data/raw/gameplay_videos/护送/委托_妮弗尔夫人"
"""

import json
import argparse
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, List, Set

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_action_config(config_path="config/game_actions.json"):
    """加载游戏动作配置"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


def load_inputs(inputs_path):
    """加载录制的输入事件"""
    inputs = []
    with open(inputs_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                inputs.append(json.loads(line))
    return inputs


def create_key_to_action_mapping(config):
    """创建键位到动作的映射表"""
    mapping = {}
    
    for action in config["actions"]:
        action_id = action["id"]
        action_name = action["name"]
        
        for key_combo in action["keys"]:
            if isinstance(key_combo, list) and len(key_combo) == 2:
                key_type, key_value = key_combo
                
                if key_type == "keyboard":
                    mapping[f"key:{key_value}"] = {
                        "id": action_id,
                        "name": action_name
                    }
                elif key_type == "mouse":
                    mapping[f"mouse:{key_value}"] = {
                        "id": action_id,
                        "name": action_name
                    }
                elif key_type in ["alt", "ctrl", "shift"]:
                    # 修饰键
                    mapping[f"key:{key_value}"] = {
                        "id": action_id,
                        "name": action_name
                    }
    
    return mapping


def normalize_input_key(input_event):
    """标准化输入事件的键名"""
    event_type = input_event["type"]
    
    if event_type in ["key_press", "key_release"]:
        key = input_event["key"]
        return f"key:{key}"
    elif event_type in ["mouse_press", "mouse_release"]:
        button = input_event["button"]
        return f"mouse:{button}"
    
    return None


def map_inputs_to_actions(inputs, key_to_action_mapping, fps=30):
    """将输入事件映射到每帧的动作"""
    # 跟踪当前按下的按键
    active_keys: Set[str] = set()
    
    # 每帧的动作列表 (frame_number -> set of action_ids)
    frame_actions: Dict[int, Set[int]] = {}
    
    for event in inputs:
        frame_num = event["frame"]
        event_type = event["type"]
        
        # 初始化该帧的动作集合
        if frame_num not in frame_actions:
            frame_actions[frame_num] = set()
        
        # 处理按键事件
        if event_type == "key_press":
            key_id = normalize_input_key(event)
            if key_id and key_id in key_to_action_mapping:
                action_info = key_to_action_mapping[key_id]
                active_keys.add(key_id)
                frame_actions[frame_num].add(action_info["id"])
        
        elif event_type == "key_release":
            key_id = normalize_input_key(event)
            if key_id in active_keys:
                active_keys.discard(key_id)
        
        # 处理鼠标点击（通常是瞬时动作）
        elif event_type == "mouse_press":
            key_id = normalize_input_key(event)
            if key_id and key_id in key_to_action_mapping:
                action_info = key_to_action_mapping[key_id]
                frame_actions[frame_num].add(action_info["id"])
        
        # 将当前活动的按键状态传递到下一帧
        if active_keys:
            for key_id in active_keys:
                if key_id in key_to_action_mapping:
                    action_info = key_to_action_mapping[key_id]
                    frame_actions[frame_num].add(action_info["id"])
    
    return frame_actions


def generate_annotations_csv(frame_actions, total_frames, output_path, fps=30):
    """生成标注CSV文件"""
    annotations = []
    
    for frame_num in range(total_frames):
        # 获取该帧的动作（如果没有则为空动作0）
        actions = frame_actions.get(frame_num, set())
        
        # 如果有多个动作，选择最主要的一个（这里简单选择ID最小的）
        # TODO: 可以改进为多标签分类
        if actions:
            primary_action = min(actions)
        else:
            primary_action = 0  # 0 表示无动作或继续上一个动作
        
        timestamp_ms = int((frame_num / fps) * 1000)
        
        annotations.append({
            "frame": frame_num,
            "timestamp_ms": timestamp_ms,
            "action_id": primary_action,
            "all_actions": ",".join(map(str, sorted(actions))) if actions else "0"
        })
    
    df = pd.DataFrame(annotations)
    df.to_csv(output_path, index=False, encoding='utf-8')
    logger.info(f"生成标注文件: {output_path}")
    logger.info(f"总帧数: {total_frames}, 包含动作的帧数: {len([a for a in annotations if a['action_id'] > 0])}")
    
    return df


def process_recording(video_dir, config_path="config/game_actions.json"):
    """处理单个录制会话"""
    video_dir = Path(video_dir)
    
    # 查找该目录下的所有录制文件
    recordings = list(video_dir.glob("**/inputs_*.jsonl"))
    if not recordings and (video_dir / "inputs.jsonl").exists():
        recordings = [video_dir / "inputs.jsonl"]
    
    if not recordings:
        logger.error(f"未找到输入文件: {video_dir}")
        return
    
    # 加载配置
    config = load_action_config(config_path)
    key_to_action_mapping = create_key_to_action_mapping(config)
    
    logger.info(f"动作映射表包含 {len(key_to_action_mapping)} 个键位")
    
    for inputs_path in recordings:
        logger.info(f"\n处理: {inputs_path}")
        
        # 查找对应的 metadata
        metadata_path = inputs_path.parent / inputs_path.name.replace("inputs_", "metadata_").replace(".jsonl", ".json")
        if not metadata_path.exists():
            metadata_path = inputs_path.parent / "metadata.json"
        
        if not metadata_path.exists():
            logger.warning(f"未找到元数据文件: {metadata_path}")
            continue
        
        # 加载元数据
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        total_frames = metadata.get("total_frames", 0)
        fps = metadata.get("video_fps", 30)
        
        logger.info(f"视频信息: {total_frames} 帧, {fps} FPS")
        
        # 加载输入
        inputs = load_inputs(inputs_path)
        logger.info(f"加载了 {len(inputs)} 个输入事件")
        
        if metadata.get("input_statistics"):
            logger.info(f"输入统计: {metadata['input_statistics']}")
        
        # 映射输入到动作
        frame_actions = map_inputs_to_actions(inputs, key_to_action_mapping, fps)
        
        # 生成标注文件
        annotations_path = inputs_path.parent / inputs_path.name.replace("inputs_", "annotations_").replace(".jsonl", ".csv")
        generate_annotations_csv(frame_actions, total_frames, annotations_path, fps)


def main():
    parser = argparse.ArgumentParser(
        description="将录制的输入转换为动作标注",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理单个录制目录
  python scripts/annotate_gameplay.py --video-dir "data/raw/gameplay_videos/护送/委托_妮弗尔夫人"
  
  # 批量处理所有录制
  python scripts/annotate_gameplay.py --video-dir "data/raw/gameplay_videos" --recursive
        """
    )
    
    parser.add_argument(
        "--video-dir",
        required=True,
        help="录制视频的目录"
    )
    parser.add_argument(
        "--config",
        default="config/game_actions.json",
        help="游戏动作配置文件路径"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="递归处理所有子目录"
    )
    
    args = parser.parse_args()
    
    video_dir = Path(args.video_dir)
    
    if args.recursive:
        # 查找所有包含 inputs 文件的目录
        all_dirs = set()
        for inputs_file in video_dir.rglob("inputs*.jsonl"):
            all_dirs.add(inputs_file.parent)
        
        logger.info(f"找到 {len(all_dirs)} 个录制目录")
        
        for directory in sorted(all_dirs):
            try:
                process_recording(directory, args.config)
            except Exception as e:
                logger.error(f"处理 {directory} 时出错: {e}")
    else:
        process_recording(video_dir, args.config)


if __name__ == "__main__":
    main()
