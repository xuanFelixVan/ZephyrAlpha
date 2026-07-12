# [A_test] module_id: SRC-TST-2009 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-626 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_dispatch_table
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""分派表单元测试——验证 13 系统分派映射的正确性。"""


from zephyr.orchestrator.execution.dispatch_table import (
    DISPATCH_TABLE,
    cold_start_reading,
    get_ct_contracts,
    get_dispatch,
    get_reading_depth,
    get_schemas,
    get_token_budget,
    list_all_systems,
    lookup_ct,
)


class TestDispatchTableStructure:
    def test_has_13_systems(self):
        assert len(DISPATCH_TABLE) == 13

    def test_all_keys_lowercase(self):
        for key in DISPATCH_TABLE:
            assert key == key.lower()


class TestLookupCT:
    def test_ct_orc_script_in_multiple_systems(self):
        systems = lookup_ct("CT-ORC-SCRIPT")
        assert "orchestrator" in systems
        assert "script-system" in systems

    def test_ct_pipe_orc_only_in_pipeline(self):
        systems = lookup_ct("CT-PIPE-ORC")
        assert systems == ["pipeline"]

    def test_unknown_ct_returns_empty(self):
        systems = lookup_ct("CT-NONEXISTENT")
        assert systems == []


class TestGetDispatch:
    def test_valid_system(self):
        dispatch = get_dispatch("orchestrator")
        assert dispatch is not None
        assert dispatch.system_name == "Orchestrator（任务系统）"

    def test_invalid_system(self):
        dispatch = get_dispatch("nonexistent")
        assert dispatch is None


class TestGetCTContracts:
    def test_orchestrator_ct_contracts(self):
        contracts = get_ct_contracts("orchestrator")
        assert "CT-ORC-SCRIPT" in contracts
        assert "CT-ORC-CE" in contracts
        assert len(contracts) == 5

    def test_invalid_system(self):
        contracts = get_ct_contracts("nonexistent")
        assert contracts == ()


class TestGetSchemas:
    def test_orchestrator_schemas(self):
        schemas = get_schemas("orchestrator")
        assert "TaskCard" in schemas
        assert "Finding" in schemas

    def test_vector_memory_no_schemas(self):
        schemas = get_schemas("vector-memory")
        assert schemas == ()


class TestGetTokenBudget:
    def test_pipeline_budget_is_400(self):
        assert get_token_budget("pipeline") == 400

    def test_cross_system_budget_is_1600(self):
        assert get_token_budget("cross-system-governance") == 1600

    def test_invalid_returns_zero(self):
        assert get_token_budget("nonexistent") == 0


class TestColdStartReading:
    def test_knowledge_base_cold_start(self):
        result = cold_start_reading("knowledge-base")
        assert result["estimated_tokens"] == 1000
        assert "CT-SCRIPT-KB" in result["ct_contracts"]
        assert "KE" in result["schemas"]

    def test_invalid_system(self):
        result = cold_start_reading("invalid")
        assert "error" in result
        assert "available" in result


class TestListAllSystems:
    def test_returns_13_systems(self):
        systems = list_all_systems()
        assert len(systems) == 13

    def test_contains_orchestrator(self):
        systems = list_all_systems()
        assert "orchestrator" in systems
        assert "pipeline" in systems
        assert "cross-system-governance" in systems


class TestReadingDepth:
    def test_500_is_emergency(self):
        assert get_reading_depth(500) == "紧急 — 冷启动"

    def test_800_is_standard(self):
        assert get_reading_depth(800) == "标准 — 功能开发"

    def test_1600_is_full(self):
        assert get_reading_depth(1600) == "完整 — 架构审查"

    def test_exact_boundary_500(self):
        assert get_reading_depth(500) == "紧急 — 冷启动"

    def test_exact_boundary_1500(self):
        assert get_reading_depth(1500) == "标准 — 功能开发"
