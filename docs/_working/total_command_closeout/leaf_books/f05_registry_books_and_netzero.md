---
ttl: task_bound
---

# 案卷 F05 · 族 5 治理册与净零（W-52 .. W-59）

> 本册为施工案卷（测量与文档），非裁定；所有"补丁条目"仅写在配套 `.yaml` 里，本册不落任何改动。
> 母骨架=docs/_working/total_command_closeout/00_master_skeleton.md 第 105-116 行（族 5 · 治理册与净零，八环节）。
> 落地面真源=`git show HEAD:<path>` 字节；工作树存在≠落地。
> 取数时间窗：2026-09-27 03:53+08:00 起（本机时钟），cwd 见各节命令块。
> 铁律复述：本族不静默改动他人断言的数字或口径；声明数与实测数不一致时**两个都报**，并给证据分级。
> 配套机读补丁册：`f05_registry_drift_patch.yaml`（纯元数据，未应用）。
> 案卷自律：本册与补丁册刻意不写"裁定前缀+数字"与"#ARCH-+纯数字"的连写形态
> （悬空号一律以"号干 NNN"文字描述，在册号一律以 registry 行号+issue_id 原文引用），
> 以免案卷自身触发 RULING-REFERENCE / ARCH-REFERENCE 面。

## 全族通则（先证尺，再量物）

**判据** — 本族所有数字先过"尺自证"（见下一节《被测面自证》），再过"物实测"；
凡"条目列表+计数"（宪法 §9 第 5 条），本册逐条标注它是生成器产出还是人手写。

**取数纪律** — 每次 python 取数前先打印 `zephyr.__file__` 证明读的是 lane；
只读解析（`yaml.safe_load`），永不 round-trip 回写（多本册带 `# [A_config]` 类标记注释，重 dump 会毁）。

## 被测面自证（先证尺，再量物）

**判据** — 本族三件工具（`_shared/registry_entry_count.py`、`d3_metadata/check_registry_consistency.py`、
`generators/generate_registry_master_index.py`）都在我 lane 内未提交，它们自身的正确性必须先验，
否则"工具说没漂移"没有意义。首要风险=寻址：工具若静默指向主区，lane 内跑出的绿是假绿。

**实测（带数）** —

| 自证项 | 实测 | 判 |
|---|---|---|
| `zephyr.__file__`（PYTHONPATH=lane/src） | `D:\ZephyrAlpha\.aidrafts\st-final-build-20260926\src\zephyr\__init__.py` | 读的是 lane |
| `_shared.constants.REPO_ROOT` | `D:\ZephyrAlpha\.aidrafts\st-final-build-20260926` | 正确 |
| 寻址机制 | `find_repo_root()` 从 `zephyr.shared.io.paths.__file__` 上溯（非 cwd），`ZEPHYR_WORKTREE_ROOT` 可显式覆盖 | 见下条风险 |
| 风险 | `check_registry_consistency.py` 第 58 行 `sys.path.insert(0, REPO_ROOT/"src")` 发生在 REPO_ROOT 已定之后——若 editable 安装把 `import zephyr` 钉回主仓，REPO_ROOT 会静默=主仓，工具仍"绿"，但量的是另一棵树。工具内无"我量的就是我所在的树"自证断言 | 建议补自证锚（本册不改码） |
| `registry_master_index` 生成器 `--check` 语义 | 只比"登记表**张数**"（第 257-264 行），不比每表的 entry_count | 检核面偏弱（在册事实，非缺陷判定） |
| 生成器时间戳 | `generate()` 第 239 行 `datetime.now(UTC)` 直写 `generated_at` | 存疑待裁（宪法 §1 第 10 条"生成器禁 datetime.now()"的字面覆盖范围未核实，不据此定罪） |
| 口径解析器 `parse_counting_rule` 自测 | "detectors.existing + detectors.new 条目数合计"→`(yaml_sum, …)` 正确；"systems 子系统数"→`(yaml_dict_len, systems)` 正确；"含 deprecated 全量（物理 yaml 条目数=datasets 数组…）"→`(yaml_sum, 'deprecated+yaml')` **错**；"capability 条目数（…）"→`(yaml_list,'capability')` **键面差一**（真键=capabilities）；"meta_question 主表行数（…）"→None | 口径文本有 7 条不可机读（见 W-52 关键发现 3） |

**取数命令**（cwd=`D:\ZephyrAlpha\.aidrafts\st-final-build-20260926`，2026-09-27 03:53–04:35+08:00）—

```bash
cd /d/ZephyrAlpha/.aidrafts/st-final-build-20260926 && export PYTHONPATH="$PWD/src"
python -c "import zephyr; print(zephyr.__file__)"
# 载入 lane 内两件工具后调用 verify_entry_counts() / verify_roor_summary() / verify_domain_ssot()
```

**派生面 vs 手工面** — 本册所有数字均由 `yaml.safe_load` 解析实测（只读，未做任何 round-trip，
未写任何被量文件），可复现者标 A；需人判读者标 B；纯 grep 推论标 C。

**HEAD 是运动靶** — 03:53:00 主区 `git rev-parse HEAD`=edca5445b7，03:53:21 已是
514698ba62（dev 分支同一时刻在推进）。本册全部"落地面"数字锁定 **dev=514698ba6213df406ae435fa42b2f898c0afc17b**；
任何 bag 应用补丁前必须复跑取数命令，sha 变了就重取。

**热册是活靶（本窗口实锤）** — 取数期间 `capability_canonical_file_registry.yaml`（mtime 04:03）与
`module_translation_registry.yaml`（mtime 04:13）正被另一进程重写：同一 lane 工作树内
`creation_tokens` 在 04:0x→04:19 从 11598 涨到 **11604**（dev 字节面=11581）。
⇒ 补丁册里凡涉这两本册的行号一律标 anchor 优先、行号仅作快路径；对不上就停，不猜（P52-11/P52-12/P54-*）。
本 lane 全程未对任何热册施加写操作（`git status` 复核其改动系他方 staged 状态，mtime 亦非本 lane 写入时刻）。

---

## W-52 · ROOR 的 REG-STATE-VOCAB-001 entry_count 与实条目对齐（派生计数改生成器派生）

**判据/命题** — 合合格不是把 29 改成 63，而是：该条 `entry_count` 由生成器按 ROOR 本条自述口径派生，
且 CI（CR-007）能在下次漂移时机械发现。改数字=治标，把这条从手工面搬到派生面=治本。
命题的另一半=**不静默改口径**：29 与 63 可能都是"对"的，只是口径不同（全量 vs 带 status 子集）。

**实测（带数）** —

1. CR-007 全表对账（lane 工作树，77 行走查）：MATCH 45 / STALE 19 / MANUAL 11 / NO_COUNT 1 / UNSPECIFIED 1。
   按 dev 字节面（`git show dev:<path>`）重算：MATCH 44 / STALE 19 / NO_COUNT 1 / UNSPECIFIED 1 / GLOB 1
   （REG-SKILL-001 是目录 glob，离线不可跨面量）。
   **STALE 集合差** = ∅（19 个 registry_id 两面完全一致）；值差异仅 2 行：
   REG-SCRIPT-002 实测 dev=450 / lane 工作树=516；REG-GEN-001 实测 dev=11581 / lane=11598。
   ⇒ 上一报"19 条 stale"在本靶面**复现成立**（19=STALE 本体，不含 UNSPECIFIED 1 条与 NO_COUNT 1 条；
   若上一报的 19 含 UNSPECIFIED，则真实 STALE 是 18——两报无法逐 id 对齐，因上一报未留 id 清单，故不合并计数）。
2. 19 条 STALE（声明→派生，均 dev 面）：SCRIPT-001 991→1037｜SCRIPT-002 434→450｜RESCHED-001 74→81｜
   CATALOG-001 55→58｜**STATE-VOCAB-001 29→63**｜DOC-001 256→294｜GATE-CAT-001 169→181｜INFRA-001 16→17｜
   FUNC-DOMAIN-001 83→94｜ARCH-ISSUE-001 761→805｜CAPCAN-001 378→388｜GEN-001 5520→11581｜
   ARCH-001 75→74（**声明高于实测**，属净删未同步）｜TECHNICAL-INDICATOR-001 102→143｜PAT-001 297→287（同上）｜
   DATAFLOW-001 342→294（同上）｜DAL-001 27→32｜BTB-001 137→142｜ATH-001 38→49。
   另有 UNSPECIFIED 1：REG-METAQ-001（声明 0，口径文本"meta_question 主表行数"不可机读）。
3. **REG-STATE-VOCAB-001 三个数并存**：ROOR 字段=29（第 257 行）/ ROOR 散文=28 套（第 260 行，
   且其四轴分解 10+12+5+1=28）/ 真源 `vocabularies` 数组实测=**63**。
   拆解 63：`status: production` 27 + `status: testing` 2 = **29**（=字段值的来源），另 34 条无 status 键；
   轴键实测分布 宏观 10/情绪 **13**/预测 5/个股 1=29（散文写 12，差 1）+ 新一代短轴键（m.regime 12/e.cycle 9/…）34。
   ⇒ 判：**29 不是"错数"，是"带 status 子集"口径**；ROOR 现写口径"vocabularies 数组条目数"是全量口径。
   两口径都对，但只能有一个在册。本册不改判（口径归谁=Owner 语义裁），补丁册里两值并列上报。
4. 派生面覆盖率实测：ROOR 77 行中仅 **38 行**自带 `counting_rule`（49%），39 行没有；
   代码侧手工口径表 `ENTRY_SPECS` 66 键（其中 **3 键指向已不在册的表**）、`ENTRY_MANUAL` 13 键（**2 键已死**）。
   对 63 个有手工口径的行做"解析本条自述文本 vs 手工表"比对：一致 23 / 文本缺失而盲 33 / **解析出不同键 7**。
   7 条键面不符：REG-CAPCAN-001（capability vs capabilities）、REG-FREEZE-001、REG-BMK-001、REG-FCT-001、
   REG-RLM-001、REG-DATAFLOW-001、REG-ATH-001。
   ⇒ **关键结论**：W-52 的终局目标（瘦身手工表、让自述口径当真源）现在**不可执行**——
   一旦删手工表，33 行退 UNSPECIFIED、7 行退到错键。必须先规范化 7 条口径文本 + 给 39 行补口径。
5. ROOR summary 段（第 878-900 行，自标 `generated_by: check_registry_consistency.py --refresh-summary`
   =**派生面字段**，只是没人复跑）：`total_registries` 存 76 / 派生 77；`by_tier.tier_2` 存 34 / 派生 35；
   `by_status.active` 存 66 / 派生 67；`by_medium.ok` 存 74 / 派生 75。其余 3 项 MATCH。
   ⇒ 上一报"4 summary scalars"在本靶面复现=**4**（同 4 项）。修法=再生，不手改。
6. 散文计数面：ROOR 的 description/name/title 文本里"数字+量词"出现 **76** 处，覆盖 55 行。
   上一报的"53"在本靶面**未复现**，且其判据未在任何工具/真源里钉过——两套数不合并，并列上报。
   朴素机械判据（散文数 ≠ 本行派生实测即算撞）会得 ≈50 处/40+ 行，**过度捕获**（把"sources 15 个/datasets 294"
   这类不同对象误判为撞车）⇒ 散文计数**不可机械裁定**。人工逐条判读后的"硬撞车"子集=**26 处/24 行**
   （明细见补丁册 `prose_advisories`，只作展示面改写建议，不作机读补丁）。

**取数命令**（cwd=lane，dev=514698ba，03:53–04:20+08:00）—

```bash
cd /d/ZephyrAlpha/.aidrafts/st-final-build-20260926 && export PYTHONPATH="$PWD/src"
python -c "import zephyr; print(zephyr.__file__)"
# (a) 全表对账：载入 lane 内 check_registry_consistency.py，调 verify_entry_counts() 取 verdict 直方图
# (b) 跨面集合差：对每行读 git show dev:<physical_path> 后用 count_by_spec 复算，rid 为键做对称差
# (c) summary：verify_roor_summary()
# (d) 单表复核：yaml.safe_load(state_vocabulary_registry.yaml)['vocabularies'] → 63，Counter(status) → 27/2/34
# (e) 口径覆盖率：统计 ROOR 内含 counting_rule 的行数；对 ENTRY_SPECS 逐行 parse_counting_rule 比对
```

**派生面 vs 手工面** — 本环节的账目分三面：①ROOR `summary`=派生面（有再生器，缺复跑）；
②ROOR 每行 `entry_count`=**手工面**（唯一写入口是 CR-007 `--update-entry-counts` 的行级手术，
且只有 38/77 行具备机读口径）；③`registry_master_index.yaml`=派生面（生成器产出，
其自身条目数 58 与 ROOR 声明 55 相撞=REG-CATALOG-001，属"生成器未复跑"）；④散文计数=纯手工面，
**宪法 §9 第 5 条与 §4 第 3 条正面对撞**（"计数用字段不写死在散文"）。

**补丁条目** — `f05_registry_drift_patch.yaml`：`P52-*`（19 条 entry_count 行级值，含 2 条跨面值差）、
`P52-REG-METAQ-001-*`（口径不可机读+永久册指临时快照）、`P52-SUM-*`（4 个 summary 标量，动作=复跑再生器）、
`P52-RULE-*`（7 条 counting_rule 文本规范化前置件）、`P52-DEADKEY-*`（工具内 3+2 死键清理建议）、
`prose_advisories`（26 处散文撞车，展示面）。

**未决问题（需 Owner，本册不自行裁定）** —

- Q-52a 口径归属：REG-STATE-VOCAB-001 的在册数取"全量 63"还是"带 status 子集 29"？两值均已在册级证据，
  改哪一个都改变别人的断言。若取 63，第 260 行散文（28 套+四轴分解）必须同步改写，否则文档自相矛盾。
- Q-52b 派生面化的顺序：先补 39 行口径再瘦身 ENTRY_SPECS，还是维持双层？本册证据显示"现在就瘦"会致 33 行失明。
- Q-52c `REG-METAQ-001` 的 physical_path 指向 `docs/_working/chain_piling_campaign/snapshots/registry_latest.yaml`
  （task_bound 快照区）却在永久册里挂着 active——是退役、迁永久区，还是改口径？涉宪法 §9 第 4 条（永久区禁引临时区）。
- Q-52d 上一报的 53 与 19 的判据未钉真源：需要么把判据写进 ROOR，要么宣布其为废数，否则后续批次会在两套数间反复横跳。

## W-53 · functional_domain_registry 的 ssot_path↔covers 错配修正

**判据/命题** — "域说它管 X，X 必须真在它声明的真源里"。合格判据=CR-008 归零或每条残留有显式豁免理由。

**实测（带数）** — 域册 entries 实测 **94** 条（ROOR 声明 83=STALE）。CR-008 全量跑（含 covers 符号扫描）
=**10 行问题**，与上一报"10"复现一致；但**分流不同**：上一报"8 条需裁定"，本册实测分流为
"AI 可提案改路径/改符号 5 条 + 需人判（Owner）5 条"。明细（行号=域册 `subdomain:` 行，ssot_path 紧随其后）：

| # | 域/子域 | 行 | verdict | 实测真身所在 | 分流 |
|---|---|---|---|---|---|
| 1 | D_GOV_DRIFT/drift_detection | 87 | COVERS_UNFOUND: `CascadeDetector`/`CanaryController` | 文件在（`cascade_detector.py`/`canary_controller.py`），**同名类不存在**（实类 CanaryComparison/CanaryResult/CanaryRun/CanaryConfig、CascadeEventRecord） | AI 提案（改符号锚点=文件名，非改资产） |
| 2 | D_SECURITY_LLM/llm_defense | 232 | COVERS_UNFOUND: `HITL` | 该真源树内 0 命中（41 个 .py 全扫）；`HITL` 出现在 `integration/pipeline_orchestrator.py`、`intelligence/human_trust_model.py` | **Owner**（覆盖面归属改判） |
| 3 | D_AUTONOMY_CORE/agent_communication | 324 | COVERS_UNFOUND: `A2AMessage`/`Arbitrator`/`ConflictDetector` | 三符真身=`shared/protocols/a2a/a2a_schemas.py` 与 `infrastructure/a2a_protocol/layer3_coordination/` | AI 提案（ssot_path 重构后未跟改） |
| 4 | D_AUTONOMY_PERM/budget_enforcement | 428 | PATH_MISSING `src/zephyr/autonomy_perm/` | 目录**全盘不存在**；covers 各件散在 `governance/ops_governance`、`governance/intelligence_governance`、`governance/security_governance`、`gov_drift` | **Owner**（无单一真源，须拆域或改声明） |
| 5 | D_AUTONOMY_PERM/escalation | 451 | PATH_MISSING 同上 | 同上 | **Owner** |
| 6 | D_INFRA_RUNTIME/persistence | 605 | PATH_MISSING `src/zephyr/data/persistence/` | 真身=`governance/persistence/task_repo.py`、`data_security/data_masking_engine.py` | **Owner**（跨两包） |
| 7 | D_SHARED/shared_services | 698 | PATH_MISSING `src/zephyr/shared/shared_services/` | 真身=`shared/event_bus.py`、`shared/lifecycle/lazy_loader.py`（同一父目录） | AI 提案（上移到 `src/zephyr/shared/`） |
| 8 | D_INTEGRATION_GATEWAY/mcp_servers | 776 | COVERS_UNFOUND: `KnowledgeBaseServer` | 全仓无此类；目录 `*server*.py` 实测 **13 个文件**=10 服务端 + 2 基类（`base_server.py`/`_base_server.py`）+ 1 网关 ⇒ covers 散文"11 个MCP服务端 + 1 Gateway"与实测差 1 | **Owner**（死符号 + 散文数改判） |
| 9 | D_DATA/data_source_integrator | 1188 | COVERS_UNFOUND: `CLS`/`EastMoney` | 真源内以**小写**出现（`data/config/policies.yaml`、`akshare_provider.py`）⇒ 尺的大小写敏感假阴性 | 尺限制（**不算册漂移**，见未决 Q-53a） |
| 10 | D_TEST/test_domain_placeholder | 1877 | PATH_UNDECLARED（`ssot_path` 字面="(depgraph domains.ssot_path 为空)"） | 条目自带 note 已声明"空壳域，净删属 Owner 门位" | **Owner**（已知设计，非新案） |

**取数命令**（cwd=lane，04:05–04:15+08:00）—

```bash
cd /d/ZephyrAlpha/.aidrafts/st-final-build-20260926 && export PYTHONPATH="$PWD/src"
python -c "import zephyr; print(zephyr.__file__)"
# verify_domain_ssot(check_covers=True) → 10 行（3.5s）；check_covers=False → 5 行
# 每条真身：按符号名在 src/ 下词边界匹配 + 目录存在性 stat（本册只读）
```

**派生面 vs 手工面** — 域册 `ssot_path`/`covers` 全为**手写**（该册 `maintenance` 未标 auto）；
depgraph 的 domains 表（PostgreSQL）是架构侧真源，D_TEST 条目 note 自陈"域元数据取自 depgraph 实测"，
⇒ 存在一条"从 depgraph 反向派生 ssot_path"的正道，但离线不可达（涉 DB 凭据，ROOR 里同类表已标
"离线不可数"）。故本环节补丁只能是**人判后的行级改值**，不能声称机生。

**补丁条目** — `P53-*`（10 行，含现字节/建议值/依据；`owner_gated: true` 的 5 条只登记不动）。

**未决问题** —

- Q-53a 尺的口径：`_symbol_in_scope` 大小写敏感 + 词边界，导致 `EastMoney`/`CLS` 假阴性；
  而词边界是红队逼出来的设计（子串会让 `GateEngine` 命中 `GateEngineV2`）。改尺=改门禁语义，需 Owner。
- Q-53b 拆域授权：D_AUTONOMY_PERM 两子域的真源散在 4 个包，"一个子域一个 ssot_path"装不下；
  拆子域=注册表结构变更（宪法 §5 第 2 条 high 门位）。
- Q-53c 派生方向未定：ssot_path 以域册为准还是以 depgraph 为准？方向未定前，本族所有 P53 补丁都可能被反向再生冲掉。

## W-54 · 翻译册 wo001_003 三条悬空条目净删（Owner-gated：本册只记不动）

**判据/命题** — "悬空"要先证两件事：①声明的 module_path 三处面（盘/HEAD/dev）都不存在；
②真身没有别的在册户口（否则净删=把一个活模块的翻译删掉）。

**实测（带数）** — 翻译册 `docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml`：

| 声明条目 | 行 | 盘 | HEAD | dev | 真身 | 活户口 |
|---|---|---|---|---|---|---|
| `…/meta_question/wo001_003/generate_source_line_register.py` | 60894 | N | N | N | `…/wo_intake_reconcile/同名.py`（在册） | 第 60403 行 |
| `…/wo001_003/intake_batch.py` | 60902 | N | N | N | 同上（在册，另有 tests/） | 第 60411 行 |
| `…/wo001_003/replay_audit_to_jsonl.py` | 60910 | N | N | N | 同上（在册，另有 tests/） | 第 60419 行 |

⇒ 三条是**目录改名（wo001_003→wo_intake_reconcile）留下的重复户口**，不是资产蒸发。
`git ls-tree HEAD scripts/governance/meta_question/` 实测无 `wo001_003/`，有 `wo_intake_reconcile/`。
因此净删**不会**触发 TRANSLATION-COVERAGE 缺口（活模块仍被 60403/60411/60419 覆盖），
删的是 3 条死路径 + 其 3 段大白话简介（简介文本已随活条目在册，无信息净损失）。
本族另见：ROOR 里 `maintenance` 与翻译册同源的死键问题在 ENTRY_MANUAL/ENTRY_SPECS 侧也存在（W-52 关键发现 4）。

**取数命令** —

```bash
cd /d/ZephyrAlpha/.aidrafts/st-final-build-20260926
for f in generate_source_line_register intake_batch replay_audit_to_jsonl; do
  p=scripts/governance/meta_question/wo001_003/$f.py
  printf "%s disk=%s HEAD=%s dev=%s\n" "$f" "$([ -f $p ] && echo Y || echo N)" \
    "$(git cat-file -e HEAD:$p 2>/dev/null && echo Y || echo N)" \
    "$(git cat-file -e dev:$p 2>/dev/null && echo Y || echo N)"; done
git ls-tree --name-only HEAD scripts/governance/meta_question/ | head
```

**派生面 vs 手工面** — 翻译册条目由 `add_module_translation.py` 登记（半手工）。本环节暴露的是
"改名不追册"的派生断点：depgraph 有 `generate_project_depgraph.py --force` 重建规程，翻译册侧未见同权追改器。

**补丁条目** — `P54-*`（3 条整块删除 + 等价性证据）。**未应用**，且本 lane 禁改该热册（另进程在写）。

**未决问题** —

- Q-54a 注册表净删=high 门位（宪法 §5 第 2 条）⇒ 需 Owner 放行；本册仅备料。
- Q-54b 是否顺手补一个"改名→翻译册追改"派生器（净零要求它声明替代哪条既有脚本），未定。

## W-55 · 取号器 next_ruling_id.py 落地（在册最大号+在途占号感知+O_EXCL）

**判据/命题** — 落地=两问：①它在不在落地面（HEAD/dev 字节）？②它**在并发窗口里能不能真看到在途号**
（记录在案的失败模式=两会话自赋同号）。第二问才是合格判据。

**实测（带数）** —

1. 在册面（`ruling_registry.yaml`，dev 字节 390759 B）：`ruling_id` 出现 **231** 次，唯一全形 231，
   唯一数字干 **220**，最大干 **413**，带字母后缀子裁定 11 条；同号多干 4 组（19/20/203/206 合计 15 条 id）。
   ⇒ **在册无重复号**（231−220=11=后缀条数，账平）。此点先记死，防后续批次把"干数<条目数"误判为撞号去"修"。
2. 落地面：`git cat-file -e {HEAD,dev}:scripts/governance/next_ruling_id.py` 在**主区与 lane 四处组合全部 ABSENT**
   ⇒ 该工具只活在 lane 工作树（31264 B，未提交）。**未落地**。
3. 在途感知实跑（只读，不带 `--reserve`）：
   - lane 默认口（queue=`.runtime/commit_queue`）⇒ **在途=0**，建议号 **414**，并显式打印
     `WARN: 队列目录不存在…worktree 场景属预期`（不静默，符合"缺一源即降级并显式记录"的自述铁律）。
   - 同一次运行改指主区队列（`--queue-root /d/ZephyrAlpha/.runtime/commit_queue`，实测该目录 **570** 个对象）
     ⇒ 扫袋 750、册快照面最大 **415**（16 个快照）、提交信息面 412 ⇒ 建议号 **416**。
   - 两口相差 **2 个号**，且默认口给出的 414 与 W-56 实扫的在途自赋号**正面相撞**。
4. 占号面：`data/runtime/ruling_id_reservations/`（默认相对仓根）在 lane 与主区都**不存在/0 文件**
   ⇒ 它是 worktree 本地路径：O_EXCL 只在同一文件系统路径内仲裁，跨 worktree 形同虚设。
   代码自述（`DEFAULT_QUEUE_REL=".runtime/commit_queue"`、`DEFAULT_RESERVATIONS_REL="data/runtime/ruling_id_reservations"`）
   证实两源均按"仓根"解析，而 `find_repo_root()` 在 worktree 里返回的就是该 worktree。
5. 号段空洞 **193** 个（2..413 间未在册干）——工具如实报告、不复用，符合"只递增"取向；是否回收属政策题。

**取数命令**（cwd=lane，04:18–04:24+08:00）—

```bash
cd /d/ZephyrAlpha/.aidrafts/st-final-build-20260926 && export PYTHONPATH="$PWD/src"
python -c "import zephyr; print(zephyr.__file__)"
python scripts/governance/next_ruling_id.py --also-head dev
python scripts/governance/next_ruling_id.py --queue-root /d/ZephyrAlpha/.runtime/commit_queue --also-head dev
ls /d/ZephyrAlpha/.runtime/commit_queue | wc -l ; ls .runtime/commit_queue | wc -l
for rev in HEAD dev; do git cat-file -e "$rev:scripts/governance/next_ruling_id.py" && echo "$rev present"; done
```

**派生面 vs 手工面** — 取号器=**派生面工具**（三源并集取 max，禁手工背号）；但它的两个在途源
（队列袋、占号凭据）在 worktree 拓扑下都是**本地私有面**，于是"派生"退化为"按各自工作树派生"——
同号双赋的结构性根因不是人背错号，是**仲裁锚点不共享**。

**补丁条目** — `P55-*`：本环节无可应用行级补丁（工具未落地）。登记三条**提案**（代码/政策级，需另批施工）：
①占号目录与队列根改按 `git rev-parse --git-common-dir` 的公共层解析（跨 worktree 唯一）；
②`--reserve` 前置断言"若 REPO_ROOT ≠ git common dir 父目录 ⇒ 硬失败，除非显式 `--allow-worktree-local`"；
③取号后把凭据路径回打进裁定的 evidence 字段，使 W-56 的悬空面可被机械指认。

**未决问题** —

- Q-55a 落地窗口：战役期间该文件是否随本批入库？涉 scripts 净增（宪法 §4 第 1 条全资产净零）——
  须声明它替代哪条旧取号规程（现真源=`lane_construction_discipline_policy.md` §5 的"手工 git show 复算"）。
- Q-55b 公共仲裁锚放哪：`.runtime`（禁直写根）、`data/runtime`（业务数据目录）、还是 git common dir？
  三选一的副作用不同，需 Owner。
- Q-55c 193 个号段空洞是否回收（回收=同号复活，历史引用会被污染，本册倾向不回收，仅提请）。

## W-56 · 工作树自赋而 HEAD 查无的裁定号处置（悬空引用消雷）

**判据/命题** — 悬空引用=文档写着某号而在册面查无；消雷判据=每一处悬空号都能机械列址并分流。

**实测（带数）** — 全 `.aidrafts` 扫描（497 个基目录、**276,576** 个 .md/.yaml 文件，>3 MB 者 97 个跳过），
以 dev 面 `ruling_registry.yaml` 的 220 个数字干为在册集：

- 悬空数字干 **4 个 / 引用 49 处 / 覆盖约 24 个文件**（对称差集 = 引用集 − 在册集）：

| 号干 | 引用处 | 出现文件 | 分流 |
|---|---|---|---|
| 414 | 9 | 3 | 真·在途自赋：`st-mapbuild-20260924` 自己的 `ruling_registry.yaml` 第 5728 行已登记该号（裁定前缀+号干连写，本册刻意不复述），未提交；同 lane 的 `alignment_checklist.md` 多处引用；**与 W-55 默认口建议号 414 正面撞** |
| 415 | 8 | 4 | 真·在途：同 lane 册第 5762 行；且它是队列快照面实测最大号（W-55 第 3 条）——即"在途可见面"确实存在，只是默认口看不见。我 lane 亦贡献引用（`docs/_working/map_build/fig16_ruling/91_wordlist_and_roor_proposal.md` 第 26 行），如实自报 |
| 34 | 29 | 15 | 历史残引（落在 193 空洞号段内），集中在 `ff_j_control` 等旧战役数据文件；非自赋，属"册未登而文已引"的考古层 |
| 999999 | 3 | 2 | 噪声：`st-final-build-20260926/.runtime/tmp/leaf_f08/probe_dangling.md`（他会话红队探针）与 `_runtime` 侧产物 ⇒ 扫描面应排除 `.runtime/`（临时区永不作引用源） |

- 反向核验：`414`/`415` 两号在 dev 与 lane 的册里都**查无**（本册依规则不复述带前缀形态，只记号干）。

**取数命令**（cwd=`D:\ZephyrAlpha`，04:24–04:33+08:00，全程只读）—

```bash
cd /d/ZephyrAlpha && python -   # 在册集：git show dev:docs/.../ruling_registry.yaml 解析 ruling_id
# 引用集：rg/python 遍历 .aidrafts/*/docs 与 .aidrafts/*/ 的 .md/.yaml，正则取数字干，做对称差
```

**派生面 vs 手工面** — "哪些号悬空"=可派生（本册已给出可复现算式，且已证明必须排除 `.runtime`）；
而"号的语义/是否作废"=纯手工面。**建议把前者做成常驻报告器**（只读），后者继续走裁定。

**补丁条目** — `P56-*`（登记 4 个号干 + 代表地址 + 分流动作；`owner_gated: true`，本族不改任何文档引用）。

**未决问题** —

- Q-56a 414/415 的归属：mapbuild 车道的册副本先落，则本战役其他 lane 取到 414 必撞；
  需总筹指定"谁先让号"，并回填 W-55 的公共仲裁锚方案。
- Q-56b 号干 34 的 29 处历史引用：改引用（重编号）还是加"作废号"注释？改引用=动他人在途文档。
- Q-56c `.runtime` 探针噪声：是否宣布"临时区引用不计入悬空面"为正式口径（本册按此口径出数并留痕）。

## W-57 · 宪法 L0 三处漂移修正（走金哈希再生规程）

**判据/命题** — 先答"金哈希再生规程在不在、跑不跑"，再答"三处漂移是不是真漂移"。
关键判据：金哈希能**防篡改**，但它**测不出一句写错的话**——若 baseline 随漂移文本一起再注册，
规程会把错文吸收成基线。

**实测（带数）** —

1. 规程存在且可跑：`scripts/governance/meta/validate_rules_integrity.py`（C 层 golden hash；
   `--check` 校验 / `--register` 重基线；DB=`scripts/governance/meta/rules_integrity_db.json`，**已跟踪**，
   收录 17 个关键文件，`AGENTS.md` critical=true，基线 hash `5198a4bbda3d7593`，
   `registered_at` 2026-09-26T14:45:53Z，`last_check_at` 停在 2026-08-02T13:43:08Z）。
2. 三面哈希**全等**：DB=5198a4bbda3d7593 == lane 工作树 AGENTS.md == 主区 `git show HEAD:AGENTS.md`
   （12222 B 一致）。⇒ 金哈希视角"零漂移"，而内容层面确有错（下条）⇒ **规程存在但不作内容裁判**。
3. 漂移性质判读：`register()` 取 `git show HEAD:` 作基线，且
   `scripts/governance/gateway_post_commit_ritual.py` 第 26/85 行明文"触碰 rules 或 contracts → 执行
   validate_rules_integrity.py --register" ⇒ 修正一旦提交，post-commit 自动重基线，"再生规程"是**必做后置步**，
   不是发现器。
4. 三处漂移逐条复测（dev 面）：
   - §7 速查表第 109 行"数据集成器 `python -m zephyr.data`（7 子命令）"——实测
     `src/zephyr/data/cli.py` 注册 **8** 子命令（status/list/run/rerun-failed/pause/resume/start/speed-test）⇒ 真漂移。
   - §7 第 104 行"提交队列 …（enqueue/status/drain/requeue…）"——实测 `scripts/commit_queue.py`
     注册 **6** 子命令（enqueue/status/drain/requeue/cleanup/+1）⇒ 真漂移（列举不全）。
   - §7 第 110 行"仪表盘 `src/zephyr/frontend/dashboard/app_panel.py`"——该文件**存在**（23741 B），
     `api_server.py` 亦存在（233227 B）⇒ 非断链，属"真源该指谁"的语义争点。
   - 在册批文：议题册第 22528 行 `#ARCH-AGENTS-SSOT-DRIFT-001`（severity P2中，status **in_progress**，
     created 2026-09-25），其 title/description 已把三处写成"8 子命令/6 子命令/仪表盘真源 api_server"——
     与本册独立实测**前两处吻合**，第三处（api_server）是本册**不采信为断链**的一项。
5. 本 lane 的 AGENTS.md 与主区逐字节相同 ⇒ 补丁两面同文，无 lane 独有漂移。

**取数命令**（cwd=lane，04:10–04:18+08:00）—

```bash
cd /d/ZephyrAlpha/.aidrafts/st-final-build-20260926
grep -c "add_parser(" src/zephyr/data/cli.py scripts/commit_queue.py
grep -n "数据集成器\|提交队列\|仪表盘" AGENTS.md
python -  # 读 rules_integrity_db.json 的 AGENTS.md hash，与 sha256(normalize(工作树))、sha256(normalize(git show HEAD:AGENTS.md)) 三方比对
git show HEAD:AGENTS.md | wc -c
```

**派生面 vs 手工面** — 宪法 §7 速查表=**纯手工面**，且"子命令数"这一列本质可派生
（`add_parser` 计数即数出）；这正是 §9 第 5 条"静态清单禁手工维护"的违例面。金哈希=派生面但只管字节完整性。

**补丁条目** — `P57-*`：3 行现字节 + 2 行机读建议值（8/6）+ 第 3 行标 `owner_gated: true`；
附后置动作"提交后经 gateway_post_commit_ritual 自动 --register，禁手工改 DB"。

**未决问题** —

- Q-57a 仪表盘真源：`app_panel.py` 与 `api_server.py` 谁作 §7 唯一指针（或双列）？本册证据只支持"都不是断链"。
- Q-57b 是否把 §7 的"（N 子命令）"改为由生成器派生（净零：需声明替代哪份现手工表），未定。
- Q-57c 议题 `#ARCH-AGENTS-SSOT-DRIFT-001` 随本批关闭还是留 in_progress（它含本册不采信的第三处断言）。

## W-58 · 议题册 severity 变体归一（纯展示面）

**判据/命题** — 归一判据不是"把长得怪的改成标准的"，而是：先钉词表真源，再定"字母与中文词谁权威"，
否则 9 条 `P1中` 会被两套规则改到不同值。

**实测（带数）** — `docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml`：
`entries` 实测 **805** 条（ROOR 声明 761=STALE，见 W-52），`severity:` 行 **806** 行（含第 41 行
schema 注释 `str | str # P0致命 | P1高 | P2中 | P3低`，它是唯一的"词表声明"，**不是**词表条目）。
取值直方图：P2中 341 / P1高 321 / P3低 77 / P0致命 44（四正版=783）+ 变体 8 种共 **22** 条：
`P1中` 9、`P0高` 4、`P0紧急` 3、`P1严重` 2、`medium` 1、`P2低` 1、`P0阻断` 1、`P4低` 1。
消费面：`grep` 遍历 scripts/ 与 src/ 未命中任何读该册 severity 的代码；
`docs/01_policies_and_standards/rules/*.yaml` 无该枚举校验 ⇒ **"纯展示面"这一断言在本册实测面成立**（证据 B，
穷尽性受 grep 面限制）。无词表真源（`_registry/vocabularies/` 下无 severity 词表文件）。

两套候选归一规则（并列上报，不择一）：
- 规则 A=字母权威（P 级定档，中文词丢给该档标准词）：P1中→P1高、P0高→P0致命、P0紧急→P0致命、
  P1严重→P1高、P2低→P2中、P0阻断→P0致命、medium→无法定档（无字母）需人判、P4低→超词表需人判。
- 规则 B=中文词权威（词定档，字母丢）：P1中→P2中、P0高→P1高、P0紧急→P0致命、P1严重→P0致命(?)、
  P2低→P3低、P4低→P3低、P0阻断→P0致命(?)、medium→P2中。
两规则对 9 条 `P1中` 与 1 条 `P2低` 给出**不同结果**（A 保字母、B 保词）⇒ 不可机械归一。

**取数命令**（cwd=lane，04:02–04:05+08:00）—

```bash
cd /d/ZephyrAlpha/.aidrafts/st-final-build-20260926 && python -   # yaml.safe_load → Counter(severity)；行级正则在第 41 行之外取 severity: 值
grep -rn "architecture_issue_registry" --include=*.py scripts src | xargs grep -ln "severity"
```

**派生面 vs 手工面** — 全手工面：无词表册、无生成器、无 gate、无消费方 ⇒ 按宪法 §4 第 2 条
"零触发零消费→退役"的判据，这一列的**治理强度**本身可议（是退役该列，还是升格为带词表的受管制字段？）。

**补丁条目** — `P58-*`：22 条逐行现值 + 两规则各自建议值 + `owner_gated: true`（规则未择一前禁止机械回填）。

**未决问题** —

- Q-58a 先钉词表还是先改值：无真源词表时任何归一都是第二次手工断言。
- Q-58b `medium`（唯一英文值，条目 ARCH-GOV-001 系（无 # 前缀，非在册 ARCH 议题号））与 `P4低`（词表外档位）是改值还是补档？
- Q-58c 是否顺手给议题册加 severity 枚举校验 gate（净零要求它声明替代哪条现有 gate）。

## W-59 · 散件 10_d_data.md 归属（Owner-gated：本册只记不动）

**判据/命题** — 骨架给的是二选一（补 token 入库 vs 删）。本册实测**两套动作都不该做**，
因为前提"未跟踪"不成立：该文件是**被 .gitignore 显式排除的派生产物**。

**实测（带数）** —

