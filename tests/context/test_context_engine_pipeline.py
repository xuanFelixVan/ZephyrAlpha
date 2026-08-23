# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] tests.context.test_context_engine_pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/context/test_context_engine_pipeline.py -q
# [TTL] permanent

"""Context Engine 四段流水线（MOD-CONTEXT_ENGINE 补齐）单元测试——
build/compress/validate/inject + register_rules + adjust_strategy。"""

from __future__ import annotations

import os
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from zephyr.shared.context.context_engine import (
    ContextBundle,
    ContextEngine,
    InjectResult,
    ValidationReport,
)


@pytest.fixture()
def tmp_project():
    d = tempfile.mkdtemp(prefix="ce_pipe_test_")
    os.makedirs(os.path.join(d, "docs"), exist_ok=True)
    with open(os.path.join(d, "docs", "a.md"), "w", encoding="utf-8") as f:
        f.write("# 架构决策\n" + "内容行\n" * 50)
    with open(os.path.join(d, "docs", "b.md"), "w", encoding="utf-8") as f:
        f.write("# 经验教训\n" + "教训行\n" * 30)
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


def _manifest():
    return [
        {"file_path": "docs/a.md", "reason": "arch", "slot": "architecture"},
        {"file_path": "docs/b.md", "reason": "lesson", "slot": "lessons"},
    ]


def _manifest_with_missing():
    return _manifest() + [{"file_path": "docs/missing.md", "reason": "gap", "slot": "lessons"}]


class TestBuild:
    def test_build_groups_slices_into_slots(self, tmp_project):
        eng = ContextEngine(project_root=tmp_project)
        bundle = eng.build("T-1", _manifest())
        assert isinstance(bundle, ContextBundle)
        assert set(bundle.slots) == {"architecture", "lessons"}
        assert bundle.slots["lessons"].token_count > 0
        assert bundle.total_token_count > 0
        assert len(bundle.bundle_hash) == 64
        assert bundle.degraded is False

    def test_build_marks_degraded_when_source_missing(self, tmp_project):
        eng = ContextEngine(project_root=tmp_project)
        bundle = eng.build("T-1", _manifest_with_missing())
        assert bundle.degraded is True
        assert any("missing" in r for r in bundle.degrade_reasons)

    def test_slot_overrides_change_budget_split(self, tmp_project):
        eng = ContextEngine(project_root=tmp_project, max_tokens=200)
        bundle = eng.build("T-1", _manifest(), slot_overrides={"architecture": 0.9, "lessons": 0.1})
        arch = bundle.slots["architecture"].token_count
        les = bundle.slots["lessons"].token_count
        assert arch > les


class TestCompress:
    def test_truncate_strategy_respects_budget(self, tmp_project):
        eng = ContextEngine(project_root=tmp_project)
        bundle = eng.build("T-1", _manifest())
        out = eng.compress(bundle, token_budget=20, strategy="truncate")
        assert out.total_token_count <= 20
        assert out.compression_ratio is not None and out.compression_ratio < 1.0

    def test_llm_summary_falls_back_to_rule_based(self, tmp_project):
        eng = ContextEngine(project_root=tmp_project)
        bundle = eng.build("T-1", _manifest())
        out = eng.compress(bundle, token_budget=30, strategy="llm_summary")
        assert any("DEGRADE-002" in r for r in out.degrade_reasons)
        assert out.total_token_count <= 30

    def test_source_traces_preserved(self, tmp_project):
        eng = ContextEngine(project_root=tmp_project)
        bundle = eng.build("T-1", _manifest())
        out = eng.compress(bundle, token_budget=10, strategy="rule_based")
        traces = [t for s in out.slots.values() for t in s.source_traces]
        assert any("docs/a.md" in t for t in traces)


