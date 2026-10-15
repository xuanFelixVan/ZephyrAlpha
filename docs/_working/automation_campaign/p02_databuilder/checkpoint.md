---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ②数据建设席·游标
---

# 游标

cursor: 已收口（本班无在途 DB 写；回补件已落地并通过三查，非"跑一半交班"）
last_run: 2026-10-15 10:4x
last_batch: st-qoder-p02-1015-04
notes: 游标由本岗每批推进；监督员(⑩)可代修。旧案全文在 `ledger.md`（09:12／09:47／10:3x 三段），本游标只承载"下一班要执行什么"。

  **本班（1015-04）四件交付**：①**结案 1015-03 唯一硬件**——consensus_daily 10-08/10-09 未推进的真因＝
  `consensus_daily_compute.py:81 _INCREMENTAL_OVERLAP_DAYS=3`＋`:300 infer_incremental_start()`（表内最新快照日−3
  自然日），09:47 那轮起点被推到 **10-12**，日志实测 `p02_consensus_1015_03.log:18` `交易日 4 天（2026-10-12~2026-10-15）`
  ⇒ 这两天**没进产出行集**；上一班留给本班的候选假说"新研报无 EPS⇒不产行"本班正面跑全月分布**证伪**
  （10-01..10-11 带 eps_fy0 的研报 31 条，其中 10-08 四条、10-09 十三条）。②**回补落地**＝
  `python scripts/ch/build_consensus_daily.py --start 2026-10-08 --end 2026-10-09`，两跑各 8,960 行，FINAL
  10-08/10-09 各 4,480 行／1,495 只、`max(last_report_date)` 09-30→**10-08／10-09**，全表 6,856,172→**6,856,196**
  （净增 24＝两日增量逐位闭合），PIT 违例 0，六项聚合与落笔前干推演**逐值相同**，幂等复跑不变，
  三查②`system.query_log` 两笔 QueryFinish written_rows 各 8,960 与 CLI 日志逐秒相符。③**tick 近端断崖定性**
  （①席点名归本席，只读）：逐日 FINAL 20,203,768(10-08)→6,708,423(10-09)→357,130(10-12，qmt_bridge 盘中 11:29:56 停)
  →**0**(10-13)→14,582(10-14，只有 15 时收盘档 14,498 行，且 ingest 落在本地 10-15 04:38→08:41＝重启后补录)
  →5,769,354(10-15 至今，实时腿在岗)；塌陷起点在 **10-09** 而非 10-13。④**B-15 容量裁决**（本班不施工）：
  CH default 盘余 **170.59 GiB**，单价尺 kline_1min 25.084 B/行／etf 16.332／60min 32.797／tick 18.10⇒
  分钟线三张合计≈**59.5 GiB（占余 34.9%，可派，须按年/月分块）**，tick 119.29 亿行≈**201 GiB ＞余量（全量装不下）**。

  **下一班待办序（本班修订）**：
  ①**B-15 分钟线族挂回**（本班已给裁决，可直接进施工）：源清单＝`F:/zephyr_cold/50_archive/by_project/zephyralpha/archive_manifest.jsonl`
  2,533 行逐条 verified&dropped，本班未复核该清单本身（下班挂回前须自数 `is_file()` 谓词，勿拿 `rglob('*')` 空目录计数）；
  接缝本班已核在线 `kline_1min` min=2021-09-01/max=2026-10-15、14.95 亿行✓。硬约束三条：
  **(a)** 分区上限＝1015-01 在册死因 `Too many partitions for single INSERT block (>100)`，冷段跨 255 个月分区⇒**按年/按月分块，逐批行数对账**，
  禁以"文件数对上"充数；**(b)** ①席验收判据四条原样吃（接缝无重叠／行数守恒／裸 6 位 symbol 不加后缀／`ingest_ts`+`recorded_time` 保留原值禁 `now()` 覆盖）；
  **(c)** **tick 腿（201 GiB）不在本班授权面内**——扩容=花钱、清 backups 腾挪=物理删，两条都是 Owner/⑩门位，且 119 亿行大批写要等
  内存态（本班进场 reaper 报 `commit_pct=96.21 degraded=True ALERT-SYS-003`、`ram_used_pct=80`、D 盘 97% 余 23G）缓解后再议。
  ②**consensus 重叠窗这条约束请转⑤/⑩席定性**（本席不改码）：`_INCREMENTAL_OVERLAP_DAYS=3` 使"原料迟到超过 3 个自然日"
  的快照日**永久不再被夜档覆盖**——本班已手工回补 10-08/10-09 两天，但只要明细腿再出现跨≥4 日的迟到簇，同样形态必复发。
  ③`known_data_gaps.yaml` 翻转补丁仍压班：本班 10:0x 实测工作区面 **253 insertions / 0 deletions 未落地**（①席 hunks，
  上一班量到的是 209，说明该册仍在被他班续写）；净态落地后再翻
  `research_report_hot_value_rating_change_empty`／`consensus_daily_value_cols_pit_broken`／`tick_data_2026_jul_aug_qmt_range_gap`。
  ④B-11/B-12/B-13/B-14 施工动作全在采集器写侧（tushare 新腿/换主源＋新调度任务），本席按 1015-02/03/04 同型判例不越界，
  **请⑩席派⑤实现席**；B-12 的 10-14 末日塌陷（盘面 1,553 行 vs 源 5,563 行）1015-03 已只读复证并自带"故意不跑现役腿"的承重证据，勿重做。
  ⑤B-1/B-2/B-9 三张仍等 Owner"建腿 vs 退役"一字裁（呈批面 1015-02 已合并一份，每班只重读门位、不重复催）。
  ⑥tick 断崖的**进程侧取证本班没做**（只到 CH 面）：10-09 起逐日塌陷要采集器/订阅进程在岗链路与 10-13 全缺原因，
  归⑤/⑩；④席"10-14＝8,027 行"与本班 FINAL 14,582 属**口径差**（拆 market_type 后 8,027 与任一分项及组合都不等），
  下班若要合账先问④席取数谓词，别按"谁错"起手。

  ⚑**派生脚本到期日**：`.runtime/tmp/p02_backfill_rating_change_1015.py`（6,023 字节，mtime 10-15 07:04，24h TTL
  ⇒ **明日 10-16 07:04 过期**）；若 10 月还有新研报到库需再复跑 rating_change，过期后按 1015-01 段口径重造。
  本班新建三件临时件（均 `[TTL] task_bound`，落 `.runtime/tmp/`，TTL 24h）：`p02_probe_1015_04.py`／
  `p02_cd_pre_1015_04.tsv.gz`（回补前快照，sha256[:16]=cc11925fff5b5add，**唯一回退基底**）／`p02_dry_cd_1015_04.log`。

  ⚑会话与锁（本班第四次复现在册坑，**下班起手照做**）：主区投袋先 `SessionRegistry().register(sid, pid=0, held_files=[...])`
  **并且立刻** `PYTHONPATH=<仓根>` 起 `_spawn_heartbeat_daemon(sid, Path('D:/ZephyrAlpha'), 30)`——本班 10:09 只注册没起守护，
  10:19 前三个 claim 已被他班 `lock_files.py cleanup` 收走（`lock_files.py status` 里查无自家件＝已被收，不是没拿到）。
  判"某班注册没有"读分片面 `.runtime/session_registry/<sid>.json`，聚合面是过期投影。投袋前先复 acquire（TTL 30 分钟）。
  ⚠`git_commit.py --enqueue` 外层**禁套 `timeout`**（1015-03 登记坑，本班未犯）。
  本班 CH 侧坑三枚（都是"读数断半路/假 500"）：`python -c` 内联多行读数须改文件＋重定向落盘；日期谓词必须带引号
  （裸 `2026-10-01` 被当算术⇒HTTP 500）；`system.parts` 查询禁拿 `rows` 当别名（与列名撞⇒HTTP 500）。

  ⚑本班袋态与终验（本班投一袋，files=3：ledger.md／checkpoint.md／unblocked.md）：
  刻意排除面＝`known_data_gaps.yaml`（①席 253 insertions 未落地）、`to_builder.md`／`to_datasource.md`／`to_impl.md`／
  `to_miners.md`（他班 A/AM 新件，随袋＝归属篡改）。本班 DB 面无在途写，**下一班读 `last_batch` 非在途即可开工**。
  落地面终验只认本班独有标记：
  `git show HEAD:docs/_working/automation_campaign/p02_databuilder/ledger.md | grep -c "P02-1015-04-ENDSTATE"`
  ＝0 就是没落地（09:12／09:47 段文本会假绿）；对策＝按在册三步重投，重投前用同一把 Counter 尺对**当下 HEAD** 复量。

  ⚑**交班态（本班如实写明，别当"已清场"）**：袋在飞 ⇒ 按在册铁律**不放锁、不停守护**——
  `ENQUEUE-RENEW` 已把三件 claim 续租到 `ttl=7200s`（约 12:5x 才自然过期），心跳守护进程实测 `daemon_pid=34992` 仍在 beat。
  ⇒ **下一班（约 11:0x 起）会撞本席这三件锁**：正解不是抢锁也不是放锁（抢占式 re-acquire 会摘掉在飞袋的执法依据），
  而是照在册"锁对偶"第 3 条走——先 `lock_files.py status` 判明持有者＝`st-qoder-p02-1015-04` 且袋在飞，
  再把本班件写进 `.runtime/sessions/<自己sid>/staging/` 的整册副本，`difflib` 自证纯新增后走 `git_commit.py --allow-overlap`。
  若 12:5x 后本席袋仍未落地，则视为死信，按 §2 第 6 条当日四态分诊处理，不隔夜。

