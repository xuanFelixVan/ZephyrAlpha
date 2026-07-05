# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.anomaly.silent_corruption_detector
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_silent_corruption_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""Silent Corruption Detector — v0.40.0 R499

Blindspot: Stored metrics, baselines, and checkpoints can suffer silent data
corruption — bit flips in RAM/disk, cosmic rays, faulty storage controllers,
truncated writes. No checksum validation on read-back means corrupted data
enters the FLE pipeline undetected.

Risk: R499 — Corrupted baselines produce phantom anomalies or mask real ones.
FLE acts on data that is silently wrong, producing cascading bad decisions.

Mitigation: Attach SHA256 checksum to every persisted data block. Validate
checksum on every read. Track corruption events per storage sink. When
corruption rate exceeds threshold → alert and quarantine the sink.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum


class CorruptionSeverity(str, Enum):
    NONE = "NONE"
    ISOLATED = "ISOLATED"
    PATTERN = "PATTERN"
    SYSTEMIC = "SYSTEMIC"


@dataclass
class SilentCorruptionDetector:
    max_corruption_rate: float = 0.001
    systemic_threshold: int = 5

    read_validations: dict[str, dict] = field(default_factory=dict)
    corruption_events: list[dict] = field(default_factory=list)
    quarantined_sinks: set[str] = field(default_factory=set)

    def seal(self, data: bytes) -> tuple[bytes, str]:
        checksum = hashlib.sha256(data).hexdigest()
        return data, checksum

    def validate(self, sink_name: str, block_id: str, data: bytes, expected_checksum: str) -> dict:
        actual_checksum = hashlib.sha256(data).hexdigest()
        valid = actual_checksum == expected_checksum

        if sink_name not in self.read_validations:
            self.read_validations[sink_name] = {"total": 0, "corrupted": 0, "recent": []}

        stats = self.read_validations[sink_name]
        stats["total"] += 1
        if not valid:
            stats["corrupted"] += 1

        stats["recent"].append({"ts": time.time(), "valid": valid})
        if len(stats["recent"]) > 100:
            stats["recent"] = stats["recent"][-100:]

        corruption_rate = stats["corrupted"] / max(stats["total"], 1)

        if corruption_rate > self.max_corruption_rate * 3:
            severity = CorruptionSeverity.SYSTEMIC
            self.quarantined_sinks.add(sink_name)
        elif corruption_rate > self.max_corruption_rate:
            severity = CorruptionSeverity.PATTERN
        elif not valid:
            severity = CorruptionSeverity.ISOLATED
        else:
            severity = CorruptionSeverity.NONE

        if not valid:
            self.corruption_events.append(
                {
                    "ts": time.time(),
                    "sink": sink_name,
                    "block_id": block_id,
                    "expected_checksum": expected_checksum[:16],
                    "actual_checksum": actual_checksum[:16],
                    "severity": severity.value,
                }
            )

        return {
            "valid": valid,
            "sink": sink_name,
            "block_id": block_id,
            "severity": severity.value,
            "corruption_rate": round(corruption_rate, 6),
            "recommendation": (
                "quarantine_sink_and_investigate_hardware"
                if severity is CorruptionSeverity.SYSTEMIC
                else "trigger_integrity_scan"
                if severity is CorruptionSeverity.PATTERN
                else "log_and_monitor"
                if not valid
                else "continue"
            ),
        }

    def is_sink_quarantined(self, sink_name: str) -> bool:
        return sink_name in self.quarantined_sinks

    def get_sink_health_summary(self) -> dict:
        result = {}
        for sink, stats in self.read_validations.items():
            rate = stats["corrupted"] / max(stats["total"], 1)
            result[sink] = {
                "total_reads": stats["total"],
                "corrupted_reads": stats["corrupted"],
                "corruption_rate": round(rate, 6),
                "quarantined": sink in self.quarantined_sinks,
                "healthy": rate <= self.max_corruption_rate,
            }
        return result

    def get_total_corruptions(self) -> int:
        return len(self.corruption_events)

    def overall_data_integrity(self) -> float:
        total_reads = sum(s["total"] for s in self.read_validations.values())
        total_corrupted = sum(s["corrupted"] for s in self.read_validations.values())
        if total_reads == 0:
            return 1.0
        return round(max(0.0, 1.0 - total_corrupted / total_reads * 100), 6)
