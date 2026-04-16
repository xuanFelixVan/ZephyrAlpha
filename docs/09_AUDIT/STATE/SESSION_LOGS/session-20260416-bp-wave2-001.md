---
session_id: session-20260416-bp-wave2-001
date: 2026-04-16
session_type: BP Wave 2 (蓝图安全流水线) - 重叠蓝图去重
executor: ZephyrAlpha-Trae
---

# Session Log: BP Wave 2 - 01_FRAMEWORK 与 05_IMPLEMENTATION 重叠蓝图去重 (第一批)

## 任务摘要
启动蓝图安全流水线 BP Wave 2，识别并处理 docs/01_FRAMEWORK/ 与 docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/ 之间的重叠蓝图文件。

## 完成的任务列表

### 1. 目录扫描与重叠识别
扫描两个目录识别功能重叠的蓝图文件：
- `docs/01_FRAMEWORK/` - 约200+ 个蓝图文件
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/` - 约163个蓝图文件

### 2. 文件对比与评估

#### 数据质量相关文件对比
| 文件 | 位置 | 评估 | 决策 |
|------|------|------|------|
| data-quality-management-blueprint.md | 01_FRAMEWORK | ⭐⭐⭐⭐⭐ 最完整，含执行摘要、价值评估 | **保留** |
| data-quality-monitoring-blueprint.md | 05_IMPLEMENTATION | ⭐⭐ 较简短，仅监控功能 | **归档** |
| data-quality-enhanced-blueprint.md | 05_IMPLEMENTATION | ⭐⭐⭐ 中等长度，增强版检查 | **归档** |

#### 风险预算相关文件对比
| 文件 | 位置 | 评估 | 决策 |
|------|------|------|------|
| dynamic-risk-budgeting-blueprint.md | 01_FRAMEWORK | ⭐⭐ 较简短，仅基础内容 | **归档** |
| risk-control-blueprint.md | 05_IMPLEMENTATION | ⭐⭐ 较简短，基础内容 | **归档** |
| hierarchical-risk-budget-blueprint.md | 05_IMPLEMENTATION | ⭐⭐⭐⭐⭐ 最完整，含接口规范 | **保留** |

### 3. 执行的去重操作

#### 归档的文件 (5个)
使用 `git mv` 移动到 docs/06_ARCHIVE/：
1. `bp-archived-20260416-data-quality-monitoring-blueprint.md` (来自 05_IMPLEMENTATION)
2. `bp-archived-20260416-data-quality-enhanced-blueprint.md` (来自 05_IMPLEMENTATION)
3. `bp-archived-20260416-dynamic-risk-budgeting-blueprint.md` (来自 01_FRAMEWORK)
4. `bp-archived-20260416-risk-control-blueprint.md` (来自 05_IMPLEMENTATION)

#### 保留的文件 (2个)
- `docs/01_FRAMEWORK/data-quality-management-blueprint.md` - 数据质量主蓝图
- `docs/05_IMPLEMENTATION/.../hierarchical-risk-budget-blueprint.md` - 风险预算主蓝图

### 4. 注册表更新
- 更新 BLUEPRINT_DOMAIN_INVENTORY.yaml：5个条目的 status 和 path
  - 5个条目：status → ARCHIVED, path → 更新为归档路径
- 更新 elimination-pipeline-tracker.yaml：
  - bp_wave_2.status: in_progress
  - files_processed: 5
  - files_deduplicated: 5
  - started_date: 2026-04-16
  - 添加 session log 条目

## 关键决策
1. **保留标准**：选择内容最完整、包含接口规范、有详细设计决策的版本
2. **归档标准**：功能被主蓝图覆盖、内容较少、缺少技术规格的文件
3. **不删除**：所有归档文件保留在 docs/06_ARCHIVE/，便于追溯

## BP Wave 2 进度
- 预估文件数: 163
- 已处理: 5
- 剩余: 约158个文件待评估
- 进度: 3%

## 下步建议
1. 继续识别功能重叠的蓝图组（如 portfolio-optimization、backtest、alpha-factor 等）
2. 每组对比内容完整性，保留最全面的版本
3. 预计需要 20-30 个 session 完成 BP Wave 2

## 文件变更汇总
| 操作类型 | 数量 | 详情 |
|----------|------|------|
| 归档 | 5 | git mv 到 docs/06_ARCHIVE/ |
| 保留 | 2 | 主蓝图文件 |
| 注册表更新 | 2 | BLUEPRINT_DOMAIN_INVENTORY.yaml, elimination-pipeline-tracker.yaml |
