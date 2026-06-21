# [A_module] module_id=MOD-INF_sqlite_schema | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-012 | docs/03_modules/_cross_layer/database/blueprint.md | §task-system

# [MODULE] zephyr.infrastructure.db.sqlite_schema

# [INVARIANTS] Re-export wrapper only; authoritative implementation at zephyr.data.persistence.sqlite_schema

# [MODIFY-GUARD] Do not add logic here; all changes must go to zephyr.data.persistence.sqlite_schema

# [CONSUMERS] Backward-compatible import path for legacy consumers

# [STABILITY] frozen

# [SAFETY] L

# [AI_AUTONOMY] immutable_core

# [ERROR_CONTRACT] Delegates to zephyr.data.persistence.sqlite_schema

# [TESTS]

"""
Backward-compatible re-export wrapper.

Authoritative implementation: zephyr.data.persistence.sqlite_schema
This module re-exports all public names for legacy import paths.
New code should import from zephyr.governance.persistence.sqlite_schema directly.
"""
from zephyr.governance.persistence.sqlite_schema import *  # noqa: F401,F403
from zephyr.governance.persistence.sqlite_schema import (  # noqa: F401 — explicit re-exports for type checkers
    DB_PATH,
    init_db,
    get_db_connection,
    table_names,
    view_names,
    schema_version,
    migration_dry_run,
    SchemaManager,
)
