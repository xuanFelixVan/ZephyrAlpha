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
    "make_manifest_reconciler",
    "make_baseline_aware_reconciler",
    "make_ttl_reconciler",
    "make_ghost_reconciler",
    "make_path_tree_reconciler",
    "make_working_docs_reconciler",
    "make_domain_doc_reconciler",
    "scan_and_archive_working_docs",
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


def make_manifest_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-19 manifest post-commit 对账 reconciler（P2-T2）。

    把原 ``GitCommitGateway._post_commit_reconcile`` 逻辑迁移为独立 ReconcilerSpec，
    注册到 ReconciliationRegistry。闭包捕获 gateway 实例以复用 ``project_root``
    与 ``_run_git``。

    对账链（与迁移前行为等价）：
    1. trigger: committed_files 含 scripts/ 下 .py → 命中
    2. 重生成 scripts/script_manifest.yaml（generate_manifest.py os.walk 全树 SSoT）
    3. git diff 检测 manifest 变更 → 无变更返回 clean
    4. 有变更 → git add + git commit --no-verify（斩断 zombie 引用循环）

    manifest 体系区分（P1-T4 校正）：本 reconciler 重生成的是
    ``scripts/script_manifest.yaml``（全树 manifest，generate_manifest.py 产出，
    供 gateway + audit_registration 消费）；非 ``scripts/governance/script_manifest.yaml``
    （governance 子集，generate_script_manifest.py 产出，GATE-19 校验）。二者非冗余。

    Args:
        gateway: GitCommitGateway 实例（仅用其 project_root + _run_git，类型注解为
            object 避免本纯 stdlib 模块 import zephyr.*）。

    Returns:
        ReconcilerSpec(gate_id="GATE-19-manifest", priority=100)。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel.startswith("scripts/") and rel.endswith(".py"):
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 重生成 manifest（SSoT disk-scan）
        gen_result = subprocess.run(
            [sys.executable, "scripts/generate_manifest.py"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        if gen_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"manifest regeneration failed: {gen_result.stderr.strip()[:200]}",
            )

        # 2. 检测 manifest 变更
        diff_result = gateway._run_git(
            ["git", "diff", "--name-only", "--", "scripts/script_manifest.yaml"]
        )
        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="manifest up to date")

        # 3. 变更 → 自动提交修复
        add_result = gateway._run_git(["git", "add", "scripts/script_manifest.yaml"])
        if add_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"git add manifest failed: {add_result.stderr.strip()[:200]}",
            )

        auto_msg = (
            f"chore(manifest): auto-reconcile by GitCommitGateway post-commit "
            f"[GW:{session_id}:auto]"
        )
        commit_result = gateway._run_git(
            ["git", "commit", "--no-verify", "-m", auto_msg,
             "--", "scripts/script_manifest.yaml"]
        )
        if commit_result.returncode == 0:
            return ReconcileResult(
                action="auto_committed",
                detail="manifest drift detected and auto-reconciled",
            )
        return ReconcileResult(
            action="warn",
            detail=f"manifest drift detected, auto-commit failed: "
                   f"{commit_result.stderr.strip()[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-19-manifest",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=100,
    )


