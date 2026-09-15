---
ttl: task_bound
title: T1-α 节点挖矿：overlay 8 转换维度生产件（D-SIGNAL-68 Phase 2b/2c）
session: st-qoder-t1a-20260915
date: 2026-09-15
parent: S11_assembled_backtest
---

# 挖矿节点 5：overlay 8 转换维度生产件（D-SIGNAL-68 Phase 2b/2c）

> 挖矿日期：2026-09-15 ｜ 会话：st-qoder-t1a-20260915 ｜ 唯源骨架：S11_assembled_backtest/nodes/
> 挖矿依据：regime 节点 §5 第 3 件 + feature_pipeline_mining §4 第 1 子节点——TRANSITION_CONFIG
> 的 32 维度评分由谁生产、阈值是否经 A 股校准。产出=数据，采纳裁定归主力会话施工班。

## 1 现状盘点（逐条带 file:line 锚点）

### 1.1 两层架构（overlay_signals_builder.py 728 行 + overlay_features.py 1288 行全读）

- **builder 层**（OverlaySignalsConstructor）：预计算全序列 shift(1)+O(1) 切片（同 risk
  构造器模式）；32 维 key 与 TRANSITION_CONFIG 契约对齐（_TRANSITION_DIMS L95-126，含
  keys_or_gte 析取维 breadth_thrust）；_STUB_DIMS=∅（L134，全激活）；feature_builder 数据
  透传（_fb_call，mock 兼容降级）。
- **评分层**（overlay_features 纯函数）：S1 四维（vix_panic/correlation/liquidity/
  flash_recover）、S2 十三维（capitulation 衰减加权多过滤器 E9a/valuation 路A+路B/
  wyckoff 委托引擎/spring 三级 velocity/breadth_thrust Zweig/three_yang v2_index/NLP
  policy+bad_news_flat）、T1 三维/T2/T3 七维（Phase 2c 资金板块激活）/T4/T5/T6。
- **生产写方开关**：print_regime_history.py 默认 full+on+phase2c（节点 4 已核）。

### 1.2 数据源存活普查（CH 只读实测 2026-09-15）

| 源 | 表 | max date | 判 |
|----|----|----------|----|
| 主力资金流 | c1_market.money_flow | 2026-09-15（40.6 万行） | ✅ 活 |
| 板块 K 线 | market_sector_kline | 2026-09-15 | ✅ 活 |
| 新闻（NLP 源） | fund_news_data | 2026-09-15（790 万行） | ✅ 活 |
| 期权 IV（合成 VIX 源） | market_option_iv | 2026-09-15 | ✅ 活 |
| 指数估值（S2 路A） | index_valuation_daily | 2026-09-14 | ✅ 活 |
| 涨跌停统计 | market_limit_up_down | 活但**事件行制**（见 1.3） | ⚠️ |
| 广度涨跌家数 | kline_index 399106 adv/dec | **2026-07-02** | ❌ 断更 |
| 北向资金 | market_hk_connect_flow | **2024-08-16** | ❌ 停发 |

## 2 六向挖矿日志（信号 ✅ / 噪音 ✗ / 受阻 ⛔）

| # | 方向 | 判 | 发现（file:line） |
|---|------|----|------------------|
| 1 | F4 死源下游全图 | ✅ P0 | **四连杀全图**（CH 实测扩展）：399106 adv/dec 断更 → ①HMM F4 恒 0；②RiskSignal #7 恒 1.0；③**T3 sentiment 恒 0**（builder L442-445 吃 ad_ratio）；④**S2 breadth_thrust 恒 0**（L386-390 同源，confirm 析取通路之一）。且 breadth_thrust 的 A 股校准闭环 docstring 自认依赖 399106（overlay_features.py:836-837"§4.5 验证闭环 Step 0 ③"）——**修复 FPB-1 是校准闭环的前置** |
| 2 | 连板/晋级率算法 | ✅ P1 | **虚增实锤**：_compute_limit_up_metrics（builder L696-725）run_group=(x==0).cumsum 假设每 symbol 每交易日有行；CH 实测真表也是**事件行制**（2026-09-12 仅 61 行，limit_type 值域仅{涨停,跌停}，无全市场逐日行）→ 连板数跨无事件日累加（3 月涨停+4 月涨停=记 2 连板）、promotion_rate 按"上一涨停日"而非"上一交易日"算。T3 leader 维度系统性虚高 → trigger leader>=60 假触发概率增大。derived fallback 同款（regime_data_loader.py:402-443 只产事件行） |
| 3 | 北向资金存活性 | ✅ P1 | **静默退役**：hk_connect_flow 止于 2024-08-16（交易所停发实时披露，4052 行）。消费端（builder L636-649）reindex 到 feat.index 全 NaN → hk_adj fillna(0) → 融合项加 0 不报错——P1-E5 北向融合设计自 2024-08 起名存实亡；"主力资金缺失时北向弱代理"后备路径同死。无日志、无披露 |
| 4 | 阈值 A 股校准缺口 | ✅ P1 | **欠账名册**（docstring 自认"待 §4.5 校准闭环"但闭环从未跑）：①breadth_thrust 0.615/0.40=NYSE 原值（L836-837 自认）；②capitulation confirm 档 halflife=30/lookback=40 占位（L256-258 自认）；③s1_vix_panic/s2_vix 阈值族继承 vol_pct 分布语义，但生产优先注入合成 VIX（下行半偏差分位，分布不同）同阈值套用（L105-121）；④t3_money_effect 涨停家数阈值 >100/50/30（L1034-1038）无 A 股分年代留痕；⑤t3_mainline HHI>0.08/0.10/0.15（L1067-1071）依赖板块分类法版本（板块数变 HHI 基线变）无留痕。正面对照：capitulation 组合 2026-08-29 走过预注册 walk-forward（WFE 3.44/MC p=0.87 未过已注记，L338-339）——唯一跑过闭环的维度 |
| 5 | T5 leader_break 语义 | ✅ P2 | **指数冒充领涨股**：docstring 自认"MVP 用市场代理代替领涨股"（L1169-1170）——T5 逃顶转换 trigger（leader_break>=60）实际=000300 跌破 MA20+放量。语义错位：指数破位≠龙头股破位，且常态可能反向（牛市回调即触发）。spec §4 若承诺"领涨股"则为文档失真 |
| 6 | mainline HHI 口径 | ✅ P3 | HHI 用 \|ret\|（含下跌板块贡献集中度）与"涨幅集中度"语义不符（builder L304-309 同款两处：risk #8 siphon + T3 mainline）——下跌日 HHI 也升高，可能与"主线确立"语义反向 |
| 7 | PIT/契约守护 | ✗ | 32 维末尾统一 shift(1)（L502-504）；_eval_stage 缺 key 计 0 语义与 _TRANSITION_DIMS 全 key 填充对齐（L93-95 注释）；噪音（纪律良好） |
| 8 | 合成 VIX 双路径 | ✗ | 期权 IV 优先/下行半偏差后备（L565-613），per-element NaN 回退 vol_pct 设计周全； CH 期权数据活到 2026-09-15——噪音（健康） |

