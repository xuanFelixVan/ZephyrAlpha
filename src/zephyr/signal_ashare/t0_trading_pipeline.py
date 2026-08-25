# [BLUEPRINT] MOD-SIG-090 | docs/03_modules/_domain_signal/t0_trading_pipeline/blueprint.md
# [MODULE] zephyr.signal_ashare.t0_trading_pipeline
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.t0_point_analyzer（MOD-SIG-068 信号源复用，testing）；executor 注入契约（生产侧由集成批接 MOD-SELL-018 t_trade_coordinator，本模块不 import 跨域 sell_decision）
# [CONSUMERS] （候选：做T分析页、45号 W2 平开平走格做T动作联动）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 底仓自平衡为最高不变量（任意路径结束当日净腿量=0，破坏即升级 escalation）；单轮买量=卖量；轮次≤max_rounds；延迟预算耗尽不再开新轮但平衡腿仍闭合；回滚失败不静默（escalation+notes）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B1-00191 行 + 候选注册表 CAND-TESTB-005
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空 bars/非法配置/缺 executor → ValueError（fail-closed）；执行失败走回滚路径非异常
# [TESTS] tests/signal_ashare/test_t0_trading_pipeline.py
# [A_module] module_id=MOD-SIG-090 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""C-012 做T日内套利管线（MOD-SIG-090，B1-00191）。

做T信号点（MOD-SIG-068）与 t_trade_coordinator（MOD-SELL-018）在，独立做T
信号管线与盘中即时反应决策引擎未收口（深挖裁定理由）。本模块收口全链路：

    信号（MOD-SIG-068 generate_t0_signals 复用）
    → 决策（硬约束过滤：底仓/价差/次数/手数/置信度/延迟预算）
    → 执行（executor 注入契约；生产接线 MOD-SELL-018 留集成批）
    → 当日复盘（T0DayReport：轮次/价差/延迟/回滚/升级留痕）

**硬约束**（全部 fail-closed 配置校验 + 运行时强制）：
- 底仓自平衡：单轮买量=卖量；当日净腿量=0（最高不变量，优先级高于延迟预算）；
- 单轮最小价差 min_spread_pct（不达标的配对信号跳过继续等）；
- 当日轮次上限 max_rounds；单腿股数≤底仓且手数对齐。

**延迟预算**：累计成交延迟超 latency_budget_ms → aborted，不再开新轮；
轮内平衡腿仍须闭合（平衡>预算，违例留 notes）。

**失败回滚**：平衡腿未成交 → 反向腿回滚恢复底仓；回滚再失败 →
escalation=True + "回滚失败" notes（fail-closed 留痕，不静默）。

**尾盘强制平衡**：EOD 未闭合轮按末 bar 收盘价强制闭合，保底仓不变量。

不做什么：不直连券商（executor 注入）、不重复做T点位算法（MOD-SIG-068）、
不涉交易成本口径（归执行层/宪章§3约束一）。

依据: AUD-DRAFT-001 深挖批 B1-00191（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-090
Version: 0.1.0

# [ALGO_FLOW]
# 输入: list[MinuteBar] + T0Context + executor 注入
# 特征: MOD-SIG-068 T买/T卖信号（置信度过滤）
# 算法: 信号流逐条配对开/闭轮 → 硬约束过滤 → 双腿执行 → 失败回滚/EOD强平
# 输出: T0DayReport（rounds/completed_rounds/realized_spread_pct/aborted/escalation/notes）
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Final

from zephyr.signal_ashare.t0_point_analyzer import (
    T_BUY,
    T_SELL,
    MinuteBar,
    T0AnalyzerConfig,
    T0Context,
    generate_t0_signals,
)

logger = logging.getLogger(__name__)

__all__: Final = [
    "T0DayReport",
    "T0Fill",
    "T0OrderIntent",
    "T0PipelineConfig",
    "T0RoundResult",
    "T0TradingPipeline",
]

#: 轮次终态封闭集
STATUS_COMPLETED: Final[str] = "completed"
STATUS_ROLLED_BACK: Final[str] = "rolled_back"
STATUS_FORCED_CLOSED: Final[str] = "forced_closed"


@dataclass(frozen=True, slots=True)
class T0PipelineConfig:
    """做T管线配置（硬约束全可配，MVP 初拍值）。"""

    base_position: int = 1000  # 底仓股数
    lot_size: int = 100  # 手数
    min_spread_pct: float = 0.5  # 单轮最小价差 %
    max_rounds: int = 3  # 当日轮次上限
    trade_volume: int = 300  # 单腿股数
    latency_budget_ms: float = 500.0  # 全链路延迟预算 ms
    signal_confidence_min: float = 0.0  # 信号置信度下限（0~100，MOD-SIG-068 口径）

    def __post_init__(self) -> None:
        if self.base_position <= 0:
            raise ValueError(f"base_position 须>0: {self.base_position}")
        if self.trade_volume <= 0 or self.trade_volume > self.base_position:
            raise ValueError(
                f"trade_volume 须∈(0,base_position]: {self.trade_volume}/{self.base_position}"
            )
        if self.lot_size <= 0 or self.trade_volume % self.lot_size != 0:
            raise ValueError(
                f"trade_volume({self.trade_volume}) 须按 lot_size({self.lot_size}) 手数对齐"
            )
        if self.max_rounds < 1:
            raise ValueError(f"max_rounds 须≥1: {self.max_rounds}")
        if self.min_spread_pct <= 0:
            raise ValueError(f"min_spread_pct 须>0: {self.min_spread_pct}")
        if self.latency_budget_ms <= 0:
            raise ValueError(f"latency_budget_ms 须>0: {self.latency_budget_ms}")
        if not 0.0 <= self.signal_confidence_min <= 100.0:
            raise ValueError(f"signal_confidence_min 须∈[0,100]: {self.signal_confidence_min}")


