# [MODULE] zephyr.governance.registry_ledger
# [DOMAIN] D_GOVERNANCE
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [TTL] permanent
"""注册表 PG 行级账本（W-M1 车道A·波0 底座）。

真源：docs/_working/registry_migration/02_ledger_design.md §2-§3（D1-D6/A1-A3 已批）。
三件套：deploy.py 幂等 DDL 部署器；api.py 意图 API（register/update/retire 按条目声明，
禁整文件接口）；identity.py 条目身份键（gate 真源复用，永不复制逻辑）。
DDL 真源=schemas/categories/registry_ledger/（DDL-as-Code 唯一真源）。


# [ALGO_FLOW]
层: 出口
- 聚合再导出意图 API 公共面（register/update/retire/takeover/fetch_entry/Result），无独立算法流程"""

from typing import Final

from zephyr.governance.registry_ledger.api import (
    AUTHORITY_REQUIRED,
    CONFLICT_DUPLICATE,
    CONFLICT_VERSION,
    FORBIDDEN_FORCE,
    INVALID_ARGUMENT,
    NOT_FOUND,
    OK,
    OK_NOOP,
    SCHEMA_INVALID,
    Result,
    register,
    retire,
    takeover,
    update,
)
from zephyr.governance.registry_ledger.deploy import (
    SCHEMA_NAME,
    deploy_registry_ledger,
    schema_fingerprint,
)

__all__: Final = [
    "INVALID_ARGUMENT",
    "AUTHORITY_REQUIRED",
    "CONFLICT_DUPLICATE",
    "CONFLICT_VERSION",
    "FORBIDDEN_FORCE",
    "NOT_FOUND",
    "OK",
    "OK_NOOP",
    "SCHEMA_INVALID",
    "Result",
    "register",
    "update",
    "retire",
    "takeover",
    "SCHEMA_NAME",
    "deploy_registry_ledger",
    "schema_fingerprint",
]
