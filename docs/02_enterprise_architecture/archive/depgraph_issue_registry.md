# 依赖全景图问题注册表

> **文档责任**：记录 depgraph.db 当前所有已知问题、根因、修复方案、优先级和状态。RooCode 执行者直接消费此文档。
> **文档生命周期**：问题修复完成→状态改为 CLOSED→定期清理 CLOSED 项。施工完成的内容可删除。
> **关联文档**：
> - 能力定位书（`依赖与架构全景图能力定位书.md` V5.4）：定义全景图的能力边界和设计裁定
> - 架构升级讨论（`architecture_upgrade_discussion.md` V2.6.0）：项目导航图、决策链、方法论。七批次施工（P0-1~P0-7）全部完成（2026-06-18）
>
> **2026-06-17 文档合并说明**：本文件已合并以下两个文档的内容（修复方案+生成器问题），原文件已删除：
> - `depgraph_fix_plans.md`（2255行，修复方案+执行顺序因果链）
> - `generator_issues.md`（224行，生成器问题 G1-G6）

---

## 一、问题总览

> **最后更新**: 2026-06-19，全部12张任务卡执行完毕（DM-100242~DM-100251 + SRC-100295 + OPS-2026061804）。七批次施工（P0-1~P0-7）+ 深度审查 + RECHECK + 修复任务全部CLOSED。
> **深度审查**: 2026-06-18 按设计态/运营态分别审查所有OPEN问题。大量问题被重新定性。2026-06-19 完成7项RECHECK和5项修复任务。

| Phase | 问题数 | 已完成 | 需重新校验 | 待修复 | 未来扩展 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| P0 | 3 | 3 | 0 | 0 | 0 |
| H | 9 | 9 | 0 | 0 | 0 |
| J | 4 | 4 | 0 | 0 | 0 |
| A | 4 | 4（A1/A2暂缓/A3/A4已修复） | 0 | 0 | 0 |
| I | 18 | 18（I1-I18全部CLOSED） | 0 | 0 | 0 |
| E | 5 | 5（E1-E5全部CLOSED） | 0 | 0 | 0 |
| C | 3 | 3（C1/C2/C3全部CLOSED） | 0 | 0 | 0 |
| B | 3 | 3（B1/B2/B3全部CLOSED） | 0 | 0 | 0 |
| F | 2 | 2（F1/F2） | 0 | 0 | 0 |
| K | 1 | 1（K1已CLOSED，决策文档已交付） | 0 | 0 | 0 |
| D | 3 | 0 | 0 | 0 | 3 |
| G | 6 | 6 | 0 | 0 | 0 |

> **深度审查结论（2026-06-19 最终更新）**：
> - **15项CLOSED**：I2/I14/I9（设计态误报/契约）、B1/F1/F2（扩展阶段正常）、B3/E2/E3/E4/C2（搬迁后解决）、A2/A3/I17/I18（已解决/暂缓）
> - **7项RECHECK全部CLOSED**：I5（belongs_to存模块ID非node_id，real broken=0）、I13（real code orphans=0）、A4（cross-domain cycles=0）、I8（无build_status消费者）、I15（无nodes.tags消费者）、E5（无last_verified消费者）、C1（3字段无需索引）
> - **5项真正需修复全部CLOSED**：B2（安全敏感文件标记）、E1（旧层名清理，10条记录已删）、C3（门禁增量扫描）、K1（3项待定决策文档已交付）、G5（生成器域名双源统一，DM-100242）
> - **3项未来扩展**：D1/D2/D3（1500模块完成后）
>
> **当前数据质量（2026-06-19，全部任务卡完成后）**：8555节点，8083-8087边，61域，0循环，4 arch_layers（标准层）。所有RECHECK和修复任务均已CLOSED。

---

## 二、已关闭问题摘要

> 以下问题已在七批次施工（P0-1~P0-7）中全部修复并验证通过。修复代码在 `generate_project_depgraph.py`，git log 可追溯细节。

| Phase | 问题数 | 摘要 | 验证结果 |
|:---:|:---:|------|------|
| P0 | 3 | 生成器4bug + 设计态恢复 + 假blueprint_id | 0重复/0空/0假ID |
| H | 9 | H1-H9 生成器根因级修复（路径/ID/边字段/容量/约束/扫描目录） | 8746节点/8229边/61域，数据质量全绿 |
| J | 4 | J1-J4 Schema偏差（design_maturity/event_type/domain_id列缺失） | 列均已存在 |

---

## 三、Phase A：数据治理——让设计生效

### A1：架构层标签混乱（15种→4种）— 已修复 ✅

> **2026-06-17 更新**：基于实际数据库验证，architecture_layer 现在只有4种标准层，无非标准层。NULL值已从1,045降为0。此问题已完全修复。

**问题（历史）**：当前仅4标准层(L0-L3)+0个NULL值（已修复），非标准层值已全部映射到标准层。

**当前实际分布**（2026-06-17 验证）：

| architecture_layer | 节点数 | 占比 | 状态 |
|-------------------|------:|----:|------|
| L1_foundation | 3,478 | 45.8% | ✅ 标准层 |
| L3_application | 2,120 | 27.9% | ✅ 标准层 |
| L2_domain | 1,330 | 17.5% | ✅ 标准层 |
| L0_infrastructure | 662 | 8.7% | ✅ 标准层 |

标准4层覆盖100%节点。**已修复，无需进一步操作。**

**历史映射规则**（供追溯）：

| 旧值 | → 标准值 | 依据 |
|------|---------|------|
| infrastructure | L0_infrastructure | 同义 |
| governance | L1_foundation | 治理=基础层 |
| intelligence | L1_foundation | 智能基础 |
| shared | L1_foundation | 共享基础 |
| data | L2_domain | 数据域 |
| signal | L2_domain | 信号域 |
| simulation | L2_domain | 模拟域 |
| domain | L2_domain | 同义 |
| L1/L0/L2(简写) | 对应标准值 | 补全 |

**验证 SQL**：

```sql
SELECT architecture_layer, COUNT(*) FROM nodes GROUP BY architecture_layer;
-- 期望：仅4种标准层值（已验证通过）
```

| 状态 |
|:---:|
| CLOSED ✅ |

**新发现补充（2026-06-15）**：
- **node_id格式不统一**：部分节点使用path-based格式（如`src/zephyr/governance/audit_trail/__init__.py`），部分节点使用domain-module混合格式（如`D-DATA:module_name`）。根因：生成器在不同代码路径使用了不同的ID生成策略，缺少统一的node_id命名规范。影响：跨表JOIN不稳定、手工查询困难。

### A2：超容域拆分与域-层映射

**问题**：
1. 部分域映射指向旧叙事层，需重映射到L0-L3
2. 部分域 current_modules 超过 max_modules，需评估拆分

**修复方案**：
1. 所有域重映射到L0-L3：业务域→L2_domain, 平台域→L1_foundation, 横切域→L1_foundation, 基础设施→L0_infrastructure
2. 超容域评估拆分（当前无需执行，详见下文）

> **2026-06-18 更新**：原方案以 D-SECURITY 拆分为例，但 D-SECURITY 已不在超容域清单（已通过其他方式解决）。当前超容域详见 §十二。**当前无需拆分任何域**（D-TEST已豁免，其余轻微超容通过max_modules调整解决）。拆分 SQL 示例保留供未来参考。

**超容域拆分 SQL（通用模板，以 D-SECURITY 拆分为例）**：

```sql
-- A2: 超容域拆分 — D-SECURITY → D-SECURITY + D-SECURITY-LLM

-- Step 1: 创建新域 D-SECURITY-LLM
INSERT OR IGNORE INTO domains (domain_id, domain_name, domain_group, description, ssot_path, current_modules, max_modules, lifecycle, created_at, updated_at, build_status, can_build)
VALUES ('D-SECURITY-LLM', '安全-LLM', '安全', 'LLM安全子域。负责LLM防火墙、提示注入检测、安全审计等AI安全功能。', 'src/zephyr/security/llm/', 0, 80, 'operational', datetime('now'), datetime('now'), 'production', 1);

-- Step 2: 创建容量记录
INSERT OR IGNORE INTO arch_domain_capacity (domain_id, current_modules, max_modules, last_capacity_check)
VALUES ('D-SECURITY-LLM', 0, 80, datetime('now'));

-- Step 3: 创建层映射
INSERT OR IGNORE INTO arch_domain_layers (domain_id, layer_id)
VALUES ('D-SECURITY-LLM', 'L1_foundation');

-- Step 4: 重新分配节点到新域（依据路径规则）
UPDATE nodes SET domain_id = 'D-SECURITY-LLM'
WHERE domain_id = 'D-SECURITY'
  AND (path LIKE 'src/zephyr/security/llm/%'
       OR path LIKE 'src/zephyr/security/%llm%'
       OR path LIKE 'src/zephyr/security/%prompt%');

-- Step 5: 更新容量
UPDATE domains SET current_modules = (
    SELECT COUNT(*) FROM nodes WHERE domain_id = domains.domain_id
), updated_at = datetime('now');

UPDATE arch_domain_capacity SET current_modules = (
    SELECT COUNT(*) FROM nodes WHERE domain_id = arch_domain_capacity.domain_id
), last_capacity_check = datetime('now');
```

**验证命令**：

```sql
-- 验证拆分后无超容域（或超容倍数显著降低）
SELECT domain_id, current_modules, max_modules,
       CAST(current_modules AS REAL) / max_modules as ratio
FROM arch_domain_capacity
WHERE current_modules > max_modules
ORDER BY ratio DESC;
-- 期望：D-SECURITY 和 D-SECURITY-LLM 均 ≤80
```

**回滚方案**：

```sql
-- 回滚 D-SECURITY 拆分
UPDATE nodes SET domain_id = 'D-SECURITY' WHERE domain_id = 'D-SECURITY-LLM';
DELETE FROM arch_domain_layers WHERE domain_id = 'D-SECURITY-LLM';
DELETE FROM arch_domain_capacity WHERE domain_id = 'D-SECURITY-LLM';
DELETE FROM domains WHERE domain_id = 'D-SECURITY-LLM';
```

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-18 深度审查**：D-TEST已豁免，其余域轻微超容（1.0x-1.2x），通过max_modules调整解决，无需拆分。

### A3：容量数据过时

**问题**：部分域 current_modules 与 max_modules 不一致，容量表需与实际同步。

> **2026-06-17 更新**：原方案称"11个域超80模块硬上限"，但当前实际只有8个超容域（详见§十二），且大部分轻微超容（1.0x-1.2x）。D-GOVERNANCE（max已调整为750）和 D-SECURITY 已不在超容清单。

**修复方案**：
1. 从nodes COUNT(*)更新current_modules
2. 按D76三档设定max_modules（16域×80 + 19域×60 + 5域×40）
3. D-TEST 和 D-GOV-DOCS 因内部依赖极少/零内部依赖，豁免80模块限制（已裁定）

**[A3与H7同根因]**。H7 修复后重新生成，A3 自动解决。

**验证命令**：

```sql
-- H7修复后验证
SELECT d.domain_id, d.current_modules,
       (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id) as actual
FROM domains d
WHERE d.current_modules != (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id);
-- 期望：0 rows
```

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-18 深度审查**：H7已修复current_modules计算，61域已同步。

### A4：循环依赖（8组循环，dep_cycles视图）

**问题**：当前（61域，2026-06-18）dep_cycles视图含8行循环依赖数据。

> **2026-06-18 验证**：基于实际数据库 dep_cycles 视图，8行循环依赖。旧文档中的17组双向依赖对基于52域快照，已过时。

**历史双向依赖对参考**（52域快照，当前实际为8组循环，以 dep_cycles 视图为准）：

