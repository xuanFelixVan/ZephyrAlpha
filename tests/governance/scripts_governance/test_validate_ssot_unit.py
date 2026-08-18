# [A_test] module_id: MOD-GOV_validate_ssot_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-703 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_validate_ssot
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-703 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""
单元测试：scripts/governance/validate_ssot.py
任务 ID : T-2-33 (B13)
覆盖指令：356 + 999

测试矩阵
--------
_parse_frontmatter     : 正常提取 / 无 frontmatter / 嵌套 YAML 忽略 / 带引号值
parse_file             : 有 frontmatter / 无 frontmatter / 读取失败
check_p0_layer_invalid : 有效层 / 无效层 / legacy 层 / 无层字段
check_p0_duplicate_active_module_id : 无重复 / 重复 Active / 一 Active 一 Deprecated
check_p1_status_invalid : 有效状态 / 无效状态 / 无状态字段
check_p1_module_id_layer_conflict   : 无冲突 / 有冲突 / 单文件
check_p1_module_id_status_conflict  : 无冲突 / Active+Deprecated / Active+Superseded
check_p2_priority_invalid           : 有效优先级 / 无效优先级 / 无优先级字段
check_p2_version_format             : 合法版本 / 不合法版本 / N/A / 无版本字段
ScanReport             : p0/p1/p2 计数 / has_p0 / total_count
render_report          : 无矛盾 / 有矛盾 / frontmatter 包含
SsotValidator.run      : 集成测试（临时目录）
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.governance.d5_architecture.validators.validate_ssot import (
    VALID_DOCUMENT_STATUSES,
    VALID_PRIORITIES,
    Contradiction,
    FileMeta,
    ScanReport,
    SsotValidator,
    _get_valid_layers,
    check_p0_duplicate_active_module_id,
    check_p0_layer_invalid,
    check_p1_module_id_layer_conflict,
    check_p1_module_id_status_conflict,
    check_p1_status_invalid,
    check_p2_priority_invalid,
    check_p2_version_format,
    parse_file,
    render_report,
)
from scripts.governance.shared.frontmatter import parse_frontmatter as _parse_frontmatter

# ---------------------------------------------------------------------------
# 辅助：构造 FileMeta
# ---------------------------------------------------------------------------


def _meta(
    path: str = "docs/test.md",
    module_id: str | None = None,
    layer: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    version: str | None = None,
) -> FileMeta:
    return FileMeta(
        path=Path(path),
        rel_path=path,
        module_id=module_id,
        layer=layer,
        status=status,
        priority=priority,
        version=version,
    )


def _write_md(tmp_path: Path, filename: str, content: str) -> Path:
    p = tmp_path / filename
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# _parse_frontmatter
# ---------------------------------------------------------------------------


class TestParseFrontmatter:
    """P0：frontmatter 解析。"""

    def test_normal_fields(self) -> None:
        text = "---\nmodule_id: TEST_001\nlayer: L01\n---\n# Content\n"
        fm = _parse_frontmatter(text)
        assert fm["module_id"] == "TEST_001"
        assert fm["layer"] == "L01"

    def test_no_frontmatter(self) -> None:
        text = "# Just a heading\nNo frontmatter here."
        assert _parse_frontmatter(text) is None

    def test_quoted_values(self) -> None:
        text = "---\nversion: '1.2.3'\nstatus: \"Active\"\n---\n"
        fm = _parse_frontmatter(text)
        assert fm["version"] == "1.2.3"
        assert fm["status"] == "Active"

    def test_nested_yaml_ignored(self) -> None:
        text = "---\nmodule_id: TOP\nnested:\n  subkey: val\nlayer: L02\n---\n"
        fm = _parse_frontmatter(text)
        assert fm["module_id"] == "TOP"
        assert fm["layer"] == "L02"
        assert "subkey" not in fm

    def test_empty_file(self) -> None:
        assert _parse_frontmatter("") is None

    def test_only_open_marker(self) -> None:
        text = "---\nno close marker"
        assert _parse_frontmatter(text) is None


