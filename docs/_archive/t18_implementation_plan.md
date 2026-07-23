---
module_id: ARCH-ENT-005
title: "T18 设计态YAML化 — 施工方案"
status: active
version: 1.0.0
date: 2026-06-27
owner: ZephyrAlpha-Owner
ttl: permanent
---

# T18 设计态YAML化 — 施工方案

> **文档ID**: ARCH-T18-IMPL-001
> **创建时间**: 2026-06-21
> **最后更新**: 2026-06-21（Owner讨论后更新状态）
> **关联决策**: _archive/architecture_decisions_pending.md 决策4 (T18)
> **状态**: ⏸ **暂缓** — 转为阶段8业务层建设的"生产环节"，当前不执行
> **风险等级**: 极高（涉及全景图核心数据，数据量比预估大66倍）
> **AI_AUTONOMY**: human_gated（需Owner审批）

---

## 〇、Owner讨论结论（2026-06-21）

### 裁定：T18暂缓，转为未来"生产环节"

**核心共识**：

1. **全景图的核心价值已达成共识**：depgraph是完整的项目蓝图，所有模块依赖、数据流向、边界约束都在里面更新和对齐。有了全景图后，AI几乎不会产生幻觉和漂移——全局依赖关系可查、模块边界清晰、数据流向明确。

2. **T18的本质是"生产环节"而非"治理环节"**：
   - T18描述的YAML化实际上是"按域生产蓝图"的过程
   - 应该等业务域一个一个设计好、蓝图做好、代码做好后再生产
   - 不是现在做的治理工作，而是阶段8业务层建设时的生产工作

3. **未来生产流程**：
   ```
   业务域设计 → 域内依赖全景图设计 → 模块蓝图制作 → 代码实现
                                                        ↓
                                               按域导出蓝图（YAML或MD）
   ```

4. **蓝图格式倾向YAML**：Owner倾向于YAML格式，理由：
   - AI解析YAML无歧义（结构化字段）
   - 与现有规则体系一致（trae_XXX.yaml）
   - 程序可直接消费（yaml.load）
   - 字段明确性优于MD

5. **当前优先级**：先做阶段3数据治理（Phase A-I-E-C-B-F-K），T18推迟到阶段8业务层建设时按域生产。

### 本文档保留价值

本文档保留作为**未来生产环节的参考方案**，包含：
- §1 实际DB核实数据（8020节点+15295边+8595目录树，17个schema差异）
- §3-§9 施工步骤、风险评估、回滚方案、验收标准
- 未来重启时可直接参考，无需重新调研

### 未来重启条件

- 阶段8业务层建设启动
- 业务域设计完成，开始按域生产蓝图
- 届时重新评估蓝图格式（YAML vs MD）和拆分策略

### 关联文档变更

- T18_design_state_yaml_assessment.md — **已删除**（数据过时，边数预估230 vs 实际15295，差66倍）
- _archive/architecture_decisions_pending.md — T18状态更新为"暂缓"
- 本文档（T18_implementation_plan.md）— 保留，添加暂缓声明

---

## 一、实际DB核实数据（2026-06-21）

> ⚠️ **重大发现**：评估报告数据严重失实，以下为实际DB查询结果

### 0.1 实际数据量

| 指标 | 评估报告预估 | 实际值 | 差异 |
|------|:---:|:---:|:---:|
| 设计态节点数 | 7,977 | **8,020** | +43（小） |
| **设计态边数** | **~230** | **15,295** | **66倍！** |
| **arch_directory_tree设计态** | **~100** | **8,595** | **85倍！** |

### 0.2 实际Schema差异

| 表 | DDL字段数 | 实际字段数 | 缺失字段 |
|---|:---:|:---:|---|
| nodes | 30 | **41** | implementation_ref, has_dynamic_import, blueprint_id_invalid, in_degree, out_degree, blueprint_path, business_stream, stream_role, runtime_plane, ddd_aggregate, provided_interfaces |
| edges | 19 | **23** | from_node_id(原from_node), to_node_id(原to_node), dep_maturity, valid_since, migration_status, is_legal_cycle |

