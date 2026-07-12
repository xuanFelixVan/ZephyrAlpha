# [A_test] module_id: SRC-TST-0151 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-308 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.infrastructure.test_drift_extended_e2e
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Drift Detector 扩展 E2E 测试 — 覆盖剩余 5% 差距
===================================================
1. 红白对抗扩展：6个 AI 检测器 + 深度检测器（从 4→12+ 注入场景）
2. 风暴模式 E2E（>50 漂移触发 storm）
3. Hotfix 旁路 E2E（[HOTFIX] commit 72h 抑制）
4. 维护窗口 E2E（冻结期 + 自动恢复）
5. _fallback_to_rollback_handler 无 DeprecationWarning 验证
"""

from __future__ import annotations

import shutil
import tempfile
import uuid
import warnings
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from zephyr.gov_drift.ai_construction_detectors import AIConstructionDetectors
from zephyr.gov_drift.drift_engine import (
    _create_bulk_event,
    _detect_expected_storm,
    load_detector_registry,
)
from zephyr.gov_drift.drift_infrastructure import (
    check_budget_for_gate,
    declare_maintenance_window,
    get_maintenance_window,
)
from zephyr.gov_drift.drift_models import DriftEvent, DriftState


def _make_event(
    dimension: str = "D5_blueprint_code_sync",
    detector_id: str = "test_detector",
    module_id: str = "MOD-INF-023",
) -> DriftEvent:
    return DriftEvent(
        event_id=uuid.uuid4(),
        module_id=module_id,
        detector_id=detector_id,
        drift_dimension=dimension,
        baseline_version="0.1.0",
        state=DriftState.DETECTED,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


# ── 1. AI 检测器扩展红白对抗 ──────────────────────────────────


class TestAIConstructionDetectorsExtended:
    """6 个 AI 检测器逐一注入 + 检出验证。"""

    def setup_method(self):
        self.tmp = tempfile.mkdtemp(prefix="drift_ai_ext_")

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_ai_dead_code_hollow_class(self):
        (Path(self.tmp) / "hollow.py").write_text(
            "class EmptyService:\n    pass\n\nclass AnotherHollow:\n    ...\n",
            encoding="utf-8",
        )
        ai = AIConstructionDetectors()
        events = ai.detect_ai_dead_code(self.tmp)
        assert len(events) >= 1
        assert any("Dead code" in (e.resolution_detail or "") for e in events)

    def test_ai_broken_logic_todo_bomb(self):
        src = "\n".join(["# TODO: fix this"] * 20 + ["def real_work(): pass"])
        (Path(self.tmp) / "todo_heavy.py").write_text(src, encoding="utf-8")
        ai = AIConstructionDetectors()
        events = ai.detect_ai_broken_logic(self.tmp)
        assert len(events) >= 1
        assert any("TODO" in (e.resolution_detail or "") for e in events)

    def test_ai_broken_logic_context_truncation(self):
        (Path(self.tmp) / "truncated.py").write_text(
            "def mega_func(a, b, c, d, e, f, g):\n    pass\n",
            encoding="utf-8",
        )
        ai = AIConstructionDetectors()
        events = ai.detect_ai_broken_logic(self.tmp)
        assert len(events) >= 1
        assert any("truncation" in (e.resolution_detail or "").lower() for e in events)

    def test_ai_duplicate_functionality_cross_file(self):
        dup_code = "def compute_hash(data: bytes) -> str:\n    return 'abc'\n"
        (Path(self.tmp) / "mod_a.py").write_text(dup_code, encoding="utf-8")
        (Path(self.tmp) / "mod_b.py").write_text(dup_code, encoding="utf-8")
        ai = AIConstructionDetectors()
        events = ai.detect_ai_duplicate_functionality(self.tmp)
        assert len(events) >= 1
        assert any("Duplicate" in (e.resolution_detail or "") for e in events)

    def test_ai_session_style_drift_dataclass_init_mix(self):
        (Path(self.tmp) / "mixed_style.py").write_text(
            "from dataclasses import dataclass\n\n"
            "@dataclass\nclass Config:\n    value: int = 0\n\n"
            "class ManualService:\n"
            "    def __init__(self, x: int):\n"
            "        self.x = x\n\n"
            "async def async_handler():\n    pass\n\n"
            "def sync_handler():\n    pass\n",
            encoding="utf-8",
        )
        ai = AIConstructionDetectors()
        events = ai.detect_ai_session_style_drift(self.tmp)
        assert len(events) >= 1

    def test_ai_knowledge_pollution_name_collision(self):
        (Path(self.tmp) / "polluted.py").write_text(
            "class Processor:\n    pass\n\ndef Processor():\n    pass\n",
            encoding="utf-8",
        )
        ai = AIConstructionDetectors()
        events = ai.detect_ai_knowledge_pollution(self.tmp)
        assert len(events) >= 1
        assert any("collision" in (e.resolution_detail or "").lower() for e in events)

    def test_ai_hallucination_import_nonexistent(self):
        (Path(self.tmp) / "bad_import.py").write_text(
            "from nonexistent_module_xyz import Something\nimport also_does_not_exist_abc\n",
            encoding="utf-8",
        )
        ai = AIConstructionDetectors()
        events = ai.detect_ai_hallucination_import(self.tmp)
        assert len(events) >= 1
        assert any("Hallucinated" in (e.resolution_detail or "") for e in events)


# ── 2. 风暴模式 E2E ──────────────────────────────────────────


class TestStormMode:
    """验证 >50 漂移事件触发风暴模式。"""

    def test_storm_detection_bulk_event(self):
        events = [_make_event(dimension=f"D5_dim_{i}") for i in range(55)]
        scan_id = uuid.uuid4()
        bulk = _create_bulk_event(scan_id, events, commit_message="REFACTOR everything")
        assert bulk.is_expected is True
        assert len(bulk.child_event_ids) == 55

    def test_storm_unexpected_without_keyword(self):
        events = [_make_event(dimension=f"D5_dim_{i}") for i in range(55)]
        scan_id = uuid.uuid4()
        bulk = _create_bulk_event(scan_id, events, commit_message="normal commit")
        assert bulk.is_expected is False
        assert bulk.is_unexpected is True

    def test_detect_expected_storm_keywords(self):
        assert _detect_expected_storm("REFACTOR: restructure modules") is True
        assert _detect_expected_storm("MIGRATION: move to new schema") is True
        assert _detect_expected_storm("RENAME: update variable names") is True
        assert _detect_expected_storm("fix: minor bug") is False


# ── 3. Hotfix 旁路 E2E ──────────────────────────────────────


class TestHotfixBypass:
    """验证 [HOTFIX]/[EMERGENCY] commit 旁路逻辑。"""

    def test_hotfix_commit_detected(self):
        from zephyr.gov_drift.drift_hotfix_bypass import HotfixBypass

        bypass = HotfixBypass(project_root=tempfile.gettempdir())
        assert bypass.is_hotfix_commit("[HOTFIX] critical production fix") is True
        assert bypass.is_hotfix_commit("[EMERGENCY] data loss prevention") is True

    def test_normal_commit_not_bypassed(self):
        from zephyr.gov_drift.drift_hotfix_bypass import HotfixBypass

        bypass = HotfixBypass(project_root=tempfile.gettempdir())
        assert bypass.is_hotfix_commit("fix: minor typo") is False
        assert bypass.is_hotfix_commit("feat: add new feature") is False

    def test_hotfix_bypass_in_trigger_recovery(self):
        from zephyr.gov_drift.drift_detector import trigger_recovery

        payload = {
            "module_id": "MOD-INF-023",
            "commit_message": "[HOTFIX] production outage fix",
            "changed_files": [],
        }
        with patch(
            "zephyr.governance.drift_detection.drift_hotfix_bypass.HotfixBypass.is_hotfix_commit",
            return_value=True,
        ):
            result = trigger_recovery(payload)
            assert result["hotfix_bypass"] is True
            assert result["recovery_status"] == "HOTFIX_BYPASSED"


# ── 4. 维护窗口 E2E ─────────────────────────────────────────


class TestMaintenanceWindow:
    """验证维护窗口声明 + 活跃状态 + 自动恢复。"""

    def test_declare_maintenance_window(self):
        window = declare_maintenance_window(hours=2)
        assert window.is_active() is True
        assert window.time_remaining().total_seconds() > 0

    def test_maintenance_window_retrieval(self):
        window = declare_maintenance_window(hours=1)
        retrieved = get_maintenance_window()
        assert retrieved is not None
        assert retrieved.is_active() is True

    def test_maintenance_window_shadow_mode(self):
        window = declare_maintenance_window(hours=1, triggered_by_auto=True)
        assert window.is_shadow_mode is True
        assert window.triggered_by_auto is True


# ── 5. DeprecationWarning 验证 ────────────────────────────────


class TestNoDeprecationWarning:
    """验证 _fallback_to_rollback_handler 不触发 DeprecationWarning。"""

    def test_fallback_no_deprecation_warning(self):
        from zephyr.gov_drift.drift_detector import _fallback_to_rollback_handler

        mock_event = MagicMock()
        mock_event.event_id = uuid.uuid4()
        mock_event.drift_dimension = "D5_unknown"
        mock_event.auto_fixable = False

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            with patch(
                "zephyr.infrastructure.rollback.drift_fix",
                create=True,
            ) as mock_mod:
                mock_mod.DriftFixHandler.side_effect = ImportError("test")
                result = _fallback_to_rollback_handler(mock_event)
                deprecation_warnings = [
                    x
                    for x in w
                    if issubclass(x.category, DeprecationWarning) and "governance.drift_detector" not in str(x.message)
                ]
                assert len(deprecation_warnings) == 0, (
                    f"DeprecationWarning triggered: {[str(x.message) for x in deprecation_warnings]}"
                )
                assert result["action"] == "MANUAL_REQUIRED"


# ── 6. 深度检测器接口验证 ─────────────────────────────────────


class TestDeepDetectorInterfaces:
    """验证深度检测器可正常调用并返回结果。"""

    def test_semantic_drift_concept_cardinality(self):
        from zephyr.gov_drift.drift_result_types import detect_concept_cardinality

        tmp = tempfile.mkdtemp(prefix="drift_semantic_")
        try:
            ya = Path(tmp) / "a.yaml"
            yb = Path(tmp) / "b.yaml"
            ya.write_text("modules:\n  - mod1\n  - mod2\n  - mod3\n", encoding="utf-8")
            yb.write_text("modules:\n  - mod1\n", encoding="utf-8")
            result = detect_concept_cardinality(str(ya), str(yb), "modules")
            assert result.drift_detected is True
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_semantic_drift_enum_value_sync(self):
        from zephyr.gov_drift.drift_result_types import detect_enum_value_sync

        tmp = tempfile.mkdtemp(prefix="drift_enum_")
        try:
            ya = Path(tmp) / "a.yaml"
            yb = Path(tmp) / "b.yaml"
            ya.write_text("states:\n  - DETECTED\n  - RESOLVED\n", encoding="utf-8")
            yb.write_text("states:\n  - DETECTED\n  - FIXED\n", encoding="utf-8")
            result = detect_enum_value_sync(str(ya), str(yb), "states")
            assert result.drift_detected is True
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_registry_all_detectors_active(self):
        detectors = load_detector_registry()
        assert len(detectors) >= 31
        inactive = [d for d in detectors if d.status != "active"]
        assert len(inactive) == 0, f"Inactive detectors: {[d.id for d in inactive]}"

    def test_budget_system_gate_integration(self):
        budget = check_budget_for_gate("MOD-INF-023", tier="P0")
        assert "allowed" in budget
        assert "reason" in budget
