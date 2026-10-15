---
ttl: task_bound
completes_when: 对应数据就位并被消费席确认
title: 解锁清单（②数据建设席产出）
---

# 解锁清单（②→⑥）

格式：日期｜建设/回补项｜由此满足 data_binding/lineage 的卡号清单｜验收三查记录指针。

（空册待首班填写）

## 10-15 07:07 · st-qoder-p02-1015-01 · 回补项 B-3 → 研报评级变动列就位

- **建设/回补项**：`c3_fundamental.research_report.rating_change` 派生回填 146,940 行（①席建设单 B-3）。四态读数=维持 92,173／上调 19,735／下调 19,522／首次 2,458／留空 13,052；非空率 **91.12%**；同源一致性 mismatch=0；幂等复跑 FINAL 不增行；`OPTIMIZE FINAL` 后 raw=FINAL=uniq=146,940（不带 FINAL 的旧探针形态不再双计）。验收三查全文=台账 `docs/_working/automation_campaign/p02_databuilder/ledger.md` 10-15 07:07 段。
- **由此满足 data_binding 的卡号**：
  1. `TDM-E-L9-A17/calibration/02_研报评级调整事件研究`（现册 status=`blocked_on_data`）——该卡在册解锁条件"rating_change 非空率>=60% 且看空类样本>=300 条"**两档均实测超线**（91.12%；下调全史 19,522 条，限 publish_date>=2022-01-01 仍 11,324 条）。本班只报数据面就位，**卡状态改判不归本席**（⑥制卡/⑨成绩官面）。
  2. `TDM-E-L2-09/calibration/03_评级上调聚集`（现册 status=`preregistered`）——其 `signal_column` 含 `rating_change`，且卡内自述"rating_change 列若有值则以其为准并与自算口径对账（差异>5% 先查口径再开考）"；列已就位，对账腿可开。口径提示：本列由**东财研报中心评级**派生（序数 买入5>增持4>中性/持有3>减持/回避2>卖出1，`rating=''` 留空不造），与券商原文口径不同源，禁混。
  3. `TDM-E-L2-09/calibration/02_板块催化剂密度`——`signal_column` 列面（industry/rating/rating_change/publish_date/org_name/symbol）本班起 `rating_change` 由空转实，列面补齐；该卡是否依赖此列做主信号由⑥席判。
  4. 关联提示（不解锁）：`TDM-E-L9-A17/calibration/03_一致预期修正` 是 A17 在"rating_change 100% 空"时的替代可算面，现 A17 已具备开考前件——两卡是否并存/退役属⑥席与 Owner 面，本席不代裁。
- **未解锁的卡**：建设单 B-1/B-2/B-4/B-5/B-6/B-7 六张本班未动，其卡号（含 `TDM-E-L9-A15/calibration/02_资金费率拥挤跨市场预警` 依赖 `c1_market.hl_liquidation_raw`）仍卡在原 data_binding 上。
- **有效前提（重要）**：本列新鲜度受"研报明细增量腿自 2026-10-01 起 0 行入库"约束（见台账在途风险 1）。新行到达时 `rating_change` 会是空串（采集器不派生），**非空率将随新数据稀释**——派生日度化（或采集器写前派生）落地前，A17 的事件窗建议截到 `publish_date<=2026-09-30`。

## 10-15 08:15 · st-qoder-p02-1015-02 · 一致预期快照轴回补 → **本班不产新解锁**（负结论留痕，防他班误判）

