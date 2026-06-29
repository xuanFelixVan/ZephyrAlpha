# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.infrastructure.budget_enforcement.tamper_evident_log
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.audit_trail.writer
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_tamper_evident_log | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LogEntry:
    entry_id: str
    action: str
    data: str
    prev_hash: str
    timestamp: float = field(default_factory=time.time)
    hash: str = ""


class TamperEvidentLog:
    def __init__(self, log_path: str = "logs/tamper_evident.jsonl"):
        self._log_path = Path(log_path)
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        self._chain: list[LogEntry] = []
        self._last_hash: str = "0" * 64
        self._counter: int = 0
        self._load_chain()

    def _load_chain(self) -> None:
        if not self._log_path.exists():
            return
        with open(self._log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = LogEntry(
                        entry_id=data.get("entry_id", ""),
                        action=data.get("action", ""),
                        data=data.get("data", ""),
                        prev_hash=data.get("prev_hash", ""),
                        timestamp=data.get("timestamp", 0.0),
                        hash=data.get("hash", ""),
                    )
                    self._chain.append(entry)
                    self._last_hash = entry.hash
                    self._counter += 1
                except (json.JSONDecodeError, KeyError):
                    continue

    def append(self, action: str, data: str) -> LogEntry:
        self._counter += 1
        now = time.time()
        raw = f"{self._counter}:{action}:{data}:{now}:{self._last_hash}"
        h = hashlib.sha256(raw.encode()).hexdigest()

        entry = LogEntry(
            entry_id=f"tel-{self._counter:06d}",
            action=action,
            data=data,
            prev_hash=self._last_hash,
            timestamp=now,
            hash=h,
        )
        self._chain.append(entry)
        self._last_hash = h

        with open(self._log_path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "entry_id": entry.entry_id,
                        "action": entry.action,
                        "data": entry.data,
                        "prev_hash": entry.prev_hash,
                        "timestamp": entry.timestamp,
                        "hash": entry.hash,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

        try:
            from zephyr.governance.audit_trail.writer import get_audit_writer

            get_audit_writer().write(
                {
                    "event_type": "budget_enforcement",
                    "action_type": action,
                    "agent_id": "budget-enforcer",
                    "target_path": str(self._log_path),
                    "operation": action,
                }
            )
        except Exception:
            pass

        return entry

    def verify(self) -> tuple[bool, int]:
        prev = "0" * 64
        for i, entry in enumerate(self._chain):
            raw = f"{i + 1}:{entry.action}:{entry.data}:{entry.timestamp}:{prev}"
            expected = hashlib.sha256(raw.encode()).hexdigest()
            if expected != entry.hash:
                return False, i
            prev = entry.hash
        return True, len(self._chain)

    def recent(self, n: int = 20) -> list[LogEntry]:
        return self._chain[-n:]

    def chain_length(self) -> int:
        return len(self._chain)

    def tail_hash(self) -> str:
        return self._last_hash
