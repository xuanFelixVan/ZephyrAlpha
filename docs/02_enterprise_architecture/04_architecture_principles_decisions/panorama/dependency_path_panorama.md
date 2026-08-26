---
ttl: permanent
doc_type: architecture_view
---

# 依赖与路径全景图能力定位书

> 版本：V6.0 | 2026-07-30
> 读者：项目 Owner（主要）+ AI 开发 Agent（次要）
> 写法：大白话为主。变更历史见 git log。本文档只保留当前有效的设计规格和裁定结论。

> **文档责任范围**：本文档定义**依赖与路径全景图**（depgraph + 生成器）的能力定位、设计决策和裁定记录。
> 合并后覆盖：依赖全景图（dep_ 表组，管"谁依赖谁"）+ 路径全景图（arch_ 表组，管"放在哪"）+ 设计规则缓存表（domains/contracts 等）。
> 不包含：施工步骤和问题清单（见 archive/depgraph_issue_registry.md）、架构升级项目导航（见 architecture_upgrade_discussion.md）、生成器技术问题清单（见 generator_issues.md）。

> **数据源**：全景图数据库为 PostgreSQL 16，数据库名 `depgraph`（与 SQLite 物理文件 `depgraph.db` 区分）。PostgreSQL 特性：IDENTITY 列自增主键、MVCC 行级锁、`NOT VALID` 延迟校验 + `VALIDATE CONSTRAINT`。

---

## 一、依赖与路径全景图是什么？（一句话）

**依赖与路径全景图是整个项目的最大蓝图，记录"规划中应该依赖什么、放在哪"和"代码里实际依赖什么、放在哪"。**

它存在数据库里（`depgraph`），不是一张图片，不是一份文档。里面写清楚了：这个项目有多少个功能域、每个功能域有多少个模块、模块和模块之间怎么依赖、每个文件放在哪个目录属于哪个域、哪些模块造好了、哪些还没造。

**两个职责合一**：
- **依赖全景图**（dep_ 表组）：管"谁依赖谁"——模块间的 import 关系
- **路径全景图**（arch_ 表组）：管"放在哪"——文件/目录的物理位置和域归属

两者同库不同表组，共享 domains 表外键，合并为一份能力定位书。

---

## 二、它解决什么问题？

它解决 AI 开发的四个老毛病：

| 毛病 | 全景图怎么治 |
|------|------------|
| **AI 幻觉** — AI 自己编模块 | AI 动手之前必须先查：这个模块在不在图里？不在 → 不能造 |
| **AI 漂移** — 做着做着就跑偏 | 每次改代码都要和全景图对齐。图没变，代码不准变 |
| **局部最优** — AI 只看眼前 | AI 一眼看到整个项目的依赖关系网。改一个模块之前知道会影响谁 |
| **位置漂移** — AI 把文件放错地方 | AI 建文件前必须先查：这个路径属于哪个域？域容量还够吗？位置和蓝图一致吗？ |

**本质**：让 AI 从"凭感觉瞎猜"变成"照着地图走路"。

---

## 三、它不是什么？（边界要画清楚）

全景图只管两件事——**定义模块依赖关系**和**记录文件物理位置**。

| 不是这个 | 为什么不是 |
|---------|-----------|
| UML 图 | UML 画的是类和方法的关系，全景图画的是模块和模块的关系，层级更高 |
| 数据库表结构 | 那是具体实现，全景图只管"有这个模块"，不管模块里面怎么实现 |
| 微服务架构图 | 全景图不关心部署在哪台机器上 |
| 项目管理工具 | 全景图不管排期和任务分配 |
| 代码文档 | 全景图不记录函数签名和 API 参数 |

以上这些东西，全景图都不管。它们可以单独存在，但必须以全景图为基准。

---

## 四、它由哪几部分组成？

依赖与路径全景图由三部分组成，共同存在 `depgraph` 里：

### 4.1 依赖全景（nodes + edges）

两张表：

| 表 | 存什么 | 例子 |
|----|--------|------|
| `nodes` | 所有代码制品（8 种 node_type：module/package/script/test/config/schema/doc_template/data_template） | 订单中心、风控引擎、行情网关 |
| `edges` | 制品之间的依赖关系 | 订单中心 → 依赖 → 风控引擎 |

**目前规模**：运营态 6,003 个节点（production 6,003）+ 设计态 89 个 = 6,092 个节点 [ARCH-MM-002: prototype 已归入 production]，53 个功能域，运营态 6,084 条 + 设计态 113 条依赖边。（2026-06-30 查询 depgraph (PostgreSQL)）

### 4.2 架构全景（arch_ 表组 3 张表，v6 合并 arch_domain_layers/arch_domain_capacity 入 domains 表，v14 删除 arch_layers/arch_bottlenecks 后）

| 表 | 存什么 | 例子 |
|----|--------|------|
| `arch_directory_tree` | 目录树（所有文件/目录的物理位置） | src/zephyr/trading/order_center/main.py |
| `arch_path_mappings` | 路径→域映射规则 | src/zephyr/trading/ → D_TRADING |
| `arch_constraints` | 架构约束（跨域违规等） | D_TRADING → D-INFRA 违规 |

> **v6 合并说明**：原 `arch_domain_layers`（域→层映射）和 `arch_domain_capacity`（域容量上限）已在 v6 合并入 `domains` 表（layer_id/max_modules/current_modules 列），不再作为独立表存在。

### 4.3 设计规则缓存表（5 张表，v14 删除 invariants 后）

| 表 | 存什么 | 两个全景图怎么共享 |
|----|--------|----------------|
| `domains` | 功能域定义 | nodes.domain_id + arch_directory_tree.domain_id 共同外键 |
| `contracts` | 契约定义（基础字段共享，扩展字段 P0-6 管理） | edges.api_contract_refs 引用 |
| `domain_events` | 领域事件 | edges.event_ref 引用 |
| `domain_dependencies` | 域间依赖声明 | arch_constraints 跨域检测引用 |
| `rule_bindings` | 规则绑定 | 门禁检查引用 |

### 4.4 表归属矩阵（当前 25 张表 + 1 业务视图 dep_cycles；v14 删除 arch_layers/arch_bottlenecks/invariants，v6 合并 arch_domain_layers/arch_domain_capacity 入 domains，v15 删除 dead columns，v18 新增 blueprint_id CHECK 触发器；系统表 _schema_version 由 PG schema 脚本一次性填充，PostgreSQL IDENTITY 列内部序列自动维护）

