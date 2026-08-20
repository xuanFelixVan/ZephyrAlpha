# [BLUEPRINT] MOD-RK-08 | docs/03_modules/_domain_risk/liquidity_monitor/blueprint.md
# [MODULE] zephyr.risk.core.liquidity_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.risk_manager_base; pandas; numpy
# [CONSUMERS] MOD-L04-001(DefaultRiskManagerOrchestrator,流动性评估) ; MOD-RK-09(AshareSystemicRiskDetector,LIQUIDITY_CRISIS输入)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Amihud ILLIQ=|r_d|/V_d;成交量萎缩=V_t/MA(V,N);is_illiquid=Amihud超阈值 OR 成交量萎缩;纯机制零参数
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidLiquidityInputError
# [TESTS] tests/risk/core/test_liquidity_monitor.py
# [A_module] module_id=MOD-RK-08 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

D_RISK — Liquidity Monitor (MOD-RK-08)

流动性监控器——计算 Amihud 非流动性指标 + 成交量萎缩比率，产出
LiquidityMetrics。属 A 类基础设施（纯机制零参数）。

与 AshareSystemicRiskDetector 的 LIQUIDITY_CRISIS 信号互补:
  - 系统性风险检测器: 买卖价差扩大 + 卖盘压力 → 紧急性流动性危机（盘内）
  - 本模块: Amihud + 成交量萎缩 → 结构性流动性恶化（日频趋势）

核心公式 (blueprint §3):
  Amihud ILLIQ_d = |r_d| / V_d    (r_d=日收益率, V_d=日成交额)
  ILLIQ_N = (1/N) × Σ ILLIQ_d     (N日均值)
  V_ratio = V_t / MA(V, N)        (成交量萎缩比率, <1=萎缩)

日志埋点:
  - INFO: 评估完成（symbol + amihud + shrinkage + is_illiquid）
  - WARNING: 数据不足跳过（symbol + 原因）
  - DEBUG: 计算中间值（逐日 ILLIQ + MA）

CTR 契约:
  消费者 — OHLCV 标准化行情数据 (CTR-006)
  生产者 — LiquidityMetrics (CTR-P1-018)

SSoT: depgraph MOD-RK-08 | blueprint.md §3 核心规则

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: OHLCV行情数据 DataFrame
#   fields: 需close列+volume或amount列(优先amount成交额, 元) CTR-006标准化行情
#   code: assess() ohlcv L246 / _extract_ohlcv L392-416
# - id: I2
#   name: 买卖价差 浮点数可选
#   fields: bid_ask_spread外部提供, 仅透出不参与is_illiquid判定
#   code: assess() bid_ask_spread L247
# - id: I3
#   name: 阈值窗口参数 配置
#   fields: amihud_threshold默认1e-8 + volume_shrinkage_threshold默认0.5 + window默认20交易日
#   code: __init__() L122-130
# 层: 特征
# - id: F1
#   name_zh: Amihud非流动性
#   name_en: amihud_illiq
#   intro: 单位成交额推动的收益幅度, 越大越不流动
#   formula: r_d=close.pct_change; ILLIQ_d=|r_d|/V_d(剔零成交额); ILLIQ=tail(N).mean
#   code: liquidity_monitor.py L164-189
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: 成交量萎缩比率
#   name_en: volume_shrinkage_ratio
#   intro: 最新成交额相对前N日均量缩了多少
#   formula: V_ratio=V_t/MA(V[:-1].tail(N)); <1=萎缩 >1=放量; 数据<2点→1.0
#   code: liquidity_monitor.py L222-239
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 流动性综合评估
#   name_en: LiquidityMonitor.assess
#   intro: Amihud超阈值或成交量萎缩即判非流动性恶化
#   desc: is_illiquid=amihud>amihud_threshold OR shrinkage<shrinkage_threshold; 数据<2点WARNING并返回零值快照(不判定)
#   inputs: I1 I2 I3 F1 F2
#   outputs: LiquidityMetrics快照
#   invariant: is_illiquid=Amihud超阈值 OR 成交量萎缩
# - id: A2
#   name_zh: ② 风控检查结果转换
#   name_en: to_risk_check_result
#   intro: 流动性快照转RiskCheckResult供编排器聚合
#   desc: passed=!is_illiquid; limit=amihud_threshold; actual=amihud_illiq; severity非流动=HALT否则info
#   inputs: A1
#   outputs: RiskCheckResult
# 层: 输出
# - id: O1
#   name_zh: 流动性指标快照
#   name_en: LiquidityMetrics
#   intro: 单标的Amihud+萎缩比率+综合判定的不可变快照(CTR-P1-018生产契约)
#   downstream: DefaultRiskManagerOrchestrator MOD-L04-001(流动性评估); AshareSystemicRiskDetector MOD-RK-09(LIQUIDITY_CRISIS输入)
# - id: O2
#   name_zh: 风控检查结果
#   name_en: RiskCheckResult
#   intro: 供风控编排器统一聚合的流动性检查结果
#   downstream: DefaultRiskManagerOrchestrator MOD-L04-001
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I1 -.->|断点| F2
# F1 --> A1
# F2 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
# A1 --> A2
# A2 --> O2
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional

