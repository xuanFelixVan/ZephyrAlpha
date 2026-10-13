---
ttl: task_bound
title: 环节✦ 验证班开班矿——板块模块普查台账与判据预冻结清单草案
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 该环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 环节✦ 验证班开班矿（20+ 模块普查台账＋判据预冻结清单草案）

> **令据**：研究册 §0-3"最优先动作=开板块信号验证班（判据预冻结→对在册 20+ 板块模块统一打靶）→按内收原则退役零增量模块"；附录 A 草案的挖矿落地。
> **纪律**：本册只立判据草案与普查台账，零开考（判据零自拟=先冻结后跑数）；闭卷考试=最终考试（mining SOP 头注 Owner 永久原则 2026-10-12 裁定②）。

## §1 逐项台账表（普查：逐件实读头注 MATURITY/INVARIANTS，2026-10-13）

### A 块·sector/ 信号族（17 件）

| 件名 | 真源:行号(MATURITY 行) | 标记 | 能复用什么 | 缺什么 | 可考性 |
|------|------------------------|------|-----------|--------|--------|
| sector_analyzer | sector/sector_analyzer.py:7 production/stable | ✅ | 强度分 [0,100]+连板梯队+趋势（TDM 双挂 L2-01-1/02-2） | - | A（分值连续输出） |
| sector_crowding_launch | sector/sector_crowding_launch.py:8 production/evolving M | ✅ | 拥挤三态+启动状态机（4 号册 T-5/T-7） | 过热阈值>90% 无回测证据 | A（状态机确定性） |
| sector_state_aggregator | sector/sector_state_aggregator.py:7 testing | 🔨 | 22 号 spec 公式级全域+D2 预承诺阈值 | 偏好映射阈值待考 | A（纯函数+frozen） |
| sector_momentum_persistence | sector/sector_momentum_persistence.py:8 testing M | 🔨 | 五维持续分+breadth 二态 | 资金腿 29 日窗 | A（MPS 连续分） |
| sector_leader | sector/sector_leader.py:7 testing | 🔨 | 四档梯队+连板高度推算口径 | 涨停幅度列缺口实证（pct_change 2026-08-22 全 0） | A（四档封闭） |
| sector_divergence | sector/sector_divergence.py:7 testing | 🔨 | 轮动序列+条件频率（不预测纪律自带） | 方向判据=禁（44 号原文） | A（velocity/overlap 连续） |
| sector_detail_enricher | sector/sector_detail_enricher.py:7 testing | 🔨 | 周期五态+拉升原因五类封闭 | 证据超窗仅 window_notes 留痕 | B（描述性为主） |
| sector_attribute_rules | sector/sector_attribute_rules.py:7 testing | 🔨 | 属性四态封闭（攻/守/衡/未标）规则自上而下 | 纯标注件无收益判据 | B（属性标签） |
| sector_volume_anomaly | sector/sector_volume_anomaly.py:7 testing | 🔨 | 偏倍度五档+PIT 严格 | 单股异常不稀释=板块聚合口径 | A（z-score） |
| sector_adjustment | sector/sector_adjustment.py:6 new | 🔨 | 调整进度 [0,1] 纯函数 | 进入/退出判定 | A |
| sector_breadth | sector/sector_breadth.py:7 new | 🔨 | 涨停比/资金分（L2-01-4 挂） | - | A |
| sector_gate | sector/sector_gate.py:7 new | 🔨 | 三级门槛+水温表（5 号册） | 上游归并表 | A（查表映射） |
| sector_momentum | sector/sector_momentum.py:7 new | 🔨 | 多周期动量 q 分位（L2-01-3） | - | A |
| sector_pullback | sector/sector_pullback.py:6 new | 🔨 | fib 回撤+ABC grade | - | A |
| sector_rotation_state | sector/sector_rotation_state.py:6 new | 🔨 | 市场 5 态+watch_score | 粒度错位（3 号册） | A |
| sector_rrg | sector/sector_rrg.py:7 new | 🔨 | JdK DualEma 10/26+象限确认 | 最小 62 日窗 | A（象限封闭） |
| sector_siphon | sector/sector_siphon.py:7 new | 🔨 | hhi+outflow_ratio | 资金腿 29 日窗 | A |

### B 块·core/ 与上层（8 件）

