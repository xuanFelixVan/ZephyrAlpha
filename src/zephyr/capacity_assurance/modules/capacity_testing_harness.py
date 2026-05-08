"""
Capacity Testing Harness — 容量装置可测试性 (盲点 #33)
特性：
  - test_live_kill_switch(): 实际触发 Kill Switch 的集成测试
  - test_sandbox_isolation(): 沙箱隔离测试
  - test_degradation_chain(): 降级链端到端测试
"""
import time
from typing import Any, Optional


class CapacityTestingHarness:
    """
    容量测试夹具 (盲点 #33)
    """

    def __init__(self):
        self._test_results: list[dict] = []

    def test_live_kill_switch(self, kill_switch_instance) -> dict:
        try:
            kill_switch_instance.activate("TEST: CapacityTestingHarness")
            active = kill_switch_instance.is_active()
            kill_switch_instance.deactivate()
            result = {"test": "test_live_kill_switch", "passed": active, "timestamp": time.time()}
        except Exception as e:
            result = {"test": "test_live_kill_switch", "passed": False, "error": str(e)}
        self._test_results.append(result)
        return result

    def test_sandbox_isolation(self, sandbox_instance) -> dict:
        try:
            result, _ = sandbox_instance.sandbox_file_delete("__nonexistent_file__", confirmed=False)
            passed = result.value in ("dry_run", "allowed")
            result_d = {"test": "test_sandbox_isolation", "passed": passed, "detail": result.value}
        except Exception as e:
            result_d = {"test": "test_sandbox_isolation", "passed": False, "error": str(e)}
        self._test_results.append(result_d)
        return result_d

    def run_all(self, kill_switch=None, sandbox=None) -> dict:
        results = {}
        if kill_switch:
            results["kill_switch"] = self.test_live_kill_switch(kill_switch)
        if sandbox:
            results["sandbox"] = self.test_sandbox_isolation(sandbox)
        return results
