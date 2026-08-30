# [BLUEPRINT] MOD-DATA_GOV-014 | docs/03_modules/_domain_data_governance/asset_auto_discovery/blueprint.md
# [MODULE] zephyr.data_governance.asset_auto_discovery
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES] 无（纯内存；三类 scanner/registry_sink/clock 全注入；指纹 sha256 stdlib）
# [CONSUMERS] 运行时装配批（CH表/因子注册表/信号注册表 scanner 绑定 / metadata_registry 注册回调）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 资产类型词表闭合(clickhouse_table|factor|signal); 每类型 scanner 唯一; 指纹与属性字典序无关; 指纹 diff 仅变更推注册表(added/updated); 报告 added/updated/unchanged/cards 按 asset_id 确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data_governance/asset_auto_discovery/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AssetDiscoveryError(占位 ZA-DATA-UNREGISTERED-ASSET-DISCOVERY)——词表外类型/非法scanner/重复注册/空asset_id/无scanner运行/scanner或sink异常时抛
# [TESTS] tests/data_governance/test_asset_auto_discovery.py
# [A_module] module_id=MOD-DATA_GOV-014 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



asset_auto_discovery — 数据资产自动发现器（MOD-DATA_GOV-014）。

B10-02326（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATGOV-011，A1 M8-NEW-07）：
资产自动发现——扫描源注册（**ClickHouse 表 / 因子注册表 / 信号注册表**三类
scanner 注入）+ 自动生成**数据资产卡片**（asset_id/类型/owner/更新频率/质
量分默认）+ 入 metadata_registry（注入注册表回调）+ 定时增量更新（**指纹
diff 只更新变更**）。

查重分工（蓝图 §0）：infrastructure/asset_inventory=资产台账本体（本件=发
现与增量推送协调，不重建台账）；core/metadata_registry=元数据注册实现（本
件仅注入其注册回调）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: asset_auto_discovery.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: registry_sink 参数
#   fields: 参数 registry_sink（无注解）
#   code: asset_auto_discovery.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: default_quality_score 参数
#   fields: 参数 default_quality_score（无注解）
#   code: asset_auto_discovery.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AssetAutoDiscovery
#   name_en: AssetAutoDiscovery
#   intro: 资产自动发现器（scanner 注册 + 卡片生成 + 指纹 diff 增量推送）。
#   desc: 资产自动发现器（scanner 注册 + 卡片生成 + 指纹 diff 增量推送）。；公共方法（定义序）: register_scanner, fingerprint_of, run；源码 L143-L248
#   inputs: clock registry_sink default_quality_score
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: AssetAutoDiscovery
#   downstream: 运行时装配批（CH表/因子注册表/信号注册表 scanner 绑定 / metadata_registry 注册回调）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import hashlib
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "AssetAutoDiscovery",
    "AssetCard",
    "AssetDiscoveryError",
    "AssetType",
    "DiscoveryReport",
    "RawAssetInfo",
]

#: scanner 协议：零参返回原始资产信息序列
ScannerFn = Callable[[], Iterable["RawAssetInfo"]]


class AssetDiscoveryError(Exception):
    """资产自动发现登记/运行输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DATA-UNREGISTERED-ASSET-DISCOVERY。
    """


class AssetType(str, Enum):
    """扫描源资产类型词表（闭合，三类）。"""

    CLICKHOUSE_TABLE = "clickhouse_table"
    FACTOR = "factor"
    SIGNAL = "signal"


@dataclass(frozen=True)
class RawAssetInfo:
    """scanner 上报的原始资产信息（frozen）。"""

    asset_id: str
    owner: str = ""
    update_frequency: str = ""
    attributes: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class AssetCard:
    """数据资产卡片（asset_id/类型/owner/更新频率/质量分/指纹，frozen）。"""

    asset_id: str
    asset_type: AssetType
    owner: str
    update_frequency: str
    quality_score: float
    fingerprint: str
    discovered_at: datetime.datetime


@dataclass(frozen=True)
class DiscoveryReport:
    """发现运行报告（added/updated/unchanged + 全量卡片，frozen，各自排序）。"""

    run_at: datetime.datetime
    added: tuple[str, ...]
    updated: tuple[str, ...]
    unchanged: tuple[str, ...]
    cards: tuple[AssetCard, ...]


