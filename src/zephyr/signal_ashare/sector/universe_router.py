# [BLUEPRINT] MOD-SIG-161 | docs/04_research_records/cross_domain/condaxis/sector/1_universe_router.md §2-§4（施工裁定·P1 边界 2026-10-13）
# [MODULE] zephyr.signal_ashare.sector.universe_router
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] config/sector_universe_router.yaml（B_yaml 声明态规则真源，路径可注入）；stdlib only（re/dataclasses/pathlib/yaml 解析经传入 payload 时零依赖）
# [CONSUMERS] 条件轴战役验证班面板装配件（7_validation_class.md §2 新建件）；板块线五件套信号件口径声明引用；禁表名直连——表一律经 TableRegistry.table(category_id)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 纯函数零副作用零 I/O（除显式 load_sector_universe_router 读盘）；判别式真源=YAML routing_rules（自上而下首命中），代码零硬编码板块码；880001-880009 市场统计指数 action=exclude 防大盘双计；6 位数字与个股码同形→无 source_hint 判 unknown 不猜（fail-loud）；申万身份=(industry_level, industry_sw) 无数码判别；schema_version 不识别→ValueError（fail-closed）；frozen dataclass JSON 可序列化；禁 datetime.now()/time.time()
# [MODIFY-GUARD] docs/04_research_records/cross_domain/condaxis/sector/1_universe_router.md（挖矿裁定：施工）；config/sector_universe_router.yaml（判别式变更须同批改 YAML+测试）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 配置缺 routing_rules/calibers/decision→ValueError；regex 编译失败→ValueError；schema_version 不在 SUPPORTED→ValueError；未知 family 引用→ValueError；route_sector_code 对空码/非 str→ValueError
# [TESTS] tests/zephyr/signal_ashare/sector/test_universe_router.py
# [A_module] module_id=MOD-SIG-161 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-161 — 板块口径路由薄件（三口径唯一化，CONDAXIS-CAMPAIGN 板块线环节⓪）。

问题（挖矿册 1_universe_router.md）：通达信 880/申万/概念三套板块口径并存，六套
数字（729/727/582/86/90/376）六个口径源，无一处声明谁是主口径——D 族"两宏观轴
21% 分歧"事故的板块版温床。

裁定（P1 边界 2026-10-13）：主口径=申万（S1 默认先行，对齐 ig_* 图谱）；
通达信 880=盘中快照辅助；概念=事件标签层。降级序 shenwan_l1→tdx880→ths881。

本件只做两件事（薄）：
1. parse/universe 配置装载（fail-closed 校验 config/sector_universe_router.yaml）；
2. 板块代码→口径族判别（route_sector_code：YAML routing_rules 自上而下首命中，
   带交易所后缀剥离、市场统计指数剔除、881 同号不同义与 6 位歧义码 fail-loud）。

非目标：不查库、不取数、不建映射表（跨口径桥经 sector_code_bridge 等既有件）。


# [ALGO_FLOW] external: docs/03_modules/_domain_signal/algo_flow/universe_router.yaml
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

import yaml

__all__: Final = [
    "SUPPORTED_SCHEMA_VERSION",
    "DEFAULT_CONFIG_PATH",
    "RouteRule",
    "CaliberSpec",
    "SectorUniverseRouterConfig",
    "RouteVerdict",
    "parse_sector_universe_config",
    "load_sector_universe_router",
    "route_sector_code",
    "primary_universe",
]

#: 支持的配置 schema 版本（不识别即 fail-closed）
SUPPORTED_SCHEMA_VERSION: tuple[str, ...] = ("1.0.0",)

#: 默认配置真源路径（仓库根相对）
DEFAULT_CONFIG_PATH: Final[Path] = Path("config/sector_universe_router.yaml")

