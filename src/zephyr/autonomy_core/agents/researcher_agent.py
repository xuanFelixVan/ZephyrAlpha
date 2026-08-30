# [BLUEPRINT] MOD-AU-008 | docs/03_modules/_domain_autonomy_core/researcher_agent/blueprint.md
# [MODULE] zephyr.autonomy_core.agents.researcher_agent
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 运行时装配批（C-027 工厂实验产出接入 / C-003 回测门禁指标装配 / 人工门禁链 / 报告入库持久化）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] evaluate/draft_report 纯函数无IO; 假设/指标/配置非法 Fail-Closed; 报告永远 requires_human_gate=True; 门禁触发仅 ACCEPT 且经 human_gate_trigger 回调（不直接入库）; 回调/sink 异常不阻断判定; 评估与门禁信号双审计记录
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_core/researcher_agent/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidHypothesisError; InvalidExperimentMetricsError; InvalidResearcherConfigError
# [TESTS] tests/autonomy/test_researcher_agent.py
# [A_module] module_id=MOD-AU-008 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
ResearcherAgent — 研究 Agent (MOD-AU-008)

B1-00238（AUD-DRAFT-001-DIGEST P1 波 W-P1-11）：Researcher 角色卡（对齐
14号文 §3.0 role façade 族卡模式，与 MOD-AU-007 RiskManager 同族）。
因子假设 → 实验指标（C-027 工厂实验 / C-003 回测门禁产出后注入）→ 确定性
研究裁决（ACCEPT/REJECT/NEEDS_MORE_DATA）→ 研究报告经 report_sink 外发，
**入库必过人工门禁**（human_gate_trigger 回调，本 Agent 不直接入库）；
实验登记委托 experiment_tracking（experiment_sink 回调，不 import 不复制）。

**canonical 声明**：B11-02483（W-P1-12，同名"研究Agent（Researcher）"）以
本模块为 canonical 实现，重复候选按 REVIEW 归并。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: thresholds 参数
#   fields: 参数 thresholds（无注解）
#   code: researcher_agent.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: experiment_sink 参数
#   fields: 参数 experiment_sink（无注解）
#   code: researcher_agent.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: report_sink 参数
#   fields: 参数 report_sink（无注解）
#   code: researcher_agent.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: human_gate_trigger 参数
#   fields: 参数 human_gate_trigger（无注解）
#   code: researcher_agent.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ResearcherAgent
#   name_en: ResearcherAgent
#   intro: 研究 Agent：假设×指标 → 裁决与报告草稿（判定核心纯函数）。
#   desc: 研究 Agent：假设×指标 → 裁决与报告草稿（判定核心纯函数）。 Args: thresholds: 判定阈值配置。 experiment_sink: 实验登记回调（委托 e…；公共方法（定义序）: evaluat…
#   inputs: thresholds experiment_sink report_sink human_gate_trigger
#   outputs: 返回值
#   （注：A1 之后另有 9 个公共定义未列入（含 9 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（10 定义）
#   name_en: public defs
#   intro: ResearcherAgent
#   downstream: 运行时装配批（C-027 工厂实验产出接入 / C-003 回测门禁指标装配 / 人工门禁链 / 报告入库持久化）
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
import math
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "AGENT_CARD",
    "ROLE",
    "ExperimentMetrics",
    "FactorHypothesis",
    "InvalidExperimentMetricsError",
    "InvalidHypothesisError",
    "InvalidResearcherConfigError",
    "ResearcherAction",
    "ResearcherAgent",
    "ResearcherThresholds",
    "ResearchReport",
    "ResearchVerdict",
]

ROLE: Final[str] = "researcher"

AGENT_CARD: Final[dict[str, Any]] = {
    "role": ROLE,
    "capabilities": [
        {
            "id": "experiment_evaluation",
            "name": "因子假设实验指标确定性裁决（IC/Sharpe/回撤/样本门禁）",
            "inputs": "FactorHypothesis + ExperimentMetrics（C-027/C-003 产出注入）",
            "outputs": "ResearchVerdict + ResearchReport（报告草稿）",
            "autonomyLevel": "L1_suggest",
        },
        {
            "id": "report_gate_signal",
            "name": "研究报告入库人工门禁信号",
            "inputs": "ResearchVerdict=ACCEPT",
            "outputs": "human_gate_trigger 回调（入库执行委托人工门禁链）",
            "autonomyLevel": "L2_approval",
        },
    ],
    "autonomyBoundaries": {
        "ai_modifiable": ["报告文本草稿", "NEEDS_MORE_DATA 补充建议"],
        "human_gated": ["研究报告入库人工门禁", "ACCEPT 裁决的入库生效"],
        "immutable": ["判定阈值真源（ResearcherThresholds 配置）", "实验登记/回测执行本体（C-027/C-003/MOD-OBS-001）"],
    },
    "healthCheck": {"heartbeat": "on_demand_evaluate"},
}


class InvalidHypothesisError(ZephyrBaseError):
    """因子假设非法（Fail-Closed）。"""


