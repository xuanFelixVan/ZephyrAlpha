---
module_id: MOD-GOV-ALIGN-ALL
responsibility_domain: 
title: "五图对齐执行入口蓝图 — align_all.py 统一入口"
doc_type: blueprint
status: Active
version: "1.0.0"
ttl: permanent
layer: L1_foundation
layer_name: cross_layer
functional_domain: governance
design_maturity: production
build_status: production
arch_ref: "#ARCH-ALIGN-UNIFIED-001"
last_updated: "2026-08-08"
---

# 五图对齐执行入口蓝图 (align_all Blueprint)

> 裁定真源: `architecture_issue_registry.yaml` #ARCH-ALIGN-UNIFIED-001
> 规则真源: `trae_080_panorama_alignment.yaml` v1.1.0
> 代码真源: `scripts/governance/d5_architecture/generators/align_all.py`

## §main 功能定义

**align_all.py** 是五图对齐统一执行入口（ARCH-ALIGN-UNIFIED-001），一站式检测五图两轴对齐问题：

- **module_id 轴（图 1-4）**：调 `align_panoramas.run_alignment` 检测 depgraph/dataflowgraph/decisiongraph/blueprint.md 四类问题（孤儿/状态漂移/域不一致/设计态孤立）
- **step_id 轴（图 5）**：调 `align_battle_map.run_alignment` 检测 battle_map 七类问题（BM-INV-001~007）

### 强制力分层

| 级别 | 问题 | exit code |
|---|---|---:|
| 硬阻断 | domain_mismatches / ghost_anchors | 1 |
| 异常 | 任一检测器报错 | 2 |
| 软警告 | orphans / state_drifts / orphan_modules 等 | 0 + warn |

### 依赖关系

| 依赖模块 | node_id | 调用方式 |
|---|---:|---|
| align_panoramas | 9103502 | `run_alignment(write_report=False)` |
| align_battle_map | 9103326 | `run_alignment(write_report=False)` |
| _shared.constants | 9103792 | `EXIT_PASS / EXIT_FINDINGS / EXIT_ERROR` |

### 用法

```bash
# 施工前对齐验证（AGENTS.md RULE-DEPGRAPH 第三件事 Step 3）
python scripts/governance/d5_architecture/generators/align_all.py

# 仅检测不写报告（门禁场景）
python scripts/governance/d5_architecture/generators/align_all.py --no-report

# 自定义输出路径
python scripts/governance/d5_architecture/generators/align_all.py --output custom/overview.md
```

### 输出

- 总览报告：`docs/02_enterprise_architecture/03_governance_reports/panorama_alignment_overview.md`（派生产物，自动生成）
- exit code：0=通过 / 1=硬问题 / 2=异常

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-GOV-ALIGN-ALL`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-GOV-ALIGN-ALL` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-GOV-ALIGN-ALL` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-GOV-ALIGN-ALL | MOD-GOV-ALIGN-ALL | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
