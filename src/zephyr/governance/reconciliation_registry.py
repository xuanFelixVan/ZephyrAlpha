# [BLUEPRINT] MOD-INF-035 | .trae/documents/systemic_drift_root_cure_continuation_plan.md | §4 P2-T1
# [MODULE] zephyr.governance.reconciliation_registry
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] (none — pure stdlib)
# [CONSUMERS] zephyr.governance.git_commit_gateway.GitCommitGateway
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] ReconciliationRegistry.register 幂等（同 gate_id 覆盖旧 spec）；reconcile_for 按 priority 升序执行命中 trigger 的 reconciler；reconciler 异常被捕获为 warn 结果（不阻断后续 reconciler）
# [MODIFY-GUARD] ReconcilerSpec 字段结构；ReconcileResult.action 枚举语义
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile_for 永不抛异常——单个 reconciler 异常降级为 ReconcileResult(action="warn")
# [TESTS] tests/unit/test_reconciliation_registry.py (P3-T1)
# [A_module] module_id=MOD-GOV-reconciliation_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""reconciliation_registry.py — GitCommitGateway post-commit 漂移对账注册表（P2-T1）

把 ``_post_commit_reconcile`` 单线硬编码升级为声明式 registry：每个被
``--no-verify`` 绕过的 pre-commit GATE 注册一个 post-commit reconciler，
commit 完成后由 registry 统一调度。

设计理由（三层病根之机制层治本）
--------------------------------
GitCommitGateway 在所有 commit 路径统一用 ``--no-verify``（斩断 stash 冲突链），
副作用是系统性关闭全部 pre-commit 漂移检测 GATE。P0-DRC 仅硬编码补了 manifest
1/4 条线。本 registry 把"补偿"从硬编码 if-then 流水线升级为可扩展声明式框架：
新增 GATE 补偿只需 ``register(spec)``，不改 gateway 方法体。

命名区隔（防混淆）
------------------
本模块的 ``ReconcilerSpec`` / ``ReconciliationRegistry`` 管 **commit-gateway
post-commit drift 对账**，与 ``zephyr.infrastructure.asset_inventory.Reconciler``
（MOD-INF-026 资产清单对账，磁盘 vs unified-asset-index.yaml）是**完全不同的
关注点**，勿混淆。

纯 stdlib 解耦
---------------
本模块仅依赖 stdlib（dataclasses/typing），不 import zephyr.*，便于 mutation
testing 用 ``importlib.util.spec_from_file_location`` 直接加载（仿
``post_sync_validator.py`` SSoT 解耦模式，规避 ``zephyr.integration.events``
import 链断裂）。

Usage::

    from zephyr.governance.reconciliation_registry import (
        ReconcileResult, ReconcilerSpec, ReconciliationRegistry,
    )

    registry = ReconciliationRegistry()
    registry.register(ReconcilerSpec(
        gate_id="GATE-19-manifest",
        trigger=lambda files: any(f.startswith("scripts/") and f.endswith(".py") for f in files),
        reconcile=lambda files, sid: ReconcileResult(action="clean", detail="ok"),
        priority=100,
    ))
    results = registry.reconcile_for(["scripts/foo.py"], "sess-001")
    # results == [ReconcileResult(action="clean", detail="ok")]
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable

logger = logging.getLogger(__name__)

__all__ = [
    "ReconcileResult",
    "ReconcilerSpec",
    "ReconciliationRegistry",
]


@dataclass
class ReconcileResult:
    """post-commit 真源对账结果（P0-DRC / P2-T1 迁移至本模块）。

    action 含义：
    - skip: 本次 commit 未涉及该 reconciler 关心的文件，跳过对账
    - clean: 真源重生成后无变更，一致
    - auto_committed: 检测到漂移并自动提交修复
    - warn: 检测到漂移但自动修复失败（仅告警，不阻断；commit 已入 git 历史）
    """

    action: str  # "skip" | "clean" | "auto_committed" | "warn"
    detail: str = ""


@dataclass
class ReconcilerSpec:
    """单个 GATE 的 post-commit 对账声明。

    Attributes:
        gate_id: 关联的 pre-commit GATE 标识（如 "GATE-19-manifest"）。
        trigger: 判断本次 committed_files 是否命中该 reconciler；
            返回 True 才执行 reconcile。签名 ``(committed_files: list[str]) -> bool``。
        reconcile: 执行对账，返回 ReconcileResult。
            签名 ``(committed_files: list[str], session_id: str) -> ReconcileResult``。
            reconciler 是闭包，注册时捕获所需上下文（project_root / gateway 实例等）。
        priority: 执行优先级（升序，数字小先执行）；同 priority 按 register 顺序。
    """

    gate_id: str
    trigger: Callable[[list[str]], bool]
    reconcile: Callable[[list[str], str], ReconcileResult]
    priority: int = 100


class ReconciliationRegistry:
    """声明式 post-commit 漂移对账注册表（P2-T1）。

    每个 GitCommitGateway 实例持有一个 registry（实例级，非模块级单例——
    避免 reconciler 闭包捕获 gateway 前的先有鸡先有蛋问题）。
    commit 完成后调 ``reconcile_for(committed_files, session_id)``，
    registry 按 priority 升序遍历所有注册的 spec，trigger 命中即执行 reconcile。

    容错：单个 reconciler 抛异常时降级为 ``ReconcileResult(action="warn")``，
    不阻断后续 reconciler 执行（drift 对账非阻断，commit 已入历史）。
    """

    def __init__(self) -> None:
        self._specs: list[ReconcilerSpec] = []

    def register(self, spec: ReconcilerSpec) -> None:
        """注册一个 reconciler spec（同 gate_id 覆盖旧 spec，幂等）。

        按 priority 升序保持 _specs 有序（注册后即排序，reconcile_for 时无需再排）。
        """
        # 幂等：同 gate_id 先移除旧 spec
        self._specs = [s for s in self._specs if s.gate_id != spec.gate_id]
        self._specs.append(spec)
        self._specs.sort(key=lambda s: s.priority)

    def reconcile_for(
        self, committed_files: list[str], session_id: str
    ) -> list[ReconcileResult]:
        """遍历注册的 reconciler，trigger 命中即执行，返回结果列表。

        单个 reconciler 异常降级为 warn 结果，不阻断后续。
        """
        results: list[ReconcileResult] = []
        for spec in self._specs:
            try:
                if not spec.trigger(committed_files):
                    continue
                result = spec.reconcile(committed_files, session_id)
                results.append(result)
            except Exception as e:  # noqa: BLE001 — drift 对账非阻断
                logger.warning(
                    "ReconciliationRegistry: reconciler %s failed: %s",
                    spec.gate_id, e,
                )
                results.append(
                    ReconcileResult(
                        action="warn",
                        detail=f"reconciler {spec.gate_id} raised: {e}",
                    )
                )
        return results

    @property
    def spec_count(self) -> int:
        """已注册的 reconciler 数量（测试/诊断用）。"""
        return len(self._specs)

    def list_gate_ids(self) -> list[str]:
        """已注册的 gate_id 列表（诊断用）。"""
        return [s.gate_id for s in self._specs]
