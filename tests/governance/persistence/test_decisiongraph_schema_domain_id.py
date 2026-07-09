# [A_test] module_id: SRC-TST-2210 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SH-DB-002 | docs/03_modules/_cross_layer/database/blueprint.md | §decisiongraph
# [MODULE] tests.governance.persistence.test_decisiongraph_schema_domain_id
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/governance/persistence/test_decisiongraph_schema_domain_id.py
# [TTL] task_bound
"""test_decisiongraph_schema_domain_id.py — decision_layers/decision_nodes domain_id 字段测试（ARCH-056 Phase 1）

验证 DDL 常量中包含 domain_id 字段，用于四图模块同步引擎的核心字段对齐。
"""
from __future__ import annotations

from zephyr.governance.persistence.decisiongraph_schema import (
    _DDL_DECISION_LAYERS,
    _DDL_DECISION_NODES,
)


class TestDecisionLayersHasDomainId:
    """decision_layers 表 DDL 必须包含 domain_id 字段（ARCH-056 裁定 (d)）。"""

    def test_ddl_contains_domain_id(self):
        assert "domain_id" in _DDL_DECISION_LAYERS


class TestDecisionNodesHasDomainId:
    """decision_nodes 表 DDL 必须包含 domain_id 字段（ARCH-056 裁定 (d)）。"""

    def test_ddl_contains_domain_id(self):
        assert "domain_id" in _DDL_DECISION_NODES
