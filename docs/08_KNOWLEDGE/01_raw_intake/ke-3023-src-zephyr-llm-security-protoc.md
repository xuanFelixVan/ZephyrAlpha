---
module_id: KE-2923
status: active
title: src/zephyr/llm-security/protocol.py (experimental 产出)
category: module_blueprint
---

# src/zephyr/llm-security/protocol.py (experimental 产出)

src/zephyr/llm-security/protocol.py (experimental 产出)

from typing import Protocol

class LLMSecurityGatewayProtocol(Protocol):
    async def validate_input(self, payload: InputPayload) -> InputVerdict: ...
    async def validate_output(self, payload: OutputPayload, schema_id: str) -> OutputVerdict: ...
    async def scan_secrets(self, text: str, context: str = "generic") -> SecretScanResult: ...
    async def inspect_patterns(self, text: str, profile: str = "default") -> PatternScanResult: ...
    async def bump_strictness(self, delta: float, ttl_minutes: int, reason: str) -> None: ...
    async def get_strictness(self) -> StrictnessSnapshot: ...
    async def stats(self) -> LSGStats: ...

class InProcessLLMSecurityGateway:
    """experimental（当前目标）：进程内调用，规则 + Pydantic。"""

class RemoteLLMSecurityGateway:
    """beta+（按需启用）：独立 HTTP 服务，便于多进程共享策略。"""
```

| Phase | 实施形态 | 运行方式 | 触发升级条件 |
|:-:|---------|---------|-------------|
| **experimental** | **`InProcessLLMSecurityGateway`（Python 库）** | 进程内异步调用 | - |
| beta | `RemoteLLMSecurityGateway`（HTTP 服务） | FastAPI | 多进程共享策略 / 集中审计日志 |
| stable | gRPC + 策略中心 | 服务化 | 多环境统一策略 |

**所有 API 均为 `async`**。进程内锁 `asyncio.Lock`，跨进程锁 `filelock.FileLock`。**严禁 `threading.Lock`**。

---
