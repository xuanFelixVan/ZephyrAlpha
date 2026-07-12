# [A_module] module_id=MOD-GOV_governance_a2a_protocol_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.governance
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
A2A Protocol — MOD-INF-025

Agent-to-Agent 通信协议：消息格式 + 握手 + 能力宣告.
"""

_SUBMODULES = [
    "auditor",
    "governance_adapter",
    "phase_hold",
    "protocol",
    "_base_server",
    "audit_logger",
    "error_codes",
    "policy_engine",
    "rate_limiter",
    "session_manager",
]


def __getattr__(name: str):
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(f"zephyr.infrastructure.a2a_protocol.governance.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "A2AProtocol",
    "_base_server",
    "audit_logger",
    "auditor",
    "error_codes",
    "governance_adapter",
    "phase_hold",
    "policy_engine",
    "protocol",
    "rate_limiter",
    "session_manager",
]


from zephyr.infrastructure.a2a_protocol.governance.phase_hold import Phase4Hold as A2AProtocol

__version__ = "0.1.0"
__module_id__ = "MOD-INF-025"
