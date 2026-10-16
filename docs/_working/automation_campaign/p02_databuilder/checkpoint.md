---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ②数据建设席·游标
---

# 游标

cursor: 已收口（本班 tick_depth_5 回补 15 格 DB 写已提交并逐位验收，无在途批；回退谓词在册未执行；B-15 commit_pct=77.88 未过 70 闸＝不起批；三整日判未封板）
last_run: 2026-10-16 22:2x
last_batch: st-qoder-p02-1016-02
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

---

## 游标覆盖式更新 · st-qoder-p02-1015-07（10-15 17:3x）——**下一班只读本节即够**

`cursor: 已收口`（本班 DB 写已提交并逐位验收，无在途批）｜`last_batch: st-qoder-p02-1015-07`｜耗时 **27 分 51 秒**（`date` 实测 17:07:42 进场 → 17:35:33 写账，**未超 60 硬窗**；本班写账时一度误记为"约 65 分钟／超窗"＝体感钟前移在册自犯形态，`date` 现测后改回，留痕见 ledger 同段）。全文＝`ledger.md` 段「2026-10-15 17:0x · st-qoder-p02-1015-07」，终态标记 `P02-1015-07-ENDSTATE`。

1. **B-22 央行族数据侧已落地＝本班保底达成**：`c1_market.macro_data` 的 `央行_*` 族新增 **2,341 行**（8 指标 × 335 个新月份），族 `FINAL` **96 → 2,437**、`months` 12 → **347**、span 1993-03-31..**2026-09-30**（＝源右端，开班上月）；31 个按年块全 `disposition=ch_committed detail=http`，逐位对拍 `missing=0／value-mismatch=0／重复键组=0／NULL=0`，回退谓词 `startsWith(indicator_name,'央行_') AND ingest_ts >= '2026-10-15 09:27:34'` 写前 0 行／写后恰 2,341（**未执行**）。写集基底＝`.runtime/tmp/p02_b22_rows_1015_07.tsv.gz`（sha16 `4810a9ce9349ac00`）。
2. **⚑该族 status 本班未翻、`unblocked.md` 本班未写＝第四查未过**，根因是一行码：`akshare_provider.py:1556` `_transform_cb_balance` 的 `df = df.tail(12)`，而源帧**倒序**（head=2026.9／tail=1993.3）⇒ 常设腿天天只重灌**最旧 12 个月**（该族 `max(ingest_ts)` 今天 17:13:44＝腿活着，右端却冻在 1995-12-31）。**处方给⑤（一行，勿扩面）**：截断前按 `统计时间` 排序再取近 12，或直接去掉截断（源全窗仅 357 行）。⑤改完下班复跑本班脚本即闭环——写者形制是"只写新键、重叠键交还腿"，天然幂等。
3. **⚑B-18 判死，且死在写侧不是源侧（下一班别再试第三种形态）**：`index_valuation_daily`＝`ReplacingMergeTree(ingest_ts) ORDER BY (symbol, trade_date)`，**`data_source` 不在键**；`index_valuation_compute.py:289/:295/:297` 把 `pb_mrq`／`broken_net_ratio`／`buffett_ratio` **硬编码 None** 且全列重灌、无 preserve；`tasks.yaml:3822 index_valuation_daily_compute_daily`＝`schedule: daily_kline`／`incremental: false`。CH 实测该轨 `max(ingest_ts)=2026-10-15 09:07:40 UTC＝本地 17:07:40`＝**本班开班那一分钟它刚全史重灌过 16,286 raw／8,144 FINAL 行**。⇒ 任何回填最迟下一次日频重算即被更高 `ingest_ts` 的 None 行洗掉；换 `data_source` 打标**不幸免**（与 B-17"两轨键重叠 0"能成立的条件＝日期互斥不同，勿套用）。**排产顺序＝MUST 先⑤给 compute 腿补"读库携带"（`_INDEX_VALUATION_PRESERVED_COLS:768-781` 的对称另一半），再②回填**；本班据此不落 B-18。`buffett_ratio` 三择一仍是 Owner 讨论项，本班未动。
4. **可复用的节拍尺（第三次生效，写进规程）**：判"某腿今天真跑了吗"用 `SELECT data_source, count(), max(ingest_ts) FROM <表> GROUP BY data_source`——比 grep 中文标签／比 tasks.yaml 硬，本班两条定性（央行族"在跑但不续深史"、compute 腿"日频洗地"）都由它给出。
5. **B-15 三闸复量**：`commit_pct=87.31`（1015-05 是 92.07、1015-06 是 94.03）仍 ≥70 ⇒ **不起批**；第④闸（归档器清单 mtime 近 10 分钟是否仍在追加）**本班没测**，下班起手先测再谈排产；队列 pending 138→2→**1**（head=`q-20261015-st-qoder-p03-1015-06-0008`，151.7s）已疏通。tick 腿 201 GiB 超盘余＝Owner 门，勿代裁。
6. **照旧不动的册**：`known_data_gaps.yaml` 本班工作区面 `MM`（①席 1015-11 在写）⇒ 整档不碰、不翻任何 status；`to_builder.md`／`to_impl.md`／`to_miners.md`／`to_datasource.md`／`unblocked.md` 全部他席在途件，随袋＝归属篡改。B-20/B-21＝新建采集腿施工面（B-20 另撞 `capability_semantic_gate.py:91-95` 的 `allowed_apis={"THS_*","ifind.*"}`，门执法本班**没跑**，属⑤/Owner 扩容），归⑩派⑤；B-16 跨日后方可再投 `pro.report_rc`；B-1/B-2/B-9 仍等 Owner"建腿 vs 退役"一字裁。
7. **⚑本班坑（下班照抄避抄）**：①ClickHouse `LIKE '央行_%'` 的 `_` 是**单字符通配**，判族前缀一律 `startsWith()`；②`macro_data` 是**无 version 列**的 ReplacingMergeTree ⇒ 回退只能靠 `ingest_ts` 划窗，写集必须"纯新增不碰重叠键"，否则谓词圈不进精确集合；③照抄在产腿的 `field_map`/`frequency` 常量保住词表唯一，但会把腿的**季频误标**一起继承（1993–2001 段源侧实为季频，本班如实登记不擅自改标）；④`df.tail(12)` 在倒序帧上取最旧 12 行——凡"取近 N 期"先看排序向，别信 docstring。
8. **本班临时件**（`.runtime/tmp/`，`[TTL] task_bound` 24h，明日 17:3x 前自清或复跑重造）：`p02_boot_1015_07.py`（注册＋`daemon_pid=33108`）／`p02_b18_probe_1015_07.py`＋`.log`／`p02_b22_probe_1015_07.py`／`p02_b22_src_1015_07.py`＋`.log`／`p02_b22_backfill_1015_07.py`＋`p02_b22_dry_1015_07.log`＋`p02_b22_commit_1015_07.log`／`p02_b22_verify_1015_07.py`＋`.log`／`p02_b22_rows_1015_07.tsv.gz`（**唯一对拍基底**）。
9. **本班袋面与锁**：files＝**2**（`ledger.md`／`checkpoint.md`），两件全程 **Edit 追加**（checkpoint 另原地改写顶部 `cursor/last_run/last_batch` 三行＝删除集仅这 3 行，键集合差自证过）⇒ 对 1015-06 袋是单调超集；袋在飞照在册**不放锁不停守护**，`lock_files.py acquire` 的 30 分钟 TTL 若到期，投袋前复 acquire。落地面只认 `git show HEAD:…ledger.md | grep -c "P02-1015-07-ENDSTATE"`。

---

## 游标覆盖式更新 · st-qoder-p02-1015-08（10-15 18:1x）——**下一班只读本节即够**

`cursor: 已收口`（本班 DB 写已提交并逐位验收，无在途批）｜`last_batch: st-qoder-p02-1015-08`｜耗时 **28 分 33 秒起算至写账**（`date` 实测 17:50:13 进场 → 18:18:46 写账，**未超 60 硬窗**）。全文＝`ledger.md` 段「2026-10-15 18:1x · st-qoder-p02-1015-08」，终态标记 `P02-1015-08-ENDSTATE`。

