---
module_id: KE-module_blu-src_zephyr_context_engine_prot-003
title: src/zephyr/context_engine/protocol.py (experimental 产出)
category: module_blueprint
---

# src/zephyr/context_engine/protocol.py (experimental 产出)

src/zephyr/context_engine/protocol.py (experimental 产出)

from typing import Protocol, Literal

class ContextEngineProtocol(Protocol):
    """业务层永远依赖此 Protocol。"""

    async def build(self, request: ContextRequest) -> ContextBundle: ...
    async def compress(self, bundle: ContextBundle, token_budget: int) -> ContextBundle: ...
    async def validate(self, bundle: ContextBundle) -> ValidationReport: ...
    async def inject(self, bundle: ContextBundle, channel: IDEChannel) -> InjectResult: ...

    # 反馈通道（遗漏 #5）—— Feedback Loop Engine 用 FeedbackAction Protocol 调用此接口
    async def adjust_strategy(self, task_id: str, signal: FeedbackSignal) -> AdjustResult: ...

    # 辅助
    async def probe_ide_capabilities(self, ide_id: str) -> IDECapabilities: ...
    async def stats(self) -> CEStats: ...

class InProcessContextEngine:
    """experimental（当前目标）：进程内调用，直接依赖 VectorMemoryProtocol + NetworkX。"""

class RemoteContextEngine:
    """beta+（按需启用）：HTTP/gRPC Client。"""
```

| Phase | 实施形态 | 运行方式 | 触发升级条件 |
|:-:|---------|---------|-------------|
| **experimental** | **`InProcessContextEngine`（Python 库，当前目标）** | `from zephyr.context_engine import get_ce` | - |
| beta | `RemoteContextEngine`（HTTP 服务） | `POST /v1/*` FastAPI | ≥1 触发：① 多 IDE 实例并发 build ≥ 3；② entity-graph > 10k 节点不宜多进程加载 |
| stable | gRPC | 按需 | RPS > 200 |

**所有 API 均为 `async`**。进程内锁用 `asyncio.Lock`（事件循环友好），跨进程锁用 `filelock.FileLock`。**严禁 `threading.Lock`**。

---
