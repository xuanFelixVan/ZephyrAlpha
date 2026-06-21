---
module_id: KE-2852----9-000
status: active
title: PIPELINE_COMPLETE 事件→9个下游联动
category: module_blueprint
---

# PIPELINE_COMPLETE 事件→9个下游联动

PIPELINE_COMPLETE 事件→9个下游联动

Pipeline 完成 dispatch 后 emit PIPELINE_COMPLETE 事件，触发：
1. Orchestrator.assign_session()
2. FeedbackLoopEngine(B10 MOD-INF-010)接收反馈
3. CapacityAssurance(MOD-INF-001)更新Token Budget
4. SessionContinuity保存session状态
5. DeadLetterQueue检查是否需要replay
6. CostTracker累计成本
7. Descheduler扫描是否需要重调度
8. Notification System(B515)发送通知
9. AuditTrail(B101)写入决策日志
