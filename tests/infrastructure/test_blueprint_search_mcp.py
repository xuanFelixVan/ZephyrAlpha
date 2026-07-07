# [A_test] module_id: SRC-TST-1981 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-598 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_blueprint_search_mcp
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""BlueprintSearchServer（BaseMCPServer）轻量单测。"""


import json

from zephyr.integration.mcp.blueprint_search_server import BlueprintSearchServer


def test_find_relevant_blueprint_returns_structure() -> None:
    srv = BlueprintSearchServer()
    resp = srv.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "blueprint_search.find_relevant_blueprint",
                "arguments": {
                    "task_description": "governance blueprint MOD-INF script system",
                    "num_results": 2,
                },
            },
        }
    )
    assert "result" in resp
    text = resp["result"]["content"][0]["text"]
    data = json.loads(text)
    assert "results" in data
    assert "count" in data
    assert data["source"] == "config/blueprint_routing.yaml"
