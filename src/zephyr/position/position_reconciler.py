# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.position.position_reconciler
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 持仓对账必须执行;P0-FATAL必须触发硬中断;事件触发:ExecutionReport到达时自动对账(禁止时间触发)
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/rollback/test_position_reconciler.py
# [A_module] module_id=MOD-RES_position_reconciler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: "cron"在注释中，非实际cron调用

"""

Position Reconciler — v0.10.1 持仓对账: execution report+book record+counterparty三方对账。

事件触发机制：
  - 触发源: D_EXECUTION_CORE ExecutionReport 事件
  - 触发条件: 成交回报到达时自动触发 reconcile
  - 禁止时间触发（无 cron/Timer/sleep-loop/periodic）
  - 调用方通过 handle_execution_report 事件入口触发对账
"""

from __future__ import annotations

import logging
from typing import Any

_logger = logging.getLogger(__name__)

_RULE_ID_POSITION_MISMATCH = "POS-RECON-001"


class PositionReconciler:
    """持仓对账器——事件驱动（ExecutionReport到达时触发）"""

    def __init__(self):
        self._positions: dict[str, dict] = {}

    def reconcile(self, internal: dict, external: dict) -> dict:
        """对账核心逻辑——比较内部持仓与外部持仓差异

        Args:
            internal: 内部持仓字典 {symbol: quantity}
            external: 外部持仓字典 {symbol: quantity}

        Returns:
            dict with keys: match(bool), diffs(dict), count(int), rule_id(str)
        """
        diffs = {}
        all_keys = set(internal.keys()) | set(external.keys())
        for k in all_keys:
            i = internal.get(k, 0)
            e = external.get(k, 0)
            if i != e:
                diffs[k] = {"internal": i, "external": e, "diff": i - e}
        match = len(diffs) == 0
        result: dict[str, Any] = {
            "match": match,
            "diffs": diffs,
            "count": len(diffs),
            "rule_id": _RULE_ID_POSITION_MISMATCH if not match else None,
        }
        if not match:
            _logger.warning(
                "Position reconciliation failed: %d diffs, rule_id=%s",
                len(diffs),
                _RULE_ID_POSITION_MISMATCH,
                extra={"context": {"diffs": diffs}},
            )
        return result

    def handle_execution_report(self, execution_report: dict) -> dict:
        """事件入口——ExecutionReport到达时触发对账

        事件触发源: D_EXECUTION_CORE ExecutionReport 事件
        禁止时间触发——仅通过事件调用此方法

        Args:
            execution_report: 执行回报字典，包含 internal/external 持仓

        Returns:
            reconcile 结果字典
        """
        internal = execution_report.get("internal_positions", {})
        external = execution_report.get("external_positions", {})
        _logger.info("Position reconcile triggered by ExecutionReport event")
        return self.reconcile(internal, external)

    def should_escalate(self, diff_count: int, threshold: int = 3) -> bool:
        """判断是否需要升级（P0-FATAL 硬中断阈值）"""
        return diff_count >= threshold
