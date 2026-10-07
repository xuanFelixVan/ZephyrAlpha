---
created: 2026-10-07
auditor: st-extaudit-20261007
ttl: task_bound
completes_when: 总报告交付并经 Owner 查收后随战役树归档
---

# 车道 H：过渡工程/不必要工程专项 findings

审计对象：st-mastertc 总包夜战（2026-10-06 夜~10-07）全部 HEAD 产出。基准 HEAD=649a8c93c7，战役基线 014ccf5b18。全程只读，零文件写入，零 git 状态变更。

## P0 候选

**H-P0-1 close_lane.md 交付台账错哈希归属：把未落地内容标成"已落地"（假完成）**
- `docs/_working/master_tc_night/99_delivery/close_lane.md` §三在途袋表 L35：`| q-...-l6-0004 | 8 | 落地 45c1f0b224（signal_ashare 三件+测试+双册） |`
- 实证：`git show --name-only 45c1f0b224` = **5 文件 docs 袋**（34_trigger_surface/p2_card_ledger/L6 workbook/双注册表），不含任何 src/测试；`git log --all --diff-filter=A -- src/zephyr/signal_ashare/limit_up/event_axis.py swing_sequence.py resonance_pair.py` = **空**（三件在任何分支全史从未 A 落地）；HEAD src 域 A 面=0（见 §产出面统计）。
- 该三件在 `99_delivery/redblue_findings.md` L33-35 被红蓝明确标注 **(untracked)**——审查面知情，但收尾班单仍写"落地+错哈希"。与既证"信号三模块死袋假完成簇"互证，且证明假完成面已渗入交付链正式台账（close_lane 是晨会移交凭据）。

**H-P0-2 quant_methodology 07/08/12 悬空 token：为从未存在的文件预登占位 token（不必要工程+登记面悬空）**
- `capability_canonical_file_registry.yaml` HEAD L45510/45515/45520 三条 token 指向 `docs/_working/quant_methodology/07|08|12_placeholder_skeleton.md`；`git ls-tree` 实存仅 01-06+README+三附录；`git log --all --diff-filter=A` 三路径=**空**（任何分支全史零存在）。
- 落点=b0fe4b5940（st-mastertc-l7 06:19，"M2.1 token 先行"）：merge_evaluation 自称"断号防御；内容全史零命中如实申报；主题命名/撤号=Owner"——**有声明**，故非隐瞒型假完成；但为纯编号美学（断号）给全史零内容对象登记 token，是登记面自造悬空引用，与 module_translation_registry 4 条幽灵条目（他车道已证）同型。撤号=内收判据②的正解。

## 产出面清单统计（第 1 项）

**commit 集口径勘误**：`git log --grep=st-mastertc` 实得 **47** 条；剔除任务书点名 2 条他队件（7e6f66d055/e5118cd455）后为 **45**，非 44。再甄别：649a8c93c7=外部审查批0 自身 token 登记（st-extaudit，正文提及被审对象）、04f94e865a=st-t3series 会话件（正文提及 st-mastertc-l11），剔除后**总包本体=43 条**；若计入 5e0152917e（GitCommitGateway reconciler 自提交，由本役工作触发）则恰为 44。以下统计基于 43 条本体。

| 域 | 触达文件(去重) | 纯新增 A | 纯删 D |
|---|---|---|---|
| docs | 270 | 44 | 0 |
| tests | 75 | 20 | 0 |
| src | 14 | **0** | 0 |
| scripts | 8 | 4 | 0 |
| config | 5 | 1 | 0 |
| **合计** | **372** | **69** | **0** |

- 全集零删除（两条 `[allow-mass-deletion]` 披露均属实为索引老化伪影，抽核 01bf541fbb 对注册表为纯追加）。
- 纯新增面 69 件：docs 44 全落 `master_tc_night/`（35 件战役树）+`fms_overhaul/` 重建件 6（C473 四簿+mirror_tree_prep+DEEP_DIVE_R2 等）+`fullflow_mining/57_gap_vs_fullflow_matrix.md`+decision_map links 2+commit_speedup 1；scripts 4=grid_stats_engine/lead_lag_validator/retention_derived/backfill_created_from_filename；config 1=chart_resonance_prereg.yaml；tests 20。
- 巨袋两件：01bf541fbb（216 文件=C127 created 回填 209 旧档+L9 重建册）、5ed131fb1d（48 trae_rules 测试重指）。
- **src 纯新增=0**：本役宣称的 src 新模块（signal 三件/tech_factor/fill writer/红证尺）在清单层面即不存在于任何分支——他车道死袋结论在 manifest 层面成立。

