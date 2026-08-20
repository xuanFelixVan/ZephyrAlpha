# [A_test] module_id: SRC-TST-3000 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_HEALTH_SCORE_CALCULATOR | docs/03_modules/_domain_governance/blueprint.md | §ARCH-PREVENTABILITY-LAYER-001 Phase 3 P3-2
# [MODULE] tests.governance.audit.test_health_score_calculator
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_HEALTH_SCORE_CALCULATOR | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_health_score_calculator.py — P3-2 健康度评分计算器单测。

覆盖：
- HealthScore dataclass 字段默认值
- calculate_health_score 基本：5 维归一化 + 加权求和
- 边界条件：threshold=0 / count=0 / count>threshold (clamp 1.0)
- 权重处理：默认权重 / 自定义权重 / 权重总和≠1.0 自动归一化 / 权重总和=0 fallback
- 触发维度识别（dim_score >= 1.0）
- 未知维度过滤（thresholds/effective_thresholds 等非评分字段）
- 综合评分 clamp [0, 1]
- fail-safe：异常输入不抛异常
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from zephyr.governance.audit.health_score_calculator import (  # noqa: E402
    _DEFAULT_WEIGHTS,
    AbuseHealthScore,
    calculate_health_score,
)


class TestHealthScoreDataclass:
    """HealthScore dataclass 字段测试。"""

    def test_default_factories_independent(self):
        """每个 AbuseHealthScore 实例的 dict/list 字段相互独立（不是共享引用）。"""
        h1 = AbuseHealthScore(score=0.5)
        h2 = AbuseHealthScore(score=0.8)
        h1.dimension_scores["x"] = 1.0
        h1.triggered_dimensions.append("x")
        assert "x" not in h2.dimension_scores
        assert "x" not in h2.triggered_dimensions

    def test_score_field_required(self):
        """score 是必填字段（无默认值）。"""
        with pytest.raises(TypeError):
            AbuseHealthScore()  # type: ignore[call-arg]


class TestDefaultWeights:
    """_DEFAULT_WEIGHTS 常量测试。"""

    def test_weights_sum_to_one(self):
        """默认权重总和 = 1.0。"""
        assert abs(sum(_DEFAULT_WEIGHTS.values()) - 1.0) < 1e-10

    def test_forged_gw_marker_has_highest_weight(self):
        """forged_gw_marker 权重最高（任何伪造都 serious）。"""
        max_weight = max(_DEFAULT_WEIGHTS.values())
        assert _DEFAULT_WEIGHTS["forged_gw_marker_24h"] == max_weight

    def test_six_dimensions_present(self):
        """6 维都有权重。"""
        expected = {
            "warn_only_24h",
            "emergency_commit_24h",
            "allow_overlap_7d",
            "forged_gw_marker_24h",
            "non_gw_commit_24h",
            "force_merge_7d",
        }
        assert set(_DEFAULT_WEIGHTS.keys()) == expected


