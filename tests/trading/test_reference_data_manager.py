# [BLUEPRINT] MOD-TRADING-014 | docs/03_modules/_domain_trading/reference_data_manager/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-TRADING-014 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.trading.test_reference_data_manager
# [TESTS] src/zephyr/trading/reference_data_manager.py
"""MOD-TRADING-014 单元测试：reference_data_manager 证券主数据管理器。

蓝图验收（B14-04639/CAND-TRD-013，A9 D-TRADING-14）：
主数据 SSOT（代码/名称/行业/涨跌停规则/ST 与退市标记/交易日历，注入
sqlite 内存连接）+ 日终刷新（全量快照替换）+ 版本号严格递增 + 查询 API
（监控与风控统一引用入口）+ 变更审计回调（异常吞没）+ 确定性排序。
时钟/审计全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime
import sqlite3
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.trading.reference_data_manager",
    reason="reference_data_manager not importable",
)

from zephyr.trading.reference_data_manager import (  # noqa: E402
    ReferenceDataError,
    ReferenceDataManager,
    SecurityRecord,
)

_T0 = datetime.datetime(2026, 8, 25, 17, 0, 0)
_D1 = datetime.date(2026, 8, 25)
_D2 = datetime.date(2026, 8, 26)
_D3 = datetime.date(2026, 8, 27)


def _record(
    code: str = "600000",
    name: str = "浦发银行",
    industry: str = "银行",
    up: str = "10.00",
    down: str = "10.00",
    st: bool = False,
    delisted: bool = False,
) -> SecurityRecord:
    return SecurityRecord(
        code=code,
        name=name,
        industry=industry,
        limit_up_pct=Decimal(up),
        limit_down_pct=Decimal(down),
        is_st=st,
        is_delisted=delisted,
    )


@pytest.fixture
def conn() -> sqlite3.Connection:
    c = sqlite3.connect(":memory:")
    yield c
    c.close()


def _manager(conn: sqlite3.Connection, audits: list | None = None, **kwargs) -> ReferenceDataManager:
    base = {"conn": conn, "clock": lambda: _T0}
    if audits is not None:
        base["audit_sink"] = lambda e: audits.append(e)
    base.update(kwargs)
    return ReferenceDataManager(**base)


# ──────────────────────────────────────────────────────────────────────────────
# 构造（sqlite 连接强制注入）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_init_version_zero(self, conn) -> None:
        mgr = _manager(conn)
        assert mgr.version() == 0
        assert mgr.all_codes() == ()

    def test_conn_missing_raises(self) -> None:
        with pytest.raises(ReferenceDataError):
            _manager(None)


# ──────────────────────────────────────────────────────────────────────────────
# 日终刷新（SSOT 快照替换 + 版本递增 + 差异）
# ──────────────────────────────────────────────────────────────────────────────


class TestEodRefresh:
    def test_first_refresh(self, conn) -> None:
        mgr = _manager(conn)
        change = mgr.eod_refresh(records=[_record()])
        assert change.from_version == 0
        assert change.to_version == 1
        assert change.added == ("600000",)
        assert change.removed == ()
        assert change.changed == ()
        assert change.refreshed_at == _T0
        assert mgr.version() == 1

    def test_version_increments_each_refresh(self, conn) -> None:
        mgr = _manager(conn)
        mgr.eod_refresh(records=[_record()])
        mgr.eod_refresh(records=[_record()])
        change = mgr.eod_refresh(records=[_record()])
        assert change.to_version == 3
        assert mgr.version() == 3

    def test_diff_added(self, conn) -> None:
        mgr = _manager(conn)
        mgr.eod_refresh(records=[_record()])
        change = mgr.eod_refresh(records=[_record(), _record(code="000001", name="平安银行")])
        assert change.added == ("000001",)
        assert change.removed == ()
        assert change.changed == ()

    def test_diff_removed(self, conn) -> None:
        mgr = _manager(conn)
        mgr.eod_refresh(records=[_record(), _record(code="000001", name="平安银行")])
        change = mgr.eod_refresh(records=[_record(code="000001", name="平安银行")])
        assert change.added == ()
        assert change.removed == ("600000",)
        assert not mgr.exists("600000")

    def test_diff_changed(self, conn) -> None:
        mgr = _manager(conn)
        mgr.eod_refresh(records=[_record()])
        change = mgr.eod_refresh(records=[_record(name="浦发银行股份", st=True, up="5.00", down="5.00")])
        assert change.added == ()
        assert change.removed == ()
        assert change.changed == ("600000",)
        rec = mgr.get("600000")
        assert rec.name == "浦发银行股份"
        assert rec.is_st is True
        assert rec.limit_up_pct == Decimal("5.00")

    def test_no_change_refresh_still_bumps_version(self, conn) -> None:
        mgr = _manager(conn)
        mgr.eod_refresh(records=[_record()])
        change = mgr.eod_refresh(records=[_record()])
        assert change.added == change.removed == change.changed == ()
        assert change.to_version == 2

    def test_decimal_roundtrip(self, conn) -> None:
        mgr = _manager(conn)
        mgr.eod_refresh(
            records=[
                _record(up="10.00", down="10.00"),
                _record(code="688981", name="中芯国际", industry="半导体", up="20.05", down="20.05"),
            ]
        )
        rec = mgr.get("688981")
        assert rec.limit_up_pct == Decimal("20.05")  # TEXT 保真存取
        assert mgr.get("600000").limit_down_pct == Decimal("10.00")


# ──────────────────────────────────────────────────────────────────────────────
# 刷新校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestRefreshValidation:
    def test_empty_snapshot_raises(self, conn) -> None:
        mgr = _manager(conn)
        with pytest.raises(ReferenceDataError):
            mgr.eod_refresh(records=[])
        assert mgr.version() == 0

    def test_duplicate_code_raises(self, conn) -> None:
        mgr = _manager(conn)
        with pytest.raises(ReferenceDataError):
            mgr.eod_refresh(records=[_record(), _record(name="重复代码")])

    def test_empty_fields_raise(self, conn) -> None:
        mgr = _manager(conn)
        with pytest.raises(ReferenceDataError):
            mgr.eod_refresh(records=[_record(code="")])
        with pytest.raises(ReferenceDataError):
            mgr.eod_refresh(records=[_record(name="")])
        with pytest.raises(ReferenceDataError):
            mgr.eod_refresh(records=[_record(industry="")])

    def test_negative_limit_raises(self, conn) -> None:
        mgr = _manager(conn)
        with pytest.raises(ReferenceDataError):
            mgr.eod_refresh(records=[_record(down="-10.00")])
        with pytest.raises(ReferenceDataError):
            mgr.eod_refresh(records=[_record(up="-0.01")])
        # 零涨跌停幅度（无涨跌幅限制场景）合法
        mgr.eod_refresh(records=[_record(up="0", down="0")])
        assert mgr.get("600000").limit_up_pct == Decimal("0")

    def test_invalid_batch_atomic(self, conn) -> None:
        mgr = _manager(conn)
        mgr.eod_refresh(records=[_record()])
        with pytest.raises(ReferenceDataError):
            mgr.eod_refresh(records=[_record(code="000001", name="平安银行"), _record(code="")])
        # 校验先于写入：版本与既有数据不受影响
        assert mgr.version() == 1
        assert mgr.all_codes() == ("600000",)


# ──────────────────────────────────────────────────────────────────────────────
# 查询 API（监控与风控统一引用入口）
# ──────────────────────────────────────────────────────────────────────────────


class TestQueryApi:
    def test_get_unknown_or_empty_raises(self, conn) -> None:
        mgr = _manager(conn)
        mgr.eod_refresh(records=[_record()])
        with pytest.raises(ReferenceDataError):
            mgr.get("999999")
        with pytest.raises(ReferenceDataError):
            mgr.get("")
        with pytest.raises(ReferenceDataError):
            mgr.exists("")

    def test_exists(self, conn) -> None:
        mgr = _manager(conn)
        assert mgr.exists("600000") is False
        mgr.eod_refresh(records=[_record()])
        assert mgr.exists("600000") is True

    def test_all_codes_sorted(self, conn) -> None:
        mgr = _manager(conn)
        mgr.eod_refresh(
            records=[
                _record(code="688981", name="中芯国际", industry="半导体"),
                _record(),
                _record(code="000001", name="平安银行"),
            ]
        )
        assert mgr.all_codes() == ("000001", "600000", "688981")  # 确定性排序

    def test_list_by_industry(self, conn) -> None:
        mgr = _manager(conn)
        mgr.eod_refresh(
            records=[
                _record(code="600519", name="贵州茅台", industry="白酒"),
                _record(code="000001", name="平安银行"),
                _record(code="601398", name="工商银行"),
            ]
        )
        banks = mgr.list_by_industry("银行")
        assert [r.code for r in banks] == ["000001", "601398"]  # 按代码排序
        assert mgr.list_by_industry("军工") == ()
        with pytest.raises(ReferenceDataError):
            mgr.list_by_industry("")


# ──────────────────────────────────────────────────────────────────────────────
# 交易日历
# ──────────────────────────────────────────────────────────────────────────────


class TestCalendar:
    def test_trading_days_roundtrip_sorted(self, conn) -> None:
        mgr = _manager(conn)
        mgr.eod_refresh(records=[_record()], trading_days=[_D2, _D1])  # 乱序输入
        assert mgr.trading_days() == (_D1, _D2)  # 确定性排序
        assert mgr.is_trading_day(_D1) is True
        assert mgr.is_trading_day(_D3) is False
        with pytest.raises(ReferenceDataError):
            mgr.is_trading_day(datetime.datetime(2026, 8, 25, 9, 30))  # datetime 非法

    def test_calendar_isolation_by_name(self, conn) -> None:
        mgr = _manager(conn)
        mgr.eod_refresh(records=[_record()], trading_days=[_D1], calendar_name="SSE_A")
        assert mgr.is_trading_day(_D1, calendar_name="SSE_A") is True
        assert mgr.is_trading_day(_D1, calendar_name="HKEX") is False
        assert mgr.trading_days(calendar_name="HKEX") == ()

    def test_calendar_kept_when_not_provided(self, conn) -> None:
        mgr = _manager(conn)
        mgr.eod_refresh(records=[_record()], trading_days=[_D1])
        mgr.eod_refresh(records=[_record(code="000001", name="平安银行")])  # 不带日历
        assert mgr.trading_days() == (_D1,)  # 日历保留

    def test_calendar_replaced_when_provided(self, conn) -> None:
        mgr = _manager(conn)
        mgr.eod_refresh(records=[_record()], trading_days=[_D1])
        mgr.eod_refresh(records=[_record()], trading_days=[_D2, _D3])
        assert mgr.trading_days() == (_D2, _D3)  # 快照替换
        assert mgr.is_trading_day(_D1) is False

    def test_invalid_calendar_element_raises(self, conn) -> None:
        mgr = _manager(conn)
        with pytest.raises(ReferenceDataError):
            mgr.eod_refresh(records=[_record()], trading_days=["2026-08-25"])  # 非 date
        assert mgr.trading_days() == ()


# ──────────────────────────────────────────────────────────────────────────────
# 变更审计回调
# ──────────────────────────────────────────────────────────────────────────────


class TestAudit:
    def test_audit_event_content(self, conn) -> None:
        audits: list = []
        mgr = _manager(conn, audits=audits)
        mgr.eod_refresh(records=[_record()])
        assert len(audits) == 1
        event = audits[0]
        assert event.occurred_at == _T0
        assert event.change.to_version == 1
        assert event.change.added == ("600000",)

    def test_audit_exception_swallowed(self, conn) -> None:
        def bad_sink(event):
            raise RuntimeError("审计通道故障")

        mgr = _manager(conn, audit_sink=bad_sink)
        change = mgr.eod_refresh(records=[_record()])  # 审计异常不阻断刷新
        assert change.to_version == 1
        assert mgr.version() == 1
