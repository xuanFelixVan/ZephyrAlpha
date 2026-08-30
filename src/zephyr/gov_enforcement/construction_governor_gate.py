# [BLUEPRINT] MOD-GOV-056 | docs/03_modules/_domain_gov_enforcement/construction_governor_gate/blueprint.md
# [MODULE] zephyr.gov_enforcement.construction_governor_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] 无（协议核心纯内存；approval_sink/record_sink/clock 全注入；指纹仅用 stdlib hashlib）
# [CONSUMERS] 运行时装配批（施工产物门装配 / GatePipeline 挂接 / 升级审批回调与判定留痕路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 公式指纹登记后方可核验(未登记 Fail-Closed); 指纹漂移必拒绝(REJECT 优先于升级); 影响面超阈值未获批必 ESCALATE 不 PASS; 截断段=超出阈值尾部(获批则放行全量); 判定逐条留痕且查询确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_gov_enforcement/construction_governor_gate/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ConstructionGateError(占位 ZA-GOVE-UNREGISTERED-CONSTRUCTION-GATE)——空id/空公式/非法阈值/重复登记/未知产物/非法product/审批回调异常或返回非bool时抛
# [TESTS] tests/gov_enforcement/test_construction_governor_gate.py
# [A_module] module_id=MOD-GOV-056 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
ConstructionGovernorGate — AI 施工门禁器（MOD-GOV-056）。

B10-02423（AUD-DRAFT-001-DIGEST P2 波 P2-W12，CAND-GOVENFOR-002，A1
D-GOVERNANCE-15）：施工门禁挂 GatePipeline 语义——产物**公式 Hash 校验**
（登记公式指纹 → 产出比对，漂移拒绝）+ **回归截断**（变更影响面超阈值截
断，须升级审批）+ 门禁判定**留痕**。fitness function 思路。

查重分工（蓝图 §0）：commit_gates 包=GitCommitGateway pre-commit 门禁实现
（本件=施工产物公式指纹与影响面门禁，不挂 git hook）；behavioral_admission
=行为准入（本件=产物内容指纹与影响面，零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: construction_governor_gate.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: impact_threshold 参数
#   fields: 参数 impact_threshold（无注解）
#   code: construction_governor_gate.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: approval_sink 参数
#   fields: 参数 approval_sink（无注解）
#   code: construction_governor_gate.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: record_sink 参数
#   fields: 参数 record_sink（无注解）
#   code: construction_governor_gate.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ConstructionGovernorGate
#   name_en: ConstructionGovernorGate
#   intro: AI 施工门禁件（公式指纹校验 + 回归截断升级审批 + 判定留痕）。
#   desc: AI 施工门禁件（公式指纹校验 + 回归截断升级审批 + 判定留痕）。；公共方法（定义序）: register_formula, verify, registrations, verdicts；源码 L163-L311
#   inputs: clock impact_threshold approval_sink record_sink
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: ConstructionGovernorGate
#   downstream: 运行时装配批（施工产物门装配 / GatePipeline 挂接 / 升级审批回调与判定留痕路由）
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

import datetime
import hashlib
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "ArtifactProduct",
    "ConstructionGateError",
    "ConstructionGovernorGate",
    "EscalationRequest",
    "FormulaRegistration",
    "GateDecision",
    "GateVerdict",
]


class ConstructionGateError(Exception):
    """施工门禁输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-GOVE-UNREGISTERED-CONSTRUCTION-GATE。
    """


class GateDecision(str, Enum):
    """门禁判定词表（闭合）。"""

    PASS = "pass"
    REJECT = "reject"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class FormulaRegistration:
    """公式指纹登记条目（frozen；fingerprint=sha256(formula_text) 十六进制）。"""

    artifact_id: str
    fingerprint: str
    registered_at: datetime.datetime


@dataclass(frozen=True)
class ArtifactProduct:
    """施工产物核验请求（frozen）。

    affected_paths：本次变更影响面（路径词元，去重前原样计入影响面大小）。
    """

    artifact_id: str
    produced_text: str
    affected_paths: tuple[str, ...]


@dataclass(frozen=True)
class EscalationRequest:
    """升级审批请求（影响面超阈值时注入 approval_sink 的载荷，frozen）。"""

    artifact_id: str
    impact_size: int
    impact_threshold: int
    truncated_paths: tuple[str, ...]


@dataclass(frozen=True)
class GateVerdict:
    """单次门禁判定留痕（frozen）。

    allowed_paths/truncated_paths：回归截断语义——超阈值未获批时仅阈值内
    头部放行语义（allowed），尾部截断待审批（truncated）；获批或不超阈值
    时 allowed=全量、truncated=空。
    """

    artifact_id: str
    decision: GateDecision
    formula_match: bool
    expected_fingerprint: str
    actual_fingerprint: str
    impact_size: int
    impact_threshold: int
    allowed_paths: tuple[str, ...]
    truncated_paths: tuple[str, ...]
    escalated: bool
    reason: str
    decided_at: datetime.datetime


