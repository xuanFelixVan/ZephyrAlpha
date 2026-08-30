"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: version_manifest.py
# 层: 算法
# - id: A1
#   name_zh: ① VersionManifest
#   name_en: VersionManifest
#   intro: class VersionManifest 源码 L69-L77
#   desc: 公共方法（定义序）: get_version, get_path, list_systems；源码 L69-L77
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: VersionManifest
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.governance.version_manifest
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""模块全版本管理（Version Manifest）——各系统版本号+文件路径索引。"""

VERSION_MANIFEST: Final[dict[str, dict]] = {
    "orchestrator": {"version": "v0.1.0", "path": "src/zephyr/orchestrator/"},
    "script_system": {"version": "v0.1.0", "path": "src/zephyr/script_system/"},
    "context-engine": {"version": "v0.1.0", "path": "src/zephyr/context-engine/"},
    "gate_engine": {"version": "v0.1.0", "path": "src/zephyr/gov_enforcement/rule_enforcement/"},
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
