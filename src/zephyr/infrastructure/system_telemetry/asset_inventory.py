# [BLUEPRINT] MOD-OPS-003 | docs/03_modules/_domain_infrastructure/asset_inventory/blueprint.md
# [MODULE] zephyr.infrastructure.system_telemetry.asset_inventory
# [DOMAIN] D_OPS
# [DEPENDENCIES] 无（协议核心纯内存；时钟注入，资产声明经注册接口进入）
# [CONSUMERS] 运行时装配批（统一资产索引装配 / 健康评分入面板 / 依赖图供运维拓扑消费）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 资产类型词表闭合(service|database|queue|model|strategy|config); asset_id 唯一非空; 禁止自依赖/空依赖项; 健康评分=元数据完整度/依赖连通/新鲜度三分量均值（各∈[0,1]，round6）; 孤儿=无依赖且无归属; 列表/图输出按 asset_id 确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure/asset_inventory/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AssetInventoryError(占位 ZA-OPS-UNREGISTERED-ASSET-INVENTORY)——空id/非法类型/重复注册/自依赖/空依赖项/未知资产时抛
# [TESTS] tests/infrastructure/system_telemetry/test_asset_inventory.py
# [A_module] module_id=MOD-OPS-003 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""AssetInventory — 资产盘点器（MOD-OPS-003）。

B9-11648（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-OPS-003，B9 OPS-06）：
unified_asset_index 统一资产索引（资产类型词表 + 注册表）+ 资产健康评分
（元数据完整度/依赖连通/新鲜度三分量）+ 孤儿率统计（无依赖/无归属资产
占比）+ 依赖图生成。

查重分工（蓝图 §0）：registry_governance=注册表治理（本件不重建注册框
架，只做运维视角资产盘点）；本件纯内存确定性，时钟注入，同输入必同输出。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "Asset",
    "AssetInventory",
    "AssetInventoryError",
    "AssetType",
    "DependencyGraph",
    "HealthScore",
    "OrphanStats",
]

#: 健康评分-元数据完整度必备键
REQUIRED_METADATA_KEYS: Final[tuple[str, ...]] = (
    "description",
    "version",
    "environment",
)


class AssetInventoryError(Exception):
    """资产盘点输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-OPS-UNREGISTERED-ASSET-INVENTORY。
    """


class AssetType(str, Enum):
    """资产类型（词表闭合）。"""

    SERVICE = "service"
    DATABASE = "database"
    QUEUE = "queue"
    MODEL = "model"
    STRATEGY = "strategy"
    CONFIG = "config"


@dataclass(frozen=True)
class Asset:
    """资产声明（统一索引条目，frozen）。"""

    asset_id: str
    asset_type: AssetType
    name: str
    owner: str | None
    metadata: Mapping[str, str]
    dependencies: tuple[str, ...]
    refreshed_at: datetime.datetime


@dataclass(frozen=True)
class HealthScore:
    """资产健康评分（三分量 + 均值，各 ∈ [0,1]，frozen）。"""

    asset_id: str
    metadata_completeness: float
    dependency_connectivity: float
    freshness: float
    total: float


@dataclass(frozen=True)
class OrphanStats:
    """孤儿率统计（无依赖且无归属资产占比，frozen）。"""

    total_assets: int
    orphan_count: int
    orphan_rate: float
    orphan_ids: tuple[str, ...]


@dataclass(frozen=True)
class DependencyGraph:
    """依赖图（节点/边均确定性排序；边仅含已注册端点，frozen）。"""

    nodes: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]


