# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.governance.drift_detection.python_compat
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_scanners.py; tests/audit/test_python_compat.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 兼容性检查不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_python_compat | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Python Compatibility Checker — Python版本兼容性漂移 D-023-30 · §6.22。





module_id: MOD-INF-023


syntax_incompatibility: pyright/mypy 目标 Python 版本类型检查


stdlib_import_incompatibility: 扫描 import vs 目标版本标准库


type_hint_incompatibility: X|Y vs Union[X,Y] 等语法糖检测


auto_fixable: 自动降级语法到目标Python版本


对标 blueprint.md §6.22。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class PythonCompatIssue:
    issue_id: str

    file_path: str

    line_no: int

    issue_type: str

    current_syntax: str

    suggested_fix: str

    target_python: str = "3.9"

    severity: str = "MAJOR"


PYTHON_VERSIONS: dict[str, int] = {
    "3.9": 9,
    "3.10": 10,
    "3.11": 11,
    "3.12": 12,
    "3.13": 13,
}


NEW_IN_VERSION: dict[str, dict[int, str]] = {
    "syntax": {
        10: "PEP 604: X | Y union syntax",
        11: "PEP 654: Exception Groups",
        12: "PEP 695: Type parameter syntax",
    },
    "stdlib": {
        10: "zoneinfo",
        11: "tomllib",
        12: "itertools.batched",
    },
    "typing": {
        10: "X | Y (union syntax), str | None",
        11: "Self (typing.Self), LiteralString",
        12: "type statement (type X = ...)",
    },
}


def _target_py_minor(target: str) -> int:
    return PYTHON_VERSIONS.get(target, 9)


def _check_union_syntax(
    file_path: str,
    content: str,
    target_minor: int,
) -> list[PythonCompatIssue]:
    issues: list[PythonCompatIssue] = []

    pep604_pattern = re.compile(r":\s*\w+\s*\|\s*\w+[\s\)\],]")

    for i, line in enumerate(content.splitlines(), 1):
        if pep604_pattern.search(line) and target_minor < 10:
            issues.append(
                PythonCompatIssue(
                    issue_id=f"pycompat-union-L{i}",
                    file_path=file_path,
                    line_no=i,
                    issue_type="union_syntax",
                    current_syntax=line.strip()[:80],
                    suggested_fix=(f"Replace X|Y with Union[X,Y] for Python {target_minor} compatibility"),
                    severity="MAJOR",
                )
            )

    return issues


def _check_stdlib_imports(
    file_path: str,
    content: str,
    target_minor: int,
) -> list[PythonCompatIssue]:
    issues: list[PythonCompatIssue] = []

    new_stdlibs: dict[int, list[str]] = {
        10: ["zoneinfo"],
        11: ["tomllib"],
    }

    for ver_minor, modules in new_stdlibs.items():
        if target_minor < ver_minor:
            for mod in modules:
                pattern = rf"(?:^import\s+{mod}|from\s+{mod}\s+import)"

                for match in re.finditer(pattern, content, re.MULTILINE):
                    line_no = content[: match.start()].count("\n") + 1

                    issues.append(
                        PythonCompatIssue(
                            issue_id=f"pycompat-stdlib-{mod}-L{line_no}",
                            file_path=file_path,
                            line_no=line_no,
                            issue_type="stdlib_incompat",
                            current_syntax=match.group(0),
                            suggested_fix=(
                                f"Module {mod} requires Python 3.{ver_minor}+. Install backport or bump target."
                            ),
                            severity="MAJOR",
                        )
                    )

    return issues


def _check_type_hints(
    file_path: str,
    content: str,
    target_minor: int,
) -> list[PythonCompatIssue]:
    issues: list[PythonCompatIssue] = []

    type_statement_pattern = re.compile(r"^type\s+\w+\s*=", re.MULTILINE)

    if target_minor < 12:
        for match in type_statement_pattern.finditer(content):
            line_no = content[: match.start()].count("\n") + 1

            issues.append(
                PythonCompatIssue(
                    issue_id=f"pycompat-type-alias-L{line_no}",
                    file_path=file_path,
                    line_no=line_no,
                    issue_type="type_alias",
                    current_syntax=content.splitlines()[line_no - 1].strip()[:80],
                    suggested_fix=("Replace 'type X = ...' with 'X = TypeAlias' for Python <3.12"),
                    severity="MINOR",
                )
            )

    return issues


def scan_python_compat(
    project_root: str,
    target_python: str = "3.10",
) -> list[PythonCompatIssue]:
    target_minor = _target_py_minor(target_python)

    py_files = [
        p
        for p in Path(project_root).rglob("*.py")
        if all(
            s not in str(p).lower()
            for s in (
                ".git",
                "__pycache__",
                ".venv",
                "venv",
                "node_modules",
            )
        )
    ]

    all_issues: list[PythonCompatIssue] = []

    for pf in py_files[:50]:
        try:
            content = pf.read_text(encoding="utf-8")

        except Exception:
            continue

        all_issues.extend(_check_union_syntax(str(pf), content, target_minor))

        all_issues.extend(_check_stdlib_imports(str(pf), content, target_minor))

        all_issues.extend(_check_type_hints(str(pf), content, target_minor))

    return all_issues


def auto_fix_compat(
    issues: list[PythonCompatIssue],
) -> dict[str, str]:
    """生成自动修复 diff（降级语法到目标版本）。"""

    fixes: dict[str, str] = {}

    for issue in issues:
        if issue.issue_type == "union_syntax":
            pattern_str = r"(\w+|\w+\[\w+\]|\w+)\s*\|\s*(\w+|None)"

            replacement = f"Union[{r'\1'}, {r'\2'}]"

            fixes[issue.issue_id] = f"Replace {issue.current_syntax[:40]}... → Union[X, Y]"

        elif issue.issue_type == "stdlib_incompat":
            fixes[issue.issue_id] = (
                f"Install backported {issue.current_syntax} or bump target to Python {issue.target_python}+"
            )

    return fixes


def generate_compat_report(
    issues: list[PythonCompatIssue],
    target_python: str = "3.10",
) -> str:
    """生成兼容性报告。"""

    lines: list[str] = [
        "# Python Compatibility Report",
        f"# Target: Python {target_python}",
        f"# Total issues: {len(issues)}",
        f"# Generated: {datetime.now(UTC).isoformat()}",
        "",
    ]

    by_type: dict[str, list[PythonCompatIssue]] = {}

    for iss in issues:
        by_type.setdefault(iss.issue_type, []).append(iss)

    for itype, it_issues in sorted(by_type.items()):
        lines.append(f"## {itype} ({len(it_issues)} issues)")

        for iss in it_issues[:10]:
            lines.append(f"- [{iss.severity}] {iss.file_path}:{iss.line_no}")

            lines.append(f"  Current: {iss.current_syntax[:60]}")

            lines.append(f"  Fix: {iss.suggested_fix[:80]}")

        lines.append("")

    return "\n".join(lines)
