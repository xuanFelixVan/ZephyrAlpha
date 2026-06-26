---
module_id: KE-4235
title: 9.1 四级限流体系
category: module_blueprint
ttl: permanent
---

# 9.1 四级限流体系

9.1 四级限流体系

| 级别 | 维度 | 默认值 | 配置文件 |
|------|------|--------|---------|
| **Level 1: Per-request** | 单次请求最大 token | input: 32K / output: 4K / tool_calls: 10 | `config/capacity/token_budget.yaml` |
| **Level 2: Per-session** | 单 session token 预算 | 50K tokens / 5 iterations | `config/context-rules.yaml`（已有） |
| **Level 3: Per-org** | 每日 token 总量 | 5M tokens / $10/day | `config/capacity/token_budget.yaml` |
| **Level 4: Global** | 全局 token 上限 | 50M tokens / $100/day | `config/capacity/token_budget.yaml` |