| 管理方 | 表 | 生成器每次运行会怎样 | AI能手动改吗 |
|--------|---|---------------------|:---:|
| **生成器管理** | nodes（运营态字段） | DELETE+INSERT（`WHERE design_maturity != 'design' OR design_maturity IS NULL`） | ❌ 禁止，会被覆盖 |
| | nodes（设计态字段） | 保留不动 | ✅ 可以（通过 apply_depgraph.py 写入） |
| | edges（active 字段） | DELETE+INSERT（`WHERE dep_maturity != 'design' OR dep_maturity IS NULL`） | ❌ 禁止，会被覆盖 |
| | edges（design 字段） | 保留不动 | ✅ 可以（通过 apply_depgraph.py 写入） |
| | domains | 不DELETE，只UPDATE current_modules | ✅ 可以改domain_name/layer_id/max_modules等（v6 合并原 arch_domain_layers/arch_domain_capacity 入此表）；P0-6 扩展的 modification_permission 字段 ❌ 禁止（YAML 真源，由 sync 脚本写入） |
| **path_tree 管理** | arch_directory_tree（运营态） | 不碰（由 path_tree 脚本独立管理，V5.5 裁定） | ❌ 禁止，会被 path_tree 覆盖 |
| | arch_directory_tree（设计态） | 不碰（`WHERE design_maturity='design'`） | ⚠️ 通过 sync 脚本写入（YAML 派生，如 sync_directory_registry） |
| **脚本管理** | arch_constraints | 不碰（VR规则由sync_yaml_to_depgraph.py同步；audit_domain_nodes.py已归档，4类检测职责待恢复） | ⚠️ 只能通过脚本改 |
| **P0-6 字段扩展（YAML→DB，约定保护）** | nodes（+5 字段：business_stream/stream_role/runtime_plane/ddd_aggregate/provided_interfaces，#165-169；~~**v15已删此5字段**，见§迁移说明后v15裁定~~） | 生成器只填充运营态字段，不碰这 5 个扩展字段 | ❌ 禁止（YAML 真源，由 sync 脚本覆盖；无字段级只读触发器，依赖 sync 脚本每次运行覆盖） |
| | edges（+3 字段：valid_since/migration_status/is_legal_cycle，#152；~~**migration_status v15已删**，见§迁移说明后v15裁定~~） | 生成器只填充运营态字段，不碰这 3 个扩展字段 | ❌ 禁止（同上；migration_status 由 sync 脚本根据 YAML 迁移状态写入） |
| | domains（+1 字段：modification_permission，#156） | 生成器不碰此字段 | ❌ 禁止（同上；YAML ai_autonomy → DB modification_permission 映射） |
| | contracts（基础字段 7 列：contract_id/name/provider_domain/consumer_domain/contract_type/schema_definition/version + P0-6 扩展 6 字段：promise/actual_consumer/fulfillment_status/gap/target_phase/last_reviewed，共 13 列） | 生成器不碰此表 | ❌ 禁止（YAML 真源，基础字段由 sync_contract_mapping_table 写入，扩展字段由 sync_declarative_contract_tracker 写入） |
| **sync 脚本管理（P0-6 新增，YAML→DB 只读缓存）** | gates | 不碰（由sync_yaml_to_depgraph.py写入，只读触发器保护） | ❌ 禁止（只读触发器，YAML 是唯一真源） |
| | field_vocabularies | 不碰（同上） | ❌ 禁止 |
| | registries | 不碰（同上） | ❌ 禁止 |
| | cross_registry_rules | 不碰（同上） | ❌ 禁止 |
| | infrastructure_components | 不碰（同上） | ❌ 禁止 |
| | model_capabilities | 不碰（同上） | ❌ 禁止 |
| | hard_boundaries | 不碰（同上） | ❌ 禁止 |
| | business_streams | 不碰（同上） | ❌ 禁止 |
| | blueprint_links | 不碰（数据源为 nodes 表派生，非 YAML；由 sync_blueprint_links 从 nodes.blueprint_id 派生） | ❌ 禁止（只读触发器保护） |
| **人工/蓝图管理** | arch_path_mappings | 不碰 | ✅ 可以 |
| | domain_events | 不碰 | ✅ 可以 |
| | domain_dependencies | 不碰 | ✅ 可以 |
| | rule_bindings | 不碰 | ✅ 可以 |

### 4.5 生成器（generate_project_depgraph.py）

生成器是把物理世界的文件"翻译"到全景图的桥梁。它同时管依赖全景图（扫描 import）和路径全景图（扫描文件系统目录树）。

**它做的事（V3.2 合并后 12 步完整流程，V5.5 裁定：arch_directory_tree 由 path_tree 独立管理，生成器不再处理）**：
1. 获取 PostgreSQL MVCC 行级锁（G-Blind-6 修复，PG 无需文件级写锁）
2. 加载设计态数据（nodes WHERE design_maturity='design' + edges WHERE dep_maturity='design'）→ 存到内存
3. DELETE 运营态数据（nodes WHERE design_maturity != 'design' OR design_maturity IS NULL + edges WHERE dep_maturity != 'design' OR dep_maturity IS NULL）
4. 扫描 15 个白名单目录（§14.8，裁定#186 移除 tests/）
5. 生成运营态数据（nodes + edges 的 import 依赖）
6. 合并设计态数据（从内存恢复），设计态字段保留不动
7. 冲突时设计态优先（SSoT 分层：设计态全景图 > 代码）
8. 校验 blueprint_id 存在性（D-Blind-3 修复）
9. 检测循环依赖（Tarjan SCC），输出循环报告（D-Blind-1 修复）
10. 调用 audit_domain_nodes.py 写入 arch_constraints（A-Blind-5 修复）（已归档到 _archive/prototype/，4类检测职责待恢复）
11. 输出执行报告（G-Blind-5 修复，§14.10 格式）
12. 释放锁（PG 事务结束自动释放行锁）

**它不做的**：
- 不创造设计态模块（设计态必须来自用户输入，生成器不碰）
- 不删除设计态节点和 design edge
- 不修改蓝图（蓝图是设计态派生物，生成器只管运营态对齐）
- 不碰人工管理的表（arch_path_mappings 等）
- 不处理 arch_directory_tree（由 path_tree 脚本独立管理，V5.5 裁定）

---

## 路径全景图能力定位（§5-§11）

> 路径全景图管"放在哪"，依赖全景图管"谁依赖谁"。两者同库不同表组，共享 domains 表外键。

---

## 五、路径全景图是什么？（一句话）

**路径全景图是项目的"物理地图"**——记录每个文件/目录放在哪、属于哪个域、什么状态。

它回答 AI 的三个问题：
1. 这个路径属于哪个功能域？（arch_directory_tree.domain_id）
2. 这个域的容量上限是多少？（domains.max_modules）
3. 这个路径的架构约束是什么？（arch_constraints）

**与依赖全景图的区别**：

| 维度 | 依赖全景图（nodes/edges） | 路径全景图（arch_ 表组） |
|------|-------------------------|------------------------|
| 管什么 | 谁依赖谁（import 关系） | 放在哪（物理位置） |
| 粒度 | 模块级（功能级+文件级） | 文件级+目录级 |
| 覆盖范围 | 有 import 依赖的代码节点 | 所有文件（包括文档/数据/模板） |
| 生成方式 | 扫描 import 语句 | 扫描文件系统目录树 |
| 消费者 | AI 改代码时查依赖 | AI 建文件时查归属 |

---

## 六、路径全景图的 3 张表（v6 合并 arch_domain_layers/arch_domain_capacity 入 domains 表，v14 删除 arch_layers/arch_bottlenecks 后）

| # | 表名 | 职责 | 管理方 | 生成器行为 |
|---|------|------|--------|-----------|
| 1 | `arch_directory_tree` | 目录树（所有文件/目录的物理位置） | path_tree | 不碰（由 path_tree 脚本独立管理，V5.5 裁定） |
| 2 | `arch_path_mappings` | 路径→域映射规则 | 人工 | 不碰 |
| 3 | `arch_constraints` | 架构约束（跨域违规等） | sync_yaml_to_depgraph.py | 不碰（脚本写） |

