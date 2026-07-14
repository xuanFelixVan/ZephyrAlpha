# D_GOVERNANCE + D_TRADING 域拆分方案

> **方案状态**：待审批
> **创建日期**：2026-07-12
> **创建者**：session-20260712
> **关联债务**：architecture_debt_registry.md §5.176.2（D_GOVERNANCE 超限）、#ARCH-052（D_TRADING 超限）

---

## 1. 背景与调研结果

### 1.1 ARCH-CAP-002 违规现状

ARCH-CAP-002 v1.0.8 规定：单域 production_nodes ≤150 通过，>150 必须拆分，无例外。

| 域 | domain_name | production 节点 | 超限倍数 | 违规登记 |
|---|---|---|---|---|
| D_GOVERNANCE | registry_management | 506 | 3.37x | V-HARD150-D_GOVERNANCE |
| D_TRADING | 交易运营 | 280 | 1.87x | V-HARD150-D_TRADING |

### 1.2 D_GOVERNANCE 调研结果

**业务职责**：ZephyrAlpha 的"Agent 治理八件套"——身份验证(RBAC)、权限执行、操作审计、异常回滚、升级委托、漂移检测、预算控制、多 Agent 协调。同时管注册表总索引。

**超限原因**：
1. **拆分半途而废**（主因）：domains 表已建 6 个拆分域（D_GOV_AUDIT/D_GOV_DRIFT/D_GOV_ENFORCEMENT 等），但仅 2 个完成节点迁移，4 个是空壳
2. **src/zephyr/governance/ 包本身过大**：403 production 节点，单独超限 2.7x
3. **docs/01_policies_and_standards/ 被错误归入**：64 个规则文档节点被聚合进来

**现有空壳域**：

| 拆分域 | domains 表 | nodes 表实际 | D_GOVERNANCE 中应迁 subdomain | 应迁 production |
|---|---|---|---|---|
| D_GOV_AUDIT | ✅ | 2（空壳） | D_GOVERNANCE-AUDIT_TRAIL | 56 |
| D_GOV_DRIFT | ✅ | 1（空壳） | D_GOVERNANCE-DRIFT_DETECTION | 56 |
| D_GOV_ENFORCEMENT | ✅ | 82（已迁部分） | D_GOVERNANCE-RULE_ENFORCEMENT | 62 |
| D_GOV_KB | ❌ 不存在 | — | D_GOVERNANCE-KB | 22 |
| D_GOV_SCRIPTS | ✅ | 440（已迁） | D_GOVERNANCE-SCRIPT_GOVERNANCE | 4 |

### 1.3 D_TRADING 调研结果

**业务职责**：名义上是量化交易系统的交易执行中枢。但 `src/zephyr/trading/` 目录被当成"杂物间"，塞入了 4 个本应独立的子系统。

**超限原因**：feedback_loop(336节点) 和 orchestrator(74节点) 是跨层基础设施子系统，被错误地物理放在 `src/zephyr/trading/` 目录下，depgraph 按路径前缀归入 D_TRADING。

| 子系统 | 节点数 | production | 蓝图标注 | 该不该属于"交易运营" |
|---|---|---|---|---|
| Feedback Loop Engine | 336 | 177 | layer: L1_foundation, functional_domain: operations | ❌ |
| Agent Orchestrator | 74 | 60 | cross_layer | ❌ |
| Auto Runtime Core | 29 | ~20 | cross_layer | ❌ |
| 真正的交易运营 | ~42 | ~30 | L2_domain | ✅ |

---

## 2. 拆分策略

### 2.1 原则：先 depgraph 映射后物理迁移

- **第一阶段（本次）**：仅改 depgraph 中节点的 domain_id + 同步所有引用（代码表头、蓝图、注册表等）。不移动代码物理路径。
- **第二阶段（后续专项）**：物理迁移代码目录（如 `src/zephyr/feedback_loop/` → `src/zephyr/feedback_loop/`），修改 import 路径。

### 2.2 域边界划分规则

1. 按 blueprint_id 划分：同一 blueprint 的节点归入同一域
2. 按 subdomain_id 划分：已有 subdomain_id 的节点按其归属迁移
3. 按 path 前缀划分：无 subdomain_id 的节点按代码目录前缀迁移
4. 新建域必须有完整的域定义（domains 表 + architecture_model/index.yaml + functional_domain_registry + domain_name_mapping + target_layer_vocabulary）

---

## 3. D_GOVERNANCE 拆分方案

### 3.1 第一步：新建 D_GOV_KB 域定义

