---
title: blueprint_id / 节点路径 命名一致性病根调研与裁定报告
doc_type: audit_report
status: active
ttl: task_bound
created_by: agent
created: '2026-06-25'
approved_by: owner
approved_date: '2026-06-25'
module_id: REG-GOV-NAMING-RCA-001
related_adjudication: '#206'
related_rename: '#204 D-SIGNAL* 4 域改名'
---

# blueprint_id / 节点路径 命名一致性病根调研与裁定报告

> **文档定位**：D-SIGNAL* 4 域改名（裁定#204）完成后，用户质疑"blueprint_id `MOD-SIGNAL_ASHARE` 等是否应为小写、是否应跟随改名"。本报告作为客观架构师调研，查清病根、对标社区、给出裁定与治本方案。
>
> **调研方法**：内部规则真源审计 + depgraph.db 量化探针 + 代码头部扫描 + 社区实践 WebSearch。所有结论附证据（文件:行号 / 来源 URL / 量化数据）。

---

## 1. 问题陈述

裁定#204 完成 D-SIGNAL* 4 域改名，仅改 depgraph.db 的 domain_id 列（16 列 488 行）。审查收尾时，4 类"残留"被原审查判为 out of scope：

| 残留类型 | 样本 | 原审查判定 |
|---|---|---|
| blueprint_id | `MOD-SIGNAL_ASHARE` | 蓝图ID命名，未纳入改名范围 |
| 节点路径 | `信号域-A股特色-主力资金/D-SIGNAL-21` | 路径片段，非 domain_id 字段值 |
| 文档历史引用 | 改名方案/调研报告中的"旧名→新名" | 合法历史记录 |
| 归档脚本 | `scripts/_archive/migration/*` | 已归档，非活跃代码 |

用户质疑前两类"应该是小写"，触发本次深度调研。核心问题：

> **Q1**：blueprint_id / module_id 的命名规则到底是什么？是否应为小写？
> **Q2**：domain_id 改名后，派生的 blueprint_id 和节点路径是否应跟随改名？
> **Q3**：原审查判 out of scope 是否正确？病根在哪？

---

## 2. 内部规则真源审计

### 2.1 命名规则真源定位

项目命名规则的**唯一真源**为 [trae_028_doc_structure_naming.yaml gov_doc_003_naming_ssot](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1022-L1074)（SSoT 声明，L1028-1031）。各标识符规则如下：

