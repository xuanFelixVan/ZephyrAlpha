---


task_id: TASK-MOD-INF-001-0016
module_id: MOD-INF-001
title: "第四轮盲点深度审计关闭：盲点 #39 至 #54 + 五条元原则 + M-36~M-41 内联增强"
doc_type: task_card
status: done
priority: P1
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T03:03:30+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0010
  - TASK-MOD-INF-001-0015
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\capacity_fingerprint.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\budget_aware_prompt.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\vibe_experiment_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\capacity_runbook_generator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\alert_precision_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\longevity_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\dependency_capacity_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\capacity_digital_twin.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\alert_escalation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\core_integrity_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\code_economy_analyzer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\module_birth_registry.py"
  - "D:\\ZephyrAlpha\\config\\capacity\\owner_offline_protocol.yaml"
  - "D:\\ZephyrAlpha\\config\\capacity\\capacity_slo.yaml"
  - "D:\\ZephyrAlpha\\config\\capacity\\token_budget.yaml"
acceptance_criteria:
  - "#39 AI生成非确定性→CapacityFingerprint类: compare()检测2×内存/3×导入时间退化"
  - "#40 Prompt与容量指令语义冲突→BudgetAwarePromptMerger: full_build/essential_only/minimal_viable三模式"
  - "#41 氛围编程快速实验容量税→VibeExperimentTracker: 每日200K tokens/15次实验上限,自动清理产物"
  - "#42 长期离线(7天+)容量自治→Vacation Mode: DO NOT BUILD/DEPLOY/SPEND,仅监控+每日快照"
  - "#43 AI模型切换容量行为突变→ModelCapacityProfile+ModelSwitchRecalibrator: 切换时自动重校准预算"
  - "#44 容量运维知识单点蒸发→CapacityRunbookGenerator:自文档化Runbook,每次事后产出诊断+修复步骤"
  - "#45 告警精度退化→AlertPrecisionTracker: Precision/Recall计算,Precision<30%自动抑制高误报规则"
  - "#46 多周黄昏退化→LongevityMonitor: GC代际/WAL膨胀/ChromDB持久化/句柄泄漏月频检测"
  - "#47 Git仓库膨胀→git gc自动调度: 每周日03:00, >50MB文件建议LFS"
  - "#48 pip依赖容量炸弹→DependencyCapacityGuard: pip前后容量快照,内存增长>100MB→回滚"
  - "#49 容量数字孪生→CapacityDigitalTwin: G5门禁事前模拟,启动退化>30%或内存增长>50%→BLOCK"
  - "#50 容量系统自身生命周期→Meta-SLO: META-001~META-004,self_upgrade_protocol三阶段升级"
  - "#51 卡珊德拉困境→AlertEscalation: 4级升格(0min→15min→1h→4h),L3自动行动"
  - "#52 AI自我修改容量代码元风险→CoreIntegrityGuard: IMMUTABLE_CORE清单+双签+每日哈希校验"
  - "#53 氛围编程过度抽象→CodeEconomyAnalyzer: 函数平均<5行/类>函数数/模式名检测"
  - "#54 AI影子模块容量泄漏→ModuleBirthRegistry: 出生证明+每周孤儿扫描"
  - "五条元原则在对应模块中落地"
rollback_instructions:
  - "每个模块独立可禁用"
  - "逐个盲点独立回滚"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§23 第四轮盲点审计 #39-#54", "§23.9 五条元原则", "§23.8 M-36~M-41", "§24.7 取证发现#7 META-005 通知渠道健康"]
    purpose: "提取第四轮16个盲点+五条元原则+M-36~M-41内联增强+META-005通知渠道健康"
tags:
  - capacity-assurance
  - blind-spots
  - round-4
  - BS-039-to-BS-054
  - meta-principles
phase: phase_2_enhance
estimated_effort_minutes: 240
ai_autonomy: AI-Modifiable
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 §23 第四轮盲点审计 #39-#54 + §24.7 META-005"
description: "第四轮盲点深度审计关闭：盲点 #39 至 #54 + 五条元原则 + M-36~M-41 内联增强"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\capacity_fingerprint.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\budget_aware_prompt.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\vibe_experiment_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\capacity_runbook_generator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\alert_precision_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\longevity_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\dependency_capacity_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\capacity_digital_twin.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\alert_escalation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\core_integrity_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\code_economy_analyzer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\module_birth_registry.py"
  - "D:\\ZephyrAlpha\\config\\capacity\\owner_offline_protocol.yaml"
  - "D:\\ZephyrAlpha\\config\\capacity\\capacity_slo.yaml"
  - "D:\\ZephyrAlpha\\config\\capacity\\token_budget.yaml"
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
estimated_tokens: 72000
timeout_minutes: 240
depends_on:
  - TASK-MOD-INF-001-0010
  - TASK-MOD-INF-001-0015
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