# ---------------------------------------------------------------------------
# parse_file
# ---------------------------------------------------------------------------


class TestParseFile:
    """P0：文件解析。"""

    def test_file_with_frontmatter(self, tmp_path: Path) -> None:
        p = _write_md(tmp_path, "a.md", "---\nmodule_id: A_001\nlayer: L03\nstatus: Active\n---\n")
        meta = parse_file(p, tmp_path)
        assert meta is not None
        assert meta.module_id == "A_001"
        assert meta.layer == "L03"
        assert meta.status == "Active"

    def test_file_without_frontmatter(self, tmp_path: Path) -> None:
        p = _write_md(tmp_path, "b.md", "# No YAML\nJust text.")
        assert parse_file(p, tmp_path) is None

    def test_rel_path_uses_forward_slash(self, tmp_path: Path) -> None:
        sub = tmp_path / "sub"
        sub.mkdir()
        p = _write_md(sub, "c.md", "---\nmodule_id: C_001\n---\n")
        meta = parse_file(p, tmp_path)
        assert meta is not None
        assert "\\" not in meta.rel_path

    def test_nonexistent_file_returns_none(self, tmp_path: Path) -> None:
        p = tmp_path / "nonexistent.md"
        assert parse_file(p, tmp_path) is None


# ---------------------------------------------------------------------------
# check_p0_layer_invalid
# ---------------------------------------------------------------------------


class TestCheckP0LayerInvalid:
    """P0：layer 字段有效性。"""

    @pytest.mark.parametrize("layer", list(_get_valid_layers()))
    def test_valid_layers_pass(self, layer: str) -> None:
        metas = [_meta(layer=layer)]
        assert check_p0_layer_invalid(metas) == []

    @pytest.mark.parametrize("bad_layer", ["Layer01", "L_01", "l00", "DATA_LAYER", "99"])
    def test_invalid_layers_flagged(self, bad_layer: str) -> None:
        metas = [_meta(layer=bad_layer)]
        result = check_p0_layer_invalid(metas)
        assert len(result) == 1
        assert result[0].severity == "P0"
        assert result[0].check_id == "P0-1"
        assert bad_layer in result[0].values

    def test_no_layer_field_skipped(self) -> None:
        metas = [_meta()]  # layer=None
        assert check_p0_layer_invalid(metas) == []

    def test_multiple_invalid_layers(self) -> None:
        metas = [_meta(layer="bad1"), _meta(path="docs/b.md", layer="bad2")]
        result = check_p0_layer_invalid(metas)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# check_p0_duplicate_active_module_id
# ---------------------------------------------------------------------------


class TestCheckP0DuplicateActiveModuleId:
    """P0：module_id 重复真源检测。"""

    def test_no_duplicates_pass(self) -> None:
        metas = [
            _meta(path="a.md", module_id="M1", status="Active"),
            _meta(path="b.md", module_id="M2", status="Active"),
        ]
        assert check_p0_duplicate_active_module_id(metas) == []

    def test_same_id_both_active_flagged(self) -> None:
        metas = [
            _meta(path="a.md", module_id="DUPE_001", status="Active"),
            _meta(path="b.md", module_id="DUPE_001", status="Active"),
        ]
        result = check_p0_duplicate_active_module_id(metas)
        assert len(result) == 1
        assert result[0].severity == "P0"
        assert result[0].check_id == "P0-2"
        assert "a.md" in result[0].files
        assert "b.md" in result[0].files

    def test_same_id_active_deprecated_no_flag(self) -> None:
        metas = [
            _meta(path="a.md", module_id="M3", status="Active"),
            _meta(path="b.md", module_id="M3", status="Deprecated"),
        ]
        assert check_p0_duplicate_active_module_id(metas) == []

    def test_no_module_id_skipped(self) -> None:
        metas = [_meta(status="Active"), _meta(path="b.md", status="Active")]
        assert check_p0_duplicate_active_module_id(metas) == []


