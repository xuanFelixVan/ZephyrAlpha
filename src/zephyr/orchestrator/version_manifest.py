"""模块全版本管理（Version Manifest）——各系统版本号+文件路径索引。"""

from __future__ import annotations

VERSION_MANIFEST: dict[str, dict] = {
    "orchestrator": {"version": "v0.1.0", "path": "src/zephyr/orchestrator/"},
    "script_system": {"version": "v0.1.0", "path": "src/zephyr/script_system/"},
    "knowledge_base": {"version": "v0.1.0", "path": "src/zephyr/knowledge_base/"},
    "context_engine": {"version": "v0.1.0", "path": "src/zephyr/context_engine/"},
    "gate_engine": {"version": "v0.1.0", "path": "src/zephyr/gates/"},
    "pipeline": {"version": "v0.1.0", "path": "src/zephyr/pipeline/"},
    "feedback_loop": {"version": "v0.1.0", "path": "src/zephyr/feedback_loop/"},
    "vector_memory": {"version": "v0.1.0", "path": "src/zephyr/vector_memory/"},
    "database": {"version": "v0.1.0", "path": "src/zephyr/database/"},
    "llm_security": {"version": "v0.1.0", "path": "src/zephyr/llm_security/"},
    "system_telemetry": {"version": "v0.1.0", "path": "src/zephyr/telemetry/"},
    "mcp_servers": {"version": "v0.1.0", "path": "src/zephyr/mcp_servers/"},
    "shared": {"version": "v0.1.0", "path": "src/zephyr/shared/"},
    "mod_master_001": {"version": "v0.1.0", "path": "docs/03_modules/_master-blueprint/"},
}


class VersionManifest:
    def get_version(self, system: str) -> str:
        return VERSION_MANIFEST.get(system, {}).get("version", "v0.0.0")

    def get_path(self, system: str) -> str:
        return VERSION_MANIFEST.get(system, {}).get("path", "")

    def list_systems(self) -> list[str]:
        return list(VERSION_MANIFEST.keys())
