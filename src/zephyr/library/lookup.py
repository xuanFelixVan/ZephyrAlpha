# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §3
# [MODULE] zephyr.library.lookup
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.registry; zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] scripts/governance/generators/generate_library_index.py; tests/library/test_library_smoke.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读查询；查询入口统一（总口 v1：API+CLI，MCP server W+1 挂接）
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DB 异常原样上抛；CLI 无结果返回 1
# [TESTS] tests/library/test_library_smoke.py
# [A_module] module_id=MOD-LIB-003 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""lookup.py — 图书馆总口查询（MOD-LIB-003）：API + CLI。

Usage::

    python -m zephyr.library.lookup kline_1min
# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/lookup.yaml
"""

from __future__ import annotations

import sys
from typing import Any, Final

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.library.librarian import Librarian

__all__ = ["lookup_assets"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注（先例=asyncio_run_in_context_gate.py L77）


def lookup_assets(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """连接资产总线并执行借阅查询。

    Args:
        query: 查询串（ID/home/标题模糊匹配）。
        limit: 上限。

    Returns:
        资产行列表。
    """
    conn = get_depgraph_pg_connection()
    try:
        return Librarian(conn).lookup(query, limit=limit)
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：打印查询结果表。

    Args:
        argv: 命令行参数（默认 sys.argv[1:]）。

    Returns:
        退出码：0=有结果，1=无结果或用法错误。

    """
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("usage: python -m zephyr.library.lookup <query> [limit]")
        return 1
    limit = 20
    if len(args) > 1:
        try:
            limit = int(args[1])
        except ValueError:
            print(f"invalid limit: {args[1]!r}")
            return 1
        limit = max(1, min(limit, 10000))
    rows = lookup_assets(args[0], limit=limit)
    if not rows:
        print(f"(no results for {args[0]!r})")
        return 1
    for row in rows:
        print(f"{row['asset_id']}\t{row['kind']}\t{row['status']}\t{row['home']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
