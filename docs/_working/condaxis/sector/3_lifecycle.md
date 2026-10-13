---
ttl: task_bound
title: 环节② 板块状态阶段——轮动五态/持续分/生命周期五态与活跃度档
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 该环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 环节② 板块状态/阶段（生命周期五态＋各态灰度）

> **目标形态**（研究册 §1.2②）：生命周期五态（点火/主升/分歧/退潮/调整）+ 各态灰度；消费=考试卡条件与卖出决策（接线后）。
> **外部对应**（研究册 §5）：Hawkes 高/低活跃期分态结论（arXiv:2512.08000）——"活跃度档"加为②的输入特征。

## §1 逐项台账表

| 件名 | 仓内真源路径:行号 | 现状标记 | 消费方 | 缺口 | 六向定位 |
|------|------------------|---------|--------|------|---------|
| sector_rotation_state（市场级轮动 5 态） | src/zephyr/signal_ashare/sector/sector_rotation_state.py:52-59（new；RotationState=CONSENSUS_CLIMAX/DISAGREEMENT_PULLBACK/HEALTHY_MAINLINE/DISTRIBUTION_RISK/NEUTRAL_MIXED，watch_score 5 值冻结） | 🔨 new 落码（纯函数） | mainline_candidates（①依赖）/ecology_judge（高潮分口径） | **市场级**轮动态≠单板块生命周期态——粒度错位：本件输出"市场处于哪种轮动格局"，②要的是"某板块处于哪一期" | ①turnover HHI ②①⑤环节 ③top_n_hhi+分类 ④已落 ⑤- ⑥sector_state 表在 |
| sector_momentum_persistence（板块级持续分） | src/zephyr/signal_ashare/sector/sector_momentum_persistence.py:7-8/:182-330（testing；五维=MPS 正收益日占比/资金子分(F3 口径 0.6 正流入占比+0.4 尾部连正)/梯队 CV/共振 ρ/恢复速度查表+market_breadth 二态 mainline≥0.6/speculative≤0.3） | 🔨 testing（SAFETY M；缺维重归一） | TDM-E-L2-08 已挂 | 五维是"持续性强弱"连续分，**不是五态离散标签**——②的"阶段"输出无现成件 | ①K线+资金+梯队 ②TDM-E-L2-08 ③加权五维 ④已落 ⑤- ⑥资金腿=sector_fund_flow 仅 29 日 |
| sector_detail_enricher（板块周期五态） | src/zephyr/signal_ashare/sector/sector_detail_enricher.py:7（testing；INVARIANTS 周期五态封闭=酝酿/启动/发弹/高潮/退潮+拉升原因五类封闭+状态机平滑） | 🔨 testing（GAP-F-17 行） | 板块详情页/报告 | 词表与目标五态（点火/主升/分歧/退潮/调整）**不同源**（发弹 vs 主升命名差、缺"调整"态） | ①板块详情输入 ②前端详情 ③状态机 ④已落 ⑤详情页 ⑥- |
| sector_adjustment（调整周期进度） | src/zephyr/signal_ashare/sector/sector_adjustment.py:6-10（new；progress∈[0,1] 纯函数） | 🔨 new | TDM-E-L2-03 | 进度单值≠"调整"态的进入/退出判定 | ①盘后截面 ②TDM-E-L2-03 ③- ④已落 ⑤- ⑥- |
| adjustment_cycle_tracker（调整周期跟踪） | src/zephyr/signal_ashare/adjustment_cycle_tracker.py:6（production） | ✅ | TDM-E-L2-03-1 已挂 | 与 sector_adjustment 分工须路由册写明（同名域两件） | ①-②TDM-E-L2-03-1 ③-④已落 ⑤- ⑥- |
| sector_state_aggregator（状态聚合纯函数） | src/zephyr/signal_ashare/sector/sector_state_aggregator.py:7-22（testing；22 号 spec 全公式级条目：momentum 0.4/0.3/0.3、RRG DualEma 10/26+2 日确认、强度=涨停比40%+梯队30%+趋势30%、5 态 4 维规则映射、preference tilt∈[0.8,1.2] frozen 考试卡 D2 预承诺） | 🔨 testing | sector_state_pipeline | **5 态 4 维规则映射**是仓内唯一成体系的板块态规则——但词表归属 22 号 spec，与 detail_enricher 五态两套并存 | ①CH 面板 ②pipeline/策略门 ③spec 公式级 ④已落 ⑤- ⑥sector_state 432k 行 |
| sector_state_pipeline（落库编排） | src/zephyr/data/sector_state_pipeline.py:6-18（testing；close_final T15:10 真源态/pre_open T+1 09:15 复制+偏好重映射） | 🔨 testing | daily_gate_snapshot L2 门三原料/plan_engine | **实查断更 1 交易日**：sector_state max=2026-10-09，10-12 缺（880 K 线有 10-12）——巡检移交项（00_skeleton §4-3） | ①CH 面板 ②L2 门 ③编排零算法 ④已落 ⑤- ⑥断更待修 |
| sentiment_cycle（情绪水温档真源） | src/zephyr/signal_ashare/sentiment/sentiment_cycle.py:6-13（new；PHASE_DISCIPLINE/STRATEGY_DEPLOYMENT_MATRIX 覆盖全 5 阶段） | 🔨 new | TDM-E-L2-05-1 已挂；G07/G08 | ②的"活跃度档"输入候选之一（Hawkes 结论落地口） | ①情绪序列 ②⑤环节/打板 ③5 阶段 ④已落 ⑤- ⑥- |
| 活跃度档特征件（Hawkes 输入） | ⬜ grep"活跃度档"零命中 | ⬜ | ② | 研究册 §5 明确动作"验证时把活跃度档加为②输入特征"——无件，验证班一并考 | ①-②-③-④⬜⑤-⑥- |
| 统一五态词表映射 | ⬜（三套五态并存见 §3-1，无映射件） | ⬜ | ②输出契约/考试卡 | **本环节核心缺口**：目标五态与仓内三套词表（rotation_state/persistence 连续分/detail_enricher）的映射不存在 | ①-②考试条件轴 ③-④⬜⑤-⑥- |

