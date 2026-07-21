# [A_test] module_id: MOD-GOV_cross_env_consistency | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md
# [MODULE] tests.test_cross_env_consistency
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] src/zephyr/behavioral-auditor/cross_env_consistency.py
# [CONSUMERS] CI pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip
# [TESTS] python -m pytest tests/test_cross_env_consistency.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.architecture_governance.cross_env_consistency import (
    MODEL_FLOAT_TOLERANCE,
    PYTHON_VERSION,
    WIN11_RISKS,
    WIN_MAX_CPU_LOAD,
    WIN_MIN_RAM_GB,
    ConsistencyDim,
)


class TestConsistencyDim:
    def test_enum_values_exist(self):
        assert ConsistencyDim.PYTHON.value == "Python3.11.9"
        assert ConsistencyDim.DEPENDENCIES.value == "freeze.md5 hash"
        assert ConsistencyDim.DATA_STRUCTURE.value == "parquet/pickle schema"
        assert ConsistencyDim.MODEL_OUTPUT.value == "float ε<1e-9"

    def test_enum_is_str(self):
        for dim in ConsistencyDim:
            assert isinstance(dim.value, str)

    def test_enum_members_count(self):
        assert len(ConsistencyDim) == 4

    def test_enum_access_by_name(self):
        assert ConsistencyDim["PYTHON"] is ConsistencyDim.PYTHON
        assert ConsistencyDim["DEPENDENCIES"] is ConsistencyDim.DEPENDENCIES

    def test_enum_iteration(self):
        members = list(ConsistencyDim)
        assert len(members) == 4
        assert ConsistencyDim.PYTHON in members


class TestConstants:
    def test_python_version(self):
        assert isinstance(PYTHON_VERSION, str)
        assert "." in PYTHON_VERSION

    def test_model_float_tolerance(self):
        assert isinstance(MODEL_FLOAT_TOLERANCE, float)
        assert MODEL_FLOAT_TOLERANCE > 0
        assert MODEL_FLOAT_TOLERANCE < 1.0

    def test_win_min_ram_gb(self):
        assert isinstance(WIN_MIN_RAM_GB, int)
        assert WIN_MIN_RAM_GB > 0

    def test_win_max_cpu_load(self):
        assert isinstance(WIN_MAX_CPU_LOAD, float)
        assert 0.0 < WIN_MAX_CPU_LOAD <= 1.0

    def test_win11_risks_keys(self):
        expected_keys = {"permissions", "paths", "crlf", "memory", "process"}
        assert set(WIN11_RISKS.keys()) == expected_keys

    def test_win11_risks_values_are_strings(self):
        for key, value in WIN11_RISKS.items():
            assert isinstance(value, str), f"WIN11_RISKS[{key}] is not str"
            assert len(value) > 0, f"WIN11_RISKS[{key}] is empty"
