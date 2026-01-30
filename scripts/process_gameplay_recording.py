"""
Process Gameplay Recording - Converts recorded video and inputs into training dataset

This script:
1. Extracts frames from recorded video
2. Maps recorded inputs (keyboard/mouse) to frames
3. Creates training dataset CSV with frame-to-action mapping
4. Generates action annotations file

Usage:
    python scripts/process_gameplay_recording.py --session 20250125_120000
    python scripts/process_gameplay_recording.py --session 20250125_120000 --output my_dataset
"""

import cv2
import json
import logging
import argparse
import os
import numpy as np
from pathlib import Path
from tqdm import tqdm
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Map keyboard/mouse inputs to game actions
INPUT_TO_ACTION_MAP = {
    # Movement
    'w': 'move_forward',
    'a': 'move_left',
    's': 'move_backward',
    'd': 'move_right',
    
    # Turning
    'q': 'turn_left',
    'e': 'turn_right',
    'left': 'turn_left',
    'right': 'turn_right',
    
    # Camera/Looking (mouse movement)
    'mouse_move': ('look_x', 'look_y'),
    
    # Combat
    'left_click': 'melee_attack',
    'right_click': 'ranged_attack',
    'space': 'jump',
    'shift': 'dodge',
    'ctrl': 'slide',
    'c': 'combat_skill',
    'x': 'ultimate_skill',
    'r': 'reload',
    
    # Interaction
    'f': 'interact',
    'i': 'inventory',
    'm': 'map',
    'p': 'menu',
    'l': 'lock_target',
    't': 'geniemon',
    'q_hold': 'revive',
}


