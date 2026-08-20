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
# [A_module] module_id=MOD-TEST-278 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
    derive_exchange_index,
    is_bare_symbol,
    normalize_symbol,
    split_prefix_symbol,
    split_suffix_symbol,
    to_canonical,
)


class TestDeriveExchange:
    """derive_exchange：A 股裸码首位 → exchange 推导。"""

    @pytest.mark.parametrize(
        "symbol,expected",
        [
            ("600519", "SH"),  # 贵州茅台
            ("900901", "SH"),  # 沪市 B 股（3 位前缀 '900'→SH）
            ("000001", "SZ"),  # 平安银行
            ("300750", "SZ"),  # 创业板 宁德时代
            ("510050", "SH"),  # 沪市 ETF
            ("588000", "SH"),  # 科创 50 ETF
            ("159915", "SZ"),  # 深市 ETF
            ("830799", "BJ"),  # 北交所
            ("430047", "BJ"),  # 北交所老三板
            # 1.1.0 新增（#ARCH-DATA-SYMBOL-002）
            ("200026", "SZ"),  # 深市 B 股（'2'→SZ，实测 281K 行）
            ("201872", "SZ"),  # 深市 B 股
            ("920001", "BJ"),  # 北交所 920xxx（2 位 '92'→BJ，避免 '9'→SH 误判）
            ("930001", "BJ"),  # 北交所 930xxx（2 位 '93'→BJ）
            ("903001", "SH"),  # 沪市 B 股 903xxx（3 位 '903'→SH）
            # 1.1.1 新增：可转债 + 国债逆回购前缀消歧
            ("110064", "SH"),  # 沪市可转债（'1'→SZ 是 ETF 规则，110 需 3 位消歧→SH）
            ("113537", "SH"),  # 沪市可转债
            ("123001", "SZ"),  # 深市可转债
            ("128001", "SZ"),  # 深市可转债
            ("204001", "SH"),  # 沪市国债逆回购 GC001（'2'→SZ 是 B 股，204 需 3 位消歧→SH）
        ],
    )
    def test_a_share_prefix_derivation(self, symbol, expected):
        assert derive_exchange(symbol) == expected

    def test_9xx_disambiguation(self):
        """1.1.0 核心消歧：9 前缀不再是单一 SH，按 3 位/2 位前缀细分。"""
        # 沪市 B 股（3 位 900/901/902/903 → SH）
        assert derive_exchange("900901") == "SH"
        assert derive_exchange("901001") == "SH"
        assert derive_exchange("902001") == "SH"
        assert derive_exchange("903001") == "SH"
        # 北交所（2 位 92/93/94 → BJ）
        assert derive_exchange("920001") == "BJ"
        assert derive_exchange("930001") == "BJ"
        assert derive_exchange("940001") == "BJ"
        # 其他 9 前缀仍 → SH（1 位 fallback）
        assert derive_exchange("910001") == "SH"

    def test_b_share_sz_prefix(self):
        """1.1.0 新增：深市 B 股 200xxx/201xxx → SZ（实测 281K 行）。"""
        assert derive_exchange("200026") == "SZ"
        assert derive_exchange("200012") == "SZ"
        assert derive_exchange("201872") == "SZ"

    @pytest.mark.parametrize(
        "symbol",
        [
            "AAPL",  # 美股（字母代码，无法推断）
            "IF2510",  # 期货（字母代码）
            "",  # 空
        ],
    )
    def test_non_a_share_returns_none(self, symbol):
        assert derive_exchange(symbol) is None


class TestDeriveExchangeIndex:
    """derive_exchange_index：指数裸码 → exchange 推导（kline_index 表专用）。

    关键差异：000001 在股票表→SZ（平安银行），在指数表→SH（上证指数）。
    这是 TRAE-082 跨表碰撞消歧的核心。
    """

    @pytest.mark.parametrize(
        "symbol,expected",
        [
            ("000001", "SH"),  # 上证指数（非平安银行！）
            ("000300", "SH"),  # 沪深300
            ("000016", "SH"),  # 上证50
            ("399001", "SZ"),  # 深证成指
            ("399006", "SZ"),  # 创业板指
            ("880001", "SH"),  # 申万全A
            ("930001", "SH"),  # 中证指数
        ],
    )
    def test_index_prefix_derivation(self, symbol, expected):
        assert derive_exchange_index(symbol) == expected

    def test_stock_vs_index_collision_disambig(self):
        """000001 在股票 vs 指数表推导不同 exchange（核心消歧）。"""
        # 股票表（kline_daily）：000001 平安银行 → SZ
        assert derive_exchange("000001") == "SZ"
        # 指数表（kline_index）：000001 上证指数 → SH
        assert derive_exchange_index("000001") == "SH"
        # 两者不同 → symbol_canonical 消歧成功
        assert derive_exchange("000001") != derive_exchange_index("000001")

    @pytest.mark.parametrize(
        "symbol",
        [
            "AAPL",  # 字母代码
            "12",  # 不足 3 位
            "",  # 空
        ],
    )
    def test_non_index_returns_none(self, symbol):
        assert derive_exchange_index(symbol) is None


class TestSplitSuffixSymbol:
    """split_suffix_symbol：后缀式 symbol 拆分。"""

    @pytest.mark.parametrize(
        "symbol,expected_bare,expected_ex",
        [
            ("159865.SZ", "159865", "SZ"),
            ("600519.SH", "600519", "SH"),
            ("000001.SZ", "000001", "SZ"),
            ("AAPL.US", "AAPL", "US"),
        ],
    )
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

    @pytest.mark.parametrize(
        "symbol,expected_bare,expected_ex",
        [
            ("sh501001", "501001", "SH"),
            ("sz159915", "159915", "SZ"),
            ("bj430047", "430047", "BJ"),
        ],
    )
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

    @pytest.mark.parametrize(
        "symbol,exchange,expected",
        [
            ("600519", "SH", "600519.SH"),
            ("000001", "SZ", "000001.SZ"),
            ("000001", "SH", "000001.SH"),  # 上证指数（与平安银行消歧）
        ],
    )
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
