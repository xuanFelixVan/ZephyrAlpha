# [A_test] module_id: SRC-TST-0063 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-221 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.architecture.test_cross_module_contracts
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""跨模块契约一致性测试（MOD-INF-013 §7）。

验证 MCP 模块的 depends_on 依赖可达性 + 契约三方一致性。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml
from zephyr.shared.io.paths import REPO_ROOT


REQUIRED_DEPENDENCIES = [
    "MOD-INF-039",
    "MOD-KB-001",
    "MOD-GATE_ENGINE",
    "MOD-INF-018",
]

MCP_BLUEPRINT = REPO_ROOT / "docs/03_modules/_cross_layer/mcp-servers/blueprint.md"
B_MCP_YAML = REPO_ROOT / "architecture_model/layers/b_mcp.yaml"
TOOL_CONTRACTS = REPO_ROOT / "src/zephyr/mcp/tool-contracts.yaml"


def _read_frontmatter(path: Path) -> dict:
    if not path.exists():
        return {}
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    return yaml.safe_load(content[3:end]) or {}


class TestUpstreamDependencyReachability:
    """上游依赖可达性验证。"""

    def test_blueprint_depends_on_present(self):
        fm = _read_frontmatter(MCP_BLUEPRINT)
        depends = fm.get("depends_on", [])
        assert len(depends) >= 4, f"depends_on should have >=4 entries, got {len(depends)}"

    def test_depends_on_ids_valid(self):
        fm = _read_frontmatter(MCP_BLUEPRINT)
        depends = fm.get("depends_on", [])
        if isinstance(depends, list) and all(isinstance(d, str) for d in depends):
            ids = depends
        elif isinstance(depends, list):
            ids = [d.get("module_id", d.get("id", str(d))) for d in depends if isinstance(d, dict)]
        else:
            ids = []
        for req in ["MOD-INF-039", "MOD-KB-001", "MOD-GATE_ENGINE"]:
            found = any(req in str(i) for i in ids)
            assert found, f"Missing upstream dependency: {req}"

    def test_b_mcp_yaml_exists_and_valid(self):
        assert B_MCP_YAML.exists(), "b_mcp.yaml must exist"
        with open(B_MCP_YAML, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        assert "modules" in data or "partition" in data
        if "modules" in data:
            modules = data["modules"]
            for mod in modules:
                assert "files" in mod or "id" in mod

    def test_tool_contracts_yaml_valid(self):
        assert TOOL_CONTRACTS.exists(), "tool-contracts.yaml must exist"
        with open(TOOL_CONTRACTS, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        assert isinstance(data, dict), "tool-contracts.yaml must be a dict"
        expected_servers = [
            "task_manager",
            "knowledge_base",
            "gate_engine",
            "session_handoff",
            "intent_router",
            "blueprint_search",
        ]
        for s in expected_servers:
            assert s in data, f"Missing server in tool-contracts.yaml: {s}"

    def test_b_mcp_all_servers_listed(self):
        with open(B_MCP_YAML, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        modules = data.get("modules", [])
        all_files: list[str] = []
        for mod in modules:
            all_files.extend(mod.get("files", []))
        expected = [
            "_base_server.py",
            "blueprint_search_server.py",
            "doc_guard_server.py",
            "gate_engine_server.py",
            "knowledge_base_server.py",
            "sandbox_server.py",
            "sentinel_server.py",
            "task_manager_server.py",
            "tool-contracts.yaml",
        ]
        for f in expected:
            assert f in all_files, f"b_mcp.yaml missing file: {f}"

    def test_all_server_files_exist_on_disk(self):
        server_files = [
            "_base_server.py",
            "blueprint_search_server.py",
            "doc_guard_server.py",
            "gate_engine_server.py",
            "knowledge_base_server.py",
            "sentinel_server.py",
            "task_manager_server.py",
            "error_codes.py",
            "rate_limiter.py",
            "audit_logger.py",
            "gateway_server.py",
            "handoff_auto_loader.py",
            "__init__.py",
            "tool-contracts.yaml",
        ]
        mcp_dir = REPO_ROOT / "src/zephyr/mcp"
        for f in server_files:
            fp = mcp_dir / f
            assert fp.exists(), f"Missing MCP file: {f}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