class InvalidExperimentMetricsError(ZephyrBaseError):
    """实验指标非法（Fail-Closed：不评估脏输入）。"""


class InvalidResearcherConfigError(ZephyrBaseError):
    """Researcher 阈值配置非法。"""


class ResearchVerdict(str, Enum):
    """研究裁决。"""

    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    NEEDS_MORE_DATA = "NEEDS_MORE_DATA"


@dataclass(frozen=True)
class FactorHypothesis:
    """因子假设（不可变）。"""

    hypothesis_id: str
    name: str
    expression: str
    rationale: str

    def __post_init__(self) -> None:
        if not self.hypothesis_id or not self.hypothesis_id.strip():
            raise InvalidHypothesisError("hypothesis_id 不能为空")
        if not self.name or not self.name.strip():
            raise InvalidHypothesisError("name 不能为空")
        if not self.expression or not self.expression.strip():
            raise InvalidHypothesisError("expression 不能为空")


@dataclass(frozen=True)
class ExperimentMetrics:
    """实验指标快照（由 C-027 工厂实验 / C-003 回测门禁产出后注入）。"""

    ic: float  # 信息系数 ∈ [-1, 1]
    sharpe: float  # 夏普比（有限实数）
    max_drawdown: float  # 最大回撤（非负，0.2=20%）
    sample_count: int  # 样本数（非负）

    def __post_init__(self) -> None:
        if not (-1.0 <= self.ic <= 1.0):
            raise InvalidExperimentMetricsError(f"ic 必须 ∈ [-1,1]: {self.ic}")
        if math.isnan(self.sharpe) or math.isinf(self.sharpe):
            raise InvalidExperimentMetricsError(f"sharpe 必须为有限实数: {self.sharpe}")
        if self.max_drawdown < 0:
            raise InvalidExperimentMetricsError(f"max_drawdown 不能为负: {self.max_drawdown}")
        if self.sample_count < 0:
            raise InvalidExperimentMetricsError(f"sample_count 不能为负: {self.sample_count}")


@dataclass(frozen=True)
class ResearcherThresholds:
    """判定阈值配置（C 类可调参数）。"""

    min_ic: float = 0.03
    min_sharpe: float = 1.0
    max_drawdown: float = 0.2
    min_samples: int = 60

    def __post_init__(self) -> None:
        if not (0.0 < self.min_ic <= 1.0):
            raise InvalidResearcherConfigError(f"min_ic 必须 ∈ (0,1]: {self.min_ic}")
        if self.min_sharpe <= 0:
            raise InvalidResearcherConfigError(f"min_sharpe 必须为正: {self.min_sharpe}")
        if self.max_drawdown <= 0:
            raise InvalidResearcherConfigError(f"max_drawdown 必须为正: {self.max_drawdown}")
        if self.min_samples <= 0:
            raise InvalidResearcherConfigError(f"min_samples 必须为正: {self.min_samples}")


@dataclass(frozen=True)
class ResearchReport:
    """研究报告草稿（不可变；入库必过人工门禁）。"""

    hypothesis_id: str
    verdict: ResearchVerdict
    reasons: tuple[str, ...]
    metrics: ExperimentMetrics
    requires_human_gate: bool = True


@dataclass(frozen=True)
class ResearcherAction:
    """act 编排结果：裁决 + 报告 + 门禁信号 + 双审计记录。"""

    verdict: ResearchVerdict
    report: ResearchReport
    gate_signaled: bool
    audit_records: tuple[dict[str, Any], ...]


