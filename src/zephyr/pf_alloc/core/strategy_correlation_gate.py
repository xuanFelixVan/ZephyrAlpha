# [BLUEPRINT] MOD-PA-004 | docs/03_modules/_domain_portfolio_alloc/strategy_correlation_gate/blueprint.md
# [MODULE] zephyr.pf_alloc.core.strategy_correlation_gate
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-PA-003(资金分配) ; MOD-PA-005(策略生命周期) ; D-PF-CORE
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 指标∈[0,1]且相关性取绝对值;整体裁决=max(pair裁决)按严重度;尾部相关REJECT仅same_direction生效;门禁无副作用只产出裁决
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidCorrelationInputError
# [TESTS] tests/pf_alloc/test_strategy_correlation_gate.py
# [A_module] module_id=MOD-PA-004 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""
Strategy Correlation Gate — 策略相关性门禁 (MOD-PA-004)

G12 相关性门禁: 策略两两之间检查相关性/因子重叠/股票池重叠/行业集中度/尾部相关,
超阈值产出 PA-E03 CorrelationGateTriggered, 阻止过度同质化策略组合上线。

门禁规则 (D-PF-ALLOC §1 PA-04, §7.1, §7.2):
    - 相关性 > 0.90 → HARD_REJECT (硬否决)
    - 相关性 > 0.85 → REJECT (否决)
    - 因子重叠 > 80% → REJECT (否决上线)
    - 因子重叠 > 60% → WARN
    - 股票池重叠 > 70% 且 行业集中度 > 50% → WARN
    - 尾部相关 > 0.7 且 same_direction → REJECT (否决新增同方向策略)

属A类基础设施(阈值判定+多维度门禁, 逻辑明确), 阈值为C类可调参数。
相关性矩阵/因子重叠的*计算*属数据层职责, 本模块只消费已计算好的指标做门禁判定。
依据: D:\临时工作区\依赖图\06-D-PF-ALLOC-组合分配域.md §1 PA-04, §7.1, §7.2
SSoT: depgraph MOD-PA-004
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: strategy_correlation_gate.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: strategy_correlation_gate.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CorrelationGateResult
#   name_en: CorrelationGateResult
#   intro: 门禁整体裁决结果。
#   desc: 门禁整体裁决结果。；公共方法（定义序）: passed, rejected；源码 L225-L241
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② StrategyCorrelationGate
#   name_en: StrategyCorrelationGate
#   intro: 策略相关性门禁——多维度阈值判定+整体裁决聚合。
#   desc: 策略相关性门禁——多维度阈值判定+整体裁决聚合。 用法: gate = StrategyCorrelationGate() pairs = [StrategyPairMetric…；公共方法（定义序）: config,…
#   inputs: config clock
#   outputs: 返回值
#   （注：A2 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（8 定义）
#   name_en: public defs
#   intro: CorrelationGateResult, StrategyCorrelationGate
#   downstream: MOD-PA-003(资金分配) ; MOD-PA-005(策略生命周期) ; D-PF-CORE
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "GateVerdict",
    "CorrelationGateConfig",
    "StrategyPairMetrics",
    "GateViolation",
    "CorrelationGateResult",
    "CorrelationGateTriggeredEvent",
    "StrategyCorrelationGate",
    "InvalidCorrelationInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class GateVerdict(str, Enum):
    """门禁裁决级别 (严重度递增)。"""

    PASS = "PASS"  # 通过
    WARN = "WARN"  # 警告(可上线但标记)
    REJECT = "REJECT"  # 否决
    HARD_REJECT = "HARD_REJECT"  # 硬否决

    @property
    def severity(self) -> int:
        """严重度排序值 (越大越严重)。"""
        return {"PASS": 0, "WARN": 1, "REJECT": 2, "HARD_REJECT": 3}[self.value]

    @classmethod
    def worst(cls, verdicts: list[GateVerdict]) -> GateVerdict:
        """取一组裁决中最严重者。"""
        if not verdicts:
            return cls.PASS
        return max(verdicts, key=lambda v: v.severity)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidCorrelationInputError(ZephyrBaseError):
    """相关性门禁输入数据非法(如指标越界、策略自相关)。"""

    # 2026-08-17 改号 ZA-PA-0002→ZA-PA-0004：与 signal_synthesis_combiner(MOD-PA-002)
    # 重码，按 #ARCH-ERRCODE-001「后引入者改号」裁定；0004 对齐本模块 MOD-PA-004
    error_code = "ZA-PA-0004"


