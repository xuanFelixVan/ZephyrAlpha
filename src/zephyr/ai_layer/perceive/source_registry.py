# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [MODULE] zephyr.ai_layer.perceive.source_registry
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT); PyYAML
# [CONSUMERS] zephyr.ai_layer.perceive.translator（source_scope 合法性校验）;
#             scripts/ai_layer/sync_ai_source_quota.py（配额行派生）;
#             结构校验=施工项 1 验收"12 源 URL/频率/配额/健康度/核验日齐"的机检面
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 配额真源=config/ai_source_registry.yaml（RULE-SSOT 规则=YAML），本模块只读不回写;
#              结构校验 fail-closed（缺字段/坏枚举/重复 slug/quota<1/URL 非法→SourceRegistryError）;
#              健康度墓碑不删除（retired 行保留，消费端按 health 过滤）;
#              总量闸 total_daily_cap 与每源配额独立生效（源配额之和可大于总量闸——总量闸是漏斗闸非加总闸）;
#              长尾候选不进 sources、不占配额（DESIGN §2.1"不入 v1"）;
#              校验失败一律就地 raise（不引公共断言助手——CloneGuard extract 级克隆教训，2026-09-23 本车道）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L1_perceive/DESIGN.md §2.1（源定稿表，改源先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 注册表缺文件→SourceRegistryError（fail-closed）; YAML 畸形→SourceRegistryError;
#                  单源缺必填字段/坏枚举/daily_quota<1/url 非 http(s)→SourceRegistryError（指名 slug）;
#                  重复 slug→SourceRegistryError; 长尾缺 url/note→SourceRegistryError
# [TESTS] tests/ai_layer/perceive/test_source_registry.py（真源 12 源全字段加载/枚举白名单/
#         缺字段指名报错/坏枚举报错/quota<1 报错/重复 slug 报错/长尾不入配额/总量闸读数）
# [TTL] permanent
"""source_registry — L1 外部源注册表加载与结构校验器（施工项 1 的机检面）。

设计真源：``docs/_working/ai_layer_vision/L1_perceive/DESIGN.md`` §2.1（12 源·四轨+治理轨定稿）。
配额真源=``config/ai_source_registry.yaml``；本模块是该 YAML 的唯一程序化读取入口——
加载即全量结构校验（fail-closed），保证"12 源 URL/频率/配额/健康度/核验日齐"这条
验收标准在任何消费方（配额同步器/翻译器）读数前已被机检。

本模块零网络行为：只做文件读取、解析、校验、派生只读视图。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.shared.io.paths import REPO_ROOT

log = logging.getLogger(__name__)

__all__: Final = [
    "DEFAULT_REGISTRY_PATH",
    "FREQUENCIES",
    "HEALTH_STATES",
    "LONGTAIL_REQUIRED_FIELDS",
    "QUOTA_GOVERNANCE_REQUIRED_KEYS",
    "SOURCE_REQUIRED_FIELDS",
    "SOURCE_TRACKS",
    "SourceRecord",
    "SourceRegistry",
    "SourceRegistryError",
    "load_source_registry",
]

DEFAULT_REGISTRY_PATH: Final = REPO_ROOT / "config" / "ai_source_registry.yaml"

SOURCE_TRACKS: Final[frozenset[str]] = frozenset(
    {"github", "academic", "chinese_community", "baseline", "governance"}
)
FREQUENCIES: Final[frozenset[str]] = frozenset({"daily", "weekly", "monthly", "semiannual"})
HEALTH_STATES: Final[frozenset[str]] = frozenset({"active", "degraded", "blocked", "retired"})

SOURCE_REQUIRED_FIELDS: Final[tuple[str, ...]] = (
    "slug",
    "track",
    "url",
    "fetch",
    "frequency",
    "daily_quota",
    "health",
    "last_verified",
    "basis",
)
LONGTAIL_REQUIRED_FIELDS: Final[tuple[str, ...]] = ("slug", "url", "note")
QUOTA_GOVERNANCE_REQUIRED_KEYS: Final[tuple[str, ...]] = (
    "total_daily_cap",
    "per_source_floor",
    "demotion",
)


class SourceRegistryError(ValueError):
    """源注册表结构/内容不合规（fail-closed，绝不带病读数）。

    :param details: 敏感上下文（url/路径等）走 details 不进消息文本（5.99.20）。
    """

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}


@dataclass(frozen=True)
class SourceRecord:
    """注册表内一个外部源（只读快照形态）。"""

    slug: str
    track: str
    url: str
    fetch: str
    frequency: str
    daily_quota: int
    health: str
    last_verified: str
    basis: str
    notes: str = ""


@dataclass(frozen=True)
class LongtailCandidate:
    """长尾待核验源（不入 v1 配额，核验通过前不进 sources）。"""

    slug: str
    url: str
    note: str


@dataclass(frozen=True)
class SourceRegistry:
    """已校验的源注册表视图（只读）。"""

    sources: tuple[SourceRecord, ...]
    longtail: tuple[LongtailCandidate, ...]
    total_daily_cap: int
    per_source_floor: int
    demotion: dict[str, Any] = field(default_factory=dict)
    path: Path = DEFAULT_REGISTRY_PATH

    def by_slug(self) -> dict[str, SourceRecord]:
        """slug → 源记录（含 retired 墓碑行——消费端自行按 health 过滤）。"""
        return {s.slug: s for s in self.sources}

    def active_slugs(self) -> tuple[str, ...]:
        """health=active 的 slug 元组（节拍扫的默认 source_scope）。"""
        return tuple(s.slug for s in self.sources if s.health == "active")

    def quota_of(self, slug: str) -> int | None:
        """按 slug 查每日配额；未知 slug 返回 None（调用方决定 fail 方向）。"""
        record = self.by_slug().get(slug)
        return None if record is None else record.daily_quota


def _validate_source(raw: dict[str, Any], index: int) -> SourceRecord:
    """单源结构校验（缺字段/坏枚举/配额/URL 逐项机检，报错指名 slug）。"""
    slug_hint = str(raw.get("slug") or f"<no-slug@{index}>")
    missing = [k for k in SOURCE_REQUIRED_FIELDS if k not in raw or raw.get(k) in (None, "")]
    if missing:
        raise SourceRegistryError(f"source[{slug_hint}] 缺必填字段: {','.join(missing)}")
    slug = str(raw["slug"])
    if str(raw["track"]) not in SOURCE_TRACKS:
        raise SourceRegistryError(
            f"source[{slug}] 非法 track: {raw['track']}（白名单={sorted(SOURCE_TRACKS)}）"
        )
    if str(raw["frequency"]) not in FREQUENCIES:
        raise SourceRegistryError(
            f"source[{slug}] 非法 frequency: {raw['frequency']}（白名单={sorted(FREQUENCIES)}）"
        )
    if str(raw["health"]) not in HEALTH_STATES:
        raise SourceRegistryError(
            f"source[{slug}] 非法 health: {raw['health']}（白名单={sorted(HEALTH_STATES)}）"
        )
    quota = raw["daily_quota"]
    if not isinstance(quota, int) or isinstance(quota, bool) or quota < 1:
        raise SourceRegistryError(f"source[{slug}] daily_quota 必须为 >=1 的整数（禁清零），实为 {quota!r}")
    url = str(raw["url"])
    if not url.startswith(("http://", "https://")):
        raise SourceRegistryError(f"source[{slug}] url 非 http(s)", details={"url": url})
    return SourceRecord(
        slug=slug,
        track=str(raw["track"]),
        url=url,
        fetch=str(raw["fetch"]),
        frequency=str(raw["frequency"]),
        daily_quota=int(quota),
        health=str(raw["health"]),
        last_verified=str(raw["last_verified"]),
        basis=str(raw["basis"]),
        notes=str(raw.get("notes") or ""),
    )


def _validate_longtail(raw: dict[str, Any], index: int) -> LongtailCandidate:
    missing = [k for k in LONGTAIL_REQUIRED_FIELDS if k not in raw or raw.get(k) in (None, "")]
    if missing:
        raise SourceRegistryError(f"longtail[{index}] 缺必填字段: {','.join(missing)}")
    return LongtailCandidate(slug=str(raw["slug"]), url=str(raw["url"]), note=str(raw["note"]))


def _read_registry_yaml(registry_path: Path) -> dict[str, Any]:
    """load_source_registry 内联逻辑搬移：存在性+YAML 解析+顶层映射三道 fail-closed 闸。"""
    if not registry_path.exists():
        raise SourceRegistryError("源注册表缺文件", details={"path": str(registry_path)})
    try:
        raw = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SourceRegistryError(f"源注册表 YAML 畸形: {exc}", details={"path": str(registry_path)}) from exc
    if not isinstance(raw, dict):
        raise SourceRegistryError("源注册表顶层必须是映射", details={"path": str(registry_path)})
    return raw


def _validated_sources(raw: dict[str, Any]) -> tuple[SourceRecord, ...]:
    """load_source_registry 内联逻辑搬移：sources 全量单源校验+slug 查重。"""
    raw_sources = raw.get("sources")
    if not isinstance(raw_sources, list) or not raw_sources:
        raise SourceRegistryError("sources 缺失或为空（12 源定稿不可为空）")
    records = tuple(_validate_source(item, i) for i, item in enumerate(raw_sources))
    slugs = [r.slug for r in records]
    duplicated = sorted({s for s in slugs if slugs.count(s) > 1})
    if duplicated:
        raise SourceRegistryError(f"slug 重复: {duplicated}")
    return records


def _validated_longtail(raw: dict[str, Any]) -> tuple[LongtailCandidate, ...]:
    """load_source_registry 内联逻辑搬移：longtail_candidates 列表校验+逐项校验。"""
    raw_longtail = raw.get("longtail_candidates") or []
    if not isinstance(raw_longtail, list):
        raise SourceRegistryError("longtail_candidates 必须是列表")
    return tuple(_validate_longtail(item, i) for i, item in enumerate(raw_longtail))


def _validated_quota_governance(raw: dict[str, Any]) -> dict[str, Any]:
    """load_source_registry 内联逻辑搬移：quota_governance 必填键+total_daily_cap 校验。"""
    gov = raw.get("quota_governance") or {}
    missing_gov = [k for k in QUOTA_GOVERNANCE_REQUIRED_KEYS if k not in gov]
    if missing_gov:
        raise SourceRegistryError(f"quota_governance 缺键: {','.join(missing_gov)}")
    total_cap = gov["total_daily_cap"]
    if not isinstance(total_cap, int) or total_cap < 1:
        raise SourceRegistryError(
            f"quota_governance.total_daily_cap 必须 >=1 的整数，实为 {total_cap!r}"
        )
    return gov


def load_source_registry(path: Path | str | None = None) -> SourceRegistry:
    """加载并全量校验源注册表（fail-closed；测试传 tmp_path 注入 fixture）。"""
    registry_path = Path(path) if path else DEFAULT_REGISTRY_PATH
    raw = _read_registry_yaml(registry_path)
    records = _validated_sources(raw)
    longtail = _validated_longtail(raw)
    gov = _validated_quota_governance(raw)

    registry = SourceRegistry(
        sources=records,
        longtail=longtail,
        total_daily_cap=int(gov["total_daily_cap"]),
        per_source_floor=int(gov["per_source_floor"]),
        demotion=dict(gov["demotion"]) if isinstance(gov["demotion"], dict) else {},
        path=registry_path,
    )
    log.info(
        "源注册表加载完成: %s（%d 源，%d 长尾，总量闸=%d/日）",
        registry_path, len(registry.sources), len(registry.longtail), registry.total_daily_cap,
    )
    return registry
