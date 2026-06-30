# [BLUEPRINT] MOD-INF-035 | .trae/documents/systemic_drift_root_cure_continuation_plan.md | §4 P2-T1
# [MODULE] zephyr.governance.reconciliation_registry
# [DOMAIN] D_GOVERNANCE
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
# [TTL] task_bound
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
    "make_rule_catalog_reconciler",
    "make_working_docs_reconciler",
    "make_domain_doc_reconciler",
    "make_precommit_id_uniqueness_reconciler",
    "make_rules_integrity_reconciler",
    "make_vocab_change_reconciler",
    "make_commit_gateway_audit_reconciler",
    "make_deprecated_directory_reconciler",
    "make_rule_file_audit_reconciler",
    "make_exempt_zone_frontmatter_reconciler",
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


def _write_reconcile_report(
    project_root: "object", prefix: str, report: dict
) -> "tuple[object, str]":
    """写 reconciler 报告到 ``.runtime/reconcile_reports/{prefix}_{ts}.json``。

    向内收（消除重复）：6 个 reconciler 都有 mkdir+ts+write+try/except 报告落盘
    模式，本函数收拢为单点。自动添加 ``timestamp`` 字段。

    Args:
        project_root: Path 对象（gateway.project_root，类型注解 object 保持纯 stdlib）。
        prefix: 报告文件名前缀（如 "baseline_aware" / "rules_integrity"）。
        report: 报告字典（不含 timestamp，本函数自动注入）。

    Returns:
        (report_path, "") 成功 | (None, error_msg) 失败。
    """
    import json
    import time
    reports_dir = project_root / ".runtime" / "reconcile_reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    report["timestamp"] = ts
    report_path = reports_dir / f"{prefix}_{ts}.json"
    try:
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return report_path, ""
    except OSError as e:
        return None, str(e)


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
        report = {
            "gate_id": "GATE-REG-BL",
            "session_id": session_id,
            "exit_code": scan_result.returncode,
            "stdout_tail": scan_result.stdout.strip()[-500:],
            "stderr_tail": scan_result.stderr.strip()[-500:],
            "committed_files": committed_files,
            "scanned_files": rel_py_files,
        }
        report_path, write_err = _write_reconcile_report(project_root, "baseline_aware", report)
        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"baseline_aware scan done (exit={scan_result.returncode}) but report write failed: {write_err}",
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
        report = {
            "gate_id": "GATE-15-ttl",
            "session_id": session_id,
            "exit_code": scan_result.returncode,
            "checked_files": md_files,
            "stdout_tail": scan_result.stdout.strip()[-500:],
            "stderr_tail": scan_result.stderr.strip()[-500:],
        }
        report_path, write_err = _write_reconcile_report(project_root, "ttl", report)
        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"ttl scan done (exit={scan_result.returncode}) but report write failed: {write_err}",
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
        report = {
            "gate_id": "GATE-GHOST",
            "session_id": session_id,
            "exit_code": diag_result.returncode,
            "ghost_count": ghost_count,
            "deleted_files": [f for f in committed_files if not os.path.isfile(f)],
            "stdout_tail": diag_result.stdout.strip()[-800:],
            "stderr_tail": diag_result.stderr.strip()[-500:],
        }
        report_path, write_err = _write_reconcile_report(project_root, "ghost", report)
        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"ghost diagnose done (exit={diag_result.returncode}) but report write failed: {write_err}",
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
        # 治本（2026-06-27）：删除 depgraph.db git diff/add/commit 死代码。
        # P2 PG 迁移后 depgraph 已迁至 PostgreSQL，generate_project_path_tree.py --write
        # 直接写入 PG（不产生 .db 文件变更），原 git diff/add/commit depgraph.db 逻辑
        # 永远不会命中（diff 永远为空），属于路径污染残留死代码。
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
        return ReconcileResult(
            action="clean",
            detail="arch_directory_tree synced to PostgreSQL",
        )

    return ReconcilerSpec(
        gate_id="GATE-PATH-TREE",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=150,
    )


def make_rule_catalog_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 rule_catalog_registry post-commit 自动同步 reconciler。

    commit ``docs/01_policies_and_standards/rules/`` 下文件后，
    ``rule_catalog_registry.yaml`` 可能过时（新增/修改/删除规则文件但 catalog
    未重新生成）。本 reconciler 在 post-commit 跑
    ``generate_rule_catalog.py`` 重新生成，如有变更自动提交。

    对标 ``make_path_tree_reconciler`` 的"检测变更→自动提交"模式。
    治 P3 审查发现的 catalog stale 问题（2026-05-07 至 2026-06-26 stale
    1个月+，153条目74%死链）。catalog 是 ``sync_yaml_to_depgraph.py`` 的
    数据源（同步到 depgraph.db 的 arch_directory_tree 表），stale 会导致
    全景图数据污染。

    Args:
        gateway: GitCommitGateway 实例（用 project_root + _run_git）。

    Returns:
        ReconcilerSpec(gate_id="GATE-RULE-CATALOG", priority=160)。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root
    _CATALOG_REL = "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml"
    _RULES_PREFIX = "docs/01_policies_and_standards/rules/"

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel.startswith(_RULES_PREFIX) and rel.endswith((".yaml", ".yml", ".md")):
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 重新生成 catalog（generate_rule_catalog.py 幂等）
        gen_result = subprocess.run(
            [sys.executable, "scripts/governance/d3_metadata/generate_rule_catalog.py"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        if gen_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"rule_catalog generation failed: {gen_result.stderr.strip()[:200]}",
            )

        # 2. 检测 catalog 变更
        diff_result = gateway._run_git(
            ["git", "diff", "--name-only", "--", _CATALOG_REL]
        )
        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="rule_catalog_registry up to date")

        # 3. 变更 → 自动提交（精确路径，禁 git add -A 防捡拾其他 session WIP）
        add_result = gateway._run_git(["git", "add", "--", _CATALOG_REL])
        if add_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"git add rule_catalog_registry failed: {add_result.stderr.strip()[:200]}",
            )

        auto_msg = (
            f"chore(catalog): auto-sync rule_catalog_registry by GitCommitGateway post-commit "
            f"[GW:{session_id}:auto]"
        )
        commit_result = gateway._run_git(
            ["git", "commit", "--no-verify", "-m", auto_msg,
             "--", _CATALOG_REL]
        )
        if commit_result.returncode == 0:
            return ReconcileResult(
                action="auto_committed",
                detail="rule_catalog_registry drift detected and auto-reconciled",
            )
        return ReconcileResult(
            action="warn",
            detail=f"rule_catalog_registry drift detected, auto-commit failed: "
                   f"{commit_result.stderr.strip()[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-RULE-CATALOG",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=160,
    )


