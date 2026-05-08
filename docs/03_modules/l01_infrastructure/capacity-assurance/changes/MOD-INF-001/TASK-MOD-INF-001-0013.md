---


task_id: TASK-MOD-INF-001-0013
module_id: MOD-INF-001
title: "第一轮盲点审计关闭：盲点 #1 至 #16（对照 Google SRE / Netflix / Meta / ISACA 全量审计）"
doc_type: task_card
status: done
priority: P1
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T03:02:00+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0001
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0009
  - TASK-MOD-INF-001-0010
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
  - "D:\\ZephyrAlpha\\config\\capacity\\capacity_slo.yaml"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\alert_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\adaptive_sampler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\slo_review_assistant.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\ai_understandability_constraint.py"
acceptance_criteria:
  - "#1 SLI 插桩点未定义: capacity_slo.yaml v2.2.0 instrumentation 字段已扩展（TASK-0009）"
  - "#2 SLO 窗口未分层: fast_cycle(3d)/medium_cycle(7d)/slow_cycle(30d) 三层已定义（TASK-0009）"
  - "#3 Error Budget 消耗归因缺失: error_budget_events 表 + get_budget_attribution() 实现（本任务 AlertManager + TASK-0014）"
  - "#4 短窗口高 Burn Rate 误触发: 持续时长判定 + 脉冲过滤（TASK-0014 kill_switch.py 增强）"
  - "#5 SLO 定期 Review 与演进机制缺失: SLOReviewAssistant 类（本任务）"
  - "#6 容量保障自身资源消耗未管控: AdaptiveSampler 自适应采样 + 自身开销估算（本任务）"
  - "#7 缺少单一聚合容量健康评分: ZephyrHealthScore（TASK-0006 M-13）"
  - "#8 AI 行为预测维度缺失: ai_behavior_slis（TASK-0006 M-14）"
  - "#9 容量预警→修复行动闭环断裂: remediation_playbook.yml（TASK-0006 M-15）"
  - "#10 成本回归后的自动回升缺失: model_routing restoration 规则（TASK-0006 M-16）"
  - "#11 缺少渐进式流量切换能力: ChangeRateLimiter（TASK-0006 M-17）"
  - "#12 告警疲劳: alert_governance 告警收敛四机制（本任务 AlertManager）"
  - "#13 AI 可理解性作为第一性设计约束: AIUnderstandabilityConstraint 声明与验证（本任务）"
  - "#14 hash 链校验性能退化: risk_register.yaml R11（TASK-0010）"
  - "#15 Token 预估模型白盒包裹风险: risk_register.yaml R12（TASK-0010）"
  - "#16 Kill Switch 双通道竞态: risk_register.yaml R13（TASK-0010）"
rollback_instructions:
  - "盲点关闭模块独立部署，逐个删除不影响核心保障功能"
  - "每个新模块可独立回滚"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§20.1 SLI/SLO + Error Budget 层盲点 #1-#5", "§20.2 容量保障结构性盲点 #6-#11", "§20.3 SOLO Coder 特异性盲点 #12-#16"]
    purpose: "提取全部 16 个盲点及其逆源的完整上下文"
tags:
  - capacity-assurance
  - blind-spots
  - round-1
  - BS-001-to-BS-016
phase: phase_1_scaffold
estimated_effort_minutes: 150
ai_autonomy: AI-Modifiable
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 §20 第一轮盲点审计 #1-#16"
description: "第一轮盲点审计关闭：盲点 #1 至 #16（对照 Google SRE / Netflix / Meta / ISACA 全量审计）"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\alert_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\adaptive_sampler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\slo_review_assistant.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\ai_understandability_constraint.py"
forbidden_touch:
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\**\*.md"
  - "D:\ZephyrAlpha\src\zephyr\shared\schemas.py"
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式 TASK-{DOMAIN}-{NNNN}"
  - module_id: "PS-STD-011"
  - module_id: "ADR-0040"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 45000
timeout_minutes: 150
depends_on:
  - TASK-MOD-INF-001-0001
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0009
  - TASK-MOD-INF-001-0010
blocked_by: []
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



# 第一轮盲点审计关闭：盲点 #1 至 #16

## 1. 任务来源

从蓝图 §20 "盲点分析与补充设计（v2.2.0 新增）"提取，审计方法：对照 Google SRE Workbook §4 §5 §12 §14 + OpenTelemetry 2025 GenAI Semantic Conventions + ISACA AI Audit Program + Anthropic Codified Context + VictoriaMetrics Vibe Coding Blog 2026。

