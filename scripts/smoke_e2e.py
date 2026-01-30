"""
End-to-end smoke test (production-safe):

1) Quick-train Transformer (~2s) -> models/transformer/transformer_model_finetuned.pth
2) Start deploy_transformer.py
3) Start control_backend.py
4) Verify /health and real /api/test_predict calls
5) ALWAYS stop everything cleanly (success or failure)

Run:
  uv run python scripts/smoke_e2e.py
"""

from __future__ import annotations

import os
import sys
import time
import signal
import subprocess
from pathlib import Path

import requests
import torch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

TR_WEIGHTS = PROJECT / "models/transformer/transformer_model_finetuned.pth"

TR_URL = "http://127.0.0.1:5001"
CB_URL = "http://127.0.0.1:8000"

TIMEOUT_START = 12.0


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _wait_health(url: str, timeout: float = TIMEOUT_START) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{url}/health", timeout=1.5)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.25)
    return False


def _terminate(proc: subprocess.Popen | None, name: str) -> None:
    if proc is None or proc.poll() is not None:
        return
    try:
        if os.name != "nt":
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        else:
            proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            if os.name != "nt":
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            else:
                proc.kill()
        except Exception:
            pass
    finally:
        print(f"[CLEANUP] {name} stopped")


# -----------------------------------------------------------------------------
# Quick training
# -----------------------------------------------------------------------------
def quick_train_transformer(seconds: float = 2.0) -> None:
    from models.transformer.transformer_model import GameplayTransformer

    model = GameplayTransformer(
        input_size=128,
        num_heads=4,
        hidden_size=64,
        num_layers=2,
        output_size=10,
    )
    model.train()

    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = torch.nn.CrossEntropyLoss()

    start = time.time()
    steps = 0
    while time.time() - start < seconds:
        x = torch.randn(32, 128)
        y = torch.randint(0, 10, (32,))
        opt.zero_grad()
        loss = loss_fn(model(x), y)
        loss.backward()
        opt.step()
        steps += 1

    TR_WEIGHTS.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), TR_WEIGHTS)
    print(f"[OK] Transformer trained {steps} steps, saved -> {TR_WEIGHTS}")


# -----------------------------------------------------------------------------
# Main test
# -----------------------------------------------------------------------------
def main() -> int:
    print("== Smoke E2E: quick train + start services + API checks ==")

    tr_proc = cb_proc = None

    try:
        # 1) Train model
        quick_train_transformer(2.0)

        # 2) Spawn services
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONPATH"] = str(PROJECT)

        def spawn(script: Path) -> subprocess.Popen:
            preexec = os.setsid if os.name != "nt" else None
            return subprocess.Popen(
                [sys.executable, str(script)],
                cwd=str(PROJECT),
                env=env,
                preexec_fn=preexec,
            )

        tr_proc = spawn(PROJECT / "deployment/deploy_transformer.py")
        cb_proc = spawn(PROJECT / "deployment/control_backend.py")

        # 3) Health checks
        if not _wait_health(TR_URL):
            raise RuntimeError("Transformer service did not become healthy")
        if not _wait_health(CB_URL):
            raise RuntimeError("Control backend did not become healthy")

        # 4) API checks
        status = requests.get(f"{CB_URL}/api/status", timeout=3).json()
        print("[OK] /api/status:", status)

        r = requests.post(
            f"{CB_URL}/api/test_predict",
            json={"model": "transformer"},
            timeout=5,
        )
        print(f"[OK] /api/test_predict (transformer) ->", r.status_code, r.json())
        if r.status_code != 200:
            raise RuntimeError(f"/api/test_predict failed: {r.status_code} {r.text}")

        print("\n[PASS] End-to-end smoke test succeeded.")
        print(f"UI available at: {CB_URL}/")
        return 0

    except Exception as e:
        print(f"\n[FAIL] Smoke test failed: {e}")
        return 1

    finally:
        # 5) ALWAYS cleanup
        _terminate(cb_proc, "control_backend")
        _terminate(tr_proc, "transformer_service")


if __name__ == "__main__":
    raise SystemExit(main())
