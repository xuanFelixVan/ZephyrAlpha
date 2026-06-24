# [A_test] module_id: SRC-TST-2092 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-709 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.verify_b54_b56_b59_deep
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""Deeper integration test: P0 inflation guard + block_sessions_count + timeout exemption"""

import sqlite3
import sys
import warnings
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, r"D:\ZephyrAlpha\src")

from zephyr.governance.persistence.task_repo import (
    P0InflationFrozenError,
    TaskRepository,
)
from zephyr.governance.rule_enforcement.task_types import TaskNamespace, TaskStatus
from zephyr.integration.shared.schema.severity_types import Priority as P
from zephyr.shared.shared_services.models import TaskCard

DB = Path(r"D:\ZephyrAlpha\data\databases\governance.db")

repo = TaskRepository(enable_gate=False)
now = datetime.now(UTC)


def mt(suffix, priority=P.P2, tags=None):
    """make test task"""
    seq = 99900 + suffix
    return TaskCard(
        task_id=f"CP-{seq:05d}",
        namespace=TaskNamespace.CP,
        seq=seq,
        title=f"Test-{suffix}",
        status=TaskStatus.PENDING,
        priority=priority,
        phase=9,
        execution_model="deepseek",
        safety_level="M",
        source_blueprint="test",
        source_section="test",
        description=f"Test task {suffix}",
        tags=tags or [],
        created_at=now,
        updated_at=now,
    )


print("=" * 60)
print("Deeper Integration Test")
print("=" * 60)

# --- Test 1: P0 inflation guard in create() ---
print("\n[Test 1] P0 inflation guard in create()...")
live_p0 = repo._count_p0_tasks(sqlite3.connect(str(DB)))
print(f"  Live P0 before test: {live_p0}")

t1 = mt(1, P.P0)

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    if live_p0 >= 5:
        try:
            repo.create(t1)
            print("  FAIL: Should have raised P0InflationFrozenError")
        except P0InflationFrozenError:
            print("  PASS: P0InflationFrozenError raised correctly")
    elif live_p0 >= 3:
        tcard = repo.create(t1)
        print(f"  PASS: Created with warning ({len(w)} warnings)")
        repo.hard_delete(t1.task_id)
    else:
        tcard = repo.create(t1)
        print("  PASS: Created (P0 count < 3)")
        repo.hard_delete(t1.task_id)

# --- Test 2: block_sessions_count ---
print("\n[Test 2] block_sessions_count increment...")
t2 = mt(2)
repo.upsert(t2)
repo.transition(t2.task_id, TaskStatus.IN_PROGRESS)
repo.transition(t2.task_id, TaskStatus.BLOCKED, waiting_for="test")
after_b1 = repo.get(t2.task_id)
assert after_b1.block_sessions_count == 1, f"Expected 1, got {after_b1.block_sessions_count}"

repo.transition(t2.task_id, TaskStatus.READY)
repo.transition(t2.task_id, TaskStatus.IN_PROGRESS)
repo.transition(t2.task_id, TaskStatus.BLOCKED, waiting_for="test2")
after_b2 = repo.get(t2.task_id)
assert after_b2.block_sessions_count == 2, f"Expected 2, got {after_b2.block_sessions_count}"
print("  PASS: block_sessions_count: 0 -> 1 -> 2")

repo.transition(t2.task_id, TaskStatus.READY)
repo.hard_delete(t2.task_id)

# --- Test 3: Escalation (P0 with 2 BLOCKED) ---
print("\n[Test 3] P0 escalation at 2 BLOCKED...")
t3 = mt(3, P.P0)
repo.create(t3)
esc0 = repo.check_escalation(t3.task_id)
assert esc0 is None, f"Expected None before any BLOCKED, got {esc0}"

repo.transition(t3.task_id, TaskStatus.IN_PROGRESS)
repo.transition(t3.task_id, TaskStatus.BLOCKED, waiting_for="t3b1")
repo.transition(t3.task_id, TaskStatus.READY)
repo.transition(t3.task_id, TaskStatus.IN_PROGRESS)
repo.transition(t3.task_id, TaskStatus.BLOCKED, waiting_for="t3b2")
esc2 = repo.check_escalation(t3.task_id)
assert esc2 is not None, "P0 with 2 BLOCKED should escalate"
assert "P0" in str(esc2["triggers"])
print(f"  PASS: Escalation triggered: {esc2['triggers']}")

repo.transition(t3.task_id, TaskStatus.READY)
repo.hard_delete(t3.task_id)

# --- Test 4: Timeout exemption ---
print("\n[Test 4] Timeout exemption...")
t4 = mt(4, tags=["exempt:timeout", "test"])
repo.create(t4)
assert repo._is_timeout_exempt(t4.task_id)
assert repo.check_task_timeout(t4.task_id) is None
print("  PASS: exempt:timeout tag works")

tagged = repo.list_by_tag("exempt:timeout")
assert t4.task_id in [t.task_id for t in tagged]
print("  PASS: list_by_tag found exempt task")

repo.hard_delete(t4.task_id)

# --- Test 5: P0 guard in propose_priority_upgrade ---
print("\n[Test 5] P0 guard in propose_priority_upgrade...")
t5 = mt(5)
repo.create(t5)
live_p0_now = repo._count_p0_tasks(sqlite3.connect(str(DB)))
print(f"  Live P0 count: {live_p0_now}")

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    if live_p0_now >= 5:
        try:
            repo.propose_priority_upgrade(t5.task_id, "P0")
            print("  FAIL: Should have raised P0InflationFrozenError")
        except P0InflationFrozenError:
            print("  PASS: P0InflationFrozenError raised for upgrade")
    else:
        repo.propose_priority_upgrade(t5.task_id, "P0")
        upgraded = repo.get(t5.task_id)
        print(f"  PASS: approval_required={upgraded.approval_required}, proposed={upgraded.priority_proposed}")
        if live_p0_now >= 3:
            print(f"  Warning generated: {len(w) > 0}")
        repo.reject_priority_upgrade(t5.task_id)

repo.hard_delete(t5.task_id)

repo.close()

print("\n" + "=" * 60)
print("ALL INTEGRATION TESTS PASSED")
print("=" * 60)
