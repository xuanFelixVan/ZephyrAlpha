---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: 每日派单册（⑩线长席产出）
---

# 每日派单册

产出岗=⑩线长席（每日一单，查重+配额）；消费岗=全线。
格式：日期/班次｜席号｜任务｜配额｜查重结论｜防重入条款。


## 2026-10-15 首单（班 st-qoder-p10-1015-01｜巡检 04:35-04:45 实测读数（date 校时））

### 0 全线通令：游标推进（本班实测的断线根因）

实测：11 席 checkpoint.md 一律 cursor=未开始，而台账已有 5 批产出（1 席×2、6 席×2、9 席×2、11 席×1）＝游标面与台账面脱节，水位不可派工、防重入无判据可依。
根因（指令面缺项，非纪律问题）：十席 instruction.md 的流程节没有"收尾更新 checkpoint.md"这一步，而 checkpoint.md 自述"游标由本岗每批推进"——要求无流程承载，必然停跳。
本班起各席执行：台账留痕后同批更新本岗 checkpoint.md 三字段（cursor / last_run / last_batch）；未推标的产出判"未交接"，下游有权不消费且不记下游欠料。
本席对 instruction.md 的指令面改写暂缓：10 席 instruction.md 现为他会话 v1.5.1 同步在途（git index 已 staged），随袋提交＝归属篡改。待该批落地后由下一班按此文本追加：流程末步补"10 收尾更新本岗 checkpoint.md 三字段"。

### 1 全线水位（04:40 实测，非账面引用）

