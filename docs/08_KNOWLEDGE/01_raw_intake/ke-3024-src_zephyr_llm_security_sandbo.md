---
module_id: KE-2924
status: active
title: src/zephyr/llm-security/sandbox/code_exec_sandbox.py
category: module_blueprint
ttl: permanent
---

# src/zephyr/llm-security/sandbox/code_exec_sandbox.py

src/zephyr/llm-security/sandbox/code_exec_sandbox.py

class CodeExecSandbox:
    """代码执行沙箱——整合原 L2 ProcessSandbox + 新增代码隔离执行。"""

    def __init__(self, backend: str = "docker"):
        self._backend = backend  # docker | wasi | subprocess_only
        self._process_sandbox = L2aSandbox()  # 现有进程沙箱实例

    def execute(self, code: str, language: str, timeout: float = 60.0) -> ExecResult:
        """在隔离环境中执行代码。

        执行映射：
        - Python → Docker python:3.12-slim（隔离执行，禁止网络）
        - Shell → ProcessSandbox（路径白名单 + 命令白名单）
        - SQL → 仅允许 SELECT（参数化查询，禁止 DDL/DML）
        - JS/TS → WebAssembly/WASI 运行时
        """

    def execute_shell(self, cmd: list[str], **kwargs) -> SandboxResult:
        """委托给现有 L2aSandbox 的进程沙箱执行。

        （原 L2 ProcessSandbox 的功能在此保留）
        """
```
