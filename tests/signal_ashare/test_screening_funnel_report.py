# [A_test] module_id: MOD-SIG-067 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-067 | 待统筹登记 | 缺口总账 GAP-F-11 + 21号 memo §3.6
# [MODULE] tests.signal_ashare.test_screening_funnel_report
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""ScreeningFunnelReport (MOD-SIG-067) 施工验证测试。

覆盖：
- 四层适配器：046（kept/excluded）/047（truncated 透传）/048（Top-N，入数由
  调用方给）/049（skipped 直通透传）→ FunnelStageStat 计数+排除原因分桶。
- 排除原因分桶："dim:volume_ratio(1.20<=1.5)"→"dim:volume_ratio" 桶计数。
- 全链报告：chain=[universe]+各层 out_count；非单调留痕 note；降级层透传。
- L5/L6 扩展位：inject 自定义 stage（组合/风控层、作战池层）链到 L6。
- 契约：to_dict JSON 可序列化；非法 in_count fail-closed；空 stages 合法空链。
全程内存构造（直接 new 四层 Result），无 DB 无 CH。
"""

from __future__ import annotations

import json

import pytest

from zephyr.signal_ashare.coarse_screening_funnel import CoarseScreenResult
from zephyr.signal_ashare.event_driven_screener import EventScreenResult
from zephyr.signal_ashare.fine_scoring_engine import FineScoreResult, ScoredEntry
from zephyr.signal_ashare.screening_funnel_report import (
    FunnelStageStat,
    ScreeningFunnelReport,
    build_funnel_report,
    stage_from_coarse,
    stage_from_event,
    stage_from_fine,
    stage_from_tiered,
)
from zephyr.signal_ashare.tiered_screening_filter import TieredFilterResult

TRADE_DATE = "2026-08-24"


def _tiered() -> TieredFilterResult:
    return TieredFilterResult(
        kept=tuple(f"6000{i:02d}.SH" for i in range(10)),
        excluded={
            "600100.SH": "physical:limit_locked",
            "600101.SH": "physical:suspended",
            "600102.SH": "gate:new_stock(12d<30d)",
            "600103.SH": "tier:low_amount",
        },
    )


def _coarse(truncated: bool = False) -> CoarseScreenResult:
    return CoarseScreenResult(
        kept=tuple(f"6000{i:02d}.SH" for i in range(6)),
        excluded={
            "600010.SH": "dim:volume_ratio(1.20<=1.5)",
            "600011.SH": "dim:volume_ratio(0.80<=1.5)",
            "600012.SH": "dim:sector_rank",
        },
        truncated=truncated,
    )


def _fine() -> FineScoreResult:
    return FineScoreResult(
        top=tuple(
            ScoredEntry(symbol=f"6000{i:02d}.SH", raw_score=80.0 - i, z_score=1.0 - i * 0.1, rank=i + 1)
            for i in range(4)
        ),
    )


def _event(skipped: bool = False) -> EventScreenResult:
    return EventScreenResult(
        kept=tuple(f"6000{i:02d}.SH" for i in range(3)),
        excluded={"600000.SH": "event:negative"},
        weights={},
        skipped=skipped,
    )


# ── 适配器 ──


def test_stage_from_tiered_counts_and_buckets() -> None:
    stage = stage_from_tiered(_tiered(), in_count=14)
    assert stage.stage_id == "L1"
    assert stage.in_count == 14
    assert stage.out_count == 10
    assert stage.excluded_reasons == {
        "physical:limit_locked": 1,
        "physical:suspended": 1,
        "gate:new_stock": 1,
        "tier:low_amount": 1,
    }


def test_stage_from_tiered_in_count_inferred() -> None:
    stage = stage_from_tiered(_tiered())
    assert stage.in_count == 14  # len(kept)+len(excluded)


def test_stage_from_coarse_truncated_passthrough() -> None:
    stage = stage_from_coarse(_coarse(truncated=True))
    assert stage.truncated is True
    assert stage.out_count == 6
    # volume_ratio 两条参数化原因归一桶
    assert stage.excluded_reasons["dim:volume_ratio"] == 2


def test_stage_from_fine_requires_in_count() -> None:
    with pytest.raises(ValueError):
        stage_from_fine(_fine())
    stage = stage_from_fine(_fine(), in_count=6)
    assert stage.out_count == 4
    assert stage.excluded_reasons == {"rank:below_top_n": 2}  # Top-N 截断语义桶


def test_stage_from_event_skipped_passthrough() -> None:
    stage = stage_from_event(_event(skipped=True))
    assert stage.skipped is True
    assert stage.out_count == 3


def test_stage_in_count_negative_fail_closed() -> None:
    with pytest.raises(ValueError):
        stage_from_tiered(_tiered(), in_count=-1)


def test_stage_out_exceeds_in_note() -> None:
    stage = stage_from_tiered(_tiered(), in_count=5)
    assert stage.out_count == 10
    assert any("出>入" in n or "in_count" in n for n in stage.notes)


# ── 全链报告 ──


def test_build_full_chain() -> None:
    stages = [
        stage_from_tiered(_tiered(), in_count=3412),
        stage_from_coarse(_coarse()),
        stage_from_fine(_fine(), in_count=6),
        stage_from_event(_event()),
    ]
    report = build_funnel_report(TRADE_DATE, stages, universe_count=3412)
    assert report.chain == (3412, 10, 6, 4, 3)
    assert [s.stage_id for s in report.stages] == ["L1", "L2", "L3", "L4"]
    assert report.trade_date == TRADE_DATE


def test_extension_slots_l5_l6() -> None:
    # L5/L6 扩展位：组合/风控层 + 作战池层（GAP-F-06 产出）以自定义 stage 注入
    stages = [
        stage_from_event(_event()),
        FunnelStageStat(stage_id="L5", name_zh="组合风控层", in_count=3, out_count=2),
        FunnelStageStat(stage_id="L6", name_zh="作战池", in_count=2, out_count=2),
    ]
    report = build_funnel_report(TRADE_DATE, stages)
    assert report.chain == (3, 2, 2)
    assert report.stages[-1].stage_id == "L6"


def test_non_monotonic_chain_note() -> None:
    stages = [
        FunnelStageStat(stage_id="L1", name_zh="x", in_count=10, out_count=5),
        FunnelStageStat(stage_id="L2", name_zh="y", in_count=5, out_count=8),
    ]
    report = build_funnel_report(TRADE_DATE, stages)
    assert any("非单调" in n for n in report.notes)


def test_empty_stages_legal() -> None:
    report = build_funnel_report(TRADE_DATE, [])
    assert report.chain == ()
    assert report.stages == ()


def test_trade_date_invalid() -> None:
    with pytest.raises(ValueError):
        build_funnel_report("2026/08/24", [])


def test_degraded_passthrough() -> None:
    degraded_tiered = TieredFilterResult(kept=("600000.SH",), degraded=True)
    stage = stage_from_tiered(degraded_tiered, in_count=1)
    assert stage.degraded is True


def test_to_dict_json_serializable() -> None:
    stages = [
        stage_from_tiered(_tiered(), in_count=3412),
        stage_from_coarse(_coarse()),
        stage_from_fine(_fine(), in_count=6),
        stage_from_event(_event()),
    ]
    report = build_funnel_report(TRADE_DATE, stages, universe_count=3412)
    payload = report.to_dict()
    json.dumps(payload, ensure_ascii=False)
    assert payload["chain"] == [3412, 10, 6, 4, 3]
    assert payload["stages"][0]["stage_id"] == "L1"
    assert isinstance(report, ScreeningFunnelReport)
    pass_rates = [s["pass_rate"] for s in payload["stages"]]
    assert pass_rates[0] == pytest.approx(10 / 3412, rel=1e-3)
