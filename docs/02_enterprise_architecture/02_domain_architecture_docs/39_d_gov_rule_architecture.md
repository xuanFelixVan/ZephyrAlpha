---
doc_type: architecture_view
title: D-GOV_RULE 规则治理架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 39_d_gov_rule / 规则治理 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示规则治理（D-GOV_RULE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:20
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 规则治理（D-GOV_RULE）的模块分布。共 12 个模块 / 12 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (11 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   config/alert_rules.yaml  [production]                          │
│   config/budget_policy.yaml  [production]                        │
│   config/capacity/ai_context_policy.yaml  [production]           │
│   config/capacity/sandbox_policy.yaml  [production]              │
│   config/compression/policy.yaml  [production]                   │
│   config/context_rules.yaml  [production]                        │
│   config/context_rules_v1.yaml  [production]                     │
│   config/data/survivorship_policy.yaml  [production]             │
│   config/feature_activation_policy.yaml  [production]            │
│   src/zephyr/governance/constitutional_update/constitutional_... │
│   src/zephyr/governance/rule_engine.py  [production]             │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (1 modules)                 │
├──────────────────────────────────────────────────────────────────┤
│   F2-gate-engine/  [design]                                      │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 12 个模块 / 12 modules）。

### L1 基础层 / Foundation Layer (11 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | config/alert_rules.yaml | config/alert_rules.yaml | production | deprecated |
| 2 | config/budget_policy.yaml | config/budget_policy.yaml | production | deprecated |
| 3 | config/capacity/ai_context_policy.yaml | config/capacity/ai_context_policy.yaml | production | deprecated |
| 4 | config/capacity/sandbox_policy.yaml | config/capacity/sandbox_policy.yaml | production | deprecated |
| 5 | config/compression/policy.yaml | config/compression/policy.yaml | production | deprecated |
| 6 | config/context_rules.yaml | config/context_rules.yaml | production | deprecated |
| 7 | config/context_rules_v1.yaml | config/context_rules_v1.yaml | production | deprecated |
| 8 | config/data/survivorship_policy.yaml | config/data/survivorship_policy.yaml | production | deprecated |
| 9 | config/feature_activation_policy.yaml | config/feature_activation_policy.yaml | production | deprecated |
| 10 | src/zephyr/governance/constitutional_update/constitutiona... | src/zephyr/governance/constitutional_... | production | generated |
| 11 | src/zephyr/governance/rule_engine.py | src/zephyr/governance/rule_engine.py | production | generated |

### 未分类 / Unclassified (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | F2-gate-engine/ | F2-gate-engine/ | design | stable |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `39_d_gov_rule_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
