# [BLUEPRINT] MOD-SIG-113 | docs/03_modules/_domain_signal/banker_pattern_simulator/blueprint.md
# [MODULE] zephyr.signal_ashare.banker_pattern_simulator
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（协议核心纯内存；价量规则库/回测回调/时钟全注入）
# [CONSUMERS] 运行时装配批（统一注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 六阶段词表闭合（建仓/洗盘/拉升/出货/对倒/护盘）；阶段转移矩阵不可跳跃；价量规则匹配结果置信度∈[0,1]；反庄沙盒仅回测/模拟语义标注；识别结论 advisory=True 硬标注；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/banker_pattern_simulator/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] BankerPatternError(占位 ZA-SIG-UNREGISTERED-BANKER-PATTERN)——阶段词表非法/规则库含非法区间/空序列/序列不等长时抛
# [TESTS] tests/signal_ashare/test_banker_pattern_simulator.py
# [A_module] module_id=MOD-SIG-113 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
BankerPatternSimulator — 庄家行为模式识别与模拟（MOD-SIG-113，B1-00168，C2 C-035）。

六阶段子模式（建仓/洗盘/拉升/出货/对倒/护盘词表闭合）规则识别器
（价量特征规则库+阶段转移判定）+ 反庄策略沙盒模拟
（注入回测环境回调，仅回测/模拟语义标注）+ 风险警示与回避清单输出
+ 识别结论不直接下单硬标注 advisory。

纯内存/DI设计；外部副作用全部经注入回调。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: rules 参数
#   fields: 参数 rules（无注解）
#   code: banker_pattern_simulator.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: backtest_runner 参数
#   fields: 参数 backtest_runner（无注解）
#   code: banker_pattern_simulator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① BankerPatternSimulator
#   name_en: BankerPatternSimulator
#   intro: 庄家行为模式识别与模拟器（规则库+阶段转移+沙盒）。
#   desc: 庄家行为模式识别与模拟器（规则库+阶段转移+沙盒）。；公共方法（定义序）: match_phase, transition_allowed, next_phases, sandbox_simulate, analyze…
#   inputs: rules backtest_runner
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: BankerPatternSimulator
#   downstream: 运行时装配批（统一注入点装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "BankerPatternError",
    "BankerPatternSimulator",
    "BankerPhase",
    "PriceVolumeRule",
    "PatternMatchResult",
    "SandboxResult",
]


class BankerPatternError(Exception):
    """庄家模式协议输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-BANKER-PATTERN。
    """


class BankerPhase(str, Enum):
    """庄家操纵六阶段词表（闭合）。"""

    ACCUMULATION = "建仓"
    WASH = "洗盘"
    PULL = "拉升"
    DISTRIBUTION = "出货"
    MATCH_TRADE = "对倒"
    SUPPORT = "护盘"


@dataclass(frozen=True)
class PriceVolumeRule:
    """价量特征规则（用于匹配阶段）。"""

    phase: BankerPhase
    min_price_change_pct: float
    max_price_change_pct: float
    min_volume_ratio: float
    max_volume_ratio: float
    min_duration: int = 1
    max_duration: int = 20
    weight: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.phase, BankerPhase):
            raise BankerPatternError(f"非法阶段: {self.phase!r}")
        if self.min_price_change_pct > self.max_price_change_pct:
            raise BankerPatternError("价变区间下界大于上界")
        if self.min_volume_ratio > self.max_volume_ratio:
            raise BankerPatternError("量比区间下界大于上界")
        if self.min_duration < 1 or self.max_duration < self.min_duration:
            raise BankerPatternError("duration 非法")
        if not 0.0 <= self.weight <= 1.0:
            raise BankerPatternError(f"weight 越界: {self.weight!r}")


@dataclass(frozen=True)
class PatternMatchResult:
    """阶段识别结果。"""

    phase: BankerPhase
    confidence: float
    matched_duration: int
    advisory: bool = True
    risk_warnings: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class SandboxResult:
    """反庄沙盒模拟结果。"""

    simulated: bool
    pnl_estimate: float | None
    notes: tuple[str, ...] = ()


#: 阶段转移矩阵：当前阶段 -> 允许下一阶段的集合
_PHASE_TRANSITIONS: Final[dict[BankerPhase, frozenset[BankerPhase]]] = {
    BankerPhase.ACCUMULATION: frozenset({BankerPhase.WASH, BankerPhase.PULL, BankerPhase.MATCH_TRADE}),
    BankerPhase.WASH: frozenset({BankerPhase.PULL, BankerPhase.ACCUMULATION, BankerPhase.DISTRIBUTION}),
    BankerPhase.PULL: frozenset({BankerPhase.DISTRIBUTION, BankerPhase.SUPPORT, BankerPhase.WASH}),
    BankerPhase.DISTRIBUTION: frozenset({BankerPhase.ACCUMULATION, BankerPhase.SUPPORT}),
    BankerPhase.MATCH_TRADE: frozenset({BankerPhase.WASH, BankerPhase.DISTRIBUTION, BankerPhase.PULL}),
    BankerPhase.SUPPORT: frozenset({BankerPhase.PULL, BankerPhase.ACCUMULATION}),
}

