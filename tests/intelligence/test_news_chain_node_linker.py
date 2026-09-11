"""NewsChainNodeLinker（MOD-INT-NEWS-CHAIN，接线 W3）单元测试——词表/匹配/歧义/墓碑/泛化词。

覆盖（接线指令 W3 验收口径：命中+置信度；未命中/歧义路径 + 红蓝对抗）：
- 词表构建：注入 entries / 墓碑剔除（"已并入"）/ 泛化词整词剔除（候选>8）/ 超短词剔除
- 匹配：归一化子串（全角/空白/大小写）→ name 0.90 / alias 0.80
- 嵌套防重：最长词优先+span 占用（"半导体材料"命中后"半导体"不再单记）
- 歧义：同名跨链多节点→全量产出 ambiguous=True ×0.8
- 未命中 fail-open：空文本/空词表→空元组不抛
- 红蓝·边界：纯空白文本/全角文本/单字符词攻击
- 红蓝·故障：from_pg 连接工厂异常上抛（fail-closed 显式契约）
- 红蓝·前视：词表注入畸形条目（空 node_id/空 name）fail-closed（ZA-IT-0029）
全部离线（entries 注入 / conn_factory mock），不触网不触库。
"""

from __future__ import annotations

import pytest

from zephyr.intelligence.news_chain_node_linker import (
    MAX_CANDIDATES_PER_TERM,
    ChainNodeHit,
    ChainNodeLinker,
    ChainNodeLinkerError,
)

# ── 词表夹具（图谱真实形态样本：墓碑名/跨链重名/泛化滚总名）──
_ENTRIES = [
    ("ND-1", "CH-1", "半导体材料", "上游", None),
    ("ND-2", "CH-1", "光刻胶生产", "中游", None),
    ("ND-3", "CH-2", "晶圆制造", "中游", None),
    ("ND-4", "CH-3", "晶圆制造", "中游", None),  # 跨链重名（歧义）
    # 墓碑节点（长城墓碑合并法命名形态）
    ("ND-T1", "CH-9", "半导体材料（已并入ND-1-自ND-T1）", "上游", None),
    ("ND-T2", "CH-9", "电子布（已并入ND-519417e6a5f5-自ND-T2）", "上游", None),
] + [
    (f"ND-G{i}", "CH-G", "行业聚合", "", None) for i in range(MAX_CANDIDATES_PER_TERM + 4)
]


def _linker() -> ChainNodeLinker:
    return ChainNodeLinker(_ENTRIES)


# ============================================================================
# 1. 词表构建
# ============================================================================


class TestVocab:
    def test_vocab_size_after_exclusions(self) -> None:
        # 半导体材料 / 光刻胶生产 / 晶圆制造（2 候选=1 词）= 3 词；
        # 墓碑×2 与泛化词（12 候选>8）均不入词表
        assert _linker().vocab_size() == 3

    def test_tombstone_never_hits(self) -> None:
        hits = _linker().link("电子布（已并入ND-519417e6a5f5-自ND-T2）涨价")
        assert hits == ()  # 墓碑名整体不入词表

    def test_generic_rollup_never_hits(self) -> None:
        hits = _linker().link("行业聚合度提升")
        assert hits == ()

    def test_short_term_dropped(self) -> None:
        lk = ChainNodeLinker([("ND-S", "CH-1", "硅", "上游", None)])
        assert lk.vocab_size() == 0
        assert lk.link("硅涨价") == ()

    def test_alias_term_supported(self) -> None:
        lk = ChainNodeLinker([("ND-A", "CH-1", "第三代半导体", "中游", ["SiC", "碳化硅"])])
        assert lk.vocab_size() == 3
        hits = lk.link("碳化硅衬底扩产")
        assert len(hits) == 1 and hits[0].match_source == "alias"
        assert hits[0].confidence == pytest.approx(0.80)


# ============================================================================
# 2. 匹配与置信度
# ============================================================================


class TestMatch:
    def test_normalized_fullwidth_and_case(self) -> None:
        lk = ChainNodeLinker([("ND-1", "CH-1", "LED 芯片", "中游", None)])
        # 全角字母+内部空格归一化后命中
        assert len(lk.link("ＬＥＤ芯片涨价")) == 1

    def test_multi_hit_single_news(self) -> None:
        hits = _linker().link("半导体材料涨价，光刻胶生产受益")
        assert {h.node_name for h in hits} == {"半导体材料", "光刻胶生产"}

    def test_confidence_unique_name(self) -> None:
        hits = _linker().link("半导体材料板块走强")
        assert len(hits) == 1
        assert hits[0].confidence == pytest.approx(0.90)
        assert hits[0].ambiguous is False

    def test_ambiguous_duplicate_names(self) -> None:
        hits = _linker().link("晶圆制造稼动率回升")
        assert len(hits) == 2  # 同词两节点全量产出
        assert all(h.ambiguous for h in hits)
        assert {h.node_id for h in hits} == {"ND-3", "ND-4"}
        assert all(h.confidence == pytest.approx(0.72) for h in hits)  # 0.9×0.8

    def test_no_double_count_nested(self) -> None:
        # "半导体材料" 命中后，其子串场合不应再衍生（无 "半导体" 词时体现为单命中）
        hits = _linker().link("半导体材料涨价")
        assert [h.node_name for h in hits] == ["半导体材料"]