#: 交易所后缀剥离（880001.SH → 880001；SC 表内码可能带后缀）
_EXCHANGE_SUFFIX_RE: re.Pattern[str] = re.compile(r"\.(SH|SZ|BJ)$", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class RouteRule:
    """判别式单行（yaml routing_rules 行映射）。"""

    pattern: re.Pattern[str]
    family: str
    role: str
    action: str = "route"  # route / exclude
    note: str = ""


@dataclass(frozen=True, slots=True)
class CaliberSpec:
    """单口径声明（yaml calibers.* 映射的薄投影）。"""

    family: str
    role: str
    category_ids: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SectorUniverseRouterConfig:
    """路由配置（装载校验后的只读视图）。"""

    primary_caliber: str
    roles: Mapping[str, str]
    degradation_order: tuple[str, ...]
    calibers: Mapping[str, CaliberSpec]
    rules: tuple[RouteRule, ...]
    shenwan_levels: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RouteVerdict:
    """单板块代码判定（JSON 可序列化）。"""

    code: str
    family: str  # shenwan/tdx880/ths881/concept/ambiguous/unknown
    role: str
    action: str  # route / exclude / unknown
    match_via: str = "pattern"  # pattern / source_hint / none
    note: str = ""


@dataclass(frozen=True, slots=True)
class UniverseSpec:
    """主口径宇宙解析结果。"""

    primary_caliber: str
    degradation_order: tuple[str, ...]
    category_ids: tuple[str, ...] = field(default_factory=tuple)


def _require_str(payload: Mapping[str, Any], key: str, ctx: str) -> str:
    val = payload.get(key)
    if not isinstance(val, str) or not val.strip():
        raise ValueError(f"{ctx}: 字段 {key} 缺失或非非空字符串")
    return val


def parse_sector_universe_config(payload: Mapping[str, Any]) -> SectorUniverseRouterConfig:
    """配置载荷 → 路由配置（fail-closed）。

    Args:
        payload: yaml 解析结果（须含 schema_version/decision/calibers/routing_rules）。

    Returns:
        校验后的只读配置。

    Raises:
        ValueError: 版本不识别/结构缺失/regex 非法/family 引用未声明。
    """
    if not isinstance(payload, Mapping):
        raise ValueError(f"载荷非法（须映射）: {type(payload).__name__}")
    version = _require_str(payload, "schema_version", "sector_universe_router")
    if version not in SUPPORTED_SCHEMA_VERSION:
        raise ValueError(f"schema_version 不受支持: {version}（支持: {SUPPORTED_SCHEMA_VERSION}）")

    decision = payload.get("decision")
    if not isinstance(decision, Mapping):
        raise ValueError("decision 缺失或非映射")
    primary = _require_str(decision, "primary_caliber", "decision")

    roles_raw = decision.get("roles")
    if not isinstance(roles_raw, Mapping) or not roles_raw:
        raise ValueError("decision.roles 缺失或为空")
    roles: dict[str, str] = {}
    for k, v in roles_raw.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise ValueError(f"decision.roles[{k!r}] 非字符串值")
        roles[k] = v

    degr_raw = decision.get("degradation_order")
    if not isinstance(degr_raw, Sequence) or isinstance(degr_raw, (str, bytes)) or not degr_raw:
        raise ValueError("decision.degradation_order 须为非空列表")
    degradation = tuple(str(x) for x in degr_raw)

    calibers_raw = payload.get("calibers")
    if not isinstance(calibers_raw, Mapping) or not calibers_raw:
        raise ValueError("calibers 缺失或为空")
    known_families: set[str] = set()
    calibers: dict[str, CaliberSpec] = {}
    shenwan_levels: tuple[str, ...] = ()
    for name, spec in calibers_raw.items():
        if not isinstance(spec, Mapping):
            raise ValueError(f"calibers.{name} 非映射")
        family = _require_str(spec, "family", f"calibers.{name}")
        role = _require_str(spec, "role", f"calibers.{name}")
        cat_ids: list[str] = []
        tables = spec.get("tables")
        if tables is not None:
            if not isinstance(tables, Sequence) or isinstance(tables, (str, bytes)):
                raise ValueError(f"calibers.{name}.tables 须为列表")
            for i, t in enumerate(tables):
                if not isinstance(t, Mapping):
                    raise ValueError(f"calibers.{name}.tables[{i}] 非映射")
                cat_ids.append(_require_str(t, "category_id", f"calibers.{name}.tables[{i}]"))
        notes: list[str] = []
        constraints = spec.get("constraints")
        if isinstance(constraints, Sequence) and not isinstance(constraints, (str, bytes)):
            notes.extend(str(c) for c in constraints)
        if family == "shenwan":
            identity = spec.get("identity")
            if isinstance(identity, Mapping):
                levels = identity.get("levels")
                if isinstance(levels, Sequence) and not isinstance(levels, (str, bytes)) and levels:
                    shenwan_levels = tuple(str(x) for x in levels)
        known_families.add(family)
        calibers[str(name)] = CaliberSpec(family=family, role=role, category_ids=tuple(cat_ids), notes=tuple(notes))

    if primary not in calibers:
        raise ValueError(f"decision.primary_caliber={primary} 未在 calibers 声明")
    for d in degradation:
        if d not in calibers:
            raise ValueError(f"degradation_order 项 {d} 未在 calibers 声明")

    rules_raw = payload.get("routing_rules")
    if not isinstance(rules_raw, Sequence) or isinstance(rules_raw, (str, bytes)) or not rules_raw:
        raise ValueError("routing_rules 缺失或为空")
    rules: list[RouteRule] = []
    for i, item in enumerate(rules_raw):
        if not isinstance(item, Mapping):
            raise ValueError(f"routing_rules[{i}] 非映射")
        pattern_src = _require_str(item, "pattern", f"routing_rules[{i}]")
        try:
            pattern = re.compile(pattern_src)
        except re.error as exc:
            raise ValueError(f"routing_rules[{i}].pattern 编译失败: {pattern_src} ({exc})") from exc
        family = _require_str(item, "family", f"routing_rules[{i}]")
        role = _require_str(item, "role", f"routing_rules[{i}]")
        action = str(item.get("action", "route"))
        if action not in ("route", "exclude"):
            raise ValueError(f"routing_rules[{i}].action 非法: {action}")
        if family not in known_families and family != "ambiguous":
            raise ValueError(f"routing_rules[{i}].family={family} 未在 calibers 声明（ambiguous 除外）")
        rules.append(
            RouteRule(
                pattern=pattern,
                family=family,
                role=role,
                action=action,
                note=str(item.get("note", "")),
            )
        )

    return SectorUniverseRouterConfig(
        primary_caliber=primary,
        roles=roles,
        degradation_order=degradation,
        calibers=calibers,
        rules=tuple(rules),
        shenwan_levels=shenwan_levels,
    )


def load_sector_universe_router(path: str | Path | None = None) -> SectorUniverseRouterConfig:
    """从盘面装载路由配置（默认 config/sector_universe_router.yaml）。

    Raises:
        FileNotFoundError: 配置不存在。
        ValueError: 解析/校验失败（fail-closed）。
    """
    p = Path(path) if path is not None else DEFAULT_CONFIG_PATH
    with p.open("r", encoding="utf-8") as fh:
        payload = yaml.safe_load(fh)
    return parse_sector_universe_config(payload)


def route_sector_code(
    code: str,
    config: SectorUniverseRouterConfig,
    *,
    source_hint: str | None = None,
) -> RouteVerdict:
    """板块代码 → 口径族判定（判别式真源=配置 routing_rules，自上而下首命中）。

    Args:
        code: 板块代码（可带 .SH/.SZ/.BJ 后缀，判别前剥离）。
        config: 已装载路由配置。
        source_hint: 6 位歧义码（与个股码同形）的消歧提示——'concept'/'stock'；
            非 6 位歧义场景忽略。

    Returns:
        RouteVerdict（action=exclude=市场统计指数剔除；unknown=无法判定不猜）。

    Raises:
        ValueError: code 非非空字符串。
    """
    if not isinstance(code, str) or not code.strip():
        raise ValueError(f"code 非法: {code!r}")
    normalized = _EXCHANGE_SUFFIX_RE.sub("", code.strip())
    for rule in config.rules:
        if rule.pattern.search(normalized):
            if rule.family == "ambiguous":
                if source_hint == "concept":
                    return RouteVerdict(
                        code=code,
                        family="concept",
                        role="event_tag",
                        action="route",
                        match_via="source_hint",
                        note=rule.note,
                    )
                if source_hint == "stock":
                    return RouteVerdict(
                        code=code,
                        family="stock",
                        role="stock",
                        action="unknown",
                        match_via="source_hint",
                        note="个股码非板块宇宙（6 位同形消歧）",
                    )
                return RouteVerdict(
                    code=code,
                    family="unknown",
                    role="ambiguous",
                    action="unknown",
                    match_via="none",
                    note="6 位码与个股码同形——须 source_hint=concept/stock 消歧（fail-loud 不猜）",
                )
            return RouteVerdict(
                code=code,
                family=rule.family,
                role=rule.role,
                action=rule.action,
                note=rule.note,
            )
    return RouteVerdict(
        code=code,
        family="unknown",
        role="unknown",
        action="unknown",
        match_via="none",
        note="无判别式命中（如申万口径身份=(industry_level, industry_sw) 无数码判别）",
    )


def primary_universe(config: SectorUniverseRouterConfig) -> UniverseSpec:
    """主口径宇宙解析（主口径 + 降级链 + 主口径表品类锚）。

    申万主口径的行情面为派生视图（config derived_views 声明），本件只回品类锚，
    派生装配归消费端（面板装配件）。
    """
    spec = config.calibers[config.primary_caliber]
    return UniverseSpec(
        primary_caliber=config.primary_caliber,
        degradation_order=config.degradation_order,
        category_ids=spec.category_ids,
    )
