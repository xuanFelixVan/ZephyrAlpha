# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.foundation.flags
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors
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
# [A_module] module_id=MOD-SHR_flags | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from typing import Self

"""
flags.py —— Feature Flag / 功能开关系统（Phase 2 新增 | 盲点 B7 修复）

痛点修复：100% AI 施工 + 1人+AI 维护下，没有开关控制 AI 的行为——
  1. AI 改了不该改的功能——无法紧急关闭
  2. 新功能灰度上线——无法仅对特定模块/用户开启
  3. 回滚依赖 full git revert——太重了

设计对标：
  - Google //shared/flags (Guava FeatureFlag)
  - LaunchDarkly / Unleash 的配置驱动模式
  - K8s feature gates（alpha → beta → GA 渐进式启用）

设计原则：
  - 配置驱动（YAML/JSON）——不改代码就能开关功能
  - 三态：ALWAYS_ON / CONDITIONAL / ALWAYS_OFF
  - 支持按 module_id / agent_id 粒度控制
  - 默认安全：新 flag 默认为 OFF（AI 新增的功能不自动打开）

AI 施工约定：
  - 所有实验性功能 MUST 通过 FeatureFlag 守护
  - AI 新加功能时 MUST 创建对应 flag（初始 OFF）
  - 运维在 config/ 中启用 flag 后才生效
  - 禁止 AI 自行修改 flag 状态——那是人工运维的权限

SSoT: MOD-INF-016 §2.8 shared-feature-flags
Version: 0.1.0
"""


import logging
from dataclasses import dataclass, field
from enum import Enum, unique

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "FeatureFlag",
    "FlagNotFoundError",
    "FlagRegistry",
    "FlagState",
    "global_flag_registry",
]

logger = logging.getLogger(__name__)


@unique
class FlagState(str, Enum):
    ALWAYS_ON = "ALWAYS_ON"
    CONDITIONAL = "CONDITIONAL"
    ALWAYS_OFF = "ALWAYS_OFF"


class FlagNotFoundError(ZephyrBaseError):
    """请求的 FeatureFlag 未在注册表中找到。"""


@dataclass(frozen=True)
class FeatureFlag:
    key: str
    state: FlagState = FlagState.ALWAYS_OFF
    description: str = ""
    allowed_modules: list[str] = field(default_factory=list)
    allowed_agents: list[str] = field(default_factory=list)
    rollout_pct: int = 0

    def is_enabled(
        self,
        *,
        module_id: str | None = None,
        agent_id: str | None = None,
    ) -> bool:
        if self.state is FlagState.ALWAYS_ON:
            return True
        if self.state is FlagState.ALWAYS_OFF:
            return False

        if self.allowed_modules and module_id:
            if module_id not in self.allowed_modules:
                return False

        if self.allowed_agents and agent_id:
            if agent_id not in self.allowed_agents:
                return False

        if self.rollout_pct > 0 and module_id:
            import hashlib

            bucket = int(hashlib.md5(module_id.encode()).hexdigest(), 16) % 100
            return bucket < self.rollout_pct

        return self.state is FlagState.CONDITIONAL


class FlagRegistry:
    """全局 FeatureFlag 注册表（单例）。

    Usage::

        registry = FlagRegistry()
        registry.register(FeatureFlag("use_gpt4o", FlagState.ALWAYS_OFF,
                                       description="启用 GPT-4o 替代 GPT-4o-mini"))

        if registry.is_enabled("use_gpt4o", module_id="MOD-CONTEXT_ENGINE"):
            model = "gpt-4o"
        else:
            model = "gpt-4o-mini"
    """

    def __init__(self) -> None:
        self._flags: dict[str, FeatureFlag] = {}

    def register(self, flag: FeatureFlag) -> None:
        self._flags[flag.key] = flag
        logger.info("feature flag registered: %s (state=%s)", flag.key, flag.state.value)

    def unregister(self, key: str) -> None:
        self._flags.pop(key, None)

    def get(self, key: str) -> FeatureFlag:
        flag = self._flags.get(key)
        if flag is None:
            raise FlagNotFoundError(
                f"FeatureFlag '{key}' not found in registry",
                details={"key": key},
            )
        return flag

    def is_enabled(
        self,
        key: str,
        *,
        module_id: str | None = None,
        agent_id: str | None = None,
    ) -> bool:
        flag = self.get(key)
        return flag.is_enabled(module_id=module_id, agent_id=agent_id)

    def list_all(self) -> dict[str, FeatureFlag]:
        return dict(self._flags)

    def reset(self) -> None:
        self._flags.clear()


global_flag_registry = FlagRegistry()
