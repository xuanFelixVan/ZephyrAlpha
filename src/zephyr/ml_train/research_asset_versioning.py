# [BLUEPRINT] MOD-ML-022 | docs/03_modules/_domain_machine_learning_train/research_asset_versioning/blueprint.md
# [MODULE] zephyr.ml_train.research_asset_versioning
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] 无（纯内存/DI；clock 注入；SemVer 校验 stdlib re；语义旁挂 reporting.report_version_manager）
# [CONSUMERS] 运行时装配批（因子/模型/策略登记口绑定 / 跨项目复用登记路由装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 资产类别词表闭合(factor|model|strategy); SemVer 严格 major.minor.patch(禁前导零); 版本记录写后不可改(重复登记拒绝); 指标键非空且值须数值; 跨项目复用须异项目且来源项目与登记一致; 检索结果确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_machine_learning_train/research_asset_versioning/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AssetVersionError(占位 ZA-MLT-UNREGISTERED-ASSET-VERSION)——非法类别/非法 SemVer/重复版本/非法指标/未知版本/复用项目不符时抛
# [TESTS] tests/ml_train/test_research_asset_versioning.py
# [A_module] module_id=MOD-ML-022 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ResearchAssetVersioning — 研究资产版本化管理器（MOD-ML-022）。

B13-04341（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-030，A3 D-RESEARCH-18）：
**因子/模型/策略三类统一 SemVer**（major.minor.patch 严格校验，禁前导零）
+ **不可变版本记录**（写后不可改，重复登记拒绝）
+ **复用索引**（按资产/版本/指标三维检索，确定性排序）
+ **跨项目复用登记**（异项目 + 来源项目一致性校验，留痕）。

