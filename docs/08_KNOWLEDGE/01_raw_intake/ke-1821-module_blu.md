---
module_id: KE-1730
status: active
title: 2.17 辅助能力——上下文浪费检测 + 冷启动豁免 + 自托管模型成本模型
category: module_blueprint
ttl: permanent
---

# 2.17 辅助能力——上下文浪费检测 + 冷启动豁免 + 自托管模型成本模型

2.17 辅助能力——上下文浪费检测 + 冷启动豁免 + 自托管模型成本模型

> **决策 D-024-15（🆕 v0.4.0）**：补充三个之前被忽略的辅助能力——它们不影响核心逻辑，但在 solo maintainer 场景下持续性产生隐性成本。

```yaml
context_waste_detector:
  description: "你控制了预算上限，但不知道塞进上下文的材料里有多少是 LLM 实际没看的"
  tracking: "每次 LLM 调用后分析 response 中实际引用到的上下文片段"
  metric: "referenced_chars / total_context_chars"
  alert: "waste_ratio > 0.60 持续 5 个请求 → 建议 /compact 或精简 AGENTS.md"
  integration: "Context Engine 的 DocCompressor 根据 waste 数据优化选择策略"

cold_start_allowance:
  description: "每个 Session 初始阶段（读蓝图、索引文件、建立上下文）有固定'入场费'——不应计入任务预算"
  fixed_cost:
    - step: "读取 AGENTS.md + 核心蓝图"
      estimated_tokens: 3000
    - step: "建立 workspace index"
      estimated_tokens: 2000
    - step: "加载 budget_policy.yaml"
      estimated_tokens: 500
  total_cold_start: 5500             # 每个 Session 默认豁免
  accounting: "cold_start_tokens 计入 session 级预算但不计入任何任务的 task_budget"
  overridable: true                   # 复杂项目可以调整

local_model_cost_model:
  description: "蓝图假设全走 API。但如果你跑了本地模型（Ollama），'成本'怎么算？"
  cost_model:
    electricity: "$0.12/kWh"
    gpu_power: "200W"                   # 单 GPU 功耗
    tokens_per_second: 50              # 本地模型吞吐量（因模型而异）
    cost_per_1m_tokens: "electricity / (tokens_per_second × 3600) × 1,000,000 ≈ $0.13/MTok"
  accounting: "local tokens 记为 'local_cost' 而非 'api_cost'——在 showback 中分开展示"
  model_assignment: "tier_local（独立于 API Tier 体系）"
```
