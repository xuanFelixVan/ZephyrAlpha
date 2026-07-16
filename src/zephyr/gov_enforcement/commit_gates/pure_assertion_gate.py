# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.pure_assertion_gate
# [DOMAIN] D_GOV_DOC_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); scripts.governance.d3_metadata.check_pure_assertion (subprocess --ci，检测真源)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .md 文件 added 行含纯陈述违规（GOV-DOC-016）时阻断 commit；只检 staged .md added 行（增量检测，现存违规 grandfather）；checker 缺失/超时/exit 2 时 fail-open（不阻断）；exit 1 时硬阻断；scope 过滤在 checker 内（SSoT）
# [MODIFY-GUARD] gate_id="PURE-ASSERTION"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——subprocess 异常降级为 fail-open；检出违规则 fail-closed
# [TESTS] tests/governance/commit_gates/test_pure_assertion_gate.py
# [A_module] module_id=MOD-GOV-006 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""pure_assertion_gate.py — 纯陈述原则阻断门禁（PURE-ASSERTION，GOV-DOC-016 治本）

治本 AD-001 阶段3 删除 _check_pure_assertion 后纯陈述检测无 commit-time 强制：
本 gate 在 GitCommitGateway pre-commit 阶段（in-process）注册，--no-verify 绕不过。
检测真源=check_pure_assertion.py（subprocess 调用 --ci），本 gate 是 thin wrapper。

Usage::

    from zephyr.gov_enforcement.commit_gates.pure_assertion_gate import make_pure_assertion_gate
    registry.register(make_pure_assertion_gate())
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_pure_assertion_gate"]

_PROJECT_ROOT = (
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ))))
)
_CHECKER_SCRIPT = os.path.join(
    _PROJECT_ROOT, "scripts", "governance", "d3_metadata", "check_pure_assertion.py"
)


def _get_staged_md_files(gateway) -> list[str]:
    """获取所有 staged .md 文件（新增+修改）。git 异常时返回空列表（fail-open）。"""
    try:
        r = gateway._run_git(["git", "diff", "--cached", "--name-only"])
        if r.returncode != 0:
            logger.warning("PURE-ASSERTION fail-open: git diff 失败(rc=%d)。", r.returncode)
            return []
        return [
            f.replace("\\", "/") for f in r.stdout.strip().splitlines()
            if f.endswith(".md")
        ]
    except Exception as e:
        logger.warning("PURE-ASSERTION fail-open: git diff 异常(%s: %s)。", type(e).__name__, e)
        return []


def _resolve_worktree_root(gateway) -> str:
    """获取 worktree root 绝对路径，失败回退 gateway.project_root。"""
    try:
        r = gateway._run_git(["git", "rev-parse", "--show-toplevel"])
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return str(getattr(gateway, "project_root", _PROJECT_ROOT))


def _resolve_abs_paths(rel_files: list[str], wt_root: str) -> list[str]:
    """将相对路径解析为绝对路径，过滤不存在的文件。"""
    abs_files = []
    for rel in rel_files:
        if os.path.isabs(rel):
            abs_files.append(rel)
        else:
            abs_files.append(os.path.join(wt_root, rel.replace("/", os.sep)))
    return [f for f in abs_files if os.path.isfile(f)]


def _run_assertion_checker(abs_files: list[str], wt_root: str) -> subprocess.CompletedProcess | None:
    """subprocess 调用 check_pure_assertion.py --ci <files>。"""
    if not os.path.isfile(_CHECKER_SCRIPT):
        logger.warning("PURE-ASSERTION fail-open: check_pure_assertion.py 不存在(%s)。", _CHECKER_SCRIPT)
        return None
    try:
        return subprocess.run(
            [sys.executable, _CHECKER_SCRIPT, "--ci"] + abs_files,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=wt_root, timeout=60,
        )
    except subprocess.TimeoutExpired:
        logger.warning("PURE-ASSERTION fail-open: checker 超时(60s)。")
        return None
    except Exception as e:
        logger.warning("PURE-ASSERTION fail-open: subprocess 异常(%s: %s)。", type(e).__name__, e)
        return None


def _parse_assertion_result(result: subprocess.CompletedProcess) -> tuple[bool, str]:
    """解析 checker exit code：0=pass, 2=fail-open, 1=block。"""
    if result.returncode == 0:
        return True, ""
    if result.returncode == 2:
        logger.warning("PURE-ASSERTION fail-open: checker 异常(exit 2): %s", result.stderr[:200])
        return True, ""
    # exit 1 = 违规
    detail = result.stderr.strip() if result.stderr else "纯陈述违规检出"
    return False, (
        "PURE_ASSERTION_VIOLATION——检出纯陈述原则违规（GOV-DOC-016）。\n"
        "正文只应承载当前真实值，历史差异是 git log 的职责。\n"
        "修复：删除过渡文本（'已废止''之前是X现在改为Y'等），直接写当前值。\n"
        + detail
    )


def make_pure_assertion_gate() -> GateSpec:
    """构造纯陈述原则阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="PURE-ASSERTION", priority=69)。
        priority=69——紧邻 PURE-SHIM(68) 之后、DANGLING-REFERENCE(70) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        staged_md = _get_staged_md_files(gateway)
        if not staged_md:
            return True, ""
        wt_root = _resolve_worktree_root(gateway)
        abs_files = _resolve_abs_paths(staged_md, wt_root)
        if not abs_files:
            return True, ""
        result = _run_assertion_checker(abs_files, wt_root)
        if result is None:
            return True, ""
        return _parse_assertion_result(result)

    return GateSpec(gate_id="PURE-ASSERTION", check=_check, priority=69)
