# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/generate_script_manifest.py | §
# [MODULE] scripts.governance.generators.generate_script_manifest
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES] scripts.governance.generators.__init__
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
# [TTL] permanent
"""
generate_script_manifest.py — 脚本清单自动生成器

扫描 scripts/governance/ 下所有 .py 文件 → 提取 __manifest__ →
生成 script_manifest.yaml。

**病根（历史问题）**：早期仅用正则匹配三引号 YAML；若开发者写成
`__manifest__ = {"dimensions": [...], ...}` 的 **dict 字面量**，
生成器会误判为「manifest 缺失」→ manifest/蓝图/run_all 全线漂移。

**现行规则**（按顺序尝试，命中即止）：
1. 三引号双引号包裹的 YAML：`__manifest__` + `=` + ASCII 三引号 `"`×3 …（canonical，推荐）
2. 三引号单引号包裹的 YAML（同上，使用 `'`×3）
3. 模块顶层的 `__manifest__ = { ... }` —— 仅限 dict / list / 常量等安全字面量（`ast` 解析）

对标 §6.16 静态清单自动生成铁律。

__manifest__ 块格式（推荐）：
    __manifest__ = \"\"\"
    dimensions: [D5, D8]
    priority: P0
    timeout_seconds: 30
    description: >
      校验蓝图 §16 与磁盘实际文件的一致性。
    \"\"\"

Usage:
    python scripts/governance/generators/generate_script_manifest.py
    python scripts/governance/generators/generate_script_manifest.py --check
"""
# 双 manifest 体系说明（P1-T4 校正，2026-06-26）
# 本生成器 → scripts/governance/script_manifest.yaml（governance 子集 369，
#   __manifest__ 块提取，三引号 YAML / dict ast 多形态）
# 兄弟生成器 scripts/generate_manifest.py
#   → scripts/script_manifest.yaml（全树 563 脚本，简单 desc 提取）
# 二者非冗余：消费链不同（本生成器供 GATE-19 validate_static_manifest_drift --check；
#   兄弟供 GitCommitGateway _post_commit_reconcile + audit_registration）
# 禁止以"统一 SSoT"为由废弃任一——会破坏对应消费链。
# 详见 .trae/documents/systemic_drift_root_cure_continuation_plan.md §3

from __future__ import annotations

import argparse
import ast
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.constants import EXIT_FINDINGS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
from _shared.yaml_utils import load_yaml

__manifest__ = """
dimensions: [D1, D5]
priority: P1
timeout_seconds: 15
args:
  - {flag: --check, type: bool, description: "检测漂移 + 报告 missing manifest"}
  - {flag: --output, type: str, description: "输出路径"}
warn_only: false
description: >
  扫描 scripts/governance/**/*.py 的 __manifest__ 块，自动生成 script_manifest.yaml。
  对标 §6.16 静态清单自动生成铁律。
"""

SCRIPTS_DIR = REPO_ROOT / "scripts" / "governance"
DEFAULT_OUTPUT = SCRIPTS_DIR / "script_manifest.yaml"

EXCLUDE_DIRS = frozenset({"_shared", "__pycache__", "test_fixtures", "_archive"})  # 治本(ARCH-036 P0-C): 归档目录不应被脚本发现机制扫描

# ---------------------------------------------------------------------------
# 蓝图 §3.6 标签自动推导（与 run_all.py 同源）
# ---------------------------------------------------------------------------

_DIMENSION_TAGS: dict[str, list[str]] = {
    "D1": ["Quick"],
    "D2": ["Quick"],
    "D3": ["Quick"],
    "D4": ["Quick"],
    "D5": ["Critical"],
    "D6": ["Security", "Critical"],
    "D7": ["Critical"],
    "D8": ["Quick"],
    "D9": ["AI-Generated", "Periodic"],
    "D10": ["Periodic"],
    "D11": ["Security"],
    "D12": ["AI-Generated", "Periodic"],
}

_PREFIX_TAGS: tuple[tuple[str, list[str]], ...] = (
    ("fix_", ["Disruptive"]),
    ("generate_", ["Disruptive"]),
    ("audit_", ["Periodic"]),
)


def _derive_tags(script_name: str, dimensions: list[str], priority: str) -> list[str]:
    """_derive_tags implementation."""
    tags: set[str] = set()
    for dim in dimensions:
        tags.update(_DIMENSION_TAGS.get(str(dim), []))
    for prefix, prefix_tags in _PREFIX_TAGS:
        sn_lower = script_name.lower()
        if sn_lower.startswith(prefix) or f"/{prefix}" in sn_lower:
            tags.update(prefix_tags)
    if priority == "P0":
        tags.add("Critical")
    return sorted(tags)


