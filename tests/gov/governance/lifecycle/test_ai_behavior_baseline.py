# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.lifecycle.test_ai_behavior_baseline
# [DOMAIN] D_GOVERNANCE
# [A_module] module_id=MOD-TEST-GOV-AIBEH | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AI 行为基线 + 异常告警单元测试（61 号 §3.6 BM-RC-04-F）。

覆盖:
  - compute_baseline：均值/总体标准差/known_modules 并集；样本不足 fail-closed；负值拒
  - detect_anomalies：正常会话零异常；commit 频率突增 → commit_frequency；
    类型分布偏离 → type_distribution；首次触碰未见模块 → first_touch_module（逐模块）
  - std=0 退化：等于均值零异常，偏离均值即异常（inf z）
  - 边界：duration_hours=0 / 全零文件计数 → 不抛；z_threshold 非法 → 拒
"""

from __future__ import annotations

import pytest

from zephyr.governance.lifecycle_governance.ai_behavior_baseline import (
    BehaviorBaselineError,
    SessionBehavior,
    compute_baseline,
    detect_anomalies,
)


def _sessions(n=5):
    """5 个正常基线会话：commits/hour≈4，docs/code/registry≈5/3/2，模块 m1/m2。"""
    return [
        SessionBehavior(
            session_id=f"hist-{i}",
            commits=8 + (i % 2),
            duration_hours=2.0,
            files_docs=5,
            files_code=3,
            files_registry=2,
            modules_touched=("m1", "m2"),
        )
        for i in range(n)
    ]


class TestComputeBaseline:
    def test_baseline_stats(self):
        b = compute_baseline(_sessions())
        assert b.n_sessions == 5
        assert b.cph_mean == pytest.approx(4.2)
        assert b.cph_std >= 0.0
        assert b.docs_ratio_mean == pytest.approx(0.5)
        assert b.code_ratio_mean == pytest.approx(0.3)
        assert b.registry_ratio_mean == pytest.approx(0.2)
        assert b.known_modules == frozenset({"m1", "m2"})

    def test_min_samples_fail_closed(self):
        with pytest.raises(BehaviorBaselineError):
            compute_baseline(_sessions(2))
        # 边界：恰好 3 个样本 → 可判
        assert compute_baseline(_sessions(3)).n_sessions == 3

    @pytest.mark.parametrize("kw", [{"commits": -1}, {"duration_hours": -0.5}, {"files_docs": -1}])
    def test_negative_values_rejected(self, kw):
        sessions = _sessions() + [SessionBehavior(session_id="bad", **{**dict(commits=1, duration_hours=1.0), **kw})]
        with pytest.raises(BehaviorBaselineError):
            compute_baseline(sessions)


class TestDetectAnomalies:
    def test_normal_session_no_anomaly(self):
        b = compute_baseline(_sessions())
        normal = SessionBehavior(
            session_id="cur",
            commits=8,
            duration_hours=2.0,
            files_docs=5,
            files_code=3,
            files_registry=2,
            modules_touched=("m1",),
        )
        assert detect_anomalies(normal, b) == []

    def test_commit_frequency_burst(self):
        """单会话突增 commit 频率 → commit_frequency 告警。"""
        b = compute_baseline(_sessions())
        burst = SessionBehavior(
            session_id="cur",
            commits=80,
            duration_hours=2.0,  # 40/h vs 基线 4.2/h
            files_docs=5,
            files_code=3,
            files_registry=2,
            modules_touched=("m1",),
        )
        rules = {a.rule for a in detect_anomalies(burst, b)}
        assert "commit_frequency" in rules

    def test_type_distribution_shift(self):
        """类型分布剧变（全注册表修改）→ type_distribution 告警。"""
        b = compute_baseline(_sessions())
        shifted = SessionBehavior(
            session_id="cur",
            commits=8,
            duration_hours=2.0,
            files_docs=0,
            files_code=0,
            files_registry=20,
            modules_touched=("m1",),
        )
        anomalies = detect_anomalies(shifted, b)
        metrics = {a.metric for a in anomalies if a.rule == "type_distribution"}
        assert "registry_ratio" in metrics

    def test_first_touch_module(self):
        """首次触碰基线外模块 → 逐模块告警。"""
        b = compute_baseline(_sessions())
        novel = SessionBehavior(
            session_id="cur",
            commits=8,
            duration_hours=2.0,
            files_docs=5,
            files_code=3,
            files_registry=2,
            modules_touched=("m1", "prod_risk_engine", "prod_order_manager"),
        )
        first_touch = [a for a in detect_anomalies(novel, b) if a.rule == "first_touch_module"]
        assert {a.metric for a in first_touch} == {"prod_risk_engine", "prod_order_manager"}

    def test_std_zero_degenerate(self):
        """退化：基线 std=0（全同会话）——等于均值零异常，偏离即异常。"""
        same = [
            SessionBehavior(
                session_id=f"h{i}", commits=8, duration_hours=2.0, files_docs=5, files_code=3, files_registry=2
            )
            for i in range(4)
        ]
        b = compute_baseline(same)
        assert b.cph_std == 0.0
        assert detect_anomalies(same[0], b) == []
        deviant = SessionBehavior(session_id="d", commits=9, duration_hours=2.0)
        assert any(a.rule == "commit_frequency" for a in detect_anomalies(deviant, b))

    def test_zero_duration_and_files(self):
        """边界：duration_hours=0 / 全零文件计数 → 不抛，比率 0。"""
        b = compute_baseline(_sessions())
        edge = SessionBehavior(session_id="e", commits=0, duration_hours=0.0)
        anomalies = detect_anomalies(edge, b)  # cph=0 偏离基线 → 可能告警，但不抛
        assert isinstance(anomalies, list)

    def test_invalid_z_threshold(self):
        b = compute_baseline(_sessions())
        with pytest.raises(BehaviorBaselineError):
            detect_anomalies(_sessions()[0], b, z_threshold=0)