def make_registry_index_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 registry_master_index post-commit 自动同步 reconciler。

    commit ``infrastructure_registry.yaml`` 后，``registry_master_index.yaml``
    可能过时（新增/修改/删除基础设施条目但总索引未重新生成）。本 reconciler
    在 post-commit 跑 ``generate_registry_master_index.py`` 重新生成，如有
    变更自动提交。

    对标 ``make_rule_catalog_reconciler`` 的"检测变更→自动提交"模式。
    治 P2 审查发现的 registry_master_index stale 问题：当前仅有 pre-commit
    GATE-19 校验（阻断漂移），无 post-commit 自动重新生成，违反"永久性系统
    必须自动维护"铁律（逻辑2.2）。补建后形成"校验+自动修复"双闭环。

    Args:
        gateway: GitCommitGateway 实例（用 project_root + _run_git）。

    Returns:
        ReconcilerSpec(gate_id="GATE-REGISTRY-INDEX", priority=155)。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root
    _INDEX_REL = "docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml"
    _INFRA_REL = "docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml"

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel == _INFRA_REL:
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 重新生成 registry_master_index（generate_registry_master_index.py 幂等）
        gen_result = subprocess.run(
            [sys.executable, "scripts/governance/generators/generate_registry_master_index.py"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        if gen_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"registry_master_index generation failed: {gen_result.stderr.strip()[:200]}",
            )

        # 2. 检测 index 变更
        diff_result = gateway._run_git(
            ["git", "diff", "--name-only", "--", _INDEX_REL]
        )
        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="registry_master_index up to date")

        # 3. 变更 → 自动提交（精确路径，禁 git add -A 防捡拾其他 session WIP）
        add_result = gateway._run_git(["git", "add", "--", _INDEX_REL])
        if add_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"git add registry_master_index failed: {add_result.stderr.strip()[:200]}",
            )

        auto_msg = (
            f"chore(registry): auto-sync registry_master_index by GitCommitGateway post-commit "
            f"[GW:{session_id}:auto]"
        )
        commit_result = gateway._run_git(
            ["git", "commit", "--no-verify", "-m", auto_msg,
             "--", _INDEX_REL]
        )
        if commit_result.returncode == 0:
            return ReconcileResult(
                action="auto_committed",
                detail="registry_master_index drift detected and auto-reconciled",
            )
        return ReconcileResult(
            action="warn",
            detail=f"registry_master_index drift detected, auto-commit failed: "
                   f"{commit_result.stderr.strip()[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-REGISTRY-INDEX",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=155,
    )


