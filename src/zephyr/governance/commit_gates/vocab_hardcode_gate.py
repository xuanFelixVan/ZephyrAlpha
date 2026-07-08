# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.vocab_hardcode_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec); scripts.governance.d3_metadata.check_vocab_hardcode (subprocess 调用，检测真源)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬阻断——staged 新增 .py 文件含词表硬编码时阻断 commit（passed=False）；tests/ 豁免（真源：commit_gate_registry.is_test_exempt）；只检测新增文件（diff-filter=A），不检测修改文件（避免基线 13 个存量违规划死工作流，存量违规由第2期批量修复）；检测真源=check_vocab_hardcode.py（subprocess 调用 --files --ci），本 gate 是 thin wrapper 不重复检测逻辑（SSoT）；check_vocab_hardcode.py 缺失/超时/exit 2（脚本异常）时 fail-open（logger.warning 告警检测器失效，不阻断——脚本故障是环境异常非违规）；exit 1（检出违规）时硬阻断；worktree 适配——通过 git rev-parse --show-toplevel 获取 worktree root 作为 subprocess cwd
# [MODIFY-GUARD] gate_id="VOCAB-HARDCODE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——subprocess 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_vocab_hardcode_gate.py
# [A_module] module_id=MOD-GOV-vocab_hardcode_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""vocab_hardcode_gate.py — 新增 .py 文件词表硬编码阻断门禁（VOCAB-HARDCODE，2026-07-03 Phase 1）

治本 --no-verify 绕过 GATE-VOCAB：check_vocab_hardcode.py 是 pre-commit hook，
``git commit --no-verify`` 绕过所有 pre-commit hooks，GATE-VOCAB 沦为君子协定。
本 gate 在 GitCommitGateway pre-commit 阶段（in-process）注册，``--no-verify`` 绕不过。

病根（architecture_debt_registry.md §六 第1期）
-------------------------------------------------
M01 检出 13 个词表硬编码违规（基线）。check_vocab_hardcode.py 能检出但：
  1. 是 pre-commit hook（--no-verify 绕过）
  2. 全量扫描（含 13 个存量违规，不能硬阻断否则卡死工作流）
本 gate 治本：
  1. in-process gate（--no-verify 绕不过）
  2. 只检测 staged 新增文件（diff-filter=A），不触碰存量违规
  3. subprocess 调用 check_vocab_hardcode.py（SSoT，不重复检测逻辑）

设计权衡
--------
1. **只检测新增文件**：存量 13 个违规由第2期批量修复。本 gate 防止新增违规。
   若检测修改文件，存量违规文件被改动时会误阻断（AI 改个注释也被卡）。
2. **subprocess 调用**：check_vocab_hardcode.py 在 scripts/ 不可从 src/ import。
   subprocess + --files flag 保持 SSoT（检测逻辑唯一真源在 check_vocab_hardcode.py）。
3. **fail-open on script error**：脚本故障（exit 2）是环境异常，不阻断 commit。
   检出违规（exit 1）才阻断。对标 create_guard fail-closed 设计但更宽松——
   create_guard 的 YAML 是项目内文件，缺失=异常；本 gate 的 subprocess 可能因
   Python 环境问题失败，fail-open 更安全。
4. **priority=80**：在 ARCH-REFERENCE(75) 之后、CAPABILITY-OVERLAP(200) 之前。

Usage::

    from zephyr.governance.commit_gates.vocab_hardcode_gate import make_vocab_hardcode_gate

    registry.register(make_vocab_hardcode_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_vocab_hardcode_gate"]

# check_vocab_hardcode.py 路径（检测逻辑 SSoT）
_SCRIPT_PATH = (
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ))))
)
# src/zephyr/governance/commit_gates/ -> 上 5 级 = 项目根
_VOCAB_SCRIPT = os.path.join(_SCRIPT_PATH, "scripts", "governance", "d3_metadata", "check_vocab_hardcode.py")


