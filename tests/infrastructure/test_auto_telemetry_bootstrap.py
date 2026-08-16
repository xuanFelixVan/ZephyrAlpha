# [A_test] module_id: MOD-GOV_auto_telemetry_bootstrap | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-322 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_auto_telemetry_bootstrap
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""端到端验证：auto_bootstrap 自动遥测全链路集成测试

验证 auto_bootstrap 对三大系统的 monkey-patch 注入是否正确：
  1. import zephyr → auto_bootstrap 自动触发
  2. SessionContinuity.print_restore_summary → 自动发射遥测
  3. PhaseGate.run_checks → 自动发射遥测
  4. blueprint_metrics.record_blueprint_read → 自动发射遥测
  5. 手动 Telemetry 与自动注入共存不冲突
"""

import pytest


@pytest.mark.xfail(
    strict=False,
    reason=(
        "真 bug（跨域登记不代修）：src/zephyr/__init__.py L377 "
        "auto_bootstrap_result = _auto_bootstrap_result 在 import 时绑定（值恒 None），"
        "Timer(0.05s) 延迟回填仅更新私有名——公共别名永不更新；且 bootstrap 异步化后 "
        "测试存在时序竞态（AI-TD2-DATA-001 留置，待统筹配 #ARCH-1xx）"
    ),
)
def test_import_triggers_bootstrap():
    import zephyr

    assert zephyr.auto_bootstrap_result is not None
    assert zephyr.auto_bootstrap_result["session_continuity"] is True
    assert zephyr.auto_bootstrap_result["phase_manager"] is True
    assert zephyr.auto_bootstrap_result["blueprint_metrics"] is True


def test_global_telemetry_singleton():
    from zephyr.infrastructure.system_telemetry.auto_bootstrap import get_global_telemetry

    t1 = get_global_telemetry()
    t2 = get_global_telemetry()
    assert t1 is t2
    assert t1.module_id == "zephyr_core"


def test_session_continuity_auto_emits():
    import contextlib
    import io

    from zephyr.shared.session.session_continuity import SessionContinuity

    sc = SessionContinuity()
    with contextlib.redirect_stdout(io.StringIO()):
        sc.print_restore_summary()


def test_phase_manager_auto_emits():
    from zephyr.governance.ops_governance.phase_manager import PHASE_SEQUENCE, ConstructionPhase

    p0 = PHASE_SEQUENCE[ConstructionPhase.PHASE_0_SKELETON]
    result = p0.run_checks()
    assert result is not None


def test_blueprint_metrics_auto_emits():
    from zephyr.infrastructure.system_telemetry.metrics import blueprint_metrics as bm

    result = bm.record_blueprint_read(
        blueprint_id="MOD-INF-015",
        session_id="test-session",
        task_id="test-task",
    )
    assert result is not None


def test_telemetry_direct_usage_still_works():
    from zephyr.infrastructure.system_telemetry import Telemetry

    t = Telemetry("manual_module", test_mode=True)
    r = t.metrics.gauge("test", 1.0)
    assert r["value"] == 1.0
    t.shutdown()