def make_baseline_aware_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-REG-BL baseline-aware post-commit 对账 reconciler（P2-T3）。

    GATE-REG-BL 被 GitCommitGateway 的 --no-verify 系统性绕过（机制层病根）。
    本 reconciler 在 post-commit 跑 audit_registration.py --incremental --baseline-aware
    增量扫描，检测 NEW 孤儿（不阻断——commit 已入历史，仅记录报告供人工追责）。

    非阻断设计理由：post-commit 对账无法回滚已提交 commit；记录 NEW 孤儿到
    .runtime/reconcile_reports/baseline_aware_<ts>.json，供 ide_health_daemon + 人工追责。

    flag 真实性已核实：--baseline-aware 在 audit_registration.py L810-814 真实注册
    （呼应 project_memory 反幻觉教训：上一轮 AI 误判为臆造 flag）。

    Args:
        gateway: GitCommitGateway 实例（用 project_root，类型注解 object
            保持本模块纯 stdlib 不 import zephyr.*）。

    Returns:
        ReconcilerSpec(gate_id="GATE-REG-BL", priority=200)。
    """
    import json
    import os
    import subprocess
    import sys
    import time

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel.startswith("src/zephyr/") and rel.endswith(".py"):
                return True
            if rel.startswith("scripts/governance/") and rel.endswith(".py"):
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. post-commit baseline-aware 扫描（非阻断）
        # 治本 Bug 1：改用 --files 传入精确 committed_files，替代 --incremental。
        # --incremental 用 git diff HEAD 扫描工作树全部 WIP，会把与本次 commit 无关的
        # WIP 文件误判为 NEW orphan（例如 runtime_interceptor.py 是 WIP 未提交却被扫到，
        # 而 commit 实际只含 fix_shared_bypass.py 等 4 个无关文件）。
        # 仅传 src/zephyr/ 与 scripts/ 下的 .py（与 trigger 范围一致；audit 内部会再过滤）。
        rel_py_files = [
            os.path.relpath(f, str(project_root)).replace("\\", "/")
            for f in committed_files
            if f.endswith(".py")
        ]
        rel_py_files = [
            rel for rel in rel_py_files
            if rel.startswith("src/zephyr/") or rel.startswith("scripts/")
        ]
        if not rel_py_files:
            return ReconcileResult(
                action="skip",
                detail="baseline_aware: no src/zephyr|scripts .py in committed files",
            )
        scan_result = subprocess.run(
            [sys.executable, "scripts/governance/audit_registration.py",
             "--baseline-aware", "--files"] + rel_py_files,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        # 2. 报告落盘（无论 exit code，记录供追责）
        reports_dir = project_root / ".runtime" / "reconcile_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        report_path = reports_dir / f"baseline_aware_{ts}.json"
        report = {
            "gate_id": "GATE-REG-BL",
            "session_id": session_id,
            "timestamp": ts,
            "exit_code": scan_result.returncode,
            "stdout_tail": scan_result.stdout.strip()[-500:],
            "stderr_tail": scan_result.stderr.strip()[-500:],
            "committed_files": committed_files,
            "scanned_files": rel_py_files,
        }
        try:
            report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as e:
            return ReconcileResult(
                action="warn",
                detail=f"baseline_aware scan done (exit={scan_result.returncode}) but report write failed: {e}",
            )
        # 3. 判定结果
        if scan_result.returncode == 0:
            return ReconcileResult(
                action="clean",
                detail=f"baseline_aware scan clean, report={report_path.name}",
            )
        # exit 1 = NEW 孤儿检出（commit 已入历史，仅告警）
        return ReconcileResult(
            action="warn",
            detail=f"baseline_aware scan detected NEW orphans (exit={scan_result.returncode}), report={report_path.name}",
        )

    return ReconcilerSpec(
        gate_id="GATE-REG-BL",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=200,
    )


def make_ttl_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-15 ttl post-commit 兜底 reconciler（P2-T4）。

    GATE-15 (frontmatter ttl) 已有 pre-compensation（``_check_frontmatter_ttl``
    在 commit() 前阻断违规 .md），但若 pre-compensation 因异常被吞，违规 .md
    会漏放入库。本 reconciler 在 post-commit 兜底重校，记录违规报告供追责。

    设计裁定（增量 vs 全量）：
    continuation plan §4.4 原述"全量校验"，经核实 check_frontmatter_metadata.py
    的真实 CLI（手动读 sys.argv，无 argparse；--all-files=全量 docs/，传文件参=增量）后，
    采用**增量模式**（传 committed .md 文件为参数）。理由：
    1. pre-compensation 已对 committed 文件增量校验，post 兜底应镜像同范围
    2. 全量 5149 文件每次 .md 提交都跑会慢且产生无关噪声
    3. 增量精确锁定"本次 commit 是否漏放违规 .md"（兜底语义）

    非阻断设计：post-commit 无法回滚 commit；记录违规到
    .runtime/reconcile_reports/ttl_<ts>.json，与 pre-compensation 形成双层防御。

    Args:
        gateway: GitCommitGateway 实例（用 project_root，类型注解 object
            保持本模块纯 stdlib 不 import zephyr.*）。

    Returns:
        ReconcilerSpec(gate_id="GATE-15-ttl", priority=300)。
    """
    import json
    import os
    import subprocess
    import sys
    import time

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel.startswith("docs/") and rel.endswith(".md"):
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 筛选本次 committed 的 docs/*.md（增量模式参数）
        md_files = []
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel.startswith("docs/") and rel.endswith(".md"):
                md_files.append(rel)
        if not md_files:
            return ReconcileResult(action="skip", detail="no docs/*.md in committed files")
        # 2. post-commit 增量 ttl 校验（传文件参 → 增量模式，非 --all-files）
        scan_result = subprocess.run(
            [sys.executable, "scripts/governance/d3_metadata/check_frontmatter_metadata.py"]
            + md_files,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        # 3. 报告落盘
        reports_dir = project_root / ".runtime" / "reconcile_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        report_path = reports_dir / f"ttl_{ts}.json"
        report = {
            "gate_id": "GATE-15-ttl",
            "session_id": session_id,
            "timestamp": ts,
            "exit_code": scan_result.returncode,
            "checked_files": md_files,
            "stdout_tail": scan_result.stdout.strip()[-500:],
            "stderr_tail": scan_result.stderr.strip()[-500:],
        }
        try:
            report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as e:
            return ReconcileResult(
                action="warn",
                detail=f"ttl scan done (exit={scan_result.returncode}) but report write failed: {e}",
            )
        # 4. 判定（exit 0 = clean，非 0 = 违规检出）
        if scan_result.returncode == 0:
            return ReconcileResult(
                action="clean",
                detail=f"ttl scan clean ({len(md_files)} .md), report={report_path.name}",
            )
        return ReconcileResult(
            action="warn",
            detail=f"ttl scan detected violations (exit={scan_result.returncode}), report={report_path.name}",
        )

    return ReconcilerSpec(
        gate_id="GATE-15-ttl",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=300,
    )


def make_ghost_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 depgraph ghost post-commit 对账 reconciler（P2-T5）。

    commit 删除文件后，depgraph.db 可能残留 ghost node（磁盘已删除但 depgraph
    仍保留——对称漂移）。本 reconciler 在 post-commit 跑 diagnose_depgraph.py
    检测 ghost_count，记录报告供 ide_health_daemon + 人工追责。

    路径核实（反幻觉第四次验证）：diagnose_depgraph.py 真实路径为
    ``scripts/governance/diagnose_depgraph.py``（非 continuation plan §4.5 所述
    ``scripts/governance/d5_architecture/diagnose_depgraph.py``——该路径不存在）。

    设计裁定（trigger 检测删除方式）：
    continuation plan §4.5 建议用 ``git show --name-status HEAD`` 检测 D 状态。
    本实现改用 ``os.path.isfile(f)`` 检测 committed 文件不在磁盘 = 删除 commit。
    理由：①更廉价（无 git subprocess）；②post-commit 时点等价（commit 刚发生，
    工作树反映删除）；③代码更简。

    非阻断设计：post-commit 无法回滚 commit；记录 ghost_count 到
    .runtime/reconcile_reports/ghost_<ts>.json，ghost_count>0 仅告警。

    Args:
        gateway: GitCommitGateway 实例（用 project_root，类型注解 object
            保持本模块纯 stdlib 不 import zephyr.*）。

    Returns:
        ReconcilerSpec(gate_id="GATE-GHOST", priority=400)。
    """
    import json
    import os
    import re
    import subprocess
    import sys
    import time

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:
        # committed 文件不在磁盘 = 删除 commit（post-commit 时点，工作树已反映删除）
        return any(not os.path.isfile(f) for f in committed_files)

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 跑 diagnose_depgraph.py（无 --output，捕获 stdout 解析 ghost_count）
        diag_result = subprocess.run(
            [sys.executable, "scripts/governance/diagnose_depgraph.py"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        # 2. 解析 ghost_count（输出格式：[DIAG]   Found N orphan nodes (M ghost: ...))
        ghost_count = -1
        m = re.search(r"\((\d+)\s+ghost:", diag_result.stdout)
        if m:
            ghost_count = int(m.group(1))
        # 3. 报告落盘
        reports_dir = project_root / ".runtime" / "reconcile_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        report_path = reports_dir / f"ghost_{ts}.json"
        report = {
            "gate_id": "GATE-GHOST",
            "session_id": session_id,
            "timestamp": ts,
            "exit_code": diag_result.returncode,
            "ghost_count": ghost_count,
            "deleted_files": [f for f in committed_files if not os.path.isfile(f)],
            "stdout_tail": diag_result.stdout.strip()[-800:],
            "stderr_tail": diag_result.stderr.strip()[-500:],
        }
        try:
            report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as e:
            return ReconcileResult(
                action="warn",
                detail=f"ghost diagnose done (exit={diag_result.returncode}) but report write failed: {e}",
            )
        # 4. 判定（ghost_count==0 = clean；>0 = warn；-1 = 解析失败 = warn）
        if diag_result.returncode == 0 and ghost_count == 0:
            return ReconcileResult(
                action="clean",
                detail=f"ghost diagnose clean (ghost_count=0), report={report_path.name}",
            )
        return ReconcileResult(
            action="warn",
            detail=f"ghost diagnose: ghost_count={ghost_count} (exit={diag_result.returncode}), report={report_path.name}",
        )

    return ReconcilerSpec(
        gate_id="GATE-GHOST",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=400,
    )


def make_path_tree_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 arch_directory_tree post-commit 自动同步 reconciler。

    commit .py/.yaml 文件后，depgraph.db 的 arch_directory_tree 表可能过时
    （磁盘文件结构变了但 DB 未同步）。本 reconciler 在 post-commit 跑
    generate_project_path_tree.py --write 同步磁盘→DB，如有变更自动提交。

    对标 make_manifest_reconciler 的"检测变更→自动提交"模式。
    替代原 pre-commit GATE-SYNC-PATH-TREE hook（该 hook 有 depgraph.db
    unstaged 死循环副作用，reconciler 在 post-commit 自动提交修复此问题）。

    Args:
        gateway: GitCommitGateway 实例（用 project_root + _run_git）。

    Returns:
        ReconcilerSpec(gate_id="GATE-PATH-TREE", priority=150)。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel.endswith((".py", ".yaml", ".yml")):
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 同步磁盘→DB（generate_project_path_tree.py --write 幂等）
        sync_result = subprocess.run(
            [sys.executable, "scripts/governance/generate_project_path_tree.py", "--write"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        if sync_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"path_tree sync failed: {sync_result.stderr.strip()[:200]}",
            )

        # 2. 检测 depgraph.db 变更
        diff_result = gateway._run_git(
            ["git", "diff", "--name-only", "--", "data/databases/depgraph.db"]
        )
        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="arch_directory_tree up to date")

        # 3. 变更 → 自动提交
        add_result = gateway._run_git(["git", "add", "data/databases/depgraph.db"])
        if add_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"git add depgraph.db failed: {add_result.stderr.strip()[:200]}",
            )

        auto_msg = (
            f"chore(depgraph): auto-sync arch_directory_tree by GitCommitGateway post-commit "
            f"[GW:{session_id}:auto]"
        )
        commit_result = gateway._run_git(
            ["git", "commit", "--no-verify", "-m", auto_msg,
             "--", "data/databases/depgraph.db"]
        )
        if commit_result.returncode == 0:
            return ReconcileResult(
                action="auto_committed",
                detail="arch_directory_tree drift detected and auto-reconciled",
            )
        return ReconcileResult(
            action="warn",
            detail=f"arch_directory_tree drift detected, auto-commit failed: "
                   f"{commit_result.stderr.strip()[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-PATH-TREE",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=150,
    )


def scan_and_archive_working_docs(project_root: "object", dry_run: bool = False) -> dict:
    """扫描 docs/_working/*.md 的幽灵引用并归档有幽灵引用的文档。

    真源函数：``make_working_docs_reconciler`` 与一次性归档（S5/CLI）共用此逻辑
    （向内收——扫描+归档逻辑唯一真源在此，两处复用，不另建脚本）。

    扫描 docs/_working/*.md（排除 README.md permanent 定位说明），提取每个文档
    引用的项目内文件路径（.py/.yaml/.yml/.md），检测引用路径是否仍存在于磁盘。
    有幽灵引用的文档移动到 .runtime/working_archive/<ts>/<name>（可恢复，且
    .runtime/ 已 .gitignore 不入库）。

    路径引用提取（v1 保守，宁漏勿误）：
    - markdown 链接 ``](path)`` → 提取 path
    - 反引号代码 ``` `path` ``` → 提取 path
    - file:/// 绝对路径 → 转项目相对路径
    - 排除 http(s):// / mailto: / # 锚点等外部引用
    - 不扫描裸文本路径（避免代码示例误判）

    Args:
        project_root: 项目根路径（Path 或 str）。
        dry_run: True 只扫描不归档（返回候选列表）；False 归档（移动文件）。

    Returns:
        报告 dict：::

            {
              "scanned": int,
              "archived": [filename, ...],   # dry_run 时为候选
              "clean": [filename, ...],
              "details": {filename: {"ghost_refs": [...], optional "archive_error": str}},
              "archive_dir": str | None,
            }
    """
    import re
    import shutil
    import time
    from pathlib import Path

    project_root = Path(project_root)
    working_dir = project_root / "docs" / "_working"
    if not working_dir.is_dir():
        return {"scanned": 0, "archived": [], "clean": [], "details": {}, "archive_dir": None}

    # 路径引用正则：markdown 链接 ](path) 与反引号 `path`（保守，只匹配明确引用语法）
    _MD_LINK_RE = re.compile(r"\]\(([^)]+\.(?:py|yaml|yml|md))\)", re.IGNORECASE)
    _BACKTICK_RE = re.compile(r"`([^`]+\.(?:py|yaml|yml|md))`", re.IGNORECASE)

    def _looks_like_path(ref: str) -> bool:
        """过滤非路径引用：必须含路径分隔符，不含空格/通配符/括号。

        宁漏勿误——裸文件名（如 project_memory.md）可能指项目外文件；
        含空格的多是命令行示例（如 ``python scripts/foo.py``）；
        含通配符的是 glob（如 ``**/index.md``）。
        """
        if "/" not in ref and "\\" not in ref:
            return False  # 裸文件名，可能指项目外，跳过
        if any(c in ref for c in (" ", "*", "?", "[", "(", "{")):
            return False  # 命令行示例或通配符，跳过
        if "..." in ref:
            return False  # 省略写法（如 docs/.../foo.md），跳过
        return True

    def _extract_refs(content: str) -> list[str]:
        refs: list[str] = []
        for m in _MD_LINK_RE.finditer(content):
            r = m.group(1).replace("\\", "/")
            if _looks_like_path(r):
                refs.append(r)
        for m in _BACKTICK_RE.finditer(content):
            r = m.group(1).replace("\\", "/")
            if _looks_like_path(r):
                refs.append(r)
        # 去重保序
        seen: set[str] = set()
        unique: list[str] = []
        for r in refs:
            if r not in seen:
                seen.add(r)
                unique.append(r)
        return unique

    def _is_external(ref: str) -> bool:
        return ref.startswith(("http://", "https://", "mailto:", "#"))

    def _is_ghost(ref: str) -> bool:
        if _is_external(ref):
            return False
        # file:/// 绝对路径 → 直接作为绝对路径检查（不拼 project_root，避免前导/解析 bug）
        if ref.startswith("file:///"):
            abs_path = ref[len("file:///"):]
            return not Path(abs_path).exists()
        # 相对于 project_root
        if (project_root / ref).exists():
            return False
        # 相对于 _working/（处理 ../ 相对路径，resolve 兜底 .. 折叠）
        if (working_dir / ref).resolve().exists():
            return False
        return True

    md_files = [f for f in working_dir.glob("*.md") if f.name != "README.md"]
    archived: list[str] = []
    clean: list[str] = []
    details: dict = {}
    archive_dir = None

    for md in md_files:
        try:
            content = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        refs = _extract_refs(content)
        ghosts = [r for r in refs if _is_ghost(r)]
        if ghosts:
            details[md.name] = {"ghost_refs": ghosts}
            if not dry_run:
                if archive_dir is None:
                    archive_dir = project_root / ".runtime" / "working_archive" / str(int(time.time()))
                    archive_dir.mkdir(parents=True, exist_ok=True)
                dest = archive_dir / md.name
                try:
                    shutil.move(str(md), str(dest))
                    archived.append(md.name)
                except OSError as e:
                    details[md.name]["archive_error"] = str(e)
            else:
                archived.append(md.name)  # dry_run 计入候选供审阅
        else:
            clean.append(md.name)

    return {
        "scanned": len(md_files),
        "archived": archived,
        "clean": clean,
        "details": details,
        "archive_dir": str(archive_dir) if archive_dir else None,
    }


def make_working_docs_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 docs/_working/ 幽灵引用 post-commit 对账 reconciler（治本：AI 工作文档堆积治理）。

    docs/_working/ 下的 task_bound 文档引用脚本/规则/状态，随项目演进这些引用会
    过时变成"幽灵引用"，误导后续 AI 产生幻觉（违反"减少幻觉"核心原则）。本
    reconciler 在 post-commit 扫描 _working/*.md 的文件路径引用，检测引用路径
    是否仍存在；有幽灵引用的文档归档到 .runtime/working_archive/，并自动 commit
    _working/ 的删除，防止幽灵引用持续误导。

    向内收设计（三原则审核）：
    - 责任唯一：扫描+归档逻辑只在 ``scan_and_archive_working_docs`` 一处，reconciler
      与一次性归档（S5/CLI）共用，不另建脚本
    - 真源唯一：复用 ReconciliationRegistry 框架（第6个 reconciler），不新建清理系统；
      复用 make_ghost_reconciler 的"删除检测 trigger"模式；复用 make_manifest_reconciler
      的"检测→git add→git commit --no-verify"自动提交模式
    - 向内收：扩展 ``_register_default_reconcilers`` 一行，不改 gateway 方法体

    非阻断设计：归档后自动 commit 删除；commit 失败降级为 warn（报告落盘供追责）。
    .runtime/ 已 .gitignore，归档文件不入库，仅 _working/ 删除需 commit。

    trigger 裁定：与 make_ghost_reconciler 一致——committed 文件不在磁盘 = 删除
    commit。删除是产生幽灵引用的主要原因（引用的文件被删/改名）；改名 = 删除+新增，
    删除部分会被检测。

    Args:
        gateway: GitCommitGateway 实例（用 project_root + _run_git，类型注解
            object 保持本纯 stdlib 模块不 import zephyr.*）。

    Returns:
        ReconcilerSpec(gate_id="GATE-WORKING-DOCS", priority=500)。
    """
    import json
    import os
    import time

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:
        # 与 make_ghost_reconciler 一致：committed 文件不在磁盘 = 删除 commit
        return any(not os.path.isfile(f) for f in committed_files)

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 扫描+归档（复用真源函数）
        scan = scan_and_archive_working_docs(project_root, dry_run=False)
        scanned = scan["scanned"]
        archived = scan["archived"]
        details = scan["details"]

        # 2. 报告落盘
        reports_dir = project_root / ".runtime" / "reconcile_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        report_path = reports_dir / f"working_docs_{ts}.json"
        report = {
            "gate_id": "GATE-WORKING-DOCS",
            "session_id": session_id,
            "timestamp": ts,
            "scanned": scanned,
            "archived": archived,
            "clean": scan["clean"],
            "details": details,
            "archive_dir": scan["archive_dir"],
        }
        try:
            report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as e:
            return ReconcileResult(
                action="warn",
                detail=f"working_docs scan done but report write failed: {e}",
            )

        if scanned == 0:
            return ReconcileResult(action="skip", detail="no task_bound .md in _working/")
        if not archived:
            return ReconcileResult(
                action="clean",
                detail=f"working_docs scan clean ({scanned} .md, 0 ghost), report={report_path.name}",
            )

        # 3. 归档后自动 commit _working/ 的删除
        # 只 stage 归档产生的删除文件（不用 -A，避免捡拾其他 session 在 _working/ 的 WIP）
        # 违反 session 隔离强不变量的修复：原 git add -A docs/_working/ 会把其他 session 的 WIP 一并 commit
        archived_rel = [f"docs/_working/{name}" for name in archived]
        add_result = gateway._run_git(["git", "add", "--"] + archived_rel)
        if add_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"working_docs archived {len(archived)} but git add failed: "
                       f"{add_result.stderr.strip()[:200]}",
            )
        auto_msg = (
            f"chore(working_docs): auto-archive {len(archived)} ghost-ref docs by "
            f"GitCommitGateway post-commit [GW:{session_id}:auto]"
        )
        commit_result = gateway._run_git(
            ["git", "commit", "--no-verify", "-m", auto_msg, "--"] + archived_rel
        )
        if commit_result.returncode == 0:
            return ReconcileResult(
                action="auto_committed",
                detail=f"working_docs archived {len(archived)} ghost-ref docs, "
                       f"report={report_path.name}",
            )
        return ReconcileResult(
            action="warn",
            detail=f"working_docs archived {len(archived)} but auto-commit failed: "
                   f"{commit_result.stderr.strip()[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-WORKING-DOCS",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=500,
    )


