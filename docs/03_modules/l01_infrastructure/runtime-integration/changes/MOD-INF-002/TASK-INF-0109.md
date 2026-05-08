---
task_id: "TASK-INF-0109"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §2.1-F 1人+AI运维深度强化 B4-F01~F10 + §6.5 深度运维场景 + §6.3 容量模型"
title: "盲点关闭——F.1人+AI深度运维 B4-F01~F10：认知负荷/晨报/睡眠协议/自动决策/紧急唤醒/周报/消失演练/知识外化/入职自生成/心理健康防护"
description: |
  关闭运维深度盲点 B4-F01~F10——"Owner是人会累会忘会犯错"的设计。
  B4-F01 认知负荷预算→C_max模型（告警×3+审批×2+架构×4~5+手动×3），C_today>0.8→轻负载日+
  B4-F02 晨报推送→Daily Briefing Markdown报告（昨日关键指标+费用+自愈记录+待决策项）+
  B4-F03 睡眠时段协议→§5.3 SleepTimeProtocol 代码骨架实现（23:00-07:00静音；CRITICAL仅1次+5min→自愈）+
  B4-F04 自动决策阈值→§5.3 AutoDecideEngine 代码骨架：影响≤3模块+费用≤$0.10+RPN≤50→自动执行+
  B4-F05 紧急唤醒判定→精确定义：核心回路DOWN+3次自愈失败+影响≥L04/L05/L06任一层+
  B4-F06 周报→Weekly Report Markdown+飞书推送+自动存KB+
  B4-F07 Owner消失演练→每月1次6h全自动运行+验证0依赖+
  B4-F08 知识外化→Owner决策偏好→系统规则自动执行+
  B4-F09 入职自生成→系统自文档化→30min理解系统+
  B4-F10 弃用螺旋防护→72h无介入→降频30%+升高自愈阈值。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\sleep_time_protocol.py"
    description: "SleepTimeProtocol——§5.3代码骨架实现：睡眠时段判断+告警静音策略+CRITICAL单次触发"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\auto_decide_engine.py"
    description: "AutoDecideEngine——§5.3代码骨架实现：三阈值(模块数/费用/RPN)→自动决策"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\cognitive_load_tracker.py"
    description: "CognitiveLoadTracker——Owner认知负荷C_max模型+超载保护"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\daily_briefing.py"
    description: "DailyBriefing——晨报生成+周报生成+飞书推送+KB存储"
  - path: "D:\\ZephyrAlpha\\config\\owner_notification_tiers.yaml"
    description: "Owner告警预算N=10/通知分层/休假模式激活码（与TASK-INF-0105共用）"
  - path: "D:\\ZephyrAlpha\\tests\\l01_infrastructure\\test_sleep_time_protocol.py"
    description: "睡眠时段协议单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\l01_infrastructure\\test_auto_decide.py"
    description: "自动决策引擎单元测试"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\sleep_time_protocol.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\auto_decide_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\cognitive_load_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\daily_briefing.py"
  - "D:\\ZephyrAlpha\\config\\owner_notification_tiers.yaml"
  - "D:\\ZephyrAlpha\\tests\\l01_infrastructure\\test_sleep_time_protocol.py"
  - "D:\\ZephyrAlpha\\tests\\l01_infrastructure\\test_auto_decide.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
applicable_rules:
  - module_id: "MOD-INF-002"
    section: "§5.3 SleepTimeProtocol 代码骨架"
    reason: "is_sleep_time() + handle_alert() 三策略: SEND_SINGLE / AUTO_HEAL / QUEUE_FOR_MORNING"
  - module_id: "MOD-INF-002"
    section: "§5.3 AutoDecideEngine 代码骨架"
    reason: "三维阈值 AND 满足=自动执行 | OR 不满足=送审批"
  - module_id: "MOD-INF-002"
    section: "§6.5"
    reason: "9大运维场景矩阵——睡眠保护/晨报/决策疲劳/紧急唤醒/Owner消失演练/知识外化/弃用螺旋/自我解释/周报"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "§2.1-F 10项盲点 + §5.3 SleepTimeProtocol/AutoDecideEngine 代码骨架 + §6.3/§6.5 容量模型"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 30000
timeout_minutes: 90
acceptance_criteria:
  - "SleepTimeProtocol: 23:00-07:00 时段 CRITICAL 仅触发1次→5min无响应→AUTO_HEAL（B4-F03）"
  - "AutoDecideEngine: 三阈值 AND 满足→auto_approved=True；OR 不满足→needs_approval（B4-F04）"
  - "CognitiveLoadTracker: C_today > 0.8×C_max→轻负载日；> C_max→认知超载保护（B4-F01）"
  - "DailyBriefing: 07:00 自动生成晨报→飞书推送 Markdown（B4-F02）"
  - "周报: 每周日自动生成 SLO/费用/健康/AI施工统计（B4-F06）"
  - "紧急唤醒: 仅核心回路DOWN+3次自愈失败+影响L04/L05/L06时触发（B4-F05）"
  - "弃用螺旋防护: 72h 无介入→降频 30%（B4-F10）"
rollback_instructions: |
  1. 删除 l01_infrastructure/ 下新增文件：sleep_time_protocol.py / auto_decide_engine.py / cognitive_load_tracker.py / daily_briefing.py
  2. 删除新增测试文件
  3. config/owner_notification_tiers.yaml 若与其他任务冲突→保留（由 TASK-INF-0105 管理）
  4. 如 l01_infrastructure/ 目录仅剩这些文件→删除目录
depends_on:
  - "TASK-INF-0105"
blocked_by: []
status: "created"
tags_fn:
  - "infra"
  - "observability"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-002"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
