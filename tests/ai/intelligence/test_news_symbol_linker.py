"""NewsSymbolLinker（MOD-INT-NEWS-LINK，tracker #139）单元测试——词表加载/简称匹配/歧义/market 级兜底。

覆盖（92号 §8.4 验收口径）：
- 词表加载：from_entries 注入 / from_ch mock TSV / 畸形条目 fail-closed（ZA-IT-0007）/ 空词表 fail-open
- 简称匹配：归一化精确子串（全角/空白/大小写归一）→ 唯一标的 confidence=0.9
- 代码显式匹配：6 位裸码命中词表→0.95；幻影码（词表外）不关联
- 歧义多标的：一词多标→关联全部候选 ambiguous=True confidence=0.6
- 最长匹配优先：短名被已命中长名包含时剔除
- 公告路径：related_symbol/related_symbols 直用 confidence=1.0
- 无关联兜底：symbols=() 即 market 级 confidence=0.0
全部离线（entries 注入 / ch_client mock），不触网不触库。
"""

from __future__ import annotations

import pandas as pd
import pytest

from zephyr.intelligence.news_symbol_linker import (
    CONFIDENCE_AMBIGUOUS,
    CONFIDENCE_ANNOUNCEMENT,
    CONFIDENCE_CODE_EXPLICIT,
    CONFIDENCE_MARKET,
    CONFIDENCE_NAME_UNIQUE,
    NewsSymbolLinker,
    NewsSymbolLinkerError,
    SymbolLinkage,
    code_to_canonical,
    normalize_text,
    to_canonical,
)

# ── 词表夹具（A 股真实形态样本：含全角字符/多空白/ST 前缀/重名歧义）──
_ENTRIES = [
    ("000001", "平安银行"),
    ("600000", "浦发银行"),
    ("000002", "万  科Ａ"),  # stock_basic 实证形态：内含空格+全角Ａ
    ("600519", "贵州茅台"),
    ("300750", "宁德时代"),
    ("830799", "艾融软件"),
    # 一词多标的（重名简称歧义构造）
    ("600001", "平安科技"),
    ("300001", "平安科技"),
]


def _linker() -> NewsSymbolLinker:
    return NewsSymbolLinker(_ENTRIES)


# ============================================================================
# 1. 归一化与代码规则
# ============================================================================


class TestNormalize:
    """normalize_text / to_canonical 纯函数。"""

    def test_fullwidth_and_whitespace(self) -> None:
        assert normalize_text("万  科Ａ") == "万科A"

    def test_fullwidth_space_removed(self) -> None:
        assert normalize_text("贵州　茅台") == "贵州茅台"  # 　全角空格

    def test_upper_ascii(self) -> None:
        assert normalize_text("st 平安") == "ST平安"

    def test_empty(self) -> None:
        assert normalize_text("") == ""

    def test_code_to_canonical_prefix_rules(self) -> None:
        assert code_to_canonical("600000") == "600000.SH"
        assert code_to_canonical("000001") == "000001.SZ"
        assert code_to_canonical("300750") == "300750.SZ"
        assert code_to_canonical("830799") == "830799.BJ"

    def test_to_canonical_passthrough_with_suffix(self) -> None:
        assert to_canonical("600000.sh") == "600000.SH"
        assert to_canonical(" 600000.SH ") == "600000.SH"

    def test_to_canonical_empty(self) -> None:
        assert to_canonical("") == ""


# ============================================================================
# 2. 词表加载
# ============================================================================


class TestLexiconLoading:
    """词表加载：注入/CH/畸形/空词表。"""

    def test_from_entries_size(self) -> None:
        linker = _linker()
        assert linker.lexicon_size == 7  # 8 条 entries，"平安科技" 重名合并 1 键

    def test_from_ch_mock_tsv(self) -> None:
        """from_ch 经注入 ch_client 加载 stock_basic TSV（离线）。"""
        tsv = "000001\t平安银行\n600000\t浦发银行\n"
        linker = NewsSymbolLinker.from_ch(ch_client=lambda sql: tsv)
        assert linker.lexicon_size == 2
        lk = linker.link("n1", "平安银行发布中报")
        assert lk.symbols == ("000001.SZ",)

    def test_from_ch_failure_fail_open(self) -> None:
        """CH 异常→空词表 fail-open，关联全降级 market 级。"""

        def _boom(sql: str) -> str:
            raise RuntimeError("CH down")

        linker = NewsSymbolLinker.from_ch(ch_client=_boom)
        assert linker.lexicon_size == 0
        lk = linker.link("n1", "平安银行发布中报")
        assert lk.symbols == ()
        assert lk.confidence == CONFIDENCE_MARKET

    def test_malformed_entry_fail_closed(self) -> None:
        """词表条目畸形（空 symbol/空 name）→ ZA-IT-0007 契约违反。"""
        with pytest.raises(NewsSymbolLinkerError) as exc_info:
            NewsSymbolLinker([("", "平安银行")])
        assert exc_info.value.error_code == "ZA-IT-0007"
        with pytest.raises(NewsSymbolLinkerError):
            NewsSymbolLinker([("600000", "")])

    def test_short_name_skipped(self) -> None:
        """归一化后长度<2 的名称不入词表（防超短词误伤）。"""
        linker = NewsSymbolLinker([("600000", "浦")])
        assert linker.lexicon_size == 0
        # 代码仍可在词表（代码匹配独立于名称长度门禁）
        lk = linker.link("n1", "600000 公告")
        assert lk.symbols == ("600000.SH",)


