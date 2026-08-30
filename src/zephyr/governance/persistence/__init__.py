# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.persistence
# [TTL] permanent
# zephyr.governance.persistence 包
#
# ARCH-OLAP-RETIRE（2026-07-16）：olap_engine.py 已退役删除。
#   原因：DuckDB OLAP 层被 ClickHouse（Hyper-V VM）替代后，olap_engine.py
#   成孤儿模块（src/ 业务侧零调用，consumer count=0）。详见 architecture_issue_registry.yaml。
# 其他原代理模块已删除，真源统一在 zephyr.governance.* 或 zephyr.feedback_loop.* 下。
# 详见 commit 消息（代理层消除）。
#
# ARCH-051（2026-07-06）：新增 dataflowgraph_schema.py（数据流图 schema，同库不同表）

# 显式 import（声明依赖关系，满足 ORPHAN-MODULE 门禁的 src/**/*.py 检测范围）
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: _DATAFLOW_CORE_TABLES
#   code: __init__.py import L45
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 dataflowgraph_schema, base_repo, database_service, depgraph_reader, intent_…
#   desc: __init__ import L45；__all__ 10 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（10 符号）
#   name_en: __all__
#   intro: dataflowgraph_schema, base_repo, database_service, depgraph_reader, intent_keyw…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.governance.persistence.dataflowgraph_schema import _DATAFLOW_CORE_TABLES  # noqa: F401

# 显式 import 子模块（满足 TEST-SOURCE-CONSISTENCY 门禁的符号漂移检测）
from . import intent_keyword_mapper, intent_parser  # noqa: F401

__all__ = [
    "dataflowgraph_schema",
    "base_repo",
    "database_service",
    "depgraph_reader",
    "intent_keyword_mapper",
    "intent_parser",
    "pg_wrapper",
    "protocol_state_store",
    "sqlite_schema",
    "task_repo",
]