---

## 游标覆盖式更新 · st-qoder-p02-1015-05（10-15 12:3x）——**下一班只读本节即够**

`cursor: 已收口`（本班零 DB 写，无在途批）｜`last_batch: st-qoder-p02-1015-05`｜本班耗时 **约 130 分钟**（超 60 分窗口，如实记）。

**本班交付＝三件裁决定性 + 一处新发缺陷，不是数据落地**（保底"每班≥1 项建设或回补落地"**本班未达**，承重证据在 ledger 件②末段＋件③末段＋件④自检段）。全文＝`ledger.md` 段「2026-10-15 11:5x · st-qoder-p02-1015-05」，终态标记 `P02-1015-05-ENDSTATE`。

1. **B-16 已改判：禁写入 `c3_fundamental.analyst_forecast`，须新建逐报告表。** 键级证据＝该表 `sorting_key=symbol, report_date`（不含预测期/机构），而 `pro.report_rc` 真实粒度四维（同票同日同机构有 2024Q4/2025Q4 两行）。两处在役消费者（`consensus_daily_repaired_compute.py:92/:356/:444`、`consensus_crosscheck.py:70-72`）谓词里**都没有 data_source 过滤**⇒ 逐报告行落进 2026-07-22 之后的日期就把"聚合值"口径换掉。**续供第四查已过**（`report_rc(20261001,20261009)`＝723 行／max 报告日 20261009）；深史端 2010-01 实测 4,752 行成立。**切片判据须升级**：①席"≤10 交易日"会被恰 5,000 行静默截断（本班 20240801-20240815 实测恰 5,000），正解＝**"恰 5,000 即二分重取"自适应＋逐片行数对账**。**本班未排产**：配额"当日剩余额度"这一维本机无可测口，须先做一次"连续 10 次调用是否触发限频"实测才能定 35 天 vs 数小时。报批面：SOP §3"免费+四格≥3→直接推进"⇒ 不占 Owner 门，但候选册 `docs/_working/altdata_line/10_data_source_candidates.yaml` 已被 10-14 归档波移走（本班实测目录不存在、该件 staged-D），登记前先定新址。
2. **B-15 已择路①（分段挂回分钟线族）。路②实测判死**：`system.disks`＝`default /var/lib/clickhouse/`、`backups /mnt/chbackup_local/`、`backups2 /mnt/chbackup2/`，**无一块指向 F:**，`file()` 三形态路径全 500；要走路②须 VM 加挂载＋放开 `user_files_path` 两道，非本席权限。**路③属 Owner 门（扩容＝花钱／清 backups＝物理删）**，本班不催不代裁。
3. **冷库清单自数已交**（上一班列的 `is_file()` 活）：2,533→**2,536** 条（本班值守内被上游 +3，mtime 12:31，尾条＝`kline_etf_30min` 2011 段），`verified&dropped` 全真、`parquet_path` 逐条 `is_file()` **零缺失**，parquet 合计 **159.29 GiB**；新算出**无人计过的 17.93 GiB**（technical_indicator_60min 11.04＋120min 6.89）——若①席意图含这两张，容量账要重算。**parquet 字节 ≠ 入库占盘**：kline_1min parquet 26.38 GiB，按在线 25.084 B/行折算仍≈57 GiB（1015-04 量级成立，勿"改正成错的"）。
4. **⚑挂回排期第四道前置（本班新立，下班必读）**：**归档器此刻仍在并发追加清单**⇒ 起手先复量 `archive_manifest.jsonl` mtime，**近 10 分钟内仍在被追加就停车不起批**；叠加上原有三道＝①`process_reaper --status` 的 `commit_pct` **<70 才起批**（本班进场实测 **92.07／degraded=True／ALERT-SYS-003**，与 1015-04 的 96.21 同档未缓解）②队列 pending 实测 **138**、head 袋等待 **9.5h**（本班进场态，非本班造成）③分块铁律照旧＝按年/月分块逐批行数对账（在册死因 `Too many partitions for single INSERT block (>100)`，冷段跨 255 个月分区）。
5. **⚑新发缺陷呈批（修法属⑤/⑩，本席不擅自重建表）**：`analyst_forecast` 正被自己的排序键**静默吃掉约 3/4**——写侧 `akshare_provider.py:4416` docstring 自陈"每只股票返回4年预测展开为4行"，盘面三把尺同向：`GROUP BY forecast_year` **只剩 2028 一档**（131,081 行／2,817 只）、`GROUP BY symbol,report_date` 的 131,081 个键**全部恰 1 行**、裸表 `count()`＝`FINAL`＝131,081。后果＝`consensus_daily_repaired`（1,563,996 行）**segment B（2026-07-22 起）整段 EPS 取自"2028 预期"**而非当年/次年；①席在册 consensus_daily 三档（2026/2027/2028＝2,558,858／2,391,837／1,905,477 行）证明多年才是应有口径。
6. **回补面本班实测无目标**（不是没找）：`consensus_daily` 10-08..10-15 六日全在（4480/4480/4471/4474/4462/4453 行，`max(last_report_date)` 逐日对齐，10-15 的右端＝10-14 属明细腿采集滞后而非聚合缺口），PIT 违例 **0**⇒ 1015-04 的修复在岗且夜档没再漏。
7. **照旧不动的册**：`known_data_gaps.yaml` 本班实测工作区面 **299 insertions／0 deletions 未落地**（1015-04 量到 253，本班量到 299 ⇒ ①席仍在续写），净态落地前**不翻任何 status**；B-11..B-14／tick 断崖进程侧取证／④席读数合账＝归⑤/⑩（本席不越界，判据沿用 1015-02/03/04 同型判例）；B-1/B-2/B-9 仍等 Owner 一字裁。

