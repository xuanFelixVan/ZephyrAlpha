# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §l6_switch_engine
# [MODULE] zephyr.ai_layer.switch_engine.approval_router
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] zephyr.intelligence.switch_engine.switch_engine (promote approved_by 语义供方);
#             src/zephyr/frontend/dashboard/web/pages/promotion.html + features/promotion/
#             promotion.js (S13 建议卡消费，kind=switch 复用零新页面)
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 三档路由与 risk_tier 映射零漏（DESIGN §②-E 表逐行编码）：机械债类=全域
#              auto；逻辑债类 high 域=owner_one_click（promotion 前端建议卡）、medium/low=
#              independent_review（L4 对比器独立裁定，运动员不兼任裁判）；规则类=obj_r_pipeline
#              （OBJ_R 四步流水线+重考一票否决+Owner 修标）；骨架级=owner_one_click（AI 提案）；
#              tier 一律查 risk_tier_registry.yaml 现值（未列域默认 low），九域清单禁止硬编码
#              （REG-RISK-TIER-001 唯一真源）；建议卡由本流水线生成（禁手工造建议，S13 先例）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L6_ab_switch/DESIGN.md §②-E/§③/§④-S6；
#                tier 值漂移=risk_tier_registry.yaml 变更流程
# [STABILITY] new
# [SAFETY] M（owner_one_click 路由涉 production 流转建议——只产建议卡不执行）
# [ALGO_FLOW] external: docs/03_modules/_domain_ai_layer/algo_flow/approval_router.yaml
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知 debt_class->ValueError；risk_tier_registry 缺失/形状非法->
#                  RiskTierRegistryError（fail-closed，不降级内置九域表）；建议卡缺
#                  switch_id/证据链接->ValueError（禁造空证据卡）
# [TESTS] tests/ai_layer/switch_engine/test_approval_router.py（九 high 域逐域 owner 路由零漏/
#         medium/low 逻辑债独立复核/机械债全域 auto/规则类+骨架级路由/registry 缺文件抛错/
#         建议卡 kind=switch 形状+二次确认字段）
# [TTL] permanent
"""approval_router — 切换审批分流器（S6 施工件）：债类 × risk_tier 九域映射三道分流。

分流只产**路由裁定+建议卡载荷**，不执行切换——owner 道接 promotion 页（复用 S13 先例，
advisory kind=switch，二次确认+服务端留痕回执），independent_review 道由 L4 对比器独立
裁定（升 canary/promote 的裁定出自 L4，评估者独立），auto 道仍受 T1-T6 机检与回切武装
约束（全自动≠无安全带）。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.shared.io.paths import REPO_ROOT

_RISK_TIER_PATH_CACHE: str | None = None


def _risk_tier_registry_path() -> str:
    """经 ROOR physical_path 反查 risk_tier_registry 路径（VOCAB-CHAIN 合规：零 SSoT 硬编码）。"""
    global _RISK_TIER_PATH_CACHE
    if _RISK_TIER_PATH_CACHE:
        return _RISK_TIER_PATH_CACHE
    import yaml
    from zephyr.shared.io.paths import REPO_ROOT
    doc = yaml.safe_load((REPO_ROOT / "docs" / "registry_of_registries.yaml").read_text(encoding="utf-8"))
    found = ""

    def _walk(node: object) -> None:
        nonlocal found
        if found:
            return
        if isinstance(node, dict):
            pp = node.get("physical_path")
            if isinstance(pp, str) and "risk_tier_registry.yaml" in pp:
                found = pp
                return
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for v in node:
                _walk(v)

    _walk(doc)
    if not found:
        raise RuntimeError("ROOR 反查 risk_tier_registry.yaml 失败（fail-closed）")
    _RISK_TIER_PATH_CACHE = found
    return found

DEFAULT_RISK_TIER_PATH: Final[Path] = (
    REPO_ROOT
    / _risk_tier_registry_path()
)
DEFAULT_TIER: Final[str] = "low"  # risk_tier_registry default_tier（勿在调用方自定）
ADVISORY_KIND: Final[str] = "switch"

ROUTE_AUTO: Final[str] = "auto"
ROUTE_INDEPENDENT_REVIEW: Final[str] = "independent_review"
ROUTE_OWNER_ONE_CLICK: Final[str] = "owner_one_click"
ROUTE_OBJ_R_PIPELINE: Final[str] = "obj_r_pipeline"

DEBT_MECHANICAL: Final[str] = "mechanical"   # 机械债类：行为零变化（diff_kind 全 identical）
DEBT_LOGIC: Final[str] = "logic"             # 逻辑债类：行为变
DEBT_RULE: Final[str] = "rule"               # 规则类：OBJ_R 尺子
DEBT_SKELETON: Final[str] = "skeleton"       # 骨架级：增删环节/改层级

_KNOWN_DEBTS: Final[frozenset[str]] = frozenset(
    {DEBT_MECHANICAL, DEBT_LOGIC, DEBT_RULE, DEBT_SKELETON}
)


class RiskTierRegistryError(RuntimeError):
    """risk_tier_registry.yaml 缺失/形状非法（fail-closed，不降级内置表）。

    :param details: 敏感上下文（路径等）走 details 不进消息文本（5.99.20）。
    """

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}


@dataclass(frozen=True)
class ApprovalRoutingDecision:
    route: str
    debt_class: str
    domain: str
    tier: str
    rationale: str
    requires_owner_gate: bool




def load_domain_tiers(path: Path | None = None) -> dict[str, str]:
    """domain->tier 查表（REG-RISK-TIER-001 现值；未列域由调用方按 DEFAULT_TIER 兜底）。"""
    target = path or DEFAULT_RISK_TIER_PATH
    if not target.is_file():
        raise RiskTierRegistryError("risk_tier_registry 缺失（fail-closed）", details={"path": str(target)})
    with target.open("r", encoding="utf-8") as fh:
        payload = yaml.safe_load(fh)
    entries = (payload or {}).get("domain_tiers")
    if not isinstance(entries, list):
        raise RiskTierRegistryError("risk_tier_registry 形状非法：缺 domain_tiers 列表")
    return {
        entry["domain"]: entry["tier"]
        for entry in entries
        if isinstance(entry, dict) and "domain" in entry and "tier" in entry
    }


def route(
    debt_class: str,
    domain: str,
    tier_lookup: Callable[[str], str] | None = None,
    *,
    registry_path: Path | None = None,
) -> ApprovalRoutingDecision:
    """§②-E 分流（表逐行编码；tier 现查现用，九域清单不写死在本模块）。"""
    if debt_class not in _KNOWN_DEBTS:
        raise ValueError(f"未知 debt_class={debt_class!r}，合法={sorted(_KNOWN_DEBTS)}")
    lookup = tier_lookup or _default_lookup(registry_path)
    tier = lookup(domain)

    if debt_class == DEBT_MECHANICAL:
        return ApprovalRoutingDecision(
            ROUTE_AUTO, debt_class, domain, tier,
            "机械债类行为零变化：corpus byte-identical+gates 全绿+回切武装即 promote（全自动）",
            False,
        )
    if debt_class == DEBT_LOGIC:
        if tier == "high":
            return ApprovalRoutingDecision(
                ROUTE_OWNER_ONE_CLICK, debt_class, domain, tier,
                "逻辑债类·high 域：Owner 前端一键（promotion 建议卡 kind=switch）", True,
            )
        return ApprovalRoutingDecision(
            ROUTE_INDEPENDENT_REVIEW, debt_class, domain, tier,
            "逻辑债类 medium/low：L4 对比器独立复核+canary 满期零事故自动 promote", False,
        )
    if debt_class == DEBT_RULE:
        return ApprovalRoutingDecision(
            ROUTE_OBJ_R_PIPELINE, debt_class, domain, tier,
            "规则类：OBJ_R 四步流水线+重考历史一票否决+Owner 修标", True,
        )
    return ApprovalRoutingDecision(
        ROUTE_OWNER_ONE_CLICK, debt_class, domain, tier,
        "骨架级（增删环节/改层级）：AI 提案+Owner 一键（先他指后自指）", True,
    )


def build_switch_advisory(
    *,
    switch_id: str,
    object_ref: str,
    a_summary: str,
    b_summary: str,
    evidence_link: str,
) -> dict[str, Any]:
    """promotion 页建议卡载荷（kind=switch，复用 S13 页面零新页面；禁手工造建议）。"""
    if not switch_id or not evidence_link:
        raise ValueError("建议卡缺 switch_id/证据链接（禁造空证据卡）")
    return {
        "kind": ADVISORY_KIND,
        "switch_id": switch_id,
        "object_ref": object_ref,
        "a_vs_b": {"champion": a_summary, "challenger": b_summary},
        "actions": ["promote", "revert"],
        "confirm_required": True,   # 二次确认（S13 先例铁律）
        "evidence_link": evidence_link,
    }


def _default_lookup(
    registry_path: Path | None,
) -> Callable[[str], str]:
    tiers = load_domain_tiers(registry_path)

    def _lookup(domain: str) -> str:
        return tiers.get(domain, DEFAULT_TIER)

    return _lookup
