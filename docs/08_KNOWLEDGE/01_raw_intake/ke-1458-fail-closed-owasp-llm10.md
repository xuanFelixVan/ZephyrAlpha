---
module_id: KE-1368---owasp-llm10-000
status: active
title: 10.4 fail-closed 与 OWASP LLM10 的平衡
category: module_blueprint
---

# 10.4 fail-closed 与 OWASP LLM10 的平衡

10.4 fail-closed 与 OWASP LLM10 的平衡

`LLM10 Unbounded Consumption` 要求防 DoS。LSG fail-closed 本身就是 DoS（拒绝所有），这看起来矛盾，实际：

- LSG fail-closed 是 **安全优于可用性** 的刻意选择
- 配套：健康检查每 30s 一次，`lsg_degrade.log` 主动告警，**要求运维 5 分钟内介入**
- beta+ 服务化后可以双活 LSG 实例消除 SPOF
