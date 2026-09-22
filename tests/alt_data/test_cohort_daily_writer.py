# [A_test] module_id: MOD-DATA-COHORT-WRITER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-DATA-COHORT-WRITER | docs/_working/daily_loop_campaign/wiring_proposals_cohort_and_t4.md §A
# [MODULE] tests.alt_data.test_cohort_daily_writer
# [DEPENDENCIES]
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme;零DB零时钟零真CH（fake client/builder 全内存注入，禁触生产表与生产路径）;fail-open 契约断言不得弱化（任何失败禁抛）
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/alt_data/test_cohort_daily_writer.py
# [TTL] permanent
"""cohort_daily_writer 写入器单测（Owner 批 2026-09-21 wiring_proposals §A）。

覆盖（全 fake IO / 零 DB / 零时钟，无任何文件输出——生产路径零接触）：
- 列对齐：行 dict 键序打乱仍严格按 schemas INSERT_COLUMNS 序出元组（列序即 insert 契约）
- Decimal(18,4) 归一：float str 中转四舍五入 4 位；Decimal 直通 quantize
- 缺列防御：缺键行拒写不炸整批；全缺列/空产出 -> committed=False 零写库
- 幂等口径：同日重跑=两次直接 INSERT 同数据（ReplacingMergeTree 同键覆盖），
  全程零 DELETE/零查重语句（schemas :9-11 禁先删禁 UPDATE）
- fail-open：CH 写入异常 -> log+committed=False 不抛；表名注册表缺注册降级 schemas 真源
"""

from __future__ import annotations

import datetime
import decimal

import pytest

import zephyr.alt_data.cohort_daily_ledger as cdl
import zephyr.alt_data.cohort_daily_writer as writer_mod
import zephyr.data.ch_writer as ch_writer_mod
from schemas.categories.cohort_daily_ledger import INSERT_COLUMNS, QUALIFIED_NAME

_COLS = [c.strip() for c in INSERT_COLUMNS.strip("()").split(",")]


class _FakeClient:
    """捕获 execute 调用的假 strict 客户端（可注入异常）。"""

    def __init__(self, boom: bool = False):
        self.calls: list[tuple[str, list[tuple]]] = []
        self._boom = boom

    def execute(self, sql, data=None):
        if self._boom:
            raise RuntimeError("CH TCP 不可达（fake）")
        self.calls.append((sql, list(data or [])))


def _install(monkeypatch, rows, boom: bool = False) -> _FakeClient:
    """注入假 builder 行数据 + 假 strict 客户端（writer 两者均延迟导入，属性补丁即生效）。"""
    client = _FakeClient(boom=boom)
    monkeypatch.setattr(cdl, "build_cohort_daily", lambda day, reader=None: rows)
    monkeypatch.setattr(ch_writer_mod, "get_client_strict", lambda: client)
    return client


def _fake_row(**overrides):
    base = {
        "trade_date": "2026-09-15",
        "cohort_id": "retail",
        "metric_id": "net_inflow_sum",
        "metric_value": decimal.Decimal("12.3456"),
        "state": "net_pos",
        "proxy_source": "c1_market.market_money_flow.small_net_inflow",
        "bias_note": "测试偏差注",
        "detail": '{"unit": "万元"}',
    }
    base.update(overrides)
    return base


def test_columns_aligned_tuple_order_and_table(monkeypatch):
    """行键序打乱仍按 INSERT_COLUMNS 序出元组；INSERT 语句含表全限定名+显式列子句。"""
    scrambled = {k: _fake_row()[k] for k in reversed(list(_fake_row().keys()))}
    rows = [_fake_row(metric_id="net_inflow_median"), scrambled]
    client = _install(monkeypatch, rows)

    out = writer_mod.write_cohort_daily("2026-09-15")

    assert out == {"rows": 2, "committed": True, "day": "2026-09-15", "error": None}
    assert len(client.calls) == 1
    sql, data = client.calls[0]
    assert _COLS and _TBL_OK(sql)
    for tup in data:
        assert len(tup) == len(_COLS)
        d = dict(zip(_COLS, tup, strict=True))
        # Date 列收口契约（2026-09-22 实跑修）：写入侧把 ISO str 转 date 对象——
        # clickhouse_driver 序列化 Date 列要求 date，str 直传 'str' has no 'year' 假失败。
        assert d["trade_date"] == datetime.date(2026, 9, 15) and d["cohort_id"] in ("retail",)
        assert isinstance(d["metric_value"], decimal.Decimal)  # zip 列表推导见上：strict=True 已收口


