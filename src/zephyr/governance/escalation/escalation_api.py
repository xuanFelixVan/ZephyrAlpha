# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.escalation_api
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 模块接口签名不可变
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_escalation_api | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""

Escalation API — v0.7.0 Service Account API: 外部系统安全触发升级，不绕过引擎。
v0.7.0: 集成EscalationEngine + 速率限制 + 审计日志
"""

from __future__ import annotations

import logging
import time
from collections import deque
from datetime import UTC, datetime

logger = logging.getLogger(__name__)


class EscalationAPI:
    def __init__(self, engine: object = None, rate_limit_per_hour: int = 100):
        self._api_keys: dict[str, str] = {}
        self._engine = engine
        self._rate_limit_per_hour = rate_limit_per_hour
        self._rate_buckets: dict[str, deque] = {}
        self._audit_log: list[dict] = []

    def register_service(self, service_name: str, api_key: str):
        self._api_keys[service_name] = api_key

    def validate_request(self, service_name: str, api_key: str, operation: str) -> tuple[bool, str]:
        expected = self._api_keys.get(service_name)
        if expected is None:
            return False, "Unknown service"
        if expected != api_key:
            return False, "Invalid API key"
        return True, "OK"

    def _check_rate_limit(self, service_name: str) -> bool:
        now = time.monotonic()
        window = 3600.0
        if service_name not in self._rate_buckets:
            self._rate_buckets[service_name] = deque()
        bucket = self._rate_buckets[service_name]
        while bucket and bucket[0] < now - window:
            bucket.popleft()
        if len(bucket) >= self._rate_limit_per_hour:
            return False
        bucket.append(now)
        return True

    def _record_audit(
        self, service_name: str, operation: str, status: str, reason: str = "", context: dict = None
    ) -> None:
        self._audit_log.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "service": service_name,
                "operation": operation,
                "status": status,
                "reason": reason,
                "context": context or {},
            }
        )

    def get_audit_log(self) -> list[dict]:
        return list(self._audit_log)

    def clear_audit_log(self) -> None:
        self._audit_log.clear()

    def trigger_escalation(self, service_name: str, api_key: str, operation: str, context: dict = None) -> dict:
        ok, reason = self.validate_request(service_name, api_key, operation)
        if not ok:
            self._record_audit(service_name, operation, "rejected", reason)
            return {"status": "rejected", "reason": reason}
        if not self._check_rate_limit(service_name):
            self._record_audit(service_name, operation, "rate_limited", f"exceeded {self._rate_limit_per_hour}/hour")
            return {"status": "rate_limited", "reason": f"Rate limit exceeded for {service_name}"}
        engine_result = None
        if self._engine is not None:
            try:
                from zephyr.governance.escalation.escalation_models import RuleCategory

                category = RuleCategory.CUSTOM
                event = self._engine.evaluate(
                    category=category,
                    description=f"API trigger: {operation} by {service_name}",
                    owner_id=service_name,
                )
                engine_result = {
                    "event_id": getattr(event, "event_id", None),
                    "level": str(getattr(event, "level", "")),
                    "state": str(getattr(event, "state", "")),
                }
            except Exception as e:
                logger.warning("Engine evaluate failed: %s", e, exc_info=True)
        self._record_audit(service_name, operation, "escalated", "OK", context)
        result = {"status": "escalated", "operation": operation, "service": service_name, "context": context or {}}
        if engine_result is not None:
            result["engine_result"] = engine_result
        return result