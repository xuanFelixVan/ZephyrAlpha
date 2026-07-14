# [A_test] module_id: SRC-TST-0360 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md | §test
# [MODULE] tests.test_audit_orchestrator_e2e
# [INVARIANTS] AuditAdmissionController 5模块健康检查覆盖; ResourceAwarePool 双池路由正确
# [MODIFY-GUARD] audit_orchestrator/blueprint.md; test_audit_orchestrator_e2e.py
# [CONSUMERS] CI; pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; RuntimeError on submit after shutdown
# [TESTS] tests/test_audit_orchestrator_e2e.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

audit_orchestrator = pytest.importorskip("zephyr.gov_audit")
AuditAdmissionController = audit_orchestrator.AuditAdmissionController
AdmissionResult = audit_orchestrator.AdmissionResult
ResourceAwarePool = audit_orchestrator.ResourceAwarePool
PoolStats = audit_orchestrator.PoolStats


@pytest.mark.e2e
class TestAuditAdmissionControllerE2E:
    def test_full_health_check(self):
        controller = AuditAdmissionController()
        health = controller.full_health_check()
        assert isinstance(health, dict)
        expected_keys = {
            "audit-trail",
            "semantic-auditor",
            "orphan-judge",
            "red-blue-validator",
            "behavioral-auditor",
        }
        assert set(health.keys()) == expected_keys
        for key in expected_keys:
            assert isinstance(health[key], bool)

    def test_check_admission_all_healthy(self):
        with patch.object(AuditAdmissionController, "full_health_check") as mock_hc:
            mock_hc.return_value = {
                "audit-trail": True,
                "semantic-auditor": True,
                "orphan-judge": True,
                "red-blue-validator": True,
                "behavioral-auditor": True,
            }
            controller = AuditAdmissionController()
            result = controller.check_admission("write", "/some/path")
            assert isinstance(result, AdmissionResult)
            assert result.allowed is True
            assert result.reason == ""
            assert len(result.checks_passed) == 5
            assert len(result.checks_failed) == 0
            assert len(result.blocked_by) == 0

    def test_check_admission_module_down(self):
        with patch.object(AuditAdmissionController, "full_health_check") as mock_hc:
            mock_hc.return_value = {
                "audit-trail": True,
                "semantic-auditor": True,
                "orphan-judge": False,
                "red-blue-validator": True,
                "behavioral-auditor": True,
            }
            controller = AuditAdmissionController()
            controller._modules["orphan-judge"] = None
            result = controller.check_admission("write", "/some/path")
            assert isinstance(result, AdmissionResult)
            assert result.allowed is False
            assert "orphan-judge" in result.reason
            assert "orphan-judge" in result.checks_failed
            assert "orphan-judge" in result.blocked_by
            assert "audit-trail" in result.checks_passed
            assert "semantic-auditor" in result.checks_passed
            assert "red-blue-validator" in result.checks_passed
            assert "behavioral-auditor" in result.checks_passed

    def test_check_audit_trail_health(self):
        controller = AuditAdmissionController()
        result = controller.check_audit_trail_health()
        assert isinstance(result, bool)

    def test_check_semantic_auditor_health(self):
        controller = AuditAdmissionController()
        result = controller.check_semantic_auditor_health()
        assert isinstance(result, bool)

    def test_check_orphan_judge_health(self):
        controller = AuditAdmissionController()
        result = controller.check_orphan_judge_health()
        assert isinstance(result, bool)


@pytest.mark.e2e
class TestResourceAwarePoolE2E:
    def test_cpu_pool_routing(self):
        pool = ResourceAwarePool(cpu_workers=2, gpu_workers=1)
        try:
            future = pool.submit("file_scan", lambda: "cpu_result")
            result = future.result(timeout=5)
            assert result == "cpu_result"
            assert future in pool._cpu_futures
        finally:
            pool.shutdown()

    def test_gpu_pool_routing(self):
        pool = ResourceAwarePool(cpu_workers=2, gpu_workers=1)
        try:
            future = pool.submit("llm_inference", lambda: "gpu_result")
            result = future.result(timeout=5)
            assert result == "gpu_result"
            assert future in pool._gpu_futures
        finally:
            pool.shutdown()

    def test_submit_and_get_result(self):
        pool = ResourceAwarePool(cpu_workers=2, gpu_workers=1)
        try:

            def add(a, b):
                return a + b

            future = pool.submit("computation", add, 3, 7)
            assert future.result(timeout=5) == 10
        finally:
            pool.shutdown()

    def test_stats(self):
        pool = ResourceAwarePool(cpu_workers=2, gpu_workers=1)
        try:
            import time

            barrier_event = MagicMock()

            def slow_task():
                time.sleep(0.5)
                return 42

            pool.submit("file_scan", slow_task)
            pool.submit("llm_inference", slow_task)
            stats = pool.stats()
            assert isinstance(stats, PoolStats)
            assert stats.cpu_active >= 0
            assert stats.gpu_active >= 0
            assert stats.cpu_pending >= 0
            assert stats.gpu_pending >= 0
        finally:
            pool.shutdown()

    def test_shutdown(self):
        pool = ResourceAwarePool(cpu_workers=2, gpu_workers=1)
        pool.submit("file_scan", lambda: "done")
        pool.shutdown()
        assert pool._shutdown is True
        with pytest.raises(RuntimeError, match="shut down"):
            pool.submit("file_scan", lambda: "should_fail")

    def test_batch_submit(self):
        pool = ResourceAwarePool(cpu_workers=4, gpu_workers=2)
        try:
            cpu_futures = []
            gpu_futures = []
            for i in range(4):
                cpu_futures.append(pool.submit("file_scan", lambda x: x * 2, i))
            for i in range(3):
                gpu_futures.append(pool.submit("semantic_analysis", lambda x: x + 10, i))

            cpu_results = [f.result(timeout=10) for f in cpu_futures]
            gpu_results = [f.result(timeout=10) for f in gpu_futures]

            assert cpu_results == [0, 2, 4, 6]
            assert gpu_results == [10, 11, 12]
            assert len(pool._cpu_futures) == 4
            assert len(pool._gpu_futures) == 3
        finally:
            pool.shutdown()
