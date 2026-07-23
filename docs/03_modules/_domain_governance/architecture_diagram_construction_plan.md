---
module_id: GOV-ARCH-DIAGRAM-PLAN
title: 架构图施工蓝图
doc_type: blueprint
status: Active
version: 1.0.0
created: '2026-07-06'
last_updated: '2026-07-06'
ttl: permanent
description: |
  架构图生成器与检测器施工蓝图。统一登记 d5_architecture/generators/ 下所有生成器
  与检测器的施工计划、章节划分、依赖关系。
  被以下生成器/检测器在头部 [BLUEPRINT] 字段引用：
  - generate_dataflow_diagram.py (§dataflowgraph)
  - generate_decision_diagram.py (§decisiongraph)
  - align_panoramas.py (§panorama-alignment)
  - _common.py (§generator-common)
---

# 架构图施工蓝图 (ARCHITECTURE-DIAGRAM-PLAN)

## §generator-common

生成器公共工具。canonical = `scripts/governance/d5_architecture/generators/_common.py`。

提供 `cleanup_stale_files()`（治本"生成器只增不删"问题）+ `DB_DISPLAY_NAME` 常量。

## §dataflowgraph

数据流图生成器。canonical = `scripts/governance/d5_architecture/generators/generate_dataflow_diagram.py`。

从 dataflowgraph (PostgreSQL) 读取 Dataset/Job/Edge，生成 Mermaid 图 + 索引 MD。

依据：ARCH-051 裁定（2026-07-06）。

## §decisiongraph

决策流图生成器。canonical = `scripts/governance/d5_architecture/generators/generate_decision_diagram.py`。

从 decisiongraph (PostgreSQL) 读取 Layer/Node/Edge，生成 5 个 Mermaid 图（合并全景图/运营态子图/设计态子图/层级详情图/不变量图）+ 索引 MD。

依据：ARCH-052 裁定。

## §panorama-alignment

三图对齐检测器。canonical = `scripts/governance/d5_architecture/generators/align_panoramas.py`。

### 功能定位

只读检测器（不自动修复），从 depgraph/dataflowgraph/decisiongraph 三图读取节点，检测 4 类对齐问题：

1. **孤儿**（orphans）：仅在一图存在的 module_id
2. **状态漂移**（state_drifts）：同一 module_id 在不同图 design_maturity 不一致
3. **域不一致**（domain_mismatches）：同一 module_id 在不同图 domain_id 不一致
4. **设计态孤立**（design_only_in_one）：design 状态仅出现在一图，其它两图无对应

### 对齐 key

`module_id` 作为三图对齐 key：
- depgraph：使用 `blueprint_id` 派生（nodes.blueprint_id 字段）
- dataflowgraph：使用 `entity_name`（datasets）或 `job_name`（jobs）
- decisiongraph：使用 `module_id` 字段（decision_nodes + decision_layers）

**已知限制**：三图语义不同（depgraph 是模块 ID，dataflow 是实体名，decision 是模块 ID），是已知妥协。当前主要用于检测"完全孤立"的节点。

### 退出码（ERROR_CONTRACT）

- 0 = 成功（报告已生成，可能含问题）
- 1 = 错误（DB 连接失败/查询异常等）
- 2 = 三图任一为空（检测无意义，拒绝运行）

### 输出

`docs/02_enterprise_architecture/generated/panorama_alignment_report.md`

### 触发方式

manual 启动（[STARTUP] manual）。未来可考虑加入 GATE-ARCH-DIAGRAM _GENERATORS 列表实现自动重生。

### 依据

ARCH-053 裁定（2026-07-06）。

### 测试

`tests/test_align_panoramas.py`（20 个单元测试，覆盖 4 类检测逻辑 + 数据模型 + 异常 + 报告渲染）。
