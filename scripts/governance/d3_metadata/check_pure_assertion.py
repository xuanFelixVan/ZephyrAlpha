# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/check_pure_assertion.py | §gate-pure-assertion
# [MODULE] scripts.governance.d3_metadata.check_pure_assertion
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] —
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.pure_assertion_gate (subprocess --ci)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] GOV-DOC-016 纯陈述原则检测真源——6 条 regex 检测"过去态"过渡文本；只检 .md 文件（YAML 规则由 rules_integrity_reconciler 负责）；跳过 frontmatter + 代码块避免误报；--ci 模式只检 added 行（增量），--full-scan 模式检全行；exit 0=clean, 1=violations, 2=error
# [MODIFY-GUARD] 改 6 条 regex 同步改 test_check_pure_assertion.py 命中用例；改 scope INCLUDE/EXCLUDE 同步改 design §1.2 + test scope 边界用例
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_CLEAN=0（无违规）；EXIT_FINDINGS=1（--ci 模式检出违规）；EXIT_ERROR=2（脚本异常）；gate 调用时 exit 2 fail-open
# [TESTS] tests/governance/d3_metadata/test_check_pure_assertion.py
# [TTL] permanent
"""check_pure_assertion.py — GOV-DOC-016 纯陈述原则检测真源（SSoT）。

检测 .md 文档中的"过去态"过渡文本（如"已废止""之前是X现在改为Y"），
正文只应承载当前真实值，历史差异是 git log 的职责。

双模式：
  --ci <files>      供 pure_assertion_gate.py subprocess 调用（增量 added 行）
  --full-scan       供一次性审计（全量扫描所有 in-scope .md）

Exit codes: 0=clean, 1=violations found, 2=script error
"""

from __future__ import annotations

import re

# Exit codes
EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_ERROR = 2

# 6 条违规 regex（从 cde1255c^ 恢复，原版词表）
_VIOLATION_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"已[废止弃]\w*"), "已废止/已废弃/已弃用"),
    (re.compile(r"旧[定规]义?[则]?"), "旧定义/旧规则"),
    (re.compile(r"之前是.{1,30}现在"), "之前是X现在改为Y"),
    (re.compile(r"已被取[代替]"), "已被取代/已被替代"),
    (re.compile(r"P[0-9]迁移后"), "P2迁移后"),
    (re.compile(r"从.{1,30}迁移(至|到)"), "从X迁移到Y"),
]

# Scope：INCLUDE 目录前缀
_SCOPE_INCLUDE_DIRS = [
    ".trae/rules/",
    "docs/01_policies_and_standards/",
    "docs/02_enterprise_architecture/",
    "docs/03_modules/",
    "docs/08_knowledge/",
]

# Scope：INCLUDE 精确文件
_SCOPE_INCLUDE_FILES = [
    "AGENTS.md",
    "README.md",
]

# Scope：EXCLUDE 目录前缀（即使命中 INCLUDE 也跳过）
_SCOPE_EXCLUDE_DIRS = [
    "docs/_archive/",
    "docs/_working/",
    "session_logs/",
    "docs/03_governance_reports/",
    "docs/01_policies_and_standards/rules/",
]

# Scope：EXCLUDE 精确文件
_SCOPE_EXCLUDE_FILES = [
    "docs/02_enterprise_architecture/architecture_debt_registry.md",
]

# Scope：EXCLUDE basename（任意层级匹配）
_SCOPE_EXCLUDE_BASENAMES = [
    "CHANGELOG.md",
]


