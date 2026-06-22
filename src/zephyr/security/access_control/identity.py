# [A_module] module_id=MOD-SEC_identity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""Stub module: zephyr.security.access_control.identity — implementation pending."""

from enum import Enum

MATURITY_AUTO_GUARD_TIMEOUT = {
    "L0_INTERN": 300,
    "L1_JUNIOR": 900,
    "L2_REGULAR": 3600,
    "L3_SENIOR": 3600,
    "L4_PRINCIPAL": 7200,
}  # stub constant

MATURITY_TLB_LIMITS = {
    "L0_INTERN": 100,
    "L1_JUNIOR": 500,
    "L2_REGULAR": 2000,
    "L3_SENIOR": 10000,
    "L4_PRINCIPAL": 50000,
}  # stub constant

ROLE_DEFAULT_PERMISSIONS = None  # stub constant


class AgentRole(str, Enum):
    """Stub enum — implementation pending."""

    EXECUTOR = "EXECUTOR"
    BUILDER = "BUILDER"
    REVIEWER = "REVIEWER"
    RESEARCHER = "RESEARCHER"
    ADMIN = "ADMIN"
    OBSERVER = "OBSERVER"


class MaturityLevel(str, Enum):
    """Stub enum — implementation pending."""

    L0_INTERN = "L0_INTERN"
    L1_JUNIOR = "L1_JUNIOR"
    L2_REGULAR = "L2_REGULAR"
    L3_SENIOR = "L3_SENIOR"
    L4_PRINCIPAL = "L4_PRINCIPAL"


class IDESource(str, Enum):
    """Stub enum — implementation pending."""

    TRAE = "TRAE"
    CURSOR = "CURSOR"
    CLAUDE = "CLAUDE"
    COPILOT = "COPILOT"
    CLI = "CLI"
    API = "API"


class AgentIdentity:
    """Stub class — implementation pending."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


__all__ = [
    "MATURITY_AUTO_GUARD_TIMEOUT",
    "MATURITY_TLB_LIMITS",
    "ROLE_DEFAULT_PERMISSIONS",
    "AgentIdentity",
    "AgentRole",
    "IDESource",
    "MaturityLevel",
]
