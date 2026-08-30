# [BLUEPRINT] MOD-INT-NEWS-LINK | 待统筹登记（92号清单 §8.4 M3-② / tracker #139）
# [MODULE] zephyr.intelligence.news_symbol_linker
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.data.ch_reader（默认 CH 读取通道）; zephyr.data.table_registry（表名解析，fail-open 降级）
# [CONSUMERS] zephyr.intelligence.nightly_sentiment_window（夜间情绪聚合标的关联）；MOD-SIG-002 信号生成器（后续波次，tracker #139 CTR-INT-AISA 契约对齐候选）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 公告 related_symbol(s) 字段非空时直用（confidence=1.0）；新闻走规则 MVP：6 位代码显式匹配须命中词表（幻影码不关联）+ 证券简称归一化精确子串匹配（最长匹配优先，短名被长名包含则剔除）；一词多标的→关联全部候选且 ambiguous=True；零命中→symbols=() 即 market 级；词表为空 fail-open 不抛（全部 market 级）；归一化=去全部空白（含 ）+ 全角 ASCII 转半角 + 大写
# [MODIFY-GUARD] 待统筹登记（92号清单 §8.4）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] NewsSymbolLinkerError(ZA-IT-0007)——词表条目畸形（空 symbol/空 name）时抛；CH 不可达/词表为空走降级不抛
# [TESTS] tests/intelligence/test_news_symbol_linker.py
# [A_module] module_id=MOD-INT-NEWS-LINK | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] tracker #139 symbol 级舆情标的关联（26号备忘 §2.7 情绪作事件信号维度非独立 alpha）

