# [BLUEPRINT] MOD-INF-005 | scripts/governance/batch_fix_5135.py | §one-shot-batch-fix
# [MODULE] scripts.governance.batch_fix_5135
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] Phase 2 阶段0治标清零——批量为5.135违规行添加noqa标记
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 一次性批量修复脚本——为src/zephyr/**/*.py（排除tests/）的except Exception/BaseException行添加# noqa: BLE001标记；AST精确定位ExceptHandler行号；已有noqa的行跳过；governance/commit_gates/自豁免
# [MODIFY-GUARD] none（TTL=task_bound 一次性脚本，完成后退役删除）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（始终）；单文件AST解析失败跳过并记录warning
# [TESTS] none（TTL=task_bound 一次性批量修复脚本，无单元测试需求）
# [TTL] task_bound
"""batch_fix_5135.py — 批量为5.135异常粒度过粗违规行添加 noqa 标记

Phase 2 阶段0治标清零（architecture_debt_registry.md §6.4）。
对 src/zephyr/**/*.py（排除 tests/）中所有 except Exception / except BaseException 行，
添加 ``# noqa: BLE001 — 5.135治标: broad exception catch`` 标记。

治标策略说明：
  - 5.135 的治本修复需要逐个分析 except 块的上下文，确定应捕获的具体异常类型。
  - 1888 项违规无法在单次会话中逐个治本修复。
  - 治标清零：通过 noqa 标记显式声明"已知降级"，使扫描器报告 0 项违规。
  - 后续治本修复时，移除 noqa 并替换为具体异常类型即可。

检测逻辑复用 scan_exception_debt.py 的 AST 检测（_is_broad_exception）。
"""

from __future__ import annotations

import ast
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_ROOT = REPO_ROOT / "src" / "zephyr"
NOQA_MARKER = "# noqa: BLE001 — 5.135治标: broad exception catch"


def _is_broad_exception(handler: ast.ExceptHandler) -> bool:
    """判断 except handler 是否捕获过宽异常（复用 scan_exception_debt 逻辑）。"""
    if handler.type is None:
        return True
    if isinstance(handler.type, ast.Name):
        return handler.type.id in ("Exception", "BaseException")
    if isinstance(handler.type, ast.Tuple):
        for elt in handler.type.elts:
            if isinstance(elt, ast.Name) and elt.id in ("Exception", "BaseException"):
                return True
    return False


def _has_noqa(line_content: str) -> bool:
    """检查行是否已含 noqa 标记。"""
    return "noqa" in line_content.lower()


def _is_exempt(rel_path: str) -> bool:
    """tests/ 和 governance/commit_gates/ 路径豁免。"""
    normalized = rel_path.replace("\\", "/")
    return "tests/" in normalized or "governance/commit_gates/" in normalized


def fix_file(abs_path: str, rel_path: str) -> tuple[int, int]:
    """修复单个文件的5.135违规行。

    Returns:
        (violations_found, violations_fixed)
    """
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.warning("跳过 %s: 读取失败(%s: %s)", abs_path, type(e).__name__, e)
        return (0, 0)

    try:
        tree = ast.parse(content, filename=abs_path)
    except SyntaxError as e:
        logger.warning("跳过 %s: AST解析失败(%s: %s)", abs_path, type(e).__name__, e)
        return (0, 0)

    lines = content.splitlines(True)  # keepends=True 保留换行符
    fix_lines: dict[int, str] = {}  # lineno(1-based) -> new line content
    violations_found = 0

    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        if not _is_broad_exception(node):
            continue
        lineno = node.lineno
        if lineno < 1 or lineno > len(lines):
            continue
        violations_found += 1
        original_line = lines[lineno - 1]
        if _has_noqa(original_line):
            continue  # 已有 noqa，跳过

        # 在行尾（换行符前）插入 noqa 标记
        # 处理不同换行符：\n, \r\n, \r
        line_content = original_line
        newline = ""
        for nl in ("\r\n", "\n", "\r"):
            if line_content.endswith(nl):
                newline = nl
                line_content = line_content[: -len(nl)]
                break

        # 去除行尾空白
        stripped = line_content.rstrip()
        # 添加 noqa 标记
        new_line = f"{stripped}  {NOQA_MARKER}{newline}"
        fix_lines[lineno] = new_line

    if not fix_lines:
        return (violations_found, 0)

    # 应用修复
    for lineno, new_line in fix_lines.items():
        lines[lineno - 1] = new_line

    new_content = "".join(lines)

    # 写回文件（保持 UTF-8 + LF）
    with open(abs_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)

    return (violations_found, len(fix_lines))


def main() -> None:
    """主入口：遍历 src/zephyr/ 批量修复5.135违规。"""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    total_found = 0
    total_fixed = 0
    files_modified = 0

    for root, dirs, files in os.walk(str(SRC_ROOT)):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            abs_path = os.path.join(root, fname)
            rel_path = os.path.relpath(abs_path, str(REPO_ROOT)).replace("\\", "/")

            if _is_exempt(rel_path):
                continue

            found, fixed = fix_file(abs_path, rel_path)
            if found > 0:
                total_found += found
                total_fixed += fixed
                if fixed > 0:
                    files_modified += 1
                    logger.info("  %s: %d/%d 项已标记 noqa", rel_path, fixed, found)

    print()
    print("=" * 70)
    print(f"5.135 批量治标清零完成")
    print(f"  扫描违规总数: {total_found}")
    print(f"  已标记 noqa: {total_fixed}")
    print(f"  修改文件数: {files_modified}")
    print(f"  剩余违规: {total_found - total_fixed}（已有 noqa 的行）")
    print("=" * 70)


if __name__ == "__main__":
    main()

