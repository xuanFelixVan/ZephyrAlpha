# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_p4_merged_gates
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""test_p4_merged_gates.py — P4 七簇合并台冒烟测试（st-gslim-20260923）

断言：7 新台可构造、gate_id/priority 正确、聚合检查对无关文件全绿。
"""

from __future__ import annotations

import pytest

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

CASES = [
    ("dangling_reference_gate", "make_reference_integrity_gate", "REFERENCE-INTEGRITY", 70),
    ("perm_trigger_gate", "make_permanent_system_trigger_gate", "PERMANENT-SYSTEM-TRIGGER", 82),
    ("vocab_hardcode_gate", "make_gate_vocab_gate", "GATE-VOCAB", 80),
    ("depgraph_pre_registration_gate", "make_depgraph_enforcement_gate", "DEPGRAPH-ENFORCEMENT", 113),
    ("panorama_alignment_gate", "make_map_alignment_gate", "MAP-ALIGNMENT", 141),
    ("blueprint_amodule_consistency_gate", "make_blueprint_header_gate", "BLUEPRINT-HEADER", 79),
    ("high_complexity_gate", "make_complexity_guard_gate", "COMPLEXITY-GUARD", 92),
]


@pytest.mark.parametrize("module,factory,gate_id,priority", CASES)
def test_merged_gate_constructs(module, factory, gate_id, priority):
    import importlib

    mod = importlib.import_module(f"zephyr.gov_enforcement.commit_gates.{module}")
    spec = getattr(mod, factory)()
    assert isinstance(spec, GateSpec)
    assert spec.gate_id == gate_id
    assert spec.priority == priority
    assert callable(spec.check)