| 域集群 | 双向依赖对 | 边数 |
|--------|-----------|:---:|
| 数据域集群 | D-ALT_DATA ↔ D-DATA_ENG | 1/1 |
| | D-ALT_DATA ↔ D-DATA_GOV | 1/1 |
| | D-ALT_DATA ↔ D-DATA_SEC | 1/1 |
| | D-ALT_DATA ↔ D-MKT_DATA | 1/1 |
| | D-DATA_ENG ↔ D-DATA_GOV | 1/1 |
| | D-DATA_ENG ↔ D-DATA_SEC | 1/1 |
| | D-DATA_ENG ↔ D-MKT_DATA | 1/1 |
| 投资组合集群 | D-CROSS_ASSET ↔ D-PF_CORE | 1/1 |
| | D-PF_ALLOC ↔ D-PF_CORE | 1/1 |
| | D-PF_CORE ↔ D-RISK | 1/1 |
| 风险信号集群 | D-POSITION ↔ D-RISK | 1/1 |
| | D-RISK ↔ D-SIGNAL | 1/1 |
| | D-RISK ↔ D-SIGNAL_ASHARE | 1/1 |
| | D-RISK ↔ D-SIGNAL_FUNDAMENTAL | 1/1 |
| | D-RISK ↔ D-SIGNAL_QUALITY | 1/1 |
| ML集群 | D-ML_SERVE ↔ D-ML_TRAIN | 1/1 |
| 交易报表 | D-REPORTING ↔ D-TRADING | 1/1 |

**修复方案**（方法论）：
- 数据域集群（7组）：D-ALT_DATA 作为数据源被多个数据域双向引用 → 引入事件总线，数据域单向订阅 D-ALT_DATA
- 投资组合集群（3组）：D-PF_CORE 作为核心被双向引用 → 定义窄接口契约（contracts 表）
- 风险信号集群（5组）：D-RISK 与多个信号域双向引用 → 观察者模式，D-RISK 单向订阅信号
- ML集群（1组）：D-ML_SERVE ↔ D-ML_TRAIN → 接口隔离，训练结果通过契约发布
- 交易报表（1组）：D-REPORTING ↔ D-TRADING → 观察者模式，报表单向订阅交易事件

**检测 SQL**：

```sql
-- A4.1: 域级双向依赖（当前实际数据）
SELECT d1.from_domain, d1.to_domain, d1.edge_count, d2.edge_count as reverse_count
FROM domain_dependencies d1
JOIN domain_dependencies d2
  ON d1.from_domain = d2.to_domain AND d1.to_domain = d2.from_domain
WHERE d1.from_domain < d1.to_domain
ORDER BY d1.from_domain;

-- A4.2: 节点级双向import
SELECT e1.from_node_id, e1.to_node_id
FROM edges e1
JOIN edges e2 ON e1.from_node_id = e2.to_node_id AND e1.to_node_id = e2.from_node_id
WHERE e1.from_node_id < e1.to_node_id
  AND e1.dep_type = 'import_depends'
  AND e2.dep_type = 'import_depends';
```

**拆解策略**（不直接执行，供架构决策参考）：

| 循环集群 | 策略 | 具体操作 |
|---------|------|---------|
| 数据域集群（7组） | 事件总线解耦 | D-ALT_DATA 发布数据事件，D-DATA_ENG/GOV/SEC/MKT_DATA 单向订阅 |
| 投资组合集群（3组） | 接口隔离 | D-PF_CORE 定义窄接口契约（contracts 表），D-PF_ALLOC/D-CROSS_ASSET/D-RISK 单向依赖 |
| 风险信号集群（5组） | 观察者模式 | D-SIGNAL* 发布信号事件，D-RISK 单向订阅 |
| ML集群（1组） | 接口隔离 | D-ML_TRAIN 通过 contracts 发布模型，D-ML_SERVE 单向消费 |
| 交易报表（1组） | 观察者模式 | D-TRADING 发布交易事件，D-REPORTING 单向订阅 |

**验证**：`diagnose_depgraph.py` → 0 双向依赖对

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-19 复审完成（DM-100250）**：检测2节点循环（A→B且B→A）共3个，全部为同域循环（Python包结构正常现象，模块与__init__.py互导）。跨域循环=0。dep_cycles视图7行循环均为同域内循环或设计态文档循环，无架构问题。

> **2026-06-18 深度审查**：需过滤出跨域循环。dep_cycles视图8行样本显示：D-GOV-AUDIT内部（audit_admission_controller.py ↔ __init__.py，同域内循环，Python包结构正常现象）、D-GOVERNANCE内部（多个blueprint.md互相引用，设计态文档循环，正常）、D-TEST（测试文件，测试制造的循环，正常）。
> **正确做法**：同域内循环（模块导入__init__.py，__init__.py又导入模块）是Python包结构的正常现象。只有跨域循环才是架构问题。需过滤出跨域循环。

---

## 四、Phase B：安全与稳定性

### B1：稳定性分级虚设（88.8% evolving）+ G3：生成器不解析[STABILITY]标记

**问题**：当前分布（2026-06-17 验证）：evolving=6,737(88.8%), stable=759(10.0%), frozen=79(1.0%), volatile=15(0.2%)。分级形同虚设。

**根因（G3，已修复✅）**：生成器 `scan_py_file()` 中 `parse_blueprint_header()` 未正确解析文件头 `[STABILITY]` 标记。G3 已随 P0-3 生成器升级完成修复——生成器现已能正确解析标记。**剩余问题**：代码文件中 `[STABILITY]` 标记覆盖率仍不足，需系统性补充标记。

**修复方案**：

1. **按规则分级**——核心不变量→frozen, 已发布API→stable, 开发中→evolving, 实验→volatile
2. **G3已修复✅**：生成器现已正确解析 `[STABILITY]` 标记。B1 剩余工作为补充代码文件中的标记覆盖率。

**目标**：frozen≥5%, stable≥20%, evolving≤70%, volatile≤5%

**验证 SQL**：

```sql
-- B1: stability分布
SELECT change_policy, COUNT(*) FROM nodes GROUP BY change_policy ORDER BY COUNT(*) DESC;
-- 目标：frozen≥5%, stable≥20%, evolving≤70%, volatile≤5%
```

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-18 深度审查**：当前节点分布为 prototype 66.6% / design 24.2% / production 9.2%。66.6%的节点是prototype，标 evolving 是实际状态——实验性代码确实在频繁变化。等代码从prototype转production后，再调整稳定性标记。当前阶段不是问题。

### B2：安全边界薄（96.9% ai_modifiable）+ G4：生成器不解析[AI_AUTONOMY]标记

**问题**：当前分布（2026-06-17 验证）：ai_modifiable=7,359(96.9%), human_gated=161(2.1%), immutable_core=70(0.9%)。安全风险高。

**根因（G4，已修复✅）**：生成器 `scan_py_file()` 中 `parse_blueprint_header()` 未正确解析文件头 `[AI_AUTONOMY]` 标记。G4 已随 P0-3 生成器升级完成修复——生成器现已能正确解析标记。**剩余问题**：代码文件中 `[AI_AUTONOMY]` 标记覆盖率仍不足，需系统性补充标记。

**修复方案**：

1. **按安全分级**——安全组件+核心引擎→immutable_core, 配置+策略→human_gated, 业务逻辑→ai_modifiable
2. **G4已修复✅**：生成器现已正确解析 `[AI_AUTONOMY]` 标记。B2 剩余工作为补充代码文件中的标记覆盖率。

**目标**：immutable_core≥5%, human_gated≥15%, ai_modifiable≤80%

**验证 SQL**：

```sql
-- B2: ai_autonomy分布
SELECT modification_permission, COUNT(*) FROM nodes GROUP BY modification_permission ORDER BY COUNT(*) DESC;
-- 目标：immutable_core≥5%, human_gated≥15%, ai_modifiable≤80%
```

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-19 修复完成（SRC-100295）**：扫描任务卡指定的4个安全敏感文件，将2个有[AI_AUTONOMY]字段的文件从ai_modifiable改为human_gated：gateway.py（LLM安全网关，MOD-SEC_gateway）和kill_switch.py（紧急制动，MOD-RES_kill_switch，SAFETY=H）。3个文件（llm_security_01/gateway.py、scripts/rollback.py、security/access_control/kill_switch.py）无[AI_AUTONOMY]字段未修改。注：整体分布目标（human_gated≥15%）需后续系统性补充标记。

### B3：物理路径冲突

**问题**：部分域共享同一物理路径前缀。根因与 H1 相关（生成器路径处理），但 H1 修复的是重复路径，B3 是域间路径前缀冲突——不同症状。

> **2026-06-17 更新**：原方案引用 D-DATA_GOV/D-DATA_SEC 等域名，但这些域名在当前 domains 表中未定义。实际路径冲突需基于当时52域重新检测。**注意**：七批次施工后域数已增至61域，路径冲突需重新检测。

**修复方案**：按域隔离路径——检测当前多域共享同一物理路径前缀的情况，按域重新分配独占路径。

**验证**：`SELECT path, COUNT(DISTINCT domain_id) FROM nodes GROUP BY path HAVING COUNT(DISTINCT domain_id) > 1` → 0

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-18 深度审查**：3个冲突（src/zephyr/data/ 3域、src/zephyr/integration/ 2域、src/zephyr/signal/ 2域）正是路径全景图搬迁要解决的问题。搬迁后每个域有独立路径前缀，B3自动消失。无需独立修复。

---

## 五、Phase C：性能与扩展性

### C1：缺失3个关键索引（原12个，已修复9个）

> **2026-06-17 更新**：基于实际数据库验证，21个索引已存在。原方案称"缺失12个索引"，实际只缺3个。

**当前已存在的索引**（21个）：

| 表 | 已有索引 |
|------|---------|
| nodes | idx_nodes_arch_layer, idx_nodes_blueprint, idx_nodes_build_status, idx_nodes_can_build, idx_nodes_change_policy, idx_nodes_domain, idx_nodes_file_path, idx_nodes_impact, idx_nodes_modperm, idx_nodes_path, idx_nodes_type |
| edges | idx_edges_cross_domain, idx_edges_dep_type, idx_edges_from, idx_edges_to |
| domains | idx_domains_can_build, idx_domains_group, idx_domains_lifecycle |
| domain_dependencies | sqlite_autoindex_domain_dependencies_1 |

**仍缺失的3个索引**：

| 表 | 缺失索引 | 影响 |
|------|---------|------|
| nodes | last_verified | 验证时间范围查询无保障 |
| edges | coupling_strength | 耦合强度筛选全表扫描（8,229行） |
| domain_dependencies | constraint_type | 约束类型查询全表扫描 |

**修复方案 — CREATE INDEX SQL**（仅3个）：

```sql
-- C1: 创建3个仍缺失的索引
CREATE INDEX IF NOT EXISTS idx_nodes_last_verified ON nodes(last_verified);
CREATE INDEX IF NOT EXISTS idx_edges_coupling_strength ON edges(coupling_strength);
CREATE INDEX IF NOT EXISTS idx_domain_dependencies_constraint_type ON domain_dependencies(constraint_type);
```

**验证 SQL**：

```sql
SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND tbl_name IN ('nodes', 'edges', 'domains', 'domain_dependencies') ORDER BY tbl_name, name;
```

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-19 复审完成（DM-100251）**：3个字段查询频率分析：last_verified查询0次（无消费者）、coupling_strength查询2次（diagnose_depgraph.py低频诊断，基数仅7索引选择性差）、constraint_type查询0次（无SQL WHERE查询）。3个字段均不需要创建索引。

> **2026-06-18 深度审查**：需确认查询频率。edges.coupling_strength仅7个不同值（基数太低，索引效果有限）。nodes.last_verified有290个不同值，加索引有一定效果。但如果这些字段不常被查询，索引无意义。
> **正确做法**：确认这些字段是否常被查询。如果不常查询，不需要加索引。

### C2：测试目录扁平（2,104文件）

**问题**：tests/目录扁平，单目录文件过多。

**修复方案**：按域分组——tests/_domain_mkt_data/, tests/_domain_risk/, ...

**与 D-TEST 目录整理合并处理**（A2当前无需拆分任何域，D-TEST已豁免）。`tests/` 目录按被测域分子目录。

**验证**：无单目录>200文件

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-18 深度审查**：路径全景图搬迁计划包含测试目录重组。搬迁后自然解决。

### C3：门禁全量扫描

**问题**：门禁全量扫描，执行时间长。

**修复方案**：实现增量门禁——只扫描变更文件影响的门禁

