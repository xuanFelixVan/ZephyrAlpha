# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §4.2
# [MODULE] zephyr.security.access_control.orphan_judge.models
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.orphan_judge.judge
# [CONSUMERS] db.py; report_generator.py; config_loader.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 数据模型是orphan_judge的类型SSoT; 不修改任何文件
# [MODIFY-GUARD] 修改字段必须同步blueprint.md §4.2; 已有模型(Judgment/Verdict/LayerResult)的真源在judge.py,此处仅re-export
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] Pydantic ValidationError on bad input
# [TESTS] tests/orphan-judge/test_models.py
# [A_module] module_id=MOD-SEC_models | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from zephyr.security.access_control.orphan_judge.judge import (
    Confidence,
    Judgment,
    LayerResult,
    OrphanJudgeReport,
    Verdict,
)

__all__ = [
    "Confidence",
    "Judgment",
    "JudgmentRecord",
    "LayerResult",
    "OrphanJudgeConfig",
    "OrphanJudgeReport",
    "ScanSummary",
    "Verdict",
]


class JudgmentRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(description="文件路径")
    verdict: str = Field(description="判决结果(KEEP/DELETE/DEPRECATE/EXTRACT_AND_MERGE/ESCALATE)")
    confidence: str = Field(description="置信度(high/medium/low)")
    reason: str = Field(default="", description="判决原因")
    layers_json: str = Field(default="{}", description="层级结果JSON")
    scanned_at: datetime = Field(default_factory=datetime.now, description="扫描时间")
    file_hash: str = Field(default="", description="文件SHA256")


class ScanSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int = Field(default=0, description="扫描文件总数")
    keep: int = Field(default=0)
    delete: int = Field(default=0)
    deprecate: int = Field(default=0)
    extract_and_merge: int = Field(default=0)
    escalate: int = Field(default=0)
    error: int = Field(default=0)
    duration_ms: float = Field(default=0.0, description="扫描耗时(毫秒)")
    scanned_at: datetime = Field(default_factory=datetime.now)


class OrphanJudgeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_unique_nodes: int = Field(default=5, ge=1, description="L3最小独特节点数阈值")
    max_scan_files: int = Field(default=50, ge=1, description="扫描文件上限")
    max_references: int = Field(default=20, ge=1, description="引用检测结果上限")
    standalone_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="L4独立价值阈值")
    file_size_weight: float = Field(default=0.15, ge=0.0, le=1.0)
    code_lines_weight: float = Field(default=0.20, ge=0.0, le=1.0)
    definition_count_weight: float = Field(default=0.20, ge=0.0, le=1.0)
    docstring_ratio_weight: float = Field(default=0.10, ge=0.0, le=1.0)
    test_exists_weight: float = Field(default=0.10, ge=0.0, le=1.0)
    import_depth_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    registry_candidates: list[str] = Field(
        default_factory=lambda: [
            "docs/registry_of_registries.yaml",
            "scripts/script-manifest.yaml",
            "src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml",
            "data/asset_index/unified-asset-index.yaml",
        ]
    )
