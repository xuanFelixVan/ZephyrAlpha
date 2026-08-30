# [BLUEPRINT] MOD-FAC-007 | docs/03_modules/_domain_factor/strategy_iteration_upgrader/blueprint.md
# [MODULE] zephyr.research.strategy_iteration_upgrader
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] 无（协议核心纯内存；attribution_parser/hypothesis_sink 全注入）
# [CONSUMERS] 运行时装配批（策略迭代升级批 / 产物经 hypothesis_registry 回调入研究治理流）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 归因报告仅经注入 attribution_parser 解析（缺失/异常/结构非法 Fail-Closed）；权重建议词表闭合 increase|decrease|keep（贡献<弱点线→decrease、>强点线→increase、余者 keep），建议权重=当前×注入系数确定性；新因子候选=弱点方向→算子库词表闭合映射（momentum|volatility|volume|trend，词表外方向 Fail-Closed），仅弱点因子产候选；产物（逐候选+权重调整批）必经注入 hypothesis_sink 回调登记（未注入 run Fail-Closed）；迭代历史 seq 自 1 单调递增留痕不可变；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_factor/strategy_iteration_upgrader/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] StrategyUpgradeError(占位 ZA-FAC-UNREGISTERED-STRATEGY-UPGRADE)——parser/sink 缺失或异常/报告结构非法/词表外方向/空 strategy_id/阈值序非法时抛
# [TESTS] tests/research/test_strategy_iteration_upgrader.py
# [A_module] module_id=MOD-FAC-007 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
StrategyIterationUpgrader — 策略迭代升级器（MOD-FAC-007）。

B10-02221（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-FAC-022，A1 D-RESEARCH-17）：
归因→**权重调整建议**（归因报告注入解析）+ **新因子候选生成**（弱点方向映射
算子库）+ 产物入 **hypothesis_registry 回调** + **迭代历史留痕**。

查重分工（蓝图 §0）：iteration_guide=证据聚合→continue/pivot/abandon 规则建
议（假设生命周期层）；本件=策略归因→**权重/因子候选**产物层（产出经注入回
调登记 hypothesis_registry，本件不直写注册表、不落盘）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: attribution_parser 参数
#   fields: 参数 attribution_parser（无注解）
#   code: strategy_iteration_upgrader.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: hypothesis_sink 参数
#   fields: 参数 hypothesis_sink（无注解）
#   code: strategy_iteration_upgrader.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: weak_threshold 参数
#   fields: 参数 weak_threshold（无注解）
#   code: strategy_iteration_upgrader.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: strong_threshold 参数
#   fields: 参数 strong_threshold（无注解）
#   code: strategy_iteration_upgrader.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① StrategyIterationUpgrader
#   name_en: StrategyIterationUpgrader
#   intro: 策略迭代升级器（归因→权重建议 + 新因子候选 + registry 回调 + 历史）。
#   desc: 策略迭代升级器（归因→权重建议 + 新因子候选 + registry 回调 + 历史）。 Args: attribution_parser: 注入归因报告解析器，``raw_re…；公共方法（定义序）: upgrade…
#   inputs: attribution_parser hypothesis_sink weak_threshold strong_threshold in…
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: StrategyIterationUpgrader
#   downstream: 运行时装配批（策略迭代升级批 / 产物经 hypothesis_registry 回调入研究治理流）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "DIRECTION_TEMPLATES",
    "WEAKNESS_DIRECTIONS",
    "FactorCandidateProposal",
    "StrategyIterationUpgrader",
    "StrategyUpgradeError",
    "UpgradeRecord",
    "WeightAction",
    "WeightSuggestion",
]

#: 弱点方向词表（闭合）
WEAKNESS_DIRECTIONS: Final = ("momentum", "volatility", "volume", "trend")

#: 弱点方向 → 新因子候选算子模板（词表闭合映射）
DIRECTION_TEMPLATES: Final[dict[str, tuple[str, ...]]] = {
    "momentum": ("sub(close, ts_mean(close,10))", "div(close, ts_max(high,20))"),
    "volatility": ("ts_std(close,20)", "div(ts_std(close,5), ts_std(close,20))"),
    "volume": ("div(volume, ts_mean(volume,20))", "mul(gt(close, open), volume)"),
    "trend": ("sub(ts_mean(close,5), ts_mean(close,20))", "sub(ts_max(high,10), ts_min(low,10))"),
}


class StrategyUpgradeError(Exception):
    """策略迭代升级输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FAC-UNREGISTERED-STRATEGY-UPGRADE。
    """


