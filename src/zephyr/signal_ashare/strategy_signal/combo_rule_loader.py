# [BLUEPRINT] MOD-SIG-147 | 待统筹登记（supplement：图形技术库四件要单——组合规则 YAML 卡加载器；Owner 2026-09-29 最高优先令）
# [MODULE] zephyr.signal_ashare.strategy_signal.combo_rule_loader
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] （yaml 配置读端；消费方 unified_pattern_engine 融合判定）
# [CONSUMERS] unified_pattern_engine.UnifiedPatternEngine（combo_rules 注入 + recognize 装配）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] yaml 缺失/非法/字段越界 → ValueError fail-closed（禁半读）；direction 封闭集 {向上,向下}；sr_side 封闭集 {support,resistance,any}；strength_delta 与 proximity/volume 阈值须非负；match 单规则至多一命中（取最近水平位）；量能比 None=跳过量能条件（SKIP 口径）；引擎 PatternClass 封闭集不动，组合事件挂 SR 类、name 前缀「组合:」
# [MODIFY-GUARD] docs/_working/decision_map_campaign_20260924/HANDOVER_FINAL.md §五第二优先行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 配置非法 → ValueError（fail-closed）；talib/sklearn 无关（纯规则匹配）
# [TESTS] tests/signal_ashare/strategy_signal/test_combo_rule_loader.py
# [A_module] module_id=MOD-SIG-147_combo_rule_loader | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""组合规则 YAML 卡加载与匹配（图形四件要单之「组合规则卡」真源读端）。

配置真源=config/pattern_combo_rules.yaml：三要素（形态事件 × SR 邻近度 ×
量能比）→ 方向/强度增量。加载 fail-closed；match 返回 ComboHit（引擎负责
转 PatternEvent 装配，本模块不碰引擎类型，保持无环依赖）。

# [ALGO_FLOW] external: docs/03_modules/_domain_signal/algo_flow/combo_rule_loader.yaml
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, Sequence

import yaml

__all__: Final = ["ComboHit", "ComboRule", "load", "match", "validate"]

_SIDE_SET: Final = {"support", "resistance", "any"}
_DIR_SET: Final = {"向上", "向下"}


@dataclass(frozen=True, slots=True)
class ComboRule:
    """组合规则卡（三要素阈值 + 输出方向/强度增量）。"""

    rule_id: str
    pattern_id: str  # 匹配事件的 pattern_id 或 name
    sr_side: str  # support/resistance/any（相对 last_close 的位侧）
    sr_proximity_pct_max: float  # 现价距水平位 % 上限
    volume_ratio_min: float  # 量能比下限（末量/前20均量）
    direction: str  # 向上/向下
    strength_delta: float  # 置信度增量（引擎侧 0.5 基线叠加后截断 0~1）
    enabled: bool = True


@dataclass(frozen=True, slots=True)
class ComboHit:
    """一次规则命中（最近水平位口径）。"""

    rule_id: str
    matched_pattern: str
    sr_price: float
    proximity_pct: float
    volume_ratio: float | None
    direction: str
    strength_delta: float


def _parse(raw: dict[str, Any], idx: int) -> ComboRule:
    if not isinstance(raw, dict):
        raise ValueError(f"rules[{idx}] 非法（须映射）: {type(raw).__name__}")
    for k in (
        "rule_id",
        "pattern_id",
        "sr_side",
        "sr_proximity_pct_max",
        "volume_ratio_min",
        "direction",
        "strength_delta",
    ):
        if k not in raw:
            raise ValueError(f"rules[{idx}] 缺必填字段: {k}")
    rule = ComboRule(
        rule_id=str(raw["rule_id"]),
        pattern_id=str(raw["pattern_id"]),
        sr_side=str(raw["sr_side"]),
        sr_proximity_pct_max=float(raw["sr_proximity_pct_max"]),
        volume_ratio_min=float(raw["volume_ratio_min"]),
        direction=str(raw["direction"]),
        strength_delta=float(raw["strength_delta"]),
        enabled=bool(raw.get("enabled", True)),
    )
    validate((rule,))
    return rule


