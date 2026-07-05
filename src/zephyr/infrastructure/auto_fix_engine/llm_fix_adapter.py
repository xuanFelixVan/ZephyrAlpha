# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.llm_fix_adapter
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__; zephyr.shared.contracts.llm_gateway_protocol
# [CONSUMERS] engine.py;MOD-INF-028(semantic-auditor)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] LLM输出MUST经SecretLeakGuard扫描;置信度<MEDIUM不自动应用
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml llm_fix_adapter段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LLMFixError;SecretLeakDetectedError
# [TESTS] tests/auto-fix-engine/test_llm_fix_adapter.py
# [A_module] module_id=MOD-INF_llm_fix_adapter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zephyr.shared.contracts.llm_gateway_protocol import LLMGatewayProtocol as LLMGateway

from zephyr.infrastructure.auto_fix_engine.fix_safety import SecretLeakGuard
from zephyr.infrastructure.auto_fix_engine.models import (
    BaseFixer,
    FixAction,
    FixConfidence,
    FixLevel,
    FixStatus,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class LLMFixAdapter(BaseFixer):

    def __init__(self) -> None:
        super().__init__(
            fixer_id="llm_fix_adapter",
            action_type="llm_fix",
            level=FixLevel.L2_LLM,
            dimension="DIM-SEMANTIC-001",
            description="L2 LLM 修复桥接",
        )
        self._secret_guard = SecretLeakGuard()
        self._llm_bridge: LLMGateway | None = None

    def _get_llm_bridge(self) -> Any:
        if self._llm_bridge is not None:
            return self._llm_bridge
        try:
            from zephyr.shared.contracts.llm_gateway_protocol import LLMGatewayProtocol as LLMGateway

            self._llm_bridge = LLMGateway()
            return self._llm_bridge
        except ImportError:
            logger.warning("LLMGateway not available, using fallback")
            return None

    def scan(self) -> list[dict[str, Any]]:
        return []

    def fix(self, target: str, dry_run: bool = False) -> FixAction:
        action = FixAction(
            action_type=self.action_type,
            level=self.level,
            target=target,
            confidence=FixConfidence.MEDIUM,
        )
        bridge = self._get_llm_bridge()
        if bridge is None:
            action.status = FixStatus.FAILED
            action.metadata["error"] = "LLM bridge not available"
            return action
        try:
            from pathlib import Path

            target_path = Path(target)
            if not target_path.exists():
                action.status = FixStatus.FAILED
                action.metadata["error"] = "Target not found"
                return action
            original = target_path.read_text(encoding="utf-8")
            prompt = self._build_fix_prompt(target, original)
            llm_response = self._call_llm(bridge, prompt)
            if not llm_response:
                action.status = FixStatus.FAILED
                action.metadata["error"] = "LLM returned empty response"
                return action
            is_clean, findings = self._secret_guard.scan(llm_response)
            if not is_clean:
                action.status = FixStatus.FAILED
                action.metadata["error"] = "Secret leak detected in LLM output"
                action.metadata["findings"] = findings
                action.escalated = True
                return action
            redacted, _ = self._secret_guard.scan_and_redact(llm_response)
            action.before = original
            action.after = redacted
            action.confidence = FixConfidence.MEDIUM
            if not dry_run:
                import os

                tmp_path = f"{target}.{os.getpid()}.tmp"
                try:
                    with open(tmp_path, "w", encoding="utf-8") as f:
                        f.write(redacted)
                    os.replace(tmp_path, target)
                except PermissionError:
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
                    action.status = FixStatus.FAILED
                    return action
            action.status = FixStatus.COMPLETED
        except Exception as exc:
            action.status = FixStatus.FAILED
            action.metadata["error"] = str(exc)
        return action

    def _build_fix_prompt(self, target: str, content: str) -> str:
        return (
            f"Fix the following Python file. Only fix actual issues, do not change working code.\n"
            f"File: {target}\n\n"
            f"Content:\n```\n{content}\n```\n\n"
            f"Return ONLY the fixed file content, no explanations."
        )

    def _call_llm(self, bridge: Any, prompt: str) -> str:
        try:
            if hasattr(bridge, "generate"):
                result = bridge.generate(prompt)
                return result if isinstance(result, str) else str(result)
            if hasattr(bridge, "call"):
                result = bridge.call(prompt)
                return result if isinstance(result, str) else str(result)
            return ""
        except Exception as exc:
            logger.error("LLM call failed: %s", exc)
            return ""

    def validate(self, target: str) -> ValidationResult:
        from pathlib import Path

        target_path = Path(target)
        if not target_path.exists():
            return ValidationResult(valid=False, check_name="llm_fix", evidence="", error="Target not found")
        try:
            content = target_path.read_text(encoding="utf-8")
            compile(content, target, "exec")
            is_clean, _ = self._secret_guard.scan(content)
            if not is_clean:
                return ValidationResult(
                    valid=False, check_name="llm_fix", evidence="Secret leak detected", error="Secret leak in output"
                )
            return ValidationResult(valid=True, check_name="llm_fix", evidence="Syntax check passed, no secrets")
        except SyntaxError as exc:
            return ValidationResult(valid=False, check_name="llm_fix", evidence="", error=f"Syntax error: {exc}")

    def rollback(self, target: str) -> bool:
        return False