class WeightAction(str, Enum):
    """权重调整动作词表（闭合）。"""

    INCREASE = "increase"
    DECREASE = "decrease"
    KEEP = "keep"


@dataclass(frozen=True)
class WeightSuggestion:
    """单因子权重调整建议（frozen）。"""

    factor_id: str
    action: WeightAction
    current_weight: float
    suggested_weight: float


@dataclass(frozen=True)
class FactorCandidateProposal:
    """新因子候选（弱点方向映射算子库产出，frozen）。"""

    candidate_id: str
    expression: str
    direction: str
    source_factor_id: str


@dataclass(frozen=True)
class UpgradeRecord:
    """单轮迭代升级记录（frozen；历史留痕不可变）。"""

    seq: int
    strategy_id: str
    weight_suggestions: tuple[WeightSuggestion, ...]
    factor_candidates: tuple[FactorCandidateProposal, ...]
    hypothesis_ids: tuple[str, ...]


class StrategyIterationUpgrader:
    """策略迭代升级器（归因→权重建议 + 新因子候选 + registry 回调 + 历史）。

    Args:
        attribution_parser: 注入归因报告解析器，``raw_report -> 条目序列``，
            条目须含 ``factor_id/weight/contribution/direction`` 四键。
        hypothesis_sink: 注入 hypothesis_registry 登记回调，``payload -> str``。
        weak_threshold: 弱点线（contribution < 线 → 弱点因子，decrease）。
        strong_threshold: 强点线（contribution > 线 → increase；须 > 弱点线）。
        increase_factor / decrease_factor: 权重调整系数（确定性）。
    """

    def __init__(
        self,
        *,
        attribution_parser: Callable[[object], Sequence[Mapping[str, object]]] | None,
        hypothesis_sink: Callable[[Mapping[str, object]], str] | None,
        weak_threshold: float = 0.05,
        strong_threshold: float = 0.20,
        increase_factor: float = 1.2,
        decrease_factor: float = 0.8,
    ) -> None:
        if attribution_parser is None:
            raise StrategyUpgradeError("attribution_parser 未注入（Fail-Closed）")
        if hypothesis_sink is None:
            raise StrategyUpgradeError("hypothesis_sink 未注入（Fail-Closed）")
        if not (0.0 <= float(weak_threshold) < float(strong_threshold)):
            raise StrategyUpgradeError(f"阈值序非法（须 0≤弱点线<强点线）: {weak_threshold!r} / {strong_threshold!r}")
        if float(increase_factor) <= 1.0:
            raise StrategyUpgradeError(f"increase_factor 非法（须 >1）: {increase_factor!r}")
        if not (0.0 < float(decrease_factor) < 1.0):
            raise StrategyUpgradeError(f"decrease_factor 非法（须 ∈ (0,1)）: {decrease_factor!r}")
        self._parser = attribution_parser
        self._sink = hypothesis_sink
        self._weak = float(weak_threshold)
        self._strong = float(strong_threshold)
        self._inc = float(increase_factor)
        self._dec = float(decrease_factor)
        self._history: list[UpgradeRecord] = []
        self._counter = 0

    # ── 归因报告解析（注入 + 结构校验 Fail-Closed） ─────────────────────────

    def _parse(self, raw_report: object) -> list[dict[str, object]]:
        try:
            entries = self._parser(raw_report)
        except StrategyUpgradeError:
            raise
        except Exception as exc:  # noqa: BLE001 — 注入件异常 Fail-Closed
            raise StrategyUpgradeError(f"attribution_parser 异常（{type(exc).__name__}）") from exc
        if not entries:
            raise StrategyUpgradeError("归因报告为空（无因子条目）")
        out: list[dict[str, object]] = []
        seen: set[str] = set()
        for entry in entries:
            if not isinstance(entry, Mapping):
                raise StrategyUpgradeError(f"归因条目非法（须为映射）: {entry!r}")
            factor_id = entry.get("factor_id")
            weight = entry.get("weight")
            contribution = entry.get("contribution")
            direction = entry.get("direction")
            if not isinstance(factor_id, str) or not factor_id.strip():
                raise StrategyUpgradeError(f"归因条目 factor_id 空白: {entry!r}")
            if factor_id in seen:
                raise StrategyUpgradeError(f"归因条目 factor_id 重复: {factor_id!r}")
            seen.add(factor_id)
            for name, val in (("weight", weight), ("contribution", contribution)):
                if isinstance(val, bool) or not isinstance(val, (int, float)):
                    raise StrategyUpgradeError(f"归因条目 {name} 非法（须为数值）: {entry!r}")
            if float(weight) < 0.0:  # type: ignore[arg-type]
                raise StrategyUpgradeError(f"归因条目 weight 为负: {entry!r}")
            if direction not in WEAKNESS_DIRECTIONS:
                raise StrategyUpgradeError(f"词表外弱点方向: {direction!r}（词表：{list(WEAKNESS_DIRECTIONS)}）")
            out.append(
                {
                    "factor_id": factor_id.strip(),
                    "weight": float(weight),  # type: ignore[arg-type]
                    "contribution": float(contribution),  # type: ignore[arg-type]
                    "direction": str(direction),
                }
            )
        return out

    # ── 产物登记（注入 hypothesis_registry 回调） ────────────────────────────

    def _register(self, payload: Mapping[str, object]) -> str:
        try:
            hid = self._sink(payload)
        except StrategyUpgradeError:
            raise
        except Exception as exc:  # noqa: BLE001 — 注入件异常 Fail-Closed
            raise StrategyUpgradeError(f"hypothesis_sink 异常（{type(exc).__name__}）") from exc
        if not isinstance(hid, str) or not hid.strip():
            raise StrategyUpgradeError(f"hypothesis_sink 返回非法 hypothesis_id: {hid!r}")
        return hid.strip()

    # ── 主流程 ────────────────────────────────────────────────────────────

    def upgrade(self, strategy_id: str, raw_report: object) -> UpgradeRecord:
        """归因 → 权重调整建议 + 新因子候选 → registry 回调 → 历史留痕。"""
        if not isinstance(strategy_id, str) or not strategy_id.strip():
            raise StrategyUpgradeError(f"strategy_id 空白: {strategy_id!r}")
        strategy_id = strategy_id.strip()
        entries = self._parse(raw_report)

        suggestions: list[WeightSuggestion] = []
        candidates: list[FactorCandidateProposal] = []
        for e in entries:
            contribution = float(e["contribution"])  # type: ignore[arg-type]
            weight = float(e["weight"])  # type: ignore[arg-type]
            if contribution < self._weak:
                action, new_weight = WeightAction.DECREASE, round(weight * self._dec, 6)
            elif contribution > self._strong:
                action, new_weight = WeightAction.INCREASE, round(weight * self._inc, 6)
            else:
                action, new_weight = WeightAction.KEEP, weight
            suggestions.append(
                WeightSuggestion(
                    factor_id=str(e["factor_id"]),
                    action=action,
                    current_weight=weight,
                    suggested_weight=new_weight,
                )
            )
            if action is WeightAction.DECREASE:  # 仅弱点因子产新因子候选
                for template in DIRECTION_TEMPLATES[str(e["direction"])]:
                    self._counter += 1
                    candidates.append(
                        FactorCandidateProposal(
                            candidate_id=f"SU-{self._counter:04d}",
                            expression=template,
                            direction=str(e["direction"]),
                            source_factor_id=str(e["factor_id"]),
                        )
                    )

        hypothesis_ids: list[str] = []
        adjusted = [s for s in suggestions if s.action is not WeightAction.KEEP]
        if adjusted:
            hypothesis_ids.append(
                self._register(
                    {
                        "kind": "weight_adjustment",
                        "strategy_id": strategy_id,
                        "suggestions": [
                            {
                                "factor_id": s.factor_id,
                                "action": s.action.value,
                                "current_weight": s.current_weight,
                                "suggested_weight": s.suggested_weight,
                            }
                            for s in adjusted
                        ],
                    }
                )
            )
        for cand in candidates:
            hypothesis_ids.append(
                self._register(
                    {
                        "kind": "factor_candidate",
                        "strategy_id": strategy_id,
                        "candidate_id": cand.candidate_id,
                        "expression": cand.expression,
                        "direction": cand.direction,
                        "source_factor_id": cand.source_factor_id,
                    }
                )
            )
        record = UpgradeRecord(
            seq=len(self._history) + 1,
            strategy_id=strategy_id,
            weight_suggestions=tuple(suggestions),
            factor_candidates=tuple(candidates),
            hypothesis_ids=tuple(hypothesis_ids),
        )
        self._history.append(record)
        _log.info(
            "策略迭代升级 #%d: %s 权重建议 %d / 因子候选 %d / 登记 %d",
            record.seq,
            strategy_id,
            len(suggestions),
            len(candidates),
            len(hypothesis_ids),
        )
        return record

    def history(self) -> tuple[UpgradeRecord, ...]:
        """迭代历史（seq 升序留痕，不可变副本）。"""
        return tuple(self._history)