class TestCalculateHealthScoreBasic:
    """calculate_health_score 基本功能测试。"""

    NOW_TS = 1784000000
    THRESHOLDS = {
        "warn_only_24h": 50,
        "emergency_commit_24h": 5,
        "allow_overlap_7d": 30,
        "forged_gw_marker_24h": 3,
        "non_gw_commit_24h": 10,
        "force_merge_7d": 5,
    }

    def test_all_zero_metrics_returns_zero_score(self):
        """所有 metrics=0 → score=0.0（完全健康）。"""
        metrics = {dim: 0 for dim in self.THRESHOLDS}
        result = calculate_health_score(metrics, self.THRESHOLDS)
        assert result.score == 0.0
        assert result.triggered_dimensions == []
        assert all(v == 0.0 for v in result.dimension_scores.values())

    def test_all_above_threshold_returns_one_score(self):
        """所有 metrics > threshold → score=1.0（完全失控）。"""
        metrics = {
            "warn_only_24h": 100,
            "emergency_commit_24h": 10,
            "allow_overlap_7d": 60,
            "forged_gw_marker_24h": 6,
            "non_gw_commit_24h": 20,
            "force_merge_7d": 10,
        }
        result = calculate_health_score(metrics, self.THRESHOLDS)
        assert abs(result.score - 1.0) < 1e-10
        assert len(result.triggered_dimensions) == 6

    def test_single_dimension_partial_score(self):
        """单维部分得分：warn_only=25, threshold=50 → dim_score=0.5, weighted=0.5*0.15=0.075。"""
        metrics = {dim: 0 for dim in self.THRESHOLDS}
        metrics["warn_only_24h"] = 25  # 25/50 = 0.5
        result = calculate_health_score(metrics, self.THRESHOLDS)
        assert result.dimension_scores["warn_only_24h"] == 0.5
        # 加权：0.5 * 0.15 = 0.075
        assert abs(result.score - 0.075) < 1e-10

    def test_dimension_score_clamped_to_one(self):
        """count > threshold → dim_score clamp 到 1.0。"""
        metrics = {dim: 0 for dim in self.THRESHOLDS}
        metrics["warn_only_24h"] = 200  # 200/50 = 4.0, clamp to 1.0
        result = calculate_health_score(metrics, self.THRESHOLDS)
        assert result.dimension_scores["warn_only_24h"] == 1.0
        assert "warn_only_24h" in result.triggered_dimensions

    def test_triggered_dimensions_only_above_threshold(self):
        """triggered_dimensions 只包含 dim_score >= 1.0 的维度。"""
        metrics = {
            "warn_only_24h": 60,  # 60/50=1.2 → 1.0 triggered
            "emergency_commit_24h": 3,  # 3/5=0.6 not triggered
            "allow_overlap_7d": 0,
            "forged_gw_marker_24h": 4,  # 4/3=1.33 → 1.0 triggered
            "non_gw_commit_24h": 0,
        }
        result = calculate_health_score(metrics, self.THRESHOLDS)
        assert set(result.triggered_dimensions) == {"warn_only_24h", "forged_gw_marker_24h"}


class TestThresholdZeroFailSafe:
    """threshold=0 fail-safe 测试（避免除零）。"""

    def test_threshold_zero_dim_score_zero(self):
        """threshold=0 → 该维得分=0.0（fail-safe，不抛异常）。"""
        metrics = {
            "warn_only_24h": 100,
            "emergency_commit_24h": 0,
            "allow_overlap_7d": 0,
            "forged_gw_marker_24h": 0,
            "non_gw_commit_24h": 0,
        }
        thresholds = {
            "warn_only_24h": 0,
            "emergency_commit_24h": 5,
            "allow_overlap_7d": 30,
            "forged_gw_marker_24h": 3,
            "non_gw_commit_24h": 10,
        }
        result = calculate_health_score(metrics, thresholds)
        assert result.dimension_scores["warn_only_24h"] == 0.0
        assert "warn_only_24h" not in result.triggered_dimensions

    def test_all_thresholds_zero_returns_zero_score(self):
        """所有 threshold=0 → score=0.0（fail-safe）。"""
        metrics = {
            "warn_only_24h": 100,
            "emergency_commit_24h": 10,
            "allow_overlap_7d": 60,
            "forged_gw_marker_24h": 6,
            "non_gw_commit_24h": 20,
        }
        thresholds = {dim: 0 for dim in metrics}
        result = calculate_health_score(metrics, thresholds)
        assert result.score == 0.0


