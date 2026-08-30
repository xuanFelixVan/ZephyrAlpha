# [BLUEPRINT] MOD-AU-005 | docs/03_modules/_domain_autonomy_core/autonomy_level_registry/blueprint.md
# [MODULE] zephyr.autonomy_core.autonomy_level_registry
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-AU-001(autonomy_boundary_gate 运行时按级别拦截) ; MOD-AU-002(kill_switch_orchestrator 越级熔断信号)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] check_action 纯内存无IO同输入必同输出; 区上限不可被声明抬升(human_gated→L2/immutable_core→L0); 未登记角色 fail-closed 按 L0 兜底; immutable_core 越级 execute 必产 kill_switch_triggered 信号
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_core/autonomy_level_registry/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidAutonomyDeclarationError
# [TESTS] tests/autonomy/test_autonomy_level_registry.py
# [A_module] module_id=MOD-AU-005 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""



AutonomyLevelRegistry — Agent 自治边界四级自治模型 (MOD-AU-005)

CAND-AUTONOMYCORE-004（B11-02454）：四级自治注册表。
每 Agent 角色声明自治级别入 Agent Card：

- L0_RULE        纯规则：仅确定性规则输出，无自主执行
- L1_SUGGEST     建议：可产出建议，不执行
- L2_APPROVAL    审批后执行
- L3_AUTONOMOUS  自主执行（仍受区上限约束）

级别对三区映射（human_gated / immutable_core **不可降级**）：
``ZONE_LEVEL_CEILING`` 给出每区级别上限，有效级别 = min(声明级别, 区上限)，
声明永远抬不过区上限。运行时供 autonomy_boundary_gate（MOD-AU-001）按级别
拦截；immutable_core 上的 execute 越级行为产出 ``kill_switch_triggered`` 信号
与审计记录（``audit_record``），熔断执行委托 kill_switch_orchestrator
（MOD-AU-002，本模块不 import 执行体）。

判定核心 ``check_action`` 为纯内存纯函数（无 IO，<1ms 热路径兼容）；
``violation_hook`` 为可选回调，hook 异常不阻断判定（留痕降级）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: declarations 参数
#   fields: 参数 declarations（无注解）
#   code: autonomy_level_registry.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: violation_hook 参数
#   fields: 参数 violation_hook（无注解）
#   code: autonomy_level_registry.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AutonomyCheckVerdict
#   name_en: AutonomyCheckVerdict
#   intro: 单次动作判定结果（不可变）。
#   desc: 单次动作判定结果（不可变）。；公共方法（定义序）: allowed, audit_record；源码 L153-L185
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② AutonomyLevelRegistry
#   name_en: AutonomyLevelRegistry
#   intro: 四级自治注册表（纯内存判定核心）。
#   desc: 四级自治注册表（纯内存判定核心）。 Args: declarations: 初始声明映射 {agent_role: AutonomyLevel}。 violation_hook:…；公共方法（定义序）: registe…
#   inputs: declarations violation_hook
#   outputs: 返回值
#   （注：A2 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: AutonomyCheckVerdict, AutonomyLevelRegistry
#   downstream: MOD-AU-001(autonomy_boundary_gate 运行时按级别拦截) ; MOD-AU-002(kill_switch_orchestrat…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "AgentAutonomyDeclaration",
    "AutonomyCheckVerdict",
    "AutonomyDecision",
    "AutonomyLevel",
    "AutonomyLevelRegistry",
    "BoundaryZone",
    "InvalidAutonomyDeclarationError",
    "ZONE_LEVEL_CEILING",
]


class InvalidAutonomyDeclarationError(ZephyrBaseError):
    """自治级别声明非法（空角色/非法级别/重复登记）。"""


