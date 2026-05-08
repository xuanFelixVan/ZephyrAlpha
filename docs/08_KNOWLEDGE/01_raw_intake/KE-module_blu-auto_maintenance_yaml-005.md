---
module_id: KE-module_blu-auto_maintenance_yaml-005
title: auto_maintenance.yaml
category: module_blueprint
---

# auto_maintenance.yaml

auto_maintenance.yaml
auto_maintenance:
  # ─── 规则效果评估 ───
  rule_effectiveness:
    metric: "rule_effectiveness_score"
    formula: "（过去90天该规则触发的实际拦截次数）/ （规则存在天数）"
    classification:
      active: "score > 0.01（每天至少触发0.01次 = 每100天至少1次）"
      dormant: "0 < score <= 0.01（存在且配置但极少触发）"
      zombie: "score == 0（90天内从未触发——候选删除）"
    
    auto_deprecation:
      zombie_threshold_days: 90
      action: "自动标记 [DEPRECATED_CANDIDATE] + 在Owner健康仪表盘中高亮"
      owner_review: "Owner确认删除 → 规则归档（非物理删除——保留历史）"
      auto_cleanup: "Owner 14天内未审阅 → 规则自动禁用（非删除）+ 告警升级"
    
    protected_rules:  # 以下规则永不被自动deprecate，即使score=0
      - "L0 不可变核心规则"
      - "Kill Switch 触发器规则"
      - "数据外泄防护规则（read_sensitive→external_output）"

  # ─── 权限复杂度预算 ───
  complexity_budget:
    max_total_rules: 30                 # L1-L4规则总数上限（L0硬编码不计入，L5-L7不计入）
    warnings:
      - at: 20
        level: "info"
        message: "规则数达到上限的67%——建议检查是否有冗余"
      - at: 25
        level: "warning"
        message: "规则数达到上限的83%——强制触发自动化deprecation扫描"
      - at: 30
        level: "error"
        message: "规则数达到上限——禁止新增规则直到删除达到28条以下"
    
    cost_per_rule:
      avg_execution_time_us: 8.5        # 每条规则的平均检查耗时（微秒）
      complexity_budget_us: 255         # 30条 × 8.5us = 总耗时预算
      burn_rate_warning: "规则总数×平均耗时 > 预算的80% → 告警"

  # ─── 定期审计报告（每周自动生成）───
  weekly_audit_report:
    generation: "每周一 09:00 自动生成（crontab）"
    content:
      - "本周权限决策统计（ALLOW/AUTO_GUARD/BLOCKED 分布）"
      - "auto_guard 后验成功率趋势"
      - "僵尸规则清单（90天无触发）"
      - "规则复杂度预算消耗"
      - "Kill Switch 触发历史（含原因和恢复时间）"
      - "Maturity 升级/降级事件"
      - "推荐的规则清理列表"
    delivery: "写入 docs/03_modules/l01_infrastructure/agent-rbac/reports/weekly-{date}.md"

  # ─── Owner 健康仪表盘 ───
  owner_dashboard:
    description: "每次施工后自动更新的5个关键数字——Owner5秒看懂权限系统状态"
    file_path: "config/agent_rbac/health_dashboard.yaml"
    metrics:
      - metric: "today_allowed_count"
        display: "今日 ALLOW 次数"
        healthy_range: "无上限——越多越正常"
        alarm: "无（这是常态）"
        
      - metric: "today_auto_guard_count"
        display: "今日 AUTO_GUARD 次数（及后验通过率%）"
        healthy_range: "< 20次 AND 后验通过率 > 90%"
        alarm: "auto_guard > 50次 → 规则太严或Agent行为异常。后验通过率 < 80% → Agent信任度下降"
        
      - metric: "today_blocked_count"
        display: "今日 BLOCKED 次数"
        healthy_range: "< 5次"
        alarm: "> 10次 → Agent频繁触碰权限边界——可能被投毒或理解偏差"
        
      - metric: "kill_switch_status"
        display: "Kill Switch 状态 [NORMAL / WARNING / TRIGGERED / MAINTENANCE] + 最近触发时间"
        healthy_range: "NORMAL"
        alarm: "非NORMAL = 立即关注"
        
      - metric: "agent_maturity_distribution"
        display: "Agent成熟度分布 [L1:3, L2:2, L3:1, L4:0]"
        healthy_range: "L1+L2 > 50% 且 无异常跳跃"
        alarm: "L3+占比 > 30% → 高风险Agent过多"
    
    auto_generation: "每次 PermissionGuard.check() 执行后异步更新"
    visual_indicator: |
      ┌─────────────────────────────────────────────┐
      │ AGENT RBAC HEALTH DASHBOARD                  │
      ├──────────────────────────────