⚑**降级直改主区投袋的原因登记（RULE-WORKTREE 显式申请制留痕）**：本班袋从主区直投（`--allow-non-worktree`），原因＝本班全部取证为**只读**（CH 系统表＋tushare 单次调用＋F 盘清单统计），零代码改动、零 DB 写，产物只有本席两件活文档；车道内跑不出这些读数（CH 访问口与 F 盘挂载都在宿主侧），且队列现 138 pending／head 等 9.5h，另开车道只增加一层连坐面。同型判例＝1015-01..04 四班同路。

⚑**12:5x 对本游标第 1 条的更正（旧文留上不抹，B-16 排产定性改硬）**：复跑交付命令 (3) 拿到服务端原文 **`频率超限(10次/天)`（doc_id=108）**⇒ 本仓 report_rc **真实档＝10 次/天，且今日 10 次已被①席 4＋本班 5＋来源未取证 1 用尽**。所以游标第 1 条里"配额无可测口／可能远快于 35 天"两句作废：**B-16 在现档下是 ≥35 个自然日的常设轮转腿，不是一次性回补**，且"恰 5,000 即二分"只会增加调用数。**明日之前禁再投 `pro.report_rc`**（要投先 `date` 跨日）。排产二选一＝①10 次/天跨班长轮（游标须记"已消化到哪个 report_date"防重防漏）②升 8000 积分正式档＝花钱，**Owner 门**；①席 03 班"唯一可突破值类断供的非爬虫通道需付费"这一立法前提被本班实测推翻（免费可用，只是慢），改判请①/⑩席另起留旧案。
⚑**本班坑（下班照抄避坑）**：①`sop §3` 候选册路径已失效，照抄必撞 `No such file`；②`archive_manifest.jsonl` **带 UTF-8 BOM**，`encoding='utf-8'` 读首行即 `JSONDecodeError: Unexpected UTF-8 BOM`，必须 `utf-8-sig`；③猜键名会**空跑不报错**（清单真键＝`parquet_path`，本班首跑拿 `('path','file_path','abs_path','host_path')` 猜⇒整段零输出，看着像"查无"）；④`os.path.isfile` 之类谓词若在字符串里含 `'kline'` 这类子串匹配，会误抓 `table` 键⇒得到一次**假 FAIL**，本班已作废重投；⑤`pro.report_rc` 有频控，连跑要留 ≥60s 间隔；⑥heredoc 写 Python 会把 `'\\'` 折成 `'\'`⇒语法崩，改 `chr(92)`（在册坑第二次复现）。
⚑**临时件（均 `.runtime/tmp/`，`[TTL] task_bound` 24h，明日 12:3x 前自清或复跑重造）**：`p02_probe_1015_05.py`／`p02_probe_1015_05.log`／`p02_b15_1015_05.py`／`p02_b15b_1015_05.py`＋`.log`／`p02_cd_gap_1015_05.py`／`p02_af_key_1015_05.py`；另 `/tmp/p02_probe1..3.py`（Git Bash 侧，仓外，无需台账销账）。
⚑**本班袋面（刻意排除）**：files＝**2**（`ledger.md`／`checkpoint.md`）；**排除** `known_data_gaps.yaml`（①席 299 insertions 未落地）、`to_builder.md`／`to_datasource.md`（④席/①席 staged-A 新件，随袋＝归属篡改）；本班**未写** `unblocked.md`（本班没有销任何缺口，只新立一条缺陷）。ledger 与 checkpoint 两件都按 **difflib 纯新增**写法（append/末段追加）⇒ 对 1015-04 两袋的 blob 是单调超集，不抢锁不放锁（在册"锁对偶"正解）；前班袋 `q-20261015-st-qoder-p02-1015-04-0001/0002` 仍 pending，**本班未 requeue、未动**。