> **域→层映射和域容量**：原 `arch_domain_layers`（域→层映射）和 `arch_domain_capacity`（max_modules）在 v6 合并入 `domains` 表（layer_id/max_modules/current_modules 列，共 15 列）。

---

## 七、两个全景图的协同协议

### 7.1 SSoT 分层

| 数据 | SSoT | 消费方 |
|------|------|--------|
| 物理路径 path | **arch_directory_tree.path**（路径全景图） | nodes.path 外键引用 |
| 域归属 domain_id | **domains 表**（设计规则缓存表） | nodes + arch_directory_tree 共同外键 |
| 模块依赖 | **edges 表**（依赖全景图） | arch_constraints 引用 |
| 容量上限 | **domains.max_modules**（v6 合并自 arch_domain_capacity） | 门禁检查引用 |

### 7.2 外键约束（V3.3 E15 修正：单向外键）

```
nodes.path → arch_directory_tree.path（单向：nodes.path 必须在 arch_directory_tree 中存在）
nodes.domain_id → domains.domain_id（必须存在）
edges.from_node_id → nodes.node_id（必须存在，V3.4 后）
edges.to_node_id → nodes.node_id（必须存在，V3.4 后）
arch_directory_tree.domain_id → domains.domain_id（必须存在，A-Blind-3 修复后非空）
```

**单向约束说明**（V3.3 E15 修正）：
- `nodes.path` 必须在 `arch_directory_tree` 中存在（运营态节点必须有物理位置）
- 反向不要求：`arch_directory_tree` 中的 path 不一定在 `nodes` 中（文档/数据/模板节点不在 nodes 表）
- 这是因为路径全景图覆盖所有文件，依赖全景图只覆盖有 import 依赖的代码节点
- **迁移期注意**：详见 §12.3 迁移期统一说明

### 7.3 同步协议

| 场景 | 谁先写 | 谁后同步 |
|------|--------|---------|
| 新建文件 | path_tree 扫描 → arch_directory_tree 先有 | 生成器扫描 → nodes 后有 |
| 删除文件 | path_tree 扫描 → arch_directory_tree 先删 | 生成器扫描 → nodes 后删 |
| 移动文件 | path_tree 扫描 → arch_directory_tree 更新 path | 生成器扫描 → nodes 更新 path（node_id 不变，因 node_id 与 path 解耦） |
| 新建设计态节点 | apply_depgraph.py → nodes 先有 | arch_directory_tree 后有（path_tree 下次运行，运营态记录）；设计态 arch_directory_tree 由 sync 脚本写入 |

**移动文件说明**（V3.3 修正）：node_id 与 path 解耦后，移动文件时 node_id 保持不变，只更新 path 字段。edges 表的 from_node_id/to_node_id 无需变更（引用 node_id 而非 path）。

### 7.4 冲突解决

| 冲突场景 | 解决规则 |
|---------|---------|
| nodes.path 在 arch_directory_tree 中不存在 | 生成器报警告（path 校验失败，节点无物理位置） |
| nodes.blueprint_id 在蓝图中不存在 | 生成器标记 `blueprint_id_invalid=1`（V3.4 新增字段，表示 blueprint_id 校验失败）。详见 §12.3 迁移期统一说明 |
| arch_directory_tree 有 path 但 nodes 没有 | 正常（文档/数据/模板节点不在 nodes 中） |
| domain_id 在 nodes 和 arch_directory_tree 不一致 | 以 arch_directory_tree 为准（路径全景图是 path 归属的 SSoT） |

---

## 八、路径全景图的双态模型（V3.3 E16 修正）

路径全景图共享依赖全景图的双态模型，但职责不同：

| 维度 | 依赖全景图（nodes） | 路径全景图（arch_directory_tree） |
|------|-------------------|-------------------------------|
| 设计态 | 功能级节点，目录 path | 目录节点，design_maturity='design' |
| 运营态 | 文件级节点，文件 path | 文件/目录节点，design_maturity='production' |
| design_maturity | design / production | design / production |
| build_status | planned / generated / testing / stable / deprecated / production | planned / generated / testing / stable / deprecated / production |

**V3.3 E16 修正：删除 state 字段，统一用 design_maturity**

**问题**：当前 arch_directory_tree 同时有 `state`（design/operational）和 `design_maturity`（design/production）两个字段，语义重叠：
- `state='design'` 等价于 `design_maturity='design'`
- `state='operational'` 等价于 `design_maturity = 'production'`

**裁定**：删除 `state` 字段，统一用 `design_maturity` 作为单一判定信号（与 §12.4 一致）。

**arch_directory_tree 字段（当前 PG schema 10 列；V3.4 删除 state，v15 重建表时移除 node_id 外键列，最终 10 列）**：

| 字段 | 类型 | 设计态 | 运营态 | 说明 |
|------|------|:---:|:---:|------|
| path | TEXT PK | 目录路径 | 文件/目录路径 | 物理路径（SSoT） |
| parent_path | TEXT FK | 父目录 | 父目录 | 父路径外键 |
| path_type | TEXT | `directory` | `directory`/`file` | 路径类型 |
| domain_id | TEXT FK | 用户指定 | 路径推导 | 归属域（A-Blind-3 修复后非空） |
| ~~state~~ | ~~TEXT~~ | ~~`design`/`operational`~~ | ~~—~~ | ~~V3.4 删除（与 design_maturity 冗余）~~ |
| ~~node_id~~ | ~~INTEGER FK~~ | ~~NULL~~ | ~~nodes.node_id~~ | ~~V3.4 #147 新增，替换 state；v15 重建表时删除（不再关联 nodes 表）~~ |
| design_maturity | TEXT | `design` | `production` | 拓扑状态（单一判定信号，删除 state） |
| build_status | TEXT | `planned`/`generated`/`testing`/`stable`/`deprecated`/`production` | `stable` | 生命周期状态（与 nodes 对齐，裁定#178 5态；B-007 P0 2026-08-26 扩展 6 态 +production） |
| blueprint_id | TEXT | 用户指定 | 代码头部解析 | 关联蓝图 |
| change_policy | TEXT | — | 人工 | 变更策略 |
| modification_permission | TEXT | — | 人工 | 修改权限 |
| last_scanned | TEXT | — | 时间戳 | 最后扫描时间 |

**A-Blind-4 修复**：删除 state 后，build_status 和 design_maturity 正交化。design_maturity 是拓扑状态（design/production），build_status 是生命周期状态（planned/generated/testing/stable/deprecated/production，裁定#178 5态；B-007 P0 2026-08-26 扩展 6 态 +production）。禁止 `build_status='planned'` 且 `design_maturity='production'` 的矛盾组合。

---

## 九、arch_constraints 写入流程

**写入方**：`sync_yaml_to_depgraph.py`（VR规则同步）

**触发时机**：生成器运行完成后自动触发（生成器末尾调用）

**写入内容**：
- 跨域违规检测（nodes 的 import 跨越域边界但未在 domain_dependencies 中声明）
- 容量超限检测（domains.current_modules > domains.max_modules）
- 孤儿节点检测（nodes 有 path 但 arch_directory_tree 无对应记录）
- 层级违规检测（低层域依赖高层域）

