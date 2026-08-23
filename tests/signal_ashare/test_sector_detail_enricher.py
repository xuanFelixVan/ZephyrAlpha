# [BLUEPRINT] MOD-SIG-081 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-17 行 + GAP-F-D1 核查）
# [MODULE] tests.signal_ashare.test_sector_detail_enricher
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.sector_detail_enricher
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=周期定位状态机/拉升原因聚合逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-SIG-081_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIG-081 板块详情补充维度 单元测试（GAP-F-17，合成数据不触库）。

覆盖：周期五态封闭（蛰伏/启动/发酵/高潮/退潮）+ 高潮次日转退潮状态机平滑、
拉升原因四类封闭（政策催化/业绩驱动/题材联动/资金推动）+ 无明确原因兜底、
业绩证据超窗留痕（analyst_forecast 约 1 个月覆盖窗，GAP-F-D1 实证）、
证据样本截断、输入校验 fail-closed、JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from zephyr.signal_ashare.sector_detail_enricher import (
    PHASE_CLIMAX,
    PHASE_DORMANT,
    PHASE_FERMENT,
    PHASE_RETREAT,
    PHASE_START,
    REASON_EARNINGS,
    REASON_FUND_FLOW,
    REASON_NONE,
    REASON_POLICY,
    REASON_THEME,
    EarningsEvidence,
    NewsItemInput,
    SectorDetailConfig,
    SectorMetricsInput,
    aggregate_rally_reasons,
    enrich_sector_detail,
    locate_cycle_phase,
)


def _cfg(**kw) -> SectorDetailConfig:
    return SectorDetailConfig(**kw)


def _metrics(**kw) -> SectorMetricsInput:
    base = dict(
        sector_code="881319.SH", sector_name="半导体",
        day_ret_pct=2.5, limit_up_count=2, amount_deviation_pct=40.0,
    )
    base.update(kw)
    return SectorMetricsInput(**base)


NEWS = [
    NewsItemInput(news_id="n1", title="工信部发布半导体产业扶持政策", content="鼓励晶圆制造", publish_time="2026-08-21 10:00"),
    NewsItemInput(news_id="n2", title="多家半导体公司业绩预告大增", content="净利润预增", publish_time="2026-08-21 12:00"),
    NewsItemInput(news_id="n3", title="大盘综述", content="两市成交平稳", publish_time="2026-08-21 15:00"),
]


# ------------------------------------------------------------------
# 周期定位状态机
# ------------------------------------------------------------------


def test_phase_climax_by_limit_count() -> None:
    out = locate_cycle_phase(_metrics(limit_up_count=6, day_ret_pct=4.0), config=_cfg())
    assert out.phase == PHASE_CLIMAX


def test_phase_climax_by_ret_and_count() -> None:
    out = locate_cycle_phase(_metrics(limit_up_count=3, day_ret_pct=5.5), config=_cfg())
    assert out.phase == PHASE_CLIMAX


def test_phase_ferment() -> None:
    out = locate_cycle_phase(_metrics(limit_up_count=2, day_ret_pct=2.5, amount_deviation_pct=40.0), config=_cfg())
    assert out.phase == PHASE_FERMENT


def test_phase_start() -> None:
    out = locate_cycle_phase(_metrics(limit_up_count=1, day_ret_pct=1.2, amount_deviation_pct=10.0), config=_cfg())
    assert out.phase == PHASE_START


def test_phase_retreat_after_climax() -> None:
    out = locate_cycle_phase(
        _metrics(limit_up_count=0, day_ret_pct=-1.0, amount_deviation_pct=-10.0),
        prev_phase=PHASE_CLIMAX, config=_cfg(),
    )
    assert out.phase == PHASE_RETREAT
    assert any("高潮" in e or "退潮" in e for e in out.evidence)


def test_phase_dormant_default() -> None:
    out = locate_cycle_phase(
        _metrics(limit_up_count=0, day_ret_pct=0.1, amount_deviation_pct=-5.0), config=_cfg()
    )
    assert out.phase == PHASE_DORMANT


def test_phase_retreat_requires_prev_or_zero_limit() -> None:
    # 无 prev 且有涨停，但跌幅超阈 → 退潮（limit_up_count=0 条件）
    out = locate_cycle_phase(
        _metrics(limit_up_count=0, day_ret_pct=-2.0, amount_deviation_pct=-20.0), config=_cfg()
    )
    assert out.phase == PHASE_RETREAT
    # 有涨停时跌 → 不直接退潮（高位分歧归 DORMANT，MVP 不出第六态）
    out2 = locate_cycle_phase(
        _metrics(limit_up_count=1, day_ret_pct=-2.0, amount_deviation_pct=-20.0), config=_cfg()
    )
    assert out2.phase == PHASE_DORMANT


