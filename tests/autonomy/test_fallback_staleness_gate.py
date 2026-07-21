# [A_test] module_id: MOD-GOV_fallback_staleness_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_fallback_staleness_gate
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_fallback_staleness_gate.py -q
# [TTL] task_bound
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from zephyr.autonomy_core.context.fallback_staleness_gate import FallbackStalenessGate, StalenessReport


class TestStalenessReport:
    def test_instantiation_with_all_fields(self):
        sr = StalenessReport(
            file_path="/tmp/test.md",
            sha256="abc123",
            age_days=10.0,
            is_stale=False,
            alert_message="OK",
        )
        assert sr.file_path == "/tmp/test.md"
        assert sr.sha256 == "abc123"
        assert sr.age_days == 10.0
        assert sr.is_stale is False
        assert sr.alert_message == "OK"

    def test_instantiation_stale_true(self):
        sr = StalenessReport(file_path="x", sha256="", age_days=100.0, is_stale=True, alert_message="old")
        assert sr.is_stale is True

    def test_equality(self):
        a = StalenessReport(file_path="f", sha256="s", age_days=1.0, is_stale=False, alert_message="OK")
        b = StalenessReport(file_path="f", sha256="s", age_days=1.0, is_stale=False, alert_message="OK")
        assert a == b


class TestFallbackStalenessGate:
    def test_instantiation_default(self):
        gate = FallbackStalenessGate()
        assert gate is not None
        assert gate._file == Path("AGENTS.md")

    def test_instantiation_custom_path(self):
        gate = FallbackStalenessGate(defaults_file="/custom/path.md")
        assert gate._file == Path("/custom/path.md")

    def test_instantiation_path_object(self):
        gate = FallbackStalenessGate(defaults_file=Path("/obj/path.md"))
        assert gate._file == Path("/obj/path.md")

    def test_check_returns_staleness_report(self):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8") as f:
            f.write("test content")
            tmp_path = f.name
        try:
            gate = FallbackStalenessGate(defaults_file=tmp_path)
            result = gate.check()
            assert isinstance(result, StalenessReport)
        finally:
            os.remove(tmp_path)

    def test_check_file_path_in_report(self):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8") as f:
            f.write("content")
            tmp_path = f.name
        try:
            gate = FallbackStalenessGate(defaults_file=tmp_path)
            result = gate.check()
            assert result.file_path == tmp_path
        finally:
            os.remove(tmp_path)

    def test_check_sha256_is_hex_string_for_existing_file(self):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8") as f:
            f.write("deterministic content")
            tmp_path = f.name
        try:
            gate = FallbackStalenessGate(defaults_file=tmp_path)
            result = gate.check()
            assert len(result.sha256) == 16
            int(result.sha256, 16)
        finally:
            os.remove(tmp_path)

    def test_check_fresh_file_is_not_stale(self):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8") as f:
            f.write("fresh")
            tmp_path = f.name
        try:
            gate = FallbackStalenessGate(defaults_file=tmp_path)
            result = gate.check()
            assert result.is_stale is False
            assert result.alert_message == "OK"
        finally:
            os.remove(tmp_path)

    def test_check_fresh_file_age_near_zero(self):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8") as f:
            f.write("just created")
            tmp_path = f.name
        try:
            gate = FallbackStalenessGate(defaults_file=tmp_path)
            result = gate.check()
            assert result.age_days < 1.0
        finally:
            os.remove(tmp_path)

    def test_check_nonexistent_file_empty_sha(self):
        gate = FallbackStalenessGate(defaults_file="/nonexistent/path/ghost.md")
        result = gate.check()
        assert result.sha256 == ""

    def test_check_nonexistent_file_zero_age(self):
        gate = FallbackStalenessGate(defaults_file="/nonexistent/path/ghost.md")
        result = gate.check()
        assert result.age_days == 0.0

    def test_check_nonexistent_file_not_stale(self):
        gate = FallbackStalenessGate(defaults_file="/nonexistent/path/ghost.md")
        result = gate.check()
        assert result.is_stale is False

    def test_check_sha256_truncated_to_16_chars(self):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8") as f:
            f.write("content for hash check")
            tmp_path = f.name
        try:
            gate = FallbackStalenessGate(defaults_file=tmp_path)
            result = gate.check()
            assert len(result.sha256) == 16
        finally:
            os.remove(tmp_path)

    def test_check_age_days_rounded_to_one_decimal(self):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8") as f:
            f.write("rounding test")
            tmp_path = f.name
        try:
            gate = FallbackStalenessGate(defaults_file=tmp_path)
            result = gate.check()
            str_repr = str(result.age_days)
            if "." in str_repr:
                decimals = str_repr.split(".")[1]
                assert len(decimals) <= 1
        finally:
            os.remove(tmp_path)

    def test_check_consistent_hash_for_same_content(self):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8") as f:
            f.write("same content both times")
            tmp_path = f.name
        try:
            gate = FallbackStalenessGate(defaults_file=tmp_path)
            r1 = gate.check()
            r2 = gate.check()
            assert r1.sha256 == r2.sha256
        finally:
            os.remove(tmp_path)
