# [BLUEPRINT] MOD-LIB-004 | docs/03_modules/_domain_library/blueprint.md | §4.3
# [MODULE] zephyr.library.collectors.ch_collector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.schema; zephyr.data.ch_writer (get_client_strict, 统一入口)
# [CONSUMERS] zephyr.library.collectors
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读 system.tables；SQL 模块级常量；CH 不可达返回单条 error 记录（fail-soft）
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任何异常折叠为 [{"error": ...}]（collect_all 兜底）
# [TESTS] tests/library/test_library_smoke.py
# [A_module] module_id=MOD-LIB-004 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ch_collector — 图书馆采集器（MOD-LIB-004，只读）。

# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/collectors/ch_collector.yaml
"""

from __future__ import annotations

from typing import Any, Final

from zephyr.library.ledger_schema import derive_asset_id

__all__ = ["collect"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注（先例=asyncio_run_in_context_gate.py L77）

_SQL_CH_TABLES = """
SELECT database, name, total_rows
FROM system.tables
WHERE database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')
ORDER BY database, name
"""


def collect() -> list[dict[str, Any]]:
    """枚举 CH 全库表，产出 TBL:ch. 资产（含 total_rows）。

    Returns:
        资产字典列表；CH 不可达时返回 [{"error": ...}]。

    """
    try:
        from zephyr.data.ch_writer import get_client_strict

        client = get_client_strict()
        rows = client.execute(_SQL_CH_TABLES)
    except Exception as exc:  # noqa: BLE001 — CH 不可达 fail-soft
        return [{"error": f"{type(exc).__name__}: {exc}"}]
    out: list[dict[str, Any]] = []
    for database, name, total_rows in rows:
        out.append(
            {
                "asset_id": derive_asset_id("table", f"ch:{database}.{name}"),
                "kind": "table",
                "home": f"ch:{database}.{name}",
                "fingerprint_sha256": None,
                "fingerprint_aux": {"total_rows": int(total_rows or 0)},
                "title": f"{database}.{name}",
                "ai_contract": None,
                "owner_domain": None,
                "tags": ["ch"],
            }
        )
    return out
