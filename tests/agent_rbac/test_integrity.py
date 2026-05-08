"""完整性自检测试."""
from __future__ import annotations

import pytest
from zephyr.agent_rbac.integrity_self_check import IntegritySelfCheck


class TestIntegrity:
    def test_check_all_modules(self):
        checker = IntegritySelfCheck()
        results = checker.check_all()
        assert len(results) >= 55
        assert all(r.passed for r in results)

    def test_summary(self):
        checker = IntegritySelfCheck()
        results = checker.check_all()
        summary = checker.summary()
        assert summary["total_modules"] >= 55
        assert summary["passed"] >= 55
        assert summary["all_ok"] is True
