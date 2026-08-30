# [BLUEPRINT] MOD-INT-LLM-SELFEVAL | docs/03_modules/_domain_intelligence/llm_self_evaluation/blueprint.md
# [MODULE] zephyr.intelligence.llm_self_evaluation
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] 无（评估核心纯内存；judge/三模型回调/cot_rechecker/review_sink/audit_sink 全注入）
# [CONSUMERS] 运行时装配批（judge 接 exam_judge / 三模型接 llm 池回调 / 争议人工审核队列 / CoT 审计接审计链）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Judge 三维词表闭合(factuality|logic|risk)且分值须落 [0,1]；投票模型恰为三个独立回调；CoT 逐步重验逐条标记；一致性<阈值或 CoT 不一致→争议降权+人工审核；输出硬标注 advisory 不可直接交易；CoT 链随裁决写审计；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_intelligence/llm_self_evaluation/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] LlmSelfEvalError(占位 ZA-IT-UNREGISTERED-LLM-SELFEVAL)——模型数非三/回调缺失/judge 分值越界/空 query/空 CoT 链/空结论/非法阈值时抛
# [TESTS] tests/intelligence/test_llm_self_evaluation.py
# [A_module] module_id=MOD-INT-LLM-SELFEVAL | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
LlmSelfEvaluation — LLM 自评估与交叉验证（MOD-INT-LLM-SELFEVAL）。

B10-01883（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-AISA-013，A1 §29.37）：
LLM-as-Judge **三维评分**（事实/逻辑/风险，judge 注入）+ CoT 推理链
**反向自校验**（逐步重验标记不一致）+ **三模型独立分析投票**（模型回调注
入，一致性度量）+ 低一致性**标争议降权或人工审核** + 结论**不可直接触发
交易**硬约束（输出硬标注 advisory）+ CoT 链写审计。canonical 承接
AISA-010 归并。

查重分工（蓝图 §0）：exam_judge=模型考试评分器（本件经注入 judge 消费其
语义，不重建评分实现）；model_profiling=模型画像（零交集）；本件输出仅
advisory 信号，无下单语义。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: judge 参数
#   fields: 参数 judge（无注解）
#   code: llm_self_evaluation.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: models 参数
#   fields: 参数 models（无注解）
#   code: llm_self_evaluation.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: cot_rechecker 参数
#   fields: 参数 cot_rechecker（无注解）
#   code: llm_self_evaluation.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: consistency_threshold 参数
#   fields: 参数 consistency_threshold（无注解）
#   code: llm_self_evaluation.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① LlmSelfEvaluation
#   name_en: LlmSelfEvaluation
#   intro: LLM 自评估件（Judge 三维 + CoT 自校验 + 三模型投票 + 争议处置）。
#   desc: LLM 自评估件（Judge 三维 + CoT 自校验 + 三模型投票 + 争议处置）。；公共方法（定义序）: evaluate；源码 L157-L275
#   inputs: judge models cot_rechecker consistency_threshold dispute_weight revie…
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: LlmSelfEvaluation
#   downstream: 运行时装配批（judge 接 exam_judge / 三模型接 llm 池回调 / 争议人工审核队列 / CoT 审计接审计链）
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
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "CotStepCheck",
    "EvalDimension",
    "EvalVerdict",
    "LlmSelfEvalError",
    "LlmSelfEvaluation",
    "ModelVote",
    "OUTPUT_LABEL_ADVISORY",
]

#: 输出硬标签：结论仅 advisory，不可直接触发交易
OUTPUT_LABEL_ADVISORY: Final = "advisory"

#: 默认一致性阈值（三模型多数一致 = 2/3）
_DEFAULT_CONSISTENCY_THRESHOLD: Final = 2.0 / 3.0


class LlmSelfEvalError(Exception):
    """LLM 自评估输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-IT-UNREGISTERED-LLM-SELFEVAL。
    """


class EvalDimension(str, Enum):
    """Judge 三维评分维度（词表闭合）。"""

    FACTUALITY = "factuality"
    LOGIC = "logic"
    RISK = "risk"


@dataclass(frozen=True)
class CotStepCheck:
    """CoT 单步反向重验结果（frozen）。"""

    step_index: int
    step_text: str
    consistent: bool


@dataclass(frozen=True)
class ModelVote:
    """单模型独立分析投票（frozen）。"""

    model_name: str
    conclusion: str


@dataclass(frozen=True)
class EvalVerdict:
    """自评估裁决（frozen；output_label 恒为 advisory，不可直接交易）。"""

    query: str
    dimension_scores: tuple[tuple[EvalDimension, float], ...]
    cot_checks: tuple[CotStepCheck, ...]
    cot_consistent: bool
    votes: tuple[ModelVote, ...]
    consistency: float
    majority_conclusion: str
    disputed: bool
    weight: float
    requires_human_review: bool
    output_label: str = field(default=OUTPUT_LABEL_ADVISORY)
    tradeable: bool = field(default=False)

    def __post_init__(self) -> None:
        # 硬约束：结论仅 advisory，不可直接触发交易（不可绕过）
        if self.output_label != OUTPUT_LABEL_ADVISORY:
            raise LlmSelfEvalError(f"output_label 非法: {self.output_label!r}（恒为 advisory）")
        if self.tradeable:
            raise LlmSelfEvalError("tradeable=True 非法（advisory 结论不可直接交易）")


