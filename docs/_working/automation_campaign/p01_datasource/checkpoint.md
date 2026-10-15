---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ①数据源席·游标
---

# 游标

cursor: 本班第 12 批处理 3 项（大宗／北向／解禁）＋1 项对表销单＋1 处自纠。①项零＝④席 p04-02..06 六班缺数单逐单对表：daily_valuation+is_st→B-12、turnover 死列→B-17/B-18 条5、analyst_forecast→B-16、stock_valuation→B-9、index_valuation_daily→B-18、bond_yield 短腿→B-17，**全部已在册，本班零重复开单**，工作面改攻三条零建设单的悬置项。②项一＝**④席"大宗两表 amount 差 3–4 数量级＝不同源"改判＝同物异单位（恰 10^4）＋异粒度**：本库 block_trade=元/股（与 akshare stock_dzjy_mrmx 逐位同）、block_trade_detail=万元/万股（与 tushare block_trade 逐位同），000656 detail 单行=源侧 6 笔之和逐值可复；全表自洽 block_trade 1706/1706、detail 1683/1878（195 行=10.4% 转②定标）；深史四断面 2010=23/2015=65/2019=209/2024=120 行 且 akshare 2010 窗=109/2019 窗=562 行，本库两表按年只有 2026⇒④"大宗折价不可考"改判为**免费可回补至 2010-01-04、楼8 门槛⑤可达**⇒出 B-23＋新建 gaps 条目 block_trade_depth_and_unit_split。③项二＝**北向"右端落后 3.5 个月"＝源侧尚未发布、非欠采**：hk_hold exchange 分层实测 20260930={HK 1014/SH+SZ 0}、单票 600519.SH 在 20260601..20261015 只 1 行（20260630），本库 8 断面全为季末；官方锚=上证发〔2024〕106号（2024-08-19 起北向单票持有量改季度第五交易日公布上季末数）。**本班新雷判据（11 班在册未定性那 792/1,018 行）**＝政策后同一 trade_date 混两方向两频率，取北向必须 exchange IN (SH,SZ)，否则把南向当北向；日频北向唯一可行窗实测 2017-03-16..2024-08-16（akshare stock_hsgt_individual_em 600519=1,683 行、正对照 000001=1,723 行同右端）⇒ 该段标注=一次性历史档案，禁常设准入⇒出 B-24＋并条进在册 hk_connect_flow_hkex_disclosure_retirement（键 p01_probe_20261015l，零新建条目）。④项三＝答④"解禁前瞻是可持续采集还是一次性导入"＝**可持续**：akshare 三腿未来窗 20261015..20270115 实测 summary=66/detail=460/queue(600000)=4 行，本库 1,442 行未来解禁属正常前瞻面；PIT 雷=queue_em 自带"解禁后20日涨跌幅"后视列，入库须剔列、消费须按解禁时间≤as-of 截断。⑤自纠＝本席按 ④ 给的裸表名限定 c1_market.share_unlock 严格读两次报 ENGINE-PROBE 空返回，正对照 block_trade 有值⇒判"库名限定错"而非"读不到"，跨库定位 system.tables name=share_unlock ⇒ **c3_fundamental.share_unlock**（本席第三次撞同型坑，06 班 shareholder_count 已留过一次更正）；另登记 `system.tables WHERE name LIKE ...` 返 [] 而等值命中⇒LIKE 在本通道不可信，本席未据其下结论。净零＝gaps **83→84 净增 1 条**（block_trade 面全文 grep 0 命中＝从未入册，非重复开单；轨 B 退役属 Owner 门，本席不自裁⇒如实报净增请⑩/Owner 复核）；建设单 B-22→B-24（`### B-` 22→24）。
last_run: 2026-10-15 17:40（date 实测，见 ledger 本班耗时段）
last_batch: st-qoder-p01-1015-12
next_up: ①**B-23 施工前置**＝请②先定标 block_trade_detail 那 195 行（amount≠price×volume）是聚合行取何均价，再回补深史；本席只测到 2010-01-04 单日可得（23 行），**未逐年二分左界、未测 tushare 单次限量外的更早年份**，禁据本行外推"2010 前也无"。②**北向 Q3 断面须复量**＝本席实测 2026-09-30 北向在源侧尚未发布（该日 SH/SZ=0）；官方称"每季度第 5 个交易日公布"，下一班应在 2026-10-20 前后复跑 `hk_hold(trade_date=20260930)` 的 exchange 分层，一旦 SH/SZ 出现即转②补采本库第 9 个断面。③**日频北向历史段（2017-03-16..2024-08-16）是否回补=Owner/②门位**，本席只给通道与右端证据，未估逐票调用次数与耗时（akshare 是逐票接口）。④解禁三腿的**在册调度归属本席未查全量**（只按本批真跑陈述），且 share_unlock 真身在 c3_fundamental，请②⑩凡写 c1_market.share_unlock 的在册件都要复核库名。⑤11 班在册四项待他席回文仍未回收（B-20 语义门执法／880 原生面 tq.download_file／OD-c 采购呈批／index_weight 左界二分／SW2014 体系成分）＋本席 09 班交办两笔（news_sentiment_window completed 分层复核、B-1..B-16 续供确认栏是否回补）仍候 Owner/⑩；⑩rows[88]/[87] 两笔一日差仍候⑤/②认。
notes: 游标由本岗每批推进；监督员(⑩)可代修。