## §2 与既有资产边界

- **复用**：state_aggregator+pipeline（22 号 spec 体系，sector_state 表 432,208 行在产数据）为②的落库主干；persistence 五维连续分与 detail_enricher 五态作为**候选特征**全部复用进验证班。
- **换参**：detail_enricher 词表若验证班裁定为目标五态的近邻，走词表映射层换参（禁原地改其封闭词表——INVARIANTS 冻结）；persistence 权重与 breadth 二态阈值（mainline≥0.6/speculative≤0.3）按验证结果重标。
- **新建**：统一五态词表映射件（输出契约层）+活跃度档特征件两件；禁新建第三套板块态算法（state_aggregator 已是 spec 真源，内收判据同真源必并）。

## §3 施工要点

1. **三套五态词表不是同一物**（挖矿最大坑）：rotation_state=**市场级**（哪类轮动格局）、detail_enricher=**板块级**（酝酿/启动/发弹/高潮/退潮）、state_aggregator 的 5 态映射=**22 号 spec 规则**（另有 4 维规则）——施工统一映射前必须先做词表对齐表（对齐键=状态语义非状态名，镜像 state_vocabulary_registry 先例，formreg 册 §12.3-3 已立"预先给映射表防第 29 套词表"）。
2. **D2 预承诺阈值禁动**：state_aggregator 的 preference tilt∈[0.8,1.2] 头注明写"考试卡 D2 预承诺（改阈值=升版+重考）"——映射件施工禁顺手改。
3. **资金腿 29 日约束**：persistence 的资金子分（F3 口径）吃 sector_fund_flow，历史仅 2026-09-15 起 29 交易日且概念腿缺（1 号册 §1）——②验证班对资金维样本量不足，判据预冻结要给"资金维降级跑"的预案。
4. **断更修复先于验证**：sector_state 10-12 缺行会让 rolling 面板出现假跳变——pipeline 巡检修复是②施工前置。
5. **sector_state_pipeline 的 stage 契约**（close_final/pre_open 双时戳）是 PIT 关键：pre_open 行是 T 日复制——回测取数必须带 stage 过滤，禁两行混算（头注 INVARIANTS 明载）。

## §4 自审闸三态裁定

**裁定：施工**（与验证班同批启动、映射件先行）——理由：②是考试条件轴"板块态"字段唯一定义源，词表统一消灭"三套五态各说各话"的人工翻译环节；数据面齐（sector_state 43 万行），终局有位。活跃度档特征件与验证班同窗（其价值本就要靠 IC 裁定）。