class AutonomyLevel(IntEnum):
    """四级自治模型（类比自动驾驶分级 + human-in-the-loop 审批层级）。"""

    L0_RULE = 0  # 纯规则：仅确定性规则输出，无自主执行
    L1_SUGGEST = 1  # 建议：可产出建议，不执行
    L2_APPROVAL = 2  # 审批后执行
    L3_AUTONOMOUS = 3  # 自主执行


class BoundaryZone(str, Enum):
    """三区边界（与 GOV-AI-001 注册表三分类对齐）。"""

    AI_MODIFIABLE = "ai_modifiable"
    HUMAN_GATED = "human_gated"
    IMMUTABLE_CORE = "immutable_core"


class AutonomyDecision(str, Enum):
    """单次动作判定。"""

    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    DENY = "deny"


#: 区上限：声明级别不可抬升的上界（"human_gated/immutable 不可降级"）。
ZONE_LEVEL_CEILING: Final[dict[BoundaryZone, AutonomyLevel]] = {
    BoundaryZone.AI_MODIFIABLE: AutonomyLevel.L3_AUTONOMOUS,
    BoundaryZone.HUMAN_GATED: AutonomyLevel.L2_APPROVAL,
    BoundaryZone.IMMUTABLE_CORE: AutonomyLevel.L0_RULE,
}


@dataclass(frozen=True)
class AgentAutonomyDeclaration:
    """单角色自治级别声明（入 Agent Card，不可变）。"""

    agent_role: str
    level: AutonomyLevel
    declared_by: str = ""
    rationale: str = ""


@dataclass(frozen=True)
class AutonomyCheckVerdict:
    """单次动作判定结果（不可变）。"""

    agent_role: str
    level: AutonomyLevel  # 声明级别（未登记=L0 兜底）
    effective_level: AutonomyLevel  # min(声明级别, 区上限)
    action: str
    mode: str  # "execute" | "suggest"
    zone: BoundaryZone
    decision: AutonomyDecision
    reason: str
    fail_closed: bool = False
    kill_switch_triggered: bool = False

    @property
    def allowed(self) -> bool:
        return self.decision is AutonomyDecision.ALLOW

    def audit_record(self) -> dict[str, object]:
        """审计记录 dict（持久化委托调用方；运行时装配批接 MOD-AU-001/002 链路）。"""
        return {
            "event_type": "AUTONOMY_LEVEL_VIOLATION" if self.kill_switch_triggered else "AUTONOMY_LEVEL_CHECK",
            "agent_role": self.agent_role,
            "declared_level": self.level.name,
            "effective_level": self.effective_level.name,
            "action": self.action,
            "mode": self.mode,
            "zone": self.zone.value,
            "decision": self.decision.value,
            "reason": self.reason,
            "fail_closed": self.fail_closed,
            "kill_switch_triggered": self.kill_switch_triggered,
        }


def _validate_role(agent_role: str) -> str:
    if not isinstance(agent_role, str) or not agent_role.strip():
        raise InvalidAutonomyDeclarationError(f"agent_role 必须为非空字符串: {agent_role!r}")
    return agent_role.strip()


def _validate_level(level: AutonomyLevel) -> AutonomyLevel:
    if not isinstance(level, AutonomyLevel):
        raise InvalidAutonomyDeclarationError(f"level 必须为 AutonomyLevel: {level!r}")
    return level