---

## 游标覆盖式更新 · st-qoder-p02-1015-06（10-15 16:5x）——**下一班只读本节即够**

`cursor: 已收口`（本班 DB 写已提交并逐位验收，无在途批）｜`last_batch: st-qoder-p02-1015-06`｜耗时 **约 63 分钟**（超 60 硬窗，超因＝写库前多跑一轮全精度接缝＋负对照）。全文＝`ledger.md` 段「2026-10-15 16:5x · st-qoder-p02-1015-06」，终态标记 `P02-1015-06-ENDSTATE`。

1. **B-17 已落地＝保底达成**：`c1_market.market_china_bond_yield` 新增 **15,552 行**（5Y/10Y/30Y × 5,184 个估值日），左端 **2025-09-23 → 2005-01-04**；`data_source='akshare_eastmoney_bond_zh_us_rate'`，按年切 **21 块**提交（每块 ≤12 分区，规避在册 `Too many partitions >100` 死因），全块 `disposition=ch_committed detail=http`。全表 FINAL 21,792＝现轨 6,240＋新轨 15,552（逐位守恒），两轨键重叠 **0**，`ytm IS NULL` **0**，与落笔前基底 `p02_b17_rows_1015_06.tsv.gz`（sha16 `3d72a2706332596f`）键集合双向差 0、值失配 0。回滚谓词写前实测 0 行 ⇒ `ALTER TABLE ... DELETE WHERE data_source='akshare_eastmoney_bond_zh_us_rate'` 恰等本班插入集（**未执行**）。
2. **⚑①席一条前提被本班实测改判（下一班别再接"两口径不同物"）**：东财 `bond_zh_us_rate` 的中国国债 5Y/10Y/30Y 与库内 chinamoney 中债估值在 **780 对重叠日上 mean|Δ|=max|Δ|=0.00000000pp、>1e-6 计数 0**；同尺错位配对负对照（src10Y vs db5Y）＝mean 0.2610pp、260/260 全非零 ⇒ 尺能分辨，零是真零。该页属**中债估值转挂、同一条序列**，所以本班沿用同一 `curve_name`（另立曲线名会把一条真实序列无据撕裂）；①席"禁混算"要防的口径断裂在本通道不存在，"按 data_source 打标分轨"的字面已满足。**两处口径不同物≠所有通道都不同物，下班逐通道测勿套用。**
3. **⚑①席"中债腿零调度命中"不成立**（它是按中文标签 grep 的）：按表名/能力名复量即命中 `tasks.yaml:2174 china_bond_yield_refresh`（`source=akshare`／`schedule=daily_capital`／`incremental=false`）＋`schedule.yaml:85 daily_capital` 槽；更硬的证据＝直读 `ingest_ts`：现轨末次 **2026-10-14 10:00:39 UTC＝本地 18:00 槽位时刻**，自 2026-09-18 起 9 个 ingest 日 ⇒ 任务真跑。**处方给下班：判"某腿有没有在产"，读 `max(ingest_ts)` 与 `data_source` 分组比 grep 中文标签硬得多**（B-19 的 miniqmt-vs-bdpan 形态同一把尺）。
4. **B-17 三查＝两闭一开，故本班未翻 status、未写 unblocked.md**：①表有数右端新鲜✓／②调度真跑✓／**③消费者查得数＝不可执行**（`.py` 面查询侧零命中，正对照 6 命中全在写侧与注册表；楼3 ERP 属未来接线）。第四条理由＝本班东财腿**无常设调度**（源一次取尽全史），按 SOP"只有历史一次性数据的不准当常设源"，本表续供主体仍是 chinamoney 腿；且深度只补 3×8 里的 1×3（`3M/6M/1Y/3Y/7Y` 五点＋商行债/中票两曲线仍封 2025-09-23），①席"禁宣称整曲线补齐"照抄有效。
5. **`known_data_gaps.yaml` 本班实测 15 insertions／0 deletions 未落地**（1015-04 量 253、1015-05 量 299 ⇒ ①席大批已落地、仍小批在飞）⇒ 本班整档不碰，翻 status 交净态后班次；`to_builder.md` 新增 **B-17/B-18/B-19 三张均带「续供确认」栏**⇒ 本班不拒收（1015-05 记的"B-1..B-16 全体缺栏"只适用于旧十六张）。
6. **下一手＝B-18 pb_mrq**（①席实测最干净：tushare 4,072 行整窗可平替、现表 `countIf(pb_mrq IS NOT NULL)=0`）。开工前两把闸：(a) 该表是 **akshare 原始列＋internal_compute 计算列双写者**，2026-09-13 全史重采曾把计算列抹 NULL ⇒ 回填若走"重插整行"必须先量清重采语义；(b) **buffett_ratio 落位三择一是设计分叉**，按在册口径先与 Owner 讨论再动，不属回补。tushare 单次 3,000 行上限＝"恰 3,000 即截断二分"（B-16 恰 5,000 同款）。
7. **B-15 三闸复量结果**：`commit_pct=94.03`（本班进场，1015-05 是 92.07，**未缓解反而更差**，`degraded=True`＋`ALERT-SYS-001/003`＋`cpu 97.7`）⇒ 不起批；归档器并发闸**已解除**（清单 mtime 12:31:06，本班 15:5x 复量 3h25m 无追加）；队列 pending 138→**2** 已疏通；分块闸＝本班 B-17 已实操验证"按年≤12 分区"够用，可直接复用。tick 腿 201 GiB 仍超盘余＝Owner 门，勿代裁。
8. **B-16 明日跨日后方可再投 `pro.report_rc`**（10 次/天额度 1015-05 已用尽，本班未投）。

