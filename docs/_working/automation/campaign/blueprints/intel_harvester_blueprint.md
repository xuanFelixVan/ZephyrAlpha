---
ttl: task_bound
completes_when: 模块晋升 docs/03_modules（H-01 解冻）或工单废弃
---

# MOD-AUTO-L3-001（暂编号）intel_harvester 蓝图

## 定位

AI 层"胃"的地基件（业务层代建，迭代归 AI 层——对话⑥三层定案）。全网情报→关键词过滤→本地 LLM 摘要→收件箱。**只搜不自动入册**（Owner 红线）。

## ALGO_FLOW

- I1: arXiv q-fin 官方 API（免 key，20 条/班）
- A1: 关键词过滤（factor/momentum/regime/LLM agent/overfitting 等）
- A2: OllamaChat 摘要（qwen3:8b，内嵌 LSG；不可达降级原文）
- O1: docs/_working/automation/inbox/intel-YYYYMMDD.md

## 消费方

业务层⑥号车道（策略线索）、治理层（门禁章法检索）、AI 层（设备自省）——胃只有一个，三层点菜。

## 扩展位（AI 层接手后）

RSSHub 本地源、GitHub trending、会议论文榜、X/推特列表——源注册表化。
