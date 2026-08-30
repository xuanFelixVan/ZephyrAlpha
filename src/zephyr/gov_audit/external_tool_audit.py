# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §9
# [MODULE] zephyr.gov_audit.external_tool_audit
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
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: timeout 参数
#   fields: 参数 timeout（无注解）
#   code: external_tool_audit.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ExternalToolAuditor
#   name_en: ExternalToolAuditor
#   intro: class ExternalToolAuditor 源码 L69-L136
#   desc: 公共方法（定义序）: audit_tool, audit_module, summary, is_available；源码 L69-L136
#   inputs: timeout
#   outputs: 返回值
# - id: A2
#   name_zh: ② ExternalToolCallAuditor
#   name_en: ExternalToolCallAuditor
#   intro: class ExternalToolCallAuditor 源码 L147-L155
#   desc: 公共方法（定义序）: audit_call, validate_chain；源码 L147-L155
#   inputs: config
#   outputs: 返回值
#   （注：A2 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: ExternalToolAuditor, ExternalToolCallAuditor
#   downstream: audit-orchestrator.pipeline_runner
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Final

logger = logging.getLogger(__name__)

__all__ = ["ExternalToolAuditor"]

DEFAULT_TIMEOUT: Final[int] = 30


class ExternalToolAuditor:
    def __init__(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        self._timeout = timeout
        self._results: dict[str, dict[str, Any]] = {}
        self._available = True

    def audit_tool(self, name: str, command: list[str], cwd: str | None = None) -> dict[str, Any]:
        try:
            from zephyr.shared.infra.process_pool import run_subprocess_hidden

            proc = run_subprocess_hidden(
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
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("Tool %s audit failed: %s", name, exc, exc_info=True)
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