def make_vocab_hardcode_gate() -> GateSpec:
    """构造新增 .py 文件词表硬编码阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="VOCAB-HARDCODE", priority=80)。
        priority=80——在 ARCH-REFERENCE(75) 之后、CAPABILITY-OVERLAP(200) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged 新增 .py 文件
        try:
            diff_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=A"]
            )
            if diff_result.returncode != 0:
                logger.warning(
                    "VOCAB-HARDCODE gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                    diff_result.returncode,
                )
                return True, ""
            staged_new = diff_result.stdout.strip().splitlines()
        except Exception as e:
            logger.warning(
                "VOCAB-HARDCODE gate fail-open: git diff 异常(%s: %s)，检测器失效。",
                type(e).__name__, e, exc_info=True
            )
            return True, ""

        new_py_files = [
            f.replace("\\", "/") for f in staged_new
            if f.endswith(".py") and not is_test_exempt(f)
        ]
        if not new_py_files:
            return True, ""

        # 2. 获取 worktree root（worktree 模式下 cwd 是 worktree，文件在 worktree 文件系统）
        try:
            toplevel_result = gateway._run_git(
                ["git", "rev-parse", "--show-toplevel"]
            )
            if toplevel_result.returncode == 0:
                wt_root = toplevel_result.stdout.strip()
            else:
                wt_root = str(gateway.project_root)
        except Exception:
            wt_root = str(gateway.project_root)

        # 3. 解析为绝对路径（相对 worktree root）
        abs_files = []
        for rel in new_py_files:
            if os.path.isabs(rel):
                abs_files.append(rel)
            else:
                abs_files.append(os.path.join(wt_root, rel.replace("/", os.sep)))

        # 过滤不存在的文件（防御性）
        abs_files = [f for f in abs_files if os.path.isfile(f)]
        if not abs_files:
            return True, ""

        # 4. subprocess 调用 check_vocab_hardcode.py --files --ci
        if not os.path.isfile(_VOCAB_SCRIPT):
            logger.warning(
                "VOCAB-HARDCODE gate fail-open: check_vocab_hardcode.py 不存在(%s)，检测器失效。",
                _VOCAB_SCRIPT,
            )
            return True, ""

        try:
            result = subprocess.run(
                [sys.executable, _VOCAB_SCRIPT, "--files"] + abs_files + ["--ci"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=wt_root,
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            logger.warning(
                "VOCAB-HARDCODE gate fail-open: check_vocab_hardcode.py 超时(60s)，检测器失效。"
            )
            return True, ""
        except Exception as e:
            logger.warning(
                "VOCAB-HARDCODE gate fail-open: subprocess 异常(%s: %s)，检测器失效。",
                type(e).__name__, e, exc_info=True
            )
            return True, ""

        # 5. 解析结果
        # exit 0 = 无违规；exit 1 = 有违规（EXIT_FINDINGS）；exit 2 = 脚本异常（EXIT_ERROR）
        if result.returncode == 0:
            return True, ""  # 无违规
        if result.returncode == 2:
            logger.warning(
                "VOCAB-HARDCODE gate fail-open: check_vocab_hardcode.py 异常(exit 2)：%s",
                result.stderr[:200] if result.stderr else "",
            )
            return True, ""  # 脚本异常，fail-open

        # exit 1 = 检出违规，硬阻断
        # 解析输出提取违规详情
        details: list[str] = []
        for line in (result.stdout + result.stderr).splitlines():
            line = line.strip()
            if line.startswith("WARN:"):
                details.append(line[5:].strip())
        detail_str = "; ".join(details[:5]) if details else "词表硬编码违规（见 check_vocab_hardcode.py 输出）"
        return False, f"新增 .py 文件含词表硬编码（应从 *_vocabulary.yaml 动态加载）: {detail_str}"

    return GateSpec(gate_id="VOCAB-HARDCODE", check=_check, priority=80)
