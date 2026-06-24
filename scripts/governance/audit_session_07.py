# [BLUEPRINT] MOD-INF-005 | scripts/governance/audit_session_07.py | §
# [MODULE] scripts.governance.audit_session_07
# [DOMAIN] D-GOVERNANCE
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
"""对话#07 全量产出审计脚本。

验证所有新建/修改文件的落盘状态、语法正确性、导入解析性。
"""

from __future__ import annotations

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

from _shared.constants import EXIT_FINDINGS, EXIT_PASS

ROOT = Path(__file__).resolve().parent.parent.parent

# ─── 对话#07 应产出的全部唯一文件路径 ───
EXPECTED_FILES: list[dict[str, Any]] = [
    # Card 1: 模块骨架
    {"path": "src/zephyr/mcp/__init__.py", "card": "TASK-INF-013-0001", "new": False, "check": "exports_9_classes"},
    {"path": "architecture-model/layers/b_mcp.yaml", "card": "TASK-INF-013-0001", "new": False, "check": "has_9_files"},
    {"path": "AGENTS.md", "card": "TASK-INF-013-0001", "new": False, "check": "rule_8_mcp_naming"},
    # Card 2: 错误码+帧
    {
        "path": "src/zephyr/mcp/_base_server.py",
        "card": "TASK-INF-013-0002",
        "new": False,
        "check": "content_length_frame",
    },
    {
        "path": "src/zephyr/mcp/error_codes.py",
        "card": "TASK-INF-013-0002",
        "new": True,
        "check": "all_10_codes_defined",
    },
    # Card 4: 5-server增强
    {
        "path": "src/zephyr/mcp/knowledge_base_server.py",
        "card": "TASK-INF-013-0004",
        "new": False,
        "check": "has_list_kes_tool",
    },
    {
        "path": "src/zephyr/mcp/gate_engine_server.py",
        "card": "TASK-INF-013-0004",
        "new": False,
        "check": "has_gate_5_6_cb",
    },
    {
        "path": "src/zephyr/mcp/doc_guard_server.py",
        "card": "TASK-INF-013-0004",
        "new": False,
        "check": "has_validate_doc_version",
    },
    {
        "path": "src/zephyr/mcp/sentinel_server.py",
        "card": "TASK-INF-013-0004",
        "new": False,
        "check": "has_health_status",
    },
    {
        "path": "src/zephyr/mcp/blueprint_search_server.py",
        "card": "TASK-INF-013-0004",
        "new": False,
        "check": "has_cache_refresh",
    },
    # Card 5: Gateway
    {"path": "src/zephyr/mcp/gateway_server.py", "card": "TASK-INF-013-0005", "new": True, "check": "has_5_pipeline"},
    {"path": "src/zephyr/mcp/rate_limiter.py", "card": "TASK-INF-013-0005", "new": True, "check": "has_per_tool_rl"},
    {"path": "src/zephyr/mcp/audit_logger.py", "card": "TASK-INF-013-0005", "new": True, "check": "has_log_call"},
    {"path": "config/mcp.json", "card": "TASK-INF-013-0005", "new": True, "check": "has_7_servers"},
    {"path": "tests/unit/test_mcp_gateway.py", "card": "TASK-INF-013-0005", "new": True, "check": "has_19_tests"},
    # Card 6: 集成脚本
    {"path": "scripts/mcp/start_all.py", "card": "TASK-INF-013-0008", "new": True, "check": "syntax"},
    {"path": "scripts/mcp/stop_all.py", "card": "TASK-INF-013-0008", "new": True, "check": "syntax"},
    {"path": "scripts/mcp/status_all.py", "card": "TASK-INF-013-0008", "new": True, "check": "syntax"},
    {"path": "scripts/mcp/generate_ide_config.py", "card": "TASK-INF-013-0008", "new": True, "check": "syntax"},
    {
        "path": "src/zephyr/mcp/handoff_auto_loader.py",
        "card": "TASK-INF-013-0008",
        "new": True,
        "check": "has_HandoffAutoLoader",
    },
    {
        "path": "scripts/governance/verify_file_paths.py",
        "card": "TASK-INF-013-0008",
        "new": True,
        "check": "has_EXPECTED_FILES",
    },
    {"path": ".env.example", "card": "TASK-INF-013-0008", "new": False, "check": "has_mcp_section"},
    # Card 7: 风险缓解
    {
        "path": "scripts/governance/validate_tool_contracts_consistency.py",
        "card": "TASK-INF-013-0009",
        "new": True,
        "check": "has_SERVER_MAP",
    },
    {"path": ".pre_commit-config.yaml", "card": "TASK-INF-013-0009", "new": False, "check": "has_gate_mcp_contract"},
    {
        "path": "src/zephyr/mcp/task_manager_server.py",
        "card": "TASK-INF-013-0009",
        "new": False,
        "check": "has_idempotency_cache",
    },
    # Card 8: DAG
    {"path": "scripts/mcp/launcher.py", "card": "TASK-INF-013-0014", "new": True, "check": "has_DAG_LAYERS"},
    # Card 9: 跨模块契约
    {
        "path": "tests/architecture/test_cross_module_contracts.py",
        "card": "TASK-INF-013-0020",
        "new": True,
        "check": "has_6_tests",
    },
    # Card 10: 审计报告
    {
        "path": "docs/03_modules/_cross_layer/mcp-servers/changes/MOD-INF-013/_decomposition_completeness.yaml",
        "card": "TASK-INF-013-0021",
        "new": True,
        "check": "yaml_valid",
    },
    {
        "path": "docs/03_modules/_cross_layer/mcp-servers/changes/MOD-INF-013/_audit_report.md",
        "card": "TASK-INF-013-0021",
        "new": True,
        "check": "has_conclusion",
    },
    # Card 11: Resource/Prompt/Sandbox
    {
        "path": "src/zephyr/mcp/resource_provider.py",
        "card": "TASK-INF-013-0006",
        "new": True,
        "check": "has_5_resources",
    },
    {"path": "src/zephyr/mcp/prompt_provider.py", "card": "TASK-INF-013-0006", "new": True, "check": "has_5_prompts"},
    {"path": "src/zephyr/mcp/sandbox_server.py", "card": "TASK-INF-013-0006", "new": True, "check": "has_execute_tool"},
    # Card 12: Stress/Chaos/Runbook
    {
        "path": "tests/performance/test_mcp_stress.py",
        "card": "TASK-INF-013-0007",
        "new": True,
        "check": "has_concurrent_test",
    },
    {"path": "tests/chaos/test_mcp_chaos.py", "card": "TASK-INF-013-0007", "new": True, "check": "has_5_experiments"},
    {
        "path": "docs/03_modules/_cross_layer/mcp-servers/runbook.md",
        "card": "TASK-INF-013-0007",
        "new": True,
        "check": "has_8_scenarios",
    },
    # Card 22: KB index
    {
        "path": "docs/03_modules/infrastructure_runtime_integration/knowledge-base/index.md",
        "card": "TASK-KB-0001",
        "new": True,
        "check": "has_blueprint_ref",
    },
]


