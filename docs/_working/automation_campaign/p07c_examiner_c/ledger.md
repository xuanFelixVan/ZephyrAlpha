---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑦考工C·findings台账
---

# findings 台账（追加式，禁删改他人行）

格式：`## <MM-DD HH:MM> · <一批摘要>` + 要点若干 + 自检结论（两轮）。
本席四件套建册时点＝2026-10-15 班次 01（st-qoder-p07c-1015-01），本班之前无班次记录。

## 10-15 19:25 · 班次 01（st-qoder-p07c-1015-01）建席首班·全族机动：0 张出分（保底双口径未达，如实呈报）＋对静态席"零可考"的独立第三复量＋类 A 错面升格为落地实测

**本班实际耗时**：起 18:50:19 冷启动 → 19:25 交账 ≈ 35 分（`date` 实测三锚点 18:50:19／19:05:39／19:24:23，非体感）。
**出分 0 张＜8，未跑满 4 小时 ⇒ 保底双口径均未达**，本班不产分数行、不翻卡状态、不改判据门柱（理由见⑤⑥节，非"没干活"）。

### 一、冷启动与值守环境（三态实测，含水位三读）

- 步骤一 python=3.12.8；`setup_dev_env.py --check` usercustomize exists=True／installed（指 D:\\ZephyrAlpha）。
- 步骤二 `lock_files.py cleanup`＝**CLEAN 无死锁需要清理**（与 ⑨席 14 班"释放报 NOT FOUND 而 released=4"不同形态，本班进场即无过期 claim 面）。
- 步骤三 `process_reaper --status` source=live／last_run=18:50:38／scanned=50／whitelist_hits=32／killed=1／reported=2 ⇒ 允许写。
- **水位三读**（本班全程未起 GPU、未装全市场面板，只做单列 CH 聚合与只读尺）：
  18:51 `commit_pct 95.95／degraded=True／breached=[ALERT-SYS-001, ALERT-SYS-003]`→19:2x `90.85／True／[ALERT-SYS-003]`→19:24 `85.74／**degraded=False**`。
  起批闸前读数即 95.95 处我未起任何重计算，与 ⑥席 1015-11 班／⑧B 06 班"degraded 即不试重装载"同纪律。
- reaper dry-run 点名 `would kill PID=2380 reason=runtime_dir_orphan:age=60min cmd=...\.runtime\tmp\st-doc`＝**他会话件，本席不代杀不认领**；
  `worktree_changes=5859 > 50` 并行漂移告警在报（非本席造成，本席未建车道）。

### 二、防重入＝四件套缺失，按指令卡允许路径补建（禁裸建）

- 指令卡要求先读 `docs/_working/automation_campaign/p07c_examiner_c/checkpoint.md`——**该目录盘/HEAD 两面查无**。
- 负空间三扫尽净：①`git ls-files | grep -i p07c` 零行；②`git grep -l -iE "p07c_examiner_c|examiner_c" HEAD` 零行；
  ③全仓 `grep -rliE "p07c_examiner_c|考工c席|examiner_c" docs/ scripts/ src/ tests/` 零文件；
  ④`.aidrafts/*/docs/_working/automation_campaign/` 逐车道快照只见 p01..p10（含 p07_examiner_a／p08_examiner_b），无 c 席；
  ⑤`docs/_archive/**` 无 p07c／examiner_c。**⇒ 本席确为建席首班，无上一班游标可撞**（"两址同读游标"在册教训此处不适用：只有一个址，且它当时不存在）。
- 正对照（防"0 命中是尺坏"）：同批目录同型 grep 对 A/B 席图案命中 **17** 行 ⇒ 尺通、C 席缺席是真缺席。
- SOP 侧核对：§3-A 白纸黑字"只扩吞吐席：考工（⑦⑧→C/D/E…按 preregistered 积压>50 张时每 50 张加一席）"——本班实测积压 171–175 张＞50，
  扩 C 属政策预授权；但 **§3⑦⑧ 席位节与 §3-D 排班表至今未列 C 席**，且 `docs/01_policies_and_standards/_registry/catalogs/seat_registry.yaml`
  是龙虎榜交易席位册（SEAT-INST/YOUZI…）与本生产线无关，非席位登记面。
  ⇒ **SOP 席位节补记 C 席归 ⑩ 线长，本席不代改政策/他席指令面**（指令卡"禁代⑩线长改其它席指令面"）。
- 补建走令在册通道（先例＝`6ba6295646` 十席 40 件"token 同袋登记 autopipeline×40"）：
  `batch_creation_tokens.py --capability p07c-examiner-c`（**ASCII slug**，避在册坑①）
  先 `--dry-run` 预览 4 件 → 实跑回显 `OK: 已登记 4 条` → 册面自证
  `grep -cE "p07c_examiner_c/(scope|instruction|checkpoint|ledger)\.md" capability_canonical_file_registry.yaml` ＝ **4**。
  令牌热册本身未随袋投（在册教训：整档快照入袋＝归属篡改）。
- **在册坑第③条本班实地命中一次**：首次 `--dry-run` 报"无待登记文件（全部已登记或前缀为空）"，
  真因＝当时前缀目录尚不存在（非"已被他人登记"）。工具扫描面＝`git ls-files` ∪ `--others --exclude-standard`，
  空目录自然零候选。⇒ 顺序须"先落件、后登令牌"，CREATE-GUARD 在提交时才看账本，非"登记了才能落笔"。

### 三、分母实测（本班值守内面值被上游推进，两时点都记，不拿旧数当现值）

| 尺 | 18:53 | 19:05:39／46／54（三测同值） | 19:12:59 | 19:2x |
|---|---|---|---|---|
| grep `status: preregistered`（磁盘） | 175 | 175 | **171** | 171 |
| yaml 解析同谓词 | — | 175 | — | **171** |
| `find -name *.yaml` 文件总数 | 552 | 552 | — | 552 |
| HEAD 面 grep | 191 | — | — | — |

- 全树五态加总自证（18:56）：empty 186／preregistered 175／examined 73／blocked_on_data 71／blocked_on_impl 47＝**552**＝文件总数。
- 族分片（18:53）：entry_flow 103／exit_flow 26／portfolio_flow 21／position_flow 25＝175（目录实名 `portfolio_flow`，非 portfolio）。
- **面值移动归因**：19:05→19:12 磁盘 preregistered 175→171，减少的 4 张全在 entry_flow（103→99，见④节 family×class 加总）。
  本班未翻任何卡，故系他席（A/B）在途推进——与 `face-value-moves-under-you-during-shift` 同型；配额面须写实名领卡少写条件式。
- HEAD 191 ＞ 磁盘 171 ⇒ 他席翻卡字节尚未落地（落地链不健康侧证），本席按指令"采磁盘面"不自行合面。
- 分数册（18:56）：双文档结构，doc1 `rows:` 长度 **96**（⑩席 ledger 记 06:12 时 examined 恒 55，现磁盘 73／册 96 行 ⇒ 今日确有产出，非全线停摆）。
- raw 形制尺：全库含 `prereg` 的 `status:` 行**恰 175 处、全为 indent=0 且无引号**⇒ grep 与解析两尺此处同构，无别名/引号漏网。

### 四、独立普查（机动席本职：不复抄 A/B 结论，自带三尺）

`card_binding.classify_card` 逐卡直调（docstring 自陈"零 CH"），n=171 与 preregistered 面**加总自证相等**：

- 类别：**C 120／U 27／B 15／A? 7／A 2／D 0**（加总 171）。可绑面 `_BINDABLE_CLASSES=("A","D")` ⇒ **全班可绑面＝2 张**（均 entry_flow L2）。
- family×class：entry_flow A2+A?7+B14+C50+U26＝**99**；exit_flow B1+C24+U1＝**26**；portfolio_flow C21＝**21**；position_flow C25＝**25**；加总 171。
  ⇒ 与 ⑦A 席游标"entry 族 A2・A?7・…加总 103"在两格上逐字复现（A2／A?7），其 103 与本班 99 的差＝③节那 4 张在途推进。
- 拒因头名分账（加总 171）：`target_face_not_index_next_day` **117**／`panel_deferred` 15／`multi_table_needs_composite_recipe` 13／
  `no_data_binding_section` 13／`table_not_in_recipe_book` 4／`normalization_recipe_undecided` 3／`needs_replay_engine` 2／
  `signal_column_not_a_single_identifier` 1／`executor_horizon_mismatch` 1／none（＝2 张 A）2。
- 类 C 目标面分型（执行器硬绑"指数次日收益"撞空的形状，加总 **117** 与拒因头名精确相等＝两尺互锁）：
  `engine_replay` 64／`other` 27／`panel_stock` 20／`sector_series` 3／`probability_hit` 3。
- 绑定块形状普查：175 张中 **160 张** data_binding 齐 `signal_table+signal_column+signal_derivation+target_source`（CH 表式）、
  **13 张**整块无 data_binding（含积压最久的 10-09 20:25 十二张里多数）、**0 张**申报本地 `derived_series/target_series`。

### 五、类 A 两卡"可绑＝假绿"——本班把它从读码结论升格为落地实测

尺（读码）：`SQL_FACE_DAILY = "SELECT toDate({date_col}) AS d, anyLast({col}) AS v FROM {tbl} WHERE {where} GROUP BY d ORDER BY d"`
——`anyLast` 跨 `sector_code` 塌成每日一值；`c1_market.kline_sector_880` 日频面 per（卡面自证 industry_l1 61 codes＋industry_ths 128 codes），
故该式取的是**任意一个板块**的 amount/close，既非合计也非卡面声明的截面份额。且 `WHERE` 只有 `period='1d'`、**无日期谓词**。

实测（`build_signal(card, cls)` 直调，只读 CH、不写册、不改卡面）：

- `TDM-E-L2-01-2/calibration/02_板块成交额占比活跃度`：返回 Series len=**1595**，index 起 **2020-03-17**（卡 IS 窗起 **2021-08-02**，越界即证无日期闸），
  值 527702.0／781991.0／559322.19…末 2306761.25／1721043.38／2064194.13，nunique 1584——**原始 amount 量级**，
  而卡面 `signal_derivation` 逐字冻结的是"占比=sector amount / Σ(同 code_family 全体 sector amount)（分母口径=industry_l1∪industry_ths，
  由 c1_market.sector_code_name_map.code_family 在册映射界定，禁自拟名单）；环比=占比/占比.shift(5)−1；series 面取占比前 10% 板块等权组合的次日超额与全样本差"。
  份额值域应∈[0,1]，实测值域 5×10^5..2×10^6 ⇒ **不同物**。
- `TDM-E-L2-01-3/calibration/02_多周期动量主导度`：返回 close 首 6594.24／6710.3／6816.43、末 596.77／578.12／556.23
  ——逐日在不同板块指数间跳（首末差 10 倍）＝`anyLast` 任取一码的直接可见性；卡面声明的是"各周期截面 rank-pct 归一→主导度=argmax_i(rank_i)；
  连续面=0.2·rank_q3+0.3·rank_q5+0.5·rank_q20"。
- 两次的 `ev` 凭据面均如实记 `op: amount|anyLast_per_day`／`close|anyLast_per_day`＋完整 SQL 前缀 ⇒ 机器自证喂的是错面，非本席推测。

结论：**这两张若开考＝往永久分数册写两条"信号无/弱信息"的假陈述**（考的是随机板块的原始量价，不是卡面冻结的截面份额／主导度）。
与 ⑧B 席 top_n=20 撞 `ic_exam.py` 30 列地板致 `ic_stats([])` 交回 **0.0 而非 nan** 是同族病灶（仪器没测到却报数），不同层：那里是地板，这里是**绑定面**。

正解在册、非本席职权：模块内已有截面形算子 `op_sector_top_n_amount_share`（用 `SQL_SECTOR_TOP_N`＝`sumIf(amt, rk<=n)/nullIf(sum(amt),0)`）
与 `load_sector_family_panel`（`SQL_SECTOR_FAMILY_PANEL`，GROUP BY d,code＋anyLast 收版本行），
其 `:929` 注释自陈"族名单／映射表／周期／列名四要素**整表取自册 args**——本函数不写"。
而这两张卡面**无 `composite_join_rules` 块**，`_card_composite_pairs` 对该情形直接 `raise ValueError("composite_card_face_rules_absent（卡面无 composite_join_rules 块＝不许走复合口）")`。
⇒ 缺的是**卡面绑定申报位**（⑥制卡席）与**册格**（⑤/⑥），不是考工可以自造的东西——"考工自制册格＝自批"在 ⑧B 05 班已定性违甲案③，本席照此不越。

### 六、正对照：管道未失明，"0" 是面结论

- 全库申报本地序列的卡恰 **8 张**，状态 **8/8 全为 examined**、preregistered 面 **0 张**；`SERIES_DIR=docs/04_research_records/mining/ledgers/nightmine_20261010/series`
  exists=True、37 件在盘，申报名 `avg_abs_ret／avg_abs_ret_z20／lu_count／lu_count_z20／lu_ratio／lu_ratio_z20／mkt_fwd5／mkt_fwd10` 可解。
- 磁盘 examined 73（⑩ 06:12 记 55）＋分数册 rows 96 ⇒ 本班工具面能判出可绑类（D 路径在 examined 那 8 张上仍判得通）。
- ⇒ 本席"0 出分"不是"考工永远跑不了"（04 班两张真分即自物化跑的，⑧B 亦如此纠偏），而是**当前 preregistered 面的构成里没有一张能被现有执行器喂对口径**。

### 七、断供册避让纪律：面积≠阻断，两条在册缺口经实测判定"不挡本席候选"

- `rate_decision_calendar_jin10_retired`（status=**no_source**）：停更窗 2025-11-01..2026-09-18，
  而本席最久积压卡（10-09 20:25 十二张）OOS 窗逐字＝`2024-01-01..2025-09-09`（⑨席 13 班同值），**整窗在停更窗之前**；
  且该条 `primary_alternative` 自记"11 央行历史决议 2,386 行在库无损（1991/1970 起）"⇒ **不因该条拒考**。
- `kline_sector_880_resample_false_success`（status=**open**，表名正是两张 A 卡的 signal_table）：
  `impact` 逐字＝"15min/30min/60min 重采样行在 09-22 与 09-23 缺失；**日K腿无恙**"，两张卡走 `period='1d'` 且 IS/OOS 均早于 2026-09 ⇒ **不挡**。
- ⇒ 本席把这两条写清是防下一班拿"表名命中断供册"当拒考理由（⑧B 06 班"按表名级避让会白挡 8 张"同型，本族数字另立）。
- 断供册盘面：84 条，status 分布 completed 7／accepted 19／resolved 13／monitoring 5／**open 28**／mitigated 4／**no_source 7**／retired_quarantine 1。

### 八、堵点分账与路由（本席不自清、不代签、不改判据）

给 **⑤ 实现席**（117 张，占积压 68.4%）：执行器目标面硬绑 `_INDEX_TARGET_RE`（指数次日收益），
类 C 中 `engine_replay` 64 张需双臂/NAV 回放口、`panel_stock` 20 张需面板撮合口、`probability_hit` 3／`sector_series` 3／`other` 27。
⇒ 这是**执行器能力面缺口**，不是卡缺陷；不补齐则 preregistered 积压永远出不了分。
给 **⑥ 制卡席**：①两张类 A（L2-01-2/02、L2-01-3/02）缺 `composite_join_rules` 申报位 ⇒ 补了才走得通在册截面算子；
②13 张整块无 data_binding（含 10-09 20:25 十二张最久积压者多数）；
③A? 7 张逐卡：`normalization_recipe_undecided` 3 张（L2-01/comparison/02、L2-01/comparison/03、L2-04-1/calibration/02）＝归一配方未定，
`table_not_in_recipe_book` 4 张（L2-09/calibration/03→`c3_fundamental.research_report`；L9-A10/calibration/02→`c1_market.macro_data`；
L9-A15/calibration/02・/03→`c1_market.hl_funding_history`）＝表未入配方册，且三张表各自在册均有 open 缺口
（`research_report_hot_value_rating_change_empty`／`macro_data_eastmoney_ssl_eof_chronic`／`hl_liquidation_raw_empty`）⇒ 须与 ①席复测联判，勿先入册后补数。
给 **① 数据源席**：上列 4 张 A? 卡的表名与其 open 缺口一一对应，见⑦节判据（勿把"表名命中"当"必挡"）。
给 **⑩ 线长**：本班＝⑩ 席 ledger 第 58 行预告的"第三班"（"⑦⑧ 两班未开闸（examined 恒 55），若第三班仍零消费，
须把'考工席位无人发车'升级成呈批面而非再派同文配额"）。**第三席独立复量结论＝现器可考面 2 张、且 2 张口径错配不可考**。
与 10-12 在册档 `exam-card-pipeline-blockage-map` 的"现器可考=0 三证＋三条闸（面板形 39／目标面 118／供题）"同向；
本班 10-15 现值＝目标面闸 **117**（当日 118）、面板/持仓面闸 15+20＝35（当日 39）——**三天未变，属结构性而非当日抖动**。
另：SOP §3⑦⑧/§3-D 席位节补记 C 席归 ⑩，本席未代改。

### 九、本班自纠（四处，另起留旧案不改上文）

1. **首个普查脚本自报 preregistered=191 未复现**：19:05 三尺三测（grep／find／yaml 解析）同值 175，19:12 起 171。
   该 191 读数无法在任何尺上重现，**下一班勿引用**；本班不据此判事故（在册教训：勿把行数骤变当事故、0 命中/满命中都要对照）。
2. **第一版 route 尺取 `route:` 键，103 张全归空值**＝族盲尺（卡面真字段是 `family:`＋`signal_kind:`）；改键后加总恰＝175 才自证。
   与 ⑧B 06 班"拿单一 `_CALIBRATION_JUDGED_KEYS` 量 72 张属族盲"同型，本席首版比它更糟（直接全空）。
3. **data_binding 覆盖首版只扁平探一层**，误报 `derived_series/target_series` 在 examined 面也全 0，
   与"examined 有 8 张真分走双注入"当场矛盾；改按执行器真读路径 `card["data_binding"][...]` 重测，得 8/8 examined、0/175 preregistered。
4. **`GitCommitGateway.list_active` 不存在**（AttributeError：type object has no attribute）——本班未拿它当活性尺，
   改按会话册与四件套实面直查；在册教训"liveness 尺须与执行工具守卫同源"此处表现为**我记错了单口名**，勿照抄。

### 十、自检两轮

- 第一轮（only-add 未动旧行）：ledger 与 checkpoint 均以 Edit 追加/原地游标行改写，本席四件系本班新建（建册首班），
  不存在他人旧行；分数册 `exam_scores_v1.yaml` 本班 **plus=0／minus=0**（未写任何行）；卡面文件本班 plus=0／minus=0（未翻状态）。
  卡锁：本班未 claim 任何 exam_card（未开考即不占卡），仅 claim 自家四件（TTL 30 分，交账后即 release）。
- 第二轮（与门柱一致）：本班未跑任何判据、未读门柱出分⇒无"分数与门柱不一致"可能；
  判据/门柱/冻结值零改动、零新建卡、零翻态、零入册行、零改他席面；`断供` 与 `可达性` 结论全部带实测读数与文件行号，无凭记忆路径。
- 加总自证三处：五态 552＝文件总数；family×class 99+26+21+25=171＝类别普查加总＝preregistered 面；
  类 C 目标面分型 64+27+20+3+3=117＝拒因 `target_face_not_index_next_day` 计数。

### 十一、降级直改主区理由（RULE-WORKTREE 显式申请制留痕）

本班两件写入件系本岗 `_working` 活文档（新建席位台账／游标）＋席位 scope/instruction 两件，
**非施工件、不改判据面、不碰分数册、不翻卡状态**；与 ⑧B 06／05 班同型先例。
未建车道的原因＝产出全部为只读尺与自岗账，且落地链当日不健康（死信 315、⑩ 停发生产配额），建车道再合批只会增加三方冲突面。

## 10-15 20:06 · 班次 01 补记（同一班，另起留旧案、上文不改）＝本班两处结论被 ⑦A 席 06 班当场纠正＋袋态实报

