# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.pure_shim_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); scripts.governance.d7_code.check_pure_shim (subprocess 调用，检测真源)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py 文件含纯 re-export shim（star import + 无实质代码）时阻断 commit（passed=False）；检测所有 staged .py（新增+修改），因修改文件也可能被退化为 shim；tests/ 豁免（真源：commit_gate_registry.is_test_exempt）；__init__.py 豁免由 check_pure_shim.is_pure_reexport_shim() 内部处理（包聚合豁免）；检测真源=check_pure_shim.py（subprocess 调用 --ci），本 gate 是 thin wrapper 不重复检测逻辑（SSoT）；check_pure_shim.py 缺失/超时/exit 2（脚本异常）时 fail-open（logger.warning 告警检测器失效，不阻断——脚本故障是环境异常非违规）；exit 1（检出违规）时硬阻断
# [MODIFY-GUARD] gate_id="PURE-SHIM"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——subprocess 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_pure_shim_gate.py
# [A_module] module_id=MOD-GOV-pure_shim_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""pure_shim_gate.py — 纯 re-export shim 阻断门禁（PURE-SHIM，P6 治本 2026-07-09）

治本 --no-verify 绕过 GATE-NO-PURE-SHIM：check_pure_shim.py 是 pre-commit hook
（GATE-SSOT-CODE 三合一之一），``git commit --no-verify`` 绕过所有 pre-commit hooks。
本 gate 在 GitCommitGateway pre-commit 阶段（in-process）注册，``--no-verify`` 绕不过。

病根（AI-15 shared/ 审计裁定 P6）
---------------------------------
check_pure_shim.py 能检出纯 re-export shim 但：
  1. 是 pre-commit hook（--no-verify 绕过）
  2. PURE_SHIM_VIOLATION 状态已定义但无 in-process gate 使用（死代码）
AGENTS.md L361 声称"--no-verify 绕不过 GitCommitGateway Python 层门禁"但实际 pure shim
检测可被 --no-verify 绕过——文档声称与代码现实不符。
本 gate 治本：in-process gate（--no-verify 绕不过），subprocess 调用 check_pure_shim.py（SSoT）。

设计权衡
--------
1. **检测所有 staged .py（新增+修改）**：修改文件也可能被退化为 shim（删除实质代码+加
   star import）。check_pure_shim.is_pure_reexport_shim() 不会误报——含实质代码的文件
   永远不被判定为 shim。
2. **subprocess 调用**：check_pure_shim.py 在 scripts/ 不可从 src/ import。
   subprocess + --ci flag 保持 SSoT（检测逻辑唯一真源在 check_pure_shim.py）。
3. **fail-open on script error**：脚本故障（exit 2）是环境异常，不阻断 commit。
   检出违规（exit 1）才阻断。对标 vocab_hardcode_gate 设计。
4. **priority=68**：紧随 unsafe_dict_spread(66) 之后、dangling_reference(70) 之前
   ——同属"代码结构完整性"类检查。

Usage::

    from zephyr.gov_enforcement.commit_gates.pure_shim_gate import make_pure_shim_gate

    registry.register(make_pure_shim_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_pure_shim_gate"]

# check_pure_shim.py 路径（检测逻辑 SSoT）
_PROJECT_ROOT = (
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ))))
)
# src/zephyr/gov_enforcement/commit_gates/ -> 上 5 级 = 项目根
_SHIM_SCRIPT = os.path.join(
    _PROJECT_ROOT, "scripts", "governance", "d7_code", "check_pure_shim.py"
)


def _get_staged_py_files(gateway) -> list[str]:
    """获取所有 staged .py 文件（新增+修改），排除 tests/。

    Returns:
        .py 文件相对路径列表（正斜杠）；git 异常时返回空列表（fail-open）。
    """
    try:
        diff_result = gateway._run_git(
            ["git", "diff", "--cached", "--name-only"]
        )
        if diff_result.returncode != 0:
            logger.warning(
                "PURE-SHIM gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                diff_result.returncode,
            )
            return []
        staged = diff_result.stdout.strip().splitlines()
    except Exception as e:
        logger.warning(
            "PURE-SHIM gate fail-open: git diff 异常(%s: %s)，检测器失效。",
            type(e).__name__, e, exc_info=True,
        )
        return []

    return [
        f.replace("\\", "/") for f in staged
        if f.endswith(".py") and not is_test_exempt(f)
    ]


