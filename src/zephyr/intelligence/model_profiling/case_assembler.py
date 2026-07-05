# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.case_assembler
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES]
# [CONSUMERS] zephyr.intelligence.model_profiling.exam_test_cases
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 仅读白名单目录；埋针标记不暴露给被测模型（判分侧用 expected_* 字段）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_exam_test_cases.py
# [A_module] module_id=MOD-RUB_case_assembler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
真实多文件注入装配器（Phase 3 极限深度）。

从项目 src/scripts 下读取真实治理文件，拼成带文件名标注的大上下文，
按 needles 埋针/埋错（注入不存在的方法引用、断的依赖边、伪造的字段），
用于 OLYMPIAD 级极限深度题。

设计要点（P3.1 / P3.3）：
- 路径白名单：仅允许读治理脚本 + task_gate（已审查、稳定、无敏感数据）。
- 埋针内容（fabricated line）会出现在给被测模型的上下文中——这是测试本体；
  但「埋针标记」（NEEDLE_xxx）仅作内部记账，不写入输出文本。
- 大文件按 max_chars_per_file 截断，避免单题上下文爆炸。
- 真实文件缺失时用占位符降级（保证模块可导入、mock 测试不抛异常），
  真实模型重跑时文件必然存在（同仓库）。
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

_logger = logging.getLogger(__name__)


# 白名单基目录（仅这些目录下的文件可被读取）
_WHITELIST_DIRS: tuple[Path, ...] = (
    REPO_ROOT / "scripts" / "governance",
    REPO_ROOT / "scripts",                 # scripts/git_commit.py 等顶层脚本
    REPO_ROOT / "src" / "zephyr" / "trading",
    REPO_ROOT / "src" / "zephyr" / "governance",
)

# 单文件默认截断阈值（字符数），避免 apply_depgraph.py(110k) 这类巨型文件撑爆上下文
_DEFAULT_MAX_CHARS = 12000


def _validate_whitelist(path: Path) -> None:
    """安全检查：仅允许读白名单目录下的文件。"""
    resolved = path.resolve()
    for base in _WHITELIST_DIRS:
        try:
            resolved.relative_to(base.resolve())
            return
        except ValueError:
            continue
    raise PermissionError(f"路径不在白名单内: {path}")


def read_real_file(rel_path: str, max_chars: int = _DEFAULT_MAX_CHARS) -> str:
    """读取白名单内的真实文件，返回（可能截断的）内容。

    缺失时返回占位符（不抛异常），保证模块可导入。
    """
    full = REPO_ROOT / rel_path
    try:
        _validate_whitelist(full)
    except PermissionError:
        _logger.warning("case_assembler: 路径越白名单，降级占位: %s", rel_path)
        return f"# [FALLBACK: {rel_path} — out of whitelist]\n"
    if not full.is_file():
        _logger.warning("case_assembler: 文件缺失，降级占位: %s", rel_path)
        return f"# [FALLBACK: {rel_path} — not found]\n"
    text = full.read_text(encoding="utf-8")
    if len(text) > max_chars:
        text = text[:max_chars] + f"\n# [... 截断：原 {len(text)} 字符，保留前 {max_chars} ...]\n"
    return text


def _inject_needle(content: str, needle: dict[str, Any]) -> str:
    """在 content 中注入单根针：after 锚点行后插入，锚点缺失则追加末尾。

    needle dict 结构：{"file": <basename>, "content": <注入行>, "after": <锚点子串|None>}
    """
    line = needle["content"]
    anchor = needle.get("after")
    if not anchor:
        return content.rstrip("\n") + "\n" + line + "\n"
    lines = content.splitlines(keepends=True)
    out: list[str] = []
    injected = False
    for ln in lines:
        out.append(ln)
        if not injected and anchor in ln:
            # 锚点行可能无尾换行，补齐
            if not ln.endswith("\n"):
                out.append("\n")
            out.append(line if line.endswith("\n") else line + "\n")
            injected = True
    if not injected:
        out.append(line if line.endswith("\n") else line + "\n")
    return "".join(out)


def assemble_real_context(
    file_specs: list[str],
    needles: list[dict[str, Any]] | None = None,
    *,
    max_chars_per_file: int = _DEFAULT_MAX_CHARS,
    extra_files: dict[str, str] | None = None,
) -> str:
    """读取真实文件 + 注入埋针，拼成带文件名标注的大上下文。

    Args:
        file_specs: 相对项目根的文件路径列表（必须在白名单内）。
        needles: 埋针列表，每项 {"file": basename, "content": 注入行, "after": 锚点|None}。
        max_chars_per_file: 单文件最大字符数（超出截断）。
        extra_files: 追加的伪造文件（filename -> content），用于埋错文件场景。

    Returns:
        拼接后的上下文字符串。每个文件以 ``===== FILE: <rel_path> =====`` 标注。
        埋针内容出现在文本中（测试本体），但无 NEEDLE 标记（不暴露判分侧记账）。
    """
    needles = needles or []
    extra_files = extra_files or {}
    # 按 basename 索引埋针
    needle_by_file: dict[str, list[Needle]] = {}
    for n in needles:
        needle_by_file.setdefault(n["file"], []).append(n)

    parts: list[str] = []
    for rel in file_specs:
        content = read_real_file(rel, max_chars=max_chars_per_file)
        name = Path(rel).name
        # 注入针对该文件的埋针
        for n in needle_by_file.get(name, []):
            content = _inject_needle(content, n)
        header = f"\n{'=' * 72}\n# FILE: {rel}\n{'=' * 72}\n"
        parts.append(header + content)

    # 追加伪造文件（埋错文件）
    for fname, fcontent in extra_files.items():
        header = f"\n{'=' * 72}\n# FILE: {fname}\n{'=' * 72}\n"
        parts.append(header + fcontent)

    return "\n".join(parts)
