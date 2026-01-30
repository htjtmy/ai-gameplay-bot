"""
Gameplay Recorder - Records video and player inputs simultaneously

This script records:
1. Screen/game window video
2. Keyboard and mouse inputs
3. Timestamp mapping between video frames and inputs

Usage:
    python scripts/gameplay_recorder.py --output my_gameplay --duration 60
"""

import cv2
import json
import logging
import argparse
import time
import os
import ctypes
from ctypes import wintypes
from datetime import datetime
from pynput import mouse, keyboard
from threading import Thread, Event
from pathlib import Path
import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _find_window_by_process_name(process_name: str):
    """Find a top-level window for the given process name. Returns (hwnd, (x, y, w, h))."""
    target_name = process_name.lower()
    target_pids = {p.pid for p in psutil.process_iter(['name']) if p.info.get('name', '').lower() == target_name}
    if not target_pids:
        raise RuntimeError(f"未找到进程: {process_name}")

    user32 = ctypes.windll.user32

    EnumWindows = user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    GetWindowThreadProcessId = user32.GetWindowThreadProcessId
    IsWindowVisible = user32.IsWindowVisible
    GetWindowRect = user32.GetWindowRect

    found = {'hwnd': None, 'rect': None}

    def _callback(hwnd, lparam):
        if not IsWindowVisible(hwnd):
            return True
        pid = wintypes.DWORD()
        GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in target_pids:
            rect = wintypes.RECT()
            if GetWindowRect(hwnd, ctypes.byref(rect)):
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                if width > 0 and height > 0:
                    found['hwnd'] = hwnd
                    found['rect'] = (rect.left, rect.top, width, height)
                    return False  # stop enumeration
        return True

    EnumWindows(EnumWindowsProc(_callback), 0)

    if not found['hwnd'] or not found['rect']:
        raise RuntimeError(f"未找到 {process_name} 的可见窗口")

    return found['hwnd'], found['rect']


def _focus_window(hwnd):
    """Bring target window to foreground."""
    user32 = ctypes.windll.user32
    ShowWindow = user32.ShowWindow
    SetForegroundWindow = user32.SetForegroundWindow
    SW_RESTORE = 9
    ShowWindow(hwnd, SW_RESTORE)
    SetForegroundWindow(hwnd)


def _slugify(text: str) -> str:
    """Filesystem-safe slug (保留中文、ASCII字母/数字/_-). / Filesystem-safe slug (preserves Chinese, ASCII letters/digits/_-)."""
    import unicodedata
    # 保留中文、ASCII字母数字和 -_ / Preserve Chinese, ASCII alphanumeric and -_
    allowed_ascii = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    result = []
    for c in text:
        if c in allowed_ascii:
            result.append(c)
        elif '\u4e00' <= c <= '\u9fff':  # 中文字符范围 / Chinese character range
            result.append(c)
        elif c.isspace():
            result.append('_')
        else:
            result.append('_')
    return ''.join(result)[:100]


