---
ttl: task_bound
title: 99_checkpoint——过夜总令战役运行中断点卡（滚动更新）
created: "2026-10-10"
sid: st-nightmine-20261010
family_id: NIGHTMINE-CAMPAIGN
---

# 运行中断点卡（接手者先读这页）

工作根=工棚 `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010`（sid=st-nightmine-20261010，
逻辑长会话 pid=0，keeper 每 600s 续期，窗 10h）。
总报告机生件=`docs/_working/nightmine_campaign/00_final_report.md`（重跑
`python D:/ZephyrAlpha/.runtime/tmp/st-nightmine-20261010/build_final_report.py` 即刷新，勿手改数字）。

## 〇、续战班 T1 速报（st-nightmine2-20261010，2026-10-10 11:5x 更新）

| 项 | 状态 | 凭据 |
|----|------|------|
| quarantine 119 件认领 | ✅ 全数搬离（TTL 前逐件 sha256 对账） | manifest=`.runtime/sessions/st-nightmine2-20261010/staging/_claim_manifest.json`；原棚留收据 `_CLAIMED_BY_st-nightmine2-20261010.md` |
| 验属翻案 | ✅ 118 卡与 HEAD 九袋版逐字节一致（非欠落地=冗余孪生）；99_delivery.md=govjudge 遗物不冒领 | `git ls-tree -r HEAD --name-only -- docs/03_modules/_domain_backtest/exam_cards/ \| wc -l`=454；对账脚本在案 |
| index 排雷 | ✅ exam_cards 248 条 rm--cached 型 staged 删除全清（git restore --staged，零盘面触碰） | 清后子树无 D 行；8 条既有 ` M` 显性保留；2 A dualwindow+7 MM 他在飞未碰 |
| 实体修复 | ✅ TDM-F-C2-02 shadow02 卡内 card_id 笔误（node_id+姊妹卡双证孤例） | commit `0544db35bd3`（q-0001 已落地，`git show HEAD:<卡> \| grep ^card_id`=TDM-F-C2-02/） |
| 详录 | 📄 独立件已写待落地 | `docs/_working/nightmine_campaign/T1_quarantine_claim_20261010.md`（untracked；git 落地被 CREATE-GUARD 入队面 HEAD 仿真 × CAP 册盘面 R9⑤ 同族回退残影互锁拦——**本班未碰 CAP 册**（带册落地=重打投影袋禁令+毁他会话 staged 残影），待残影班修册后随净增袋落地，或由册主车道代带） |

> 续战令后续：T2 断供补监测中；T3 对照卡执行器立项；T4 F06 批A 处置；T5 L8b 更正袋——见各 T 交付记录。

## 〇-2、续战班 T2-T5 终态（st-nightmine2-20261010，2026-10-10 12:5x 更新）

| 任务 | 终态 | 凭据/落地 |
|---|---|---|
| T2 断供补 | ✅ 方案落地+执行门判定（禁双开红线守住） | 现读翻案三件：①断供在**源侧**（夜批已完成片标的 max 仍 09-30，回填腿到位也写不进 10 月）；②weekly/monthly TI（period 同表）max=09-15 比 daily 更陈旧 2 周；③emotion 10 月仅 pre_open 腿，close_final 仍 0；hfq daily 归 st-acure（活会话，weekly/monthly 已收 10-09）本班禁碰。D7 四件套=窗口/行数/验收/解锁清单全数落入 L8b 续读段 §八（前置闸 A=夜批收官、B=源侧恢复实证）；reaper keep 补登 wrapper/runner 两条 |
| T3 对照卡执行器 | ✅ 三件套里程碑（基线+目标件）；首批真卡出分待 W4 绑定层 | MOD-BT-243 原位扩面：双臂 PIT 回放+配对判据机判（maxdd/sharpe/turnover/cost_tier/oos_same_sign；misfire 无机判面如实记败）；红蓝 4 新增 11/11 绿+相邻回归 118 绿；q-0004 入袋 |
| T4 F06 批A 处置 | ✅ 作废+计次+v2 冻结+排窗 全件落地 | 计次 6000 宁严勿宽入账（总 20767→26767）；prereg f06_grid.enabled=false+f06_grid_v2（n=1000/同 seed/判据面零变动/Sat 08:00 起跑 22:30 硬收窗禁跨 23:00）；启动器同步+任务已改 08:00；三件原子袋 q-0003=723a6a10a983 |
| T5a L8b 更正袋 | ✅ 救援+续读段（新件落地受 CREATE-GUARD×CAP 册残影互锁，随残影班修册后落） | L8b_ledger.md 自一期工棚救援至主区战役目录+续读段 §七现读更正/§八 D7 四件套/§九监测履行 |
| T5b 封矿复挖硬门 | ✅ mining_sop v1.8.0 | §3 增设邻车道抽样复挖硬门（16 漏矿+4 翻案实证，替代"自报即封"默认惯例，存量不追溯） |

