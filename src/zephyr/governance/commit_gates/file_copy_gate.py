# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.file_copy_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec); scripts.governance.d5_architecture.checkers.check_code_duplication (subprocess 调用，检测真源)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬阻断——staged 新增 .py 文件与已有同名文件 AST 归一化相似度>70%时阻断 commit（passed=False）；tests/ 豁免（真源：commit_gate_registry.is_test_exempt）；只检测新增文件（diff-filter=A），不检测修改文件（避免基线 159 对存量重复卡死工作流，存量违规由第2期批量修复）；检测真源=check_code_duplication.py（subprocess 调用 --files --ast --threshold 0.7），本 gate 是 thin wrapper 不重复检测逻辑（SSoT）；check_code_duplication.py 缺失/超时/exit 2（脚本异常）时 fail-open（logger.warning 告警检测器失效，不阻断）；exit 1（检出违规）时硬阻断；路径解析对标 gateway.project_root（主仓库根，非 worktree root）——因 check_code_duplication.py 扫描主仓库已有文件做比对，新文件在主仓库工作树存在（AI 用 Write/Edit 写项目根，session_worktree_commit 复制到 worktree），主仓库路径使 script 的 new_resolved 排除集正确排除新文件自身
# [MODIFY-GUARD] gate_id="FILE-COPY"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——subprocess 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_file_copy_gate.py
# [A_module] module_id=MOD-GOV-file_copy_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""file_copy_gate.py — 新增 .py 文件复制检测阻断门禁（FILE-COPY，2026-07-03 Phase 1 sub-task 3）

治本文件复制检测无 commit-time 强制：check_code_duplication.py 是手动脚本，
``git commit --no-verify`` 绕过所有 pre-commit hooks，文件复制检测沦为君子协定。
本 gate 在 GitCommitGateway pre-commit 阶段（in-process）注册，``--no-verify`` 绕不过。

病根（architecture_debt_registry.md §六 第1期）
-------------------------------------------------
M05 检出 159 对文件复制（基线）。check_code_duplication.py 能检出但：
  1. 是手动脚本（无自动触发，--no-verify 绕过）
  2. 全量扫描（含 159 对存量违规，不能硬阻断否则卡死工作流）
本 gate 治本：
  1. in-process gate（--no-verify 绕不过）
  2. 只检测 staged 新增文件（diff-filter=A），不触碰存量违规
  3. subprocess 调用 check_code_duplication.py --files --ast（SSoT，不重复检测逻辑）
  4. AST 归一化比较（parse->unparse->SequenceMatcher），剥离注释/格式差异

设计权衡
--------
1. **只检测新增文件**：存量 159 对由第2期批量修复。本 gate 防止新增违规。
2. **同名文件比对**：文件复制最常见模式=AI 复制 foo.py 从包 A 到包 B（同 basename）。
   跨 basename 比对成本高且误报多，同名比对覆盖主要场景。
3. **AST 归一化**：parse->unparse 自动剥离注释/空白/格式差异，聚焦代码结构。
   比 SequenceMatcher 原始行比较更鲁棒（改注释/格式不误报）。
4. **threshold=0.7**：对标 architecture_debt_registry.md §六"AST共享行百分比>70%即阻断"。
5. **fail-open on script error**：脚本故障（exit 2）是环境异常，不阻断 commit。
6. **priority=85**：在 VOCAB-HARDCODE(80) 之后、CAPABILITY-OVERLAP(200) 之前。
7. **路径解析用 gateway.project_root**：check_code_duplication.py 扫描主仓库已有文件，
   新文件需在主仓库路径可达（AI 写项目根->session_worktree_commit 复制到 worktree）。
   主仓库路径使 script 的 new_resolved 排除集正确排除新文件自身（避免自比自=100%）。

Usage::

    from zephyr.governance.commit_gates.file_copy_gate import make_file_copy_gate

    registry.register(make_file_copy_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_file_copy_gate"]

# check_code_duplication.py 路径（检测逻辑 SSoT）
_SCRIPT_PATH = (
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ))))
)
# src/zephyr/governance/commit_gates/ -> 上 5 级 = 项目根
_DUP_SCRIPT = os.path.join(
    _SCRIPT_PATH, "scripts", "governance", "d5_architecture", "checkers", "check_code_duplication.py"
)

