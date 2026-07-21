# [A_test] module_id: MOD-GOV_audit_orphan_judge_e2e | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""[BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan-judge/blueprint.md | §e2e

[MODULE] tests.test_audit_orphan_judge_e2e

[INVARIANTS] E2E tests cover DecisionTable 12-row routing; SafetyFence blocks frozen/immutable_core; DeprecationTracker lifecycle; CascadeAnalyzer dependency chain; OrphanJudge five-layer pipeline with safety fence

[MODIFY-GUARD] orphan-judge/blueprint.md

[CONSUMERS] CI pipeline; governance audit

[STABILITY] evolving

[SAFETY] L

[AI_AUTONOMY] ai_modifiable

[ERROR_CONTRACT] pytest assertion errors on verdict mismatch

[TESTS] self
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("zephyr.security.access_control.orphan_judge.decision_table")
pytest.importorskip("zephyr.security.access_control.orphan_judge.safety_fence")
pytest.importorskip("zephyr.security.access_control.orphan_judge.deprecation_tracker")
pytest.importorskip("zephyr.security.access_control.orphan_judge.cascade_analyzer")
pytest.importorskip("zephyr.security.access_control.orphan_judge.judge")

from zephyr.security.access_control.orphan_judge.cascade_analyzer import CascadeAnalyzer, CascadeResult, CascadeRisk
from zephyr.security.access_control.orphan_judge.decision_table import DecisionTable
from zephyr.security.access_control.orphan_judge.decision_table import LayerResult as DTLayerResult
from zephyr.security.access_control.orphan_judge.decision_table import Verdict as DTVerdict
from zephyr.security.access_control.orphan_judge.deprecation_tracker import DeprecationTracker
from zephyr.security.access_control.orphan_judge.judge import (
    Confidence,
    LayerResult,
    OrphanJudge,
    OrphanJudgeReport,
    Verdict,
)
from zephyr.security.access_control.orphan_judge.safety_fence import SafetyFence


@pytest.mark.e2e
class TestDecisionTableE2E:
    def test_registered_file_kept(self):
        """L0已注册→KEEP"""
        table = DecisionTable()
        result = table.evaluate(l0_result=DTLayerResult(registered=True))
        assert result == DTVerdict.KEEP

    def test_reachable_file_kept(self):
        """L1可达→KEEP"""
        table = DecisionTable()
        result = table.evaluate(l1_result=DTLayerResult(reachable=True))
        assert result == DTVerdict.KEEP

    def test_duplicate_no_unique_deleted(self):
        """重复+无独特→DELETE"""
        table = DecisionTable()
        result = table.evaluate(
            l2_result=DTLayerResult(is_duplicate=True),
            l3_result=DTLayerResult(has_unique_value=False),
        )
        assert result == DTVerdict.DELETE

    def test_duplicate_has_unique_merged(self):
        """重复+有独特→EXTRACT_AND_MERGE"""
        table = DecisionTable()
        result = table.evaluate(
            l2_result=DTLayerResult(is_duplicate=True),
            l3_result=DTLayerResult(has_unique_value=True),
        )
        assert result == DTVerdict.EXTRACT_AND_MERGE

    def test_uncertain_escalated(self):
        """不确定→ESCALATE"""
        table = DecisionTable()
        result = table.evaluate(l2_result=DTLayerResult(uncertain=True))
        assert result == DTVerdict.ESCALATE


