# [BLUEPRINT] MOD-L00-006 | tests/zephyr/data/test_format_transformer.py
# [MODULE] tests.zephyr.data.test_format_transformer
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.normalizers.format_transformer
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L00-006 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FormatTransformer 单元测试——Schema驱动的格式转换器（CAND-DAT-010 / B1-00343 / D-INT-16）。

覆盖：
    1. 内置 ctr001_ohlcv schema 注册与未知 schema fail-closed
    2. 正常记录 → CTR-001 NormalizedMarketData（Decimal 字段/UTC 时区/幂等键）
    3. 字段校验：必填缺失/类型无法强转/负价格/负成交量 → 隔离不抛错
    4. 单位归一：scale 倍率（手→股）
    5. 时区归一：naive 时间按 source_tz 本地化 → UTC
    6. 批量混合：合格入 records，不合格入 quarantined 留痕
    7. 隔离报告：供质量门控消费的统计载荷
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from zephyr.data.normalizers.format_transformer import (
    SCHEMA_REGISTRY,
    FormatTransformer,
)
from zephyr.shared.contracts.market_data import NormalizedMarketData

# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

_GOOD_ROW = {
    "symbol": "sh600000",
    "timestamp": "2026-08-25 09:30:00",
    "open": "13.01",
    "high": "13.10",
    "low": "12.98",
    "close": "13.06",
    "volume": "12345",
}


def _make(schema: str = "ctr001_ohlcv") -> FormatTransformer:
    return FormatTransformer(schema)


# ---------------------------------------------------------------------------
# 1. Schema 注册
# ---------------------------------------------------------------------------


class TestSchemaRegistry:
    def test_builtin_schema_registered(self):
        assert "ctr001_ohlcv" in SCHEMA_REGISTRY

    def test_unknown_schema_fail_closed(self):
        with pytest.raises(ValueError, match="schema"):
            FormatTransformer("no_such_schema")


# ---------------------------------------------------------------------------
# 2. 正常转换
# ---------------------------------------------------------------------------


class TestTransformHappyPath:
    def test_records_are_ctr001_contract(self):
        result = _make().transform([_GOOD_ROW])
        assert len(result.records) == 1
        rec = result.records[0]
        assert isinstance(rec, NormalizedMarketData)
        assert isinstance(rec.close, Decimal)
        assert rec.close == Decimal("13.06")
        assert rec.volume == Decimal("12345")

    def test_symbol_normalized(self):
        result = _make().transform([_GOOD_ROW])
        assert result.records[0].symbol == "600000.SH"

    def test_naive_timestamp_localized_to_utc(self):
        result = _make().transform([_GOOD_ROW])
        ts = result.records[0].timestamp
        assert ts.tzinfo is not None
        # Asia/Shanghai 09:30 -> UTC 01:30
        assert ts == datetime(2026, 8, 25, 1, 30, tzinfo=timezone.utc)

    def test_idempotency_key_deterministic(self):
        r1 = _make().transform([_GOOD_ROW]).records[0]
        r2 = _make().transform([dict(_GOOD_ROW)]).records[0]
        assert r1.idempotency_key
        assert r1.idempotency_key == r2.idempotency_key

    def test_data_source_stamped(self):
        rec = _make().transform([_GOOD_ROW]).records[0]
        assert rec.data_source == SCHEMA_REGISTRY["ctr001_ohlcv"].data_source


# ---------------------------------------------------------------------------
# 3. 字段校验 → 隔离
# ---------------------------------------------------------------------------


class TestFieldValidation:
    def test_missing_required_field_quarantined(self):
        row = {k: v for k, v in _GOOD_ROW.items() if k != "close"}
        result = _make().transform([row])
        assert result.records == []
        assert len(result.quarantined) == 1
        assert any(i.field == "close" for i in result.quarantined[0].issues)

    def test_uncoercible_type_quarantined(self):
        row = dict(_GOOD_ROW, close="not_a_number")
        result = _make().transform([row])
        assert result.records == []
        assert len(result.quarantined) == 1

    def test_negative_price_quarantined(self):
        row = dict(_GOOD_ROW, open="-1.0")
        result = _make().transform([row])
        assert result.records == []
        assert any(i.field == "open" for i in result.quarantined[0].issues)

    def test_negative_volume_quarantined(self):
        row = dict(_GOOD_ROW, volume="-5")
        result = _make().transform([row])
        assert result.records == []

    def test_zero_volume_allowed(self):
        row = dict(_GOOD_ROW, volume="0")
        result = _make().transform([row])
        assert len(result.records) == 1

    def test_input_list_not_mutated(self):
        row = dict(_GOOD_ROW)
        snapshot = dict(row)
        _make().transform([row])
        assert row == snapshot


# ---------------------------------------------------------------------------
# 4. 单位/时区归一
# ---------------------------------------------------------------------------


class TestUnitTimezoneNormalization:
    def test_volume_scale_hand_to_share(self):
        row = dict(_GOOD_ROW, volume="12")  # 12 手
        result = FormatTransformer("ctr001_ohlcv_hand").transform([row])
        assert result.records[0].volume == Decimal("1200")

    def test_explicit_utc_timestamp_kept(self):
        row = dict(_GOOD_ROW, timestamp="2026-08-25T01:30:00+00:00")
        result = _make().transform([row])
        assert result.records[0].timestamp == datetime(2026, 8, 25, 1, 30, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# 5. 批量混合 + 隔离报告
# ---------------------------------------------------------------------------


class TestBatchAndQuarantineReport:
    def test_mixed_batch_split(self):
        bad = dict(_GOOD_ROW, close="")
        result = _make().transform([_GOOD_ROW, bad, dict(_GOOD_ROW)])
        assert len(result.records) == 2
        assert len(result.quarantined) == 1
        assert result.quarantined[0].index == 1

    def test_quarantine_report_payload(self):
        bad = dict(_GOOD_ROW, high="x")
        result = _make().transform([_GOOD_ROW, bad])
        report = result.quarantine_report()
        assert report["schema"] == "ctr001_ohlcv"
        assert report["total"] == 2
        assert report["ok"] == 1
        assert report["failed"] == 1
        assert report["samples"]
