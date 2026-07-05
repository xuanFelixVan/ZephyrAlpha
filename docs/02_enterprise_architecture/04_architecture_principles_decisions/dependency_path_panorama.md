---
ttl: permanent
doc_type: architecture_view
---

> **裁定 #ARCH-REN-001（2026-06-26）**：6 个域 ID 连字符→下划线改名：
> D_GOV_DOCS→D_GOV_DOCS, D_GOV_ENFORCEMENT→D_GOV_ENFORCEMENT, D_GOV_SCRIPTS→D_GOV_SCRIPTS,
> D_GOV_AUDIT_TESTS→D_AUDITTEST, D_INTEGRATION-GATEWAY→D_INTEGRATION_GATEWAY, D_SECURITY-LLM→D_SECURITY_LLM。
> 本文档中出现的旧域名均为历史记录，已由上述裁定更新。


# 依赖与路径全景图能力定位书

> 版本：V6.0 | 2026-06-30（全量更新版：P2/P3 迁移 + v15-v18 schema + 53 域）
> 读者：项目 Owner（主要）+ AI 开发 Agent（次要）
> 写法：大白话为主。这是我的私人项目，我写了给我自己看，也是给接手的 AI 看。
> 变更历史见 git log。本文档只保留当前有效的设计规格和裁定结论。

> **⚠️ 命名变更说明（2026-07-01）**：为消除"架构"一词的歧义（"架构"易被误解为"架构设计规则"，但实际管的是"物理路径"），本次重命名如下：
> - **原"架构全景图" → 现"路径全景图"**（arch_ 表组，管"放在哪"——文件/目录的物理位置和域归属）
> - **原"共享表" → 现"设计规则缓存表"**（domains/contracts/gates 等，从 YAML 同步过来的只读缓存）
> - 文档标题同步从"依赖与架构全景图能力定位书"改为"依赖与路径全景图能力定位书"
> - 英文文件名已从 `dependency_architecture_panorama.md` 重命名为 `dependency_path_panorama.md`（2026-07-01）
> - 旧名"架构全景图"在本文档历史段落中若仍出现，均按本说明映射为"路径全景图"

> **文档责任范围**：本文档定义**依赖与路径全景图**（depgraph + 生成器）的能力定位、设计决策和裁定记录。
> 合并后覆盖：依赖全景图（dep_ 表组，管"谁依赖谁"）+ 路径全景图（arch_ 表组，管"放在哪"）+ 设计规则缓存表（domains/contracts 等）。
> 不包含：施工步骤和问题清单（见 archive/depgraph_issue_registry.md）、架构升级项目导航（见 architecture_upgrade_discussion.md）、生成器技术问题清单（见 generator_issues.md）。

> **⚠️ 数据源迁移说明（P2 迁移完成 2026-06-27）**：全景图数据库已从 SQLite 迁移至 **PostgreSQL 16**，数据库名统一为 `depgraph (PostgreSQL)`（一眼可知全景图所在引擎，避免与 SQLite 物理文件 `depgraph.db` 混淆）。本次迁移带来的引擎差异：
> - 自增主键：SQLite 的 `INTEGER PK AUTOINCREMENT` → PostgreSQL 的 `GENERATED ALWAYS AS IDENTITY`（不再需要 `sqlite_sequence` 序列跟踪表）
> - 并发控制：SQLite 的文件级写锁 → PostgreSQL 的 MVCC 行级锁（多版本并发控制，读写互不阻塞）
> - 约束校验：SQLite 的 `ALTER TABLE ADD CHECK` 不回溯限制 → PostgreSQL 支持 `NOT VALID` 延迟校验 + `VALIDATE CONSTRAINT`
> - 序列管理：SQLite 由 `sqlite_sequence` 表自动维护 → PostgreSQL 由 IDENTITY 列内部序列自动维护，无需 PRAGMA
> - 以下文中出现的 `AUTOINCREMENT` / `写锁` / `sqlite_sequence` 等 SQLite 特有术语，均按上述映射理解为 PostgreSQL 等价机制。

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

**目前规模**：运营态 6,003 个节点（production 1,251 + prototype 4,752）+ 设计态 89 个 = 6,092 个节点，53 个功能域，运营态 6,084 条 + 设计态 113 条依赖边。（2026-06-30 查询 depgraph (PostgreSQL)）

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
| 运营态 | 文件级节点，文件 path | 文件/目录节点，design_maturity='production'/'prototype' |
| design_maturity | design / production / prototype | design / production / prototype |
| build_status | planned / generated / testing / stable / deprecated | planned / generated / testing / stable / deprecated |

**V3.3 E16 修正：删除 state 字段，统一用 design_maturity**

**问题**：当前 arch_directory_tree 同时有 `state`（design/operational）和 `design_maturity`（design/production/prototype）两个字段，语义重叠：
- `state='design'` 等价于 `design_maturity='design'`
- `state='operational'` 等价于 `design_maturity in ('production','prototype')`

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
| design_maturity | TEXT | `design` | `production`/`prototype` | 拓扑状态（单一判定信号，删除 state） |
| build_status | TEXT | `planned`/`generated`/`testing`/`stable`/`deprecated` | `stable` | 生命周期状态（与 nodes 对齐，裁定#178 5态） |
| blueprint_id | TEXT | 用户指定 | 代码头部解析 | 关联蓝图 |
| change_policy | TEXT | — | 人工 | 变更策略 |
| modification_permission | TEXT | — | 人工 | 修改权限 |
| last_scanned | TEXT | — | 时间戳 | 最后扫描时间 |

**A-Blind-4 修复**：删除 state 后，build_status 和 design_maturity 正交化。design_maturity 是拓扑状态（design/production/prototype），build_status 是生命周期状态（planned/generated/testing/stable/deprecated，裁定#178 5态）。禁止 `build_status='planned'` 且 `design_maturity='production'` 的矛盾组合。

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

### 12.2 运营态（design_maturity = 'production' / 'prototype'）

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
设计态节点（1行）：node_id=1001, blueprint_id=bp-trading-order-center, path=src/zephyr/trading/order_center/, design_maturity=design
运营态节点（N行）：node_id=1002, blueprint_id=bp-trading-order-center, path=src/zephyr/trading/order_center/main.py, design_maturity=production
运营态节点（N行）：node_id=1003, blueprint_id=bp-trading-order-center, path=src/zephyr/trading/order_center/validator.py, design_maturity=production

关联规则：运营态节点和设计态节点共享相同 blueprint_id → 自动关联（一对多）
```

**禁止用 path 前缀匹配关联**——多个设计态节点的 path 前缀可能重叠，导致歧义。用 blueprint_id 精确关联，零歧义。

**业界依据**：Netflix Service Topology 用服务 ID 精确关联；Google Bazel 用目标 label 精确关联。业界一致用稳定标识符而非可变路径作为关联键。

**node_id 格式**（V3.4 修正）：
- **V3.4 前（历史）**：TEXT 类型，格式混乱（有 `D-TRADING-01` 也有文件名）
- **当前（V3.4 P0-1 + PG 迁移后）**：bigint（INTEGER GENERATED ALWAYS AS IDENTITY），自增整数，与 path 完全解耦
- **迁移策略**（P0-1 Schema 迁移执行）：
  1. 创建新表 `nodes_new`，node_id 为 INTEGER GENERATED ALWAYS AS IDENTITY，其余字段与 nodes 相同 + 新增 5 字段（has_dynamic_import/blueprint_id_invalid/in_degree/out_degree/blueprint_path）
  2. 从 nodes 复制数据到 nodes_new，node_id 自增分配新值
  3. 创建 `node_id_mapping` 临时表，记录旧 node_id → 新 node_id 映射
  4. edges 表新增 from_node_id/to_node_id（INTEGER FK），根据 mapping 填充
  5. edges 表新增 dep_maturity 字段（TEXT，默认 'active'，区分 design/active edge）
  6. 删除 edges 旧字段 from_node/to_node
  7. arch_directory_tree 删除 state 字段，新增 node_id 外键（INTEGER FK → nodes.node_id）
  8. 删除旧 nodes 表，重命名 nodes_new 为 nodes
  9. 重建外键约束和索引

**业界依据**：Google Bazel 的 target label（//pkg:target）是稳定标识符；Jane Street 的模块路径是稳定标识符。node_id 作为边的端点，必须稳定——路径可变，ID 不变。

> **⚠️ 迁移期统一说明（V3.4 P0-1 Schema 迁移，已完成）**
>
> 以下字段在 V3.4 P0-1 前**不存在**，P0-1 施工时新增（现已存在，部分被 v15 删除见下方说明）：
> - `edges.dep_maturity`（TEXT，默认 'active'，区分 design/active edge）
> - `edges.from_node_id` / `edges.to_node_id`（INTEGER FK，替换旧的 `from_node`/`to_node` TEXT 字段）
> - `nodes.has_dynamic_import` / `nodes.blueprint_id_invalid` / `nodes.in_degree` / `nodes.out_degree` / `nodes.blueprint_path`
> - `arch_directory_tree.node_id`（INTEGER FK → nodes.node_id，**替换**删除的 `state` 字段，列数不变）
>
> 以下字段在 V3.4 迁移前**存在**，迁移后**已删除**：
> - `edges.from_node` / `edges.to_node`（TEXT，迁移后删除）
> - `arch_directory_tree.state`（TEXT，迁移后删除，统一用 `design_maturity`）
>
> 迁移前：edges 用 `from_node`/`to_node`（TEXT），无 `dep_maturity`；arch_directory_tree 有 `state` 字段，无 `node_id`。
> 迁移后：edges 用 `from_node_id`/`to_node_id`（bigint FK），有 `dep_maturity`；arch_directory_tree 删除 `state`，新增 `node_id`（列数不变，11→11）。**v15 后**：arch_directory_tree 重建表时删除 `node_id`（最终 10 列），edges 的 `INTEGER FK` 在 PG 迁移后为 `bigint FK`。
>
> **本文档其他章节引用上述字段时，不再重复此说明。**
>
> **⚠️ v15/v16 Schema 变更裁定说明（#ARCH-016 治本，2026-06）**
>
> V3.4 P0-1 新增的部分字段在 v15 migration 中被删除（dead column 清理），当前 schema 不再包含：
> - `nodes.has_dynamic_import` / `nodes.in_degree` / `nodes.out_degree`（v15 删除；in/out_degree 改由生成器动态 COUNT 计算，不持久化）
> - `nodes.business_stream` / `nodes.stream_role` / `nodes.runtime_plane` / `nodes.ddd_aggregate` / `nodes.provided_interfaces`（v15 删除；裁定#165-169 合并的字段经评估无业务读写）
> - `nodes.implementation_ref`（v15 删除；无业务读写）
> - `edges.migration_status`（v15 删除；无业务读写，连带删除 idx_edges_migration 索引 + chk_edges_migration_status* 触发器）
> - `arch_directory_tree.node_id`（v15 删除；重建表模式移除 node_id FK + idx_arch_tree_node_id 索引）
> - v16 删除 orphan trigger `chk_edges_design_immutable_update`（源码中不存在，仅 DB 实例遗留）
>
> v15 后 nodes 表 31 列（V3.4 后曾达 36 列，v15 删 9 dead 列回到 31，但列组成与 V3.3 的 31 列不同）。本文档上述章节（§V3.4 迁移策略、§14.7 字段清单、§20.3 裁定表、§22.9 P0-6 扩展）引用上述字段时，均为历史记录，反映 V3.4/V5 当时的 schema 状态。

### 12.4 机械判定规则（AI零歧义执行）

**单一判定信号**：`design_maturity` 字段是唯一判定依据。path 末尾 `/` 仅作为生成器写入时的格式约束，不作为读取时的判定依据。

| design_maturity 值 | 含义 | path 格式 | 来源 |
|:---:|------|---------|------|
| `design` | 设计态（规划中） | 目录路径（末尾带 `/`） | 用户输入写入 |
| `production` | 运营态（已实现） | 文件路径 | 生成器扫描代码 |
| `prototype` | 运营态（草稿） | 文件路径 | 生成器扫描代码（无 blueprint_id） |

**AI 执行规则**：读取 `design_maturity` 字段判定态。禁止用 `os.path.exists()` 或 path 末尾 `/` 作为判定依据——目录存在时 `os.path.exists()` 也返回 True，会产生歧义。

**业界依据**：Google Bazel 1:1:1 规则（一个文件=一个目标=一个包）用单一信号判定；Jane Street OCaml 用类型系统单一信号判定。多信号判定 = 歧义 = AI 幻觉温床。

### 12.5 为什么放在一起而不是分开？

| 放在一起（一个数据库一个表） | 分开（两个数据库两个表） |
|---------------------------|------------------------|
| 一个功能域里，设计态和运营态模块的依赖关系是交织的 | 设计态和运营态完全隔离 |
| AI 能看到"设计态模块未来会依赖运营态模块" | AI 看不到全局 |
| 从设计态→运营态的过渡是自然的状态流转 | 需要手动同步 |

**裁定**：放在一起，用字段区分。`design_maturity` 字段标记拓扑状态（design/production/prototype），`build_status` 字段标记生命周期状态（planned/generated/testing/stable/deprecated，裁定#178 5态）。两个正交维度，分离定义（见 §12.6）。edges 表用 `dep_maturity` 字段标记 'design'（规划依赖）或 'active'（实际依赖）。

### 12.6 设计态实现检测（双正交状态机）

**两个正交维度，分离定义**：

| 维度 | 字段 | 含义 | 状态机 |
|------|------|------|--------|
| 拓扑状态 | `design_maturity` | 节点在依赖图中的身份 | `design` → `production`（单向不可逆） |
| 生命周期状态 | `build_status` | 节点的实现进度 | `planned` → `generated` → `testing` → `stable` → `deprecated` |

**design_maturity 状态机**（拓扑状态，3 值，裁定#179）：
- `design`：规划中，功能级节点，目录 path（人工通过 apply_depgraph.py 写入，生成器不得创建）
- `production`：已实现，文件级节点，文件 path（由生成器产生）
- `prototype`：原型占位（如空 __init__.py），文件级节点
- **单向不可逆**：设计态节点是规划记录，保留 `design_maturity='design'`；运营态节点由生成器产生 `design_maturity='production'`。两者通过 blueprint_id 关联，不互相转换。

**build_status 状态机**（生命周期，5 态单调推进，裁定#178）：
- `planned`：规划中，未实现（设计态节点默认值）
- `generated`：AI 已生成未验证（生产节点无对应 test 时推导值）
- `testing`：开发中/测试中
- `stable`：已验证/已上线运行
- `deprecated`：已废弃/已退役

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
- prototype → `generated`
- `deprecated` 通过 apply_depgraph.py --transition-build-status 手工写入

**业界依据**：Netflix Service Topology 明确分离"部署状态"（canary/stable/deprecated）和"拓扑状态"（是否存在依赖）。ZephyrAlpha 的 `design_maturity` 是拓扑状态，`build_status` 是生命周期状态，两者正交。V4.3 将原 4 态 build_status（unbuilt/testing/stable/deprecated）扩展为 5 态（planned/generated/testing/stable/deprecated），新增 `generated` 态标记 AI 生成但未验证的代码——这是 100% AI 开发场景必需（对齐 K8s Pod Phase 5 值实践）。合并原 module_lifecycle_state 字段到 build_status，消除双字段语义重叠（裁定#178/#183）。

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
FROM nodes WHERE node_id = 1001;
-- design_maturity='design' → 设计态（可改蓝图）
-- design_maturity='production' → 运营态（只能改代码）
-- design_maturity='prototype' → 运营态草稿（无 blueprint_id）
```

**第四步：评估影响面**

