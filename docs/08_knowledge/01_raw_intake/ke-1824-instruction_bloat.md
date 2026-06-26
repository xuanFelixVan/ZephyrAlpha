---
module_id: KE-1733--------instruction-bloat--003
status: active
title: 2.18 指令膨胀检测（Instruction Bloat Detector）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.18 指令膨胀检测（Instruction Bloat Detector）

2.18 指令膨胀检测（Instruction Bloat Detector）

> **决策 D-024-16（🆕 v0.5.0）**：Boris Cherny 400 小时 Claude 使用分析——14% 的 token 浪费来自膨胀的 CLAUDE.md/AI 指令文件。我们的 Context Waste Detector (§2.17) 追踪 "sent vs referenced"，但指令文件是被动的——它总是被发送但永远不会被"引用"，仅跟踪 referenced 比例会误报。

```yaml
instruction_bloat_detector:
  description: "专门检测 AGENTS.md/CLAUDE.md/system_prompt 等指令文件的膨胀——这些文件每个 turn 都被发送，膨胀的边际成本极大"
  targets:
    - "AGENTS.md"
    - "budget_policy.yaml"
    - "所有 *blueprint.md 的 §1-§2（设计理念部分）"
  metrics:
    - "instruction_token_count"
    - "instruction_growth_rate_weekly"      # 每周增长率（超过 20% 告警）
    - "per_turn_instruction_overhead"       # 每轮的平均指令 token 开销
  alerts:
    instruction_oversized: "instruction_token_count > session_budget × 0.25"
    instruction_growing: "growth_rate_weekly > 20% → WARN '指令文件正在膨胀——建议精简冗余规则'"
    instruction_dominance: "per_turn_instruction_overhead > productive_tokens → 指令比产出还多"
  auto_compact:
    enabled: false                  # 不自动压缩（可能删除有用规则）
    suggest: "生成精简建议——检测哪个段落过去 30 天没被遵守过 → 建议删除"
  visual: "终端显示 '📋 指令: 3.2K (占预算 8%) | 本周增长 +5%'"
```
