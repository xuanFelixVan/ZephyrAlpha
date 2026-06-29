# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.ops.observability.health
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.shared.lifecycle.hooks
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
# [A_module] module_id=MOD-SHR_health | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
health.py —— ZephyrAlpha 聚合健康检查

Phase 6 新增（盲点 B9）——解决 LifecycleManager 虽有单模块健康但
无整体视图的问题。运维需要一瞥即知系统整体状态。

设计原则：
  - 聚合所有 LifecycleAware 模块的健康状态
  - 生成 summary（ALL_HEALTHY / DEGRADED / UNHEALTHY / UNKNOWN）
  - 支持 JSON 可序列化输出——可直接暴露为 /health endpoint
  - 零侵入——不修改 LifecycleManager，在其 health_check_all() 之上构建

对标：
  - Spring Boot Actuator /health: aggregated health with status + details
  - Kubernetes pod conditions: Ready/Healthy/Degraded
  - AWS ELB health check: path + expected status code

SSoT: MOD-INF-016 §2.16 shared-health
Version: 0.1.0
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, unique
from typing import Any

from zephyr.shared.lifecycle.hooks import (
    LifecycleAware,
    LifecycleManager,
    LifecycleState,
    ModuleHealth,
)

__all__ = [
    "AggregateHealth",
    "HealthStatus",
    "HealthSummary",
    "collect_health",
]


@unique
class HealthStatus(str, Enum):
    ALL_HEALTHY = "ALL_HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


@dataclass
class HealthSummary:
    status: HealthStatus
    total_modules: int = 0
    healthy_count: int = 0
    unhealthy_count: int = 0
    degraded_count: int = 0
    failed_count: int = 0
    checked_at: str = ""
    details: list[ModuleHealth] = field(default_factory=list)
    unhealthy_modules: list[str] = field(default_factory=list)
    degraded_modules: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "total_modules": self.total_modules,
            "healthy_count": self.healthy_count,
            "unhealthy_count": self.unhealthy_count,
            "degraded_count": self.degraded_count,
            "failed_count": self.failed_count,
            "checked_at": self.checked_at,
            "unhealthy_modules": self.unhealthy_modules,
            "degraded_modules": self.degraded_modules,
            "details": [
                {
                    "module_name": d.module_name,
                    "state": d.state.value,
                    "healthy": d.healthy,
                    "message": d.message,
                    "details": d.details,
                }
                for d in self.details
            ],
        }


def _derive_summary(health_map: dict[str, ModuleHealth]) -> Self:
    healthy_count = 0
    unhealthy_count = 0
    degraded_count = 0
    failed_count = 0
    unhealthy_modules: list[str] = []
    degraded_modules: list[str] = []
    details: list[ModuleHealth] = []

    for mod_health in health_map.values():
        details.append(mod_health)
        if mod_health.state == LifecycleState.FAILED:
            failed_count += 1
            unhealthy_count += 1
            unhealthy_modules.append(mod_health.module_name)
        elif mod_health.state == LifecycleState.DEGRADED:
            degraded_count += 1
            degraded_modules.append(mod_health.module_name)
        elif not mod_health.healthy:
            unhealthy_count += 1
            unhealthy_modules.append(mod_health.module_name)
        else:
            healthy_count += 1

    total = len(health_map)

    if total == 0:
        status = HealthStatus.UNKNOWN
    elif unhealthy_count > 0:
        status = HealthStatus.UNHEALTHY
    elif degraded_count > 0:
        status = HealthStatus.DEGRADED
    else:
        status = HealthStatus.ALL_HEALTHY

    return HealthSummary(
        status=status,
        total_modules=total,
        healthy_count=healthy_count,
        unhealthy_count=unhealthy_count,
        degraded_count=degraded_count,
        failed_count=failed_count,
        checked_at=datetime.now(UTC).isoformat(),
        details=details,
        unhealthy_modules=unhealthy_modules,
        degraded_modules=degraded_modules,
    )


class AggregateHealth:
    """聚合所有 LifecycleAware 模块的健康状态。

    Usage:
        agg = AggregateHealth(lifecycle_manager)
        summary = await agg.check()
        print(summary.status)           # HealthStatus.ALL_HEALTHY
        print(summary.unhealthy_modules)  # []
        json_output = summary.to_dict() # 可直接序列化

        # 或者只检查特定模块:
        summary = await agg.check(module_names=["db", "context-engine"])
    """

    def __init__(self, lifecycle_manager: LifecycleManager) -> None:
        self._mgr = lifecycle_manager

    async def check(
        self,
        *,
        module_names: list[str] | None = None,
        timeout: float = 5.0,
    ) -> Self:
        """执行聚合健康检查。

        Args:
            module_names: 要检查的模块名列表。None = 检查全部
            timeout: 每个模块健康检查的超时时间（秒）

        Returns:
            HealthSummary——聚合后的健康状态
        """
        modules = self._mgr.modules

        if module_names:
            name_set = set(module_names)
            modules = [m for m in modules if m.module_name in name_set]

        if not modules:
            return _derive_summary({})

        async def _check_one(module: LifecycleAware) -> tuple[str, ModuleHealth]:
            try:
                result = await asyncio.wait_for(module.health_check(), timeout=timeout)
                return (module.module_name, result)
            except TimeoutError:
                return (
                    module.module_name,
                    ModuleHealth(
                        module_name=module.module_name,
                        state=LifecycleState.DEGRADED,
                        healthy=False,
                        message=f"Health check timed out after {timeout}s",
                    ),
                )
            except Exception as exc:
                return (
                    module.module_name,
                    ModuleHealth(
                        module_name=module.module_name,
                        state=LifecycleState.FAILED,
                        healthy=False,
                        message=str(exc),
                    ),
                )

        tasks = [_check_one(m) for m in modules]
        results = await asyncio.gather(*tasks)
        health_map = dict(results)
        return _derive_summary(health_map)

    async def check_block_fast(
        self,
        *,
        timeout: float = 2.0,
    ) -> Self:
        """快速聚合检查——更短超时。

        Args:
            timeout: 超时时间（默认 2 秒）

        Returns:
            HealthSummary
        """
        return await self.check(timeout=timeout)


async def collect_health(
    modules: list[LifecycleAware],
    *,
    timeout: float = 5.0,
) -> Self:
    """便利函数——从模块列表直接收集聚合健康状态。

    Args:
        modules: LifecycleAware 模块列表
        timeout: 每个模块的超时时间

    Returns:
        HealthSummary
    """
    dummy_mgr = LifecycleManager()
    for m in modules:
        dummy_mgr.register(m)
    agg = AggregateHealth(dummy_mgr)
    return await agg.check(timeout=timeout)