@dataclass(frozen=True, slots=True)
class T0OrderIntent:
    """执行意图（executor 契约入参）。"""

    symbol: str
    side: str  # BUY / SELL
    volume: int
    price: float
    reason: str


@dataclass(frozen=True, slots=True)
class T0Fill:
    """执行回报（executor 契约出参）。"""

    filled: bool
    price: float
    latency_ms: float
    note: str = ""


@dataclass(frozen=True, slots=True)
class T0RoundResult:
    """单轮做T结果。"""

    round_no: int
    open_side: str  # 开轮腿方向 BUY/SELL
    open_price: float
    close_price: float
    volume: int
    spread_pct: float  # 实现价差 %（卖出-买入口径，负=亏损轮）
    status: str  # completed / rolled_back / forced_closed
    rolled_back: bool
    latency_ms: float
    open_ts: str
    close_ts: str
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class T0DayReport:
    """做T当日复盘。"""

    symbol: str
    trade_date: str
    rounds: tuple[T0RoundResult, ...]
    completed_rounds: int
    realized_spread_pct: float  # 已完成+强制闭合轮价差合计 %
    total_latency_ms: float
    aborted: bool  # 延迟预算耗尽
    escalation: bool  # 底仓平衡被破坏/回滚失败升级
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


class _OpenRound:
    """轮内可变状态（非契约，仅运行期）。"""

    __slots__ = ("side", "open_price", "open_ts", "latency_ms", "round_no")

    def __init__(self, round_no: int, side: str, open_price: float, open_ts: str, latency_ms: float) -> None:
        self.round_no = round_no
        self.side = side
        self.open_price = open_price
        self.open_ts = open_ts
        self.latency_ms = latency_ms


