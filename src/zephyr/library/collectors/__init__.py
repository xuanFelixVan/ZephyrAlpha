# [BLUEPRINT] MOD-LIB-004 | docs/03_modules/_domain_library/blueprint.md | §4
# [MODULE] zephyr.library.collectors
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""collectors — 图书馆五采集器（MOD-LIB-004）：fs/pg/ch/schtasks/mcp，全部只读。

ingest_all 把采集结果经馆员 act(register) 写入总账（幂等 upsert）。
# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/collectors/__init__.yaml
"""

from __future__ import annotations

from typing import Any, Final

from zephyr.library.librarian import Librarian

__all__ = ["collect_all", "ingest_all"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注（先例=asyncio_run_in_context_gate.py L77）


def collect_all(names: list[str] | None = None) -> dict[str, list[dict[str, Any]]]:
    """运行指定采集器（缺省全部），返回 {采集器名: 资产列表}。

    Args:
        names: 采集器名列表（fs/pg/ch/schtasks/mcp），None=全部。

    Returns:
        采集结果（fail-soft：单采集器异常记入 error 键）。
    """
    from zephyr.library.collectors.ch_collector import collect as ch_collect
    from zephyr.library.collectors.fs_collector import collect as fs_collect
    from zephyr.library.collectors.mcp_collector import collect as mcp_collect
    from zephyr.library.collectors.pg_collector import collect as pg_collect
    from zephyr.library.collectors.schtasks_collector import collect as sch_collect

    registry: dict[str, Any] = {
        "fs": fs_collect,
        "pg": pg_collect,
        "ch": ch_collect,
        "schtasks": sch_collect,
        "mcp": mcp_collect,
    }
    selected = {k: v for k, v in registry.items() if names is None or k in names}
    out: dict[str, list[dict[str, Any]]] = {}
    for name, fn in selected.items():
        try:
            out[name] = fn()
        except Exception as exc:  # noqa: BLE001 — 采集器 fail-soft，错误入结果
            out[name] = [{"error": f"{type(exc).__name__}: {exc}"}]
    return out


def ingest_all(librarian: Librarian, collected: dict[str, list[dict[str, Any]]], actor: str) -> int:
    """把采集结果经馆员批量登记入总账（单事务，幂等）。

    Args:
        librarian: 馆员实例。
        collected: collect_all 的结果。
        actor: 登记会话标识。

    Returns:
        登记条数。
    """
    flat = [asset for assets in collected.values() for asset in assets]
    return librarian.register_batch(flat, actor)