#: 默认价量规则库（MVP初拍值，纯规则）
_DEFAULT_RULES: Final[tuple[PriceVolumeRule, ...]] = (
    PriceVolumeRule(
        phase=BankerPhase.ACCUMULATION,
        min_price_change_pct=-3.0,
        max_price_change_pct=3.0,
        min_volume_ratio=0.5,
        max_volume_ratio=2.0,
        min_duration=5,
        max_duration=30,
        weight=0.8,
    ),
    PriceVolumeRule(
        phase=BankerPhase.WASH,
        min_price_change_pct=-5.0,
        max_price_change_pct=2.0,
        min_volume_ratio=0.3,
        max_volume_ratio=1.5,
        min_duration=2,
        max_duration=10,
        weight=0.7,
    ),
    PriceVolumeRule(
        phase=BankerPhase.PULL,
        min_price_change_pct=3.0,
        max_price_change_pct=20.0,
        min_volume_ratio=1.2,
        max_volume_ratio=5.0,
        min_duration=3,
        max_duration=15,
        weight=0.9,
    ),
    PriceVolumeRule(
        phase=BankerPhase.DISTRIBUTION,
        min_price_change_pct=-2.0,
        max_price_change_pct=5.0,
        min_volume_ratio=1.5,
        max_volume_ratio=4.0,
        min_duration=3,
        max_duration=20,
        weight=0.85,
    ),
    PriceVolumeRule(
        phase=BankerPhase.MATCH_TRADE,
        min_price_change_pct=-1.0,
        max_price_change_pct=1.0,
        min_volume_ratio=2.0,
        max_volume_ratio=6.0,
        min_duration=1,
        max_duration=5,
        weight=0.6,
    ),
    PriceVolumeRule(
        phase=BankerPhase.SUPPORT,
        min_price_change_pct=-2.0,
        max_price_change_pct=2.0,
        min_volume_ratio=0.8,
        max_volume_ratio=2.5,
        min_duration=1,
        max_duration=5,
        weight=0.5,
    ),
)


def _default_risk_warnings(phase: BankerPhase) -> tuple[str, ...]:
    """按阶段输出风险警示回避清单。"""
    warnings: dict[BankerPhase, tuple[str, ...]] = {
        BankerPhase.ACCUMULATION: ("主力吸筹期，勿急于跟风；",),
        BankerPhase.WASH: ("洗盘剧烈，短线止损易被扫；",),
        BankerPhase.PULL: ("拉升阶段追涨风险高，注意止盈；",),
        BankerPhase.DISTRIBUTION: ("出货阶段，严禁追高；", "建议减仓回避；"),
        BankerPhase.MATCH_TRADE: ("对倒放量 suspicious，回避参与；",),
        BankerPhase.SUPPORT: ("护盘不等于反转，观望为主；",),
    }
    return warnings.get(phase, ())


