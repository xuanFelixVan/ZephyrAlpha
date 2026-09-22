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


def _suffix_lookup(ds_index: dict[str, dict[str, Any]], table_name: str) -> dict[str, Any]:
    """表名尾段唯一匹配回退（登记表 name 用 dataset 空间名而 CH 物理名不同库前缀时救名_zh）。

    仅尾段（``.name``）唯一命中才采纳；歧义/无匹配 → 空表（退物理名回退，防误挂他表中文名）。
    """
    if not table_name:
        return {}
    hits = [e for k, e in ds_index.items() if k.endswith("." + table_name)]
    return hits[0] if len(hits) == 1 else {}


def _load_ds_index() -> dict[str, dict[str, Any]]:
    """读 data_asset_registry（REG-DATAFLOW-001）clickhouse_table 条目索引（ulib3 T11 两册连线）。

    键=物理全限定名（如 ``c1_market.kline_daily``）——TBL 空壳回填 owner_domain/name_zh 的
    SSOT 反查面。读取失败返回空 dict（fail-soft，退化为原空壳行为）。
    """
    try:
        from pathlib import Path

        import yaml

        from zephyr.shared.io.paths import REPO_ROOT

        reg = REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml"
        data = yaml.safe_load(reg.read_text(encoding="utf-8")) or {}
        index: dict[str, dict[str, Any]] = {}
        for e in data.get("datasets") or []:
            if str(e.get("physical_type") or "") != "clickhouse_table":
                continue
            name = str(e.get("name") or "").strip()
            if name:
                index[name] = e
        return index
    except Exception as exc:  # noqa: BLE001 — fail-soft（空壳退化）
        return {"_error": {"msg": f"{type(exc).__name__}: {exc}"}}


def collect() -> list[dict[str, Any]]:
    """枚举 CH 全库表，产出 TBL:ch. 资产（含 total_rows；DS 反查回填归属，ulib3 T11）。

    Returns:
        资产字典列表；CH 不可达时返回 [{"error": ...}]。

    """
    try:
        from zephyr.data.ch_writer import get_client_strict

        client = get_client_strict()
        rows = client.execute(_SQL_CH_TABLES)
    except Exception as exc:  # noqa: BLE001 — CH 不可达 fail-soft
        return [{"error": f"{type(exc).__name__}: {exc}"}]
    ds_index = _load_ds_index()
    out: list[dict[str, Any]] = []
    for database, name, total_rows in rows:
        physical = f"{database}.{name}"
        ds = ds_index.get(physical) or _suffix_lookup(ds_index, name)
        owner_domain = ds.get("domain_id")
        title = ds.get("name_zh") or physical
        ai_contract = None
        if ds:
            ai_contract = (
                f"CH 表（data_asset_registry {ds.get('dataset_id', '')}）：{ds.get('format_summary', '')}。"
                f"生产方={ds.get('produced_by_job') or ds.get('owner') or '未登记'}。"
            )
        out.append(
            {
                "asset_id": derive_asset_id("table", f"ch:{database}.{name}"),
                "kind": "table",
                "home": f"ch:{database}.{name}",
                "fingerprint_sha256": None,
                "fingerprint_aux": {"total_rows": int(total_rows or 0)},
                "title": title,
                "ai_contract": ai_contract,
                "owner_domain": owner_domain,
                "tags": ["ch"],
            }
        )
    return out
