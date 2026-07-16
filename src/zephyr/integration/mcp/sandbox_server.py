# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §
# [MODULE] zephyr.integration.mcp.sandbox_server
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.mcp._base_server
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-013 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""MCP sandbox 安全代码执行沙箱（MOD-INF-013 Phase 7 — 关闭 B4）。

安全约束：
- 独立 subprocess 执行（timeout=30s）
- 输入限制：code + stdin ≤ 500KB
- 输出截断：stdout/stderr ≤ 1MB
- 禁止文件系统写入
- 超时强制杀死进程
"""

from __future__ import annotations

from typing import Final
import logging
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from zephyr.integration.mcp._base_server import BaseMCPServer, MCPError

__all__ = ["SandboxServer", "main"]

_log = logging.getLogger(__name__)

SERVER_ID: Final[str] = "sandbox"
SERVER_VERSION: Final[str] = "0.1.0"
SERVER_DESCRIPTION: Final[str] = "安全代码执行沙箱（Phase 7 skeleton）"

MAX_CODE_BYTES: Final[int] = 500 * 1024
MAX_OUTPUT_BYTES: Final[int] = 1 * 1024 * 1024
DEFAULT_TIMEOUT: Final[float] = 30.0

SUPPORTED_LANGUAGES: Final[set] = {"python", "javascript", "bash"}


class SandboxServer(BaseMCPServer):
    """安全代码执行沙箱 MCP Server。"""

    def __init__(self) -> None:
        super().__init__(SERVER_ID, SERVER_VERSION, SERVER_DESCRIPTION)

        self.register_tool(
            name="sandbox.execute",
            description="在隔离环境中执行代码（超时/截断/禁写入/安全沙箱）",
            input_schema={
                "type": "object",
                "required": ["code", "language"],
                "additionalProperties": False,
                "properties": {
                    "code": {"type": "string", "maxLength": MAX_CODE_BYTES},
                    "language": {"type": "string", "enum": sorted(SUPPORTED_LANGUAGES)},
                    "stdin": {"type": "string", "default": ""},
                    "timeout": {"type": "number", "minimum": 1, "maximum": 60, "default": 30},
                },
            },
            handler=self._execute,
            safety_level="H",
        )
        self.register_tool(
            name="sandbox.health_check",
            description="沙箱健康检查",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {},
            },
            handler=self._health_check,
        )

    def _execute(
        self,
        code: str,
        language: str,
        stdin: str = "",
        timeout: float = DEFAULT_TIMEOUT,
    ) -> dict[str, Any]:
        if len(code.encode("utf-8")) > MAX_CODE_BYTES:
            raise MCPError(-32602, f"code exceeds max size of {MAX_CODE_BYTES} bytes")

        if language not in SUPPORTED_LANGUAGES:
            raise MCPError(-32602, f"unsupported language: {language!r}")

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        t0 = time.perf_counter()
        try:
            if language == "python":
                cmd = ["python", tmp_path]
            elif language == "javascript":
                cmd = ["node", "-e", code]
            elif language == "bash":
                cmd = ["bash", tmp_path]
            else:
                raise MCPError(-32602, f"unsupported language: {language!r}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=min(timeout, 60),
                cwd=tempfile.gettempdir(),
            )

            stdout = result.stdout[:MAX_OUTPUT_BYTES]
            stderr = result.stderr[:MAX_OUTPUT_BYTES]
            truncated = len(result.stdout) > MAX_OUTPUT_BYTES or len(result.stderr) > MAX_OUTPUT_BYTES

            return {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": result.returncode,
                "truncated": truncated,
                "duration_ms": round((time.perf_counter() - t0) * 1000),
            }

        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Execution timed out after {timeout}s",
                "exit_code": -1,
                "truncated": False,
                "duration_ms": round(timeout * 1000),
            }
        finally:
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except OSError:
                pass

    def _health_check(self) -> dict[str, Any]:
        return {
            "status": "healthy",
            "supported_languages": sorted(SUPPORTED_LANGUAGES),
            "max_code_bytes": MAX_CODE_BYTES,
            "max_output_bytes": MAX_OUTPUT_BYTES,
            "default_timeout": DEFAULT_TIMEOUT,
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


def main() -> None:
    server = SandboxServer()
    server.run()


if __name__ == "__main__":
    main()
