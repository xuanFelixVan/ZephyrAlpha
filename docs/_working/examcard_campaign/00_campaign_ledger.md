---
ttl: task_bound
title: 考试卡+断言治本双战役作战台账（st-examchief-20261009）
created: "2026-10-09"
sid: st-examchief-20261009
family_id: EXAMCARD-CAMPAIGN
---

# 作战台账（随进展追加）

## 车道状态板（2026-10-09 21:00 快照）

| 车道 | 状态 | 凭据锚点 |
|---|---|---|
| W1 F06 治本 | ✅根因钉死+修复+蓝探针绿；彩排批A 计算中（py-spy 实证 active，非挂起）；正式验收=10-11 周六窗 | 01_w1_f06_root_cause.md + w1_evidence/ |
| W3 骨架生成器 | ✅核心闭环：186/186 覆盖、重跑零 diff、only-add+手工卡保护（10/10 测试）；户口五合一已办 | MOD-BT-241；tests/backtest/test_generate_exam_card_skeleton.py |
| W4 20 卡预注册 | ✅20 张预注册卡落盘（看数前冻结，零数据窥视）；**分数面阻塞**：前置② dexp TI 读侧确定性修复未落 HEAD（argMax 第三路 git log 零命中）——如实登记阻塞非跳过 | exam_cards/entry_flow/L1/*__calibration__0[2-8]*.yaml |
| W5 confidence 闭环 | ✅裁定#501 冻结 v1 判据+回写器落地（13/13 测试）；实弹演示随 W4 首分 | MOD-BT-242；裁定#501 |
| W6 Qoder 云模型 | ✅实弹达成：LLMGateway 增 qwen provider（G1-1 内收零新模块），经 LSG 全链真云调用一次（qwen-flash 1250ms"链路正常"） | src/zephyr/infrastructure/pipeline/llm_gateway.py |
| W7-① fexam 搬家 | ⏸避让延迟：横跨 4 本热册（3 本可能总队在持）——总队队列落地后执行 | 本表 |
| W7-②③ | 候补（dataset_registry 立项/lockfile 钉扎） | 方案 §7.5 净零候补位 |
| F1 lookup state | 🔨子代理施工中 | agent 报告待回 |
| F2 边界登记 | ✅offzone_retrieval_boundary_sop.md 落盘（裁决 b 案） | library_sop/ |
| F3 触发面 | ✅trae_065 v1.1.0+裁定#499 | rules/trae_065 |
| F4 挖矿 SOP | ✅mining_sop_policy v1.7.0 §7.5 | mining_sop/ |
| F5 复盘入册 | ✅CASEBOOK-010 开册+case 0 首录（裁定#500）+prereg 三元组结构落地 | casebook_registry+asset_assertion_cases.yaml |
| W2 GPU 摊销 | ⏳等批A 完成取真全引擎 s/格（热点复测①）；L1 实测已大幅跑赢 L2 设计预期（0.061-0.606s/格纯 pass vs 推演 11.7s），若全引擎 ≤3.5 则按架构册 §六停手条款登记判定，不为饱和而饱和 | p1_wiring_benchmark.md |

## 排队与提交账

- q-20261009-st-examchief-20261009-0001（W1 件 7 文件，含 token 册补 3 条 quant_methodology 修复）已入袋，传送带消化中。
- 待投批次：W3 生成器+186 卡册+2 测试件；W4 20 卡；W5 回写器+裁定#501；W6 llm_gateway；F 文档批（F2/F3/F4/F5+裁定#499/#500）。
- token 工具 HEAD 基底自检在 W1 件落地前会拦（补回 3 条在 W1 批里）——投递序=先等 W1 落地。

## 阻塞与升旗

1. W4 分数面/前置②：dexp argMax(ingest_ts) 第三路未落 HEAD——20 卡分数建立在任意版本指标上的风险未排除，禁开考分数面。
2. W7-① 热册避让：等总队（st-chiefc）队列消化。
3. 批A 时长：全引擎旧路径 ~35s/格推算，census-extend 剩余格数决定收窗时点；不干预（他会在途 CH 负载为 main 因素，reaper keep 在册）。

## 追记（2026-10-10 早）：主袋清障动作账

- st-fig16-20261005（10-05 老会话，零活进程实证）的暂存件 panorama_alignment_gate.py（+25/-13，63 行 `__all__` 缺 Final 触发 MUTABLE-CONST-WITHOUT-FINAL 全局门）封死全仓直落通道。
- 处置=git restore --staged 单文件退栈（**三态验证零丢失**：worktree==index，内容全留工作树，其回来 re-add 即可恢复）；未代改其代码（§3.4）；本条即登记。


## 追记（2026-10-10）：W4 首分开考+W5 判据实弹

- **前置②解除**：dexp 0060 落 HEAD（indicator_reader argMax ×4，总统筹验真同数）。
- **首卡开考**：TDM-E-L1-S1/02_指数趋势位置（kline_index 000300 全窗 1880 行，与冻结窗 2019-2023 IS+2024-2025.09 OOS 完全匹配；信号=MA20/MA60 复合三态档位，序数桶型 runner 回退已补）。**verdict=fail**（ic_mean=-0.0013<0.02、OOS 反号 IS-0.0013/OOS+0.0445；桶序单调 1.0=三态平凡序）。**负结果如实入 exam_scores_v1.yaml**（预注册纪律：门柱冻在先跑分在后，fail 行不迁移 confidence=W5 判据机判实弹正确拒绝）。
- **数据面断供新发现**：c1_market.limit_up_down 仅覆盖 2026-07-20 起（5397 行）——广度面 6+1 卡冻结窗（2019-2025）无数据，需源回补（接 HANDOVER 断供修复工单族）；波动面 IV/宏观事件表待接。20 卡可立即开考面=指数族；广度面候源回补后按各自冻结窗开考。
- **N 账本 CAS 告警**：TrialLedger 记账撞注册表族保护 ×10（热册竞态），ledger_warning 已如实入分数行（不吞考试结果）——转维护班面。
- **runner 顺手修**：序数分桶回退/窗口边界 Timestamp 化/行情段日期正则解析（含中文段注容许），测试 7 passed。

## 追记（2026-10-10 晨）：追加令执行账

- **R3-B5 停呈**：X-R1-03 查证命中保留面①（护盘资产定向加仓白名单：熔断期窄门+总资金 5-10% 预算+position/core 实盘面）→立即停，呈 Owner。
- **R3-B2 口径查证收口**：E 道（2025-10..2026-09 深回撤年/无止损 MaxDD -57.56%/止损必触发）vs T3b（2020-02/03 CRISIS/覆盖 0.35%/27 对）=情景区+覆盖率混杂，双测量各自内部有效；三坑过检。裁定#505 入 PG 账本（#503 撞号让位、#504 他班占用、#505 取号登记 v16）。
- **R3-B1 冻卡**：双窗锚定卡两张（X-S1-03 止盈族/X_tp 维、X-S1-02 止损重考/X_stop 维新考卷——旧 T3b FAIL 存续 G4-5）门柱看数前冻结；X_sector 命名缺口（草案无此维疑 X_ladder）挂 Owner 确认；B3/B4 跑数三件套齐才动（fire_grid fail-closed 在守）。
- **R8**：famex v2 维持暂缓；标定判据预注册=下一步（3 条非 state 先例派生，判据立不起=停呈）。
- **T5 三态现测**：见下。
- **T5 判定=继续避让并登记**：活进程零占用+fs 目标位空闲，但四本引用目录（trial_ledger/factor/technical_indicator/capability）现归 regsolo 单口写面活跃管理（capability/ruling/translation 三册本会话全程目击其单口写）——引用改写应提交该通道而非直改；搬家本体（git mv 31 件）候通道窗口。

## 追记（2026-10-10 晨二）：X_sector 命名取证定谳+R10 治本+门柱三件

- **X_sector 定谳（批复退回件，证据定谳非上报）**：index.md:85 原文"schema 增维（X_stop/X_tp/X_sector 等）须裁定"=三维并列各有实义；X_sector=**板块传导维**（sector_propagation_wiring_v1.md:40,67：sector_surface.py 新件+`X_sector=['off','strength_top15','conduction']`，沿 X_stop/X_breaker T3b 先例），与 X_ladder（X-S2-05 分批止盈 Exit Ladder）**异物非同名**。追加令三维授权指向成立；X_sector 开维施工（新件+schema 增维）=独立批次，不在本次两张冻卡范围（已冻 X_tp/X_stop 正确）。
- **R10 治本+补记**：根因=TrialLedger CAS 的 yaml.safe_dump 往返丢他会话新增注释块（13 行非条目）触发注册表族 mass-edit 保护误拒。治本=条目级无损断言（_entry_fingerprints：旧 batch_records/screen_runs 键集 ⊆ 新集）+断言过则 allow_mass_edit 放行（保护意图=防条目蒸发，注释损失由断言兜底）。补记入账 ✓（examcard:TDM-E-L1-S1/02_指数趋势位置:2026-10-10），测试 15 passed。
- **G1/G2 实施**：净费参数入 exam_scale_cost_gate.yaml 唯一参数面（net_fee 节，禁硬编码）；校准器出分附净费桶读数（net_bucket_medians）+换手计量（signal_turnover_daily，只计量不判罚）。
- **G3**：缓行登记（触发器=总资金≥300 万或外部资金接入；缓行期禁预立阶梯门柱）。

## 追记（2026-10-10 午）：二号收口令执行账（st-examclose-20261010）

- **归属协调+W1 claim（先到登记）**：原二号 st-examchief-20260909 无会话目录=不在岗；备袋会话 st-examchief-20261009 心跳末条 2026-10-10T02:31:35Z exited（idle 超时）。无活口，本会话接手二号余件并 claim 今晚 23:00 W1 F06 窗验收。
- **T1 清窗实测=翻动未止（停投分支）**：观测窗 11:16:05→11:33:28；capability 册 worktree 11:32:21 被旧形态渲染覆写（无 GENERATED 头/键序旧形，对 HEAD +832/-790 reflow 残留），11:32:52 index 被写回 HEAD 正典态（index mtime 08:46→11:32:52）；gate_audit（allow_overlap_usage/obj_s_env_denial/registry_mass_deletion_foreign_staged 35MB）11:25 仍在写。与 11:26:18 队列落地（q-20261010-st-fwin-exec-20261009-0004，GW overlap+multi-domain+tracked-drift 留痕）同窗同现；stash_notice 所记 09-30 侧 stash 含 capability/translation/architecture 三册旧形（本仓无 stash reflog，该通知=陈旧文档）；与 disk_reorg 台账「蒸发战争：stale-index 并发提交回退他人内容今晨三起」同源。写入 PID 未能逐个钉死（无 stash reflog、无 hook 写审计命中）——系统级根因=共享暂存区落地周期复活 stale 形，归维护班根治面。按令登记上报，不硬投。
- **R3 袋实况=半数载荷已过时（第二停投理由）**：袋 231 件仅 11 件对 HEAD 有差，其中——①双窗卡 token 两条已在 HEAD 正典投影在册（merge_evaluation=「R3 离场族双窗冻卡（裁定#505）归 exam_card 族」×2），capability 册携带=纯渲染 reflow 零内容增量；②7 张 L1 卡 staged 形=examined→preregistered 回退+run_id/score_row 置 null，与 exam_scores_v1（17 行 fail 实录，nightmine 05:07-08:56 实跑在案）相抵，落地=数据倒退；③真剩余增量=calibration_exam.py（+30 未暂存，chief 末笔）+本台账段+2 件 ruff 修复（writeback SIM300/skeleton I001，修后 46 测试全绿）。建议：袋作废重 derive（剔三册与 7 卡，仅余真增量件），候翻动根治后走正门。
- **T4 巡检收账**：W4 分数册 17 行全 fail（如实入册，预注册纪律）；W5 零 PASS（回写器候面不动）；W2 批A 16h+ 仍在算（19:17 到限先杀，全引擎 s/格 标定取数大概率落空=如实不动）。
- **W1 验收安排**：19:17 彩排批（PID 32284 wrapper+50252 python，10-09 19:16:58 起）到限先杀不占窗位（F06Grid state=Running 在位会顶掉 23:00 自然触发）；23:00 自然窗按冻结门柱（manifest.csv 有产出且 rc=0）验收；红=五层证伪链取证上报，禁现场改判据。

## 追记（2026-10-10 15:1x）：守望面重大更正——批A 死亡与 trigger 搬迁全部有名主（st-examclose-20261010）

- **14:58 守望实查批A 进程已消失**→深挖定谳：非杀手、非事故，系 st-nightmine2-20261010「夜矿续战令三连裁③」裁定手术（commit 723a6a10a9 12:11，adjudicator 署名+队列 GW 全留痕）：批A（grid_20261009-191707）16.7h 零 manifest、44.8s/格超停手阈值 12.8 倍→作废入 N 账本（6000 试次宁严勿宽入计），三进程 50252/25712/32284 由其亲停，「现场释放避开 10-10 23:00 W1 窗（OD-5 叠跑教训）」。backfix 班杀手案（案#5-#7：短命 spawner→stdin 喂码 python 杀 backup 族）与本面无关，仍由其追凶；reaper_kill.log 对 50252 零命中（reaper 再证无罪）。
- **T3 窗位被裁定搬迁**：F06Grid 计划任务 trigger 23:00→Sat 08:00（任务 XML 12:07:34 改写、启动器与 register 脚本同 commit 12:11 落账）；f06_grid.enabled→false，f06_grid_v2 重冻结（n_samples 6000→1000 同 seed 前缀可比、判据面零变动=manifest+rc、window_discipline=Sat 08:00 起跑/22:30 硬收窗禁跨 23:00）。**冻结门柱（manifest+rc0）本身未动**，但「今晚 23:00 自然火」已被 v2 纪律合法取消（禁跨 23:00；首个 v2 自然窗=2026-10-17 08:00，今晨 08:00 已过）。
- **T3 处置=按预注册纪律改旗不投**：本令原钉「今晚 23:00 自然验收」与三连裁③构成先后令冲突，后至且经裁定并有 commit 原子的 v2 安排为准——今晚 23:04 本会话仍到窗取证（预期=无 fired 行+任务 Ready/next 10-17 08:00，如实记录=窗位合法空置），**不手动点火自证**；验收改指首个 v2 自然窗（10-17 08:00 起/22:30 硬收窗），改指生效候 Owner/总令确认。19:17 自动化顺延为无害核账（批A 已死，仅验任务态+落账）。

## 追记（2026-10-10 17:20）：批 A 终局验尸+收口时刻表

- **批 A 终局**：10-09 19:17 起跑 → 2211 warnings（≈1105 格评估）→ **10-10 11:59 最后输出** → 静默 5.2h → **17:10 进程消失**。无 exit 行/无 manifest/无 traceback/reaper 击杀日志 11:56-17:10 无本批记录（keep 名册在册未杀）。**死因=未知（新失败形态：长静默挂起后无声消失）**，与已治本的 stderr 地雷（wrapper 层，已修）不同层。证据保全：.runtime/logs/f06_grid.log（原始捕获）+空 grid 目录+task rc=1。
- **19:17 顺延无害核账=提前完成**：批已于 17:10 自灭，19:17 的 P1D 击杀无对象；无害核验 ✓=无 manifest 无半成品无账本污染（grid 目录空、N 账本仅我 R10 补记一条）。
- **排程改指已生效**：F06Grid NextRunTime=2026-10-17 08:00（v2 首窗，与批复改指一致）；10-10 23:00 位=合法空置。
- **收口时刻表**：①**23:04 到窗取证**——grep f06_grid.log 应无新 fired 行（排程已改指，空置=合法），照实记录；②**00:30/07:00 终判收口**——终检 log+任务态+grid 目录，按批复口径记录；③**W1 验收改指 2026-10-17 08:00 v2 首窗**（候 Owner 确认中）——判据面不变=manifest+rc=0，v2 管线就位后按原冻结门柱验收。
- **批 A 遗产**：≈1105 格 census-extend 计算量已沉没（无产物落盘=不可回收），v2 首窗前建议=长跑挂起段加心跳/分段 manifest 落盘（防 11:59 型静默损失再发）——v2 设计输入，非本班施工面。

## 追记（2026-10-10 19:1x）：彩排批到限处置=落空为核账（st-examclose-20261010·19:17 自动化轮）

- 19:17:41 实查：彩排批 32284/50252 死透（无 batch A exit 行=非自然完成；12:0x nightmine2 裁定手术亲停，见本日 15:1x 段）；F06Grid 任务 state=Ready、next=2026-10-17 08:00（v2 窗纪在位；本自动化原文预期 next=23:00 已被 15:1x 更正段合法替代，如实记录）。今日日志段 FutureWarning=2211 条（彩排批遗产，兼证 PS 地雷修复后 stderr 无害流通——治本面旁证）。
- **新发现（只记录不干预）**：今日 18:38 与 19:16 两个新 grid 目录（grid_20261010-183819≈90KB、grid_20261010-191646≈3.5KB 进行中）；19:16:37 起 python 2584=factory_grid_executor **--n-samples 200**（同 seed 20260916），父=另一活会话的 ZCode exec bash 快照（52196）——他班在途探测性小跑，非彩排批、非 19:17 杀令对象，按「他会话在途不干预」纪律不动；其与 22:30 硬收窗/禁跨 23:00 纪律的相容性归其属主自证。
- 处置结论：19:17 杀令落空为核账（对象已死，无事可杀），与 15:1x 更正段预期一致；今晚 23:04 窗取证照旧（预期无 fired 行=窗位合法空置）。
- 清障附记（19:2x）：本段首次提交被 MUTABLE-CONST-WITHOUT-FINAL 拦——无主外来 staged 件 src/zephyr/gov_enforcement/commit_gates/registry_yaml_parse_gate.py:88（`__all__` 缺 Final；19:16 registry_ledger 修复班 0fa47f5b5e 落地后属主无活跃片，门自判无主）。按门自附处方+chief 晨间 panorama 同款先例：单文件 `git restore --staged` 退栈（worktree 内容 +4/-58 全留，属主回来 re-add 即恢复，未代改其代码 §3.4），本条即登记。

## 追记（2026-10-10 19:4x）：提前窗知会（总统筹 19:30）

- Owner 加速令激活提前窗：GPU 喂饱班影子对照绿 ⇒ F06 任务改 **2026-10-11（明早）08:00** 起跑；若影子对照未绿则维持 10-17——**以任务 NextRunTime 现值为准**。
- 本班口径同步：23:04 取证口径不变（23:00 空置合法照实记录）；验收跟踪窗随 v2.1 窗纪注记改指（NextRunTime 现值为权威）。
- **NextRunTime 现值实证=2026-10-11 08:00:00**（提前窗已激活，影子对照绿确认）；值守自动化升格四时点=23:04 取证/00:30 勘误/07:00 窗前终检/08:05 起跑确认（manifest+rc 终验归日班）。

## 追记（2026-10-10 20:55）：W1 v2 提前窗开考令四步执行账

- **①启动器复位**：git checkout HEAD -- scripts/tasks/run/run_f06_grid.ps1，hash 复验 worktree==HEAD（609be76de01beb82）✓。v2 版窗口纪律=**22:30 当日绝对钟硬收窗**（文档语义，引擎体无钟守卫——纪律属运行面）；batch A n 降 6000→1000（f06_grid_v2 重冻，search_space_prereg.yaml）；批 B 语义不变。
- **②触发器换装**：删 10-11 08:00 一次性触发、设今晚 21:00 一次性（自然点火禁手动 run）✓ NextRunTime=21:00。注：原周六 WeeklyTrigger 已被前序车道换掉（10-11 08:00 TimeTrigger 顶替态）——v2 常规周六窗位恢复=考后事项登记。
- **③值守换装**：自动化 automation-307e3219 改 W1 今晚窗值守（21:05 起跑确认→5 分钟轮询三判定谳→22:30 硬收核）。
- **④CH 让路通知**：本台账段+队列可视面为准——矿考班 21:00-22:30 窗内暂停重查询。
- **v2.2 窗注记**：仅时间面（今晚 21:00 一次性+22:30 硬收）；acceptance/n=1000/seed=20260916/stratify 零动（f06_grid_v2 重冻语义夜矿 T4 在册）。

## 21:05 起跑确认（W1 v2 今晚窗）
- fired 行 ×6（第 6 行=2026-10-10 21:00 新窗）✓；任务 State=Running ✓；grid_20261010-210008 目录已建 ✓；warning 流入=eval 循环进行中。窗位就绪三样全绿。

## W1 定谳（2026-10-10 21:32·三判全过=PASS）
- **判据三判**：①21:00 fired 行 ✓（fired×6）②manifest.csv **非空 1000 行**（v2 n=1000 全产出，grid_20261010-210008）✓ ③**LastTaskResult=0**（State=Ready）✓。
- **收卷时刻**：21:29:02（起跑 21:00→收卷 29 分钟——0.5h 预估精确兑现；批 A+批 B 双 exit=0；22:30 硬收前 1h 自收）。
- **定谳：W1 验收 PASS**——全项目第一场治本版引擎正式考试通过。4.8s/格实测（29 分钟/2100 格估算口径）vs 旧 44.8s/cell=**11.7x**（批 A 段），v2 引擎+序钉修复+窗口纪律全链生效。
- W1 销账（三窗全绿验收判据自此闭环：v2 首窗 21:00 位 PASS 在案）。

## 终判口径与周触发器处置（2026-10-10 21:4x·总统统筹 21:25 口径）
- **批 A 实测（总统筹读数）**：manifest 1000 行+**85.4% 命中率**+**9 分钟收卷**；批 B（10080 格）ETA 21:28 实际 21:29 收卷——与三判定谳一致（PASS，c69a4a6948）。
- **周触发器处置（PASS⇒删兜底防双跑）**：Set-ScheduledTask 空集被拒（参数校验）→等效达意=**Disable-ScheduledTask**（State=Disabled、NextRunTime 清空、LastTaskResult=0 PASS 保留；触发器定义原样留存，v2.1 窗系排新窗时 Enable-ScheduledTask 一键复启）。双跑风险解除。

## 收口（2026-10-10 23:1x）：W1 定谳 PASS 复核与二号收口终态（st-examclose-20261010）

- **23:04 窗点复核=三判独立重验全过**：①log fired 21:00:00 ②manifest 非空（批A=1000 行=v2 n_samples 精确吻合；批B=10081 行）③LastTaskResult=0；batch A/B 双 exit=0、21:29:02 收卷（29 分钟），195 条 FutureWarning 全程无害流过=PS 地雷治本直接实证；21:00 起/21:29 收在 v2 纪律带（08:00-22:30）内。chief-20261009 于 21:34（c69a4a6948）判定「W1 定谳 PASS·三判全过……4.8s/格 vs 旧 44.8s=11.7x，W1 销账」、21:38（cdec731bf9）终判口径+任务 Disabled 兜底解除（双跑风险解除、触发器原样可复启）。
- **令面演进链（最终态）**：本令原钉 23:00 自然窗→nightmine2 三连裁③改 v2 窗纪（Sat 08:00/22:30 硬收）→总统筹令 W1 考试提前至今晚 21:00-22:30（F06Grid 触发器改 21:00 一次性载体；我方 14:58 读数「10-17 08:00」系 schtasks 陈旧显示，nightmine2 断点卡§令面 如实在案）→21:00 实弹→chief 21:34 PASS 定谳→nightmine2 重挂 10-17 08:00 周窗为后续批次载体（现行 Disabled 可复启）。我方 15:1x「验收改指 10-17 候 Owner 确认」旗被本演进链覆盖=考试已提前兑现且 PASS，撤旗。
- **本会话收口清单**：T1 停投上报（ca446e99）｜R3 袋作废重 derive 建议在案（剔三册与 7 卡，真增量=calibration_exam.py +30+ruff 修复 2 件、46 测试绿）｜T2 99_delivery 终态刷新（与本批同件）｜T4 收账（W4 分数册 25 行全 fail 如实——21:52 矿考循环班续 7 行；W5 零 PASS 候面不动；W2=4.8s/格 实测已入 chief 终判，≤3.5 停手条款判定归架构册通道非本面）｜19:17 杀令落空核账（b421bc64）。
- **遗留移交**：①R3 袋重 derive 投递候 capability 册翻动根治（维护班「蒸发战争」面）；②TAKEOVER 误封本会话双命中——f87bfa8bf7（21:26）已治本（PID 亡改判必要非充分），后续会话免灾；③无主外来 staged 残件（registry_yaml_parse_gate.py 等）已单文件退栈在 worktree，属主回来 re-add 即恢复，未代改代码。