@pytest.mark.e2e
class TestSafetyFenceE2E:
    def test_frozen_file_blocked(self, tmp_path):
        """frozen文件拒绝删除"""
        frozen_file = tmp_path / "frozen_module.py"
        frozen_file.write_text(
            '"""[STABILITY] frozen\n[AI_AUTONOMY] ai_modifiable"""\npass\n',
            encoding="utf-8",
        )
        fence = SafetyFence(project_root=tmp_path)
        assert fence.is_deletion_allowed(str(frozen_file)) is False
        result = fence.check_safety(str(frozen_file), "delete")
        assert result.allowed is False
        assert "STABILITY=frozen" in result.reason

    def test_high_safety_file_blocked(self, tmp_path):
        """SAFETY=H文件拒绝删除"""
        high_safety_file = tmp_path / "high_safety_module.py"
        high_safety_file.write_text(
            '"""[STABILITY] stable\n[AI_AUTONOMY] immutable_core"""\npass\n',
            encoding="utf-8",
        )
        fence = SafetyFence(project_root=tmp_path)
        assert fence.is_deletion_allowed(str(high_safety_file)) is False
        result = fence.check_safety(str(high_safety_file), "delete")
        assert result.allowed is False
        assert "AI_AUTONOMY=immutable_core" in result.reason

    def test_normal_file_allowed(self, tmp_path):
        """普通文件允许删除"""
        normal_file = tmp_path / "normal_module.py"
        normal_file.write_text(
            '"""[STABILITY] evolving\n[AI_AUTONOMY] ai_modifiable"""\npass\n',
            encoding="utf-8",
        )
        fence = SafetyFence(project_root=tmp_path)
        assert fence.is_deletion_allowed(str(normal_file)) is True
        result = fence.check_safety(str(normal_file), "delete")
        assert result.allowed is True
        assert result.blocked_by == []


@pytest.mark.e2e
class TestDeprecationTrackerE2E:
    def test_deprecate_and_check(self, tmp_path):
        """标记废弃→查询废弃→确认已废弃"""
        tracker = DeprecationTracker(project_root=tmp_path)
        record = tracker.deprecate(
            "src/zephyr/example.py",
            ttl_days=30,
            reason="Replaced by new_module",
        )
        assert record.path == "src/zephyr/example.py"
        assert record.ttl_days == 30
        assert record.reason == "Replaced by new_module"
        assert tracker.is_deprecated("src/zephyr/example.py") is True
        fetched = tracker.get_record("src/zephyr/example.py")
        assert fetched is not None
        assert fetched.path == "src/zephyr/example.py"
        assert fetched.reason == "Replaced by new_module"
        all_records = tracker.list_all()
        assert any(r.path == "src/zephyr/example.py" for r in all_records)

    def test_remove_expired(self, tmp_path):
        """过期废弃文件被移除"""
        tracker = DeprecationTracker(project_root=tmp_path)
        tracker.deprecate(
            "src/zephyr/old_module.py",
            ttl_days=-1,
            reason="Expired immediately for test",
        )
        expired = tracker.check_deprecated()
        assert len(expired) >= 1
        assert any(r.path == "src/zephyr/old_module.py" for r in expired)
        removed = tracker.remove_deprecated()
        assert "src/zephyr/old_module.py" in removed
        assert tracker.is_deprecated("src/zephyr/old_module.py") is False
        assert tracker.get_record("src/zephyr/old_module.py") is None


@pytest.mark.e2e
class TestCascadeAnalyzerE2E:
    @staticmethod
    def _setup_project(tmp_path: Path) -> dict[str, Path]:
        src_dir = tmp_path / "src" / "zephyr"
        src_dir.mkdir(parents=True)
        (src_dir / "__init__.py").write_text("", encoding="utf-8")
        target = src_dir / "target_lib.py"
        target.write_text("def core_func(): pass\n", encoding="utf-8")
        consumer = src_dir / "consumer_a.py"
        consumer.write_text("from zephyr.target_lib import core_func\n", encoding="utf-8")
        return {"src_dir": src_dir, "target": target, "consumer": consumer}

    def test_analyze_cascade(self, tmp_path):
        """分析删除级联影响"""
        paths = self._setup_project(tmp_path)
        analyzer = CascadeAnalyzer(project_root=tmp_path)
        result = analyzer.analyze_cascade(str(paths["target"]))
        assert isinstance(result, CascadeResult)
        assert result.path == str(paths["target"])
        assert len(result.direct_dependents) >= 1
        assert any("consumer_a" in d for d in result.direct_dependents)
        assert result.cascade_risk in (CascadeRisk.LOW, CascadeRisk.MEDIUM, CascadeRisk.HIGH)

    def test_find_dependents(self, tmp_path):
        """查找依赖文件"""
        src_dir = tmp_path / "src" / "zephyr"
        src_dir.mkdir(parents=True)
        (src_dir / "__init__.py").write_text("", encoding="utf-8")
        target = src_dir / "shared_util.py"
        target.write_text("def helper(): pass\n", encoding="utf-8")
        dep_a = src_dir / "module_a.py"
        dep_a.write_text("from zephyr.shared_util import helper\n", encoding="utf-8")
        dep_b = src_dir / "module_b.py"
        dep_b.write_text("import zephyr.shared_util\n", encoding="utf-8")
        unrelated = src_dir / "unrelated.py"
        unrelated.write_text("x = 1\n", encoding="utf-8")
        analyzer = CascadeAnalyzer(project_root=tmp_path)
        dependents = analyzer.find_dependents(str(target))
        dep_names = [Path(d).name for d in dependents]
        assert "module_a.py" in dep_names
        assert "module_b.py" in dep_names
        assert "unrelated.py" not in dep_names


