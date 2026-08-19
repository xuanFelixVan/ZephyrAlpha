# [TTL] permanent
"""25号memo §3.7#8 HoldingDriftMonitor 测试。

覆盖：因子/行业/权重三通道 alert/critical 分级 / should_trigger_rebalance /
空输入退化 / 边界阈值（恰好等于阈值不触发）。
"""
from __future__ import annotations

import pytest

mod = pytest.importorskip("zephyr.pf_core.core.multifactor_holding_drift_monitor")

DriftAlertType = mod.DriftAlertType
monitor = mod.monitor


class TestFactorChannel:
    def test_factor_alert(self):
        r = monitor(current_factor_exposure={"f1": 0.12}, target_factor_exposure={"f1": 0.05})
        assert r.alerts[0].alert_type is DriftAlertType.FACTOR_ALERT  # 0.07>0.05
        assert r.critical_count == 0
        assert not r.should_trigger_rebalance

    def test_factor_critical_triggers_rebalance(self):
        r = monitor(current_factor_exposure={"f1": 0.16}, target_factor_exposure={"f1": 0.05})
        assert r.alerts[0].alert_type is DriftAlertType.FACTOR_CRITICAL  # 0.11>0.10
        assert r.critical_count == 1
        assert r.should_trigger_rebalance

    def test_factor_below_alert_silent(self):
        r = monitor(current_factor_exposure={"f1": 0.09}, target_factor_exposure={"f1": 0.05})
        assert r.alerts == ()


class TestIndustryChannel:
    def test_industry_alert(self):
        r = monitor(current_industry_exposure={"银行": 0.10}, target_industry_exposure={"银行": 0.06})
        assert r.alerts[0].alert_type is DriftAlertType.INDUSTRY_ALERT  # 0.04>0.03
        assert not r.should_trigger_rebalance

    def test_industry_critical(self):
        r = monitor(current_industry_exposure={"银行": 0.12}, target_industry_exposure={"银行": 0.06})
        assert r.alerts[0].alert_type is DriftAlertType.INDUSTRY_CRITICAL  # 0.06>0.05
        assert r.should_trigger_rebalance


class TestWeightChannel:
    def test_weight_drift_alert_no_force(self):
        r = monitor(weight_drift=0.12)
        assert r.alerts[0].alert_type is DriftAlertType.WEIGHT_DRIFT
        assert r.alerts[0].name == "portfolio"
        assert r.critical_count == 0
        assert not r.should_trigger_rebalance  # 只喂 RebalanceTrigger，不强制

    def test_weight_drift_boundary_not_alerted(self):
        r = monitor(weight_drift=0.10)  # 恰好=阈值不触发（>才触发）
        assert r.alerts == ()


class TestCombined:
    def test_empty_inputs(self):
        r = monitor()
        assert r.alerts == ()
        assert r.critical_count == 0
        assert not r.should_trigger_rebalance
        assert r.weight_drift == 0.0

    def test_mixed_alerts_critical_count(self):
        r = monitor(
            current_factor_exposure={"f1": 0.20, "f2": 0.07},
            target_factor_exposure={"f1": 0.05, "f2": 0.05},
            current_industry_exposure={"银行": 0.20},
            target_industry_exposure={"银行": 0.06},
            weight_drift=0.15,
        )
        types = {a.alert_type for a in r.alerts}
        assert DriftAlertType.FACTOR_CRITICAL in types      # f1 0.15
        assert DriftAlertType.FACTOR_ALERT not in types     # f2 0.02<0.05 静默
        assert DriftAlertType.INDUSTRY_CRITICAL in types    # 银行 0.14
        assert DriftAlertType.WEIGHT_DRIFT in types
        assert r.critical_count == 2
        assert r.should_trigger_rebalance

    def test_new_key_in_current_only(self):
        # 新出现的暴露（target 无）按 |current-0| 计偏差
        r = monitor(current_factor_exposure={"f_new": 0.12})
        assert r.alerts[0].alert_type is DriftAlertType.FACTOR_CRITICAL
