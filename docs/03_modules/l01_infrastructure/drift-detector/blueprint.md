---
module_id: "MOD-INF-023"
title: "漂移运行时检测蓝图 — Git-native Drift Detection + 自动对账"
doc_type: blueprint
status: draft
version: "0.2.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: not_started
summary: "ZephyrAlpha 漂移运行时检测蓝图——基于 git diff + YAML 对比的运行时漂移检测。整合现有 80+ 治理脚本为运行时检测 + 自动对账（可自动修复的漂移自动修，不可自动修复的生成修复建议）。对标 Terraform drift detection + K8s reconciliation loop。"
tags: [drift-detection, reconciliation, runtime-check, consistency, git-native, infrastructure]
priority: P1
depends_on:
  - {target: "MOD-INF-007", at: "§5", why: "Gate Engine——漂移检测作为 G1 门禁的增强"}
  - {target: "MOD-INF-020", at: "§2", why: "Audit Trail——漂移事件写入审计日志"}
  - {target: "MOD-INF-021", at: "§2", why: "Rollback——漂移修复失败时自动回滚"}
---

# 漂移运行时检测蓝图 — Git-native Drift Detection

> **module_id**: MOD-INF-023 | **version**: 0.2.0 | **status**: draft | **layer**: cross_layer

> **对标**：Terraform drift detection（`terraform plan -detailed-exitcode`）+ K8s controller reconciliation loop + OpenAPI spec:lint。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-023 |
| 代码落位 | `src/zephyr/drift_detector/` |
| 运行时平面 | Warm memory（git commit 后触发 + 定期轮询） |
| 核心职责 | 检测"蓝图声明"与"代码实际"的偏差——持续对账，自动修复 |

### 1.2 核心职能（一句话）

**Drift Detector 是系统的质检员**——基于 git diff 持续检查蓝图与代码的一致性，能自动修的自动修，不能的生成修复建议。

### 1.3 运行场景约束

| 约束 | 影响 |
|------|------|
| 先干后验模式 | 漂移检测是后验的核心组件——AI 先干，drift detector 后验 |
| 80+ 现有治理脚本 | 不重写，整合为运行时检测的检测器 |
| 能自动绝不人工 | 可自动修复的漂移自动修，不可自动修复的生成修复建议 |

---

## 2. 核心架构

### 2.1 整合现有脚本为运行时检测器（决策 D-023-01）

> **决策 D-023-01**：不重写检测逻辑，将现有 80+ 治理脚本整合为 drift detector 的检测器。每个治理脚本就是一个 drift detector，drift detector 负责调度和汇总。
>
> **决策依据**：80+ 脚本已经覆盖了大部分漂移检测场景，重写是浪费。整合为统一调度即可。

```yaml
detector_integration:
  existing_scripts:
    - script: "validate_blueprint_code_sync.py"
      drift_dimension: "blueprint_code_sync"
      severity: HIGH

    - script: "validate_code_yaml_alignment.py"
      drift_dimension: "yaml_disk_sync"
      severity: MEDIUM

    - script: "validate_blueprint_registry.py"
      drift_dimension: "registry_consistency"
      severity: MEDIUM

    - script: "validate_blueprint_overlap.py"
      drift_dimension: "blueprint_overlap"
      severity: LOW

  new_detectors:
    - detector: "contract_implementation_detector"
      drift_dimension: "contract_implementation"
      severity: HIGH
      method: "AST 级对比——蓝图 §3 接口 vs 代码实际接口"
      status: "待实现"
```

### 2.2 自动对账策略（决策 D-023-02）

> **决策 D-023-02**：漂移检测后自动对账——可自动修复的漂移自动修（如 YAML 路径索引更新），不可自动修复的生成修复建议。自动修复失败则触发 auto-rollback。
>
> **决策依据**：与先干后验模式一致。能自动绝不人工。

```yaml
reconciliation_strategy:
  auto_fixable:
    description: "可自动修复的漂移——脚本自动修复"
    examples:
      - "蓝图 §5 路径索引与磁盘不一致 → 自动更新路径索引"
      - "YAML 注册表缺少新模块 → 自动追加条目"
      - "blueprint-registry.yaml 统计数字不准 → 自动重新计算"
    action: "自动修复 → 审计日志记录 → 通知 Owner（异步）"

  needs_suggestion:
    description: "不可自动修复的漂移——生成修复建议"
    examples:
      - "蓝图 §3 接口与代码实际接口不一致 → 生成 diff 报告"
      - "蓝图缺失 §6-§13 → 生成待补全提醒"
    action: "生成修复建议 → 审计日志记录 → 通知 Owner（异步）"

  auto_fix_failed:
    description: "自动修复失败 → 触发 auto-rollback"
    action: "回滚修复操作 → 审计日志记录 → 通知 Owner（异步）"
```

### 2.3 检测触发策略

```yaml
triggers:
  post_commit:
    description: "git commit 后自动触发——检测本次 commit 引入的漂移"
    scope: "受影响模块"
    latency: "< 10s"

  periodic:
    description: "每 30 分钟全局扫描一次"
    scope: "global"
    note: "轻量级——仅跑 HIGH severity 检测器"

  on_demand:
    description: "MCP Tool call / Owner 手动触发"
    scope: "指定范围"
    note: "全量——跑所有检测器"
```

---

## 3. 文件组成

| 文件 | 职责 |
|------|------|
| `drift_detector.py` | 漂移检测引擎——调度现有治理脚本 + 汇总结果 |
| `reconciler.py` | 自动对账器——可自动修复的漂移自动修 |
| `drift_report.py` | 漂移报告模型——DriftReport + 修复建议 |

---

## 4. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| scaffold | 整合现有脚本为检测器 + DriftReport 模型 + post-commit 触发 | 📋 Backlog |
| experimental | 自动对账 + 契约-代码 AST 对比 + 审计闭环 | 📋 Backlog |
| beta | 漂移趋势分析 + 预测性告警 | 📋 Backlog |

---

## 决策记录

| 决策 ID | 决策内容 | 日期 | 依据 |
|---------|---------|------|------|
| D-023-01 | 整合现有 80+ 脚本为检测器，不重写 | 2026-05-05 | 80+ 脚本已覆盖大部分场景，重写是浪费 |
| D-023-02 | 自动对账——可自动修的自动修，不能的生成建议 | 2026-05-05 | 与先干后验一致，能自动绝不人工 |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-05 | 0.2.0 | 两项决策写入：D-023-01 整合现有脚本 + D-023-02 自动对账 |
| 2026-05-05 | 0.1.0 | 初始创建——漂移检测维度 + 对账循环 + 触发策略 |