1. **B-23 聚合面已落地＝本班保底达成**：`c1_market.block_trade_detail` 新增 **174,834 行**（5,127 只票），左端 **2026-08-03 → 2010-01-04**；通道＝与在产腿同一条 `ak.stock_dzjy_mrtj`、解析＝直接 import 腿的 `_parse_block_trade_detail_row`（`akshare_provider.py:6573`）、`data_source='akshare'`（＝表列 DEFAULT 同值，不新造词表）；按年切 **17 块**全 `disposition=ch_committed detail=http`（最大块 2022＝19,634 行／≤12 分区）。表 FINAL 1,925 → **176,759**、`uniqExact(symbol)` 5,157、span 到 **2026-10-15**（腿今日 18:00 槽位还在写）。逐位终验 **missing=0／value-mismatch=0／重复键组=0**，回退谓词 `trade_date <= '2026-07-31' AND ingest_ts >= '2026-10-15 10:10:53'` 写前 0 行／写后恰 174,834（**未执行**）。基底＝`.runtime/tmp/p02_b23_rows_1015_08.tsv.gz`（sha16 `6e0ea3fec9992ab0`），写集 TSV sha16 `8e093716bc3aac47`。**接缝＝本班右界 2026-07-31（周五）与腿左界 2026-08-03（周一）之间只隔一个周末**（08-01/02 系非交易日，已 `strftime('%A')` 实测）。
2. **⚑不翻 status、不写 unblocked＝本班没有销卡**（两条独立理由，任一条即够）：在册条目 `block_trade_depth_and_unit_split` 的 `table:` 是 **`c1_market.block_trade`（逐笔面）**，本班只补齐了 `block_trade_detail`（聚合面）⇒ 对象不满足；且 `known_data_gaps.yaml` 工作区面 `M`（3 insertions/3 deletions 未落地，①席在写）⇒ 整档不碰。第四查本身**过了近端、没过深史段**：近端腿在册且真跑✓，但深史段是一次性回补（见第 3 条），按 SOP"只有历史一次性数据的不准当常设源"，本班不据此宣称整表续供。
3. **⚑新发缺陷一件、波及整族（本班最值钱的一条，建议⑩优先派⑤）**：`scheduler.py:2320 _compute_start_date` 对 `incremental: false` 无条件 `return today.replace(day=1)`（**第 2334 行**）⇒ 凡全量任务起点恒等于**本月初**，永远够不着月初以前。这解释 `block_trade_detail_full_refresh`（`tasks.yaml:2589`，description 自陈"5 年历史回补"）为何跑了两个月只出 2026-08 起，同型受害者至少含 `limit_up_down_full_refresh:2601`／`etf_nav_full_refresh:2612`／`technical_indicator_full_refresh` 等全部 `weekend_calibration` 条目——**这是连续四班"源侧明明可得、库里就是没有"的共同上游**。处方＝全量分支给左界（照 `akshare_provider.py:11277-11288` 已在册先例：`incremental=False` 时固定 2010-01-01，或按表内 `min(date_col)` 推断）；**本班不改调度语义**（一次唤醒整族＝爆炸半径不可控）。
4. **⚑新发缺陷二件、挡 B-23 逐笔面（改表＝Owner 门）**：`c1_market.block_trade`＝`ReplacingMergeTree`（**无版本列**）`ORDER BY (trade_date, symbol)`，而该表语义是**逐笔**（含买方/卖方营业部）⇒ 同票同日 N 笔**被排序键静默塌成 1 笔**。三把尺同向：raw 1,738 vs FINAL 1,706（本班会话中 raw 涨到 1,826）；与聚合面键级对拍 585/1,753 键（33.4%）金额偏小、**金额合计只有聚合面的 50.4%**（比值 1.9863）、成交量 2.0593；单例可复现＝000656 在 2026-10-14 六笔剩一笔、001255 在 2026-10-13 两笔剩一笔。**排产顺序＝先⑤给 `block_trade` 加笔次身份（`deal_no` 或营业部码入键＋版本列，Owner 门），再②回补逐笔深史；现在回补进去照样塌**（与 B-18"先⑤补携带、再②回填"同型判例）。附带复证一条在册形态：该表 `data_source` 全 = `ifind` 而 `tasks.yaml:118` 写 `source: akshare` ⇒ "调度在册≠该腿是写者"（B-19 的 miniqmt-vs-bdpan 同型）。
5. **①席转来的两笔定标已给机制级结论**（下班别再重测）：**(a)** 同物异单位 **10^4** 在 **1,753 键**放大样本上成立（`detail × 10^4` 折算后等值 1,154 键），不是三票抽样；**(b)** `amount ≠ price × volume` 的因＝`akshare_provider.py:6582` 的 `int(vol)` 把**万股小数位直接截断**（非四舍五入）、<1 万股归零——回补前 1,925 行里 1,004 行（52.2%）不同向、17 行 volume=0；回补后 176,759 行：>0.01 元档 77,319（43.7%）／相对>5% 档 10,243（5.8%）／volume=0 共 **622 行**。⇒ **`price`/`amount` 是源侧原值，只有 `volume` 降精度；下游禁再用 `price × volume` 反推金额**（楼8 折价轴若用反推值会系统性偏大）。列注释/资产册写入属⑤/册面，本席未动。
6. **B-15 四闸复量＝只剩第一闸挡道**：①`commit_pct=**93.17**`（进场 17:50:43 实测，`degraded=True`／`ALERT-SYS-003`／ram_used 71.2%／cpu 76.7%）≥70 ⇒ **不起批**（05→06→07→08 四班＝92.07→94.03→87.31→93.17，同档未缓解）；②队列 head=`q-20261015-st-qoder-p09-1015-13-0001` 等待 **6.9 秒**、daemon online ⇒ 疏通；③分块铁律本班第二次实操验证够用；④**归档器并发闸已解除**——清单真路径 `F:/zephyr_cold/50_archive/by_project/zephyralpha/archive_manifest.jsonl`（⚑令面从未给全路径，本班 `os.walk` 定位；mtime **2026-10-15 12:31:06**／789,332 B，17:52:55 复量＝**5h22m 无追加**）。tick 腿 201 GiB 超盘余仍属 Owner 门。
7. **下一手＝B-19，但起手先过词表分叉这道"讨论门"**：`earnings_forecast.forecast_type` 我库 10 值含 **"其他"** 而无 **增亏/减亏**，源侧 11 值有后者——**折进"其他"＝丢信息、新增两枚举＝改词表**，两条都不是回补而是口径分叉 ⇒ 按在册"新设计分叉先讨论"请 Owner/①先定映射，本席不自决（第 4 把闸＝`earnings_forecast` 键不含 `data_source`、版本列 `ingest_ts`，而在册 miniqmt 腿自 2026-07-23 零产出；`express_report` 盘面已有 bdpan＋akshare **双轨先例**可参照）。**B-16 跨日后方可再投 `pro.report_rc`**；B-20/B-21＝⑩派⑤施工面；B-24 属判据并条、无本席落地面；B-1/B-2/B-9 仍等 Owner 一字裁。
8. **⚑本班自犯一枚（尺失真形态，第 N 次同族）**：首版验收拿 Python `round(x, 2)`（半偶）对 CH `Decimal(18,2)` 的**服务端截断（ROUND_DOWN）** ⇒ 假报 `mismatch=7,068`；改成"两列同向截断"后 `mismatch=0`。处方＝**Decimal 列逐位对拍必须显式指定舍入方向并与服务端一致，`round()` 不是中性尺**。另四处坑：①`stock_dzjy_mrtj` 对空返回直接抛 `TypeError: 'NoneType' object is not subscriptable`（本班撞在周末窗），禁当"该窗无史"；②该源 **5,000 行硬截断且返回序＝按 `成交总额/流通市值` 降序不是日期序**（截掉的是比率高的一头），按月窗切才安全（整年窗 2015/2019 实测恰 5,000，月窗取回真值 7,002/9,030）；③本机 `system.columns` 返回空、`DESCRIBE TABLE` 正常 ⇒ 取列形制只认 DESCRIBE；④CH `INNER JOIN ... USING` 配 `countIf` 本班实测自相矛盾（common=585 < bt_less=1154）⇒ 两表键级对拍改走 Python 侧。
9. **会话与袋面（本条含本班两处自纠，旧文不抹、另记于此）**：开班按在册形制做＝**同一个 python 进程内** `SessionRegistry().register(sid, pid=0, held_files=[两件])`＋`_spawn_heartbeat_daemon(sid, Path('D:/ZephyrAlpha'), 30)`（`daemon_pid=32860`）。⚑**首版此处写"全程未被外来 cleanup 收走"＝本班自己随后证伪**：18:2x 首投 `git_commit.py --enqueue` 被 **`SESSION-REQUIRED` 预检拦下**，实测 `.runtime/session_registry/st-qoder-p02-1015-08.json` 分片**文件不存在**、`tasklist //FI "PID eq 32860"` 报"没有运行的任务"（守护已被收走），连 07 班的条目也不在。修因＝**重跑 boot 脚本**（注册幂等，条目 515B 复现＋新 daemon `58572`）**并紧接着 enqueue** ⇒ `ENQUEUED: q-20261015-st-qoder-p02-1015-08-0001 (files=2)`；预防面另把 **sid 本身**写进 `data/runtime/process_reaper_keep.txt`（在册先例＝`st-qoder-p07-1015-03` 这类会话名条目，`_spawn_heartbeat_daemon` 起的进程在 reaper 的 `runtime_dir_orphan_watch` 眼里就是 `.runtime` 孤儿）。⇒ **下班起手式修正＝"开班注册"不等于"投袋时在册"，投袋前务必复跑一次注册再 enqueue，别拿开班时的读数当活性证明。** files＝**2**（`ledger.md` 纯追加、`checkpoint.md` 本节追加＋顶部 `last_run`·`last_batch` 两行原地改写，对 1015-07 袋是单调超集。判据只写**不随追加变化**的那一项＝`git diff --numstat HEAD` 现读 **ledger deletions=0＝纯追加**；⚑`cursor:` 行文字与上班逐字相同故未入删除集⇒上班写的"删除集仅这 3 行"在本班量到的是 2 行，如实改记；insertions 数字**故意不写进散文**，写死必被本班自纠批自证伪）；**排除** `known_data_gaps.yaml`（①席在写且本班不满足其对象）／`to_builder.md`／`to_datasource.md`／`to_impl.md`／`to_miners.md`／`unblocked.md`／`process_reaper_keep.txt`。⚑本班在该 keep 册追加过 `p02_b23_collect_1015_08`（采集完已退出＝陈旧令牌）与 `st-qoder-p02-1015-08`（守护需要，**落地交班后方可摘**）；该册系多班并发追加的热册（实测 397→399→402 行，期间他席加了 `st-qoder-p08-1015-06`），本班用的是非 CAS 写法，**已读回核验他人条目完好**（`st-qoder-p07-1015-03`／`mine06.py` 均在）。落地面只认 `git show HEAD:docs/_working/automation_campaign/p02_databuilder/ledger.md | grep -c "P02-1015-08-ENDSTATE"`。