def _is_in_scope(rel_path: str) -> bool:
    """判定 .md 文件是否在 PURE-ASSERTION gate 检测范围内。

    Args:
        rel_path: 相对项目根的路径（正斜杠）。

    Returns:
        True 若 in-scope（INCLUDE 命中且 EXCLUDE 未命中）。
    """
    rel_path = rel_path.replace("\\", "/")
    if not rel_path.endswith(".md"):
        return False
    # EXCLUDE 优先
    for excl_dir in _SCOPE_EXCLUDE_DIRS:
        if rel_path.startswith(excl_dir):
            return False
    for excl_file in _SCOPE_EXCLUDE_FILES:
        if rel_path == excl_file:
            return False
    basename = rel_path.rsplit("/", 1)[-1]
    for excl_bn in _SCOPE_EXCLUDE_BASENAMES:
        if basename == excl_bn:
            return False
    # INCLUDE
    for incl_dir in _SCOPE_INCLUDE_DIRS:
        if rel_path.startswith(incl_dir):
            return True
    for incl_file in _SCOPE_INCLUDE_FILES:
        if rel_path == incl_file:
            return True
    return False


def _check_file(content: str, added_lines: set[int] | None) -> list[str]:
    """检测文件内容中的纯陈述违规。

    Args:
        content: 文件完整内容。
        added_lines: 需检测的 1-based 行号集合（None=检测所有行）。

    Returns:
        违规描述列表，格式 "line {n}: [{pattern_name}] {line_content}"。
    """
    violations: list[str] = []
    in_frontmatter = False
    in_code_block = False

    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()

        # frontmatter 状态机（仅文件首行 --- 触发）
        if i == 1 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter and stripped == "---":
            in_frontmatter = False
            continue

        # 代码块状态机（``` 或 ~~~ toggle）
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            continue

        # 跳过 frontmatter 和代码块
        if in_frontmatter or in_code_block:
            continue

        # 增量模式：只检 added 行（状态机仍跟踪所有行）
        if added_lines is not None and i not in added_lines:
            continue

        # 匹配 6 条违规 regex
        for pattern, name in _VIOLATION_PATTERNS:
            # 表格行和受控词表行豁免（当前态描述，非历史过渡）
            # 已废止/已废弃/已弃用：表格状态值（| 已废弃 |）和受控词表定义行是当前态描述
            # 已被取代/已被替代：蓝图 §15 表格中的"已被取代的旧蓝图"也是当前态描述
            if name in ("已废止/已废弃/已弃用", "已被取代/已被替代"):
                if stripped.startswith("|"):
                    continue
            if name == "已废止/已废弃/已弃用":
                # 受控词表定义行（"存在性状态"/"存在性："/"未实现/已实现"等变体）
                if any(marker in line for marker in ("受控词表", "存在性状态", "存在性：", "未实现/已实现")):
                    continue
                # 文件树行（auto-generated file tree，"已废弃"是当前态文件标签）
                if stripped.startswith(("│", "├", "└")):
                    continue
                # 受控词表 bullet 定义行（"> - `已废弃`：..." / "- `deprecated`：..."）
                # 以及生命周期值枚举行（"→已废弃" / "→ 已废弃"）
                if "`已废弃`" in line or "`deprecated`" in line:
                    continue
                if "→已废弃" in line or "→ 已废弃" in line:
                    continue
            if pattern.search(line):
                violations.append(f"line {i}: [{name}] {line.strip()}")
                break  # 一行只报一条

    return violations


# ---------------------------------------------------------------------------
# --ci / --full-scan 双模式入口（Task 2 追加）
# ---------------------------------------------------------------------------
import argparse
import os
import subprocess
import sys

_HUNK_HEADER_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def _get_project_root() -> str:
    """获取 git 项目根目录。"""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return os.getcwd()


def _to_rel_path(abs_or_rel: str, project_root: str) -> str:
    """将路径转为相对项目根的正斜杠路径。"""
    p = os.path.abspath(abs_or_rel)
    root = os.path.abspath(project_root)
    if p.startswith(root):
        rel = p[len(root):].lstrip(os.sep)
        return rel.replace("\\", "/")
    return abs_or_rel.replace("\\", "/")