D_GOV_KB 在所有注册表中都不存在，需新建 4 处定义：
1. depgraph DB `domains` 表 INSERT
2. `architecture_model/index.yaml` 新增域定义
3. `functional_domain_registry.yaml` 新增条目
4. `domain_name_mapping.py` 新增中/英文名映射
5. `target_layer_vocabulary.yaml` 新增词表条目

### 3.2 第二步：完成空壳域节点迁移（depgraph SQL UPDATE）

| 操作 | subdomain_id | 迁移 production | 目标域 | 目标域现状 |
|---|---|---|---|---|
| 1 | D_GOVERNANCE-AUDIT_TRAIL | 56 | D_GOV_AUDIT | 空壳(2节点) |
| 2 | D_GOVERNANCE-DRIFT_DETECTION | 56 | D_GOV_DRIFT | 空壳(1节点) |
| 3 | D_GOVERNANCE-RULE_ENFORCEMENT | 62 | D_GOV_ENFORCEMENT | 已有82节点 |
| 4 | D_GOVERNANCE-KB | 22 | D_GOV_KB（新建） | 不存在 |
| 5 | D_GOVERNANCE-SCRIPT_GOVERNANCE | 4 | D_GOV_SCRIPTS | 已有440节点 |

**预期效果**：506 - 200 = ~306 production 节点（仍超限，需二期）

### 3.3 第三步：同步代码表头（53 个 src/ 文件）

| 子目录 | 文件数 | 迁移目标域 |
|---|---|---|
| commit_gates/ | 22 | D_GOV_ENFORCEMENT |
| kb/（含 pipeline/、storage/） | 14 | D_GOV_KB |
| rule_enforcement/（含 rule_engine/） | 6 | D_GOV_ENFORCEMENT |
| rule_bridge/ | 4 | D_GOV_ENFORCEMENT |
| semantic_audit/ | 3 | D_GOV_AUDIT |
| audit_trail/ + audit/ | 2 | D_GOV_AUDIT |
| drift_detector_core/ | 1 | D_GOV_DRIFT |
| behavioral_admission/ | 1 | D_GOV_ENFORCEMENT |

### 3.4 第四步：同步脚本表头（~100 个 scripts/ 文件）

全部 `# [DOMAIN] D_GOVERNANCE` 表头，需逐个判断迁移目标。

### 3.5 第五步：同步测试文件（22 个）

- 19 个表头更新
- 3 个含逻辑断言的测试需特别处理：
  - `test_depgraph_generator_design_protection.py` L27: `_TEST_DOMAIN = "D_GOVERNANCE"`
  - `test_align_panoramas.py` L449: 测试 fixture
  - `test_depgraph_schema.py` L449: 测试数据 frontmatter

### 3.6 第六步：同步文档和注册表

- AGENTS.md L132 域归属描述
- functional_domain_registry.yaml D_GOVERNANCE 条目调整
- architecture_issue_registry.yaml 超容问题状态更新
- domain_name_mapping.py 新增 D_GOV_KB
- architecture_model/index.yaml 新增 D_GOV_KB
- target_layer_vocabulary.yaml 新增 D_GOV_KB

### 3.7 二期（后续专项，不在本次范围）

src/zephyr/governance/ 包按"八件套"拆分，目标 D_GOVERNANCE 核心降至 ≤60 节点。

---

## 4. D_TRADING 拆分方案

### 4.1 第一步：新建域定义

| 新域 | domain_id | domain_name | ssot_path | blueprint_id |
|---|---|---|---|---|
| 反馈循环引擎 | D_FEEDBACK_LOOP | feedback_loop_engine | src/zephyr/feedback_loop/ | MOD-FEEDBACK_LOOP |
| 代理编排器 | D_ORCHESTRATOR | agent_orchestrator | src/zephyr/orchestrator/ | MOD-INF-039 |

每域需新建 5 处定义（同 D_GOV_KB）。

### 4.2 第二步：节点迁移（depgraph SQL UPDATE by path prefix）

| 操作 | 迁移条件 | 节点数 | production | 目标域 |
|---|---|---|---|---|
| 1 | path LIKE 'src/zephyr/feedback_loop/%' | 336 | 177 | D_FEEDBACK_LOOP |
| 2 | path LIKE 'src/zephyr/orchestrator/%' | 74 | 60 | D_ORCHESTRATOR |

**预期效果**：D_TRADING 降至 ~43 production（合规）。D_FEEDBACK_LOOP = 177（仍超限，需二期二分）。

### 4.3 第三步：同步代码表头（175 个文件）

| 代码目录 | 文件数 | 当前表头 | 新表头 |
|---|---|---|---|
| src/zephyr/feedback_loop/ | 100 | 多为 D_OPS | D_FEEDBACK_LOOP |
| src/zephyr/orchestrator/ | 75 | 多为 D_INFRA_RUNTIME | D_ORCHESTRATOR |

