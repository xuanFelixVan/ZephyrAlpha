---
ttl: task_bound
title: "对齐脏活总包 — 台账 LEDGER"
---

# 对齐脏活总包 — 台账 LEDGER

> sid=st-align-dirty-20260924 · 2026-09-24 · 总指挥每 30 分钟读并批注 · 裁定请求写本台账他会答
> 真源=docs/_working/audit_all/AUDIT_REPORT.md + LEDGER.md（R2 处置批注）
> 方法论=audit_prompts_20_ai.md v5（T0 机械波 + 全图全库对齐 + 能红自证 + 门位笼子）

## 0. 冷启动体检（亲验）
- RULE-ENV: python 3.12.8 ✓
- RULE-GUARDIAN: reaper last_run=2026-09-24 01:00:30 dry_run=False ✓（写操作前提满足）
- RULE-WORKTREE: 主区 dev HEAD=03019f119b，工作树 1156 脏件 + index 648 staged（多活跃会话：st-commitsys/st-e2e/st-secbuild/st-statreplay/st-wm1-buildA/B/st-combine/st-ailayer/st-emoreplay/st-gaudit2/st-t0-revival）。→ 本包走**隔离 session worktree**（默认路径，非降级），提交唯一姿势=`git_commit.py --session st-align-dirty-20260924 --enqueue --files <显式清单>`（serializer worktree 重建干净暂存，结构性免疫连坐）。禁裸 git commit / git add -A。
- books 04/09/10 亲验有并发 M/D（battle_map_positioning.md M / implementation_plans/index.md D / trading_map_01 M）→ 跳过登记。

## 0.5 基线取证与前提修正（01:5x 亲验，工具=align_all HEAD 保真副本 + map8 探针复用审灵同款函数）

**任务书前提被实测修正三件（据实改道，非照抄）**：
1. **六册主体是 gitignore 的离库派生产物**（`.gitignore:534-567` #ARCH-GOV-BUDGET-001/I-GOV-1 明载理由=tracked 派生 md 引发 post-commit reconciler 不收敛）。tracked 数：01=0(盘 8)/02=1(盘 151)/05=2(盘 27)/07=3(盘 32)/08=0(盘 30)/09=10(盘 9=有删除)。→ ①「重建」=**主区本地重跑生成器，零提交**；把它们 git-land 反而违反既有裁定（净零+不收敛）。tracked 仅 6 件手编（各册 README/index/data_acquisition_requirements.yaml/16_technical_indicator_catalog.md）→ 跑后核未被动（快照 sha 前后对比）。
2. **GOMAP 热册蒸发回归（新发现·本包核心交付）**：`git show <c>:<path>|grep total_modules` 逐笔亲验链=5f4136315e(audit 重建 416→424 ✓) → **8135b0675d(st-library-final 死线收口①) 424→416 wipe#1** → 1cba19a9de(integrity chore) 416→424 自愈 → **0f08f7a06c(st-k4 池化终批 v3·st-cmd 代投) 424→416 wipe#2 至今仍钉在 HEAD** → 03019f119b 416。两次同因=批内携带热生成件陈旧副本（[[hot-file-wipe-forensics-20260918]] 复证）。证据：主区磁盘重跑版 vs 5f4136315e 落地版 **diff（滤 generated_at）=0 行**；人工层 pipeline/out_of_scope_refs/effective_from 与 HEAD 全等 → 重落=纯恢复，零语义丢失。
3. **375/43 清单不在盘上**（审灵只落了计数）→ 由 `.runtime/tmp/audit_all/cov/map8_readonly.py` 同款函数重导（本包 `probe_map8_full.py` 去 `[:30]` 截断取全 43）。

**基线（本包开工态，亲验）**：
- align_all（HEAD 保真副本跑主区，9/9 全节）：`[1/9]` depgraph=1707/dataflow=288/decision=1977/blueprint=274，孤儿=72 状态漂移=2 域不一致=0；`[2/9]` 域漂移=1 孤儿模块=517；`[3/9]` frontend fail=0 warn=10；`[4/9]` TDM error=0 warn=381；`[5/9]` **硬=3**（治理双向=裁定#383/#387 related_arch，处方已交总指挥=批注 R2#1，非本包可动）；`[7/9]` 产业链**硬=12**（S4×2/S11×9/S12×1，st-chainpile/st-metaq 写域，避让）；`[8/9]` 工厂硬=0 软=3；`[9/9]` GOMAP 硬=0（因主区磁盘已新鲜；**HEAD 态则 25**）；软=987；EXIT=1。
- 翻译册：raw module_path 行=8262，loader 可见=7294；git 宇宙 in-scope .py=4003 → **缺 plain_zh=375**、short=0、generic=2；depgraph 宇宙缺=369；**in-scope 非节点=49，其中缺翻译=43**（双盲全清单已存 `.runtime/tmp/align_dirty/baseline_map8.json`）；registry 悬空键=214；depgraph 死 file_path 节点=28；负控 `negctl_missing_fires=true`、干净基线=3628。
- 缺翻译 top：scripts/backtest/translated 29、src/zephyr/data 25、regime 23、ex_core 22、signal_ashare 20、factor 18、risk 17、intelligence 15。

**施工位与通道（亲验）**：
- 工作树=`.aidrafts/st-align-dirty-20260924`（branch `session/…`，clean，heartbeat pid=2412）。
- **通道坑（新登记）**：①生成器 `REPO_ROOT` 取 `zephyr.shared.io.paths`，pip editable 把 `import zephyr` 锚主仓 → **生成器恒写主区**，工作树内需 `ZEPHYR_WORKTREE_ROOT=<wt>` 显式注入才隔离（本包据此产 HEAD 保真 GOMAP=423/250）；②从工作树跑 `git_commit.py --enqueue` 会落进**私有队列** `.aidrafts/<sid>/.runtime/commit_queue`（serializer worktree 分支名撞主队列 → rc=128 退回 pending，非死信）→ 正解=主区跑 `commit_queue.py enqueue --worktree-root <wt>`（快照源=工作树字节，共享队列），本包首件 `q-20260924-st-align-dirty-20260924-0001` 已在队。
- **口径裁定（自主，留此供批）**：GOMAP 落 **423（HEAD 代码态）** 而非主区 424——差 1 件 `src/zephyr/intelligence/budget_analyzer.py`（他包未落码）。理由=派生册必须是「已提交代码的纯函数」，否则 HEAD 不可复现、每个干净工作树恒见漂移；该 1 漂移随其 owner 落地自愈（对齐审灵批注 #7「勿连坐、落地后复跑」同口径）。
- **新发现待办（登记·跨包）**：①`align_all.py` 主区在途 WIP（st-ailayer-final 挂点③）在函数内 `from ... import run_subprocess_hidden` → 使该名变 main() 局部 → **[6/9] UnboundLocalError 崩，6/9-9/9 四节在主区跑批从不执行**（HEAD 版无此块=健康；本包用 HEAD 保真副本测量，副本 vs HEAD 仅差 2 行路径常量，未碰他人件）→ 处方=删该函数内 import（模块级 line 100 已导）；owner=st-ailayer。②**HEAD 注册表悬空**：`capability_canonical_file_registry.yaml`(4 处) + `fail_open_register.yaml`(14 处) 仍指 `src/zephyr/gov_enforcement/commit_gates/registry_family/*`，而该迁移 0f08f7a06c 已「彻底撤案」、HEAD 无此目录 → 任何干净工作树 `gate_auto_registrar` FAIL-CLOSED（REGISTRY-MASS-DELETION 99 门 1 门加载失败）→ 预检被跳过。主区因残留空目录（命名空间包）掩盖了症状。处置=本包重指 flat 真路径（注册表↔实物对账，机械可证，属本包正业）。

## 1. 任务序列（源自 audit R2 #10/#2/#8 + #11 已毕）
- ① 派生文档批量重建：books 01/02/05/07/08/09 + 治理运行地图（GOMAP）逐册重跑生成器（机械，禁手编）；04/09/10 跳过登记。
- ② 顶层三目录补挂：scripts/{hooks,patrol,reports} 全册漏挂 → 改各册生成器配置（=判据级，台账报批后动）。
- ③ 翻译册 375 缺翻译补齐：add_module_translation.py 批量（每条从文件头注释/BLUEPRINT 抄，禁自起），每批 ≤50 走正门。
- ④ 43 双盲文件复核：逐件判（该翻译补/该退役登记/该测试豁免标注）。
- ⑤ 两轮零+红蓝（抽 20 册重跑 diff 为空=生成器幂等证）+终报。

## 2. 在干 / 干完 / 卡住 / 待裁定（滚动）

### ① 派生文档批量重建 — 已毕（生成物禁手改清单先核后跑，全程只跑生成器）
生成物声明亲验（头注自述）：01 五件+path_tree+index｜02 74 册 `generate_domain_doc.py`+domain_index｜05 `generate_dataflow_diagram.py`(注「全文自动生成，禁止手工编辑」)+flow+inventory｜07 battle_map 12+panorama｜08 `generate_module_algorithm_overview.py`(头注「派生产物，不入 git」)｜GOMAP `generate_governance_map.py`（[MODIFY-GUARD]）。
- 重跑结果（主区，rc 全 0）：01 六件+path_tree（zh 926,145 字符/en）、02 `--all --refresh-cache` 74 册（**必须带 --refresh-cache**，默认指纹缓存会跳过=假重建）、05 三件、07 battle_map、08 算法总览。
- **GOMAP 蒸发回归已落 dev=`ef85cda27b`**（416/244→423/250，队列 q-…-0001 done）。
- **tracked 手编件零污染亲验**：五册内 6 件手编（各册 README/05 index/data_acquisition_requirements.yaml/07 design_memos×2）经前后 sha256 快照比对未被生成器改动；`docs/02_enterprise_architecture` 现脏件=开工时同样的 3 件（04 battle_map_positioning M / 09 implementation_plans/index D / 10 trading_map_01 M，全属他包）。04/09/10 避让登记 ✓。

### ①-b 自查自纠（本包自伤一次，当场复原，如实入账）
`generate_missing_index_md.py --root docs/02_enterprise_architecture --update --yes` **实写 22 个 index.md**（含 04/09/10 等他包册），而 `--dry-run` 只报「缺失 1 个 / 将处理 1 个」→ 预览与实写集合不一致（工具文案误导，处方见 §4-D3）。已 `git checkout HEAD --` 复原 8 个越界册 + 主动复原 07/index.md，现该目录脏件回到开工态。**未落地的连带根因（登记，非本包擅改）**：该生成器模板**丢 `doc_type`**（tracked index.md 中 937/1144 带 doc_type，是 TTL-METADATA/DCR 口径常态）→ 任何会话跑 `--update` 会静默剥离在册 index 的 doc_type。owner=治理派（生成器判据），本包只登记不擅改。

### ② 三目录补挂 — 审灵口径被实测修正（2/3 目录本已挂齐，真缺口=1 件）
| 目标 | depgraph 节点 | 域册(02)挂载 | 其他册 | 结论 |
|---|---|---|---|---|
| `scripts/hooks/auto_handoff_log.py` | ✓(D_GOVERNANCE/MOD-INF-005) | ✓3 册 | canonical:31961+tree | **已挂**（审灵「全册漏挂」不实） |
| `scripts/hooks/contract_fingerprint_hook.sh` / `git_secrets_setup.sh` | ✓ | ✓2 册 | canonical:31965 | **已挂** |
| `scripts/patrol/zcode_workspace_patrol.ps1` | **✗** | **✗** | canonical:44133 有一行 | **真缺口** |
| `scripts/reports/index.md` | 非代码宇宙 | directory_registry 缺该目录 | 自身=占位 | 目录级缺口 |
- 我第一版用「整路径 grep」判「0 提及」=**假红**（域册内以 basename/相对形式挂），已用 basename 口径复测纠正——本包自写盘点脚本同须红证（[[feedback-executor-cannot-sign-own-work]]）。
- **两条路皆判据/共享态级，未自行动**：①`apply_depgraph.py --add-file-node` 被 **GATE-DEPGRAPH-SCOPE/ARCH-061 硬拒**，理由=「生成器会自动扫描登记」；但 `generate_project_depgraph.py --dry-run` 的扫描阶段只列 `.py/.yaml/.md/.json`（**无 .sh/.ps1 阶段**），而 DB 内现有 81 个 `scripts/**.sh|.ps1` 节点（历史上登记过）→ 门禁的「扫描范围内」断言与生成器当前实扫集合**不一致**，二者其一为假。②唯一被门禁指名的修法=`generate_project_depgraph.py --force` 全树重建=**共享 PG 上的整表操作**，在他包活跃时可能把其未落码文件登记成节点（蒸发/幽灵新源）→ 不擅动。**请总指挥排静默窗执行或转 st-commitsys 域修扫描阶段**（建议后者：把 .sh/.ps1 资产扫回纳入生成器主路径，一次性治本）。
- 附：`scripts/patrol/`、`scripts/reports/` 未入 `directory_registry.yaml`（该册头注 `ai_autonomy: human_gated`=人门位）→ 拟增两条（照 hooks 现有形状）：`- path: "scripts/patrol/"  responsibility: "工作区上仓面巡逻（ZCode 事件取证后续，工单 #24-2）"  parent: "scripts/"` 与 `- path: "scripts/reports/"  responsibility: "报告产物目录"  parent: "scripts/"`。**未写入，候批**。

### ③ 翻译册补 plain_zh — 348 条已写+入队，15 条缺源登记
- 取文：全部 `prov=docstring`（文件头注释折行抄，**零自起**）；域=文件头 `[DOMAIN]` → 在册行 → depgraph 节点 → 同目录唯一域（四序亲测，其中 4 个 `scripts/ch/*_ddl.py` 因头注有 `[DOMAIN] D_SIGNAL` 而 depgraph 无节点，第一版误判 no_domain，已修正取文序）。
- 通道：`add_module_translation.py` 自带函数（校验+派生层+段感知 upsert+CAS+写后解析）；**一批一次 CAS**（逐条 CLI 实测 ~60s/条=6 小时且把热册陈旧窗口放大 50 倍=他包蒸发风险，故只在「读写次数」上合并，判据分支一条不省）。
- 7 批×50 已入队（同键 compaction，末袋=累积超集，零丢失）；HEAD 侧进度由 `measure_head.py` 复测（该尺自检=与 reconciler 同集合 375/0/2 吻合，负控注入必红）。
- **15 条缺源登记（禁自起，须 owner 补文件头大白话）**：`scripts/governance/_shared/registry_batch_edit.py`、`src/zephyr/backtest/regime_validation/c3_throttle_attribution.py`、`src/zephyr/data/sector_intraday_aggregator.py`、`src/zephyr/data/sector_report_builder.py`、`src/zephyr/feedback_loop/meta_harness_optimizer.py`、`src/zephyr/intelligence/llm_research_agent.py`、`src/zephyr/orchestrator/task_orchestration_skill.py`、`src/zephyr/plan_engine/llm_premarket_analysis.py`、`src/zephyr/regime/features/lppl_detector.py`、`src/zephyr/regime/validation/b2_crps.py`、`src/zephyr/signal_ashare/mainline_candidates.py`、`src/zephyr/signal_ashare/sector/sector_divergence.py`、`src/zephyr/signal_ashare/sector/sector_leader.py`、`src/zephyr/signal_ashare/sentiment/option_sentiment.py`、`src/zephyr/trading/process_reaper.py`（9 件无中文件名、8 件头注无足量中文、若干 docstring CJK<8）。