### 0.3 已有触发器保护

edges表已有3个设计态保护触发器：
- `chk_edges_design_immutable_update`
- `chk_edges_migration_status`
- `chk_edges_migration_status_update`

### 0.4 设计态边按类型分布

| dep_type | 数量 | 占比 |
|---|:---:|:---:|
| import_depends | 6,317 | 41.3% |
| contract | 2,963 | 19.4% |
| event | 2,186 | 14.3% |
| data | 2,179 | 14.2% |
| config_depends | 1,342 | 8.8% |
| runtime | 272 | 1.8% |
| domain_dependency | 36 | 0.2% |
| **合计** | **15,295** | **100%** |

### 0.5 设计态节点按域分布（精确值，Top 10）

| domain_id | 节点数 | 占比 |
|---|:---:|:---:|
| D_COMPLIANCE | 891 | 11.1% |
| D_RISK | 749 | 9.3% |
| D_GOVERNANCE | 605 | 7.5% |
| D_SECURITY | 603 | 7.5% |
| D_AUTONOMY_CORE | 475 | 5.9% |
| D_SIGLEGACY | 474 | 5.9% |
| D_INTEGRATION | 416 | 5.2% |
| D_INFRA_OPS | 387 | 4.8% |
| D_INFRA_RUNTIME | 311 | 3.9% |
| D_FACTOR | 302 | 3.8% |
| 其他29个域 | 2,807 | 35.0% |
| **合计** | **8,020** | **100%** |

### 0.6 重新预估YAML文件大小

| 数据类型 | 条目数 | 单条平均字节 | 总大小 |
|---------|:---:|:---:|:---:|
| 设计态节点 | 8,020 | ~650 B | ~5.2 MB |
| **设计态边** | **15,295** | **~400 B** | **~6.1 MB** |
| **设计态目录树** | **8,595** | **~200 B** | **~1.7 MB** |
| **合计** | — | — | **~13.0 MB** |

**结论**：总YAML大小从预估5.3MB增至**13MB**，edges必须按域拆分。

---

## 一、背景与目标

### 1.1 背景

当前depgraph混合了设计态和运营态数据，导致：
1. 设计态决策（域划分、路径映射、跨模块依赖声明）无法git审计
2. 7977个设计态节点存在二进制db中，git无法diff/merge/blame
3. AI不能直接Read（157MB OOM风险）
4. 设计态修改需apply_depgraph.py，无冲突可见性

### 1.2 目标

将设计态数据从depgraph迁移到YAML文件，实现：
- 设计态数据git可审计（diff/merge/blame）
- AI可直接Read设计态YAML（分域文件，<2MB）
- 设计态修改通过YAML编辑+sync脚本同步到DB
- DB保持查询加速层角色（只读缓存）

### 1.3 成功标准

| # | 标准 | 验证方式 |
|---|------|---------|
| 1 | 7977个设计态节点全部导出为YAML | 节点数对比 |
| 2 | 230条设计态边全部导出为YAML | 边数对比 |
| 3 | YAML→DB sync后数据一致 | 字段级对比 |
| 4 | DB设计态数据只读保护生效 | 触发器拦截测试 |
| 5 | apply_depgraph.py写入YAML而非DB | 功能测试 |
| 6 | 零数据丢失 | 迁移前后节点/边数对比 |

---

## 二、范围界定

### 2.1 做什么（In Scope）

| # | 工作项 | 说明 |
|---|--------|------|
| 1 | 核实实际DB schema | 查询PRAGMA table_info，消除DDL与DB不一致 |
| 2 | 更新depgraph_schema.py | 补全P0-1/P0-6/V3.4扩展字段 |
| 3 | 开发export脚本 | 一次性导出DB设计态数据→YAML文件 |
| 4 | 开发sync脚本 | YAML→DB单向同步（设计态节点+边） |
| 5 | 开发validate脚本 | YAML格式校验+字段完整性检查 |
| 6 | 改造apply_depgraph.py | 写入入口从DB改为YAML |
| 7 | 安装触发器保护 | nodes/edges表设计态数据只读保护 |
| 8 | 更新onboarding_detail.md | 真源声明更新 |
| 9 | 更新extract_depgraph.py | 支持从YAML+DB混合源提取 |
| 10 | 全量测试与验收 | 数据一致性+功能+回归测试 |