def check_file(item: dict) -> dict:
    """Check compliance and report findings."""
    fp = ROOT / item["path"]
    result = {"path": item["path"], "card": item["card"], "exists": fp.exists()}

    if not fp.exists():
        result["status"] = "MISSING"
        return result

    result["size_bytes"] = fp.stat().st_size

    if item["path"].endswith(".py"):
        try:
            source = fp.read_text(encoding="utf-8")
            ast.parse(source)
            result["syntax"] = "OK"
        except SyntaxError as e:
            result["syntax"] = f"FAIL: {e}"
            result["status"] = "SYNTAX_ERROR"
            return result

    result["status"] = "OK"
    return result


def check_imports():
    """验证关键模块可导入。"""
    sys.path.insert(0, str(ROOT))
    results: dict[str, bool] = {}
    checks = [
        ("from zephyr.infrastructure._base_server import BaseMCPServer, ToolDefinition, MCPError", "base_server"),
        ("from zephyr.infrastructure.error_codes import ERR_GATE_FAILED, ERR_RBAC_DENIED", "error_codes"),
        ("from zephyr.infrastructure.rate_limiter import RateLimiter, PerToolRateLimiter", "rate_limiter"),
        ("from zephyr.infrastructure.audit_logger import AuditLogger", "audit_logger"),
        ("from zephyr.infrastructure.gateway_server import MCPGateway, create_gateway", "gateway"),
        ("from zephyr.integration.mcp.resource_provider import ResourceProvider", "resource"),
        ("from zephyr.integration.mcp.prompt_provider import PromptProvider", "prompt"),
        ("from zephyr.integration.mcp.sandbox_server import SandboxServer", "sandbox"),
        ("from zephyr.integration.mcp.handoff_auto_loader import HandoffAutoLoader", "handoff"),
    ]
    for stmt, name in checks:
        try:
            exec(stmt)
            results[name] = True
        except Exception as e:
            results[name] = False
            results[f"{name}_error"] = str(e)[:80]
    return results


def main():
    """Entry point: parse args, run logic, return exit code."""
    print("=" * 60)
    print("对话#07 全量产出审计")
    print("=" * 60)

    # 文件存在性
    print("\n── 1. 文件落盘检查 ──")
    missing = []
    ok = 0
    for item in EXPECTED_FILES:
        r = check_file(item)
        if r["status"] == "OK":
            ok += 1
            print(f"  ✅ {r['path']} ({r['size_bytes']} bytes)")
        else:
            missing.append(r)
            print(f"  ❌ {r['path']} — {r['status']}")

    total = len(EXPECTED_FILES)
    print(f"\n  结果: {ok}/{total} 文件存在且语法正确")

    # 导入验证
    print("\n── 2. 关键模块导入检查 ──")
    imports = check_imports()
    imp_ok = sum(1 for v in imports.values() if v is True)
    imp_total = len([k for k in imports if "_error" not in k])
    for name, passed in imports.items():
        if "_error" in name:
            continue
        if passed:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}: {imports.get(f'{name}_error', 'N/A')}")

    print(f"\n  结果: {imp_ok}/{imp_total} 模块可导入")

    if missing:
        print(f"\n🔴 发现 {len(missing)} 个缺失文件!")
        return EXIT_FINDINGS
    if imp_ok < imp_total:
        print(f"\n🔴 发现 {imp_total - imp_ok} 个导入失败!")
        return EXIT_FINDINGS
    print("\n🟢 全部通过!")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