import numpy as np
import pandas as pd

from zephyr.risk.risk_manager_base import RiskCheckResult

_logger = logging.getLogger(__name__)

__all__ = [
    "InvalidLiquidityInputError",
    "LiquidityMetrics",
    "LiquidityMonitor",
    "OpeningPermission",
    "compute_stress_exit_days",
    "compute_lvar",
]


#: Amihud ILLIQ 阈值（A股经验值，>此值判定为非流动性恶化）
DEFAULT_AMIHUD_THRESHOLD: float = 1e-8

#: 成交量萎缩阈值（V_ratio < 此值判定为萎缩）
DEFAULT_VOLUME_SHRINKAGE_THRESHOLD: float = 0.5

#: 默认计算窗口（交易日）
DEFAULT_WINDOW: int = 20

# ── 90 号 Phase2 项（#8 流动性扩展）常量 ──
#: 压力情景 ADV 折扣（90 号 §8 裁定①）
STRESS_ADV_DISCOUNT: float = 0.3
#: 压力情景参与率（90 号 §8 裁定①）
STRESS_PARTICIPATION_RATE: float = 0.10
#: 压力退出时间上限（天，>1 天→禁新开仓，90 号 §8 裁定①）
MAX_STRESS_EXIT_DAYS: float = 1.0


class InvalidLiquidityInputError(ValueError):
    """流动性监控输入数据无效。"""


# ── 数据模型 ──────────────────────────────────────────────────────────


@dataclass(frozen=True)
class LiquidityMetrics:
    """单标的流动性指标快照（不可变）。

    Attributes:
        symbol: 标的代码
        amihud_illiq: Amihud 非流动性指标（N日均值，越高越不流动）
        volume_shrinkage_ratio: 成交量萎缩比率（<1=萎缩，>1=放量）
        bid_ask_spread: 买卖价差（可选，外部提供）
        is_illiquid: 综合判定（Amihud超阈值 OR 成交量萎缩）
        window: 计算窗口（交易日数）
        timestamp: 评估时间（UTC）
        idempotency_key: 幂等键
    """

    symbol: str
    amihud_illiq: float
    volume_shrinkage_ratio: float
    bid_ask_spread: float | None
    is_illiquid: bool
    window: int
    timestamp: datetime
    idempotency_key: str


# ── 90 号 Phase2 扩展数据模型与纯函数（#8 流动性）──


@dataclass(frozen=True)
class OpeningPermission:
    """开仓许可评估结果（90 号 §8 裁定①④）。"""

    symbol: str
    allowed: bool
    exit_days: float
    reasons: list[str]


def compute_stress_exit_days(
    position_value: float,
    adv_value: float,
    *,
    stress_discount: float = STRESS_ADV_DISCOUNT,
    participation_rate: float = STRESS_PARTICIPATION_RATE,
) -> float:
    """压力情景退出时间（90 号 §8 裁定①）。

    退出天数 = 持仓 / (ADV × 0.3 压力折扣 × 10% 参与率)

    Args:
        position_value: 持仓市值（元，≥0）
        adv_value: 日均成交额 ADV（元；≤0 视为流动性枯竭→inf）
        stress_discount: 压力情景 ADV 折扣（默认 0.3）
        participation_rate: 参与率（默认 0.10）

    Returns:
        退出天数；ADV≤0 时返回 inf（必然触发禁开仓）
    """
    if position_value < 0:
        raise ValueError("持仓市值不能为负")
    capacity = adv_value * stress_discount * participation_rate
    if capacity <= 0:
        return float("inf")
    return float(position_value) / capacity


