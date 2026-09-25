# [MODULE] tests.scripts.test_deadman_dashboard_channel
# [DOMAIN] D_DATA
# [TTL] permanent
"""QMine 06 业务扶正②验收：deadman_switch.ps1 第 6 路（dashboard 条件门控通道）三态。

未监听=静默（manual 语义不假警）/ 监听+心跳新鲜=绿 / 监听+stale>阈值=告警（含 pid 验活）。
沙盒法：拷贝 ps1 → `$RepoRoot` 指向 tmp_path（心跳与告警日志全落沙盒）→ Event Log 源
替换为未注册名（防测试写生产事件日志）；端口探测走真实 TCP（ephemeral 端口模拟 8890
监听态），时间用回拨时间戳控制（mock stale）。
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
PS1 = _SCRIPTS / "deadman_switch.ps1"


def _make_sandbox(tmp_path: Path) -> Path:
    text = PS1.read_text(encoding="utf-8")
    assert '$RepoRoot = "D:\\ZephyrAlpha"' in text, "ps1 配置行漂移，沙盒重定向失效"
    text = text.replace('$RepoRoot = "D:\\ZephyrAlpha"', f"$RepoRoot = '{tmp_path}'")
    # Event Log 源换未注册名：Write-EventLog 静默跳过，测试零生产事件日志副作用
    text = text.replace('-Source "ZephyrAlpha"', '-Source "ZephyrAlphaDeadmanTestUnreg"')
    dst = tmp_path / "deadman_switch.ps1"
    dst.write_text(text, encoding="utf-8", newline="\n")
    return dst


def _seed_heartbeats(tmp_path: Path, dash_content: str | None) -> None:
    """基础三路心跳必新鲜 + 双业务心跳挂假日门控（盘中时段也静默）——隔离出纯第 6 路信号。"""
    tmpdir = tmp_path / "tmp"
    tmpdir.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    for name in ("scheduler.heartbeat", "tick_subscriber.heartbeat", "ch_health_probe.heartbeat"):
        (tmpdir / name).write_text(f"{now}|{os.getpid()}|{os.getpid()}\n", encoding="utf-8")
    biz = json.dumps({"is_trading_day": False, "ts": now})
    (tmpdir / "tick_subscriber_biz.heartbeat").write_text(biz, encoding="utf-8")
    (tmpdir / "live_strategy_biz.heartbeat").write_text(biz, encoding="utf-8")
    if dash_content is not None:
        (tmpdir / "dashboard.heartbeat").write_text(dash_content, encoding="utf-8")


def _run_ps1(sandbox: Path, port: int) -> int:
    env = os.environ.copy()
    env["DEADMAN_DASHBOARD_PORT"] = str(port)
    env["DEADMAN_STALE_MIN"] = "100000"  # 基础三路双保险不触警
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(sandbox)],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    assert proc.returncode == 0, f"ps1 退出码异常: {proc.returncode}, stderr={proc.stderr[:300]}"
    return proc.returncode


def _alert_log(tmp_path: Path) -> str:
    f = tmp_path / "tmp" / "deadman_switch_alerts.log"
    return f.read_text(encoding="utf-8", errors="ignore") if f.exists() else ""


class _Listener:
    """占住一个 ephemeral 端口模拟 api_server 监听态（真实 TCP 探测路径）。"""

    def __init__(self):
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(1)
        self.port = self.sock.getsockname()[1]

    def __enter__(self) -> int:
        return self.port

    def __exit__(self, *exc):
        self.sock.close()


def _stale_iso(minutes: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(minutes=minutes)).isoformat()


def test_silent_when_port_not_listening(tmp_path: Path):
    """三态①：端口无监听 = 面板未开（manual 语义），心跳 stale 也不告警。"""
    sandbox = _make_sandbox(tmp_path)
    _seed_heartbeats(tmp_path, f"{_stale_iso(30)}|{os.getpid()}|{os.getpid()}\n")
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    free_port = s.getsockname()[1]
    s.close()  # 关闭即无监听（抢占竞态窗口极小，可接受）
    _run_ps1(sandbox, free_port)
    assert "dashboard" not in _alert_log(tmp_path)


def test_green_when_listening_and_fresh(tmp_path: Path):
    """三态②：监听在 + 心跳新鲜 = 绿，静默。"""
    sandbox = _make_sandbox(tmp_path)
    _seed_heartbeats(tmp_path, f"{datetime.now(timezone.utc).isoformat()}|{os.getpid()}|{os.getpid()}\n")
    with _Listener() as port:
        _run_ps1(sandbox, port)
    assert "dashboard" not in _alert_log(tmp_path)


def test_alert_when_listening_and_stale_alive_pid(tmp_path: Path):
    """三态③：监听在 + 心跳 stale>10min = 告警；pid 验活 ALIVE 分支（进程在但心跳停跳=疑挂死）。"""
    sandbox = _make_sandbox(tmp_path)
    _seed_heartbeats(tmp_path, f"{_stale_iso(30)}|{os.getpid()}|{os.getpid()}\n")
    with _Listener() as port:
        _run_ps1(sandbox, port)
    log = _alert_log(tmp_path)
    assert "dashboard: port" in log and "stale" in log
    assert f"pid={os.getpid()} ALIVE" in log


def test_alert_reports_dead_pid(tmp_path: Path):
    """pid 验活 DEAD 分支：心跳记已退出 pid 而端口有监听 → 提示端口被他进程占用。"""
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    proc.wait()  # 立即退出 → pid 确定已死（秒级窗口内无复用风险）
    sandbox = _make_sandbox(tmp_path)
    _seed_heartbeats(tmp_path, f"{_stale_iso(30)}|{proc.pid}|{proc.pid}\n")
    with _Listener() as port:
        _run_ps1(sandbox, port)
    assert f"pid={proc.pid} DEAD" in _alert_log(tmp_path)