class AssetInventory:
    """统一资产索引（注册表 + 健康评分 + 孤儿率 + 依赖图）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        freshness_ttl_seconds: float = 3600.0,
    ) -> None:
        if freshness_ttl_seconds <= 0:
            raise AssetInventoryError(
                f"freshness_ttl_seconds 须 >0: {freshness_ttl_seconds}"
            )
        self._clock = clock or datetime.datetime.now
        self._ttl = float(freshness_ttl_seconds)
        self._assets: dict[str, Asset] = {}

    # ── 注册表 ───────────────────────────────────────────────────────────

    def register(self, asset: Asset) -> None:
        """登记资产：词表/唯一性/依赖声明校验（Fail-Closed）。"""
        if not isinstance(asset, Asset):
            raise AssetInventoryError(f"非法 asset: {type(asset)!r}")
        if not asset.asset_id:
            raise AssetInventoryError("asset_id 为空")
        if not isinstance(asset.asset_type, AssetType):
            raise AssetInventoryError(f"非法资产类型: {asset.asset_type!r}")
        if not asset.name:
            raise AssetInventoryError("name 为空")
        if asset.asset_id in self._assets:
            raise AssetInventoryError(f"asset_id 重复: {asset.asset_id!r}")
        for dep in asset.dependencies:
            if not dep:
                raise AssetInventoryError("依赖项 asset_id 为空")
            if dep == asset.asset_id:
                raise AssetInventoryError(f"自依赖非法: {asset.asset_id!r}")
        self._assets[asset.asset_id] = asset
        _log.info("资产登记: %s (%s)", asset.asset_id, asset.asset_type.value)

    def deregister(self, asset_id: str) -> None:
        """注销资产（未知 → Fail-Closed；他方悬挂依赖由连通度体现）。"""
        if asset_id not in self._assets:
            raise AssetInventoryError(f"未知资产: {asset_id!r}")
        del self._assets[asset_id]

    def get(self, asset_id: str) -> Asset:
        """单资产查询（未知 → Fail-Closed）。"""
        asset = self._assets.get(asset_id)
        if asset is None:
            raise AssetInventoryError(f"未知资产: {asset_id!r}")
        return asset

    def list_assets(self, asset_type: AssetType | None = None) -> list[Asset]:
        """资产列表（可按类型过滤；按 asset_id 确定性排序）。"""
        if asset_type is not None and not isinstance(asset_type, AssetType):
            raise AssetInventoryError(f"非法类型过滤: {asset_type!r}")
        out = [
            a for a in self._assets.values()
            if asset_type is None or a.asset_type is asset_type
        ]
        out.sort(key=lambda a: a.asset_id)
        return out

    # ── 健康评分（三分量） ───────────────────────────────────────────────

    def health_score(self, asset_id: str) -> HealthScore:
        """健康评分：元数据完整度 / 依赖连通 / 新鲜度 三分量均值。"""
        asset = self.get(asset_id)
        completeness = (
            sum(1 for k in REQUIRED_METADATA_KEYS if asset.metadata.get(k))
            / len(REQUIRED_METADATA_KEYS)
        )
        if not asset.dependencies:
            connectivity = 1.0
        else:
            connectivity = (
                sum(1 for d in asset.dependencies if d in self._assets)
                / len(asset.dependencies)
            )
        age = (self._clock() - asset.refreshed_at).total_seconds()
        if age <= self._ttl:
            freshness = 1.0
        elif age >= 2 * self._ttl:
            freshness = 0.0
        else:
            freshness = 1.0 - (age - self._ttl) / self._ttl
        completeness = round(completeness, 6)
        connectivity = round(connectivity, 6)
        freshness = round(freshness, 6)
        return HealthScore(
            asset_id=asset_id,
            metadata_completeness=completeness,
            dependency_connectivity=connectivity,
            freshness=freshness,
            total=round((completeness + connectivity + freshness) / 3, 6),
        )

    # ── 孤儿率统计 ───────────────────────────────────────────────────────

    def orphan_stats(self) -> OrphanStats:
        """孤儿率：无依赖且无归属（owner 空）资产占比（id 确定性排序）。"""
        orphans = tuple(sorted(
            a.asset_id
            for a in self._assets.values()
            if not a.dependencies and not (a.owner or "").strip()
        ))
        total = len(self._assets)
        return OrphanStats(
            total_assets=total,
            orphan_count=len(orphans),
            orphan_rate=round(len(orphans) / total, 6) if total else 0.0,
            orphan_ids=orphans,
        )

    # ── 依赖图 ───────────────────────────────────────────────────────────

    def dependency_graph(self) -> DependencyGraph:
        """依赖图：节点=全部注册资产；边=(资产, 依赖) 仅含已注册端点，均排序。"""
        nodes = tuple(sorted(self._assets))
        edges = tuple(sorted(
            (a.asset_id, dep)
            for a in self._assets.values()
            for dep in a.dependencies
            if dep in self._assets
        ))
        return DependencyGraph(nodes=nodes, edges=edges)