def compute_lvar(var: float, exit_days: float, half_spread: float) -> float:
    """LVaR 简化式（90 号 §8 裁定③）。

    LVaR = VaR × √退出天数 + 半价差
    （完整 Kyle Lambda 估计器不建，日频 Amihud 已足够）
    """
    if var < 0 or exit_days < 0 or half_spread < 0:
        raise ValueError("VaR/退出天数/半价差不能为负")
    return var * float(np.sqrt(exit_days)) + half_spread


# ── 流动性监控器 ──────────────────────────────────────────────────────


class LiquidityMonitor:
    """流动性监控器——Amihud 非流动性指标 + 成交量萎缩比率。

    纯机制零参数：阈值和窗口为 C 类参数（有行业默认值），可在构造时
    覆盖。计算逻辑为标准 Amihud (2002) 公式，无业务策略参数。

    Usage:
        mon = LiquidityMonitor()
        metrics = mon.assess(symbol="600000.SH", ohlcv=df)
    """

    def __init__(
        self,
        amihud_threshold: float = DEFAULT_AMIHUD_THRESHOLD,
        volume_shrinkage_threshold: float = DEFAULT_VOLUME_SHRINKAGE_THRESHOLD,
        window: int = DEFAULT_WINDOW,
    ):
        self._amihud_threshold = amihud_threshold
        self._volume_shrinkage_threshold = volume_shrinkage_threshold
        self._window = window

    # ── Amihud 非流动性指标 ──

    def compute_amihud(
        self,
        closes: pd.Series,
        volumes: pd.Series,
        window: int | None = None,
    ) -> float:
        """计算 Amihud 非流动性指标（N日均值）。

        ILLIQ_d = |r_d| / V_d
        ILLIQ_N = (1/N) × Σ ILLIQ_d

        Args:
            closes: 收盘价序列（按日期升序）
            volumes: 成交额序列（按日期升序，单位：元）
            window: 计算窗口（默认用构造时的 window）

        Returns:
            Amihud ILLIQ 值（越高越不流动），数据不足返回 0.0

        Raises:
            InvalidLiquidityInputError: 输入长度不匹配或为空
        """
        n = window or self._window
        self._validate_inputs(closes, volumes)

        if len(closes) < 2:
            raise InvalidLiquidityInputError(f"Amihud 计算需 ≥2 个数据点，实际 {len(closes)}")

        # 日收益率: r_d = (close_d - close_{d-1}) / close_{d-1}
        returns = closes.pct_change().dropna()

        # 对齐 volume（去掉第一个，因为 return 无第一个）
        vol_aligned = volumes.iloc[1:]

        # 过滤零成交额（避免除零），设为 NaN 后 dropna
        with np.errstate(divide="ignore", invalid="ignore"):
            illiq_daily = (returns.abs() / vol_aligned).replace([np.inf, -np.inf], np.nan)
        illiq_daily = illiq_daily.dropna()

        if len(illiq_daily) == 0:
            return 0.0

        # 取最近 N 日均值
        illiq_n = illiq_daily.tail(n).mean()

        _logger.debug(
            "Amihud computed: data_points=%d window=%d illiq=%.2e",
            len(illiq_daily),
            min(n, len(illiq_daily)),
            illiq_n,
        )
        return float(illiq_n)

    # ── 成交量萎缩比率 ──

    def compute_volume_shrinkage(
        self,
        volumes: pd.Series,
        window: int | None = None,
    ) -> float:
        """计算成交量萎缩比率。

        V_ratio = V_t / MA(V, N)
        - V_t = 最新日成交额
        - MA(V, N) = N日成交额移动平均（不含当日）

        Args:
            volumes: 成交额序列（按日期升序）
            window: 计算窗口（默认用构造时的 window）

        Returns:
            萎缩比率（<1=萎缩，>1=放量），数据不足返回 1.0

        Raises:
            InvalidLiquidityInputError: 输入为空
        """
        n = window or self._window

        if len(volumes) == 0:
            raise InvalidLiquidityInputError("成交量序列为空")

        if len(volumes) < 2:
            return 1.0  # 数据不足，不判定萎缩

        # 最新日成交额
        v_today = float(volumes.iloc[-1])

        # N日移动平均（不含当日，用前 N 日）
        v_ma = float(volumes.iloc[:-1].tail(n).mean())

        if v_ma == 0:
            return 1.0  # 避免除零

        ratio = v_today / v_ma

        _logger.debug(
            "Volume shrinkage: v_today=%.2e v_ma=%.2e ratio=%.4f",
            v_today,
            v_ma,
            ratio,
        )
        return float(ratio)

    # ── 综合评估 ──

    def assess(
        self,
        symbol: str,
        ohlcv: pd.DataFrame,
        bid_ask_spread: float | None = None,
    ) -> LiquidityMetrics:
        """综合评估单标的流动性。

        Args:
            symbol: 标的代码
            ohlcv: OHLCV DataFrame，需含 close 列和 volume 或 amount 列
            bid_ask_spread: 买卖价差（可选，外部提供）
            window: 计算窗口（可选，覆盖默认值）

        Returns:
            LiquidityMetrics 流动性指标快照

        Raises:
            InvalidLiquidityInputError: 数据格式无效
        """
        closes, volumes = self._extract_ohlcv(ohlcv)

        if len(closes) < 2:
            _logger.warning(
                "Liquidity assessment skipped (insufficient data): symbol=%s data_points=%d",
                symbol,
                len(closes),
            )
            return LiquidityMetrics(
                symbol=symbol,
                amihud_illiq=0.0,
                volume_shrinkage_ratio=1.0,
                bid_ask_spread=bid_ask_spread,
                is_illiquid=False,
                window=self._window,
                timestamp=datetime.now(UTC),
                idempotency_key=f"liq-{symbol}-{uuid.uuid4().hex[:8]}",
            )

        amihud = self.compute_amihud(closes, volumes)
        shrinkage = self.compute_volume_shrinkage(volumes)

        is_illiquid = amihud > self._amihud_threshold or shrinkage < self._volume_shrinkage_threshold

        metrics = LiquidityMetrics(
            symbol=symbol,
            amihud_illiq=amihud,
            volume_shrinkage_ratio=shrinkage,
            bid_ask_spread=bid_ask_spread,
            is_illiquid=is_illiquid,
            window=self._window,
            timestamp=datetime.now(UTC),
            idempotency_key=f"liq-{symbol}-{uuid.uuid4().hex[:8]}",
        )

        _logger.info(
            "Liquidity assessed: symbol=%s amihud=%.2e shrinkage=%.4f is_illiquid=%s",
            symbol,
            amihud,
            shrinkage,
            is_illiquid,
        )
        return metrics

    # ── 批量评估 ──

    def assess_batch(
        self,
        ohlcv_map: dict[str, pd.DataFrame],
        bid_ask_spreads: dict[str, float] | None = None,
    ) -> list[LiquidityMetrics]:
        """批量评估多标的流动性。

        Args:
            ohlcv_map: {symbol: OHLCV DataFrame}
            bid_ask_spreads: {symbol: spread}（可选）

        Returns:
            list[LiquidityMetrics]
        """
        spreads = bid_ask_spreads or {}
        results: list[LiquidityMetrics] = []

        for symbol, ohlcv in ohlcv_map.items():
            try:
                metrics = self.assess(
                    symbol=symbol,
                    ohlcv=ohlcv,
                    bid_ask_spread=spreads.get(symbol),
                )
                results.append(metrics)
            except InvalidLiquidityInputError as exc:
                _logger.warning(
                    "Batch assess skipped: symbol=%s error=%s",
                    symbol,
                    exc,
                )

        illiquid_count = sum(1 for m in results if m.is_illiquid)
        _logger.info(
            "Batch assess complete: total=%d illiquid=%d",
            len(results),
            illiquid_count,
        )
        return results

    # ── 风控检查结果转换 ──

    def to_risk_check_result(
        self,
        metrics: LiquidityMetrics,
    ) -> RiskCheckResult:
        """将 LiquidityMetrics 转换为 RiskCheckResult（供编排器聚合）。

        Args:
            metrics: 流动性指标

        Returns:
            RiskCheckResult（passed=!is_illiquid, severity=HALT/WARNING）
        """
        return RiskCheckResult(
            check_id=f"liquidity-{metrics.symbol}",
            rule_name="liquidity_monitor",
            passed=not metrics.is_illiquid,
            limit_value=self._amihud_threshold,
            actual_value=metrics.amihud_illiq,
            message=(
                f"Amihud={metrics.amihud_illiq:.2e} "
                f"shrinkage={metrics.volume_shrinkage_ratio:.4f} "
                f"symbol={metrics.symbol}"
            ),
            severity="HALT" if metrics.is_illiquid else "info",
        )

    # ── 90 号 Phase2 扩展（#8 流动性：压力退出时间/LVaR 简化式/A股特有维度）──

    def assess_opening_permission(
        self,
        symbol: str,
        position_value: float,
        adv_value: float,
        *,
        is_limit_down: bool = False,
        is_suspended: bool = False,
        is_st: bool = False,
    ) -> "OpeningPermission":
        """开仓许可评估（90 号 §8 裁定①④：压力退出时间>1天禁开仓+A股特有维度）。

        裁定真源 90_methodology_open_questions.md §8 v2.0.0：
          ① 退出天数 = 持仓 /(ADV×0.3 压力折扣 ×10% 参与率)，>1 天→禁新开仓
             （精准拦截微盘股与跌停粘连票）；
          ④ 跌停/停牌/ST 任一 → 禁开仓（比 ILLIQ 更致命）。

        Args:
            symbol: 标的代码
            position_value: 拟持仓市值（元）
            adv_value: 日均成交额 ADV（元）
            is_limit_down: 跌停（粘连）标志
            is_suspended: 停牌标志
            is_st: ST/退市警示标志

        Returns:
            OpeningPermission（allowed + exit_days + 拒绝理由列表）
        """
        reasons: list[str] = []
        exit_days = compute_stress_exit_days(position_value, adv_value)
        if exit_days > MAX_STRESS_EXIT_DAYS:
            reasons.append(f"压力退出时间 {exit_days:.2f} 天 > {MAX_STRESS_EXIT_DAYS} 天，禁新开仓")
        if is_limit_down:
            reasons.append("跌停（粘连），禁开仓")
        if is_suspended:
            reasons.append("停牌，禁开仓")
        if is_st:
            reasons.append("ST/退市警示，禁开仓")

        allowed = not reasons
        _logger.info(
            "Opening permission assessed: symbol=%s exit_days=%.4f allowed=%s reasons=%s",
            symbol,
            exit_days,
            allowed,
            reasons,
        )
        return OpeningPermission(
            symbol=symbol,
            allowed=allowed,
            exit_days=exit_days,
            reasons=reasons,
        )

    # ── 内部工具 ──

    @staticmethod
    def _validate_inputs(closes: pd.Series, volumes: pd.Series) -> None:
        """验证 Amihud 计算输入。"""
        if len(closes) != len(volumes):
            raise InvalidLiquidityInputError(f"closes 与 volumes 长度不匹配: {len(closes)} vs {len(volumes)}")

    @staticmethod
    def _extract_ohlcv(ohlcv: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
        """从 DataFrame 提取 close 和 volume/amount 序列。

        优先使用 amount 列（成交额，元），其次用 volume × close 估算。
        """
        if "close" not in ohlcv.columns:
            raise InvalidLiquidityInputError(f"OHLCV 缺少 close 列: {ohlcv.columns.tolist()}")

        closes = ohlcv["close"].astype(float)

        if "amount" in ohlcv.columns:
            volumes = ohlcv["amount"].astype(float)
        elif "volume" in ohlcv.columns:
            # volume 可能是成交额（元）或成交量（股）
            # A股数据源通常 volume=成交额，这里直接用
            volumes = ohlcv["volume"].astype(float)
        else:
            raise InvalidLiquidityInputError(f"OHLCV 缺少 volume/amount 列: {ohlcv.columns.tolist()}")

        return closes, volumes