cursor_qid: q-20261015-st-qoder-p01-1015-11-0001（按入袋号规则预写，落袋后回读队列核实；若与本行不符则下一班以队列现值为准更正）

## 本班自纠留痕（另起留旧案卷，不改写史实）

- 06 班那条「shareholder_count 引擎探针空返回＝观测面失明、如实报堵」**本班撤回并改判**：真因是本席把表名限定成 c1_market.shareholder_count，真表在 c3_fundamental.shareholder_count；严格读抛 GATE-P0-ENGINE-PROBE 属 fail-closed 正确行为，探针无需修（②席反证＋本席同名严格通道复现 FINAL 515,280／quality_flag 单组恒 1／announce<end 3,904 逐值复现④席）。教训入册：引擎探测空返回与「表不存在」同形，跨库查表须先从 system.tables 取真库名再下「读不到」结论。
- 04 班 B-10 那句「schtasks 实测 ZephyrAlpha_BdpanTickWatch state=Ready」**本班证伪并更正**（438 行任务表内 bdpan/tickwatch 各 0 命中，正对照 ProcessReaper 2 命中；坑因＝Git Bash 未关参数路径转换时 /query 被吞、乱码看似跑过）。
- 本班开班后一度据 0 字节／No such file 判定「本席工作面被外部复位」，据第二次哈希实测（四面与 06 袋 4/4 逐字节相等、p01-p10 目录 mtime 齐为 09:29）**撤回该定性**：撞到的是跨十席批量换面的中途，非洗盘、无需恢复。并发换面期读数须哈希级复量≥2 次才定性。

- 本班更正①席历史案卷（另起留旧案，不改写 03 班原文）：03 班在 consensus_daily 值类段写的「tushare pro.report_rc＝未实测、本席不烧额度不自购」与采购呈批草稿 OD-b 的前提「唯一可突破值类断供的非爬虫通道、需 8000 积分」，本班真跑四窗（134／5,000／5,000／2,134 行）判为**既有 token 即可调用**⇒ 该段由「断」改判「可免费回补」，OD-b 降级为可选加速项；本席未实测的积分档与当日剩余额度已显式标注为推算。
  同班更正：本班首把容量尺用 shutil.disk_usage 读得 F: total=385GB（真值 1,863GB，CIM 实测），free 值两尺一致故结论未翻，但已在建设单与 YAML 证据块写明「盘容量类读数一律取 CIM 或 system.disks」。
- 本班更正 08 班游标 next_up⑥（另起留旧案，不改写 08 原文）：08 写「to_datasource 无新单时可自挖 kline_sector_880 族深史（两班未做）」——本班实测 to_datasource.md 已有 ④席 p04-05 八条新单（该件 mtime **10:24:49**，晚于 08 班游标写入 10:22:38，故 08 落笔时确未见单、非其误判），本班按 SOP 工序 1（先读缺数申请）优先清新单，880 族遂为**三班未做**（07/08/09）。下一班若见"无新单"再启 880，勿据 08 原句判本班漏项。
- 本班自纠二（另起留旧案）：**本班把脑估时戳写成了「date/系统钟实测」**——游标 last_run 原文 11:14 与台账「≈35 分钟」两处均无同命令 date 输出支撑，实测跨度是 10:38:14 → 13:5x（≈3 小时 2X 分）。已在两处就地更正并留原句。同型形态本席已多轮记档（体感钟快约一倍＋交付命令须正文原样跑），本次是同班 ⑧席也独立撞上同一坑（commit 1b3facb831），判据补齐一句：**「实测」二字只能跟在同行跑过的命令读数后面**。