class AutonomyLevelRegistry:
    """四级自治注册表（纯内存判定核心）。

    Args:
        declarations: 初始声明映射 {agent_role: AutonomyLevel}。
        violation_hook: 越级（kill_switch_triggered）回调；异常不阻断判定。
    """

    def __init__(
        self,
        declarations: Mapping[str, AutonomyLevel] | None = None,
        violation_hook: Callable[[AutonomyCheckVerdict], None] | None = None,
    ) -> None:
        self._decls: dict[str, AgentAutonomyDeclaration] = {}
        self._violation_hook = violation_hook
        for role, level in (declarations or {}).items():
            self.register(role, level)

    def register(
        self,
        agent_role: str,
        level: AutonomyLevel,
        *,
        declared_by: str = "",
        rationale: str = "",
    ) -> AgentAutonomyDeclaration:
        """登记角色自治级别；重复登记拒绝（声明唯一真源）。"""
        role = _validate_role(agent_role)
        lvl = _validate_level(level)
        if role in self._decls:
            raise InvalidAutonomyDeclarationError(f"角色已登记，禁止重复声明: {role}")
        decl = AgentAutonomyDeclaration(agent_role=role, level=lvl, declared_by=declared_by, rationale=rationale)
        self._decls[role] = decl
        return decl

    def level_of(self, agent_role: str) -> AutonomyLevel:
        """查询声明级别；未登记 fail-closed 按 L0 兜底。"""
        decl = self._decls.get(agent_role.strip() if isinstance(agent_role, str) else "")
        return decl.level if decl is not None else AutonomyLevel.L0_RULE

    def snapshot(self) -> tuple[AgentAutonomyDeclaration, ...]:
        """全部声明的不可变快照。"""
        return tuple(self._decls.values())

    def check_action(
        self,
        agent_role: str,
        action: str,
        *,
        mode: str = "execute",
        zone: BoundaryZone = BoundaryZone.AI_MODIFIABLE,
        approval_granted: bool = False,
    ) -> AutonomyCheckVerdict:
        """按级别+区上限判定单动作（纯函数，无 IO）。

        - mode="suggest"：所有级别放行（建议不执行）。
        - mode="execute"：L0/L1 DENY；L2 REQUIRE_APPROVAL（获批 ALLOW）；L3 ALLOW。
        - 区上限先行：有效级别 = min(声明级别, ZONE_LEVEL_CEILING[zone])。
        - immutable_core 上 execute 一律 DENY 且 kill_switch_triggered=True。
        """
        role = agent_role.strip() if isinstance(agent_role, str) else ""
        decl = self._decls.get(role)
        fail_closed = decl is None
        declared = decl.level if decl is not None else AutonomyLevel.L0_RULE
        effective = min(declared, ZONE_LEVEL_CEILING[zone])

        kill = False
        if mode != "execute":
            decision, reason = AutonomyDecision.ALLOW, "建议模式不执行，全级别放行"
        elif zone is BoundaryZone.IMMUTABLE_CORE:
            decision = AutonomyDecision.DENY
            reason = "immutable_core 区禁止任何自治执行（区上限 L0，不可降级）"
            kill = True
        elif effective is AutonomyLevel.L0_RULE:
            decision = AutonomyDecision.DENY
            reason = "L0 纯规则：无自主执行权" if not fail_closed else "未登记角色 fail-closed 按 L0 兜底，执行需人审"
            if fail_closed:
                decision = AutonomyDecision.REQUIRE_APPROVAL
        elif effective is AutonomyLevel.L1_SUGGEST:
            decision, reason = AutonomyDecision.DENY, "L1 建议级：仅可产出建议，禁止执行"
        elif effective is AutonomyLevel.L2_APPROVAL:
            if approval_granted:
                decision, reason = AutonomyDecision.ALLOW, "L2 审批后执行：已获批"
            else:
                decision, reason = AutonomyDecision.REQUIRE_APPROVAL, "L2 审批后执行：待人审批准"
        else:
            decision, reason = AutonomyDecision.ALLOW, "L3 自主执行（区上限内）"

        verdict = AutonomyCheckVerdict(
            agent_role=role,
            level=declared,
            effective_level=AutonomyLevel(effective),
            action=action,
            mode=mode,
            zone=zone,
            decision=decision,
            reason=reason,
            fail_closed=fail_closed,
            kill_switch_triggered=kill,
        )
        if kill and self._violation_hook is not None:
            try:
                self._violation_hook(verdict)
            except Exception:  # noqa: BLE001 — hook 异常不阻断判定（留痕降级）
                _logger.exception("violation_hook 异常（已降级，判定不受影响）")
        return verdict