class TestCustomWeights:
    """自定义权重测试。"""

    THRESHOLDS = {
        "warn_only_24h": 50,
        "emergency_commit_24h": 5,
        "allow_overlap_7d": 30,
        "forged_gw_marker_24h": 3,
        "non_gw_commit_24h": 10,
        "force_merge_7d": 5,
    }

    def test_custom_weights_used(self):
        """自定义权重被使用（非默认）。"""
        metrics = {dim: 0 for dim in self.THRESHOLDS}
        metrics["warn_only_24h"] = 25  # dim_score=0.5
        # 自定义权重：warn_only=1.0，其余=0
        custom_weights = {dim: 0.0 for dim in self.THRESHOLDS}
        custom_weights["warn_only_24h"] = 1.0
        result = calculate_health_score(metrics, self.THRESHOLDS, weights=custom_weights)
        # score = 0.5 * 1.0 = 0.5
        assert abs(result.score - 0.5) < 1e-10
        assert result.weights["warn_only_24h"] == 1.0

    def test_weights_normalized_when_sum_not_one(self):
        """权重总和≠1.0 时自动归一化。"""
        metrics = {dim: 0 for dim in self.THRESHOLDS}
        metrics["warn_only_24h"] = 50  # dim_score=1.0
        # 权重总和=2.0（非 1.0）
        custom_weights = {dim: 0.0 for dim in self.THRESHOLDS}
        custom_weights["warn_only_24h"] = 2.0
        result = calculate_health_score(metrics, self.THRESHOLDS, weights=custom_weights)
        # 归一化后 warn_only=1.0, score = 1.0 * 1.0 = 1.0
        assert abs(result.weights["warn_only_24h"] - 1.0) < 1e-10
        assert abs(result.score - 1.0) < 1e-10

    def test_weights_zero_sum_fallback_to_defaults(self):
        """权重总和=0 → fallback 到默认权重（不抛异常）。"""
        metrics = {dim: 0 for dim in self.THRESHOLDS}
        zero_weights = {dim: 0.0 for dim in self.THRESHOLDS}
        result = calculate_health_score(metrics, self.THRESHOLDS, weights=zero_weights)
        # fallback 后使用默认权重
        assert result.weights == _DEFAULT_WEIGHTS
        assert result.score == 0.0  # metrics 全 0


class TestUnknownDimensionsFiltered:
    """未知维度过滤测试。"""

    def test_non_scoring_keys_ignored(self):
        """metrics 中的非评分字段（thresholds/effective_thresholds 等）被忽略。"""
        metrics = {
            "warn_only_24h": 50,
            "emergency_commit_24h": 0,
            "allow_overlap_7d": 0,
            "forged_gw_marker_24h": 0,
            "non_gw_commit_24h": 0,
            "force_merge_7d": 0,
            # 非评分字段（应被忽略）
            "thresholds": {"warn_only_24h": 50},
            "effective_thresholds": {"warn_only_24h": 50},
            "adaptive_thresholds": {"warn_only_sustained_24h": 75.0},
        }
        thresholds = {
            "warn_only_24h": 50,
            "emergency_commit_24h": 5,
            "allow_overlap_7d": 30,
            "forged_gw_marker_24h": 3,
            "non_gw_commit_24h": 10,
            "force_merge_7d": 5,
        }
        result = calculate_health_score(metrics, thresholds)
        # 只应包含 6 维得分
        assert set(result.dimension_scores.keys()) == set(_DEFAULT_WEIGHTS.keys())
        # warn_only=50/50=1.0, score = 1.0 * 0.15 = 0.15
        assert result.dimension_scores["warn_only_24h"] == 1.0
        assert abs(result.score - 0.15) < 1e-10


class TestScoreClamp:
    """综合评分 clamp [0, 1] 测试。"""

    def test_score_never_below_zero(self):
        """score 永远 >= 0.0（即使权重为负，但权重不应为负）。"""
        metrics = {dim: 0 for dim in _DEFAULT_WEIGHTS}
        thresholds = {dim: 1 for dim in _DEFAULT_WEIGHTS}
        result = calculate_health_score(metrics, thresholds)
        assert result.score >= 0.0

    def test_score_never_above_one(self):
        """score 永远 <= 1.0（即使所有维度满分）。"""
        metrics = {dim: 1000 for dim in _DEFAULT_WEIGHTS}
        thresholds = {dim: 1 for dim in _DEFAULT_WEIGHTS}
        result = calculate_health_score(metrics, thresholds)
        assert result.score <= 1.0


