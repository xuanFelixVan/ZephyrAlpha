# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] tests.governance.test_alert_threshold_consistency
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] 注册表阈值=代码默认值（漂移即失败——注册表不许说谎）；active 条目全有代码锚点getter；design 条目存在性校验；注册表缺失/畸形时目标模块 fail-closed
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即漂移证据（哪条 THD/代码值/注册表值）
# [TESTS] self
# [A_module] module_id=MOD-GOVERNANCE | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""REG-ATH-001 告警阈值注册表 ↔ 代码一致性对账测试（55 号 §3.3 配套，#ARCH-MON-001）.

裁定模型（2026-08-17 AI-THD-001 统读改造后，对齐 tracker #87 完工口径）：
  存量 9 模块阈值默认值已统读——运行真源=alert_threshold_registry.yaml
  （fail-closed 经 shared/alerts/threshold_loader.py 加载，禁止码内第二真源）；
  本对账测试机器锁定「注册表值=代码默认值」接线完整性（防加载接线断裂/回退硬编码），
  并含红队用例——注册表缺文件/缺条目/畸形 YAML/类型错误时目标模块 fail-closed 报错。
  新模块（MOD-RK-23/退役评估器）运行时已 fail-closed 直读注册表（改表即生效），
  不在本对账范围（其一致性由自身加载测试覆盖）。

覆盖 32 条 active 条目全量对账 + 3 条 design 条目存在性校验 + 红队 fail-closed 四类。
（2026-08-15 v1.1.0：4 条 pending_adjudication 经 Owner 裁定转正 active——
THD-RETIRE-001/002/003 + THD-DEVIATION-003，值不变，并入 active 对账。）
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import zephyr.backtest.core.decision_gate as decision_gate
import zephyr.governance.lifecycle_governance.post_live_verification as post_live_verification
import zephyr.reporting.risk_report_engine as risk_report_engine
import zephyr.risk.core.alert_generator as alert_generator
import zephyr.risk.core.daily_auditor as daily_auditor
import zephyr.risk.core.drawdown_tracker as drawdown_tracker
import zephyr.risk.core.operational_risk_monitor as oprisk_module
import zephyr.shared.alerts.alert_escalation as alert_escalation
from zephyr.backtest.core.decision_gate import DecisionGateConfig
from zephyr.gov_drift.detector_core.model_drift_monitor import (
    DRIFT_MONITORS,
    ModelDriftType,
)
from zephyr.governance.lifecycle_governance.post_live_verification import (
    PLV_CHECKS,
    PLVCheck,
)
from zephyr.risk.core.alert_generator import AlertGenerator
from zephyr.risk.core.daily_auditor import AuditConfig
from zephyr.risk.core.drawdown_tracker import DrawdownTrackerConfig
from zephyr.risk.core.operational_risk_monitor import (
    _SEVERE_MULTIPLIER,
    DEFAULT_FAILURE_RATE_THRESHOLD,
    DEFAULT_LATENCY_P95_THRESHOLD_MS,
)
from zephyr.risk.core.strategy_deviation_monitor import ALERT_THRESHOLD_REGISTRY_PATH
from zephyr.shared.alerts.alert_escalation import AlertEscalation
from zephyr.shared.alerts.threshold_loader import AlertThresholdConfigError
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
        # 统读后默认经注册表 fail-closed 加载：默认构造 → 注册表值（THD-ALERT-001=300 秒）
        dedup_default = AlertGenerator()._dedup_window
        assert float(e["THD-ALERT-001"]["value"]) == dedup_default.total_seconds()
        # pydantic default_factory 构造期加载（THD-ALERT-002=300 秒）
        esc_default = AlertEscalation().auto_escalate_after_seconds
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


# ── 红队：fail-closed 实证（统读后安全网，tracker #87 验收①）──────────────

#: 9 个统读模块的统一加载入口（每模块的 _load_*/build_* 即其默认值真源加载路径）
_FAIL_CLOSED_LOADERS = {
    "drawdown_tracker": drawdown_tracker._load_drawdown_thresholds,
    "health_monitor": health_monitor._load_pressure_thresholds,
    "decision_gate": decision_gate._load_deviation_thresholds,
    "post_live_verification": post_live_verification.build_plv_checks,
    "alert_generator": alert_generator._load_dedup_window_seconds,
    "alert_escalation": alert_escalation._load_auto_escalate_after_seconds,
    "daily_auditor": daily_auditor._load_audit_thresholds,
    "risk_report_engine": risk_report_engine._load_report_thresholds,
    "operational_risk_monitor": oprisk_module._load_oprisk_thresholds,
}

#: 各模块加载映射的首个必需条目（类型畸形攻击的注入点）
_FIRST_TID = {
    "drawdown_tracker": "THD-DRAWDOWN-001",
    "health_monitor": "THD-HEALTH-001",
    "decision_gate": "THD-DEVIATION-001",
    "post_live_verification": "THD-PLV-001",
    "alert_generator": "THD-ALERT-001",
    "alert_escalation": "THD-ALERT-002",
    "daily_auditor": "THD-AUDIT-001",
    "risk_report_engine": "THD-REPORT-001",
    "operational_risk_monitor": "THD-OPRISK-001",
}

#: 类型畸形攻击值（缺省 "abc"——float cast 拒绝；int cast 拒浮点/字符串；str cast 拒数值）
_TYPE_ERROR_VALUE = {
    "health_monitor": 70.5,      # int cast 拒绝浮点（防 90.5→90 静默截断）
    "alert_escalation": "abc",   # int cast 拒绝字符串
    "post_live_verification": 1,  # str cast 拒绝数值（PLV 字符串规约不数值化）
}