def test_phase_evidence_attached() -> None:
    out = locate_cycle_phase(_metrics(), config=_cfg())
    assert out.evidence  # 证据非空留痕


def test_phase_invalid_metrics_fail_closed() -> None:
    with pytest.raises(ValueError, match="metrics 非法"):
        locate_cycle_phase("x", config=_cfg())  # type: ignore[arg-type]


# ------------------------------------------------------------------
# 拉升原因聚合器
# ------------------------------------------------------------------


def test_reasons_policy_and_earnings_and_theme() -> None:
    out = aggregate_rally_reasons(
        sector_name="半导体", news_items=NEWS,
        earnings=None, metrics=_metrics(), config=_cfg(),
    )
    kinds = [r.reason for r in out.reasons]
    assert REASON_POLICY in kinds  # n1 工信部+扶持政策
    assert REASON_EARNINGS in kinds  # n2 业绩预告+预增
    # 政策命中样本留痕
    policy = next(r for r in out.reasons if r.reason == REASON_POLICY)
    assert "n1" in policy.sample_news_ids


def test_reason_fund_flow_when_no_news_and_volume_spike() -> None:
    out = aggregate_rally_reasons(
        sector_name="半导体", news_items=[NEWS[2]],  # 无命中新闻
        earnings=None, metrics=_metrics(amount_deviation_pct=80.0), config=_cfg(),
    )
    kinds = [r.reason for r in out.reasons]
    assert REASON_FUND_FLOW in kinds


def test_reason_none_when_no_evidence() -> None:
    out = aggregate_rally_reasons(
        sector_name="半导体", news_items=[NEWS[2]],
        earnings=None, metrics=_metrics(amount_deviation_pct=5.0), config=_cfg(),
    )
    assert [r.reason for r in out.reasons] == [REASON_NONE]


def test_theme_reason_via_theme_keywords() -> None:
    news = [NewsItemInput(news_id="n9", title="光刻机国产化突破", content="晶圆厂扩产", publish_time="2026-08-21 09:00")]
    out = aggregate_rally_reasons(
        sector_name="半导体", news_items=news, earnings=None,
        metrics=_metrics(amount_deviation_pct=5.0), config=_cfg(),
    )
    kinds = [r.reason for r in out.reasons]
    assert REASON_THEME in kinds


def test_earnings_stale_window_note() -> None:
    earnings = EarningsEvidence(latest_date="2026-07-01", summary="板块 12 家预增")
    out = aggregate_rally_reasons(
        sector_name="半导体", news_items=[], earnings=earnings,
        metrics=_metrics(), config=_cfg(earnings_stale_days=35), as_of="2026-08-21",
    )
    # 超窗 → 业绩原因降级为留痕 note，不作为有效原因
    kinds = [r.reason for r in out.reasons]
    assert REASON_EARNINGS not in kinds
    assert any("覆盖窗" in n or "超窗" in n for n in out.window_notes)


def test_earnings_fresh_counts() -> None:
    earnings = EarningsEvidence(latest_date="2026-08-15", summary="板块 12 家预增")
    out = aggregate_rally_reasons(
        sector_name="半导体", news_items=[], earnings=earnings,
        metrics=_metrics(), config=_cfg(), as_of="2026-08-21",
    )
    kinds = [r.reason for r in out.reasons]
    assert REASON_EARNINGS in kinds


def test_sample_cap() -> None:
    news = [
        NewsItemInput(news_id=f"n{i}", title=f"工信部政策{i}", content="补贴", publish_time="2026-08-21 09:00")
        for i in range(10)
    ]
    out = aggregate_rally_reasons(
        sector_name="半导体", news_items=news, earnings=None,
        metrics=_metrics(), config=_cfg(max_samples_per_reason=3),
    )
    policy = next(r for r in out.reasons if r.reason == REASON_POLICY)
    assert len(policy.sample_news_ids) <= 3
    assert policy.evidence_count == 10


# ------------------------------------------------------------------
# 组合卡
# ------------------------------------------------------------------


def test_enrich_sector_detail_composite() -> None:
    card = enrich_sector_detail(
        metrics=_metrics(), news_items=NEWS, earnings=None,
        prev_phase=None, config=_cfg(), as_of="2026-08-21",
    )
    assert card.sector_code == "881319.SH"
    assert card.cycle_phase in {PHASE_FERMENT, PHASE_CLIMAX, PHASE_START}
    assert card.rally_reasons
    assert card.degraded is False
    json.dumps(asdict(card), ensure_ascii=False)


def test_enrich_invalid_as_of_fail_closed() -> None:
    with pytest.raises(ValueError, match="as_of"):
        enrich_sector_detail(
            metrics=_metrics(), news_items=[], earnings=None,
            prev_phase=None, config=_cfg(), as_of="2026-13-01",
        )
