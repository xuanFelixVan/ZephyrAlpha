# 全景图内容排查重造讨论

> 版本：V1.1 | 2026-06-19
> 读者：项目 Owner + AI 开发 Agent
> 目标：让全景图（depgraph.db）成为**可施工的最大蓝图**——去掉重复域/模块，统一域分类体系，重新设计依赖关系与路径架构。

## 关联文档（完整路径）

| 文档 | 完整路径 | 作用 |
|------|---------|------|
| 依赖与架构全景图能力定位书 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_architecture_panorama_capability.md` | 全景图能力定位、设计决策、裁定记录、七批次施工规格（§5-§22） |
| 架构升级深度讨论记录 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\architecture_upgrade_discussion.md` | 架构升级总纲：需求定义、39域裁定、8阶段工作流、当前进度（§1-§22） |
| depgraph 问题清单 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\depgraph_issue_registry.md` | 全景图已知问题清单与修复方案 |
| 功能域注册表（YAML 真源） | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\functional_domain_registry.yaml` | 9 小写域 + 35 subdomain 的 YAML 真源 |
| sync 同步脚本 | `D:\ZephyrAlpha\scripts\governance\sync_yaml_to_depgraph.py` | YAML→DB 同步（9 小写域 bug 根因，行 311） |

---

## 〇、架构升级大背景（本文档的上下文）

> 本排查重造是**架构升级总纲**（architecture_upgrade_discussion.md）的子任务。定位前先理解大流程。

### 0.1 架构升级总流程（8 阶段）

| 阶段 | 内容 | 状态 |
|:---:|------|:---:|
| 阶段0 | 安全网+修bug（ide_health_service 守护进程） | 部分完成 |
| 阶段1 | 确定整体架构+数据库设计+CI/CD | ✅ 已完成（CI/CD 未开始） |
| 阶段2 | R1/R2 升级（async runtime + DuckDB 时序存储） | 未开始 |
| 阶段3 | depgraph/全景图迁移到数据库 | 深化施工✅，数据治理待执行 |
| 阶段4 | 搬家对齐（实际目录→全景图设计）+ 全量清洁 | 未开始 |
| 阶段5-8 | R3-R8 升级 + 业务层建设 | 未开始 |

### 0.2 核心流程逻辑（Owner 描述，已核对正确）

```
1. 项目在经历架构级大更新，目的是满足 1,500 模块容量（设计上限 3,000）
   ← architecture_upgrade_discussion.md §1.5 规模目标：60→1,500→3,000

2. 数据库全景图（depgraph.db）是整个项目蓝图，包含所有文件夹/文件、
   功能域依赖关系和架构关系
   ← dependency_architecture_panorama_capability.md §一：依赖全景图管"谁依赖谁"，架构全景图管"放在哪"

3. 数据库全景图重新设计了一套全新文件路径，为满足 1,500 模块容量
   ← architecture_upgrade_discussion.md §3.1 抽屉架构扩容 + §17.6 39域方案
   ← §2.3 21个未映射目录裁定（旧目录→新域路径映射）

4. 实际目录结构/文件位置应按数据库全景图最新设计去修改和搬家
   ← architecture_upgrade_discussion.md §17.7 STEP 5 搬家 + 阶段4 搬家对齐

5. 修改全景图生成器代码，对齐实际目录结构和数据库全景图；
   在此之前不运行生成器，否则会覆盖全景图
   ← dependency_architecture_panorama_capability.md §4.4：生成器 DELETE+INSERT 运营态，
     但保留设计态（WHERE design_maturity='design'）
   ← 搬家前运行生成器会把旧目录结构扫进运营态，与设计态新路径冲突
   ← 阶段3 生成器升级已完成✅，但阶段4 搬家前不应运行生成器

6. 数据库全景图未来功能领域拓展可像抽屉一样增加
   ← architecture_upgrade_discussion.md §3.1 抽屉架构：src/zephyr/ 域路径，
     每个域一个抽屉，新增域=新增抽屉
```

**结论：Owner 描述的流程逻辑完全正确。**

### 0.3 当前进行到哪里