> 残留交接：①CAP 册（capability_canonical_file_registry）盘面=R9⑤ 同族回退残影+本班 1 条 token 已入 PG 账本待投影——归残影班修册后随净增袋落 T1/T5 新件；②T1 独立详录件与 L8b 续读段两个 untracked 新件随上述通道落地；③v2 首跑=下周六 08:00（或 L2 提速落地后经裁定升点）。

## 〇-3、夜矿批复登记（总统统筹 2026-10-10 13:2x，st-nightmine2-20261010 执行）

| 批复项 | 结论 | 本班动作 |
|---|---|---|
| 五件验收 | **全验收**（T1 排雷记大功） | 已登记 |
| CAP 互锁两件 | 转终清二期 render 路线，落地后本班补投 | L8b_ledger.md 借一期预登记 token（HEAD 册已在）**同批复窗直投**；T1_quarantine_claim_20261010.md 俟 render 落地后补投（续办凭据=本行） |
| 排窗对表 | 与 examclose 无冲突：23:00 空置合法；**v2 首窗=2026-10-17 08:00** | 已按此对表 |
| T3 首批出分 | 待 W4 绑定层照计划 | 里程碑已交付（37931954） |
| 99_delivery 路由 | 随 CAP render 解堵后一并落库 | 救援件现位=`.runtime/sessions/st-nightmine2-20261010/staging/_rescued_foreign/st-govjudge-20261010/docs/_working/govjudge_campaign/99_delivery.md`（终清二期取件即此路径；TTL 内安全，若过期由本班 staging 重新出件） |

> **事故注记（14:0x）**：T1 详录与 L8b 两 untracked 新件曾于 12:2x-14:0x 间自主区盘面失踪（T1 全盘零命中、L8b 仅余工棚原件）＝st-examclose 上报的「共享暂存区落地周期复活 stale 形」同族新表现（**untracked 清扫面**，归维护班根治）。两件已自会话上下文全额复原重建（L8b sha=e2fcc1764ff7），保险副本入本班 staging `_insurance/`；本班 staging 救援物（99_delivery/claim manifest）复验完好。

## 〇-4、矿考班让路令遵守登记（总统统筹 14:4x 令，st-nightmine2-20261010）

- **令面**：W1 考试提前至今晚 21:00-22:30（GPU+CH）；期间考试车道暂停 CH 重查询（挖矿只读照常）；明早 08:00 原窗取消勿等。
- **实测**：F06Grid 任务触发器已被统筹侧改为**今晚 21:00 一次性**（W1 考试提前窗载体）；本班昨改的 08:00 残留载体在触发器层已不存在（schtasks LIST 曾显示"10-11 08:00"系陈旧显示，取消令与此对表）。
- **本班动作**：①补挂 v2 首窗载体=每周六 08:00 自 **2026-10-17** 起（批复口径），任务 NextRun=今晚 21:00（考试优先，原触发器零触碰）；②21:00-22:30 期间本班无 CH 重查询——监测探针均为 max/count 只读轻查询，属"挖矿只读车道照常"范畴，收卷自动恢复；③提请统筹知悉：夜批 TI 回填（数据车道进程，非本班所启）14:4x 仍在跑（58 片），若 21:00 未收官，其 CH 写入面归数据车道对表，本班不代停。

## 一、已完成（凭据面）

