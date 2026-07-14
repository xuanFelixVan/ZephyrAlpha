# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain-infra_ops/asset-inventory/blueprint.md
# [MODULE] zephyr.infrastructure.asset_inventory.models
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.asset_inventory.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_models | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""AssetInventoryModels — MOD-INF-026 Pydantic V2 共享数据模型

蓝图 §2 定义的全部 12 个数据模型。
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AssetType(str, Enum):
    MODULE = "module"
    SCRIPT = "script"
    GATE = "gate"
    DOC = "doc"
    CONFIG = "config"
    TEST = "test"
    DATA = "data"
    REGISTRY = "registry"
    UNKNOWN = "unknown"


class AssetLayer(str, Enum):
    L00 = "L00"
    L01 = "L01"
    L02 = "L02"
    L03 = "L03"
    L04 = "L04"
    CROSS_LAYER = "cross_layer"


class AssetStatus(str, Enum):
    ACTIVE = "active"
    STALE = "stale"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    GHOST = "ghost"
    ORPHAN = "orphan"


class Priority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class DriftType(str, Enum):
    SHA256 = "sha256"
    SIZE = "size"
    MTIME = "mtime"
    REGISTRY_PATH = "registry_path"
    STATUS = "status"


class ReconStatus(str, Enum):
    MATCHED = "matched"
    ORPHAN = "orphan"
    GHOST = "ghost"
    DRIFT = "drift"
    RENAME = "rename"


class HealthGrade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class RawFileEntry(BaseModel):
    relative_path: str = Field(description="项目根相对路径")
    absolute_path: str = Field(description="绝对路径")
    file_name: str = Field(description="文件名")
    extension: str = Field(description="文件扩展名，含点")
    size_bytes: int = Field(description="文件大小（字节）")
    mtime_utc: datetime = Field(description="最后修改时间 UTC")
    sha256: str = Field(description="SHA-256 十六进制字符串")
    is_binary: bool = Field(default=False, description="是否为二进制文件")


class ScanResult(BaseModel):
    scan_id: str = Field(description="扫描唯一标识 SCAN-YYYYMMDD-NNN")
    scanned_at: datetime = Field(default_factory=datetime.utcnow, description="扫描开始时间")
    completed_at: datetime | None = Field(default=None, description="扫描完成时间")
    total_files: int = Field(description="扫描文件总数")
    total_size_bytes: int = Field(description="扫描总大小")
    scan_mode: str = Field(default="full", description="full / incremental")
    entries: list[RawFileEntry] = Field(default_factory=list, description="扫描条目")
    errors: list[str] = Field(default_factory=list, description="扫描错误列表")
    duration_seconds: float | None = Field(default=None, description="扫描耗时")


class ClassifiedAsset(BaseModel):
    relative_path: str = Field(description="项目根相对路径")
    asset_type: AssetType = Field(description="资产类型")
    layer: AssetLayer = Field(default=AssetLayer.CROSS_LAYER, description="所属层级")
    status: AssetStatus = Field(default=AssetStatus.ACTIVE, description="资产状态")
    priority: Priority = Field(default=Priority.P3, description="优先级")
    size_bytes: int = Field(description="文件大小")
    mtime_utc: datetime = Field(description="最后修改时间")
    sha256: str = Field(description="SHA-256")
    registered_in: list[str] = Field(default_factory=list, description="已注册的注册表ID列表")
    classification_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="分类置信度")
    tags: list[str] = Field(default_factory=list, description="语义标签")
    custom_metadata: dict[str, str] = Field(default_factory=dict, description="自定义键值对")
    tags_last_updated: datetime | None = Field(default=None, description="标签最近更新时间")

    @field_validator("tags", "registered_in", mode="before")
    @classmethod
    def _none_to_list(cls, v: object) -> object:
        """容忍旧版 index 中的 None 值，转为空列表。"""
        return v if v is not None else []

    @field_validator("custom_metadata", mode="before")
    @classmethod
    def _none_to_dict(cls, v: object) -> object:
        """容忍旧版 index 中的 None 值，转为空字典。"""
        return v if v is not None else {}

    @field_validator("tags_last_updated", mode="before")
    @classmethod
    def _none_str_to_none(cls, v: object) -> object:
        """容忍旧版 index 中的 'None' 字符串，转为 None。"""
        if v in (None, "None"):
            return None
        return v


