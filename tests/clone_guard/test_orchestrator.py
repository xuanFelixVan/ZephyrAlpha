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
"""CloneGuardOrchestrator 单元测试——mock 适配器，验证编排逻辑。

Phase A: 单引擎（Echo-Guard）文件筛选/降级/严重性判定。
Phase B: 多引擎并发（asyncio.gather）+ 聚合 + 共识 + 部分降级。
"""

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


# ===========================================================================
# Phase B：多引擎并发 + 聚合 + 共识 + 部分降级
# ===========================================================================


def _make_sg_finding(
    severity: str = "review",
    similarity: float = 1.0,
    source_function: str = "calc",
    existing_function: str = "compute",
    source_lineno: int = 10,
) -> Finding:
    """构造测试用 ast-grep Finding（clone_type=rule，existing_file=规则文件）。"""
    return Finding(
        finding_id=f"SG-{source_function}-{source_lineno}",
        severity=severity,
        clone_type="rule",
        similarity=similarity,
        source_file="src/new.py",
        source_function=source_function,
        source_lineno=source_lineno,
        existing_file="clone_guard/rules/no-bare-except.yml",
        existing_function=existing_function,
        existing_lineno=0,
    )


class TestOrchestratorMultiEngine:
    """Phase B 多引擎并发调度测试。"""

    def test_both_engines_invoked(self, tmp_path: Path):
        """两个引擎都被调用（并发调度生效）。"""
        orch = CloneGuardOrchestrator(tmp_path)
        with patch.object(orch._echo_guard, "detect", return_value=([], False)) as m_echo, \
             patch.object(orch._ast_grep, "detect", return_value=([], False)) as m_sg:
            orch.check(["src/foo.py"])
        m_echo.assert_called_once()
        m_sg.assert_called_once()

    def test_both_engines_same_dedup_key_merges_unanimous(self, tmp_path: Path):
        """两引擎报相同去重键 → 合并为 1 个 unanimous finding，severity 就高。"""
        orch = CloneGuardOrchestrator(tmp_path)
        # echo_guard 报 review，ast_grep 报 extract——相同去重键
        eg_finding = _make_finding(severity="review", similarity=0.8)
        sg_finding = Finding(
            finding_id="SG-1",
            severity="extract",
            clone_type="rule",
            similarity=0.95,
            source_file="src/new.py",
            source_function="calc",
            source_lineno=10,
            existing_file="src/old.py",
            existing_function="compute",
            existing_lineno=20,
        )
        with patch.object(orch._echo_guard, "detect", return_value=([eg_finding], False)), \
             patch.object(orch._ast_grep, "detect", return_value=([sg_finding], False)):
            result = orch.check(["src/new.py"])
        assert result.passed is False  # extract 就高 → 阻断
        assert len(result.findings) == 1
        f = result.findings[0]
        assert f.consensus == "unanimous"
        assert f.severity == "extract"  # 就高原则
        assert f.similarity == 0.95  # 取最大
        assert set(f.engines) == {"echo_guard", "ast_grep"}
        assert result.consensus_summary == {"unanimous": 1}

    def test_consensus_summary_mixed(self, tmp_path: Path):
        """混合共识：f1 两引擎一致(unanimous) + f2 仅 ast_grep(majority)。"""
        orch = CloneGuardOrchestrator(tmp_path)
        # f1：两引擎报相同去重键
        eg_f1 = _make_finding(severity="review", similarity=0.8)
        sg_f1 = Finding(
            finding_id="SG-f1",
            severity="review",
            clone_type="rule",
            similarity=0.9,
            source_file="src/new.py",
            source_function="calc",
            source_lineno=10,
            existing_file="src/old.py",
            existing_function="compute",
            existing_lineno=20,
        )
        # f2：仅 ast_grep 报（不同去重键）——2 引擎 threshold=1, vote=1 → majority
        sg_f2 = _make_sg_finding(
            severity="review",
            source_function="other_fn",
            existing_function="no-bare-except",
            source_lineno=50,
        )
        with patch.object(orch._echo_guard, "detect", return_value=([eg_f1], False)), \
             patch.object(orch._ast_grep, "detect", return_value=([sg_f1, sg_f2], False)):
            result = orch.check(["src/new.py"])
        assert result.passed is True  # 全 review
        assert len(result.findings) == 2
        assert result.consensus_summary == {"unanimous": 1, "majority": 1}

    def test_ast_grep_rule_finding_flows_through(self, tmp_path: Path):
        """ast_grep 结构反模式 finding 流经聚合器（clone_type=rule 保留）。"""
        orch = CloneGuardOrchestrator(tmp_path)
        sg_finding = _make_sg_finding(
            severity="review",
            source_function="unknown",
            existing_function="no-bare-except",
            source_lineno=5,
        )
        with patch.object(orch._echo_guard, "detect", return_value=([], False)), \
             patch.object(orch._ast_grep, "detect", return_value=([sg_finding], False)):
            result = orch.check(["src/new.py"])
        assert result.passed is True  # review 不阻断
        assert len(result.findings) == 1
        assert result.findings[0].clone_type == "rule"