def make_domain_doc_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造域文档制品 post-commit 自动重生 reconciler。

    commit depgraph.db 后，域文档制品（.md/.mmd）可能过时（DB 变了但制品未重生）。
    本 reconciler 在 post-commit 跑 generate_domain_doc.py --all +
    generate_domain_dependency_diagram.py --all 重生所有域制品，如有变更自动提交。

    治本修复2a/2b：消除"DB 变更→制品漂移"窗口（红蓝对抗严重2 治本延伸）。
    之前手工运行生成器（违反逻辑2.2 自动触发原则），现改为 post-commit 事件驱动。

    循环安全：trigger 只匹配 depgraph.db，制品 auto-commit 的 committed_files
    是 .md/.mmd，不命中 trigger，不会递归触发。

    Args:
        gateway: GitCommitGateway 实例（用 project_root + _run_git）。

    Returns:
        ReconcilerSpec(gate_id="GATE-DOMAIN-DOC", priority=600)。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root
    _DEPGRAPH_DB_REL = "data/databases/depgraph.db"
    _GEN_DIR = "scripts/governance/d5_architecture/generators"
    _DOC_DIRS = (
        "docs/02_enterprise_architecture/02_domain_architecture_docs",
        "docs/02_enterprise_architecture/generated/domains",
    )

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel == _DEPGRAPH_DB_REL:
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 重生所有域制品（生成器不含时间戳，相同 DB 输入→相同输出）
        for gen_name in ("generate_domain_doc.py", "generate_domain_dependency_diagram.py"):
            gen_result = subprocess.run(
                [sys.executable, f"{_GEN_DIR}/{gen_name}", "--all"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
            )
            if gen_result.returncode != 0:
                return ReconcileResult(
                    action="warn",
                    detail=f"{gen_name} --all failed: {gen_result.stderr.strip()[:200]}",
                )

        # 2. 检测制品变更
        diff_result = gateway._run_git(
            ["git", "diff", "--name-only", "--", *_DOC_DIRS]
        )
        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="domain docs up to date")

        # 3. 变更 → 自动提交
        add_result = gateway._run_git(["git", "add", "--", *_DOC_DIRS])
        if add_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"git add domain docs failed: {add_result.stderr.strip()[:200]}",
            )

        auto_msg = (
            f"chore(docs): auto-regenerate domain docs by GitCommitGateway post-commit "
            f"[GW:{session_id}:auto]"
        )
        commit_result = gateway._run_git(
            ["git", "commit", "--no-verify", "-m", auto_msg, "--", *_DOC_DIRS]
        )
        if commit_result.returncode == 0:
            return ReconcileResult(
                action="auto_committed",
                detail="domain docs drift detected and auto-regenerated",
            )
        return ReconcileResult(
            action="warn",
            detail=f"domain docs drift detected, auto-commit failed: "
                   f"{commit_result.stderr.strip()[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-DOMAIN-DOC",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=600,
    )
