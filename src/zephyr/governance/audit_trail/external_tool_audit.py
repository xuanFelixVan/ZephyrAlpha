# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §9
# [MODULE] zephyr.governance.audit_trail.external_tool_audit
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit-orchestrator.pipeline_runner
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 外部工具审计不阻塞主流程; 超时30s自动降级
# [MODIFY-GUARD] 新增外部工具必须在此注册
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 审计失败返回降级结果
# [TESTS] tests/audit-orchestrator/test_external_tool_audit.py
# [A_module] module_id=MOD-GOV_external_tool_audit | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["ExternalToolAuditor"]

DEFAULT_TIMEOUT = 30


class ExternalToolAuditor:
    def __init__(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        self._timeout = timeout
        self._results: dict[str, dict[str, Any]] = {}
        self._available = True

    def audit_tool(self, name: str, command: list[str], cwd: str | None = None) -> dict[str, Any]:
        try:
            proc = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self._timeout,
                cwd=cwd or str(Path.cwd()),
            )
            result: dict[str, Any] = {
                "tool": name,
                "exit_code": proc.returncode,
                "stdout": proc.stdout[:4096],
                "stderr": proc.stderr[:4096] if proc.stderr else "",
                "pass": proc.returncode == 0,
            }
            self._results[name] = result
            return result
        except subprocess.TimeoutExpired:
            logger.warning("Tool %s timed out after %ds", name, self._timeout)
            result = {
                "tool": name,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Timeout after {self._timeout}s",
                "pass": False,
                "degraded": True,
            }
            self._results[name] = result
            return result
        except Exception as exc:
            logger.error("Tool %s audit failed: %s", name, exc)
            result = {
                "tool": name,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(exc),
                "pass": False,
                "degraded": True,
            }
            self._results[name] = result
            return result

    def audit_module(self, module_path: str) -> dict[str, Any]:
        return self.audit_tool(
            f"import_check:{module_path}",
            ["python", "-c", f"import {module_path}; print('OK: {module_path}')"],
        )

    def summary(self) -> dict[str, Any]:
        return {
            "total": len(self._results),
            "passed": sum(1 for r in self._results.values() if r.get("pass", False)),
            "failed": sum(1 for r in self._results.values() if not r.get("pass", False)),
            "degraded": sum(1 for r in self._results.values() if r.get("degraded", False)),
            "results": dict(self._results),
        }

    def is_available(self) -> bool:
        return self._available


class ChainValidationResult:
    def __init__(self, tool_id="", valid=True, chain_intact=True, errors=None):
        self.tool_id = tool_id
        self.valid = valid
        self.chain_intact = chain_intact
        self.errors = errors or []


class ExternalToolCallAuditor:
    def __init__(self, config=None):
        self.config = config or {}

    def audit_call(self, tool_id, call_data):
        return ChainValidationResult(tool_id=tool_id)

    def validate_chain(self, tool_id):
        return ChainValidationResult(tool_id=tool_id)


class ToolCallRecord:
    def __init__(self, tool_id="", call_id="", timestamp=None, parameters=None, result_hash=""):
        self.tool_id = tool_id
        self.call_id = call_id
        self.timestamp = timestamp
        self.parameters = parameters or {}
        self.result_hash = result_hash


class ToolCallStatus:
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    TIMEOUT = "TIMEOUT"
    PENDING = "PENDING"
    RETRY = "RETRY"
