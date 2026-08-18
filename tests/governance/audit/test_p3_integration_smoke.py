# [A_test] module_id: MOD-GOV_p3_integration_smoke | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-280 | docs/03_modules/_domain_governance/blueprint.md | §ARCH-PREVENTABILITY-LAYER-001 Phase 3 P3-5
# [MODULE] tests.governance.audit.test_p3_integration_smoke
# [DOMAIN] D_GOV_AUDIT
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module; 断言失败->fail
# [TESTS] tests/governance/audit/test_p3_integration_smoke.py
# [A_module] module_id=MOD-TEST-280 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_p3_integration_smoke.py — Phase 3 全链路集成 smoke test（P3-5）

#ARCH-PREVENTABILITY-LAYER-001 Phase 3 P3-5 核心交付物（2026-07-20）。

验证 Phase 3 三个核心组件的端到端集成链路：
1. **AdaptiveThreshold**（P3-0）：COUNT 模式，static_floor + EWMA + factor
2. **_compute_adaptive_thresholds**（P3-1）：7d baseline → 6 维自适应阈值
3. **calculate_health_score**（P3-2）：6 维 metrics + thresholds → AbuseHealthScore
4. **_classify_abuse**（P3-1/P3-3）：reports + adaptive_thresholds → 触发维度 + effective thresholds

集成链路（P3-5 验证目标）::

    7d baseline ──→ _compute_adaptive_thresholds ──→ adaptive_thresholds
                                                          │
    today's reports ──→ _classify_abuse ──────────────→ metrics + effective_thresholds
                                                          │
                    calculate_health_score ←──────────────┘
                                                          │
                                                    AbuseHealthScore
                                                          │
                    P3-3 判定: score>0.7 critical, >0.9 block_next

设计原则（对标 test_sync_yaml_to_depgraph_smoke.py）：
1. 真实 import 三个组件模块（不 mock 内部连接）
2. 真实数据场景（clean/warn/critical/block_next 4 档）
3. 真实断言链路完整性（每个环节的输出 = 下个环节的输入）
4. @pytest.mark.smoke：快速运行（<5s）

Usage::

    py -3.12 -m pytest tests/governance/audit/test_p3_integration_smoke.py -v
