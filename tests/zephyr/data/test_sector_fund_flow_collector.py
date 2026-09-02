# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_sector_fund_flow_collector
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.implementations.sector_fund_flow_collector
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] mock akshare 假数据源，不触网不触库；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=板块资金流快照采集/解析逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-DAT-sector_fund_flow_ingest_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sector_fund_flow 板块资金流快照采集器 单元测试（D3/GAP-F-16，假数据源不触真 akshare/CH）。

覆盖：THS 即时帧全字段映射（行业指数/涨跌幅/流入/流出/净额/公司家数/领涨股）、
行业+概念双类型、非法行跳过（空名/数值全空）、注入 ts 透传、源失败容错（异常→空列表）、
collect 落库参数化（假 ch_client 捕获）、表名未注册 fail-closed、to_csv 中间层、
dataclass asdict JSON 可序列化。
"""

from __future__ import annotations

import datetime
import sys
from unittest.mock import MagicMock

import pytest

from src.zephyr.data.implementations.sector_fund_flow_collector import (
    INSERT_COLUMNS,
    SectorFundFlowEntry,
    collect_sector_fund_flow,
    fetch_sector_fund_flow,
    parse_ths_fund_flow_rows,
    to_csv,
)

D = datetime.date
DT = datetime.datetime
TS = DT(2026, 8, 24, 10, 30)


def _industry_row(**over) -> dict:
    """合成 THS stock_fund_flow_industry(即时) 单行。"""
    base = {
        "序号": 1,
        "行业": "贵金属",
        "行业指数": 6382.23,
        "行业-涨跌幅": 3.19,
        "流入资金": 220.06,
        "流出资金": 217.33,
        "净额": 2.73,
        "公司家数": 14,
        "领涨股": "湖南白银",
        "领涨股-涨跌幅": 9.98,
        "当前价": 11.46,
    }
    base.update(over)
    return base


def _concept_row(**over) -> dict:
    base = {
        "序号": 1,
        "行业": "转基因",
        "行业指数": 1722.14,
        "行业-涨跌幅": 1.23,
        "流入资金": 21.25,
        "流出资金": 19.93,
        "净额": 1.32,
        "公司家数": 21,
        "领涨股": "登海种业",
        "领涨股-涨跌幅": 10.04,
        "当前价": 10.19,
    }
    base.update(over)
    return base


def _mock_ak(monkeypatch, **attrs) -> MagicMock:
    """构造 akshare 模块 mock（不触网）。"""
    mock_ak = MagicMock()
    for name, val in attrs.items():
        child = getattr(mock_ak, name)
        child.__name__ = name
        if isinstance(val, Exception) or callable(val):
            child.side_effect = val
        else:
            child.return_value = val
    monkeypatch.setitem(sys.modules, "akshare", mock_ak)
    return mock_ak


class _FakeCH:
    """假 ch_client：捕获 insert 调用。"""

    def __init__(self):
        self.inserts: list[tuple] = []

    def execute(self, sql, params=None):
        self.inserts.append((sql, params))
        return []


# ---------- 解析层（纯函数） ----------


class TestParseThsFundFlowRows:
    def test_full_field_mapping(self):
        entries = parse_ths_fund_flow_rows([_industry_row()], "industry", TS)
        assert len(entries) == 1
        e = entries[0]
        assert e.trade_date == "2026-08-24"
        assert e.timestamp == "2026-08-24 10:30:00"
        assert e.sector_type == "industry"
        assert e.sector_name == "贵金属"
        assert e.sector_index == pytest.approx(6382.23)
        assert e.pct_change == pytest.approx(3.19)
        assert e.inflow_amount == pytest.approx(220.06)
        assert e.outflow_amount == pytest.approx(217.33)
        assert e.net_amount == pytest.approx(2.73)
        assert e.company_count == 14
        assert e.lead_stock == "湖南白银"
        assert e.lead_pct_change == pytest.approx(9.98)
        assert e.data_source == "ths"

    def test_concept_type(self):
        entries = parse_ths_fund_flow_rows([_concept_row()], "concept", TS)
        assert entries[0].sector_type == "concept"
        assert entries[0].sector_name == "转基因"

    def test_blank_name_skipped(self):
        entries = parse_ths_fund_flow_rows(
            [_industry_row(行业=""), _industry_row(行业="  "), _industry_row()], "industry", TS
        )
        assert [e.sector_name for e in entries] == ["贵金属"]

    def test_all_numeric_blank_skipped(self):
        """流入/流出/净额全空 → 无效行跳过。"""
        entries = parse_ths_fund_flow_rows([_industry_row(流入资金=None, 流出资金=None, 净额=None)], "industry", TS)
        assert entries == []

    def test_dirty_numeric_gives_none_not_crash(self):
        entries = parse_ths_fund_flow_rows([_industry_row(行业指数="--", **{"行业-涨跌幅": "abc"})], "industry", TS)
        e = entries[0]
        assert e.sector_index is None
        assert e.pct_change is None
        assert e.net_amount == pytest.approx(2.73)  # 净额正常保留

    def test_date_derivation_from_ts(self):
        entries = parse_ths_fund_flow_rows([_industry_row()], "industry", DT(2026, 8, 24, 14, 59))
        assert entries[0].trade_date == "2026-08-24"

    def test_bad_sector_type_fail_closed(self):
        with pytest.raises(ValueError, match="sector_type"):
            parse_ths_fund_flow_rows([_industry_row()], "bogus", TS)

    def test_ts_str_accepted(self):
        entries = parse_ths_fund_flow_rows([_industry_row()], "industry", "2026-08-24 10:30:00")
        assert entries[0].timestamp == "2026-08-24 10:30:00"


# ---------- 采集层（mock akshare 假数据源） ----------


class TestFetchSectorFundFlow:
    def test_fetch_happy_path_both_types(self, monkeypatch):
        import pandas as pd

        _mock_ak(
            monkeypatch,
            stock_fund_flow_industry=pd.DataFrame([_industry_row(), _industry_row(行业="煤炭开采加工")]),
            stock_fund_flow_concept=pd.DataFrame([_concept_row()]),
        )
        entries = fetch_sector_fund_flow(ts=TS)
        assert len(entries) == 3
        types = {e.sector_type for e in entries}
        assert types == {"industry", "concept"}

    def test_fetch_partial_failure_tolerated(self, monkeypatch):
        """单类型源失败 → 该类型空、另一类型照出（容错不抛）。"""
        import pandas as pd

        _mock_ak(
            monkeypatch,
            stock_fund_flow_industry=RuntimeError("网络故障"),
            stock_fund_flow_concept=pd.DataFrame([_concept_row()]),
        )
        entries = fetch_sector_fund_flow(ts=TS)
        assert len(entries) == 1
        assert entries[0].sector_type == "concept"

    def test_fetch_all_failure_returns_empty(self, monkeypatch):
        _mock_ak(
            monkeypatch,
            stock_fund_flow_industry=RuntimeError("x"),
            stock_fund_flow_concept=RuntimeError("y"),
        )
        assert fetch_sector_fund_flow(ts=TS) == []

    def test_fetch_empty_frames(self, monkeypatch):
        import pandas as pd

        _mock_ak(
            monkeypatch,
            stock_fund_flow_industry=pd.DataFrame(),
            stock_fund_flow_concept=pd.DataFrame(),
        )
        assert fetch_sector_fund_flow(ts=TS) == []


class TestCollectSectorFundFlow:
    def test_collect_insert_parametrized(self, monkeypatch):
        import pandas as pd

        _mock_ak(
            monkeypatch,
            stock_fund_flow_industry=pd.DataFrame([_industry_row()]),
            stock_fund_flow_concept=pd.DataFrame([_concept_row()]),
        )
        client = _FakeCH()
        n = collect_sector_fund_flow(ts=TS, ch_client=client, table="c1_market.sector_fund_flow")
        assert n == 2
        sql, params = client.inserts[0]
        assert "INSERT INTO c1_market.sector_fund_flow" in sql
        assert "net_amount" in sql
        assert len(params) == 2
        assert len(params[0]) == len(INSERT_COLUMNS)

    def test_collect_registry_resolves_table(self, monkeypatch):
        """table=None 时品类已在 business_data_categories.yaml 注册（2026-08-26 DDL 建表+品类登记完成）→ 经 registry 解析全限定表名。"""
        import pandas as pd

        _mock_ak(
            monkeypatch,
            stock_fund_flow_industry=pd.DataFrame([_industry_row()]),
            stock_fund_flow_concept=pd.DataFrame([_concept_row()]),
        )
        client = _FakeCH()
        n = collect_sector_fund_flow(ts=TS, ch_client=client, table=None)
        assert n == 2
        sql, _ = client.inserts[0]
        assert "c1_market.sector_fund_flow" in sql

    def test_collect_no_rows_no_insert(self, monkeypatch):
        import pandas as pd

        _mock_ak(
            monkeypatch,
            stock_fund_flow_industry=pd.DataFrame(),
            stock_fund_flow_concept=pd.DataFrame(),
        )
        client = _FakeCH()
        n = collect_sector_fund_flow(ts=TS, ch_client=client, table="c1_market.sector_fund_flow")
        assert n == 0
        assert client.inserts == []


class TestCsvSink:
    def test_to_csv_writes_header_and_rows(self, tmp_path):
        entries = parse_ths_fund_flow_rows([_industry_row(), _concept_row()], "industry", TS)
        out = to_csv(entries, tmp_path / "sff.csv")
        assert out.endswith("sff.csv")
        lines = (tmp_path / "sff.csv").read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 3  # header + 2 rows
        assert "sector_name" in lines[0]
        assert "贵金属" in lines[1]

    def test_to_csv_empty_entries_no_file(self, tmp_path):
        out = to_csv([], tmp_path / "sff_empty.csv")
        assert out == ""
        assert not (tmp_path / "sff_empty.csv").exists()

    def test_to_csv_append_mode(self, tmp_path):
        entries = parse_ths_fund_flow_rows([_industry_row()], "industry", TS)
        to_csv(entries, tmp_path / "sff.csv")
        to_csv(entries, tmp_path / "sff.csv", append=True)
        lines = (tmp_path / "sff.csv").read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 3  # header 不重复 + 2 数据行


class TestEntryContract:
    def test_entry_json_serializable(self):
        import json
        from dataclasses import asdict

        e = parse_ths_fund_flow_rows([_industry_row()], "industry", TS)[0]
        json.dumps(asdict(e), ensure_ascii=False)
        assert isinstance(e, SectorFundFlowEntry)
