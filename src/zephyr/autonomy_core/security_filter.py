# [BLUEPRINT] MOD-MASTER-001 | docs/03_modules/_master-blueprint/blueprint_baseline.md | CT-CE-LSG-001
# [MODULE] zephyr.autonomy_core.security_filter
# [DOMAIN] D-AUTONOMY_CORE
# [DEPENDENCIES] zephyr.security.llm_defense.llm_security_01.context_scanner
# [CONSUMERS] zephyr.autonomy_core.task_context_builder
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 上下文构建完成后MUST经过此过滤器; blocked blocks不注入; warnings记录; 降级不阻塞
# [MODIFY-GUARD] CT-CE-LSG-001 协议变更必须同步更新llm_security/context_scanner
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LSG不可用返回original_blocks+degraded_warning; 空输入返回空
# [TESTS] scripts/connect/ce_lsg.py --trigger
# [A_module] module_id=MOD-ORC_security_filter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""CE 安全过滤器 — filter_context() 生产者

CT-CE-LSG-001: 将构建好的上下文块送入 LSGSecurityGateway 扫描后返回安全的执行上下文。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "FilterResult",
    "SecurityFilter",
    "filter_context",
]


@dataclass
class FilterResult:
    safe_blocks: list[dict[str, Any]] = field(default_factory=list)
    blocked_blocks: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    passed: bool = True
    scan_duration_ms: int = 0


class SecurityFilter:
    def filter(
        self,
        blocks: list[dict[str, Any]],
        task_id: str = "",
        session_id: str = "",
    ) -> FilterResult:
        if not blocks:
            return FilterResult(passed=True)

        try:
            from zephyr.security.llm_defense.llm_security_01.context_scanner import scan_context

            response = scan_context(blocks, task_id, session_id)

            logger.info(
                "[CE-LSG] filter: task=%s passed=%s safe=%d blocked=%d warnings=%d elapsed=%dms",
                task_id,
                response.passed,
                len(response.sanitized_blocks),
                len(response.blocked_blocks),
                len(response.warnings),
                response.scan_duration_ms,
            )

            return FilterResult(
                safe_blocks=response.sanitized_blocks,
                blocked_blocks=response.blocked_blocks,
                warnings=response.warnings,
                passed=response.passed,
                scan_duration_ms=response.scan_duration_ms,
            )
        except Exception as exc:
            logger.warning("[CE-LSG] LSG unavailable, degraded pass: %s", exc)
            return FilterResult(
                safe_blocks=list(blocks),
                blocked_blocks=[],
                warnings=[{"rule": "degraded", "message": f"LSG unavailable: {exc}"}],
                passed=True,
                scan_duration_ms=0,
            )


def filter_context(
    blocks: list[dict[str, Any]],
    task_id: str = "",
    session_id: str = "",
) -> FilterResult:
    return SecurityFilter().filter(blocks, task_id, session_id)
