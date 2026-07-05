# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability.cross_session_consistency_validator
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_cross_session_consistency_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R510: CrossSessionConsistencyValidator
跨session阈值跳变+配置哈希链 — 昨天校准的阈值今天不能突变
"""

import hashlib
import json
from dataclasses import dataclass, field


@dataclass
class CrossSessionConsistencyValidator:
    config_hashes: list[dict] = field(default_factory=list)
    max_hashes: int = 50
    threshold_history: dict[str, list[float]] = field(default_factory=dict)
    jump_threshold_sigma: float = 2.0

    def record_config(self, config: dict, session_id: str) -> str:
        config_str = json.dumps(config, sort_keys=True)
        h = hashlib.sha256(config_str.encode()).hexdigest()[:16]

        entry = {
            "hash": h,
            "session_id": session_id,
            "prev_hash": self.config_hashes[-1]["hash"] if self.config_hashes else None,
        }
        self.config_hashes.append(entry)
        if len(self.config_hashes) > self.max_hashes:
            self.config_hashes = self.config_hashes[-self.max_hashes :]

        for key, value in config.items():
            if isinstance(value, (int, float)):
                if key not in self.threshold_history:
                    self.threshold_history[key] = []
                self.threshold_history[key].append(float(value))
                if len(self.threshold_history[key]) > 50:
                    self.threshold_history[key] = self.threshold_history[key][-50:]

        return h

    def detect_jumps(self) -> dict:
        jumps = {}
        for key, values in self.threshold_history.items():
            if len(values) < 3:
                continue
            result = self._check_jumps(values)
            if result:
                jumps[key] = result
        return {"jumps_detected": list(jumps.keys()), "details": jumps}

    def _check_jumps(self, values: list[float]) -> dict | None:
        mean = sum(values[:-1]) / max(len(values) - 1, 1)
        std = (sum((v - mean) ** 2 for v in values[:-1]) / max(len(values) - 1, 1)) ** 0.5
        if std < 1e-10:
            return None

        latest = values[-1]
        deviation = abs(latest - mean) / std
        if deviation > self.jump_threshold_sigma:
            return {
                "latest_value": round(latest, 4),
                "historical_mean": round(mean, 4),
                "std": round(std, 4),
                "sigma_deviation": round(deviation, 2),
                "severity": "critical" if deviation > 5 else "warning",
            }
        return None

    def verify_hash_chain(self) -> dict:
        if len(self.config_hashes) < 2:
            return {"chain_intact": True, "length": len(self.config_hashes)}

        breaks = []
        for i in range(1, len(self.config_hashes)):
            expected_prev = self.config_hashes[i].get("prev_hash")
            actual_prev = self.config_hashes[i - 1]["hash"]
            if expected_prev is not None and expected_prev != actual_prev:
                breaks.append({"index": i, "expected": expected_prev, "actual": actual_prev})

        return {"chain_intact": len(breaks) == 0, "length": len(self.config_hashes), "breaks": breaks}