class TestOrchestratorPartialDegradation:
    """Phase B 部分降级 + 全降级测试（守 blueprint §5.2）。"""

    def test_partial_degradation_uses_active_engine(self, tmp_path: Path):
        """ast_grep 降级、echo_guard 正常 → 用 echo_guard 结果，degraded=True。"""
        orch = CloneGuardOrchestrator(tmp_path)
        finding = _make_finding(severity="extract")
        with patch.object(orch._echo_guard, "detect", return_value=([finding], False)), \
             patch.object(orch._ast_grep, "detect", return_value=([], True)):
            result = orch.check(["src/new.py"])
        assert result.passed is False  # extract 阻断
        assert result.degraded is True
        assert result.degraded_engines == ["ast_grep"]
        assert len(result.findings) == 1
        # 单活跃引擎 → unanimous
        assert result.findings[0].consensus == "unanimous"

    def test_partial_degradation_reverse(self, tmp_path: Path):
        """echo_guard 降级、ast_grep 正常 → 用 ast_grep 结果。"""
        orch = CloneGuardOrchestrator(tmp_path)
        sg_finding = _make_sg_finding(severity="extract")
        with patch.object(orch._echo_guard, "detect", return_value=([], True)), \
             patch.object(orch._ast_grep, "detect", return_value=([sg_finding], False)):
            result = orch.check(["src/new.py"])
        assert result.passed is False
        assert result.degraded is True
        assert result.degraded_engines == ["echo_guard"]

    def test_engine_exception_normalized_to_degraded(self, tmp_path: Path):
        """echo_guard 抛异常 → asyncio.gather 捕获归一为降级；ast_grep 正常。"""

        def boom(*args, **kwargs):
            raise RuntimeError("echo-guard boom")

        orch = CloneGuardOrchestrator(tmp_path)
        sg_finding = _make_sg_finding(severity="review")
        with patch.object(orch._echo_guard, "detect", side_effect=boom), \
             patch.object(orch._ast_grep, "detect", return_value=([sg_finding], False)):
            result = orch.check(["src/new.py"])
        assert result.passed is True  # review 不阻断
        assert result.degraded is True
        assert "echo_guard" in result.degraded_engines
        assert len(result.findings) == 1

    def test_total_degradation_fail_open(self, tmp_path: Path):
        """两引擎全降级 + fail_closed=False → warn-only 放行。"""
        cfg = CloneGuardConfig(fail_closed=False)
        orch = CloneGuardOrchestrator(tmp_path, cfg)
        with patch.object(orch._echo_guard, "detect", return_value=([], True)), \
             patch.object(orch._ast_grep, "detect", return_value=([], True)):
            result = orch.check(["src/foo.py"])
        assert result.passed is True
        assert result.degraded is True
        assert set(result.degraded_engines) == {"echo_guard", "ast_grep"}
        assert result.findings == []

    def test_total_degradation_fail_closed(self, tmp_path: Path):
        """两引擎全降级 + fail_closed=True → 铁律阻断。"""
        cfg = CloneGuardConfig(fail_closed=True)
        orch = CloneGuardOrchestrator(tmp_path, cfg)
        with patch.object(orch._echo_guard, "detect", return_value=([], True)), \
             patch.object(orch._ast_grep, "detect", return_value=([], True)):
            result = orch.check(["src/foo.py"])
        assert result.passed is False
        assert result.degraded is True
        assert set(result.degraded_engines) == {"echo_guard", "ast_grep"}

    def test_no_py_files_skips_engines(self, tmp_path: Path):
        """无 .py 文件 → 引擎不被调用。"""
        orch = CloneGuardOrchestrator(tmp_path)
        with patch.object(orch._echo_guard, "detect", return_value=([], False)) as m_echo, \
             patch.object(orch._ast_grep, "detect", return_value=([], False)) as m_sg:
            result = orch.check(["README.md"])
        m_echo.assert_not_called()
        m_sg.assert_not_called()
        assert result.passed is True
        assert result.degraded is False
