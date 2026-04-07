---
module_id: INDEX_07_RESEARCH
version: 1.0.0
status: Active
created_date: 2026-04-03
last_updated: 2026-04-03
owner: 首席文档架构�?standard_type: 专业量化机构索引
responsibility:
  - 索引文档、导航目录
applicable_scope: 研究支持
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 已完�?
---
---

# 研究支持目录索引
> **核心职责**: 目录导航和文档索引
> **职责边界**: 
> - ✅ 本文档负责：目录导航和文档索引相关内容
> - ❌ 本文档不负责：其他模块内容


> **目录职责**: 提供研究环境配置、探索性分析、实验追踪支�?
## 📁 目录结构

| 目录 | 职责 | 状�?|
|------|------|------|
| [01_ENVIRONMENT/](01_ENVIRONMENT/) | 研究环境配置 | Active |
| [02_EXPLORATORY_ANALYSIS/](02_EXPLORATORY_ANALYSIS/) | 探索性分析工�?| Active |
| [03_PATTERN_RECOGNITION/](03_PATTERN_RECOGNITION/) | 模式识别研究 | Active |
| [04_EXPERIMENT_TRACKING/](04_EXPERIMENT_TRACKING/) | 实验追踪 | Active |

## 📂 子目录详�?
### 01_ENVIRONMENT - 研究环境

| 文件 | 说明 |
|------|------|
| [README.md](API_README.md) | 环境说明 |
| [docker_setup.md](07_RESEARCH/01_ENVIRONMENT/docker_setup.md) | Docker配置 |

### 02_EXPLORATORY_ANALYSIS - 探索性分�?
| 文件 | 说明 |
|------|------|
| [README.md](API_README.md) | 分析工具说明 |
| [correlation_analysis.md](07_RESEARCH/02_EXPLORATORY_ANALYSIS/correlation_analysis.md) | 相关性分�?|
| [statistical_tools.md](07_RESEARCH/02_EXPLORATORY_ANALYSIS/statistical_tools.md) | 统计工具 |
| [research_report_generator.md](07_RESEARCH/02_EXPLORATORY_ANALYSIS/research_report_generator.md) | 研究报告生成�?|

### 03_PATTERN_RECOGNITION - 模式识别

| 文件 | 说明 |
|------|------|
| [README.md](API_README.md) | 模式识别说明 |
| [candle_patterns.md](07_RESEARCH/03_PATTERN_RECOGNITION/candle_patterns.md) | K线形态识�?|

### 04_EXPERIMENT_TRACKING - 实验追踪

| 文件 | 说明 |
|------|------|
| [BLUEPRINT.md](01_FRAMEWORK/ACCEPTANCE_CRITERIA_BLUEPRINT.md) | 实验追踪蓝图 |
| [experiment_tracking.md](07_RESEARCH/04_EXPERIMENT_TRACKING/experiment_tracking.md) | 实验追踪实现 |

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
- **回测框架**: [../02_FACTOR_LIBRARY/05_BACKTEST/](../02_FACTOR_LIBRARY/05_BACKTEST/)
- **AI工作流**: [../10_AI_WORKFLOW/INDEX.md](../10_AI_WORKFLOW/INDEX.md)
- **研究战略层**: [../09_RESEARCH_INNOVATION/INDEX.md](../09_RESEARCH_INNOVATION/INDEX.md)
---

*最后更�? 2026-04-03*

- [技术验证计�?](./TECHNICAL_VALIDATION_PLAN.md) - 系统文档