class GameplayProcessor:
    """Process recorded gameplay into training dataset."""
    
    def __init__(self, session_dir, output_dir=None):
        """
        Initialize processor.
        
        Args:
            session_dir (str): Path to session directory containing video and inputs
            output_dir (str): Where to save processed data (default: data/processed)
        """
        self.session_dir = Path(session_dir)
        self.output_dir = Path(output_dir or "data/processed")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Session files
        self.video_path = self.session_dir / "gameplay.mp4"
        self.inputs_path = self.session_dir / "inputs.jsonl"
        self.metadata_path = self.session_dir / "metadata.json"
        
        # Output files
        self.frames_dir = self.output_dir / f"frames_{self.session_dir.name}"
        self.actions_file = self.output_dir / f"actions_{self.session_dir.name}.txt"
        self.dataset_file = self.output_dir / f"dataset_{self.session_dir.name}.csv"
        self.mapping_file = self.output_dir / f"mapping_{self.session_dir.name}.json"
        
        self.frames_dir.mkdir(exist_ok=True)
        
        # Data
        self.frames = []
        self.inputs = []
        self.actions = []
        self.frame_timestamps = []
        
        logger.info(f"Processing session: {self.session_dir.name}")
        logger.info(f"Video: {self.video_path}")
        logger.info(f"Inputs: {self.inputs_path}")
    
    def load_metadata(self):
        """Load metadata."""
        if not self.metadata_path.exists():
            logger.warning(f"Metadata file not found: {self.metadata_path}")
            return
        
        with open(self.metadata_path, 'r') as f:
            metadata = json.load(f)
        
        logger.info(f"Duration: {metadata['duration_seconds']:.1f}s")
        logger.info(f"Video FPS: {metadata['video_fps']}")
        logger.info(f"Total inputs: {metadata['total_inputs']}")
        
        return metadata
    
    def extract_frames(self, skip_frames=1):
        """
        Extract frames from video.
        
        Args:
            skip_frames (int): Extract every nth frame (default: 1 = extract all)
        """
        logger.info(f"Extracting frames from video...")
        
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {self.video_path}")
        
        cap = cv2.VideoCapture(str(self.video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Video FPS: {fps}, Total frames: {total_frames}")
        
        frame_count = 0
        extracted_count = 0
        
        with tqdm(total=total_frames, desc="Extracting frames") as pbar:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % skip_frames == 0:
                    frame_path = self.frames_dir / f"frame_{extracted_count:06d}.jpg"
                    cv2.imwrite(str(frame_path), frame)
                    
                    timestamp_ms = (frame_count / fps) * 1000
                    self.frames.append(str(frame_path))
                    self.frame_timestamps.append(timestamp_ms)
                    extracted_count += 1
                
                frame_count += 1
                pbar.update(1)
        
        cap.release()
        logger.info(f"Extracted {extracted_count} frames")
        return extracted_count
    
    def load_inputs(self):
        """Load recorded inputs from JSONL file."""
        logger.info("Loading recorded inputs...")
        
        if not self.inputs_path.exists():
            raise FileNotFoundError(f"Inputs file not found: {self.inputs_path}")
        
        with open(self.inputs_path, 'r') as f:
            for line in f:
                input_event = json.loads(line.strip())
                self.inputs.append(input_event)
        
        logger.info(f"Loaded {len(self.inputs)} input events")
        return len(self.inputs)
    
    def map_inputs_to_frames(self):
        """
        Map input events to frames.
        Creates action sequence based on recorded inputs.
        """
        logger.info("Mapping inputs to frames...")
        
        # Initialize actions for each frame
        self.actions = ['idle'] * len(self.frames)
        
        # Track which keys are currently pressed
        pressed_keys = set()
        
        for i, frame_timestamp in enumerate(self.frame_timestamps):
            current_actions = []
            
            # Find all inputs that affect this frame
            for input_event in self.inputs:
                event_time = input_event['timestamp']
                
                # Look ahead up to next frame's timestamp
                next_frame_time = self.frame_timestamps[i + 1] if i + 1 < len(self.frame_timestamps) else frame_timestamp + 100
                
                if frame_timestamp <= event_time < next_frame_time:
                    current_actions.append(input_event)
            
            # Determine the primary action for this frame
            action = self._determine_action(current_actions, pressed_keys)
            self.actions[i] = action
        
        logger.info(f"Mapped actions for {len(self.actions)} frames")
        
        # Print action distribution
        unique_actions = list(set(self.actions))
        logger.info(f"Unique actions: {len(unique_actions)}")
        for action in sorted(unique_actions)[:10]:
            count = self.actions.count(action)
            logger.info(f"  {action}: {count} frames")
    
    def _determine_action(self, current_actions, pressed_keys):
        """
        Determine the primary action for a frame based on current inputs.
        
        Args:
            current_actions (list): List of input events for this frame
            pressed_keys (set): Currently pressed keys
        
        Returns:
            str: Action name
        """
        action = 'idle'
        
        # Update pressed keys
        for input_event in current_actions:
            if input_event['type'] == 'key_press':
                pressed_keys.add(input_event['key'])
            elif input_event['type'] == 'key_release':
                pressed_keys.discard(input_event['key'])
            elif input_event['type'] == 'mouse_press':
                pressed_keys.add(f"{input_event['button']}_click")
            elif input_event['type'] == 'mouse_release':
                pressed_keys.discard(f"{input_event['button']}_click")
        
        # Determine primary action (priority order)
        priority_keys = ['space', 'left_click', 'c', 'x', 'r', 'f', 'w', 'd', 's', 'a']
        
        for key in priority_keys:
            if key in pressed_keys:
                action = INPUT_TO_ACTION_MAP.get(key, 'idle')
                break
        
        # Check for mouse movement
        mouse_moves = [e for e in current_actions if e['type'] == 'mouse_move']
        if mouse_moves:
            # Return primary action + mouse if applicable
            if action == 'idle' and mouse_moves:
                action = 'looking'  # or use look_x, look_y
        
        return action
    
    def save_actions(self):
        """Save actions to text file (one per line)."""
        with open(self.actions_file, 'w') as f:
            for action in self.actions:
                f.write(action + '\n')
        
        logger.info(f"Saved {len(self.actions)} actions to {self.actions_file}")
    
    def save_dataset(self, extract_features=True):
        """
        Save dataset as CSV for model training.
        
        Args:
            extract_features (bool): Whether to extract features or just save paths
        """
        from deployment.feature_extractor import image_to_features
        from config import ACTION_MAPPING
        
        logger.info("Building training dataset...")
        
        data = []
        
        for frame_path, action in tqdm(zip(self.frames, self.actions), total=len(self.frames)):
            try:
                # Read image and convert to base64 for feature extraction
                import base64
                with open(frame_path, 'rb') as f:
                    img_base64 = base64.b64encode(f.read()).decode('utf-8')
                
                # Extract features (128 dimensions)
                features = image_to_features(img_base64, feature_len=128)
                
                # Map action to index
                action_idx = ACTION_MAPPING.get(action, 0)
                
                # Create row
                row = {f"feature_{i}": features[i] for i in range(len(features))}
                row['action'] = action_idx
                row['action_name'] = action
                
                data.append(row)
            except Exception as e:
                logger.warning(f"Error processing frame {frame_path}: {e}")
        
        # Create DataFrame
        df = pd.DataFrame(data)
        df.to_csv(self.dataset_file, index=False)
        
        logger.info(f"Dataset saved to {self.dataset_file} ({len(df)} samples)")
        logger.info(f"Columns: {list(df.columns)[:5]}... + action")
        
        return df
    
    def save_mapping(self):
        """Save detailed mapping between frames and inputs."""
        mapping = {
            "session_name": self.session_dir.name,
            "total_frames": len(self.frames),
            "total_actions": len(self.actions),
            "frames_dir": str(self.frames_dir),
            "actions_file": str(self.actions_file),
            "dataset_file": str(self.dataset_file),
            "frame_to_action": {
                str(i): {"frame": frame, "action": action}
                for i, (frame, action) in enumerate(zip(self.frames, self.actions))
            }
        }
        
        with open(self.mapping_file, 'w') as f:
            json.dump(mapping, f, indent=2)
        
        logger.info(f"Mapping saved to {self.mapping_file}")
    
    def process(self, skip_frames=1, extract_features=True):
        """
        Run complete processing pipeline.
        
        Args:
            skip_frames (int): Extract every nth frame
            extract_features (bool): Whether to extract features
        """
        try:
            self.load_metadata()
            self.extract_frames(skip_frames=skip_frames)
            self.load_inputs()
            self.map_inputs_to_frames()
            self.save_actions()
            self.save_dataset(extract_features=extract_features)
            self.save_mapping()
            
            logger.info("\n" + "="*50)
            logger.info("Processing complete!")
            logger.info(f"Frames: {self.frames_dir}")
            logger.info(f"Actions: {self.actions_file}")
            logger.info(f"Dataset: {self.dataset_file}")
            logger.info("="*50)
            
            return True
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Process recorded gameplay into training dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/process_gameplay_recording.py --session data/raw/gameplay_videos/20250125_120000
  python scripts/process_gameplay_recording.py --session data/raw/gameplay_videos/20250125_120000 --skip 2
  python scripts/process_gameplay_recording.py --session data/raw/gameplay_videos/20250125_120000 --output my_datasets
        """
    )
    
    parser.add_argument(
        "--session",
        required=True,
        help="Path to session directory containing video and inputs"
    )
    parser.add_argument(
        "--output",
        default="data/processed",
        help="Output directory for processed data (default: data/processed)"
    )
    parser.add_argument(
        "--skip",
        type=int,
        default=1,
        help="Extract every nth frame (default: 1 = extract all)"
    )
    
    args = parser.parse_args()
    
    # Process
    processor = GameplayProcessor(args.session, args.output)
    success = processor.process(skip_frames=args.skip)
    
    if success:
        logger.info("\nNext steps:")
        logger.info("1. Review extracted frames and actions")
        logger.info("2. Train model: python models/transformer/transformer_training.py")
        logger.info("3. Deploy: python deployment/control_backend.py")
    else:
        logger.error("Processing failed!")


if __name__ == "__main__":
    main()