```sql
-- 改了这个模块，下游哪些模块会受影响（递归查询）
WITH RECURSIVE downstream(node_id, path, depth) AS (
  SELECT node_id, path, 0 FROM nodes WHERE node_id = 1001
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

#### 裁定#209：依赖全景图运营态触发机制改造（2026-07-02）

**背景**：原 §14.2 "禁止触发，因会覆盖手动修复"条款基于早期无保护机制的设计。经 §14.2.1 调研核实：生成器已内置 P1/P2 保护机制（`PRODUCTION_PROTECTED_FIELDS` 14字段 + `EDGES_PROTECTED_FIELDS` 9字段），DELETE 前读出保护字段、重建后仅当重建字段为空时恢复——原"覆盖手动修复"的禁用理由已大幅弱化。同时确认 15 个 reconciler 中**无任何针对 nodes/edges 运营态同步的 reconciler**（GATE-PATH-TREE 只管 arch_directory_tree，GATE-YAML-SYNC 只管规则缓存表），是设计缺口。

**核心裁定**：依赖全景图运营态应改为自动触发，分 4 阶段实施：

| 阶段 | 内容 | 产出 |
|------|------|------|
| 阶段0（立即） | 纠正文档与认知——本裁定即阶段0产出 | 本节修订 |
| 阶段1（短期） | 新增 GATE-DEPGRAPH-OPS reconciler（priority=130，trigger=commit .py，reconcile=dry-run检测→有漂移则 --output-db --force，失败降级 warn）+ 加 pg_advisory_lock 与 apply_depgraph.py 互斥 | 新 reconciler + 任务卡 |
| 阶段2（中期） | 字段角色分离治本——新建 nodes_metadata / edges_metadata 表，迁移 PRODUCTION_PROTECTED_FIELDS(14) + EDGES_PROTECTED_FIELDS(9) 出 nodes/edges；nodes/edges 回归纯派生态，可全量 DELETE+INSERT 无保护顾虑；P1/P2 保护机制下线 | schema 迁移 + 任务卡 |
| 阶段3（已完成，commit 2093db3615） | 增量引擎 Stage 3——content_hash 列 + compute_file_hash() + --incremental skip（无变更时跳过 DB 重建，二元 skip） | 增量引擎 |
| 阶段4（已完成，commit 8641f2b74） | scan-level 缓存（真正增量重建 Stage 4）——ScanCache 缓存 scan 结果到 .runtime/depgraph_scan_cache.json，key=(path, content_hash)，命中跳过 AST 解析；fingerprint（domain_derivation hash）+ SCAN_LOGIC_VERSION 双重失效；3.7x 加速（cached 3.13s vs no-cache 11.61s） | scan 缓存引擎 |

**第一性原理病根**：依赖全景图运营态本质是"代码世界的派生投影"，重新生成本不应有信息丢失。当前设计的悖论是运营态字段同时承担"派生数据"（from_node_id/dep_type 等9字段，应自动重生）与"人工 curated 元数据"（PRODUCTION_PROTECTED_FIELDS 14 + EDGES_PROTECTED_FIELDS 9，不应被覆盖）两种角色——业界主流做法是物理分离这两种角色（Sourcegraph 派生索引+仓库元数据分离；Netflix 流量拓扑+服务所有权分离）。阶段2 的字段分离才是治本。

**业界对标**（详见 §14.2.1）：Netflix "不完整数据比没有数据更糟糕"、Stripe 从"季度迁移"到"持续计算"、Sourcegraph 周期调度+webhook——业界主流是自动触发，"手动触发防覆盖"是反主流取舍。100% AI 开发场景下图漂移危害被放大（腾讯 Ghost Dependencies、SRI 论文 13.5× 依赖膨胀、Replit Agent 删库事件），自动触发必要性随 AI 改代码频率上升而上升。

**关联议题**：#ARCH-040（[architecture_issue_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)）。

---

#### 14.2.1 自动触发机制调研依据（裁定#209 证据基础）

> 调研时间：2026-07-02。方法：阅读 [generate_project_depgraph.py](../../../../scripts/governance/generate_project_depgraph.py)（3924行）+ [reconciliation_registry.py](../../../../src/zephyr/governance/audit/reconciliation_registry.py) + [git_commit_gateway.py](../../../../src/zephyr/governance/rule_bridge/git_commit_gateway.py) 代码实证 + 业界网络调研。

##### A. 生成器实现证据

| 项目 | 实证 |
|------|------|
| 扫描模式 | 全量扫描 + scan-level 缓存（裁定#209 Stage 4，commit 8641f2b74）；--incremental 支持二元 skip（Stage 3）；扫描范围 14 个白名单目录 |
| DELETE+INSERT | 有保留范围：`WHERE design_maturity != 'design'` 保留设计态节点/边 |
| 覆盖手动修复的真实含义 | 指运营态 production 字段的手动修改——**已有 P1/P2 保护机制**：`PRODUCTION_PROTECTED_FIELDS`（14字段：blueprint_id/owner/impact_level/build_status 等）+ `EDGES_PROTECTED_FIELDS`（9字段：failure_mode/fallback/resource_impact 等） |
| 保护机制语义 | DELETE 前读出保护字段 → 重建后 `apply_production_metadata_protection` 恢复——"仅当重建字段为空时恢复，不覆盖磁盘新值" |
| 并发控制 | **无显式跨进程锁**——生成器与 apply_depgraph.py 都仅依赖 PG MVCC 事务（autocommit=False），未用 advisory lock / row lock / table lock（阶段1需补） |
| dry-run | 支持 `--dry-run`（只检测漂移不写入） |
| 外部触发 | `main()` 不接受 argv，但可 subprocess 调用；当前无任何 reconciler 调用它 |
| 运行时长 | 代码里有计时但无基线数值，无法验证"成本高"是否成立 |

##### B. Reconciler 清单证据（确认缺口）

当前注册 15 个 reconciler，**无任何针对 depgraph nodes/edges 运营态同步的 reconciler**：

| priority | gate_id | 同步对象 |
|---|---|---|
| 50 | GATE-RUNTIME-CLEANUP | .runtime/ 旧文件 |
| 100 | GATE-19-manifest | script_manifest.yaml |
| 150 | GATE-PATH-TREE | **arch_directory_tree（路径全景图）** |
| 160 | GATE-YAML-SYNC | 规则缓存表（domains/contracts/gates） |
| 170 | GATE-ASSET-INDEX | unified-asset-index.yaml |
| 200 | GATE-REGISTRY-SYNC | 注册主索引+审计 |
| 250 | GATE-ID-UNIQ | pre-commit hook id 唯一性 |
| 280 | GATE-VOCAB-CHANGE | ttl 重判 |
| 300 | GATE-MODULE-ID-CONSISTENCY | module_id 三声明轨道一致 |
| 500 | GATE-DELETE-AUDIT | 幽灵节点检测+归档 |
| 600 | GATE-DEPRECATED-DIR | 废弃目录迁移 |
| 620 | GATE-REGENERATE | 域文档/index.yaml/manifest 重生 |
| 710 | GATE-EXEMPT-ZONE-FM | 豁免区 frontmatter |
| 710 | GATE-RULE-AUDIT | 规则审计+DCR+ARCH引用 |
| 810 | GATE-INTEGRITY-AUDIT | 规则完整性+裸commit审计 |

**GATE-DEPGRAPH-OPS 应排 priority=130**（在 GATE-RUNTIME-CLEANUP=50 之后，GATE-19-manifest=100 之后，GATE-PATH-TREE=150 之前——depgraph nodes/edges 是更上游真源，路径全景图依赖它）。

##### C. 业界对标证据

| 工具/公司 | 触发方式 | 关键论断 |
|----------|---------|---------|
| Bazel Skyframe | on-demand + Watchman 增量失效 | 图是派生态，重生成不覆盖手工（无手工字段概念） |
| Buck2 DICE | daemon + Watchman + 值相等 skip | 同上 |
| Cargo | 命令调用全量重算 | 依赖图小，全量可控 |
| Netflix Service Topology | 完全事件驱动 near-real-time | **"不完整或不正确的依赖数据比没有数据更糟糕"** |
| Stripe AutoJDK | continuous computation | 从"季度迁移项目"改为"持续自动计算"是明确演进方向 |
| Sourcegraph | 周期调度（2min任务+24h仓库）+ webhook | per-commit SCIP 全量上传 |
| LSP（rust-analyzer/pyright） | didChange 事件驱动 | 全部自动触发，无"手动触发"概念 |

**业界主流规律**：没有任何主流工具把"手动触发"作为长期方案。三个根本原因——① 派生态原则（图是 derived view，重生成不应有信息丢失）；② 漂移即事故（图漂移导致错误告警/根因定位/影响面判断）；③ 规模化不可承受手动（AI 改代码频率远高于人类，漂移窗口被放大）。

**AI 开发场景危害案例**：腾讯 Ghost Dependencies（2026-02，LLM 幻觉包名→供应链投毒）、SRI 论文（AI 声明依赖 vs 运行时依赖膨胀 13.5×）、Replit Agent 删生产数据库（2025-07，不知下游影响）。

##### D. 问题清单（7项）

| # | 问题 | 类型 | 严重度 |
|---|------|------|--------|
| P1 | 依赖全景图运营态无自动触发 reconciler（15个里缺一个） | 架构缺口 | 高 |
| P2 | §14.2"禁止触发"基于"覆盖手动修复"，但生成器已有 P1/P2 保护机制，原禁用理由已大幅弱化 | 文档失真 | 高 |
| P3 | design edge 已被 WHERE 条件保护不被覆盖，production 字段已有 P1/P2 保护——"覆盖手动修复"具体场景已说不清，可能已不存在 | 语义漂移 | 高 |
| P4 | 生成器与 apply_depgraph.py 之间无显式跨进程锁，自动触发时可能并发冲突 | 并发风险 | 中 |
| P5 | 全量扫描成本无基线数值，"成本高"是主观判断未实证 | 决策依据缺失 | 中 |
| P6 | 不支持增量，每次全量重算，制约自动触发频率上限 | 性能瓶颈 | 中 |
| P7 | 100% AI 开发下，图漂移窗口被放大——AI 改代码后立即查图可能看到旧图 | 场景特殊性 | 高 |

##### E. 裁定对用户观点的回应

用户观点："自动生成→出现垃圾→优化→测试→再生成→优化，而不是直接禁止触发停在那里不管"——**完全认可**。与 Netflix "incomplete data is worse than no data" 教训一致，与 Stripe "持续计算"演进方向一致。

关键补充认知：当前"垃圾"的来源不是自动触发本身，而是**字段角色混淆**——把人工 curated 数据塞进派生表，自动触发就会"覆盖手工"。这是设计债，不是自动触发的错。阶段2 的字段分离才是治本。阶段1 的 GATE-DEPGRAPH-OPS 是"先动起来"——用 P1/P2 保护机制兜底，让自动触发跑起来，发现什么字段被错误覆盖，再针对性分离。这正是"自动生成→出现垃圾→优化"的迭代循环。

### 14.3 生成器覆盖矩阵

生成器每次运行对各表的操作（**字段级覆盖**，非全表 DELETE+INSERT）：

| 表 | 运营态字段 | 设计态字段 |
|---|---------|---------|
| nodes | DELETE+INSERT（`WHERE design_maturity != 'design' OR design_maturity IS NULL`） | 保留不动（`WHERE design_maturity='design'`） |
| edges | DELETE+INSERT（`WHERE dep_maturity != 'design' OR dep_maturity IS NULL`） | 保留不动（`WHERE dep_maturity='design'`） |
| domains | UPDATE current_modules（v6 合并自 arch_domain_capacity） | — |
| 其余 21 张表（含 P0-6 新增 9 张 sync 管理表 + arch_directory_tree 由 path_tree 独立管理） | 不碰 | 不碰 |

**统一表述**：运营态字段 DELETE+INSERT（全覆盖），设计态字段保留。非"全表 DELETE+INSERT"。这与 Netflix Service Topology 的多源融合模式一致——每个源各管各的字段。

### 14.4 edges表字段级覆盖裁定（对齐实际 schema）

**V3.3 E1 修复**：对齐数据库实际 schema。当前 edges 表用 `from_node_id`/`to_node_id`（bigint FK，V3.4 P0-1 + PG 迁移后），有 `dep_maturity` 字段（V3.4 新增）。

edges表当前 22 列（v15 删除 migration_status 后）。

**字段归属总览**（当前 22 列 = 1 主键 + 9 运营态 + 9 设计态（含 resource_impact）+ 1 共享 + 2 P0-6 扩展）：

**主键（1 列）**：

| 字段 | 类型 | 含义 | 来源 |
|------|------|------|------|
| edge_id | bigint PK（IDENTITY） | 主键自增 | 新edge分配新ID |

**生成器重建的字段（运营态，9 列）**——从代码扫描得出：

| 字段 | 类型 | 含义 | 来源 |
|------|------|------|------|
| from_node_id | bigint FK | 源节点 ID（V3.4 改名，原 from_node TEXT，PG 迁移后为 bigint） | 生成器扫描import语句，关联到节点 node_id |
| to_node_id | bigint FK | 目标节点 ID（V3.4 改名，原 to_node TEXT，PG 迁移后为 bigint） | 同上 |
| dep_type | TEXT | 依赖类型（import/inherit等） | 生成器分析import语句 |
| architecture_direction | TEXT | 架构方向（upstream/downstream） | 生成器根据域层级推导 |
| coupling_strength | TEXT | 耦合强度 | 生成器根据import类型推导 |
| used_symbol | TEXT | 使用的符号 | 生成器解析import的具体符号 |
| invocation_method | TEXT | 调用方式 | 生成器分析代码调用方式 |
| cross_domain | INTEGER | 是否跨域 | 生成器比较from/to的domain_id |
| verified | INTEGER | 是否已验证 | 生成器扫描到=已验证 |

**共享字段（1 列）**——生成器和 apply_depgraph.py 都可写，但写入值不同：

| 字段 | 类型 | 生成器写入值 | apply_depgraph.py 写入值 | 说明 |
|------|------|------------|------------------------|------|
| dep_maturity | TEXT | active | design | **V3.4 新增字段**。生成器只写 active（运营态边），apply_depgraph.py 和 sync 脚本写 design（设计态/YAML 派生边）。生成器 DELETE 运营态时用 `WHERE dep_maturity != 'design' OR dep_maturity IS NULL`，保留设计态边。详见 §12.3 迁移期统一说明 |

**设计态保留的字段（9 列）**——用户定义的规划依赖，生成器不碰：

| 字段 | 类型 | 含义 | 为什么不覆盖 |
|------|------|------|------------|
| api_contract_refs | TEXT | API契约引用 | 设计态定义的契约关系 |
| event_ref | TEXT | 事件引用 | 设计态定义的事件驱动关系 |
| ddd_integration_pattern | TEXT | DDD集成模式 | 设计态定义的集成模式 |
| failure_mode | TEXT | 失败模式 | 设计态定义的容错设计 |
| fallback | TEXT | 降级方案 | 设计态定义的降级策略 |
| activation_condition | TEXT | 激活条件 | 设计态定义的条件依赖 |
| data_transfer_description | TEXT | 数据传输描述 | 设计态定义的数据流 |
| relationship_type | TEXT | 关系类型 | 设计态定义的基数关系 |
| resource_impact | TEXT | 资源影响 | 设计态定义的资源约束（当前 schema 第 16 列） |

**字段数**：当前 22 列（含 dep_maturity，v15 删除 migration_status 后）。

**from_node_id / to_node_id 说明**（V3.3 E1 修正，V3.4 P0-1 + PG 迁移后已施工）：
- **当前 schema**：`from_node_id`/`to_node_id`（bigint FK），引用 nodes.node_id（自增整数）
- **V3.4 前（历史）**：`from_node`/`to_node`（TEXT），存 node_id 字符串（已删除）
- 边的两端用节点 ID（稳定标识符），不用 path（可变属性）。路径变更时边不丢失。

**业界依据**：Netflix Service Topology 用服务 ID 作为边主键；Google Bazel 用目标 label 作为边主键。业界一致用稳定标识符而非可变属性作为边端点。

**生成器edges处理逻辑**：

```
1. DELETE FROM edges WHERE dep_maturity != 'design' OR dep_maturity IS NULL  → 删除运营态edge，保留design edge
2. design edge（dep_maturity='design'）完全保留不动（含 sync 写入的 YAML 派生 edge）
3. 扫描代码import → 生成新的active edge
4. active edge的9个运营态字段由生成器填充
5. design edge的9个设计态字段保留不动
6. dep_maturity 字段：生成器写 'active'，apply_depgraph.py 和 sync 脚本写 'design'
```

**design edge与active edge的关联**：

同一个依赖关系A→B可能同时有两条edge，通过 `from_node_id + to_node_id` 关联（V3.4 后）：

| edge类型 | dep_maturity | from_node_id | to_node_id | 来源 |
|---------|:---:|:---:|:---:|------|
| design | design | A | B | 用户写入 |
| active | active | A | B | 生成器扫描 |

AI查询模式：
- 查规划依赖：`SELECT * FROM edges WHERE dep_maturity='design'`
- 查实际依赖：`SELECT * FROM edges WHERE dep_maturity='active'`
- 查对齐状态：比较同一 from_node_id + to_node_id 的 design edge 和 active edge 是否一致

**迁移期注意**：详见 §12.3 迁移期统一说明。

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

### 14.7 nodes表字段级覆盖裁定（对齐实际 schema）

**V3.3 E7 修复**：对齐数据库实际 schema（当前 31 列）。V3.4 P0-1 新增了 `blueprint_id_invalid`/`blueprint_path`（保留至今）；`has_dynamic_import`/`in_degree`/`out_degree` 被 v15 删除（改由生成器动态 COUNT 计算）。edges 表的 `from_node_id`/`to_node_id` 见 §14.4。

**字段数**：当前 31 列（V3.4 后曾达 36 列，v15 删 9 dead 列回到 31，但列组成与 V3.3 的 31 列不同——含 blueprint_id_invalid/blueprint_path，无 has_dynamic_import/in_degree/out_degree/business_stream/stream_role/runtime_plane/ddd_aggregate/provided_interfaces/implementation_ref）。

**字段归属总览**（当前 31 列 = 1 主键 + 11 运营态 + 3 设计态 + 13 人工/脚本 + 3 共享）：

**主键（1 列）**：

| 字段 | 类型 | 含义 | 来源 |
|------|------|------|------|
| node_id | bigint（INTEGER GENERATED ALWAYS AS IDENTITY） | 节点 ID | 数据库自增（V3.4 P0-1 + PG 迁移后） |

**生成器重建的字段（运营态，11 列）**——从代码扫描得出：

| 字段 | 类型 | 含义 | 来源 |
|------|------|------|------|
| node_type | TEXT | 节点类型（8种文件制品类） | 生成器分析文件类型 |
| path | TEXT | 文件路径 | 生成器扫描代码 |
| granularity | TEXT | 粒度（file/module/feature） | 生成器推导 |
| domain_id | TEXT | 功能域 ID | 生成器从路径推导 |
| belongs_to | TEXT | 归属模块 ID | 生成器推导 |
| architecture_layer | TEXT | 架构层（L0-L6） | 生成器推导 |
| drive_direction | TEXT | 驱动方向（bottom_up） | 生成器推导 |
| deployment_lifecycle | TEXT | 部署生命周期（stable） | 生成器推导 |
| file_path | TEXT | 文件路径（冗余，与 path 相同） | 生成器扫描 |
| node_name | TEXT | 节点名称 | 生成器从文件名推导 |
| last_verified | TEXT | 最后验证时间 | 生成器填充 |

**设计态保留的字段（3 列）**——用户定义的规划节点，生成器不碰：

| 字段 | 类型 | 含义 | 为什么不覆盖 |
|------|------|------|------------|
| ~~module_lifecycle_state~~ | ~~TEXT~~ | ~~模块生命周期状态~~（裁定#183 已废弃，合并到 build_status，字段已删除） | V4.3 已合并到 build_status |
| subdomain_id | TEXT | 子域 ID | 设计态定义的子域归属 |
| owner | TEXT | 负责人 | 设计态定义的负责人 |

**共享字段（3 列，当前 schema）**——生成器和 apply_depgraph.py 都可写，但写入值不同：

| 字段 | 类型 | 生成器写入值 | apply_depgraph.py 写入值 | 说明 |
|------|------|------------|------------------------|------|
| design_maturity | TEXT | production / prototype | design | 生成器只写运营态值，apply_depgraph.py 只写设计态值。生成器 DELETE 运营态时用 `WHERE design_maturity != 'design' OR design_maturity IS NULL`，保留设计态行 |
| blueprint_id | TEXT | 从代码头部 [BLUEPRINT] 字段解析 | 用户指定 | 设计态节点由用户写入 blueprint_id；运营态节点由生成器从代码头部解析。两者通过相同 blueprint_id 关联（一对多） |
| build_status | TEXT | 从文件特征推导（见下） | planned/stable/deprecated（3 态子集） | 生成器从文件特征推导（裁定#180）：design→planned, production+test→stable, production无test→generated, prototype→generated；设计态节点由 apply_depgraph.py --transition-build-status 更新（3 态子集 planned/stable/deprecated，裁定#190） |

**V3.4 新增共享字段（1 列）**：

| 字段 | 类型 | 生成器写入值 | apply_depgraph.py 写入值 | 说明 |
|------|------|------------|------------------------|------|
| blueprint_path | TEXT | 从代码头部解析或 NULL | 机械推导（§12.1 规则） | **V3.4 新增字段**。设计态节点由 apply_depgraph.py 推导写入，运营态节点由生成器从代码头部解析（如有）。详见 §12.3 迁移期统一说明 |

**字段归属说明**：
- `design_maturity`：生成器只写运营态值（production/prototype），设计态值（design）由 apply_depgraph.py 写入。生成器 DELETE 运营态时用 `WHERE design_maturity != 'design' OR design_maturity IS NULL`，保留设计态行。
- `blueprint_id`：设计态节点由用户指定，运营态节点由生成器从代码头部解析。两者通过相同 blueprint_id 关联（一对多）。
- `build_status`：生成器从文件特征推导（裁定#180，不用默认值 draft/stable）——推导规则：design→planned, production+test→stable, production无test→generated, prototype→generated；`deprecated` 通过 apply_depgraph.py --transition-build-status 手工写入。设计态节点使用 3 态子集（planned/stable/deprecated，裁定#190），realization detection 自动更新（裁定#191）。
- `blueprint_path`：设计态节点由 apply_depgraph.py 按 §12.1 机械推导规则写入，运营态节点由生成器从代码头部解析（如有 [BLUEPRINT] 字段则填充，否则 NULL）。

**人工/脚本管理的字段（13 列）**——生成器不碰：

| 字段 | 类型 | 含义 | 管理方 |
|------|------|------|--------|
| change_policy | TEXT | 变更策略 | 人工 |
| impact_level | TEXT | 影响级别 | 人工 |
| modification_permission | TEXT | 修改权限 | 人工 |
| file_header_score | INTEGER | 文件头部评分 | 脚本 |
| tags | TEXT | 标签 | 人工 |
| trust_zone | TEXT | 信任区 | 人工 |
| license | TEXT | 许可证 | 人工 |
| type_specific_data | TEXT | 类型特定数据 | 人工 |
| can_build | INTEGER | 能否构建 | 脚本 |
| gate_reason | TEXT | 门禁原因 | 脚本 |
| hard_boundary_ref | TEXT | 硬边界引用 | 人工 |
| consumed_interfaces | TEXT | 消费接口 | 人工 |
| ~~implementation_ref（v15已删）~~ | TEXT | 实现引用 | 人工 |

**字段数**：当前 31 列（V3.4 后曾达 36 列，v15 删 9 dead 列回到 31，含 V3.4 新增的 blueprint_id_invalid/blueprint_path）。

**V3.4 新增的字段（5 列，已施工；has_dynamic_import/in_degree/out_degree v15 已删，blueprint_path/blueprint_id_invalid 仍在）**：

| 字段 | 类型 | 含义 | 来源 | 归属 | 当前状态 |
|------|------|------|------|:---:|:---:|
| blueprint_path | TEXT | 蓝图文档路径 | apply_depgraph.py 机械推导（§12.1）/ 生成器从代码头部解析 | 共享 | ✅ 仍在 |
| has_dynamic_import | INTEGER | 是否含动态 import | 生成器扫描 importlib/__import__ | 运营态 | ~~v15 已删~~ |
| blueprint_id_invalid | INTEGER | blueprint_id 校验失败标记 | 生成器校验 | 运营态 | ✅ 仍在 |
| in_degree | INTEGER | 入度 | 生成器统计 | 运营态 | ~~v15 已删，改由动态 COUNT~~ |
| out_degree | INTEGER | 出度 | 生成器统计 | 运营态 | ~~v15 已删，改由动态 COUNT~~ |

**8 种 node_type（V3.3 E13 修复）**：

| # | node_type | 含义 | 例子 |
|---|-----------|------|------|
| 1 | module | Python 模块 | src/zephyr/trading/main.py |
| 2 | package | Python 包 | src/zephyr/trading/__init__.py |
| 3 | script | 脚本 | scripts/governance/audit.py |
| 4 | test | 测试 | tests/test_trading.py |
| 5 | config | 配置文件 | config/trading.yaml |
| 6 | schema | Schema 定义 | schemas/order_schema.yaml |
| 7 | doc_template | 文档模板 | docs/03_modules/template.md |
| 8 | data_template | 数据模板 | data/asset_index/template.yaml |

**生成器合并设计态字段逻辑**：
1. 从数据库加载所有 `design_maturity='design'` 的节点到内存
2. DELETE 运营态节点（`WHERE design_maturity != 'design' OR design_maturity IS NULL`）
3. 扫描代码生成运营态节点
4. 运营态字段以代码扫描为准，设计态字段以数据库为准
5. 冲突时设计态优先（SSoT 分层：设计态全景图 > 代码）
6. 从内存恢复设计态节点

**业界依据**：Netflix Service Topology 三源融合（eBPF/IPC/traces）有明确的字段归属规则——每个源各管各的字段。ZephyrAlpha 的双态模型本质是多源融合（设计态来源 + 运营态来源），必须明确字段归属。

### 14.8 扫描范围白名单（显式声明）

**扫描文件类型（V3.3 E8 裁定）**：

| 文件类型 | 扫描 | 理由 |
|---------|:---:|------|
| .py | ✅ | 有 import 依赖，是依赖图主体 |
| .yaml/.yml | ✅ | 有配置依赖（config_depends），是路径全景图主体 |
| .md | ✅ | 有蓝图引用（blueprint_depends），设计态派生物 |
| .json | ❌ | 无解析器，不扫（未来如需扫描需新增解析器） |
| .toml | ❌ | 无解析器，不扫 |
| .sql | ❌ | 无解析器，不扫 |
| 其他 | ❌ | 无解析器，不扫 |

**扫描白名单（15 个目录，裁定#186 移除 tests/）**——生成器扫描这些目录下的 .py/.yaml/.yml/.md 文件：

| # | 目录 | 扫描内容 | 域归属 | 裁定 |
|---|------|---------|--------|:---:|
| 1 | `src/zephyr/` | 核心业务代码 | 35 个功能域（动态推导） | 保留 |
| 2 | `scripts/` | 治理脚本 | D_GOV_SCRIPTS | 保留 |
| 3 | `data/asset_index/` | 资产索引 YAML | D-DATA-ASSET | 保留 |
| 4 | `data/config/` | 数据配置 | D-DATA-CONFIG | 保留 |
| 5 | `data/metrics/` | 指标定义 | D-DATA-METRICS | 保留 |
| 6 | `config/` | 项目配置 YAML | D-INFRA-CONFIG | 保留 |
| 7 | `schemas/` | Schema 定义 | D-DATA-SCHEMA | 保留 |
| 8 | `docs/03_modules/` | 模块蓝图 | D_GOV_DOCS | 保留 |
| 9 | `docs/01_policies_and_standards/` | 政策标准 | D_GOV_DOCS | 保留 |
| 10 | `docs/02_enterprise_architecture/` | 企业架构 | D_GOV_DOCS | 保留 |
| 11 | `frontend/` | 前端代码 | D_FRONTEND | 保留 |
| 12 | `architecture_model/` | 架构模型 | D-ARCH-MODEL | 保留 |
| 13 | `infra/` | 基础设施 | D-INFRA | 保留 |
| 14 | `tools/` | 工具脚本 | D-TOOLS | 保留 |
| 15 | `specs/` | 规格文档 | D-SPECS | 保留 |

**排除黑名单（10 个目录）**——生成器不扫描：

| # | 目录 | 排除理由 | 裁定 |
|---|------|---------|:---:|
| 1 | `docs/08_knowledge/` | 知识库条目，纯文本无 import 依赖 | 保留排除 |
| 2 | `docs/_working/audit/` | 审计日志，历史记录无代码依赖 | 保留排除 |
| 3 | `data/cache/` | 运行时缓存，非代码 | 保留排除 |
| 4 | `data/telemetry/` | 遥测数据，非代码 | 保留排除 |
| 5 | `scripts/governance/_archive/` | 归档脚本，非活跃代码 | 保留排除 |
| 6 | `scripts/governance/repair/` | 修复脚本，临时性 | 保留排除 |
| 7 | `scripts/governance/_shared/` | 共享内部，非 depgraph 相关 | 保留排除 |
| 8 | `session_logs/` | 会话日志，历史记录无代码依赖 | 新增排除 |
| 9 | `reports/` | 报告输出，非代码 | 新增排除 |
| 10 | `logs/` | 运行时日志，非代码 | 新增排除 |

**节点类型白名单准入（4 种，裁定#184）**——只有这 4 种 node_type 进入依赖图（nodes 表），其余类型保留在路径全景图（arch_directory_tree 表）：

| # | node_type | 准入理由 | 文件类型 | 裁定 |
|---|-----------|---------|---------|:---:|
| 1 | `module` | Python 代码模块，有 import 依赖 | .py | 准入 |
| 2 | `script` | Python 脚本，有 import 依赖 | .py | 准入 |
| 3 | `test` | Python 测试，有 import 依赖 | .py | 准入 |
| 4 | `config` | 运行时配置，有配置依赖 | .yaml/.yml | 准入 |

**白名单机制**（裁定#184）：删除原 EXCLUDED_NODE_TYPES 黑名单，改为 `if node_type not in NODES_WHITELIST: skip`。黑名单已证明不可靠（漏掉 gate/contract/registry/schema 共 561 个非代码节点污染 nodes 表）；白名单天然安全——新类型默认不进 nodes。gate/contract/registry/schema/blueprint/doc/policy/standard/template/diagram/data 等类型不进 nodes，保留在 arch_directory_tree。

**关键边界**：依赖全景图只管有 import 依赖的代码节点（4 种白名单类型）；路径全景图管所有文件（包括文档/数据/模板）。非白名单类型在 arch_directory_tree 中有记录，在 nodes 表中无记录。

**业界依据**：Google Bazel 显式声明 BUILD 文件位置；Jane Street 显式声明模块路径。扫描范围必须显式文档化，否则 AI 不知道哪些目录被扫、哪些不被扫。

**问题1深度裁定（2026-06-24，#173）——依赖图 nodes 表的节点准入边界**：

裁定结论：依赖图（nodes 表）只收录有 import 依赖的代码节点（.py + .yaml/.yml 配置）；文档/规则/模板/数据文件不进 nodes 表，只在 arch_directory_tree 记录位置。

分析过程（以目的论推导）：

| 维度 | 分析 | 依据 |
|------|------|------|
| 全景图目的 | 防止 AI 幻觉/漂移/局部最优/位置漂移 | §一、§二 |
| 依赖图职责 | 回答"谁依赖谁"——只对有依赖关系的代码节点有意义 | §4.1、裁定#19 |
| 路径全景图职责 | 回答"放在哪"——所有文件都需要位置记录 | §4.2、裁定#19 |
| 噪音 vs 信息 | 零 import 边的文件进 nodes 表 = 孤岛节点，增加图规模但不增加依赖信息 | 图论：孤岛节点对依赖分析无贡献 |
| 规则约束落地 | 规则不通过 nodes 表附加，通过 arch_constraints + rule_bindings 表附加 | §9、§14.4 |

业界实践对标（100% AI 开发场景）：

| 工具/实践 | 做法 | 与本裁定关系 |
|-----------|------|-------------|
| dependency-cruiser | 只分析代码 import 边，不收录文档 | 一致 |
| madge | 只分析 JS/TS import，不收录 README | 一致 |
| ArchUnit | 只分析代码依赖，规则作为测试约束附加 | 一致（规则附加而非节点化） |
| KGsMCP VIOLATES 关系 | 规则作为约束关系附加，不作为节点 | 一致（规则约束化） |
| Google Bazel | 只跟踪有 BUILD 文件的代码目标 | 一致（显式声明） |

AI 开发场景适配：项目依靠 100% AI 开发，AI 需要的是"依赖关系清晰可查"+"规则约束可附加"，而非"所有文件都进依赖图"。文档/规则/模板进 nodes 表会制造大量孤岛节点，增加 AI 查询成本但不增加依赖信息——违反极简产出标准（§十.3）。

落地状态：已落地。当前 nodes 表 6,092 节点均为代码节点；arch_directory_tree 9,363 行包含 3,271 个文档/数据/模板节点（差值即被排除的 6 种 node_type）。

### 14.9 循环依赖检测能力（V3.4 E19 补充 DDL）

**检测时机**：生成器运行后自动检测（运营态循环）+ apply_depgraph.py 写入前检测（设计态循环）。

**dep_cycles 视图 DDL**（V3.4 E19 新增，P0-5 已施工创建，当前 PG schema 中存在）：

```sql
CREATE VIEW IF NOT EXISTS dep_cycles AS
WITH RECURSIVE
-- 使用 Tarjan SCC 算法检测强连通分量
-- 这里用简化版：找出所有在环中的节点
cycle_nodes AS (
  SELECT DISTINCT from_node_id AS node_id FROM edges e1
  WHERE EXISTS (
    SELECT 1 FROM edges e2
    WHERE e2.from_node_id = e1.to_node_id
    AND e2.to_node_id = e1.from_node_id
  )
  UNION
  SELECT DISTINCT to_node_id AS node_id FROM edges e1
  WHERE EXISTS (
    SELECT 1 FROM edges e2
    WHERE e2.from_node_id = e1.to_node_id
    AND e2.to_node_id = e1.from_node_id
  )
)
SELECT
  n.node_id,
  n.path,
  n.domain_id,
  n.design_maturity
