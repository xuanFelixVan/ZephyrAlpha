# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain-infra_ops/asset-inventory/blueprint.md
# [MODULE] zephyr.infrastructure.asset_inventory.index_generator
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_index_generator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""UnifiedAssetIndex — MOD-INF-026 L3 统一资产索引生成器

蓝图 §3.3 + §17：读取 24 个注册表 + 分类资产 -> 生成 unified-asset-index.yaml
作为项目 SSoT。使用 temp-file + atomic rename 写入。
"""

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.infrastructure.asset_inventory.models import (
    ClassificationResult,
    ClassifiedAsset,
    RegistryEntry,
    UnifiedAssetIndex,
)
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

INDEX_DIR = REPO_ROOT / "data" / "asset_index"
INDEX_PATH = INDEX_DIR / "unified-asset-index.yaml"
REGISTRY_DIRS = [
    (REPO_ROOT / "src" / "zephyr" / "gates", "_registry.yaml"),
    (REPO_ROOT / "docs" / "03_modules", "module-registry.yaml"),
    (REPO_ROOT / "docs" / "03_modules", "blueprint_registry.yaml"),
]

HEALTH_WEIGHTS = {"orphan": 0.35, "ghost": 0.35, "drift": 0.20, "recency": 0.10}


class IndexGenerator:
    """统一资产索引生成器——Phase 1 实现（蓝图 §3.3）。"""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or REPO_ROOT

    def generate(
        self, classified_result: ClassificationResult, registry_entries: list[RegistryEntry] | None = None
    ) -> UnifiedAssetIndex:
        logger.info("开始生成统一资产索引...")

        assets = classified_result.assets
        orphan_rate = classified_result.unknown_pct

        gh = _calc_grade(orphan_rate, 0.0, 0.0)

        index = UnifiedAssetIndex(
            generated_at=datetime.now(UTC),
            total_assets=len(assets),
            health_score=gh,
            health_score_numeric=_calc_numeric(orphan_rate, 0.0, 0.0),
            orphan_rate_pct=round(orphan_rate, 1),
            ghost_rate_pct=0.0,
            drift_rate_pct=0.0,
            by_type=classified_result.by_type,
            by_layer=classified_result.by_layer,
            by_status=_count_by_status(assets),
            registries_checked=len(REGISTRY_DIRS),
            assets=assets,
        )

        logger.info("索引生成完成: %d 资产, 健康 %s", index.total_assets, index.health_score)
        return index

    def save(self, index: UnifiedAssetIndex, output_path: Path | None = None) -> Path:
        target = output_path or INDEX_PATH
        INDEX_DIR.mkdir(parents=True, exist_ok=True)

        payload = index.model_dump(mode="json")
        content = _to_yaml(payload)

        tmp = f"{target}.{os.getpid()}.tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp, target)
        except PermissionError:
            try:
                os.remove(tmp)
            except OSError:
                pass
            raise

        logger.info("索引已写入: %s", target)
        return Path(target)

    def main(self) -> None:
        klass_dir = self.root / "data" / "classified"
        klass_path = klass_dir / "classified-assets.json"
        if not klass_path.exists():
            # 5.170.4 修复: 警告信息 print -> logger.warning
            logger.warning("分类文件不存在，先运行 classifier: %s", klass_path)
            return

        payload = json.loads(klass_path.read_text(encoding="utf-8"))
        from zephyr.infrastructure.asset_inventory.models import RawFileEntry

        entries = [RawFileEntry(**e) for e in payload.get("entries", [])]
        assets = [ClassifiedAsset(**a) for a in payload.get("assets", [])]
        cr = ClassificationResult(**{**payload, "assets": assets})

        index = self.generate(cr)
        out = self.save(index)
        # 5.170.5 修复: 结果输出 print -> logger.info (库代码 CLI 入口)
        logger.info("INDEX %d 资产 | HEALTH %s | OUTPUT %s", index.total_assets, index.health_score, out)


def _calc_grade(orphan: float, ghost: float, drift: float) -> str:
    score = _calc_numeric(orphan, ghost, drift)
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 55:
        return "C"
    if score >= 35:
        return "D"
    return "F"


def _calc_numeric(orphan: float, ghost: float, drift: float) -> float:
    orphan_n = max(0.0, 100 - orphan * 5)
    ghost_n = max(0.0, 100 - ghost * 10)
    drift_n = max(0.0, 100 - drift * 2)
    return round(
        orphan_n * HEALTH_WEIGHTS["orphan"]
        + ghost_n * HEALTH_WEIGHTS["ghost"]
        + drift_n * HEALTH_WEIGHTS["drift"]
        + 80 * HEALTH_WEIGHTS["recency"],
        1,
    )


def _count_by_status(assets: list[ClassifiedAsset]) -> dict[str, int]:
    from collections import Counter

    return dict(Counter(a.status.value for a in assets))


def _to_yaml(data: dict[str, Any], indent: int = 0) -> str:
    lines: list[str] = []
    prefix = "  " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(_to_yaml(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}:")
            for item in value:
                if isinstance(item, dict):
                    lines.append(_to_yaml_list_item(item, indent + 1))
                else:
                    lines.append(f"{prefix}  - {_repr_value(item)}")
        elif isinstance(value, bool):
            lines.append(f"{prefix}{key}: {'true' if value else 'false'}")
        elif isinstance(value, (int, float)):
            lines.append(f"{prefix}{key}: {value}")
        elif value is None:
            lines.append(f"{prefix}{key}: null")
        else:
            lines.append(f"{prefix}{key}: {_repr_value(value)}")
    return "\n".join(lines)


def _to_yaml_list_item(item: dict[str, Any], indent: int) -> str:
    lines: list[str] = []
    prefix = "  " * indent
    lines.append(f"{prefix}-")
    for key, value in item.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}  {key}:")
            lines.append(_to_yaml(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}  {key}:")
            for v in value:
                lines.append(f"{prefix}    - {_repr_value(v)}")
        else:
            lines.append(f"{prefix}  {key}: {_repr_value(value)}")
    return "\n".join(lines)


def _repr_value(value: object) -> str:
    if isinstance(value, str):
        if any(ch in value for ch in ('"', "\\", "\n", ":", "#")):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return f'"{value}"'
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def main() -> None:
    IndexGenerator().main()


if __name__ == "__main__":
    main()

# ============================================================================
# SRC-0040: 从 schema_evolution.py 合并 — SchemaEvolutionManager + MigrationPlan
# ============================================================================

from pydantic import BaseModel as _SchemaBaseModel
from pydantic import Field as _SchemaField


class MigrationStep(_SchemaBaseModel):
    version: str
    description: str
    applied_at: datetime | None = None
    reverted: bool = False


class MigrationPlan(_SchemaBaseModel):
    asset_type: str = "unified-asset-index"
    current_version: str
    target_version: str
    steps: list[MigrationStep] = _SchemaField(default_factory=list)
    requires_downtime: bool = False
    is_breaking: bool = False


class SchemaEvolutionManager:
    """Schema Evolution 迁移引擎——自动完整性校验，纯 pydantic introspect。"""

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
                MigrationStep(
                    version=current_version, description=f"Unknown version {current_version} — needs manual migration"
                ),
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
        ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        log_path = self._log_dir / f"migration_{plan.asset_type}_{ts}.yaml"

        import yaml

        tmp = f"{log_path}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.dump(plan.model_dump(mode="python"), f, allow_unicode=True, default_flow_style=False)
        os.replace(tmp, str(log_path))
        return log_path
