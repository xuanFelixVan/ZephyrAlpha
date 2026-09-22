# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §3
# [MODULE] zephyr.library.lookup
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.registry; zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.shared.io.yaml_utils (load_vocabulary_alias_map)
# [CONSUMERS] scripts/governance/generators/generate_library_index.py; tests/library/test_library_smoke.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读查询；查询入口统一（总口：API+CLI；T5 两轴过滤器 kind/owner_domain/tags/status/home 前缀组合筛选+回测产物查询面）；G15-① 别名轴=查询词先过词表归一（近似词→标准词→match_tokens 资产 token）再匹配，fail-open 词表不可用退原词；MCP server W+1 挂接
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DB 异常原样上抛；CLI 无结果返回 1
# [TESTS] tests/library/test_library_smoke.py; tests/library/test_lookup_alias.py
# [A_module] module_id=MOD-LIB-003 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 总目查询 CLI（python -m zephyr.library.lookup）人工按需调用是设计形态，非常驻系统
"""lookup.py — 图书馆总口查询（MOD-LIB-003）：API + CLI。

Usage::

    python -m zephyr.library.lookup kline_1min
    python -m zephyr.library.lookup kline --kind table --owner-domain D_DATA --tags ch,行情
    python -m zephyr.library.lookup 融资融券            # G15-① 别名轴：→杠杆→margin_trading
    python -m zephyr.library.lookup --backtest --strategy my_strat --since 2026-09-01 --until 2026-09-22
# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/lookup.yaml
"""

from __future__ import annotations

import argparse
import sys
from typing import Any, Final

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.library.librarian import Librarian