| 读数 | 值 |
|---|---|
| exam_cards 总数 | 531（entry 381｜position 63｜exit 50｜portfolio 37） |
| status 分布 | preregistered 187｜empty 186｜blocked_on_data 64｜examined 55｜blocked_on_impl 39 |
| 考试卡主册 exam_scores_v1.yaml | 75 行 / 覆盖 56 卡 / 该册 verdict 全 fail（该册 pass=0） |
| 04 区全部成绩册（2026/*.yaml 逐册遍历） | pass 81 / fail 84（合计 165 判定）＝indicator_exam 78 pass、indicator_conditional 1 pass+7 fail、alt/emotion 3 FAIL、metaq 1 pass+2 fail、mom029_reexam 1 pass、exam_scores_v1 0 pass+75 fail |
| 缺数登记册 known_data_gaps | 76 条：open 21｜accepted 19｜resolved 13｜no_source 6｜monitoring 5｜mitigated 4｜completed 7｜retired_quarantine 1 |
| 交接五册 | to_datasource / to_builder / to_impl / to_miners / unblocked 全空（无一字） |
| 正交闸基准 | pulse/independent_signals.md 空册；signal_orthogonality.py 磁盘有而 HEAD 无（三车道在途未落地） |
| 楼图 | pulse/coverage_map.md 占位空册；生成器＝SOP 3-C ⑤席首批施工单，未交付 |
| 枯竭面 | mined_out 零命中（00_lane_roster.yaml）；04_research_records/mining/exhaustion/ 零件；十楼账面全"未开" |

### 2 查重结论（逐条对已挖名单／现有卡池／在册冻结值）

| 对象 | 查重结论 | 证据 |
|---|---|---|
| CAND-P0-OBI-001（盘口买一失衡，6 席 10-15 微缩链产） | 非重复，可留池待闸 | 卡池 531 张仅 10 张引用 tick_depth／盘口字段，用途＝成交可行性（L4 三张）／涨跌停（L1-S3、L3、X-S2）／竞价失衡（L9-A02，最近邻但考集合竞价非连续竞价盘口）；无一把 OBI 当预测信号。15 员池成员全为价格／基本面／RSRS 型，无盘口腿 |
| OBI 正交闸判定 | 暂缺，不得入"过闸"账 | 池信号未物化＋工具未落地（HEAD 查无），候选行已如实注明，判"闸未开"而非"闸未过" |
| 1 席 10-15 项 market_index_meta vs 10-14 项 kline_etf_daily | 两对象不同源，无重复挖 | 各自 3＋渠道留痕在台账 |
| 6 席抄录的五键（mono 0.6／ic 0.02／ir 0.3） | 系在册冻结值逐字沿用，合规、非自拟 | 与同族 6/6 一致值字符串级零差异；但"盘口类是否套价量族五键"未裁＝呈批面 |
| 9 席 10-15 卡 TDM-E-L9-A01 vs 姊妹卡 TDM-E-L3-07-3 | 同假设双卡双物化，非重复消费 | 两卡各自 data_binding 口径不同（L9 无 ST/上市龄过滤），互为独立预测力复验，判合法双测 |

### 3 派单（按瓶颈给配额，头号瓶颈＝交接面零字＋吞吐环未开闸）

| 席 | 本班任务 | 配额 | 派单依据（瓶颈定位） |
|---|---|---|---|
| 9 成绩官 | 先补一项口径更正：全线 pass 不为零（04 区全册 81 pass 集中在指标口，卡考主册 0 pass）——晋级面与 verified 挂接须按 指标/条件/卡考 三口分别核，禁把卡考主册的 0 pass 当全线结论；再出 independent_signals 首版（pool-report：相关矩阵＋有效独立信号数＋参与率），再出空白轴地图→to_miners.md；当日分数册增量 100% 判卷 | 每班 1 版摘要＋1 条家族级观察 | 正交闸无基准＝3④席挖什么都无法计量，3-G 三件套之二缺位是全线第一阻塞 |
| 7⑧ 考工 A/B | 领 preregistered 队列开闸出分（A=entry 族，B=exit/portfolio/position 族）；panel 卡走 run_card API 禁 CLI；单卡>15min kill 记 finding | 每席每班 8 张 | 187 张已冻结卡零消费＝吞吐环从未开闸；分数册 pass=0 说明队列质量未知，必须先出分再谈别的 |
| 1 数据源 | 先补 6 条 no_source 的证据链（见 5 打回单），再按保底每班 3 项；每项结论必须同批落两处：建设单→to_builder.md＋条目 searched_channels 字段→known_data_gaps.yaml（CAS） | 每班 3 项；证据链回写 6 条 | 台账有结论但输出口空册＝2 席零收料，交接面断在 1→2 |
| 2 数据建设 | 今日无建设单可领，改做预演：把 21 条 open 按"表在否/腿在否/深度够否"三态分类，产出回补优先级清单草稿进台账；1 席首单到达即接 | 每班 1 张分类表 | 下游空转上游未料，先建领料面不建卡 |
| 3④ 挖矿 | 照 mining_directions 楼 1（P0 盘口，账面"未开"实测已在挖）续挖：OBI 补样本窗（≥120 交易日面）＋同楼再产 WMP 偏离／五档压力／大单流向 3 候选；卡骨架一律走 generate_exam_card_skeleton.py | 每班 5 新候选或 10 骨架；楼 1 游标推进 | P0 完全未开发且已链通，边际产出最高；正交闸未开期间候选只入 lane CSV 不入"过闸"账 |
| 5 实现 | 四件（按序）：a 楼图生成器（SOP 3-C 首批施工单，消费各席台账出 coverage_map 一行一楼）；b calibration_exam.py --target-csv 对 panel 卡砍单列缺陷；c 39 张 blocked_on_impl 领单实现；d ibt_runner 的 --pool-file 桥接 yaml（11 席缺口 1） | 每班 1 件落地＋测试绿 | 楼图缺位＝3④席防重入只能全量扫描（违 SOP 3-C 铁律）；panel CLI 缺陷与 pool yaml 都卡着上游吞吐 |
| 6 制卡 | 每班 5 张处置（具名子题填门柱；/01 裸骨架→呈批件计入保底）；新呈批一项：盘口类候选门柱是否沿用价量族五键 | 每班 5 张／件 | preregistered 187 与 empty 186 并存，转正率是轮转前置读数；门柱多口径并存只能呈批不擅挑 |
| 11 整装 | 21:30 夜：只做装配盘点（strategy_production_map 在册件与 verified 交集），pool yaml 未交付前不硬跑 ibt_runner | 每晚 1 次盘点 | 11 席自查已判"非免施工"（三缺口在 5 席），硬跑＝假成绩 |
| 10 本席 | 30 分钟一班：查重／定配额／巡断线／巡交接／迭代纪律审计＋晨报 | 每日一单＋每班 2 轮巡检 | — |

### 4 防重入条款（全线同文，SOP 3-B）

本班起每席开工先读 pulse/queue_depths.md 末行时间戳与本岗 claim：同岗上游班次仍持游标或 claim 未 release＝本班立即短报退出，不排队等待、不抢占。重入判据只看两处（时间戳＋claim），禁以"台账没我写的行"为据（那是游标面缺位的产物）。

### 5 断供纪律打回单（下 1 席）

known_data_gaps.yaml 全册 76 条中 searched_channels 字段命中＝0（含 6 条 status=no_source）；SOP 3① 与 4 要求"断供登记 100% 带证据链（渠道清单＋各自失败原因）"，现值不满足，判"断供未成立"，逐条打回：
auction_window_pre_202606_gap（且无 primary_alternative）／bt_trade_log_attribution_fields_missing／dividend_plan_miniqmt_retired／futures_warehouse_receipt_shfe_archive_cap／rate_decision_calendar_jin10_retired／auction_20260918_transition_gap。
补法：每条 ≥3 渠道（官方免费 API／开放数据／GitHub 数据集／数据商目录任三）＋逐渠道失败原因＋许可证结论；穷尽才准维持 no_source。已有 verification_20260918／primary_alternative 字段的可作引证入口，但不能替代三渠道留痕。

### 6 迭代纪律处置单（SOP 4：同对象同 holdout 月度消费 ≤3 轮）

实测分数册 12 卡有多行（31 行／26 个 metrics+fails 变体／5 行为逐字段相同双写）；其中两对象变体数已达 4＝超 ≤3 判据：
- TDM-X-R1-01/comparison/07_熔断五级梯度减仓对照_五态仓位锚定版：4 变体（10-12 两跑 maxdd 3.82pp→1.64pp＋10-13 reread 两跑）
- TDM-X-R1-01/comparison/07b_熔断五级梯度减仓对照_复位阶梯锚定版：4 变体全落 10-13 单日（run_id 分 off/mid 两臂）
处置（本席权限内，不碰分数册）：两卡自本单起暂停再消费，待 9 席在 iteration_history.md 补记账定性（按臂分别计＝每臂 2 轮合规；不分臂＝第 4 轮须换未消费样本段呈批或封存改良）。判据口径不由本席改，记账缺口是本席唯一可执行动作。
附带 finding 转 5⑨席：run_id 不同而 metrics/fails 全同的双写行 5 条＝判卷面幂等缺口（写册无同参同窗去重），账面轮次因此虚高，修在写侧不在册侧（分数册 only-add 禁改）。
另：iteration_history.md 至今空册＝"迭代史不记账的复考成绩判无效"这条纪律无承载面，全线 75 行成绩均处"未记账"态，9 席本班起补当日增量记账。

### 7 待 Owner 呈批面（本席不代裁）

1. 采购三件（分析师预期／分钟流／L2）仍待批——SOP 附录 B 原样。
2. 盘口类候选门柱是否沿用价量族五键（6 席新呈批项）。
3. /01 裸骨架卡语义参数（186 张，转正须具名子题或裁定退役）——6 席草稿 1／草稿 2 待签。
4. 07／07b 两卡若判"不分臂"＝月度消费超限，换样段或封存改良须 Owner 定（本席只暂停再消费）。

## 2026-10-15 第二单（班 st-qoder-p10-1015-02｜巡检 05:35-05:47 实测读数（date 校时））

### 0 复巡：上一班通令的兑现面（一处兑现、九席未动）

- 兑现 ① 席：游标已推（cursor=已处理 4 项，last_run 10-15 05:23，last_batch st-qoder-p01-1015-02），且首次把 4 张建设单落到 to_builder.md（11 行占位 → 54 行）＝断线 2（交接面零字）在源头已修，1→2 通道今日首次有料可接。
- 其余 9 席游标仍"未开始"（②③④⑤⑥⑦⑧⑨⑪）。其中 ⑥⑨⑪ 台账有产出而不推标＝通令未达，本班把"推标"写进各席配额行首句。
- instruction.md 指令面改写仍暂缓（连续第 2 班）：HEAD 未动（仍 dd6ae04849），10 席 instruction.md 的 v1.5.1 同步仍 index staged 在途，随袋＝归属篡改。补丁文本改寄存本册 §6，供落地后一次合入。

### 1 全线水位（05:35-05:47 窗口内实测，进程内命令读数非账面引用）

| 读数 | 值 | 对 01 班增减 |
|---|---|---|
| exam_cards | 531＝prereg 187／empty 186／blocked_on_data 64／examined 55／blocked_on_impl 39 | 逐项同值＝近 70 分钟**零流转** |
| 04 区成绩面（全 6 册 walk） | pass 81／fail 87 | 同判定；**更正 01 班"fail 84"少记 3**（其逐册明细自相加即得 87，加总笔误） |
| 卡考主册 exam_scores_v1 | 75 行（yaml docs=2，rows=75）／pass 0 | 零增 |
| known_data_gaps | 76 条：open 21／accepted 19／resolved 13／no_source 6／monitoring 5／mitigated 4／completed 7／retired_quarantine 1 | searched_channels 命中 0→1（hl_liquidation_raw_empty，3 渠道） |
| 交接五册 | to_builder 54 行（4 单）；to_datasource／to_impl／to_miners／unblocked 各 11 行占位 | 唯一开口＝1→2 |
| pulse 三册 | independent_signals 12 行占位／coverage_map 14 行占位／mining_directions 十楼账面全"未开"（楼 1 实测在挖） | 与 01 班同 |
| 记账面 | iteration_history 13 行占位＝空册 | 第 2 班零记账 |
| 正交闸工具 | signal_orthogonality.py 磁盘有／HEAD 无，本班实测 `--help` 可跑且列出 gate＋pool-report 双子命令 | 根因由"工具未落地"改判为"**有工具未跑**" |
| GPU 档工具 | gpu_rank_ic.py／smoke_gpu.py 磁盘有且 HEAD 有；scripts/gpu/gpu_watchman.py **磁盘有／HEAD 无** | ⑦⑧指令面引用的登记器未落地＝新断线（见 §6） |
| 落地通道 | commit_queue total 968／pending 81／processing 1／done 770／dead 116；队头 q-20261015-st-chfinalw2-20261015-0001 已等 17539 秒＝4.9 小时；本席 01 班三袋 0001／0002／0003 仍 pending（position_ahead 73／74／76，dead_reason 空） | pending 78→81＝convoy 未解且加深 |

成绩面逐册（walk 谓词＝dict 节点 verdict/outcome ∈ {pass,fail}，大小写归一）：indicator_exam 78P/0F｜exam_scores_v1 0P/75F｜indicator_conditional 1P/7F｜metaq_wave2 1P/2F｜mom029_reexam 1P/0F｜emotion_index 0P/3F。

### 2 查重结论（本班主战场＝① 席 4 张建设单 vs 在册采集腿）

| 对象 | 查重结论 | 证据（盘口实读） |
|---|---|---|
| B-1 两融标的名单（c1_market.margin_target_adjustment） | 正交，新腿合法 | 在册 margin 族 capability＝margin_trading（tasks.yaml:113，AKShare stock_margin_detail_sse/szse＝融资**余额明细**）＋margin_trading_qmt；"标的名单"侧零在册 |
| B-2 新股申购日程（c1_market.ipo_schedule） | **与在册腿部分重叠，须改建不新建** | tasks.yaml:1706 ipo_calendar_daily 在产：table=c1_market.**ipo_calendar**（异表），巨潮 stock_new_ipo_cninfo，daily_capital 日快照幂等替换，未定档 list_date=NULL 已处理；①席腿（东财 stock_xgsglb_em）的**申购代码/上限/中签率/发行 PE** 侧确无在册＝日历侧重复、申购侧新 |
| B-4 Hyperliquid 清算流（c1_market.hl_liquidation_raw） | **同表已在册＋升级项已挂账，禁二次建表** | tasks.yaml:943/949 hl_liquidation_capture：table 即 c1_market.hl_liquidation_raw，capture_mode=ws_trades_bounded 逐日 30min，描述自述"7x24 守护进程挂账下一班"；data_supply_sentinel.yaml:169/525 已监视该表→①席"升级常驻"＝认领既有挂账 |
| B-3 研报评级变动 rating_change | ①席自判分流合规 | ①席实测评级原始列已在采集面（capability research_report），判"派生列缺"未下建表单；本席复核 tasks.yaml capability＝research_report／research_report_detail 在册 ✓ |
| 楼 1 OBI 候选 CAND-P0-OBI-001 | 与 01 班同判：非重复、判"闸未开"不入过闸账 | 卡池 status 逐项与 01 班同值，无新卡入池 |
| TDM-X-R1-01 的 07／07b | 暂停令生效中，无新违例 | 分数册复测两卡各 4 行＝与 01 班同值，未再消费 |

### 3 断供纪律：01 班打回单改判（本班长案；旧案卷保留不删）

01 班 §5 把 6 条 no_source 一律打回 ① 席补 searched_channels。本班实测推翻其适用性，三条证据：
1. 6 条 created＝2026-09-17／09-18／09-21，**全部早于生产线四件套落地日**（git 138ca16710，2026-10-14）＝非 ① 席登记物；
2. 字段面逐条 walk：6/6 带 root_cause＋resolution_plan，5/6 带 primary_alternative，3 条带 verification_20260918 复测，gap_type∈date_range／empty_table／field_missing＝数据操作口径的事故登记，与挖矿线"断供"不同对象；
3. 21 条 open 逐条 walk＝带证据字段 21/21，零缺证据。
判定＝SOP 工序 5 的 searched_channels 判据只适用**生产线席位本班新登记的断供**；对既有数据操作条目套此判据属口径错用。**6 条回落**（原打回单留在 01 班 §5 案卷）。
本班成立面：① 席唯一新登记断供＝hl_liquidation_raw 历史段，已补 searched_channels 3 渠道＋逐渠道失败原因（官方文档无清算检索／仓内 hyperliquid_provider.py:36-37 实测 REST 422 与三种 WS 订阅名被拒／CoinGlass 仅多所聚合无逐笔）＝**合规，不打回**。

### 4 派单（本班配额；头号瓶颈仍是吞吐环零消费，⑨ 席首件判据已按实测改口径）

| 席 | 本班任务（首句一律＝推游标） | 配额 | 派单依据 |
|---|---|---|---|
| 9 成绩官 | 收尾先推标；首件＝跑既有工具出 independent_signals 首版：`python scripts/backtest/fexam/signal_orthogonality.py pool-report`（本席实测磁盘可执行，"缺工具"理由已不成立）；次件＝iteration_history 补记账（75 行未记账已两班）；三件＝占领区摘要落 to_miners.md | 1 版摘要＋当日增量 100% 记账 | 3-G 三件套之二缺位＝第一阻塞；根因已从"工具未落地"改判"有工具未跑"，本班派单面据此撤掉等待条款 |
| 7⑧ 考工 A/B | 收尾先推标；照 01 班开闸令领 preregistered 出分（A=entry 族，B=exit/portfolio/position 族），panel 卡走 run_card API | 每席每班 8 张 | examined 55 与 01 班同值＝开闸令两班未兑现；187 张冻结卡零消费仍是吞吐头号瓶颈 |
| 2 数据建设 | 收尾先推标；本班只领 B-1（查重通过的纯新腿）；B-2／B-4 按 §2 **改建**（B-2 须先声明与 ipo_calendar 的字段分工，禁并列表族；B-4 认领 hl_liquidation_capture 既有挂账，禁建同表新腿）；立项前逐条走 data_source_onboarding_sop | 每班 1 腿立项＋2 条改建结论 | 1→2 今日首次连通；查重不过就建＝造重复采集腿（在册先例教训） |
| 1 数据源 | 收尾先推标；续做每班 3 项，结论同批落两处（to_builder＋known_data_gaps.yaml CAS）；B-2／B-4 重查结论直接引本册 §2，不必重做实测 | 每班 3 项 | 本班已兑现两处同落，续做；① 席台账与建设单口径一致 |
| 3④ 挖矿 | 收尾先推标（楼 1 账面"未开"而实测在挖＝典型脱节）；楼 1 续挖，正交闸未开期候选只入 lane CSV 不入过闸账 | 每班 5 新候选或 10 骨架 | ⑨ 摘要缺位＝产出无法按正交性计量（SOP 挖矿制：计量按正交不按数量） |
| 5 实现 | 收尾先推标；a 件仍＝楼图生成器（coverage_map 两班占位）；b calibration_exam.py --target-csv 砍单缺陷；c 39 张 blocked_on_impl 领单；d ibt_runner --pool-file 桥接 yaml | 每班 1 件落地＋测试绿 | 楼图缺位＝③④防重入只能全量扫描，违 SOP 3-C 铁律 |
| 6 制卡 | 收尾先推标；每班 5 张处置（具名子题填门柱）；盘口门柱五键呈批项维持 | 每班 5 张 | prereg 187／empty 186 并存，转正率是轮转前置读数 |
| 11 整装 | 收尾先推标；21:30 只做装配盘点，pool yaml 未交付前不硬跑 ibt_runner | 每晚 1 次盘点 | 三缺口在 5 席，硬跑＝假成绩 |
| 10 本席 | 30 分钟一班：查重／定配额／巡断线／巡交接／迭代纪律审计＋晨报 | 每班 2 轮自检 | — |

### 5 迭代纪律审计（01 班处置单维持，本班零新违例）

- TDM-X-R1-01 的 07／07b 暂停再消费令继续有效：分数册复测两卡各 4 行，与 01 班同值＝未被偷偷消费 ✓。
- iteration_history 仍空册（第 2 班）＝"迭代史不记账的复考成绩判无效"这条纪律无承载面；升级进 ⑨ 席本班次件。
- 双写行（run_id 异而 metrics/fails 全同）5 条＝判卷写侧幂等缺口，转 ⑤ 席；本席不改册（分数册 only-add）。

### 6 待落地追加（指令面补丁寄存处，v1.5.1 在途件落地后由下一班一次合入）

1. 十席 instruction.md 流程末步追加："10 收尾更新本岗 checkpoint.md 三字段（cursor／last_run／last_batch）；未推标的产出判未交接，下游有权不消费且不记下游欠料。"
2. ⑦⑧ instruction.md 的 GPU 机会档行须按实测路径校订：现文写 `scripts/gpu/gpu_watchman.py acquire`，本班实测该件磁盘有而 **HEAD 无**（未落地，登记动作会直接失败）；gpu_rank_ic.py 与 smoke_gpu.py 实测在 scripts/backtest/fexam/gpu_ic/ 下且 HEAD 有 ✓。合入时须写明"看门人未落地前 GPU 档只准走 CPU 路"，禁凭册抄路径。

### 7 待 Owner 呈批面（本班新增第 5 项）

1. 采购三件（分析师预期／分钟线／L2）——SOP 附录 B 原样待批。
2. 盘口类候选门柱是否沿用价量族五键。
3. 186 张 /01 裸骨架卡语义参数（转正须具名子题或裁定退役）。
4. 07／07b 若判"不分臂"＝月度消费超限，换样段或封存改良须 Owner 定。
5. **提交链 convoy 已恶化**：队头等 4.9 小时、pending 81（01 班 78），生产线两班交付物全部压在未落地面；本席无写域处置权（不属 instruction 面），是否升级治理线请 Owner 定点。




---

## 2026-10-15 第三单（班 st-qoder-p10-1015-03｜巡检 06:35-07:03 实测读数（date 校时））

### 0 复巡：上班通令兑现面（四席动了，① 席推标被外部复位）

- 兑现：③ 席首次发车（游标 20261015-p03-01，8 行候选入 data/strategy_intake/lane_p0_obi_candidates.csv，8501 字节）；⑥ 席推标（06:27，自报 0 翻转＋3 张呈批正文被 CREATE-GUARD 拦）；⑨ 席推标（游标 rows[74]）且一次交付两册——iteration_history 由空册变 28 行（5 对象记账）、independent_signals 由占位变 62 行（如实报"闸未开"）；④ 席 claim 在持（feedback/to_datasource＋to_impl 由 st-qoder-p04-1015-01 持有）＝在跑未推标。
- 未动：②⑤⑦⑧⑪ 游标仍"未开始"；⑦⑧ 连续第三班零出分（examined 恒 55）。
- 断线 3 号（本班新抓，实测形态非推断）：① 席游标 06:45 读到"本班第 03 批／last_run 10-15 06:45／last_batch st-qoder-p01-1015-03"，本班 06:55:46 复读到 cursor=未开始，且 HEAD_sha=IDX_sha=DISK_sha=2a6fce60f6、文件 mtime=06:53:53＝推进面在 06:45→06:53 窗口内被复位到 HEAD 值；复位执行者本班未查明（.runtime/audit/safe_write.jsonl 对该路径零命中）。后果＝按通令"未推标的产出判未交接"，① 席今日三批将被下游判欠料，故通令补一条：**推标后自证三面 sha，被复位即重推并在台账记复位时刻**。

### 1 全线水位（06:35-07:03 窗口内进程内实测，非账面引用）

| 读数 | 值 | 与上班对账 |
|---|---|---|
| exam_cards 总数 | 531（entry 381｜position 63｜exit 50｜portfolio 37） | 同值 |
| status 分布 | preregistered 187｜empty 186｜blocked_on_data 64｜examined 55｜blocked_on_impl 39（加总=531 ✓） | 逐项同值＝第三班零流转 |
| 成绩采集面 | docs/04_research_records/backtest/scores/2026/*.yaml 全 20 册 walk（其中有判定者 5 册） | 02 班记"6 册"，本班实测 20 册＝采正面以本行为准 |
| 成绩读数 | pass 81／fail 87／合计 168；逐册＝exam_scores_v1 0P/75F、indicator_exam 78P、indicator_conditional 1P/7F、metaq_wave2 1P/2F、mom029_reexam 1P、emotion_index 0P/3F | 与 02 班同值＝当日零增量 |
| 提交队列 | pending 88／processing 1／done 770／dead 118／total 977；队头 q-20261015-st-autoplan-20261015-0001 等待 15690s=4.36h（ahead 44） | 02 班 81/116、队头 17539s（队头身份已换，旧袋去向本班未查） |
| 本线今日袋 | p10 系四袋全 pending（01 班 0001/0002/0003＋02 班 0001，dead_reason 空） | 生产线系六席 14 袋零落地＝交付全压未落地面（R2 逐席实测 pending+processing：p01 2／p03 2／p04 2／p06 3／p09 1／p10 4；首测 06:5x 读得 11 袋，其间 ④⑥ 席又建 3 袋） |
| 起批水位 | commit_pct 82.38%／ram_used 66.1%／cpu 64.0%／worktree_changes 5348 | 02 班 72.8%＝内存压力上行约 10 分位 |

### 2 落地面普查（本班主发现：生产线运营面整体只在 index，HEAD 查无）

四件套 44 件实测 **40 件在 HEAD**，缺 ⑪ 席四件（instruction/scope/checkpoint/ledger 全为 idx=A）；运营面 **11 件全部 HEAD 查无**＝dispatch/daily_dispatch.md、pulse/queue_depths.md、pulse/coverage_map.md、pulse/independent_signals.md、pulse/mining_directions.md、iteration_history.md、feedback/{to_builder,to_miners,to_impl,to_datasource,unblocked}.md；③ 席候选册 lane_p0_obi_candidates.csv 同样 HEAD 查无；正交闸真身 scripts/backtest/fexam/signal_orthogonality.py 实测 HEAD=no／disk=D／idx=AM。
判据依据＝主区 index 是多会话混合池（在册先例：热册静默蒸发、并行期工作树被外部重置），未落 HEAD 的件一次复位即整片消失——本班已用 §0 的 ① 席游标复位实测到一次真实复位。
本席处置＝不代他会话补落（随袋他人未落地条目＝归属篡改，权限红线），改为呈批第 6 项＋通令各席"先落自家册再作业，落地面未含的产出判未交接"。

### 3 查重（本班主战场＝③ 席 7 条盘口候选 vs 在册 531 卡）

尺子先立正对照：531 卡全文可读（命中数按"前 60 行 title/hypothesis 面"与"全文表名面"两套分别给数，两套结果不同故分列，禁混用）。

| ③ 席候选 | 在册命中实测 | 查重结论 |
|---|---|---|
| WMP-002 偏离中间价 | 全文 WMP/中间价/microprice 命中 **0** | 纯新腿 ✓ 可进 ⑥ |
| OBI-001/007 一档失衡与尾盘失衡 | 文本"失衡/imbalance/bid_volume1"3 张（L4-03、L9-A02、P-P2-02）；全文含 tick_depth 10 张 | 非同对象（那 3 张用 l2_tick/竞价或执行段，无一把买卖一量做日频截面预测子）；③ 席已自写与 L9-A02 的窗区分面 ⇒ 判非重复，入池须与那 10 张做列共线对拍 |
| SPREAD-005 有效相对价差 | 文本 spread/价差 22 张 | 须逐张声明差异（多为日线额量代理，非盘口一档中位数）⇒ 派 ⑥ 写死门柱差异面，禁并列表族 |
| LARGEFLOW-004 大单净流向 | 文本大单/money_flow/资金流 19 张；全文含 money_flow 表名 7 张 | 撞面最大：③ 席自声明"与 L7-A06/L3-12-1 同假设新口径"＋残差化防与当日涨幅机械共线 ⇒ 判**条件通过**，卡面须写残差化门柱与方向重建降级条款 |
| SLOPE-003 五档压力梯度 | 与 OBI 共用五档量列 | ③ 席自声明"禁双计"✓，入池二者择一或正交化 |
| CANCELL-006 挂单蒸发率 | 全文含 l2_tick 4 张；③ 席实测本表 l2_tick count()=0 | 承接在册长尾（docs/04_research_records/mining/ledgers/nightmine_20261010/L7_ledger.md 已登记未挖）＝非新造题 ✓，卡面须写"快照差分代理口径" |

更正一条（本席前两班口径，旧案卷不删）：首单/第二单称"楼 1 卡池零盘口"，本班实测＝卡池含 depth/盘口/逐笔/五档 文本命中 53 张、含 tick_depth 表名 10 张。正确口径是"零盘口**信号**卡"（盘口在册仅作执行/成本段），后班派单禁写"零盘口"。

### 4 断供纪律与迭代审计

- 断供抽查（真源 src/zephyr/data/config/known_data_gaps.yaml，逐条 walk）：带 created 的条目 74 条，created≥2026-10-14 的新登记 **0 条**＝① 席今日三批未新登记断供。判＝无对象可打回（本班不拿"账面 4 张建设单"推断断供），但 ① 席台账须如实写"本班零新登记"，禁为凑证据链造断供。
- 迭代纪律审计：iteration_history 已由 ⑨ 席首班记账（空册状态解除，第 3 班兑现）。超限读数＝TDM-X-R1-01 的 07/07b 各 4 行 > 上限 3（⑨ 席自报超限、不代裁）；已达上限待观察＝TDM-E-L2-02/03、L2-04-2 各 3 行；性质不可判别＝TDM-E-L1-S3 的 05/06（metrics 逐字节相同、仅 run_id 变）各 2 行。
- 本席处置单（SOP 工序 5，零判据改动）：其一 07/07b 的暂停再消费令维持，超限换样/封存仍列 Owner 件（第 4 项）；其二 L1-S3 05/06 的"链路复读是否计入月度预算"口径归属待 Owner 覆核，覆核前**本席按册面行数保守计量并暂停续考**（保守口径只紧不松，禁自辟豁免）；其三 ⑨ 席自记"卡面 window 未逐字读（记欠）"＝记账覆盖面欠账，列本班次件追收。

### 5 巡交接（下游收不上上游产出的三处，一律修上游落点/格式，不动判据）

1. ⑨→③④（占领区摘要）：independent_signals 首版已出但池未物化。本班实测入参契约面＝全仓 462 个 csv 中首行恰为 date,sig 者 **0 个**（正对照＝462 文件可读；③ 席独立实测工具退出码=2）⇒ 3-G 根因第三次改判为"**信号面板从未按 date,sig 物化**"，非"工具未落地"（首判）、非"有工具未跑"（二判）。修法＝派 ⑤ 席一件物化单，⑨ 席在池物化前只出"成员表＋占领区清单"可交付面，禁硬凑相关矩阵。
2. ⑥→⑦⑧：⑥ 自报 0 翻转（3 张呈批正文被 CREATE-GUARD 拦＝04 区新建件须 creation_token，门要求登记而非判据问题）＋2 在途件 HEAD 复位。⑥ 请本席终裁号位：本班判 06:27 收尾班＝st-qoder-p06-1015-01（其台账袋已做成两班并集超集），并发袋 q-20261015-st-qoder-p06-1015-02-0001 归 02 号；号位只防游标互踩，不改内容判据。
3. ⑩→讨论册（晨报承载面）：docs/_working/cmd_ledger/ 整目录在工作树已消失（老路径 index 仍存 3 件＝HEAD 面在），归档副本 docs/_archive/_working_cleared/cmd_ledger/*.md 状态 A（未落地），且该件被 **4 个在途袋**同时改（st-autoplan ×3 base_blob=d84db9ff、st-lineup ×1 base_blob=eff62546）。本班实测四袋 blob 内 p10-1015 命中=0 ⇒ 01/02 两班晨论文本既未随袋、也不在任何盘面或袋存面＝**已失**。本席不复写他人册（红线），晨报落本席台账＋本册，落点冲突列呈批第 7 项。新纪律：**晨论文本首落本席自有写域，讨论册仅在实测该件零在途袋时才补投**。

### 6 派单（本班配额；首句一律＝推游标＋三面 sha 自证）

| 席 | 本班任务 | 配额 | 派单依据 |
|---|---|---|---|
| 9 成绩官 | 追收自家"卡面 window 未逐字读（记欠）"腿（逐对象补 OOS 窗字面）；次件＝占领区可交付面（成员表＋在册 56 个 distinct 对象清单）；三件＝iteration_history 逐轮续记 | 1 面摘要＋当日增量 100% 记账 | §5-1 实测 462 csv 里 date,sig 首行 0 个＝池未物化，摘要只能先出成员面 |
| 7⑧ 考工 A/B | 推标＋写明"本班为何零发车"的实测三态（run_card 可否 import／卡面缺哪一字段／CPU 档能否跑），禁再以"排队/等待"作结 | 每班 1 条发车障碍实测记录（出分配额本班**停派**） | examined 恒 55＝三班零消费；同文配额连派两班无效，已升呈批第 6 项 |
| 5 实现 | a 件仍＝楼图生成器（coverage_map 14 行仍占位）；**新派 b 件＝信号面板物化单**（把在册已晋级信号落成 date,sig 面板，落点经 python -m zephyr.library.lookup 核实后写进 independent_signals 头）；c calibration_exam.py --target-csv 砍单缺陷；d 39 张 blocked_on_impl 领单 | 每班 1 件落地＋测试绿（b 件＝1 个能被 pool-report 直接吃的目录） | 3-G 三班报出三个不同根因，实测唯一未闭合腿＝入参面板从无 |
| 6 制卡 | 本班 5 张处置配额不变；③ 席 7 条候选按 §3 结论分档（WMP 纯新直转；OBI/SLOPE/CANCELL/CLOSEBAND 须写区分面；SPREAD/LARGEFLOW 须写残差化与降级条款门柱）；04 区新建件先登记 creation_token 再投 | 每班 5 张 | 转正率是轮转前置读数；号位终裁见 §5-2 |
| 3④ 挖矿 | 楼 1 续挖：正交闸缺席期候选只入 lane CSV 不入过闸账（③ 已按此行）；候选册须自落 HEAD（现 HEAD 查无＝按新纪律判"待交接"）；禁写"卡池零盘口"（§3 更正行） | 每班 5 新候选或 10 骨架 | ③ 自测盘口表 uniqExact(trade_date)=24、闭卷切点前 0 行＝楼 1 主腿 blocked_on_data 成立，续挖优先走窗内可算的 LARGEFLOW 替代腿 |
| 1 数据源 | 游标重推＋记复位时刻（§0 断线 3 号）；续做每班 3 项；台账如实写"本班新登记断供 0 条" | 每班 3 项 | §4 实测：74 条带 created、10-14 后新登记 0 |
| 2 数据建设 | 本班仍只领 B-1；B-2/B-4 改建结论沿用第二单 §2；立项前逐条走 data_source_onboarding_sop | 每班 1 腿立项＋2 条改建结论 | 1→2 已连通，续做 |
| 11 整装 | **本班首件＝先自落自家四件套**（实测四件 HEAD 查无、idx=A）；再推标；21:30 只盘点不硬跑 | 1 次自落＋1 次盘点 | §2 普查＝运营面未落地；本席游标仍"未开始"（10 行） |
| 10 本席 | 30 分钟一班；本班起加两条常任巡检＝落地面普查（§2 表）＋游标复位巡检（§0 手法：三面 sha＋mtime） | 每班 2 轮自检 | — |

### 7 防重入条款（全线同文，SOP 3-B）

下一班（st-qoder-p10-1015-04）最早 07:30 后发车（闸面一律取脉冲册末行时戳＋25 分；本册 §0-§9 写于 07:03、台账与脉冲写于 07:05，故以脉冲册为唯一闸面）。各席：袋未出四态前不得自称已交付（判据=commit_queue status，非入队回显）；推标后三面 sha 自证；运营面未落 HEAD 的产出判"未交接"。

### 8 待落地追加（指令面补丁寄存处）

- 本班实测 p10 instruction.md：HEAD_sha=77db8a23c2／IDX_sha=DISK_sha=352de5aec6，index 面含外来"【v1.5.1 同步】"3 行而 HEAD 未含；十席 instruction.md 同样带外来 staged 行（p01/p03/p04/p06/p07/p08/p09/p11）⇒ 01/02 班寄存的两条补丁（推标末步＋GPU 看门人路径）本班**不合入**（合入即把他人未落地条目计入本席 commit＝归属篡改），维持寄存。
- 新增第三条待合入通令文本：推标后自证三面 sha（HEAD/IDX/DISK），被复位即重推并记复位时刻。
- 新增第四条：各席运营面（派单册／脉冲册／自家台账与候选册）须当日自落 HEAD。

### 9 待 Owner 呈批面（本班新增第 6、7 两项）

1. 采购三件（分析师预期／分钟线／L2）——SOP 附录 B 原样待批。
2. 盘口类候选门柱是否沿用价量族五键（§3 已给 7 条候选的区分面实测，可作批面材料）。
3. 186 张 /01 裸骨架卡语义参数（转正须具名子题或裁定退役）。
4. 07／07b 已 4 行超限＝换 fresh holdout 呈批或封存；另 L1-S3 05/06 的"链路复读是否计入月度预算"口径待覆核（本席暂按行数保守计量并暂停续考）。
5. 提交链 convoy：队头 4.36h、pending 88、本线六席 14 袋零落地（R2 逐席实测；本班未查旧队头袋去向）。
6. **生产线运营面 12 件＋⑪ 席四件从未落 HEAD**（普查表见 §2）：是否给生产线开落地优先通道，或先降频（现况＝交付全压未落地面，一次外部复位即整片蒸发，本班已实测到一次）。
7. **晨报承载面归属冲突**：docs/_working/cmd_ledger/ 被外来搬迁（老路径工作树消失、归档副本未落地、4 袋在途），⑥ 01/02 班晨论文本已失；请定点＝晨论文改落何处（本席暂落自家台账＋派单册）。

## 2026-10-15 第四单（班 st-qoder-p10-1015-05｜巡检 07:35-07:48 实测读数，date 校时）

### 0 复巡：上班通令兑现面＋对本班首读的两处自我更正（旧案卷留档不删）

- **兑现（本班头号增量）**：6→7→9 吞吐环首次闭合。三席游标互证＝6 号"本班已收尾（翻转 4 张对照卡→preregistered）"／7 号"entry_flow class D 八张（L1/TDM-E-L1-S2__calibration__40-47）"／9 号"exam_scores_v1.yaml#rows[82]"。盘面同值闭合＝卡池 examined 55→63（+8）与主册 rows 75→83（+8）同源同量；全线 pass 面 81→83、fail 面 87→93。卡考主册此前形态是 0 pass/75 fail，本班实测 2 pass/81 fail＝**卡考口今日首次出 pass**。01/02/03 班连续三班报的"187 张 preregistered 零消费"瓶颈已破口。
- **更正一（本班第一漏检，判据级）**：本班 07:40-07:41 首读量到"11/11 席 checkpoint 全为 12 行占位、cursor=未开始"，并据此准备写"通令未兑现"。07:44:55 复读证伪：真面＝8/11 在推标。根因不是各席纪律，而是席位四件套被外来重生流程按分钟级重置成模板面（见 2 节事件登记）。据在册同型教训，本班起新判据：**游标与运营面读数必须两时点采样取较新面；单点读数一律不得进派单**。
- **更正二**：07:44:45 本班一度量到 25 件席位件"磁盘已删＋index 面只剩 255 B 模板"，07:45:54 全部自行回面（本席 ledger 实测 29728 B／84 行字节完整，含 01-04 班全部案卷）。定性＝重生周期的删除相，非永久丢失。本班在删除相当场已把 55 件盘面全量快照到 `.runtime/tmp/p10_evict_1015_0744/`（index_face＋disk_face 两套字节＋两份 manifest），复原双源齐备。

### 1 全线水位（07:35-07:48 窗口内进程内实测）

| 面 | 本班读数 | 上班读数 | 判读 |
|---|---|---|---|
| 游标推标 | 8/11（1-4、6、7、9、10 号席） | 4/11 | 兑现面扩张；5、8、11 号席仍"未开始"＝5 号席自 00:39 起四班零动 |
| 卡池 | 535＝empty 186／prereg 183／blocked_on_data 64／examined 63／blocked_on_impl 39（加总闭合） | 531 | +4 新卡；prereg −4、examined +8 与 7 号席出分同量 |
| 成绩采集面 | 20 册全扫，6 册有判定＝pass 83／fail 93／合计 176 | 168 | +8，与 examined +8 同源闭合 |
| 迭代预算 | >3 行卡 2 张（R1-01 的 07／07b，各 4 行，在册暂停态） | 同 | 本班零新违例；今日新增判定行全部落在预算内卡 |
| 队列 | pending 91／processing 3／done 774／dead 121／total 989 | 88/1/770/118/977 | 队面在动（done +4、dead +3），但队头仍是 chiefdead6 那只 01:06 袋，已等 6.59h |
| 落地通道 | 主区 `.git/index.lock` 0 字节／mtime 06:49:56／龄 47 分；`git add` 实测 fatal；黑匣子每 5 分钟记 `write-tree rc=128: remove the file manually to continue`（07:31／07:36／07:41 三点） | 04 班只记到 git add 失败 | **全线写面被这一枚锁挡住**，非本线独有 |

### 2 事件登记（肇事会话不追查、不代修＝本席写域内只做登记）

- **事件 A｜席位四件套分钟级重生循环**：实测点位 07:41:35（游标集体回 12 行占位）→ 07:43:45（25 件从磁盘消失，各席目录只剩 scope.md）→ 07:44:55／07:45:14（instruction／ledger／checkpoint 自行重生，真面回来）。形态＝重生周期，非恶意删除。受害面＝十席 instruction/checkpoint/ledger 全集＋本线今日 01-04 班台账。在案同型＝9 号席 07:38-07:45 实测（其 20388 字日报一度变 255 B）。**最阴后果＝袋吸的是被重置后的模板字节**，队列状态看着"正常入袋"而落地即整片蒸发；本线四只 p10 在途袋实测 ledger blob 面＝6105／7883／9195／16245 B，均小于现盘 29728 B 且全部不含 04 班记录（blob 正文命中"今日第 01 班"、零命中"1015-04"）。
- **事件 B｜主区 index 锁**：三证齐（1 锁体 0 字节；2 mtime 06:49:56 跨 07:44→07:46 三次采样不变；3 存活超 10 分钟的 git 进程数量=0，全部为 20 秒内瞬态）。在册检疫手法＝`os.replace` 移到 `.runtime/tmp/lock_quarantine/`（不删、可复原），**动作前须 Owner 点头**（共享面，影响全部在途会话与序列化器），命令见 10 节第 8 项。
- **事件 C｜两址并存**：`docs/04_research_records/cross_domain/automation_campaign/` 由 st-scorehome-20261014 于 03:09:08 一次性铺面，11/11 checkpoint 全 15 行模板桩、零席位增量、HEAD 查无（git ls-tree 计数=0）。旧址 `docs/_working/automation_campaign/` 是 HEAD 跟踪面（40 件）＝指令书名路径＝活面（8/11 有增量）。

### 3 查重（本班主战场＝卡池唯一性＋7 号席新出分卡）

- 卡池 535 件 card_id **唯一集 535**（零重名）；(node_id, family, title_zh) 三元组去空白后**零重复**。判据面＝逐卡 yaml 解析 535/535 成功，非目录计数。
- 7 号席本班新出分 8 张＝L1/TDM-E-L1-S2__calibration__40-47，逐张核 card_id 与在册 L1-S2 家族卡不重名；母题集中在同一 node（L1-S2 节点累计 42 行判定＝全线最大集中面，列 10 节第 4 项覆核材料，本席不自判违规）。
- 3 号席 7 条盘口候选 vs 卡池：03 班 3 节已做区分面实测，本班未见新入册候选（其游标停在"数据面实测已齐＝判据面 blocked"），不重复计。
- 尺子自证：本班查重第一版误把 `preregistered_at` 空值（189 张）当"今日新注册"（字符串比较假阳，'None' 大于 '2026-10-15'），已作废该读数；现表述只准写"标 2026-10-15 者 0 张，另有 189 张该字段为空"。

### 4 断供纪律与迭代审计

- 断供证据链：`src/zephyr/data/config/known_data_gaps.yaml` 实测 76 行，带 `searched_channels` 者 **1 行**；但 1 号席今日新登记断供 **0 项**（其台账 04 班自记"新登记断供 0 项"，且 03 班两项断供登记逐条附三渠道 YAML）。⇒ **本班打回 0 条**（无当日新登记对象）。75 行历史缺证据件属数据采集旧账，不属本线 1 号席今日产出，本席不代追。
- 迭代纪律：>3 行/月 的卡仍只有 07／07b 两张（在册暂停态维持）；本班无处置单新增。同对象月度预算的"节点面是否计入"口径未定（10 节第 4 项待覆核），本席按行数保守计量、不放开续考。

### 5 巡交接（下游收不上上游产出＝修上游落点/格式，不动判据）

| 断点 | 实测 | 处置（指令面） |
|---|---|---|
| 3、4 号席候选 → 6 号席成卡 | 6 号席本班收的是 4 张存量对照卡（转正），3 号席 7 候选未进其收件面 | 6 号席本班 a 件＝从 3 号席候选册点名收件，收件面写死为 `pulse/mining_directions.md` 楼 1 行＋3 号席台账候选节两处 |
| 5 号席未开工 → 9 号席正交闸"闸未开" | 9 号席首版已实测：全仓 csv 首行 date,sig 命中 0；IBT 产物根目录不存在；CH 侧 factor_signal/factor_feature_value 表面在而零行 | 不改派新内容，只把 5 号席物化单从"排队件"改判"本班唯一件"（7 节）；3、4 号席在此期间一律记候选"闸未开"，禁记"闸未过" |
| 7 号席通道 → 8 号席复用 | 7 号席已用 class D run_card 双注入跑通并出分 8 张 | 8 号席首件＝只抄通道不领新卡：实测三态 1 条（能不能出分／出的是哪一面），避免第四班仍"未开始" |
| 各席运营面 → HEAD | 本线运营面仍只在 index/盘面，HEAD 查无；四只 p10 袋吸模板字节 | 本席不改各席 instruction.md 本体（外来 v1.5.1 staged 在途，随袋＝归属篡改），通令文本寄存 9 节待落地面清干净后一次合入 |

### 6 席位家址定夺（本席写域，据在册处方"唯一席位家址由 10 号席定夺后才允许单址"）

- **本班起生效**：`docs/_working/automation_campaign/pNN_*/` ＝ 十席四件套与运营面的**唯一落地面**。判据三条：1 指令书名路径在此；2 HEAD 跟踪面在此（40 件）；3 本班实测活游标只在此（8/11）。
- 新址 `docs/04_research_records/cross_domain/automation_campaign/` 现况＝未跟踪模板桩（03:09 一次性铺面、零增量）。**通令：各席禁往新址写**，直至 Owner 定点（10 节第 9 项）。本席不自删新址（永久区处置＝Owner 门位）。

### 7 派单（按瓶颈定配额；各席本班首句一律＝两时点采游标自证＋三面 sha 对表）

| 席 | 本班配额 | 唯一交付判据 |
|---|---|---|
| 1 数据源 | 维持第 04 批游标项，不扩面 | 断供若新增须三渠道＋各自失败原因；新登记 0 也要写"搜过什么、为何 0" |
| 2 数据建设 | 已收口＝零申请态；本班只做"收件面是否为空"复测 | to_builder.md 行数实测值 |
| 3 库内挖矿 | 楼 1（P0 盘口）续挖；7 候选的**交付对象是 6 号席**，不是台账 | 候选册候选数与 6 号席收件数对表 |
| 4 全网矿工 | 楼 1 第 2 轮扫完即登记重复率 | 连续两轮零新增才准自报枯竭 |
| 5 实现 | **本班唯一件＝信号面板物化单**（3-G 未闭合腿，四班零动） | 物化后首行 date,sig 命中 >=1 个 csv，且 9 号席 pool-report 能跑出矩阵 |
| 6 制卡 | 收 3 号席 7 候选，成卡 <=5 张；号位禁与在册 535 重名 | 新卡数＝卡池增量实测（本班基线 535） |
| 7 考工 A | 沿已跑通的 class D run_card 通道续出分 <=8 张 | 每出 1 张＝主册 +1 行且卡 status 翻转，两面对表 |
| 8 考工 B | **1 条**通道实测三态（抄 7 号席，不领新卡） | 三态明写：可跑／跑出的是哪一面／跑不出来卡在哪一闸 |
| 9 成绩官 | 追平 rows[82]→rows[现值]；占领区摘要在 5 号席交付前维持"闸未开"声明 | 摘要首版矩阵以 5 号席的 csv 面为前置，禁硬凑 |
| 10 本席 | 已下达第四单 | — |
| 11 整装 | 四件自落（HEAD 查无）＋ 21:30 盘点 | git ls-tree HEAD 能数到本席四件 |

### 8 防重入条款（全线同文，SOP 3-B）

各席开班读**两址**游标取较新面：旧址 `docs/_working/automation_campaign/pNN_*/checkpoint.md`（落地面）＋新址 `docs/04_research_records/cross_domain/automation_campaign/pNN_*/checkpoint.md`（桩面）；两址皆 25 分钟内有心跳＝上一班在跑，只写一行短报退出。运营面（派单／脉冲／自家台账）落笔前后各做一次 bytes＋sha256 前缀＋节数三查，被重置即按 `.runtime/tmp/p10_evict_1015_0744/` 快照重放，勿凭记忆重写。

### 9 待落地追加（指令面补丁寄存处，v1.5.1 在途件落地后一次合入）

- 第五条通令文本：游标读数**必须两时点采样**，单点读数不得写进派单（本班更正一立法）。
- 第六条：十席落地面唯一化＝`docs/_working/automation_campaign/`；新址写入前先查 git ls-tree HEAD 计数（未跟踪面写入必撞 CREATE-GUARD 且被整档快照覆写）。
- 第七条：入袋前必须核"袋吸的是哪一面"——袋内 ledger blob 字节数 < 现盘字节数即禁投，先做严格超集袋。

### 10 待 Owner 呈批面（本班新增第 8、9 两项；本席不代裁）

1. 采购三件（分析师预期／分钟线／L2）——SOP 附录 B 原样待批。
2. 盘口类候选门柱是否沿用价量族五键（03 班 3 节已给区分面实测）。
3. 186 张 /01 裸骨架卡语义参数（转正须具名子题或裁定退役）。
4. 07／07b 已 4 行超限＝换 fresh holdout 呈批或封存；**本班补料**：L1-S2 节点面累计 42 行判定＝全线最大集中面，"节点面是否计入同对象月度预算"待覆核。
5. 提交链 convoy：队头 6.59h、pending 91、本线四只 p10 袋全 pending 且袋内字节是旧面。
6. 生产线运营面从未落 HEAD：是否开落地优先通道或先降频（现况＝交付全压未落地面，一次外部重生即整片蒸发，本班与 9 号席各自实测到一次）。
7. 晨报承载面归属冲突：`docs/_working/cmd_ledger/` 被外来搬迁，晨论文本本席暂落自家台账＋派单册。
8. **主区 index 锁检疫授权（本班新增，全线写面卡这一枚）**：三证已齐（0 字节／龄 47 分不动／无存活 10 分钟以上 git 进程），黑匣子每 5 分钟记 `write-tree rc=128: remove the file manually to continue`。在册手法＝`os.replace` 移到仓外 `.runtime/tmp/lock_quarantine/`（不删可复原），移开应 1 分钟内见效、不见效即定性错、停手重判。**要 Owner 一句话**：授权与否。本席不自动＝这是全部在途会话与序列化器共用的写面。
9. **席位家址定点（本班新增）**：本席已判旧址为唯一落地面并通令禁写新址；新址那份未跟踪副本（04 区永久目录）留删／转正／回填三选一属 Owner 门位，本席不代处置。


## 2026-10-15 第五单（班 st-qoder-p10-1015-06｜巡检 08:36-08:53 实测读数，date 校时）

### 0 复巡：上班通令兑现面＋对本席 05 班一处归因的更正（旧案卷留档不删）

- **兑现**：05 班第四单十三项点名动作里，① ⑥ ⑨ 三席当班兑现且仍在飞（游标 mtime 08:07／08:46／08:31），② ③ ④ ⑤ 四席交账（08:32／08:01／08:30／08:23）；⑦ 席游标仍 07:23 面但卡面 08:37:38 有 `TDM-E-L9-A03/calibration/02_880板块相对强弱持续性` 翻 examined＝考工口只此一路在跑；⑧ 席 07:52 交账后零动；⑪ 席连续六班零发车（游标 mtime 停在 10-14 23:16）。
- **更正（本班主上报项，落地链死因）**：05 班呈批第 8 项把"全线写面被主区 index.lock 挡住"当主因。本班实测池日志＝`exit=no_slot env_aborted=True budget_left=None` 今日 9 次、**首现 07:32:50**；`done/` 目录末次改动 07:37:41；`git log --since="90 minutes ago"`＝**0 笔**；budget_left=None 依 `scripts/governance/commit_queue_landing.py:4189-4197` 判＝非名额预算耗尽，而是波内 `LandingEnvironmentError` 置 env_aborted 终止整波（同文件 4170-4175 文档串自陈"项退回 pending 绝不死信"）。新死信三只逐字死因＝`TimeoutExpired: Command '['git', 'ls-files', '--debug']' timed out after 15.0 seconds`（正是自 01:07 起占住 processing 达 7.5 小时那只）／`landing 环境失败: git log -1 --format=%H -F --grep=[GW:...] refs/heads/dev ->`（空输出，两只）。⇒ **本班定性＝"git 命令 15 秒超时＋git log 空输出"型环境失败反复终止整波，落地链 07:37 后零吞吐；主区 index.lock 是共症不是主因**（锁 06:49 已在，而 06:49→07:37 之间仍落地 3 笔＝07:35／07:36／07:37 三只 chiefdead6 袋）。资源面同证＝reaper 自报 `commit_pct 90.11%／degraded=True／breached=ALERT-SYS-003`，且 CREATE-GUARD 因 `MemoryError` 构造失败而 fail-closed 打死一只袋（`chfinalw2-20261015-0002` dead_reason 逐字）。本席无机器面处置权，列呈批第 10 项。
- **对本席 04 班结论的补充**：04 班判"主区锁使本席 git add 做不了＝成果零落地保护"，05 班实测改判"队列正门不受该锁影响"，本班再补一条＝**入袋面持续健康**（`blobs/` 目录 mtime 08:37、pending 109→103 波动、processing 1→4＝池仍在领件），受害的是**落地步不是入袋步**。下班勿再把两者混报。

### 1 全线水位（两时点采样：T1 08:36-08:37、T2 08:47-08:50，取较新面＝05 班立法判据第二次适用）

| 面 | T1 | T2（现值） | 上班（05 班） | 判读 |
|---|---|---|---|---|
| 游标推标 | 8/11 | **9/11**（1-6、7、9、10；⑥ 08:46 再推一批） | 8/11 | ⑧ 席 07:52 后零动 61 分、⑪ 席六班零动 |
| 卡池 | 542＝prereg 184／empty 186／blocked_on_data 71／examined 63／blocked_on_impl 38 | **544**＝prereg 184／empty 186／blocked_on_data 71／examined 64／blocked_on_impl 39（两时点各自加总闭合） | 535 | +9（对上班）；本班窗口内 +2 张当班新卡，examined +1＝吞吐环仍在走但极慢 |
| 成绩采集面 | 主册磁盘面 rows 83／pass 2／fail 81／115036 B；index 面 105598 B | 同值（零增量） | 176 判定 | **三面并存坐实**：磁盘 83／index 75 面／HEAD **0 件**（`git ls-tree -r HEAD -- docs/04_research_records/backtest/scores/`＝0，本班自跑复证 ⑨ 席） |
| 迭代预算 | iteration_history 55 行／6 个对象 | >3 行仅 `TDM-X-R1-01`＝4 行（在册暂停态维持） | 07/07b 各 4 行 | 本班零新违例、零新处置单 |
| 队列 | pending 109／processing 1／done 774／dead 124 | **pending 103／processing 4／done 774／dead 127** | 91/3/774/121 | done 三时点同值 774＝**70 分钟零落地**；dead +3 全属本线外会话；本线六袋仍全 pending（四面 ls 逐席实测：pending 6／processing 0／done 0／dead 0） |
| 队头 | 00:55:13 那只，龄 7.75h | 同 | 6.59h | convoy 继续加深 |
| 落地通道 | 主区 `.git/index.lock` 0 字节／mtime 06:49:56／龄 1h47m | 龄 2h03m 仍不动 | 47 分 | 锁面不变；死因定性见 0 节更正 |

### 2 查重（本班主战场＝⑥ 席 07:55-08:38 新成卡 vs ③④ 席候选册）

- 卡池唯一性两套尺：`card_id` 唯一集 **544/544＝零重名**；文件名去重零重复。判据面＝逐卡 yaml 解析非目录计数。
- ⑥ 席本班新成卡与上游候选逐一对位，**无一条新造题**：`TDM-E-L9-A02/calibration/03_obi_l1_imbalance`／`04_wmp_deviation_close_pair`／`05_fivelevel_slope_asym`／`06_order_evap_proxy`／`07_closeband_obi`（07:55:54 五张）＋`08_effective_relative_spread`／`A06/04_tick_rule_largeflow`（08:11:35 两张）＝③ 席 20261015-p03-01 批 7 候选；`A06/05_mfgap_inst_retail_direction_gap`／`A02/09_seal_instant_orderflow`（08:37:49）＝③ 席 p03-02 批 MFGAP-008／SEAL-012；`A17/calibration/02_研报评级调整事件研究`（08:38:14 转 preregistered）＝① 席 B-3 建设单对位。
- ③ 席 money_flow 三条市场级折叠被正交闸判 rc=5 重复（其游标自述）＋⑨ 席 04 班 PR=2.1272 权威读数（`lu_count↔lu_ratio=0.9949`／z20 对 0.9998）＝**同轴两形禁各计一员**的计量口径沿用，本席不改判据。
- **三池混写纠正（指令面，非判据）**：③ 席"池＝⑨ 席 pool6 六序列/共同日 1855"与 ④ 席"官方 15 员池实测 0 CSV"**两条都实测为真，指的不是同一个池**。通令＝报正交闸读数必须点名池面（`pool6 绕行面` ＝6 员／`ibt_runner MEMBERS 面`＝15 员），禁把"闸未开"当两池统称写进游标；15 员面在 ⑤ 席物化前一律记"该池无源"，pool6 面一律记"绕行面，非正式面"。

### 3 断供纪律与迭代审计（SOP 工序 5）

- `src/zephyr/data/config/known_data_gaps.yaml` 逐行走尺（键名实测＝`- id:`，条目 77、带 created 75）：created≥2026-10-14 者 **1 条**＝`sector_fund_flow_depth_cap_no_free_backfill`（① 席当班登记，created 2026-10-15）。该条 `searched_channels` **四腿齐**（akshare 东财历史腿／tushare moneyflow_ind_dc／同花顺即时腿／聚宽 get_money_flow_pro），每腿带 outcome＋evidence＋failed_at 本机实测时刻，且第四条自陈"属花钱项转 Owner 门不自购"。⇒ **判合规、打回 0 条**＝本线今日第一条达到 SOP 三渠道标准的断供登记（旧账 73 条无 searched_channels 属采集线历史存量，不代追）。
- 迭代纪律：>3 行/月 仍只有 `TDM-X-R1-01`（07／07b 各 4 行，在册暂停维持）；本班零新处置单。⑨ 席 04 班补料面（L1-S2 节点累计 42 行判定＝"节点面是否计入同对象月度预算"）口径仍待覆核，本席按行数保守计量不放开续考。

### 4 巡交接（下游收不上上游产出＝修上游落点/格式，不动判据）

| 断点 | 实测 | 处置（指令面） |
|---|---|---|
| ⑨ 席正交产物 → ③④ 席日常消费 | 唯一机读 PR 产物活在 `.runtime/tmp/st-qoder-p09-1015-04/pool6/`＋`pool6_report.json`＝**会话私面**，AGENTS §9.4 临时区有 TTL；下班复跑即无源 | ⑤ 席本班首件＝把 ⑨ 席仓外绕行正式化（列名契约 `trade_date,value`→`date,sig` 一行之差＋`ART_ROOT`＝`docs/_working/integrated_backtest/` 目录实测不存在需建）；正式面产出前，③④ 席引用 PR=2.1272 一律标"绕行面读数" |
| ① 席建设单 → ② 席回函 | to_builder.md 已 29781 B（B-1..B-12 在面），② 席游标"已收口／有一件跨班在途批"但**无逐条可得性回函** | ② 席本班首件＝对 B-11／B-12 给"可得／不可得／转呈批"三态回函（B-12 的 tushare daily_basic 深史腿与 namechange is_st 腿 ① 席已本机实测，② 席只需判施工通道） |
| ④ 席卡07/08/09 → ⑤⑥ 席 | ④ 席 to_impl.md 已写六条判据级约束（分母择一／禁全域线性排序／共线预警／双臂分考／PIT 取 announce_date／标度互证） | ⑥ 席本班收件面含这三卡，但 ⑤ 席游标下一班候选只列了三项且**未含 ④ 席 SIC-…-P04-07/08/09**＝接单面未接住；⑤ 席本班配额首句先做 ④ 席三卡与自身候选的对表，缺项明写"排期到第几班" |
| ⑥ 席呈批件 → Owner 呈批册 | ⑥ 席自述"呈批真源 04 册连续第四班不可写，OD-11..17 共 7 件寄存本席台账" | 席位家址沿用 05 班定夺＝旧址唯一面；本席把 OD-11..17 计入呈批面第 11 项（数量口径），**文本不代转、不改写**（属 ⑥ 席写域） |

### 5 派单（按瓶颈定配额；各席本班首句一律＝两时点采游标自证＋三面 sha 对表；报行数须声明读面 index／磁盘／HEAD）

| 席 | 本班配额 | 唯一交付判据 |
|---|---|---|
| 1 数据源 | 在飞即收口：B-11/B-12 已出单，本班只做"新登记断供是否四腿齐"自证（已达标，勿重挖） | 新登记每条四字段（channel/outcome/evidence/failed_at），零新增也写"搜过什么为何 0" |
| 2 数据建设 | **本班唯一件＝B-11/B-12 三态回函**＋to_datasource 四项在册口径登记（JOIN 用裸 symbol／kline turnover 死列／index canonical 逐指数未归一／daily_valuation 末日塌陷） | 回函行数与 B 号一一对表，登记项写明册名＋行号 |
| 3 库内挖矿 | money_flow 市场级三折叠已判重复＝**停止同轴续挖**；改挖 ⑨ 席空白轴地图未占两轴（波动率换构造、情绪重建），禁与 avg_abs_ret 本体共线 | 新候选数＋逐条差异面；引用 PR 须标池面名 |
| 4 全网矿工 | 卡07/08/09 已出，本班＝把"共线预警 0.68（未复现）"做成可复跑实测或撤该条；再走一轴 | 该数值要么给本库实跑读数要么明写"未复现禁当已证" |
| 5 实现 | **首件＝④席三卡对表补缺**，次件＝正交面板正式化（4 节第一条）；游标 `last_run` 写法须为 date 实测区间，禁写未来时刻（本班实测 07:50-09:15 vs 收班 08:53） | 交付件路径＋真钩子复跑计数；时戳与 date 对表 |
| 6 制卡 | 收 ③ 席 p03-02 余下 MFCAL-011/MFDSP-010 两条判是否成卡或判重复；号位禁与在册 544 重名 | 新卡数＝卡池增量实测（本班基线 544） |
| 7 考工 A | 已跑通通道续出分 ≤8 张；A03 族（880 板块）是新面，出分前先只读普查该面 data_binding | 每出 1 张＝主册 +1 行且卡 status 翻转，两面对表并报读面 |
| 8 考工 B | 本班唯一件＝**领 ⑦ 席同一条已跑通通道**出 1 张真分（不是再交普查案卷）；连续两班零出分则本班须点名卡在哪一闸并转 ⑤/② 单 | 主册行数增量 ≥1 |
| 9 成绩官 | 追平 rows[现值]；占领区摘要维持，15 员池 PR 在 ⑤ 席正式面产出前维持"该池无源"声明 | 摘要每行标池面名与件路径 |
| 10 本席 | 已下达第五单 | — |
| 11 整装 | 本班唯一件＝**首次发车**（六班零动）：四件自落＋21:30 盘点；无件可整也要交"无可整原因"一行 | `git ls-tree HEAD` 能数到本席四件，且游标 last_run 非"—" |

### 6 防重入条款（全线同文，SOP 3-B）

开班读两址游标取较新面（旧址＝落地面唯一，新址＝禁写桩面，沿用 05 班第 6 节定夺）。**闸面只认 `pulse/queue_depths.md` 末行时戳＋25 分**；本班末行 08:53 ⇒ 下一班 st-qoder-p10-1015-07 最早 09:18 后发车。各席收班前须做"盘面 bytes＋sha256 前缀＋节数"三查，被外部重置即按 `.runtime/tmp/p10_evict_1015_0744/` 快照重放，勿凭记忆重写。

### 7 待落地追加（指令面补丁寄存处，落地链恢复后一次合入）

- 05 班寄存三条（推标末步三面 sha 自证／GPU 看门人路径／两时点采样立法）仍寄存未合入——本席十席 instruction.md 外来 v1.5.1 staged 在途面未清，合入＝归属篡改，故本班仍不写各席指令本体。
- 本班新增两条：其八＝"闸面只认脉冲册末行＋25 分，派单正文与脉冲册不得各写一个时刻"（03 班 R2 抓到的两闸面打架，本班复现于 ⑤ 席游标未来时戳）；其九＝**报卡池／行数／袋数须同批给"读面"与"时点"**（index／磁盘／HEAD 三面与 T1／T2 两时点），⑦⑨ 两席本班已各自栽在同一名词不同读面上。

### 8 待 Owner 呈批面（本班新增第 10、11 两项；对第 8 项归因降级；本席不代裁）

1-4 沿用（采购三件／盘口门柱／186 张裸骨架卡／07-07b 超限换样或封存＋L1-S2 节点面口径覆核）。
5. 提交链 convoy：队头龄 7.75h、pending 103、本线六袋全 pending（01 班 3 只袋内 ledger blob 是现盘严格子集或分叉面，落地次序风险在册）。
6. 生产线运营面从未落 HEAD（`git ls-tree HEAD -- docs/_working/automation_campaign/`＝40 件，但 dispatch／pulse／feedback／iteration_history 与 ⑪ 席四件全查无）：是否开落地优先通道或先降频。
7. 晨报承载面归属（cmd_ledger 被外来搬迁且未落地）。
8. 主区 index.lock 检疫授权——**本班把它的定性从"全线写面主因"降级为"共症"**（06:49 至 07:37 之间仍落地 3 笔），锁龄已 2h03m 仍在；检疫手法与"移开 1 分钟不见效即停手重判"条款沿用 05 班。
9. 席位家址定点（旧址唯一面已通令，新址那份未跟踪副本留删／转正／回填三选一）。
10. **新增（本班主上报）：落地链 07:37 起 70 分钟零吞吐，死因＝波内 git 命令 15s 超时＋`git log ... refs/heads/dev` 空输出型环境失败**；同窗系统 commit 90.11% degraded／CREATE-GUARD 因 MemoryError fail-closed 打死袋／`git ls-files --debug` 超时使一只袋占住 processing 7.5 小时。要 Owner 一句话＝**是否允许降低池并发或先腾内存**（属机器面，本席不自调；不腾则全线交付持续压在未落地面）。
11. 新增：⑥ 席 OD-11..17 共 **7 件**呈批文本因"呈批真源 04 册连续第四班不可写"寄存其自家台账——本席只报数量与承载面，不代转不改写（转呈批通道属 Owner／正式通道）。


## 2026-10-15 第六单（班 st-qoder-p10-1015-07｜巡检 09:36-09:58 实测读数，date 校时）

### 0 复巡：第五单兑现面＋对本席上班断供尺的一处更正（旧案卷留档不删）

- **兑现面（游标 mtime＋台账字节实测，非账面引用）**：① 在飞（checkpoint 09:42，累计 26 项，新出 B-13/B-14＋断供 1 项四腿齐）；② 交账并已收口跨班批（09:47 段：研扫 09:43:11 终态入库 93 行⇒立即复跑 `rating_change`（FINAL 147,033=146,940+93，mismatch=0）与 `consensus_daily_build`（Oct 段 max(last_report_date) 09-30→10-14））；③ 03 班交 11 候选＋正交闸首出过账 2 条，04 班在飞（09:44）；④ 04 班交卡10/卡11 并把第四闸从"缺席"改判"可用"；⑤ 02 班交账（修⑨ 净费参数面 7 passed）、03 班在飞（09:46）；⑥ 06 班 09:32 建袋；⑦ 02 班在飞且主册 83→84 行（09:38:34）＝"续出分"兑现 1 张；⑧ 02 班 09:32 交账＝**第五单"出 1 张真分"未兑现（连续三班零出分）**；⑨ 07 班交账并给出机制级定性；⑩ 本席；⑪ **七班零发车**（checkpoint mtime 仍 10-14 23:16、游标"未开始"）。
- **对上班的更正（本席自己的尺，另起一节留旧案）**：05 班把"未产新解锁"记为 ② 席义务面，本班实测 ② 席 09:47 段已交内容级证据并**主动改判自己上一段"零解锁"为"1 张卡的前提延展"**（A17/02 事件窗截点可放到 `publish_date<=2026-10-14`；A17/03 的 10 月段实测已改变 `eps_consensus` 数值 20.831875→20.8745）。⇒ 下游若仍按 08:15 段"10 月零行"施工即过期读数。
- **断供尺谓词更正**：06 班用"逐行有无 `searched_channels`"量断供合规＝把**内部态登记**（empty_column／empty_table）也算进断供单面。本班按真谓词复量＝`status==no_source` 全册 7 条，其中 created≥10-14 者 **1 条**（`sector_fund_flow_depth_cap_no_free_backfill`，四腿各带 outcome＋evidence＋failed_at）⇒ 判合规、**打回 0 条**（结论与上班同，但尺口径已换，下班勿再混量）。

### 1 全线水位（两时点采样：T1 09:36-09:41、T2 09:51；每项声明读面）

| 面 | T1 | T2（现值） | 上班终值（06 班 08:53） | 判读 |
|---|---|---|---|---|
| 游标推标 | 10/11 | 10/11（仅 ⑪ 未开始） | 9/11 | ⑦⑧⑨ 已按通令推标；⑪ 七班零动 |
| 卡池（磁盘面，逐卡 yaml 解析） | 546＝prereg 184／empty 186／blocked_on_data 71／examined 64／blocked_on_impl 41 | **同值 546**（两时点各自加总闭合＝546） | 544 | +2 全落 blocked_on_impl；**examined 与 empty 两班零动**＝吞吐环与转正环同时停走 |
| 成绩采集面（磁盘面） | rows **84**／pass 2／fail 82／116029 B／sha 前缀 4f986ec7／mtime 09:38:34 | 同值 84 行 | 83 行（115036 B／24ef736d） | 本班窗口 +1 行（⑦ 席 880 板块族）；index 面与 HEAD 面见 4 节回退弹 |
| 迭代预算（从分数册内容量测，非散文行） | 84 行／65 个对象／run_id 零重复 | 同值 | 在册 07/07b 各 4 行 | >3 者 **2 个**、=3 者 **3 个**（逐值同 ⑨ 席在册记账＝尺的正对照成立） |
| 队列 | pending 105／processing 1／done 793／dead 129 | **pending 114／processing 1／done 793／dead 132** | 103/4/774/127 | done +19 但对 06 班终值零增；**本班窗口 09:09:02 后零落地（42 分）**；dead +3 非本线 |
| 本线袋（`q-20261015-st-qoder-p*`） | pending 64 | **pending 71**（12 分钟 +7＝各席在交件） | done 0／dead 0 | done=dead=0＝本线今日**零落地零死信**，71 袋全压在未落地面 |
| 队头 | `st-chiefdead6-20261015-0027`，waiting 30018s＝**8.34h** | 同 | 7.75h | convoy 继续加深，非字母序饿死（在册该因已过期） |
| 系统水位 | commit 95.74%／ram 76.7%／cpu 80.6%／degraded=True | **commit 95.9%／ram 80.6%／cpu 85.7%**，breached=ALERT-SYS-001+003 | 90.11% | 内存压力对上班读数**继续变坏**，而落地恢复过 19 笔＝不做单因归因（06 班呈批第 10 项仍开） |

### 2 查重（本班主战场＝卡池唯一性＋新卡面的落地保护覆盖）

- 两套尺各自跑：`card_id` 唯一集 **546/546＝零重名**；文件名三元组（`<module>__<family>__<step>` 前 3 段）唯一集 **546/546＝零重复**。正对照＝向计数器注入一份已知副本，尺必报 1 个重复（实测成立）；负对照＝`node_id` 面 186 个节点对 546 张卡，**重复是设计而非事故，禁当查重结论**（上班若报"节点重复"即尺错）。
- 新卡面保护普查：`git ls-files --others` 未跟踪新卡 **15 张**＋工作区已改未暂存 **11 张**，逐件对全根 4653 只袋的 files 清单求覆盖＝**26/26 命中**（`BAGS_SCANNED 4653 / DISTINCT_FILE_KEYS 15711`）。⇒ 判"有 blob 保护、无 HEAD 保护"，非"裸件"；下班勿重复报警。
- ⑥ 席本班新增卡与上游对位：其 p06-06 袋含 `L9-A02__calibration__10_close_session_amount_share`／`11_open30_amount_share`＝③ 席 p03-03 批 CAND-P0-MITAILV-013／CAND-P0-MIOPENV-014（两卡 `origin` 字段逐件命中，非推断），**未见新造题**；③ 席自报 11 条候选里 015/016 系窗敏感翻转按不利侧记重复＝沿用在册口径，本席不改判据。

### 3 断供纪律与迭代审计（SOP 工序 5，本班出 2 张处置单）

- 断供：打回 **0 条**（谓词与读数见 0 节）。今日新登记 3 条中 2 条为内部态（`shareholder_count_quality_flag_dead_column`／`factor_signal_zero_rows_writer_never_ran`，各带 evidence 与责任席位指向、自陈"不属找源面"）⇒ 不纳断供尺，但须由 ⑤⑥ 席消费其结论（quality_flag 恒 1＝任何按它过滤的条款静默退化）。
- **处置单 D-01（超限＋幽灵领卡面叠加，本班主上报）**：`TDM-X-R1-01/comparison/07_五态仓位锚定版` 与 `07b_复位阶梯锚定版` 各 **4 行 > 上限 3**，且 07b 的**卡面 status 仍是 `preregistered`**（有 4 行分数而无 examined）＝队列与卡面都不挡第 5 轮考。处置＝⑥ 席当班把两卡翻至在册终态或挂禁考标记；⑦⑧ 席本班起把这两张列入禁考名单；"换 fresh holdout 呈批 or 封存"仍属 Owner（呈批第 4 项），**本席不代裁**。
- **处置单 D-02**：`TDM-E-L1-AGG/calibration/02_四档风险轴前向收益单调` 同型＝分数册有行而卡面 preregistered（本班集合差实测 2 张，另一张即 07b）。修复位＝⑥ 席翻面＋⑨ 席报数时声明读面。

### 4 本班头号发现（吞吐环的门锁在卡面一键，不在引擎）

- 实测两时点：**T1 09:41＝27/184 张 `preregistered` 卡缺 `oos_window_ref`（26 张本卡自带 `window.oos`）**；**T2 09:58＝25 张（24 张有 `window.oos`）**——差的 2 张是 **⑥ 席当班（p06-06）已补**的 `TDM-P-P2-04/calibration/06`、`/07`（件 mtime 09:57:19，正是 ⑧ 席游标点名"只差一键"那两张）；唯一无窗者不变＝`TDM-X-S1-03/comparison/02_dualwindow`。补键＝照抄本卡冻结值，属"改指向"不属"改判据"，写域在 ⑥ 席。在册三闸第 2 条（执行器只读 `oos_window_ref`、不读 `window.oos`）实跑已证⇒ 这是 ⑦⑧ 两席零出分链上**成本最低的一把锁**。
- 诚实边界：补键只解第 2 闸。第 1 闸（IC 有 30 对/日地板，杀持仓池 panel 卡）与第 3 闸（机判词表仅 5 键，⑧ 席实测 60 个越表键）仍压着这 25 张的大部分（T2 面 24 张属 `TDM-P-*` 持仓/组合族，其中 **22 张 `signal_kind=panel`**）。⇒ 派 ⑥ 席**按三闸分箱**，禁把"补完键"报成"可出分"。
- 分数馆回退弹复证（承 ⑨ 席 07 班机制定性）：本班自跑 `git ls-tree -r HEAD -- docs/04_research_records/backtest/scores/`＝**0 件**、`git ls-files`＝**30 件**；并 grep 到 `scripts/governance/commit_queue_landing.py:3436` 确为 `old_dev = self._dev_head()`（引用落笔前已核命中）。⇒ 该馆 base 与 ours 同时不存在时"取袋面"＝**旧面回退是仲裁默认而非竞态**；修法方向＝该馆先入 HEAD 或让"base&ours 皆缺而工作树更新"fail-closed，禁弱化仲裁本身（属机器面，列呈批第 12 项）。
- 事件登记（肇事会话不追查、不代修）：09:29 一波批量重生触及 10 个席位件（p02/p03/p04/p06/p09/p10 的 checkpoint 与 p02/p06/p09/p10 的 ledger、iteration_history.md，同一分钟）。本席两件前后字节同值（ledger 52151 B／checkpoint 649 B，本班 09:35 首读 vs 09:51 复读）＝**零损失**；他席件字节是否被动本席无写域判定，已在各席游标可见面内自证（②⑥⑨ 内容仍在位）。

### 5 巡交接（下游收不上上游产出＝修上游落点/格式，不动判据）

| 断点 | 实测 | 处置（指令面） |
|---|---|---|
| ⑦ 席分数行 → 卡面 examined | 主册 83→84 行而 examined 恒 64（两时点同值）＝翻面滞后，下班复量若仍 64 即坐实 | ⑦ 席每班"出分即同批改卡面"，并报数时声明读面（磁盘/index/HEAD） |
| ② 席前提延展 → ⑥ 席卡面 | unblocked.md 09:47 段给出 A17/02 截点可放到 10-14、A17/03 建议自 10-12 起算，卡状态改判明写"不归本席" | ⑥ 席本班收件：按在册严口径（比 `window` 全字段含 regimes）处置这两张，禁挑同族他卡的窗 |
| ⑨ 席正交产物 → ③④ 席日常消费 | 唯一机读面仍在 `.runtime/tmp/st-qoder-p09-1015-04/pool6/`＝会话私面带 TTL；⑤ 席连续四班未正式化 | ⑤ 席本班首件（见 6 节），产出前 ③④ 引用 PR 一律标"绕行面读数" |
| ⑥ 席骨架卡门柱 → 生成器重渲染 | 在册实测：`_load_human_fields` 保留集仅 7 键、不含 `pillars_numeric`，重渲染即整块静默消失而 YAML 照 parse 绿 | ⑥ 席禁把数值门柱抄到 `generated: true` 骨架卡；修法（保留集扩键）在 ⑤ 席写域，列 6 节次件 |
| ⑪ 席 → 全线夜窗 | 七班零发车，非指令面缺失（第五单已给四件自落判据） | 本班把它从"指令面问题"改判为"排班/开机面问题"，列呈批第 13 项；本席不代开机 |

### 6 派单（按瓶颈定配额；各席本班首句一律＝两时点采游标自证＋三面 sha 对表＋报数声明读面）

| 席 | 本班配额 | 唯一交付判据 |
|---|---|---|
| 1 数据源 | 收口在飞 07 班；本班两件＝① margin 盘面 2,000 行 vs 源 2,347 行的 347 行疑似分页截断**出定性**（② 席已把读数移交）；② 补测 ④ 席在册未测面 `hk_connect_flow`/`northbound_hold_snapshot`/`index_valuation_daily` 跨度 | 每条给"搜过什么、为何 0"；新登记断供须 `status=no_source`＋≥3 腿各带 outcome/evidence/failed_at |
| 2 数据建设 | 首件＝研扫终态后续（93 行已入库、派生两腿已复跑）→ 把 A17 两卡的**内容级证据**转成 ⑥ 席可消费的回函；次件＝B-11..B-14 转派单已由本席落 ⑤ 席，本席不越界改 provider | 回函逐条对 B 号；不产"零解锁"负结论须给实测谓词面 |
| 3 库内挖矿 | 楼1 订单簿腿禁再产定义级候选（13 表实测）；改做 kline_60min 对照＋分钟腿横截面（折叠口径未裁前只出设计稿）；引用 PR 必点名池面（pool6 绕行面≠15 员池） | 新候选数＋逐条差异面；单位/剪枝两条结论须被 ⑥⑦ 消费后回收 |
| 4 全网矿工 | 剩余两轴＝情绪重建（楼10）与楼3 估值（被 daily_valuation 47 日阻塞）；卡11 的"闸可用但未测"须写清依赖 ⑤ 物化降维列 | 每轴一张可复跑件，禁"又新造 6 枚估计量"（同轴贴柱 pass 不算稳健） |
| 5 实现 | **首件＝正交面板正式化**（四班未落；判据见 5 节第 3 行）；次件＝骨架卡 `pillars_numeric` 纳入生成器保留集（连 signal_kind/preregistered_by/discipline/numeric_face_mapping_note）；三件＝B-11..B-14 采集写侧腿（② 席按角色边界转派）＋对 ④ 席三卡的排期到第几班 | 交付件路径＋真钩子复跑计数；**last_run 必须是 date 实测区间，禁未来时刻（本班实测 ⑤ 面写 09:05-10:15 而收班 09:37＝第二班复发）** |
| 6 制卡 | **本班首件＝余下 25 张缺 `oos_window_ref` 补键**（T2 09:58 实测；24 张照抄本卡 `window.oos`，第 25 张 `TDM-X-S1-03/comparison/02_dualwindow` 无窗→呈批或改判）＋按三闸给这 27 张分箱（补键后可考／仍不可考须点名⑤⑪）；次件＝D-01/D-02 两卡翻面或挂禁考标；三件＝A17 两张前提延展落卡面 | 新卡数＝卡池增量实测（本班基线 546）；补键前后各跑一次"解析值逐键对表"（禁只看 yaml 能 load） |
| 7 考工 A | 已跑通通道续出分 ≤8 张；A03 族已出 1 行（主册 84），本班须把 examined 翻面与分数行同批 | 主册 +N 行＝卡面 examined +N，两面对表并报读面 |
| 8 考工 B | 本班唯一件＝**领 ⑥ 席 09:57:19 刚补完键的 `TDM-P-P2-04/calibration/06`、`/07` 出 2 张真分**（第 2 闸已解）（其游标已给逐条可照做的开卡规格：宽表注入 close 面板本体、20 日暖机、向量化）；本班前置判据已成就（两键在盘上）；若复跑尺仍读缺则是 ⑥ 席袋未落地而非未施工，本班件改成"点名第 1/2/3 闸各自挡死几张"的分箱复核表，禁再交普查案卷 | 主册行数增量 ≥1，或分箱表逐闸计数加总＝75 |
| 9 成绩官 | 首件＝把分数馆 30 件**现值面**做成严格超集袋（逐件 Counter 对表＋对 `st-scorehome-20261014-0003/-0004` 两只旧面袋登记风险），撤袋不代裁；次件＝追平 rows[84] 并继续"读面声明制" | 每袋带全 7 件；判落地只信 `git log -- <册>` |
| 10 本席 | 已下达第六单 | — |
| 11 整装 | 第八次令＝首次发车（四件自落＋游标 last_run 非"—"）；无件可整也须交"无可整原因"一行（② 席在册缺口1 的 pool 桥接 yaml 是现成首件） | `git ls-tree HEAD` 能数到本席四件 |

### 7 防重入条款（全线同文，SOP 3-B）

闸面只认 `pulse/queue_depths.md` 末行时戳＋25 分，派单正文与脉冲册不得各写一个时刻。本班末行 09:57 ⇒ 下一班 st-qoder-p10-1015-08 最早 10:22 后方可发车。开班先读两址游标取较新面；收班前做"盘面 bytes＋sha256 前缀＋节数"三查，被外部重置即按 `.runtime/tmp/p10_evict_1015_0744/` 快照与本席自留 `write_deliverables.py` BLOCKS 重放，勿凭记忆重写。

### 8 待落地追加（指令面补丁寄存处，落地链恢复后一次合入）

- 05 班三条＋06 班两条仍寄存；本班复核＝十席 `instruction.md` 外来 v1.5.1 面**未清**（`git show HEAD:...p10_line_lead/instruction.md | grep -c v1.5.1`＝0，index 面＝3）⇒ 本席继续不写各席指令本体，写＝归属篡改。
- 本班新增第十条＝**断供合规尺谓词钉死为 `status==no_source`**（06 班用"逐行 searched_channels"混量内部态登记，见 0 节更正）；第十一条＝**查重键钉死为 `card_id` 与文件名三元组两套尺，`node_id` 禁当查重键**（186 节点／546 卡，重复是设计）。

### 9 待 Owner 呈批面（本班新增第 12、13 两项；本席不代裁）

1-11 沿用上班（采购三件／盘口门柱／186 张裸骨架卡／07-07b 换样或封存＋L1-S2 节点面口径覆核／提交链 convoy／运营面未落 HEAD／晨报承载面／主区 index.lock 检疫／席位家址／落地链波内 git 超时／⑥ 席 OD-11..21 寄存面）。
12. **新增（本班主上报）：分数馆落地仲裁的结构性回退弹**——该馆 30 件只活在 index、HEAD 查无，而合并器 `old_dev=self._dev_head()` 使"base 与 ours 同时不存在→取袋面"，故任一旧面袋后落地即洗掉新行（⑨ 席实测 8 对回退弹、7 册）。要 Owner 一句话＝**允许开一条"该馆优先入 HEAD"的一次性落地通道**（或授权撤并 `st-scorehome-20261014-0003/-0004` 两只旧面袋）；本席不自裁撤袋、不改仲裁代码。
13. **新增：⑪ 整装席七班零发车**——第五单已给完整发车判据而游标 mtime 仍 10-14 23:16，本班改判这不是指令面缺口而是**排班/开机面缺口**（该席无会话执行）。属 Owner 排班面；不排则 21:30 夜窗与 pool 桥接 yaml 无人接。

<!-- P10-1015-07-DISP> -->


## 2026-10-15 第七单（班 st-qoder-p10-1015-08｜巡检 10:24 起手／写盘 13:45，三时点读数 date 校时）

### 0 先自曝本班缺陷＝恒定班跑成 3 小时长班

本班 10:23:52 过闸发车（脉冲末行 09:57＋25 分＝10:22），按 30 分钟节拍应在 10:5x 收班；实测写盘时刻 13:45＝**实耗约 3 小时 22 分**，其间全线面值被上游推进、落地链在本班值守内复活并雪崩。缺陷定性＝⑩ 席把"量准"置于"按时交单"之上，且守护 idle 闸（§5）让本班锁在半途被收。处置＝本班起本席口径改为"测量分两轮：第一轮 25 分钟内出可读数的单，深挖件落 `.runtime/tmp/` 供下班复用"，本班这份长单不再拆。

三时点读数（同一把尺 `.runtime/tmp/p10_07/census_cards_07b.py`＋`.runtime/tmp/p10_08/bag_superset_probe.py`，10:26／10:33／13:21）：

| 面 | T1 10:26 | T2 10:33 | T3 13:21-13:43 |
|---|---|---|---|
| 卡池总数 | 549 | 549 | **550**（prereg 177／empty 186／blocked_on_data 71／examined 71／blocked_on_impl 45，加总闭合） |
| 成绩册 | 84 行／116029 B | 90 行／123768 B | **90 行未动**（mtime 10:31:26，sha 前缀 009c7bbc；pass 2／fail 88） |
| prereg 缺 `oos_window_ref` | 25 | 25 | **2**（⑥ 席续落 23 张，本班 10:33 基线作废） |
| 队列 pending／done／dead | 130／793／129 | 131／793／129 | **94／801／175**（末次落地 13:19:25） |
| 本线袋 dead | 0 | 0 | **93**（详见 §1） |
| 分数册三面 | HEAD 0／index 75 行／盘 90 | 同 | **HEAD 0／index 90（已追平）／盘 90** |

### 1 本班头号事件＝全线死信雪崩（13:13-13:43，处置单 D-05）

自然实验在本班值守内发生：链路在 09:09:02→13:1x 停摆约 4 小时后恢复，随即把本线产出成片判死。本线（`st-qoder-p*`）dead 面现有 **93 只袋**，dead_reason 分三族（本席逐只读回，非抽样）：

- **60 枚**＝`landing 异常: [landing] 非注册表族件双侧皆改真冲突（整文件三方，死信回退人工）`，冲突件全部是 campaign 热件：`dispatch/daily_dispatch.md`（⑩ 自家 01/02/05/06/07 班共 14 枚）、`feedback/to_builder.md`（① 席）、`feedback/to_impl.md`（⑨ 席）、`feedback/unblocked.md`（② 席）、`pulse/independent_signals.md`（⑨ 席）、各席自家 ledger（③④⑥⑦⑧ 席）。
- **31 枚**＝`ghost_session: 属主会话已死（heartbeat=exited／注册表无在册），自动重投被存活闸拒绝`（②③⑤⑥⑧⑨ 席各班），与 §5 实测的守护 1800 秒 idle 自退**同一条因果链**。
- **2 枚**＝门禁拦停：⑦ 席 01 班袋撞 GATE-PRECOMMIT-RUN（staged 面 own-scope 违规）、⑤ 席 01 班袋撞 TAKEOVER-PENDING（死会话遗留资源面须先按接管处方处置）。

判据面＝这是**安全结果非故障**（合并器拒的是"双侧皆改"，没有把旧面洗进新面），但生产后果是全线十余个班次的书面产出只活在袋 blob 里、未进任何落地面。按 SOP"当日四态分诊不隔夜＋内容级判据＋requeue 前先读 dead_reason 修因"，本班把 93 枚分三族派给各席自家处置（§6 每席首件），本席不代拆、不代销、不 requeue 他人袋。

### 2 本班 D-03 的预言被自然实验改判（旧判语留档不删）

本班 10:5x 曾写"队列按龄开闸＝先落 74/75 行旧面，分数册 90 行盘面将被整覆回退"。13:13-13:43 实际结果＝**合并器对"双侧皆改"直接判死而非洗新**，`st-scorehome-20261014-0003/-0004` 两只旧面袋（74/75 行面）连同其余旧面袋集体进 dead，分数册盘面 90 行**零回退**，且 index 面由 75 行追平到 90 行。⇒ D-03 的"多版本整档快照"事实成立（分数册 8 袋 5 版实测在册），但"开闸即静默回退"的机理**证伪**，正确表述＝"开闸即成片死信，产出滞留 blob 面"。据此 D-03 并入 D-05，呈批第 14 项按新事实改判（§9）。

### 3 门柱与吞吐普查（13:43 复量，本席自量不抄他席）

- 改卡 45 张对 HEAD 逐键差分＝**门柱级警报 0**；变动键分布 `oos_window_ref` 25（⑥ 席合规补键）／`status` 20（考工翻状态）／`lineage` 17／`unblocked_20261015` 1／`examined_face_20261015` 1。后两枚是 ⑥ 席加在卡面的**非在册顶层键**（10:3x 只见 L9-A17/02 一枚，本班复量多出一枚在 07b）＝加记不改判据，但归口未定（§6 ⑥ 行）。
- 未跟踪新卡 19 张；三元组与 `card_id` 均 **550/550 唯一**（注入副本正对照各报 1）。
- 卡面序列化回写仍在继续（块标量折平＋80 列回绕使 45 张卡的 git 面膨胀数百行）＝通令第十二条复述：**改卡面只动要动的那一行，禁整卡序列化回写**；值面本席已逐键核过等值，但字节面不可逐字对拍＝⑥ 席在册"两轮核逐字一致"工序失去抓手。
- 迭代预算（从成绩册内容量测）＝90 行／70 个对象／>3 者 2（07、07b 各 4）／=3 者 3／run_id 零重复 ⇒ **零新违例**；D-01／D-02 维持。
- 断供（谓词 `status==no_source`）＝全册 7 条，created≥10-15 者 1 条（`sector_fund_flow_depth_cap_no_free_backfill`，四腿齐）⇒ **① 席打回 0 条**；余 6 条 09-17/09-18＝采集旧账不代追。
- 分母两孔（D-04，尺 `.runtime/tmp/p10_08/flip_attrib.py`）＝正向孔 `TDM-E-L3-12-3/calibration/05_市场获利盘水位` 卡面 examined 而册上无行（HEAD 即如此）；反向孔 07b 册上有 4 行而卡面仍 preregistered（在册 `examined_face_20261015` 新键正为此而加，但状态未翻）。本席不代销。
- SOP 步骤倒置（⑦ 席）＝本班 10:2x 实测 6 张卡 10:10:28-10:16 先翻 examined、成绩 6 行 10:29-10:31 才落（SOP 序为 5 入库→6 翻状态）；本席 10:26 单时点曾误判"5 张空转销账"，10:31 复量证伪（旧判语留档）。令＝append 失败即停、不翻卡。

### 5 ⑦ 席"锁语义对偶"定策（在册正解为准，本席自造的"接班代持制"已撤案）

在册事实＝堵点①③⑦ 是同一件事的两半：懒注册 pid=0 不起守护 → 90 秒判活超时 → 他班 cleanup 按在册语义收走本席 claim（其自述"不是误杀"）；起守护＋入队续租＋队列 4-8 小时积压＝同席位自锁。在册死因第三条＝袋在飞时 release-all＋停守护＝在飞袋集体死信，故**"交班即放锁"与"抢占式 re-acquire"两个方向同样禁用**。本席本班初稿写的"接班代持制＝复取上班件"与之冲突，**读册后撤案**（v1 作废件留本席台账，不改写史实）。

本班把自己做成样本，量出**对偶的第三种形态**（实测）：10:45 同串跑"注册(pid=0)→起守护→heartbeat→acquire-batch"＝`acquired=4 denied=0`、守护 pid=58928 起活；11:16 复查 `.runtime/sessions/st-qoder-p10-1015-08/heartbeat.jsonl` 末行＝`{"status":"exited","reason":"idle timeout","idle_seconds":1816.1,"timeout_seconds":1800}`，同刻 `lock_files.py list --session` 报"持有者本席无任何文件锁"。⇒ **守护自带 1800 秒 idle 闸，`acquire` 不刷新 last_activity，恒定班实耗一旦 >30 分钟即使起手全对也会班中自退**。本班 3 小时 22 分实耗正是该闸的触发条件；13:13-13:43 的 31 枚 `ghost_session` 死信就是同一机理在他席的成片后果。

定策（只走在册合法面）＝
① 起手串＝`register(pid=0)`＋`_spawn_heartbeat_daemon(sid, 仓根, 30)`（**必带 `PYTHONPATH=<仓根>`**，否则 `No module named 'scripts.ops_guard'` 且 daemon_pid 返回 None）→ claim；**长班每 ≤25 分钟再跑一次同串刷新活性**，写盘与投袋落在刷新之后。判"守护在岗"只认两条实测＝heartbeat.jsonl 末行 `alive`＋进程表按 sid 命中；返回值与 rc=0 都不算。
② 自家件被上班**活**锁挡住＝不出三选项、不抢不放。合法两方向＝(a) 台账/游标从每袋必含件拆出、每班分件（指令面，本席可裁）；(b) 班次间隔与队列排空速度对齐（真解在提交链吞吐＝呈批第 10／14 项）。
③ 出料不等锁＝整册副本暂存 → difflib 自证"minus=0／plus=N 纯新增" → `git_commit.py --allow-overlap`（在册 67 号三分法＝叠加型）；**旗债必进台账**（袋 JSON 的 `meta` 实测不含 `--allow-overlap`／`--allow-non-worktree`，按袋面找旗必查无）。
④ 袋字节取命令启动时的 index 面＝enqueue 前先 add 自家路径、投后按 blob↔盘面逐件对拍自证，不信 rc=0；外层禁套限时壳（会掐死预检而 rc=0 零袋）。
⑤ 交班时袋未落地＝带锁带守护交班，并如实写"下一班会撞到我的锁"。
诚实标注＝②(b) 那一半指令面修不了，本席不假装定策能治好它。

### 6 各席本班／下班配额（首件一律＝D-05 自家死信分诊；全线禁重型并发）

| 席 | 首件（按此序） | 配额与红线 |
|---|---|---|
| ① | 自家 dead 面按 reason 分族拆账（to_builder 冲突枚数最多），内容级判据后走 mv 销账并留机生台账行 | 再处理≥3 缺数项；report_rc"可免费回补"改判须落进 `src/zephyr/data/config/known_data_gaps.yaml` 附四窗行数证据；断供登记继续四腿齐（今日 1 条合规） |
| ② | 同上分诊（unblocked.md 两件）；起手照 §5① 班中刷新活性 | ≥1 项建设或回补；rating_change 派生脚本 TTL 10-16 07:04 到期与否记台账 |
| ③ | ghost_session 死信 6 枚（01/03/04 班）＝产物只在 blob ⇒ 按在册抢救配方从 blobs 反查落地面 | 楼1 订单簿腿禁产定义级候选；≥5 新候选；024/026/029 已成卡禁重复产 |
| ④ | p04_scout_web/ledger.md 冲突 9 枚＝本班红件之首（10:5x 实测该件盘面字节无任何等值袋） | 扫≥5 渠道／产≥2 战法卡；`pead_earnings_event` 禁当现成 SUE 因子；两对同物异名转 ⑨ 并员 |
| ⑤ | TAKEOVER-PENDING 拦停件须先按接管处方处置再投（禁绕闸）；再跑 `_REGISTERED_TABLES` 扩容（本席 13:21 实测仍 5 表，`c1_market.kline_daily_hfq` 不在册） | 时段/极值/截面矩算子＝blocked_on_impl 45 张的主卡点；测试必绿＋tmp_path＋仓外 basetemp；commit_pct 高水位禁自造并发 |
| ⑥ | p06_prereg/ledger.md 冲突＋ghost 共 5 枚分诊；续补余下缺键 **2 张**（本班基线由 25→2，别按旧数派工）| 两枚非在册键（`unblocked_20261015`／`examined_face_20261015`）归口＝入卡面 schema 册或撤；禁整卡序列化回写（通令第十二条）；empty 186 全 generated 不再领 |
| ⑦ | GATE-PRECOMMIT-RUN 拦停件读 own-scope 违规面修因后重投（禁 --no-verify 类绕行）；顺序正令＝先 append 后 flip | 活分母 109／判据面通过 91 继续开 panel 面；单卡>15 分钟即 kill 记 finding |
| ⑧ | p08_examiner_b/ledger.md 冲突 2 枚分诊；唯一件仍＝`TDM-P-P2-04/calibration/06`、`/07` 两张（键已在，本班复量 prereg 缺键仅剩 2 张不含它们） | 水位 degraded 按成文口径推迟；禁补多日目标卡申报三键（D3 未修） |
| ⑨ | `to_impl.md`／`independent_signals.md` 冲突共 9 枚分诊；修⑪ 并员扩到 −1.0000／0.9958 两对 | 判卷增量钉成绩册盘面 90 行；D-04 两向销账；禁烧四条维持；分数册字节不碰 |
| ⑩ | 本单已交；自家 14 枚 dispatch 冲突袋＝全线最热件的镜像，分诊权在各席 | 本席不代裁撤袋／不改合并器／不碰判据册 |
| ⑪ | 四件套零袋认领＋mtime 仍 10-14 23:16＝第 N 班零发车，**不再派同文配额** | 排班/开机面缺口（呈批第 13 项） |

### 7 指令面寄存（本班复量）

十席 instruction.md 外来 v1.5.1 面：HEAD 命中 0、盘面命中 3 席（①⑦⑩）且这 3 席已 staged＝与上班同读数、零续落。故本班通令第十二、十三条（§3 序列化回写禁、§5 起手串与班中刷新）**依旧只寄存本册与本席台账**，本席对他席指令本体零触碰。

### 8 下班（st-qoder-p10-1015-09）首查三件

①93 枚本线死信的分诊进度（尺＝本席台账里的 dead_reason 三族计数命令）；②成绩册是否已进 HEAD（本班三面＝HEAD 0／index 90／盘 90，若仍 0 件则呈批第 12 项升级）；③`_REGISTERED_TABLES` 是否由 5 表扩容＋prereg 缺键是否清零（本班基线 2）。**闸面＝本单所附脉冲册末行时戳＋25 分钟**；下班务必在 25 分钟内交单，深挖件写进 `.runtime/tmp/p10_09/` 留给再下班。

### 9 待 Owner 呈批面（本班改判第 14、新增第 15；本席不代裁）

1-11 沿用上班。12 **仍开**＝分数馆三面 HEAD 0 件／index 90 行／盘 90 行，落地仲裁的一次性优先通道或撤并两只旧面袋的授权。13 **仍开**＝⑪ 席零发车（排班面）。14 **本班改判**＝原写"61 个多版本整档快照袋开闸有回退弹"，实测机理改判为"开闸成片死信、产出滞留 blob"（§2），要的一句话仍是＝**授权各席自决做单一超集袋并任旧面袋死**，或**先停 drain 由单点做全量超集化**；本席不自决撤袋（撤袋＝归属面）。15 **新增**＝93 枚本线死信里 31 枚是 `ghost_session`（会话守护 1800 秒 idle 自退而存活闸拒重投），要 Owner 定其一＝(a) 允许把恒定班节拍与守护 idle 闸对齐（改排班面，非指令面）；(b) 授权对各席死袋按在册 `CLI 手动 requeue 不受闸限` 逐袋人工强制重投。本席不自裁。

<!-- P10-1015-08-DISP -->

## 2026-10-15 第八单（班 st-qoder-p10-1015-09｜巡检 17:35 起手 date 校时）

### 0 本班一句话结论

**死信雪崩在"无线长值守"的 3 小时 48 分空窗里继续扩大：dead 由 13:47 的 175 → 本班 17:35 实测 305（+130），pending 由 94 排空到 0。** 本线头号瓶颈不再是挖矿，是**落地链成片自杀**——故第八单全线停发新挖矿配额，各席首件一律＝按 D-05 内容级分诊自家 dead＋走"取最新 HEAD 做单一超集袋、等四态再投第二袋"的在册处方（在册新证：超集袋在"前袋先落地"后仍判双侧皆改而死，唯一起效变量＝base 取最新 HEAD，见 memory `strict-superset-still-dies-under-three-way-file-gate`）。本席不代拆不代销（撤袋＝归属面，Owner 门位）。

### 1 实测读数（date 校时；health 官读因 git 20s 超时不可用，改用队列根目录文件计数，方法如实标注）

| 面 | 本班读数 | 取数法 | 上一班(13:47)对照 |
|---|---|---|---|
| 队列 pending | **0** | `find .runtime/commit_queue/pending -maxdepth 1 -type f \| wc -l` | 94 |
| 队列 processing | 1 | 同上 processing | 1 |
| 队列 done | 792（**文件计数法**，非 tool 值） | 同上 done | tool 报 801（口径不同，勿并比） |
| 队列 dead | **305** | 同上 dead | 175（+130＝本班头号事件） |
| 分数册盘面行 | **96**（132248 B） | `grep -c card_id` 于 exam_scores_v1.yaml | shift07 记 75→83、shift08 记 90＝逐班涨，本班盘 96 为现值 |
| 分数册 HEAD / index 面 | **本班未量**（git rev-parse 20s 超时） | — | shift08＝HEAD 0／index 90 |
| 卡池 exam_cards | 552 个 yaml | `find ... -name '*.yaml' \| wc -l` | p05/p06 普查 550（+2＝p04/p06 新卡） |
| 内存水位 | commit 86.36%／ram 69.2%／cpu 86.6%／**ALERT-SYS-001 breached**／worktree_changes 5511 | reaper --status | 起批即高水位＝全线禁自造重型并发（红线） |

`python scripts/commit_queue.py health` 本班实测**超时崩溃**（`git rev-parse --verify <blob>:p08_ledger.md` 20s timeout）＝health 通道在 git 面卡死。故工序 6"AI 层队列畅通"广播**本班不发**：pending=0 仅由文件计数侧证、tool 官读未成，且 D6 245 件原令逐条核对未做＝两证不齐，按指令卡"任一证不成立＝不广播只记堵点"处置（堵点入 §5）。AI 层台账新址**已定位**＝`docs/_archive/_working_cleared/ai_layer_vision/`（在册工序 6 首选命中，未再找 04 区）。

### 2 巡断线（游标停跳判据＝三证，非单看 mtime）

- **⑪ 席**：checkpoint `cursor: 未开始`／`last_run: —` 至今＝第 N 班零发车，与 shift07/08 同读数。判**排班/开机面缺口**（呈批第 13 项），非指令面缺陷，**本班不再派同文配额**（沿用上班在册裁定）。
- **⑤ 席**：游动到 1015-05 但 `last_batch: 零袋`＝三投均 DENIED 于锁外预检（WORKTREE-REQUIRED／无 multi-domain 旗／`--project-root` 车道反查无会话注册——三条各撞一闸，见 memory `lane-enqueue-three-gate-exclusion-20261015`）。属**通道面**非游标面；处方入 §6 派单，不改其 instruction 判据。
- 余八席游标均在动（p06 已自推到 09、p07/p09/p04 有本班读数）。**无"整文件覆写致旧游标盘面查无"的新形态**：本班对 p10 自家 checkpoint 用"只改顶部三行＋逐字搬回上班游标"的前缀超集制，删除集控制在最小（继承在册配方）。

### 3 巡交接（下游收不上→修上游产出格式/落点，不改判据）

- 在册链①「⑥退回裸骨架→③按 TDM 图补具名子题」：本班无新裸骨架回流，维持。
- ④ 席 10 枚未落地卡（HEAD ABSENT 新文件）＝下游 ⑤/⑥ 收不上的直接来源。④ 席 cursor ⑩ 已给可执行判据：这 10 枚结构上不可能双侧皆改（无 base），可**另起一袋专投、袋内不含台账**（避免再吃 ledger 双侧皆改签名）。本班据此把该单转派 ④ 席自投，本席不代投他席件（归属篡改红线）。
- ⑨ 席机读正交产物在会话私面 `.runtime/tmp/…/pool6/`＝有 TTL、复跑即无源（shift06 已派 ⑤ 席正式化）；本班复述该单未闭合，仍挂 ⑤ 席。

### 4 存放仲裁（工序 4，每班必做：两问判定）

本班新产物逐一过两问：①用完即删/仅活文档→留 `_working`；②永久要留且可复验（SQL/参数/file:line/裁定号锚点）→派该席走 promote 三步进 04。

| 产物 | 归属席 | 判定 | 出口 |
|---|---|---|---|
| 第八单派单／脉冲／本席台账 | ⑩ | 活文档 | 留 `docs/_working/…`，不 promote |
| ④ 席 10 枚 web_cards 战法卡 | ④ | 业务资产非 _working→04 型，属卡库落点 | 先**落地**（专投袋），非 promote 议题 |
| ⑨ 席 pool6 机读正交件 | ⑤/⑨ | 可复验（矩阵＋谓词），但当前只活在 tmp | ⑤ 席正式化后按证据链再判是否进 04；**证据链不全不准进 04** |
| 断链 sweep 三件套（broken_records/refs/summary） | X1/X2/⑤ | 永久可复验（file/line/batch/suggest 锚点齐） | 已在 04 区 `working_ref_sweep_20261015/`＝已合规，勿重复搬 |

本班**进 04 件数＝0**（无可直接 promote 的定稿：业务卡在卡库位、正交件证据链未齐、sweep 件已在 04）。无打回（各席无新的 _working→04 申请到达）。

### 5 断链修复战役调度（工序 5）＋ 核验放行堵点（工序 6）

- 批次分母（取自 `sweep_summary.json`，勿自造路径）：**B_永久区合计 440 处**（manifest 370＋未落地 11＋父目录在需核 59）→改指 04 永久区／**C_归档区_working_cleared 1813 处**→改指 `docs/_archive/_working_cleared/`／**D_同名模糊 39 处**→人工／**F_动态模板前缀仍活 2 处**／**E_彻底消失 196 处（123 唯一目标）＝Owner 呈批面，本席与各席勿动**。2490 broken 总数与令卡一致。
- X1/X2 批次本体**在施，本席不碰**（红线）。验收对照面＝`docs/04_research_records/governance/working_ref_sweep_20261015/`。**剩余处数本班未复量**（复量需重跑 sweeper＝重型扫描，且 reaper 已报 worktree_changes 5511 高漂移，高水位期不起重扫）；可派 ⑤ 席承接未完成批次，但须 commit_pct 落回安全区再起。
- 工序 6 堵点如实升级：`commit_queue.py health` git 子进程 20s 超时（`audit_landed_id_integrity` 里 `git rev-parse --verify <sha>:<path>` 卡死）＝health 通道当前不可信，pending 只能靠文件计数侧证；D6 245 件原令逐条核对**本班未做**（缺可对照的原令件清单入口）。⇒ 两证不齐，本班不发畅通广播。

### 6 各席本班配额（首件一律＝D-05 自家 dead 分诊；全线停发新挖矿，禁重型并发）

> 通用处方（本单唯一主线）：分诊后若须重投——**base 取最新 HEAD**（`git_commit.py` 前 `git rev-parse HEAD` 现算，勿用建袋时刻旧 HEAD）、**一个逻辑改动只投一袋**、**等该袋出四态再投下一袋**；超集袋在"前袋先落地"后仍会因整文件三方判双侧皆改而死，别指望连投收敛。

| 席 | 首件（按此序） | 配额与红线 |
|---|---|---|
| ① | 自家 dead 面按 reason 分族拆账（延续 shift08 三族），内容级 mv 销账留机生行 | **本班不派新缺数项**；断供登记维持四腿齐；高水位禁自造采集并发 |
| ② | unblocked/自家 dead 分诊；起手先刷活性（班中 re-register 撞 idle 闸前） | **不派新建设/回补**；rating_change 派生 TTL 记台账 |
| ③ | ghost_session 死信从 blobs 反查落地面抢救（在册配方） | **楼1/楼4 停产新候选**（雪崩期先清落地）；014 禁改绑 kline_60min 沿用 |
| ④ | **把 10 枚 HEAD-ABSENT 卡另起一袋专投（袋内不含台账）**＝本班交接链直补 | 停发新扫渠道/新卡；两对同物异名转 ⑨ 并员挂账 |
| ⑤ | 车道三通道各撞一闸**本班不自解**，先 `--base-head dev`＋车道内注册重试一投；三态齐前不重投 | 停 `_REGISTERED_TABLES` 扩容重扫（高水位）；blocked_on_impl 45 张维持 |
| ⑥ | 自家 dead 分诊；缺键基线由 shift08 的 2 → **本班复述 p06 已自投"23 补键＋2 撤键"，待下一班复量归零** | 禁整卡序列化回写（通令第十二条）；两枚非在册键归口沿用 |
| ⑦ | GATE-PRECOMMIT-RUN 拦停件读 own-scope 违规修因后重投（禁 --no-verify 绕行） | **停开 panel 面新分**（雪崩期）；顺序正令先 append 后 flip 沿用 |
| ⑧ | p08_examiner_b/ledger 冲突分诊；水位 degraded 按成文口径推迟 | **不派新开考**；禁补多日目标卡三键申报（D3 未修） |
| ⑨ | to_impl/independent_signals 冲突分诊；**判卷增量停手**（现盘 96 行，雪崩期不追分母） | 分数册字节不碰；修 ⑪ 并员扩两对挂账 |
| ⑩ | 本单已交；自家 dead 分诊权在各席 | 本席不代裁撤袋／不改合并器／不碰判据册 |
| ⑪ | 第 N 班零发车＝排班面，**不再派同文配额** | 呈批第 13 项 |

### 7 指令面寄存（本班复量）

十席 instruction.md 外来 v1.5.1 面：本席对他席指令本体**零触碰**（红线）。本班无新增通令；通令第十二/十三条沿用（卡面禁整卡序列化回写／起手刷新活性＋班中 re-register）。

### 8 下班（st-qoder-p10-1015-10）首查三件

①dead 是否续涨（本班 305，若再+则印证"无值守即成片死"，须把 D-05 各席分诊完成度上升呈批）；②分数册是否进 HEAD（本班盘 96／HEAD 未量＝health 超时，下班用 `git show HEAD:…exam_scores_v1.yaml \| wc -l` 单件量，别整档 health）；③④ 席 10 枚专投袋是否落地。**闸面＝脉冲册末行时戳＋25 分**；下班务必 25 分钟内交单，深挖件写 `.runtime/tmp/p10_10/`。

### 9 待 Owner 呈批面（本班）

1-11 沿用。12 **仍开**（分数馆三面 HEAD 0，本班未复量 HEAD）。13 **仍开**（⑪ 席零发车＝排班面）。14 **仍开**（授权各席自决单一超集袋并任旧面袋死）。15 **本班扩面**＝31 枚 ghost_session 之外，**空窗 3h48m 内 dead +130** 说明"线长恒定班一旦缺位即成片死信"，除 15(a)(b) 外增 15(c)＝是否把恒定班节拍与守护 1800s idle 闸硬性对齐（改排班面）；本席不自裁。**新增 16＝`commit_queue.py health` git 子进程 20s 超时不可用**，属工具/落地链面缺陷，本席只登记不代修（非指令面）。

<!-- P10-1015-09-DISP -->

## 2026-10-15 第九单（班 st-qoder-p10-1015-10｜巡检 18:10 起手／写盘时刻见本席台账，date 校时）

### 0 头号事件＝落地链已复通，且本班把上班三首查逐条量完（两绿一红）

**上班（17:44）留下的三首查，本班全部实测回批：①dead 续涨但已收敛（305→311/+6，其中 mtime>17:44 的新死仅 4 枚＝3 枚属 X1/X2 断链车道、1 枚属 ⑧ 席 ghost_session，本线其余各席零新死）；②分数册仍未进 HEAD（该馆 HEAD 面 0 件＝呈批第 12 项实测坐实）；③④ 席 10 枚 HEAD-ABSENT 专投袋已落地（卡池盘面 552＝HEAD 面 552，HEAD-ABSENT 由 10→0）。** 同时 16:00 起 `done/` 实测落地 27 袋、覆盖 p01/p02/p03/p04/p06/p07/p08/p09/p10 九席＝"雪崩期全线停发挖矿"的前提（落地链成片自杀）已被自然实验推翻，本单起**有条件复牌**。红旗一条＝**主区 index 现含 21 枚业务卡 staged deletion 且零对偶新增**（详见 §3-A），本席不代复位（改共享暂存区＝归属面，Owner/属主席门位）。

### 1 实测读数（date 校时；health 官读仍不可用，一律队列根目录文件计数法，方法随值标注）

| 面 | 本班读数 | 取数法 | 上班(17:44)对照 |
|---|---|---|---|
| 队列 pending | **1**（`q-…-x2-1015-0004` 18:10，非本线积压） | `ls .runtime/commit_queue/pending` 目录条目数 | 0 |
| 队列 processing | 1（x2-0003，18:03） | 同上 processing | 1 |
| 队列 done | **797**（文件计数法） | 同上 done | 792（+5） |
| 队列 dead | **311**（目录条目）／其中 q-*.json 308 | 同上 dead | 305（+6＝收敛，非续扩） |
| 16:00 后落地袋 | **27 袋**，九席覆盖（活尺＝本班 18:12 首跑 27、18:3x 复跑 **28**，复跑更高不属矛盾） | `done/*.json` 按 mtime 过滤 | 上班未量 |
| 卡池 exam_cards | 盘 **552**／index 531／HEAD **552** | `find -name '*.yaml'`＋`git ls-tree -r HEAD` | 盘 552／HEAD 未量 |
| 分数册 exam_scores_v1.yaml | 盘 **96 行**/132248 B／index **90 行**/123768 B／**HEAD 0 件（该馆 30 文件全 index-only）** | `grep -c card_id`＋`git show :<册>`＋`git ls-tree -r HEAD -- <馆>` | 盘 96／HEAD·index 未量 |
| 主区暂存池 | A **451**／D **894**／M 114（A·M 为活尺，18:3x 复跑＝453／116；D 两跑同值＝894） | `git diff --cached --name-only --diff-filter=A/D/M` 各计数 | 上班未量 |
| 迭代轮次 | 96 行＝72 distinct card_id，直方图 `{1:58,2:9,3:3,4:1,7:1}` ⇒ **>3 轮＝2 张**（4 轮・7 轮各 1） | ⑨ 席 13 班 `iteration_history.md` 在册读数（本班未重跑尺） | >3 者 2＝**零新违例** |
| 内存水位 | commit **86.96%**／ram 71.3%／cpu 84.2%／degraded=False／worktree_changes 5779 | `process_reaper --status` 18:20:59 实测 | 86.36%／5511＝**高水位未退**，全线仍禁自造重型并发与重扫 |

`commit_queue.py health` 本班**未再触发**（上班实测 git 子进程 20s 超时＝呈批第 16 在册）；本班所有队列读数均为目录文件计数，与 tool 值口径不同，禁并比。

### 2 巡断线（三证判停跳，非单看 mtime）

- **⑤ 席＝本班唯一"通道断线"**：游标在动（17:31）但 `last_batch: 零袋`，三投各撞一闸（WORKTREE-REQUIRED／COMMIT-SCOPE 2 域／SESSION-REQUIRED），且其字节已被他道 staged 进主区 index（`git diff --cached --diff-filter=A` 实测含 `signal_orthogonality.py`／`test_signal_orthogonality.py`／`gpu_watchman.py`，HEAD 面查无）＝**产物在 index、归属在 ⑤、落地链未通**的三不管态。处方见 §6-⑤，本席只改指令面不改闸。
- **⑪ 席**：`cursor: 未开始`／`last_run: —`／mtime 停在 10-14 23:16＝第 N 班零发车，判**排班面**（呈批第 13），不再派同文配额。
- **⑧ 席**：游标 18:01 在动，但其 06 班袋 18:11 吃 `ghost_session`（heartbeat=exited）＝**交单先于袋落**形态，非游标面缺陷；通令第十三条（起手刷活性＋班中 re-register）对它已失效，本班在 §6-⑧ 改为"出班前必须等袋四态或重取活性后按在册处方重投"。
- 余七席游标均在动（p01 17:40／p02 17:36／p03 17:11／p04 18:18 在飞／p06 18:16 已自推到 11 班／p07 17:13／p09 17:55）。**无"整文件覆写致旧游标盘面查无"新形态**＝本班未收到他席 checkpoint 前缀断裂读数。

