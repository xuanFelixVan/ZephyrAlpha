# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.hallucination_detector
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas; zephyr.shared.utils.time_utils
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_hallucination_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
HallucinationDetector · Chain-of-Verification（CoVe）幻觉检测器
================================================================

Task ID      : T-3-07
KBG          :  四步 + Sonnet 4.6 × GLM-5.1 双模型交叉）
safety_level : H
Depends      :  三阶段）、 策略）、
                契约）、T-2-32（ai_behavior_audit_logger）

本模块职责
----------
在不外接任何生产 LLM SDK 的前提下，提供一个 **可注入调用者（ModelCaller）**
的 CoVe 幻觉检测执行引擎。核心能力：

1. **CoVe 四步流程**
   - Step 1 Baseline + Plan（合并单次调用，主模型 Sonnet 4.6）
   - Step 2 Verify（异构验证模型 GLM-5.1 独立作答 verify_questions）
   - Step 3 Cross-Check（本地一致性打分，无 API 调用）
   - Step 4 Final Check（仅 risk_level=H 且 inconsistency_score>0 触发）

2. **触发矩阵（§4.1）**
   - L1 白名单：`source_stage in {semantic, llm}` 且 intent_confidence<0.90；
     或 MCP `safety_level=H`；或 `requires_human=True`；或 frozen 资产 → 强制触发
   - L2 灰名单：落盘到 docs/ 的 claim / MCP safety=M → 按预算条件触发
   - L3 黑名单：纯代码补全 / session 元信息 → 禁止触发（节省成本）

3. **风险分级阈值（§4.3）**
   - L：inconsistency_score ≤ 0.40 判定非幻觉；> 0.75 判定幻觉
   - M：≤ 0.25 / > 0.60；中间带强制走 Step 4
   - H：≤ 0.10 / > 0.40；中间带强制人工介入（requires_human=True）

4. **降级级联（§4.4）**
   - 双模型全可达 → 正常 CoVe
   - 仅一方可达 → 单模型 lite（fallback_used="single_model"）
   - 两方都不可达 / 本地亦无 embedding → keyword 规则兜底（fallback_used="keyword"）

5. **预算控制（§4.5）**
   - 月度软上限 $15、日度软上限 $0.75、单次 ≤ $0.02
   - L/M 级超出日度后直接跳过 CoVe（budget_skip）；H 级强制执行并记告警

6. **keyword 规则兜底 `_KEYWORD_HALLU_RULES`**
   - 数值异常（IC/Sharpe/win_rate 超 [-1,1]）
   - 不存在的 .md/.py/.yaml 文件路径
   - 违禁断言（"Meta 论文 XXXX-YYYY 证明"等无源引用）
   - frozen 资产未经 Handoff 的修改建议

