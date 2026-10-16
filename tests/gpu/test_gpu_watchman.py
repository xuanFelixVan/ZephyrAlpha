# [BLUEPRINT] MOD-GPU-WATCHMAN | docs/03_modules/_domain_infrastructure_runtime/index.md
# [TESTS] tests/gpu/test_gpu_watchman.py
# 测试隔离：GPU 读数全走注入位（canned 字符串/detect_fn/假命令 GPU_WATCHMAN_NVIDIA_SMI），
#   登记册全走 tmp_path（GPU_WATCHMAN_REGISTRY 注入），零真 GPU、零生产路径依赖。
# [TTL] permanent
"""GPU 看门人红绿双向：canned nvidia-smi 解析、登记册 acquire/release/status、独占互斥与不可知分流。"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _REPO_ROOT / "scripts" / "gpu" / "gpu_watchman.py"

_spec = importlib.util.spec_from_file_location("gpu_watchman", _SCRIPT)
gpu_watchman = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gpu_watchman)

IDLE_READING = {"free_gb": 20.0, "util_pct": 5.0}
BUSY_READING = {"free_gb": 2.0, "util_pct": 95.0}


# ---------- parse_smi_output：canned nvidia-smi 字符串 ----------


def test_parse_basic():
    out = gpu_watchman.parse_smi_output(" 1234, 24576, 35\n")
    assert out == {"free_gb": 22.795, "util_pct": 35.0}


def test_parse_takes_first_gpu_row():
    out = gpu_watchman.parse_smi_output(" 512, 32768, 3\n 4096, 24576, 90\n")
    assert out == {"free_gb": 31.5, "util_pct": 3.0}


def test_parse_unsupported_util_raises():
    with pytest.raises(ValueError):
        gpu_watchman.parse_smi_output(" 1234, 24576, [Not Supported]\n")


def test_parse_na_memory_raises():
    with pytest.raises(ValueError):
        gpu_watchman.parse_smi_output("N/A, 24576, 3\n")


def test_parse_garbage_raises():
    with pytest.raises(ValueError):
        gpu_watchman.parse_smi_output("abc, def, ghi\n")


def test_parse_units_suffix_real_smi_output():
    """真机 nvidia-smi 默认输出带单位后缀（不加 nounits）——Git Bash status 恒 unknown 回归。

    st-ibtclose-20261015 件4：旧 _to_float('3348 MiB') 恒 ValueError → detect() 恒 None。
    """
    out = gpu_watchman.parse_smi_output("3348 MiB, 24576 MiB, 39 %\n")
    assert out == {"free_gb": round((24576 - 3348) / 1024.0, 3), "util_pct": 39.0}


def test_to_float_tolerates_units_and_still_rejects_unreadable():
    assert gpu_watchman._to_float("1234 MiB") == 1234.0
    assert gpu_watchman._to_float("39 %") == 39.0
    assert gpu_watchman._to_float("35") == 35.0
    with pytest.raises(ValueError):
        gpu_watchman._to_float("[Not Supported]")
    with pytest.raises(ValueError):
        gpu_watchman._to_float("N/A")
    with pytest.raises(ValueError):
        gpu_watchman._to_float("abc")


def test_parse_empty_raises():
    with pytest.raises(ValueError):
        gpu_watchman.parse_smi_output("\n \n")


# ---------- detect：缺失/超时/非零退出→None；假命令注入可测 ----------


def test_detect_none_when_override_cmd_missing(monkeypatch):
    monkeypatch.setenv("GPU_WATCHMAN_NVIDIA_SMI", "gpu-watchman-no-such-cmd-xyz")
    assert gpu_watchman.detect() is None


def test_detect_none_when_no_smi_on_path(monkeypatch):
    monkeypatch.delenv("GPU_WATCHMAN_NVIDIA_SMI", raising=False)
    monkeypatch.setattr(gpu_watchman.shutil, "which", lambda name: None)
    assert gpu_watchman.detect() is None


def _write_fake_smi(tmp_path: Path, body_lines: list[str]) -> str:
    """写假 nvidia-smi 命令（win=.bat / posix=.sh），忽略参数只回 canned 输出。"""
    if os.name == "nt":
        script = tmp_path / "fake_smi.bat"
        script.write_text("@echo off\r\n" + "\r\n".join(body_lines) + "\r\n", encoding="ascii")
    else:
        script = tmp_path / "fake_smi.sh"
        script.write_text("#!/bin/sh\n" + "\n".join(body_lines) + "\n", encoding="utf-8")
        script.chmod(0o755)
    return str(script)


def test_detect_parses_fake_command_output(monkeypatch, tmp_path):
    if os.name == "nt":
        fake = _write_fake_smi(tmp_path, ["@echo 1234, 24576, 35"])
    else:
        fake = _write_fake_smi(tmp_path, ['echo "1234, 24576, 35"'])
    monkeypatch.setenv("GPU_WATCHMAN_NVIDIA_SMI", fake)
    assert gpu_watchman.detect() == {"free_gb": 22.795, "util_pct": 35.0}


def test_detect_none_on_nonzero_exit(monkeypatch, tmp_path):
    if os.name == "nt":
        fake = _write_fake_smi(tmp_path, ["@exit 4"])
    else:
        fake = _write_fake_smi(tmp_path, ["exit 4"])
    monkeypatch.setenv("GPU_WATCHMAN_NVIDIA_SMI", fake)
    assert gpu_watchman.detect() is None


def test_detect_none_on_timeout(monkeypatch, tmp_path):
    sleeper = f'"{sys.executable}" -c "import time; time.sleep(5)"'
    if os.name != "nt":
        sleeper = f"{sys.executable} -c 'import time; time.sleep(5)'"
    fake = _write_fake_smi(tmp_path, [f"@{sleeper}" if os.name == "nt" else sleeper])
    monkeypatch.setenv("GPU_WATCHMAN_NVIDIA_SMI", fake)
    monkeypatch.setattr(gpu_watchman, "SMI_TIMEOUT", 0.3)
    assert gpu_watchman.detect() is None


# ---------- 登记册：acquire/release/status（tmp_path，注入读数） ----------


def _acquire(task, registry_path, detect_fn=None, exclusive=False, wait_timeout=5.0, poll=0.02):
    return gpu_watchman.acquire(
        task,
        exclusive=exclusive,
        registry_path=registry_path,
        wait_timeout=wait_timeout,
        poll_interval=poll,
        detect_fn=detect_fn if detect_fn is not None else (lambda: IDLE_READING),
    )


def test_acquire_opportunistic_idle_approves_and_records(tmp_path):
    reg = tmp_path / "reg.jsonl"
    assert _acquire("t1", reg) is True
    active = gpu_watchman.read_active(reg)
    assert set(active) == {"t1"}
    assert active["t1"]["mode"] == "opportunistic"
    rows = [json.loads(line) for line in reg.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    assert set(rows[0]) == {"ts", "task", "mode", "event"}
    assert rows[0]["task"] == "t1"
    assert rows[0]["event"] == "acquire"
    assert rows[0]["mode"] == "opportunistic"


def test_acquire_opportunistic_unknown_gpu_approves(tmp_path):
    reg = tmp_path / "reg.jsonl"
    assert _acquire("t1", reg, detect_fn=lambda: None) is True
    assert set(gpu_watchman.read_active(reg)) == {"t1"}


def test_acquire_exclusive_unknown_gpu_rejected(tmp_path):
    reg = tmp_path / "reg.jsonl"
    assert _acquire("t1", reg, detect_fn=lambda: None, exclusive=True, wait_timeout=0.2) is False
    assert gpu_watchman.read_active(reg) == {}
    assert not reg.exists()  # 未获准禁落 acquire 事件


def test_acquire_opportunistic_busy_times_out(tmp_path):
    reg = tmp_path / "reg.jsonl"
    assert _acquire("t1", reg, detect_fn=lambda: BUSY_READING, wait_timeout=0.2) is False
    assert not reg.exists()


def test_acquire_exclusive_blocked_by_active_task_then_approved(tmp_path):
    reg = tmp_path / "reg.jsonl"
    assert _acquire("t1", reg) is True
    # 登记册有任何活跃任务→独占与机会档同规让路（即使 GPU 读数空闲）
    assert _acquire("t2", reg, exclusive=True, wait_timeout=0.2) is False
    assert _acquire("t2", reg, exclusive=False, wait_timeout=0.2) is False
    gpu_watchman.release("t1", reg)
    assert _acquire("t2", reg, exclusive=True) is True
    assert set(gpu_watchman.read_active(reg)) == {"t2"}


def test_release_clears_marker_and_reacquire(tmp_path):
    reg = tmp_path / "reg.jsonl"
    assert _acquire("t1", reg) is True
    gpu_watchman.release("t1", reg)
    assert gpu_watchman.read_active(reg) == {}
    assert _acquire("t1", reg) is True  # 释放后可再申请
    modes = [json.loads(line)["event"] for line in reg.read_text(encoding="utf-8").splitlines()]
    assert modes == ["acquire", "release", "acquire"]  # only-append，历史行不改写


def test_release_idempotent(tmp_path):
    reg = tmp_path / "reg.jsonl"
    gpu_watchman.release("ghost", reg)  # 未持有→无异常
    assert gpu_watchman.read_active(reg) == {}


def test_env_registry_override(monkeypatch, tmp_path):
    env_reg = tmp_path / "env" / "reg.jsonl"
    monkeypatch.setenv("GPU_WATCHMAN_REGISTRY", str(env_reg))
    gpu_watchman.append_event("t9", "opportunistic", "acquire")
    assert env_reg.exists() and set(gpu_watchman.read_active()) == {"t9"}


# ---------- status / CLI ----------


def test_status_active_and_unknown_gpu(tmp_path, monkeypatch):
    reg = tmp_path / "reg.jsonl"
    monkeypatch.setattr(gpu_watchman, "detect", lambda: None)
    gpu_watchman.append_event("t1", "exclusive", "acquire", reg)
    text = gpu_watchman.status(reg)
    assert "task=t1" in text and "mode=exclusive" in text
    assert "gpu: unknown" in text  # 不可知禁冒充空闲


def test_status_with_reading(tmp_path, monkeypatch):
    reg = tmp_path / "reg.jsonl"
    monkeypatch.setattr(gpu_watchman, "detect", lambda: IDLE_READING)
    text = gpu_watchman.status(reg)
    assert "active: (none)" in text
    assert "free_gb=20.0" in text and "util_pct=5.0" in text


def test_cli_acquire_timeout_exit7(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(gpu_watchman, "detect", lambda: BUSY_READING)
    code = gpu_watchman.main(["acquire", "--task", "t1", "--exclusive", "--wait-timeout", "0.2"])
    assert code == gpu_watchman.EXIT_TIMEOUT == 7
    assert "timeout" in capsys.readouterr().err


def test_cli_acquire_success_exit0(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(gpu_watchman, "detect", lambda: IDLE_READING)
    monkeypatch.setenv("GPU_WATCHMAN_REGISTRY", str(tmp_path / "cli.jsonl"))
    code = gpu_watchman.main(["acquire", "--task", "t1", "--exclusive"])
    assert code == 0
    assert "acquired" in capsys.readouterr().out
    assert gpu_watchman.read_active()["t1"]["mode"] == "exclusive"


def test_cli_release(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("GPU_WATCHMAN_REGISTRY", str(tmp_path / "cli.jsonl"))
    monkeypatch.setattr(gpu_watchman, "detect", lambda: IDLE_READING)
    assert gpu_watchman.main(["acquire", "--task", "t1"]) == 0
    assert gpu_watchman.main(["release", "--task", "t1"]) == 0
    assert gpu_watchman.read_active() == {}
    assert "released" in capsys.readouterr().out


def test_cli_status_exit0(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("GPU_WATCHMAN_REGISTRY", str(tmp_path / "cli.jsonl"))
    monkeypatch.setattr(gpu_watchman, "detect", lambda: IDLE_READING)
    assert gpu_watchman.main(["status"]) == 0
    assert "free_gb=20.0" in capsys.readouterr().out
