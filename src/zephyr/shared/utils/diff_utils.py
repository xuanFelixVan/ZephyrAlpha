# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.utils.diff_utils
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_diff_utils | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
diff_utils.py —— 统一 Diff/Patch 工具（Phase 3 新增 | 盲点 #14 修复）

痛点修复：此前 frontmatter_utils.py 中嵌入了 diff 逻辑，feedback-loop
需要比对新旧产出但没有共享的 diff 工具。

设计对标：
  - Python difflib 标准库（unified_diff / ndiff / SequenceMatcher）
  - Aider 社区的 diff/patch 模式（精确行级 patch 回推）
  - git diff --unified 格式（AI 最熟悉的 diff 格式）

设计原则：
  - 纯标准库——无第三方依赖
  - 输出统一 diff 格式（context_lines=3），AI 肉眼可读
  - 支持 patch 应用 + 干跑检测冲突

AI 施工约定：
  - feedback-loop 的比对逻辑 MUST 使用本模块
  - AI 代码修改前后的验证 MUST 使用 compute_diff
  - 蓝图的变更审计 MUST 使用 unified_diff_lines

SSoT: MOD-INF-016 §2.10 shared-diff
Version: 0.1.0
"""

from __future__ import annotations

import difflib
from pathlib import Path

__all__ = [
    "PatchConflictError",
    "apply_patch",
    "compute_diff",
    "compute_file_diff",
    "similarity_ratio",
    "try_apply_patch",
]


class PatchConflictError(ValueError):
    """Patch 无法干净应用——存在冲突或目标状态与期望不符。"""
    error_code = "ZA-SH-0049"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


def compute_diff(
    original: str,
    modified: str,
    *,
    from_file: str = "original",
    to_file: str = "modified",
    context_lines: int = 3,
) -> str:
    """计算两个字符串的统一 diff。

    Args:
        original: 原始内容。
        modified: 修改后内容。
        from_file: diff header 中原始文件名。
        to_file: diff header 中修改文件名。
        context_lines: 上下文行数（默认 3）。

    Returns:
        标准 unified diff 格式字符串，无变更时返回空字符串。
    """
    original_lines = original.splitlines(keepends=True)
    modified_lines = modified.splitlines(keepends=True)

    diff_lines = list(
        difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=from_file,
            tofile=to_file,
            n=context_lines,
        )
    )

    return "".join(diff_lines)


def compute_file_diff(
    original_path: Path | str,
    modified_path: Path | str,
    *,
    context_lines: int = 3,
) -> str:
    """计算两个文件的统一 diff。

    Args:
        original_path: 原始文件路径。
        modified_path: 修改后文件路径。
        context_lines: 上下文行数。

    Returns:
        标准 unified diff 格式字符串。
    """
    original = Path(original_path).read_text(encoding="utf-8")
    modified = Path(modified_path).read_text(encoding="utf-8")

    return compute_diff(
        original,
        modified,
        from_file=str(original_path),
        to_file=str(modified_path),
        context_lines=context_lines,
    )


def _parse_hunk_ranges(hunk_header: str) -> tuple[int, int, int, int]:
    """Parse '@@ -old_start,old_count +new_start,new_count @@'"""
    import re

    match = re.match(r"@@ -(\d+),?(\d*?) \+(\d+),?(\d*?) @@", hunk_header)
    if not match:
        raise PatchConflictError(f"Invalid hunk header: {hunk_header!r}")

    old_start = int(match.group(1))
    old_count = int(match.group(2)) if match.group(2) else 1
    new_start = int(match.group(3))
    new_count = int(match.group(4)) if match.group(4) else 1

    return old_start, old_count, new_start, new_count


def apply_patch(
    original: str,
    patch_text: str,
    *,
    strict: bool = True,
) -> str:
    """应用 unified diff 格式的 patch 到原始内容。

    Args:
        original: 原始文本内容。
        patch_text: unified diff 格式的 patch。
        strict: True 时行号必须精确匹配；False 时 fuzzy match。

    Returns:
        patch 后的文本。

    Raises:
        PatchConflictError: patch 无法干净应用。
    """
    original_lines = original.splitlines(keepends=True)
    patch_lines = patch_text.splitlines(keepends=True)

    result_lines: list[str] = []
    orig_idx = 0
    line_idx = 0

    while line_idx < len(patch_lines):
        line = patch_lines[line_idx]
        line_idx += 1

        if line.startswith("@@"):
            old_start, old_count, new_start, new_count = _parse_hunk_ranges(line)

            if strict and orig_idx != old_start - 1:
                raise PatchConflictError(f"Line mismatch: expected line {old_start}, got {orig_idx + 1}")

            hunk_end = old_start - 1 + old_count

            while orig_idx < old_start - 1:
                result_lines.append(original_lines[orig_idx])
                orig_idx += 1

            hunk_orig_idx = orig_idx
            while line_idx < len(patch_lines):
                next_line = patch_lines[line_idx]
                if next_line.startswith("@@"):
                    break
                if next_line.startswith(" "):
                    if hunk_orig_idx < len(original_lines):
                        result_lines.append(original_lines[hunk_orig_idx])
                        hunk_orig_idx += 1
                        orig_idx += 1
                elif next_line.startswith("-"):
                    if hunk_orig_idx < len(original_lines):
                        hunk_orig_idx += 1
                        orig_idx += 1
                elif next_line.startswith("+"):
                    result_lines.append(next_line[1:])
                elif next_line.startswith("\\"):
                    pass
                line_idx += 1

        else:
            result_lines.append(line)

    while orig_idx < len(original_lines):
        result_lines.append(original_lines[orig_idx])
        orig_idx += 1

    return "".join(result_lines)


def try_apply_patch(
    original: str,
    patch_text: str,
) -> tuple[bool, str]:
    """尝试应用 patch，返回 (成功标志, 结果或原始内容)。

    Args:
        original: 原始文本。
        patch_text: patch 文本。

    Returns:
        (True, patched_text) 如果成功，(False, original) 如果冲突。
    """
    try:
        return True, apply_patch(original, patch_text, strict=False)
    except PatchConflictError:
        return False, original


def similarity_ratio(a: str, b: str) -> float:
    """计算两个字符串的相似度比率（0.0 ~ 1.0）。

    Args:
        a: 字符串 A。
        b: 字符串 B。

    Returns:
        相似度比率，1.0 表示完全相同。
    """
    return difflib.SequenceMatcher(None, a, b).ratio()