| 项 | 状态 | 凭据 |
|----|------|------|
| 冷启动四闸 | ✅ | python 3.12.8／setup_dev_env --check 装位／lock_files cleanup 无死锁／reaper 计划任务在位 |
| T0a 新闻断供 | ✅ 治本+实跑 | 真病灶=PIT 日度段（window_type='1d'）从未物化（非夜窗腿停更，夜窗日日鲜至 2026-10-08 且零触碰）；构造腿字符串喂 DateTime64(3) 必抛 Code 53＝"工具有而未跑"根因；修后小批 5 日验门 PASS→全窗 2421 行/2421 uniq 日/4,646,749 事件；质量画像 2025 断崖（日均事件 52 vs 2024 的 2048） |
| T0b dexp 第四袋 | ✅ 已在 HEAD | `git show HEAD:src/zephyr/factor/indicator_reader.py \| grep -c argMax`=4 且内容级见 `_projection()` argMax 实装；本班曾据工棚旧盘面误判"第三路未落"＝在册 P0 形态"运行码落后 HEAD"，以 git show 现读纠判，零回退弹提交 |
| T0c 1004 件主袋 | ✅ 已落地跳过直落 | 四枚 commit 经 `git merge-base --is-ancestor` 验为 HEAD 祖先；`.runtime/tmp/mega_msg.txt` 缺席＝袋定义不完整 |
| W4 第二分开考 | ✅ 出分 | TDM-E-L1-S0-1/02_新闻情绪时滞 verdict=**fail**（ic_mean -0.0231／mono -0.224／oos_sign_flip＋IS-OOS 反号，n=1622），分数册 1→2 行 |
| W5 判据实弹 | ✅ dry-run 取证 | changed=0，两行 fail 均"只标候选关系 confidence 不动"；**未 --apply**（主区 TDM 盘面挂他会话在途面） |
| GPU 采样 | 🔄 在跑 | 采样器 `.runtime/tmp/st-nightmine-20261010/nightmine_gpu_sampler.py`→`.runtime/nightmine/gpu_util.log`（10min/档，9h 窗）；F06 窗 PID 50252 自 19:17 已跑 >12h，`grid_20261009-191707/` 现零件＝manifest 尚未落 |
| 车道名册 | ✅ 机生 | `00_lane_roster.yaml`（186 节点全覆盖，未分配 0，生成器同名 tmp 件） |

## 二、在飞

- 挖矿车道：L1（32 卡，已收口报）／L4（34 卡，已收口报）／L5（20 卡，已收口报）／L6（17 卡，已收口报）
  ／L7（L9 层，盘面已见 46 件在写）／L3（L0/L1/L4 补卡面，盘面已见 38 件在写）／L2（个股层，盘面暂 0 件）
  ／L0d（广度序列推导，含对拍官方涨停池自校验门）
- 队列：`q-20261010-st-nightmine-20261010-0002`＝**token 先行袋**（creation_tokens 净增 46 条，HEAD 基＋
  节扫描尾部纯增，+231/−0 键集合差自证）processing 中。其后待投：内容袋 L5/L6/L1/L4＋战役作业面袋＋
  token 先行袋 #2（新增 8 条战役面＋各车道卡）。

## 三、接班必读的三个今日新坑（都写进袋与台账了，勿再踩）

1. **心跳守护 idle 自退→袋被判 ghost_session 全死**：`session_worktree_start` 注册的是非逻辑会话，
   heartbeat_daemon 30min idle 即写 `status=exited`，存活闸（裁定#459）据此把袋直落 dead/（CLI 自动重投
   被拒）。正解=单一 API `SessionRegistry.open_session(sid, task_files=[...])`（register(pid=0, logical=True)
   一口完成，W-29 豁免 idle 自退）＋周期续期守护（本役 keeper=tmp/nightmine_session_keeper.py）。
   已死袋取回=`requeue <qid> --from-bag --force`（原快照 blob 免疫工作区漂移；--force 越同签名 419 次复发熔断留痕）。
2. **CREATE-GUARD 读的是落地面投影册**：预检忠实模拟 landing，故内容袋在 token 袋落地**之前**必被
   "无 creation_token" 拦——**两段式**（token 先行袋独立先落，内容袋随后）是硬顺序，不是可选项。
   先行袋构造禁照抄处方锚点：HEAD 里 `creation_tokens` 之后还有 `file_token`/`t2-*` 三个小家族，
   照"di_seam_exemptions 行之前"插会插进他人列表（构造件 added!=mine 守卫已自拦一次）。
   热册盘面另有撕裂读坑：登记与预检并行跑会让门禁读到半写册（误报单条无 token），串行即解。
3. **烟测未隔离**：`calibration_exam.run_card` 无论 `scores_path` 指向哪都翻卡状态⇒"卡 examined 而正式册
   无行"账面不一致。补正=对同一卡带 `--force` 重考落正式册（DSR 分母如实 +试次）。

