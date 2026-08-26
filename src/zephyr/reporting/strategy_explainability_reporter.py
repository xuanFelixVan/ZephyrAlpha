# [BLUEPRINT] MOD-RPT-035 | docs/03_modules/_domain_reporting/strategy_explainability_reporter/blueprint.md
# [MODULE] zephyr.reporting.strategy_explainability_reporter
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] 无（协议核心纯内存；shap/lime 解释器/rule_importance/publisher/clock 全注入）
# [CONSUMERS] 运行时装配批（策略 SHAP+LIME 双归因报告 / 可解释性门控降权拦截 / 报告发布对接）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 归因方法词表闭合(shap+lime|shap|lime|rule_fallback); 解释器异常降级不抛(余者兜底); SHAP/LIME 全缺→规则重要性兜底(未注入 Fail-Closed); 覆盖度须∈[0,1](越界 Fail-Closed); 门控口径 coverage≥pass→放行 / ≥downweight→降权 / 其余拦截; 拦截不发布; 重要性按 |权重|降序+名称升序确定性排序; 发布副作用全注入(异常不阻断); 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_reporting/strategy_explainability_reporter/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ExplainabilityError(占位 ZA-RPT-UNREGISTERED-EXPLAINABILITY)——空strategy_id/非法门控阈值/覆盖度越界/双解释器缺失且无规则兜底/未知报告查询时抛
# [TESTS] tests/reporting/test_strategy_explainability_reporter.py
# [A_module] module_id=MOD-RPT-035 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""StrategyExplainabilityReporter — 策略可解释性报告器（MOD-RPT-035）。

B4-06655（AUD-DRAFT-001-DIGEST P2 波 P2-W10，CAND-RPT-010，B4
D-REPORTING-14）：**SHAP+LIME 双归因**报告（shap/lime 解释器全注入，
单解释器异常降级为余者，双缺降级**规则重要性兜底**，兜底未注入
Fail-Closed）+ **可解释性门控**（解释覆盖度 < 阈值 → 策略降权/拦截，
拦截不发布）+ **报告发布对接**（注入 publisher，异常不阻断）。

边界：default_attribution_engine（本域）=收益归因（本件=模型特征可归因
性/解释覆盖度，不重复收益分解）；策略降权/拦截的执行归决策门（本件仅产
出门控结论与报告）；本件纯内存/DI，不触网不落盘。
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass, replace
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "AttributionMethod",
    "ExplainabilityError",
    "ExplainabilityReport",
    "ExplanationResult",
    "FeatureImportance",
    "GateDecision",
    "StrategyExplainabilityReporter",
]


class ExplainabilityError(Exception):
    """可解释性报告输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-RPT-UNREGISTERED-EXPLAINABILITY。
    """


class AttributionMethod(str, Enum):
    """归因方法（词表闭合）。"""

    DUAL = "shap+lime"
    SHAP = "shap"
    LIME = "lime"
    RULE_FALLBACK = "rule_fallback"


class GateDecision(str, Enum):
    """可解释性门控结论。"""

    PASS = "pass"
    DOWNWEIGHT = "downweight"
    BLOCK = "block"


@dataclass(frozen=True)
class ExplanationResult:
    """单解释器产出（frozen）：特征重要性 + 解释覆盖度∈[0,1]。"""

    importances: dict
    coverage: float


@dataclass(frozen=True)
class FeatureImportance:
    """单特征重要性（frozen）。"""

    feature: str
    weight: float


@dataclass(frozen=True)
class ExplainabilityReport:
    """可解释性报告（frozen）。"""

    strategy_id: str
    method: AttributionMethod
    shap_importances: tuple[FeatureImportance, ...]
    lime_importances: tuple[FeatureImportance, ...]
    coverage: float
    gate: GateDecision
    published: bool
    generated_at: datetime.datetime