### 4.4 第四步：同步蓝图和文档

- 2 个蓝图 responsibility_domain 字段填入
- 8 个手动维护的架构文档审查
- target_layer_vocabulary.yaml 新增 2 域
- architecture_issue_registry.yaml #ARCH-052 更新
- domain_name_mapping.py 新增 2 域
- sync_yaml_to_depgraph.py 硬编码映射审查
- generate_capability_heatmap.py 硬编码域列表审查

### 4.5 二期（后续专项）

- D_FEEDBACK_LOOP 内部二分：D_FLE_DETECT(141) + D_FLE_CORE(195)
- 物理代码迁移：feedback_loop/ 和 orchestrator/ 移出 trading/ 目录

---

## 5. 影响面全量清单

### 5.1 D_GOVERNANCE（181 个文件需手动修改）

| 类别 | 文件数 | 说明 |
|---|---|---|
| 代码表头（src/） | 53 | commit_gates(22) + kb(14) + rule_enforcement(6) + rule_bridge(4) + audit(5) + drift(1) + behavioral(1) |
| 脚本表头（scripts/） | ~100 | 需逐个判断迁移目标 |
| 测试文件（tests/） | 22 | 19 表头 + 3 逻辑断言 |
| 蓝图文件 | 1 | panorama_alignment_engine frontmatter |
| AGENTS.md | 1 | L132 |
| 注册表 | 2 | functional_domain_registry + architecture_issue_registry |
| domain_name_mapping.py | 1 | 新增 D_GOV_KB |
| architecture_model/index.yaml | 1 | 新增 D_GOV_KB |
| target_layer_vocabulary.yaml | 1 | 新增 D_GOV_KB |

### 5.2 D_TRADING（~195 个文件需手动修改）

| 类别 | 文件数 | 说明 |
|---|---|---|
| feedback_loop 代码表头 | 100 | 当前多为 D_OPS |
| orchestrator 代码表头 | 75 | 当前多为 D_INFRA_RUNTIME |
| trading 根目录表头 | 3 | orchestrator 下 3 个文件 |
| 蓝图文件 | 2 | responsibility_domain 填入 |
| 架构文档 | ~8 | target_architecture/ 手动维护 |
| 词表 | 1 | target_layer_vocabulary.yaml |
| 注册表 | 1 | architecture_issue_registry #ARCH-052 |
| domain_name_mapping.py | 1 | 新增 2 域 |
| 测试 | 1 | test_align_panoramas.py |
| 脚本 | ~3 | sync_yaml_to_depgraph + generate_capability_heatmap |

### 5.3 自动同步（reconciler 自动处理）

| 同步项 | 数量 | 机制 |
|---|---|---|
| 架构文档（generated/） | 77+66 | depgraph 变更后生成器自动重生 |
| 蓝图 frontmatter | — | blueprint_frontmatter_reconciler 自动同步 |
| path_ownership_map.yaml | 1 | 自动重新生成 |
| arch_directory_tree | — | 自动同步 |
| rule_catalog_registry | — | 自动重新对账 |
| rules_integrity baseline | — | 自动重新注册 |

---

## 6. 任务卡清单

### 6.1 总卡（2张）

| task_id | title | namespace | priority | phase | depends_on |
|---|---|---|---|---|---|
| OPS-2026071201 | D_GOVERNANCE 域拆分总卡（depgraph映射阶段） | OPS | P1 | 1 | - |
| OPS-2026071202 | D_TRADING 域拆分总卡（depgraph映射阶段） | OPS | P1 | 2 | OPS-2026071201 |

### 6.2 子卡（13张）

