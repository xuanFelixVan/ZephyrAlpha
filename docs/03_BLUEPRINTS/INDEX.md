---
module_id: DOCS_03_BLUEPRINTS_INDEX
version: 1.1.0
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
layer: cross_layer
responsibility: 按 Layer 组织的蓝图目录索引（长期目标结构，与 docs/01_FRAMEWORK/ 过渡期并存）
---

# 蓝图按层目录（`docs/03_BLUEPRINTS/`）

> **定位**：长期目标结构——按 `L00`–`L11` 子目录存放迁移后的蓝图。
> **当前真源**：`docs/01_FRAMEWORK/`（过渡期，约 332 个蓝图仍在此处）。
> **迁移计划**：Pipeline B（蓝图安全流水线）Wave 2-3 完成后，蓝图将逐步迁移至本目录。
> **注意**：子目录命名使用旧版 Layer 标识（L00_INFRASTRUCTURE 等），与 MASTER_DEVELOPMENT_PLAN 中的 L00 数据基础设施等对应关系见下表。

## 已建子目录（12 个，已存在但多数为空）

| 子目录 | 对应 Phase 2 Layer | 当前蓝图数 | INDEX |
|--------|-------------------|------------|-------|
| [L00_INFRASTRUCTURE/](L00_INFRASTRUCTURE/INDEX.md) | L00 数据基础设施 | 0（迁移中） | [INDEX](L00_INFRASTRUCTURE/INDEX.md) |
| [L01_DATA_INGESTION/](L01_DATA_INGESTION/INDEX.md) | L01 数据处理 | 0（迁移中） | [INDEX](L01_DATA_INGESTION/INDEX.md) |
| [L02_DATA_PREPROCESSING/](L02_DATA_PREPROCESSING/INDEX.md) | L02 特征工程 | 0（迁移中） | [INDEX](L02_DATA_PREPROCESSING/INDEX.md) |
| [L03_FACTOR_ENGINE/](L03_FACTOR_ENGINE/INDEX.md) | L03 信号生成 | 0（迁移中） | [INDEX](L03_FACTOR_ENGINE/INDEX.md) |
| [L04_ML_MODELS/](L04_ML_MODELS/INDEX.md) | L04 风险管理 | 0（迁移中） | [INDEX](L04_ML_MODELS/INDEX.md) |
| [L05_SIGNAL_GENERATION/](L05_SIGNAL_GENERATION/INDEX.md) | L05 组合构建 | 0（迁移中） | [INDEX](L05_SIGNAL_GENERATION/INDEX.md) |
| [L06_PORTFOLIO_CONSTRUCTION/](L06_PORTFOLIO_CONSTRUCTION/INDEX.md) | L06 交易执行 | 0（迁移中） | [INDEX](L06_PORTFOLIO_CONSTRUCTION/INDEX.md) |
| [L07_RISK_MANAGEMENT/](L07_RISK_MANAGEMENT/INDEX.md) | L07 交易后分析 | 0（迁移中） | [INDEX](L07_RISK_MANAGEMENT/INDEX.md) |
| [L08_EXECUTION/](L08_EXECUTION/INDEX.md) | — | 0（迁移中） | [INDEX](L08_EXECUTION/INDEX.md) |
| [L09_MONITORING/](L09_MONITORING/INDEX.md) | — | 0（迁移中） | [INDEX](L09_MONITORING/INDEX.md) |
| [L10_HUMAN_AI_INTERFACE/](L10_HUMAN_AI_INTERFACE/INDEX.md) | — | 0（迁移中） | [INDEX](L10_HUMAN_AI_INTERFACE/INDEX.md) |
| [L11_GOVERNANCE_COMPLIANCE/](L11_GOVERNANCE_COMPLIANCE/INDEX.md) | — | 0（迁移中） | [INDEX](L11_GOVERNANCE_COMPLIANCE/INDEX.md) |

> **注**：上表"对应 Phase 2 Layer"列是近似对应关系，子目录命名体系与 MASTER_DEVELOPMENT_PLAN 命名体系的精确对齐由 ADR-010（目录编号重设计）决定，当前处于 PROPOSED 状态。

## 当前蓝图真源

在迁移完成之前，蓝图真源在：

```
docs/01_FRAMEWORK/           # ~332 个蓝图（过渡期真源）
docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/   # 部分重叠蓝图
```

查询蓝图：`docs/02_ARCHITECTURE/BLUEPRINT_DOMAIN_INVENTORY.yaml`（654 个蓝图注册表）

## 相关文档

- [subsystem-registry.yaml](../subsystem-registry.yaml) — 子系统目录登记
- [BLUEPRINT_DOMAIN_INVENTORY.yaml](../02_ARCHITECTURE/BLUEPRINT_DOMAIN_INVENTORY.yaml) — 654 个蓝图注册表
- [blueprint-lifecycle-standard.md](../01_GOVERNANCE/STANDARDS/blueprint-lifecycle-standard.md) — 蓝图生命周期标准
- [elimination-pipeline-tracker.yaml](../09_AUDIT/STATE/elimination-pipeline-tracker.yaml) — Pipeline B 迁移进度
