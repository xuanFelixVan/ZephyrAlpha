---
module_id: 07_RESEARCH_INDEX
version: 1.0.1
status: Active
created_date: 2026-04-03
last_updated: '2026-04-11'
owner: 首席文档架构师
responsibility:
- 目录导航与文档索引管理与优化维护
standard_type: 专业量化机构索引文档
applicable_scope: 研究支持
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 活跃维护
layer: layer_07
---


# 研究支持目录索引

> **核心职责**: 目录导航和文档索引  
> **职责边界**:
> - ✅ 本文档负责：`docs/07_RESEARCH/` 下导航与子域门面入链
> - ❌ 本文档不负责：其他业务域规格正文的实质性改写

> **目录职责**: 研究环境配置、探索性分析、模式识别与实验追踪支持  
> **最后更新**: 2026-04-11

```
```---
```

## 上级与接力

- [docs 根索引](../INDEX.md)
- ~~[本目录 README（概述）]~~
- 全仓库文件治理任务清单 §7
- 治理工具总索引
- [09_AUDIT STATE 索引](../09_AUDIT/STATE/INDEX.md)

### 索引健全性与目录体量（P5 §7）

- **零入链扫描（最新）**：../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260503.md（`scan_index_health.py --prefix docs/07_RESEARCH --date 20260503`；**zero_inbound=0**；候选 md **18**；首轮子域 **`INDEX`/`README`** 与根 **`INDEX`** 零入链，已由 [`docs/INDEX.md`](../INDEX.md) 与本页**子域门面表**补链后复跑归零）
- **rollup（深度 3）**：../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260414.md（JSON 真源同 stem；键 `docs/07_RESEARCH` **18** 条路径）

```
```---
```

## 📁 子域门面（INDEX / README）

| 子域 | 索引 | 概述 |
|------|------|------|
| 01_ENVIRONMENT | ~~[INDEX.md]~~ | ~~[README.md]~~ |
| 02_EXPLORATORY_ANALYSIS | ~~[INDEX.md]~~ | ~~[README.md]~~ |
| 03_PATTERN_RECOGNITION | ~~[INDEX.md]~~ | ~~[README.md]~~ |
| 04_EXPERIMENT_TRACKING | ~~[INDEX.md]~~ | ~~[README.md]~~ |

```
```---
```

## 📁 目录结构（职责）

| 目录 | 职责 | 状态 |
|------|------|------|
| ~~[01_ENVIRONMENT/]~~ | 研究环境配置 | Active |
| ~~[02_EXPLORATORY_ANALYSIS/]~~ | 探索性分析工具 | Active |
| ~~[03_PATTERN_RECOGNITION/]~~ | 模式识别研究 | Active |
| ~~[04_EXPERIMENT_TRACKING/]~~ | 实验追踪 | Active |

```
```---
```

## 📄 根目录文档

| 文档 | 说明 |
|------|------|
| TECHNICAL_VALIDATION_PLAN.md | 技术验证计划 |
| EXPERIMENT_TRACKING.md | 实验追踪（根文档） |

```
```---
```

## 🧭 严格孤儿挂载（入口补齐）

> 只做索引挂载，不改正文。

- 相关性分析
- 研究报告生成器
- docker_setup
- statistical_tools
- candle_patterns

### 子域正文（补充入链）

| 子域 | 文档 |
|------|------|
| 02_EXPLORATORY_ANALYSIS | correlation_analysis.md · statistical_tools.md · research_report_generator.md |
| 03_PATTERN_RECOGNITION | candle_patterns.md |
| 04_EXPERIMENT_TRACKING | experiment_tracking.md |

```
```---
```

## 🔍 与其他目录的边界

### 与 09_RESEARCH_INNOVATION/ 的区别

| 维度 | 07_RESEARCH/ (本文档) | 09_RESEARCH_INNOVATION/ |
|------|----------------------|-------------------------|
| **定位** | 研究工具支持层 | Layer 9 研究战略层 |
| **内容** | 环境配置、分析工具、实验追踪 | AI研究实验室、创新孵化器 |
| **层级** | 基础设施层 | 架构层 (Layer 9) |
| **使用者** | 研究人员日常使用 | 系统架构设计参考 |
| **状态** | ✅ 已实现 | 🔄 规划中 |

**边界说明**:

- `07_RESEARCH/` 提供**研究工具和方法**（如何做研究）
- `09_RESEARCH_INNOVATION/` 定义**研究战略和架构**（研究体系设计）

## 🔗 相关链接

- **因子研究**: [../02_FACTOR_LIBRARY/01_STANDARDS/](../02_FACTOR_LIBRARY/01_STANDARDS/)
- **回测框架**: [../02_FACTOR_LIBRARY/05_BT_ENGINE/](../02_FACTOR_LIBRARY/05_BT_ENGINE/)
- **AI工作流**: [../10_AI_WORKFLOW/INDEX.md](../10_AI_WORKFLOW/INDEX.md)
- **研究战略层**: [../09_RESEARCH_INNOVATION/INDEX.md](../09_RESEARCH_INNOVATION/INDEX.md)

```
```---
```

*最后更新 2026-04-11*

<!-- orphan-link -->
- [experiment-tracking](experiment-tracking.md)

<!-- orphan-link -->
- [technical-validation-plan](technical-validation-plan.md)
