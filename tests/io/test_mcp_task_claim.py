# [BLUEPRINT] MOD-DATABASE | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-GOV_mcp_task_claim | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from zephyr.governance.persistence.task_repo import TaskRepository
from zephyr.integration.mcp.task_manager_server import TaskManagerMCP
from zephyr.shared.io.paths import DB_PATH, REPO_ROOT

DB_PATH = REPO_ROOT / "data" / "databases" / "governance.db"

# 契约真源：tool_contracts.yaml §task_manager（fc318f9631 复制簇#3 治理收敛为 6 工具，
# claim_task/mark_task_done/mark_task_failed/batch_progress/list_dependents 及
# staging 系列 write_draft/commit_draft/list_drafts/discard_draft 已移出契约）
_CONTRACT_TOOLS = {
    "task_manager.create_task",
    "task_manager.get_task",
    "task_manager.list_tasks",
    "task_manager.update_task_status",
    "task_manager.decompose_blueprint",
    "task_manager.register_from_triage",
}


def test_mcp_claim_task():
    repo = TaskRepository(str(DB_PATH))
    mcp = TaskManagerMCP(task_repo=repo)
    tool_names = mcp.tool_names
    for name in _CONTRACT_TOOLS:
        assert name in tool_names, f"{name} not in {tool_names}"
    print("test_mcp_claim_task PASSED")


def test_mcp_list_dependents():
    repo = TaskRepository(str(DB_PATH))
    # 真源演进：CP-1001/CP-1002 历史依赖关系已在 DB 中清空（depends_on=[]）；
    # 改为从真源动态取一条 depends_on 非空的任务，验证 list_by_dependency 反查。
    conn = sqlite3.connect(str(DB_PATH))
    row = conn.execute(
        "SELECT task_id, depends_on FROM tasks "
        "WHERE depends_on != '[]' AND depends_on IS NOT NULL AND is_deleted = 0 LIMIT 1"
    ).fetchone()
    conn.close()
    assert row is not None, "真源 DB 中无 depends_on 非空任务，无法验证 list_by_dependency"
    downstream_id, upstream_id = row[0], json.loads(row[1])[0]
    downstream = repo.list_by_dependency(upstream_id)
    ids = [d.task_id for d in downstream]
    assert downstream_id in ids, f"{downstream_id} should depend on {upstream_id}, got {ids}"
    print(f"  {upstream_id} downstream: {ids}")
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
    # staging 系列工具已随契约收敛移除；契约为准的 6 工具须全部注册
    for name in _CONTRACT_TOOLS:
        assert name in tool_names, f"{name} not in {tool_names}"
    print("test_mcp_staging_tools PASSED")


if __name__ == "__main__":
    test_mcp_claim_task()
    test_mcp_list_dependents()
    test_mcp_batch_progress()
    test_mcp_staging_tools()
    print("\nAll MCP task claim tests PASSED!")
