# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/detectors/detect_duplicate_module_names.py | §
# [MODULE] scripts.governance.d5_architecture.detectors.detect_duplicate_module_names
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.detectors.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""detect_duplicate_module_names.py --- 同名模块语义关系分析



对标：AGENTS.md §6.4（最有利于 AI 施工 --- 机器可读优于自然语言推理）
     §6.1（专业机构论证先行 --- 不能靠"感觉"判断冲突）

检测 src/zephyr/ 下同名 .py 文件的语义关系，区分三类情况：
- 适配器/消费者（Facade）：一个文件导入另一个 --- INFO，不阻塞
- 真正重复定义：无 import 关系 + 定义相同符号 --- HIGH，必须调查
- 仅名称碰撞：无 import 关系 + 定义不同符号 --- LOW，命名规范建议

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 同名模块语义关系分析——AST级导入链+符号重叠检测，区分适配器/Facade vs 真正重复
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import ast
import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_PY, SRC_DIR
from _shared.walk import iter_files


def _file_to_module_path(filepath: Path) -> str:
    """_file_to_module_path implementation."""
    rel = filepath.relative_to(SRC_DIR)
    parts = list(rel.parts[:-1])
    if parts:
        return "zephyr." + ".".join(parts)
    return "zephyr"


def _parse_import_targets(filepath: Path) -> set[str]:
    """_parse_import_targets implementation."""
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except (SyntaxError, OSError):
        return set()

    targets: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                targets.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                targets.add(node.module)
    return targets


def _parse_public_symbols(filepath: Path) -> set[str]:
    """_parse_public_symbols implementation."""
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except (SyntaxError, OSError):
        return set()

    symbols: set[str] = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            symbols.add(node.name)
        elif isinstance(node, ast.FunctionDef):
            if not node.name.startswith("_"):
                symbols.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    symbols.add(target.id)
    return symbols


def _analyze_pair(file_a: Path, file_b: Path) -> tuple[str, str, str | None]:
    """_analyze_pair implementation."""
    pkg_a = _file_to_module_path(file_a)
    pkg_b = _file_to_module_path(file_b)

    imports_a = _parse_import_targets(file_a)
    imports_b = _parse_import_targets(file_b)

    a_consumes_b = any(t == pkg_b or t.startswith(pkg_b + ".") for t in imports_a) or (
        any(t == "zephyr" or t.startswith("zephyr.") for t in imports_a)
        and _file_to_module_path(file_b) in str(imports_a)
    )

    b_consumes_a = any(t == pkg_a or t.startswith(pkg_a + ".") for t in imports_b) or (
        any(t == "zephyr" or t.startswith("zephyr.") for t in imports_b)
        and _file_to_module_path(file_a) in str(imports_b)
    )

    if a_consumes_b:
        symbols_a = _parse_public_symbols(file_a)
        symbols_b = _parse_public_symbols(file_b)
        overlap = symbols_a & symbols_b
        if overlap:
            return (
                "MEDIUM",
                "adapter_with_overlap",
                f"{file_a.name} 是 {file_b.name} 的消费者，但两者定义了相同的公共符号: {', '.join(sorted(overlap))}",
            )
        return (
            "INFO",
            "adapter",
            f"{file_a.name} 导入自 {_file_to_module_path(file_b)}，属于适配器/Facade 模式",
        )

    if b_consumes_a:
        symbols_a = _parse_public_symbols(file_a)
        symbols_b = _parse_public_symbols(file_b)
        overlap = symbols_a & symbols_b
        if overlap:
            return (
                "MEDIUM",
                "adapter_with_overlap",
                f"{file_b.name} 是 {file_a.name} 的消费者，但两者定义了相同的公共符号: {', '.join(sorted(overlap))}",
            )
        return (
            "INFO",
            "adapter",
            f"{file_b.name} 导入自 {_file_to_module_path(file_a)}，属于适配器/Facade 模式",
        )

    symbols_a = _parse_public_symbols(file_a)
    symbols_b = _parse_public_symbols(file_b)
    overlap = symbols_a & symbols_b

    if overlap:
        return (
            "HIGH",
            "true_duplication",
            f"同名文件 {file_a.name} 定义了相同公共符号且无 import 关系: {', '.join(sorted(overlap))}",
        )

    return (
        "LOW",
        "name_collision_only",
        f"同名文件 {file_a.name} 在不同目录，但公共符号无重叠",
    )


def scan() -> tuple[list[dict], int]:
    """scan."""
    findings: list[dict] = []
    """scan."""
    files_scanned = 0

    by_basename: dict[str, list[Path]] = defaultdict(list)
    for filepath in iter_files(SRC_DIR, extensions=SCAN_EXTENSIONS_PY, exclude_files=frozenset({"__init__.py"})):
        by_basename[filepath.name].append(filepath)
        files_scanned += 1

    for basename, paths in sorted(by_basename.items()):
        if len(paths) < 2:
            continue

        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                severity, category, message = _analyze_pair(paths[i], paths[j])
                rel_a = paths[i].relative_to(REPO_ROOT)
                rel_b = paths[j].relative_to(REPO_ROOT)
                findings.append(
                    {
                        "severity": severity,
                        "category": category,
                        "file": str(rel_a),
                        "peer": str(rel_b),
                        "message": message,
                    }
                )

    return findings, files_scanned
    """scan."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="同名模块语义关系分析 --- 区分适配器 vs 真正重复")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="所有严重度均不改变 exit code（始终返回 0）",
    )
    args = parser.parse_args()

    findings, files_scanned = scan()

    if not findings:
        print(f"OK: 扫描 {files_scanned} 个 .py 文件，无同名模块冲突", file=sys.stderr)
        sys.exit(EXIT_PASS)

    by_severity: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        by_severity[f["severity"]].append(f)

    for severity in ("HIGH", "MEDIUM", "LOW", "INFO"):
        items = by_severity.get(severity, [])
        if not items:
            continue
        print(f"\n--- {severity} ({len(items)} 对) ---", file=sys.stderr)
        for item in items:
            print(f"  {item['file']}", file=sys.stderr)
            print(f"  {item['peer']}", file=sys.stderr)
            print(f"  -> [{item['category']}] {item['message']}", file=sys.stderr)
            print(file=sys.stderr)

    total_high = len(by_severity.get("HIGH", []))
    total_medium = len(by_severity.get("MEDIUM", []))
    total_low = len(by_severity.get("LOW", []))
    total_info = len(by_severity.get("INFO", []))

    print(
        f"扫描 {files_scanned} 个 .py 文件, "
        f"{len(findings)} 对同名模块: "
        f"HIGH={total_high} MEDIUM={total_medium} LOW={total_low} INFO={total_info}",
        file=sys.stderr,
    )

    if args.warn_only:
        sys.exit(EXIT_PASS)

    sys.exit(EXIT_FINDINGS if findings else EXIT_PASS)


if __name__ == "__main__":
    main()
