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
  CH_PROBE_REPLAY_LAG_H     僵尸回放阈值小时（默认 24）：max(ingest_ts) 领先
                            max(timestamp) 超过此值即疑似回放陈旧数据（#ZOMBIE-REPLAY）
  CH_PROBE_BIZ_LAG_DAYS     业务时间戳滞后阈值交易日（默认 1）：max(trade_date)
                            落后最新交易日超过此值即判真断流

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
from zephyr.data.alerter import LEVEL_ERROR, Alerter  # noqa: E402
from zephyr.data.redundant_source.heartbeat_monitor import (  # noqa: E402
    HeartbeatMonitor,
    SourceState,
)
from zephyr.data.table_registry import get_registry  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402  m46：时间戳唯一真源（DATETIME-NOW-FORBIDDEN）

log = logging.getLogger("ch_health_probe")

_DEFAULT_INTERVAL = 60.0
_DEFAULT_THRESHOLD = 3
_DEFAULT_LOG = REPO_ROOT / "logs" / "ch_health_probe.log"
_PID_FILE = REPO_ROOT / "logs" / "ch_health_probe.pid"

# A3 推进度看门狗（2026-09-16）：盘中 tick 新鲜度阈值（分钟）
_DEFAULT_TICK_STALE_MIN = 15.0
_TICK_TRADE_WINDOWS = ((570, 690), (780, 900))  # 09:30-11:30 / 13:00-15:00（当日分钟数）
_TBL_TICK = get_registry().table("market_tick")  # TableRegistry 真源（#ARCH-CH-024）

# 僵尸回放/业务时间戳滞后看门狗（2026-10-14 #ZOMBIE-REPLAY）：
# 判活口径必须以**业务时间戳**（tick 的 timestamp/trade_date）为准，ingest_ts 只证明
# "我们在写"，不证明"数据新"（supply_sentinel BRK-038/040 同型教训）。实测反例：
# c1_market.tick_depth_5 的 max(ingest_ts)=2026-10-14 16:41（今日，全绿幻觉），
# 而 max(timestamp)=2026-10-12 11:14——反复回放陈旧桥文件并盖上新 ingest_ts。
_TBL_TICK_DEPTH = get_registry().table("market_tick_depth_5")  # c1_market.tick_depth_5
# ingest_ts 领先 timestamp 超过该小时数 = 疑似僵尸回放（陈旧数据盖新入库时间）
_DEFAULT_REPLAY_LAG_H = 24.0
# max(trade_date) 落后最新交易日超过该交易日数 = 业务时间戳滞后（真断流）
_DEFAULT_BIZ_LAG_DAYS = 1
# 日级检查周期（秒）：日级判据无需跟 60s 探测同频，避免过度打 CH
_REPLAY_CHECK_INTERVAL_S = 1800.0


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
    except Exception as e:  # noqa: BLE001
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


_BIZ_TZ = datetime.timezone(datetime.timedelta(hours=8))  # 业务时区（A 股，固定 +08:00 不依赖 tzdata）


def _parse_ch_dt(raw: str) -> datetime.datetime | None:
    """解析 CH DateTime 字符串 → **恒带时区**的 datetime（避免 naive/aware 相减抛错）。

    CH 实测返回带偏移（timestamp="2026-10-12 11:14:47+08:00"、
    ingest_ts="2026-10-14 08:41:08+00:00"）；无偏移时按业务时区 +08:00 补齐。
    """
    s = (raw or "").strip()
    if not s or s.startswith("0000-00-00") or s.startswith("1970-01-01"):
        return None
    try:
        dt = datetime.datetime.fromisoformat(s)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=_BIZ_TZ)


def _trading_days_between(start: datetime.date, end: datetime.date) -> int:
    """(start, end] 区间内（不含 start 当日）的交易日数 = 业务时间戳落后最新交易日的天数。

    日历包不可用则退化为日历日数：退化只会让滞后天数更大（更严），不会把断流判成健康。
    """
    if end <= start:
        return 0
    try:
        return len(trading_calendar.trading_days_in_range(start + datetime.timedelta(days=1), end))
    except Exception as e:  # noqa: BLE001 — 日历不可用不应吞掉断流告警
        log.warning("交易日区间计算失败（退化为日历日口径）: %s", e)
        return (end - start).days


