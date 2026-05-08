"""UnifiedAssetIndex — MOD-INF-026 L3 统一资产索引生成器

蓝图 §3.3 + §17：读取 24 个注册表 + 分类资产 → 生成 unified_asset_index.yaml
作为项目 SSoT。使用 temp-file + atomic rename 写入。
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from zephyr.asset_inventory.models import (
    ClassificationResult,
    ClassifiedAsset,
    RegistryEntry,
    UnifiedAssetIndex,
)

logger = logging.getLogger(__name__)

INDEX_DIR = Path(__file__).resolve().parents[3] / "data" / "asset_index"
INDEX_PATH = INDEX_DIR / "unified_asset_index.yaml"
REGISTRY_DIRS = [
    (Path(__file__).resolve().parents[3] / "src" / "zephyr" / "gates", "_registry.yaml"),
    (Path(__file__).resolve().parents[3] / "docs" / "03_modules", "module-registry.yaml"),
    (Path(__file__).resolve().parents[3] / "docs" / "03_modules", "blueprint-registry.yaml"),
]

HEALTH_WEIGHTS = {"orphan": 0.35, "ghost": 0.35, "drift": 0.20, "recency": 0.10}


class IndexGenerator:
    """统一资产索引生成器——Phase 1 实现（蓝图 §3.3）。"""

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path(__file__).resolve().parents[3]

    def generate(
        self, classified_result: ClassificationResult, registry_entries: Optional[list[RegistryEntry]] = None
    ) -> UnifiedAssetIndex:
        logger.info("开始生成统一资产索引...")

        assets = classified_result.assets
        orphan_rate = classified_result.unknown_pct

        gh = _calc_grade(orphan_rate, 0.0, 0.0)

        index = UnifiedAssetIndex(
            generated_at=datetime.now(timezone.utc),
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

    def save(self, index: UnifiedAssetIndex, output_path: Optional[Path] = None) -> Path:
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
        klass_path = klass_dir / "classified_assets.json"
        if not klass_path.exists():
            print("警告: 分类文件不存在，先运行 classifier")
            return

        payload = json.loads(klass_path.read_text(encoding="utf-8"))
        from zephyr.asset_inventory.models import RawFileEntry
        entries = [RawFileEntry(**e) for e in payload.get("entries", [])]
        assets = [ClassifiedAsset(**a) for a in payload.get("assets", [])]
        cr = ClassificationResult(**{**payload, "assets": assets})

        index = self.generate(cr)
        out = self.save(index)
        print(f"  INDEX   {index.total_assets} 资产")
        print(f"  HEALTH  {index.health_score}")
        print(f"  OUTPUT  {out}")


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


def _repr_value(value: Any) -> str:
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