def _extract_triple_quoted_yaml(source: str, delim: str) -> dict | None:
    """delim 为三引号：`\"\"\"` 或 `'''`。"""
    esc = re.escape(delim)
    pattern = rf"__manifest__\s*=\s*{esc}\s*\n(.*?){esc}"
    match = re.search(pattern, source, re.DOTALL)
    if not match:
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def _manifest_literal_from_ast(node: ast.expr) -> object:
    """将 AST 表达式转为 Python 字面量（仅限 manifest 允许的子集）。"""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return [_manifest_literal_from_ast(e) for e in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(_manifest_literal_from_ast(e) for e in node.elts)
    if isinstance(node, ast.Dict):
        out: dict[str, object] = {}
        for k, v in zip(node.keys, node.values, strict=False):
            if k is None or not isinstance(k, ast.Constant) or not isinstance(k.value, str):
                raise ValueError("manifest dict keys must be string literals")
            out[k.value] = _manifest_literal_from_ast(v)
        return out
    raise ValueError(f"unsupported manifest literal: {type(node).__name__}")


def _extract_module_level_manifest_dict_safe(source: str) -> dict | None:
    """_extract_module_level_manifest_dict_safe implementation."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in tree.body:
        expr: ast.expr | None = None
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "__manifest__":
                    expr = node.value
                    break
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == "__manifest__" and node.value is not None:
                expr = node.value
        if expr is None:
            continue
        if not isinstance(expr, ast.Dict):
            continue
        try:
            data = _manifest_literal_from_ast(expr)
        except ValueError:
            continue
        if isinstance(data, dict):
            return data
    return None


def extract_manifest_from_source(source: str) -> dict | None:
    """从源码提取 __manifest__；多形态兼容（消除 dict/yaml 分裂病根）。"""
    for data in (
        _extract_triple_quoted_yaml(source, '"""'),
        _extract_triple_quoted_yaml(source, "'''"),
        _extract_module_level_manifest_dict_safe(source),
    ):
        if data is not None:
            return data
    return None


def _derive_owner(rel_path: str) -> str:
    """_derive_owner implementation."""
    parts = rel_path.split("/")
    if len(parts) >= 2:
        return f"governance:{parts[0]}"
    return "governance"


def scan_scripts() -> list[dict]:
    """scan_scripts implementation."""
    scripts = []
    for py_file in sorted(SCRIPTS_DIR.rglob("*.py")):
        parts = py_file.relative_to(SCRIPTS_DIR).parts
        if any(p in EXCLUDE_DIRS for p in parts):
            continue
        if py_file.name == "__init__.py":
            continue

        rel_path = str(py_file.relative_to(SCRIPTS_DIR)).replace("\\", "/")
        source = py_file.read_text(encoding="utf-8")
        manifest = extract_manifest_from_source(source)
        owner = _derive_owner(rel_path)

        if manifest is None:
            scripts.append(
                {
                    "name": rel_path,
                    "owner": owner,
                    "dimensions": [],
                    "priority": "P2",
                    "timeout_seconds": 60,
                    "args": [],
                    "warn_only": False,
                    "description": "⚠ __manifest__ 缺失——请添加元数据块",
                    "tags": [],
                    "_manifest_missing": True,
                }
            )
            continue

        dims = manifest.get("dimensions", [])
        pri = manifest.get("priority", "P2")
        scripts.append(
            {
                "name": rel_path,
                "owner": manifest.get("owner", owner),
                "dimensions": dims,
                "priority": pri,
                "timeout_seconds": manifest.get("timeout_seconds", 60),
                "args": manifest.get("args", []),
                "warn_only": manifest.get("warn_only", False),
                "description": manifest.get("description", ""),
                "tags": _derive_tags(rel_path, dims, pri),
            }
        )

    return scripts


def generate() -> dict:
    """generate implementation."""
    scripts = scan_scripts()
    missing = sum(1 for s in scripts if s.get("_manifest_missing"))
    total = len(scripts)

    categories: dict[str, int] = {}
    for s in scripts:
        owner = s.get("owner", "governance")
        categories[owner] = categories.get(owner, 0) + 1

    return {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "scripts/governance/generators/generate_script_manifest.py",
        "source": "scripts/governance/**/*.py → __manifest__ 块",
        "total_scripts": total,
        "with_manifest": total - missing,
        "missing_manifest": missing,
        "categories": categories,
        "scripts": scripts,
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="从 __manifest__ 块自动生成 script_manifest.yaml")
    parser.add_argument("--check", action="store_true", help="检测漂移 + 报告 missing manifest")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT), help="输出路径")
    args = parser.parse_args()

    result = generate()

    if args.check:
        missing = result["missing_manifest"]
        if missing > 0:
            print(f"WARNING: {missing}/{result['total_scripts']} 个脚本缺少 __manifest__ 块")
        existing = load_yaml(args.output)
        ex_scripts = existing.get("scripts", [])
        if len(ex_scripts) != result["total_scripts"]:
            print(f"DRIFT: 磁盘 {len(ex_scripts)} 脚本 ≠ 实际 {result['total_scripts']} 脚本")
            sys.exit(EXIT_FINDINGS)
        print(f"OK: 脚本清单与实际一致（{result['total_scripts']} 个脚本）")
        return

    content = (
        f"# 自动生成于 {result['generated_at']}\n"
        "# 来源: scripts/governance/**/*.py __manifest__ 块\n"
        "# 手工编辑无效——修改请通过各 .py 文件的 __manifest__ 块\n\n"
        + yaml.dump(result, allow_unicode=True, default_flow_style=False, sort_keys=False)
    )
    atomic_write_safe(args.output, content)
    print(f"已生成 {result['total_scripts']} 个脚本清单 → {args.output}")
    if result["missing_manifest"]:
        print(f"⚠ {result['missing_manifest']} 个脚本缺少 __manifest__ 块")


if __name__ == "__main__":
    main()
