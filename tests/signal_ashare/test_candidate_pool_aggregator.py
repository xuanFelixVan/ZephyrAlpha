# [BLUEPRINT] MOD-SIG-038 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""candidate_pool_aggregator 单元测试（L3-08 汇总件施工批 2026-09-11，Owner 立项）。

红蓝手法覆盖：红-边界（空来源/容量端点 10-20/tie-break 链）/红-契约（完全重复对
fail-closed/未知 sleeve/非有限分数）/红-前视（无墙钟，as_of 仅透传）/红-竞态
（frozen+确定序输出）/红-容灾（空来源 fail-open、否决留痕不丢）。

任务真源：TDM-E-L3-08 algo_note（双池合流+策略链候选+顺位排序+否决后清单=
最终候选池 10-20 只，带各自 sleeve 标签与顺位分，喂 L4 买卖点层）。
"""

from __future__ import annotations

import json

import pytest

from zephyr.signal_ashare.core.candidate_pool_aggregator import (
    DEFAULT_MAX_SIZE,
    DEFAULT_MIN_SIZE,
    SLEEVE_ORDER,
    CandidatePoolConfig,
    CandidatePoolInputError,
    FinalCandidatePool,
    FinalPoolEntry,
    PoolCandidateInput,
    SleeveKind,
    VetoMark,
    aggregate_candidate_pool,
)


def _c(
    symbol: str,
    sleeve: str | SleeveKind,
    score: float,
    rank: int | None = None,
) -> PoolCandidateInput:
    return PoolCandidateInput(symbol, sleeve, score, rank)


class TestContract:
    def test_capacity_defaults_match_node_truth(self) -> None:
        """节点真源：最终候选池 10-20 只。"""
        assert DEFAULT_MIN_SIZE == 10
        assert DEFAULT_MAX_SIZE == 20
        cfg = CandidatePoolConfig()
        assert cfg.min_size == 10 and cfg.max_size == 20

    def test_capacity_config_violation_fail_closed(self) -> None:
        with pytest.raises(CandidatePoolInputError, match="容量配置越界"):
            CandidatePoolConfig(min_size=25, max_size=20)
        with pytest.raises(CandidatePoolInputError, match="容量配置越界"):
            CandidatePoolConfig(min_size=0, max_size=20)

    def test_sleeve_order_no_priority_semantics(self) -> None:
        """sleeve 定义序仅 tie-break 用（五 sleeve 齐，无优先级语义——文档声明）。"""
        assert len(SLEEVE_ORDER) == 5
        assert [s.value for s in SLEEVE_ORDER] == [
            "short_term",
            "swing",
            "daban",
            "multifactor",
            "event_driven",
        ]


class TestInputValidation:
    def test_unknown_sleeve_fail_closed(self) -> None:
        with pytest.raises(CandidatePoolInputError, match="sleeve 未知"):
            _c("000001", "bogus", 1.0)

    def test_non_finite_score_fail_closed(self) -> None:
        for bad in (float("nan"), float("inf"), float("-inf")):
            with pytest.raises(CandidatePoolInputError, match="非有限"):
                _c("000001", "short_term", bad)

    def test_empty_symbol_fail_closed(self) -> None:
        with pytest.raises(CandidatePoolInputError, match="symbol 为空"):
            _c("", "short_term", 1.0)
        with pytest.raises(CandidatePoolInputError):
            _c("   ", "short_term", 1.0)

    def test_negative_source_rank_fail_closed(self) -> None:
        with pytest.raises(CandidatePoolInputError, match="source_rank 为负"):
            _c("000001", "short_term", 1.0, rank=-1)

    def test_empty_as_of_fail_closed(self) -> None:
        with pytest.raises(CandidatePoolInputError, match="as_of 为空"):
            aggregate_candidate_pool([], [], [], "")

    def test_empty_veto_reason_fail_closed(self) -> None:
        with pytest.raises(CandidatePoolInputError, match="否决原因为空"):
            aggregate_candidate_pool([], [], [VetoMark("000001", ())], "D1")

    def test_exact_duplicate_pair_fail_closed(self) -> None:
        """完全重复 (symbol,sleeve) 对=fail-closed（上游契约违反/同源束劈注入防线）。"""
        with pytest.raises(CandidatePoolInputError, match="完全重复"):
            aggregate_candidate_pool(
                [_c("000001", "short_term", 1.0), _c("000001", "short_term", 2.0)],
                [],
                [],
                "D1",
            )
        # 跨束同 (symbol,sleeve) 对同样 fail-closed（同源束劈参数注入）
        with pytest.raises(CandidatePoolInputError, match="完全重复"):
            aggregate_candidate_pool(
                [_c("000001", "daban", 1.0)],
                [_c("000001", "daban", 2.0)],
                [],
                "D1",
            )


class TestMergeThreeSources:
    def test_three_sources_merge_with_sleeve_labels(self) -> None:
        """三来源合并：双池+策略链候选全部入池，各带 sleeve 标签。"""
        pool = aggregate_candidate_pool(
            dual_pool_candidates=[
                _c("000001", "short_term", 3.0),
                _c("000002", "swing", 2.0),
            ],
            strategy_chain_candidates=[
                _c("300001", "daban", 5.0),
                _c("300002", "multifactor", 1.0),
                _c("300003", "event_driven", 0.5),
            ],
            veto_marks=[],
            as_of="2026-09-11",
        )
        assert pool.actual_size == 5
        sleeves = {e.symbol: e.sleeves for e in pool.entries}
        assert sleeves["000001"] == ("short_term",)
        assert sleeves["300001"] == ("daban",)
        assert sleeves["300003"] == ("event_driven",)
        # 顺位排序：300001(5.0) > 000001(3.0) > 000002(2.0) > 300002(1.0) > 300003(0.5)
        assert [e.symbol for e in pool.entries] == [
            "300001",
            "000001",
            "000002",
            "300002",
            "300003",
        ]

    def test_cross_source_same_symbol_merges_sleeves(self) -> None:
        """跨束同 symbol 异 sleeve=合法合流：sleeves 按定义序合并，best_sleeve=顺位最优来源。"""
        pool = aggregate_candidate_pool(
            dual_pool_candidates=[
                _c("000001", "swing", 2.0, rank=3),
                _c("000001", "short_term", 4.0, rank=1),
            ],
            strategy_chain_candidates=[_c("000001", "daban", 1.0, rank=9)],
            veto_marks=[],
            as_of="D1",
        )
        assert pool.actual_size == 1
        e = pool.entries[0]
        assert e.sleeves == ("short_term", "swing", "daban")
        assert e.best_sleeve == "short_term"
        assert e.rank_score == 4.0
        assert e.source_rank == 1

    def test_same_symbol_across_dual_pool_bundles_merges(self) -> None:
        """双池束内同 symbol 异 sleeve（短线+波段同命中）=合法合流去重。"""
        pool = aggregate_candidate_pool(
            dual_pool_candidates=[
                _c("000001", "short_term", 1.0),
                _c("000001", "swing", 3.0),
            ],
            strategy_chain_candidates=[],
            veto_marks=[],
            as_of="D1",
        )
        assert pool.actual_size == 1
        e = pool.entries[0]
        assert e.sleeves == ("short_term", "swing")
        assert e.best_sleeve == "swing"  # 顺位最优（3.0 > 1.0）


class TestDedupKeepBest:
    def test_dedup_keeps_best_rank_score(self) -> None:
        """同 symbol 三来源命中 → 保留顺位最优分。"""
        pool = aggregate_candidate_pool(
            dual_pool_candidates=[_c("000001", "short_term", 1.5, rank=7)],
            strategy_chain_candidates=[
                _c("000001", "daban", 9.9, rank=1),
                _c("000001", "multifactor", 3.0, rank=5),
            ],
            veto_marks=[],
            as_of="D1",
        )
        assert pool.actual_size == 1
        e = pool.entries[0]
        assert e.rank_score == 9.9
        assert e.best_sleeve == "daban"
        assert e.source_rank == 1
        assert e.sleeves == ("short_term", "daban", "multifactor")

    def test_tie_break_source_rank_then_sleeve_order_then_symbol(self) -> None:
        """tie-break 链：rank_score 平→source_rank 升→sleeve 定义序→symbol 字典序。"""
        # source_rank tie-break：同分 5.0，rank=2 优于 rank=5
        pool = aggregate_candidate_pool(
            dual_pool_candidates=[
                _c("000001", "short_term", 5.0, rank=5),
                _c("000002", "short_term", 5.0, rank=2),
            ],
            strategy_chain_candidates=[],
            veto_marks=[],
            as_of="D1",
        )
        assert [e.symbol for e in pool.entries] == ["000002", "000001"]
        # sleeve 定义序 tie-break：同分同 rank，swing 定义序在 daban 前
        pool2 = aggregate_candidate_pool(
            dual_pool_candidates=[_c("000001", "daban", 5.0, rank=1)],
            strategy_chain_candidates=[_c("000001", "swing", 5.0, rank=1)],
            veto_marks=[],
            as_of="D1",
        )
        assert pool2.entries[0].best_sleeve == "swing"
        assert pool2.entries[0].sleeves == ("swing", "daban")
        # symbol 字典序 tie-break：同分同 rank 同 sleeve
        pool3 = aggregate_candidate_pool(
            dual_pool_candidates=[
                _c("600001", "swing", 5.0),
                _c("000003", "swing", 5.0),
            ],
            strategy_chain_candidates=[],
            veto_marks=[],
            as_of="D1",
        )
        assert [e.symbol for e in pool3.entries] == ["000003", "600001"]

    def test_source_rank_none_loses_to_ranked(self) -> None:
        """source_rank=None 视为 +inf：同分下有名次者胜。"""
        pool = aggregate_candidate_pool(
            dual_pool_candidates=[
                _c("000001", "short_term", 5.0, rank=3),
                _c("000002", "short_term", 5.0, rank=None),
            ],
            strategy_chain_candidates=[],
            veto_marks=[],
            as_of="D1",
        )
        assert [e.symbol for e in pool.entries] == ["000001", "000002"]


class TestVetoMarks:
    def test_veto_marked_not_dropped_sinks_to_tail(self) -> None:
        """否决清单不丢只标记：vetoed 条目留在池中沉底，不占容量。"""
        pool = aggregate_candidate_pool(
            dual_pool_candidates=[
                _c("000001", "short_term", 9.0),
                _c("000002", "short_term", 8.0),
                _c("000003", "short_term", 7.0),
            ],
            strategy_chain_candidates=[],
            veto_marks=[VetoMark("000001", ("立案调查",))],
            as_of="D1",
        )
        assert pool.actual_size == 2  # 否决不占容量
        assert [e.symbol for e in pool.entries] == ["000002", "000003", "000001"]
        vetoed = pool.entries[-1]
        assert vetoed.vetoed is True
        assert vetoed.veto_reasons == ("立案调查",)
        assert pool.vetoed_symbols == ("000001",)

    def test_veto_outside_candidates_still_recorded(self) -> None:
        """否决标记不丢：候选束外的否决留痕照常透出（vetoed_symbols）。"""
        pool = aggregate_candidate_pool(
            dual_pool_candidates=[_c("000001", "short_term", 1.0)],
            strategy_chain_candidates=[],
            veto_marks=[
                VetoMark("999999", ("大股东减持公告",)),
                VetoMark("888888", ("业绩暴雷（预告亏损）", "配股圈钱")),
            ],
            as_of="D1",
        )
        assert pool.vetoed_symbols == ("888888", "999999")
        assert pool.actual_size == 1
        assert all(not e.vetoed for e in pool.entries)

    def test_duplicate_veto_marks_merge_reasons(self) -> None:
        """重复否决标记：reasons 合并去重保序（否决记录天然可叠加）。"""
        pool = aggregate_candidate_pool(
            dual_pool_candidates=[_c("000001", "short_term", 1.0)],
            strategy_chain_candidates=[],
            veto_marks=[
                VetoMark("000001", ("立案调查", "商誉减值风险")),
                VetoMark("000001", ("立案调查", "黑名单")),
            ],
            as_of="D1",
        )
        e = pool.entries[0]
        assert e.veto_reasons == ("立案调查", "商誉减值风险", "黑名单")
        assert pool.vetoed_symbols == ("000001",)

    def test_vetoed_full_capacity_overflow(self) -> None:
        """全容量溢出场景：vetoed 全员仍全部留痕（一个不丢）。"""
        cands = [_c(f"{i:06d}", "daban", float(i)) for i in range(30)]
        marks = [VetoMark(f"{i:06d}", ("黑名单",)) for i in range(25, 30)]
        pool = aggregate_candidate_pool(cands, [], marks, "D1")
        assert pool.actual_size == 20
        assert pool.vetoed_symbols == tuple(f"{i:06d}" for i in range(25, 30))
        vetoed_in_pool = [e for e in pool.entries if e.vetoed]
        assert len(vetoed_in_pool) == 5

    def test_vetoed_excluded_from_truncation_accounting(self) -> None:
        """容量截断只数未否决：否决沉底不挤占容量名额。"""
        cands = [_c(f"{i:06d}", "swing", float(100 - i)) for i in range(22)]
        pool = aggregate_candidate_pool(cands, [], [VetoMark("000000", ("立案调查",))], "D1")
        # 22 候选中 1 只否决 → 21 未否决 → 截到 20
        assert pool.actual_size == 20
        assert len(pool.truncated_out) == 1
        assert pool.truncated_out == ("000021",)  # 顺位最末的未否决者（000001..000021 共 21 只，截掉末位）


class TestCapacityTruncation:
    def test_upper_bound_truncates_by_rank(self) -> None:
        """上限截断：25 未否决 → 保留顺位前 20，截断名单按顺位留痕。"""
        cands = [_c(f"{i:06d}", "short_term", float(100 - i)) for i in range(25)]
        pool = aggregate_candidate_pool(cands, [], [], "D1")
        assert pool.actual_size == 20
        assert pool.capacity == 20
        assert [e.symbol for e in pool.entries] == [f"{i:06d}" for i in range(20)]
        assert pool.truncated_out == tuple(f"{i:06d}" for i in range(20, 25))
        assert any("容量截断" in n for n in pool.notes)

    def test_lower_bound_fail_open_no_forcing(self) -> None:
        """下限不足：8 只 < 10 → 全保留不硬凑（fail-open），notes 透出。"""
        cands = [_c(f"{i:06d}", "swing", float(i)) for i in range(8)]
        pool = aggregate_candidate_pool(cands, [], [], "D1")
        assert pool.actual_size == 8
        assert pool.truncated_out == ()
        assert any("不硬凑" in n for n in pool.notes)

    def test_within_band_no_notes(self) -> None:
        """10-20 带内：12 只全保留，无容量 notes。"""
        cands = [_c(f"{i:06d}", "daban", float(i)) for i in range(12)]
        pool = aggregate_candidate_pool(cands, [], [], "D1")
        assert pool.actual_size == 12
        assert not any("容量" in n or "硬凑" in n for n in pool.notes)

    def test_custom_config_respected(self) -> None:
        cfg = CandidatePoolConfig(min_size=2, max_size=3)
        cands = [_c(f"{i:06d}", "multifactor", float(i)) for i in range(5)]
        pool = aggregate_candidate_pool(cands, [], [], "D1", config=cfg)
        assert pool.actual_size == 3
        assert pool.capacity == 3
        assert pool.truncated_out == ("000001", "000000")  # 分数降序 000004 最优，截掉末两位


class TestFailOpenEmptySources:
    def test_all_empty_returns_empty_pool(self) -> None:
        """空来源 fail-open：返回空池不抛异常。"""
        pool = aggregate_candidate_pool([], [], [], "D1")
        assert isinstance(pool, FinalCandidatePool)
        assert pool.entries == ()
        assert pool.actual_size == 0
        assert pool.vetoed_symbols == ()
        assert any("fail-open" in n for n in pool.notes)

    def test_empty_candidates_with_veto_marks_keeps_veto_trace(self) -> None:
        """空候选+否决标记：空池但否决留痕不丢。"""
        pool = aggregate_candidate_pool([], [], [VetoMark("000001", ("黑名单",))], "D1")
        assert pool.entries == ()
        assert pool.actual_size == 0
        assert pool.vetoed_symbols == ("000001",)
        assert any("留痕" in n for n in pool.notes)

    def test_none_iterables_equivalent_to_empty(self) -> None:
        """空元组/空列表/生成器空流一致 fail-open。"""
        p1 = aggregate_candidate_pool((), (), (), "D1")
        p2 = aggregate_candidate_pool([], [], (_ for _ in ()), "D1")
        assert p1 == p2


class TestOrderingAndPurity:
    def test_final_order_qualified_desc_then_vetoed(self) -> None:
        """最终排序：未否决按顺位分降序在前，vetoed 沉底（内部仍按顺位确定序）。"""
        cands = [
            _c("A1", "short_term", 5.0),
            _c("B2", "swing", 9.0),
            _c("C3", "daban", 1.0),
            _c("D4", "multifactor", 7.0),
        ]
        pool = aggregate_candidate_pool(cands, [], [VetoMark("A1", ("黑名单",))], "D1")
        assert [e.symbol for e in pool.entries] == ["B2", "D4", "C3", "A1"]

    def test_determinism_same_input_same_output(self) -> None:
        """同输入必同输出（红-竞态：乱序注入+生成器输入，frozen+确定序）。"""
        cands1 = [_c(f"{i:06d}", "short_term", float(i % 7)) for i in range(15)]
        import random

        cands2 = cands1.copy()
        random.Random(42).shuffle(cands2)
        marks = [VetoMark("000003", ("立案调查",))]
        p1 = aggregate_candidate_pool(iter(cands1), iter([]), iter(marks), "D1")
        p2 = aggregate_candidate_pool(iter(cands2), iter([]), iter(marks), "D1")
        assert p1 == p2

    def test_frozen_output(self) -> None:
        """输出 frozen：条目与池均不可变（红-竞态）。"""
        pool = aggregate_candidate_pool([_c("000001", "short_term", 1.0)], [], [], "D1")
        with pytest.raises(Exception):
            pool.entries[0].rank_score = 99.0  # type: ignore[misc]
        with pytest.raises(Exception):
            pool.as_of = "hacked"  # type: ignore[misc]

    def test_no_wall_clock_as_of_passthrough(self) -> None:
        """无墙钟：as_of 仅审计透传，不影响任何判定。"""
        cands = [_c("000001", "short_term", 1.0)]
        p1 = aggregate_candidate_pool(cands, [], [], "2099-01-01")
        p2 = aggregate_candidate_pool(cands, [], [], "1999-12-31")
        assert p1.entries == p2.entries
        assert p1.as_of == "2099-01-01" and p2.as_of == "1999-12-31"

    def test_tier_slot_reserved_none(self) -> None:
        """Tier 槽位仅预留：本件一律 None，分层归 TDM-E-L3-09。"""
        pool = aggregate_candidate_pool(
            [_c("000001", "short_term", 1.0)], [], [], "D1"
        )
        assert all(e.tier_slot is None for e in pool.entries)


class TestSerialization:
    def test_to_dict_round_trip(self) -> None:
        """to_dict 全基本类型（json.dumps 直序列化）。"""
        pool = aggregate_candidate_pool(
            dual_pool_candidates=[_c("000001", "short_term", 3.0, rank=1)],
            strategy_chain_candidates=[_c("000001", "daban", 1.0, rank=5)],
            veto_marks=[VetoMark("000002", ("黑名单",))],
            as_of="D1",
        )
        d = pool.to_dict()
        json.dumps(d, ensure_ascii=False)  # 不抛即通过
        assert d["actual_size"] == 1
        assert d["vetoed_symbols"] == ["000002"]
        e0 = d["entries"][0]
        assert e0["sleeves"] == ["short_term", "daban"]
        assert e0["best_sleeve"] == "short_term"
        assert e0["tier_slot"] is None


class TestMirrorHelpers:
    def test_from_fine_scored_entry_mapping(self) -> None:
        """ScoredEntry 姿态镜像（symbol/z_score/rank → symbol/rank_score/source_rank）。"""

        class _FakeEntry:
            symbol = "600001"
            z_score = 1.7
            rank = 4

        c = PoolCandidateInput.from_fine_scored_entry(_FakeEntry(), SleeveKind.SHORT_TERM)
        assert c.symbol == "600001"
        assert c.rank_score == 1.7
        assert c.source_rank == 4
        assert c.sleeve == "short_term"

    def test_from_mirror_generic_mapping(self) -> None:
        """通用鸭型镜像：任意带属性对象 + 指定字段名。"""

        class _ChainPick:
            code = "300001"
            final_score = 0.83
            order = 2

        c = PoolCandidateInput.from_mirror(
            _ChainPick(), "daban", score_attr="final_score", rank_attr="order", symbol_attr="code"
        )
        assert c.symbol == "300001"
        assert c.rank_score == 0.83
        assert c.source_rank == 2

    def test_from_veto_verdict_mapping(self) -> None:
        """NegativeVetoVerdict 姿态转换：vetoed=True → VetoMark；False → None。"""

        class _Verdict:
            def __init__(self, vetoed: bool, reasons: tuple[str, ...]) -> None:
                self.vetoed = vetoed
                self.reasons = reasons

        assert VetoMark.from_veto_verdict(_Verdict(False, ()), "000001") is None
        m = VetoMark.from_veto_verdict(_Verdict(True, ("立案调查", "黑名单")), "000001")
        assert m is not None
        assert m.symbol == "000001"
        assert m.reasons == ("立案调查", "黑名单")
