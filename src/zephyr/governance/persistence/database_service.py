# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.governance.persistence.database_service
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.database_service
# [CONSUMERS] src/zephyr/governance/; scripts/database/; tests/db/test_db_auto_ops.py; tests/governance/data_layer/test_database_service.py
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] re-export canonical from infrastructure.database_service; 单真源派生层，禁止在此重复定义连接管理代码
# [MODIFY-GUARD] 禁止修改——本模块为派生 re-export，真源在 zephyr.infrastructure.database_service
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 透传 zephyr.infrastructure.database_service.DatabaseService 的错误契约
# [TESTS] tests/test_db_auto_ops.py::test_database_service_init
# [TTL] permanent
"""
DatabaseService 真源收敛（AI-14 审计 P1 修复）

治本修复(2026-07-17): 消除双真源同步违规。本模块原为独立 DatabaseService 定义，
与 infrastructure/database_service.py 重复（~100 行连接管理代码重复，capability
registry L3627 明确记载"被两个 DatabaseService 类继承"——属多真源同步硬违规）。

现已收敛为单真源 re-export：
    - 真源（canonical）: zephyr.infrastructure.database_service.DatabaseService
      （MOD-INF-002，含 governance + depgraph + ClickHouse + Redis 接口）
    - 派生（re-export）: 本模块，向后兼容现有 import 路径

现有 import 保持可用，无需改动调用方：
    from zephyr.governance.persistence.database_service import DatabaseService

infrastructure 版为超集（含 ClickHouse/Redis 接口），governance 消费者获得
完整能力。DatabaseCRUDMixin（SH-DB-001）的 [MODIFY-GUARD] 已同步更新为单真源。
"""
from zephyr.infrastructure.database_service import DatabaseService

__all__ = ["DatabaseService"]
