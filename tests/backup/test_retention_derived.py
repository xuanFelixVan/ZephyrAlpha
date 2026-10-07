"""tests/backup/test_retention_derived.py — C440 纯函数单测（derive/validate/parse_keep）。"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.backup.retention_derived import (
    build_shadow_doc,
    derive_retention_p95,
    parse_keep_text,
    validate_config,
)

SAMPLE_CONFIG = {
    "working_vault": {"retention_days": 14, "min_keep_days": 3, "free_floor_gb": 60},
    "db_dumps": {"retention_days": 14, "versioned": True},
    "trigger": {"min_interval_seconds": 28800},
    "mirror_guard": {"max_propagated_deletes": 200},
}


def test_derive_p95_from_measured_values():
    out = derive_retention_p95(SAMPLE_CONFIG)
    assert out["working_vault_retention_p95_days"] == 14
    assert out["working_vault_retention_floor_days"] == 3
    assert out["db_dumps_retention_p95_days"] == 14
    assert out["trigger_interval_p95_hours"] == 8.0
    assert out["mirror_delete_cap"] == 200
    assert out["mirror_cap_trusted"] is True


def test_derive_handles_missing_keys_without_raising():
    out = derive_retention_p95({})
    assert out["working_vault_retention_p95_days"] is None
    assert out["trigger_interval_p95_hours"] is None
    assert out["mirror_cap_trusted"] is False


def test_validate_flags_floor_ge_retention():
    bad = {"working_vault": {"retention_days": 3, "min_keep_days": 3}, "trigger": {"min_interval_seconds": 0}}
    v = validate_config(bad)
    assert any("min_keep_days" in x for x in v)
    assert any("min_interval_seconds" in x for x in v)
    assert validate_config(SAMPLE_CONFIG) == []


def test_parse_keep_text_separates_comments():
    parsed = parse_keep_text("# 注释\n\npython\n-c .runtime/tmp/x\n# 另一条\n")
    assert parsed["entry_count"] == 2
    assert parsed["comment_lines"] == 2
    assert parsed["entries"] == ["python", "-c .runtime/tmp/x"]


def test_build_shadow_doc_readonly_copy(tmp_path: Path):
    keep = tmp_path / "process_reaper_keep.txt"
    keep.write_text("# head\nZEPHYR-RESTORE-DRILL\n", encoding="utf-8")
    now = datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc)
    doc, raw = build_shadow_doc(keep, now)
    assert doc["entry_count"] == 1
    assert doc["entries"] == ["ZEPHYR-RESTORE-DRILL"]
    assert doc["ttl_days"] == 3
    assert len(doc["source_sha256"]) == 64
    assert raw == "# head\nZEPHYR-RESTORE-DRILL\n"
    # 本体未被改动（只读契约）
    assert keep.read_text(encoding="utf-8") == "# head\nZEPHYR-RESTORE-DRILL\n"


@pytest.mark.parametrize("cap,trusted", [(200, True), (5000, True), (5001, False), (0, False), ("x", False)])
def test_mirror_cap_trust_bound(cap, trusted):
    out = derive_retention_p95({"mirror_guard": {"max_propagated_deletes": cap}})
    assert out["mirror_cap_trusted"] is trusted