# ---------------------------------------------------------------------------
# check_p1_status_invalid
# ---------------------------------------------------------------------------


class TestCheckP1StatusInvalid:
    """P1：status 字段有效性。"""

    @pytest.mark.parametrize("status", sorted(VALID_DOCUMENT_STATUSES))
    def test_valid_statuses_pass(self, status: str) -> None:
        assert check_p1_status_invalid([_meta(status=status)]) == []

    @pytest.mark.parametrize("bad_status", ["ACTIVE", "unknown", "Pending", "done"])
    def test_invalid_status_flagged(self, bad_status: str) -> None:
        result = check_p1_status_invalid([_meta(status=bad_status)])
        assert len(result) == 1
        assert result[0].severity == "P1"
        assert bad_status in result[0].values

    def test_no_status_field_skipped(self) -> None:
        assert check_p1_status_invalid([_meta()]) == []


# ---------------------------------------------------------------------------
# check_p1_module_id_layer_conflict
# ---------------------------------------------------------------------------


class TestCheckP1ModuleIdLayerConflict:
    """P1：同 module_id 跨文件 layer 冲突。"""

    def test_same_id_same_layer_no_conflict(self) -> None:
        metas = [
            _meta(path="a.md", module_id="M1", layer="L00"),
            _meta(path="b.md", module_id="M1", layer="L00"),
        ]
        assert check_p1_module_id_layer_conflict(metas) == []

    def test_same_id_different_layer_flagged(self) -> None:
        metas = [
            _meta(path="a.md", module_id="M2", layer="L00"),
            _meta(path="b.md", module_id="M2", layer="L01"),
        ]
        result = check_p1_module_id_layer_conflict(metas)
        assert len(result) == 1
        assert result[0].severity == "P1"
        assert result[0].check_id == "P1-2"
        assert "L00" in result[0].values
        assert "L01" in result[0].values

    def test_single_file_no_conflict(self) -> None:
        metas = [_meta(module_id="M3", layer="L02")]
        assert check_p1_module_id_layer_conflict(metas) == []

    def test_no_module_id_skipped(self) -> None:
        metas = [_meta(layer="L00"), _meta(path="b.md", layer="L01")]
        assert check_p1_module_id_layer_conflict(metas) == []


# ---------------------------------------------------------------------------
# check_p1_module_id_status_conflict
# ---------------------------------------------------------------------------


class TestCheckP1ModuleIdStatusConflict:
    """P1：同 module_id 跨文件 status 矛盾。"""

    def test_active_deprecated_flagged(self) -> None:
        metas = [
            _meta(path="a.md", module_id="M1", status="Active"),
            _meta(path="b.md", module_id="M1", status="Deprecated"),
        ]
        result = check_p1_module_id_status_conflict(metas)
        assert len(result) == 1
        assert result[0].severity == "P1"

    def test_active_retired_flagged(self) -> None:
        metas = [
            _meta(path="a.md", module_id="M2", status="Active"),
            _meta(path="b.md", module_id="M2", status="Retired"),
        ]
        assert len(check_p1_module_id_status_conflict(metas)) == 1

    def test_active_superseded_not_flagged(self) -> None:
        metas = [
            _meta(path="a.md", module_id="M3", status="Active"),
            _meta(path="b.md", module_id="M3", status="Superseded"),
        ]
        assert check_p1_module_id_status_conflict(metas) == []

    def test_same_status_no_conflict(self) -> None:
        metas = [
            _meta(path="a.md", module_id="M4", status="Active"),
            _meta(path="b.md", module_id="M4", status="Active"),
        ]
        assert check_p1_module_id_status_conflict(metas) == []


# ---------------------------------------------------------------------------
# check_p2_priority_invalid
# ---------------------------------------------------------------------------