FROM cycle_nodes c
JOIN nodes n ON c.node_id = n.node_id
ORDER BY n.domain_id, n.node_id;
```

**注意**：上述是简化版（只检测 2 节点环）。完整 Tarjan SCC 算法在生成器 Python 代码中实现，检测结果写入 `dep_cycles_report` 临时表，包含 cycle_id / node_ids / edge_count / domain_ids / detected_at 字段。

**Tarjan SCC Python 实现骨架**（生成器内置）：

```python
def tarjan_scc(nodes, edges):
    """Tarjan 强连通分量算法，返回所有 SCC 列表"""
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = {}
    result = []

    def strongconnect(node):
        index[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack[node] = True

        for successor in edges.get(node, []):
            if successor not in index:
                strongconnect(successor)
                lowlinks[node] = min(lowlinks[node], lowlinks[successor])
            elif on_stack.get(successor):
                lowlinks[node] = min(lowlinks[node], index[successor])

        if lowlinks[node] == index[node]:
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == node:
                    break
            if len(scc) > 1:  # 只保留有环的 SCC（节点数>1）
                result.append(scc)

    for node in nodes:
        if node not in index:
            strongconnect(node)
    return result
```

**运营态循环检测**（生成器内置）：
- 生成器运行完成后，对 edges 表执行 Tarjan SCC 算法
- 检测到的强连通分量（SCC）写入 `dep_cycles_report` 临时表
- 生成器输出循环依赖报告

**设计态循环检测**（apply_depgraph.py 内置）：
- `--add-design-edge` 写入前执行 DFS 循环检测
- 检测到循环则拒绝写入，返回错误：`CycleDetected: A → B → C → A`
- 防止设计态图出现循环，避免后续实现时无法拓扑排序

**AI 查询模式**：
```sql
-- 查询所有循环依赖（简化版视图）
SELECT * FROM dep_cycles ORDER BY domain_id;

-- 查询完整循环报告（生成器运行后可用）
SELECT * FROM dep_cycles_report ORDER BY edge_count DESC;

-- 查询特定域的循环依赖
SELECT * FROM dep_cycles WHERE domain_id = 'D_TRADING';
```

**业界依据**：Google Bazel 检测到循环依赖直接构建失败；Jane Street OCaml 编译器报错；Meta Hack 类型检查器报错。ZephyrAlpha 对齐——运营态循环警告，设计态循环阻断。

### 14.10 生成器执行报告

生成器运行后输出标准化报告：

```
=== 依赖与路径全景图生成器报告 ===
扫描统计：
  - 扫描目录：15 个
  - 扫描文件：3,400 个
  - 跳过文件：15 个（排除目录）
  - 解析失败：3 个（见失败清单）

节点统计：
  - 运营态节点：6,003 个（新增 12 / 删除 8 / 变更 45）
  - 设计态节点：89 个（保留不动）

边统计：
  - active edge：6,084 条（新增 23 / 删除 15 / 变更 8）
  - design edge：113 条（保留不动）

循环依赖检测：
  - 发现 8 个 SCC（453 条边）
  - 最大 SCC：D_TRADING（12 节点 / 45 边）

blueprint_id 校验：
  - 校验失败：2 个（见失败清单）

执行时间：3.5 分钟
=== 报告结束 ===
```

**业界依据**：Google Bazel 输出构建摘要；Netflix Spinnaker 输出 pipeline 报告；Meta Hack 输出变更摘要。AI 需要知道"发生了什么变化"才能判断是否需要重新评估影响面。

---

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

**当前实际覆盖**：53 个功能域，依赖全景图 6,092 节点（1,251 production + 4,752 prototype + 89 design）+ 6,197 边（6,084 active + 113 design），路径全景图 9,363 行目录树。（2026-06-30 查询 depgraph (PostgreSQL)）

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
- `build_status`（生命周期状态）：planned → generated → testing → stable → deprecated（5 态单调推进，裁定#178）

不是所有模块都走完——有些可能永远停在"规划中"（design + planned），这没关系。全景图允许"占位"。

### 17.2 生命周期与design_maturity映射

**与 §12.6 双正交状态机一致**。build_status 为 5 态单调推进（V4.3 裁定#178：planned→generated→testing→stable→deprecated）。设计态节点使用 3 态子集（裁定#190）。

**生产节点（5 态完整推进）**：

| 生命周期状态 | design_maturity | build_status | 说明 |
|------------|----------------|-------------|------|
| 概念/规划中 | design | planned | 蓝图已定义，设计态占位 |
| 已生成 | production | generated | AI 已生成代码未验证（无对应 test） |
| 测试中 | production | testing | 代码测试中 |
| 运行中 | production | stable | 代码已验证上线（运营态节点由生成器产生） |
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

## 十八、当前状态（2026-06-30 V6.0 更新）

> Phase H+J 修复 + V3.1-V3.4 审查 + V4.1-V5.8 规则统一 + P0-1~P0-5 七批次施工 + P2 PostgreSQL 迁移 + v15-v18 schema 治本 + 53 域拆分 + #ARCH-REN-001 域 ID 统一，全部已完成。历史进度详见 git log。

| 指标 | 修复前 (2026-06-15) | 修复后 (2026-06-16) | V5.8 状态 | V6.0 状态 (2026-06-30) |
|------|:---:|:---:|:---:|:---:|
| 总节点 | 8,174 | **7,590** | 7,700 | **6,092**（1,251 production + 4,752 prototype + 89 design） |
| arch_directory_tree 行数 | — | 9,204 | 9,204 | **9,363** |
| 重复路径 | 21个严重 | **0** | 0 | **0** |
| 空路径 | 42个 | **0** | 0 | **0** |
| 假blueprint_id | 6,219 | **0** | 0 | **0** |
| cross_domain=1 edges | 0（全默认） | **4,110** | 4,110 | **2,679**（裁定#203-B 清理孤儿边后下降） |
| 功能域 | 52 | 52 | 52 | **53**（裁定#200/#201 域拆分后） |
| 总表数 | 17 | 17 | 22 | **25**（含 _schema_version 系统表；v15-v18 治本后） |
| 业务视图 | 0 | 0 | 1（dep_cycles） | **1**（dep_cycles；pg_stat_statements 为 PG 扩展视图不计入） |
| schema 版本 | v1 | v14 | v14 | **v18**（v15 删 dead columns，v16 删孤儿触发器，v17 删陈旧索引，v18 加 blueprint_id CHECK 触发器） |
| nodes表列数 | 29 | **31** | 41（含 P0-6 扩展 5 列） | **31**（v15 删除 5 个 dead columns 后回落） |
| edges表列数 | 17 | **19** | 23（含 P0-6 扩展 3 列） | **22**（v15 删除 migration_status 后） |
| arch_directory_tree 列数 | — | 11 | 11 | **10**（v15 重建表，删除 node_id 外键列） |
| domains 列数 | — | — | — | **15**（v6 合并 arch_domain_layers/arch_domain_capacity 后） |
| 数据库引擎 | SQLite | SQLite | SQLite | **PostgreSQL 16**（P2 迁移 2026-06-27） |
| P0 阻断问题 | 8 | 2 | **0** | **0** |
| P1 重要问题 | — | 14 | **0** | **0** |

**修复文件**：`scripts/governance/generate_project_depgraph.py`（H1-H9, A1, V3.1/V3.2/V3.3/V3.4 裁定，2026-06-30 治本：node_type/edge_type/semantic 词表从 YAML 动态加载）
**Schema修复**：depgraph (PostgreSQL)（P2 迁移 2026-06-27，SQLite 物理文件 `data/databases/depgraph.db` 已删除归档；PG schema 真源为 `scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql`）
**文档合并**：原"依赖全景图能力定位书.md" → "dependency_architecture_panorama.md"（V3.2），后重命名为 "dependency_path_panorama.md"（2026-07-01，消除 architecture 歧义）

**已施工**（P0-1~P0-5 + P2/P3 全部完成）：
- ✅ P0-1：Schema 迁移（node_id 改 INTEGER PK + edges 字段重命名 + edges 新增 dep_maturity + arch_directory_tree 删 state）
- ✅ P0-2：apply_depgraph.py 扩展（4 个新命令）
- ✅ P0-3：生成器升级（12 步流程，2026-06-30 词表动态加载治本）
- ✅ P0-4：audit_domain_nodes.py 升级（4 类检测）
- ✅ P0-5：dep_cycles 视图创建 + 数据修复（I7/I8）
- ✅ P2：SQLite → PostgreSQL 16 迁移（2026-06-27，MVCC 行级锁，删除文件锁补丁）
- ✅ P3：pgvector 改造/LISTEN-NOTIFY 删除/分区表删除/监控告警改造（2026-06-28）
- ✅ v15-v18：schema dead column 清理 + 孤儿触发器/索引删除 + blueprint_id 双轨制+历史兼容 CHECK 触发器（裁定#ARCH-016/#208）

**已修复数据问题**：
- ✅ I7：arch_directory_tree 空 domain_id（P0-5 施工时修复）
- ✅ I8：arch_directory_tree build_status/state 逻辑矛盾（P0-1 删除 state 字段后消解）

---

## 十九、一句话总结

依赖与路径全景图的本质：

> **设计态定义"应该长什么样、放在哪"（施工图纸），运营态记录"当前长什么样、放在哪"（竣工照片）。两者共存于同一数据库，用 design_maturity 字段区分。依赖全景图管"谁依赖谁"，路径全景图管"放在哪"，设计规则缓存表管"域定义"。**

设计态是整个项目最大的蓝图，所有蓝图和代码都从它派生。运营态是代码的实际照片，由生成器自动扫描产生。所有 AI 干活之前必须先来查它。

---

## 二十、裁定记录

> 执行状态：✅=已执行 | ⏳=已裁定未执行 | ❌=未裁定
> 历史裁定过程（V3.0-V3.4）见 git log。本表只保留**当前有效的裁定结论**。裁定编号 #89-#144 为历史裁定，已归档至 git log，本表不再保留。

### 20.1 核心设计裁定（架构层）

| # | 裁定 | 结论 | 状态 |
|---|------|------|:---:|
| 1 | 设计态和运营态 | **放一起，字段区分**（design_maturity 字段判定） | ✅ |
| 5 | 设计态粒度 | **功能级（1功能=1节点）**，path 存目录路径（末尾带 /） | ✅ |
| 6 | 运营态粒度 | **文件级（1文件=1节点）**，path 存文件路径 | ✅ |
| 9 | 双态关联方式 | **blueprint_id 精确关联**（禁止 path 前缀匹配） | ✅ |
| 16 | 状态机 | **双正交：design_maturity（拓扑）+ build_status（生命周期）** | ✅ |
| 17 | SSoT 分层 | **设计态全景图>代码，运营态代码>全景图** | ✅ |
| 19 | 两全景图职责 | **依赖全景图管"依赖什么"，路径全景图管"放在哪"** | ✅ |
| 30 | 域数 | **53 域**（以数据库实际值为准；裁定#200/#201 拆分后） | ✅ |
| 42 | 设计态-运营态关系 | **一对多：1 设计态（功能级）→ N 运营态（文件级）** | ✅ |
| 145 | 两表设计 | **保持两张表不合并**（nodes 6,092 节点 vs arch_directory_tree 9,363 行） | ✅ |
| 146 | 两表关联方式 | **node_id 关联**（不用 path，稳定标识符与路径解耦） | ✅ |
| 147 | arch_directory_tree 新增字段 | **V3.4 新增 node_id 外键，替换删除的 state 字段** | ✅ |
| 148 | 共享字段处理 | **保留在两张表中**（domain_id/design_maturity/build_status/blueprint_id），不抽取第三张表 | ✅ |
| 150 | 两表关系 | **1:1（代码节点）和 1:0（文档/数据/模板节点）** | ✅ |

### 20.2 生成器与脚本裁定（执行层）

| # | 裁定 | 结论 | 状态 |
|---|------|------|:---:|
| 2 | 生成器必要性 | **有必要**，9 个 bug 已修复，只做扫描+对齐不做创造 | ✅ |
| 13 | 生成器覆盖范围 | **nodes 运营态全覆盖，edges active 全覆盖，设计态保留** | ✅ |
| 14 | edges 字段级覆盖 | **9 运营态字段重建，9 设计态字段保留，1 共享字段(dep_maturity)各写各的** | ✅ |
| 15 | 生成器加载设计态 | **从数据库加载**（不依赖已退役的 YAML 文件） | ✅ |
| 18 | 生成器触发条件 | **只在改了代码后才触发**（代码文件数变化>0 OR 蓝图§4变化 OR 路径树变化） | ✅ |
| 39 | 设计态节点写入入口 | **apply_depgraph.py --add-design-node 唯一入口** | ✅ |
| 40 | 设计态边写入入口 | **apply_depgraph.py --add-design-edge 唯一入口** | ✅ |
| 41 | blueprint_path 推导 | **blueprint_path = docs/03_modules/{domain_id}/{module_name}/blueprint.md** | ✅ |
| 44 | 生成器触发量化 | **代码文件数变化>0 OR 蓝图§4变化 OR 路径树变化 → 触发** | ✅ |
| 46 | 设计态节点删除 | **apply_depgraph.py --remove-design-node + RULE-THREE 三步审判 + 软删除** | ✅ |
| 57 | 生成器并发锁 | **运行时获取 PostgreSQL MVCC 行级锁，禁止 apply_depgraph.py 并发写入** | ✅ |
| 62 | 运营态循环检测 | **生成器内置 Tarjan SCC，写入 dep_cycles 视图** | ✅ |
| 63 | 设计态边循环检测 | **apply_depgraph.py --add-design-edge 写入前 DFS 检测，阻断循环** | ✅ |
| 64 | blueprint_id 校验 | **生成器校验 blueprint_id 指向的蓝图文件是否存在，不存在标记 blueprint_id_invalid** | ✅ |

### 20.3 Schema 与字段裁定（数据层）

| # | 裁定 | 结论 | 状态 |
|---|------|------|:---:|
| 3 | edges 区分设计/实际依赖 | **edges 加 dep_maturity 字段**（design/active，V3.4 P0-1 新增，已施工） | ✅ |
| 10 | 蓝图路径记录 | **新增 blueprint_path 字段**（V3.4 新增） | ✅ |
| 25 | edges 关联字段 | **from_node_id / to_node_id（bigint FK），不用 path**（V3.4 P0-1 已施工，PG 迁移后为 bigint） | ✅ |
| 34 | 判定信号单一化 | **design_maturity 字段为唯一判定依据**，禁止 os.path.exists() 或 path 末尾 / | ✅ |
| 37 | build_status 5 态 | **planned → generated → testing → stable → deprecated**（裁定#178） | ✅ |
| 55 | 动态 import 标记 | **nodes 表加 has_dynamic_import 字段**（V3.4 新增；~~v15已删，见§迁移说明后v15裁定~~） | ✅ |
| 67 | node_id 稳定性 | **node_id 改为 bigint（INTEGER GENERATED ALWAYS AS IDENTITY），与 path 解耦**（V3.4 P0-1 已施工，PG 迁移后为 bigint） | ✅ |
| 80 | 8 种 node_type | **module/package/script/test/config/schema/doc_template/data_template** | ✅ |
| 82 | arch_directory_tree state | **删除 state 字段，统一用 design_maturity**（V3.4 P0-1 已施工，v15 确认移除） | ✅ |
| 87 | ~~arch_layers 层级~~ | **清除后 7 条（L0-L6）**（~~v14已删arch_layers表~~） | ✅ |

### 20.4 路径全景图裁定（位置层）

| # | 裁定 | 结论 | 状态 |
|---|------|------|:---:|
| 53 | 路径全景图合并 | **合并到本文档 §5-§11** | ✅ |
| 58 | 两全景图协同 | **arch_directory_tree.path 是 SSoT，nodes.path 外键约束** | ✅ |
| 81 | 外键约束方向 | **单向外键：nodes.path 必须在 arch_directory_tree 存在，反向不要求** | ✅ |
| 149 | 两表覆盖范围 | **nodes 6,092 节点 vs arch_directory_tree 9,363 行**（差 3,271 个文档/数据/模板节点） | ✅ |
| 173 | nodes 表节点准入边界 | **只收录有 import 依赖的代码节点（.py+.yaml），文档/规则/模板不进 nodes 表**（业界对标 dependency-cruiser/ArchUnit） | ✅ |
| 174 | 规则文件归属 | **规则文件（trae_*.yaml）不进 nodes 表，归属 D_GOV_DOCS（文档域），在 arch_directory_tree 记录位置**。规则文件虽是 yaml 格式但本质是"规则文档"非"运行时配置"，无 import 依赖边，是孤岛节点。D_GOV_RULE 域 179 个规则文件节点应从 nodes 表清理。规则与业务域的逻辑约束通过 arch_constraints 表独立解决（from_domain/to_domain），不通过 nodes 表归属实现 | ✅ |
| 175 | 测试域处理 | **删除 10 个并发测试域**（D-T3-W0~W3/D-T4-SAME/D-T5-W0~W3/D-T9-PREREQ）。这些是 concurrent_write_test.py 红蓝对抗测试残留，已泄漏到生产 depgraph（0 模块空壳），ssot_path 路径不存在代码，测试隔离机制失效。业界实践：测试用独立测试库，不污染生产 DB（JUnit/K8s kind/Google Bazel） | ✅ |
| 176 | 设计态域处理 | **保留 5 个设计态域**（D_GOV_ENFORCEMENT/D-GOV_REPAIR/D_GOV_SCRIPTS/D_INTEGRATION_GATEWAY/D_SECURITY_LLM），标记为"计划中"。这些域为缓解超容父域而规划（D_GOVERNANCE 3860 模块超容 1930%、D_SECURITY 849、D_INTEGRATION 705、D_OPS 679），functional_domain_registry.yaml 已有完整 covers 规划。业界对标 DDD Bounded Context planned/TOGAF Transition Architecture | ✅ |
| 177 | 域命名统一 | **统一为下划线风格**（D-XXX_YYY），符合 trae_028 GOV-DOC-003 §SSoT 规定。当前 15 个域违规（25.9%）：5 个功能域（D_GOV_ENFORCEMENT→D_GOV_ENFORCEMENT 等）+ 10 个测试域（如保留则 D-T3-W0→D-T3_W0）。连字符已导致域重复 bug（project_memory 记录），sync 脚本已打 normalize_domain_id 补丁。业界对标 PEP8/K8s 社区均用 snake_case | ✅ |

### 20.5 施工优先级与验收裁定（施工层）

| # | 裁定 | 结论 | 状态 |
|---|------|------|:---:|
| 72 | 施工优先级 | **§22 七批次因果链：Schema→apply→生成器→audit→数据修复→Schema v5→YAML同步** | ✅ |
| 73 | 验收标准 | **§23 每批次机械可判定验收命令（exit code + 预期输出）** | ✅ |
| 88 | 回滚方案 | **§22.3 施工前备份 + 失败回滚命令** | ✅ |

### 20.6 待裁定与长期目标

| # | 裁定 | 结论 | 状态 |
|---|------|------|:---:|
| 11 | node_type 简化 | **文件制品类为主，DDD概念转 tags** | ⏳ |
| 28 | contracts 表来源 | **先确认来源再决定去重/合并** | ❌ |
| 31 | 超容域 21 个（current_modules > 150，2026-06-30 实查） | **重新评估拆分策略** | ⏳ |
| 49 | 6 层与 53 域映射 | **后续阶段补充映射规则** | ⏳ |
| 65 | 增量更新机制 | **长期目标——引入文件 mtime/hash 缓存** | ⏳ |
| 66 | 设计态版本管理 | **长期目标——记录变更历史，当前用 git log** | ⏳ |

### 20.7 V4.1 规则统一合并裁定（#151-164）

#### 唯一真源裁定（#151，V4.3 修订）

> **核心原则**：项目只能有一个真源、一个责任，这是不可逾越的规则。
> **业界对标**：Google Bazel（BUILD 文件是唯一真源，内存是只读派生物）、Kubernetes（YAML 是唯一真源，etcd 是只读派生物）。
> **裁定结论**：YAML 文件是**唯一真源**（唯一责任），depgraph 中的规则表是**只读缓存**（派生物，不是真源）。生成器单向同步（YAML → DB），DB 规则表通过触发器标记为只读，禁止任何直接修改。

| 维度 | YAML 文件（唯一真源） | depgraph 规则表（只读缓存） |
|------|---------------------|---------------------------|
| 角色 | **唯一真源**（唯一责任） | **只读缓存**（派生物，不是真源） |
| 能否修改 | ✅ 唯一可修改处 | ❌ 触发器拦截，禁止任何直接修改 |
| 写入方 | 人工/AI 修改规则时 | 只有 sync_yaml_to_depgraph.py（有通行证） |
| 读取方 | AI 理解规则语义 | AI 查询关系、SQL JOIN |
| Git 追踪 | ✅ 可追踪、可 review | ❌ 二进制不可追踪 |
| 枚举校验 | ❌ 无 CHECK 约束 | ✅ 有 CHECK 约束 |
| 同步方向 | 源 | 目标（YAML → DB 单向） |
| 删除策略 | **保留**（永不删除） | 可随时从 YAML 重建 |
| 责任归属 | **数据管理责任在此** | 无责任（只是查询工具） |

**为什么 DB 不是真源？**
1. **不能改**：触发器拦截，AI 改不了
2. **可重建**：DB 删了，从 YAML 重新同步就行
3. **无责任**：DB 不负责数据管理，只负责查询加速
4. **派生物**：DB 数据是 YAML 的复制品，不是独立数据

**只读触发器机制**（保证 DB 不可直接修改）：
- 9 张规则表（gates/field_vocabularies/registries/cross_registry_rules/hard_boundaries/business_streams/infrastructure_components/model_capabilities/blueprint_links）安装触发器
- 任何 INSERT/UPDATE/DELETE 操作被触发器拒绝
- 只有 sync_yaml_to_depgraph.py 能临时禁用触发器写入（有通行证）

**AI 工作流程**（永不困惑）：
| AI 要做什么 | 改哪里 | DB 怎么更新 |
|------------|--------|------------|
| 修改门禁规则 | 改 `gate_registry.yaml` | 运行 `sync_yaml_to_depgraph.py` |
| 修改枚举值 | 改 `stability_vocabulary.yaml` | 运行 `sync_yaml_to_depgraph.py` |
| 修改契约 | 改 `contract_mapping_table.yaml` | 运行 `sync_yaml_to_depgraph.py` |
| 查询"这个文件触发哪些门禁" | 查 DB（SQL JOIN） | 不需要更新 |
| 写入 nodes 节点 | 写 DB（nodes 表可写） | — |
| 写入设计态节点 | 用 apply_depgraph.py | — |

#### 14 项合并裁定（#152-164）

| # | 合并项 | 源文件 | 目标表 | 合并方式 | 优先级 |
|---|--------|--------|--------|---------|:---:|
| 152 | 跨模块依赖注册表（111 条） | cross_module_dependency_registry.yaml | edges 表（dep_maturity='design'） | 数据导入（YAML→DB） | P0 |
| 153 | 架构契约 VR 规则（11 条） | architecture_contract.yaml | arch_constraints 表 | 数据导入 | P0 |
| 154 | 契约映射表（18 条层契约） | contract_mapping_table.yaml | contracts 表 | 数据导入 | P0 |
| 155 | 门禁注册表（25 个） | gate_registry.yaml | 新建 gates 表 | 新建表+数据导入 | P1 |
| 156 | 功能域注册表（35 域） | functional_domain_registry.yaml | domains + arch_path_mappings（含 modification_permission 字段映射） | 数据导入 | P1 |
| 157 | 词汇表（22 个枚举字段） | vocabularies/*.yaml | 新建 field_vocabularies + CHECK 约束 | 新建表+约束 | P1 |
| 158 | 架构规则 TRAE-013~017/036~038 | rules/trae_*.yaml | arch_constraints 表 | 数据导入 | P1 |
| 159 | 声明式契约追踪（11 条） | declarative_contract_tracker_registry.yaml | contracts 表扩展 | 扩展表+数据导入 | P2 |
| 160 | Frontmatter 字段注册表（54 字段） | frontmatter_field_registry.yaml | field_vocabularies 表 | 数据导入 | P2 |
| 161 | 注册表之注册表（18 个） | registry_consistency_contract.yaml | 新建 registries + cross_registry_rules 表 | 新建表+数据导入 | P2 |
| 162 | 目录注册表 | directory_registry.yaml | arch_directory_tree 表 | 数据导入 | P2 |
| 163 | 规则路径目录（154 文件） | rule_catalog_registry.yaml | arch_directory_tree 表（文档节点位置） | 数据导入 | P2 |
| 164 | 基础设施+模型能力契约 | infrastructure_registry.yaml + model_capability_contract.yaml | 新建 infrastructure_components + model_capabilities 表 | 新建表+数据导入 | P3 |

#### Schema v5 新增表/字段裁定

| 操作 | 对象 | 说明 |
|------|------|------|
| 新建表 | `gates` | 25 个门禁定义（gate_id/name/entry/files_trigger/category） |
| 新建表 | `field_vocabularies` | 22 个枚举字段的合法值（field_name/value/definition） |
| 新建表 | `registries` | 18 个注册表元数据（registry_id/name/path/ssot_for） |
| 新建表 | `cross_registry_rules` | 6 条跨注册表一致性规则（CR-001~006） |
| 新建表 | `infrastructure_components` | 11 个基础设施组件 |
| 新建表 | `model_capabilities` | 9 个 AI 模型能力 |
| 扩展表 | `contracts` | +6 字段（promise/actual_consumer/fulfillment_status/gap/target_phase/last_reviewed） |
| 扩展表 | `edges` | +3 字段（valid_since/migration_status/is_legal_cycle；~~migration_status v15已删，见§迁移说明后v15裁定~~） |
| 扩展表 | `domains` | +1 字段（modification_permission） |
| 添加约束 | nodes | CHECK 约束（change_policy/impact_level/modification_permission 枚举校验，触发器方式实现） |
| 添加约束 | edges | CHECK 约束（migration_status 枚举校验，触发器方式实现；~~v15已删 migration_status + chk_触发器，见§迁移说明后v15裁定~~） |

#### 减少漂移和幻觉的核心价值

| 价值 | 说明 |
|------|------|
| 消除双源漂移 | YAML 注册表与 depgraph 各自维护同类数据 → 合并为 SSoT（YAML）+ 派生物（DB） |
| 消除枚举幻觉 | 无 CHECK 约束 → 数据库层强制枚举校验 |
| 消除跨文件关联幻觉 | AI 需跨 YAML+DB 人工匹配 → SQL JOIN 自动化 |
| 消除契约锚点幻觉 | 字符串引用无法验证 → 外键关联自动检测断链 |
| 消除合法循环幻觉 | 白名单只在 YAML → edges 表字段直接读取 |

### 20.8 V4.2 模板字段对齐裁定（#165-172）

> **背景**：扫描 `docs/01_policies_and_standards/templates` 目录下 11 个模板文件，特别是依赖图模板（TPL-DEPGRAPH-001 v6.0.0），找出 depgraph 缺失的字段。
> **对齐情况**：nodes 核心字段 100% 对齐（20/20），edges 字段 100% 对齐（16/16），但 5 个域级节点字段缺失，7 个模板顶层段无对应表。

#### 模板字段对齐总览

| 维度 | 对齐率 | 说明 |
|------|:---:|------|
| nodes 核心字段 | 100% (20/20) | 完全对齐 |
| nodes 差异字段 | 64% (9/14) | 5 个域级字段缺失 |
| edges 字段 | 100% (16/16) | 完全对齐 |
| arch_directory_tree | 100% | 完全对齐 |
| 顶层段→表映射 | 27% (6/22) | 6 段有对应表，16 段缺失（7 个计算字段无需建表，9 个业务数据建议建表） |

#### 缺失字段裁定（#165-169，高优先级，影响 AI 防幻觉）（~~v15已删此5字段，见§迁移说明后v15裁定~~）

| # | 缺失字段 | 所属模板段 | 裁定 | 理由 |
|---|---------|-----------|------|------|
| 165 | `business_stream` | nodes 域级字段 | ✅ 合并到 nodes 表 | 业务流归属是域级核心字段，缺失导致 AI 无法查询节点所属业务流 |
| 166 | `stream_role` | nodes 域级字段 | ✅ 合并到 nodes 表 | 业务流角色（producer/consumer/both）影响依赖分析 |
| 167 | `runtime_plane` | nodes 域级字段 | ✅ 合并到 nodes 表 | 运行时平面（data_plane/control_plane/management_plane）影响部署决策 |
| 168 | `ddd_aggregate` | nodes 域级字段 | ✅ 合并到 nodes 表 | DDD 聚合根标识影响领域驱动设计分析 |
| 169 | `provided_interfaces` | nodes 域级字段 | ✅ 合并到 nodes 表 | 已有 consumed_interfaces，缺 provided_interfaces 导致接口契约不完整 |

#### 缺失表裁定（#170-172，中优先级，影响架构治理）

| # | 缺失表 | 所属模板段 | 裁定 | 理由 |
|---|--------|-----------|------|------|
| 170 | `hard_boundaries` | §0 | ✅ 新建表 | 8 条硬边界是架构核心约束，当前散落在模板中 |
| 171 | `business_streams` | §11 | ✅ 新建表 | 业务流定义是跨域分析的基础 |
| 172 | `blueprint_links` | §19 | ✅ 新建表 | 蓝图→文件映射是蓝图-代码双向对齐的核心 |

#### 不合并的模板段（计算字段或文档元数据）

| 模板段 | 裁定 | 理由 |
|--------|------|------|
| §4 adjacency_lists | ❌ 不建表 | 从 edges 派生 |
| §7 orphan_nodes | ❌ 不建表 | 从 edges 计算 |
| §9 graph_metrics | ❌ 不建表 | diagnose_depgraph.py 计算 |
| §13 dependency_matrix | ❌ 不建表 | 从 domain_dependencies 派生 |
| §21 shard_index | ❌ 不建表 | 低优先级，可选 |
| §22 granularity_hierarchy | ❌ 不建表 | 低优先级，可选 |
| 蓝图 frontmatter 16 个文档元数据字段 | ❌ 不合并 | version/classification/language/created_by/date/ttl/summary/depends_on/references/rule_form/scope/verifiability/priority/ssot_claims/template_for/completeness 属于文档自身治理信息，不是依赖关系数据 |

#### Schema v5 补充字段/表（在 §22.9 P0-6 基础上追加）

| 操作 | 对象 | 说明 |
|------|------|------|
| 扩展表 | `nodes` | +5 字段（business_stream/stream_role/runtime_plane/ddd_aggregate/provided_interfaces；~~v15已删，见§迁移说明后v15裁定~~） |
| 新建表 | `hard_boundaries` | 8 条硬边界（id/category/constraint/parameters/impact） |
| 新建表 | `business_streams` | 业务流定义（stream_id/name/goal/input/output/runtime_plane） |
| 新建表 | `blueprint_links` | 蓝图→文件映射（blueprint_id/blueprint_path/alignment_verified） |

---

### 20.9 V4.3 build_status 枚举统一裁定（#178-183）

> **背景**：DB 实际值与 §12.6 定义严重不一致——build_status 有 10 种值（合法 4 种仅占 0.6%），module_lifecycle_state 有 5 种值（55% NULL），design_maturity 有 4 种值（合法 3 种）。五个病根导致脏值自循环：R1 字段重命名后代码未同步（生成器 L2635-2636 仍写 draft/inactive）；R2 生成器不从文件头部解析（parse_blueprint_header 只解析 6 字段）；R3 extract_depgraph.py L270 字段混淆（把 deployment_lifecycle 当 build_status 显示）；R4 merge_design_fields L311-313 永久保留脏值 design_only；R5 无 DB CHECK 约束。
>
> **业界对标**：K8s Pod Phase（5 值单调推进 + Conditions 正交布尔向量）；Backstage lifecycle（3 值极简，AI 场景最优）；Netflix Service Topology（部署状态与拓扑状态正交分离）；dependency-cruiser/madge/ArchUnit（纯依赖工具不维护状态）。
>
> **100% AI 开发场景特殊性**：需显式"生成态"（generated）标记 AI 生成但未验证的代码；测试是升级门禁；状态值 ≤5 防 AI 幻觉；双字段语义重叠导致 AI 困惑。

| # | 裁定 | 理由 |
|---|------|------|
| 178 | **合并双字段为单一 build_status（5 态枚举）**：删除 module_lifecycle_state，合并到 build_status，统一为 `planned`→`generated`→`testing`→`stable`→`deprecated` 单调推进状态机。planned=设计态未实现；generated=AI 已生成未验证；testing=测试中；stable=已验证；deprecated=已废弃 | Backstage 3 值太简（无法区分 AI 生成态），K8s 5 值正合适。`generated` 态是 100% AI 开发场景必需——标记 AI 生成但未验证的代码，防止下游 AI 基于未验证代码做决策。合并双字段消除语义重叠 |
| 179 | **design_maturity 保留 3 值**：`design`/`production`/`prototype`；`scaffold_placeholder`（216 个）归一化为 `prototype`（空 __init__.py 是 prototype 的一种）；design_maturity 作为独立字段保留（不从文件派生），因设计态节点是规划记录需持久化 | scaffold_placeholder 是 phase4b 清理脚本临时引入的非标准值，不在 §12.6 定义中。空 __init__.py 本质是"有文件但无实现"= prototype |
| 180 | **build_status 由生成器从文件特征推导，不新增文件头部字段**：不新增 [BUILD_STATUS]/[LIFECYCLE_STATE] 头部字段；推导规则：design→planned；production+test→stable；production 无 test→generated；prototype→generated。少数需手工标记的状态（deprecated）通过 apply_depgraph.py --transition-build-status 写入 | 从文件特征推导=数据从代码派生=代码变则状态变=永远准确。文件头部手工字段=维护负担+生成器覆盖风险（R2 病根）。推导规则机械可执行，AI 零歧义 |
| 181 | **orphan 为计算属性，不作为 build_status 字段值**：orphan 是零边节点的计算属性（由 audit 脚本实时计算），不持久化到 build_status；697 个 build_status='orphan' 节点执行 RULE-THREE 审判，有价值=planned，无价值=deprecated | orphan 是依赖关系属性（零边），不是生命周期属性。把 orphan 塞进 build_status 是概念混淆——一个节点可以同时是 orphan 和 stable。正交分离：build_status 管生命周期，orphan 由 edges 表计算 |
| 182 | **添加 DB CHECK 约束**：nodes 表 build_status CHECK(5 值) + design_maturity CHECK(3 值)，堵住多入口写入漏洞 | R5 病根（无 CHECK 约束）是多入口写入脏值的根本原因。CHECK 约束是 DB 层最后防线——无论哪个入口写入非法值，DB 直接拒绝。对齐 K8s admission controller 实践 |
| 183 | **删除 module_lifecycle_state 字段**：字段废弃（先标记 deprecated 停止写入，数据归档到 _archive 表后 DROP）；所有写入该字段的代码删除 | 7647 个 NULL（55% 空值）+ 6834 个 inactive（与 build_status 重叠）= 字段形同虚设。合并到 build_status 后无存在意义。保留只会继续制造脏值 |

#### 治本施工方案（7 步，按因果链执行）

> **核心原则**：先堵漏洞（防新脏值），再清旧账（洗历史脏值），最后加防御（DB 约束）。

| 步骤 | 施工内容 | 修复病根 | 验证 |
|:---:|---------|:---:|------|
| 1 | 修复生成器 derive 函数：新增 derive_build_status()，删除 derive_deployment_lifecycle()，修改 L2635-2636 | R1+R2 | `--dry-run` 确认输出 5 种合法值 |
| 2 | 删除 merge_design_fields L311-313 的 design_only 保留逻辑 | R4 | 运行后 design_only=0 |
| 3 | 修复 extract_depgraph.py L270 字段混淆 | R3 | `--summary` 显示正确 build_status |
| 4 | 添加 DB CHECK 约束 + 归档 module_lifecycle_state | R5 | INSERT 非法值被 DB 拒绝 |
| 5 | 数据清洗：design_only→planned，draft→按文件推导，orphan→RULE-THREE 审判，production/active→stable，path_invalid→删除，scaffold_placeholder→prototype | 全部 | `SELECT DISTINCT build_status` 只返回 5 种合法值 |
| 6 | 修复 apply_depgraph.py：transition 状态机更新 5 态，add_file_node 默认 generated，add_design_node 默认 planned | R1 | `--transition-build-status` 成功 |
| 7 | 更新文档与规则：§12.6 更新 5 态，trae_056 解除生成器禁用，trae_054 更新合法值列表 | — | 文档与 DB 值一致 |

#### 为什么治本

| 病根 | 治本措施 | 治本逻辑 |
|------|---------|---------|
| R1 代码未同步 | Step 1 修复 derive 函数 | 生成器从文件特征推导，不再用旧默认值 |
| R2 不从文件头部解析 | 裁定#180 不新增头部字段，改用文件特征推导 | 数据从代码派生，代码变则状态变，永远准确 |
| R3 extract 字段混淆 | Step 3 修复字段名 | AI 读到的 build_status 就是 DB 里的 build_status |
| R4 merge 保留脏值 | Step 2 删除保留逻辑 | 脏值被新推导值覆盖，不再锁死 |
| R5 无 CHECK 约束 | Step 4 添加 DB 约束 | DB 层最后防线，任何入口写非法值都被拒绝 |

**治本核心**：从"生成器写默认值 + 手工维护 + merge 保留脏值"的脏值自循环，转变为"生成器从文件特征推导 + apply_depgraph 手工标记 + CHECK 约束防御"的干净数据自循环。

---

### 20.10 V4.3 扫描范围白名单裁定（#184-188）

> **背景**：DB nodes 表有 18 种 node_type，但只有 4 种（module/script/test/config）应进入 nodes 表。gate(210)/contract(284)/registry(65)/schema(2) 共 561 个非代码节点污染 nodes 表（违反裁定#173/#174）；9 种非标准 node_type（event/decision/boundary/capability/domain/value_object/aggregate/design_node/production_node/domain_root）共 966 个 DDD/域概念节点混入 nodes 表；"data"类型同时出现在 CONFIG_TYPES 和 EXCLUDED_NODE_TYPES 中（自相矛盾）；tests/ 在文档中标记废止但代码仍扫描。
>
> **业界对标**：dependency-cruiser/madge/Bazel/Backstage/K8s 无一例外用白名单准入，不用黑名单排除。黑名单天然漏防——每新增一种非代码类型就要手动加排除，已漏掉 4 种。白名单天然安全——新类型默认不进 nodes。
>
> **100% AI 开发场景**：AI 无法判断"这个节点该不该在 nodes 表"——准入规则必须机械可执行；DDD 概念节点容易与文件节点混淆——概念不应在 nodes 表；AI 需要知道所有文件位置——arch_directory_tree 必须全覆盖。

| # | 裁定 | 理由 |
|---|------|------|
| 184 | **翻转为白名单准入**：删除 EXCLUDED_NODE_TYPES 黑名单，改为白名单。nodes 表只收录 4 种 node_type：`module`(.py 代码)/`script`(.py 脚本)/`test`(.py 测试)/`config`(.yaml 运行时配置)。gate/contract/registry/schema/blueprint 等不进 nodes，保留在 arch_directory_tree | 黑名单已证明不可靠（漏掉 4 种类型导致 561 个非代码节点污染）。白名单天然安全——新类型默认不进 nodes。对齐 dependency-cruiser/madge/Bazel 实践。精确实现裁定#173"nodes 表只包含.py 代码文件+.yaml 运行时配置文件" |
| 185 | **清理 9 种非标准 node_type**：event(326)/decision(256)/boundary(189)/capability(87)/domain(69)/value_object(60)/design_node(45)/aggregate(33)/production_node(5)/domain_root(5) 共 966 个概念节点迁移到 arch_directory_tree 或 design_nodes 表；production_node/domain_root 删除（与 design_maturity/domains 表语义重复） | nodes 表是文件级依赖图，只存文件节点。DDD/域概念是设计概念，不是文件——混在一起导致 AI 混淆"这个节点是文件还是概念"。正交分离：文件→nodes 表，概念→design_nodes 表或 arch_directory_tree |
| 186 | **移除 tests/从 SCAN_DIRS**：从 _FALLBACK_SCAN_DIRS 删除 tests/目录，与文档"已废止(2026-06-22)"对齐 | tests/已在文档标记废止但代码未同步。代码-文档不一致是 AI 幻觉来源。如未来需恢复需先更新文档再改代码 |
| 187 | **arch_directory_tree 扫描范围保持全覆盖**：保持 15 个扫描目录（移除 tests/后），所有文件（含文档/规则/模板/数据）都记录在 arch_directory_tree 中，不缩减 | AI 需要知道所有文件位置——"放在哪"是全景图核心目的。arch_directory_tree 不产生依赖边——不会因包含文档而产生噪音边。path_tree 生成器依赖 arch_directory_tree |
| 188 | **修复 CONFIG_TYPES 矛盾**：从 CONFIG_TYPES 中移除 data 类型。CONFIG_TYPES 保留 config/registry/contract/schema/gate（其中 registry/contract/schema/gate 按裁定#184 不进 nodes，但保留在 CONFIG_TYPES 定义中用于分类） | "data"类型是纯数据文件，无 import 依赖，不应与 config（运行时配置）混为一谈。移除后 CONFIG_TYPES 与白名单不再矛盾 |

#### 治本施工方案（5 步）

| 步骤 | 施工内容 | 修复问题 | 验证 |
|:---:|---------|:---:|------|
| 1 | 翻转白名单准入：删除 EXCLUDED_NODE_TYPES 黑名单逻辑，改为 `if node_type not in NODES_WHITELIST: skip`。白名单={module,script,test,config} | S1/S5 | `SELECT DISTINCT node_type FROM nodes` 只返回 4 种 |
| 2 | 清理 966 个概念节点：迁移 event/decision/boundary/capability/domain/value_object/aggregate/design_node 到 arch_directory_tree 或 design_nodes 表；删除 production_node/domain_root | S2 | `SELECT COUNT(*) FROM nodes WHERE node_type NOT IN ('module','script','test','config')` = 0 |
| 3 | 移除 tests/从 SCAN_DIRS + 同步 trae_058 | S4 | 代码与文档一致 |
| 4 | 修复 CONFIG_TYPES：移除 data 类型 | S3 | CONFIG_TYPES 与白名单无矛盾 |
| 5 | 更新 §14.8 文档：扫描范围从"16 目录+6 排除类型"改为"15 目录+4 准入类型" | 全部 | 文档与代码一致 |

#### 为什么白名单治本

| 策略 | 机制 | 风险 |
|------|------|------|
| 黑名单（当前） | 每新增一种非代码类型 → 必须手动加排除 → 漏加 = 污染 | 已漏 4 种（gate/contract/registry/schema），未来还会漏 |
| 白名单（裁定后） | 每新增一种代码类型 → 显式声明准入 → 不声明 = 默认不进 | 天然安全，零漏防 |

---

### 20.11 V4.3 设计态节点角色裁定（#189-193）

> **背景**：DB 有 8064 个 design_maturity='design' 节点，但 95.3%（7682 个）无 blueprint_id——是生成器违规为.md 文件创建的"幽灵设计节点"（违反§12.1"唯一来源"规则）。仅 456 个有 blueprint_id（175 已实现 + 281 未实现）。关联机制（blueprint_id）对 95.3% 的节点失效。"单向不可逆迁移"描述误导——设计节点不会变成生产节点，只是被生产节点"伴随"。
>
> **业界对标**：K8s desired state（yaml manifest）vs actual state（pod status）分离存储，controller 做 reconciliation；Terraform desired（.tf）vs actual（tfstate）分离文件；Bazel BUILD 文件定义 target，代码实现 target——分离但关联。ZephyrAlpha 选择合并存储（用 design_maturity 字段区分）为 AI 便利，但需清晰的 realization detection 机制。
>
> **100% AI 开发场景**：AI 需要知道"还没造的模块有哪些"——设计态节点必须准确，幽灵节点会误导 AI 认为这些模块"已规划"；AI 需要知道"规划实现了没"——需要自动 realization detection。

| # | 裁定 | 理由 |
|---|------|------|
| 189 | **设计态节点只由人工通过 apply_depgraph.py 写入，生成器不得创建**：重申§12.1"唯一来源"规则；删除 derive_design_maturity 的 `if node_type == "blueprint": return "design"` 分支；生成器扫描到的所有文件节点都是 production/prototype，不是 design | §12.1 已规定"不自动生成"，但代码违反此规则。7682 个幽灵设计节点是生成器违规产生的噪音。设计态节点代表"人工规划 intent"，自动生成的节点没有 intent |
| 190 | **设计态节点 build_status 使用 3 态子集**：planned（规划中，未实现）/stable（已实现，规划已落地）/deprecated（已废弃）。不使用 generated/testing——这两个状态只适用于有代码文件的生产节点 | 设计态节点是规划占位符，不是代码文件。build_status 只表示"规划是否落地"。对齐 K8s reconciliation：desired state 的 status 是"已满足/未满足" |
| 191 | **realization detection 由生成器自动执行**：生成器每次运行时，查询所有 design_maturity='design' 且有 blueprint_id 的节点，检测是否有同 blueprint_id 的 production 节点，有则设 build_status='stable'，无则设 build_status='planned' | 对齐 K8s reconciliation controller——自动对比 desired/actual。AI 无需写复杂 JOIN 查询——build_status 直接反映实现状态 |
| 192 | **清理 7682 个幽灵设计节点**：删除无 blueprint_id 的 design_maturity='design' 节点；保留 281 个未实现设计节点（build_status='planned'）+ 175 个已实现设计节点（build_status='stable'） | 幽灵节点无人工 intent，不是规划——保留只会误导 AI。删除后设计态节点从 8064 降至 456，精确反映实际规划。裁定#184 白名单准入实施后，.md 文件不再进 nodes 表，幽灵节点不会再产生 |
| 193 | **设计态→运营态不是"迁移"而是"实现"**：更新§12.6 和§17 文档，将"设计态升级为运营态"改为"设计态实现检测"。设计态节点不会变成运营态节点——它们是不同的行，通过 blueprint_id 关联。"实现"= 生成器扫描到代码文件，创建 production 节点，同时更新设计态节点 build_status='stable' | "迁移"暗示设计节点变成生产节点——这是误导。实际上它们是不同的行。"实现"准确描述了发生的事——规划被实现了，但规划记录本身不变。对齐 K8s：desired state manifest 不会变成 pod |

#### 治本施工方案（4 步）

| 步骤 | 施工内容 | 修复问题 | 验证 |
|:---:|---------|:---:|------|
| 1 | 删除 derive_design_maturity 的 blueprint 分支：生成器不再为.md 文件创建设计态节点 | P1/P5 | 生成器运行后 design_maturity='design' 节点数≤456 |
| 2 | 清理 7682 个幽灵设计节点：删除无 blueprint_id 的 design_maturity='design' 节点 | P1 | `SELECT COUNT(*) FROM nodes WHERE design_maturity='design' AND (blueprint_id IS NULL OR blueprint_id='')` = 0 |
| 3 | 实现 realization detection：生成器每次运行时自动检测设计态节点实现状态，更新 build_status | P3/P4 | `SELECT COUNT(*) FROM nodes WHERE design_maturity='design' AND build_status='stable'` ≈ 175 |
| 4 | 更新§12.6 和§17 文档：将"设计态升级为运营态"改为"设计态实现检测"；更新 build_status 状态机表 | P2 | 文档与代码一致 |

#### 为什么治本

| 问题 | 治本措施 | 治本逻辑 |
|------|---------|---------|
| 7682 幽灵节点 | Step 1 堵源头 + Step 2 清存量 | 生成器不再违规创建 + 历史噪音清除 |
| 关联机制失效 | 裁定#191 realization detection | 生成器自动检测，AI 无需手动 JOIN |
| "迁移"误导 | 裁定#193 改为"实现" | 准确描述：设计节点不变成生产节点，只是被"伴随" |
| build_status 混乱 | 裁定#190 3 态子集 | 设计态只用 planned/stable/deprecated，不用 generated/testing |

---

## 二十一、已知数据质量问题与教训

> 详细问题清单见 `archive/depgraph_issue_registry.md`。生成器 9 个 Bug 已修复，数据质量已验证（2026-06-16）。

**核心教训**（4条）：
1. **生成器是唯一数据入口** — 生成器的 bug 会系统性污染整个依赖图
2. **设计态数据需要独立保护** — DELETE+INSERT 架构中，设计态节点需用 `WHERE design_maturity='design'` 保护
3. **备份是最后防线** — 施工前必须 `pg_dump` 导出 depgraph (PostgreSQL)备份（SQLite 时期为 `cp data/databases/depgraph.db data/databases/depgraph.db.backup.V5.7`）
4. **AI vibe coding 的膨胀效应** — 需系统性清理机制（如 5,738 个 prototype 节点）

---

## 二十二、施工记录（已落盘，折叠归档）

> 以下施工已于 V5.8 完成，详细 SQL 脚本和验收命令见 git 历史。本节仅保留因果链和批次概要供 AI 理解施工逻辑。

### 22.1 七批次因果链

| 批次 | 施工内容 | 状态 |
|:---:|---------|:---:|
| P0-1 | Schema 迁移：node_id 改 INTEGER PK + edges 字段重命名 + nodes 新增 5 字段 | ✅ 已完成 |
| P0-2 | apply_depgraph.py 扩展：--add-design-node / --transition-build-status 等 4 命令 | ✅ 已完成 |
| P0-3 | 生成器升级：12 步流程 + 异常处理 + 执行报告 + 循环检测 | ✅ 已完成 |
| P0-4 | audit_domain_nodes.py 升级：4 类检测 + 写入 arch_constraints | ✅ 已完成 |
| P0-5 | dep_cycles 视图创建 + 数据修复 | ✅ 已完成 |
| P0-6 | Schema v5 迁移：新建 9 表 + 扩展 4 表 + CHECK 约束 + 只读触发器 | ✅ 已完成 |
| P0-7 | YAML→DB 同步：17 项规则/契约/门禁从 YAML 同步到 depgraph | ✅ 已完成 |

### 22.2 因果链原则

- **先核心架构后规则合并**：P0-1~P0-5（核心架构）→ P0-6/P0-7（规则合并）
- **原因**：规则表是"约束"，nodes/edges 是"被约束的对象"。必须先有被约束的对象，约束才有意义
- **回滚**：施工前已备份 depgraph.backup.V5.7，脚本可通过 git checkout 回滚

### 22.3 裁定备注

| 规格要求 | 裁定 | 原因 |
|---------|------|------|
| 生成器调用 write_cycles_to_view | 不需要 | dep_cycles 递归 CTE 视图自动计算 |
| 生成器 DELETE arch_directory_tree | 不需要 | path_tree 脚本自行 DELETE+INSERT |
| 生成器内置 parse_arch_tree | 不需要 | 职责分离：path_tree 独立承担 |
| _schema_version 单行 TEXT 模式 | 不需要 | INTEGER 递增 + description 更灵活 |

### 22.4 验收标准（已通过）

所有 P0-1~P0-7 批次验收命令已通过（exit 0），详细验收命令见 git 历史。

### 22.5 Schema 对齐（当前状态）

| 表 | 列数 | 关键字段 |
|------|:---:|---------|
| nodes | 31 | node_id(bigint IDENTITY) / path / node_type / domain_id / design_maturity / build_status / blueprint_id / blueprint_path |
| edges | 22 | from_node_id(bigint FK) / to_node_id(bigint FK) / dep_type / dep_maturity |
| arch_directory_tree | 10 | path / path_type / domain_id / design_maturity / build_status（v15 删除 node_id 外键后 10 列） |
| domains | 15 | domain_id / domain_name / ssot_path / layer_id / max_modules（v6 合并 arch_domain_layers/arch_domain_capacity 后） |

| 脚本 | 当前能力 |
|------|---------|
| apply_depgraph.py | --update-module / --batch / --add-design-node / --add-design-edge / --transition-build-status / --remove-design-node / --insert-domain / --migrate-dependencies / --insert-domain-mapping |
| generate_project_depgraph.py | 12 步流程 + 异常处理 + 执行报告 + 循环检测 + blueprint_id 校验 |
| audit_domain_nodes.py | 4 类检测 + 写入 arch_constraints |
| sync_yaml_to_depgraph.py | 17 项规则/契约/门禁从 YAML 单向同步到 DB |

### 20.11 架构债：worktree vs StagingArea 评估（裁定C，2026-06-25）

> **背景**：项目采用 100% AI 开发，Trae 多对话窗口并发执行。并发写入隔离方案有两个选择：
> - **git worktree**（业界标准）：每个 AI 分支级隔离，多 worktree 独立工作目录
> - **StagingArea 草稿模式**（项目自定义）：文件级隔离，`.aidrafts/{session_id}/` 草稿区
>
> **当前选择**：StagingArea 草稿模式（文件级隔离）。已在 `staging_area.py` 中修复跨进程锁缺陷（裁定A，`threading.Lock` → `os.open(O_CREAT|O_EXCL)` 文件锁）。
>
> **评估结论**：StagingArea 当前满足需求，worktree 评估标记为**条件触发架构债**——仅在以下条件满足时重新评估：
>
> | 触发条件 | 说明 |
> |---------|------|
> | StagingArea 冲突率 > 20% | 草稿提交冲突频繁，自动合并失败率高 |
> | 并发 AI 数 > 50 | 当前 37 个 AI，超过 50 时文件级隔离可能成为瓶颈 |
> | 跨分支依赖需求 | AI 需要并行开发不同分支特性（worktree 天然支持） |
>
> **worktree 优势**（若未来切换）：
> - 分支级隔离，天然无冲突
> - 业界标准（GitHub Copilot Worktree、Cursor 多分支）
> - git 原生支持，无自定义代码维护成本
>
> **StagingArea 优势**（当前保持）：
> - 文件级粒度更细，同一文件不同部分可并发修改
> - 不需要 git branch 管理，AI 学习成本低
> - 已有跨进程锁修复，PoC 验证通过
>
> **债务状态**：⏳ 条件触发——当前不评估，仅在触发条件满足时重新评估。

### 20.12 V4.4 容量治理体系重构裁定（#194-199，2026-06-25）

> **背景**：domains 表 max_modules=150 容量治理存在三大问题：
> 1. **高度耦合放宽机制**（ARCH-CAP-003）允许 5 个域上限放宽到 200，但 AI 无法可靠判断"高度耦合"，100% AI 开发项目不应有模糊地带
> 2. **统计口径混淆**：current_modules 字段混用全节点数和 production 节点数，H7 fix 错误地把 production 口径写入 current_modules
> 3. **装饰字段堆积**：22 个字段中 7 个无区分度或全空（can_build 全=1、gate_reason 全 NULL、growth_pattern 全='linear' 等），无治理价值
>
> **裁定结果**（6 条决策记录已写入 KE，topic=`domain_capacity::<domain_id>`）：

#### 裁定#194：废除高度耦合放宽，统一 150 硬上限（二元规则）

- **ARCH-CAP-003 废除**：trae_055 v1.0.8 移除 aliases 中的 ARCH-CAP-003
- **ARCH-CAP-002 重写为二元规则**：≤150 通过，>150 必须拆分，无例外
- **5 个 max=200 域统一改为 150**：D_GOVERNANCE / D_GOV_AUDIT / D_GOV_DRIFT / D_GOV_RULE / D_SECURITY
- **理由**：100% AI 开发项目不应有模糊地带。"高度耦合"是拆分信号，不是放宽上限的理由

#### 裁定#195：修复统计口径，新增 production_nodes 字段（v9 migration）

- **current_modules** = 全节点数（含 design + prototype + production + scaffold_placeholder）
- **production_nodes** = production 节点数（design_maturity='production' 的真实代码文件）——**容量判定口径**
- **v9 migration**：`ALTER TABLE domains ADD COLUMN production_nodes INTEGER DEFAULT 0`
- **H7 口径修复**：生成器分离 current_modules（全节点）和 production_nodes（production only）的统计逻辑
- **48 个域 production_nodes 已填充**

#### 裁定#196：容量门禁统一 production_nodes 口径

- **audit_domain_nodes.py**：`detect_hard_limit_violations` 硬上限从 200 改为 150，使用 production_nodes 口径
- **generate_domain_doc.py**：`capacity_status` 改用 `production_nodes` 判定（≤max_modules 正常，>max_modules 超容）
- **generate_capacity_report.py**：`actual_nodes` 全部替换为 `production_nodes`，查询从子查询改为直接读 DB 字段
- **generate_domain_architecture_diagram.py**：SELECT 添加 production_nodes，默认 max 200→150

#### 裁定#197：清理 7 个无区分度装饰字段（v10 migration）

- **v10 migration**：DROP COLUMN can_build / gate_reason / hard_boundary_ref / growth_pattern / feasibility / bottleneck_description / last_capacity_check
- **domains 表 22 列 → 15 列**
- **清理依据**：
  - `can_build`：全=1（无区分度，所有域都是可构建的）
  - `gate_reason`：全 NULL（从未使用）
  - `hard_boundary_ref`：全 NULL（从未使用）
  - `growth_pattern`：全='linear'（无区分度）
  - `feasibility`：2 种值 feasible/stable 语义混乱（可行性 vs 稳定性不是同一维度），与 build_status 重复
  - `bottleneck_description`：全 NULL 或空（从未使用）
  - `last_capacity_check`：39 个域为同一时间戳（批量更新写入，无实际区分意义）
- **nodes 表的 can_build/gate_reason/hard_boundary_ref 保留**（节点级有治理价值）

#### 裁定#198：决策记录统一到 KE（UnifiedMemoryAPI）

- **不使用 ADR**：100% AI 开发项目决策变化快，ADR 的不可变性成为束缚
- **决策记录写入 KE**：topic 命名约定 `domain_capacity::<domain_id>`
- **recall bug 修复**：VMSMemoryBackend.list_by_topic 未按 topic 过滤，导致 recall 返回所有 topic 的记录（commit c1dea1b595）

#### 裁定#199：4 个超限域拆分作为后续任务

- **4 个超限域**（production_nodes > 150）：
  - D_INFRA_RUNTIME：412（超限 262，2.7x）
  - D_GOV_AUDIT：230（超限 80，1.5x）
  - D_GOVERNANCE：185（超限 35，1.2x）
  - D_GOV_RULE：177（超限 27，1.2x）
- **拆分作为后续任务**，本次只修复统计口径和字段

#### 施工记录

| 阶段 | 内容 | Commit |
|------|------|--------|
| 阶段1 | 统一决策记录到 KE + recall bug 修复 | c1dea1b595 |
| 阶段2 | trae_055 v1.0.8 废除高度耦合 + 5 域 max 200→150 | a41e34ff8f, 1c23ab00e3, 953d6b9064 |
| 阶段3 | v9 migration + production_nodes 填充 + H7 口径修复 | bd4c500822, 2325b98283 |
| 阶段4 | 容量门禁统一 production_nodes 口径 + 硬上限 200→150 | 575e51abe2 |
| 阶段5 | v10 migration 清理 7 个装饰字段 | 9a06b0a8b2 |
| 阶段6 | 文档对齐（本节） | — |

#### 裁定#200：4 个超限域拆分完成（ARCH-CAP-002 v1.0.8 合规）

- **执行日期**: 2026-06-25
- **规则依据**: ARCH-CAP-002 v1.0.8（单域 production_nodes ≤ 150，> 150 必须拆分，无例外）
- **拆分方案**: [domain_split_plan_4_oversized_domains.md](file:///d:/ZephyrAlpha/docs/_working/domain_split_plan_4_oversized_domains.md)（附录E+F）

**拆分结果**:

| 原域 | 原 prod 数 | → | 拆分后域 | prod 数 | 说明 |
|------|--------:|---|---------|------:|------|
| D_INFRA_RUNTIME (411) | | → | D_INFRA_RUNTIME (保留) | 139 | 运行时核心 |
| | | → | **D_INFRA_A2A** (新建) | 114 | A2A 通信与管线 |
| | | → | **D_INFRA_RECOVERY** (新建) | 107 | 回滚与自愈 |
| | | → | **D_INFRA_TELEMETRY** (新建) | 51 | 可观测与画像 |
| D_GOV_AUDIT (228) | | → | D_GOV_AUDIT (保留) | 54 | 审计核心 |
| | | → | D_BEHAVIORAL_AUDIT (扩充) | 79 | 红蓝对抗测试 |
| | | → | **D_GOV_AUDIT_TESTS** (新建) | 142 | 审计测试套件 |
| D_GOVERNANCE (178) | | → | D_GOVERNANCE (保留) | 117 | 治理核心 |
| | | → | **D_GOV_DOCS** (新建) | 100 | 架构文档 |
| | | → | D_GOV_SCRIPTS (扩充) | 26 | 治理脚本 |
| D_GOV_RULE (118) | | → | D_GOV_RULE (保留) | 11 | 规则配置 |
| | | → | D_GOV_DOCS (共享) | (计入上方) | 规则文档 |
| | | → | D_GOV_ENFORCEMENT (扩充) | 69 | 规则执行代码 |

**新建域**: 5 个（D_INFRA_A2A, D_INFRA_RECOVERY, D_INFRA_TELEMETRY, D_GOV_AUDIT_TESTS, D_GOV_DOCS）
**扩充域**: 3 个（D_BEHAVIORAL_AUDIT, D_GOV_SCRIPTS, D_GOV_ENFORCEMENT）

**工具扩展**（apply_depgraph.py）:
- `--migrate-nodes`: 按 node_id 列表精确迁移 domain_id（解决跨域共享 blueprint_id 误迁问题）
- `--update-domain-ssot-path`: UPDATE domains 表的 ssot_path 字段
- `--force-cross-domain`: 强制执行跨域匹配的 `--update-domain-id`

**验证**: 全部 53 个域 production_nodes ≤ 150，ALL CACHE CONSISTENT，ARCH-CAP-002 v1.0.8 合规。

**施工记录**:

| 阶段 | 内容 | Commit |
|------|------|--------|
| 阶段0 | git 备份 + 刷新 4 域缓存 | da53f1cffd |
| 阶段0.5 | 扩展 apply_depgraph.py（3 个新功能） | d8be4eade3 |
| 阶段1 | 修正 674 个错位节点 | 681cab37b3 |
| 阶段2 | 拆分 D_GOV_AUDIT（171 测试节点） | 7b3a9b1655, edce73646f |
| 阶段3 | 拆分 D_INFRA_RUNTIME（411 节点→4 域） | cd85c37b10 |
| 阶段4 | 刷新 15 域缓存 + 文档同步 | 02b3903ea6 |

#### 裁定#201：D_SIGLEGACY 拆分补裁定（追溯正式记录）

- **执行日期**: 2026-06-25（补裁定，实际拆分发生在裁定#200前后但未记录）
- **规则依据**: D38/D41（平铺域，无子域）、ARCH-CAP-002（单域 production_nodes ≤ 150）
- **背景**: preexisting DB 问题调研发现 D_SIGLEGACY→3 子域拆分无任何裁定记录，无 registry 条目。本裁定追溯补记。

**拆分结果**:

| 原域 | 原 prod 数 | → | 拆分后域 | prod 数 | 说明 |
|------|--------:|---|---------|------:|------|
| D_SIGLEGACY (1) | | → | D_SIGLEGACY (保留) | 0 | 设计态占位域，45 个 design 节点待重新分配，ssot_path 留空 |
| | | → | **D_ASHARE_SIGNAL** (新建) | 0 | A 股特色信号，ssot_path=`src/zephyr/signal_ashare/` |
| | | → | **D_FUNDAMENTAL_SIGNAL** (新建) | 4 | 基本面信号，ssot_path=`src/zephyr/signal_fundamental/` |
| | | → | **D_SIGQC** (新建) | 0 | 信号质量，ssot_path=`src/zephyr/signal_quality/` |

**命名说明**（裁定#ARCH-002）: D_ASHARE_SIGNAL/FUNDAMENTAL/QUALITY 的 `D_SIGLEGACY_` 前缀仅表示拆分来源关系，**不表示层级子域**。依据 D38 裁定（parent_domain 仅作分组属性），这 3 个域是独立平级域，无 parent_domain 字段指向 D_SIGLEGACY。重命名涉及 105 文件 + 301 行 DB 更新，风险远大于收益，故保留命名。

**D_SIGLEGACY 保留说明**（裁定#ARCH-004）: D_SIGLEGACY 保留为设计态占位域（build_status=planned），45 个 design 节点（虚拟设计态路径如"信号域-核心基础设施/D-SIGLEGACY-12"）后续随架构演进重新分配到子域。ssot_path 留空（无代码目录）。

**验证**: D_SIGLEGACY production_nodes=0，D_FUNDAMENTAL_SIGNAL production_nodes=4，全部 ≤ 150，ARCH-CAP-002 合规。

#### 裁定#202：数据一致性修复（registry 与 panorama 对齐）

- **执行日期**: 2026-06-25
- **背景**: preexisting DB 问题调研发现 2 个域存在 registry 与 panorama 不一致问题。

| 域 | 问题 | 修复 |
|----|------|------|
| D_GOV_RULE | panorama 有 4 条裁定（#174/#194/#199/#200），但 registry 无条目 | 补写 registry 条目 |
| D_INFRA_OPS | registry 有 3 条（asset-inventory/capacity-assurance/resource_optimization），但 panorama 无直接裁定 | 补写 panorama 裁定记录 |

**D_INFRA_OPS 补记**: D_INFRA_OPS 在 domain_split_plan 附录 C.1 作为跨域共享 blueprint_id 引用域出现，但未作为拆分主体被裁定。该域有 7 个 production 节点，ssot_path=`src/zephyr/infra_ops/`，lifecycle=design_only，build_status=planned（已修正）。本裁定追溯确认其合法地位。

#### 裁定#203：合并 6a3c179e 会话发现的 3 项预存 DB 问题裁定

- **执行日期**: 2026-06-25
- **背景**: preexisting DB 问题调研期间，另一 AI 会话（6a3c179e）独立发现 5 项问题。经用户裁定，5 项问题统一归并到本会话处理（发现 3/5 并入 #ARCH-002/#ARCH-004，发现 1/2/4 由本裁定处理）。交接文档 `handover_to_session_6a3cacc8.md` 已按用户要求删除。

**本裁定涵盖 3 项子裁定**:

| 子裁定 | 对应议题 | 内容 | 状态 |
|--------|---------|------|:---:|
| #203-A | #ARCH-005 | layer_id 非法值修复（9 域 L1_platform→L1_foundation） | ✅ 已执行 (commit fadd3fdc) |
| #203-B | #ARCH-006 | 孤儿边 148 条清理 | ✅ 已执行 (commit 290df512 + 0a69d345) |
| #203-C | #ARCH-007 | lifecycle/build_status/layer_id CHECK 约束 + nodes DELETE 自动清理 edges | ✅ 已执行 (commit 87e793ec + 0a69d345) |

**#203-A 详情（layer_id 非法值修复）**:

`arch_layers` 表仅定义 4 个合法层（L0_infrastructure / L1_foundation / L2_domain / L3_application），但 DB 中有 9 个域使用了非法值 `L1_platform`（不在合法层表中）。其中 7 个为预存脏值，2 个（D_SECURITY-LLM / D_INTEGRATION-GATEWAY）为本会话阶段1错误沿用。

裁定采用方案C：将全部 9 个域的 layer_id 改为 `L1_foundation`（基础服务层）。

理由：
1. `L1_platform` 无任何架构依据，是预存脏值
2. 这 9 个域的 ssot_path 都是 `src/zephyr/xxx/` 基础服务路径，归属 L1_foundation 语义正确
3. 方案B（注册第5层）成本远大于收益；方案A（仅修2域）留下7个脏值治标不治本

修复后 layer_id 分布：L2_domain 32 / L1_foundation 15 / L0_infrastructure 5 / NULL 1（D_GOV_REPAIR，已 deprecated）。

**#203-B 详情（孤儿边清理）**:

edges 表有 148 条边引用了不存在的 node（from_node_id 或 to_node_id 在 nodes 表中不存在）。经验证：不涉及 node 50999/51005（两会话迁移的节点），是纯预存问题。

根因：edges 表 FK 无 `ON DELETE CASCADE`，删除 node 时不会自动清理引用它的边，长期累积形成孤儿边。

阶段4执行结果（commit 290df512 + 0a69d345）：
1. 在 `apply_depgraph.py` 新增 `cmd_cleanup_orphan_edges()` 命令 + `--cleanup-orphan-edges` CLI 参数（commit 87e793ec）
2. 执行清理：148 条孤儿边全部删除（commit 290df512）
3. 验证：`SELECT COUNT(*) FROM edges WHERE ...` 返回 0
4. 同时在 v12 迁移中新增 `trg_nodes_delete_cleanup_edges` 触发器，从根源杜绝孤儿边再生（见 #203-C）

**#203-C 详情（lifecycle/build_status/layer_id CHECK 约束）**:

domains 表 lifecycle/build_status/layer_id 三个字段当前均无 CHECK 约束。lifecycle 实际分布 4 值：operational(22) / design_only(19) / prototype(11) / deprecated(1)；build_status 合法 5 态（裁定#178）：planned→generated→testing→stable→deprecated；layer_id 合法 4 层（arch_layers 表）：L0_infrastructure / L1_foundation / L2_domain / L3_application。

裁定：接受当前 4 值为 lifecycle 合法值集合。理由：
1. 4 值覆盖域完整生命周期（生产运行→原型验证→纯设计态→已废弃）
2. 与 build_status 5 态互补（lifecycle 描述运行态，build_status 描述构建态）
3. 4 值已满足需求，不扩展

阶段4执行结果（commit 87e793ec + 0a69d345）：
1. 在 `depgraph_schema.py` `_MIGRATIONS` 列表新增 v12 迁移（7 个触发器），DDL 幂等执行
2. 7 个触发器：
   - `trg_nodes_delete_cleanup_edges`（AFTER DELETE ON nodes）：自动清理被删节点引用的 edges（根治 #203-B 根因）
   - `chk_domains_lifecycle_insert/update`：校验 lifecycle ∈ 4 值
   - `chk_domains_build_status_insert/update`：校验 build_status ∈ 5 值
   - `chk_domains_layer_id_insert/update`：校验 layer_id ∈ 4 值或 NULL
3. 修复 `apply_depgraph.py` 中 `cmd_insert_domain` 的默认值：max_modules 200→150（裁定#194 硬上限），build_status 'unbuilt'→'planned'（避免被触发器拦截）；`add_design_node` build_status 默认值 'unbuilt'→'planned'
4. 修复 D_GOV_REPAIR max_modules NULL → 150
5. 执行 `init_db()` 完成 v12 迁移，`_schema_version` 表新增版本 12 记录
6. 验证全部通过：schema_version=12，7 个新触发器存在，非法值插入测试 5 项全 PASS

**为何采用触发器而非 ALTER TABLE ADD CHECK**：早期 SQLite 的 `ALTER TABLE ADD CHECK` 在表已有数据时不会回溯校验，且不可与既有 DDL 合并；迁移至 PostgreSQL 后，PG 虽支持 `ALTER TABLE ADD CHECK NOT VALID` 延迟校验，但触发器方案仍具优势——支持 BEFORE INSERT/UPDATE 实时拦截 + 幂等创建（`CREATE OR REPLACE TRIGGER`，PG14+），更适合版本化迁移框架。

**合并说明**: 本裁定整合了 6a3c179e 会话的 5 项发现，统一归并到 preexisting 调研报告（`preexisting_db_issues_investigation_report.md` 附录B）。原交接文档已删除，避免信息分散。

---

#### 议题 #ARCH-008：vocabulary 同步链路根因性失效

- **发现日期**: 2026-06-25
- **影响等级**: P1（SSoT 硬约束被违反，但当前无运行时功能阻断）
- **关联议题**: #ARCH-005（layer_id 非法值）、#ARCH-007（CHECK 约束）、裁定#203-C
- **根因**: vocabulary YAML → 派生文件 / DB 缓存自动同步链路自项目建立以来从未真正工作过

**8 个 Bug（A~H）**:

| Bug | 位置 | 严重性 | 描述 |
|-----|------|:---:|------|
| A | generate_derived_files.py:81-91 | P0 | 路径常量用连字符+错扩展名（.md），磁盘上实际是 snake_case+.yaml/.json，`_sync_*` 函数静默返回 False 形成虚假绿灯 |
| B | sync_yaml_to_depgraph.py:441 | P0 | 键名错配（`field_name` vs `vocabulary_name`），DB `field_vocabularies` 表写入脏值 |
| C | generate_derived_files.py:175-177 | P1 | `enum_values` apply 分支恒 False（只处理 `allowed_values`，不处理 `enum_values`） |
| D | generate_derived_files.py:182/227/286 | P1 | `open()` 缺 `"w"` 模式，tmp 文件不存在时 `FileNotFoundError` 崩溃 |
| E | generate_derived_files.py:280 | P1 | schema_json `oneOf` 重写逻辑错（写空 `enum` 键，不清理 `oneOf`） |
| F | generate_derived_files.py:186/231/291 | P2 | 异常捕获太窄（仅 `PermissionError`，不捕获 `OSError`/`JSONDecodeError`/`YAMLError`） |
| G | sync_yaml_to_depgraph.py 全文 | P3 | 无跨进程并发保护（治理脚本中唯一缺事务隔离的 DB 写入者；迁移 PG 后由 MVCC 行级锁兜底，但建议显式事务包裹） |
| H | sync_yaml_to_depgraph.py:51 | P3 | `DB_PATH` 硬编码绝对路径，与 `_shared/constants.py` 不一致 |

**影响范围**: 7 个 Python 代码文件、8+ YAML/JSON 规则文件、6+ 文档/索引文件、3 个派生文件、1 个 DB 表（`field_vocabularies`）、2 个孤儿模块（`kb/triage.py`、`kb/pipeline/triage.py`）

---

#### 裁定#206：vocabulary 同步链路根因性修复

- **执行日期**: 2026-06-25 ~ 2026-06-26
- **背景**: 议题 #ARCH-008 浮现后，5 路并行深度调研综合编写修复方案（`vocabulary_sync_chain_repair_plan.md` v1.1），用户批准后执行

**本裁定涵盖 4 项子裁定**:

| 子裁定 | 对应议题 | 内容 | 状态 |
|--------|---------|------|:---:|
| #206-A | #ARCH-008 | 8 个 Bug 修复 + 派生文件重生成 + DB 脏值清理 + 孤儿模块删除 | ✅ 已执行 (commit 5326a70+764d425+03d2425+cc0fd08) |
| #206-B | #ARCH-009 | layer 命名体系统一为 layer_vocabulary.yaml 16 值语义命名，废弃 L0/L1/L2/L3 旧格式（方案 A） | ✅ 已执行 (commit 9bc18706) |
| #206-C | #ARCH-010 | apply_depgraph.py ALLOWED_LAYERS 与 DB CHECK 对齐 | ✅ 已执行 (commit 9bc18706) |
| #206-D | #ARCH-011 | layer_vocabulary.yaml 新增 dir_prefix 字段（根本方案） | ✅ 已执行 (commit 9b14586e) |

**#206-A 详情（8 个 Bug 修复）**:

修复链路分 6 个阶段（任务卡 OPS-2026062621~2626）：
1. 阶段0：depgraph 备份 + field_vocabularies 主键验证（2621）
2. 阶段1：修复 generate_derived_files.py Bug A/C/D/E/F（2622）
3. 阶段2：修复 sync_yaml_to_depgraph.py Bug B + field_vocabularies 134 条脏值清理（2623, commit 5326a7038）
4. 阶段3：重生成 3 个派生文件 + 重跑 sync（2624, commit 764d42591）
5. 阶段4：修复 4 处 validator 硬编码 layer 改为 vocabulary 动态加载（2625, commit 03d2425f9）
6. 阶段5：删除 2 个孤儿 triage.py + 修复主版 triage.py 硬编码（2626, commit cc0fd0830）

**#206-B 详情（layer 命名体系统一）**:

裁定采用方案 A：layer 字段统一用 layer_vocabulary.yaml 的 16 值语义命名（data/infra_ops/factor/signal/risk/pf_core/ex_core/reporting/frontend/research/compliance/ml_train/system/telemetry/simulation/shared/cross_layer），废弃 L0/L1/L2/L3 旧格式。

理由：
1. L0/L1/L2/L3 是 layer_vocabulary.yaml 注释中明确标记为"废弃"的旧格式
2. 16 值语义命名是 SSoT（layer_vocabulary.yaml），自 2026-05-03 创建以来即为真源
3. 所有治理规则文件（trae_*.yaml）的 layer 字段统一为 `compliance`（映射与旧 L 值无关）

执行（任务卡 OPS-2026062627）：
1. 修复 59 个 trae_*.yaml 的 layer 字段 L0/L1/L2/L3 → compliance（commit 9bc187061）
2. 修复 g2_triage.yaml valid_layers（18→16）
3. 修复 apply_depgraph.py ALLOWED_LAYERS（L1_platform→L3_application）

**#206-C 详情（apply_depgraph.py 对齐）**:

修复 apply_depgraph.py 的 ALLOWED_LAYERS 常量，从硬编码的 L1_platform 改为从 layer_vocabulary.yaml 动态加载，与 DB CHECK 约束对齐（commit 9bc187061）。

**#206-D 详情（dir_prefix 字段——已执行）**:

在 layer_vocabulary.yaml 16 个 entry 中新增 `dir_prefix` 字段（data→l00_、infra_ops→l01_、factor→l02_、signal→l03_、risk→l04_、pf_core→l05_、ex_core→l06_、reporting→l07_、frontend→l08_、research→l09_、compliance→l10_、ml_train→l11_、system-telemetry→l12_、simulation→l13_，shared/cross_layer→空字符串），schema_version 1.0.0→1.1.0；`validate_blueprint_placement.py` 删除 `_LAYER_DIR_PREFIX_MAP` 硬编码映射表，`_layer_to_dir_prefix()` 改为从 `layer_vocabulary.yaml` 的 `dir_prefix` 字段动态读取，消除映射表硬编码漂移风险（任务卡 OPS-2026062646，commit 9b14586e2）。

后续 GATE-GENERATE hook 接入（任务卡 OPS-2026062647，commit cfcf35be）：在 `.pre-commit-config.yaml` GATE-19 之后追加 `gate-generate-derived` hook，当 vocabulary YAML 变更时自动触发 `generate_derived_files.py --check --warn-only` 校验派生文件一致性（骨架阶段 warn-only，验证稳定后转硬阻断）。至此裁定#206 全部 4 项子裁定（A/B/C/D）均已执行完毕。

**kebab-case 路径引用清理（任务卡 OPS-2026062628）**:

清理全项目 kebab-case 文件路径引用，统一为 snake_case（commit e3a3e821，54 个文件）。包括 18 个 vocabulary 文件名引用、module_id 注释头、BUG 修复（refresh_master_entries.py:85 stem 检查）。

---

### 20.13 V5.9 域 ID 统一与 schema 治本裁定（#ARCH-REN-001 / #ARCH-016 / #208，2026-06-26~30）

#### 裁定#ARCH-REN-001：域 ID 连字符→下划线统一（2026-06-26）

- **执行日期**: 2026-06-26
- **背景**: 6 个域 ID 含连字符（kebab-case），违反 snake_case 命名约束（AGENTS.md 硬约束）
- **变更**: D_GOV_AUDIT_TESTS→D_AUDITTEST、D_INTEGRATION-GATEWAY→D_INTEGRATION_GATEWAY、D_SECURITY-LLM→D_SECURITY_LLM（其余 3 个已是下划线）
- **状态**: ✅ 已执行（迁移脚本 `migrate_domain_id_hyphen_to_underscore.py`）

#### 裁定#ARCH-016：schema dead column 清理（v15/v16/v17，2026-06）

- **执行日期**: 2026-06（v15-v17 分批执行）
- **背景**: nodes/edges/arch_directory_tree 表累积 11 个 dead/drifted 列 + 1 个孤儿触发器 + 1 个陈旧索引
- **v15**（治本）: 删除 11 个 dead columns + 重建 arch_directory_tree（移除 node_id FK）；nodes 列数 41→31，edges 列数 23→22（删 migration_status），arch_directory_tree 列数 11→10
- **v16**（残留）: 删除孤儿触发器 `chk_edges_design_immutable_update`
- **v17**（残留）: 删除陈旧索引 `idx_domains_can_build`
- **状态**: ✅ 已执行（`_MIGRATIONS` v15/v16/v17）

#### 裁定#208：blueprint_id 双轨制+历史兼容 CHECK 触发器（v18，2026-06-30）

- **执行日期**: 2026-06-30
- **背景**: blueprint_id 字段需强制双轨制+历史兼容格式（MOD-*/D-*/SH-*/PLACEHOLDER*）
- **变更**: 新增 BEFORE INSERT + BEFORE UPDATE OF blueprint_id 触发器，校验 blueprint_id 符合四类前缀之一
- **状态**: ✅ 已执行（`_MIGRATIONS` v18）

---

### 20.14 P2/P3 PostgreSQL 迁移裁定（2026-06-27~28）

#### P2 迁移：SQLite → PostgreSQL 16（2026-06-27）

- **执行日期**: 2026-06-27
- **背景**: SQLite 文件级写锁导致 40+AI 并发写入瓶颈（39 个等待 1 个写）
- **变更**:
  - depgraph 从 SQLite 迁移至 PostgreSQL 16，获得 MVCC 行级锁并发能力
  - SQLite 物理文件 `data/databases/depgraph.db` 已删除归档
  - PG schema 真源：`scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql`（25 表 + 1 视图 + 39 索引 + 28 触发器）
  - 删除文件锁补丁（apply_depgraph.py / generate_project_depgraph.py / sync_yaml_to_depgraph.py）
  - SQL 方言调整：AUTOINCREMENT→GENERATED AS IDENTITY、INSERT OR REPLACE→ON CONFLICT、PRAGMA 全删、sqlite_master→information_schema
- **状态**: ✅ 已执行（详见 `docs/03_modules/_cross_layer/database/sub_blueprints/mod_inf_012b_p2_postgresql_migration.md`）

#### P3 优化：pgvector/LISTEN-NOTIFY/分区表/监控告警（2026-06-28 裁定，2026-06-30 文档归档删除）

- **执行日期**: 2026-06-28 裁定 / 2026-06-30 文档归档删除
- **变更**:
  - P3-T1: pgvector 改造（待VMS code_context自然演进，不新建pgvector）
  - P3-T2: LISTEN-NOTIFY 机制裁定删除（伪需求，100% AI开发无常驻监听者）
  - P3-T3: 分区表裁定删除（24MB过度工程，edges无domain_id列）
  - P3-T4: 监控告警改造已实现（扩展verify_schema_health.py事件驱动检查）
- **状态**: P3文档已于2026-06-30归档删除（T2/T3裁定删除，T1待VMS演进，T4已实现）。裁定约束见AGENTS.md §11.2
- **当前规模**: edges 表 6,197 行 / 24MB（P3 审查时记录，AGENTS.md §11.2）