"""
from __future__ import annotations

import pytest

import zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler as reconciler_mod

# 真实 import 三个组件（不 mock——集成 smoke test 的核心要求）
from zephyr.gov_enforcement.rule_enforcement.adaptive_threshold import (
    AdaptiveThreshold,
    ThresholdMode,
)
from zephyr.governance.audit.health_score_calculator import (
    AbuseHealthScore,
    calculate_health_score,
)

# short-name 阈值字典（与 _classify_abuse 返回的 effective_thresholds key 一致）
# _DEFAULT_THRESHOLDS 用 full names，但 calculate_health_score 用 short names
_SHORT_THRESHOLDS = {
    "warn_only_24h": 50,
    "emergency_commit_24h": 5,
    "allow_overlap_7d": 30,
    "forged_gw_marker_24h": 3,
    "non_gw_commit_24h": 10,
    "force_merge_7d": 5,
}


# ============================================================================
# Test 1: AdaptiveThreshold COUNT 模式单元验证（P3-0 基础）
# ============================================================================


class TestAdaptiveThresholdCountMode:
    """验证 AdaptiveThreshold COUNT 模式核心不变量（P3-0）。"""

    def test_set_count_config_creates_count_state(self):
        """set_count_config 创建 COUNT 模式 state。"""
        at = AdaptiveThreshold()
        at.set_count_config("test_dim", static_floor=50.0, factor=1.5)
        state = at.get_state("test_dim")
        assert state is not None, "set_count_config 未创建 state"
        assert state.mode == ThresholdMode.COUNT, (
            f"mode 应为 COUNT，实际: {state.mode}"
        )
        assert state.static_floor == 50.0
        assert state.factor == 1.5

    def test_observe_count_updates_threshold_via_ewma(self):
        """observe_count 记录历史并更新阈值 = max(ewma * factor, static_floor)。"""
        at = AdaptiveThreshold()
        at.set_count_config("test_dim", static_floor=50.0, factor=1.5)
        # 观察 3 天数据：[10, 20, 30]
        for count in [10, 20, 30]:
            at.observe_count("test_dim", count)
        state = at.get_state("test_dim")
        # EWMA 应在 10-30 之间，threshold = max(ewma * 1.5, 50)
        ewma_val = at.ewma("test_dim")
        expected_threshold = max(ewma_val * 1.5, 50.0)
        assert state.current_threshold == pytest.approx(
            expected_threshold, rel=1e-6
        ), (
            f"threshold={state.current_threshold} != max(ewma*factor, floor)="
            f"{expected_threshold} (ewma={ewma_val})"
        )

    def test_static_floor_prevents_threshold_below_floor(self):
        """static_floor 防止阈值降到很低后掩盖真实恶化。"""
        at = AdaptiveThreshold()
        at.set_count_config("test_dim", static_floor=50.0, factor=1.5)
        # 观察很低的计数 [1, 1, 1] —— ewma 很低，但 threshold 不应低于 static_floor
        for count in [1, 1, 1]:
            at.observe_count("test_dim", count)
        threshold = at.get_threshold("test_dim")
        assert threshold >= 50.0, (
            f"static_floor 失效：threshold={threshold} < 50.0（应 >= static_floor）"
        )

    def test_count_mode_is_immutable(self):
        """COUNT 模式不可变更为 PROBABILITY（fail-safe）。"""
        at = AdaptiveThreshold()
        at.set_count_config("test_dim", static_floor=50.0, factor=1.5)
        # 尝试用概率型 observe（应被忽略）
        at.observe("test_dim", 0.5, "FAIL")
        state = at.get_state("test_dim")
        assert state.mode == ThresholdMode.COUNT, "COUNT 模式被变更为 PROBABILITY"


# ============================================================================
# Test 2: _compute_adaptive_thresholds 集成验证（P3-1）
# ============================================================================


class TestComputeAdaptiveThresholds:
    """验证 _compute_adaptive_thresholds 从 7d baseline 计算自适应阈值（P3-1）。"""

    def test_empty_baseline_returns_empty_dict(self):
        """空 baseline 返回空 dict（调用方降级为纯静态阈值）。"""
        result = reconciler_mod.compute_adaptive_thresholds([])
        assert result == {}, f"空 baseline 应返回空 dict，实际: {result}"

    def test_7d_baseline_produces_6_dim_thresholds(self):
        """7d baseline 产生 6 维自适应阈值。"""
        # 构造 7d baseline daily_records
        daily_records = []
        for day in range(7):
            daily_records.append({
                "date": f"2026-07-{13+day:02d}",
                "metrics": {
                    "warn_only_24h": 30,
                    "emergency_commit_24h": 2,
                    "allow_overlap_7d": 10,
                    "forged_gw_marker_24h": 0,
                    "non_gw_commit_24h": 5,
                    "force_merge_7d": 0,
                },
            })
        result = reconciler_mod.compute_adaptive_thresholds(daily_records)
        # 应返回 6 维阈值
        assert len(result) == 6, f"应返回 6 维阈值，实际: {len(result)} 个"
        # 每维阈值应 >= static_floor（_DEFAULT_THRESHOLDS 值）
        for dim_name, threshold in result.items():
            static_val = reconciler_mod._DEFAULT_THRESHOLDS.get(dim_name, 0)
            assert threshold >= static_val, (
                f"{dim_name}: threshold={threshold} < static_floor={static_val}"
            )

    def test_high_baseline_produces_higher_thresholds(self):
        """高基线产生更高阈值（EWMA 跟随趋势）。"""
        # 高基线场景：每日计数远超静态阈值
        high_records = [
            {"metrics": {
                "warn_only_24h": 100, "emergency_commit_24h": 10,
                "allow_overlap_7d": 50, "forged_gw_marker_24h": 5,
                "non_gw_commit_24h": 20, "force_merge_7d": 10,
            }}
            for _ in range(7)
        ]
        high_thresholds = reconciler_mod.compute_adaptive_thresholds(high_records)

        # 低基线场景
        low_records = [
            {"metrics": {
                "warn_only_24h": 5, "emergency_commit_24h": 0,
                "allow_overlap_7d": 2, "forged_gw_marker_24h": 0,
                "non_gw_commit_24h": 1, "force_merge_7d": 0,
            }}
            for _ in range(7)
        ]
        low_thresholds = reconciler_mod.compute_adaptive_thresholds(low_records)

        # 高基线的阈值应 >= 低基线的阈值（EWMA 跟随）
        for dim_name in reconciler_mod._DEFAULT_THRESHOLDS:
            assert high_thresholds[dim_name] >= low_thresholds[dim_name], (
                f"{dim_name}: high={high_thresholds[dim_name]} < "
                f"low={low_thresholds[dim_name]}（EWMA 未跟随趋势）"
            )


# ============================================================================
# Test 3: calculate_health_score 集成验证（P3-2）
# ============================================================================


class TestHealthScoreIntegration:
    """验证 calculate_health_score 与 abuse_monitor metrics/thresholds 集成（P3-2）。"""

    def test_clean_scenario_low_score(self):
        """clean 场景：所有维度远低于阈值 → 低 score。"""
        metrics = {
            "warn_only_24h": 5,
            "emergency_commit_24h": 0,
            "allow_overlap_7d": 2,
            "forged_gw_marker_24h": 0,
            "non_gw_commit_24h": 1,
            "force_merge_7d": 0,
        }
        health = calculate_health_score(metrics, dict(_SHORT_THRESHOLDS))
        assert health.score < 0.3, (
            f"clean 场景 score={health.score} 应 < 0.3"
        )
        assert len(health.triggered_dimensions) == 0, (
            f"clean 场景不应有触发维度，实际: {health.triggered_dimensions}"
        )

    def test_critical_scenario_high_score(self):
        """critical 场景：多维度超阈 → 高 score。"""
        metrics = {
            "warn_only_24h": 60,  # > 50
            "emergency_commit_24h": 6,  # > 5
            "allow_overlap_7d": 35,  # > 30
            "forged_gw_marker_24h": 0,  # 未触发
            "non_gw_commit_24h": 12,  # > 10
            "force_merge_7d": 0,  # 未触发
        }
        health = calculate_health_score(metrics, dict(_SHORT_THRESHOLDS))
        assert health.score > 0.5, (
            f"critical 场景 score={health.score} 应 > 0.5"
        )
        assert len(health.triggered_dimensions) >= 3, (
            f"critical 场景应 >=3 维触发，实际: {health.triggered_dimensions}"
        )

    def test_block_next_scenario_max_score(self):
        """block_next 场景：全部维度超阈 → score 接近 1.0。"""
        metrics = {
            "warn_only_24h": 100,  # 2x threshold
            "emergency_commit_24h": 10,  # 2x threshold
            "allow_overlap_7d": 60,  # 2x threshold
            "forged_gw_marker_24h": 6,  # 2x threshold
            "non_gw_commit_24h": 20,  # 2x threshold
            "force_merge_7d": 10,  # 2x threshold
        }
        health = calculate_health_score(metrics, dict(_SHORT_THRESHOLDS))
        assert health.score > 0.9, (
            f"block_next 场景 score={health.score} 应 > 0.9"
        )
        assert len(health.triggered_dimensions) == 6, (
            f"block_next 场景应 6 维全触发，实际: {health.triggered_dimensions}"
        )

    def test_forged_gw_marker_has_highest_weight(self):
        """forged_gw_marker 权重最高（0.30）—— 任何伪造都 serious。"""
        # 仅 forged_gw_marker 超阈
        metrics = {
            "warn_only_24h": 0,
            "emergency_commit_24h": 0,
            "allow_overlap_7d": 0,
            "forged_gw_marker_24h": 10,  # >> 3
            "non_gw_commit_24h": 0,
            "force_merge_7d": 0,
        }
        health = calculate_health_score(metrics, dict(_SHORT_THRESHOLDS))
        # forged_gw_marker 单维贡献 = 0.30 * 1.0 = 0.30
        assert health.score == pytest.approx(0.30, rel=1e-6), (
            f"forged_gw_marker 单维 score={health.score} 应 ≈ 0.30 (weight=0.30)"
        )


# ============================================================================
# Test 4: _classify_abuse 集成验证（P3-1 + P3-3）
# ============================================================================


class TestClassifyAbuseIntegration:
    """验证 _classify_abuse 接入 adaptive_thresholds 后的有效阈值判定（P3-1）。"""

    def test_classify_abuse_with_adaptive_thresholds(self):
        """_classify_abuse 接受 adaptive_thresholds 参数并计算有效阈值。"""
        # 构造空报告（无违规）
        now_ts = 1784553000
        result = reconciler_mod.classify_abuse(
            post_commit_reports=[],
            audit_reports=[],
            emergency_count=0,
            now_ts=now_ts,
            allow_overlap_count=0,
            adaptive_thresholds={
                "warn_only_24h": 60.0,  # > static 50
                "emergency_commit_24h": 5.0,
                "allow_overlap_7d": 30.0,
                "forged_gw_marker_24h": 3.0,
                "non_gw_commit_24h": 10.0,
                "force_merge_7d": 5.0,
            },
        )
        # 无违规 → 0 维度触发
        assert len(result["dimensions_triggered"]) == 0, (
            f"无违规不应触发维度，实际: {result['dimensions_triggered']}"
        )
        # metrics 应包含 effective_thresholds（P3-1 产出）
        assert "effective_thresholds" in result["metrics"], (
            "metrics 缺少 effective_thresholds（P3-1 产出）"
        )

    def test_classify_abuse_without_adaptive_falls_back_to_static(self):
        """无 adaptive_thresholds 时降级为纯静态阈值（向后兼容）。"""
        now_ts = 1784553000
        result = reconciler_mod.classify_abuse(
            post_commit_reports=[],
            audit_reports=[],
            emergency_count=0,
            now_ts=now_ts,
            allow_overlap_count=0,
            adaptive_thresholds=None,  # 无自适应
        )
        # effective_thresholds 应等于静态阈值（short names）
        eff = result["metrics"].get("effective_thresholds", {})
        for dim_name, static_val in _SHORT_THRESHOLDS.items():
            assert eff.get(dim_name) == static_val, (
                f"{dim_name}: effective={eff.get(dim_name)} != static={static_val}"
            )


# ============================================================================
# Test 5: 全链路端到端验证（P3-5 核心集成 smoke test）
# ============================================================================


class TestFullPipelineIntegration:
    """验证全链路：baseline → adaptive → classify → health_score → action 判定。

    这是 P3-5 的核心交付物——验证 Phase 3 三个组件协同工作，
    任何一环断裂都会导致 score 计算错误或 action 判定错误。

    注意：_classify_abuse 从 post_commit_reports/audit_reports 计算 warn_only/
    forged/non_gw 维度，emergency/allow_overlap 由参数传入。本测试用 _classify_abuse
    产出 effective_thresholds（short names），然后注入 today_metrics 模拟今日计数，
    调 calculate_health_score 验证全链路 score。
    """

    def _run_full_pipeline(
        self,
        baseline_records: list[dict],
        today_metrics: dict,
    ) -> tuple[AbuseHealthScore, dict]:
        """执行全链路：baseline → adaptive → classify → health_score。

        Args:
            baseline_records: 7d baseline daily_records（full-name keys）
            today_metrics: 今日 6 维原始计数（short-name keys，注入 metrics 模拟）

        Returns:
            (health_score, classify_result)
        """
        # Step 1: 7d baseline → adaptive thresholds（P3-1）
        adaptive_thresholds = reconciler_mod.compute_adaptive_thresholds(
            baseline_records
        )

        # Step 2: _classify_abuse 产出 effective_thresholds（P3-1/P3-3）
        # 传 emergency_count + allow_overlap_count 以覆盖维度 2/3
        now_ts = 1784553000
        classify_result = reconciler_mod.classify_abuse(
            post_commit_reports=[],
            audit_reports=[],
            emergency_count=today_metrics.get("emergency_commit_24h", 0),
            now_ts=now_ts,
            allow_overlap_count=today_metrics.get("allow_overlap_7d", 0),
            force_merge_count=today_metrics.get("force_merge_7d", 0),
            adaptive_thresholds=adaptive_thresholds if adaptive_thresholds else None,
        )

        # Step 3: 注入今日完整 metrics（short names）→ calculate_health_score
        # _classify_abuse 返回的 metrics 已含 emergency/allow_overlap，但 warn_only/
        # forged/non_gw 在空报告下为 0。这里用 today_metrics 覆盖，模拟真实场景。
        merged_metrics = dict(classify_result["metrics"])
        merged_metrics.update(today_metrics)
        effective_thresholds = merged_metrics.get(
            "effective_thresholds"
        ) or merged_metrics.get("thresholds", {})
        health = calculate_health_score(merged_metrics, effective_thresholds)

        return health, classify_result

    def test_clean_pipeline(self):
        """全链路 clean 场景：低基线 + 低今日计数 → score < 0.7 → clean。"""
        baseline = [
            {"metrics": {
                "warn_only_24h": 5, "emergency_commit_24h": 0,
                "allow_overlap_7d": 2, "forged_gw_marker_24h": 0,
                "non_gw_commit_24h": 1, "force_merge_7d": 0,
            }}
            for _ in range(7)
        ]
        today = {
            "warn_only_24h": 5, "emergency_commit_24h": 0,
            "allow_overlap_7d": 2, "forged_gw_marker_24h": 0,
            "non_gw_commit_24h": 1, "force_merge_7d": 0,
        }
        health, result = self._run_full_pipeline(baseline, today)
        assert health.score < 0.7, (
            f"clean pipeline score={health.score} 应 < 0.7（_CRITICAL_WARN_SCORE）"
        )
        assert len(result["dimensions_triggered"]) == 0

    def test_critical_pipeline(self):
        """全链路 critical 场景：emergency + allow_overlap + warn_only + non_gw 超阈 + forged 部分贡献 → 0.7 < score <= 0.9。

        权重设计（v1.3.0 6 维）：forged=0.30 最高。emergency(0.20) + allow_overlap(0.15)
        + warn_only(0.15) + non_gw(0.10) 超阈 = 0.60。要达到 critical（>0.7），需 forged
        部分贡献（count < threshold 但 > 0）。例如 forged=2/3 → dim_score=0.667
        → score = 0.60 + 0.30*0.667 ≈ 0.80。

        注：_classify_abuse 从 post_commit_reports/audit_reports 计算 warn_only/
        forged/non_gw 维度（空报告下为 0，不触发 dimensions_triggered）。本测试
        通过 today_metrics 注入完整 6 维计数到 calculate_health_score，验证 score
        计算的全链路正确性。dimensions_triggered 仅反映 _classify_abuse 输出
        （emergency + allow_overlap 2 维，由参数传入）。
        """
        baseline = [
            {"metrics": {
                "warn_only_24h": 30, "emergency_commit_24h": 2,
                "allow_overlap_7d": 10, "forged_gw_marker_24h": 0,
                "non_gw_commit_24h": 5, "force_merge_7d": 0,
            }}
            for _ in range(7)
        ]
        today = {
            "warn_only_24h": 60,  # > 50 → dim_score=1.0（注入 health_score 计算）
            "emergency_commit_24h": 6,  # > 5 → dim_score=1.0（_classify_abuse 触发）
            "allow_overlap_7d": 35,  # > 30 → dim_score=1.0（_classify_abuse 触发）
            "forged_gw_marker_24h": 2,  # < 3 → dim_score=0.667（部分贡献）
            "non_gw_commit_24h": 12,  # > 10 → dim_score=1.0（注入 health_score 计算）
            "force_merge_7d": 0,  # 未触发
        }
        health, result = self._run_full_pipeline(baseline, today)
        assert health.score > 0.7, (
            f"critical pipeline score={health.score} 应 > 0.7（_CRITICAL_WARN_SCORE）"
        )
        assert health.score <= 0.9, (
            f"critical pipeline score={health.score} 应 <= 0.9（_BLOCK_NEXT_SCORE），"
            f"超过则应归入 block_next 场景"
        )
        # _classify_abuse 空报告下仅 emergency + allow_overlap 2 维触发（参数传入）
        assert len(result["dimensions_triggered"]) >= 2, (
            f"critical pipeline 应 >=2 维触发（emergency + allow_overlap），"
            f"实际: {result['dimensions_triggered']}"
        )

    def test_block_next_pipeline(self):
        """全链路 block_next 场景：全维度超阈 → score > 0.9 → block_next。"""
        baseline = [
            {"metrics": {
                "warn_only_24h": 50, "emergency_commit_24h": 5,
                "allow_overlap_7d": 30, "forged_gw_marker_24h": 3,
                "non_gw_commit_24h": 10, "force_merge_7d": 5,
            }}
            for _ in range(7)
        ]
        today = {
            "warn_only_24h": 100,  # 2x threshold
            "emergency_commit_24h": 10,  # 2x threshold
            "allow_overlap_7d": 60,  # 2x threshold
            "forged_gw_marker_24h": 6,  # 2x threshold
            "non_gw_commit_24h": 20,  # 2x threshold
            "force_merge_7d": 10,  # 2x threshold
        }
        health, result = self._run_full_pipeline(baseline, today)
        assert health.score > 0.9, (
            f"block_next pipeline score={health.score} 应 > 0.9（_BLOCK_NEXT_SCORE）"
        )
        assert len(health.triggered_dimensions) == 6, (
            f"block_next pipeline 应 6 维全触发，实际: {health.triggered_dimensions}"
        )

    def test_pipeline_with_high_baseline_raises_thresholds(self):
        """高基线提高自适应阈值 → 同样今日计数不再触发（EWMA 跟随）。

        这是 P3-1 的核心治本点：自适应阈值避免静态阈值在基线升高后误报。
        """
        # 高基线：每日计数 = 静态阈值
        high_baseline = [
            {"metrics": {
                "warn_only_24h": 50, "emergency_commit_24h": 5,
                "allow_overlap_7d": 30, "forged_gw_marker_24h": 3,
                "non_gw_commit_24h": 10, "force_merge_7d": 5,
            }}
            for _ in range(7)
        ]
        # 今日计数 = 静态阈值（刚好等于，不应触发——因为自适应阈值 > 静态）
        today_at_static = {
            "warn_only_24h": 50, "emergency_commit_24h": 5,
            "allow_overlap_7d": 30, "forged_gw_marker_24h": 3,
            "non_gw_commit_24h": 10, "force_merge_7d": 5,
        }
        health_high_baseline, _ = self._run_full_pipeline(
            high_baseline, today_at_static
        )

        # 低基线场景：今日计数 = 静态阈值（应触发——因为阈值就是静态值）
        low_baseline = [
            {"metrics": {
                "warn_only_24h": 1, "emergency_commit_24h": 0,
                "allow_overlap_7d": 0, "forged_gw_marker_24h": 0,
                "non_gw_commit_24h": 0, "force_merge_7d": 0,
            }}
            for _ in range(7)
        ]
        health_low_baseline, _ = self._run_full_pipeline(
            low_baseline, today_at_static
        )

        # 高基线下 score 应更低（自适应阈值提高了，同样计数不再超阈）
        assert health_high_baseline.score <= health_low_baseline.score, (
            f"高基线 score={health_high_baseline.score} 应 <= "
            f"低基线 score={health_low_baseline.score}（自适应阈值未生效）"
        )


# ============================================================================
# Test 6: 代码常量与 YAML 真源一致性（P3-4 交叉验证）
# ============================================================================


class TestCodeYamlConsistency:
    """验证代码常量与 trae_069 YAML 真源一致（P3-4 smoke test 的交叉验证）。

    P3-5 集成 smoke test 顺带验证 P3-4 的 YAML→代码同步链路，
    确保 _DEFAULT_THRESHOLDS / _CRITICAL_WARN_SCORE / _BLOCK_NEXT_SCORE
    与 YAML 真源一致。
    """

    def test_default_thresholds_match_yaml_values(self):
        """_DEFAULT_THRESHOLDS 与 trae_069 YAML thresholds 段值一致。

        _DEFAULT_THRESHOLDS 和 YAML thresholds 段都用 full names 作 key
        （warn_only_sustained_24h 等）。
        """
        from pathlib import Path

        import yaml

        yaml_path = (
            Path(__file__).resolve().parents[3]
            / "docs"
            / "01_policies_and_standards"
            / "rules"
            / "trae_069_commit_gateway_abuse_thresholds.yaml"
        )
        with yaml_path.open(encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)

        yaml_thresholds = yaml_data["thresholds"]
        code_thresholds = reconciler_mod._DEFAULT_THRESHOLDS

        # 两者都用 full names 作 key（_DEFAULT_THRESHOLDS key = YAML thresholds key）
        for dim_name, code_val in code_thresholds.items():
            yaml_dim = yaml_thresholds.get(dim_name, {})
            yaml_val = yaml_dim.get("value")
            assert yaml_val is not None, (
                f"{dim_name}: YAML thresholds 段缺失该维度"
            )
            assert code_val == yaml_val, (
                f"{dim_name}: code={code_val} != yaml={yaml_val}（SSoT 违规）"
            )

    def test_score_constants_match_yaml(self):
        """_CRITICAL_WARN_SCORE / _BLOCK_NEXT_SCORE 与 YAML 一致。"""
        from pathlib import Path

        import yaml

        yaml_path = (
            Path(__file__).resolve().parents[3]
            / "docs"
            / "01_policies_and_standards"
            / "rules"
            / "trae_069_commit_gateway_abuse_thresholds.yaml"
        )
        with yaml_path.open(encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)

        hsc = yaml_data["health_score_classification"]
        assert reconciler_mod._CRITICAL_WARN_SCORE == hsc["critical_warn"]["score_min"]
        assert reconciler_mod._BLOCK_NEXT_SCORE == hsc["block_next"]["score_min"]
