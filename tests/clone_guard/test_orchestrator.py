# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.1
# [MODULE] tests.clone_guard.test_orchestrator
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/clone_guard/test_orchestrator.py
# [A_test] module_id: MOD-CLONE_GUARD | layer=test | stability=volatile | safety=L | ai_modifiable
# [TTL] permanent
"""CloneGuardOrchestrator 单元测试——mock EchoGuardAdapter，验证编排逻辑。"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.orchestrator import CheckResult, CloneGuardOrchestrator
from zephyr.clone_guard.engines.echo_guard_adapter import Finding


def _make_finding(severity: str = "extract", similarity: float = 0.95) -> Finding:
    """构造测试用 Finding。"""
    return Finding(
        finding_id="F-001",
        severity=severity,
        clone_type="T2",
        similarity=similarity,
        source_file="src/new.py",
        source_function="calc",
        source_lineno=10,
        existing_file="src/old.py",
        existing_function="compute",
        existing_lineno=20,
    )


class TestOrchestratorFileFiltering:
    """_filter_files 文件筛选测试。"""

    def test_no_py_files_returns_pass(self, tmp_path: Path):
        orch = CloneGuardOrchestrator(tmp_path)
        result = orch.check(["README.md", "config.yml"])
        assert result.passed is True
        assert result.checked_files == 0

    def test_test_files_excluded(self, tmp_path: Path):
        """测试文件不被检测。"""
        orch = CloneGuardOrchestrator(tmp_path)
        with patch.object(orch._echo_guard, "detect", return_value=([], False)) as mock_detect:
            orch.check(["test_foo.py", "tests/bar.py", "src/conftest.py"])
        # 所有文件都被过滤，detect 不应被调用
        mock_detect.assert_not_called()

    def test_ignore_paths_excluded(self, tmp_path: Path):
        """忽略路径下的文件不被检测。"""
        orch = CloneGuardOrchestrator(tmp_path)
        with patch.object(orch._echo_guard, "detect", return_value=([], False)) as mock_detect:
            orch.check(["docs/guide.py", ".runtime/cache.py", "src/real.py"])
        mock_detect.assert_called_once_with(["src/real.py"], 30)

    def test_only_py_files_detected(self, tmp_path: Path):
        """仅 .py 文件被检测。"""
        orch = CloneGuardOrchestrator(tmp_path)
        with patch.object(orch._echo_guard, "detect", return_value=([], False)) as mock_detect:
            orch.check(["src/a.py", "src/b.js", "src/c.ts"])
        mock_detect.assert_called_once_with(["src/a.py"], 30)


class TestOrchestratorDegraded:
    """降级模式测试（守 blueprint §5.2 warn-only 兜底契约）。"""

    def test_degraded_fail_open_passes(self, tmp_path: Path):
        """降级 + fail_closed=False → passed=True（warn-only 兜底）。"""
        cfg = CloneGuardConfig(fail_closed=False)
        orch = CloneGuardOrchestrator(tmp_path, cfg)
        with patch.object(orch._echo_guard, "detect", return_value=([], True)):
            result = orch.check(["src/foo.py"])
        assert result.passed is True
        assert result.degraded is True
        assert result.checked_files == 1

    def test_degraded_fail_closed_blocks(self, tmp_path: Path):
        """降级 + fail_closed=True → passed=False（铁律阻断）。"""
        cfg = CloneGuardConfig(fail_closed=True)
        orch = CloneGuardOrchestrator(tmp_path, cfg)
        with patch.object(orch._echo_guard, "detect", return_value=([], True)):
            result = orch.check(["src/foo.py"])
        assert result.passed is False
        assert result.degraded is True

    def test_degraded_no_py_files_not_triggered(self, tmp_path: Path):
        """无 .py 文件时不触发降级逻辑。"""
        orch = CloneGuardOrchestrator(tmp_path)
        with patch.object(orch._echo_guard, "detect", return_value=([], True)) as mock_detect:
            result = orch.check(["README.md"])
        mock_detect.assert_not_called()
        assert result.passed is True
        assert result.degraded is False


class TestOrchestratorSeverityJudgment:
    """严重性判定测试——extract 级硬阻断，review 级警告。"""

    def test_extract_severity_blocks(self, tmp_path: Path):
        """extract 级克隆 → passed=False（硬阻断）。"""
        orch = CloneGuardOrchestrator(tmp_path)
        finding = _make_finding(severity="extract")
        with patch.object(orch._echo_guard, "detect", return_value=([finding], False)):
            result = orch.check(["src/new.py"])
        assert result.passed is False
        assert len(result.findings) == 1
        assert result.findings[0].severity == "extract"

    def test_review_severity_passes_with_warning(self, tmp_path: Path):
        """review 级克隆 → passed=True（警告不阻断）。"""
        orch = CloneGuardOrchestrator(tmp_path)
        finding = _make_finding(severity="review")
        with patch.object(orch._echo_guard, "detect", return_value=([finding], False)):
            result = orch.check(["src/new.py"])
        assert result.passed is True
        assert len(result.findings) == 1

    def test_mixed_severity_blocks_on_extract(self, tmp_path: Path):
        """extract + review 混合 → passed=False（extract 级触发阻断）。"""
        orch = CloneGuardOrchestrator(tmp_path)
        findings = [
            _make_finding(severity="review", similarity=0.6),
            _make_finding(severity="extract", similarity=0.95),
        ]
        with patch.object(orch._echo_guard, "detect", return_value=(findings, False)):
            result = orch.check(["src/new.py"])
        assert result.passed is False
        # block_findings 仅含 extract 级
        assert len(result.findings) == 1
        assert result.findings[0].severity == "extract"

    def test_no_findings_passes(self, tmp_path: Path):
        """无克隆发现 → passed=True。"""
        orch = CloneGuardOrchestrator(tmp_path)
        with patch.object(orch._echo_guard, "detect", return_value=([], False)):
            result = orch.check(["src/new.py"])
        assert result.passed is True
        assert result.findings == []

    def test_review_fail_on_review_blocks(self, tmp_path: Path):
        """fail_on=review 时 review 级也硬阻断。"""
        cfg = CloneGuardConfig(fail_on_severity="review")
        orch = CloneGuardOrchestrator(tmp_path, cfg)
        finding = _make_finding(severity="review")
        with patch.object(orch._echo_guard, "detect", return_value=([finding], False)):
            result = orch.check(["src/new.py"])
        assert result.passed is False