class T0TradingPipeline:
    """C-012 做T管线：信号→决策→执行→复盘（底仓自平衡最高不变量）。"""

    def __init__(
        self,
        config: T0PipelineConfig,
        executor: Callable[[T0OrderIntent], T0Fill],
    ) -> None:
        if executor is None:
            raise ValueError("executor 不能为空（执行契约注入，fail-closed）")
        self._cfg = config
        self._executor = executor

    def _execute(self, symbol: str, side: str, price: float, reason: str) -> T0Fill:
        return self._executor(
            T0OrderIntent(
                symbol=symbol,
                side=side,
                volume=self._cfg.trade_volume,
                price=price,
                reason=reason,
            )
        )

    def run_day(
        self,
        bars: list[MinuteBar],
        context: T0Context,
        analyzer_config: T0AnalyzerConfig | None = None,
    ) -> T0DayReport:
        """单日做T主流程：信号配对开闭轮 → 硬约束 → 执行 → 复盘。"""
        if not bars:
            raise ValueError("bars 不能为空")
        cfg = self._cfg
        symbol = context.symbol
        signals = [
            s
            for s in generate_t0_signals(bars, context, analyzer_config)
            if s.confidence >= cfg.signal_confidence_min
        ]

        rounds: list[T0RoundResult] = []
        notes: list[str] = []
        open_round: _OpenRound | None = None
        completed = 0
        total_latency = 0.0
        aborted = False
        escalation = False
        realized = 0.0
        next_round_no = 1

        for sig in signals:
            if open_round is None:
                if aborted or completed >= cfg.max_rounds:
                    continue
                side = "SELL" if sig.direction == T_SELL else "BUY"
                fill = self._execute(symbol, side, sig.price, f"开轮{sig.direction}@{sig.pattern}")
                total_latency += fill.latency_ms
                if not fill.filled:
                    notes.append(f"开轮腿未成交@{sig.ts}（{sig.pattern}），放弃该信号")
                    continue
                open_round = _OpenRound(next_round_no, side, fill.price, sig.ts, fill.latency_ms)
                next_round_no += 1
                if total_latency > cfg.latency_budget_ms:
                    aborted = True
                    notes.append("延迟预算耗尽，不再开新轮（轮内平衡腿仍闭合）")
                continue

            # 轮内：等反向信号闭轮
            want = T_BUY if open_round.side == "SELL" else T_SELL
            if sig.direction != want:
                continue
            spread = (
                (open_round.open_price - sig.price) / open_round.open_price * 100.0
                if open_round.side == "SELL"
                else (sig.price - open_round.open_price) / open_round.open_price * 100.0
            )
            if spread < cfg.min_spread_pct:
                notes.append(
                    f"配对信号@{sig.ts} 价差 {spread:.3f}%<{cfg.min_spread_pct}%，跳过继续等"
                )
                continue

            close_side = "BUY" if open_round.side == "SELL" else "SELL"
            fill2 = self._execute(symbol, close_side, sig.price, f"闭轮{sig.direction}@{sig.pattern}")
            total_latency += fill2.latency_ms
            latency = open_round.latency_ms + fill2.latency_ms

            if fill2.filled:
                real_spread = (
                    (open_round.open_price - fill2.price) / open_round.open_price * 100.0
                    if open_round.side == "SELL"
                    else (fill2.price - open_round.open_price) / open_round.open_price * 100.0
                )
                realized += real_spread
                completed += 1
                rounds.append(
                    T0RoundResult(
                        round_no=open_round.round_no,
                        open_side=open_round.side,
                        open_price=open_round.open_price,
                        close_price=fill2.price,
                        volume=cfg.trade_volume,
                        spread_pct=real_spread,
                        status=STATUS_COMPLETED,
                        rolled_back=False,
                        latency_ms=latency,
                        open_ts=open_round.open_ts,
                        close_ts=sig.ts,
                    )
                )
            else:
                # 平衡腿失败 → 反向回滚开轮腿
                rb_side = "SELL" if open_round.side == "BUY" else "BUY"
                rb = self._execute(symbol, rb_side, sig.price, f"回滚{open_round.side}腿")
                total_latency += rb.latency_ms
                latency += rb.latency_ms
                rb_notes: list[str] = [f"平衡腿未成交@{sig.ts}，触发回滚"]
                if not rb.filled:
                    escalation = True
                    notes.append(f"回滚失败@{sig.ts}，底仓平衡被破坏，升级人工")
                    rb_notes.append("回滚失败")
                rounds.append(
                    T0RoundResult(
                        round_no=open_round.round_no,
                        open_side=open_round.side,
                        open_price=open_round.open_price,
                        close_price=sig.price,
                        volume=cfg.trade_volume,
                        spread_pct=0.0,
                        status=STATUS_ROLLED_BACK,
                        rolled_back=rb.filled,
                        latency_ms=latency,
                        open_ts=open_round.open_ts,
                        close_ts=sig.ts,
                        notes=tuple(rb_notes),
                    )
                )
            open_round = None
            if total_latency > cfg.latency_budget_ms and not aborted:
                aborted = True
                notes.append("延迟预算耗尽，不再开新轮")

        # ── EOD：未闭合轮尾盘强制平衡（平衡不变量优先于一切）──
        if open_round is not None:
            close_side = "BUY" if open_round.side == "SELL" else "SELL"
            last_price = bars[-1].close
            fill = self._execute(symbol, close_side, last_price, "尾盘强制平衡")
            total_latency += fill.latency_ms
            eod_notes = ["尾盘强制平衡闭合"]
            if fill.filled:
                spread = (
                    (open_round.open_price - fill.price) / open_round.open_price * 100.0
                    if open_round.side == "SELL"
                    else (fill.price - open_round.open_price) / open_round.open_price * 100.0
                )
                realized += spread
                rounds.append(
                    T0RoundResult(
                        round_no=open_round.round_no,
                        open_side=open_round.side,
                        open_price=open_round.open_price,
                        close_price=fill.price,
                        volume=cfg.trade_volume,
                        spread_pct=spread,
                        status=STATUS_FORCED_CLOSED,
                        rolled_back=False,
                        latency_ms=open_round.latency_ms + fill.latency_ms,
                        open_ts=open_round.open_ts,
                        close_ts=bars[-1].ts,
                        notes=tuple(eod_notes),
                    )
                )
                notes.append("尾盘强制平衡：未闭合轮按末 bar 价闭合")
            else:
                escalation = True
                notes.append("尾盘强制平衡未成交，底仓平衡被破坏，升级人工")
                rounds.append(
                    T0RoundResult(
                        round_no=open_round.round_no,
                        open_side=open_round.side,
                        open_price=open_round.open_price,
                        close_price=last_price,
                        volume=cfg.trade_volume,
                        spread_pct=0.0,
                        status=STATUS_ROLLED_BACK,
                        rolled_back=False,
                        latency_ms=open_round.latency_ms + fill.latency_ms,
                        open_ts=open_round.open_ts,
                        close_ts=bars[-1].ts,
                        notes=tuple(eod_notes + ["强制平衡未成交"]),
                    )
                )

        if not rounds and not notes:
            notes.append("无达标信号，当日未开轮")

        logger.info(
            "做T复盘: %s 完成=%d 价差=%.3f%% 中止=%s 升级=%s",
            symbol, completed, realized, aborted, escalation,
        )
        return T0DayReport(
            symbol=symbol,
            trade_date=bars[0].ts[:10],
            rounds=tuple(rounds),
            completed_rounds=completed,
            realized_spread_pct=realized,
            total_latency_ms=total_latency,
            aborted=aborted,
            escalation=escalation,
            notes=tuple(notes),
        )