**三层结构：**
- §20.1: SLI/SLO + Error Budget 层盲点（5项：#1~#5）
- §20.2: 容量保障结构性盲点（6项：#6~#11）
- §20.3: SOLO Coder（1人+AI 维护）特异性盲点（5项：#12~#16）

## 2. 盲点清单与关闭映射

### 2.1 §20.1: SLI/SLO + Error Budget 层盲点

| 盲点 | 蓝图原文标题 | 本质 | 关闭方式 | 任务卡 |
|------|------------|------|---------|--------|
| #1 | SLI 插桩点未定义 | §13 capacity_slo.yaml 缺失 instrumentation hook_point/collection_method/aggregation | capacity_slo.yaml v2.2.0 每个 SLI 新增 instrumentation 字段 | TASK-0009 |
| #2 | SLO 窗口未分层 | 所有 SLO 共享统一窗口，未按组件稳定性分层 | fast_cycle(3d)/medium_cycle(7d)/slow_cycle(30d) | TASK-0009 |
| #3 | Error Budget 消耗归因缺失 | error_budget 表只能答"哪个SLO预算在减"，不能答"为什么" | error_budget_events 表(violation_type/module_id/agent_id) + get_budget_attribution() | TASK-0014 + 本任务 |
| #4 | 短窗口高 Burn Rate 误触发 | Burn Rate 1h > 14.4× 直接触发只读模式 → 临时脉冲误触发 | 持续时长判定(≥5min)+脉冲过滤 → escalate_if_sustained | TASK-0014 |
| #5 | SLO 定期 Review 与演进机制缺失 | 没有定义 SLO 目标值本身的演进周期 | SLOReviewAssistant.generate_quarterly_review() + auto_retire_stale_slis() | 本任务 |

### 2.2 §20.2: 容量保障结构性盲点

| 盲点 | 蓝图原文标题 | 本质 | 关闭方式 | 任务卡 |
|------|------------|------|---------|--------|
| #6 | 容量保障自身的资源消耗未管控 | capacity_governance_loop 每 300s 轮询 + OTel SDK 自有开销 → 容量极限时可能是最后一根稻草 | AdaptiveSampler（高负载降频）+ SelfOverheadReport（自身开销<2%系统资源） | 本任务 |
| #7 | 缺少单一聚合容量健康评分 | Owner 面对 27 模块+8 SLI+五级EB+四级TB+DR 四级 → 信息过载 | ZephyrHealthScore（Technical:0.40 + Business:0.30 + Cost:0.30）| TASK-0006(M-13) |
| #8 | AI 行为预测维度缺失 | §17 容量预测的 6 维全是资源消耗结果，不是资源消耗原因——是 AI 行为驱动了资源消耗 | ai_behavior_slis（5个SLI: task-generation-rate/code-churn-rate/model-call-failure-rate/code-rework-rate/owner-approval-burst）| TASK-0006(M-14) |
| #9 | 容量预警→修复行动闭环断裂 | Kill Switch 保守模式阻止 AI 施工 → AI 无法优化内存 → 锁死在只读模式 | remediation_playbook（remediation_channel保持open，用降级模型执行修复） | TASK-0006(M-15) |
| #10 | 成本回归后的自动回升缺失 | degradation 降级是单向的（只降不升）→ 成本回落$2/day但仍在用降级模型 | model_routing.restoration（双向切换：降级条件 + 回升条件 + cooldown 6h）| TASK-0006(M-16) |
| #11 | 缺少渐进式流量切换能力 | Kill Switch（全或无）是核弹，对中间状态（"让AI慢50%而非停工"）缺少手术刀级控制 | ChangeRateLimiter（progressive throttle pct 0.0-1.0） | TASK-0006(M-17) |

### 2.3 §20.3: SOLO Coder 特异性盲点

| 盲点 | 蓝图原文标题 | 本质 | 关闭方式 | 任务卡 |
|------|------------|------|---------|--------|
| #12 | 告警疲劳——这个架构的阿喀琉斯之踵 | 5级EB + 4级TB + DR4级 + 容量预测6维 = 20+告警源 → 1人必然告警疲劳 | alert_governance 四机制（收敛30min/静默期00-08/自愈优先/消息优先级路由） | 本任务 |
| #13 | AI 可理解性作为第一性设计约束 | 90%+代码是AI生成的 → 容量保障代码质量由"AI改得有多对"决定 → 本蓝图复杂度已是27模块 | AIUnderstandabilityConstraint（前向编码约束 + 后向审计度量）+ 入代码级合规 | 本任务 |
| #14 | hash链校验性能退化 | 大型文件hash计算随Provenance增长而退化 | R11 → risk_register.yaml | TASK-0010 |
| #15 | Token预估模型白盒包裹风险 | AI构造的input特殊格式导致预估失败 | R12 → risk_register.yaml | TASK-0010 |
| #16 | Kill Switch双通道竞态 | 环境变量+文件信号竞态 | R13 → risk_register.yaml | TASK-0010 |

