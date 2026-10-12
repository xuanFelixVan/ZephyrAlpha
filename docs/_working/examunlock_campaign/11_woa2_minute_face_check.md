---
ttl: task_bound
title: WO-A2 分钟面存在性核查（本班只核不拍，缺面=数据解锁呈批）
created: "2026-10-13"
sid: st-examunlock-20261013
family_id: EXAMUNLOCK-20261013
---

# 〇、本件的边界

令卡："WO-A2 分钟面存在性核查（原 P2d）：核查提速后呈批（缺面=数据解锁申请，禁代拍）"。
⇒ 本班只做存在性/覆盖真面的**在册读数**，不提数、不改采集、不代拍解锁。全部证据来自册面与代码面，
零 DB 查询（01:00-04:00 让路窗内亦零 CH，本班未发一条查询）。

# 一、工单要什么（逐字）

`docs/_working/mineloop_campaign/15_work_orders_engine_and_vocab.yaml:124-125`
`wo_a2_five_min_slicer: title: WO-A2 5 分钟执行切片器（单列，不与 A1 混收）`；
其 `precondition_data_probe` 自书两条前置：①"先查 TableRegistry 是否已有个股 5min/1min 品类
（已知 `market_etf_kline_1min/5min/30min` 在册）；若个股分钟面缺表＝〔先落 data-unlock，不得日频近似冒充分钟面〕"；
②"分钟表多版本行须先钉 anyLast/argMax 去重口径（在册 30 倍放大事故面）"。
被它 unblocks 的卡含 `TDM-X-S1-06/comparison/02_K3连续破位强清对照` 等（同件 :130 起逐条列）。

# 二、核查结果（本班自取，两本册交叉）

| 品类 id | 派生表 | 册面 enabled | 册面 valid_since | consumed_by_jobs |
|---|---|---|---|---|
| market_kline_1min | c1_market.kline_1min | true | 2021-09-01 | 空（资产册未记消费者） |
| market_kline_5min | c1_market.kline_5min | true | 2021-09-01 | 空 |
| market_kline_15/30/60min | c1_market.kline_15/30/60min | true | 未记 | 未记 |
| market_tick_depth_5 | c1_market.tick_depth_5 | true | 2026-10-01（册面带引号原样） | calendar_coverage_checker.py, qmt_bridge_provider.py |
| market_auction_snapshot | c1_market.auction_snapshot | true | 2026-08-01 | 空 |
| market_auction_book | c1_market.auction_book | **false** | 2026-07-01 | 空 |
| market_l2_tick | c1_market.l2_tick | **false** | 资产册内查无该表条目 | — |
| market_etf_kline_5min | c1_market.kline_etf_5min | true | 未记 | — |

出处=品类册 `docs/03_modules/_cross_layer/database/business_data_categories.yaml`（enabled/frequency 面）
＋资产册 `docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml`（valid_since 面）。
两本册对同一表可能不同步（本班只报各自面值，不合并成第三口径）。

# 三、结论（三条，不含建议拍板）

1. **工单前置①已被册面回答：个股分钟面不缺表。** 1/5/15/30/60min 全部 enabled=true，
   个股 1min/5min 的在册起始日=2021-09-01。
   在册另一条相关但未完成的动作（本班如实区分，不混为一条）：
   `docs/_working/mineloop_campaign/27_five_card_freeze_protocol.yaml` 在 needs_ch_after_window 段要求
   "kline_etf_1min 在场清单＋品种前缀归户……窗毕一条 SQL 出清单后写进卡面数据字典节（带版本日期）"——
   那是 **ETF 在场清单**的取数义务，不是"个股分钟面是否存在"的问题；本班核的是后者，结论见上。
2. **真实约束不是"有没有表"，而是"起始日 2021-09-01 与卡片窗不相容"。** 凡 IS 窗早于 2021-09-01 的
   执行切片卡（含 unblocks 清单里的卡），按 5min 面切片只能覆盖约 5 年，不能沿用日频卡的全窗；
   要么逐卡声明分钟窗（=新版本卡，G4-5），要么保持日频近似并如实标口径降级（工单明文禁"日频近似冒充分钟面"）。
   在册过期读数登记：`docs/_working/mineloop_campaign/99_checkpoint.md:218`
   仍写"ETF 5/15/30min 已在册，**个股面未证**"，与品类册现值（个股 1/5/15/30/60min 全 enabled=true）不一致——
   本班如实登记这条差异，不替属主班改他们的文档。
   （本班一度把这条也挂到 `27_five_card_freeze_protocol.yaml:25`，实跑 grep 该件"未证"零命中，
   属自家引用未过正对照，已删——留此一句记本班这次自纠。）
3. **两条面确实查无/禁用**：`auction_book` 与 `l2_tick` 在册 enabled=false；
   `tick_depth_5` 在册起始 2026-10-01（≈两周）⇒ 逐笔/集合竞价形命题的分母极小。
   这是**呈批面**（数据解锁＝Owner 门位"数据源"类），本班不代拍、不提采集变更。

# 四、若统筹要往下推，缺的不是核查而是这两件

- 甲：`consumed_by_jobs` 大面积为空 ⇒ "表在册但无人消费"与"消费了但没登记"两种情况无法区分；
  要判"能不能直接接进考试执行面"，须由数据车道做一次消费者回填普查（本班域外）。
- 乙：分钟面多版本去重口径（工单前置②）在 `card_binding` 现无分钟形算子，
  与 05 号判定册同一族缺口（A 路一日一值装不下分钟序列）——须面板/切片通道，属矿考域。
