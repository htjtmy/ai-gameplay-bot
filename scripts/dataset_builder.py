import pandas as pd
import numpy as np
import os
import cv2
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_image_features(image_path, target_size=(224, 224)):
    """
    从图像中提取特征 / Extract features from an image.
    
    参数 Args:
        image_path (str): 图像文件路径 / Path to the image file
        target_size (tuple): 目标大小 / Target size for resizing
    
    返回 Returns:
        numpy.ndarray: 扁平化的图像特征 / Flattened image features
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            logger.warning(f"Failed to read image: {image_path}")
            return np.zeros(target_size[0] * target_size[1] // 64)  # 返回虚拟特征 / Return dummy features

        # 调整大小并归一化 / Resize and normalize
        img = cv2.resize(img, target_size)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 下采样以获得特征向量 / Downsample for feature vector
        img = cv2.resize(img, (target_size[0] // 8, target_size[1] // 8))
        features = img.flatten() / 255.0

        return features
    except Exception as e:
        logger.error(f"Error extracting features from {image_path}: {e}")
        return np.zeros(target_size[0] * target_size[1] // 64)


def map_action_to_index(action_str):
    """
    将动作字符串映射到索引 / Map action string to index.
    
    参数 Args:
        action_str (str): 动作字符串 / Action string
    
    返回 Returns:
        int: 动作索引 / Action index
    """
    action_mapping = {
        "move_forward": 0,
        "move_backward": 1,
        "turn_left": 2,
        "turn_right": 3,
        "melee_attack": 4,
        "ranged_attack": 5,
        "lock_target": 6,
        "combat_skill": 7,
        "ultimate_skill": 8,
        "jump": 9,
        "slide": 10,
        "dodge": 11,
        "helix_leap": 12,
        "reload": 13,
        "interact": 14,
        "inventory": 15,
        "map": 16,
        "combat": 17,
        "armoury": 18,
        "revive": 19,
        "menu": 20,
        "geniemon": 21,
        "navigate": 22,
        "quests": 23,
        "quit_challenge": 24,
        "look_x": 25,
        "look_y": 26
    }
    action = action_str.lower().strip()
    if action not in action_mapping:
        logger.warning(f"Unknown action '{action_str}' will be skipped")
        return None
    return action_mapping[action]


def build_dataset(frames_dir, actions_file, output_file, extract_features=True):
    """
    Build a dataset from extracted frames and mapped actions.
    Args:
        frames_dir (str): Directory containing extracted frames.
        actions_file (str): Path to the file containing actions.
        output_file (str): Path to save the resulting dataset.
        extract_features (bool): Whether to extract image features or just save paths
    """
    logger.info(f"Building dataset from {frames_dir}")

    frames = sorted([os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith(".jpg")])
    actions = []

    with open(actions_file, "r") as f:
        actions = [line.strip() for line in f.readlines()]

    if len(frames) != len(actions):
        logger.warning(f"Frame count ({len(frames)}) != action count ({len(actions)})")
        # Truncate to minimum length
        min_len = min(len(frames), len(actions))
        frames = frames[:min_len]
        actions = actions[:min_len]

    if extract_features:
        logger.info("Extracting features from frames...")
        features_list = []
        action_indices = []

        for frame_path, action in tqdm(zip(frames, actions), total=len(frames)):
            features = extract_image_features(frame_path)
            action_idx = map_action_to_index(action)

            features_list.append(features)
            action_indices.append(action_idx)

        # Create DataFrame with features
        features_array = np.array(features_list)
        data = {f"feature_{i}": features_array[:, i] for i in range(features_array.shape[1])}
        data["action"] = action_indices

        df = pd.DataFrame(data)
    else:
        # Simple dataset with paths
        action_indices = [map_action_to_index(a) for a in actions]
        data = {
            "frame": frames,
            "action": action_indices
        }
        df = pd.DataFrame(data)

    # Save dataset
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    logger.info(f"Dataset saved to {output_file} ({len(df)} samples)")

if __name__ == "__main__":
    frames_dir = "data/processed/frames"
    actions_file = "data/raw/annotations/actions.txt"
    output_file = "data/processed/transformer_dataset.csv"
    build_dataset(frames_dir, actions_file, output_file)
