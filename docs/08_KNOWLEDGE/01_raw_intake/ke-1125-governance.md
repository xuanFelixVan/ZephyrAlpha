---
module_id: KE-1040
status: active
title: 9. 接口文档要求
category: governance
ttl: permanent
---

# 9. 接口文档要求

9. 接口文档要求

每个接口契约必须附带以下文档：

- 接口用途说明（一段话）
- 请求/响应示例
- 错误码清单
- 性能约束（P0 模块必填：**延迟 p99 与吞吐下限 MUST 在契约进入 `frozen` 之前**，由 Owner 写入 module-registry / cross-layer-contracts（或蓝图 SLA 小节）中的 SLA 字段；本策略正文不复制具体毫秒值或 qps。非 P0 选填）
- 调用频率限制（P0 模块必填；非 P0 选填）