## 四、待决与呈报（不自行拍）

- `net_fee` 缺键（L5 附带发现）：`exam_scale_cost_gate.yaml` 无该键⇒G1 净费读数静默返 nan；
  仅信息面不进 judge()，判据零影响，故本班**不当班改**，转考试卡车道。
- 灰度切换类卡（L6 报 C1-03/C3-02 标 owner_gate_required）＝Owner 保留面，只出卡未执行任何动作。
- 2025 新闻采集断供（news_data 2025=31,427 行 vs 2024=759,512）与广度面 limit_up_down 断供
  （仅 2026-07-20 起）＝L0 断供族工单面，非考试卡面。
- token 先行袋依 Owner 在册裁定**不带他人账本条目**：盘面残留 3 条他车道未投影登记
  （examchief 2＋final4 1，15 行）留待册主车道净增袋。

## 五、增量（07:32 快照，滚动）

- 车道收口：L1 32／L3 39／L4 34／L5 20／L6 17／L7 51＝**193 张新卡**；L2（个股层）仍在跑。
  L7 mined_out 5 节点（C01/C02/C03/G2/G5）余 40 有明列长尾未降格；L3 mined_out 空。
- **L3 硬结论（决定考试面上限）**：`对照卡/消融卡执行器缺位`（`library.lookup state "对照卡执行器"`
  0/3 源命中）⇒ comparison/ablation 族 25 张卡 blocked_on_impl＝**今晚能出分的只有 calibration 族**。
  这是真缺口，不是卡的问题；补该执行器＝考试车道工单（触 MOD-BT 族，净零须声明替代/合并面）。
- L0d 广度解锁件过门：7 序列×1,622 交易日零缺日；对拍官方涨停池干净基准日 12 天
  （剔 ST MAE=0.33 只／mean|rel|=0.43%）＋外部公开事件独立回验 5 例全命中；
  残余风险如实记：seal_ratio 与 blast_ratio 恒等互补（两卡信息冗余，卡侧须合并或改定义，待裁定）。
- 考试段实测分＝**8 行**（1 指数趋势＋1 新闻情绪＋6 广度），全 fail 如实入册。
  其中 **跌停家数 ic_mean=+0.0528、炸板率 ic_mean=+0.0786 已过 0.02 IC 地板**，
  仅 mono_spearman（0.539／0.576）未过 0.6 单调门柱——非"无信号"而是"响应曲线不单调"，
  这条区分对 Owner 早上判"要不要挪门柱重考"很关键（挪门柱=作废，须走新卡）。
- 队列五查（07:32 实测）：belt daemon heartbeat age=22s 活／processing=2（我 0002、0003 并行两池工）／
  四池工 tip 同指 fe3b426e75 ⇒ 病灶＝慢门禁链（2.7MB 热册落地面）非楔死，处方＝等，禁插队重投。
- W2 标定实测（代理口径，待收窗 summary 复核）：批自 fired 12.23h·A2-IC 组成标记 1003 次
  ⇒ **43.9 s/格**（历史 35.33 s/格，L2 停手条款阈值 3.5 s/格）⇒ 停手条款判**不触发**；
  GPU 均值占用个位数~30% 区间＝该批 CPU-bound，摊销未兑现。

## 七、落地收账（08:45 实测）

九袋全数入 dev（`git log --oneline dev` 可逐袋对账，pending=0）：
14b9a48d97 token 先行袋（272 条 creation_tokens，键集合差 +272/−0）→ 47dcaed9c1 s1 exit 25 件 →
3eab511c58 s2 portfolio 21 件 → 89e307646c s3 position 37 件 → 27e85ba1e9 s4 板块 35 件 →
df365ce1ec s5 个股 39 件 → d08c70ac4b s7 L9 非 A 族 28 件 → 85dde70f5f s8 L0/L1/LROOT＋分数册 31 件 →
另含 s6 L9-A 族与 s13 战役作业面末袋（含 creation_token 末 1 条同批）。
在册可复核尺：`git show dev:docs/03_modules/_domain_backtest/exam_scores_v1.yaml | grep -c "^- card_id"` = 17。

考试段终账：**17 行分数全 fail 如实入册**（10 行原批＝广度母卡口径替换＋新闻＋指数＋ERP＋研报密度；
7 行末批＝L3 车道导生卡 09-15，与本役导生序列**口径同源**＝正确配对面，用以更正母卡出分的口径申报缺口）。
W5 判据实弹：`writeback_exam_confidence` dry-run changed=0（17 行 fail 全部"只标候选关系不动 confidence"），
未 --apply（主区 TDM 盘面挂他会话在途面）。
GPU/W2：采样至 08:45 共 13+ 档，占用 17-30% 区间（均值个位数~30%）＝F06 批 CPU-bound；
批自 fired 已 >13h，manifest 仍 0 件，代理速率 43.9 s/格（>>3.5 阈值⇒L2 停手条款不触发）。

未竟与风险申报：工棚基底对齐 dev 失败（`git merge --ff-only` 因文件冲突 Aborting，本机版停在 14b9a48d97），
**在册面不受影响**（内容已全落 dev，本机字节另有 pre_ff_backup 与 rescue_final 双备份，481 件＋sha256 册）；
接班者若续挖须先把工棚基底对齐（建议弃本机冲突件后从 dev 重放，勿在陈旧基底上再投袋）。

## 八、环境与链路实测（接班可直接引用）

- **工棚外部重建会抹在途件**（L2 车道实证）：本工棚 06:27 被外部重建，L2 首轮 22 卡＋台账连坐消失，
  该车道选择全部重挖并逐条重测（未沿用旧数字）。本班随后做**字节保全**：
  `.runtime/tmp/st-nightmine-20261010/rescue_<HHMM>/`（467 件＋rescue_manifest.sha256）。
  判据：未落地件只活在工棚盘面与队列 blob 两处，故入袋=备份，长驻工棚≠安全。
- **本班自踩两坑（已当班补正）**：① 烟测未隔离（run_card 无论分数册指向都翻卡状态）→ 以 --force
  重考对齐；② 6 张广度母卡（02-08，冻结时口径=AKShare 涨停池）被我用 stk_limit 导生序列喂数出分＝
  **口径替换未在卡面申报**——正确配对是 L3 车道为此另立的 09-15 导生卡。已入册不改旧行，
  申报见本节；导生 vs 官方池在 12 个干净基准日 mean|rel|=0.43%（剔 ST），偏差小但须记账。
- **三档量纲/口径陷阱（两车道独立复证同一结论）**：
  ① 涨停/炸板/一字判定 MUST 用**不复权** `kline_daily` 配 `stk_limit`——用 `kline_daily_hfq` 得 3,882 家涨停
  荒谬值（L2 实测），L0d 选不复权面板因此被独立验证为正确；
  ② `technical_indicator` 原始行多版本（2024 raw 2,978 万 vs 去重 91 万 symbol-day），
  panel 类 IC **不去重=被放大 30 倍**；
  ③ `stock_basic` 窗内无创业板（2026-08-14 起）/北交所（2026-09-15 起）＝宇宙口径雷，已写死进卡。
- **执行器缺口两条（决定考试面上限，非卡的问题）**：
  ① comparison/ablation 族无执行器（L3 正查 0/3 源命中）⇒ 今晚 178 comparison＋64 ablation（含骨架）不可考；
  ② calibration 执行器 `_series_metrics` 硬编码 `shift(-1)`（仅次日目标）⇒
  凡 primary 声明多日前向收益的卡（如 A08 的 next_20day_sector_return）**不可用现器考**，
  否则测的是与冻结假设不同的目标。普查 15 张"scorable_now"里 6 张属①、A08 属②；
  另 A10 卡面 signal 写"日变化率**或** z-score(60 日)"未择一＝冻结不完整，本班不代拍、不开考。
- **落地链现场**：0002（2.7MB 热册单件）自 07:19 起 processing，手工 drain 得
  `SKIPPED: Serializer lease 被活体持有` ⇒ 病灶＝慢门禁链（pre_commit 全钩跑热册）非楔死，处方＝等；
  五查中 ①daemon heartbeat 新、②子进程 `pre_commit run --files <registry>` 在、③pending=0 无 convoy。
  `git/worktrees/w0/` 有 9 枚 0 字节 `tmpidx_precommit_*.lock`（10-07..10-09 陈旧）＝在册"无主陈锁毒 worktree"
  同型物证，但因 w0 index 16 分钟前有写且 lease 有活体持有者，**三证不齐不动锁**（在册手法=可检疫不可重试）。