**验证**：门禁执行时间<30s

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-19 修复完成（OPS-2026061804）**：为 audit_registration.py 添加 --incremental 和 --full 参数。--incremental 通过 `git diff --name-only HEAD` + `git ls-files --others` 获取变更文件列表，仅扫描变更文件；--full 显式全量扫描（默认）。四个扫描函数（_scan_module_orphans/_scan_script_orphans/_scan_gate_orphans/_detect_missing_all）均支持 changed_files 过滤。验证：单文件增量扫描返回1问题，全量扫描返回717问题（预存孤儿），过滤逻辑正确。注：当前 exit=1 因有717个预存孤儿，非C3引入。

---

## 六、Phase D：未来扩展

| # | 问题 | 依赖 | 状态 |
|---|------|------|:---:|
| D1 | 蓝图注册表缩放 | A1(✅CLOSED),A2 | OPEN |
| D2 | 知识库大规模查询 | — | OPEN |
| D3 | 冷启动不可控 | A1(✅CLOSED)~C3 | OPEN |

---

## 七、Phase E：审计清理

> 与 Phase A 并行执行。清理 AI vibe coding 产生的膨胀和残留。

### E1：arch_layers 表10条零引用遗留记录

**问题**：arch_layers 表有14条记录，但只有4条标准层（L0-L3）被 nodes 表实际使用。其余10条（shared/contracts/meta/infrastructure/data/signal/domain/intelligence/simulation/governance）零节点引用，仅在 arch_path_mappings 的 path_prefix 字段中有残留路径。

**根因**：新老两套分层体系并存。生成器迁移时只更新了 nodes 的 architecture_layer，但 arch_layers 表的老条目没有清理。

**修复方案 — DELETE SQL**：

```sql
-- E1: 识别零引用层
SELECT l.layer_id, l.layer_name,
       (SELECT COUNT(*) FROM nodes n WHERE n.architecture_layer = l.layer_id) as node_count
FROM arch_layers l
ORDER BY node_count ASC;

-- 删除零引用且非标准层的记录
DELETE FROM arch_layers
WHERE layer_id NOT IN ('L0_infrastructure', 'L1_foundation', 'L2_domain', 'L3_application')
  AND layer_id NOT IN (
    SELECT DISTINCT architecture_layer FROM nodes WHERE architecture_layer IS NOT NULL AND architecture_layer != ''
  );

-- 验证
SELECT * FROM arch_layers;
-- 期望：仅 L0-L3 4条记录
```

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-19 修复完成（DM-100243）**：从 arch_layers 表删除 10 条零引用旧层名记录（shared/contracts/meta/infrastructure/data/signal/domain/intelligence/simulation/governance），仅保留 4 条标准层（L0_infrastructure/L1_foundation/L2_domain/L3_application）。验收：非标准层计数=0，总计数=4，nodes 表无孤儿层引用。备份：depgraph.db.backup.e1_20260619_005606。

### E2：文件级审计清理

**问题**：AI vibe coding 产生大量临时/残留/空壳文件。

| 清理项 | 预估数量 | 方法 |
|--------|---------|------|
| __init___from_* 合并残留 | ~19个 | 确认无引用后删除文件+DB记录 |
| _archive/ 归档脚本 | 26个 | 移出或标记为 archived |
| _temp* / _check* / _repair* 临时文件 | ~264个 | 按 RULE-FIVE 零残留原则清理 |
| _extensions/ 空壳 | 38个 | 确认无实际功能后删除 |
| 重复节点（16个文件410条重复） | 410条 | ✅ H1修复后重跑生成器已自动清除 |

**磁盘膨胀分布**：

| 目录 | .py文件数 | 说明 |
|------|--------:|------|
| src/zephyr/governance/ | 1,032 | 治理域膨胀最严重 |
| tests/ | 2,104 | 测试扁平 |
| scripts/governance/ | 534 | 治理脚本 |
| src/zephyr/ops/ | 367 | 运维 |
| src/zephyr/integration/ | 297 | 集成 |
| src/zephyr/security/ | 305 | 安全 |

**清理 SQL 模板**（待RooCode执行时按实际数据调整）：

```sql
-- E2.1: 识别 __init___from_* 合并残留
SELECT node_id, path FROM nodes
WHERE path LIKE '%__init___from_%';

-- E2.2: 识别 _archive/ 归档脚本
SELECT node_id, path FROM nodes
WHERE path LIKE '%_archive/%' OR path LIKE '%\_archive\_%' ESCAPE '\';

-- E2.3: 识别临时文件（_temp*/_check*/_repair*）
SELECT node_id, path FROM nodes
WHERE path LIKE '%_temp%' OR path LIKE '%_check%' OR path LIKE '%_repair%'
   OR path LIKE '%_fix%' OR path LIKE '%_phase_%' OR path LIKE '%_audit%';

-- E2.4: 识别 _extensions/ 空壳
SELECT node_id, path FROM nodes
WHERE path LIKE '%_extensions/%';

-- E2.5: 删除确认无引用的临时文件DB记录（需逐个确认后执行）
-- DELETE FROM nodes WHERE node_id IN (...确认列表...);
-- DELETE FROM edges WHERE from_node_id IN (...确认列表...) OR to_node_id IN (...确认列表...);
```

**应用层清理脚本实现要点**（待RooCode执行时编写）：

```python
# 脚本位置建议：D:/ZephyrAlpha/scripts/governance/repair/cleanup_e2_files.py
# 策略：对每个候选文件，检查是否被其他文件import，无引用则删除文件+DB记录
import sqlite3, os, ast

DB = 'data/databases/depgraph.db'
PROJECT_ROOT = 'D:/ZephyrAlpha'

def is_referenced(target_path, all_paths):
    """检查目标文件是否被其他文件import"""
    target_module = target_path.replace('/', '.').replace('.py', '')
    for p in all_paths:
        if p == target_path:
            continue
        full = os.path.join(PROJECT_ROOT, p.replace('/', os.sep))
        if not os.path.exists(full):
            continue
        try:
            with open(full, 'r', encoding='utf-8') as f:
                content = f.read()
            if target_module in content or os.path.basename(target_path) in content:
                return True
        except Exception:
            continue
    return False

# 主流程：查询候选文件 → 检查引用 → 无引用则删除
# 注意：删除前必须备份DB，并记录删除日志
```

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-18 深度审查**：路径全景图搬迁会重新组织所有文件位置，这些文件清理问题自然解决。无需独立修复。

### E3：422个governance根目录平铺文件重分类

**问题**：src/zephyr/governance/ 根目录有422个.py文件直接平铺，其中约30-40%属于其他域（如 order_manager→D-TRADING）。

**修复方案**：分两个子批次——

| 批次 | 内容 | 优先级 |
|------|------|--------|
| 批次A | 明确属于其他域的错放文件（如 order_manager→D-TRADING）→ 直接搬家 | 高 |
| 批次B | 归属模糊的文件 → 逐个人工裁定 | 低 |

**修复 SQL**：

```sql
-- E3: 按功能子域重新分配domain_id
-- 批次A: 明确属于其他域的错放文件
-- 示例: portfolio相关 → D-TRADING
UPDATE nodes SET domain_id = 'D-TRADING'
WHERE domain_id = 'D-GOVERNANCE'
  AND path LIKE '%portfolio%';

-- 更多映射规则需根据实际文件分布确定
-- 具体映射在施工时逐批执行
```

**时机**：标记为技术债，在 A3 容量重算后执行。

**前置依赖**：无硬依赖（A2当前无需拆分任何域，D-GOVERNANCE已未超容，可直接执行）

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-18 深度审查**：路径全景图搬迁计划包含governance目录重组。搬迁后自然解决。

### E4：同类功能文件合并

**问题**：12个rollback文件、6个escalation文件、4个compliance文件散布在governance根目录。

**修复方案**：合并会改变import路径，影响面大。放在错放文件搬家完成后，作为子包化重构单独建卡。

**时机**：标记为技术债，放在 A3 容量重算之后。优先级最低。

**建议任务卡信息**（待RooCode执行时创建）：

| 字段 | 内容 |
|------|------|
| 任务卡ID | E4-SUBPACKAGE-REFACTOR |
| 标题 | governance根目录同类功能文件子包化重构 |
| 范围 | rollback(12) + escalation(6) + compliance(4) = 22个文件 |
| 前置依赖 | E3（错放文件搬家完成） |
| 操作 | 创建 `src/zephyr/governance/rollback/`、`escalation/`、`compliance/` 子包 → 移动文件 → 更新所有import路径 → 重跑生成器 |
| 验证 | `python -c "from zephyr.governance.rollback import *"` 无 ImportError（落盘为 .py 脚本执行，禁止内联 python -c） |
| 风险 | import路径变更影响面大，需全项目Grep确认所有引用点 |

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-18 深度审查**：路径全景图搬迁会重新组织文件位置，同类功能文件合并自然解决。无需独立修复。

### E5：tags/last_verified字段空洞

**问题**：
- nodes.tags 88.8%为空数组（7,775/8,759节点），tags字段形同虚设，无法按标签筛选节点
- nodes.last_verified 部分为NULL，审计追溯能力弱

> **2026-06-18 验证**：tags空洞率=88.8%（7,775/8,759）。

**根因**：生成器不填充tags字段（无import/class/docstring自动推断逻辑）；last_verified仅在手工验证后更新，无自动填充机制。

**修复方案**：
1. 生成器从import语句/类名/docstring自动推断tags
2. 全量重建后批量设置last_verified为当前时间戳

**[与I15合并处理]**。I15 的 SQL 已覆盖 tags 回填。

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-19 复审完成（DM-100249）**：Grep搜索last_verified引用：src/zephyr/无匹配，scripts/governance/17行全是schema定义/生成器写入/迁移工具/任务卡文本。无业务消费者读取last_verified判断数据新鲜度。与I15同类：字段空洞+无消费者=可忽略。

> **2026-06-18 深度审查**：与I15合并处理。last_verified空洞意味着AI不知道数据的新鲜度，但在数据刚生成的阶段，所有数据都是新鲜的。需确认last_verified字段有无消费者。

---

## 八、Phase F：流程防护

> 与 Phase B 并行执行。防止 AI vibe coding 再次膨胀。

### F1：原型上限告警

**问题**：当前 prototype 占比需重新统计（七批次施工后8,759节点），无上限控制。

> **2026-06-18 验证**：prototype占比需重新统计（旧数据75.8%/5,750/7,590已过时）。

**修复方案**：prototype 占比 > 60% → 触发告警，暂停新文件创建。

**告警 SQL**：

```sql
-- F1: 原型占比告警查询（供监控脚本使用）
SELECT
    COUNT(*) as total_nodes,
    SUM(CASE WHEN design_maturity = 'prototype' THEN 1 ELSE 0 END) as prototype_count,
    ROUND(SUM(CASE WHEN design_maturity = 'prototype' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as prototype_pct,
    CASE
        WHEN SUM(CASE WHEN design_maturity = 'prototype' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) > 60
        THEN 'ALERT: prototype ratio exceeds 60%'
        ELSE 'OK'
    END as status
FROM nodes;
```

**集成方式**：将此查询集成到 `scripts/governance/diagnose_depgraph.py` 的告警逻辑中。

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-18 深度审查**：扩展阶段prototype占比高（66.6%）是正常的。等1500模块扩展完成后prototype占比自然下降。当前阶段不需要告警机制。

### F2：不活跃清理

**问题**：当前 inactive 节点占比需重新统计（七批次施工后8,759节点），无自动清理机制。

> **2026-06-18 验证**：inactive占比需重新统计（旧数据99.2%/7,528/7,590已过时）。

**修复方案**：标记为 inactive > 30天的文件 → 自动归档或删除审查。

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-18 深度审查**：扩展阶段"不活跃"节点可能是"还没实现的规划"。等扩展完成后再清理。当前阶段不是问题。

---

## 九、Phase G：生成器问题

> **来源**：原 `generator_issues.md`（2026-06-17 合并）。G1/G3/G4/G6 已 CLOSED/合并，G2/G5 仍 OPEN。
>
> **已关闭摘要**：G1（设计态加载源YAML→DB）、G3（[STABILITY]标记解析）、G4（[AI_AUTONOMY]标记解析）均随 P0-3 生成器升级修复。G6（contracts表来源）已合并到 I9。详见 §二。

### G2：edges表设计态依赖存储 — 已解决 ✅

> **2026-06-18 更新**：P0-1 Schema迁移已为 edges 表新增 `dep_maturity` 字段。数据库验证：8,229条边全部有 dep_maturity 值。设计态依赖关系已有存储位置。

