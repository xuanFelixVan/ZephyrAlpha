# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.verifiers.cross_session_knowledge_integrity

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Cross-Session Knowledge Integrity — v0.16.0 R225

Blindspot: KB fragments across AI sessions; knowledge continuity broken between sessions.
Risk: R225 — Session N+1 starts with KB corruption; diagnosis chain severed.

Mitigation: Hash anchor across sessions + continuity audit to detect KB fragmentation.
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
