# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §3
# [MODULE] zephyr.library.lookup
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.registry; zephyr.governance.depgraph_schema (get/release_depgraph_pg_connection); zephyr.library.librarian; zephyr.library.ledger_cache (世代缓存读侧); zephyr.shared.io.yaml_utils (load_vocabulary_alias_map)
# [CONSUMERS] scripts/governance/generators/generate_library_index.py; tests/library/test_library_smoke.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读查询；查询入口统一（总口：API+CLI；T5 两轴过滤器 kind/owner_domain/tags/status/home 前缀组合筛选+回测产物查询面）；G15-① 别名轴=查询词先过词表归一（近似词→标准词→match_tokens 资产 token）再匹配，fail-open 词表不可用退原词；MCP server W+1 挂接；读侧接入世代缓存（lib_ram_campaign R1）：命中即零账本数据 SQL，水位翻代才重建，LIBRAM_DIRECT=1 逃生直查——供数反查面 --feeds 恒现读（未携 potential_consumers 列，禁跨代拼装）；连接借还成对（get→release，禁 close 弃池）；读侧存在性标注（st-libstale-20261013）：file/doc/module 三类的 home 现判盘上存在性，missing 只加尾标 [missing-on-disk]（--hide-missing 可剔除），命名空间型/含冒号 home 恒不判（宁缺毋滥），零账本写零 status 改口径
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DB 异常原样上抛；CLI 无结果返回 1
# [TESTS] tests/ai/library/test_library_smoke.py; tests/ai/library/test_lookup_alias.py; tests/ai/library/test_ledger_cache.py; tests/ai/library/test_lookup_on_disk_marker.py
# [A_module] module_id=MOD-LIB-003 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 总目查询 CLI（python -m zephyr.library.lookup）人工按需调用是设计形态，非常驻系统
"""lookup.py — 图书馆总口查询（MOD-LIB-003）：API + CLI。

Usage::

    python -m zephyr.library.lookup kline_1min
    python -m zephyr.library.lookup kline --kind table --owner-domain D_DATA --tags ch,行情
    python -m zephyr.library.lookup 融资融券            # G15-① 别名轴：→杠杆→margin_trading
    python -m zephyr.library.lookup --backtest --strategy my_strat --since 2026-09-01 --until 2026-09-22
    python -m zephyr.library.lookup kline_1min --session st-xxx   # 审计留痕（裁定#460 ②，fail-open）
    python -m zephyr.library.lookup state "GPU 摊销"   # state 子命令：资产状态三源证据包（馆索引+git log+工棚/挂账面）
# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/lookup.yaml
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:  # Path 仅供注解（惰性字符串）；运行时零导入成本，守 import 面预算
    from pathlib import Path

from zephyr.library import ledger_cache
from zephyr.library.ledger_cache import LedgerFilters
from zephyr.library.librarian import Librarian

# R4（st-fms-tc-20260927）：池化连接件（zephyr.governance.depgraph_schema）只在两条腿用到
# ——_lookup_terms_via_sql（缓存旁路/无缓存位）与 _run_feeds_query（--feeds），而
# commit-guide:/--backtest 两条 CLI 腿与世代缓存命中腿都不碰 PG。原模块级 import 让
# "只要一个查询函数"的消费方（门禁探针）也为连接层买单，故下沉到使用点（同仓惯例
# =scripts/backup/library_ledger_backup.py 的 refresh_snapshot 与本文件 _load_lookup_axis）。
# 语义逐字不变：两条腿仍各借还一次连接，DB 异常仍原样上抛（ERROR_CONTRACT 不变）。

__all__ = ["lookup_assets"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注（先例=asyncio_run_in_context_gate.py L77）

_BACKTEST_HOME_PREFIX: Final[str] = "data/backtest_artifacts/"
_COMMIT_GUIDE_PREFIX: Final[str] = "commit-guide:"
_RULING_PREFIX: Final[str] = "ruling:"
_COMMIT_GUIDE_PLAYBOOK_REL: Final[str] = (
    "docs/01_policies_and_standards/sop/governance_sop/commit_navigation_playbook.md"
)
_BACKTEST_LOG_HINT: Final[str] = (
    "回测运行日志抽屉：logs/c1_repro/、logs/c1_real_*.log（族级入册=T10，明细见 registry_of_logs.yaml）"
)
_VOCAB_REL: Final[str] = "docs/01_policies_and_standards/_registry/catalogs/library_tag_vocabulary.yaml"

# ─── 读侧"盘上存在性"标注（st-libstale-20261013，纯视图面，零账本写）─────────────
# 起因：lib_assets status='active' 的行里 11.7%（43,367 中 5,086）home 既不在盘上也不在
# git HEAD——账本 INVARIANT"零删除零状态改写"决定了这类行只能人工死亡证明退账，而读侧
# 一直在把它们当"在编资产"回给 agent（含防重复施工探针）。本面只在出口标注/剔除，
# 不碰 status 口径（撤账属 Owner 终裁治理面）。
_ON_DISK_JUDGED_KINDS: Final[frozenset[str]] = frozenset({"file", "doc", "module"})
_MISSING_ON_DISK_MARKER: Final[str] = " [missing-on-disk]"
_MISSING_ON_DISK_FOOTER: Final[str] = (
    "# view-only: {n}/{t} 行 home 盘上不存在{hidden}（仅出口标注，账本 status 未改；剔除用 --hide-missing）"
)

# ─── state 子命令常量（F1 资产状态断言·三源模式，st-examchief-20261009）───────
_STATE_WORKSHOP_REL: Final[str] = "docs/_working"
_STATE_CONFIG_REL: Final[str] = "config"
_STATE_GIT_SINCE: Final[str] = "--since=90.days"
_STATE_SOURCE_LINE_CAP: Final[int] = 15  # 单源输出行上限（F1 规格 2）
_STATE_INDEX_ROW_CAP: Final[int] = 10  # 源① 馆内条目上限
_STATE_GIT_PATHS_DIR_CAP: Final[int] = 6  # 源② touched-paths·目录命中组总配额（工棚战役目录）
_STATE_GIT_PATHS_DIR_SUB_CAP: Final[int] = 3  # 源② 目录命中组·单目录子查询配额
_STATE_GIT_PATHS_OTHER_CAP: Final[int] = 2  # 源② touched-paths·内容命中组配额（挂账册等）
_STATE_GIT_PATHSPEC_CAP: Final[int] = 40  # 源③回喂源②的 pathspec 总量上限
_STATE_GIT_PICKAXE_CAP: Final[int] = 5  # 源② pickaxe 全串配额
_STATE_GIT_PICKAXE_WORD_CAP: Final[int] = 2  # 源② pickaxe 逐词配额（防高频词淹没）
_STATE_GIT_GREP_CAP: Final[int] = 15  # 源② grep 通道配额（合并后仍截 15）
_STATE_GIT_LINE_WIDTH: Final[int] = 200  # oneline 超长提交消息截断宽
_STATE_EXCERPT_WIDTH: Final[int] = 180  # 源③ 命中行摘录截断宽
_STATE_EXCERPTS_PER_FILE: Final[int] = 1  # 源③ 单文件摘录上限（全词同现文件各取其最佳 1 行）
_STATE_EXCERPT_BUDGET_TOTAL: Final[int] = 3  # 源③ 摘录总额（其余预算让位给文件列名行）
_STATE_SCAN_MAX_FILE_BYTES: Final[int] = 1_000_000  # 内容扫描单文件字节上限
_STATE_SCAN_MAX_FILES: Final[int] = 6000  # 内容扫描文件总数上限
_STATE_SCAN_HITLINES_PER_FILE: Final[int] = 200  # 单文件内容命中采集上限
_STATE_SKIP_DIRS: Final[frozenset[str]] = frozenset({"__pycache__", "node_modules"})


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


def _lookup_terms_via_sql(terms: list[str], limit: int, filters: LedgerFilters) -> list[list[dict[str, Any]]]:
    """直查真源腿（缓存旁路/无缓存位走这里）：一条池化连接借还一次，用毕**归还**而非 close。

    conn.close() 会让 per-role 池（min1/max5）反复回收槽位、失去复用收益（§5.64.1 反模式，
    归还接口 release_depgraph_pg_connection）；tags 空元组按 None 透传（=SQL 侧无该过滤器）。
    """
    from zephyr.governance.depgraph_schema import (  # noqa: PLC0415 — R4 惰性化（见模块头注释）
        get_depgraph_pg_connection,
        release_depgraph_pg_connection,
    )

    conn = get_depgraph_pg_connection()
    try:
        lib = Librarian(conn)
        return [
            lib.lookup(
                term,
                limit=limit,
                kind=filters.kind,
                owner_domain=filters.owner_domain,
                tags=list(filters.tags) or None,
                status=filters.status,
                home_prefix=filters.home_prefix,
            )
            for term in terms
        ]
    finally:
        release_depgraph_pg_connection(conn)


def _merge_per_term(per_term: list[list[dict[str, Any]]], limit: int) -> list[dict[str, Any]]:
    """逐深度轮转合并：同深度上原词（terms[0]）优先，展开词首命中不被原词长尾挤掉。"""
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
    """连接资产总线并执行借阅查询（T5 组合过滤器透传；G15-① 别名轴默认展开，模块开关可关）。

    读侧世代缓存（lib_ram_campaign R1）：水位未变即纯内存匹配（零账本数据 SQL，仅 1 次
    O(1) 水位探测），水位翻代才 single-flight 重建；``LIBRAM_DIRECT=1`` 逃生旁路直查真源。
    写侧与对账面（Librarian 注入连接 / _SQL_* 直查）不经本函数，故 S4 §⑤ 不可缓存位天然隔离。
    """
    filters = LedgerFilters(
        kind=kind,
        owner_domain=owner_domain,
        tags=tuple(tags or ()),
        status=status,
        home_prefix=home_prefix,
    )
    terms = _expand_query(query)
    if ledger_cache.cache_enabled():
        per_term = [ledger_cache.search(term, limit, filters) for term in terms]
    else:
        per_term = _lookup_terms_via_sql(terms, limit, filters)
    return _merge_per_term(per_term, limit)


def _query_commit_guide(topic: str) -> int:
    """提交指路指南查询面（st-commitsys×st-library 协同，机生 playbook 的投影检索）。

    用法::

        python -m zephyr.library.lookup commit-guide:            # 全部锚点目录
        python -m zephyr.library.lookup commit-guide:FT-py       # 类型节全文
        python -m zephyr.library.lookup commit-guide:SESSION-REQUIRED  # gate 卡全文

    topic 匹配规则：空=列锚点目录；精确锚点=节全文；其余=子串检索命中的节全文（≤3 节）。
    指南真源=机生 playbook（禁手改），本面只读投影零第二真源。
    """
    from zephyr.shared.io.paths import REPO_ROOT  # noqa: PLC0415

    playbook = REPO_ROOT / _COMMIT_GUIDE_PLAYBOOK_REL
    if not playbook.exists():
        print(f"(commit guide playbook missing: {_COMMIT_GUIDE_PLAYBOOK_REL})")
        return 1
    sections: list[tuple[str, list[str]]] = []
    for line in playbook.read_text(encoding="utf-8").splitlines():
        if line.startswith(("## ", "### ")):
            sections.append((line, []))
        elif sections:
            sections[-1][1].append(line)
    topic = topic.strip()
    if not topic:
        print(f"commit-guide anchors ({len(sections)} sections):")
        for head, _ in sections:
            print(f"  {head}")
        return 0
    matched = [(h, body) for h, body in sections if topic in h]
    if not matched:
        matched = [(h, body) for h, body in sections if topic in " ".join(body)][:3]
    if not matched:
        print(f"(no commit-guide section matching {topic!r})")
        return 1
    for head, body in matched[:3]:
        print(head)
        text = "\n".join(body).strip()
        print(text[:2000])
        print()
    return 0


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


def _successor_display(row: dict[str, Any]) -> str:
    """墓碑去向渲染（08 词典 §6 successor_of 两态纪律）。

    非空串=后继资产 asset_id（照直显示）；''=确认无后继；NULL=未评估→退显
    disposition_authority 前 40 字符作墓志铭（无批文则示"去向未评估"）。
    行键缺失（旧调用方/旧快照）一律按未评估处理，永不抛异常。
    """
    successor = row.get("successor_of")
    if successor is None:
        authority = str(row.get("disposition_authority") or "").strip()
        return f"去向未评估｜墓志:{authority[:40]}" if authority else "去向未评估"
    text = str(successor).strip()
    return text if text else "(无后继)"


def _tombstone_tail(row: dict[str, Any]) -> str:
    """deceased 行尾墓碑尾巴（``\\t-> 去向``）；非 deceased 行恒返回空串。"""
    if row.get("status") != "deceased":
        return ""
    return f"\t-> {_successor_display(row)}"


def _on_disk_state(home: str | None, kind: str | None, root: Path) -> str:
    """行级"盘上存在性"现判（纯视图，零账本写）：present / missing / unknown。

    只判带仓内路径的三类 kind（_ON_DISK_JUDGED_KINDS）；命名空间型 home（含 ``:``
    且非盘符，如 ``schtasks:\\...``/``TBL:ch:...``）恒 unknown——把"账本没这个概念"
    误读成"资产已消失"比漏标更致命，故判据不确定时不判。
    """
    if kind not in _ON_DISK_JUDGED_KINDS:
        return "unknown"
    text = str(home or "").strip()
    if not text:
        return "unknown"
    import os  # noqa: PLC0415 — 惰性 stdlib（保 import 计时面，R4 同法）

    if len(text) >= 2 and text[1] == ":" and text[0].isalpha():  # 盘符绝对路径（仓外资产）
        return "present" if os.path.exists(text) else "missing"
    if ":" in text:
        return "unknown"
    return "present" if os.path.exists(root / text.replace("/", os.sep)) else "missing"


def _on_disk_root() -> Path:
    """存在性判定基准根（=本次运行的 checkout 根，非另一条车道的盘面）。"""
    from zephyr.shared.io.paths import REPO_ROOT  # noqa: PLC0415 — 惰性（CLI 计时面）

    return REPO_ROOT


def _annotate_on_disk(
    rows: list[dict[str, Any]], *, hide_missing: bool, root: Path | None = None
) -> tuple[list[tuple[dict[str, Any], str]], int]:
    """把行集按盘上存在性判读一遍，返回 (保留的 (row, state) 序, missing 计数)。

    视图层唯一入口：不改 row 内容、不写账本、不动 status 口径——世代缓存里的行
    因此永不被污染（污染会让"存在性"自身变成旧代）。
    """
    base = root if root is not None else _on_disk_root()
    judged = [(row, _on_disk_state(row.get("home"), row.get("kind"), base)) for row in rows]
    missing = sum(1 for _, state in judged if state == "missing")
    if hide_missing:
        judged = [pair for pair in judged if pair[1] != "missing"]
    return judged, missing


def _run_feeds_query(keyword: str, limit: int) -> int:
    """供数反查面（裁定#410）：potential_consumers 含关键词的资产清单。

    恒现读真源（不经世代缓存）：potential_consumers 属写侧对账轴，世代快照未携该列
    ——宁可多一次查询，也不让供数反查读到旧代（S4 §⑤ 不可缓存位；同代化留 R2 判）。
    空结果两态披露（K10 措辞）：该腿 SQL 只带 limit、关键词在 Python 侧过滤，
    故 0 行既可能是"整轴零供给"也可能是"轴上有供给而此词未命中（且受 limit 截断）"——
    两态含义相反，混为一谈会把"查空"读成"查无"。零供给态只在同面空关键词探针亦 0 行
    时才宣布；探针仅在未命中路径上发生（命中路径零额外查询）。
    """
    from zephyr.governance.depgraph_schema import (  # noqa: PLC0415 — R4 惰性化（见模块头注释）
        get_depgraph_pg_connection,
        release_depgraph_pg_connection,
    )

    conn = get_depgraph_pg_connection()
    try:
        lib = Librarian(conn)
        rows = lib.lookup_by_feeds(keyword, limit=limit)
        supply = [] if rows else lib.lookup_by_feeds("", limit=limit)
    finally:
        release_depgraph_pg_connection(conn)
    if not rows:
        if not supply:
            print(
                f"(no assets feeding {keyword!r}: 供数轴现面零供给——同面同 limit 的空关键词探针亦 0 行，"
                "即 lib_assets.potential_consumers 非空行本身为 0；本结果不等于'该关键词无消费者'，"
                "供数写侧采集器未接线为在册缺口)"
            )
        else:
            print(
                f"(no assets feeding {keyword!r}: 供数轴现有 {len(supply)} 行供给"
                f"（同面 limit={limit} 截断后未命中，不等于无消费者)"
            )
        return 1
    for row in rows:
        consumers = ",".join(row.get("potential_consumers") or [])
        print(f"{row['asset_id']}	{row['kind']}	{consumers}")
    return 0


def _run_main_query(args: argparse.Namespace, parser: argparse.ArgumentParser) -> tuple[int, list[dict[str, Any]]]:
    """主查询面：别名展开提示 + lookup_assets 结果表 + 墓碑去向升级提示。

    Returns:
        (退出码, 结果行列表)——退出码语义不变（0=有结果，1=无结果或用法错误）；
        行列表供 main() 在 --session 审计留痕时取 result_count（裁定#460 ②）。
    """
    if not args.query:
        parser.print_usage()
        return 1, []
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
        return 1, []
    judged, missing_n = _annotate_on_disk(rows, hide_missing=bool(getattr(args, "hide_missing", False)))
    if not judged:
        print(f"(no results for {args.query!r})")
        return 1, []
    for row, state in judged:
        marker = _MISSING_ON_DISK_MARKER if state == "missing" else ""
        print(f"{row['asset_id']}\t{row['kind']}\t{row['status']}\t{row['home']}{_tombstone_tail(row)}{marker}")
    if missing_n:
        hidden = len(rows) - len(judged)
        print(
            _MISSING_ON_DISK_FOOTER.format(n=missing_n, t=len(rows), hidden=f"｜已剔除 {hidden} 行" if hidden else "")
        )
    kept = [row for row, _ in judged]
    # 墓碑卡升级：全结果无 active 命中但有 deceased 命中=路径已迁移，报去向而非死账
    if not any(r.get("status") == "active" for r in kept) and any(r.get("status") == "deceased" for r in kept):
        dead = next(r for r in kept if r.get("status") == "deceased")
        print(f"(moved: {dead['asset_id']} -> {_successor_display(dead)})")
    return 0, kept


def _write_cli_audit(session_id: str, query_payload: dict[str, Any], result_count: int) -> None:
    """CLI 反查审计留痕（裁定#460 ②）：复用 capability_lookup.write_lookup_audit_log 现成通道。

    与 CapabilityLookup.find（capability_lookup.py:941）同一落盘面
    （.runtime/lookup_audit/<sid>.jsonl），tool="zephyr.library.lookup"——CAPABILITY-LOOKUP
    审计链据此识别图书馆总口 CLI 路径的反查留痕。fail-open 双层：write_lookup_audit_log
    自身吞写入异常仅告警，本侧再兜 import 失败等意外——审计故障绝不阻断查询主路径；
    未提供 --session 时本函数不被调用（行为零变化）。
    """
    try:
        from zephyr.governance.capability_lookup import (  # noqa: PLC0415 — 懒加载防循环依赖
            write_lookup_audit_log,
        )

        write_lookup_audit_log(
            session_id=session_id,
            query=query_payload,
            result_count=result_count,
            capability_ids=[],
            tool="zephyr.library.lookup",
        )
    except Exception as exc:  # noqa: BLE001 — fail-open：审计故障不阻断查询（ERROR_CONTRACT 不变）
        logging.getLogger(__name__).warning("library.lookup: --session 审计留痕失败（fail-open）: %s", exc)


# ═══ state 子命令（F1 资产状态断言·三源模式，st-examchief-20261009）═════════════
# 起因：docs/_working/ 是图书馆场外区（fs_collector._SKIP_DIRS 跳过，梵蒂冈条款），馆查
# 不到场外落地证据，而 agent 无便捷 git log 通道——规划轮曾误报 GPU 摊销"未做"。
# state 一条命令返回三源证据包：①馆索引 ②git log（grep/pickaxe/touched-paths 三通道）
# ③工棚+挂账面（docs/_working + config 内容扫描）。只读零副作用；负存在断言
# （"查过且无"）由 -- no hits -- 与 sources-with-hits 计数承载。


def _state_words(query: str) -> list[str]:
    """搜词拆分：按空白拆词去重保序（"GPU 摊销"→["GPU","摊销"]；中文 git 通道逐词可用）。"""
    words: list[str] = []
    for word in query.split():
        if word not in words:
            words.append(word)
    return words


def _state_snapshot_line() -> str:
    """时间戳头（规格 2）：ISO8601 带本地时区偏移（如 +08:00），三源共用同一读数。"""
    from datetime import UTC, datetime  # noqa: PLC0415 — 惰性 stdlib（保 import 计时面，R4 同法）

    return f"state-snapshot at {datetime.now(UTC).astimezone().isoformat(timespec='seconds')}"


def _state_truncate(line: str, width: int) -> str:
    """定宽截断（超长提交消息/命中行摘录保输出可读，哈希与前缀证据保全）。"""
    text = line.rstrip()
    return text if len(text) <= width else text[:width] + "…"


def _run_git(args: list[str], repo_root: str | Path) -> str:
    """只读 git 调用：stdout 按 UTF-8 解码（win32 下 git 输出恒 UTF-8，errors=replace 防炸）。

    经 run_subprocess_hidden 统一入口（TRAE-067 铁律2 CREATE_NO_WINDOW，BARE-SUBPROCESS 处方）。
    """
    import subprocess  # noqa: PLC0415 — 惰性 stdlib（保 import 计时面，R4 同法）

    from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: PLC0415

    try:
        proc = run_subprocess_hidden(
            ["git", *args],
            cwd=str(repo_root),
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return ""
    return proc.stdout if proc.returncode == 0 else ""


def _git_log_lines(args: list[str], repo_root: str | Path, cap: int) -> list[str]:
    """git log --all --oneline 包装：非空行取前 cap 条（空仓/无命中返回空表）。"""
    out = _run_git(["log", "--all", "--oneline", *args], repo_root)
    return [line for line in out.splitlines() if line.strip()][:cap]


def _state_source_index(query: str) -> tuple[list[str], bool]:
    """源① 馆索引：复用 lookup_assets 现有只读查询路径（lib_assets 账本，≤10 条）。

    全 query 先查；不足额再逐词补充（词表归一轴照常生效）。DB 故障=源级隔离：
    记错误行、has=False，绝不拖垮证据包其余两源。
    """
    q = query.strip()
    rows: list[dict[str, Any]] = []
    try:
        rows = lookup_assets(q, limit=_STATE_INDEX_ROW_CAP)
        if len(rows) < _STATE_INDEX_ROW_CAP:
            seen = {r.get("asset_id") for r in rows}
            for word in _state_words(q):
                if word == q:
                    continue
                for row in lookup_assets(word, limit=_STATE_INDEX_ROW_CAP):
                    if row.get("asset_id") in seen:
                        continue
                    seen.add(row.get("asset_id"))
                    rows.append(row)
                    if len(rows) >= _STATE_INDEX_ROW_CAP:
                        break
                if len(rows) >= _STATE_INDEX_ROW_CAP:
                    break
    except Exception as exc:  # noqa: BLE001 — 源级隔离（单源故障不阻断三源证据包）
        return [f"(index source error: {exc})"], False
    judged, _ = _annotate_on_disk(rows[:_STATE_INDEX_ROW_CAP], hide_missing=False)
    # has 语义本批不变：missing 行仍是"账本声称它有"的证据，剔除/改判据属方案③
    lines = [
        f"{r.get('asset_id', '?')}\t{r.get('home', '?')}\t{_state_truncate(str(r.get('title') or ''), 80)}"
        + (_MISSING_ON_DISK_MARKER if state == "missing" else "")
        for r, state in judged
    ]
    return lines, bool(lines)


def _state_source_gitlog(
    query: str, dir_hit_paths: list[str], other_hit_paths: list[str], repo_root: str | Path
) -> tuple[list[str], bool]:
    """源② git log 三通道（--all --oneline，近 90 天，总 ≤15 行，每行带通道标注）：

    - channel:paths   —— 源③命中文件的落库提交，两组分查：目录命中组（工棚战役目录，
      "做没做"最直接证据，配额 6）+ 内容命中组（挂账册等，配额 2）；
    - channel:pickaxe —— -S 内容增删证据：query 去空格全串优先，逐词补充（每词配额 2）；
    - channel:grep    —— -i --grep 提交消息：全串优先，逐词补充（配额 15）。

    逐词拆分是硬需求：实测 "GPU 摊销" 全串 grep 零命中（目标提交消息只含 "GPU"），
    且 90 天窗口内 GPU 命中 105 条、目标提交列第 23/44 位——目录命中组按目录分组的
    定向反查（如 gpu_rewrite/ 整目录 90 天仅 4 条落库提交）是让 c8da/cf16 类证据
    稳定浮现的正解。stash 派生提交（subject 前缀 "WIP on "/"index on "/"On "）非落库
    证据，过滤不显。
    """
    words = _state_words(query)
    nospace = "".join(words)
    ordered: list[tuple[str, list[str]]] = []
    if dir_hit_paths:
        # 按目录分组、目录序=源③排名序（dir_hit_paths 已按文件排名排好）逐目录子查询——
        # 全 pathspec 并集会让高频被 touch 的目录（如他会话战役目录 g_backtest_gpu/）
        # 的新提交反超目标提交；单目录子查（如 gpu_rewrite/ 90 天仅 4 条）则目标提交恒在顶部。
        from pathlib import PurePosixPath  # noqa: PLC0415 — 惰性 stdlib（保 import 计时面）

        dir_groups: dict[str, list[str]] = {}
        for path_text in dir_hit_paths:
            dir_key = str(PurePosixPath(path_text).parent)
            dir_groups.setdefault(dir_key, []).append(path_text)
        merged_dir_lines: list[str] = []
        seen_dir_hashes: set[str] = set()
        for dir_key in dir_groups:
            if len(merged_dir_lines) >= _STATE_GIT_PATHS_DIR_CAP:
                break
            for raw in _git_log_lines([_STATE_GIT_SINCE, "--", dir_key], repo_root, _STATE_GIT_PATHS_DIR_SUB_CAP):
                commit_hash, _, subject = raw.partition(" ")
                if subject.startswith(("WIP on ", "index on ", "On ")):  # stash 派生提交=非落库证据
                    continue
                if commit_hash in seen_dir_hashes:
                    continue
                seen_dir_hashes.add(commit_hash)
                merged_dir_lines.append(raw)
                if len(merged_dir_lines) >= _STATE_GIT_PATHS_DIR_CAP:
                    break
        if merged_dir_lines:
            ordered.append(("paths", merged_dir_lines))
    if other_hit_paths:
        ordered.append(
            (
                "paths",
                _git_log_lines(
                    [_STATE_GIT_SINCE, "--", *other_hit_paths[:_STATE_GIT_PATHSPEC_CAP]],
                    repo_root,
                    _STATE_GIT_PATHS_OTHER_CAP,
                ),
            )
        )
    pickaxe: list[str] = []
    if nospace:
        pickaxe.extend(_git_log_lines([_STATE_GIT_SINCE, f"-S{nospace}"], repo_root, _STATE_GIT_PICKAXE_CAP))
    for word in words:
        pickaxe.extend(_git_log_lines([_STATE_GIT_SINCE, f"-S{word}"], repo_root, _STATE_GIT_PICKAXE_WORD_CAP))
    if pickaxe:
        ordered.append(("pickaxe", pickaxe))
    grep: list[str] = []
    q = query.strip()
    if q:
        grep.extend(_git_log_lines(["-i", f"--grep={q}", _STATE_GIT_SINCE], repo_root, _STATE_GIT_GREP_CAP))
    for word in words:
        if len(grep) >= _STATE_GIT_GREP_CAP:
            break
        grep.extend(
            _git_log_lines(["-i", f"--grep={word}", _STATE_GIT_SINCE], repo_root, _STATE_GIT_GREP_CAP - len(grep))
        )
    if grep:
        ordered.append(("grep", grep))
    seen: set[str] = set()
    lines: list[str] = []
    for channel, raw_lines in ordered:
        for raw in raw_lines:
            commit_hash, _, subject = raw.partition(" ")
            if subject.startswith(("WIP on ", "index on ", "On ")):  # stash 派生提交=非落库证据
                continue
            if commit_hash in seen:
                continue
            seen.add(commit_hash)
            lines.append(f"{_state_truncate(raw, _STATE_GIT_LINE_WIDTH)}  [channel:{channel}]")
            if len(lines) >= _STATE_SOURCE_LINE_CAP:
                return lines, True
    return lines, bool(lines)


def _scan_file_words(path: Path, lowered_words: list[str]) -> tuple[set[int], list[tuple[int, str, int]], int]:
    """单文件内容扫描（大小写不敏感子串）。

    返回 (命中词索引集, [(行号, 行文本, 命中词数)], 全词同现行数)——全词同现
    （一行内齐含全部搜词）是最强短语级相关性信号，驱动源③排序与摘录位。
    二进制（首 8KB 含 NUL）/超限文件跳过内容；命中行只采集前 _STATE_SCAN_HITLINES_PER_FILE 条。
    """
    try:
        if path.stat().st_size > _STATE_SCAN_MAX_FILE_BYTES:
            return set(), [], 0
        data = path.read_bytes()
    except OSError:
        return set(), [], 0
    if b"\x00" in data[:8192]:
        return set(), [], 0
    text = data.decode("utf-8", errors="replace")
    hit_indexes: set[int] = set()
    hits: list[tuple[int, str, int]] = []
    cooccurrence = 0
    full_cover = len(lowered_words)
    for lineno, raw in enumerate(text.splitlines(), 1):
        lowered = raw.lower()
        matched = [i for i, w in enumerate(lowered_words) if w in lowered]
        if not matched:
            continue
        hit_indexes.update(matched)
        if len(matched) == full_cover:
            cooccurrence += 1
        if len(hits) < _STATE_SCAN_HITLINES_PER_FILE:
            hits.append((lineno, raw.strip(), len(matched)))
    return hit_indexes, hits, cooccurrence


def _state_source_workshop(
    query: str, workshop_root: str | Path, config_root: str | Path
) -> tuple[list[str], list[str], list[str], bool]:
    """源③ 工棚面+挂账面：docs/_working 目录名+文件名+内容子串扫描 + config/*.yaml 内容扫描。

    返回 (输出行, 目录命中相对路径组, 其余命中相对路径组, has_hits)。排序=(-全词同现行数,
    -目录名命中词数, -文件名命中词数, -命中词覆盖数, -内容命中行数, 路径)：全词同现
    （如挂账便签一行齐含 gpu+摊销）置顶；战役目录（目录名含搜词，如 gpu_rewrite/）
    下的文件优先列名。摘录策略=全词同现文件各取最佳 1 行、总额 3 行，其余以头部行列名
    （1 行/文件）直到 15 行预算耗尽——列名本身就是"文件命中"证据。两组命中路径回喂
    源② touched-paths 通道分查——场外区（fs_collector._SKIP_DIRS 跳过）的落地文件
    由此接回 git 证据链。
    """
    import os  # noqa: PLC0415 — 惰性 stdlib（保 import 计时面，R4 同法）
    from pathlib import Path as _Path  # noqa: PLC0415

    words = _state_words(query)
    if not words:
        return [], [], [], False
    lowered_words = [w.lower() for w in words]
    records: list[tuple[str, set[int], int, int, int, int, list[tuple[int, str, int]], bool]] = []
    scanned = 0
    truncated = False

    def _record(  # noqa: PLR0913 — 记录组装器，八参皆必要（排名轴+输出轴+分组轴）
        display: str,
        name_idx: set[int],
        dir_idx: set[int],
        content_idx: set[int],
        hits: list[tuple[int, str, int]],
        cooc: int,
        is_dir_hit: bool,
    ) -> None:
        word_union = name_idx | content_idx
        excerpts = sorted(hits, key=lambda h: (-h[2], h[0]))[:_STATE_EXCERPTS_PER_FILE]
        records.append((display, word_union, cooc, len(dir_idx), len(name_idx), len(hits), excerpts, is_dir_hit))

    def _display_for(path: Path, base: Path, fallback: Path) -> str:
        try:
            return path.relative_to(base).as_posix()
        except ValueError:
            return fallback.as_posix()

    if workshop_root and _Path(workshop_root).is_dir():
        workshop_root = _Path(workshop_root)
        # 展示/回喂 git 的基准=仓库根（<repo>/docs/_working 上溯两级）；注入异常树时退 rel
        display_base = workshop_root.parent.parent if workshop_root.parent != workshop_root else workshop_root
        for dirpath, dirnames, filenames in os.walk(workshop_root):
            dirnames[:] = [d for d in dirnames if d not in _STATE_SKIP_DIRS and not d.startswith(".")]
            for filename in filenames:
                if scanned >= _STATE_SCAN_MAX_FILES:
                    truncated = True
                    break
                path = _Path(dirpath) / filename
                scanned += 1
                rel = path.relative_to(workshop_root)
                rel_text = rel.as_posix().lower()
                name_hits = {i for i, w in enumerate(lowered_words) if w in rel_text}
                dir_parts = [p.lower() for p in rel.parts[:-1]]
                dir_hits = {i for i, w in enumerate(lowered_words) if any(w in part for part in dir_parts)}
                content_hits, hit_lines, cooc = _scan_file_words(path, lowered_words)
                if not name_hits and not content_hits:
                    continue
                _record(
                    _display_for(path, display_base, rel),
                    name_hits,
                    dir_hits,
                    content_hits,
                    hit_lines,
                    cooc,
                    bool(dir_hits),
                )
            if truncated:
                break
    if config_root and _Path(config_root).is_dir():
        config_root = _Path(config_root)
        display_base = config_root.parent if config_root.parent != config_root else config_root
        for pattern in ("*.yaml", "*.yml"):
            for path in sorted(config_root.glob(pattern)):
                if scanned >= _STATE_SCAN_MAX_FILES:
                    truncated = True
                    break
                scanned += 1
                content_idx, hit_lines, cooc = _scan_file_words(path, lowered_words)
                if not hit_lines:
                    continue
                _record(_display_for(path, display_base, path), set(), set(), content_idx, hit_lines, cooc, False)
            if truncated:
                break
    records.sort(key=lambda rec: (-rec[2], -rec[3], -rec[4], -len(rec[1]), -rec[5], rec[0]))
    lines: list[str] = []
    dir_hit_paths: list[str] = []
    other_hit_paths: list[str] = []
    excerpt_budget = _STATE_EXCERPT_BUDGET_TOTAL
    for rec in records:
        display, word_hits, cooc, _dir_n, _name_n, _hit_n, excerpts, is_dir_hit = rec
        if len(lines) >= _STATE_SOURCE_LINE_CAP:
            break
        (dir_hit_paths if is_dir_hit else other_hit_paths).append(display)
        lines.append(f"{display}  [words {len(word_hits)}/{len(lowered_words)}]")
        # 摘录策略：全词同现文件各取其最佳 1 行（如挂账便签的 measured 注释行），
        # 总额 3 行——其余 12 行预算让位给文件列名（列名本身即"文件命中"证据）。
        if cooc > 0 and excerpt_budget > 0 and excerpts:
            lineno, text, _ = excerpts[0]
            lines.append(f"  L{lineno}: {_state_truncate(text, _STATE_EXCERPT_WIDTH)}")
            excerpt_budget -= 1
    if truncated and len(lines) < _STATE_SOURCE_LINE_CAP:
        lines.append(f"(scan truncated at {_STATE_SCAN_MAX_FILES} files)")
    return (
        lines,
        dir_hit_paths[:_STATE_GIT_PATHSPEC_CAP],
        other_hit_paths[:_STATE_GIT_PATHSPEC_CAP],
        bool(lines),
    )


def lookup_state(
    query: str,
    *,
    repo_root: str | Path | None = None,
    workshop_root: str | Path | None = None,
    config_root: str | Path | None = None,
) -> int:
    """state 面：资产状态三源证据包（只读零副作用；馆查询走现有只读路径）。

    Args:
        query: 状态断言查询串（如 "GPU 摊销"）。
        repo_root: git 仓库根（默认 REPO_ROOT；测试注入临时仓）。
        workshop_root: 工棚根（默认 <repo>/docs/_working；测试注入 tmp_path 假树）。
        config_root: 挂账面根（默认 <repo>/config；测试注入 tmp_path）。

    Returns:
        退出码：任一源命中=0；三源全零=1（负存在断言依据）。

    输出契约：每源一节 ``== source-N: <名称> ==`` + ``state-snapshot at <ISO8601+08:00>`` 头，
    命中行原样；零命中打 ``-- no hits --``；结尾 ``sources-with-hits: N/3``。
    """
    from pathlib import Path as _Path  # noqa: PLC0415 — 惰性 stdlib（保 import 计时面，R4 同法）

    from zephyr.shared.io.paths import REPO_ROOT  # noqa: PLC0415 — 懒加载避免 import 期依赖

    q = (query or "").strip()
    if not q:
        print("(state: empty query)")
        return 1
    root = _Path(repo_root) if repo_root else _Path(REPO_ROOT)
    workshop = _Path(workshop_root) if workshop_root else root / _STATE_WORKSHOP_REL
    config = _Path(config_root) if config_root else root / _STATE_CONFIG_REL
    try:  # win32 管道态 stdout 默认 locale 编码，重配置 UTF-8 防中文/特殊字符炸 print
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        pass
    snapshot = _state_snapshot_line()
    workshop_lines, dir_hit_paths, other_hit_paths, workshop_has = _state_source_workshop(q, workshop, config)
    git_lines, git_has = _state_source_gitlog(q, dir_hit_paths, other_hit_paths, root)
    index_lines, index_has = _state_source_index(q)
    sections: list[tuple[str, list[str], bool]] = [
        ("source-1: 馆索引 (lib_assets)", index_lines, index_has),
        ("source-2: git log (--grep/-S/touched-paths, --all, 90d)", git_lines, git_has),
        ("source-3: 工棚+挂账面 (docs/_working + config)", workshop_lines, workshop_has),
    ]
    sources_with_hits = 0
    for name, lines, has_hits in sections:
        print(f"== {name} ==")
        print(snapshot)
        if has_hits and lines:
            sources_with_hits += 1
            for line in lines:
                print(line)
        else:
            print("-- no hits --")
    print(f"sources-with-hits: {sources_with_hits}/3")
    return 0 if sources_with_hits else 1


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：打印查询结果表。

    Args:
        argv: 命令行参数（默认 sys.argv[1:]）。

    Returns:
        退出码：0=有结果，1=无结果或用法错误。

    ``--session`` 提供时写 lookup audit 留痕（裁定#460 ②，fail-open 不阻断查询；
    未提供时行为零变化）。

    """
    parser = argparse.ArgumentParser(prog="zephyr.library.lookup", description="图书馆总口查询（T5 两轴过滤器）")
    parser.add_argument(
        "query",
        nargs="?",
        default="",
        help="查询串（ID/home/标题模糊匹配；ruling: 前缀=裁定先例机检面；state <词> 前缀=资产状态三源断言）",
    )
    parser.add_argument("limit_pos", nargs="?", type=int, default=None, help="上限（位置式旧用法）")
    parser.add_argument("--limit", type=int, default=20, help="上限（默认 20，最大 10000）")
    parser.add_argument("--kind", default=None, help="kind 精确过滤（12 枚举，如 table/module/file）")
    parser.add_argument("--owner-domain", default=None, help="owner_domain 精确过滤（83 域，如 D_DATA）")
    parser.add_argument("--tags", default=None, help="tags 过滤（逗号分隔多值 AND，如 ch,行情）")
    parser.add_argument("--status", default=None, help="status 精确过滤（active/stale/...）")
    parser.add_argument("--home-prefix", default=None, help="home 前缀过滤（如 TBL:ch:）")
    parser.add_argument(
        "--hide-missing",
        action="store_true",
        help="读侧视图：剔除 home 盘上不存在的行（默认只标注 [missing-on-disk]，不改账本 status）",
    )
    parser.add_argument("--backtest", action="store_true", help="回测产物查询面（按策略/日期段列产物+日志抽屉提示）")
    parser.add_argument("--no-alias", action="store_true", help="关闭 G15-① 别名轴展开（原词直查）")
    parser.add_argument("--feeds", default=None, help="供数反查（裁定#410）：potential_consumers 含关键词的资产")
    parser.add_argument("--strategy", default=None, help="[backtest] 策略 ID 过滤")
    parser.add_argument("--since", default=None, help="[backtest] 起始日期 YYYY-MM-DD（含）")
    parser.add_argument("--until", default=None, help="[backtest] 截止日期 YYYY-MM-DD（含）")
    parser.add_argument(
        "--session",
        default=None,
        help="session 标识（裁定#460 ②：提供则写 lookup audit 留痕，fail-open；缺省行为零变化）",
    )
    raw_argv = sys.argv[1:] if argv is None else list(argv)
    state_face = bool(raw_argv) and raw_argv[0] == "state"
    if state_face:
        raw_argv = raw_argv[1:]  # state 子命令与其余查询面互斥（F1）：占位词不进主 query 位置
    args = parser.parse_args(raw_argv)

    session_id = (args.session or "").strip()
    if state_face:
        rc = lookup_state(args.query)
        result_count = 1 if rc == 0 else 0
        payload: dict[str, Any] = {"query": args.query, "face": "state"}
    elif args.backtest:
        rc = _query_backtest(args.strategy, args.since, args.until, max(1, min(args.limit, 10000)))
        result_count = 1 if rc == 0 else 0
        payload: dict[str, Any] = {"query": args.strategy, "face": "backtest"}
    elif args.feeds:
        rc = _run_feeds_query(args.feeds, max(1, min(args.limit, 10000)))
        result_count = 1 if rc == 0 else 0
        payload = {"query": args.feeds, "face": "feeds"}
    elif args.query.startswith(_COMMIT_GUIDE_PREFIX):
        rc = _query_commit_guide(args.query[len(_COMMIT_GUIDE_PREFIX) :])
        result_count = 1 if rc == 0 else 0
        payload = {"query": args.query, "face": "commit_guide"}
    elif args.query.startswith(_RULING_PREFIX):
        from zephyr.library.ruling_precedent import query_face  # noqa: PLC0415 — 懒加载防环（MOD-LIB-007 面）

        rc = query_face(args.query[len(_RULING_PREFIX) :])
        result_count = 1 if rc == 0 else 0
        payload = {"query": args.query, "face": "ruling_precedent"}
    else:
        rc, rows = _run_main_query(args, parser)
        result_count = len(rows)
        payload = {"query": args.query, "face": "main"}
    if session_id:
        _write_cli_audit(session_id, payload, result_count)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