| 标识符 | 真源规定 | 证据 |
|---|---|---|
| **domain_id** | `D-XXX_YYY`（大写D+大写域缩写+下划线分隔子域）；示例 `D-MKT_DATA`/`D-ASHARE_SIGNAL` | [trae_028:1033-1035](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1033-L1035) + [domain_naming_rules.yaml NR-002](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/domain_naming_rules.yaml#L32-L39) |
| **module_id** | `MOD-{LAYER_CODE}-{SEQ}`（如 MOD-L00-001）或 `D-XXX-{SEQ}`（如 D-MKT_DATA-001）；Shared `SH-{ABBR}-{NNN}`；Frontend `FE-L{N}-{ABBR}-{NNN}` | [trae_028:1036-1039](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1036-L1039) |
| **文件名** | 全小写 snake_case；禁 kebab-case/大写（AGENTS.md 白名单除外） | [trae_028:1041-1043](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1041-L1043) |
| **目录名** | 单词或 snake_case（小写+下划线）；禁 kebab-case/大写/驼峰 | [trae_028:1045-1047](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1045-L1047) |
| **代码标识符** | 类 PascalCase；函数/变量 snake_case；常量 UPPER_SNAKE_CASE | [trae_028:1053-1055](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1053-L1055) |

**关键边界声明**（[trae_028:1064](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1064)）：

> "域ID保持大写 D-XXX_YYY 格式（**标识符不是文件名**）；统一使用下划线分隔子域（禁止连字符）"

→ **直接回答 Q1**：domain_id 大写是刻意设计，"标识符不是文件名"。文件名 snake_case 小写规则**不适用于** domain_id / module_id / blueprint_id。用户"应该是小写"的直觉源于文件名规则，但标识符层另有规则。

### 2.2 病根 #1：blueprint_id 规则真空

真源 [trae_028:1036-1039](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1036-L1039) 规定的是 **module_id** 格式（`MOD-{LAYER}-{SEQ}` 数字序号制）。但项目同时存在 **blueprint_id**（depgraph nodes.blueprint_id 列、blueprint.md frontmatter、blueprint_registry.yaml）。全文检索：

- **无任何规则文件显式定义 blueprint_id 的命名格式**
- blueprint_id 与 module_id 是否同体系、是否同命名空间——**未形式化**
- 派生关系（blueprint_id 的域片段是否来自 domain_id）——**未形式化**

blueprint_id 落入"既非文件名、又无独立规则、与 module_id 关系不明"的**规则真空**。

### 2.3 病根 #2：改名传播规则缺失

Grep `改名.*传播|传播.*改名|派生.*改名|rename.*propagat|派生标识|衍生ID` 于 docs/01_policies_and_standards/ → **0 匹配**。

项目**无任何规则**规定：当父标识符（domain_id）改名时，从它派生的子标识符（blueprint_id 域片段、节点路径域片段）是否必须同步改名。这是裁定#204 只改 domain_id 列、不传播派生标识符的**直接根因**。

### 2.4 病根 #3：执行缺口（enforcement gap）

[check_naming_convention.py:252-257](file:///D:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py#L252-L257) N-06 规则的正则：

```python
r"^\s*module_id:[ \t]*[\"']?(ADR|CP|KE|...|MOD|...|DM)(?:[-_][A-Za-z0-9_]+)+[\"']?"
```

只校验 module_id 有**合法 scope 前缀**（MOD/GOV/...），**不强制 `MOD-{LAYER}-{SEQ}` 数字序号格式**。因此 `MOD-SIGNAL_ASHARE`（大写下划线）、`MOD-GOV-git_commit_gateway`（混合描述名）**都能通过**门禁。真源规定的数字序号制**从未被自动化执行**。

### 2.5 病根 #4：规则溯源链断裂

[domain_naming_rules.yaml:31,39,47,55](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/domain_naming_rules.yaml#L31) 的 `source_doc` 字段引用 `docs/01_policies_and_standards/rules/trae_011_domain_attribution.yaml`——**该文件不存在**（实际存在的是 `trae_011_code_type_import.yaml`，无关）。AI 查规则溯源时找不到源文件 → 靠记忆/猜测 → 命名漂移。

### 2.6 病根 #5：module_id 现实与规则严重脱节

真源规定 module_id = `MOD-{LAYER}-{SEQ}` 数字序号制，但实测（见 §3.2）src/ 代码头部 2921 个 module_id 中**仅 1 个**符合数字序号制。规则与现状背离，使规则失去权威性，AI 无所适从。

---

## 3. 量化证据（depgraph.db + 代码探针）

探针脚本 `_tmp_naming_probe.py`（临时，调研后清理）实测结果：

### 3.1 blueprint_id 命名模式分布（nodes 表 6782 行）

| 命名模式 | 行数 | 占比 | 合规性 | 样本 |
|---|---|---|---|---|
| 数字序号制 `MOD-XX-NNN`（真源规定） | 4810 | 71% | ✅ 合规 | MOD-FEEDBACK_LOOP, MOD-INF-005 |
| 大写下划线 `MOD-XXX_YYY` | 897 | 13% | ❌ 违规（无序号） | MOD-SIGNAL_ASHARE, MOD-SECURITY, MOD-GOVERNANCE |
| 混合描述名 `MOD-XX-xxx_yyy` | 1 | <1% | ❌ 违规 | MOD-GOV-git_commit_gateway |
| 其他 | 1074 | 16% | ❓ 需细分 | — |

### 3.2 含旧域名片段的 blueprint_id（改名未传播）

| blueprint_id | 行数 | 派生自旧 domain_id |
|---|---|---|
| MOD-SIGNAL | 45 | D-SIGNAL → D-SIGLEGACY |
| MOD-SIGNAL_ASHARE | 27 | D-SIGNAL_ASHARE → D-ASHARE_SIGNAL |
| MOD-SIGNAL_QUALITY | 17 | D-SIGNAL_QUALITY → D-SIGQC |
| MOD-SIGNAL_FUNDAMENTAL | 6 | D-SIGNAL_FUNDAMENTAL → D-FUNDAMENTAL_SIGNAL |
| **合计** | **95** | **4 种** |

这 95 行 blueprint_id 的域片段仍为旧名，与已改名的 domain_id **语义脱钩**。

### 3.3 节点路径含 D-SIGNAL（改名未传播）

nodes.path 含 `D-SIGNAL` 的节点：**75 个**，按当前 domain_id 分组：

| 当前 domain_id（已改名） | 节点路径含 D-SIGNAL 数 |
|---|---|
| D-SIGLEGACY | 45 |
| D-ASHARE_SIGNAL | 20 |
| D-SIGQC | 10 |

样本：`[D-ASHARE_SIGNAL] 信号域-A股特色-主力资金/D-SIGNAL-21` —— domain_id 已是 D-ASHARE_SIGNAL，但路径里的节点ID片段仍是 `D-SIGNAL-21`，**逻辑归属与路径标识不一致**。

arch_directory_tree / arch_path_mappings：**0 残留**（已清理）。

### 3.4 src/ 代码头部 module_id 命名模式（2921 个）

| 模式 | 数量 | 样本 |
|---|---|---|
| 数字序号制 `MOD-XX-NNN`（真源规定） | **1** | MOD-INF-021 |
| 大写下划线 `MOD-XXX_YYY` | 19 | MOD-ALT_DATA, MOD-AUTONOMY_CORE |
| 混合描述名 | 1 | MOD-GOV-git_commit_gateway |
| 其他（多种混合格式） | ~2900 | MOD-UNK_xxx_yyy 等 |

**真源规定的数字序号制在 src/ 几乎不存在**（1/2921），印证病根 #5。

---

## 4. 社区实践对标

### 4.1 专业机构：标识符不可变 + 弃用窗口

**Kubernetes 弃用策略**（[kubernetes.io deprecation-policy](https://kubernetes.io/docs/reference/using-api/deprecation-policy/)）：

- **规则#1**：API 元素加入某版本后，**不可从该版本删除或大幅改行为**；只能通过递增 API 组版本来移除。
- **name vs UID 分离**：name 是资源 URL 中的客户端字符串（同 kind 内唯一，删除后可复用）；UID 是全集群唯一不可变标识。资源改名 = 新建 + 弃用旧，**非原地改名**。
- K8s name 命名：小写字母+数字+`-`/`.`（RFC 1123 DNS 子域）——**name 用小写**。

→ **启示**：业界区分"不可变 UID"与"可读 name"。本项目 domain_id 更接近"可读 name"（含语义、可改名），而非不可变 UID。

### 4.2 AI 编程社区：命名漂移是头号问题（与本场景高度相关）

**vahu.org 实践指南**（[Consistent Naming Conventions in AI-Generated Codebases](https://vahu.org/consistent-naming-conventions-in-ai-generated-codebases-a-practical-guide)）引用 2024-2025 多项调研：

| 数据 | 来源 | 与本场景对应 |
|---|---|---|
| **37%** AI 生成代码因命名不一致被审查拒绝 | ONSpace AI 2025 | blueprint_id 三种格式混用 |
| **34%** AI 辅助重构因"未更新所有重命名实例"而损坏 | GitLab 2025 调研 1200 团队 | **正是病根#2**：domain 改名未传播到 blueprint_id/路径 |
| **63%** AI 代码用泛化名（data/result/temp）vs 人类 22% | ONSpace AI 2024 | — |
| CLAUDE.md 显式规则使依从率 **94%** | Anthropic 推荐 | 对标本项目 AGENTS.md/规则真源 |
| pre-commit 自动化使命名违规降 **89%** | GitLab 2024 | 对标本项目 check_naming_convention.py（但执行有缺口） |

**FSE2025 ACM 论文**（[Beyond Functional Correctness](https://mingwei-liu.github.io/assets/pdf/FSE2025CodingStyle.pdf)）：建立 LLM 代码风格不一致分类法（24 类，5 维度），证实 LLM 与人类代码风格显著差异。

**EACL2026 论文**（code_transformed）：Python snake_case 函数名占比 2023Q1 40.7% → 2025Q3 49.8%，LLM 正在推动命名收敛——但**收敛前提是规则被机器可读地强制执行**。

### 4.3 项目自身对标（trae_028 gov_doc_normative_refs_028）

项目已声明对标：ISO 9001 §7.5.2（唯一标识）、K8s API Group Naming、ITIL SACM、**Unicode CID（ID 永不回收 append-only）**、PEP8、Google Monorepo。

→ Unicode CID append-only 原则支持"ID 不可变"，但项目 domain_id 实际可改名（裁定#204），说明项目**实际采用"可读 name 可改 + 弃用"混合模式**，未与 append-only 对齐。

### 4.4 业界共识 vs 分歧

| 议题 | 共识 | 分歧/本项目现状 |
|---|---|---|
| 标识符 ≠ 文件名，可不同大小写 | ✅ 普遍（K8s name 小写 vs UID；常量大写） | 本项目已声明但边界未在显眼处 |
| 不可变 UID + 可读 name 分离 | ✅ K8s/ITIL | 本项目未分离，domain_id 兼任两者 |
| 改名 = 新建+弃用，非原地改 | ✅ K8s | 本项目 domain_id 原地改（裁定#204） |
| 派生ID跟随父ID改名 | ⚠️ 分歧 | 数据库外键跟随；K8s 不跟随（不可变） |
| AI 场景规则须机器可读+自动执行 | ✅ 2025 社区 | 本项目有真源但执行缺口（病根#3） |

---

## 5. 裁定结果

### 5.1 回答三个核心问题

**Q1（是否应为小写）**：**否**。domain_id/module_id/blueprint_id 是**标识符**，不是文件名。真源 [trae_028:1064](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1064) 明确"标识符不是文件名"，domain_id 大写是刻意设计。用户"应该是小写"的直觉适用于文件名层，不适用于标识符层。**但** module_id 真源规定为 `MOD-{LAYER}-{SEQ}` 数字序号制，现状大量违规（病根#5）需另行治理。

**Q2（派生标识符是否应跟随改名）**：**应跟随，但需建立形式化派生规则 + 传播工具**。理由：
- blueprint_id `MOD-SIGNAL_ASHARE` 的 `SIGNAL_ASHARE` 片段**派生自** domain_id，是 module_id 体系的语义组成部分。不跟随改名 → ID 语义与实际 domain 脱钩 → AI 理解混乱（对应 GitLab 34% 重构损坏）。
- 节点路径 `D-SIGNAL-21` 的 `D-SIGNAL` 片段**派生自** domain_id，是节点逻辑归属标识。domain_id 已是 D-ASHARE_SIGNAL 但路径仍 D-SIGNAL-21 → 逻辑归属与路径不一致。
- K8s 不可变范式适用于"UID/纯序号ID"，不适用于"含语义的派生可读名"。本项目 blueprint_id/节点路径属后者。

**Q3（原审查 out of scope 是否正确）**：**部分不正确**。原审查将 blueprint_id 和节点路径判为 out of scope，是基于"规则真空"的默认放行，而非基于明确的架构裁定。病根是**改名传播规则缺失（病根#2）+ 派生关系未形式化**，使审查无据可依。

### 5.2 裁定 #206（已 Owner 拍板 2026-06-25）

| 裁定项 | 决定 | 依据 |
|---|---|---|
| **B-1** blueprint_id 跟随 domain_id 改名 | ✅ 采纳派生范式（已拍板） | 派生语义必须一致；AI 场景防漂移 |
| **B-2** 节点路径域片段跟随 domain_id 改名 | ✅ 采纳派生范式（已拍板） | 逻辑归属与路径一致 |
| **B-3** domain_id 保持大写 D-XXX_YYY | ✅ 维持现状 | 真源规定，标识符≠文件名 |
| **B-4** module_id 数字序号制现状治理 | ⏸ 另立议题（已拍板：立议题不本次施工） | 影响面大（2921处），独立裁定 |
| **B-5** 新增"改名传播规则"入真源 | ✅ 治本 | 填补病根#2 |
| **B-6** 新增"派生标识符关系表" | ✅ 治本 | 形式化派生，使传播可自动化 |
| **B-7** 修复 check_naming_convention.py 执行缺口 | ✅ 治本 | 填补病根#3 |
| **B-8** 修复 domain_naming_rules.yaml 失效 source_doc | ✅ 治本 | 填补病根#4 |
| **B-9** 节点路径改名编号策略 | ✅ 重新编号（已拍板） | 按域内顺序重新分配 D-XXX-01,-02...；编号规整；**需全量扫描所有引用仔细检查** |
| **B-10** 阶段 C 节点路径改名 | ✅ 本次执行（已拍板） | 消除 domain_id 与节点路径长期不一致 |

### 5.3 改名传播映射（B-1/B-2 具体值）

| 旧值 | 新值 | 影响范围 |
|---|---|---|
| MOD-SIGNAL_ASHARE | MOD-ASHARE_SIGNAL | 27 行 blueprint_id + 对应 blueprint.md frontmatter + module_registry.yaml |
| MOD-SIGNAL_FUNDAMENTAL | MOD-FUNDAMENTAL_SIGNAL | 6 行 |
| MOD-SIGNAL_QUALITY | MOD-SIGQC | 17 行 |
| MOD-SIGNAL | MOD-SIGLEGACY | 45 行 |
| 节点路径 `D-SIGNAL-NN` (D-ASHARE_SIGNAL 域) | `D-ASHARE_SIGNAL-01,-02...` **重新编号** | 20 个节点 |
| 节点路径 `D-SIGNAL-NN` (D-SIGQC 域) | `D-SIGQC-01,-02...` **重新编号** | 10 个节点 |
| 节点路径 `D-SIGNAL-NN` (D-SIGLEGACY 域) | `D-SIGLEGACY-01,-02...` **重新编号** | 45 个节点 |

> ⚠️ **节点路径改名风险（重新编号策略，B-9 已拍板）**：节点路径是 nodes.path 主键性字段，被 edges、contracts、migration_registry、arch_path_mappings 等多处引用。**重新编号**意味着旧路径→新路径无简单前缀替换关系（编号也变），必须：
> 1. **全量扫描**所有引用节点路径的表/文件（nodes.path / edges.source_node / edges.target_node / contracts.* / migration_registry.* / arch_path_mappings / 制品 yaml）
> 2. 建立**旧路径→新路径映射表**（含编号重映射）
> 3. 用 apply_depgraph.py 工具化批量更新，**禁止裸 SQL**
> 4. dry-run 验证后再执行
>
> 用户明确强调："需要全量扫描仔细检查"——重新编号比保编号改前缀风险更高，必须确保零遗漏。

---

## 6. 治本施工方案

### 6.1 分阶段施工（按风险递增）

#### 阶段 A：规则治本（低风险，先做）

| 步骤 | 内容 | 验证 |
|---|---|---|
| A1 | 修复 domain_naming_rules.yaml 4 处失效 source_doc → 指向 trae_028 gov_doc_003_naming_ssot | grep 无 `trae_011_domain_attribution` |
| A2 | 在 trae_028 gov_doc_003_naming_ssot 新增"派生标识符规则"section：定义 blueprint_id = `MOD-{DOMAIN_ID去掉D-前缀}` 形式化派生；定义节点路径域片段 = domain_id 去掉 D-前缀 | 规则 YAML 校验通过 |
| A3 | 在 trae_028 新增"改名传播规则"section：domain_id 改名时，派生 blueprint_id/节点路径必须同步；提供传播算法 | 规则入库 |
| A4 | 修复 check_naming_convention.py N-06：增加 blueprint_id/module_id 完整格式正则校验（区分数字序号制 vs 派生制） | 单测覆盖 |

#### 阶段 B：blueprint_id 改名传播（中风险）

| 步骤 | 内容 | 影响行 |
|---|---|---|
| B1 | apply_depgraph.py 新增 `--propagate-rename` 子命令：给定旧/新 domain_id，自动更新 nodes.blueprint_id | — |
| B2 | 执行 4 组传播（MOD-SIGNAL_ASHARE→MOD-ASHARE_SIGNAL 等） | 95 行 |
| B3 | 同步更新 blueprint.md frontmatter 的 blueprint_id 字段 | 4 个蓝图文件 |
| B4 | 同步更新 module_registry.yaml / blueprint_registry.yaml | 2 文件 |
| B5 | 重新生成 target_path_tree.yaml / project_entity_depgraph.yaml | 2 制品 |
| B6 | 循环审查（CIRCULAR_ACCEPTANCE_ROUNDS=2）至 0 残留 | 探针脚本 |

#### 阶段 C：节点路径改名传播（高风险，重新编号策略，本次执行）

| 步骤 | 内容 | 影响行 |
|---|---|---|
| C1 | **全量扫描**所有引用节点路径的表/字段（nodes.path / edges.source_node / edges.target_node / contracts.* / migration_registry.* / arch_path_mappings / 制品 yaml），输出影响清单 | — |
| C2 | 建立**旧路径→新路径映射表**（按域内顺序重新编号 D-XXX-01,-02...） | 75 节点 |
| C3 | apply_depgraph.py 扩展 `--propagate-rename` 支持节点路径**重新编号**更新（含 edges/contracts 引用同步） | 75 节点 |
| C4 | dry-run 确认影响范围 → 人工核对映射表 → 执行 | — |
| C5 | 重新生成所有引用节点路径的制品 | — |
| C6 | 循环审查（CIRCULAR_ACCEPTANCE_ROUNDS=2）至 0 残留 | 探针脚本 |

#### 阶段 D：module_id 数字序号制治理（独立议题，另行裁定）

不纳入本次裁定#206 范围，登记为议题 #ARCH-XXX。

### 6.2 防再发机制

1. **派生关系形式化**（B-6）：新建 `derived_identifier_registry.yaml`，记录每个派生标识符的父标识符 + 派生算法，使改名传播可自动计算。
2. **改名门禁**：apply_depgraph.py `--rename-domain` 执行后自动调用传播检查，未传播则阻断 COMPLETED。
3. **CI 巡检**：定期运行改名一致性探针（本报告 _tmp_naming_probe.py 固化为 governance 脚本）。
4. **AGENTS.md 显式声明**：在 AGENTS.md 增加"标识符层 vs 文件名层命名边界"段落，消除"应该是小写"类混淆。

### 6.3 回滚预案

- 阶段 A/B/C 每步前 `git commit` 备份 depgraph.db（项目铁律：改 depgraph 前必备份）
- 阶段 C 节点路径改名若引发引用断裂，通过 apply_depgraph.py `--diagnose`（已存在）检测孤儿边，回滚至备份

---

## 7. Owner 决策记录（2026-06-25 拍板）

本报告已由 Owner 拍板（status: draft → active），决策如下：

1. **裁定#206 B-1/B-2 派生范式**：✅ **采纳派生范式**（blueprint_id/节点路径跟随 domain_id 改名）。
2. **节点路径改名编号策略**：✅ **重新编号**（D-ASHARE_SIGNAL-01,-02... 按域内顺序重新分配）。Owner 强调"**需要全量扫描仔细检查**"——重新编号风险高于保编号改前缀，施工时必须全量扫描所有引用并人工核对映射表。
3. **module_id 数字序号制治理**：✅ **立议题但不在本次施工**（登记为 #ARCH-XXX，独立裁定）。
4. **阶段 C 节点路径改名**：✅ **本次执行**（消除 domain_id 与节点路径长期不一致）。

→ 施工按 §6 阶段 A→B→C 顺序执行，阶段 D 另立议题。

---

## 附录 A：证据索引

| 编号 | 证据 | 位置 |
|---|---|---|
| E1 | 命名规则 SSoT 声明 | trae_028:1022-1074 |
| E2 | domain_id 大写规则 | trae_028:1033-1035 + domain_naming_rules.yaml NR-002 |
| E3 | module_id 数字序号制规定 | trae_028:1036-1039 |
| E4 | "标识符不是文件名"边界 | trae_028:1064 |
| E5 | blueprint_id 规则真空 | 全文检索 0 匹配 blueprint_id 命名格式规则 |
| E6 | 改名传播规则缺失 | grep 0 匹配 |
| E7 | N-06 执行缺口 | check_naming_convention.py:252-257 |
| E8 | source_doc 溯源断裂 | domain_naming_rules.yaml:31,39,47,55 |
| E9 | blueprint_id 量化分布 | _tmp_naming_probe.py §1（6782行） |
| E10 | 旧域名片段残留 | _tmp_naming_probe.py §2（95行） |
| E11 | 节点路径残留 | _tmp_naming_probe.py §4（75节点） |
| E12 | module_id 现状脱节 | _tmp_naming_probe.py §6（1/2921） |
| E13 | K8s 弃用策略 | https://kubernetes.io/docs/reference/using-api/deprecation-policy/ |
| E14 | AI 命名漂移 34% 重构损坏 | https://vahu.org/consistent-naming-conventions-in-ai-generated-codebases-a-practical-guide |
| E15 | LLM 代码风格不一致分类法 | https://mingwei-liu.github.io/assets/pdf/FSE2025CodingStyle.pdf |
