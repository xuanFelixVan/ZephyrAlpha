# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §4
# [MODULE] zephyr.shared.contracts.skill_protocol
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.mcp_servers; zephyr.governance.agent_spec; zephyr.infrastructure.rollback
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Protocol MUST NOT import from zephyr.trading; only structural subtyping
# [MODIFY-GUARD] shared/contracts/__init__.py; all consumers of SkillLoader/SkillRouter
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError when orchestration layer unavailable; consumers MUST handle
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: registry_path 参数
#   fields: 参数 registry_path，类型注解 Path | None
#   code: skill_protocol.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SkillLoaderProtocol
#   name_en: SkillLoaderProtocol
#   intro: Skill加载器协议——解耦D-INFRA/D-GOV对D-ORCH的直接依赖。
#   desc: Skill加载器协议——解耦D-INFRA/D-GOV对D-ORCH的直接依赖。；公共方法（定义序）: list_skills, load, progressive_load, progressive_load_ful…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② SkillRouterProtocol
#   name_en: SkillRouterProtocol
#   intro: Skill路由协议——解耦D-GOV对D-ORCH的直接依赖。
#   desc: Skill路由协议——解耦D-GOV对D-ORCH的直接依赖。；公共方法（定义序）: route, list_registered_skills；源码 L104-L109
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ create_skill_loader
#   name_en: create_skill_loader
#   intro: 延迟导入并创建SkillLoader实例。
#   desc: 延迟导入并创建SkillLoader实例。；源码 L112-L116
#   inputs: registry_path
#   outputs: SkillLoaderProtocol
# - id: A4
#   name_zh: ④ create_skill_router
#   name_en: create_skill_router
#   intro: 延迟导入并创建SkillRouter实例。
#   desc: 延迟导入并创建SkillRouter实例。；源码 L119-L123
#   inputs: registry_path
#   outputs: SkillRouterProtocol
# 层: 输出
# - id: O1
#   name_zh: SkillLoaderProtocol
#   name_en: SkillLoaderProtocol
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.infrastructure.mcp_servers; zephyr.governance.agent_spec; zephyr.infrast…
# - id: O2
#   name_zh: SkillRouterProtocol
#   name_en: SkillRouterProtocol
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.infrastructure.mcp_servers; zephyr.governance.agent_spec; zephyr.infrast…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class SkillLoaderProtocol(Protocol):
    """Skill加载器协议——解耦D-INFRA/D-GOV对D-ORCH的直接依赖。"""

    def list_skills(self) -> list[Any]: ...

    def load(self, skill_id: str) -> object | None: ...

    def progressive_load(self, skill_id: str) -> dict[str, Any]: ...

    def progressive_load_full(self, skill_id: str) -> dict[str, Any]: ...

    def load_l0(self) -> dict[str, Any]: ...

    def load_l3_reference(self, skill_id: str, ref_name: str) -> str: ...

    def check_token_budget(self, domain_skill_id: str, role_skill_id: str) -> dict[str, Any]: ...


@runtime_checkable
class SkillRouterProtocol(Protocol):
    """Skill路由协议——解耦D-GOV对D-ORCH的直接依赖。"""

    def route(self, stage: str, task_description: str) -> tuple[str, str | None]: ...

    def list_registered_skills(self) -> dict[str, dict[str, str]]: ...


def create_skill_loader(registry_path: Path | None = None) -> SkillLoaderProtocol:
    """延迟导入并创建SkillLoader实例。"""
    _mod = importlib.import_module("zephyr.autonomy_core.skills.skill_loader")
    _SkillLoader = _mod.SkillLoader
    return _SkillLoader(registry_path=registry_path)


def create_skill_router(registry_path: Path | None = None) -> SkillRouterProtocol:
    """延迟导入并创建SkillRouter实例。"""
    _mod = importlib.import_module("zephyr.autonomy_core.skills.skill_router")
    _SkillRouter = _mod.SkillRouter
    return _SkillRouter(registry_path=registry_path)
