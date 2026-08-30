# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.verifiers.cross_session_knowledge_integrity
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Cross-Session Knowledge Integrity — v0.16.0 R225

Blindspot: KB fragments across AI sessions; knowledge continuity broken between sessions.
Risk: R225 — Session N+1 starts with KB corruption; diagnosis chain severed.

Mitigation: Hash anchor across sessions + continuity audit to detect KB fragmentation.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: cross_session_knowledge_integrity.py
# 层: 算法
# - id: A1
#   name_zh: ① CrossSessionKnowledgeIntegrity
#   name_en: CrossSessionKnowledgeIntegrity
#   intro: class CrossSessionKnowledgeIntegrity 源码 L70-L86
#   desc: 公共方法（定义序）: anchor, verify_continuity；源码 L70-L86
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CrossSessionKnowledgeIntegrity
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
from dataclasses import dataclass, field


@dataclass
class SessionAnchor:
    session_id: str
    kb_hash: str
    prev_anchor_hash: str = ""
    timestamp: str = ""


@dataclass
class CrossSessionKnowledgeIntegrity:
    anchors: list[SessionAnchor] = field(default_factory=list)
    genesis_kb_hash: str = ""

    def anchor(self, session_id: str, knowledge: dict) -> SessionAnchor:
        kb_hash = hashlib.sha256(json.dumps(knowledge, sort_keys=True).encode()).hexdigest()[:16]
        prev_hash = self.anchors[-1].kb_hash if self.anchors else self.genesis_kb_hash
        anchor = SessionAnchor(session_id=session_id, kb_hash=kb_hash, prev_anchor_hash=prev_hash)
        self.anchors.append(anchor)
        return anchor

    def verify_continuity(self) -> list[int]:
        breaks: list[int] = []
        for i in range(1, len(self.anchors)):
            if self.anchors[i].prev_anchor_hash != self.anchors[i - 1].kb_hash:
                breaks.append(i)
        return breaks