class TestValidate:
    def test_valid_bundle_passes(self, tmp_project):
        eng = ContextEngine(project_root=tmp_project)
        bundle = eng.build("T-1", _manifest())
        report = eng.validate(bundle)
        assert isinstance(report, ValidationReport)
        assert report.passed is True
        assert report.token_within_budget is True

    def test_over_budget_bundle_fails(self, tmp_project):
        eng = ContextEngine(project_root=tmp_project)
        bundle = eng.build("T-1", _manifest())
        oversized = ContextBundle(
            request_id=bundle.request_id,
            task_id=bundle.task_id,
            slots=bundle.slots,
            total_token_count=bundle.token_budget + 1,
            token_budget=bundle.token_budget,
            compression_ratio=bundle.compression_ratio,
            bundle_hash=bundle.bundle_hash,
            degraded=bundle.degraded,
            degrade_reasons=bundle.degrade_reasons,
        )
        report = eng.validate(oversized)
        assert report.passed is False
        assert any("token_overflow" in v for v in report.violations)


class TestInject:
    def test_generic_ide_falls_back_to_prompts(self, tmp_project):
        eng = ContextEngine(project_root=tmp_project)
        bundle = eng.build("T-1", _manifest())
        result = eng.inject(bundle, ide_id="generic_mcp")
        assert isinstance(result, InjectResult)
        assert result.channels_used == ["prompts"]
        assert result.channels_skipped != []

    def test_trae_uses_resources_channel(self, tmp_project):
        eng = ContextEngine(project_root=tmp_project)
        bundle = eng.build("T-1", _manifest())
        result = eng.inject(bundle, ide_id="trae")
        assert "resources" in result.channels_used

    def test_unknown_ide_uses_static_matrix_fallback(self, tmp_project):
        eng = ContextEngine(project_root=tmp_project)
        bundle = eng.build("T-1", _manifest())
        result = eng.inject(bundle, ide_id="no-such-ide")
        assert result.channels_used == ["prompts"]


class TestRegisterRules:
    def test_register_and_query_rules(self):
        eng = ContextEngine()
        eng.register_rules("HOT", [{"rule_id": "R1", "text": "禁止重复造轮子"}])
        eng.register_rules("HOT", [{"rule_id": "R2", "text": "先查注册表"}])
        eng.register_rules("COLD", [{"rule_id": "R3", "text": "低频规则"}])
        assert [r.rule_id for r in eng.rules_for("HOT")] == ["R1", "R2"]
        assert [r.rule_id for r in eng.rules_for("COLD")] == ["R3"]
        assert eng.rules_for("DOMAIN") == []

    def test_register_rules_rejects_bad_tier(self):
        eng = ContextEngine()
        with pytest.raises(ValueError):
            eng.register_rules("WARM", [{"rule_id": "R1", "text": "x"}])


class TestAdjustStrategy:
    def test_downweight_slot_takes_effect(self):
        t0 = datetime(2026, 8, 23, 12, 0, 0)
        eng = ContextEngine(now=lambda: t0)
        before = eng.slot_budgets()["lessons"]
        result = eng.adjust_strategy(
            "T-1",
            {"suggested_action": "downweight_slot", "target_slot": "lessons", "adjustment_magnitude": 0.05},
        )
        assert result.applied is True
        assert eng.slot_budgets()["lessons"] == pytest.approx(before - 0.05)

    def test_budget_sum_conserved(self):
        eng = ContextEngine()
        eng.adjust_strategy(
            "T-1",
            {"suggested_action": "upweight_slot", "target_slot": "code_refs", "adjustment_magnitude": 0.1},
        )
        assert sum(eng.slot_budgets().values()) == pytest.approx(1.0, abs=1e-6)

    def test_ttl_expiry_reverts_to_default(self):
        t0 = datetime(2026, 8, 23, 12, 0, 0)
        state = {"now": t0}
        eng = ContextEngine(now=lambda: state["now"])
        default = eng.slot_budgets()["lessons"]
        eng.adjust_strategy(
            "T-1",
            {"suggested_action": "downweight_slot", "target_slot": "lessons", "adjustment_magnitude": 0.05, "ttl_minutes": 30},
        )
        assert eng.slot_budgets()["lessons"] != default
        state["now"] = t0 + timedelta(minutes=31)
        assert eng.slot_budgets()["lessons"] == pytest.approx(default)

    def test_unknown_slot_rejected(self):
        eng = ContextEngine()
        with pytest.raises(ValueError):
            eng.adjust_strategy("T-1", {"suggested_action": "downweight_slot", "target_slot": "nope", "adjustment_magnitude": 0.05})