10. **⚑本班第二枚自犯＋首袋落地后请照此复核（引用类错误，非判据变更）**： ledger 件②(b)/件④ 与交付复核表 #7/#8 首版的三个行号 `scheduler.py:2336`／`akshare_provider.py:6577`／`2052` 是**我按 `sed` 输出偏移心算、没 grep 就落笔**，真跑读数为 **2334／6582／2058**（该表达式全文件实为 3 处：2058 逐笔面、6582 聚合面、6676 属期指 K线族与本件无关，首版"两处"亦不准确），本文与 ledger 均已就地改正并留痕。**连带申报**：复核表首行"本班每条都已实跑"对 #7/#8 **当时不成立**（#1–#6 逐字跑过；#7/#8 于 18:35 补跑）。#5 那行 `('akshare', 2047, …10:00:24)` 是**写库前**取证，写库后同命令现读 `('akshare', 176881, …10:10:57)`（174,834 行进同一 `data_source` 组），下班重跑勿据此判台账说谎。⇒ 给⑤的话：**若照 2336 去改会改到 `_build_fetch_payload` 定义区而不是 `_compute_start_date` 的返回行——错行号比缺行号更坏。** 本席已把该形态回填长期记忆（`bitwise-device-mirrors-three-silent-downgrades` 第 6 条＝Decimal 截断 vs `round()` 不同向；`session-register-pid0-for-heartbeat-daemon` 10-15 ②席 08 班增量＝开班注册≠投袋时在册）。


<!-- P10-1016-01-FORCE-CLOSEOUT -->
> **⑩线长席强制收班提醒（2026-10-16 01:5x 实测追加，指令面-only，未改任何判据）**
> 本席 `ledger.md` 里 `[BLOCKER]` 行数实测 **0**（同尺负对照＝⑤席 8 行／⑨席 13 行命中；本席 ledger 正文 132542 字节内连 `BLOCKER` 子串都零命中⇒不是谓词伪空，是真未收班）；10-16 00:53 班同读数＝**连续两班 0 行** ⇒ 依 SOP §3⑩ 工序 9 追记本提醒。
> 下班收班三件（缺一＝本班不算收班）＝①ledger.md 追加至少一行 `[BLOCKER] <YYYY-MM-DD>|<席+班号>|<工具缺陷|判据缺失|数据问题|流程问题|需Owner>|<一句话>|<file:line 或路径>|<要谁做什么>|<高|中|低>`（零问题必写 `[BLOCKER] <date>|<席+班号>|无`）；②提交只走 `python scripts/commit_queue.py` 上游的 `git_commit.py --session <sid> --files <自家清单> --enqueue`（禁裸 git commit／禁从主区 index 直连）；③release 自家 claim＋注销心跳＋台账记实耗分钟。

---

## 2026-10-16 17:2x · st-qoder-p02-1016-01 班游标（追加节，上文各行逐字不改）

**⚑下班起手第一件（先于领单）＝本席单写面三态核实**。今晨 03:22 外来 `stash@{27}` apply 波把本席 `ledger.md` 打成 HEAD 的陈旧子集（本班实测 盘 630 行／132,542 B vs HEAD 724 行／155,353 B，`git diff HEAD --numstat`＝0 insertions/94 deletions）。谓词与处方＝①`git diff --numstat HEAD -- docs/_working/automation_campaign/p02_databuilder/ledger.md`；②**只有纯删除、零插入时**才 `git checkout HEAD -- <该件>`（盘面含 HEAD 没有的字节＝禁复位，改走热册超集差分配方）；③复位前先 `cp` 存证；④复位后 `wc -l` 应等于 `git show HEAD:<件> | wc -l`。⑩ 两道令面在册（`instruction.md` [P10-1016-17]＋`to_builder.md` ⑩1016-05）。本班已按此复位并落地 724 行版＋追加 113 行。

**本班交付终值（落地面可复量）**：①`c1_market.option_iv_surface` 官方腿 `sse_official` **388,236 行／1,099 交易日／2019-01-02..2025-12-31**（本班入库 **131,802**＝基 A 89,916＋基 B 增量 41,886）；全表 `raw==FINAL==uniqExact(五元键)==419,801`；②2020＝243/243、2022＝242/242 与 `kline_daily` 逐年交易日**逐值相等、缺口日集合空**；③1015-10 未竟班遗物（89,916 键基底，无台账无袋无收班）已抢救入库而非重建；④B-15 工序 4 自验出三处令面不符（2,533≠实测 **2,539**；行数字段不存在＝不可验；**manifest 头 UTF-8 BOM⇒utf-8 逐行 json 首条恒失败而总数不变**，第一条＝`kline_60min/200006`）。