## 逐项 verdict（2~7）

**第 2 项：第二真源清查 — 总体 verdict：过渡（声明面齐备，无第二真源坐实），2 处瑕疵**

| 文档 | (a)派生/刷新声明 | (b)与既有真源关系 | verdict |
|---|---|---|---|
| 00_环节总表.md | 头条声明"挂接视图不是新 taxonomy……凡重复处声明真源指针，不复制内容"；读数口径=可复跑 grep；ttl+completes_when 齐 | 指针视图，指向 132 表/fullflow 总册/fullconnect 工单三真源 | 过渡（合规） |
| 交付报告.md 120卡三态表 | 头部声明"数据源=各 lane lane_result.json/workbook/close_lane/orchestration"；126 vs 120 差额 6 卡诚实披露"不臆造" | 派生汇总表，非真源 | 过渡（合规） |
| 57_gap_vs_fullflow_matrix.md | "数据源（机械提取，零手抄）=nightsweep 132 表开口 57 行"；三态判定规则机械可复跑；"不替代各卡六向台账" | 派生对账，明令"禁重建第二真源" | 过渡（合规，六件中声明最规范） |
| c266_owner_gate_list.md | "真源：清单原件=recovered_...checklist §4；裁定册=ruling_registry"；"本卡=对账清单+移交，不直接写裁定册" | 双真源指针对账 | 过渡（合规） |
| c342_ghost_refs.md | 有普查面漂移声明（卡面 37 处→实查 mining 1 处/扩面 16 处） | 三态清单 | **过渡但不完全**：30+ 处"已治愈/随原件蒸发"未逐处考古（自述"逐处考古不经济"），"引用已删"大头判定=待证；交付报告标 DONE 高估了清偿度 |
| p2_card_ledger.md | "真源=links/L02_emotion/_INDEX.md+12 簿 MINE.md"；计数漂移披露（22/24/23 三口径，取簿列 23 为准）；"两战役立卡前 MUST 查本表" | 派生台账，防重复立卡用途明确 | 过渡（合规）；frontmatter"token 待随批登记"已由 45c1f0b224 补齐（token=master-tc-l6-factory-p2-card-ledger-20261007 在册） |

**"零手改真源数字"抽验（3 处）**：
1. 三真源 grep 读数 9/10/1 — HEAD 复跑**逐字命中**（fullflow orchestration=9、nightsweep=10、fullconnect workorders=1）。真。
2. F027 行引用 — nightsweep L46 原行 `F027|E8 组装与资金分配（partial/P0）|开口|—|处方 c_exam_pipeline/05_f27...` 与总表新卡#1 依据完全一致。真。
3. "车道簿 F 号 0 命中" — 在落笔 commit 6072df11ef（09:10）树内**为真（0 命中）**；但 HEAD 已 **140 命中**（7 个 lane 文件，含 c266/p2_card_ledger 自身）——同日上午后续车道批回灌了 F 号，声明未刷新。机械读数声明无 snapshot 哈希印记，属快照陈旧缺陷（非造假）。

**第 3 项：占位骨架清查 — verdict：1 项不必要（悬空 token），其余无真占位**
- quant_methodology 07/08/12：见 H-P0-2（不必要+悬空）。
- master_tc_night 树 grep 占位/骨架/placeholder/skeleton：命中的 01_skeleton 七件**均非占位骨架**——6 个 block 文件（99-133 行/件）是实质派生视图，头声明"环节行/职责/上下游全部复用三真源……只做块视图组装，不重挖不改真源"，作者=超时前任 st-mastertc-mine，经 mine2 复核收编（总表头有收编声明）。定性：合规派生视图，非不必要工程；瑕疵=6 件缺 completes_when（见第 7 项）。
- r5_exemption.md：见第 7 项（非占位、非越权）。