class ClassificationResult(BaseModel):
    classification_id: str = Field(description="分类任务 ID")
    classified_at: datetime = Field(default_factory=datetime.utcnow)
    source_scan_id: str = Field(description="源扫描 ID")
    total_classified: int = Field(description="已分类资产总数")
    unknown_count: int = Field(default=0, description="未能分类的资产数")
    unknown_pct: float = Field(default=0.0, description="未知率 %")
    by_type: dict[str, int] = Field(default_factory=dict, description="按类型统计计数")
    by_layer: dict[str, int] = Field(default_factory=dict, description="按层级统计计数")
    assets: list[ClassifiedAsset] = Field(default_factory=list, description="已分类资产")


class RegistryEntry(BaseModel):
    registry_id: str = Field(description="来源注册表 ID")
    registry_path: str = Field(description="注册表文件路径")
    entry_path: str = Field(description="资产相对路径")
    entry_type: AssetType = Field(default=AssetType.UNKNOWN, description="注册表中声明的类型")
    entry_status: AssetStatus = Field(default=AssetStatus.ACTIVE)
    extra: dict[str, Any] = Field(default_factory=dict, description="注册表特有字段")


class UnifiedAssetIndex(BaseModel):
    schema_version: str = Field(default="1.0.0", description="索引 Schema 版本")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="生成时间")
    last_reconciliation_at: datetime | None = Field(default=None, description="最近对账时间")
    total_assets: int = Field(description="资产总数")
    health_score: str = Field(default="N/A", description="健康评分 A/B/C/D/F")
    health_score_numeric: float = Field(default=0.0, ge=0.0, le=100.0, description="健康评分 0-100")
    orphan_rate_pct: float = Field(default=0.0, description="孤儿率 %")
    ghost_rate_pct: float = Field(default=0.0, description="幽灵率 %")
    drift_rate_pct: float = Field(default=0.0, description="漂移率 %")
    by_type: dict[str, int] = Field(default_factory=dict)
    by_layer: dict[str, int] = Field(default_factory=dict)
    by_status: dict[str, int] = Field(default_factory=dict)
    registries_checked: int = Field(default=0, description="已检查的注册表数")
    registries_skipped: int = Field(default=0, description="跳过的损坏注册表数")
    assets: list[ClassifiedAsset] = Field(default_factory=list, description="全量资产")


class GhostEntry(BaseModel):
    registry_id: str = Field(description="注册表 ID")
    registry_path: str = Field(description="注册表中记录的路径")
    registered_type: AssetType = Field(description="注册表中声明的类型")
    cached_sha256: str | None = Field(default=None, description="上次索引中缓存的 SHA-256")
    last_known_mtime: datetime | None = Field(default=None, description="最近已知的修改时间")
    ghost_since: datetime = Field(default_factory=datetime.utcnow, description="首次检测为幽灵的时间")
    days_ghost: float = Field(default=0.0, description="幽灵天数")
    candidates_for_cleanup: bool = Field(default=False, description="是否建议清理（>30d）")


class DriftEntry(BaseModel):
    relative_path: str = Field(description="漂移资产的相对路径")
    registered_sha256: str = Field(description="索引中记录的 SHA-256")
    disk_sha256: str = Field(description="磁盘上的实际 SHA-256")
    drift_types: list[DriftType] = Field(default_factory=list, description="漂移类型列表")
    registered_size: int | None = Field(default=None)
    disk_size: int | None = Field(default=None)
    registered_mtime: datetime | None = Field(default=None)
    disk_mtime: datetime | None = Field(default=None)
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class RenameEvent(BaseModel):
    old_path: str = Field(description="旧路径（幽灵）")
    new_path: str = Field(description="新路径（孤儿）")
    sha256: str = Field(description="一致的 SHA-256——证明是同一文件")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="重命名置信度")
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    auto_fixed: bool = Field(default=False)


