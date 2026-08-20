# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_northbound_hold_fetcher
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] 本文件即测试（pytest -q tests/zephyr/data/test_northbound_hold_fetcher.py）
# [TTL] permanent
"""northbound_hold_fetcher 单元测试（memo 19，task-19-northbound-snapshot）。

覆盖：PIT 季度枚举（genesis 边界/发布缓冲/未发布剔除/国庆长假最差情形）、
字段映射（vol→hold_share/ratio→hold_ratio/exchange/data_source）、
质量校验（hold_share<=0 或 ratio 越界跳过）、SH/SZ 拆分双调用（4200 行上限规避）、
已发布季度 0 行 fail-closed、单季度异常不阻断其余季度。
全部用 fake pro 客户端 + today 注入，无网络依赖。
"""

from __future__ import annotations

import datetime

import pandas as pd
import pytest

from zephyr.data.implementations.northbound_hold_fetcher import (
    COLUMNS,
    GENESIS_QUARTER_END,
    PIT_PUBLISH_LAG_DAYS,
    fetch_northbound_hold_snapshot,
    published_quarter_ends,
)
from zephyr.data.provider_base import FetchPayload

# 冻结"今日"：2026-07-20 → 2026Q2（06-30+20d=07-20 当天已发布）及更早季度可采
_TODAY = datetime.date(2026, 7, 20)


def _payload() -> FetchPayload:
    return FetchPayload(
        table="c1_market.northbound_hold_snapshot",
        symbols=None,
        start=datetime.date(2026, 7, 1),
        end=_TODAY,
        incremental=False,
        extra={"capability": "northbound_hold_snapshot"},
    )


def _call_with_policy(fn, policy, **kwargs):
    return fn(**kwargs)


class _FakePro:
    """按 (trade_date, exchange) 返回预设 DataFrame 的假 pro 客户端。"""

    def __init__(self, data: dict[tuple[str, str], pd.DataFrame]):
        self._data = data
        self.calls: list[tuple[str, str]] = []

    def hk_hold(self, trade_date: str, exchange: str):
        self.calls.append((trade_date, exchange))
        return self._data.get((trade_date, exchange), pd.DataFrame())