class TestFailSafeOnInvalidInput:
    """异常输入 fail-safe 测试（不抛异常）。"""

    def test_non_numeric_count_returns_zero_dim_score(self):
        """count 是非数字 → 该维得分=0.0（不抛异常）。"""
        metrics = {
            "warn_only_24h": "not a number",
            "emergency_commit_24h": 0,
            "allow_overlap_7d": 0,
            "forged_gw_marker_24h": 0,
            "non_gw_commit_24h": 0,
        }
        thresholds = {dim: 10 for dim in _DEFAULT_WEIGHTS}
        result = calculate_health_score(metrics, thresholds)
        assert result.dimension_scores["warn_only_24h"] == 0.0

    def test_non_numeric_threshold_returns_zero_dim_score(self):
        """threshold 是非数字 → 该维得分=0.0（不抛异常）。"""
        metrics = {dim: 10 for dim in _DEFAULT_WEIGHTS}
        thresholds = {
            "warn_only_24h": "not a number",
            "emergency_commit_24h": 10,
            "allow_overlap_7d": 10,
            "forged_gw_marker_24h": 10,
            "non_gw_commit_24h": 10,
        }
        result = calculate_health_score(metrics, thresholds)
        assert result.dimension_scores["warn_only_24h"] == 0.0

    def test_empty_metrics_returns_zero_score(self):
        """空 metrics → score=0.0（所有维度缺失，按 0 处理）。"""
        result = calculate_health_score({}, {})
        assert result.score == 0.0
        assert len(result.dimension_scores) == 6  # 6 维都有得分（全 0）


class TestAbuseMonitorIntegration:
    """模拟 abuse_monitor metrics 场景，验证 P3-2 设计满足 P3-3 接入需求。"""

    THRESHOLDS = {
        "warn_only_24h": 50,
        "emergency_commit_24h": 5,
        "allow_overlap_7d": 30,
        "forged_gw_marker_24h": 3,
        "non_gw_commit_24h": 10,
        "force_merge_7d": 5,
    }

    def test_clean_scenario_low_score(self):
        """clean 场景：所有 metrics 低 → score < 0.7（不触发 critical_warn）。"""
        metrics = {
            "warn_only_24h": 5,  # 5/50=0.1
            "emergency_commit_24h": 0,  # 0/5=0
            "allow_overlap_7d": 2,  # 2/30=0.067
            "forged_gw_marker_24h": 0,  # 0/3=0
            "non_gw_commit_24h": 1,  # 1/10=0.1
            "force_merge_7d": 0,  # 0/5=0
        }
        result = calculate_health_score(metrics, self.THRESHOLDS)
        assert result.score < 0.7
        assert result.triggered_dimensions == []

    def test_forged_only_high_score(self):
        """仅 forged 触发 → score 较高（forged 权重 0.30）。"""
        metrics = {
            "warn_only_24h": 0,
            "emergency_commit_24h": 0,
            "allow_overlap_7d": 0,
            "forged_gw_marker_24h": 4,  # 4/3=1.33 → 1.0
            "non_gw_commit_24h": 0,
            "force_merge_7d": 0,
        }
        result = calculate_health_score(metrics, self.THRESHOLDS)
        # forged 得分=1.0, 权重=0.30 → score=0.30
        assert abs(result.score - 0.30) < 1e-10
        assert result.triggered_dimensions == ["forged_gw_marker_24h"]

    def test_critical_scenario_high_score(self):
        """critical 场景：3+ 维度触发 → score > 0.7。"""
        metrics = {
            "warn_only_24h": 60,  # 60/50=1.2 → 1.0, weight 0.15
            "emergency_commit_24h": 8,  # 8/5=1.6 → 1.0, weight 0.20
            "allow_overlap_7d": 0,
            "forged_gw_marker_24h": 5,  # 5/3=1.67 → 1.0, weight 0.30
            "non_gw_commit_24h": 0,
            "force_merge_7d": 0,
        }
        result = calculate_health_score(metrics, self.THRESHOLDS)
        # 3 维满分：0.15 + 0.20 + 0.30 = 0.65
        assert abs(result.score - 0.65) < 1e-10
        assert len(result.triggered_dimensions) == 3

    def test_block_next_scenario_very_high_score(self):
        """block_next 场景：所有维度触发 → score=1.0 > 0.9。"""
        metrics = {dim: 1000 for dim in self.THRESHOLDS}
        result = calculate_health_score(metrics, self.THRESHOLDS)
        assert abs(result.score - 1.0) < 1e-10
        assert result.score > 0.9
        assert len(result.triggered_dimensions) == 6
