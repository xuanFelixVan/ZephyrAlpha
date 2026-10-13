---
ttl: task_bound
title: 环节① 主线名单梯队——强度合分与主线候选/概率逐件挖
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 该环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 环节① 主线名单与梯队（逐件挖：算法/输入表/成熟度/缺口）

> **目标形态**（研究册 §1.2①）：主线 Top-N（1-3）+ 次线/潜线/补涨梯队标签 + 灰度合分。
> **外部对应**（研究册 §5）：Moskowitz-Grinblatt 行业动量；免梯度在线集成（arXiv:2304.09947，合分不成再换的候选）。

## §1 逐项台账表

| 件名 | 仓内真源路径:行号 | 现状标记 | 消费方 | 缺口 | 六向定位 |
|------|------------------|---------|--------|------|---------|
| sector_strength_aggregator（MOD-SIG-142 四路合分） | src/zephyr/signal_ashare/core/sector_strength_aggregator.py:6-19（design；INVARIANTS 四路等权 0.25×4 最大熵、market delta±10 clamp、Top-15%≥1） | 🔨 design 已落码（研究册核验更正#2：在 core/ 非 sector/） | TDM-E-L2-01；L2-06 强度调节、L3 候选池（头注 CONSUMERS，待接线） | 权重=等权先验"待 IC 数据重加权"（头注自认）；四路子分产线只有 2/4 在产（下两行） | ①analyzer/ranking/momentum/breadth 四子分+forecast_fusion ②TDM-E-L2-01/L3 ③纯函数合成 ④已落码 ⑤IDX-02 待接 ⑥子分表齐 |
| └ 四子分产线现状 | sector_analyzer.py:7(production)/sector_ranking_engine.py:8(production,5因子)/sector_momentum.py:7(new)/sector_breadth.py:7(new) | ✅✅🔨🔨 | strength_wiring | momentum/breadth 两路 new 未结案 | ①-②-③-④-⑤-⑥- |
| sector_strength_wiring（MOD-SIG-144 接线层） | src/zephyr/signal_ashare/core/sector_strength_wiring.py:6-19（production；四维跨截面百分位归一 rank-based、缺维剔除） | ✅ 头注 production；消费 sector_report_builder 日频 JSON | TDM-E-L2-01/L2-04 生产接线、IDX-02 | 高潮分代理=涨停比分档映射（proposed 未考） | ①report_builder ②TDM ③rank 归一 ④已落 ⑤IDX-02 ⑥齐 |
| mainline_candidates（MOD-SIG-061 候选榜） | src/zephyr/signal_ashare/mainline_candidates.py:6-16/:22-32（testing；三维计分：当日涨幅居首+1/q3 前排+1/RRG 领先或改善+1，score≥2 入榜，top_k=5） | 🔨 testing 落码+依赖三件 import 消费（rotation_state/momentum/rrg） | sector_report_builder 主线维度；远期 IDX-02 D-06 | 无主线混沌空榜逻辑已有；**但无梯队分层标签**（次线/潜线/补涨三类标签不存在，grep 零命中⬜） | ①880K线+成分 ②报告/前端 ③计分制 ④已落 ⑤待接 ⑥齐 |
| mainline_probability（MOD-SIG-064 四因子概率） | src/zephyr/signal_ashare/mainline_probability.py:6-16/:112-124/:260（testing；四因子=rrg/relay(连板梯队)/fund(资金)/echelon(梯队完备)，静态权重"初拍值待实盘标定"，weight_overrides 动态接口位，top_k=10） | 🔨 testing | position_sector_context（MOD-SIG-065）；板块 Top10 页 | 权重零 IC 证据；fund 因子吃 money_flow（个股聚合口径，非板块资金流表——口径混用风险） | ①candidates/leader+money_flow ②持仓语境/前端 ③启发式合成 ④已落 ⑤Top10 页 ⑥money_flow 在、sector_fund_flow 概念腿缺 |
| strength_ic_data_assembler（IC 装配） | src/zephyr/signal_ashare/strength_ic_data_assembler.py:6-14（testing；60 日滚动窗、n_ret==n_dim 对齐） | 🔨 落码 | strength_ic_weight_calibrator | 板块级强度四路的 IC 装配未跑（先例是个股强度维度） | ①强度面板 ②calibrator ③纯函数 ④已落 ⑤- ⑥历史=sector_state 432k 行可用 |
| strength_ic_weight_calibrator（IC 校准） | src/zephyr/signal_ashare/strength_ic_weight_calibrator.py:7-13（new；Σ=1、IC 全无效回退经验权重） | 🔨 new | 待 G08 接 quant_short_term_strength_engine | 同上——**仓内已有 IC 校准先例但从未对板块面跑过** | ①-②-③-④已落 ⑤- ⑥- |
| market_forecast_fusion（市场级调节分） | src/zephyr/regime/market_forecast_fusion.py:6(production) | ✅ | TDM-E-L2-01-5（地图已挂） | - | ①regime ②强度合分 delta ③- ④已落 ⑤- ⑥- |
| 梯队标签件（次线/潜线/补涨） | ⬜ grep 零命中（"次线\|潜线\|补涨梯队"模块级零命中；仅 TDM-E-L2-10 补涨比价挂 supply_chain_momentum） | ⬜ | ①输出物契约 | **目标形态的梯队分层无件**——现只有"候选榜 Top5+概率 Top10"两层，无四层梯队 | ①-②-③-④⬜⑤-⑥- |
| 在线集成排序器（外部候选） | 仓外（arXiv:2304.09947） | ⬜ 班外 | ① 兜底 | 研究册 §5：合分不成再换；不预建 | ①-②-③-④⬜⑤-⑥- |
| 分析师预期修正（买方第一大输入） | ⬜ 仓内空白（研究册 §6.2 呈 Owner） | 💰 | ① 期望共振因子 | 花钱门位：Choice/朝阳永续/恒生聚源/tushare | ①-②-③-④⬜⑤-⑥⬜ |

