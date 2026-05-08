---
module_id: KE-governance-beta_exit_criteria-003
title: beta exit_criteria
category: governance
---

# beta exit_criteria

beta exit_criteria

| ID | 描述 | 校验方式 |
|----|------|---------|
| EXIT-3-01 | 至少一个服务（VMS / Orc）已切到 Remote* 实现，原 Protocol 不变 | `pytest tests/integration/remote/` |
| EXIT-3-02 | HTTP / NATS 通信层的重试 + 超时 + 熔断配置就位 | 混沌测试 |
| EXIT-3-03 | 端到端性能回归测试通过（稳态延迟不劣化 > 20%）| 性能基准测试 |
