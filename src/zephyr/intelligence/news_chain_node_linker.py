# [BLUEPRINT] MOD-INT-NEWS-CHAIN | 待统筹登记（蓝图未建，真源=docs/_working/2026-09-09-news-industry-wiring-directive.md W3 行 + §3 入图交接协议）
# [MODULE] zephyr.intelligence.news_chain_node_linker
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.news_symbol_linker（normalize_text 归一化复用）; zephyr.governance.depgraph_schema（ig_* 图谱只读连接）; zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.intelligence.chain_impact_resolver（W4 冲击标的生成器，消费 ChainNodeHit）; zephyr.intelligence.chain_impact_stream（W5 盘中事件冲击流）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 词表=ig_node JOIN ig_chain(status='active')，墓碑节点（name 含"已并入"）不入词表（合并残留名带 ND- 标注噪声，canonical 信息在并入目标）；同名归一化词候选节点数>8 视为泛化聚合名整词剔除（自动排除"行业聚合"×90 类滚总节点，不硬编码名单）；纯 ASCII 两字母词不入词表（"IP"⊂"IPO" 误命中实证）且匹配时 ASCII 词边界防拆词（"AIPC"⊂"AIPCB" 误命中实证，_splits_ascii_token）；归一化复用 news_symbol_linker.normalize_text（全角→半角+去空白+大写）；匹配=最长词优先+span 占用（长词命中后短词仅在未被覆盖 span 外再命中，防"半导体材料"嵌套重复记"半导体"）；歧义=同词多节点全量产出 ambiguous=True；置信度=name 0.90/alias 0.80 基础，歧义×0.8，截断 [0,1]；空词表 fail-open 返回空结果不抛；注入词表条目畸形（空 node_id/空 name）抛 ChainNodeLinkerError；只读不落库（传导结果由调用方消费）
# [MODIFY-GUARD] 待统筹登记（真源=接线指令 W3 行，蓝图由施工轨补画）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ChainNodeLinkerError(ZA-IT-0029)——注入词表条目畸形时抛；PG 不可达由 from_pg 显式抛（W5 流层 catch 降级），匹配层空词表 fail-open 不抛
# [TESTS] tests/intelligence/test_news_chain_node_linker.py
# [A_module] module_id=MOD-INT-NEWS-CHAIN | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] 接线指令 W3（事件→产业链传导器，TDM 预留坑位 TDM-E-L2-09-1，module_ref 由增长轨落图时挂本模块）