**下班待办序（本班修订）**：
1. **B-25 续深剩三段**＝2021／2023／2025-H1（605 交易日≈18 分采集）。脚本可直接续用：`p02_b25_collect_1015_10.py` 的 `RANGES` 改三段（resume＋按月 FLUSH＋P0b 幂等三闸全备），采完 `P02_BASES=<新基> P02_COMMIT=1 python .runtime/tmp/p02_b25_commit_1015_09.py`。⚑**TTL 24h**：基底 `p02_b25_rows_1016_01_b.tsv.gz` mtime 今 16:46⇒**明日 16:4x 过期**，过期后按 ledger 1016-01 段口径重造；过期前可直接 `P02_BASES=.runtime/tmp/p02_b25_rows_1016_01_b.tsv.gz python .runtime/tmp/p02_b25_commit_1015_09.py`（不带 `P02_COMMIT`）跑**幂等复验**，应读 `IDEMPOTENT-NOOP`。
2. **B-27 tick 回补起手动作硬时限 10-18 02:00**（①席 15 班令＝对 10-08/10-09 跑一次 xtquant 试下载并申报回文）。本班未接（已落 B-25＋工序 4 自验），**下一班若不接则由①席工序 5 落断供登记**——请下班把这条排在 B-25 续深之前（时限硬）。
3. **B-15 可起批的两闸已开**（reaper 现读 `commit_pct 65.54／degraded False／breached []`＝五班以来首次缓解；归档器最近追加在 10.2 小时前）。起批前置三条＝(a) 重拍 manifest 快照并记 sha256（清单是活面，今晨已长 6 条）；(b) 读取用 `utf-8-sig`＋禁吞异常＋断言 `parsed==lines`；(c) **只挂分钟线族 63.03 GiB**（D 盘现余 100.31 GiB）；**tick 腿 96.26 GiB 禁并入**（只剩 4 GiB 缓冲，且换盘/扩容/腾挪属 Owner/⑩ 门，本席不代裁）。
4. **仍不翻 status**：`tasks.yaml:971` 期权 IV 腿现读仍 `source: miniqmt`＝官方腿无在册调度⇒续供第四查不过；`known_data_gaps.yaml` 工作区面进场时仍 ` M`（①席在写）＝压班不随袋。B-26 须先规模标定；B-1/B-2/B-9 等 Owner 一字裁；B-11..B-14 转⑤。
5. **本席陈旧保活令牌 8 枚未摘**（`data/runtime/process_reaper_keep.txt:388-409` 内属 1015-02..10 各班者）＝本班不整档重写（在册热册蒸发判例）且袋在飞，已登 [BLOCKER] 交⑫ hygiene 代摘或给 CAS 删行通道。

⚑**本班会话与锁（照 1015-08/09 处方执行成功，下班继续照抄）**：主区投袋先 `SessionRegistry().register(sid, pid=0, held_files=[自家两件])` **并立刻** `_spawn_heartbeat_daemon(sid, Path('D:/ZephyrAlpha'), 30)`（本班 daemon_pid 4420）；投袋前复 acquire（TTL 30 分，本班 15:2x claim→17:3x 投袋已跨 TTL，必复）；`git_commit.py --enqueue` 外层**禁套 `timeout`**。
⚑**本班 CH SQL 两坑（自犯改正留册）**：`GROUP BY toYear` 别名不可引（须写全表达式）；`'2020'=toString(toYear(trade_date))` 字符串对 Date 比较→`Code 47`＋整屏 C++ stack trace⇒ 键级/集合对拍一律走 Python 侧（与 1015-08"JOIN 配 countIf 自相矛盾"同族）。
⚑**本班临时件**（`.runtime/tmp/`，`[TTL] task_bound` 24h）：`p02_1016_01/boot_1016_01.py`／`verify_1016_01.py`／`b15_preflight_1016_01.py`／`b15_manifest_1016_01.py`／`b15_1016_01.log`／`verify.log`／`ledger_diskpre_1016_01.bak`（复位存证）＋`p02_b25_rows_1016_01_a.tsv.gz`／`_b.tsv.gz`（**唯一回退基底**）＋`p02_b25_collect_1016_01.log`；另 1015-10 遗物三件（`p02_b25_collect_1015_10.py`／`…_10.log`／`p02_b25_rows_1015_10.tsv.gz`）本班保留至下班续采可复用，过期由⑫ hygiene 按 24h 面自清。

`P02-1016-01-CP-ENDSTATE`（本班游标节独有标记，落地面核验＝`git show HEAD:docs/_working/automation_campaign/p02_databuilder/checkpoint.md | grep -c "P02-1016-01-CP-ENDSTATE"`；上一班游标节 `P10-1016-01-FORCE-CLOSEOUT` 各行逐字仍在）


---

## 2026-10-16 22:2x · st-qoder-p02-1016-02 班游标（追加节，上文各行逐字不改）

**本班一句话**＝B-27 P0 起手（硬时限 10-18 02:00）**已提前完成并证结**：服务端保留窗实测到 2026-09-28，10-13/09-28 由 EMPTY 变整日满档 ⇒ 判定＝**可取⇒转②回补，①席不需落断供登记**；并按正门补进 `c1_market.tick_depth_5` 15 格（5 票×3 缺格日，末趟 CLI 报 74,893 / CH 现读 RAW=FINAL=KEYUNIQ=74,878，4 趟复跑已写格逐值不增行）。全文＝`ledger.md` 段「2026-10-16 22:1x · st-qoder-p02-1016-02」，终态标记 `P02-1016-02-CP-ENDSTATE`。

**下班待办序（本班修订）**：
1. **B-27 放量＝首件**，但**必须先修 CLI 才能放量**（否则放量批仍是 0 行报 OK）。两相配方：(a) 独立下载相——按票发 `download_history_data(sym,'tick',prev,day)`，**进程内等待**（实测 60–75s 可让 3–8 格齐货），不要把下载与读放在同一次短命 CLI 调用里；(b) 缓存暖了之后 `python scripts/data/backfill_tick_depth5.py --days 20261008 20261009 20261013 --symbols <裸码勿用，须 QMT 后缀码> `（**不带 `--download`**，本班实测暖态 ≈0.7–1.3 秒/格）。规模＝7,934 票 × 3 日 = 23,802 格 ⇒ 串行下限 5.5–8.5 小时／≈68M 行 ⇒ 长批先登记 `data/runtime/process_reaper_keep.txt`，**按票分块**（单格即一次 FetchResult 直写）。
2. **放量前置＝件 3-B**：`tick_depth_5` 是**无版本列 ReplacingMergeTree**，ORDER BY `(market_type,symbol,trade_date,timestamp,price)` 不含 volume/amount ⇒ 同秒同价相邻快照静默塌行，本班实测**每格恰塌 1 行**（74,893 写进 / 74,878 在册）。⑤给笔次身份入键属 **Owner 门**；键未修就放 68M 行＝每天系统性丢 ≈7,900 行。排产呈批面已写 ledger 件 6 [BLOCKER] 第 2 行。
3. **symbol 口径（防下班重踩本席的伪空）**：表内是**裸码** `000001`/`301189`，CLI 入参是 **QMT 后缀码** `000001.SZ`，写侧由 `MiniQmtIngestProvider._stock_to_symbol` 转换（安全）；**查询侧必须用裸码**，本席首版用后缀码查回 0 行＝测量伪空。
4. **三整日仍未封板**（本班覆盖率 5/7,934＝0.063%）：10-08=24,985/5、10-09=24,986/5、10-13=24,907/5，对照 09-28=22,827,093/7,934 与 **10-16=23,672,271/7,940（live 腿今日满档）** ⇒ `known_data_gaps.yaml` 相关条 **status 一律不翻**；第四查（续供）近端腿在册在产✓、深史回补腿＝一次性，不得据此宣称整表常设。
5. **B-15 仍不起批**＝`commit_pct` 21:50:56 现读 **77.88**（≥70 闸未过；五班序列 92.07→94.03→87.31→93.17→77.88，本班为最低但未破闸）。
6. **B-25 续深三段＝别按令面找脚本**：`p02_b25_collect_1015_10.py`／`p02_b25_commit_1015_09.py` 已被 24h TTL 清走（盘面零命中），仅基底三件 `.tsv.gz` 仍在（`_b` mtime 16:53，**明日 16:5x 过期**）⇒ 要么先重造脚本再排独立长批，要么由⑩把该脚本升 `ttl:permanent` 落 `scripts/` 侧（⑤面），**勿在 60 分窗内半起**。
7. **本班起手已做的收养（下班勿重复）**：1016-01 班 113 行 ledger／24 行 checkpoint **从未入队**（队列＋dead＋dead_archive＋corrupt_20261016 四面零命中），本班逐字不改随袋投出 ⇒ 若本袋落地，下班盘面应同时含 `P02-1016-01-CP-ENDSTATE` 与 `P02-1016-02-CP-ENDSTATE` 两枚标记。

