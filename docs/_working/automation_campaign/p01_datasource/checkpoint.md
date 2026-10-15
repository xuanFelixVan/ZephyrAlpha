---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ①数据源席·游标
---

# 游标

cursor: 本班第 09 批处理 8 项（④席 p04-05 全批，10:2x 新到、02..08 七班未覆盖）——出两单 B-17 中债深史（akshare bond_zh_us_rate 东财真跑 5,808 行 2005-01-03..2026-10-14，零采购；交集仅 5Y/10Y/30Y 三点，2Y 须扩列，信用债两曲线无源，口径分轨禁混算）＋ B-18 指数估值二期三列（既有 token 直取 pro.index_dailybasic 两片 3,000＋1,072×2=4,072 行恰盖本表 4,071 交易日、pb 非空 100%；乐咕破净三档 5,275/5,219/4,797 行右端皆 2026-10-14；乐咕巴菲特指数 5,224 行属全市场口径与按指数行的语义错配，落位三择一归②席/Owner）；不达通道实测两条（乐咕指数级 stock_index_pb_lg 仅 238 行≈月频⇒日频不可用；中证官网 indicator.xls curl http_code=404）；news_sentiment_window 判**非源断供**（分层实测 market/night 止 2026-10-14 腿在跑、market/1d 止 2025-09-09、symbol/night 止 2026-08-20 滞后 55 日⇒在册 completed 只对 market/night 粒度成立，转②，本席不翻 status）；stock_valuation 判**重复开单**（04 班 B-9 在案，880 之外不复挖）；daily_valuation turnover 恒 0 判死列第二处＋同真源可派生（唯一真源 stock_daily_basic.turnover_rate）；erp_pct 只补调度面 grep 零命中不代裁；sentiment_panel 跨市场登记一句；CH TCP 冷却坑改本班操作规程（单进程≤4 聚合＋SELECT 1 正对照）。YAML 新增 1 条（bond_yield 深史 open）＋2 条证据块，status 零翻转、断供零新增。⚑两项本班自纠：①本班 cleanup 收走 08 班在飞袋 claim（在册锁对偶第二次同案，本班为加害方，已同串重注册＋重 claim，判据呈⑩）；②grep 实测 B-1..B-16 **全体缺「续供确认」栏**（0 命中），本班起补栏，旧十六单是否回补候 Owner/⑩。
last_run: 10-15 14:05（date 实测；原文写 11:14 并称 date 实测系本班脑估，已另起更正）
last_batch: st-qoder-p01-1015-09
next_up: ①⚑**起手先做袋态三态分诊，勿默认前班已落地**——本班 13:5x 实测 02..08 八袋**全 dead**（七袋同因 to_builder.md 双侧皆改真冲突，05 袋 ghost_session），dev 现值被 **ff8a0a68d5（12:58，十席指令面重脚手架）** 洗回模板（builder 面 `grep -c '^### B-'`=0），而盘面经 Counter 三面对拍证实是 dev 现值严格超集（gaps 0／builder 0／ledger 0／checkpoint 仅 3 行占位符覆写）⇒ 02..08 内容一行未丢、由 09 新袋带走；下一班须先确认 09 袋真落地（done/或 HEAD 面 `git show HEAD:...to_builder.md | grep -c '^### B-'` 应 ≥18）再按 mv 通道销那八袋，**未落地禁先销**；②下一班起手仍按全根袋态判定（find .runtime/commit_queue 各态 q-*p01-1015-*），并留意 pending 目录里 files=0 的空壳影子件不可当活袋；③等②席回函 B-11..B-18（B-17 中债三点期限回补＋B-18 指数估值三列；B-18 的 buffett_ratio 落位三择一须②席或 Owner 表态，本席不代裁；B-17 的 2Y 扩列与调度常设属②施工面）；④news_sentiment_window 的 completed 定性请②席按粒度分层复核并在册留证，本席只补证据未改 status；⑤B-16 配额账仍系推算（放量前实测本仓 report_rc 积分档与当日剩余额度）；⑥楼3 准入叙述修正（daily_valuation 47 日只卡个股截面腿，市场级 4,071 日可达）请②席并入资产册，本席不改散文；⑦「续供确认」是否回补 B-1..B-16 十六单＝Owner/⑩裁，本席不自决批量补栏；⑧恒定班 cleanup 收同席在飞袋 claim＋重脚手架把在飞袋集体打死＝两条请⑩定性（本席未自改 lock_files.py 与队列代码）；⑨若下批无新单可自挖 kline_sector_880 族深史（07/08/09 三班未做）；⑩队列拥堵与死信处置属⑩面，成果落地前他班勿判本席未交付
notes: 游标由本岗每批推进；监督员(⑩)可代修。

