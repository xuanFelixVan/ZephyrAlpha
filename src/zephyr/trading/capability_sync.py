# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.capability_sync
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS] zephyr.trading.auto_runtime_core
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] sync_a2a and sync_skills are idempotent; existing cap_ids are skipped
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] returns int (count synced); never raises; logs on failure
# [TESTS]
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: registry 参数
#   fields: 参数 registry（无注解）
#   code: capability_sync.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CapabilitySync
#   name_en: CapabilitySync
#   intro: class CapabilitySync 源码 L86-L162
#   desc: 公共方法（定义序）: registry, sync_a2a, sync_skills；源码 L86-L162
#   inputs: registry
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: CapabilitySync
#   downstream: zephyr.trading.auto_runtime_core
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from zephyr.trading.capability_card import CapabilityCard, CapabilityCategory
from zephyr.trading.capability_registry import CapabilityRegistry

if TYPE_CHECKING:
    from zephyr.infrastructure.a2a_protocol.layer1_discovery.a2a_registry import A2ARegistry

logger = logging.getLogger(__name__)

_SKILL_CATEGORY_MAP: dict[str, CapabilityCategory] = {
    "database-specialist": CapabilityCategory.DATA,
    "mcp-specialist": CapabilityCategory.INFRA,
    "context-specialist": CapabilityCategory.INFRA,
    "feedback-specialist": CapabilityCategory.OBSERVABILITY,
    "gate-specialist": CapabilityCategory.GOVERNANCE,
    "agent-specialist": CapabilityCategory.SECURITY,
    "master-blueprint": CapabilityCategory.GOVERNANCE,
    "drift-detector": CapabilityCategory.GOVERNANCE,
    "knowledge-specialist": CapabilityCategory.SEARCH,
    "rollback-specialist": CapabilityCategory.INFRA,
    "lsg-security": CapabilityCategory.SECURITY,
    "vector-memory": CapabilityCategory.SEARCH,
    "task-system": CapabilityCategory.ORCHESTRATION,
    "system-telemetry": CapabilityCategory.OBSERVABILITY,
    "code-dedup-engine": CapabilityCategory.GOVERNANCE,
    "budget-enforcer": CapabilityCategory.GOVERNANCE,
    "auto-fix-engine": CapabilityCategory.INFRA,
    "a2a-protocol": CapabilityCategory.COORDINATION,
    "behavioral-auditor": CapabilityCategory.SECURITY,
}


class CapabilitySync:
    def __init__(self, registry: CapabilityRegistry) -> None:
        self._registry = registry

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def registry(self):
        """只读：registry（Stage 4 公共化）。"""
        return self._registry

    @registry.setter
    def registry(self, value):
        """写入：registry（Stage 4 公共化）。"""
        self._registry = value

    def sync_a2a(self, a2a_registry: A2ARegistry | None) -> int:
        if a2a_registry is None:
            return 0
        synced = 0
        try:
            for card in a2a_registry._cards.values():
                cap_id = f"a2a-agent-{card.agent_id}"
                existing = self._registry.get(cap_id)
                if existing is None:
                    cap_card = CapabilityCard(
                        capability_id=cap_id,
                        name=f"A2A Agent: {card.name}",
                        category=CapabilityCategory.SEARCH,
                        description=card.description,
                        input_schema={"type": "object"},
                        output_schema={"type": "object"},
                        tags=["a2a-agent", card.agent_id] + [c.value for c in card.capabilities],
                        priority="P2",
                        runtime_plane="warm",
                        requires_human=False,
                    )
                    self._registry.register(cap_card)
                    synced += 1
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in capability_sync", exc_info=True)
        return synced

    def sync_skills(self, skill_registry_path: Path) -> int:
        synced = 0
        try:
            if not skill_registry_path.exists():
                return 0
            with open(skill_registry_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            for category in ("domain", "role"):
                for sid, sdata in data.get("skills", {}).get(category, {}).items():
                    cap_id = sid.lower().replace("_", "-")
                    existing = self._registry.get(cap_id)
                    if existing is not None:
                        continue
                    name = sdata.get("name", sid)
                    desc = sdata.get("description", f"Skill-derived capability: {name}")
                    cap_category = _SKILL_CATEGORY_MAP.get(name, CapabilityCategory.INFRA)
                    tier = sdata.get("tier", "L1")
                    plane = "warm" if tier in ("L0", "L1") else "cold"  # noqa: gate-vocab  业务逻辑：L0/L1 层映射 warm 运行面，其余 cold（非词表成员校验）
                    cap_card = CapabilityCard(
                        capability_id=cap_id,
                        name=f"Skill: {name}",
                        category=cap_category,
                        description=desc,
                        input_schema={"type": "object"},
                        output_schema={"type": "object"},
                        tags=["skill-derived", category, name],
                        priority="P1" if category == "domain" else "P2",
                        runtime_plane=plane,
                        requires_human=False,
                    )
                    self._registry.register(cap_card)
                    synced += 1
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in capability_sync", exc_info=True)
        return synced
