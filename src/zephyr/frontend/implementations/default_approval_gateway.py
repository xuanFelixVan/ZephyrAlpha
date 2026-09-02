# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md | §4.1
# [MODULE] zephyr.frontend.implementations.default_approval_gateway
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.frontend.interface_base; zephyr.shared.foundation.errors
# [CONSUMERS] D_PORTFOLIO_CORE(风控硬限触达人工审批) ; D_EXECUTION_CORE(关键决策审批) ; 策略工厂(B-007新策略上线审批)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 仅pending单可decide(重复decide=False); 过期单不可批(fail-closed,自动转expired不再入pending); DELEGATE/ESCALATE为非终态(保持pending); APPROVE/REJECT为终态(移出pending); 全部decide动作落decision_log(B-016审计友好); 重复request_id/空action→InvalidApprovalRequestError
# [MODIFY-GUARD] docs/03_modules/_domain_frontend/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidApprovalRequestError
# [TESTS] tests/frontend/test_default_approval_gateway.py
# [A_module] module_id=MOD-L08-001 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""Default Approval Gateway — 默认审批网关 (MOD-L08-001 步骤2, B-007 审批载体)

ApprovalGatewayBase 的具体实现（蓝图 §4.1 / §16 步骤2：
submit 返回 request_id，decide 返回 bool，pending 返回 list）。

B-007 语义落地：禁止 AI 在无人工审批的情况下上线新策略模块——
本网关是"人工审批"动作的载体：AI/策略工厂 submit，人类经 Dashboard decide。

终态语义：
  - APPROVE / REJECT → 终态（移出 pending，落 decision_log）
  - DELEGATE / ESCALATE → 非终态（保持 pending，落 decision_log 留痕）
  - 过期单（expires_at < now）→ fail-closed：不可批，自动转 expired 出 pending
线程安全：内部锁保护 pending 存储；时钟可注入（clock 协议）保证判定确定性。
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final

from zephyr.frontend.interface_base import (
    ApprovalAction,
    ApprovalGatewayBase,
    ApprovalRequest,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "ApprovalDecisionRecord",
    "DefaultApprovalGateway",
    "InvalidApprovalRequestError",
]

#: 终态动作（移出 pending）
_TERMINAL_ACTIONS: Final = frozenset({ApprovalAction.APPROVE, ApprovalAction.REJECT})


class InvalidApprovalRequestError(ZephyrBaseError):
    """审批请求非法（重复 request_id / 空 action 等）。"""

    error_code = "ZA-FE-0003"


@dataclass(frozen=True)
class ApprovalDecisionRecord:
    """审批决策留痕（B-016 审计友好）。"""

    request_id: str
    action: ApprovalAction
    comment: str
    decided_at: datetime
    terminal: bool


class DefaultApprovalGateway(ApprovalGatewayBase):
    """默认人工审批网关（内存态 + 决策留痕；时钟可注入）。

    Args:
        clock: 时钟协议（默认 datetime.now(UTC)）；测试注入固定时钟保证确定性。
    """

    def __init__(self, clock: Callable[[], datetime] | None = None) -> None:
        self._clock = clock or (lambda: datetime.now(UTC))
        self._lock = threading.Lock()
        self._pending: dict[str, ApprovalRequest] = {}
        self._decision_log: list[ApprovalDecisionRecord] = []

    def submit(self, request: ApprovalRequest) -> str:
        """提交审批请求，返回 request_id。

        Raises:
            InvalidApprovalRequestError: request_id 重复 / action 为空。
        """
        if not request.action.strip():
            raise InvalidApprovalRequestError(
                "审批动作不允许为空",
                details={"request_id": request.request_id},
            )
        with self._lock:
            if request.request_id in self._pending:
                raise InvalidApprovalRequestError(
                    f"审批单号重复: {request.request_id}",
                    details={"request_id": request.request_id},
                )
            self._pending[request.request_id] = request
        _logger.info(
            "APPROVAL_SUBMITTED request=%s action=%s requester=%s",
            request.request_id,
            request.action,
            request.requester,
        )
        return request.request_id

    def decide(self, request_id: str, action: ApprovalAction, comment: str = "") -> bool:
        """执行审批决策。仅 pending 且未过期单可决策；返回是否受理。"""
        with self._lock:
            request = self._pending.get(request_id)
            if request is None:
                return False
            now = self._clock()
            if request.expires_at is not None and request.expires_at < now:
                # fail-closed：过期即不可批，自动转 expired 出 pending
                del self._pending[request_id]
                self._append_log(
                    ApprovalDecisionRecord(
                        request_id=request_id,
                        action=action,
                        comment=f"expired_before_decision;{comment}",
                        decided_at=now,
                        terminal=True,
                    )
                )
                _logger.warning(
                    "APPROVAL_EXPIRED request=%s expires_at=%s",
                    request_id,
                    request.expires_at,
                )
                return False
            terminal = action in _TERMINAL_ACTIONS
            if terminal:
                del self._pending[request_id]
            self._append_log(
                ApprovalDecisionRecord(
                    request_id=request_id,
                    action=action,
                    comment=comment,
                    decided_at=now,
                    terminal=terminal,
                )
            )
        _logger.info(
            "APPROVAL_DECIDED request=%s action=%s terminal=%s",
            request_id,
            action,
            terminal,
        )
        return True

    def pending(self) -> list[ApprovalRequest]:
        """返回所有待审批请求（先惰性清理过期单）。"""
        with self._lock:
            now = self._clock()
            expired_ids = [
                rid for rid, req in self._pending.items() if req.expires_at is not None and req.expires_at < now
            ]
            for rid in expired_ids:
                del self._pending[rid]
            return list(self._pending.values())

    def decision_log(self) -> tuple[ApprovalDecisionRecord, ...]:
        """决策留痕（tuple 拷贝，外部不可变内部状态）。"""
        with self._lock:
            return tuple(self._decision_log)

    def _append_log(self, record: ApprovalDecisionRecord) -> None:
        self._decision_log.append(record)
