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
        # 1. post-commit 增量 baseline-aware 扫描（非阻断）
        scan_result = subprocess.run(
            [sys.executable, "scripts/governance/audit_registration.py",
             "--incremental", "--baseline-aware"],
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