- **建设/回补项**：`c3_fundamental.consensus_daily` 快照轴回补 +26,658 行，`max(trade_date)` 2026-09-30 → **2026-10-15**，10 月六交易日齐（10-08/09/12/13/14/15），幂等复跑 FINAL 恒 6,856,034、uniq 主键=FINAL。验收三查全文=台账 `docs/_working/automation_campaign/p02_databuilder/ledger.md` 10-15 08:15 段。
- **由此满足 data_binding 的卡号**：**零张**。理由逐条（负结论也是结论，禁按"表变新了"就报解锁）：
  1. 吃 `consensus_daily` 的在册卡只有两张（`grep -rl consensus_daily exam_cards/` 实测=2），且**都不处 `blocked_on_data`**：`TDM-E-L9-A17/calibration/03_一致预期修正` 现册 status=`preregistered`；`02_研报评级调整事件研究` 的 signal_table 是 `research_report`（上一班 B-3 已报数据面就位）。
  2. 03 卡的 `signal_column=eps_consensus` 落在 **plain consensus_daily 值类列**，而缺口 `consensus_daily_value_cols_pit_broken` 现册 status=**open**（值类因子在 plain 表禁用裁定生效中）⇒ 本班补的是**快照轴**（逐交易日行齐），**没补信息轴**（10 月全部行 `last_report_date=2026-09-30`，`n_reports` 逐日衰减 4,474→4,417）。该卡若按 20 日修正幅度开考，10 月段修正值恒 0/近 0，属"数据齐而信号空"形态，**本班明确不背书其可考**。
  3. 卡内 `data_window_evidence` 在册读数仍是旧值（trade_date 至 2026-09-30、rows=6,829,376）——本班**未改卡**（卡面归⑥制卡席），只在此登记"证据块与盘上现值已不一致"，供⑥席复核。
- **下游可用性变化（非卡级）**：任何按 `consensus_daily` 逐交易日取数的消费面，自本班起可读到 2026-10-15；若其语义要求"当日新研报参与聚合"，仍须待研报明细腿补跑完成后重跑本腿才有信息含量（本班已起补跑，见台账本班 §定因 3/4）。
- **本席建议给⑥/⑨席的一句话**：`consensus_daily` 的 10 月段可以用作"矩阵连续性"自检，**不可**用作 EPS 修正信号的样本增量，除非先确认 `research_report` 的 10 月行已入库且 `last_report_date` 随之推进。

## 10-15 09:1x · st-qoder-p02-1015-03 · 本班**零解锁**（两件均不触 data_binding），另交一条"疑似缺数"反证

- **建设/回补项 1**：`scripts/data/bdpan_tick_watch.py`（①席建设单 B-10）路径常量治本＋探路失败显式告警（新退出码 4、告警行 `BDPAN-PROBE-FAIL`）。**由此满足 data_binding 的卡号=零张**：本件是网盘分笔缺口守护脚本，无任何在册卡以它为绑定源；且本班实测缺口 7 日（2026-07-03/06/07/08/09、08-05/06）在 `c1_market.tick_data` **早已全有数**（各 1,392–1,513 万行，data_source 全 bdpan），故连"回补面新解锁"也不存在。
- **建设/回补项 2**：①席楼8 回函第 4 条"shareholder_count 探针可见性"定性=**探针无需修**，因①席用的是 `c1_market.shareholder_count`，实测该表在 **c3_fundamental**。本班用与①席同名的严格通道 `zephyr.data.ch_reader.query_rows/count_strict` 按真名复跑：FINAL **515,280**、raw 515,690、uniq symbol **5,907**、`quality_flag` 分组单组 `1`（100%，④席"恒 1=死列"**复证成立**）、`countIf(announce_date<end_date)`=**3,904**（④席值**逐值复现**）、`>end`=509,418、考试窗 2019-01-04..2025-09-09 内 261,802 行。**由此满足 data_binding 的卡号=零张**——④席卡 `SIC-20261015-P04-09` 的 `primary_table` 本来就写对（`c3_fundamental.shareholder_count`），本班未改任何卡，卡状态改判不归本席。本件价值＝拆掉一条挂在①席案卷上的"读不到⇒疑似探针坏"空转前提，并把④席两项读数从"单方申报"升为"两方独立复证"。
- **给①席的一句话（不改判据）**：B-10 单里"OS 任务 ZephyrAlpha_BdpanTickWatch state=Ready"这句本班三把尺实测**不成立**（`*dpan*` 通配零命中；`Zephyr*` 全 56 个任务无名；`generate_resource_profile_registry.py:1260` 注释自陈 2026-09-24 已删除退役）。若①席还立过别的结论在该读数上，请按台账 09:12 段复核。
- **验收三查记录指针**：`docs/_working/automation_campaign/p02_databuilder/ledger.md` 10-15 09:12 段（本班三节各带三查，含正/负对照真跑读数与可原样复跑的复核命令）。
- **未解锁清单延续**：上一班点名的 B-1/B-2/B-4/B-5/B-6/B-7 六张本班未动；本班新登记 B-11/B-12/B-13/B-14 四张的"施工动作"落点在采集器写侧（tushare 新腿/换主源＋新调度任务），**本席按 1015-02 同型判例不越界**，请⑩席派⑤实现席；B-1/B-2/B-9 三张仍等 Owner 建腿/退役门（呈批面已在 1015-02 台账合并为一份，本班不重复催）。

