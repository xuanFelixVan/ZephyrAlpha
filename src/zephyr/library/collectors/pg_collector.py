# [BLUEPRINT] MOD-LIB-004 | docs/03_modules/_domain_library/blueprint.md | §4.2
# [MODULE] zephyr.library.collectors.pg_collector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.schema; zephyr.governance.depgraph_schema
# [CONSUMERS] zephyr.library.collectors
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读 information_schema；SQL 模块级常量；lib_* 自身表排除（防自吞）
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 连接失败上抛（collect_all fail-soft 兜底）
# [TESTS] tests/library/test_library_smoke.py
# [A_module] module_id=MOD-LIB-004 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""pg_collector — 图书馆采集器（MOD-LIB-004，只读）。

# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/collectors/pg_collector.yaml
"""

from __future__ import annotations

from typing import Any, Final

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.library.ledger_schema import derive_asset_id

__all__ = ["collect"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注（先例=asyncio_run_in_context_gate.py L77）

_SQL_LIST_TABLES = """
SELECT c.relname, c.reltuples::bigint AS est_rows
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public' AND c.relkind = 'r'
ORDER BY c.relname
"""


def collect() -> list[dict[str, Any]]:
    """枚举 depgraph PG 公共表，产出 TBL: 资产（含估算行数）。

    Returns:
        资产字典列表。

    """
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(_SQL_LIST_TABLES)
            rows = cur.fetchall()
    finally:
        conn.close()
    out: list[dict[str, Any]] = []
    for name, est_rows in rows:
        out.append(
            {
                "asset_id": derive_asset_id("table", f"pg:{name}"),
                "kind": "table",
                "home": f"pg:{name}",
                "fingerprint_sha256": None,
                "fingerprint_aux": {"est_rows": max(est_rows, 0)},
                "title": name,
                "ai_contract": None,
                "owner_domain": None,
                "tags": ["pg", "asset_bus"],
            }
        )
    return out