#: 全量合法注册表夹具（9 模块全部必需条目，类型各异正确）
_GOOD_REGISTRY_ENTRIES = [
    {"threshold_id": "THD-DRAWDOWN-001", "value": 0.05},
    {"threshold_id": "THD-DRAWDOWN-002", "value": 0.10},
    {"threshold_id": "THD-DRAWDOWN-003", "value": 0.15},
    {"threshold_id": "THD-HEALTH-001", "value": 70},
    {"threshold_id": "THD-HEALTH-002", "value": 80},
    {"threshold_id": "THD-HEALTH-003", "value": 90},
    {"threshold_id": "THD-HEALTH-004", "value": 90},
    {"threshold_id": "THD-DEVIATION-001", "value": 0.30},
    {"threshold_id": "THD-DEVIATION-002", "value": 0.50},
    {"threshold_id": "THD-PLV-001", "value": "±1%"},
    {"threshold_id": "THD-PLV-002", "value": "±0.5%"},
    {"threshold_id": "THD-PLV-003", "value": "≥limits"},
    {"threshold_id": "THD-PLV-004", "value": "checksum verified"},
    {"threshold_id": "THD-PLV-005", "value": "±$5/1000trades"},
    {"threshold_id": "THD-ALERT-001", "value": 300},
    {"threshold_id": "THD-ALERT-002", "value": 300},
    {"threshold_id": "THD-AUDIT-001", "value": 0.001},
    {"threshold_id": "THD-AUDIT-002", "value": 0.8},
    {"threshold_id": "THD-AUDIT-003", "value": 0.1},
    {"threshold_id": "THD-REPORT-001", "value": 0.3},
    {"threshold_id": "THD-REPORT-002", "value": 0.6},
    {"threshold_id": "THD-REPORT-003", "value": 0.8},
    {"threshold_id": "THD-REPORT-004", "value": 0.05},
    {"threshold_id": "THD-OPRISK-001", "value": 0.05},
    {"threshold_id": "THD-OPRISK-002", "value": 500.0},
    {"threshold_id": "THD-OPRISK-003", "value": 2.0},
]


class TestFailClosedRedTeam:
    """红队 fail-closed 实证：注册表异常时 9 个统读模块一律报错（禁止静默回退硬编码）。

    四类攻击面全模块参数化：① 注册表文件不存在 ② YAML 畸形 ③ 缺条目 ④ 类型畸形。
    """

    @staticmethod
    def _write_registry(tmp_path: Path, entries: list[dict]) -> Path:
        p = tmp_path / "alert_threshold_registry.yaml"
        p.write_text(
            yaml.safe_dump({"thresholds": entries}, allow_unicode=True),
            encoding="utf-8",
        )
        return p

    @pytest.mark.parametrize("module_name", sorted(_FAIL_CLOSED_LOADERS))
    def test_missing_file_fail_closed(self, module_name: str, tmp_path: Path):
        with pytest.raises(AlertThresholdConfigError):
            _FAIL_CLOSED_LOADERS[module_name](tmp_path / "nonexistent.yaml")

    @pytest.mark.parametrize("module_name", sorted(_FAIL_CLOSED_LOADERS))
    def test_malformed_yaml_fail_closed(self, module_name: str, tmp_path: Path):
        bad = tmp_path / "malformed.yaml"
        bad.write_text("key: [unclosed\n", encoding="utf-8")
        with pytest.raises(AlertThresholdConfigError):
            _FAIL_CLOSED_LOADERS[module_name](bad)

    @pytest.mark.parametrize("module_name", sorted(_FAIL_CLOSED_LOADERS))
    def test_missing_entry_fail_closed(self, module_name: str, tmp_path: Path):
        reg = self._write_registry(
            tmp_path, [{"threshold_id": "THD-UNRELATED-001", "value": 1.0}]
        )
        with pytest.raises(AlertThresholdConfigError):
            _FAIL_CLOSED_LOADERS[module_name](reg)

    @pytest.mark.parametrize("module_name", sorted(_FAIL_CLOSED_LOADERS))
    def test_type_error_fail_closed(self, module_name: str, tmp_path: Path):
        entries = [dict(e) for e in _GOOD_REGISTRY_ENTRIES]
        target = _FIRST_TID[module_name]
        bad_value = _TYPE_ERROR_VALUE.get(module_name, "abc")
        for entry in entries:
            if entry["threshold_id"] == target:
                entry["value"] = bad_value
        reg = self._write_registry(tmp_path, entries)
        with pytest.raises(AlertThresholdConfigError):
            _FAIL_CLOSED_LOADERS[module_name](reg)

    @pytest.mark.parametrize("module_name", sorted(_FAIL_CLOSED_LOADERS))
    def test_bool_value_fail_closed(self, module_name: str, tmp_path: Path):
        """bool 攻击面：YAML `value: true` 笔误一律 fail-closed。

        float cast 拒 bool（防静默 1.0）；int cast 拒 bool（isinstance 守护）；
        str cast 拒 bool（非字符串）——三种 cast 布尔值全拒。
        """
        entries = [dict(e) for e in _GOOD_REGISTRY_ENTRIES]
        target = _FIRST_TID[module_name]
        for entry in entries:
            if entry["threshold_id"] == target:
                entry["value"] = True
        reg = self._write_registry(tmp_path, entries)
        with pytest.raises(AlertThresholdConfigError):
            _FAIL_CLOSED_LOADERS[module_name](reg)