⚑**本班会话与锁（照 1015-08/09、1016-01 处方执行成功，下班继续照抄）**：主区投袋先 `SessionRegistry(ROOT).register(sid, pid=0, held_files=[自家两件])` **并立刻** `_spawn_heartbeat_daemon(sid, Path('D:/ZephyrAlpha'), 30)`（本班 `daemon_pid=31220`）；sid 本身 CAS 追加进 `data/runtime/process_reaper_keep.txt`（本班 413 行，用 `safe_write_text`＋`content_sha256(read_text())` 口径，`SafeWriteResult` 字段是 `written` **不是 `ok`**）；投袋前复 acquire（TTL 30 分）；`git_commit.py --enqueue` 外层**禁套 `timeout`**。
⚑**本班 xtquant 三坑（自犯改正留册）**：①`download_history_data` 异步 ⇒ 发完立即 `get_market_data_ex` 必读旧态（本席 v1 探针的 `after==before` 即此伪象，已被 v2 证伪并推翻）；②`10-09 读到 900 行`是**本地缓存截断**不是源面稀疏（判据＝首末时间戳 09:15→15:30 覆盖整日而 n 只及开盘段）；③`xtdata` 进程退出会带走在途下载。
⚑**本班 CH SQL 坑**：`SELECT symbol, trade_date, count()` 漏 `GROUP BY` ⇒ `Code: 215` 且 ch_writer TCP+HTTP 双试各吐整屏 C++ stack trace（本席首版自犯）；`query_rows` 是严格读（报错即抛），正对照 `SELECT 1`→`[(1,)]` 每次验收都先跑。
⚑**本班临时件**（`.runtime/tmp/p02_1016_02/`，`[TTL] task_bound` 24h）：`boot_1016_02.py`／`keep_add_1016_02.py`／`b27_probe_1016_02.py`＋`b27_probe.log`／`b27_probe2_1016_02.py`＋`.log`／`b27_depth_baseline_1016_02.py`＋`depth_before.log`／`b27_verify_1016_02.py`＋`verify1.log`／`verify_final.log`／`b27_cold_1016_02.py`＋`cold.log`／`write_ledger_1016_02.py`／`msg_1016_02.txt`／`qstatus.json`。**回补基底**＝xtquant 终端本地缓存（`E:/国金QMT交易端模拟/userdata_mini/datadir`，非本席产物，下班复量暖态即可续用）。

`P02-1016-02-CP-ENDSTATE`（本班游标节独有标记，落地面核验＝`git show HEAD:docs/_working/automation_campaign/p02_databuilder/checkpoint.md | grep -c "P02-1016-02-CP-ENDSTATE"`；上一班游标节各行逐字仍在）


---

## 2026-10-16 23:27 · st-qoder-p02-1016-03 班游标（追加节，上文各行逐字不改）

**本班一句话**＝B-27 五档深史分块回补落地 **1,401,385 行／216 票**（三缺格日票面 5→**118/7,934＝1.5%**，行面对满档日基线 6.47%，仍不封板、status 不翻）＋**塌缩尺重建**（`RAW−FINAL` 假绿作废，守恒式实测 **每格 0.99 行／整日外推 ≈7,863 行＝对上班「≈7,900 行/日」**同幅确证****）＋节奏标定＝**3.9 秒/票（24 票/批）→ 剩余 7713 票 ≈8.4 小时**／10.7 秒/票（8 票/批）→ ≈22.9 小时（批大小是决定项，上班估算未给该口径）＋工序 4 B-15 第五次自验复拍（2,539 条全 verified、快照未变、commit_pct 82.08 未破闸＝不起批）。全文＝`ledger.md` 段「2026-10-16 23:27 · st-qoder-p02-1016-03」，终态标记 `P02-1016-03-CP-ENDSTATE`。

**下班待办序（本班修订）**：
1. **本班袋若判死（上班袋先落地）取回三步**＝①`git show HEAD:docs/_working/automation_campaign/p02_databuilder/checkpoint.md | grep -c "P02-1016-02-CP-ENDSTATE"` 先量上班是否已落；②已落⇒盘面本就含上班全段（本班为严格超集），只需以新 HEAD 为基重排：复位前**必须先 `cp` 存证，并先量 `git diff --numstat HEAD` 是否纯删除**——盘面含 HEAD 没有的字节时禁复位，改走热册超集差分配方（本档 1016-01 游标段②条在册处方）；③复位动作照该条处方执行后，重追加本班段并核对上班两枚标记＋本班标记三齐。
2. **B-27 续采＝直接跑自 resume 谓词**，无需游标文件：`universe(09-28 FINAL DISTINCT symbol 升序) ∖ done(10-08 FINAL DISTINCT symbol)`；脚本＝`.runtime/tmp/p02_1016_03/b27_run2_1016_03.py`（**24h TTL，明 23:0x 过期**），参数配方 `<N> 24 840`（实测 3.9 秒/票）。⚑起班先 `date` 实测再算窗，勿按 60 分窗承诺整面（整面 ≈8.4 小时＝须走登记 keep 的长批或⑩重排产）。
3. **幂等复跑销口（验收③本班标未验）**＝对已入库票面同命令重跑一次，FINAL 不增行即销；顺带用守恒式复量塌缩（应与本班每格 0.99 行同幅）。
4. **件 3-B 复议材料已备**＝本班给守恒式尺与比值；请⑩汇总呈 Owner 定"键先改/先放量"次序。本席不自裁。
5. **B-15 仍不起批**＝判据只看 `commit_pct<70`；本班现读 82.08。三条前置（重拍快照 sha／`utf-8-sig`／只挂分钟线族 63.03 GiB）本班已复核完毕，下班只需再读一次闸值。
6. **仍不翻 status**＝`known_data_gaps.yaml` 工作区面他席在写（本班进场即 ` M`，压班不随袋）；期权 IV 腿 `tasks.yaml:971` 源面仍 `miniqmt`（续供第四查不过，上班在册）；B-26/B-28 各须先规模标定与当期宇宙判据，勿在 60 分窗内半起。

⚑**本班会话与锁（下班照抄，本班实测有效）**：`SessionRegistry(ROOT).register(sid, pid=0, held_files=[自家两件])` **并立刻** `_spawn_heartbeat_daemon(sid, Path('D:/ZephyrAlpha'), 30)`（本班 daemon_pid **46956**，收班现读存活=0）；sid CAS 入 `process_reaper_keep.txt`（本班 417→418 行；`SafeWriteResult` 真字段＝`written`，**无 `ok`**，`getattr(res,'ok','?')` 实测 `?`）；②**runner 的 argv 必须带 sid**（reaper 白名单按 cmdline 子串命中，脚本路径名不含 sid ⇒ 只加 sid 不加 argv 等于没加）；投袋前复 acquire（TTL 30 分）；`git_commit.py --enqueue` 外层禁套 `timeout`。
②**本班 xtquant 新读数**＝`download_history_data` 一次区间 `20261007→20261013` 可同时喂三缺格日（8 票 2.4–4.3s／24 票 ~12s 发完，70s 等待后读回）；空格率 **48%**＝退市/停牌/无行情，非通道故障；`格_err=0`（两块共 648 格零异常）。
②**本班临时件**（`.runtime/tmp/p02_1016_03/`，`[TTL] task_bound 24h`，共 10 件）＝b27_batch_1016_03.json、b27_caliber_1016_03.py、b27_run.log、b27_run2.log、b27_run2_1016_03.py、b27_run_1016_03.py、boot_1016_03.py、keep_add_1016_03.py、msg_1016_03.txt、write_ledger_1016_03.py。

