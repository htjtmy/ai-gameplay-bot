from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
from flask import Flask, jsonify, request
from flask_cors import CORS

# Imports / paths / 导入和路径
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from models.transformer.transformer_model import GameplayTransformer
from deployment.feature_extractor import safe_features_from_payload

# Logging / 日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("transformer_service")

# Config / 配置
DEFAULT_MODEL_PATH = ROOT_DIR / "models" / "transformer" / "transformer_model_finetuned.pth"  # 默认模型路径
MODEL_PATH = Path(os.environ.get("TRANSFORMER_MODEL_PATH", str(DEFAULT_MODEL_PATH))).expanduser().resolve()

INPUT_SIZE = int(os.environ.get("TRANSFORMER_INPUT_SIZE", "128"))  # 输入维度
NUM_HEADS = int(os.environ.get("TRANSFORMER_NUM_HEADS", "4"))  # 注意力头数
HIDDEN_SIZE = int(os.environ.get("TRANSFORMER_HIDDEN_SIZE", "64"))  # 隐藏层大小
NUM_LAYERS = int(os.environ.get("TRANSFORMER_NUM_LAYERS", "2"))  # Transformer层数

HOST = os.environ.get("TRANSFORMER_HOST", "0.0.0.0")  # 服务主机
PORT = int(os.environ.get("TRANSFORMER_PORT", "5001"))  # 服务端口
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"  # 计算设备（GPU或CPU）

# 从配置文件加载动作映射 / Load action mapping from config file
def load_action_mapping_from_config() -> Dict[int, str]:
    """从game_actions.json加载动作映射 / Load action mapping from game_actions.json"""
    config_path = os.environ.get("GAME_ACTIONS_CONFIG", "config/game_actions.json")
    
    if not Path(config_path).is_absolute():
        config_path = str(ROOT_DIR / config_path)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 构建ID到名称的映射 / Build ID to name mapping
        action_mapping = {}
        for action in config.get("actions", []):
            action_id = action["id"]
            action_name = action["name"]
            action_mapping[action_id] = action_name
        
        game_name = config.get("game_name", "Unknown")
        logger.info(f"✅ 加载动作配置 / Loaded action config: {game_name} ({len(action_mapping)} actions)")
        
        return action_mapping
        
    except FileNotFoundError:
        logger.error(f"❌ 配置文件不存在 / Config file not found: {config_path}")
        logger.warning("⚠️ 使用空动作映射 / Using empty action mapping")
        return {}
    except Exception as e:
        logger.error(f"❌ 加载配置失败 / Failed to load config: {e}")
        logger.warning("⚠️ 使用空动作映射 / Using empty action mapping")
        return {}


# 动作映射字典 / Action mapping dictionary
ACTION_MAPPING = load_action_mapping_from_config()
OUTPUT_SIZE = len(ACTION_MAPPING)  # 输出类别数（自动从配置获取）/ Output size (auto from config)

# -----------------------------------------------------------------------------
# Flask app / Flask应用
# -----------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)

# -----------------------------------------------------------------------------
# Model / 模型
# -----------------------------------------------------------------------------
model = GameplayTransformer(INPUT_SIZE, NUM_HEADS, HIDDEN_SIZE, NUM_LAYERS, OUTPUT_SIZE).to(DEVICE)
model_loaded: bool = False
model_error: Optional[str] = None


def load_weights() -> None:
    global model_loaded, model_error
    if not MODEL_PATH.exists():
        model_loaded = False
        model_error = f"Model weights not found at: {MODEL_PATH}"
        logger.error(model_error)
        return

    try:
        state = torch.load(str(MODEL_PATH), map_location=DEVICE)
        if isinstance(state, dict) and "state_dict" in state and isinstance(state["state_dict"], dict):
            state = state["state_dict"]

        missing, unexpected = model.load_state_dict(state, strict=False)
        if missing:
            logger.warning("Missing keys (strict=False): %s", missing)
        if unexpected:
            logger.warning("Unexpected keys (strict=False): %s", unexpected)

        model.eval()
        model_loaded = True
        model_error = None
        logger.info("Transformer weights loaded: %s (device=%s)", MODEL_PATH, DEVICE)
    except Exception as e:
        model_loaded = False
        model_error = str(e)
        logger.exception("Failed to load Transformer weights: %s", e)


load_weights()