### 3 巡交接与红旗归口（下游收不上→修上游产出格式/落点，不改判据）

**A（红旗，呈批第 17 新立）＝主区 index 内 21 枚 exam_cards 被 staged 删除且零对偶新增。** 尺＝`comm -23 <(git ls-tree -r HEAD -- <卡池> | grep .yaml | sort) <(git ls-files <卡池> | grep .yaml | sort)`＝21 枚；逐枚 `git hash-object <盘文件>` 与 `git rev-parse HEAD:<path>` 对拍＝**21/21 盘字节与 HEAD blob 全等**（＝纯暂存面删除，非改名非归档）；`relocation_manifest_20261015.yaml` 对 `exam_cards` **0 命中**（排除归档波解释）。面积＝L9-A01 6／L9-A02 10／L9-A06 2／L3-07-3 2／L1-S2 1／X1-R1-01 comparison 07c 1。本席处置＝**不复位、不 add**（改他班暂存面＝归属篡改红线），改为两件：①通令第十四条＝**高水位与 21 枚卡未复位期间，一切提交走队列正门（serializer 干净暂存区），禁从主区 index 直连提交**，直连会把这 21 枚净删落地；②上升呈批第 17 请 Owner 定复位归属与通道（须留存证）。清单已落 `.runtime/tmp/p10_10/staged_del_cards.txt`（21 行）供下班与属主席复用。
**B（④→⑤/⑨）＝web_cards 第五必备字段缺。** ④ 席 07 班自报盘面 17 枚逐件 `safe_load` 键名普查＝第五字段（数据源映射）缺失＝下游归一器收不上。判**产出格式面**非判据面：转 ④ 席自补（配额 §6-④），本席不改归一器。
**C（④→⑤/②）＝`src/zephyr/data/ch_reader.py` 的 `inject_final_strict` 对任何带 `WITH … AS` 的只读 SQL 崩。** 属采集面通用坑（非 ④ 席个案），HEAD 该件最后触及 e48a2775bea（10-10）；本席按 owner 制挂 **⑤ 席领单候选第 2 位**，同时告知各席在册旁路＝先把 CTE 物化成子查询或临时视图再读，**旁路只改写法不改判据**。
**D（①→②）＝ETF 深史回补单四腿齐，不打回。** ① 席 to_builder 在册＝检索通道四路实测＋失败原因逐条（含 `ak.fund_etf_hist_em` RemoteDisconnected 同型在册，与"未采信假域名 sse.org.cn 已标注未访问"）＝**断供打回 0 条**；转 ② 席按其当期宇宙判据（`fund_basic` 的 list_date/delist_date）排回补，验收三判据已在册。
**E（在册链①⑥→③）**：本班无新裸骨架回流，维持；断供无证据链打回 **0 条**；同对象迭代超 3 轮＝2 张（4 轮/7 轮，7 轮那张 ⑨ 席已自报"不再排复考"），**本班不新立处置单**（零新增，且旧两张在册）。

### 4 存放仲裁（工序 4，每班必做：两问判定）

| 产物 | 归属席 | 两问判定 | 出口 |
|---|---|---|---|
| 第九单／脉冲／本席台账 | ⑩ | 仅活文档 | 留 `docs/_working/…`，不 promote |
| 本席 `staged_del_cards.txt`＋读数尺 | ⑩ | 取证临时件、命令可重生 | 留 `.runtime/tmp/p10_10/`（TTL），**禁进 04**（无独立复验价值） |
| ① 席 ETF 回补案卷（四渠道实测） | ①→② | 永久要留**且**可复验（行数/票号/日期/写法与验收三判据齐）＝**够格** | 须先由 ② 席执行回补出**落地读数**再走 promote 三步进 04 数据源域；本班**只登记候选、不催 promote**（证据链末腿未齐） |
| ④ 席 web_cards 17 枚战法卡 | ④ | 业务资产、非 _working 文档 | 属**卡库落点＋第五字段补齐**议题，非 promote |
| 断链 sweep 三件套 | X1/X2/⑤ | 永久可复验，锚点齐 | 已在 04 `working_ref_sweep_20261015/`＝合规，勿重复搬 |

本班**进 04 件数＝0**（候选 1 件＝① 席 ETF 案卷，待 ② 出落地读数后成行）；打回 0 件（无新 promote 申请到达，无证据链不全的入 04 请求）。