### 2.2 不做什么（Out of Scope）

| # | 排除项 | 理由 |
|---|--------|------|
| 1 | 运营态数据YAML化 | 运营态可由代码扫描重建，不需YAML化 |
| 2 | project-entity-depgraph.yaml处理 | 该yaml是废弃产物，阶段5后统一处理 |
| 3 | 规则yaml→db同步改造 | 已有sync_yaml_to_depgraph.py，不在本次范围 |
| 4 | depgraph物理结构变更 | 不改DB文件位置/大小/表结构 |
| 5 | 阶段5物理搬家 | 独立工作项，不合并 |

---

## 三、前置条件

### 3.1 强制前置条件（必须满足才能启动）

| # | 前置条件 | 状态 | 验证方式 |
|---|---------|:---:|---------|
| 1 | Owner审批T18裁定 | ⏸ 待审批 | _archive/architecture_decisions_pending.md决策4签字 |
| 2 | 阶段5物理搬家完成 | ⏸ 未开始 | 文件结构稳定，路径不再变化 |
| 3 | depgraph备份 | ⏸ 待做 | 复制到backup目录 |
| 4 | 无其他session操作depgraph | ⏸ 待验证 | lock_files.py status |

### 3.2 技术前置条件（施工第一步核实）

| # | 前置条件 | 验证方式 |
|---|---------|---------|
| 1 | 核实实际DB schema | `PRAGMA table_info(nodes)` + `PRAGMA table_info(edges)` |
| 2 | 查询精确设计态节点按域分布 | `SELECT domain_id, COUNT(*) FROM nodes WHERE design_maturity='design' GROUP BY domain_id` |
| 3 | 查询精确设计态边数量 | `SELECT COUNT(*) FROM edges WHERE dep_maturity='design'` |
| 4 | 确认DDL与DB差异 | 对比depgraph_schema.py与PRAGMA输出 |

---

## 四、施工阶段（分7步）

### STEP 1: Schema核实与DDL更新（前置）

**目标**：消除depgraph_schema.py与实际DB的schema不一致

**已核实差异**（2026-06-21实际查询）：

nodes表缺失11个字段：
- implementation_ref, has_dynamic_import, blueprint_id_invalid
- in_degree, out_degree, blueprint_path
- business_stream, stream_role, runtime_plane
- ddd_aggregate, provided_interfaces

edges表缺失6个字段（含字段名变更）：
- from_node(TEXT) → from_node_id(INTEGER) **字段名+类型变更**
- to_node(TEXT) → to_node_id(INTEGER) **字段名+类型变更**
- dep_maturity, valid_since, migration_status, is_legal_cycle

**操作**：
1. 更新depgraph_schema.py的_DDL_NODES，补全11个字段
2. 更新depgraph_schema.py的_DDL_EDGES，修正from_node→from_node_id等6个字段
3. 验证DDL更新后init_db幂等性（不能破坏现有DB）
4. 更新相关索引（from_node→from_node_id）

**产出**：
- 更新后的depgraph_schema.py（nodes 41字段 + edges 23字段）

**验收**：
- DDL字段数 = PRAGMA输出字段数（nodes 41 = 41, edges 23 = 23）
- `python -c "from zephyr.governance.depgraph_schema import init_db; init_db()"` 幂等执行
- 现有DB数据无丢失（init_db是CREATE IF NOT EXISTS，不删表）

**风险**：中（DDL变更可能影响依赖depgraph_schema.py的脚本）

**回滚**：git checkout depgraph_schema.py

**影响分析**：
- generate_project_depgraph.py：已用from_node_id（无需改）
- extract_depgraph.py：需检查是否用from_node（如果是需改）
- apply_depgraph.py：已用from_node_id（无需改）
- diagnose_depgraph.py：需检查