def validate(rules: Sequence[ComboRule]) -> None:
    """规则域校验（fail-closed）：封闭集 + 非负阈值。"""
    seen: set[str] = set()
    for r in rules:
        if not r.rule_id:
            raise ValueError("rule_id 不能为空")
        if r.rule_id in seen:
            raise ValueError(f"rule_id 重复: {r.rule_id}")
        seen.add(r.rule_id)
        if r.sr_side not in _SIDE_SET:
            raise ValueError(f"{r.rule_id}: sr_side 非法（support/resistance/any）: {r.sr_side!r}")
        if r.direction not in _DIR_SET:
            raise ValueError(f"{r.rule_id}: direction 非法（向上/向下）: {r.direction!r}")
        if r.sr_proximity_pct_max < 0 or r.volume_ratio_min < 0:
            raise ValueError(f"{r.rule_id}: 阈值须非负")
        if not r.pattern_id:
            raise ValueError(f"{r.rule_id}: pattern_id 不能为空")


def load(path: str) -> tuple[ComboRule, ...]:
    """读组合规则 YAML 卡（缺失/非法 fail-closed ValueError）。"""
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except OSError as exc:
        # MSG-EXPOSURE：消息不带路径（细节由调用方日志承载），只留异常类型名
        raise ValueError(f"组合规则卡不可读（fail-closed）: {type(exc).__name__}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("rules"), list):
        raise ValueError("组合规则卡结构非法（须含 rules 列表）")
    rules = tuple(_parse(r, i) for i, r in enumerate(data["rules"]))
    validate(rules)
    return rules


def _best_sr_level(rule: ComboRule, sr_levels: Sequence[float], last_close: float) -> tuple[float, float] | None:
    """单规则的水平位匹配：侧位过滤+邻近度阈值，返回 (proximity, sr_price) 取最近；无命中 None。"""
    best: tuple[float, float] | None = None
    for sr in sr_levels:
        if sr <= 0:
            continue
        if rule.sr_side == "support" and sr > last_close:
            continue
        if rule.sr_side == "resistance" and sr < last_close:
            continue
        prox = abs(last_close - sr) / sr * 100.0
        if prox <= rule.sr_proximity_pct_max and (best is None or prox < best[0]):
            best = (prox, float(sr))
    return best


def match(
    rules: Sequence[ComboRule],
    events: Sequence[Any],
    sr_levels: Sequence[float],
    last_close: float,
    volume_ratio: float | None = None,
) -> tuple[ComboHit, ...]:
    """规则×事件×水平位×量能 匹配（单规则取最近水平位，至多一命中）。

    events 为引擎腿部原始事件（duck 型：读 pattern_id/name）；sr_levels 为
    SR 腿水平位价；volume_ratio=None 跳过量能条件（SKIP 口径）。
    """
    if last_close <= 0:
        raise ValueError(f"last_close 须为正: {last_close!r}")
    hits: list[ComboHit] = []
    for rule in rules:
        if not rule.enabled:
            continue
        cands = [e for e in events if rule.pattern_id in (getattr(e, "pattern_id", ""), getattr(e, "name", ""))]
        if not cands:
            continue
        best = _best_sr_level(rule, sr_levels, last_close)
        if best is None:
            continue
        if volume_ratio is not None and volume_ratio < rule.volume_ratio_min:
            continue
        hits.append(
            ComboHit(
                rule_id=rule.rule_id,
                matched_pattern=rule.pattern_id,
                sr_price=best[1],
                proximity_pct=best[0],
                volume_ratio=volume_ratio,
                direction=rule.direction,
                strength_delta=rule.strength_delta,
            )
        )
    return tuple(hits)