## 10-15 09:47 · st-qoder-p02-1015-03(续) · 研扫终态收口 ＋ rating_change/consensus 两腿复跑 → **改判本班上一段"零解锁"为"1 张卡的前提延展"**

- **回补项**：`research_report_detail_incremental` 09:43:11 终态入库 **93 行**（`publish_date` 10-01..10-14，`max=2026-10-14`）；据上一班交接令立即复跑派生 `rating_change`（FINAL 147,033=146,940+93，四态和与分年和两把尺各自闭合，mismatch=0，raw=2×FINAL 且 uniq=FINAL⇒零真重复）；再复跑 `consensus_daily_build`（rows=17,860，Oct 段 `max(last_report_date)` 09-30→**10-14**，FINAL 6,856,034→6,856,172）。全文＝台账 09:47 段。
- **由此满足/延展 data_binding 的卡号**：
  1. `TDM-E-L9-A17/calibration/02_研报评级调整事件研究`——**前提延展（不是新解锁）**：1015-01 段在册"有效前提"建议把事件窗截到 `publish_date<=2026-09-30`（因明细腿 10 月 0 行）。本班实测 10 月已 93 行且派生列非空率 91.10%（下调 19,534 条，门槛 >=300 远过）⇒ **该截点现可放到 `publish_date<=2026-10-14`**；卡状态改判仍不归本席（⑥/⑨面）。
  2. `TDM-E-L9-A17/calibration/03_一致预期修正`——本班**部分改判 1015-02 段第 2 条的负结论**：那段说 10 月段"数据齐而信号空、不可用作 EPS 修正样本增量"。本班实测内容级证据（非行数）：`300750 / forecast_year=2026` 的 `eps_consensus` **20.831875(n_reports 8) → 20.8745(n_reports 10)**、`last_report_date` 09-29 → 10-09，即 10 月新研报已进聚合并**改变数值**；Oct 段带 10 月研报的行 **831** 条。⇒ **10-12 起可作样本增量**；但 10-08/10-09 两日 rows 与 `max(last_report_date)` 本班实测**未推进且未定性**，考 20 日修正窗时**建议从 2026-10-12 起算**，别整月一起烧（值类列在 plain 表禁用的在册裁定本班未动）。
- **本班仍不解锁**：B-1/B-2/B-4/B-5/B-6/B-7/B-11/B-12/B-13/B-14 十张（B-11..B-14 施工落点在采集器写侧，请⑩席派⑤席；B-1/B-2/B-9 等 Owner 门）。

## 10-15 10:4x · st-qoder-p02-1015-04 · 回补 consensus_daily 10-08/09 → **零新解锁，但把上一班"10-12 起算"的建议改判为"10-08 起算"**