def _check_tick_replay(
    replay_lag_h: float,
    biz_lag_days: int,
    alerter: Alerter,
    now: datetime.datetime | None = None,
) -> None:
    """僵尸回放 + 业务时间戳滞后检查（7×24，#ZOMBIE-REPLAY 2026-10-14）。

    与 _check_tick_freshness 的分工：
      - _check_tick_freshness = **盘中分钟级**端到端新鲜度（只在盘中交易窗内跑）；
      - 本检查 = **日级业务时间戳**判活，盘后/周末/节假日同样生效，专治
        "反复回放陈旧文件 + 盖新 ingest_ts" 的僵尸形态。

    判据两条，均只认业务时间戳，不认 ingest_ts：
      1. 滞后告警：max(trade_date) 落后最新交易日超过 biz_lag_days 个交易日 → 真断流；
      2. 回放告警：max(ingest_ts) 领先 max(timestamp) 超过 replay_lag_h 小时 →
         入库的是陈旧业务数据（僵尸回放特征）。

    Alerter 内置 300s 冷却：持续断供时每 5 分钟重复告警。
    """
    try:
        from zephyr.data import ch_reader

        tsv = ch_reader.query(
            f"SELECT max(timestamp), max(ingest_ts) FROM {_TBL_TICK_DEPTH} FORMAT TSV",  # noqa: bare-sql  独立探针脚本单一查询，无常驻 SQL 层可集中
            timeout=15,
        )
        parts = (tsv or "").strip().split("\t")
        if len(parts) < 2:
            return
        max_ts = _parse_ch_dt(parts[0])
        max_ingest = _parse_ch_dt(parts[1])
        now = now or now_utc().astimezone(_BIZ_TZ)  # 业务时区（北京时间）当日，非机器本地墙钟
        if max_ts is None:
            alerter.notify(
                "tick_replay",
                f"{_TBL_TICK_DEPTH} 无有效业务时间戳（空表或时间戳全损）",
                level=LEVEL_ERROR,
                source="tick_pipeline",
            )
            return

        # 判据 1：业务时间戳滞后（交易日口径）
        lag = _trading_days_between(max_ts.date(), now.date())
        if lag > biz_lag_days:
            alerter.notify(
                "tick_biz_lag",
                f"{_TBL_TICK_DEPTH} 业务时间戳滞后 {lag} 个交易日"
                f"（max(timestamp)={max_ts:%Y-%m-%d %H:%M:%S}，阈值 {biz_lag_days}）",
                level=LEVEL_ERROR,
                source="tick_pipeline",
            )
            log.error("tick 业务时间戳滞后: max(timestamp)=%s 落后 %d 个交易日", max_ts, lag)

        # 判据 2：僵尸回放（ingest_ts 显著领先业务时间戳）
        if max_ingest is not None:
            gap_h = (max_ingest - max_ts).total_seconds() / 3600.0
            if gap_h > replay_lag_h:
                alerter.notify(
                    "tick_replay",
                    f"{_TBL_TICK_DEPTH} 疑似僵尸回放：max(ingest_ts)={max_ingest:%Y-%m-%d %H:%M:%S} "
                    f"领先 max(timestamp)={max_ts:%Y-%m-%d %H:%M:%S} 达 {gap_h:.1f} 小时"
                    f"（阈值 {replay_lag_h:.0f}）",
                    level=LEVEL_ERROR,
                    source="tick_pipeline",
                )
                log.error("tick 僵尸回放告警: ingest 领先业务时间戳 %.1f 小时", gap_h)
    except Exception as e:  # noqa: BLE001 — 监控自身异常不逃逸
        log.warning("tick 回放/滞后检查异常: %s", e)


def main() -> None:
    interval = float(os.environ.get("CH_PROBE_INTERVAL", _DEFAULT_INTERVAL))
    threshold = int(os.environ.get("CH_PROBE_THRESHOLD", _DEFAULT_THRESHOLD))
    stale_min = float(os.environ.get("CH_PROBE_TICK_STALE_MIN", _DEFAULT_TICK_STALE_MIN))
    replay_lag_h = float(os.environ.get("CH_PROBE_REPLAY_LAG_H", _DEFAULT_REPLAY_LAG_H))
    biz_lag_days = int(os.environ.get("CH_PROBE_BIZ_LAG_DAYS", _DEFAULT_BIZ_LAG_DAYS))
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
        "探针已启动，7×24 监控 CH 连通性 + 盘中 tick 新鲜度（阈值 %.0f 分钟）"
        " + tick 业务时间戳滞后/僵尸回放（阈值 %d 交易日 / %.0f 小时）。状态变化时自动告警。",
        stale_min,
        biz_lag_days,
        replay_lag_h,
    )

    # 主循环：等待停止信号
    prev_state = SourceState.UNKNOWN
    last_freshness = 0.0
    last_replay = 0.0
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
            # 僵尸回放/业务时间戳滞后（日级，7×24，与盘中分钟级检查正交）
            if time.monotonic() - last_replay >= _REPLAY_CHECK_INTERVAL_S:
                last_replay = time.monotonic()
                _check_tick_replay(replay_lag_h, biz_lag_days, alerter)
            time.sleep(1)
    finally:
        monitor.stop()
        _PID_FILE.unlink(missing_ok=True)
        log.info("CH 健康探针已停止 (PID=%d)", os.getpid())


if __name__ == "__main__":
    main()
