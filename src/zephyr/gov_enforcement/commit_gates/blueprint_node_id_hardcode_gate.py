# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.blueprint_node_id_hardcode_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.gov_enforcement.commit_gates.doc_ref_broken_gate (_get_worktree_root 共享); scripts.governance.d3_metadata.check_doc_node_id_hardcode (subprocess 调用，检测真源)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__ (via gate_auto_registrar YAML 驱动自动注册)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged blueprint.md 中出现 node_id=数字/edge_id=数字 硬编码时阻断 commit；检测 staged 新增+修改的 blueprint.md（--diff-filter=AM）；subprocess 调用 check_doc_node_id_hardcode.py --ci --files（检测逻辑 SSoT 在 check_doc_node_id_hardcode.py，本 gate 是 thin wrapper 不重复检测逻辑）；脚本缺失/超时/exit 2（脚本异常）时 fail-open（logger.warning 告警检测器失效，不阻断——脚本故障是环境异常非违规）；exit 1（检出违规）时硬阻断
# [MODIFY-GUARD] gate_id="BLUEPRINT-NODE-ID-HARDCODE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——subprocess/IO/git 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_blueprint_node_id_hardcode_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# M03豁免: AI趋同演化(与pure_shim_gate.py相似结构),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
r"""
blueprint_node_id_hardcode_gate.py — blueprint.md node_id/edge_id 硬编码阻断门禁

检测 staged blueprint.md 文件中是否硬编码 node_id/edge_id（文档引用铁律）。
in-process gate，注册到 CommitGateRegistry，在 GitCommitGateway 的 check_all() 阶段执行。
--no-verify 无法绕过 in-process gate（与 pre-commit hook GATE-DOC-NODE-ID 互补）。

病根（第一性原理）
-----------------
GATE-DOC-NODE-ID（pre-commit hook）检测 node_id 硬编码，但 GitCommitGateway 用 --no-verify
绕过 pre-commit hooks。AI 通过 GitCommitGateway 提交含 node_id 硬编码的 blueprint.md
不会被 GATE-DOC-NODE-ID 拦截。本 gate 补齐 GitCommitGateway 路径的覆盖缺口。

文档引用铁律（2026-08-04）：蓝图/文档引用 depgraph 时只写稳定逻辑标识
（module_id/blueprint_id/path），禁止写易变物理ID（node_id/edge_id——
PostgreSQL 自增主键，删除重建即变，成死引用）。

SSoT 治本（2026-08-04，三源→单源）
-----------------------------------
原设计：本 gate 内联 _NODE_ID_HARDCODE_RE 正则，与 check_doc_node_id_hardcode.py
（GATE-DOC-NODE-ID）和 validate_blueprint_provenance.py（GATE-12）形成三源。三源正则
已漂移（check_doc_node_id_hardcode.py 无尾 \b，另两处有尾 \b，行为差异已实证）。

治本：检测逻辑真源 = check_doc_node_id_hardcode.py（专门检测器，已有 --ci --files 接口）。
本 gate 改为 subprocess 调用（对标 pure_shim_gate.py → check_pure_shim.py 模式），
成为 thin wrapper 不重复检测逻辑。validate_blueprint_provenance.py 的 node_id lint
同步移除（冗余于 GATE-DOC-NODE-ID，scope 子集）。

设计权衡
--------
1. **检测 staged 新增+修改的 blueprint.md**：GATE-DOC-NODE-ID 只检测 pre-commit 触发范围，
   本 gate 检测 GitCommitGateway 路径的 staged 文件。--diff-filter=AM 覆盖新增+修改。
2. **subprocess 调用**：check_doc_node_id_hardcode.py 在 scripts/ 不可从 src/ import。
   subprocess + --ci --files 保持 SSoT（检测逻辑唯一真源在 check_doc_node_id_hardcode.py）。
3. **fail-open on script error**：脚本故障（exit 2/超时/缺失）是环境异常，不阻断 commit。
   检出违规（exit 1）才阻断。对标 pure_shim_gate 设计。
4. **priority=57**：在 HELD-OVERLAP(50) 之后、NEW-FILE-DEPGRAPH(58) 之前。

Usage::

    from zephyr.gov_enforcement.commit_gates.blueprint_node_id_hardcode_gate import make_blueprint_node_id_hardcode_gate

    registry.register(make_blueprint_node_id_hardcode_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: blueprint_node_id_hardcode_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① make_blueprint_node_id_hardcode_gate
#   name_en: make_blueprint_node_id_hardcode_gate
#   intro: 构造 blueprint.md node_id/edge_id 硬编码阻断门禁 GateSpec（硬阻断型）。
#   desc: 构造 blueprint.md node_id/edge_id 硬编码阻断门禁 GateSpec（硬阻断型）。 Returns: GateSpec(gate_id="BLUEPR…；源码 L241-L271
#   inputs: 无参数
#   outputs: GateSpec
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from typing import Final

# 共享 _get_worktree_root（避免 FUNCTION-DUP 重复——与 doc_ref_broken_gate.py 共用）
from zephyr.gov_enforcement.commit_gates.doc_ref_broken_gate import _get_worktree_root
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.shared.infra.process_pool import run_subprocess_hidden

logger = logging.getLogger(__name__)

__all__: Final = ["make_blueprint_node_id_hardcode_gate"]

# check_doc_node_id_hardcode.py 路径（检测逻辑 SSoT——node_id/edge_id 硬编码检测唯一真源）
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)
# src/zephyr/gov_enforcement/commit_gates/ -> 上 5 级 = 项目根
_CHECKER_SCRIPT = os.path.join(_PROJECT_ROOT, "scripts", "governance", "d3_metadata", "check_doc_node_id_hardcode.py")


def _get_staged_blueprint_files(gateway) -> list[str] | None:
    """获取 staged 新增+修改的 blueprint.md 文件列表（fail-open：出错返回 None）。

    Args:
        gateway: GitCommitGateway 实例（提供 ``run_git``）。

    Returns:
        blueprint.md 相对路径列表（正斜杠归一化）；git diff 失败/异常时返回 None。
    """
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
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
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None
    # 过滤 blueprint.md 文件（文件名匹配，不限目录）
    return [f.replace("\\", "/") for f in staged if f.endswith("blueprint.md")]


def _resolve_abs_paths(staged_bp: list[str], wt_root: str) -> list[str]:
    """将相对路径解析为绝对路径，过滤不存在的文件。

    Args:
        staged_bp: staged blueprint.md 文件相对路径列表（正斜杠）。
        wt_root: worktree root 绝对路径。

    Returns:
        存在的 blueprint.md 文件绝对路径列表。
    """
    abs_files = []
    for rel in staged_bp:
        if os.path.isabs(rel):
            abs_files.append(rel)
        else:
            abs_files.append(os.path.join(wt_root, rel.replace("/", os.sep)))
    return [f for f in abs_files if os.path.isfile(f)]


def _run_checker(abs_files: list[str], wt_root: str) -> subprocess.CompletedProcess | None:
    """subprocess 调用 check_doc_node_id_hardcode.py --ci --files <files>。

    Returns:
        CompletedProcess 对象；脚本缺失/超时/异常时返回 None（fail-open）。
    """
    if not os.path.isfile(_CHECKER_SCRIPT):
        logger.warning(
            "BLUEPRINT-NODE-ID-HARDCODE gate fail-open: check_doc_node_id_hardcode.py 不存在(%s)，检测器失效。",
            _CHECKER_SCRIPT,
        )
        return None

    try:
        return run_subprocess_hidden(
            [sys.executable, _CHECKER_SCRIPT, "--ci", "--files"] + abs_files,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=wt_root,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        logger.warning(
            "BLUEPRINT-NODE-ID-HARDCODE gate fail-open: check_doc_node_id_hardcode.py 超时(60s)，检测器失效。"
        )
        return None
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "BLUEPRINT-NODE-ID-HARDCODE gate fail-open: subprocess 异常(%s: %s)，检测器失效。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None


def _parse_checker_result(result: subprocess.CompletedProcess) -> tuple[bool, str]:
    """解析 check_doc_node_id_hardcode.py 的 exit code。

    Returns:
        (passed, detail)——exit 0=pass，exit 2=fail-open(pass)，
        exit 1=fail-closed(block，detail 含违规详情)。
    """
    # exit 0 = 无违规；exit 1 = 有违规（EXIT_FINDINGS）；exit 2 = 脚本异常（EXIT_ERROR）
    if result.returncode == 0:
        return True, ""
    if result.returncode == 2:
        logger.warning(
            "BLUEPRINT-NODE-ID-HARDCODE gate fail-open: check_doc_node_id_hardcode.py 异常(exit 2)：%s",
            result.stderr[:200] if result.stderr else "",
        )
        return True, ""

    # exit 1 = 检出违规，硬阻断（check_doc_node_id_hardcode.py 输出到 stdout）
    # rstrip（非 strip）：保留行首两空格，使 "  WARN:" 前缀可被 startswith 匹配
    raw = result.stdout.rstrip() if result.stdout else ""
    if not raw:
        raw = (
            result.stderr.rstrip()
            if result.stderr
            else "node_id/edge_id 硬编码检出（见 check_doc_node_id_hardcode.py 输出）"
        )
    # 提取违规行（WARN/FOUND/ERROR 开头），限 10 行
    detail_lines = [
        line
        for line in raw.splitlines()
        if line.strip() and (line.startswith("  WARN") or line.startswith("  ERROR") or line.startswith("FOUND"))
    ][:10]
    detail_str = "\n".join(detail_lines) if detail_lines else raw[:300]
    return False, (
        "BLUEPRINT_NODE_ID_HARDCODE_VIOLATION——检出 node_id/edge_id 硬编码"
        "（文档引用铁律：禁止易变物理ID，改用 module_id/blueprint_id/path）。\n" + detail_str
    )


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

        # 3. 解析为绝对路径
        abs_files = _resolve_abs_paths(staged_bp_files, wt_root)
        if not abs_files:
            return True, ""

        # 4. subprocess 调用 check_doc_node_id_hardcode.py --ci --files <files>
        result = _run_checker(abs_files, wt_root)
        if result is None:
            return True, ""  # fail-open

        # 5. 解析结果
        return _parse_checker_result(result)

    return GateSpec(gate_id="BLUEPRINT-NODE-ID-HARDCODE", check=_check, priority=57)