分工：report_version_manager=报告件版本；本件=研究资产（因子/模型/策略）
版本与复用协议面，纯内存登记簿。
"""

from __future__ import annotations

import datetime
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "AssetKind",
    "AssetVersion",
    "AssetVersionError",
    "ResearchAssetVersioning",
    "ReuseRecord",
    "parse_semver",
]

#: 严格 SemVer（major.minor.patch，禁前导零）
_SEMVER_RE: Final = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")


class AssetVersionError(Exception):
    """研究资产版本化输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-MLT-UNREGISTERED-ASSET-VERSION。
    """


class AssetKind(str, Enum):
    """研究资产类别（词表闭合）。"""

    FACTOR = "factor"
    MODEL = "model"
    STRATEGY = "strategy"


def parse_semver(version: str) -> tuple[int, int, int]:
    """SemVer 解析（非法 Fail-Closed）。"""
    if not isinstance(version, str):
        raise AssetVersionError(f"非法 SemVer: {version!r}（须字符串 major.minor.patch）")
    m = _SEMVER_RE.fullmatch(version)
    if m is None:
        raise AssetVersionError(f"非法 SemVer: {version!r}（须 major.minor.patch，禁前导零）")
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


@dataclass(frozen=True)
class AssetVersion:
    """资产版本记录（frozen；写后不可改）。"""

    asset_id: str
    kind: AssetKind
    version: str
    metrics: dict
    project: str
    note: str
    registered_at: datetime.datetime

    @property
    def semver(self) -> tuple[int, int, int]:
        """SemVer 三元组（登记期已校验）。"""
        return parse_semver(self.version)


@dataclass(frozen=True)
class ReuseRecord:
    """跨项目复用登记（frozen，留痕）。"""

    reuse_id: str
    asset_id: str
    version: str
    from_project: str
    to_project: str
    note: str
    registered_at: datetime.datetime


class ResearchAssetVersioning:
    """研究资产版本化管理器（登记 + 不可变记录 + 三维索引 + 复用登记）。"""

    def __init__(self, *, clock: Callable[[], datetime.datetime] | None = None) -> None:
        self._clock = clock or datetime.datetime.now
        self._versions: dict[tuple[str, str], AssetVersion] = {}
        self._reuses: list[ReuseRecord] = []
        self._reuse_counter = 0

    # ── 版本登记（不可变记录） ──────────────────────────────────────────────

    def register_version(
        self,
        kind: AssetKind,
        asset_id: str,
        version: str,
        metrics: Mapping,
        project: str,
        note: str = "",
    ) -> AssetVersion:
        """登记资产版本：类别/SemVer/指标校验 + (asset_id, version) 唯一。"""
        if not isinstance(kind, AssetKind):
            raise AssetVersionError(f"非法资产类别: {kind!r}（词表闭合 factor|model|strategy）")
        if not asset_id:
            raise AssetVersionError("asset_id 为空")
        if not project:
            raise AssetVersionError("project 为空")
        parse_semver(version)
        if not isinstance(metrics, Mapping):
            raise AssetVersionError("metrics 非映射")
        for key, value in metrics.items():
            if not key:
                raise AssetVersionError("metrics 存在空指标键")
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise AssetVersionError(f"metrics[{key!r}] 非数值: {value!r}")
        key = (asset_id, version)
        if key in self._versions:
            raise AssetVersionError(
                f"版本记录不可变: {asset_id!r}@{version!r} 已登记（重复登记拒绝）"
            )
        rec = AssetVersion(
            asset_id=asset_id,
            kind=kind,
            version=version,
            metrics=dict(metrics),
            project=project,
            note=note,
            registered_at=self._clock(),
        )
        self._versions[key] = rec
        _log.info("资产版本登记: %s %s@%s (%s)", kind.value, asset_id, version, project)
        return rec

    # ── 三维复用索引（资产/版本/指标） ──────────────────────────────────────

    def get_version(self, asset_id: str, version: str) -> AssetVersion:
        """按资产+版本检索（未知 Fail-Closed）。"""
        rec = self._versions.get((asset_id, version))
        if rec is None:
            raise AssetVersionError(f"未知资产版本: {asset_id!r}@{version!r}")
        return rec

    def versions_of(self, asset_id: str, kind: AssetKind | None = None) -> tuple[AssetVersion, ...]:
        """按资产检索版本序列（SemVer 降序；可按类别过滤）。"""
        if kind is not None and not isinstance(kind, AssetKind):
            raise AssetVersionError(f"非法资产类别: {kind!r}")
        out = [
            rec for (aid, _), rec in self._versions.items()
            if aid == asset_id and (kind is None or rec.kind is kind)
        ]
        out.sort(key=lambda r: r.semver, reverse=True)
        return tuple(out)

    def latest(self, asset_id: str) -> AssetVersion:
        """资产最新版本（SemVer 最大；未知资产 Fail-Closed）。"""
        versions = self.versions_of(asset_id)
        if not versions:
            raise AssetVersionError(f"未知资产: {asset_id!r}")
        return versions[0]

    def list_assets(self, kind: AssetKind | None = None) -> tuple[str, ...]:
        """资产清单（字典序确定性；可按类别过滤）。"""
        if kind is not None and not isinstance(kind, AssetKind):
            raise AssetVersionError(f"非法资产类别: {kind!r}")
        ids = {
            rec.asset_id for rec in self._versions.values()
            if kind is None or rec.kind is kind
        }
        return tuple(sorted(ids))

    def search_by_metric(
        self,
        metric_key: str,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> tuple[AssetVersion, ...]:
        """按指标区间检索（按 指标值降序, asset_id, SemVer 确定性排序）。"""
        if not metric_key:
            raise AssetVersionError("metric_key 为空")
        for bound, name in ((min_value, "min_value"), (max_value, "max_value")):
            if bound is not None and (isinstance(bound, bool) or not isinstance(bound, (int, float))):
                raise AssetVersionError(f"{name} 非数值: {bound!r}")
        if min_value is None and max_value is None:
            raise AssetVersionError("指标检索须至少一端界")
        if min_value is not None and max_value is not None and min_value > max_value:
            raise AssetVersionError(f"指标区间非法: [{min_value}, {max_value}]")
        out = []
        for rec in self._versions.values():
            value = rec.metrics.get(metric_key)
            if value is None:
                continue
            if min_value is not None and value < min_value:
                continue
            if max_value is not None and value > max_value:
                continue
            out.append(rec)
        out.sort(key=lambda r: (-r.metrics[metric_key], r.asset_id, r.semver))
        return tuple(out)

    # ── 跨项目复用登记 ──────────────────────────────────────────────────────

    def register_reuse(
        self,
        asset_id: str,
        version: str,
        from_project: str,
        to_project: str,
        note: str = "",
    ) -> ReuseRecord:
        """跨项目复用登记：版本须已登记，异项目且来源项目与登记一致。"""
        rec = self.get_version(asset_id, version)
        if not from_project:
            raise AssetVersionError("from_project 为空")
        if not to_project:
            raise AssetVersionError("to_project 为空")
        if from_project != rec.project:
            raise AssetVersionError(
                f"来源项目不符: 登记项目 {rec.project!r}，声明 {from_project!r}"
            )
        if to_project == from_project:
            raise AssetVersionError("跨项目复用须异项目（to_project == from_project）")
        self._reuse_counter += 1
        reuse = ReuseRecord(
            reuse_id=f"reuse-{self._reuse_counter:04d}",
            asset_id=asset_id,
            version=version,
            from_project=from_project,
            to_project=to_project,
            note=note,
            registered_at=self._clock(),
        )
        self._reuses.append(reuse)
        _log.info("跨项目复用: %s@%s %s -> %s", asset_id, version, from_project, to_project)
        return reuse

    def reuses_of(self, asset_id: str, version: str | None = None) -> tuple[ReuseRecord, ...]:
        """资产复用记录（按 (registered_at, reuse_id) 确定性排序；可按版本过滤）。"""
        out = [
            r for r in self._reuses
            if r.asset_id == asset_id and (version is None or r.version == version)
        ]
        out.sort(key=lambda r: (r.registered_at, r.reuse_id))
        return tuple(out)