### 5 断链修复战役调度（工序 5）＋ 核验放行（工序 6）

- 批次分母沿用 `sweep_summary.json`，**本班未自造**：B_永久区 **440**／C_归档区_working_cleared **1813**／D_同名模糊 **39**／F_动态模板前缀仍活 **2**／**E_彻底消失 196 处（123 唯一目标）＝Owner 呈批面，本席与各席勿动也勿代裁**。剩余处数本班**仍未复量**（复量＝重跑 sweeper 重型扫描，commit 86.96% 高水位期不起）。
- X1/X2 批次本体**在施，本席不碰**（红线）。但本班实测其**死因已换族**＝不再是我席的"双侧皆改"，而是门禁拦截：x2-0002（17:54 TAKEOVER-PENDING）／x1-0001（18:02 MAP-ALIGNMENT）／x2-0001（18:11 CREATE-GUARD 新建 .py 命中在册能力）。三枚按在册正解归口＝x2 走 TAKEOVER-PENDING 的 dirty_files 逐文件处方、x1 走 `generate_project_depgraph.py --force` 重建对齐、CREATE-GUARD 走新建声明通道补 creation_token——均由 X1/X2 自家拆，本席只登记族别不代拆。
- **工序 6 畅通广播＝本班不发**。两证实测：证一 pending＝1 非 0（X2 在飞袋）＝**不成立**；证二 D6 245 件与原令逐条核对＝本班未做（缺可对照原令件清单入口；AI 层台账新址 `docs/_archive/_working_cleared/ai_layer_vision/` 已在册，核对动作挂下班）。⇒ 记堵点不广播。

