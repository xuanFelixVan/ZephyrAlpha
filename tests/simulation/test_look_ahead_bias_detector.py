# [BLUEPRINT] MOD-SIM-022 | docs/03_modules/_domain_simulation/look_ahead_bias_detector/blueprint.md
# [MODULE] tests.simulation.test_look_ahead_bias_detector
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.simulation.look_ahead_bias_detector
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SIM-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIM-022 Look-Ahead Bias Detector 单元测试.

覆盖: 干净DataFrame无偏差、前瞻列名检测、标签泄露、尾部NaN检测、
截断重算验证(有偏差/无偏差)、时间戳单调性、审计摘要、边界值(空/列缺失)、
严重度排序、配置自定义、frozen不可变.
"""

from __future__ import annotations

import math

import pandas as pd
import pytest

from zephyr.simulation.look_ahead_bias_detector import (
    BiasIssue,
    BiasSeverity,
    BiasType,
    DetectionResult,
    DetectorConfig,
    LookAheadBiasDetector,
    SimulationError,
)

# ============== 辅助函数 ==============


def make_clean_df(n: int = 100) -> pd.DataFrame:
    """生成无前瞻偏差的特征 DataFrame。"""
    return pd.DataFrame(
        {
            "ma5": [float(i % 10) for i in range(n)],
            "rsi": [float(i % 5) for i in range(n)],
            "volume": [float(i) for i in range(n)],
        }
    )


def make_trailing_nan_df(n: int = 100, shift_k: int = 5) -> pd.DataFrame:
    """生成含尾部 NaN 的特征(模拟 shift(-k))。"""
    col = [float(i) for i in range(n)]
    # 末尾 shift_k 行置 NaN
    for i in range(n - shift_k, n):
        col[i] = float("nan")
    return pd.DataFrame({"fwd_ret": col, "clean_feat": [float(i) for i in range(n)]})


# ============== 配置 ==============


class TestDetectorConfig:
    def test_defaults(self):
        cfg = DetectorConfig()
        assert "_fwd" in cfg.forward_name_patterns
        assert "_target" in cfg.target_name_patterns
        assert cfg.truncation_test_points == 10
        assert cfg.truncation_tolerance == 1e-9

    def test_frozen(self):
        cfg = DetectorConfig()
        with pytest.raises(Exception):
            cfg.truncation_test_points = 20  # type: ignore[misc]

    def test_custom(self):
        cfg = DetectorConfig(
            forward_name_patterns=("_lead",),
            truncation_test_points=5,
            truncation_tolerance=1e-6,
        )
        assert cfg.forward_name_patterns == ("_lead",)
        assert cfg.truncation_test_points == 5


class TestFrozenDataclasses:
    def test_bias_issue_frozen(self):
        issue = BiasIssue(
            bias_type=BiasType.LABEL_LEAKAGE,
            severity=BiasSeverity.CRITICAL,
            column="y",
            description="d",
            evidence="e",
        )
        with pytest.raises(Exception):
            issue.severity = BiasSeverity.LOW  # type: ignore[misc]

    def test_detection_result_frozen(self):
        r = DetectionResult()
        with pytest.raises(Exception):
            r.is_clean = False  # type: ignore[misc]

    def test_empty_result_is_clean(self):
        r = DetectionResult()
        assert r.is_clean is True
        assert r.total_issues == 0
        assert r.max_severity is None


# ============== 干净 DataFrame ==============


class TestCleanDataFrame:
    def test_clean_df_no_issues(self):
        detector = LookAheadBiasDetector()
        result = detector.scan(make_clean_df())
        assert result.is_clean
        assert result.total_issues == 0
        assert result.critical_count == 0
        assert result.max_severity is None

    def test_clean_with_label_separate(self):
        detector = LookAheadBiasDetector()
        df = make_clean_df()
        df["label"] = [float(i % 2) for i in range(len(df))]
        result = detector.scan(df, feature_columns=["ma5", "rsi"], label_column="label")
        assert result.is_clean


# ============== 前瞻列名检测 ==============


class TestForwardColumnName:
    def test_forward_pattern_detected(self):
        detector = LookAheadBiasDetector()
        df = pd.DataFrame({"ret_fwd": [1.0] * 100, "clean": [2.0] * 100})
        result = detector.scan(df, feature_columns=["ret_fwd", "clean"])
        assert not result.is_clean
        types = [i.bias_type for i in result.issues]
        assert BiasType.FORWARD_COLUMN_NAME in types
        # ret_fwd 应被标记
        fwd_issue = next(i for i in result.issues if i.column == "ret_fwd")
        assert fwd_issue.severity == BiasSeverity.MEDIUM

    def test_target_pattern_high_severity(self):
        detector = LookAheadBiasDetector()
        df = pd.DataFrame({"ret_target": [1.0] * 100})
        result = detector.scan(df, feature_columns=["ret_target"])
        assert not result.is_clean
        issue = result.issues[0]
        assert issue.severity == BiasSeverity.HIGH
        assert issue.column == "ret_target"

    def test_clean_name_not_flagged(self):
        detector = LookAheadBiasDetector()
        df = pd.DataFrame({"ma5": [1.0] * 50, "rsi_14": [2.0] * 50})
        result = detector.scan(df, feature_columns=["ma5", "rsi_14"])
        assert result.is_clean

    def test_case_insensitive(self):
        detector = LookAheadBiasDetector()
        df = pd.DataFrame({"RET_FWD": [1.0] * 100})
        result = detector.scan(df, feature_columns=["RET_FWD"])
        assert not result.is_clean


# ============== 标签泄露 ==============


class TestLabelLeakage:
    def test_label_in_features_critical(self):
        detector = LookAheadBiasDetector()
        df = pd.DataFrame({"ma5": [1.0] * 100, "label": [0.0] * 100})
        result = detector.scan(df, feature_columns=["ma5", "label"], label_column="label")
        assert not result.is_clean
        leakage = [i for i in result.issues if i.bias_type == BiasType.LABEL_LEAKAGE]
        assert len(leakage) == 1
        assert leakage[0].severity == BiasSeverity.CRITICAL
        assert leakage[0].column == "label"

    def test_label_not_in_features_no_leakage(self):
        detector = LookAheadBiasDetector()
        df = pd.DataFrame({"ma5": [1.0] * 100, "label": [0.0] * 100})
        result = detector.scan(df, feature_columns=["ma5"], label_column="label")
        leakage = [i for i in result.issues if i.bias_type == BiasType.LABEL_LEAKAGE]
        assert len(leakage) == 0


# ============== 尾部 NaN 检测 ==============


class TestTrailingNaN:
    def test_trailing_nan_detected(self):
        detector = LookAheadBiasDetector()
        df = make_trailing_nan_df(100, shift_k=5)
        result = detector.scan(df, feature_columns=["fwd_ret", "clean_feat"])
        shifts = [i for i in result.issues if i.bias_type == BiasType.FUTURE_SHIFT]
        assert len(shifts) == 1
        assert shifts[0].column == "fwd_ret"
        assert shifts[0].severity == BiasSeverity.HIGH
        assert "5" in shifts[0].description

    def test_scattered_nan_not_flagged(self):
        """前部含 NaN 的列不触发(常规缺失值)。"""
        detector = LookAheadBiasDetector()
        n = 100
        col = [float(i) for i in range(n)]
        col[5] = float("nan")  # 中部 NaN
        col[50] = float("nan")
        df = pd.DataFrame({"feat": col})
        result = detector.scan(df, feature_columns=["feat"])
        shifts = [i for i in result.issues if i.bias_type == BiasType.FUTURE_SHIFT]
        assert len(shifts) == 0

    def test_no_nan_not_flagged(self):
        detector = LookAheadBiasDetector()
        df = pd.DataFrame({"feat": [float(i) for i in range(100)]})
        result = detector.scan(df, feature_columns=["feat"])
        shifts = [i for i in result.issues if i.bias_type == BiasType.FUTURE_SHIFT]
        assert len(shifts) == 0


# ============== 时间戳单调性 ==============


class TestTimestampMonotonic:
    def test_monotonic_ok(self):
        detector = LookAheadBiasDetector()
        df = pd.DataFrame({"feat": [1.0] * 50, "ts": list(range(50))})
        result = detector.scan(df, feature_columns=["feat"], timestamp_column="ts")
        ts_issues = [i for i in result.issues if i.bias_type == BiasType.NON_MONOTONIC_TIMESTAMP]
        assert len(ts_issues) == 0

    def test_non_monotonic_detected(self):
        detector = LookAheadBiasDetector()
        ts = list(range(50))
        ts[10] = 5  # 倒退
        df = pd.DataFrame({"feat": [1.0] * 50, "ts": ts})
        result = detector.scan(df, feature_columns=["feat"], timestamp_column="ts")
        ts_issues = [i for i in result.issues if i.bias_type == BiasType.NON_MONOTONIC_TIMESTAMP]
        assert len(ts_issues) == 1
        assert ts_issues[0].severity == BiasSeverity.MEDIUM

    def test_duplicate_timestamp_detected(self):
        detector = LookAheadBiasDetector()
        ts = list(range(50))
        ts[10] = ts[9]  # 重复
        df = pd.DataFrame({"feat": [1.0] * 50, "ts": ts})
        result = detector.scan(df, feature_columns=["feat"], timestamp_column="ts")
        ts_issues = [i for i in result.issues if i.bias_type == BiasType.NON_MONOTONIC_TIMESTAMP]
        assert len(ts_issues) == 1


# ============== 截断重算验证 ==============


class TestTruncationValidation:
    def test_clean_function_passes(self):
        """滚动均值(仅用过去数据)无前瞻偏差。"""
        detector = LookAheadBiasDetector()

        def rolling_mean_past(d: list) -> list:
            result = []
            for i in range(len(d)):
                result.append(sum(d[: i + 1]) / (i + 1))
            return result

        data = [float(i) for i in range(100)]
        result = detector.validate_function(rolling_mean_past, data)
        assert result.is_clean

    def test_biased_function_detected(self):
        """全样本均值(用全部数据)有前瞻偏差。"""
        detector = LookAheadBiasDetector()

        def full_sample_mean(d: list) -> list:
            # 用全样本均值填充每一行——前瞻!
            m = sum(d) / len(d)
            return [m] * len(d)

        data = [float(i) for i in range(100)]
        result = detector.validate_function(full_sample_mean, data)
        assert not result.is_clean
        mismatches = [i for i in result.issues if i.bias_type == BiasType.TRUNCATION_MISMATCH]
        assert len(mismatches) == 1
        assert mismatches[0].severity == BiasSeverity.CRITICAL

    def test_full_sample_std_detected(self):
        """全样本标准化(z-score)有前瞻偏差。"""
        detector = LookAheadBiasDetector()

        def zscore_full(d: list) -> list:
            m = sum(d) / len(d)
            var = sum((x - m) ** 2 for x in d) / len(d)
            std = math.sqrt(var)
            return [(x - m) / std for x in d]

        data = [float(i) for i in range(100)]
        result = detector.validate_function(zscore_full, data)
        assert not result.is_clean
        assert result.critical_count >= 1

    def test_custom_test_indices(self):
        detector = LookAheadBiasDetector()

        def full_mean(d: list) -> list:
            m = sum(d) / len(d)
            return [m] * len(d)

        data = [float(i) for i in range(100)]
        result = detector.validate_function(full_mean, data, test_indices=[50])
        assert not result.is_clean

    def test_empty_data_raises(self):
        detector = LookAheadBiasDetector()
        with pytest.raises(SimulationError):
            detector.validate_function(lambda d: d, [])


# ============== 边界值 ==============


class TestEdgeCases:
    def test_empty_df_raises(self):
        detector = LookAheadBiasDetector()
        with pytest.raises(SimulationError):
            detector.scan(pd.DataFrame())

    def test_missing_column_raises(self):
        detector = LookAheadBiasDetector()
        df = pd.DataFrame({"a": [1.0] * 10})
        with pytest.raises(SimulationError):
            detector.scan(df, feature_columns=["a", "nonexistent"])

    def test_error_code(self):
        assert SimulationError.error_code == "ZA-SIM-0022"

    def test_none_df_raises(self):
        detector = LookAheadBiasDetector()
        with pytest.raises(SimulationError):
            detector.scan(None)  # type: ignore[arg-type]


# ============== 严重度排序 ==============


class TestSeverityOrdering:
    def test_issues_sorted_descending(self):
        detector = LookAheadBiasDetector()
        # 构造含 CRITICAL + MEDIUM 的场景
        df = pd.DataFrame(
            {
                "ret_fwd": [1.0] * 100,  # MEDIUM (forward name)
                "label": [0.0] * 100,  # CRITICAL (label leakage)
            }
        )
        result = detector.scan(df, feature_columns=["ret_fwd", "label"], label_column="label")
        # 第一个应是最严重
        assert result.issues[0].severity == BiasSeverity.CRITICAL
        # 严重度非递增
        for i in range(len(result.issues) - 1):
            s1 = result.issues[i].severity
            s2 = result.issues[i + 1].severity
            assert _severity_rank(s1) >= _severity_rank(s2)

    def test_critical_count(self):
        detector = LookAheadBiasDetector()
        df = pd.DataFrame({"label": [0.0] * 50})
        result = detector.scan(df, feature_columns=["label"], label_column="label")
        assert result.critical_count == 1
        assert result.max_severity == BiasSeverity.CRITICAL


def _severity_rank(s: BiasSeverity) -> int:
    return {
        BiasSeverity.CRITICAL: 4,
        BiasSeverity.HIGH: 3,
        BiasSeverity.MEDIUM: 2,
        BiasSeverity.LOW: 1,
    }[s]


# ============== 审计摘要 ==============


class TestAuditSummary:
    def test_clean_summary(self):
        detector = LookAheadBiasDetector()
        result = detector.scan(make_clean_df())
        summary = detector.audit_summary(result)
        assert "PASS" in summary
        assert "0" in summary

    def test_biased_summary_lists_issues(self):
        detector = LookAheadBiasDetector()
        df = pd.DataFrame({"label": [0.0] * 50})
        result = detector.scan(df, feature_columns=["label"], label_column="label")
        summary = detector.audit_summary(result)
        assert "FAIL" in summary
        assert "CRITICAL" in summary
        assert "label_leakage" in summary
        assert "label" in summary


# ============== 枚举 ==============


class TestEnums:
    def test_bias_type_values(self):
        assert BiasType.LABEL_LEAKAGE.value == "label_leakage"
        assert BiasType.FUTURE_SHIFT.value == "future_shift"
        assert BiasType.TRUNCATION_MISMATCH.value == "truncation_mismatch"

    def test_severity_values(self):
        assert BiasSeverity.CRITICAL.value == "critical"
        assert BiasSeverity.LOW.value == "low"

    def test_enums_are_str_enum(self):
        assert isinstance(BiasType.LABEL_LEAKAGE, str)
        assert isinstance(BiasSeverity.CRITICAL, str)


# ============== 配置只读 ==============


class TestConfigReadonly:
    def test_config_property(self):
        cfg = DetectorConfig(truncation_test_points=7)
        detector = LookAheadBiasDetector(cfg)
        assert detector.config.truncation_test_points == 7
        assert detector.config is cfg