"""
MOD-INT-NEWS-CHAIN NewsChainNodeLinker — 新闻/事件文本→产业链图谱节点传导层（接线 W3）。

功能边界（规则法 MVP，news_symbol_linker 链接手法从标的级升维到图谱节点级）：
- 词表：ig_node 环节名（+aliases 列，当前全空但 schema 支持）——active 链、剔除
  墓碑节点（"已并入"）与泛化聚合名（同词候选>8 整词剔除）
- 匹配：归一化子串扫描，最长词优先+span 占用防嵌套重复命中
- 歧义：同名跨链节点（如"晶圆制造"×4）全量产出 ambiguous=True，由下游
  （W4 冲击标的生成器/消费端）按 chain 上下文裁定或合并
- 输出 ChainNodeHit 只读 frozen dataclass，不写库不挂调度

不做什么：不做 NER/语义模型抽取（规则法 MVP，与 news_symbol_linker 同代际）；
         不做上下游扩散与方向判定（属 MOD-INT-CHAIN-IMPACT W4 施工面）；
         不直接读新闻表（文本由调用方传入，新闻窗拉取属 MOD-INT_IMPACT_STREAM W5）。

依据: docs/_working/2026-09-09-news-industry-wiring-directive.md W3 行
SSoT: depgraph MOD-INT-NEWS-CHAIN（design 态 node 见 depgraph DB）
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: text 参数
#   fields: 参数 text，类型注解 str
#   code: link 方法形参（新闻标题+正文拼接文本）
# - id: I2
#   name: entries 词表
#   fields: (node_id, chain_id, name, tier, aliases) 五元组可迭代
#   code: 构造注入或 from_pg 加载
# 层: 算法
# - id: A1
#   name_zh: ① 词表构建与泛化词剔除
#   name_en: build_vocab
#   intro: 归一化环节名建 term→候选节点映射，同词候选>8 剔除，最长优先扫描序。
#   desc: 墓碑名不入词表；归一化后 len<2 剔除；aliases 展开为独立 term（同候选组）。
#   inputs: I2
#   outputs: _term_map/_terms_sorted
#   invariant: 墓碑/泛化词零命中
# - id: A2
#   name_zh: ② 最长优先 span 占用匹配
#   name_en: link
#   intro: 文本归一化后按词长降序扫描，命中 span 标记占用，短词仅在空闲 span 命中。
#   desc: str.find 全 occurrences 扫描；占用 span 用有序区间表判相交。
#   inputs: I1 A1
#   outputs: list[候选命中]
#   invariant: 嵌套词不重复计分（长词吞并短词 span）
# - id: A3
#   name_zh: ③ 置信度与歧义标注
#   name_en: score_and_flag
#   intro: 基础分 name 0.90/alias 0.80，多候选 ambiguous=True 并 ×0.8，截断 [0,1]。
#   desc: 同一 matched_term 的候选节点共享同一次命中证据（span 与置信度）。
#   inputs: A2
#   outputs: tuple[ChainNodeHit, ...]
#   invariant: confidence∈[0,1]；ambiguous ⇔ 同词候选>1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Final, Iterable, Sequence

from zephyr.intelligence.news_symbol_linker import normalize_text
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "ChainNodeHit",
    "ChainNodeLinker",
    "ChainNodeLinkerError",
    "MAX_CANDIDATES_PER_TERM",
    "normalize_text",
]


class ChainNodeLinkerError(ZephyrBaseError):
    """ZA-IT-0029: 产业链节点链接错误（注入词表条目畸形等）。"""

    error_code = "ZA-IT-0029"


# 泛化聚合名单词候选上限：同词命中节点数超过此值视为滚总名（如"行业聚合"×90）整词剔除
MAX_CANDIDATES_PER_TERM: Final[int] = 8

# 置信度基础分（name 全词命中 / alias 命中）与歧义折减系数
_CONF_NAME: Final[float] = 0.90
_CONF_ALIAS: Final[float] = 0.80
_CONF_AMBIGUOUS_DECAY: Final[float] = 0.8

# 墓碑节点名标注（长城任务墓碑合并法：合并残留节点名带"已并入ND-xxx"标注）
_TOMBSTONE_MARK: Final[str] = "已并入"

# SQL 常量（NO-BARE-SQL gate 豁免：_SQL_ 前缀，与 news_symbol_linker 同约定）
# 词表口径：active 链环节 + 剔墓碑（"已并入"）；aliases 数组列当前全空，展开逻辑已支持
_SQL_VOCAB: Final[str] = (
    "SELECT n.node_id, n.chain_id, n.name, n.tier, n.aliases "  # noqa: bare-sql  模块级 SQL 常量（集中化专项另行治理）
    "FROM ig_node n JOIN ig_chain c ON c.chain_id = n.chain_id "  # noqa: bare-sql  模块级 SQL 常量（集中化专项另行治理）
    "WHERE c.status = 'active' AND n.name NOT LIKE '%已并入%'"  # noqa: bare-sql  模块级 SQL 常量（集中化专项另行治理）
)


@dataclass(frozen=True)
class ChainNodeHit:
    """单次文本命中产出的产业链节点匹配。

    Attributes
    ----------
    node_id / chain_id : 图谱稳定标识（ig_node/ig_chain 主键，文档引用只写此级）。
    node_name / tier : 环节原名（未归一化）与层级（上游/中游/下游，空=通用）。
    match_source : "name"（环节名全词命中）| "alias"（别名命中）。
    matched_term : 命中词表词（原词未归一化，供证据展示）。
    confidence : [0,1]，公式见模块 INVARIANTS。
    ambiguous : 同词多节点=True（下游按 chain 上下文裁定或合并）。
    """

    node_id: str
    chain_id: str
    node_name: str
    tier: str
    match_source: str
    matched_term: str
    confidence: float
    ambiguous: bool


def _overlaps(start: int, end: int, occupied: Sequence[tuple[int, int]]) -> bool:
    """[start, end) 是否与任一已占用区间相交。"""
    return any(start < e and s < end for s, e in occupied)


def _splits_ascii_token(norm: str, start: int, end: int, term: str) -> bool:
    """命中 span 是否拆散了更长的 ASCII 词（词内命中=误命中）。

    仅当 term 的边界字符本身是 ASCII 字母数字、且紧邻文本字符也是 ASCII
    字母数字时判 True——如 "IP" ⊂ "IPO"、"AIPC" ⊂ "AIPCB"；中文边界不受限
    （"AI" in "AI眼镜" 合法）。norm 已归一化大写，无需大小写处理。
    """
    left = start > 0 and term[0].isascii() and norm[start - 1].isascii() and norm[start - 1].isalnum()
    right = end < len(norm) and term[-1].isascii() and norm[end].isascii() and norm[end].isalnum()
    return left or right


def _entry_terms(name: str, aliases: Sequence[str] | None) -> list[tuple[str, str]]:
    """单条目展开为 (词, 来源) 列表（环节名=name 来源，aliases 逐个 alias 来源）。"""
    terms: list[tuple[str, str]] = [(name, "name")]
    for alias in aliases or ():
        alias_s = str(alias or "").strip()
        if alias_s:
            terms.append((alias_s, "alias"))
    return terms


def _build_term_map(
    entries: Iterable[tuple[str, str, str, str, Sequence[str] | None]],
) -> dict[str, list[tuple[str, str, str, str, str, str]]]:
    """词表构建：归一化展开 aliases、剔除墓碑/超短词/纯 ASCII 两字母词、泛化词整词剔除。

    候选元组 = (node_id, chain_id, 原名, tier, 来源, 原词)；同名多节点=歧义候选组。
    """
    term_map: dict[str, list[tuple[str, str, str, str, str, str]]] = {}
    for node_id, chain_id, name, tier, aliases in entries:
        node_s = str(node_id or "").strip()
        name_s = str(name or "").strip()
        if not node_s or not name_s:
            raise ChainNodeLinkerError(f"词表条目畸形（空 node_id/空 name）: {(node_id, name)!r}")
        if _TOMBSTONE_MARK in name_s:
            continue  # 墓碑节点不入词表（INVARIANTS）
        for term, source in _entry_terms(name_s, aliases):
            _add_term(term_map, term, source,
                      (node_s, str(chain_id or "").strip(), name_s, str(tier or "").strip()))
    # 泛化聚合名整词剔除（INVARIANTS：候选>8 的词不进扫描序）
    return {k: v for k, v in term_map.items() if len(v) <= MAX_CANDIDATES_PER_TERM}


def _add_term(
    term_map: dict[str, list[tuple[str, str, str, str, str, str]]],
    term: str,
    source: str,
    candidate: tuple[str, str, str, str],
) -> None:
    """归一化词条入表（超短词/纯 ASCII 两字母词剔除）。candidate=(node_id, chain_id, 原名, tier)。"""
    norm = normalize_text(term)
    if len(norm) < 2:
        return  # 超短词噪声大，不入词表（与 news_symbol_linker 同口径）
    if norm.isascii() and len(norm) < 3:
        return  # 纯 ASCII 两字母词（如"IP"）误命中温床，不入词表（IPO 实证）
    node_s, chain_s, name_s, tier_s = candidate
    term_map.setdefault(norm, []).append((node_s, chain_s, name_s, tier_s, source, term))


class ChainNodeLinker:
    """新闻/事件文本→产业链图谱节点链接器（规则法 MVP）。

    词表经构造注入（测试/离线）或 :meth:`from_pg` 加载（生产）；
    空词表 fail-open：link() 返回空元组不抛。
    """

    def __init__(self, entries: Iterable[tuple[str, str, str, str, Sequence[str] | None]] = ()) -> None:
        """
        Parameters
        ----------
        entries : (node_id, chain_id, name, tier, aliases) 五元组可迭代。
                  条目畸形（空 node_id/空 name）抛 ChainNodeLinkerError（ERROR_CONTRACT）。
        """
        self._term_map = _build_term_map(entries)
        # 长词优先扫描序（span 占用前提）
        self._terms_sorted: Final[tuple[str, ...]] = tuple(
            sorted(self._term_map.keys(), key=len, reverse=True)
        )

    # ------------------------------------------------------------------
    # 词表加载
    # ------------------------------------------------------------------

    @classmethod
    def from_pg(cls, conn_factory: Callable[[], Any] | None = None) -> ChainNodeLinker:
        """从 depgraph PG 加载图谱词表（active 链 + 剔墓碑）。

        conn_factory 可注入（测试 mock）；None 走 depgraph_schema 只读连接。
        PG 不可达异常显式上抛（调用方 W5 流层 catch 降级），查询为空→空词表 fail-open。
        """
        if conn_factory is None:
            from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

            conn_factory = get_depgraph_pg_connection
        conn = conn_factory()
        try:
            cur = conn.cursor()
            cur.execute(_SQL_VOCAB)
            rows = cur.fetchall()
        finally:
            try:
                conn.close()
            except Exception:  # noqa: BLE001 — 连接关闭失败静默（只读查询已完成）
                pass
        return cls(
            (node_id, chain_id, name, tier, aliases or []) for node_id, chain_id, name, tier, aliases in rows
        )

    # ------------------------------------------------------------------
    # 链接
    # ------------------------------------------------------------------

    def vocab_size(self) -> int:
        """词表词数（归一化后词条数，非节点数）。"""
        return len(self._term_map)

    def link(self, text: str) -> tuple[ChainNodeHit, ...]:
        """文本→产业链节点命中集（最长优先+span 占用；空词表/空文本→空元组）。"""
        norm = normalize_text(text)
        if not norm or not self._terms_sorted:
            return ()
        occupied: list[tuple[int, int]] = []  # 已占用 [start, end) 区间
        hits: list[ChainNodeHit] = []
        for term in self._terms_sorted:
            candidates = self._term_map[term]
            start = norm.find(term)
            while start >= 0:
                end = start + len(term)
                if _overlaps(start, end, occupied) or _splits_ascii_token(norm, start, end, term):
                    start = norm.find(term, start + 1)
                    continue
                # 同词候选共享同一次命中证据；多候选=歧义（置信度折减）
                ambiguous = len(candidates) > 1
                base = _CONF_ALIAS if candidates[0][4] == "alias" else _CONF_NAME
                conf = min(1.0, base * (_CONF_AMBIGUOUS_DECAY if ambiguous else 1.0))
                for node_id, chain_id, name, tier, _source, raw_term in candidates:
                    hits.append(
                        ChainNodeHit(
                            node_id=node_id,
                            chain_id=chain_id,
                            node_name=name,
                            tier=tier,
                            match_source=_source,
                            matched_term=raw_term,
                            confidence=conf,
                            ambiguous=ambiguous,
                        )
                    )
                occupied.append((start, end))
                start = norm.find(term, start + 1)
        return tuple(hits)
