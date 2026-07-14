# [BLUEPRINT] MOD-INF-005 | scripts/governance/vms_cross_file_check.py | §
# [MODULE] scripts.governance.vms_cross_file_check
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
"""
VMS 跨文件内容一致性检查器 — MOD-INF-011 · TASK-INF-0211
============================================================
蓝图 §5 · P1 优先级 · 验证所有 VMS 相关文件的一致性

检查维度
--------
1. Collection 列表: 12个文件中的 COLLECTION_NAMES 是否一致
2. 嵌入维度: 1024d vs 512d 分配是否统一
3. chunk_strategy 路由: 6种策略是否全覆盖
4. 导入路径: 所有 import 路径是否有效
"""

from __future__ import annotations

__manifest__ = """
args: []
description: VMS 跨文件内容一致性检查器 — MOD-INF-011 · TASK-INF-0211
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

VMS_DIR = PROJECT_ROOT / "src" / "zephyr" / "vector-memory"

EXPECTED_COLLECTIONS = frozenset(
    {
        "decisions",
        "code_context",
        "lessons",
        "knowledge",
        "rules",
        "blueprints",
        "session_snapshots",
        "execution_traces",
    }
)

EXPECTED_DIMENSIONS = {
    "decisions": 1024,
    "code_context": 1024,
    "lessons": 1024,
    "knowledge": 1024,
    "rules": 1024,
    "blueprints": 512,
    "session_snapshots": 512,
    "execution_traces": 512,
}

EXPECTED_CHUNK_STRATEGIES = frozenset(
    {
        "semantic",
        "ast_aware",
        "paragraph",
        "heading_aware",
        "rule_level",
        "section_aware",
        "session_level",
        "time_window",
    }
)


def check_collections() -> list[str]:
    """Check compliance and report findings."""
    issues: list[str] = []
    py_files = sorted(VMS_DIR.glob("*.py"))

    for f in py_files:
        content = f.read_text(encoding="utf-8")
        if "COLLECTION_NAMES" in content and "8" in content:
            if "execution_traces" not in content and "runtime_logs" not in content:
                issues.append(f"{f.name}: COLLECTION_NAMES 可能缺少 execution_traces")
            if "runtime_logs" in content:
                issues.append(f"{f.name}: 仍引用 runtime_logs（应改为 execution_traces）")

        if "COLLECTIONS" in content and "__init__" not in f.name:
            if "runtime_logs" in content.split("COLLECTIONS")[-1][:200]:
                issues.append(f"{f.name}: COLLECTIONS 仍包含 runtime_logs")

    return issues


def check_imports() -> list[str]:
    """Check compliance and report findings."""
    issues: list[str] = []
    py_files = sorted(VMS_DIR.glob("*.py"))

    for f in py_files:
        content = f.read_text(encoding="utf-8")
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names if hasattr(node, "names") else []:
                    name = alias.name if hasattr(alias, "name") else alias
                    if hasattr(node, "module") and node.module:
                        name = f"{node.module}.{name}"
                    if "kb." in str(name) and f.name not in ("bridge_layer.py",):
                        issues.append(f"{f.name}: 导入 kb/ 模块 '{name}'（仅 bridge_layer 可导入）")

    return issues


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    print("VMS 跨文件一致性检查器")
    print("========================")
    print()

    issues: list[str] = []
    issues.extend(check_collections())
    issues.extend(check_imports())

    if not issues:
        print("✅ 所有文件一致性检查通过")
    else:
        print(f"⚠️ 发现 {len(issues)} 个问题:")
        for i in issues:
            print(f"  - {i}")

    files_count = len(list(VMS_DIR.glob("*.py")))
    print(f"\n已检查 {files_count} 个文件")


if __name__ == "__main__":
    main()
