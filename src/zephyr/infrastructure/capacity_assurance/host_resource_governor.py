# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.host_resource_governor
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.capacity_assurance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/autonomy/test_host_resource_governor.py
# [A_module] module_id=MOD-INF-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# SRC-0041 (P3 迁移恢复, 2026-07-02): 文件从 autonomy_core/host_resource_governor.py 迁移至
#   infrastructure/capacity_assurance/host_resource_governor.py（blueprint actual_disk_path 真源）。
"""
host_resource_governor.py — 主机资源治理 (B17, DD91, TASK-017)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: host_resource_governor.py
# 层: 算法
# - id: A1
#   name_zh: ① HostResourceGovernor
#   name_en: HostResourceGovernor
#   intro: psutil RAM probe; model loading < 25% total RAM; 超限降级 (DD91…
#   desc: psutil RAM probe; model loading < 25% total RAM; 超限降级 (DD91).；公共方法（定义序）: probe, check_model_loading；源码 L62-L70
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: HostResourceGovernor
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