# ============================================================================
# 3. 未命中 / fail-open
# ============================================================================


class TestMissAndFailOpen:
    def test_empty_text(self) -> None:
        assert _linker().link("") == ()

    def test_no_match(self) -> None:
        assert _linker().link("央行开展逆回购操作") == ()

    def test_empty_vocab_fail_open(self) -> None:
        lk = ChainNodeLinker([])
        assert lk.vocab_size() == 0
        assert lk.link("半导体材料涨价") == ()


# ============================================================================
# 4. 红蓝对抗（边界/故障/前视）
# ============================================================================


class TestRedBlue:
    """红蓝对抗 ≥3 手法留痕：边界 / 故障 / 前视。"""

    def test_rb_boundary_whitespace_only_text(self) -> None:
        # 边界：纯空白/控制字符文本归一化后为空
        assert _linker().link("   \t\n  ") == ()

    def test_rb_boundary_substring_aggression(self) -> None:
        # 边界：词表词作为更长无关词的子串出现——"光刻胶生产"藏在超长拼接串中仍属合法命中；
        # 但词表外相近词（"光刻机生产"）不得误命中
        lk = ChainNodeLinker([("ND-2", "CH-1", "光刻胶生产", "中游", None)])
        assert lk.link("光刻机生产线扩产") == ()
        assert len(lk.link("光刻胶生产线扩产")) == 1

    def test_rb_fault_pg_unreachable_raises(self) -> None:
        # 故障：PG 不可达 → from_pg 显式上抛（fail-closed 契约，由 W5 流层降级）
        def _boom() -> object:
            raise RuntimeError("connection refused")

        with pytest.raises(RuntimeError):
            ChainNodeLinker.from_pg(_boom)

    def test_rb_lookahead_malformed_entries_fail_closed(self) -> None:
        # 前视：畸形词表注入（空 node_id/空 name）→ ZA-IT-0029 fail-closed
        with pytest.raises(ChainNodeLinkerError):
            ChainNodeLinker([("", "CH-1", "半导体材料", "上游", None)])
        with pytest.raises(ChainNodeLinkerError):
            ChainNodeLinker([("ND-1", "CH-1", "", "上游", None)])

    def test_rb_lookahead_tombstone_injected_still_filtered(self) -> None:
        # 前视：攻击者绕过 SQL 侧直接注入墓碑行 → 构造器仍按名剔除（双保险）
        lk = ChainNodeLinker([("ND-X", "CH-1", "半导体（已并入ND-1-自ND-X）", "中游", None)])
        assert lk.vocab_size() == 0

    def test_rb_lookahead_ascii_intra_word_no_hit(self) -> None:
        # 前视（2026-09-11 24h dry-run 实证回归）："明星IPO项目"不得拆出"IP"、
        # "AIPCB"不得拆出"AIPC"——ASCII 词内命中全拦
        lk = ChainNodeLinker([
            ("ND-IP", "CH-1", "IP", "", None),
            ("ND-AIPC", "CH-2", "AIPC", "中游", None),
        ])
        assert lk.vocab_size() == 1  # 两字母纯 ASCII 词"IP"直接不入词表
        assert lk.link("明星IPO项目、并购计划引关注") == ()
        assert lk.link("AIPCB需求高增长") == ()  # AIPC ⊂ AIPCB 拆词拦截
        assert len(lk.link("AIPC 终端放量")) == 1  # 独立出现合法命中

    def test_rb_lookahead_mixed_cjk_ascii_boundary(self) -> None:
        # 前视：CJK 邻接不受 ASCII 词边界限制——"AI设备"独立出现合法命中，
        # 且其 ASCII 词头不因左侧邻接 CJK 被误拦
        lk = ChainNodeLinker([("ND-AI", "CH-1", "AI设备", "中游", None)])
        assert len(lk.link("AI设备出货创新高")) == 1
        assert len(lk.link("全新AI设备发布")) == 1

    def test_rb_boundary_hit_dataclass_frozen(self) -> None:
        hits = _linker().link("半导体材料涨价")
        with pytest.raises(Exception):  # frozen dataclass 拒绝改写
            hits[0].confidence = 1.0  # type: ignore[misc]


# ============================================================================
# 5. from_pg SQL 侧口径（mock 连接验证行解包与 aliases 展开）
# ============================================================================


class TestFromPg:
    def test_rows_unpacked_with_aliases(self) -> None:
        class _FakeCursor:
            def execute(self, sql: str, *a: object) -> None:
                assert "ig_node" in sql and "已并入" in sql  # 口径：剔墓碑 SQL 下推
                self._sql = sql

            def fetchall(self) -> list[tuple[str, str, str, str, list[str] | None]]:
                return [("ND-1", "CH-1", "半导体材料", "上游", ["SiC"])]

        class _FakeConn:
            def cursor(self) -> _FakeCursor:
                return _FakeCursor()

            def close(self) -> None:
                pass

        lk = ChainNodeLinker.from_pg(lambda: _FakeConn())
        assert lk.vocab_size() == 2  # name + alias 各一词
        assert len(lk.link("sic")) == 1  # alias 归一化（大写）命中
