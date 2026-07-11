from typing import Final

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.governance.version_manifest
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_version_manifest | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""模块全版本管理（Version Manifest）——各系统版本号+文件路径索引。"""

VERSION_MANIFEST: Final[dict[str, dict]] = {
    "orchestrator": {"version": "v0.1.0", "path": "src/zephyr/orchestrator/"},
    "script_system": {"version": "v0.1.0", "path": "src/zephyr/script_system/"},
    "knowledge_base": {"version": "v0.1.0", "path": "src/zephyr/knowledge_base/"},
    "context-engine": {"version": "v0.1.0", "path": "src/zephyr/context-engine/"},
    "gate_engine": {"version": "v0.1.0", "path": "src/zephyr/governance/rule_enforcement/"},
    "pipeline": {"version": "v0.1.0", "path": "src/zephyr/pipeline/"},
    "feedback-loop": {"version": "v0.1.0", "path": "src/zephyr/feedback-loop/"},
    "vector-memory": {"version": "v0.1.0", "path": "src/zephyr/vector-memory/"},
    "database": {"version": "v0.1.0", "path": "src/zephyr/database/"},
    "llm-security": {"version": "v0.1.0", "path": "src/zephyr/llm-security/"},
    "system-telemetry": {"version": "v0.1.0", "path": "src/zephyr/telemetry/"},
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
