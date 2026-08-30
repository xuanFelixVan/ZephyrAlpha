# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.architecture_governance.local_first_arch
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.architecture_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: local_first_arch.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: ComputeLocation, LocalFirstPolicy
#   desc: 数据契约/异常/枚举声明共 2 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（2 类）
#   name_en: data classes
#   intro: ComputeLocation, LocalFirstPolicy
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum
from typing import Final

from pydantic import BaseModel


class ComputeLocation(str, Enum):
    LOCAL = "LOCAL"
    CLOUD_BACKFILL = "CLOUD_BACKFILL"


class LocalFirstPolicy(BaseModel):
    all_compute: ComputeLocation = ComputeLocation.LOCAL
    websocket_dep: str = "唯一远程依赖——仅WebSocket行情"
    cloud_role: str = "backfill only — 灾备恢复用"
    zero_cloud_dep: bool = True

    def is_local_first(self) -> bool:
        return self.all_compute is ComputeLocation.LOCAL and self.zero_cloud_dep


LOCAL_FIRST: Final[LocalFirstPolicy] = LocalFirstPolicy()