**第 4 项：零消费新模块复核 — verdict：未发现"无声明零消费"新件**
- HEAD 本役 src 新增 .py=0（A 面为空），死袋宣称件均未落地，无需复核消费方。
- scripts 新件 4 逐个：
  - grid_stats_engine.py：消费=chart_resonance_prereg.yaml（status: READY_NOT_FIRED，"禁点火"双保险）+lead_lag_validator import+单测。声明面齐（C324 例外在册）。过渡（规格内观察轨）。
  - lead_lag_validator.py：头标 `[TTL] permanent`+"观察轨 P2：不接生产……negative_result_promise 口径"，CONSUMERS=观察轨报告消费（G-C 主体排产后）+单测。有声明零生产消费。过渡（合规）。
  - retention_derived.py（C440）：`[TTL] task_bound`，CONSUMERS=manual CLI+`.runtime/audit/keep_shadow_*.json`（维护班/晨会判读）+单测。零自动触发器但声明为 manual——与 C128 同型"工具在册无触发器"，唯 C440 卡面本=余量尺，规格内。过渡，P2 关注影子账无人跑则归零价值。
  - backfill_created_from_filename.py（C127）：自声明"一次性回填器 task_bound、本夜实跑读数即验收、无常驻测试面"，已消费一次（209 件）。任务已完成而脚本永久驻留 `scripts/governance/generators/`。过渡偏不必要（P2：归档时应随批退役或声明保留理由）。

**第 5 项：10 条新立卡建议有效性 — verdict：8 真完成 + 2 待证（同夜自相矛盾需仲裁）**
- 10/10 F 号在 132 表逐行实存，状态/优先级引用零错：F027/F028/F072/F082 均为 `partial/P0/开口`（nightsweep L46/47/91/101）、F019 `partial/P2/开口`（L38，建议定 P2 与源表优先级一致）、F033/F058/F087/F096 均 `partial/P1/开口`、F095 `design/P1/开口, design§1.4`——引用精度高。
- 10 条 per-F 处方指针文件 HEAD 全部实存（c_exam_pipeline/05_f27、06_f28、h_sched_recovery/03_f72、i_ai_ops_gov/01_f82、d_l9_knowledge/04_f33、g_backtest_gpu/01_f58、i_ai_ops_gov/06_f87、j_ai_design_gates/02_f95、03_f96、b_factory_inbound/07_f19，逐一 cat-file 通过）。
- 撞车检查：10 个 F 号在分派真源 00_orchestration.md（120 unique 卡号，独立计数验证=120）中 **0 命中**——与既有 120 卡零撞车。
- **矛盾 1（F096）**：C192 矩阵 L74 判"合并｜与 F020 同'胃·全网搜索'职责面，并单至 F020 处理（挂卡 C251）"；W1 总表新卡#9 判"零卡"建议新立——同夜两产出对同一环节给出相反处置，#9 的依据自查只点了"C46 跨环清单未点名"，未对表 C192 并单例外。
- **矛盾 2（F033）**：C192 矩阵 L50 判"重复｜TDM-E-L9-V2 已挖（links/L01 s3/s12），对账动作=挂接引用，禁重建第二真源"；W1 新卡#5 判"三快照判断账本零卡"建议立卡。两表口径轴不同（施工状态 vs 挖矿覆盖）但均以"卡"为处置单位且未互相引用，Owner 收到对立建议。
- 结论：登记行为本身真完成（只登记不扩权），F096/F033 两条建议有效性=待证，须一条总裁定归一后再排产。

**第 6 项：重建版指针纪律（裁定#375 三要素）— verdict：三处全部真完成（过渡义务已履行）**
- C129（fms_overhaul/99_delivery_report.md §十七~廿八，831a35b30a 落）：替代对象=明示"重建版纲要节，非原 640 行全文"；考古指针="原件若有备份/死袋可考古，考古后以原件为准替换本纲要节"+"重建过程零虚构"；终态条件=以原件替换（正文 §廿七）。前置断言核验：C129 前夜文件恰 **240 行止 §十六**（`git show 831a35b30a^ | wc -l`=240，逐字命中声明）。（车道 F 补考：原件字节实存 object DB 悬挂 blob，考古义务未履行=P0-F1，见 lane_f。）
- C473 四簿（S1/S4/S6/S9 README，01bf541fbb 落）：四件 frontmatter 统一含 `status: 重建骨架`+`reconstruction: 原件蒸发（S1-S9 九簿未落地四簿之一）`+completes_when 各异且具体（如 S4="ROOR 补登三条+8 候选净删获 Owner 批+CR-007 回填接线落地"）；替代对象+终态条件齐，考古指针以"原件名不可考"如实缺省（原件从未落 HEAD，无对象可指——属如实申报而非缺要素）。
- C28 备料簿（M3/mirror_tree_prep.md）：`status: W0 备料重建（登记不执行迁移）`+reconstruction 声明+completes_when="W0 备料定版并按 C490 裁定开工 R1-R3 试点批"；"本簿只备料+登记，不执行任何迁移"边界明确；规格真源双指针（NR-006..010+#488）。三要素齐。