---

### STEP 2: 数据导出（一次性）

**目标**：将DB设计态数据导出为YAML文件

**操作**：
1. 开发export_design_state_to_yaml.py脚本
2. 执行导出：DB→YAML（按域拆分）
3. 验证导出完整性（节点数/边数对比）

**产出**：
```
data/asset_index/design_state/
├── nodes/
│   ├── D_COMPLIANCE.yaml          # 891节点
│   ├── D_RISK.yaml                # 749节点
│   ├── D_GOVERNANCE.yaml          # 605节点
│   └── ... (39个域文件，共8020节点)
├── edges/
│   ├── D_COMPLIANCE.yaml          # 按from_node的域拆分
│   ├── D_RISK.yaml
│   ├── D_GOVERNANCE.yaml
│   └── ... (39个域文件，共15295边)
├── arch_directory_tree/
│   └── design_arch.yaml           # 8595条目录树
└── index.yaml                     # 索引文件
```

**验收**：
- YAML节点数 = DB设计态节点数（**8020**）
- YAML边数 = DB设计态边数（**15295**）
- YAML目录树数 = DB设计态目录树数（**8595**）
- 字段完整性（所有必填字段非空）
- 17个缺失字段全部覆盖（nodes 11个 + edges 6个）

**风险**：高（数据量大，边数是预估的66倍，导出过程可能超时或遗漏）

**回滚**：删除data/asset_index/design_state/目录

**关键设计**：
- YAML中edges的from/to用path引用（非node_id，因为node_id是DB自增）
- YAML中排除DB自增字段（node_id/edge_id）
- YAML中排除派生字段（in_degree/out_degree/file_header_score等）
- **edges按from_node的domain_id拆分**（15295条边不能放单文件，会达6.1MB）
- arch_directory_tree单独文件（8595条，约1.7MB，在AI可读范围内）

---

### STEP 3: Sync脚本开发

**目标**：开发YAML→DB单向同步脚本

**操作**：
1. 开发sync_design_state_to_depgraph.py
2. 复用sync_yaml_to_depgraph.py的触发器管理模式
3. 实现冲突检测（YAML与DB不一致时报警）

**产出**：
- sync_design_state_to_depgraph.py脚本

**脚本结构**：
```python
def sync_design_state(cur):
    # 1. 禁用触发器
    disable_design_state_triggers(cur)
    # 2. 删除DB旧设计态数据
    cur.execute("DELETE FROM nodes WHERE design_maturity='design'")
    cur.execute("DELETE FROM edges WHERE dep_maturity='design'")
    # 3. 从YAML加载设计态数据
    nodes = load_yaml("data/asset_index/design_state/nodes/*.yaml")
    edges = load_yaml("data/asset_index/design_state/edges/design_edges.yaml")
    # 4. 插入DB
    for node in nodes:
        cur.execute("INSERT INTO nodes (...) VALUES (...)")
    for edge in edges:
        # path→node_id解析
        from_id = resolve_path_to_node_id(cur, edge['from_path'])
        to_id = resolve_path_to_node_id(cur, edge['to_path'])
        cur.execute("INSERT INTO edges (...) VALUES (...)")
    # 5. 恢复触发器
    restore_design_state_triggers(cur)
```

**验收**：
- sync后DB设计态节点数 = YAML节点数
- sync后DB设计态边数 = YAML边数
- 字段级一致性（随机抽检10个节点）

**风险**：高（sync可能覆盖DB数据）

**回滚**：从STEP 2的备份恢复DB

---

### STEP 4: 触发器保护安装

**目标**：DB设计态数据只读保护

**已有触发器**（2026-06-21核实）：
edges表已有3个设计态保护触发器：
- `chk_edges_design_immutable_update` — 禁止UPDATE设计态边
- `chk_edges_migration_status` — 迁移状态检查
- `chk_edges_migration_status_update` — 迁移状态UPDATE检查