## §2 与既有资产边界

- **复用**：strength_aggregator（design 核）+wiring（production 适配）+candidates/probability（testing）四件骨架全部复用；IC 校准两件复用为验证班工具（7 号册同录）；rotation_state/momentum/rrg 三依赖原样。
- **换参**：probability 四因子权重从"初拍"换 IC 数据重加权（头注已留 weight_overrides 接口位——**接口在、数据线没跑**）；candidates top_k=5 与①契约"Top1-3+梯队"的差=换参可解一半。
- **新建**：梯队分层标签件（次线/潜线/补涨）=①契约的真缺口；禁新建平行强度分（内收判据：同真源可派生→必并，aggregator 已是合分唯一真源）。

## §3 施工要点

1. **概率件 fund 因子口径混用**：mainline_probability 走 c1_market.money_flow（个股级聚合），而板块级专用表 sector_fund_flow 已存在（行业腿 29 日）——施工时统一到板块口径需先等资金流历史积累（7 号册判据约束），短期保留 money_flow 聚合口径须在路由册登记。
2. **"Top-N=1-3"与现状 Top5/Top10 的契约差**：candidates top_k 与 probability top_k 语义不同（候选 vs 展示），施工时在输出契约层裁剪，禁改两件默认值（消费方 report_builder/前端在用）。
3. **等权=最大熵默认的理由要保住**：strength_aggregator 头注明写"量化社区无 IC 证据时的标准起步"——验证班跑出板块级 IC 前禁手工调权（预冻结纪律，7 号册）。
4. **lead_streak<2 空榜是纪律不是 bug**：两件都有"无主线混沌→空榜+注解不强行出分"（candidates/probability INVARIANTS）——梯队标签件施工必须继承该纪律，混沌日不出四层梯队。
5. **补涨腿已有挂点**：TDM-E-L2-10 补涨比价挂 supply_chain_momentum（production）——梯队标签的"补涨"档应消费它，不重造。

## §4 自审闸三态裁定

**裁定：施工**（验证班之后第二批）——理由：①是五件套的头部产物且骨架 80% 在码（四件复用+两件换参），缺的梯队标签件消灭"Owner 盘后人工分层"参与，终局有位。时序上排在 7 号册验证班之后：权重重加权依赖 IC 结果，先施工会返工（mining §6 世界地图完备优先）。