def _resolve_worktree_root(gateway) -> str:
    """获取 worktree root 路径。

    Returns:
        worktree root 绝对路径；获取失败时回退到 gateway.project_root。
    """
    try:
        toplevel_result = gateway._run_git(
            ["git", "rev-parse", "--show-toplevel"]
        )
        if toplevel_result.returncode == 0:
            return toplevel_result.stdout.strip()
    except Exception:
        pass
    return str(gateway.project_root)


def _resolve_abs_paths(staged_py: list[str], wt_root: str) -> list[str]:
    """将相对路径解析为绝对路径，过滤不存在的文件。

    Args:
        staged_py: staged .py 文件相对路径列表（正斜杠）。
        wt_root: worktree root 绝对路径。

    Returns:
        存在的 .py 文件绝对路径列表。
    """
    abs_files = []
    for rel in staged_py:
        if os.path.isabs(rel):
            abs_files.append(rel)
        else:
            abs_files.append(os.path.join(wt_root, rel.replace("/", os.sep)))
    return [f for f in abs_files if os.path.isfile(f)]


def _run_shim_checker(abs_files: list[str], wt_root: str) -> subprocess.CompletedProcess | None:
    """subprocess 调用 check_pure_shim.py --ci <files>。

    Returns:
        CompletedProcess 对象；脚本缺失/超时/异常时返回 None（fail-open）。
    """
    if not os.path.isfile(_SHIM_SCRIPT):
        logger.warning(
            "PURE-SHIM gate fail-open: check_pure_shim.py 不存在(%s)，检测器失效。",
            _SHIM_SCRIPT,
        )
        return None

    try:
        return subprocess.run(
            [sys.executable, _SHIM_SCRIPT, "--ci"] + abs_files,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=wt_root,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        logger.warning(
            "PURE-SHIM gate fail-open: check_pure_shim.py 超时(60s)，检测器失效。"
        )
        return None
    except Exception as e:
        logger.warning(
            "PURE-SHIM gate fail-open: subprocess 异常(%s: %s)，检测器失效。",
            type(e).__name__, e, exc_info=True,
        )
        return None


def _parse_shim_result(result: subprocess.CompletedProcess) -> tuple[bool, str]:
    """解析 check_pure_shim.py 的 exit code。

    Returns:
        (passed, detail)——exit 0=pass，exit 2=fail-open(pass)，
        exit 1=fail-closed(block，detail 含违规详情)。
    """
    # exit 0 = 无违规；exit 1 = 有违规（EXIT_FINDINGS）；exit 2 = 脚本异常（EXIT_ERROR）
    if result.returncode == 0:
        return True, ""
    if result.returncode == 2:
        logger.warning(
            "PURE-SHIM gate fail-open: check_pure_shim.py 异常(exit 2)：%s",
            result.stderr[:200] if result.stderr else "",
        )
        return True, ""

    # exit 1 = 检出违规，硬阻断
    detail = result.stderr.strip() if result.stderr else "纯 re-export shim 检出（见 check_pure_shim.py 输出）"
    detail_lines = [
        line for line in detail.splitlines()
        if line.strip() and not line.startswith("-") * 5
    ][:10]
    detail_str = "\n".join(detail_lines) if detail_lines else detail[:300]
    return False, (
        "PURE_SHIM_VIOLATION——检出纯 re-export shim 文件（star import + 无实质代码）。\n"
        "纯 shim 是真源分裂温床，禁止新建。修复：删除 shim 文件，消费者改引 canonical 路径。\n"
        + detail_str
    )


def make_pure_shim_gate() -> GateSpec:
    """构造纯 re-export shim 阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="PURE-SHIM", priority=68)。
        priority=68——紧随 unsafe_dict_spread(66) 之后、dangling_reference(70) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取所有 staged .py 文件（新增+修改）
        staged_py = _get_staged_py_files(gateway)
        if not staged_py:
            return True, ""

        # 2. 获取 worktree root
        wt_root = _resolve_worktree_root(gateway)

        # 3. 解析为绝对路径
        abs_files = _resolve_abs_paths(staged_py, wt_root)
        if not abs_files:
            return True, ""

        # 4. subprocess 调用 check_pure_shim.py --ci <files>
        result = _run_shim_checker(abs_files, wt_root)
        if result is None:
            return True, ""  # fail-open

        # 5. 解析结果
        return _parse_shim_result(result)

    return GateSpec(gate_id="PURE-SHIM", check=_check, priority=68)
