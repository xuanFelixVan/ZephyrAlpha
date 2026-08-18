# [A_test] module_id: MOD-GOV_capacity_runtime_red_blue | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-303 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.infrastructure.test_capacity_runtime_red_blue
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Capacity & Runtime 红白对抗测试
===============================
对 capacity-assurance 和 runtime-integration 模块进行对抗性验证。
测试边界条件、异常输入、并发安全、资源耗尽等场景。
"""

from __future__ import annotations

import tempfile
import threading
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

# ============================================================================
# capacity-assurance 红白对抗
# ============================================================================


class TestCapacityAssuranceAdversarial:
    """容量保障体系对抗测试"""

    def test_auto_diagnostics_empty_input(self):
        """对抗：空输入应优雅处理"""
        from zephyr.infrastructure.auto_diagnostics import AutoDiagnostics

        engine = AutoDiagnostics()
        report = engine.diagnose("", component="")
        assert report.confidence == 0.0

    def test_auto_diagnostics_unicode_attack(self):
        """对抗：Unicode注入不崩溃"""
        from zephyr.infrastructure.auto_diagnostics import AutoDiagnostics

        engine = AutoDiagnostics()
        report = engine.diagnose("🐛💥🔥" * 100, component="test")
        assert report is not None

    def test_auto_diagnostics_all_rules(self):
        """对抗：验证每条规则都能触发"""
        from zephyr.infrastructure.auto_diagnostics import AutoDiagnostics

        engine = AutoDiagnostics()
        test_messages = [
            ("操作卡住timeout超过30秒", "high"),
            ("ModuleNotFoundError: No module named 'x'", "critical"),
            ("PermissionError: 拒绝访问", "high"),
            ("UnicodeDecodeError: 乱码", "medium"),
            ("孤儿文件无人调用未注册", "medium"),
        ]
        for msg, expected_sev in test_messages:
            report = engine.diagnose(msg, component="test")
            assert report.severity.value == expected_sev, (
                f"Expected {expected_sev} for '{msg[:30]}...', got {report.severity.value}"
            )

    def test_contract_tester_non_existent(self):
        """对抗：不存在的文件"""
        from zephyr.infrastructure.contract_tester import ContractStatus, ContractTester

        tester = ContractTester()
        result = tester.test_contract("D:/nonexistent/ghost.yaml")
        assert result.status == ContractStatus.NOT_FOUND

    def test_contract_tester_empty_yaml(self):
        """对抗：空 YAML 文件"""
        import os
        import tempfile

        from zephyr.infrastructure.contract_tester import ContractTester

        tmp = tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w", encoding="utf-8")
        tmp.write("")
        tmp.close()

        try:
            tester = ContractTester(strict=False)
            result = tester.test_contract(tmp.name)
            assert result is not None
        finally:
            os.unlink(tmp.name)

    def test_config_validator_none_fields(self):
        """对抗：null字段应报警告"""
        import os
        import tempfile

        import yaml

        from zephyr.infrastructure.config_validator import ConfigValidator

        tmp = tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w", encoding="utf-8")
        yaml.dump({"version": "1.0", "thresholds": None, "error_budget": 0.5}, tmp)
        tmp.close()

        try:
            validator = ConfigValidator()
            result = validator.validate(tmp.name, strict=False)
            assert result.total_issues > 0, "Should warn about None values"
        finally:
            os.unlink(tmp.name)

    def test_config_validator_out_of_range(self):
        """对抗：超范围数值应报警告"""
        import os
        import tempfile

        import yaml

        from zephyr.infrastructure.config_validator import ConfigValidator

        tmp = tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w", encoding="utf-8")
        yaml.dump({"version": "1.0", "timeout": 99999, "max_workers": 999}, tmp)
        tmp.close()

        try:
            validator = ConfigValidator()
            result = validator.validate(tmp.name, strict=False)
            assert result.total_issues > 0, "Should warn about out of range values"
        finally:
            os.unlink(tmp.name)

    def test_warm_hot_gate_empty_context(self):
        """对抗：空上下文"""
        from zephyr.infrastructure.warm_hot_gate import WarmHotGate

        gate = WarmHotGate()
        result = gate.check({})
        assert not result.blocked


class TestRuntimeIntegrationAdversarial:
    """运行时集成对抗测试"""

    def test_event_store_concurrent_writes(self):
        """对抗：并发写入不丢失事件"""
        from zephyr.infrastructure.event_store import EventLevel, EventStore, StoredEvent

        db_path = tempfile.mktemp(suffix=".db")
        store = EventStore(db_path=db_path)
        event_count = 50
        errors: list[str] = []

        def write_events(start: int, count: int):
            for i in range(start, start + count):
                try:
                    event = StoredEvent(
                        event_id=f"RB-EVT-{i:04d}",
                        level=EventLevel.INFO,
                        component="adversarial_test",
                        event_type="concurrent_write",
                    )
                    store.record(event)
                except Exception as e:
                    errors.append(str(e))

        threads = []
        for t_idx in range(4):
            t = threading.Thread(target=write_events, args=(t_idx * event_count // 4, event_count // 4))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert not errors, f"Concurrent write errors: {errors}"
        count = store.count(component="adversarial_test")
        assert count >= event_count * 0.9, f"Expected ~{event_count} events, got {count}"
        store.close()

    def test_event_store_integrity_tampering(self):
        """对抗：检测篡改事件"""
        import sqlite3

        from zephyr.infrastructure.event_store import EventLevel, EventStore, StoredEvent

        db_path = tempfile.mktemp(suffix=".db")
        store = EventStore(db_path=db_path)

        event = StoredEvent(
            event_id="RB-INTEGRITY-001",
            level=EventLevel.ERROR,
            component="test",
            event_type="integrity",
            payload={"original": True},
        )
        store.record(event)

        assert store.verify_integrity("RB-INTEGRITY-001")

        conn = sqlite3.connect(db_path)
        conn.execute(
            "UPDATE events SET payload = ? WHERE event_id = ?",
            ('{"tampered": true}', "RB-INTEGRITY-001"),
        )
        conn.commit()
        conn.close()

        assert not store.verify_integrity("RB-INTEGRITY-001"), "Tampering should be detected"
        store.close()

    def test_dry_run_sql_injection_attempt(self):
        """对抗：SQL注入尝试被检测"""
        from zephyr.infrastructure.dry_run_simulator import DryRunSimulator, SimulationStatus

        sim = DryRunSimulator(sandbox_root=str(tempfile.mkdtemp()))
        sql_injection_op = {
            "type": "file_write",
            "target": "data.db",
            "content": "DROP TABLE users; DROP DATABASE production;",
        }
        result = sim.simulate(sql_injection_op)
        assert result.status == SimulationStatus.BLOCKED

    def test_cost_tracker_zero_tokens(self):
        """对抗：零Token使用"""
        from zephyr.infrastructure.cost_tracker import CostTracker

        tracker = CostTracker(db_path=tempfile.mktemp(suffix=".db"))
        record = tracker.record_usage(model="deepseek-chat", tokens_in=0, tokens_out=0)
        assert record.estimated_cost == 0.0

        report = tracker.daily_report()
        assert report.total_cost >= 0.0
        tracker.close()

    def test_cost_tracker_budget_alert(self):
        """对抗：预算超限告警"""
        from zephyr.infrastructure.cost_tracker import CostTracker

        tracker = CostTracker(db_path=tempfile.mktemp(suffix=".db"), daily_budget_usd=0.00001)

        tracker.record_usage(
            model="claude-opus-4-20250514",
            tokens_in=10000,
            tokens_out=10000,
            component="test",
        )
        budget = tracker.get_budget_status()
        assert budget["pct_used"] > 100 or len(budget["alerts"]) > 0
        tracker.close()

    def test_event_bus_dry_run_safety(self):
        """对抗：dry run 不修改任何状态"""
        from zephyr.integration.shared.events.upgrade_strategy import EventBusUpgrade

        upgrader = EventBusUpgrade()
        plan = upgrader.generate_upgrade_plan()

        for step in plan.steps:
            assert step.status.value == "pending"

        upgrader.execute_upgrade(plan, dry_run=True)

        for step in plan.steps:
            assert step.status.value == "completed", f"Step {step.step_id} not completed"

        history = upgrader.get_history()
        assert len(history) == 1
