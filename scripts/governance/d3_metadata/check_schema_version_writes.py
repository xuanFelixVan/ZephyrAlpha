#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.check_schema_version_writes
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] G_TRAE_059 gate
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只读扫描; 不修改任何文件
# [MODIFY-GUARD] 无
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=无违规; exit 1=发现违规; exit 2=加载失败
# [TESTS] manual --dry-run
# [TTL] task_bound
"""
G_TRAE_059 验证脚本：_schema_version 写入保护 + 版本一致性检查。

两层检查：
1. AST 扫描：检测非 depgraph_schema.py 文件中对 _schema_version 表的写入操作
2. DB 状态校验：_schema_version.MAX(version) == _MIGRATIONS 最大版本号

用法:
    python scripts/governance/check_schema_version_writes.py            # AST 扫描
    python scripts/governance/check_schema_version_writes.py --db-check  # DB 状态校验
    python scripts/governance/check_schema_version_writes.py --all       # 全部检查
"""

__manifest__ = """
args: []
description: G_TRAE_059 验证脚本：_schema_version 写入保护 + 版本一致性检查。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import ast
import re
import sys
from pathlib import Path

# 治本(2026-06-30): _REPO_ROOT 删除, REPO_ROOT 真源来自 _shared.constants (SSoT)
SCAN_DIRS = ["src/zephyr", "scripts", "tests"]

# P2迁移后：depgraph.db 已迁移到 PostgreSQL，通过 _shared.constants 获取 PG 连接。
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection, REPO_ROOT as _REPO_ROOT  # noqa: E402  治本(2026-06-30): SSoT
# Whitelist: depgraph_schema.py (depgraph.db migrations) + sqlite_schema.py (governance.db migrations)
WHITELIST = {
    "src/zephyr/governance/depgraph_schema.py",
    "src/zephyr/governance/persistence/sqlite_schema.py",
}
WRITE_PATTERNS = {"insert", "update", "replace"}
# Word-boundary pattern: matches _schema_version but NOT _capacity_schema_version
_SCHEMA_VERSION_RE = re.compile(r"(?<![a-z_])_schema_version(?![a-z_])", re.IGNORECASE)


def _check_ast_string(node_value: str) -> bool:
    """Check if a string literal contains a _schema_version write operation.

    Uses word-boundary matching to avoid false positives like _capacity_schema_version.
    """
    lowered = node_value.lower()
    if not _SCHEMA_VERSION_RE.search(lowered):
        return False
    return any(p in lowered for p in WRITE_PATTERNS)


def _scan_file(filepath: Path) -> list[str]:
    """Scan a single Python file for _schema_version write operations.

    Returns a list of violation descriptions (empty if clean).
    Excludes docstrings (only checks actual SQL string literals in execute() calls).
    """
    violations = []
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return violations

    # Collect docstring node IDs to exclude them
    docstring_ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                docstring_ids.add(id(node.body[0].value))

    for node in ast.walk(tree):
        # Check string literals (SQL statements in execute() calls)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in docstring_ids:
                continue
            if _check_ast_string(node.value):
                rel = filepath.relative_to(_REPO_ROOT).as_posix()
                violations.append(
                    f"{rel}:{node.lineno}: _schema_version write detected: {node.value[:80].strip()}"
                )
    return violations


def run_ast_scan() -> int:
    """AST scan: detect non-depgraph_schema.py files writing to _schema_version."""
    print("[G_TRAE_059] AST scan: checking for _schema_version writes...")
    all_violations = []
    files_scanned = 0

    for scan_dir in SCAN_DIRS:
        root = _REPO_ROOT / scan_dir
        if not root.exists():
            continue
        for py_file in root.rglob("*.py"):
            rel = py_file.relative_to(_REPO_ROOT).as_posix()
            if rel in WHITELIST:
                continue
            files_scanned += 1
            violations = _scan_file(py_file)
            all_violations.extend(violations)

    print(f"  Files scanned: {files_scanned} (excluding {len(WHITELIST)} whitelist)")
    if all_violations:
        print(f"  [FAIL] Found {len(all_violations)} violation(s):")
        for v in all_violations:
            print(f"    - {v}")
        return 1
    print("  [PASS] No _schema_version writes found outside whitelist.")
    return 0


def run_db_check() -> int:
    """DB state check: verify _schema_version.MAX(version) == _MIGRATIONS max version."""
    print("[G_TRAE_059] DB check: verifying schema version consistency...")

    sys.path.insert(0, str(_REPO_ROOT / "src"))
    # 5.154.6 修复: 使用 MIGRATIONS 公共别名而非 _MIGRATIONS 私有列表
    from zephyr.governance.depgraph_schema import MIGRATIONS

    migrations_max = max(v for v, _, _ in MIGRATIONS)
    print(f"  MIGRATIONS max version: v{migrations_max}")

    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        row = conn.execute("SELECT MAX(version) AS max_version FROM _schema_version").fetchone()
        db_max = row["max_version"] if row else None
    finally:
        conn.close()

    print(f"  DB _schema_version MAX: v{db_max}")

    if db_max != migrations_max:
        print(f"  [FAIL] Version mismatch: DB v{db_max} != MIGRATIONS v{migrations_max}")
        return 1
    print("  [PASS] DB version matches _MIGRATIONS max version.")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--db-check" in args:
        return run_db_check()
    if "--all" in args:
        r1 = run_ast_scan()
        r2 = run_db_check()
        return max(r1, r2)
    return run_ast_scan()


if __name__ == "__main__":
    sys.exit(main())