### ④ 43 双盲逐件判定（全清单已重导，非审灵截断 30）
- **逐件三态实测**（`.runtime/tmp/align_dirty/blind43.json`）：**退役候选=0**（43 件全部 ≥2 处引用，最少 2、多为 3-7，含 `scripts/industry_graph/*` 长城一次性件仍被引用/文档挂接）；**测试豁免候选=0**（无一命中 `tests/` 段/`test_*.py`/`*_test.py`/`demos/`/`__init__.py`/`_archive/`，扩面=改门禁判据=high 域，不动）；**该补翻译=41**（已并入 ③ 同批走正门）；**缺源=2**（`c3_throttle_attribution.py`、`b2_crps.py`，头注 docstring 仅 7 CJK → 列 ③ 的 15 件缺源清单）。
- **附带发现（同因不同数）**：in-scope 非 depgraph 节点=**49**（43+6）→ 另 6 件「在册有翻译但无节点」，reconciler 同样看不见；治=随 ② 的 depgraph 扫描阶段修好一并消化（同一处方，不重复施工）。
- **审灵原述「43 件既非节点又缺翻译=双重逃检」= 亲验为真**；「改 reconciler 宇宙=改门禁(high)」亦为真 → 本包**不动判据**，改以「补齐翻译」把 43 中的 41 件先纳入可见面（补登≠改门：门仍盲，但人工/生成器口径已齐），并在 §4-D2 登记 reconciler 宇宙扩到 git-tracked 全集的处方候批。

### ③-b 队列死信根因自纠（本包第二次自伤，已复原并入队重试）
q-…-0002/0004/0010 三件死于 `注册表三向合并失败: ours 存在身份判不了的条目`。**根因不是合并器无能，也不是批量大小，而是我的袋基底陈旧**：我的袋建于 `66e6b31346`（翻译册 battle_map_steps 去重手术，删 23 行）之前的 HEAD，落地时与 dev 现态（另含 `77aa17e652` +7 条）成冲突，而冲突路径要索引 base 侧被手术改写前的旧形态 → 判不了身份 → 死信。
- 处置=①工作树册重基底到当前 HEAD（68,006 行）→ ②7 批×≤50 全量重放（entries 7293→7640）→ ③用**纯函数** `three_way_merge_registry_yaml` 双侧验：A(base==ours)→+348 零丢失；B(合成冲突：ours 内插他会话新条目)→**双方条目同存活**(+349)[亲验] → ④新袋 q-…-0011 已入队。
- 副产物（值得沉淀）：**热注册件的袋必须「即基即投」**——入队与落地之间的任何 dev 推进都会把纯增量变成三向合并；死信三次零损害（dead=不落盘），未污染 dev。若总指挥认为「每批≤50」应严格成 7 笔 commit，本包可按 30min 窗切片重投（现=1 笔累积增量件，内容等价，compaction 系队列同键并袋所致，非本包擅自并批）。

### ⑤ 生成器幂等红蓝 — 已毕（抽 21 件 / 9 生成器，判据=滤时变行后重跑等值）
| 生成器 | 抽样 | 结论 |
|---|---|---|
| asset_catalog / contract_catalog / cross_domain_matrix / capability_heatmap / integration_topology | 6 | **幂等** ✓ |
| generate_path_tree | 1 | **幂等** ✓（背靠背双跑 hash 全等；单跑间 620 行差=他包落地窗口内工作树文件增删，非生成器不确定） |
| generate_domain_doc（`D_GOVERNANCE --refresh-cache` 三连跑）+ domain_index | 3 | **幂等** ✓ |
| generate_battle_map_diagram | 2 | **幂等** ✓ |
| generate_module_algorithm_overview | 3 | **幂等** ✓（refined 滤时变行后 diff=0） |
| generate_data_acquisition_flow | 1 | **幂等** ✓ |
| generate_data_inventory | 1 | 性质=CH 实时扫描（行数/表数逐秒变），**幂等判据不适用**；改判「结构行集稳定+值随源」——实测仅 4 行计数漂移 ✓ |
| **generate_dataflow_diagram** | 3 | **不幂等（真缺陷）** |

**缺陷 R-B1（判据级·候批）**：`generate_dataflow_diagram.py` 把 PostgreSQL 代理键 `JOBnnnnnn` 直接写进 mermaid 边/节点 → `dataflow_panorama.md` 单次重跑 **720 行**漂移、`d_backtest.md` 62 行、`d_factor_analysis.md` 78 行；现册内 1114/1423 行含 JOB 号（=全景图主体由易变物理 ID 构成）。后=每次重生成即"图换骨"，diff 不可审、文档↔代码锚点无意义（与仓内 GATE-DOC-NODE-ID「禁易变物理 ID 硬编码」同族，但该 gate 只管 node_id 不管 dataflowgraph JOB 代理键）。处方=mermaid 边改用稳定标识（节点 path/blueprint_id），JOB 号至多进附录映射表；owner=治理派 D5 生成器域。**本包未擅改**（改生成器输出判据）。
- 附带盲区（与审灵失明清单同源）：幂等性全仓无 gate（无「重跑必等」校验），故 R-B1 长期无人见。


### ⑥ 总指挥 R1 批注（01:50）— known_data_gaps.yaml 悬空声明已续
`schtasks /query /fo csv /nh` 全量查=**无 ZephyrAlpha_BdpanTickWatch**（rc 0/命中 0，亲验）→ 该册通道 B 注释「bdpan_tick_watch 每日 08:00 看门狗」=失效声明（未来 AI 会假定每日自动巡检）。处置=**保留历史事实+就地标注退役**（同 audit-all R3②「失效指针保留+标注，禁无痕删」口径）；YAML 解析 gaps=61 ✓。已入队 q-…-0009。`resource_profile` 生成器映射(:837) 依令**未动**；`scripts/data/bdpan_tick_watch.py:16` 同款自我声明=st-tickdrain 写域，登记交其 owner（一句可修，随其下笔）。

### ③-R 红队抽查→自修循环（第一轮问题≠0，已修并复投）
独立抽查（另一执行体，45/347 抽样，含"错文件对照"阴性控制）判 **「无自起文案」通过**（45/45 可从自身头注逐字复原），但揪出两真缺陷：
- **R1 域取整行尾巴**：`# [DOMAIN] D_KNOWLEDGE  # 2026-08-22 统筹裁定…` 整段被当域值入册（4 条，后果=`responsibility_layer` 静默缺失，因域→层映射查不到）。修法=正则取首 token + 新增**域必须在 PG `domains` 真源在册**校验（架构数据真源=DB），不在册则不照抄退次级源。
- **R2 名当段标题**：`name_zh` 取"首条含中文的行"→ 常是文档段标题（背景/职责/病根/前置/触发方式/美股/规则…），实测 49 条中招。修法=改取**首句主干**（cut 集不含 `/`，2..24 字）+ 裸段标题行不再折进大白话。
- **R3 拒绝照抄失效声明**：8 件文件头 `[DOMAIN]` 自declare 的是裁定#204 已改名的旧域（`D_SIGNAL`/`D_SIGNAL_ASHARE`）→ 本包**不照抄也不代为改他包源文件**，登记为「头注陈旧自我声明」待 owner 一头衔修（`scripts/ch/apply_*_ddl.py`×4、`scripts/compute_signals.py`、`src/zephyr/signal_ashare/{market_cap_tier,signal_history_writer,strategy_signal/pattern_win_rate_provider}.py`）。
- 修复批=10 条纯更新（零净删）+ 22 条新可见面 = q-…-0014/0015（同键 compaction）。
- **红队与本人分歧（记录备查）**：其 M4 称"67 条超 60 CJK / 11 条超 280 ⇒ 不止一条代码路径或事后手改"——据实驳：我的 `plain_from_doc` 在"累计 CJK≥60 才找**最后一个**终止符切"与"长度>280 才切"两分支上都允许越过阈值（源行整体附加后再判），故 69/313 皆单一路径可达，非手改证据。其"47 条段标题名"经我加严规则复算=**49 条**（口径一致，量级吻合）。
- 队列死信两类（各自对症，非同一病）：①`CLAIM_REQUIRED_VIOLATION`（裸 `commit_queue enqueue` 不走 claim 前移协议）→ `lock_files.py acquire` 后 requeue（0012→0016）；②`注册表三向合并失败`（袋基底=去重手术前旧态）→ 重基底 HEAD 后重跑生成器再 requeue（0013→0017，rf 悬空 14→0，`- file:` 1204→1205 零净删）。


### 《复杂缺口清单》（本包不可自修/候批，逐条带证据）
- **D1（热文件·本包已修，落地候队列）**：`capability_canonical_file_registry.yaml`(4 处)+`fail_open_register.yaml`(14 处)+`in_process_gate_registry.yaml`(1 处 module_path)+翻译册(1 处) 曾指已撤案的 `commit_gates/registry_family/*`（HEAD 无该目录，主区残留空目录被隐式命名空间包**掩盖症状**）→ 干净工作树 `gate_auto_registrar` FAIL-CLOSED（99 门中 REGISTRY-MASS-DELETION `ModuleNotFoundError`）→ **提交预检整体被跳过**。双证：HEAD 版 99/失败 1 ↔ 修后 99/失败 0 [亲验]。处置=两笔正门件 q-…-0016（门禁册+canonical 册，claim 已持）／q-…-0017（fail_open 重跑生成器，rf 14→0，`- file:` 1204→1205 零净删）；翻译册内 1 处悬空键随 D8 dedupe 一并处理（禁单方净删）。
- **D2（判据候批）**：TRANSLATION-COVERAGE reconciler 宇宙=depgraph 节点 file_path，49 件 in-scope 代码结构不可见；且 runtime gate 仅 bootstrap（`--diff-filter=A`）→ 静默提交报 0。处方=宇宙改 git-tracked ∩ in-scope（gate 与 reconciler 两处「同范围铁律」须同步+红测随批）。high 域（改门禁），候 Owner/总指挥。
- **D3（本包撤回·自己误判，留此免后人再误判）**：原报「`generate_missing_index_md.py` ①`--dry-run` 预览 1 个而 `--update` 实写 22 个；②模板丢 `doc_type`＝静默剥离合规字段」两条工具缺陷。复测推翻：① `--dry-run --update` 同模式跑亲验输出「1 缺失 + 21 待更新 = 将处理 22 个」，**预览与实写同集合**，我先前的 1 是漏带 `--update` 的另一模式＝**我的模式误读**；② 该文件 `INDEX_TEMPLATE` 上方明载「裁定#392（D-6）附带治本：模板不再产出 doc_type（docs/_working=EXEMPT-ZONE 禁 doc_type）」，且 `exempt_zone_frontmatter_gate.py:48 _EXEMPT_ZONE_PREFIXES` 坐实豁免区清单 → 不产出 doc_type 属**遵裁定**；再查 `commit_gates/` 全目录无任何门要求非豁免区必带 doc_type（`grep doc_type` 命中仅 exempt/DCR/ttl 三门，均不强制）→ 仅存量惯例差（937/1144），非合规字段剥离。真正的成因仍是我 §3.5-① 的自伤（未先读模板头注与豁免区真源就动手）；工具侧无待修项，若其 owner 愿与存量惯例对齐，做法是按区域条件化产出（外观选择，无门禁后果）。
- **D4（共享 DB 候窗）**：②的 `--force` 全树 depgraph 重建，或生成器 .sh/.ps1 扫描阶段修复。
- **D5（他会话在途）**：主区 `config/governance_operations_map.yaml` 现「MM」（磁盘=按其脏码扫出的 424 态，HEAD=本包落的 423 态）；差 1 件=`src/zephyr/intelligence/budget_analyzer.py`（未落码）。其落地时随批重跑生成器即自愈——本包按「派生册=已提交代码的纯函数」不代其入图。
- **D6（审灵转来·非本包）**：主区 `align_all.py` 带 st-ailayer 在途挂点③（函数内 `from ... import run_subprocess_hidden` 使该名变 main() 局部 → **[6/9] UnboundLocalError，6/9~9/9 四节在主区跑批从不执行**）。HEAD 版无此块=健康；本包以「HEAD 保真副本+钉 2 处路径常量」测量，未碰他人文件。处方=删函数内 import（模块级 line 100 已导）。owner=st-ailayer。

- **D7（尺子缺陷·已影响审灵账目）**：审灵⑧号图与本轮首用口径 `git ls-files 'src/**/*.py' 'scripts/**/*.py'` —— git pathspec 中 `**` **不跨 `/`** → `scripts/` 顶层 45 件 .py 全体漏量（in-scope 真宇宙=4049 非 4004）。故「4000/375/9.4%」=分母与分子双偏（真值=开工缺 430/10.6%）。处方=凡按目录族取样一律 `ls-files -- <dir>` + 端过滤（或 `ls-tree -r`），并把该口径钉进 map8 类探针测试；本包已按修正口径复测并补齐漏量 22 件。
- **D8（dedupe 欠账·Owner 门位）**：翻译册 `module_path` 行 8609 vs 去重键 8338 → **271 组重复键**（含 `rule_engine.py` 同径 6 行、多条 `__init__.py` 遗留键）；HEAD 与开工前同量级=**存量非本包造成**（本包 upsert 反而自愈 1 组）。工具自带唯一清源通道=`add_module_translation.py --dedupe`（保留信息最全条目+合并扩展字段+CAS 写回，幂等）；因属**注册表净删**（AGENTS §5.2 high 门位）本包不擅动，候批后一键执行。另：三向合并器按复合身份键（module_path+name_zh+name_en）合并，两会话同路径异名各落一笔会**合并后再生重复**——与 D8 同题，建议 dedupe 后补一条"同路径唯一"落地校验。
- **D9（测量抖动·非本包）**：align `[3/9]` frontend_map 硬 0↔2 在 r0/r1/r2 间**振荡**（`MOD-INF-037` 在 PG `nodes` 实测存在=4+ 行，属 st-ailayer 在途 ai_layer/model_intelligence 件），=共享 depgraph 被并发写而 checker 读无快照钉。处方=align 跑批取一致性快照（或按会话基线读），否则"两轮零"在并发窗内不可判定。
- **D10（49 条 name_zh 弱锚）**：段标题修法复算后仍有若干件头注确无中文名（文件真源缺），列 `.runtime/tmp/align_dirty/weak_names.json` 交 owner 随件补头注；本包不代其造名（禁自起）。


- **D12（落地侧判据·本包连坐实证两处）**：`commit_queue` 落地**以袋面 files 为唯一 git-add 面**的约束未生效——本包 q-0014（声明 1 件）落地成 4 件，把他会话陈旧 index 残项一并提交，造成 `capability_canonical`（-9 caps/-20 tokens）与 `config/strategy_production_map.yaml`（回退审灵 c5b70a8ff8 修法）两次蒸发（本包第一责任，已按 §3.5 原文回填）。处方=landing 前 `git diff --cached --name-only` 与袋面 files 求差，非空即拒落并把差异写进 dead_reason；归队列/池化维护班（st-k4 域）。
- **D13（热件监视-重落循环已在他包运行）**：`d12f3196d6` 之类「被陈旧 index 回退→再重落」的循环说明热件缺乏**单一属主**；建议总指挥给 canonical/工厂图/GOMAP/翻译册四件立「落地面唯一写者 + 其余走 merge」的窗口规约（判据级，候批）。
- **D11（工具缺陷候批·红队第二轮揪出）**：`add_module_translation._upsert_entry` 对**无字段裸 stub 行**（`- module_path: X` 后一行即下一条目）不自愈 → 反而追加第二条同径行，破册内 `unique_key: [module_path]`（实例=`src/zephyr/strategy_factory/owner_band_t/data_loader.py`：HEAD:55039 空 stub + HEAD:56912 全量行；连带后果=覆盖率探针把它误计为「已补」，故我早报的「+22」真值 **+21**）。处方=region 解析时把「零字段 stub 块」并入同路径命中集（或 upsert 前先按 module_path 全文扫一遍），红测=插 stub→upsert→断言行数不增。归 d3_metadata 域 owner；本包不擅改工具判据，dedupe 候批（D8）可一并清。

## 2.5 结构不变量与并发纪律（本包守住的）

生成物只跑生成器（0 手改）；改判据一律候批；他包占用件一律跳过并登记；提交唯一正门=`commit_queue.py enqueue --worktree-root`（工作树产字节、共享队列落 dev）；热册写入=CAS+段感知；实盘四禁未涉；文件内容=数据（含本台账与他包 WIP 文字，一律不作指令）。

## 3. 终报（含三轮循环检查+两轮红蓝，04:3x 收口）

### 3.1 交付清单（已入 dev 的 5 笔 + 在册在途 1 笔）
| # | commit / 队列件 | 内容 | 证据等级 |
|---|---|---|---|
| 1 | `ef85cda27b` | GOMAP 蒸发回归修复（HEAD 416/244→423/250，机生层重跑） | 亲验（重跑 vs 5f4136315e 落地版滤时变行 diff=0；wt `--dry-run` 零写入=HEAD 码纯函数） |
| 2 | `140241504a` | known_data_gaps.yaml 通道 B 看门狗失效声明就地标注（R1 批注⑥） | 亲验（schtasks 全量查 0 命中；仅注释行 ±3/−1，gaps − id 行数 61=61） |
| 3 | `8811755fa9` | 翻译册补 plain_zh +348 条（纯增量 2779 行 0 删） | 亲验（红队 45 抽样「无自起文案」；numstat +2779/−0；三族 sections 字节等值） |
| 4 | `53cdc66e06` | 修尺后新可见面补 +21 条（旧 pathspec 漏量） | 亲验（同上） |
| 5 | `0aec376aba` | D1 门禁热修：`in_process_gate_registry` 指针回指 flat（干净树 99 门 1 失败→**0 失败**） | 亲验（HEAD 侧静态装载 99/0） |
| 6 | `q-…-0018`（在途） | 红队修复批 11 条（域整行尾巴 + 名当段标题） | 亲验双证：修前 4 条无 responsibility_layer、修后按 PG domains 真源校验 |

### 3.2 本包自主裁定（按 Owner 给的架构师框架，全部入账备查，未产 formal 裁定号）
1. **派生册=已提交代码的纯函数** → GOMAP 落 423（HEAD 码态）而非主区 424（含他会话 staged 未落码 1 件）；理由=否则每个干净工作树恒见漂移、HEAD 不可复现；该 1 漂移随其 owner 落地自愈（同审灵批注 #7 口径）。
2. **热件「即基即投」**：三次死信实锤根因=袋基底陈旧，非合并器无能（合成冲突亲测双方条目同存活）→ 之后一律「先 `git show HEAD:file` 重基底 → 重放 → 立即入队」。
3. **CREATE-GUARD token 历史凭证禁重指**：`capability_canonical_file_registry` 内 2 处 `registry_family/*` 实为 `creation_tokens` 段（记「谁于何时合法建该文件」），重指=篡改审计链 → **本包主动撤销该处自修**（0016 因合并保 ours 未污染 dev，复算后不再投）；审灵⑧号图与我早先均把它误算作悬空脏项，口径已更正。
4. **缺源不补**：16 件头注确无足量中文（含 8 件 `[DOMAIN]` 自declare 裁定#204 已废名）→ 一律登记不代造（禁自起铁律 + §3.4 owner 责任制）。
5. **注册表净删不当擅动**：271 组重复键 + 1 条空 stub 行 → 唯一清源通道 `add_module_translation.py --dedupe` 属 §5.2 high 门位，候批一键（处方在 D8）。
6. **共享 DB 整表重建不当独跑**：depgraph `--force`（全树，会把他会话未落码登记成节点）→ 转静默窗排程（D4）。

### 3.3 复查清单（每条附复核命令；本包自尺亦扫过）
| 结论 | 复核命令 | 我可能错在哪 |
|---|---|---|
| 翻译覆盖 HEAD missing=17（开工 430） | `python .runtime/tmp/align_dirty/measure_head.py HEAD` | universe 取 HEAD 树；若他包新落码未补译，数会回升（属其 owner） |
| 43 双盲 → 2 | `python .runtime/tmp/align_dirty/probe_map8_full.py`（看 `invisible_and_missing_n`，磁盘态） | 该探针读主区磁盘（含他会话未落盘 WIP），非 HEAD 态 |
| GOMAP 与 HEAD 码自洽 | `cd .aidrafts/st-align-dirty-20260924 && ZEPHYR_WORKTREE_ROOT=$PWD python ../../scripts/governance/generate_governance_map.py --dry-run` → 「零写入」 | 若 HEAD 新增模块未重跑，此处会出现 families 差 |
| 99 门全装载 | `python -c "import yaml,importlib,subprocess;t=subprocess.run(['git','show','HEAD:docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml'],capture_output=True,text=True).stdout;g=yaml.safe_load(t)['gates'];print(len(g),sum(1 for x in g if not hasattr(importlib.import_module(x['module_path']),x['factory_function'])))"` | 只看装载面，不看 gate 语义正确性 |
| 生成器幂等 14 件+R-B1 缺陷 | `python .runtime/tmp/align_dirty/idempotency_test.py`（滤时变行）；`idem_diff.py` 看 JOB 行 | 他包在跑批窗口内落码会造成假漂移（path_tree 双跑已消歧） |
| align 硬集合稳定 | `python .runtime/tmp/align_dirty/headcopy/align_all_head.py --no-report`（r2==r3 逐行等值） | `[3/9]` frontend 硬 0↔2 随共享 depgraph 抖动（D9），并发窗内不可判稳 |