def _TBL_OK(sql: str) -> bool:
    return f"INSERT INTO {QUALIFIED_NAME} {INSERT_COLUMNS} VALUES" in sql


def test_float_metric_normalized_to_decimal(monkeypatch):
    """float 经 str 中转四舍五入 4 位转 Decimal；已有 Decimal quantize 对齐 18,4。"""
    rows = [
        _fake_row(metric_id="a", metric_value=0.12345678),
        _fake_row(metric_id="b", metric_value=decimal.Decimal("9.99999")),
    ]
    client = _install(monkeypatch, rows)
    writer_mod.write_cohort_daily("2026-09-15")
    data = client.calls[0][1]
    vals = {
        dict(zip(_COLS, t, strict=True))["metric_id"]: dict(zip(_COLS, t, strict=True))["metric_value"] for t in data
    }
    assert vals["a"] == decimal.Decimal("0.1235")
    assert vals["b"] == decimal.Decimal("10.0000")


def test_missing_key_row_skipped_not_fatal(monkeypatch):
    """缺键行拒写出声、不炸整批：合法行照常落库，拒写行计数不含在 rows。"""
    bad = _fake_row()
    del bad["state"]
    client = _install(monkeypatch, [bad, _fake_row(metric_id="ok_row")])

    out = writer_mod.write_cohort_daily("2026-09-15")

    assert out["committed"] is True and out["rows"] == 1
    assert len(client.calls[0][1]) == 1


def test_empty_build_output_writes_nothing(monkeypatch):
    """空产出防御：零行 -> committed=False 且零 INSERT（禁空批打表）。"""
    client = _install(monkeypatch, [])

    out = writer_mod.write_cohort_daily("2026-09-15")

    assert out == {"rows": 0, "committed": False, "day": "2026-09-15", "error": "no_writable_rows"}
    assert client.calls == []


def test_all_rows_missing_keys_writes_nothing(monkeypatch):
    """全行缺列：同空产出契约——零写库 fail-open。"""
    bad = _fake_row()
    del bad["detail"]
    client = _install(monkeypatch, [bad])

    out = writer_mod.write_cohort_daily("2026-09-15")

    assert out["committed"] is False and out["error"] == "no_writable_rows"
    assert client.calls == []


def test_client_failure_fail_open(monkeypatch):
    """CH 写入异常：出声 log + committed=False + error 带异常类型，绝不抛（调用方=调度任务）。"""
    client = _install(monkeypatch, [_fake_row()], boom=True)

    out = writer_mod.write_cohort_daily("2026-09-15")  # 不抛即契约

    assert out["committed"] is False and out["rows"] == 1
    assert out["error"] is not None and "RuntimeError" in out["error"]


def test_idempotent_rerun_reinserts_without_dedup(monkeypatch):
    """幂等=ReplacingMergeTree 同键覆盖：同日重跑两次直接重插，零 DELETE/查重语句。"""
    rows = [_fake_row()]
    client = _install(monkeypatch, rows)

    first = writer_mod.write_cohort_daily("2026-09-15")
    second = writer_mod.write_cohort_daily("2026-09-15")

    assert first["committed"] and second["committed"]
    assert len(client.calls) == 2
    assert client.calls[0] == client.calls[1]  # 同数据重插，覆盖交给合并引擎
    for sql, _ in client.calls:
        assert "DELETE" not in sql.upper() and "SELECT" not in sql.upper()


def test_table_fallback_to_schema_truth_when_unregistered(monkeypatch):
    """品类缺注册：降级 schemas DDL 真源 QUALIFIED_NAME（禁硬编码字面量，双真源派生）。"""

    class _NoReg:
        def table(self, category_id):
            raise KeyError(f"category_id '{category_id}' 未注册")

    monkeypatch.setattr(writer_mod, "get_registry", lambda: _NoReg())
    client = _install(monkeypatch, [_fake_row()])

    out = writer_mod.write_cohort_daily("2026-09-15")

    assert out["committed"] is True
    assert _TBL_OK(client.calls[0][0])


def test_invalid_day_fails_fast(monkeypatch):
    """非法日期串：输入契约 fail-fast 抛 ValueError（builder 同口径校验，兼防注入）。"""
    _install(monkeypatch, [_fake_row()])
    with pytest.raises(ValueError):
        writer_mod.write_cohort_daily("2026-9-15")
