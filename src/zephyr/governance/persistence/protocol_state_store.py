# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.persistence.protocol_state_store
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 协议状态持久化不可丢失;崩溃恢复必须可用
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Protocol State Store — v0.10.0 协议运行时状态持久化: JSON snapshot+recovery state+crash恢复。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: state_dir 参数
#   fields: 参数 state_dir（无注解）
#   code: protocol_state_store.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ProtocolStateStore
#   name_en: ProtocolStateStore
#   intro: class ProtocolStateStore 源码 L55-L80
#   desc: 公共方法（定义序）: state, save, update；源码 L55-L80
#   inputs: state_dir
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ProtocolStateStore
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime


class ProtocolStateStore:
    def __init__(self, state_dir: str = ".audit_cache"):
        self._dir = state_dir
        self._state: dict = {}
        os.makedirs(self._dir, exist_ok=True)

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def state(self) -> dict:
        """只读：state（Stage 4 公共化）。"""
        return self._state

    @state.setter
    def state(self, value):
        """写入：state（Stage 4 公共化）。"""
        self._state = value

    def save(self) -> str:
        snapshot = {"state": self._state, "timestamp": datetime.now(UTC).isoformat()}
        path = os.path.join(self._dir, "protocol_state.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, default=str)
        return path

    def update(self, key: str, value):
        self._state[key] = value