**写入流程**：
1. 生成器运行完成
2. 生成器调用 `audit_domain_nodes.py --check`
3. 脚本读取 nodes + edges + arch_directory_tree + domains
4. 执行 4 类检测
5. 检测结果写入 arch_constraints 表
6. 输出检测报告

**AI 查询模式**：
```sql
-- 查询所有架构约束违规
SELECT * FROM arch_constraints WHERE violation_status = 'open';

-- 查询特定域的违规
SELECT * FROM arch_constraints WHERE domain_id = 'D_TRADING';
```

---

## 十、合并后的生成器完整流程

生成器同时管依赖全景图（扫描 import），12 步完整流程见 §4.5。arch_directory_tree 由 path_tree 脚本独立管理（V5.5 裁定）。

**合并后的关键变化**（V3.2）：
- 步骤 2 加载设计态数据时，加载 nodes/edges 的设计态行
- 步骤 3 DELETE 运营态数据时，清理 nodes/edges 的运营态行
- 步骤 5 生成运营态数据时，生成 nodes/edges（import 依赖）
- 步骤 6 合并设计态数据时，恢复 nodes/edges 的设计态行

---

## 十一、合并后的整体能力边界

| 能力 | 依赖全景图 | 路径全景图 | 设计规则缓存表 |
|------|:---:|:---:|:---:|
| 查"谁依赖谁" | ✅ | ❌ | ❌ |
| 查"放在哪" | ❌ | ✅ | ❌ |
| 查"属于哪个域" | ✅（nodes.domain_id） | ✅（arch_directory_tree.domain_id） | ✅（domains 表） |
| 查"域容量" | ❌ | ✅（domains） | ❌ |
| 查"架构约束违规" | ❌ | ✅（arch_constraints） | ❌ |
| 查"循环依赖" | ✅（dep_cycles 视图） | ❌ | ❌ |
| 查"设计态规划" | ✅（design_maturity='design'） | ✅（design_maturity='design'） | ❌ |
| 查"运营态实际" | ✅（design_maturity='production'） | ✅（design_maturity='production'） | ❌ |

**一句话总结**：依赖全景图管"谁依赖谁"（import 关系），路径全景图管"放在哪"（物理位置），设计规则缓存表管"域定义"（domains/contracts 等）。三者合并为《依赖与路径全景图能力定位书》。

---

## 十二、核心概念：双态模型

这是整个设计里最重要的概念。一个模块可以同时有两个"身份"：

### 12.1 设计态（design_maturity = 'design'）

> **"未来应该有的样子"** — 提前规划好的。

**唯一来源**：用户输入/讨论/描述，通过 `apply_depgraph.py --add-design-node` 唯一入口写入。不自动生成，不来自蓝图文件，不来自代码扫描。禁止直接 SQL 写入。

**粒度**：功能级（1功能=1节点）。不细化到文件级。

**path字段**：存目录路径（末尾带 `/`），如 `src/zephyr/trading/order_center/`。文件还不存在，但规划了将来放在这个目录下。

**blueprint_path字段**（新增）：存蓝图文档路径，如 `docs/03_modules/D_TRADING/order_center/blueprint.md`。

**blueprint_path 机械推导规则**（零歧义）：
```
blueprint_path = docs/03_modules/{domain_id}/{module_name}/blueprint.md
```
- `domain_id`：节点所属功能域 ID（如 D_TRADING）
- `module_name`：从设计态节点 path 末尾目录名推导（如 `src/zephyr/trading/order_center/` → `order_center`）

蓝图可能还没创建，但位置已定。推导规则机械可计算，AI 零歧义。

**业界依据**：Google Bazel 的 BUILD 文件路径 = 包路径（机械推导，零歧义）；Jane Street 的模块路径 = 文件路径（机械推导）。推导规则必须可机械计算，否则 AI 会幻觉。

**依赖关系**：edges表中 `dep_maturity='design'` 的edge。记录"规划中A应该依赖B"。

**不能做什么**：设计态只是描述，不能自动生成任何文件（不自动生成蓝图、不自动生成代码）。它是整个项目最大的蓝图，所有蓝图和代码都从它派生。

**作用**：从上至下指导开发。

**例子**：我先把交易域的所有模块在依赖全景图里设计好——因子研究中心、信号管线、组合优化器……一共 100 多个模块，它们的依赖关系全部提前画好。这些模块现在大部分没代码，但它们的位置和关系已经定了。

### 12.2 运营态（design_maturity = 'production'）

> **"当前真实的样子"** — 代码里实际存在的。

**来源**：生成器扫描代码文件自动产生。

**粒度**：文件级（1文件=1节点）。

**path字段**：存文件路径，如 `src/zephyr/trading/order_center/main.py`。

**依赖关系**：edges表中 `dep_maturity='active'` 的edge。记录"代码里A实际import了B"。

**作用**：从下至上反映真实状态。

**例子**：我在治理域写了一个临时脚本来修复某个 bug，生成器扫到它了，它就出现在运营态里。这个脚本不是提前设计的，是当下需要的。

### 12.3 双态关联规则

**核心裁定（V3.3 E1/E2 修复）**：设计态和运营态是**不同的行**，通过 `blueprint_id` 关联（一对多）。node_id 是**自增整数主键**（V3.4 P0-1 施工后为 INTEGER GENERATED ALWAYS AS IDENTITY，PG 迁移后为 bigint），与 path 解耦。

**为什么 node_id 不能含 filename**：
- filename 变了 → node_id 变了 → 所有关联的 edges 丢失
- 含 filename 的 node_id 不是稳定标识符
- 业界一致用与路径解耦的标识符（Google target label / Netflix 服务 ID / UUID）

**关联规则**：
```
设计态节点（1行）：node_id=<自增ID，查DB获取>, blueprint_id=bp-trading-order-center, path=src/zephyr/trading/order_center/, design_maturity=design
运营态节点（N行）：node_id=<自增ID，查DB获取>, blueprint_id=bp-trading-order-center, path=src/zephyr/trading/order_center/main.py, design_maturity=production
运营态节点（N行）：node_id=<自增ID，查DB获取>, blueprint_id=bp-trading-order-center, path=src/zephyr/trading/order_center/validator.py, design_maturity=production

关联规则：运营态节点和设计态节点共享相同 blueprint_id → 自动关联（一对多）
```

**禁止用 path 前缀匹配关联**——多个设计态节点的 path 前缀可能重叠，导致歧义。用 blueprint_id 精确关联，零歧义。

**业界依据**：Netflix Service Topology 用服务 ID 精确关联；Google Bazel 用目标 label 精确关联。业界一致用稳定标识符而非可变路径作为关联键。

**node_id 格式**：bigint（GENERATED ALWAYS AS IDENTITY），自增整数，与 path 完全解耦。edges 用 `from_node_id`/`to_node_id`（bigint FK）+ `dep_maturity`（design/active）。arch_directory_tree 无 `node_id` 外键（v15 重建表时移除），无 `state` 字段（统一用 `design_maturity`）。nodes 表当前 31 列。

**业界依据**：Google Bazel 的 target label（//pkg:target）是稳定标识符；Jane Street 的模块路径是稳定标识符。node_id 作为边的端点，必须稳定——路径可变，ID 不变。

### 12.4 机械判定规则（AI零歧义执行）

**单一判定信号**：`design_maturity` 字段是唯一判定依据。path 末尾 `/` 仅作为生成器写入时的格式约束，不作为读取时的判定依据。