def scan_and_archive_working_docs(project_root: "object", dry_run: bool = False) -> dict:
    """递归扫描 docs/_working/ 下工作文档的幽灵引用并归档有幽灵引用的文档。

    真源函数：``make_working_docs_reconciler`` 与一次性归档（S5/CLI）共用此逻辑
    （向内收——扫描+归档逻辑唯一真源在此，两处复用，不另建脚本）。

    递归扫描 docs/_working/ 下的工作文档（.md/.csv/.yaml/.yml/.json，排除
    README.md permanent 定位说明），提取每个文档引用的项目内文件路径，检测
    引用路径是否仍存在于磁盘。有幽灵引用的文档移动到
    .runtime/working_archive/<ts>/<name>（可恢复，且 .runtime/ 已 .gitignore 不入库）。

    路径引用提取（v2 扩展，治本 GAP-5：覆盖纯文本/CSV/YAML 路径）：
    - markdown 链接 ``](path)`` → 提取 path
    - 反引号代码 ``` `path` ``` → 提取 path
    - 纯文本路径（CSV 单元格值、YAML 值、正文裸路径 docs/foo/bar.md）
    - CSV 专用：逐单元格精确提取（避免正则误匹配 CSV 结构）
    - file:/// 绝对路径 → 转项目相对路径
    - 排除 http(s):// / mailto: / # 锚点等外部引用

    双重路径解析（治本 GAP-1，与 audit_broken_links.py 一致）：
    - 先相对于文档所在目录解析（markdown 链接习惯，嵌套子目录正确）
    - 若不存在，尝试相对于 project_root 解析（CSV/YAML 项目根相对路径）
    - 两者任一存在即判定非幽灵

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
    import csv
    import re
    import shutil
    import time
    from pathlib import Path

    project_root = Path(project_root)
    working_dir = project_root / "docs" / "_working"
    if not working_dir.is_dir():
        return {"scanned": 0, "archived": [], "clean": [], "details": {}, "archive_dir": None}

    # 支持的工作文档扩展名（治本 GAP-5：.md only → 多类型）
    _SUPPORTED_EXT = frozenset({".md", ".csv", ".yaml", ".yml", ".json"})

    # 路径引用正则（与 audit_broken_links.py 保持一致，向内收复用模式）：
    # - markdown 链接 ](path) 与反引号 `path`（保守，明确引用语法）
    # - 纯文本路径：含路径分隔符的文件路径（覆盖 .py/.ps1/.sh/.toml/.txt/.csv 等全扩展名）
    _MD_LINK_RE = re.compile(r"\]\(([^)]+\.(?:py|yaml|yml|md))\)", re.IGNORECASE)
    _BACKTICK_RE = re.compile(r"`([^`]+\.(?:py|yaml|yml|md))`", re.IGNORECASE)
    # 纯文本路径正则（治本 GAP-5 + 中文前缀防误捕）：
    # - lookbehind 用 [a-zA-Z0-9/] 而非 \w：中文是 \w，用 \w 会阻挡中文后的路径起点，
    #   导致"删除architecture_model/foo.yaml"中"删除"被吞入匹配；
    #   用 ASCII 集合则中文不阻挡，路径从 ASCII 字母处正确起match。
    # - 首字符限 [a-zA-Z]：路径必以 ASCII 字母起（docs/scripts/src/architecture_model/），
    #   杜绝中文前缀（删除/修订）被 [\w] 捕获为路径首字符。
    _TEXT_PATH_RE = re.compile(
        r"(?<![a-zA-Z0-9/])([a-zA-Z][\w\-./]*?/[\w\-]+\.(?:md|yaml|yml|json|py|ps1|sh|toml|txt|csv))\b"
    )

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

    def _extract_refs(content: str, source_ext: str) -> list[str]:
        """提取文档中引用的项目内文件路径。

        根据 source_ext 选择提取策略：
        - .md: markdown 链接 + 反引号 + 纯文本路径
        - .csv: markdown 链接 + 反引号 + 纯文本路径 + CSV 逐单元格精确提取
        - .yaml/.yml/.json: markdown 链接 + 反引号 + 纯文本路径
        """
        refs: list[str] = []
        # markdown 链接与反引号（所有文本类型都扫，.csv/.yaml 也可能含 markdown）
        for m in _MD_LINK_RE.finditer(content):
            r = m.group(1).replace("\\", "/")
            if _looks_like_path(r):
                refs.append(r)
        for m in _BACKTICK_RE.finditer(content):
            r = m.group(1).replace("\\", "/")
            if _looks_like_path(r):
                refs.append(r)
        # 纯文本路径（治本 GAP-5：覆盖 CSV/YAML/JSON 中的裸路径）
        for m in _TEXT_PATH_RE.finditer(content):
            r = m.group(1).replace("\\", "/")
            if _looks_like_path(r):
                refs.append(r)
        # CSV 专用：逐单元格提取（更精确，避免正则误匹配 CSV 结构）
        if source_ext == ".csv":
            try:
                reader = csv.reader(content.splitlines())
                for row in reader:
                    for cell in row:
                        cell = cell.strip().strip('"').strip("'")
                        if "/" in cell and "." in cell and _looks_like_path(cell):
                            refs.append(cell)
            except Exception:
                pass  # CSV 解析失败回退到正则结果
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

    def _is_ghost(ref: str, source: Path) -> bool:
        """双重路径解析判定幽灵引用（治本 GAP-1，与 audit_broken_links.py 一致）。

        先相对于文档所在目录解析（markdown 链接习惯，嵌套子目录正确）；
        若不存在，尝试相对于 project_root 解析（CSV/YAML 项目根相对路径）。
        两者任一存在即判定非幽灵。
        """
        if _is_external(ref):
            return False
        ref = ref.split("#")[0].strip()  # 剥离锚点（如 foo.md#section → foo.md）
        if not ref:
            return False
        # file:/// 绝对路径 → 直接作为绝对路径检查（不拼 project_root，避免前导/解析 bug）
        if ref.startswith("file:///"):
            abs_path = ref[len("file:///"):]
            return not Path(abs_path).exists()
        # 策略1：相对于文档所在目录解析（markdown 链接习惯，嵌套子目录正确）
        try:
            if (source.parent / ref).resolve().exists():
                return False
        except (OSError, ValueError):
            pass
        # 策略2：相对于 project_root 解析（CSV/YAML 项目根相对路径）
        try:
            if (project_root / ref).exists():
                return False
        except (OSError, ValueError):
            pass
        return True

    # 递归扫描多类型工作文档（治本 GAP-5：glob("*.md") → rglob 多扩展名）
    working_files = [
        f for f in working_dir.rglob("*")
        if f.is_file()
        and f.suffix.lower() in _SUPPORTED_EXT
        and f.name != "README.md"
    ]
    archived: list[str] = []
    clean: list[str] = []
    details: dict = {}
    archive_dir = None

    for doc in working_files:
        try:
            content = doc.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        refs = _extract_refs(content, doc.suffix.lower())
        ghosts = [r for r in refs if _is_ghost(r, doc)]
        if ghosts:
            details[doc.name] = {"ghost_refs": ghosts}
            if not dry_run:
                if archive_dir is None:
                    archive_dir = project_root / ".runtime" / "working_archive" / str(int(time.time()))
                    archive_dir.mkdir(parents=True, exist_ok=True)
                dest = archive_dir / doc.name
                try:
                    shutil.move(str(doc), str(dest))
                    archived.append(doc.name)
                except OSError as e:
                    details[doc.name]["archive_error"] = str(e)
            else:
                archived.append(doc.name)  # dry_run 计入候选供审阅
        else:
            clean.append(doc.name)

    return {
        "scanned": len(working_files),
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
        report = {
            "gate_id": "GATE-WORKING-DOCS",
            "session_id": session_id,
            "scanned": scanned,
            "archived": archived,
            "clean": scan["clean"],
            "details": details,
            "archive_dir": scan["archive_dir"],
        }
        report_path, write_err = _write_reconcile_report(project_root, "working_docs", report)
        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"working_docs scan done but report write failed: {write_err}",
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

    治本（2026-06-27）：原 trigger 匹配 ``data/databases/depgraph.db`` commit 事件，
    P2 PG 迁移后 depgraph 已迁至 PostgreSQL，无 .db 文件 commit 路径，trigger 永不命中，
    reconciler 沦为死代码。现改为匹配 PG 写入脚本 commit（apply_depgraph.py /
    sync_yaml_to_depgraph.py / generate_project_path_tree.py），这三者是 PG depgraph
    的唯一写入入口，其变更即代表 DB 内容可能漂移，需重生域制品。

    本 reconciler 在 post-commit 跑 generate_domain_doc.py --all +
    generate_domain_dependency_diagram.py --all 重生所有域制品，如有变更自动提交。

    治本修复2a/2b：消除"DB 变更→制品漂移"窗口（红蓝对抗严重2 治本延伸）。
    之前手工运行生成器（违反逻辑2.2 自动触发原则），现改为 post-commit 事件驱动。

    循环安全：trigger 只匹配 PG 写入脚本（.py），制品 auto-commit 的 committed_files
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
    # 治本（2026-06-27）：PG 写入脚本真源列表（替代 depgraph.db trigger）。
    # 这三脚本是 PostgreSQL depgraph 的唯一写入入口，其 commit 即代表 DB 变更。
    _PG_WRITE_SCRIPTS = (
        "scripts/governance/apply_depgraph.py",
        "scripts/governance/sync_yaml_to_depgraph.py",
        "scripts/governance/generate_project_path_tree.py",
    )
    _GEN_DIR = "scripts/governance/d5_architecture/generators"
    _DOC_DIRS = (
        "docs/02_enterprise_architecture/02_domain_architecture_docs",
        "docs/02_enterprise_architecture/generated/domains",
    )

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel in _PG_WRITE_SCRIPTS:
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


def make_arch_model_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 EA 树 architecture_model/index.yaml post-commit 自动重生 reconciler。

    治本（2026-06-30）：dm200916_write_direct.py 当前 ``[STARTUP] manual``，EA 树
    index.yaml 的 domains 部分在 depgraph 域变更后不会自动重生，与 GATE-DOMAIN-DOC
    （priority=600，重生域文档）形成缺口——DB 域变更（新增/删除/重命名域）后，EA 树
    index.yaml 的 domains 列表漂移。本 reconciler 在 PG 写入脚本 commit 后触发
    dm200916 重生 EA 树 index.yaml。

    派生范围：index.yaml 的 domains 列表 + global_stats.total_domains（从 PG depgraph
    domains 表派生）。不派生：partitions/query_hints/id_conventions（手工模板）、
    index.md、capability_heatmap.yaml（含手工评估数据）。

    循环安全：trigger 只匹配 PG 写入脚本（.py），制品 auto-commit 的 committed_files
    是 index.yaml，不命中 trigger，不会递归触发。dm200916 不修改 PG depgraph（只读
    domains 表）。

    priority=610（在 GATE-DOMAIN-DOC 600 之后，确保域文档先生成再重生架构模型索引）。

    Args:
        gateway: GitCommitGateway 实例（用 project_root + _run_git）。

    Returns:
        ReconcilerSpec(gate_id="GATE-ARCH-MODEL", priority=610)。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root
    # PG 写入脚本真源列表（与 GATE-DOMAIN-DOC 一致，DB 变更即代表域可能漂移）
    _PG_WRITE_SCRIPTS = (
        "scripts/governance/apply_depgraph.py",
        "scripts/governance/sync_yaml_to_depgraph.py",
        "scripts/governance/generate_project_path_tree.py",
    )
    _GEN_SCRIPT = "scripts/governance/d5_architecture/dm200916_write_direct.py"
    _ARCH_MODEL_INDEX = (
        "docs/02_enterprise_architecture/target_architecture/architecture_model/index.yaml",
    )

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel in _PG_WRITE_SCRIPTS:
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 重生 EA 树 index.yaml（dm200916 从 PG depgraph domains 表派生）
        gen_result = subprocess.run(
            [sys.executable, _GEN_SCRIPT],
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
                detail=f"dm200916_write_direct.py failed: {gen_result.stderr.strip()[:200]}",
            )

        # 2. 检测 index.yaml 变更
        diff_result = gateway._run_git(
            ["git", "diff", "--name-only", "--", *_ARCH_MODEL_INDEX]
        )
        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="EA tree index.yaml up to date")

        # 3. 变更 → 自动提交
        add_result = gateway._run_git(["git", "add", "--", *_ARCH_MODEL_INDEX])
        if add_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"git add EA tree index.yaml failed: {add_result.stderr.strip()[:200]}",
            )

        auto_msg = (
            f"chore(arch_model): auto-regenerate EA tree index.yaml by GitCommitGateway post-commit "
            f"[GW:{session_id}:auto]"
        )
        commit_result = gateway._run_git(
            ["git", "commit", "--no-verify", "-m", auto_msg, "--", *_ARCH_MODEL_INDEX]
        )
        if commit_result.returncode == 0:
            return ReconcileResult(
                action="auto_committed",
                detail="EA tree index.yaml drift detected and auto-regenerated",
            )
        return ReconcileResult(
            action="warn",
            detail=f"EA tree index.yaml drift detected, auto-commit failed: "
                   f"{commit_result.stderr.strip()[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-ARCH-MODEL",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=610,
    )


def make_precommit_id_uniqueness_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-ID-UNIQ post-commit 兜底 reconciler（治本改进点2）。

    GATE-ID-UNIQ (pre-commit hook id 唯一性) 被 GitCommitGateway 的 --no-verify
    系统性绕过（机制层病根，与 GATE-15-ttl / GATE-REG-BL 同根：post-commit 补偿层）。
    本 reconciler 在 post-commit 跑 check_precommit_id_uniqueness.py --ci 重校，
    检测到 same-repo 重复 id 则记录违规报告供追责（commit 已入历史，非阻断——
    与 make_ttl_reconciler 一致的设计裁定）。

    设计裁定（非阻断）：
    post-commit 无法回滚 commit；same-repo 重复 id 已入 git 历史，仅告警记录到
    .runtime/reconcile_reports/id_uniqueness_<ts>.json，供 ide_health_daemon +
    人工追责 + 后续修复（git revert 或 amend）。双层防御：pre-commit GATE-ID-UNIQ
    阻断 + post-commit reconciler 兜底 --no-verify 绕过场景。

    向内收设计（三原则审核）：
    - 责任唯一：检测逻辑只在 check_precommit_id_uniqueness.py 一处（pre-commit
      hook 与本 reconciler 共用同一脚本，无第二检测实现）
    - 真源唯一：复用 ReconciliationRegistry 框架（第8个 reconciler），不新建兜底系统；
      复用 make_ttl_reconciler 的"post-commit 重校 + 报告落盘 + 非阻断"模式
    - 向内收：扩展 ``_register_default_reconcilers`` 一行，不改 gateway 方法体

    trigger 裁定：committed_files 含 ``.pre-commit-config.yaml`` 即命中
    （该文件是 GATE-ID-UNIQ 的唯一校验对象，与 pre-commit hook 的 files 正则一致）。

    Args:
        gateway: GitCommitGateway 实例（用 project_root，类型注解 object
            保持本纯 stdlib 模块不 import zephyr.*）。

    Returns:
        ReconcilerSpec(gate_id="GATE-ID-UNIQ", priority=250)。
    """
    import json
    import os
    import subprocess
    import sys
    import time

    project_root = gateway.project_root
    _CONFIG_REL = ".pre-commit-config.yaml"
    _CHECK_SCRIPT = "scripts/governance/d5_architecture/checkers/check_precommit_id_uniqueness.py"

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel == _CONFIG_REL:
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. post-commit 重校（脚本内部读 CONFIG_PATH = REPO_ROOT/.pre-commit-config.yaml，
        #    不接受文件参；--ci 硬阻断语义在 post-commit 退化为非阻断——exit 1 仅作信号）
        scan_result = subprocess.run(
            [sys.executable, _CHECK_SCRIPT, "--ci"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        # 2. 报告落盘
        report = {
            "gate_id": "GATE-ID-UNIQ",
            "session_id": session_id,
            "exit_code": scan_result.returncode,
            "checked_file": _CONFIG_REL,
            "stdout_tail": scan_result.stdout.strip()[-500:],
            "stderr_tail": scan_result.stderr.strip()[-500:],
        }
        report_path, write_err = _write_reconcile_report(project_root, "id_uniqueness", report)
        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"id_uniqueness scan done (exit={scan_result.returncode}) but report write failed: {write_err}",
            )
        # 3. 判定（exit 0 = clean；exit 1 = same-repo 重复 id 检出；exit 2 = 脚本异常）
        if scan_result.returncode == 0:
            return ReconcileResult(
                action="clean",
                detail=f"id_uniqueness scan clean, report={report_path.name}",
            )
        return ReconcileResult(
            action="warn",
            detail=f"id_uniqueness scan detected violations (exit={scan_result.returncode}), report={report_path.name}",
        )

    return ReconcilerSpec(
        gate_id="GATE-ID-UNIQ",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=250,
    )


def make_vocab_change_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-VOCAB-CHANGE post-commit reconciler（词表变更自动纠偏）。

    当 ttl_vocabulary.yaml 的 decision_tree 变更时，自动重判所有 docs/*.md 的 ttl，
    修正不一致的值并自动提交（治本：词表变更后 ttl 漂移自动纠偏，无需手动跑 backfill）。

    对账链：
    1. trigger: committed_files 含 ttl_vocabulary.yaml → 命中
    2. 调用 backfill_ttl_metadata.py --rejudge 重判所有 docs/*.md 的 ttl
    3. git diff 检测 docs/ 下 .md 变更 → 无变更返回 clean
    4. 有变更 → git add + git commit --no-verify（斩断循环）

    设计依据：trae_060 治本方案——decision_tree 机器可读化后，词表变更应自动传播到
    所有 .md 文件的 ttl 字段，消除手动 backfill 漂移风险。reconciler 优先级 280
    （在 GATE-15-ttl 300 之前执行，确保 ttl 校验前 ttl 值已纠偏）。

    Args:
        gateway: GitCommitGateway 实例（用 project_root + _run_git）。

    Returns:
        ReconcilerSpec(gate_id="GATE-VOCAB-CHANGE", priority=280)。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root
    _VOCAB_REL = (
        "docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml"
    )

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel == _VOCAB_REL:
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 重判所有 docs/*.md 的 ttl（--rejudge 模式重判已有 ttl 的文件）
        rejudge_result = subprocess.run(
            [sys.executable,
             "scripts/governance/d3_metadata/backfill_ttl_metadata.py", "--rejudge"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,  # 5175 文件重判需要较长时间
        )
        if rejudge_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"ttl rejudge failed (exit={rejudge_result.returncode}): "
                       f"{rejudge_result.stderr.strip()[:200]}",
            )

        # 2. 检测 docs/ 下 .md 变更（reconciler 执行时工作区只有本次修改，
        #    其他 session 修改已被 stash 隔离）
        #    只提交 .md 变更——reconciler 目的是重判 docs/*.md 的 ttl（docstring 明确）；
        #    .yaml/.json 等规则文件的 body section 变更不应由 reconciler 代提交
        #    （防御 backfill_ttl_metadata.py 误改 rules/*.yaml 的 body section，
        #     2026-06-30 红蓝对抗修复：曾因无 .md 过滤误删 trae_001 ttl_design section）
        diff_result = gateway._run_git(
            ["git", "diff", "--name-only", "--", "docs/"]
        )
        if diff_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"git diff failed: {diff_result.stderr.strip()[:200]}",
            )
        changed_files = [
            f.strip() for f in diff_result.stdout.strip().splitlines()
            if f.strip() and f.strip().endswith(".md")
        ]
        if not changed_files:
            return ReconcileResult(
                action="clean",
                detail="ttl rejudge: no drift detected (all ttl consistent)",
            )

        # 3. 变更 → 自动提交修复（--no-verify 斩断 pre-commit 循环）
        add_result = gateway._run_git(["git", "add", "--"] + changed_files)
        if add_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"git add rejudge changes failed: "
                       f"{add_result.stderr.strip()[:200]}",
            )

        auto_msg = (
            f"chore(ttl): auto-rejudge by GATE-VOCAB-CHANGE post-commit "
            f"(decision_tree changed) [GW:{session_id}:auto]"
        )
        commit_result = gateway._run_git(
            ["git", "commit", "--no-verify", "-m", auto_msg, "--"] + changed_files
        )
        if commit_result.returncode == 0:
            return ReconcileResult(
                action="auto_committed",
                detail=f"ttl rejudge: {len(changed_files)} files auto-reconciled",
            )
        return ReconcileResult(
            action="warn",
            detail=f"ttl rejudge: auto-commit failed: "
                   f"{commit_result.stderr.strip()[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-VOCAB-CHANGE",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=280,
    )


def make_rules_integrity_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-RULES-INTEGRITY post-commit 基线自动同步 reconciler（红蓝发现1 治本）。

    根因（红蓝发现1 P0）：
    ``rules_integrity_db.json``（C 层 golden hash 基线）不被 git 跟踪，合法 commit
    修改 RULES_MANIFEST 文件后本地基线不自动更新 → 下次 ``--check`` 误报 TAMPERED
    → 阻断裸 git commit（pre-commit gate-rules-integrity hook 触发）。这是 C 层基线
    与 commit 不同步的结构性缺陷。

    治本（事件驱动自动同步）：
    commit 涉及 RULES_MANIFEST 任一文件后，post-commit 自动跑
    ``validate_rules_integrity.py --register`` 重算全部 RULES_MANIFEST 文件 hash
    并写入本地基线。合法 commit 通过 gateway 时 A 层 AST 锚点校验已先行通过
    （红蓝发现2 治本：空桩绕过已堵），故 post-commit 重注册的基线是"已验证合法"
    的状态——消除 C 层误报，同时不削弱篡改检测能力。

    RULES_MANIFEST 真源为 ``validate_rules_integrity.py`` 顶部的列表（SSoT）。本
    reconciler 的 trigger 总是返回 True（每次 commit 都 --register）。第一性原理：
    trigger 的价值是避免不必要的 --register（性能优化），但 --register 仅 hash
    RULES_MANIFEST 文件（毫秒级），远小于 commit 开销；而宽匹配（路径前缀判断）
    基于"RULES_MANIFEST 全在 governance 下"的未校验假设，未来新增其他路径文件会
    假阴性漏触发且无告警 → 基线不同步 → 误报 TAMPERED。性能收益不值得假设漂移风险，
    治本：总是触发，消除假设。

    非阻断设计：--register 仅写本地非跟踪文件，exit 0 即基线已更新；失败降级 warn
    （报告落盘供追责）。priority 270（在 GATE-ID-UNIQ 250 之后、GATE-VOCAB-CHANGE
    280 之前），确保其他可能修改 RULES_MANIFEST 文件的 reconciler（如 manifest pri 100
    会 auto-commit script_manifest.yaml）先完成，再统一重注册基线。

    Args:
        gateway: GitCommitGateway 实例（用 project_root，类型注解 object
            保持本纯 stdlib 模块不 import zephyr.*）。

    Returns:
        ReconcilerSpec(gate_id="GATE-RULES-INTEGRITY", priority=270)。
    """
    import json
    import os
    import subprocess
    import sys
    import time

    project_root = gateway.project_root
    _VALIDATE_SCRIPT = "scripts/governance/meta/validate_rules_integrity.py"

    def _trigger(committed_files: list[str]) -> bool:
        # 第一性原理治本：总是触发。原宽匹配（AGENTS.md | scripts/governance/ 前缀）
        # 基于未校验假设，未来 RULES_MANIFEST 新增其他路径文件会假阴性漏触发。
        # --register 仅 hash RULES_MANIFEST 文件（毫秒级），不值得为省此开销引入假设。
        # RULES_MANIFEST 真源在 validate_rules_integrity.py 顶部。
        return True

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. post-commit 重注册基线（--register 内部读 RULES_MANIFEST 真源，重算全部 hash）
        # 红蓝发现4 治本：设置 ZEPHYR_RECONCILER_MODE=1 门禁令牌，允许 --register。
        # validate_rules_integrity.py --register 检查此变量，手动调用不设置 → 阻断。
        _env = dict(os.environ)
        _env["ZEPHYR_RECONCILER_MODE"] = "1"
        reg_result = subprocess.run(
            [sys.executable, _VALIDATE_SCRIPT, "--register"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            env=_env,
        )
        # 2. 报告落盘（无论 exit code，记录供追责）
        report = {
            "gate_id": "GATE-RULES-INTEGRITY",
            "session_id": session_id,
            "exit_code": reg_result.returncode,
            "stdout_tail": reg_result.stdout.strip()[-500:],
            "stderr_tail": reg_result.stderr.strip()[-500:],
            "triggered_by": committed_files,
        }
        report_path, write_err = _write_reconcile_report(project_root, "rules_integrity", report)
        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"rules_integrity --register done (exit={reg_result.returncode}) "
                       f"but report write failed: {write_err}",
            )
        # 3. 判定（--register exit 0 = 基线已更新；非 0 = 脚本异常）
        if reg_result.returncode == 0:
            return ReconcileResult(
                action="auto_committed",
                detail=f"rules_integrity baseline re-registered post-commit "
                       f"(C层基线已同步合法 commit), report={report_path.name}",
            )
        return ReconcileResult(
            action="warn",
            detail=f"rules_integrity --register failed (exit={reg_result.returncode}), "
                   f"report={report_path.name}",
        )

    return ReconcilerSpec(
        gate_id="GATE-RULES-INTEGRITY",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=270,
    )


def make_commit_gateway_audit_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-COMMIT-GW-AUDIT post-commit 审计 reconciler（C级 缺口4）。

    扫描最近 N 个 commit，标记未经 GitCommitGateway 的裸 commit（message 不含
    ``[GW:`` 标记）。双层防御：pre-commit GATE-COMMIT-GW 阻断裸 commit +
    post-commit 审计兜底 ``--no-verify`` 绕过场景。

    设计裁定（非阻断）：
    post-commit 无法回滚 commit；裸 commit 已入 git 历史，仅告警记录到
    ``.runtime/reconcile_reports/commit_gateway_audit_<ts>.json``，供追责。
    与 make_precommit_id_uniqueness_reconciler 一致的"post-compensation 非阻断"模式。

    trigger 裁定：always True（第一性原理：绕过 gateway 的裸 commit 可能涉及任何
    文件，无法用文件前缀限定；审计扫描 git log 是毫秒级，不值得为省此开销引入
    路径假设）。reconciler 仅在 ``commit()``（用户提交）后触发，
    ``_commit_auto``（reconciler 自动提交）不触发 reconcile_for，无递归风险。

    审计窗口裁定：最近 20 个 commit（覆盖一次开发会话的提交密度，平衡召回率与
    噪音）。merge commit 跳过（合并提交无作者意图，非裸 commit 范畴）。

    向内收设计（三原则审核）：
    - 责任唯一：检测逻辑只在 validate_commit_gateway.py 一处（pre-commit hook
      与本 reconciler 共用同一 GW 标记判定语义 ``[GW:``）
    - 真源唯一：复用 ReconciliationRegistry 框架（第 11 个 reconciler），不新建
      兜底系统；复用 _write_reconcile_report 报告落盘
    - 向内收：扩展 ``_register_default_reconcilers`` 一行，不改 gateway 方法体

    Args:
        gateway: GitCommitGateway 实例（用 project_root，类型注解 object
            保持本纯 stdlib 模块不 import zephyr.*）。

    Returns:
        ReconcilerSpec(gate_id="GATE-COMMIT-GW-AUDIT", priority=800)。
    """
    import os
    import subprocess

    project_root = gateway.project_root
    _AUDIT_WINDOW = 20  # 审计最近 20 个 commit
    _GW_MARKER = "[GW:"

    def _trigger(committed_files: list[str]) -> bool:
        # 审计始终运行：绕过 gateway 的裸 commit 可能涉及任何文件
        return True

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 扫描最近 N 个 commit（--oneline 快速扫描 subject）
        log_result = subprocess.run(
            ["git", "log", f"-{_AUDIT_WINDOW}", "--oneline"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        if log_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"git log failed: {log_result.stderr.strip()[:200]}",
            )

        # 2. 解析，标记无 [GW: 标记的 commit（跳过 merge commit）
        #    两阶段检查：subject 快速扫描 + body 二次确认
        #    （GitCommitGateway.commit() 把 [GW:tag] 追加到 message 末尾用 \n\n 分隔，
        #     --oneline 只看 subject 会误判手动 commit 为裸 commit，需查 body）
        violations: list[dict] = []
        for line in log_result.stdout.strip().splitlines():
            # format: <hash> <subject>
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            commit_hash, subject = parts[0], parts[1]
            # 跳过 merge commit（合并提交无作者意图）
            if subject.startswith("Merge "):
                continue
            if _GW_MARKER in subject:
                continue  # subject 已含 [GW:（reconciler auto-commit）
            # subject 无 [GW: → 查 body（手动 commit 的 [GW:tag] 在 body 末尾）
            body_result = subprocess.run(
                ["git", "show", "-s", "--format=%B", commit_hash],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
            )
            if body_result.returncode == 0 and _GW_MARKER in body_result.stdout:
                continue  # body 含 [GW:（手动 commit 经 GitCommitGateway）
            violations.append({"hash": commit_hash, "subject": subject[:120]})

        # 3. 报告落盘
        report = {
            "gate_id": "GATE-COMMIT-GW-AUDIT",
            "session_id": session_id,
            "audit_window": _AUDIT_WINDOW,
            "violations_count": len(violations),
            "violations": violations,
        }
        report_path, write_err = _write_reconcile_report(
            project_root, "commit_gateway_audit", report
        )
        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"audit done ({len(violations)} violations) but report write failed: {write_err}",
            )

        # 4. 判定（非阻断：commit 已入历史，仅告警）
        if not violations:
            return ReconcileResult(
                action="clean",
                detail=f"audit clean (window={_AUDIT_WINDOW}), report={report_path.name}",
            )
        return ReconcileResult(
            action="warn",
            detail=f"audit detected {len(violations)} non-GW commits (window={_AUDIT_WINDOW}), report={report_path.name}",
        )

    return ReconcilerSpec(
        gate_id="GATE-COMMIT-GW-AUDIT",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=800,  # 最后执行（审计非阻断，低优先级）
    )


def make_deprecated_directory_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-DEPRECATED-DIR post-commit reconciler（09_audit 治本加固）。

    扫描 docs/ 下是否存在已废弃目录（如 09_audit/），存在则告警。
    双层防御：GitCommitGateway._check_deprecated_directories 阻断提交 +
    post-commit reconciler 兜底 mkdir 但未提交的场景（如脚本 mkdir 后未 commit）。

    设计裁定（非阻断）：
    post-commit 无法回滚已提交内容；废弃目录可能是脚本 mkdir 的副作用（未 commit），
    仅告警记录到 ``.runtime/reconcile_reports/deprecated_directory_<ts>.json``。

    trigger 裁定：always True（废弃目录可能由任何脚本 mkdir 重建，与 commit 文件无关）。

    向内收设计：
    - 复用 ReconciliationRegistry 框架，不新建兜底系统
    - 废弃目录清单复用 GitCommitGateway._DEPRECATED_DIRS（通过 gateway 引用，不复制）
    - 复用 _write_reconcile_report 报告落盘

    Args:
        gateway: GitCommitGateway 实例（用 project_root + _DEPRECATED_DIRS）。

    Returns:
        ReconcilerSpec(gate_id="GATE-DEPRECATED-DIR", priority=600)。
    """
    project_root = gateway.project_root
    # 复用 gateway 的废弃目录清单（真源唯一，不复制）
    deprecated_dirs: dict[str, str] = getattr(gateway, "_DEPRECATED_DIRS", {})

    def _trigger(committed_files: list[str]) -> bool:
        # 始终检测：脚本可能 mkdir 但未 commit（如 session_continuity 的 handoff 写入）
        return True

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        """自动修复：迁移废弃目录内容到合规目录 + 删除空目录。

        治本策略（非 warn-only）：
        - 空目录 → 直接 rmdir → action=clean
        - 非空目录 → shutil.move 迁移到 docs/_working/audit/（不覆盖已有文件）
          → rmdir 空目录 → action=warn（迁移的文件需人工 commit）
        - 部分失败 → action=warn

        消灭"只告警不消除"——无论脚本如何 mkdir，下一次 commit 后自动清理。
        """
        import shutil  # 局部导入（避免模块级依赖膨胀）
        import os
        from pathlib import Path

        # 合规目标目录：docs/09_audit/ → docs/_working/audit/
        _COMPLIANT_MAP: dict[str, str] = {
            "docs/09_audit": "docs/_working/audit",
        }

        violations: list[dict] = []
        for dep_dir, reason in deprecated_dirs.items():
            dep_path = project_root / dep_dir
            if not (dep_path.exists() and dep_path.is_dir()):
                continue

            # 收集所有文件（不含目录本身）
            items = [p for p in dep_path.rglob("*") if p.is_file()]

            # 自动迁移：将文件迁移到合规目录（不覆盖已有文件）
            target_base_rel = _COMPLIANT_MAP.get(dep_dir, dep_dir.replace("09_audit", "_working/audit"))
            target_base = project_root / target_base_rel
            migrated: list[dict] = []
            for item in items:
                rel_to_dep = item.relative_to(dep_path)
                target = target_base / rel_to_dep
                src_rel = str(item.relative_to(project_root)).replace("\\", "/")
                dst_rel = str(target.relative_to(project_root)).replace("\\", "/")
                if target.exists():
                    migrated.append({"src": src_rel, "dst": dst_rel, "status": "skipped_exists"})
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(item), str(target))
                    migrated.append({"src": src_rel, "dst": dst_rel, "status": "moved"})

            # 删除空目录（从最深层开始，bottom-up）
            removed_dirs: list[str] = []
            for root, _dirs, _files in os.walk(dep_path, topdown=False):
                try:
                    if not os.listdir(root):
                        os.rmdir(root)
                        removed_dirs.append(
                            str(Path(root).relative_to(project_root)).replace("\\", "/")
                        )
                except OSError:
                    pass  # 目录非空或权限不足，跳过

            still_exists = dep_path.exists()
            moved_count = sum(1 for m in migrated if m["status"] == "moved")
            violations.append({
                "deprecated_dir": dep_dir,
                "reason": reason,
                "item_count": len(items),
                "migrated": migrated,
                "moved_count": moved_count,
                "removed_dirs": removed_dirs,
                "dir_removed": not still_exists,
            })

        report = {
            "gate_id": "GATE-DEPRECATED-DIR",
            "session_id": session_id,
            "violations_count": len(violations),
            "violations": violations,
        }
        report_path, write_err = _write_reconcile_report(
            project_root, "deprecated_directory", report
        )
        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"scan done ({len(violations)} violations) but report write failed: {write_err}",
            )

        if not violations:
            return ReconcileResult(
                action="clean",
                detail=f"no deprecated directories found, report={report_path.name}",
            )

        all_removed = all(v.get("dir_removed") for v in violations)
        total_moved = sum(v.get("moved_count", 0) for v in violations)

        if all_removed and total_moved == 0:
            # 空目录已自动删除——彻底消灭
            return ReconcileResult(
                action="clean",
                detail=f"auto-removed {len(violations)} empty deprecated directories, report={report_path.name}",
            )
        elif all_removed and total_moved > 0:
            # 文件已迁移 + 目录已删除，迁移的文件待 commit
            return ReconcileResult(
                action="warn",
                detail=f"auto-migrated {total_moved} files to docs/_working/audit/ and removed deprecated dirs (commit migrated files), report={report_path.name}",
            )
        else:
            return ReconcileResult(
                action="warn",
                detail=f"partial remediation ({len(violations)} violations, some dirs remain), report={report_path.name}",
            )

    return ReconcilerSpec(
        gate_id="GATE-DEPRECATED-DIR",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=600,  # 中等优先级（非阻断，但需要及时发现）
    )


# ============================================================
# 缺口2/3 共享辅助（规则文件审计 + 豁免区 frontmatter 检测）
# 提取到模块级避免两个 reconciler 重复定义（向内收原则）
# ============================================================
_RULE_FILE_PATHS = (
    "docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml",
    "docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml",
    "docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml",
    "docs/01_policies_and_standards/_registry/contracts/architecture_contract.yaml",
    "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml",
)
_EXEMPT_ZONE_PREFIXES = (
    "docs/_working/",
    "docs/_archive/",
    ".runtime/",
    ".trae/",
    "docs/01_policies_and_standards/templates/",
)
_FRONTMATTER_EXTS = (".md", ".yaml", ".yml")


def _rel_path(f: str, project_root_str: str) -> str:
    """文件路径归一化：os.path.relpath + replace("\\", "/")。"""
    import os
    return os.path.relpath(f, project_root_str).replace("\\", "/")


def _extract_doc_type(content: str, is_markdown: bool) -> str:
    """从 frontmatter 提取 doc_type 值；无 frontmatter/doc_type 返回空串。

    frontmatter 判定：首行以 ``---`` 开头。.md 取 ``---`` 之间的块；
    .yaml/.yml 取首行 ``---`` 之后的全部内容（YAML document start marker）。
    doc_type 仅识别内联形式 ``doc_type: <value>``（最常见，块形式不识别——
    原型启发式，非完整 YAML 解析，避免引入非 stdlib yaml 依赖）。
    """
    lines = content.splitlines()
    if not lines or not lines[0].lstrip().startswith("---"):
        return ""
    if is_markdown:
        block: list[str] = []
        closed = False
        for line in lines[1:]:
            if line.lstrip().startswith("---"):
                closed = True
                break
            block.append(line)
        if not closed:
            return ""
    else:
        block = lines[1:]
    for line in block:
        stripped = line.strip()
        if ":" not in stripped:
            continue
        key, _, val = stripped.partition(":")
        if key.strip() != "doc_type":
            continue
        val = val.strip()
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            val = val[1:-1]
        if " #" in val:
            val = val.split(" #", 1)[0].strip()
        return val
    return ""


def make_rule_file_audit_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-RULE-FILE-AUDIT post-commit 审计 reconciler（缺口3：规则文件变更审计）。

    治本动机：directory_contract / doc_type_vocabulary / ttl_vocabulary /
    architecture_contract / gate_registry 等治理真源被修改后无 post-commit
    兜底告警，可能被悄悄放宽约束。本 reconciler 落盘审计记录，提示人工审查。

    P0 修复（2026-06-30）：原设计此函数同时承担缺口2（豁免区 frontmatter 检测），
    但两者共用一个 trigger（只检测规则文件变更），导致缺口2成死代码——单独提交
    豁免区文件时 trigger 不命中，缺口2检测永不执行。现已将缺口2拆分到独立的
    make_exempt_zone_frontmatter_reconciler，trigger 改为检测豁免区文件。

    priority=700（审计非阻断，post-compensation 层）。
    """
    import json
    import os
    from datetime import datetime

    project_root = gateway.project_root
    _project_root_str = str(project_root)
    _rule_set = set(_RULE_FILE_PATHS)

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            if _rel_path(f, _project_root_str) in _rule_set:
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        rule_files_changed = [
            _rel_path(f, _project_root_str)
            for f in committed_files
            if _rel_path(f, _project_root_str) in _rule_set
        ]

        reports_dir = os.path.join(_project_root_str, ".runtime", "reconcile_reports")
        os.makedirs(reports_dir, exist_ok=True)
        ts_iso = datetime.now().isoformat(timespec="seconds")
        ts_file = ts_iso.replace(":", "")
        report = {
            "timestamp": ts_iso,
            "session_id": session_id,
            "rule_files_changed": rule_files_changed,
            "note": "规则文件变更需人工审查（约束可能被放宽）",
        }
        report_path = os.path.join(reports_dir, f"rule_file_audit_{ts_file}.json")
        try:
            with open(report_path, "w", encoding="utf-8") as fh:
                json.dump(report, fh, ensure_ascii=False, indent=2)
        except OSError as e:
            return ReconcileResult(
                action="warn",
                detail=f"rule-file audit done ({len(rule_files_changed)} file(s)) but report write failed: {e}",
            )

        return ReconcileResult(
            action="warn",
            detail=(
                f"{len(rule_files_changed)} rule file(s) changed "
                f"(manual review recommended), report={os.path.basename(report_path)}"
            ),
        )

    return ReconcilerSpec(
        gate_id="GATE-RULE-FILE-AUDIT",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=700,
    )


def make_exempt_zone_frontmatter_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-EXEMPT-ZONE-FM post-commit reconciler（缺口2：豁免区 frontmatter 检测）。

    治本动机：docs/_working/ / docs/_archive/ / .runtime/ / .trae/ / templates/
    五类豁免前缀不受 DCR-001/002 frontmatter 校验约束。若豁免区文件带
    frontmatter + 非空 doc_type，说明本应放正式目录却被塞进豁免区。

    P0 修复（2026-06-30）：原设计此检测与规则文件审计共用 trigger（只在规则文件
    变更时才触发），导致单独提交豁免区文件时检测永不执行（死代码）。现拆分为
    独立 reconciler，trigger 改为检测豁免区文件被提交。

    priority=710（在 GATE-RULE-FILE-AUDIT 700 之后）。
    """
    import json
    import os
    from datetime import datetime
    from pathlib import Path

    project_root = gateway.project_root
    _project_root_str = str(project_root)

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = _rel_path(f, _project_root_str)
            for zone in _EXEMPT_ZONE_PREFIXES:
                if rel.startswith(zone):
                    return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        exempt_zone_frontmatter_files: list[dict] = []
        for f in committed_files:
            rel = _rel_path(f, _project_root_str)
            matched_zone = ""
            for zone in _EXEMPT_ZONE_PREFIXES:
                if rel.startswith(zone):
                    matched_zone = zone
                    break
            if not matched_zone:
                continue
            if not rel.endswith(_FRONTMATTER_EXTS):
                continue
            abs_path = Path(_project_root_str) / rel
            try:
                content = abs_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            doc_type = _extract_doc_type(content, rel.endswith(".md"))
            if doc_type:
                exempt_zone_frontmatter_files.append({
                    "file": rel,
                    "doc_type": doc_type,
                    "exempt_zone": matched_zone,
                })

        if not exempt_zone_frontmatter_files:
            return ReconcileResult(action="clean", detail="no exempt-zone frontmatter files")

        reports_dir = os.path.join(_project_root_str, ".runtime", "reconcile_reports")
        os.makedirs(reports_dir, exist_ok=True)
        ts_iso = datetime.now().isoformat(timespec="seconds")
        ts_file = ts_iso.replace(":", "")
        report = {
            "timestamp": ts_iso,
            "session_id": session_id,
            "exempt_zone_frontmatter_files": exempt_zone_frontmatter_files,
            "note": "豁免区下有 frontmatter 的文件不受 DCR-001/002 约束，请确认是否应迁移到正式目录",
        }
        report_path = os.path.join(reports_dir, f"exempt_zone_fm_{ts_file}.json")
        try:
            with open(report_path, "w", encoding="utf-8") as fh:
                json.dump(report, fh, ensure_ascii=False, indent=2)
        except OSError as e:
            return ReconcileResult(
                action="warn",
                detail=f"exempt-zone audit done ({len(exempt_zone_frontmatter_files)} file(s)) but report write failed: {e}",
            )

        return ReconcileResult(
            action="warn",
            detail=(
                f"{len(exempt_zone_frontmatter_files)} exempt-zone frontmatter file(s) "
                f"detected (manual review recommended), report={os.path.basename(report_path)}"
            ),
        )

    return ReconcilerSpec(
        gate_id="GATE-EXEMPT-ZONE-FM",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=710,
    )
