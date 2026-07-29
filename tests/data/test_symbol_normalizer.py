# [A_test] module_id: MOD-TEST-symbol_normalizer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-278 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.data.test_symbol_normalizer
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/data/test_symbol_normalizer.py
# [TTL] permanent
# [ARCH-REF] #ARCH-DATA-SYMBOL-001 TRAE-082
"""test_symbol_normalizer.py — TRAE-082 symbol 标准化模块测试。

覆盖：
  - derive_exchange：A 股裸码前缀推断
  - split_suffix_symbol：后缀式拆分（tushare/akshare 格式）
  - split_prefix_symbol：前缀式拆分（lof_list 旧格式）
  - to_canonical：canonical key 构造
  - normalize_symbol：三格式归一
  - is_bare_symbol：裸码判定（provider 写入校验）
  - 治本场景：000001 裸码碰撞（平安银行 SZ vs 上证指数 SH）
"""
from __future__ import annotations

import pytest

from zephyr.data.symbol_normalizer import (
    derive_exchange,
    split_suffix_symbol,
    split_prefix_symbol,
    to_canonical,
    normalize_symbol,
    is_bare_symbol,
)


class TestDeriveExchange:
    """derive_exchange：A 股裸码首位 → exchange 推导。"""

    @pytest.mark.parametrize("symbol,expected", [
        ("600519", "SH"),   # 贵州茅台
        ("900901", "SH"),   # B 股
        ("000001", "SZ"),   # 平安银行
        ("300750", "SZ"),   # 创业板 宁德时代
        ("510050", "SH"),   # 沪市 ETF
        ("588000", "SH"),   # 科创 50 ETF
        ("159915", "SZ"),   # 深市 ETF
        ("830799", "BJ"),   # 北交所
        ("430047", "BJ"),   # 北交所老三板
    ])
    def test_a_share_prefix_derivation(self, symbol, expected):
        assert derive_exchange(symbol) == expected

    @pytest.mark.parametrize("symbol", [
        "AAPL",     # 美股（字母代码，无法推断）
        "IF2510",   # 期货（字母代码）
        "",         # 空
    ])
    def test_non_a_share_returns_none(self, symbol):
        assert derive_exchange(symbol) is None


class TestSplitSuffixSymbol:
    """split_suffix_symbol：后缀式 symbol 拆分。"""

    @pytest.mark.parametrize("symbol,expected_bare,expected_ex", [
        ("159865.SZ", "159865", "SZ"),
        ("600519.SH", "600519", "SH"),
        ("000001.SZ", "000001", "SZ"),
        ("AAPL.US", "AAPL", "US"),
    ])
    def test_suffix_split(self, symbol, expected_bare, expected_ex):
        bare, ex = split_suffix_symbol(symbol)
        assert bare == expected_bare
        assert ex == expected_ex

    def test_bare_code_returns_none_exchange(self):
        bare, ex = split_suffix_symbol("600519")
        assert bare == "600519"
        assert ex is None

    def test_empty_input(self):
        assert split_suffix_symbol("") == ("", None)


class TestSplitPrefixSymbol:
    """split_prefix_symbol：前缀式 symbol 拆分（lof_list 旧格式）。"""

    @pytest.mark.parametrize("symbol,expected_bare,expected_ex", [
        ("sh501001", "501001", "SH"),
        ("sz159915", "159915", "SZ"),
        ("bj430047", "430047", "BJ"),
    ])
    def test_prefix_split(self, symbol, expected_bare, expected_ex):
        bare, ex = split_prefix_symbol(symbol)
        assert bare == expected_bare
        assert ex == expected_ex

    def test_bare_code_returns_none_exchange(self):
        bare, ex = split_prefix_symbol("600519")
        assert bare == "600519"
        assert ex is None

    def test_empty_input(self):
        assert split_prefix_symbol("") == ("", None)


class TestToCanonical:
    """to_canonical：symbol_canonical 派生。"""

    @pytest.mark.parametrize("symbol,exchange,expected", [
        ("600519", "SH", "600519.SH"),
        ("000001", "SZ", "000001.SZ"),
        ("000001", "SH", "000001.SH"),  # 上证指数（与平安银行消歧）
    ])
    def test_canonical_construction(self, symbol, exchange, expected):
        assert to_canonical(symbol, exchange) == expected

    def test_empty_symbol(self):
        assert to_canonical("", "SH") == ""

    def test_empty_exchange_returns_bare(self):
        assert to_canonical("AAPL", "") == "AAPL"


class TestNormalizeSymbol:
    """normalize_symbol：三格式归一（治本 #ARCH-DATA-SYMBOL-001）。"""

    def test_bare_code_with_derivation(self):
        bare, ex = normalize_symbol("600519")
        assert bare == "600519"
        assert ex == "SH"

    def test_suffix_format(self):
        bare, ex = normalize_symbol("600519.SH")
        assert bare == "600519"
        assert ex == "SH"

    def test_prefix_format(self):
        bare, ex = normalize_symbol("sh501001")
        assert bare == "501001"
        assert ex == "SH"

    def test_unknown_returns_none_exchange(self):
        bare, ex = normalize_symbol("AAPL")
        assert bare == "AAPL"
        assert ex is None

    def test_empty(self):
        assert normalize_symbol("") == ("", None)


class TestIsBareSymbol:
    """is_bare_symbol：裸码判定（provider 写入校验 INV-001）。"""

    @pytest.mark.parametrize("symbol", ["600519", "000001", "159915", "AAPL"])
    def test_bare_codes(self, symbol):
        assert is_bare_symbol(symbol) is True

    @pytest.mark.parametrize("symbol", ["600519.SH", "sh501001", "159865.SZ"])
    def test_non_bare_codes(self, symbol):
        assert is_bare_symbol(symbol) is False

    def test_empty(self):
        assert is_bare_symbol("") is False


class TestSymbolCollisionFix:
    """治本场景：000001 裸码跨表碰撞（TRAE-082 核心动机）。

    kline_daily 000001 = 平安银行（SZ）
    kline_index 000001 = 上证指数（SH）
    裸码相同但 exchange 不同 → symbol_canonical 消歧。
    """

    def test_same_bare_code_different_exchange(self):
        """000001 在不同表通过 exchange 消歧。"""
        # 平安银行（kline_daily）
        bank_bare, bank_ex = normalize_symbol("000001.SZ")
        assert bank_bare == "000001"
        assert bank_ex == "SZ"

        # 上证指数（kline_index）
        index_bare, index_ex = normalize_symbol("000001.SH")
        assert index_bare == "000001"
        assert index_ex == "SH"

        # 裸码相同
        assert bank_bare == index_bare

        # canonical 不同（消歧成功）
        assert to_canonical(bank_bare, bank_ex) == "000001.SZ"
        assert to_canonical(index_bare, index_ex) == "000001.SH"
        assert to_canonical(bank_bare, bank_ex) != to_canonical(index_bare, index_ex)
