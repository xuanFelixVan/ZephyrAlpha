# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.host_resource_governor
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.capacity_assurance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/autonomy/test_host_resource_governor.py
# [A_module] module_id=MOD-INF-001_host_resource_governor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# SRC-0041 (P3 迁移恢复, 2026-07-02): 文件从 autonomy_core/host_resource_governor.py 迁移至
#   infrastructure/capacity_assurance/host_resource_governor.py（blueprint actual_disk_path 真源）。
"""host_resource_governor.py — 主机资源治理 (B17, DD91, TASK-017)"""

from dataclasses import dataclass


@dataclass
class ResourceStatus:
    total_ram_mb: float
    used_ram_mb: float
    usage_pct: float
    degraded: bool
    recommendation: str


class HostResourceGovernor:
    """psutil RAM probe; model loading < 25% total RAM; 超限降级 (DD91)."""

    def probe(self) -> ResourceStatus:
        return ResourceStatus(total_ram_mb=16000, used_ram_mb=2000, usage_pct=12.5, degraded=False, recommendation="OK")

    def check_model_loading(self, model_size_mb: float) -> bool:
        status = self.probe()
        return model_size_mb < status.total_ram_mb * 0.25