⚑**本班自犯并转成正证据一枚**：首版回补脚本拿 `oc.elapsed_sec` 打印，而 `WriteOutcome` 实测只有 `disposition/detail` ⇒ **AttributeError 崩在 INSERT 之后**，2005 年块已提交；本班不回滚掩盖，改判为幂等自然实验（该块 raw 1,506 → FINAL 753＝重复插不增 FINAL），并把它升格为验收第 (2) 号复核项。处方：**用 `ch_writer.write_tsv_outcome` 时打印字段只认 `disposition/detail`，且写后必做 raw-vs-FINAL 双读**。
⚑**会话与锁（照抄 1015-04 处方即生效）**：起手 `SessionRegistry().register(sid, pid=0, held_files=[两件])` ＋**立刻** `_spawn_heartbeat_daemon(sid, Path('D:/ZephyrAlpha'), 30)`（本班 daemon_pid=52964），再 `lock_files.py acquire` 两件；本班全程未被外来 cleanup 收走。`git_commit.py --enqueue` 外层禁套 `timeout`。CH 侧：TCP 面走 `DatabaseService().get_clickhouse_conn()`，聚合分批＋`SELECT 1` 正对照（本班实测 [(1,)]）；`grep -rl .runtime/` 会超时（目录巨大），扫调度证据改窄路径或直接读 `ingest_ts`。