| 状态 |
|:---:|
| CLOSED ✅ |

### G5：域名在2处独立定义，无单向同步（P2）

**问题描述**：

域名在两个地方独立定义：
1. depgraph.db `domains` 表（数据库）
2. 生成器代码中的三字典硬编码（`_DOMAIN_MAP` / `_DOMAIN_SHORT_MAP` / `_DOMAIN_GROUP_MAP`）

两处定义没有单向同步机制——改了一处另一处不变，导致域名不一致。

**影响**：

- 生成器使用的域名可能与数据库中的域名不一致
- 新增/删除域时需要同时改两处，容易遗漏

**修复方向**：

生成器从DB `domains` 表加载域名列表，验证硬编码字典中的域名是否合法。三字典改为从DB动态加载。

**关联**：

- 能力定位书§七裁定#2根因
- 裁定#2：生成器有没有必要 — 状态✅（已修复9个bug），但根因（域名双源）未解决

**文件路径**：`D:/ZephyrAlpha/scripts/governance/generate_project_depgraph.py` 域名定义相关代码

> **2026-06-19 修复完成（DM-100242）**：移除生成器中硬编码的 `domain_to_name` 字典（32条D-prefix→英文名映射），改为从DB加载的 `domains_data` 构建 `domain_id_to_group` 映射。同时补充 `DOMAIN_NAME_TO_LAYER` 缺失的4个中文键（基础设施/交易/安全/治理）。验证：生成器连续2轮exit=0，domains表61条数据不变，D-GOVERNANCE group='平台' 保留。

| 状态 |
|:---:|
| CLOSED ✅ |

---

## 十、Phase I：数据质量问题（症状级）

> **定位**：Phase I 是 Phase H 的下游症状。H修复后，I中的大部分问题将自动消失。剩余问题需独立修复。
> **优先级**：P1-P2。先修H，再评估I剩余。

### I2：非法路径格式

**描述**：路径以域ID开头（如`D-DATA/subdir/file.py`）、绝对Windows路径（如`D:/ZephyrAlpha/...`）、含emoji或特殊字符。

> **2026-06-18 验证**：当前非法路径=1,774个（主要是域ID前缀路径）。

**根因**：H3（`normalize_path`不校验）。

**影响**：路径不可用于文件系统定位、不可跨平台使用。

**证据**：`SELECT path FROM nodes WHERE path LIKE 'D-%' OR path GLOB '[A-Z]:/%'` → 非法格式

**修复方案 — 清理 SQL**：

```sql
-- I2.1: 识别所有非法路径
SELECT node_id, path FROM nodes
WHERE path LIKE 'D-%'          -- 域ID前缀
   OR path GLOB '[A-Z]:/%'     -- 绝对路径
   OR path LIKE '//%'          -- UNC/nix绝对路径
   OR path LIKE '\\\\%';       -- UNC Windows路径

-- I2.2: 修复域ID前缀路径（D-DATA/subdir/file.py → subdir/file.py）
-- [ASSUMPTION] 需要逐个确认正确路径
-- 示例修复（需根据实际数据调整）：
UPDATE nodes SET path = REPLACE(path, 'D-DATA/', 'src/zephyr/data/')
WHERE path LIKE 'D-DATA/%';
-- 其他域前缀类似处理

-- I2.3: 无法自动修复的标记为待清理
UPDATE nodes SET build_status = 'path_invalid'
WHERE path GLOB '[A-Z]:/%' OR path LIKE '//%' OR path LIKE '\\\\%';
```

**验证命令**：

```sql
-- 验证无非法路径残留
SELECT COUNT(*) FROM nodes
WHERE path LIKE 'D-%' OR path GLOB '[A-Z]:/%' OR path LIKE '//%';
-- 期望：0
```

**前置依赖**：H3（防复发）✅ CLOSED — I2 可直接执行

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-18 深度审查**：1,774个非法路径全部是设计态节点的逻辑路径（如 `D-DATA/DAT-CORE/Connector`），不是文件系统路径。运营态非法路径=0。设计态用逻辑路径标识是正常行为，用文件系统路径校验规则校验设计态路径本身就是错误的。

### I3：幽灵域引用 — 已解决 ✅

> **2026-06-18 更新**：数据库验证：0个节点引用不存在的domain_id。七批次施工已修复此问题。

| 状态 |
|:---:|
| CLOSED ✅ |

### I5：belongs_to引用不存在的node_id

**描述**：5,588个节点belongs_to引用的node_id在nodes表中不存在（如MOD-INF-005）。

> **2026-06-18 验证**：基于实际数据库验证。belongs_to断裂=5,588。**注意**：node_id已改为INTEGER类型，belongs_to为TEXT，可能存在类型不匹配问题。

**根因**：生成器在设置belongs_to时未校验目标node_id是否存在；部分引用来自已删除的历史节点。

**影响**：父子关系断裂，无法追溯模块归属。

**修复方案 — 修复 SQL**：

```sql
-- I5.1: 清除指向不存在node_id的belongs_to引用
UPDATE nodes SET belongs_to = ''
WHERE belongs_to IS NOT NULL
  AND belongs_to != ''
  AND belongs_to NOT IN (SELECT node_id FROM nodes);

-- I5.2: 从蓝图路径反推belongs_to（对module/script类型，belongs_to应指向blueprint节点）
UPDATE nodes SET belongs_to = (
    SELECT n2.node_id FROM nodes n2
    WHERE n2.type = 'blueprint'
      AND n2.blueprint_id = nodes.blueprint_id
      AND n2.blueprint_id IS NOT NULL AND n2.blueprint_id != ''
    LIMIT 1
)
WHERE (belongs_to IS NULL OR belongs_to = '' OR belongs_to NOT IN (SELECT node_id FROM nodes))
  AND blueprint_id IS NOT NULL AND blueprint_id != '';

-- I5.3: 验证
SELECT COUNT(*) FROM nodes
WHERE belongs_to IS NOT NULL AND belongs_to != ''
  AND belongs_to NOT IN (SELECT node_id FROM nodes);
-- 期望：0
```

**前置依赖**：H4（假blueprint_id清理后，belongs_to 引用更可靠）✅ CLOSED — I5 可直接执行

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-19 复审完成（DM-100245）**：原校验SQL用belongs_to匹配node_id（数字）导致5587个虚假断裂。用正确字段blueprint_id重新校验：真实断裂=0。所有belongs_to值（如MOD-INF-008）都能在blueprint_id中找到匹配。

> **2026-06-18 深度审查**：校验逻辑错误。belongs_to字段存的是**模块ID**（如 `MOD-INF-008`、`MOD-L02-001`），不是node_id（INTEGER）。校验SQL用 `belongs_to NOT IN (SELECT CAST(node_id AS TEXT) FROM nodes)` 是错的——拿模块ID去匹配数字node_id当然匹配不上。
> **正确做法**：需确认nodes表有无module_id字段。如果有，用 `belongs_to NOT IN (SELECT module_id FROM nodes)` 重新校验。如果没有module_id字段，belongs_to引用的是蓝图模块编号，需和蓝图注册表匹配。
> **实际数据**：production断裂529个、prototype断裂5,059个、设计态0个断裂。5,588个"断裂"可能是校验逻辑错误造成的虚假问题。

### I7：arch_directory_tree domain_id为空 — 已解决 ✅

> **2026-06-18 更新**：数据库验证：arch_directory_tree 中 domain_id 为空的行数=0。P0-5 施工已修复此问题。

| 状态 |
|:---:|
| CLOSED ✅ |

### I8：arch_directory_tree 100% build_status=unbuilt但实际已建成

**描述**：arch_directory_tree所有行的build_status均为'unbuilt'，但实际路径以 src/zephyr/ 开头的目录已建成——逻辑矛盾。

> **2026-06-17 更新**：原方案使用 `state` 字段，但 V3.4 施工将删除 `state` 字段（替换为 node_id 外键）。改为使用 `build_status` + `design_maturity` 双字段判定。

**根因**：生成器写入时 build_status 使用默认值 'unbuilt'，未根据路径实际状态做一致性校验。

**影响**：无法区分"规划中"和"已建成"的目录，目录树状态不可信。

**修复方案 — 修复 SQL**（不使用 state 字段）：

```sql
-- I8: 修复 build_status 矛盾（V3.4 兼容，不使用 state 字段）
-- 方案：若目录路径以 src/zephyr/ 开头（代码目录），认为已构建
UPDATE arch_directory_tree
SET build_status = 'built'
WHERE build_status = 'unbuilt'
  AND path LIKE 'src/zephyr/%';

-- 其他保持 unbuilt（规划中目录）
```

**验证命令**：

```sql
SELECT build_status, COUNT(*) FROM arch_directory_tree GROUP BY build_status;
-- 期望：src/zephyr/ 下的目录为 built，其余为 unbuilt
```

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-19 复审完成（DM-100246）**：Grep搜索build_status引用：src/zephyr/仅depgraph_schema.py（schema定义），scripts/19个文件全是生成器/迁移工具/任务卡创建。无业务消费者读取build_status做决策。生成器默认填draft对系统运行无影响。

> **2026-06-18 深度审查**：需确认build_status字段有无消费者。production 804个全标draft、prototype 5,833个全标draft——生成器扫描代码时默认填draft。但如果AI不依赖build_status字段做决策，标draft影响不大。arch_directory_tree中设计态8,507个标unbuilt是正常的（还没建成）。
> **正确做法**：确认build_status字段有无消费者。如果没有消费者，这不是问题。如果有消费者，需修复生成器默认值逻辑。

### I9：contracts consumer_domain缺乏域多样性

**描述**：contracts表大部分记录consumer_domain='D-SHARED'，域多样性不足。

> **2026-06-18 验证**：当前42条记录consumer_domain≠D-SHARED（已有部分改善），但大部分仍为D-SHARED。

**G6 补充**：生成器不写入 `contracts` 表。当前contracts表的数据来源不明——可能是历史脚本写入的，也可能是手动插入的。需要先查contracts表数据来源，再决定：
- 如果是设计态文档生成的 → 保留，生成器不碰
- 如果是生成器自动生成的 → 和edges去重

**关联**：
- 裁定#15：contracts表来源确认 — 状态❌（未裁定）
- 裁定#20：contracts来源调查 — 待RooCode执行时先查

**修复方案 — 修复 SQL**：

```sql
-- I9: 从edges表推导实际consumer_domain
-- 策略：contracts表记录provider→consumer关系
-- 如果所有consumer_domain都是D-SHARED，说明生成器未正确推导

-- I9.1: 识别当前的共享契约分布
SELECT provider_domain, consumer_domain, COUNT(*) FROM contracts
GROUP BY provider_domain, consumer_domain;

-- I9.2: 从边缘推导消费者域
-- 找到edges中from_node_id所在域 ≠ to_node_id所在域的跨域边
-- 更新contracts的consumer_domain为实际消费者域
UPDATE contracts SET consumer_domain = (
    SELECT n_to.domain_id FROM edges e
    JOIN nodes n_from ON e.from_node_id = n_from.node_id
    JOIN nodes n_to ON e.to_node_id = n_to.node_id
    WHERE n_from.domain_id = contracts.provider_domain
      AND n_from.domain_id != n_to.domain_id
      AND n_to.domain_id IS NOT NULL AND n_to.domain_id != ''
    GROUP BY n_to.domain_id
    ORDER BY COUNT(*) DESC
    LIMIT 1
)
WHERE consumer_domain = 'D-SHARED'
  AND EXISTS (
    SELECT 1 FROM edges e
    JOIN nodes n_from ON e.from_node_id = n_from.node_id
    WHERE n_from.domain_id = contracts.provider_domain
  );

-- I9.3: 无法推导的保持D-SHARED（表示真实的共享契约）
```

**验证命令**：

```sql
SELECT consumer_domain, COUNT(*) FROM contracts GROUP BY consumer_domain;
-- 期望：D-SHARED不再是唯一值
```

**前置依赖**：H5（cross_domain 边信息正确）✅ CLOSED — I9 可直接执行

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-18 深度审查**：contracts表样本显示 version='design'、fulfillment_status='unresolved'、actual_consumer=None——这些是设计态契约（规划中的接口契约，还没实现）。consumer_domain=D-SHARED是因为它们是跨域共享的通用契约。契约实际实现后 actual_consumer 字段会被填充。当前阶段不是问题。

