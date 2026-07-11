# [BLUEPRINT] MOD-INF-035 | .trae/documents/systemic_drift_root_cure_continuation_plan.md | §4 P2-T1
# [MODULE] zephyr.governance.audit.reconciliation_registry
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] (none — pure stdlib)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] ReconciliationRegistry.register 幂等（同 gate_id 覆盖旧 spec）；reconcile_for 按 priority 升序执行命中 trigger 的 reconciler；reconciler 异常被捕获为 warn 结果（不阻断后续 reconciler）
# [MODIFY-GUARD] ReconcilerSpec 字段结构；ReconcileResult.action 枚举语义
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile_for 永不抛异常——单个 reconciler 异常降级为 ReconcileResult(action="warn")
# [TESTS] tests/test_reconciliation_registry.py (P3-T1)
# [A_module] module_id=MOD-GOV-reconciliation_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
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

    from zephyr.governance.audit.reconciliation_registry import (
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
import subprocess
from dataclasses import dataclass, field
from typing import Callable
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__ = [
    "ReconcileResult",
    "ReconcilerSpec",
    "ReconciliationRegistry",
    "make_manifest_reconciler",
    "make_path_tree_reconciler",
    "make_path_ownership_reconciler",
    "make_depgraph_ops_reconciler",
    "make_yaml_sync_reconciler",
    "make_precommit_id_uniqueness_reconciler",
    "make_vocab_change_reconciler",
    "make_deprecated_directory_reconciler",
    "make_exempt_zone_frontmatter_reconciler",
    "make_delete_audit_reconciler",
    "make_regenerate_reconciler",
    "make_rule_audit_reconciler",
    "make_registry_sync_reconciler",
    "make_integrity_audit_reconciler",
    "make_module_id_consistency_reconciler",
    "make_index_generator_reconciler",
    "make_runtime_cleanup_reconciler",
    "make_architecture_health_reconciler",
    "make_session_log_index_reconciler",
    "make_arch_diagram_reconciler",
    "make_gate_inventory_sync_reconciler",
    "scan_and_archive_working_docs",
]


# 5.59.5 修复：统一 subprocess 解码策略
# 病根：reconciler 中 subprocess.run 调用散落 24 处，解码策略不一致（部分 strict、
# 部分 errors="replace"），含非 UTF-8 字符的子进程输出在 strict 模式下抛
# UnicodeDecodeError 导致 reconciler 降级失败。封装统一入口确保 errors="replace"。
def _run_subprocess(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """5.59.5 修复：统一 subprocess 解码策略，使用 errors='replace' 避免非 UTF-8 字符抛 UnicodeDecodeError。"""
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    kwargs.setdefault("errors", "replace")
    return subprocess.run(cmd, **kwargs)


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
            except (Exception, KeyboardInterrupt) as e:  # noqa: BLE001 — drift 对账非阻断；KeyboardInterrupt 也降级（commit 已入库，reconciler 中断不应 crash 进程，治本 #2026-0701）
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
        return None, "internal error"


def make_manifest_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-19 manifest post-commit 对账 reconciler（P2-T2）。

    把原 ``GitCommitGateway._post_commit_reconcile`` 逻辑迁移为独立 ReconcilerSpec，
    注册到 ReconciliationRegistry。闭包捕获 gateway 实例以复用 ``project_root``
    与 ``_run_git``。

    对账链（与迁移前行为等价）：
    1. trigger: committed_files 含 scripts/ 下 .py -> 命中
    2. 重生成 scripts/script_manifest.yaml（generate_manifest.py os.walk 全树 SSoT）
    3. git diff 检测 manifest 变更 -> 无变更返回 clean
    4. 有变更 -> git add + git commit --no-verify（斩断 zombie 引用循环）

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
        gen_result = _run_subprocess(
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

        # 3. 变更 -> 自动提交修复（经 _commit_auto 统一入口，DCR gate 覆盖）
        # 治本（2026-06-30）：原裸调 _run_git commit 绕过 DCR gate，改为走 _commit_auto
        # 统一入口，ttl/deprecated/pure_assertion/pure_shim/DCR 五重 gate 覆盖。
        auto_msg = "chore(manifest): auto-reconcile by GitCommitGateway post-commit"
        abs_files = [str(project_root / "scripts/script_manifest.yaml")]
        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)
        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="manifest drift detected and auto-reconciled",
            )
        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="manifest no drift (auto-commit found no staged changes)",
            )
        return ReconcileResult(
            action="warn",
            detail=f"manifest drift detected, auto-commit failed ({commit_result.status}): "
                   f"{commit_result.message[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-19-manifest",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=100,
    )


def make_path_tree_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 arch_directory_tree post-commit 自动同步 reconciler。

    commit .py/.yaml 文件后，depgraph 的 arch_directory_tree 表可能过时
    （磁盘文件结构变了但 DB 未同步）。本 reconciler 在 post-commit 跑
    generate_project_path_tree.py --write 同步磁盘->DB，如有变更自动提交。

    对标 make_manifest_reconciler 的"检测变更->自动提交"模式。
    替代原 pre-commit GATE-SYNC-PATH-TREE hook（该 hook 有原 depgraph.db（SQLite）
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
        sync_result = _run_subprocess(
            [sys.executable, "scripts/governance/generate_project_path_tree.py", "--write"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,  # 止血：60->120（项目规模 10k+ 目录逼近 60s 预算；治本见 generate_path_tree.py 性能优化任务）
        )
        if sync_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"path_tree sync failed: {sync_result.stderr.strip()[:200]}",
            )
        # 串联调用 d5 generate_path_tree.py 生成架构文档 md（治本 trae_060 §5）
        # 读 depgraph arch_directory_tree -> 生成 md 文档供人类查看
        doc_result = _run_subprocess(
            [sys.executable, "scripts/governance/d5_architecture/generators/generate_path_tree.py"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,  # 止血：60->120（项目规模 10k+ 目录逼近 60s 预算；治本见 generate_path_tree.py 性能优化任务）
        )
        if doc_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"path_tree sync OK but doc gen failed: {doc_result.stderr.strip()[:150]}",
            )
        # 4. 检测 full_project_tree 文档变更 -> 自动提交（治本 post-commit 循环）
        # 病根：原实现生成 md 后返回 action="clean" 不自动提交，导致每次 commit 后
        # full_project_tree_en/zh.md 变成 modified 残留（post-commit 循环）。
        # 治本：对标 make_manifest_reconciler line 277-304，检测变更->_commit_auto 自动提交。
        _tree_files = [
            "docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_en.md",
            "docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_zh.md",
        ]
        _diff_result = gateway._run_git(
            ["git", "diff", "--name-only", "--"] + _tree_files
        )
        if _diff_result.returncode == 0 and not _diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="arch_directory_tree synced + path doc up to date")
        # 变更 -> 自动提交（_commit_auto 不触发 reconciler，无循环风险）
        _auto_msg = "chore(path-tree): auto-reconcile full_project_tree by GitCommitGateway post-commit"
        _abs_files = [str(project_root / f) for f in _tree_files]
        _commit_result = gateway._commit_auto(session_id, _abs_files, _auto_msg)
        if _commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="arch_directory_tree synced + path doc regenerated and auto-committed",
            )
        if _commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="arch_directory_tree synced + path doc no drift (auto-commit found no staged changes)",
            )
        return ReconcileResult(
            action="warn",
            detail=f"path doc drift detected, auto-commit failed ({_commit_result.status}): "
                   f"{_commit_result.message[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-PATH-TREE",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=150,
    )


# trae_060-reviewed: 合规——新增 reconciler（无法合并进已有：path_tree 触发 .py/.yaml，path_ownership 触发 blueprint.md，生成器不同；治本：path_ownership_map.yaml 自动同步消除手工维护漂移）
def make_path_ownership_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 path_ownership_map.yaml post-commit 自动同步 reconciler。

    commit docs/03_modules/**/blueprint.md 后，path_ownership_map.yaml 可能过时
    （蓝图 §0.1 文件清单变了但 ownership map 未同步）。本 reconciler 在 post-commit
    跑 generate_path_ownership_map.py --write 同步，如有变更自动提交。

    对标 make_path_tree_reconciler（arch_directory_tree 同步）的 subprocess 模式。
    区别：
    - 触发条件：仅 blueprint.md 变更（path_tree 触发 .py/.yaml）
    - 生成器：generate_path_ownership_map.py（path_tree 用 generate_project_path_tree.py）
    - 输出：docs/03_modules/path_ownership_map.yaml（path_tree 输出 full_project_tree.md）
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel.endswith("blueprint.md") and rel.startswith("docs/03_modules/"):
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        ownership_file = "docs/03_modules/path_ownership_map.yaml"
        # 1. 重新生成 path_ownership_map.yaml
        sync_result = _run_subprocess(
            [sys.executable, "scripts/governance/generators/generate_path_ownership_map.py", "--write"],
            cwd=str(project_root),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=60,
        )
        if sync_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"path_ownership sync failed: {sync_result.stderr.strip()[:200]}",
            )
        # 2. 检测 path_ownership_map.yaml 是否有变更
        diff_result = gateway._run_git(
            ["git", "diff", "--name-only", "--", ownership_file]
        )
        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="path_ownership_map.yaml up to date")
        # 3. 有变更 -> 自动提交
        abs_file = str(project_root / ownership_file)
        auto_msg = "chore(path-ownership): auto-reconcile path_ownership_map by GitCommitGateway post-commit"
        commit_result = gateway._commit_auto(session_id, [abs_file], auto_msg)
        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="path_ownership_map.yaml regenerated and auto-committed",
            )
        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="path_ownership_map.yaml no drift (auto-commit found no staged changes)",
            )
        return ReconcileResult(
            action="warn",
            detail=f"path_ownership_map.yaml drift detected, auto-commit failed ({commit_result.status}): "
                   f"{commit_result.message[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-PATH-OWNERSHIP",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=160,  # 在 path_tree(150) 之后
    )


def make_depgraph_ops_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 depgraph nodes/edges 运营态 post-commit 自动同步 reconciler（裁定#209）。

    commit .py 文件后，depgraph 的 nodes/edges 运营态表可能过时（代码变了但
    depgraph 未同步）。本 reconciler 在 post-commit 跑 generate_project_depgraph.py
    同步代码->DB。

    对标 make_path_tree_reconciler（arch_directory_tree 同步）的 subprocess 模式。
    区别：
    - trigger 只匹配 .py（不匹配 .yaml/.yml——避免改 depgraph 数据时触发自己）
    - reconcile 直接跑 --output-db --force（P1/P2 保护机制兜底，不覆盖手工字段）
    - 失败降级 warn，不阻断 commit
    - 无文档自动提交（nodes/edges 无人类可读 md 派生，由 design_vs_production 独立生成）

    阶段1（裁定#209）：全量扫描，每次 commit .py 都重跑。
    阶段3（裁定#209）：引入文件级 hash fingerprint 增量，降低频率成本。

    实弹验证（2026-07-02 R2）：干净环境重跑，确认 reconciler 全流程在无并发干扰下正常工作。

    Args:
        gateway: GitCommitGateway 实例（用 project_root）。

    Returns:
        ReconcilerSpec(gate_id="GATE-DEPGRAPH-OPS", priority=130)。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel.endswith(".py"):
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 全量同步代码->DB（P1/P2 保护机制兜底，不覆盖手工字段，详见 §14.2.1）
        import time
        start = time.time()
        sync_result = _run_subprocess(
            [
                sys.executable,
                "scripts/governance/generate_project_depgraph.py",
                "--output-db", "depgraph",
                "--force",
            ],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,  # 全量扫描，给足 5 分钟
        )
        elapsed = time.time() - start
        if sync_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"depgraph ops sync failed in {elapsed:.1f}s (rc={sync_result.returncode}): "
                       f"{sync_result.stderr.strip()[:200]}",
            )
        return ReconcileResult(
            action="clean",
            detail=f"depgraph nodes/edges synced in {elapsed:.1f}s "
                   f"(P1/P2 protection active, 裁定#209 阶段1)",
        )

    return ReconcilerSpec(
        gate_id="GATE-DEPGRAPH-OPS",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=130,
    )


