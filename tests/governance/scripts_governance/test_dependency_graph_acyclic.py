# [A_test] module_id: MOD-GOV_dependency_graph_acyclic | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-280 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_dependency_graph_acyclic
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""依赖无环测试 — 验证 governance/ 下有向图无循环."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_dependency_graph_acyclic():
    from scripts.governance.d5_architecture.dependency_graph import build_dependency_graph, has_cycle

    graph = build_dependency_graph()
    cyclic, path = has_cycle(graph)
    assert not cyclic, f"循环依赖检测到: {path}"
