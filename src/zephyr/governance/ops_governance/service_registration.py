# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.governance.ops_governance.service_registration
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.shared.__init__; zephyr.shared.contracts.task_repository_protocol; zephyr.governance.persistence.task_repo; zephyr.governance.persistence.sqlite_schema; zephyr.governance.__init__
# [CONSUMERS] zephyr.trading.boot_hooks (startup); zephyr.__init__ (eager registration)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] register_services() MUST be called before any D-INFRA code uses ServiceRegistry.get(); idempotent
# [MODIFY-GUARD] Adding registrations requires updating shared_core.registry._VALID_KEYS
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if D-DATA modules unavailable; KeyError if registry key invalid
# [TESTS] tests/test_shared_core.py
# [A_module] module_id=MOD-GOV-service_registration | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
D-DATA -> ServiceRegistry 注册模块
==================================
将 D-DATA 的实现注册到 shared_core.ServiceRegistry，
使 D-INFRA 能通过 ServiceRegistry.get() 获取实现，
消除 D-INFRA->D-DATA 的直接 import 依赖。
"""

from __future__ import annotations

import logging
from zephyr.shared.io.paths import DB_PATH

logger = logging.getLogger(__name__)

_registered = False


def register_services() -> None:
    """将 D-DATA 实现注册到 ServiceRegistry。幂等，可重复调用。"""
    global _registered
    if _registered:
        return

    from zephyr.shared.protocols.registry import ServiceRegistry

    # task_repo — TaskRepository 实例
    def _make_task_repo() -> object:
        from zephyr.governance.persistence.task_repo import TaskRepository

        return TaskRepository()

    ServiceRegistry.register("task_repo", _make_task_repo)

    # db_connection — sqlite3.Connection
    def _make_db_connection() -> object:
        from zephyr.governance.persistence.sqlite_schema import get_db_connection

        return get_db_connection()

    ServiceRegistry.register("db_connection", _make_db_connection)

    # db_path — Path
    def _make_db_path() -> object:
        from zephyr.governance.persistence.sqlite_schema import DB_PATH

        return DB_PATH

    ServiceRegistry.register("db_path", _make_db_path)

    # vector-memory — InProcessVectorMemory
    def _make_vector_memory() -> object:
        from zephyr.integration.vector_memory.in_process_vector_memory import InProcessVectorMemory

        return InProcessVectorMemory()

    ServiceRegistry.register("vector-memory", _make_vector_memory)

    # reranker — Reranker instance
    def _make_reranker() -> object:
        from zephyr.gov_kb.reranker import Reranker

        return Reranker()

    ServiceRegistry.register("reranker", _make_reranker)

    # collection_schemas — COLLECTION_SCHEMAS dict
    def _make_collection_schemas() -> object:
        from zephyr.integration.vector_memory.collection_manager import COLLECTION_SCHEMAS

        return COLLECTION_SCHEMAS

    ServiceRegistry.register("collection_schemas", _make_collection_schemas)

    _registered = True
    logger.debug("D-DATA services registered with ServiceRegistry")
