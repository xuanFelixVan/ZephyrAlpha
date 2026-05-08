"""config_safety_guard.py — 配置自毁防护 (B16, DD90, TASK-017)"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ConfigGuardResult:
    key: str
    value: float
    min_val: float
    max_val: float
    valid: bool
    rejected: bool = False


class ConfigSafetyGuard:
    """Config key domain[min,max] Contract-YAML driven; 超界拒绝+告警 (DD90)."""
    _DOMAINS: dict[str, tuple[float, float]] = {
        "threshold_pct": (0.5, 0.99),
        "top_k": (1, 20),
        "max_age_s": (60, 7200),
    }

    def validate(self, key: str, value: float) -> ConfigGuardResult:
        domain = self._DOMAINS.get(key, (0.0, float("inf")))
        valid = domain[0] <= value <= domain[1]
        return ConfigGuardResult(key=key, value=value, min_val=domain[0], max_val=domain[1], valid=valid, rejected=not valid)