class GameplayRecorder:
    """Records gameplay video and player inputs."""
    
    def __init__(self, output_dir="data/raw/gameplay_videos", session_name=None, screen_area=None, process_name=None, category=None, label=None):
        """
        Initialize the recorder.
        
        Args:
            output_dir (str): Directory to save recordings
            session_name (str): Custom session name (auto-generated if None)
            screen_area (tuple): (x, y, width, height) for screen capture area
            process_name (str): Target process name to focus and capture
            category (str): 分类目录名
            label (str): 标签，附加到文件名
        """
        # Resolve category folder
        base_dir = Path(output_dir)
        if category:
            base_dir = base_dir / _slugify(category)
        base_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = base_dir
        
        # Session setup with label appended
        if session_name is None:
            session_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = _slugify(session_name)
        if label:
            safe_name = f"{safe_name}_{_slugify(label)}"
        self.session_name = safe_name
        self.session_dir = self.output_dir / safe_name
        self.session_dir.mkdir(exist_ok=True)
        
        # Paths with timestamp to avoid overwriting previous recordings
        recording_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_path = self.session_dir / f"gameplay_{recording_timestamp}.mp4"
        self.inputs_path = self.session_dir / f"inputs_{recording_timestamp}.jsonl"
        self.metadata_path = self.session_dir / f"metadata_{recording_timestamp}.json"
        
        # Video recording
        self.screen_area = screen_area or (0, 0, 1280, 720)
        self.fps = 30
        self.video_writer = None
        self.frame_count = 0
        
        # Input tracking
        self.inputs = []
        self.recording = Event()
        self.recording_stopped = Event()
        self.listener = None
        self.mouse_listener = None
        
        self.process_name = process_name
        self.category = category
        self.label = label
        logger.info(f"Recorder initialized for session: {self.session_name}")
        logger.info(f"Category: {self.category or 'none'} | Label: {self.label or 'none'}")
        logger.info(f"Output directory: {self.session_dir}")
        logger.info(f"Screen area: {self.screen_area}")
    
    def _on_keyboard_press(self, key):
        """Callback for keyboard press."""
        if not self.recording.is_set():
            return
        
        try:
            timestamp = int((time.time() - self.start_time) * 1000)  # milliseconds
            
            # Handle special keys
            if isinstance(key, keyboard.Key):
                key_name = key.name
            else:
                try:
                    key_name = key.char
                except AttributeError:
                    key_name = str(key)
            
            self.inputs.append({
                "timestamp": timestamp,
                "type": "key_press",
                "key": key_name,
                "frame": int(self.frame_count)
            })
            
            # Check for stop key (F8) / 检查停止键（F8）
            if key == keyboard.Key.f8:
                logger.info(f"Pressed F8 - stopping recording... / 按下F8 - 停止录制...")
                self.recording.clear()  # 停止录制 / Stop recording
            
            # Log important keys / 记录重要按键
            if key_name in ['esc', 'f8']:
                logger.info(f"Pressed: {key_name}")
                
        except Exception as e:
            logger.error(f"Error recording keyboard press: {e}")
    
    def _on_keyboard_release(self, key):
        """Callback for keyboard release."""
        if not self.recording.is_set():
            return
        
        try:
            timestamp = int((time.time() - self.start_time) * 1000)
            
            if isinstance(key, keyboard.Key):
                key_name = key.name
            else:
                try:
                    key_name = key.char
                except AttributeError:
                    key_name = str(key)
            
            self.inputs.append({
                "timestamp": timestamp,
                "type": "key_release",
                "key": key_name,
                "frame": int(self.frame_count)
            })
        except Exception as e:
            logger.error(f"Error recording keyboard release: {e}")
    
    def _on_mouse_move(self, x, y):
        """Callback for mouse movement."""
        if not self.recording.is_set():
            return
        
        try:
            timestamp = int((time.time() - self.start_time) * 1000)
            
            # Sample mouse movement every 50ms to reduce data
            if len(self.inputs) > 0 and self.inputs[-1]["type"] == "mouse_move":
                if timestamp - self.inputs[-1]["timestamp"] < 50:
                    return
            
            self.inputs.append({
                "timestamp": timestamp,
                "type": "mouse_move",
                "x": x,
                "y": y,
                "frame": int(self.frame_count)
            })
            
            # Log first few mouse moves to confirm recording is working
            mouse_move_count = sum(1 for inp in self.inputs if inp["type"] == "mouse_move")
            if mouse_move_count <= 5:
                logger.info(f"Mouse moved to ({x}, {y}) - recorded #{mouse_move_count}")
                
        except Exception as e:
            logger.error(f"Error recording mouse move: {e}")
    
    def _on_mouse_click(self, x, y, button, pressed):
        """Callback for mouse clicks."""
        if not self.recording.is_set():
            return
        
        try:
            timestamp = int((time.time() - self.start_time) * 1000)
            
            self.inputs.append({
                "timestamp": timestamp,
                "type": "mouse_press" if pressed else "mouse_release",
                "button": button.name,
                "x": x,
                "y": y,
                "frame": int(self.frame_count)
            })
            
            logger.info(f"Mouse {button.name} {'pressed' if pressed else 'released'} at ({x}, {y})")
        except Exception as e:
            logger.error(f"Error recording mouse click: {e}")
    
    def _record_video(self):
        """Record video from screen."""
        try:
            import mss
            
            monitor = {
                "top": self.screen_area[1],
                "left": self.screen_area[0],
                "width": self.screen_area[2],
                "height": self.screen_area[3]
            }
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                str(self.video_path),
                fourcc,
                self.fps,
                (self.screen_area[2], self.screen_area[3])
            )
            
            if not self.video_writer.isOpened():
                logger.error("Failed to initialize video writer")
                return
            
            logger.info("Video recording started")
            
            with mss.mss() as sct:
                while self.recording.is_set():
                    # Capture screen / 捕获屏幕
                    screenshot = sct.grab(monitor)
                    # 转换 mss 截图为 numpy 数组 / Convert mss screenshot to numpy array
                    import numpy as np
                    frame = np.array(screenshot)[:, :, :3]  # 去除 alpha 通道 / Remove alpha channel
                    frame = cv2.resize(frame, (self.screen_area[2], self.screen_area[3]))
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    # Write frame
                    self.video_writer.write(frame)
                    self.frame_count += 1
                    
                    # Control FPS
                    time.sleep(1 / self.fps)
            
            if self.video_writer is not None:
                self.video_writer.release()
            
            logger.info(f"Video recording stopped. Frames: {self.frame_count}")
            
        except ImportError:
            logger.error("mss library not installed. Install with: pip install mss")
        except Exception as e:
            logger.error(f"Error in video recording: {e}")
        finally:
            self.recording_stopped.set()
    
    def start(self):
        """Start recording."""
        logger.info("Starting recorder...")
        logger.info("Press 'F8' on keyboard or Ctrl+C to stop recording / 按F8或Ctrl+C停止录制")
        
        self.start_time = time.time()
        self.recording.set()
        
        # Start video recording thread
        video_thread = Thread(target=self._record_video, daemon=True)
        video_thread.start()
        
        # Start input listeners
        self.listener = keyboard.Listener(
            on_press=self._on_keyboard_press,
            on_release=self._on_keyboard_release
        )
        self.listener.start()
        
        self.mouse_listener = mouse.Listener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click
        )
        self.mouse_listener.start()
        
        logger.info("Recorder started")
        return video_thread
    
    def stop(self):
        """Stop recording."""
        logger.info("Stopping recorder...")
        self.recording.clear()
        
        # Wait for video to finish
        timeout = 5
        start = time.time()
        while not self.recording_stopped.is_set() and (time.time() - start) < timeout:
            time.sleep(0.1)
        
        # Stop listeners
        if self.listener:
            self.listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        
        # Save data
        self._save_inputs()
        self._save_metadata()
        
        logger.info("Recorder stopped")
    
    def _save_inputs(self):
        """Save inputs to JSONL file."""
        with open(self.inputs_path, 'w') as f:
            for input_event in self.inputs:
                f.write(json.dumps(input_event) + '\n')
        
        logger.info(f"Saved {len(self.inputs)} input events to {self.inputs_path}")
    
    def _save_metadata(self):
        """Save recording metadata."""
        duration = time.time() - self.start_time
        
        # Count input types for statistics
        input_stats = {}
        for inp in self.inputs:
            input_type = inp["type"]
            input_stats[input_type] = input_stats.get(input_type, 0) + 1
        
        metadata = {
            "session_name": self.session_name,
            "category": self.category,
            "label": self.label,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "duration_seconds": duration,
            "video_fps": self.fps,
            "total_frames": self.frame_count,
            "total_inputs": len(self.inputs),
            "input_statistics": input_stats,
            "screen_area": self.screen_area,
            "video_path": str(self.video_path),
            "inputs_path": str(self.inputs_path)
        }
        
        with open(self.metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Metadata saved to {self.metadata_path}")
        logger.info(f"Total duration: {duration:.1f} seconds")
        logger.info(f"Total frames: {self.frame_count}")
        logger.info(f"Input statistics: {input_stats}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Record gameplay video and inputs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/gameplay_recorder.py
  python scripts/gameplay_recorder.py --output my_recordings --session my_game
  python scripts/gameplay_recorder.py --screen 0 0 1920 1080
        """
    )
    
    parser.add_argument(
        "--output",
        default="data/raw/gameplay_videos",
        help="Output directory for recordings (default: data/raw/gameplay_videos)"
    )
    parser.add_argument(
        "--session",
        help="Custom session name (default: auto-generated timestamp)"
    )
    parser.add_argument(
        "--screen",
        type=int,
        nargs=4,
        metavar=("X", "Y", "WIDTH", "HEIGHT"),
        default=(0, 0, 1280, 720),
        help="Screen capture area (default: 0 0 1280 720)"
    )
    parser.add_argument(
        "--process",
        help="进程名（如 game.exe），自动根据窗口设置录制区域并在 3 秒后开始"
    )
    parser.add_argument(
        "--category",
        help="视频分类（将作为子目录创建/复用）"
    )
    parser.add_argument(
        "--label",
        help="视频标签（附加在文件名中）"
    )
    
    args = parser.parse_args()
    
    try:
        screen_area = tuple(args.screen)
        target_hwnd = None

        if args.process:
            logger.info(f"查找进程窗口: {args.process}")
            hwnd, rect = _find_window_by_process_name(args.process)
            target_hwnd = hwnd
            screen_area = rect
            logger.info(f"找到窗口区域: {screen_area}")
            _focus_window(hwnd)
            logger.info("已激活目标窗口，3 秒后开始录制...")
            time.sleep(3)

        # Create recorder
        recorder = GameplayRecorder(
            output_dir=args.output,
            session_name=args.session,
            screen_area=screen_area,
            process_name=args.process,
            category=args.category,
            label=args.label
        )
        
        # Start recording
        video_thread = recorder.start()
        
        # Wait for user to stop
        try:
            video_thread.join()
        except KeyboardInterrupt:
            pass
        
        # Stop recording
        recorder.stop()
        
    except KeyboardInterrupt:
        logger.info("Recording interrupted by user")
        if 'recorder' in locals():
            recorder.stop()


if __name__ == "__main__":
    main()
