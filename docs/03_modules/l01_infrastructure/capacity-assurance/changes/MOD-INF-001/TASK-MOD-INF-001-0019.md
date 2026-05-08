---


task_id: TASK-MOD-INF-001-0019
module_id: MOD-INF-001
title: "防御性设计规则：开发-重构-测试循环的门禁植入 + 深度硬规则"
doc_type: task_card
status: done
priority: P0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T03:06:00+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0016
  - TASK-MOD-INF-001-0017
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\code_economy_analyzer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\module_birth_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\core_integrity_guard.py"
acceptance_criteria:
  - "§23.5 氛围编程特有深层反模式(2项): #53过度抽象 #54影子模块"
  - "§24.3 #56蓝图-实现漂移检测"
  - "§24.9 #62蓝图分级访问控制"
  - "§24.11 #64 Owner信任监测"
  - "门禁植入: AI施工→代码提交→契约测试→回归测试(全部PASS才合入)"
  - "提交4步: file_check→contract_check→preset→regression_test"
rollback_instructions:
  - "CodeEconomyAnalyzer仅是检测工具,误报时可关闭"
  - "ModuleBirthRegistry不可删除——删除会破坏孤儿扫描"
  - "CoreIntegrityGuard的IMMUTABLE_CORE清单回滚需Owner双签"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§23.5 氛围编程深层反模式 #53-#54", "§24.3 #56蓝图-实现漂移", "§24.9 #62蓝图分级访问", "§24.11 #64 Owner信任监测"]
    purpose: "提取氛围编程反模式、实现漂移检测、蓝图访问控制、Owner信任监测"
tags:
  - capacity-assurance
  - code-economy
  - birth-registry
  - core-integrity
  - blueprint-audit
  - owner-trust
  - anti-pattern
phase: phase_2_enhance
estimated_effort_minutes: 150
ai_autonomy: Human-Gated
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 §23.5+§24 反模式防护+门禁植入"
description: "防御性设计规则：开发-重构-测试循环的门禁植入 + 深度硬规则"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\code_economy_analyzer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\module_birth_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\core_integrity_guard.py"
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
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0016
  - TASK-MOD-INF-001-0017
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



# 防御性设计规则：门禁植入 + 深度硬规则

> **注意**：蓝图并无显式 AP1~AP8 编号的反模式清单。蓝图仅在以下位置提及"反模式"：
> - §23.5（氛围编程特有的深层反模式 2 项：#53-#54）
> - §24 外部取证中的若干保护性设计
>
> 本任务卡基于蓝图实际内容，合并以下保护性模块的施工。

## 1. 模块清单

| 模块 | 实际路径 | 对盲点 | 职责 | 权限 |
|------|---------|:---:|------|------|
| CodeEconomyAnalyzer | `src/zephyr/shared/code_economy_analyzer.py` | #53 | 检测函数平均<5行/类>函数数/模式名 | AI-Modifiable |
| ModuleBirthRegistry | `src/zephyr/shared/module_birth_registry.py` | #54 | 出生证明注册+每周孤儿扫描 | Immutable Core |
| CoreIntegrityGuard | `src/zephyr/shared/core_integrity_guard.py` | #52 | IMMUTABLE_CORE清单+双签+哈希校验 | Immutable Core |
| BlueprintCodeAuditor | `src/zephyr/shared/blueprint_code_auditor.py` | #56 | 蓝图-代码一致性取证 | weekly cron |
| BlueprintAccessFilter | `src/zephyr/shared/context_assembler.py` + `config/capacity/ai_context_policy.yaml` | #62 | 蓝图阈值移除（不告知AI所有敏感参数） | Immutable Core |
| OwnerTrustGauge | `src/zephyr/shared/owner_trust_gauge.py` | #64 | alert_dismissal_rate>30%=CRITICALLY_LOW | weekly report |

## 2. 氛围编程深层反模式（蓝图 §23.5）

### 2.1 #53: CodeEconomyAnalyzer——过度抽象检测

