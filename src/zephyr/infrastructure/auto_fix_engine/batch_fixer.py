# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.batch_fixer
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] MUST使用ThreadPoolExecutor(max_workers=8);MUST通过冲突解决器
# [MODIFY-GUARD] blueprint.md §3;auto_fix_config.yaml engine.max_concurrent_fixes
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] BatchFixError
# [TESTS] tests/auto-fix-engine/test_batch_fixer.py
# [A_module] module_id=MOD-INF-031 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: max_workers 参数
#   fields: 参数 max_workers（无注解）
#   code: batch_fixer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: fix_budget 参数
#   fields: 参数 fix_budget（无注解）
#   code: batch_fixer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: storm_guard 参数
#   fields: 参数 storm_guard（无注解）
#   code: batch_fixer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: idempotency_guard 参数
#   fields: 参数 idempotency_guard（无注解）
#   code: batch_fixer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① BatchFixer
#   name_en: BatchFixer
#   intro: class BatchFixer 源码 L80-L225
#   desc: 公共方法（定义序）: conflict_resolver, idempotency, storm_guard, budget, max_workers, execute_batch；源码 L80-L225
#   inputs: max_workers fix_budget storm_guard idempotency_guard conflict_resolver
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: BatchFixer
#   downstream: engine.py
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
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from zephyr.infrastructure.auto_fix_engine.fix_budget import FixBudget, FixStormGuard
from zephyr.infrastructure.auto_fix_engine.fix_reliability import ConflictResolver, IdempotencyGuard
from zephyr.infrastructure.auto_fix_engine.models import (
    FixAction,
    FixReport,
    FixStatus,
)

logger = logging.getLogger(__name__)


class BatchFixer:
    def __init__(
        self,
        max_workers: int = 8,
        fix_budget: FixBudget | None = None,
        storm_guard: FixStormGuard | None = None,
        idempotency_guard: IdempotencyGuard | None = None,
        conflict_resolver: ConflictResolver | None = None,
    ) -> None:
        self._max_workers = max_workers
        self._budget = fix_budget or FixBudget()
        self._storm_guard = storm_guard or FixStormGuard()
        self._idempotency = idempotency_guard or IdempotencyGuard()
        self._conflict_resolver = conflict_resolver or ConflictResolver()

    @property
    def conflict_resolver(self):
        """只读：conflict_resolver（Stage 4 公共化）。"""
        return self._conflict_resolver

    @conflict_resolver.setter
    def conflict_resolver(self, value):
        """写入：conflict_resolver（Stage 4 公共化）。"""
        self._conflict_resolver = value

    @property
    def idempotency(self):
        """只读：idempotency（Stage 4 公共化）。"""
        return self._idempotency

    @idempotency.setter
    def idempotency(self, value):
        """写入：idempotency（Stage 4 公共化）。"""
        self._idempotency = value

    @property
    def storm_guard(self):
        """只读：storm_guard（Stage 4 公共化）。"""
        return self._storm_guard

    @storm_guard.setter
    def storm_guard(self, value):
        """写入：storm_guard（Stage 4 公共化）。"""
        self._storm_guard = value

    @property
    def budget(self):
        """只读：budget（Stage 4 公共化）。"""
        return self._budget

    @budget.setter
    def budget(self, value):
        """写入：budget（Stage 4 公共化）。"""
        self._budget = value

    @property
    def max_workers(self):
        """只读：max_workers（Stage 4 公共化）。"""
        return self._max_workers

    @max_workers.setter
    def max_workers(self, value):
        """写入：max_workers（Stage 4 公共化）。"""
        self._max_workers = value

    def execute_batch(
        self,
        actions: list[FixAction],
        fix_fn: Callable[[FixAction], FixAction],
        module_name: str = "",
    ) -> FixReport:
        if not actions:
            return FixReport(budget_remaining=self._budget.get_info())
        storm_ok, storm_reason = self._storm_guard.check()
        if not storm_ok:
            return FixReport(
                total_attempted=len(actions),
                cascade_alerts=[storm_reason],
                budget_remaining=self._budget.get_info(),
            )
        ordered = self._conflict_resolver.resolve(actions)
        results: list[FixAction] = []
        succeeded = 0
        failed = 0
        escalated = 0
        dead_lettered = 0
        cascade_alerts: list[str] = []

        def _process_one(action: FixAction) -> FixAction:
            nonlocal succeeded, failed, escalated, dead_lettered
            idem_ok, idem_reason = self._idempotency.check(action)
            if not idem_ok:
                action.status = FixStatus.CANCELLED
                action.metadata["skip_reason"] = idem_reason
                return action
            budget_decision = self._budget.check(action.level, action.token_cost)
            if not budget_decision.allowed:
                action.status = FixStatus.FAILED
                action.metadata["budget_reason"] = budget_decision.reason
                failed += 1
                return action
            lock = self._conflict_resolver.acquire(action.target)
            with lock:
                try:
                    self._storm_guard.record()
                    result = fix_fn(action)
                    self._budget.consume(action.level, action.token_cost, operation_id=action.action_id)
                    self._idempotency.record(result, result.status.value)
                    if result.status == FixStatus.COMPLETED:
                        succeeded += 1
                    elif result.status == FixStatus.APPROVAL_PENDING:
                        escalated += 1
                    elif result.status == FixStatus.DEAD_LETTER:
                        dead_lettered += 1
                    else:
                        failed += 1
                    return result
                except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                    action.status = FixStatus.FAILED
                    action.metadata["error"] = str(exc)
                    failed += 1
                    return action

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_to_action = {executor.submit(_process_one, action): action for action in ordered}
            for future in as_completed(future_to_action):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                    original = future_to_action[future]
                    original.status = FixStatus.FAILED
                    original.metadata["error"] = str(exc)
                    results.append(original)
                    failed += 1

        return FixReport(
            total_attempted=len(actions),
            succeeded=succeeded,
            failed=failed,
            escalated=escalated,
            dead_lettered=dead_lettered,
            budget_remaining=self._budget.get_info(),
            actions=results,
            cascade_alerts=cascade_alerts,
        )
