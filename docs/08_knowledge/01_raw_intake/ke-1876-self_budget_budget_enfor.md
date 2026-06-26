---
module_id: KE-1785
status: active
title: 2.21 Self-Budget——Budget Enforcer 自身运营成本管控
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.21 Self-Budget——Budget Enforcer 自身运营成本管控

2.21 Self-Budget——Budget Enforcer 自身运营成本管控

> **决策 D-024-19（🆕 v0.6.0）**：SUPERVISORAGENT (ICLR 2026) 引入 LLM-free 自适应触发——传统 guards 自身消耗 token 来评估 token 消耗，形成悖论。Budget Enforcer 自身的运作成本（Output Quality Gate 的 LLM 调用、Instruction Bloat 的语义分析、Conversation Tax 的引用追踪）必须被预算。

```yaml
self_budget:
  description: "Budget Enforcer 不是免费的——自身 guards/detectors/analyzers 消耗的 token 需要独立上限"
  # SUPERVISORAGENT 原则：guards 应该是 LLM-free 的 trigger，仅在必要时升级到 LLM evaluation
  daily_cap: 50000                # Budget Enforcer 自身每日 token 上限

  components:
    # ── LLM-Free triggers（零成本，应优先使用）──
    llm_free:
      - "format_check (regex-based)"
      - "action_history.dedup_rules (hash-based)"
      - "timeout_guard (timer-based)"
      - "context_waste_detector.sent_count (non-LLM)"
      - "burn_rate_monitor (EMA-based)"

    # ── LLM-Dependent triggers（有成本，需配额控制）──
    llm_dependent:
      - name: "output_quality_gate.relevance_check"
        model: "tier_0_free"      # 强制用免费模型
        cap_per_call: 500
      - name: "output_quality_gate.hallucination_check"
        model: "tier_0_free"
        cap_per_call: 1000
      - name: "instruction_bloat_detector.auto_compact_suggest"
        model: "tier_0_free"
        cap_per_day: 2000
      - name: "conversation_tax_detector.reference_analysis"
        model: "tier_0_free"
        cap_per_day: 1500

  guard_efficiency:
    description: "Guards 的收益-成本比——如果 guard 自身消耗超过它节省的 token，关闭该 guard"
    metric: "tokens_saved_by_guard / tokens_consumed_by_guard"
    auto_disable_threshold: "< 0.5"  # guard 每花 2 token 才省 1 token → 关闭
    weekly_efficiency_report: true

  self_budget_exceeded:
    action: "HALT——所有 LLM-dependent guards 降级为 LLM-free 模式仅 warn 不 block"
    visual: "终端显示 '🛡 Self-Budget: 18K/50K (36%) | Guard 效率: 1:4.2 (省 budget:guard cost)'"
```
