# [BLUEPRINT] MOD-INF-005 | scripts/governance/verify_file_paths.py | §
"""代码路径索引验证脚本（MOD-INF-013 §5 governance）。"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

EXPECTED_FILES: list[str] = [
    # §5.1 源码文件
    "src/zephyr/mcp/_base_server.py",
    "src/zephyr/mcp/error_codes.py",
    "src/zephyr/mcp/__init__.py",
    "src/zephyr/mcp/task_manager_server.py",
    "src/zephyr/mcp/knowledge_base_server.py",
    "src/zephyr/mcp/gate_engine_server.py",
    "src/zephyr/mcp/doc_guard_server.py",
    "src/zephyr/mcp/sentinel_server.py",
    "src/zephyr/mcp/blueprint_search_server.py",
    "src/zephyr/mcp/gateway_server.py",
    "src/zephyr/mcp/rate_limiter.py",
    "src/zephyr/mcp/audit_logger.py",
    "src/zephyr/mcp/handoff_auto_loader.py",
    "src/zephyr/mcp/tool-contracts.yaml",
    # §5.2 测试文件
    "tests/unit/test_mcp_servers.py",
    "tests/unit/test_task_manager_mcp.py",
    "tests/unit/test_mcp_gateway.py",
    # §5.3 脚本 + 配置
    "scripts/mcp/start_all.py",
    "scripts/mcp/stop_all.py",
    "scripts/mcp/status_all.py",
    "scripts/mcp/generate_ide_config.py",
    "scripts/governance/verify_file_paths.py",
    "config/mcp.json",
    "config/blueprint_routing.yaml",
    # 集成依赖
    "src/zephyr/shared/SHARED-QUICKREF.yml",
    "AGENTS.md",
    "pyproject.toml",
    "requirements.txt",
    ".env.example",
    "docker-compose.yml",
    ".pre_commit-config.yaml",
    "docs/01_policies_and_standards/governance/ai/ai-autonomy-authority-registry.md",
    "architecture-model/layers/b_mcp.yaml",
    "docs/03_modules/_cross_layer/mcp-servers/blueprint.md",
]


def verify() -> dict[str, list[str]]:
    """verify implementation."""
    found: list[str] = []
    missing: list[str] = []
    for rel in EXPECTED_FILES:
        fp = REPO_ROOT / rel
        if fp.exists():
            found.append(rel)
        else:
            missing.append(rel)
    return {"found": found, "missing": missing}


if __name__ == "__main__":
    result = verify()
    found = result["found"]
    missing = result["missing"]

    print(f"Found: {len(found)}/{len(EXPECTED_FILES)}")
    if missing:
        print(f"MISSING ({len(missing)}):")
        for m in missing:
            print(f"  [MISSING] {m}")
    else:
        print("All paths verified - PASS")
    sys.exit(0 if not missing else 1)
