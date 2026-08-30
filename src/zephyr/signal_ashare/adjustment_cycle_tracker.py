# [BLUEPRINT] MOD-SIG-040 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/22_sector_rotation_spec.md §3.1③
# [MODULE] zephyr.signal_ashare.adjustment_cycle_tracker
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.sector_adjustment; zephyr.data.ch_reader; zephyr.data.table_registry
# [CONSUMERS] (待 BM-BUY-04 分批建仓市场级门控 / 下游风控节流层)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] progress ∈ [0,1]; confidence ∈ [0,1]; drawdown_pct ∈ [0,1); 纯函数计算与 DB 加载隔离
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 纯函数输入长度不足/nh 序列长度不一致 → ValueError; loader 查询为空/失败 → AdjustmentCycleDataError
# [TESTS] tests/signal_ashare/test_adjustment_cycle_tracker.py
# [A_module] module_id=MOD-SIG-040 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 指数日 K 收盘序列 closes（默认 000300，loader 走 market_index_kline 真源表）
# I2: 可选新高占比序列 nh_ratios（板块扩散指标，调用方供给；None 时广度维降级）
# A1: 周期峰检测: trailing 250 日窗口最高收盘为周期峰，elapsed = 距峰交易日数
# A2: 调整判定: 当前回撤 ≥5% → 调整中; 创新高且窗内最大回撤 ≥5% → COMPLETE; 其余 → NO_ADJUSTMENT
# A3: 进度引擎复用 sector_adjustment.compute_adjustment_progress（0.4 时间+0.3 回撤+0.3 扩散）;
#     扩散数据缺失时剔除广度维、权重按 0.4:0.3 重归一
# A4: 相位分带: progress <0.4 EARLY / [0.4,0.8) MID / ≥0.8 LATE; action 透传 sector_adjustment
# O1: AdjustmentCycleSnapshot（相位 + 进度 + 动作 + 置信度，供下游风控节流消费）
# [/ALGO_FLOW]
"""
调整周期追踪器（市场级，22 号 spec §3.1③ 同源，MOD-SIG-040）。

追踪市场（指数级）调整周期走到哪了：自动定位周期峰、计算调整已持续交易日
与当前回撤深度，进度引擎复用 sector_adjustment 的三维加权（0.4 时间 + 0.3
回撤 + 0.3 扩散恢复），输出市场级相位与动作门控——进度 ≥80%（LATE）才允许
分批低吸，初期 <40%（EARLY）直接拦截，供下游风控节流消费。

与 sector_adjustment 的分工：sector_adjustment 是板块级纯函数计算器（输入
手工供给的标量）；本模块是市场级时序追踪器（输入指数收盘序列，自动找峰/
算持续天数/追踪扩散序列），两者经 compute_adjustment_progress 复用同源公式，
不重复实现。

扩散指标（新高占比序列）由调用方注入（如板块广度链路）；缺省时广度维剔除、
时间/回撤权重按 0.4:0.3 重归一（降级友好）。

定位红线：输出是相位/进度/置信度状态，非择时买卖信号。阈值（回撤门槛 5%、
预期窗口 20 日、目标回撤 15%）为初拟，与 sector_adjustment 同源待 G05/G08 校准。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: closes 参数
#   fields: 参数 closes，类型注解 Sequence[float]
#   code: adjustment_cycle_tracker.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: lookback 参数
#   fields: 参数 lookback，类型注解 int
#   code: adjustment_cycle_tracker.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: nh_ratios 参数
#   fields: 参数 nh_ratios，类型注解 Sequence[float] | None
#   code: adjustment_cycle_tracker.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: config 参数
#   fields: 参数 config，类型注解 AdjustmentCycleConfig | None
#   code: adjustment_cycle_tracker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① find_cycle_peak
#   name_en: find_cycle_peak
#   intro: 周期峰下标：trailing lookback 窗口内最高收盘的位置（并列取最早）。
#   desc: 周期峰下标：trailing lookback 窗口内最高收盘的位置（并列取最早）。；源码 L194-L202
#   inputs: closes lookback
#   outputs: int
# - id: A2
#   name_zh: ② track_adjustment_cycle
#   name_en: track_adjustment_cycle
#   intro: 核心纯函数：收盘序列（+可选新高占比序列）→ 调整周期快照。
#   desc: 核心纯函数：收盘序列（+可选新高占比序列）→ 调整周期快照。 Args: closes: 指数收盘序列（升序），长度 ≥ config.min_history。 nh_ratio…；源码 L205-L299
#   inputs: closes nh_ratios config
#   outputs: AdjustmentCycleSnapshot
# - id: A3
#   name_zh: ③ AdjustmentCycleTracker
#   name_en: AdjustmentCycleTracker
#   intro: 调整周期追踪器（DB 加载层薄封装，计算全部委托纯函数）。
#   desc: 调整周期追踪器（DB 加载层薄封装，计算全部委托纯函数）。 DB 依赖注入：query_fn 默认走项目既有 data 层 ch_reader.query（TSV）， regis…；公共方法（定义序）: load_in…
#   inputs: registry query_fn config
#   outputs: 返回值
#   （注：A3 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 BM-BUY-04 分批建仓市场级门控 / 下游风控节流层)
# - id: O2
#   name_zh: AdjustmentCycleSnapshot
#   name_en: AdjustmentCycleSnapshot
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 BM-BUY-04 分批建仓市场级门控 / 下游风控节流层)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Sequence

from zephyr.signal_ashare.sector_adjustment import (
    PROGRESS_ACTIVATE,
    PROGRESS_BLOCK,
    adjustment_action,
    compute_adjustment_progress,
)

_logger = logging.getLogger(__name__)

__all__: Final = [
    "AdjustmentCycleConfig",
    "AdjustmentCycleDataError",
    "AdjustmentCycleSnapshot",
    "AdjustmentCycleTracker",
    "CyclePhase",
    "find_cycle_peak",
    "track_adjustment_cycle",
]

#: 默认市场代理指数（沪深300）
DEFAULT_MARKET_SYMBOL: Final = "000300"

#: 非调整/完成相位的动作占位（不触发任何门控）
ACTION_NONE: Final = "NONE"

#: 三维权重（与 sector_adjustment 同源 22 号 spec §3.1③；扩散维缺省时按此重归一）
_W_TIME: Final = 0.4
_W_DRAWDOWN: Final = 0.3

# SQL 模板常量（_SQL_* 前缀约定）
_SQL_INDEX_KLINE = (
    "SELECT trade_date, close FROM {table} FINAL "
    "WHERE symbol = '{symbol}' "
    "AND trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "ORDER BY trade_date"
)


class AdjustmentCycleDataError(Exception):
    """调整周期数据加载失败（loader 查询为空/解析失败）。"""


class CyclePhase(str, Enum):
    """调整周期相位（市场级）"""

    NO_ADJUSTMENT = "NO_ADJUSTMENT"  # 未处于调整中（创新高无深回撤 / 轻微回撤）
    EARLY = "EARLY"  # 调整初期（progress < 0.4）——拦截低吸
    MID = "MID"  # 调整中期（0.4 ≤ progress < 0.8）——观察
    LATE = "LATE"  # 调整末期（progress ≥ 0.8）——允许分批低吸
    COMPLETE = "COMPLETE"  # 调整完成（深回撤后创新高确认结束）


@dataclass(frozen=True)
class AdjustmentCycleConfig:
    """调整周期追踪配置（阈值为初拟，与 sector_adjustment 同源待校准）。"""

    lookback: int = 250  # 周期峰回看窗口（交易日）
    min_drawdown: float = 0.05  # 调整成立的最小回撤门槛
    expected_window: int = 20  # 预期调整窗口（交易日，时间维分母）
    target_drawdown: float = 0.15  # 预期回撤深度（回撤维分母）
    min_history: int = 30  # 最少输入交易日数


@dataclass(frozen=True)
class AdjustmentCycleSnapshot:
    """调整周期快照（输出契约：相位 + 进度 + 动作 + 置信度，非买卖信号）。"""

    phase: CyclePhase
    progress: float  # 调整进度 ∈ [0, 1]（COMPLETE 记 1.0）
    action: str  # sector_adjustment ACTION_* 或 "NONE"（非调整/完成不门控）
    days_elapsed: int  # 距周期峰交易日数
    drawdown_pct: float  # 当前回撤深度（正数）
    peak_close: float  # 周期峰收盘价
    confidence: float  # ∈ [0, 1]
    n_days: int  # 输入序列长度


def find_cycle_peak(closes: Sequence[float], lookback: int = 250) -> int:
    """周期峰下标：trailing lookback 窗口内最高收盘的位置（并列取最早）。"""
    n = len(closes)
    start = max(0, n - lookback)
    peak_idx = start
    for i in range(start + 1, n):
        if closes[i] > closes[peak_idx]:
            peak_idx = i
    return peak_idx


def track_adjustment_cycle(
    closes: Sequence[float],
    nh_ratios: Sequence[float] | None = None,
    config: AdjustmentCycleConfig | None = None,
) -> AdjustmentCycleSnapshot:
    """核心纯函数：收盘序列（+可选新高占比序列）→ 调整周期快照。

    Args:
        closes: 指数收盘序列（升序），长度 ≥ config.min_history。
        nh_ratios: 新高占比序列（与 closes 等长对齐；None 时广度维降级重归一）。
        config: 配置。

    Raises:
        ValueError: 输入长度不足，或 nh_ratios 与 closes 长度不一致。
    """
    cfg = config or AdjustmentCycleConfig()
    n = len(closes)
    if n < cfg.min_history:
        raise ValueError(f"closes 长度 {n} 不足 min_history={cfg.min_history}")
    if nh_ratios is not None and len(nh_ratios) != n:
        raise ValueError(f"nh_ratios 长度 {len(nh_ratios)} 与 closes 长度 {n} 不一致")

    start = max(0, n - cfg.lookback)
    peak_idx = find_cycle_peak(closes, cfg.lookback)
    peak_close = closes[peak_idx]
    current = closes[-1]
    elapsed = n - 1 - peak_idx
    drawdown = 1.0 - current / peak_close if peak_close > 0 else 0.0

    # 窗内最大回撤（自运行峰值的最大落差，用于 COMPLETE 判定）
    max_dd = 0.0
    running_peak = closes[start]
    for i in range(start, n):
        if closes[i] > running_peak:
            running_peak = closes[i]
        dd_i = 1.0 - closes[i] / running_peak if running_peak > 0 else 0.0
        if dd_i > max_dd:
            max_dd = dd_i

    prev_peak = max(closes[start:-1]) if n - 1 > start else peak_close
    at_new_high = current >= prev_peak

    if at_new_high and max_dd >= cfg.min_drawdown:
        phase = CyclePhase.COMPLETE
        progress = 1.0
        action = ACTION_NONE
        clarity = 1.0
    elif at_new_high or drawdown < cfg.min_drawdown:
        phase = CyclePhase.NO_ADJUSTMENT
        progress = 0.0 if at_new_high else min(drawdown / cfg.min_drawdown, 1.0) * PROGRESS_BLOCK
        action = ACTION_NONE
        clarity = min(1.0, (cfg.min_drawdown - drawdown) / cfg.min_drawdown) if not at_new_high else 1.0
    else:
        # 调整中：进度引擎（扩散维可选降级）
        time_prog = min(elapsed / cfg.expected_window, 1.0) if cfg.expected_window > 0 else 1.0
        dd_prog = min(drawdown / cfg.target_drawdown, 1.0) if cfg.target_drawdown > 0 else 1.0
        if nh_ratios is not None:
            nh_current = nh_ratios[-1]
            nh_trough = min(nh_ratios[peak_idx:])
            nh_peak = max(nh_ratios[start : peak_idx + 1])
            progress = compute_adjustment_progress(
                elapsed_days=elapsed,
                drawdown_pct=drawdown,
                nh_ratio_current=nh_current,
                nh_ratio_trough=nh_trough,
                nh_ratio_peak=nh_peak,
                expected_window=cfg.expected_window,
                target_drawdown=cfg.target_drawdown,
            )
        else:
            # 广度维剔除，时间/回撤权重按 0.4:0.3 重归一（降级友好）
            progress = (_W_TIME * time_prog + _W_DRAWDOWN * dd_prog) / (_W_TIME + _W_DRAWDOWN)
            progress = max(0.0, min(1.0, progress))
        if progress >= PROGRESS_ACTIVATE:
            phase = CyclePhase.LATE
        elif progress >= PROGRESS_BLOCK:
            phase = CyclePhase.MID
        else:
            phase = CyclePhase.EARLY
        action = adjustment_action(progress)
        clarity = min(1.0, drawdown / cfg.min_drawdown)

    sample_factor = min(1.0, n / (2.0 * cfg.min_history))
    confidence = max(0.0, min(1.0, 0.4 * sample_factor + 0.6 * clarity))

    return AdjustmentCycleSnapshot(
        phase=phase,
        progress=progress,
        action=action,
        days_elapsed=elapsed,
        drawdown_pct=drawdown,
        peak_close=peak_close,
        confidence=confidence,
        n_days=n,
    )


class AdjustmentCycleTracker:
    """调整周期追踪器（DB 加载层薄封装，计算全部委托纯函数）。

    DB 依赖注入：query_fn 默认走项目既有 data 层 ch_reader.query（TSV），
    registry 默认 get_registry()（表名经 TableRegistry 派生，禁止硬编码）。
    扩散指标序列由调用方注入（如板块广度链路），本类不自建数据管道。
    """

    def __init__(
        self,
        registry: object = None,
        query_fn: Callable[..., str] | None = None,
        config: AdjustmentCycleConfig | None = None,
    ) -> None:
        self._registry = registry
        self._query_fn = query_fn
        self._config = config or AdjustmentCycleConfig()

    def _resolve_query_fn(self) -> Callable[..., str]:
        if self._query_fn is not None:
            return self._query_fn
        from zephyr.data import ch_reader  # 延迟导入，保持纯函数路径零 DB 依赖

        return ch_reader.query

    def _resolve_table(self) -> str:
        registry = self._registry
        if registry is None:
            from zephyr.data.table_registry import get_registry

            registry = get_registry()
        return registry.table("market_index_kline")

    def load_index_closes(
        self,
        symbol: str = DEFAULT_MARKET_SYMBOL,
        start: str = "2010-01-01",
        end: str = "2099-12-31",
    ) -> list[float]:
        """从 market_index_kline 加载指数收盘序列（升序）。

        Raises:
            AdjustmentCycleDataError: 查询为空或无可解析行。
        """
        sql = _SQL_INDEX_KLINE.format(table=self._resolve_table(), symbol=symbol, start=start, end=end)
        tsv = self._resolve_query_fn()(sql)
        closes: list[float] = []
        for line in (tsv or "").strip().split("\n"):
            parts = line.rstrip("\r").split("\t")
            if len(parts) >= 2:
                try:
                    closes.append(float(parts[1]))
                except ValueError:
                    _logger.warning("adjustment_cycle_tracker 跳过不可解析行: %s", line[:80])
        if not closes:
            raise AdjustmentCycleDataError(f"market_index_kline 查询为空: symbol={symbol}, [{start}, {end}]")
        return closes

    def track(
        self,
        symbol: str = DEFAULT_MARKET_SYMBOL,
        start: str = "2010-01-01",
        end: str = "2099-12-31",
        nh_ratios: Sequence[float] | None = None,
    ) -> AdjustmentCycleSnapshot:
        """加载指数日 K 并输出调整周期快照（计算委托 track_adjustment_cycle）。"""
        closes = self.load_index_closes(symbol, start, end)
        return track_adjustment_cycle(closes, nh_ratios, self._config)