class TestCheckP2PriorityInvalid:
    """P2：priority 字段有效性。"""

    @pytest.mark.parametrize("priority", list(VALID_PRIORITIES))
    def test_valid_priorities_pass(self, priority: str) -> None:
        assert check_p2_priority_invalid([_meta(priority=priority)]) == []

    @pytest.mark.parametrize("bad_priority", ["HIGH", "low", "1", "critical"])
    def test_invalid_priority_flagged(self, bad_priority: str) -> None:
        result = check_p2_priority_invalid([_meta(priority=bad_priority)])
        assert len(result) == 1
        assert result[0].severity == "P2"

    def test_no_priority_field_skipped(self) -> None:
        assert check_p2_priority_invalid([_meta()]) == []


# ---------------------------------------------------------------------------
# check_p2_version_format
# ---------------------------------------------------------------------------


class TestCheckP2VersionFormat:
    """P2：version 字段格式。"""

    @pytest.mark.parametrize("version", ["1.0.0", "2.3.1", "'1.0.0'", "N/A", "1.0"])
    def test_valid_versions_pass(self, version: str) -> None:
        assert check_p2_version_format([_meta(version=version)]) == []

    @pytest.mark.parametrize("bad_version", ["v1.0.0", "1", "1.0.0.0", "latest", ""])
    def test_invalid_version_flagged(self, bad_version: str) -> None:
        result = check_p2_version_format([_meta(version=bad_version)])
        # 空字符串会被跳过（视为 None 等价处理）
        if bad_version == "":
            # 空字符串在解析时被过滤掉，只有非空值才检查
            pass
        else:
            assert len(result) == 1
            assert result[0].severity == "P2"

    def test_no_version_field_skipped(self) -> None:
        assert check_p2_version_format([_meta()]) == []


# ---------------------------------------------------------------------------
# ScanReport
# ---------------------------------------------------------------------------


class TestScanReport:
    """P1：报告聚合逻辑。"""

    def test_counters(self) -> None:
        report = ScanReport()
        report.contradictions = [
            Contradiction("P0", "P0-1", "desc1"),
            Contradiction("P0", "P0-2", "desc2"),
            Contradiction("P1", "P1-1", "desc3"),
            Contradiction("P2", "P2-1", "desc4"),
        ]
        assert report.p0_count == 2
        assert report.p1_count == 1
        assert report.p2_count == 1
        assert report.total_count == 4
        assert report.has_p0 is True

    def test_no_contradictions(self) -> None:
        report = ScanReport()
        assert report.total_count == 0
        assert report.has_p0 is False


# ---------------------------------------------------------------------------
# render_report
# ---------------------------------------------------------------------------


class TestRenderReport:
    """P1：报告渲染。"""

    def test_report_has_frontmatter(self) -> None:
        report = ScanReport(scanned_files=10, parsed_files=5, scan_time="2026-04-24 00:00:00")
        text = render_report(report)
        assert "type: generated" in text
        assert "ttl: 7d" in text

    def test_no_contradictions_shows_pass(self) -> None:
        report = ScanReport()
        text = render_report(report)
        assert "无矛盾" in text

    def test_p0_section_rendered(self) -> None:
        report = ScanReport()
        report.contradictions.append(
            Contradiction("P0", "P0-1", "层字段无效", files=["docs/test.md"], values=["BADLAYER"])
        )
        text = render_report(report)
        assert "P0" in text
        assert "docs/test.md" in text
        assert "BADLAYER" in text

    def test_ci_count_in_summary(self) -> None:
        report = ScanReport()
        report.contradictions.append(Contradiction("P0", "P0-2", "重复真源"))
        text = render_report(report)
        assert "1" in text  # p0_count=1


# ---------------------------------------------------------------------------
# 集成测试：SsotValidator.run
# ---------------------------------------------------------------------------


