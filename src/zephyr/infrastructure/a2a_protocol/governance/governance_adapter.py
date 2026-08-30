# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.governance.governance_adapter
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.contracts.security.security_decision
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
A2A GovernanceAdapter — Phase 4 治理集成桥接器

G-CT-008: A2A -> RBAC + Escalation
触发条件：Phase 4 激活后，A2A 通信需要经过 RBAC 验证 + Escalation 升级。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: governance_adapter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① GovernanceAdapter
#   name_en: GovernanceAdapter
#   intro: A2A GovernanceAdapter — G-CT-008 消费端.
#   desc: A2A GovernanceAdapter — G-CT-008 消费端. Phase 4 激活后，A2A 通信对在执行前 MUST 通过此适配器： 1. verify_a2a_…；公共方法（定义序）: verify_…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② MCPAdapter
#   name_en: MCPAdapter
#   intro: class MCPAdapter 源码 L172-L180
#   desc: 公共方法（定义序）: adapt, validate；源码 L172-L180
#   inputs: config
#   outputs: 返回值
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: GovernanceAdapter, MCPAdapter
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界

logger = logging.getLogger(__name__)

__all__ = ["A2AGovernanceRecord", "GovernanceAdapter"]

_log = logging.getLogger(__name__)

_lsg_gateway = None


def _get_lsg():
    global _lsg_gateway
    if _lsg_gateway is not None:
        return _lsg_gateway
    try:
        import importlib

        _lsg_gateway = importlib.import_module("zephyr.security.llm_defense.llm_security.gateway").LSGSecurityGateway()
        return _lsg_gateway
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        _log.debug("LSG not available for A2A governance", exc_info=True)
        return None


def _lsg_scan_a2a_sync(from_agent: str, to_agent: str, content: str) -> str | None:
    # 5.52.1 fail-closed：LSG 不可用或扫描执行失败时视同阻断（返回 blocked_by 标记），
    # 禁止 return None 静默跳过安全扫描。仅扫描正常执行且显式放行时返回 None。
    gw = _get_lsg()
    if gw is None:
        logger.warning("LSG gateway unavailable for A2A governance — fail-closed (treated as blocked)")
        return "lsg_unavailable"
    try:
        from zephyr.shared.contracts.security.security_decision import SecurityDecision

        result = run_sync(
            gw.scan_agent_action(
                text=content,
                tool_name="a2a_communication",
                tool_params={"from_agent": from_agent, "to_agent": to_agent},
                metadata={"source": "a2a_governance"},
            )
        )
        if result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK):
            return result.blocked_by or "lsg_agent_scan"
        return None
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        # 5.162 C1 修复: 移除 except RuntimeError + get_event_loop().is_running() fail-open 回退。
        # run_sync 已处理所有 async/sync 场景。原 is_running() 时 return None = fail-open 漏洞。
        logger.warning("LSG A2A scan failed — fail-closed (treated as blocked)", exc_info=True)
        return "lsg_scan_error"


@dataclass
class A2AGovernanceRecord:
    agent_pair: tuple[str, str]
    action: str
    granted: bool = False
    escalation_level: str = ""
    audit_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class GovernanceAdapter:
    """A2A GovernanceAdapter — G-CT-008 消费端.

    Phase 4 激活后，A2A 通信对在执行前 MUST 通过此适配器：
    1. verify_a2a_pair()  — 验证 Agent 对是否合法
    2. escalate_if_needed() — 必要时触发升级
    """

    ALLOWED_PAIRS: set[tuple[str, str]] = {
        ("orchestrator", "worker"),
        ("reviewer", "builder"),
        ("auditor", "any"),
    }

    def verify_pair(self, agent_a: str, agent_b: str, content: str = "") -> A2AGovernanceRecord:
        pair = (agent_a, agent_b)
        reverse = (agent_b, agent_a)
        granted = pair in self.ALLOWED_PAIRS or reverse in self.ALLOWED_PAIRS

        lsg_blocked_by = None
        if content:
            lsg_blocked_by = _lsg_scan_a2a_sync(agent_a, agent_b, content)
        if lsg_blocked_by:
            granted = False

        return A2AGovernanceRecord(
            agent_pair=(agent_a, agent_b),
            action="verify_pair",
            granted=granted,
            metadata={
                "allowed_pairs": list(self.ALLOWED_PAIRS),
                "lsg_blocked_by": lsg_blocked_by,
            },
        )

    def escalate_if_needed(self, record: A2AGovernanceRecord, severity: str = "WARN") -> A2AGovernanceRecord:
        if not record.granted:
            record.escalation_level = severity
        return record

    def audit_communication(self, record: A2AGovernanceRecord, session_id: str = "") -> A2AGovernanceRecord:
        record.audit_id = f"a2a-{hash(record.agent_pair)}-{session_id}"
        return record


class MCPAdapter:
    def __init__(self, config=None):
        self.config = config or {}

    def adapt(self, request):
        return request

    def validate(self, request):
        return True


class MCPSource:
    def __init__(self, source_id="", source_type="", endpoint="", metadata=None):
        self.source_id = source_id
        self.source_type = source_type
        self.endpoint = endpoint
        self.metadata = metadata or {}
