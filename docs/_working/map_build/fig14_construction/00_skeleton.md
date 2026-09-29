---
ttl: task_bound
completes_when: 图14 封矿且 config/construction_workflow_map.yaml 四件套（生成器+图 YAML+步骤锚校验器+MAP-ALIGNMENT 子台+挂轴）落地后本件退役为归档参考
title: 图14 AI 施工升级流图·环节总骨架（00_skeleton，本图唯一收敛基准）
owner: st-mapbuild-20260924
---

# 图14 AI 施工升级流图 00_skeleton

> 一句话域：**一个施工任务从"冷启动+文档审查"到"验收+全景图转正"的任务序（step 序）与每步的可验锚**——不管改动如何到达 dev（那是图11），不管运行时模块归属（那是 GOMAP）。
> 本图域的**唯一现行真源** = `docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md`（下称 **policy**，v1.7.2 / 2026-09-15）。骨架的工作不是重写它，是**逐步核它声称的东西在仓库里是否真实存在**，并把"每步可机验"从散文变成规格（规格=本文件夹 `90_step_anchor_validator_spec.md`）。
> 本件=环节全集 + 三态计分板 + 路由表 + 红条目点名册。环节编号 `D14-*` 一经定稿即契约，作业簿标题必须引用。
> 状态纪律=`sop/mining_sop/skeleton_mining_policy.md` §5：**✅ 必附实查路径/命令/行号**，凭印象标 ✅=审计事故。本件所有行号均为 2026-09-24 在 worktree `.aidrafts/st-mapbuild-20260924` 上实测（复核命令见 §7）。
> **本骨架的诚实结论**：policy 自述"15 步"，实测 **17 个 Step 段**；17 步中**真有机验锚 6 / 锚半断 7 / 无机验面 4**，可机验分解为 **yes 6 / partial 6 / no 5**。红条目总表 **R-01~R-18 共 18 条**：其中"**文档说有、实则不存在**"9 条（R-01/03/04/05/06/07/08/09 + R-11 的上游真源整体归档 12 处链接）、真源已废弃 1 条（R-10）、行号锚 **7/7 全失效**（R-13）、gate 实名漂移 1 条（R-14）、矩阵与正文不一一映射（R-15）、域宽自相矛盾（R-16）、计数漂移 4 类（R-02/12/17/18）。**因此四道门第④门目前不过**——建图前必须先立步骤锚校验器（块B，见 `90_step_anchor_validator_spec.md`）。

## §0 域定义与四道门实证（裁定#409 一域一图准入四问）

**域职责**：管"施工任务的时间序 + 每步的通过判据 + 失败回哪一步"。policy L39 自述性质=**编排层**（"只串联流程+引用真源规则，不重复规则内容"），L77-79 三条定位（不重复规则/只编排/每步指向真源路径）——**这三条正是本图 INV-1 纪律（图只存 step_id+引用，不复制政策正文）的政策依据**。

### 门① 独立触发与终点

| 项 | 实证 |
|---|---|
| 触发 | 新 AI session 接施工任务：policy L107「Step 0 何时触发：任何新 AI session 开始施工前」；L177「Step 1 何时触发：施工 AI 接到施工任务后第一步」；宪法冷启动序列 §0 第 4 步 RULE-CAPABILITY-LOOKUP 明文"施工/新模块另必读 construction_workflow_policy" |
| 终点 | L708-722 Step 12（merge 回 dev + cleanup）；宪法 §2 第 9 条会话收尾序列（merge 回主分支→release 全部 claim→staging promote→handoff→汇报） |
| 中间有独立状态机？ | 是——17 个 Step 段全部具备 7 个统一粗体字段（何时触发/前置条件/操作摘要/引用真源/通过判据/不通过处置/产出物），实测 17/17 覆盖率 100%（解析脚本见 §7-C1）。**这就是步骤锚的天然结构**：字段齐但值不可机验 |
| 域边界自相矛盾（**红条目 R-16**） | frontmatter L13 `scope: global` vs L40 适用范围"**仅**交易决策域施工……数据层/基础设施/治理脚本走全局规则" vs L812-814 §5.2 再次收窄。**图14 建图必须先裁域宽**：若按 global，本图覆盖全部施工（含图11/图12/图16 车道）；若按 L40 则只覆盖 07 域。本骨架按 **L40 收窄口径**建（否则与图11/12/16 全域撞车），并把矛盾列总包收口请求 §X-1 |

### 门② 跨模块交接（本域是一条流程线而非一堆散件的证明）

| 交接边 | 上游→下游 | 证据（文件:行） |
|---|---|---|
| J1 | Step 2 → Step 3：depgraph planned 节点 → sync 派生三图 → align 验证 | policy L279-281（apply_depgraph --add-design-node/--add-edge）→ L307-310（sync_panorama_module --all / align_all）；实存 `scripts/governance/apply_depgraph.py`、`scripts/governance/sync_panorama_module.py`（`--all` flag 实测在，§7-C4） |
| J2 | Step 3/8 → 七图体系：align_all 单入口聚合九节 | `scripts/governance/d5_architecture/generators/align_all.py`（701 行；第七/八/九节=图 8/9/10，L551/L581/L613）；`alignment_checklist.md:79` |
| J3 | Step 5 → Step 10：循环验收轮次由任务卡状态机强制 | `src/zephyr/governance/persistence/task_repo.py:667 CIRCULAR_ACCEPTANCE_ROUNDS: Final[int] = 2`（政策 L426/L443 引用同一常量） |
| J4 | Step 10 → 门禁链：99 个 in-process gate + 180 台 pre-commit 登记 | `in_process_gate_registry.yaml:41 total_gates: 99`（实测 `grep -c '^- gate_id:'`=99）、`gate_registry.yaml:8 total_gates: 174`（实测条目 180，册内字段自述 174——**R-17 册字段与条目数已不一致**，勿背数） |
| J5 | Step 1.8 → Owner 门位：架构评审"必须由 Owner 亲自执行或书面委托" | policy L229；`risk_tier_registry.yaml`（AGENTS §5.2 high 域门位） |
| J6 | Step 1.9 → mining_sop / skeleton_mining_policy | policy L249-252；实存 `sop/mining_sop/mining_sop_policy.md`、`sop/mining_sop/skeleton_mining_policy.md`、`sop/mining_sop/trading_decision_map_pathfinding_policy.md` |
| J7 | Step 3.5 → 前端拆件闭环（"有得拆"转 8 步 SOP 再回 Step 4） | policy L351；实存 `sop/construction_sop/frontend_component_split_policy.md`、`rules/trae_086_frontend_module_construction.yaml §truth_source_wiring/§split_judgment`（两锚实测在，§7-C5） |
| J8 | Step 8/10 → post-commit reconciler 链（40+ 声明） | `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:1547 _register_default_reconcilers`；`reconciliation_registry.py` 内 `gate_id=` 声明 78 处（图11 D11-C11 实测 register 调用 58 处）——"40+"口径成立但**政策给的行号 L783 已偏 764 行**（R-13） |

### 门③ 不被现有图覆盖（与图11 的切分线实证）

**切分线（本骨架的判定）**：**图11=改动如何到达 dev 的机制流（锁/快照/队列/落地/对账）；图14=施工任务的次序与每步判据（设计→验收）**。这条线在政策原文里自带证据，不是本会话的发明：

| 证据 | 原文（逐字） | 出处 |
|---|---|---|
| E1 | `\| Step 10 GitCommitGateway 落地 \| 66_commit_queue_serialization / trae_075 / trae_084 \| 不重复，引用 \|` | policy L99 |
| E2 | `\| Step 12 worktree 合并与清理 \| trae_078 / trae_076 / project_memory session_worktree 教训 \| 不重复，引用 \|` | policy L101 |
| E3 | Step 11 引用真源=trae_071/trae_035 清扫三步法（临时文件生命周期机制，属图11 车道①） | policy L668 |
| E4 | 图11 骨架已双向认领此线：`construction_workflow_policy 15 步不承载……15 步域=单个施工任务的生命周期，其落地两步明确转引本域真源` | `docs/_working/map_build/fig11_delivery/00_skeleton.md:46`、`:115` |
| E5 | GOMAP 边界排除开发时流水线：`out_of_scope_refs: 提交门禁体系 / note: 门禁是每模块配套,非运行时流水线节点` | `config/governance_operations_map.yaml:17-19`；GOMAP layers=GOM-L0..L6 全为**运行时**治理模块装配（同文件 L28-），实测 17 步的 Step 段在 GOMAP 中零出现（grep 无命中） |

**切分成立，但必须钉死三条硬边界（否则本图就是第二真源）**：

1. `D14-01`（Step 0）、`D14-14`~`D14-17`（Step 9/10/11/12）在本图只能是**交接锚（handoff node）**：只存 step_id + 「机制真源在图11 的哪个环节编号」的引用，**禁**复制 claim/lock/queue/merge 的机制描述（宪法 §4 内收判据"同真源可派生→必并"）。
2. 本图独有段=Step 1~8 及其子步（1.5/1.8/1.9/3.5），共 12 个节点，**图11 无对应物**（图11 28 环节=D11-S01..S09 会话车道 / D11-C01..C13 提交流 / D11-D01..D06 死信，均为机制环节，无"设计/审查/验收/文档转正"语义）。
3. 与 battle_map 的 `step_id` 轴**不得复用**：`battle_map_domain_policy.yaml` 的 `flow_stage_allowed_domains` 键=stock_selection/buy_flow/position_management 等**交易阶段**（L45-），BM-INV-004 会按域清单判红施工步骤（详见 §3 旁轴 O4）。故本图自建 `D14-*` 前缀轴。

### 门④ 机生真源可建性 —— **当前不过**

| 项 | 实证 |
|---|---|
| 有没有步骤登记面？ | **没有**。全仓 75 个 catalogs 中无任何以"施工步骤"为条目的册（`ls docs/01_policies_and_standards/_registry/catalogs/`，grep `step_id` 仅命中 architecture_issue/battle_map_domain_policy/capability_canonical/module_translation/ruling 五册，均非施工步骤宿主；`rule_catalog_registry.yaml:2007-2021` 对本 policy 只有一行文档级条目且 `section_count: 0`） |
| 政策声明的锚可用吗？ | 不能全用：17 步中 9 步给了 powershell 命令块（实测 §7-C2），8 步只给"执行要点"散文；9 个命令块内含 **5 条命令/flag/子命令实不存在**（R-01/R-03/R-04/R-06/R-07） |
| 有没有可机验的字段枚举？ | 有——`verifiability` 受控词表（`_registry/vocabularies/verifiability_vocabulary.yaml:30-36`：automated/manual/inspection 三值），policy frontmatter L5 现值 `manual`。步骤锚的 `verifiable` 字段直接复用该词表，零新册零新枚举（满足全资产净零） |
| 结论 | **先立校验器再建图**（普查 §4 L58 判定成立）。规格见 `90_step_anchor_validator_spec.md`：校验面=政策 MD 内嵌机读锚块（唯一真源）→ 生成器抽图 → `validate_construction_steps.py` 双向一致 + 锚磁盘实存 + gate 在册 + 回边无环 + INV-1 不复制正文。四道门第④门在锚块落地并由 MAP-ALIGNMENT 聚合台封住后方可转"过" |

## §1 环节全集（17 环节 = policy 17 个 Step 段，编号 D14-01 起）

**列口径**：
- **状态**：✅=政策声明的锚在本仓实存且可跑/在册（附实查）；🔨=有真源但断链或需补锚；⬜=无任何机验面。
- **可机验否**：yes=该步通过判据可由既有脚本/门禁直接判定；partial=部分子项有机验面，主判据仍人工；no=判据落在"对话内"或纯人工，结构性无机验面。
- 「本图角色」：内=图14 独有节点；**交接**=只存引用，机制真源在图11。

| 环节编号 | 环节名（Step） | 段 | 本图角色 | 状态 | 真源映射（policy 锚点 + 实测脚本/门禁路径:行） | 可机验否 |
|---|---|---|---|---|---|---|
| D14-01 | Step 0 Session 冷启动（policy L105-173） | 前置 | 交接 | 🔨 | policy L115 `lock_files.py cleanup`✅（`scripts/lock_files.py:1626 cmd=="cleanup"`）；L116/118 `scripts/ide_health_service.py` ❌**全仓无此文件**（R-01）；L136 "46 个门控检查"❌ 实测 58（R-02）；**真锚未被政策指认**=`scripts/governance/meta/session_startup_check.py`（CLI `--json/--phase`，L20-22）→ `src/zephyr/governance/ops_governance/phase_manager.py`（`PHASE_SEQUENCE` 内 `"gate_*"` 字符串实测 58 个唯一）；L161 handoff 目标 `.runtime/handoffs/handoff_<sid>.json`（图11 D11-S09 实测在盘非空）；L171 `bare_getenv_gate` ✅`src/zephyr/gov_enforcement/commit_gates/bare_getenv_gate.py` | partial |
| D14-02 | Step 1 文档审查（L175-192） | 前置 | 内 | ⬜ | policy L180 真源 `docs/_archive/AI_review_instructions.md`：文件✅在，但 `status=deprecated`＋文首"2026-08-28 Owner 裁定归档不删，**后续不再更新**；现行治理规则真源=construction_workflow_sop + 68 号代码算法审查流水线 active 机制"（R-10）；68 号设计文档也已归档（`docs/_working/archive/2026-09/design_memos/68_code_algorithm_review_pipeline.md`）而其实现✅活（`src/zephyr/gov_enforcement/behavioral_admission/code_review_ai.py` + `tests/audit/quality_static/test_code_review_ai.py`）；产出物=对话内（L184 明禁创建报告文件）→ **无留痕面** | no |
| D14-03 | Step 1.5 创建前搜索（L194-211） | 前置 | 内 | 🔨 | CAPABILITY-LOOKUP-REQUIRED gate ✅在册（`in_process_gate_registry.yaml`/`gate_registry.yaml` 各 1 条）；trae_056 §phase_1_search ✅（`trae_056_module_creation_workflow.yaml`）；trae_002 **§rule_eight ❌ 该 YAML 无此锚**（其 sections 仅 `anti_orphan`/`search_first`，R-09）；REUSE-DECISION 标注=对话内无面 | partial |
| D14-04 | Step 1.8 架构评审门控（L214-242） | 判定 | 内 | ⬜ | trae_036 §gov_arch_002 ✅、trae_049 OPS-DEV-002 ✅、trae_017 ✅；policy L228 落盘路径 `docs/_working/audit/architecture-reviews/` ❌**目录不存在**，实际在 `docs/_working/archive/2026-09/audit/architecture-reviews/`（仅 2 条记录，最新 2026-09-15）（R-11）；L229 "Owner 亲自执行或书面委托"=人门位 | no |
| D14-05 | Step 1.9 方案挖矿（L245-266） | 判定 | 内 | ⬜ | 真源三件✅在（mining_sop_policy/skeleton_mining_policy/TDM_pathfinding_policy）；但"挖矿日志 MUST 写进方案'挖矿增补'章节"（L257）**零 checker**——全仓 `挖矿增补` 无任何 .py 命中（§7-C6），仅 7 篇 MD 提及；无 checker ⇒ 无法机械判"无日志=没挖过" | no |
| D14-06 | Step 2 全景图登记（设计态先行）（L269-294） | 设计登记 | 内 | ✅ | `apply_depgraph.py --add-design-node`/`--add-edge` ✅实测在册（§7-C4）；gate `DEPGRAPH-ENFORCEMENT`/`DEPGRAPH-PRE-REGISTRATION`/`NEW-FILE-DEPGRAPH-ENFORCEMENT` ✅在册；`generate_project_depgraph.py:3368 restore_design_data` ✅函数在（政策写 L3094，R-13）；L291/L971 `--query-production` ❌**flag 不存在**（R-04）；L284 准入记录 `module-id-registry.json admission_records` ❌**全仓无此文件**（R-05，trae_032 另六处同源声明 L63/84/245/514/571/583）；L817 "trae_056 10 phase" vs 实测 phase_0~phase_10=11（R-12） | yes |
| D14-07 | Step 3 全图全库对齐（L297-329） | 设计登记 | 内 | ✅ | `sync_panorama_module.py --all` ✅、`align_all.py` ✅（九节，L551/581/613）；gate `MAP-ALIGNMENT` ✅在册且**聚合 6 子台**（`panorama_alignment_gate.py:282 make_map_alignment_gate`、`:295-302 subs`、`:319 priority=141`、`in_process_gate_registry.yaml:301-307` files_trigger 触发式）；policy L313-320 "七图定义"vs `alignment_checklist.md:65` "现 10 张"（R-12）；附录 A.13 L985-995 仍写"五图对齐 7 项"未随七/十图升级（R-12） | yes |
| D14-08 | Step 3.5 后端盘点与拆件判定（L331-356） | 设计登记 | 内 | 🔨 | `trae_086 §truth_source_wiring`+`§split_judgment` ✅（实测两锚命中）；`frontend_component_split_policy.md` ✅；`data_asset_registry.yaml` ✅；`web/frontend_map.yaml` ✅；gate `FRONTEND-TRUTH-SOURCE` ✅在册但 policy L341 自述 **warn 兜底**（不阻断）；拆件判定"留痕"无指定结构化落点（L356 说"进设计备忘或验收单 ACC-*.yaml"，而设计备忘体系已归档，R-11） | partial |
| D14-09 | Step 4 施工编码（L358-408） | 施工 | 内 | ✅ | 文件头 15 字段清单与 `trae_047:48 §A_full` **逐字段一致**（实测比对）；gate ✅：`BLUEPRINT-HEADER`/`BLUEPRINT-FORMAT`（inproc L363/376）、`GIT-CALL-BUDGET`（L415）、`FOLDER-CAPACITY-HARD-LIMIT`（L453）、`COMPLEXITY-GUARD`（L333）；`GitCommandBatcher` ✅`src/zephyr/infrastructure/git_batcher.py`；`scripts/git_guard.py` ✅（DANGEROUS_SUBCOMMANDS 七项含 reset/checkout/clean，L90）；`scaffold.py` ✅；trae_032 MAD-001~005 ✅锚在；trae_034/003/004/006/010/063/066/082 文件全在 | yes |
| D14-10 | Step 5 单元测试+循环验收（L411-452） | 验收 | 内 | 🔨 | `CIRCULAR_ACCEPTANCE_ROUNDS=2` ✅代码常量在（`task_repo.py:667`）但**仅在任务卡 COMPLETED 转换上强制**——无任务卡的施工不触发；gate `TEST-SOURCE-CONSISTENCY` ✅（inproc L357）、`TEST-RESIDUE-SSOT` ✅（L561）；`trae_071 §test_residue_reclaim` ✅且**行号 L414 准确**（全 policy 唯一命中锚）；GATE-RUNTIME-CLEANUP ✅是 reconciler 非 gate（`reconciliation_registry.py:7678/7844`），政策 L448 称"post-commit reconciler 兜底"口径正确；政策 L441 官方词表 `zephyr.shared.vocab.market_state` + `EXTREME_STATE_ALIASES` ❌**模块不存在**（无 `src/zephyr/shared/vocab/`；该路径仅在 `commit_gates/library/state_vocab_registry_gate.py:184` 的注释里被提及），而 `docs/_working/vocab_legislation/01_official_state_vocabulary.md:15` 自称"W1 已建成"（R-08） | partial |
| D14-11 | Step 6 长清单审查（L455-480 + 附录 A L852-1014） | 验收 | 内 | ⬜ | 清单真源=政策自身附录 A（A.0~A.14，实测 14 节齐）；基座 `trae_081` 54 维度 ✅（实测 `grep -c` =54，与政策 L460 一致）；但 L465"审查结论在对话内给出，禁止创建报告文件"⇒**结构性无机验面**（与门④直接冲突，需裁定，见总包收口 §X-5）；漂移套件✅六件全在（`check_contract_code_drift.py`/`validate_load_path_integrity.py`/`d1_structure/validate_config_integrity.py`/`d2_links/`/`d4_paths/`/`d9_knowledge/`）；遗留项登记目标 `design_memos/construction_progress_tracker.md §六` ❌旧路径失效，实际 `docs/_working/archive/2026-09/design_memos/construction_progress_tracker.md:176`（§六标题实存，R-11） | no |
| D14-12 | Step 7 更新施工文档（L482-507） | 文档 | 内 | 🔨 | gate `TTL-METADATA` ✅在册、`FILE-PLACEMENT-TTL` ✅；`d8_doc_sync/validate_document_lifecycle.py` ✅、`update_progress.py` ✅、`auto_sync_all_registries.py` ✅；trae_052 §rule_eleven ✅、trae_030 GOV-DOC-011 ✅、trae_029 GOV-DOC-007 ✅、trae_037 GOV-ARCH-003 ✅；**但管理上游 `01_design_memo_management_spec.md` 与同步目标 `00_index_trading_decision.md` 均已归档**（`docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/README.md:1-14`：裁定#384 WO-14 于 2026-09-20 将 49 件归档至 `_working/archive/2026-09/design_memos/`，仅 `16_technical_indicator_catalog.md` 留置，台账 `docs/_working/code_doc_gov_campaign/p3_placement/w14_placement_ledger.md`✅在）（R-11） | partial |
| D14-13 | Step 8 全景图状态流转（L511-565） | 文档转正 | 内 | ✅ | `apply_depgraph --transition-design-maturity`/`--transition-build-status` ✅两 flag 实测在册；`generate_battle_map_diagram.py` ✅；`generate_project_path_tree.py --write` ✅；`align_all.py` ✅；gate `DEPGRAPH-FRESHNESS` ✅在册；**L558/L1038 `scripts/governance/diagnose_depgraph.py` ❌该路径不存在**，实际 `scripts/governance/d5_architecture/diagnose_depgraph.py`（R-03）；worktree 分流"只登记不流转 + merge 执行人实证核验双态"（L519-528）无任何自动面（人工职责） | yes |
| D14-14 | Step 9 文件完整性检查（L568-600） | 落地收尾 | 交接 | 🔨 | 命令=`git status`/`git diff --cached --stat`（纯人工读）；`session_worktree.py status` ❌CLI 无 status 子命令（R-06，库函数在 `rule_bridge/session_worktree.py:7668`）；`lock_files.py status` ✅（L1571）；机制真源已由图11 承载=D11-C11 post-commit 对账 + D11-S07 pre-merge topo check（`fig11_delivery/00_skeleton.md` §1）；`workspace_governance_policy.md` ✅、`scripts/rollback.py` ✅、`65_git_safety_governance.md` ❌已归档（R-11） | no |
| D14-15 | Step 10 GitCommitGateway 落地（L603-660） | 落地收尾 | 交接 | ✅ | **L613 `python scripts/git_commit_gateway.py` ❌该脚本不存在**（R-03；实际正门=`scripts/git_commit.py`，AGENTS §2.1，图11 D11-C01）；`session_worktree.py commit <sid> "msg"` ❌CLI 无 commit 子命令（R-06）；关键 gate 清单逐条核：HELD-OVERLAP✅/CLAIM-REQUIRED✅/WORKTREE-REQUIRED✅/FOREIGN-CHANGE✅(仅 inproc，gate_registry 无同名)/COMMIT-SCOPE✅/DIRECTORY-CONTRACT✅/TTL-METADATA✅/FILE-PLACEMENT-TTL✅/RENAME-DEPGRAPH-SYNC✅(仅 pre-commit)/BLUEPRINT-NODE-ID-HARDCODE✅/CAPABILITY-LOOKUP-REQUIRED✅/TEST-RESIDUE-SSOT✅/TEST-SOURCE-CONSISTENCY✅/PURE-SHIM✅/STASH-ACCUMULATION✅；`SECRET-HARDCODE` ❌实名 `NO-SECRET-HARDCODE`（R-14）；"100 个 in-process gate"vs `total_gates: 99`（R-12）；机制真源=图11 D11-C01..C13 | yes（本图不重述） |
| D14-16 | Step 11 临时文件清理（L663-705） | 落地收尾 | 交接 | 🔨 | `make_session_staging_lifecycle_reconciler` ✅在且 priority=802 口径与政策 L681 一致（`reconciliation_registry.py:10988`、注册注释 :179）；`lock_files.py release <sid>` ❌**参数元数不符**（实际 `release <file> <owner>`，L1616；意图对应=`release-all <owner>` L1620）（R-07）；`session_worktree.py mark-completed <sid>` ❌**CLI 与库函数全仓均无**（R-06）；`trae_070 DCR-008`✅、`gate GATE-DIRECTORY-CONTRACT`→ 册内实名 `DIRECTORY-CONTRACT`✅ | partial |
| D14-17 | Step 12 worktree 合并与清理（L708-778） | 落地收尾 | 交接 | ✅ | CLI 子命令实测=`create/exec/merge/abort/list`（`scripts/session_worktree.py:651-685`）⇒ `merge <sid>` ✅、`cleanup <sid>` ❌（R-06，实际 abort）；`session_worktree_abort` ✅实存 L7497（政策 L748 写 L8037，偏 -540，R-13）、`session_worktree_sweep` ✅实存 L2194（政策 L755 写 L2163，R-13）；`_ACTIVITY_IDLE_TIMEOUT_SECONDS` ✅在 `session_concurrency.py`（图11 D11-S03 实测 :148）；`heartbeat_daemon.py` ✅`src/zephyr/gov_enforcement/rule_bridge/`；trae_078/076/074/075 ✅文件全在；`merge_conflict_resolution_policy.md` ✅、`branch_strategy_policy.md` ✅ | yes（本图不重述） |

**计分板（本图唯一计分面）**：

| 维度 | 计数 | 说明 |
|---|---|---|
| 环节总数 | **17** | policy `^### Step` 实测 17（标题与 §3 章名均写"15 步"=R-12） |
| ✅（锚实存在册） | **6** | D14-06/07/09/13/15/17 |
| 🔨（有真源但断链/需补锚） | **7** | D14-01/03/08/10/12/14/16 |
| ⬜（无任何机验面） | **4** | D14-02/04/05/11 |
| 可机验 yes | **6** | D14-06/07/09/13/15/17 |
| 可机验 partial | **6** | D14-01/03/08/10/12/16 |
| 可机验 no | **5** | D14-02/04/05/11/14 |
| 本图独有（内） | **12** | D14-02~D14-13（除 D14-01） |
| 交接锚（机制归图11） | **5** | D14-01/14/15/16/17 |

> 计数纪律：上表 ✅+🔨+⬜=17 的分解为 ✅6 / 🔨7 / ⬜4；"可机验"三分解为 6/6/5。**同一环节可以是 ✅ 但 partial**（如 D14-06 的 depgraph 锚在、但同段的准入锚是幽灵）——两列口径独立，勿合并解读。

### 红条目点名册（"文档说有实则没有/断"——骨架存在的唯一理由）

| # | 类 | 断点 | 政策出处（行） | 实测结论 |
|---|---|---|---|---|
| R-01 | 命令不存在 | `python scripts/ide_health_service.py --status/--start` | L116/L118 | 全仓 `find -iname "*ide_health*"` 零命中；仅 5 份文档引用同一幽灵脚本（含 project_rules.md、trae_053/056/067） |
| R-02 | 计数漂移 | "Phase Manager 检查（当前施工阶段 46 个门控检查）" | L136 | `phase_manager.py` 内 `"gate_*"` 实测 **58** 个唯一名；模块 docstring 自述"三阶段 51 检查"——三个数互不相同；且真正的可跑入口 `scripts/governance/meta/session_startup_check.py` 政策**完全未提** |
| R-03 | 路径失效 ×2 | `python scripts/git_commit_gateway.py`；`python scripts/governance/diagnose_depgraph.py`（含 frontmatter related_modules L28） | L613/L558/L1038/L29 | 前者不存在（正门=`scripts/git_commit.py`）；后者实际在 `scripts/governance/d5_architecture/diagnose_depgraph.py` |
| R-04 | flag 不存在 | `apply_depgraph --query-production`（L2 铁律的执行手段，两处声明） | L291/L971 | `apply_depgraph.py` 全部 `--*` 选项实测无此选项；⇒ "写入设计态前确保运营态已就绪"这条铁律**没有可执行工具面** |
| R-05 | 记录面不存在 | 准入记录写入 `module-id-registry.json admission_records` | L284（trae_032 L63/84/245/514/571/583、trae_056 L288 同源） | 全仓无 `module-id-registry.json`；近似面 `architecture_model/module_id_registry.yaml` 无 `admission_records` 字段（grep 零命中）⇒ MAD-001~005 四级筛选**留痕无处可落** |
| R-06 | CLI 子命令不存在 ×4 | `session_worktree.py status/commit/mark-completed/cleanup` | L585/L615/L688/L722 | CLI 实测仅 `create/exec/merge/abort/list`（`scripts/session_worktree.py:651-685`）；`status`/`commit` 有库函数（`rule_bridge/session_worktree.py:7668/:4580`）但 CLI 未暴露；`mark-completed` 全仓零命中 |
| R-07 | 命令契约错 | `lock_files.py release <sid>` | L685 | 实际 `release <file> <owner>`（`lock_files.py:1616`，需 ≥3 参）；意图命令=`release-all <owner>`（:1620）。照抄政策命令必失败 |
| R-08 | 词表模块不存在 | `zephyr.shared.vocab.market_state` 四轴常量 + `EXTREME_STATE_ALIASES` | L441 | 无 `src/zephyr/shared/vocab/` 目录；`EXTREME_STATE_ALIASES` 仅出现在 3 份 MD（本 policy + vocab_legislation 两卷），零 .py 命中；而 `docs/_working/vocab_legislation/01_official_state_vocabulary.md:15` 自称"**W1 已建成**"——**双册同谎**，属验收不通过级事故候选（本车道只点名不修） |
| R-09 | 引用锚不存在 | `trae_002 §rule_eight` | L199 | `trae_002_anti_orphan_search_first.yaml` 的 sections 仅 `anti_orphan`/`search_first`，全文件无 `rule_eight` 字串 |
| R-10 | 真源已 deprecated | Step 1 真源 `AI_review_instructions.md` | L180/L42/L68 | 文件在 `docs/_archive/`，frontmatter `status=deprecated`，文首 Owner 裁定"归档不删、后续不再更新"并指后继="本 SOP + 68 号审查流水线"；68 号设计文档亦已归档（实现 `code_review_ai.py` 活）⇒ Step 1 的 12 节审查清单**无现行真源** |
| R-11 | 上游真源整体归档（最大面） | `01_design_memo_management_spec.md`（frontmatter `depends_on` 首位=L15，正文 L41/L52/L71/L487 引用）、`65_git_safety_governance.md`（Step 9 真源 L98/L573/L592）、`66_commit_queue_serialization.md`（Step 10 真源 L99/L608/L654）、`construction_progress_tracker.md`（Step 6 遗留项登记目标 L470）、`00_index_trading_decision.md`（Step 7 同步目标 L492/L498） | L15/L41/L98/L228/L470/L487/L492/L573/L608 | 五件**全部**于 2026-09-20 依裁定#384（WO-14 包①）迁至 `docs/_working/archive/2026-09/design_memos/`（该目录实测 49 件；`07.../design_memos/` 现仅剩 README.md + 16 号）；SOP v1.7.2（2026-09-15）早于归档 5 天，**未跟进**；blast radius：全仓 62 个文件仍引用旧 `07_trading_decision_architecture/design_memos` 路径 |
| R-12 | 计数漂移（散文写死数） | "15 步"（L6/L36/L38/L103）／"13 项"（L782）／"84 个 trae_xxx"（L38/L61）／"100 个 in-process gate"（L638）／"七图"（L297/L313）／"五图对齐 7 项"（L985-995）／"trae_056 10 phase"（L66/L817/L835） | 如左 | 实测：**17** 个 Step 段／**16** 行 Checklist／**86** 个 trae_*.yaml／**99** 个 in-process gate／**10** 张全景图／trae_056 实有 phase_0~phase_10 共 **11** 个 phase（且同时存在 `phase_2_design_state` 与 `phase_2_design_node` 两个 phase_2 键=锚二义）。宪法 §4.3"计数用字段勿写死散文"在本 policy 全文违反 |
| R-13 | 行号锚系统性失效（7/7 全偏） | `boot_sequence L88`／`register_boot_hooks L579`／`HookRegistry L73`／`restore_design_data L3094`／`_register_default_reconcilers L783`／`session_worktree_abort L8037`／`session_worktree_sweep L2163` | L143/L146/L160/L293/L641/L748/L755 | 实测：L98 / L629 / L75 / L3368 / **L1547** / **L7497** / L2194。唯一准确锚=`trae_071 §test_residue_reclaim L414`（✅）。⇒ 规格必须**禁行号锚，改符号锚**（块B CV-09） |
| R-14 | gate 实名漂移 | Step 10 清单里的 `SECRET-HARDCODE` | L640 | 两册实名均为 `NO-SECRET-HARDCODE`；另 `FOREIGN-CHANGE`/`NEW-FILE-DEPGRAPH-ENFORCEMENT`/`RENAME-DEPGRAPH-SYNC` 只在一册在册（跨册命名面不齐） |
| R-15 | 矩阵与正文不一一映射 | §2.3 关系矩阵（L83-101）17 行，含"Step 1 前置·地图逐层讨论闸"一行，**但没有 Step 3.5 行**；正文 17 个 Step 段 | L83-101 vs L105-778 | 无法机械比对"矩阵声称的引用真源"与"正文各段引用真源"是否一致——**这正是步骤锚缺失的直接后果**，也是块B CV-11 的靶子 |
| R-16 | 域宽自相矛盾 | frontmatter `scope: global` vs 正文"仅交易决策域施工" | L13 vs L40/L812-814 | 已在 §0 门① 展开并取图14 收窄口径；总包收口 §X-1 |
| R-17 | gate 册自述计数与条目不符 | `alignment_checklist`/政策引用的 gate 数口径 | `gate_registry.yaml:8 total_gates: 174` | 实测 `grep -c "^- gate_id:"`=**180**（同文件，generated_at=2026-09-22）⇒ 册字段本身已漂移；本图校验器一律读条目集合，不读 total 字段 |
| R-18 | 战役共识件与规则锚字段数不符 | 共识件 §5④"gate 需 14 字段头标注" vs `trae_047:48 §A_full` 定义 **15 字段** | `docs/_working/map_build/00_campaign_brief.md:86` | 图 9 gate 实测头部 18 行（15 规范字段 + `[A_module]`/`[ARCH-REF]`/`[CREATION-TOKEN]`）⇒ 施工期照 trae_047 的 15 字段做，勿照"14"；请总包纠共识件措辞 |

## §2 17 步的分层与回边（循环在哪、失败回哪）

### 2.1 段分层（五段，MECE）

| 段 | 环节 | 段职责（一句话） | 段的出口判据 |
|---|---|---|---|
| 前置段 | D14-01/02/03 | 会话就绪 + 任务文档可施工 + 不重复造轮子 | 守护/门控 GREEN + 审查无 GAP 或 GAP 已登记 + [REUSE-DECISION] |
| 判定段 | D14-04/05 | 要不要动架构（人门位）+ 有没有挖干的方案 | Owner 评审记录落盘 + 挖矿日志齐全 |
| 设计登记段 | D14-06/07/08 | 先登记后施工 + 全图对齐 + 前端数据真源盘点 | depgraph planned + align_all exit 0 + 拆件判定留痕 |
| 施工+验收段 | D14-09/10/11 | 落码 + 循环验收 + 14 节对抗审查 | 连续 2 轮 0 错误 + 12(14) 节全 PASS |
| 文档转正段 | D14-12/13 | 文档↔代码对齐 + 全景图双态流转 | 备忘/索引三处对齐 + diagnose exit 0 |
| 落地收尾段 | D14-14/15/16/17 | 完整性 + 提交 + 清理 + merge（**机制归图11**） | commit hash + release 完 + merge 成功 |

### 2.2 回边全集（政策原文逐条实证，块B 的回边合法性真源）

| # | 回边 | 政策原文锚 | 性质 |
|---|---|---|---|
| B1 | Step 1 GAP → 回讨论环节（出图，回 design_memo） | L187"回讨论备忘补齐施工算法/接口签名/状态机 → 重新审查" | 外循环（跨图） |
| B2 | Step 1.8 否决 → 重新设计消除冲突 → 重新评审 | L232 | 自环 |
| B3 | Step 1.9 无日志 → 回本步补挖，禁止进 Step 2 | L262 | 自环（阻塞前进） |
| B4 | Step 2 依赖缺失 → 回 design_memo 补设计 | L288 | 出图回 B1 |
| B5 | Step 3 domain 不一致 → **回 Step 2** 修正 | L325 | 正式回边 |
| B6 | Step 3 孤儿/状态漂移 → 重跑 sync+align | L325 | 自环 |
| B7 | Step 3.5 该拆不拆 → 回拆件闭环 | L355 | 子 SOP 环 |
| B8 | Step 4 算法缺失 → **回 Step 1** 补文档 | L380 | 长回边 |
| B9 | Step 5 修复循环（E1>0 → 修 → E2）**连续 2 轮 0** | L424-426 + `task_repo.py:667` | 真循环（次数由代码常量定） |
| B10 | Step 6 FAIL 无法就地修 → **回 Step 4** → 重审该节 | L468 | 正式回边 |
| B11 | Step 7 文档与代码漂移 → **回 Step 4** | L499 | 正式回边 |
| B12 | Step 8 对齐失败 → **回 Step 7**；diagnose 错误 → 修复后重跑 | L562 | 正式回边 |
| B13 | Step 10 网关拒绝 → **回 Step 6** 长清单审查 | L650 | 跨段回边 |
| B14 | Step 12 merge 冲突 → **暂不清理，保留逃生通道**（不进 abort） | L763 | 终止分支（非回边） |
| B15 | Step 9 文件丢失 → git reflog/dangling blob 恢复后重走 | L592 | 恢复分支 |

**环检测结论（块B CV-07 的依据）**：B1~B15 中存在**双向成对回边**（B8 Step4→Step1 与 B10/B11 →Step4），因此主序 Step1→…→Step12 加回边后**不是 DAG**。校验器不能简单禁环，必须要求：回边一律声明在 `rollback_to[]` 且**只许指向编号更小的环节**（B9/B6 自环例外，须带 `max_rounds` 引用常量）；主序边不许反向。这正是 `validate_strategy_production_map.py:121-128`（自环拒绝 + 反向边必须在 `feedback_loops` 显式声明）的既有形态，可直接照抄语义。

## §3 重叠判定（旁轴，处置五选一：吸收/融合/扩展/废弃/引用）

