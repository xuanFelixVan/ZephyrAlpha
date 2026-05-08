"""
Audit Trail — MOD-INF-020

不可变审计追踪：所有Agent操作记录 + 异常检测。
G-CT-001 (RBAC→Audit), G-CT-002 (Audit→Rollback).
"""

__all__ = ['anomaly', 'contracts', 'drift_bridge', 'spec_auditor', 'feedback_bridge', 'tiered_storage_bridge', 'trust_bridge', 'delegation_bridge']


__version__ = "0.1.0"
__module_id__ = "MOD-INF-020"