`P02-1016-03-CP-ENDSTATE`（本班游标节独有标记，落地面核验＝`git show HEAD:docs/_working/automation_campaign/p02_databuilder/checkpoint.md | grep -c "P02-1016-03-CP-ENDSTATE"`；上一班游标节各行逐字仍在）


**23:33 游标补记（P02-1016-03B，逐字追加不改上文）**＝本班件 0 的自然实验结论已改变本班收班动作＝**本班只投一袋**（`q-20261016-st-qoder-p02-1016-03-0001`，files=2，已 ENQUEUED；claim 已 release 2/2；心跳 46956/48360 按 PID 杀并 60s 双读复核 False；投袋后 23:32:12 复现 `.aidrafts/st-qoder-p02-1016-03` 影子树 1 枚＝工具自建、勿自删、已在件 5 挂号转⑩）。⇒ **下班起手第一件改为**：先量 `git diff --numstat HEAD -- ledger.md`，若读数为"纯 insertions 且行数＞本班袋 payload 差值"＝本班件 7 更正段仍未落地，**逐字收养随你班袋投出**；再按待办序第 1 条核本班袋是否已落（`git show HEAD:.../ledger.md | grep -c P02-1016-03-ENDSTATE`）。

`P02-1016-03B`（补记节独有标记，落地面核验＝`git show HEAD:docs/_working/automation_campaign/p02_databuilder/checkpoint.md | grep -c "P02-1016-03B"`）

---

## 2026-10-17 00:34 · st-qoder-p02-1016-04 班游标（追加节，上文各行逐字不改）

**本班一句话**＝B-27 验收④**幂等复跑销口取得**（重灌 289,558 行，FINAL 289,489→289,489＝**DELTA 0**、RAW 同步零增）＋**空格按票名级交付**（87 枚逐字入台账件 2，上班"交不出空格清单"在采集面解除；⚑归因尺第二层 symbol 列交叉核本班未被非空格触发＝**未触发不是通过**，见 ledger 件 2）＋续采 168 票（uniq 118→199）＋塌缩复现每格 0.99 行（对上班 0.99 同幅）＋B-15 闸值 83.73≥70 第六次复证不起批。全文＝ledger 段「2026-10-17 00:34 · st-qoder-p02-1016-04」。

**下班待办序（本班修订）**：
1. 起手**两件**＝(a) `git diff --numstat HEAD -- ledger.md checkpoint.md`：若盘面纯 insertions 且含本班段＝**逐字收养随你袋投出**（同席写域），再核 `git show HEAD:docs/_working/automation_campaign/p02_databuilder/ledger.md | grep -c P02-1016-04-ENDSTATE`；(b) ⚑**本班实测换来的新增判据**＝`python scripts/commit_queue.py status` 里按 `st-qoder-p02-` 扫前任 sid 是否仍 pending/processing——本班 00:28:42 亲历「前任游标三证齐自称收班、38 分钟后自己补投第二袋落地」，故**收班自述不等于无在途袋**，先查队列再动笔可免双写撞面。
2. B-27 续采＝直接跑自 resume 谓词，参数配方本班复标＝**批 24 票、预算按"票/班"而非秒/票**（本班 7 块 168 票、`per_sym` 末值 5.7 秒/票，比上班 3.9 秒/票慢，因 read 相随 CH 负载漂）；排除集＝**从本班 ledger 件 2 的 EMPTY-LIST 行逐字重建**（⚑`.runtime/tmp/p02_1016_04/excl_1016_04.txt` 按收班⑤自清纪律已随班删除，勿再去 tmp 找——在册教训＝清 tmp 前须 grep 消费者）。⚑起班先 `date` 实测再算窗。
3. **件 1 幂等腿已销，勿重复做**；本班留一条**未触发判据**待下班销口＝归因尺第二层（每个非空格核 `row[3]` symbol 全等）在本班窗内零行使（全部格零行），**下班须在"有货票面"复跑一次该层**（最省＝直接对 DONE 里任取 24 票跑同一 divmod 尺，非空格数应 >0），跑通才准写"票名归因可用"。另＝放量前严重度复议材料转呈（本班件 4 第 2 行给了"同批内键重复 69 行"这第二层证据）。
4. B-15 判据只看 `commit_pct<70`（本班 23:51 现读 83.73）；三条前置上班已复核完毕，下班只需再读一次闸值。
5. `known_data_gaps.yaml` 仍不随袋（本班 `MM` 复证）；期权 IV 腿与 B-26/B-28 各须先规模标定与当期宇宙判据，勿在 60 分窗内半起；**10-18 02:00 前**的 xtquant 试下载腿＝五档面本班已按 (票×日) 试过并逐票归名，`tick_data`（18 列逐笔面）**不在本席红线内、仍未试**，该时限属 ②/① 共认在册，请⑩在 10-17 派单时点名承接者。

⚑**本班会话与锁（下班照抄，本班实测有效）**：`SessionRegistry(ROOT).register(sid, pid=0, held_files=[自家两件])` **并立刻** `_spawn_heartbeat_daemon(sid, Path('D:/ZephyrAlpha'), 30)`（本班 daemon_pid 18124）；sid CAS 入 `process_reaper_keep.txt`（本班 418→419）；runner argv 末位必带 sid（reaper 白名单按 cmdline 子串命中）；`git_commit.py --enqueue` 外层禁套 `timeout`；⑂ 收班删除保活令牌时**只摘自家 sid**（`st-qoder-p02-1016-03` 上班令牌在其袋已落地后仍在册＝本班见 418/419 行相邻，属⑫清扫面，本席不代摘）。
②**本班 xtquant 新读数**＝区间下载 `20261007→20261013` 一次可喂三缺格日在重灌面同样成立（24 票 dl 11.6s）；终端本地缓存**跨班仍暖**（本班未重下也应得，但本班照配方重下故不作"缓存持久性"结论）。
②**本班临时件**（`.runtime/tmp/p02_1016_04/`，`[TTL] task_bound 24h`）＝boot/keep_add/b27_idem/b27_run3/write_ledger 五件 .py＋idem.log/run3.log/excl_1016_04.txt/msg_1016_04.txt。

`P02-1016-04-CP-ENDSTATE`（本班游标节独有标记，落地面核验＝`git show HEAD:docs/_working/automation_campaign/p02_databuilder/checkpoint.md | grep -c "P02-1016-04-CP-ENDSTATE"`；上一班游标节各行逐字仍在）

**2026-10-17 00:39 游标补记（P02-1016-04-CP-B，逐字追加不改上文）**＝本班首袋 `q-20261017-st-qoder-p02-1016-04-0001` 收班时现读 **pending／队前 8**，而本班件 8 收班补记（含①②⑧实测读数与"同目录 instruction.md 3/0 系外来临时未随袋"一条）**写在盘面未随袋**⇒ 下班起手第一件改为：先 `python scripts/commit_queue.py status --session st-qoder-p02-1016-04`，若仍 pending⇒把本席盘面 `P02-1016-04B` 整段**逐字不改收养**随你袋投出；若已 done⇒照件 8 读数核 `git show HEAD:.../ledger.md | grep -c P02-1016-04B`，缺则另投（条件＝前袋 done 且 base 取最新 HEAD，本班已把该正解写进件 0）。

`P02-1016-04-CP-B`（补记节独有标记，落地面核验＝`git show HEAD:docs/_working/automation_campaign/p02_databuilder/checkpoint.md | grep -c "P02-1016-04-CP-B"`）