| 维度 | 状态 | 证据 |
|------|:---:|------|
| 阶段1 架构+DB 设计 | ✅ 完成 | 39域裁定+3库DDL+迁移框架（§5.2 STEP 1-2） |
| 阶段3 depgraph 深化施工 | ✅ 完成 | 七批次 P0-1~P0-7 全部完成（2026-06-18，§5.4） |
| 阶段3 数据治理 | ⏳ 待执行 | Phase A-I-E-C-B-F-K（10张卡，§22.1 下一步） |
| **本文档排查的 9 小写域问题** | 🔴 新发现 | sync 脚本 bug，domains 表 61 行（应为 39/52） |
| 阶段4 搬家对齐 | ❌ 未开始 | 依赖阶段3数据治理完成 |

**关键差距**：架构升级总纲裁定 **39 域**（§2.1），但数据库 domains 表实际有 **61 行**（52 D-XXX + 9 小写）。即：
- 总纲设计的 39 域方案尚未完全落地到数据库（D-XXX 52 域 vs 设计的 39 域，存在差异）
- 9 个小写域是 sync 脚本 bug 产生的脏数据（本文档§二排查结论）
- 阶段4 搬家对齐前，必须先清理 domains 表到正确的域数量

### 0.4 本文档在总流程中的定位

本文档（全景图内容排查重造）属于**阶段3 数据治理**的组成部分，具体是 Phase A（数据治理）的前置清理：
- 清理 domains 表 9 个小写域脏数据（阶段3 数据治理）
- 统一域分类体系（39域方案落地）
- 为阶段4 搬家对齐准备干净的蓝图

---

## 一、为什么要做这次排查重造

全景图是项目最大蓝图（裁定 #30：52 域；架构升级总纲裁定：39 域）。但当前数据库 `domains` 表实际有 **61 行**，存在两套并存的域分类体系，导致：

| 毛病 | 表现 | 后果 |
|------|------|------|
| 两套域体系并存 | 52 个 `D-XXX` 标准域 + 9 个小写命名域（data/governance/security 等） | AI 查全景图看到 61 个域，不知道该用哪套 |
| sync 脚本 bug | 9 个小写域的 domain_name 被折叠为"最后一条 subdomain" | 35 个 subdomain 只剩 9 条记录，34 条信息丢失 |
| 路径重复 | 3 处 ssot_path 被多个 D-XXX 域共享 | 域归属歧义，AI 建文件不知归哪个域 |
| 架构表不对齐 | arch_domain_layers(50) / arch_domain_capacity(52) / domains(61) 三表域数不一致 | 域容量/分层检查漏域 |
| YAML 理想路径与实际不符 | functional_domain_registry.yaml 的 35 个 subdomain 中 25 个 ssot_path 不存在 | 蓝图不可施工 |

**重造目标**：统一到 `D-XXX` 单一域体系，修复 sync 脚本，消除路径重复，三表对齐，让每个域的依赖关系和路径架构机械可施工。

---

## 二、排查结论：9 个小写命名域的来源

### 2.1 根因（已锁定）

**来源**：`functional_domain_registry.yaml` 经 `sync_yaml_to_depgraph.py` 同步写入。
**根因**：sync 脚本设计 bug——用 YAML 的 `domain` 字段（小写类别名）作 DB 的 `domain_id` 主键，UPSERT 折叠导致同 domain 下多个 subdomain 互相覆盖，只留最后一条。

### 2.2 唯一写入点

