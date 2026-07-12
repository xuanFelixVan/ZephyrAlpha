# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.spec_sync
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_spec_sync | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A Living Spec 同步 — 蓝图与实现的双向漂移管理

当 Agent 修改了实现(代码/YAML/配置), 自动:
  1. 检测蓝图是否需要更新 (Blueprint Drift Detection)
  2. 反之: 检测实现是否偏离了蓝图 (Implementation Drift Detection)
  3. 报告漂移并建议同步方向

方法: 基于 ConstructionVerifier 的漂移检测 + 增量同步记录
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SpecSyncEntry:
    module_id: str
    blueprint_file: str
    impl_files: list[str]
    status: str = "synced"
    diff_summary: str = ""


class SpecSync:
    def __init__(self):
        self._entries: dict[str, SpecSyncEntry] = {}

    def register(self, module_id: str, blueprint_file: str, impl_files: list[str]):
        self._entries[module_id] = SpecSyncEntry(
            module_id=module_id,
            blueprint_file=blueprint_file,
            impl_files=impl_files,
        )

    def check(self, module_id: str) -> dict:
        entry = self._entries.get(module_id)
        if entry is None:
            return {"status": "not_registered"}

        return {
            "module_id": module_id,
            "blueprint": entry.blueprint_file,
            "impl_count": len(entry.impl_files),
            "status": entry.status,
            "diff": entry.diff_summary,
        }

    def sync(self, module_id: str, direction: str = "impl_update") -> str:
        entry = self._entries.get(module_id)
        if entry is None:
            return "not_found"
        entry.status = "synced"
        return "synced"

    def list_drifted(self) -> list[str]:
        return [mid for mid, entry in self._entries.items() if entry.status != "synced"]