# 第四轮盲点深度审计关闭：盲点 #39 至 #54 + 五条元原则 + M-36~M-41

## 1. 任务来源

从蓝图 §23 "第四轮盲点审计" 提取（16 个盲点 #39-#54 + M-36~M-41 + 五条元原则）。

§23 分为五个维度：
- §23.1 AI 生成代码特有容量盲点（3 项：#39-#41）
- §23.2 1人+AI运维的生存临界盲点（4 项：#42-#45）
- §23.3 物理/工程深层退化（3 项：#46-#48）
- §23.4 顶尖设计的架构盲区（4 项：#49-#52）
- §23.5 氛围编程特有的深层反模式（2 项：#53-#54）

## 2. 盲点清单与关闭映射

| 盲点 | 内容 | 严重度 | 关闭方式 |
|------|------|:---:|---------|
| #39 | AI代码生成的非确定性→容量行为不可复现 | 高 | CapacityFingerprint (M-36) |
| #40 | Prompt与容量指令的语义冲突 | 高 | BudgetAwarePromptMerger (M-37) |
| #41 | 氛围编程"快速实验"的隐性容量税 | 高 | VibeExperimentTracker (M-38) |
| #42 | 长期离线(7天+)的容量自治 | 高 | Vacation Mode (owner_offline_protocol.yaml) |
| #43 | AI模型切换的容量行为突变 | 高 | ModelCapacityProfile + ModelSwitchRecalibrator |
| #44 | 容量运维知识的单点蒸发(Bus Factor=1) | 致命 | CapacityRunbookGenerator |
| #45 | 容量告警的精度退化 | 高 | AlertPrecisionTracker |
| #46 | 系统的"黄昏退化"——多周运行的结构性容量流失 | 高 | LongevityMonitor (M-39) |
| #47 | Git仓库膨胀的隐性容量成本 | 中 | git gc 自动调度 + git_repo_health CAP-015 |
| #48 | pip依赖更新的"容量炸弹" | 高 | DependencyCapacityGuard |
| #49 | 容量"数字孪生"——AI动手前先模拟 | 高 | CapacityDigitalTwin (M-40) |
| #50 | 容量系统自身生命周期——谁维护维护者 | 高 | Meta-SLO (META-001~005) + self_upgrade_protocol |
| #51 | "卡珊德拉困境"——系统预测准确但Owner不信 | 致命 | AlertEscalation (4级升格) |
| #52 | AI自我修改容量治理代码的"元风险" | 致命 | CoreIntegrityGuard (M-41) |
| #53 | 氛围编程的"过度抽象"容量陷阱 | 中 | CodeEconomyAnalyzer |
| #54 | AI生成的"影子模块"容量泄漏 | 高 | ModuleBirthRegistry |

## 3. 施工内容

### 3.1 #39: CapacityFingerprint (M-36)

文件：`D:\ZephyrAlpha\src\zephyr\shared\capacity_fingerprint.py`

实现 `CapacityFingerprint` 类：
- `fingerprint(module_path)`: 生成模块容量指纹（loc/import数/class数/function数/依赖数/AST深度 + 运行时import_time/memory_delta）
- `compare(old, new)`: 比较新旧指纹，检测退化：
  - 内存用量 > 2× → Warning
  - 导入时间 > 3× → Warning
  - 代码行数 > 1.8× 但函数数 ≤ 1.1× → 过度设计警告
- 集成到 G5 门禁（合入前容量指纹检查）

### 3.2 #40: BudgetAwarePromptMerger (M-37)

文件：`D:\ZephyrAlpha\src\zephyr\shared\budget_aware_prompt.py`

实现 `BudgetAwarePromptMerger` 类：
- `full_build` 模式（Token Budget > 70% + Error Budget healthy）
- `essential_only` 模式（Token Budget 30%~70% + warning）
- `minimal_viable` 模式（Token Budget < 30% + critical/emergency）
- `merge(task, budget_status)`: 根据预算选择施工模式

### 3.3 #41: VibeExperimentTracker (M-38)