**触发**：20:0x 读到 ⑦A 席班次 06（起手 18:10:12、写册 19:3x、实测 87 分）主产出＝**推翻前任"现器可考面=0"并已 8 张入册（0 pass／8 fail）**。
本补记优先于上文④⑤⑧节的相应结论；上文原样留着不涂（Owner 两轮追认过的更正法＝另起留旧案）。

### 一、被纠正的两处（逐字引 A 席在册原文，非本席转述）

1. 上文⑧节我把 117 张 `target_face_not_index_next_day` 判为"**执行器能力面缺口，不补齐则积压永远出不了分**"——**判重了**。
   真身＝**绑定层**只认指数次日面（`card_binding.py:330-338`），而 `signal_kind=panel` 的卡由考工自己灌面对象即可考；
   A 席原文＝"panel 且目标=个股次日 的卡 **24 张**，其中 **21 张被归 C、3 张归 B**；按卡面绑定逐张人读后**可考面 ≥8（本班烧尽 8 张）**"。
2. 上文⑤节我把两枚类 A 卡判为"缺卡面绑定申报位与 22 册格⇒考工不可自造"——**停在了错误的一步**。
   A 席正尺原文（ledger:242）＝"正确尺＝逐表面三件实测（①重复行数 ②有效码数≥30 ③目标面是否 1 日），
   **'卡面没写'绝不等于'跑不了'，也绝不等于'可以瞎跑'**"；且他们确实自己按卡面 `universe_rule` 原文直译造了宇宙掩码
   （前缀留 5,365 票／剔 279；窗内留 7,152,422 格）。⇒ 两枚 sector 卡的**正确动作＝本席按卡面逐字冻结式自物化截面份额／rank-pct 主导度后 run_card 注入**，
   而非把它们退回 ⑥。本班把"绑定层不给路"误读成"执行器没能力"，是把**自家工序**记在了别人账上（同 `lane-enqueue` 与 ⑧B"别把 class A/D=0 当考工永远跑不了"两次在册纠偏同型，我第三次踩）。

**仍然成立的部分（不被本次纠正覆盖）**：`build_signal` 类 A 路实跑出 `anyLast(amount|close) GROUP BY d`＝跨 729 板块码任取一码，
该结论只否定**自动绑定路**，不否定**考工自物化注入路**。卡1 len=1595／值 5.3e5..2.3e6／index 起 2020-03-17 越 IS 窗，与卡2 close 首 6594→末 556 逐日跳码，
仍是"下一班**勿走 --mode run 自动绑**、须走注入"的直接凭据。

### 二、本班剩余时间内为何仍未补跑这 2 张（不是省力，是两条硬约束）

- 时间：20:06 起距班期上限 20:20 仅≈14 分，而 A 席为同类 sector/panel 面付出 87 分（超 60 分班期，超支记因见其 §七）；
  本席若此刻起做截面份额物化＋五分位分桶＋regime 同号＋OOS 同号五柱，**必然落在"瞎跑"一侧**，正撞 A 席那句"绝不等于可以瞎跑"。
- 写册面：分数册当日是热件且**落地面未跟上盘面**——A 席原文"分数册照旧不随袋（index 仍是他班 **97 行**快照）"＋"分数册从未落 HEAD⇒开班必自带备份"。
  本席在 18:56 量到 rows=96，A 席 19:3x 已写到 97 行且其袋亦 landing 失败（"8 张卡面 status 仍 examined ⇒ 本次 landing 失败未洗掉本席交付"）
  ⇒ 在 14 分内追加分数行＝给他席在途快照再叠一个必撞"双侧皆改"的热件写面。**记堵点即停**，交下一班带备份做。

### 三、袋态实报（本班交付未落地，不自封已交付）

- 袋①`q-20261015-st-qoder-p07c-1015-01-0001`＝**dead**，dead_reason 逐字已读＝
  `ghost_session: 属主会话 … 已死（heartbeat=exited / 注册表无在册），自动重投被存活闸拒绝（裁定#459；CLI 手动 requeue 不受闸限，人工可强制）`
  ⇒ **本席未取人工强制杠杆**（不越闸）。
- 根因实测钉死（非猜）：`register(pid=0)` 的条目**活不过一次外来 `list_active` 收割**——
  19:36 注册→19:45 `mark_logical` 时 `get_session` 已 None；再注册（19:50）→19:55 守护首拍即
  `{"status":"exited","reason":"session not in registry"}` 且条目又查无＝
  在册坑 `examcard-wrong-dir-and-pid0-claim-reaped` 与 `save()=merge-upsert 永不删（删除只能走 unregister/**list_active 收割**）`两档互证。
  **正解实测＝守护进程用自己的活 PID 自注册后再进循环**（单进程内 `register(pid=os.getpid())`→`run_daemon`），
  三态核实通过：注册表 present=True 且 **pid=29748（活 PID 非 0）**／heartbeat 末三行 `status=alive` 30s 一拍／keepalive grant 在册（ttl 3600）。
  该形态下 `ENQUEUE-RENEW: claim 续租 **4/4** 件`（pid=0 那次是 **0/4**）＝pid 形态真被下游消费的旁证。
- 袋②`q-…-0002` 于 20:04 实测仍 **pending**（head 他袋 `q-20261015-st-qoder-p07-1015-06-0002` 在压），
  `git log -- 本席目录`＝**0**、`git show HEAD:…ledger.md`＝**0 行**⇒**未落地**；`landed_commits=0` 是唯一判据，入队回显不作数。
- 袋③＝本补记（严格超集：同四件仅 ledger 追加本节＋游标追加本段，纯 plus/minus=0），本班末投。
- 另记一处非本席事件：`git add` 当轮报 `fatal: Unable to create '.git/index.lock': File exists`＝并发他席 git 进程；
  按在册"主区 index.lock 不挡入袋只挡直连落地"复量 `staged=4` 后照投，未代拆锁未清他人锁。

### 四、给下一班 C 的改判（游标同步改，勿再按上文⑤⑧节的"退回⑥"领面）

- **本席真实可考面不是 2**：照 A 席 06 班口径，entry_flow 里 `panel＋个股次日` 那一层 24 张中 21 张归 C 只是**绑定层**拒，
  不是不能考；下一班第一动作＝**自带分数册备份**（A 席在册教训"分数册从未落 HEAD"）→
  按卡面 `universe_rule`／`signal_derivation` 逐字自物化面 → `run_card` 注入 → only-add 追加行。
- 两枚 sector 卡（L2-01-2/02・L2-01-3/02，10-10 08:20，积压 5 日）**改判为"可考、须注入"**，
  禁走 `--mode run` 自动绑（本班实测凭据在⑤节）；分母口径先跑 A 席三件实测（重复行数／有效码数≥30／目标面是否 1 日）。
- 上文⑧节给 ⑤ 的"117 张目标面口缺口"工单**降级为线索非结论**；给 ⑥ 的"补 composite_join_rules"仍有效但对这 2 张**不是前置条件**。
- 会话保活配方照③节实测形态抄：**守护自注册活 PID＋单进程进环**，勿再 `pid=0` 裸注册后指望条目活着。

### 五、补记之补记（20:09）：③节那条"活 PID 守护"处方**只成立约 9 分钟**，勿当已验证配方继承

实测追证（`tasklist //FI "PID eq 29748"`＝无匹配；heartbeat 末条 `{"ts":"...12:05:06...","pid":29748,"status":"alive"}` 后即断，
下一条是 pid 58484 的 `exited / reason="session not in registry"`；20:08:56 复量 `get_session` present=**False**）：

- 三态曾在 19:57 全绿（在册 True＋活 PID＋heartbeat alive），**但守护进程本身于≈20:05 静默消失**（无 traceback、nohup 壳不留痕），
  条目随之被外来 `list_active` 收割 ⇒ 第三袋预检再次 **SESSION-REQUIRED**（20:07／20:08 两次同因，均"1 项违规一次给全"、锁外白烧已避免）。
- ⇒ ③节末句应读作"**必要条件**而非充分条件"：主区无车道形态下，会话活性靠一个本机长驻进程撑着，而本机长批进程会静默消失
  （同在册 `long-batch-collector-must-flush-per-block`）。**充分解不在本席职权**＝要么走 `session_worktree_start` 车道（daemon 由 worktree 锚定），
  要么由 ⑩/统筹改存活闸判据（⑨席 14 班原文同结论："恒定班要保袋须跨班 keeper 或 ⑩/统筹改存活闸判据，非本席职权"）。
- 本班据此**不再无限重试**：最后一次尝试＝同一命令串内"注册→立即 enqueue"（不给收割留窗口）；投得进与否都就此收班，
  四件字节在盘＋暂存面双存证（`git diff --cached` 4 件），不丢。下一班续投前先读 dead_reason 再定（不盲重推死袋）。
- 纪律复核：本席**未**取 CLI 手动 requeue 人工强制杠杆、**未**代拆他人 index.lock、**未**自清他会话 claim、
  未动判据/门柱/冻结值、未翻任何卡状态、未写分数册一行；袋在飞故本班 claim **未释放**（在册"袋在飞禁放锁"）。


## ⑦考工C 班次 1016-01（st-qoder-p07c-1016-01）｜出分 2 张（均 fail）｜保底 2＜8 未达・超 90 分班限（实耗≈96 分）如实呈报

### 一、分母实测（date 现测 14:20:11 起手・以磁盘面为准）

- 卡池 553 件＝entry_flow 402／exit_flow 51／portfolio_flow 37／position_flow 63。五态加总自证：
  preregistered **167**／empty 186／examined 81／blocked_on_data 71／blocked_on_impl 48 ＝ 553 ✓（与 ⑩1016-19 班 13:39 的 167 同值＝停发解除后当日尚无新翻卡）。
- prereg 面 `classify_card` 逐卡 n=167 加总自证：**C 116／U 27／B 15／A? 7／A 2／D 0** ⇒ 自动绑定层可绑面仍＝2（与 10-15 首班同值，三个班未动）。
- flow×class：entry 95（U26/A2/A?7/B14/C46）・exit 26（C24/B1/U1）・portfolio 21（全 C）・position 25（全 C）。
- C 面目标分型：engine_replay 64／other 27／panel_stock 16／sector_series 3／probability_hit 3／无标注 3 ＝ 116（上班 117→本班 116，差值枚系 panel_stock 20→16 与 U/B 面各动一枚，非本班动作）。

### 二、本班出分两张（panel 注入路・`run_card` 正卷・卡面已自翻 examined）

| 卡 | verdict | ic_mean | ic_ir | oos_ic | regime(bull/bear) | n | 分数行 |
|---|---|---|---|---|---|---|---|
| TDM-E-L3-12-3/calibration/02_获利盘占比 | fail | 0.0094 | 0.0693 | 0.0063 | 0.0155／0.0123 | 1620 | rows[104] |
| TDM-E-L3-03-2/calibration/02_均线多排 | fail | -0.0104 | -0.0822 | -0.0090 | -0.0176／-0.0012 | 1519 | rows[105] |

- 判据面读数：两卡均 `ic_mean < 0.02` 且 `ic_ir < 0.3` 双柱记败；获利盘卡 IC 与 OOS、两段 regime 同号为正（弱正信息、不过地板），均线多排卡全面对齐为负（该冻结式在此宇宙上是反向信号）。
- 前置闸 G1-G4（⑦A 席在册自设数据充分性面，非门柱、未动 pillars）两卡全过：ic_days 1620／1519，日均有效名数 4476.6／4149.3，ic_std 0.1358／0.1270，oos 非 NaN。dry 先落 tmp 册验形状，再落真册。

### 三、口径出处与写面自证（零自创，逐条对卡面）

- 供数装载＝复用 ⑦A 席在册宽面板口 `load_column`（同 argMax(ingest_ts) 去重语义＋parquet 缓存），technical_indicator 均线族命中其既有缓存、chips_winner/conc_90 现拉（首拉 45.7 分含 8 年分块）。
- 目标面 `stock_fwd_ret_t1o_to_t2c`＝close.shift(-1)/open−1，执行器 `_panel_metrics` 内部 shift(-1) ⇒ t 日对位 T+1 开→T+2 收（与 A 席 1015-06 班同一冻结面，非本班新造）。
- 宇宙＝L3-03-2/02 卡面原文"读取须按宇宙重建源过滤（该表含 14,357 个非个股符号）"⇒ 仅留个股前缀 60/00/30/68；L3-12-3/02 与它同源（technical_indicator 同表）故同过滤，其自身卡面未再声明宇宙；两卡卡面**均未申报** ST／上市年龄剔除 ⇒ **未套** A 席 V1 掩码（套了＝把未申报口径写进永久分数册）。
- 取值域首跑实证：chips_winner ∈ [0,1]（卡面明令"首跑以分布实证并写死换算"）⇒ 不乘 100；conc_90 ∈ [0, 98.0]。
- 联合分／复合分位＝卡面逐字：获利盘联合分＝截面秩分位(chips_winner) × (1 − 截面秩分位(conc_90))；均线多排计数＝[ma5>ma10]+[ma10>ma20]+[ma20>ma60]，趋势分位＝计数与 (close/ma20−1) 两列截面分位的等权复合。
- 分数册 only-add 三面自证：写前 sha16 `21ce93c0a55c450e`（104 行）→ `7b79f81eb9f0b17f`（105 行，+988B）→ `05bc7ce014f204a0`（106 行，+939B），两次 `new.startswith(old)` 均 True。
- GPU：本班未 acquire 看门人，未点名 device_ledger ⇒ 收班⑥ 如实免执行，且本班两行分数不申报为 GPU 读数。

### 四、堵点与转单（不开考的面，逐条给因）

- **全班唯二 class A 可绑面＝两张 sector series 卡（L2-01-2/02・L2-01-3/02，积压 6 日）本班仍不开考**：卡面 `signal_derivation` 的 series 面写的是**响应变量式**（"占比前 10% 板块等权组合的次日超额"与全样本差），不是 t 日可算的 PIT 信号式；同卡面另给 5 日环比式读法，两读法不可由卡面裁决 ⇒ 择一入册＝往永久分数册写未冻结口径（承本席 10-15 首班在册结论，非本班省力）。
  供数面已实测可达（非断供）：c1_market.kline_sector_880 period='1d' 804,110 行／max trade_date 2026-10-15，sector_code_name_map code_family 在册映射 industry_l1 61＋industry_ths 128 ⇒ 转 ⑥ 补 signal 侧申报位后本席下即可考；本席不自制 22 册格（＝自批）。
- L3-03-2/03 温和放量卡已占卡未开考＝班限已到（14:20 起手→15:5x），非口径堵点；其"温和带命中二值与截面分位（爆量惩罚取负构造）"的带界与合成序仍需 ⑥/⑤ 认定，下班带此条再判。

### 五、[BLOCKER] 登记（本班 6 枚：中 4／低 2・需Owner 1）

- [BLOCKER] 2026-10-16|⑦c席1016-01|工具缺陷|考工占卡锁 TTL 30 分远短于班限 90 分，CH 宽面板首拉窗（45.7 分）内三把卡锁全部静默过期，收班 release 三面同读"未被锁定"且全程零告警面|docs/03_modules/_domain_backtest/exam_cards/entry_flow/L3/TDM-E-L3-03-2__calibration__03_温和放量.yaml 与 scripts/lock_files.py list 现值 p07c 命中 0|⑤席定"考工席 claim TTL≥班限"或给长拉数窗自动续租钩子|中
- [BLOCKER] 2026-10-16|⑦c席1016-01|判据缺失|panel 路 mono_spearman 恒 None 而卡面冻 mono_spearman_min=0.6，两行分数 unjudged 面自述"panel 路恒 None／分桶样本不足 NaN"＝响应单调柱从未被评估|scripts/backtest/fexam/calibration_exam.py 内 _panel_metrics 返回面 mono_spearman 置 None 一行|⑤席补 panel 路分桶单调面，或 ⑩判该柱对 panel 卡豁免并写进词表|中
- [BLOCKER] 2026-10-16|⑦c席1016-01|判据缺失|前置闸 G2 只量日均有效名数（4476.6／4149.3）而 min_names_per_day 实测 0（IS 起点前空窗）＝日均尺挡不住头部空窗仍能入册|.runtime/tmp/p07c_1016_01/shift_dry.json 与 shift_real.json 两面 measured 字段|⑤席判 G2 是否须加逐日地板腿；本席未自改闸|低
- [BLOCKER] 2026-10-16|⑦c席1016-01|流程问题|全班唯二可绑面（两张 sector series 卡）卡面 series 面写响应式不写 t 日信号式，两读法不可裁决⇒本席不开考并转单|docs/03_modules/_domain_backtest/exam_cards/entry_flow/L2/TDM-E-L2-01-2__calibration__02_板块成交额占比活跃度.yaml 的 data_binding.signal_derivation 字段|⑥席补 signal 侧申报位（考工自制册格＝自批，勿越）|中
- [BLOCKER] 2026-10-16|⑦c席1016-01|工具缺陷|本岗唯一宽面板装载口系他席临时件（.runtime/tmp/p07/shift06_panel_materialize.py，头注 TTL task_bound 24h 名义已过期），本班复用其 load_column 与均线缓存|.runtime/tmp/p07/shift06_panel_materialize.py 与 shift06_ma5/ma10/ma20/ma60.parquet|⑤/⑩判是否收编为正式装载件；收编后本席下班改读正式口|中
- [BLOCKER] 2026-10-16|⑦c席1016-01|需Owner|保底口径与班限互斥：指令卡"每班≥8 张出分或跑满 4 小时"对 90 分恒定班不可同时满足（实测单张 panel 卡含 CH 宽面板首拉 45.7 分＋真跑 20.3 分），且 167 张积压里自动可绑面仅 2 张＝供题形状结构性问题非本席省力|docs/01_policies_and_standards/sop/automation_sop/research_production_line_policy.md 三-A 节扩席条款与 ⑦⑧ 席位节（C 席至今未列）|⑩改判考工席保底口径，或 ⑥/⑤ 补目标面口后本席自解；Owner 知会|中

### 六、收班八件（本班终态）

1. **release 全部 claim**＝三张卡锁均已于 15:0x 自然过期（现值 list 面 p07c 命中 0），本席自家四件与两卡、分数册随袋由正门 finally 释放；见 BLOCKER 1（静默过期族已立案）。
2. **注销心跳**＝守护 pid 43804（本席 keeper 单进程自注册活 PID 形态，14:27 起环）按 PID 核活后终止，再复证 pid 不存在＋心跳末行 exited；未按镜像名批杀。
3. **实耗**＝起手 14:20:11 → 真跑落册 15:5x ≈ **96 分**（超班限 6 分，超因＝CH 首拉 45.7 分未被预估，非返工）；例行取证≈12 分・拉数≈46 分・判分≈21 分・写作投袋≈余量。
4. **[BLOCKER]**＝6 枚（中 4／低 2，含需Owner 1）；写后现测两把尺同框＝严式 `grep -c "^- \[BLOCKER\] 2026-10-16|⑦c席1016-01"` **6**、宽式 `grep -c "\[BLOCKER\]"` **8**（宽式多出的 2 处＝本节标题与本行两处叙述体命中，非登记行；⑩对账请用严式或"行含 BLOCKER 且含日期"谓词，本席席位段新立为 `⑦c席1016-NN`）。
5. **自清**＝`.runtime/tmp/p07c_1016_01/` 本班临时件（脚本 4＋json 4＋dry 册 2＋备份 1）在投袋后清单如实保留（缓存 p07c_ti_*/p07c_hfq_* 落在 ⑦A 席 tmp 目录内，非本席件面，如实归位呈报不代删）；四件套外零散落；主区根零临时件。
6. **GPU 还牌**＝未 acquire 看门人 ⇒ 免执行，读数不申报为 GPU。
7. **后台子任务清点**＝零 spawn 子代理；本班唯一长驻进程＝本席心跳守护 pid 43804，收班按 PID 终止并复证 ⇒ 零孤儿。
8. **零 worktree 确认**＝本班未调用任何工棚/工作树入口、未建任何 worktree（TRAE-079 Phase 2 遵令），全程主区＋claim 互斥作业；发现的历史遗留 `.worktrees/` 与本岗无关件一枚未动，整批交清理专班。