# ──────────────────────────────────────────────────────────────────────────────
# 配置 (C 类可调参数)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CorrelationGateConfig:
    """相关性门禁阈值配置 (设计真源 §1 PA-04, §7.1)。"""

    # Pearson 相关性
    reject_correlation: float = 0.85  # > 0.85 → REJECT
    hard_reject_correlation: float = 0.90  # > 0.90 → HARD_REJECT
    # 因子重叠率
    warn_factor_overlap: float = 0.60  # > 60% → WARN
    reject_factor_overlap: float = 0.80  # > 80% → REJECT
    # 股票池重叠 + 行业集中度 (联合判定)
    warn_stock_pool_overlap: float = 0.70  # 股票池重叠 > 70%
    warn_sector_concentration: float = 0.50  # 且 行业集中度 > 50% → WARN
    # 尾部相关性 (EVT, 仅 same_direction 生效)
    reject_tail_correlation: float = 0.70  # > 0.7 且 same_direction → REJECT
    # 相关性否决持久化条件（90 号 Phase2 #20：与 90 天滚动相关性剔除规则口径统一，
    # 补"持续 30 天"避免单日噪声误剔除；pair 未提供持续天数数据时维持立即否决=向后兼容）
    correlation_reject_sustained_days: int = 30

    def __post_init__(self) -> None:
        for name, val in (
            ("reject_correlation", self.reject_correlation),
            ("hard_reject_correlation", self.hard_reject_correlation),
            ("warn_factor_overlap", self.warn_factor_overlap),
            ("reject_factor_overlap", self.reject_factor_overlap),
            ("warn_stock_pool_overlap", self.warn_stock_pool_overlap),
            ("warn_sector_concentration", self.warn_sector_concentration),
            ("reject_tail_correlation", self.reject_tail_correlation),
        ):
            if not 0 <= val <= 1:
                raise InvalidCorrelationInputError(f"{name} must be in [0,1], got {val}")
        if not (self.reject_correlation < self.hard_reject_correlation):
            raise InvalidCorrelationInputError("reject_correlation must be < hard_reject_correlation")
        if not (self.warn_factor_overlap < self.reject_factor_overlap):
            raise InvalidCorrelationInputError("warn_factor_overlap must be < reject_factor_overlap")
        if self.correlation_reject_sustained_days < 0:
            raise InvalidCorrelationInputError("correlation_reject_sustained_days must be >= 0")


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StrategyPairMetrics:
    """策略两两相关性指标 (一个 pair)。

    所有指标 ∈ [0, 1]; correlation 取绝对值。
    未提供的维度可为 None (门禁跳过该维度)。
    """

    strategy_a: str
    strategy_b: str
    correlation: float | None = None  # Pearson 相关性 (取绝对值)
    factor_overlap: float | None = None  # 因子重叠率
    stock_pool_overlap: float | None = None  # 股票池重叠率
    sector_concentration: float | None = None  # 行业集中度
    tail_correlation: float | None = None  # 尾部相关性 (EVT)
    same_direction: bool = False  # 是否同方向 (尾部相关 REJECT 仅对同方向生效)
    # 相关性持续天数（90 号 Phase2 #20 持久化条件；None=未提供→维持立即否决）
    correlation_sustained_days: int | None = None


@dataclass(frozen=True)
class GateViolation:
    """单条门禁违规。"""

    strategy_a: str
    strategy_b: str
    rule: str  # 违反的规则名
    dimension: str  # 维度 (correlation/factor_overlap/...)
    value: float  # 实际值
    threshold: float  # 触发阈值
    verdict: GateVerdict


@dataclass(frozen=True)
class CorrelationGateResult:
    """门禁整体裁决结果。"""

    overall_verdict: GateVerdict
    violations: list[GateViolation] = field(default_factory=list)
    pairs_checked: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def passed(self) -> bool:
        """是否通过 (PASS 或 WARN 视为可上线, REJECT/HARD_REJECT 视为不通过)。"""
        return self.overall_verdict.severity < GateVerdict.REJECT.severity

    @property
    def rejected(self) -> bool:
        """是否被否决。"""
        return self.overall_verdict.severity >= GateVerdict.REJECT.severity