__all__ = ["lookup_assets"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注（先例=asyncio_run_in_context_gate.py L77）

_BACKTEST_HOME_PREFIX: Final[str] = "data/backtest_artifacts/"
_BACKTEST_LOG_HINT: Final[str] = "回测运行日志抽屉：logs/c1_repro/、logs/c1_real_*.log（族级入册=T10，明细见 registry_of_logs.yaml）"
_VOCAB_REL: Final[str] = "docs/01_policies_and_standards/_registry/catalogs/library_tag_vocabulary.yaml"


def _load_lookup_axis() -> tuple[dict[str, str], dict[str, list[str]]]:
    """G15-① 别名轴装载（fail-open）：返回 (别名→标准词, 标准词→match_tokens)。

    真源=library_tag_vocabulary.yaml（与 TAG-VOCAB 闸同源）：aliases 层走
    yaml_utils.load_vocabulary_alias_map；match_tokens 层直接读同一 SSOT 文件——
    同一 token 可被多个标准词复用（如 stock_daily_basic 同喂拥挤度/每日基本面），
    单键别名装载器会静默吞重键，故 match_tokens 走多值直读。
    词表缺失/结构漂移一律返回空映射（退化为原词直查=行为向前兼容）。
    """
    from pathlib import Path as _Path  # noqa: PLC0415

    import yaml  # noqa: PLC0415

    from zephyr.shared.io.paths import REPO_ROOT  # noqa: PLC0415 — 懒加载避免 import 期依赖
    from zephyr.shared.io.yaml_utils import load_vocabulary_alias_map  # noqa: PLC0415

    try:
        vocab_path = _Path(REPO_ROOT) / _VOCAB_REL
        _, alias_to_canonical = load_vocabulary_alias_map(vocab_path, strict=False)
        canonical_to_tokens: dict[str, list[str]] = {}
        for entry in (yaml.safe_load(vocab_path.read_text(encoding="utf-8")) or {}).get("values") or []:
            word = entry.get("value") if isinstance(entry, dict) else None
            tokens = entry.get("match_tokens") if isinstance(entry, dict) else None
            if word and tokens:
                canonical_to_tokens.setdefault(str(word), []).extend(str(t) for t in tokens)
        return alias_to_canonical, canonical_to_tokens
    except Exception:  # noqa: BLE001 — fail-open：词轴故障不影响原词直查主路径
        return {}, {}


def _expand_query(query: str) -> list[str]:
    """查询词归一展开：原词 + （别名→标准词） + （标准词→match_tokens），去重保序。

    仅整词精确命中词表才展开（模糊/自由文本原样直查）；原词恒在首位（精确原词命中优先）。
    模块开关 _alias_expansion_enabled=False 时透传原词（CLI --no-alias）。
    """
    if not _alias_expansion_enabled:
        return [query]
    alias_map, canonical_to_tokens = _load_lookup_axis()
    terms: list[str] = [query]
    q = query.strip()
    canonical = alias_map.get(q)
    if canonical and canonical not in terms:
        terms.append(canonical)
    for token in canonical_to_tokens.get(canonical or q, []):
        if token not in terms:
            terms.append(token)
    return terms


#: G15-① 别名轴进程级开关（CLI --no-alias 置 False；模块级 bool 非 mutable 容器）
_alias_expansion_enabled = True


def lookup_assets(
    query: str,
    limit: int = 20,
    *,
    kind: str | None = None,
    owner_domain: str | None = None,
    tags: list[str] | None = None,
    status: str | None = None,
    home_prefix: str | None = None,
) -> list[dict[str, Any]]:
    """连接资产总线并执行借阅查询（T5 组合过滤器透传；G15-① 别名轴默认展开，模块开关可关）。"""
    conn = get_depgraph_pg_connection()
    try:
        lib = Librarian(conn)
        terms = _expand_query(query)
        per_term = [
            lib.lookup(
                term,
                limit=limit,
                kind=kind,
                owner_domain=owner_domain,
                tags=tags,
                status=status,
                home_prefix=home_prefix,
            )
            for term in terms
        ]
        # 逐深度轮转合并：同深度上原词（terms[0]）优先，展开词首命中不被原词长尾挤掉
        merged: dict[str, dict[str, Any]] = {}
        for depth in range(limit):
            for rows in per_term:
                if depth >= len(rows):
                    continue
                row = rows[depth]
                merged.setdefault(row["asset_id"], row)
                if len(merged) >= limit:
                    return list(merged.values())[:limit]
        return list(merged.values())[:limit]
    finally:
        conn.close()


def _query_backtest(strategy: str | None, since: str | None, until: str | None, limit: int) -> int:
    """回测产物查询面（增量A）：按策略/日期段列产物+关联日志抽屉提示。退出码语义同主查询。"""
    import json  # noqa: PLC0415 — 懒加载

    from zephyr.backtest.io.result_repository import list_artifacts  # noqa: PLC0415 — 懒加载避免 CLI 常规路径依赖回测域
    from zephyr.shared.io.paths import REPO_ROOT  # noqa: PLC0415

    storage = REPO_ROOT / _BACKTEST_HOME_PREFIX
    run_ids = list_artifacts(strategy_id=strategy, storage_path=storage)
    hits = 0
    for run_id in run_ids:
        f = storage / f"{run_id}.json"
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        created_at = str(d.get("created_at", ""))
        if since and created_at[:10] < since:
            continue
        if until and created_at[:10] > until:
            continue
        print(f"{run_id}\t{d.get('strategy_id', '*')}\t{created_at}\t{f}")
        hits += 1
        if hits >= limit:
            break
    if not hits:
        print("(no backtest artifacts matched)")
        return 1
    print(_BACKTEST_LOG_HINT)
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：打印查询结果表。

    Args:
        argv: 命令行参数（默认 sys.argv[1:]）。

    Returns:
        退出码：0=有结果，1=无结果或用法错误。

    """
    parser = argparse.ArgumentParser(prog="zephyr.library.lookup", description="图书馆总口查询（T5 两轴过滤器）")
    parser.add_argument("query", nargs="?", default="", help="查询串（ID/home/标题模糊匹配）")
    parser.add_argument("limit_pos", nargs="?", type=int, default=None, help="上限（位置式旧用法）")
    parser.add_argument("--limit", type=int, default=20, help="上限（默认 20，最大 10000）")
    parser.add_argument("--kind", default=None, help="kind 精确过滤（12 枚举，如 table/module/file）")
    parser.add_argument("--owner-domain", default=None, help="owner_domain 精确过滤（83 域，如 D_DATA）")
    parser.add_argument("--tags", default=None, help="tags 过滤（逗号分隔多值 AND，如 ch,行情）")
    parser.add_argument("--status", default=None, help="status 精确过滤（active/stale/...）")
    parser.add_argument("--home-prefix", default=None, help="home 前缀过滤（如 TBL:ch:）")
    parser.add_argument("--backtest", action="store_true", help="回测产物查询面（按策略/日期段列产物+日志抽屉提示）")
    parser.add_argument("--no-alias", action="store_true", help="关闭 G15-① 别名轴展开（原词直查）")
    parser.add_argument("--strategy", default=None, help="[backtest] 策略 ID 过滤")
    parser.add_argument("--since", default=None, help="[backtest] 起始日期 YYYY-MM-DD（含）")
    parser.add_argument("--until", default=None, help="[backtest] 截止日期 YYYY-MM-DD（含）")
    args = parser.parse_args(argv)

    if args.backtest:
        return _query_backtest(args.strategy, args.since, args.until, max(1, min(args.limit, 10000)))

    if not args.query:
        parser.print_usage()
        return 1
    limit = args.limit_pos if args.limit_pos is not None else args.limit
    limit = max(1, min(limit, 10000))
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None
    if args.no_alias:
        globals()["_alias_expansion_enabled"] = False
    else:
        expanded = _expand_query(args.query)
        if expanded != [args.query]:
            print(f"[alias] {args.query!r} -> {' -> '.join(expanded)}", file=sys.stderr)
    rows = lookup_assets(
        args.query,
        limit=limit,
        kind=args.kind,
        owner_domain=args.owner_domain,
        tags=tags,
        status=args.status,
        home_prefix=args.home_prefix,
    )
    if not rows:
        print(f"(no results for {args.query!r})")
        return 1
    for row in rows:
        print(f"{row['asset_id']}\t{row['kind']}\t{row['status']}\t{row['home']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
