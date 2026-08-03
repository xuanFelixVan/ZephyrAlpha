# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.blueprint_node_id_hardcode_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.gov_enforcement.commit_gates.doc_ref_broken_gate (_get_worktree_root 共享)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__ (via gate_auto_registrar YAML 驱动自动注册)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged blueprint.md 中出现 node_id=数字/edge_id=数字 硬编码时阻断 commit；检测 staged 新增+修改的 blueprint.md（--diff-filter=AM）；in-process 正则检测；文件读取失败 fail-open（logger.warning）
# [MODIFY-GUARD] gate_id="BLUEPRINT-NODE-ID-HARDCODE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；正则 _NODE_ID_HARDCODE_RE 与 validate_blueprint_provenance.py 同步（双源标注）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——IO/git 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_blueprint_node_id_hardcode_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# M03豁免: AI趋同演化(与doc_ref_broken_gate.py相似结构),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
"""blueprint_node_id_hardcode_gate.py — blueprint.md node_id/edge_id 硬编码阻断门禁

检测 staged blueprint.md 文件中是否硬编码 node_id/edge_id（文档引用铁律）。
in-process gate，注册到 CommitGateRegistry，在 GitCommitGateway 的 check_all() 阶段执行。
--no-verify 无法绕过 in-process gate（与 pre-commit hook GATE-12 互补）。

病根（第一性原理）
-----------------
GATE-12（pre-commit hook）检测 node_id 硬编码，但 GitCommitGateway 用 --no-verify
绕过 pre-commit hooks。AI 通过 GitCommitGateway 提交含 node_id 硬编码的 blueprint.md
不会被 GATE-12 拦截。本 gate 补齐 GitCommitGateway 路径的覆盖缺口。

文档引用铁律（2026-08-04）：蓝图/文档引用 depgraph 时只写稳定逻辑标识
（module_id/blueprint_id/path），禁止写易变物理ID（node_id/edge_id——
PostgreSQL 自增主键，删除重建即变，成死引用）。

设计权衡
--------
1. **检测 staged 新增+修改的 blueprint.md**：GATE-12 只检测 pre-commit 触发范围，
   本 gate 检测 GitCommitGateway 路径的 staged 文件。--diff-filter=AM 覆盖新增+修改。
2. **in-process 正则**：无 subprocess 调用检查器脚本，纯 re.findall，自包含。
3. **fail-open on IO error**：文件读取/git diff 失败不阻断 commit。
4. **正则双源同步**：_NODE_ID_HARDCODE_RE 与 validate_blueprint_provenance.py
   （GATE-12 pre-commit hook）保持一致，正则变更需同步两处。
5. **priority=57**：在 HELD-OVERLAP(50) 之后、NEW-FILE-DEPGRAPH(58) 之前。

Usage::

    from zephyr.gov_enforcement.commit_gates.blueprint_node_id_hardcode_gate import make_blueprint_node_id_hardcode_gate

    registry.register(make_blueprint_node_id_hardcode_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging
import os
import re
from typing import Final

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
# 共享 _get_worktree_root（避免 FUNCTION-DUP 重复——与 doc_ref_broken_gate.py 共用）
from zephyr.gov_enforcement.commit_gates.doc_ref_broken_gate import _get_worktree_root

logger = logging.getLogger(__name__)

__all__: Final = ["make_blueprint_node_id_hardcode_gate"]

# 文档引用铁律（2026-08-04）：禁止蓝图/文档硬编码 node_id/edge_id
# ⚠️ 双源同步：此正则与 scripts/governance/d3_metadata/validate_blueprint_provenance.py
#    的 _NODE_ID_HARDCODE_RE 保持一致。正则变更需同步两处。
_NODE_ID_HARDCODE_RE = re.compile(r"\b(node_id|edge_id)\s*=\s*(\d+)\b")


def _get_staged_blueprint_files(gateway) -> list[str] | None:
    """获取 staged 新增+修改的 blueprint.md 文件列表（fail-open：出错返回 None）。

    Args:
        gateway: GitCommitGateway 实例（提供 ``run_git``）。

    Returns:
        blueprint.md 相对路径列表（正斜杠归一化）；git diff 失败/异常时返回 None。
    """
    try:
        diff_result = gateway.run_git(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"]
        )
        if diff_result.returncode != 0:
            logger.warning(
                "BLUEPRINT-NODE-ID-HARDCODE gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                diff_result.returncode,
            )
            return None
        staged = diff_result.stdout.strip().splitlines()
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "BLUEPRINT-NODE-ID-HARDCODE gate fail-open: git diff 异常(%s: %s)，检测器失效。",
            type(e).__name__, e, exc_info=True
        )
        return None
    # 过滤 blueprint.md 文件（文件名匹配，不限目录）
    return [f.replace("\\", "/") for f in staged if f.endswith("blueprint.md")]


def _detect_violation(abs_path: str, wt_root: str) -> str | None:
    """检测单个 blueprint.md 文件的 node_id/edge_id 硬编码。

    Args:
        abs_path: blueprint.md 绝对路径。
        wt_root: worktree 根目录（用于生成相对路径描述）。

    Returns:
        违规描述字符串；读取失败/无违规返回 None。
    """
    try:
        with open(abs_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError as e:
        logger.warning(
            "BLUEPRINT-NODE-ID-HARDCODE gate skip file %s: 读取失败(%s: %s)。",
            abs_path, type(e).__name__, e,
        )
        return None

    matches = _NODE_ID_HARDCODE_RE.findall(content)
    if not matches:
        return None
    rel_name = os.path.relpath(abs_path, wt_root).replace("\\", "/")
    # 去重，保留前 5 个
    seen: set[str] = set()
    unique: list[str] = []
    for kind, num in matches:
        key = f"{kind}={num}"
        if key not in seen:
            seen.add(key)
            unique.append(key)
    refs_str = "; ".join(unique[:5])
    return f"文档硬编码物理ID {rel_name}: {refs_str}（文档引用铁律：改用 module_id/blueprint_id/path）"


def make_blueprint_node_id_hardcode_gate() -> GateSpec:
    """构造 blueprint.md node_id/edge_id 硬编码阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="BLUEPRINT-NODE-ID-HARDCODE", priority=57)。
        priority=57——在 HELD-OVERLAP(50) 之后、NEW-FILE-DEPGRAPH(58) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged blueprint.md 文件（None 表示 fail-open 检测器失效）
        staged_bp_files = _get_staged_blueprint_files(gateway)
        if not staged_bp_files:
            return True, ""

        # 2. 获取 worktree root
        wt_root = _get_worktree_root(gateway)

        # 3. 解析为绝对路径并检测
        all_violations: list[str] = []
        for rel_path in staged_bp_files:
            if os.path.isabs(rel_path):
                abs_path = rel_path
            else:
                abs_path = os.path.join(wt_root, rel_path.replace("/", os.sep))
            if not os.path.isfile(abs_path):
                continue
            violation = _detect_violation(abs_path, wt_root)
            if violation:
                all_violations.append(violation)

        if all_violations:
            return False, "; ".join(all_violations[:5])
        return True, ""

    return GateSpec(gate_id="BLUEPRINT-NODE-ID-HARDCODE", check=_check, priority=57)
