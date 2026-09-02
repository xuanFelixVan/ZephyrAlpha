# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] tests.ex_core.adapters.test_qmt_file_bridge_quote
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.adapters.qmt_file_bridge_quote
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] draft
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L06-002-QMTFQ | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""QMT File Bridge Quote Provider 单元测试"""

from __future__ import annotations

import os
import tempfile
import time
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.ex_core.adapters.qmt_file_bridge_quote import (
    QmtFileBridgeQuoteError,
    QmtFileBridgeQuoteProvider,
    QuoteSnapshot,
)

_HEADER = (
    "symbol,lastPrice,open,high,low,lastClose,volume,amount,"
    "bid1,bid2,bid3,bid4,bid5,ask1,ask2,ask3,ask4,ask5,"
    "bidVol1,bidVol2,bidVol3,bidVol4,bidVol5,"
    "askVol1,askVol2,askVol3,askVol4,askVol5,timetag\n"
)


def _quote_line(symbol: str = "510300.SH", last: str = "4.123", timetag: str = "20260826103001000") -> str:
    return (
        f"{symbol},{last},4.100,4.150,4.090,4.080,12345678,50987654.32,"
        "4.122,4.121,4.120,4.119,4.118,"
        "4.123,4.124,4.125,4.126,4.127,"
        "100,200,300,400,500,"
        "110,210,310,410,510,"
        f"{timetag}\n"
    )


class TestQmtFileBridgeQuoteProvider:
    """QmtFileBridgeQuoteProvider 测试"""

    @pytest.fixture
    def temp_quote_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "quote.csv"

    @pytest.fixture
    def provider(self, temp_quote_file):
        config = QmtFileBridgeQuoteProvider.ENV_CONFIG["sim"].copy()
        config["quote_file"] = str(temp_quote_file)
        with patch.dict(QmtFileBridgeQuoteProvider.ENV_CONFIG, {"sim": config}):
            yield QmtFileBridgeQuoteProvider(env="sim", stale_seconds=10.0)

    def test_invalid_env(self):
        with pytest.raises(QmtFileBridgeQuoteError):
            QmtFileBridgeQuoteProvider(env="invalid")

    def test_connect_file_missing(self, provider):
        with pytest.raises(QmtFileBridgeQuoteError, match="行情文件不存在"):
            provider.connect()

    def test_connect_ok(self, provider, temp_quote_file):
        temp_quote_file.write_text(_HEADER, encoding="ascii")
        assert provider.connect() is True
        assert provider.provider_id == "qmt_file_quote_sim"

    def test_get_quote_latest_line(self, provider, temp_quote_file):
        """同一标的多行时取最新（最后一行）"""
        content = _HEADER
        content += _quote_line(last="4.100", timetag="20260826103000000")
        content += _quote_line(last="4.123", timetag="20260826103001000")
        temp_quote_file.write_text(content, encoding="ascii")

        snap = provider.get_quote("510300.SH")
        assert snap is not None
        assert snap.last_price == Decimal("4.123")
        assert snap.timetag == "20260826103001000"
        assert snap.bid1 == Decimal("4.122")
        assert snap.ask1 == Decimal("4.123")
        assert snap.bid_vols == (100, 200, 300, 400, 500)
        assert snap.ask_vols == (110, 210, 310, 410, 510)
        assert snap.volume == 12345678

    def test_get_quote_skips_broken_last_line(self, provider, temp_quote_file):
        """末行残缺（QMT 写入一半被读到）时回退上一完整行"""
        content = _HEADER
        content += _quote_line(last="4.100", timetag="20260826103000000")
        content += "510300.SH,4.999,4.1"  # 残缺行
        temp_quote_file.write_text(content, encoding="ascii")

        snap = provider.get_quote("510300.SH")
        assert snap is not None
        assert snap.last_price == Decimal("4.100")

    def test_get_quotes_multiple_symbols(self, provider, temp_quote_file):
        content = _HEADER
        content += _quote_line(symbol="510300.SH", last="4.123")
        content += _quote_line(symbol="159915.SZ", last="2.345")
        temp_quote_file.write_text(content, encoding="ascii")

        quotes = provider.get_quotes(["510300.SH", "159915.SZ", "600000.SH"])
        assert len(quotes) == 2
        assert quotes["510300.SH"].last_price == Decimal("4.123")
        assert quotes["159915.SZ"].last_price == Decimal("2.345")

    def test_get_quote_file_missing(self, provider):
        assert provider.get_quote("510300.SH") is None

    def test_get_quote_symbol_not_found(self, provider, temp_quote_file):
        temp_quote_file.write_text(_HEADER + _quote_line(), encoding="ascii")
        assert provider.get_quote("600000.SH") is None

    def test_is_fresh(self, provider, temp_quote_file):
        assert provider.is_fresh() is False  # 文件不存在
        temp_quote_file.write_text(_HEADER + _quote_line(), encoding="ascii")
        assert provider.is_fresh() is True
        # 手工把 mtime 改老
        old = time.time() - 3600
        os.utime(temp_quote_file, (old, old))
        assert provider.is_fresh() is False

    def test_price_provider_fresh(self, provider, temp_quote_file):
        temp_quote_file.write_text(_HEADER + _quote_line(last="4.123"), encoding="ascii")
        fn = provider.make_price_provider()
        prices = fn(["510300.SH"])
        assert prices == {"510300.SH": Decimal("4.123")}

    def test_price_provider_stale_returns_empty(self, provider, temp_quote_file):
        """行情中断时返回空 dict，避免用错价下单"""
        temp_quote_file.write_text(_HEADER + _quote_line(), encoding="ascii")
        old = time.time() - 3600
        os.utime(temp_quote_file, (old, old))
        fn = provider.make_price_provider()
        assert fn(["510300.SH"]) == {}

    def test_get_order_book(self, provider, temp_quote_file):
        temp_quote_file.write_text(_HEADER + _quote_line(), encoding="ascii")
        book = provider.get_order_book("510300.SH")
        assert book is not None
        assert book["bid_prices"][0] == Decimal("4.122")
        assert book["ask_prices"][0] == Decimal("4.123")
        assert len(book["bid_vols"]) == 5
        assert provider.get_order_book("600000.SH") is None

    def test_tail_window_large_file(self, provider, temp_quote_file):
        """大文件只读尾部窗口，仍能取到最新行"""
        content = _HEADER
        # 塞入大量旧行超过 64KB 窗口
        content += _quote_line(last="3.000", timetag="20260826093000000") * 2000
        content += _quote_line(last="4.999", timetag="20260826145959000")
        temp_quote_file.write_text(content, encoding="ascii")
        assert temp_quote_file.stat().st_size > 64 * 1024

        snap = provider.get_quote("510300.SH")
        assert snap is not None
        assert snap.last_price == Decimal("4.999")

    def test_health_check_missing_file(self, provider):
        """健康检查：文件不存在 → down"""
        h = provider.health_check()
        assert h["level"] == "down"
        assert h["ok"] is False
        assert h["file_exists"] is False
        assert "未启动" in h["detail"]

    def test_health_check_fresh(self, provider, temp_quote_file):
        """健康检查：新鲜文件 → ok"""
        temp_quote_file.write_text(_HEADER + _quote_line(), encoding="ascii")
        h = provider.health_check()
        assert h["level"] == "ok"
        assert h["ok"] is True
        assert h["fresh"] is True
        assert h["file_age_seconds"] < 10

    def test_health_check_stale_degraded(self, provider, temp_quote_file):
        """健康检查：2 分钟未更新 → degraded"""
        temp_quote_file.write_text(_HEADER + _quote_line(), encoding="ascii")
        old = time.time() - 120
        os.utime(temp_quote_file, (old, old))
        h = provider.health_check()
        assert h["level"] == "degraded"
        assert h["ok"] is False

    def test_health_check_stale_down(self, provider, temp_quote_file):
        """健康检查：超 5 分钟未更新 → down"""
        temp_quote_file.write_text(_HEADER + _quote_line(), encoding="ascii")
        old = time.time() - 3600
        os.utime(temp_quote_file, (old, old))
        h = provider.health_check()
        assert h["level"] == "down"
        assert "中断" in h["detail"]