def _df(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


# ============== PIT 季度枚举 ==============


class TestPublishedQuarterEnds:
    def test_pit_guard_excludes_unpublished_quarter(self):
        # 2026-08-15：2026Q2（06-30）+20d=07-20 已发布；2026Q3（09-30）未发布
        ends = published_quarter_ends(datetime.date(2026, 8, 15))
        assert datetime.date(2026, 6, 30) in ends
        assert datetime.date(2026, 9, 30) not in ends
        assert ends[0] == GENESIS_QUARTER_END

    def test_genesis_boundary(self):
        before = GENESIS_QUARTER_END + datetime.timedelta(days=PIT_PUBLISH_LAG_DAYS - 1)
        assert published_quarter_ends(before) == []
        at = GENESIS_QUARTER_END + datetime.timedelta(days=PIT_PUBLISH_LAG_DAYS)
        assert published_quarter_ends(at) == [GENESIS_QUARTER_END]

    def test_full_backfill_sequence(self):
        # memo §5.3 回填序列：2024Q3/2024Q4/2025Q1~Q4/2026Q1/Q2
        ends = published_quarter_ends(datetime.date(2026, 8, 15))
        assert ends == [
            datetime.date(2024, 9, 30),
            datetime.date(2024, 12, 31),
            datetime.date(2025, 3, 31),
            datetime.date(2025, 6, 30),
            datetime.date(2025, 9, 30),
            datetime.date(2025, 12, 31),
            datetime.date(2026, 3, 31),
            datetime.date(2026, 6, 30),
        ]

    def test_q3_national_day_worst_case(self):
        # Q3 末（09-30）遇国庆长假：10-15（+15d）不应采，10-21（+21d）应采
        assert datetime.date(2025, 9, 30) not in published_quarter_ends(datetime.date(2025, 10, 15))
        assert datetime.date(2025, 9, 30) in published_quarter_ends(datetime.date(2025, 10, 21))


# ============== 拉取与字段映射 ==============


class TestFetchNorthboundHoldSnapshot:
    @staticmethod
    def _q2_data() -> dict[tuple[str, str], pd.DataFrame]:
        sh = _df(
            [
                {
                    "code": "600519",
                    "trade_date": "20260630",
                    "ts_code": "600519.SH",
                    "name": "贵州茅台",
                    "vol": 12345678.0,
                    "ratio": 5.23,
                    "exchange": "SH",
                },
            ]
        )
        sz = _df(
            [
                {
                    "code": "300750",
                    "trade_date": "20260630",
                    "ts_code": "300750.SZ",
                    "name": "宁德时代",
                    "vol": 9876543.0,
                    "ratio": 3.21,
                    "exchange": "SZ",
                },
            ]
        )
        return {("20260630", "SH"): sh, ("20260630", "SZ"): sz}

    def test_field_mapping_and_exchange_split(self):
        # 仅 2026Q2 供数；更早季度 fake 返回空 → error 结果（不影响本断言）
        pro = _FakePro(self._q2_data())
        results = list(
            fetch_northbound_hold_snapshot(
                pro,
                _payload(),
                None,
                _call_with_policy,
                today=_TODAY,
            )
        )

        ok = [r for r in results if r.error is None]
        assert len(ok) == 1
        res = ok[0]
        assert res.table == "c1_market.northbound_hold_snapshot"
        assert res.columns == COLUMNS
        assert res.last_key == "2026-06-30"
        assert res.rows == [
            (datetime.date(2026, 6, 30), "600519.SH", "贵州茅台", 12345678, pytest.approx(5.23), "SH", "tushare"),
            (datetime.date(2026, 6, 30), "300750.SZ", "宁德时代", 9876543, pytest.approx(3.21), "SZ", "tushare"),
        ]
        # SH/SZ 拆分双调用（每季度 2 次，规避 4200 行上限）；HK 南向永不调用
        assert ("20260630", "SH") in pro.calls and ("20260630", "SZ") in pro.calls
        assert all(ex != "HK" for _, ex in pro.calls)

    def test_quality_filter_skips_invalid_rows(self):
        dirty = _df(
            [
                {
                    "code": "000001",
                    "trade_date": "20260630",
                    "ts_code": "000001.SZ",
                    "name": "平安银行",
                    "vol": 0.0,
                    "ratio": 0.0,
                    "exchange": "SZ",
                },  # hold_share=0 剔
                {
                    "code": "000002",
                    "trade_date": "20260630",
                    "ts_code": "000002.SZ",
                    "name": "万科A",
                    "vol": 100.0,
                    "ratio": 101.5,
                    "exchange": "SZ",
                },  # ratio>100 剔
                {
                    "code": "000003",
                    "trade_date": "20260630",
                    "ts_code": "000003.SZ",
                    "name": "正常股",
                    "vol": 100.0,
                    "ratio": 1.5,
                    "exchange": "SZ",
                },  # 合法
            ]
        )
        pro = _FakePro({("20260630", "SZ"): dirty})
        results = list(
            fetch_northbound_hold_snapshot(
                pro,
                _payload(),
                None,
                _call_with_policy,
                today=_TODAY,
            )
        )
        ok = [r for r in results if r.error is None]
        assert len(ok) == 1
        assert len(ok[0].rows) == 1
        assert ok[0].rows[0][1] == "000003.SZ"

    def test_published_quarter_zero_rows_fail_closed(self):
        pro = _FakePro({})  # 全部已发布季度 0 行 = 上游异常
        results = list(
            fetch_northbound_hold_snapshot(
                pro,
                _payload(),
                None,
                _call_with_policy,
                today=_TODAY,
            )
        )
        assert results
        assert all(r.error is not None and "0 行" in r.error for r in results)

    def test_quarter_exception_does_not_block_others(self):
        class _BoomPro(_FakePro):
            def hk_hold(self, trade_date: str, exchange: str):
                if trade_date == "20260331":
                    raise ConnectionError("boom")
                return super().hk_hold(trade_date, exchange)

        pro = _BoomPro(self._q2_data())
        results = list(
            fetch_northbound_hold_snapshot(
                pro,
                _payload(),
                None,
                _call_with_policy,
                today=_TODAY,
            )
        )
        err_q1 = [r for r in results if r.last_key == "2026-03-31"]
        assert err_q1 and "boom" in (err_q1[0].error or "")
        ok = [r for r in results if r.error is None]
        assert len(ok) == 1 and ok[0].last_key == "2026-06-30"

    def test_no_published_quarter_yields_error(self):
        results = list(
            fetch_northbound_hold_snapshot(
                _FakePro({}),
                _payload(),
                None,
                _call_with_policy,
                today=GENESIS_QUARTER_END,  # genesis 当天，无已发布季度
            )
        )
        assert len(results) == 1
        assert results[0].error is not None and "无已发布季度" in results[0].error


# ============== 上游撞码判别（2026-08-15 联调实证 + probe6-9 深挖）==============


class TestCodeCollisionDrop:
    def test_conflict_groups_dropped_benign_dups_kept(self):
        # 撞码组内 0 行 code 自洽（判别规则失效）→ 整组剔除兜底；完全重复行保留首行
        sz = _df(
            [
                {
                    "code": "31000",
                    "trade_date": "20260630",
                    "ts_code": "300750.SZ",
                    "name": "某ETF",
                    "vol": 999.0,
                    "ratio": 0.5,
                    "exchange": "SZ",
                },  # 撞码假行（31000+223000≠300750）
                {
                    "code": "93000",
                    "trade_date": "20260630",
                    "ts_code": "300750.SZ",
                    "name": "宁德时代",
                    "vol": 123.0,
                    "ratio": 0.3,
                    "exchange": "SZ",
                },  # 亦不自洽（93000+223000≠300750）
                {
                    "code": "000001",
                    "trade_date": "20260630",
                    "ts_code": "000001.SZ",
                    "name": "平安银行",
                    "vol": 100.0,
                    "ratio": 1.0,
                    "exchange": "SZ",
                },
                {
                    "code": "000001",
                    "trade_date": "20260630",
                    "ts_code": "000001.SZ",
                    "name": "平安银行",
                    "vol": 100.0,
                    "ratio": 1.0,
                    "exchange": "SZ",
                },  # 完全重复，保留首行
            ]
        )
        pro = _FakePro({("20260630", "SZ"): sz})
        results = list(
            fetch_northbound_hold_snapshot(
                pro,
                _payload(),
                None,
                _call_with_policy,
                today=_TODAY,
            )
        )
        ok = [r for r in results if r.error is None]
        assert len(ok) == 1
        codes = [row[1] for row in ok[0].rows]
        # 撞码组 300750.SZ 判别失效整组剔除（宁缺毋错）；000001.SZ 去重后仅存 1 行
        assert "300750.SZ" not in codes
        assert codes == ["000001.SZ"]

    def test_conflict_group_salvaged_by_code_consistency(self):
        # 组内恰好 1 行 code 自洽 → 保留真主行剔除入侵行（2026Q2 实证 243 组全救回）
        # SH: 093000+510000=603000 自洽（真主，繁体真名）；031000+510000=541000 不自洽（50ETF 入侵）
        sh = _df(
            [
                {
                    "code": "031000",
                    "trade_date": "20260630",
                    "ts_code": "603000.SH",
                    "name": "50ETF",
                    "vol": 16315908.0,
                    "ratio": 0.9,
                    "exchange": "SH",
                },  # 入侵 ETF 假行
                {
                    "code": "093000",
                    "trade_date": "20260630",
                    "ts_code": "603000.SH",
                    "name": "人民網",
                    "vol": 7248271.0,
                    "ratio": 0.4,
                    "exchange": "SH",
                },  # 真主行（繁体名保持上游原值）
            ]
        )
        # SZ: 077132+223000=300132 自洽（真主）；079132+223000=302132≠300132 不自洽（中航成飞撞入）
        sz = _df(
            [
                {
                    "code": "079132",
                    "trade_date": "20260630",
                    "ts_code": "300132.SZ",
                    "name": "中航成飛",
                    "vol": 500.0,
                    "ratio": 0.1,
                    "exchange": "SZ",
                },  # 入侵他股假行
                {
                    "code": "077132",
                    "trade_date": "20260630",
                    "ts_code": "300132.SZ",
                    "name": "青松股份",
                    "vol": 800.0,
                    "ratio": 0.2,
                    "exchange": "SZ",
                },  # 真主行
            ]
        )
        pro = _FakePro({("20260630", "SH"): sh, ("20260630", "SZ"): sz})
        results = list(
            fetch_northbound_hold_snapshot(
                pro,
                _payload(),
                None,
                _call_with_policy,
                today=_TODAY,
            )
        )
        ok = [r for r in results if r.error is None]
        assert len(ok) == 1
        got = {row[1]: row for row in ok[0].rows}
        # 两组均救回：保留真主行（name/vol 为真主值），入侵行剔除
        assert set(got) == {"603000.SH", "300132.SZ"}
        assert got["603000.SH"][2] == "人民網" and got["603000.SH"][3] == 7248271
        assert got["300132.SZ"][2] == "青松股份" and got["300132.SZ"][3] == 800

    def test_conflict_group_multi_self_consistent_dropped(self):
        # 组内 >1 行 code 自洽（判别规则失效另一形态）→ 整组剔除兜底
        sh = _df(
            [
                {
                    "code": "093000",
                    "trade_date": "20260630",
                    "ts_code": "603000.SH",
                    "name": "人民網",
                    "vol": 100.0,
                    "ratio": 0.4,
                    "exchange": "SH",
                },  # 自洽
                {
                    "code": "93000",
                    "trade_date": "20260630",
                    "ts_code": "603000.SH",
                    "name": "人民网",
                    "vol": 200.0,
                    "ratio": 0.5,
                    "exchange": "SH",
                },  # 同码异写亦自洽（zfill 后相同）
                {
                    "code": "099001",
                    "trade_date": "20260630",
                    "ts_code": "609001.SH",
                    "name": "正常股票",
                    "vol": 300.0,
                    "ratio": 0.6,
                    "exchange": "SH",
                },
            ]
        )
        pro = _FakePro({("20260630", "SH"): sh})
        results = list(
            fetch_northbound_hold_snapshot(
                pro,
                _payload(),
                None,
                _call_with_policy,
                today=_TODAY,
            )
        )
        ok = [r for r in results if r.error is None]
        assert len(ok) == 1
        codes = [row[1] for row in ok[0].rows]
        assert "603000.SH" not in codes
        assert codes == ["609001.SH"]