**第 7 项：战役树生命周期 — verdict：大体过渡合规，1 项对容缺陷（并入 P0-1），1 项 moot 残留**
- frontmatter 覆盖：master_tc_night 35 件中 ttl 34/35（2 个 JSON 无 frontmatter 属格式豁免）；**completes_when 缺 10 件 md**（01_skeleton 六 block、L3/L6 workbook、34_trigger_surface、p2_card_ledger、r5_exemption）。注意 L0 簿 §五曾声明"TTL-METADATA 8 个 .md 统一补 ttl+completes_when"——该批补齐只覆盖当批，后到件（l6 袋 09:43、l3b 袋 08:35 等）重新引入缺口。
- r5_exemption.md 定性：全文=4 行 frontmatter，为 R5-DIGIT-SUFFIX 门官方逃生通道②的目录级豁免标记。L0 簿 §一实证：门真源=r5_digit_suffix_gate.py（fail-closed），官方三通道=历史违规跳过/本标记/改名；本役选了改名（master_tc_20261006→master_tc_night，600abe9991，18 文件），标记"保留作审计痕迹（改名后豁免语义已 moot，战役收尾可删）"。**非越权豁免面**——是官方通道的合法产物+有声明删除条件的 moot 残留。（审查注：本审查产出目录亦按同款治本先例由 external_audit_20261007 更名 external_audit_mastertc。）
- 残余移交抽验 3 项：
  1. L8 合并 DEFERRED——`git branch` 证实 `session/st-mastertc-l8` tip=cf5b6ddcf7 在（六文件差异面），`merge-base --is-ancestor`=NOT-MERGED，与"分支在、合并窗口无内容风险、等脏面清偿"陈述**对容**。
  2. 裁定#488 落地 6555113e56——ruling_registry.yaml HEAD 命中 #488（2 处），该 commit 单文件纯插入，**对容**。
  3. l6-0004"落地 45c1f0b224 signal_ashare 三件"——**不对容**（H-P0-1：错哈希+内容全史未落地）。
- 附带核验：交付报告 v2"48 测试文件 MOCK_YAML 重指 tests/meta/fixtures"——5ed131fb1d 抽样 diff 确认重指，且 tests/meta/fixtures/g_trae_*_mock.yaml HEAD 实存 48 件，重指闭环真完成；但 v1（13:40）开的"48 stub fixture 回填"处方袋死于 N-16，而 meta/fixtures 48 件最早 04:58 已由他会话（st-cure-p05b 02a191ec33，27 件）分批在位——v1 处方在瞄准旧路径建第二份 fixture，属被门正确拦下的不必要工程微循环（v2 重指收口正确）。

## 证据块

