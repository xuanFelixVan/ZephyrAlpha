# [BLUEPRINT] MOD-INF-008 | 03_modules/_cross_layer/context-engine/blueprint.md | §

# [MODULE] zephyr.context_engine.fallback_staleness_gate

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""fallback_staleness_gate.py — 兜底层自腐检测 (B13, DD87, TASK-017)"""
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

UTC = timezone.utc


@dataclass
class StalenessReport:
    file_path: str
    sha256: str
    age_days: float
    is_stale: bool
    alert_message: str


class FallbackStalenessGate:
    """embedded_defaults SHA256 + age check; >90d alert (DD87)."""
    def __init__(self, defaults_file: str | Path = "AGENTS.md") -> None:
        self._file = Path(defaults_file)

    def check(self) -> StalenessReport:
        exists = self._file.exists()
        sha = hashlib.sha256(self._file.read_bytes()).hexdigest() if exists else ""
        age = 0.0
        if exists:
            age = (datetime.now(UTC) - datetime.fromtimestamp(self._file.stat().st_mtime, UTC)).total_seconds() / 86400
        is_stale = age > 90
        return StalenessReport(
            file_path=str(self._file),
            sha256=sha[:16],
            age_days=round(age, 1),
            is_stale=is_stale,
            alert_message=f"AGENTS.md is {age:.0f} days old — needs review" if is_stale else "OK",
        )
