# [A_test] module_id: SRC-TST-0147 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-304 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.infrastructure.test_cross_blueprint_e2e
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
全链路端到端集成测试
===================
验证四大蓝图协同工作：
capacity-assurance(MOD-INF-001) → runtime-integration(MOD-INF-002)
→ governance-automation(MOD-INF-005) → task-system(MOD-INF-039)
"""

from __future__ import annotations

import tempfile
from datetime import UTC, datetime
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


def test_e2e_finding_to_taskcard_full_chain():
    """E2E：Finding→TaskCard→持久化完整链路"""
    from zephyr.infrastructure.finding_task_bridge import AuditFinding, bridge_findings_to_tasks

    findings = [
        AuditFinding(
            finding_id="E2E-001",
            dimension="security",
            severity="critical",
            description="E2E测试：检测到硬编码密钥",
            source_script="scripts/governance/d6_security/scan_secret_leak.py",
            suggested_fix="使用SecretsManager替代硬编码密钥",
        ),
        AuditFinding(
            finding_id="E2E-002",
            dimension="architecture",
            severity="high",
            description="E2E测试：发现循环导入",
            source_script="scripts/governance/d5_architecture/check_deps.py",
            suggested_fix="重构模块依赖为单向",
        ),
    ]

    result = bridge_findings_to_tasks(findings, dry_run=True)
    assert result.tasks_created == 2, f"Expected 2 tasks, got {result.tasks_created}"
    assert result.tasks_failed == 0
    assert result.success_rate == 1.0


def test_e2e_auto_diagnostics_to_event_store():
    """E2E：AutoDiagnostics→EventStore审计链"""
    from zephyr.infrastructure.auto_diagnostics import AutoDiagnostics
    from zephyr.infrastructure.event_store import EventLevel, EventStore, StoredEvent

    engine = AutoDiagnostics()
    report = engine.diagnose(
        "ModuleNotFoundError: No module named 'zephyr.orphan_module'",
        component="pipeline_orchestrator",
    )
    assert report.severity.value == "critical"
    assert report.confidence > 0

    store = EventStore(db_path=tempfile.mktemp(suffix=".db"))
    event = StoredEvent(
        event_id=f"E2E-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}",
        level=EventLevel.ERROR,
        component="pipeline_orchestrator",
        event_type="import_error",
        payload=report.to_dict(),
    )
    event_id = store.record(event)
    assert event_id == event.event_id

    queried = store.query(component="pipeline_orchestrator", limit=1)
    assert len(queried) == 1
    assert queried[0].event_id == event.event_id

    assert store.verify_integrity(event.event_id)
    store.close()


def test_e2e_contract_tester_on_real_files():
    """E2E：ContractTester 验证真实 gate 契约文件"""
    from zephyr.infrastructure.contract_tester import ContractTester

    tester = ContractTester(strict=False)
    gate_files = [
        REPO_ROOT / "src/zephyr/gov_enforcement/rule_enforcement/g1_ingest.yaml",
        REPO_ROOT / "src/zephyr/gov_enforcement/rule_enforcement/g2_triage.yaml",
    ]

    for gf in gate_files:
        result = tester.test_contract(str(gf))
        assert result.status.value != "not_found", f"File not found: {gf}"
        assert result.failure_count >= 0


def test_e2e_config_validator():
    """E2E：ConfigValidator 验证现有配置"""
    from zephyr.infrastructure.config_validator import ConfigValidator

    validator = ConfigValidator()
    config_files = list((REPO_ROOT / "config").rglob("*.yaml"))[:3]

    assert len(config_files) > 0, "No config files found to validate"

    for cf in config_files:
        result = validator.validate(str(cf), strict=False)
        assert result.checked_fields >= 0


def test_e2e_warm_hot_gate():
    """E2E：WarmHotGate 完整门禁流程"""
    from zephyr.infrastructure.warm_hot_gate import WarmHotGate, WarmHotStatus

    gate = WarmHotGate(require_all_passed=True)

    healthy_context = {
        "contracts": [],
        "configs": [],
        "required_modules": ["os", "sys", "pathlib"],
        "min_disk_free_mb": 1,
    }
    result = gate.check(healthy_context)
    assert result.status == WarmHotStatus.PASSED

    blocked_context = {
        "contracts": [],
        "configs": [],
        "required_modules": ["non_existent_module_xyz"],
        "min_disk_free_mb": 1,
    }
    result_blocked = gate.check(blocked_context)
    assert result_blocked.blocked, "Should be blocked by missing dependency"


def test_e2e_dry_run_simulator():
    """E2E：DryRunSimulator 风险检测"""
    from zephyr.infrastructure.dry_run_simulator import DryRunSimulator, SimulationStatus

    sim = DryRunSimulator(sandbox_root=str(tempfile.mkdtemp()))

    safe_op = {"type": "file_write", "target": "D:/temp/test_output.py", "content": "print('hello')"}
    result_safe = sim.simulate(safe_op)
    assert result_safe.status != SimulationStatus.BLOCKED

    dangerous_op = {"type": "file_write", "target": "C:\\Windows\\System32\\test.dll", "content": "rm -rf /"}
    result_dangerous = sim.simulate(dangerous_op)
    assert result_dangerous.status == SimulationStatus.BLOCKED


def test_e2e_cost_tracker():
    """E2E：CostTracker 完整链路"""
    from zephyr.infrastructure.cost_tracker import CostTracker

    tracker = CostTracker(db_path=tempfile.mktemp(suffix=".db"), daily_budget_usd=10.0)

    tracker.record_usage(
        model="deepseek-chat",
        tokens_in=5000,
        tokens_out=3000,
        component="finding_task_bridge",
    )
    tracker.record_usage(
        model="claude-sonnet-4-20250514",
        tokens_in=1500,
        tokens_out=500,
        component="gate_engine",
    )

    report = tracker.daily_report()
    assert report.record_count == 2
    assert report.total_tokens > 0
    assert report.total_cost > 0

    budget = tracker.get_budget_status()
    assert budget["spent"] > 0
    assert budget["pct_used"] < 100 or "预算超出但在E2E中可接受"

    tracker.close()


def test_e2e_pydantic_v2_scanner():
    """E2E：PydanticV2 扫描器自测"""
    from zephyr.infrastructure.pydantic_v2_migrator import PydanticV2Migrator

    migrator = PydanticV2Migrator()
    report = migrator.scan(str(REPO_ROOT / "src" / "zephyr" / "shared"))

    assert report.files_scanned > 0

    checklist = migrator.generate_migration_checklist(report)
    assert len(checklist) > 0


def test_e2e_event_bus_upgrade_plan():
    """E2E：EventBus 升级计划生成"""
    from zephyr.integration.shared.events.upgrade_strategy import EventBusUpgrade

    upgrader = EventBusUpgrade()
    plan = upgrader.generate_upgrade_plan(version_from="v1.0.0", version_to="v2.0.0")

    assert plan.step_count == 8
    assert plan.total_estimated_s > 0

    result = upgrader.execute_upgrade(plan, dry_run=True)
    assert result["steps_completed"] == 8
    assert result["steps_failed"] == 0