```
E1  git log --grep=st-mastertc --format="%h" | wc -l            → 47
E2  43 本体提交聚合: 372 files | docs 270(A44) tests 75(A20) src 14(A0) scripts 8(A4) config 5(A1) | D=0
E3  git show --name-only 45c1f0b224                              → 5 files(docs+注册表), 无 src/无 signal_ashare
E4  git log --all --diff-filter=A -- src/zephyr/signal_ashare/{limit_up/event_axis,swing_sequence,resonance_pair}.py → 空
E5  close_lane.md L35 "落地 45c1f0b224（signal_ashare 三件+测试+双册）" vs E3/E4 → 错哈希+假落地
E6  capability_canonical_file_registry.yaml L45510/45515/45520 三 token → *_placeholder_skeleton.md；
    git log --all --diff-filter=A 三路径 → 空（全史零存在）
E7  git grep -c "环节" HEAD -- fullflow_mining/00_orchestration.md=9 | nightsweep=10 | fullconnect/00_workorders.md=1
    （与 00_环节总表读数逐字一致）
E8  git grep -hoE "F[0-9]{3}" 6072df11ef -- .../lanes/ = 0；HEAD 同查询 = 140（7 文件）
E9  nightsweep L46/47/91/101/38/52/77/106/114/115：F027/F028/F072/F082=partial/P0/开口，
    F019=P2、F033/F058/F087/F096=partial/P1、F095=design/P1——与 10 条建议引用零偏差；10 处方文件 cat-file 全过
E10 00_orchestration.md unique C 号 = 120（sort -u 计数）；10 建议 F 号在其内 0 命中（零撞车）
E11 57_gap_vs_fullflow_matrix.md L74 F096=合并→F020(C251) vs 00_环节总表 新卡#9"零卡"；
    L50 F033=重复(禁重建第二真源) vs 新卡#5"零卡"
E12 831a35b30a^:fms_overhaul/99_delivery_report.md | wc -l = 240（C129"仅存 240 行止 §十六"断言命中）
E13 S1/S4/S6/S9 README 四件 frontmatter 均含 status: 重建骨架 + reconstruction + 各异 completes_when
E14 branch session/st-mastertc-l8 tip=cf5b6ddcf7 在；merge-base --is-ancestor → NOT-MERGED（DEFERRED 属实）
E15 ruling_registry.yaml HEAD 含 #488（6555113e56 单文件落地）
E16 5ed131fb1d 抽样 diff：tests/fixtures/→tests/meta/fixtures/；tests/meta/fixtures/g_trae_*  HEAD=48 件；
    最早落地=02a191ec33(st-cure-p05b, 04:58, 27 件)——v1 stub 回填处方与在位资产撞车，N-16 拦截正确
E17 master_tc_night 35 件 frontmatter 扫描：ttl 34/35；completes_when 缺 10 件 md（清单见正文）
E18 消费方 grep：grid_stats_engine→prereg+lead_lag+test；lead_lag→test+grid_stats；
    retention_derived→册+blueprint（manual CLI 声明）；backfill_created→册+workbook（一次性器声明）
```

## 小结

**过渡清单（合规过渡，含声明，归档时随批次处置即可）**：W1 挂接视图族（00_环节总表+6 block files）、57 对账矩阵、C266 对账、C342 清单（部分待证）、p2_card_ledger、交付报告/close_lane 主体、grid_stats_engine+lead_lag（READY_NOT_FIRED 规格内）、retention_derived、C129/C473/C28 三处重建件（三要素齐备；C129 的考古义务未履行面见 lane_f P0-F1）。

**不必要清单**：① quant_methodology 07/08/12 悬空占位 token（为全史零存在文件预登 token，撤号优先）；② close_lane l6-0004 错哈希"落地"行（假完成入台账，P0）；③ v1 fixture stub 回填微循环（被 N-16 正确拦下，v2 已收口，留作门有效案例）；④ backfill_created_from_filename.py 任务完成后的持久驻留。

**该并未并清单**：① 同一分派信息的三个静态视图（00_orchestration §二分派真源 / 00_环节总表 §二挂接表 / 6 block files"本夜卡"列 / 交付报告 120 卡三态表）——block files 卡列可由总表机械派生，归档时应收敛为"分派真源+交付报告"两层；② F096 双处置（C192 并单 vs W1 新卡）与 F033 双处置（C192 重复 vs W1 新卡）须总裁定归一后才能排产；③ 132 表/挂接视图/三态表三处状态轴，归档后应只剩 132 表一个活状态轴。

**P1 建议**：1) close_lane/交付报告对 l6-0004 行发勘误（改"未落地，袋在 dead，处方=捞回重投或销账"），与晨会移交同步；2) F096/F033 出一条总裁定归一双表口径；3) C342 的 DONE 改"部分完成"或对 16 处逐处补考古；4) 机械读数类声明（grep 计数/命中数）一律附 snapshot commit 哈希，防 E8 型同日陈旧；5) quant 07/08/12 走 Owner 撤号（内收判据②）。
**P2 建议**：6) 10 件缺 completes_when 的 md 随归档批补齐（6 block files+L3/L6 workbook+34_trigger_surface+p2_card_ledger+r5_exemption）；7) 归档时执行 r5_exemption.md 删除（删除条件已自declared）；8) backfill 一次性器与 retention_derived 在归档批声明退役或转正；9) block files 若保留，卡列改机生（宪法 §9.5 静态清单禁手工维护）；10) p2_card_ledger 的"台账状态"列为手维护判断态，二期排产消费后应回写 INDEX 并退役本表。

**审计口径披露**：本报告所有结论以 HEAD 649a8c93c7 为准；工作区在飞面（他会话）未采信；commit 集=47 grep 命中剔除 4 条非本体（2 条任务书点名+st-extaudit 批0+st-t3series），统计基于 43 条本体，与任务书"44"之差=5e0152917e（reconciler 自提交）归属口径，已在 §统计中注明。
