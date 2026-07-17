# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.tests_coverage_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged 文件含 src/zephyr/gov_enforcement/commit_gates/*.py 变更时，扫描整个 gate 目录，检测每个 .py 文件 [TESTS] 头部声明的测试文件路径是否实际存在；声明但文件不存在 → 阻断 commit（passed=False）；[TESTS] — / 空 / none 豁免；_*.py 前缀文件豁免（helpers）；文件系统异常 fail-open（logger.warning）；守卫者的守卫者（quis custodiet ipsos custodes）——确保每个 gate 自身有测试
# [MODIFY-GUARD] gate_id="META-TESTS-COVERAGE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——文件系统异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_tests_coverage_gate.py
# [A_module] module_id=MOD-GOV-tests_coverage_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""tests_coverage_gate.py — Gate 测试覆盖率校验 meta-gate（META-TESTS-COVERAGE，#ARCH-057）

检测 ``src/zephyr/gov_enforcement/commit_gates/*.py`` 的 ``[TESTS]`` 头部声明的测试文件
是否实际存在——"声明但不兑现"的系统性缺口治本。

病根（第一性原理）
-----------------
36 个 gate 源文件头部都声明了 ``# [TESTS] tests/.../test_xxx.py``，但 15 个 gate
的测试文件不存在（声明但不兑现）。无 meta-gate 校验，头部规范成摆设。

100% AI 开发模式下无人类 PR review，AI 创建 gate 后立即提交，"守卫者无人守卫"
（quis custodiet ipsos custodes）。本次 post_commit_guard.sh 误回滚 bug 正是
"gate 无测试"的直接后果——若有测试，allow_overlap 逃生通道的边界场景会被覆盖。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册 meta-gate：
  1. trigger 条件：staged 文件含 ``src/zephyr/gov_enforcement/commit_gates/*.py`` 变更
  2. 扫描整个 gate 目录所有 ``*.py`` 文件（跳过 ``_`` 前缀 helpers）
  3. 正则提取头部 ``# [TESTS] <path>`` 声明
  4. 豁免：``—`` / 空 / ``none``（显式声明无测试）
  5. 检测 ``<path>`` 是否存在（相对 project_root）
  6. 不存在 -> 硬阻断

设计权衡
--------
1. **trigger 限 gate 目录变更**：只在 commit_gates/*.py 变更时触发，避免每次
   commit 都扫描 gate 目录（性能）。
2. **扫描整个目录而非仅 staged 文件**：确保存量 gate 的测试覆盖也持续校验。
3. **跳过 _ 前缀文件**：``_diff_helpers.py`` 等 helper 不是 gate，无 [TESTS]。
4. **priority=99**：在所有业务 gate（最高 94）之后执行——meta-gate 最后运行。
5. **fail-open on FS error**：文件系统异常不阻断（环境问题非违规）。

Usage::

    from zephyr.gov_enforcement.commit_gates.tests_coverage_gate import make_tests_coverage_gate

    registry.register(make_tests_coverage_gate())
"""

from __future__ import annotations

import logging
import os
import re

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_tests_coverage_gate"]

_GATE_DIR = "src/zephyr/gov_enforcement/commit_gates"
_TRIGGER_PREFIX = "src/zephyr/gov_enforcement/commit_gates/"

# 注意：用 [ \t] 而非 \s，避免 \s 匹配换行符导致跨行提取下一行内容
_TESTS_HEADER_RE = re.compile(r"^#[ \t]*\[TESTS\][ \t]*(.*?)[ \t]*$", re.MULTILINE)

_EXEMPT_VALUES = frozenset({"", "—", "-", "none", "None", "无", "N/A", "n/a"})


def make_tests_coverage_gate() -> GateSpec:
    """构造 Gate 测试覆盖率校验 meta-gate（硬阻断型）。

    Returns:
        GateSpec(gate_id="META-TESTS-COVERAGE", priority=99)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        has_gate_change = any(
            f.replace("\\", "/").startswith(_TRIGGER_PREFIX) and f.endswith(".py")
            for f in files
        )
        if not has_gate_change:
            return True, ""

        project_root = str(gateway.project_root)
        gate_dir_abs = os.path.join(project_root, _GATE_DIR.replace("/", os.sep))

        if not os.path.isdir(gate_dir_abs):
            return True, ""

        violations: list[str] = []
        try:
            entries = sorted(os.listdir(gate_dir_abs))
        except OSError as e:
            logger.warning(
                "META-TESTS-COVERAGE gate fail-open: listdir 失败(%s: %s)。",
                type(e).__name__, e,
            )
            return True, ""

        for entry in entries:
            if not entry.endswith(".py") or entry.startswith("_"):
                continue
            gate_file = os.path.join(gate_dir_abs, entry)
            if not os.path.isfile(gate_file):
                continue

            try:
                with open(gate_file, "r", encoding="utf-8", errors="replace") as f:
                    head_lines = [f.readline() for _ in range(30)]
                head = "".join(head_lines)
            except OSError as e:
                logger.warning(
                    "META-TESTS-COVERAGE gate skip %s: 读取失败(%s: %s)。",
                    entry, type(e).__name__, e,
                )
                continue

            match = _TESTS_HEADER_RE.search(head)
            if not match:
                continue
            tests_path = match.group(1).strip()

            if tests_path in _EXEMPT_VALUES:
                continue

            tests_abs = os.path.join(project_root, tests_path.replace("/", os.sep))
            if not os.path.isfile(tests_abs):
                violations.append(
                    f"  {entry}: [TESTS] 声明 {tests_path} 但文件不存在"
                )

        if violations:
            detail = (
                "META-TESTS-COVERAGE：检测到 gate 测试文件缺失（声明但不兑现）。\n"
                "  gate 自身无测试 = 防线可能有未发现 bug"
                "（quis custodiet ipsos custodes——谁来监督监督者）。\n"
                + "\n".join(violations)
                + "\n-> 请为每个 gate 创建对应的 test_*.py 文件，或将 [TESTS] 改为 — 显式声明无测试"
            )
            logger.error("META-TESTS-COVERAGE gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="META-TESTS-COVERAGE", check=_check, priority=99)