class ReconciliationReport(BaseModel):
    report_id: str = Field(description="对账报告 ID")
    reconciled_at: datetime = Field(default_factory=datetime.utcnow)
    scan_id: str = Field(description="数据来源扫描 ID")
    dry_run: bool = Field(default=True, description="是否为预演模式")
    matched: int = Field(default=0, description="完全一致")
    orphans: list[ClassifiedAsset] = Field(default_factory=list, description="孤儿资产")
    ghosts: list[GhostEntry] = Field(default_factory=list, description="幽灵引用")
    drifts: list[DriftEntry] = Field(default_factory=list, description="漂移资产")
    renames: list[RenameEvent] = Field(default_factory=list, description="重命名事件")
    registries_checked: int = Field(default=0)
    registries_skipped: int = Field(default=0)
    skipped_registry_ids: list[str] = Field(default_factory=list, description="跳过的注册表ID")
    auto_fixed_count: int = Field(default=0, description="自动修复数")
    orphan_rate_before: float = Field(default=0.0)
    orphan_rate_after: float = Field(default=0.0)
    summary_text: str = Field(default="")


class DashboardData(BaseModel):
    dashboard_id: str = Field(description="仪表盘 ID")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    health_score: str = Field(description="健康评分 A/B/C/D/F")
    total_assets: int
    orphan_rate_pct: float = Field(description="孤儿率 %")
    ghost_rate_pct: float = Field(description="幽灵率 %")
    drift_rate_pct: float = Field(description="漂移率 %")
    by_type: dict[str, int] = Field(default_factory=dict)
    by_layer: dict[str, int] = Field(default_factory=dict)
    alerts: list[str] = Field(default_factory=list, description="告警信息")
    trend_orphan: list[float] = Field(default_factory=list, description="孤儿率趋势")
    trend_health: list[float] = Field(default_factory=list, description="健康评分趋势")
    last_reconciliation: str | None = Field(default=None, description="最近对账 ISO 时间戳")


class HealthScore(BaseModel):
    grade: HealthGrade = Field(description="健康等级 A-F")
    numeric: float = Field(description="0-100 数值评分")
    orphan_weight: float = Field(default=0.35)
    ghost_weight: float = Field(default=0.35)
    drift_weight: float = Field(default=0.20)
    recency_weight: float = Field(default=0.10)
    orphan_subscore: float = Field(default=0.0)
    ghost_subscore: float = Field(default=0.0)
    drift_subscore: float = Field(default=0.0)
    recency_subscore: float = Field(default=0.0)


class AssetLifecycleEvent(BaseModel):
    event_id: str = Field(description="事件 ID")
    event_type: str = Field(description="TIME_DECAY / ZERO_REF / DIR_CONVENTION")
    asset_path: str = Field(description="资产路径")
    from_status: AssetStatus
    to_status: AssetStatus
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    rule_detail: str = Field(default="", description="触发规则详情")
    auto_applied: bool = Field(default=True, description="是否自动应用")


class DuplicateGroup:
    """重复代码组 - 描述一组相似/重复的代码块.

    字段:
    - group_id: 组 ID
    - members: 成员列表 [(file_path, content_hash), ...]
    - similarity: 相似度 (0.0-1.0)
    - detection_method: 检测方法 (如 minhash_lsh)
    - confidence: 置信度 (0.0-100.0)
    """

    def __init__(
        self,
        group_id: str = "",
        members: list[tuple[str, str]] | None = None,
        similarity: float = 0.0,
        detection_method: str = "",
        confidence: float = 0.0,
    ):
        self.group_id = group_id
        self.members = members if members is not None else []
        self.similarity = similarity
        self.detection_method = detection_method
        self.confidence = confidence


__all__ = [
    "AssetLayer",
    "AssetLifecycleEvent",
    "AssetStatus",
    "AssetType",
    "ClassificationResult",
    "ClassifiedAsset",
    "DashboardData",
    "DriftEntry",
    "DriftType",
    "DuplicateGroup",
    "GhostEntry",
    "HealthGrade",
    "HealthScore",
    "Priority",
    "RawFileEntry",
    "ReconStatus",
    "ReconciliationReport",
    "RegistryEntry",
    "RenameEvent",
    "ScanResult",
    "UnifiedAssetIndex",
]