cursor_qid: q-20261015-st-qoder-p01-1015-09-0001（按入袋号规则预写，落袋后回读队列核实；若与本行不符则下一班以队列现值为准更正）

## 本班自纠留痕（另起留旧案卷，不改写史实）

- 06 班那条「shareholder_count 引擎探针空返回＝观测面失明、如实报堵」**本班撤回并改判**：真因是本席把表名限定成 c1_market.shareholder_count，真表在 c3_fundamental.shareholder_count；严格读抛 GATE-P0-ENGINE-PROBE 属 fail-closed 正确行为，探针无需修（②席反证＋本席同名严格通道复现 FINAL 515,280／quality_flag 单组恒 1／announce<end 3,904 逐值复现④席）。教训入册：引擎探测空返回与「表不存在」同形，跨库查表须先从 system.tables 取真库名再下「读不到」结论。
- 04 班 B-10 那句「schtasks 实测 ZephyrAlpha_BdpanTickWatch state=Ready」**本班证伪并更正**（438 行任务表内 bdpan/tickwatch 各 0 命中，正对照 ProcessReaper 2 命中；坑因＝Git Bash 未关参数路径转换时 /query 被吞、乱码看似跑过）。
- 本班开班后一度据 0 字节／No such file 判定「本席工作面被外部复位」，据第二次哈希实测（四面与 06 袋 4/4 逐字节相等、p01-p10 目录 mtime 齐为 09:29）**撤回该定性**：撞到的是跨十席批量换面的中途，非洗盘、无需恢复。并发换面期读数须哈希级复量≥2 次才定性。

- 本班更正①席历史案卷（另起留旧案，不改写 03 班原文）：03 班在 consensus_daily 值类段写的「tushare pro.report_rc＝未实测、本席不烧额度不自购」与采购呈批草稿 OD-b 的前提「唯一可突破值类断供的非爬虫通道、需 8000 积分」，本班真跑四窗（134／5,000／5,000／2,134 行）判为**既有 token 即可调用**⇒ 该段由「断」改判「可免费回补」，OD-b 降级为可选加速项；本席未实测的积分档与当日剩余额度已显式标注为推算。
  同班更正：本班首把容量尺用 shutil.disk_usage 读得 F: total=385GB（真值 1,863GB，CIM 实测），free 值两尺一致故结论未翻，但已在建设单与 YAML 证据块写明「盘容量类读数一律取 CIM 或 system.disks」。
- 本班更正 08 班游标 next_up⑥（另起留旧案，不改写 08 原文）：08 写「to_datasource 无新单时可自挖 kline_sector_880 族深史（两班未做）」——本班实测 to_datasource.md 已有 ④席 p04-05 八条新单（该件 mtime **10:24:49**，晚于 08 班游标写入 10:22:38，故 08 落笔时确未见单、非其误判），本班按 SOP 工序 1（先读缺数申请）优先清新单，880 族遂为**三班未做**（07/08/09）。下一班若见"无新单"再启 880，勿据 08 原句判本班漏项。
- 本班自纠二（另起留旧案）：**本班把脑估时戳写成了「date/系统钟实测」**——游标 last_run 原文 11:14 与台账「≈35 分钟」两处均无同命令 date 输出支撑，实测跨度是 10:38:14 → 13:5x（≈3 小时 2X 分）。已在两处就地更正并留原句。同型形态本席已多轮记档（体感钟快约一倍＋交付命令须正文原样跑），本次是同班 ⑧席也独立撞上同一坑（commit 1b3facb831），判据补齐一句：**「实测」二字只能跟在同行跑过的命令读数后面**。
