# [A_test] module_id: SRC-TST-2076 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-693 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_task_manager_mcp
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""TaskManagerMCP（FastMCP）协议与 BlueprintDecomposer 绑定单测。"""


import json

import pytest

from zephyr.governance.persistence.task_repo import TaskRepository
from zephyr.integration.mcp.task_manager_server import TaskManagerMCP
from zephyr.shared.blueprint_tools.blueprint_decomposer import BlueprintDecomposer
from zephyr.shared.foundation.models import DecompositionResult


@pytest.fixture()
def task_repo(tmp_path) -> TaskRepository:
    return TaskRepository(db_path=tmp_path / "mcp_task.db", auto_init=True, enable_gate=False)


@pytest.fixture()
def tm(task_repo: TaskRepository) -> TaskManagerMCP:
    return TaskManagerMCP(task_repo=task_repo)


@pytest.mark.asyncio
async def test_list_tools_has_six_tools(tm: TaskManagerMCP) -> None:
    tools = await tm.mcp.list_tools()
    names = {t.name for t in tools}
    assert names >= {
        "task_manager.create_task",
        "task_manager.get_task",
        "task_manager.list_tasks",
        "task_manager.update_task_status",
        "task_manager.decompose_blueprint",
        "task_manager.register_from_triage",
    }


@pytest.mark.asyncio
async def test_create_and_get_task_roundtrip(tm: TaskManagerMCP) -> None:
    raw = await tm.mcp.call_tool(
        "task_manager.create_task",
        {
            "task_id": "CP-1",
            "title": "unit title",
            "source_blueprint": "MOD-T",
            "source_section": "1",
            "description": "long enough description for pydantic min length ten",
        },
    )
    data = json.loads(raw[0].text)
    tid = data["task_id"]
    got = await tm.mcp.call_tool("task_manager.get_task", {"task_id": tid})
    body = json.loads(got[0].text)
    assert body["task_id"] == tid
    assert body["status"] == "PENDING"


@pytest.mark.asyncio
async def test_update_status_pending_to_in_progress(tm: TaskManagerMCP) -> None:
    raw = await tm.mcp.call_tool(
        "task_manager.create_task",
        {
            "task_id": "CP-1",
            "title": "state",
            "source_blueprint": "MOD-T",
            "source_section": "1",
            "description": "long enough description for pydantic min length ten",
        },
    )
    tid = json.loads(raw[0].text)["task_id"]
    upd = await tm.mcp.call_tool(
        "task_manager.update_task_status",
        {"task_id": tid, "new_status": "IN_PROGRESS"},
    )
    body = json.loads(upd[0].text)
    assert body["status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_list_tasks_returns_created(tm: TaskManagerMCP) -> None:
    await tm.mcp.call_tool(
        "task_manager.create_task",
        {
            "title": "listed",
            "source_blueprint": "MOD-X",
            "source_section": "§1",
            "description": "long enough description for pydantic min length ten",
        },
    )
    raw = await tm.mcp.call_tool("task_manager.list_tasks", {"limit": 10})
    out = json.loads(raw[0].text)
    assert out["total"] >= 1
    assert isinstance(out["items"], list)


@pytest.mark.asyncio
async def test_decompose_blueprint_invokes_decomposer(
    tmp_path, task_repo: TaskRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    sample = tmp_path / "bp.md"
    sample.write_text(
        "- [ADR-001-1] **Sample** — line for decompose\n",
        encoding="utf-8",
    )
    calls: list[dict] = []

    def fake_decompose(self, **kwargs: object) -> DecompositionResult:
        calls.append(dict(kwargs))
        return DecompositionResult(
            total_tasks=0,
            tasks=[],
            dependency_graph={},
            unassigned_items=[],
            warnings=[],
        )

    monkeypatch.setattr(BlueprintDecomposer, "decompose_blueprint", fake_decompose)
    tm = TaskManagerMCP(task_repo=task_repo)
    await tm.mcp.call_tool(
        "task_manager.decompose_blueprint",
        {"blueprint_path": str(sample), "namespace": "CP", "phase": 2},
    )
    assert len(calls) == 1
    assert calls[0]["blueprint_path"] == str(sample)
    assert calls[0]["namespace"] == "CP"
    assert calls[0]["phase"] == 2


@pytest.mark.asyncio
async def test_server_property_exposes_lowlevel_name(tm: TaskManagerMCP) -> None:
    assert tm.server.name == "task-manager"
