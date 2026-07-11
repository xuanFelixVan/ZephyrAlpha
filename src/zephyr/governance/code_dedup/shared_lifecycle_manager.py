# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.shared_lifecycle_manager
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/shared/test_shared_lifecycle_manager.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_shared_lifecycle_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""共享函数生命周期管理 — Active->Deprecated->Grace->Sunset->Retired 五阶段状态机.

职责：
  - 5阶段状态机：Active -> Deprecated(0caller_30days) -> Grace(30days) -> Sunset(precommit_block) -> Retired(kb_only)
  - 迁移diff生成（from old_import -> to new_import）
  - 影子清单同步降级
  - shared-lifecycle.yaml 维护
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

import yaml


class LifecycleStage(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    GRACE_PERIOD = "grace_period"
    SUNSET = "sunset"
    RETIRED = "retired"


@dataclass
class MigrationDiff:
    old_import: str = ""
    new_import: str = ""
    deprecation_reason: str = ""
    generated_at: str = ""


@dataclass
class LifecycleEntry:
    function_name: str = ""
    module_path: str = ""
    lifecycle_stage: str = LifecycleStage.ACTIVE.value
    active_since: str = ""
    deprecated_at: str = ""
    grace_period_start: str = ""
    sunset_at: str = ""
    retired_at: str = ""
    caller_count: int = 0
    migration_diff: MigrationDiff | None = None
    retirement_reason: str = ""
    graveyard_fingerprint: str = ""


class SharedLifecycleManager:
    """共享函数生命周期管理器."""

    def __init__(self, lifecycle_path: str | Path | None = None) -> None:
        if lifecycle_path is None:
            lifecycle_path = Path("data/cache/shared-lifecycle.yaml")
        self._lifecycle_path = Path(lifecycle_path)
        self._entries: dict[str, LifecycleEntry] = {}
        self._load()

    # ── 公共 API ──────────────────────────────────────────────

    def register_active(self, function_name: str, module_path: str, caller_count: int = 0) -> LifecycleEntry:
        """注册活跃函数."""
        key = f"{module_path}::{function_name}"
        entry = LifecycleEntry(
            function_name=function_name,
            module_path=module_path,
            lifecycle_stage=LifecycleStage.ACTIVE.value,
            active_since=datetime.now(UTC).isoformat(),
            caller_count=caller_count,
        )
        self._entries[key] = entry
        self._save()
        return entry

    def transition(
        self, function_name: str, module_path: str, to_stage: str, reason: str = ""
    ) -> LifecycleEntry | None:
        """状态转移."""
        key = f"{module_path}::{function_name}"
        entry = self._entries.get(key)
        if entry is None:
            return None

        now = datetime.now(UTC).isoformat()
        entry.lifecycle_stage = to_stage

        if to_stage == LifecycleStage.DEPRECATED.value:
            entry.deprecated_at = now
        elif to_stage == LifecycleStage.GRACE_PERIOD.value:
            entry.grace_period_start = now
        elif to_stage == LifecycleStage.SUNSET.value:
            entry.sunset_at = now
        elif to_stage == LifecycleStage.RETIRED.value:
            entry.retired_at = now
            entry.retirement_reason = reason

        self._entries[key] = entry
        self._save()
        return entry

    def generate_migration(
        self,
        old_function: str,
        old_module: str,
        new_function: str,
        new_module: str,
        reason: str = "",
    ) -> MigrationDiff:
        """生成迁移 diff."""
        return MigrationDiff(
            old_import=f"from {old_module} import {old_function}",
            new_import=f"from {new_module} import {new_function}",
            deprecation_reason=reason,
            generated_at=datetime.now(UTC).isoformat(),
        )

    def remove_from_shadow_manifest(self, function_name: str, module_path: str) -> bool:
        """从影子清单移除（Deprecated 状态触发）."""
        key = f"{module_path}::{function_name}"
        entry = self._entries.get(key)
        if entry is None:
            return False
        entry.lifecycle_stage = LifecycleStage.DEPRECATED.value
        entry.deprecated_at = datetime.now(UTC).isoformat()
        self._entries[key] = entry
        self._save()
        return True

    def get_graveyard(self) -> list[dict]:
        """获取退役记录."""
        return [
            {
                "function_name": e.function_name,
                "module_path": e.module_path,
                "retired_at": e.retired_at,
                "retirement_reason": e.retirement_reason,
            }
            for e in self._entries.values()
            if e.lifecycle_stage == LifecycleStage.RETIRED.value
        ]

    def get_deprecated_functions(self) -> list[LifecycleEntry]:
        """获取已弃用的函数列表."""
        return [e for e in self._entries.values() if e.lifecycle_stage != LifecycleStage.ACTIVE.value]

    def get_active_functions(self) -> list[LifecycleEntry]:
        """获取活跃函数列表."""
        return [e for e in self._entries.values() if e.lifecycle_stage == LifecycleStage.ACTIVE.value]

    # ── 内部 ──────────────────────────────────────────────────

    def _load(self) -> None:
        self._entries.clear()
        if not self._lifecycle_path.exists():
            return
        try:
            data = yaml.safe_load(self._lifecycle_path.read_text(encoding="utf-8")) or {}
            for entry_data in data.get("functions", []):
                md = entry_data.pop("migration_diff", None)
                entry = LifecycleEntry(**entry_data)
                if md:
                    entry.migration_diff = MigrationDiff(**md)
                key = f"{entry.module_path}::{entry.function_name}"
                self._entries[key] = entry
        except (yaml.YAMLError, OSError):
            pass

    def _save(self) -> None:
        self._lifecycle_path.parent.mkdir(parents=True, exist_ok=True)
        functions_data = []
        for entry in self._entries.values():
            data = entry.__dict__.copy()
            if entry.migration_diff:
                data["migration_diff"] = entry.migration_diff.__dict__
            functions_data.append(data)

        yaml_data = {
            "version": "1.0.0",
            "updated_at": datetime.now(UTC).isoformat(),
            "total_functions": len(functions_data),
            "functions": functions_data,
        }
        self._lifecycle_path.write_text(
            yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )
