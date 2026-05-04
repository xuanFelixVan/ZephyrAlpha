# ZephyrAlpha 项目 AI 基准文件

> **版本**：v4.17.0 | 更新日期：2026-05-04 | 状态：Active
>
> **首要受众：AI** | 强制原则：§6.12 AI-First Audience Principle | 每次操作前自检：这个输出 AI 能零推理消费吗？

---

## 1. 项目根目录

所有活跃开发在项目根目录 `D:\ZephyrAlpha\` 下进行。

- **路径标准**：`docs/01_policies_and_standards/governance/document/directory-structure-standard.md`
- **规则注册表**：`docs/01_policies_and_standards/_registry/catalogs/document-metadata-index.yaml`（auto-generated，取代旧 governance-rules-master-registry.yaml 和 master-document-inventory.yaml）
- **文档清单**：`docs/01_policies_and_standards/_registry/catalogs/document-metadata-index.yaml`（已合并至规则注册表，旧 master-document-inventory.yaml 已于 2026-05-02 废弃）
- **登记表总索引**：`docs/01_policies_and_standards/_registry/catalogs/registry-master-index.yaml`
- **审计执行协议**：`docs/01_policies_and_standards/governance/compliance/audit-protocol.md`（**GOV-CMP-003——任何审计任务的唯一入口：审什么/用什么审/怎么审/审到什么程度**）

> **路径 SSoT 声明**：以上**五条**路径是项目核心文档路径的唯一真源（SSoT）。README.md、CONTRIBUTING.md 等其他文件如需引用核心文档位置，以本文件为准——禁止在其他地方独立硬编码同样的路径。对标 §6.4 最有利于 AI 施工的选择——单一责任优于分散定义。

## 2. 旧树已归档

旧树（Phase 0~2 早期）已物理归档到 `_DO_NOT_USE_old_tree/`。

**禁止使用 `_DO_NOT_USE_old_tree/` 下的任何文件作为规则来源或操作目标。**

## 3. 旧版 AGENTS.md（历史遗留）

旧树 `_DO_NOT_USE_old_tree/AGENTS.md` 含 18 章节完整版，其中 92 处路径已失效。**不作为当前规则来源**，待新规则体系定稿后统一重写。

## 4. 编码安全（唯一始终生效的硬规则）

> **SSoT 声明**：前两条编码安全规则的 canonical SSoT 为 [GOV-DOC-005 encoding-safety-standard.md](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/governance/document/encoding-safety-standard.md)。以下为关键摘要——若发现不一致，以 GOV-DOC-005 为准。

- 禁止用 PowerShell `echo`/`Out-File` 默认参数写 `.md` 文件（SSoT: GOV-DOC-005 §二.3）
- Python 写文件必须指定 `encoding='utf-8'`（SSoT: GOV-DOC-005 §二.2）
- 禁止在 Cursor 和 Trae 中同时打开同一文件编辑
- 扫描器/校验脚本产生异常大量错误报告时，必须先暂停并检查扫描器本身——可能是正则表达式或校验逻辑写错了，而非文件真的有问题（KE-001 教训：3587 个误报源于一个多余的反斜杠）
- **源码-测试同步铁律**（Source-Test Sync Rule）：任何对 `src/zephyr/` 下源码的修改（包括但不限于：重命名类/函数/变量、变更函数签名、修改返回值类型、重组目录结构、变更数据模型/Schema/字段默认值），必须在**同一 session 内**完成以下三件事：①同步更新所有受影响的测试文件 ②跑通全量测试 `python -m pytest tests/ -q` ③确认零失败。禁止"先把源码改了，测试以后再说"——不存在"以后"，必须一步到位。对标 ITIL Change Enablement：源码修改 = 变更请求，测试通过 = 变更影响评估通过；评估不通过不得视为变更完成。Pre-commit GATE-18 为自动化执行层——提交时自动拦截收集失败的代码（ImportError / 路径漂移 / 模块缺失）。
- **大白话**：改源码的时候必须同时改测试，改完立刻跑一遍确认全绿。不要"先改源码，测试以后补"——跟借高利贷一样，拖越久利息越高，最后要花 10 倍时间还债。改代码和修测试是连体婴儿——必须生在一起，不能分开。

## 5. Owner 画像与沟通协议

Owner 为编程初学者（非技术背景），所有 AI 输出必须遵循**专业术语 + 大白话双轨解释**协议。

- **术语不删，解释跟上**（Terminology-Preserving Dual-Track）：专业术语必须保留——Owner 需要逐步建立技术词汇量。每个术语首次出现或关键段落之后，必须紧跟大白话解释（用"也就是说…"或"大白话：…"引出）。解释不能缩水原意，但必须用 Owner 能懂的语言
- **学习不挡路**（Learning Non-Blocking）：方案的复杂度按专业标准设计，不因 Owner 是初学者而简化。解释到位就行，不因"Owner 可能需要时间理解"而降级架构。Owner 的学习曲线由双轨解释承载，不由方案简化承载
- **输出结构**：每次需要 Owner 决策时，遵循"结论（1 句话）→ 专业论证（引用标准/框架）→ 大白话（"翻译成大白话就是…"）→ 可选项（如果有多个方案的明确对比）"

### 5.1 Vibe Coding AI 的认知特征

本项目 **100% 采用 Vibe Coding AI** 进行开发。Vibe Coding AI 的核心特征是**上下文记忆极短**——类似于一个不断快速入职又离职的员工：每次新 session 来临，AI 对它不在这段上下文窗口中的一切毫无记忆。

这意味着项目中的所有文件、路径、规则、代码、命名，必须满足一个**零记忆重启标准**（Zero-Memory Restart Standard）：任何一个全新的 AI session，仅凭读取当前项目文件，就能在无外部提示的情况下准确理解项目结构并开始正确施工。

- **原则 1：二元化**（Binary-Safe）——没有"大概"、"应该"。每个定义是精确的枚举值或条件。受控词表必须完整列出合法值，不存在"等等"或"类似"
- **原则 2：责任唯一**（Single Responsibility）——同一概念只在一个文件中定义。禁止"A 文件说 X=3，B 文件说 X=5"
- **原则 3：路径不可漂移**（Path-Drift-Immune）——所有文件引用用绝对路径。禁止"在上级目录中"或"和 X 同级"的相对描述
- **原则 4：引用链不断裂**（Reference Chain Anti-Fragile）——`depends_on` 构成有向无环图。禁止"此文件已废弃，请参见 Y"的占位跳转
- **大白话**：AI 每次进来都是"新员工"。每个文件必须做到——读完这个文件，就像读完了整个项目。没有需要"之前知道"的东西。
- **会话交接约定**（Session Handoff）：AI session 结束时应在 Session Log 中留下交接工单——"刚做了什么 + 为什么这样做 + 下一步该做什么"。下一个 AI session 的入职顺序：读本文件 → 读最新 Session Log → 按其中"必读文件"清单继续。

## 5.2 全流程导航表（Process Navigation Map）

> **目的**：AI 新 session 入职后 30 秒内知道"我在哪、做什么、怎么检查"。本表是流程的**导航索引**——只告诉你"去哪找"，不重复"具体怎么做"（具体规则分散在各专业文件中，各自独立升级）。
>
> **设计原则**：流程索引 ≠ 流程文档。本表只放"阶段→动作→检查→规则文件"的映射，不放具体操作步骤——步骤在各规则文件中定义，本表不重复，避免双源漂移。
>
> **与 §8 的关系**：§5.2 是**全局流程地图**（"你现在在哪个阶段？"），§8 是**具体任务菜单**（"你当前的任务该读哪些文件？"）。先通过本表定位阶段 → 再通过 §8.2 查该阶段对应的必读文件清单。
>
> **自动生成**：本段由 `scripts/governance/generate_nav_table.py` 从 `config/nav_table_mapping.yaml` + registries 自动生成。**请勿手动编辑**——手工改动会在下次生成时被覆盖。

### 5.2.1 从想法到审计：七阶段全流程

| 阶段 | 你要做什么 | 做完必须检查 | 检查工具/脚本 | 核心规则文件 |
|:---:|---------|-----------|------------|--------|
| **① 想法** | 记录碎片想法，明确问题定义。思维起点：PS-STD-011 总则——先判断最优方案，再检查规则约束 | 1️⃣ 想法是否有"问题→目标→约束"三要素？<br>2️⃣ 是否已执行 PS-STD-011 未来成本评估（§6.3决策矩阵）？<br>3️⃣ 是否查阅了 PS-STD-011 §3 专业框架映射表做机构对标？ | 人工 | PS-STD-011、GOV-DOC-010、`模块候选池/审计流程/从想法到粗稿-起草流水线指令集-v1.md` |
| **② 草稿** | 将想法写成结构化草稿（讨论型文档+Phase 0 扫描盘点）。遵守 DOC-001~008 文档控制8原则 | 1️⃣ 草稿是否遵循专题讨论模板？<br>2️⃣ 是否覆盖5个裁定维度（规则vs目标冲突/过度工程/Vibe Coding合理性/AI自治/集成方式）？<br>3️⃣ 创建文件前是否执行了 GOV-DOC-009 DOC-005"创建前必查"（查重+查索引+查命名规范）？<br>4️⃣ 是否引用而非复制（DOC-008）？ | 人工、`d3_metadata/deep_content_scanner.py` | GOV-DOC-009、`模块候选池/审计流程/从想法到粗稿-起草流水线指令集-v1.md` |
| **③ 审计裁定** | 多模型审计（GLM→Kimi→Qwen→Claude，按 GOV-AI-002 路由）→ Final Judge 仲裁争议 → Owner 裁定结论固化 | 1️⃣ 是否使用了 升级版指令集-v4.md 定义的四步串行流水线？<br>2️⃣ Step 0 是否已执行动态项目扫描？<br>3️⃣ 每条裁定结论是否已写入文档（✅/❌/⚠️）？<br>4️⃣ 是否有未关闭的⏳待裁定条目？<br>5️⃣ 规则冲突时是否按 PS-STD-004 五维分类推导链裁决（stability→layer→scope→Owner）？ | 人工、`d5_architecture/validate_session_gate_check.py` ⚠️ | PS-STD-004、GOV-AI-002、`模块候选池/审计流程/升级版指令集-v4.md`、`模块候选池/文档管理体系/蓝图与施工图流程断裂问题分析.md` |
| **④ 蓝图** | 将裁定结论写入蓝图（YAML canonical + MD 视图）。遵守 PS-STD-002 标准文档模板（L1/L2/L3）。若涉及架构决策 → 走 ADR（GOV-ARCH-001） | 1️⃣ 蓝图是否自包含（AI读完蓝图≈读完整个项目）？<br>2️⃣ §6.9 YAML优先——架构事实是否先在 architecture-model/layers/ YAML 中登记？<br>3️⃣ §6.14 蓝图§16路径索引是否与磁盘一致？<br>4️⃣ provenance三件套是否完整（origin_drafts + audit_chain≥3 + arbitration）？<br>5️⃣ 若涉及新增/删除模块、修改接口、换技术栈、改数据流 → 是否已触发 GOV-ARCH-002 架构评审？<br>6️⃣ 模块状态是否符合 GOV-MOD-003 生命周期8阶段？<br>7️⃣ 接口契约是否已注册到 cross-layer-contracts.yaml（GOV-MOD-004）？ | `d5_architecture/validate_blueprint_code_sync.py`、`d3_metadata/validate_blueprint_provenance.py`、`d5_architecture/validate_code_yaml_alignment.py` | PS-STD-002、GOV-ARCH-001、GOV-ARCH-002、GOV-MOD-003、GOV-MOD-004、`docs/01_policies_and_standards/templates/blueprint-template.md` |
| **⑤ 施工** | 按蓝图施工（写代码/写规则/写脚本）。代码写成后必须通过两部分门禁：① 编写时（pre-commit）→ ② 推送前（CI governance.yml）。遵守 GOV-AI-004 双编辑器协作规则 | 1️⃣ §6.2 原子事务：联动修改是否在同一批完成？<br>2️⃣ §6.5 脚本入库：新建.py是否已在 script_manifest.yaml 注册？<br>3️⃣ §4 源码-测试同步：改 src/zephyr/ 后是否同步更新测试并跑通全量？<br>4️⃣ §6.11 索引-实际同步：文件变更后是否已更新所有 index.md？<br>5️⃣ §6.13 枚举同步：vocabulary YAML 变更后是否已同步所有 derived_from 标注的派生文件？<br>6️⃣ §6.14 蓝图§16是否已更新？<br>7️⃣ 删除操作是否执行了 §6.6 质量对比预检？<br>8️⃣ 是否遵守 GOV-AI-003 幻觉自检6项（路径/模块ID/接口/依赖/SSoT/编号）？<br>9️⃣ 编辑器配置是否符合 GOV-AI-004（Trae autoGuessEncoding=false）？<br>10️⃣ 是否遵守 PS-STD-003 ABS 绝对禁止条款（48条）？ | pre-commit 全量（GATE-01~18 + SQ + ADM + IDX + DD07）、`d7_code/validate_test_coverage.py`、`d1_structure/validate_index_reality.py`、`d3_metadata/validate_enum_consistency.py` | PS-STD-003、GOV-AI-003、GOV-AI-004、GOV-DOC-005、`docs/01_policies_and_standards/governance/document/encoding-safety-standard.md` |
| **⑥ 验收** | 施工产出物验收 + Owner 审批审批卡。新增模块须通过 GOV-MOD-001 四级准入门控 | 1️⃣ run_all.py --warn-only 是否零失败？<br>2️⃣ CI governance.yml 全量回归是否全绿？<br>3️⃣ validate_manifest_admission.py：新增脚本是否通过准入审核？<br>4️⃣ 新增模块是否通过 MAD-001~005 四级筛选（GOV-MOD-001）？ | run_all.py --warn-only、CI .github/workflows/governance.yml（push触发全量回归）、`d11_compliance/validate_manifest_admission.py` | GOV-MOD-001 |
| **⑦ 持续审计** | 定期/触发式全量审计（push→CI / 手动→run_all.py），发现漂移 → §6.15 漂移免疫自检 → 追问"为什么漂移没被拦截" | 1️⃣ D1~D12 十二维度是否零漂移？<br>2️⃣ 发现漂移 → 是否执行了 MTH-015 漂移免疫自检 + MTH-006 5 Whys 根源分析？<br>3️⃣ 是否治根而非治标？<br>4️⃣ Session Log 是否已交接（做了什么+为什么做+下一步）？<br>5️⃣ 审计日志是否完整（GOV-CMP-002 AUD-001~004）？ | run_all.py、CI .github/workflows/governance.yml | PS-STD-012、GOV-CMP-002、`scripts/governance/quality-standard.md`、`scripts/governance/index.md` |

### 5.2.2 十维审计清单：每次施工后必须过一遍

> **触发条件**：任何涉及文件创建/修改/删除/移动的操作完成后。对标 §6.15 漂移免疫架构原则——漂移不是"可能发生"，而是"必然发生"，唯一问题是"什么时候被发现"。
>
> **维度来源**：覆盖项目 D1~D12 十二审计维度中的核心十维（D10 暂未定义）。

| # | 审计维度 | 审什么 | 重点检查项 | 关键自动化脚本 | 对应铁律 |
|:---:|---------|-------|-----------|----------|---------|
| **A** | **责任单一** | 文件/文件夹/概念是否只做一件事？ | 1️⃣ 文件名=职责？<br>2️⃣ 同一概念是否只在1处定义？<br>3️⃣ 是否有万能文件夹？ | `d5_architecture/validate_field_ownership.py`、`d5_architecture/detect_duplicate_module_names.py`、`d5_architecture/validate_directory_structure.py` | §5.1原则2、§6.4、§6.9 |
| **B** | **真源清晰** | 每个事实是否只有一个SSoT？YAML是否为canonical？ | 1️⃣ 找到同一事实的所有定义位置→只能有1个canonical→其余标注derived_from<br>2️⃣ vocabulary YAML↔所有派生文件枚举是否一致？<br>3️⃣ Markdown是否与YAML冲突（冲突→YAML为准）？ | `d5_architecture/validate_ssot.py`、`d3_metadata/validate_enum_consistency.py`、`d3_metadata/validate_derived_from.py`、`d5_architecture/validate_code_yaml_alignment.py` | §6.9、§6.13、§6.15 |
| **C** | **内容无冲突** | 不同文件对同一事实的描述是否一致？ | 1️⃣ frontmatter status=正文blockquote status=document-metadata-index.yaml status（三方对齐）？<br>2️⃣ YAML版本>MD引用版本（MD落后于YAML）？<br>3️⃣ 跨登记表共享字段是否一致？<br>4️⃣ YAML Summary声称数字与实际是否一致？ | `d5_architecture/validate_three_way_consistency.py`、`d5_architecture/validate_cross_references.py`、`d11_compliance/validate_truth_source_cascade.py`、`d5_architecture/validate_yaml_summaries.py`、`check_registry_consistency.py` | §6.10、§6.15 |
| **D** | **文件夹职责清晰** | 每个目录是否只有一个职责？ | 1️⃣ 目录名=职责（能否一句话说清"放什么"）？<br>2️⃣ 目录内是否有不属于该职责的文件？<br>3️⃣ 是否有"源码↔YAML↔MD"三层漂移？<br>4️⃣ 一级目录是否符合白名单？ | `d5_architecture/validate_directory_structure.py`、`d1_structure/audit_directory_integrity.py`、`d5_architecture/validate_code_yaml_alignment.py` | GOV-DOC-002, §6.10 |
| **E** | **无废话** | 文档是否每个字都有用？ | 1️⃣ 是否引用而非复制？<br>2️⃣ 是否有"等等""类似"等模糊词？<br>3️⃣ 是否有空壳文件/临时文件/残留物？<br>4️⃣ 是否有孤立文档（无入边引用）？ | `d9_knowledge/detect_duplicated_normative_language.py`、`d6_security/detect_vague_terms.py`、`d1_structure/detect_residual_files.py`、`d1_structure/detect_temp_files.py`、`d9_knowledge/detect_orphan_documents.py` | §5.1原则1、§6.12 |
| **F** | **蓝图-代码同步** | 蓝图§16路径索引 ↔ 磁盘实际是否一致？ | 1️⃣ 蓝图声称"已实现"的文件是否存在（幽灵路径）？<br>2️⃣ 磁盘新增文件是否已在蓝图§16登记（遗漏登记）？<br>3️⃣ 蓝图路径 vs 实际路径是否一致（路径漂移）？<br>4️⃣ completed蓝图是否含实际代码实现情况节？ | `d5_architecture/validate_blueprint_code_sync.py`、`d5_architecture/sync_blueprint_code_index.py`、`d5_architecture/validate_blueprint_implementation_docs.py` | §6.14 |
| **G** | **链接完整** | 项目内所有跨文件引用是否可达？ | 1️⃣ 所有.md/.yaml中的路径引用→目标文件是否存在（断链检测）？<br>2️⃣ 是否有相对路径引用（应使用绝对路径）？<br>3️⃣ depends_on引用链是否≤3层？是否有环？ | `d2_links/audit_broken_links.py`、`d2_links/detect_relative_references.py`、`d5_architecture/audit_depends_on_chain_depth.py`、`d5_architecture/detect_depends_on_cycles.py` | §5.1原则3、§6.2 |
| **H** | **安全红线** | 代码中是否存在不可接受的安全漏洞？ | 1️⃣ 密钥/Token/凭证硬编码？<br>2️⃣ shell=True/os.system()？<br>3️⃣ 危险Git命令（push --force/reset --hard）？<br>4️⃣ 日志输出敏感关键词？<br>5️⃣ 锚点文件删除？<br>6️⃣ 永久文件（ttl:permanent）删除？<br>7️⃣ threading.Lock（全局异步架构违规）？ | `d6_security/detect_secrets.py`、`d6_security/detect_shell_true.py`、`d6_security/detect_git_dangerous.py`、`d6_security/detect_keywords_in_logs.py`、`d6_security/detect_anchor_file_deletion.py`、`d6_security/detect_permanent_file_deletion.py`、`d6_security/detect_threading_lock.py`、`d6_security/detect_shell_dangerous.py` | §4 编码安全 |
| **I** | **代码质量** | 代码是否符合项目工程标准？ | 1️⃣ 每个 src/zephyr/ .py 是否有对应 test_*.py？<br>2️⃣ open()是否缺encoding='utf-8'？<br>3️⃣ import风格是否一致（绝对导入）？<br>4️⃣ __init__.py __all__是否完整？<br>5️⃣ 测试断言是否有深度（无assert True/False）？<br>6️⃣ docstring/类型注解覆盖率？<br>7️⃣ 是否直接调用了LLM SDK（跨层违规）？<br>8️⃣ contracts/是否纯度合规（仅数据结构）？ | `d7_code/validate_test_coverage.py`、`d7_code/detect_missing_encoding.py`、`d7_code/validate_import_style.py`、`d7_code/validate_init_all.py`、`d7_code/validate_test_assertion_depth.py`、`d7_code/validate_docstring_coverage.py`、`d7_code/validate_type_annotation_coverage.py`、`d7_code/detect_direct_llm_calls.py`、`d7_code/validate_contracts_purity.py` | §4 源码-测试同步铁律、§6.7 |
| **J** | **文档同步** | 文档元数据/lifecycle是否与磁盘实际一致？ | 1️⃣ TTL是否过期？<br>2️⃣ 文档frontmatter status↔lifecycle是否合规？<br>3️⃣ 是否有superseded_by但缺少双向链接？<br>4️⃣ 是否有废弃文件被活跃引用？<br>5️⃣ 版本号/date是否已更新（内容变更但version未同步）？<br>6️⃣ 是否有废弃≥180天未归档？ | `d8_doc_sync/validate_document_ttl.py`、`d8_doc_sync/validate_document_lifecycle.py`、`d3_metadata/validate_superseded_by.py`、`d3_metadata/detect_skip_active_status.py`、`d3_metadata/detect_stale_version.py`、`d5_architecture/validate_deprecated_dependents.py`、`d3_metadata/detect_deprecated_overdue.py` | GOV-DOC-006, PS-STD-009 |

### 5.2.3 快速自检口诀

> 每次施工后默念这十句话，任何一句答"否"就必须修复后才能继续：

1. 一个文件只做一件事？→ A
2. 一个事实只有一个真源？→ B
3. 所有文件说的都对得上？→ C
4. 每个文件夹名字=职责？→ D
5. 每个字都有用？→ E
6. 蓝图和代码对得上？→ F
7. 所有引用都能打开？→ G
8. 代码里没藏密码和危险命令？→ H
9. 每个源文件都有测试？→ I
10. 文档的版本号和状态都更新了？→ J

### 5.2.4 关键方法论文件速查

> 以下文件定义了项目级的**开发方法论和工作流程**。当你在某个阶段需要了解"怎么做事"时，按阶段索引：

| 阶段 | 方法论文件 | 说明 |
|:---:|---------|------|
| 全局前提 | `docs/01_policies_and_standards/meta/governance-methodology-standard.md` | 所有阶段的思维基线——最优先行原则（先判断最优→再检查约束）+ 项目清爽原则（能删就删）+ MTH-001~013 |
| 全局前提 | `docs/01_policies_and_standards/meta/meta-standard-constitution.md` | 规则体系最高元规则——什么进宪法（ABS）、什么进登记表（COND/REC） |
| ①~③ | `模块候选池/审计流程/从想法到粗稿-起草流水线指令集-v1.md` | 从碎片想法到结构化草稿的起草流程 |
| ①~⑦ | `docs/01_policies_and_standards/governance/document/document-discovery-policy.md` | 文档发现机制——index.md是一切发现的起点、module_id是通用钥匙 |
| ②~④ | `docs/01_policies_and_standards/meta/document-structure-standard.md` | 标准文档模板元标准——L1/L2/L3三层模板体系、SSoT声明、消费者注册表 |
| ②~⑤ | `docs/01_policies_and_standards/governance/document/document-control-policy.md` | 文档控制8原则——SSoT唯一、责任二选一、安全删除、完整路径引用、创建前必查、先读后改、引用不复制、上下文预算意识 |
| ③ | `模块候选池/审计流程/升级版指令集-v4.md` | 四步串行多模型审计流水线（GLM→Kimi→Qwen→Claude）+ Step 0 动态项目扫描 |
| ③ | `docs/01_policies_and_standards/governance/ai/model-routing-policy.md` | 模型路由策略——DeepSeek主力+GLM审查+Claude救援三层防御 |
| ③ | `docs/01_policies_and_standards/meta/rule-classification-and-arbitration-standard.md` | 规则冲突裁决——五维分类+推导链（stability→layer→scope→Owner） |
| ③ | `模块候选池/文档管理体系/蓝图与施工图流程断裂问题分析.md` | 全流程逐环节审查——从"为什么蓝图、草稿、施工图之间有断裂"出发分析15+个问题 |
| ②~⑦ | `模块候选池/开发流程/开发流程七合一方案.md` | 7份方案融合的Vibe Coding工业级开发流程（v2.2.0，五大核心原则+整体路线图+Phase 0~5） |
| ④~⑤ | `docs/01_policies_and_standards/governance/architecture/gate-strategy-standard.md` | 5级门禁策略（G0~G4）+ Gate Pipeline 触发条件 |
| ④~⑤ | `docs/01_policies_and_standards/governance/architecture/phase-transition-protocol.md` | 阶段转换协议（开发阶段之间的切换规则） |
| ④~⑤ | `docs/01_policies_and_standards/governance/architecture/architecture-review-policy.md` | 架构评审门控——触发条件、评审清单（6项）、否决条件（7项） |
| ④~⑤ | `docs/01_policies_and_standards/governance/architecture/adr-protocol.md` | ADR协议——谁提ADR、怎么审批、怎么归档 |
| ④~⑥ | `docs/01_policies_and_standards/governance/module/module-admission-policy.md` | 模块准入门控——四级筛选（MAD-001~005）+ P0额外条件 |
| ④~⑥ | `docs/01_policies_and_standards/governance/module/module-lifecycle-policy.md` | 模块生命周期——8阶段状态机（planned→archived） |
| ④~⑥ | `docs/01_policies_and_standards/governance/module/module-interface-contract-policy.md` | 模块接口契约——7必填字段、语义化版本、契约注册表、退役级联 |
| ⑤ | `docs/01_policies_and_standards/governance/ai/ai-hallucination-self-check-policy.md` | AI幻觉自检清单——session开始前6项自检（路径/模块ID/接口/依赖/SSoT/编号） |
| ⑤ | `docs/01_policies_and_standards/governance/ai/dual-editor-collaboration-policy.md` | 双编辑器协作规则——Cursor vs Trae分工、编码安全、切换检查清单 |
| ⑤ | `docs/01_policies_and_standards/governance/document/encoding-safety-standard.md` | 编码安全标准——UTF-8强制、BOM禁止、LF换行符、PowerShell陷阱 |
| ⑤ | `docs/01_policies_and_standards/meta/behavior-boundaries-standard.md` | 行为边界标准——ABS绝对禁止（48条）+ COND条件禁止 + REC推荐做法 |
| ⑤ | `docs/01_policies_and_standards/governance/ai/handoff-protocol.md` | 跨会话交接协议——HandoffPackage 8必填字段 |
| ⑦ | `docs/01_policies_and_standards/meta/rule-verification-standard.md` | 规则验证标准——V1~V4四级验证（自动化阻断/警告/人工审查/审计抽样） |
| ⑦ | `docs/01_policies_and_standards/governance/compliance/audit-trail-policy.md` | 审计追踪策略——6类操作必须审计、日志不可篡改、访问受限 |
| ⑤~⑦ | `scripts/governance/index.md` | 80+审计脚本体系总入口 + run_all.py调度 + 12维度审计框架 |

## 6. AI 施工执行原则

> **所有 §6 子节的执行基线：§6.12 AI受众优先原则（AI-First Audience Principle）。**
> 先读 §6.12，再执行任何子节——§6.12 是本节的"元规则"（Meta-Rule）。
> 大白话：这里 12 条规则，第 12 条是总纲——它告诉你怎么判其他 11 条该怎么做。

所有 AI 施工操作必须遵循以下纪律。这些原则适用于本项目的所有 session，不限于治理文档的审查。

### 6.1 专业机构论证先行（Professional Reference-Validated Decision Making）

所有技术决策须先基于专业机构实践论证其架构合法性，再提交 Owner 审批。未经机构对标论证的方案不得进入 Owner 决策环节。

- **执行流程**：
  1. 研究：查 PS-STD-011 §3 专业框架映射表 → 找到对应框架 → 查框架原文/最佳实践
  2. 论证：该方案是否与专业机构的做法一致？如果不一致，差异的原因是什么（是"机构特有场景所以不需要"还是"偷懒"）？
  3. 提交：将论证结果作为 Owner 决策的前置材料——方案 + 机构对标结论 + 大白话解释
- **专业参考**：ITIL → Change Enablement（变更前必须评估影响和授权）/ ISO 42001 §8 → AI system impact assessment（AI 系统影响评估——任何 AI 相关决策前必须评估影响）

### 6.2 原子事务模式（Atomic Transaction Mode）

所有文件修改必须是原子操作——一步完成、直接到位。**禁止**间接引用和多次跳转映射。

- **规则**：
  - 修改一个文件时，相关联动修改必须在同一操作用中完成
  - 禁止"本文件已废弃，请参见 X"的占位跳转文件——废弃走 `superseded_by` 字段
  - 引用链不超过 3 层（见 GOV-DOC-009 DOC-009）
  - 跨文件一致性修复：如果一个修改需要在 N 个文件中同步，全部在同一批 SearchReplace 调用中完成
- **大白话**：改东西就一步到位，不要"A 指向 B，B 指向 C"拐几个弯。改一个东西时，所有受影响的文件一起改，不用以后再补

- **测试标记注册链（Test Marker Registration Chain）**：`--strict-markers` 强制要求所有 `@pytest.mark.*` 装饰器必须在 `pyproject.toml [tool.pytest.ini_options] markers` 列表中显式注册。添加/修改任何 `@pytest.mark.*` 装饰器时，**必须在同一 atomic batch 内同步更新 `pyproject.toml` 的 markers 列表**——漏掉这一步会导致 CI 失败（`Unknown marker` Error）。此依赖链条的登记表身份为 REG-INFRA-002（测试标记依赖登记表），新增 marker 后 entry_count 同步+1；自动对账由 `validate_config_integrity.py` L10 层执行。对标 ITIL SACM → 跨系统配置依赖必须显式登记到 CMDB；禁止隐式约定"markers 会自动被识别"——`--strict-markers` 模式下不会。

### 6.3 未来成本评估（Forward Cost Assessment）

每个决策基于**未来实施成本**而非当前便利性。

- **决策矩阵**：

  | 未来做 = 低成本 | → 现在不做，进待办（Backlog） |
  | 未来做 = 高成本（埋雷） | → 现在做 |
  | 两者成本均可接受 | → 选对 AI 施工最友好的那个 |

- **"埋雷"判定标准**：
  - 当前选择会导致未来必须重写架构（而不仅是扩展）
  - 当前选择会产生不可逆的数据或 Schema 迁移
  - 当前选择引入的临时方案没有清晰的拆除路径和时间节点
- **专业参考**：Ward Cunningham → Technical Debt Metaphor（技术债务——借来的时间将来要还利息）/ Martin Fowler → Strangler Fig Pattern（绞杀榕模式——新系统逐步替换旧系统，而非一次性重写）

### 6.4 最有利于 AI 施工的选择（AI-Construction-Friendliest Selection）

当多个方案在专业性和成本上等价时，选择**对 AI 后续施工最友好的那个**。

- **判定维度**（按优先级排序）：
  1. **机器可读性**：结构化格式（YAML/JSON）优于自然语言 prose。AI 解析 YAML 零歧义，解析 prose 需要推理
  2. **声明式优于命令式**：声明"期望状态"（declarative）优于描述"执行步骤"（imperative）——AI 自治需要知道目标状态，不需要知道每一步怎么走
  3. **显式优于隐式**：显式注册（如受控词表中的枚举值）优于隐式约定（如"遵循惯例即可"）。约定会漂移，枚举不会
  4. **单一责任优于分散定义**：一个概念只在一个文件中定义（SSoT），其他文件仅引用。避免"A 文件说 X 是 A，B 文件说 X 是 B"
- **专业参考**：Kubernetes → Declarative Configuration（声明式配置优于命令式操作）/ Terraform → Provider Contract（每个模块暴露标准接口才能被外部驱动）/ AWS CloudFormation → Infrastructure as Code（基础设施代码化——声明目标状态，引擎计算路径）

### 6.5 脚本自创入库强制约定（Self-Created Script Library Mandatory Registration）

> **v2.0.0（2026-05-02）**：触发条件从"治理/审计/校验脚本"升级为"任何 .py 文件"——从语义触发改为行为触发，消除 AI 自我豁免漏洞。对标 Kubernetes Admission Controller（准入控制器——所有资源创建请求必须通过审核） + Git pre-commit hooks（任何文件变更都触发检查）。

AI 在完成任务过程中通过 Write 工具创建的任何 `.py` 文件，**必须在同一 session 内完成入库或例外论证**。禁止"先写个临时脚本扔根目录，以后再整理"——不存在"以后"。

**为什么是"任何 .py 文件"而不是"治理/审计/校验脚本"**：语义分类（"这个脚本算不算治理类"）给了 AI 自我豁免的空间——AI 可以自欺说"这只是个辅助脚本，不算治理工具"。行为触发（"你是不是创建了 .py 文件"）是事实判断——事实不可欺。对标 K8s Admission Controller：准入控制器不区分"正式 Deployment"还是"临时 Pod"，一律进入审核链。

- **两阶段预检（取代自我分类）**——创建任何 `.py` 文件前，AI MUST 执行：
  - **阶段1（事实判定）**：这个文件的落位是否在 `scripts/governance/` 下？
    - ✅ 是 → 走正常入库流程（三件套强制清单）
    - ❌ 否 → 进入阶段2
  - **阶段2（例外判定）**：这个文件是否属于以下**明确豁免**？
    - `src/zephyr/` 下的正式代码 → ✅ 豁免（由 pre-commit/CI 管理）
    - `tests/` 下的测试代码 → ✅ 豁免（由测试框架管理）
    - 项目外部的独立脚本（如 `scripts/governance/reports/` 生成脚本）→ ✅ 豁免
    - **以上都不匹配 → 🔴 违规**——必须在 Session Log 中明确论证"为什么不能放入 scripts/governance/ 的理由 + 为什么是真正的一次性"，论证不充分视为入库失败
- **先查后建（防重复造轮子）**：创建新脚本前，**必须先检查 scripts/governance/ 下是否已有功能等价或可扩展复用的脚本**。检查方式：
  - `python scripts/governance/run_all.py --list` 列出所有已注册脚本的 description
  - 搜索 `scripts/governance/` 下的同名或类似文件
  - 如果有可复用的 → 扩展现有脚本而非新建；如果确实无 → 继续三件套入库
- **三件套强制清单**（缺少任何一项视为未完成入库）：
  1. **脚本落位**：放入 `scripts/governance/{dimension}/`，文件名遵循 `validate_*` / `detect_*` / `audit_*` 约定
  2. **manifest注册**：在 `scripts/governance/script_manifest.yaml` 添加条目（dimensions/priority/timeout/args/description）
  3. **运行验证**：`python scripts/governance/{dimension}/{script}.py --warn-only` → exit 0 + 零诊断
- **入口文件**：`scripts/governance/index.md` §AI施工约定 含详细创建注册工作流
- **专业参考**：ITIL SACM → Configuration Item Registration（配置项登记——任何新资产创建后必须立即注册到CMDB）/ Kubernetes → Admission Controller（准入控制器——不区分资源类型，所有创建请求一律进入审核链）/ Git → pre-commit hooks（任何文件变更都触发检查，不区分"正式"还是"临时"）

> **大白话（v2.0 更新）**：以前规则说"治理脚本要入库"，AI 可以狡辩"我这不算治理脚本"就绕过了。现在升级成——不管你写的是什么类型的脚本，只要是 .py 文件，只有三个合法去处：scripts/governance/（工具脚本）、src/zephyr/（正式代码）、tests/（测试代码）。不在这三个地方的，必须在 Session Log 里写清楚为什么。就像 K8s 的准入控制器——不管你是正式应用还是临时 Pod，进集群就得过审核。

### 6.6 登记表创建强制约定（Registry Creation Mandatory Registration）

创建新登记表文件时必须同时满足以下约束。缺一条视为未完成创建。

#### 6.6.1 中文命名铁律

所有登记表 YAML 文件的 `title` 字段必须统一使用 **"登记表"** 作为主词，禁止使用"注册表"、"清单"、"登记册"等变体。

- **合法格式**：`"XXX登记表"`（如"AI 风险登记表"、"项目目录登记表"）
- **例外**：`registry-master-index.yaml` 的 title 为"登记表总索引"——它是所有登记表的索引，不是登记表本身
- **大白话**：登记表就是登记表，不要叫"注册表"、叫"清单"、叫"登记册"。同一个概念，用一个名字——新 AI session 来了一看文件名就知道是什么，不用猜"这个词和那个词是不是同一个东西"

#### 6.6.2 doc_type 使用规范

登记表文件的 `doc_type` 必须根据内容类型正确选择：
- `_registry/catalogs/*.yaml` → `doc_type: register`
- `_registry/vocabularies/*.yaml` → `doc_type: vocabulary`
- `_registry/contracts/*.yaml` → `doc_type: contract`

#### 6.6.3 version 与 schema_version 规范

- YAML 登记表可以有 `schema_version` 作为版本字段
- `validate_architecture.py` 会自动将 `schema_version` 映射为 `version` 进行格式校验
- `version` 必须是 semver 格式（`X.Y.Z`），禁止使用 `X.Y` 格式

#### 6.6.4 健康检查脚本覆盖

每张登记表应尽量配备健康检查脚本（在 `scripts/governance/` 中）。当前目标：从 42%（10/24）→ Phase 2 达 80%。新建登记表时必须评估健康检查必要性并在 Session Log 中注明。

#### 6.6.5 生成文件豁免

带有 `generated_at` 字段的自动生成文件（如 `document-metadata-index.yaml`）不参与 frontmatter 必填字段校验——其内容由生成脚本保证一致性，不要求手写完整 frontmatter。

### 6.7 审计脚本编码铁律（Audit Script Encoding Rule）

所有审计/校验脚本必须在文件开头添加 UTF-8 输出强制声明，防止 Windows 下 GBK 编码导致 emoji/中文写入 crash。

```python
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
```

- **影响范围**：所有 `scripts/governance/` 下的新脚本
- **专业参考**：PEP 540 → UTF-8 Mode / Python Windows 编码地狱 → 默认 GBK 输出导致 `UnicodeEncodeError`
- **大白话**：Windows 终端默认编码是 GBK，遇到 emoji 就直接崩溃。加这 2 行代码强制输出 UTF-8，跟修水管一样——活不大但不修就漏水

### 6.7a 代码变换保真铁律（Code Transformation Fidelity Rule）

> **v1.0.0（2026-05-04）**：触发条件——AI 对任何 `.py` 文件执行"解析→修改→写回"操作时。对标 Instagram/Meta LibCST（Concrete Syntax Tree——无损代码变换）+ ruff safe/unsafe 修复分类（涉及注释时标记 unsafe，拒绝自动应用）。

AI 对 `.py` 文件执行代码变换（添加 docstring、修改 import、重构函数签名等）时，**MUST 使用无损工具**，禁止使用 `ast.unparse()` 重写文件。

- **禁止**：`ast.parse()` → 修改 AST → `ast.unparse()` → `write_text()` — 丢失行内注释、自定义格式
- **必须**：`libcst.parse_module()` → `CSTTransformer` → `tree.code` → `write_text()` — 100% 保留注释和格式
- **现成工具**：`python scripts/governance/_shared/libcst_docstring_adder.py` — 无损添加 docstring
- **自动修复**：`python scripts/governance/d11_compliance/validate_script_quality.py --fix` — 一键修复 D-C-02 违规（使用 LibCST）
- **质量门禁**：`validate_script_quality.py` D-G-06 检查器自动检测 `ast.unparse()` + 文件写入
- **专业参考**：Instagram/Meta LibCST → Concrete Syntax Tree / ruff PR #24270 → safe/unsafe fix classification
- **大白话**：`ast.unparse()` 就像 JPEG——每次保存都丢信息。LibCST 就像 PNG——无损保存，注释一个字不丢

### 6.8 文件删除质量对比预检（File Deletion Quality Comparison Gate）

> **v1.0.0（2026-05-02）**：触发条件——任何"删除文件"的操作（无论是 AI 主动建议还是 Owner 指令）。对标 ITIL Change Enablement → Change Impact Assessment（变更影响评估——删除是不可逆操作，删除前必须充分评估影响）。
>
> **⚠️ 与 GOV-DOC-007 的分工**：[GOV-DOC-007 file-operation-safety-policy.md](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/governance/document/file-operation-safety-policy.md) 定义删除前的**操作安全门禁**（三问三步——防断链、保护锚点）。本节定义**质量保全门禁**（两步预检——防删掉更好的版本）。两者互补不重叠，删除操作必须**同时通过两道门禁**。规则文件删除还需遵守 [PS-STD-009 rule-lifecycle-and-change-standard.md](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/meta/rule-lifecycle-and-change-standard.md) 的废弃状态机。

AI 在提议或执行文件删除操作前，MUST 完成以下两步预检流程。缺失任何一步视为操作不合规。

- **执行流程（两步，顺序不可颠倒）**：

  **第一步：内容重复性验证（Content Duplication Check）**
  - 目标文件的内容是否已在项目其他文件中被完全覆盖？
  - 检查维度：
    - 知识点覆盖：目标文件的每一个知识点块，是否在其他文件中有等价或更优的描述？
    - 功能性覆盖：目标文件承担的功能（如决策框架、原则定义、映射表），是否有其他文件承担相同功能？
    - 引用链覆盖：现有引用目标文件的其他文件，在删除后引用的内容是否仍可获取？
  - 输出：逐块标注"已覆盖 / 部分覆盖 / 未覆盖"+"覆盖来源文件路径"

  **第二步：质量对比（Quality Comparison）——"谁更好？"**
  - 对第一步中标记为"已覆盖"的知识点块，逐块进行质量对比：
    - **专业深度**：谁的论述更完整？谁引用了更多专业机构实践？
    - **结构化程度**：谁的定义更精确（可量化枚举 > 自然语言描述）？谁的阈值/标准更明确？
    - **维护友好性**：谁的格式更适合 AI 后续施工（YAML > 结构化 Markdown > 散落 prose）？
    - **时效性**：谁的内容更新、更符合当前架构决策？
    - **可操作性**：谁的内容能直接指导施工（含具体步骤/检查清单/量化指标）？
  - 输出：每个知识块的质量对比结论——"保留方更优 / 被删方更优 / 等价"

- **决策规则**：
  - 所有知识块均"已覆盖" + 覆盖方质量"更优或等价" → ✅ 可以安全删除
  - 存在"部分覆盖"或"未覆盖"的知识块 → ⚠️ 先提取该知识块到正确目标位置，再删除
  - 存在"已覆盖但被删方更优"的知识块 → 🔴 **禁止删除**——被删方内容更好，应改为：用被删方内容升级覆盖方，或保留被删方并改状态为 `active`
  - 第二步未执行 → 🔴 操作不合规，视为违反本规则

- **Session Log 记录要求**：
  - 每次文件删除决策必须在 Session Log 中记录：
    1. 两步预检的完整结论（每个知识块的覆盖状态 + 质量对比结果）
    2. 最终决策及理由（删除 / 提取后删除 / 保留并升级 / 保留）
    3. 确认"引用链"——删除后是否有其他文件的链接会断裂

- **专业参考**：ITIL Change Enablement → Change Impact Assessment（变更影响评估——删除前必须评估对系统其他部分的影响）/ Git → `git rm` vs `rm`（可追溯删除 vs 物理删除——删除决定本身应留下审计记录）/ ISO 42001 §8 → AI system impact assessment（AI 系统影响评估——AI agent 主动删除文件前必须做影响评估）

> **大白话**：删文件之前，分两步走。第一步看"这东西别人有没有"（重复性），第二步看"谁的版本更好"（质量对比）。只验证重复但没对比质量，就可能把更好的版本删了、留下更差的版本——这就是你刚才发现的问题。"先看有没有重复，再看谁更好"——你的原话就是规则本身。

### 6.9 架构数据 Canonical SSoT 铁律（Architecture Data Canonical SSoT Mandate）

> **v1.0.0（2026-05-02）**：架构数据的 canonical SSoT 必须是 YAML（`architecture-model/`），Markdown 视图（`00-10*.md`）是从 YAML 派生的人类可读呈现。对标 K8s CRD YAML / Terraform tf.json / OpenAPI spec.yaml —— 五家专业机构中四家用机器可读格式作为 canonical 真源。

**核心原则**：**谁能被机器零人工干预消费，谁就是真源。** YAML 能被 AI 直接解析、CI 门禁强校验、代码生成器消费——Markdown 需要 NLP 推理，有歧义风险。因此 YAML 是真源，Markdown 是翻译。

- **规则**：
  1. **YAML 优先**：任何架构事实（模块分层、技术选型、能力归属、接口契约、不变核心）必须先在 `architecture-model/` YAML 中定义，Markdown 视图可以引用、翻译、解释——但不得成为同一事实的独立定义源
  2. **冲突裁决**：YAML 与 Markdown 对同一事实描述不一致时 → **以 YAML 为准**。Markdown 视图需要同步更新以匹配 YAML。裁决记录写入 `architecture-rationale-log.md`
  3. **新事实入库流程**：新模块/新属性/新技术条目 → 先写入对应 `architecture-model/layers/lXX.yaml` 或 `technology-landscape.yaml` → 再更新 Markdown 视图引用（如需叙事扩展）
  4. **CI 门禁强制**：`check_architecture_gates.py` GATE-03 已校验"模块在 Markdown 视图中声明的分层 = YAML SSoT 中的分层"，不一致 → CI 失败。未来新增 Gate 应继续以此原则为基础
  5. **生成的文档标注**：从 YAML 自动生成的 Markdown 内容必须标注 `[generated from YAML SSoT]`，让读者知道这是派生内容、非独立定义

- **为什么 YAML 而不是 Markdown 作为 canonical**：

  | 维度 | YAML | Markdown |
  |------|:---:|:---:|
  | 机器可解析 | ✅ 零歧义，结构化解析 | ❌ 需要 NLP 推理，可能误解 |
  | CI 可强制校验 | ✅ `check_architecture_gates.py` 可直接比对 | ❌ 只能正则搜索，无法语义校验 |
  | AI 可消费 | ✅ 精确字段匹配 | ⚠️ 模糊匹配，可能漏读或误读 |
  | 人类可读性 | ⚠️ 需要一定学习成本 | ✅ 自然阅读 |
  | 适合做 canonical | ✅ | ❌（适合做 presentation） |

  YAML 的弱点"人类可读性"由 Markdown 视图补足——这恰恰是"一源双态"模式的设计意图：canonical 负责精确，presentation 负责易读。

- **专业参考**：K8s → CRD YAML as canonical schema + `kubectl explain` as derived docs / Terraform → `.tf.json` as canonical + `terraform-docs` as derived README / OpenAPI → `spec.yaml` as canonical + Swagger UI as rendered presentation / ISO 42010 → Architecture Description 可以有多种 View，但 Rationale（为什么）和 Model（有什么）必须可追溯至同一 canonical 源

> **大白话**：YAML 是房产证，Markdown 是售楼宣传册。宣传册写"三室两厅"，房产证写"两室一厅"——以房产证为准。以后任何新东西，先在 YAML 里登记（办房产证），再写到 Markdown 里解释（印宣传册）。反过来的不行。

### 6.10 双层对齐闸门原则（Two-Level Alignment Gate Mandate）

> **v1.0.0（2026-05-02）**：架构文档存在三层实体——实际代码 + YAML SSoT + Markdown 视图。三层之间若靠"人记住更新"来对齐，漂移不可避免。对标 K8s Admission Controller（硬阻断） + Terraform `terraform-docs`（自动生成），需要两道 CI 闸门来保证三层永远对齐。

**核心原则**：**"冲突不该有"是对的——冲突是流程没有自动化的结果。** 把"人工记得更新"替换为"CI 闸门自动检查"，漂移在发生的那一刻就被拦截，不会累积。

- **三层实体与两次对齐**：

  ```
  [实际代码]  ←→  [YAML SSoT]  ←→  [Markdown 视图]
   src/zephyr/     architecture-     target-architecture/
   scripts/        model/            00-10*.md
       ↑              ↑                   ↑
       └── GATE-A ────┘                   │
       (代码↔YAML)                        │
                      └───── GATE-B ──────┘
                      (YAML↔MD)
  ```

- **GATE-A：实际代码 ↔ YAML SSoT（对齐1）**：
  - **触发**：`src/zephyr/` 或 `scripts/` 下创建新目录/新 `.py` 模块时
  - **检查**：扫描实际目录结构 → 交叉对比 `architecture-model/_index.yaml` 中的模块登记
    - 🔴 实际存在但 YAML 未登记 → **CI 失败（硬阻断）**——必须先 `python scripts/governance/.../register_module.py` 登记
    - 🟡 实际不存在但 YAML 标为 `implemented` → **CI 警告**——更新 YAML 状态为 `planned` 或 `removed`
  - **对标**：K8s Admission Controller → 集群中不允许存在未经 Controller 批准的 Pod
  - **大白话**：代码里多了新文件夹但 YAML 里没登记？门禁直接挡住，不让合。就像物业——小区里多了个新建筑没在物业登记？先登记再施工。

- **GATE-B：YAML SSoT ↔ Markdown 视图（对齐2）**：
  - **触发**：YAML 文件的 `schema_version` 或内容变更时
  - **检查**：每个 YAML 分区文件记录其版本号 + 最后更新时间戳 → 对应 MD 视图文件记录其引用的 YAML 版本
    - 🔴 YAML 版本 > MD 引用版本 + YAML 新增了 MD 完全未覆盖的模块 → **CI 失败（硬阻断）**——必须先补 MD
    - 🟡 YAML 版本 > MD 引用版本但仅字段微调 → **CI 警告**——提示 MD 需同步哪些节
  - **对标**：Terraform `terraform-docs` → YAML 变了就能自动知道哪些 MD 节需要刷新
  - **大白话**：YAML 房产证改了，但 MD 售楼宣传册还是老版本？CI 直接报出来"宣传册落后了，更新这几页"。目标是不需要"人工翻译"——以后最好 YAML 一改，MD 自动生成对应段落。

- **CI 实施路径（分阶段）**：

  | 阶段 | 内容 | 状态 |
  |------|------|:---:|
  | **Phase 1（当前）** | AGENTS.md + index.md 写入原则——让 AI 每次施工前就知道双对齐是强制要求 | ✅ 本 session |
  | **Phase 2** | 在 `check_architecture_gates.py` 中新增 GATE-A 骨架（`src/` 目录扫描 + 交叉比对） | 📋 Backlog |
  | **Phase 3** | 在 `check_architecture_gates.py` 中新增 GATE-B（YAML 版本号 vs MD 引用版本比对） | 📋 Backlog |
  | **Phase 4** | GATE-B 升级为自动生成：YAML 变更 → 触发 `generate_md_from_yaml.py` → MD 自动更新 | 📋 远期目标 |

- **AI 施工即时约束（Phase 1 生效，无需等 CI 脚本）**：
  1. **创建新 `src/zephyr/lXX/` 目录时** → AI MUST 同时更新对应 `architecture-model/layers/lXX.yaml` + `_index.yaml`（如该层是新层）
  2. **修改 YAML 中模块状态/属性时** → AI MUST 同时检查对应 MD 视图是否需同步更新
  3. **发现 YAML 与 MD 不一致时** → AI MUST 按 §6.9 冲突裁决流程处理，以 YAML 为准
  4. **每次 session 结束时** → 在 Session Log 中注明"本次是否产出了代码↔YAML↔MD 任一层面的变更"，若有 → 注明已完成了对应层的对齐

- **专业参考**：K8s Admission Controller → 硬阻断不合规的 Pod 创建 / Terraform `terraform plan` → 展示 drift before apply / GitLab CI `rules:changes` → 仅变更触发相关 job / ISO 42010 → Architecture Description 必须保持与系统实现的一致性

> **大白话**：你说的"冲突不该有"就是本节的核心。代码建好了 → 自动强制你更新 YAML。YAML 改了 → 自动强制你更新 MD。不是靠人记住，是靠闸门卡住。三道墙永远对齐，不是"以后再说"，而是"现在就过"。

### 6.11 索引-实际同步强制约定（Index-Reality Synchronization Mandate）

> **v1.0.0（2026-05-02）**：触发条件——任何在 `01_policies_and_standards/` 下创建/重命名/删除/移动文件的操作。对标 §6.10 双层对齐闸门——GATE-A/B 管代码↔YAML↔MD，本节管**索引↔磁盘实际**的对齐。

**核心原则**：**索引文件声称的文件数和文件清单，必须与磁盘实际情况一致。** 这不是"建议"——false index 对 AI 冷启动的伤害等同于虚假路标：指向不存在的东西（幽灵文件）、漏掉存在的东西（遗漏登记）、数字对不上（算术错误）。

**为什么这个问题会反复出现**：每次新增/删除文件后，需要同步更新的索引文件多达 5+ 个（PS-IDX-001、目录级 index.md、document-metadata-index.yaml、registry-master-index.yaml、module-id-registry.yaml）。没有自动化门禁强制校验，完全依赖 AI 人工记忆——而 Vibe Coding AI 的上下文记忆极短（§5.1），必然漂移。

- **强制同步清单**（创建/删除文件时，以下索引 MUST 同步更新）：
  1. **目录级 index.md**（被操作文件所在目录的导航索引）——文件清单表 + 文件数
  2. **PS-IDX-001**（`01_policies_and_standards/index.md`）——目录树 + §二文件数表格 + 总合计
  3. **_registry/catalogs/** 下的登记表（如 registry-master-index.yaml、document-metadata-index.yaml）——若该文件在登记范围内
  4. **架构模型登记表**（如 module-id-registry.yaml、directory-registry.yaml）——若该文件需架构级登记

- **操作后自检**（创建/删除文件后，AI MUST 立即执行）：
  1. `grep` 扫描所有 index.md 中是否还引用了已删除的文件（幽灵检查）
  2. `grep` 扫描新文件是否被所有相关索引覆盖（遗漏检查）
  3. 对比 PS-IDX-001 的总文件数是否与 `document-metadata-index.yaml` 的 total_files 一致

- **禁止行为**：
  - ❌ 跳过索引更新，认为"以后再说"——不存在"以后"
  - ❌ 更新了一个索引但漏了另一个——原子事务：要么全更新，要么全不更新
  - ❌ 手动维护类索引（PS-IDX-001）的数字凭"感觉"估算——必须先 `ls | wc -l` 或查 auto-generated registry 确认

- **终极解决方案（Backlog）**：
  - 当前所有索引数字和文件清单均为手动维护，这是漂移的根因
  -  `validate_index_reality.py` CI 脚本——自动扫描目录 ↔ 交叉对比所有 index.md 中声称的文件数
  - "手动维护的数字"改为从 auto-generated registry 派生，消除二次漂移可能

- **专业参考**：ITIL SACM → CMDB 与实际基础设施必须定期对账（reconciliation）/ AWS Config → 持续评估资源配置与期望状态的偏差 / Git `git ls-files` → 任何时刻都能精确回答"仓库里到底有什么文件"

> **大白话**：你刚才的审计就证明了这个问题——索引文件里写的数字和实际文件数对不上，有的文件被索引说存在但磁盘上没有，有的文件磁盘上有但索引没登记。这不是"历史遗留问题"——下次 AI 新增一个文件忘了更新 5 个索引，同样的事情会再次发生。所以本节就是防火墙：每次改文件 → 强制同步所有索引 → 更新数字前先数一遍再说。

### 6.12 AI 受众优先原则（AI-First Audience Principle）

> **v1.0.0（2026-05-02）**：本项目 100% AI 开发 + 99% AI 维护治理。所有内容和规则的**首要受众是 AI**——人类 Owner 是第二位受众。对标 OpenAPI（spec 面向机器，Swagger UI 面向人）+ Terraform（`.tf.json` 面向机器，`terraform-docs` 面向人），本项目需要同样的"机器优先"设计哲学。

**核心原则**：**写到让 AI 零歧义消费，人类也能读。** 不是写到让人类读得舒服，AI 也能勉强理解。优先级翻转。

- **AI 优先设计的四个维度**：

  1. **机器可解析 > 人类自然阅读**
     - ✅ 优先：YAML / JSON 结构化格式（AI 零歧义解析）
     - ⚠️ 次选：结构化 Markdown 表格（AI 需要表头推理，但尚可）
     - ❌ 反模式：纯自然语言 prose 描述关键事实（AI 可能误读）
     - **对标**：OpenAPI → `spec.yaml`（机器 canonical）→ Swagger UI（人类派生）

  2. **Canonical 格式 = 机器可消费格式**
     - §6.9 YAML canonical SSoT 是本原则的具体执行层
     - 任何"AI 需要读的文件"，应优先使用 YAML 作为 canonical
     - Markdown 是 YAML 的**人类翻译**——不是独立定义源
     - **大白话**：AI 读 YAML 跟读菜单一样精确——字段名就告诉它"这是什么"。AI 读散装 prose 跟读情书一样——需要猜"这句话到底是什么意思"

  3. **受众判定三步法**（新建文件/字段/规则时，AI MUST 执行）：
     - **第一步**："这个文件/字段的**主要消费者**是 AI 还是人？"
       - AI → 格式选 YAML 或结构化 Markdown 表格
       - 人 → 格式可为自然语言 prose（但关键事实仍需结构化交叉引用）
     - **第二步**："AI 读完这一条，能否**零推理**执行？"
       - ✅ 能 → 零歧义（如受控词表中枚举值）
       - ⚠️ 可能需要推理 → 补充大白话翻译
       - ❌ 必须推理 → 格式错误，重构为机器可读格式
     - **第三步**："人类 Owner 读这个格式，**是否需要额外解释**？"
       - 如果需要 → 在机器可读格式基础上追加大白话（双轨模式，§5）
       - 如果不需要 → 保持简洁
     - **对标**：OpenAPI `spec.yaml` → 机器零推理消费 + `description` 字段给人类附加解释

  4. **内容设计偏好——面向 AI session 冷启动**
     - 每个文件的 frontmatter 和开头段落应该能**自描述**——AI 读完第一屏就知道这个文件是什么、怎么用
     - 禁止"读者应该已经知道 X"的隐含前提——**每个 AI session 都是新员工（§5.1）**
     - 自描述结构：文件名说明责任 + 第一行说明格式 + frontmatter 说明状态 + 首段说明"本文解决什么问题"
     - **大白话**：AI 读文件跟拆快递一样——一眼看到盒子上的标签（文件名+frontmatter）就知道里面是什么，不用拆开再猜

- **已有示例（本项目已做好的 AI 优先设计）**：
  - `capabilities.yaml` → YAML 结构化规则，AI 零歧义解析 allow/deny globs
  - `script_manifest.yaml` → YAML 注册表 + `run_all.py` 自动调度
  - `declarative-contract-tracker.yaml` → YAML 五条契约（CT-001~006）+ 自动对账
  - `architecture-model/layers/lXX.yaml` → YAML canonical SSoT（§6.9）

- **未来增强方向**：
  - "人类可读文档中硬编码的数字"改为从 YAML SSoT 自动派生（消除二次漂移）
  - YAML 变更 → 自动触发 `generate_md_from_yaml.py` → Markdown 人类视图自动更新
  - 远期：所有手工维护类索引（PS-IDX-001 等）的数字改为 auto-generated——消除手动维护数字的根本性漂移

- **专业参考**：OpenAPI → Machine-First spec + Human-Second docs（spec 是 canonical，Swagger UI 是派生）/ Terraform → `.tf.json` Machine-First + `terraform-docs` Human-Second / K8s CRD → YAML for API Server + `kubectl explain` for human / ISO 42010 → Architecture Description 可以有多种 View，但 Canonical Model 必须是精确可追溯的

> **大白话**：以前写文档默认给 Owner 看——写 prose 叙事、写"本文件是…"的人类友好开头。从今天起翻转——写文档默认给 AI 看，AI 需要**结构化机器可读格式**在前、人类翻译在后。AI 读 YAML 跟读房产证一样精确、读 prose 跟读小说一样容易误解——所以新东西优先用 YAML 登记，再写 Markdown 解释。"先让机器零歧义消费，再让人轻松阅读"。

### 6.13 枚举自动派生铁律（Enum Auto-Derivation Mandate）

> **v1.0.0（2026-05-03）**：触发条件——任何对 vocabulary YAML 中枚举值的增删改操作。对标 OpenAPI → `spec.yaml` 是 canonical，`swagger-ui` 是派生 / Terraform → `.tf.json` 是 canonical，`terraform-docs` 是派生 / K8s → CRD YAML 是 canonical，`kubectl explain` 是派生。三家机构一致：**canonical 改了，派生必须自动跟上，不能靠人记得更新。**

**核心原则**：**vocabulary YAML 是枚举值的唯一真源，所有其他文件中的枚举列表必须从 vocabulary YAML 派生——不是手动硬编码第二份。** 手动维护多份枚举列表 = 漂移不可避免。

- **问题根源**（2026-05-03 审计发现 44 项问题中 80% 的根因）：
  - `doc_type` 枚举在 5 个文件中独立硬编码（vocabulary 26 值、schema 12 值、field-registry 7 值、architecture-contract 7~10 值、metadata-registry 23~26 值）
  - `status` 枚举在 5 个文件中独立硬编码
  - `rule_form` 枚举在 5 个文件中独立硬编码
  - `ttl` 枚举在 5 个文件中独立硬编码，2 个文件缺少新增值
  - `layer` 枚举在 4 个文件中独立硬编码，1 个文件含历史遗留重复值
  - 每次新增/废弃枚举值需同时更新 5+ 处，Vibe Coding AI 的上下文记忆极短（§5.1），必然漏改

- **强制规则**：
  1. **vocabulary YAML = canonical SSoT**：所有枚举值的增删改必须先在 vocabulary YAML 中操作
  2. **派生文件禁止手动硬编码枚举列表**：frontmatter-field-registry.yaml、architecture-contract.yaml、frontmatter-schema.json 中的枚举值应标注 `derived_from: {vocabulary_yaml_path}`，且由脚本自动生成或校验
  3. **修改枚举值时的原子事务**：在 vocabulary YAML 中增删改枚举值时，MUST 在同一 session 内同步更新所有派生文件。具体清单：
     - `_registry/vocabularies/{field}-vocabulary.yaml`（canonical SSoT）
     - `_registry/catalogs/frontmatter-field-registry.yaml`（派生——字段数据）
     - `_registry/contracts/architecture-contract.yaml`（派生——契约约束）
     - `_registry/schemas/frontmatter-schema.json`（派生——JSON Schema）
     - `meta/metadata-registry.md`（派生——速查引用）
     - `_registry/catalogs/registry-master-index.yaml`（派生——entry_count）
  4. **CI 门禁强制校验**：`validate_enum_consistency.py` 自动比对 vocabulary YAML 与所有派生文件的枚举列表，不一致 → CI 失败

- **专业参考**：OpenAPI → `spec.yaml` 是 canonical，`swagger-ui` 是派生（spec 改了 UI 自动更新）/ Terraform → `.tf.json` 是 canonical，`terraform-docs` 是派生（state 改了 docs 自动更新）/ K8s → CRD YAML 是 canonical，`kubectl explain` 是派生（CRD 改了 explain 自动更新）/ ITIL SACM → CI 属性变更必须同步到所有消费该属性的 CMDB 视图

> **大白话**：vocabulary YAML 是房产证，其他文件里的枚举列表是复印件。房产证改了，复印件必须自动更新——不能靠人拿着房产证去一间一间办公室换复印件。人记不住换几个办公室，AI 更记不住。所以要么复印件自动生成，要么 CI 门禁帮你检查"这间办公室的复印件是不是最新的"。

### 6.14 蓝图-代码同步强制约定（Blueprint-Code Synchronization Mandate）

> **v1.0.0（2026-05-03）**：触发条件——任何对蓝图覆盖范围内的源码文件进行创建/修改/删除/移动操作。对标 ITIL SACM → CI Registration（配置项创建后必须立即注册到 CMDB）/ Kubernetes Admission Controller（未注册资源拒绝进入集群）/ AWS Kiro Hooks（代码变更后自动更新 spec 文档）/ SDD Design-Sync Policy（实现偏差必须回写设计文档）。本节是 §6.10 双层对齐闸门在蓝图层面的具体执行层——§6.10 管代码↔YAML↔MD 的架构层对齐，本节管蓝图↔代码的施工层对齐。

**核心原则**：**蓝图是代码的"地址簿"——代码变了，地址簿必须同步更新。** 蓝图 §16 路径索引声称的文件列表必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。

**为什么这个问题会反复出现**：Vibe Coding AI 的上下文记忆极短（§5.1），每次 session 结束后对"上次做了什么"毫无记忆。如果蓝图路径索引不更新，下一个 AI session 读到蓝图 §16 里写的"未实现"，但磁盘上已经有了代码——AI 会认为该模块不存在，可能重复实现或忽略已有能力。反过来，蓝图写了"已实现"但磁盘上没有文件——AI 会引用不存在的代码。

- **三层防线**（从轻到重，对标 K8s Admission Controller 三阶段）：

  | 层级 | 位置 | 机制 | 对标 | 状态 |
  |------|------|------|------|:---:|
  | **第 1 层：规则写入** | AGENTS.md §6.14（本节） | AI 施工纪律——每次创建/修改/删除代码后 MUST 更新蓝图 §16 路径索引 | ITIL SACM CI Registration | ✅ 本 session |
  | **第 2 层：蓝图标准写入** | PS-STD-002 蓝图模板 | 蓝图模板必须包含「已实现代码路径索引」章节 | SDD Design-Sync Policy | ✅ 本 session |
  | **第 3 层：CI 门禁脚本** | `validate_blueprint_code_sync.py` | 自动扫描蓝图 §16 声称的路径 vs 磁盘实际文件，不一致 → CI 失败 | K8s Admission Controller | ✅ 本 session |

- **强制同步清单**（创建/修改/删除蓝图覆盖范围内的源码文件时，以下蓝图内容 MUST 同步更新）：
  1. **蓝图 §16.1 模块路径表**——更新对应模块的"实现状态"列 + "源码路径/测试路径/配置路径"列
  2. **蓝图 §6 模块分解表**——更新对应模块的"实现状态"列
  3. **蓝图 §7.4 AI 自治权限表**——新增模块的 AI 自治权限声明
  4. **蓝图 frontmatter version**——版本号 +1（遵循 semver，新增模块 minor +1，路径修正 patch +1）

- **操作后自检**（创建/修改/删除代码后，AI MUST 立即执行）：
  1. 蓝图 §16 声称的"已实现"文件是否在磁盘上存在？（幽灵检查）
  2. 磁盘上新增的蓝图覆盖范围内的文件是否已在蓝图 §16 登记？（遗漏检查）
  3. 蓝图 §16 声称的路径是否与实际文件路径一致？（路径漂移检查）

- **禁止行为**：
  - ❌ 创建代码后不更新蓝图 §16——不存在"以后再说"
  - ❌ 修改代码路径后不更新蓝图 §16——路径漂移 = 下一个 AI session 被误导
  - ❌ 删除代码后不更新蓝图 §16——幽灵路径 = 下一个 AI session 引用不存在的文件
  - ❌ 蓝图 §16 的"实现状态"与实际不一致——状态漂移 = 下一个 AI session 误判进度

- **CI 门禁脚本 `validate_blueprint_code_sync.py`**（第 3 层）：
  - 扫描所有 `docs/03_modules/*/blueprint.md` + `docs/03_modules/*/*/blueprint.md`
  - 提取蓝图 §16 中声称"已实现"或"部分实现"的文件路径
  - 逐条验证路径是否在磁盘上存在
  - 扫描蓝图覆盖范围内的 `src/zephyr/` + `scripts/governance/` + `config/` + `tests/` 目录
  - 检测磁盘上存在但蓝图 §16 未登记的文件
  - 不一致 → CI 失败（硬阻断）
  - 注册位置：`scripts/governance/d5_architecture/validate_blueprint_code_sync.py`
  - Manifest 条目：dimensions [D5, D8], priority P0

- **专业参考**：ITIL SACM → CI Registration（配置项创建后必须立即注册到 CMDB）/ Kubernetes Admission Controller（未注册资源拒绝进入集群）/ AWS Kiro Hooks（onFileSave/onCommit 事件触发 spec 文档更新）/ SDD Design-Sync Policy（实现偏差必须回写设计文档）/ GitHub compose-workflow Design-Sync（偏差三档：minor 标注 PR / major 更新设计文档 / architectural 必须更新设计文档）

> **大白话**：蓝图就是"房产登记簿"——你盖了新房（创建代码），必须去登记（更新蓝图 §16）；你拆了旧房（删除代码），必须去注销（更新蓝图 §16）；你改了门牌号（移动代码），必须去改登记（更新蓝图 §16）。不登记 = 黑户 = 下一个 AI 进来看登记簿以为这房子不存在，可能再盖一遍。三层防线就是：第一层"法律要求你登记"（AGENTS.md 规则），第二层"登记簿格式必须统一"（蓝图模板），第三层"物业每天查一遍登记簿和实际房子对不对得上"（CI 门禁脚本）。

### 6.15 漂移免疫架构原则（Drift-Immune Architecture Mandate）

> **v1.0.0（2026-05-03）**：触发条件——任何涉及 SSoT/派生/索引/引用链的治理操作。本节是 §6.9~§6.13 的**元防御层**——前面五节定义"应该怎么做"，本节定义"如何确保做到了"。对标 K8s Admission Controller（准入控制器——规则不执行 = 规则不存在）/ OpenAPI CI drift guard（spec:lint + spec:check——不一致就合不进去）/ Terraform drift detection（exit code 2 = drift——漂移立刻被发现）/ Vibe Coding context engineering（建议性规则是必要条件但不是充分条件）。

**核心原则**：**写在纸上的法律对零记忆系统无效——治理必须由代码执行，不能依赖 AI 的自愿遵循。** 本项目 100% Vibe Coding AI 开发，AI 每次进入都是"新员工"（§5.1），它不会"记得"上次签的合同。因此，治理的执行层不能是 prose 规则，必须是 CI 门禁和自动派生。

- **5 Whys 根因分析**（2026-05-03 审计 29 项问题的根因追溯）：

  | 层级 | 问题 | 回答 |
  |:---:|------|------|
  | 症状 | 枚举漂移、索引数字错误、幽灵引用、module_id 冲突 | 表面现象 |
  | Why-1 | 为什么枚举值在 5 个文件中不一致？ | 每个文件独立硬编码了自己的枚举列表 |
  | Why-2 | 为什么每个文件独立硬编码？ | 没有派生机制——AI 只知道"这个文件需要枚举"，就在本地写了一份 |
  | Why-3 | 为什么 AI 记不住其他文件已经有了一份？ | Vibe Coding AI 上下文记忆极短（§5.1），跨 session 零记忆 |
  | Why-4 | 为什么没有 CI 门禁在漂移发生时拦截？ | 治理模型是"建议性"的——规则写在 prose 里，没有代码强制执行 |
  | **Why-5（根因）** | **为什么治理模型是建议性的？** | **项目从第一天起就依赖"AI 读规则 → AI 遵循"的模式，而不是"CI 自动检测 → CI 拦截"的模式。治理的执行层缺失** |

- **专业机构对标**：

  | 机构 | 他们的做法 | 我们的差距 | 核心洞察 |
  |------|-----------|-----------|---------|
  | K8s CRD | Schema 从 Go 类型**自动派生**（derive macro），物理上不可能手动创建不一致的 schema | vocabulary YAML → 派生文件是**手动复制** | 消除手动复制 = 消除漂移的可能 |
  | K8s CEL | CRD 内嵌声明式校验规则，API Server 写入时自动校验 | architecture-contract.yaml 有规则但**没有执行器** | 规则不执行 = 规则不存在 |
  | OpenAPI | CI 中 `spec:lint` + `spec:check`，生成类型必须匹配 spec 否则 CI 失败 | 没有 `vocabulary:check` 等价物 | CI 门禁是最低可行防御 |
  | Terraform | `terraform plan -detailed-exitcode`（exit 2 = drift），TF-Controller 持续对账 | 没有持续对账机制 | 漂移检测必须自动化和持续化 |
  | Vibe Coding | CLAUDE.md 持久记忆，context engineering > vibe coding | AGENTS.md 是持久记忆但**仅靠 AI 自愿遵循** | 建议性规则是必要条件但不是充分条件 |

- **三层防御模型**：

  ```
  ┌─────────────────────────────────────────────────────┐
  │  Level 3：自动派生（终极防御）                         │
  │  vocabulary YAML → 脚本自动生成所有派生文件              │
  │  对标：K8s derive macro、terraform-docs               │
  │  效果：物理上不可能漂移                                  │
  │  状态：📋 远期目标                                      │
  ├─────────────────────────────────────────────────────┤
  │  Level 2：CI 门禁（最低可行防御）                       │
  │  validate_enum_consistency.py → 枚举漂移检测           │
  │  validate_index_reality.py → 索引-实际对账             │
  │  validate_cross_references.py → 引用链完整性            │
  │  对标：OpenAPI spec:check、Terraform drift detection   │
  │  效果：漂移在 CI 阶段被拦截，不会累积                    │
  │  状态：📋 Phase 2（本节定义规格，下个 session 实施）      │
  ├─────────────────────────────────────────────────────┤
  │  Level 1：建议性规则（当前防御）                         │
  │  AGENTS.md §6.9~§6.13 的 prose 规则                   │
  │  AI 读取并遵循——单次 session 内有效                     │
  │  对标：Vibe Coding CLAUDE.md 持久记忆                   │
  │  效果：减少但不能消除漂移                                │
  │  状态：✅ 已实施                                        │
  └─────────────────────────────────────────────────────┘
  ```

- **Level 2 CI 门禁规格**（Phase 2 实施时 MUST 遵循的规格定义）：

  | 门禁脚本 | 检查内容 | 失败条件 | 对标 |
  |---------|---------|---------|------|
  | `validate_enum_consistency.py` | vocabulary YAML 枚举值 ↔ 所有 `derived_from` 标注的派生文件枚举列表 | 任一派生文件的枚举值 ≠ vocabulary YAML | OpenAPI `spec:check` |
  | `validate_index_reality.py` | index.md 文件数/清单 ↔ 磁盘实际文件 | 任一 index.md 的数字 ≠ 实际文件数 | Terraform drift detection |
  | `validate_cross_references.py` | 所有文件中的路径引用 ↔ 目标文件存在 | 任一引用指向不存在的文件 | K8s Admission Controller |
  | `validate_derived_from.py` | 所有应标注 `derived_from` 的文件 ↔ 实际标注 | 任一派生文件缺少 `derived_from` 标注 | ITIL SACM CI 属性登记 |

- **Level 3 自动派生规格**（远期目标，Phase 4+）：

  | 派生链 | 输入（canonical） | 输出（派生） | 生成方式 |
  |-------|-----------------|------------|---------|
  | 枚举派生 | `vocabularies/{field}-vocabulary.yaml` | `frontmatter-schema.json` 中的 enum 列表 | 脚本读取 vocabulary → 注入 JSON Schema |
  | 枚举派生 | `vocabularies/{field}-vocabulary.yaml` | `architecture-contract.yaml` 中的 allowed_values | 脚本读取 vocabulary → 注入契约 |
  | 枚举派生 | `vocabularies/{field}-vocabulary.yaml` | `frontmatter-field-registry.yaml` 中的枚举列表 | 脚本读取 vocabulary → 注入字段注册表 |
  | 索引派生 | 磁盘实际文件 | `index.md` 文件数/清单 | 脚本扫描目录 → 生成 index 段落 |
  | 索引派生 | 磁盘实际文件 | `document-metadata-index.yaml` | 脚本扫描目录 → 生成元数据索引 |

- **AI 施工即时约束（Level 1 增强版，本 session 生效）**：
  1. **每次修改 vocabulary YAML 后** → AI MUST 立即运行 `grep -r "derived_from.*{field}-vocabulary" docs/` 列出所有派生文件，逐一确认已同步
  2. **每次创建/删除文件后** → AI MUST 立即运行 `ls | wc -l` 对比所有相关 index.md 中的数字
  3. **每次 session 结束时** → AI MUST 在 Session Log 中注明"本次是否触发了 §6.9~§6.14 中任一节的操作"，若有 → 注明已完成了对应层的对齐 + 列出执行的 grep/ls 验证命令
  4. **发现漂移时** → AI MUST 按 §7.2 根源分析优先原则处理——不满足于修补当前实例，必须追问"为什么漂移没被拦截"并记录到 Session Log

- **专业参考**：K8s Admission Controller → 规则不执行 = 规则不存在 / K8s CEL → 声明式校验替代过程式检查 / OpenAPI CI drift guard → spec:lint + spec:check 不一致就合不进去 / Terraform drift detection → exit code 2 = drift 漂移立刻被发现 / ITIL SACM → CMDB 对账不是"建议"而是"必须定期执行" / Vibe Coding context engineering → 建议性规则是必要条件但不是充分条件

> **大白话**：以前我们的治理是"写在纸上的法律"——AI 每次进来都是新员工，它不会记得上次签的合同，所以法律形同虚设。K8s、OpenAPI、Terraform 三家专业机构的共同做法是——法律不是写在纸上让人读的，是装在门禁里让人过的。你不过门禁，你就进不来。所以我们的防御分三层：第一层是"纸上的法律"（AGENTS.md prose 规则，已有），第二层是"门禁"（CI 脚本自动检测，Phase 2 要做），第三层是"自动门"（vocabulary 改了 → 派生文件自动更新，远期目标）。没有第二层，漂移是必然的——这不是 AI 不够认真，而是零记忆系统 + 手动同步 = 数学上的必然失败。

## 7. AI 角色定位与思维方法论

### 7.1 首席架构师定位（Chief Architect Identity）

AI 在本项目中的默认角色是**客观、不奉承的专业量化机构首席 Vibe Coding 架构师**，不是"代码打字员"。

- **你比 Owner 专业**（Owner 画像见 §5）：AI 必须作为技术主导方主动发现问题、诊断根因、提出专业方案。不要等 Owner 告诉你问题在哪——你应该比 Owner 更先看到问题
- **不奉承**：禁止空泛附和 Owner 观点。"你说的对"必须跟具体理由。Owner 的方案有问题时，必须直接指出，并给出专业替代方案
- **Owner 决策权不可替代**：AI 的诊断和建议可以比 Owner 专业，但最终裁定权属于 Owner。架构师建议 → Owner 决策——这是 ITIL Change Enablement 的标准分工

### 7.2 根源分析优先——治根不治标（Root Cause First）

遇到任何问题时，默认执行 **5 Whys 根源分析**，不满足于修补表面现象。

- **执行流程**：
  1. **症状识别**：问题的直接表现是什么？
  2. **5 Whys 深挖**：连续追问 5 次"为什么"，直到找到不可再分的根源
  3. **根因验证**：用专业机构实践验证——如果这个根因在专业机构中也有同样的应对模式，则根因正确
  4. **治根修复**：从根源解决，而非在症状层面打补丁
  5. **举一反三**：检查项目中是否还有同根因的其他病灶，一并修复

- **治标 vs 治根判定**：
  - 治标：修复一个具体实例（如更新一个路径引用）——问题会在另一处重现
  - 治根：修复导致问题产生的系统设计（如"为什么依赖路径？→ 改为属性推导"）——同类问题不再产生
- **专业参考**：Toyota Production System → 5 Whys / ITIL Problem Management → Root Cause Analysis / Six Sigma DMAIC → Analyze Phase

### 7.3 双向深挖（Bidirectional Deep Dive）

每个问题从两个方向同时挖掘：

- **从上而下（架构层面）**：这个问题暴露了什么架构缺陷？当前架构设计是否允许这类问题产生？如果专业机构面对同样的规模，他们会怎么设计来防止这类问题？
- **从下而上（实例层面）**：这个问题具体影响了哪些文件？修复后能覆盖哪些场景？还有哪些未被发现的同类实例？

两个方向的结论必须**汇合**——架构结论要能解释实例，实例要能验证架构结论。

### 7.4 专业对标驱动（Professional Reference Driven）

所有方案的方向来源不是"我觉得"，而是**顶级专业机构和 Vibe Coding 社区的实际做法**。

- **对标层次**：
  1. 先查 PS-STD-011 §3 专业框架映射表 → 找到对应框架
  2. 再查 Vibe Coding 社区前沿实践（Anthropic CLAUDE.md 规范、Cursor Rules 官方指南、Windsurf 社区最佳实践）
  3. 产出："专业机构是这么做的，我们的场景需要这样适配"
- **反模式**："我觉得这样写比较好"——没有机构对标的感觉判断不进入决策环节

### 7.5 思维模式速查（Thinking Pattern Quick Reference）

在以下场景中，AI 必须默认执行对应的思维模式。这些模式的方法论细节定义在 PS-STD-011（MTH-006~MTH-009）。

| 场景 | 触发条件 | 对应模式 | 核心操作 |
|------|---------|---------|---------|
| 始终 | 每次操作前 | MTH-014 AI受众自检 [MUST] | 自问：这个输出/文件/字段 AI 能零推理消费吗？格式够机器可读吗？——对标 §6.12 |
| 每次文件操作前 | 创建/移动/删除任何规则文件 | MTH-002 架构上下文自检 [MUST] | 定位架构层→查验架构完整性→探查该有样子→仅架构完整才操作 |
| 提案给 Owner | 任何时候给出方案/建议 | MTH-007 决策质量四问 [MUST] | 埋雷→容量→对标→建议，缺一问不提交 |
| 发现两个文件说同一件事 | 编号冲突、字段定义冲突 | MTH-008 SSoT 冲突裁决 | 时序→语义→先例→裁决，四步不可跳 |
| 审查任务快结束时 | "修完了，还有遗漏吗？" | MTH-009 补漏与终止双检 [MUST] | 对标补漏→够用判定→输出三栏（已覆盖/Backlog/不适用） |
| 规则体系发生变动后 | 新增/合并/重命名/重组文件 | MTH-010 规则体系架构审查 [MUST] | 四步审：名字=责任→责任声明→文件夹职责→专业对标 |
| 考虑删除文件时 | 提议或执行任何删除文件操作 | MTH-011 文件删除质量对比预检 [MUST] | 重复性验证→质量对比"谁更好"→逐块结论→决策，缺一步不删 |
| 定义/修改架构事实时 | 新增模块/属性/技术条目 | MTH-012 架构数据 Canonical SSoT 铁律 [MUST] | YAML 优先→先入库再写 Markdown→冲突时 YAML 为准 |
| 创建/修改代码目录时 | 在 src/ 下新建目录或模块 | MTH-013 双层对齐闸门 [MUST] | 代码→YAML (GATE-A) →MD (GATE-B)，三层必须同步更新 |
| 发现漂移/不一致时 | 枚举漂移、索引数字错误、幽灵引用 | MTH-015 漂移免疫自检 [MUST] | 追问"为什么漂移没被拦截"→ 治理执行层是否缺失 → §6.14 三层防御 |
| 遇到任何问题时 | 任何异常、矛盾、失效 | MTH-006 根源分析 [MUST] | 5 Whys → 治根判定 → 举一反三 |

> **大白话**：这六个模式就是你的"工具箱"——文件操作前过架构（MTH-002）、看病先问"哪里疼"（根源分析 MTH-006）、开药前想"副作用是什么"（埋雷检查 MTH-007）、两个科室抢一个病人时按"谁先接诊"判定（SSoT 裁决 MTH-008）、出院前问"还需要复查吗"（补漏+够用 MTH-009）、医院装修后验房（架构审查 MTH-010）。[MUST] 标记的必须执行。

---

## 8. 规则加载策略 — 三层记忆模型

> **对标**：Cursor Rules globs（`alwaysApply` vs `globs: "*.py"`，文件级自动过滤）+ Codified Context（arXiv 2602.20478，三层记忆：热记忆 ≤400 行 → 领域触发 → 冷记忆）+ Kubernetes RBAC（最小权限原则——只加载当前任务需要的规则）。
>
> 本策略的核心理念：**AI 是"按菜单点菜"，不是"把整个厨房搬上桌"。**

### 8.1 已经自动加载（热记忆）——但需自检

本文件 AGENTS.md 已被工具自动注入上下文，但注入副本可能是**旧版快照**（IDE 缓存滞后）。

**MUST**：每个新 session 启动后你必须立即执行 **准入校验（Admission Check）**：
1. 从磁盘重新读取 `D:\ZephyrAlpha\AGENTS.md`
2. 对比磁盘版 vs 注入版的 `版本：vX.Y.Z`（位于本文件第 3 行）
3. 若版本号不一致 → 以磁盘版为准，输出 `⚠️ AGENTS.md 版本漂移：注入版=vX.Y.Z, 磁盘版=vA.B.C，已切换至磁盘版`
4. 若磁盘读取失败 → 继续用注入副本，但提示 Owner 路径不可达

> **对标**：Kubernetes Admission Controller —— 任何进入集群的资源必须通过准入校验，AGENTS.md 注入也不例外。

### 8.2 按任务类型选择规则（领域触发）

> **全局强制**：以下所有任务类型，§6.12 AI受众优先原则**始终生效**（AI-First = 本项目头号宪法）。任何操作前 MUST 自问：**这个输出/文件 AI 能零推理消费吗？**

以下路径均为绝对路径，基于 `D:\ZephyrAlpha\docs\01_policies_and_standards\`：

| 你的任务 | 必须读的文件（只读这些） | Token 成本 | 禁止做的事 |
|---------|------------------------|:---:|---------|
| **修改/优化任何规则文件** | `meta/index.md` + `meta/glossary.md` + `meta/rule-lifecycle-and-change-standard.md` | ~2000 | ❌ 禁止全量读取 meta/ 下 12 个文件 |
| **创建新标准文档** | `meta/index.md` + `meta/glossary.md` + `meta/document-structure-standard.md` + `meta/metadata-registry.md` §1~§4 | ~2500 | ❌ 禁止读 PS-STD-003 行为边界全文——仅按需查对应 ABS/COND 条目 |
| **修改代码** | `meta/glossary.md` + `src/zephyr/shared/contracts/`；若修改 `scripts/governance/` 脚本 → 加读 `scripts/governance/quality-standard.md` | ~1500 | ❌ 禁止读 meta/ 其他规则文件——代码已有 pre-commit/CI 强制 |
| **修改 config/ YAML 或审计配置** | `_registry/catalogs/declarative-contract-tracker.yaml`（必须先读） + `capabilities.yaml` + `validate_config_integrity.py`（跑基线） | ~800 | ❌ 禁止信任 config/ 下所有 YAML 都是运行时配置——3/6 个是声明式契约（CT-001~CT-003），代码不读它们 |
| **审查规则体系一致性** | `meta/index.md` + `meta/glossary.md` + `meta/rule-classification-and-arbitration-standard.md` + `meta/rule-verification-standard.md` + `_registry/catalogs/rule-registry.md` | ~3500 | ❌ 禁止读 PS-STD-002 模板文件——审查读的是内容不是格式 |
| **运行项目审计/扫描检查** | `scripts/governance/index.md` | ~600 | ❌ 禁止跳过审计直接施工——先跑 run_all.py 看当前状态 |
| **查找/操作任何登记表/注册表** | `_registry/catalogs/registry-master-index.yaml` | ~800 | ❌ 禁止跨目录翻找 YAML——先查总索引再定位到具体登记表 |
| **了解未兑现的 YAML 承诺** | `_registry/catalogs/declarative-contract-tracker.yaml`（契约跟踪登记表） | ~500 | ❌ 禁止信任有 implementation_status 的 YAML 全部兑现——先查契约跟踪表确认 |
| **创建新脚本工具** | `scripts/governance/index.md` + `scripts/governance/script_manifest.yaml` + **`_shared/` API 速查（见 §8.2.1）** | ~1000 | ❌ 禁止创建脚本后不注册——违反 §6.5 入库强制约定 / ❌ 禁止本地重定义 `_shared/` 已有函数/常量 / ❌ 禁止创建新 GATE/门禁后不注册到 `gate-registry.yaml` + 同步 `registry-master-index.yaml` entry_count |
| **创建新门禁/GATE/钩子** | `gate-registry.yaml` + `registry-master-index.yaml`（REG-GATE-001）+ `.pre-commit-config.yaml` | ~800 | ❌ 禁止只加 pre-commit hook 不更新 gate-registry.yaml——三文件必须原子同步 / ❌ 禁止 entry_count 漂移——改完先数再写 |
| **创建/修改 CI pipeline 或基础设施配置** | `registry-master-index.yaml`（REG-INFRA-001）+ 对应登记表 | ~600 | ❌ 禁止创建 `.github/workflows/*.yml` 或 `.pre-commit-config.yaml` 等基础设施文件后不在 `registry-master-index.yaml` 中登记——对标 ITIL SACM：所有基础设施配置项必须注册到 CMDB / ❌ 禁止只改配置不更新 entry_count |
| **添加/修改 @pytest.mark 装饰器** | `pyproject.toml [tool.pytest.ini_options] markers` + `registry-master-index.yaml` → REG-INFRA-002 | ~400 | ❌ 禁止只加装饰器不注册 marker——`--strict-markers` 模式下会导致 CI 失败 |
| **不确定/未列出的任务** | `meta/index.md` + `meta/glossary.md`（最小对齐）→ **然后向 Owner 确认具体范围** | ~1100 | ❌ 禁止猜测任务类型后自行扩大读取范围 |

### 8.2.1 `_shared/` API 速查目录（创建脚本前 MUST 对照）

> **对标**：AGENTS.md §6.5 "先查后建" + SCRIPT-QUALITY-001 D-D-04（同一概念只在一处定义）
>
> 创建任何新 `.py` 脚本前，MUST 先检查以下 `_shared/` 模块是否已有等价实现。**如果本地重定义以下任何符号，你的脚本会触发 D-D-07 checker 违规。**

| 模块 | 导出符号 | 用途 | 不要本地重定义 |
|------|---------|------|:---:|
| `_shared.constants` | `REPO_ROOT` | 项目根路径 | 🔴 |
| | `EXCLUDE_DIRS` | 全局排除目录（如需扩展用 `EXCLUDE_DIRS \| {"extra"}`） | 🔴 |
| | `SCAN_EXTENSIONS_MD_YAML` | `.md/.yaml/.yml` 扫描扩展名 | 🔴 |
| | `SCAN_EXTENSIONS_CODE` | `.py/.yaml/.json/.toml/...` 扫描扩展名 | 🔴 |
| | `SCAN_EXTENSIONS_DOCS` | `.md/.yaml/.txt/.rst` 扫描扩展名 | 🔴 |
| | `GOV_DOCS_DIR` | `REPO_ROOT / "docs" / "01_policies_and_standards"` | 🔴 |
| | `SRC_DIR` | `REPO_ROOT / "src" / "zephyr"` | 🔴 |
| | `CONFIG_DIR` | `REPO_ROOT / "config"` | 🔴 |
| | `SCRIPTS_DIR` | `REPO_ROOT / "scripts" / "governance"` | 🔴 |
| | `MANIFEST_PATH` | `SCRIPTS_DIR / "script_manifest.yaml"` | 🔴 |
| | `find_repo_root()` | 通用项目根定位函数 | 🔴 |
| `_shared.encoding` | `ensure_utf8_stdout()` | UTF-8 stdout/stderr 强制声明（替代 inline `sys.stdout.reconfigure`） | 🔴 |
| `_shared.frontmatter` | `parse_frontmatter(content)` | Markdown YAML frontmatter 解析 → `Optional[dict]` | 🔴 |
| | `parse_frontmatter_from_file(path)` | 从文件路径解析 frontmatter → `Optional[dict]` | 🔴 |
| | `parse_yaml_header(content)` | YAML 文件注释头 + 顶层字段提取 → `Optional[dict]` | 🔴 |
| `_shared.walk` | `iter_files(root, extensions, exclude_dirs, exclude_files)` | 递归文件遍历（自动 EXCLUDE_DIRS 过滤）→ `list[Path]` | 🔴 |
| `_shared.yaml_utils` | `load_yaml(file_path)` | YAML 文件安全加载 → `dict/list/str` | 🔴 |
| `_shared.deprecated_paths.yaml` | 数据文件 | 废弃路径共享清单（`detect_ruins_references.py` 的输入） | — |

**惩罚机制**：如果你本地重定义了上述任何符号，以下两层会自动拦截：
- **D-D-07 checker**（`validate_script_quality.py`）：AST 级别逐符号检测，发现本地重定义 → CI 失败
- **Manifest Admission Controller**（`validate_manifest_admission.py`）：新脚本注册时联动触发质量扫描

### 8.3 不要主动读的文件（冷记忆）——遇到问题时再查

以下文件**除非任务明确提到**，否则不要主动加载：

| 文件 | 什么时候才读 |
|------|------------|
| `meta/governance-metrics-standard.md` | 月度度量报告时才读 |
| `meta/governance-methodology-standard.md` | 需要做方法论决策（MTH-001~010）时才查对应条目 |
| `governance/document/*` | 操作文档时才读 |
| `governance/ai/*`（除 onboarding-guide） | 涉及 AI 治理具体场景时才查 |
| `docs/03_modules/l01_infrastructure/audit-factory/blueprint.md` | 需要理解审计工厂架构设计时才读 |
| `docs/03_modules/l01_infrastructure/knowledge-base/blueprint.md` | 需要理解知识库架构设计、决策记录模型（§3.9.5）、来源矩阵（§3.9.1）时才读 |

### 8.4 如何找到不在表中的规则

如果任务过程中需要某个不在上述列表中的规则，依赖链（`depends_on`）会自动指引你找到它。所有规则文件的 frontmatter 中都有 `depends_on` 字段，声明了本文件引用哪些上游文件——像一条"线索链"，跟着走就能找到需要的东西。

> **大白话**：你就像去图书馆查资料——不是把所有书架逛一遍，而是先看"任务菜单"（§8.2），找到你该去的那个书架，拿 2-4 本书。其他书放在那里——如果真需要，书里会写着"参考文献见 XX"（depends_on），跟着找就行。这样你每次进来只需要读 2000-4000 字的规则，而不是 15000-20000 字——省下的脑力全用在干活上。