---

## 2026-10-17 01:2x · st-qoder-p02-1017-01 班游标（追加节，上文各行逐字不改）

**本班一句话**＝B-27 五档深史续采一趟分块落地，入库面（三缺格日 FINAL）`(2457070, 199) → (3852976, 313)`＋**归因尺第二层在有货面正式销口**（上班零行使 ⇒ 本班 ATTRIBUTION {'非空格': 342, '票名全等': 342, '票名错配': 0} MISMATCH_SAMPLE []，错配 0 起"裸码归因可用"成立）＋**新立放量前置闸＝通道暖态探针**（正对照 9/9 有货、负对照 2/2 零行、`_COLUMNS.index('symbol')=3` 实测）＋工序 4 B-15 第七次复拍 `commit_pct 84.46≥70` 不起批＋上班 00:39 未落地收班段（ledger 15 行／checkpoint 4 行）逐字收养随本袋。全文＝ledger 段「2026-10-17 01:0x · st-qoder-p02-1017-01」，终态标记 `P02-1017-01-CP-ENDSTATE`。

**下班待办序（本班修订）**：
1. 起手三件＝(a) `python scripts/commit_queue.py status --session st-qoder-p02-1017-01` 看本班袋四态；(b) ⚑**本班已把上班要求的"队列面按 sid 扫前任在途"跑通**（四态目录直读、零依赖，读数＝本席前任 34 枚中 pending/processing=0）⇒ 下班照抄该尺再动笔，勿只信前任游标自述；(c) `git diff --numstat HEAD -- docs/_working/automation_campaign/p02_databuilder/ledger.md checkpoint.md`，若纯插入且含本班段＝逐字收养随你袋投出。
2. **落地面核验谓词请照抄本条、勿用裸子串**（本席正文自带标记名，裸 `grep -c` 会把自家引用也数进去）＝
   `git show HEAD:docs/_working/automation_campaign/p02_databuilder/checkpoint.md | grep -c '^`P02-1017-01-CP-ENDSTATE`'`（应为 1，盘面同尺应为 2）。
3. B-27 续采＝**同脚本同谓词直接续跑**（排除集自 resume，无需人工游标）：脚本配方已在册（本档 1016-03/04 与本班段），⚑**本班新登的 6 枚"试过且空"耐久真源＝ledger 本班 EMPTY-LIST 行**（承 1016-04 的 87 枚另加），tmp 件按收班⑤随班删除勿找；起班先 `date` 实测再算窗，批 24 票、本班末块节奏 per_sym=9.2 秒/票（含 70s 等待摊销），⚑**放量前必跑通道暖态探针**（正对照取 DONE 面 DESC LIMIT 3、负对照取排除集首两枚），冷通道禁放量。
4. **件 1 幂等腿与件 5 归因腿均已销口，勿重复做**；下班若要再证塌缩，用守恒式（写前 FINAL＋写入−写后 FINAL），本班两趟复量读数已入 ledger 件 4，与两班在册"每格 0.99 行"同幅。
5. B-15 判据只看 `commit_pct<70`（本班 01:01:09 现读 84.46＝第七次不起批）；三条前置上班已复核完毕，下班只需再读一次闸值。令面 2,533 vs 实测 2,539 的六次复证继续有效，禁按令面起批。
6. `known_data_gaps.yaml` 仍不随袋（他席在写面，本班进场即 `MM`）；本班**未翻任何 status**（三整日票面远未封板）；B-28（估值深史换源）＝需新建调度＋复用 baostock provider＋当期宇宙判据，**勿在 60 分窗内半起**；期权 IV 腿续供第四查仍不过（承在册）。
7. ⚑**10-18 02:00 的 `tick_backfill_weekly` 自动窗将把 10-08/10-09 滑出在册时限**（①席 B-27 时限＋1016-04 同条）＝距该窗本班现算约 25 小时；本班未越权改 threshold（属⑤/Owner 面），只把时限再报一次给⑩排产。

⚑**本班会话与锁（下班照抄，本班实测有效）**：主区无 worktree（TRAE-079 Phase 2 遵令）；`SessionRegistry(ROOT).register(sid, pid=0, held_files=[自家两件])` **并立刻** `_spawn_heartbeat_daemon(sid, Path('D:/ZephyrAlpha'), 30)`（本班 boot 回显 daemon_pid 35008）；sid CAS 入 `data/runtime/process_reaper_keep.txt`（本班 419→420 行，`SafeWriteResult` 真字段＝`written`）；⚑**两趟采集的 argv 末位均带 sid**（reaper 白名单按 cmdline 子串命中）；`lock_files.py acquire <两件> <sid>` TTL 30 分 < 班限 60 分 ⇒ **投袋前必复 acquire**；`git_commit.py --enqueue` 外层禁套 `timeout`；收班②杀心跳须**末次网关调用之后**且按 pid 文件单 PID 精确杀（禁 cmdline 子串扫，在册 1017 自杀案）。
②**本班 xtquant 新读数**＝本班共试 120 票 ×3 日＝360 格，其中有货格 342、零行格 18（5.0%）、异常格 0；新登"三日皆空"票 6 枚（占本班试票 5.0%），对照头段在册 87/216≈40% ⇒ **越往深段走空格率越低、单位时间入库效率越高**，下班排产按"票/班"外推，本班末块节奏 per_sym=9.2 秒/票。
②**本班临时件**（`.runtime/tmp/p02_1017_01/`，`[TTL] task_bound 24h`）＝boot/keep_add/probe_channel/b27_run/write_ledger1（已随件消费当场删）/write_ledger2/write_cursor 各 .py＋run.log/run2.log/excl_1017_01.txt/msg_1017_01.txt。

`P02-1017-01-CP-ENDSTATE`（本班游标节独有标记，落地面核验谓词见本段待办序第 2 条；上一班游标节各行逐字仍在）
---

## 2026-10-17 02:1x · st-qoder-p02-1017-02 班游标（追加节，上文各行逐字不改）

**本班一句话**＝B-27 主落地件＝**在册"试过且空"93 枚经逐票复验全数翻案有货并当场回补入库**（三缺格日 FINAL `(3852976, 313)`→`(5233549, 406)`＝**＋1,380,573 行／＋93 票**，279 格全命中、err 0、票名错配 0）＋**根因定性**＝`download_history_data` 异步派发而采集腿下载后只等 60–100 秒即读终端缓存，未落盘格返回 0 行且 `error=None` 与"确无货"同形⇒前两班"空格率随深度递减""零行段与已试区对齐"两条结论都是同一伪影＋暖态闸谓词改正（只认正对照臂，负对照臂降级为排除集复验尺）＋B-15 第八次复拍 `commit_pct 87.66≥70` 不起批＋本班**零收养面**（上班袋 01:56 已落地）。全文＝`ledger.md` 段「2026-10-17 02:0x · st-qoder-p02-1017-02」，终态标记 `P02-1017-02-CP-ENDSTATE`。

