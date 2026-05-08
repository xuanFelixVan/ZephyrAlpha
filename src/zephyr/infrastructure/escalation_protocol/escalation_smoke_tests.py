"""Escalation Smoke Tests — v0.11.0 升级协议烟雾测试。"""
from __future__ import annotations

def test_smoke_engine_init():
    from zephyr.infrastructure.escalation_protocol.escalation_engine import EscalationEngine
    return True

def test_smoke_delegation_init():
    from zephyr.infrastructure.escalation_protocol.delegation_manager import DelegationManager
    return True

SMOKE_TESTS=[test_smoke_engine_init, test_smoke_delegation_init]

def run_smoke()->dict:
    results={}
    for t in SMOKE_TESTS:
        try:
            results[t.__name__]=t()
        except Exception as e:
            results[t.__name__]=str(e)
    return results
