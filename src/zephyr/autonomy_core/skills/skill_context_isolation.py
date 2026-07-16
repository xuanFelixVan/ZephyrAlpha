# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_context_isolation
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Context Isolation
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

Skill 上下文隔离引擎
====================
防止跨 Skill 上下文污染:
  1. NamespaceIsolation: 每个 Skill 独立命名空间
  2. DataLeakagePrevention: 阻止前一个 Skill 的输出泄露到下一个 Skill
  3. ContaminationCheck: 检测上下文是否已被污染
  4. SnapshotRestore: 多 Skill 切换时的上下文快照
"""

from __future__ import annotations

import copy
from datetime import UTC, datetime
from typing import Any


class ContextIsolation:
    """Skill 上下文隔离器"""

    ISOLATION_STRICT = "strict"
    ISOLATION_PERMISSIVE = "permissive"
    ISOLATION_SNAPSHOT = "snapshot"

    def __init__(self, mode: str = ISOLATION_STRICT):
        self._mode = mode
        self._namespaces: dict[str, dict[str, Any]] = {}
        self._snapshots: dict[str, dict[str, Any]] = {}
        self._contamination_log: list[dict[str, Any]] = []

    @property
    def isolation_level(self) -> str:
        return self._mode

    def create_namespace(self, skill_id: str) -> str:
        ns_key = f"ns:{skill_id}"
        if ns_key not in self._namespaces:
            self._namespaces[ns_key] = {
                "skill_id": skill_id,
                "created_at": datetime.now(UTC).isoformat(),
                "data": {},
                "tokens_used": 0,
                "locked": False,
            }
        return ns_key

    def isolate_execution(
        self,
        skill_id: str,
        context: dict[str, Any],
        previous_skill_id: str | None = None,
    ) -> dict[str, Any]:
        ns_key = self.create_namespace(skill_id)

        # 5.147.6 修复: context: dict[str, Any] 值类型为 Any, 调用方可传入含循环引用或极深嵌套的结构,
        # copy.deepcopy 可能抛 RecursionError。捕获后回退到浅拷贝避免崩溃 (隔离功能降级优于进程崩溃)
        try:
            clean_context = copy.deepcopy(context)
        except RecursionError:
            clean_context = dict(context)

        if previous_skill_id and self._mode == self.ISOLATION_STRICT:
            prev_ns = f"ns:{previous_skill_id}"
            if prev_ns in self._namespaces:
                self._namespaces[prev_ns]["locked"] = True

            leaked_keys = []
            for key in clean_context:
                if key.startswith("skill_") or key.startswith(f"_{previous_skill_id}_"):
                    leaked_keys.append(key)

            for key in leaked_keys:
                del clean_context[key]

            if leaked_keys:
                self._contamination_log.append(
                    {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "action": "context_cleaned",
                        "from_skill": previous_skill_id,
                        "to_skill": skill_id,
                        "leaked_keys": leaked_keys,
                    }
                )

        self._namespaces[ns_key]["data"] = clean_context

        return {
            "isolation_level": self._mode,
            "namespace": ns_key,
            "context_cleaned": len(clean_context) < len(context),
            "context": clean_context,
        }

    def snapshot(self, skill_id: str) -> str:
        ns_key = f"ns:{skill_id}"
        snapshot_id = f"snap:{skill_id}:{datetime.now(UTC).timestamp()}"
        self._snapshots[snapshot_id] = copy.deepcopy(self._namespaces.get(ns_key, {"skill_id": skill_id}))
        return snapshot_id

    def restore(self, snapshot_id: str) -> dict[str, Any] | None:
        if snapshot_id in self._snapshots:
            data = self._snapshots[snapshot_id]
            skill_id = data.get("skill_id", "")
            ns_key = f"ns:{skill_id}"
            self._namespaces[ns_key] = copy.deepcopy(data)
            # 5.85.2 修复：原返回 self._namespaces[ns_key]（内部dict的直接引用），调用方可修改返回的dict，直接篡改isolator的内部状态。
            return copy.deepcopy(self._namespaces[ns_key])
        return None

    def check_contamination(
        self,
        skill_id: str,
        current_context: dict[str, Any],
    ) -> dict[str, Any]:
        ns_key = f"ns:{skill_id}"
        namespace = self._namespaces.get(ns_key, {}).get("data", {})

        foreign_keys = []
        for key in current_context:
            if key.startswith("skill_") and not key.startswith(f"skill_{skill_id.replace('-', '_')}"):
                foreign_keys.append(key)

        contaminated = len(foreign_keys) > 0

        return {
            "skill_id": skill_id,
            "contaminated": contaminated,
            "foreign_keys": foreign_keys,
            "contamination_count": len(foreign_keys),
            "isolation_level": self._mode,
        }
