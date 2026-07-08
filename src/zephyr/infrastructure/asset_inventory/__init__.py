# [A_module] module_id=MOD-INF_asset_inventory | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain-infra_ops/asset-inventory/blueprint.md
# [MODULE] zephyr.infrastructure.asset_inventory
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
asset-inventory — MOD-INF-026 · 资产盘点系统：发现->分类->登记->对账->生命周期
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
  - SSoT: unified-asset-index.yaml 是唯一事实来源
  - Safe-by-Default: 所有变更操作默认 --dry-run
  - Self-Referential: 盘点系统通过盘点自己来证明自己存在
  - RULE-ZERO~EIGHT 全合规
"""

__all__ = [
    "TELEMETRY",
    "BypassManager",
    "BypassState",
    "Classifier",
    "ConcurrentScanner",
    "ConsoleChannel",
    "Dashboard",
    "DependencyEdge",
    "DependencyExtractor",
    "DependencyGraph",
    "DependencyNode",
    "GitAssetMetadata",
    "GitCommitInfo",
    "GitMetadataExtractor",
    "IndexGenerator",
    "KnowledgeTransferGate",
    "Lifecycle",
    "MigrationPlan",
    "MultiIDERuleGenerator",
    "NotificationChannel",
    "NotificationManager",
    "Reconciler",
    "RegistryAdapter",
    "RegistryManager",
    "RegistryParseError",
    "Scanner",
    "SchemaEvolutionManager",
    "SecurityAccessLogger",
    "SecurityFilter",
    "TripleTrustAnchorGate",
    "TrustAnchorResult",
    "TrustLevel",
    "__main__",
    "build_dependency_graph",
    "classifier",
    "dashboard",
    "dependency",
    "get_telemetry",
    "index_generator",
    "lifecycle",
    "mcp_server",
    "merge_scans",
    "metadata",
    "models",
    "priority_from_dependency",
    "reconciler",
    "registry_adapter",
    "scanner",
    "telemetry",
    "trust_anchor",
]

_LAZY_IMPORTS = {
    "Classifier": ("zephyr.infrastructure.asset_inventory.classifier", "Classifier"),
    "Dashboard": ("zephyr.infrastructure.asset_inventory.dashboard", "Dashboard"),
    "KnowledgeTransferGate": ("zephyr.infrastructure.asset_inventory.dashboard", "KnowledgeTransferGate"),
    "DependencyEdge": ("zephyr.infrastructure.asset_inventory.dependency", "DependencyEdge"),
    "DependencyExtractor": ("zephyr.infrastructure.asset_inventory.dependency", "DependencyExtractor"),
    "DependencyGraph": ("zephyr.infrastructure.asset_inventory.dependency", "DependencyGraph"),
    "DependencyNode": ("zephyr.infrastructure.asset_inventory.dependency", "DependencyNode"),
    "build_dependency_graph": ("zephyr.infrastructure.asset_inventory.dependency", "build_dependency_graph"),
    "priority_from_dependency": ("zephyr.infrastructure.asset_inventory.dependency", "priority_from_dependency"),
    "IndexGenerator": ("zephyr.infrastructure.asset_inventory.index_generator", "IndexGenerator"),
    "MigrationPlan": ("zephyr.infrastructure.asset_inventory.index_generator", "MigrationPlan"),
    "SchemaEvolutionManager": ("zephyr.infrastructure.asset_inventory.index_generator", "SchemaEvolutionManager"),
    "Lifecycle": ("zephyr.infrastructure.asset_inventory.lifecycle", "Lifecycle"),
    "GitAssetMetadata": ("zephyr.infrastructure.asset_inventory.metadata", "GitAssetMetadata"),
    "GitCommitInfo": ("zephyr.infrastructure.asset_inventory.metadata", "GitCommitInfo"),
    "GitMetadataExtractor": ("zephyr.infrastructure.asset_inventory.metadata", "GitMetadataExtractor"),
    "MultiIDERuleGenerator": ("zephyr.infrastructure.asset_inventory.metadata", "MultiIDERuleGenerator"),
    "Reconciler": ("zephyr.infrastructure.asset_inventory.reconciler", "Reconciler"),
    "RegistryAdapter": ("zephyr.infrastructure.asset_inventory.registry_adapter", "RegistryAdapter"),
    "RegistryManager": ("zephyr.infrastructure.asset_inventory.registry_adapter", "RegistryManager"),
    "RegistryParseError": ("zephyr.infrastructure.asset_inventory.registry_adapter", "RegistryParseError"),
    "ConcurrentScanner": ("zephyr.infrastructure.asset_inventory.scanner", "ConcurrentScanner"),
    "Scanner": ("zephyr.infrastructure.asset_inventory.scanner", "Scanner"),
    "SecurityAccessLogger": ("zephyr.infrastructure.asset_inventory.scanner", "SecurityAccessLogger"),
    "SecurityFilter": ("zephyr.infrastructure.asset_inventory.scanner", "SecurityFilter"),
    "merge_scans": ("zephyr.infrastructure.asset_inventory.scanner", "merge_scans"),
    "TELEMETRY": ("zephyr.infrastructure.asset_inventory.telemetry", "TELEMETRY"),
    "ConsoleChannel": ("zephyr.infrastructure.asset_inventory.telemetry", "ConsoleChannel"),
    "NotificationChannel": ("zephyr.infrastructure.asset_inventory.telemetry", "NotificationChannel"),
    "NotificationManager": ("zephyr.infrastructure.asset_inventory.telemetry", "NotificationManager"),
    "get_telemetry": ("zephyr.infrastructure.asset_inventory.telemetry", "get_telemetry"),
    "BypassManager": ("zephyr.infrastructure.asset_inventory.trust_anchor", "BypassManager"),
    "BypassState": ("zephyr.infrastructure.asset_inventory.trust_anchor", "BypassState"),
    "TripleTrustAnchorGate": ("zephyr.infrastructure.asset_inventory.trust_anchor", "TripleTrustAnchorGate"),
    "TrustAnchorResult": ("zephyr.infrastructure.asset_inventory.trust_anchor", "TrustAnchorResult"),
    "TrustLevel": ("zephyr.infrastructure.asset_inventory.trust_anchor", "TrustLevel"),
    "logger": ("zephyr.infrastructure.asset_inventory.__main__", "logger"),
    "ROOT": ("zephyr.infrastructure.asset_inventory.__main__", "ROOT"),
    "main": ("zephyr.infrastructure.asset_inventory.__main__", "main"),
}

_SUBMODULES = [
    "classifier",
    "dashboard",
    "dependency",
    "index_generator",
    "lifecycle",
    "mcp_server",
    "metadata",
    "models",
    "reconciler",
    "registry_adapter",
    "scanner",
    "telemetry",
    "trust_anchor",
    "__main__",
]


def __getattr__(name):
    if name in _LAZY_IMPORTS:
        import importlib

        mod_path, attr_name = _LAZY_IMPORTS[name]
        mod = importlib.import_module(mod_path)
        value = getattr(mod, attr_name)
        globals()[name] = value
        return value
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(f"zephyr.data_governance.asset_inventory.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