# -----------------------------------------------------------------------------
# Payload -> features (production-safe)
# -----------------------------------------------------------------------------
def _extract_and_validate_features(payload: dict) -> Tuple[Optional[List[float]], Optional[str]]:
    """
    Uses shared safe_features_from_payload(payload) (currently hardcoded to 128 for image-derived features).
    Production-safe behavior:
      - Always validate output length against INPUT_SIZE.
      - If INPUT_SIZE != 128 and payload uses "image", fail with a clear message.
    """
    if not isinstance(payload, dict):
        return None, "payload must be a JSON object"

    # If user uses image but expects non-128 input, fail early with a clear explanation.
    if payload.get("image") is not None and INPUT_SIZE != 128:
        return None, (
            f"image-based feature extraction outputs 128 features, but TRANSFORMER_INPUT_SIZE={INPUT_SIZE}. "
            f"Send 'features' with length {INPUT_SIZE}, or upgrade feature_extractor to support {INPUT_SIZE}."
        )

    feats, err = safe_features_from_payload(payload)  # <-- NO expected_dim kwarg (fixes your crash)
    if err:
        return None, err
    if feats is None:
        return None, "failed to extract features"

    if len(feats) != INPUT_SIZE:
        return None, f"features length mismatch: got {len(feats)}, expected {INPUT_SIZE}"

    return feats, None


# -----------------------------------------------------------------------------
# Inference
# -----------------------------------------------------------------------------
def _to_model_input(features: List[float]) -> torch.Tensor:
    """
    Safer default for transformer-like models: (B, S, F) with S=1.
    If your GameplayTransformer expects (B, F), it can still handle reshape internally,
    but (1,1,F) avoids the common rank mismatch.
    """
    x = torch.tensor(features, dtype=torch.float32, device=DEVICE)
    return x.view(1, 1, -1)  # (F,) -> (1, 1, F)


def infer(features: List[float]) -> Dict[str, Any]:
    x = _to_model_input(features)
    with torch.no_grad():
        out = model(x)

        # Normalize output into a 1D vector of class scores
        if isinstance(out, (list, tuple)):
            out = out[0]

        if out.dim() == 3:
            # (B, S, C) -> last token
            vec = out[0, -1, :]
        elif out.dim() == 2:
            # (B, C)
            vec = out[0, :]
        else:
            vec = out.reshape(-1)

        probs = torch.softmax(vec, dim=0)
        probs_list = probs.detach().cpu().tolist()
        action_idx = int(torch.argmax(probs).item())
        conf = float(max(probs_list)) if probs_list else 0.0

        # 索引越界保护
        if 0 <= action_idx < len(ACTION_MAPPING):
            action_name = ACTION_MAPPING[action_idx]
        else:
            logger.error(f"Action index {action_idx} out of bounds (expected 0-{len(ACTION_MAPPING)-1})")
            action_name = "UNKNOWN_ACTION"

        return {
            "action": action_name,
            "confidence": conf,
            "tensor_viz": probs_list,
            "action_index": action_idx,
            "device": DEVICE,
        }


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    t0 = time.time()
    payload = request.get_json(silent=True) or {}

    if not model_loaded:
        return jsonify({"error": "Model not loaded", "details": model_error}), 503

    features, err = _extract_and_validate_features(payload)
    if err:
        return jsonify({"error": err}), 400

    try:
        out = infer(features)
        out["latency_ms"] = int((time.time() - t0) * 1000)
        out["model_path"] = str(MODEL_PATH)
        out["model_loaded"] = model_loaded
        out["input_size"] = INPUT_SIZE
        return jsonify(out), 200
    except Exception as e:
        logger.exception("Prediction failed: %s", e)
        return jsonify({"error": "Prediction failed", "details": str(e)}), 500


@app.route("/reload", methods=["POST"])
def reload_model():
    load_weights()
    if not model_loaded:
        return jsonify({"success": False, "error": model_error}), 503
    return jsonify({"success": True, "model_path": str(MODEL_PATH)}), 200


@app.route("/health", methods=["GET"])
def health():
    return (
        jsonify(
            {
                "status": "healthy" if model_loaded else "degraded",
                "service": "transformer",
                "model_loaded": model_loaded,
                "model_path": str(MODEL_PATH),
                "device": DEVICE,
                "input_size": INPUT_SIZE,
                "error": model_error,
            }
        ),
        (200 if model_loaded else 503),
    )


if __name__ == "__main__":
    logger.info("Starting Transformer service on %s:%s (device=%s)", HOST, PORT, DEVICE)
    app.run(host=HOST, port=PORT, debug=False)
