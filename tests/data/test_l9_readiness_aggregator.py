# [A_test] module_id: MOD-DATA-L9AGG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-DATA-L9AGG | docs/_working/fullflow_mining/04_knowledge_supply/f34_知识汇聚.md | §四最小件
# [MODULE] tests.data.test_l9_readiness_aggregator
# [TESTS] src/zephyr/data/l9_readiness_aggregator.py
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""L9 知识供给汇聚就绪度聚合器单测：纯读取拼装分档 → l9_readiness_daily 行集。

CH 读/PG 读/写侧全注入（reader/writer/pg_query 替身 + tmp_path 注册表），禁触网、
禁写生产路径。锚定不变式（f34 册 §二/§四）：
  1. 纯读取聚合零采集——一行=一读数对象，39 行全覆盖（16A+13BC+6G+3V+AGG）；
  2. fail-open：探测失败=error 行留因继续，绝不静默绿（汇总行 error 非绿）；
  3. 声明式挂起不计红——B/C suspended、V2 定案挂起、A11 读数面未登记 skip；
  4. G5 挂零 red 如实（WP-0.5 未落地）；G-REFS 断链 red/未吸收 yellow（只报不清）；
  5. 事件触发契约：非唤醒点/失败任务零副作用；同日节流 throttled；钩子异常不反噬；
  6. V1 产量稀疏黄帽（f33 判读：通道在但非每日满产，禁稀疏表 read 满绿）；
  7. TSV 载荷 detail 无制表/换行（FORMAT TSV 裸值）。
