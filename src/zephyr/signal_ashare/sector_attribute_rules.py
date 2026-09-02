# [BLUEPRINT] MOD-SIG-077 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-18 行）
# [MODULE] zephyr.signal_ashare.sector_attribute_rules
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] config/sector_attribute_mapping.yaml（B_yaml 规则真源，路径可注入）
# [CONSUMERS] （候选：板块页 Top10 属性列、下游策略语境标注）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 属性四态封闭 offensive/defensive/balanced/unlabeled；code 命中优先于 keyword 命中；规则自上而下首命中生效；未命中→未标注（不强行归类）；载荷非法 fail-closed ValueError；纯函数与文件 I/O 隔离（字典注入可单测）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-18 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 配置载荷非法/文件读取失败→ValueError（fail-closed）；rules/sectors 入参类型非法→ValueError；单板块未命中→unlabeled 不抛
# [TESTS] tests/signal_ashare/test_sector_attribute_rules.py
# [A_module] module_id=MOD-SIG-077 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-077 — 板块属性标注规则库（GAP-F-18，板块 Top10「属性」列后端）。

进攻/防御/平衡三分类静态映射表 + 解析器：
- **真源**：config/sector_attribute_mapping.yaml（B_yaml，本模块唯一消费方）；
  与 config/sector_attribute_labels.yaml（攻/防两族，MOD-SIG-060 rs_ratio 专用）
  边界写在该 yaml 头注——两文件粒度不同不合并（防双轨留痕）。
- **匹配口径**：code 精确命中（881xxx 行业板锚定码）优先；其次名称关键词
  子串命中；规则表自上而下首命中生效；未命中→「未标注」（不强行归类，
  match_via=none 留痕）。
- **纯静态规则**（行业贝塔属性常识分类，初拍待实盘标定），非动态计算；
  观测层消费，不接交易。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 配置载荷 dict（yaml 解析结果或测试直注）
# - id: I2 板块查询 (sector_name, sector_code) / 批量行
# 层: 算法
# - id: A1 载荷校验→规则表（fail-closed）
# - id: A2 code 精确匹配 → keyword 子串匹配（首命中）
# 层: 输出
# - id: O1 SectorAttributeVerdict（attribute/label/rule_key/match_via）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1,I2 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final, Mapping, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "ATTR_BALANCED",
    "ATTR_DEFENSIVE",
    "ATTR_OFFENSIVE",
    "ATTR_UNLABELED",
    "ATTRIBUTE_LABELS",
    "DEFAULT_CONFIG_PATH",
    "SectorAttributeRule",
    "SectorAttributeVerdict",
    "annotate_sectors",
    "load_attribute_mapping",
    "parse_attribute_mapping",
    "resolve_sector_attribute",
]

#: 属性四态（封闭集合；unlabeled=未命中兜底，不强行归类）
ATTR_OFFENSIVE: Final[str] = "offensive"
ATTR_DEFENSIVE: Final[str] = "defensive"
ATTR_BALANCED: Final[str] = "balanced"
ATTR_UNLABELED: Final[str] = "unlabeled"

_VALID_ATTRIBUTES: Final[frozenset[str]] = frozenset({ATTR_OFFENSIVE, ATTR_DEFENSIVE, ATTR_BALANCED})

#: 属性 → 中文标签（展示层）
ATTRIBUTE_LABELS: Final[dict[str, str]] = {
    ATTR_OFFENSIVE: "进攻",
    ATTR_DEFENSIVE: "防御",
    ATTR_BALANCED: "平衡",
    ATTR_UNLABELED: "未标注",
}

#: 默认配置真源路径（仓库根相对）
DEFAULT_CONFIG_PATH: Final = Path("config/sector_attribute_mapping.yaml")


@dataclass(frozen=True, slots=True)
class SectorAttributeRule:
    """属性标注规则（yaml rules 行映射）。"""

    key: str
    name: str
    attribute: str  # offensive/defensive/balanced
    code: str = ""  # 881xxx 行业板锚定码（空=待锚定，仅关键词匹配）
    keywords: tuple[str, ...] = ()
    evidence: str = ""


@dataclass(frozen=True, slots=True)
class SectorAttributeVerdict:
    """单板块属性判定（JSON 可序列化）。"""

    sector_code: str
    sector_name: str
    attribute: str  # 四态封闭
    label: str  # 中文标签
    rule_key: str = ""  # 命中规则键（未命中空串）
    match_via: str = "none"  # code/keyword/none


# ------------------------------------------------------------------
# 载荷解析（fail-closed）
# ------------------------------------------------------------------