**操作**：
1. 评估现有edges触发器是否满足T18需求（可能已足够，无需新增）
2. 为nodes表新增设计态保护触发器（INSERT/UPDATE/DELETE）
3. 为edges表补充缺失的触发器（INSERT/DELETE，如果现有只有UPDATE）
4. sync脚本中实现disable/restore机制

**触发器设计**（nodes表新增）：
```sql
-- nodes表设计态保护（3个触发器）
CREATE TRIGGER nodes_design_readonly_insert
BEFORE INSERT ON nodes
WHEN NEW.design_maturity = 'design'
BEGIN
    SELECT RAISE(ABORT, 'nodes设计态数据只读，请修改YAML后运行sync_design_state_to_depgraph.py');
END;

CREATE TRIGGER nodes_design_readonly_update
BEFORE UPDATE ON nodes
WHEN NEW.design_maturity = 'design' OR OLD.design_maturity = 'design'
BEGIN
    SELECT RAISE(ABORT, 'nodes设计态数据只读，请修改YAML后运行sync_design_state_to_depgraph.py');
END;

CREATE TRIGGER nodes_design_readonly_delete
BEFORE DELETE ON nodes
WHEN OLD.design_maturity = 'design'
BEGIN
    SELECT RAISE(ABORT, 'nodes设计态数据只读，请修改YAML后运行sync_design_state_to_depgraph.py');
END;
```

**edges表触发器**：
- 评估现有3个触发器是否覆盖INSERT/UPDATE/DELETE
- 如不覆盖，补充缺失的触发器

**验收**：
- 直接INSERT设计态节点→被触发器拒绝
- 直接UPDATE设计态节点→被触发器拒绝
- 直接DELETE设计态节点→被触发器拒绝
- sync脚本运行（disable触发器后）→正常写入
- 现有edges触发器与新增nodes触发器协同工作

**风险**：高（触发器可能影响generate_project_depgraph.py等现有脚本）

**回滚**：DROP TRIGGER nodes_design_readonly_*

**影响分析**：
- generate_project_depgraph.py：会写设计态节点→需在sync脚本中disable触发器
- apply_depgraph.py：STEP 5改造后写YAML，不直接写DB→无影响
- 其他直接写DB的脚本：需排查并适配

---

### STEP 5: apply_depgraph.py改造

**目标**：设计态写入入口从DB改为YAML

**操作**：
1. --add-design-node改为写YAML文件
2. --add-design-edge改为写YAML文件
3. 保留--add-design-node-legacy（兼容旧DB写入，标记deprecated）

**改造内容**：
```python
# 旧：直接写DB
def add_design_node(path, ...):
    INSERT INTO nodes (...) VALUES (...)

# 新：写YAML
def add_design_node(path, ...):
    yaml_file = f"data/asset_index/design_state/nodes/{domain_id}.yaml"
    append_to_yaml(yaml_file, node_dict)
    print(f"[YAML] 设计态节点已写入 {yaml_file}")
    print(f"[提示] 运行 sync_design_state_to_depgraph.py 同步到DB")
```

**验收**：
- --add-design-node生成YAML条目
- --add-design-edge生成YAML条目
- 生成的YAML格式正确

**风险**：中（破坏现有工作流）

**回滚**：git checkout apply_depgraph.py

---

### STEP 6: 文档更新

**目标**：更新真源声明和消费指南

**操作**：
1. 更新onboarding_detail.md STEP 1.2/4.15
2. 更新_archive/architecture_decisions_pending.md T18状态
3. 更新architecture_upgrade_discussion.md §18.3

**更新内容**：
- 真源声明：设计态YAML + 运营态DB
- AI消费路径：设计态直接Read YAML + 运营态extract_depgraph.py
- sync流程：YAML→DB单向

**验收**：
- 文档与实际实现一致
- 无过时引用

**风险**：低

**回滚**：git checkout

---

### STEP 7: 全量测试与验收

**目标**：验证整体方案的正确性