### 七、下班（⑦c 1016-02）首查四件

① 本班袋是否落地（只认 git log 与 blob 内容级，勿信盘面自述）；② ⑥ 是否已补两张 sector 卡的 signal 申报位（补后即考，供数面本班已实测可达）；③ mono_spearman panel 面是否已由 ⑤ 补齐（补齐前本班两行的"未判柱"注记须保留勿涂）；④ 卡池 prereg 是否仍 167（若 A/B 席当日推进则改按新分母领面，勿沿旧数）。

## ⑦考工C 班次 1016-02（st-qoder-p07c-1016-02）｜起手 21:50:15・出分 2 张（SHC/UNL，均 fail）・本班第一段收口

### 一、分母实测与上一班交班四查（date 现测，磁盘面为准）

- 卡池 553 件（entry 402／exit 51／portfolio 37／position 63）；磁盘面六态加总自证：
  empty 186／preregistered **163**／examined **83**／blocked_on_data 71／blocked_on_impl 48／examining **2**＝553 ✓。
  上班（1016-01・14:20）读数 prereg 167／examined 81／examining 0 ⇒ 当日 A/B 席确有推进（−4 prereg／+2 examined／+2 examining）。
- 现值 examining 两张＝`L3/TDM-E-L3-03-2__calibration__03_温和放量`・`L3/TDM-E-L3-05__calibration__02_连板顺位`，
  mtime 18:38 系 ⑦A 席在途（其 tmp 内 dry01 两件 18:37 在册），本席**未碰**该两把卡。
- 交班四查逐条回批（上班台账 §七）：① 上班袋**已落地**＝`git log -- 本席目录` 首条 98410ca45f；
  ② ⑥ **未补**两张 sector 卡 signal 申报位＝两卡 mtime 仍 10-10 08:20、grep composite_join_rules 零命中、status 仍 preregistered ⇒ 继续转单（本班零动作）；
  ③ ⑤ **未补** panel 路 mono_spearman 面＝本班两行 unjudged 仍自述"panel 路恒 None／分桶样本不足 NaN"（旧案卷不涂）；
  ④ prereg **已非 167**＝现值 163，本班按新分母领面。
- 积压最久面实测（mtime 从旧到新）：10-09 20:25 批 12 张全在 entry/L1（其中 4 张本班抽读 `data_binding` 整块缺位＝
  与 10-15 在册"13 张整块无 data_binding"同族，非本班新堵），10-10 08:14 批为 exit_flow 对照/消融族（需撮合与双臂引擎）。
  ⇒ 本班领面按"卡面给出 t 日可算式＋供数在册可达"两条件取 panel 注入路，落在 10-10 08:35 批（积压 6 日）。

### 二、本班第一段出分两张（panel 注入路・`run_card` 正卷・执行器自翻 examined）

| 卡 | verdict | ic_mean | ic_ir | oos_ic | regime(bull/bear) | n | 分数行 |
|---|---|---|---|---|---|---|---|
| TDM-E-L3-12-3/calibration/03_股东户数集中度 | fail | 0.0079 | 0.1840 | 0.0106 | 0.0073／0.0079 | 1620 | rows[106] |
| TDM-E-L3-04/calibration/02_解禁否决 | fail | 0.0097 | 0.3393 | 0.0099 | 0.0053／0.0143 | 1620 | rows[107] |

- 判据面读数：户数集中卡 `ic_mean<0.02` ＋ `ic_ir<0.3` 双柱记败（IC/OOS/两段 regime 同号为正＝弱正信息不过地板）；
  解禁否决卡**只输 `ic_mean`**（ic_ir 0.339 过 0.3 柱，oos/regime 三段同号为正）＝该冻结式方向与卡面负向假说一致
  （signal=−1×解禁比例分位 ⇒ 分数越高＝解禁压力越小＝后视收益越高），但幅度不到地板，非读数噪声。
- 口径出处零自创：两卡 `data_binding.signal_derivation`/`universe_rule`/`target_source` 逐字实现（户数比取
  `ln(hc_t/hc_prev)` 按 announce_date 严格 <=T 的最近已公告期前视禁填充；解禁档＝未来 20 个交易日内**最近一次**解禁的
  ratio 截面分位、无解禁=0 档；目标面＝卡面 primary `stock_fwd_ret_t1o_to_t2c`＝close.shift(-1)/open−1，
  执行器内部再 shift(-1) ⇒ t 日对位 T+1 开→T+2 收，与本席 1016-01 班同一冻结面）。
- 宇宙＝两卡卡面 `data_binding.universe_rule` 写死块（前缀 60/00/30/68＋ST 取 `stk_limit.st_flag`＋上市满 60 交易日）
  ⇒ 复用 ⑦A 席在册掩码缓存 `shift06_mask.parquet`（同谓词非本班新造；1016-01 那两卡卡面未申报 ST/年龄故当时未套，本班两卡**已申报**故套＝按卡面而非按偏好）。
- 供数实测（开考前现量，不引用卡面 evidence 当读数）：`c3_fundamental.shareholder_count` announce_date<=2025-09-09 且
  holder_count>0 ⇒ 457,054 行／事件 392,160 条／(symbol,end_date) 唯一性实测 458,277=458,277（无版本重复，无需 argMax）；
  `c3_fundamental.share_unlock` ⇒ 26,997 行（argMax(ratio,ingest_ts) 去重后）／事件落位后在窗保留格 312,791。
- 分数册 only-add 三面自证：写前 sha16 `05bc7ce014f204a0`（106 行・141,704B＝上班班末终值，本班起手自带备份
  `register_backup_head.bin` 与之逐字节相等）→ `9185e03c374be980`（107 行・+940B）→ `bb557705beea260f`（108 行・+866B），
  两次 `new.startswith(old)` 均 True，读回 rows[106]/[107] 的 card_id／run_id／date 与卡面 lineage 双向对得上。
- 前置闸 G1-G5 两卡全过（ic_days 1620／日均有效名数 4316.2・4143.6／signal_spread_day_frac 1.0・0.9994／oos 非 NaN）。
  **G5 为本班新加的自设数据充分性面（非门柱、未动 pillars_numeric）**，立案缘由见 §四 BLOCKER-3（退化读数差点入册）。
- GPU：本班第一段未 acquire 看门人 ⇒ 收班⑥ 如实免执行，两行分数不申报为 GPU 读数。

### 三、[BLOCKER] 登记（本班第一段 3 枚：高 1／中 2）

- [BLOCKER] 2026-10-16|⑦c席1016-02|流程问题|指令卡"占卡三步"（acquire→翻 status=examining→才开跑）与执行器状态闸互斥：run_card 只认 preregistered（`force` 的在册语义＝重考已出分卡），本席把 SHC 卡翻 examining 后 run_card 直接抛"卡状态非 preregistered"；本班正解取"回翻 preregistered＋靠卡锁互斥＋由执行器自翻 examined"，未滥用重考旗|scripts/backtest/fexam/calibration_exam.py:979-980 与 :1113-1114；.runtime/tmp/p07c_1016_02/flip.py 两面读数（examining→preregistered changed_lines=2）|⑩改占卡协议措辞或 ⑤给执行器加"examining 视同 preregistered 首考"分支|中
- [BLOCKER] 2026-10-16|⑦c席1016-02|工具缺陷|心跳守护进程被 reaper 收割后本席卡锁遭外来清理静默释放：21:52 起 keeper（cmdline=`python .runtime/tmp/p07c_1016_02/keeper.py`）22:05 实测进程不存在且 `.runtime/locks` 无自家 heartbeat 文件，21:56 acquire 的 SHC 卡锁 22:02/22:11 两读均"未被锁定"（TTL 30 分未到期＝非自然过期）；在册白名单只有裸子串 `heartbeat_daemon`，考工席 keeper 形态不匹配|data/runtime/process_reaper_keep.txt 现值（本班已追加 `.runtime/tmp/p07c_1016_02` 与 `st-qoder-p07c-1016-02` 两行，416 行＝追加前后键集合差自证）＋lock_files.py list p07c-1016-02 命中 0|⑤/运行班判 keeper cmdline 是否收进默认白名单（本席只登记自家子串，未扩面）；⑩知会各考工席开工即登记 keep 行|高
- [BLOCKER] 2026-10-16|⑦c席1016-02|判据缺失|在册前置闸 G2（日均有效名数≥100）对"全同值信号"失明：UNL 卡装载方向写错时保留格 0，6,743,477 格全是同一个 0 值，G1-G4 四绿且 dry 行照出 ic_mean 4.58e-17／ic_std 0.0＝退化读数差一步进永久分数册；本席当场自设 G5（signal_spread_day_frac≥0.5，逐日截面 std>0 的天占比）拦下并改正 `bfill` 方向|\.runtime/tmp/p07c_1016_02/shift_dry.json 两版读数对照（首版 cells_kept 0／spread 0.0／ic_std 0.0 ⇒ 修后 312791／0.9994／0.028682）|⑤判"信号非全同值"是否收进在册前置闸面（本席未动门柱与 pillars）；收编前各席自设 G5 只能算席侧临时面|中
### 四、本班第二段＝一张开考未遂并转单（L9-A06/02 主力净流入截面）

- 领面动作：22:13 acquire 该卡锁成功（29.9m TTL），卡面保持 preregistered（未翻态、未越闸）。
- 供数装载**已完成并缓存在册**（可复用，非堵点）：`c1_market.money_flow` 2021-01-04..2025-09-09 分年块
  argMax(ingest_ts) 去重取 main_net_inflow_pct＋pct_change 两面 ⇒ 实测 5,509,521 行 = 5,509,521 唯一 (trade_date,symbol)
  （零版本重复），前缀分解 00=1,565／30=1,414／60=1,766／68=591／**92=199（北交所，本班按与目标面对齐的最小过滤显式排除）**；
  缓存件 `.runtime/tmp/p07c_1016_02/mf_mnp.parquet`（32,007,191B）・`mf_pc.parquet`（2,743,763B），2021..2025 五块合计 49 秒。
- 崩点＝**执行器在判分前死在卡面 regimes 的散文条目**（非缺数据、非形状不配、非本席装载）：
  `_panel_metrics → _in_spans` 对 `window.regimes` 逐键 `pd.Timestamp(...)`，而本卡 regimes 除两段真 span 外还混入
  `bull_note`＝"2019-2021H1 牛段 money_flow 无数据（起 2021-01-04）⇒ 本卡 regime 用熊/修复两段替代…"（卡面自述性披露，
  不是窗口）⇒ `pandas._libs.tslibs.parsing.DateParseError: Unknown datetime string format`，22:15:48 实测整腿终止，
  **零分数行、卡面零触碰**（本班未改卡面一字：regimes 属冻结出题面，改＝考工自批）。
- 同签名面普查（本班新立的机判谓词，只读）：全池 553 件中**有 `window.regimes` 者 369 件**，其中**含非 span 条目者 39 件**
  ＝preregistered **14**／blocked_on_data 17／blocked_on_impl 8。谓词＝`window.regimes` 的每个 value 须匹配
  `^\d{4}-\d{2}-\d{2}\.\.\d{4}-\d{2}-\d{2}`，不匹配即计入。14 枚 prereg 具名（键名括注）：
  L3-11-1/calibration/03（single_state）・L3-11-2/calibration/03（single_state）・L9-A06/calibration/02（bull_note）・
  L9-A10/calibration/02（bull_note）・L9-A11/calibration/02（bull_note）・L9-A15/calibration/02（bull_note）・
  L9-A15/calibration/03（unavailable）・L9-V3/ablation/02（bull_note）・exit S1-04/comparison/05（bull_note）・
  exit S2-02/calibration/03（ipo_regime_note）・position P2-01/comparison/02（bull,bear 值为枚举名非日期串）・
  position P2-03/comparison/02（同）・position P2/comparison/02（同）・position P3-01/comparison/03（同）。
- 转单路由：**⑥ 制卡席**＝把 14 枚 prereg 卡的 regimes 散文条目移出窗口映射（或 ⑤ 给 `_in_spans` 加"非 span 条目跳过＋计数留痕"容错，
  但那是执行器面不是考工面）；**本席**＝两列缓存与目标口径（next_day_stock_return＝传入滞后一日 hfq 日收益面，
  执行器 shift(-1) 后＝close(t+1)/close(t)−1）已在册，卡面一修即可考，预计零拉数。
- 本班未做的第三件（如实，自带承重证据）：`L3-03/ablation/02_双池代理合成`・`L3-07-2/ablation/02_IC加权对等权` 两张
  仍在 prereg 且卡面给出 t 日可算式，但各需新拉 `stk_limit.limit_up`（9.25M 行级）与 `technical_indicator.atr_14` 两把宽面板
  ＋合成式（0.5/0.5 与 0.4/0.3/0.3 权重、60 日涨停次数滚动计数、过去 60 日半衰 IC 加权）逐字实现；
  22:20 实测本班剩余 ≈60 分，扣除投袋与收班八件（上班实测 15–20 分）不足 40 分，
  而本班第一段刚出过一次"装载方向写反＝6,743,477 格全同值"的退化读数（见 §三 BLOCKER-3），
  在班限尾追新复合式＝拿永久分数册赌时间，本席判**不做**，逐件移交下班（首查序：先复量 mf 两缓存是否仍在，再拉新面）。
### 五、[BLOCKER] 追加（本班第二段 1 枚・高）

- [BLOCKER] 2026-10-16|⑦c席1016-02|工具缺陷|执行器 regime 分段对卡面 `window.regimes` 的非 span 条目零容错，直接 DateParseError 终止整条开考腿：L9-A06/02 卡面 regimes 除 bear/recovery 两真 span 外混入 `bull_note` 散文披露，`_panel_metrics→_in_spans` 逐键 `pd.Timestamp()` 崩于 22:15:48，零分数行零翻卡；本班新立机判谓词普查＝有 regimes 者 369 件・含非 span 条目者 39 件（prereg 14／blocked_on_data 17／blocked_on_impl 8），14 枚 prereg 已逐件具名|scripts/backtest/fexam/calibration_exam.py:251-259（`_panel_metrics` 内 `for name, span in regimes.items(): _in_spans(...)`）＋docs/03_modules/_domain_backtest/exam_cards/entry_flow/L9/TDM-E-L9-A06__calibration__02_主力净流入截面.yaml 的 window.regimes.bull_note＋本班台账 §四 具名清单|⑥席把 14 枚 prereg 卡的散文条目移出 regimes（或 ⑤席给 _in_spans 加"非 span 条目跳过＋计数留痕"容错并配负对照）；两列供数缓存已在册，卡面一修即可考|高
### 六、本班自纠（§三 BLOCKER-2 归因未成立，另起留旧案卷，原文不涂）

- 上文 §三 第 2 枚把"三把卡锁 6 分钟内消失"归因为"心跳守护被收割后遭外来清理静默释放"。**归因半句作废，事实半句保留**：
  事实面两条各自实测为真＝① 首班 keeper（pid 37316，21:52 起）于 22:05 实测进程不存在且 `.runtime/locks` 无自家 heartbeat 文件
  （本班已按冷启动条款在 `data/runtime/process_reaper_keep.txt` 追加自家两行并按在册配方重启 keeper，22:19:57 复测
  pid 22976 存活・heartbeat_age 12.4s）；② SHC・UNL・MF 三把卡锁均在 `release` 面读"未被锁定"（22:11／22:19 两次）。
- 反证＝**外来清理未动手**：`grep "p07c-1016-02" .ailocks/salvage_audit.jsonl` 三条全为
  `action=salvage-skip・dead_confirmed=false・evidence1=registry:alive・released_locks=[]`，时间戳 22:00:15／22:10:18／22:15:31，
  且三条同记 `evidence2=claims:none`（＝该三点上本席名下 claim 已为零，非该工具所删）。
- 机制本席**不下结论**，两条候选如实标注未验：（a）卡文件被改写后锁记录失效（SHC 系本席 CAS 翻面后消失、UNL 系执行器
  :1118 `Path(card_path).write_text` 改写后消失；**MF 全程零写入却同样消失＝该候选不自洽**）；
  （b）外来 `lock_files.py cleanup` 按 acquiring 进程 PID 判死（本席 acquire 用短命 CLI 进程，PID 即退）。
  转 ⑤/运行班定论；在下述结论出来前，各考工席**不可把"acquire 成功"当作整班互斥凭据**，领面须按卡面 status 复量。
- 本节不改判据、不动门柱、不新增豁免；§三 原行的严重度（高）保留，因"互斥凭据不可信"这一后果面仍成立。
### 七、收班八件（22:28 现测读数，逐件给证据）

1. **release 全部 claim**＝本席名下 `.ailocks` 锁面现测 **0 把**（`lock_files.py list | grep -c p07c-1016-02`＝0；
   三把卡锁各自在 22:11／22:19 的 release 面已读"未被锁定"，机制与反证见 §六）；
   投袋时 `ENQUEUE-RENEW: claim 续租 0/5 件` 与该读数同框自洽（＝入袋时本席名下已无 claim，非续租失败）。
2. **注销心跳＝本班未按②执行，如实呈报并带承重证据**：袋 `q-20261016-st-qoder-p07c-1016-02-0001` 22:27:41 现测 `state=pending`，
   队列 head 系他班 `q-20261016-st-diskp0-20261015-0082`（300 件・已等 1409 秒），`daemon.online=false`；
   在册先例＝`data/runtime/process_reaper_keep.txt` 第 43 行"袋落地期间 keeper 必须在岗"＋本席 10-15 首班 ghost_session 袋死实证。
   ⇒ 本席 keeper（单进程自注册活 PID 形态，pid **22976**，22:19:57 复测 alive＋heartbeat_age 12.4s，
   `.runtime/locks/heartbeat_st-qoder-p07c-1016-02.pid` 22:26 mtime）**留岗不终止**，交下班按 PID 精确核活后销（禁按镜像名批杀）。
   该与收班② 的互斥面已登 §八 BLOCKER-5，判措辞权在 ⑩。
3. **实耗**＝起手 21:50:15 → 22:28 现测 `date`＝**38 分**（例行取证≈10 分・CH 拉数≈9 分・判分含两次返工≈11 分・
   写作投袋≈8 分）；**未跑满班限 90 分即收**，停因＝注入路可考面复量为零（见游标①）＋第三件自带承重证据（台账 §五末条），非缺时。
   两把尺同框：出分 2＜保底 8，实耗 38＜4 小时 ⇒ **保底双口径均未达，如实呈报**（承 1016-01 在册需Owner 条，不重复立案）。
4. **[BLOCKER]**＝本班累计 5 枚（§三 3＋§四/§五 1＋本节新增 1，见 §八）；严式尺现测见 §八写后读数。
5. **自清收口**＝`.runtime/tmp/p07c_1016_02/` 现测 22 件／42M：保留件＝两把供数缓存
   （`mf_mnp.parquet` 32,007,191B・`mf_pc.parquet` 2,743,763B）＋`shc_delta_wide.parquet`・`unl_nearest_wide.parquet`
   （游标§四已点名为下班零拉数资产，删＝让下班重烧 CH）＋分数册两面备份＋本班脚本与案卷；
   已删＝`dry_*.yaml`・`dry_scores_*.yaml`（验形状件）与 `__pycache__`（22:28 当场删，见下）。
   四件套外零散落；项目根零临时件；`git status` 本席写面全部已入袋（5 件，无遗漏面）。
6. **GPU 还牌确认**＝本班未 acquire 看门人 ⇒ 免执行；本班两行分数不申报为 GPU 读数（device_ledger 零本席条目）。
7. **后台子任务清点**＝零 spawn 子代理；本班唯一长驻进程＝keeper pid 22976（按② 判定留岗，非孤儿，归属与销法已写明）。
8. **零 worktree 确认**＝`ls .worktrees/ | grep -c p07c`＝0；本班未调用任何工棚/工作树入口（TRAE-079 Phase 2 遵令），
   全程主区＋pathspec 提交；发现的历史遗留 `.worktrees/` 与本岗无关件一枚未动，整批交清理专班。

### 八、[BLOCKER] 追加（收班级 1 枚・中）