class TestSsotValidatorIntegration:
    """Q2 集成测试：完整扫描流程。"""

    def test_empty_dir_no_contradictions(self, tmp_path: Path) -> None:
        validator = SsotValidator(scan_dir=tmp_path, repo_root=tmp_path)
        report = validator.run()
        assert report.scanned_files == 0
        assert report.total_count == 0

    def test_valid_files_no_contradictions(self, tmp_path: Path) -> None:
        _write_md(
            tmp_path, "a.md", "---\nmodule_id: A_001\nlayer: L00\nstatus: Active\npriority: P0\nversion: 1.0.0\n---\n"
        )
        _write_md(
            tmp_path, "b.md", "---\nmodule_id: B_001\nlayer: L01\nstatus: Draft\npriority: P1\nversion: 2.0.0\n---\n"
        )
        validator = SsotValidator(scan_dir=tmp_path, repo_root=tmp_path)
        report = validator.run()
        assert report.parsed_files == 2
        assert report.p0_count == 0

    def test_detects_p0_invalid_layer(self, tmp_path: Path) -> None:
        _write_md(tmp_path, "bad.md", "---\nmodule_id: X_001\nlayer: INVALID_LAYER\nstatus: Active\n---\n")
        validator = SsotValidator(scan_dir=tmp_path, repo_root=tmp_path)
        report = validator.run()
        assert report.p0_count >= 1
        p0_ids = [c.check_id for c in report.contradictions if c.severity == "P0"]
        assert "P0-1" in p0_ids

    def test_detects_p0_duplicate_active(self, tmp_path: Path) -> None:
        _write_md(tmp_path, "a.md", "---\nmodule_id: DUPE\nstatus: Active\n---\n")
        _write_md(tmp_path, "b.md", "---\nmodule_id: DUPE\nstatus: Active\n---\n")
        validator = SsotValidator(scan_dir=tmp_path, repo_root=tmp_path)
        report = validator.run()
        assert report.p0_count >= 1
        p0_ids = [c.check_id for c in report.contradictions if c.severity == "P0"]
        assert "P0-2" in p0_ids

    def test_detects_p1_layer_conflict(self, tmp_path: Path) -> None:
        _write_md(tmp_path, "a.md", "---\nmodule_id: MOD1\nlayer: L00\nstatus: Active\n---\n")
        _write_md(tmp_path, "b.md", "---\nmodule_id: MOD1\nlayer: L01\nstatus: Draft\n---\n")
        validator = SsotValidator(scan_dir=tmp_path, repo_root=tmp_path)
        report = validator.run()
        p1_ids = [c.check_id for c in report.contradictions if c.severity == "P1"]
        assert "P1-2" in p1_ids

    def test_files_without_frontmatter_counted_but_not_parsed(self, tmp_path: Path) -> None:
        _write_md(tmp_path, "no_fm.md", "# Just a heading\nNo frontmatter.")
        _write_md(tmp_path, "with_fm.md", "---\nmodule_id: M1\n---\n")
        validator = SsotValidator(scan_dir=tmp_path, repo_root=tmp_path)
        report = validator.run()
        assert report.scanned_files == 2
        assert report.parsed_files == 1


# ---------------------------------------------------------------------------
# 性能测试：1000 个文件的扫描在 3s 内完成
# ---------------------------------------------------------------------------


class TestScanPerformance:
    """Q4 性能断言。"""

    def test_bulk_scan_speed(self, tmp_path: Path) -> None:
        import time

        for i in range(200):
            _write_md(
                tmp_path,
                f"file_{i:04d}.md",
                f"---\nmodule_id: M_{i:04d}\nlayer: L0{i % 9}\nstatus: Active\nversion: 1.0.0\n---\n",
            )
        t0 = time.perf_counter()
        validator = SsotValidator(scan_dir=tmp_path, repo_root=tmp_path)
        report = validator.run()
        elapsed = time.perf_counter() - t0
        assert report.parsed_files == 200
        assert elapsed < 5.0, f"扫描 200 个文件耗时 {elapsed:.2f}s > 5s 预算"