| design_maturity 值 | 含义 | path 格式 | 来源 |
|:---:|------|---------|------|
| `design` | 设计态（规划中） | 目录路径（末尾带 `/`） | 用户输入写入 |
| `production` | 运营态（已实现） | 文件路径 | 生成器扫描代码 |

**AI 执行规则**：读取 `design_maturity` 字段判定态。禁止用 `os.path.exists()` 或 path 末尾 `/` 作为判定依据——目录存在时 `os.path.exists()` 也返回 True，会产生歧义。

**业界依据**：Google Bazel 1:1:1 规则（一个文件=一个目标=一个包）用单一信号判定；Jane Street OCaml 用类型系统单一信号判定。多信号判定 = 歧义 = AI 幻觉温床。

### 12.5 为什么放在一起而不是分开？

| 放在一起（一个数据库一个表） | 分开（两个数据库两个表） |
|---------------------------|------------------------|
| 一个功能域里，设计态和运营态模块的依赖关系是交织的 | 设计态和运营态完全隔离 |
| AI 能看到"设计态模块未来会依赖运营态模块" | AI 看不到全局 |
| 从设计态→运营态的过渡是自然的状态流转 | 需要手动同步 |

**裁定**：放在一起，用字段区分。`design_maturity` 字段标记拓扑状态（design/production），`build_status` 字段标记生命周期状态（planned/generated/testing/stable/deprecated/production，裁定#178 5态；B-007 P0 2026-08-26 扩展 6 态 +production）。两个正交维度，分离定义（见 §12.6）。edges 表用 `dep_maturity` 字段标记 'design'（规划依赖）或 'active'（实际依赖）。

### 12.6 设计态实现检测（双正交状态机）

**两个正交维度，分离定义**：

| 维度 | 字段 | 含义 | 状态机 |
|------|------|------|--------|
| 拓扑状态 | `design_maturity` | 节点在依赖图中的身份 | `design` → `production`（单向不可逆） |
| 生命周期状态 | `build_status` | 节点的实现进度 | `planned` → `generated` → `testing` → `stable` → `production`（`stable` → `deprecated` 为废弃分支；B-007 P0 2026-08-26 六态） |

**design_maturity 状态机**（拓扑状态，3 值，裁定#179）：
- `design`：规划中，功能级节点，目录 path（人工通过 apply_depgraph.py 写入，生成器不得创建）
- `production`：已实现，文件级节点，文件 path（由生成器产生）
- [ARCH-MM-002: prototype 已删除，原 prototype 节点现归入 production]
- **单向不可逆**：设计态节点是规划记录，保留 `design_maturity='design'`；运营态节点由生成器产生 `design_maturity='production'`。两者通过 blueprint_id 关联，不互相转换。

**build_status 状态机**（生命周期，6 态单调推进，裁定#178；B-007 P0 2026-08-26 扩展 +production）：
- `planned`：规划中，未实现（设计态节点默认值）
- `generated`：AI 已生成未验证（生产节点无对应 test 时推导值）
- `testing`：开发中/测试中
- `stable`：已验证/已上线运行
- `deprecated`：已废弃/已退役
- `production`：全量转正态（B-007 P0 新增；仅 stable 可转入，testing 须走 testing→stable→production 两步法，禁跳态）

**设计态节点的 build_status 子集**（3 态，裁定#190）：
- 设计态节点只使用 `planned`/`stable`/`deprecated`，不使用 `generated`/`testing`——后两个状态只适用于有代码文件的生产节点。
- `planned`：规划中，尚未被实现（无同 blueprint_id 的 production 节点）
- `stable`：规划已落地（生成器检测到同 blueprint_id 的 production 节点）
- `deprecated`：规划已废弃

**设计态→运营态不是"迁移"而是"实现"**（裁定#193）：
- 设计态节点不会变成生产节点——它们是不同的行，通过 `blueprint_id` 关联。
- "实现"= 生成器扫描到代码文件，创建 production 节点，同时更新设计态节点 `build_status='stable'`。
- 设计节点本身不变，只是被生产节点"伴随"（对齐 K8s：desired state manifest 不会变成 pod）。

**realization detection（实现检测）**（裁定#191）：
- 由生成器每次运行时自动执行，无需人工干预。
- 流程：查询所有 `design_maturity='design'` 且有 blueprint_id 的节点，检测是否有同 blueprint_id 的 production 节点——有则设 `build_status='stable'`，无则设 `build_status='planned'`。
- 对齐 K8s reconciliation controller：自动对比 desired/actual，AI 无需写复杂 JOIN 查询。

**build_status 推导规则**（生成器从文件特征推导，不新增文件头部字段，裁定#180）：
- design → `planned`
- production + 有 test → `stable`
- production 无 test → `generated`
- [ARCH-MM-002: prototype 已删除]
- `deprecated` 通过 apply_depgraph.py --transition-build-status 手工写入

**业界依据**：Netflix Service Topology 明确分离"部署状态"（canary/stable/deprecated）和"拓扑状态"（是否存在依赖）。ZephyrAlpha 的 `design_maturity` 是拓扑状态，`build_status` 是生命周期状态，两者正交。V4.3 将原 4 态 build_status（unbuilt/testing/stable/deprecated）扩展为 5 态（planned/generated/testing/stable/deprecated），新增 `generated` 态标记 AI 生成但未验证的代码——这是 100% AI 开发场景必需（对齐 K8s Pod Phase 5 值实践）。合并原 module_lifecycle_state 字段到 build_status，消除双字段语义重叠（裁定#178/#183）。2026-08-26 B-007 前置批 P0 再扩展为 6 态 +production（Owner 2026-08-26 全量转正裁定隐含前置；`stable`→`production` 为新增推进边，单调不跳态）。

### 12.7 设计态写入流程（唯一入口）

**当前脚本能力**（V3.3 E17/E18 确认）：`apply_depgraph.py` 已存在，但当前只支持 `--update-module` 和 `--batch`。V3.3 施工需扩展以下命令。

**设计态节点写入**：
```bash
python scripts/governance/apply_depgraph.py --add-design-node \
  --path "src/zephyr/trading/order_center/" \
  --blueprint-id "bp-trading-order-center" \
  --domain-id D_TRADING \
  [--build-status planned]
```
写入时 `design_maturity='design'`，`build_status` 默认 `planned`（可通过 `--build-status` 指定 stable/deprecated，但需符合 §12.6 状态机转换规则，裁定#190 设计态只用3态子集 planned/stable/deprecated）。`blueprint_path` 由脚本按 §12.1 机械推导规则自动填充。node_id 由数据库自增分配。

**设计态边写入**：
```bash
python scripts/governance/apply_depgraph.py --add-design-edge \
  --from-node-id 1001 \
  --to-node-id 1004 \
  --dep-type import \
  [--coupling-strength strong] \
  [--used-symbol "ClassName.method_name"] \
  [--invocation-method direct] \
  [--api-contract-refs "docs/api/order_api.md"] \
  [--event-ref "order_created"] \
  [--ddd-integration-pattern "shared_library"] \
  [--failure-mode "runtime_error"] \
  [--fallback "graceful_degradation"] \
  [--activation-condition "always"] \
  [--data-transfer-description "Order object"] \
  [--relationship-type "one_to_one"] \
  [--resource-impact "low"]
```
写入时 `dep_maturity='design'`，由蓝图 §4 文件清单驱动。写入前执行 DFS 循环检测，检测到循环则拒绝写入（D-Blind-2 修复）。

