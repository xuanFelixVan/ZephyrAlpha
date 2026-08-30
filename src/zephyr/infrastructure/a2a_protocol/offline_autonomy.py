# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.offline_autonomy
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.__init__
# [CONSUMERS] MOD-INF-027;MOD-INF-018;MOD-INF-022
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Agent间通信;冲突解决;四级委托约束
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md;src/zephyr/infrastructure/runtime_integration/a2a_protocol/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CommunicationError;ConflictError;DelegationError
# [TESTS] tests/test_a2a_protocol/
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: offline_autonomy.py
# 层: 算法
# - id: A1
#   name_zh: ① AutonomyState
#   name_en: AutonomyState
#   intro: class AutonomyState 源码 L61-L82
#   desc: 公共方法（定义序）: mode, transition, cache_command, has_cached_commands；源码 L61-L82
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: AutonomyState
#   downstream: MOD-INF-027;MOD-INF-018;MOD-INF-022
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum


class OfflineMode(str, Enum):
    AUTO = "AUTO"
    SEMIAUTO_MANUAL = "SEMIAUTO_MANUAL"
    ONLINE = "ONLINE"


class AutonomyState:
    def __init__(self) -> None:
        self._mode: OfflineMode = OfflineMode.ONLINE
        self._cache: list[str] = []

    @property
    def mode(self) -> OfflineMode:
        return self._mode

    def transition(self, connected: bool) -> OfflineMode:
        if connected:
            self._mode = OfflineMode.ONLINE
            self._cache.clear()
        elif self._mode is OfflineMode.ONLINE:
            self._mode = OfflineMode.AUTO
        return self._mode

    def cache_command(self, cmd: str) -> None:
        self._cache.append(cmd)

    def has_cached_commands(self) -> bool:
        return len(self._cache) > 0