### I13：孤儿节点（非设计态）

**描述**：非设计态节点中无任何边连接的孤儿节点。

> **2026-06-18 验证**：当前585个非设计态孤儿节点（8,759节点中，占比6.7%）。较七批次施工前（1,471/19.4%）显著改善，接近5%目标。

**根因**：
- 孤儿节点中大部分为design态——设计态节点天然无运行时依赖
- 非设计态孤儿585个（6.7%）——需运行 import 分析补边
- 生成器的import解析覆盖不全（只解析`from zephyr.X`不解析`from .X`相对导入）

**影响**：6.7%节点在依赖分析中不可见，影响分析、循环检测、架构审计均遗漏这些节点。

**修复方案**：

1. **design 态孤儿**：保留（设计态节点天然无运行时依赖）
2. **prototype/production 态孤儿**：运行 import 分析补边

**修复 SQL/代码**：

```sql
-- I13.1: 统计孤儿节点分布
SELECT n.design_maturity, n.node_type, COUNT(*) as orphan_count
FROM nodes n
WHERE n.node_id NOT IN (SELECT from_node_id FROM edges)
  AND n.node_id NOT IN (SELECT to_node_id FROM edges)
GROUP BY n.design_maturity, n.node_type
ORDER BY orphan_count DESC;

-- I13.2: 标记design态孤儿为设计待实现
UPDATE nodes SET build_status = 'design_only'
WHERE node_id NOT IN (SELECT from_node_id FROM edges)
  AND node_id NOT IN (SELECT to_node_id FROM edges)
  AND design_maturity = 'design';

-- I13.3: 对prototype/production孤儿，运行import分析补边
-- 此步骤需生成器修复或使用应用层Python代码
```

**应用层import分析补边实现要点**（待RooCode执行时编写）：

```python
# 脚本位置建议：D:/ZephyrAlpha/scripts/governance/repair/fix_orphan_imports.py
# 策略：对prototype/production态孤儿节点，解析其import语句，补全缺失的边
import ast, sqlite3, os

DB = 'data/databases/depgraph.db'
PROJECT_ROOT = 'D:/ZephyrAlpha'

def parse_imports(file_path):
    """解析Python文件的import语句，返回被引用的模块路径列表"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
        return imports
    except Exception:
        return []

conn = sqlite3.connect(DB)
cur = conn.cursor()
# 查询prototype/production态孤儿节点
cur.execute("""
    SELECT node_id, path FROM nodes
    WHERE design_maturity IN ('prototype', 'production')
      AND node_id NOT IN (SELECT from_node_id FROM edges)
      AND node_id NOT IN (SELECT to_node_id FROM edges)
      AND path IS NOT NULL AND path != ''
""")
orphans = cur.fetchall()

# 解析每个孤儿节点的import，补全边
for from_node_id, path in orphans:
    full_path = os.path.join(PROJECT_ROOT, path.replace('/', os.sep))
    if not os.path.exists(full_path):
        continue
    imports = parse_imports(full_path)
    for imp in imports:
        # 查找被import的模块对应的node_id
        cur.execute("SELECT node_id FROM nodes WHERE path LIKE ?", (f'%{imp.replace(".", "/")}%',))
        target = cur.fetchone()
        if target:
            # 插入边（避免重复）
            cur.execute("""
                INSERT OR IGNORE INTO edges (from_node_id, to_node_id, dep_type, cross_domain, verified)
                VALUES (?, ?, 'import_depends', 0, 0)
            """, (from_node_id, target[0]))
conn.commit()
print(f"处理 {len(orphans)} 个孤儿节点的import补边")
conn.close()
```

**验证 SQL**：

```sql
-- 孤儿率统计（排除design态）
SELECT
    COUNT(*) as total_orphans,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM nodes), 1) as orphan_pct
FROM nodes n
WHERE n.node_id NOT IN (SELECT from_node_id FROM edges)
  AND n.node_id NOT IN (SELECT to_node_id FROM edges)
  AND n.design_maturity != 'design';
-- 目标：< 5%（当前6.7%）
```

**前置依赖**：H1（重复节点清理后）✅ CLOSED，H5（边字段正确后）✅ CLOSED，I5（belongs_to校验逻辑待重新校验）🔍 RECHECK

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-19 复审完成（DM-100247）**：过滤node_type=module AND design_maturity=production后，真实代码孤儿=0。2776个孤儿中975个是module但全部为design/prototype态，无production代码孤儿。原报告157个production孤儿全是config/registry/yaml等非代码文件。

> **2026-06-18 深度审查**：需过滤出代码文件。production孤儿157个，样本全是config/registry/yaml文件（如 `config/capacity/*.yaml`、`docs/03_modules/template_registry.yaml`）。配置文件和注册表文件没有代码import依赖是正常的——它们被运行时读取，不被其他代码import。
> **正确做法**：过滤出 `node_type='module'` 的production孤儿才是真问题。设计态孤儿2,068个是正常的（还没实现，当然没依赖边）。

### I14：design态节点路径在文件系统中不存在

**描述**：设计态节点中，部分节点的path在文件系统中不存在——这些是"纸上设计"，从未落地为代码。

> **2026-06-17 更新**：基于实际数据库验证。旧数据为"1,645个design态节点中1,121个(68.1%)路径不存在"，实际design态节点=1,069（52域快照）。**注意**：七批次施工后设计态节点已增至2,109（61域），路径不存在的具体数量需应用层脚本重新验证。

**此外**：
- 14个production态节点路径不存在（`docs/02_enterprise_architecture/target_architecture/`子目录）
- 66个prototype态节点路径不存在（`src/zephyr/ops/gates/safety_gate_l*.py`等）

**根因**：
- design态：蓝图定义了模块但代码未创建（正常情况的一部分）
- production/prototype：文件已被删除或移动，但DB未更新

**影响**：DB路径与文件系统严重脱节，路径不可信。

**修复方案 — 修复 SQL**：

```sql
-- I14.1: 标记设计态路径不存在的节点
-- 由于SQL无法检查文件系统，使用应用层脚本

-- I14.2: 在应用层标记后
UPDATE nodes SET build_status = 'design_only'
WHERE design_maturity = 'design' AND build_status = 'unbuilt';

-- I14.3: 对于production/prototype态但路径不存在的节点，标记为orphan
-- (需应用层文件系统检查后执行)
```

**应用层脚本实现要点**（待RooCode执行时编写）：

```python
# 脚本位置建议：D:/ZephyrAlpha/scripts/governance/repair/check_design_paths.py
import sqlite3, os
DB = 'data/databases/depgraph.db'
PROJECT_ROOT = 'D:/ZephyrAlpha'

conn = sqlite3.connect(DB)
cur = conn.cursor()
# 查询所有design/production/prototype态节点的path
cur.execute("""
    SELECT node_id, path, design_maturity FROM nodes
    WHERE design_maturity IN ('design', 'production', 'prototype')
      AND path IS NOT NULL AND path != ''
""")
invalid_nodes = []
for node_id, path, maturity in cur.fetchall():
    full_path = os.path.join(PROJECT_ROOT, path.replace('/', os.sep))
    if not os.path.exists(full_path):
        invalid_nodes.append((node_id, path, maturity))

# 批量更新build_status
cur.executemany(
    "UPDATE nodes SET build_status = 'design_only' WHERE node_id = ? AND design_maturity = 'design'",
    [(n[0],) for n in invalid_nodes if n[2] == 'design']
)
cur.executemany(
    "UPDATE nodes SET build_status = 'orphan' WHERE node_id = ? AND design_maturity IN ('production', 'prototype')",
    [(n[0],) for n in invalid_nodes if n[2] in ('production', 'prototype')]
)
conn.commit()
print(f"标记 {len(invalid_nodes)} 个路径不存在的节点")
conn.close()
```

**前置依赖**：H2（空路径清理）✅ CLOSED — I14 可直接执行

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-18 深度审查**：设计态路径本就不该存在于文件系统。能力定位书§12.1明确说"文件还不存在，但规划了将来放在这个目录下"。这是设计态的核心特征，不是问题。

### I15：nodes.tags 87%为空数组

**描述**：7,775/8,759节点tags为空数组（88.8%），tags字段形同虚设。

> **2026-06-18 验证**：基于实际数据库验证。tags空洞率=88.8%（7,775/8,759）。

**根因**：生成器不填充tags；tags字段在v3 schema中定义但从未被写入（此条目跟踪症状侧，修复见E5）。

**影响**：无法按标签筛选节点，标签驱动的架构分析不可用。

**修复方案 — 修复 SQL**：

```sql
-- I15: 从node_type和domain_id自动生成tags
UPDATE nodes SET tags = json_array(
    node_type,
    CASE
        WHEN architecture_layer = 'L0_infrastructure' THEN 'infrastructure'
        WHEN architecture_layer = 'L1_foundation' THEN 'foundation'
        WHEN architecture_layer = 'L2_domain' THEN 'domain'
        WHEN architecture_layer = 'L3_application' THEN 'application'
        ELSE 'unclassified'
    END,
    COALESCE(domain_id, 'no-domain')
)
WHERE (tags IS NULL OR tags = '' OR tags = '[]')
  AND node_type IS NOT NULL;
```

**验证 SQL**：

```sql
SELECT COUNT(*) FROM nodes WHERE tags IS NULL OR tags = '' OR tags = '[]';
-- 期望：显著减少
```

**前置依赖**：A1（层标签归一化）✅ CLOSED — I15 可直接执行

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-19 复审完成（DM-100248）**：Grep搜索nodes表tags字段引用：无任何代码引用nodes.tags做查询。所有tags引用都是其他表（tasks/metrics/knowledge/strategy）的tags字段。nodes.tags 88.8%为空不影响系统运行——无消费者。

> **2026-06-18 深度审查**：需确认tags字段有无消费者。tags空洞率88.8%（7,775/8,759）。设计态tags空洞1,138个可接受（规划中的模块还没打标签）。运营态tags空洞6,637个需要关注——但如果AI不需要按tags筛选节点，这个字段空着影响不大。
> **正确做法**：确认tags字段有无消费者。如果没有消费者，这不是问题。如果有消费者（如按标签筛选模块），需回填tags。

### I17：超容域（8个）— 已有A2覆盖

**描述**：当前8个域节点数超过max_modules。其中 D-TEST 严重超容（26.3x），其余7个轻微超容（1.0x-1.2x）。D-TEST 因内部依赖极少已豁免80模块限制。详见Phase A2和"十二、超容域拆分"章节。**已有覆盖，不重复录入。**

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-18 深度审查**：已有A2覆盖，A2已CLOSED。

### I18：5个域 max_modules > 80 — 已有A2覆盖

**描述**：部分域的max_modules超过80的硬上限（如 D-GOVERNANCE max=750, D-GOV-DOCS max=210, D-SHARED max=210 等），这些是已裁定的容量调整。详见Phase A2。**已有覆盖，不重复录入。**

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-18 深度审查**：已有A2覆盖，A2已CLOSED。

---

## 十一、Phase K：待定决策遗漏

> **定位**：已识别的待定决策（T6/T7/T17）未被纳入问题跟踪体系，可能被遗忘。
> **优先级**：P2。

### K1：3项待定决策无对应问题卡

**描述**：以下3项待定决策在架构升级讨论（`architecture_upgrade_discussion.md` §16）中标记为"待定"，但未创建对应的问题卡或任务卡，存在被遗忘风险：

| 编号 | 待定决策 | 说明 |
|:---:|------|------|
| T6 | 事件类型体系 | 事件分类标准未确定 |
| T7 | 三级配置结构 | 全局/域级/模块级配置规范未定义 |
| T17 | 模块级DOMAIN字段声明 | 模块如何声明自己的域归属 |

> **2026-06-18 更新**：原8项清单中，T2（market.duckdb DDL）和T5（45能力→域映射）已在阶段1解决；T8（场外文件提取）和T9（场外文件优先级）已在§17.4裁定；T11（35平铺域清单）已由D44裁定删除。剩余3项仍待定。