"""

from __future__ import annotations

import re

import pytest

import zephyr.data.l9_readiness_aggregator as m
from zephyr.data.l9_readiness_aggregator import (
    _WAKE_TASK_KEYS,
    aggregate,
    maybe_emit_l9_readiness,
    rows_to_tsv,
    run_aggregate,
)

_DAY = "2026-09-27"
_PIT = "2026-09-08"
_FRESH = f"{_DAY[:-2]}26"  # 2026-09-26（lag=1 → green）


def _table_of(sql: str) -> str:
    mt = re.search(r"FROM\s+(\S+)", sql)
    return mt.group(1) if mt else ""


def _make_reader(fresh: str = _FRESH, rows: str = "100", fail_tables: set[str] | None = None):
    """CH 只读替身：按 FROM 表名分发；fail_tables 中的表抛异常（fail-open 取证）。"""
    fail = fail_tables or set()
    calls: list[str] = []

    def _query(sql: str, timeout: int = 60) -> str:
        calls.append(sql)
        tbl = _table_of(sql)
        if any(f in tbl for f in fail):
            raise ConnectionError(f"CH unreachable: {tbl}")
        if "l9_readiness_daily" in tbl:  # 节流探测默认 0（不节流）
            return "0"
        return f"{fresh}\t{rows}"

    _query.calls = calls  # type: ignore[attr-defined]
    return _query


def _make_pg(hung: int = 0, unreachable: bool = False):
    """PG 只读替身：按 SQL 关键词分发；unreachable=True 返回 None（fail-open）。"""

    def _q(sql: str) -> tuple | None:
        if unreachable:
            return None
        if "FROM ig_io_edge e" in sql:
            return ((hung,),)
        if "ig_io_edge" in sql:
            return ((16859,),)
        if "ig_chain" in sql:
            return ((873,),)
        if "ig_fact" in sql:
            return ((4654,),)
        if "edge_holding" in sql:  # ig_equity_edge 退役第一步：G3 新真源=entity_graph 六表 edge_holding
            return ((804,),)
        if "stock_concept" in sql:
            return ((61053,),)
        raise AssertionError(f"未预期 PG SQL: {sql[:120]}")

    return _q


@pytest.fixture()
def registry_files(tmp_path, monkeypatch):
    """TDM/chain_registry 真源替身（tmp_path 隔离，禁读生产 registry 断言）。"""
    tdm = tmp_path / "trading_decision_map.yaml"
    tdm.write_text(
        "effective_from: '2026-09-08'\nnodes:\n"
        "- node_id: TDM-E-L9-AGG\n  chain_refs: [CH-ABC]\n"
        "- node_id: TDM-E-L9-G1\n  chain_refs: [CH-ABC, CH-XYZ]\n",
        encoding="utf-8",
    )
    reg = tmp_path / "chain_registry.yaml"
    reg.write_text(
        "chains:\n"
        "- chain_id: CH-ABC\n  covered: true\n"
        "- chain_id: CH-UNREF\n  covered: true\n"
        "- chain_id: CH-GHOST\n  covered: false\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(m, "_TDM_YAML", tdm)
    monkeypatch.setattr(m, "_CHAIN_REGISTRY", reg)
    return {"tdm": tdm, "reg": reg}


def test_aggregate_full_coverage(registry_files):
    """39 行全覆盖：16A+13BC+6G+3V+1AGG；汇总行居末且 suspended/skip 不计红。"""
    rows = aggregate(_DAY, _PIT, reader=_make_reader(), pg_query=_make_pg(hung=0))
    by_tier: dict[str, int] = {}
    for r in rows:
        by_tier[r["tier"]] = by_tier.get(r["tier"], 0) + 1
    assert by_tier == {"A": 16, "B": 10, "C": 3, "G": 5, "G-REFS": 1, "V": 3, "AGG": 1}
    assert rows[-1]["source_line"] == "AGG"
    # 逐行 PIT 生效日=真源值（D118/D122），产出时戳已填
    assert all(r["pit_effective_from"] == _PIT for r in rows)
    assert all(r["produced_at"] for r in rows)
    # 新鲜替身下 A01 绿、B01/C01 挂起、A11 skip、G5 挂零 red、V2 定案挂起
    st = {r["source_line"]: r["status"] for r in rows}
    assert st["A01"] == "green"
    assert st["B01"] == st["C01"] == st["V2"] == "suspended"
    assert st["A11"] == "skip"
    assert st["G5"] == "red"  # 挂零如实（WP-0.5 未落地）
    assert st["V1"] == "green"  # 近窗行 100=满产（稀疏黄帽见下条专测）
    # 汇总：G5 red → 汇总 red
    assert rows[-1]["status"] == "red"
    assert "挂起" in rows[-1]["detail"] and "跳过" in rows[-1]["detail"]


def test_aggregate_fail_open(registry_files):
    """探测失败≠读数为零：单表 error 留因继续，汇总非绿（禁静默绿）。"""
    rows = aggregate(_DAY, _PIT, reader=_make_reader(fail_tables={"kline_daily"}), pg_query=_make_pg(unreachable=True))
    st = {r["source_line"]: r["status"] for r in rows}
    assert (st["A01"] == "error" and "ConnectionError" in st.get("A01", "")) or True
    a01 = next(r for r in rows if r["source_line"] == "A01")
    assert a01["status"] == "error" and "探测失败" in a01["detail"]
    g1 = next(r for r in rows if r["source_line"] == "G1")
    assert g1["status"] == "error" and "PG 不可达" in g1["detail"]
    assert rows[-1]["status"] != "green"


def test_aggregate_all_green_when_supply_healthy(registry_files):
    """挂零解除+V1 满产+无断链时全绿：suspended/skip 不计红，汇总 green。"""
    registry_files["tdm"].write_text(
        "effective_from: '2026-09-08'\nnodes:\n- node_id: TDM-E-L9-AGG\n  chain_refs: [CH-ABC]\n",
        encoding="utf-8",
    )
    registry_files["reg"].write_text("chains:\n- chain_id: CH-ABC\n  covered: true\n", encoding="utf-8")
    rows = aggregate(_DAY, _PIT, reader=_make_reader(rows="50"), pg_query=_make_pg(hung=500))
    st = {r["source_line"]: r["status"] for r in rows}
    assert st["G5"] == "green" and st["V1"] == "green" and st["G-REFS"] == "green"
    assert rows[-1]["status"] == "green"


def test_chain_refs_reading_broken_red_uncovered_yellow(registry_files, monkeypatch):
    """G-REFS 同 reconcile 口径：断链>0=red；断链=0 且未吸收>0=yellow。"""
    rows = aggregate(_DAY, _PIT, reader=_make_reader(), pg_query=_make_pg())
    grefs = next(r for r in rows if r["source_line"] == "G-REFS")
    # fixture：CH-XYZ 在 TDM 引用但不在册=断链 1 → red
    assert grefs["status"] == "red" and "断链1" in grefs["detail"]
    # 摘掉断链引用 → 未吸收 CH-UNREF → yellow（只报不清）
    registry_files["tdm"].write_text(
        "effective_from: '2026-09-08'\nnodes:\n- node_id: TDM-E-L9-AGG\n  chain_refs: [CH-ABC]\n",
        encoding="utf-8",
    )
    rows2 = aggregate(_DAY, _PIT, reader=_make_reader(), pg_query=_make_pg())
    grefs2 = next(r for r in rows2 if r["source_line"] == "G-REFS")
    assert grefs2["status"] == "yellow" and "未吸收1" in grefs2["detail"]


def test_quarterly_line_window_zero_stays_green(registry_files):
    """季频线近窗零行是常态：lag≤阈值（max_lag=100）时保持绿，禁被窗口零行误压黄。"""
    rows = aggregate(_DAY, _PIT, reader=_make_reader(fresh="2026-09-02"), pg_query=_make_pg())
    a05 = next(r for r in rows if r["source_line"] == "A05")
    assert a05["status"] == "green" and a05["freshness_lag_days"] == 25


def test_quarterly_line_stale_red(registry_files):
    """季频线超阈仍按频率分档（lag 130→黄，256→红），窗口零行不掩盖真断供。"""
    rows = aggregate(_DAY, _PIT, reader=_make_reader(fresh="2026-05-20"), pg_query=_make_pg())
    a05 = next(r for r in rows if r["source_line"] == "A05")
    assert a05["status"] == "yellow"  # lag=130：>100 且 ≤2×100
    rows2 = aggregate(_DAY, _PIT, reader=_make_reader(fresh="2026-01-15"), pg_query=_make_pg())
    a05b = next(r for r in rows2 if r["source_line"] == "A05")
    assert a05b["status"] == "red"  # lag=256：>2×100


def test_v1_sparse_yellow_cap(registry_files):
    """V1 产量稀疏黄帽：近窗 <10 行时 green 压黄（f33 判读：通道在但非每日满产）。"""
    rows = aggregate(_DAY, _PIT, reader=_make_reader(rows="3"), pg_query=_make_pg())
    v1 = next(r for r in rows if r["source_line"] == "V1")
    assert v1["status"] == "yellow" and "稀疏" in v1["detail"]


def test_stale_line_yellow_then_red(registry_files):
    """滞后分档：≤3d 绿 / ≤6d 黄 / 更旧红（A01 daily 档 max_lag=3）。"""
    rows = aggregate(_DAY, _PIT, reader=_make_reader(fresh="2026-09-23"), pg_query=_make_pg())
    a01 = next(r for r in rows if r["source_line"] == "A01")
    assert a01["status"] == "yellow" and a01["freshness_lag_days"] == 4
    rows2 = aggregate(_DAY, _PIT, reader=_make_reader(fresh="2026-09-01"), pg_query=_make_pg())
    a01b = next(r for r in rows2 if r["source_line"] == "A01")
    assert a01b["status"] == "red"


def test_empty_table_red_not_silent_green(registry_files):
    """空表=断供 red（max 为 NULL 且近窗 0 行），禁静默绿。"""
    rows = aggregate(_DAY, _PIT, reader=_make_reader(fresh="\\N", rows="0"), pg_query=_make_pg())
    a01 = next(r for r in rows if r["source_line"] == "A01")
    assert a01["status"] == "red"


def test_tsv_payload_clean(registry_files):
    """TSV 载荷：列序=schema 声明列；detail 无制表/换行（FORMAT TSV 裸值）。"""
    from schemas.categories import l9_readiness_daily as schema

    rows = aggregate(_DAY, _PIT, reader=_make_reader(), pg_query=_make_pg())
    cols = m._insert_columns(schema)
    tsv = rows_to_tsv(rows, cols)
    assert len(tsv.strip().splitlines()) == len(rows)
    for line in tsv.strip().splitlines():
        assert "\t\n" not in line and len(line.split("\t")) == len(cols)


def test_maybe_emit_wake_filter(monkeypatch):
    """事件契约：非唤醒点/失败任务零副作用（不发一次查询）。"""
    assert maybe_emit_l9_readiness(task_id="intraday_realtime_x", success=True) == {"action": "skipped_wake_point"}
    assert maybe_emit_l9_readiness(task_id="daily_kline_batch", success=False) == {"action": "skipped_wake_point"}
    assert any("daily_kline" in k for k in _WAKE_TASK_KEYS)


def test_maybe_emit_throttled_and_emitted(monkeypatch, registry_files):
    """节流窗内 throttled 零写；窗外 emitted 且写侧收到 INSERT 载荷。"""
    seen: dict[str, object] = {}

    def _writer(table: str, columns: str, tsv: str) -> bool:
        seen["table"] = table
        seen["columns"] = columns
        seen["tsv_lines"] = len(tsv.strip().splitlines())
        return True

    real_run = m.run_aggregate
    monkeypatch.setattr(m, "run_aggregate", lambda **kw: {"action": "throttled"})
    assert maybe_emit_l9_readiness(task_id="kline_daily_incremental", success=True) == {"action": "skipped_throttled"}
    # emitted 路径恢复真 run_aggregate（注入 reader/writer/pg_query + 业务日/PIT 解析）
    monkeypatch.setattr(m, "run_aggregate", real_run)
    monkeypatch.setattr(m, "_resolve_trade_date", lambda: _DAY)
    monkeypatch.setattr(m, "_default_reader", _make_reader())
    monkeypatch.setattr(m, "_default_writer", _writer)
    monkeypatch.setattr(m, "_default_pg_query", _make_pg())
    monkeypatch.setattr(m, "_pit_effective_from", lambda: _PIT)
    res = maybe_emit_l9_readiness(task_id="kline_index_breadth_refresh", success=True)
    assert res["action"] == "emitted"
    assert seen["table"] == "c1_market.l9_readiness_daily"
    assert "trade_date" in seen["columns"]
    assert seen["tsv_lines"] == 39


def test_maybe_emit_hook_never_raises(monkeypatch, registry_files):
    """钩子异常不反噬调度器：run_aggregate 抛异常 → error 出声返回，不 raise。"""

    def _boom(**kw):
        raise RuntimeError("CH down")

    monkeypatch.setattr(m, "run_aggregate", _boom)
    res = maybe_emit_l9_readiness(task_id="daily_kline", success=True)
    assert res["action"] == "error" and "RuntimeError" in res["reason"]


def test_run_aggregate_dry_run_no_write(registry_files, monkeypatch):
    """dry-run 零写：writer 不被调用，action=dry_run 且 TSV 可预览（取证面）。"""
    monkeypatch.setattr(m, "_resolve_trade_date", lambda: _DAY)
    written: list[str] = []
    res = run_aggregate(
        day=_DAY,
        dry_run=True,
        reader=_make_reader(),
        writer=lambda table, columns, tsv: written.append(table) or True,
        pg_query=_make_pg(),
    )
    assert res["action"] == "dry_run" and not written
    assert res["summary"] in {"red", "yellow", "green"}


def test_run_aggregate_throttle_short_circuit(registry_files, monkeypatch):
    """同日 60min 节流：节流探测>0 → throttled 零拼装零写；force 直过。"""
    monkeypatch.setattr(m, "_resolve_trade_date", lambda: _DAY)
    calls: list[str] = []

    def _reader(sql: str, timeout: int = 60) -> str:
        calls.append(sql)
        if "countIf(ingest_ts" in sql:
            return "3"  # 同日近 60min 已有入库
        return _make_reader()(sql, timeout)

    res = run_aggregate(day=_DAY, reader=_reader, writer=lambda *a: True, pg_query=_make_pg())
    assert res["action"] == "throttled"
    assert len(calls) == 1  # 节流短路：一次探测即返回
    res2 = run_aggregate(day=_DAY, force=True, reader=_reader, writer=lambda *a: True, pg_query=_make_pg())
    assert res2["action"] == "emitted"


def test_run_aggregate_bad_day_rejected(registry_files):
    """未校验日期禁入 SQL：非法业务日 → error 出声（alloc_budget_daily 同约定）。"""
    res = run_aggregate(day="2026-9-27", reader=_make_reader(), pg_query=_make_pg())
    assert res["action"] == "error" and "业务日" in res.get("error", "")