class BankerPatternSimulator:
    """庄家行为模式识别与模拟器（规则库+阶段转移+沙盒）。"""

    def __init__(
        self,
        *,
        rules: Sequence[PriceVolumeRule] | None = None,
        backtest_runner: Callable[[BankerPhase, Sequence[float], Sequence[float]], dict] | None = None,
    ) -> None:
        self._rules = tuple(rules) if rules is not None else _DEFAULT_RULES
        for rule in self._rules:
            if not isinstance(rule, PriceVolumeRule):
                raise BankerPatternError("规则库含非法条目（非 PriceVolumeRule）")
        self._backtest_runner = backtest_runner

    # ── 规则匹配 ──────────────────────────────────────────────────────────

    def match_phase(
        self,
        prices: Sequence[float],
        volumes: Sequence[float],
        avg_volume: float | None = None,
    ) -> PatternMatchResult:
        """价量序列→阶段匹配（取最高置信度规则）。"""
        if not prices or not volumes:
            raise BankerPatternError("价格或成交量序列为空")
        if len(prices) != len(volumes):
            raise BankerPatternError(f"价量序列不等长: {len(prices)} vs {len(volumes)}")
        if len(prices) < 2:
            raise BankerPatternError("序列长度须≥2")

        n = len(prices)
        price_change_pct = (prices[-1] - prices[0]) / prices[0] * 100.0
        avg_vol = avg_volume if avg_volume is not None else (sum(volumes) / n)
        volume_ratio = (volumes[-1] / avg_vol) if avg_vol > 0 else 0.0

        best: PatternMatchResult | None = None
        for rule in self._rules:
            score = self._score_rule(rule, price_change_pct, volume_ratio, n)
            if score is None:
                continue
            if best is None or score > best.confidence:
                best = PatternMatchResult(
                    phase=rule.phase,
                    confidence=round(score, 6),
                    matched_duration=n,
                    advisory=True,
                    risk_warnings=_default_risk_warnings(rule.phase),
                )

        if best is None:
            return PatternMatchResult(
                phase=BankerPhase.ACCUMULATION,
                confidence=0.0,
                matched_duration=n,
                advisory=True,
                risk_warnings=("无匹配规则，默认观望；",),
                notes=("价量特征未落入任何规则区间",),
            )
        return best

    @staticmethod
    def _score_rule(
        rule: PriceVolumeRule,
        price_change_pct: float,
        volume_ratio: float,
        duration: int,
    ) -> float | None:
        """规则匹配打分；不匹配返回 None。"""
        if not (rule.min_duration <= duration <= rule.max_duration):
            return None
        if not (rule.min_price_change_pct <= price_change_pct <= rule.max_price_change_pct):
            return None
        if not (rule.min_volume_ratio <= volume_ratio <= rule.max_volume_ratio):
            return None
        # 置信度=规则权重×区间中心距离归一化（简化）
        pc_mid = (rule.min_price_change_pct + rule.max_price_change_pct) / 2
        vr_mid = (rule.min_volume_ratio + rule.max_volume_ratio) / 2
        pc_range = rule.max_price_change_pct - rule.min_price_change_pct
        vr_range = rule.max_volume_ratio - rule.min_volume_ratio
        pc_dist = abs(price_change_pct - pc_mid) / (pc_range / 2 + 1e-12)
        vr_dist = abs(volume_ratio - vr_mid) / (vr_range / 2 + 1e-12)
        closeness = max(0.0, 1.0 - (pc_dist + vr_dist) / 2)
        return rule.weight * closeness

    # ── 阶段转移判定 ──────────────────────────────────────────────────────

    def transition_allowed(self, current: BankerPhase, next_phase: BankerPhase) -> bool:
        """阶段转移是否合法（矩阵闭合）。"""
        return next_phase in _PHASE_TRANSITIONS.get(current, frozenset())

    def next_phases(self, current: BankerPhase) -> tuple[BankerPhase, ...]:
        """当前阶段允许转移的目标阶段（确定性排序）。"""
        return tuple(sorted(_PHASE_TRANSITIONS.get(current, frozenset()), key=lambda p: p.value))

    # ── 反庄沙盒模拟（注入回测环境回调） ──────────────────────────────────

    def sandbox_simulate(
        self,
        phase: BankerPhase,
        prices: Sequence[float],
        volumes: Sequence[float],
    ) -> SandboxResult:
        """反庄策略沙盒模拟；未注入回测环境则降级标记。"""
        if self._backtest_runner is None:
            return SandboxResult(
                simulated=False,
                pnl_estimate=None,
                notes=("backtest_runner 未注入，跳过沙盒模拟",),
            )
        try:
            raw = self._backtest_runner(phase, prices, volumes)
            pnl = float(raw.get("pnl_estimate", 0.0)) if isinstance(raw, dict) else None
            return SandboxResult(
                simulated=True,
                pnl_estimate=pnl,
                notes=("沙盒模拟完成",),
            )
        except Exception as exc:  # noqa: BLE001 — 降级不阻断
            _log.warning("沙盒模拟异常，降级: %s", exc)
            return SandboxResult(
                simulated=False,
                pnl_estimate=None,
                notes=(f"沙盒异常降级: {exc}",),
            )

    # ── 综合识别 ──────────────────────────────────────────────────────────

    def analyze(
        self,
        prices: Sequence[float],
        volumes: Sequence[float],
        avg_volume: float | None = None,
    ) -> dict[str, object]:
        """综合识别入口：阶段匹配 + 沙盒 + 风险清单。"""
        match = self.match_phase(prices, volumes, avg_volume)
        sandbox = self.sandbox_simulate(match.phase, prices, volumes)
        return {
            "phase": match.phase.value,
            "confidence": match.confidence,
            "duration": match.matched_duration,
            "advisory": match.advisory,
            "risk_warnings": match.risk_warnings,
            "sandbox": sandbox,
            "notes": match.notes,
        }
