# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.forensic.crypto_bootstrap
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Cryptographic Bootstrap — v0.15.0 R204

Blindspot: FLE action log tamperable; no cryptographic chain of trust from genesis.
Risk: R204 — Attacker rewrites FLE audit trail; first recorded state is fiction.

Mitigation: Genesis->Current hash chain; every state transition cryptographically linked to predecessor.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: crypto_bootstrap.py
# 层: 算法
# - id: A1
#   name_zh: ① CryptoBootstrap
#   name_en: CryptoBootstrap
#   intro: class CryptoBootstrap 源码 L72-L104
#   desc: 公共方法（定义序）: genesis, append, verify_chain；源码 L72-L104
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CryptoBootstrap
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field


@dataclass
class HashLink:
    index: int
    timestamp: float
    action_hash: str
    prev_hash: str
    state_hash: str


@dataclass
class CryptoBootstrap:
    genesis_hash: str = ""
    chain: list[HashLink] = field(default_factory=list)

    def genesis(self, initial_state: dict) -> str:
        state_json = json.dumps(initial_state, sort_keys=True)
        self.genesis_hash = hashlib.sha256(f"GENESIS:{state_json}".encode()).hexdigest()
        self.chain.append(
            HashLink(
                index=0, timestamp=time.time(), action_hash="GENESIS", prev_hash="0" * 64, state_hash=self.genesis_hash
            )
        )
        return self.genesis_hash

    def append(self, action: str, state: dict) -> HashLink:
        action_hash = hashlib.sha256(action.encode()).hexdigest()
        state_hash = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
        prev_hash = self.chain[-1].state_hash if self.chain else self.genesis_hash
        link = HashLink(
            index=len(self.chain),
            timestamp=time.time(),
            action_hash=action_hash,
            prev_hash=prev_hash,
            state_hash=state_hash,
        )
        self.chain.append(link)
        return link

    def verify_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            if self.chain[i].prev_hash != self.chain[i - 1].state_hash:
                return False
        return True
