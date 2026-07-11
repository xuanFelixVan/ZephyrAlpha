# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.forensic.self_modification_audit
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_self_modification_audit | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Self-Modification Audit — v0.15.0 R218

Blindspot: FLE can modify its own code/config; self-modification invisible.
Risk: R218 — FLE "self-upgrade" introduces backdoor; no audit of self-modifications.

Mitigation: File integrity monitoring on all FLE source/config files; alert on unexpected changes.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from zephyr.shared.utils.time_utils import now_utc


@dataclass
class FileIntegrity:
    path: str
    sha256: str
    last_verified: str = ""


@dataclass
class SelfModificationAudit:
    files: dict[str, FileIntegrity] = field(default_factory=dict)
    unauthorized_changes: list[str] = field(default_factory=list)
    protected_paths: list[str] = field(default_factory=list)

    def register(self, filepath: str, content: str) -> None:
        sha = hashlib.sha256(content.encode()).hexdigest()
        self.files[filepath] = FileIntegrity(path=filepath, sha256=sha, last_verified=now_utc().isoformat())

    def verify(self, filepath: str, current_content: str) -> bool:
        current_sha = hashlib.sha256(current_content.encode()).hexdigest()
        record = self.files.get(filepath)
        if record is None:
            return True
        if record.sha256 != current_sha:
            self.unauthorized_changes.append(filepath)
            return False
        record.last_verified = now_utc().isoformat()
        return True

    def scan_all(self, file_contents: dict[str, str]) -> list[str]:
        return [f for f, c in file_contents.items() if not self.verify(f, c)]
