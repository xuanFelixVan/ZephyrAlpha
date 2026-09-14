# [BLUEPRINT] MOD-SIG-145 | docs/03_modules/_domain_signal/pattern_event_stats/blueprint.md
# [MODULE] zephyr.signal_ashare.strategy_signal.pattern_event_job
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] scripts.data.pattern_event_backfill(扫描器正身,subprocess); scripts.data.pattern_win_rate_materialize(物化正身,subprocess); zephyr.signal_ashare.strategy_signal.pattern_signal_runtime(调权正身,subprocess -m,消费班 W-C3)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider(pattern_event/pattern_win_rate_materialize/pattern_weight_sync capability 分支,JOB-108+消费班 W-C3)
# [STARTUP] imported(经调度器 daily_kline 档事件触发;禁 cron 自轮询)
# [MATURITY] design
# [INVARIANTS] 薄适配零业务逻辑(窗口组装+退出码透传+记账,扫描/物化真源在 scripts/data 正身); 扫描器自行经 pattern_event_store 落库(本模块不碰 CH); 子进程 stdout 按 UTF-8 解码(Windows GBK 默认会炸中文 JSON); FetchResult 空 rows 仅记账(rows_fetched=子进程实产行数,推进游标+避免 0 行 WARN 误报); 失败经 FetchResult.error 传播(scheduler 判 FAILED)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 子进程退出码非0->FetchResult.error(scheduler 记 FAILED); stdout 尾行非 JSON->记账降级 rows_fetched=0 不炸(扫描结果以库为准)
# [TESTS] tests/signal_ashare/strategy_signal/test_pattern_event_job.py(打桩 subprocess,不触库)
# [A_module] module_id=MOD-SIG-145 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""pattern_event 增量/物化的调度器薄适配（MOD-SIG-145 W4b，JOB-108）。

接线拓扑（声明式 DAG，tasks.yaml 为真源）::

    kline_daily_incremental（日K线落地）
      → pattern_event_incremental（本模块 run_incremental：滚动窗重扫，
        只产出近 15 日确认事件；确定性 event_id + ReplacingMergeTree 幂等）
        → pattern_win_rate_materialize（本模块 run_win_rate_materialize：
          事件表×日K 全量重算胜率统计，ReplacingMergeTree 同键取最新）
        → pattern_weight_sync（本模块 run_weight_sync：消费班 W-C3——
          物化完成后拉统计→Wilson 口径录样本→131 限幅调权→权重状态持久化）

为什么是 subprocess 而非 import：扫描/物化的真身在 scripts/data 两个 CLI
（W2/W3 已实弹落码），其 main() 承载完整参数与环境装配（ensure_ch_env_loaded、
断点续扫 state 文件）。适配层保持"零业务逻辑"——只组装窗口参数、透传退出码、
把子进程实产行数记账进 FetchResult；逻辑升级只动 scripts 侧，本模块零改动。
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from collections.abc import Iterator
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from zephyr.data.provider_base import FetchResult

logger = logging.getLogger(__name__)

# A股日历日=北京日界（窗口字符串喂给 scripts 正身的 --start/--end，非 DB 时间戳列）
_TZ = ZoneInfo("Asia/Shanghai")

# src/zephyr/signal_ashare/strategy_signal/ → 仓库根 = parents[4]
_REPO_ROOT = Path(__file__).resolve().parents[4]
_BACKFILL_SCRIPT = _REPO_ROOT / "scripts" / "data" / "pattern_event_backfill.py"
_MATERIALIZE_SCRIPT = _REPO_ROOT / "scripts" / "data" / "pattern_win_rate_materialize.py"
_SYNC_MODULE = "zephyr.signal_ashare.strategy_signal.pattern_signal_runtime"
_SYNC_STATE = _REPO_ROOT / "data" / "runtime" / "pattern_signal_weights.json"

_DEFAULT_LOOKBACK_DAYS = 15
_DEFAULT_CONTEXT_DAYS = 400  # 形态上下文（约 270 交易日），与 incremental CLI 同口径
_EVENT_TABLE = "c1_market.market_pattern_event"
_WIN_RATE_TABLE = "c1_market.market_pattern_win_rate"


