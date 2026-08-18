# [A_test] module_id: MOD-GOV_validate_truth_source_cascade_governance | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-514 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.governance.test_validate_truth_source_cascade
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-514 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""
T-V2-012 单元测试 — TruthSourceCascadeValidator
================================================
覆盖场景（验收标准 #8 ≥ 80%）：
  - 0 条决策 / 0 个 affected_files
  - 单条决策 → 单级联
  - 多条决策叠加同一文件 → 多级联
  - 文件 last_updated 早于最新决策 → CASCADE-WARN
  - 文件 last_updated 晚于或等于最新决策 → 无告警
  - frontmatter 缺少 last_updated → INFO（不当 WARN）
  - 报告文件输出（文件创建 + 内容校验）
  - affected_files 多种嵌入格式解析
"""

from __future__ import annotations

import sys
import textwrap
from datetime import UTC, date, datetime
from pathlib import Path

# validate_truth_source_cascade.py imports `_shared` as a top-level package
# (e.g. `from _shared.constants import ...`), which requires scripts/governance
# to be on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "governance"))

from scripts.governance.d11_compliance.validate_truth_source_cascade import (
    RationaleDecision,
    TruthSourceCascadeResult,
    _extract_affected_files,
    _parse_frontmatter_date,
    build_cascade_map,
    detect_outdated_truth_sources,
    generate_report,
    parse_rationale_log,
    run,
)

# ---------------------------------------------------------------------------
# 辅助工厂
# ---------------------------------------------------------------------------


def _make_decision(
    decision_id: str,
    decision_date: date,
    affected_files: list[str],
    decision_summary: str = "测试决策",
) -> RationaleDecision:
    return RationaleDecision(
        decision_id=decision_id,
        decision_date=decision_date,
        decision_summary=decision_summary,
        affected_files=affected_files,
    )


def _write_md_with_fm(path: Path, last_updated: str | None) -> None:
    """在给定路径写入带 frontmatter 的 markdown 文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    if last_updated is None:
        content = "# 标题\n\n正文内容。\n"
    else:
        content = textwrap.dedent(
            f"""\
            ---
            title: 测试文件
            last_updated: {last_updated}
            ---

            # 标题

            正文内容。
            """
        )
    path.write_text(content, encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------
# 1. _extract_affected_files 格式解析测试
# ---------------------------------------------------------------------------


class TestExtractAffectedFiles:
    def test_inline_list_format(self):
        cell = "... affected_files: [docs/a.md, src/b.py] ..."
        result = _extract_affected_files(cell)
        assert result == ["docs/a.md", "src/b.py"]

    def test_inline_list_with_quotes(self):
        cell = 'affected_files: ["docs/a.md", "src/b.py"]'
        result = _extract_affected_files(cell)
        assert result == ["docs/a.md", "src/b.py"]

    def test_code_block_format(self):
        cell = textwrap.dedent(
            """\
            some text
            ```affected_files
            - docs/a.md
            - src/b.py
            ```
            more text
            """
        )
        result = _extract_affected_files(cell)
        assert result == ["docs/a.md", "src/b.py"]

    def test_yaml_block_format(self):
        cell = textwrap.dedent(
            """\
            affected_files:
              - docs/c.md
              - config/d.yaml
            """
        )
        result = _extract_affected_files(cell)
        assert result == ["docs/c.md", "config/d.yaml"]

    def test_no_affected_files_returns_empty(self):
        cell = "这是一条没有 affected_files 字段的决策描述。"
        result = _extract_affected_files(cell)
        assert result == []

    def test_single_file_inline(self):
        cell = "affected_files: [docs/only_one.md]"
        result = _extract_affected_files(cell)
        assert result == ["docs/only_one.md"]


# ---------------------------------------------------------------------------
# 2. parse_rationale_log 测试
# ---------------------------------------------------------------------------


class TestParseRationaleLog:
    def test_empty_file_returns_empty_list(self, tmp_path: Path):
        log_file = tmp_path / "rationale-log.md"
        log_file.write_text("", encoding="utf-8", newline="\n")
        result = parse_rationale_log(log_file)
        assert result == []

    def test_no_affected_files_returns_empty(self, tmp_path: Path):
        log_file = tmp_path / "rationale-log.md"
        log_file.write_text(
            "| R87 | **Wave 2** | **当前结论（2026-04-28）**：普通描述 |\n",
            encoding="utf-8",
            newline="\n",
        )
        result = parse_rationale_log(log_file)
        assert result == []

    def test_entry_below_min_r_number_is_skipped(self, tmp_path: Path):
        log_file = tmp_path / "rationale-log.md"
        log_file.write_text(
            "| R50 | **Old** | **（2026-01-01）** affected_files: [docs/x.md] |\n",
            encoding="utf-8",
            newline="\n",
        )
        result = parse_rationale_log(log_file)
        assert result == []

    def test_valid_entry_with_inline_affected_files(self, tmp_path: Path):
        log_file = tmp_path / "rationale-log.md"
        log_file.write_text(
            "| R87 | **Wave 2** | **当前结论（2026-04-28）**： affected_files: [docs/a.md, src/b.py] |\n",
            encoding="utf-8",
            newline="\n",
        )
        result = parse_rationale_log(log_file)
        assert len(result) == 1
        d = result[0]
        assert d.decision_id == "R87"
        assert d.decision_date == date(2026, 4, 28)
        assert "docs/a.md" in d.affected_files
        assert "src/b.py" in d.affected_files

    def test_multiple_entries_parsed(self, tmp_path: Path):
        log_file = tmp_path / "rationale-log.md"
        log_file.write_text(
            "| R87 | A | **（2026-04-28）** affected_files: [docs/a.md] |\n"
            "| R88 | B | **（2026-04-29）** affected_files: [docs/b.md] |\n",
            encoding="utf-8",
            newline="\n",
        )
        result = parse_rationale_log(log_file)
        assert len(result) == 2
        assert result[0].decision_id == "R87"
        assert result[1].decision_id == "R88"

    def test_nonexistent_file_returns_empty(self, tmp_path: Path):
        result = parse_rationale_log(tmp_path / "nonexistent.md")
        assert result == []

    def test_separator_line_is_ignored(self, tmp_path: Path):
        log_file = tmp_path / "rationale-log.md"
        log_file.write_text(
            "|------|------|------|\n| R87 | A | **（2026-04-28）** affected_files: [docs/a.md] |\n",
            encoding="utf-8",
            newline="\n",
        )
        result = parse_rationale_log(log_file)
        assert len(result) == 1


# ---------------------------------------------------------------------------
# 3. build_cascade_map 测试
# ---------------------------------------------------------------------------


class TestBuildCascadeMap:
    def test_empty_decisions_returns_empty_map(self):
        result = build_cascade_map([])
        assert result == {}

    def test_single_decision_single_file(self):
        d = _make_decision("R87", date(2026, 4, 28), ["docs/a.md"])
        cascade = build_cascade_map([d])
        assert "docs/a.md" in cascade
        assert cascade["docs/a.md"] == [d]

    def test_single_decision_multiple_files(self):
        d = _make_decision("R87", date(2026, 4, 28), ["docs/a.md", "src/b.py"])
        cascade = build_cascade_map([d])
        assert "docs/a.md" in cascade
        assert "src/b.py" in cascade

    def test_multiple_decisions_same_file_sorted_by_date(self):
        d1 = _make_decision("R87", date(2026, 4, 28), ["docs/x.md"])
        d2 = _make_decision("R88", date(2026, 4, 29), ["docs/x.md"])
        d3 = _make_decision("R89", date(2026, 4, 27), ["docs/x.md"])
        cascade = build_cascade_map([d1, d2, d3])
        dates = [d.decision_date for d in cascade["docs/x.md"]]
        assert dates == sorted(dates)

    def test_multiple_decisions_disjoint_files(self):
        d1 = _make_decision("R87", date(2026, 4, 28), ["docs/a.md"])
        d2 = _make_decision("R88", date(2026, 4, 29), ["docs/b.md"])
        cascade = build_cascade_map([d1, d2])
        assert "docs/a.md" in cascade
        assert "docs/b.md" in cascade
        assert cascade["docs/a.md"] == [d1]
        assert cascade["docs/b.md"] == [d2]


# ---------------------------------------------------------------------------
# 4. _parse_frontmatter_date 测试
# ---------------------------------------------------------------------------


class TestParseFrontmatterDate:
    def test_valid_date(self, tmp_path: Path):
        f = tmp_path / "test.md"
        _write_md_with_fm(f, "2026-04-20")
        assert _parse_frontmatter_date(f) == date(2026, 4, 20)

    def test_missing_last_updated_returns_none(self, tmp_path: Path):
        f = tmp_path / "test.md"
        _write_md_with_fm(f, None)
        assert _parse_frontmatter_date(f) is None

    def test_nonexistent_file_returns_none(self, tmp_path: Path):
        assert _parse_frontmatter_date(tmp_path / "ghost.md") is None

    def test_no_frontmatter_returns_none(self, tmp_path: Path):
        f = tmp_path / "test.md"
        f.write_text("# 无 frontmatter\n正文。\n", encoding="utf-8", newline="\n")
        assert _parse_frontmatter_date(f) is None


# ---------------------------------------------------------------------------
# 5. detect_outdated_truth_sources 测试
# ---------------------------------------------------------------------------


class TestDetectOutdatedTruthSources:
    def test_outdated_file_triggers_warn(self, tmp_path: Path):
        f = tmp_path / "docs" / "a.md"
        _write_md_with_fm(f, "2026-04-20")
        d = _make_decision("R87", date(2026, 4, 28), ["docs/a.md"])
        cascade = build_cascade_map([d])
        warnings, rows = detect_outdated_truth_sources(cascade, tmp_path)
        assert len(warnings) == 1
        assert "CASCADE-WARN" in warnings[0]
        assert "docs/a.md" in warnings[0]
        assert rows[0]["status"] == "⚠️ OUTDATED"

    def test_up_to_date_file_no_warn(self, tmp_path: Path):
        f = tmp_path / "docs" / "b.md"
        _write_md_with_fm(f, "2026-04-30")
        d = _make_decision("R87", date(2026, 4, 28), ["docs/b.md"])
        cascade = build_cascade_map([d])
        warnings, rows = detect_outdated_truth_sources(cascade, tmp_path)
        assert len(warnings) == 0
        assert rows[0]["status"] == "✅ OK"

    def test_missing_last_updated_is_info_not_warn(self, tmp_path: Path):
        f = tmp_path / "docs" / "c.md"
        _write_md_with_fm(f, None)
        d = _make_decision("R87", date(2026, 4, 28), ["docs/c.md"])
        cascade = build_cascade_map([d])
        warnings, rows = detect_outdated_truth_sources(cascade, tmp_path)
        assert len(warnings) == 0
        assert "INFO" in rows[0]["status"]

    def test_same_date_no_warn(self, tmp_path: Path):
        f = tmp_path / "docs" / "d.md"
        _write_md_with_fm(f, "2026-04-28")
        d = _make_decision("R87", date(2026, 4, 28), ["docs/d.md"])
        cascade = build_cascade_map([d])
        warnings, _ = detect_outdated_truth_sources(cascade, tmp_path)
        assert len(warnings) == 0

    def test_multiple_decisions_latest_date_used(self, tmp_path: Path):
        f = tmp_path / "docs" / "e.md"
        _write_md_with_fm(f, "2026-04-28")
        d1 = _make_decision("R87", date(2026, 4, 25), ["docs/e.md"])
        d2 = _make_decision("R88", date(2026, 4, 29), ["docs/e.md"])
        cascade = build_cascade_map([d1, d2])
        warnings, rows = detect_outdated_truth_sources(cascade, tmp_path)
        assert len(warnings) == 1
        assert "R88" in warnings[0]

    def test_empty_cascade_returns_empty(self):
        warnings, rows = detect_outdated_truth_sources({})
        assert warnings == []
        assert rows == []


# ---------------------------------------------------------------------------
# 6. generate_report 测试
# ---------------------------------------------------------------------------


class TestGenerateReport:
    def _make_result(
        self,
        warnings: list[str] | None = None,
        rows: list[dict] | None = None,
    ) -> TruthSourceCascadeResult:
        return TruthSourceCascadeResult(
            report_date=datetime(2026, 4, 27, 10, 0, 0, tzinfo=UTC),
            decisions_scanned=3,
            files_impacted=2,
            warnings=warnings or [],
            cascade_rows=rows or [],
        )

    def test_report_file_created(self, tmp_path: Path):
        result = self._make_result()
        path = generate_report(result, tmp_path)
        assert path.exists()
        assert path.suffix == ".md"

    def test_report_contains_summary(self, tmp_path: Path):
        result = self._make_result()
        path = generate_report(result, tmp_path)
        content = path.read_text(encoding="utf-8")
        assert "扫描决策数" in content
        assert "受影响文件数" in content

    def test_report_contains_warning(self, tmp_path: Path):
        result = self._make_result(
            warnings=["[CASCADE-WARN] 真源 docs/a.md 受 R87 影响但未更新（2026-04-20 < 2026-04-28）"]
        )
        path = generate_report(result, tmp_path)
        content = path.read_text(encoding="utf-8")
        assert "CASCADE-WARN" in content
        assert "docs/a.md" in content

    def test_report_no_warn_has_placeholder(self, tmp_path: Path):
        result = self._make_result(warnings=[])
        path = generate_report(result, tmp_path)
        content = path.read_text(encoding="utf-8")
        assert "无 CASCADE-WARN" in content

    def test_report_contains_cascade_table(self, tmp_path: Path):
        rows = [
            {
                "file": "docs/a.md",
                "decisions": "R87",
                "latest_date": "2026-04-28",
                "last_updated": "2026-04-20",
                "status": "⚠️ OUTDATED",
            }
        ]
        result = self._make_result(rows=rows)
        path = generate_report(result, tmp_path)
        content = path.read_text(encoding="utf-8")
        assert "docs/a.md" in content
        assert "⚠️ OUTDATED" in content

    def test_duplicate_date_gets_timestamp_suffix(self, tmp_path: Path):
        result = self._make_result()
        path1 = generate_report(result, tmp_path)
        path2 = generate_report(result, tmp_path)
        assert path1 != path2

    def test_report_utf8_encoding(self, tmp_path: Path):
        result = self._make_result(warnings=["[CASCADE-WARN] 真源 docs/测试文件.md 受 R87 影响但未更新"])
        path = generate_report(result, tmp_path)
        content = path.read_text(encoding="utf-8")
        assert "测试文件" in content


# ---------------------------------------------------------------------------
# 7. run() 集成测试
# ---------------------------------------------------------------------------


class TestRunIntegration:
    def _make_log(self, tmp_path: Path, entries: list[str]) -> Path:
        log = tmp_path / "rationale-log.md"
        log.write_text("\n".join(entries) + "\n", encoding="utf-8", newline="\n")
        return log

    def test_run_with_no_affected_files(self, tmp_path: Path):
        log = self._make_log(
            tmp_path,
            ["| R87 | A | **（2026-04-28）**：普通决策 |"],
        )
        reports = tmp_path / "reports"
        result = run(log, reports, tmp_path, quiet=True)
        assert result.decisions_scanned == 0
        assert result.files_impacted == 0
        assert result.warnings == []

    def test_run_with_one_outdated_file(self, tmp_path: Path):
        f = tmp_path / "docs" / "x.md"
        _write_md_with_fm(f, "2026-04-20")
        log = self._make_log(
            tmp_path,
            ["| R87 | A | **（2026-04-28）**： affected_files: [docs/x.md] |"],
        )
        reports = tmp_path / "reports"
        result = run(log, reports, tmp_path, quiet=True)
        assert result.decisions_scanned == 1
        assert result.files_impacted == 1
        assert len(result.warnings) == 1
        assert (reports / "truth_source_cascade_").parent.exists()

    def test_run_with_multi_cascade(self, tmp_path: Path):
        f1 = tmp_path / "docs" / "a.md"
        f2 = tmp_path / "docs" / "b.md"
        _write_md_with_fm(f1, "2026-04-20")
        _write_md_with_fm(f2, "2026-04-30")
        log = self._make_log(
            tmp_path,
            [
                "| R87 | A | **（2026-04-28）** affected_files: [docs/a.md, docs/b.md] |",
                "| R88 | B | **（2026-04-29）** affected_files: [docs/a.md] |",
            ],
        )
        reports = tmp_path / "reports"
        result = run(log, reports, tmp_path, quiet=True)
        assert result.decisions_scanned == 2
        assert result.files_impacted == 2
        # docs/a.md: latest = R88 2026-04-29 > last_updated 2026-04-20 → WARN
        # docs/b.md: latest = R87 2026-04-28 < last_updated 2026-04-30 → OK
        assert len(result.warnings) == 1
        assert "docs/a.md" in result.warnings[0]

    def test_run_exit_code_is_always_zero(self, tmp_path: Path):
        """experimental warn-only：即使有告警，exit code = 0（本测试验证不抛出异常）。"""
        log = self._make_log(tmp_path, [])
        reports = tmp_path / "reports"
        try:
            run(log, reports, tmp_path, quiet=True)
        except SystemExit as e:
            assert e.code == 0
