---
asset_id: "DOC:docs/_working/ultimate_library/ulib3b_to_derive_candidates.md"
ttl: "task_bound"
---

# 待推导清单（G15-② potential_consumers 增枝前置挖矿·产出三件/三件）

- 班次：st-ulib3b-20260922（增补令 #14③：文档无据、需强模型推导的供数关系）
- 口径：三路摘抄代理一致报告"明文未载"的推断候选；**本册只登记推导方向不做断言**——逐条需回到代码/表实探后方可入 potential_consumers 回填批
- 定稿：st-ulib3b 强模型（增补令 #14"审编定稿必须本班强模型"）

## 一、battle_map 抽象类 → 具体表映射（表级绑定全靠推断）

| # | 推断方向 | 依据 | 推导所需实探 |
|---|---|---|---|
| T1 | BM-SEL-22-C/23-A/24-A 系列消费的"L0 涨停数据"→limit_up_pool（含 industry 列）；"L0 盘口"→tick_depth_5；"L0 集合竞价"→auction_snapshot/auction_book；"L0 资金流向"→money_flow | battle_map_05:2731-3259 用抽象类；data.md 有上述表但从未被点名 | 代码消费面 grep：这些模块实读哪张 CH 表 |
| T2 | 做T 分时因子（量比/CVD/VPIN）的 C-009 管线原料→tick_data/kline_1min/l2_tick 之一或组合 | battle_map_07:487 说消费 C-009 产出，C-009 吃什么全图无载 | C-009 管线代码上游 |
| T3 | "全球市场数据（L0）"（BM-SEL-06 跨市场传导）→kline_global/us_index/hk_kline 子集 | battle_map_05:753 | 模块实读面 |
| T4 | 系统性风险五信号的"融资余额/政策新闻/外围指数"→margin_trading/news_data/us_index | battle_map_09:1214 | 风控模块实读面 |
| T5 | "A 股风险日历（D-DATA）"→calendar_event/ipo_schedule/index_adjustment 候选 | battle_map_08:218 | 日历模块 |

## 二、资产闲置嫌疑（表在库、疑似有用途无人接线）

| # | 推断方向 | 依据 |
|---|---|---|
| T6 | sentiment_panel（25 行无持久化史）疑似 BM-SEL-03-A"市场情绪指标"的断链供表 | battle_map_05:2005 + 情绪线盘点册 :113（币圈恐贪禁顶替 A 股） |
| T7 | c1_backtest.decision_daily/regime_state_anchored/sim_daily_report 与 BM03/BM04 域高度相关但 battle_map 从未点名 | data.md 表目录 vs battle_map 全文 |
| T8 | pipeline.md 任务名暗示链：ZephyrAlpha_TickSubscriber→tick 入库、SectorSnapshot→sector_snapshot、BoardIndexRealtime→board_index_tick、counter_trend_feeder→逆势馈送——任务→表→消费方完整明文链不存在 | docs/library/pipeline.md:20-91 任务名 |
| T9 | 券商结算单（BM-REC-01 消费）与关联账户合并数据（BM-BUY-15 合规）无对应表资产——是缺口还是散落数据待认 | battle_map_11:126 + data.md 322 表反查 |
| T10 | factor_analysis 11 表高密度互引是否构成 factor.value_factor/momentum_20d 的下游消费线 | 63 号 CSV 计数无方向；需查代码 |
| T11 | 63 号 CSV（2026-08-24）与 09-22 实库探针口径差异：zero_ref 的 fundamental 5 表 vs c3_fundamental.daily_valuation/analyst_forecast"在库有货"——命名空间是否同一套 | 两文对读无对齐声明；需一次表名映射核验 |
| T12 | 情绪线 C5 杠杆成分与板块线"杠杆资金分布"共用 margin_trading——两线是否同源共享未见声明 | 两侧台账各自引用同表 |

## 三、推导批处置建议

- T1-T5 为 potential_consumers 首批回填的最大宗来源（battle_map 75 条供给关系里约六成卡在"抽象类→表名"这最后一公里）；建议下一班用"模块实读面 grep"一次跑完，机械可证
- T6-T8 为闲置资产复活线索，回填时标 derived=true + 推导依据路径
- T9-T12 为口径对齐项，宜并入数据面班对账而非本维度
