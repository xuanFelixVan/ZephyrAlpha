# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_limit_up_pool_collector
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.implementations.limit_up_pool_collector
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] mock akshare 假数据源，不触网不触库；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=涨停池明细采集/解析逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-DAT-limit_up_pool_ingest_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""limit_up_pool 涨停池明细采集器 单元测试（GAP-F-13，假数据源不触真 akshare/CH）。

覆盖：stock_zt_pool_em 源字段全量映射（封板资金/首封/末封/炸板次数/连板/涨停统计/
行业）、封单比派生（seal_amount/float_market_cap）、封住秒数派生（末封→15:00）、
时间字段规整（int/str/脏值）、非法代码跳过、源失败容错（异常→空列表）、
collect 落库参数化（假 ch_client 捕获）、表名未注册 fail-closed。
"""

from __future__ import annotations

import datetime
import sys
from unittest.mock import MagicMock

import pytest

from src.zephyr.data.implementations.limit_up_pool_collector import (
    INSERT_COLUMNS,
    LimitUpPoolEntry,
    collect_limit_up_pool,
    fetch_limit_up_pool,
    parse_zt_pool_rows,
)

D = datetime.date
TD = D(2026, 8, 21)


def _row(**over) -> dict:
    """合成 stock_zt_pool_em 单行（东财涨停股池全字段形态）。"""
    base = {
        "代码": "600000",
        "名称": "浦发银行",
        "涨跌幅": 10.0,
        "最新价": 11.0,
        "成交额": 5.0e8,
        "流通市值": 3.0e10,
        "总市值": 3.2e10,
        "换手率": 1.5,
        "封板资金": 1.5e9,
        "首次封板时间": 92500,
        "最后封板时间": 100000,
        "炸板次数": 2,
        "涨停统计": "3/2",
        "连板数": 2,
        "所属行业": "银行",
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


class TestParseZtPoolRows:
    def test_full_field_mapping_and_derivations(self):
        entries = parse_zt_pool_rows([_row()], TD)
        assert len(entries) == 1
        e = entries[0]
        assert e.trade_date == "2026-08-21"
        assert e.symbol == "600000"
        assert e.name == "浦发银行"
        assert e.close == pytest.approx(11.0)
        assert e.pct_change == pytest.approx(10.0)
        assert e.amount == pytest.approx(5.0e8)
        assert e.turnover_rate == pytest.approx(1.5)
        assert e.float_market_cap == pytest.approx(3.0e10)
        assert e.total_market_cap == pytest.approx(3.2e10)
        assert e.seal_amount == pytest.approx(1.5e9)
        # 封单比 = 封板资金/流通市值 = 1.5e9/3.0e10 = 0.05
        assert e.seal_ratio == pytest.approx(0.05)
        assert e.first_seal_time == "09:25:00"
        assert e.last_seal_time == "10:00:00"
        # 封住时间 = 10:00:00 → 15:00:00 = 18000 秒
        assert e.sealed_seconds == 18000
        assert e.open_board_count == 2
        assert e.consec_limit == 2
        assert e.limit_stat == "3/2"
        assert e.industry == "银行"
        assert e.data_source == "akshare"

    def test_time_normalization_variants(self):
        """首封/末封时间：int 92500 / str '143000' / 带冒号 '09:30:00' 均规整为 HH:MM:SS。"""
        entries = parse_zt_pool_rows(
            [
                _row(代码="600001", 首次封板时间="143000", 最后封板时间="143000"),
                _row(代码="600002", 首次封板时间="09:30:00", 最后封板时间="09:30:00"),
            ],
            TD,
        )
        assert entries[0].first_seal_time == "14:30:00"
        assert entries[0].sealed_seconds == 1800
        assert entries[1].first_seal_time == "09:30:00"
        assert entries[1].sealed_seconds == 19800

    def test_dirty_time_gives_none_derivations(self):
        """脏时间（非法/超界）→ 时间字段 None，sealed_seconds None，不炸。"""
        entries = parse_zt_pool_rows(
            [_row(首次封板时间="abc", 最后封板时间=999999)], TD
        )
        e = entries[0]
        assert e.first_seal_time is None
        assert e.last_seal_time is None
        assert e.sealed_seconds is None

    def test_seal_ratio_guard_zero_mcap(self):
        """流通市值 0/缺失 → 封单比 None（除零守卫），其余字段照出。"""
        entries = parse_zt_pool_rows([_row(流通市值=0.0)], TD)
        assert entries[0].seal_ratio is None
        entries2 = parse_zt_pool_rows([_row(流通市值=None, 封板资金=None)], TD)
        assert entries2[0].seal_ratio is None
        assert entries2[0].seal_amount is None

    def test_invalid_symbol_skipped(self):
        entries = parse_zt_pool_rows([_row(代码=""), _row(代码="ABC"), _row()], TD)
        assert [e.symbol for e in entries] == ["600000"]

    def test_str_trade_date_accepted(self):
        entries = parse_zt_pool_rows([_row()], "2026-08-21")
        assert entries[0].trade_date == "2026-08-21"


# ---------- 采集层（mock akshare 假数据源） ----------


class TestFetchLimitUpPool:
    def test_fetch_happy_path(self, monkeypatch):
        import pandas as pd

        _mock_ak(monkeypatch, stock_zt_pool_em=pd.DataFrame([_row(), _row(代码="600001")]))
        entries = fetch_limit_up_pool(TD)
        assert len(entries) == 2

    def test_fetch_source_failure_returns_empty(self, monkeypatch):
        """源接口异常 → 空列表不抛（对齐 _collect_limit_rows 容错口径）。"""
        _mock_ak(monkeypatch, stock_zt_pool_em=RuntimeError("网络故障"))
        assert fetch_limit_up_pool(TD) == []

    def test_fetch_empty_frame(self, monkeypatch):
        import pandas as pd

        _mock_ak(monkeypatch, stock_zt_pool_em=pd.DataFrame())
        assert fetch_limit_up_pool(TD) == []


class TestCollectLimitUpPool:
    def test_collect_insert_parametrized(self, monkeypatch):
        import pandas as pd

        _mock_ak(monkeypatch, stock_zt_pool_em=pd.DataFrame([_row()]))
        client = _FakeCH()
        n = collect_limit_up_pool(TD, ch_client=client, table="c1_market.limit_up_pool")
        assert n == 1
        sql, params = client.inserts[0]
        assert "INSERT INTO c1_market.limit_up_pool" in sql
        assert "trade_date" in sql
        assert len(params) == 1
        assert len(params[0]) == len(INSERT_COLUMNS)

    def test_collect_unregistered_table_fail_closed(self, monkeypatch):
        """table=None 且品类未在 business_data_categories.yaml 注册 → RuntimeError 明确待办。"""
        import pandas as pd

        _mock_ak(monkeypatch, stock_zt_pool_em=pd.DataFrame([_row()]))
        with pytest.raises(RuntimeError, match="market_limit_up_pool"):
            collect_limit_up_pool(TD, ch_client=_FakeCH(), table=None)

    def test_collect_no_rows_no_insert(self, monkeypatch):
        import pandas as pd

        _mock_ak(monkeypatch, stock_zt_pool_em=pd.DataFrame())
        client = _FakeCH()
        n = collect_limit_up_pool(TD, ch_client=client, table="c1_market.limit_up_pool")
        assert n == 0
        assert client.inserts == []


class TestEntryContract:
    def test_entry_json_serializable(self):
        import json
        from dataclasses import asdict

        e = parse_zt_pool_rows([_row()], TD)[0]
        json.dumps(asdict(e), ensure_ascii=False)
        assert isinstance(e, LimitUpPoolEntry)
