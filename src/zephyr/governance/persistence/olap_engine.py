# [BLUEPRINT] MOD-INF-012 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.governance.persistence.olap_engine
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.olap_engine
# [CONSUMERS] tests/unit/test_olap_engine_unit.py; tests/unit/db/test_olap_engine_db.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim only; truth source is zephyr.infrastructure.db.olap_engine (trae_046 GOV-ENG-004)
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.infrastructure.db.olap_engine
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if infrastructure.db.olap_engine symbols unavailable
# [TESTS] tests/unit/test_olap_engine_unit.py; tests/unit/db/test_olap_engine_db.py
# [A_module] module_id=MOD-DAT_olap_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""
OLAPEngine re-export shim — 真源已合并至 zephyr.infrastructure.db.olap_engine (trae_046 GOV-ENG-004)。

本文件保留为向后兼容 shim，所有符号从 zephyr.infrastructure.db.olap_engine 重新导出。
新代码应直接 import from zephyr.infrastructure.db.olap_engine。

Import 路径映射:
    from zephyr.governance.persistence.olap_engine import OLAPEngine      -> zephyr.infrastructure.db.olap_engine
    from zephyr.governance.persistence.olap_engine import OLAPEngineError  -> zephyr.infrastructure.db.olap_engine
    from zephyr.governance.persistence.olap_engine import TrendRow        -> zephyr.infrastructure.db.olap_engine
"""

from zephyr.infrastructure.db.olap_engine import (  # noqa: F401
    OLAPEngine,
    OLAPEngineError,
    TrendRow,
)

__all__ = ["OLAPEngine", "OLAPEngineError", "TrendRow"]