def _get_added_lines_ci(rel_path: str) -> set[int]:
    """--ci 模式：从 git diff --cached 提取 added 行号集合。"""
    try:
        r = subprocess.run(
            ["git", "diff", "--cached", "--unified=0", "--", rel_path],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if r.returncode != 0:
            return set()
    except Exception:
        return set()
    added: set[int] = set()
    current = 0
    for line in r.stdout.splitlines():
        m = _HUNK_HEADER_RE.match(line)
        if m:
            current = int(m.group(1))
            continue
        if line.startswith("+++"):
            continue
        if line.startswith("+"):
            added.add(current)
            current += 1
        elif line.startswith("-"):
            pass
        else:
            current += 1
    return added


def _read_staged_content(rel_path: str) -> str:
    """读取 staged 版本文件内容（git show :path）。"""
    try:
        r = subprocess.run(
            ["git", "show", ":" + rel_path],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if r.returncode == 0:
            return r.stdout
    except Exception:
        pass
    return ""


def _walk_scope_files(project_root: str) -> list[str]:
    """--full-scan 模式：遍历项目根，返回所有 in-scope .md 文件绝对路径。"""
    result: list[str] = []
    for dirpath, _dirs, filenames in os.walk(project_root):
        # 跳过 .git
        if ".git" in dirpath:
            continue
        for fname in filenames:
            if not fname.endswith(".md"):
                continue
            abs_path = os.path.join(dirpath, fname)
            rel = _to_rel_path(abs_path, project_root)
            if _is_in_scope(rel):
                result.append(abs_path)
    return result


def _run_ci_mode(files: list[str], project_root: str) -> int:
    """--ci 模式：检查指定文件的 added 行。"""
    all_violations: list[str] = []
    for abs_file in files:
        rel = _to_rel_path(abs_file, project_root)
        if not _is_in_scope(rel):
            continue
        added = _get_added_lines_ci(rel)
        if not added:
            continue
        content = _read_staged_content(rel)
        if not content:
            continue
        violations = _check_file(content, added)
        for v in violations:
            all_violations.append(f"{rel}: {v}")
    if all_violations:
        print("PURE_ASSERTION_VIOLATION——检出纯陈述原则违规（GOV-DOC-016）：", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)
        print("\n正文只应承载当前真实值，历史差异是 git log 的职责。", file=sys.stderr)
        print("修复：删除过渡文本（'已废止''之前是X现在改为Y'等），直接写当前值。", file=sys.stderr)
        return EXIT_FINDINGS
    return EXIT_CLEAN


def _run_full_scan(project_root: str) -> int:
    """--full-scan 模式：全量扫描所有 in-scope .md 文件。"""
    files = _walk_scope_files(project_root)
    all_violations: list[str] = []
    for abs_file in files:
        rel = _to_rel_path(abs_file, project_root)
        try:
            with open(abs_file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            continue
        violations = _check_file(content, None)
        for v in violations:
            all_violations.append(f"{rel}: {v}")
    if all_violations:
        print(f"PURE-ASSERTION full-scan: 检出 {len(all_violations)} 条违规：", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)
        return EXIT_FINDINGS
    print(f"PURE-ASSERTION full-scan: 扫描 {len(files)} 个 in-scope .md 文件，0 违规。")
    return EXIT_CLEAN


def main() -> int:
    """入口：argparse 解析 --ci / --full-scan。"""
    parser = argparse.ArgumentParser(
        description="GOV-DOC-016 纯陈述原则检测（SSoT）"
    )
    parser.add_argument(
        "--ci", nargs="*", default=None, metavar="FILE",
        help="增量模式：检查指定文件的 staged added 行",
    )
    parser.add_argument(
        "--full-scan", action="store_true",
        help="全量模式：扫描所有 in-scope .md 文件",
    )
    args = parser.parse_args()

    project_root = _get_project_root()

    if args.full_scan:
        return _run_full_scan(project_root)
    if args.ci is not None:
        return _run_ci_mode(args.ci, project_root)
    # 无参数：报错
    print("错误：必须指定 --ci <files> 或 --full-scan", file=sys.stderr)
    return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
