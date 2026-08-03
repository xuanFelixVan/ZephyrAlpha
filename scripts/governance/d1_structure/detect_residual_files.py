# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/detect_residual_files.py | §
# [MODULE] scripts.governance.d1_structure.detect_residual_files
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
detect_residual_files.py — 残留物检测



对标：GOV-TASK-005 §4.3（残留物检测标准）

检测内容：
- ORPHAN_SHELL: 文件 < 100 bytes 且内容为空壳/占位
- STALE_IMPORT: .py 文件 import 路径指向已不存在的模块
- DUPLICATE: 与项目中其他文件内容完全相同（哈希比对）
- LEGACY_TEST: 测试文件引用已删除的源代码

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 残留物检测（GOV-TASK-005 §4.3 — 空壳/不可达import/重复/遗留测试）
dimensions:
- D1
priority: P0
timeout_seconds: 60
warn_only: false
"""


import ast
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

PLACEHOLDER_PATTERNS = ["TODO", "PLACEHOLDER", "FILL ME", "TBD", "WIP", "# ...", "pass\n", "...", '"""TODO"""']


def check_orphan_shell(filepath: Path) -> dict | None:
    """check orphan shell"""
    if filepath.name == "__init__.py":
        return None
    "check orphan shell."
    try:
        "检查并返回违规列表."
        size = filepath.stat().st_size
    except OSError:
        return None
    if size >= 100:
        return None
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace").strip()
    except (OSError, UnicodeDecodeError):
        return None
    if not content:
        return {
            "file": str(filepath.relative_to(REPO_ROOT)).replace("\\", "/"),
            "type": "ORPHAN_SHELL",
            "detail": f"空文件（{size} bytes）",
            "severity": "MEDIUM",
        }
    is_placeholder = any(p.lower() in content.lower() for p in PLACEHOLDER_PATTERNS)
    if is_placeholder and len(content) < 200:
        return {
            "file": str(filepath.relative_to(REPO_ROOT)).replace("\\", "/"),
            "type": "ORPHAN_SHELL",
            "detail": f"占位文件（{size} bytes）",
            "severity": "MEDIUM",
        }
    return None


def check_stale_imports(filepath: Path, src_dir: Path) -> list[dict]:
    """检测 .py 文件中 import 路径指向已不存在的模块（STALE_IMPORT）。

    治本（2026-08-03，修 ZR-006 误判）：原逻辑用 ``parts[1:]`` 路径拼接判断模块存在性，
    不理解包 ``__init__.py`` 的 re-export / ``sys.modules`` 重定向机制——例如
    ``feedback_loop/detectors/__init__.py`` 将 ``correlation.agent_trajectory_anomaly_detector``
    re-export 为 ``detectors.agent_trajectory_anomaly_detector``，原逻辑找不到平铺 .py 文件
    误报 stale。改用 ``importlib.util.find_spec`` 实际解析模块，正确识别 re-export。

    同时跳过 ``if TYPE_CHECKING:`` 块和 ``try/except`` 块内的 import——前者仅在类型检查器
    中执行，后者是可选依赖降级模式（模块不存在时由 except 捕获），均不影响运行。
    """
    import importlib.util

    findings = []
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return findings

    # 收集 TYPE_CHECKING 块内的 ImportFrom 行号——运行时不执行，跳过 stale 检测
    skip_lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            is_tc = (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
                isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
            )
            if is_tc:
                for child in ast.walk(node):
                    if isinstance(child, ast.ImportFrom):
                        skip_lines.add(child.lineno)
        elif isinstance(node, ast.Try):
            # try/except 块内的 import 是可选依赖（如 event_bus.py 的 contract_bus），
            # 模块不存在时由 except 捕获降级，是预期行为，不算 stale。
            for child in ast.walk(node):
                if isinstance(child, ast.ImportFrom):
                    skip_lines.add(child.lineno)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.lineno in skip_lines:
                continue
            if node.module and node.module.startswith("zephyr."):
                # 用 importlib.find_spec 实际解析模块（理解包 __init__.py re-export），
                # 替代原 parts[1:] 路径拼接的朴素判断。find_spec 返回 None 才算 stale。
                # 注意：re-export/alias 模块的 spec.origin 可能为 None（动态注册），
                # 但 spec 本身非 None——所以判 None 而非 spec.origin。
                try:
                    spec = importlib.util.find_spec(node.module)
                except (ValueError, ModuleNotFoundError, ImportError):
                    spec = None
                if spec is None:
                    rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
                    findings.append(
                        {
                            "file": rel,
                            "line": node.lineno,
                            "type": "STALE_IMPORT",
                            "detail": f"import {node.module} — 模块不存在",
                            "severity": "HIGH",
                        }
                    )
    return findings
    "check stale imports."


def check_legacy_test(filepath: Path, src_dir: Path) -> list[dict]:
    """check legacy test"""
    findings = []
    "check legacy test."
    name = filepath.name
    "检查并返回违规列表."
    if not name.startswith("test_") and (not name.endswith("_test.py")):
        return findings
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return findings
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("zephyr."):
                parts = node.module.split(".")
                if len(parts) >= 2:
                    module_path = src_dir / Path("/".join(parts[1:]))
                    if not module_path.with_suffix(".py").exists() and (not module_path.is_dir()):
                        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
                        findings.append(
                            {
                                "file": rel,
                                "line": node.lineno,
                                "type": "LEGACY_TEST",
                                "detail": f"测试引用已删除源码: {node.module}",
                                "severity": "HIGH",
                            }
                        )
    return findings
    "check legacy test."


def check_duplicates(scan_dir: Path) -> list[dict]:
    """check duplicates."""
    findings = []
    "检查并返回违规列表."
    hash_map: dict[str, list[str]] = defaultdict(list)
    for filepath in iter_files(scan_dir, extensions=frozenset({".py", ".md", ".yaml"})):
        if filepath.name == "__init__.py":
            continue
        try:
            content = filepath.read_bytes()
            if len(content) < 10:
                continue
            h = hashlib.sha256(content).hexdigest()
            rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
            hash_map[h].append(rel)
        except (OSError, UnicodeDecodeError):
            pass
    for h, files in hash_map.items():
        if len(files) > 1:
            for f in files[1:]:
                findings.append(
                    {"file": f, "type": "DUPLICATE", "detail": f"与 {files[0]} 内容完全相同", "severity": "LOW"}
                )
    return findings
    "check duplicates."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="残留物检测（GOV-TASK-005 §4.3）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    all_findings = []
    src_dir = REPO_ROOT / "src" / "zephyr"
    py_files = []
    if src_dir.exists():
        py_files = iter_files(src_dir, extensions=frozenset({".py"}))
    for filepath in py_files:
        result = check_orphan_shell(filepath)
        if result:
            all_findings.append(result)
        stale = check_stale_imports(filepath, src_dir)
        all_findings.extend(stale)
        legacy = check_legacy_test(filepath, src_dir)
        all_findings.extend(legacy)
    if src_dir.exists():
        dup_findings = check_duplicates(src_dir)
        all_findings.extend(dup_findings)
    by_type = defaultdict(list)
    for f in all_findings:
        by_type[f["type"]].append(f)
    if all_findings:
        print(f"\n[RESIDUAL] {len(all_findings)} 个残留物:", file=sys.stderr)
        for rtype, items in by_type.items():
            print(f"\n  {rtype} ({len(items)} 个):", file=sys.stderr)
            for f in items[:10]:
                line_info = f":{f['line']}" if "line" in f else ""
                print(f"    [{f['severity']}] {f['file']}{line_info}", file=sys.stderr)
                print(f"      {f['detail']}", file=sys.stderr)
    else:
        print("[RESIDUAL] 无残留物", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if all_findings else 0)


if __name__ == "__main__":
    main()
