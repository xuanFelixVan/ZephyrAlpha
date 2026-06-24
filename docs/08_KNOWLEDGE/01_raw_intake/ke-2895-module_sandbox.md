---
module_id: KE-2795
status: active
title: Module Sandbox（模块级进程隔离）
category: module_blueprint
---

# Module Sandbox（模块级进程隔离）

Module Sandbox（模块级进程隔离）

```python
class ModuleSandbox:
    """RI 模块间运行时隔离——每模块独立子进程。
    AI生成的代码在子进程中运行→crash/无限循环→不污染主进程。
    """
    _module_procs: dict[str, asyncio.subprocess.Process] = {}
    _crash_counter: dict[str, int] = {}  # crash 计数→自动熔断

    async fn spawn_module(self, module_id: str,
                           entrypoint: str) -> None:
        """启动模块为独立子进程——通过 stdin/stdout JSON-RPC 通信"""
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", f"zephyr.{module_id}",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        self._module_procs[module_id] = proc

    async def restart_if_crashed(self, module_id: str) -> bool:
        """检测模块进程是否存活→crash则重启→5次后永久隔离+通知Owner"""
        proc = self._module_procs.get(module_id)
        if proc and proc.returncode is not None:
            self._crash_counter[module_id] = self._crash_counter.get(module_id, 0) + 1
            if self._crash_counter[module_id] >= 5:
                await self.notify_owner(
                    f"💀 {module_id} 已连续crash 5次→已隔离，需Owner手动恢复"
                )
                return False
            await self.spawn_module(module_id, proc.entrypoint)
            return True
        return True
```