文件：`D:\ZephyrAlpha\src\zephyr\shared\vibe_experiment_tracker.py`

实现 `VibeExperimentTracker` 类：
- `start_experiment(task_desc)`: 检查日预算（200K tokens/15次/天），超限→VibeBudgetExhausted
- `end_experiment(exp_id, kept_files)`: 统计资源消耗，清理实验产物
- 配置：`vibe_experiment_budget` 节 in token_budget.yaml

### 3.4 #42: Vacation Mode

在 `D:\ZephyrAlpha\config\capacity\owner_offline_protocol.yaml` 中新增 vacation_mode 节：
- 触发：Owner设置 OR 连续72h无响应
- 核心原则：DO NOT BUILD / DO NOT DEPLOY / DO NOT SPEND / DO MONITOR / DO PERSIST
- 每日报告：健康评分/Error Budget消耗/Token消耗/P0告警/度假天数
- 最大14天，回来后24h warm-up期

### 3.5 #43: ModelCapacityProfile + ModelSwitchRecalibrator

文件：`D:\ZephyrAlpha\src\zephyr\shared\model_capacity_profile.py`

- `ModelCapacityProfile`: 每模型容量画像（成本/延迟/典型Token消耗/API限制/质量指标）
- `ModelSwitchRecalibrator.on_model_switch(from, to)`: 切换时自动重校准所有预算

### 3.6 #44: CapacityRunbookGenerator

文件：`D:\ZephyrAlpha\src\zephyr\shared\capacity_runbook_generator.py`

- `generate_from_incident(incident)`: 产出诊断方法+修复步骤+预防措施
- `_score(incident)`: 自评Runbook质量(0-100)，Owner审核加分
- 存储：`data/runbook/` Markdown格式

### 3.7 #45: AlertPrecisionTracker

文件：`D:\ZephyrAlpha\src\zephyr\shared\alert_precision_tracker.py`

- `record_alert_and_outcome(alert, outcome)`: 以Owner实际行动为Ground Truth
- `compute_precision_recall(window_days=30)`: Precision<30%→自动抑制高误报规则
- 每周一自动生成AlertQualityReport

### 3.8 #46: LongevityMonitor (M-39)

文件：`D:\ZephyrAlpha\src\zephyr\shared\longevity_monitor.py`

- `monthly_check()`: 对比月初快照 vs 当前状态
- 监控指标：python_gc_time / sqlite_wal_size / chromadb_pending_persist / open_file_handles / avg_import_time
- 月内增长>50%→告警+建议操作

### 3.9 #47: Git仓库健康监控

在 `capacity_slo.yaml` 中新增 git_repo_health 节：
- CAP-015-git-repo-size-mb 指标
- weekly git gc --aggressive
- >50MB文件跟踪+建议LFS
- git操作性能：status/diff耗时基线监控

### 3.10 #48: DependencyCapacityGuard

文件：`D:\ZephyrAlpha\src\zephyr\shared\dependency_capacity_guard.py`

- `guard_pip_operation(operation, packages)`: Sandbox中先跑→前后容量快照
- 内存增长>100MB → BLOCK + 回滚命令
- 导入时间增加>500ms → BLOCK

### 3.11 #49: CapacityDigitalTwin (M-40)

文件：`D:\ZephyrAlpha\src\zephyr\shared\capacity_digital_twin.py`

- `simulate_merge(task_card)`: Sandbox副本中应用所有变更→测量容量
- 判定：启动退化>30% → BLOCK / 内存增长>50% → BLOCK / 新依赖>5 → WARN
- 集成到 G5 pre-merge gate

### 3.12 #50: Meta-SLO

在 `capacity_slo.yaml` 中新增 meta_slo 节：
- META-001-governance-loop-liveness: 5分钟内至少执行一次评估
- META-002-error-budget-integrity: 每周原始SQL交叉验证，误差<1%
- META-003-kill-switch-drill: 每月dry-run
- META-004-circuit-breaker-drift: 30min状态一致性检查
- META-005-notification-channel-health: 通知渠道（飞书/PUSH/本地持久化）本身的健康监控——主通道发送失败率、本地持久化队列长度、系统重启后未确认告警恢复扫描
- self_upgrade_protocol: staging→canary→production三阶段

### 3.13 #51: AlertEscalation

文件：`D:\ZephyrAlpha\src\zephyr\shared\alert_escalation.py`

