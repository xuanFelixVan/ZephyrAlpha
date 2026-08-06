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
from zephyr.clone_guard.engines.echo_guard_adapter import Finding
from zephyr.clone_guard.orchestrator import CheckResult, CloneGuardOrchestrator


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
        existing_file="src/zephyr/clone_guard/rules/no-bare-except.yaml",
        existing_function=existing_function,
        existing_lineno=0,
    )


class TestOrchestratorMultiEngine:
    """Phase B 多引擎并发调度测试。"""

    def test_both_engines_invoked(self, tmp_path: Path):
        """两个引擎都被调用（并发调度生效）。"""
        orch = CloneGuardOrchestrator(tmp_path)
        with (
            patch.object(orch._echo_guard, "detect", return_value=([], False)) as m_echo,
            patch.object(orch._ast_grep, "detect", return_value=([], False)) as m_sg,
        ):
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
        with (
            patch.object(orch._echo_guard, "detect", return_value=([eg_finding], False)),
            patch.object(orch._ast_grep, "detect", return_value=([sg_finding], False)),
        ):
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
        with (
            patch.object(orch._echo_guard, "detect", return_value=([eg_f1], False)),
            patch.object(orch._ast_grep, "detect", return_value=([sg_f1, sg_f2], False)),
        ):
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
        with (
            patch.object(orch._echo_guard, "detect", return_value=([], False)),
            patch.object(orch._ast_grep, "detect", return_value=([sg_finding], False)),
        ):
            result = orch.check(["src/new.py"])
        assert result.passed is True  # review 不阻断
        assert len(result.findings) == 1
        assert result.findings[0].clone_type == "rule"


class TestOrchestratorPartialDegradation:
    """Phase B 部分降级 + 全降级测试（守 blueprint §5.2）。"""

    def test_partial_degradation_uses_active_engine(self, tmp_path: Path):
        """ast_grep 降级、echo_guard 正常 → 用 echo_guard 结果，degraded=True。"""
        # redup_enabled=False 隔离出 echo_guard/ast_grep 双引擎场景
        orch = CloneGuardOrchestrator(tmp_path, CloneGuardConfig(redup_enabled=False))
        finding = _make_finding(severity="extract")
        with (
            patch.object(orch._echo_guard, "detect", return_value=([finding], False)),
            patch.object(orch._ast_grep, "detect", return_value=([], True)),
        ):
            result = orch.check(["src/new.py"])
        assert result.passed is False  # extract 阻断
        assert result.degraded is True
        assert result.degraded_engines == ["ast_grep"]
        assert len(result.findings) == 1
        # 单活跃引擎 → unanimous
        assert result.findings[0].consensus == "unanimous"

    def test_partial_degradation_reverse(self, tmp_path: Path):
        """echo_guard 降级、ast_grep 正常 → 用 ast_grep 结果。"""
        orch = CloneGuardOrchestrator(tmp_path, CloneGuardConfig(redup_enabled=False))
        sg_finding = _make_sg_finding(severity="extract")
        with (
            patch.object(orch._echo_guard, "detect", return_value=([], True)),
            patch.object(orch._ast_grep, "detect", return_value=([sg_finding], False)),
        ):
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
        with (
            patch.object(orch._echo_guard, "detect", side_effect=boom),
            patch.object(orch._ast_grep, "detect", return_value=([sg_finding], False)),
        ):
            result = orch.check(["src/new.py"])
        assert result.passed is True  # review 不阻断
        assert result.degraded is True
        assert "echo_guard" in result.degraded_engines
        assert len(result.findings) == 1

    def test_total_degradation_fail_open(self, tmp_path: Path):
        """三引擎全降级 + fail_closed=False → warn-only 放行。"""
        cfg = CloneGuardConfig(fail_closed=False)
        orch = CloneGuardOrchestrator(tmp_path, cfg)
        with (
            patch.object(orch._echo_guard, "detect", return_value=([], True)),
            patch.object(orch._ast_grep, "detect", return_value=([], True)),
            patch.object(orch._redup, "detect", return_value=([], True)),
        ):
            result = orch.check(["src/foo.py"])
        assert result.passed is True
        assert result.degraded is True
        assert set(result.degraded_engines) == {"echo_guard", "ast_grep", "redup"}
        assert result.findings == []

    def test_total_degradation_fail_closed(self, tmp_path: Path):
        """三引擎全降级 + fail_closed=True → 铁律阻断。"""
        cfg = CloneGuardConfig(fail_closed=True)
        orch = CloneGuardOrchestrator(tmp_path, cfg)
        with (
            patch.object(orch._echo_guard, "detect", return_value=([], True)),
            patch.object(orch._ast_grep, "detect", return_value=([], True)),
            patch.object(orch._redup, "detect", return_value=([], True)),
        ):
            result = orch.check(["src/foo.py"])
        assert result.passed is False
        assert result.degraded is True
        assert set(result.degraded_engines) == {"echo_guard", "ast_grep", "redup"}

    def test_no_py_files_skips_engines(self, tmp_path: Path):
        """无 .py 文件 → 引擎不被调用。"""
        orch = CloneGuardOrchestrator(tmp_path)
        with (
            patch.object(orch._echo_guard, "detect", return_value=([], False)) as m_echo,
            patch.object(orch._ast_grep, "detect", return_value=([], False)) as m_sg,
        ):
            result = orch.check(["README.md"])
        m_echo.assert_not_called()
        m_sg.assert_not_called()
        assert result.passed is True
        assert result.degraded is False


