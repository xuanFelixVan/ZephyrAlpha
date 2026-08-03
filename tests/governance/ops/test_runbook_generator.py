# [A_test] module_id: MOD-GOV_runbook_generator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_runbook_generator
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] runbook_format_markdown_yaml;frontmatter_fields_complete;remediation_options_generated
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_runbook_generator.py
# [A_module] module_id=MOD-INF-033 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound

import os
import tempfile
import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import yaml

from zephyr.infrastructure.rollback.runbook_generator import (
    build_runbook_frontmatter,
    generate_bulk_runbook,
    generate_runbook,
)


def _make_event(
    detector_id="db_schema_drift",
    severity_value="HIGH",
    state_value="DETECTED",
    scan_level_value="STANDARD",
    auto_fixable=True,
    description="Schema mismatch detected",
    details="Column 'foo' missing in table 'bar'",
    event_id=None,
):
    event = MagicMock()
    event.event_id = event_id or uuid.UUID("12345678-1234-5678-1234-567812345678")
    event.detector_id = detector_id
    event.timestamp = datetime(2026, 1, 15, 10, 30, 0, tzinfo=UTC)
    event.severity = MagicMock(value=severity_value)
    event.state = MagicMock(value=state_value)
    event.scan_level = MagicMock(value=scan_level_value)
    event.auto_fixable = auto_fixable
    event.description = description
    event.details = details
    event.roi_score = 0.85
    return event


class TestBuildRunbookFrontmatter:
    def test_contains_required_fields(self):
        event = _make_event()
        fm = build_runbook_frontmatter(event)
        assert "drift_id" in fm
        assert "module_id" in fm
        assert "detector_id" in fm
        assert "timestamp" in fm
        assert "severity" in fm
        assert "state" in fm
        assert "scan_level" in fm
        assert "auto_fixable" in fm

    def test_values_match_event(self):
        event = _make_event(detector_id="dep_version_drift", severity_value="MEDIUM")
        fm = build_runbook_frontmatter(event)
        assert fm["detector_id"] == "dep_version_drift"
        assert fm["severity"] == "MEDIUM"
        assert fm["auto_fixable"] is True

    def test_module_id_is_fixed(self):
        event = _make_event()
        fm = build_runbook_frontmatter(event)
        assert fm["module_id"] == "MOD-INF-023"

    def test_roi_score_included(self):
        event = _make_event()
        fm = build_runbook_frontmatter(event)
        assert fm["roi_score"] == 0.85


class TestGenerateRunbook:
    def test_produces_markdown_with_frontmatter(self):
        event = _make_event()
        md = generate_runbook(event)
        assert md.startswith("---")
        parts = md.split("---")
        assert len(parts) >= 3

    def test_frontmatter_is_valid_yaml(self):
        event = _make_event()
        md = generate_runbook(event)
        parts = md.split("---")
        yaml_content = parts[1].strip()
        parsed = yaml.safe_load(yaml_content)
        assert isinstance(parsed, dict)
        assert parsed["drift_id"] == str(event.event_id)

    def test_contains_diagnosis_section(self):
        event = _make_event()
        md = generate_runbook(event)
        assert "## Diagnosis" in md

    def test_contains_remediation_section(self):
        event = _make_event()
        md = generate_runbook(event)
        assert "## Remediation" in md

    def test_contains_rollback_section(self):
        event = _make_event()
        md = generate_runbook(event)
        assert "## Rollback" in md

    def test_contains_references_section(self):
        event = _make_event()
        md = generate_runbook(event)
        assert "## References" in md

    def test_known_detector_has_specific_remediation(self):
        event = _make_event(detector_id="db_schema_drift")
        md = generate_runbook(event)
        assert "Rebuild migration from ORM" in md

    def test_unknown_detector_has_generic_remediation(self):
        event = _make_event(detector_id="custom_detector_xyz")
        md = generate_runbook(event)
        assert "Triage drift event" in md

    def test_auto_fixable_rollback_mentions_revert(self):
        event = _make_event(auto_fixable=True)
        md = generate_runbook(event)
        assert "git revert" in md

    def test_non_auto_fixable_rollback(self):
        event = _make_event(auto_fixable=False)
        md = generate_runbook(event)
        assert "No auto-fix applied" in md

    def test_description_included(self):
        event = _make_event(description="Custom drift description")
        md = generate_runbook(event)
        assert "Custom drift description" in md

    def test_details_included_as_code_block(self):
        event = _make_event(details="Column X missing")
        md = generate_runbook(event)
        assert "Column X missing" in md


class TestGenerateBulkRunbook:
    def test_creates_files(self):
        events = [_make_event(event_id=uuid.UUID(f"00000000-0000-0000-0000-{i:012d}")) for i in range(1, 4)]
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = generate_bulk_runbook(events, tmpdir)
            assert len(paths) == 3
            for p in paths:
                assert os.path.isfile(p)

    def test_file_content_is_valid_runbook(self):
        event = _make_event()
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = generate_bulk_runbook([event], tmpdir)
            with open(paths[0], encoding="utf-8") as f:
                content = f.read()
            assert "## Diagnosis" in content
            assert "## Remediation" in content

    def test_empty_events_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = generate_bulk_runbook([], tmpdir)
            assert paths == []

    def test_output_dir_created_if_missing(self):
        event = _make_event()
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "nested", "dir")
            paths = generate_bulk_runbook([event], subdir)
            assert len(paths) == 1
            assert os.path.isfile(paths[0])