# AST 共享行百分比阈值（architecture_debt_registry.md §六：>70%即阻断）
_THRESHOLD = 0.7


def make_file_copy_gate() -> GateSpec:
    """构造新增 .py 文件复制检测阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="FILE-COPY", priority=85)。
        priority=85——在 VOCAB-HARDCODE(80) 之后、CAPABILITY-OVERLAP(200) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged 新增 .py 文件
        try:
            diff_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=A"]
            )
            if diff_result.returncode != 0:
                logger.warning(
                    "FILE-COPY gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                    diff_result.returncode,
                )
                return True, ""
            staged_new = diff_result.stdout.strip().splitlines()
        except Exception as e:
            logger.warning(
                "FILE-COPY gate fail-open: git diff 异常(%s: %s)，检测器失效。",
                type(e).__name__, e, exc_info=True
            )
            return True, ""

        new_py_files = [
            f.replace("\\", "/") for f in staged_new
            if f.endswith(".py") and not is_test_exempt(f)
        ]
        if not new_py_files:
            return True, ""

        # 2. 解析为绝对路径（对标 gateway.project_root 主仓库根，非 worktree root）
        #    原因：check_code_duplication.py 扫描主仓库已有文件做比对，
        #    新文件在主仓库工作树存在（AI 用 Write/Edit 写项目根）。
        #    主仓库路径使 script 的 new_resolved 排除集正确排除新文件自身。
        repo_root = str(gateway.project_root)
        abs_files = []
        for rel in new_py_files:
            if os.path.isabs(rel):
                abs_files.append(rel)
            else:
                abs_files.append(os.path.join(repo_root, rel.replace("/", os.sep)))

        # 过滤不存在的文件（防御性）
        abs_files = [f for f in abs_files if os.path.isfile(f)]
        if not abs_files:
            return True, ""

        # 3. subprocess 调用 check_code_duplication.py --files --ast --threshold 0.7
        if not os.path.isfile(_DUP_SCRIPT):
            logger.warning(
                "FILE-COPY gate fail-open: check_code_duplication.py 不存在(%s)，检测器失效。",
                _DUP_SCRIPT,
            )
            return True, ""

        try:
            result = subprocess.run(
                [sys.executable, _DUP_SCRIPT,
                 "--files"] + abs_files +
                ["--ast", "--threshold", str(_THRESHOLD)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=repo_root,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            logger.warning(
                "FILE-COPY gate fail-open: check_code_duplication.py 超时(120s)，检测器失效。"
            )
            return True, ""
        except Exception as e:
            logger.warning(
                "FILE-COPY gate fail-open: subprocess 异常(%s: %s)，检测器失效。",
                type(e).__name__, e, exc_info=True
            )
            return True, ""

        # 4. 解析结果
        # exit 0 = 无违规；exit 1 = 有违规（EXIT_FINDINGS）；exit 2 = 脚本异常（EXIT_ERROR）
        if result.returncode == 0:
            return True, ""  # 无违规
        if result.returncode == 2:
            logger.warning(
                "FILE-COPY gate fail-open: check_code_duplication.py 异常(exit 2)：%s",
                result.stderr[:200] if result.stderr else "",
            )
            return True, ""  # 脚本异常，fail-open

        # exit 1 = 检出违规，硬阻断
        # 解析输出提取违规详情（相似度行）
        details: list[str] = []
        for line in (result.stdout + result.stderr).splitlines():
            line = line.strip()
            if line and not line.startswith("FILE COPY") and not line.startswith("新文件") and not line.startswith("---"):
                details.append(line)
        detail_str = "; ".join(details[:5]) if details else "文件复制检测违规（见 check_code_duplication.py 输出）"
        return False, f"新增 .py 文件与已有同名文件 AST 相似度>{_THRESHOLD:.0%}: {detail_str}"

    return GateSpec(gate_id="FILE-COPY", check=_check, priority=85)