**参数说明**（13 个字段 = 4 个运营态子集 + 9 个设计态，对应 §14.4 edges 字段。4 个运营态是用户可指定的子集，其余 5 个运营态字段 from_node_id/to_node_id 为必需参数，architecture_direction/cross_domain/verified 由生成器计算）：

**运营态字段（4 个，设计态边也需指定基本信息）**：
- `--dep-type`：依赖类型（import/call/inheritance/composition）
- `--coupling-strength`：耦合强度（strong/medium/weak）
- `--used-symbol`：使用的符号（类名.方法名）
- `--invocation-method`：调用方式（direct/callback/event）

**设计态字段（9 个，对应 §14.4 设计态保留字段）**：
- `--api-contract-refs`：API 契约引用（文档路径）
- `--event-ref`：事件引用（事件驱动关系）
- `--ddd-integration-pattern`：DDD 集成模式（shared_library/anti_corruption_layer/open_host_service）
- `--failure-mode`：失败模式（runtime_error/silent_failure/cascading_failure）
- `--fallback`：回退策略（graceful_degradation/circuit_breaker/no_fallback）
- `--activation-condition`：激活条件（always/conditional）
- `--data-transfer-description`：数据传输描述
- `--relationship-type`：关系类型（one_to_one/one_to_many/many_to_many）
- `--resource-impact`：资源影响（low/medium/high）

**注意**：`--from-node-id`/`--to-node-id` 引用 nodes.node_id（当前为 bigint，V3.4 P0-1 + PG 迁移已完成，命令可用）。

**build_status 状态转换**（V3.3 E4 新增）：
```bash
python scripts/governance/apply_depgraph.py --transition-build-status \
  --node-id 1001 \
  --to testing
```
转换规则（机械判定，裁定#178 5态状态机）：
- `planned → generated`：允许（AI生成代码）
- `generated → testing`：允许（开始测试）
- `testing → stable`：允许（测试通过）
- `stable → deprecated`：允许（废弃）
- `deprecated → stable`：禁止（不可复活，需新建节点）
- 任何跳转（如 `planned → stable`）：禁止（必须逐步转换）

**设计态节点删除**：
```bash
python scripts/governance/apply_depgraph.py --remove-design-node --node-id 1001
```
执行 RULE-THREE 三步审判，通过后软删除（`build_status='deprecated'`）。

**禁止直接 SQL 写入**——必须通过 `apply_depgraph.py` 唯一入口。这与 RULE-FOUR 的 scaffold.py 哲学一致：唯一入口 + 自动校验 + 防孤儿。

---

## 十三、AI 怎么用它？（开发流程）

任何 AI 要在这个项目里干活，必须遵守这个流程：

```
接到任务
  ↓
第一步：查依赖全景图 → 这个功能域有什么模块？我要改的模块依赖谁？谁依赖它？
  ↓
第二步：查路径全景图 → 这个路径属于哪个域？域容量还够吗？位置和蓝图一致吗？
  ↓
第三步：确认模块在设计态还是运营态 → 设计态 = 可以改蓝图，运营态 = 只能改代码
  ↓
第四步：评估影响面 → 改了这个模块，下游哪些模块会受影响？跨域了吗？
  ↓
第五步：动手改
  ↓
第六步：是否需要触发生成器？（机械判定）
  ├─ 代码文件数变化 > 0？ → 是 → 触发生成器
  ├─ 蓝图 §4 文件清单变化？ → 是 → 触发生成器
  ├─ 路径树变化？ → 是 → 触发生成器
  └─ 以上全否（只改了 depgraph 数据）→ 禁止触发（会覆盖手动修复）
  ↓
第七步：验证通过 → 完事
```

**禁止的操作**：接到任务直接改代码，不看全景图。

### 13.1 AI 查询模板（SQL 速查）

**第一步：查依赖全景图**

```sql
-- 查某个域的所有模块
SELECT node_id, path, design_maturity, build_status, blueprint_id
FROM nodes WHERE domain_id = 'D_TRADING' ORDER BY design_maturity, path;

-- 查某个模块依赖谁（出边）
SELECT e.to_node_id, e.dep_type, e.dep_maturity, n.path AS to_path
FROM edges e JOIN nodes n ON e.to_node_id = n.node_id
WHERE e.from_node_id = 1001;

-- 查谁依赖某个模块（入边）
SELECT e.from_node_id, e.dep_type, e.dep_maturity, n.path AS from_path
FROM edges e JOIN nodes n ON e.from_node_id = n.node_id
WHERE e.to_node_id = 1001;

-- 查设计态规划依赖
SELECT * FROM edges WHERE dep_maturity = 'design';

-- 查实际依赖
SELECT * FROM edges WHERE dep_maturity = 'active';

-- 查循环依赖（简化版视图，按域分组）
SELECT * FROM dep_cycles ORDER BY domain_id, node_id;

-- 查完整循环报告（生成器运行后可用，含 edge_count）
SELECT * FROM dep_cycles_report ORDER BY edge_count DESC;
```

**注意**：上述 SQL 使用 `from_node_id`/`to_node_id`（V3.4 后字段名）。P0-1 Schema 迁移完成前，需用 `from_node`/`to_node`。

**第二步：查路径全景图**

```sql
-- 查某个路径属于哪个域
SELECT path, domain_id, design_maturity, build_status FROM arch_directory_tree
WHERE path = 'src/zephyr/trading/order_center/main.py';

-- 查某个域的容量（max_modules/current_modules 在 v6 合并入 domains 表）
SELECT domain_id, domain_name, max_modules, current_modules,
       (current_modules * 100.0 / max_modules) AS usage_pct
FROM domains
WHERE domain_id = 'D_TRADING';

-- 查超容域（>80%）
SELECT domain_id, domain_name, max_modules, current_modules,
       (current_modules * 100.0 / max_modules) AS usage_pct
FROM domains
WHERE current_modules * 100.0 / max_modules > 80
ORDER BY usage_pct DESC;

-- 查架构约束违规
SELECT * FROM arch_constraints WHERE violation_status = 'open';
```

**注意**：arch_directory_tree 的 `state` 字段已删除（V3.4 E16 裁定删除，P0-1 施工执行，v15 重建表时确认移除）。统一用 `design_maturity`。详见 §12.3 迁移期统一说明。

**第三步：确认模块在设计态还是运营态**

```sql
-- 单一判定信号：design_maturity 字段
SELECT node_id, path, design_maturity, build_status
FROM nodes WHERE blueprint_id = 'bp-trading-order-center';
-- design_maturity='design' → 设计态（可改蓝图）
-- design_maturity='production' → 运营态（只能改代码）
-- design_maturity='design' → 运营态草稿（无 blueprint_id）
```

**第四步：评估影响面**

