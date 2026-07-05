# [A_module] module_id=MOD-INF_capacity_assurance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
ZephyrAlpha 容量保障体系 (Capacity Assurance) — MOD-INF-001 · 基础设施 Infrastructure.

六大核心能力 (Six Core Capabilities):
  1. SSoT Validation        — 单一事实源校验，蓝图与实现一致性守护
  2. Capacity SLO + Error Budget   — 容量 SLO 定义与 Error Budget 五级响应 (L0~BLACK)
  3. AI Audit Guard (Provenance Chain) — AI 修改全量溯源，不可篡改审计链
  4. Multi-level Token Budget — 四级令牌预算 (Global→Module→Agent→Model) 驱动施工速率
  5. Kill Switch + Sandbox  — 全局熔断 + 高风险操作沙箱隔离
  6. Graceful Degradation   — 模型降级链 + 自动回升 + 渐进式自治

设计约束 (Design Constraints):
  1. 所有设计按 1500 模块极限容量考虑
  2. 零依赖优先：Python stdlib + SQLite 完成的不引入新依赖
  3. 免费优先：Trae CN 免费模型优先
  4. 保留多进程/分布式事件总线/数据库分片扩展口子
  5. 单进程极限 500 模块，超过则启用多进程/分布式扩展

Version: 2.6.0
Module ID: MOD-INF-001
Source: docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
"""

version = "2.6.0"
module_id = "MOD-INF-001"

_SUBMODULES = [
    "contracts",
    "cross_module_integration",
    "risk_mitigation",
    "schema",
    "sli_instrumentation",
    "tech_stack",
]


def __getattr__(name: str):
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(f"zephyr.infrastructure.capacity_assurance.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "contracts",
    "cross_module_integration",
    "module_id",
    "risk_mitigation",
    "schema",
    "sli_instrumentation",
    "tech_stack",
    "version",
'budget_forecaster', 'host_resource_governor', 'kill_switch', 'token_budget']