# ===========================================================================
# Phase B 补齐：reDUP 接入——3 引擎并发（echo_guard + ast_grep + redup）
# ===========================================================================


def _make_rd_finding(
    severity: str = "review",
    similarity: float = 0.9,
    clone_type: str = "T3",
    source_function: str = "calc",
    existing_function: str = "compute",
) -> Finding:
    """构造测试用 reDUP Finding（clone_type=T3/T4 语义克隆）。"""
    return Finding(
        finding_id=f"RD-{source_function}",
        severity=severity,
        clone_type=clone_type,
        similarity=similarity,
        source_file="src/new.py",
        source_function=source_function,
        source_lineno=10,
        existing_file="src/old.py",
        existing_function=existing_function,
        existing_lineno=20,
    )


class TestOrchestratorThreeEngines:
    """reDUP 接入后 3 引擎并发调度测试。"""

    def test_all_three_engines_invoked(self, tmp_path: Path):
        """3 个引擎都被调用（并发调度生效）。"""
        orch = CloneGuardOrchestrator(tmp_path)
        with (
            patch.object(orch._echo_guard, "detect", return_value=([], False)) as m_echo,
            patch.object(orch._ast_grep, "detect", return_value=([], False)) as m_sg,
            patch.object(orch._redup, "detect", return_value=([], False)) as m_rd,
        ):
            orch.check(["src/foo.py"])
        m_echo.assert_called_once()
        m_sg.assert_called_once()
        m_rd.assert_called_once()

    def test_three_engines_unanimous_consensus(self, tmp_path: Path):
        """3 引擎报相同去重键 → consensus=unanimous（3/3）。"""
        orch = CloneGuardOrchestrator(tmp_path)
        eg_f = _make_finding(severity="review", similarity=0.8)
        sg_f = Finding(
            finding_id="SG-1",
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
        rd_f = _make_rd_finding(severity="extract", similarity=0.95)
        with (
            patch.object(orch._echo_guard, "detect", return_value=([eg_f], False)),
            patch.object(orch._ast_grep, "detect", return_value=([sg_f], False)),
            patch.object(orch._redup, "detect", return_value=([rd_f], False)),
        ):
            result = orch.check(["src/new.py"])
        assert result.passed is False  # extract 就高 → 阻断
        assert len(result.findings) == 1
        f = result.findings[0]
        assert f.consensus == "unanimous"  # 3/3
        assert f.severity == "extract"  # 就高
        assert f.similarity == 0.95  # 取最大
        assert set(f.engines) == {"echo_guard", "ast_grep", "redup"}
        assert result.consensus_summary == {"unanimous": 1}

    def test_two_of_three_majority_consensus(self, tmp_path: Path):
        """3 引擎中 2 个报相同键 → consensus=majority（2/3，threshold=ceil(3/2)=2）。"""
        orch = CloneGuardOrchestrator(tmp_path)
        eg_f = _make_finding(severity="review", similarity=0.8)
        rd_f = _make_rd_finding(severity="review", similarity=0.9)
        # ast_grep 报不同去重键（rule 类，existing_file=规则文件）
        sg_other = _make_sg_finding(severity="review", source_function="other", existing_function="no-bare-except")
        with (
            patch.object(orch._echo_guard, "detect", return_value=([eg_f], False)),
            patch.object(orch._ast_grep, "detect", return_value=([sg_other], False)),
            patch.object(orch._redup, "detect", return_value=([rd_f], False)),
        ):
            result = orch.check(["src/new.py"])
        assert result.passed is True  # 全 review
        assert len(result.findings) == 2
        # eg+rd 同键 → majority；sg 单独 → single(1/3 < 2)
        summary = result.consensus_summary
        assert summary.get("majority") == 1
        assert summary.get("single") == 1

    def test_redup_only_single_engine_majority(self, tmp_path: Path):
        """仅 redup 报 finding（echo/ast 空）→ 3 引擎 threshold=2，1<2 → single。"""
        orch = CloneGuardOrchestrator(tmp_path)
        rd_f = _make_rd_finding(severity="review", similarity=0.9)
        with (
            patch.object(orch._echo_guard, "detect", return_value=([], False)),
            patch.object(orch._ast_grep, "detect", return_value=([], False)),
            patch.object(orch._redup, "detect", return_value=([rd_f], False)),
        ):
            result = orch.check(["src/new.py"])
        assert result.passed is True  # review 不阻断
        assert len(result.findings) == 1
        assert result.findings[0].consensus == "single"  # 1/3 < 2
        assert result.findings[0].clone_type == "T3"  # reDUP 语义克隆类型保留

    def test_redup_disabled_excludes_from_engine_set(self, tmp_path: Path):
        """redup_enabled=False → redup 不参与调度（2 引擎场景）。"""
        orch = CloneGuardOrchestrator(tmp_path, CloneGuardConfig(redup_enabled=False))
        with (
            patch.object(orch._echo_guard, "detect", return_value=([], False)) as m_echo,
            patch.object(orch._ast_grep, "detect", return_value=([], False)) as m_sg,
            patch.object(orch._redup, "detect", return_value=([], False)) as m_rd,
        ):
            orch.check(["src/foo.py"])
        m_echo.assert_called_once()
        m_sg.assert_called_once()
        m_rd.assert_not_called()  # redup 被禁用，不调用


# ===========================================================================
# Phase C：L2 audit() + L3 compare()（架构裁定：可运行核心闭环）
# ===========================================================================

from zephyr.clone_guard.orchestrator import AuditResult, CompareResult  # noqa: E402


def _patch_l2_engines(orch, echo_ret=([], False), redup_ret=([], False), ast_ret=([], False)):
    """patch L2 引擎集（mcrit 默认禁用，仅 echo/redup/ast 参与）。

    echo_guard 在 L2 走 scan()（全仓库扫描，守蓝图 §3.4 阶段2 + L2 scan 改造），
    故 patch scan；redup/ast_grep 无 scan 方法，仍走 detect()。
    """
    return (
        patch.object(orch._echo_guard, "scan", return_value=echo_ret),
        patch.object(orch._redup, "detect", return_value=redup_ret),
        patch.object(orch._ast_grep, "detect", return_value=ast_ret),
    )


class TestOrchestratorAudit:
    """L2 周期审计测试（架构裁定：可运行核心闭环）。"""

    def test_audit_no_py_files(self, tmp_path: Path):
        """无 .py 文件 → 空审计，health_score=A。"""
        orch = CloneGuardOrchestrator(tmp_path)
        result = orch.audit(["README.md"])
        assert result.checked_files == 0
        assert result.health_score == "A"
        assert result.findings == []
        assert result.refactoring_plan == []

    def test_audit_no_findings_health_a(self, tmp_path: Path):
        """L2 引擎无发现 → health_score=A。"""
        orch = CloneGuardOrchestrator(tmp_path)
        p1, p2, p3 = _patch_l2_engines(orch)
        with p1, p2, p3:
            result = orch.audit(["src/foo.py"])
        assert result.checked_files == 1
        assert result.health_score == "A"
        assert result.findings == []

    def test_audit_health_score_c_one_extract(self, tmp_path: Path):
        """1 个 extract finding → health_score=C。"""
        orch = CloneGuardOrchestrator(tmp_path)
        finding = _make_finding(severity="extract", similarity=0.95)
        p1, p2, p3 = _patch_l2_engines(orch, echo_ret=([finding], False))
        with p1, p2, p3:
            result = orch.audit(["src/new.py"])
        assert result.health_score == "C"
        assert len(result.findings) == 1

    def test_audit_health_score_b_review_only(self, tmp_path: Path):
        """仅 review findings（<5）→ health_score=B。"""
        orch = CloneGuardOrchestrator(tmp_path)
        finding = _make_finding(severity="review", similarity=0.8)
        p1, p2, p3 = _patch_l2_engines(orch, echo_ret=([finding], False))
        with p1, p2, p3:
            result = orch.audit(["src/new.py"])
        assert result.health_score == "B"

    def test_audit_health_score_f_many_extract(self, tmp_path: Path):
        """≥5 个 extract findings → health_score=F。"""
        orch = CloneGuardOrchestrator(tmp_path)
        findings = [
            Finding(
                finding_id=f"F-{i}",
                severity="extract",
                clone_type="T2",
                similarity=0.95,
                source_file=f"src/a{i}.py",
                source_function="calc",
                source_lineno=10,
                existing_file="src/old.py",
                existing_function="compute",
                existing_lineno=20,
            )
            for i in range(5)
        ]
        p1, p2, p3 = _patch_l2_engines(orch, echo_ret=(findings, False))
        with p1, p2, p3:
            result = orch.audit(["src/new.py"])
        assert result.health_score == "F"

    def test_audit_refactoring_plan_built(self, tmp_path: Path):
        """extract findings 生成 refactoring_plan 条目。"""
        orch = CloneGuardOrchestrator(tmp_path)
        finding = _make_finding(severity="extract", similarity=0.95)
        p1, p2, p3 = _patch_l2_engines(orch, echo_ret=([finding], False))
        with p1, p2, p3:
            result = orch.audit(["src/new.py"])
        assert len(result.refactoring_plan) == 1
        assert "src/new.py" in result.refactoring_plan[0]
        assert "src/old.py" in result.refactoring_plan[0]

    def test_audit_persists_result_to_runtime(self, tmp_path: Path):
        """审计结果持久化到 .runtime/clone_guard_audit/audit_*.json。"""
        orch = CloneGuardOrchestrator(tmp_path)
        p1, p2, p3 = _patch_l2_engines(orch)
        with p1, p2, p3:
            result = orch.audit(["src/foo.py"])
        assert result.persisted_path is not None
        assert result.persisted_path.startswith(".runtime/clone_guard_audit/")
        audit_file = tmp_path / result.persisted_path
        assert audit_file.exists()

    def test_audit_persisted_json_has_findings(self, tmp_path: Path):
        """持久化的 JSON 包含 findings 字段。"""
        import json as _json

        orch = CloneGuardOrchestrator(tmp_path)
        finding = _make_finding(severity="review", similarity=0.8)
        p1, p2, p3 = _patch_l2_engines(orch, echo_ret=([finding], False))
        with p1, p2, p3:
            result = orch.audit(["src/new.py"])
        audit_file = tmp_path / result.persisted_path
        data = _json.loads(audit_file.read_text(encoding="utf-8"))
        assert data["health_score"] == "B"
        assert data["findings_count"] == 1
        assert data["findings"][0]["severity"] == "review"

    def test_audit_load_latest_reads_persisted(self, tmp_path: Path):
        """load_latest_audit 读取最近持久化的审计结果。"""
        orch = CloneGuardOrchestrator(tmp_path)
        p1, p2, p3 = _patch_l2_engines(orch)
        with p1, p2, p3:
            orch.audit(["src/foo.py"])
        loaded = orch.load_latest_audit()
        assert loaded is not None
        assert loaded["health_score"] == "A"

    def test_audit_load_latest_no_history(self, tmp_path: Path):
        """无历史审计记录 → load_latest_audit 返回 None。"""
        orch = CloneGuardOrchestrator(tmp_path)
        assert orch.load_latest_audit() is None

    def test_audit_degraded_engines_tracked(self, tmp_path: Path):
        """L2 引擎降级被追踪到 degraded_engines。"""
        orch = CloneGuardOrchestrator(tmp_path)
        p1, p2, p3 = _patch_l2_engines(orch, echo_ret=([], False), redup_ret=([], True), ast_ret=([], True))
        with p1, p2, p3:
            result = orch.audit(["src/foo.py"])
        assert set(result.degraded_engines) == {"redup", "ast_grep"}

    def test_audit_no_l2_engines_returns_empty(self, tmp_path: Path):
        """所有 L2 引擎禁用 → 空审计（不抛异常）。"""
        cfg = CloneGuardConfig(
            echo_guard_enabled=False, ast_grep_enabled=False, redup_enabled=False, mcrit_enabled=False
        )
        orch = CloneGuardOrchestrator(tmp_path, cfg)
        result = orch.audit(["src/foo.py"])
        assert result.checked_files == 1
        assert result.findings == []


class TestOrchestratorAuditScanMode:
    """L2 scan 改造——echo_guard 走 scan()（治本），ast_grep 仍走 detect()（_chunk_files 兜底）。"""

    def test_audit_calls_echo_guard_scan_not_detect(self, tmp_path: Path):
        """L2 审计对 echo_guard 调 scan()（全仓库扫描），不调 detect()。"""
        orch = CloneGuardOrchestrator(tmp_path)
        with (
            patch.object(orch._echo_guard, "scan", return_value=([], False)) as m_scan,
            patch.object(orch._echo_guard, "detect", return_value=([], False)) as m_detect,
            patch.object(orch._ast_grep, "detect", return_value=([], False)),
            patch.object(orch._redup, "detect", return_value=([], False)),
        ):
            orch.audit(["src/foo.py"])
        m_scan.assert_called_once()
        m_detect.assert_not_called()  # echo_guard 在 L2 不走 detect

    def test_audit_ast_grep_still_uses_detect(self, tmp_path: Path):
        """ast_grep 无 scan 方法，L2 仍走 detect()（_chunk_files 兜底）。"""
        orch = CloneGuardOrchestrator(tmp_path)
        with (
            patch.object(orch._echo_guard, "scan", return_value=([], False)),
            patch.object(orch._ast_grep, "detect", return_value=([], False)) as m_sg_detect,
            patch.object(orch._redup, "detect", return_value=([], False)),
        ):
            orch.audit(["src/foo.py"])
        m_sg_detect.assert_called_once()

    def test_check_still_uses_detect_not_scan(self, tmp_path: Path):
        """L1 check() 不走 scan——echo_guard 仍用 detect()（staged 文件少，无上限问题）。"""
        orch = CloneGuardOrchestrator(tmp_path)
        with (
            patch.object(orch._echo_guard, "detect", return_value=([], False)) as m_detect,
            patch.object(orch._echo_guard, "scan", return_value=([], False)) as m_scan,
            patch.object(orch._ast_grep, "detect", return_value=([], False)),
            patch.object(orch._redup, "detect", return_value=([], False)),
        ):
            orch.check(["src/foo.py"])
        m_detect.assert_called_once()
        m_scan.assert_not_called()

    def test_audit_echo_guard_scan_finding_flows_through(self, tmp_path: Path):
        """echo_guard scan() 返回的 finding 流经聚合器到 AuditResult。"""
        orch = CloneGuardOrchestrator(tmp_path)
        finding = _make_finding(severity="extract", similarity=0.95)
        with (
            patch.object(orch._echo_guard, "scan", return_value=([finding], False)),
            patch.object(orch._ast_grep, "detect", return_value=([], False)),
            patch.object(orch._redup, "detect", return_value=([], False)),
        ):
            result = orch.audit(["src/new.py"])
        assert result.health_score == "C"  # 1 个 extract
        assert len(result.findings) == 1

    def test_audit_echo_guard_scan_degraded_tracked(self, tmp_path: Path):
        """echo_guard scan() 降级 → degraded_engines 含 echo_guard，其余引擎正常。"""
        orch = CloneGuardOrchestrator(tmp_path)
        with (
            patch.object(orch._echo_guard, "scan", return_value=([], True)),
            patch.object(orch._ast_grep, "detect", return_value=([], False)),
            patch.object(orch._redup, "detect", return_value=([], False)),
        ):
            result = orch.audit(["src/foo.py"])
        assert "echo_guard" in result.degraded_engines
        assert result.active_engine_count == 2  # ast_grep + redup 活跃


class TestOrchestratorCompare:
    """L3 跨边界审计测试。"""

    def test_compare_no_py_files(self, tmp_path: Path):
        """无 .py 文件 → 空比对。"""
        cfg = CloneGuardConfig(vendetect_enabled=True, vendetect_remote_url="https://x/y")
        orch = CloneGuardOrchestrator(tmp_path, cfg)
        result = orch.compare(["README.md"])
        assert result.checked_files == 0
        assert result.remote_url == "https://x/y"

    def test_compare_cross_repo_findings_separated(self, tmp_path: Path):
        """vendored findings 分离到 cross_repo_findings。"""
        cfg = CloneGuardConfig(
            vendetect_enabled=True,
            vendetect_remote_url="https://x/y",
            relate_enabled=True,
            redup_enabled=True,
        )
        orch = CloneGuardOrchestrator(tmp_path, cfg)
        # vendetect 报 vendored finding；redup 报 T3 finding
        vd_finding = Finding(
            finding_id="VD-1",
            severity="extract",
            clone_type="vendored",
            similarity=0.97,
            source_file="src/new.py",
            source_function="calc",
            source_lineno=10,
            existing_file="vendor/lib.py",
            existing_function="compute",
            existing_lineno=20,
        )
        rd_finding = Finding(
            finding_id="RD-1",
            severity="review",
            clone_type="T3",
            similarity=0.88,
            source_file="src/new.py",
            source_function="calc",
            source_lineno=10,
            existing_file="src/old.py",
            existing_function="compute",
            existing_lineno=20,
        )
        with (
            patch.object(orch._redup, "detect", return_value=([rd_finding], False)),
            patch.object(orch._vendetect, "detect", return_value=([vd_finding], False)),
            patch.object(orch._relate, "detect", return_value=([], False)),
        ):
            result = orch.compare(["src/new.py"])
        assert len(result.findings) == 2
        assert len(result.cross_repo_findings) == 1  # 仅 vendored
        assert result.cross_repo_findings[0].clone_type == "vendored"

    def test_compare_remote_url_propagated(self, tmp_path: Path):
        """remote_url 传播到 CompareResult。"""
        cfg = CloneGuardConfig(vendetect_enabled=True, vendetect_remote_url="https://config/url")
        orch = CloneGuardOrchestrator(tmp_path, cfg)
        with patch.object(orch._redup, "detect", return_value=([], False)):
            result = orch.compare(["src/foo.py"])
        assert result.remote_url == "https://config/url"

    def test_compare_explicit_remote_overrides_config(self, tmp_path: Path):
        """显式 remote_url 覆盖 config。"""
        cfg = CloneGuardConfig(vendetect_enabled=True, vendetect_remote_url="https://config/url")
        orch = CloneGuardOrchestrator(tmp_path, cfg)
        with patch.object(orch._redup, "detect", return_value=([], False)):
            result = orch.compare(["src/foo.py"], remote_url="https://explicit/url")
        assert result.remote_url == "https://explicit/url"

    def test_compare_no_l3_engines_returns_empty(self, tmp_path: Path):
        """所有 L3 引擎禁用 → 空比对。"""
        cfg = CloneGuardConfig(redup_enabled=False, vendetect_enabled=False, relate_enabled=False)
        orch = CloneGuardOrchestrator(tmp_path, cfg)
        result = orch.compare(["src/foo.py"])
        assert result.checked_files == 1
        assert result.findings == []
        assert result.cross_repo_findings == []

    def test_compare_degraded_engines_tracked(self, tmp_path: Path):
        """L3 引擎降级被追踪。"""
        cfg = CloneGuardConfig(
            vendetect_enabled=True,
            vendetect_remote_url="https://x/y",
            relate_enabled=True,
            redup_enabled=True,
        )
        orch = CloneGuardOrchestrator(tmp_path, cfg)
        with (
            patch.object(orch._redup, "detect", return_value=([], True)),
            patch.object(orch._vendetect, "detect", return_value=([], True)),
            patch.object(orch._relate, "detect", return_value=([], True)),
        ):
            result = orch.compare(["src/foo.py"])
        assert set(result.degraded_engines) == {"redup", "vendetect", "relate"}
