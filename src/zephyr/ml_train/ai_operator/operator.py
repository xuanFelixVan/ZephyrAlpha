# [BLUEPRINT] MOD-ML-002 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.ai_operator.operator
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] 无（标准库）
# [CONSUMERS] MOD-ML-001 training_pipeline（运行记录巡检）；MOD-ML-004 gray_release_shadow_deployer（影子部署申请位）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 全操作留痕（含被拒绝的尝试）；online/offline 只产申请记录永不真生效（B-007/B-009 testing 封顶）；批准令牌 scope 必须匹配动作
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] OperatorActionError(ZA-MLT-0005)——令牌无效/scope 不匹配时抛（拒绝同样留痕）
# [TESTS] tests/ml_train/test_ai_operator.py
# [A_module] module_id=MOD-ML-002 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent

"""D_ML_TRAIN — MOD-ML-002 AI 操作员。

模型上线/下线/巡检三操作封装：

- ``request_online`` / ``request_offline``：需合法批准令牌（scope 匹配）；
  **testing 封顶**——即便令牌合法也只产 ``pending_owner_execution`` 申请记录，
  ``effective`` 恒 False，模型上线生效权属 Owner（B-007），参数/模型禁止
  生效实盘（B-009）。
- ``inspect``：健康巡检（免令牌），产指标快照并留痕。
- 全操作（含被拒绝的令牌尝试）按序留痕，``audit_log()`` 返回副本防篡改。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Final

_log = logging.getLogger(__name__)

_OPERATOR: Final[str] = "ai_operator"


class OperatorActionError(Exception):
    """ZA-MLT-0005: AI 操作员动作被拒绝（令牌无效/scope 不匹配）。"""

    error_code = "ZA-MLT-0005"


@dataclass(frozen=True)
class ApprovalToken:
    """批准令牌（B-007 人工闸门载体）。

    Attributes
    ----------
    token_id : 令牌标识（追溯用）。
    approver : 批准人。
    scope : 批准范围（model_online / model_offline / ...）。
    valid : 令牌是否有效（过期/吊销=False）。
    """

    token_id: str
    approver: str
    scope: str
    valid: bool


@dataclass(frozen=True)
class OperatorRecord:
    """操作留痕记录。"""

    action: str  # online / offline / inspect
    model_id: str
    operator: str
    status: str  # pending_owner_execution / rejected / done
    effective: bool  # 是否真生效（testing 封顶恒 False）
    detail: str = ""
    at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AIOperator:
    """AI 操作员（MOD-ML-002）。"""

    def __init__(self) -> None:
        self._log: list[OperatorRecord] = []

    # ── 上线/下线申请（testing 封顶：只记录不生效） ───────────────────

    def request_online(self, model_id: str, token: ApprovalToken) -> OperatorRecord:
        """模型上线申请。令牌合法也只产申请记录，永不真上线。"""
        return self._gated_action("online", model_id, token, required_scope="model_online")

    def request_offline(self, model_id: str, token: ApprovalToken) -> OperatorRecord:
        """模型下线申请。令牌合法也只产申请记录，永不真下线。"""
        return self._gated_action("offline", model_id, token, required_scope="model_offline")

    # ── 巡检（免令牌） ───────────────────────────────────────────────

    def inspect(self, model_id: str, metrics: dict[str, float]) -> dict[str, Any]:
        """健康巡检：产指标快照并留痕。"""
        snap: dict[str, Any] = {
            "model_id": model_id,
            "metrics": dict(metrics),
            "inspected_at": datetime.now(timezone.utc).isoformat(),
        }
        self._log.append(
            OperatorRecord(
                action="inspect",
                model_id=model_id,
                operator=_OPERATOR,
                status="done",
                effective=False,
            )
        )
        _log.info("巡检: %s metrics=%s", model_id, metrics)
        return snap

    # ── 留痕 ─────────────────────────────────────────────────────────

    def audit_log(self) -> list[OperatorRecord]:
        """返回留痕副本（防外部篡改内部日志）。"""
        return list(self._log)

    # ── 内部 ─────────────────────────────────────────────────────────

    def _gated_action(
        self,
        action: str,
        model_id: str,
        token: ApprovalToken,
        required_scope: str,
    ) -> OperatorRecord:
        if not token.valid:
            rec = self._record(action, model_id, "rejected", "令牌无效")
            raise OperatorActionError(f"批准令牌无效（token_id={token.token_id}）") from self._chain(rec)
        if token.scope != required_scope:
            rec = self._record(action, model_id, "rejected", f"scope 不匹配: {token.scope}")
            raise OperatorActionError(
                f"批准令牌 scope 不匹配: 需 {required_scope!r} 实得 {token.scope!r}"
            ) from self._chain(rec)
        rec = self._record(action, model_id, "pending_owner_execution", "申请已留痕，待 Owner 执行")
        _log.info("%s 申请: %s（testing 封顶，不生效）", action, model_id)
        return rec

    def _record(self, action: str, model_id: str, status: str, detail: str) -> OperatorRecord:
        rec = OperatorRecord(
            action=action,
            model_id=model_id,
            operator=_OPERATOR,
            status=status,
            effective=False,  # testing 封顶：任何操作不真生效
            detail=detail,
        )
        self._log.append(rec)
        return rec

    @staticmethod
    def _chain(rec: OperatorRecord) -> Exception:
        """把留痕记录挂到异常 __cause__ 链上（拒绝原因可追溯）。"""
        return OperatorActionError(f"action={rec.action} model={rec.model_id} status={rec.status}")


__all__ = [
    "AIOperator",
    "ApprovalToken",
    "OperatorActionError",
    "OperatorRecord",
]
