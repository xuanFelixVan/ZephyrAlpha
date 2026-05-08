---
module_id: KE-session_lo-context-engine-interface_md__3-003
title: 由 context-engine-interface.md §3.5 约束
category: session_log
---

# 由 context-engine-interface.md §3.5 约束

由 context-engine-interface.md §3.5 约束
class ContextEngineProtocol(Protocol):
    async def save_session_carryover(self,
                                      session_id: str,
                                      reason: EndedReason) -> None: ...

    async def load_session_carryover(self) -> SessionCarryover | None: ...

    async def clear_session_carryover(self) -> None: ...
```
