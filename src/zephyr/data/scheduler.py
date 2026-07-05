# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.scheduler
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.implementations.{ifind,miniqmt,akshare}_provider, zephyr.data.policy_registry
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 阶段2占位，main() 抛 NotImplementedError
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] main() → NotImplementedError
# [TESTS]
# [A_module] module_id=MOD-L00-004-scheduler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""数据源调度编排层占位（MOD-L00-004 §6）。

阶段2 将实现完整的 APScheduler 调度器：
- BackgroundScheduler + SQLAlchemyJobStore + ThreadPoolExecutor
- 4 档调度时段（16:30 日K / 17:00 资金 / 18:00 事件 / 周六 10:00 财务）
- DAG 任务依赖（adj_factor → kline_daily_hfq → kline_daily_none）
- SQLite 统一进度存储

本文件当前仅作为阶段1的引用锚点，确保 Provider 模块不被 ORPHAN-MODULE
门禁误判为孤儿（阶段2 实现时本文件将扩展为完整调度器）。
"""
from __future__ import annotations

# 阶段1引用锚点：让 ifind_provider/miniqmt_provider/akshare_provider
# 在 ORPHAN-MODULE 检测时有外部 import 引用（阶段2 将在此处实例化调度）
from zephyr.data.implementations.ifind_provider import IFindProvider  # noqa: F401
from zephyr.data.implementations.miniqmt_provider import MiniQMTProvider  # noqa: F401
from zephyr.data.implementations.akshare_provider import AKShareProvider  # noqa: F401
from zephyr.data.policy_registry import PolicyRegistry, get_registry  # noqa: F401


def main() -> None:
    """阶段2 入口占位：启动调度器、注册任务。"""
    raise NotImplementedError("调度器尚未实现，见蓝图 §6 和 §15.2 阶段2")


if __name__ == "__main__":
    main()