| 文件 | 行号 | 函数 | 操作 |
|------|:---:|------|------|
| [sync_yaml_to_depgraph.py](file:///d:/ZephyrAlpha/scripts/governance/sync_yaml_to_depgraph.py) | 311 | `sync_functional_domain_registry()` | `INSERT INTO domains ... ON CONFLICT(domain_id) DO UPDATE` |

### 2.3 Bug 机制

```python
# sync_yaml_to_depgraph.py 行 320-321
d.get('domain', ''),     # domain_id = 小写类别名（如 "governance"）← 主键
d.get('subdomain', ''),  # domain_name = subdomain（如 "semantic_audit"）
```

YAML 中 `domain: governance` 有 7 个 subdomain 条目 → UPSERT 按 domain_id 去重 → 7 条互相覆盖 → 只留最后一条 `semantic_audit`。

### 2.4 证据：DB 9 行 = YAML 每个 domain 的最后一条 subdomain

| DB domain_id | DB domain_name | YAML 该 domain 最后一条 subdomain |
|---|---|---|
| data | knowledge_management | knowledge_management（data 域第 4/最后） |
| governance | semantic_audit | semantic_audit（governance 域第 7/最后） |
| infrastructure | lifecycle_management | lifecycle_management（infrastructure 域第 6/最后） |
| intelligence | model_profiling | model_profiling（intelligence 域第 2/最后） |
| observability | feedback-loop | feedback-loop（observability 域第 4/最后） |
| orchestration | context_management | context_management（orchestration 域第 5/最后） |
| resilience | escalation | escalation（resilience 域第 3/最后） |
| security | adversarial_validation | adversarial_validation（security 域第 3/最后） |
| testing | code_dedup | code_dedup（testing 域第 1/唯一） |

9/9 完美匹配。`domain_group` 全为 `governance` 是因为 `tier` 字段在 YAML 顶层而非 entry 内，`d.get('tier', 'governance')` 永远返回默认值。

### 2.5 排除项

| 排查对象 | 结论 |
|---------|------|
| 迁移脚本 mig5_fill_gaps.py | ❌ 只 INSERT INTO nodes，不写 domains 表 |
| 设计态提取规则 | ❌ 临时工作区 MD 文件定义的是 D-XXX 大写域（见 mig5 SOURCE_MD_DOMAIN 映射） |
| 其他迁移脚本 | ❌ migrate_schema_v3.4/v5、migrate_arch_constraints_v1 均无 domains 表写入 |

---

## 三、全面排查：重复功能域/模块

### 3.1 domains 表 61 行构成

| 类型 | 数量 | 来源 | 有实际节点 |
|------|:---:|------|:---:|
| `D-XXX` 标准域 | 52 | 架构全景图/设计态迁移 | ✅（nodes 表有节点） |
| 小写命名域 | 9 | functional_domain_registry.yaml（sync bug 折叠） | ❌（nodes 表无小写 domain_id） |

### 3.2 ssot_path 重复（3 处）

| 重复路径 | 涉及域 | 问题 |
|---------|--------|------|
| `src/zephyr/data/` | D-DATA_GOV, D-DATA_SEC, D-MKT_DATA | 3 域共享同一路径前缀，归属歧义 |
| `src/zephyr/integration/` | D-INTEGRATION, D-INTEGRATION-GATEWAY | 2 域共享 |
| `src/zephyr/signal/` | D-SIGNAL, D-SIGNAL_FUNDAMENTAL | 2 域共享 |

### 3.3 nodes 表重复路径

**0 个重复**（Phase H+J 修复后已清零，见能力定位书 §18）。

### 3.4 架构三表对齐问题

| 表 | 域数 | 与 domains(61) 差异 |
|----|:---:|------|
| domains | 61 | 基准 |
| arch_domain_layers | 50 | 缺 12 个（9 小写 + D-GOV-DOCS/D-GOV-SCRIPTS/D-TEST），多 1 个（D-TRAE） |
| arch_domain_capacity | 52 | 缺 9 个小写域 |

### 3.5 functional_domain_registry.yaml 的 35 个 subdomain 与 D-XXX 域功能重叠

YAML 定义 9 大类 35 子域，**全部与 D-XXX 域功能重叠**，且 25 个 ssot_path 在项目中不存在（理想化路径）。

| YAML domain | subdomain 数 | ssot_path 存在数 | 对应 D-XXX 域（功能重叠） |
|-------------|:---:|:---:|------|
| governance | 7 | 7/7 | D-GOV-ENFORCEMENT/SCRIPTS/DRIFT/AUDIT, D-GOVERNANCE |
| security | 3 | 3/3 | D-SECURITY, D-SECURITY-LLM |
| orchestration | 5 | 0/5 | D-INTEGRATION, D-AUTONOMY-CORE, D-INFRA-RUNTIME, D-INTELLIGENCE |
| resilience | 3 | 0/3 | D-GOV-REPAIR, D-AUTONOMY-PERM |
| observability | 4 | 0/4 | D-GOV-AUDIT, D-INFRA-OPS, D-OPS |
| data | 4 | 1/4 | D-INFRA-OPS/RUNTIME, D-KNOWLEDGE |
| intelligence | 2 | 2/2 | D-ML-TRAIN |
| infrastructure | 6 | 0/6 | D-SHARED, D-INFRA-OPS/RUNTIME, D-INTEGRATION-GATEWAY, D-GOVERNANCE |
| testing | 1 | 0/1 | D-GOV-SCRIPTS |

**结论**：functional_domain_registry.yaml 是一套"理想化分类法"，与项目实际的 D-XXX 体系完全重叠且路径不符。两套体系并存是历史遗留，必须统一。

---

## 四、问题清单（按严重度排序）

| # | 问题 | 严重度 | 影响范围 | 根因 |
|---|------|:---:|---------|------|
| P1 | 两套域分类体系并存（D-XXX 52 + 小写 9） | 🔴 高 | 全景图可信度 | functional_domain_registry.yaml 与 D-XXX 体系未统一 |
| P2 | sync 脚本 UPSERT 折叠 bug | 🔴 高 | domains 表 9 行数据错误 | domain_id 主键选错（用 domain 而非 domain+subdomain） |
| P3 | 3 处 ssot_path 重复 | 🟡 中 | data/integration/signal 域归属歧义 | 域拆分时未拆分物理路径 |
| P4 | 架构三表域数不一致（61/50/52） | 🟡 中 | 域容量/分层检查漏域 | 三表无同步机制 |
| P5 | YAML 25 个 subdomain 路径不存在 | 🟡 中 | 蓝图不可施工 | YAML 是理想化分类，未对齐实际结构 |
| P6 | D-TRAE 域在 arch_domain_layers 但不在 domains | 🟢 低 | 单点不一致 | 历史遗留 |
| P7 | 9 个小写域 domain_group 全为 governance | 🟢 低 | 域分组错误 | tier 字段位置 bug |

---

## 五、重造方案

### 5.1 核心决策：统一到 D-XXX 单一域体系

**裁定**：废弃 functional_domain_registry.yaml 的小写 domain 分类法，将其 35 个 subdomain 作为 D-XXX 域的**子域描述**归并，不再作为独立域。

**理由**：
1. D-XXX 体系有实际节点（7,590 运营态 + 110 设计态），是事实标准
2. 小写体系无节点，纯理想化分类，且路径不符
3. 两套体系并存 = AI 困惑 = 蓝图不可施工
4. 能力定位书裁定 #30 已明确"52 域（以数据库实际值为准）"

### 5.2 35 个 subdomain → D-XXX 域归并映射

| YAML subdomain | 归并到 D-XXX 域 | 归并依据 |
|----------------|---------------|---------|
| rule_enforcement | D-GOV-ENFORCEMENT | 功能直接对应 |
| script_governance | D-GOV-SCRIPTS | 功能直接对应 |
| drift_detection | D-GOV-DRIFT | 功能直接对应 |
| registry_management | D-GOVERNANCE | 注册表治理属治理核心 |
| orphan_judgment | D-GOVERNANCE | 孤儿审判属治理核心 |
| audit_orchestration | D-GOV-AUDIT | 审计编排属审计域 |
| semantic_audit | D-GOV-AUDIT | 语义审计属审计域 |
| access_control | D-SECURITY | 访问控制属安全域 |
| llm_defense | D-SECURITY-LLM | LLM 防御独立子域 |
| adversarial_validation | D-SECURITY | 对抗验证属安全域 |
| pipeline_routing | D-INTEGRATION | 管线路由属集成域 |
| agent_lifecycle | D-AUTONOMY-CORE | Agent 生命周期属自治核心 |
| agent_communication | D-AUTONOMY-CORE | Agent 通信属自治核心 |
| runtime_core | D-INFRA-RUNTIME | 运行时核心属运行时基础设施 |
| context_management | D-INTELLIGENCE | 上下文管理属智能域 |
| rollback | D-GOV-REPAIR | 回滚属治理修复 |
| budget_enforcement | D-AUTONOMY-PERM | 预算执行属自治保护 |
| escalation | D-AUTONOMY-PERM | 升级属自治保护 |
| audit-trail | D-GOV-AUDIT | 审计追踪属审计域 |
| asset-inventory | D-INFRA-OPS | 资产盘点属运维 |
| telemetry | D-OPS | 遥测属运维域 |
| feedback-loop | D-OPS | 反馈环属运维域 |
| capacity-assurance | D-INFRA-OPS | 容量保障属运维 |
| persistence | D-INFRA-RUNTIME | 持久化属运行时 |
| vector_storage | D-KNOWLEDGE | 向量存储属知识域 |
| knowledge_management | D-KNOWLEDGE | 知识管理属知识域 |
| model_evaluation | D-ML-TRAIN | 模型评估属训练 |
| model_profiling | D-ML-TRAIN | 模型画像属训练 |
| shared_services | D-SHARED | 共享服务属共享域 |
| resource_optimization | D-INFRA-OPS | 资源优化属运维 |
| runtime_integration | D-INFRA-RUNTIME | 运行时集成属运行时 |
| mcp_servers | D-INTEGRATION-GATEWAY | MCP 服务器属集成网关 |
| task_management | D-GOVERNANCE | 任务管理属治理核心 |
| lifecycle_management | D-GOVERNANCE | 生命周期管理属治理核心 |
| code_dedup | D-GOV-SCRIPTS | 代码去重属脚本治理 |

### 5.3 路径重复解决方案

| 重复路径 | 解决方案 |
|---------|---------|
| `src/zephyr/data/` (3 域) | 拆分为 `src/zephyr/data/governance/` (D-DATA_GOV)、`src/zephyr/data/security/` (D-DATA_SEC)、`src/zephyr/data/market/` (D-MKT_DATA) |
| `src/zephyr/integration/` (2 域) | 拆分为 `src/zephyr/integration/core/` (D-INTEGRATION)、`src/zephyr/integration/gateway/` (D-INTEGRATION-GATEWAY) |
| `src/zephyr/signal/` (2 域) | 拆分为 `src/zephyr/signal/technical/` (D-SIGNAL)、`src/zephyr/signal/fundamental/` (D-SIGNAL_FUNDAMENTAL) |

**注意**：路径拆分涉及文件迁移，必须走 RULE-TEN 治理施工流程（§15 五步强制流程：依赖图推演→蓝图归属→导入路径映射→执行→验证）。

### 5.4 sync 脚本修复方案

```python
# 修复 sync_functional_domain_registry() 行 320-321
# 错误：用 domain 作 domain_id 主键
# 正确：用 domain+subdomain 组合作唯一键，但 domain_id 仍映射到 D-XXX 域

# 方案 A（推荐）：废弃小写域同步，YAML 改为 D-XXX 域的子域描述表
#   - functional_domain_registry.yaml 重构为 D-XXX 域的 subdomain 清单
#   - sync 脚本不再 INSERT domains 表（D-XXX 域已由其他途径定义）
#   - sync 脚本改为 INSERT 新表 domain_subdomains（记录 D-XXX 域下的子域）

# 方案 B：保留 YAML 结构，修复 sync 脚本主键
#   - domain_id = f"{domain}.{subdomain}"（如 "governance.rule_enforcement"）
#   - 但这会产生 35 个新域，与 D-XXX 体系冲突，不推荐
```

**推荐方案 A**：YAML 重构为 D-XXX 子域描述，sync 脚本不再写 domains 表。

### 5.5 架构三表对齐方案

| 表 | 操作 |
|----|------|
| domains | 删除 9 个小写域，保留 52 个 D-XXX 域（+ 补 D-TRAE 若需要） |
| arch_domain_layers | 补齐 D-GOV-DOCS/D-GOV-SCRIPTS/D-TEST，删除 D-TRAE（或补到 domains） |
| arch_domain_capacity | 已是 52 域，与 domains 对齐后一致 |

---

## 六、各功能域依赖关系与路径架构重新设计

### 6.1 当前 D-XXX 域节点规模分布（前 15）

| domain_id | 节点数 | 不同路径前缀数 | 容量健康度 |
|-----------|:---:|:---:|------|
| D-TEST | 2105 | 2034 | ⚠️ 测试域过大，应拆分 |
| D-INFRA_RUNTIME | 937 | 580 | ⚠️ 接近上限 |
| D-GOVERNANCE | 743 | 467 | ⚠️ 治理核心过载 |
| D-OPS | 456 | 386 | 正常 |
| D-GOV-SCRIPTS | 360 | 215 | 正常 |
| D-SECURITY | 350 | 83 | ⚠️ 路径集中度高 |
| D-INTEGRATION | 321 | 115 | 正常 |
| D-SHARED | 305 | 256 | 正常 |
| D-GOV-REPAIR | 241 | 43 | ⚠️ 路径集中度高 |
| D-AUTONOMY-CORE | 225 | 118 | 正常 |
| D-GOV-DOCS | 207 | 42 | ⚠️ 路径集中度高 |
| D-GOV-AUDIT | 171 | 2 | 🔴 路径极度集中（仅 2 前缀） |
| D-TRADING | 168 | 85 | 正常 |
| D-RISK | 155 | 147 | 正常 |
| D-GOV-DRIFT | 147 | 4 | 🔴 路径极度集中（仅 4 前缀） |

### 6.2 需重新设计的域（路径集中度过高）

| 域 | 问题 | 重新设计方向 |
|----|------|------------|
| D-GOV-AUDIT | 171 节点仅 2 路径前缀 | 按审计子功能拆分路径：audit_trail/、audit_orchestration/、semantic_audit/ |
| D-GOV-DRIFT | 147 节点仅 4 路径前缀 | 按漂移类型拆分：config_drift/、concept_drift/、schema_drift/ |
| D-GOV-REPAIR | 241 节点仅 43 前缀 | 按修复阶段拆分：detection/、planning/、execution/、verification/ |
| D-GOV-DOCS | 207 节点仅 42 前缀 | 按文档类型拆分：policies/、standards/、blueprints/、runbooks/ |
| D-SECURITY | 350 节点仅 83 前缀 | 按安全子域拆分：access_control/、llm_defense/、adversarial/ |
| D-TEST | 2105 节点 | 按测试类型拆分：unit/、integration/、e2e/、adversarial/、performance/ |

### 6.3 域间依赖关系重新设计原则

| 原则 | 说明 |
|------|------|
| 单向依赖 | 按架构层 L0→L6 单向依赖，禁止反向 |
| 跨域违规检测 | arch_constraints 表记录所有跨域违规，逐项消除 |
| 域容量上限 | arch_domain_capacity 严格执行 max_modules，超限触发拆分 |
| 共享域隔离 | D-SHARED 只被依赖，不依赖业务域 |
| 治理域独立 | D-GOV-* 域不依赖业务域（D-TRADING/D-RISK 等） |

### 6.4 路径架构重新设计原则

| 原则 | 说明 |
|------|------|
| 一域一路径 | 每个 D-XXX 域有唯一 ssot_path 前缀，禁止多域共享 |
| 路径=域ID | ssot_path 末尾目录名机械推导 domain_id（如 `src/zephyr/trading/` → D-TRADING） |
| 子域子路径 | 域内子功能用子目录表达（如 `src/zephyr/governance/audit/`） |
| 蓝图路径机械推导 | blueprint_path = `docs/03_modules/{domain_id}/{module_name}/blueprint.md`（裁定 §12.1） |

---

## 七、施工步骤（建议）

> 按 RULE-TEN 治理施工流程 + 能力定位书 §22 因果链执行。

### 7.1 阶段一：数据清理（不动代码结构）

| 步骤 | 操作 | 验收 |
|:---:|------|------|
| 1 | 备份 depgraph.db | `data/databases/depgraph.db.backup.pre_rebuild` 存在 |
| 2 | 修复 sync 脚本 bug（方案 A：YAML 重构 + sync 不写 domains） | sync 脚本运行后 domains 表仍 52 行 |
| 3 | 删除 domains 表 9 个小写域 | `SELECT COUNT(*) FROM domains WHERE domain_id NOT LIKE 'D-%'` = 0 |
| 4 | 对齐 arch_domain_layers（补 D-GOV-DOCS/SCRIPTS/TEST，删 D-TRAE 或补 domains） | 三表域数一致 = 52 |
| 5 | 重新生成 depgraph + path_tree | 生成器 exit 0 |

### 7.2 阶段二：YAML 重构（functional_domain_registry.yaml）

| 步骤 | 操作 | 验收 |
|:---:|------|------|
| 6 | YAML 重构为 D-XXX 域的 subdomain 描述表（按 §5.2 映射） | 35 个 subdomain 全部归并到 D-XXX 域 |
| 7 | 修正 25 个不存在的 ssot_path（对齐实际项目结构） | 所有 ssot_path exists=True |
| 8 | sync 脚本改为写新表 domain_subdomains（不写 domains） | sync 运行后 domain_subdomains 有 35 行 |

### 7.3 阶段三：路径重复消除（涉及文件迁移，走 RULE-TEN）

| 步骤 | 操作 | 验收 |
|:---:|------|------|
| 9 | 依赖图推演：模拟 data/integration/signal 路径拆分 | 无新循环依赖 |
| 10 | 蓝图归属确认：3 处拆分域的蓝图 [BLUEPRINT] 字段 | 指向正确 domain_id |
| 11 | 导入路径映射：Grep 所有 import 语句 | 列出受影响 import 清单 |
| 12 | 执行路径拆分（原子事务） | 文件迁移完成 |
| 13 | 验证：depgraph + path_tree + audit_registration | 全部 exit 0 |

### 7.4 阶段四：路径集中度治理（可选，高成本）

| 步骤 | 操作 | 验收 |
|:---:|------|------|
| 14 | 对 D-GOV-AUDIT/D-GOV-DRIFT/D-TEST 等 6 个路径集中度过高域，按 §6.2 拆分子路径 | 路径前缀数提升 |
| 15 | 更新 arch_path_mappings | 路径映射与新结构一致 |

---

## 八、风险与回滚

| 风险 | 回滚方案 |
|------|---------|
| sync 脚本修改导致 domains 表数据丢失 | 阶段一前备份 depgraph.db，失败时 restore |
| 路径拆分导致 import 断裂 | 阶段三前生成 import 清单，失败时按清单回滚 |
| YAML 重构丢失 subdomain 信息 | 重构前 git commit，失败时 git checkout |
| 三表对齐操作误删有效域 | 操作前导出 domains/arch_domain_layers/capacity 全量，逐项核对 |

---

## 九、待 Owner 决策项

| # | 决策点 | 选项 | 建议 |
|---|--------|------|------|
| 1 | 小写域体系去留 | A. 废弃归并到 D-XXX（推荐）/ B. 保留并修复 sync | A |
| 2 | functional_domain_registry.yaml 重构方向 | A. 改为 D-XXX 子域描述（推荐）/ B. 保留结构修 sync | A |
| 3 | D-TRAE 域去留 | A. 补到 domains / B. 从 arch_domain_layers 删除 | 需确认 D-TRAE 是否有效域 |
| 4 | 路径拆分时机 | A. 本次一并做 / B. 数据清理后单独批次 | B（降低风险） |
| 5 | D-TEST 2105 节点拆分 | A. 按测试类型拆 / B. 保持现状 | A（但单独批次） |

---

## 十、附录：排查数据快照（2026-06-19）

### 10.1 数据库表清单（26 张）

`_schema_version`, `arch_bottlenecks`, `arch_constraints`, `arch_directory_tree`, `arch_domain_capacity`, `arch_domain_layers`, `arch_layers`, `arch_path_mappings`, `blueprint_links`, `business_streams`, `contracts`, `cross_registry_rules`, `domain_dependencies`, `domain_events`, `domains`, `edges`, `field_vocabularies`, `gates`, `hard_boundaries`, `infrastructure_components`, `invariants`, `model_capabilities`, `nodes`, `registries`, `rule_bindings`, `sqlite_sequence`

### 10.2 52 个 D-XXX 标准域清单

D-ALT_DATA, D-AUTONOMY_CORE, D-AUTONOMY_PERM, D-BACKTEST, D-COMPLIANCE, D-CROSS_ASSET, D-DATA_ENG, D-DATA_GOV, D-DATA_SEC, D-DIGITAL_TWIN, D-EXEC_SIM, D-EX_CORE, D-EX_SOR, D-FACTOR, D-FRONTEND, D-GOV-AUDIT, D-GOV-DOCS, D-GOV-DRIFT, D-GOV-ENFORCEMENT, D-GOV-REPAIR, D-GOV-SCRIPTS, D-GOV-SCRIPTS-ARCH, D-GOV-SCRIPTS-META, D-GOVERNANCE, D-INFRA_OPS, D-INFRA_RUNTIME, D-INTEGRATION, D-INTEGRATION-GATEWAY, D-INTELLIGENCE, D-KNOWLEDGE, D-MKT_DATA, D-ML_SERVE, D-ML_TRAIN, D-OPS, D-PF_ALLOC, D-PF_CORE, D-POSITION, D-REPORTING, D-RISK, D-SECURITY, D-SECURITY-LLM, D-SELL_DECISION, D-SHARED, D-SHARED-CONTRACTS, D-SIGNAL, D-SIGNAL_ASHARE, D-SIGNAL_FUNDAMENTAL, D-SIGNAL_QUALITY, D-SIMULATION, D-TEST, D-TRADING, D-TRADING-CONTRACTS

### 10.3 排查脚本

本次排查使用临时脚本（已删除）：
- `_query_domains.py` — domains 表统计
- `_audit_panorama.py` — 全面重复分析

---

> **下一步**：请 Owner 审阅本文档，确认 §九 待决策项后，按 §七 施工步骤建卡执行。
