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
  CH_PROBE_INTERVAL         探测间隔秒数（默认 60）
  CH_PROBE_THRESHOLD        连续失败阈值（默认 3，约 3min 后告警）
  CH_PROBE_LOG              日志文件路径（默认 logs/ch_health_probe.log）
  CH_PROBE_TICK_STALE_MIN   盘中 tick 新鲜度阈值分钟（默认 15，A3 2026-09-16）

与调度器探针的关系：
  - 调度器 _probe_loop 仅在调度器运行期生效（盘后时段覆盖不到）
  - 本探针 7×24 常驻，填补调度器不运行时段的监控盲点
  - 两者均通过 Alerter 发告警，Alerter 内置 300s 冷却防重复
"""

from __future__ import annotations

import datetime
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

from zephyr.data import trading_calendar  # noqa: E402
from zephyr.data.alerter import Alerter, LEVEL_ERROR  # noqa: E402
from zephyr.data.redundant_source.heartbeat_monitor import (  # noqa: E402
    HeartbeatMonitor,
    SourceState,
)
from zephyr.data.table_registry import get_registry  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

log = logging.getLogger("ch_health_probe")

_DEFAULT_INTERVAL = 60.0
_DEFAULT_THRESHOLD = 3
_DEFAULT_LOG = REPO_ROOT / "logs" / "ch_health_probe.log"
_PID_FILE = REPO_ROOT / "logs" / "ch_health_probe.pid"

# A3 推进度看门狗（2026-09-16）：盘中 tick 新鲜度阈值（分钟）
_DEFAULT_TICK_STALE_MIN = 15.0
_TICK_TRADE_WINDOWS = ((570, 690), (780, 900))  # 09:30-11:30 / 13:00-15:00（当日分钟数）
_TBL_TICK = get_registry().table("market_tick")  # TableRegistry 真源（#ARCH-CH-024）


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


def _in_tick_window(now: datetime.datetime | None = None) -> bool:
    """盘中窗口判定：09:30-11:30 / 13:00-15:00（A3 推进度看门狗）。"""
    now = now or datetime.datetime.now()
    m = now.hour * 60 + now.minute
    return any(a <= m < b for a, b in _TICK_TRADE_WINDOWS)


def _check_tick_freshness(
    stale_min: float,
    alerter: Alerter,
    now: datetime.datetime | None = None,
) -> None:
    """盘中 tick 数据新鲜度检查（端到端：订阅→WAL→CH 全链路，A3 2026-09-16）。

    今日 09:36 实时链路断供 3 小时而全部监控绿灯的盲区补丁——既有看门狗
    全部锚定订阅侧 last_tick_ts（回调接收时刻），写入侧断链时照样刷新。
    本检查锚定 CH 侧 max(timestamp)，独立于任何进程存亡。
    Alerter 内置 300s 冷却：持续断供时每 5 分钟重复告警。
    """
    try:
        if not _in_tick_window(now) or not trading_calendar.is_trading_day():
            return
        from zephyr.data import ch_reader

        tsv = ch_reader.query(
            f"SELECT max(timestamp) FROM {_TBL_TICK} WHERE trade_date = today() FORMAT TSV",  # noqa: bare-sql  独立探针脚本单一查询，无常驻 SQL 层可集中
            timeout=10,
        )
        max_ts = (tsv or "").strip()
        now = now or datetime.datetime.now()
        if not max_ts:
            # 今日零数据：开盘缓冲（09:45）后仍为空=链路自始断供
            open_plus = now.replace(hour=9, minute=45, second=0, microsecond=0)
            if now >= open_plus:
                alerter.notify(
                    "tick_freshness",
                    "盘中无今日 tick 数据（链路断供）",
                    level=LEVEL_ERROR,
                    source="tick_pipeline",
                )
            return
        max_dt = datetime.datetime.strptime(max_ts[:19], "%Y-%m-%d %H:%M:%S")
        age_min = (now - max_dt).total_seconds() / 60
        if age_min > stale_min:
            alerter.notify(
                "tick_freshness",
                f"盘中 tick 最新数据落后 {age_min:.0f} 分钟（阈值 {stale_min:.0f}），链路疑似断供",
                level=LEVEL_ERROR,
                source="tick_pipeline",
            )
            log.error("tick 新鲜度告警: max(timestamp)=%s 落后 %.0f 分钟", max_ts, age_min)
    except Exception as e:  # noqa: BLE001 — 监控自身异常不逃逸
        log.warning("tick 新鲜度检查异常: %s", e)


def main() -> None:
    interval = float(os.environ.get("CH_PROBE_INTERVAL", _DEFAULT_INTERVAL))
    threshold = int(os.environ.get("CH_PROBE_THRESHOLD", _DEFAULT_THRESHOLD))
    stale_min = float(os.environ.get("CH_PROBE_TICK_STALE_MIN", _DEFAULT_TICK_STALE_MIN))
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
    log.info(
        "探针已启动，7×24 监控 CH 连通性 + 盘中 tick 新鲜度（阈值 %.0f 分钟）。状态变化时自动告警。",
        stale_min,
    )

    # 主循环：等待停止信号
    prev_state = SourceState.UNKNOWN
    last_freshness = 0.0
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
            # A3：盘中 tick 新鲜度检查（与连通性同频，Alerter 自带冷却）
            if time.time() - last_freshness >= interval:
                last_freshness = time.time()
                _check_tick_freshness(stale_min, alerter)
            time.sleep(1)
    finally:
        monitor.stop()
        _PID_FILE.unlink(missing_ok=True)
        log.info("CH 健康探针已停止 (PID=%d)", os.getpid())


if __name__ == "__main__":
    main()
