# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.folder_capacity_hard_limit_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged 新增/修改文件所在目录平铺文件数（排除 __init__.py/隐藏文件/子目录）> _HARD_LIMIT(120) 时阻断 commit；tests/ 豁免；git diff 不可达 fail-open（logger.warning）；文件系统扫描失败 fail-open；检出违规则 fail-closed（passed=False）
# [MODIFY-GUARD] gate_id="FOLDER-CAPACITY-HARD-LIMIT"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；文件系统扫描异常降级为 fail-open；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""folder_capacity_hard_limit_gate.py — 文件夹容量硬上限门禁（FOLDER-CAPACITY-HARD-LIMIT）

补强 GATE-NESTED-FLAT-PREFIX（pre-commit hook，--warn-only）的硬阻断缺口：
GATE-NESTED-FLAT-PREFIX 仅 warn-only 检测 >60 文件目录无命名前缀，但不阻断。
本 gate 在 in-process 层对 >120 文件的目录硬阻断，防止文件夹无限膨胀。

病根（第一性原理）
-----------------
12 维度审计 §四"文件夹容量治理"痛点：手工审反复发现"某目录文件数 150+"
（如 commit_gates/ 目录已达 78 文件）。GATE-NESTED-FLAT-PREFIX 是 pre-commit
hook + --warn-only，被 --no-verify 绕过且不阻断。需要 in-process 硬阻断兜底。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified .py/.yaml/.md 文件
  2. 过滤 tests/ 豁免
  3. 对每个文件所在目录，统计平铺文件数（排除 __init__.py、隐藏文件、子目录内文件）
  4. N > _HARD_LIMIT (120) -> 硬阻断

设计权衡
--------
1. **阈值 120**：对齐 GOV-DOC-018 T_soft=120（GATE-NESTED-FLAT-PREFIX 真源）。
   T_hard=60 由 GATE-NESTED-FLAT-PREFIX warn-only 覆盖（命名前缀强制），
   本 gate 只管 T_soft=120 硬上限——互补不重复。
2. **只统计平铺文件**：不递归子目录（子目录是独立容量单元）。
3. **排除 __init__.py**：包标识文件不计入容量（Python 约定）。
4. **排除隐藏文件**：以 . 开头的文件（.gitkeep 等）不计入。
5. **priority=112**：在 CAPABILITY-LOOKUP-REQUIRED(110) 之后，
   GATE-PRECOMMIT-OFFLINE(111, pre-commit hook 非 in-process) 之后。
6. **fail-open on scan error**：文件系统扫描失败不阻断（避免误伤），
   检出违规则 fail-closed 阻断。

Usage::

    from zephyr.gov_enforcement.commit_gates.folder_capacity_hard_limit_gate import (
        make_folder_capacity_hard_limit_gate,
    )

    registry.register(make_folder_capacity_hard_limit_gate())
"""

from __future__ import annotations

import logging
import os

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    GateSpec,
    is_test_exempt,
)

logger = logging.getLogger(__name__)

__all__ = ["make_folder_capacity_hard_limit_gate"]

# 硬上限阈值——对齐 GOV-DOC-018 T_soft=120（GATE-NESTED-FLAT-PREFIX 真源）
# T_hard=60 由 GATE-NESTED-FLAT-PREFIX warn-only 覆盖（命名前缀强制）
# 本 gate 只管 T_soft=120 硬上限
_HARD_LIMIT = 120

# 触发检测的文件扩展名（代码 + 配置 + 文档）
_TRIGGER_EXTENSIONS: tuple[str, ...] = (".py", ".yaml", ".yml", ".md")


def _collect_staged_trigger_files(gateway) -> list[str]:
    """获取 staged added/modified 的 .py/.yaml/.md 文件列表。

    fail-open：git diff 失败返回空列表（不阻断 commit）。
    """
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
        if diff_result.returncode != 0:
            logger.warning(
                "FOLDER-CAPACITY-HARD-LIMIT gate fail-open: git diff 失败(rc=%d)。",
                diff_result.returncode,
            )
            return []
        staged = [f.replace("\\", "/") for f in diff_result.stdout.strip().splitlines() if f]
    except Exception as e:  # noqa: BLE001 — fail-open 不阻断
        logger.warning(
            "FOLDER-CAPACITY-HARD-LIMIT gate fail-open: git diff 异常(%s: %s)。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return []

    return [f for f in staged if f.endswith(_TRIGGER_EXTENSIONS) and not is_test_exempt(f)]


def _count_flat_files(dir_path: str) -> int:
    """统计目录下平铺文件数（排除 __init__.py、隐藏文件、子目录内文件）。

    Args:
        dir_path: 目录绝对路径。

    Returns:
        平铺文件数；目录不存在返回 0；扫描异常返回 0（fail-open）。
    """
    try:
        entries = os.listdir(dir_path)
    except (OSError, NotADirectoryError):
        return 0

    count = 0
    for entry in entries:
        # 排除隐藏文件（以 . 开头）
        if entry.startswith("."):
            continue
        full = os.path.join(dir_path, entry)
        if not os.path.isfile(full):
            continue  # 跳过子目录
        # 排除 __init__.py（包标识文件）
        if entry == "__init__.py":
            continue
        count += 1
    return count


def _scan_violations(gateway, trigger_files: list[str]) -> list[str]:
    """扫描触发文件所在目录的容量违规。

    返回违规消息列表（每个违规目录一条）。
    """
    project_root = gateway.project_root
    checked_dirs: set[str] = set()
    violations: list[str] = []

    for rel in trigger_files:
        # 提取文件所在目录（相对路径）
        rel_dir = os.path.dirname(rel)
        if not rel_dir:
            continue  # 根目录文件，跳过
        if rel_dir in checked_dirs:
            continue  # 同目录只检查一次
        checked_dirs.add(rel_dir)

        abs_dir = os.path.join(str(project_root), rel_dir)
        count = _count_flat_files(abs_dir)
        if count > _HARD_LIMIT:
            violations.append(
                f"  {rel_dir}/: {count} 文件 > {_HARD_LIMIT} 硬上限（GOV-DOC-018 T_soft=120）。请拆分子目录或迁移文件。"
            )

    return violations


def make_folder_capacity_hard_limit_gate() -> GateSpec:
    """构造文件夹容量硬上限 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="FOLDER-CAPACITY-HARD-LIMIT", priority=112)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        trigger_files = _collect_staged_trigger_files(gateway)
        if not trigger_files:
            return True, ""

        violations = _scan_violations(gateway, trigger_files)

        if violations:
            detail = (
                "FOLDER-CAPACITY-HARD-LIMIT：检测到目录文件数超硬上限，\n"
                "  违反 GOV-DOC-018 T_soft=120 文件夹容量治理原则。\n"
                + "\n".join(violations)
                + "\n-> 拆分子目录（按职责/层级/前缀簇）或迁移文件到合适目录"
            )
            logger.error("FOLDER-CAPACITY-HARD-LIMIT gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="FOLDER-CAPACITY-HARD-LIMIT", check=_check, priority=112)