class ResearcherAgent:
    """研究 Agent：假设×指标 → 裁决与报告草稿（判定核心纯函数）。

    Args:
        thresholds: 判定阈值配置。
        experiment_sink: 实验登记回调（委托 experiment_tracking）；异常不阻断。
        report_sink: 报告外发回调；异常不阻断。
        human_gate_trigger: 人工门禁信号回调（payload dict）；异常不阻断，
            gate_signaled 如实记 False。
    """

    ROLE: Final[str] = ROLE
    AGENT_CARD: Final[dict[str, Any]] = AGENT_CARD

    def __init__(
        self,
        thresholds: ResearcherThresholds | None = None,
        experiment_sink: Callable[[dict[str, Any]], None] | None = None,
        report_sink: Callable[[dict[str, Any]], None] | None = None,
        human_gate_trigger: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._thresholds = thresholds or ResearcherThresholds()
        self._experiment_sink = experiment_sink
        self._report_sink = report_sink
        self._human_gate_trigger = human_gate_trigger

    # ── 判定阶梯（纯函数） ──────────────────────────────────────────────────

    def _verdict_with_reasons(
        self, hypothesis: FactorHypothesis, metrics: ExperimentMetrics
    ) -> tuple[ResearchVerdict, tuple[str, ...]]:
        t = self._thresholds
        hard_reasons: list[str] = []
        if metrics.max_drawdown > t.max_drawdown:
            hard_reasons.append(f"回撤 {metrics.max_drawdown:.4f} 破上限 {t.max_drawdown:.4f}（回测门禁硬否）")
        if metrics.sample_count < t.min_samples:
            hard_reasons.append(f"样本数 {metrics.sample_count} < 下限 {t.min_samples}（统计效力不足硬否）")
        if hard_reasons:
            return ResearchVerdict.REJECT, tuple(hard_reasons)
        ic_ok = metrics.ic >= t.min_ic
        sharpe_ok = metrics.sharpe >= t.min_sharpe
        if ic_ok and sharpe_ok:
            return ResearchVerdict.ACCEPT, (
                f"IC {metrics.ic:.4f} ≥ {t.min_ic:.4f} 且 Sharpe {metrics.sharpe:.4f} ≥ {t.min_sharpe:.4f}（双达标）",
            )
        if ic_ok or sharpe_ok or metrics.ic >= t.min_ic / 2:
            weak = []
            weak.append(f"IC {metrics.ic:.4f}{'≥' if ic_ok else '<'}{t.min_ic:.4f}")
            weak.append(f"Sharpe {metrics.sharpe:.4f}{'≥' if sharpe_ok else '<'}{t.min_sharpe:.4f}")
            return ResearchVerdict.NEEDS_MORE_DATA, (
                f"边缘证据（{'，'.join(weak)}），建议补充样本/正交性验证: 假设 {hypothesis.name}",
            )
        return ResearchVerdict.REJECT, (
            f"IC {metrics.ic:.4f} < {t.min_ic / 2:.4f}（半数阈值）且 Sharpe {metrics.sharpe:.4f} < {t.min_sharpe:.4f}（信号过弱）",
        )

    def evaluate(self, hypothesis: FactorHypothesis, metrics: ExperimentMetrics) -> ResearchVerdict:
        """确定性判定阶梯：硬否 → 双达标 ACCEPT → 边缘 NEEDS_MORE_DATA → REJECT。"""
        return self._verdict_with_reasons(hypothesis, metrics)[0]

    def draft_report(self, hypothesis: FactorHypothesis, metrics: ExperimentMetrics) -> ResearchReport:
        """报告草稿（纯函数）：永远 requires_human_gate=True。"""
        verdict, reasons = self._verdict_with_reasons(hypothesis, metrics)
        return ResearchReport(
            hypothesis_id=hypothesis.hypothesis_id,
            verdict=verdict,
            reasons=reasons,
            metrics=metrics,
            requires_human_gate=True,
        )

    # ── 编排：评估→登记→报告→（ACCEPT）门禁信号，双审计 ─────────────────────

    def act(self, hypothesis: FactorHypothesis, metrics: ExperimentMetrics) -> ResearcherAction:
        """evaluate → 实验登记 → 报告外发 → ACCEPT 时人工门禁信号。"""
        report = self.draft_report(hypothesis, metrics)
        eval_record: dict[str, Any] = {
            "record_type": "RESEARCHER_EVALUATION",
            "role": ROLE,
            "hypothesis_id": hypothesis.hypothesis_id,
            "verdict": report.verdict.value,
            "reasons": list(report.reasons),
            "metrics": {
                "ic": metrics.ic,
                "sharpe": metrics.sharpe,
                "max_drawdown": metrics.max_drawdown,
                "sample_count": metrics.sample_count,
            },
        }
        records: list[dict[str, Any]] = [eval_record]
        self._emit(self._experiment_sink, eval_record, "experiment_sink")
        self._emit(
            self._report_sink,
            {
                "record_type": "RESEARCH_REPORT",
                "role": ROLE,
                "hypothesis_id": report.hypothesis_id,
                "verdict": report.verdict.value,
                "requires_human_gate": report.requires_human_gate,
            },
            "report_sink",
        )
        gate_signaled = False
        if report.verdict is ResearchVerdict.ACCEPT:
            payload: dict[str, Any] = {
                "role": ROLE,
                "hypothesis_id": hypothesis.hypothesis_id,
                "verdict": report.verdict.value,
                "note": "研究报告入库必过人工门禁；本 Agent 不直接入库",
            }
            if self._human_gate_trigger is not None:
                try:
                    self._human_gate_trigger(payload)
                    gate_signaled = True
                except Exception:  # noqa: BLE001 — 回调异常不阻断，如实标记
                    _logger.exception("human_gate_trigger 异常（已降级，gate_signaled=False）")
            records.append(
                {
                    "record_type": "RESEARCHER_GATE_SIGNAL",
                    "role": ROLE,
                    "hypothesis_id": hypothesis.hypothesis_id,
                    "gate_signaled": gate_signaled,
                }
            )
        return ResearcherAction(
            verdict=report.verdict,
            report=report,
            gate_signaled=gate_signaled,
            audit_records=tuple(records),
        )

    def _emit(
        self,
        sink: Callable[[dict[str, Any]], None] | None,
        record: dict[str, Any],
        sink_name: str,
    ) -> None:
        if sink is not None:
            try:
                sink(record)
            except Exception:  # noqa: BLE001 — sink 异常不阻断（记录仍内嵌返回值）
                _logger.exception("%s 异常（已降级，判定不受影响）", sink_name)