**下班待办序（本班修订）**：
1. ⚑**起手第一件＝别再抄旧排除集**＝`本台账 1016-04 件 2 的 87 枚＋1017-01 件 5 的 6 枚` 已被本班 **93/93 翻案**（`STILL-EMPTY 0 枚`），该集作废后谓词天然单口＝**UNIVERSE(09-28 FINAL distinct) ∖ DONE(10-08 FINAL distinct)**，无需人工抄录件（本班 [BLOCKER] 第 2 条已请⑩定永久归属；定案前下班按此两面差集起，勿再引 EMPTY-LIST 散文）。
2. 暖态探针谓词改正＝**正对照臂唯一承重**（DONE 面按 symbol DESC LIMIT 3 × 三缺格日，本班实测 9/9 有货）；负对照臂（旧空票）本班已证其"应为零行"前提不成立⇒降级为"排除集复验尺"，其翻面**不阻断放量**。冷通道判据仍有效＝正对照零命中⇒不起采只报堵。
3. 节拍与等待配方（本班实测）＝下载派发 **0.28 秒/次**（24 票×3 日 72 次仅 20.0 秒），首块等 100 秒、后续块等 60 秒后 read 相 35.0–48.7 秒/块、**零空零 err**；归因配对序仍须 `seq=[s for s in blk for _ in DAYS]`（票主序，与 `backfill_days` 生成序同构）＋`zip(strict=True)`＋块内 `len(cells)!=len(seq)` 即停。⚑要判"某票真无货"必须**二次复读间隔后仍空且 err 仍 None** 才准记（本班 [BLOCKER] 第 1 条）。
4. 面值续位＝三缺格日 FINAL `(5233549, 406)`；UNIVERSE=7934；DONE(10-08)=406；剩 **7,528 票**；本班节奏 **5.55 秒/票**（＝516.2 秒/93 票）⇒整面约 11.6 小时单进程量，60 分窗结构性做不完（本班 [BLOCKER] 第 5 条，请⑩重排产）。⚑塌缩守恒式本班余数 **0 行**（每格 1.00），与 1016-04/1017-01 的"每格 0.99 行"同尺不同幅⇒该余数勿当定值验收判据（[BLOCKER] 第 3 条）。
5. 票码映射禁自造前缀规则＝取 `src/zephyr/data/tick_subscriber.py:620 _get_all_symbols` 同一组 QMT 板块名（沪深A股/京市A股/沪深基金/沪深转债/沪深指数）反查裸码，本班实测入图 **8755** 条、跨板块裸码碰撞 **100** 枚（按板块序首见，本班口径已披露）、**4 枚 UNMAPPED**＝`110075,128134,159047,166007`（转债/基金码不在终端板块面，**禁记进"试过且空"**）。
6. 工序 4 B-15＝判据只看 `commit_pct<70`（本班 02:03:48 现读 **87.66**＝第八次不起批；起手 01:50:45 那趟 90.08/degraded True）；令面 2,533 vs 实测 2,539 的六次复证继续有效，禁按令面起批、禁重复重拍快照。
7. `known_data_gaps.yaml` 仍不随袋（本班进场即 `MM`，他席在写）；本班**未翻任何 status**（406/7934＝5.1% 远未封板，三查③与第四查虽"两腿均在册调度"但封板判定未闭）；同目录 `instruction.md` 亦他席件**不随袋**。B-28 仍勿在 60 分窗内半起（需新建调度＋当期宇宙判据）。
8. 时限复报＝10-18 02:00 的 `tick_backfill_weekly` 自动窗将把 10-08/10-09 滑出（本班 02:16 现算距该窗约 **23.7 小时**）；④席下游评估窗右端仍停 2026-10-07。
9. 会话与锁三条（本班实测代价换来的）＝(a) boot 脚本必须把**仓根**也送进 `sys.path`，否则 `_spawn_heartbeat_daemon` 报 `No module named 'scripts.ops_guard'` 而**注册仍打印成功且 rc=0**＝活性锚假绿；(b) 起手即 `mark_logical(sid, logical=True)` 上真盾——本班 pid=0 会话在 **claim TTL 远未到期**时被外来回收（02:16 实测 `lock_files.py list` 对本席 sid 命中 0，02:0x 还是 2 件各剩 29.8m），复 acquire 才恢复；(c) 投袋前复 acquire＋杀心跳只认 pid 文件**单 PID**（禁 cmdline 子串扫描）。
10. 落地面核验谓词（勿用裸子串，正文自带标记名）＝`git show HEAD:docs/_working/automation_campaign/p02_databuilder/checkpoint.md | grep -c '^`P02-1017-02-CP-ENDSTATE`'`；上班 1017-01 那条"盘面同尺应为 2"的预言本班实测是 **3**（正文两处抄录该串）⇒计数请按行首形态而非裸子串。

⚑**本班会话与锁（下班照抄）**＝主区零 worktree（TRAE-079 Phase 2）；`register(sid, pid=0, held_files=[两件])`＋`_spawn_heartbeat_daemon(sid, ROOT, 30)`＝daemon_pid **40268**（幂等复跑同 pid）＋`mark_logical(True)`（本班实测回 True，未遇 1015-08 那趟"非 chief 形态降级"）；sid 已 CAS 入 `data/runtime/process_reaper_keep.txt`（本班 base 430→431 行，⚑该册起手 `wc -l` 读到 428、写前读到 430＝他席在本班值守内追加，本班只报自家 delta）；两件采集脚本 argv 末位均带 sid。袋面＝files=**2**（`ledger.md`／`checkpoint.md`，全程纯追加、`git diff --numstat HEAD` 删除集 0）；**排除** `known_data_gaps.yaml`／`feedback/*`／`instruction.md`／`process_reaper_keep.txt`（他席在途或非本席写域）。本班临时件＝`.runtime/tmp/p02_1017_02/` 六 .py＋六文本，读数已逐值抄录入账后按收班⑤删除（⚑`b27_reverify_1017_02.py` 与 `b27_run_1017_02.py` 有 import 依赖，须同批且末件删）。

`P02-1017-02-CP-ENDSTATE`（本班游标节独有标记，落地面核验谓词见上段第 10 条；上一班游标节各行逐字仍在）

**2026-10-17 02:34 游标更正（P02-1017-02-CP-B，逐字追加不改上文）**＝本班待办序第 9 条 (b)「起手即 `mark_logical(sid, logical=True)` 上真盾」被本班随后实测**反证**＝02:16 复 acquire 并当场 mark_logical 回 True（分片读回 `logical=True pid=0 held=2`），02:18:22 复量 `lock_files.py list` 对本席 sid 仍命中 0 ⇒ **真盾不是 mark_logical**（它只挡"条目被摘"，挡不住"锁被回收"）。代码级机制＝`scripts/lock_files.py:186 _is_stale()` 的判活谓词不看锁 TTL，而经 owner.json 的 session_id 走 SessionRegistry 会话判活（同文件 192–197 行在册 F2 治本注释自述 pid=0 走心跳 90 秒）⇒**任何一班冷启动第 2 条 `lock_files.py cleanup` 都会据此回收他人 claim**；本班 02:33 实测该判活的读取面报红两条原文＝`shard skipped (corrupt/unreadable) file=st-qoder-p05-1017-01.json: [Errno 13] Permission denied`＋`failed to load legacy registry: [Errno 13] Permission denied`⇒聚合面读不下去时判活偏向"死"，活会话锁被结构性误收（已登⑫/⑤呈批，全文＝ledger 本班件 8）。**下班规避动作（实测有效）＝复 acquire 之后立刻投袋，acquire 与 enqueue 之间不插任何动作**＝本窗 02:18:37 复 acquire → 02:19:06 入袋，网关回显 `ENQUEUE-RENEW: claim 续租 2/2 件（ttl=7200s）`，且袋 blob 与盘面逐字节相等⇒随后锁即便再被收也不丢本班面。⚑另注＝收班 release 时 `--release-only` 的回执自相矛盾（先打 `NOT FOUND — 未被锁定` 两支，又打 `BATCH-SUMMARY — released=2 / RELEASED: 2 files (verified)`），本班**采盘面直查**为终态＝`.runtime/locks/` 内 grep 本席 sid 命中 0（＝无锁在持），不信工具自述；下班判"锁是否还在"请同样两用并查。本班取号三面并集自证（承 10-17 在册"取号只数台账⇒撞鬼班"新教训）＝台账面本 sid 命中 5 次（全为本班）＋tmp 面 01:51 起手扫描无 `p02_1017_02`＋队列面仅 `done/q-20261017-st-qoder-p02-1017-02-0001.json` 一枚且 `.seq` 计数为 0001⇒本班号无前任。

`P02-1017-02-CP-B`（本班补记节独有标记，落地面核验谓词须按行首形态、勿用裸子串＝本段标题行也含该串，裸量会得 2＝`git show HEAD:docs/_working/automation_campaign/p02_databuilder/checkpoint.md | grep -c '^`P02-1017-02-CP-B`'` 应为 1；上一节各行逐字仍在）