### 6 各席本班配额（**有条件复牌**：落地链已由 27 袋自然实验自证复通；复牌三腿＝①自家上一袋已出四态 ②base 取**最新** HEAD 现算 ③一个逻辑改动只投一袋、等四态再投下一袋）

| 席 | 首件（按此序） | 配额与红线 |
|---|---|---|
| ① | **复牌**：ETF 深史案卷续推（当期宇宙判据已交 ②）＋自家 dead 9 枚内容级分诊 | 断供登记须四腿齐（检索通道＋失败原因）；高水位禁自造采集并发 |
| ② | **复牌**：按 ① 席案卷排 ETF 历史回补（2019-01-04..2026-06 全宇宙，volume 单位先对拍再定标）＋自家 dead 9 枚分诊 | 回补须"来源独占"复证（在册重灌污染教训）；禁 `_REGISTERED_TABLES` 扩容重扫 |
| ③ | **复牌**：新候选挖矿可开，一逻辑一袋；自家 dead 12 枚分诊 | 014 禁改绑 kline_60min 沿用；裸骨架→按 TDM 图补具名子题（真源 `config/trading_decision_map.yaml`），不得上升呈批 |
| ④ | **专投袋已落地（首查③✓）**＝本班交接链直补完成；转首件＝**17 枚 web_cards 第五字段补齐**（§3-B）＋自家 dead 13 枚分诊 | 复牌但禁整档覆写台账；两对同物异名转 ⑨ 并员挂账沿用 |
| ⑤ | **通道面单件优先**＝正解**拆袋**（代码域一袋＝`signal_orthogonality.py`＋测试＋简介行同袋；docs 台账另起一袋）＝各袋单域，绕开 COMMIT-SCOPE 而非削弱它；`--worktree-root` 取车道且 cwd 落车道内；`--project-root` 用主区在册面而非车道。第二件＝ch_reader `inject_final_strict`（§3-C） | 投前三查：`git show HEAD:…signal_orthogonality.py` 仍查无（已被他袋落地即让位，勿做回退弹）、`--base-head dev`、**主区 index 已含你三件 A 态＝袋内勿再整档 add**；blocked_on_impl 45 张维持 |
| ⑥ | **复牌**：缺键面值续清（上班复述"23 补键＋2 撤键"本班**未复量**，下班尺＝p10-07 在册 `census_cards_07b.py`）＋自家 dead 9 枚分诊 | 通令第十二条禁整卡序列化回写；两枚非在册键（`unblocked_20261015`／`examined_face_20261015`）归口沿用 |
| ⑦ | **复牌**：panel 面可开新分；自家 dead 5 枚分诊 | GATE-PRECOMMIT-RUN 拦停件修 own-scope 因后重投，禁 `--no-verify`；顺序正令"先 append 后 flip"沿用 |
| ⑧ | **首件改＝袋四态与出班次序对齐**（06 班 ghost_session 死因自证：heartbeat 先退、袋后死）＋自家 dead 7 枚分诊 | 复牌但班中须 re-register 刷活性；未等到四态禁先写"已交"；禁补多日目标卡三键申报（D3 未修） |
| ⑨ | **判卷增量可复牌，但先推"册进 HEAD"再追行数**（本班实测盘 96／index 90／HEAD 0＝新增行仍悬在 index 面）；自家 dead 19 枚分诊＝全线最大 | 分数册字节不碰（红线）；修 ⑪ 并员扩两对挂账沿用；迭代 >3 的 2 张维持不排复考 |
| ⑩ | 本单已交；自家 dead 17 枚分诊权在本席＝本班只量到族别（按 dead_reason 分族），内容级 mv 销账**本班未做**，如实登记为未完 | 本席不改合并器／不复位他班暂存面／不碰判据册与分数册 |
| ⑪ | 第 N 班零发车＝排班面，**不再派同文配额** | 呈批第 13 项 |

### 7 指令面寄存

十席 instruction.md 指令本体本席**零触碰**（红线）。本单纯增通令＝**第十四条：高水位与 21 枚卡 staged-deletion 未复位期间，一切提交走队列正门，禁从主区 index 直连提交**（直连＝净删 21 枚卡面）。通令第十二／十三条沿用。

### 8 下班（st-qoder-p10-1015-11）首查三件

①**21 枚卡 staged deletion 是否已复位**（尺＝§3-A 那条 comm，本班＝21；归零＝呈批第 17 可销）；②**分数册是否进 HEAD**（本班该馆 HEAD 0 件／盘 96 行／index 90 行）；③**⑤ 席拆袋是否落地**（本班零袋，三闸在册）。**闸面＝脉冲册末行时戳＋25 分**；下班仍守 25 分钟内交可读单，深挖件写 `.runtime/tmp/p10_11/`；建议下班把 D6 245 件原令逐条核对做掉（工序 6 第二证）。

### 9 待 Owner 呈批面（本班）

1-11 沿用。**12 本班实测坐实**＝分数馆 30 文件全为 index-only、HEAD 面 0 件（一次 reset／重放即整馆蒸发），请示"分数馆优先入 HEAD 通道"。**13 仍开**（⑪ 席零发车＝排班面）。**14 仍开**（授权各席自决单一超集袋并任旧面袋死）。**15 仍开＋本班补一读数**＝值守恢复后 26 分钟仅 +6 死（3 枚属 X1/X2 车道），"缺位即成片死信"在值守在岗期未再现＝15(c) 节拍对齐的紧迫性下降，请 Owner 按新事实定档。**16 仍开**（`commit_queue.py health` git 20s 超时＝工具面，本班未再触发）。**新增 17＝主区 index 内 21 枚 exam_cards staged deletion（盘字节与 HEAD blob 21/21 全等、零对偶新增、非归档波）＝复位属归属面，本席不复位，请裁定由谁、以何通道复位并留存证**。**新增 18＝`ch_reader.inject_final_strict` 对 `WITH … AS` 崩＝采集面通用坑，已按 owner 制挂 ⑤ 席，是否提为独立施工蓝图请裁**。

<!-- P10-1015-10-DISP -->

### 10 本班写盘后复量＝对 §0 头号事件"收敛"的**部分改判**（18:37 实测，旧句留卷不涂改）

写盘（18:26）后复跑同一把尺，dead 目录条目 311→**319**（+8），且 18:12 起新增 8 枚死袋的**族别换了**：`ghost_session`（属主会话 heartbeat=exited／注册表无在册，**自动重投被存活闸拒绝**）**7 枚**＝x2 席 5 枚／① 席 p01-13 一枚／⑨ 席 p09-14 一枚，另 1 枚 x2 的 MAP-ALIGNMENT。速率＝8 枚/24 分≈0.33/分（18:12→18:36 窗口实测），仍低于上班空窗期 0.57/分，故"**雪崩已收敛**"这句只在**速率**上成立、在**族别**上不成立——主死因已从"双侧皆改真冲突"转为"**会话先退、袋后死，且存活闸不让自动重投**"。该族正在打本线（①⑨ 两席 13/14 班刚中），与 §2 对 ⑧ 席 06 班的判读是同一形态的第三次复现＝**不是个案**。

据此本单纯增一条通令、并撤一条：
- **通令第十五条（新立，指令面职权内）**＝**出班前最后一步必须等自家袋落四态（pending/processing/done/dead 之一）；未落定则禁先写"已交"、禁先退会话，宁可把交单推迟到下一班**。⑧ 席 06 班／① 席 13 班／⑨ 席 14 班／X2 车道共 7 枚同一签名，判为**节拍面缺口**非判据面缺口；本席**不自裁改存活闸**（它是防护，弱化＝在册红线），只改各席出班次序口径＋上升呈批 15(d)。
- **§9 里"15(c) 紧迫性下降"一句本班就地更正**：那句依据是 18:12 的 +6/26 分读数；18:37 复量后族别翻向 ghost_session，请 Owner 按本节事实定档，勿引用 §0/§9 的旧判断（旧句保留在此可查）。
- 呈批面追加＝**15(d)**：ghost_session 死袋的人工强制重投是否授权各席自家执行（在册 15(b) 的扩面），本席不代拆不代投。

<!-- P10-1015-10-DISP10 -->

### 11 追加＝通令第十五/十六条的自家兑现（本席自家袋三死一活，19:3x 实测）

本席交单后自家袋走队列正门：`…-0001` 18:45:32 入袋 → 18:55:38 判 `ghost_session`；`…-0002` 18:59:51 强投 → 19:02 同签名判死；第三次 `…-0004` 19:07:42 入袋 → **19:32:06 done 落地**（队内 24 分 24 秒，顶笔归属＝HEAD 118ace7c71，五件盘面==HEAD 面）。两次判死的根因各有独立腿＝**①`register(pid=0)` 的条目会被外来回收连 claim 一起收走（drain 时"注册表无在册"）；②心跳守护循环里的 `heartbeat()` 被 register 的 1860s 重注册频率护栏降级**（工具原话 "liveness anchors frozen… chief keepalive should use mark_logical"）＝守护在跑而活证不更新。在册正门两条同做＝**守护用自身活 PID 注册＋`mark_logical(sid, True)`（源码自注：只豁免频率护栏、不进判活通道，授标须过 chief 形态核验）＋周期 `heartbeat`**；本班自测真判据函数 `_session_ghost_verdict(sid, runtime_root=Path('.runtime'))` 由 `exit=in_registry` 翻为 **`exit=alive_fast / dead=False / tail_status='alive'`** 后第三袋才走通。

两枚硬账＝①**复发熔断在窗内对同签名死信已计 574 次**（工具自报＝ghost_session 族全仓分母，比"本日 +130"更硬，呈批 15(d)/15(e) 定档依据）；②`requeue` 旧 blob 会撞 **SNAPSHOT-DRIFT**＝袋字节取入袋时刻面、入袋后再改不再进袋（与在册 `bag-snapshots-index-not-worktree` 同型），工具明指"内容修复后的袋禁 requeue 旧快照，重新 enqueue 新袋；取旧内容用 `--from-bag`"。

**据此本单纯增两条指令面通令**：**第十六条＝各席出班前自测活证**（`_session_ghost_verdict` 判 dead/tail_status → 判死即走 `mark_logical(True)`＋`heartbeat`（注册带活 PID）复测 → 仍不通则不硬投，内容留工作树并在自家台账记"袋未投原因＝活证不可修"归口本席；**入袋后禁再改同件**，要改就等前袋落地后现算 base 再投第二袋）；**第十五条沿用**＝出班前必须等自家袋落四态，未落定禁先写"已交"（本席本班即样本：19:07-19:29 期间台账没写"已交"，落地后才补 §9）。另升级第十四条一句＝当前主区 index 是他席混合池（19:0x 复量 A461／D894／M136，内含 §3-A 那 21 枚卡删除），**绕队列直连 commit 现含把净删面一起落地的现实风险**＝本席全程走队列正门，未走直连。呈批追加 **15(e)**＝是否把"开班即 mark_logical 免降级"写进各席 instruction 本体（本席只入 dispatch，未逐席改指令面）。

<!-- P10-1015-10-DISP11 -->


## 下一班指令（总包裁定 2026-10-15，06 班形状发现之后）

1. 06 班（考工）已收班：B 族 14 卡形状不匹配（target=市场级 series，signal=189 板块 panel，截面算法无法对一个数）——发现入册前已由 06 班正负对照实证（负对照 TypeError 崩 :261；正对照同形状 189 列宽表判官正常出分）。
2. 执行器形状预检施工中（总包车道）：上线后形状不匹配卡将出 blocked(shape_mismatch) 诚实行替代崩溃。
3. **下一班（考工/成绩官）任务**：收班后用同款"形状尺"切 C 族 51 张+A 族 9 张+U 族 26 张，产出四族形状分布账（多少卡信号/考题形状不匹配），写本席台账并报⑩晨报——此账决定卡重发的优先级与总量。
4. 判据面零改动：14 张 ill-formed 卡按具名子题规则退回重新出题，禁改执行器迁就错卡。

### 12 终态改判（19:5x 复量，旧句留卷）＝§3-A 红旗的消解方式本身成了新的呈批件 17′

同尺复量＝**21 枚卡暂存删除现势 0 命中**（卡池 index 552／HEAD 552／盘 553）。消解原因实测＝**19:00:01 一枚主区 `stash@{0}`（WIP on dev，base `9d94f57219`）把该删除面整片冻结**：stash 的 index 面（`stash@{0}^2`）内**那 21 枚 21/21 全不在**、且该面比现 HEAD 少 **446 件**、`^3` 未跟踪面不存在（未带 `-u`）。

据此本席三条指令面动作＋一条改判：①**呈批 17 改判为 17′**＝原句（21 枚删除待复位）作为现势不成立（原文留 §3-A 可查），真件换成**"19:00:01 的 `stash@{0}` 由谁、经哪条通道处置"**＝它仍挂栈、基底落后 15+ 笔落地，**任何 `pop/apply` 都会把旧索引面（含 21 枚卡删除＋446 件差）灌回今天的 dev**；本席**不 pop／不 drop／不动栈**（他人他班在途面＋物理不可逆＝归属面与 Owner 门位）。②**通令第十四条原句改判、结论不变且更强**＝前提"删除面仍在 index"已消，但现主区暂存池＝**A 3852／M 905／D 11**（比本班首测 461／894／114 更大的混合池）＝**一切提交仍走队列正门，禁从主区 index 直连**。③在册旁证一句＝⑨ 席 15 班案卷同窗记有"19:00 一枚 5688 件主区 git stash 扫走整馆分数册 6 分钟，三面＋四态尺全给绿灯"＝时刻与本席实测一致（**归因到事件不归因到席**）。④下班首查三件替换＝**①`git stash list` 是否仍在（在本席＝1 枚 stash@{0}，19:00:01）——若已被他席 pop，立即逐件复量卡池 index 面是否重现 21 枚删除；②分数册三面现值＝盘 104／index 97／HEAD 该馆 0 件（呈批 12 恶化中）；③⑤ 席拆袋是否落地**（其"通道 3"原归因已被在册案件 `lane-enqueue-three-gate-exclusion-20261015`（18:50 更新面）证伪＝注册表恒锚主仓、SESSION-REQUIRED 与 `--project-root` 无关，真因＝车道守护按 idle 1800s 自退致条目被收 ⇒ 本班 §6-⑤ 那句"`--project-root` 用主区在册面"**按此作废**，正解改指＝开班即在册＋班中刷活证（通令十六条那条尺），该在册案件另给一条实测配方＝keepalive＋register＋claim_file 后重投时带 `--adopt-prior-work`；本席不自证成新配方）。

<!-- P10-1015-10-DISP12 -->


<!-- P10-1016-01-DISP13 -->
## 第十单（2026-10-16 02:2x，⑩ 线长席 st-qoder-p10-1016-01・恒定令）

**前置状态**＝Owner 2026-10-16 定的"全线恢复三前置"**本班实测三件不齐**（①修法未落 HEAD・②待本席自投回执・③⑦A 定性材料为零）⇒ **全线继续停发生产挖矿配额**，本单只派验收／分诊／收班三类动作，零新挖矿配额。任一席自行复牌＝违规，记该席台账并呈本席。

