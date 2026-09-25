# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] zephyr.ai_layer.scheduling.router
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] 零仓内依赖（三证据机检=纯函数，注册表/文件集由调用方注入）
# [CONSUMERS] zephyr.ai_layer.scheduling.order_daemon（工单分流挂接）;
#             zephyr.ai_layer.scheduling.dispatcher（owner_gate 工单不进自动派工队列）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 三证据机检（R1 作用域/R2 风险/R3 自指），任一命中骨架级即骨架级（DESIGN §2.4）；
#              骨架级必置 owner_gate=true（提案包走前端一键确认，promotion.js 惯例）；
#              自指命中（目标=AI 层自身：src/zephyr/ai_layer/**、gate 体系、排班表）必 Owner——
#              定调 #9"先他指后自指"，v1 自指一律 Owner 确认；模块级 owner_gate=false 自动派
#              fresh worktree 施工队；判定=纯函数（全枚举可测，注册表快照注入禁写生产路径）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L5_schedule_gate/DESIGN.md §2.4（D-L5-05 设计真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 判定不抛业务错（缺证据按从重 fail-closed：未知域→low 但触达词表命中骨架级；
#                  空 registered 集合→R1 判骨架级——无登记图不自动派工）
# [TESTS] tests/ai_layer/scheduling/test_router.py（R1-R3 全枚举：登记内=模块级/新顶层文件/
#         跨域边=骨架级/high 域与宪法触达=骨架级/未列域默认 low/自指四类命中=Owner/
#         混合证据任一命中即骨架级/owner_gate 恒真值断言）
# [TTL] permanent
"""router — L5 骨架级分流器（D-L5-05）：三证据机检 + Owner 门位路由。

判定规则（任一命中骨架级即骨架级）::

    R1 作用域  模块级=目标文件全部落在既有 module_id 的 depgraph 已登记范围内；
               骨架级=出现新模块/新顶层文件/跨域新依赖边
    R2 风险    模块级=risk_tier_registry 未命中 high（未列域默认 low）且不触达
               宪法正文/规则 YAML 权限语义/根约束清单；
               骨架级=命中 high 九域或触达上述三面
    R3 自指    模块级=目标在 AI 层之外；骨架级=目标=AI 层自身
               （src/zephyr/ai_layer/**、gate 体系、排班表）——定调 #9"先他指后自指"

路由：模块级→owner_gate=false，自动派施工队（fresh worktree 会话）；骨架级→owner_gate=true，
生成提案包（利弊对照+两问打分展示）进前端一键确认页；Owner 拒→工单作废归档（审计留痕不删）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Iterable, Mapping

__all__: Final = [
    "TIER_MODULE",
    "TIER_SKELETON",
    "SchedulingRouteDecision",
    "classify_scope",
    "classify_risk",
    "classify_selfref",
    "route",
]

TIER_MODULE: Final = "module"
TIER_SKELETON: Final = "skeleton"

# R3 自指面：AI 层自身（src/zephyr/ai_layer/**）、gate 体系（gov_enforcement 门禁/提交闸）、
# 排班表（资源画像注册表+种子+policy——排班一张真源禁自改）
SELF_REF_PREFIXES: Final[tuple[str, ...]] = (
    "src/zephyr/ai_layer/",
    "src/zephyr/gov_enforcement/",
    "config/resource_profile_registry.yaml",
    "config/evolution_schedule_seeds.yaml",
    "config/schedule_gate_policy.yaml",
    "scripts/governance/generators/generate_resource_profile_registry.py",
)
# R2 骨架级触达面：宪法正文/规则 YAML 权限语义/根约束清单
CONSTITUTION_TOUCH_PATTERNS: Final[tuple[str, ...]] = (
    "AGENTS.md",
    ".trae/rules/",
    "docs/01_policies_and_standards/rules/",
    "docs/registry_of_registries.yaml",
    "SECRETS.md",
)


@dataclass(frozen=True)
class SchedulingRouteDecision:
    """分流判决（tier + owner_gate + 命中证据清单；骨架级必 owner_gate=true）。"""

    tier: str
    owner_gate: bool
    reasons: list[str] = field(default_factory=list)


def classify_scope(
    target_files: Iterable[str],
    registered_files: Iterable[str],
    *,
    module_domain: str = "",
    file_domains: Mapping[str, str] | None = None,
) -> tuple[bool, list[str]]:
    """R1 作用域证据：目标是否全部落在既有 module_id depgraph 已登记范围。

    :param target_files: 工单目标文件（repo 相对路径）
    :param registered_files: depgraph 该模块已登记文件集合
    :param module_domain: 工单所属域
    :param file_domains: 文件→域映射（检出跨域新依赖边）
    :return: (is_module_level, reasons)；骨架级理由逐条列出
    """
    targets = [f.replace("\\", "/") for f in target_files]
    registered = {f.replace("\\", "/") for f in registered_files}
    reasons: list[str] = []
    if not registered:
        reasons.append("R1:depgraph 无登记文件集（无登记图不自动派工，从重骨架级）")
    outside = [f for f in targets if f not in registered]
    if outside:
        reasons.append(f"R1:目标超出已登记范围:{','.join(outside[:3])}")
    # 新顶层文件=目标父目录在登记集中无任何同目录文件（=新模块/新顶层落点）
    registered_parents = {f.rsplit("/", 1)[0] if "/" in f else "" for f in registered}
    new_top = [
        f for f in targets
        if f not in registered and (f.rsplit("/", 1)[0] if "/" in f else "") not in registered_parents
    ]
    if new_top:
        reasons.append(f"R1:新顶层文件:{','.join(new_top[:3])}")
    if file_domains and module_domain:
        cross = [
            f for f in targets if file_domains.get(f) not in (None, "", module_domain)
        ]
        if cross:
            reasons.append(f"R1:跨域新依赖边:{','.join(cross[:3])}")
    return (not reasons), reasons


def classify_risk(
    domain_id: str,
    risk_tier_map: Mapping[str, str],
    target_files: Iterable[str],
) -> tuple[bool, list[str]]:
    """R2 风险证据：risk_tier 未命中 high（未列域默认 low）且不触达宪法/规则权限/根约束面。

    :return: (is_module_level, reasons)
    """
    reasons: list[str] = []
    tier = risk_tier_map.get(domain_id, "low")  # 未列域默认 low（risk_tier_registry 口径）
    if tier == "high":
        reasons.append(f"R2:命中 high 九域:{domain_id}")
    for f in target_files:
        norm = f.replace("\\", "/")
        for pat in CONSTITUTION_TOUCH_PATTERNS:
            if norm == pat or norm.startswith(pat):
                reasons.append(f"R2:触达宪法/规则权限语义/根约束面:{norm}")
                break
    return (not reasons), reasons


def classify_selfref(target_files: Iterable[str]) -> tuple[bool, list[str]]:
    """R3 自指证据：目标=AI 层自身（ai_layer/gate 体系/排班表）→ 骨架级，v1 一律 Owner。

    :return: (is_module_level, reasons)
    """
    reasons: list[str] = []
    for f in target_files:
        norm = f.replace("\\", "/")
        for prefix in SELF_REF_PREFIXES:
            if norm == prefix or norm.startswith(prefix):
                reasons.append(f"R3:自指命中（先他指后自指）:{norm}")
                break
    return (not reasons), reasons


def route(
    target_files: Iterable[str],
    *,
    registered_files: Iterable[str],
    domain_id: str,
    risk_tier_map: Mapping[str, str],
    file_domains: Mapping[str, str] | None = None,
) -> SchedulingRouteDecision:
    """三证据机检合流：任一命中骨架级即骨架级（owner_gate=true）；全过=模块级自动派。"""
    targets = list(target_files)
    reasons: list[str] = []
    ok_r1, why_r1 = classify_scope(
        targets, registered_files, module_domain=domain_id, file_domains=file_domains
    )
    ok_r2, why_r2 = classify_risk(domain_id, risk_tier_map, targets)
    ok_r3, why_r3 = classify_selfref(targets)
    reasons.extend(why_r1)
    reasons.extend(why_r2)
    reasons.extend(why_r3)
    if not (ok_r1 and ok_r2 and ok_r3):
        return SchedulingRouteDecision(tier=TIER_SKELETON, owner_gate=True, reasons=reasons)
    return SchedulingRouteDecision(tier=TIER_MODULE, owner_gate=False, reasons=[])