def parse_attribute_mapping(payload: Mapping[str, Any]) -> tuple[SectorAttributeRule, ...]:
    """配置载荷 → 规则表（fail-closed 校验）。

    Args:
        payload: yaml 解析结果（须含 rules 列表）。

    Returns:
        规则元组（自上而下=匹配优先级序）。

    Raises:
        ValueError: 载荷非法（非映射/rules 缺失/属性越界/key 重复/keywords 类型非法）。
    """
    if not isinstance(payload, Mapping):
        raise ValueError(f"载荷非法（须映射含 rules 列表）: {type(payload).__name__}")
    raw_rules = payload.get("rules")
    if not isinstance(raw_rules, Sequence) or isinstance(raw_rules, (str, bytes)):
        raise ValueError("载荷非法（rules 须为列表）")
    rules: list[SectorAttributeRule] = []
    seen_keys: set[str] = set()
    for i, item in enumerate(raw_rules):
        if not isinstance(item, Mapping):
            raise ValueError(f"rules[{i}] 非法（须映射）: {type(item).__name__}")
        key = item.get("key")
        name = item.get("name")
        if not isinstance(key, str) or not key.strip() or not isinstance(name, str) or not name.strip():
            raise ValueError(f"rules[{i}] key/name 非法（须非空字符串）")
        attribute = item.get("attribute")
        if attribute not in _VALID_ATTRIBUTES:
            raise ValueError(f"rules[{i}] attribute 非法（须 ∈{sorted(_VALID_ATTRIBUTES)}）: {attribute!r}")
        if key in seen_keys:
            raise ValueError(f"rules[{i}] key 重复: {key!r}")
        seen_keys.add(key)
        code = item.get("code", "")
        if code is None:
            code = ""
        if not isinstance(code, str):
            raise ValueError(f"rules[{i}] code 非法（须字符串）: {code!r}")
        keywords = item.get("keywords", [])
        if not isinstance(keywords, Sequence) or isinstance(keywords, (str, bytes)):
            raise ValueError(f"rules[{i}] keywords 非法（须列表）: {type(keywords).__name__}")
        kw = tuple(str(k).strip() for k in keywords if str(k).strip())
        evidence = item.get("evidence", "")
        rules.append(
            SectorAttributeRule(
                key=key.strip(),
                name=name.strip(),
                attribute=str(attribute),
                code=code.strip(),
                keywords=kw,
                evidence=str(evidence),
            )
        )
    return tuple(rules)


def load_attribute_mapping(path: Path | str = DEFAULT_CONFIG_PATH) -> tuple[SectorAttributeRule, ...]:
    """从 yaml 真源加载规则表（文件 I/O 边界，fail-closed）。

    Args:
        path: 配置文件路径（默认 config/sector_attribute_mapping.yaml）。

    Returns:
        规则元组。

    Raises:
        ValueError: 文件读取失败/解析失败/载荷非法。
    """
    import yaml  # 延迟导入——纯函数路径零第三方依赖

    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"配置文件读取失败: {path}") from exc
    try:
        payload = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"配置解析失败: {path}") from exc
    return parse_attribute_mapping(payload)


# ------------------------------------------------------------------
# 匹配核（纯函数）
# ------------------------------------------------------------------


def resolve_sector_attribute(
    sector_name: str,
    sector_code: str,
    rules: Sequence[SectorAttributeRule],
) -> SectorAttributeVerdict:
    """单板块属性判定（code 优先 → keyword 首命中 → 未标注）。

    Args:
        sector_name: 板块名（关键词匹配底本，可空串）。
        sector_code: 板块码（881xxx 锚定码精确匹配，可空串）。
        rules: 规则表（parse_attribute_mapping 产出）。

    Returns:
        SectorAttributeVerdict；未命中 attribute=unlabeled + match_via=none。

    Raises:
        ValueError: rules 元素类型非法（fail-closed）。
    """
    for r in rules:
        if not isinstance(r, SectorAttributeRule):
            raise ValueError(f"rules 元素非法（须 SectorAttributeRule）: {type(r).__name__}")
    name = sector_name if isinstance(sector_name, str) else ""
    code = sector_code.strip() if isinstance(sector_code, str) else ""
    if code:
        for r in rules:
            if r.code and r.code == code:
                return SectorAttributeVerdict(
                    sector_code=code,
                    sector_name=name,
                    attribute=r.attribute,
                    label=ATTRIBUTE_LABELS[r.attribute],
                    rule_key=r.key,
                    match_via="code",
                )
    if name:
        for r in rules:
            if any(kw in name for kw in r.keywords):
                return SectorAttributeVerdict(
                    sector_code=code,
                    sector_name=name,
                    attribute=r.attribute,
                    label=ATTRIBUTE_LABELS[r.attribute],
                    rule_key=r.key,
                    match_via="keyword",
                )
    return SectorAttributeVerdict(
        sector_code=code,
        sector_name=name,
        attribute=ATTR_UNLABELED,
        label=ATTRIBUTE_LABELS[ATTR_UNLABELED],
        rule_key="",
        match_via="none",
    )


def annotate_sectors(
    sectors: Sequence[Mapping[str, Any]],
    rules: Sequence[SectorAttributeRule],
) -> list[SectorAttributeVerdict]:
    """批量标注（板块 Top10 行 → 属性判定列表，输入序保持）。

    Args:
        sectors: 行映射序列（须含 sector_code/sector_name 键，缺省按空串）。
        rules: 规则表。

    Returns:
        SectorAttributeVerdict 列表（与输入等长同序）。

    Raises:
        ValueError: 行类型非法（fail-closed）。
    """
    out: list[SectorAttributeVerdict] = []
    for i, row in enumerate(sectors):
        if not isinstance(row, Mapping):
            raise ValueError(f"行非法（须映射含 sector_code/sector_name）[{i}]: {type(row).__name__}")
        code = row.get("sector_code", "")
        name = row.get("sector_name", "")
        if code is not None and not isinstance(code, str):
            raise ValueError(f"行非法（sector_code 须字符串）[{i}]: {code!r}")
        if name is not None and not isinstance(name, str):
            raise ValueError(f"行非法（sector_name 须字符串）[{i}]: {name!r}")
        out.append(resolve_sector_attribute(name or "", code or "", rules))
    return out