- [BLOCKER] 2026-10-16|⑦c席1016-02|流程问题|收班八件②"注销心跳"与"在途袋需会话存活"互斥：本班袋 22:27:41 实测 state=pending、队列 head 为他班 300 件已等 1409 秒、daemon.online=false，按②即销 keeper＝把袋推进 ghost_session 死族（10-15 本席在册袋死实证＋keep 名册第 43 行"袋落地期间 keeper 必须在岗"）；本席选择留岗并交下班按 PID 22976 销，属自裁偏离指令面，须 ⑩ 定性|data/runtime/process_reaper_keep.txt:43＋commit_queue.py status --session st-qoder-p07c-1016-02 现值（pending 1・drain-active）＋.runtime/locks/heartbeat_st-qoder-p07c-1016-02.pid|⑩判措辞＝"存在本席在途袋时收班② 延后到袋终态，且必须登记 PID 与销法交下一班"；本席不改指令面|中

### 九、字面串预防改写（22:34 现测，另起留旧案卷）

- 本班自查 [CHIEF-1016-3]⑤ 时发现自家三处写有"双划 force 旗"的**字面原文**（§三 BLOCKER 流程问题行・游标⑤纪律①・msg 件），
  而 `gate-detect-git-dangerous` 对"引用型字面串与该门互斥"在案先例＝⑩席 1016-01 班自家两枚袋死（其台账自述病根同签名）。
  本班正对照失败＝近 40 笔落地 commit message 与 HEAD 面本台账内该字面串均 **0 命中**＝拿不到"该串能过门"的证据。
- 处置取最小面＝**改写为指称**（"重考旗／force 逃生位"），不新增加标、不弱化门、不白名单（循 ⑩ 在册正解）；
  袋①快照（22:26:48 入队）仍含旧字面串且 message 已固化不可改 ⇒ 若 drain 判死，先读 `dead_reason` 对症，再以袋②（本改写版＋严格超集）重投，禁盲重投。
### 十、袋②投出后机生读数一行（本行为袋② 快照之后的尾巴行，由下班袋承接落地＝本班不自投第三袋，避加队列压）

- 22:34:15 实测：袋② `q-20261016-st-qoder-p07c-1016-02-0002`（5 件）ENQUEUED 成功，同时打印
  `[compaction] qid=q-20261016-st-qoder-p07c-1016-02-0001 共享注册表路径不可信合并——拒绝压缩，两袋保留`
  ⇒ **同会话前后两袋不会被合并，两袋都将各自 drain**；本席盘面终值＝袋② 内容＋本行。
  风险如实预告＝袋① 先落地后，袋② 对同五件可能与基面判"双侧皆改"而死（＝本班指令卡开工前必读节点名的 83 枚死因族）；
  若死，正解＝下班读 `dead_reason` 后按盘现字节另投一袋（盘＝权威版，勿 requeue 旧袋），本席不自 drain、不代判。
### 十一、班尾实测新发现（22:38・袋② 吸收他会话未落地条目＝本席自犯归属篡改风险，另起不涂）

- 量尺＝两袋 meta 里的分数册 blob 逐字节 sha 对盘/HEAD 三面读数：
  HEAD＝`05bc7ce014f204a0`（106 行）・盘＝`682ab7cf437164b4`（**109 行**）・
  **袋① q-…-0001 册 blob＝`bb557705beea260f…`（108 行＝只含本席两行）・袋② q-…-0002 册 blob＝`682ab7cf437164b4…`（109 行）**。
- 读法＝袋② 快照时刻（22:34:15）⑦A 席在途件的 rows[108]（`TDM-E-L3-05/calibration/02_连板顺位`，
  本席 21:52 首测该卡 status=examining・22:38 复测已转 examined，lineage.run_id=`st-qoder-p07-1016-02`/score_row=rows[108]）
  **已被整档快照吸进本席袋**，而该条在 HEAD 面为 0 命中＝尚未落地。
  ⇒ 袋② 若先于该席自家袋落地＝**本席 commit 替他席写行**；该席随后投的自家袋对同一件极可能判"双侧皆改"而死（连坐）。
  本席承认＝这是自家 [CHIEF-1016-3] 自检漏量的一格（只过了 .py/新建件/旗标四条，未对共写热册做"袋 blob vs HEAD 差额逐条归属"），
  与在册红线"袋=整档快照＝归属篡改；绝不随袋提交他人未落地条目"同型。
- 本席**不自作主张处置**（删队列件＝动共享态，且禁盲重投/禁代判死）：
  请 ⑩/运行班二选一＝(a) drain 前把袋② 的分数册件按 HEAD 为基重放成"仅本席两行"的指称版（本席盘上不动 ⑦A 字节）；
  (b) 让 ⑦A 席自家袋先落地，袋② 该件随之判死或空转（先例＝代投件须让位于车道自落地）。
  本席盘上面保持现状＝**不删 ⑦A 那行**（删＝毁他工作）。
- [BLOCKER] 2026-10-16|⑦c席1016-02|流程问题|投袋前自检五门缺"共写热册袋 blob 与 HEAD 差额的逐条归属"这一格⇒本席袋②（22:34:15 快照）整档吸收 ⑦A 席未落地 rows[108]（HEAD 面 0 命中・盘 109 行 vs 袋① 108 行），先落即替他席写行并可能连坐其自家袋判"双侧皆改"死；本席不自删他席字节也不自行处置队列件|.runtime/commit_queue/pending/q-20261016-st-qoder-p07c-1016-02-0002.json 的 files[].blob_sha256=682ab7cf437164b4…（＝盘现值）与 -0001.json 的 bb557705beea260f…（＝本席两行版）＋git show HEAD:分数册＝05bc7ce014f204a0/106 行＋rows[108].run_id=st-qoder-p07-1016-02|⑩/运行班在 drain 前择一处置（重放本席袋为"仅自家两行"版，或让他席袋先落地）；SOP 侧建议给 [CHIEF-1016-3] 增第六格＝"共写热册投袋前逐条比 HEAD 差额归属"|高
### 十二、班尾自纠一行（22:40 现测，§十 末句被自家随后动作推翻，旧文不涂）

- §十 末句"本班不自投第三袋，避加队列压"＝**作废为线索**（原文保留不涂）：本席随后于 22:39:29 实投袋③
  `q-20261016-st-qoder-p07c-1016-02-0003`（files=2＝本席台账＋游标，**故意不含分数册与卡面**）。
  改判缘由＝§十一 实测发现袋② 的册 blob 与盘逐字节相等（109 行＝含 ⑦A 席未落地行），
  让"含册"版本继续留在途面＝归属外溢风险，而把尾巴面（§十・§十一・游标补充二）以"不含册"两件套落地
  ＝既不吞他席字节又保全本班登记 ⇒ 两害相权取加投一袋，代价如实＝队列多一席件（head 现仍为他班 300 件袋）。
- 本行本身＝袋③ 快照之后的第二截尾巴，**由下班袋承接落地**（本席此后不再加投）。
### 十三、班尾心跳守护第二次死亡实测（22:40:35・§三 BLOCKER-2 严重度上调依据，旧文不涂）

- 三把 keeper 时间线（全部现测，非推断）：pid **37316** 21:52 起 → 22:05 实测进程不存在且 `.runtime/locks` 无自家 heartbeat 文件；
  pid **22976** 22:07 起（按 10-15 在册配方＝守护单进程自注册活 PID 后同进程进环）→ **22:40:35 实测 `psutil.pid_exists(22976)=False`**，
  此时本席三袋仍 `state=pending`（`pending 3 / done 0`，head 已换为他班 0083 件袋＝带在推进但本席袋未轮到）；
  第 三次重启 pid **31156** 22:41 实测 registered/present True・entry_pid 已换新・hb_age 秒级。
- **关键反证＝白名单没挡住**：`data/runtime/process_reaper_keep.txt` 本班已登记自家两行
  （`.runtime/tmp/p07c_1016_02`・`st-qoder-p07c-1016-02`，第 415-416 行），而 pid 22976 的 cmdline
  ＝`python .runtime/tmp/p07c_1016_02/keeper.py` **逐字包含已登记子串**，仍于登记后 33 分钟死亡
  ⇒ "登记即免杀"这条在册假设在本班被证伪（或杀手非 reaper，§六 两候选均未验）；
  本班已按 ⑦c 席纪律不代杀、不自 drain，仅如实上报并第三次重启。
- §三 第 2 枚（卡锁互斥凭据不可信）与本条合读＝**考工席在途袋的心跳保活面不可依赖**，
  严重度按事实上调为"高"（原行不涂，本行为上调依据）；请 ⑩/运行班处置问项＝
  (1) keeper 真实杀手是谁（reaper 白名单为何不生效）；(2) 三袋 pending 期间若本席会话终结，
  是否由 ⑩ 代看落地；(3) 收班② 与在途袋互斥的措辞（§八 BLOCKER-5 已立）。
- 本行＝袋③ 之后第三截尾巴，仍由下班袋承接（本席不再加投）；本席 keeper pid 31156 留岗交下班按 PID 销。
### 十四、班尾分母复量与本席尺自犯（22:44・另起留旧案卷）

- 心跳归属实测收口（交下班勿追错 PID）：`.runtime/locks/heartbeat_st-qoder-p07c-1016-02.pid` 内容＝**28532**（psutil alive True・22:26 mtime）
  ＝会话注册时由工具自动生成的心跳守护，**不是**本席 keeper；本席 keeper 三代实测＝37316 亡／22976 亡／**31156 现 alive**。
  ⇒ 本班 §八"留岗不销"与 §十三"重启"所防的会话失活面，实测由 28532 兜住（这正解释 §六 里 salvage 三次同读 `registry:alive`）。
  下班＝袋终态复查后按 PID 精确销 31156；28532 属工具面，本席与下班均不自杀（在册红线＝禁按镜像名批杀）。
- **本席尺自犯一处（当场改判，旧数不涂）**：起手分母用 `exam_cards/*/*/*.yaml` 三层 glob＝559 件，
  而 22:43 复量 `find -name '*.yaml' -type f`＝**565** 件，六态加总 190＋163＋86＋71＋48＋1＝559 恰差 6＝
  **本席 glob 深度谓词族盲**，漏的正是新增四层目录 `entry_flow/L9/p03_crossday_shape/` 六件（逐件实测 status 全为 empty：
  L9-A01/calibration/09・10・11・12 与 L9-A02/calibration/14・15）。逐件复核＝565 件**全部**含顶层 `status:` 行
  （`grep -q "^status:"` 逐件零 miss）＝不是"6 件无状态"，是"本席的尺够不到 6 件"。
  本班 §一 那句"六态加总自证＝553 ✓"因此仅在起手时点成立；prereg 163 这一读数不受影响（新 6 件全为 empty）。