| 件名 | 真源:行号 | 标记 | 能复用什么 | 缺什么 | 可考性 |
|------|-----------|------|-----------|--------|--------|
| sector_strength_wiring | core/sector_strength_wiring.py:6 production | ✅ | 四维 rank 归一接线+日频 JSON 通道 | 高潮分代理 proposed | A |
| sector_strength_aggregator | core/sector_strength_aggregator.py:15 design | 🔨 | 四路合分核+Top-15% | 等权先验待 IC 重加权（7 号册主靶） | A |
| sector_ecology_judge | core/sector_ecology_judge.py:15 design | 🔨 | 三态封闭+阈值取自锚定文档 | 待接线（L3-06） | A |
| sector_conduction | core/sector_conduction.py:15 design | 🔨 | 锚点乘数 [0.90,1.15] | 时滞×位置排序 | B（乘数语义=打分调整非预测） |
| mainline_candidates | mainline_candidates.py:12 testing | 🔨 | 三维计分+空榜纪律 | 梯队标签 | A（候选榜命中率可考） |
| mainline_probability | mainline_probability.py:12 testing | 🔨 | 四因子+动态权重接口位 | 权重初拍零 IC；fund 因子口径混用（2 号册） | A（相对评分 vs 后验主线） |
| strength_ic_data_assembler | strength_ic_data_assembler.py:12 testing | 🔨 | 60 日滚动 IC 装配 | 未对板块面跑过 | A（工具件） |
| strength_ic_weight_calibrator | strength_ic_weight_calibrator.py:12 new | 🔨 | 滚动 IC 权重+回退经验权重 | 同上 | A（工具件） |

### C 块·数据底座（9 件）

| 件名 | 真源:行号 | 标记 | 复用 | 缺 | 可考性 |
|------|-----------|------|------|-----|--------|
| sector_snapshot_collector | data/sector_snapshot_collector.py:7 production | ✅ | 880 快照采集（99 推送+30s 轮询） | 无资金字段 | 基建 |
| sector_intraday_aggregator | data/sector_intraday_aggregator.py:7 production | ✅ | 582 板块盘中聚合 | 资金腿=成交额代理 | 基建 |
| sector_report_builder | data/sector_report_builder.py:7 production | ✅ | 盘后全景报告（观测只读 B-007） | - | 基建（报告非判据） |
| sector_kline_downloader | data/sector_kline_downloader.py:7 production | ✅ | 880 日线 1d/1m/5m | - | 基建 |
| sector_ranking_engine | data/sector_ranking_engine.py:7 production | ✅ | 5 因子推送池排名 | - | A（排名 vs 后验） |
| sector_state_pipeline | data/sector_state_pipeline.py:7 testing | 🔨 | close_final/pre_open 双 stage | 10-12 断更（1 号册） | 基建 |
| sector_factor_manager | data/sector_factor_manager.py:7 testing | 🔨 | 86 板块因子纯函数 | 因子→验证班接入位 | A |
| sector_fund_flow_collector | data/implementations/sector_fund_flow_collector.py:7 testing | 🔨 | THS 即时资金流（industry 腿在产） | concept 腿接线+29 日窗 | 基建（数据腿） |
| sector_code_bridge | data/implementations/sector_code_bridge.py:7 testing | ✅ | THS881↔TDX880 90/90 映射 | - | 基建 |

### D 块·TDM 挂件与支持族（14 件精选）

| 件名 | 真源:行号 | 标记 | 复用 | 缺 | 可考性 |
|------|-----------|------|------|-----|--------|
| adjustment_cycle_tracker | signal_ashare/adjustment_cycle_tracker.py:6 production | ✅ | 调整周期（L2-03-1） | 与 sector_adjustment 分工 | A |
| market_forecast_fusion | regime/market_forecast_fusion.py:6 production | ✅ | 市场级调节分（L2-01-5） | - | A |
| supply_chain_momentum | signal_ashare/supply_chain_momentum.py:6 production | ✅ | 链上动量补涨（L2-10） | - | A |
| event_driven_screener | signal_ashare/screening/event_driven_screener.py:6 production | ✅ | 事件驱动筛选（L2-09） | 方向语义（5 号册） | A |
| sector_rotation_criterion | signal_ashare/source_line/sector_rotation_criterion.py:9 design | 🔨 | 源线 RS 分位（L9-A03） | - | A（源线判据口径） |
| sector_rotation_score_mapping | signal_fundamental/sector_rotation_score_mapping.py:12 new | 🔨 | 象限→score 映射 | 待 G06 定型 | B（映射件） |
| position_sector_context | signal_ashare/position_sector_context.py:12 testing | 🔨 | 持仓板块语境 | 观测先行纪律 | B（语境非判据） |
| sentiment_cycle | sentiment/sentiment_cycle.py:12 new | 🔨 | 5 阶段+部署矩阵 | - | A |
| sentiment_cycle_evaluator | sentiment/sentiment_cycle_evaluator.py:12 testing | 🔨 | **定位器准确率评估件（验证班现成工具）** | - | A |
| limit_up_ecosystem_leadership | limit_up/limit_up_ecosystem_leadership.py:6 testing | 🔨 | 梯队断层/晋级率/Granger 领导 | - | A |
| youzi_relay_emotion_engine | limit_up/youzi_relay_emotion_engine.py:4 production/stable | ✅ | 6 因子情绪+4+1 阶段 | - | A |
| industry_chain_graph | signal_ashare/industry_chain_graph.py:8 production | ✅(库件) | BFS 乘积衰减算法 | 零生产实例化（5 号册） | 算法件 |
| chain 三件套 W3/W4/W5 | intelligence/news_chain_node_linker.py:12 / chain_impact_resolver.py:12 / chain_impact_stream.py:12（均 testing） | 🔨 | 新闻→环节→标的→盘中流 | 方向语义 | A（命中定位可考；方向禁考红线） |
| event_chain_causal_graph | intelligence/event_chain_causal_graph.py:8 production | ✅ | 事件 Granger+贝叶斯条件概率 | - | A |

