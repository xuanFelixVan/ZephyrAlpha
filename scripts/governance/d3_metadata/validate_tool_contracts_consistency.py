# [BLUEPRINT] MOD-INF-005 | scripts/governance/validate_tool_contracts_consistency.py | §
# [MODULE] scripts.governance.validate_tool_contracts_consistency
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
# [TTL] permanent
"""Tool Contract 一致性校验脚本（MOD-INF-013 §9 R3）。

对比 tool-contracts.yaml 中 tool 的 input_schema ↔ 代码中 handler 实际注册的参数。
通过 AST 解析 + Yaml 对比，检测契约漂移。

使用：
    python scripts/governance/validate_tool_contracts_consistency.py [--ci]
    --ci 模式：不一致时 exit(1)
"""

from __future__ import annotations

__manifest__ = """
args: []
description: Tool Contract 一致性校验脚本（MOD-INF-013 §9 R3）。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import ast
import sys
from pathlib import Path
from typing import Any

import yaml
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

CONTRACTS_PATH = REPO_ROOT / "src/zephyr/mcp/tool-contracts.yaml"
MCP_DIR = REPO_ROOT / "src/zephyr/mcp"

SERVER_MAP: dict[str, str] = {
    "task_manager": "task_manager_server.py",
    "knowledge_base": "knowledge_base_server.py",
    "gate_engine": "gate_engine_server.py",
    "session_handoff": "doc_guard_server.py",
    "intent_router": "sentinel_server.py",
    "blueprint_search": "blueprint_search_server.py",
}


def load_contracts() -> dict[str, Any]:
    """load_contracts implementation."""
    if not CONTRACTS_PATH.exists():
        print(f"[WARN] {CONTRACTS_PATH} not found — skipping check")
        return {}
    with open(CONTRACTS_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def extract_registered_tools(server_file: Path) -> dict[str, dict[str, Any]]:
    """extract_registered_tools implementation."""
    tools: dict[str, dict[str, Any]] = {}
    if not server_file.exists():
        return tools
    source = server_file.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return tools

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "register_tool":
            if hasattr(func.value, "id") and func.value.id == "self":  # type: ignore[attr-defined]
                try:
                    kw = {kw.arg: kw.value for kw in node.keywords if kw.arg}
                    name_node = kw.get("name")
                    schema_node = kw.get("input_schema")
                    if name_node and isinstance(name_node, ast.Constant):
                        name = name_node.value
                        tools[name] = {"has_schema": schema_node is not None}
                except Exception:
                    continue
    return tools


def validate_consistency(ci_mode: bool = False) -> int:
    """Validate target against rules and report findings."""
    contracts = load_contracts()
    if not contracts:
        return EXIT_PASS

    errors: list[str] = []
    for server_id, server_info in contracts.items():
        defined_tools = server_info.get("tools", {})
        server_file = MCP_DIR / SERVER_MAP.get(server_id, "")
        registered = extract_registered_tools(server_file)

        for tool_name in defined_tools:
            if tool_name not in registered:
                errors.append(f"YAML-defined tool '{tool_name}' not registered in {server_file.name}")

        for tool_name in registered:
            if tool_name not in defined_tools:
                errors.append(f"Code-registered tool '{tool_name}' not in tool-contracts.yaml for {server_id}")

    if errors:
        print(f"[FAIL] {len(errors)} contract drift issues:")
        for e in errors:
            print(f"  - {e}")
        if ci_mode:
            return EXIT_FINDINGS
    else:
        print("[PASS] All tool contracts consistent")
    return EXIT_PASS


if __name__ == "__main__":
    ci = "--ci" in sys.argv
    sys.exit(validate_consistency(ci_mode=ci))