| # | 撞车面对象 | 撞什么 | 处置 | 落地要求（必须在图 YAML 里体现） |
|---|---|---|---|---|
| O1 | `construction_workflow_policy.md` 本身 | 本图若把 17 步的"做什么/怎么做/判据/处置"写进节点字段 = 造第二真源，必然漂移（§0 门④ 与 R-11/R-12 已示范漂移速度） | **引用** | 图节点仅允许：`step_id` + `segment` + `anchor_commands[]`/`anchor_gates[]`/`anchor_docs[]`（路径或 gate_id 引用）+ `rollback_to[]` + `verifiable`。**禁**复制政策正文散文（INV-1 型条款，同 TDM/图9 纪律；块B CV-12 判红）。政策 MD 保持唯一真源，图=派生件（生成器产出，根宪法 §9 条目 5） |
| O2 | 图11 交付流水线图 | Step 0/9/10/11/12 五行（政策 L99/L101 自标"不重复，引用"） | **引用** | D14-01/14/15/16/17 五个节点标 `role: handoff` + `handoff_to: D11-*`；本图不得登记 lock/queue/landing/merge 的机制锚（那是图11 的 anchor 面）。切分线证据见 §0 门③ E1-E5 |
| O3 | GOMAP（图10） | "治理流程"名义相近 | **不并（引用）** | GOMAP 是运行时模块装配（L0-L6），其 `out_of_scope_refs` 原文（`config/governance_operations_map.yaml:17-19`）已把"提交门禁体系"排除在运行时流水线之外；本图 17 步在 GOMAP 中零出现（实测 grep）。图 YAML `boundary:` 段须逐字引该 out_of_scope 行 |
| O4 | battle_map `step_id` 轴（BM-*） | 都叫"步骤/环节"、都有 step_id 轴、都有 anchors/edges 三表结构 | **扩展否 → 并列新轴（引用结构，不复用值域）** | `battle_map_domain_policy.yaml:45-` 的 `flow_stage_allowed_domains` 是**交易阶段**闭集（stock_selection/buy_flow/position_management/…），施工步骤挂进去必被 BM-INV-004 判域漂移，且 BM-INV-007 会要求交易域锚点 ⇒ 语义污染。结论：本图自建 `D14-*` 轴，对齐 key 名在 `alignment_checklist §3` 显式标 `step_id(D14-*)` 与 battle_map `step_id(BM-*)` 区分（总包收口 §X-3） |
| O5 | `alignment_checklist.md` §3/§4 | 本图建图后要登记；Step 3 的"图"清单也是它的真源 | **引用（不复制）** | 本图不得内嵌"哪十张图"清单（R-12 已证该清单数会变）；D14-07 节点的锚只写 `align_all.py` + `MAP-ALIGNMENT` gate_id，图的张数读 `alignment_checklist.md:65` |
| O6 | `trae_056_module_creation_workflow.yaml`（11 phase） | Step 4 的 phase_4~9 与本图环节边界重叠 | **引用 + 边界声明** | 政策 §5.3 L817-819 已定关系（"Step 4 涉新建模块才引 trae_056 phase_4-9"）；图节点 D14-09 须带 `sub_workflow: trae_056#phase_4..phase_9` 引用而非展开；R-12 的 11 vs 10 phase 计数与 `phase_2_design_state`/`phase_2_design_node` 双键须一并纠 |
| O7 | `lane_construction_discipline_policy.md` / `frontend_component_split_policy.md` / `data_ops_policy.md` | 同目录 SOP，都是"流程闭环" | **引用（子 SOP 挂节点）** | Step 3.5 的"有得拆"分支已声明转 8 步拆件闭环（L351）；图里用 `sub_workflow` 表达，不另立节点族。数据回灌类施工政策 L40 明确"另必读 data_ops_policy"，本图 boundary 须写"不含数据运维流" |

## §4 批次志（四类批次视角 + 增量曲线 + 三扫是否收敛）

| 批次 | 类型 | 视角/做法 | 本批产出 | 增量 |
|---|---|---|---|---|
| B1 | 需求批 | 从消费端反向挖：AGENTS §0.4（施工必读）、普查 §4 L58（缺口=SOP verifiability=manual）、图11/图12 骨架对 15 步的引用位 | 环节数从普查的"15"校正为 **17**，并定五段分层（§2.1） | +2 环节（1.9/3.5 类"后补步"须独立计锚） |
| B2 | 三重扫描批·①按生产者（政策自身逐段） | 17 个 Step 段逐段解析 7 个粗体字段覆盖率（§7-C1） | 字段覆盖率 100%，但 `执行命令` 块仅 9/17 段有（其余 8 段只有散文"执行要点"）⇒ 锚缺口清单 | +0 环节，+9 命令断点候选 |
| B3 | 三重扫描批·②按形态（锚→实体验证） | 政策每条命令/flag/CLI 子命令/gate 名/文件路径逐条 `find`/`grep -c` 实查（§7-C3~C8） | **红条目 R-01~R-09 + R-14**（9 条"说有实则没有"+1 条命名漂移） | +10 断点，0 新环节 |
| B4 | 三重扫描批·③按消费者 | 反向核：谁引用 construction_workflow_policy（宪法冷启动序列第 4 步 / alignment_checklist §8 / project_rules / 图11/12 骨架 / rule_catalog_registry L2007） | 消费者全部按"15 步"口径引用 ⇒ 计数纠偏必须同步 5 个消费面（总包收口 §X-2） | 0 新环节 |
| B5 | 案例批 | 拿本会话自身当案例：本图车道（骨架会话）实际走的步序=Step 0（worktree 隔离）→Step 1（读真源）→Step 1.9（普查先验挖矿）→Step 6（自审）→Step 11（只落盘不提交）；Step 2/3/8/10 被总包统一执行 | **实测发现"17 步全序对一条只写文档的车道过重"**：Step 4（施工编码）/Step 3.5（前端盘点）对本任务 N/A，Step 5 无测试可跑——这是图必须表达"可选/条件触发环节"的实证（`trigger:` 字段设计依据，块B §2） | 0 环节，+1 结构性判据 |
| B6 | 考古批 | 政策 frontmatter/修订记录逐版（L833-850 共 11 版）+ 裁定#384 归档事件 + AI_review_instructions 归档事件 | **R-11（上游真源整体归档未跟进）**、R-10、R-12 的腐化链条清晰：五图→六图→七图→十图三次改名，design_memos 一次整体搬家，SOP 一次没跟 | 0 环节，+3 红条目类 |

**增量曲线**：环节数 15（普查先验）→ 17（B1）→ 17（B2~B6 四轮零新增）。**红条目数曲线 9→10→13→15 仍在上升**——说明"锚的实存性"这一维还没扫完（各步的锚不止政策给的那些）。

**三扫是否收敛**：**未收敛**。①政策逐段扫 = 收敛（结构字段已 100% 解析）；②锚→实体验证 = **不收敛**（本批只扫了政策明文提到的锚，未扫"政策未提但实际存在的锚"——已发现两例反例：Step 0 的 `session_startup_check.py`、Step 7 的 `validate_document_lifecycle.py`，这类"有锚未被认"预计还有一批）；③消费者扫 = 不收敛（只扫了文档消费者，未扫代码/测试侧消费者）。**封矿四判据均未满足**，本件为波1 v1，不封顶。

## §5 待挖清单（作业簿领取入口；编号即文件名契约）

按"生产者变→拆；验证口径变→拆；只是标签变→不拆"（skeleton_mining_policy §3）定簿。**优先级 P0=块B 校验器落地前置**（不挖则四道门第④门永不过）。

