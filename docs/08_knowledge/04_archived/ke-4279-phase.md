---
module_id: KE-4120-----phase-000
title: 5. 施工 Phase 规划
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 5. 施工 Phase 规划

5. 施工 Phase 规划

| Phase | 任务 | 状态 | 产出 |
|:---:|------|:---:|------|
| sandbox | 🆕 v0.5.0：三维 Budget Policy Sandbox（dry-run 4场景含 Time Budget 验证）+ Policy Versioning + 自修复螺旋检测沙盘 | 📋 Backlog | 策略三维验证全覆盖 |
| scaffold | BudgetTracker（五级三维含Self-Budget）+ BudgetPolicy YAML + Pre-flight Gate（三维+长上下文+Self-Budget check）+ Action History with Dedup + Stream Abort Guard 骨架 + Timeout Guard + Spiral EWS 骨架 | 📋 Backlog | 全生命周期+三维+Self-Budget 核心可运行 |
| experimental | Model Router（多Provider least-cost + Batch + Provider Tier感知+长上下文溢价+Think-time路由）+ Degradation Manager（六级+Narrow/Reroute/Timeout+回升）+ Semantic Cache + 价格同步 + ENV Profile Manager + Poison Cascade Detector 骨架 | 📋 Backlog | 完整的降级+路由+安全+环境适配 |
| beta | Cost Attributor（含Outcome/Judge/Parent-Child）+ ROI Calculator + Weekly Auto-Summary + Burn Rate面板 + Context Waste Detector + Instruction Bloat Detector + Conversation Tax Detector + Guard Efficiency Report | 📋 Backlog | 全量归因+检测+审计+Self-Budget |
| stable | 自学习阈值 + Anti-Spiral 验证 + 自修复螺旋检测 + Budget Savings 储蓄验证 + 新模型发现 + Budget Policy Sandbox 全场景验证 | 📋 Backlog | Solo maintainer 全能力验证 |
| self_calibrating | 计划 vs 实际三维偏差校准 + 模型路由质量反馈闭环 + Distribution Shift + 对话历史税自适应权重 + 指令膨胀持续监控 | 📋 Backlog | 自适应进化 |

---