**普查汇总**：45 件（A 块 17+B 块 8+C 块 9+D 块 14，含库件/工具件）；成熟度分布 production 17／testing 17／new 8／design 4／experimental 1（emotion_index_builder 未入核心普查）——**断层实证**：测试/新码占 25/45≈56%，production 件集中在数据底座与执行邻域，信号件仅 crowding/analyzer 两件到产。可考性分级：**A 可回测 36 件／B 半可考 5 件（detail_enricher/attribute_rules/conduction/score_mapping/position_context）／数据面阻塞=资金腿类信号受 29 日窗约束**。

## §2 与既有资产边界（复用/换参/新建三分）

- **复用**：sixphase-v1 冻结五要素先例（PHASE_VERSION 版本化禁原地改/CLOSED_BOOK_CUTOFF/PIT_TAIL_LAG=1/warmup 700/重放幂等，2026-10-12-d-family-qualification-freeze-draft.md:46）；n_trial_ledger（src/zephyr/backtest/core/n_trial_ledger.py run_card 钩子）；IC 校准两件（B 块）直接当验证班工具；sentiment_cycle_evaluator=定位器评估现成范式；mining SOP §8.5 三本账（试次 t≥3.0/增量对族残差化/复制出生四件）。
- **换参**：sixphase warmup 700 日→板块面 62 日（RRG 最小窗）；CLOSED_BOOK_CUTOFF 2025-09-09→板块面样本期切点另定（见 §3-1）。
- **新建**：判据预冻结清单册（本册 §3 草案的正式化）+板块面板装配件（考试数据面：sector_state 432,208 行+880 K 线 766,114 行现成，缺统一面板视图）。

## §3 判据预冻结清单草案（看数前冻结，六组）

1. **样本期与数据腿版本**：主样本期=tqcenter 腿 2026-06-17~今（连续新鲜）；全史参考段=tdx 腿 2025-07-18~2026-07-31（禁与主段拼接混考，1 号册断代坑）；资金腿=2026-09-15 起 29 交易日→**资金维信号设最短历史门槛（建议 ≥60 交易日才入考，不足=降级剔除不判负）**；宇宙=880 族 729 码（880001-880009 市场统计指数剔除）。
2. **PIT 规则**：PIT_TAIL_LAG=1（sixphase 先例）；sector_state 取数必须带 stage 过滤（close_final 真源态，禁 pre_open 复制行混算，3 号册 §3-5）；成分股 SCD-2 时点过滤（各件 INVARIANTS 已内置，面板装配件统一执行）；kline_sector 强制 data_source 过滤。
3. **前瞻窗口**：20 日远期收益 rank IC 主口径＋60 日确认双口径（研究册附录 A）；隔夜/日内双腿拆列（mining §8.5.3 模板 A 纪律——板块面同理防"只在一边赚"）。
4. **多重比较校正**：显著性门槛 t≥3.0 起步随 total_tests 上调（HLZ2016）；信号池规模→通过门槛关系**先冻结**（本册普查 A 级 36 件×前置窗口×阈值变体=试次总账基数，开考前登记）；N_eff 双口径披露（raw+effective）；增量账=对在册板块因子族（sector_factor_manager 86 因子为族基座）残差化取增量 IC，禁孤立显著入池。
5. **验收线与样本量现实**：板块拐点事件=百级样本→置信区间口径而非点估计；主线判定后验基准=候选榜命中率（top_k=5 vs 次日/20 日后主线归属）需先冻结"主线后验定义"（建议：20 日窗口内板块累计超额 Top3 且 lead_streak≥2——**此条为草案，开班呈批**）。
6. **红线三则**：热度传导预测禁复辟（IC=-0.029，ACC-F-CHAINMAP-CATALYST.yaml:25）；D109 先产特征不联动仓位（验证班全部输出=特征态，禁接扳机）；闭卷考试=最终考试（账面折减不替代考试）。

## §4 自审闸三态裁定

**裁定：施工**（板块线第一优先级）——理由：验证班消灭的是"40+ 件信号哪个真的有用"这一当前最大人工盲区，且是①②③④施工的统一前置（权重重加权/词表裁定/信号退役全等它的产出）；判据工具面 80% 是仓内先例复用（sixphase/n_trial_ledger/IC 件），施工量集中在判据册正式化+面板装配两件。反问封矿三理由不成立（终局必考、无既有件全覆盖、成本=两件）。**挂起项**：分析师预期因子入考（💰数据未采，解锁=Owner 采购裁定）；分钟面信号入考（🌑解锁=数据外购或降级日频代理裁定）。
