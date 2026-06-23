# [BLUEPRINT] MOD-INF-012 | docs/03_modules/_cross_layer/database/blueprint.md | §task-system
# [MODULE] zephyr.infrastructure.db.sqlite_schema
# [DOMAIN] D-INFRA_RUNTIME
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema
# [CONSUMERS] Backward-compatible import path for legacy consumers
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Re-export wrapper only; authoritative implementation at zephyr.data.persistence.sqlite_schema
# [MODIFY-GUARD] Do not add logic here; all changes must go to zephyr.data.persistence.sqlite_schema
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] Delegates to zephyr.data.persistence.sqlite_schema
# [TESTS]
# [A_module] module_id=MOD-INF_sqlite_schema | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
Backward-compatible re-export wrapper.

Authoritative implementation: zephyr.data.persistence.sqlite_schema
This module re-exports all public names for legacy import paths.
New code should import from zephyr.governance.persistence.sqlite_schema directly.
"""

from zephyr.governance.persistence.sqlite_schema import *  # noqa: F403
from zephyr.governance.persistence.sqlite_schema import (  # noqa: F401 — explicit re-exports for type checkers
    DB_PATH,
    SchemaManager,
    get_db_connection,
    init_db,
    migration_dry_run,
    schema_version,
    table_names,
    view_names,
)
