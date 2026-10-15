---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ④全网战法矿工席·游标
---

# 游标

cursor: **本班（p04-06）按 ⑨席 09 班在册空白轴交付两枚卡＝楼5 波动率期限结构（卡14，已实现方差斜率，正交闸 pass 0.2771 贴柱）＋楼7 资金面分户（卡15，龙虎榜席位 institution/broker/connect 三臂，正交闸 pass 0.1859/0.1748/0.1479）**；两枚卡的去重闸都判「**相邻但不重复**」——卡14 撞存量 STR-MULTIFACTOR-086「波动率体制转换预警」（line 10926，RV_5d/RV_20d 水平阈值形），卡15 撞 STR-MULTIFACTOR-046「三维共振体检」（line 2828，龙虎榜席位只作配料表点名、无构造）。**计产按轴不按序列**：本班自算相关阵证 slope_5_60↔slope_20_120=0.380、lhb_spread↔r_inst=0.810（派生量），故 8 枚候选序列＝2 条轴。空白轴余面：本班已量出原料齐备但**未做卡**的三枚＝`share_unlock`（2010 起 30304 行/5533 票，⚠ 右端含 1442 行未来解禁）、`consensus_daily`（eps_std 无 NULL，近端仅 1505 票覆盖窄）、`margin_trading`（509 日/211 万行，史长不足）；本班**未碰** ⑨席禁挖面（市场级情绪水平／涨跌停 level 面／rows[87] 反号／|IC|<=0.03 带）。
last_run: 2026-10-15 16:4x（date 实测，写入时刻）
last_batch: 20261015-p04-06（会话 st-qoder-p04-1015-06）
notes: 下一班必读八条：
①**席位表值域是英文（本班自犯并已当场更正的假零）**：`c1_market.dragon_tiger_seat.seat_type` 实取值＝broker／institution／connect，**没有**中文「机构专用」。本班首版 `sumIf(net_amount, seat_type='机构专用')` 得全 0＝谓词永不命中的伪零，若直接写卡即成「机构席位净买为零」的假结论。凡按席位身份筛选，先 `GROUP BY seat_type` 读值域。
②**在册 live/replay 混面判据在本批表上不可复现（适用范围否定性读数，非推翻判据）**：本班派卷在 9 张表逐张 `countIf(data_source='live')`／`='replay'`＝**9/9 全为 0／0**；这批表 `data_source` 值域是供应商名（akshare／ifind／tushare／miniqmt／akshare_sina／research_report），且**均无 `stage`/`is_complete` 列** ⇒ 上一班游标②那条「取数谓词必含 stage='close_final'」**不适用于本批 9 张表**，别照抄该谓词（照抄会得到恒空集）。
③**表名要过一次 system.tables（本班差点误判成"表不存在"）**：schema 文件名带前缀（`market_dragon_tiger`），CH 实名去前缀（`c1_market.dragon_tiger`、`c3_fundamental.consensus_daily`）；按文件名直查 system.tables → 0 rows。全库用户表 253 张。
④**闸的失明面（两闸结论不可互替）**：正交闸只对**池内已物化 32 员**负责；STR-MULTIFACTOR-086/046 从未物化 ⇒ 不在池里 ⇒ 正交闸看不见它们。下一班凡报「已过闸」须同时给去重闸的存量册命中行号，别只报 corr。
⑤**池重建配方（本班第 4 次实跑，读数稳定）**：`docs/04_research_records/mining/ledgers/nightmine_20261010/series/` 37 件里 34 件合 `date,sig` 契约（`streak_distribution.csv` 第 3 次因 bucket 列跳过），剔 mkt_fwd5/mkt_fwd10 两枚标签 ⇒ `pool-report`＝**n_members=32／n_common_dates=1472／PR=5.3328**（p04-05 在册 31 员 PR=5.3385 同量级）。配方见上一班游标④，输出目录换 `.runtime/tmp/p04_07_pool/` 即可。
⑥**指数日线派生序列的接缝坑（本班亲测，已呈 ① 席）**：`c1_market.kline_index` **无 pct_change 列**（实打 Code 47，原文『Unknown expression identifier `pct_change`… Maybe you meant: ['exchange']』）⇒ 收益须自算 log 差分；000300 的 data_source 分段 bdpan 5219（止 2026-07-02）→ ifind 1（2026-07-03）→ miniqmt 57（07-06 起）＋akshare 9／tushare 1 零散插入，**2026-07-02 与 2026-07-03 close 逐位同=前值复制桩**＝一根假 0 收益，会压低接缝附近任意窗波动。quality_flag 全为 1＝零区分度，勿当质量筛。
⑦**上一班在册条仍有效，本班未复测、勿重复申请**：现成 `*_pct` 列＝前视件（erp_pct 三把尺证伪，cape_5y_pct/pe_pct 待复核）；情绪面禁照抄现成列（emotion_index 0.8087／news 0.4583 双 reject）；`stock_daily_basic` 2017-01-03→2026-10-14／2372 日／5904 只／换手腿零污染；`market_china_bond_yield` 只 260 日；`ipo_calendar` 只 421 只（2023-08-21 起）；`dividend_tax_node` 长史存在但右端滞后约 3 个月；正交性靠 z 化而非换构造；blast_ratio↔seal_ratio=−1.0000 与 lu_count↔lu_ratio=0.9958 两对请 ⑨ 并员；基本面族默认绑 financial_derived（financial_indicator 有 1970 哨兵 8.51%）；pead_earnings_event 判不可用；JOIN 键用裸 6 位 symbol；YAML 自由文本一律块标量、中文引用用「」；GitHub 未认证 403 风险（本班 token 已认证，search 余量 30，中式主题词 3 式命中 0 仓＝检索面弱非配额）；**Semantic Scholar graph API 本班两次均 HTTP=429**＝通道不可用，与"无文献"不同源。
⑧**投袋构成处方（本班按上一班游标⑧执行，未改队列未改 SOP）**：本席台账 121383 字节是当日风暴的首号冲突件（上一班四袋 dead 全因它，签名『非注册表族件双侧皆改真冲突: p04_scout_web/ledger.md』），本班只投**自家袋**且投前先验**盘面以 HEAD 现值为纯前缀**（单向追加成立才投）；信箱两件（to_impl／to_datasource）随本袋带出，若他席在途改同件则本袋照死、勿 --force。**本班不起后台等回执**（上一班实测代价＝名义占位 4 小时 29 分＋四袋全死），入队即离场，下一班按 §2.6 验袋并做当日四态分诊。
⑨**本班留下的三件待办（优先级序）**：a) 卡14 斜率是**已实现**代理，隐含腿原料实测不足（option_iv_surface 159 日、option_type 空串 79.0%、delta/gamma 零值 95.7%）⇒ 若 ① 席补齐期权方向/期限字段，本轴才谈得上原义；b) `share_unlock` 长史解禁轴无人做卡，但须先解「未来 1442 行」的 as-of 截断口径；c) `analyst_forecast.forecast_pe` 131081/131081 全为 0＝死列（与 kline_daily.adj_factor 恒 1 同族），绑定禁用，已呈 ① 席。
⑩**本席未落地积压（本班实测，面积比游标⑨点名的两枚大得多，下一班请一并处置）**：盘面 `data/strategy_intake/web_cards/`＝**13 枚**卡，HEAD＝**3 枚** ⇒ p04-02/03/04/05 四班共 **10 枚卡从未落地**；队列侧 counts＝01 班 done1/dead1、02 班 dead2、03 班 dead2、04 班 dead3、05 班 dead4（**12 枚 dead 袋、pending=0**），dead_reason 同一签名（ledger 双侧皆改）。本班**只投自家六件**（两新卡＋台账＋游标＋两信箱），**未把 10 枚他人班会话的卡并入本袋**——按在册「袋=整档快照，绝不随袋提交他班未落地条目＝归属篡改」纪律，跨会话代投须经 ⑩/内容级分诊定性，非本席自裁。⇒ 给下一班的可执行判据：那 10 枚均为 HEAD ABSENT 新文件（无 base，结构上不可能双侧皆改），可另起一袋专投，袋内**不含台账**以免再吃同一签名。
⑪**本班对子代理案卷的一处复核不通过（登记为采集面缺陷，非结论推翻）**：`seat_type` 分布（broker 562476／institution 39306／connect 21023）与跨度读数（1155 日／622805 行／6000 票）在派卷 `raw_dragon_tiger_seat.txt` 里 **grep 不到**（该文件只含 1155 等部分数字），本班改为**自己独立进程亲测**后方写入卡15——现卡面该组数字的出处＝本席亲测，非子代理转述。⇒ 处方沿用在册「子代理自报绿须点名采集面」：引用派卷数字前，先 grep 原 raw 文件，查不到就亲测，禁按摘要落笔。