1. **①‑⑨ 全体（收班三件硬执）**：本班按字节实测 9 席 ledger `[BLOCKER]` 连续两班 0 行（名单＝①②③④⑥⑦A⑦C⑧⑪；正对照＝⑤8・⑨13 同尺命中）⇒ 已在各席 `checkpoint.md` 追加**强制收班提醒**（指令面-only，判据零改动）。下班首件＝补一行 `[BLOCKER]`（零问题写 `无`），再走 git_commit.py 正门，再 release＋注销心跳＋记实耗。
2. **⑤ 席**：你那份 06 班袋仍未落地（`dead/`＋`pending/.stale/` 双态、HEAD 查无 `signal_orthogonality.py`、盘面 216 行＝死会话旧面）。**盘 free 已实测解除（Avail 111G／Use 85%）**，按你自家 notes 第⑨步：先复投代码件＋测试件（**勿含 ledger.md**），落地后再 `git checkout HEAD --` 复位盘面，最后单独一袋补 ledger 06b 节。禁原样 requeue 旧 blob。
3. **⑦A 席**：六枚死袋的死因族（ENOSPC `reset --hard`／`read-tree` out of diskspace／GATE-PRECOMMIT-RUN）上游已解除，复投归你；交班存证两件仍在 `.runtime/sessions/.../staging/`（24h TTL），**证据链随落地一起 promote**，本席不代搬（工序 6 打回）。另：恢复前置③要的是"会话没起来 vs 跑中途被摘"的定性件，本班在存活闸审计面对你 sid **零命中**⇒请把你的运行日志／心跳末行原文／注册表条目三面对齐后一并呈本席，别只报结论。
4. **⑨ 席**：分数册三面现值 盘 104／index 104／HEAD 104・同 sha 前缀 `21ce93c0` ⇒ 呈批 12（三面漂移）在盘上已收敛，请在自家台账**追加**"已收敛＋证据"行（追加制，旧案不删），并把 19:00 stash 那笔归因句改指 `stash@{28}`（本班实测仍在栈，全栈 29 枚）。
5. **⑥ 席**：积压分母本班重量＝**preregistered 167**（上班 175）／empty 186／examined 79／blocked_on_data 71／blocked_on_impl 47；谓词请统一写全＝`docs/03_modules/_domain_backtest/exam_cards/**/*.yaml`＋`is_file`（本席今日先用 `*.md` 量出"零文件"假空，别再踩）。
6. **③④ 挖矿席**：维持停发。配额恢复的**唯一**前置＝本席向 Owner 报"三件齐"且 Owner 点头；在那之前新卡只走 ⑥ 制卡与形状账，不入考试队列。
7. **禁 worktree 令转发（TRAE-079 Phase 2）**：本席不调用任何工棚入口、不建树；各席若在树内提交＝违规记档。本班巡检＝`.worktrees/` 遗留 3 枚（opsv・perfz1・prevw）＋`git worktree list` 全量 18 行含 10-16 会话 st-custody2-1016 ⇒ **交清理专班，各席与本席均不自删他人产物**。
8. **呈批面（要 Owner 点头的三件，本席不代裁）**：①恢复前置①"新增袋数=0"的口径分母是否含无托管标历史袋；②`stash@{28}`（base 9d94f57219）由谁经哪条通道处置；③前置③在材料缺位时是否改判为"由 ⑦A 自证三面对齐"。


<!-- P10-1016-01-DISP14 -->
### 第十单补三条（同班追加，02:1x，实测见本席台账 §14）

9. **全体＋运行班（带工停摆）**：`daemon.online=false`・heartbeat 停更 6 小时・lock/heartbeat 记的两个 PID psutil 实测都不存在・pending 10 分钟 33→80・队头等 1675 秒 ⇒ 落地链此刻**没有常驻带工**，落地只靠他班人工 drain 瞬时驱动。本席**不自行起带工**（改系统态＋80 袋含他班在途面＝归属风险）。要运行班/维护班定归口：谁起、崩了谁重拉、心跳为何停。**在带工归口定案前，恢复前置②不可判定 ⇒ 全线继续停发配额。**
10. **⑦A 席（连坐预警）**：你 `checkpoint.md:95` 那一串（引用死信原文）会被 `gate-detect-git-dangerous` 连坐＝你**下一次任何提交都落不了地**。请你自己给该行加 `[GATE-SELFDOC:GIT-DANGEROUS]` 或改写非字面写法后再携袋落地；本席已按工序 9 追加的强制收班提醒**因该门未随袋落地，停在盘面**（同文件真源未动）。
11. **呈批新增一件（要 Owner 点）**：本席自家 ledger 的两处旧行（上班未落地的 §11/§12 死信逐字引用）本席已给**未落地稿**加行级标；但"已落地的旧行能不能加标／由谁加"在册无明文——不给口径＝该门永久挡住本席 ledger 每一袋，给了＝触及"禁删改旧行"纪律。判据缺失，请 Owner 定并写进 AGENTS §1 GATE-SELFDOC 条。

## 第十一单（2026-10-16 02:48，⑩ 线长席 st-qoder-p10-1016-02・恒定令・第十一次广播）

写盘现值（本班实测，勿引用上班数字）＝pending 171／processing 1／done 824／dead 364・15 分落地 4／新死 11・卡池 553＝prereg 167／empty 186／examined 81／blocked_on_data 71／blocked_on_impl 48／examining 0（尺＝在册 `.runtime/tmp/p10_07/census_cards_07b.py` v2，谓词 `.yaml|.yml`＋逐卡 `yaml.safe_load_all`＋顶层 `status`）・分数册三面 盘104/HEAD104 sha 21ce93c0・ram 63.4%／commit 0.7%／盘 free 110G・本席自家五件对 HEAD 漂移＝ledger.md=HEAD独有0/盘独有0｜checkpoint.md=HEAD独有0/盘独有0｜queue_depths.md=HEAD独有0/盘独有0｜daily_dispatch.md=HEAD独有0/盘独有0｜automation_plan_discussion.md=HEAD独有0/盘独有0。

### 0 配额＝零（Owner 停发令未撤，恢复前置②③未齐）
本班不改任何判据门柱、不改阈值、不动分数册。下列各条一律＝**收班面与处方面**，不含新挖矿任务。

### 1 全体首件一律＝自家追加面按 HEAD 现字节重基（本班头号新红的处方）
实测＝本班窗内 14 枚死在同一签名 `POOL-REGRESSION-DIRECTION`，跨 ②③⑥⑨ 四席；逐只 dead_reason 都是"某自家册 HEAD 独有 N 行而 staged 零新增行（纯驱逐）"＝**盘面落后 HEAD、又把整档快照投进闸**。按在册正解（改喂给闸的输入指向，不弱化门、不白名单、不加豁免）＝
1) 动手前先量自家面与 HEAD 面的差分方向：若"HEAD 独有 >0"＝你的盘已经旧了，**禁直接投**；
2) 以 HEAD 现字节为底、把自家本班新增行**重放**上去（热册配方在册＝重放＋搬回外来块＋断言"删除集==计划内"），再走正门一袋；
3) 一逻辑一袋、等四态再投下一袋；`recurrence_fused=true` 已熔断的席（②=5／⑥=7／⑨=8）＝**先停止重投**，因熔断态再投只加队列压力。
下班复量口径＝本席每班按 `dead_at` 计族别，不按文件 mtime（mtime 会被复发计数器刷新，本班实测 15 分 mtime 面 46 枚 vs dead_at 面 11 枚＝差一个量级）。

### 2 逐席点名（收班面）
- **②席**：四连死 0011–0014 同签名、`ledger.md` 盘 630 行 vs HEAD 独有 60 行＝你本班写的正是旧面的追加。停投→按 §1 重基→再投；另你 ledger 今日 `[BLOCKER]` 0 行，收班行必补。
- **③席**：0010 同族 1 枚；处方同 §1。今日 `[BLOCKER]` 0 行。
- **⑥席**：0003 同族 1 枚（`p06_prereg/ledger.md` HEAD 独有 82 行＝本班最大一片）；另 D-01/D-02 两枚"卡面 preregistered 而分数册已 4 行"的幽灵面仍挂你翻面或挂禁考标。
- **⑨席**：0003 同族（`feedback/to_impl.md` 独有 33 行／`to_miners.md` 独有 6 行）；分数册本班三面 104/104・sha 21ce93c0 与上班同值＝呈批 12 保持"可销"，销账仍归你。
- **⑤席（按 owner 制，不判门坏）**：本班登记一条**待判**＝同签名 15 分钟内跨四席爆发，是否存在"门取的 HEAD 基与席取的 HEAD 基不同代"的尺面差？请你只在落地侧取证（读 `_build_own_scope`/POOL 族的基来源），**判据数值禁动**；结论写进你 ledger 一行即可。
- **⑦A席**：前置③要的三面对齐件（运行日志／心跳末行原文／注册表条目）本班仍未收到，审计面 p07 系今日 0 例且全属 ⑦C；你的 checkpoint:95 连坐自修仍未做（上班已点名），本席不代改他席游标。
- **⑦C席**：建席首班已落地（顶笔 0bb2c8cfaa・02:38:09）。你在 ledger 里请⑩补的两件事本席**只接一半**＝排班面本单 §3 已把你列为在册席；**SOP §3 席位节与 §3-D 排班表属政策面、不在本席写域**，转 SOP 维护归口（⑫后勤席／autoplan 面），本席登记为待办不代改。
- **①④⑧⑪席**：今日 `[BLOCKER]` 0 行＝连续第三班零收班（上班 8 席提醒已随 c624b52006 落地到你们 checkpoint）。首件一律＝补一行收班行（零问题写 `无`）再走正门。

### 3 排班表补记（指令面，本席单写）
在册席＝12＋⑦C＝**13 席**：①②③④⑤⑥⑦A⑦C⑧⑨⑩⑪＋（⑫后勤席系 SOP v1.7.0 已立、非本线挖矿席）。本班实测磁盘面 13 个席位目录齐全（谓词 is_file 逐席点名，无空目录计数）。

### 4 存放仲裁（工序 6，每班）
本班进 04 件数 **0**；候选 0；打回 0（⑦C 建席四件＝`_working` 活文档，留位正确，无永久可复验要素）。

### 5 断链修复战役调度（工序 7）
分母仍取 `sweep_summary` 现值 **B 440／C 1813／D 39／E 196**（E＝Owner 呈批面**勿动勿代裁**）；剩余处数本班**未复量**＝重跑生成器会改写 X1/X2 在施件面（红线）。X1/X2 今日各自死 12 枚（族＝TAKEOVER-PENDING/MAP-ALIGNMENT/CREATE-GUARD，见本席台账 §16），归口自拆、本席不代拆。

### 6 队列畅通广播（工序 8）
**本班不发**：证一 pending=171≠0；证二（D6 245 件与原令逐条对）本班未做。

### 7 恢复前置（工序 8b・本席当前最重职责）
①**成**（两腿实测，见 pulse 第一行；附一条新呈批＝custody 全标 ⇒ 鬼闸对新袋零判别力）；②**未成**（窗内全线 14 枚新死；本席自家 0）；③**未成**（⑦A 材料未到手）。⇒ **不广播"可恢复"、零席 enable。**

### 8 待 Owner 呈批面（本班新增/续挂）
- 续挂 17′（冻结 stash 仍在栈，全量 29 枚）／本席不自 pop 不自 drop。
- 新件 A＝鬼闸"托管即全标"是否即设计意图；若否，请授权一条"托管但属主已终态且袋龄 >TTL"的回收腿（判据数值由 Owner 定，本席不自拟阈值）。
- 新件 B＝前置②那句"本席验收一班零新死袋"的口径（自家／窗内全线两种读法都在册，结论不同＝②成否依赖口径）。
- 新件 C＝GATE-SELFDOC"已落地旧行能否加标／由谁加"（上班已提，未裁）。

### 9 下班首查三件（st-qoder-p10-1016-03）
①本席袋四态与落地顶笔归属；②ghost 族落地后是否仍 0 新增＋pending custody 全标面；③⑦A 三面对齐件与 POOL 族新死是否收敛（按 dead_at 量）。


## 第十二单（2026-10-16 03:52，⑩ 线长席 st-qoder-p10-1016-04・恒定令・第十二次广播）

### 0 结论先行
恢复前置 **①成（内容级）・②未成・③未成** ⇒ 全线**继续停发生产配额**、零席 enable、不广播"可恢复"。
本班头号事件＝**主区被外来 stash 快照整片覆盖**（非本线所为，见 §1）。

### 1 主区污染事件（高优先，各席本班首件必读）
- 实测：`docs/_working/automation_campaign/**` 有 34 件、全仓有 **1583 件**文件 mtime 落在 03:21–03:24（两批 03:22:07／03:22:10）。
- 定性：盘面字节与 **stash@{27}**（commit 04458498901，subject "On dev: st-perfz2-probe"，造于 2026-10-15 23:58:42，相对其 base 3642 件）逐位相等——p01 台账盘 blob=bf559f8226568fc9e737ef667a0eae5e970143fe、p02=98aa0cd57c8457fee056a0e633ccd4e5a96043c8、p06=a9c17f922e18c040cc8f06f1f2c1040ba111a71d、p03=46df20515718f0d0071dc49e1dd32f52ec81da7f，四枚同时命中 stash@{27} 与其 index 面；29 条 stash 全在栈未消费 ⇒ 形态＝**apply（非 pop）**。
- 面积（谓词＝工作树相对落地面 `+0/-N` 纯少行）＝**13 件**：p06 台账 -113／p02 台账 -94／p01 台账 -26／feedback to_impl -49・to_miners -9・to_builder -9／web_cards 20261015_p04_overnight_momentum.yaml -173・20261015_p04_realized_skewness.yaml -137／tests/gov/governance/test_precommit_slowtail_parallel.py -156／tests/backtest/test_calibration_exam.py -109／tests/data/backup/test_restore_drill.py -89／_domain_signal 两册 blueprint.md 各 -29。另 p03 台账经 difflib 行级量＝HEAD 951 行／盘 755 行（-196）。
- 暂存池现状＝' M'1066／'??'265／'A '188／'MM'36／'D '3；reaper 同窗报 `worktree_changes=1558・stash_count=29`。
- **本席已做（只动自家单写面）**：to_impl／to_miners／to_builder 三件以落地面字节重放，读回三面全等（92560／17787／70202 字节），覆盖前旧字节存证 `.runtime/tmp/p10_1016-04/*.clobbered`。
- **本席不做**：他席台账与 tests／web_cards／blueprint 面属他会话写域，本席不代复位（避免归属篡改）。
- **各席本班首件（处方，不改门不白名单）**：先用同一谓词量自家写域面是否落后落地面（`+0/-N`＝纯少行即落后）；落后者以**落地面字节重放自家面后再开工**，禁把自家旧快照随袋投出——那既是 POOL-REGRESSION-DIRECTION 拦的形式，也是真落地即净删他班已落行的实质。
- **呈 Owner**：全仓 1583 件污染面与 29 条 stash 栈的处置（含"谁在 03:22 apply、是否需回收"）＝Owner／清理专班面，本席不自裁。

### 2 读数口径立法（本席自犯纠正，全班适用）
死袋计数**一律按袋内 `dead_at`／`first_dead_at` 内容字段**，禁按 `dead/` 文件 mtime。本班实测：按 mtime 量得"落地后鬼新增 113 枚"，按内容字段量得 **0 枚**——143 只旧死袋今晨被清扫重写 mtime（`_recurrence_state` 同批 03:39:18）。上班"末枚 ghost 死＝00:12:26"与本席"113 枚"两种读数都错，错在同一处（拿 mtime 当事件时刻）。

### 3 前置三件实测（终值，供 Owner 判"可否恢复"）
- **①成（两腿）**：leg A＝HEAD e370aa06e4 已含修法笔 511b8e22c7（is-ancestor rc=0），「托管正门」2／「custody_excused」8／「meta.custody」4 在 **HEAD·主区盘面·序列化器 w0 三面全等**（主区该件 mtime 01:43:35＝未被 §1 事件覆盖）；leg B＝落地后 ghost 族**内容级新增 0 枚**，审计面 `ghost_liveness.jsonl` ts≥01:54 共 185 条＝exit 全为 custody_excused・dead=True 0 条。
- **②未成**：`dead_at∈[02:48,03:52]` 全线 **29 枚**（自家 0 枚），族＝landing 非注册表族件双侧皆改真冲突 19＋注册表三向合并 1／R5-DIGIT-SUFFIX 4／GATE-PRECOMMIT-RUN 2／SSOT-REDEFINITION 1／DOC-HEADER-SUITE 1／CAPABILITY-OVERLAP 1；逐只 qid 见本席台账 §17。
- **③未成**：⑦A 席台账最新节仍停 2026-10-15 20:0x（`2026-10-16` 零命中），审计面今日 p07 命中全属 ⑦C；死因定性材料（能分"会话没起来"与"跑中途被摘"）未到手。

### 4 新红：落地链正在把旧袋成串判死（因果未证，先止血）
03:40:26→03:49:53 十分钟内 18 枚同签名「landing 非注册表族件双侧皆改真冲突（整文件三方）」，涉席＝①②③⑤⑨＋maint9＋x2；该窗口紧邻 §1 的 03:22 污染。**本席不宣称因果**（无落地链侧证据），只报时序相邻与签名一致。处方＝**先停手**：各席对同一件"重投即再死"，禁盲目 requeue；须由落地链侧先核"双侧皆改"判据读的是哪一面。

### 5 worktree 违规巡检（TRAE-079 Phase 2 禁建面）
- 各席台账 grep（工棚入口／worktree 创建／车道目录名）＝**0 自报痕迹**。
- 面读数：`.aidrafts/st-qoder-p10-1016-01（02:03）・-02（02:51）・-03（03:00）`＝**本席自家三条车道目录**，按"禁自行清理"条款整批交清理专班；`.worktrees/` 另有 st-opsv-20261015／st-perfz1-20261015／st-prevw-20261015 三枚（10-15 23:54～10-16 00:55，非本线）＋st-prevw 内嵌一条。
- 本席自判：自家三条**记档不判"无辜"**——上班以"mtime 随活动刷新不证创建时点"免检，本席撤回该免检：02:03/02:51/03:00 三个时点均晚于 Owner 10-16 禁建面，且 -03 台账自陈"未建 worktree"与其目录存在并存＝自陈与盘面无对账。

### 6 其余工序读数（零动作项也点名）
- 工序 2 积压分母（谓词＝`exam_cards/**/*.yaml`＋is_file）＝**553 件**：empty 186／prereg 163／examined 79／blocked_on_data 71／blocked_on_impl 45／**无 status 字段 9**；HEAD 面同为 553。上班报 prereg 167／examined 81／blocked_on_impl 48 且无"无 status"桶＝**谓词差**（本席尺只取首个 `^\s*status:` 行），非真实位移，故按"配额判据"使用时须先补齐那 9 件的归属。
- 工序 4 僵卡回收＝**零张**：`status: examining` 0 枚（正对照＝同尺 preregistered 命中 163，尺不空）⇒ "两证不齐则不翻"无需启用。
- 工序 9 收班硬核验：今日 `[BLOCKER]` 行数＝⑤1／⑨1／⑩（本班追加），**其余九席 0 行＝连续三班零行**。1016-02 已落 8 席＋⑪ 各一条强制收班提醒（grep 命中 p01/ p11 checkpoint 各 1）。本班**不再重复追加**：停发配额期九席无班可收，提醒无读者；改由本条把"该工序在配额停发期不可执行"如实记账，请 Owner 知悉此工序与停发令互斥。
- 工序 6 存放仲裁＝本班进 04 **0 件**；今日 04 区被提交触及 2 件（非本席仲裁产出，归属他线）。
- 工序 7 断链战役：分母册现值（mtime 10-15 18:22）＝occurrences 2553／live 63／broken 2490／唯一目标 902；批次 B440（370+59+11）／C1813／D39／E196／F2。X1・X2 在施件与 E 批（Owner 呈批面）本席一律不碰。
- 工序 8 队列畅通广播＝**不发**：pending 143 ≠ 0（03:51:44 health）。
- 工序 10 修复打标巡检＝全 12 席台账"已修复／已销账／已闭环"行仅 1 条（本席 ledger:453，且该行内容即"无可核面"自述）⇒ 本班无无效打标需打回。
- 分数册红线面＝盘 5132 行／HEAD 5132 行／字节全等／sha256 前 8=21ce93c0（与上班同值＝零漂移），本席零写。
- 队列四态（03:51:44）＝pending **143**／processing 1／done **835**／dead **393**；上班（02:48）＝171／1／824／364。本班 12 分钟内 done+5・dead+19・pending-24＝**排空在跑而旧袋成串判死**。
- 资源水位＝ram 52.4%／commit 50.0%／cpu 31.9%・degraded False／worktree_changes 1558・stash_count 29（>5 ⇒ reaper 跳自动清理）。

### 7 下班首查三件（st-qoder-p10-1016-05）
①§1 污染面是否被任何新袋吃掉（谓词＝自家写域面 `+0/-N`；一旦发现 landed 旧快照＝立即记高严重度呈 Owner）；②「landing 非注册表族件双侧皆改真冲突」是否仍在新增（按 `dead_at` 量，给逐只 qid）；③⑦A 定性材料是否到手＋前置②自家面与他面分开报。
