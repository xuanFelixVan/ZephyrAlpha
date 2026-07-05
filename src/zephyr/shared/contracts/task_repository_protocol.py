# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §4
# [MODULE] zephyr.shared.contracts.task_repository_protocol
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.trading; zephyr.governance; zephyr.resilience
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Protocol MUST NOT import from zephyr.data; only structural subtyping
# [MODIFY-GUARD] shared/contracts/__init__.py; infrastructure/shared_core/ports.py; all 19 consumers
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TypeError if runtime implementation does not satisfy Protocol
# [TESTS] tests/utils/test_shared_core.py
# [A_module] module_id=MOD-SHR_task_repository_protocol | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
TaskRepositoryProtocol — TaskRepository 的 Protocol 接口
=========================================================
D-ORCH / D-GOV / D-RESILIENCE 通过此 Protocol 访问任务持久化，
消除对 D-DATA / D-INFRA 的直接 import 依赖。
运行时通过 ServiceRegistry 获取具体实现。

类型策略：Protocol 内部使用 Any 代替 Task / TaskCard / TaskStatus 等域类型，
避免 Protocol 反向依赖 D-DATA 层。消费者按需在调用侧做类型窄化。
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class TaskRepositoryProtocol(Protocol):
    """TaskRepository 的 Protocol — D-ORCH / D-GOV / D-RESILIENCE 通过此接口访问任务持久化。"""

    # ------------------------------------------------------------------
    # 连接管理
    # ------------------------------------------------------------------

    def close(self) -> None: ...

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    def create(
        self,
        task: Any,
        *,
        files: list[dict[str, str]] | None = None,
        allow_direct_create: bool = False,
    ) -> Any: ...

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------

    def get(self, task_id: str) -> Any | None: ...

    def get_or_raise(self, task_id: str) -> Any: ...

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update(
        self,
        task_id: str,
        *,
        title: str | None = None,
        session_id: str | None = None,
        waiting_for: str | None = None,
        estimate_hours: float | None = None,
        actual_hours: float | None = None,
        deliverables: list[str] | None = None,
        acceptance: list[str] | None = None,
        files_in_scope: list[str] | None = None,
        tags: list[str] | None = None,
        model_rationale: str | None = None,
    ) -> Any: ...

    # ------------------------------------------------------------------
    # TRANSITION（状态机）
    # ------------------------------------------------------------------

    def transition(
        self,
        task_id: str,
        to_status: Any,
        *,
        session_id: str | None = None,
        waiting_for: str | None = None,
        note: str | None = None,
    ) -> Any: ...

    # ------------------------------------------------------------------
    # PRIORITY GOVERNANCE
    # ------------------------------------------------------------------

    def propose_priority_upgrade(self, task_id: str, proposed_priority: str) -> Any: ...

    def approve_priority_upgrade(self, task_id: str) -> Any: ...

    def reject_priority_upgrade(self, task_id: str) -> Any: ...

    # ------------------------------------------------------------------
    # ESCALATION / TIMEOUT GOVERNANCE
    # ------------------------------------------------------------------

    def check_escalation(self, task_id: str) -> dict | None: ...

    def check_all_escalations(self) -> list[dict]: ...

    def check_task_timeout(self, task_id: str) -> dict | None: ...

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    def delete(self, task_id: str) -> bool: ...

    def hard_delete(self, task_id: str) -> bool: ...

    # ------------------------------------------------------------------
    # LIST 查询
    # ------------------------------------------------------------------

    def list_by_status(self, status: Any) -> list[Any]: ...

    def list_by_phase(self, phase: int) -> list[Any]: ...

    def list_by_session(self, session_id: str) -> list[Any]: ...

    def query_tasks(
        self,
        *,
        phase: int | None = None,
        status: Any | None = None,
        session_id: str | None = None,
        file_path_glob: str | None = None,
        limit: int = 50,
    ) -> list[Any]: ...

    def list_by_namespace(self, namespace: Any) -> list[Any]: ...

    def list_active(self) -> list[Any]: ...

    def count_by_status(self) -> dict[str, int]: ...

    def list_by_dependency(self, dependency_task_id: str) -> list[Any]: ...

    def list_by_tag(self, tag: str) -> list[Any]: ...

    def list_by_blocked_by(self, blocker_task_id: str) -> list[Any]: ...

    # ------------------------------------------------------------------
    # task_files 读写
    # ------------------------------------------------------------------

    def add_file(self, task_id: str, file_path: str, role: str = "in_scope") -> None: ...

    def remove_file(self, task_id: str, file_path: str) -> None: ...

    def get_files(self, task_id: str) -> list[dict[str, str]]: ...

    def get_tasks_for_file(self, file_path: str) -> list[str]: ...

    # ------------------------------------------------------------------
    # SEQUENCE
    # ------------------------------------------------------------------

    def next_seq(self, namespace: Any = None) -> int: ...

    # ------------------------------------------------------------------
    # UPSERT
    # ------------------------------------------------------------------

    def upsert(self, task: Any, *, files: list[dict[str, str]] | None = None) -> Any: ...

    # ------------------------------------------------------------------
    # Multi-Worker Batch Coordination
    # ------------------------------------------------------------------

    def claim_next(self, batch_id: str, worker_id: str) -> Any | None: ...

    def recover_stale_claims(self, batch_id: str, timeout_minutes: int = 30) -> int: ...

    def batch_progress(self, batch_id: str) -> dict[str, int]: ...

    # ------------------------------------------------------------------
    # Auto-split
    # ------------------------------------------------------------------

    def auto_split_task(self, task_id_or_task: Any, *, session_id: str | None = None) -> list[Any]: ...

    # ------------------------------------------------------------------
    # Drift / Hallucination
    # ------------------------------------------------------------------

    def detect_completed_candidates(self) -> list[Any]: ...

    def drift_check(self, task_id: str) -> dict | None: ...

    def delete_completed_tasks_in_phase(self, phase: int) -> int: ...

    def cleanup_terminal_tasks(self) -> int: ...
