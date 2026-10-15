---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ①数据源席·游标
---

# 游标

cursor: 本班第 14 班处理 4 项（含 13 班 next_up 两项＋两项④席新单），出建设单 B-27/B-28，缺口册一个字节未动。①项零＝**缺口册承接由“下一班落地”改判“本班不动”**：扫队列发现他席在途袋 q-20261015-st-qoder-x2-1015-0010（created 18:34:55）携带该册，其 blob 与本席工作树该册逐字节相等（222,904B／条目 85／含 13 班 option_iv 那条）⇒本席补丁已在别人袋里排队；此时再写＝工作树与在途 blob 分叉，踩在册“双侧皆改/回退弹”死法⇒本班只把四枚证据键原文写台账交下一班。归因实测：git diff --numstat HEAD -- 该册 两次读数均 41加/25减（13 班开班为 3/3，在途清扫仍在扩面），其中 50/66 行是路径改写。②项一＝④席 p04-01 第1条 tick 近端断崖改判＝源活在/采集退化（决定性一条：同终端同窗 kline_1min 六日全满采 1.34M 行、uniq 恒 5,562–5,569）；10-13 整日零行、10-14 本班复量 14,582（④席 8,027，该日仍在写入）、10-15=9,207,409/7,937＝在产但仅正常深度的 37.6%（**不判自愈**，收盘后 3.8h 复量仍此量）；回补通道四测＝xtquant 连接成功且 10-08 单票 4,859 行可取（服务端可读窗未证：本席未跑 download_history_data）／akshare 仅剩当日分笔接口（4,721 行、无日期参数）＝历史结构性不可回／tushare 腿本席尺无效当场作废／baostock frequency='t' 官方拒绝 10004012＝无 tick 腿确证；**时限=date 实测**：今日周四、下个周日 2026-10-18，tick_backfill_weekly 的 7 天窗=[10-11,10-18]⇒10-08/10-09 三日后滑出自动窗；**判据缺陷**＝threshold=5,000,000 按行数判缺⇒10-08/10-09 均>5M 被判不缺而宇宙少 34.2% 零告警⇒出 B-27（含“10-18 02:00 前手工试下载”硬时限）。③项二＝④席 p04-02 第1条估值深史：先定真源方向＝daily_valuation 的 data_source 全表只有 local_valuation 254,151＋repair_kline_join 1,280＝**现表零外源腿、自算派生**⇒要 2017 起点只能换外接源；baostock 匿名免费三窗真跑（2017=36 行／2019=35 行／2026-10-08..**10-15**=6 行右端已达当日）含 peTTM/pbMRQ/psTTM/pcfNcfTTM/**isST** ⇒**④席 is_st 该问结案：有逐日真值列，禁再由名称反推**；tushare daily_basic 真跑 20190104=3,556 行(0.32s)／20170103=2,832 行(0.23s)＋官方载该 API 最低 2000 积分⇒**反证本仓 token 已达 2000 档**（零现金）；akshare 个股估值腿未通（stock_a_indicator_lg 在 1.18.75 不存在、baidu 腿 TypeError），不外推“akshare 无估值腿”；**在册断供风险**＝tasks.yaml:1069/:1077 原文“baostock 有 IP 黑名单史”（#ARCH-DATA-015）⇒可得≠可续供，禁单腿常设＋须复用本仓 baostock_provider.py 禁新建 provider⇒出 B-28。④项三＝13 班 next_up② MSCI：用其台账在册的检索命中官方 URL 亲测，index-review 页**公开可达**（列 China A 等 9 个分区入口），PublicList PDF 返回内容但本席工具未解析出表行⇒可达性由“未证”改判“已证可达”、可解析性仍未证、五门“续供=是否自动化”仍未过⇒**维持不放行**（结论不变、理由升级）。⑤项四＝13 班 next_up⑤ B-26 规模半实测闭合（单次 0.23–0.32s 亲测＋官方表 2000 档=每分钟 200 次⇒1,696 票下限≈9 分钟，不含新浪腿与并发上限）；next_up③（B-25 右端 20261016）＝未来日、本班不可测，原样下移。⑥自纠＝本班 probe3 用 hasattr(pro,'tick'…) 判 tushare 分笔腿，Pro 对象 __getattr__ 动态转发⇒hasattr 恒真零判别力，该通道判未证、不当放行依据（下轮要判须真调并落报错原文）。纪律：零新建卡、零翻态、零改判据与门柱、零写库、零花钱；缺口册/分数册零字节；本席对 13 班 staged 字节纯超集追加（minus=0）。保底双口径如实呈报：本班处理 4 项＋出 2 张建设单（≥3 项达标），但 B-27 的服务端可读窗与 B-28 的全市场对拍两项关键证据**本席未闭合**，已在件内显式标注为②起跑前置。
last_run: 2026-10-15 18:57（date 实测，见 ledger 本班耗时段）
last_batch: st-qoder-p01-1015-14
next_up: ①**缺口册四键一次性落地（本班刻意未写盘面，勿凭本行重写正文）**：先三态核实 x2 袋是否已落（`git log -1 --name-only -- src/zephyr/data/config/known_data_gaps.yaml`／`git status --porcelain`／`python -c "import yaml;print(len(yaml.safe_load(...)['gaps']))"` HEAD 面 84 vs 盘面 85）；落地后以 HEAD 现值为基**纯追加**四键＝13 班 `p01_probe_20261015o`（宿主 kline_etf_daily_shallow_depth）＋`p01_probe_20261015p`（宿主 msci_adjustment_empty_table_no_leg，含 searched_channels 四行）＋本班 `p01_probe_20261015q`（宿主 tick_data_2026_0917_gap :1538）＋`p01_probe_20261015r`（宿主 daily_valuation_price_legs_zero_mislabeled :1132 区，与“深史不可达”面二选一并写明理由），原文均在 ledger 13/14 两节末代码块内；写后断言 `git diff --numstat HEAD -- 该册` 的 minus=0。②**B-27 时限盯人**：2026-10-18 02:00（周日 weekend_backfill）之前须见②席对 10-08/10-09 的试下载申报；过期则该两日宇宙缺口转永久，须按工序 5 落断供登记（searched_channels=本席四测）。下一班首件＝复量 10-15/10-16 tick_data 每票笔数量级（本席读数 1,160 笔/票 vs 正常 3,088）判是否写满，禁把“在产”读成“已愈”。③B-25 官方腿右端复量＝跑 ak.option_risk_indicator_sse(20261016) 验 T-1 口径（本班不可测，日期在未来）；且 13 班在册“未逐年二分左界、未证 2015-02-09 前无”仍有效。④B-26 规模已半实测闭合（见游标本班项四），剩未测面＝tushare 并发上限与当日剩余额度（本席未查）、新浪腿 volume 单位=手 与本库对拍归②。⑤北向 Q3 断面复量按 12 班处方在 2026-10-20 前后跑 hk_hold(trade_date=20260930) exchange 分层，未到点勿抢跑。⑥MSCI 那条若要判得放行，须补“PublicList PDF 可解析性”证据（本席工具面判未证），并守 announcement_date 与 effective_date 两列分离的 PIT 要求。⑦11 班在册四项待他席回文（B-20 语义门执法／880 原生面 tq.download_file／OD-c 采购呈批／index_weight 左界二分／SW2014 体系成分）＋09 班交办两笔（news_sentiment_window completed 分层复核、B-1..B-16 续供确认栏是否回补）仍候 Owner/⑩；⑧**tushare 分笔腿＝在册“尺无效未证”**，下一班要判须真调一次并落报错原文。
notes: 游标由本岗每批推进；监督员(⑩)可代修。

cursor_qid: q-20261015-st-qoder-p01-1015-14-0001（按入袋号规则预写，落袋后回读队列核实；若与本行不符则下一班以队列现值为准更正）

## 本班自纠留痕（另起留旧案卷，不改写史实）

- 06 班那条「shareholder_count 引擎探针空返回＝观测面失明、如实报堵」**本班撤回并改判**：真因是本席把表名限定成 c1_market.shareholder_count，真表在 c3_fundamental.shareholder_count；严格读抛 GATE-P0-ENGINE-PROBE 属 fail-closed 正确行为，探针无需修（②席反证＋本席同名严格通道复现 FINAL 515,280／quality_flag 单组恒 1／announce<end 3,904 逐值复现④席）。教训入册：引擎探测空返回与「表不存在」同形，跨库查表须先从 system.tables 取真库名再下「读不到」结论。
- 04 班 B-10 那句「schtasks 实测 ZephyrAlpha_BdpanTickWatch state=Ready」**本班证伪并更正**（438 行任务表内 bdpan/tickwatch 各 0 命中，正对照 ProcessReaper 2 命中；坑因＝Git Bash 未关参数路径转换时 /query 被吞、乱码看似跑过）。
- 本班开班后一度据 0 字节／No such file 判定「本席工作面被外部复位」，据第二次哈希实测（四面与 06 袋 4/4 逐字节相等、p01-p10 目录 mtime 齐为 09:29）**撤回该定性**：撞到的是跨十席批量换面的中途，非洗盘、无需恢复。并发换面期读数须哈希级复量≥2 次才定性。

- 本班更正①席历史案卷（另起留旧案，不改写 03 班原文）：03 班在 consensus_daily 值类段写的「tushare pro.report_rc＝未实测、本席不烧额度不自购」与采购呈批草稿 OD-b 的前提「唯一可突破值类断供的非爬虫通道、需 8000 积分」，本班真跑四窗（134／5,000／5,000／2,134 行）判为**既有 token 即可调用**⇒ 该段由「断」改判「可免费回补」，OD-b 降级为可选加速项；本席未实测的积分档与当日剩余额度已显式标注为推算。
  同班更正：本班首把容量尺用 shutil.disk_usage 读得 F: total=385GB（真值 1,863GB，CIM 实测），free 值两尺一致故结论未翻，但已在建设单与 YAML 证据块写明「盘容量类读数一律取 CIM 或 system.disks」。
- 本班更正 08 班游标 next_up⑥（另起留旧案，不改写 08 原文）：08 写「to_datasource 无新单时可自挖 kline_sector_880 族深史（两班未做）」——本班实测 to_datasource.md 已有 ④席 p04-05 八条新单（该件 mtime **10:24:49**，晚于 08 班游标写入 10:22:38，故 08 落笔时确未见单、非其误判），本班按 SOP 工序 1（先读缺数申请）优先清新单，880 族遂为**三班未做**（07/08/09）。下一班若见"无新单"再启 880，勿据 08 原句判本班漏项。
- 本班自纠二（另起留旧案）：**本班把脑估时戳写成了「date/系统钟实测」**——游标 last_run 原文 11:14 与台账「≈35 分钟」两处均无同命令 date 输出支撑，实测跨度是 10:38:14 → 13:5x（≈3 小时 2X 分）。已在两处就地更正并留原句。同型形态本席已多轮记档（体感钟快约一倍＋交付命令须正文原样跑），本次是同班 ⑧席也独立撞上同一坑（commit 1b3facb831），判据补齐一句：**「实测」二字只能跟在同行跑过的命令读数后面**。

<!-- P10-1016-01-FORCE-CLOSEOUT -->
> **⑩线长席强制收班提醒（2026-10-16 01:5x 实测追加，指令面-only，未改任何判据）**
> 本席 `ledger.md` 里 `[BLOCKER]` 行数实测 **0**（同尺负对照＝⑤席 8 行／⑨席 13 行命中；本席 ledger 正文 160499 字节内连 `BLOCKER` 子串都零命中⇒不是谓词伪空，是真未收班）；10-16 00:53 班同读数＝**连续两班 0 行** ⇒ 依 SOP §3⑩ 工序 9 追记本提醒。
> 下班收班三件（缺一＝本班不算收班）＝①ledger.md 追加至少一行 `[BLOCKER] <YYYY-MM-DD>|<席+班号>|<工具缺陷|判据缺失|数据问题|流程问题|需Owner>|<一句话>|<file:line 或路径>|<要谁做什么>|<高|中|低>`（零问题必写 `[BLOCKER] <date>|<席+班号>|无`）；②提交只走 `python scripts/commit_queue.py` 上游的 `git_commit.py --session <sid> --files <自家清单> --enqueue`（禁裸 git commit／禁从主区 index 直连）；③release 自家 claim＋注销心跳＋台账记实耗分钟。
