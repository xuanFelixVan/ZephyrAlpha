# [A_test] module_id: SRC-TST-0755 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.dispatch_table
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.orchestrator.execution.dispatch_table import (
        SystemDispatch,
        cold_start_reading,
        get_ct_contracts,
        get_dispatch,
        get_reading_depth,
        get_schemas,
        get_token_budget,
        list_all_systems,
        lookup_ct,
    )
except Exception as exc:
    pytest.skip(f"无法导入 dispatch_table: {exc}", allow_module_level=True)


class TestDispatchTable:
    def test_list_all_systems_returns_keys(self):
        systems = list_all_systems()
        assert isinstance(systems, list)
        assert len(systems) == 13
        assert "orchestrator" in systems
        assert "context-engine" in systems

    def test_get_dispatch_known_system(self):
        dispatch = get_dispatch("orchestrator")
        assert dispatch is not None
        assert isinstance(dispatch, SystemDispatch)
        assert "CT-ORC-SCRIPT" in dispatch.ct_contracts

    def test_get_dispatch_unknown_system(self):
        result = get_dispatch("nonexistent")
        assert result is None

    def test_lookup_ct_finds_systems(self):
        systems = lookup_ct("CT-ORC-SCRIPT")
        assert "orchestrator" in systems
        assert "script-system" in systems

    def test_lookup_ct_unknown_returns_empty(self):
        result = lookup_ct("CT-FAKE-999")
        assert result == []

    def test_get_ct_contracts_known(self):
        contracts = get_ct_contracts("pipeline")
        assert "CT-PIPE-ORC" in contracts

    def test_get_ct_contracts_unknown(self):
        contracts = get_ct_contracts("nonexistent")
        assert contracts == ()

    def test_get_schemas_known(self):
        schemas = get_schemas("orchestrator")
        assert "TaskCard" in schemas

    def test_get_schemas_unknown(self):
        schemas = get_schemas("nonexistent")
        assert schemas == ()

    def test_get_token_budget_known(self):
        budget = get_token_budget("orchestrator")
        assert budget == 1800

    def test_get_token_budget_unknown(self):
        budget = get_token_budget("nonexistent")
        assert budget == 0

    def test_cold_start_reading_known(self):
        result = cold_start_reading("context-engine")
        assert "system" in result
        assert "ct_contracts" in result
        assert "schemas" in result
        assert "estimated_tokens" in result
        assert result["estimated_tokens"] == 1400

    def test_cold_start_reading_unknown(self):
        result = cold_start_reading("nonexistent")
        assert "error" in result
        assert "available" in result

    def test_get_reading_depth_emergency(self):
        assert get_reading_depth(400) == "紧急 — 冷启动"

    def test_get_reading_depth_standard(self):
        assert get_reading_depth(1000) == "标准 — 功能开发"

    def test_get_reading_depth_full(self):
        assert get_reading_depth(1800) == "完整 — 架构审查"

    def test_system_dispatch_frozen(self):
        dispatch = get_dispatch("orchestrator")
        with pytest.raises(Exception):
            dispatch.system_name = "modified"
