---
module_id: KE-341
status: active
title: 4.3 安全编排点
category: documentation
---

# 4.3 安全编排点

4.3 安全编排点

```
Cursor / Trae / Claude Desktop
         │  MCP 协议调用
         ▼
┌────────────────────────────────────┐
│   LSG L1  Input Classifier        │◀─── 阻止 Prompt Injection（OWASP LLM01）
│   [ Pattern + 启发式 + 正则 ]     │
└───────────┬────────────────────────┘
            ▼
┌────────────────────────────────────┐
│   LSG L2  System Prompt Isolator   │◀─── 防止用户指令提升权限
│   [ 双层 Prompt + 分隔符 ]        │
└───────────┬────────────────────────┘
            ▼
         LLM Call
            │
            ▼
┌────────────────────────────────────┐
│   LSG L3  Output Validator         │◀─── Schema + Secret Scan（OWASP LLM02/06）
│   [ Pydantic + Regex 敏感词扫描 ]  │
└───────────┬────────────────────────┘
            ▼
┌────────────────────────────────────┐
│   LSG L4  Pattern Auditor          │◀─── 累积异常模式检测
│   [ 滑动窗口 + EMA 异常分 ]        │
└───────────┬────────────────────────┘
            ▼
    Agent Orchestrator / Context Engine 消费
```
