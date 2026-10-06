# [BLUEPRINT] MOD-PA-030 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] tests.pf_alloc.test_sleeve_provenance
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] pytest; zephyr.pf_alloc.allocation_inputs; zephyr.pf_alloc.allocation_orchestrator; schemas.categories.alloc_budget_daily
# [CONSUMERS] FAC-E8 sleeve 语义落库守卫（PP-001 plan/条目/相位三件套贯通到 alloc_budget_daily 行）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 命中 PP-001 的策略行必带 sleeve 三件套；未命中（补齐/等权）ref 恒空；
#   旧 3 元组 load_pp001_plan 兼容不破；sleeve 模板占位符契约与既有读模板同形
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败即红
# [TESTS] self
# [A_module] module_id=MOD-PA-030-SLV | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E8 sleeve 语义落库测试——PP-001 先验命中面按行落库（JSON 贯通）。

背景：挖矿簿 b2_f27 §四.3——alloc_budget_daily 按 strategy 粒度落行，sleeve 层
（PP-001 条目）落库语义未定义。治本口径：plan_id/sleeve_ref/activation_state 相位
三件套折入 batch_plan_json.sleeve（同 cash_seat 先例，改列=跨域 schema 变更），
读面=SQL_SLEEVE_DAY_SLICE（JSONExtract 子查询聚合）。

测试纪律：TDM 地图用 tmp_path 假件，零触生产配置/库。
"""

# skip 移除（st-circ-a7，2026-10-01）：依赖的 allocation_inputs 新 API
# load_pp001_plan_detail/Pp001PlanDetail/BaseWeightTable.sleeve_phases 已补齐落地
# （a349ddc1fec 分袋断链的丢失半截——orchestrator 读侧 09-28 先落、本侧因勿碰令移出
# 袋外=E8/C1 停摆真断点；本批按 2026-09-28 夜班调度令预留的本行恢复通道复位）。

from __future__ import annotations

import json
from pathlib import Path

import pytest

from schemas.categories.alloc_budget_daily import (
    SQL_DAY_SLICE,
    SQL_SLEEVE_DAY_SLICE,
)
from zephyr.pf_alloc.allocation_config import AllocationConfig
from zephyr.pf_alloc.allocation_inputs import (
    SOURCE_EQUAL,
    SOURCE_PP001,
    BaseWeightTable,
    build_base_weights,
    load_pp001_plan,
    load_pp001_plan_detail,
)
from zephyr.pf_alloc.allocation_orchestrator import StrategyAllocation

_TDM_YAML = """
portfolio_plan:
  plan_id: PP-TEST-1
  sleeves:
  - {strategy_ref: STR-AAA-001, weight: 0.30, activation_state: [ignition, expansion]}
  - {strategy_ref: multifactor-sleeve, weight: 0.20, activation_state: null}
  aggregator: {max_single_sleeve: 0.25}
"""


def _make_config(tmp_path: Path) -> AllocationConfig:
    tdm = tmp_path / "tdm.yaml"
    tdm.write_text(_TDM_YAML, encoding="utf-8")
    return AllocationConfig(tdm_path=str(tdm))


class TestLoadPp001PlanDetail:
    def test_parses_phases_and_legacy_tuple(self, tmp_path):
        cfg = _make_config(tmp_path)
        detail = load_pp001_plan_detail(cfg.tdm_full_path)
        assert detail.plan_id == "PP-TEST-1"
        assert detail.sleeve_phases["STR-AAA-001"] == ("ignition", "expansion")
        assert "multifactor-sleeve" not in detail.sleeve_phases  # null 相位=空表不落键
        # 旧 3 元组消费方（plan_engine.daily_loop_master_switch）兼容
        weights, aggregator, plan_id = load_pp001_plan(cfg.tdm_full_path)
        assert plan_id == "PP-TEST-1"
        assert weights["STR-AAA-001"] == 0.30
        assert aggregator["max_single_sleeve"] == 0.25

    def test_missing_file_returns_empty_detail(self, tmp_path):
        detail = load_pp001_plan_detail(tmp_path / "nope.yaml")
        assert detail.weights == {} and detail.plan_id == "" and detail.sleeve_phases == {}


class TestBuildBaseWeightsProvenance:
    def test_matched_sid_carries_phases(self, tmp_path):
        table = build_base_weights(["STR-AAA-001", "STR-XXX-999"], _make_config(tmp_path))
        assert table.sources["STR-AAA-001"] == SOURCE_PP001
        assert table.sleeve_phases["STR-AAA-001"] == ("ignition", "expansion")
        assert table.sources["STR-XXX-999"] in (SOURCE_PP001, "pp001_mean_prior_fill", SOURCE_EQUAL)
        assert table.sleeve_phases.get("STR-XXX-999", ()) == ()

    def test_default_table_has_empty_phases(self):
        """存量直接构造（tests/pf_alloc/test_allocation_chain 先例）零破坏。"""
        table = BaseWeightTable(weights={"S1": 1.0}, sources={"S1": "test"})
        assert table.sleeve_phases == {}


def _allocation(
    sid: str, *, source: str, plan_id: str = "", ref: str = "", phases: tuple[str, ...] = ()
) -> StrategyAllocation:
    return StrategyAllocation(
        strategy_id=sid,
        strategy_type="多因子",
        base_weight=0.5,
        base_weight_source=source,
        perf_score=1.0,
        perf_sample_days=30,
        allocation=0.5,
        global_shrinkage=1.0,
        cold_start_ratio=1.0,
        effective_budget=0.5,
        previous_budget=0.5,
        allocated_capital=5000.0,
        final_weight=0.5,
        budget_action="NO_ACTION",
        current_tier="idle",
        freeze_new_positions=False,
        retain_ratio=None,
        adjudication_ids=(),
        symbols=(),
        sleeve_plan_id=plan_id,
        sleeve_ref=ref,
        sleeve_phases=phases,
    )


class TestRowFold:
    def test_matched_row_folds_sleeve_block(self):
        row = _allocation(
            "STR-AAA-001",
            source=SOURCE_PP001,
            plan_id="PP-TEST-1",
            ref="STR-AAA-001",
            phases=("ignition", "expansion"),
        ).to_row("run-x", "2026-09-27")
        sleeve = json.loads(row["batch_plan_json"])["sleeve"]
        assert sleeve == {"plan_id": "PP-TEST-1", "ref": "STR-AAA-001", "phases": ["ignition", "expansion"]}

    def test_unmatched_row_keeps_empty_ref(self):
        row = _allocation("STR-XXX-999", source="pp001_mean_prior_fill").to_row("run-x", "2026-09-27")
        sleeve = json.loads(row["batch_plan_json"])["sleeve"]
        assert sleeve == {"plan_id": "", "ref": "", "phases": []}


class TestSleeveReadTemplate:
    def test_template_shape_and_placeholders(self):
        assert "{table}" in SQL_SLEEVE_DAY_SLICE and "{date}" in SQL_SLEEVE_DAY_SLICE
        assert "JSONExtractString(batch_plan_json, 'sleeve', 'plan_id')" in SQL_SLEEVE_DAY_SLICE
        assert "LIMIT 1 BY strategy_id" in SQL_SLEEVE_DAY_SLICE  # 最近 run 判据与 DAY_SLICE 同形
        assert "{table}" in SQL_DAY_SLICE  # 既有模板未被本批改动破坏
