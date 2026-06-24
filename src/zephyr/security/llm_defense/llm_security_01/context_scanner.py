# [BLUEPRINT] MOD-MASTER-001 | docs/03_modules/_master_blueprint/blueprint_baseline.md | CT-CE-LSG-001
# [MODULE] zephyr.security.llm_defense.llm_security_01.context_scanner
# [DOMAIN] D-SECURITY
# [DEPENDENCIES] zephyr.security.llm_defense.llm_security.gateway
# [CONSUMERS] zephyr.autonomy_core.security_filter
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 九层纵深扫描; fail-closed: 任一层DENY→整体DENY; 不可用时返回pass+degraded_marker
# [MODIFY-GUARD] CT-CE-LSG-001 协议变更必须同步更新context_engine/security_filter
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LSGSecurityGateway不可用返回status=degraded不阻断; 空blocks返回passed
# [TESTS] scripts/connect/ce_lsg.py --trigger
# [A_module] module_id=MOD-SEC_context_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""LSG 上下文扫描器 — scan_context() 消费者

CT-CE-LSG-001: 接收 CE 投递的上下文块, 九层纵深防御扫描后返回安全判定。
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "ContextScanner",
    "SecurityCheckResponse",
    "scan_context",
]


@dataclass
class SecurityCheckResponse:
    passed: bool = True
    blocked_blocks: list[dict[str, Any]] = field(default_factory=list)
    sanitized_blocks: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    scan_duration_ms: int = 0


class ContextScanner:
    def scan_context(
        self,
        blocks: list[dict[str, Any]],
        task_id: str = "",
        session_id: str = "",
    ) -> SecurityCheckResponse:
        if not blocks:
            return SecurityCheckResponse(passed=True)

        t0 = time.perf_counter()

        try:
            from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway

            gateway = LSGSecurityGateway()
            blocked: list[dict[str, Any]] = []
            sanitized: list[dict[str, Any]] = []
            warnings: list[dict[str, Any]] = []
            all_passed = True

            async def _scan_all() -> None:
                nonlocal all_passed
                for i, block in enumerate(blocks):
                    content = block.get("content", "")
                    if not content:
                        sanitized.append(block)
                        continue
                    try:
                        result = await gateway.scan_input(
                            text=str(content)[:5000],
                            source=f"ce-context-block-{i}",
                            metadata={
                                "request_id": f"ce-lsg-{task_id}-{i}",
                                "block_index": i,
                                "block_type": block.get("type", "unknown"),
                                "session_id": session_id,
                            },
                        )
                    except Exception:
                        sanitized.append(block)
                        continue

                    if result.decision.value == "DENY":
                        all_passed = False
                        blocked.append(block)
                        warnings.append(
                            {
                                "block_index": i,
                                "rule": f"layer_{result.layers_denied}",
                                "message": f"Blocked by LSG: layers_evaluated={result.layers_evaluated} layers_denied={result.layers_denied}",
                            }
                        )
                        logger.info(
                            "[CE-LSG] blocked block %d: type=%s decision=%s",
                            i,
                            block.get("type"),
                            result.decision,
                        )
                    elif result.decision.value == "FLAG":
                        sanitized.append(block)
                        warnings.append(
                            {
                                "block_index": i,
                                "rule": "flagged",
                                "message": f"Flagged: score={result.total_score}",
                            }
                        )
                    else:
                        sanitized.append(block)

            asyncio.run(_scan_all())

            elapsed = round((time.perf_counter() - t0) * 1000)
            logger.info(
                "[CE-LSG] scan: task=%s passed=%s elapsed=%dms blocked=%d warnings=%d",
                task_id,
                all_passed,
                elapsed,
                len(blocked),
                len(warnings),
            )

            return SecurityCheckResponse(
                passed=all_passed,
                blocked_blocks=blocked,
                sanitized_blocks=sanitized,
                warnings=warnings,
                scan_duration_ms=elapsed,
            )
        except Exception as exc:
            elapsed = round((time.perf_counter() - t0) * 1000)
            logger.error("[CE-LSG] scan failed (degraded): %s", exc)
            return SecurityCheckResponse(
                passed=True,
                sanitized_blocks=list(blocks),
                warnings=[{"rule": "degraded", "message": f"LSG unavailable: {exc}"}],
                scan_duration_ms=elapsed,
            )


def scan_context(
    blocks: list[dict[str, Any]],
    task_id: str = "",
    session_id: str = "",
) -> SecurityCheckResponse:
    return ContextScanner().scan_context(blocks, task_id, session_id)
