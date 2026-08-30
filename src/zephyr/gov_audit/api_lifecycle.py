# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.gov_audit.api_lifecycle
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不可变审计记录;密码学完整性;只追加
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md;src/zephyr/audit-trail/__init__.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] IntegrityError;WriteError
# [TESTS] tests/test_audit_trail/
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: endpoint 参数
#   fields: 参数 endpoint，类型注解 APIEndpoint
#   code: api_lifecycle.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: migration_guide 参数
#   fields: 参数 migration_guide，类型注解 str
#   code: api_lifecycle.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: grace_period_days 参数
#   fields: 参数 grace_period_days，类型注解 int
#   code: api_lifecycle.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① deprecate_api
#   name_en: deprecate_api
#   intro: deprecate_api(endpoint, migration_guide, grace_period_days)…
#   desc: 源码 L112-L126
#   inputs: endpoint migration_guide grace_period_days
#   outputs: DeprecationNotice
# - id: A2
#   name_zh: ② remove_api
#   name_en: remove_api
#   intro: remove_api(endpoint) 源码 L129-L131
#   desc: 源码 L129-L131
#   inputs: endpoint
#   outputs: 返回值
#   （注：A2 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: DeprecationNotice
#   name_en: DeprecationNotice
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import Enum

from pydantic import BaseModel


class APIState(str, Enum):
    ACTIVE = "Active"
    DEPRECATED = "Deprecated"
    REMOVED = "Removed"


class DeprecationNotice(BaseModel):
    api_name: str
    deprecated_at: str
    removal_at: str
    migration_guide: str = ""
    deprecation_header: str = "X-API-Deprecated"
    grace_period_days: int = 90

    @property
    def days_until_removal(self) -> int:
        try:
            dep_dt = datetime.fromisoformat(self.deprecated_at.replace("Z", "+00:00"))
            removal_dt = dep_dt + timedelta(days=self.grace_period_days)
            remaining = (removal_dt - datetime.now(UTC)).days
            return max(0, remaining)
        except (ValueError, TypeError):
            return 0

    @property
    def expired(self) -> bool:
        return self.days_until_removal == 0


class APIEndpoint(BaseModel):
    name: str
    version: str
    state: APIState = APIState.ACTIVE
    deprecation: DeprecationNotice | None = None
    sunset_date: str | None = None


def deprecate_api(
    endpoint: APIEndpoint,
    migration_guide: str = "",
    grace_period_days: int = 90,
) -> DeprecationNotice:
    notice = DeprecationNotice(
        api_name=endpoint.name,
        deprecated_at=datetime.now(UTC).isoformat(),
        removal_at=(datetime.now(UTC) + timedelta(days=grace_period_days)).isoformat(),
        migration_guide=migration_guide,
        grace_period_days=grace_period_days,
    )
    endpoint.state = APIState.DEPRECATED
    endpoint.deprecation = notice
    return notice


def remove_api(endpoint: APIEndpoint) -> None:
    endpoint.state = APIState.REMOVED
    endpoint.sunset_date = datetime.now(UTC).isoformat()
