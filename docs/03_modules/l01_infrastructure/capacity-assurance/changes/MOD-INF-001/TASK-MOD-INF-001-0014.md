---

task_id: TASK-MOD-INF-001-0014
module_id: MOD-INF-001
title: "第二轮盲点审计关闭：盲点 #17 至 #25（§21 v2.3.0 扩展——新增 M-28/29/30）"
doc_type: task_card
status: done
priority: P1
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T03:02:30+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0003
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0009
  - TASK-MOD-INF-001-0013
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
  - "D:\\ZephyrAlpha\\config\\capacity\\capacity_slo.yaml"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\context_budget_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\per_task_token_budget.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\ai_skill_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\degradation_spiral_detector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\token_value_attribution.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\owner_health_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\trace_capacity_injector.py"
acceptance_criteria:
  - "#17 Context 预算慢泄漏: ContextBudgetGuard + SLI CAP-CTX-001 水位线告警"
  - "#18 AI 多轮对话令牌通胀: PerTaskTokenBudget（与 Per-request 预算正交）"
  - "#19 模型幻觉-容量正反馈螺旋: DegradationSpiralDetector（M-29）+ SLI CAP-SPI-001"
  - "#20 SQLite 并发写入瓶颈: MetricsWriteBuffer + 批量异步刷盘（TASK-0003）"
  - "#21 Telemetry 存储爆炸: capacity_metrics_hourly + 30d→14d→7d TTL（TASK-0003）"
  - "#22 Owner 决策疲劳: OwnerHealthMonitor + SEV-2 自动响应规则"
  - "#23 AI 技能退化检测: AISkillMonitor（M-28, 4维检测器）"
  - "#24 Token 成本 vs 产出价值 ROI: TokenValueAttribution（M-30, ROI评分）"
  - "#25 W3C TraceContext 容量元数据缺失: TraceCapacityInjector（tracestate cap_* 注入）"
rollback_instructions:
  - "每个模块独立可回滚，删除单个.py文件不影响其他模块"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§21 第二轮盲点审计 #17-#25", "M-28/M-29/M-30 模块定义"]
    purpose: "提取 9 个 v2.3.0 盲点及对应代码骨架"
tags:
  - capacity-assurance
  - blind-spots
  - round-2
  - BS-017-to-BS-025
phase: phase_2_enhance
estimated_effort_minutes: 210
ai_autonomy: AI-Modifiable
governance_layer: GOV-P1
runtime_plane: RP-3

source_blueprint: "MOD-INF-001"
source_section: "蓝图 §21 第二轮盲点审计 #17-#25"
description: "第二轮盲点审计关闭：盲点 #17 至 #25（§21 v2.3.0 扩展——新增 M-28/29/30）"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\context_budget_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\per_task_token_budget.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\ai_skill_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\degradation_spiral_detector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\token_value_attribution.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\owner_health_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\modules\\trace_capacity_injector.py"
forbidden_touch:
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\**\*.md"
  - "D:\ZephyrAlpha\src\zephyr\shared\schemas.py"
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 63000
timeout_minutes: 210
depends_on:
  - TASK-MOD-INF-001-0003
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0009
  - TASK-MOD-INF-001-0013
blocked_by: []
status: done
tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-001"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---


# 第二轮盲点审计关闭：盲点 #17 至 #25

## 1. 任务来源

从蓝图 §21 "第二轮盲点审计" 提取（9 个盲点 #17-#25），对照 Google SRE Workbook §24、Anthropic 2026 Codified Context Patterns、OpenAI Token Economics、AWS Well-Architected Cost Optimization。

## 2. 盲点清单与关闭映射

| 盲点 | 蓝图原文标题 | 本质 | 关闭方式 |
|------|------------|------|---------|
| #17 | Context 预算慢泄漏 | context_window 90%→94%→98%缓慢侵蚀，耗尽后触发级联错误 | ContextBudgetGuard：context_watermark（80%/90%/100%）三级保护 |
| #18 | AI 多轮对话令牌通胀 | ReAct 循环 3 轮→5 轮→8 轮+，工具调用响应越来越大 | PerTaskTokenBudget（与 Per-request 正交）：task_max_tokens + 拆分子任务 |
| #19 | 模型幻觉-容量正反馈螺旋 | 幻觉→token浪费→容量告警→模型降温→更多幻觉 死循环 | DegradationSpiralDetector（M-29）：检测螺旋模式 + circuit_break |
| #20 | SQLite 并发写入瓶颈 | 容量保障自身是最频写的 consumer，写锁竞争破坏 SLI 精度 | 写入缓冲+批量异步刷盘（TASK-0003 MetricsWriteBuffer） |
| #21 | Telemetry 存储爆炸 | 27模块×10 metrics/sec×7天TTL = 108GB→磁盘撑满 | 30d→14d→7d 降级TTL + capacity_metrics_hourly 聚合（TASK-0003） |
| #22 | Owner 决策疲劳 | 1人面对 200+警报/周，30%未读，50%非紧急误报 | OwnerHealthMonitor：警报疲劳评分 + SEV-2 auto\_respond |
| #23 | AI 技能退化检测 | 随着系统复杂度上升，AI 施工质量隐性下降 | AISkillMonitor（M-28）：4维检测（test_pass/merge_conflict/retry/acceptance） |
| #24 | Token 成本 vs 产出价值 ROI | 不区分稳定业务token vs 实验token，$50/day盲目消耗 | TokenValueAttribution（M-30）：按任务类型区分 ROI |
| #25 | W3C TraceContext 容量元数据缺失 | tracecontext 无容量信息导致跨模块降级不协调 | TraceCapacityInjector：tracestate 注入 cap_budget_remaining 等字段 |