零外部依赖
----------
- 只引入 pydantic（已是项目 BASE_CONFIG 依赖）
- LLM 调用通过 Protocol 注入，生产环境再提供真实 caller
- 审计写入通过可选的 ``audit_logger`` 注入，默认跳过
"""

from __future__ import annotations

from typing import Final
import hashlib
import json
import re
import time
from collections.abc import Callable
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Literal,
    Protocol,
    runtime_checkable,
)

from pydantic import BaseModel, Field, field_validator

from zephyr.integration.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.utils.time_utils import default_now

__all__ = [
    "KEYWORD_HALLU_RULES",
    "BudgetState",
    "CoVeStepError",
    "FallbackMode",
    "HallucinationDetector",
    "HallucinationResult",
    "ModelCallResult",
    "ModelCaller",
    "RiskLevel",
    "TriggerLevel",
    "build_detector_with_defaults",
]

# ---------------------------------------------------------------------------
# 枚举与基础类型
# ---------------------------------------------------------------------------


class TriggerLevel(str, Enum):
    """三级触发矩阵（ §4.1）。"""

    L1_WHITELIST = "L1"
    L2_GREY = "L2"
    L3_BLACKLIST = "L3"


class RiskLevel(str, Enum):
    """风险等级（与 schemas.SafetyLevel 一致：L/M/H，向后兼容别名）。"""

    L = "L"
    M = "M"
    H = "H"


class FallbackMode(str, Enum):
    """降级模式枚举。"""

    NONE = "none"
    SINGLE_MODEL = "single_model"
    KEYWORD = "keyword"
    BUDGET_SKIP = "budget_skip"


class CoVeStepError(RuntimeError):
    """CoVe 步骤执行失败异常。"""


# ---------------------------------------------------------------------------
# Protocol：模型调用者（由生产代码注入真实 LLM SDK）
# ---------------------------------------------------------------------------


class ModelCallResult(BaseModel):
    """
    单次模型调用的结果封装。

    Attributes
    ----------
    content : str
        模型文本输出。对 Step 1 期望为 JSON 字符串；对 Step 2 期望为每行一个答案。
    cost_usd : float
        本次调用的实际费用（美元）。
    latency_ms : int
        本次调用耗时（毫秒）。
    success : bool
        是否成功返回。False 表示 API 不可达 / 限流 / 超时。
    error : Optional[str]
        失败原因（success=False 时必填）。
    """

    model_config = BASE_CONFIG

    content: str = Field(default="", description="模型文本输出")
    cost_usd: float = Field(default=0.0, ge=0.0, description="单次费用（USD）")
    latency_ms: int = Field(default=0, ge=0, description="单次耗时（毫秒）")
    success: bool = Field(default=True, description="是否成功")
    error: str | None = Field(default=None, description="失败原因")


@runtime_checkable
class ModelCaller(Protocol):
    """
    模型调用者协议。生产实现封装真实 LLM SDK（Anthropic / Zhipu 等）；
    单元测试传入 mock 即可。

    设计成 Protocol 是为了解耦：本模块**不**依赖任何具体 SDK。
    """

    def __call__(self, prompt: str, *, purpose: str) -> ModelCallResult:  # pragma: no cover - Protocol 签名
        ...


# ---------------------------------------------------------------------------
# Pydantic 输出契约（HallucinationResult）
# ---------------------------------------------------------------------------


class HallucinationResult(BaseModel):
    """幻觉检测最终输出（ §4.3 契约）。"""

    model_config = BASE_CONFIG

    claim: str = Field(min_length=1, description="被检测的 claim 文本")
    is_hallucination: bool = Field(description="是否判定为幻觉")
    confidence: float = Field(ge=0.0, le=1.0, description="置信度 0.0–1.0")
    risk_level: Literal["L", "M", "H"] = Field(description="风险等级")
    inconsistency_score: float = Field(ge=0.0, le=1.0, description="不一致分数 0.0–1.0")
    verify_questions: list[str] = Field(default_factory=list, description="Step 1 拆出的验证问题")
    verify_answers: list[dict[str, Any]] = Field(
        default_factory=list, description="Step 2 异构模型对 verify_questions 的作答"
    )
    evidence: list[str] = Field(default_factory=list, description="可展示给 Owner 的证据片段")
    requires_human: bool = Field(default=False, description="是否需要 Handoff 人工介入")
    execution_model: str = Field(default="", description="主模型名称")
    verifier_model: str = Field(default="", description="验证模型名称")
    corrected_answer: str | None = Field(default=None, description="Step 4 修正后的答案")
    latency_ms: int = Field(default=0, ge=0, description="端到端耗时")
    cost_usd: float = Field(default=0.0, ge=0.0, description="端到端费用")
    fallback_used: str | None = Field(default=None, description="降级模式，见 FallbackMode")
    triggered: bool = Field(default=True, description="CoVe 是否实际运行（L3 黑名单时为 False）")

    @field_validator("verify_questions")
    @classmethod
    def validate_questions_count(cls, v: list[str]) -> list[str]:
        """verify_questions 限 0-5 条；Step 1 产出 3-5 条，兜底可为 0（未触发）。"""
        if len(v) > 5:
            raise ValueError("verify_questions 不得超过 5 条")
        return v


# ---------------------------------------------------------------------------
# 预算追踪
# ---------------------------------------------------------------------------


class BudgetState(BaseModel):
    """CoVe 月度 / 日度预算状态。"""

    model_config = BASE_CONFIG

    monthly_spent_usd: float = Field(default=0.0, ge=0.0)
    daily_spent_usd: float = Field(default=0.0, ge=0.0)
    monthly_budget_usd: float = Field(default=15.0, gt=0.0)
    daily_budget_usd: float = Field(default=0.75, gt=0.0)
    per_call_max_usd: float = Field(default=0.02, gt=0.0)
    current_month: str = Field(default="", description="YYYY-MM 用于月度窗口重置")
    current_day: str = Field(default="", description="YYYY-MM-DD 用于日度窗口重置")

    def reset_if_window_changed(self, now: datetime) -> None:
        """若跨天 / 跨月则自动重置对应窗口累计。"""
        today = now.date().isoformat()
        month = now.strftime("%Y-%m")
        if self.current_day != today:
            self.current_day = today
            self.daily_spent_usd = 0.0
        if self.current_month != month:
            self.current_month = month
            self.monthly_spent_usd = 0.0

    def can_afford(self, risk_level: RiskLevel) -> bool:
        """L/M 级在日度超预算时返回 False；H 级始终强制执行（在外层记告警）。"""
        if risk_level is RiskLevel.H:
            return True
        return self.daily_spent_usd < self.daily_budget_usd

    def record(self, cost_usd: float) -> None:
        self.daily_spent_usd += cost_usd
        self.monthly_spent_usd += cost_usd


# ---------------------------------------------------------------------------
# Keyword 规则兜底
# ---------------------------------------------------------------------------

_NUMERIC_FIELD_PATTERN = re.compile(
    r"\b(IC|Sharpe|win[_\s-]*rate|ic|sharpe)\s*[:=]\s*(-?\d+\.?\d*)",
    re.IGNORECASE,
)
_FILE_PATH_PATTERN = re.compile(r"(?<![A-Za-z0-9_/.-])([A-Za-z0-9_./-]+\.(?:md|py|yaml|yml))(?![A-Za-z0-9_/])")
_FROZEN_ASSET_PATTERN = re.compile(
    r"(tool-contracts\.yaml)",
    re.IGNORECASE,
)
_SUSPECT_CITATIONS = [
    re.compile(r"Meta\s*(?:20\d{2})?\s*(?:论文|paper)", re.IGNORECASE),
    re.compile(r"Citadel\s*(?:内部|internal)", re.IGNORECASE),
    re.compile(r"Google\s*(?:20\d{2})?\s*白皮书", re.IGNORECASE),
    re.compile(r"OpenAI\s*(?:内部|internal)", re.IGNORECASE),
    re.compile(r"Jane\s*Street\s*(?:内部|internal)", re.IGNORECASE),
]


def _numeric_out_of_range(claim: str) -> list[str]:
    """IC/Sharpe/win_rate 超出 [-1, 1]（Sharpe 放宽到 ±5）。"""
    evidence: list[str] = []
    for match in _NUMERIC_FIELD_PATTERN.finditer(claim):
        field, raw_value = match.group(1).lower(), match.group(2)
        try:
            value = float(raw_value)
        except ValueError:
            continue
        if "sharpe" in field:
            if value < -5.0 or value > 5.0:
                evidence.append(f"numeric_out_of_range: {field}={value}（超出 ±5）")
        else:
            if value < -1.0 or value > 1.0:
                evidence.append(f"numeric_out_of_range: {field}={value}（超出 ±1）")
    return evidence


def _missing_files(claim: str, repo_root: Path | None) -> list[str]:
    """claim 中提及的 .md/.py/.yaml 路径若 repo 下不存在则标红。"""
    if repo_root is None:
        return []
    evidence: list[str] = []
    for match in _FILE_PATH_PATTERN.finditer(claim):
        path_str = match.group(1)
        if path_str.startswith("http") or "://" in path_str:
            continue
        candidate = repo_root / path_str
        if not candidate.exists():
            evidence.append(f"missing_file: {path_str}")
    return evidence


def _suspect_citations(claim: str) -> list[str]:
    """黑名单断言：Meta/Citadel/Google 等具体但不可验证的引用。"""
    evidence: list[str] = []
    for pattern in _SUSPECT_CITATIONS:
        if pattern.search(claim):
            evidence.append(f"suspect_citation: {pattern.pattern}")
    return evidence


def _frozen_asset_mutation(claim: str, handoff_approved: bool) -> list[str]:
    """frozen 资产（tool_contracts.yaml / KBG-*.md）未经 Handoff 修改建议标红。"""
    if handoff_approved:
        return []
    evidence: list[str] = []
    if _FROZEN_ASSET_PATTERN.search(claim) and re.search(
        r"(修改|修订|更新|替换|删除|modify|update|replace|delete)", claim, re.IGNORECASE
    ):
        evidence.append("frozen_asset_mutation: claim 建议修改 frozen 资产但未 Handoff")
    return evidence


KEYWORD_HALLU_RULES: Final[dict[str, Callable[..., list[str]]]] = {
    "numeric_out_of_range": _numeric_out_of_range,
    "missing_files": _missing_files,
    "suspect_citations": _suspect_citations,
    "frozen_asset_mutation": _frozen_asset_mutation,
}
"""keyword 规则表。单元测试可通过 import 直接校验每条规则。"""

# ---------------------------------------------------------------------------
# 主检测器
# ---------------------------------------------------------------------------

_THRESHOLDS: dict[RiskLevel, tuple[float, float]] = {
    RiskLevel.L: (0.40, 0.75),
    RiskLevel.M: (0.25, 0.60),
    RiskLevel.H: (0.10, 0.40),
}
"""风险分级阈值：(非幻觉上限, 幻觉下限)。 §4.3。"""


def _hash_claim(claim: str) -> str:
    return "claim#sha256:" + hashlib.sha256(claim.encode("utf-8")).hexdigest()[:16]


def _token_overlap(a: str, b: str) -> float:
    """简易 Jaccard token 相似度（兜底语义匹配，无 embedding 时使用）。"""
    ta = set(re.findall(r"[\w\u4e00-\u9fff]+", a.lower()))
    tb = set(re.findall(r"[\w\u4e00-\u9fff]+", b.lower()))
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _contains_negation(text: str) -> bool:
    return bool(re.search(r"(不是|不对|不会|不能|错误|no\b|not\b|never\b|wrong)", text, re.IGNORECASE))


class HallucinationDetector:
    """
    CoVe 幻觉检测器。

    Parameters
    ----------
    primary_caller : Optional[ModelCaller]
        Step 1 Baseline+Plan 的主模型调用者（默认 Sonnet 4.6）。
        None 表示不可达 → 跳过 Step 1，触发降级。
    verifier_caller : Optional[ModelCaller]
        Step 2 Verify 的异构验证模型调用者（默认 GLM-5.1）。
        None 表示不可达 → 触发单模型降级或 keyword 兜底。
    execution_model_name : str
        主模型名称（写入审计日志）。
    verifier_model_name : str
        验证模型名称（写入审计日志）。
    monthly_budget_usd : float
        月度软上限（默认 $15）。
    daily_budget_usd : float
        日度软上限（默认 $0.75）。
    per_call_max_usd : float
        单次硬上限（默认 $0.02）。
    repo_root : Optional[Path]
        用于 keyword 规则 "missing_files" 检查的仓库根目录。
    now : Callable[[], datetime]
        注入时间源，便于测试跨窗口重置。
    audit_logger : Optional[Callable[[HallucinationResult], None]]
        可选审计回调，每次 detect 完成后调用一次。
    """

    def __init__(
        self,
        *,
        primary_caller: ModelCaller | None = None,
        verifier_caller: ModelCaller | None = None,
        execution_model_name: str = "Sonnet 4.6",
        verifier_model_name: str = "GLM-5.1",
        monthly_budget_usd: float = 15.0,
        daily_budget_usd: float = 0.75,
        per_call_max_usd: float = 0.02,
        repo_root: Path | None = None,
        now: Callable[[], datetime] = default_now,
        audit_logger: Callable[[HallucinationResult], None] | None = None,
    ) -> None:
        self._primary = primary_caller
        self._verifier = verifier_caller
        self._execution_model_name = execution_model_name
        self._verifier_model_name = verifier_model_name
        self._per_call_max_usd = per_call_max_usd
        self._repo_root = repo_root
        self._now = now
        self._audit_logger = audit_logger
        self._budget = BudgetState(
            monthly_budget_usd=monthly_budget_usd,
            daily_budget_usd=daily_budget_usd,
            per_call_max_usd=per_call_max_usd,
        )

    # ------------------------------------------------------------------ public

    @property
    def budget_state(self) -> BudgetState:
        """用于测试 / 观测当前预算状态。"""
        return self._budget

    def should_trigger(
        self,
        risk_level: RiskLevel,
        *,
        source_stage: Literal["keyword", "semantic", "llm"] | None = None,
        intent_confidence: float | None = None,
        mcp_safety_level: RiskLevel | None = None,
        target_is_doc: bool = False,
        requires_human: bool = False,
        frozen_asset_touch: bool = False,
        historical_recurrence: bool = False,
        pure_codegen: bool = False,
        meta_info: bool = False,
    ) -> TriggerLevel:
        """
        判定触发级别（ §4.1）。

        Returns
        -------
        TriggerLevel
            - L3_BLACKLIST: 禁止触发（pure codegen / session meta）
            - L1_WHITELIST: 强制触发
            - L2_GREY: 条件触发（由预算进一步决定）
        """
        if pure_codegen or meta_info:
            return TriggerLevel.L3_BLACKLIST

        if (
            (source_stage in ("semantic", "llm") and (intent_confidence is None or intent_confidence < 0.90))
            or mcp_safety_level is RiskLevel.H
            or requires_human
            or frozen_asset_touch
            or historical_recurrence
            or risk_level is RiskLevel.H
        ):
            return TriggerLevel.L1_WHITELIST

        if target_is_doc or mcp_safety_level is RiskLevel.M or risk_level is RiskLevel.M:
            return TriggerLevel.L2_GREY

        return TriggerLevel.L2_GREY

    def detect(
        self,
        claim: str,
        context: dict[str, Any] | None = None,
        risk_level: RiskLevel | str = RiskLevel.M,
        *,
        handoff_approved: bool = False,
        trigger_level: TriggerLevel = TriggerLevel.L1_WHITELIST,
    ) -> HallucinationResult:
        """
        执行一次幻觉检测（CoVe 四步 + 降级级联 + 预算门禁）。

        Parameters
        ----------
        claim : str
            被检测的 AI 输出。不得为空。
        context : dict
            附加上下文（query / domain 等）；允许为 None。
        risk_level : RiskLevel | str
            风险等级 L/M/H。
        handoff_approved : bool
            frozen 资产修改是否已获 Handoff 批准（关闭对应 keyword 规则）。
        trigger_level : TriggerLevel
            外部预判的触发级别；L3_BLACKLIST 时直接返回 triggered=False 结果。

        Returns
        -------
        HallucinationResult
        """
        if not claim or not claim.strip():
            raise ValueError("claim 不得为空")
        rl = risk_level if isinstance(risk_level, RiskLevel) else RiskLevel(str(risk_level).upper())
        context = context or {}
        started_at = time.perf_counter()
        self._budget.reset_if_window_changed(self._now())

        if trigger_level is TriggerLevel.L3_BLACKLIST:
            return self._skip_result(claim, rl, reason="L3_BLACKLIST", started_at=started_at)

        if not self._budget.can_afford(rl):
            return self._skip_result(claim, rl, reason=FallbackMode.BUDGET_SKIP.value, started_at=started_at)

        primary_ok = self._primary is not None
        verifier_ok = self._verifier is not None

        try:
            if primary_ok and verifier_ok:
                result = self._run_cove(claim, context, rl, handoff_approved, started_at)
            elif primary_ok ^ verifier_ok:
                result = self._run_single_model_lite(claim, rl, handoff_approved, started_at)
            else:
                result = self._run_keyword_fallback(claim, rl, handoff_approved, started_at)
        except CoVeStepError:
            result = self._run_keyword_fallback(claim, rl, handoff_approved, started_at)

        self._budget.record(result.cost_usd)
        if self._audit_logger is not None:
            self._audit_logger(result)
        return result

    # ----------------------------------------------------------------- core CoVe

    def _run_cove(
        self,
        claim: str,
        context: dict[str, Any],
        risk_level: RiskLevel,
        handoff_approved: bool,
        started_at: float,
    ) -> HallucinationResult:
        if self._primary is None or self._verifier is None: raise RuntimeError("primary/verifier LLM 未注入")  # 5.88.4 修复: assert→if/raise

        total_cost = 0.0

        baseline_answer, verify_questions, step1_cost = self._step1_baseline_plan(claim, context)
        total_cost += step1_cost

        if len(verify_questions) < 3:
            verify_questions = self._ensure_min_questions(claim, verify_questions)

        verify_answers, step2_cost = self._step2_verify(verify_questions)
        total_cost += step2_cost

        inconsistency_score, evidence = self._step3_cross_check(baseline_answer, verify_answers)

        corrected: str | None = None
        requires_human = False
        final_check_confidence: float | None = None

        ok_upper, bad_lower = _THRESHOLDS[risk_level]
        is_hallu_pre = inconsistency_score > bad_lower
        is_midband = ok_upper < inconsistency_score <= bad_lower

        if is_midband and risk_level is RiskLevel.H:
            requires_human = True
        elif (is_midband and risk_level is RiskLevel.M) or (is_hallu_pre and risk_level is RiskLevel.H):
            corrected, final_check_confidence, step4_cost = self._step4_final_check(baseline_answer, evidence)
            total_cost += step4_cost

        # keyword 规则叠加一次，产出 evidence 但不改 inconsistency_score 除非已判幻觉
        kw_evidence = self._collect_keyword_evidence(claim, handoff_approved)
        if kw_evidence:
            evidence = evidence + kw_evidence
            inconsistency_score = max(inconsistency_score, 0.55)

        is_hallucination = inconsistency_score > bad_lower
        confidence = max(0.0, 1.0 - inconsistency_score)
        if final_check_confidence is not None:
            confidence = max(confidence, final_check_confidence * 0.85)

        if risk_level is RiskLevel.H and is_hallucination:
            requires_human = True

        latency_ms = int((time.perf_counter() - started_at) * 1000)

        return HallucinationResult(
            claim=claim,
            is_hallucination=is_hallucination,
            confidence=min(1.0, confidence),
            risk_level=risk_level.value,
            inconsistency_score=min(1.0, inconsistency_score),
            verify_questions=verify_questions,
            verify_answers=verify_answers,
            evidence=evidence,
            requires_human=requires_human,
            execution_model=self._execution_model_name,
            verifier_model=self._verifier_model_name,
            corrected_answer=corrected,
            latency_ms=latency_ms,
            cost_usd=round(total_cost, 6),
            fallback_used=None,
            triggered=True,
        )

    def _step1_baseline_plan(self, claim: str, context: dict[str, Any]) -> tuple[str, list[str], float]:
        """Step 1：Baseline 回答 + N 条 verify_questions（合并单次调用）。"""
        if self._primary is None: raise RuntimeError("primary LLM 未注入")  # 5.88.4 修复: assert→if/raise
        prompt = self._build_step1_prompt(claim, context)
        result = self._primary(prompt, purpose="cove_step1_baseline_plan")
        if not result.success:
            raise CoVeStepError(f"step1 失败: {result.error}")
        if result.cost_usd > self._per_call_max_usd * 2:
            raise CoVeStepError(f"step1 成本 {result.cost_usd} 超过硬上限")
        try:
            payload = json.loads(result.content)
        except json.JSONDecodeError as exc:
            raise CoVeStepError(f"step1 JSON 解析失败: {exc}") from exc
        baseline = str(payload.get("baseline_answer", "")).strip()
        raw_questions = payload.get("verify_questions", [])
        if not isinstance(raw_questions, list):
            raise CoVeStepError("step1 verify_questions 非列表")
        questions = [str(q).strip() for q in raw_questions if str(q).strip()][:5]
        return baseline, questions, result.cost_usd

    def _step2_verify(self, verify_questions: list[str]) -> tuple[list[dict[str, Any]], float]:
        """Step 2：异构模型独立作答（不看 baseline，防止 prime）。"""
        if self._verifier is None: raise RuntimeError("verifier LLM 未注入")  # 5.88.4 修复: assert→if/raise
        prompt = self._build_step2_prompt(verify_questions)
        result = self._verifier(prompt, purpose="cove_step2_verify")
        if not result.success:
            raise CoVeStepError(f"step2 失败: {result.error}")
        answers: list[dict[str, Any]] = []
        try:
            parsed = json.loads(result.content)
            if isinstance(parsed, list):
                for idx, item in enumerate(parsed):
                    if isinstance(item, dict):
                        answers.append(
                            {
                                "question": str(
                                    item.get("question", verify_questions[idx] if idx < len(verify_questions) else "")
                                ),
                                "answer": str(item.get("answer", "")),
                                "confidence_self": float(item.get("confidence_self", 0.5)),
                            }
                        )
        except (json.JSONDecodeError, ValueError):
            for idx, line in enumerate(result.content.splitlines()):
                if not line.strip():
                    continue
                answers.append(
                    {
                        "question": verify_questions[idx] if idx < len(verify_questions) else "",
                        "answer": line.strip(),
                        "confidence_self": 0.5,
                    }
                )
        return answers, result.cost_usd

    def _step3_cross_check(
        self,
        baseline_answer: str,
        verify_answers: list[dict[str, Any]],
    ) -> tuple[float, list[str]]:
        """Step 3：本地一致性打分（精确匹配 / 语义 / 矛盾）。"""
        if not verify_answers:
            return 0.0, ["step3: no verify answers"]
        inconsistent = 0
        evidence: list[str] = []
        baseline_lower = baseline_answer.lower()
        for item in verify_answers:
            answer = str(item.get("answer", ""))
            if not answer:
                inconsistent += 1
                evidence.append(f"empty_answer_for: {item.get('question')}")
                continue
            answer_lower = answer.lower()
            if answer_lower in baseline_lower or baseline_lower in answer_lower:
                continue
            if _contains_negation(answer) and not _contains_negation(baseline_answer):
                inconsistent += 1
                evidence.append(f"negation_conflict: {item.get('question')}")
                continue
            overlap = _token_overlap(baseline_answer, answer)
            if overlap < 0.30:
                inconsistent += 1
                evidence.append(f"semantic_drift(q='{item.get('question')}'): overlap={overlap:.2f}")
        score = inconsistent / max(1, len(verify_answers))
        return score, evidence

    def _step4_final_check(self, baseline_answer: str, inconsistencies: list[str]) -> tuple[str, float, float]:
        """Step 4：仅 H 级触发；主模型修正 baseline。"""
        if self._primary is None: raise RuntimeError("primary LLM 未注入")  # 5.88.4 修复: assert→if/raise
        prompt = (
            "请基于以下不一致点修正原回答，保持简洁：\n"
            f"原回答：{baseline_answer}\n"
            f"不一致：{inconsistencies}\n"
            '输出 JSON：{"corrected": "...", "confidence": 0.0-1.0}'
        )
        result = self._primary(prompt, purpose="cove_step4_final_check")
        if not result.success:
            raise CoVeStepError(f"step4 失败: {result.error}")
        try:
            payload = json.loads(result.content)
            corrected = str(payload.get("corrected", baseline_answer))
            confidence = float(payload.get("confidence", 0.5))
        except (json.JSONDecodeError, ValueError):
            corrected, confidence = result.content.strip(), 0.5
        return corrected, max(0.0, min(1.0, confidence)), result.cost_usd

    # ----------------------------------------------------------------- fallbacks

    def _run_single_model_lite(
        self,
        claim: str,
        risk_level: RiskLevel,
        handoff_approved: bool,
        started_at: float,
    ) -> HallucinationResult:
        """单模型降级（仅一方可达）：keyword 规则 + 固定 confidence=0.5。"""
        kw_evidence = self._collect_keyword_evidence(claim, handoff_approved)
        inconsistency = 0.55 if kw_evidence else 0.30
        is_hallu = bool(kw_evidence) and risk_level is not RiskLevel.L
        requires_human = risk_level is RiskLevel.H
        latency_ms = int((time.perf_counter() - started_at) * 1000)
        return HallucinationResult(
            claim=claim,
            is_hallucination=is_hallu,
            confidence=0.5,
            risk_level=risk_level.value,
            inconsistency_score=inconsistency,
            verify_questions=[],
            verify_answers=[],
            evidence=kw_evidence or ["single_model_fallback"],
            requires_human=requires_human,
            execution_model=self._execution_model_name if self._primary else "",
            verifier_model=self._verifier_model_name if self._verifier else "",
            corrected_answer=None,
            latency_ms=latency_ms,
            cost_usd=0.0,
            fallback_used=FallbackMode.SINGLE_MODEL.value,
            triggered=True,
        )

    def _run_keyword_fallback(
        self,
        claim: str,
        risk_level: RiskLevel,
        handoff_approved: bool,
        started_at: float,
    ) -> HallucinationResult:
        """keyword 规则兜底（两模型都不可达）。"""
        kw_evidence = self._collect_keyword_evidence(claim, handoff_approved)
        is_hallu = bool(kw_evidence)
        inconsistency = 0.60 if is_hallu else 0.0
        confidence = 0.4 if is_hallu else 0.7
        requires_human = is_hallu and risk_level is RiskLevel.H
        latency_ms = int((time.perf_counter() - started_at) * 1000)
        return HallucinationResult(
            claim=claim,
            is_hallucination=is_hallu,
            confidence=confidence,
            risk_level=risk_level.value,
            inconsistency_score=inconsistency,
            verify_questions=[],
            verify_answers=[],
            evidence=kw_evidence or ["keyword_fallback: no rule hit"],
            requires_human=requires_human,
            execution_model="",
            verifier_model="",
            corrected_answer=None,
            latency_ms=latency_ms,
            cost_usd=0.0,
            fallback_used=FallbackMode.KEYWORD.value,
            triggered=True,
        )

    def _skip_result(
        self,
        claim: str,
        risk_level: RiskLevel,
        *,
        reason: str,
        started_at: float,
    ) -> HallucinationResult:
        """L3 黑名单 / 预算跳过时返回的占位结果。"""
        latency_ms = int((time.perf_counter() - started_at) * 1000)
        return HallucinationResult(
            claim=claim,
            is_hallucination=False,
            confidence=1.0 if reason == "L3_BLACKLIST" else 0.5,
            risk_level=risk_level.value,
            inconsistency_score=0.0,
            verify_questions=[],
            verify_answers=[],
            evidence=[f"skipped: {reason}"],
            requires_human=False,
            execution_model="",
            verifier_model="",
            corrected_answer=None,
            latency_ms=latency_ms,
            cost_usd=0.0,
            fallback_used=None if reason == "L3_BLACKLIST" else reason,
            triggered=False,
        )

    # ----------------------------------------------------------------- helpers

    def _collect_keyword_evidence(self, claim: str, handoff_approved: bool) -> list[str]:
        evidence: list[str] = []
        evidence.extend(_numeric_out_of_range(claim))
        evidence.extend(_missing_files(claim, self._repo_root))
        evidence.extend(_suspect_citations(claim))
        evidence.extend(_frozen_asset_mutation(claim, handoff_approved))
        return evidence

    def _ensure_min_questions(self, claim: str, existing: list[str]) -> list[str]:
        """Step 1 产出少于 3 条时，追加模板问题至 3 条。"""
        templates = [
            f"此 claim 中引用的事实在仓库/知识库中是否可被验证？原 claim：{claim[:120]}",
            "此 claim 中的数值/参数是否在合理范围内？",
            "此 claim 中引用的文件 / decision record / 任务 ID 是否真实存在？",
        ]
        merged = list(existing)
        for tpl in templates:
            if len(merged) >= 3:
                break
            if tpl not in merged:
                merged.append(tpl)
        return merged[:5]

    @staticmethod
    def _build_step1_prompt(claim: str, context: dict[str, Any]) -> str:
        ctx_json = json.dumps(context, ensure_ascii=False)
        return (
            "你是 ZephyrAlpha 的验证前置代理。针对下列 claim：\n"
            f"{claim}\n\n上下文：\n{ctx_json}\n\n"
            "请输出：\n"
            "1. baseline_answer：你认为最可能正确的回答（不超过 200 字）\n"
            "2. verify_questions：将 baseline_answer 拆成 3~5 条可独立验证的事实型问题\n\n"
            '输出 JSON：{"baseline_answer": "...", "verify_questions": ["...", "..."]}'
        )

    @staticmethod
    def _build_step2_prompt(verify_questions: list[str]) -> str:
        listing = "\n".join(f"- {q}" for q in verify_questions)
        return (
            "请对以下每条问题独立作答，仅基于你的知识，不要引用任何外部 baseline：\n"
            f"{listing}\n\n"
            '输出 JSON 列表：[{"question":"...","answer":"...","confidence_self":0.0-1.0}]'
        )

    @staticmethod
    def claim_hash(claim: str) -> str:
        """暴露 claim 指纹，便于外部审计日志复用。"""
        return _hash_claim(claim)


# ---------------------------------------------------------------------------
# 便捷工厂：当 BudgetState 需要历史持久化时使用（非本 Task 范围）
# ---------------------------------------------------------------------------


def build_detector_with_defaults(
    *,
    primary_caller: ModelCaller | None = None,
    verifier_caller: ModelCaller | None = None,
    repo_root: Path | None = None,
) -> HallucinationDetector:
    """
    便捷构造：使用默认预算 / 模型名，主要用于 beta 联调阶段。
    单元测试应直接使用 ``HallucinationDetector(...)`` 以便显式注入参数。
    """
    return HallucinationDetector(
        primary_caller=primary_caller,
        verifier_caller=verifier_caller,
        repo_root=repo_root,
    )
