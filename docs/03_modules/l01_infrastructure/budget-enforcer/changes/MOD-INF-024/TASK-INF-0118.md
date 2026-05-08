---
task_id: "TASK-INF-0118"
module_id: "MOD-INF-024"
title: "Conversation History Tax Detector — 对话历史加权衰减 + 有效引用率（§2.19 + D-024-17）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: beta
blueprint_section: "§2.19"
estimated_tokens: 3500
estimated_time_minutes: 90
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0102"
  - "TASK-INF-0116"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\conversation_tax_detector.py"
acceptance_criteria:
  - "AC-01: ConversationHistoryTaxDetector 三大追踪：total_history_tokens_sent, history_tokens_referenced, history_tax_ratio"
  - "AC-02: history_tax_ratio > 5× → 5 倍浪费 → WARN + 建议 /compact-aggressive（仅保留最近 3 轮关键摘要）"
  - "AC-03: decay_model——加权衰减：last_3_turns(1.0), turns_4_10(0.3—仅决策+异常), turns_11_plus(0.05—仅摘要)"
  - "AC-04: synergy——联动 Context Engine DocCompressor 加权衰减策略"
  - "AC-05: decay model 权重可配置——来自 budget_policy.yaml conversation_tax 段"
  - "AC-06: 终端显示 '📜 历史: 12K/15K (80%) | 有效引用: 仅 22%'"
  - "AC-07: 自适应权重——基于有效引用率动态调整 decay 权重（self_calibrating phase）"
  - "AC-08: 写入 history_tax audit events——含 window, total_sent, referenced, tax_ratio"
rollback_instructions: "删除 conversation_tax_detector.py。系统退化为均匀历史压缩——所有历史轮次等权重保留（C 等权压缩 + Boris Cherny 13% waste benchmark）"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L956-L977 (§2.19 Conversation Tax)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [conversation-tax, history-decay, weighted-compression, cherny-benchmark, beta]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0118: Conversation History Tax Detector — 对话历史加权衰减

## 1. 任务目标

实现对话历史赋税检测——对话历史每次被发送但不一定被当前 turn 使用。Boris Cherny 数据：13% token 浪费来自对话历史重读。加权衰减模型（越远的 turn 权重越低）联动 Context Engine 优化上下文质量。

## 2. 背景

蓝图 §2.19（决策 D-024-17，v0.5.0 新增）：Context Engine DocCompressor 解决"大小"但没解决"价值"——压缩后的历史 tokens 可能 80% 对当前任务无价值。此组件追踪 sent vs referenced 比率。

## 3. 实施步骤

```python
class ConversationTaxDetector:
    def __init__(self, policy: dict):
        self.weights = ConversationDecayWeights(
            last_3_turns=1.0, turns_4_10=0.3, turns_11_plus=0.05
        )

    def analyze(self, history: list[ConversationTurn],
                current_response: str) -> HistoryTaxReport:
        total_sent = sum(t.token_count for t in history)
        referenced = self._find_turn_refs(current_response, history)
        tax_ratio = total_sent / max(referenced, 1)
        return HistoryTaxReport(total_sent, referenced, tax_ratio)

    def apply_decay(self, history: list[ConversationTurn]) -> list[ConversationTurn]:
        # 按 turn 距离应用衰减权重
        # 返回 decayed_history（标记哪些 turn 可省略）
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/conversation_tax_detector.py` | 新建 |