| 簿号 | 文件名 | 覆盖环节 | 优先级 | 本簿要答的唯一问题 |
|---|---|---|---|---|
| 01 | `01_D14-06_设计态登记与准入面.md` | D14-06 | **P0** | depgraph 锚已实；MAD-001~005 的准入记录到底落在哪（R-05 幽灵文件的替代面）？`--query-production` 该用哪个真命令替代（R-04）？ |
| 02 | `02_D14-01_冷启动与阶段门控58检查.md` | D14-01 | **P0** | `session_startup_check.py` 58 项里哪些等价于"施工准入"？R-01 幽灵脚本该删还是该建？Step 0 能否直接成为第一个 verifiable=yes 的锚？ |
| 03 | `03_D14-05_方案挖矿可验化.md` | D14-05 | **P0** | "挖矿增补章节存在 + 六向各≥1 条 + 三态裁定留痕"能否用 30 行 checker 判红（真源=mining_sop_policy §判据 + 方案 MD 结构）？ |
| 04 | `04_D14-11_长清单审查与留痕悖论.md` | D14-11 | **P0** | "禁创建报告文件"（L465）与"每步可机验"互斥——留痕面该走 `.runtime/sessions/<sid>/`（不入 git）还是需新裁定？给 Owner 两个可执行选项 |
| 05 | `05_D14-02_文档审查真源接续.md` | D14-02 | P1 | 68 号审查流水线（`code_review_ai.py`）是不是 Step 1 的现行真源？12 节清单在政策里还剩几节有效（附录 A 与 AI_review 的差集）？ |
| 06 | `06_D14-04_架构评审门控面.md` | D14-04 | P1 | 评审记录落点纠档（R-11）后，2 条/期的触发率是否支撑"每任务必过"？与 `risk_tier_registry.yaml` 的 high 门位如何挂（避免人门位无据）？ |
| 07 | `07_D14-07_全图全库对齐锚.md` | D14-07 | P1 | 本图节点接进 `MAP-ALIGNMENT` 聚合台的最短路径（`subs` 加一行）+ align_all 第十节形态（照抄第八节）；与 O4/O5 的轴冲突复述一遍 |
| 08 | `08_D14-09_施工编码门禁簇.md` | D14-09 | P1 | 文件头 15 字段/容量/git 预算/复杂度四台 gate 的覆盖交叉与空档（例如"事件驱动启动"禁 cron 由哪台 gate 管？） |
| 09 | `09_D14-10_循环验收与词表断链.md` | D14-10 | P1 | 无任务卡时循环验收无面（`CIRCULAR_ACCEPTANCE_ROUNDS` 只在 task_repo 生效）是否可接受？R-08 词表模块缺失的补法（本车道不修，只出方案） |
| 10 | `10_D14-08_D14-12_留痕落点重建.md` | D14-08/12 | P2 | design_memos 归档后，Step 3.5"拆件判定留痕"与 Step 7"更新施工文档"的新落点是什么（同一问题的两面，合簿） |
| 11 | `11_D14-13_双态流转与worktree分流.md` | D14-13 | P2 | 政策 L519-528 "worktree 内只登记不流转 + merge 执行人事后实证核验"能否机械化（这是 R-03 diagnose 路径纠偏的落点） |
| 12 | `12_D14-14_15_16_17_交接锚清单.md` | D14-14/15/16/17 | P2 | 与图11 骨架逐节点的引用表（`D14-* → D11-*` 一对一/一对多），产出=图 YAML 的 `handoff_to` 字段值；不重述机制 |

簿数=12（环节 17，合并 5 对：3.5+7 / 9+10+11+12 四簿独立）。9-12 为 P2，可在波2 后半或封矿批承接。

## §6 封顶声明与🌑点名

**本件不封顶**（波1 v1，§4 三扫未收敛）。封顶声明留待波2 后补，格式=「此后增长=环节内部锚的补齐，不再增枝；增枝须过 skeleton_mining_policy §3 三问并留理由」。

**🌑 点名（个人/当前形态不可得，永久或本期不可机验）**：

| # | 🌑 项 | 为什么不可得 | 处置 |
|---|---|---|---|
| L-1 | Step 1.8 Owner 亲自执行或书面委托（L229） | 人门位=设计上的不可自动化（AGENTS §5.2/§5.3） | 图节点标 `human_gate: owner`；校验器只验"评审记录文件实存"，不验内容 |
| L-2 | Step 1 / Step 6 的"审查结论 MUST 在对话内，禁创建报告文件"（L184/L465） | 政策明文禁止留痕 ⇒ 结构性不可机验；强行加留痕=改政策，需裁定，超骨架会话权限 | 标 `verifiable: manual` + `blocked_by: 裁定待取`，写进总包收口 §X-5，**不自作主张建留痕面** |
| L-3 | 会话内"上下文是否真的读了必读文件"（Step 0 第 2 项） | 无采集面；AGENTS §6 上下文预算不允许 | 🌑 永久（除非引入 LLM 调用审计面，属图11/LSG 域） |
| L-4 | `D:\临时工作区\依赖图\*.md`（政策 L209 称"设计意图查询真源"） | 盘外路径，本 worktree 不可达，且违反"项目根零临时文件/绝对路径外置"精神 | 点名并建议改指仓内真源（总包收口 §X-6） |
| L-5 | `c:\Users\fanzi\.trae-cn\memory\...\project_memory.md`（政策 L623/L653/L713/L764 四处 `file:///c:` 绝对外链） | 单机个人记忆文件，非仓库资产，换机即断；实测 `grep -c "file:///c:"`=4 | 🌑 对本仓不可验；建议政策外链改仓内件（§X-6） |
| L-6 | Step 11 "session_worktree 标记可清理" | 该状态位全仓零命中（R-06），机制不存在 | 🔨 非 🌑：属"待建"，作业簿 12 承接 |

## §7 实查命令附录（全部只读，Owner/后续会话照跑可复核；在仓库根执行）