## 3 业界对照（四门）

| 项 | 本仓 | 业界 | 判 |
|----|------|------|----|
| Zweig breadth thrust | 10 日 EMA 0.40→0.615，NY 原值 | 美股 NYSE 标准参数；A 股涨跌停制+IPO 节奏下需本土化 | ⚠️ 未校准（自认） |
| Wyckoff 6 阶段 FSM | wyckoff_engine 委托+MVP 回退 | 经典框架，spring velocity 分级属现代改良 | ✅ 来源可溯 |
| capitulation 过程化 | 衰减加权/簇计数+预注册组合 | 业界前沿做法（过程信号防粘滞），MC 检验诚实 | ✅ 可回测 |
| 连板/晋级率 | 事件行制上 cumsum | A 股情绪周期标准指标（淘股吧/开盘啦口径=按交易日） | ❌ 实现与业界口径不符（虚增） |
| 北向资金 | 2024-08 后静默加 0 | 业界普遍显式弃用或换盘后口径（CLH 持仓披露） | ❌ 无披露退役 |

## 4 堵点清单（按优先级，含验收）

| id | 优先 | 堵点 | 验收 |
|----|------|------|------|
| OVB-1 | P0 | 广度死源四连杀（同 FPB-1，本节点补全下游清单）；修复后须补跑 breadth_thrust A 股校准闭环 | FPB-1 验收 + 0.58-0.65 区间扫描出本土化阈值+walk-forward 报告 |
| OVB-2 | P1 | 连板/晋级率事件行虚增 | _compute_limit_up_metrics 先按全交易日历 reindex（事件缺失日 is_up=0）再算 run_group/promotion；验收=抽样 5 只已知连板股对照真值（±0 误差） |
| OVB-3 | P1 | 北向停发静默退役 | 二选一：显式退役（删融合逻辑+spec 披露）或换盘后口径数据源（如 CLH 季度/盘后额度）；短期至少加"hk 新鲜度>5 交易日断更"进 FPB-1 同款巡检 |
| OVB-4 | P1 | 阈值校准欠账台账（§2#4 五项） | 统一登记 §4.5 校准闭环 backlog（预注册纪律同 capitulation）；每项验收=walk-forward 报告或显式降格披露 |
| OVB-5 | P2 | T5 leader_break 指数冒充 | 二选一：接真实领涨股池（连板股/涨幅榜，数据在 limit_up_down/kline_daily）或 spec+docstring 降格为"指数破位"并评估对 T5 trigger 行为的影响 |

## 5 子节点清单

| 节点 | 为什么值得挖 | 入口 |
|------|-------------|------|
| wyckoff_engine 6 阶段 FSM | 178 行小件，Spring+40 是 S2 关键转折分，从未深挖 | src/zephyr/regime/features/wyckoff_engine.py |
| synthetic_vix 合成 VIX | 179 行，CBOE 简化 VIX+下行半偏差双实现，vix_panic/vix 两维的分布根基 | src/zephyr/regime/features/synthetic_vix.py |
| chip_distribution_engine 转正 | 同 feature 节点 §4（#12 现成件） | 已登记，不重复 |

## 6 封矿判定

- **本节点主体封批**：builder+评分两层全读；CH 四路实测（事件行制/北向停发/五源存活/
  广度断更扩展）把 3 个 P1 从推断升实锤；阈值欠账名册 5 项 concrete 到 docstring 行号。
- **未枯竭部分转子节点**（§5 两小件）：wyckoff_engine + synthetic_vix（合计 357 行，
  可合并一节点扫尾）。
- 一句话结论：**overlay 层的"方法论纪律"是全仓标杆（预注册/MC 检验/回源核对/诚实注记
  应有尽有），但"数据卫生纪律"塌方——事件行制算连板、北向停发加零、NYSE 阈值裸奔、
  校准闭环"待跑"挂账，四类问题同根：评分函数假设数据存在且语义对，没人验过假设。**