```sql
-- 改了这个模块，下游哪些模块会受影响（递归查询）
WITH RECURSIVE downstream(node_id, path, depth) AS (
  SELECT node_id, path, 0 FROM nodes WHERE blueprint_id = 'bp-trading-order-center'
  UNION ALL
  SELECT n.node_id, n.path, d.depth + 1
  FROM downstream d JOIN edges e ON e.from_node_id = d.node_id
  JOIN nodes n ON e.to_node_id = n.node_id
  WHERE d.depth < 10  -- 防止无限递归
)
SELECT * FROM downstream WHERE depth > 0 ORDER BY depth;

-- 查是否跨域
SELECT e.from_node_id, e.to_node_id, n1.domain_id AS from_domain,
       n2.domain_id AS to_domain, e.cross_domain
FROM edges e
JOIN nodes n1 ON e.from_node_id = n1.node_id
JOIN nodes n2 ON e.to_node_id = n2.node_id
WHERE e.from_node_id = 1001 AND e.cross_domain = 1;
```

---

## 十四、生成器到底是什么角色？

### 14.1 它是什么

生成器是"照相机"——扫描真实代码世界，拍一张照片，存进 depgraph 的运营态部分。

### 14.2 它什么时候跑

三声明轨道触发（裁定#209，2026-07-02）：

| 触发方式 | 场景 | 机制 |
|---------|------|------|
| **自动触发**（阶段1起） | commit `.py` 文件后 | GATE-DEPGRAPH-OPS post-commit reconciler（priority=130，详见 §14.2.1）|
| **手动触发**（兜底） | 批量改代码后强制对齐 / 疑似漂移时人工核查 | `python scripts/governance/generate_project_depgraph.py` |
| **dry-run 检测**（不写入） | 只想知道漂移状况不修改 DB | `python scripts/governance/generate_project_depgraph.py --dry-run` |

**禁止触发的情况**（已收窄，原"覆盖手动修复"风险由 P1/P2 保护机制兜底，详见 §14.2.1）：
- 改了 depgraph 数据（apply_depgraph.py / sync 脚本写入）但没改代码——此时重跑生成器无新数据可扫描，是空操作（不再是"损失"，但也是浪费）。
- 生成器正在运行时（pg_advisory_lock 互斥，阶段1施工后）。

---

**裁定#209 结论**：依赖全景图运营态改为自动触发。commit `.py` 文件后由 GATE-DEPGRAPH-OPS post-commit reconciler（priority=130）触发：dry-run 检测漂移 → 有漂移则 `--output-db --force`，失败降级 warn。生成器内置 P1/P2 保护机制（`PRODUCTION_PROTECTED_FIELDS` 14 字段 + `EDGES_PROTECTED_FIELDS` 9 字段）：DELETE 前读出保护字段、重建后仅当重建字段为空时恢复，避免覆盖人工 curated 元数据。性能：增量引擎 Stage 3（content_hash 二元 skip）+ Stage 4 scan-level 缓存（ScanCache 命中跳过 AST 解析，3.7× 加速）。关联议题 #ARCH-040。

### 14.3 生成器覆盖矩阵

生成器每次运行对各表的操作（**字段级覆盖**，非全表 DELETE+INSERT）：

| 表 | 运营态字段 | 设计态字段 |
|---|---------|---------|
| nodes | DELETE+INSERT（`WHERE design_maturity != 'design' OR design_maturity IS NULL`） | 保留不动（`WHERE design_maturity='design'`） |
| edges | DELETE+INSERT（`WHERE dep_maturity != 'design' OR dep_maturity IS NULL`） | 保留不动（`WHERE dep_maturity='design'`） |
| domains | UPDATE current_modules（v6 合并自 arch_domain_capacity） | — |
| 其余 21 张表（含 P0-6 新增 9 张 sync 管理表 + arch_directory_tree 由 path_tree 独立管理） | 不碰 | 不碰 |

**统一表述**：运营态字段 DELETE+INSERT（全覆盖），设计态字段保留。非"全表 DELETE+INSERT"。这与 Netflix Service Topology 的多源融合模式一致——每个源各管各的字段。

### 14.5 生成器必须做到的（功能要求）

1. **从数据库加载设计态节点和 design edge**（不是从YAML文件）—— 修复G1隐患
2. **只删除运营态节点**（`WHERE design_maturity != 'design' OR design_maturity IS NULL`）—— 设计态保留
3. **只删除运营态 edge**（`WHERE dep_maturity != 'design' OR dep_maturity IS NULL`）—— design edge 保留（含 sync 写入的 YAML 派生 edge）
4. **扫描代码生成运营态节点和 active edge**
5. **active edge 只填充 9 个运营态字段**，不碰 9 个设计态字段（含 resource_impact）。dep_maturity 字段由生成器写 'active'
6. **合并设计态节点和 design edge**（从内存恢复），设计态字段保留不动
7. **冲突时设计态优先**（SSoT 分层：设计态全景图 > 代码）
8. **edges 用 from_node_id / to_node_id**（V3.4 后，稳定标识符），不用 path。**生成器代码已改为 from_node_id/to_node_id（bigint FK，V3.4 P0-1 + PG 迁移后完成）。**
9. **不处理 arch_directory_tree**（V5.5 裁定：path_tree 脚本独立管理，生成器不碰）

### 14.6 它有没有必要？

**有必要。** 虽然理论上每次改模块时可以手动更新全景图，但实际上：

- 项目有 3,400+ 个 .py 文件，手动更新不可能
- 生成器能自动发现代码里 import 了什么依赖，人做不到
- 生成器能在全局层面检测循环依赖，人一眼看不出来

**生成器修复历史**：详见 git log。

**P2 长期项**（不阻断当前施工）：
- G-Blind-4：增量更新机制（当前全量扫描可接受，10,000 文件时需增量）
- D-Blind-4：设计态节点版本管理（当前用 git log 追踪，未来加变更历史表）

## 十五、SSoT 原则（分层真源）

SSoT = Single Source of Truth = 唯一真源。

**V3.3 E9 修正**：设计态 SSoT = **数据库中的设计态数据**（depgraph 中 `design_maturity='design'` 的行）。用户输入必须通过 `apply_depgraph.py` 写入数据库才生效——未写入数据库的用户讨论不构成 SSoT。

不同状态下的真源优先级不同：

| 状态 | 真源优先级 | 理由 |
|------|-----------|------|
| 设计态 | depgraph（设计态数据）> 代码 > 文档 > AI记忆 | 蓝图定义的依赖关系是权威，代码必须服从 |
| 运营态 | 代码 > depgraph（运营态数据）> 文档 > AI记忆 | 生成器从代码扫描，运营态全景图是代码的"照片" |

**例子**：
- 设计态：数据库说"订单中心依赖风控引擎" → 代码里必须import风控引擎 → 对齐，没问题
- 运营态：代码里import了风控引擎 → 生成器扫描后数据库也会有这条edge → 对齐，没问题

**为什么设计态数据库优先？** 因为设计态数据是经过用户深思熟虑并通过 apply_depgraph.py 写入的——用户花了时间想清楚"应该是什么样"。代码可能是 AI 临时生成的，可能有幻觉。

**为什么运营态代码优先？** 因为运营态记录的是"当前实际长什么样"。代码是事实，数据库是照片。照片必须服从事实。

### 十五.1 业界对标（DB-as-Truth 的定位）