**测试计划**：
1. **数据一致性测试**：YAML节点数=DB节点数，字段级对比
2. **触发器测试**：直接写DB被拒，sync脚本正常
3. **功能测试**：apply_depgraph.py写YAML，sync同步到DB
4. **回归测试**：现有脚本（extract_depgraph.py等）正常工作
5. **AI消费测试**：AI能直接Read YAML理解设计态

**验收清单**：
- [ ] YAML节点数 = 7977
- [ ] YAML边数 = ~230
- [ ] sync后DB数据一致
- [ ] 触发器保护生效
- [ ] apply_depgraph.py写YAML
- [ ] 现有脚本无回归
- [ ] 文档更新完成

---

## 五、风险评估与缓解

> ⚠️ **风险升级**：实际数据量比预估大66倍（边数230→15295），风险等级从"高"升级为"极高"

### 5.1 极高风险项

| # | 风险 | 影响 | 缓解措施 | 应急方案 |
|---|------|------|---------|---------|
| 1 | **导出15295条边超时/丢数据** | 设计态边丢失 | 分批导出（按域）+ 边数对比 + 字段级抽检 | 从DB备份恢复 |
| 2 | **sync覆盖DB数据（15295边）** | DB设计态边被清空 | sync前自动备份DB + 事务回滚 | 从备份恢复 |
| 3 | **触发器影响generate_project_depgraph.py** | 生成器崩溃，无法更新depgraph | 生成器适配disable触发器 + 全量回归测试 | DROP TRIGGER |
| 4 | **17个schema字段遗漏** | YAML数据不完整 | STEP 1先更新DDL + 字段对比 | 修正DDL后重做 |
| 5 | **edges YAML按域拆分逻辑错误** | 边归属错误，跨域边丢失 | 双向验证（from域+to域）+ 边数对比 | 重新导出 |

### 5.2 高风险项

| # | 风险 | 影响 | 缓解措施 | 应急方案 |
|---|------|------|---------|---------|
| 1 | YAML文件过大（13MB总量） | AI无法全量加载 | 按域拆分（39文件×3类型=117文件） | 增加拆分粒度 |
| 2 | arch_directory_tree 8595条YAML化 | 单文件1.7MB | 按域拆分或分块加载 | 按域拆分 |
| 3 | 现有edges触发器与新增nodes触发器冲突 | 触发器互相干扰 | 评估现有触发器逻辑 + 协同测试 | DROP冲突触发器 |

### 5.3 中风险项

| # | 风险 | 影响 | 缓解措施 |
|---|------|------|---------|
| 1 | apply_depgraph.py改造破坏工作流 | 用户习惯中断 | 保留legacy命令+deprecated警告 |
| 2 | YAML与DB双源不一致 | 数据漂移 | sync脚本强制单向+触发器保护 |
| 3 | 代码节点设计态与运营态冲突 | 双源数据 | sync时检测path是否已实现 |
| 4 | extract_depgraph.py改造影响AI冷启动 | AI无法获取设计态数据 | 保留DB读取fallback + 双源支持 |

---

## 六、回滚方案

### 6.1 分步回滚

| 步骤 | 回滚操作 | 命令 |
|------|---------|------|
| STEP 7 | 无需回滚（测试阶段） | - |
| STEP 6 | 还原文档 | `git checkout docs/` |
| STEP 5 | 还原apply_depgraph.py | `git checkout scripts/governance/apply_depgraph.py` |
| STEP 4 | 删除触发器 | `DROP TRIGGER nodes_design_readonly_*` |
| STEP 3 | 还原DB数据 | 从STEP 2前的DB备份恢复 |
| STEP 2 | 删除YAML文件 | `rm -rf data/asset_index/design_state/` |
| STEP 1 | 还原DDL | `git checkout src/zephyr/governance/depgraph_schema.py` |

### 6.2 紧急回滚（数据丢失时）

