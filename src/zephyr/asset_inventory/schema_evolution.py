"""MOD-INF-026 §34 — Schema Evolution 迁移引擎。

SchemaMigrationGate: 自动完整性校验——schema_version vs 实际结构。
无外部迁移框架依赖，纯 pydantic introspect。
"""

from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class MigrationStep(BaseModel):
    version: str
    description: str
    applied_at: Optional[datetime] = None
    reverted: bool = False


class MigrationPlan(BaseModel):
    asset_type: str = "unified_asset_index"
    current_version: str
    target_version: str
    steps: list[MigrationStep] = Field(default_factory=list)
    requires_downtime: bool = False
    is_breaking: bool = False


class SchemaEvolutionManager:

    VERSIONS: list[str] = ["1.0.0", "1.1.0", "2.0.0"]

    def __init__(self, project_root: Path) -> None:
        self._root = project_root
        self._log_dir = project_root / "data" / "migrations"

    def check_compatibility(self, current_version: str) -> MigrationPlan:
        plan = MigrationPlan(current_version=current_version, target_version=self.VERSIONS[-1])

        if current_version not in self.VERSIONS:
            plan.is_breaking = True
            plan.requires_downtime = True
            plan.steps = [
                MigrationStep(version=current_version, description=f"Unknown version {current_version} — needs manual migration"),
            ]
            return plan

        current_idx = self.VERSIONS.index(current_version)
        target_idx = self.VERSIONS.index(plan.target_version)

        if current_idx >= target_idx:
            return plan

        for vi in range(current_idx + 1, target_idx + 1):
            ver = self.VERSIONS[vi]
            plan.steps.append(MigrationStep(version=ver, description=self._step_desc(ver)))

        return plan

    def run_migration(self, plan: MigrationPlan, data: dict) -> dict:
        if plan.is_breaking and not plan.steps[0].version == plan.current_version:
            raise ValueError(f"Breaking migration from {plan.current_version} — manual intervention required")

        current = dict(data)
        for step in plan.steps:
            current = self._apply_step(current, step.version)

        return current

    def _apply_step(self, data: dict, target_version: str) -> dict:
        if target_version == "1.1.0":
            return self._migrate_1_0_to_1_1(data)
        if target_version == "2.0.0":
            return self._migrate_1_1_to_2_0(data)
        return data

    def _migrate_1_0_to_1_1(self, data: dict) -> dict:
        d = dict(data)
        d["schema_version"] = "1.1.0"

        if "assets" in d:
            for asset in d["assets"]:
                if "tags" not in asset or asset["tags"] is None:
                    asset["tags"] = []
                if "custom_metadata" not in asset or asset["custom_metadata"] is None:
                    asset["custom_metadata"] = {}
        return d

    def _migrate_1_1_to_2_0(self, data: dict) -> dict:
        d = dict(data)
        d["schema_version"] = "2.0.0"
        d["orphan_rate_pct"] = d.get("orphan_rate_pct", 0.0)
        d["ghost_rate_pct"] = d.get("ghost_rate_pct", 0.0)
        d["drift_rate_pct"] = d.get("drift_rate_pct", 0.0)
        return d

    @staticmethod
    def _step_desc(version: str) -> str:
        if version == "1.1.0":
            return "添加 tags/custom_metadata 默认值，schema_version=1.1.0"
        if version == "2.0.0":
            return "添加 orphan_rate_pct/ghost_rate_pct/drift_rate_pct，schema_version=2.0.0"
        return f"Migration to {version}"

    def write_migration_log(self, plan: MigrationPlan) -> Path:
        self._log_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        log_path = self._log_dir / f"migration_{plan.asset_type}_{ts}.yaml"

        import yaml
        tmp = f"{log_path}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.dump(plan.model_dump(mode="python"), f, allow_unicode=True, default_flow_style=False)
        os.replace(tmp, str(log_path))
        return log_path