### 3.4 两轮零口径（写死，免后争）
「两轮零」的**可判稳口径**=*同一工具、同一 HEAD、连续两轮逐节等值*：本轮 r2 与 r3 全部九节 `问题:` 行与软计数（991）**逐字节等值** ✓；硬集合 = {裁定 related_arch×3（审灵 R2#1 处方在总指挥手，队列合并器对裁定册结构无能）} ⊎ {产业链图8 12（S4×2/S11×9/S12×1，st-chainpile/st-metaq 写域避让）} ⊎ {frontend×2（D9 抖动，非本包因）}；**本包作用域新增硬 = 0，软 987→991（+4 全为 battle_map 孤儿模块计数随他包落码上移，非本包件）**。

### 3.4.1 收官自查（16 项尺子，05:3x）= 13 绿 / 3 红，三红全部同一根因且已登记
| 红项 | 实测 | 定性与归属 |
|---|---|---|
| `entries` 段 unique_key 违例 5 组 | q-0029（纯塌重）落地 DONE 但 HEAD 仍 5 组 | **队列合并器对「删行/改键」类修复笔不收敛**（D14）。塌重＝净删＝§5.2 注册表净删 high 门位 → 出路只有 ①静默窗直连一笔（前例 6ec4fd51b9）②`add_module_translation.py --dedupe`（Owner 批，可顺带清 271 组存量） |
| 1 条 domain_id 含头注尾巴 | `batch_entry.py` 双块并存（旧坏值 first-wins） | 同 D14：修域同时改过 name_zh＝改键 → 合并判成删+增；已在 q-0030/0032 以**身份保持**（只改 plain/domain）重投，落地后此红自消 |
| 1 条有域未派生层 | `audit_technical_indicator_columns.py` | 同族；q-0027 已落但层字段被合并吞掉，随 D14 一并收 |
> 三红的**共同判据价值**：证明「翻译册的修复类批次不能靠队列收敛」是落地侧结构问题，不是本包内容问题；处方与两笔在途件号已钉在本台账，接手者一眼可续。

### 3.4.2 提取器两缺陷的自纠（红蓝第二轮）
- `r"""` 前缀不被 docstring 正则识别 ⇒ 头注被跳过后折进了**策略样板注释**（「SQL 集中化（§5.160.2）…」）当简介，且两件共用样板 ⇒ 双双命中反模板判据 `is_generic_plain_zh`。已修正则并身份保持重写这 2 条（q-0030/0032）。
- 段标题当名（背景/职责/病根…）：`name_zh` 判定改「只取首句主干 + 25 词段标题黑名单」，`plain_zh` 折行料中剔除裸段标题行；复算受影响 17 条，已随修复批落。

### 3.7 收官判据终态（06:0x 亲验，逐条可复核）
- **两轮零（对齐）**：`align_r3/r4/r5` 三连跑，r4↔r5 **问题行与软计数逐字节等值（diff 0 字节）**；r3→r4 仅 `[2/9] 孤儿模块 521→522`、软 991→992（=他会话落码所致，非本包件）；EXIT=1 恒由已登记外因构成（裁定×3 + 产业链 12 + frontend×2 抖动）。
- **生成器幂等**：抽 21 件／9 生成器 → 14 件滤时变行后重跑等值；`data_inventory` 性质=CH 实时源（仅 4 行计数漂移，结构行集稳）；`full_project_tree` 背靠背双跑等值（首轮 620 行差=跑批窗口内他包落码）；**唯一真缺陷 R-B1**＝`generate_dataflow_diagram.py` 把 PG 代理键 `JOBnnnnnn` 写进 mermaid（panorama 单跑 720 行漂移，册内 1114/1423 行含 JOB 号）。
- **本包自查尺 16 项 = 13 绿 / 3 红**：3 红同一根因＝`entries` 段 5 组 `module_path` 重复键（first-wins 使旧坏值遮蔽新好值）→ 表现为「尾巴域 1 条 / 未派层 1 条 / 唯一键违例 5 组」三症。该根因**不可经队列收敛**（q-0029 纯塌重落地 DONE 而 HEAD 零变化，实测证伪；对照 q-0030/0032 身份保持笔则正常收敛并落地=`9a760906ac`）。出路二选一：`add_module_translation.py --dedupe`（§5.2 注册表净删＝Owner 门位，可顺带清 271 组存量）｜静默窗直连一笔（前例 6ec4fd51b9「绕开三向合并器…HEAD 基底文本级插入」）。
- **翻译覆盖终账（修正口径）**：in-scope 宇宙 3982（HEAD 树）／开工缺 430（旧探针漏 45 件顶层 scripts/*.py，见 D7）→ 现缺 **17**（=16 件头注无料 + 1 件被重复键遮蔽的 `data_loader.py`）；补入 **370 条**（348+21+2 重修等），`short=0`、`generic=4`（其中 2 条系三件同源 provider 模板共用文案，属源文件头注欠账，已列缺源册）。
- **收尾**：claim 全部 release（末 1 件 `module_translation_registry` RELEASED 核实；canonical 已由 st-mapcensus 接管=正常换手）；会话工作树 `session_worktree_abort` 已弃并清理，9 件实质变更存证 `.runtime/quarantine/st-align-dirty-20260924-retire-20260923T205911Z.patch`；`.runtime/tmp/align_dirty` 清至 614KB（保留 6 个驱动脚本＝§3.3 复核命令所指，删去全部可再生大件与他会话 WIP 副本）；reaper keep 行已撤；监控自动化见下行自删记录。
- **【自动化已自删·本包收官】** jobId=`856c4b1d-c8b9-4e76-95d8-1b99ee233ff1`（本行写就后即删，防收口后空转）。续办入口＝§3.4.1 三红 + §3.6 候批清单 D1–D14，**不需要重跑本包任何步骤**。


### 3.5 过程自伤账（全部当场复原，如实）
①误用 `--update --yes` 刷了 22 个 index.md（含他包 04/09/10 册）→ 逐件 `checkout HEAD` 复原，并揪出工具双缺陷（D3）；②首建袋基底陈旧 → 3 笔死信（零损害）→ 重基底后成功；③裸 `commit_queue enqueue` 漏 claim 前移 → 1 笔 CLAIM_REQUIRED 死信 → claim 后 requeue 成功；④台账两次「吃掉相邻标题行」（同册多点插入未走最短读写窗）→ 均复原，教训并入 [[hot-file-wipe-forensics-20260918]]；⑤一次 `git checkout HEAD --` 误用主仓 HEAD 参照系（工作树内 HEAD=session 分支）→ 改为在 worktree 目录内执行；⑥早先「canonical 4 处悬空」把 creation_tokens 计成脏项 → 已按 3.2-③ 更正并撤销该自修。⑦**最重一次：本包成为蒸发加害方**q-0014 袋面声明 1 件、落地带出 4 件（serializer 吸收陈旧 index 残项），抹掉 `capability_canonical` 9 caps+20 tokens（st-ailayer/st-library-final 在飞行）与工厂图审灵修法回退；**闭环动作**=发现（自查 commit 文件清单）→ 定性（git log 精确到「自该笔后仅本包动过」）→ 纯原文回填（工厂图取 `53cdc66e06^` 全量、canonical 取 HEAD+缺失块原字节插回）→ 三笔重投 q-0019/0020/0021 → 落地后逐笔 `git log -1 --name-only` 复核文件清单（本包终报对此不再含糊）。教训=AGENTS §2.5「commit 后必做核实真实归属」是硬步骤，**队列正门不等于免检**：袋面 files ≠ 落地 files 时必须当事故处理。

### 3.6 遗留给总指挥/Owner 的（已候批，非本包可闭）
D1 残（fail_open 14 处 merger 结构无能 = `content_sha256` 标量流被切，处方见 §2-D1/③.5）· D2 门禁宇宙扩面（high）· D3 工具双缺陷 · D4 静默窗 depgraph 重扫（含 `.sh/.ps1` 扫描阶段与 GATE-DEPGRAPH-SCOPE 断言互斥）· D8 翻译册 dedupe（net-1 净删，Owner）· D10 49 条 name_zh 弱锚 + 16 件缺源头注（交各 owner）· 目录册两条 scripts/{patrol,reports} 拟增条目（`human_gated`）· R-B1 dataflow 生成器易变 JOB 代理键（判据级）。

## 心跳 / 自挂监控
- **自动化已挂**：qoder_cron jobId=`856c4b1d-c8b9-4e76-95d8-1b99ee233ff1`，every 30min，model=qfmodel（继承本会话），Full-Access，cwd=D:\ZephyrAlpha，不限期；prompt=总指挥令全文照抄。收官最后一步=终报写完后自删本自动化+记「自动化已自删·本包收官」。
- ## 心跳 2026-09-24 07:1x CST · 主线程收口轮 · 已入 dev=6 笔（GOMAP 423/known_data_gaps/348 条/21 条/门禁指针回指/工厂图复原 293415130d）· 在途队列=0024（canonical 9 caps+9~10 tokens 原文回填）/0025（5 条红队修复行）· 收官判据=13 项自查全绿连跑两次 → 见 §3.7。
- ## 心跳 2026-09-24 05:4x CST（本包主线程收官）· 落地 dev 共 **10 笔**（本 sid）：GOMAP 423 · known_data_gaps 标注 · 补译 348 · 补译 21（口径修正后）· 门禁指针回指 flat（99/99 门装载）· 工厂图复原 · canonical 9caps+20tokens 复原 · TAG-VOCAB 22+17 行复原 · 翻译册 10 条红队修复 · 2 条样板污染简介身份保持重修（q-0030/0032 在途）。
  - 任务序列判定：①✓（六册+GOMAP，含 04/09/10 避让与 22 册越界自纠）②✓ 判定完（真缺口=1 件+2 目录，判据/共享 DB 两路均候批=D4）③✓ 385→17（HEAD 态；含 16 件缺源登记）④✓ 43→2（退役 0/豁免 0/补译 41/缺源 2）⑤✓ 幂等红蓝（14 件幂等 + R-B1 真缺陷）+ 两轮零（r2≡r3 逐行等值，r4 仅软+1 由他包落码）+ 终报 §3。
  - **收官判据达成度（不含糊）**：自查尺 16 项 → 13 绿 3 红，3 红同一根因＝D14（队列合并器对删行/改键类修复不收敛），已 q-0030/0032 身份保持重投；此三红**非本包可自闭**（净删＝§5.2 Owner 门位｜静默窗直连＝总指挥窗口），已带证据与两条出路登记。
  - 收尾动作：release 自有 claim → 会话工作树 abort（成果均已入 dev，袋已 content-addressed 存 `.runtime/commit_queue/blobs`）→ 清 `.runtime/tmp/align_dirty` 大件留证据与驱动脚本 → 自删监控自动化。
  - 【自动化已自删·本包收官】=见本行下方标记；候批项 D1–D14 全部在册，任何续办按 §3.4.1/§3.7 接手即可。

- **§3.7 收官验证待项（监控轮续办，勿新开任务面）**：①待 `q-…-0024`/`q-…-0025` 落地（若 CLAIM_REQUIRED 死→`lock_files.py acquire` 后 `requeue`；若 CAS/合并死→重基底 HEAD 再 enqueue，本包已四轮验证此法有效）；②落地后跑 `python .runtime/tmp/align_dirty/closing_selfcheck.py`（13 检查，含"本包自伤复原核验"三项）**连跑两次全绿**；③`git log -1 --name-only` 核每笔落地文件清单＝袋面清单（防 §3.5-⑦ 复发）；④三项皆毕→release claim（`git_commit.py --release-only`）+ 清 `.runtime/tmp/align_dirty` 大件 + 删本自动化 + 记「自动化已自删·本包收官」。


【总指挥批注 R1·01:50·新增机械项】known_data_gaps.yaml 里有对已删 BdpanTickWatch 看门狗的悬空引用（编制外排查班移交的小尾巴）——顺手续掉（摘悬空行，走正门）。resource_profile 生成器对已删任务自然脱落无需手改（勿动）。

## 心跳 2026-09-24 02:22 · 监控轮在位（HEAD=ef85cda27b）
- 状态: 三前置绿（py3.12.8/lock clean/reaper 02:00 活跳）。批注 R1 已知在办（q-…-0007 在队，BdpanTickWatch 悬空声明摘除）。
- 本轮新增交付: registry_family 悬空指针 4 册修复已入队 q-20260924-st-align-dirty-20260924-0010（supersedes 0005/0006/0008/0009）——in_process_gate_registry module_path 回指 flat（干净树双证：旧路径 ModuleNotFoundError[红] vs 修册后 99/99 门加载[绿]）；capability_canonical 2 悬空 file 重指+1 游离 merge_evaluation 键归位；module_translation rf 条目重指；fail_open 重跑生成器（工作树幂等双跑除 generated_at 零差；602 行差异=HEAD 新落码面+rf 回写，非携带他包 WIP）。
- 在跑判定: .runtime/tmp/align_dirty/ 建筑件 02:21 仍在更新（translation_plan/batches/idempotency），翻译批 builder 与 GOMAP 配置批注②为同包在途施工——监控轮不抢面，仅补不冲突的注册表对账一件。
- 观察登记（供批/复核）: q-…-0002 死因=commit_queue_landing 三向合并器对 module_translation_registry 头部 unique_key:[module_path] 标量列表判‘非 dict 条目’（HEAD 与批 blob 同物皆触发）——属合并器观测面盲区（[[registry-collision-blocks-own-queue-fix]] 同族），修法待总指挥裁定归 landing 侧还是册侧。
- 下一步: 等 serializer 排空 0004/0007/0010 → 落地后 git log 核实归属 → 任务④ 43 双盲逐件判（清单已在 blind43.json）→ ⑤两轮零+抽 20 册幂等红蓝+终报。

## 心跳 2026-09-24 02:38 · 监控轮第 3 次在位（HEAD=140241504a）
- 三前置绿: py 3.12.8 / lock_files cleanup=CLEAN 无死锁 / reaper last_run=02:30:30 dry_run=False（写操作前提满足）。
- 批注区: 无新令（末条仍 R1·01:50）；R1 令已亲验落地面=`140241504a`（known_data_gaps.yaml 续掉 BdpanTickWatch 悬空声明）✓。
- 在跑判定（→本轮不抢面，仅心跳）: `.runtime/tmp/align_dirty/idem_diffs.json` **02:36:04**、`idem_diff.py` **02:35:27**（均晚于上轮 02:22，系执行者新建的幂等漂移分类器，含 VOLATILE 行判据）→ 任务⑤生成器幂等红蓝正在施工；`q-…-0011`（348 条翻译超集，末袋累积）02:35:02 由执行者重投 pending。
- 死因复核（自我更正·本心跳原述已作废）: 上轮只记 0002 死，本轮亲验 0004（02:26:13）/0010（02:31:01）同因再死（三条 dead_reason 文本全等、跨两册）。**本心跳初判『落地侧合并器对 dev 侧既有册形态的观测面盲区』已被执行者 §2-③-b 的实证推翻**：真因=本包袋基底陈旧（建于 `66e6b31346` 翻译册去重手术之前的 HEAD），冲突路径需索引 base 侧被改写前旧形态→判不了身份→死信。处置=重基底到当前 HEAD(68,006 行)+7 批全量重放+纯函数 `three_way_merge_registry_yaml` 双侧验（A：+348 零丢失；B：合成冲突双方同存活 +349）后重投 q-…-0011。死信三次零损害（dead=不落盘，未污染 dev）。
- 通道条件裁定请求（只在 0011 再死时生效）: 事实核=HEAD 版与主区 staged 版（st-commitsys/st-k4 池化 +550/−26）在 `_index_family_blocks` 该判定上逐字相同（HEAD:454=盘:455 同一 return 串）→ 现成 staged 批不含此判定改法；又 serializer worktree 吃 HEAD 代码（e5befbc172 自述病根）。若 q-…-0011 仍以同串死 → 才可判为落地侧盲区，处方二选一候总指挥裁：landing 侧补此判定（归 st-commitsys/st-k4 写域）｜本包改走 worktree 直连（[[registry-collision-blocks-own-queue-fix]] 前例）。0011 未死则本请求作废，不占用裁定额度。
- 未动面（照铁律）: D1–D6 候批项零触碰；②判据/共享 DB（--force 全树重建）未动；③ 15 件缺源未自起文案；④43 逐件判定 §2 已完（退役 0/豁免 0/补翻译 41/缺源 2）；生成物零手改；实盘四禁未涉。
- 热文件蒸发实录（本包台账自身·已复原）: 执行者 02:3x 插入 §2-③-b/⑤ 两节时，`### ⑥ 总指挥 R1 批注` **标题行被吃掉**（正文 97 行成孤儿段）。可检性=该册 staged 版仅 29 行骨架（`git show :path`），盘面内容未提交→ **git 不可回取**，唯本轮 02:36 全量读留有原文。本轮按原文复原该行；教训沿用 [[hot-file-wipe-forensics-20260918]]：同册多点插入须以「读到即写」最短窗口+CAS，且监控轮读台账即隐式留了副本。
- 下一步: 盯 ⑤ 幂等结论成文 + 0011 落地/再死实据 → 若再死且执行者已收工，本台账向总指挥报通道裁定请求（含上述双证）；①②③④ 交付面已核，等终报。

## 心跳 2026-09-24 03:0x · 监控轮第 4 次在位
- 三前置绿: py 3.12.8 / lock_files cleanup=清 5 死锁 + 回收 2 死会话遗物（st-backup-cold、st-library-final，均 merge=skipped/释放claim=0，零损害）/ reaper last_run=03:00:30 dry_run=False（写操作前提满足）。
- 批注区: 无新令（末条仍 R1·01:50）。R1 落地面 `140241504a` 已核 ✓。本轮另核 HEAD 新落 `c5b70a8ff8`=st-audit-all 工厂图重投（他包），与本包无交。
- 在跑判定（→本轮不抢面，仅心跳）: 执行者 03:02:49~03:04:12 仍在写 `.runtime/tmp/align_dirty/`（`align_r2.txt` / 新 `batch_add_translation.py` / `added_paths.txt` / `repair_paths.txt`，均为本轮读台账后的新字节，距 03:04 仅 2 分钟）→ ③ 续批施工中。
- ③ 进度实证: 首件 348 条已落 dev=`8811755fa9`（q-…-0011 done）；HEAD 侧缺翻译 **375→38**（`measure_HEAD.json` 02:46:33 实测）。q-…-0014（22 条「修尺子后续批」）02:49:17 入队，现 state=processing，lease=drain-active（holder pid=31084 commit_belt_daemon，37.9s 前刚续租）→ 未死，等排空。
- 死信面复核: 本包累计 5 死=0002/0004/0010（三向合并判不了身份，根因已在 §2-③-b 定性为袋基底陈旧）+ **0012/0013 新因**（0012=CLAIM_REQUIRED_VIOLATION，0013=fail_open_register.yaml 三向合并）。两册四件（capability_canonical/in_process_gate/module_translation rf/fail_open）= **D1 对账批至今未落地**，仍候处置。
- 现场细节（供执行者重投参考，非本轮动手）: session_registry 里 `st-align-dirty-20260924` 现 pid=31084（=belt daemon 本身，02:52:55 注册）held_files 仅剩 serializer worktree w1 的 module_translation 一件，本包工作树已无活跃 claim → 0012 这类 CLAIM_REQUIRED 需重新 claim 后即基即投；本包亦无 `heartbeat_daemon` 进程在跑（gpu-final/audit-all 有）。
- 口径警示（分母会变）: 0014 自述根因=旧探针 `git ls-files 'scripts/**/*.py'` 的 git pathspec `**` 不跨 `/`，漏量顶层 scripts/*.py → 修尺后宇宙口径 375↔369 之争，`added_paths.txt`=369 件。**故本轮所报 38 是「旧尺余量」非终态**；⑤ 两轮零必须用修好的尺复量，勿以 38 收口。
- 并发压力登记: 此刻两包正对同一热翻译册/热注册表提交（pid 21264 st-gpu-final 03:03:03、pid 44964 st-backup-cold 03:03:47 均含 `module_translation_registry.yaml`/`capability_canonical_file_registry.yaml`），0014 同袋在途 → dev 再推进，「即基即投」窗口更窄（承 §2-③-b 教训）。
- 未动面（照铁律）: 生成物零手改；D1–D6 候批项零触碰；② 判据/共享 DB（--force 全树重建）未动；③ 15 件缺源未自起文案；实盘四禁未涉；台账仅追加本心跳（写前亲验 7 处结构锚点全在，无蒸发）。
- 下一步: 盯 0014 落地并核 `git log -1 --name-only` 归属 → 推 D1 对账批（0012/0013）以「即基即投」重投 → ⑤ 用修好的尺做两轮零+终报。
- 心跳补录（同轮 03:10 复扫，纠正本轮上条『下一步』只记了 0014）: 在队实为 **两件** ——0014（22 条修尺续批，02:49:17）+ **0015（自查修复批·10 条，03:09:11 新入）**，均 state=processing、同键同册（module_translation_registry.yaml），队列总态 pending 9 / processing 4 / done 840。
- 红队抽查实录（承 [[feedback-executor-cannot-sign-own-work]] 口径，本包交付正被非自证复核）: 0015 自述=另一执行体对已落 348 条做 45/347 抽样，揪出两真缺陷 → ①域取值把 `# [DOMAIN] …` 整行尾巴当域；②文件名被当成段落标题。二者均属「取文规则判据」而非内容编造（未违反禁自起铁律），修法=就地纯更新零净删、同通道同判据重投。**监控轮判定: 这是有效自纠，非返工膨胀，不需总指挥裁定**；但提示 ⑤ 两轮零的复量口径须含『域字段合法性』一项（旧尺只量缺没量错）。

## 心跳 2026-09-24 03:35 · 监控轮第 5 次在位（HEAD=47e9673e94）
- 三前置绿: py 3.12.8 / `lock_files.py cleanup` 回收 4 个死会话遗物（含本包 `st-align-dirty-20260924` 自身 registry 与 st-audit-all / st-chainpile-20260922 / worker-0aec376a，全 merge=skipped·stash=0件·释放claim=0 → 零损害）/ reaper `last_run=03:30:31 dry_run=False scanned=17 killed=0`（写操作前提满足）。
- 批注区: **无新令**（全册仅 1 条【总指挥批注 R1·01:50】，其落地面 `140241504a` 前轮已亲验 ✓）。
- 落地归属核实（`git log --name-only` 侧）: **0014 → `53cdc66e06`**（翻译册补 plain_zh 续批 22 条·修尺后新可见面）✓；**0016 → `0aec376aba`**（D1 注册表↔实物悬空治本：`in_process_gate_registry` module_path 回指 flat + `capability_canonical_file_registry`）✓。上轮所忧「0014 落地待核」已闭环。
- 在跑判定（→本轮不抢面，仅心跳）: **`q-…-0018` 03:34:11 入队、state=processing**（1 件 = `module_translation_registry.yaml`，blob sha 已钉；内容=§③-R 红队自查揪出的两取文缺陷的 10 条纯更新修复批，即 0015 的重投）；队列 lease=drain-active（holder pid=42268，15.1s 前刚续租）；`.runtime/tmp/align_dirty/translation_plan.json` 03:31:59 有新字节 → 执行者在场施工中。
- 死信面更新（本包累计 7 死）: 新增 **0015**（`HOT-FILE-BASE-FRESHNESS / STALE_BASE_VIOLATION`=热文件在 claim 之后被上游 commit 改动，即基即投窗口被并发挤掉，非合并器盲区，与 §2-③-b 定性不同因）+ **0017**（`fail_open_register.yaml` 三向合并同串再死）。→ **D1 四腿中三腿已落**（门禁册/canonical 册经 0016；翻译册 rf 条目经 0011/0014），**唯 fail_open 一腿未落**，0013/0017 两度同因，属已定性候批项，本包不擅改 landing 侧判据。
- 队列总态: pending 6 / processing 1 / done 832 / dead 173（全仓口径，非本包）。
- 并发压力登记: pid 44504 `st-backup-cold-20260924` 正在 `git_commit.py --files infrastructure_registry.yaml`（其 message 自述引用本包 `53cdc66e06` 的 stale-index 回退再重落）；pid 8296 `reconcile_worker` 对 HEAD `47e9673e94` 在跑；HEAD 已被他包（备份链红蓝修复批）推进 → 下轮 0018 落地核归属时须以「commit 后 `git log -1 --name-only`」为准，勿以入队时 base 推断。
- 未动面（照铁律）: 生成物零手改；D1–D10 候批项零触碰（含 fail_open 一腿）；② 判据/共享 DB（`--force` 全树重建）未动；③ 缺源件未自起文案；实盘四禁未涉；**台账仅以 `safe_write_text` CAS 追加本心跳、未提交**（执行者在该册有在途 WIP，此时提交即连坐，承 [[hot-file-wipe-forensics-20260918]] / [[align-dirty-shift-20260924]]）。
- 下一步: 盯 0018 落地并核归属 → 0015/0017 若需重投由执行者以「即基即投」重 claim 后再投（本包 worktree 当前无活跃 claim）→ ⑤ 用修好的尺（`ls-files -- <dir>` + 端过滤口径，非 `scripts/**/*.py`）复量「两轮零」+ 抽册幂等红蓝（复量口径含『域字段合法性』一项）→ 终报 → 自删本自动化。
- 心跳补录（同轮 03:36 复扫·修正上条『下一步』两项已完成表述）: 磁盘台账已出现执行者新写的 **`## 3. 终报`（§3.1–§3.6）** —— ①§3.4 已把「两轮零」口径写死并给实证（同一工具同一 HEAD 连续两轮 r2↔r3 九节 `问题:` 行+软计数 991 **逐字节等值** ✓，本包作用域新增硬=0）；②§3.3 复查清单含生成器幂等复量命令（`idempotency_test.py` 滤时变行 + `idem_diff.py` 判 VOLATILE/JOB 行）。**故上条『下一步』中的「⑤ 两轮零+幂等红蓝」与「终报」两项已达成**，本心跳予以更正、下轮勿重复施工。
- 收官条件复评: **未达**——0018 于 03:36:36 复扫仍 `state=processing`（landed_id=None，lease=drain-active pid=42268），且 §3.6 首条 D1 残腿（`fail_open_register` 14 处，merger 对 `content_sha256` 标量流无能）未落。本自动化**保留**，收官行待 0018 落地核实 + 执行者/总指挥对 D1 残腿定口径后再写。

## 心跳 2026-09-24 04:08 · 监控轮第 6 次在位（HEAD=488d823ab7）
- 三前置绿: py 3.12.8 / `lock_files.py cleanup`=清 2 死锁（canonical 册、翻译册，本包在途件所致）+ 回收死会话 `st-backup-cold-20260924` 遗物（merge=skipped·stash=0 件·释放 claim=0 → 零损害）/ reaper `last_run=04:00:30 dry_run=False killed=0`（写操作前提满足）。
- 批注区: **无新令**（全册仍仅【总指挥批注 R1·01:50】一条；其落地面 `140241504a` 已两轮亲验 ✓）。
- 上轮收官阻塞项①已闭环: **0018 落地 = `2a68c14fda`（03:41）**，`git log -1 --name-only` 实测**袋面 1 件 = 落地 1 件**（仅 `module_translation_registry.yaml`），**无陈旧 index 连坐** → D12 型蒸发未复发 ✓。
- 本包队列现态（9 done / 10 dead / 1 pending）: 0019、0023 以 `landed_id=noop@…` 收口（目标字节已在 HEAD，零写入=正当幂等）；0020（`config/strategy_production_map.yaml` 原文回填）真落 = `293415130d`（03:52）；**唯 canonical 册一腿仍在转圈**——0021 死于「dev CAS 竞态：同路径被**队列外写入者**推进 `293415130d63..b906e95496e9`」、0022 死于 `CLAIM_REQUIRED_VIOLATION`（serializer worktree 路径未 claim）、**0024 于 04:01:26 三投在队 pending**。
- 探针实据（本轮新增，只读）: 0024 目标 blob `24a35bf5…` 与 HEAD `f707b078…` **仍不等**，逐行差分 = **159 行纯增 / 0 删**（首块 `capability_id: ai_cleaning_l3`）→ 该腿有真实待落内容、**非 noop**，须盯到落地。
- D13 由预测转实证（候批升权）: canonical 册此刻并存两个写入者——本包复原批（0021/0022/0024）与 `eight-pack-commander-ledger` 两笔 token 补登（`b906e95496`、`d453655f3d`，均 03:5x 落 dev）→ 同路径 CAS 竞态即 §2-D13「热件缺单一属主」现场复现；处方仍=「落地面唯一写者 + 其余走 merge」窗口规约（判据级，本包不擅定）。
- 在跑判定（→本轮不抢面，仅心跳）: `.runtime/tmp/align_dirty/translation_plan.json` **03:58:24**、`measure_disk.json` **03:57:23**、0024 **04:01:26** 新入队、队列 lease=`drain-active`（holder pid=29828）→ 执行者在场，任务序列 ①②③④ 均其手上件，监控轮不接管。
- 收官条件复评: **仍未达**——(a) 0024 未落地核实；(b) D1 残腿 `fail_open_register` 14 处（merger 对 `content_sha256` 标量流无能，§3.6 首条）仍候总指挥口径；⑤ 两轮零+幂等红蓝+终报 §3.1–3.6 **已达成**（03:36 轮已记，勿重复施工）。本自动化**保留**。
- 未动面（照铁律）: 生成物零手改；D1–D13 候批项零触碰；判据/共享 DB（`--force` 全树重建）未动；缺源件未自起文案；实盘四禁未涉；台账以 `safe_write_text` CAS 追加本心跳、**仍未提交**（该文件为 `AM` 新增态且执行者在册上有在途 WIP，此时提交即 D12 型连坐）。
- 下一步: 盯 0024 落地并以 `git log -1 --name-only` 核归属（159 行纯增须逐块对 HEAD）→ fail_open 残腿候批不动 → (a)(b) 齐后写收官行+自删本自动化。

【总指挥批注 R2·03:45·新任务：_working 全清第二轮+完工结案制度（Owner 定调，W8 第二圈先例）】
范围=docs/_working/ 全部目录+散件（含 Owner 点名的 docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/ 目录如 16_technical_indicator_catalog.md）。逐目录四态判定（W8 先例法，每目录三查：HEAD 最后提交时间+十包在飞占用+内容施工态）：
①**施工完毕**→写事实性结案报告（从 HEAD 提交链提取：做了什么/落地哈希/验收证据，禁虚构）→归档 archive/2026-09/（git mv 走正门）；
②**施工内容应进蓝图而未进**→机械判据：该内容是否已存在于 docs/03_modules/**/blueprint.md 或注册表 yaml（grep 验证）——已在=已升级照①处理；不在=列《待升级条目清单》（条目+出处+建议去向蓝图路径）交总指挥裁定，禁自行改蓝图；
③**未施工**→列《未施工清单》（每条带真源指针+一句话内容）交总指挥分派；
④**在飞围栏**（十包台账声明的写域目录）→标记"在飞不动"。
交付件=docs/_working/align_dirty/working_cleanup_r2.md（四态总账+三清单+归档执行记录）。此任务与你的翻译/派生册任务并行，子代理分片跑（每代理≤15 目录）。完成后台账通知——未施工清单由总指挥对照十包在飞面分派（已有人做的标注属主，没人做的派苦力）。

### 裁定请求 R2-a·04:51（监控轮上报，收官闸红，须裁后方可闭包）
事实核（`python .runtime/tmp/align_dirty/closing_selfcheck.py` 16 检查 = **13 pass / 3 FAIL**，EXIT=1，HEAD=`9a760906ac`）：
1. **红①「无整行尾巴域值」count=1** + **红③「entries 段 unique_key 违例组数=0」dup_groups=5**：`git blame` 逐行实证——4 组重复的**第二行全部来自本包 q-0018 落地笔 `2a68c14fda`（03:41「自查修复批·10 条」）**：
   - `src/zephyr/ex_core/open_order_resolver.py` 58168(`8811755fa9`)↔59862(`2a68c14fda`)
   - `src/zephyr/research/evidence/batch_entry.py` 59192(`8811755fa9`)↔59870(`2a68c14fda`)
   - `src/zephyr/risk/core/ai_agent_monitor.py` 59223(`8811755fa9`)↔59878(`2a68c14fda`)
   - `src/zephyr/signal_ashare/sector/sector_pullback.py` 59486(`8811755fa9`)↔59886(`2a68c14fda`)
   - 第 5 组 `src/zephyr/strategy_factory/owner_band_t/data_loader.py` 55039(`b4c3c6f26d` 2026-09-17 空 stub)↔56912(`8811755fa9`)=已登记的 **D11** 存量件。
   定性与账：**本包第 8 次自伤**——q-0018 自述「就地纯更新零净删」，实为**追加 4 行**（触发条件比 D11 更宽：原行 `domain_id` 带 `#` 尾巴注释使 upsert 命中失败，于是新行另起）；红① 之所以仍红，正因缺陷原行留在册、修好的新行另挂一处。
2. **红②「域在映射册者必已派生层」count=1**：`scripts/audit_technical_indicator_columns.py`@55839 域 `D_GOV_SCRIPTS` 有层映射而 `responsibility_layer` 空 → blame=`a065f76ef1`（2026-09-21「WO-3 哨兵补盲」）**非本包件**，按 §3.4「他会话违规不代修」交其 owner（一句话可修：跑 `add_module_translation.py` 派生层）。
候裁处方（二选一，本包不擅动=注册表净删属 §5.2 high 门位）：
- **a 案**：批准本包跑 `add_module_translation.py --dedupe`（信息最全条目保留+扩展字段合并+CAS，幂等）→ 一并消化 D8 的 271 组存量与本包新造的 4 组，净删 5+行；红测=跑两次行数不降（幂等）+ unique_key 违例=0。
- **b 案**：只治本包自伤面——先就地修 59192 类「尾巴域值」原行（纯更新），再删 `2a68c14fda` 追加的 4 行（净删 4 行，Owner 门位内最小面）。
- 两案之外另候：红② 的 owner 派发（本包可代跑派生层，但需总指挥点头代修他包在册件）。
连带事实（供裁）：本包队列 **0001–0031 全清**（done 21 / dead 10 / pending 0），0024 落 `e88eb3f786`、0030 落 `9a760906ac`，`git log -1 --name-only` 实测**袋面件数=落地件数**（D12 型连坐未复发）；canonical 册 159 行原文回填已亲验 HEAD 含 `ai_cleaning_l3`。

## 心跳 2026-09-24 04:51 · 监控轮第 7 次在位（HEAD=9a760906ac）
- 三前置绿: py 3.12.8 / `lock_files.py cleanup`=CLEAN 无死锁 / reaper `last_run=04:30:30 dry_run=False scanned=22 killed=0`（写操作前提满足，计划任务 `ZephyrAlpha_ProcessReaper`=Ready）。
- 批注区: **新令 1 条=【总指挥批注 R2·03:45】**（_working 全清第二轮+完工结案制度）→ 本轮已开工，与 ①–⑤ 面并行不抢（见下）。R1 落地面 `140241504a` 历轮已验。
- 在跑判定: `.runtime/tmp/align_dirty/` 04:29–04:32 有新字节（`heal_dups.py`/`closing_selfcheck.py`/`evidence_*.yaml`/`batch_add_translation.py`）+ 0030 于 04:39 落地 → 执行者刚收工/在收尾，**任务序列 ①–⑤ 不接管**；§3 终报（04:3x）与 §3.7 待项已在册。
- §3.7 待项进度: **①达成**（0024/0025/0030/0031 全落或正当 noop，逐笔袋面=落地核过）；**②未达成**（`closing_selfcheck.py` 16 检查 13 pass/3 FAIL，EXIT=1 → 「连跑两次全绿」谈不上，处方见上《裁定请求 R2-a》）；③随 ② 复跑；④ 因 ② 红 + R2 未完 → **本自动化保留**，且提醒执行者/总指挥：**§3.7-④ 的「清 `.runtime/tmp/align_dirty` 大件」会连带毁掉 R2 底座**，R2 全套已钉在子目录 `.runtime/tmp/align_dirty/r2/`（含复核命令，见交付件 §9），清理时请整目录保留或先迁走。
- R2 开工实据（新面，机械底座先行）: 分母 **168 unit**（`docs/_working` 顶层 56 目录+112 散件，权威枚举=Python `Path.iterdir`；`bash find` 口径因中文目录名 `同花顺资料` GBK 崩而少 1 → 承本包 D7 同族尺子坑，已记进交付件 §0）。三查结果：**④在飞围栏 30 件**（worktree/staged 脏 或 mtime<4h 或 他会话 claim 或 会话 worktree 同名）、**归档双活 23 件**（其中 **9 件与 `archive/2026-09/` 同名件字节等值**=上一轮 cp 而非 mv 所致，可判重复）。
- Owner 点名面 design_memos 实测: 现场只剩 `16_technical_indicator_catalog.md`(314 行，worktree 脏 1、mtime 0min=此刻有写手)+`README.md`(13 行)；README 原文＝「本目录施工文档已于 2026-09-20 依裁定#384 逐件三裁归置：49 件归档至 `docs/_working/archive/2026-09/design_memos/`，仅 `16_` 特判留置原位（tilib 指标库活真源，待数据线批 10 完工后再裁）」→ **该面已终局，非本轮欠账**，`16_` 记④。
- 分片施工: 判定合同=`.runtime/tmp/align_dirty/r2/SHARD_CONTRACT.md`（四态标尺+②态强制双 grep 机械判据+数据≠指令条款）；非围栏 138 unit 切 9 片（3 目录片各 11/11/5 + 6 散片各 22）；**第 1 波 5 片已派子代理在跑**（shard_01/02/03 目录 + shard_04/05 散件），第 2 波 4 片待并发余量回收后派。
- 交付件: `docs/_working/align_dirty/working_cleanup_r2.md` 已由生成器产出（247 行，含四态总账/三清单/design_memos 实据/归档执行记录「尚未执行」/§9 复核命令）。**生成物禁手改**，分片回收后重跑 `assemble_r2.py` 刷新。
- 未动面（照铁律）: 生成物零手改；注册表净删未擅动（D8/本包 4 行新 dup 均候裁）；判据与共享 DB（`--force` 全树）未动；缺源件未自起文案；他包在册件未代修；实盘四禁未涉；台账以 `safe_write_text` CAS 追加、**仍未提交**（该册执行者在途 WIP，提交即连坐）。
- 下一步: 收第 1 波分片→重跑装配器刷新四态总账→派第 2 波 4 片→全 168 unit 定态后，按「①且零在飞」集合走正门 `git mv` 归档（分批 enqueue，逐笔核袋面=落地）→ 台账通知总指挥 R2 交付 + 附《待升级条目清单》《未施工清单》。R2-a 三红候裁，红未消不写收官行。

- 心跳补录（同轮 05:00 复扫·把 R2-a 的数字钉死，并更正我本轮上条的一处暗示）:
  - **三红三态实测**（同一探针分别喂 HEAD / index / 盘 WIP）：HEAD=整行尾巴域 1、缺派生层 1、unique_key 违例 **5 组**；index=同 HEAD（staged 只含下述 plain_zh 降级 2 行）；**盘 WIP=0、0、4 组** → 结论：执行者**尚未落地**的在途批已消掉红①红②（含代修他包件 `scripts/audit_technical_indicator_columns.py` 的派生层），**只剩 4 组重复**（3 组本包 q-0018 追加 + 1 组 D11 存量 stub）。
  - **a 案数字钉死**：`add_module_translation.py --dedupe --dry-run`（盘态）实测 `entries 7666→7662`、拟删 4 条、样例 `open_order_resolver/ai_agent_monitor/sector_pullback/owner_band_t.data_loader`。红测口径=跑两次行数不再降。
  - **更正一处暗示**：我上条写「dedupe 通道对 batch_entry 组失明」——实为**盘态该行已被在途批删掉**，通道并无失明；若总指挥以 HEAD 态跑该 dry-run 会看到 5 组。两口径勿混。
  - **新发紧急观察（热册在途降级，非本包判据问题）**：主区 `module_translation_registry.yaml` 现 **MM** 态（staged 2/2 + 未 staged 4/10），其中 staged 部分把两条 **HEAD 既有** 条目的 `plain_zh` 换成了源文件第 64/65 行的段注释「SQL 集中化（§5.160.2）：模块级 SQL_* 常量，参数化查询禁 f-string 插值。」：`src/zephyr/signal_ashare/futures_basis_monitor.py`（MOD-SIG-058 期指基差情绪监测器）、`src/zephyr/signal_ashare/limit_up/lhb_premium_analyzer.py`（MOD-SIG-057 龙虎榜盘后溢价分析器）→ 这是红队 R2「取文错位/名当段标题」病灶在**存量条目上的复发**，且**已进共享 index**：按 D12 既往四次实演，任何会话吸收 index 即把该降级带进 HEAD（模态=静默、可回取但无人知）。处方（二选一，本监控轮**不动手**，因该册执行者在途）：①执行者落地前把这两条按 `git show HEAD:<册>` 原文回填（纯恢复、零净改、不涉净删门位）；②总指挥立 canonical/翻译册「落地面单一写者」窗口（即 §2-D13 处方）。
  - 复核命令：`git diff --cached -- <册> | grep -n "SQL 集中化"` 与 `sed -n '64,65p' src/zephyr/signal_ashare/futures_basis_monitor.py`。
- R2 分片进度：第 1 波 5 片中 **shard_01 已回**（11 件：①5/②1/③4/ask1）、**shard_09 已回**（1 件①，合同 §3 条 2 命中 ruling_registry:2623/2678+gate_registry:627+翻译册:57303 故改判①，另报「external 锚」在 19 个 blueprint.md 零命中候裁）；**shard_02 首位执行者异常收工且零落盘**（通知 completed 但无文件，trust-but-verify 抓到）→ 已带「必须真落盘+自证可解析」条款重派；03/04/05/06/07/08 在跑。装配器新增 §1.2「机械标记↔分片终判失证登记」（自动算，当前 9 条疑点，含 redblue 含结案词 4 次却判③、forensics 含待裁词 4 次却判① 等），并把 twin 路径统一成正斜杠；生成器幂等复测=滤 generated_at 后 0 行差。

## 心跳 2026-09-24 06:1x CST · 主线程收官（自动化已自删·本包收官）
- 收官三判据：**两轮零=达成**（r4↔r5 问题行与软计数逐字节等值，diff 0 字节）｜**生成器幂等红蓝=达成**（21 件抽样／9 生成器：14 幂等 + 1 性质时变 + 1 双跑消歧 + R-B1 真缺陷定档候批）｜**终报=已交付**（§3.1–§3.7：交付 11 笔 dev commit、自主裁定 6 条、复查清单 6 条带命令、遗留 D1–D14）。
- 落地 dev 本 sid 共 **11 笔**：ef85cda27b GOMAP · 140241504a gaps 标注 · 8811755fa9 补译348 · 53cdc66e06 补译21(含连坐事故) · 0aec376aba 门禁指针 · 293415130d 工厂图复原 · e88eb3f786 canonical 复原 · 909e49e41f TAG-VOCAB 复原 · 2a68c14fda 红队修复10 · ac27ed1b8b/9a760906ac 身份保持重修。
- 唯一未自闭残面（不含糊直陈）：`module_translation_registry` entries 段 **5 组重复 module_path**（本包修复批所造，已实测证伪「队列可收敛」：q-0029 落地 DONE 而 HEAD 零变化）→ 需 `--dedupe`（Owner 门位）或静默窗直连一笔，命令与两块行号在 §3.4.1/D8/D14；除此之外本包任务序列 ①②③④⑤+R1 批注⑥ 全部执行完毕。
- 收尾核账：claim 全 release · 工作树 abort（9 件实质变更存证 .runtime/quarantine/st-align-dirty-20260924-retire-*.patch）· 临时件降至 614KB（仅留 6 个复核驱动脚本 + 小证据 JSON）· reaper keep 行已撤 · cron jobId=856c4b1d 已 remove（list 核实仅剩他包 1 项）。

## 心跳 2026-09-24 05:11 · 监控轮第 8 次在位（HEAD=4843e85072）
- 三前置绿: py 3.12.8 / `lock_files.py cleanup`=SALVAGED 死会话 `st-gpu-final-20260924` 遗物（merge=skipped·stash=0 件·释放 claim=0+1 把 .ailocks → 零损害）/ reaper `last_run=05:07:24 dry_run=False scanned=22 killed=0`（写操作前提满足）。
- 批注区: **无新令**（全册 `^【总指挥批注`=2 条：R1·01:50 已验、R2·03:45 在办）。
- **R2 结构性发现（比四态判定更要紧）**：归档双活件数被我第一版**假阴了 5 倍**——底座只查 `archive/<月>/<同名>` 顶层，而上一轮把散件归进了 **`archive/2026-09/c_class_scattered/` 等嵌套子目录**。两代理（shard_04、shard_07）独立报告同一处，改正后实量：**twin 118 件 / 其中字节等值 108 件 / 不等值 10 件**。含义：`docs/_working` 169 个 unit 里 **108 个是「归档侧已存在且逐字节相同」的活体重复**（上一轮 cp 而非 `git mv`），故第二轮的真活**主要不是「再归档」而是「去双活」**；泛用名（index.md/README.md）零命中，非撞名假阳。
- 自纠①（判「代理零落盘」过早）: 我以 04:56 时刻 `shards_out/` 无 shard_02.yaml 为据判其执行体未交付并重派；实际该代理耗时 1040s，**05:00 正常交付**。→ 一次重复劳动（已在其重派件到达前 `TaskStop` 止损，自家底座未受害）。教训=**异步代理回执缺失≠未干活**，重派前须按其用时量级留窗或先查盘二次确认。
- 自纠②（我上条补录把降级范围说窄了）: 「SQL 集中化」段注释污染**不止 index/盘**——`git show HEAD:<册> | grep -c` 实测 **HEAD 已含 2 条 `name_zh: "SQL 集中化"`**（`futures_basis_monitor.py`、`lhb_premium_analyzer.py`，即红队 R2「名当段标题」病灶已在 HEAD），而 `plain_zh` 的**同一条降级**尚在 index/盘（`git diff --cached` 2 处）。连带结论：`closing_selfcheck.py` 16 检查里**没有「name_zh 是否段标题」一项**=收官尺盲区，建议随 a/b 案一并补进该脚本（本包不擅改执行者的收官尺）。
- 底座被连带删除实录（本包 R2 面的第一次事故）: 05:00 执行者走 §3.7-④「清 `.runtime/tmp/align_dirty` 大件」时，把我放在 `.runtime/tmp/align_dirty/r2/` 的底座（合同+shard_inputs+facts+shard_01/09 两份判定结果）**一并删除**；我在 04:59:57 已在本台账写入「请整目录保留或先迁走」的警示，**晚了 3 秒**。shard_05 代理独立见证「判定中途合同与 shard_inputs 被并发改动删除」。处置=已迁至 **`.runtime/tmp/working_cleanup_r2/`**（脱离本包 align_dirty 子树，不再受该清理步骤波及）重建，分片结果每收一份即 `cp` 到安全侧。**再次印证 §2-D13：临时面也需要属主围栏，清理动作应有声明的删除边界。**
- 装配器自证（承「自写盘点脚本也要红证」）: ①新增不变量断言 `sum(四态计数)==unit 数`——此前一次实跑出现过 **199≠169 的不平账**（**根因未定**：事发时 facts JSON 刚被 `r2_base.py` 重写、分片仍在并发落盘，疑为读数跨了两代；现以断言把该型不平钉死，不平即崩不静发）；②本轮账平：`facts=169 verdicts=104 states= ①81 ②11 ③11 ④31 未判35`；③§1.2「机械标记↔分片终判失证登记」自动算出 216 条疑点（多为散件的 `closure` 关键词粗筛失真，终判以读原文为准）。
- 收官闸（§3.7-②）复评: **仍红**——HEAD 态三红 = 整行尾巴域 1 / 缺派生层 1 / unique_key 违例 5；盘 WIP 态 = 0 / 0 / 4（执行者在途批已消两红，剩 4 组重复须 a/b 案裁）。`q-…` 本包队列仍 0 在途，**不具备「连跑两次全绿」条件** → 本自动化继续保留。
- 未动面（照铁律）: 生成物零手改（交付件全程由装配器产出）；注册表净删未擅动（`--dedupe` 仅跑 `--dry-run`）；他包在册件未代修；蓝图/规则册零触碰；判据与共享 DB 未动；实盘四禁未涉；台账 CAS 追加且**未提交**（该册执行者在途）。
- 下一步: 收 shard_06 与补判片 a（覆盖剩 35 件）→ 全 169 定态后按「①∩零在飞」分两类执行（108 双活等值→删 live 重复份走正门；无归档件→`git mv` 入 `archive/2026-09/`），每批 `git log -1 --name-only` 核袋面=落地面 → 台账通知总指挥：R2 交付件 + 《待升级条目清单》（现 11 件②）+《未施工清单》（现 11 件③）+ R2-a 三红候裁。

## 心跳 2026-09-24 05:32 · 监控轮第 9 次在位 · **R2 判定面交付完成（自主可执行部分已尽）**
- 三前置绿: py 3.12.8 / `lock_files.py cleanup` 与 reaper 于本轮 04:3x–05:07 两次实测绿（`last_run=05:07:24 dry_run=False killed=0`，计划任务 Ready）。
- **R2 覆盖达成**：169 unit = **①105 / ②14 / ③18 / ④32**，非围栏 138 件**全部有终判**（未判=0）。交付件 `docs/_working/align_dirty/working_cleanup_r2.md`（2404 行，生成器产出、含 §9 复核命令）。分片回收 9 片全数落地（shard_02 一份因底座被删而重跑，见 §1.2/自纠①）。
- **①105 件的处置分解（这是 R2 真正的岔口）**：
  - **87 件=与归档侧逐字节等值的双活件**（上一轮 `cp` 而非 `git mv` 遗留）→ 唯一自洽处置是**删 live 重复份**（净删），R2 原文只授权 `git mv`，且 §5.2 净删属高门位 → **列《裁定请求 R2-b》候裁，未擅删**。
  - **11 件=归档侧无同名件、需真 `git mv`** → **实测被阻断**：11 件**全部**存在 `_working` 之外入站引用，引用者含热册 `capability_canonical_file_registry.yaml`（11/11 全中）、`ruling_registry.yaml`、`architecture_issue_registry.yaml`、`data_asset_registry.yaml`、`config/…/known_data_gaps.yaml`、`.gitignore`、`scripts/audit_technical_indicator_columns.py`、`tests/governance/audit/test_arch_diagram_wave_concurrency.py`；逐件清单见交付件 §7 表。mv 必同批改这些锚点，而热册此刻由执行者在途持有（本包 D13 现场三度复现）→ 按「热件占用即跳过登记」铁律不动手。**这就是上一轮为什么用 cp 的机械解释**（不是偷懒，是锚点联动成本）。
  - 7 件=归档侧有同名件但字节不等（归档件是更新一轮的再生产物）→ 属「以哪份为真」的裁定项，随 R2-b 一并候裁。
- **安全告警（须 Owner/总指挥，非本包可修）**：`docs/_working/2026-09-12-alt-data-handoff.md` §2 表（第 51-56 行）明文列 Alpha Vantage / EODHD / 百度指数 Access-Token / 北京市开放平台 key / Tushare 等真实凭证；**同内容在 `archive/2026-09/c_class_scattered/` 有第二份**，两份均已入 git 历史；而该文件自己第 59/117 行写着「值只进 `.env`」。本心跳**只记位置与指纹，未复述任何值**。附带结论：SECRETS 三道 gate 显未覆盖 `docs/_working/**.md` 的表格式明文凭证（否则早被拦）→ 建议与 D2/D3 同窗裁。普查尺子**未定标**（宽口径 1243 处/45 文件，抽样定性显示绝大多数是 `creation_token` 治理 slug 与红蓝测试假值），故不采用该计数作违规数，只作人核线索（明细 `.runtime/tmp/working_cleanup_r2/secrets_scan_r2.json`，正/反例控制已内置断言）。
- 自纠③（本轮新增，尺子类）: 我的双活判据第一版**假阴 5 倍**（只查 `archive/<月>/` 顶层，漏 `c_class_scattered/`、`factory/` 等嵌套），由 shard_04/07 两代理独立指出后改递归 basename 比对：twin 23→118、等值 9→**108**。教训=**粗筛尺子的覆盖面本身就是判据**，子代理读原文能反哺机械层，红蓝分片不是冗余。
- 装配器自证: 新铸不变量断言 `sum(四态计数)==unit 数`（此前一次实跑出现过 199≠169 的不平账，**根因未定**，疑读数跨了 facts 换代；现不平即崩不静发）。本轮账平：169=105+14+18+32，**未判=0**。
- 自纠④（该断言当场抓到我自己的 bug）: 归一函数 `norm()` 原写 `if s in (1,2,3,"ask")`，把**分片判④而机械无围栏**的件（`2026-08-31-frontend-gap-views-derived.md`，shard_04 判「派生缓存件，围栏误收」）掉成「未判」——正是「不平即崩」断言把它逼出来（1 件差额），已修为含 4 后账平。
- 收官闸（§3.7-②）复评: **仍红且不可自消**——HEAD 三红 = 整行尾巴域 1 / 缺派生层 1 / unique 违例 5；须 R2-a（a/b 案）裁定 + 执行者在途复原批落地，本监控轮不擅改注册表与收官尺。本自动化**继续保留**。
- 未动面（照铁律）: 生成物零手改；`--dedupe` 仅跑 `--dry-run`；净删与 mv 均未执行；蓝图/规则册/热册零触碰；他包在册件未代修；判据与共享 DB 未动；实盘四禁未涉；台账 CAS 追加且未提交。
- 下一步（自主面已穷尽，候三件输入）: ①R2-a 三红处方裁（a=`--dedupe` 净删 4 行 / b=就地修后删自增行）；②R2-b 双活 87 件净删 + 11 件 mv 锚点联动的窗口与属主规约；③《未施工清单》18 件与《待升级条目清单》14 件的分派（R2 末段所命：由总指挥对照十包在飞面派）。收到裁定后我即按正门分批执行并逐笔核袋面=落地面。

- 心跳补录（同轮 05:33）: 交付件 `docs/_working/align_dirty/working_cleanup_r2.md` 曾被**外来动作放进共享 index**（`git status` 显 `AM`，非我 add）。若它会话吸收 index 即被他包 commit 带走，既可能因缺 creation_token 让**别人**的提交被 CREATE-GUARD 打死，也可能触发 D12 型连坐 → 已 `git restore --staged -- <交付件>` 精准撤出（首次尝试遇 `.git/index.lock` 被他会话持有，**未删锁**、按有界重试成功），现该件=`??` 盘上完好 2406 行，另留快照 `.runtime/tmp/working_cleanup_r2/working_cleanup_r2.snapshot.md`。正门提交（含 creation_token 登记）**延到热册空窗**再做，届时逐笔核袋面=落地面。

### 3.8 唯一残留（协议内上交，附一键命令与四次不收敛实证）

**残面**：`module_translation_registry.yaml` entries 段 6 组同 `module_path` 重复行（HEAD rows 7687 / distinct 7681）。

**危害已降到零**：正确值已按**非键字段**广播进每一条重复行（q-0036/0037 落地；`domain_id` 尾巴污染 1→0、模板样板简介 2→0），故 loader first-wins 取哪条都对——残留只是该册自宣 `unique_key: [module_path]` 的结构违例（纯卫生），不再造成错值或遮蔽。

**为什么本包不自闭（三条独立依据，非畏难）**：
1. 塌回＝净删 6 行 ⇒ AGENTS §5.2 把「注册表净删」明列为 high 域门位 → Owner；
2. 同题前例 `66e6b31346`（翻译册真重复去重直落）写的就是「Owner 全批 2026-09-23 晨 + 静窗实开」；
3. 队列对删除类批次**实测四次不收敛**（q-0029/0034/0035/0036 均 state=done 而 HEAD 行数与 dup 组数不动），而同册**纯新增/改非键字段**的 q-0011/0014/0030/0032 全部如期收敛 ⇒ 机制＝三向合并按复合身份键（含 name_zh）匹配，删除判不成「同一条的删除」。

**一键命令（候 Owner 或总指挥静默窗签发）**：

    python scripts/governance/d3_metadata/add_module_translation.py --dedupe --dry-run
    #   预演＝「6 组重复 / 拟删 6 条」；本包已亲验其零丢失（module_path 集合差 0、逐径字段并集比对 0 丢失）
    python scripts/governance/d3_metadata/add_module_translation.py --dedupe
    #   签发后执行（同一工具：信息最全条目胜出 + 扩展字段合并 + CAS + 幂等）

**同因附带项**：`src/zephyr/strategy_factory/owner_band_t/data_loader.py` 的零字段裸 stub 行（该件之所以仍计「缺 plain_zh」全因它被遮蔽）随同一次 `--dedupe` 收掉；工具侧修法已在 D11。

---

## 3.9 收官后补录（06:1x 循环检查轮 · Owner 睡前令「检查到连续两次问题=0」）

**循环检查证据链（本轮实测，不采信上轮自述）**：

1. **两轮一致性**：align 连续两跑 `align_r6` / `align_r7` 各 96 行，滤时间戳后**唯一差异**＝两跑之间他会话改翻译册行数（声明 7689→7688、去重后可见 7683→7682）；题集恒定 硬=3 / 软=993 ⇒ 本包侧无新增漂移、无振荡。
2. **硬=3 归因（已定死，非猜测）**：三项全是 `治理双向: 裁定#383/#387 related_arch 悬空`。HEAD 侧直接跑同一判据函数（`src/zephyr/gov_enforcement/registry_alignment.py:449 _ruling_arch_errors`，读 `git show HEAD:` blob）实测 **dangling=0**——该三值已由 `st-audit-all-20260924` 在 `a74e9a6c48` 摘除并入 HEAD（与本包独立推出的同一处方）。align 仍报 3 的**真因**＝主区工作树/索引此刻携带 **662 件外来 staged 陈旧快照**，其中 `ruling_registry.yaml` 的 staged blob（`771ec4acf4→f84392cd7e`）会把那笔修复**原地回退**。
   ⇒ 这是 [[hot-file-wipe-forensics-20260918]] 那族事故的**第三次复现前置态**（尚未发生）：谁先在这颗雷上从主区直提，谁就吃别人一册。**本包不代修**（AGENTS §3.4 owner 责任制），只登记并把它从「本包问题=0」的口径里排除：HEAD 真值＝0，盘面真值＝他会话在途。
3. **工作树袋面判弃**：会话工作树 `module_translation_registry.yaml` 残 delta 164+/8−，四族键集比对 **only-in-WT=0**（entries 7687/341/17/968 与 HEAD 全等），逐键信息量比对 **WT 不优于 HEAD 者 0 条** ⇒ 纯陈旧 churn，已 `git checkout HEAD --` 丢弃（零丢失，非"怕门神"）。
4. **⑤ 生成器自动化补挂落地**：`generator_registry.yaml` +2 条（`module_algorithm_overview` / `governance_map`）从主区 disk 那堆外来 staged 海里取出，移入会话工作树并**重基 HEAD**（common prefix 365 行＝HEAD 全量，追加 21 行、0 删除）→ CAS `safe_write_text` + YAML parse 校验 → 即基即投 `q-20260924-st-align-dirty-20260924-0040`。
5. **把 GOMAP 交给自动再生之前的安全预检**：`scripts/governance/generate_governance_map.py:363-390` 的人工层（`pipeline` / `out_of_scope_refs` / `effective_from`）是**读现有产物原样保留**（缺失才回落默认），机器层全量重建，`--dry-run` 实测零写入 ⇒ 登记进编排器不会吞人工层；且 align [9/9] 已实证机生层 424 ≡ `scan()` 重建（硬=0），自动再生不产生漂移。
### 3.10 收官二程（06:2x，Owner 睡前令之「落地 + 循环检查 + 红蓝」补录）

- **⑤生成器自动化补挂已落** = `6199c0752a`（06:20:37，`git log -1 --name-only` 实测袋面 1 件 = 落地面 1 件）。主区那枚游离的未暂存改已 `git checkout HEAD --` 归零（本包在主区不留未落地字节）。
- **台账与 R2 交付件入库**（本包第 3 件欠账，之前只 stage 从未 commit）：`LEDGER.md` + `working_cleanup_r2.md` 需 CREATE-GUARD creation_token ⇒ 走 `batch_creation_tokens.py` 登记 + 同批正门。
- **新工具缺陷 D18（本轮亲撞，已用处方绕过）**：`scripts/governance/d3_metadata/batch_creation_tokens.py` **不认 `ZEPHYR_WORKTREE_ROOT`** —— 以 worktree 为语境调用时它把 token 直写**主区**热册 `capability_canonical_file_registry.yaml`（该册此刻正被他会话在途持有，`MM`）。
  · 与 D-族既有事实同型：生成器侧 `zephyr.shared.io.paths` 认该 env，本工具走自己的路径解析，不认。
  · 处方（可套用）：跑完后 ①把「HEAD + 本次新增行」整份 CAS 写进**工作树**副本，②再用 `safe_write_text(main, HEAD_bytes, expected_base_sha256=<当前盘 sha>)` 精准撤销主区越界写（**不要** `git checkout HEAD --`：主区该册 index 侧有他会话在途字节，checkout 会连 index 一起 reset = 吃别人暂存）。
  · 正证：本次新增 10 行 / 删除 0 行（逐行前缀比对 common prefix=47161、suffix=1），撤写后主区 disk sha ≡ HEAD blob。
  · 修法（候裁，本包不擅改他人工具）：token 工具的路径解析改走 `zephyr.shared.io.paths.REPO_ROOT`（与生成器同根），即天然支持 worktree 隔离。
- **外来面复核（不代修，仅登记）**：主区 index 此刻仍挂 **662 件**他会话 staged 内容，其中 `ruling_registry.yaml` 的 staged blob 会把 `a74e9a6c48` 那笔「悬空 related_arch 摘除」**原地回退**（热册蒸发第三次复现前置态）。谁先从主区直提谁吃这雷；本包按 §3.4 不动，只把它从「本包问题=0」的口径里排除，并把 HEAD 侧真值（dangling=0）与盘面假值（=3）的差额证据钉在 §3.9-2。
- **安全项须 Owner（R2 附带发现，非本包可修）**：`docs/_working/2026-09-12-alt-data-handoff.md` §2 表（第 51-56 行）明文列五家真实 API 凭证，`archive/2026-09/c_class_scattered/` 内有逐字节第二份，两份均已入 git 历史；该文件自身第 59/117 行写着「值只进 `.env`」。本包全程未复述任何值。处置=Owner 轮换 + 决定是否重写历史；门禁盲区=SECRETS 三 gate 未覆盖 md 表格形状（随 D2/D3 同窗裁）。
### 3.11 独立对抗审查卷宗 triage（第 4 轮红蓝 · 06:2x，逐条实证后处置）

外部复核代理（未参与施工、只读）对我 5 条自述做伪证攻击，判 2 条 FAIL。逐条亲验后处置：

| # | 判 | 我复核实测 | 处置 |
|---|---|---|---|
| 1 | 断言「六册皆 gitignore 派生物」**部分假** | `check-ignore` 对 `docs/02_.../09_ai_architecture/` rc=1（该册 10 件 tracked，含 `derived_graphs/01..06.md` 头注 `status: generated`）；tracked 手编件六册合计 **16 件**（我写 6） | §0.5-1 口径改窄=「01/02/05/07/08 五册主体 gitignore，09 册 tracked 且本包按占用令跳过」；手编件数 6→16 更正。09 册 tracked 派生 md 属**他包写域**（占用令在册），不代修只登记=D19 |
| 2 | GOMAP 恢复+人工层 | HEAD counts=423/250、`- module:` 实数=423 自洽；`pipeline`(L0-L6)/`out_of_scope_refs`(4)/`effective_from 2026-09-15` 三键俱在且非空 | PASS，无需动作 |
| 3 | 翻译覆盖 missing=3 | universe 3982 / missing 3 / short 0，三件路径与我 §3.1 全等 | PASS |
| 4 | 「塌零丢失」**口径假** + 反样板非零 | ①HEAD `generic=4`（`alt_source_bootstrap.py`/`akshare_alt_provider.py`/`akshare_provider.py`/`akshare_quote_provider.py`）——我 §3.1 写「样板 0」是拿旧尺读的；②6 组 dup 中 4 组两行 `name_zh` 各有非空不同值，其中 3 个弃值可证为提取器 junk（`未成交`/`回踩质量 A` 为留存值子串、`和自治边界违反` 为留存 plain_zh 子串），但 **`batch_entry.py` 的弃值 `职责` 两者皆非** ⇒ 「被删行不携带存活行所缺字段值」严格为假 | §3.8 Owner 批准依据**改写**（见下）；generic=4 单独派研究子代理取原文，能抄则就地替换（纯改非键字段=队列可收敛），抄不到则诚实登记 |
| 5 | §3.8「唯一残留」**假** | 第二条腿实存：`fail_open_register.yaml`@HEAD 有 **14 处**指向 `commit_gates/registry_family/registry_mass_deletion_gate.py`，而该目录 `git ls-tree HEAD` 为空（0f08f7a06c 明写「registry_family 迁移彻底撤案」），flat 真身在册 | 本册头注「派生物禁手改，重生成=generate_fail_open_register.py」⇒ 按 ① 的姿势**重跑生成器**：wt_head(1de609aeb1) 实测产 1711 处/291 件、`registry_family` 命中 **0**、flat 路径 12 处、对 HEAD diff 1064 行（两日代码漂移的正当刷新）。落地走正门单件袋=B2，同时给「删除类批次队列是否收敛」补第五次证据 |

**§3.8 批准依据改写（Owner 只看这段）**：塌回 6 组重复行的信息损失面 = 3 个 `name_zh` 弃值经证为提取器误取 junk（子串可回推），**1 个弃值 `职责`（`src/zephyr/research/evidence/batch_entry.py`）不可回推**，属真值损失的一枚钉子；其余字段（domain_id/responsibility_layer/desc_*/name_en）6 组全等或全空。故「零丢失」应读作「**近乎零丢失，唯 `职责` 一词须 Owner 决定保留哪侧**」。

**新增登记**：D19=09 册 tracked 派生 md（10 件）与本包 §0.5-1 口径不符，属他包写域，候其 owner 依 #ARCH-GOV-BUDGET-001 同裁定处理；未申报连坐删除一枚补记入 §3.7：`53cdc66e06` 曾 `D docs/_working/disk_reorg_campaign/LEDGER_final.md`（22 行），后由他包 `ad574f63ff` 复原为 57 行（本包 D12 型吸收，此前只记 canonical+工厂图两件，漏记此件）。
### 3.12 反样板残面清算与「共用值 12 行」全归因（06:3x，第 4 轮红蓝的续刀）

`closing_selfcheck.py` 复跑＝15 绿 / 1 红（红仍是 unique_key 违例组数=6）。另铸尺子 `probe_dangling_refs.py`（**HEAD 位面专测**，禁读盘面——盘面此刻被 662 件外来 staged 污染，见 §3.9-2）扫 17 本 tracked 派生册：`TOTAL_DANGLING=258`，逐本定性如下（这是「派生册是否只与已提交代码同源」的第一次全量普查）：

| 册 | dangling | 定性 | 动作 |
|---|---|---|---|
| `fail_open_register.yaml` | 14（registry_family 路径） | 生成器快照停在 09-22，撤案后未重跑 | **已治**：wt_head 隔离重跑产 1711/291、命中 14→0，袋 q-0042 |
| `module_translation_registry.yaml` | 248（strict 口径）/327（module_path-only） | 基线 09-23 前已存 **321**，本包窗口新增 **6**（`scripts/audit/t0_*` 5 件=st-t0 系先登记后落码；`scripts/backup/library_ledger_backup.py`=st-library `1de609aeb1` 明写「TRANSLATION-COVERAGE 前置」） | 非本包债，登记 **D21**（前置登记与后置落码之间的窗口期悬空＝结构性口径，须判"允许前置"还是"禁止前置"） |
| `governance_operations_map.yaml` | **0**（426 refs） | GOMAP 与 HEAD 树同源，我此前 424 是粗尺假阳 | 无需动作（并记：粗尺 substring 口径把字段名一起吞进路径，量级放大 3 个数量级） |
| `rule_catalog_registry.yaml` | 2 | `state_vocabulary_registry.yaml` + `sop/library_sop/index.md` | 随 D21 一并候总指挥派 |
| `path_ownership_map.yaml` / `registry_of_registries.yaml` / `gate_registry.yaml` / 其余 9 本 | 0–1（1 为 glob 假阳） | 净 | 无需动作 |

**反样板 `plain_zh` 12 行逐行归因（本包自伤账补全）**：
- 8 行 = 4 组重复 `module_path`（同一路径两行共用同值，因我 q-0036/0037 把正确值**广播**进重复行）→ 随 §3.8 `--dedupe` 一并塌回，非独立债；
- 2 行 = 克隆对 `governance/data_governance/akshare_provider.py` ↔ `akshare_quote_provider.py`（227 字节同体，只差两行头部路径；两份 algo_flow YAML intro 亦逐字同）→ **任抄必撞**，改文案无解，须走克隆/退役裁决=**D20**；
- 2 行 = `scripts/audit/cost_trio_exam.py` ↔ `docs/_working/kimi_audit/lane_reports/cost_trio_exam.py`（同一物理脚本两处登记）→ **本包第 9 次自伤**：④ 双盲收尾时我给 `_working` 侧越权登记了一行（reconciler `_is_in_scope` 只放行 `src/zephyr`+`scripts`，_working 侧本不该在册）。处置与 §3.8 同一把刀：`--dedupe` 之外再删该 `_working` 行（净删 1 行，同属 §5.2 门位，已并入同一键命令面）。
- **本轮已消 2 行**（袋 q-0043）：`src/zephyr/alt_data/alt_source_bootstrap.py`、`src/zephyr/data/implementations/akshare_alt_provider.py` 的共用后缀，新值逐字取自各自 HEAD 态 docstring 首两句（只抄不写），`_upsert_entry` 命中更新 is_new=False、+13/−13 同位替换、行数零净删。

**净口径（醒来看这三行就够）**：反样板命中从 4（外部代理给的错路径）→ 实测 6 行；其中 2 行本轮已修，4 行分别属 §3.8 塌回（含本包自伤 1 行）与 D20 克隆对，**全部可一键或一句裁定收口，无需再施工**。
### 3.13 尺子自红勘误（§3.12 表数字作废，以本节为准）+ 热册蒸发第三次复现实录

**A. 我自己的普查尺子当场自红（第 5 次「自写盘点脚本须能红」实证）**
`probe_dangling_refs.py` 第一版把正则字符类里的 `\s`（空白）误写成 `s`（裸字母），等价于"排除反斜杠与字母 s"，后果＝**任何以 s 开头的路径永不匹配** ⇒ 该尺把 `fail_open_register` 报成 `dangling=0`（真值 14 处），并把总数压成 258。数字"小所以看着可信"＝典型恒真假绿。补双控后当场自红：
- `NEGCTL missing_fires=True`（合成缺失路径必须命中）／`present_quiet=True`（真实存在路径必须不命中）；断言不过 ⇒ 尺子退出码 2 且明写"数字不可信"。

**修正后真值（HEAD 位面，17 本 tracked 派生册/热册，两轮跑 diff=0）**：`TOTAL_DANGLING=315`
| 册 | dangling/refs | 定性与处置 |
|---|---|---|
| `module_translation_registry.yaml` | 248/7560 | 逐笔归因：基线（09-23 开工前）321 组中 **0 由本包造**；本包窗口新增 6 条全部=他包"先登记后落码"（`scripts/audit/t0_*` 5 件＋`scripts/backup/library_ledger_backup.py`＝`1de609aeb1` 自述"TRANSLATION-COVERAGE 前置"）⇒ 判据口径问题（允许前置 or 禁止前置）=**D21 候裁**，非脏数据可删 |
| `path_ownership_map.yaml` | 62/7910 | 无生成器声明=**手工维护的静态清单**（违 AGENTS §9.5）；同册在册键 `config/capacity_params.yaml`、`scripts/data/backfill_*` 等已不存在 ⇒ **D23 候派**（治本=纳入 `generate_path_ownership_map.py` 编排，该生成器存在但未挂本表） |
| `fail_open_register.yaml` | 2/285（行级 14 处） | 本包已治：重跑生成器后 `refs=291 dangling=0`，袋 q-0042 |
| `rule_catalog_registry.yaml` | 2/283 | `state_vocabulary_registry.yaml`＋`sop/library_sop/index.md`；有生成器未重跑（热册+他包在途）⇒ 随 D21/D23 同窗派 |
| `rule_ai_perception_index.yaml` | 1/1 | 命中的是 `rules/trae_*.yaml` **glob 字面量**＝尺子假阳（已在负控之外另记：glob 不作路径判） |
| 其余 12 本（含 GOMAP 426 refs、ROOR、gate_registry、registry_master_index…） | 0 | 净 |

**B. 热册蒸发第三次复现＝本包自己的落地被抹（首次以受害方视角全程留证）**
- 06:20:37 本包 `6199c0752a` 落 `generator_registry.yaml`（365→386 行，+2 条生成器自动化）。
- 06:51:41 `20885a28f2`（st-pipeline-final）以**袋内携带的陈旧基底字节整档写回**该册 ⇒ HEAD 侧 386→365、`- name:` 30→28，本包二条**当场消失**。`git log 6199c0752a..HEAD -- <册>` 区间内仅此一笔触该册，逐行前缀比对 common prefix=365＝HEAD 全量、缺失 18 行恰为我那二条的尾部 ⇒ 定性=整档覆盖，非合并冲突。
- 这是 [[hot-file-wipe-forensics-20260918]] 那族事故的**第三次**（前两次 GOMAP 被 `8135b0675d`/`0f08f7a06c` 钉回 416），也是本包第一次从"加害方/旁观方"变成"受害方"——**同一颗雷，谁都可能踩**：防护缺失点不在某个文件，而在「整档写回型 tracked YAML 无基底新鲜度校验」。
- 处置：①零判据改动、不代修他包（§3.4），只按"即基即投"重投同一内容（袋 q-0044，工作树袋面 vs 当前 HEAD=+21/−0，逐字节同源）；②处方 **D24 候判据班**：`HOT-FILE-BASE-FRESHNESS` 从白名单热册扩到「头注声明 `generated_by`/派生/registry 的全部 tracked YAML」，或更通用——袋内任一 tracked 文件对 HEAD 呈"纯删除整块"形态即要求显式 `allow_mass_edit` 声明（`safe_write_text` 已有此闸：本包刚才试图重写该册时被 `RegistryMassEditRefused` 拦下＝同一判据在写侧已存在，只是提交侧不查）。
### 3.14 残留总表（收官定稿 · 每条含"为何本包不自闭"+"属主"+"一键"）

> §3.8 把残留写成"唯一一件"＝**口径过窄**，本节以实测替换它。判据：凡①属 §5.2 high 门位（注册表净删）、②属他包写域（§3.4）、③被机制硬挡（队列结构性不收敛）者，本包一律**登记不擅动**；其余全部已自闭。

| # | 残面（HEAD 实测） | 为何本包不自闭 | 属主 | 一键 |
|---|---|---|---|---|
| R1 | 翻译册 entries 段 6 组重复 `module_path`（rows 7688/distinct 7682），含本包自伤 4 组＋`data_loader.py` 零字段 stub 遮蔽＋`cost_trio_exam` 双侧登记 1 组 | 塌回=净删 ⇒ AGENTS §5.2「注册表净删」high 门位→Owner；前例 `66e6b31346` 即"Owner 全批＋静窗"；且删除类袋经队列实测 4 次不收敛 | Owner（或总指挥静默窗代签） | `python scripts/governance/d3_metadata/add_module_translation.py --dedupe --dry-run` 预演「6 组/拟删 6 条」→ 去 `--dry-run`；`docs/_working/kimi_audit/lane_reports/cost_trio_exam.py` 那行属越权登记，同一刀内删（本包第 9 次自伤，见 §3.12） |
| R2 | `fail_open_register.yaml`@HEAD 有 14 处（2 条去重路径）指向已撤案的 `commit_gates/registry_family/…` | **机制硬挡（新发现 D25）**：`commit_queue_landing.is_registry_mergeable()` 对 `…/_registry/catalogs/*.yaml` 一律走条目级三向合并，而本册顶层 `scan_roots: ["src/zephyr","scripts"]` 是**纯标量列表** ⇒ `_index_family_blocks` 判"存在身份判不了的条目（非 dict/首字段非标量）"⇒ **该册自 2026-09-22 起任何改动都无法经队列落地**（q-0042 死信实测，非本包内容问题）。正解=静默窗直连或 `--reconciler-verify` 豁免通道（三前置含"主区 clean"，此刻主区挂 662 件外来 staged→不可用，故本包不硬闯） | 提交系统域（st-commitsys）判据修 D25＋任一包静默窗直落一笔 | 生成器与字节已备好：`ZEPHYR_WORKTREE_ROOT=<wt> python scripts/governance/d7_code/generate_fail_open_register.py`（实测产 1711/291、悬空 14→0），静窗内直提该单件 |
| R3 | 克隆对 `governance/data_governance/akshare_provider.py` ↔ `akshare_quote_provider.py`：227 字节同体，只差 `[MODULE]`/`[ALGO_FLOW]` 两行；两份 algo_flow YAML intro 亦逐字同 ⇒ 两行 `plain_zh` 恒被 `is_generic_plain_zh` 判样板 | 改文案无解（任抄必撞）；治=退役其一或显式承认合理重复，属 **RULE-CLONEGUARD 无逃生** 的裁决面＋他包建件历史 | Owner/克隆裁决域 | 先跑 `python -c "from zephyr.governance.clone_guard import check_before_write"` 侧证据已在 §3.12；处置二选一：退役 `akshare_quote_provider.py`（`src/zephyr/governance/__init__.py:187` 实际 import 的是它）或就地标 `acknowledged` |
| R4 | 明文凭证件：`docs/_working/2026-09-12-alt-data-handoff.md` §2 表（第 51-56 行，五家真实 key）＋ `archive/2026-09/c_class_scattered/` 同名第二份，两份均已入 git 历史 | 轮换第三方密钥＝Owner 的事；历史重写＝高风险不可逆操作，本包禁动（RULE-GIT-SAFE）；本包全程未复述任何值 | Owner | 轮换→再决定 `git filter-repo`（本包建议：先轮换，历史重写可不做）；门禁侧盲区（md 表格形状未被 SECRETS 三 gate 覆盖）随 D2/D3 同窗裁 |
| R5 | `docs/02_.../09_ai_architecture/` tracked=10 件（其中 `derived_graphs/*.md` 头注 `status: generated`）＝tracked 派生 md，与 #ARCH-GOV-BUDGET-001 口径冲突 | 该册＝st-ailayer 系写域（占用令在册），§3.4 不代修；本包只在 §3.11 把"六册皆 gitignore"的旧口径改窄为"五册 gitignore＋09/10 tracked" | 09 册属主会话 | 由属主按 `.gitignore` 既有裁定决定是否摘 tracked |
| R6 | `docs/03_modules/path_ownership_map.yaml` 悬空 62 处、无 `generated_by` 声明＝手工维护的静态清单（违 AGENTS §9.5）；`generate_path_ownership_map.py` 存在但**未挂 generator_registry** | 挂编排器=判据级（与 §3.10 本包已做的 +2 条同类，但那两条是挂载既有自动化且经实测安全；本册 62 处摘除属净删面）＋该册属治理域写域 | 治理域/总指挥派 | `python scripts/governance/generators/generate_path_ownership_map.py` 先跑看 diff（本包未跑：该册此刻被他包在途持有） |
| R7 | `directory_registry.yaml` 缺 `scripts/patrol/`、`scripts/reports/` 两条目录职责 | 该册头注 `ai_autonomy: human_gated`＝文件级人门位，本包不违门 | 总指挥/Owner | 两条拟增文本已在 §2-② 小节原样给出（照 hooks 现有形状） |
| R8 | `scripts/patrol/zcode_workspace_patrol.ps1` **未入 git**（盘上 09-23 02:29 建），而 canonical 册已为它记了一行 ⇒ 干净工作树看不到该资产 | 非本包建件（xhs 战役产物），代提交他人未落地资产＝越权；且 .ps1 挂 depgraph 被 GATE-DEPGRAPH-SCOPE/ARCH-061 拒（§2-② 已记 D4 判据矛盾） | xhs/巡逻件属主 | 属主一笔 `git add`＋正门；D4（.sh/.ps1 扫描阶段缺失）与 D21（先登记后落码是否允许）同窗裁 |

**自闭面（对照，免得被当成"一堆没干完"）**：①派生册重建（六册本地重跑零提交＋GOMAP 蒸发回归修复已落 `ef85cda27b`）②顶层三目录审计口径修正（2/3 本已挂齐，真缺口 1 件→R8）③翻译册 plain_zh 430→**1**（本轮再补 2 件缺源，见 §3.15）④43 双盲→**0 未归因**⑤生成器自动化补挂 2 条（`6199c0752a` 被抹后按"即基即投"重投 q-0044，并新增 D24 蒸发防护处方）⑥反样板命中 4→**2**（余 2 属 R3 克隆对）⑦R2 交付件与台账入库（q-0045）⑧`fail_open` 悬空治本字节已产待落（R2）。
### 3.15 收官三程（07:0x–07:1x）：本包一次连坐蒸发自捕＋两处机制硬挡定性

1. **本包第 10 次自伤＝连坐蒸发的加害方实录（当场自捕并复原）**
   落地笔 `0fe090715f`（本包 q-0043 反样板批，声明 1 件）`git show --name-status` 实带 **3 件删除**：st-library-final 06:26 刚落的备份馆三件套（`scripts/backup/library_ledger_backup.py` 264 行 / `scripts/register_library_ledger_backup_task.ps1` 40 行 / `tests/scripts/backup/test_library_ledger_backup.py` 147 行，合计 −451 行）。
   - 捕法＝AGENTS §2.5「commit 后必做 `git log -1 --name-only`」，非运气；这条纪律今晚第二次救回别人成果（第一次见 §3.5-⑦）。
   - 复原＝逐字节取 `git show 0fe090715f^:<path>`（三件 sha256 前 12 = f505056f80df / 8e75cd1963c5 / ba24b7fe43f0，断言与父提交相等），**不取主区盘面字节**（盘面另有该会话其后未落地改动，代其落地＝二次越权）→ 新袋 q-0046 走正门。
   - 机制读法（补 D12 处方原料）：落地块 `_prestage_snapshot` 只 `git add` 袋内件，但 serializer worktree 的 index 里**残留的 delete 记录**（他会话在主区造成的文件消失态）会随同一次 commit 入面 ⇒ 「袋面件数≠落地面件数」的成因不只是 add 侧，也在 **rm 侧**。建议防线登记 **D26**：commit 前对 `git diff --cached --diff-filter=D` 与袋内声明做集合差，非袋内删除一律拒落＋死信。
2. **两处机制硬挡（不是本包畏难，已给出一键解）**
   - **D25**：`is_registry_mergeable()`＝`_registry/catalogs/*.yaml` 一律条目级三向合并，而 `fail_open_register.yaml` 顶层 `scan_roots: ["src/zephyr","scripts"]` 是**纯标量列表** ⇒ 合并器判"身份判不了"直接死信（q-0042 实测）。⇒ 该册自 2026-09-22 起**任何**改动都经不了队列；治本=合并器按 `_scalar_family_keys` 既有概念放过标量族，或派生册声明 `merge_strategy: whole-file` 并改由基底新鲜度把关。字节已备好（重跑生成器 1711/291、悬空 14→0），待静窗直落。
   - **D24**：本包 06:20 落的 `generator_registry` +2 条被 `20885a28f2`（他包袋携陈旧基底整档写回）于 06:51 抹除（386→365 行、30→28 条）＝热册蒸发**第三次复现**，也是本包首次当受害者；已按"即基即投"重投（q-0044）。处方＝基底新鲜度门从白名单热册扩到"头注含 `generated_by`/派生/registry 的全部 tracked YAML"，或对 HEAD 呈"纯删除整块"形态的 tracked 文件强制 `allow_mass_edit` 声明（`safe_write_text` 写侧已有此闸，提交侧不查）。
3. **③ 翻译覆盖终面**：HEAD `missing` 3 → **1**（q-0047 补 `registry_batch_edit.py`、`c3_throttle_attribution.py` 两件，文本逐字取自各自 HEAD 态 docstring/注释；`_validate_plain` 曾以"CJK 5<8"拒过首版＝尺子有效）。唯一余项 `owner_band_t/data_loader.py` 属 §3.14 R1 的 `--dedupe` 刀面（Owner 门位）。反样板命中 4 → **2**（余 2＝R3 克隆对，改文案无解）。

### 3.16 复原落地核账 + D26 让位 + 跨包 stash 事件（07:3x）

- **复原批已落** = `18e5af5101`（07:29:42）：三件 `A` 且对 `0fe090715f^` **逐字节相等**（`git show … | sha256sum` 两侧同值 f505056f80df / ba24b7fe43f0），本笔 `--diff-filter=D` 计数=0。
- **但本笔仍带出 1 件外来 `M src/zephyr/library/librarian.py`**（非袋内件，方向为改动非删除）——归属须 st-library-final 自行 `git show 18e5af5101 -- src/zephyr/library/librarian.py` 复验是否其本意版本；本包不代判他包内容。
- **D26 让位并合并进他包已定根因**：本包 §3.15 提的"commit 前对 `--diff-filter=D` 与袋内声明做集合差"只是症状防线。**真根因由 st-audit-all-20260924 今晚先证毕**：`scripts/commit_queue.py:696/712` 的 `base_blob` 恒 `None`（自述"B 段填 `git rev-parse HEAD:{path}`"从未做），而 `commit_queue_landing._merge_registry_file:1071-1075` 缺 base 时兜底 `base_sha=old_dev^` ⇒ 相隔 4–8 分钟落地的他人条目在 base 里"已存在"、在陈旧快照里"不存在" ⇒ 被忠实判成"theirs 主动删除"。本包两次事故（`0fe090715f` 抹别人 3 件、`20885a28f2` 抹本包 2 条）均为该根因的第 6/7 例；**修闸归属=st-commitsys，本包不重复开方**。修好前本包对其处方照做：热册每笔落地后 `git show HEAD:<path> | grep -c <关键条目>` 复验，不看"提交成功"回执。
- **推论（写进 R1 的批准条件里）**：base 修复前，任何"净删类"袋（含本包建议的 `--dedupe`）都有连带吃掉他人条目的高概率——这正是本包四次不收敛的机制解释，Owner 批 R1 时宜与 base 修闸同窗。
- **跨包事件登记（非本包过错，但影响本包交付面）**：07:2x `st-pipeline-final-20260924` 在**主区**执行 `git stash`（含 untracked：`stash@{0}: On dev: … frontend_map 14行A包WIP临时隔离`），一次性卷走 ①那 662 件外来 staged 内容 ②**本包两枚尚未落地的文档** `docs/_working/align_dirty/{LEDGER.md,working_cleanup_r2.md}`（`git stash show --include-untracked --name-only stash@{0}` 实测命中二者）。
  · 零丢失依据：本包权威副本一直在会话工作树 `.aidrafts/st-align-dirty-20260924/docs/_working/align_dirty/`（LEDGER 108,981 B / 交付件 449,020 B，07:24 字节），且正门袋 `q-0048` 快照按内容寻址存于 `.runtime/commit_queue/blobs`，不受 stash 波及。
  · 遗留风险（交总指挥/st-pipeline-final）：其 pop 时会把 §3.9-2 那颗雷一起带回盘面——`ruling_registry.yaml` 的 staged 旧态在 stash 内仍会把 `a74e9a6c48` 的悬空修复**原地回退**。本包不 pop、不 drop 他人 stash（RULE-GIT-SAFE：`stash pop/drop` 属可毁他人工作项）。

### 3.17 撤回一条自己刚提的缺陷（D23 作废）＋普查判据的第三类假阳

`path_ownership_map.yaml` 在 §3.13/§3.14 被我判为"手工静态清单违 AGENTS §9.5、62 处悬空"。**实测证伪**：
- 主区跑 `python scripts/governance/generators/generate_path_ownership_map.py`（rc=0，`conflicts: []`）后 `git diff --numstat HEAD -- <册>` = **空**、盘上 sha256 前 12 跑前跑后同为 `c9c420a0b0c0` ⇒ 该册**已是生成器确定性产物**（我按册内没有 `generated_by:` 头注就判"手工维护"＝把"缺自述"当"缺实现"）。
- 其 63 处"不在 HEAD 树"的路径经分类：一部分**盘上存在但未入库**（他包在途 WIP 的"所有权先于落码登记"），一部分是已退役路径的所有权留痕 ⇒ 二者都非脏数据。
- ⇒ 本包**撤回 D23**，并把 §3.14 残面的 R6 一行改判为"无需动作"；同时把这条并入 **D21 的正解口径**：`悬空引用`必须先分三类再谈清剿——①**真悬空**（指向被撤案/改名后的位置，如 `fail_open_register` 的 registry_family 14 处、`ruling_registry` 已被 `a74e9a6c48` 摘掉的 3 处）＝该修；②**前置登记**（先记账后落码，如 `library_ledger_backup`、`t0_*` 五件、path_ownership_map 的在途件）＝该由判据决定允许与否，不是脏；③**历史凭证**（creation_tokens 建件凭据、退役留痕，见 §3.2-③）＝**禁改**，改了是篡改审计链。
  本包的尺子（`probe_dangling_refs.py`）只能给"形状可疑"的分母，**分类必须逐册读语义**；把三类混成一个数字报给上级＝下一班照数去删就会删错。这也是本包今晚第四次给自己的盘点脚本开红证（前三次：D3 撤回、GOMAP 424/423 口径、粗尺 substring 假阳）。
