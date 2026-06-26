---
module_id: KE-1933--------cost-attribution-000
status: active
title: 2.7 成本归因体系（Cost Attribution）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.7 成本归因体系（Cost Attribution）

2.7 成本归因体系（Cost Attribution）

> **决策 D-024-08（v0.4.0 修订）**：不知道钱花在哪里的 Budget Enforcer 只做了一半工作。v0.4.0 新增 Outcome 维度（成功/失败/部分分离）——失败消耗和成功消耗的 ROI 完全不同。

```yaml
cost_attribution:
  dimensions:

    entity_level:
      description: "按 Agent/模块归因"
      fields:
        - "agent_id"
        - "module_id"
        - "phase"
      query_example: "agent_id='code-generator' 本月消耗 $12.50，占总成本 65%"

    tool_level:
      description: "按工具/API 归因——含第三方 API 直接调用费用"
      fields:
        - "tool_name"
        - "tool_call_count"
        - "tool_api_cost"
        - "tool_prompt_tokens"
        - "tool_result_tokens"
        - "passthrough_cost"        # v0.4.0 新增：Web Search/Code Exec/DB Query 等服务自身的费用
      query_example: "tool_name='web_search' 调用 320 次，API 费用 $1.60 + token 费用 $8.40"

    feature_level:
      description: "按产品功能/施工活动归因"
      fields:
        - "activity_type"
        - "output_files_created"
        - "lines_of_code"
      query_example: "activity_type='debug' 占本月 45% 成本——debug 效率需优化"

    # ── v0.4.0 新增：产出结果维度 ──
    outcome_level:
      description: "按 API 调用结果分离成本——成功/失败/部分/拒止"
      fields:
        - "outcome"                  # "success" | "partial" | "failed" | "rejected"
        - "retry_count"
        - "error_category"           # "rate_limit" | "timeout" | "hallucination" | "validation_fail"
      query_example: "outcome='failed' 本月消耗 $4.20，占总成本 22%——失败重试是最大浪费源"

    # ── v0.4.0 新增：LLM-as-Judge 独立核算 ──
    judge_cost:
      description: "LLM 审查 LLM 的 Judge 模式消耗——这是二次消耗，不是直接产出"
      tracking: "独立子预算——不计入 Task 预算，走 Judge 专用预算池"
      alert: "Judge 成本 > 总成本 15% → 告警 '审查成本过高，建议简化审查逻辑'"

  showback:
    description: "每周自动生成归因摘要"
    format: "自然语言 Markdown 报告 → `docs/_working/audit/cost_reports/weekly-{date}.md`"
    content:
      - "本周总消耗：X tokens / $Y"
      - "Top 3 消耗 Agent：[agent_id] $X (占比%)"
      - "Top 3 消耗工具：[tool_name] $X (占比%)"
      - "Top 3 消耗活动：[activity_type] $X (占比%)"
      - "失败消耗：$X (占比%)——含 top failure reason"
      - "本周异常：[超过预算的事件列表]"
      - "ROI 估算：[token 产出效率 vs 上周]"
      - "预测下周：[基于 4 周趋势的预测]"

  data_retention:
    description: "v0.4.0 新增——成本数据不会无限增长"
    raw_data: "30 天保留（JSONL）"
    aggregated: "12 个月保留（按周聚合 SQLite）"
    archival: "每年自动归档上一年度数据为 gzip JSON"
    cleanup: "每周日 03:00 UTC 自动执行过期策略"

  storage: "JSONL——data/audit/cost-attribution.jsonl（按天切分）"
```