**根因**：待定决策在架构升级讨论中仅标注"待定"，未纳入depgraph_issue_registry.md的问题跟踪体系。

**影响**：决策延期无限积累，全景图能力边界持续模糊。

**修复方案**：每个T项创建独立问题卡，设定裁定截止日期（建议30天内）。

| 编号 | 待定决策 | 建议问题卡ID | 建议截止日期 |
|:---:|------|------|:---:|
| T6 | 事件类型体系 | K-T6 | +30天 |
| T7 | 三级配置结构 | K-T7 | +30天 |
| T17 | 模块级DOMAIN字段声明 | K-T17 | +30天 |

| 状态 |
|:---:|
| CLOSED ✅ |

> **2026-06-19 更新**：3项待定决策已整理为决策文档 `architecture_decisions_pending.md`，每项含3个候选方案及推荐选项：
> - T6 事件类型体系 → 推荐 Option C（Registry + Enum 混合方案）
> - T7 三级配置结构 → 推荐 Option C（Hybrid 混合方案）
> - T17 模块级DOMAIN字段 → 推荐 Option B（可选声明方案）
>
> 决策文档已交付，待 Owner 审批后落地。任务卡 DM-100244 已完成。

---

## 十二、超容域拆分

> **2026-06-17 更新**：基于当时52域实际数据重新统计。**注意**：七批次施工（P0-1~P0-7）完成后数据已变更为 61域/8746节点。以下超容域数据基于52域快照，需在数据治理阶段重新验证。
>
> **豁免裁定**：D-TEST 因内部依赖极少（测试文件单向引用被测模块，几乎无测试间依赖）豁免80模块限制；D-GOV-DOCS 因零内部依赖（154文档无相互引用）豁免80模块限制。

### 当前超容域清单（8个）

| 域 | max | actual | 倍数 | 优先级 | 备注 |
|------|:---:|:---:|:---:|:---:|------|
| D-TEST | 80 | 2105 | 26.3x | P0 | ⚠️ 已豁免（内部依赖极少） |
| D-SHARED | 210 | 249 | 1.2x | P2 | 轻微超容 |
| D-OPS | 380 | 443 | 1.2x | P2 | 轻微超容 |
| D-INTEGRATION | 220 | 254 | 1.2x | P2 | 轻微超容 |
| D-TRADING | 140 | 156 | 1.1x | P3 | 轻微超容 |
| D-AUTONOMY_CORE | 180 | 195 | 1.1x | P3 | 轻微超容 |
| D-MKT_DATA | 80 | 82 | 1.0x | P3 | 临界超容 |
| D-INFRA_RUNTIME | 480 | 481 | 1.0x | P3 | 临界超容 |

### 拆分方案

#### D-TEST（2105节点，已豁免）

> **裁定**：D-TEST 因内部依赖极少豁免80模块限制，**不拆分**。测试文件单向引用被测模块，几乎无测试间依赖，拆分反而增加管理成本。
>
> 若未来测试间依赖增长，可按被测域分组拆分为：D-TEST-GOVERNANCE(~600) / D-TEST-INFRA(~600) / D-TEST-SECURITY(~300) / D-TEST-INTELLIGENCE(~300) / D-TEST-SHARED(~305)。当前无需执行。

#### 轻微超容域（7个，1.0x-1.2x）

> **策略**：轻微超容（≤1.2x）的域通过调整 max_modules 或清理无效节点解决，**不拆分**。
>
> - D-SHARED/D-OPS/D-INTEGRATION/D-TRADING/D-AUTONOMY_CORE：清理无效节点后重新评估，或微调 max_modules
> - D-MKT_DATA/D-INFRA_RUNTIME：临界超容（1.0x），清理1-2个无效节点即可解决

### 拆分后域数预估

| Phase | 操作 | 新增域 | 累计域数 |
|:---:|------|:---:|:---:|
| 当前 | — | — | 61 |
| 未来（若D-TEST拆分） | D-TEST→5子域 | +4 | 65 |

> **注**：当前无需拆分任何域。原方案的 D-GOVERNANCE→4子域、D-INFRA_RUNTIME→3子域、D-SECURITY→2子域 均已通过调整 max_modules 解决，不再需要。

---

## 十三、执行顺序与因果链

> **来源**：原 `depgraph_fix_plans.md` §执行顺序与因果链（2026-06-17 合并）。
> **原则**：生成器bug先修 → 重跑生成器 → 数据清理 → 架构优化 → 容量治理 → 性能优化 → 流程防护

### 13.1 依赖矩阵

#### Phase H：生成器Bug（9个）— 已全部 CLOSED

| 修复ID | 前置依赖 | 后置解锁 | 可并行 | 说明 |
|--------|---------|---------|--------|------|
| **H1** | 无 | I13（去重后孤儿分析更准） | H2,H3,H4,H5,H7,H8,H9 | `_build_scan_dirs()` 去重 |
| **H2** | 无 | I14（空路径清理后设计态路径检查更准） | H1,H3,H4,H5,H7,H8,H9 | 跳过空路径设计态节点 |
| **H3** | 无 | I2（防复发：非法路径不再入库） | H1,H2,H4,H5,H7,H8,H9 | `normalize_path()` 合法性校验 |
| **H4** | 无 | I5（假blueprint_id清理后belongs_to推导更可靠） | H1,H2,H3,H5,H7,H8,H9 | 假`D-XXX-blueprint`ID过滤 |
| **H5** | 无 | A4, I9, I10, I11, I13（边字段正确填充） | H1,H2,H3,H4,H7,H8,H9 | 边`cross_domain`/`verified`/`invocation_method`填充 |
| **H6** | nodes表需有4个v3列† | 无（填充v3新字段） | H1,H2,H3,H4,H5,H7,H8,H9 | INSERT扩展`can_build`/`gate_reason`/`hard_boundary_ref`/`consumed_interfaces` |
| **H7** | 无 | A3（自动解决）, A2（current_modules数据可用） | H1,H2,H3,H4,H5,H6,H8,H9 | `current_modules`聚合写入 |
| **H8** | 无 | arch_constraints表填充 | H1,H2,H3,H4,H5,H6,H7,H9 | `architecture_model/`约束加载 |
| **H9** | 无 | 5个新目录的文件入库 | H1,H2,H3,H4,H5,H6,H7,H8 | SCAN_DIRS扩展 |

> † H6的前置条件：`depgraph_schema.py` DDL已定义这4列，`init_db()` 自动创建。若旧DB无这些列 → 需先 `ALTER TABLE nodes ADD COLUMN`。

#### Phase A：数据治理（4个）— 3个CLOSED，1个RECHECK

| 修复ID | 前置依赖 | 后置解锁 | 可并行 | 说明 |
|--------|---------|---------|--------|------|
| **A1** | （历史：H1-H9 + 重跑生成器，已完成） | — | — | ✅ CLOSED：4标准层覆盖100%节点 |
| **A2** | — | — | — | ✅ CLOSED：D-TEST已豁免，其余轻微超容通过max_modules调整解决 |
| **A3** | — | — | — | ✅ CLOSED：H7修复后自动解决 |
| **A4** | — | — | — | 🔍 RECHECK：需过滤出跨域循环。dep_cycles视图8行大部分是同域内循环（Python包结构正常现象），需确认有无跨域循环 |

#### Phase I：数据质量（18个）— 13个CLOSED，5个RECHECK

| 修复ID | 前置依赖 | 后置解锁 | 可并行 | 说明 |
|--------|---------|---------|--------|------|
| **I2** | — | — | — | ✅ CLOSED：1,774个全部是设计态逻辑路径，运营态=0。设计态用逻辑路径标识是正常行为 |
| **I3** | — | — | — | ✅ CLOSED：0幽灵域引用（数据库验证） |
| **I5** | — | — | — | 🔍 RECHECK：校验逻辑错误。belongs_to存模块ID（MOD-INF-008）非node_id（INTEGER），需用正确字段重新校验 |
| **I7** | — | — | — | ✅ CLOSED：0空domain_id（P0-5修复） |
| **I8** | — | — | — | 🔍 RECHECK：需确认build_status字段有无消费者。生成器默认填draft，若无消费者则不影响 |
| **I9** | — | — | — | ✅ CLOSED：设计态契约（version='design'），consumer_domain=D-SHARED是跨域共享通用契约的正常表现 |
| **I10** | — | — | — | ✅ CLOSED：H5修复后自动解决 |
| **I11** | — | — | — | ✅ CLOSED（部分）：H5修复后invocation_method已填充 |
| **I13** | — | — | — | 🔍 RECHECK：需过滤出node_type='module'的production孤儿。当前157个production孤儿大部分是config/registry文件，无依赖边正常 |
| **I14** | — | — | — | ✅ CLOSED：设计态路径本就不该存在于文件系统（能力定位书§12.1） |
| **I15** | — | — | — | 🔍 RECHECK：需确认tags字段有无消费者。88.8%为空，但若AI不需要按tags筛选则不影响 |
| **I17** | — | — | — | ✅ CLOSED：A2覆盖，A2已CLOSED |
| **I18** | — | — | — | ✅ CLOSED：A2覆盖，A2已CLOSED |

#### Phase J：Schema偏差（4个）— 已全部 CLOSED ✅

> 以下 J1-J4 已在 2026-06-16 全部修复并验证通过，不再出现在执行计划中。

| 修复ID | 前置依赖 | 后置解锁 | 可并行 | 说明 |
|--------|---------|---------|--------|------|
| **J1** | 无 | — | J2,J3,J4 | arch_directory_tree加design_maturity列 |
| **J2** | 无 | — | J1,J3,J4 | domain_events加event_type列 |
| **J3** | 无 | — | J1,J2,J4 | rule_bindings加domain_id列 |
| **J4** | 无 | — | J1,J2,J3 | domain_dependencies文档一致性验证 |

#### Phase B/C/E/F/G/K（5个待修复 + 2个RECHECK + 8个CLOSED）

| 修复ID | 前置依赖 | 后置解锁 | 可并行 | 说明 |
|--------|---------|---------|--------|------|
| **B1** | — | — | — | ✅ CLOSED：66.6% prototype标evolving是扩展阶段正常状态 |
| **B2** | — | — | — | **待修复（P1）**：安全敏感文件（认证/加密/回滚）应标human_gated |
| **B3** | — | — | — | ✅ CLOSED：路径全景图搬迁后自动解决 |
| **C1** | — | — | — | 🔍 RECHECK：需确认查询频率。coupling_strength仅7个不同值，索引效果有限 |
| **C2** | — | — | — | ✅ CLOSED：搬迁计划包含测试目录重组 |
| **C3** | — | — | — | **待修复（P2）**：门禁增量扫描，扩展到1500模块后全量扫描会越来越慢 |
| **E1** | — | — | — | **待修复（P2）**：arch_layers 10条旧层名清理，4标准层已覆盖100% |
| **E2** | — | — | — | ✅ CLOSED：搬迁后自然解决 |
| **E3** | — | — | — | ✅ CLOSED：搬迁后自然解决 |
| **E4** | — | — | — | ✅ CLOSED：搬迁后自然解决 |
| **E5** | — | — | — | 🔍 RECHECK：与I15合并处理，需确认有无消费者 |
| **F1** | — | — | — | ✅ CLOSED：扩展阶段prototype占比高是正常的 |
| **F2** | — | — | — | ✅ CLOSED：扩展阶段不活跃节点是"还没实现的规划" |
| **G5** | — | — | — | ✅ CLOSED（2026-06-19 DM-100242）：移除硬编码域名字典，改为DB读取 |
| **K1** | — | — | — | **待修复（P3）**：3项待定决策（T6/T7/T17），需人类拍板 |

### 13.2 因果链图

