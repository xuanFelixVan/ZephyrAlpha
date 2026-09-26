# [MODULE] tests.frontend.test_chainmap_equity_graph
# [DOMAIN] D_FRONTEND
# [TTL] permanent
"""EC1 股权接线施工件单测：chainmap_equity_graph 六表查询模块（mock 连接层，零真实 PG）。

覆盖：实体解析三键/现行版本聚合双向口径与计数/穿透 pg_function→sql_fallback 降级链
（sqlstate 42883）/兜底 SQL 防环结构/深度护栏/路径重构防环/公司卡与簇徽章字段契约
（ACC-F-CHAINMAP-EQUITY-BADGE 逐键兼容）/独立降级。禁写生产路径——全部走内存 fake。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from zephyr.frontend.dashboard import chainmap_equity_graph as ceg  # noqa: E402


# ── mock 连接层：记录 SQL+params，按脚本队列吐行 ──────────────────────────────
class FakeCursor:
    def __init__(self, script: list):
        self._script = script  # list of (match_substr | None, rows | Exception)
        self.executed: list[tuple[str, tuple]] = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        self.executed.append((sql, params or ()))
        for entry in self._script:
            match, payload = entry[0], entry[1]
            if match is None or match in sql:
                self._script.remove(entry)
                if isinstance(payload, Exception):
                    payload.sqlstate = getattr(payload, "sqlstate", None)
                    raise payload
                self._rows = payload
                return
        self._rows = []

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return list(self._rows)


class FakeConn:
    def __init__(self, script: list):
        self._script = script
        self.cursors: list[FakeCursor] = []
        self.closed = False

    def cursor(self):
        c = FakeCursor(self._script)
        self.cursors.append(c)
        return c

    def close(self):
        self.closed = True


def _ent_row(eid="E-CO-1", etype="company", name="测试公司", symbol="600566"):
    return (eid, etype, name, name.lower(), symbol, None, False)


# ── 键归一与实体解析 ──────────────────────────────────────────────────────────
def test_normalize_company_key_strips_suffix():
    assert ceg.normalize_company_key("600566.SH") == "600566"
    assert ceg.normalize_company_key(" 000651.SZ ") == "000651"
    assert ceg.normalize_company_key("600566") == "600566"


def test_resolve_entity_symbol_variants_and_row_shape():
    # 底座 symbol 锚为带后缀形态（'600566.SH'）：裸码输入须生成后缀候选
    conn = FakeConn([(None, [_ent_row()])])
    with conn.cursor() as cur:
        ent = ceg.resolve_entity(cur, "600566")
    sql, params = conn.cursors[0].executed[0]
    assert "FROM node_entity" in sql and "symbol = ANY(%s)" in sql
    variants = params[0]
    assert "600566" in variants and "600566.SH" in variants
    assert params[2] == "600566"  # name_norm 按原始输入
    assert ent == {
        "entity_id": "E-CO-1",
        "entity_type": "company",
        "name": "测试公司",
        "name_norm": "测试公司".lower(),
        "symbol": "600566",
        "uscc": None,
        "low_confidence": False,
    }


def test_resolve_entity_miss_returns_none():
    conn = FakeConn([])
    with conn.cursor() as cur:
        assert ceg.resolve_entity(cur, "999999") is None


# ── 现行版本股权聚合 ──────────────────────────────────────────────────────────
def test_company_equity_summary_two_sides_and_counts():
    # 脚本序：解析实体 → from 侧明细(controls) → to 侧明细(controlled_by)
    conn = FakeConn(
        [
            (None, [_ent_row()]),
            (
                "e.from_entity = %s",
                [
                    (
                        "E-P-1",
                        "牛散甲",
                        "",
                        "person",
                        "12.345",
                        "shareholder",
                        1,
                        "",
                        1962,
                        "2026-06-30",
                        "2026-08-20",
                        "akshare_em_top10",
                    )
                ],
            ),
            (
                "e.to_entity = %s",
                [
                    (
                        "E-CO-2",
                        "子公司乙",
                        "000876",
                        "company",
                        None,
                        "invests_in",
                        None,
                        "医药",
                        None,
                        None,
                        None,
                        "akshare_em_top10",
                    )
                ],
            ),
        ]
    )
    out = ceg.company_equity_summary(conn, "600566")
    sql1, p1 = conn.cursors[1].executed[0]
    sql2, p2 = conn.cursors[1].executed[1]  # 双向明细共用同一明细游标
    assert "valid_to IS NULL" in sql1 and "e.from_entity = %s" in sql1
    assert "valid_to IS NULL" in sql2 and "e.to_entity = %s" in sql2
    assert p1 == ("E-CO-1",) and p2 == ("E-CO-1",)
    assert out["controls_count"] == 1 and out["controlled_by_count"] == 1
    # 人对手方：symbol='' 靠 name；stake 两位小数；person 富化 birth_year
    assert out["controls"][0]["symbol"] == "" and out["controls"][0]["name"] == "牛散甲"
    assert out["controls"][0]["stake_pct"] == 12.35
    assert out["controls"][0]["birth_year"] == 1962
    # 公司对手方：industry 富化；stake None 如实
    assert out["controlled_by"][0]["industry"] == "医药"
    assert out["controlled_by"][0]["stake_pct"] is None


def test_company_equity_summary_unresolved_zero_counts():
    conn = FakeConn([])
    out = ceg.company_equity_summary(conn, "999999")
    assert out["entity"] is None and out["controls_count"] == 0 and out["controlled_by_count"] == 0
    assert len(conn.cursors) == 1  # 未命中实体不查明细


# ── 穿透：函数优先/42883 兜底/其他错误上抛/深度护栏 ────────────────────────────
_PEN_ROW = (1, "E-P-1", "牛散甲", "person", "E-CO-1", "测试公司", "shareholder", "8.88", None)


def test_penetrate_upstream_pg_function_path():
    conn = FakeConn([(None, [_ent_row()]), (None, [_PEN_ROW])])
    out = ceg.penetrate_upstream(conn, "600566", max_depth=3)
    assert out["engine"] == "pg_function" and out["root"]["entity_id"] == "E-CO-1"
    sql, params = conn.cursors[1].executed[0]
    assert "equity_penetration(%s, %s, %s)" in sql
    assert params == ("E-CO-1", 3, None)
    assert out["rows"][0]["stake_pct"] == 8.88 and out["rows"][0]["depth"] == 1


def test_penetrate_upstream_fallback_on_undefined_function():
    err = Exception("function equity_penetration(text, int, date) does not exist")
    err.sqlstate = ceg.PENETRATION_FN_STATE
    conn = FakeConn([(None, [_ent_row()]), (None, err), (None, [_PEN_ROW])])
    out = ceg.penetrate_upstream(conn, "600566", max_depth=3, min_valid_from="2025-01-01")
    assert out["engine"] == "sql_fallback"
    sql, params = conn.cursors[2].executed[0]
    assert "WITH RECURSIVE" in sql and "NOT (h.from_entity = ANY(w.path))" in sql
    assert "valid_to IS NULL" in sql
    # 参数序：基例(root,min_vf,min_vf) + 递归(min_vf,min_vf,depth)
    assert params == ("E-CO-1", "2025-01-01", "2025-01-01", "2025-01-01", "2025-01-01", 3)


def test_penetrate_upstream_reraises_non_42883():
    err = Exception("relation does not exist")
    err.sqlstate = "42P01"
    conn = FakeConn([(None, [_ent_row()]), (None, err)])
    with pytest.raises(Exception, match="relation does not exist"):
        ceg.penetrate_upstream(conn, "600566")


def test_penetrate_upstream_depth_clamped():
    err = Exception("no fn")
    err.sqlstate = ceg.PENETRATION_FN_STATE
    conn = FakeConn([(None, [_ent_row()]), (None, err), (None, [])])
    ceg.penetrate_upstream(conn, "600566", max_depth=99)
    assert conn.cursors[2].executed[0][1][-1] == 8  # 上限护栏
    conn2 = FakeConn([(None, [_ent_row()]), (None, err), (None, [])])
    ceg.penetrate_upstream(conn2, "600566", max_depth=0)
    assert conn2.cursors[2].executed[0][1][-1] == 1  # 下限护栏


# ── 路径重构（报告/冒烟展示用） ────────────────────────────────────────────────
def test_penetration_paths_root_to_leaf_and_cycle_safe():
    rows = [
        {"to_entity": "A", "from_entity": "B"},
        {"to_entity": "B", "from_entity": "C"},
        {"to_entity": "B", "from_entity": "D"},
        # 环边：C 的"上游"又指回 A——visited 必须拦截
        {"to_entity": "C", "from_entity": "A"},
    ]
    paths = ceg.penetration_paths("A", rows)
    endpoints = sorted(p[-1]["from_entity"] for p in paths)
    assert endpoints == ["C", "D"]  # 两条根→叶链，环未成路
    assert all(p[0]["to_entity"] == "A" for p in paths)


# ── 公司卡 equity 段契约（ACC 逐键兼容） ──────────────────────────────────────
_SIDE_PERSON = ("12.3", "shareholder", None, "2026-08-20", "akshare_em_top10", "E-P-1", "牛散甲", "", "person")
_SIDE_LISTED = (None, "invests_in", "2026-06-30", None, "akshare_em_top10", "E-CO-2", "子公司乙", "000876", "company")


def test_equity_domain_for_company_contract_keys():
    conn = FakeConn([(None, [_ent_row()]), (None, [_SIDE_LISTED]), (None, [_SIDE_PERSON])])
    out = ceg.equity_domain_for_company(conn, "600566.SH")
    assert out["source"] == "entity_graph"
    assert out["n_holdings"] == 1 and out["n_held"] == 1
    for row in out["holdings_in"] + out["held_by"]:
        assert set(row) == {"symbol", "name", "ref", "stake_pct", "layer", "relation", "verification", "as_of"}
    listed = out["holdings_in"][0]
    assert listed["symbol"] == "000876" and listed["name"] == "子公司乙" and listed["stake_pct"] is None
    assert listed["relation"] == "invests_in" and listed["verification"] == "akshare_em_top10"
    assert listed["as_of"] == "2026-06-30" and listed["layer"] == 1
    person = out["held_by"][0]
    assert person["symbol"] == "" and person["name"] == "牛散甲"  # 非上市对手方靠 name 展示
    assert person["as_of"] == "2026-08-20"


def test_equity_domain_degrades_on_error_and_miss():
    conn = FakeConn([(None, [_ent_row()]), (None, Exception("pg down"))])
    out = ceg.equity_domain_for_company(conn, "600566")
    assert out == {"holdings_in": [], "held_by": [], "n_holdings": 0, "n_held": 0, "source": "entity_graph"}
    conn2 = FakeConn([])  # 实体未命中
    out2 = ceg.equity_domain_for_company(conn2, "999999")
    assert out2["n_holdings"] == 0 and out2["source"] == "entity_graph"


# ── 簇徽章聚合契约 ────────────────────────────────────────────────────────────
def test_cluster_equity_badge_rows_contract_and_limit():
    rows_raw = [
        ("N-C01", "out", "", "自然人丙", "5.0", "shareholder", "2026-08-20", "akshare_em_top10"),
        ("N-C02", "in", "000876", "子公司乙", None, "invests_in", None, "akshare_em_top10"),
    ]
    conn = FakeConn([(None, rows_raw)])
    rows = ceg.cluster_equity_badge_rows(conn, ["CH-A", "CH-B"], limit=800)
    sql, params = conn.cursors[0].executed[0]
    assert sql.count("UNION ALL") == 1 and "valid_to IS NULL" in sql
    assert params == (["CH-A", "CH-B"], ["CH-A", "CH-B"], 800)
    assert rows[0]["dir"] == "out" and rows[0]["symbol"] == "" and rows[0]["name"] == "自然人丙"
    assert rows[1]["symbol"] == "000876" and rows[1]["stake_pct"] is None
    for r in rows:
        assert set(r) == {"node_id", "dir", "symbol", "name", "ref", "stake_pct", "relation", "verification", "as_of"}


def test_cluster_equity_badge_rows_empty_chains_and_degrade():
    conn = FakeConn([])
    assert ceg.cluster_equity_badge_rows(conn, []) == []
    assert len(conn.cursors) == 0  # 空链清单零查询
    conn2 = FakeConn([(None, Exception("pg down"))])
    assert ceg.cluster_equity_badge_rows(conn2, ["CH-A"]) == []  # 独立降级（ACC item7）


# ── 连接入口：只读角色走 depgraph_schema 统一入口（monkeypatch 拦截，零真实连接） ──
def test_connect_uses_reader_role_entry(monkeypatch):
    called = {}
    import types

    fake_mod = types.ModuleType("zephyr.governance.depgraph_schema")
    fake_mod.get_depgraph_pg_connection = lambda **kw: called.update(kw) or "CONN"
    monkeypatch.setitem(sys.modules, "zephyr.governance.depgraph_schema", fake_mod)
    assert ceg.connect() == "CONN"
    assert called.get("read_only") in (True, None)  # 默认只读角色，零写副作用
