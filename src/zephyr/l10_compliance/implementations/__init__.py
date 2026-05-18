# [BLUEPRINT] MOD-L10-001 | 03_modules/l10_compliance/compliance-core/blueprint.md | §
"""L10 — Compliance Concrete Implementations

Phase C 具体实现包。

实现清单：
  - DefaultSecurityGateway : SecurityGateway 的具体实现（正则检测 + 审计决策）
"""

from zephyr.l10_compliance.implementations.default_security_gateway import (
    DefaultSecurityGateway,
)

__all__ = ['DefaultSecurityGateway', 'default_security_gateway']