class AssetAutoDiscovery:
    """资产自动发现器（scanner 注册 + 卡片生成 + 指纹 diff 增量推送）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        registry_sink: Callable[[AssetCard], None] | None = None,
        default_quality_score: float = 0.5,
    ) -> None:
        if not 0.0 <= default_quality_score <= 1.0:
            raise AssetDiscoveryError(f"default_quality_score 越界[0,1]: {default_quality_score}")
        self._clock = clock or datetime.datetime.now
        self._sink = registry_sink
        self._default_quality = float(default_quality_score)
        self._scanners: dict[AssetType, ScannerFn] = {}
        self._cards: dict[str, AssetCard] = {}

    # ── scanner 注册 ──────────────────────────────────────────────────────

    def register_scanner(self, asset_type: AssetType, scanner: ScannerFn) -> None:
        """注册扫描源：类型词表闭合；scanner 可调用；每类型唯一。"""
        if not isinstance(asset_type, AssetType):
            raise AssetDiscoveryError(f"词表外资产类型: {asset_type!r}")
        if not callable(scanner):
            raise AssetDiscoveryError("scanner 不可调用")
        if asset_type in self._scanners:
            raise AssetDiscoveryError(f"scanner 重复注册: {asset_type.value}")
        self._scanners[asset_type] = scanner

    # ── 指纹 ─────────────────────────────────────────────────────────────

    @staticmethod
    def fingerprint_of(raw: RawAssetInfo) -> str:
        """资产指纹（sha256；与 attributes 字典序无关）。"""
        h = hashlib.sha256()
        h.update(f"{raw.asset_id}|{raw.owner}|{raw.update_frequency}\n".encode())
        for key in sorted(raw.attributes):
            h.update(f"{key}={raw.attributes[key]}\n".encode())
        return h.hexdigest()

    # ── 发现运行 ──────────────────────────────────────────────────────────

    def run(self) -> DiscoveryReport:
        """执行一轮发现：扫描 → 卡片生成 → 指纹 diff → 仅变更推注册表。"""
        if not self._scanners:
            raise AssetDiscoveryError("无 scanner 注册（Fail-Closed 不空跑）")
        now = self._clock()
        cards: list[AssetCard] = []
        for asset_type in sorted(self._scanners, key=lambda t: t.value):
            scanner = self._scanners[asset_type]
            try:
                raws = list(scanner())
            except AssetDiscoveryError:
                raise
            except Exception as exc:  # noqa: BLE001 — scanner 异常 Fail-Closed 包装
                raise AssetDiscoveryError(f"scanner {asset_type.value} 扫描失败: {exc}") from exc
            for raw in raws:
                if not raw.asset_id:
                    raise AssetDiscoveryError(f"空 asset_id: {raw!r}")
                cards.append(
                    AssetCard(
                        asset_id=raw.asset_id,
                        asset_type=asset_type,
                        owner=raw.owner,
                        update_frequency=raw.update_frequency,
                        quality_score=self._default_quality,
                        fingerprint=self.fingerprint_of(raw),
                        discovered_at=now,
                    )
                )
        cards.sort(key=lambda c: c.asset_id)

        added: list[str] = []
        updated: list[str] = []
        unchanged: list[str] = []
        changed_cards: list[AssetCard] = []
        for card in cards:
            old = self._cards.get(card.asset_id)
            if old is None:
                added.append(card.asset_id)
                changed_cards.append(card)
            elif old.fingerprint != card.fingerprint:
                updated.append(card.asset_id)
                changed_cards.append(card)
            else:
                unchanged.append(card.asset_id)

        if self._sink is not None:
            for card in changed_cards:
                try:
                    self._sink(card)
                except AssetDiscoveryError:
                    raise
                except Exception as exc:  # noqa: BLE001 — 注册表回调异常 Fail-Closed
                    raise AssetDiscoveryError(f"registry_sink 注册失败: {card.asset_id}: {exc}") from exc

        self._cards = {c.asset_id: c for c in cards}
        _log.info("资产发现: +%d ~%d =%d", len(added), len(updated), len(unchanged))
        return DiscoveryReport(
            run_at=now,
            added=tuple(added),
            updated=tuple(updated),
            unchanged=tuple(unchanged),
            cards=tuple(cards),
        )