class LlmSelfEvaluation:
    """LLM 自评估件（Judge 三维 + CoT 自校验 + 三模型投票 + 争议处置）。"""

    def __init__(
        self,
        *,
        judge: Callable[[str, EvalDimension], float],
        models: Mapping[str, Callable[[str], str]],
        cot_rechecker: Callable[[int, str], bool],
        consistency_threshold: float = _DEFAULT_CONSISTENCY_THRESHOLD,
        dispute_weight: float = 0.5,
        review_sink: Callable[[EvalVerdict], None] | None = None,
        audit_sink: Callable[[EvalVerdict], None] | None = None,
    ) -> None:
        if not callable(judge):
            raise LlmSelfEvalError("judge 未注入")
        if not callable(cot_rechecker):
            raise LlmSelfEvalError("cot_rechecker 未注入")
        if not models or len(models) != 3:
            raise LlmSelfEvalError(f"三模型投票须恰为 3 个独立模型，实收 {len(models) if models else 0}")
        for name, fn in models.items():
            if not name:
                raise LlmSelfEvalError("模型名为空")
            if not callable(fn):
                raise LlmSelfEvalError(f"模型回调不可调用: {name!r}")
        if not (0.0 < consistency_threshold <= 1.0):
            raise LlmSelfEvalError(f"consistency_threshold 越界 (0,1]: {consistency_threshold!r}")
        if not (0.0 < dispute_weight < 1.0):
            raise LlmSelfEvalError(f"dispute_weight 越界 (0,1): {dispute_weight!r}")
        self._judge = judge
        self._models: dict[str, Callable[[str], str]] = dict(models)
        self._cot_rechecker = cot_rechecker
        self._threshold = consistency_threshold
        self._dispute_weight = dispute_weight
        self._review_sink = review_sink
        self._audit_sink = audit_sink

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _score_dimensions(self, query: str) -> tuple[tuple[EvalDimension, float], ...]:
        scores: list[tuple[EvalDimension, float]] = []
        for dim in EvalDimension:
            score = float(self._judge(query, dim))
            if not (0.0 <= score <= 1.0):
                raise LlmSelfEvalError(f"judge 分值越界 [0,1]: {dim.value}={score!r}")
            scores.append((dim, score))
        return tuple(scores)

    def _verify_cot(self, cot_steps: Sequence[str]) -> tuple[CotStepCheck, ...]:
        checks: list[CotStepCheck] = []
        for i, step in enumerate(cot_steps):
            if not step:
                raise LlmSelfEvalError(f"CoT 第 {i} 步为空")
            consistent = bool(self._cot_rechecker(i, step))
            checks.append(CotStepCheck(step_index=i, step_text=step, consistent=consistent))
        return tuple(checks)

    def _vote(self, query: str) -> tuple[ModelVote, ...]:
        votes: list[ModelVote] = []
        for name, fn in self._models.items():
            conclusion = fn(query)
            if not conclusion:
                raise LlmSelfEvalError(f"模型 {name!r} 结论为空")
            votes.append(ModelVote(model_name=name, conclusion=conclusion))
        return tuple(votes)

    @staticmethod
    def _majority(votes: tuple[ModelVote, ...]) -> tuple[str, float]:
        counts: dict[str, int] = {}
        for v in votes:
            counts[v.conclusion] = counts.get(v.conclusion, 0) + 1
        # 多数结论：票数降序，并列按结论名序（确定性）
        winner = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0]
        return winner[0], winner[1] / len(votes)

    # ── 评估管线 ──────────────────────────────────────────────────────────

    def evaluate(self, query: str, cot_steps: Sequence[str]) -> EvalVerdict:
        """评估：三维评分 → CoT 逐步重验 → 三模型投票 → 一致性 → 争议处置。

        一致性<阈值或 CoT 任一步不一致 → 争议（降权 + 人工审核队列）；
        输出硬标注 advisory（tradeable=False），裁决含 CoT 链写审计。
        """
        if not query:
            raise LlmSelfEvalError("query 为空")
        if not cot_steps:
            raise LlmSelfEvalError("CoT 链为空")

        dimension_scores = self._score_dimensions(query)
        cot_checks = self._verify_cot(cot_steps)
        cot_consistent = all(c.consistent for c in cot_checks)
        votes = self._vote(query)
        majority, consistency = self._majority(votes)

        disputed = (consistency < self._threshold) or (not cot_consistent)
        verdict = EvalVerdict(
            query=query,
            dimension_scores=dimension_scores,
            cot_checks=cot_checks,
            cot_consistent=cot_consistent,
            votes=votes,
            consistency=consistency,
            majority_conclusion=majority,
            disputed=disputed,
            weight=self._dispute_weight if disputed else 1.0,
            requires_human_review=disputed,
        )
        if disputed:
            _log.warning(
                "LLM 结论争议: consistency=%.4f cot_consistent=%s → 降权 %.2f + 人工审核",
                consistency,
                cot_consistent,
                verdict.weight,
            )
            if self._review_sink is not None:
                self._review_sink(verdict)
        if self._audit_sink is not None:
            self._audit_sink(verdict)
        return verdict