```bash
# 1. 立即停止所有sync操作
# 2. 从备份恢复DB（P2迁移后使用pg_restore，原SQLite .db文件已废弃）
psql -d depgraph -f data/backups/depgraph_pre_t18.sql
# 3. 删除YAML文件
rm -rf data/asset_index/design_state/
# 4. 还原所有代码
git checkout src/zephyr/governance/depgraph_schema.py
git checkout scripts/governance/apply_depgraph.py
# 5. 删除触发器（如果已安装）——P2迁移后使用psycopg2，原sqlite3模块已废弃
python -c "from zephyr.governance.depgraph_schema import get_db_connection; c=get_db_connection(); cur=c.cursor(); cur.execute('DROP TRIGGER IF EXISTS nodes_design_readonly_insert ON nodes'); c.commit(); ..."
```

---

## 七、验收标准

### 7.1 数据完整性验收

| # | 验收项 | 标准 | 验证方法 |
|---|--------|------|---------|
| 1 | 节点数一致 | YAML节点数 = DB设计态节点数 | COUNT对比 |
| 2 | 边数一致 | YAML边数 = DB设计态边数 | COUNT对比 |
| 3 | 字段完整 | 所有必填字段非空 | 随机抽检10个节点 |
| 4 | 字段准确 | YAML值 = DB值 | 字段级对比 |

### 7.2 功能验收

| # | 验收项 | 标准 |
|---|--------|------|
| 1 | sync脚本 | YAML→DB同步成功，数据一致 |
| 2 | 触发器 | 直接写DB被拒，sync正常 |
| 3 | apply_depgraph | 写YAML而非DB |
| 4 | extract_depgraph | 正常提取数据 |
| 5 | 现有脚本 | 无回归 |

### 7.3 AI可读性验收

| # | 验收项 | 标准 |
|---|--------|------|
| 1 | YAML文件大小 | 最大文件<2MB |
| 2 | AI直接Read | 能理解YAML结构 |
| 3 | 增量加载 | 能按域加载单文件 |

---

## 八、测试计划

### 8.1 单元测试

| 测试项 | 测试内容 | 测试文件 |
|--------|---------|---------|
| export脚本 | 导出正确性 | tests/test_export_design_state.py |
| sync脚本 | 同步正确性 | tests/test_sync_design_state.py |
| validate脚本 | 校验正确性 | tests/test_validate_design_state.py |
| 触发器 | 拦截正确性 | tests/test_design_state_triggers.py |

### 8.2 集成测试

| 测试项 | 测试内容 |
|--------|---------|
| 端到端流程 | export→sync→validate→apply |
| 数据一致性 | YAML与DB字段级对比 |
| 回归测试 | 现有脚本正常工作 |

### 8.3 性能测试

| 测试项 | 标准 | 实际数据量 |
|--------|------|:---:|
| export耗时 | <120秒 | 8020节点+15295边+8595目录树 |
| sync耗时 | <60秒 | 8020节点+15295边 |
| YAML加载 | 单文件<5秒 | 最大文件~1.7MB |
| 触发器disable/restore | <1秒 | 6+个触发器 |

---

## 九、影响分析

### 9.1 受影响文件

