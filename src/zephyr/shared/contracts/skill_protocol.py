# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §4
# [MODULE] zephyr.shared.contracts.skill_protocol
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.mcp_servers; zephyr.governance.agent_spec; zephyr.infrastructure.rollback
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Protocol MUST NOT import from zephyr.trading; only structural subtyping
# [MODIFY-GUARD] shared/contracts/__init__.py; all consumers of SkillLoader/SkillRouter
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError when orchestration layer unavailable; consumers MUST handle
# [TESTS]
# [A_module] module_id=MOD-SHR_skill_protocol | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
