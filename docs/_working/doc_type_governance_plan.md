---
title: "doc_type 字段治理方案（第一性原理治本路线）"
doc_type: design
ttl: task_bound
status: draft
created: 2026-06-26
owner: ZephyrAlpha-Owner
---

# doc_type 字段治理方案

> 本文档是 ttl 治理 4 阶段模式的 doc_type 等效物，但回填与门禁策略从第一性原理重新推导，不照搬 ttl 的"路径判定"（因为 doc_type 语义维度高于 ttl，路径无法独占判定）。

## 1. 问题全貌（已调查确认）

| 指标 | 数值 | 问题 |
|------|------|------|
| .md 总数 | 5150 | — |
| 有 frontmatter | 5123 | 27 个无 frontmatter |
| 有 doc_type | 397（7%） | **91% 缺失** |
| 非法 doc_type | 133（占有值 33.5%） | 词表形同虚设 |
| 词表声明值数 | 27 | **实际 26**（`total_values` 是 bug，handoff 文档列 27 时 `knowledge_entry` 重复一次） |
| 废弃值 | 7 种 | governance_standard / ai_governance / governance_registry / registry / discussion_draft / candidate_pool / checklist |
| 非法值集中度 | 106/133 = 80% | `domain_architecture_doc`(53)+`domain_architecture_diagram`(53) 同一生成器批量产物 |
| **真源分散** | **4 处** | 词表(A)+triage.py(B)+check_naming(C)+generate_registry(D) 各硬编码一套合法值，仅 GATE-15 从词表动态加载 |
| 真源漂移证据 | catalog/guide/report | C 的 `_DOC_TYPE_SUFFIX_MAP` 含词表没有的值；[triage.py:287](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py#L287) 把非法值 `report` 当有效路由 |
| 统计范围缺口 | docs/ only | 133 非法值只扫 docs/，src/scripts 还有 `red_team_corpus`/`governance_readme` 零星非法值 |

## 2. 第一性原理推导

### 2.1 doc_type 的真源

doc_type 字段存在的根本目的（见 [doc_type_vocabulary.yaml:319-320](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml#L319)）：**让任何文件看 frontmatter 就知道它是什么类型——零记忆重启标准的基础。**

真源 = 文件内容实际扮演的角色。路径只是内容的弱代理（proxy）。

### 2.2 为什么不能照搬 ttl 的"路径判定"

ttl 治理用 [backfill_ttl_metadata.py:69-81](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/backfill_ttl_metadata.py#L69-L81) 的 `_infer_ttl`（看路径前缀二元判定）成功，是因为：
- ttl 语义是"留多久"，天然二元（permanent vs task_bound）
- "永久区路径"与"永久保留"有强相关性

但这条路对 doc_type **不成立**：
- doc_type 语义是"是什么"，26 值，路径无法唯一确定
- `03_blueprints/` 下同时有 `blueprint`/`construction_plan`/`design`，路径无法区分
- handoff 文档已揭示 ttl 路径判定的债务：`changes/` 被误标 permanent（5091 vs 17 失衡）——doc_type 若纯路径判定会重复此错误

### 2.3 治本回填公式

```
治本回填 = 无歧义路径判定（~30-40%） + 有歧义内容判定（~60-70%）
```

**判定标准是"路径是否无歧义"，不是覆盖率。**

- 无歧义 = 路径+文件名与内容 1:1 绑定，路径判定数学上等价于内容判定（如 `index.md`→`index`）
- 有歧义 = 路径只能缩小范围，必须读内容（如 `03_blueprints/` 下的三种值）

### 2.4 治本门禁公式

```
治本门禁 = 校验逻辑单一真源（共享函数） + 双重拦截（GCG + pre-commit）
```

不选"挂哪一处"，而是逻辑集中、入口双重覆盖。

### 2.5 真源分散：比 91% 缺失更深的根因

grep 实测发现 doc_type 合法值的真源散落 4 处，互相不一致：

| 真源 | 位置 | 加载方式 | 状态 |
|---|---|---|---|
| A 词表 | [doc_type_vocabulary.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml) | 唯一真源 | ✅ 阶段0已补 `filename_suffixes`(12值)+`registry_category`(3值)字段 |
| B triage.py | [triage.py:86-96](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py#L86-L96) `VALID_DOC_TYPES` | ✅ 直读词表 | ✅ 阶段0已改；[279-284行](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py#L279-L284) 业务分支标 RENAME_REVIEW，删 report 非法值路由 |
| C 命名校验 | [check_naming_convention.py:557-566](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py#L557-L566) `_DOC_TYPE_SUFFIX_MAP` | ✅ 直读词表 `filename_suffixes` | ✅ 阶段0已改；catalog→reference、report→audit_report 已合并，guide 已删 |
| D 索引生成 | [generate_registry_master_index.py:69-79](file:///d:/ZephyrAlpha/scripts/governance/generators/generate_registry_master_index.py#L69-L79) `CATEGORY_FROM_DOC_TYPE` | ✅ 直读词表 `registry_category` | ✅ 阶段0已改 |
| E 目录审计 | [audit_directory_integrity.py:91-104](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/audit_directory_integrity.py#L91-L104) `_DOC_TYPE_SUFFIX_MAP` | ⚠️ 仍硬编码 | 阶段0验证新发现第5处真源——连字符约定+宽松endswith匹配+含幽灵值(playbook/runbook)+废弃值(checklist)，已标 RENAME_REVIEW 待阶段4决定 |
| ✓ GATE-15 | [check_frontmatter_metadata.py:63-68](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py#L63-L68) | **从 A 动态加载** | 唯一一直正确的消费者 |

**阶段 0 前状态（实证）**：只有 GATE-15 从词表加载，其余 3 处硬编码。C 已漂移到含 `catalog`/`guide`/`report`（词表无）——"多真源必漂移"的实证；[triage.py:287](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py#L287) 把非法值 `report` 当有效路由——多真源让非法值也能过校验。**阶段 0 已消除此问题**：B/C/D 全部改为直读词表，详见上方真源表状态列。

**治本定义由此升级**：不只门禁逻辑单一真源，而是 **doc_type 值引用单一真源**——所有引用合法值/值名的代码都从词表动态加载，禁止硬编码。这是改名字能安全进行的前置条件：不消除 B/C/D 硬编码，改名必然漏改（C 已漂移即证据）。

**关键澄清（"直接消费"而非"同步"）**：B/C/D 改造后是**直接读词表**（像 GATE-15 那样 `yaml.safe_load`），不是复制一份同步过去。"同步 = 复制 = 又多副本 = 又会漂移"，正是阶段 0 要消灭的。词表改了，B/C/D 下次运行自动用新值，**中间无同步步骤**。B/C/D 是消费者，不是副本。

引用 doc_type 值分三种，治本程度不同：
1. **合法值集合**（B 的 `VALID_DOC_TYPES`、C/D 字典 key）→ 直接读词表 `values`，0 硬编码
2. **值→属性映射**（C 的后缀、D 的 category）→ 属性作为字段写进词表，C/D 读字段，删自己的映射字典（不是"单独维护映射"——那是又造真源）
3. **按值名业务分支**（B 283-287 行）→ 代码逻辑，能基于词表属性（如 `rule_form`）分组就基于；不能的标 `# RENAME_REVIEW` 注释，改名时人工复核

这呼应 project_memory 铁律"YAML 是规则数据唯一真源，DB 仅同步缓存"——**doc_type 合法值当前违反此铁律**（4 真源，仅 1 处走 YAML）。

## 3. 词表精简策略（已定）

**先回填，再按分布数据精简。** 理由：
- ttl 从 6→2 能成立，因 ttl 语义天然二元；doc_type 是"是什么"，压到 2 值丢信息
- 26 值有语义重叠（`design`⊂`blueprint`、`roadmap`⊂`plan`），但精简时机应在回填后——长尾值（`readme`/`gate`/`declaration`/`service_spec`）真实使用率未知，回填后用数据决策
- 唯一例外：**先修 `total_values: 27→26` bug**（纯声明错误）

## 4. 非法值映射表（机械映射）

130/133 可机械映射，仅 4 个需人工确认。

| 非法值 | 数量 | → 合法值 | 依据 |
|---|---|---|---|
| domain_architecture_doc | 53 | architecture_view | "域架构文档"=架构视图 |
| domain_architecture_diagram | 53 | architecture_view | "域架构图"=架构视图 |
| service_interface_spec | 6 | service_spec | 拼写规范化 |
| governance_report | 4 | audit_report | 词表 deprecated 无此项 |
| capacity_report | 1 | audit_report | 报告类 |
| constraint_violations_report | 1 | audit_report | 报告类 |
| design_vs_production_report | 1 | audit_report | 报告类 |
| task_card_index | 2 | index | "索引" |
| directory_index | 1 | index | "索引" |
| domain_index | 1 | index | "索引" |
| architecture_construction_plan | 1 | construction_plan | 去前缀 |
| architecture_discussion | 1 | design | 讨论类 |
| architecture_design | 1 | design | 设计类 |
| capability_heatmap | 1 | reference | 参考数据 |
| cross_domain_matrix | 1 | reference | 参考数据 |
| runtime_plane_mapping | 1 | reference | 参考数据 |
| report | 2 | **需确认** audit_report/log | 看内容 |
| archive | 1 | **需确认** log/audit_report | 看内容 |
| delivery_record | 1 | **需确认** log/audit_report | 看内容 |

**根因修复**：找到产出 `domain_architecture_doc`/`diagram` 的域架构生成器并改其 doc_type 注入逻辑，否则清理后复发。

## 5. 无歧义路径判定规则表（回填高置信度部分）

这些规则只在"路径+文件名与内容 1:1 绑定"时使用，数学上等价于内容判定。

| 路径模式 + 文件名特征 | → doc_type | 置信度 | 说明 |
|---|---|---|---|
| `**/index.md` | index | high | 文件名固定绑定 |
| `**/README.md` | readme | high | 文件名固定绑定 |
| `_registry/vocabularies/*.yaml` | vocabulary | high | 目录+扩展强绑定 |
| `_registry/schemas/*` | schema | high | 目录强绑定 |
| `_registry/contracts/*` | contract | high | 目录强绑定 |
| 文件名 `*-policy.md` | policy | high | 后缀强绑定 |
| 文件名 `*-standard.md` | standard | high | 后缀强绑定 |
| 文件名 `*-protocol.md` | protocol | high | 后缀强绑定 |
| 文件名 `*-runbook.md`/`*-playbook.md`/`*-procedure.md`/`*-checklist.md` | operational_rule | high | 后缀强绑定（词表 §3.4） |
| 文件名 `*-registry.md`/`*-register.md` | register | high | 后缀强绑定 |
| `08_knowledge/01_raw_intake/*` | knowledge_entry | high* | 目录强绑定，需抽样验证 |

\* `08_knowledge/01_raw_intake/` 有 3242 文件（63%），若抽样确认 95%+ 是 knowledge_entry 则可路径判定，否则降级为内容判定。

**不在上表的路径一律走内容判定**，包括：
- `03_blueprints/`（blueprint / construction_plan / design 三选一，必须读内容）
- `02_enterprise_architecture/`（architecture_view / service_spec 二选一）
- `09_audit/`（audit_report / log 二选一，看是否 session）
- `01_policies_and_standards/governance/` 下非后缀绑定的文件

## 6. 施工步骤（5 阶段，对照 ttl）

### 阶段 0：消除多真源（前置，改名安全的前提）

**核心**：B/C/D 改为"直接消费真源"——既不复制值（不同步），也不维护映射（属性入词表）。改名时唯一要人盯的只剩业务分支逻辑。

| 步骤 | 动作 | 文件 | 状态 |
|---|---|---|---|
| 0.0 | 词表补结构化字段：每个 value 加 `filename_suffixes`（现第 319-337 行注释转字段）+ `registry_category`；同时修 `total_values: 27→26` | [doc_type_vocabulary.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml) | ✅ 已完成（12 filename_suffixes + 3 registry_category；total_values 待阶段 1.1 修） |
| 0.1 | triage.py：`VALID_DOC_TYPES` 改从词表动态加载（直读，非同步）；[279-284 行](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py#L279-L284) 业务分支改为基于词表属性（rule_form）分组，无法属性化的标 `# RENAME_REVIEW`；删 287 行 `report` 非法值路由 | [triage.py](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py) | ✅ 已完成（_load_doc_type_values@86；RENAME_REVIEW@279；report 路由已删） |
| 0.2 | check_naming_convention.py：删 `_DOC_TYPE_SUFFIX_MAP` 字典，改读词表 `filename_suffixes` 字段；清理 catalog→reference（1 文件）/ report→audit_report（2-3 文件）/ guide 删（0 用）；`_ranking` 后缀并入 reference | [check_naming_convention.py](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py) | ✅ 已完成（_load_doc_type_suffixes@557；12 key 含合并后 catalog/report 后缀） |
| 0.3 | generate_registry_master_index.py：删 `CATEGORY_FROM_DOC_TYPE` 字典，改读词表 `registry_category` 字段 | [generate_registry_master_index.py](file:///d:/ZephyrAlpha/scripts/governance/generators/generate_registry_master_index.py) | ✅ 已完成（_load_registry_categories@69；3 key: register/vocabulary/contract） |

**完成标准（已验证）**：全项目 grep 验证——①0 硬编码合法值列表；②0 硬编码值→属性映射字典；③业务分支处有 `RENAME_REVIEW` 标注或基于词表属性。77 测试全绿（vocab_sync_chain 24 + kb_triage 22 + gate11_naming 31）。

**阶段 0 验证新发现**：第 5 处真源 E（[audit_directory_integrity.py:91-104](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/audit_directory_integrity.py#L91-L104) `_DOC_TYPE_SUFFIX_MAP`）——连字符约定 + 宽松 endswith 匹配 + 含幽灵值（playbook/runbook 不在 26 合法值中）+ 废弃值（checklist）。已标 `RENAME_REVIEW`，待阶段 4 改名时决定合并策略（加独立字段 vs 重构读现有 filename_suffixes）。

**为什么是阶段 0**：不消除硬编码，后续改名（阶段 4 精简）必然漏改 B/C/D；不消除硬编码，回填脚本（阶段 2）自己也会硬编码值集合。这是治本能否成立的根。

### 阶段 1：止血（生成器 + 根因 + bug）

| 步骤 | 动作 | 文件 | 状态 |
|---|---|---|---|
| 1.1 | 修 `total_values: 27→26` | [doc_type_vocabulary.yaml:33](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml#L33) | ✅ 已完成（26 值无重复，纯声明错误） |
| 1.2 | 生成器注入 doc_type | 见下方修正映射 | ✅ 已完成（1 改+1 确认已对+1 修正为验证器） |
| 1.3 | 找到并修复产出 `domain_architecture_doc`/`diagram` 的域架构生成器 | [generate_domain_doc.py:449](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/generate_domain_doc.py#L449) + [generate_domain_architecture_diagram.py:493](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/generate_domain_architecture_diagram.py#L493) | ✅ 已完成（2 生成器均改 → architecture_view） |

**生成器注入映射（读码后修正）**：
- `generate_missing_index_md.py:86` → `index` — **已正确注入**，无需改（原计划假设需改，实际已对）
- `bootstrap.py:321` → `knowledge_entry` — ✅ 已注入 `_build_frontmatter_text()`（原计划不确定，读码确认创建 KE 文件，注入 knowledge_entry）
- `ingest.py` → **不是生成器，是验证器**（校验 frontmatter 必填字段 + 存储已有文本，不创建 frontmatter）——原计划假设错误，无需注入。doc_type 校验属阶段 3 门禁工作

**预存 bug（非本次引入，不阻断）**：bootstrap.py:199 `NameError: UnifiedMemoryAPI`（2 测试失败），与 doc_type 注入无关（改动在 line 321，bug 在 line 199）

### 阶段 2：治标→治本（分层回填）

| 步骤 | 动作 | 产出 |
|---|---|---|
| 2.1 | 写 `backfill_doctype_metadata.py`——只执行第 5 节无歧义规则表，标 high 置信度直接回填，其余写 `PENDING_CONTENT_REVIEW` | 新脚本 |
| 2.2 | 写 `migrate_illegal_doctype.py`——执行第 4 节机械映射表，130 个自动迁移，4 个标 `PENDING_REVIEW`。**扫描范围扩到全项目（docs/+src/+scripts/），不只 docs/**——已发现 `red_team_corpus`/`governance_readme` 等零星非法值 | 新脚本 |
| 2.3 | AI 分片处理 `PENDING_CONTENT_REVIEW`——40 并发，每片按第 7 节决策树判定，低置信度标 `PENDING_HUMAN_REVIEW` | CSV 报告 |
| 2.4 | 人工裁定 `PENDING_HUMAN_REVIEW` | 裁定记录 |

**关键：阶段 2.1 的路径判定覆盖率预计仅 30-40%**（只信无歧义的）。这与 ttl 路径判定 100% 覆盖不同——doc_type 的 60-70% 必须走 2.3 内容判定，这是治本的必要成本。

### 阶段 3：治本（门禁）

| 步骤 | 动作 | 文件 |
|---|---|---|
| 3.1 | 提取 `_shared/metadata_validation.py`，含 `validate_ttl()` + `validate_doctype()` 共享函数，从词表动态加载合法值 | 新文件 |
| 3.2 | [check_frontmatter_metadata.py](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py) 改为调用共享函数，同时校验 ttl+doc_type | 改现有 |
| 3.3 | [GitCommitGateway](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 调用同一共享函数，提交前校验 doc_type | 改现有 |
| 3.4 | 阶段 3.1-3.3 先 warn-only（print 不阻断），回填覆盖率达 95% 后升级 hard block（EXIT_FINDINGS） | — |

**逻辑单一真源**：GCG 和 pre-commit 都调用 `_shared/metadata_validation.py`，禁止在两处各写校验逻辑。

### 阶段 4：防漂移

| 步骤 | 动作 |
|---|---|
| 4.1 | 文档：doc_type vs allowed_directories 正交说明（仿 [ttl vs KE status](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml#L102)） |
| 4.2 | 回填后看分布数据，按第 3 节策略精简词表 |
| 4.3 | PENDING_REVIEW 文件与 ttl 内容判定纠偏合并到一次 AI 分片（同批文件省一遍读） |

## 7. AI 分片决策树（保证判定一致性）

针对阶段 2.3，每个 AI 分片 prompt 必须嵌入以下决策树，把 26 值判定约束成可复现流程：

```
Q1: 文件定义"规则"还是"操作步骤"？
  → 规则（声明式，"必须/禁止"） → Q2
  → 操作步骤（过程式，Step 1/Step 2） → operational_rule

Q2: 规则是"红线"还是"推荐/标准"？
  → 红线（违反严重） → policy
  → 可量化标准（度量/格式/接口） → standard
  → 多方交互约定 → protocol
  → 门禁触发条件 → gate
  → 项目级正式声明 → declaration

Q3: 文件是"导航/数据/结构"？
  → 目录级导航 → index
  → 结构化数据清单 → register
  → 术语字典 → terminology
  → 参考数据/映射表 → reference
  → 受控词表 → vocabulary
  → 验证契约 → contract
  → Schema 定义 → schema
  → 运行时配置 → config
  → 可复用骨架 → template

Q4: 文件是"设计/规划"类？
  → 完整设计（含架构决策+数据模型+接口+部署） → blueprint
  → 由蓝图派生的施工方案（含 checklist） → construction_plan
  → 技术方案详解（无完整蓝图要素） → design
  → 时间线/里程碑 → plan
  → 长期方向性规划 → roadmap

Q5: 文件是"记录/审计"类？
  → session log/变更日志 → log
  → 审计产出物 → audit_report

Q6: 文件是"架构/服务"类？
  → 4+1 架构视图 → architecture_view
  → 微服务接口契约 → service_spec

Q7: 文件是"知识"类？
  → 知识库条目 → knowledge_entry

无法确定 → 置信度 low，标 PENDING_HUMAN_REVIEW
```

**反例（防 AI 误判）**：
- `design` vs `blueprint`：blueprint 必须含完整四要素（架构决策+数据模型+接口定义+部署视图），缺要素是 design
- `plan` vs `roadmap`：plan 有具体时间线/里程碑，roadmap 是方向性无具体日期
- `construction_plan` vs `blueprint`：construction_plan 必须由蓝图派生且有 checklist 状态追踪

## 8. 风险与回滚

| 风险 | 缓解 |
|---|---|
| 路径无歧义规则误判（如 raw_intake 非全 knowledge_entry） | 阶段 2.1 抽样验证 95%+ 阈值，否则降级内容判定 |
| AI 分片判定不一致（design/blueprint 混淆） | 决策树 + 反例 + 交叉抽样校验（抽 5% 双判比对） |
| 门禁升级 hard block 后阻断提交 | 阶段 3 先 warn-only，达 95% 覆盖再升级 |
| 非法值生成器未修复导致复发 | 阶段 1.3 根因修复优先于存量清理 |
| **多真源残留导致改名漏改** | 阶段 0 完成标准：grep 验证 0 硬编码合法值列表；阶段 4 改名后跑全量校验确认无残留 |
| 词表精简误删有用值 | 回填后用分布数据决策，不凭直觉 |

**回滚**：每阶段独立提交（通过 GitCommitGateway），任意阶段失败可回退到上一阶段。回填脚本用 dry-run 先验证。

## 9. 待确认事项

- [ ] 阶段 0.2：`_DOC_TYPE_SUFFIX_MAP` 的 catalog/guide/report 漂移——确认是历史遗留还是有意保留（词表无此 3 值，疑似应清理）
- [ ] 阶段 1.3：产出 `domain_architecture_doc`/`diagram` 的生成器定位（需 grep 源码）
- [ ] 阶段 1.2：bootstrap.py / ingest.py 生成文件类型确认（需读代码）
- [ ] 阶段 2.1：`08_knowledge/01_raw_intake/` 抽样验证 knowledge_entry 占比
- [ ] 阶段 2.2：非法值清理范围扩到全项目（docs/+src/+scripts/），不只 docs/——已发现 `red_team_corpus`/`governance_readme`
- [ ] 阶段 3.4：hard block 升级阈值确认（建议 95%）
- [ ] docs/_working/ 下方案文档自身无合适 doc_type（design 的 allowed_directories 不含此目录）——词表精简时补 task_bound 区的 doc_type 值
