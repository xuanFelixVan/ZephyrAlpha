# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §8
# [MODULE] zephyr.governance.integrity
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.models; zephyr.gov_audit.merkle_hourly; zephyr.gov_audit.trust_bridge; zephyr.gov_audit.integrity (IntegrityVerifier 惰性转引)
# [CONSUMERS] zephyr.gov_audit.cli; zephyr.feedback_loop.scheduler; zephyr.gov_audit.__init__ (lazy re-export IntegrityGuard)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 校验所有审计组件健康状态; 不通过则禁止审计操作
# [MODIFY-GUARD] 新增审计组件必须在此注册健康检查
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 校验失败返回pass=False
# [TESTS] tests/audit-orchestrator/test_integrity.py
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from typing import Any

from zephyr.gov_audit.models import AuditContext

logger = logging.getLogger(__name__)

__all__ = ["IntegrityGuard", "IntegrityVerifier"]


def __getattr__(name: str):
    """IntegrityVerifier 惰性转引到 canonical 真源 zephyr.gov_audit.integrity。

    治本（2026-08-17 AI-AUDIT13）：原本地 stub（compute_hash 返回 ""、verify 恒 True、
    无 verify_chain）被 zephyr.gov_audit.cli 与 zephyr.feedback_loop.scheduler 当作
    真验证器调用——审计链完整性检查形同虚设（stub verify 恒通过 / verify_chain
    AttributeError 被 except 吞掉）。真实现唯一真源在 gov_audit.integrity
    （哈希链 + HMAC + Ed25519 + Merkle，MOD-INF-020 §5），此处 PEP 562 惰性转引，
    消除第二真源并修复两条断链消费者。无 import 时循环风险（调用方触发时才解析）。
    """
    if name == "IntegrityVerifier":
        from zephyr.gov_audit.integrity import IntegrityVerifier

        return IntegrityVerifier
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


class IntegrityGuard:
    def __init__(self) -> None:
        self._merkle_bridge = None
        self._trust_bridge = None
        self._available = False
        try:
            from zephyr.gov_audit.merkle_hourly import MerkleHourlyBridge

            self._merkle_bridge = MerkleHourlyBridge()
            self._available = True
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("MerkleHourlyBridge not available: %s", exc, exc_info=True)

        try:
            from zephyr.gov_audit.trust_bridge import TrustBridge

            self._trust_bridge = TrustBridge()
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("TrustBridge not available: %s", exc, exc_info=True)

    def check(self, context: AuditContext) -> dict[str, Any]:
        checks: dict[str, bool] = {}
        errors: list[str] = []

        checks["session_id_valid"] = bool(context.session_id)
        if not checks["session_id_valid"]:
            errors.append("Missing session_id")

        checks["mode_valid"] = context.mode in ("incremental", "full")
        if not checks["mode_valid"]:
            errors.append(f"Invalid mode: {context.mode}")

        checks["max_rounds_valid"] = 0 < context.max_rounds <= 10
        if not checks["max_rounds_valid"]:
            errors.append(f"Invalid max_rounds: {context.max_rounds}")

        checks["merkle_available"] = self._merkle_bridge is not None and self._merkle_bridge.is_available()
        checks["trust_available"] = self._trust_bridge is not None and self._trust_bridge.is_available()

        all_pass = all(checks.values()) and len(errors) == 0
        return {
            "pass": all_pass,
            "checks": checks,
            "errors": errors,
        }

    def verify_merkle(self, hour_key: str, expected_root: str) -> bool:
        if self._merkle_bridge and self._merkle_bridge.is_available():
            return self._merkle_bridge.verify(hour_key, expected_root)
        return False

    def health_report(self) -> dict[str, Any]:
        return {
            "merkle": self._merkle_bridge is not None and self._merkle_bridge.is_available(),
            "trust": self._trust_bridge is not None and self._trust_bridge.is_available(),
        }