# ============================================================================
# 3. 关联逻辑
# ============================================================================


class TestLinking:
    """link() 关联主逻辑。"""

    def test_name_exact_match_unique(self) -> None:
        """简称精确匹配唯一标的→confidence=0.9，输出 canonical。"""
        lk = _linker().link("n1", "贵州茅台三季度净利润增长超预期")
        assert lk.symbols == ("600519.SH",)
        assert lk.confidence == CONFIDENCE_NAME_UNIQUE
        assert lk.ambiguous is False

    def test_name_normalized_fullwidth(self) -> None:
        """词表全角名称与半角标题互配（归一化对齐）。"""
        lk = _linker().link("n1", "万科A 发布回购公告")
        assert lk.symbols == ("000002.SZ",)

    def test_code_explicit_match(self) -> None:
        """6 位代码显式命中词表→confidence=0.95。"""
        lk = _linker().link("n1", "600519 创历史新高")
        assert lk.symbols == ("600519.SH",)
        assert lk.confidence == CONFIDENCE_CODE_EXPLICIT

    def test_phantom_code_not_linked(self) -> None:
        """幻影码（词表外 6 位数字串）不关联→market 级。"""
        lk = _linker().link("n1", "成交 999999 手 创 123456 纪录")
        assert lk.symbols == ()
        assert lk.confidence == CONFIDENCE_MARKET

    def test_ambiguous_multi_symbol(self) -> None:
        """一词多标的→关联全部候选 ambiguous=True confidence=0.6。"""
        lk = _linker().link("n1", "平安科技发布新战略")
        assert set(lk.symbols) == {"600001.SH", "300001.SZ"}
        assert lk.ambiguous is True
        assert lk.confidence == CONFIDENCE_AMBIGUOUS

    def test_longest_match_subsumption(self) -> None:
        """最长匹配优先：'平安银行' 命中时剔除被包含的短名（若有）。"""
        entries = [("000001", "平安银行"), ("600002", "平安")]  # '平安'≥2字入词表
        lk = NewsSymbolLinker(entries).link("n1", "平安银行业绩大增")
        assert lk.symbols == ("000001.SZ",)
        assert lk.ambiguous is False

    def test_announcement_related_symbol_direct(self) -> None:
        """公告 related_symbol 直用→confidence=1.0，不走规则匹配。"""
        lk = _linker().link("n1", "若干公告标题", related_symbol="600519")
        assert lk.symbols == ("600519.SH",)
        assert lk.confidence == CONFIDENCE_ANNOUNCEMENT

    def test_announcement_related_symbols_list(self) -> None:
        """公告 related_symbols 多标的直用。"""
        lk = _linker().link("n1", "联合公告", related_symbols=["600000.SH", "000001"])
        assert lk.symbols == ("600000.SH", "000001.SZ")
        assert lk.confidence == CONFIDENCE_ANNOUNCEMENT

    def test_no_match_market_level(self) -> None:
        """零命中→market 级（symbols=() confidence=0.0 ambiguous=False）。"""
        lk = _linker().link("n1", "央行开展公开市场操作")
        assert lk.symbols == ()
        assert lk.confidence == CONFIDENCE_MARKET
        assert lk.ambiguous is False

    def test_multi_symbol_news(self) -> None:
        """多标的新闻→全部关联。"""
        lk = _linker().link("n1", "贵州茅台与宁德时代获机构看好")
        assert set(lk.symbols) == {"600519.SH", "300750.SZ"}

    def test_empty_lexicon_all_market(self) -> None:
        """空词表→全部 market 级不抛。"""
        lk = NewsSymbolLinker(()).link("n1", "贵州茅台涨停")
        assert lk.symbols == ()


class TestLinkDf:
    """link_df 批量关联。"""

    def test_batch(self) -> None:
        df = pd.DataFrame(
            {
                "news_id": ["n1", "n2", "n3"],
                "title": ["贵州茅台业绩大增", "央行降准", "平安科技新品"],
                "content": ["", "", ""],
            }
        )
        out = _linker().link_df(df)
        assert len(out) == 3
        assert out[0].symbols == ("600519.SH",)
        assert out[1].symbols == ()  # market 级
        assert out[2].ambiguous is True

    def test_empty_df(self) -> None:
        assert _linker().link_df(pd.DataFrame()) == []


class TestContract:
    """SymbolLinkage 契约。"""

    def test_frozen(self) -> None:
        lk = SymbolLinkage(news_id="n1")
        with pytest.raises(AttributeError):
            lk.confidence = 0.5  # type: ignore[misc]

    def test_defaults(self) -> None:
        lk = SymbolLinkage(news_id="n1")
        assert lk.symbols == ()
        assert lk.confidence == 0.0
        assert lk.ambiguous is False
