# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] tests.governance.test_alert_threshold_consistency
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] 注册表阈值=代码常量（漂移即失败——注册表不许说谎）；active 条目全有代码锚点getter；design 条目存在性校验
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即漂移证据（哪条 THD/代码值/注册表值）
# [TESTS] self
# [A_module] module_id=MOD-GOVERNANCE | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""REG-ATH-001 告警阈值注册表 ↔ 代码常量一致性对账测试（55 号 §3.3 配套，#ARCH-MON-001）.

裁定模型（对齐 #ARCH-BREG-002 分域真源裁定）：
  存量生产模块的阈值运行真源=代码常量（运行时零 YAML 耦合，fail-fast 行为不变）；
  注册表=评审/审计视图真源（55 号 §3.3「阈值不集中即不可审计」）；
  双向一致性=本对账测试机器校验（漂移→测试红→禁止「注册表说谎」）。
  新模块（MOD-RK-23/退役评估器）运行时已 fail-closed 直读注册表（改表即生效），
  不在本对账范围（其一致性由自身加载测试覆盖）。

覆盖 32 条 active 条目全量对账 + 3 条 design 条目存在性校验。
（2026-08-15 v1.1.0：4 条 pending_adjudication 经 Owner 裁定转正 active——
THD-RETIRE-001/002/003 + THD-DEVIATION-003，值不变，并入 active 对账。）
"""

from __future__ import annotations

import inspect

import yaml

from zephyr.backtest.core.decision_gate import DecisionGateConfig
from zephyr.gov_drift.detector_core.model_drift_monitor import (
    DRIFT_MONITORS,
    ModelDriftType,
)
from zephyr.governance.lifecycle_governance.post_live_verification import (
    PLV_CHECKS,
    PLVCheck,
)
from zephyr.reporting import risk_report_engine
from zephyr.risk.core import alert_generator
from zephyr.risk.core.daily_auditor import AuditConfig
from zephyr.risk.core.drawdown_tracker import DrawdownTrackerConfig
from zephyr.risk.core.operational_risk_monitor import (
    _SEVERE_MULTIPLIER,
    DEFAULT_FAILURE_RATE_THRESHOLD,
    DEFAULT_LATENCY_P95_THRESHOLD_MS,
)
from zephyr.risk.core.strategy_deviation_monitor import ALERT_THRESHOLD_REGISTRY_PATH
from zephyr.shared.alerts.alert_escalation import AlertEscalation
from zephyr.trading import health_monitor


def _registry_entries() -> dict[str, dict]:
    data = yaml.safe_load(ALERT_THRESHOLD_REGISTRY_PATH.read_text(encoding="utf-8"))
    return {e["threshold_id"]: e for e in data["thresholds"]}


class TestActiveThresholdsMatchCode:
    """32 条 active 条目：注册表值 MUST 等于代码常量当前值（漂移=测试红）。"""

    def test_drawdown_triple(self):
        e = _registry_entries()
        cfg = DrawdownTrackerConfig()
        assert float(e["THD-DRAWDOWN-001"]["value"]) == cfg.warning_threshold
        assert float(e["THD-DRAWDOWN-002"]["value"]) == cfg.critical_threshold
        assert float(e["THD-DRAWDOWN-003"]["value"]) == cfg.emergency_threshold

    def test_health_pressure(self):
        e = _registry_entries()
        assert float(e["THD-HEALTH-001"]["value"]) == health_monitor._MEM_PRESSURE_ELEVATED
        assert float(e["THD-HEALTH-002"]["value"]) == health_monitor._MEM_PRESSURE_HIGH
        assert float(e["THD-HEALTH-003"]["value"]) == health_monitor._MEM_PRESSURE_CRITICAL
        assert float(e["THD-HEALTH-004"]["value"]) == health_monitor._DISK_PRESSURE_CRITICAL

    def test_deviation_thresholds(self):
        e = _registry_entries()
        cfg = DecisionGateConfig()
        assert float(e["THD-DEVIATION-001"]["value"]) == cfg.backtest_live_deviation_warn
        assert float(e["THD-DEVIATION-002"]["value"]) == cfg.backtest_live_deviation_retire

    def test_plv_five_specs(self):
        e = _registry_entries()
        assert e["THD-PLV-001"]["value"] == PLV_CHECKS[PLVCheck.ORDER_COUNT_DEVIATION].threshold
        assert e["THD-PLV-002"]["value"] == PLV_CHECKS[PLVCheck.FILL_RATE_COMPARISON].threshold
        assert e["THD-PLV-003"]["value"] == PLV_CHECKS[PLVCheck.RISK_CONFORMANCE].threshold
        assert e["THD-PLV-004"]["value"] == PLV_CHECKS[PLVCheck.DATA_INTEGRITY].threshold
        assert e["THD-PLV-005"]["value"] == PLV_CHECKS[PLVCheck.PNL_RECONCILIATION].threshold

    def test_alert_mechanism(self):
        e = _registry_entries()
        dedup_default = inspect.signature(
            alert_generator.AlertGenerator.__init__
        ).parameters["dedup_window"].default
        assert float(e["THD-ALERT-001"]["value"]) == dedup_default.total_seconds()
        try:
            esc_default = AlertEscalation.model_fields["auto_escalate_after_seconds"].default
        except AttributeError:  # pydantic v1 兼容
            esc_default = AlertEscalation.__fields__["auto_escalate_after_seconds"].default
        assert float(e["THD-ALERT-002"]["value"]) == float(esc_default)

    def test_daily_audit(self):
        e = _registry_entries()
        cfg = AuditConfig()
        assert float(e["THD-AUDIT-001"]["value"]) == cfg.pnl_tolerance
        assert float(e["THD-AUDIT-002"]["value"]) == cfg.warn_ratio
        assert float(e["THD-AUDIT-003"]["value"]) == cfg.bias_threshold

    def test_risk_report_levels(self):
        e = _registry_entries()
        thresholds = risk_report_engine._RISK_THRESHOLDS
        assert float(e["THD-REPORT-001"]["value"]) == thresholds[0][0]
        assert float(e["THD-REPORT-002"]["value"]) == thresholds[1][0]
        assert float(e["THD-REPORT-003"]["value"]) == thresholds[2][0]
        assert float(e["THD-REPORT-004"]["value"]) == risk_report_engine._TREND_THRESHOLD

    def test_operational_risk(self):
        e = _registry_entries()
        assert float(e["THD-OPRISK-001"]["value"]) == DEFAULT_FAILURE_RATE_THRESHOLD
        assert float(e["THD-OPRISK-002"]["value"]) == DEFAULT_LATENCY_P95_THRESHOLD_MS
        assert float(e["THD-OPRISK-003"]["value"]) == _SEVERE_MULTIPLIER

    def test_drift_prediction_sharpe(self):
        """静态登记「Sharpe 30 日 < 0」↔ THD-DRIFT-004 value=0（字符串↔数值语义对）。"""
        e = _registry_entries()
        assert float(e["THD-DRIFT-004"]["value"]) == 0.0
        assert DRIFT_MONITORS[ModelDriftType.PREDICTION].threshold == "< 0"

    def test_gpu_hard_cap_doc_anchor(self):
        """THD-GPU-001=90 为章程级文档锚点（gpu_monitor 探头无码内常量）——存在性+值校验。"""
        e = _registry_entries()
        assert float(e["THD-GPU-001"]["value"]) == 90.0
        assert e["THD-GPU-001"]["status"] == "active"

    def test_adjudicated_retirement_and_deviation(self):
        """2026-08-15 Owner 裁定转正 4 条（原 pending_adjudication）：active + 标准值未漂。"""
        e = _registry_entries()
        for tid, val in (
            ("THD-DEVIATION-003", 0.5),
            ("THD-RETIRE-001", 0.05),
            ("THD-RETIRE-002", 0.0),
            ("THD-RETIRE-003", 1.5),
        ):
            assert e[tid]["status"] == "active"
            assert float(e[tid]["value"]) == val


class TestDesignEntriesExist:
    """3 条 design 条目：存在性 + 状态 + 默认值未漂。"""

    def test_design_entries(self):
        e = _registry_entries()
        for tid, val in (
            ("THD-DRIFT-001", 0.2),
            ("THD-DRIFT-002", 0.4),
        ):
            assert e[tid]["status"] == "design"
            assert float(e[tid]["value"]) == val
        assert e["THD-DRIFT-003"]["status"] == "design"
        assert e["THD-DRIFT-003"]["value"] == "h=4σ"

    def test_entry_total_and_categories(self):
        """总量与分类守卫：35 条 11 类（防误删条目无感流失）。"""
        e = _registry_entries()
        assert len(e) == 35
        cats = {entry["category"] for entry in e.values()}
        assert cats == {
            "drawdown", "health", "gpu", "deviation", "plv", "alert",
            "audit", "report", "oprisk", "drift", "retirement",
        }
