---
module_id: KE-2236----api-003
status: active
title: 4.3 沙箱 API
category: module_blueprint
---

# 4.3 沙箱 API

4.3 沙箱 API

```python
    async def provision_sandbox(
        self,
        task_id: str,
        policy: SandboxPolicy,
    ) -> Sandbox:
        """
        为任务创建沙箱。
        Windows 默认：
          - repo 整体只读挂载
          - writable_paths 白名单创建可写 overlay 目录
          - network_access='none' 通过防火墙规则隔离
        超时自动销毁（配 expires_at）。
        """

    async def destroy_sandbox(self, sandbox_id: str) -> None: ...

    async def verify_sandbox_violation(
        self,
        sandbox_id: str,
    ) -> list[SandboxViolation]:
        """
        检查沙箱自创建以来的越界行为（试图写白名单外路径 / 发起外部网络 等）。
        任一违规 → 任务转 HALLUCINATING，上报 FLE（signal 类型 sandbox_violation 扩展）。
        """
```
