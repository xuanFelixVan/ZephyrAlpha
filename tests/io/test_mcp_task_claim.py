# [A_test] module_id: SRC-TST-1252 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from zephyr.shared.io.paths import REPO_ROOT, DB_PATH

from zephyr.governance.persistence.task_repo import TaskRepository
from zephyr.integration.mcp.task_manager_server import TaskManagerMCP

DB_PATH = REPO_ROOT / "data" / "databases" / "governance.db"


def test_mcp_claim_task():
    repo = TaskRepository(str(DB_PATH))
    mcp = TaskManagerMCP(task_repo=repo)
    tool_names = mcp.tool_names
    assert "task_manager.claim_task" in tool_names, f"claim_task not in {tool_names}"
    assert "task_manager.mark_task_done" in tool_names
    assert "task_manager.mark_task_failed" in tool_names
    assert "task_manager.batch_progress" in tool_names
    assert "task_manager.list_dependents" in tool_names
    print("test_mcp_claim_task PASSED")


def test_mcp_list_dependents():
    repo = TaskRepository(str(DB_PATH))
    downstream = repo.list_by_dependency("CP-1001")
    ids = [d.task_id for d in downstream]
    assert "CP-1002" in ids, f"CP-1002 should depend on CP-1001, got {ids}"
    print(f"  CP-1001 downstream: {ids}")
    print("test_mcp_list_dependents PASSED")


def test_mcp_batch_progress():
    repo = TaskRepository(str(DB_PATH))
    progress = repo.batch_progress("concurrency-staging-20260522")
    assert "READY" in progress
    assert "IN_PROGRESS" in progress
    assert "COMPLETED" in progress
    print(f"  Batch progress: {progress}")
    print("test_mcp_batch_progress PASSED")


def test_mcp_staging_tools():
    mcp = TaskManagerMCP()
    tool_names = mcp.tool_names
    assert "task_manager.write_draft" in tool_names, f"write_draft not in {tool_names}"
    assert "task_manager.commit_draft" in tool_names
    assert "task_manager.list_drafts" in tool_names
    assert "task_manager.discard_draft" in tool_names
    print("test_mcp_staging_tools PASSED")


if __name__ == "__main__":
    test_mcp_claim_task()
    test_mcp_list_dependents()
    test_mcp_batch_progress()
    test_mcp_staging_tools()
    print("\nAll MCP task claim tests PASSED!")