- 主区 `docs/02_enterprise_architecture/02_domain_architecture_docs/10_d_data.md`：
  **1,743,761 B / 19,180 LF 行**，`git ls-files` 查无、`git cat-file -e {HEAD,dev}:` 均无。
- 骨架断言 19,037 行 vs 本册实测 19,180 行 ⇒ **差 +143 行**，两个数并列上报，不改写任何一方。
- `git status --porcelain` 对该目录返回 **0** 行（不是"忘了 add"）；
  `git check-ignore -v` 命中 `.gitignore:541` = `docs/02_enterprise_architecture/02_domain_architecture_docs/*.md`
  （第 542 行 `!…/README.md` 例外，故该目录 78 个 .md 中只有 README 在册）。
- 该规则**自带理由**（`.gitignore` 第 534-540 行注释）：这批 .md 由生成器从 depgraph（PostgreSQL）派生，
  可用 `scripts/serve_docs.py` 重生成；派生产物入 git 是"非收敛循环的数学根因"（生成器任一非确定性
  → diff → post-commit reconciler auto-commit → 永续循环），故"源真源已跟踪、派生产物离库"。
  受影响生成器名就写在注释里：`generate_domain_doc.py`（73 域文档）、`generate_path_tree.py`。
- 第二副本：`.aidrafts/st-mapbuild-20260924/docs/02_…/10_d_data.md` = **1,631,952 B / 17,810 行**，
  sha256[:16] `cb6128aa285ab662` ≠ 主区 `b1b176f02c8eef67`
  ⇒ 同一派生件在两棵树里各自生成、彼此分叉（1 行级差=内容差异 11.2 万 B），这才是真问题面。

**取数命令**（cwd=`D:\ZephyrAlpha`，04:36–04:40+08:00）—

```bash
cd /d/ZephyrAlpha
wc -lc docs/02_enterprise_architecture/02_domain_architecture_docs/10_d_data.md
git check-ignore -v docs/02_enterprise_architecture/02_domain_architecture_docs/10_d_data.md
sed -n '534,543p' .gitignore
git status --porcelain -- docs/02_enterprise_architecture/02_domain_architecture_docs | wc -l
```

**派生面 vs 手工面** — 该文件属**派生面**（depgraph→.md），且派生面被有意置于库外。
"补 creation_token 入库"这一选项与在库注释所载政策正面冲突：入库=把非收敛循环重新接上。

**补丁条目** — `P59-*`：**无行级补丁**（不入库、不删）；仅登记两条待裁事实（两副本分叉 + 行数断言差）。

**未决问题** —

- Q-59a 派生件分叉：两棵树 11.2 万 B 差是"生成器非确定"还是"depgraph 面推进"造成？需一次受控复跑（本 lane 不跑，会写盘）。
- Q-59b 若总筹要的是"可核对的交付快照"，正解可能是给派生目录加**内容哈希清单**（入库的是清单，不是 .md），需 Owner 定方向。
- Q-59c 骨架的 19,037 行与实测 19,180 行：保留哪个作对外数？本册不动别人的断言。

---

## 净零与内收自评（本族自身也是被审对象）

| 本册新增资产 | 净零声明 |
|---|---|
| `f05_registry_books_and_netzero.md` | 战役工作件（ttl=task_bound），TTL 到期由会话收尾流程处置，不入永久册 |
| `f05_registry_drift_patch.yaml` | 同上；且它是"补丁规格"，不新增 gate/脚本/规则册，故不触发全资产净零的替代申报义务 |
| 本族提案的新代码（P55-1/2/3、Q-57b、Q-58c） | **未施工**，仅在未决区挂账，若落地必须各自声明替代哪条既有规程 |

## 汇总（供总筹一眼核对；与上一报的差异都写"差在哪"，不写"我对他错"）

| 环节 | 本册复测数 | 上一报数 | 判 |
|---|---|---|---|
| W-52 ROOR STALE 行 | 19（两面同一 id 集） | 19 | 复现 |
| W-52 UNSPECIFIED/NO_COUNT | 1 / 1（不计入 STALE） | 未单列 | 口径补充 |
| W-52 summary 标量 | 4（total_registries/by_tier/by_status/by_medium） | 4 | 复现；动作=复跑再生器 |
| W-52 散文计数 | 库存 76 处（55 行）；硬撞车 26 处/24 行 | 53 | **未复现**：53 的判据未钉真源；两数并列 |
| W-53 域册错配 | 10 行（AI 可提案 5 / 需人判 5） | 10，其中 8 需裁定 | 总数复现；分流口径不同（本册把 2 条尺假阴性/设计性条目移出"需裁定"） |
| W-54 悬空翻译条目 | 3 条（死路径重复户口，活户口在册） | 3 | 复现，且补上"删之无害"的等价性证据 |
| W-55 取号器 | 未落地（4 面全查无）；在途默认口看不见（lane 队列 0 vs 主区 570），默认口建议号与在途号 414 撞 | — | 新证据 |
| W-56 悬空号 | 4 个号干 / 49 处（含 .runtime 探针噪声 1 干 3 处） | — | 新证据 |
| W-57 宪法 | 规程存在可跑；三面哈希全等；3 处漂移=2 真（8/6 子命令）+1 语义争点 | 三处漂移 | 部分复现（第三处不作断链采信） |
| W-58 severity | 805 条中变体 22 条/8 种；无词表无 gate 无消费方 | 纯展示面 | 支持该断言（证据 B） |
| W-59 散件 | 被 .gitignore 显式排除的派生件；主区 19,180 行、lane 副本 17,810 行，两副本分叉 | 19,037 行未跟踪 | **前提修正**：非"未跟踪"而是"有意离库"；行数并列不覆写 |