```bash
# C1 政策 17 个 Step 段与 7 字段覆盖率（本骨架"字段 100%/命令块 9-17"结论的来源）
grep -n "^### Step" docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md
python -c "import re;L=open('docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md',encoding='utf-8').read().split('\n');\
i=[(n,l) for n,l in enumerate(L,1) if l.startswith('### Step')]+[(len(L)+1,'')];\
print([(l[4:12],sum(1 for f in ['何时触发','前置条件','操作摘要','引用真源','执行命令','执行要点','通过判据','不通过处置','产出物'] if '**'+f in '\n'.join(L[s-1:e-1])),\
'\n'.join(L[s-1:e-1]).count('\`\`\`powershell')) for (s,_),(e,_) in zip(i,i[1:])])"

# C2 计数漂移（标题 15 步 / Checklist 13 项 / trae 84 个 / in-process 100 个）
grep -c "^### Step" docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md   # 17
grep -oE "^\| [0-9]+ \|" docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md | wc -l   # 16（Checklist）
ls docs/01_policies_and_standards/rules/trae_*.yaml | wc -l                                                 # 86
grep -c "^- gate_id:" docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml        # 99（册内 total_gates:99）
grep -n "total_gates" docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml \
  docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml

# C3 幽灵命令与断链
find . -iname "*ide_health*" -not -path "./.git/*"                       # 空=R-01
ls scripts/git_commit_gateway.py scripts/governance/diagnose_depgraph.py  # 前者不存在、后者不在该路径=R-03
ls scripts/git_commit.py scripts/governance/d5_architecture/diagnose_depgraph.py   # 真身
grep -oE '"--[a-z-]+"' scripts/governance/apply_depgraph.py | sort -u | grep -i query   # 空=R-04
find . -name "module-id-registry.json" -not -path "./.git/*"             # 空=R-05
grep -n "add_parser" scripts/session_worktree.py                          # create/exec/merge/abort/list=R-06
grep -n 'cmd == "' scripts/lock_files.py | tr '\n' ' '                    # release 需 file+owner=R-07
ls src/zephyr/shared/vocab 2>&1                                           # 不存在=R-08
grep -rn "EXTREME_STATE_ALIASES" --include=*.py src scripts               # 空=R-08

# C4 锚实存（Step 3/4/8 的 yes 依据）
grep -oE '"--[a-z-]+"' scripts/governance/apply_depgraph.py | sort -u | grep transition   # 两 flag 在
ls scripts/governance/sync_panorama_module.py scripts/governance/d5_architecture/generators/align_all.py \
   scripts/governance/generate_project_path_tree.py scripts/governance/d5_architecture/generators/generate_battle_map_diagram.py
grep -n "gate_id: " docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml | grep -iE "GIT-CALL|CAPACITY|COMPLEXITY|BLUEPRINT|DEPGRAPH|TEST-|STASH|FRONTEND-TRUTH|MAP-ALIGN"

# C5 政策行号锚全偏（R-13）
grep -n "def boot_sequence" src/zephyr/trading/lifecycle_manager.py                                   # 98（政策写 88）
grep -n "def register_boot_hooks" src/zephyr/trading/boot_hooks.py                                    # 629（政策写 579）
grep -n "class HookRegistry" src/zephyr/governance/ops_governance/event_hook.py                        # 75（政策写 73）
grep -n "def restore_design_data" scripts/governance/generate_project_depgraph.py                     # 3368（政策写 3094）
grep -n "def _register_default_reconcilers" src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py  # 1547（政策写 783）
grep -n "def session_worktree_abort\|def session_worktree_sweep" src/zephyr/gov_enforcement/rule_bridge/session_worktree.py  # 7497/2194（政策写 8037/2163）

# C6 挖矿日志零 checker（R 之 Step 1.9）
grep -rl "挖矿增补" --include=*.py src scripts | wc -l    # 0

# C7 上游真源归档（R-11）
cat docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/README.md | head -14
ls docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/            # 仅 README + 16 号
ls docs/_working/archive/2026-09/design_memos/ | wc -l                                      # 49
ls docs/_working/audit/architecture-reviews 2>&1 | head -1                                  # 不存在=R-10
ls docs/_working/archive/2026-09/audit/architecture-reviews/                                # 实际落点（2 条记录）

# C8 图11 切分线双向认领（门③ 证据）
sed -n '44,50p;113,117p' docs/_working/map_build/fig11_delivery/00_skeleton.md
sed -n '97,102p' docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md   # Step 10/12 "不重复，引用"
grep -n "out_of_scope" -A 8 config/governance_operations_map.yaml | head -14                            # GOMAP 排除提交门禁

# C9 步骤锚校验器的接法坐标（块B 用）
grep -n "def make_map_alignment_gate" -A 25 src/zephyr/gov_enforcement/commit_gates/panorama_alignment_gate.py | head -30
sed -n '301,307p' docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml
sed -n '581,615p' scripts/governance/d5_architecture/generators/align_all.py            # 第八节形态（第十节照抄）
sed -n '26,45p' docs/01_policies_and_standards/_registry/vocabularies/verifiability_vocabulary.yaml   # verifiable 枚举复用面
```

## 总包收口请求（本车道禁直写共享面，逐条请总包落）

| # | 诉求 | 目标共享面 | 建议处置 |
|---|---|---|---|
| X-1 | 裁域宽：policy frontmatter `scope: global`（L13）与正文"仅 07 域"（L40/L812-814）矛盾。图14 建图口径必须先裁 | `construction_workflow_policy.md` frontmatter + §5.2 | 建议按 L40 收窄 + 图 boundary 显式声明"不含数据运维流/不含交付机制" |
| X-2 | "15 步→17 环节"计数纠偏需 5 个消费面同步（AGENTS §0.4、alignment_checklist、project_rules、图11 骨架、`rule_catalog_registry.yaml:2009` title） | 上述五处 | 一律改口径为"施工闭环环节全集（数量以 policy Step 段实测为准，勿在散文写死）"，并把 `section_count: 0` 由生成器填 |
| X-3 | `alignment_checklist.md` §3 加图14 行时，对齐 key 必须写 `step_id(D14-*)`，与 battle_map 的 `step_id(BM-*)` 显式区分；§6 时机矩阵一行；§4 原则 6 挂总线（module_id 两跳） | `alignment_checklist.md` §3/§4/§6 | 照抄图 9/图 10 两行形态 |
| X-4 | 本图 gate **不建独立台**，在 `panorama_alignment_gate.py::make_map_alignment_gate()` 的 `subs`（L295-302）加第 7 行 `("CONSTRUCTION-STEPS","construction_steps_gate","_check")`；同步 `in_process_gate_registry.yaml:301-307` MAP-ALIGNMENT 的 `files_trigger` 加 `config/construction_workflow_map.yaml` 与新校验器路径 | 两处（代码+册） | 触发式；YAML 损坏 fail-closed |
| X-5 | **需裁定**：Step 1/Step 6 "审查结论禁创建报告文件"（L184/L465）与"每步可机验"直接互斥。要么裁定允许 `.runtime/sessions/<sid>/` 留痕（不入 git，不进 docs），要么接受这两环节永久 `verifiable: manual`。骨架会话无权改政策 | 裁定册（需取号，HEAD max 现测再定） | 建议前者：留痕件放 `.runtime`，校验器只验存在性 |
| X-6 | 政策外链纠偏：**4 处** `file:///c:\Users\fanzi\...` 个人记忆外链（实测 `grep -c "file:///c:"`=4）+ `D:\临时工作区\依赖图\*.md` 盘外真源（L209）+ **12 处**失效 `07_trading_decision_architecture/design_memos/` 链接（实测 `grep -c`=12，行号 L41/42/52/69/70/71/470/487/573/592/608/654） | `construction_workflow_policy.md` | 改仓内真源或标"历史出处仅存档"；本批 R-11 的 49 件归档台账=`docs/_working/code_doc_gov_campaign/p3_placement/w14_placement_ledger.md` |
| X-7 | R-01/R-03/R-04/R-05/R-06/R-07/R-08 共 **9 条"文档说有实则没有"**属政策/代码双侧修复，跨多车道（词表=R-08 归 vocab_legislation 线；gate 实名=R-14 归 gslim 线）；请总包统一排产，勿让图14 施工期"顺手修"造成连坐 | 多面 | 图14 只负责在校验器里把这些锚登记为 `verifiable: no` + 红，不放行 |
| X-8 | token 需求（施工期）：新建 `scripts/governance/d5_architecture/validators/validate_construction_steps.py`、`.../generators/generate_construction_steps.py`、`src/zephyr/gov_enforcement/commit_gates/construction_steps_gate.py`、`config/construction_workflow_map.yaml`、`tests/governance/commit_gates/test_construction_steps_gate.py` + 本车道 2 份 MD | `batch_creation_tokens.py --prefix docs/_working/map_build/fig14_construction` | 挖矿期先给 2 份 MD 的 token；施工期五件由总包排产时再取 |
| X-9 | 建图口径确认：波3 排产前请总包确认"图14 = 17 环节（非普查先验的 15）"，且图 YAML schema 必须双字段承载本骨架两列口径——`build_status`（✅/🔨/⬜ 的机生映射=built/partial/pending）与 `verifiable`（yes/partial/no 直接取 `verifiability_vocabulary.yaml` 的 automated/inspection/manual 三值），禁把两列压成一列 | `config/construction_workflow_map.yaml` schema（施工期） | 双字段既有先例=图 9 的 `build_status` + 政策 frontmatter 的 `verifiability`，零新枚举 |

**自审裁定**：欠——六向台账中「史」向已做实（R-10/R-11 考古链完整），「新」向欠（未做外部对标：业界"definition of done pipeline / runbook-as-code"同类物一句话结论待作业簿 03/04 补），「旁」向 O4 需图11 车道会签（D14→D11 引用表未定稿，簿 12 承接）。溢出条目：无新增环节溢出（17 已在骨架），但 R-16 域宽矛盾**必须先回写骨架 §0 门①**（已回写）。
