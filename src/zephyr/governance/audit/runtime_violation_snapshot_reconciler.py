# [BLUEPRINT] MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER | docs/03_modules/_domain_governance/blueprint.md | §runtime-violation-snapshot-reconciler
# [MODULE] zephyr.governance.audit.runtime_violation_snapshot_reconciler
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec); zephyr.governance.audit.runtime_violation_snapshot
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] post-commit 事件触发（committed_files 含 .py 或 trae_060 yaml 才触发）；reconciler 永不抛异常（异常降级为 warn）；快照生成失败不阻断 commit（warn-only Phase 0）
# [MODIFY-GUARD] _TRIGGER_PATHS 触发路径；_PRIORITY 优先级
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile 永不抛异常——快照生成失败降级为 ReconcileResult(action="warn")
# [TESTS] tests/governance/audit/test_runtime_violation_snapshot_reconciler.py
# [A_module] module_id=MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable  # noqa: blueprint-amodule-cross-check [BLUEPRINT]==[A_module] same module
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)
"""

runtime_violation_snapshot_reconciler.py — trae_060 §5 evidence 运行时快照 post-commit reconciler。

#ARCH-GOV-CONVERGENCE-META Phase 3.4b（病根1 治本）

治本动机
--------
trae_060 §5 的"违规清单"是 2026-06-26 的静态快照，写入 frozen YAML 后持续脱节
（详见 runtime_violation_snapshot.py 模块 docstring）。

本 reconciler 是病根1 治本的"自动维护"环节（三要素之可维护）：
  - **持久化**：snapshot 存到 ``data/runtime_violation_snapshot/latest.json``
  - **可发现**：M20 指标报告 drift_count（AI 冷启动可查）
  - **自动维护**：post-commit 事件触发，无需人工干预

设计裁定（对标 trae_060 三原则）
--------------------------------
- **原则①能现成不创造**：复用 runtime_violation_snapshot.generate_snapshot()，
  不重新实现检测逻辑；复用 ReconciliationRegistry 框架，不新建触发系统
- **原则②创造必全自动**：post-commit 事件触发（非 cron/manual），自动生成+保存
- **原则③第一性原理**：质疑"违规清单是否该 frozen"——事实快照必须 live

触发条件
--------
committed_files 满足以下任一即触发：
  1. 含 ``src/zephyr/**/*.py`` 或 ``scripts/governance/**/*.py``（业务代码变更）
  2. 含 ``docs/01_policies_and_standards/rules/trae_060_*.yaml``（规则本身变更）

执行流程
--------
1. trigger 命中 → reconcile 执行
2. 调 ``generate_snapshot(project_root, session_id, commit_sha)``
3. 调 ``save_snapshot(snapshot, project_root)`` 持久化
4. 返回 ReconcileResult(action="clean"/"warn")，不阻断 commit

priority: 850（晚于业务 reconciler，早于 remediation_progress(900)）

Usage
-----
::

    from zephyr.governance.audit.runtime_violation_snapshot_reconciler import (
        make_runtime_violation_snapshot_reconciler,
    )

    registry.register(make_runtime_violation_snapshot_reconciler(gateway))

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: committed_files 提交文件清单 list[str]
#   fields: 本次 commit 文件路径（判定是否含 src/zephyr/ 或 scripts/governance/ 的 .py，或 trae_060 规则 yaml）
#   code: _trigger L112 / _matches_trigger L92
# - id: I2
#   name: 快照生成器函数 同包依赖
#   fields: runtime_violation_snapshot.generate_snapshot + save_snapshot
#   code: import L74-77
# 层: 算法
# - id: A1
#   name_zh: ① 触发路径匹配
#   name_en: _matches_trigger
#   intro: 判断提交文件是否命中业务代码或 trae_060 规则文件，命中才执行快照更新
#   desc: 相对路径化（os.path.relpath，跨盘 ValueError 跳过）；非 .py 仅匹配 trae_060_inward_consolidation.yaml；.py 需以 src/zephyr/ 或 scripts/governance/ 前缀开头
#   inputs: I1
#   outputs: bool 触发判定
# - id: A2
#   name_zh: ② 快照生成与落盘
#   name_en: _reconcile
#   intro: 取 HEAD sha 后调 generate_snapshot 生成 live 快照并 save_snapshot 持久化
#   desc: git rev-parse HEAD 取 sha（失败留空）→ generate_snapshot(project_root, session_id, commit_sha) → save_snapshot → 从 summary 取 drift_count/total_detected/total_claimed 组 detail；异常降级 warn
#   inputs: A1 I2
#   outputs: ReconcileResult（clean=快照已保存）
#   invariant: 永不抛异常，快照失败不阻断 commit（warn-only）
# 层: 输出
# - id: O1
#   name_zh: 快照对账结果
#   name_en: ReconcileResult
#   intro: clean 附带 drift_count/detected/claimed 摘要；warn=快照生成失败，均不阻断 commit
#   invariant: warn-only（Phase 0）
#   downstream: GitCommitGateway（[CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# I2 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import os

from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconcilerSpec,
)
from zephyr.governance.audit.runtime_violation_snapshot import (
    generate_snapshot,
    save_snapshot,
)

logger = logging.getLogger(__name__)

_GATE_ID = "GATE-RUNTIME-VIOLATION-SNAPSHOT"
_PRIORITY = 850

# 触发路径前缀（相对 project_root）
_TRIGGER_PREFIXES = (
    "src/zephyr/",
    "scripts/governance/",
)
_TRIGGER_RULE_FILE = "docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml"


def _matches_trigger(rel_path: str) -> bool:
    """检查相对路径是否命中触发条件。"""
    if not rel_path.endswith(".py"):
        # 非 .py 文件只检查是否是 trae_060 规则文件本身
        return rel_path == _TRIGGER_RULE_FILE
    # .py 文件检查是否在触发前缀下
    return any(rel_path.startswith(prefix) for prefix in _TRIGGER_PREFIXES)


def make_runtime_violation_snapshot_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-RUNTIME-VIOLATION-SNAPSHOT post-commit 运行时快照 reconciler。

    Args:
        gateway: GitCommitGateway 实例（仅用其 project_root）。

    Returns:
        ReconcilerSpec(gate_id=_GATE_ID, priority=_PRIORITY)。
    """
    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            try:
                rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            except ValueError:
                continue
            if _matches_trigger(rel):
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        try:
            # 获取 commit sha（从 gateway 或留空）
            commit_sha = ""
            try:
                sha_result = gateway.run_git(["git", "rev-parse", "HEAD"])
                if sha_result.returncode == 0:
                    commit_sha = sha_result.stdout.strip()[:12]
            except Exception:  # noqa: BLE001 — sha 非关键
                pass

            snapshot = generate_snapshot(
                project_root=project_root,
                session_id=session_id,
                commit_sha=commit_sha,
            )
            save_snapshot(snapshot, project_root=project_root)

            drift_count = snapshot.get("summary", {}).get("drift_count", 0)
            total_detected = snapshot.get("summary", {}).get("total_detected", 0)
            total_claimed = snapshot.get("summary", {}).get("total_claimed", 0)

            return ReconcileResult(
                action="clean",
                detail=(
                    f"runtime violation snapshot saved: drift_count={drift_count}, "
                    f"detected={total_detected}, claimed={total_claimed} "
                    f"(Phase 3.4b 病根1 治本)"
                ),
                gate_id=_GATE_ID,
            )
        except Exception as e:  # noqa: BLE001 — reconciler 永不抛异常
            logger.warning("runtime_violation_snapshot reconciler failed: %s", e)
            return ReconcileResult(
                action="warn",
                detail=f"snapshot generation failed: {e}",
                gate_id=_GATE_ID,
            )

    return ReconcilerSpec(
        gate_id=_GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=_PRIORITY,
        file_ops=frozenset({"read", "write"}),
    )