def make_yaml_sync_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 YAML->depgraph 规则同步 post-commit reconciler。

    commit rules/*.yaml 或 _registry/**/*.yaml 后，depgraph 的规则缓存表
    （contracts/gates/field_vocabularies 等 16 张）可能与 YAML 真源漂移。
    本 reconciler 在 post-commit 跑 sync_yaml_to_depgraph.py 同步 YAML->DB。

    S1.6 重试队列：sync 失败时写入 data/cache/yaml_sync_retry_queue.json，
    后续任意 commit 自动重试（最多 _MAX_RETRY_ATTEMPTS=3 次），超过后升级为
    error 停止重试。AI 发现 error 级别告警时应检查 sync 脚本路径/依赖是否正确，
    而非自行创建新的同步逻辑（本 reconciler 是 YAML->DB 同步的唯一入口）。

    治本 trae_060 §5 "MUST 补事件注册"——消除手动 sync 导致的漂移
    （如 contracts 表 126 条外键违规的根因：AI 改 YAML 后忘记手动跑 sync）。

    Args:
        gateway: GitCommitGateway 实例（用 project_root）。

    Returns:
        ReconcilerSpec(gate_id="GATE-YAML-SYNC", priority=160)。
    """
    import json
    import os
    import subprocess
    import sys
    from datetime import UTC, datetime
    from pathlib import Path

    project_root = gateway.project_root
    # S1.6: 重试队列持久化路径（data/cache/ 已被 .gitignore）
    _RETRY_QUEUE_PATH = Path(project_root) / "data" / "cache" / "yaml_sync_retry_queue.json"
    _MAX_RETRY_ATTEMPTS = 3  # S1.6: 超过此次数后停止重试，升级为 error 防止无限循环

    def _read_retry_queue() -> dict | None:
        """读取重试队列。返回 None 表示无待重试项。"""
        if not _RETRY_QUEUE_PATH.exists():
            return None
        try:
            return json.loads(_RETRY_QUEUE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def _write_retry_queue(data: dict) -> None:
        """写入重试队列"""
        _RETRY_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _RETRY_QUEUE_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _clear_retry_queue() -> None:
        """清空重试队列"""
        if _RETRY_QUEUE_PATH.exists():
            _RETRY_QUEUE_PATH.unlink()

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if not rel.endswith((".yaml", ".yml")):
                continue
            # 规则文件变更触发
            if rel.startswith("docs/01_policies_and_standards/rules/"):
                return True
            # 注册表文件变更触发
            if rel.startswith("docs/01_policies_and_standards/_registry/"):
                return True
            # 资产真源文件变更触发（#180/#181/#182/#179）
            # architecture_model/data/*.yaml: 数据源资产 + 数据源 API
            # architecture_model/runtime/*.yaml: 服务资产
            # architecture_model/contracts/*.yaml: 契约资产
            # config/*.yaml: 配置项资产（文件系统扫描派生）
            if rel.startswith("architecture_model/data/"):
                return True
            if rel.startswith("architecture_model/runtime/"):
                return True
            if rel.startswith("architecture_model/contracts/"):
                return True
            if rel.startswith("config/"):
                return True
        # S1.6: 有待重试项时也触发，但超过最大重试次数后停止（防止无限循环）
        queue = _read_retry_queue()
        if queue is not None:
            if queue.get("attempt", 0) < _MAX_RETRY_ATTEMPTS:
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        sync_result = _run_subprocess(
            [sys.executable, "scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        if sync_result.returncode == 0:
            # S1.6: 成功->清空重试队列
            _clear_retry_queue()
            return ReconcileResult(
                action="clean",
                detail="YAML->depgraph rules synced",
            )
        # S1.6: 失败->写入重试队列（单条记录，记录最近一次失败信息 + 累计次数）
        prev = _read_retry_queue() or {}
        attempt = prev.get("attempt", 0) + 1
        _write_retry_queue({
            "failed_at": datetime.now(UTC).isoformat(),
            "attempt": attempt,
            "error": sync_result.stderr.strip()[:500] or sync_result.stdout.strip()[:500],
            "triggered_by": session_id,
        })
        if attempt >= _MAX_RETRY_ATTEMPTS:
            # S1.6: 超过最大重试次数->升级为 error（停止重试，需人工介入修路径/依赖）
            return ReconcileResult(
                action="error",
                detail=f"yaml sync failed {attempt} times (max={_MAX_RETRY_ATTEMPTS}), STOPPED retry. Manual fix needed: {sync_result.stderr.strip()[:200]}",
            )
        return ReconcileResult(
            action="warn",
            detail=f"yaml sync failed (attempt {attempt}/{_MAX_RETRY_ATTEMPTS}, will retry on next commit): {sync_result.stderr.strip()[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-YAML-SYNC",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=160,
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
    - markdown 链接 ``](path)`` -> 提取 path
    - 反引号代码 ``` `path` ``` -> 提取 path
    - 纯文本路径（CSV 单元格值、YAML 值、正文裸路径 docs/foo/bar.md）
    - CSV 专用：逐单元格精确提取（避免正则误匹配 CSV 结构）
    - file:/// 绝对路径 -> 转项目相对路径
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

    # 支持的工作文档扩展名（治本 GAP-5：.md only -> 多类型）
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
        ref = ref.split("#")[0].strip()  # 剥离锚点（如 foo.md#section -> foo.md）
        if not ref:
            return False
        # file:/// 绝对路径 -> 直接作为绝对路径检查（不拼 project_root，避免前导/解析 bug）
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

    # 递归扫描多类型工作文档（治本 GAP-5：glob("*.md") -> rglob 多扩展名）
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
            # 5.59.4 修复：原 errors="replace" 用于路径提取，替换字符 \ufffd 可能出现在路径中间，
            # 产生形如 docs/\ufffd03_modules/foo.md 的幻觉路径，污染对账结果。
            # 改为先校验文件是否合法 UTF-8，校验失败则跳过。
            raw = doc.read_bytes()
            try:
                content = raw.decode("utf-8")
            except UnicodeDecodeError:
                continue
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
                    details[doc.name]["archive_error"] = "internal error"
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


def make_precommit_id_uniqueness_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-ID-UNIQ post-commit 兜底 reconciler（治本改进点2）。

    GATE-ID-UNIQ (pre-commit hook id 唯一性) 被 GitCommitGateway 的 --no-verify
    系统性绕过（机制层病根，与 GATE-REG-BL 同根：post-commit 补偿层；原 GATE-15-ttl 已删除）。
    本 reconciler 在 post-commit 跑 check_precommit_id_uniqueness.py --ci 重校，
    检测到 same-repo 重复 id 则记录违规报告供追责（commit 已入历史，非阻断——
    沿用原 make_ttl_reconciler 的设计裁定，该 reconciler 已删除但模式沿用）。

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
        scan_result = _run_subprocess(
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
    1. trigger: committed_files 含 ttl_vocabulary.yaml -> 命中
    2. 调用 backfill_ttl_metadata.py --rejudge 重判所有 docs/*.md 的 ttl
    3. git diff 检测 docs/ 下 .md 变更 -> 无变更返回 clean
    4. 有变更 -> git add + git commit --no-verify（斩断循环）

    设计依据：trae_060 治本方案——decision_tree 机器可读化后，词表变更应自动传播到
    所有 .md 文件的 ttl 字段，消除手动 backfill 漂移风险。reconciler 优先级 280
    （在原 GATE-15-ttl 300 之前执行；GATE-15-ttl 已删除，ttl 校验由 pre-compensation 承担）。

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
        rejudge_result = _run_subprocess(
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

        # 3. 变更 -> 自动提交修复（经 _commit_auto 统一入口，DCR gate 覆盖）
        # 治本（2026-06-30）：原裸调 _run_git commit 绕过 DCR gate，改为走 _commit_auto
        # 统一入口，五重 gate 覆盖。原"--no-verify 斩断 pre-commit 循环"由 _commit_auto
        # 内部的 --no-verify 保证（_commit_with_file_message 统一用 --no-verify）。
        abs_files = [str(project_root / f) for f in changed_files]
        auto_msg = (
            f"chore(ttl): auto-rejudge by GATE-VOCAB-CHANGE post-commit "
            f"(decision_tree changed)"
        )
        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)
        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail=f"ttl rejudge: {len(changed_files)} files auto-reconciled",
            )
        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail=f"ttl rejudge: {len(changed_files)} files but no staged changes (auto-commit)",
            )
        return ReconcileResult(
            action="warn",
            detail=f"ttl rejudge: auto-commit failed ({commit_result.status}): "
                   f"{commit_result.message[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-VOCAB-CHANGE",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=280,
    )


def _audit_commit_history(
    project_root: "object",
    audit_window: int,
    gw_marker: str,
    rv_marker: str = "",
) -> "tuple[list[dict], list[dict], str | None]":
    """扫描最近 N 个 commit，返回 (裸commit违规, rv豁免通道使用, error)。

    rv_marker 非空时，含 [GW: 且含 rv_marker 的 commit 记入 rv_uses（合法但追溯）。

    治本（2026-06-30 病根1 看门人无人看）：把 make_commit_gateway_audit_reconciler
    闭包内的审计逻辑提取为模块级函数，使其成为可被 integrity_anchors 保护的 name
    （A 层 _check_protected_script_integrity 已在 AD-001 阶段3 删除，但模块级函数
    结构保留，供未来复活 A 层时直接复用）。与 working_docs_ghost_ref_archiver 模式
    一致：工厂函数 + 模块级逻辑函数（scan_and_archive_working_docs）。

    两阶段检查：subject 快速扫描 + body 二次确认
    （GitCommitGateway.commit() 把 [GW:tag] 追加到 message 末尾用 \\n\\n 分隔，
    --oneline 只看 subject 会误判手动 commit 为裸 commit，需查 body）。

    Args:
        project_root: Path 对象（gateway.project_root，类型注解 object 保持纯 stdlib）。
        audit_window: 审计窗口（最近 N 个 commit）。
        gw_marker: GW 标记字符串（如 "[GW:"）。

    Returns:
        (violations, rv_uses, error_msg): error_msg 非 None 表示 git log 失败；
        error_msg 为 None 时 violations 为裸 commit 违规列表，rv_uses 为豁免通道使用列表。
    """
    import subprocess

    log_result = _run_subprocess(
        ["git", "log", f"-{audit_window}", "--oneline"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
    )
    if log_result.returncode != 0:
        return [], [], f"git log failed: {log_result.stderr.strip()[:200]}"

    violations: list[dict] = []
    rv_uses: list[dict] = []
    for line in log_result.stdout.strip().splitlines():
        # format: <hash> <subject>
        parts = line.split(" ", 1)
        if len(parts) < 2:
            continue
        commit_hash, subject = parts[0], parts[1]
        # 跳过 merge commit（合并提交无作者意图；大小写不敏感以兼容 session_worktree 的小写 "merge session/..."）
        if subject.lower().startswith("merge "):
            continue
        if gw_marker in subject:
            # subject 已含 [GW:（合法 commit），检测是否豁免通道使用
            if rv_marker and rv_marker in subject:
                rv_uses.append({"hash": commit_hash, "subject": subject[:120]})
            continue
        # subject 无 [GW: -> 查 body（手动 commit 的 [GW:tag] 在 body 末尾）
        body_result = _run_subprocess(
            ["git", "show", "-s", "--format=%B", commit_hash],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
        body = body_result.stdout if body_result.returncode == 0 else ""
        if gw_marker in body:
            # body 含 [GW:（合法 commit），检测是否豁免通道使用
            if rv_marker and rv_marker in body:
                rv_uses.append({"hash": commit_hash, "subject": subject[:120]})
            continue
        violations.append({"hash": commit_hash, "subject": subject[:120]})
    return violations, rv_uses, None


def make_deprecated_directory_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-DEPRECATED-DIR post-commit reconciler（09_audit 治本加固）。

    扫描 docs/ 下是否存在已废弃目录（如 09_audit/），存在则告警。
    双层防御：directory_contract_gate（subprocess 调 check_directory_contract.py）阻断提交 +
    post-commit reconciler 兜底 mkdir 但未提交的场景（如脚本 mkdir 后未 commit）。

    设计裁定（非阻断）：
    post-commit 无法回滚已提交内容；废弃目录可能是脚本 mkdir 的副作用（未 commit），
    仅告警记录到 ``.runtime/reconcile_reports/deprecated_directory_<ts>.json``。

    trigger 裁定：always True（废弃目录可能由任何脚本 mkdir 重建，与 commit 文件无关）。

    向内收设计：
    - 复用 ReconciliationRegistry 框架，不新建兜底系统
    - 废弃目录清单从 directory_contract.yaml §7 deprecated_directories 动态加载（真源唯一，治本 2026-06-30：原依赖 gateway._DEPRECATED_DIRS 已删除导致降级为 no-op）
    - 复用 _write_reconcile_report 报告落盘

    Args:
        gateway: GitCommitGateway 实例（用 project_root 定位契约文件）。

    Returns:
        ReconcilerSpec(gate_id="GATE-DEPRECATED-DIR", priority=600)。
    """
    project_root = gateway.project_root
    # 从 directory_contract.yaml §7 deprecated_directories 动态加载（真源唯一）
    # 治本 2026-06-30：原 getattr(gateway, "_DEPRECATED_DIRS", {}) 因 _DEPRECATED_DIRS
    # 已删除（AD-001 阶段3）返回空 dict 导致 reconciler 降级为 no-op，现直接读契约真源
    import yaml as _yaml  # 局部导入（模块声明 pure stdlib，yaml 仅此函数需要）
    _contract_path = (
        project_root / "docs" / "01_policies_and_standards"
        / "_registry" / "contracts" / "directory_contract.yaml"
    )
    deprecated_dirs: dict[str, str] = {}
    try:
        with open(_contract_path, encoding="utf-8") as _f:
            _contract = _yaml.safe_load(_f) or {}
        for _entry in _contract.get("deprecated_directories", []):
            _path = _entry.get("path", "")
            _reason = _entry.get("reason", "")
            if _path:
                deprecated_dirs[_path] = _reason
    except (OSError, _yaml.YAMLError):
        # fail-open：契约读取失败时 reconciler 降级为 no-op（不阻断 commit）
        deprecated_dirs = {}

    def _trigger(committed_files: list[str]) -> bool:
        # 始终检测：脚本可能 mkdir 但未 commit（如 session_continuity 的 handoff 写入）
        return True

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        """自动修复：迁移废弃目录内容到合规目录 + 删除空目录。

        治本策略（非 warn-only）：
        - 空目录 -> 直接 rmdir -> action=clean
        - 非空目录 -> shutil.move 迁移到 docs/_working/audit/（不覆盖已有文件）
          -> rmdir 空目录 -> action=warn（迁移的文件需人工 commit）
        - 部分失败 -> action=warn

        消灭"只告警不消除"——无论脚本如何 mkdir，下一次 commit 后自动清理。
        """
        import shutil  # 局部导入（避免模块级依赖膨胀）
        import os
        from pathlib import Path

        # 合规目标目录：docs/09_audit/ -> docs/_working/audit/
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

# DCR-001 全量扫描触发的契约文件子集（directory_contract + doc_type_vocabulary）
# 提取到模块级避免 check_vocab_hardcode 检测5 误报：
# 函数体内 yaml.safe_load 加载 architecture_issue_registry.yaml（非词表），
# 但同时含 "vocabularies/..." 路径字符串触发 has_vocab_ref 误报。
_CONTRACT_FILES_FOR_DCR = frozenset({
    "docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml",
    "docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml",
})


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
        ts_iso = now_utc().isoformat(timespec="seconds")
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


# ============================================================
# AD-GOV-001 治理收敛：5 组 reconciler 合并（16->11）
# 合并规则（严格遵守）：
# - trigger = 旧A trigger OR 旧B trigger（任一命中即执行）
# - reconcile = 串联执行 旧A -> 旧B；action 取较严重
#   （severity: skip/nothing=0, clean=1, warn=2, auto_committed=2），detail 拼接两者
# - priority = max(旧A, 旧B)
# 治本（2026-06-30 元问题4）：原 _make_old_*_reconciler 私有函数已删除，reconcile
# 逻辑内联到下方 5 个 make_* compose 包装函数的闭包中。Python 无真私有，保留
# _make_old_* 等于留可 import 的绕过入口；内联后 reconcile 逻辑仅在 make_* 闭包
# 内可见，无法被外部 import 绕过 compose。reconcile 逻辑真源不动（gateway._commit_auto
# / subprocess / 报告落盘调用原样保留）。
# _compose_reconcilers 是 compose 工具函数（被测试覆盖），保留。
# 测试规范见 tests/governance/audit/test_integrity_audit_reconciler.py——用公共 API +
# mock spec + 模块级函数 _audit_commit_history 测试。
# 新增 reconciler 前 MUST 过 trae_060 §4 元问题审查，教训登记 #ARCH-028。
# ============================================================


def _compose_reconcilers(
    gate_id: str,
    *specs: ReconcilerSpec,
) -> ReconcilerSpec:
    """合并 N 个（≥2）reconciler spec 为一个（AD-GOV-001 治理收敛工具函数）。

    元问题1治本扩展（2026-06-30）：原签名只支持 2 个 spec，AGENTS.md 引用检测
    需 3-way 合并（rules_integrity + commit_gw_audit + agents_md_refs）。扩展为
    *specs 可变参数，向后兼容（2 参数时行为不变，5 个现有调用点零回归）。

    - trigger: 所有 spec trigger 的 OR（任一命中即执行）
    - reconcile: 串联执行所有 spec.reconcile（按传入顺序）；action 取较严重
      （severity: warn=auto_committed=2 > clean=1 > skip=nothing=0），detail 拼接全部
    - priority: max(所有 spec.priority)
    """
    if len(specs) < 2:
        raise ValueError(f"_compose_reconcilers requires at least 2 specs, got {len(specs)}")

    triggers = [s.trigger for s in specs]
    reconciles = [s.reconcile for s in specs]
    _SEVERITY = {"skip": 0, "clean": 1, "nothing": 0, "warn": 2, "auto_committed": 2}

    def _trigger(committed_files: list[str]) -> bool:
        return any(t(committed_files) for t in triggers)

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        results = [r(committed_files, session_id) for r in reconciles]
        # action 取较严重（severity 高者胜）
        action = results[0].action
        for res in results[1:]:
            if _SEVERITY.get(res.action, 0) > _SEVERITY.get(action, 0):
                action = res.action
        # detail 平铺拼接全部（格式：[action_a] detail_a | [action_b] detail_b | ...）
        detail = " | ".join(f"[{r.action}] {r.detail}" for r in results)
        return ReconcileResult(action=action, detail=detail)

    return ReconcilerSpec(
        gate_id=gate_id,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=max(s.priority for s in specs),
    )


def _backup_depgraph_for_autoclean(project_root: "object", session_id: str) -> "tuple":
    """ghost auto-clean 前的逻辑备份（nodes + edges 表 CSV）。

    治本（2026-07-04）：符合"备份先行：改 depgraph 前必须备份"硬约束（trae_054 STEP0）。
    函数内 import psycopg2 + get_depgraph_pg_connection（F1 裸 connection，支持 copy_expert），
    不破坏本模块顶层"纯 stdlib"约束（reconciliation_registry 用于 mutation testing，
    顶层须纯 stdlib；函数内 import 是允许的，与既有 _reconcile_ghost 内 import 一致）。

    治本（2026-07-08，ARCH-DEBT-BACKUP-CLEANUP）：备份路径统一到 tmp/pg_backups/（.gitignored，
    与 backup_runtime_state.py 的 backup_pg_depgraph 标杆机制对齐），并新增保留策略——保留最近
    max_backups 个 ghost_autoclean_* 目录，超出部分自动清理（对标 backup_pg_depgraph 的保留 10 个）。
    消除"备份目录只增不减"的技术债务。详见 architecture_debt_registry.md §5.1.3。

    Args:
        project_root: Path 对象（gateway.project_root）。
        session_id: 触发 auto-clean 的 session_id（用于备份目录命名追溯）。

    Returns:
        (backup_dir_path, "") 成功 | (None, error_msg) 失败（fail-closed 不清理）。
    """
    import time
    from pathlib import Path

    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
    except Exception as e:
        return None, f"import depgraph_schema failed: {e}"

    ts = int(time.time())
    backup_dir = Path(project_root) / "tmp" / "pg_backups" / f"ghost_autoclean_{ts}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        with conn.cursor() as cur:
            for table in ("nodes", "edges"):
                csv_path = backup_dir / f"{table}.csv"
                with open(csv_path, "w", encoding="utf-8") as f:
                    cur.copy_expert(f"COPY {table} TO STDOUT WITH CSV HEADER", f)
        # 治本（2026-07-08）：保留策略——清理过期 ghost_autoclean 备份（对标 backup_pg_depgraph）
        _cleanup_old_ghost_backups(project_root, max_backups=10)
        return backup_dir, ""
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


def _cleanup_old_ghost_backups(project_root: "object", max_backups: int = 10) -> int:
    """清理过期的 ghost_autoclean_* 备份目录，保留最近 max_backups 个。

    治本（2026-07-08，ARCH-DEBT-BACKUP-CLEANUP）：对标 backup_runtime_state.py 的
    backup_pg_depgraph 保留策略（保留最近 10 个），消除"备份目录只增不减"的技术债务。

    备份目录命名：ghost_autoclean_{unix_timestamp}（按时间戳排序 = 按创建时间排序）。

    Args:
        project_root: Path 对象（gateway.project_root）。
        max_backups: 保留的备份数量上限（默认 10）。

    Returns:
        清理的备份数量（异常时返回 0，不阻断主流程）。
    """
    import os
    import shutil
    from pathlib import Path

    try:
        base = Path(project_root) / "tmp" / "pg_backups"
        if not base.exists():
            return 0
        # 列出所有 ghost_autoclean_* 目录，按名称（含时间戳）降序排序 = 最近创建的在前
        backups = sorted(
            [d for d in base.iterdir() if d.is_dir() and d.name.startswith("ghost_autoclean_")],
            key=lambda d: d.name,
            reverse=True,
        )
        # 超出 max_backups 的全部删除
        to_remove = backups[max_backups:]
        for d in to_remove:
            try:
                shutil.rmtree(str(d))
            except OSError:
                # Windows 文件锁兜底——只读位清除后重试
                import stat
                try:
                    for f in d.rglob("*"):
                        if f.is_file():
                            os.chmod(f, stat.S_IWRITE)
                    shutil.rmtree(str(d))
                except OSError:
                    pass  # fail-open，不阻断主流程
        return len(to_remove)
    except Exception:
        return 0  # fail-open，保留策略失败不阻断主备份流程


def make_delete_audit_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-DELETE-AUDIT post-commit 对账 reconciler（AD-GOV-001 合并）。

    合并来源：
    - 旧 GATE-GHOST (priority=400)：commit 删除文件后跑 diagnose_depgraph.py
      检测 depgraph 残留 ghost node（磁盘已删除但 DB 仍保留），记录报告供追责。
    - 旧 GATE-WORKING-DOCS (priority=500)：扫描 docs/_working/ 工作文档的幽灵引用，
      归档有幽灵引用的文档到 .runtime/working_archive/ 并自动提交 _working/ 删除。

    合并原因：两者 trigger 完全重叠（均检测 committed 文件不在磁盘 = 删除 commit），
    reconcile 均处理"删除引发的漂移"，逻辑可串联，合并消除冗余 trigger 评估。

    合并后执行：先 ghost 诊断，再 working_docs 归档；action 取较严重，detail 拼接。
    priority=max(400,500)=500。

    治本（2026-06-30 元问题4）：reconcile 逻辑内联自原 _make_old_ghost_reconciler
    与 _make_old_working_docs_reconciler，私有函数已删除，无法被外部 import 绕过。
    """
    import os
    import re
    import subprocess
    import sys

    project_root = gateway.project_root

    # === 旧 GATE-GHOST 逻辑（内联自 _make_old_ghost_reconciler）===
    def _trigger_ghost(committed_files: list[str]) -> bool:
        # committed 文件不在磁盘 = 删除 commit（post-commit 时点，工作树已反映删除）
        return any(not os.path.isfile(f) for f in committed_files)

    def _reconcile_ghost(committed_files: list[str], session_id: str) -> ReconcileResult:
        # P0 修复（2026-07-04）：动态查找 diagnose_depgraph.py 路径
        # 原写死 scripts/governance/diagnose_depgraph.py，gov-split 批次4b（commit 170cba56e0）
        # 将文件迁移到 scripts/governance/d5_architecture/ 后路径失效，导致检测机制完全失效
        # （所有报告 exit=2 ghost=-1 "can't open file"）。改为 glob 动态查找，兼容未来迁移。
        import glob as _glob
        diag_candidates = [
            os.path.join(str(project_root), "scripts", "governance", "diagnose_depgraph.py"),
        ]
        diag_candidates += _glob.glob(
            os.path.join(str(project_root), "scripts", "governance", "**", "diagnose_depgraph.py"),
            recursive=True,
        )
        diag_path = next((p for p in diag_candidates if os.path.isfile(p)), None)
        if diag_path is None:
            return ReconcileResult(
                action="warn",
                detail="ghost diagnose skipped: diagnose_depgraph.py not found under scripts/governance/",
            )
        # 1. 跑 diagnose_depgraph.py（无 --output，捕获 stdout 解析 ghost_count）
        diag_result = _run_subprocess(
            [sys.executable, diag_path],
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
        # 4. 判定（ghost_count==0 = clean；>0 在阈值内 = auto_clean；>阈值/-1 = warn）
        if diag_result.returncode == 0 and ghost_count == 0:
            return ReconcileResult(
                action="clean",
                detail=f"ghost diagnose clean (ghost_count=0), report={report_path.name}",
            )
        # P1 auto_clean（2026-07-04）：ghost_count > 0 且 ≤ 阈值 -> 自动清理
        # 治本：消除"检测自动/清理人工"gap（root_cause: 检测坏 + 无自动闭环导致 ghost 无声狂累积）。
        # 备份先行（符合 trae_054 STEP0 硬约束），备份失败则 fail-closed 不清理。
        # 与"永久系统必须全自动（自动触发/运行/维护/关闭）禁止需手工干预"硬约束对齐。
        _GHOST_AUTO_CLEAN_THRESHOLD = 50  # ghost ≤ 50 自动清理，> 50 warn（防批量误删）
        if (
            diag_result.returncode == 0
            and 0 < ghost_count <= _GHOST_AUTO_CLEAN_THRESHOLD
        ):
            backup_dir, backup_err = _backup_depgraph_for_autoclean(project_root, session_id)
            if backup_err:
                return ReconcileResult(
                    action="warn",
                    detail=f"ghost count={ghost_count} but backup failed: {backup_err}, skip auto-clean for safety",
                )
            # 调 apply_depgraph.py --cleanup-orphan-nodes（清理已在 backup 之后）
            clean_nodes = _run_subprocess(
                [sys.executable, "scripts/governance/apply_depgraph.py", "--cleanup-orphan-nodes"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300,
            )
            # 再调 --cleanup-orphan-edges（清理孤儿边）
            clean_edges = _run_subprocess(
                [sys.executable, "scripts/governance/apply_depgraph.py", "--cleanup-orphan-edges"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300,
            )
            return ReconcileResult(
                action="auto_committed",
                detail=(
                    f"auto-cleaned {ghost_count} ghost nodes "
                    f"(nodes_exit={clean_nodes.returncode}, edges_exit={clean_edges.returncode}), "
                    f"backup={backup_dir.name}, report={report_path.name}"
                ),
            )
        # ghost_count > 阈值 或 解析失败（-1）-> warn（防批量误删/检测失败）
        return ReconcileResult(
            action="warn",
            detail=f"ghost diagnose: ghost_count={ghost_count} (exit={diag_result.returncode}), report={report_path.name}",
        )

    spec_ghost = ReconcilerSpec(
        gate_id="GATE-GHOST",
        trigger=_trigger_ghost,
        reconcile=_reconcile_ghost,
        priority=400,
    )

    # === 旧 GATE-WORKING-DOCS 逻辑（内联自 _make_old_working_docs_reconciler）===
    def _trigger_working(committed_files: list[str]) -> bool:
        # 与 ghost 一致：committed 文件不在磁盘 = 删除 commit
        return any(not os.path.isfile(f) for f in committed_files)

    def _reconcile_working(committed_files: list[str], session_id: str) -> ReconcileResult:
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

        # 3. 归档后自动 commit _working/ 的删除（经 _commit_auto 统一入口，DCR gate 覆盖）
        archived_rel = [f"docs/_working/{name}" for name in archived]
        abs_files = [str(project_root / rel) for rel in archived_rel]
        auto_msg = (
            f"chore(working_docs): auto-archive {len(archived)} ghost-ref docs by "
            f"GitCommitGateway post-commit"
        )
        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)
        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail=f"working_docs archived {len(archived)} ghost-ref docs, "
                       f"report={report_path.name}",
            )
        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail=f"working_docs archived {len(archived)} but no staged changes "
                       f"(auto-commit), report={report_path.name}",
            )
        return ReconcileResult(
            action="warn",
            detail=f"working_docs archived {len(archived)} but auto-commit failed "
                   f"({commit_result.status}): {commit_result.message[:200]}",
        )

    spec_working = ReconcilerSpec(
        gate_id="GATE-WORKING-DOCS",
        trigger=_trigger_working,
        reconcile=_reconcile_working,
        priority=500,
    )

    return _compose_reconcilers("GATE-DELETE-AUDIT", spec_ghost, spec_working)


def make_regenerate_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-REGENERATE post-commit 自动重生 reconciler（AD-GOV-001 合并）。

    合并来源：
    - 旧 GATE-DOMAIN-DOC (priority=600)：PG 写入脚本 commit 后跑
      generate_domain_doc.py --all + generate_domain_dependency_diagram.py --all
      重生所有域制品，有变更自动提交。
    - 旧 GATE-ARCH-MODEL (priority=610)：PG 写入脚本 commit 后跑
      dm200916_write_direct.py 重生根树 architecture_model/index.yaml 的 domains
      列表，有变更自动提交。

    合并原因：两者 trigger 完全重叠（均匹配同一组 PG 写入脚本 commit），reconcile
    均为"DB 变更->派生制品重生"，逻辑可串联，合并消除冗余 trigger 评估。

    合并后执行：先重生域文档，再重生根树 index.yaml；action 取较严重，detail 拼接。
    priority=max(600,610)=610。

    治本（2026-06-30 元问题4）：reconcile 逻辑内联自原 _make_old_domain_doc_reconciler
    与 _make_old_arch_model_reconciler，私有函数已删除。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root
    # PG 写入脚本真源列表（DB 变更即代表域可能漂移）
    _PG_WRITE_SCRIPTS = (
        "scripts/governance/apply_depgraph.py",
        "scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py",
        "scripts/governance/generate_project_path_tree.py",
    )
    _GEN_DIR = "scripts/governance/d5_architecture/generators"
    _DOC_DIRS = (
        "docs/02_enterprise_architecture/02_domain_architecture_docs",
        "docs/02_enterprise_architecture/generated/domains",
    )
    _GEN_SCRIPT = "scripts/governance/d5_architecture/dm200916_write_direct.py"
    _ARCH_MODEL_INDEX = (
        "architecture_model/index.yaml",
    )

    # === 旧 GATE-DOMAIN-DOC 逻辑（内联自 _make_old_domain_doc_reconciler）===
    def _trigger_domain_doc(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel in _PG_WRITE_SCRIPTS:
                return True
            # 文件删除也触发：layer 1 ghost 过滤确保重生后的文档不含幽灵节点
            if not os.path.isfile(f) and f.endswith((".py", ".yaml", ".yml")):
                return True
        return False

    def _reconcile_domain_doc(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 重生所有域制品（生成器不含时间戳，相同 DB 输入->相同输出）
        for gen_name in ("generate_domain_doc.py", "generate_domain_dependency_diagram.py"):
            gen_result = _run_subprocess(
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

        # 1b. 重生域索引（无 --all 参数，单独运行）
        idx_result = _run_subprocess(
            [sys.executable, f"{_GEN_DIR}/generate_domain_index.py"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        if idx_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"generate_domain_index.py failed: {idx_result.stderr.strip()[:200]}",
            )

        # 2. 检测制品变更
        diff_result = gateway._run_git(
            ["git", "diff", "--name-only", "--", *_DOC_DIRS]
        )
        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="domain docs up to date")

        # 3. 变更 -> 自动提交（经 _commit_auto 统一入口，DCR gate 覆盖）
        changed_files = [
            f.strip() for f in diff_result.stdout.splitlines() if f.strip()
        ]
        abs_files = [str(project_root / f) for f in changed_files]
        auto_msg = "chore(docs): auto-regenerate domain docs by GitCommitGateway post-commit"
        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)
        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="domain docs drift detected and auto-regenerated",
            )
        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="domain docs no drift (auto-commit found no staged changes)",
            )
        return ReconcileResult(
            action="warn",
            detail=f"domain docs drift detected, auto-commit failed ({commit_result.status}): "
                   f"{commit_result.message[:200]}",
        )

    spec_domain_doc = ReconcilerSpec(
        gate_id="GATE-DOMAIN-DOC",
        trigger=_trigger_domain_doc,
        reconcile=_reconcile_domain_doc,
        priority=600,
    )

    # === 旧 GATE-ARCH-MODEL 逻辑（内联自 _make_old_arch_model_reconciler）===
    def _trigger_arch_model(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel in _PG_WRITE_SCRIPTS:
                return True
        return False

    def _reconcile_arch_model(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 重生根树 index.yaml（dm200916 从 depgraph (PostgreSQL) domains 表派生）
        gen_result = _run_subprocess(
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

        # 3. 变更 -> 自动提交（经 _commit_auto 统一入口，DCR gate 覆盖）
        abs_files = [str(project_root / rel) for rel in _ARCH_MODEL_INDEX]
        auto_msg = "chore(arch_model): auto-regenerate EA tree index.yaml by GitCommitGateway post-commit"
        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)
        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="EA tree index.yaml drift detected and auto-regenerated",
            )
        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="EA tree index.yaml no drift (auto-commit found no staged changes)",
            )
        return ReconcileResult(
            action="warn",
            detail=f"EA tree index.yaml drift detected, auto-commit failed ({commit_result.status}): "
                   f"{commit_result.message[:200]}",
        )

    spec_arch_model = ReconcilerSpec(
        gate_id="GATE-ARCH-MODEL",
        trigger=_trigger_arch_model,
        reconcile=_reconcile_arch_model,
        priority=610,
    )

    # === GATE-MANIFEST 逻辑（新增 2026-07-01：.py 文件增删后自动重生 script_manifest.yaml）===
    _MANIFEST_FILE = "scripts/governance/script_manifest.yaml"
    _MANIFEST_GEN = "scripts/governance/generators/generate_script_manifest.py"

    def _trigger_manifest(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel.endswith(".py") and rel.startswith("scripts/"):
                return True
        return False

    def _reconcile_manifest(committed_files: list[str], session_id: str) -> ReconcileResult:
        gen_result = _run_subprocess(
            [sys.executable, _MANIFEST_GEN],
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
                detail=f"generate_script_manifest.py failed: {gen_result.stderr.strip()[:200]}",
            )
        diff_result = gateway._run_git(
            ["git", "diff", "--name-only", "--", _MANIFEST_FILE]
        )
        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="script manifest up to date")
        abs_file = str(project_root / _MANIFEST_FILE)
        auto_msg = "chore(manifest): auto-regenerate script_manifest.yaml by GitCommitGateway post-commit"
        commit_result = gateway._commit_auto(session_id, [abs_file], auto_msg)
        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="script manifest drift detected and auto-regenerated",
            )
        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="script manifest no drift",
            )
        return ReconcileResult(
            action="warn",
            detail=f"script manifest drift detected, auto-commit failed ({commit_result.status})",
        )

    spec_manifest = ReconcilerSpec(
        gate_id="GATE-MANIFEST",
        trigger=_trigger_manifest,
        reconcile=_reconcile_manifest,
        priority=620,
    )

    return _compose_reconcilers("GATE-REGENERATE", spec_domain_doc, spec_arch_model, spec_manifest)


def make_rule_audit_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-RULE-AUDIT post-commit 规则同步+审计+ARCH引用检测 reconciler（AD-GOV-001 合并）。

    合并来源：
    - 旧 GATE-RULE-CATALOG (priority=160)：commit rules/ 下文件后跑
      generate_rule_catalog.py 重新生成 rule_catalog_registry.yaml，有变更自动提交。
    - 旧 GATE-RULE-FILE-AUDIT (priority=700)：commit 治理真源规则文件
      （directory_contract/doc_type_vocabulary/ttl_vocabulary/architecture_contract/
      gate_registry）后落盘审计记录，提示人工审查（约束可能被悄悄放宽）。
      P5 改造（2026-06-30）：当 directory_contract.yaml 或 doc_type_vocabulary.yaml
      变更时，额外跑 check_directory_contract.py 全量扫描，确认契约变更未引入
      DCR-001 违规（目录->doc_type 对应），违规列表写入审计报告。
    - 新增 GATE-ARCH-REFS (priority=710，元问题2治本 2026-06-30)：扫描 committed_files
      中所有 #ARCH-XXX 引用，检查是否在 architecture_issue_registry.yaml 的 entries 中
      有对应条目。病根：注册表铁律#6"任何 #ARCH-XXX 引用必须在本注册表有对应条目，禁止
      grep-and-claim 占位"是君子协定，无技术强制。#ARCH-027 冲突就是 AI 占位而不查重
      导致的。检测到未登记的 #ARCH-XXX 引用->warn（非阻断，detail 列出未登记编号）。

    合并原因：三者关注点相邻（规则文件变更的自动同步 + 人工审计兜底 + ARCH引用查重），
    trigger 重叠（规则文件/文本文件变更），合并形成"自动同步+审计告警+ARCH查重"单入口。

    合并后执行：先重生成 catalog（自动提交漂移），再落盘规则文件审计告警，最后检测
    #ARCH-XXX 引用有效性；action 取较严重，detail 拼接。priority=max(160,700,710)=710。

    治本（2026-06-30 元问题4）：reconcile 逻辑内联自原 _make_old_rule_catalog_reconciler
    与 _make_old_rule_file_audit_reconciler，私有函数已删除。

    治本（2026-06-30 元问题2）：新增 #ARCH-XXX 引用查重检测，合并入本 reconciler
    不新增 reconciler（trae_060 §4 审查通过：该存在+可合并入已有）。
    """
    import json
    import os
    import re
    import subprocess
    import sys
    from datetime import datetime

    project_root = gateway.project_root
    _project_root_str = str(project_root)
    _CATALOG_REL = "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml"
    _RULES_PREFIX = "docs/01_policies_and_standards/rules/"
    _rule_set = set(_RULE_FILE_PATHS)

    # === 旧 GATE-RULE-CATALOG 逻辑（内联自 _make_old_rule_catalog_reconciler）===
    def _trigger_catalog(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel.startswith(_RULES_PREFIX) and rel.endswith((".yaml", ".yml", ".md")):
                return True
        return False

    def _reconcile_catalog(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 重新生成 catalog（generate_rule_catalog.py 幂等）
        gen_result = _run_subprocess(
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

        # 3. 变更 -> 自动提交（经 _commit_auto 统一入口，DCR gate 覆盖）
        auto_msg = "chore(catalog): auto-sync rule_catalog_registry by GitCommitGateway post-commit"
        abs_files = [str(project_root / _CATALOG_REL)]
        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)
        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="rule_catalog_registry drift detected and auto-reconciled",
            )
        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="rule_catalog_registry no drift (auto-commit found no staged changes)",
            )
        return ReconcileResult(
            action="warn",
            detail=f"rule_catalog_registry drift detected, auto-commit failed ({commit_result.status}): "
                   f"{commit_result.message[:200]}",
        )

    spec_catalog = ReconcilerSpec(
        gate_id="GATE-RULE-CATALOG",
        trigger=_trigger_catalog,
        reconcile=_reconcile_catalog,
        priority=160,
    )

    # === 旧 GATE-RULE-FILE-AUDIT 逻辑（内联自 _make_old_rule_file_audit_reconciler）===
    def _trigger_rule_file_audit(committed_files: list[str]) -> bool:
        for f in committed_files:
            if _rel_path(f, _project_root_str) in _rule_set:
                return True
        return False

    def _reconcile_rule_file_audit(committed_files: list[str], session_id: str) -> ReconcileResult:
        rule_files_changed = [
            _rel_path(f, _project_root_str)
            for f in committed_files
            if _rel_path(f, _project_root_str) in _rule_set
        ]

        reports_dir = os.path.join(_project_root_str, ".runtime", "reconcile_reports")
        os.makedirs(reports_dir, exist_ok=True)
        ts_iso = now_utc().isoformat(timespec="seconds")
        ts_file = ts_iso.replace(":", "")

        # P5 改造（2026-06-30）：契约文件变更时触发 DCR-001 全量扫描
        # 当 directory_contract.yaml 或 doc_type_vocabulary.yaml 变更时，
        # 跑 check_directory_contract.py 全量扫描，确认契约变更未引入 DCR-001 违规
        _CONTRACT_FILES = _CONTRACT_FILES_FOR_DCR  # 模块级常量引用（避免 check_vocab_hardcode 检测5 误报）
        contract_changed = [f for f in rule_files_changed if f in _CONTRACT_FILES]
        dcr_scan_summary = None
        dcr001_violations: list[str] = []

        if contract_changed:
            scan_result = _run_subprocess(
                [sys.executable, "scripts/governance/d1_structure/check_directory_contract.py"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
            )
            # 解析 stderr 中的 DCR-001 违规行（格式: "  [error] DCR-001 <file>"）
            stderr_lines = scan_result.stderr.splitlines() if scan_result.stderr else []
            dcr001_violations = [
                line.strip() for line in stderr_lines
                if "DCR-001" in line and "error" in line
            ]
            if scan_result.returncode == 0:
                dcr_scan_summary = f"clean (exit=0, {len(dcr001_violations)} DCR-001 violations)"
            else:
                dcr_scan_summary = f"findings (exit={scan_result.returncode}, {len(dcr001_violations)} DCR-001 violations)"

        report = {
            "timestamp": ts_iso,
            "session_id": session_id,
            "rule_files_changed": rule_files_changed,
            "note": "规则文件变更需人工审查（约束可能被放宽）",
        }
        if contract_changed:
            report["contract_dcr_scan"] = {
                "contract_files_changed": contract_changed,
                "scan_summary": dcr_scan_summary,
                "dcr001_violations": dcr001_violations,
                "violation_count": len(dcr001_violations),
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

        detail_parts = [
            f"{len(rule_files_changed)} rule file(s) changed "
            f"(manual review recommended), report={os.path.basename(report_path)}"
        ]
        if contract_changed:
            if dcr001_violations:
                detail_parts.append(
                    f"DCR-001 全量扫描发现 {len(dcr001_violations)} 个违规（契约变更可能引入漂移，需人工排查）"
                )
            else:
                detail_parts.append("DCR-001 全量扫描通过（契约变更后全量合规）")

        return ReconcileResult(
            action="warn",
            detail="; ".join(detail_parts),
        )

    spec_rule_file_audit = ReconcilerSpec(
        gate_id="GATE-RULE-FILE-AUDIT",
        trigger=_trigger_rule_file_audit,
        reconcile=_reconcile_rule_file_audit,
        priority=700,
    )

    # === 元问题2治本（2026-06-30）：#ARCH-XXX 引用查重检测 ===
    _ARCH_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"
    _ARCH_PATTERN = re.compile(r'#ARCH-\d{3}\b')
    _ARCH_TEXT_EXTS = (".md", ".yaml", ".yml", ".py", ".txt")

    def _trigger_arch_refs(committed_files: list[str]) -> bool:
        # 文本文件可能含 #ARCH-XXX 引用
        for f in committed_files:
            if f.replace("\\", "/").lower().endswith(_ARCH_TEXT_EXTS):
                return True
        return False

    def _reconcile_arch_refs(committed_files: list[str], session_id: str) -> ReconcileResult:
        from pathlib import Path

        arch_registry = Path(project_root) / _ARCH_REGISTRY_REL
        if not arch_registry.exists():
            return ReconcileResult(action="clean", detail="architecture_issue_registry.yaml not found, skip ARCH refs check")

        # 加载注册表 entries（真源：architecture_issue_registry.yaml）
        try:
            import yaml
            data = yaml.safe_load(arch_registry.read_text(encoding="utf-8"))
            entries = data.get("entries", []) if isinstance(data, dict) else []
            registered_ids: set[str] = set()
            for entry in entries:
                if isinstance(entry, dict):
                    iid = entry.get("issue_id", "")
                    if isinstance(iid, str) and iid:
                        registered_ids.add(iid)
        except Exception as e:
            return ReconcileResult(action="warn", detail=f"failed to parse architecture_issue_registry: {e}")

        # 扫描 committed_files 中所有 #ARCH-XXX 引用
        referenced: set[str] = set()
        for f in committed_files:
            if not f.replace("\\", "/").lower().endswith(_ARCH_TEXT_EXTS):
                continue
            try:
                content = Path(f).read_text(encoding="utf-8")
                referenced.update(_ARCH_PATTERN.findall(content))
            except (OSError, UnicodeDecodeError):
                continue

        if not referenced:
            return ReconcileResult(action="clean", detail="no #ARCH-XXX refs in committed files")

        # 失效引用（引用了但不在注册表 entries 中）——铁律#6: 禁止 grep-and-claim 占位
        stale = referenced - registered_ids
        if stale:
            return ReconcileResult(
                action="warn",
                detail=f"committed files reference unregistered #ARCH-XXX ids: {sorted(stale)}. "
                       f"These ids not in architecture_issue_registry.yaml entries. "
                       f"Register them first or fix the reference (铁律#6: 禁止 grep-and-claim 占位).",
            )
        return ReconcileResult(action="clean", detail=f"all #ARCH-XXX refs registered ({len(referenced)} refs)")

    spec_arch_refs = ReconcilerSpec(
        gate_id="GATE-ARCH-REFS",
        trigger=_trigger_arch_refs,
        reconcile=_reconcile_arch_refs,
        priority=710,  # 最后执行（ARCH引用检测非阻断，低优先级）
    )

    return _compose_reconcilers("GATE-RULE-AUDIT", spec_catalog, spec_rule_file_audit, spec_arch_refs)


def make_registry_sync_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-REGISTRY-SYNC post-commit 注册表同步+基线对账 reconciler（AD-GOV-001 合并）。

    合并来源：
    - 旧 GATE-REGISTRY-INDEX (priority=155)：commit infrastructure_registry.yaml 后
      跑 generate_registry_master_index.py 重新生成 registry_master_index.yaml，
      有变更自动提交（校验+自动修复双闭环）。
    - 旧 GATE-REG-BL (priority=200)：commit src/zephyr/ 与 scripts/governance/ 下
      .py 后跑 audit_registration.py --baseline-aware 增量扫描 NEW 孤儿，记录报告。

    合并原因：两者均守护"注册表/基线一致性"，trigger 在 governance 域 .py 变更上
    重叠，逻辑可串联，合并形成"注册表索引同步+基线孤儿扫描"单入口。

    合并后执行：先重生成 registry_master_index，再跑 baseline-aware 孤儿扫描；
    action 取较严重，detail 拼接。priority=max(155,200)=200。

    治本（2026-06-30 元问题4）：reconcile 逻辑内联自原 _make_old_registry_index_reconciler
    与 _make_old_baseline_aware_reconciler，私有函数已删除。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root
    _INDEX_REL = "docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml"
    _INFRA_REL = "docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml"

    # === 旧 GATE-REGISTRY-INDEX 逻辑（内联自 _make_old_registry_index_reconciler）===
    def _trigger_index(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel == _INFRA_REL:
                return True
        return False

    def _reconcile_index(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 重新生成 registry_master_index（generate_registry_master_index.py 幂等）
        gen_result = _run_subprocess(
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

        # 3. 变更 -> 自动提交（经 _commit_auto 统一入口，DCR gate 覆盖）
        auto_msg = "chore(registry): auto-sync registry_master_index by GitCommitGateway post-commit"
        abs_files = [str(project_root / _INDEX_REL)]
        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)
        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="registry_master_index drift detected and auto-reconciled",
            )
        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="registry_master_index no drift (auto-commit found no staged changes)",
            )
        return ReconcileResult(
            action="warn",
            detail=f"registry_master_index drift detected, auto-commit failed ({commit_result.status}): "
                   f"{commit_result.message[:200]}",
        )

    spec_index = ReconcilerSpec(
        gate_id="GATE-REGISTRY-INDEX",
        trigger=_trigger_index,
        reconcile=_reconcile_index,
        priority=155,
    )

    # === 旧 GATE-REG-BL 逻辑（内联自 _make_old_baseline_aware_reconciler）===
    def _trigger_baseline(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel.startswith("src/zephyr/") and rel.endswith(".py"):
                return True
            if rel.startswith("scripts/governance/") and rel.endswith(".py"):
                return True
        return False

    def _reconcile_baseline(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. post-commit baseline-aware 扫描（非阻断）
        # 治本 Bug 1：改用 --files 传入精确 committed_files，替代 --incremental。
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
        scan_result = _run_subprocess(
            [sys.executable, "scripts/governance/d11_compliance/audit_registration.py",
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

    spec_baseline = ReconcilerSpec(
        gate_id="GATE-REG-BL",
        trigger=_trigger_baseline,
        reconcile=_reconcile_baseline,
        priority=200,
    )

    return _compose_reconcilers("GATE-REGISTRY-SYNC", spec_index, spec_baseline)


def make_integrity_audit_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-INTEGRITY-AUDIT post-commit 完整性+网关审计+引用检测 reconciler（AD-GOV-001 合并）。

    合并来源：
    - 旧 GATE-RULES-INTEGRITY (priority=270)：每次 commit 后跑
      validate_rules_integrity.py --register 重算 RULES_MANIFEST 文件 hash 写入
      本地基线，消除"C 层基线与 commit 不同步->误报 TAMPERED"结构性缺陷。
    - 旧 GATE-COMMIT-GW-AUDIT (priority=800)：扫描最近 20 个 commit，标记未经
      GitCommitGateway 的裸 commit（message 不含 [GW: 标记），告警 --no-verify 绕过。
    - 新增 GATE-AGENTS-MD-REFS (priority=810，元问题1治本 2026-06-30)：检测 AGENTS.md
      中引用的 reconciliation_registry.py 公共函数名（make_*_reconciler）是否在 __all__
      列表中。病根：AGENTS.md 硬编码函数名，reconciler 重命名/合并后 AGENTS.md 不会
      自动更新，新AI按失效指引造幻觉（如步骤1修复的 _make_old_rules_integrity_reconciler
      失效引用）。检测到失效引用->warn（非阻断，告警供人工修正）。

    合并原因：三者 trigger 均 always True 或与 AGENTS.md/reconciliation_registry.py
    变更相关，逻辑可串联，合并形成"基线同步+网关审计+引用检测"非阻断兜底单入口。

    合并后执行：先重注册 rules_integrity 基线，再审计 commit 网关标记，最后检测
    AGENTS.md 引用有效性；action 取较严重，detail 拼接。priority=max(270,800,810)=810。

    治本（2026-06-30 元问题4）：reconcile 逻辑内联自原 _make_old_rules_integrity_reconciler
    与 _make_old_commit_gateway_audit_reconciler，私有函数已删除。_audit_commit_history
    是模块级函数（非 _make_old_*），保留供本闭包调用与 integrity_anchors 保护。

    治本（2026-06-30 元问题1）：新增 AGENTS.md 引用有效性检测，合并入本 reconciler
    不新增 reconciler（trae_060 §4 审查通过：该存在+可合并入已有）。检测逻辑用正则
    提取 make_*_reconciler 公共函数名引用，检查是否在 __all__ 中。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root
    _VALIDATE_SCRIPT = "scripts/governance/meta/validate_rules_integrity.py"
    _AUDIT_WINDOW = 20  # 审计最近 20 个 commit
    _GW_MARKER = "[GW:"
    _RV_MARKER = "[RECONCILER-VERIFY]"  # reconciler-verify 豁免通道标记（事后审计追溯）

    # === 旧 GATE-RULES-INTEGRITY 逻辑（内联自 _make_old_rules_integrity_reconciler）===
    def _trigger_rules_integrity(committed_files: list[str]) -> bool:
        # 第一性原理治本：总是触发。原宽匹配基于未校验假设，未来 RULES_MANIFEST
        # 新增其他路径文件会假阴性漏触发。--register 仅 hash RULES_MANIFEST 文件
        # （毫秒级），不值得为省此开销引入假设。RULES_MANIFEST 真源在 validate_rules_integrity.py 顶部。
        return True

    def _reconcile_rules_integrity(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. post-commit 重注册基线（--register 内部读 RULES_MANIFEST 真源，重算全部 hash）
        # 红蓝发现4 治本：设置 ZEPHYR_RECONCILER_MODE=1 门禁令牌，允许 --register。
        _env = dict(os.environ)
        _env["ZEPHYR_RECONCILER_MODE"] = "1"
        reg_result = _run_subprocess(
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

    spec_rules_integrity = ReconcilerSpec(
        gate_id="GATE-RULES-INTEGRITY",
        trigger=_trigger_rules_integrity,
        reconcile=_reconcile_rules_integrity,
        priority=270,
    )

    # === 旧 GATE-COMMIT-GW-AUDIT 逻辑（内联自 _make_old_commit_gateway_audit_reconciler）===
    def _trigger_commit_gw_audit(committed_files: list[str]) -> bool:
        # 审计始终运行：绕过 gateway 的裸 commit 可能涉及任何文件
        return True

    def _reconcile_commit_gw_audit(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 审计逻辑真源：模块级 _audit_commit_history（A 层 AST 锚点保护，
        # 治本 2026-06-30 病根1 看门人无人看）。闭包只做调用 + 报告落盘 + 判定。
        violations, rv_uses, err = _audit_commit_history(
            project_root, _AUDIT_WINDOW, _GW_MARKER, _RV_MARKER,
        )
        if err:
            return ReconcileResult(action="warn", detail=err)

        # 3. 报告落盘
        report = {
            "gate_id": "GATE-COMMIT-GW-AUDIT",
            "session_id": session_id,
            "audit_window": _AUDIT_WINDOW,
            "violations_count": len(violations),
            "violations": violations,
            "reconciler_verify_uses_count": len(rv_uses),
            "reconciler_verify_uses": rv_uses,
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

    spec_commit_gw_audit = ReconcilerSpec(
        gate_id="GATE-COMMIT-GW-AUDIT",
        trigger=_trigger_commit_gw_audit,
        reconcile=_reconcile_commit_gw_audit,
        priority=800,  # 最后执行（审计非阻断，低优先级）
    )

    # === 元问题1治本（2026-06-30）：AGENTS.md 引用有效性检测 ===
    def _trigger_agents_md_refs(committed_files: list[str]) -> bool:
        # AGENTS.md 或 reconciliation_registry.py 变更时触发——引用关系在这两个文件
        # 变更时可能过时（reconciler 合并/重命名会导致 AGENTS.md 引用失效）
        for f in committed_files:
            fn = f.replace("\\", "/").lower()
            if "agents.md" in fn or "reconciliation_registry.py" in fn:
                return True
        return False

    def _reconcile_agents_md_refs(committed_files: list[str], session_id: str) -> ReconcileResult:
        import re
        from pathlib import Path

        agents_md = Path(project_root) / "AGENTS.md"
        if not agents_md.exists():
            return ReconcileResult(action="clean", detail="AGENTS.md not found, skip refs check")

        content = agents_md.read_text(encoding="utf-8")
        # 提取 AGENTS.md 中引用的 make_*_reconciler 公共函数名
        # （_make_old_* 私有函数引用是描述性提及"已删除"，不检测——私有函数不在 __all__ 是正常的）
        referenced = set(re.findall(r'\bmake_\w+_reconciler\b', content))
        if not referenced:
            return ReconcileResult(action="clean", detail="no make_*_reconciler refs in AGENTS.md")

        # 加载模块 __all__（真源：reconciliation_registry.__all__）
        try:
            import zephyr.governance.audit.reconciliation_registry as reg_module
            available = set(reg_module.__all__)
        except Exception as e:
            return ReconcileResult(action="warn", detail=f"failed to load reconciliation_registry: {e}")

        # 失效引用（AGENTS.md 引用了但不在 __all__ 中）
        stale = referenced - available
        if stale:
            return ReconcileResult(
                action="warn",
                detail=f"AGENTS.md references stale reconciliation_registry functions: {sorted(stale)}. "
                       f"These functions not in __all__. Update AGENTS.md to reference valid function names.",
            )
        return ReconcileResult(action="clean", detail=f"AGENTS.md refs all valid ({len(referenced)} refs)")

    spec_agents_md_refs = ReconcilerSpec(
        gate_id="GATE-AGENTS-MD-REFS",
        trigger=_trigger_agents_md_refs,
        reconcile=_reconcile_agents_md_refs,
        priority=810,  # 最后执行（引用检测非阻断，最低优先级）
    )

    return _compose_reconcilers("GATE-INTEGRITY-AUDIT", spec_rules_integrity, spec_commit_gw_audit, spec_agents_md_refs)


# trae_060-reviewed: 通过§4元问题审查。该 reconciler 该存在——三声明轨道 module_id（CFG-/MOD-/PS-*）语义此前未定义，
# 导致 AI 误判为冲突并反复"修复"。不能删除（检测需求真实），不能合并（现有 reconciler 无 module_id 三声明轨道校验逻辑）。
# 治本：S0-3 已在 PS-STD-001 定义三声明轨道语义，本 reconciler 自动校验一致性（非阻断，仅告警）。
# 向内收：扩展已有 reconciliation_registry.py 框架（第12个 reconciler），不新建独立系统。
# P8-FIX-S1 扩展：增加 count 派生校验（total_registered/total_templates/total_dependencies）。
#   元问题审查：count 不一致是真实漂移源（template_registry 声明 14 但实际 13）。
#   能否合并：是——扩展本 reconciler 职责，不新建 count_reconciler（向内收）。
def make_module_id_consistency_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-MODULE-ID-CONSISTENCY post-commit 注册表一致性校验 reconciler（P8-FIX-S0 + S1）。

    病根：单个治理文件中同时出现三种 module_id 声明（头部 CFG-* + 锚定 MOD-* +
    body PS-*/GOV-*），语义未定义导致 AI 误判为冲突并反复"修复"。

    治本（P8-FIX-S0 v2.4.0，2026-06-30）：
    - S0-3 已在 PS-STD-001 §5 定义三声明轨道语义（header_config_id / anchor_module_ownership /
      body_rule_id），明确三者互补不冲突。
    - 本 reconciler 在 post-commit 自动校验三声明轨道一致性——检查三者是否在
      module_id_registry.yaml 中归属同一模块。不一致->warn（非阻断）。

    P8-FIX-S1 扩展（2026-06-30）：count 派生校验
    - 注册表的 count 字段（total_registered/total_templates/total_dependencies）是派生数据，
      手工维护导致漂移（如 template_registry 声明 14 但实际 13）。
    - 扩展本 reconciler 增加 count 校验：统计列表条目数，与声明的 count 比对，不一致->warn。
    - 向内收：不新建 count_reconciler，扩展已有 module_id_consistency_reconciler 职责。

    设计裁定（非阻断）：
    post-commit 无法回滚 commit；不一致已入 git 历史，仅告警记录到
    .runtime/reconcile_reports/module_id_consistency_<ts>.json，供人工修正。

    trigger 裁定：committed_files 含 module_id_registry.yaml / template_registry.yaml /
    cross_module_dependency_registry.yaml 或 _registry/contracts/ 下的 .yaml 文件即命中。

    向内收设计：
    - 责任唯一：三声明轨道语义定义在 PS-STD-001 §5，校验逻辑在本 reconciler 单点
    - 真源唯一：复用 ReconciliationRegistry 框架（第12个 reconciler）
    - 事件触发：post-commit 自动执行，无 cron/manual

    Args:
        gateway: GitCommitGateway 实例（用 project_root）。

    Returns:
        ReconcilerSpec(gate_id="GATE-MODULE-ID-CONSISTENCY", priority=300)。
    """
    import os
    import re

    project_root = gateway.project_root
    _REGISTRY_REL = "architecture_model/module_id_registry.yaml"
    _TEMPLATE_REGISTRY_REL = "docs/03_modules/template_registry.yaml"
    _DEP_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/cross_module_dependency_registry.yaml"
    _CONTRACTS_DIR = "docs/01_policies_and_standards/_registry/contracts/"

    # 三声明轨道正则
    _RE_HEADER_CFG = re.compile(r"^#\s*\[A_config\]\s*module_id=(CFG-\S+)", re.MULTILINE)
    _RE_ANCHOR_MOD = re.compile(r"^#\s*module_id:\s*(MOD-\S+)", re.MULTILINE)
    _RE_BODY_RULE = re.compile(r"^module_id:\s*([A-Z]+(?:-[A-Z]+)*-\w+)\s*$", re.MULTILINE)

    # P8-FIX-S1: count 派生校验——统计列表条目数正则
    _RE_MODULE_ID_ENTRY = re.compile(r"^  - module_id:\s*\S+", re.MULTILINE)
    _RE_TEMPLATE_ENTRY = re.compile(r"^  - template_id:", re.MULTILINE)
    _RE_DEP_ENTRY = re.compile(r"^- dep_id:\s*DEP-", re.MULTILINE)

    # P8-FIX-S1: count 声明读取正则
    _RE_TOTAL_REGISTERED = re.compile(r"^total_registered:\s*(\d+)", re.MULTILINE)
    _RE_TOTAL_TEMPLATES = re.compile(r"^\s*total_templates:\s*(\d+)", re.MULTILINE)
    _RE_TOTAL_DEPS = re.compile(r"^\s*total_dependencies:\s*(\d+)", re.MULTILINE)

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if (rel == _REGISTRY_REL or rel == _TEMPLATE_REGISTRY_REL
                    or rel == _DEP_REGISTRY_REL or rel.startswith(_CONTRACTS_DIR)):
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        violations = []
        checked = 0

        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if (rel != _REGISTRY_REL and rel != _TEMPLATE_REGISTRY_REL
                    and rel != _DEP_REGISTRY_REL and not rel.startswith(_CONTRACTS_DIR)):
                continue

            abs_path = project_root / rel
            if not abs_path.exists():
                continue

            try:
                content = abs_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            checked += 1

            # === 三声明轨道一致性校验（P8-FIX-S0） ===
            cfg_match = _RE_HEADER_CFG.search(content)
            mod_match = _RE_ANCHOR_MOD.search(content)
            rule_match = _RE_BODY_RULE.search(content)

            cfg_id = cfg_match.group(1) if cfg_match else None
            mod_id = mod_match.group(1) if mod_match else None
            rule_id = rule_match.group(1) if rule_match else None

            tracks_found = sum(1 for x in [cfg_id, mod_id, rule_id] if x)
            if tracks_found < 2 and cfg_id:
                violations.append({
                    "file": rel,
                    "issue": "incomplete_tracks",
                    "cfg_id": cfg_id,
                    "mod_id": mod_id,
                    "rule_id": rule_id,
                    "detail": f"文件有 header CFG-{cfg_id} 但仅 {tracks_found}/3 声明轨声明",
                })

            # === count 派生校验（P8-FIX-S1） ===
            if rel == _REGISTRY_REL:
                actual_count = len(_RE_MODULE_ID_ENTRY.findall(content))
                declared = _RE_TOTAL_REGISTERED.search(content)
                declared_count = int(declared.group(1)) if declared else None
                if declared_count is not None and declared_count != actual_count:
                    violations.append({
                        "file": rel,
                        "issue": "count_mismatch",
                        "field": "total_registered",
                        "declared": declared_count,
                        "actual": actual_count,
                        "detail": f"total_registered={declared_count} 但实际 registered_ids 有 {actual_count} 条",
                    })
            elif rel == _TEMPLATE_REGISTRY_REL:
                actual_count = len(_RE_TEMPLATE_ENTRY.findall(content))
                declared = _RE_TOTAL_TEMPLATES.search(content)
                declared_count = int(declared.group(1)) if declared else None
                if declared_count is not None and declared_count != actual_count:
                    violations.append({
                        "file": rel,
                        "issue": "count_mismatch",
                        "field": "total_templates",
                        "declared": declared_count,
                        "actual": actual_count,
                        "detail": f"total_templates={declared_count} 但实际 templates 有 {actual_count} 条",
                    })
            elif rel == _DEP_REGISTRY_REL:
                actual_count = len(_RE_DEP_ENTRY.findall(content))
                declared = _RE_TOTAL_DEPS.search(content)
                declared_count = int(declared.group(1)) if declared else None
                if declared_count is not None and declared_count != actual_count:
                    violations.append({
                        "file": rel,
                        "issue": "count_mismatch",
                        "field": "total_dependencies",
                        "declared": declared_count,
                        "actual": actual_count,
                        "detail": f"total_dependencies={declared_count} 但实际 dependencies 有 {actual_count} 条",
                    })

        report = {
            "gate_id": "GATE-MODULE-ID-CONSISTENCY",
            "session_id": session_id,
            "checked_files": checked,
            "violations": violations,
        }
        report_path, write_err = _write_reconcile_report(project_root, "module_id_consistency", report)
        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"module_id consistency check done ({checked} files) but report write failed: {write_err}",
            )

        if not violations:
            return ReconcileResult(
                action="clean",
                detail=f"module_id consistency check clean ({checked} files), report={report_path.name}",
            )
        return ReconcileResult(
            action="warn",
            detail=f"module_id consistency check found {len(violations)} violations in {checked} files, report={report_path.name}",
        )

    return ReconcilerSpec(
        gate_id="GATE-MODULE-ID-CONSISTENCY",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=300,
    )


# trae_060-reviewed: P3 生成器自动触发接入——index_generator(infrastructure/asset_inventory)
# 接入 GitCommitGateway post-commit reconciler 轨（非 boot_hooks 事件轨）。
# 向内收：扩展已有 reconciliation_registry.py 框架（第14个 reconciler），不新建独立触发系统。
# 价值审判：index_generator 是 production 资产索引真源，unified-asset-index.yaml 漂移需自动修复。
def make_index_generator_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-ASSET-INDEX post-commit 资产索引重生 reconciler（P3 生成器触发接入）。

    病根：index_generator 是 MOD-INF-026 production 生成器，产出 unified-asset-index.yaml
    作为项目 SSoT。但 src/zephyr/**/*.py 或注册表 yaml 变更后，索引可能过时——
    原设计无自动触发，依赖手动跑 ``python -m zephyr.infrastructure.asset_inventory bootstrap``。

    治本（P3 生成器自动触发接入）：
    - 接入 GitCommitGateway post-commit reconciler 轨（事件触发，非时间触发/手动触发）
    - trigger: committed_files 含 src/zephyr/**/*.py 或注册表 yaml 变更
    - reconcile: 跑 scan->classify->index 全管线（bootstrap 幂等），检测 unified-asset-index.yaml
      漂移，有变更->auto-commit（经 _commit_auto 统一入口，DCR gate 覆盖）

    trigger 裁定（注册表路径真源：index_generator.py REGISTRY_DIRS）：
    - src/zephyr/**/*.py：资产文件变更->索引可能漂移
    - src/zephyr/governance/rule_enforcement/_registry.yaml：gates 注册表变更
    - docs/03_modules/module-registry.yaml：模块注册表变更
    - docs/03_modules/blueprint_registry.yaml：蓝图注册表变更

    向内收设计：
    - 责任唯一：索引生成逻辑只在 IndexGenerator 一处（本 reconciler 仅调用，不复制逻辑）
    - 真源唯一：复用 ReconciliationRegistry 框架（第14个 reconciler），不新建独立触发系统
    - 事件触发：post-commit 自动执行，无 cron/manual

    Args:
        gateway: GitCommitGateway 实例（用 project_root + _run_git + _commit_auto）。

    Returns:
        ReconcilerSpec(gate_id="GATE-ASSET-INDEX", priority=170)。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root
    _INDEX_REL = "data/asset_index/unified-asset-index.yaml"
    # 注册表路径真源：index_generator.py REGISTRY_DIRS
    _REGISTRY_PATHS = (
        "src/zephyr/governance/rule_enforcement/_registry.yaml",
        "docs/03_modules/module-registry.yaml",
        "docs/03_modules/blueprint_registry.yaml",
    )

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel.startswith("src/zephyr/") and rel.endswith(".py"):
                return True
            if rel in _REGISTRY_PATHS:
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 跑 scan->classify->index 全管线（bootstrap 幂等，含 index 生成）
        bootstrap_result = _run_subprocess(
            [sys.executable, "-m", "zephyr.infrastructure.asset_inventory", "bootstrap"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,  # 全管线较慢（scan+classify+index+reconcile+dashboard）
        )
        if bootstrap_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"asset_inventory bootstrap failed: {bootstrap_result.stderr.strip()[:200]}",
            )

        # 2. 检测 unified-asset-index.yaml 变更
        diff_result = gateway._run_git(
            ["git", "diff", "--name-only", "--", _INDEX_REL]
        )
        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="unified-asset-index up to date")

        # 3. 变更 -> 自动提交（经 _commit_auto 统一入口，DCR gate 覆盖）
        abs_files = [str(project_root / _INDEX_REL)]
        auto_msg = "chore(asset_index): auto-regenerate unified-asset-index.yaml by GitCommitGateway post-commit"
        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)
        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="unified-asset-index drift detected and auto-regenerated",
            )
        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="unified-asset-index no drift (auto-commit found no staged changes)",
            )
        return ReconcileResult(
            action="warn",
            detail=f"unified-asset-index drift detected, auto-commit failed ({commit_result.status}): "
                   f"{commit_result.message[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-ASSET-INDEX",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=170,  # 在 path_tree(150) 和 yaml_sync(160) 之后，vocab_change(280) 之前
    )


# trae_060-reviewed: 通过元问题审查。.runtime/ 线性增长无封顶（4100+ 文件），需 TTL 自动清理。
# 该 reconciler 该存在——扩展已有 reconciliation_registry 框架（第15个 reconciler），
# 事件触发（post-commit），非 cron/manual，满足项目约束"reconciler 必须事件触发"。
def make_runtime_cleanup_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-RUNTIME-CLEANUP post-commit .runtime/ TTL 清理 reconciler。

    病根：.runtime/ 是项目运行时产物目录（.gitignore 豁免），但无自动清理机制——
    handoffs/（700+ session 交接包）、reconcile_reports/（2900+ 对账报告）、root-level
    temp files 线性增长，总计 4100+ 文件，GOV-DOC-018 文件夹容量阈值超标。

    治本（事件触发 TTL 清理）：
    - trigger: 每次 commit 都触发（扫描 4100 文件 mtime 成本 <0.1s）
    - reconcile: 删除 mtime > 7 天的文件，保留 .gitkeep（目录标记）和 .jsonl（审计日志）
    - 自维护/自关闭：每次 commit 后自动清理，返回 ReconcileResult

    保护规则（第一性原理：只删临时产物，保留有状态的持久文件）：
    - .gitkeep：目录结构标记
    - *.jsonl：append-only 审计日志
    - 其余 >7 天文件：临时产物，过期安全删除

    向内收：扩展 ReconciliationRegistry 框架（第15个 reconciler），不新建独立清理系统。
    复用 _GlobalCommitLock 的 TTL+mtime 模式。
    """
    import os
    import time

    project_root = gateway.project_root
    _TTL_SECONDS = 7 * 86400  # 7 天
    _PROTECTED_NAMES = {".gitkeep"}
    _PROTECTED_SUFFIX = ".jsonl"

    def _trigger(committed_files: list[str]) -> bool:
        return True  # .runtime/ 增长与每次 commit 正相关

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        runtime_dir = project_root / ".runtime"
        if not runtime_dir.exists():
            return ReconcileResult(action="skip", detail=".runtime/ not found")

        now = time.time()
        deleted = 0
        errors = 0
        for dirpath, _dirnames, filenames in os.walk(runtime_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    mtime = os.path.getmtime(filepath)
                    if now - mtime < _TTL_SECONDS:
                        continue  # 仍在 TTL 内
                    if filename in _PROTECTED_NAMES:
                        continue  # 目录结构标记
                    if filename.endswith(_PROTECTED_SUFFIX):
                        continue  # append-only 审计日志
                    os.remove(filepath)
                    deleted += 1
                except OSError:
                    errors += 1

        return ReconcileResult(
            action="clean" if errors == 0 else "warn",
            detail=f".runtime/ TTL cleanup: deleted={deleted}, errors={errors}",
        )

    return ReconcilerSpec(
        gate_id="GATE-RUNTIME-CLEANUP",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=50,  # 在所有 reconciler 之前执行——先清理旧文件
    )


# trae_060-reviewed: 架构健康度仪表盘 post-commit 基线记录（第0期 warn-only，architecture_debt_registry.md §六）。
# 触发条件：任何 .py 文件变更（11 项指标覆盖代码/脚本/门禁/depgraph 维度）
# 行为：subprocess 调用 architecture_health_dashboard.py --snapshot 保存基线快照到 data/architecture_health/
# 非阻断：ReconcileResult(action="clean"/"warn")，第0期仅记录基线不阻断 commit
# 第1期升级路径：转为 pre-commit commit gate（exit 1 阻断），见 architecture_debt_registry.md §六 第1期
def make_architecture_health_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造架构健康度仪表盘 post-commit 基线记录 reconciler（第0期 warn-only）。

    architecture_debt_registry.md §六 第0期：每次 commit 自动生成架构健康度指标快照，
    替代手动调研。仪表盘 11 项指标（M01-M11），warn-only 模式（exit 0 不阻断 commit）。

    对账链：
    1. trigger: committed_files 含 .py 文件 -> 命中
    2. subprocess 调用 architecture_health_dashboard.py --snapshot
    3. 快照保存到 data/architecture_health/dashboard_<ts>.json + latest.json
    4. 返回 ReconcileResult(action="clean"/"warn")，不阻断 commit

    第1期升级路径：转为 pre-commit commit gate（exit 1 阻断），见
    architecture_debt_registry.md §六 第1期。

    Args:
        gateway: GitCommitGateway 实例（仅用其 project_root）。

    Returns:
        ReconcilerSpec(gate_id="GATE-ARCH-HEALTH", priority=300)。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root
    dashboard = project_root / "scripts" / "governance" / "architecture_health_dashboard.py"

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel.endswith(".py"):
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        if not dashboard.exists():
            return ReconcileResult(action="skip", detail="dashboard script not found")
        try:
            result = _run_subprocess(
                [sys.executable, str(dashboard), "--snapshot"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(project_root),
                timeout=120,
            )
            if result.returncode == 0:
                return ReconcileResult(
                    action="clean",
                    detail="architecture health baseline snapshot saved (warn-only, Phase 0)",
                )
            else:
                return ReconcileResult(
                    action="warn",
                    detail=f"dashboard exit code {result.returncode}: {result.stderr[:200]}",
                )
        except subprocess.TimeoutExpired:
            return ReconcileResult(action="warn", detail="dashboard timeout after 120s")
        except Exception as e:  # noqa: BLE001 — drift 对账非阻断
            return ReconcileResult(action="warn", detail=f"dashboard failed: {e}")

    return ReconcilerSpec(
        gate_id="GATE-ARCH-HEALTH",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=300,  # 低优先级最后执行——基线记录非紧急
    )


# AI-03 审计 P3 待办落地（2026-07-05）：session_logs/index.yaml 派生 reconciler。
# 病根：index.yaml 的 by_date/by_module/by_contract 派生数据截至 2026-05-08 未更新，
#   派生脚本（validate_session_log_index_integrity.py --generate）无自动触发机制。
# 治本：接入 GitCommitGateway post-commit reconciler 轨（事件触发，非时间触发/手动触发）。
# 向内收：扩展已有 reconciliation_registry.py 框架（第18个 reconciler），不新建独立触发系统。
# 真源：validate_session_log_index_integrity.py 是 index.yaml 派生逻辑唯一真源，本 reconciler 仅调用。
# trae_060-reviewed: 通过元问题审查。session_logs/index.yaml 派生数据过期是真实问题（截至 2026-05-08
# 未更新），需自动触发机制。现有 17 个 reconciler 无一处理 session_logs/ 目录，无法合并进已有。
# 事件触发（post-commit: session_logs/**/*.yaml 落盘），非 cron/manual，满足项目约束"reconciler 必须事件触发"。
# 派生逻辑真源唯一：validate_session_log_index_integrity.py --generate（本 reconciler 仅调用，不复制逻辑）。
def make_session_log_index_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-SESSION-LOG-INDEX post-commit session_logs/index.yaml 派生 reconciler。

    病根：session_logs/index.yaml 的 by_date/by_module/by_contract 派生数据由
    ``validate_session_log_index_integrity.py --generate`` 从 session log YAML 派生，
    但原设计无自动触发机制——新 session yaml 落盘后 index.yaml 不会自动更新，
    导致索引过期（截至 2026-05-08 未更新，AI-03 审计 P3）。

    治本（事件触发派生）：
    - 接入 GitCommitGateway post-commit reconciler 轨（事件触发，非 cron/manual）
    - trigger: committed_files 含 session_logs/**/*.yaml 且非 index.yaml 本身
    - reconcile: 调用 validate_session_log_index_integrity.py --generate，
      检测 index.yaml 变更，有变更->auto-commit（经 _commit_auto 统一入口，DCR gate 覆盖）

    trigger 裁定（派生真源：validate_session_log_index_integrity.py L88-99）：
    - session_logs/**/*.yaml（排除 _auto/ 子目录和 index.yaml 本身）

    向内收设计：
    - 责任唯一：派生逻辑只在 validate_session_log_index_integrity.py 一处（本 reconciler 仅调用）
    - 真源唯一：复用 ReconciliationRegistry 框架（第18个 reconciler），不新建独立触发系统
    - 事件触发：post-commit 自动执行，无 cron/manual

    Args:
        gateway: GitCommitGateway 实例（用 project_root + _run_git + _commit_auto）。

    Returns:
        ReconcilerSpec(gate_id="GATE-SESSION-LOG-INDEX", priority=175)。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root
    _INDEX_REL = "session_logs/index.yaml"
    _VALIDATOR_REL = "scripts/governance/d5_architecture/validators/session/validate_session_log_index_integrity.py"

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            # 命中 session_logs/**/*.yaml，排除 index.yaml 本身和 _auto/ 派生产物
            if (
                rel.startswith("session_logs/")
                and rel.endswith(".yaml")
                and rel != _INDEX_REL
                and "/_auto/" not in rel
            ):
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        validator = project_root / _VALIDATOR_REL
        if not validator.exists():
            return ReconcileResult(
                action="warn",
                detail=f"validator script not found: {_VALIDATOR_REL}",
            )

        # 1. 调用 validate_session_log_index_integrity.py --generate（校验 + 汇总生成）
        gen_result = _run_subprocess(
            [
                sys.executable,
                str(validator),
                "--generate",
            ],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,  # 扫描 session_logs/ 较快（<50 文件）
        )
        if gen_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"validator --generate failed (exit {gen_result.returncode}): "
                       f"{gen_result.stderr.strip()[:200]}",
            )

        # 2. 检测 index.yaml 变更
        diff_result = gateway._run_git(
            ["git", "diff", "--name-only", "--", _INDEX_REL]
        )
        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="session_logs/index.yaml up to date")

        # 3. 变更 -> 自动提交（经 _commit_auto 统一入口，DCR gate 覆盖）
        abs_files = [str(project_root / _INDEX_REL)]
        auto_msg = "chore(session_logs): auto-regenerate index.yaml by GitCommitGateway post-commit"
        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)
        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="session_logs/index.yaml drift detected and auto-regenerated",
            )
        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="session_logs/index.yaml no drift (auto-commit found no staged changes)",
            )
        return ReconcileResult(
            action="warn",
            detail=f"session_logs/index.yaml drift detected, auto-commit failed ({commit_result.status}): "
                   f"{commit_result.message[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-SESSION-LOG-INDEX",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=175,  # 在 index_generator(170) 之后，runtime_cleanup 之前
    )


# 病根：02_enterprise_architecture 下 9 个架构图生成器无自动触发，depgraph/dataflow/decision
# PG 或 YAML 真源变更后架构图 MD 过时。原 make_regenerate_reconciler 仅覆盖 domain_doc/
# domain_dependency_diagram/domain_index + arch_model + script_manifest，不含
# decision/dataflow/integration/cross_domain/constraint/capacity/capability/navigation。
# 治本：扩展 ReconciliationRegistry 框架（第19个 reconciler），事件触发，非 cron/manual。
# 三图对齐：depgraph(600-620)+dataflow(630)+decision(630) trigger 对齐，priority 相邻。
# trae_060-reviewed: 该存在（9 个生成器无自动触发是真实问题），不能合并进已有 reconciler
#   （已有 make_regenerate_reconciler 仅含 domain_doc/arch_model/manifest，trigger 虽重叠但
#   输出目标不同——9 个架构图 MD 是独立输出，需独立 reconciler），治本（事件触发+auto-commit）。
def make_arch_diagram_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-ARCH-DIAGRAM post-commit 架构图自动重生 reconciler（议题3）。

    病根：``docs/02_enterprise_architecture/`` 下 9 个架构图生成器无自动触发机制——
    depgraph/dataflow/decision PG 表变更或 YAML 真源变更后，架构图 MD 文档过时，
    依赖手动跑各生成器。这违反"永久系统必须全自动"硬约束。

    治本（事件触发自动重生，三图对齐）：
    - 接入 GitCommitGateway post-commit reconciler 轨（事件触发，非 cron/manual）
    - trigger: PG 写入脚本 commit OR YAML 真源变更 -> 命中
    - reconcile: 串联跑 12 个生成器，检测漂移，auto-commit

    涵盖生成器（输出均在 docs/02_enterprise_architecture/）：
      1. generate_decision_diagram.py        -> 06_decision_architecture/decision_index.md
      2. generate_dataflow_diagram.py        -> 05_dataflow_architecture/dataflow_index.md
      3. generate_integration_topology.py     -> 01_global_architecture_diagram/integration_topology.md
      4. generate_design_vs_production.py    -> 03_governance_reports/design_vs_production.md
      5. generate_cross_domain_matrix.py     -> 01_global_architecture_diagram/cross_domain_matrix.md
      6. generate_constraint_violations.py    -> 03_governance_reports/constraint_violations.md
      7. generate_capacity_report.py         -> 03_governance_reports/capacity_report.md
      8. generate_capability_heatmap.py       -> 01_global_architecture_diagram/global_capability_heatmap.md
      9. generate_navigation_index.py         -> 00_overview_entry/navigation_index.md
     10. generate_panorama_registry.py        -> 00_overview_entry/panorama_registry.md
     11. align_panoramas.py                   -> generated/panorama_alignment_report.md（ARCH-053 三图对齐检测器）
     12. generate_asset_catalog.py            -> 01_global_architecture_diagram/asset_catalog.md（#179/#180/#181/#182 资产清单）

    已覆盖（不在本 reconciler 范围，由 make_regenerate_reconciler 处理）：
      - generate_domain_doc.py --all
      - generate_domain_dependency_diagram.py --all
      - generate_domain_index.py
      - dm200916_write_direct.py（根树 index.yaml）
    已覆盖（由 make_path_tree_reconciler 处理）：
      - generate_path_tree.py

    trigger 真源：
      - PG 写入脚本（DB 变更即代表架构可能漂移）：
        apply_depgraph.py / sync_yaml_to_depgraph.py / generate_project_path_tree.py /
        generate_decision_graph.py（decisiongraph sync 入口）
      - YAML 真源（架构图直接数据源）：
        architecture_model/domain/decision_graph_model.yaml
        docs/01_policies_and_standards/_registry/catalogs/dataflow_graph_registry.yaml
        architecture_model/cross_cutting/capability_heatmap.yaml

    向内收设计：
    - 责任唯一：生成逻辑只在各生成器一处（本 reconciler 仅调用，不复制逻辑）
    - 真源唯一：复用 ReconciliationRegistry 框架（第19个 reconciler），不新建独立触发系统
    - 事件触发：post-commit 自动执行，无 cron/manual
    - 三图对齐：depgraph(600) / dataflow(630) / decision(630) 三图 trigger+priority 对齐

    Args:
        gateway: GitCommitGateway 实例（用 project_root + _run_git + _commit_auto）。

    Returns:
        ReconcilerSpec(gate_id="GATE-ARCH-DIAGRAM", priority=630)。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    # PG 写入脚本真源（DB 变更即代表架构图可能漂移）
    _PG_WRITE_SCRIPTS = (
        "scripts/governance/apply_depgraph.py",
        "scripts/governance/apply_decisiongraph.py",  # decisiongraph DB 写入入口（节点/边增删改）
        "scripts/governance/apply_dataflowgraph.py",  # dataflowgraph DB 写入入口 #ARCH-053
        "scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py",
        "scripts/governance/generate_project_path_tree.py",
        "scripts/governance/generate_decision_graph.py",  # decisiongraph sync 入口
    )
    # YAML 真源（架构图直接数据源）
    _YAML_SOURCES = (
        "architecture_model/domain/decision_graph_model.yaml",
        "docs/01_policies_and_standards/_registry/catalogs/dataflow_graph_registry.yaml",
        "architecture_model/cross_cutting/capability_heatmap.yaml",
        # 资产 YAML 真源（#179/#180/#181/#182）：变更触发 asset_catalog.md 重生
        "architecture_model/data/data_sources_registry.yaml",
        "architecture_model/data/data_source_apis_registry.yaml",
        "architecture_model/runtime/service_registry.yaml",
        "architecture_model/contracts/cross_layer_contracts.yaml",
    )

    _GEN_DIR = "scripts/governance/d5_architecture/generators"
    # 13 个生成器 + 输出路径（漂移检测目标）
    _GENERATORS = (
        "generate_decision_diagram.py",
        "generate_dataflow_diagram.py",
        "generate_integration_topology.py",
        "generate_design_vs_production.py",
        "generate_cross_domain_matrix.py",
        "generate_constraint_violations.py",
        "generate_capacity_report.py",
        "generate_capability_heatmap.py",
        "generate_navigation_index.py",
        "generate_panorama_registry.py",  # 全景图清单总表（00_overview_entry/panorama_registry.md）
        "align_panoramas.py",  # ARCH-053 三图对齐检测器（manual，但 PG 写入后自动重生）
        "generate_asset_catalog.py",  # #179/#180/#181/#182 资产清单全景图（256 项资产）
        "generate_policies.py",  # #183 数据源策略派生（data_sources_registry.yaml → policies.yaml）
    )
    _OUTPUTS = (
        "docs/02_enterprise_architecture/06_decision_architecture/decision_index.md",
        "docs/02_enterprise_architecture/05_dataflow_architecture/dataflow_index.md",
        "docs/02_enterprise_architecture/01_global_architecture_diagram/integration_topology.md",
        "docs/02_enterprise_architecture/03_governance_reports/design_vs_production.md",
        "docs/02_enterprise_architecture/01_global_architecture_diagram/cross_domain_matrix.md",
        "docs/02_enterprise_architecture/03_governance_reports/constraint_violations.md",
        "docs/02_enterprise_architecture/03_governance_reports/capacity_report.md",
        "docs/02_enterprise_architecture/01_global_architecture_diagram/global_capability_heatmap.md",
        "docs/02_enterprise_architecture/00_overview_entry/navigation_index.md",
        "docs/02_enterprise_architecture/00_overview_entry/panorama_registry.md",
        "docs/02_enterprise_architecture/generated/panorama_alignment_report.md",  # ARCH-053
        "docs/02_enterprise_architecture/01_global_architecture_diagram/asset_catalog.md",  # #179/#180/#181/#182
        "src/zephyr/data/config/policies.yaml",  # #183 数据源策略派生物
    )

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel in _PG_WRITE_SCRIPTS:
                return True
            if rel in _YAML_SOURCES:
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 1. 串联跑 13 个生成器（无 --all 参数，直接运行；幂等：相同输入->相同输出）
        failed_gens: list[str] = []
        for gen_name in _GENERATORS:
            gen_result = _run_subprocess(
                [sys.executable, f"{_GEN_DIR}/{gen_name}"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,  # 单个生成器最多 3 分钟（depgraph 查询 + MD 写入）
            )
            if gen_result.returncode != 0:
                failed_gens.append(
                    f"{gen_name}: {gen_result.stderr.strip()[:120]}"
                )
                # 不 return，继续跑剩余生成器（部分漂移修复优于全跳过）

        if failed_gens and len(failed_gens) == len(_GENERATORS):
            # 全部失败 -> warn 直接返回（无漂移可检测）
            return ReconcileResult(
                action="warn",
                detail=f"all {len(_GENERATORS)} generators failed: {'; '.join(failed_gens[:3])}",
            )

        # 2. 检测输出文件变更（即使部分生成器失败，已成功的可能产生漂移）
        diff_result = gateway._run_git(
            ["git", "diff", "--name-only", "--", *_OUTPUTS]
        )
        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            if failed_gens:
                return ReconcileResult(
                    action="warn",
                    detail=f"no drift but {len(failed_gens)} generator(s) failed: {'; '.join(failed_gens[:3])}",
                )
            return ReconcileResult(action="clean", detail="arch diagrams up to date")

        # 3. 变更 -> 自动提交（经 _commit_auto 统一入口，DCR gate 覆盖）
        changed_files = [
            f.strip() for f in diff_result.stdout.splitlines() if f.strip()
        ]
        abs_files = [str(project_root / f) for f in changed_files]
        auto_msg = "chore(arch): auto-regenerate architecture diagrams by GitCommitGateway post-commit"
        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)
        if commit_result.status == "OK":
            detail = f"arch diagrams drift detected and auto-regenerated ({len(changed_files)} files)"
            if failed_gens:
                detail += f"; {len(failed_gens)} generator(s) failed: {'; '.join(failed_gens[:3])}"
            return ReconcileResult(action="auto_committed", detail=detail)
        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="arch diagrams no drift (auto-commit found no staged changes)",
            )
        return ReconcileResult(
            action="warn",
            detail=f"arch diagrams drift detected, auto-commit failed ({commit_result.status}): "
                   f"{commit_result.message[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-ARCH-DIAGRAM",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=630,  # 在 regenerate(600-620) 之后，rule_audit(700-710) 之前
    )


# 病根：generate_constraint_violations.py 只读不检测，arch_constraints 表 56 条全部默认
# open，无检测器写入 violation_status/details/detected_at。链路断裂。
# 该存在：检测器是独立职责（检测 vs 展示），不能合并进生成器。
# 治本：事件触发（PG 写入脚本 commit）+ 跑检测器写 PG。
# trae_060-reviewed: 该存在（检测器是独立职责，不能合并进生成器），治本（事件触发+写PG）
def make_constraint_detect_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-CONSTRAINT-DETECT post-commit 架构违规检测 reconciler。

    病根：``generate_constraint_violations.py`` 只读 ``arch_constraints`` 表生成 MD 报告，
    但没有任何检测器实际检测违规并写入 ``violation_status``/``details``/``detected_at``。
    导致报告中 56 条约束全部默认 ``open``，无法区分真违规和正常约束——链路断裂。

    治本（补齐断链的检测层）：
    - 接入 GitCommitGateway post-commit reconciler 轨（事件触发，非 cron/manual）
    - trigger: PG 写入脚本 commit -> 命中（与 GATE-ARCH-DIAGRAM 相同 trigger）
    - reconcile: 跑 ``detect_constraint_violations.py``，5 类检测 -> 写 PG

    5 类检测（写入 constraint_type 区分规则定义和检测结果）：
      1. cross_domain_violation — 跨域违规（import 跨域但未在 domain_dependencies 声明）
      2. capacity_exceeded — 容量超限（production 节点 > max_modules，ARCH-CAP-001）
      3. hard_limit_exceeded — 硬上限违规（production 节点 > 150，ARCH-CAP-002 v1.0.8）
      4. orphan_node — 孤儿节点（路径未注册到 arch_directory_tree）
      5. layer_violation — 层级违规（低层依赖高层）

    链路（与 GATE-ARCH-DIAGRAM 协作）：
      1. GATE-CONSTRAINT-DETECT (625): 跑检测器，写 PG arch_constraints 表
      2. GATE-ARCH-DIAGRAM (630): 跑生成器，读 PG（含新检测结果），生成 MD，auto-commit

    Args:
        gateway: GitCommitGateway 实例（用 project_root）。

    Returns:
        ReconcilerSpec(gate_id="GATE-CONSTRAINT-DETECT", priority=625)。
    """
    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    # PG 写入脚本真源（DB 变更即代表可能产生新违规）
    _PG_WRITE_SCRIPTS = (
        "scripts/governance/apply_depgraph.py",
        "scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py",
        "scripts/governance/generate_project_path_tree.py",
        "scripts/governance/generate_decision_graph.py",
    )

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel in _PG_WRITE_SCRIPTS:
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        # 跑检测器（写 PG，不产生文件变更）
        gen_result = _run_subprocess(
            [sys.executable, "scripts/governance/d5_architecture/detect_constraint_violations.py"],
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
                detail=f"constraint detection failed: {gen_result.stderr.strip()[:200]}",
            )
        # 检测器写 PG，不产生文件变更，返回 clean
        # GATE-ARCH-DIAGRAM (630) 会在本 reconciler 之后触发，跑生成器展示新检测结果
        return ReconcileResult(
            action="clean",
            detail=f"constraint detection completed: {gen_result.stdout.strip().splitlines()[-1] if gen_result.stdout.strip() else 'done'}",
        )

    return ReconcilerSpec(
        gate_id="GATE-CONSTRAINT-DETECT",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=625,  # 在 GATE-ARCH-DIAGRAM (630) 之前跑，生成器依赖检测结果
    )


# ARCH-055 治本（2026-07-09）：commit_gates 模块清单漂移检测
# 病根：blueprint.md §0.1 模块清单靠手工维护，100% AI 开发模式下漂移率 20.7%（6/29）
# 现有 GATE-AGENTS-MD-REFS 是反向检测（文档引用→代码存在性），本 reconciler 补正向（代码→文档）
# trae_060-reviewed: 该 reconciler 独立存在治本（commit_gates 模块清单漂移正向检测），
# 不合并进已有 reconciler（现有 reconciler 无此检测逻辑，GATE-AGENTS-MD-REFS 是反向检测不覆盖正向）
def make_gate_inventory_sync_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 commit_gates 模块清单漂移检测 post-commit reconciler（ARCH-055 治本）。

    commit src/zephyr/governance/commit_gates/*.py 后，blueprint.md §0.1 模块清单
    可能过时（新增/删除 gate 文件但文档未同步）。本 reconciler 在 post-commit 跑
    check_gate_inventory_drift.py 检测脚本，漂移时 warn（不阻断）。

    warn-only 理由：漂移是文档同步滞后，非代码错误；阻断会导致 AI 无法 commit
    正常的 gate 新增（因 blueprint.md 未同步而阻断 gate 代码本身的 commit，形成
    死循环）。warn 提醒 AI 同步文档即可。

    Args:
        gateway: GitCommitGateway 实例（用 project_root）。

    Returns:
        ReconcilerSpec(gate_id="GATE-MODULE-INVENTORY-SYNC", priority=820)。
    """
    import os
    import sys

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            if rel.startswith("src/zephyr/governance/commit_gates/") and rel.endswith(".py"):
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        check_script = "scripts/governance/generators/check_gate_inventory_drift.py"
        result = _run_subprocess(
            [sys.executable, check_script],
            cwd=str(project_root),
            timeout=30,
        )
        if result.returncode == 0:
            return ReconcileResult(action="clean", detail=result.stdout.strip()[:200])
        if result.returncode == 1:
            return ReconcileResult(
                action="warn",
                detail=f"commit_gates inventory drift detected (ARCH-055): "
                       f"{result.stdout.strip()[:300]}",
            )
        return ReconcileResult(
            action="warn",
            detail=f"check_gate_inventory_drift.py error: {result.stderr.strip()[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-MODULE-INVENTORY-SYNC",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=820,  # 在 GATE-AGENTS-MD-REFS(810) 之后
    )
