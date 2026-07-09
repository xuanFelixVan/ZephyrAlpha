# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain-infra_ops/asset-inventory/blueprint.md
# [MODULE] zephyr.infrastructure.asset_inventory.classifier
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
# [A_module] module_id=MOD-INF_classifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""AssetClassifier — MOD-INF-026 L2 资产自动分类器

蓝图 §3.2：读取扫描结果，按 config/asset_inventory.yaml 中
classifier.type_mapping 将每个文件分类为 module/script/gate/doc/config/test/data/registry/unknown。
"""

from __future__ import annotations

import logging
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.infrastructure.asset_inventory.models import (
    AssetLayer,
    AssetStatus,
    AssetType,
    ClassificationResult,
    ClassifiedAsset,
    Priority,
    RawFileEntry,
    ScanResult,
)

logger = logging.getLogger(__name__)

TYPE_MAPPING: list[tuple[str, list[str], AssetType]] = [
    ("src/zephyr/", [".py"], AssetType.MODULE),
    ("scripts/", [".py"], AssetType.SCRIPT),
    ("docs/", [".md"], AssetType.DOC),
    ("config/", [".yaml", ".json", ".toml"], AssetType.CONFIG),
    ("tests/", [".py"], AssetType.TEST),
    ("data/", [".db", ".jsonl", ".yaml"], AssetType.DATA),
]

REGISTRY_PATTERNS = ["_registry.yaml", "manifest.yaml"]

LAYER_BY_DIR: dict[str, AssetLayer] = {
    "src/zephyr/governance/": AssetLayer.L01,
    "src/zephyr/": AssetLayer.CROSS_LAYER,
    "scripts/governance/": AssetLayer.L01,
    "scripts/": AssetLayer.CROSS_LAYER,
    "docs/01_": AssetLayer.L01,
    "docs/02_": AssetLayer.L02,
    "docs/03_": AssetLayer.L03,
    "docs/": AssetLayer.L04,
    "config/": AssetLayer.L01,
    "tests/": AssetLayer.L04,
    "data/": AssetLayer.CROSS_LAYER,
}

STATUS_BY_DIR: dict[str, AssetStatus] = {
    "_deprecated/": AssetStatus.DEPRECATED,
    "_archived/": AssetStatus.ARCHIVED,
    "_backup/": AssetStatus.ARCHIVED,
    "_legacy/": AssetStatus.DEPRECATED,
}


class Classifier:
    """基于类型映射的资产自动分类器——Phase 1 实现（蓝图 §3.2）。"""

    def __init__(
        self,
        type_mapping: list[tuple[str, list[str], AssetType]] | None = None,
        unknown_threshold_pct: float = 10.0,
    ) -> None:
        self.type_mapping = type_mapping or TYPE_MAPPING
        self.unknown_threshold_pct = unknown_threshold_pct

    def classify(self, scan_result: ScanResult) -> ClassificationResult:
        classification_id = _generate_classification_id()
        logger.info("开始分类: %s (源: %s)", classification_id, scan_result.scan_id)

        assets: list[ClassifiedAsset] = []
        for entry in scan_result.entries:
            asset = self._classify_one(entry)
            assets.append(asset)

        unknown = [a for a in assets if a.asset_type is AssetType.UNKNOWN]
        unknown_pct = (len(unknown) / len(assets) * 100) if assets else 0.0

        by_type: dict[str, int] = dict(Counter(a.asset_type.value for a in assets))
        by_layer: dict[str, int] = dict(Counter(a.layer.value for a in assets))

        if unknown_pct > self.unknown_threshold_pct:
            logger.warning(
                "未知类型占比 %.1f%% 超过阈值 %.1f%% (%d 个文件)",
                unknown_pct,
                self.unknown_threshold_pct,
                len(unknown),
            )

        logger.info(
            "分类完成: %d 资产, %d 未知 (%.1f%%)",
            len(assets),
            len(unknown),
            unknown_pct,
        )

        return ClassificationResult(
            classification_id=classification_id,
            source_scan_id=scan_result.scan_id,
            total_classified=len(assets),
            unknown_count=len(unknown),
            unknown_pct=round(unknown_pct, 1),
            by_type=by_type,
            by_layer=by_layer,
            assets=assets,
        )

    def _classify_one(self, entry: RawFileEntry) -> ClassifiedAsset:
        asset_type = AssetType.UNKNOWN
        asset_layer = AssetLayer.CROSS_LAYER
        asset_status = AssetStatus.ACTIVE
        priority = Priority.P3

        for prefix, extensions, atype in self.type_mapping:
            if entry.relative_path.startswith(prefix) and entry.extension in extensions:
                asset_type = atype
                break

        if entry.relative_path.endswith(tuple(REGISTRY_PATTERNS)):
            asset_type = AssetType.REGISTRY

        for prefix, layer in LAYER_BY_DIR.items():
            if entry.relative_path.startswith(prefix):
                asset_layer = layer
                break

        for suffix, status in STATUS_BY_DIR.items():
            if suffix in entry.relative_path:
                asset_status = status
                break

        candidate_dirs = [p for p, _, _ in self.type_mapping]
        for prefix in sorted(candidate_dirs, key=len, reverse=True):
            if entry.relative_path.startswith(prefix):
                if any(
                    True
                    for _, exts, _ in self.type_mapping
                    if prefix in entry.relative_path and entry.extension in exts
                ):
                    pass
                break
        else:
            if any(entry.relative_path.startswith(d) for d in candidate_dirs):
                pass

        if entry.extension in (".yaml",):
            for pat in REGISTRY_PATTERNS:
                if entry.relative_path.endswith(pat):
                    break

        return ClassifiedAsset(
            relative_path=entry.relative_path,
            asset_type=asset_type,
            layer=asset_layer,
            status=asset_status,
            priority=priority,
            size_bytes=entry.size_bytes,
            mtime_utc=entry.mtime_utc,
            sha256=entry.sha256,
            classification_confidence=0.85 if asset_type is not AssetType.UNKNOWN else 0.3,
        )

    def main(self) -> None:
        import json
        import os

        scans_dir = REPO_ROOT / "data" / "scans"
        scan_path = scans_dir / "raw-asset-scan.json"

        if not scan_path.exists():
            print("警告: 扫描文件不存在，运行 scanner 先")
            print(
                '  python -c "from zephyr.infrastructure.asset_inventory.scanner import Scanner; r = Scanner().scan(); Scanner().save(r)"'
            )
            return

        payload = json.loads(scan_path.read_text(encoding="utf-8"))
        from zephyr.infrastructure.asset_inventory.models import RawFileEntry

        entries = [RawFileEntry(**e) for e in payload["entries"]]
        scan_result = ScanResult(**{**payload, "entries": entries})

        result = self.classify(scan_result)

        klass_dir = REPO_ROOT / "data" / "classified"
        klass_dir.mkdir(parents=True, exist_ok=True)
        out = klass_dir / "classified-assets.json"
        payload = result.model_dump(mode="json")
        content = json.dumps(payload, ensure_ascii=False, indent=2)
        tmp = f"{out}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, out)

        print(f"  CLASSIFY  {result.classification_id}")
        print(f"  TOTAL     {result.total_classified}")
        print(f"  UNKNOWN   {result.unknown_count} ({result.unknown_pct}%)")
        print(f"  BY TYPE   {result.by_type}")
        print(f"  OUTPUT    {out}")


def _generate_classification_id() -> str:
    now = datetime.now(UTC)
    seq = str(now.timestamp()).replace(".", "")[-3:]
    return f"CLS-{now.strftime('%Y%m%d')}-{seq}"


def main() -> None:
    Classifier().main()


if __name__ == "__main__":
    main()