- **回补项**：`scripts/ch/build_consensus_daily.py --start 2026-10-08 --end 2026-10-09` 幂等重建两天快照（两跑各 8,960 行）。全文＝台账 10-15 10:3x 段。
- **由此满足 data_binding 的新卡号＝零张**。理由：吃 `consensus_daily` 的在册卡仍只有 02/03 两张（1015-02 段在册 grep 读数），02 卡绑的是 `research_report`（1015-01/03 已报数据面就位），03 卡现册 status=`preregistered` 且其 `signal_column=eps_consensus` 仍撞在册缺口 `consensus_daily_value_cols_pit_broken`（status=**open**，值类列在 plain 表禁用裁定本班未动）⇒ **本班补的是"快照轴＋信息轴"的日期缺口，没解列面禁用门**。
- **对上一班建议的部分改判（另起留旧案，不抹 09:47 段）**：1015-03 那段写"10-08/09 两日 rows 与 `max(last_report_date)` 未推进且未定性，考 20 日修正窗建议从 **2026-10-12** 起算，别整月一起烧"。本班已定性（真因＝`_INCREMENTAL_OVERLAP_DAYS=3` 使这两天没进产出行集，非"无 EPS 不产行"）并回补到位，**内容级读数**（考试席自家 `ch_data.ch_query_df` 通道）：`002594/10-08` eps **4.27→4.286**、`n_reports` 9→10、`last_report_date` 09-11→**10-07**；`300750/10-09` eps **20.831875→20.8745**、`n_reports` 8→10、`last_report_date` 09-29→**10-09**。十月六日"带 10 月研报的行数"现＝**105/138/180/207/222/222**（逐日单调）。⇒ **若某卡只按"逐交易日快照齐＋研报进聚合"取样本，起算点可放到 2026-10-08**；卡状态改判仍不归本席（⑥/⑨面）。
- **仍未推进的门（如实挂账）**：①`consensus_daily_value_cols_pit_broken` 列面禁用裁定；②B-11..B-14 四张（采集器写侧，请⑩派⑤）；③B-1/B-2/B-9（Owner 门）；④**B-15 tick 腿**本班给了容量裁决（119.29 亿行≈201 GiB ＞ CH default 盘余 170.59 GiB）⇒ 全量挂回**不可自派**，扩容/腾挪属 Owner/⑩门位；分钟线三张（≈59.5 GiB）本班判可派但本班未施工（当班内存态 `commit_pct=96.21 degraded`）。
- **给⑥/⑨席的一句话**：`tick_data` 近端 10-09 起逐日塌陷（20.2M→6.7M→0.36M→**0**(10-13)→14.6k(10-14)，今日 10-15 实时腿已复），**任何吃"近 5 交易日分笔"的卡现在都不具备可考深度**，与本班补的 consensus 面无关，别把两件事并成一条解锁。
- **验收三查记录指针**：`docs/_working/automation_campaign/p02_databuilder/ledger.md` 10-15 10:3x 段（含干推演期望值 vs 实跑读数逐值表、`system.query_log` 服务器侧两笔 written_rows=8,960、PIT 违例 0、全表净增 +24 逐位闭合，及三条可原样复跑的复核命令）。


## 2026-10-16 04:2x ｜ ⑩ 线长席 st-qoder-p10-1016-05（零解锁）

- 本班**零解锁**：恢复前置 ②未成（窗 [03:52:30,04:18:13] 全线 9 枚死袋，逐只 qid 见第十三单 §4②）、③未成（⑦A 定性材料未到手）⇒ 全线继续停发生产配额、零席 enable。
- ①成（两腿）单独记账＝托管正门修法在 HEAD（两笔 511b8e22c7/8f339c21c8）＋ghost 族内容级自 01:54:27 起新增 0 枚＋审计面 198 条全 custody_excused・dead=True 0；该腿单独成就**不构成**恢复条件，勿据此开席。
- 面级复位状态（不作解锁依据）＝①②③⑥席台账盘面仍落后落地面，本席不代复位，交清理专班／Owner 呈批。