def _run_script(script: Path, extra_args: list[str] | None = None) -> tuple[int, str]:
    """跑 scripts/data 正身脚本，返回 (退出码, stdout)。

    stderr 不捕获（透传父进程，扫描进度进调度器日志）；stdout 强制 UTF-8
    解码——Windows 子进程默认 GBK，中文 JSON summary 会直接 UnicodeDecodeError。
    """
    proc = subprocess.run(  # noqa: S603
        [sys.executable, str(script)] + (extra_args or []),
        capture_output=False,
        stdout=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return proc.returncode, proc.stdout or ""


def run_incremental(
    lookback_days: int = _DEFAULT_LOOKBACK_DAYS,
    context_days: int = _DEFAULT_CONTEXT_DAYS,
) -> Iterator[FetchResult]:
    """增量扫描：滚动窗调回填扫描器（自行落库），产出记账用 FetchResult。

    窗口口径与 scripts/data/pattern_event_incremental.py 一致：K 线读
    [今天-context_days, 今天] 全上下文，只产出 [今天-lookback_days, 今天]
    确认的事件（形态确认需要历史，窗口外仅作上下文）。重扫幂等不膨胀
    （确定性 event_id + ReplacingMergeTree）。
    """
    now = datetime.now(_TZ)
    end = now.strftime("%Y-%m-%d")
    emit_from = (now - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    start = (now - timedelta(days=context_days)).strftime("%Y-%m-%d")
    logger.info(
        "pattern_event 增量扫描启动: 上下文 %s..%s，产出窗口 %s 起",
        start, end, emit_from,
    )
    returncode, stdout = _run_script(
        _BACKFILL_SCRIPT,
        [
            "--start", start,
            "--end", end,
            "--emit-from", emit_from,
            "--data-source", "pattern_event_incremental",
        ],
    )
    if returncode != 0:
        yield FetchResult(
            table=_EVENT_TABLE, columns=[], rows=[], last_key=end,
            elapsed_sec=0.0,
            error=f"pattern_event_backfill 退出码 {returncode}（增量扫描失败，透传）",
        )
        return
    events = _parse_summary_events(stdout)
    logger.info("pattern_event 增量扫描完成: 实产事件 %d", events)
    yield FetchResult(
        table=_EVENT_TABLE, columns=[], rows=[], last_key=end,
        elapsed_sec=0.0, rows_fetched=events,
    )


def _parse_summary_events(stdout: str) -> int:
    """从扫描器 stdout 尾行 JSON summary 提取 events 数；解析失败降级 0。

    扫描结果真源在库（ReplacingMergeTree），记账仅用于调度器游标推进与
    0 行告警抑制——解析失败不构成失败（ERROR_CONTRACT）。
    """
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            summary = json.loads(line)
        except json.JSONDecodeError:
            continue
        events = summary.get("events")
        if isinstance(events, int):
            return events
    logger.warning("扫描器 stdout 未解析出 JSON summary，记账降级 rows_fetched=0")
    return 0


def run_win_rate_materialize() -> Iterator[FetchResult]:
    """胜率统计全量重物化：调 scripts/data 正身（自行写 CH），记账 FetchResult。

    全量重算重放（非增量）——统计粒度窗口随事件表整体刷新，ReplacingMergeTree
    同键取最新。挂在增量扫描任务的 DAG 下游（tasks.yaml dependencies 声明）。
    """
    logger.info("pattern_win_rate 胜率统计物化启动（全量重算）")
    returncode, stdout = _run_script(_MATERIALIZE_SCRIPT)
    end = datetime.now(_TZ).strftime("%Y-%m-%d")
    if returncode != 0:
        yield FetchResult(
            table=_WIN_RATE_TABLE, columns=[], rows=[], last_key=end,
            elapsed_sec=0.0,
            error=f"pattern_win_rate_materialize 退出码 {returncode}（物化失败，透传）",
        )
        return
    rows = _parse_materialized_rows(stdout)
    logger.info("pattern_win_rate 物化完成: %d 行", rows)
    yield FetchResult(
        table=_WIN_RATE_TABLE, columns=[], rows=[], last_key=end,
        elapsed_sec=0.0, rows_fetched=rows,
    )


def _parse_materialized_rows(stdout: str) -> int:
    """从物化脚本尾行 'OK: 物化 N 行 -> 表' 提取 N；解析失败降级 0（同上）。"""
    for line in reversed(stdout.strip().splitlines()):
        if "OK: 物化" in line:
            try:
                return int(line.split("物化")[1].split("行")[0].strip())
            except (IndexError, ValueError):
                break
    logger.warning("物化脚本 stdout 未解析出行数，记账降级 rows_fetched=0")
    return 0


def run_weight_sync() -> Iterator[FetchResult]:
    """调权同步（消费班 W-C3 钩子）：调 147 CLI --sync-weights（子进程隔离同族先例）。

    物化完成后事件触发（tasks.yaml pattern_weight_sync，DAG 依赖
    pattern_win_rate_materialize——统计落库才同步，禁 cron 自轮询）。
    CLI 正身读物化表→Wilson 口径录样本→131 限幅调权→权重状态 JSON 持久化
    （--state-path 钉仓库根绝对路径，防调度器 CWD 漂移）。
    记账 rows_fetched=本次调权信号数（stdout 尾行 JSON summary）。
    """
    logger.info("pattern_weight_sync 调权同步启动")
    cmd = [
        sys.executable, "-m", _SYNC_MODULE,
        "--sync-weights", "--state-path", str(_SYNC_STATE),
        "--reason", "materialize_done",
    ]
    proc = subprocess.run(  # noqa: S603
        cmd,
        capture_output=False,
        stdout=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    end = datetime.now(_TZ).strftime("%Y-%m-%d")
    if proc.returncode != 0:
        yield FetchResult(
            table=_WIN_RATE_TABLE, columns=[], rows=[], last_key=end,
            elapsed_sec=0.0,
            error=f"pattern_weight_sync 退出码 {proc.returncode}（调权同步失败，透传）",
        )
        return
    adjusted = _parse_sync_adjusted(proc.stdout or "")
    logger.info("pattern_weight_sync 完成: %d 信号调权", adjusted)
    yield FetchResult(
        table=_WIN_RATE_TABLE, columns=[], rows=[], last_key=end,
        elapsed_sec=0.0, rows_fetched=adjusted,
    )


def _parse_sync_adjusted(stdout: str) -> int:
    """从 CLI 尾行 JSON summary 提取 adjusted；解析失败降级 0（结果以状态文件为准）。"""
    import json as _json

    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{") and "adjusted" in line:
            try:
                return int(_json.loads(line).get("adjusted") or 0)
            except (ValueError, TypeError):
                break
    logger.warning("sync CLI stdout 未解析出 adjusted，记账降级 rows_fetched=0")
    return 0