- [BLOCKER] 2026-10-16|⑦c席1016-02|工具缺陷|领面尺惯用的三层 glob `exam_cards/*/*/*.yaml` 对四层目录面查不到，实测漏 6 件（新入库的 entry_flow/L9/p03_crossday_shape/ 整目录，逐件 status=empty）＝分母与五态加总必假小；本席起手读数即已被该尺吞去 6 件（三件考工席历史读数是否同病＝本席未验，不代判）|find docs/03_modules/_domain_backtest/exam_cards -name '*.yaml' -type f＝565 与 ls */*/*.yaml＝559 两把尺同框；差集逐件＝该 4 层目录六件|⑩ 判是否把各席指令卡的普查尺统一改为 `find … -type f`（并按 is_file() 谓词分层，禁 rglob('*') 计空目录）；本席不改他席指令面|低
- 卡池现值（22:43 复量・下班勿沿）：empty **190**／preregistered **163**／examined **86**／blocked_on_data 71／blocked_on_impl 48／examining **1**；
  队列面＝本席三袋全 pending（done 0）、head 为他班 `q-20261016-st-diskp0-20261015-0083`。
- 本行＝袋③ 之后第三截尾巴，由下班袋承接（本席不再加投）。

## ⑦考工C 班次 1017-01（st-qoder-p07c-1017-01）｜起手 00:50・零 CH 全链预演班・本班出分 0 张（CH 禁跑窗与班限互斥，如实呈报）・本班零翻卡零改判据

### 一、分母与前置实测（两时点同尺，面值未动）

- 卡池四族（entry/exit/portfolio/position）文件总数 **589**；六态加总自证＝entry 167empty＋91prereg＋81examined＋69blocked_data＋29blocked_impl＋1examining＝438・exit 19＋25＋4＋3＝51・portfolio 16＋21＝37・position 18＋25＋2＋16＋2＝63 ⇒ 438＋51＋37＋63＝589 ✓。
- **prereg 磁盘面＝162**（起手 00:52:3x 与预演器内 01:01/01:03 两次 survey 同值＝值守内未动）。尺＝`rglob('*.yaml') AND is_file() AND 顶层 status: preregistered` 且首目录∈四族（本席 1016-02 §十四 自犯的三层 glob 深度族盲已按该条更正，本班不再用 `*/*/*.yaml`）。
- 分数册三面：disk **110 行** ＝ HEAD **110 行**（逐行 `- card_id:` 严式谓词，且 yaml 解析后 rows 同为 110；本班首次用 `^  - run_id:` 缩进式尺得 0 命中＝谓词错，正对照＝同册改行首谓词后 110/110/106）；index 面 106 行（在册形态「正门每落地一次主区 index 停在落地前一版」复现，本席不复位）。今日在册四行为 ⑦c 1016-01×2・⑦c 1016-02×2・⑦A 1016-02×1・⑧B 1016-02×1。
- 上班三袋终态（`commit_queue status --session st-qoder-p07c-1016-02` 00:51 现读）：袋① **done** landed_id=`e9089e6cfc1ba363baa4db7f0a33977cb3fffa51`；袋②③ **dead**，dead_reason 逐字＝`landing 异常: RuntimeError: [landing] 非注册表族件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/automation_campaign/p07c_examiner_c/ledger.md` ⇒ 上班尾巴面（§十—§十四 与游标补充二）**仍未落地**；本席不 requeue（死因＝双侧皆改而非 ghost，同字节重投必同死＝在册红线「requeue 前先读 dead_reason 修因」）、不自 drain、不手搬队列件。
- reaper 起手 00:50:46 实测 source=live・last_run=00:50:26・scanned=34・killed=0・degraded False・commit_pct 81.46・ram_used 73.3%・cpu 87.2%；dead_archive ok=False rc=1（serializer 租约存活 pid=47508，与本席 1016-02 班尾同态，销账面仍在 ⑩/⑨ 请办中）。

### 二、本班为何零出分（两条零 CH 路实测均堵，非省力选择）

- 硬互斥＝**CH 窗 01:00–04:00 禁跑** 与本班 90 分班限（00:50→02:2x）整段重叠 ⇒ 值守内不存在可取数窗；本班起跑 00:50，禁跑窗开启前仅 9 分钟，不足以装载任何一面宽面板。
- 零 CH 出分路两条，实测均无面：① **缓存面＝0**——全 `.runtime/tmp/` 按 parquet/csv/pkl/npz 谓词扫 close/open/panel/fwd/target/mask/ret 关键词命中 **0 枚**（仅存 6 枚信号侧件＝本席 1016-02 的 mf_mnp/mf_pc/shc/unl 与 1016-01 的 ti_chips_winner/conc_90，均为信号腿无目标腿）；⑦A 席装载口 `shift06_panel_materialize.py` 及其面板缓存本班实测已不在盘（`ls .runtime/tmp/p07/`＝33 件、grep materialize 零命中）。② **本地序列申报＝0**——162 枚 prereg 逐卡查 `data_binding.derived_series`／`target_series` 全空 ⇒ 执行器 `_declared_local_faces`（calibration_exam.py:893-910）无件可装，缺省路径照其在册 fail-closed 抛「缺省 CH 取数面未接」。
- 结论如实＝本班**不掺假分**（指令卡「只有考试口径算数」），把 90 分窗改用于产出**下班可零成本领面的执行器面案卷**（§三—§五）。

### 三、零 CH 全链预演（方法与三面隔离自证）

- 方法＝162 枚 prereg 逐张走真执行器全链 `run_card(卡的 tmp 副本, signal=, target=, [signal_b=], scores_path=tmp, ledger_registry_path=tmp)`；两面用固定种子合成数据（panel＝2042×100、series＝2042，日历＝bdate_range 2018-12-03..2026-09-30 覆盖全卡面 IS/OOS/regimes 窗），`IC_DEVICE=cpu` 强制（本班全程未 acquire GPU 看门人 ⇒ 收班⑥免执行）。
- 三面隔离**跑后实测**（非声明）：`prereg card files changed = 0`（逐卡 sha256 前后同值，162/162）；`score book sha unchanged = True`；生产试次册零命中——tmp 册未生成而每行带 `ledger_warning=[Errno 2] No such file or directory: ...preflight_trial_ledger.yaml`（121/121）＝`record_run` 被 run_card 的 except 吞成告警 ⇒ **合成试次一条未进生产 DSR 分母**（该行为符合在册「预检/接线不占分母」精神，本席据此判定本班无试次污染；本席未改 n_trial_ledger 一字）。
- 读法边界（勿越）＝**ran ≠ 该卡有供数可考**，只证「绑定层之后，执行器的形状预检＋判分路吃得住该卡面形状」；合成读数无研究含义，本席未把任何 ran 读数写进分数册。
- 耗时＝162 枚全程 13.5 秒（8 枚小批）＋满批 <3 分（`sum sec=42.0`、单卡上限 0.91 秒）⇒ **该预演尺零算力成本，各考工班皆可每班复跑**，请 ⑩ 判是否收编为开考前置工序（本席不自改 SOP）。

### 四、预演结果分类（162＝ran 121＋crash 41）

- route 面（`pillars_route`）＝series **126**／dual_arm **36**／event **0** ⇒ prereg 积压面**无事件路卡**（上班游标担心的事件路 OOS 地板柱不在本面积里）。
- ran 121 分层（族×kind）：entry_flow panel=25・entry_flow series=55・exit_flow panel=3・exit_flow series=6・portfolio_flow panel=4・portfolio_flow series=17・position_flow panel=10・position_flow series=1。
- **crash 类 (a)＝28 枚**：`ValueError: Data must be 1-dimensional, got ndarray of shape (2042, 100) instead`，全部为 route=dual_arm 且 kind=panel（即双臂路的 panel 卡 28/28 全崩，无一例外）。崩点逐帧实测＝`calibration_exam.py:561 _comparison_metrics` 无条件进 `:217 _series_metrics` → `:97 _spearman` 的 `pd.Series(a)` 接 2D 数组。
  反向自证＝对照/消融族专用驱动器 `comparison_exam.run_card_comparison` 同腿：`dry=True` 零写册不出分（实测 cmp_scores 件未生成），`dry=False` 崩在同一 `calibration_exam.py:97`（同帧同消息，shape (2042,60) 随本席位列数变）⇒ **两条路同一条腿，换入口救不了这 28 枚**。
- **crash 类 (b)＝13 枚**：`DateParseError: unable to parse: <散文串>`＝`window.regimes` 条目内 ISO 日期不足两个 → `_span_pairs`（calibration_exam.py:72-84）退回「整串当单点」→ `_in_spans` 的 `pd.Timestamp(散文)` 崩。与本席独立谓词普查（数日期个数<2）所得 13 枚**逐名相等**＝双证（两把尺互不引用、样本同为 13）。
  其中 **2 枚系 ⑥ 席 10-16 22:15 新出**（`entry_flow/L3/TDM-E-L3-11-1__calibration__03_竞价量比_现势窗`・`.../L3-11-2__calibration__03_涨速异动_现势窗`）⇒ 1016-02 班转单后该形制**仍在新增**（10 枚存量 10-10/10-15 出，本班新见 2 枚 10-16 出）。
- **下班领面全集尺（零成本）**＝162 枚 prereg 减去本席 §五 点名的 41 枚＝**121 枚**执行器可吃面；下班不必重跑预演，按 §五 避让名录直接领供数即可。
- 本班未复量「供数是否可得」这一条（CH 禁跑窗内无法量）⇒ 121 枚里有多少真能在窗内装载，仍须逐卡实测，勿把本席 ran 数当供数分母。

### 五、41 枚点名（避让面＝转单面，机生名录禁手打）

#### (a) 双臂路 panel 形不支持（28 枚，转 ⑤ 实现席）
  - 10-10 08:14 | exit_flow/S1/TDM-X-S1-01__comparison__02_六桶分类增益对照.yaml
  - 10-10 08:14 | exit_flow/S1/TDM-X-S1-02__comparison__02_时间止损档对照.yaml
  - 10-10 08:14 | exit_flow/S1/TDM-X-S1-03__comparison__02_止盈族三式对照.yaml
  - 10-10 08:14 | exit_flow/S1/TDM-X-S1-05__ablation__02_融合权重与去抖消融.yaml
  - 10-10 08:14 | exit_flow/S1/TDM-X-S1-06__comparison__02_K3连续破位强清对照.yaml
  - 10-10 08:14 | exit_flow/S1/TDM-X-S1__ablation__02_卖出信号段整体消融对照.yaml
  - 10-10 08:14 | exit_flow/S2/TDM-X-S2-01__comparison__02_执行方式路由与流动性三查对照.yaml
  - 10-10 08:14 | exit_flow/S2/TDM-X-S2-03__comparison__02_执行口径净收益对照.yaml
  - 10-10 08:14 | exit_flow/S2/TDM-X-S2-04__comparison__02_本地条件单追单闭环对照.yaml
  - 10-10 08:14 | exit_flow/S2/TDM-X-S2-05__comparison__02_分批止盈阶梯对照.yaml
  - 10-10 08:14 | exit_flow/S2/TDM-X-S2-06__ablation__02_卖出闭环三率反馈权重消融.yaml
  - 10-10 08:14 | exit_flow/S2/TDM-X-S2__ablation__02_执行约束层现实性税度量.yaml
  - 10-10 08:14 | exit_flow/X1/TDM-X-R1-02__comparison__02_L3减仓顺序三臂对照.yaml
  - 10-10 08:14 | exit_flow/XFLOW/TDM-X-FLOW__ablation__02_离场信号整链消融总账.yaml
  - 10-10 23:59 | entry_flow/L2/TDM-E-L2-07-1__ablation__03_强度维单位口径错配.yaml
  - 10-10 23:59 | entry_flow/L2/TDM-E-L2-07__ablation__03_时间窗外不评级并入观望的边际.yaml
  - 10-10 23:59 | entry_flow/L2/TDM-E-L2-07__comparison__03_追高与低吸胜率对照.yaml
  - 10-10 23:59 | entry_flow/L2/TDM-E-L2-09__comparison__02_催化剂加权形式板块恒定与标的指数衰减.yaml
  - 10-15 19:00 | position_flow/P1/TDM-P-P1-04__comparison__02_否决线三型可选档对照.yaml
  - 10-15 19:00 | position_flow/P1/TDM-P-P1-05__comparison__02_单票上限三档对照.yaml
  - 10-15 19:00 | position_flow/P1/TDM-P-P1-05__comparison__03_漂移触发与周期触发对照.yaml
  - 10-15 19:00 | position_flow/P1/TDM-P-P1-05__shadow__05_组合体检帽影子对照.yaml
  - 10-15 19:00 | position_flow/P1/TDM-P-P1__comparison__02_否决腿与熔断腿双臂增量.yaml
  - 10-15 19:00 | position_flow/P2/TDM-P-P2-04__comparison__02_调仓频率与换手惩罚六臂对照.yaml
  - 10-15 19:00 | position_flow/P3/TDM-P-P3-03__comparison__02_仓位定尺寸七档对照.yaml
  - 10-15 19:00 | position_flow/P3/TDM-P-P3__comparison__02_金字塔三档与一次性足额对照.yaml
  - 10-15 19:00 | position_flow/PFLOW/TDM-P-FLOW__ablation__02_持仓叠层整链消融.yaml
  - 10-16 11:56 | position_flow/P1/TDM-P-P1-03__comparison__03_逻辑存活否决腿开闭对照.yaml

#### (b) regimes 散文条目（13 枚，转 ⑥ 制卡席；(b)-1 与 (b)-2 系本班新见）
  - 10-10 08:14 | exit_flow/S1/TDM-X-S1-04__comparison__05_早盘破位假信号时段可靠性.yaml
  - 10-10 08:14 | exit_flow/S2/TDM-X-S2-02__calibration__03_新股首日分层卖出三臂.yaml
  - 10-10 08:35 | entry_flow/L9/TDM-E-L9-A06__calibration__02_主力净流入截面.yaml
  - 10-10 08:35 | entry_flow/L9/TDM-E-L9-A11__calibration__02_EIA库存意外.yaml
  - 10-10 08:35 | entry_flow/L9/TDM-E-L9-A15__calibration__02_资金费率拥挤跨市场预警.yaml
  - 10-10 08:35 | entry_flow/L9/TDM-E-L9-A15__calibration__03_币圈镜像资金费率对BTC.yaml
  - 10-10 08:35 | entry_flow/L9/TDM-E-L9-V3__ablation__02_板块状态快照T-1纪律.yaml
  - 10-15 19:00 | position_flow/P2/TDM-P-P2-01__comparison__02_三道门串并开闭与互斥诊断.yaml
  - 10-15 19:00 | position_flow/P2/TDM-P-P2-03__comparison__02_未闭环敞口过夜代价双臂.yaml
  - 10-15 19:00 | position_flow/P2/TDM-P-P2__comparison__02_做T腿有无对照与底仓恒等性.yaml
  - 10-15 19:00 | position_flow/P3/TDM-P-P3-01__comparison__03_情绪段加仓权限分层对照.yaml
  - 10-16 22:15 | entry_flow/L3/TDM-E-L3-11-1__calibration__03_竞价量比_现势窗.yaml
  - 10-16 22:15 | entry_flow/L3/TDM-E-L3-11-2__calibration__03_涨速异动_现势窗.yaml

### 六、随机噪声下的两条 pass（现象登记，本席不裁）

- 合成两面（信号与目标互独立的白噪声，真 IC≈0）下 121 枚 ran 中 2 枚 `verdict=pass` 且 `fails=[]`：
  1. `TDM-P-P1-04/calibration/04_持仓停滞天数对后续收益预测`＝metrics 实读 ic_mean **+0.00321**／n=2042，而该卡 `pillars_numeric` 冻的是**负地板** `ic_mean_min: -0.015`・`mono_spearman_min: -0.5`・`ic_ir_min: -0.25` ⇒ 白噪声必然落在地板之上；该卡假设方向为负向（卡面 hypothesis 轴），但门柱只设下界不设上界⇒**方向柱缺位**这一读法本席未自判，请 ⑨ 成绩官/⑤ 判是否属门柱面缺陷或 ⑥ 出题面缺陷；
  2. `TDM-E-L2-01/comparison/02_等权与IC加权双臂`＝双臂路，行内 `ic_mean=None`／`n=None` 而 `fails=[]`、`unjudged.numeric_keys_not_read=[]`、`numeric_keys_no_machine_face={}`、`pillars_prose_keys` 列 6 条散文柱 ⇒ 册面自述「无未判柱」却零数值面。本席只登记该形态（双臂路的 unjudged 披露面是否漏报），**不下结论**，交 ⑤ 读 `_judge_comparison` 全貌后判。
- 两条合读给 ⑩/⑨ 一句事实：**判官在「卡面冻负地板」或「数值面无」时不会判 fail**；本席按在册红线未动任何门柱字节。

### 七、孤儿 examining 卡一枚（报 ⑦A/⑩，本席不代修）

- `docs/03_modules/_domain_backtest/exam_cards/entry_flow/L3/TDM-E-L3-03-2__calibration__03_温和放量.yaml`：盘现测 `status: examining`・`lineage.run_id: null`・文件 mtime 10-16 18:38:44，而 `git show HEAD:` 同名件 `status: preregistered`（两面不等＝该翻面未落地）；`.ailocks/` 现查无该卡锁（只有 ⑦A 席台账锁与 git_commit 全局锁）。
- 归属旁证＝⑦A 席 1016-03 班 tmp 存 `dry01_scores_L3-03-2__03_温和放量.yaml`（18:37）与 `p07/shift01_dry.json`，时点紧邻该卡翻面后 1 分钟 ⇒ 形态＝「按占卡三步翻 examining 后未开考」。**本席不翻回、不 release 他会话 claim、不代判**（在册红线＝他会话在途面 owner 责任制）。
- 后果如实：执行器状态闸只认 preregistered（`calibration_exam.py:979-980`）⇒ 该卡对**全席不可考**直至复位；本席本班未使用重考旗（force 的在册语义＝重考已出分卡，与本情形不同物）。

### 八、[BLOCKER] 登记（本班 4 枚：高 2／中 2）

- [BLOCKER] 2026-10-17|⑦c席1017-01|工具缺陷|双臂（dual_arm）路对 panel 形双腿结构性不支持＝prereg 积压里 route=dual_arm 且 signal_kind=panel 的 28 枚全部出不了分，且对照族专用驱动器 comparison_exam 同根（dry=False 崩在同一条腿），换入口救不了；崩点 calibration_exam.py:561 `_comparison_metrics` 无条件进 :217 `_series_metrics`→:97 `_spearman` 的 pd.Series(2D)|.runtime/tmp/p07c_1017_01/preflight.jsonl 里 outcome=crash 且 err 前缀 ValueError 共 28 行（全条 tb_tail 同一 pandas construction.py:715）；本席 §五(a) 28 枚具名；反向自证＝同卡 comparison_exam dry=True 零写册／dry=False 同帧崩|⑤ 判修法＝`_comparison_metrics` 按 signal_kind 分派（panel 走 `_panel_metrics` 两臂各算再取差）或显式 fail-closed 出 blocked 行；本席不动码面不改判据|高
- [BLOCKER] 2026-10-17|⑦c席1017-01|数据问题|卡面 window.regimes 的散文条目（条目内 ISO 日期不足两个）仍在新增：本班 13 枚 DateParseError 里 2 枚系 ⑥ 席 10-16 22:15 新出的现势窗卡（L3-11-1/03・L3-11-2/03），而 10-16 22:1x 本席 1016-02 班已就该形制转单一次未获修；崩因链路＝calibration_exam.py:72-84 `_span_pairs` 退回整串→`_in_spans` 的 pd.Timestamp(散文) 抛|§五(b) 13 枚具名（含两枚 mtime 10-16 22:15）；本班独立普查谓词与预演实测双证逐名相等；`git show HEAD:calibration_exam.py` 内 `_in_spans` 无散文容错支|⑥ 出题面把 regimes 只写 span（`YYYY-MM-DD..YYYY-MM-DD`）或移出窗口映射，注释另置 note 键；⑤ 若选执行器容错须每出口独立计数（禁静默跳过＝在册假绿形态）|高
- [BLOCKER] 2026-10-17|⑦c席1017-01|判据缺失|判官在「卡面冻负地板」与「数值面无」两种形态下必放行：白噪声两面（真 IC≈0）121 枚 ran 里 2 枚 verdict=pass 且 fails 空——其一 ic_mean +0.00321 对 ic_mean_min=-0.015 负地板（方向柱缺位），其二双臂路 ic_mean=None/n=None 而 unjudged 三面全空（自述无未判柱）|§六 两枚具名＋本席 tmp `preflight_scores.yaml` 两行原文；卡面 `position_flow/P1/TDM-P-P1-04__calibration__04` 的 pillars_numeric 三键全负值；calibration_exam.py:267-269 在册注释已自述「judge 对 NaN 的处置是跳过加败（只可能放行不可能记败）」|⑨ 成绩官判该两枚的历史读数可信度、⑤/⑩ 判是否立法「方向柱必配／零数值面不得 pass」；本席不自设门柱也不改冻结值|中
- [BLOCKER] 2026-10-17|⑦c席1017-01|流程问题|考工席指令卡的「CH 窗 01:00-04:00 禁跑」与「90 分班限」互斥：00:50 起班的整班落在禁跑窗内＝该班必然零出分（本班实测两条零 CH 路均无面：缓存目标面板 0 枚＋162 枚 prereg 零本地序列申报），而卡面仍要求「每班≥8 张出分」；排班器按 90 分等间隔出牌不辨窗口|本席 §二 两条实测读数＋reaper 起手 00:50・禁跑窗 01:00・班限终点约 02:2x 三点同框；`find .runtime/tmp` 目标面板关键词命中 0；162 枚 derived_series/target_series 全空|⑩ 判该窗内班次的任务书是否改派「零 CH 工序」（预演尺＝13.5 秒/162 枚，本班已给方法）或把 ⑦ 系班次窗错开禁跑段；本席不改他席指令面与排班册|中

### 九、收班八件（现测读数）

- ①release＝本席三件 claim（台账・游标・及本班追加的 keep 名册无锁）在末袋入队后自跑 `--release-only`；②心跳＝keeper pid **39796**（01:01:33 registered present=True entry_pid=39796），收班按 PID 精确终止并等 ≥70 秒双谓词复量（禁按镜像名批杀；本班实测网关调用会代起心跳守护，杀须排在末次网关动作之后）；③耗时＝00:50 起→落笔时点见本班末行实测；④[BLOCKER]＝本班 4 枚（§八，高 2／中 2），追加后严式行首计数由起手 13 增至 17；⑤自清＝本班 tmp 件在投袋后按消费者次序删除（keep 名册两行保留＝在册白名单面非本班产物）；⑥GPU＝本班全程 IC_DEVICE=cpu 未 acquire 看门人 ⇒ 免执行；⑦子代理＝本班零 spawn ⇒ 零孤儿；⑧worktree＝本班未调用任何工棚/工作树入口，收班现测 `git worktree list` 读数与 `.aidrafts/st-qoder-p07c-1017-01` 存在性一并写在本席末段（会话注册自动影子壳系工具面，本席不自删）。
- 本班未做（如实）＝零出分・零翻卡・未 requeue 任何死袋・未 release 他会话 claim・未动判据/门柱/冻结值・未动它席指令面・未动分数册字节・未 spawn 子代理・未 acquire GPU。
- 游标推进＝本席 checkpoint 只追加本班游标节（上文各节逐字不涂），写后复核上一班游标行仍在。


### 十、收班实测（01:57:00 现测，本班唯一尾巴节・上文 §一—§九 逐字不涂）

- **本班实耗＝66.2 分**（锚＝本班首条冷启动命令实测 00:50:46，落笔时点 01:57:00 现测；keeper.log 末次写盘 01:40:17＝守护心跳循环写痕，**非出生锚**，本席不用它算耗时）⇒ 90 分班限内收班，未超窗。
- **本班袋终态**（`commit_queue.py status --session st-qoder-p07c-1017-01` 现读）：counts={'pending': 0, 'processing': 0, 'done': 1, 'dead': 0}・head 位=`q-20261017-st-qoder-p01-1017-02-0002`（waiting 1996.4 秒）
    - `q-20261017-st-qoder-p07c-1017-01-0001` state=**done** landed_id=`1562d8d066e5` dead_reason=无
- **落地面复量**：台账 HEAD 面 602 行 vs 盘面 602 行；游标 HEAD 面 173 行 vs 盘面 173 行。
  盘面严式行首 `[BLOCKER]`＝**追加前现测 17／追加后本机自算 18**（本节含 BLOCKER 1 枚；§九 那句"本班 4 枚"系该节落笔时点读数，旧文不涂）；HEAD 面取数 rc=0。
- **心跳两枚现测（收班② 依据，逐枚列下）**：
    - pid 39796 alive=True cmdline=[C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe .runtime/tmp/p07c_1017_01/keeper.py]
    - pid 46040 alive=True cmdline=[C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe -m zephyr.gov_enforcement.rule_bridge.heartbeat_daemon st-qoder-p07c-1017-]
  ＝本席 keeper（39796）与网关入队时代起的 `heartbeat_daemon`（pid 文件持 46040）并存，与 10-17 ⑨席在册读数"每调一次网关各代起一枚"同形。
- **worktree 面（收班⑧ 现测）**：`git worktree list` 共 82 行，含本席 sid 者 **0** 枚；
  `.aidrafts/st-qoder-p07c-1017-01` 存在性＝**False**（本班实测**未**自动生成影子整树，与 1016-02 班"会话一注册即生成整树"读数不同＝如实报两读，本席不自删任何 worktree/aidrafts 面）。
- **GPU（收班⑥）**：本班全程 IC_DEVICE=cpu，未 acquire 看门人；`python scripts/gpu/gpu_watchman.py status` 现读 active=(none)・free_gb=21.57・util_pct=14.0 ⇒ 本席无牌可还，免执行成立。
- **下班供数分组面（现算，供领面排序；一表可服务多卡）**：c1_market.kline_daily_hfq=53; c1_market.kline_sector_880=26; c1_market.kline_index=25; c1_market.emotion_index=12; c1_market.stk_limit=11; c1_backtest.regime_state_anchored=9; c1_market.tick_data=9; c1_market.kline_daily=7；另 **13 枚 ran 卡面零表名 token**（供题面缺口，须人读卡面或转 ⑥ 补申报）。
- **断供候选交叉（本尺只给候选，真挡须按"窗与列"在 CH 窗内逐条读，禁按表名命中判——本席不据此排除任何卡）**：
  `src/zephyr/data/config/known_data_gaps.yaml` 解析 85 条，未了账态（no_source/open/monitoring/retired_quarantine）共 42 条・点名表 40 张；
  121 枚 ran 中按表名命中未了账表者 37 枚，其中集中于 `c1_market.kline_sector_880`（26 枚 ran 提该表）——该表在册 gap 的 impact 逐字为"15/30/60min 缺失、日K腿无恙"⇒ **按在册判法不挡 `period='1d'`**，本席据此把 37 枚候选**降级为不挡**，不作避让。
- **下班领面序（ran 面按 mtime 最旧 12 枚，本机时戳现读；本席扩席令面＝收积压最久）**：
    - 10-09 20:25 | kind=panel route=series | entry_flow/L1/TDM-E-L1-S0__calibration__02_货币卡.yaml
    - 10-09 20:25 | kind=series route=series | entry_flow/L1/TDM-E-L1-S0__calibration__03_流动性卡.yaml
    - 10-09 20:25 | kind=series route=series | entry_flow/L1/TDM-E-L1-S0__calibration__04_海外卡.yaml
    - 10-09 20:25 | kind=panel route=series | entry_flow/L1/TDM-E-L1-S0__calibration__05_政策事件卡.yaml
    - 10-09 20:25 | kind=panel route=series | entry_flow/L1/TDM-E-L1-S1__calibration__03_黄白线交叉.yaml
    - 10-09 20:25 | kind=series route=series | entry_flow/L1/TDM-E-L1-S2__calibration__07_连板家数分布.yaml
    - 10-09 20:25 | kind=series route=series | entry_flow/L1/TDM-E-L1-S3__calibration__02_昨日涨停溢价.yaml
    - 10-09 20:25 | kind=series route=series | entry_flow/L1/TDM-E-L1-S3__calibration__03_晋级率.yaml
    - 10-09 20:25 | kind=series route=series | entry_flow/L1/TDM-E-L1-S3__calibration__04_情绪先锋四态.yaml
    - 10-09 20:25 | kind=series route=series | entry_flow/L1/TDM-E-L1-S4__calibration__02_期权IV主路径.yaml
    - 10-09 20:25 | kind=series route=series | entry_flow/L1/TDM-E-L1-S4__calibration__03_合成VIX后备.yaml
    - 10-09 20:25 | kind=series route=series | entry_flow/L1/TDM-E-L1-S5__calibration__02_11信号环比.yaml
- **prereg 收班复量＝162**（起手 162，本班值守内未动；本班零翻卡）。
- **令卡一条已过时（现测双证）**＝本席指令卡仍写「panel 卡禁走 CLI（--target-csv 砍单列缺陷未修）」，
  而该缺陷**已由 ⑤ 于 10-16 16:48 落地治本**：`git show HEAD:scripts/backtest/fexam/calibration_exam.py` 第 1154-1155 行
  ＝「panel 目标保列语义与 --signal-csv 同款：单列→Series，多列→整面 DataFrame（禁砍单列）」＋`tgt = t.iloc[:, 0] if t.shape[1] == 1 else t`，
  磁盘面与 HEAD 面同读该两行（禁只信盘面的在册纪律），落地 commit=`8caf2743b9`（消息自述"panel 卡 CLI 解禁"）；
  `python scripts/backtest/fexam/calibration_exam.py --help` 实测三态＝口存在且带 `--signal-csv/--signal-b-csv/--target-csv/--force`。
  **本席未做端到端真跑**＝CLI 无 scores_path 旗，真跑会往生产分数册写行，而本席合成两面无研究含义 ⇒ 只出码面自证，
  下班可在 CH 窗内用真供数走 CLI 首验（该路一旦确证，panel 卡开考成本从"自物化注入"降为"两个 csv"）。
- [BLOCKER] 2026-10-17|⑦c席1017-01|流程问题|考工席指令卡的「panel 卡禁走 CLI（--target-csv 砍单列缺陷未修）」一条已被 ⑤ 治本袋作废（HEAD 面逐行可 grep），令面未随动⇒下班仍会按旧条放弃一条更省力的开考通道，且本席三班连续按"自物化注入"重造同一件事；本席不改他席指令面|`git show HEAD:scripts/backtest/fexam/calibration_exam.py` 第 1154-1155 行・落地 commit=8caf2743b9(10-16 16:48, 消息含"panel 卡 CLI 解禁")・`--help` 实跑读数四旗齐|⑩ 在 ⑦ 系令卡把该句改为"panel 可走 CLI，本席须自验首张；series 路照旧"并注实测锚；本席已把该口存在性与未真跑缘由如实登记|中
- **本班收班次序申明**：袋终态若非 done，则收班② 延后——本席 keeper 39796 与网关代起枚按上列 PID 交下班核活后精确终止（禁按镜像名批杀），本席不自 drain、不 requeue、不手搬队列件。
- **本节归属申明**＝本节写于袋① 快照之后 ⇒ **不为本节加投第二袋**（在册两难＝同会话后袋在前袋落地后必判双侧皆改而死，且每调一次网关各代起一枚心跳＝收班② 递归无出口）；本节由下班袋承接落地，下班领面以**盘面**为权威（同 1016-02 班尾巴面形态）。
- **本班 tmp 处置**＝按小步收班② 于收班末删除 `.runtime/tmp/p07c_1017_01/`（消费者次序：先出本节读数，再删；keep 名册第 420-422 行属白名单面保留）。预演器本体随之消失，**方法与参数已全数写在 §三**（副本＋双 tmp 写面＋固定种子＋两面形状＋IC_DEVICE=cpu），下班据此可 15 分钟内重建；本席不在永久区自建工具件（净零增长与 CREATE-GUARD/token/翻译登记义务不擅动）。

### 十一、收班末段（02:00x 现测・§十 之后第二截尾巴，上文 §一—§十 逐字不涂）

- **心跳真身终局实测（推翻 §十 里"alive=True"的时点后状态，两行各自在其时点为真）**：01:58:33 现测 pid **39796（本席 keeper）alive=False**・pid **46040（网关代起的 heartbeat_daemon，pid 文件持者）alive=False**；
  `keeper.log` 末次写盘 **01:40:17**，末行逐字＝`SessionRegistry: failed to load legacy registry: [Errno 13] Permission denied: 'D:\ZephyrAlpha\.runtime\session_registry.json'`
  ⇒ 本席守护死于**共享注册表读取被拒**（不是被 reaper 收割：本班两行 keep 名册在位且 01:40 后零收割事件指向本席 pid）。这是 1016-02 班 §十三"登记即免杀被证伪、杀手未定论"两候选之外的**第三条候选机制**，本席只登记观测不代他席定论。
- **⚑ 本班单样本反证（要 ⑩ 定性，不改条款）**：本席袋 `q-20261017-st-qoder-p07c-1017-01-0001` 实际落地时刻＝**01:55:51**（`git log -1 -- 台账` 现读，commit=1562d8d066），
  而两枚守护最迟于 **01:40:17** 后已不在写痕、01:58 实测双双不存在 ⇒ **袋在无自家心跳的约 15 分钟里照常 drain 成 done**。
  ⇒ 在册前提「袋落地期间 keeper 必须在岗，否则推进 ghost_session 死族」（本席 10-15 首班实证＋keep 名册第 43 行）在本样本未被复现；
  1016-02 §八 那枚"收班② 与在途袋互斥"待裁 BLOCKER 的必要性因此**下调为证据不足**，请 ⑩ 判措辞（本席不自改指令面与 SOP）。
- **收班② 终态处置**＝本班不重启 keeper（重启只为记录末段读数＝在册"为记读数再补袋＝递归无出口"同型浪费），
  只按 pid 文件精确清尾：`.runtime/locks/heartbeat_st-qoder-p07c-1017-01.pid` 内容 46040 而进程已亡 ⇒ 删除该 stale pid 文件（防"说谎心跳"面）；
  宽谓词枚举实测 4 枚命中里 **3 枚是携带本席脚本正文的父 bash 壳（pid 8036/40260/56264）＝在册"按 cmdline 子串批杀会自杀"陷阱本班再次同框，本席一律不动**，
  正对照＝同尺可枚举到他席守护，谓词非空。
- **本班不再补第二袋（申明理由）**＝§十/§十一 系本班袋① 快照之后所写，留作**盘面尾巴由下班袋承接**；
  理由不是省力而是本班实测：袋① 从入队（01:16:03）到落地（01:55:51）耗时 **39.8 分**（head 位一度为他班 1504 秒旧袋），
  此刻 02:00 再投一袋按该节拍必超本班 90 分窗（终点约 02:20），结果＝给下班留"在飞袋＋必须重起心跳"的更坏面；
  留尾巴的代价本席已知且被 1016-02 先例覆盖（下班读盘面为准，卡状态与台账均以磁盘面为权威）。
- **收班其余各件现测**＝①claim：本班末次 `--release-only` 01:57:19 回执 `RELEASED: 2 files (verified)`，随后 `lock_files.py list` 全量面 grep 本席 sid＝**0 命中**（01:58:33 复量；§十一 写作前按"改前 claim"重新 acquire 台账一枚，末段后由 ② 一并 release）；
  ③耗时＝00:50:46→02:00 约 **69 分**（90 分班限内）；④[BLOCKER]＝本节再追加 1 枚 ⇒ 盘面严式行首计数由 18 增至 **19**（起手 13＋§九 4＋本节 1，逐节各在其时点为真）；
  ⑤自清＝`.runtime/tmp/p07c_1017_01/` 全部本班件（预演器/普查器/收班读数器/副本卡目录/合成分数册）在本节落笔后删除，keep 名册 420-422 行属白名单面保留；
  ⑥GPU＝全程 IC_DEVICE=cpu・`gpu_watchman.py status` 现读 active=(none) ⇒ 无牌可还；⑦零 spawn 子代理 ⇒ 零孤儿；
  ⑧`git worktree list` 含本席 sid **0 枚**・`.aidrafts/st-qoder-p07c-1017-01` 实测不存在 ⇒ 本班零自建整树。
- **本班出分＝0 张（保底未达，如实呈报）**：双口径均未达（0＜8 张・69 分＜4 小时），根因非省力＝CH 禁跑窗与班限互斥＋两条零 CH 路实测无面（§二）。
  本班净产出＝162 枚积压的执行器面分类（121 可吃／41 避让且具名）＋两条结构性堵点定位到行（双臂 panel 路 28 枚・regimes 散文 13 枚）
  ＋令卡一条已过时的现证（panel CLI 已解禁）＋一条在册前提的单样本反证（心跳与在途袋）。
- [BLOCKER] 2026-10-17|⑦c席1017-01|工具缺陷|恒定班心跳守护可在"登记进 reaper 白名单之后"死于共享注册表读取被拒（Permission denied），非收割所致且死前无任何退出码回执，导致"在途袋须守护在岗"这一收班条款的执行面不可依赖：本席 keeper 末行逐字=[Errno 13] Permission denied: .runtime/session_registry.json（01:40:17 写痕），01:58 实测 keeper 与网关代起枚双双不存在，而袋仍于 01:55:51 成 done ⇒ 同一条款两头都失准（既没保住该保的，也没杀死该杀的）|.runtime/tmp/p07c_1017_01/keeper.log 末行（tmp 随本班收班删除，此处逐字引文为唯一留痕）・commit=1562d8d066 时间戳・lock_files list 本席 sid 0 命中・宽谓词枚举 3 枚父壳同框|⑤/运行班判 session_registry.json 的并发读写是否须改 per-session 文件或加重试；⑩ 判"收班② 与在途袋互斥"条款按本样本改措辞（本席不自改）|中

### 十二、证据指针申明（02:0x 现测・本节之后本班即自清 tmp，上文逐字不涂）

- 本台账 §三/§四/§六/§八 内引用的 `.runtime/tmp/p07c_1017_01/*`（预演器本体・`preflight.jsonl`・`preflight_scores.yaml`・`keeper.log`・卡副本目录）**自本节起按 Owner 方案1 小步收班②全部删除＝指针按设计失效**，勿再按路径取件、勿据此判"证据灭失=案卷作废"。
- 可久留面＝本台账自身：§三＝方法与隔离参数（副本卡＋双 tmp 写面＋固定种子＋两面形状＋IC_DEVICE=cpu），§四＝162＝ran 121＋crash 41 的分类与两处崩点行号，§五＝41 枚具名（已按 `is_file()`＋`status: preregistered` 双谓词反查＝41/41 在位、零转抄错），§六＝两枚白噪声 pass 的实读数值，§十/§十一＝令卡过时项与心跳反证。
- 本班收班终态一行＝出分 0・零翻卡・零改判据/门柱/冻结值・分数册字节零动作・自家 claim 0・自家心跳件 0・tmp 0・子代理 0・worktree 0・实耗约 71 分（00:50:46→02:0x）・袋① done(1562d8d066)・§十—§十二 留盘面交下班袋承接。

## ⑦考工C 班次 1017-02（st-qoder-p07c-1017-02）｜起手 02:20:21・CH 禁跑窗整班覆盖・本班出分 0 张（保底双口径均未达，如实呈报）・零翻卡零改判据/门柱/冻结值・分数册字节零动作

### 一、冷启动与上班交班四查（date 现测，磁盘面为准）

- python 3.12.8；`lock_files.py cleanup`＝CLEAN 无死锁；reaper 02:21:20 实测 source=live・killed=0 reported=30・degraded False・commit_pct 82.53・ram_used 73.5%・cpu 75.7%⇒允许写。
- 本班整班落在 **CH 禁跑窗 01:00–04:00**（起手 02:20:21，班限终点约 03:50，窗解 04:00 已超班限 10 分）⇒本班零真分；该"窗与班限互斥"已在册（上班 §八 第 4 枚），本班不重复立案，只补一条新读见 §五。
- 交班四查逐条回批（上班台账 §十/游标"下班首查四件"）：
  ① **上班袋① done**（landed_id=1562d8d066，`commit_queue status --session st-qoder-p07c-1017-01` counts done=1 dead=0）；**但上班尾巴面（台账 §十—§十二）至今未落地**＝本席台账 HEAD 面 602 行 vs 盘面 679 行（差 77 行）、盘面严式行首 `[BLOCKER]` 19 行 vs HEAD 面 17 行⇒本班随袋承接。
  ② **⑤ 双臂×panel 腿未修**（两面同证）：`scripts/backtest/fexam/calibration_exam.py` 磁盘面与 HEAD 面 sha16 全等（a8e7c40a1531ee6b），:557 `_comparison_metrics` 仍是单路、:561-562 无条件进 `_series_metrics`、:1049 无条件调用，无按 signal_kind 分派支⇒28 枚崩面原样在位。
  ③ **⑥ regimes 散文未修**：prereg 面本班复量 13 枚，逐名与上班 §五(b) 名单相等（含 10-16 22:15 新出的 L3-11-1/03・L3-11-2/03）；`TDM-E-L9-A06__calibration__02` 卡面 bull_note mtime 仍 10-10 08:35＝本席零触碰。
  ④ **孤儿卡未复位**：`entry_flow/L3/TDM-E-L3-03-2__calibration__03_温和放量` 盘 status=examining／HEAD=preregistered／mtime 仍 10-16 18:38:44；本班未翻、未 release 他会话 claim（归 ⑦A/⑩）。

### 二、分母复量与正对照（两把尺同框）

- 四族文件总数 **609**（上班 589）；六态加总自证＝empty 240／preregistered **162**／examined 87／blocked_on_data 71／blocked_on_impl 48／examining 1＝609 ✓。
- prereg 族分片＝91／25／21／25＝162（与上班逐值相等）。
- **面值移动复量＝0**：prereg 中 mtime 晚于上班 01:03 读数者 0 枚⇒上班"162＝ran 121＋crash 41"的名录与分母可直接引用，下班不必重跑预演（这是本班实测，不是推断）。
- 正对照（真源单口 `pillars_route(card)`，禁抄第二份）＝route {'series': 126, 'dual_arm': 36}／signal_kind {'series': 83, 'panel': 79}／交叉 dual_arm/panel=28／dual_arm/series=8／series/panel=51／series/series=75；dual_arm×panel＝**28**（上班在册 28）；regimes 散文＝**13**（上班在册 13）⇒两把尺与上班逐字复现＝面值确未动。
- 分数册三面（起手 02:3x 现测）＝disk **110** 行＝HEAD **110** 行（严式 `- card_id:` 谓词）、index 106 行（在册"正门每落地一次 index 停在落地前一版"形态复现，本席不复位）；本班自带备份 `.runtime/tmp/p07c_1017_02/scorebook_backup.bin`（与盘逐字节相等，sha16 a9532fceb0899c94），本班未写一行。

### 三、本班主产出＝领面序纠偏（零 CH，直接改下班动作）

- 尺＝领面全集（162 减 41 避让＝**121** 枚）按 mtime 升序，逐张量 `data_binding.signal_derivation` 非空＝本席 1016-01 在册那一关"卡面是否给出 t 日可算式"。
- 结果＝**有可算式 108／整块无 data_binding 13**（加总 108+13=121 ✓）。13 枚具名：
   - 10-09 20:25 | entry_flow\L1\TDM-E-L1-S0__calibration__02_货币卡.yaml
   - 10-09 20:25 | entry_flow\L1\TDM-E-L1-S0__calibration__03_流动性卡.yaml
   - 10-09 20:25 | entry_flow\L1\TDM-E-L1-S0__calibration__04_海外卡.yaml
   - 10-09 20:25 | entry_flow\L1\TDM-E-L1-S0__calibration__05_政策事件卡.yaml
   - 10-09 20:25 | entry_flow\L1\TDM-E-L1-S1__calibration__03_黄白线交叉.yaml
   - 10-09 20:25 | entry_flow\L1\TDM-E-L1-S2__calibration__07_连板家数分布.yaml
   - 10-09 20:25 | entry_flow\L1\TDM-E-L1-S3__calibration__02_昨日涨停溢价.yaml
   - 10-09 20:25 | entry_flow\L1\TDM-E-L1-S3__calibration__03_晋级率.yaml
   - 10-09 20:25 | entry_flow\L1\TDM-E-L1-S3__calibration__04_情绪先锋四态.yaml
   - 10-09 20:25 | entry_flow\L1\TDM-E-L1-S4__calibration__02_期权IV主路径.yaml
   - 10-09 20:25 | entry_flow\L1\TDM-E-L1-S4__calibration__03_合成VIX后备.yaml
   - 10-09 20:25 | entry_flow\L1\TDM-E-L1-S5__calibration__02_11信号环比.yaml
   - 10-10 19:37 | exit_flow\X1\TDM-X-S1-03__comparison__02_dualwindow.yaml
- **指令卡"按 mtime 从旧到新取积压最久"在本面积的前 12 枚全部命中无绑定面**＝按序领面会白烧 12×15 分窗（≈三班）。首个带可算式者位序＝index 12＝`exit_flow/S1/TDM-X-S1-04__calibration__03_席位净卖出派发前瞻收益`（10-10 08:14）。
- 这 13 枚不是本班新堵：10-15 首班在册"13 张整块无 data_binding（含 10-09 20:25 十二张最久积压者多数）"已点名，本班复量＝**同 12 枚仍在 prereg 且仍排在领面序最前**＝五个班未动，而排序规则会把每一班都送到它们面前。⇒⑥ 补绑定块是前置条件；下班领面序改指 10-10 08:14 批起。
- 10-10 批供数侧本班只读卡面（禁跑窗内不查 CH）：X1 族三枚（R1-01/ablation/03・R1-01/comparison/02・R1/shadow/02）的 signal 需 `exit_simulator.simulate` 产出的日净值面＝类 C engine_replay 依赖，不是"两个 csv"能了⇒下班优先 08:14/08:16 批的简单绑定面，勿先领 X1。
- 断供候选交叉（只给候选，真挡须按窗与列在 CH 窗内逐条读，禁按表名命中判）：
   - [18] exit_flow\X1\TDM-X-R1-03__calibration__02_宽基ETF天量与护盘滞后结构 | 表=c1_market.kline_etf_daily | [('kline_etf_daily_shallow_depth', 'open')]

### 四、本班新发现＝缺陷前移（今晚新出 32 枚骨架，其中 17 枚 panel 形双臂题）

- 实测 mtime≥10-17 00:00 的四族卡文件 **32** 枚，逐件 status 全为 **empty**（出生骨架，不在 prereg 面积内），birth_seat=③、三批 00:29／01:13／02:10。
- 形状分账：
   - status=empty kind=panel family=ablation | 1 枚
   - status=empty kind=panel family=comparison | 16 枚
   - status=empty kind=series family=ablation | 1 枚
   - status=empty kind=series family=comparison | 12 枚
   - status=empty kind=series family=shadow | 2 枚
- 关键判读（本班不自欺之处）：这 32 枚 `pillars` 现值＝None ⇒ `pillars_route` 对其返回缺省支 "series"＝**route 现在还判不出来**。本班**不宣称**这 17 枚已落进崩类 (a)；能宣称的是它们按 family 是双臂对照/消融题，一旦按兄弟卡补出 NAV 专有键即翻 dual_arm，而 ⑤ 那条 panel 腿仍未修（§一②）⇒届时无一可考，崩面上限从 28 涨到 28+17=45。
- 17 枚具名：
   - entry_flow\L2\TDM-E-L2-06-1__comparison__02_gate_then_weight_sequence_vs_joint_conjunction_pool_membership.yaml
   - entry_flow\L2\TDM-E-L2-06-2__comparison__02_first_seal_plus_max_consec_head_def_vs_strength_rank_head_def.yaml
   - entry_flow\L2\TDM-E-L2-06__comparison__02_multiplier_step_form_vs_additive_offset_form_rank_flip.yaml
   - entry_flow\L2\TDM-E-L2-08__comparison__02_price_persistence_stage_leg_vs_limit_up_confirm_stage_leg_confusion.yaml
   - entry_flow\L2\TDM-E-L2-10__comparison__02_sector_membership_path_vs_chain_graph_path_candidate_set_and_hump_timing.yaml
   - entry_flow\L3\TDM-E-L3-02__comparison__02_nine_stage_order_permutation_vs_stage_set_membership_pool_stability.yaml
   - entry_flow\L3\TDM-E-L3-03-1__comparison__02_rolling60_event_count_vs_cumulative_event_intensity_rank_flip.yaml
   - entry_flow\L3\TDM-E-L3-05__comparison__02_board_height_only_rank_vs_height_plus_anomaly_strength_rank.yaml
   - entry_flow\L3\TDM-E-L3-07-2__comparison__02_ic_weighted_ham_half_life_vs_flat_mean_weight_sensitivity.yaml
   - entry_flow\L3\TDM-E-L3-07-3__comparison__02_target_caliber_axis_vs_universe_filter_axis_interaction.yaml
   - entry_flow\L3\TDM-E-L3-07__comparison__02_union_from_replayed_labels_vs_single_chain_removal_marginal.yaml
   - entry_flow\L3\TDM-E-L3-09__ablation__02_drop_stale_removal_leg_vs_drop_demotion_leg_on_pool_turnover.yaml
   - entry_flow\L3\TDM-E-L3-11__comparison__02_auction_channel_newly_added_vs_speed_channel_newly_added_split.yaml
   - entry_flow\L3\TDM-E-L3-12-1__comparison__02_cross_sectional_quantile_form_vs_absolute_20pct_line_form_pool_migration.yaml
   - entry_flow\L3\TDM-E-L3-12-4__comparison__02_max_confidence_per_symbol_day_vs_event_count_per_symbol_day.yaml
   - entry_flow\L3\TDM-E-L3-12__comparison__02_four_dim_sum_count_vs_strict_resonance_vs_any_dim_rank_order_split.yaml
   - entry_flow\L3\TDM-E-L3__comparison__02_composite_score_topn_vs_sequential_gate_survivors_pool_set_difference.yaml
- 给 ⑤ 的时序建议（本席不裁）＝在 ③/⑥ 补齐这 32 枚之前修 `_comparison_metrics` 的 signal_kind 分派比之后修便宜。给 ⑩ 的一条事实＝"⑥ 未修 13 枚散文"与"③ 新出 32 枚骨架"并存＝制卡侧在推进、执行器侧未推进。

### 五、本班为何零出分（现测，非引用上班）

- 硬互斥见 §一。零 CH 出分路两条实测均无面：① prereg 162 枚逐卡 `data_binding.derived_series`／`target_series` 命中 **0**；② 目标腿缓存＝按 close/open/panel/fwd/target/mask/ret 关键词扫 `.runtime/tmp` 命中 **0 枚**（信号侧在册件仍在盘：mf_mnp 32,007,191B・mf_pc 2,743,763B・shc_delta_wide・unl_nearest_wide・p07c_ti_chips_winner・conc_90，但无目标面⇒任何一张真分都要 CH）。
- **本班新读（请 ⑩ 排窗内任务书时采纳）**＝窗内班的可产出面不是零：本班的领面纠偏（§三）与缺陷前移（§四）两件都是窗内零 CH 产出的，且领面纠偏直接省下班 12×15 分。上班给的是执行器面分类，本班给的是领面序本身——两班互补，非重复劳动。

### 六、本班自犯一处（另起留旧案，不涂）

- 断供册首版尺＝把 `src/zephyr/data/config/known_data_gaps.yaml` **当 list 迭代**（真身＝顶层 dict，键 `gaps`/`last_updated`）⇒未了账表命中恒 **0**＝把"尺坏"读成"无缺口"，与本席在册红线"0 命中须正对照"同型。改正后现测＝items 85／未了账 42／点名表 45。上班在册读数为"点名表 40 张"，本班 45 张的差＝正则面不同（本班 `\bc\d_[a-z]+\.[A-Za-z_0-9]+` 扫整条 dump），**本席不判谁错，两读各留**。
- 班号三面并集自证（在册教训＝取号只数台账会撞鬼班）＝台账面 1017 仅 01・`.runtime/tmp` 面 p07c_1017_* 仅本班（`p07_1017_02` 系 ⑦A 席 sid 不同物）・心跳面本班起手时 `heartbeat_st-qoder-p07c-1017-02.pid` 不存在⇒本班＝02 号唯一。

### 七、[BLOCKER] 登记（本班 3 枚：高 1／中 2）

- [BLOCKER] 2026-10-17|⑦c席1017-02|流程问题|指令卡领面排序规则"按 mtime 从旧到新取积压最久"把每一班都送到 13 枚整块无 data_binding 的卡面前：本班实测领面全集 121 枚的前 12 位全命中该面＝按序开领会白烧 12×15 分窗；该批系 10-09 20:25 entry_flow/L1 十二枚，10-15 首班已点名、连续五个班未动且仍排最前|docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/ 全 12 枚逐件 data_binding 键缺失（具名在本班台账 §三）＋本班 tmp binding_census 读数 121=108+13|⑥ 席补该 12 枚绑定块（前置条件面）；⑩ 席判是否把各考工席领面序改为"先按 signal_derivation 非空筛、再按 mtime"|中
- [BLOCKER] 2026-10-17|⑦c席1017-02|判据缺失|断供册无在册读取单口，各席现写正则⇒同一条数据两读不等：本席首版把 known_data_gaps.yaml 当 list 迭代（真身＝顶层 dict 键 gaps/last_updated）命中恒 0＝把尺坏读成无缺口，改正后 85 条/未了账 42/点名表 45 张，而上班在册为 40 张；两读本席均留不判谁错|src/zephyr/data/config/known_data_gaps.yaml 顶层键面实测＋本班 tmp gap_cross 改正版读数|① 数据源席或 ⑤ 给断供册一个读取单口（含 status 口径与表名提取规则），各席禁各自现写正则；本席不自建永久件（净零增长）|中
- [BLOCKER] 2026-10-17|⑦c席1017-02|工具缺陷|执行器双臂 panel 腿未修的同时制卡侧在批量出双臂 panel 题：今晚新增 32 枚骨架卡（逐件 status=empty・birth_seat=③）里 kind=panel 且 family∈{comparison,ablation} 者 17 枚，现 pillars=None⇒route 尚判 series（本席不宣称已崩），一旦补出 NAV 专有键即翻 dual_arm 且无一可考，崩面上限 28→45；崩点两面同证＝磁盘面与 HEAD 面 sha16 全等 a8e7c40a1531ee6b 的 calibration_exam.py:557 单路 _comparison_metrics（:561-562 无条件进 _series_metrics、:1049 无条件调用）|本班 tmp newcard_probe 的 17 枚具名（台账 §四）＋docs/03_modules/_domain_backtest/exam_cards/entry_flow/L2/TDM-E-L2-06__comparison__02_multiplier_step_form_vs_additive_offset_form_rank_flip.yaml 样本件|⑤ 在 ③/⑥ 补齐这 32 枚之前给 _comparison_metrics 加 signal_kind 分派（或显式 fail-closed 出 blocked 行）；⑩ 判制卡与执行器两侧的推进次序|高

### 八、本班实耗与收班读数（同帧现测）

- 起手 2026-10-17 02:20:21（首条冷启动命令实测）→ 本节落笔 02:36:27 现测＝**16.1 分**（本班唯一耗时自述，其余读数各自同帧）。
- 本班出分 **0** 张・翻卡 **0**・判据/门柱/冻结值改动 **0**・分数册字节动作 **0**・worktree **0**・子代理 **0**・GPU 未 acquire（全程 IC_DEVICE=cpu）・未 requeue 任何死袋・未 release 他会话 claim。

### 九、开闸工单（04:00 后首八枚逐张拆好的照单面・零 CH・机生件逐字转抄，禁手打）

- 尺＝领面全集按 mtime 升序取前 8 枚，逐张读卡面四件＝要拉哪张表哪个窗／目标面卡面冻结式／宇宙谓词是否申报／是否依赖装置产出（engine_replay 类）。
- 全面积分账（**写入同帧现测**：可算式 108 枚＝领面 121 减无绑定 13）：**panel/series=39・series/dual_arm=7・series/series=62**；其中**装置依赖 9 枚**（需 `exit_simulator.simulate` 日净值或 `strategy_exam.window_metrics` 产出）＝**纯列面可算 99 枚**。
- **前 8 枚里 4 枚是装置依赖面**（WO-03・WO-04・WO-05・WO-07）＝按 mtime 直领会在开闸首小时撞上"两个 csv 了不了"的面；本班建议下班先领 **WO-00・WO-01・WO-02・WO-06** 四枚纯列面（其中 WO-02 需 l2_tick/tick_depth_5 重面，WO-00 的 OOS 到 2026-09-30 需先实测龙虎榜两表覆盖）。
- 供数集中面（108 枚表→卡数 top，一表可服务多卡，先拉大表）：kline_daily_hfq=53／kline_sector_880=26／kline_index=25／emotion_index=12／stk_limit=11／regime_state_anchored=9／tick_data=9／kline_daily=7／sim_trade_log=6／sector_state=6／sector_constituent=6／regime_snapshot_history=5。
- **宇宙谓词一条纪律复量（本班逐字读出）**＝前 8 枚卡面 `data_binding.universe_rule` 实测**未申报者 8/8**⇒按本席 1016-01 在册口径**不套** ST/年龄掩码（套了＝把未申报口径写进永久分数册）；下班勿因为 ⑦A 席掩码缓存在盘就顺手套。
- 工单原文（本班机生件逐字，含每张的 IS/OOS/regimes/pillars 键集/表清单/target 冻结式/装置依赖）：

```
WO-00 | exit_flow\S1\TDM-X-S1-04__calibration__03_席位净卖出派发前瞻收益
      mtime=10-10 08:14 kind=panel route=series pillars=['gap_bucket3_vs_0_20d_max', 'ic_ir_min', 'ic_mean_min', 'mono_spearman_min', 'oos_same_sign', 'regime_same_sign']
      IS=['2022-01-04', '2025-09-09'] OOS=['2025-10-09', '2026-09-30'] regimes={'bull': '2024-09-14..2025-09-09（段界=ch_data.regime_series SMA200 帘子 trend_up 段，裁定#489②，考时按实取）', 'bear': '2022-01-04..2024-02-05（含 2024-01 微盘流动性危机子段的下行段）'}
      tables=['c1_market.dragon_tiger', 'c1_market.dragon_tiger_seat', 'c1_market.kline_index']
      target=forward_5d_excess_vs_000300（未来 5 日相对 000300 超额，主轴）
      universe=(卡面未申报宇宙谓词)
      device_dependency=无（纯列面可算）

WO-01 | exit_flow\S1\TDM-X-S1-04__calibration__04_除权除息参考价分母误判清仓
      mtime=10-10 08:14 kind=panel route=series pillars=['ic_ir_min', 'ic_mean_min', 'misjudge_cost_gap_min', 'misjudge_rate_ratio_min', 'mono_spearman_min', 'oos_same_sign', 'regime_same_sign']
      IS=['2019-01-04', '2023-12-31'] OOS=['2024-01-02', '2025-09-09'] regimes={'bull': '2019-01-04..2021-06-30（流动性牛）', 'bear': '2021-07-01..2024-01-31（贴现率熊+微盘熊）'}
      tables=['c1_market.kline_daily', 'c1_market.kline_daily_hfq', 'c1_market.kline_index', 'c1_market.suspend', 'c3_fundamental.ex_dividend_event']
      target=ex 日破位误判率双臂比（pre_close 臂 / dr 臂）
      universe=(卡面未申报宇宙谓词)
      device_dependency=无（纯列面可算）

WO-02 | exit_flow\S2\TDM-X-S2-02__calibration__02_连续跌停开板概率与次日处置
      mtime=10-10 08:14 kind=series route=series pillars=['ic_ir_min', 'ic_mean_min', 'mono_spearman_min', 'n3_unopen_prob_max', 'oos_same_sign', 'regime_same_sign', 'volume_split_gap_min']
      IS=['2015-01-05', '2023-12-31'] OOS=['2024-01-01', '2025-09-09'] regimes={'bull': '2019-01-04..2021-06-30（流动性牛，战役模板同轴）', 'bear': '2021-07-01..2024-01-31（贴现率熊+微盘熊）'}
      tables=['c1_market.kline_daily_hfq', 'c1_market.kline_index', 'c1_market.l2_tick', 'c1_market.stk_limit', 'c1_market.tick_depth_5']
      target=next_day_unopen_probability（次日开板条件概率，主轴）
      universe=(卡面未申报宇宙谓词)
      device_dependency=无（纯列面可算）

WO-03 | exit_flow\S2\TDM-X-S2-02__comparison__04_T1可卖额度做T回转延迟成本
      mtime=10-10 08:14 kind=panel route=series pillars=['binding_rate_min', 'deferral_cost_bad_median', 'deferral_cost_cheap_band', 'ic_ir_min', 'ic_mean_min', 'oos_same_sign', 'regime_same_sign']
      IS=['2019-01-04', '2023-12-31'] OOS=['2024-01-02', '2025-09-09'] regimes={'bull': '2019-01-04..2021-06-30（流动性牛）', 'bear': '2021-07-01..2024-01-31（贴现率熊+微盘熊）'}
      tables=['c1_backtest.sim_trade_log', 'c1_market.kline_daily_hfq', 'c1_market.kline_index', 'c1_market.stk_limit']
      target=T+0 撞额笔次的顺延执行价差中位与分位数带
      universe=(卡面未申报宇宙谓词)
      device_dependency=['build_signals', 'signals/reb_rows']

WO-04 | exit_flow\X1\TDM-X-R1-01__ablation__03_市场体制条件下熔断减仓增量
      mtime=10-10 08:14 kind=series route=dual_arm pillars=['cost_tier_bp_required', 'decomposition_abs_error_max_pp', 'missed_crisis_trigger_max', 'oos_same_sign', 'orthogonal_maxdd_increment_min_pp', 'regime_same_sign', 'sharpe_delta_min', 'turnover_delta_annual_max']
      IS=['2018-01-02', '2025-09-30'] OOS=['2025-10-09', '2026-09-30'] regimes={'bull': '2019-01-04..2021-06-30（流动性牛）', 'bear': '2021-07-01..2024-01-31（贴现率熊+微盘熊）', 'crisis': '2020-02-01..2020-03-23 与 2024-01-02..2024-02-08（在册危机段）'}
      tables=['c1_backtest.decision_daily', 'c1_backtest.regime_snapshot_history', 'c1_market.emotion_index', 'c1_market.kline_daily_hfq']
      target=both-vs-regime_only 的 OOS MaxDD 净增量（pp）与分解加和误差
      universe=(卡面未申报宇宙谓词)
      device_dependency=['回放']

WO-05 | exit_flow\X1\TDM-X-R1-01__comparison__02_熔断五级梯度减仓对照
      mtime=10-10 08:14 kind=series route=dual_arm pillars=['cost_tier_bp_required', 'maxdd_improvement_min', 'maxdd_improvement_vs_no_hysteresis_min_pp', 'missed_crisis_trigger_max', 'oos_same_sign', 'sharpe_delta_min', 'turnover_delta_annual_max', 'whipsaw_roundtrip_ratio_max']
      IS=['2018-01-02', '2025-09-30'] OOS=['2025-10-09', '2026-09-30'] regimes={'bull': '2019-01-04..2021-06-30（流动性牛）', 'bear': '2021-07-01..2024-01-31（贴现率熊+微盘熊）', 'crisis': '2020-02-01..2020-03-23 与 2024-01-02..2024-02-08（两处在册危机段，T3b 窗+微盘流动性危机窗）'}
      tables=['c1_market.account_nav_daily', 'c1_market.kline_daily_hfq']
      target=OOS 组合 MaxDD / 年化 Sharpe（strategy_exam.window_metrics，244 年化）
      universe=(卡面未申报宇宙谓词)
      device_dependency=['exit_simulator', 'simulate(', 'strategy_exam', 'window_metrics', '回放']

WO-06 | exit_flow\X1\TDM-X-R1-03__calibration__02_宽基ETF天量与护盘滞后结构
      mtime=10-10 08:14 kind=series route=series pillars=['ic_ir_min', 'ic_mean_min', 'lag_median_days_min', 'min_events', 'mono_spearman_min', 'oos_same_sign', 'regime_same_sign']
      IS=['2021-03-08', '2025-09-09'] OOS=['2025-10-09', '2026-09-30'] regimes={'bull': '2024-09-14..2025-09-09（段界=ch_data.regime_series SMA200 帘子 trend_up 段，裁定#489②，考时按实取）', 'bear': '2021-03-08..2024-02-05（含 2024-01 微盘危机子段的下行段）'}
      tables=['c1_market.kline_etf_daily', 'c1_market.kline_index', 'c1_market.market_etf_share_snapshot']
      target=forward_20d_index_return（000300 未来 20 日收益，主轴）
      universe=(卡面未申报宇宙谓词)
      device_dependency=无（纯列面可算）

WO-07 | exit_flow\X1\TDM-X-R1__shadow__02_拔电源影子运行对照
      mtime=10-10 08:14 kind=series route=dual_arm pillars=['cost_tier_bp_required', 'false_trigger_rate_max', 'forgone_gain_max_pp', 'loss_avoided_min_pp', 'oos_same_sign', 'sharpe_delta_min']
      IS=['2018-01-02', '2025-09-30'] OOS=['2025-10-09', '2026-09-30'] regimes={'bull': '2019-01-04..2021-06-30（流动性牛）', 'bear': '2021-07-01..2024-01-31（贴现率熊+微盘熊）', 'crisis': '2020-02-01..2020-03-23 与 2024-01-02..2024-02-08（两处在册危机段）'}
      tables=['c1_market.kline_daily_hfq', 'c1_market.kline_index']
      target=假想净值 OOS MaxDD 改善与错失收益（strategy_exam.window_metrics）
      universe=(卡面未申报宇宙谓词)
      device_dependency=['exit_simulator', 'simulate(', 'strategy_exam', 'window_metrics']
```

### 十、收班八件（02:40:57 现测・本班唯一投袋＝袋①，尾巴由下班承接）

- ①**release 全部 claim**＝本节落笔时本席名下锁面实测 1 把（['    持有者: st-qoder-p07c-1017-02 | 剩余 29.9m｜来源=acquire 原 TTL，ttl=30m']）；本班只写本席两件 _working 件，投袋后由正门 finally 释放，下班仍须按 `lock_files.py list` 复量。
- ②**注销心跳**＝本班不在此节执行（在册无终态面：任何一次 python 调用都会被代起守护，本席 1017-01 与 ⑨ 席 10-17 同记）；交接读数＝keeper pid **24336**（registry present=True・entry_pid=24336・last_heartbeat 秒级新鲜），重复起的 58428 已于 02:30 按 PID＋argv 逐元断言终止（**未按镜像名批杀**）。本班末次网关动作之后由本席以非 python 通道（taskkill 单 PID）终止，终判读 registry 文件撤除，不读 pid 文件（在册教训＝pid 文件恒指已死首枚）。
- ③**实耗**＝起手 02:20:21（首条冷启动命令实测）→ 本节 02:40:57 ＝ **20.6 分**（此为本节落笔同帧读数；§八 那句 16.1 分系该节时点读数，旧文不涂，本班终值以班末袋复量之后的收班末段为准）。
- ④**[BLOCKER]**＝本班 3 枚（§七，高 1／中 2）；写后同帧盘面严式行首计数见 §八 打印面（19→22，含上班尾巴 3 枚未落地行）。
- ⑤**自清收口**＝`.runtime/tmp/p07c_1017_02/` 本班件实测 15 件／221 KB（普查器・工单器・keep 追加器・keeper・分数册备份・读数件）；按小步收班② 于班末删除，方法与读数全部写进本台账（§二／§三／§四／§九），下班据此可在 15 分内重建；本席不在永久区自建工具件（净零增长）。四件套外零散落，项目根零临时件。
- ⑥**GPU 还牌确认**＝本班全程 IC_DEVICE=cpu、未 acquire 看门人⇒免执行，读数不申报为 GPU。
- ⑦**后台子任务清点**＝本班零 spawn 子代理⇒零孤儿；唯一长驻进程＝keeper pid 24336（② 已写明销法与交接）。
- ⑧**零 worktree 确认**＝`git worktree list` 含本席 sid 实测 0 行・`.aidrafts/st-qoder-p07c-1017-02` 存在性＝False⇒本班未调用任何工棚/工作树入口（TRAE-079 Phase 2 遵令）；历史遗留整树一枚未动，交 ⑩/清理专班。
- **分数册三面（收班同帧复量）**＝disk 110 行／HEAD 110 行／本班写入 0 行⇒本班零动作；台账当前盘面 773 行。
- **本班袋申明**＝本班只投一袋（§一—§十），袋终态若未达 done，本班不加投第二袋（在册两难＝同会话后袋在前袋落地后必判双侧皆改而死＋每调一次网关各代起一枚心跳＝收班② 递归无出口）；本班写作时刻之后的尾巴由下班袋承接，下班领面以**盘面**为权威。
## ⑦考工C 班次 1017-03（st-qoder-p07c-1017-03）｜起手 03:50:15・CH 禁跑窗 01:00–04:00 与本班前 10 分重叠、04:00 后开闸・本班出分 1 张（保底双口径均未达，如实呈报）・零改判据/门柱/冻结值・零 worktree・零子代理

### 一、冷启动与交班四查（date 现测，磁盘面为准）

- python 3.12.8；`lock_files.py cleanup`＝CLEAN 无死锁；reaper 03:50:35 实测 source=live・last_run=03:50:25・killed=0 reported=7・degraded False・commit_pct 77.35・ram_used 71.1%・cpu 63.9%・stash_count 27・worktree_changes 1524・dead_archive ok=False rc=1（serializer 租约 pid=47508 存活）⇒ 允许写。
- 班号三面并集自证（在册教训＝只数台账会撞鬼班）：台账面 1017 现有 01・02；tmp 面 `p07c_1017_02` 存在、`p07c_1017_03` 本班新建；心跳面本班起手时 `heartbeat_st-qoder-p07c-1017-03.pid` 不存在 ⇒ 本班＝**1017-03** 唯一。
- 上班 1017-02 袋终态实测＝`commit_queue status --session st-qoder-p07c-1017-02` 回显 state=done・landed_id=0041d793b5d7349c7ceb05c3448f6fe89b52540c ⇒ 上班台账已落地，本席台账盘面 861 行＝HEAD 861 行。
- 上班 §九 开闸工单（首八枚）本班逐条复量：装置依赖四枚（WO-03/04/05/07）本班未领；**WO-00/WO-01/WO-06 三枚本班实测全部落在"卡面 primary 是多日前向面且未成对申报"堵面**（§六 第 1 枚），照领会写方向错误读数 ⇒ 未领；WO-02 需 l2_tick/tick_depth_5 重面，本班窗内未领。
- 上班首查三件回批：① 本班袋终态见 §八；② 上班尾巴面是否被本班带走＝本班袋只含本席 `_working` 两件＋本席翻过的一枚卡，不含分数册（理由见 §八 袋申明）；③ 04:00 开闸后 prereg 面值与供数覆盖＝本班已复量（§二）并按窗与列判据实测 research_report／money_flow 两表（§四・§五）。

### 二、分母实测（本班尺 03:57:46 现测，磁盘面为准）

- 四族 yaml **609** 件；六态加总自证＝preregistered **163**／empty 240／blocked_on_impl 48／blocked_on_data 71／examined 87 → 163+240+48+71+87＝609 ✓。
- prereg **163**（上班在册 162，面值移动 +1）；kind 分面＝panel 80／series 83；绑定层 `classify_card` 面＝C 113／U 27／B 14／A? 7／A 2（加总 163 ✓，D 0）。
- 分数册三面（04:19:49 现测）＝磁盘 **113** 行／HEAD **110** 行／index 面含他会话在途册件；本班写入 1 行（rows[110]），⑦A 席 1017-02 班同期写入 rows[111]（L2-02-2/02）・rows[112] 共 2 行**未落地** ⇒ 盘面-HEAD 差 3 行由两席分别持有，本班不代落他人字节（§八 袋申明）。
- **本班一把尺的空转如实登记**：survey.py 的 route 面取 `card_binding.pillars_route` ⇒ 该符号在 card_binding 内 0 命中（真源在 `calibration_exam.pillars_route`），本班 `hasattr` 兜底使 route_census 全为 None＝**尺缺字段，不是面值真为 None**；本班未据该面下任何结论，正解＝单口取真源不写兜底缺省。
- 断供避让按"窗与列"判、禁按表名命中判（复量上班在册纪律）：`c3_fundamental.research_report` 实测 publish_date 2017-01-02..2026-10-14・rows 294,066・uniqExact(symbol) 4,711 ⇒ 该表在挂 open 缺口的名义下仍有源，L2-09/03 的堵点不在数据而在卡面口径（§五 第 6 枚）。

### 三、本班主产出＝一枚真实入册分（落笔前自证：全册 113 行中 run_id 带 `p07c` 前缀者＝1，即本班这枚；HEAD 面 0）

- 卡＝`docs/03_modules/_domain_backtest/exam_cards/entry_flow/L9/TDM-E-L9-A01__calibration__03_分钟已实现波动.yaml`；run_id＝`p07c-1017-03-l9-a01-03`；分数册 rows[110]（盘 110→111）。
- 双腿＝卡面逐字自物化：signal＝RV=Σ_i(1min 对数收益²) 按 symbol×日聚合后**当日横截面 rank_pct**（卡面 deriv 原文）；target＝`c1_market.kline_daily_hfq` close→t 日实现收益（执行器 `_panel_metrics` 内部 shift(-1) 配对＝卡面 primary `next_day_stock_return`）；卡面 `fallback_table=kline_60min` 属"须卡外声明降精"面，本席不自批降级 ⇒ 只用 1min。
- 取数＝CH 服务端聚合（`groupArray(tuple(trade_time,close))`＋`arraySort`＋`arrayMap` 一次算完，零逐日 `.loc`）；预量实测单月切片 19 交易日 84,755 行 0.8 秒，整窗分四段年拉无超时；判分面形状 894×5,602、信号非空 4,398,604 格、ic_days 893、日均配对名数 4,914.4、最小 0（末日无 t+1 配对）。
- 读数：ic_mean **−0.0639176**／ic_ir **−0.461335**／oos_ic −0.0603619／n 893／regime_ic bull −0.0697432・bear −0.0675592・recovery −0.0591563（三段同号负）。
- verdict＝**fail**；fails 两条逐字＝`ic_mean -0.0639 < 0.02`／`ic_ir -0.461 < 0.3`；unjudged 面＝mono_spearman 无面（panel 路恒 None）＋散文柱 five 条（half_life_note/ic_floor/lag_profile/regime_stability/response_monotonicity）。
- 纯加与落盘自证：difflib **minus=0**／plus=36／rows 110→111；CAS promote written=True・before_sha a9532fceb0899c94・after_sha d2bba893ea2fdb2d・equals_staging=True；卡由 `run_card` 本体翻 status=examined 并写 lineage.run_id＋score_row=`exam_scores_v1.yaml#rows[110]`（本席未手写卡面 status，亦未前置翻 examining）。
- 本枚实耗＝**2 分 34 秒**（04:06:47→04:09:52 同帧现测，含占卡/双腿/判分/promote）。
- **一条方向性发现（本席不裁，呈 ⑥/⑨）**：本枚实测三段同号负 IC＝卡面 hypothesis 自己预期的方向（"高 RV→不确定性抬升→次日折价（负 IC）"），而卡面 `pillars_numeric.ic_mean_min: 0.02` 是**正地板**、散文柱 `ic_floor` 写的是"均值**绝对值** >= 0.02"⇒ 同一张卡内数值柱与散文柱方向互斥，执行器按数值柱判，方向正确的读数被记 fail。同族第二例＝上班游标在册的 `TDM-P-P1-04/calibration/04`（冻负地板）；本席不改判据，只报两柱原文与实读数。

### 四、本班第二枚尝试＝活跑坐实残留崩面＋一处本席尺错自纠（零副作用）

- 卡＝`entry_flow/L9/TDM-E-L9-A06__calibration__02_主力净流入截面.yaml`；error＝`DateParseError: Unknown datetime string format, unable to parse: 2019-2021H1 牛段 money_flow 无数据…`（与 ⑦A 1016-03 那次同源）。
- 副作用面 04:14:20 复量＝卡 status 前后均 **preregistered**・lineage 三键均 null・分数册零动作、卡锁已 RELEASED ⇒ 崩在判分之前；本席"不前置翻 examining"的工序选择避免了 ⑦A 1016-03 留下的孤儿 examining 形态（上班游标首查④项同源）。
- 与 ⑦B/p08-1017-04 [BLOCKER]（"恰一枚 ISO 日期"那一支 CRASH 而不拦）＝**两把独立尺同判**（彼＝三态探针，彼＝读码；本＝活跑）；⑤ 今日 commit e7dada4fe5 自述"把 13 枚卡的装载崩根治成诚实不可考行"的实测覆盖面＝**零枚日期**支（本班另测 iso=0 面 prereg 8 枚），非"≤一枚"支。
- 本班自尺面积（04:21:10 现测）＝prereg 按 regimes 最小 ISO 日期枚数分面：≥2 枚 **147**／恰 1 枚 **5**／0 枚 **8**；**恰一枚 5 枚与 ⑦B 在册 prereg 5 枚逐值相等**（两席独立同判）；**加总 160 ≠ 163，差 3 枚＝本班这把尺未覆盖（no_regimes 计数 0 而差仍存）**，本席不补判、如实留差，下班若要该面请先把尺补全（可能是 window 缺段或解析异常件）。
- **本席一处判案错（另起留旧案不涂）**：04:11:15 本班曾以 `_span_pairs(card.regimes)` 返回 2 枚 span 判"⑤ 腿已生效⇒L9-A06 可考"并据此起批——活跑证伪。根因＝`_span_pairs` 不是崩点消费面（崩在 `_in_spans` 遍历 `regimes.items()` 无键名过滤），且本班那次探针自身参数序写错抛 TypeError，被本班误当成"无异常"证据链的一节。正解＝判崩面只认活跑或消费点探针，**存在性/局部函数返回≠内容判据**（在册红线复现，本席自犯第 N 次登记）。
- 该卡另有第二重不可考＝数据面无源：`c1_market.money_flow` 判分窗 2021-01-04..2025-09-09 实测 5,509,521 行中 **pct_change 非空非零 0・close 非空 0**（main_net_inflow_pct 5,495,405・super_large_net_inflow_pct 4,129,051）⇒ 卡面申报的 OLS 回归元在申报表内取不到，本席实跑 resid 非空格＝**0**；本席不自拟替代价源（那等于把卡面冻结的回归式换到另一张表的构造），转 ⑥/①（§六 第 3 枚）。

### 五、本班可跑面穷尽审计＝严格可跑 7 枚，逐枚堵因具名（下班勿再逐枚烧窗）

尺（本班自设五谓词，全部可从卡面复核）＝primary 命中 `next_day` ∧ 不命中多日词 ∧ 全部 regime 值 ISO≥2 枚 ∧ 桶名在执行器 8 词表内 ∧ data_binding 有可算式 ∧ 不挂"两路合成分/共用重算" ⇒ **7 枚**（含本班已烧的 L9-A01/03）：

1. `entry_flow/L0/TDM-E-L0-02__calibration__03_偏离幅度分位响应曲线`＝需 kline_etf_1min 盘中实际暴露代理＋盘前边界（组合层构造），非纯列面；
2. `entry_flow/L1/TDM-E-L1-AGG__calibration__03_子信号族到状态轴传导保真度`＝**主柱对象被换**：卡面 `numeric_face_mapping_note` 冻结 mono＝(三腿合成分秩, AGG 状态档序秩)，而执行器 series 路 mono＝分桶×前向收益中位单调 ⇒ 出分即非卡面命题；
3. `entry_flow/L2/TDM-E-L2-01-2__calibration__02_板块成交额占比活跃度`＝其 "series 面"定义本身含 t+1 收益（"占比前 10% 板块等权组合的次日超额与全样本差"），作信号＝前视；
4. `entry_flow/L2/TDM-E-L2-05-1__calibration__02_水温档读数与月级封顶`＝"月级允许上限"表卡面只钉死"熊市反弹→降为温"一条，余 6 态上限＝考工自批；
5. `entry_flow/L2/TDM-E-L2-07-1__calibration__03_死常量两腿_结构破坏与超窗横盘`＝卡面自相矛盾：`signal_kind: panel` 而 primary 注"series 面，执行器 shift(-1) 现器可考"、buckets.on＝板块×日的 S（panel 主对象）⇒ panel 路要 panel 目标，本席无合法单列注法，转 ⑥ 定形；
6. `entry_flow/L2/TDM-E-L2-09__calibration__03_评级上调聚集`＝"series=行业**加权**均值"（deriv）与"市场级取行业**均值**"（buckets.on）两措辞互斥且权重未定；卡面另自注行业宇宙漂移须登记名单版本；
7. `entry_flow/L9/TDM-E-L9-A10__calibration__02_全球风险隔夜传导`＝"signal＝日变化率**或** z-score(60 日)"二选一未钉＋五指标合面权重未定。

⇒ **下班勿把这 6 枚当可考面领**；每一枚要出分都得考工席自定一处卡面未钉口径＝往永久册写假陈述。另：多日前向面 20 枚见 §六 第 1 枚闸口；恰一日期面 5 枚见 §四。

### 六、[BLOCKER] 登记（本班 5 枚：高 2／中 3）

- [BLOCKER] 2026-10-17|⑦c席1017-03|判据缺失|执行器对"卡面 primary 是多日前向面且未成对申报 target_forward_face+target_horizon_days"的卡**静默退化成次日面出分且分数行零披露**＝`_forward_face` 现读 face=="" ∧ hraw is None ⇒ return (1, False)，非次日面的读数被当成卡面主柱成绩写进永久分数册；面积实测＝prereg 163 枚中 primary/target_source 命中多日前向词 **20 枚**、其中成对申报 **0 枚**；上班 §九 工单 WO-00/WO-01/WO-06 三枚全落该面（本席据此未领，照领即写方向错误读数）|尺面 `.runtime/tmp/p07c_1017_03/survey.json` 的 all[].primary＋data_binding 逐枚正则读数（多日 20／申报 0）与代码锚 `scripts/backtest/fexam/calibration_exam.py` `_forward_face` 缺省退 1 一支・`_series_metrics` shift(-1)・`_panel_metrics` shift(-1)|⑤＝把"primary 含多日词且未成对申报"改成像非在册 face 那样 `_ToolError` 拒出分（＝改喂闸的输入形态，不弱化闸、不加白名单、不开新豁免）；⑥＝该 20 枚补成对申报位；⑨/⑩＝补位前禁任何考工席领多日卡|高
- [BLOCKER] 2026-10-17|⑦c席1017-03|工具缺陷|⑤ 今日 e7dada4fe5"regimes 诚实行"腿的实测覆盖面窄于自述＝"恰一枚 ISO 日期"那一支本席**活跑**仍 DateParseError（卡 L9-A06/calibration/02，错误串与 ⑦A 1016-03 同源），消费点 `_series_metrics`/`_panel_metrics` 遍历 `regimes.items()` 无键名过滤；与 ⑦B/p08-1017-04 三态探针同判＝两把独立尺同判；本席自尺面积＝prereg 面 ≥2 枚 147／恰 1 枚 5／0 枚 8，其中"恰 1 枚＝5"与 ⑦B 在册 prereg 5 枚逐值相等|本班 run.json L9-A06 条 error 字段逐字＋卡 status/lineage 04:14:20 复量（preregistered・三键 null＝零副作用）＋`.runtime/tmp/p07c_1017_03/iso_face.json`|⑤＝把拦条件从"零枚"改成"<两枚且整串非纯日期"，或对注记类键名（*_note）不入段——属实现面 fail-fast，不动判据；⑦c/⑦A 两席在飞领面序在修前均避开该 5 枚|高
- [BLOCKER] 2026-10-17|⑦c席1017-03|数据问题|卡 L9-A06/calibration/02 的两个回归元在申报 signal_table 内无源＝`c1_market.money_flow` 判分窗 2021-01-04..2025-09-09 实测 5,509,521 行中 pct_change 非空非零 **0**・close 非空 **0**（main_net_inflow_pct 5,495,405・super_large_net_inflow_pct 4,129,051 有源）⇒ 卡面 OLS(main_net_inflow_pct ~ pct_change+20 日动量) 按申报表取不出残差（本席实跑 resid 非空格＝0）；⑦A 1016-03 同形制装配器当年崩在 regimes 之前，故该缺源面从未暴露|CH 实测三列 countIf 读数（04:14:20 现测）＋本班 run.json L9-A06 legs 行 resid_cells=0|⑥＝该卡把回归元显式绑到含该列的表或改 signal_table；①＝money_flow 的 pct_change/close 两列是否属采集缺口（可补则该卡恢复原申报）|中
- [BLOCKER] 2026-10-17|⑦c席1017-03|流程问题|指令卡占卡工序原文 `lock_files.py acquire <卡路径> <sid>` 两参数形态互斥实测 **0 秒**＝锁按 acquire 那次 CLI 瞬时 PID 判活、命令一退即 stale，他席 acquire 或 `cleanup` 都能静默回收在岗席的锁；本席按内存 claim-mutex-zero-window 补 `--session <sid>` 后实测回显"会话绑定: st-qoder-p07c-1017-03（裁定#252）"；全线八张自动化指令卡仍是不带旗形态|`scripts/lock_files.py` acquire 支现读（`bind_session = _parse_opt(args, "--session")` 只有给旗才写 session_id）＋本班 run.json 两次 lock.out 逐字对照|⑩＝更新考工 A/B/C 三席指令面与 SOP §3⑦ 占卡工序为"三参数＋--session"；本席未改判据亦未自建永久工具件（净零增长）|中
- [BLOCKER] 2026-10-17|⑦c席1017-03|工具缺陷|`lock_files.py acquire` 收到非仓根可解析路径时报"NAMING VIOLATION 命名不合规（N-01 连续大写字母／N-13 非 snake_case）"而非"路径查无"＝把考工引向"给在册合规卡改中文名/改名"方向（＝资产破坏向量）；本席首跑传卡目录相对面即中招，被拒对象正是 `TDM-E-L9-A01__calibration__03_分钟已实现波动.yaml` 这种在册合规命名件，改仓相对全路径后同一把锁立即 ACQUIRED|本席 tmp run.json 04:06:54 那次 lock.out 逐字＋04:07 手动全路径 ACQUIRED 对照＋04:09 活跑成功|⑤＝命名闸前先判路径可解析性，查无路径报 PATH-NOT-FOUND 类错误码，禁把路径问题升格成命名问题；本席不改工具|中

### 七、为何本班不硬凑到 8 枚（承重证据，非态度陈述）

- 保底口径＝出分 1＜8 且未跑满 4 小时（班限 90 分）⇒ **双口径均未达，如实呈报**。
- 面积账：prereg 163＝可忠实消费且本班已烧 **1**／严格可跑但卡面口径未钉 6／多日静默退化面 20／恰一日期崩面 5／零日期（⑤ 新腿可出诚实 blocked 行）8／其余 123＝C 类目标面（`target_face_not_index_next_day` 族）与装置依赖面，前四班已逐形制定性、本班复量面值未动。
- 那 6 枚若强出分，每枚都要考工自定一处卡面未钉的口径（权重/上限表/主柱对象/前视面定义）＝往永久分数册写假陈述；本席在册红线（考工自制册格＝自批勿越）禁之。
- GPU：本班**未 acquire**，且实测 `run_card` 出分行**无 device 字段**（`device_ledger` 只在 `conditional_exam.py:515`／`ic_exam.py:249,447`／`strategy_exam.py:333` 三条批量路存在）⇒ 指令卡"[⑦-新] device_ledger 记实际用芯"对考工 run_card 路不成立；本班收班⑥按"未 acquire＋无 ledger 落点"如实登记，**不申报用芯**，禁把回退报成 GPU 读数。

### 八、本班实耗与收班读数（同帧现测）

- 起手 2026-10-17 03:50:15（首条冷启动命令 date）→ §八 落笔现测见打印面；本班唯一出分枚实耗 2 分 34 秒，另第二枚尝试（崩面活跑）1 分 37 秒含双腿装载。
- 本班袋申明＝只投一袋，件面只含 `docs/_working/automation_campaign/p07c_examiner_c/ledger.md`・`checkpoint.md` 与本席翻过的 `entry_flow/L9/TDM-E-L9-A01__calibration__03_*.yaml`；**不含分数册**＝分数册盘面 113 行含 ⑦A 席 1017-02 班未落地的 rows[111]・rows[112] 两行，随袋即归属篡改（在册红线）；后果与待办如实登记＝本卡 lineage.score_row=rows[110] 在 HEAD 册面暂为悬指，待持册者落地即闭合，本席不代落、不自 drain、不 requeue 他人袋。
- 纪律面＝本班未建 worktree（TRAE-079 Phase 2）・未动他席指令面・未 requeue 任何死袋・未代复位孤儿卡・未 release 他会话 claim・未动判据/门柱/冻结值/桶数・分数册 only-add 一行且纯加自证 minus=0。
