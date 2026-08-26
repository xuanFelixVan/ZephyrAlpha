# [BLUEPRINT] MOD-GOV-057 | docs/03_modules/_domain_gov_rule/standards_manager/blueprint.md
# [MODULE] zephyr.gov_rule.standards_manager
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES] 无（目录/审批队列纯内存；script_registrar/clock 全注入）
# [CONSUMERS] 运行时装配批（硬边界目录装配 / gov_enforcement 校验脚本挂接 / 人工审批台）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 四要素闭合(编号/约束语句/校验脚本锚点/违反响应词表)+元标准元数据; 边界变更仅经审批队列(ADD/UPDATE/RETIRE 词表闭合)无旁路; 同 change_id 一次性裁决不重复; 批准才落目录且先触发脚本注册回调(失败不落目录); 目录按编号排序确定性; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_gov_rule/standards_manager/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] StandardsManagerError(占位 ZA-GOVR-UNREGISTERED-STANDARDS-MANAGER)——四要素缺失/非法词表/未知边界/变更冲突/重复裁决/非法裁决/脚本注册失败时抛
# [TESTS] tests/gov_rule/test_standards_manager.py
# [A_module] module_id=MOD-GOV-057 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""StandardsManager — 硬边界标准管理器（MOD-GOV-057）。

B1-00289（AUD-DRAFT-001-DIGEST P2 波 P2-W12，CAND-PC-002，C2 D-GOV-06）：
硬边界目录（**编号 / 约束语句 / 校验脚本锚点 / 违反响应**四要素 + 元标准
元数据字段）+ 与 gov_enforcement 门禁挂接（**校验脚本注册回调**）+ 边界变
更须人工门禁（**审批队列硬约束**）。canonical 承接 PC-003 归并（PS-STD/
PS-REG 元标准语义并入元数据字段）。

查重分工（蓝图 §0）：rule_patterns=治理正则 SSoT（本件=边界目录与变更审
批流，不定义正则）；gov_enforcement 门禁族=校验执行（本件仅经注入回调登
记脚本锚点，不执行校验）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "ApprovalDecision",
    "BoundaryChangeRequest",
    "ChangeKind",
    "ChangeRecord",
    "ChangeStatus",
    "HardBoundary",
    "StandardsManager",
    "StandardsManagerError",
    "ViolationResponse",
]


class StandardsManagerError(Exception):
    """硬边界标准管理输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-GOVR-UNREGISTERED-STANDARDS-MANAGER。
    """


class ViolationResponse(str, Enum):
    """违反响应词表（闭合）。"""

    BLOCK = "block"
    WARN = "warn"
    ESCALATE = "escalate"


class ChangeKind(str, Enum):
    """边界变更类别词表（闭合）。"""

    ADD = "add"
    UPDATE = "update"
    RETIRE = "retire"


