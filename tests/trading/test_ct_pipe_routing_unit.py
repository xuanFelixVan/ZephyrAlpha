# [A_test] module_id: SRC-TST-2004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-621 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_ct_pipe_routing
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""CT-PIPE-ORC-001 路由纯逻辑单测。"""


import pytest

from zephyr.infrastructure.pipeline.ct_pipe_routing import (
    CtPipeRoutingHints,
    PipelineRoutingInputsError,
    modules_slice_from_node,
    resolve_ct_pipe_orc001,
)


def test_modules_slice_m6_to_end() -> None:
    zone, mods = modules_slice_from_node("M6")
    assert zone == "B"
    assert mods[0] == "M6" and mods[-1] == "M11"


def test_resolve_audit_p0_vs_p1() -> None:
    r0 = resolve_ct_pipe_orc001(CtPipeRoutingHints(task_type="AUDIT", priority_value="P0", target_layer=None))
    r1 = resolve_ct_pipe_orc001(CtPipeRoutingHints(task_type="AUDIT", priority_value="P1", target_layer=None))
    assert r0.node_id == "M3"
    assert r1.node_id == "M4"


def test_resolve_doc_write_requires_layer() -> None:
    with pytest.raises(PipelineRoutingInputsError):
        resolve_ct_pipe_orc001(CtPipeRoutingHints(task_type="DOC_WRITE", priority_value="P2"))


def test_resolve_doc_write_foundation_vs_other() -> None:
    r_f = resolve_ct_pipe_orc001(CtPipeRoutingHints(task_type="DOC_WRITE", priority_value="P2", target_layer="D_INFRA_OPS"))
    r_o = resolve_ct_pipe_orc001(CtPipeRoutingHints(task_type="REFACTOR", priority_value="P2", target_layer="D_FACTOR"))
    assert r_f.node_id == "M5"
    assert r_o.node_id == "M6"
