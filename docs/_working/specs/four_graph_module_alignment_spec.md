# 四图模块对齐与全项目模块表 Spec

> **状态**：待审批
> **创建**：2026-07-09
> **作者**：架构师裁定（基于代码实际读取，非记忆推断）
> **关联**：trae_062 SSoT分类铁律、依赖关系先行铁律L1、100% AI开发事件驱动约束

---

## 1. 背景与问题

### 1.1 用户需求
1. **四图模块对齐**：在任一架构图添加设计态模块后，该模块自动在 depgraph / dataflowgraph / decisiongraph 三图写入、显示、对齐（位置、名字、编号一致）
2. **全项目模块表**：全项目所有模块有唯一编号、所属功能域、路径位置、状态（原型/运营/设计）、所属蓝图、功能简介（中英文）、全 py 文件清单，且与每个 py 表头对齐

### 1.2 现状根因（决定性证据）

| 问题 | 证据 | 影响 |
|------|------|------|
| 三图对齐key不统一 | [align_panoramas.py L60-64](../../../scripts/governance/d5_architecture/generators/align_panoramas.py#L60-L64)：depgraph用`blueprint_id`，dataflow用`entity_name`，decision用`module_id`。已知妥协 | 4451个孤儿（panorama_alignment_report.md） |
| dataflow/decision的module_id是软引用 | [dataflowgraph_schema.py L117](../../../src/zephyr/governance/persistence/dataflowgraph_schema.py#L117) `module_id TEXT`无FK；[decisiongraph_schema.py L198](../../../src/zephyr/governance/persistence/decisiongraph_schema.py#L198) 同样无FK | 可填入不存在的module_id，对齐无硬约束 |
| align_panoramas.py是只读检测器 | [architecture_diagram_construction_plan.md L50](../../../docs/02_enterprise_architecture/architecture_diagram_construction_plan.md#L50)："只读检测器（不自动修复）" | 不自动同步，只出报告 |
| 模块信息散落4处 | depgraph.nodes(4925文件) / blueprint_registry.yaml(55蓝图) / capability_canonical_file_registry.yaml(~45能力) / 蓝图frontmatter(55份) | 无单一模块查询入口 |
| 结构全景图不存在独立表 | 数据库只有depgraph/dataflowgraph/decisiongraph三组表，无structure_panorama表 | "结构全景图"=depgraph本身 |

### 1.3 根本矛盾
用户要"同一个模块在四图都能找到位置"，但三图连对齐key都不统一。这不是"缺功能"，是"地基裂缝"——对齐key不统一的前提下谈自动对齐，等于在流沙上盖楼。

---

## 2. 架构决策

### 2.1 Approach A：单SSoT模块表派生（已选定）

**核心原则**：depgraph.nodes 是模块元数据真源，dataflow/decision 用 module_id FK 引用 depgraph，保留各自实体数据。

**不是"其他图数据从depgraph派生"**，而是**"其他图用module_id挂靠depgraph，共享模块元数据，保留各自实体数据"**：

| 图 | 真源归属 | 挂靠方式 |
|------|------|------|
| depgraph.nodes | 模块元数据（ID/路径/域/状态/简介） | 本身就是真源 |
| dataflow_datasets/jobs | 自己的实体数据（dataset的schema/物理类型、job的trigger/运行上下文） | module_id字段FK到depgraph |
| decision_nodes/layers | 自己的实体数据（决策的inputs/outputs/conditions、层的频率/轨道） | module_id字段FK到depgraph |

### 2.2 为什么不是其他方案

| 方案 | 否决理由 |
|------|------|
| B. 各图独立维护+强检测 | 治标，不解决key不统一根因 |
| C. 新建统一modules表 | 多真源漂移，违反trae_062 |
| 严格1:1镜像 | 产生大量空壳记录（纯计算模块无dataflow实体，基础设施模块无decision节点），违反YAGNI |

### 2.3 SSoT合规性

- **架构数据真源在DB**（trae_062）：depgraph.nodes/nodes_metadata 在 PostgreSQL，符合
- **不新建YAML模块表**：避免多真源漂移
- **声明态 vs 实例态分离**：
  - 声明态（人声明的意图：priority/construction_progress）→ 蓝图frontmatter（真源）+ blueprint_registry.yaml（派生）
  - 实例态（代码实际状态：build_status/design_maturity）→ depgraph.nodes（真源）
  - 派生态（可从代码扫描：public_api）→ depgraph.nodes（自动填入）

---

## 3. 字段清单

### 3.1 必须补到 nodes_metadata（模块级，4个）

| 字段 | 类型 | 说明 | 填充方式 |
|------|------|------|------|
| module_name_cn | TEXT | 模块中文名 | apply_depgraph.py --update-module |
| module_name_en | TEXT | 模块英文名 | apply_depgraph.py --update-module |
| description_cn | TEXT | 功能简介（中文） | apply_depgraph.py --update-module |
| description_en | TEXT | 功能简介（英文） | apply_depgraph.py --update-module |

**存储约定**：模块级字段只在 blueprint_path 指向的蓝图文件那一行填写，其他文件行留空。查询时按 blueprint_id 聚合取 MAX/MIN。

### 3.2 补到 nodes 表（文件级，2个）

| 字段 | 类型 | 说明 | 填充方式 |
|------|------|------|------|
| entry_point | BOOLEAN | 是否模块入口文件 | apply_depgraph.py --mark-entry 手工标记，或约定`__init__.py` |
| public_api | TEXT | 对外API列表（逗号分隔） | generate_project_depgraph.py 从AST自动派生（扫描`__all__`或公共符号） |

**public_api 派生逻辑**：
- 扫描 .py 文件的 `__all__` 列表（优先）
- 无 `__all__` 时，扫描不以 `_` 开头的顶层 `def`/`class`/赋值语句
- 输出为逗号分隔字符串，如 `"ValueFactor,compute_value_factor,FACTOR_REGISTRY"`

### 3.3 不补到depgraph（声明态，JOIN蓝图获取）

| 字段 | 真源 | 获取方式 |
|------|------|------|
| priority | 蓝图frontmatter | JOIN blueprint_registry.yaml |
| construction_progress | 蓝图frontmatter | JOIN blueprint_registry.yaml |

**查询示例**：
```sql
SELECT n.*, nm.module_name_cn, nm.description_cn, bp.priority, bp.construction_progress
FROM nodes n
LEFT JOIN nodes_metadata nm ON n.path = nm.path
LEFT JOIN blueprint_registry bp ON n.blueprint_id = bp.module_id
```

---

## 4. 施工方案（5步）

### Step 1：统一对齐key（修bug）

**目标**：修复 align_panoramas.py 的 dataflow 对齐 key bug

**改动**：
- [align_panoramas.py](../../../scripts/governance/d5_architecture/generators/align_panoramas.py) L60-64：dataflow 对齐 key 从 `entity_name` 改为 `module_id`
- 回填 dataflow_datasets/jobs 的 module_id 字段（27个实体，对应 depgraph 中的 blueprint_id）

**验证**：孤儿数从 4451 骤降（dataflow 实体能匹配到 depgraph 模块）

### Step 2：FK硬引用（防幻觉）

**目标**：dataflow/decision 的 module_id 字段加 FK 到 depgraph.nodes.blueprint_id

**前置条件**：
- depgraph.nodes.blueprint_id 需加 UNIQUE 索引（`idx_nodes_blueprint_id_unique`）
- 注意：blueprint_id 允许 NULL（不是所有文件都归属模块）
- 注意：blueprint_id 可能有重复值（多文件同属一蓝图），UNIQUE 索引需用 `WHERE blueprint_id IS NOT NULL` 的部分索引，或在 FK 目标用独立视图

**DDL**：
```sql
-- dataflow_datasets
ALTER TABLE dataflow_datasets
  ADD CONSTRAINT fk_datasets_module_id
  FOREIGN KEY (module_id) REFERENCES nodes(blueprint_id)
  ON DELETE SET NULL;

-- dataflow_jobs
ALTER TABLE dataflow_jobs
  ADD CONSTRAINT fk_jobs_module_id
  FOREIGN KEY (module_id) REFERENCES nodes(blueprint_id)
  ON DELETE SET NULL;

-- decision_nodes
ALTER TABLE decision_nodes
  ADD CONSTRAINT fk_decision_nodes_module_id
  FOREIGN KEY (module_id) REFERENCES nodes(blueprint_id)
  ON DELETE SET NULL;

-- decision_layers
ALTER TABLE decision_layers
  ADD CONSTRAINT fk_decision_layers_module_id
  FOREIGN KEY (module_id) REFERENCES nodes(blueprint_id)
  ON DELETE SET NULL;
```

**逃生通道**：module_id 允许为 NULL（不是所有实体都归属模块）

### Step 3：补齐模块字段

**目标**：nodes_metadata 加 4 个模块级字段，nodes 表加 2 个文件级字段

**改动**：
1. [depgraph_schema.py](../../../src/zephyr/governance/depgraph_schema.py) _DDL_NODES 加 `entry_point BOOLEAN DEFAULT FALSE` 和 `public_api TEXT`
2. [depgraph_schema.py](../../../src/zephyr/governance/depgraph_schema.py) _DDL_NODES_METADATA 加 `module_name_cn TEXT` / `module_name_en TEXT` / `description_cn TEXT` / `description_en TEXT`
3. apply_depgraph.py 新增 `--update-module` 参数（写入模块级元数据）
4. apply_depgraph.py 新增 `--mark-entry` 参数（标记入口文件）
5. generate_project_depgraph.py 扩展 AST 扫描逻辑，自动填入 public_api

### Step 4：升级对齐为门禁（事件驱动）

**目标**：align_panoramas.py 从"manual只读检测"升级为 GitCommitGateway pre-commit 门禁

**改动**：
- 新增门禁 `GATE-PANORAMA-ALIGNMENT`（priority=830，在 GATE-MODULE-INVENTORY-SYNC 之后）
- 触发条件：commit 含 depgraph/dataflow/decision 相关变更
- 阻断条件：孤儿数 > 阈值（初始 100，可配置）或状态漂移 > 0
- 初期 warn-only，稳定后改 block

**符合100% AI开发事件驱动约束**（非常驻进程）

### Step 5：模块全景查询入口

**目标**：新增查询脚本，输入 module_id 输出三图所有记录

**改动**：
- 新增 `scripts/governance/query_module_panorama.py`
- 输入：module_id（MOD-XXX）
- 输出：蓝图frontmatter + 文件清单 + dataflow实体 + decision节点 + 能力索引
- 从 depgraph.nodes(文件级) GROUP BY blueprint_id 得到蓝图级模块表（55个）
- 这就是用户要的"全项目模块表"——一个查询入口，不是一张静态表

**输出格式**：
```
模块：MOD-FACTOR_ENGINE (因子引擎)
中文名：因子引擎
英文名：Factor Engine
简介：计算和存储各类因子的核心引擎
域：D_FACTOR
蓝图：docs/03_modules/factor_engine/blueprint.md
优先级：P0
进度：completed
状态：production

文件清单（50个）：
  [入口] src/zephyr/factor/engine.py
         src/zephyr/factor/registry.py
         ...

Dataflow实体（2个）：
  - dataset: factor.value_factor
  - job: compute.value_factor

Decision节点（3个）：
  - 因子合成
  - 质量检查
  - 衰减检测

能力索引（5个）：
  - factor_compute
  - factor_registry
  - ...
```

---

## 5. 验证方法

### 5.1 Step 1 验证
```bash
python scripts/governance/d5_architecture/generators/align_panoramas.py
# 预期：孤儿数从 4451 降至 < 1000
```

### 5.2 Step 2 验证
```sql
-- FK生效验证：尝试插入不存在的module_id应报错
INSERT INTO dataflow_datasets (entity_name, module_id, ...) VALUES ('test', 'MOD-NOT_EXIST', ...);
-- 预期：foreign key constraint failed
```

### 5.3 Step 3 验证
```bash
python -c "
from zephyr.governance.depgraph_schema import ensure_schema
ensure_schema()
print('schema OK')
"
# 预期：新字段创建成功
```

### 5.4 Step 4 验证
```bash
# 模拟不对齐提交，应被阻断
git add some_unaligned_change.py
git commit -m "test"
# 预期：GATE-PANORAMA-ALIGNMENT 阻断
```

### 5.5 Step 5 验证
```bash
python scripts/governance/query_module_panorama.py MOD-FACTOR_ENGINE
# 预期：输出完整模块全景
```

---

## 6. 风险与缓解

| 风险 | 缓解 |
|------|------|
| 加FK时现有数据有不合规module_id | 先跑Step1回填，再用--skip-refresh逃生通道分批修复，最后加FK |
| nodes.blueprint_id有重复值（多文件同属一蓝图） | FK用部分UNIQUE索引 `CREATE UNIQUE INDEX ... WHERE blueprint_id IS NOT NULL`，或FK指向blueprint_registry视图 |
| 门禁阻断影响开发效率 | 阈值可配置，初期warn-only，稳定后改block |
| public_api AST扫描性能 | 仅扫描entry_point标记的文件，非全量扫描 |
| nodes_metadata模块级字段存储约定（"主文件"行填） | apply_depgraph.py --update-module 自动定位blueprint_path行写入 |

---

## 7. 不做的事（YAGNI）

- **不新建YAML模块表**：违反trae_062
- **不新建独立modules表**：多真源漂移
- **不自动建空壳镜像**：不是所有模块都有dataflow/decision实体
- **不把priority/construction_progress存入depgraph**：声明态留蓝图frontmatter
- **不删除node_name/file_path冗余列**：历史遗留，单独清理任务

---

## 8. 审批要点

请确认以下决策：

1. **Approach A**（depgraph.nodes为模块真源，dataflow/decision用module_id FK挂靠）——已确认
2. **字段清单**（nodes_metadata加4字段，nodes表加2字段，priority/progress不进depgraph）——已确认
3. **5步施工顺序**（统一key → FK → 补字段 → 门禁 → 查询入口）——待确认
4. **门禁初期warn-only**——待确认
5. **public_api从AST派生**——待确认