| task_id | title | depends_on | 操作摘要 |
|---|---|---|---|
| **D_GOVERNANCE 阶段** | | | |
| OPS-2026071203 | 新建 D_GOV_KB 域定义（5处） | OPS-2026071201 | domains表INSERT + index.yaml + functional_domain_registry + domain_name_mapping + target_layer_vocabulary |
| OPS-2026071204 | 迁移 D_GOV depgraph 节点（5批SQL UPDATE） | OPS-2026071203 | AUDIT_TRAIL→D_GOV_AUDIT + DRIFT→D_GOV_DRIFT + RULE_ENFORCEMENT→D_GOV_ENFORCEMENT + KB→D_GOV_KB + SCRIPT_GOVERNANCE→D_GOV_SCRIPTS |
| OPS-2026071205 | 同步 D_GOV 代码表头（53个src/文件） | OPS-2026071204 | 批量替换 # [DOMAIN] |
| OPS-2026071206 | 同步 D_GOV 脚本表头（~100个scripts/文件） | OPS-2026071204 | 逐个判断+批量替换 |
| OPS-2026071207 | 同步 D_GOV 测试+文档+注册表（25个文件） | OPS-2026071204 | 22测试 + AGENTS.md + 2注册表 + domain_name_mapping + index.yaml + target_layer_vocabulary |
| OPS-2026071208 | D_GOV 验证：重生成depgraph + ARCH-CAP-002检查 | 05,06,07 | generate_project_depgraph + 查询验证 + reconciler全clean |
| OPS-2026071209 | D_GOV 循环验证：全项目扫描遗漏+修复至问题=0 | OPS-2026071208 | 连续2轮全项目扫描0遗漏 |
| **D_TRADING 阶段** | | | |
| OPS-2026071210 | 新建 D_FEEDBACK_LOOP + D_ORCHESTRATOR 域定义 | OPS-2026071202 | 2域×5处定义 |
| OPS-2026071211 | 迁移 D_TRADING depgraph 节点（2批SQL UPDATE） | OPS-2026071210 | feedback_loop→D_FEEDBACK_LOOP + orchestrator→D_ORCHESTRATOR |
| OPS-2026071212 | 同步 D_TRADING 代码表头（175个文件） | OPS-2026071211 | feedback_loop(100) + orchestrator(75) |
| OPS-2026071213 | 同步 D_TRADING 蓝图+文档+注册表（~15个文件） | OPS-2026071211 | 2蓝图 + 8架构文档 + 词表 + 注册表 + domain_name_mapping + 测试 + 脚本 |
| OPS-2026071214 | D_TRADING 验证：重生成depgraph + ARCH-CAP-002检查 | 12,13 | generate_project_depgraph + 查询验证 + reconciler全clean |
| OPS-2026071215 | D_TRADING 循环验证：全项目扫描遗漏+修复至问题=0 | OPS-2026071214 | 连续2轮全项目扫描0遗漏 |

### 6.3 执行顺序

```
Phase 1 (D_GOV):
  03(建域) → 04(迁移节点) → 05(代码表头) → 06(脚本表头) → 07(测试+文档) → 08(验证) → 09(循环验证)

Phase 2 (D_TRADING):
  10(建域) → 11(迁移节点) → 12(代码表头) → 13(蓝图+文档) → 14(验证) → 15(循环验证)
```

### 6.4 循环验证标准（OPS-2026071209 / OPS-2026071215）

每轮验证执行：
1. 全项目 Grep 扫描 D_GOVERNANCE / D_TRADING 在 src/、scripts/、tests/、docs/ 下的残留引用
2. 检查代码表头与 depgraph domain_id 一致性
3. 检查蓝图 frontmatter 与 depgraph 一致性
4. 检查注册表/词表与 depgraph 一致性
5. 运行 check_blueprint_code_alignment.py
6. 运行 verify_schema_health.py

**通过标准**：连续 2 轮扫描均 0 遗漏。若某轮发现问题，修复后重新计数。

---

## 7. 回滚方案

### 7.1 depgraph 节点迁移回滚

```sql
-- D_GOVERNANCE 回滚
UPDATE nodes SET domain_id = 'D_GOVERNANCE'
WHERE domain_id IN ('D_GOV_AUDIT', 'D_GOV_DRIFT', 'D_GOV_ENFORCEMENT', 'D_GOV_KB', 'D_GOV_SCRIPTS')
AND subdomain_id LIKE 'D_GOVERNANCE-%';

-- D_TRADING 回滚
UPDATE nodes SET domain_id = 'D_TRADING'
WHERE domain_id IN ('D_FEEDBACK_LOOP', 'D_ORCHESTRATOR');
```

### 7.2 新建域回滚

```sql
DELETE FROM domains WHERE domain_id IN ('D_GOV_KB', 'D_FEEDBACK_LOOP', 'D_ORCHESTRATOR');
```

### 7.3 文件变更回滚

```bash
git checkout -- src/ scripts/ tests/ docs/ AGENTS.md
```

---

## 8. 已知遗留（二期专项）

| 遗留项 | 说明 | 预期专项 |
|---|---|---|
| D_GOVERNANCE 仍超限 | 迁移后 ~306 production 节点，仍 >150 | src/zephyr/governance/ 包按八件套拆分 |
| D_FEEDBACK_LOOP 仍超限 | 177 production 节点 >150 | 内部二分：D_FLE_DETECT + D_FLE_CORE |
| 代码物理路径未迁移 | feedback_loop/orchestrator 仍在 trading/ 目录下 | 物理迁移 + import 路径修改 |
| 裁定#200 修正 | dependency_path_panorama.md 声称拆分完成但实际未完成 | 更新裁定记录 |
