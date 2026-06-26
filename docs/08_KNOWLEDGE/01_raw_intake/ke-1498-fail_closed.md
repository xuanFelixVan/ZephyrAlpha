---
module_id: KE-1408
status: active
title: 12. fail-closed 原则（贯穿全链路）
category: module_blueprint
ttl: permanent
---

# 12. fail-closed 原则（贯穿全链路）

12. fail-closed 原则（贯穿全链路）

```
LSG 健康检查失败
    │
    ├── L0 失败 → 拒绝加载未验证的模型/依赖
    ├── L1 失败 → 拒绝所有 LLM 输入（不 bypass）
    ├── L2 失败 → 拒绝构建不安全的 Prompt
    ├── L3 失败 → 拒绝所有 LLM 输出
    ├── L4 失败 → 拒绝所有 Agent 工具调用
    ├── L5 失败 → 拒绝超过预算/限制的请求
    ├── L6 失败 → 日志降级为 stderr fallback（审计不可中断）
    └── L7 失败 → 标记"验证层不可用"，不阻断主流程（L7是检测层非阻断层）
```

**例外说明**：
- L7 是持续验证层（检测+评估），其不可用不阻断主LLM流程
- L6 日志不可用时降级到 stderr——但审计数据可能丢失，触发 WARNING 告警
- 其余所有层（L0-L5）均 fail-closed——宁可误拒不可漏放