> **2026-06-18 深度审查后更新**：大量问题经设计态/运营态区分审查后CLOSED。因果链大幅简化。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TIER 0-2: 已完成 ✅                                    │
│                                                                             │
│  TIER 0: Pre-Flight（J1-J4 Schema偏差）✅ CLOSED                            │
│  TIER 1: 生成器Bug修复（H1-H9）✅ CLOSED                                    │
│  TIER 2: 重跑生成器（七批次施工 P0-1~P0-7）✅ 已完成                          │
│  自动解决: A1/A2/A3/I1/I2/I3/I4/I6/I7/I9/I10/I11/I12/I14/I16/I17/I18        │
│  深度审查CLOSED: B1/B3/C2/E2/E3/E4/F1/F2（搬迁后解决/扩展阶段正常）            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                TIER 3: 需重新校验（RECHECK 🔍）                                │
│                                                                             │
│  以下问题需重新校验后才能定性是否需要修复：                                       │
│  I5:  belongs_to校验逻辑错误（存模块ID非node_id），需用正确字段重新校验         │
│  I8:  build_status全draft，需确认字段有无消费者                                │
│  I13: 孤儿节点需过滤出node_type='module'的production代码文件                   │
│  I15: tags空洞88.8%，需确认字段有无消费者                                      │
│  E5:  与I15合并处理                                                           │
│  A4:  循环依赖需过滤出跨域循环（排除同域内Python包结构正常循环）                 │
│  C1:  3个索引需确认查询频率（coupling_strength仅7个不同值，索引效果有限）        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                TIER 4: 真正需修复（4项，G5已CLOSED）                           │
│                                                                             │
│  ✅ G5: 已修复（DM-100242）— 移除硬编码域名字典，改为DB读取                    │
│  B2:  安全敏感文件标记（P1）— 认证/加密/回滚文件应标human_gated                 │
│  E1:  arch_layers旧记录清理（P2）— 10条旧层名，4标准层已覆盖100%               │
│  C3:  门禁增量扫描（P2）— 扩展到1500模块后全量扫描会越来越慢                    │
│  K1:  3项待定决策（P3）— T6/T7/T17需人类拍板                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                TIER 5: 未来扩展（1500模块完成后）                               │
│                                                                             │
│  D1: 蓝图缩放（按域加载蓝图，节省token）                                       │
│  D2: 知识库查询（语义搜索已有知识）                                            │
│  D3: 冷启动优化（只加载必要信息）                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 13.3 关键依赖链（纵向追踪）

> **2026-06-18 深度审查后更新**：大部分链已CLOSED，仅保留RECHECK和待修复链。

```
链1（路径质量）✅ 已完成:
  H3(normalize_path校验) → 重跑生成器 → I2(设计态逻辑路径，非问题) ✅ CLOSED
  H2(空路径跳过)         → 重跑生成器 → I14(设计态路径不存在，非问题) ✅ CLOSED

链2（边质量 → 循环分析）🔍 RECHECK:
  H5(cross_domain/verified/invocation_method) ✅ 已完成 → A4(需过滤跨域循环) 🔍 RECHECK
  I9(设计态契约D-SHARED正常) ✅ CLOSED

链3（ID质量 → belongs_to → 孤儿分析）🔍 RECHECK:
  H4(假blueprint_id过滤) ✅ 已完成 → I5(校验逻辑错误：belongs_to存模块ID非node_id) 🔍 RECHECK
  I13(需过滤出module类型production孤儿) 🔍 RECHECK

链4（容量治理）✅ 已完成:
  H7(current_modules计算) → 重跑生成器 → A3(自动解决) ✅ CLOSED
  A2(D-TEST已豁免，轻微超容通过max_modules调整) ✅ CLOSED

链5（标签体系）🔍 RECHECK:
  A1(层标签归一化) ✅ CLOSED → I15(需确认tags有无消费者) 🔍 RECHECK → E5(合并) 🔍 RECHECK

链6（域拆分 → 重分类）✅ 已完成:
  B3(搬迁后自动解决) ✅ CLOSED
  E3/E4(搬迁后自然解决) ✅ CLOSED
  C2(搬迁计划包含测试目录重组) ✅ CLOSED

链7（安全标记）待修复:
  B1(扩展阶段evolving正常) ✅ CLOSED
  B2(安全敏感文件应标human_gated) 待修复 P1

链8（SSoT）已修复:
  G5(域名双源：生成器硬编码 vs DB) ✅ CLOSED（DM-100242）

链9（数据清理）待修复:
  E1(arch_layers 10条旧层名) 待修复 P2

链10（性能优化）待修复:
  C3(门禁增量扫描) 待修复 P2

链11（待定决策）待修复:
  K1(T6/T7/T17需人类拍板) 待修复 P3
```

### 13.4 Pre-Flight：生成器修复前必须确认的Schema条件（✅ 已完成）

H6修复需要 `nodes` 表存在以下4列（由 `depgraph_schema.py:init_db()` 创建）。**此步骤已在 P0-1 Schema 迁移中完成。**

| 列名 | 类型 | 默认值 |
|------|------|--------|
| `can_build` | INTEGER | 1 |
| `gate_reason` | TEXT | '' |
| `hard_boundary_ref` | TEXT | '' |
| `consumed_interfaces` | TEXT | '' |

**检查命令**：
```sql
SELECT name FROM pragma_table_info('nodes')
WHERE name IN ('can_build', 'gate_reason', 'hard_boundary_ref', 'consumed_interfaces');
-- 期望：4 rows
```

**若缺失**（旧DB未运行过最新 `init_db()`）：
```sql
ALTER TABLE nodes ADD COLUMN can_build INTEGER DEFAULT 1;
ALTER TABLE nodes ADD COLUMN gate_reason TEXT DEFAULT '';
ALTER TABLE nodes ADD COLUMN hard_boundary_ref TEXT DEFAULT '';
ALTER TABLE nodes ADD COLUMN consumed_interfaces TEXT DEFAULT '';
```

### 13.5 执行顺序总表

> **2026-06-18 深度审查后更新**：大量问题CLOSED后，执行顺序大幅简化。

| 顺序 | 阶段 | 修复ID | 前置依赖 | 可并行组 | 文件/目标 | 类型 |
|:----:|------|--------|---------|---------|-----------|------|
| 0-2 | 已完成 | P0/H/J + 重跑生成器 | 无 | ✅ CLOSED | `depgraph.db` | 代码/命令 |
| 3 | 需重新校验 | I5,I8,I13,I15,E5,A4,C1 | 无 | 7项独立校验 | `depgraph.db` | 校验SQL |
| 4 | 真正需修复 | B2,E1,C3,K1（G5已CLOSED） | 无 | 4项独立 | 多目标 | 混合 |
| 5 | 未来扩展 | D1,D2,D3 | 1500模块完成 | 3项独立 | 多目标 | 混合 |

### 13.6 并行组定义

> **2026-06-18 深度审查后更新**：原Parallel Group 3a/3b/4/5大部分已CLOSED。

#### Parallel Group 0-2: 已完成 ✅
- P0/H/J全部CLOSED，生成器重跑已完成

#### Parallel Group 3: 需重新校验（7项独立校验）
- I5（重新校验belongs_to匹配逻辑）、I8（确认build_status消费者）、I13（过滤module类型production孤儿）
- I15/E5（确认tags消费者）、A4（过滤跨域循环）、C1（确认查询频率）
- 执行方式：各自独立校验，校验后定性是否需要修复

#### Parallel Group 4: 真正需修复（4项独立，G5已CLOSED）
- ✅ G5（域名双源SSoT，P1）— 已修复（DM-100242）
- B2（安全敏感文件标记，P1）
- E1（arch_layers旧记录清理，P2）、C3（门禁增量扫描，P2）
- K1（3项待定决策，P3，需人类拍板）
- 执行方式：各自独立执行，无互相依赖

#### Parallel Group 5: 未来扩展（3项独立）
- D1（蓝图缩放）、D2（知识库查询）、D3（冷启动优化）
- 执行时机：1500模块扩展完成后

### 13.7 风险与注意事项

1. **H6前置条件风险**：若 `depgraph.db` 是旧版本（`depgraph_schema.py` 更新前的DDL），nodes表可能缺少4个v3列。Pre-Flight步骤必须100%通过后才能进入H1-H9修复。

2. **生成器重跑是原子操作**：H1-H9全部修复后必须一次重跑。部分修复就重跑会导致数据不一致（如H5修复了边字段但H4未修复假ID，边引用的节点ID可能无效）。

3. **A1已CLOSED（历史说明）**：A1原属Phase A，修复方案在 `generate_project_depgraph.py` 的 `write_depgraph_to_db()` 中（Tier 4 WHERE条件）。实际执行时H1-H9批改已包含A1的代码修改，现已CLOSED无需独立操作。

4. **A3/I10/I11自动解决的前提**：生成器重跑成功且H5/H7修复正确。若生成器中途崩溃，这些"自动解决"不会生效。

5. **I13取决于H1+H5+I5的三重依赖**：I13（孤儿标记）是依赖链最深的修复——必须等H1（去重）、H5（边正确）、I5（belongs_to正确）全部完成后才有准确结果。过早执行会产生误标记。

6. **SQLite单写锁限制**：虽然逻辑上多个SQL修复可并行，但SQLite同一时间只允许一个写连接。所有SQL修复应合并为一个脚本顺序执行，或使用WAL模式。

### 13.8 建议的施工批次

```
批次 0 (Pre-Flight):  J1+J2+J3+J4 + nodes表v3列检查     [✅ 已完成 2026-06-16]
批次 1 (Generator):   H1→H2→H3→H4→H5→H6→H7→H8→H9      [✅ 已完成 2026-06-16]
                      → 重跑生成器                         [✅ 已完成]
批次 2 (Post-Gen A):  I2+I8+I14+E1+C1(3个索引)                [1个合并SQL脚本]
批次 3 (Post-Gen B):  I5+I9+A4                            [1个合并SQL脚本]
批次 4 (Governance):  I13+I15+A2(暂缓，当前无需执行)       [1个合并SQL脚本]
批次 5 (Finalize):    E3 + C2 + B1/B2 + F1 + ✅G5 + K1      [✅ G5已完成，5个独立操作]
```

> **施工总文件数**：4个合并SQL脚本 + 6个独立操作
> **施工总命令数**：~10条（含验证SQL）
> **已完成批次**：批次0-1（Pre-Flight + Generator）已全部完成。深度审查后，批次2-5大幅简化：7项需重新校验 + 5项真正需修复 + 3项未来扩展。

---

## 十四、文件类型 × 架构层评估

| 文件类型 | 数量 | 架构层 | 设计水平 | 关键问题 |
|---------|-----|--------|:---:|---------|
| .py 模块 | ~3,000+ | L0-L3（4标准层） | ✅ | 层标签已归一化（A1已CLOSED） |
| .py 脚本 | ~500 | scripts/ | ✅ | scaffold.py唯一入口+manifest注册 |
| .py 测试 | ~2,100 | tests/ | ⚠️ | 扁平结构，搬迁计划包含测试目录重组（C2已CLOSED） |
| .md 蓝图 | ~160 | docs/03_modules/ | ✅ | 三层蓝图体系+模板强约束 |
| .md 文档 | ~5,000 | docs/ | ✅ | 5域分层+编号标准+压缩工作流 |
| .yaml 门禁 | ~110 | gates/ | ✅ | GateEngine+46门控+入场门禁 |
| .yaml 配置 | ~1,300 | config/data/ | ⚠️ | 8个超容域（§十二跟踪），D-TEST已豁免 |
| .yaml 契约 | ~360 | contracts/ | ✅ | 域间契约+版本化设计 |
| .yaml 注册表 | ~64 | 各目录 | ✅ | 29注册表体系 |
| .json 数据 | ~1,000 | data/cache/ | ✅ | Merkle审计链+增量缓存 |
| .db 数据库 | 11 | data/databases/ | ⚠️ | 3个索引缺失（C1跟踪） |
| .jsonl 日志 | ~25 | logs/data/ | ✅ | WAL+审计链 |

---

## 十五、depgraph.db 表结构参考

> **来源**：原 `_depgraph_guard_review_data.md` §2（2026-06-17 合并）。**注意**：以下为 V3.4 迁移前 schema。当前实际 schema 已升级至 V5（P0-1+P0-6 迁移后）：nodes 41列，edges 23列，arch_directory_tree 11列，共25表（24业务+1系统）。最新 schema 见 `PRAGMA table_info()` 或 `architecture_upgrade_discussion.md` §18.3。

### 所有表名

_schema_version, arch_bottlenecks, arch_constraints, arch_directory_tree, arch_domain_capacity, arch_domain_layers, arch_layers, arch_path_mappings, contracts, domain_dependencies, domain_events, domains, edges, invariants, nodes, rule_bindings, sqlite_sequence

### nodes 表结构（31列）