"""
MOD-INT-NEWS-LINK NewsSymbolLinker — 新闻/公告→标的关联层 MVP（tracker #139 闭环）。

功能边界（MVP，规则法）：
- 公告路径：news_data 表 related_symbol/related_symbols 字段非空时直用（源已标注标的）
- 新闻路径：证券简称/代码词表匹配——
  ① 6 位代码显式匹配（文本中 6 位数字串须命中词表代码，幻影码不关联）
  ② 简称归一化精确子串匹配（去空白+全半角统一+大写；最长匹配优先剔除被包含短名）
  ③ 歧义处理：一词多标的（如重名简称）→关联全部候选但 ambiguous=True
  ④ 无关联→symbols=()（market 级，由下游按市场级情绪处理）
- 词表来源：stock_basic 最新快照（当前可交易 universe 口径），也可注入 entries（测试/离线）

不做什么：不做 NER 模型抽取（MVP 规则法，26号备忘 BM-SEL-19 漏斗联动候选）；
         不写库（关联结果由调用方聚合落库）；不做情绪打分（属 MOD-INT-AISA 施工面）。

依据: 92号清单 §8.4 + 44号备忘 §4 表 M3-② 行 + tracker #139
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: text 参数
#   fields: 参数 text，类型注解 str
#   code: news_symbol_linker.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: code 参数
#   fields: 参数 code，类型注解 str
#   code: news_symbol_linker.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: symbol 参数
#   fields: 参数 symbol，类型注解 str
#   code: news_symbol_linker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① normalize_text
#   name_en: normalize_text
#   intro: 文本归一化：全角 ASCII→半角、去全部空白、转大写（简称精确匹配前提）。
#   desc: 文本归一化：全角 ASCII→半角、去全部空白、转大写（简称精确匹配前提）。；源码 L167-L171
#   inputs: text
#   outputs: str
# - id: A2
#   name_zh: ② code_to_canonical
#   name_en: code_to_canonical
#   intro: 6 位裸码→canonical 形式（前缀推导交易所，与 stock_basic TRAE-082 派生规则同口径）。
#   desc: 6 位裸码→canonical 形式（前缀推导交易所，与 stock_basic TRAE-082 派生规则同口径）。 110/113/204/900/901/902/903→S…；源码 L174-L197
#   inputs: code
#   outputs: str
# - id: A3
#   name_zh: ③ to_canonical
#   name_en: to_canonical
#   intro: 任意形式标的代码→canonical（已带后缀的原样返回，6 位裸码按前缀推导）。
#   desc: 任意形式标的代码→canonical（已带后缀的原样返回，6 位裸码按前缀推导）。；源码 L200-L207
#   inputs: symbol
#   outputs: str
# - id: A4
#   name_zh: ④ NewsSymbolLinker
#   name_en: NewsSymbolLinker
#   intro: 新闻/公告→标的关联器（规则法 MVP）。
#   desc: 新闻/公告→标的关联器（规则法 MVP）。 词表经构造注入或 from_ch 加载；空词表 fail-open（全部关联结果为 market 级）。；公共方法（定义序）: from_ch, lexicon_size,…
#   inputs: entries
#   outputs: 返回值
#   （注：A4 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.intelligence.nightly_sentiment_window（夜间情绪聚合标的关联）；MOD-SIG-002 信号生成器（后续波次…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Final, Iterable

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # noqa: BLE001  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

if TYPE_CHECKING:
    import pandas as pd

log = logging.getLogger(__name__)

# ============================================================================
# 1. 错误契约
# ============================================================================


class NewsSymbolLinkerError(ZephyrBaseError):
    """ZA-IT-0007: NewsSymbolLinker 错误（词表条目畸形等输入契约违反）。"""

    error_code = "ZA-IT-0007"


# ============================================================================
# 2. 数据契约
# ============================================================================

# 置信度档位（规则法 MVP 语义）
CONFIDENCE_ANNOUNCEMENT: Final = 1.0  # 公告 related_symbol 直给
CONFIDENCE_CODE_EXPLICIT: Final = 0.95  # 6 位代码显式命中词表
CONFIDENCE_NAME_UNIQUE: Final = 0.9  # 简称精确匹配唯一标的
CONFIDENCE_AMBIGUOUS: Final = 0.6  # 一词多标的歧义关联
CONFIDENCE_MARKET: Final = 0.0  # 无关联→market 级


@dataclass(frozen=True, slots=True)
class SymbolLinkage:
    """单条新闻/公告的标的关联结果（公开数据契约）。

    symbols 为 canonical 形式（如 600000.SH）；空元组 = market 级（无标的关联）。
    ambiguous=True 表示一词多标的，symbols 含全部候选。
    """

    news_id: str
    symbols: tuple[str, ...] = field(default_factory=tuple)
    confidence: float = CONFIDENCE_MARKET
    ambiguous: bool = False


# ============================================================================
# 3. 归一化与代码规则
# ============================================================================

# 全角 ASCII（！-～）→ 半角映射表（stock_basic 名称含全角字符实证：'万  科Ａ'）
_FW_TO_HW: Final[dict[int, int]] = {0xFF01 + i: 0x21 + i for i in range(94)}
_FW_TO_HW[0x3000] = 0x20  # 全角空格→半角空格（随后统一去除）

_WS_PATTERN: Final[re.Pattern[str]] = re.compile(r"\s+")

# 6 位数字代码显式匹配（边界防子串误伤：前后不得再跟数字）
_CODE_PATTERN: Final[re.Pattern[str]] = re.compile(r"(?<!\d)(\d{6})(?!\d)")


def normalize_text(text: str) -> str:
    """文本归一化：全角 ASCII→半角、去全部空白、转大写（简称精确匹配前提）。"""
    if not text:
        return ""
    return _WS_PATTERN.sub("", text.translate(_FW_TO_HW)).upper()


def code_to_canonical(code: str) -> str:
    """6 位裸码→canonical 形式（前缀推导交易所，与 stock_basic TRAE-082 派生规则同口径）。

    110/113/204/900/901/902/903→SH；123/128→SZ；43/83/87/92/93/94→BJ；
    4/8→BJ；5/6/9→SH；0/1/2/3→SZ；无法推导→原样返回（不编造后缀）。
    """
    if not (len(code) == 6 and code.isdigit()):
        return code
    if "." in code:
        return code
    p3, p2, p1 = code[:3], code[:2], code[:1]
    if p3 in ("110", "113", "204", "900", "901", "902", "903"):
        exch = "SH"
    elif p3 in ("123", "128"):
        exch = "SZ"
    elif p2 in ("43", "83", "87", "92", "93", "94") or p1 in ("4", "8"):
        exch = "BJ"
    elif p1 in ("5", "6", "9"):
        exch = "SH"
    elif p1 in ("0", "1", "2", "3"):
        exch = "SZ"
    else:
        return code
    return f"{code}.{exch}"


def to_canonical(symbol: str) -> str:
    """任意形式标的代码→canonical（已带后缀的原样返回，6 位裸码按前缀推导）。"""
    s = (symbol or "").strip()
    if not s:
        return ""
    if "." in s:
        return s.upper()
    return code_to_canonical(s)


# ============================================================================
# 4. 词表加载（stock_basic 最新快照 / 注入 entries）
# ============================================================================

# SQL 常量（NO-BARE-SQL gate 豁免：_SQL_ 前缀，与 ch_reader/overnight_boundary_reviser 同约定）
_SQL_LEXICON = "SELECT symbol, name FROM {table} FINAL WHERE trade_date = (SELECT max(trade_date) FROM {table})"


class NewsSymbolLinker:
    """新闻/公告→标的关联器（规则法 MVP）。

    词表经构造注入或 from_ch 加载；空词表 fail-open（全部关联结果为 market 级）。
    """

    def __init__(self, entries: Iterable[tuple[str, str]] = ()) -> None:
        """
        Parameters
        ----------
        entries : (symbol, name) 可迭代对（symbol 任意形式，内部转 canonical）。
                  条目畸形（空 symbol/空 name）抛 NewsSymbolLinkerError（ERROR_CONTRACT）。
        """
        # name_norm -> 候选 canonical symbols（保序去重）
        self._name_map: dict[str, list[str]] = {}
        # 6 位裸码 -> canonical
        self._code_map: dict[str, str] = {}
        for symbol, name in entries:
            symbol_s = (symbol or "").strip()
            name_s = str(name or "").strip()
            if not symbol_s or not name_s:
                raise NewsSymbolLinkerError(f"词表条目畸形（空 symbol/空 name）: {(symbol, name)!r}")
            canonical = to_canonical(symbol_s)
            self._code_map.setdefault(symbol_s.split(".")[0], canonical)
            norm = normalize_text(name_s)
            if len(norm) < 2:
                continue  # 超短名称噪声大，不入词表（A 股简称≥2 字）
            bucket = self._name_map.setdefault(norm, [])
            if canonical not in bucket:
                bucket.append(canonical)
        # 长名优先扫描序（最长匹配优先的剔除依据）
        self._names_sorted: Final[tuple[str, ...]] = tuple(sorted(self._name_map.keys(), key=len, reverse=True))

    # ------------------------------------------------------------------
    # 词表加载
    # ------------------------------------------------------------------

    @classmethod
    def from_ch(cls, ch_client: Callable[[str], str] | None = None) -> NewsSymbolLinker:
        """从 stock_basic 最新快照加载词表（当前可交易 universe 口径）。

        CH 不可达/查询为空 → 空词表实例（fail-open，全部关联降级 market 级）。
        ch_client 可注入（测试 mock/离线）；None 走 zephyr.data.ch_reader.query。
        """
        try:
            from zephyr.data.table_registry import get_registry

            table = get_registry().table("meta_stock_basic")
        except Exception:  # noqa: BLE001 — fail-open：表名解析失败降级常量
            table = "c1_market.stock_basic"
        sql = _SQL_LEXICON.format(table=table)
        try:
            if ch_client is not None:
                tsv = ch_client(sql)
            else:
                from zephyr.data import ch_reader

                tsv = ch_reader.query(sql)
        except Exception as exc:  # noqa: BLE001 — fail-open：CH 不可达降级空词表
            log.warning("stock_basic 词表加载异常，降级空词表: %s", exc)
            return cls(())
        entries: list[tuple[str, str]] = []
        for line in (tsv or "").strip().split("\n"):
            parts = line.rstrip("\r").split("\t")
            if len(parts) >= 2 and parts[0].strip() and parts[1].strip():
                entries.append((parts[0].strip(), parts[1].strip()))
        log.info("stock_basic 词表加载 %d 条", len(entries))
        return cls(entries)

    @property
    def lexicon_size(self) -> int:
        """词表名称条目数（0=空词表，关联全降级 market 级）。"""
        return len(self._name_map)

    # ------------------------------------------------------------------
    # 关联
    # ------------------------------------------------------------------

    def link(
        self,
        news_id: str,
        title: str,
        content: str = "",
        *,
        related_symbol: str = "",
        related_symbols: Iterable[str] = (),
    ) -> SymbolLinkage:
        """单条新闻/公告→标的关联。

        优先级：①公告 related_symbol(s) 直用；②6 位代码显式匹配（须命中词表）；
        ③简称精确匹配（最长匹配优先）。零命中→market 级（symbols=()）。
        """
        nid = str(news_id or "")

        # ① 公告路径：源已标注标的字段直用
        direct = [to_canonical(s) for s in (related_symbols or ()) if str(s).strip()]
        if not direct and str(related_symbol or "").strip():
            direct = [to_canonical(str(related_symbol))]
        if direct:
            return SymbolLinkage(
                news_id=nid, symbols=tuple(dict.fromkeys(direct)), confidence=CONFIDENCE_ANNOUNCEMENT, ambiguous=False
            )

        text = normalize_text(f"{title} {content}" if content else str(title or ""))
        if not text or (not self._name_map and not self._code_map):
            return SymbolLinkage(news_id=nid)

        found: list[str] = []  # 保序去重的候选 canonical symbols
        ambiguous = False
        confidence = CONFIDENCE_MARKET

        # ② 6 位代码显式匹配（幻影码不关联：须命中词表代码）
        code_hits = [c for c in _CODE_PATTERN.findall(text) if c in self._code_map]
        if code_hits:
            confidence = CONFIDENCE_CODE_EXPLICIT
            for c in code_hits:
                canonical = self._code_map[c]
                if canonical not in found:
                    found.append(canonical)

        # ③ 简称精确匹配（归一化子串；长名优先，剔除被已命中长名包含的短名）
        name_hits: list[str] = []
        for name in self._names_sorted:
            if name in text and not any(name != hit and name in hit for hit in name_hits):
                name_hits.append(name)
        for name in name_hits:
            candidates = self._name_map[name]
            if len(candidates) > 1:
                ambiguous = True
            for canonical in candidates:
                if canonical not in found:
                    found.append(canonical)
        if name_hits and confidence == CONFIDENCE_MARKET:
            confidence = CONFIDENCE_AMBIGUOUS if ambiguous else CONFIDENCE_NAME_UNIQUE
        elif ambiguous:
            confidence = min(confidence, CONFIDENCE_AMBIGUOUS) if confidence else CONFIDENCE_AMBIGUOUS

        if not found:
            return SymbolLinkage(news_id=nid)
        return SymbolLinkage(news_id=nid, symbols=tuple(found), confidence=confidence, ambiguous=ambiguous)

    def link_df(
        self,
        df: pd.DataFrame,
        title_col: str = "title",
        content_col: str = "content",
        news_id_col: str = "news_id",
    ) -> list[SymbolLinkage]:
        """批量关联（新闻 DataFrame → SymbolLinkage 列表，行序保持）。"""
        if df.empty:
            return []
        out: list[SymbolLinkage] = []
        for _, row in df.iterrows():
            out.append(
                self.link(
                    str(row.get(news_id_col, "")),
                    str(row.get(title_col, "")),
                    str(row.get(content_col, "")),
                )
            )
        return out


# ============================================================================
# 5. 模块导出
# ============================================================================

__all__: Final = [
    "NewsSymbolLinkerError",
    "SymbolLinkage",
    "NewsSymbolLinker",
    "normalize_text",
    "to_canonical",
    "code_to_canonical",
    "CONFIDENCE_ANNOUNCEMENT",
    "CONFIDENCE_CODE_EXPLICIT",
    "CONFIDENCE_NAME_UNIQUE",
    "CONFIDENCE_AMBIGUOUS",
    "CONFIDENCE_MARKET",
]