class ChangeStatus(str, Enum):
    """变更单状态词表（闭合）。"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class HardBoundary:
    """硬边界目录条目（frozen）。

    四要素：boundary_id（编号）/ constraint_text（约束语句）/
    script_anchor（校验脚本锚点）/ violation_response（违反响应）；
    meta 为元标准元数据（如 standard_id/title/owner/version，str→str）。
    """

    boundary_id: str
    constraint_text: str
    script_anchor: str
    violation_response: ViolationResponse
    meta: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class BoundaryChangeRequest:
    """边界变更申请（frozen；一律入人工审批队列，无旁路）。"""

    change_id: str
    kind: ChangeKind
    boundary_id: str
    new_boundary: HardBoundary | None
    reason: str
    requested_by: str


@dataclass(frozen=True)
class ApprovalDecision:
    """人工审批裁决（frozen；decided_at 由管理器裁决时落钟）。"""

    change_id: str
    approved: bool
    decided_by: str
    note: str = ""


@dataclass(frozen=True)
class ChangeRecord:
    """变更单全生命周期留痕（frozen）。"""

    change_id: str
    kind: ChangeKind
    boundary_id: str
    status: ChangeStatus
    requested_by: str
    reason: str
    proposed_at: datetime.datetime
    decided_at: datetime.datetime | None
    decided_by: str | None
    note: str | None


def _validate_boundary(boundary: HardBoundary) -> None:
    """四要素 + 元数据校验（Fail-Closed）。"""
    if not isinstance(boundary, HardBoundary):
        raise StandardsManagerError(f"非法 boundary 类型: {type(boundary).__name__}")
    if not boundary.boundary_id or not isinstance(boundary.boundary_id, str):
        raise StandardsManagerError(f"boundary_id（编号）非法: {boundary.boundary_id!r}")
    if not boundary.constraint_text or not isinstance(boundary.constraint_text, str):
        raise StandardsManagerError(f"constraint_text（约束语句）非法: {boundary.boundary_id!r}")
    if not boundary.script_anchor or not isinstance(boundary.script_anchor, str):
        raise StandardsManagerError(f"script_anchor（校验脚本锚点）非法: {boundary.boundary_id!r}")
    if not isinstance(boundary.violation_response, ViolationResponse):
        raise StandardsManagerError(f"violation_response（违反响应）非法: {boundary.violation_response!r}")
    if not isinstance(boundary.meta, Mapping) or any(
        not isinstance(k, str) or not isinstance(v, str) for k, v in boundary.meta.items()
    ):
        raise StandardsManagerError(f"meta（元标准元数据）须为 str→str: {boundary.boundary_id!r}")


class StandardsManager:
    """硬边界标准管理件（目录 + 校验脚本挂接 + 人工审批队列硬约束）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        script_registrar: Callable[[str, str], None] | None = None,
        initial_boundaries: Iterable[HardBoundary] = (),
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._script_registrar = script_registrar
        self._catalog: dict[str, HardBoundary] = {}
        self._requests: dict[str, BoundaryChangeRequest] = {}
        self._proposed_at: dict[str, datetime.datetime] = {}
        self._decisions: dict[str, ApprovalDecision] = {}
        self._decided_at: dict[str, datetime.datetime] = {}
        self._order: list[str] = []
        for boundary in initial_boundaries:
            _validate_boundary(boundary)
            if boundary.boundary_id in self._catalog:
                raise StandardsManagerError(f"种子目录编号重复: {boundary.boundary_id!r}")
            self._register_script(boundary.boundary_id, boundary.script_anchor)
            self._catalog[boundary.boundary_id] = boundary

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _register_script(self, boundary_id: str, script_anchor: str) -> None:
        """gov_enforcement 门禁挂接：校验脚本注册回调（失败 Fail-Closed）。"""
        if self._script_registrar is None:
            return
        try:
            self._script_registrar(boundary_id, script_anchor)
        except Exception as exc:  # noqa: BLE001 — 挂接失败不落目录（INVARIANTS）
            raise StandardsManagerError(f"script_registrar 注册失败: {boundary_id!r}: {exc!r}") from exc

    def _validate_request(self, request: BoundaryChangeRequest) -> None:
        if not isinstance(request, BoundaryChangeRequest):
            raise StandardsManagerError(f"非法 request 类型: {type(request).__name__}")
        if not request.change_id or not isinstance(request.change_id, str):
            raise StandardsManagerError(f"change_id 非法: {request.change_id!r}")
        if not isinstance(request.kind, ChangeKind):
            raise StandardsManagerError(f"kind 非法: {request.kind!r}")
        if not request.boundary_id or not isinstance(request.boundary_id, str):
            raise StandardsManagerError(f"boundary_id 非法: {request.boundary_id!r}")
        if not request.requested_by or not isinstance(request.requested_by, str):
            raise StandardsManagerError(f"requested_by 非法: {request.requested_by!r}")
        if not isinstance(request.reason, str):
            raise StandardsManagerError("reason 须为 str")

    def _record(self, request: BoundaryChangeRequest) -> ChangeRecord:
        decision = self._decisions.get(request.change_id)
        if decision is None:
            status = ChangeStatus.PENDING
            decided_at = decided_by = note = None
        else:
            status = ChangeStatus.APPROVED if decision.approved else ChangeStatus.REJECTED
            decided_at = self._decided_at[request.change_id]
            decided_by = decision.decided_by
            note = decision.note
        return ChangeRecord(
            change_id=request.change_id,
            kind=request.kind,
            boundary_id=request.boundary_id,
            status=status,
            requested_by=request.requested_by,
            reason=request.reason,
            proposed_at=self._proposed_at[request.change_id],
            decided_at=decided_at,
            decided_by=decided_by,
            note=note,
        )

    # ── 变更申请（入人工审批队列） ─────────────────────────────────────────

    def propose_change(self, request: BoundaryChangeRequest) -> str:
        """提交边界变更：校验 → 入审批队列（PENDING），返回 change_id。"""
        self._validate_request(request)
        if request.change_id in self._requests:
            raise StandardsManagerError(f"change_id 重复: {request.change_id!r}")
        exists = request.boundary_id in self._catalog
        if request.kind is ChangeKind.ADD:
            if exists:
                raise StandardsManagerError(f"ADD 冲突：边界已存在: {request.boundary_id!r}")
            if request.new_boundary is None:
                raise StandardsManagerError("ADD 须携带 new_boundary")
        elif request.kind is ChangeKind.UPDATE:
            if not exists:
                raise StandardsManagerError(f"UPDATE 冲突：未知边界: {request.boundary_id!r}")
            if request.new_boundary is None:
                raise StandardsManagerError("UPDATE 须携带 new_boundary")
        else:  # RETIRE
            if not exists:
                raise StandardsManagerError(f"RETIRE 冲突：未知边界: {request.boundary_id!r}")
            if request.new_boundary is not None:
                raise StandardsManagerError("RETIRE 不得携带 new_boundary")
        if request.new_boundary is not None:
            _validate_boundary(request.new_boundary)
            if request.new_boundary.boundary_id != request.boundary_id:
                raise StandardsManagerError(
                    f"new_boundary 编号与变更对象不符: {request.new_boundary.boundary_id!r} != {request.boundary_id!r}"
                )
        self._requests[request.change_id] = request
        self._proposed_at[request.change_id] = self._clock()
        self._order.append(request.change_id)
        _log.info("边界变更入审批队列: %s (%s %s)", request.change_id, request.kind.value, request.boundary_id)
        return request.change_id

    # ── 人工裁决（一次性，批准才落目录） ───────────────────────────────────

    def decide_change(self, decision: ApprovalDecision) -> ChangeRecord:
        """裁决变更单：批准→先注册脚本锚点再落目录；拒绝→仅留痕。"""
        if not isinstance(decision, ApprovalDecision):
            raise StandardsManagerError(f"非法 decision 类型: {type(decision).__name__}")
        request = self._requests.get(decision.change_id)
        if request is None:
            raise StandardsManagerError(f"未知 change_id: {decision.change_id!r}")
        if decision.change_id in self._decisions:
            raise StandardsManagerError(f"变更单已裁决（禁止重复裁决）: {decision.change_id!r}")
        if not isinstance(decision.approved, bool):
            raise StandardsManagerError(f"approved 须为 bool: {decision.approved!r}")
        if not decision.decided_by or not isinstance(decision.decided_by, str):
            raise StandardsManagerError(f"decided_by 非法: {decision.decided_by!r}")
        if not isinstance(decision.note, str):
            raise StandardsManagerError("note 须为 str")
        if decision.approved:
            if request.new_boundary is not None:
                # 先挂接 gov_enforcement 校验脚本，成功才落目录（Fail-Closed）
                self._register_script(request.boundary_id, request.new_boundary.script_anchor)
                self._catalog[request.boundary_id] = request.new_boundary
            else:  # RETIRE
                del self._catalog[request.boundary_id]
        self._decisions[decision.change_id] = decision
        self._decided_at[decision.change_id] = self._clock()
        record = self._record(request)
        _log.info("边界变更裁决: %s -> %s", decision.change_id, record.status.value)
        return record

    # ── 查询 ─────────────────────────────────────────────────────────────

    def get(self, boundary_id: str) -> HardBoundary:
        """按编号取边界（未知 Fail-Closed）。"""
        if not boundary_id:
            raise StandardsManagerError("boundary_id 为空")
        boundary = self._catalog.get(boundary_id)
        if boundary is None:
            raise StandardsManagerError(f"未知边界: {boundary_id!r}")
        return boundary

    def catalog(self) -> tuple[HardBoundary, ...]:
        """硬边界目录（按编号排序，确定性）。"""
        return tuple(self._catalog[k] for k in sorted(self._catalog))

    def pending(self) -> tuple[ChangeRecord, ...]:
        """待裁决变更单（按 (proposed_at, change_id) 排序，确定性）。"""
        pending_ids = [cid for cid in self._order if cid not in self._decisions]
        pending_ids.sort(key=lambda cid: (self._proposed_at[cid], cid))
        return tuple(self._record(self._requests[cid]) for cid in pending_ids)

    def history(self) -> tuple[ChangeRecord, ...]:
        """全部变更单留痕（按申请序，确定性）。"""
        return tuple(self._record(self._requests[cid]) for cid in self._order)

    def status_of(self, change_id: str) -> ChangeStatus:
        """单变更单状态（未知 Fail-Closed）。"""
        if not change_id:
            raise StandardsManagerError("change_id 为空")
        if change_id not in self._requests:
            raise StandardsManagerError(f"未知 change_id: {change_id!r}")
        decision = self._decisions.get(change_id)
        if decision is None:
            return ChangeStatus.PENDING
        return ChangeStatus.APPROVED if decision.approved else ChangeStatus.REJECTED