@dataclass(frozen=True)
class CorrelationGateTriggeredEvent:
    """PA-E03 CorrelationGateTriggered 事件。"""

    result: CorrelationGateResult
    timestamp: datetime
    context_snapshot: dict[str, Any] = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────────────
# 相关性门禁
# ──────────────────────────────────────────────────────────────────────────────


class StrategyCorrelationGate:
    """策略相关性门禁——多维度阈值判定+整体裁决聚合。

    用法:
        gate = StrategyCorrelationGate()
        pairs = [StrategyPairMetrics("S1", "S2", correlation=0.88, factor_overlap=0.65)]
        result = gate.check(pairs)
        if result.rejected:
            # 阻止策略组合上线
        # PA-03 消费 result.overall_verdict 决定是否分配资金

    Args:
        config: 门禁阈值配置
        clock: 可选时间源 (测试注入)
    """

    def __init__(
        self,
        config: CorrelationGateConfig | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._config = config or CorrelationGateConfig()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._listeners: list[Callable[[CorrelationGateTriggeredEvent], None]] = []

    @property
    def config(self) -> CorrelationGateConfig:
        return self._config

    def check(self, pairs: list[StrategyPairMetrics], now: datetime | None = None) -> CorrelationGateResult:
        """检查所有策略两两指标, 返回整体裁决。

        Args:
            pairs: 策略两两指标列表
            now: 时间戳

        Returns:
            CorrelationGateResult (整体裁决=最严重 pair, 含全部违规明细)

        Raises:
            InvalidCorrelationInputError: 指标越界、策略自相关
        """
        now = now or self._clock()
        all_violations: list[GateViolation] = []
        pair_verdicts: list[GateVerdict] = []

        for pair in pairs:
            self._validate_pair(pair)
            violations = self._evaluate_pair(pair)
            all_violations.extend(violations)
            if violations:
                pair_verdicts.append(max(violations, key=lambda v: v.verdict.severity).verdict)
            else:
                pair_verdicts.append(GateVerdict.PASS)

        overall = GateVerdict.worst(pair_verdicts) if pair_verdicts else GateVerdict.PASS
        result = CorrelationGateResult(
            overall_verdict=overall,
            violations=all_violations,
            pairs_checked=len(pairs),
            timestamp=now,
        )

        # 门禁触发 (有违规即触发事件, 含 WARN)
        if all_violations:
            event = CorrelationGateTriggeredEvent(
                result=result,
                timestamp=now,
                context_snapshot={
                    "overall_verdict": overall.value,
                    "violation_count": len(all_violations),
                    "pairs_checked": len(pairs),
                    "rules": sorted({v.rule for v in all_violations}),
                },
            )
            self._emit(event)
        return result

    def on_gate_triggered(self, listener: Callable[[CorrelationGateTriggeredEvent], None]) -> None:
        """订阅 PA-E03 CorrelationGateTriggered 事件。"""
        self._listeners.append(listener)

    # ── 内部 ──

    @staticmethod
    def _validate_pair(pair: StrategyPairMetrics) -> None:
        if pair.strategy_a == pair.strategy_b:
            raise InvalidCorrelationInputError(f"strategy pair cannot be self-correlated: {pair.strategy_a!r}")
        # Pearson 相关性天然可为负, 允许 [-1, 1]; 其余维度 [0, 1]
        if pair.correlation is not None and not -1 <= pair.correlation <= 1:
            raise InvalidCorrelationInputError(
                f"correlation for ({pair.strategy_a},{pair.strategy_b}) must be in [-1,1], got {pair.correlation}"
            )
        for name, val in (
            ("factor_overlap", pair.factor_overlap),
            ("stock_pool_overlap", pair.stock_pool_overlap),
            ("sector_concentration", pair.sector_concentration),
            ("tail_correlation", pair.tail_correlation),
        ):
            if val is not None and not 0 <= val <= 1:
                raise InvalidCorrelationInputError(
                    f"{name} for ({pair.strategy_a},{pair.strategy_b}) must be in [0,1], got {val}"
                )
        if pair.correlation_sustained_days is not None and pair.correlation_sustained_days < 0:
            raise InvalidCorrelationInputError(
                f"correlation_sustained_days for ({pair.strategy_a},{pair.strategy_b}) must be >= 0, got {pair.correlation_sustained_days}"
            )

    def _evaluate_pair(self, pair: StrategyPairMetrics) -> list[GateViolation]:
        """评估单个 pair, 返回所有违规 (可能多条)。"""
        cfg = self._config
        violations: list[GateViolation] = []

        # 相关性 (取绝对值)
        if pair.correlation is not None:
            corr = abs(pair.correlation)
            if corr > cfg.hard_reject_correlation:
                violations.append(
                    self._mk(
                        pair,
                        "hard_correlation_reject",
                        "correlation",
                        corr,
                        cfg.hard_reject_correlation,
                        self._correlation_verdict(pair, GateVerdict.HARD_REJECT),
                    )
                )
            elif corr > cfg.reject_correlation:
                violations.append(
                    self._mk(
                        pair,
                        "correlation_reject",
                        "correlation",
                        corr,
                        cfg.reject_correlation,
                        self._correlation_verdict(pair, GateVerdict.REJECT),
                    )
                )

        # 因子重叠
        if pair.factor_overlap is not None:
            fo = pair.factor_overlap
            if fo > cfg.reject_factor_overlap:
                violations.append(
                    self._mk(
                        pair,
                        "factor_overlap_reject",
                        "factor_overlap",
                        fo,
                        cfg.reject_factor_overlap,
                        GateVerdict.REJECT,
                    )
                )
            elif fo > cfg.warn_factor_overlap:
                violations.append(
                    self._mk(
                        pair, "factor_overlap_warn", "factor_overlap", fo, cfg.warn_factor_overlap, GateVerdict.WARN
                    )
                )

        # 股票池重叠 + 行业集中度 (联合判定)
        if pair.stock_pool_overlap is not None and pair.sector_concentration is not None:
            if (
                pair.stock_pool_overlap > cfg.warn_stock_pool_overlap
                and pair.sector_concentration > cfg.warn_sector_concentration
            ):
                violations.append(
                    self._mk(
                        pair,
                        "pool_sector_warn",
                        "stock_pool_overlap",
                        pair.stock_pool_overlap,
                        cfg.warn_stock_pool_overlap,
                        GateVerdict.WARN,
                    )
                )

        # 尾部相关性 (仅 same_direction)
        if pair.tail_correlation is not None and pair.same_direction:
            if pair.tail_correlation > cfg.reject_tail_correlation:
                violations.append(
                    self._mk(
                        pair,
                        "tail_correlation_reject",
                        "tail_correlation",
                        pair.tail_correlation,
                        cfg.reject_tail_correlation,
                        GateVerdict.REJECT,
                    )
                )

        return violations

    def _correlation_verdict(self, pair: StrategyPairMetrics, verdict: GateVerdict) -> GateVerdict:
        """相关性否决持久化条件（90 号 Phase2 #20）。

        提供了持续天数且未达 correlation_reject_sustained_days → 降级 WARN
        （避免单日噪声误剔除）；未提供持续天数数据 → 维持原裁决（向后兼容）。
        """
        days = pair.correlation_sustained_days
        if days is not None and days < self._config.correlation_reject_sustained_days:
            return GateVerdict.WARN
        return verdict

    @staticmethod
    def _mk(
        pair: StrategyPairMetrics,
        rule: str,
        dimension: str,
        value: float,
        threshold: float,
        verdict: GateVerdict,
    ) -> GateViolation:
        return GateViolation(
            strategy_a=pair.strategy_a,
            strategy_b=pair.strategy_b,
            rule=rule,
            dimension=dimension,
            value=value,
            threshold=threshold,
            verdict=verdict,
        )

    def _emit(self, event: CorrelationGateTriggeredEvent) -> None:
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as exc:  # noqa: BLE001 — 5.135治标: 隔离监听器故障
                logger.error("CorrelationGate listener error: %s", exc, exc_info=True)
