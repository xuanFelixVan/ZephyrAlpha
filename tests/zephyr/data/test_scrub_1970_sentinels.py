"""scrub_1970_date_sentinels 写入守卫单测（st-data-fix-20260921 ②b 治本）。

覆盖：空串/'1970-01-01'/date/datetime 哨兵 → None；PIT 轴豁免；
非日期列不动；fixed 计数与幂等性。
"""

import datetime

from zephyr.data.ch_writer import scrub_1970_date_sentinels


def test_empty_and_string_sentinel_become_none():
    cols = ["symbol", "announce_date", "report_period"]
    rows = [("000001", "", "2026-06-30"), ("000002", "1970-01-01", "2026-06-30")]
    out, fixed = scrub_1970_date_sentinels(cols, rows, "t")
    assert fixed == 2
    assert out[0][1] is None and out[0][2] == "2026-06-30"
    assert out[1][1] is None


def test_date_and_datetime_sentinel_become_none():
    cols = ["symbol", "list_date", "unlock_date"]
    rows = [("IDX", datetime.date(1970, 1, 1), datetime.datetime(1970, 1, 1, 0, 0, 0))]
    out, fixed = scrub_1970_date_sentinels(cols, rows, "t")
    assert fixed == 2
    assert out[0][1] is None and out[0][2] is None


def test_pit_columns_exempt():
    cols = ["ts_code", "valid_from", "valid_to"]
    rows = [("000001", "1970-01-01", "1970-01-01")]
    out, fixed = scrub_1970_date_sentinels(cols, rows, "index_list")
    assert fixed == 0
    assert out[0][1] == "1970-01-01" and out[0][2] == "1970-01-01"


def test_non_date_columns_untouched():
    cols = ["symbol", "name", "remark"]
    rows = [("000001", "", "1970-01-01")]
    out, fixed = scrub_1970_date_sentinels(cols, rows, "t")
    assert fixed == 0
    assert out[0][1] == "" and out[0][2] == "1970-01-01"


def test_dividend_year_exact_name_covered():
    cols = ["symbol", "dividend_year"]
    rows = [("000001", "1970-01-01")]
    out, fixed = scrub_1970_date_sentinels(cols, rows, "dividend")
    assert fixed == 1 and out[0][1] is None


def test_real_dates_kept_and_idempotent():
    cols = ["symbol", "announce_date"]
    rows = [("000001", "2026-09-21"), ("000001", datetime.date(2026, 9, 21))]
    once, fixed = scrub_1970_date_sentinels(cols, rows, "t")
    assert fixed == 0
    twice, fixed2 = scrub_1970_date_sentinels(cols, once, "t")
    assert fixed2 == 0 and twice == once
