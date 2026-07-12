# [A_test] module_id: SRC-TST-0744 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_detector_dispatcher
# [INVARIANTS] 检测器调度不可绕过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_detector_dispatcher.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_drift.detector_dispatcher import (
    DetectorDispatcher,
    DetectorResult,
    ResultCache,
    get_max_parallel_for_level,
)
from zephyr.gov_drift.drift_models import Detector, ScanLevel, Severity


class TestDetectorResult:
    def test_default_fields(self):
        dr = DetectorResult(detector_id="det-1", success=True)
        assert dr.detector_id == "det-1"
        assert dr.success is True
        assert dr.events == []
        assert dr.error == ""
        assert dr.cached is False
        assert dr.elapsed_ms == 0.0

    def test_custom_fields(self):
        dr = DetectorResult(
            detector_id="det-2",
            success=False,
            events=[{"a": 1}],
            error="FAIL",
            cached=True,
            elapsed_ms=100.5,
        )
        assert dr.success is False
        assert dr.error == "FAIL"
        assert dr.cached is True
        assert dr.elapsed_ms == 100.5


class TestResultCache:
    def test_get_empty(self):
        cache = ResultCache()
        assert cache.get("nonexistent") is None

    def test_put_and_get(self):
        cache = ResultCache()
        result = DetectorResult(detector_id="det-1", success=True)
        cache.put("key1", result)
        retrieved = cache.get("key1")
        assert retrieved is not None
        assert retrieved.detector_id == "det-1"

    def test_put_overwrites(self):
        cache = ResultCache()
        r1 = DetectorResult(detector_id="det-1", success=True)
        r2 = DetectorResult(detector_id="det-2", success=False)
        cache.put("key1", r1)
        cache.put("key1", r2)
        assert cache.get("key1").detector_id == "det-2"

    def test_clear(self):
        cache = ResultCache()
        cache.put("key1", DetectorResult(detector_id="det-1", success=True))
        cache.clear()
        assert cache.get("key1") is None


class TestDetectorDispatcher:
    def test_instantiation(self, tmp_path):
        dd = DetectorDispatcher(registry_path=str(tmp_path))
        assert dd._registry_path == str(tmp_path)
        assert dd._max_parallel == 8

    def test_instantiation_custom_parallel(self, tmp_path):
        dd = DetectorDispatcher(registry_path=str(tmp_path), max_parallel=4)
        assert dd._max_parallel == 4

    def test_scripts_root_property(self, tmp_path):
        dd = DetectorDispatcher(registry_path=str(tmp_path))
        root = dd.scripts_root
        assert "scripts" in root
        assert "governance" in root

    def test_cache_key_deterministic(self, tmp_path):
        dd = DetectorDispatcher(registry_path=str(tmp_path))
        key1 = dd.cache_key("det-1", "file.py")
        key2 = dd.cache_key("det-1", "file.py")
        assert key1 == key2

    def test_cache_key_different_inputs(self, tmp_path):
        dd = DetectorDispatcher(registry_path=str(tmp_path))
        key1 = dd.cache_key("det-1", "file.py")
        key2 = dd.cache_key("det-2", "file.py")
        assert key1 != key2

    def test_cache_key_is_sha256(self, tmp_path):
        dd = DetectorDispatcher(registry_path=str(tmp_path))
        key = dd.cache_key("det-1", "file.py")
        assert len(key) == 64

    def test_build_cache_key_no_script(self, tmp_path):
        dd = DetectorDispatcher(registry_path=str(tmp_path))
        det = Detector(
            id="det-no-script",
            drift_dimension="test",
            severity=Severity.MEDIUM,
            category="test",
            script=None,
        )
        result = dd.build_cache_key(det, [])
        assert result is None

    def test_build_cache_key_missing_script(self, tmp_path):
        dd = DetectorDispatcher(registry_path=str(tmp_path))
        det = Detector(
            id="det-missing",
            drift_dimension="test",
            severity=Severity.MEDIUM,
            category="test",
            script="nonexistent_script.py",
        )
        result = dd.build_cache_key(det, [])
        assert result is None

    @pytest.mark.asyncio
    async def test_dispatch_empty_detectors(self, tmp_path):
        dd = DetectorDispatcher(registry_path=str(tmp_path))
        results = await dd.dispatch([])
        assert results == []

    @pytest.mark.asyncio
    async def test_dispatch_no_script_detector(self, tmp_path):
        dd = DetectorDispatcher(registry_path=str(tmp_path))
        det = Detector(
            id="det-no-script",
            drift_dimension="test",
            severity=Severity.MEDIUM,
            category="test",
            script=None,
        )
        results = await dd.dispatch([det])
        assert len(results) == 1
        assert results[0].success is True
        assert results[0].detector_id == "det-no-script"

    @pytest.mark.asyncio
    async def test_dispatch_missing_script_detector(self, tmp_path):
        dd = DetectorDispatcher(registry_path=str(tmp_path))
        det = Detector(
            id="det-missing",
            drift_dimension="test",
            severity=Severity.MEDIUM,
            category="test",
            script="nonexistent.py",
        )
        results = await dd.dispatch([det])
        assert len(results) == 1
        assert results[0].success is False
        assert "MISSING_SCRIPT" in results[0].error


class TestGetMaxParallelForLevel:
    def test_light_level(self):
        assert get_max_parallel_for_level(ScanLevel.LIGHT) == 4

    def test_standard_level(self):
        assert get_max_parallel_for_level(ScanLevel.STANDARD) == 4

    def test_deep_level(self):
        assert get_max_parallel_for_level(ScanLevel.DEEP) == 8