class StrategyExplainabilityReporter:
    """策略可解释性报告件（双归因 + 门控 + 发布对接）。"""

    def __init__(
        self,
        *,
        shap_explainer: Callable[[str, Mapping[str, float]], ExplanationResult] | None = None,
        lime_explainer: Callable[[str, Mapping[str, float]], ExplanationResult] | None = None,
        rule_importance: Mapping[str, float] | None = None,
        fallback_coverage: float = 0.5,
        pass_threshold: float = 0.8,
        downweight_threshold: float = 0.5,
        publisher: Callable[[ExplainabilityReport], object] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        for name, value in (
            ("fallback_coverage", fallback_coverage),
            ("pass_threshold", pass_threshold),
            ("downweight_threshold", downweight_threshold),
        ):
            if not (0.0 <= float(value) <= 1.0):
                raise ExplainabilityError(f"{name} 越界: {value!r}（须∈[0,1]）")
        if float(downweight_threshold) > float(pass_threshold):
            raise ExplainabilityError(
                f"门控阈值倒挂: downweight={downweight_threshold!r} > pass={pass_threshold!r}"
            )
        if rule_importance is not None:
            for feature, weight in rule_importance.items():
                if not feature:
                    raise ExplainabilityError("rule_importance 特征名为空")
                if not math.isfinite(float(weight)):
                    raise ExplainabilityError(f"rule_importance 权重非有限实数: {feature!r}")
            self._rule: dict[str, float] | None = {
                f: float(w) for f, w in rule_importance.items()
            }
        else:
            self._rule = None
        self._shap = shap_explainer
        self._lime = lime_explainer
        self._fallback_cov = float(fallback_coverage)
        self._pass_th = float(pass_threshold)
        self._down_th = float(downweight_threshold)
        self._publisher = publisher
        self._clock = clock or datetime.datetime.now
        self._reports: dict[str, list[ExplainabilityReport]] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _sorted_importances(mapping: Mapping[str, float]) -> tuple[FeatureImportance, ...]:
        """重要性确定性排序（|权重|降序+名称升序；非有限值 Fail-Closed）。"""
        items = [FeatureImportance(feature=f, weight=float(w)) for f, w in mapping.items()]
        for item in items:
            if not item.feature:
                raise ExplainabilityError("特征名为空")
            if not math.isfinite(item.weight):
                raise ExplainabilityError(f"重要性权重非有限实数: {item.feature!r}")
        items.sort(key=lambda fi: (-abs(fi.weight), fi.feature))
        return tuple(items)

    def _explain(
        self,
        fn: Callable[[str, Mapping[str, float]], ExplanationResult] | None,
        strategy_id: str,
        features: Mapping[str, float],
        label: str,
    ) -> ExplanationResult | None:
        """单解释器调用：未注入/异常 → None 降级（不抛）；覆盖度越界 Fail-Closed。"""
        if fn is None:
            return None
        try:
            result = fn(strategy_id, features)
        except Exception:  # noqa: BLE001 — 解释器异常降级余者/兜底，不阻断
            _log.exception("%s 解释器异常，降级: %s", label, strategy_id)
            return None
        coverage = float(result.coverage)
        if not (0.0 <= coverage <= 1.0):
            raise ExplainabilityError(f"{label} 覆盖度越界: {coverage!r}（须∈[0,1]）")
        return ExplanationResult(importances=dict(result.importances), coverage=coverage)

    def _gate(self, coverage: float) -> GateDecision:
        """门控口径：≥pass 放行；≥downweight 降权；其余拦截。"""
        if coverage >= self._pass_th:
            return GateDecision.PASS
        if coverage >= self._down_th:
            return GateDecision.DOWNWEIGHT
        return GateDecision.BLOCK

    # ── 报告构建 ──────────────────────────────────────────────────────────

    def build_report(
        self,
        strategy_id: str,
        features: Mapping[str, float],
    ) -> ExplainabilityReport:
        """双归因→（双缺规则兜底）→门控→发布（拦截不发布）→留存。"""
        if not strategy_id:
            raise ExplainabilityError("strategy_id 为空")
        shap_res = self._explain(self._shap, strategy_id, features, "shap")
        lime_res = self._explain(self._lime, strategy_id, features, "lime")

        if shap_res is None and lime_res is None:
            if self._rule is None:
                raise ExplainabilityError(
                    "SHAP/LIME 双解释器缺失且 rule_importance 未注入（无兜底，Fail-Closed）"
                )
            method = AttributionMethod.RULE_FALLBACK
            shap_importances = self._sorted_importances(self._rule)
            lime_importances: tuple[FeatureImportance, ...] = ()
            coverage = self._fallback_cov
        else:
            method = (
                AttributionMethod.DUAL
                if shap_res is not None and lime_res is not None
                else (AttributionMethod.SHAP if shap_res is not None else AttributionMethod.LIME)
            )
            shap_importances = (
                self._sorted_importances(shap_res.importances) if shap_res is not None else ()
            )
            lime_importances = (
                self._sorted_importances(lime_res.importances) if lime_res is not None else ()
            )
            coverages = [
                r.coverage for r in (shap_res, lime_res) if r is not None
            ]
            coverage = sum(coverages) / len(coverages)

        gate = self._gate(coverage)
        report = ExplainabilityReport(
            strategy_id=strategy_id,
            method=method,
            shap_importances=shap_importances,
            lime_importances=lime_importances,
            coverage=coverage,
            gate=gate,
            published=False,
            generated_at=self._clock(),
        )
        if gate is not GateDecision.BLOCK and self._publisher is not None:
            try:
                ack = self._publisher(report)
                published = True if ack is None else bool(ack)
            except Exception:  # noqa: BLE001 — 发布失败不阻断（留痕 published=False）
                _log.exception("publisher 发布失败: %s", strategy_id)
                published = False
            report = replace(report, published=published)
        self._reports.setdefault(strategy_id, []).append(report)
        return report

    # ── 查询 ─────────────────────────────────────────────────────────────

    def report_of(self, strategy_id: str) -> ExplainabilityReport:
        """最新报告查询（未知策略 Fail-Closed）。"""
        reports = self._reports.get(strategy_id)
        if not reports:
            raise ExplainabilityError(f"未知可解释性报告: {strategy_id!r}")
        return reports[-1]

    def history_of(self, strategy_id: str) -> tuple[ExplainabilityReport, ...]:
        """全部历史报告（构建序；未知策略 Fail-Closed）。"""
        reports = self._reports.get(strategy_id)
        if not reports:
            raise ExplainabilityError(f"未知可解释性报告: {strategy_id!r}")
        return tuple(reports)
