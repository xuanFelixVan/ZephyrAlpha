# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.gov_audit.forensic_package
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 证据包不可篡改;因果图必须完整
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Forensic Package — v0.8.0 取证就绪: escalation event bundle+hash chain+timestamp。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: forensic_package.py
# 层: 算法
# - id: A1
#   name_zh: ① ForensicPackage
#   name_en: ForensicPackage
#   intro: class ForensicPackage 源码 L56-L99
#   desc: 公共方法（定义序）: chain, events, bundle, verify_chain；源码 L56-L99
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ForensicPackage
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from zephyr.shared.io.serialization import dumps


class ForensicPackage:
    def __init__(self):
        self._events: list[dict] = []
        self._chain: list[str] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def chain(self) -> list[str]:
        """只读：chain（Stage 4 公共化）。"""
        return self._chain

    @chain.setter
    def chain(self, value):
        """写入：chain（Stage 4 公共化）。"""
        self._chain = value

    @property
    def events(self) -> list[dict]:
        """只读：events（Stage 4 公共化）。"""
        return self._events

    @events.setter
    def events(self, value):
        """写入：events（Stage 4 公共化）。"""
        self._events = value

    def bundle(self, event: dict) -> str:
        serialized = dumps(event, sort_keys=True)
        h = hashlib.sha256(serialized.encode()).hexdigest()
        self._events.append({"hash": h, "timestamp": datetime.now(UTC).isoformat(), "event": event})
        if self._chain:
            prev = self._chain[-1]
            h = hashlib.sha256((prev + serialized).encode()).hexdigest()
        self._chain.append(h)
        return h

    def verify_chain(self) -> bool:
        for i in range(1, len(self._chain)):
            prev = self._chain[i - 1]
            curr_event = dumps(self._events[i]["event"], sort_keys=True)
            expected = hashlib.sha256((prev + curr_event).encode()).hexdigest()
            if expected != self._chain[i]:
                return False
        return True
