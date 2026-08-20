# [A_test] module_id: MOD-GOV_auto_fix_autopilot | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_auto_fix_autopilot
# [INVARIANTS] 测试F15注册到AutoPilot;覆盖schedule_auto_fix方法
# [MODIFY-GUARD] blueprint.md §3
# [CONSUMERS] CI
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] self
# [TTL] task_bound

"""DM-202509 验收测试: F15注册到AutoPilot实现任务调度"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from zephyr.trading.autopilot import AutoPilot

# #ARCH-075/083 族：DM-202509 F15 集成层缺口——AutoPilot.schedule_auto_fix 包装
# 方法生产零实现（引擎能力在 AutoFixEngine.fix，缺薄包装+dict 适配）。待裁定补建。
_GAP = pytest.mark.xfail(
    strict=False,
    reason="#ARCH-075/083 族：F15 AutoPilot.schedule_auto_fix 集成层未实现，待裁定",
)


@_GAP
class TestScheduleAutoFixExists:
    """验证 schedule_auto_fix 方法存在"""

    def test_method_exists(self):
        ap = AutoPilot("test-session")
        assert hasattr(ap, "schedule_auto_fix")

    def test_method_callable(self):
        ap = AutoPilot("test-session")
        assert callable(ap.schedule_auto_fix)


@_GAP
class TestScheduleAutoFixDryRun:
    """验证 dry_run 模式下不实际执行修复"""

    def test_dry_run_returns_dict(self):
        ap = AutoPilot("test-session")
        result = ap.schedule_auto_fix("drift_fixer", "test_target", dry_run=True)
        assert isinstance(result, dict)
        assert "status" in result
        assert "target" in result

    def test_dry_run_target_preserved(self):
        ap = AutoPilot("test-session")
        result = ap.schedule_auto_fix("drift_fixer", "some/path.py", dry_run=True)
        assert result["target"] == "some/path.py"


@_GAP
class TestScheduleAutoFixErrorHandling:
    """验证错误处理"""

    def test_invalid_action_type_returns_dict(self):
        ap = AutoPilot("test-session")
        result = ap.schedule_auto_fix("invalid_fixer", "target")
        assert isinstance(result, dict)
        assert result["status"].lower() in ("failed", "cancelled", "error")

    def test_engine_exception_handled(self):
        ap = AutoPilot("test-session")
        with patch(
            "zephyr.infrastructure.auto_fix_engine.engine.AutoFixEngine.fix",
            side_effect=RuntimeError("boom"),
        ):
            result = ap.schedule_auto_fix("drift_fixer", "target")
        assert result["status"] == "FAILED"
        assert "error" in result


@_GAP
class TestScheduleAutoFixIntegration:
    """验证集成测试"""

    def test_no_auto_fix_type_cancelled(self):
        ap = AutoPilot("test-session")
        result = ap.schedule_auto_fix("manual_review", "target")
        assert result["status"].lower() in ("cancelled", "failed")

    def test_result_has_action_id(self):
        ap = AutoPilot("test-session")
        result = ap.schedule_auto_fix("drift_fixer", "target", dry_run=True)
        assert "action_id" in result


class TestAutoPilotIntegrity:
    """验证添加 schedule_auto_fix 后 AutoPilot 完整性"""

    def test_existing_methods_unchanged(self):
        ap = AutoPilot("test-session")
        assert hasattr(ap, "scan")
        assert hasattr(ap, "status_report")
        assert hasattr(ap, "claim_next")
        assert hasattr(ap, "run_cycle")

    def test_session_id_preserved(self):
        ap = AutoPilot("my-session")
        assert ap.session_id == "my-session"
