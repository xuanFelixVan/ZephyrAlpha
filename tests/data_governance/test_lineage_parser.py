# [BLUEPRINT] MOD-DATA_GOV-004 | docs/03_modules/_domain_data_governance/lineage_parser/blueprint.md | §test
# [MODULE] tests.data_governance.test_lineage_parser
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES] zephyr.data_governance.core.lineage_parser
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_lineage_parser.py
# [A_test] module_id: MOD-DATA_GOV-004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-DATA_GOV-004 单元测试: M8-S01 血缘解析器。

覆盖: CTR 契约双向边抽取（produces/consumed_by）与畸形 Fail-Closed、模块头
[MODULE]/[DEPENDENCIES]/[CONSUMERS] 三注解解析（外部依赖略过记 skipped）、
批内去重首条胜出、tracker 幂等重加计 updated、环拒记不中断、空节点名
Fail-Closed、端到端 解析→入图→上下游查询。
"""

from __future__ import annotations

import pytest

from zephyr.data_governance.core.lineage_parser import (
    LineageParseError,
    edges_of_annotations,
    ingest_into_tracker,
    parse_ctr_contract,
    parse_module_header,
)
from zephyr.data_governance.core.lineage_tracker import LineageTracker

_CTR_002 = {
    "id": "CTR-002",
    "name": "FactorSignal / 因子信号",
    "source_domain": "D_FACTOR",
    "target_domains": ["D_ASHARE_SIGNAL", "D_RISK", "D_PF_CORE", "D_BACKTEST"],
}

_HEADER = """\
# [BLUEPRINT] MOD-X-001 | docs/x.md
# [MODULE] zephyr.factor.core.momentum
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry; numpy
# [CONSUMERS] MOD-SIG-024(intraday_buy_sell_point_analyzer 消费因子值); 运行时装配批
# [STARTUP] imported
"""


class TestCtrContractParse:
    def test_bidirectional_edges(self):
        edges = parse_ctr_contract(_CTR_002)
        assert ("D_FACTOR", "CTR-002", "produces") in [(e.source, e.target, e.transformation) for e in edges]
        consumed = {(e.target, e.transformation) for e in edges if e.source == "CTR-002"}
        assert consumed == {
            ("D_ASHARE_SIGNAL", "consumed_by"),
            ("D_RISK", "consumed_by"),
            ("D_PF_CORE", "consumed_by"),
            ("D_BACKTEST", "consumed_by"),
        }
        assert len(edges) == 5

    def test_no_target_domains_only_produces(self):
        edges = parse_ctr_contract({"id": "CTR-009", "source_domain": "D_X"})
        assert len(edges) == 1
        assert edges[0].transformation == "produces"

    def test_missing_id_fail_closed(self):
        with pytest.raises(LineageParseError):
            parse_ctr_contract({"source_domain": "D_FACTOR"})

    def test_missing_source_domain_fail_closed(self):
        with pytest.raises(LineageParseError):
            parse_ctr_contract({"id": "CTR-002"})

    def test_target_domains_not_list_fail_closed(self):
        with pytest.raises(LineageParseError):
            parse_ctr_contract({"id": "CTR-002", "source_domain": "D_FACTOR", "target_domains": "D_RISK"})


class TestModuleHeaderParse:
    def test_three_annotations(self):
        ann = parse_module_header(_HEADER)
        assert ann.module == "zephyr.factor.core.momentum"
        assert ann.dependencies == ("zephyr.data.ch_reader", "zephyr.data.table_registry")
        assert ann.skipped_external == ("numpy",)
        assert ann.consumers == ("intraday_buy_sell_point_analyzer",)

    def test_edges_of_annotations(self):
        ann = parse_module_header(_HEADER)
        edges = edges_of_annotations(ann)
        triples = {(e.source, e.target, e.transformation) for e in edges}
        assert (
            "zephyr.data.ch_reader",
            "zephyr.factor.core.momentum",
            "imports",
        ) in triples
        assert (
            "zephyr.factor.core.momentum",
            "intraday_buy_sell_point_analyzer",
            "consumed_by",
        ) in triples
        assert len(edges) == 3  # numpy 外部依赖不成边

    def test_missing_module_annotation_fail_closed(self):
        with pytest.raises(LineageParseError):
            parse_module_header("# [DEPENDENCIES] zephyr.a.b\n")

    def test_empty_annotations(self):
        ann = parse_module_header("# [MODULE] zephyr.x.y\n# [DEPENDENCIES]\n# [CONSUMERS]\n")
        assert ann.module == "zephyr.x.y"
        assert ann.dependencies == ()
        assert ann.consumers == ()
        assert edges_of_annotations(ann) == []

    def test_mod_id_only_consumer_entry(self):
        ann = parse_module_header("# [MODULE] zephyr.a.b\n# [CONSUMERS] MOD-REGIME-002\n")
        assert ann.consumers == ("MOD-REGIME-002",)


class TestIngest:
    def test_add_and_query(self):
        tracker = LineageTracker()
        edges = parse_ctr_contract(_CTR_002)
        report = ingest_into_tracker(edges, tracker)
        assert report.added == 5
        assert report.updated == 0
        assert report.rejected == ()
        assert report.skipped == 0
        assert "CTR-002" in tracker.get_downstream("D_FACTOR")
        assert "D_FACTOR" in tracker.get_upstream("D_RISK")

    def test_idempotent_readd_counts_updated(self):
        tracker = LineageTracker()
        edges = parse_ctr_contract(_CTR_002)
        ingest_into_tracker(edges, tracker)
        report = ingest_into_tracker(edges, tracker)
        assert report.added == 0
        assert report.updated == 5  # 幂等重加（首条语义保留）

    def test_batch_dedup_first_wins(self):
        tracker = LineageTracker()
        e1 = parse_ctr_contract(_CTR_002)
        e2 = parse_ctr_contract({"id": "CTR-002", "source_domain": "D_FACTOR", "target_domains": ["D_RISK"]})
        report = ingest_into_tracker([*e1, *e2], tracker)
        # e2 的 (D_FACTOR→CTR-002) 与 (CTR-002→D_RISK) 与 e1 重复 → 批内去重
        assert report.skipped == 2
        assert report.added == 5

    def test_cycle_rejected_not_blocking(self):
        tracker = LineageTracker()
        tracker.add_edge("a", "b", "imports")
        edges = parse_ctr_contract({"id": "x", "source_domain": "b", "target_domains": ["a", "c"]})
        # b→x 合法；x→a 会形成 a→b→x→a? 不——a→b→x + x→a 成环（a 是 x 上游？）
        # 实际：已有 a→b；加 b→x；加 x→a → a→b→x→a 环 → rejected
        report = ingest_into_tracker(edges, tracker)
        assert report.added == 2  # b→x 与 x→c 入图
        assert len(report.rejected) == 1
        assert report.rejected[0][0] == "x"
        assert report.rejected[0][1] == "a"
        assert "c" in tracker.get_downstream("x")

    def test_empty_node_name_fail_closed(self):
        tracker = LineageTracker()
        with pytest.raises(LineageParseError):
            parse_ctr_contract({"id": "  ", "source_domain": "D_FACTOR"})

    def test_report_sources_label(self):
        tracker = LineageTracker()
        report = ingest_into_tracker(parse_ctr_contract(_CTR_002), tracker, sources=("cross_layer_contracts.yaml",))
        assert report.sources == ("cross_layer_contracts.yaml",)


class TestEndToEnd:
    def test_header_to_tracker(self):
        tracker = LineageTracker()
        ann = parse_module_header(_HEADER)
        report = ingest_into_tracker(edges_of_annotations(ann), tracker)
        assert report.added == 3
        assert set(tracker.get_direct_upstream("zephyr.factor.core.momentum")) == {
            "zephyr.data.ch_reader",
            "zephyr.data.table_registry",
        }
        assert "intraday_buy_sell_point_analyzer" in tracker.get_downstream("zephyr.factor.core.momentum")