## 3. 施工内容

### 3.1 #17: ContextBudgetGuard

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\context_budget_guard.py`

实现 `ContextBudgetGuard` 类（蓝图 L2000-2022）：
- `check_watermark(current_pct: float) -> WatermarkLevel`：
  - ≤80% → NORMAL
  - 80%-90% → WARNING (记录告警)
  - 90%-100% → CRITICAL (拒绝更多上下文注入)
- 新增 SLI：`CAP-CTX-001` (context_watermark_breach)
- 蓝图 L2000-2035 YAML 配置完整实现

### 3.2 #18: PerTaskTokenBudget

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\per_task_token_budget.py`

实现 `PerTaskTokenBudget` 类（蓝图 L2039-2106）：
- `allocate(task_id, estimated_reasoning_steps) -> TaskBudget`
- `check_and_consume(task_id, actual_tokens) -> ConsumptionResult`
- 超出预算时触发 `task_split`（自动拆分为子任务）
- 蓝图 L2058-2078 YAML 完整实现

### 3.3 #23: AISkillMonitor (M-28)

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\ai_skill_monitor.py`

实现 `AISkillMonitor` 类（蓝图 L2431-2501）：
- 四维 AI 技能健康度检测：
  - `test_pass_rate`: 第一轮测试通过率 → trending_down → 0.2 decay_weight
  - `merge_conflict_rate`: PR 冲突率 → trending_up → 0.25
  - `retry_loop_rate`: 修复重试次数 → trending_up → 0.25
  - `instant_acceptance_rate`: Owner 直接接受率 → trending_down → 0.30
- `compute_skill_score() -> float`：加权评分
- `detect_degradation_trend() -> bool`：评分连续下降时报警
- 蓝图 L2445-2472 算法完整实现

### 3.4 #19: DegradationSpiralDetector (M-29)

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\degradation_spiral_detector.py`

实现 `DegradationSpiralDetector` 类（蓝图 L2110-2205）：
- 检测三点闭环：`幻觉率↑ ∩ Token消耗↑ ∩ 容量告警↑` → 螺旋判定
- `detect_spiral() -> SpiralDecision`：发现螺旋→circuit_break→强制切换到高可靠性模型
- 新增 SLI：`CAP-SPI-001` (spiral_detection_count)
- 蓝图 L2139-2206 算法完整实现

### 3.5 #24: TokenValueAttribution (M-30)

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\token_value_attribution.py`

实现 `TokenValueAttribution` 类（蓝图 L2507-2584）：
- 按任务类型区分消费：`stable_business` / `experiment` / `debugging` / `unknown`
- `compute_roi(task_type, tokens_consumed, task_success: bool) -> float`
- `generate_monthly_roi_report() -> ROISummary`
- 蓝图 L2519-2585 算法完整实现

### 3.6 #22: OwnerHealthMonitor

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\owner_health_monitor.py`

实现 `OwnerHealthMonitor` 类（蓝图 L2372-2427）：
- `compute_alert_fatigue_score(weekly_alerts: int, unread_pct: float, false_alarm_pct: float) -> float`
- SEV-2 级别自动响应（合并为 Morning Digest）
- `detect_burnout_risk() -> bool`：连续 2 周疲劳评分 > 0.7 触发预警
- 蓝图 L2372-2427 YAML/代码完整实现

### 3.7 #25: TraceCapacityInjector

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\trace_capacity_injector.py`

实现 `TraceCapacityInjector` 类（蓝图 L2591-2654）：
- `inject_capacity_metadata(span: Span)`：向 W3C tracestate 注入：
  - `cap_budget_remaining`: 剩余 Error Budget 百分比
  - `cap_tier`: 当前响应级别 (L0-L4)
  - `cap_model_tier`: 当前模型级别
- `extract_from_tracecontext(headers: Dict) -> CapacityMetadata`：下游提取
- 蓝图 L2571-2654 代码完整实现

### 3.8 配置扩展

- `capacity_slo.yaml` 新增 SLI：CAP-CTX-001、CAP-SPI-001
- `token_budget.yaml` 新增 per_task_budget 节

## 4. 验收标准

1. ContextBudgetGuard：context 水位 ≥ 90% 时拒绝新注入 → 断点验证通过
2. PerTaskTokenBudget：任务 token 超限时自动拆分 → 拆分验证
3. AISkillMonitor：4维评分 trend 下降 3 天 → 告警触发
4. DegradationSpiralDetector：模拟幻觉率↑+Token↑+告警↑ → 螺旋判定正确
5. TokenValueAttribution：月度 ROI 报告产出率 > 90%
6. TraceCapacityInjector：tracestate 注入后下游可解析
7. 9个盲点全部有显式关闭方式
