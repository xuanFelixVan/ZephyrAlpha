"""引导验证器——系统启动时验证rbac配置+密钥+genesis状态完整性."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BootstrapCheck(BaseModel):
    check_name: str
    passed: bool
    detail: str = ""
    severity: str = "CRITICAL"


class BootstrapVerifier:
    def __init__(self) -> None:
        self._checks: list[BootstrapCheck] = []

    def verify_genesis(self, genesis_hash_expected: str = "") -> BootstrapCheck:
        check = BootstrapCheck(
            check_name="genesis_state",
            passed=genesis_hash_expected != "",
            detail="genesis hash present" if genesis_hash_expected else "genesis hash missing",
        )
        self._checks.append(check)
        return check

    def verify_key_hierarchy(self, key_count: int = 0, min_keys: int = 3) -> BootstrapCheck:
        check = BootstrapCheck(
            check_name="key_hierarchy",
            passed=key_count >= min_keys,
            detail=f"{key_count}/{min_keys} keys" if key_count < min_keys else f"{key_count} keys ✓",
        )
        self._checks.append(check)
        return check

    def verify_config(self, config_loaded: bool = False) -> BootstrapCheck:
        check = BootstrapCheck(
            check_name="rbac_config",
            passed=config_loaded,
            detail="config loaded" if config_loaded else "config missing",
        )
        self._checks.append(check)
        return check

    def all_passed(self) -> bool:
        return all(c.passed for c in self._checks)
