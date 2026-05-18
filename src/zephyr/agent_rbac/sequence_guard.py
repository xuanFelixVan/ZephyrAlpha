# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.sequence_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
L4 Sequence Guard — 操作序列追踪与危险序列阻断

MOD-INF-018 §2.7  D-018-09

每会话独立操作链 + forbidden_sequences + 跨Session关联。
"""

import time
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class SequenceEvent:
    session_id: str
    operation: str
    target: str
    timestamp: float = field(default_factory=time.time)

    def signature(self) -> str:
        return f"{self.operation}:{self.target}"


FORBIDDEN_SEQUENCES: list[dict] = [
    {
        "name": "data_exfiltration",
        "pattern": ["read:credential", "write:network", "delete:log"],
        "description": "Read credentials → Write to network → Delete logs",
    },
    {
        "name": "privilege_escalation",
        "pattern": ["read:rbac_config", "modify:self_permission", "execute:admin"],
        "description": "Read RBAC → Modify self permissions → Execute as admin",
    },
    {
        "name": "destruction_chain",
        "pattern": ["read:config", "write:destructive", "delete:backup"],
        "description": "Read config → Write destructive → Delete backups",
    },
    {
        "name": "worm_propagation",
        "pattern": ["create:agent", "inject:prompt", "spread:cross_session"],
        "description": "Create agent → Inject prompt → Spread to other sessions",
    },
    {
        "name": "audit_wipe",
        "pattern": ["read:audit_log", "modify:audit_log", "delete:audit_log"],
        "description": "Read audit → Modify audit → Delete audit logs",
    },
    {
        "name": "identity_theft",
        "pattern": ["read:agent_identity", "forge:session_token", "impersonate:agent"],
        "description": "Read identity → Forge token → Impersonate",
    },
]

SEQUENCE_TIMEOUT = 300


class SequenceGuard:
    def __init__(self, db_path: Optional[Path] = None) -> None:
        self._db_path = db_path or Path("var/agent_rbac/sequence_guard.db")
        self._sequences: dict[str, list[SequenceEvent]] = {}
        self._forbidden = [dict(s) for s in FORBIDDEN_SEQUENCES]
        self._timeout = SEQUENCE_TIMEOUT
        self._whitelist: list[list[str]] = []

    def record(self, event: SequenceEvent) -> Optional[str]:
        session = self._sequences.setdefault(event.session_id, [])
        self._expire_old(session)
        session.append(event)

        for rule in self._forbidden:
            if self._match_sequence(session, rule["pattern"]):
                return f"FORBIDDEN: {rule['name']} — {rule['description']}"

        return None

    def check_cross_session(self, events: list[SequenceEvent]) -> Optional[str]:
        by_session: dict[str, list[str]] = {}
        for e in events:
            ops = by_session.setdefault(e.session_id, [])
            ops.append(e.signature())

        sessions = list(by_session.keys())
        for i in range(len(sessions)):
            for j in range(i + 1, len(sessions)):
                if self._detect_collaboration(
                    by_session[sessions[i]],
                    by_session[sessions[j]],
                ):
                    return f"Inter-agent communication detected between {sessions[i]} and {sessions[j]}"

        return None

    def add_whitelist(self, pattern: list[str]) -> None:
        self._whitelist.append(pattern)

    def is_whitelisted(self, session: list[SequenceEvent]) -> bool:
        sigs = [e.signature() for e in session]
        for wl in self._whitelist:
            if self._is_subsequence(sigs, wl):
                return True
        return False

    def _match_sequence(self, session: list[SequenceEvent], pattern: list[str]) -> bool:
        if len(session) < len(pattern):
            return False
        recent = session[-len(pattern):]
        sigs = [e.signature() for e in recent]
        return self._is_subsequence(sigs, pattern)

    def _is_subsequence(self, sigs: list[str], pattern: list[str]) -> bool:
        sigs_lower = [s.lower() for s in sigs]
        pattern_lower = [p.lower() for p in pattern]
        pi = 0
        for s in sigs_lower:
            if pi >= len(pattern_lower):
                break
            if pattern_lower[pi] in s:
                pi += 1
        return pi == len(pattern_lower)

    def _detect_collaboration(self, ops_a: list[str], ops_b: list[str]) -> bool:
        write_read_pairs = 0
        for a in ops_a:
            a_cat = a.split(":")[0] if ":" in a else a
            for b in ops_b:
                b_cat = b.split(":")[0] if ":" in b else b
                if (a_cat == "write" and b_cat == "read") or (a_cat == "create" and b_cat == "execute"):
                    write_read_pairs += 1
        return write_read_pairs >= 2

    def _expire_old(self, session: list[SequenceEvent]) -> None:
        cutoff = time.time() - self._timeout
        while session and session[0].timestamp < cutoff:
            session.pop(0)

    def reset_session(self, session_id: str) -> None:
        self._sequences.pop(session_id, None)

    def reset_all(self) -> None:
        self._sequences.clear()
        self._whitelist.clear()