- 4级升格：0min→15min(飞书)→1h(飞书PUSH)→4h(全渠道+自动行动)
- L3自动行动：memory_saturation→Kill Switch / error_rate_spike→并发降为1 / cost_overrun→最便宜模型

### 3.14 #52: CoreIntegrityGuard (M-41)

文件：`D:\ZephyrAlpha\src\zephyr\shared\core_integrity_guard.py`

- IMMUTABLE_CORE清单：kill_switch.py / error_budget_tracker.py / circuit_breaker.py / token_budget_tracker.py / graceful_shutdown.py / startup_guard.py
- `pre_commit_check(changed_files)`: 核心文件变更→BLOCK+要求Owner dual-sign-off
- `daily_integrity_check()`: 哈希校验，不匹配→P0告警

### 3.15 #53: CodeEconomyAnalyzer

文件：`D:\ZephyrAlpha\src\zephyr\shared\code_economy_analyzer.py`

- 检测规则：
  - 函数平均<5行+函数数>3→过度拆分
  - 类数>函数数→Factory/Builder反模式
  - 模块名含factory/builder/strategy等+1类≤2函数→过度设计
- 评分：100(PASS) / 75(WARN) / 40(HINT)

### 3.16 #54: ModuleBirthRegistry

文件：`D:\ZephyrAlpha\src\zephyr\shared\module_birth_registry.py`

- `register_birth(file_path, task_id, reason)`: 记录创建者/原因/父模块/哈希/预估内存
- `weekly_orphan_report()`: 扫描磁盘有但注册表无的影子模块→建议清理

## 4. 五条元原则实现

经过四轮54项盲点审计提炼的五条穿透性设计哲学：

| # | 元原则 | 一句话 | 驱动盲点 |
|:---:|------|------|------|
| 1 | 自愈优于告警 (Self-Healing > Alerting) | 系统自主修复90%容量问题，Owner只需知道"修好了" | #12,#16,#19,#26,#28,#42,#44,#51 |
| 2 | 预算驱动开发 (Budget-Driven Development) | Token/Error Budget决定AI施工速率和质量深度 | #9,#10,#17,#18,#24,#37,#40,#41 |
| 3 | 渐进式自治 (Progressive Autonomy) | 完全依赖→半自治→大部自治，自治级别由预算盈余决定 | #5,#7,#8,#13,#16,#43 |
| 4 | 反脆弱可观测性 (Anti-Fragile Observability) | 每事故→Runbook→校准→门禁更新，系统从事故事学习 | #3,#4,#23,#30,#31,#33,#34,#46 |
| 5 | 经济透明即控制 (Cost Transparency = Control) | 所有容量指标可翻译为¥/天和Owner时间/周 | #11,#14,#22,#24,#38,#39,#48 |

## 5. M-36~M-41 内联增强（不应纳入 §6 模块分解表）

| 模块ID | 模块名称 | 职责 | 归属 |
|--------|---------|------|------|
| M-36 | capacity_fingerprint.py | AI生成代码容量指纹+非确定性退化检测 | 集成到 capacity_governance_loop |
| M-37 | budget_aware_prompt.py | 预算感知Prompt合并——消除AI语义冲突 | 集成到 context_assembler |
| M-38 | vibe_experiment_tracker.py | 氛围编程实验预算+产物清理 | 集成到 task_manager |
| M-39 | longevity_monitor.py | 多周黄昏退化检测+月报 | 独立 cron job |
| M-40 | capacity_digital_twin.py | 变更前容量模拟——"AI先试再动手" | 集成到 G5 pre-merge gate |
| M-41 | core_integrity_guard.py | 不可变核心代码保护+哈希校验 | 集成到 G0 pre-commit hook |

## 6. 验收标准

1. 12 个新增模块文件创建完成
2. 3 个配置节新增（vacation_mode / vibe_experiment_budget / meta_slo / git_repo_health）
3. CapacityFingerprint.compare() 在模拟场景正确检测退化
4. BudgetAwarePromptMerger 三模式切换正确
5. VibeExperimentTracker 日预算超限时正确拒绝
6. Vacation Mode 72h无响应自动激活
7. ModelSwitchRecalibrator 切换时预算重校准正确
8. AlertPrecisionTracker Precision<30% 自动抑制生效
9. CapacityDigitalTwin BLOCK/WARN/PASS 判定正确
10. CoreIntegrityGuard 核心文件修改被拦截
11. ModuleBirthRegistry 每周孤儿扫描可发现影子模块
12. 五条元原则在对应模块文档中引用