class _MockL0Registered:
    def check(self, path: str) -> LayerResult:
        return LayerResult(
            layer="L0",
            passed=True,
            data={"is_registered": True, "registered_in": ["__init__.py"]},
        )


class _MockL0NotRegistered:
    def check(self, path: str) -> LayerResult:
        return LayerResult(layer="L0", passed=False, data={"is_registered": False})


class _MockL1NotReachable:
    def check(self, path: str) -> LayerResult:
        return LayerResult(
            layer="L1",
            passed=False,
            data={"is_reachable": False, "referenced_by": []},
        )


class _MockL2Duplicate:
    def check(self, path: str) -> LayerResult:
        return LayerResult(
            layer="L2",
            passed=True,
            data={"is_duplicate": True, "is_uncertain": False},
        )


class _MockL3NoUnique:
    def check(self, path: str) -> LayerResult:
        return LayerResult(
            layer="L3",
            passed=False,
            data={"has_unique": False, "is_uncertain": False},
        )


class _MockL4NoValue:
    def check(self, path: str) -> LayerResult:
        return LayerResult(
            layer="L4",
            passed=False,
            data={"has_value": False, "is_uncertain": False},
        )


def _make_orphan_judge() -> OrphanJudge:
    return OrphanJudge(
        l0_checker=_MockL0NotRegistered(),
        l1_checker=_MockL1NotReachable(),
        l2_checker=_MockL2Duplicate(),
        l3_checker=_MockL3NoUnique(),
        l4_checker=_MockL4NoValue(),
    )


@pytest.mark.e2e
class TestOrphanJudgeE2E:
    def test_judge_registered_file(self, tmp_path):
        """已注册文件→KEEP"""
        test_file = tmp_path / "registered_mod.py"
        test_file.write_text("# registered module\n", encoding="utf-8")
        judge = OrphanJudge(l0_checker=_MockL0Registered())
        result = judge.judge(str(test_file))
        assert result.verdict == Verdict.KEEP
        assert result.confidence == Confidence.HIGH
        assert result.safety_blocked is False

    def test_judge_orphan_file(self, tmp_path):
        """孤儿文件→判定处置"""
        test_file = tmp_path / "orphan_mod.py"
        test_file.write_text("# orphan module\n", encoding="utf-8")
        judge = _make_orphan_judge()
        result = judge.judge(str(test_file))
        assert result.path == str(test_file)
        assert result.verdict in (Verdict.DELETE, Verdict.ESCALATE, Verdict.DEPRECATE)
        assert len(result.layers) >= 3

    def test_batch_judge(self, tmp_path):
        """批量判定"""
        for i in range(3):
            f = tmp_path / f"batch_{i}.py"
            f.write_text(f"# batch module {i}\n", encoding="utf-8")
        judge = _make_orphan_judge()
        report = judge.batch_judge(scope=str(tmp_path), limit=10)
        assert isinstance(report, OrphanJudgeReport)
        assert report.total == 3
        assert report.execution_time_ms >= 0
        assert len(report.judgments) == 3
        assert sum(report.by_verdict.values()) == 3

    def test_safety_fence_blocks_deletion(self, tmp_path):
        """安全围栏阻止删除frozen文件"""
        frozen_file = tmp_path / "frozen_critical.py"
        frozen_file.write_text(
            '"""[STABILITY] frozen\n[SAFETY] H\n[AI_AUTONOMY] immutable_core"""\npass\n',
            encoding="utf-8",
        )
        judge = _make_orphan_judge()
        result = judge.judge(str(frozen_file))
        assert result.safety_blocked is True
        assert result.verdict == Verdict.ESCALATE