## 3. 施工内容（本任务新增模块——仅执行尚未被其他任务卡覆盖的部分）

### 3.1 #12 + #3: AlertManager + 告警收敛

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\alert_manager.py`

实现 `AlertManager` 类（集成 `AlertGovernanceConfig`）：
- `should_notify(alert: Alert) -> (bool, str)`：
  - 静默期检查（00:00-08:00，emergency/kill_switch_triggered 除外）
  - 收敛检查（30min内同 SLO+Module 重复告警 → 合并）
  - 自愈优先（warning 级别先尝试 auto_heal，成功→不入通知）
- `generate_morning_digest() -> str`：每天早上 8 点聚合摘要
- 消息优先级路由：realtime→emergency/critical/kill_switch；hourly→cautious；daily→warning
- 对应 capacity_slo.yaml v2.2.0 `alert_governance` 节（蓝图 L1613-1647）完整实现

### 3.2 #6: AdaptiveSampler

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\adaptive_sampler.py`

实现 `AdaptiveSampler` 类：
- `compute_interval(system_load: float, error_budget_tier: str) -> int`：
  - 高负载(>0.8) → 1800s（大幅降频）
  - 中负载(>0.6) → 600s（降频50%）
  - 预算健康(warning/healthy) → 再放宽 1.5×
- `estimate_self_overhead() -> SelfOverheadReport`：自身 CPU/内存/IO 开销 < 2% 系统资源验证
- 蓝图 L1334-1355 完整实现

### 3.3 #5: SLOReviewAssistant

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\slo_review_assistant.py`

实现 `SLOReviewAssistant` 类：
- `generate_quarterly_review() -> SLOReviewReport`：
  - 实际 p99 < target × 0.3 → 建议 tighten
  - 实际 p99 > target × 1.2 → 建议 relax
  - error_budget_remaining > 0.95 → 建议 retire（考虑退役此 SLI）
- `auto_retire_stale_slis(staleness_days=90)`：自动标记>90天预算消耗<5%的SLI为"待退役审查"
- 蓝图 L1299-1317 完整实现

### 3.4 #13: AIUnderstandabilityConstraint

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\ai_understandability_constraint.py`

实现 `AIUnderstandabilityConstraint` 类：
- **前向编码约束（AI施工时NZC）**：
  - `check_single_file_single_responsibility(file_path)`：每文件 ≤ 1 核心类
  - `check_yaml_zero_ambiguity(yaml_path)`：Python bool 而非 "yes/no"
  - `check_ai_navigable_name(file_path)`：文件名→AI能从文件名推断功能
- **后向审计度量（AI回读时验证）**：
  - `measure_schema_sprawl(config_dir)`：新增 YAML 字段数
  - `measure_import_ambiguity(module_path)`：模糊import数
  - `compute_explainability_score()`：综合可理解性评分
- **AI可理解性总评分 70/100 = 入常规迭代；<70 = AI上下文退化警讯 → 提示Owner回溯**
- 蓝图 L1685-1725 AI理解性约束完整落地

### 3.5 alert_governance 配置扩展

在 `D:\ZephyrAlpha\config\capacity\capacity_slo.yaml` 中追加 `alert_governance` 节（蓝图 L1613-1647 YAML 直接实现），含：
- `convergence`：窗口30min，按 slo_id+module_id 聚合
- `quiet_hours`：00:00-08:00，例外 emergency/kill_switch_triggered，早上morning_digest
- `auto_remediation`：warning→auto_heal_first (max 3 tries)，cautious→log+weekly_report_only，critical→notify_owner
- `notification_routing`：realtime/hourly_digest/daily_digest/weekly_digest 四通道

## 4. 验收标准

1. AlertManager 告警收敛：30min内同SLO+Module重复告警只入1条 → 收敛率 > 80%
2. AdaptiveSampler：系统负载 > 0.8 时采样间隔 ≥ 1800s
3. SLOReviewAssistant：生成可用季度报告含至少1条 tighten/relax/retire 建议
4. AIUnderstandabilityConstraint：总评分 < 70 时触发AI回退警讯
5. 全部16个盲点有明确的关闭方式：4个模块本任务新建 + 12个引用已有任务卡