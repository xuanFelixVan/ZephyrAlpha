#!/usr/bin/env python
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.ops.ch_health_probe
# [DOMAIN] D_DATA
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""7×24 CH 健康探针守护进程（R4b，#ARCH-DR-CH-RESTART-001）。

独立于调度器运行，覆盖盘后/周末/节假日等调度器不运行的时段。
CH 状态变化时触发告警（ALIVE→DEAD=CRITICAL，DEAD→ALIVE=INFO 恢复）。

部署方式（任选其一）：
  1. 手动后台启动：
     python scripts/ops/ch_health_probe.py &
  2. Windows 计划任务（开机自启）：
     schtasks /Create /SC ONLOGON /TN "ZephyrCHHealthProbe" /TR "python D:\\ZephyrAlpha\\scripts\\ops\\ch_health_probe.py"
  3. nohup（Linux 风格，Windows 用 start /B）：
     start /B python scripts/ops/ch_health_probe.py

配置（环境变量，可选）：
  CH_PROBE_INTERVAL     探测间隔秒数（默认 60）
  CH_PROBE_THRESHOLD    连续失败阈值（默认 3，约 3min 后告警）
  CH_PROBE_LOG          日志文件路径（默认 logs/ch_health_probe.log）

与调度器探针的关系：
  - 调度器 _probe_loop 仅在调度器运行期生效（盘后时段覆盖不到）
  - 本探针 7×24 常驻，填补调度器不运行时段的监控盲点
  - 两者均通过 Alerter 发告警，Alerter 内置 300s 冷却防重复
"""

from __future__ import annotations

import logging
import os
import signal
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 确保项目根目录在 sys.path 中
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from zephyr.data.alerter import Alerter  # noqa: E402
from zephyr.data.redundant_source.heartbeat_monitor import (  # noqa: E402
    HeartbeatMonitor,
    SourceState,
)
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

log = logging.getLogger("ch_health_probe")

_DEFAULT_INTERVAL = 60.0
_DEFAULT_THRESHOLD = 3
_DEFAULT_LOG = REPO_ROOT / "logs" / "ch_health_probe.log"
_PID_FILE = REPO_ROOT / "logs" / "ch_health_probe.pid"


def _setup_logging(log_path: Path) -> None:
    """配置日志：RotatingFileHandler + stdout。"""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    fh = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(fh)
    root.addHandler(sh)


def _real_ch_ping() -> bool:
    """真实 CH ping（SELECT 1 via ch_writer.health_check）。"""
    try:
        from zephyr.data import ch_writer

        result = ch_writer.health_check()
        return result.get("tcp") == "ok"
    except Exception as e:
        log.warning("CH ping 异常: %s", e)
        return False


def main() -> None:
    interval = float(os.environ.get("CH_PROBE_INTERVAL", _DEFAULT_INTERVAL))
    threshold = int(os.environ.get("CH_PROBE_THRESHOLD", _DEFAULT_THRESHOLD))
    log_path = Path(os.environ.get("CH_PROBE_LOG", str(_DEFAULT_LOG)))

    _setup_logging(log_path)

    # 加载 CH 配置（确保 .env.clickhouse 已加载）
    try:
        from zephyr.data.ch_config import ensure_ch_env_loaded

        ensure_ch_env_loaded()
    except Exception as e:  # noqa: BLE001
        log.warning("CH 配置加载失败（将用默认配置）: %s", e)

    # 写 PID 文件（便于进程管理）
    _PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    _PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    log.info(
        "CH 健康探针启动 (PID=%d, interval=%.0fs, threshold=%d, log=%s)", os.getpid(), interval, threshold, log_path
    )

    # 创建 HeartbeatMonitor + Alerter
    alerter = Alerter()
    monitor = HeartbeatMonitor(
        ch_ping_interval=interval,
        ch_fail_threshold=threshold,
        ch_ping_fn=_real_ch_ping,
        alerter=alerter,
    )

    # 信号处理：Ctrl+C / kill 优雅退出
    _stop = False

    def _signal_handler(signum, frame):
        nonlocal _stop
        log.info("收到信号 %s，正在停止探针...", signum)
        _stop = True

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    monitor.start()
    log.info("探针已启动，7×24 监控 CH 连通性。状态变化时自动告警。")

    # 主循环：等待停止信号
    prev_state = SourceState.UNKNOWN
    try:
        while not _stop:
            status = monitor.get_status()
            if status.ch_state != prev_state:
                log.info(
                    "CH 状态变化: %s -> %s (连续失败=%d)",
                    prev_state.value,
                    status.ch_state.value,
                    status.ch_consecutive_failures,
                )
                prev_state = status.ch_state
            time.sleep(1)
    finally:
        monitor.stop()
        _PID_FILE.unlink(missing_ok=True)
        log.info("CH 健康探针已停止 (PID=%d)", os.getpid())


if __name__ == "__main__":
    main()
