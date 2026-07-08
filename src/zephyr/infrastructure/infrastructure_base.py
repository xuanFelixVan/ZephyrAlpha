# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.infrastructure_base
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_infrastructure_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: infra_ops
# category: infrastructure_interface
# status: active
# created: "2026-05-05"
# ---

"""
基础设施 — Infrastructure Layer Skeleton

基础设施层抽象基类。定义系统初始化、配置管理、熔断控制的核心接口。

OCP 扩展点：
  - InfrastructureManagerBase  — 系统初始化编排
  - ConfigManagerBase           — 配置来源/验证/热重载
  - KillSwitchManagerBase       — 熔断控制策略

依赖方向：基础设施 -> D_DATA(data) / D_FACTOR~实验(all via CTR-P1-010)
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar


@dataclass(frozen=True)
class SystemHealth:
    """系统健康状态快照"""

    is_healthy: bool
    checks: dict[str, bool] = field(default_factory=dict)
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


class InfrastructureManagerBase(abc.ABC):
    """系统基础设施管理器（OCP 扩展点）

    实现者要求：
      - initialize(): 按依赖序初始化子系统（config -> db -> kb -> gates -> pipeline）
      - health(): 返回 SystemHealth 快照
      - shutdown(): 优雅关闭所有子系统
    """

    @abc.abstractmethod
    def initialize(self) -> bool:
        """初始化基础设施栈，返回是否全部成功"""
        ...

    @abc.abstractmethod
    def health(self) -> SystemHealth:
        """返回系统健康状态"""
        ...

    @abc.abstractmethod
    def shutdown(self) -> None:
        """优雅关闭所有子系统"""
        ...


class ConfigManagerBase(abc.ABC):
    """配置管理器（OCP 扩展点）

    实现者要求：
      - load(source): 从文件/环境/远程加载配置
      - validate(config): 校验配置合法性
      - reload(): 热重载（不重启进程）
    """

    _registry: ClassVar[dict[str, type[ConfigManagerBase]]] = {}

    @abc.abstractmethod
    def load(self, source: str | None = None) -> dict[str, Any]:
        """加载配置，返回 flat 配置字典"""
        ...

    @abc.abstractmethod
    def validate(self, config: dict[str, Any]) -> bool:
        """校验配置合法性"""
        ...

    def reload(self) -> dict[str, Any]:
        """热重载配置（默认调用 load 并 validate）"""
        config = self.load()
        if not self.validate(config):
            raise ValueError("Reloaded config failed validation")
        return config


class KillSwitchManagerBase(abc.ABC):
    """熔断管理器（OCP 扩展点）

    实现者要求：
      - trigger(reason, scope): 触发熔断，暂停指定范围的交易
      - reset(confirmation): 人工确认后重置
      - is_active(): 查询当前熔断状态

    INV-001: 熔断延迟 < 1ms（硬件级 T0/T1 实现）
    """

    _registry: ClassVar[dict[str, type[KillSwitchManagerBase]]] = {}

    @abc.abstractmethod
    def trigger(self, reason: str, scope: str = "all") -> bool:
        """触发熔断，返回是否成功触发"""
        ...

    @abc.abstractmethod
    def reset(self, confirmation: str) -> bool:
        """重置熔断（需人工确认 token）"""
        ...

    @abc.abstractmethod
    def is_active(self) -> bool:
        """查询当前熔断是否激活中"""
        ...

    @abc.abstractmethod
    def latency_us(self) -> float:
        """返回最后一次触发的回路延迟（微秒）——用于 INV-001 验证"""
        ...


__all__ = [
    "ConfigManagerBase",
    "InfrastructureManagerBase",
    "KillSwitchManagerBase",
    "SystemHealth",
]
