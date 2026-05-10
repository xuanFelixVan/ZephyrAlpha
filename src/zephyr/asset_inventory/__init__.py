"""
asset_inventory — MOD-INF-026 · 资产盘点系统：发现→分类→登记→对账→生命周期
==============================================================================
蓝图 v0.3.0 · Phase 1 construction · P0 核心模块

五层架构
--------
  L1 Discovery      — 全量文件系统扫描
  L2 Classification — 基于类型映射的多维自动分类
  L3 Registration   — 24 注册表标准化读取与统一索引生成
  L4 Reconciliation — 磁盘 vs 注册表三方对账（孤儿/幽灵/漂移）
  L5 Lifecycle      — ITIL ITAM 生命周期自动化（TIME-DECAY/ZERO-REF/DIR-CONVENTION）

模块
----
  models.py           — Pydantic V2 共享数据模型（13 模型 + 6 枚举）
  scanner.py          — AssetDiscoveryScanner 全量文件系统扫描器
  classifier.py       — AssetClassifier 资产自动分类器
  reconciler.py       — ReconciliationEngine 注册表 vs 磁盘对账引擎
  dashboard.py        — AssetDashboard 资产健康仪表盘
  index_generator.py  — UnifiedAssetIndex 统一资产索引生成器
  lifecycle.py        — AssetLifecycle ITIL 生命周期自动化管理器

设计原则
--------
  - SSoT: unified_asset_index.yaml 是唯一事实来源
  - Safe-by-Default: 所有变更操作默认 --dry-run
  - Self-Referential: 盘点系统通过盘点自己来证明自己存在
  - RULE-ZERO~EIGHT 全合规
"""

from zephyr.asset_inventory import mcp_server, models, telemetry
from zephyr.asset_inventory.classifier import Classifier
from zephyr.asset_inventory.dashboard import Dashboard, KnowledgeTransferGate  # SRC-0040: + knowledge_transfer
from zephyr.asset_inventory.dependency import (
    DependencyEdge,
    DependencyExtractor,
    DependencyGraph,
    DependencyNode,
    build_dependency_graph,
    priority_from_dependency,
)
from zephyr.asset_inventory.index_generator import (  # SRC-0040: + schema_evolution
    IndexGenerator,
    MigrationPlan,
    SchemaEvolutionManager,
)
from zephyr.asset_inventory.lifecycle import Lifecycle
from zephyr.asset_inventory.metadata import (  # SRC-0040: git_metadata + multi_ide
    GitAssetMetadata,
    GitCommitInfo,
    GitMetadataExtractor,
    MultiIDERuleGenerator,
)
from zephyr.asset_inventory.reconciler import Reconciler
from zephyr.asset_inventory.registry_adapter import RegistryAdapter, RegistryManager, RegistryParseError
from zephyr.asset_inventory.scanner import (  # SRC-0040: + concurrent, security_enforcer
    ConcurrentScanner,
    Scanner,
    SecurityAccessLogger,
    SecurityFilter,
    merge_scans,
)
from zephyr.asset_inventory.telemetry import (  # SRC-0040: + notifications
    TELEMETRY,
    ConsoleChannel,
    NotificationChannel,
    NotificationManager,
    get_telemetry,
)
from zephyr.asset_inventory.trust_anchor import (  # SRC-0040: + emergency_bypass
    BypassManager,
    BypassState,
    TripleTrustAnchorGate,
    TrustAnchorResult,
    TrustLevel,
)

__all__ = [
    "Scanner",
    "Classifier",
    "Reconciler",
    "Dashboard",
    "IndexGenerator",
    "Lifecycle",
    "TELEMETRY",
    "get_telemetry",
    "ConcurrentScanner",
    "merge_scans",
    "RegistryManager",
    "RegistryAdapter",
    "RegistryParseError",
    "DependencyExtractor",
    "DependencyGraph",
    "DependencyNode",
    "DependencyEdge",
    "build_dependency_graph",
    "priority_from_dependency",
    "GitCommitInfo",
    "GitAssetMetadata",
    "GitMetadataExtractor",
    "TripleTrustAnchorGate",
    "TrustAnchorResult",
    "TrustLevel",
    "SecurityFilter",
    "SecurityAccessLogger",
    "BypassManager",
    "BypassState",
    "SchemaEvolutionManager",
    "MigrationPlan",
    "NotificationManager",
    "NotificationChannel",
    "ConsoleChannel",
    "MultiIDERuleGenerator",
    "KnowledgeTransferGate",
    "mcp_server",
    "models",
    "telemetry",
    "dependency",
    "registry_adapter",
    "metadata",
    "trust_anchor",
]
