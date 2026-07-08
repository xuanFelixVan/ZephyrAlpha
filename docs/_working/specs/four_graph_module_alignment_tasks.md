# 四图模块对齐 - 施工计划 Tasks

> **关联spec**：[four_graph_module_alignment_spec.md](./four_graph_module_alignment_spec.md)
> **创建**：2026-07-09
> **状态**：待执行

---

## 依赖关系

```
Step1(统一key) → Step2(FK) → Step3(补字段) → Step4(门禁) → Step5(查询入口)
```

Step1必须先完成（否则FK会因不合规module_id失败）。其余顺序执行。

---

## Step 1：统一对齐key（修bug）

### Task 1.1：修复 align_panoramas.py 对齐key
- **文件**：[scripts/governance/d5_architecture/generators/align_panoramas.py](../../../scripts/governance/d5_architecture/generators/align_panoramas.py)
- **改动**：L60-64，dataflow 对齐 key 从 `entity_name` 改为 `module_id`
- **验证**：脚本可正常运行无报错

### Task 1.2：回填 dataflow module_id 字段
- **文件**：dataflow_datasets表 / dataflow_jobs表（PostgreSQL）
- **改动**：27个实体的 module_id 字段回填为对应 depgraph 的 blueprint_id
- **工具**：apply_dataflowgraph.py 扩展回填逻辑，或SQL脚本
- **验证**：`SELECT COUNT(*) FROM dataflow_datasets WHERE module_id IS NOT NULL` ≥ 14

### Task 1.3：验证孤儿数下降
- **命令**：`python scripts/governance/d5_architecture/generators/align_panoramas.py`
- **预期**：孤儿数从 4451 降至 < 1000

---

## Step 2：FK硬引用（防幻觉）

### Task 2.1：nodes.blueprint_id 加 UNIQUE 部分索引
- **文件**：[src/zephyr/governance/depgraph_schema.py](../../../src/zephyr/governance/depgraph_schema.py)
- **DDL**：`CREATE UNIQUE INDEX IF NOT EXISTS idx_nodes_blueprint_id_unique ON nodes(blueprint_id) WHERE blueprint_id IS NOT NULL`
- **前置**：先检查是否有重复 blueprint_id 值，有则先清理
- **验证**：索引创建成功

### Task 2.2-2.5：四张表加FK
- **文件**：[dataflowgraph_schema.py](../../../src/zephyr/governance/persistence/dataflowgraph_schema.py) / [decisiongraph_schema.py](../../../src/zephyr/governance/persistence/decisiongraph_schema.py)
- **改动**：
  - dataflow_datasets.module_id → FK到nodes.blueprint_id
  - dataflow_jobs.module_id → FK到nodes.blueprint_id
  - decision_nodes.module_id → FK到nodes.blueprint_id
  - decision_layers.module_id → FK到nodes.blueprint_id
- **ON DELETE**：SET NULL
- **验证**：尝试INSERT不存在的module_id应报FK约束错误

---

## Step 3：补齐模块字段

### Task 3.1：nodes 表加2个文件级字段
- **文件**：[src/zephyr/governance/depgraph_schema.py](../../../src/zephyr/governance/depgraph_schema.py) _DDL_NODES
- **改动**：加 `entry_point BOOLEAN DEFAULT FALSE` 和 `public_api TEXT`
- **验证**：`ensure_schema()` 无报错

### Task 3.2：nodes_metadata 表加4个模块级字段
- **文件**：[src/zephyr/governance/depgraph_schema.py](../../../src/zephyr/governance/depgraph_schema.py) _DDL_NODES_METADATA
- **改动**：加 `module_name_cn TEXT` / `module_name_en TEXT` / `description_cn TEXT` / `description_en TEXT`
- **验证**：`ensure_schema()` 无报错

### Task 3.3：apply_depgraph.py 新增 --update-module
- **文件**：apply_depgraph.py
- **改动**：新增 `--update-module <module_id> --name-cn <中文名> --name-en <英文名> --desc-cn <中文简介> --desc-en <英文简介>` 参数
- **逻辑**：定位 blueprint_path 对应的 nodes_metadata 行，写入4个模块级字段
- **验证**：测试写入一个模块的中英文名和简介

### Task 3.4：apply_depgraph.py 新增 --mark-entry
- **文件**：apply_depgraph.py
- **改动**：新增 `--mark-entry <path>` 参数，设置 nodes.entry_point = TRUE
- **验证**：测试标记一个入口文件

### Task 3.5：generate_project_depgraph.py 扩展 public_api AST扫描
- **文件**：generate_project_depgraph.py
- **改动**：扫描 .py 文件的 `__all__`（优先）或顶层公共符号，填入 nodes.public_api
- **验证**：重新生成后，`SELECT path, public_api FROM nodes WHERE public_api IS NOT NULL LIMIT 5` 有结果

---

## Step 4：升级对齐为门禁（事件驱动）

### Task 4.1：新增 GATE-PANORAMA-ALIGNMENT 门禁
- **文件**：新增 `src/zephyr/governance/rule_enforcement/gate_panorama_alignment.py`
- **逻辑**：调用 align_panoramas.py 检测，孤儿数 > 100 或状态漂移 > 0 时告警
- **模式**：初期 warn-only（return warning，不阻断）
- **priority**：830

### Task 4.2：注册到 GitCommitGateway
- **文件**：GitCommitGateway 注册逻辑
- **改动**：将 GATE-PANORAMA-ALIGNMENT 加入 pre-commit 门禁链
- **触发条件**：commit 含 depgraph/dataflow/decision 相关文件变更
- **验证**：模拟提交含不对齐变更，应输出warn

### Task 4.3：登记 capability_canonical_file_registry.yaml
- **文件**：capability_canonical_file_registry.yaml
- **改动**：登记 GATE-PANORAMA-ALIGNMENT 的 capability 定义和 creation_tokens
- **验证**：capability反查可发现该门禁

---

## Step 5：模块全景查询入口

### Task 5.1：新增 query_module_panorama.py
- **文件**：新增 `scripts/governance/query_module_panorama.py`
- **输入**：module_id（MOD-XXX），或 --all 列出全部模块
- **输出**：蓝图frontmatter + 文件清单 + dataflow实体 + decision节点 + 能力索引
- **SQL**：
  ```sql
  SELECT n.*, nm.module_name_cn, nm.description_cn, bp.priority, bp.construction_progress
  FROM nodes n
  LEFT JOIN nodes_metadata nm ON n.path = nm.path
  LEFT JOIN blueprint_registry bp ON n.blueprint_id = bp.module_id
  WHERE n.blueprint_id = :module_id
  ```
- **验证**：`python scripts/governance/query_module_panorama.py MOD-FACTOR_ENGINE` 输出完整模块全景

### Task 5.2：--all 模式输出全项目模块表
- **改动**：`--all` 参数，GROUP BY blueprint_id 输出55个蓝图级模块的汇总表
- **输出**：模块ID / 中文名 / 域 / 状态 / 文件数 / 蓝图路径
- **验证**：`python scripts/governance/query_module_panorama.py --all` 输出55行模块表

---

## 完成标准

- [ ] Step1：孤儿数 < 1000
- [ ] Step2：4张表FK生效，INSERT不合规module_id报错
- [ ] Step3：6个新字段创建成功，--update-module/--mark-entry 可用
- [ ] Step4：GATE-PANORAMA-ALIGNMENT 门禁 warn 触发
- [ ] Step5：query_module_panorama.py --all 输出55个模块表
