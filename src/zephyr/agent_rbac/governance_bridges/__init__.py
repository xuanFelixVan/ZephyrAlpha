# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §
"""
Agent RBAC — MOD-INF-018

RBAC 权限模型：Role-Based Access Control for AI Agents.
支持角色/权限/资源三元组判定。
"""
from . import approver_check
from . import bootstrap_superadmin
from . import capability_check
from . import contracts

__all__ = ['a2a_check', 'approver_check', 'bootstrap_superadmin', 'capability_check', 'contracts']


__version__ = "0.1.0"
__module_id__ = "MOD-INF-018"