| 文件 | 影响类型 | 说明 |
|------|---------|------|
| src/zephyr/governance/depgraph_schema.py | 修改 | 补全DDL字段 |
| scripts/governance/apply_depgraph.py | 修改 | 写入入口改YAML |
| scripts/governance/extract_depgraph.py | 修改 | 支持YAML源 |
| scripts/governance/sync_design_state_to_depgraph.py | 新增 | sync脚本 |
| scripts/governance/export_design_state_to_yaml.py | 新增 | export脚本 |
| scripts/governance/validate_design_state_yaml.py | 新增 | validate脚本 |
| .trae/rules/onboarding_detail.md | 修改 | 真源声明 |
| docs/_archive/architecture_decisions_pending.md | 修改 | T18状态 |
| data/asset_index/design_state/*.yaml | 新增 | 设计态YAML文件 |

### 9.2 受影响流程

| 流程 | 影响 | 缓解 |
|------|------|------|
| AI冷启动 | 设计态从YAML读，运营态从DB读 | 更新onboarding_detail.md |
| 设计态节点添加 | apply_depgraph写YAML+sync | 保留legacy命令 |
| depgraph生成 | 生成器保留设计态 | 无影响（生成器已支持） |
| depgraph查询 | extract_depgraph支持YAML | 改造extract脚本 |

---

## 十、施工顺序与依赖

```
STEP 1 (Schema核实) → STEP 2 (数据导出) → STEP 3 (Sync脚本)
                                              ↓
                                         STEP 4 (触发器)
                                              ↓
                                         STEP 5 (apply改造)
                                              ↓
                                         STEP 6 (文档更新)
                                              ↓
                                         STEP 7 (全量测试)
```

**关键依赖**：
- STEP 2依赖STEP 1（schema核实后才能正确导出）
- STEP 3依赖STEP 2（有YAML才能开发sync）
- STEP 4依赖STEP 3（sync脚本管理触发器）
- STEP 5依赖STEP 3（apply调用sync）
- STEP 7依赖所有前置步骤

---

## 十一、审查清单

施工方案审查清单（审查通过后建卡执行）：

### 11.1 方案完整性审查

- [ ] 背景与目标清晰
- [ ] 范围界定明确（做什么/不做什么）
- [ ] 前置条件完整
- [ ] 施工步骤可执行
- [ ] 风险评估全面（含极高风险项）
- [ ] 回滚方案可行
- [ ] 验收标准可衡量
- [ ] 测试计划完整
- [ ] 影响分析全面

### 11.2 技术可行性审查

- [ ] YAML拆分策略合理（nodes按域+edges按域+arch独立）
- [ ] sync脚本设计可行（含15295边的性能考量）
- [ ] 触发器保护机制可行（复用现有edges触发器+新增nodes触发器）
- [ ] apply_depgraph改造可行
- [ ] 数据一致性保障可行（8020节点+15295边+8595目录树）
- [ ] 17个缺失字段的DDL更新可行
- [ ] edges按域拆分逻辑可行（跨域边处理）

### 11.3 风险控制审查

- [ ] 极高风险项有缓解措施（5项）
- [ ] 高风险项有缓解措施（3项）
- [ ] 回滚方案完整（分步回滚+紧急回滚）
- [ ] 紧急回滚可行（DB备份恢复）
- [ ] 数据备份策略完整（sync前自动备份）
- [ ] 触发器冲突评估完成

### 11.4 数据准确性审查（基于2026-06-21核实）

- [ ] 设计态节点数=8020（已核实）
- [ ] 设计态边数=15295（已核实，非230）
- [ ] arch_directory_tree设计态=8595（已核实，非100）
- [ ] nodes表41字段（已核实，DDL缺11个）
- [ ] edges表23字段（已核实，DDL缺6个）
- [ ] edges已有3个设计态触发器（已核实）
- [ ] 39个域的节点分布已核实

---

## 十二、下一步

1. **Owner审查本施工方案**：按§11审查清单逐项审查
2. **审查通过后建卡**：按RULE-SIX建卡（涉及>3文件+>50行新代码）
3. **执行施工**：按STEP 1-7顺序执行
4. **每步验收**：按各STEP的验收标准验收
5. **全量测试**：STEP 7全量测试通过后关闭任务卡

---

## 十三、相关文件

| 文件 | 路径 | 用途 |
|------|------|------|
| T18决策文档 | docs/_archive/architecture_decisions_pending.md | T18裁定原文（含暂缓结论） |
| ~~T18评估报告~~ | ~~已删除~~ | 数据过时（边数预估230 vs 实际15295），实际数据见本文档§1 |
| 本施工方案 | docs/02_enterprise_architecture/T18_implementation_plan.md | 本文档（暂缓，保留作未来参考） |
| Schema DDL | src/zephyr/governance/depgraph_schema.py | DB schema定义（需更新） |
| 现有sync脚本 | scripts/governance/sync_yaml_to_depgraph.py | 可复用模式 |
| 现有apply脚本 | scripts/governance/apply_depgraph.py | 需改造 |
| 现有extract脚本 | scripts/governance/extract_depgraph.py | 需改造 |
| 生成器 | scripts/governance/generate_project_depgraph.py | 双态保护逻辑 |