| 业界方案 | 真源形态 | 项目做法 | 差异定位 |
|---------|---------|---------|---------|
| Backstage（Spotify/CNCF） | catalog-info.yaml（文本真源），DB 为派生索引 | depgraph 为真源 | 项目反向：DB 为真源，YAML 为派生 |
| Structurizr / C4 model | models-as-code（DSL 文本真源） | depgraph 为真源 | 项目用 DB 替代 DSL 文本 |
| CocoIndex + VeloDB | 一表三索引（PG + 向量 + 全文） | depgraph（PostgreSQL 单库） | 项目用 PostgreSQL 单库，轻量但够用 |
| Google Bazel / BUILD 文件 | BUILD 文件文本真源 | depgraph 为真源 | 项目用 DB 替代 BUILD 文件 |
| Terraform state | tfstate 文件（JSON 真源） | depgraph 为真源 | 项目用 DB 替代 tfstate 文件 |

**风险与缓解**：

| 风险 | 缓解措施 |
|------|---------|
| DB 数据不可直接 git diff | 强制备份门禁（apply_depgraph.py `_check_git_backup()`；PG 通过 pg_dump 导出 SQL/JSON 纳入版本管理） |
| DB 损坏无文本回退 | 定期 `extract_depgraph.py --summary` 导出 JSON 快照 |
| DB 并发写入冲突 | PostgreSQL MVCC 行级锁（事务隔离，读写互不阻塞） + `threading.Lock` 进程内锁 |

---

## 十六、覆盖范围（项目全貌）

依赖与路径全景图覆盖整个项目的所有内容，不挑食：

| 层次 | 包含内容 |
|------|---------|
| 战略层 | 交易哲学、投资原则、风控原则、资金管理原则 |
| 业务层 | 市场分析、策略研究、因子工程、资产配置、风控、资金调度、执行系统 |
| 数据层 | 行情数据、基本面数据、另类数据、宏观数据、知识库 |
| AI 层 | Agent 系统、审计系统、架构系统、研发系统、运营系统 |
| 基础设施层 | 数据库、消息总线、缓存、存储、日志、监控、部署、CI/CD |
| 治理层 | 权限治理、数据治理、模型治理、依赖治理、变更治理、架构治理 |

**两个全景图的覆盖差异**：

| 维度 | 依赖全景图（nodes/edges） | 路径全景图（arch_directory_tree） |
|------|-------------------------|-------------------------------|
| 覆盖范围 | 有 import 依赖的代码节点 | 所有文件（包括文档/数据/模板） |
| 节点数 | 6,092 | 9,363（比 nodes 多 3,271 个文档/数据/模板/目录节点） |
| 边数 | 6,197 | — |

**当前实际覆盖**：53 个功能域，依赖全景图 6,092 节点（6,003 production + 89 design）[ARCH-MM-002: prototype 已归入 production] + 6,197 边（6,084 active + 113 design），路径全景图 9,363 行目录树。（2026-06-30 查询 depgraph (PostgreSQL)）

---

## 十七、生命周期

### 17.1 模块生命周期

一个模块从"只是一个想法"到"退休"，经历这些状态（与 §12.6 双正交状态机一致）：

```
概念（design + planned）→ 规划中（design + planned）→ 设计完成（design + planned）
  → 已生成（production + generated）→ 测试中（production + testing）
  → 运行中（production + stable）→ 废弃（保留 + deprecated）
```

**两个正交维度**：
- `design_maturity`（拓扑状态）：design → production（单向不可逆）
- `build_status`（生命周期状态）：planned → generated → testing → stable → production（6 态单调推进，裁定#178；B-007 P0 2026-08-26 扩展 +production，stable→deprecated 为废弃分支）

不是所有模块都走完——有些可能永远停在"规划中"（design + planned），这没关系。全景图允许"占位"。

### 17.2 生命周期与design_maturity映射

**与 §12.6 双正交状态机一致**。build_status 为 6 态单调推进（V4.3 裁定#178：planned→generated→testing→stable→deprecated；B-007 P0 2026-08-26 扩展 +production，stable→production 为新增推进边）。设计态节点使用 3 态子集（裁定#190）。

**生产节点（6 态完整推进）**：

| 生命周期状态 | design_maturity | build_status | 说明 |
|------------|----------------|-------------|------|
| 概念/规划中 | design | planned | 蓝图已定义，设计态占位 |
| 已生成 | production | generated | AI 已生成代码未验证（无对应 test） |
| 测试中 | production | testing | 代码测试中 |
| 运行中 | production | stable | 代码已验证上线（运营态节点由生成器产生） |
| 全量转正 | production | production | B-007 全量转正目标态（2026-08-26 P0 新增；仅 stable 可转入） |
| 废弃 | 保留原值 | deprecated | 不再使用但保留 |

**设计态节点（3 态子集，裁定#190）**：

| 生命周期状态 | design_maturity | build_status | 说明 |
|------------|----------------|-------------|------|
| 规划中 | design | planned | 尚未实现（无同 blueprint_id 的 production 节点） |
| 规划已落地 | design | stable | 生成器 realization detection 检测到实现（裁定#191） |
| 废弃 | design | deprecated | 规划已废弃 |

设计态节点不使用 `generated`/`testing`——这两个状态只适用于有代码文件的生产节点。

### 17.3 依赖关系生命周期

```
提出依赖（用户写入design edge）→ 验证通过（没有循环冲突）→ 激活（代码里实现了，生成器产生active edge）→ 废弃 → 移除
```

design edge和active edge可以同时存在。design edge是规划记录，active edge是实际状态。两者不冲突。

### 17.4 设计态实现检测流程

**realization detection（实现检测）**——生成器自动执行（裁定#191）：

1. 生成器每次运行时，查询所有 `design_maturity='design'` 且有 blueprint_id 的设计态节点
2. 检测是否存在同 blueprint_id 的 production 节点
3. 有 → 设 `build_status='stable'`（规划已落地）
4. 无 → 设 `build_status='planned'`（尚未实现）
5. 对齐 K8s reconciliation controller：自动对比 desired/actual，AI 无需写复杂 JOIN 查询

**设计态节点删除流程**（禁止直接 SQL 删除设计态节点）：

1. 蓝图 §4 文件清单移除该节点
2. 运行 `apply_depgraph.py --remove-design-node --node-id 1001`（node_id 为 INTEGER，通过 `SELECT node_id FROM nodes WHERE path='...'` 查询获得）
3. 脚本执行 RULE-THREE 三步审判（登记检查 → 重复检查 → 功能价值检查）
4. 审判通过 → 软删除（`build_status='deprecated'`，保留记录）
5. 生成器下次运行时自动清理关联的 design edge

**业界依据**：Google 删除 BUILD 目标 = 删除整个包（有明确流程）；Netflix 下线服务 = 状态转 deprecated（软删除）；K8s controller 做 reconciliation（自动检测 desired/actual）。ZephyrAlpha 对齐三者：realization detection 自动检测实现状态 + RULE-THREE 三步审判禁止硬删除。

---

## 十九、一句话总结

依赖与路径全景图的本质：

> **设计态定义"应该长什么样、放在哪"（施工图纸），运营态记录"当前长什么样、放在哪"（竣工照片）。两者共存于同一数据库，用 design_maturity 字段区分。依赖全景图管"谁依赖谁"，路径全景图管"放在哪"，设计规则缓存表管"域定义"。**

设计态是整个项目最大的蓝图，所有蓝图和代码都从它派生。运营态是代码的实际照片，由生成器自动扫描产生。所有 AI 干活之前必须先来查它。

---