class ConstructionGovernorGate:
    """AI 施工门禁件（公式指纹校验 + 回归截断升级审批 + 判定留痕）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        impact_threshold: int = 10,
        approval_sink: Callable[[EscalationRequest], bool] | None = None,
        record_sink: Callable[[GateVerdict], None] | None = None,
    ) -> None:
        if not isinstance(impact_threshold, int) or isinstance(impact_threshold, bool):
            raise ConstructionGateError(f"impact_threshold 须为 int: {impact_threshold!r}")
        if impact_threshold < 1:
            raise ConstructionGateError(f"impact_threshold 须 >= 1: {impact_threshold!r}")
        self._clock = clock or datetime.datetime.now
        self._threshold = impact_threshold
        self._approval_sink = approval_sink
        self._record_sink = record_sink
        self._registry: dict[str, FormulaRegistration] = {}
        self._verdicts: list[GateVerdict] = []

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _fingerprint(text: str) -> str:
        """公式/产出文本指纹（sha256 十六进制，确定性）。"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _validate_product(product: ArtifactProduct) -> None:
        if not isinstance(product, ArtifactProduct):
            raise ConstructionGateError(f"非法 product 类型: {type(product).__name__}")
        if not product.artifact_id:
            raise ConstructionGateError("artifact_id 为空")
        if not isinstance(product.produced_text, str):
            raise ConstructionGateError("produced_text 须为 str")
        if not isinstance(product.affected_paths, tuple) or any(not isinstance(p, str) for p in product.affected_paths):
            raise ConstructionGateError("affected_paths 须为 tuple[str, ...]")

    def _request_approval(self, product: ArtifactProduct, impact: int) -> bool:
        if self._approval_sink is None:
            # 升级审批为 human_gated 硬约束：未注入审批回调一律视为未获批
            return False
        request = EscalationRequest(
            artifact_id=product.artifact_id,
            impact_size=impact,
            impact_threshold=self._threshold,
            truncated_paths=product.affected_paths[self._threshold :],
        )
        try:
            approved = self._approval_sink(request)
        except Exception as exc:  # noqa: BLE001 — 审批回调异常按 Fail-Closed 包装
            raise ConstructionGateError(f"approval_sink 调用异常: {exc!r}") from exc
        if not isinstance(approved, bool):
            raise ConstructionGateError(f"approval_sink 须返回 bool: {approved!r}")
        return approved

    def _record(self, verdict: GateVerdict) -> None:
        self._verdicts.append(verdict)
        _log.info("施工门禁判定: %s -> %s (%s)", verdict.artifact_id, verdict.decision.value, verdict.reason)
        if self._record_sink is not None:
            try:
                self._record_sink(verdict)
            except Exception:  # noqa: BLE001 — 留痕路由异常不改写判定（蓝图 §1）
                _log.exception("record_sink 留痕失败")

    # ── 公式登记 ──────────────────────────────────────────────────────────

    def register_formula(self, artifact_id: str, formula_text: str) -> FormulaRegistration:
        """登记产物公式指纹；重复登记 Fail-Closed。"""
        if not artifact_id or not isinstance(artifact_id, str):
            raise ConstructionGateError(f"artifact_id 非法: {artifact_id!r}")
        if not formula_text or not isinstance(formula_text, str):
            raise ConstructionGateError(f"formula_text 非法: {formula_text!r}")
        if artifact_id in self._registry:
            raise ConstructionGateError(f"公式已登记（禁止覆盖）: {artifact_id!r}")
        registration = FormulaRegistration(
            artifact_id=artifact_id,
            fingerprint=self._fingerprint(formula_text),
            registered_at=self._clock(),
        )
        self._registry[artifact_id] = registration
        return registration

    # ── 门禁核验 ──────────────────────────────────────────────────────────

    def verify(self, product: ArtifactProduct) -> GateVerdict:
        """核验施工产物：公式指纹比对 → 影响面阈值/升级审批 → 判定留痕。"""
        self._validate_product(product)
        registration = self._registry.get(product.artifact_id)
        if registration is None:
            raise ConstructionGateError(f"未登记公式指纹: {product.artifact_id!r}")
        actual = self._fingerprint(product.produced_text)
        formula_match = actual == registration.fingerprint
        impact = len(product.affected_paths)
        over = impact > self._threshold
        escalated = False
        allowed = product.affected_paths
        truncated: tuple[str, ...] = ()

        if not formula_match:
            # 公式漂移一票否决，优先于影响面升级（INVARIANTS）
            decision = GateDecision.REJECT
            reason = "公式指纹漂移（产出与登记指纹不符），拒绝"
        elif over:
            escalated = True
            if self._request_approval(product, impact):
                decision = GateDecision.PASS
                reason = f"影响面 {impact} 超阈值 {self._threshold}，经升级审批通过"
            else:
                decision = GateDecision.ESCALATE
                allowed = product.affected_paths[: self._threshold]
                truncated = product.affected_paths[self._threshold :]
                reason = f"影响面 {impact} 超阈值 {self._threshold}，回归截断待升级审批"
        else:
            decision = GateDecision.PASS
            reason = "公式指纹一致且影响面在阈值内"

        verdict = GateVerdict(
            artifact_id=product.artifact_id,
            decision=decision,
            formula_match=formula_match,
            expected_fingerprint=registration.fingerprint,
            actual_fingerprint=actual,
            impact_size=impact,
            impact_threshold=self._threshold,
            allowed_paths=allowed,
            truncated_paths=truncated,
            escalated=escalated,
            reason=reason,
            decided_at=self._clock(),
        )
        self._record(verdict)
        return verdict

    # ── 查询 ─────────────────────────────────────────────────────────────

    def registrations(self) -> tuple[FormulaRegistration, ...]:
        """公式登记条目（按 artifact_id 排序，确定性）。"""
        return tuple(self._registry[k] for k in sorted(self._registry))

    def verdicts(self, artifact_id: str | None = None) -> tuple[GateVerdict, ...]:
        """判定留痕（按判定序；给 artifact_id 则过滤，未知 id 返回空）。"""
        if artifact_id is None:
            return tuple(self._verdicts)
        if not artifact_id:
            raise ConstructionGateError("artifact_id 为空")
        return tuple(v for v in self._verdicts if v.artifact_id == artifact_id)