| cid | name | type | notnull | dflt_value | pk |
|-----|------|------|---------|------------|----|
| 0 | node_id | TEXT | 0 | None | 1 |
| 1 | node_type | TEXT | 1 | None | 0 |
| 2 | path | TEXT | 1 | None | 0 |
| 3 | granularity | TEXT | 1 | 'file' | 0 |
| 4 | domain_id | TEXT | 0 | None | 0 |
| 5 | subdomain_id | TEXT | 0 | None | 0 |
| 6 | blueprint_id | TEXT | 0 | None | 0 |
| 7 | belongs_to | TEXT | 0 | None | 0 |
| 8 | owner | TEXT | 0 | None | 0 |
| 9 | change_policy | TEXT | 0 | 'evolving' | 0 |
| 10 | impact_level | TEXT | 0 | 'M' | 0 |
| 11 | modification_permission | TEXT | 0 | 'ai_modifiable' | 0 |
| 12 | file_header_score | INTEGER | 0 | 0 | 0 |
| 13 | tags | TEXT | 0 | None | 0 |
| 14 | architecture_layer | TEXT | 0 | None | 0 |
| 15 | design_maturity | TEXT | 0 | 'production' | 0 |
| 16 | deployment_lifecycle | TEXT | 0 | 'stable' | 0 |
| 17 | trust_zone | TEXT | 0 | 'trusted_core' | 0 |
| 18 | license | TEXT | 0 | 'Internal' | 0 |
| 19 | drive_direction | TEXT | 0 | 'bottom_up' | 0 |
| 20 | type_specific_data | TEXT | 0 | None | 0 |
| 21 | last_verified | TEXT | 0 | None | 0 |
| 22 | node_name | TEXT | 0 | '' | 0 |
| 23 | file_path | TEXT | 0 | '' | 0 |
| 24 | build_status | TEXT | 0 | 'draft' | 0 |
| 25 | module_lifecycle_state | TEXT | 0 | 'inactive' | 0 |
| 26 | can_build | INTEGER | 0 | 1 | 0 |
| 27 | gate_reason | TEXT | 0 | None | 0 |
| 28 | hard_boundary_ref | TEXT | 0 | None | 0 |
| 29 | consumed_interfaces | TEXT | 0 | None | 0 |
| 30 | implementation_ref | TEXT | 0 | None | 0 |

### edges 表结构（23列，V5 Schema）

> **2026-06-18 更新**：P0-1 Schema迁移后，from_node/to_node（TEXT）→ from_node_id/to_node_id（INTEGER外键），新增 dep_maturity/valid_since/migration_status/is_legal_cycle 4列。

| cid | name | type | notnull | dflt_value | pk |
|-----|------|------|---------|------------|----|
| 0 | edge_id | INTEGER | 0 | None | 1 |
| 1 | from_node_id | INTEGER | 1 | None | 0 |
| 2 | to_node_id | INTEGER | 1 | None | 0 |
| 3 | dep_type | TEXT | 1 | None | 0 |
| 4 | architecture_direction | TEXT | 0 | 'downstream' | 0 |
| 5 | coupling_strength | TEXT | 0 | 'critical' | 0 |
| 6 | used_symbol | TEXT | 0 | None | 0 |
| 7 | invocation_method | TEXT | 0 | None | 0 |
| 8 | api_contract_refs | TEXT | 0 | None | 0 |
| 9 | event_ref | TEXT | 0 | None | 0 |
| 10 | ddd_integration_pattern | TEXT | 0 | None | 0 |
| 11 | failure_mode | TEXT | 0 | None | 0 |
| 12 | fallback | TEXT | 0 | None | 0 |
| 13 | activation_condition | TEXT | 0 | None | 0 |
| 14 | data_transfer_description | TEXT | 0 | None | 0 |
| 15 | resource_impact | TEXT | 0 | None | 0 |
| 16 | relationship_type | TEXT | 0 | 'one_to_many' | 0 |
| 17 | cross_domain | INTEGER | 0 | 0 | 0 |
| 18 | verified | INTEGER | 0 | 0 | 0 |
| 19 | dep_maturity | TEXT | 0 | None | 0 |
| 20 | valid_since | TEXT | 0 | None | 0 |
| 21 | migration_status | TEXT | 0 | None | 0 |
| 22 | is_legal_cycle | INTEGER | 0 | 0 | 0 |

### arch_directory_tree 表结构（11列，V5 Schema）

> **2026-06-18 更新**：P0-1 Schema迁移后，state 字段已删除，新增 node_id 外键字段（关联 nodes 表）。

| cid | name | type | notnull | dflt_value | pk |
|-----|------|------|---------|------------|----|
| 0 | path | TEXT | 0 | None | 1 |
| 1 | parent_path | TEXT | 0 | None | 0 |
| 2 | path_type | TEXT | 1 | None | 0 |
| 3 | domain_id | TEXT | 0 | None | 0 |
| 4 | state | TEXT | 1 | 'design' | 0 |
| 5 | blueprint_id | TEXT | 0 | None | 0 |
| 6 | change_policy | TEXT | 0 | None | 0 |
| 7 | modification_permission | TEXT | 0 | None | 0 |
| 8 | last_scanned | TEXT | 0 | None | 0 |
| 9 | build_status | TEXT | 0 | 'unbuilt' | 0 |
| 10 | design_maturity | TEXT | 0 | None | 0 |

> **注**：arch_directory_tree 表在 V3.4 施工时将新增 node_id 外键字段，替换删除的 state 字段（cid=4）。详见能力定位书 §22.4。当前 schema 仍保留 state 字段。

### arch_constraints 表结构（9列）

| cid | name | type | notnull | dflt_value | pk |
|-----|------|------|---------|------------|----|
| 0 | constraint_id | TEXT | 0 | None | 1 |
| 1 | name | TEXT | 1 | None | 0 |
| 2 | constraint_type | TEXT | 1 | None | 0 |
| 3 | from_domain | TEXT | 0 | None | 0 |
| 4 | to_domain | TEXT | 0 | None | 0 |
| 5 | rule_definition | TEXT | 1 | None | 0 |
| 6 | severity | TEXT | 0 | 'hard' | 0 |
| 7 | enforcement | TEXT | 0 | 'gate' | 0 |
| 8 | description | TEXT | 0 | None | 0 |

### domain_dependencies 表结构（5列）

| cid | name | type | notnull | dflt_value | pk |
|-----|------|------|---------|------------|----|
| 0 | from_domain | TEXT | 1 | None | 1 |
| 1 | to_domain | TEXT | 1 | None | 2 |
| 2 | edge_count | INTEGER | 0 | 0 | 0 |
| 3 | edge_types | TEXT | 0 | None | 0 |
| 4 | constraint_type | TEXT | 0 | None | 0 |

### domains 表结构（14列）

| cid | name | type | notnull | dflt_value | pk |
|-----|------|------|---------|------------|----|
| 0 | domain_id | TEXT | 0 | None | 1 |
| 1 | domain_name | TEXT | 1 | None | 0 |
| 2 | domain_group | TEXT | 1 | None | 0 |
| 3 | description | TEXT | 0 | None | 0 |
| 4 | ssot_path | TEXT | 0 | None | 0 |
| 5 | current_modules | INTEGER | 0 | 0 | 0 |
| 6 | max_modules | INTEGER | 0 | None | 0 |
| 7 | lifecycle | TEXT | 0 | 'design_only' | 0 |
| 8 | created_at | TEXT | 1 | None | 0 |
| 9 | updated_at | TEXT | 1 | None | 0 |
| 10 | build_status | TEXT | 0 | 'unbuilt' | 0 |
| 11 | can_build | INTEGER | 0 | 1 | 0 |
| 12 | gate_reason | TEXT | 0 | None | 0 |
| 13 | hard_boundary_ref | TEXT | 0 | None | 0 |

### contracts 表结构（7列）

| cid | name | type | notnull | dflt_value | pk |
|-----|------|------|---------|------------|----|
| 0 | contract_id | TEXT | 0 | None | 1 |
| 1 | name | TEXT | 1 | None | 0 |
| 2 | provider_domain | TEXT | 1 | None | 0 |
| 3 | consumer_domain | TEXT | 1 | None | 0 |
| 4 | contract_type | TEXT | 1 | None | 0 |
| 5 | schema_definition | TEXT | 0 | None | 0 |
| 6 | version | TEXT | 0 | None | 0 |

### arch_domain_capacity 表结构（8列）

| cid | name | type | notnull | dflt_value | pk |
|-----|------|------|---------|------------|----|
| 0 | domain_id | TEXT | 0 | None | 1 |
| 1 | current_modules | INTEGER | 0 | 0 | 0 |
| 2 | max_modules | INTEGER | 1 | None | 0 |
| 3 | growth_pattern | TEXT | 0 | 'linear' | 0 |
| 4 | target_modules | INTEGER | 0 | None | 0 |
| 5 | feasibility | TEXT | 0 | 'feasible' | 0 |
| 6 | bottleneck_description | TEXT | 0 | None | 0 |
| 7 | last_capacity_check | TEXT | 0 | None | 0 |

### arch_path_mappings 表结构（7列）

| cid | name | type | notnull | dflt_value | pk |
|-----|------|------|---------|------------|----|
| 0 | mapping_id | INTEGER | 0 | None | 1 |
| 1 | domain_id | TEXT | 1 | None | 0 |
| 2 | path_pattern | TEXT | 1 | None | 0 |
| 3 | path_type | TEXT | 1 | None | 0 |
| 4 | state | TEXT | 1 | 'design' | 0 |
| 5 | covers | TEXT | 0 | None | 0 |
| 6 | aliases | TEXT | 0 | None | 0 |

### domain_events 表结构（6列，J2后7列）

| cid | name | type | notnull | dflt_value | pk |
|-----|------|------|---------|------------|----|
| 0 | event_id | TEXT | 0 | None | 1 |
| 1 | name | TEXT | 1 | None | 0 |
| 2 | source_domain | TEXT | 1 | None | 0 |
| 3 | target_domains | TEXT | 0 | None | 0 |
| 4 | payload_schema | TEXT | 0 | None | 0 |
| 5 | priority | TEXT | 0 | 'P1' | 0 |

> **J2 修复后新增**：`event_type TEXT DEFAULT 'domain_event'`

### rule_bindings 表结构（6列，J3后7列）

| cid | name | type | notnull | dflt_value | pk |
|-----|------|------|---------|------------|----|
| 0 | binding_id | INTEGER | 0 | None | 1 |
| 1 | function_name | TEXT | 1 | None | 0 |
| 2 | rule_id | TEXT | 1 | None | 0 |
| 3 | binding_type | TEXT | 1 | None | 0 |
| 4 | trigger_type | TEXT | 1 | None | 0 |
| 5 | trigger_id | TEXT | 0 | None | 0 |

> **J3 修复后新增**：`domain_id TEXT`

### 其他表结构

**arch_layers（5列）**：layer_id(PK), layer_name, layer_description, decision_type, parent_layer

**arch_domain_layers（2列）**：domain_id(PK1), layer_id(PK2)

**arch_bottlenecks（9列）**：bottleneck_id(PK), area, description, severity, current_impact, proposed_solution, status, detected_at, resolved_at

**invariants（5列）**：invariant_id(PK), domain_id, description, constraint_type, enforcement

**_schema_version（3列）**：version(PK), applied_at, description

---

## 十六、引用源文件

> **2026-06-17 噪音精简**：原 §十七 包含 _sync_all.py 和 audit_domain_nodes.py 的完整源码（约140行），这些脚本在项目中实际存在，可用 Read 工具直接读取，无需在文档中复制。

### 引用脚本路径

| 脚本 | 路径 | 用途 |
|------|------|------|
| _sync_all.py | `D:/ZephyrAlpha/scripts/governance/repair/_sync_all.py` | 全量同步所有域的 current_modules（A3 容量同步） |
| audit_domain_nodes.py | `D:/ZephyrAlpha/scripts/governance/repair/audit_domain_nodes.py` | 审计超容域的粒度分布（SRC-100200，当前8个超容域） |

> **注**：audit_domain_nodes.py 中的 domains_13 列表基于旧数据（含 D-SECURITY 等已解决域），实际使用时需基于当前8个超容域清单更新。