- 函数平均 < 5 行 + 函数数 > 3 → 过度拆分
- 类数 > 函数数 → Factory/Builder 反模式
- 模块名含 `factory`/`builder`/`strategy` + 1类 ≤ 2函数 → 过度设计
- 评分：100(PASS) / 75(WARN) / 40(HINT)

### 2.2 #54: ModuleBirthRegistry——影子模块追踪

- `register_birth(file_path, task_id, reason)`: 记录创建者+原因+父模块+哈希+预估内存
- `weekly_orphan_report()`: 扫描磁盘有但注册表无的影子模块→建议清理

## 3. 蓝图-实现漂移检测（蓝图 §24.3 #56）

BlueprintCodeAuditor 的 4 项蓝图断言：
- CapacityFingerprint memory 阈值 = 2.0×
- CapacityDigitalTwin 启动退化 = 30%
- CapacityDigitalTwin 内存退化 = 50%
- Kill Switch 保守模式 = 90% 内存

`weekly_audit()`: 每周一 09:00 执行，正则扫描代码中数值。

## 4. 蓝图分级访问控制（蓝图 §24.9 #62）

BlueprintAccessFilter 三级访问：
- **tier_public**: AI 可读
- **tier_internal**: 仅 Owner + Meta-SLO
- **tier_forensic**: 仅取证审计

`filter_for_ai_context(blueprint_text)` —— 敏感参数替换：
- Kill Switch 90% → "[阈值信息已移除]"
- 72h 离线 → "[阈值信息已移除]"

## 5. Owner 信任监测（蓝图 §24.11 #64）

OwnerTrustGauge 三指标：
- **alert_response_time**: > 30min → COMPLACENT
- **manual_override_rate**: > 40% → CRITICALLY_LOW
- **alert_dismissal_rate**: > 30% → CRITICALLY_LOW

`weekly_gauge()`: 输出信任水平 + 建议。

## 6. 门禁植入

```
AI施工 → changed_files_check → [CodeEconomyAnalyzer.score()文件评分]
     → [ModuleBirthRegistry 若新增文件未注册 → reject]
     → [CoreIntegrityGuard 若IMMUTABLE_CORE清单文件被修改 → BLOCK]
     → contract_check → [contract_tester.py 所有ContractBus合约测试]
     → preset_pass → [代码风格检查]
     → regression_test → [全PASS才合入]
```

## 7. 深度硬规则（蓝图隐含约束）

| # | 硬规则 | 来源 |
|---|--------|------|
| 1 | **AI 不可知全阈值**: BlueprintAccessFilter 强制移除敏感数值，AI 知晓所有阈值 = 潜在越狱风险 | §24.9 #62 |
| 2 | **IMMUTABLE_CORE 清单**: kill_switch.py / error_budget_tracker.py / circuit_breaker.py / token_budget_tracker.py / graceful_shutdown.py / startup_guard.py —— 上述文件被 AI 修改 → BLOCK + Owner 双签 | §23.4 #52 |
| 3 | **出生即注册**: 任何 .py 文件被创建时必须调用 ModuleBirthRegistry.register_birth()，否则一周后被孤儿扫描标记 | §23.5 #54 |
| 4 | **蓝图-代码一致**: 代码中的关键阈值必须与蓝图 §23 中定义一致，不一致 → P0 | §24.3 #56 |
| 5 | **Owner 信任防漂移**: alert_dismissal_rate > 30% → CRITICALLY_LOW → 升级所有告警为 L3 | §24.11 #64 |

## 8. 验收标准

1. CodeEconomyAnalyzer 可检测过度拆分/过度设计（函数平均 < 5 行 + 类数 > 函数数）
2. ModuleBirthRegistry.register_birth 正确注册 + weekly_orphan_report 可发现未注册模块
3. CoreIntegrityGuard IMMUTABLE_CORE 清单文件被修改 → BLOCK
4. BlueprintCodeAuditor 检测到蓝图-代码数值不一致 → P0 告警
5. BlueprintAccessFilter 成功移除敏感阈值
6. OwnerTrustGauge alert_dismissal_rate > 30% → CRITICALLY_LOW
7. 门禁植入：全部 PASS 才合入
8. ruff 零错误 + mypy strict 通过