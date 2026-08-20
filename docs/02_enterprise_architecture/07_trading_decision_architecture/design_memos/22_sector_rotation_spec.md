---
ttl: permanent
doc_type: architecture_view
title: 板块轮动 spec
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.9.7"
date: 2026-08-15
topic: sector_rotation_spec
scope: 07_trading_decision_architecture
---

> ## 结案报告（AI-NIGHT-001 复核 2026-08-19）
>
> **实际开发**：采集层全部 production 实证——sector_snapshot_collector（582 只 880xxx/881xxx 快照）+ sector_kline_downloader（market_kline_sector_880 schema 实证）+ sector_ranking_engine（5 因子 Top99 推送池）+ sector_analyzer（MOD-SIG-026 六方法 evaluate_strength/judge_continuity/warn_rotation/evaluate_launch_conditions/adapt_market_style/detect_breakdown 落码实证）+ sector_constituent SCD-2 + money_flow 五层净流入。
>
> **最终成果**：板块轮动 spec 定稿（active v1.9.7）——11 项讨论要点逐项裁定并公式级补全（RRG DualEma 10/26、q3/q5/q20 加权、5 状态规则映射、三级门槛 v2.1、水温 5 档响应、虹吸 HHI、回踩 A/B/C、龙头识别传导）。
>
> **未做事项及原因**：8 项计算层 + 2 项 v1.8.0 补全算法全部未落码（grep 实证零命中）——① RRG 轮动序列（无 rs_momentum/relative_rotation）、② 回踩 A/B/C、③ 调整周期进度（MOD-SIG-040 无）、④ 虹吸态 HHI（detect_siphon_state 无）、⑤ q3 多 TF 动量加权、⑥ 5 状态分类（CONSENSUS_CLIMAX/watch_score 无）、⑦ 三级放行门槛、⑧ 水温响应映射、⑨ 板块涨停比归一化（sector_limit_up_ratio 无）、⑩ aggregate_capital_nature_to_sector；全部为纯函数规则层、无新增数据源需求，按 §5.2 演进路径待 G05/G06 施工批次。lead-lag network / ML 转折点检测 / 板块相关性聚类为第四阶段远期登记。

# 板块轮动 spec

> 本备忘定义板块轮动作为选股输入特征（非独立层）的算法规格、复用边界与上限。
> 性质：永久态讨论记录，可随项目演进而修订。
> 管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)。
> 路线图定位见 [00_index_trading_decision](00_index_trading_decision.md) G06（L1·Alpha 选股层，P1，依赖 G04）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G06 板块轮动 spec |
| 所属 | 作战地图 05（BM-SEL-08/09） |
| 依赖 | G04（板块是选股的输入特征，非独立层）/ G05（选股引擎消费板块强度） |
| 对标 | AQR sector momentum / 华泰板块轮动研报（残差动量+拥挤度+遗传规划 2026-03）/ 国信 AI Agent RRG 2026-06 / 东吴 GRU 形态专家 2026-03 / 国海"行业景气度轮转"2026-07 / 西部金工 RRG 2026-05 / WyckoffTradingAgent 板块一日游实证 v2.1.x 2026-04 / 中信建投 行业轮动月报 2026-08（因子动量7子维度）/ 中信证券 拥挤度三视角 2026-08-10 / Goldman Sachs 动量轮动 2026-08-03 / xkqg+quantifiedtrader RRG 公式实现 2026 |
| 正交性 | ✅ 与 regime 正交（板块强度是 sleeve 内选股特征，regime 只做风险节流，见 [30_multi_strategy_concurrency §2.2](30_multi_strategy_concurrency.md)）；水温→仓位映射归 regime（[10_regime_detector_spec.md](10_regime_detector_spec.md)/[28_sentiment_cycle_trading.md](28_sentiment_cycle_trading.md)），本 spec 只声明板块信号对水温的响应 |
| 优先级 | P1 |
| 状态 | 已定稿·部分待施工（BM-SEL-08/09 登记 proposed，板块强度/资金流已 production，轮动序列/回踩A/B/C/调整周期/虹吸态/传导映射/短周期动量q3/5状态分类/三级放行门槛/水温响应映射待施工） |

## 2. 背景

### 2.1 项目处境
- 个人 + 100% AI 开发的 A 股量化系统（miniQMT 通道，T+1 结算，不能做空）
- 板块在架构中是**选股的输入特征**，不是独立决策层——G04（[20_first_batch_strategies](20_first_batch_strategies.md)）三策略"与 regime 关系"行（§2.2/§2.3/§2.4）均裁定选股**不读** regime 输出、只收 budget 数字；板块信号作为选股打分维度的消费关系落在选股漏斗（BM-SEL-17 初筛消费板块强度）与 G04 §7.2 作战地图登记（BM-SEL-08/09 为"G06 板块轮动输入"）。⚠️ 注意：20 号 §2.5 差异化矩阵 8 行维度中无"板块信号"行，板块消费关系真实出处是 §2.2-2.4 各节 + §7.2，已登记 §7 待定问题（20 号 §2.5 矩阵补板块维度行，不越界改）
- **板块数据采集与基础分析已 production**（非空白起步，逐项真源见 §2.5 已施工设施盘点）：
  - `sector_snapshot_collector`（production，[11_d_data](../../02_domain_architecture_docs/11_d_data.md)）：tqcenter → ClickHouse `sector_snapshot` 表，混合模式（推送 99 只 + 全量轮询 30 秒），schema 真源 18 个采集字段（22 列含审计列，[market_sector_snapshot.py](../../../../schemas/categories/market_sector_snapshot.py) DDL-as-Code）。**实测 2026-07-22：582 只 = 454 个 880xxx + 128 个 881xxx**（非设计估算 584）
  - `sector_ranking_engine`（production，[11_d_data](../../02_domain_architecture_docs/11_d_data.md)）：5 因子复合排名动态选 99 只推送池，基准 880001.SH（上证指数）
  - `sector_analyzer`（[MOD-SIG-026](../../../03_modules/_domain_signal/blueprint.md)，production/stable）：6 维度板块分析（强度/延续性/轮动预警/启动条件/风格适配/抱团瓦解），纯函数（v1.9.0 代码确认 6 方法落码：evaluate_strength/judge_continuity/warn_rotation/evaluate_launch_conditions/adapt_market_style/detect_breakdown）
- [battle_map_05 BM-SEL-08/09](../battle_map/battle_map_05_stock_selection.md) 已登记 proposed：轮动序列追踪 + 回踩 A/B/C（缺失态-未实现）、调整周期进度（MOD-SIG-040 planned）

### 2.2 核心问题
460+ 板块如何量化强度、追踪轮动序列、给回踩打 A/B/C 级、追踪调整周期、识别虹吸态、度量资金流、传导到个股？**A 股板块"一日游"特征下**（§2.3 约束末条实证 Top3 次日重合率仅 14.8%），如何在不依赖"板块持续领涨"假设的前提下，快速感知轮动方向变化、对非热门启动板块放行、按大盘水温节流？哪些复用现有 production、哪些待施工？

### 2.3 约束条件
- 板块是特征非独立层 → 板块信号只进选股打分，不做独立仓位分配（与 regime 边界一致，[30_multi_strategy_concurrency §2.2](30_multi_strategy_concurrency.md)）
- 460 板块全覆盖但实时只 Top 99 → 采集层已解（推送池动态选取），计算层按需（强度盘后批量，预警实时仅推送池）
- A 股 T+1 → 板块轮动信号盘后/盘中更新，不参与日内翻转。**信号→执行时序显式声明**（v1.9.1 收拢）：本 spec 全部盘后信号（q 因子/RRG 象限/5 状态/虹吸态/涨停比）T 日收盘后批量计算 →  earliest 可执行点是 **T+1 日开盘**（集合竞价或开盘后）→ 板块信号的有效期须覆盖 T+1 全天才可操作。含义：① §3.1⑧ q3 超短周期因子在电风扇行情（§2.4 实证周度排名变化 12.75 > 历史 75 分位）下，T→T+1 隔夜衰减是主要信号损耗源，权重 0.3 已含此折损；② §3.1④ RRG 象限（DualEma 10/26 日）变化缓慢，T+1 执行时滞影响可忽略；③ §3.1⑨ 5 状态为市场级快照，T+1 日盘中若状态翻转（如 CONSENSUS_CLIMAX→DISAGREEMENT_PULLBACK），盘后重算前 watch_score 沿用 T 日判定——状态级滞后风险由 §3.1④ whipsaw 连续 2-3 日确认规则部分对冲
- 情绪周期是隐形驱动（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)）→ 板块强弱在主升/疯狂态高度集中，虹吸态是该周期的板块级表现
- **板块一日游约束**（[WyckoffTradingAgent v2.1.x 2026-04 实证](https://github.com/YoungCan-Wang/WyckoffTradingAgent/wiki/04_Finance_Sector_Rotation_Regime)）：基于"板块持续领涨"假设的策略在 A 股严重失效，强度公式与放行门槛必须为快速轮动留出感知窗口与放行通道

### 2.4 2026-08 A 股市场实证对照（行业坐标校准）

> 本节为 spec 假设的"当前市场坐标校准"——验证板块轮动 spec 的设计假设与 2026-08 实盘一致，非算法本身。

- **A 股仍处上行周期但单边行情难再现**（2026-08-10 十大券商看后市）：7 月大幅回调后，板块/风格再平衡需求提升——印证 §3.1④ RRG 轮动序列追踪的必要性（纯趋势跟随会错过再平衡期的轮动机会）
- **超跌反弹有演绎空间，小盘弹性显著强于大盘**：印证 §3.1⑩ 三级放行门槛降低阈值（v2.1：0.70→0.60 / 0.90→0.80）的合理性——小盘启动板块好股票若被高门槛拦截会错过反弹
- **8 月中下旬中报密集期是检验反弹成色窗口**：板块强度算法（§3.1①）的资金流+涨停梯队维度天然对中报业绩兑现敏感，无需新增基本面因子
- **高低切换已成定局**：科技兑现、周期加仓（煤炭/有色/化工/贵金属资金净流入榜单前四）——印证 §3.1⑤ 虹吸态识别的时效性（虹吸从 AI 产业链向周期切换）
- **PPI 连续三个月环比上行**（2026-08-09 国家统计局数据），工业产品价格底部确认；**库存周期见底**（沪铜社会库存 7.8 万吨创五年新低，电解铝连续 11 周去库）——周期板块进入 §3.1④ RRG "改善"象限（RS-Ratio<100 但 RS-Momentum>100）的宏观支撑
- **"电风扇"式再平衡的量化确认（v1.9.1 补，2026-08-10/11 最新）**——为 §2.3 一日游约束（Top3 次日重合率 14.8%）提供 2026-08 机构侧量化印证，支撑 §3.1⑧ q3 权重 0.3 与 §3.1⑩ 门槛 v2.1 降阈值：
  - [国泰海通 2026-08](https://m.weibo.cn/detail/5330754731250030)：7 月 28 日-8 月 7 日**周度行业排名变化均值 12.75，超历史 75 分位 11.75**，"典型的'电风扇'式再平衡"，"本轮科技反弹或为拥挤出清后的超跌修复，而非新一轮单边主升"
  - [川观新闻 2026-08-11 盘面](https://cbgc.scol.com.cn/news/7840749)：沪指终结六连阳跌 0.82% 报 3934 点、缩量 2.34 万亿，机器人/MLCC/算力租赁/创新药"一个接一个，但都没有持续性"——电风扇行情进行时实盘证据
  - [财信证券行业轮动周报 2026-08-10](https://m.toutiao.com/group/7672560316760490502/)（数据截至 08-07）：高拥挤区电子/食品饮料；快速升温区建筑材料/医药生物/传媒/计算机等 10 行业；Beta/Alpha 区间划分（12 行业 Beta 共振 / 18 行业 Alpha 分化）——与 §3.1⑨ 5 状态分类（高拥挤≈DISTRIBUTION_RISK/CONSENSUS_CLIMAX 视角）同向，"Alpha 区间=行业内部分化"支持 §3.1⑦ 龙头识别在分化行情中的权重溢价

### 2.5 已施工设施盘点（通用规则 #11，2026-08-12 代码侧/schema 真源审计）

> 本节盘点与本 spec 相关的全部已建设施（代码/schema/调度任务真源），作为 §3"复用 production + 补 8 项待施工"裁定的事实基座。✅=已落盘可消费，🟧=已登记未施工。

| 设施 | 真源路径 / 表 | 状态 | 本 spec 消费点 |
|---|---|---|---|
| 板块快照采集 | `src/zephyr/data/sector_snapshot_collector.py` → `c1_market.sector_snapshot`（ReplacingMergeTree，18 采集字段：now_price/open/max/min/last_close/amount/up_home/down_home/zangsu 等，**无 N 日累计涨跌幅字段，亦无资金流字段**——板块级 net_inflow 需 money_flow×sector_constituent 聚合，见 §3.1⑥） | ✅ production | §3.1① 强度实时输入；快照是**实时截面**，非多日日频序列 |
| 板块 K 线下载 | `src/zephyr/data/sector_kline_downloader.py` → `c1_market.market_kline_sector_880`（tqcenter 盘后日K/分钟K，`--period all` 全周期） | ✅ production | **§3.1⑧ q3/q5/q20 真正数据源**——N 日累计涨跌幅从 880xxx 日K 收盘价计算（v1.9.0 修正：此前误声明自 sector_snapshot 的 change_pct_3d/5d/20d 字段，该表无此字段）；§3.1④ RRG 的 P_sector 序列同源 |
| 板块动态排名 | `src/zephyr/data/sector_ranking_engine.py`（5 因子复合，基准 880001.SH） | ✅ production | §3.1① 动量活跃度维 + Top99 推送池选取 |
| 板块分析器 | `src/zephyr/signal_ashare/sector_analyzer.py`（MOD-SIG-026） | ✅ production/stable | §3.1① 结构强度维（evaluate_strength）+ §3.1④ 单板块轮动预警（warn_rotation）+ §3.1⑥ 资金流字段（SectorData.net_inflow） |
| 板块成分股 | `c1_market.sector_constituent`（sector_code/stock_code，SCD-2 valid_from/valid_to，[schema](../../../../schemas/categories/market_sector_constituent.py)） | ✅ production | §3.1① 涨停比归一化的成分股数分母 + §3.1⑦ 板块→个股传导映射的归属关系 + v1.8.0 资金性质板块级聚合的成分清单 |
| 个股资金流分层 | `c1_market.money_flow`（main/super_large/large/medium/small 五层净流入+净占比，[schema](../../../../schemas/categories/market_money_flow.py)） | ✅ production | v1.8.0 `aggregate_capital_nature_to_sector` 的个股级输入（经 sector_constituent 聚合上溯板块级） |
| 板块元数据/清单 | `c1_market.sector_meta` / `sector_list` / `concept_sector`（schemas/categories/ 下 DDL-as-Code） | ✅ production | 板块代码↔名称映射、概念板块补充维度 |
| 市场情绪分析 | `src/zephyr/signal_ashare/market_sentiment_analyzer.py`（BM-SEL-03-A） | ✅ production | §3.1① 封板率修正因子的情绪数据基础（边界：市场整体情绪温度归 G21/BM-SEL-23-B） |
| 盘中买卖点 | `src/zephyr/signal_ashare/intraday_buy_sell_point_analyzer.py`（BM-SEL-05-C） | ✅ production | §3.1② 回踩 A/B/C 复用其 PULLBACK 买点判定 + Fib 回撤位 |
| 待施工（已登记） | 轮动序列 RRG / 回踩 A/B/C 评级 / 调整周期进度（MOD-SIG-040 planned）/ 虹吸态 HHI / q3 加权 / 5 状态分类 / 三级门槛 / 水温映射 | 🟧 proposed/planned | §3.1②③④⑤⑧⑨⑩⑪——算法已在 §3.1 逐项定型，代码未落盘 |

**盘点结论**：①采集层（快照+K线+成分股+资金流+元数据）全部 production，**待施工 8 项全部是计算/逻辑层纯函数**，无新增数据源需求；②q 因子与 RRG 的日频序列数据源是 `market_kline_sector_880`（K 线）而非 `sector_snapshot`（实时快照）——两表分工：快照管实时截面，K 线管多日序列；③板块→个股传导的归属关系已有 SCD-2 成分股表承载，v1.8.0 两项补全算法（涨停比归一化/资金性质聚合）的数据依赖均已具备。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-SEL-08-A | 板块分析器 | §2.5（板块分析器 `sector_analyzer.py` MOD-SIG-026 盘点行）/ §3.1①（裁定复用 `evaluate_strength` 结构强度维：涨停数+梯队完整性+板块指数趋势 40%/30%/30%） | production已建 |

## 3. 决策：复用 production + 补 8 项待施工

### 3.1 十一项讨论要点逐项裁定

#### ① 板块强度算法（BM-SEL-08，880xxx K 线）—— 复用现有双模块

**裁定**：复用 `sector_analyzer.evaluate_strength` + `sector_ranking_engine` 5 因子，两者互补，不新建。

| 模块 | 维度 | 权重 | 性质 |
|---|---|---|---|
| `sector_analyzer.evaluate_strength` | 涨停数 + 梯队完整性 + 板块指数趋势 | 40% / 30% / 30% | **结构强度**（情绪/连板结构，主升/疯狂态敏感） |
| `sector_ranking_engine` | 成交额 + 涨跌幅绝对值 + 主动交投 + 5min 动量 + 板块-大盘强弱差 | 30%/25%/20%/15%/10% | **动量活跃度**（资金行为，全态适用） |

- `evaluate_strength` 输出 0-100 分 + 强/中/弱（强≥70 / 中≥40 / 弱<40），基准见 `SectorAnalysisConfig`
- `ranking_engine` 输出百分位排名（0~1，消除量纲），基准 880001.SH，缺失时用全板块均值
- **互补理由**：纯涨停梯队在非情绪市（震荡/冰点）失效，纯动量在主升态滞后；双模块覆盖结构+动量两维
- **情绪温度修正因子（板块内封板率）**：双模块算出的板块强度需按板块内封板率修正——[雪球 2026-02](https://xueqiu.com/2118496927/376795876) 量化实证龙头炸板率 8% vs 跟风 32% vs 孤板 58%，封板率=1-炸板率反映资金承接力。板块涨停多但封板率低（<70%）=情绪虚高不稳，强度打折（×0.8）；封板率高（≥85%）=资金共识强，强度确认。**边界**：市场整体情绪温度（全市场涨停家数/连板高度/炸板率/晋级率）归 [G21 情绪周期×交易决策](00_index_trading_decision.md) 与 BM-SEL-23-B；本 spec 只用**板块内**封板率作板块强度的情绪修正因子，不重复建市场情绪温度
- **对标**：国海固收 2026-07"行业景气度轮转"用 5 项量化指标（涨幅/营收增速/净利增速/ROE/换手率）月度打分 TOP5-10，本项目的 5 因子是日内动量版（同思路、更高频）
- **板块涨停比归一化（v1.8.0 新增——施工环节算法补全）**：`evaluate_strength` 的"涨停数"维度是绝对值，不同板块成分股数量差异大（电力设备 ~200 只 vs 油气 ~30 只），绝对数不可跨板块比较。补全算法：

  ```python
  # 板块涨停比 = 板块涨停数 / 板块成分股数（归一化宽度指标）
  sector_limit_up_ratio = sector_limit_up_count / len(sector_constituents)
  # 电力设备 19/200 ≈ 9.5% vs 油气 3/30 ≈ 10% → 油气涨停比更高但绝对数更低
  # evaluate_strength 的"涨停数"维度替换为"涨停比"，保持 40% 权重不变
  # 阈值校准：涨停比 >5% = 强情绪宽度 / >10% = 极强 / <2% = 弱
  ```

  **为何用涨停比而非绝对数**：板块级涨停绝对数无法跨板块比较——电力设备 19 涨停（200 只成分股）和油气 3 涨停（30 只成分股）的涨停比接近（9.5% vs 10%），但绝对数差 6 倍。归一化后才能公平比较板块间情绪宽度。
- **板块级资金性质聚合（v1.8.0 新增——施工环节算法补全）**：[25_multifactor_strategy_detail §647-656](25_multifactor_strategy_detail.md) 已有个股级资金性质 5 类分类（拉升/吸筹/弱托底/对倒嫌疑/出货），但未上溯到板块级聚合——板块评分缺资金流维度。补全算法：

  ```python
  def aggregate_capital_nature_to_sector(sector_constituents, capital_nature_scores):
      """将个股级资金性质聚合到板块级

      Args:
          sector_constituents: list[str], 板块成分股代码
          capital_nature_scores: dict[str, float], 个股资金性质因子值
              (拉升=+1 / 吸筹=+0.5 / 弱托底=0 / 对倒嫌疑=-0.5 / 出货=-1)

      Returns:
          sector_capital_score: float, 板块级资金性质得分 [-1, +1]
          sector_capital_label: str, "主力流入" / "中性" / "对倒主导" / "主力流出"
      """
      scores = [capital_nature_scores.get(s, 0) for s in sector_constituents]
      # 按成交额加权（大票权重高）
      weights = [get_turnover(s) for s in sector_constituents]
      total_weight = sum(weights)
      sector_capital_score = sum(s * w for s, w in zip(scores, weights)) / total_weight

      if sector_capital_score > 0.3:
          label = "主力流入"       # 板块整体拉升/吸筹主导
      elif sector_capital_score > -0.1:
          label = "中性"           # 混合或弱托底
      elif sector_capital_score > -0.5:
          label = "对倒主导"       # 板块对倒嫌疑占比高（final_report 浪潮信息案例）
      else:
          label = "主力流出"       # 板块整体出货主导
      return sector_capital_score, label
  ```

  **与 `evaluate_strength` 的整合**：板块级资金性质得分作为 `evaluate_strength` 的**修正因子**（非新维度）——"主力流入"板块强度×1.1（资金面确认结构强度），"对倒主导"板块强度×0.8（虚假流入风险），"主力流出"板块强度×0.6（资金面否定结构强度）。**不新增第 4 维度**避免重构 evaluate_strength 权重体系，仅在输出层做乘法修正。**数据源**：ClickHouse `money_flow` 表已有主力净流入/超大单/大单/中单/小单分层字段（[25号](25_multifactor_strategy_detail.md) 已确认 production），无需新建数据管道。
- **A 股 regime-dependent 行业轮动参考（v1.8.0 新增）**：[南京大学 2026 CDEMS](https://doi.org/10.2991/978-94-6239-699-9_51) 提出端到端 regime-dependent 行业轮动框架——4-regime 市场状态分类（20 日波动率×20 日轮动速度）→ XGBoost 预测下期 regime 概率 → regime-dependent risk parity。**regime 概率同时进入信号层和协方差结构**，让配置层随市场环境自适应。2023-2024 样本外优于 equal-weight 和非 regime 方案。其"20 日波动率×20 日轮动速度"定义 regime 是比纯 HMM 更可解释的替代方案，可作为本项目 [10号 regime detector](10_regime_detector_spec.md) 的 regime 定义交叉验证。Phase 2+ 候选——MVP 阶段 4-state HMM + overlay 已够，南京大学方案作为 regime 定义替代验证。

#### ② 回踩质量等级 A/B/C 判定 —— 待施工（BM-SEL-08 缺失态-未实现），量化算法

**裁定**：定义 A/B/C 三级（盘后/盘中按需计算），用于 [BM-BUY-04 买入优先级](../battle_map/battle_map_05_stock_selection.md) 与突破失败降级。量化维度 = Fibonacci 回撤位 + 量能衰减序列 + 板块强度。

| 等级 | Fib 回撤位 | 量能衰减 | 板块强度 | 买入优先级 |
|---|---|---|---|---|
| **A** | 38.2%-50%（浅/中） | 缩量序列（逐日递减至 50 日均量 35-50%，[protraderdashboard 2026](https://prodigytradingteam.com/blogs/trading-blog/why-pullbacks-fail-fake-dips-trend-traps-2026) 量能衰减 Day6:80%→Day9:35% 范式） | ≥70（强） | 优先建仓（满仓风险预算） |
| **B** | 50%-61.8%（深） | 混合量能（部分日放量但不破支撑） | 40-70（中） | 分批建仓（半仓风险预算） |
| **C** | >61.8% 或破 78.6% | 回踩放量（机构派发，[BreakoutBulletin 2026](https://breakoutbulletin.com/article/pullback-trading-strategy-fibonacci-guide-2026) 量能上升=distribution） | <40（弱）/ 轮动预警 | 观望/突破失败降级 |

- **61.8% 分水岭**（BreakoutBulletin 2026）：健康趋势回踩应守住 61.8%，>78.6% 趋势结构破坏，回踩转反转
- **回踩时间窗（第4维度）**：A/B/C 量化三维度（Fib+量能+板块强度）外，加回踩时间窗——健康回踩 3-10 交易日（[BreakoutBulletin 2026](https://breakoutbulletin.com/article/pullback-trading-strategy-fibonacci-guide-2026) "5-10 sessions ago"），>15 交易日转横盘整理（回踩失效），<2 交易日属盘中洗盘非真回踩（不入 A/B/C 评级）
- **regime 仓位适配**：主升/疯狂态回踩浅（38.2%为主，情绪推升买盘强）；冰点/震荡态回踩深（50-61.8%，[BreakoutBulletin 2026-04](https://breakoutbulletin.com/article/pullback-trading-strategy-fibonacci-guide-2026) 实证 2026 selective risk-off 应瞄准 50/61.8%）—— A/B/C 等级固定，但仓位风险预算随 regime 调整
- 输入：个股回踩形态（复用 `intraday_buy_sell_point_analyzer` 的 PULLBACK 买点判定 + Fib 回撤位）+ 量能序列 + 板块强度（§3.1①）
- **待施工**：Fib 回撤的 swing high/low 选取规则、量能衰减的具体阈值、regime→风险预算映射表需在 G05/G08 校准

#### ③ 调整周期追踪（BM-SEL-09，进度≥80% 激活分批）—— 待施工（MOD-SIG-040 planned）

**裁定**：新建调整周期进度追踪，输入**板块扩散指标**（新高占比为其变体），输出进度百分比。

- 进度≥80% → 激活 [BM-BUY-04 分批建仓条件①](../battle_map/battle_map_05_stock_selection.md)
- 进度<40% → 初期拦截低吸信号（避免接飞刀）
- 40%-80% → 观察区，不激活不拦截
- **扩散指标（Diffusion Indicator）对应**：板块新高占比 = 扩散指标的一种变体（衡量板块内多少成分股参与上涨/创新高）。[西部金工 2026-05](https://finance.sina.com.cn/wm/2026-05-27/doc-inhziqxn8446705.shtml) 实证扩散指标在震荡市/快轮动期反应滞后，需 RRG（§3.1④）补充——本项目扩散指标管"调整进度"，RRG 管"轮动序列"，分工不重叠
- **待施工**：MOD-SIG-040 草图§6.6 v4.1，进度算法（扩散指标的滚动窗口与归一化）需定参；备选方案为板块指数回撤深度+持续时间（drawdown duration），首轮用扩散指标（与 §3.1④ RRG 数据同源）

#### ④ 轮动序列追踪 —— 待施工（BM-SEL-08 缺失态-未实现），主算法 RRG

**裁定**：复用 `sector_analyzer.warn_rotation`（单板块轮动预警）+ **新增 RRG（Relative Rotation Graph）作为轮动序列主算法**。

- `warn_rotation` 已实现单板块轮动预警（rotation_score 0-100，≥60 触发：连续大涨+放量+龙头滞涨）
- **新增 RRG（相对旋转图）**：Julius de Kempenaer 2004-2005 专为板块轮动序列设计，双轴四象限顺时针旋转即轮动序列的可视化——

| 象限 | RS-Ratio | RS-Momentum | 含义 | 轮动序列位置 |
|---|---|---|---|---|
| 领先 | >100 | >100 | 相对走强且趋势强化 | 接棒中（可买） |
| 疲软 | >100 | <100 | 相对走强但动力衰减 | 见顶（持有/减仓） |
| 滞后 | <100 | <100 | 相对走弱且仍恶化 | 回避 |
| 改善 | <100 | >100 | 相对走弱但减缓/逆转 | 提前布局（观察） |

  - **RS-Ratio** = 相对强度（板块价/基准价）的变化率，>100 相对走强；**RS-Momentum** = RS-Ratio 的动量，引导 RS-Ratio 转向
  - **RRG 计算算法（公式级，v1.6.0 补全）**——采用 JdK（Julius de Kempenaer）DualEma 标准公式（[xkqg/MatPlotLibNet 2026-05](https://github.com/xkqg/MatPlotLibNet/wiki/RelativeRotationSeries) + [quantifiedtrader 2026](https://quantifiedtrader.com/projects/rrg-us-equity/)）：

    **输入**：板块指数收盘价 `P_sector(t)`，基准收盘价 `P_bench(t)`（本项目基准 880001.SH 上证指数，缺失时用全板块均值，与 `ranking_engine` 同源）

    **步骤 1 — 原始相对强度 RS**（标准化到 100 基准）：
    ```
    RS(t) = 100 × P_sector(t) / P_bench(t)
    ```
    - 乘 100 使初始基准点为 100，便于后续标准化

    **步骤 2 — JdK RS-Ratio**（DualEma 双均线比值，衡量 RS 趋势强度）：
    ```
    RS-Ratio(t) = EMA(RS, short=10) / EMA(RS, long=26) × 100
    ```
    - short/long EMA 比值 > 1 → ×100 后 > 100 = 相对走强（短期均线在长期均线之上）
    - short/long EMA 比值 < 1 → ×100 后 < 100 = 相对走弱
    - **西部金工 2026-05 参数变体**：回看 220 日 + MA20 平滑（更长窗口，适合月度调仓的中信一级行业）；本项目 880xxx 细分板块日频，采用标准 10/26 DualEma（最小数据量 = longPeriod×2 + shortPeriod = 62 日，[xkqg 2026-05](https://github.com/xkqg/MatPlotLibNet/wiki/RelativeRotationSeries)）
    - **备选 Z-score 归一化**（[quantifiedtrader 2026](https://quantifiedtrader.com/projects/rrg-us-equity/)）：`RS-Ratio(t) = 100 + z(RS, w=14)`，z = (RS − μ_w) / σ_w，滚动窗口 w=14 周；适合均值回归假设强的市场，本项目以 DualEma 为主、Z-score 作 §3.1④ RRG 增强第1项的跨象限修正输入

    **步骤 3 — JdK RS-Momentum**（RS-Ratio 的 DualEma 动量，引导 RS-Ratio 转向）：
    ```
    RS-Momentum(t) = EMA(RS-Ratio, short=10) / EMA(RS-Ratio, long=26) × 100
    ```
    - 与 RS-Ratio 同公式结构，但输入换成 RS-Ratio 序列（动量的动量）
    - RS-Momentum > 100 = RS-Ratio 上升趋势在强化；< 100 = 衰减
    - **西部金工 2026-05 参数变体**：RS-Mom 回看 60 日

    **步骤 4 — 四象限落点**（(RS-Ratio, RS-Momentum) 二维坐标 → 象限分类）：
    ```
    if RS-Ratio > 100 and RS-Momentum > 100: quadrant = "领先"
    elif RS-Ratio > 100 and RS-Momentum < 100: quadrant = "疲软"
    elif RS-Ratio < 100 and RS-Momentum < 100: quadrant = "滞后"
    elif RS-Ratio < 100 and RS-Momentum > 100: quadrant = "改善"
    ```

    **步骤 5 — 旋转路径追踪**（尾部长度 k=8，[xkqg 2026-05](https://github.com/xkqg/MatPlotLibNet/wiki/RelativeRotationSeries) 默认 TailLength=8）：
    - 保留过去 k=8 个交易日的 (RS-Ratio, RS-Momentum) 序列作为"尾巴"
    - 尾巴方向 = 象限转移趋势（如 改善→领先 的尾巴朝右上方 = 接棒确认）
    - 角度追踪（[quantifiedtrader 2026](https://quantifiedtrader.com/projects/rrg-us-equity/)）：θ(t) = atan2(RS-Momentum−100, RS-Ratio−100)，θ 变化量化顺时针/逆时针旋转速度；r = √(x²+y²) 衡量信号强度（离中性点 100,100 的距离）

  - **RRG 象限 → 交易信号映射算法（v1.6.0 补全，原缺口"象限到信号转换未算法化"）**：

    | 象限 | 交易信号 | 板块强度综合层影响 | §3.1⑩ 三级门槛关系 | §3.1⑪ 水温响应关系 |
    |---|---|---|---|---|
    | **领先** | 买入候选（接棒中） | 板块强度 +0.05（加分） | 核心热门直通（Top 列表） | NEUTRAL/RISK_ON 放行 |
    | **改善** | 提前布局候选（观察） | 板块强度 +0.02（轻加分，未确认） | 超强个股 ≥0.80 通配 | PANIC_REPAIR 优先放行 |
    | **疲软** | 持有/减仓（见顶） | 板块强度 −0.03（衰减扣分） | 次优板块 + 个股强度 ≥0.60 | RISK_OFF 仅龙头 ×1.5 |
    | **滞后** | 回避/拦截 | 板块强度 −0.08（重扣） | 拦截（不进入打分） | CRASH 全拦截 |

    - **象限转移确认规则**（应对 whipsaw 假信号，[kriterionquant 2026-01](https://kriterionquant.com/wp-content/uploads/2026/01/RRG_Dashboard_Complete_11_January_2026.html)）：
      1. **连续 2-3 日确认**：象限转移须连续 2-3 个交易日保持在新象限才采信（单日跳变 = 假信号，不触发信号变更）
      2. **transition matrix 概率门限**：历史转移概率 < 10% 的异常路径（如 领先→改善，跳过疲软/滞后）需额外 1 日确认；强趋势半圆例外（[State Street 2026-03](https://www.ssga.com/at/de/intermediary/insights/guide-to-sector-momentum-map) 领先→疲软→领先）不受此限
      3. **Z-score 跨象限修正**（§3.1④ RRG 增强第1项）：领先象限 Z>+2 = 透支，买入信号降级为持有；改善象限 Z<−2 = 异常压缩，升级为提前布局
    - **与 §3.1⑧ q3 多时间框架协同**：RRG 象限是中期信号（DualEma 10/26 日），q3 是超短期 3 日信号——q3 翻正 + RRG 改善象限 = 启动确认（双重确认加仓）；q3 翻负 + RRG 领先象限 = 动力衰减预警（减仓）
  - 顺时针旋转 领先→疲软→滞后→改善→领先 = 板块接棒顺序，直接输出给回踩 A/B/C 的板块强度输入与 BM-BUY-04 买入优先级
  - **A股实证**：[西部金工 2026-05](https://finance.sina.com.cn/wm/2026-05-27/doc-inhziqxn8446705.shtml) 用 RRG + 扩散指标做中信一级行业轮动，2018.12-2026.03 年化 20.60%（超额 9.49%），RRG 在震荡市/快轮动期弥补扩散指标滞后
- **为何 RRG 优于纯排名时序**：纯排名时序只看强弱排名变化，丢失"动量引领趋势"的领先信息；RRG 的 RS-Momentum 是 RS-Ratio 的动量，能预测 RS-Ratio 转向（领先信号），且四象限天然对应轮动序列的"接棒/见顶/回避/布局"四阶段
- **RS-Ratio 与 ranking_engine 第5因子关系澄清**（防施工重复造轮子）：§3.1① `ranking_engine` 第5因子"板块-大盘强弱差"是**当日截面快照**（选 Top99 推送池用）；RRG 的 RS-Ratio 是相对强度的**220 日时序变化率**（MA20 平滑，轮动序列追踪用）。两者数据源同源（都相对基准/大盘）但时间维度与用途不同——ranking 选池（高频截面），RRG 追轮动（低频时序），不重复计算
- **RRG 增强（2026-08 最新实践）**：
  1. **Z-score 均值回归叠加**（[closelook 2026-08-07](https://closelook.net/lab/patterns/sector-rs/)）：Z=（当前 RS-Ratio − 63 日均值）/ 63 日标准差，|Z|>2 = 统计拉伸/异常压缩——跨象限修正规则见上方"象限转移确认规则"第 3 条
  2. **多时间框架交叉**（[closelook 2026-08-07](https://closelook.net/lab/patterns/sector-rs/)）：21d/63d/252d 三独立排序。21d 领先 + 252d 滞后 = **新轮动候选**（fresh rotation）；252d 领先 + 21d 滞后 = **疲惫龙头**（tired leader，减仓信号）。全貌需三时间框架共读，单一框架可误判
  3. **whipsaw 假信号风险**（[kriterionquant 2026-01](https://kriterionquant.com/wp-content/uploads/2026/01/RRG_Dashboard_Complete_11_January_2026.html)）：板块可在象限间快速来回（whipsaw）= 假信号——确认机制见上方"象限转移确认规则"第 1/2 条（连续 2-3 日确认 + transition matrix 概率门限）
  4. **强趋势半圆旋转例外**（[State Street 2026-03](https://www.ssga.com/at/de/intermediary/insights/guide-to-sector-momentum-map)）：顺时针旋转是理想模式非必然——极强趋势下板块可 领先→疲软→领先（半圆，不经过滞后/改善），极弱趋势可 滞后→改善→滞后。施工时旋转路径检测需容许半圆模式
- **待施工**：RRG 计算（RS-Ratio/RS-Momentum 标准化到100基准，RS-Ratio 回看 220 日+MA20，RS-Mom 回看 60 日，[西部金工 2026-05](https://finance.sina.com.cn/wm/2026-05-27/doc-inhziqxn8446705.shtml) 参数）+ 四象限落点 + Z-score 叠加 + 三时间框架 + transition matrix 存储；lead-lag network（Granger/transfer entropy）作为第三阶段增强（更重，追踪板块间信息流向，非首轮）

#### ⑤ 虹吸态识别（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md) 情绪周期隐形驱动）—— 待施工

**裁定**：新建虹吸态识别。**2026 实证支撑**：国海固收 2026-07 报告指出"AI 产业链凭借产业落地提速对场内资金形成持续虹吸"，2026 上半年电子+86%/通信+74% vs 商贸零售-29%/农林牧渔-25%，首尾差超 115 个百分点——虹吸态是 2026 A 股真实现象，非理论构造。

- **虹吸态定义**：少数头部强势板块吸金，致其余板块缺血的极端分化状态（情绪周期主升/疯狂态的板块级表现）
- **识别信号**（待定参）：① 头部 N 板块成交额集中度（HHI 赫芬达尔指数，越接近 1 越集中）+ ② 净流入集中度 + ③ 其余板块资金净流出比例；三者滚动 z-score 标准化后加权
- **HHI 选用理由**：HHI 是产业经济学衡量市场集中度的标准指标（∑份额²），比简单"头部占比"更敏感于寡头化程度，且 0-1 归一便于跨期比较
- **用途**：虹吸态下选股收紧到头部强势板块，回避缺血板块（作为 G05 选股引擎的市场状态适配输入，与 regime 正交——regime 管总量风险，虹吸态管板块结构）

**施工伪代码（v1.7.0 补全——v1.6.0 为 RRG/q 因子/5 状态/门槛/水温均补了伪代码，唯独虹吸态遗漏，本轮补齐）**：

```python
def detect_siphon_state(sectors: list[SectorData], window: int = 20, n_top: int = 5) -> dict:
    """虹吸态识别——少数头部强势板块吸金，致其余板块缺血的极端分化状态
    
    Args:
        sectors: 当日全市场板块列表（含 turnover, net_inflow 字段）
        window: z-score 标准化滚动窗口（默认 20 交易日）
        n_top: 头部 N 板块数（默认 5，与 §3.1⑨ hhi_top5 协同）
    Returns:
        {"is_siphon": bool, "siphon_score": float, "siphon_sectors": list[str]}
    """
    # --- 信号①：头部 N 板块成交额集中度（HHI）---
    total_turnover = sum(s.turnover for s in sectors)
    top_n = sorted(sectors, key=lambda s: s.turnover, reverse=True)[:n_top]
    shares = [s.turnover / total_turnover for s in top_n]
    hhi_top_n = sum(share ** 2 for share in shares)  # [0, 1]，越接近 1 越集中
    
    # --- 信号②：净流入集中度（头部 N 板块净流入 / 全市场净流入绝对值之和）---
    total_abs_inflow = sum(abs(s.net_inflow) for s in sectors)
    top_n_inflow = sum(s.net_inflow for s in top_n)
    inflow_concentration = top_n_inflow / total_abs_inflow if total_abs_inflow > 0 else 0  # [-1, 1]
    
    # --- 信号③：其余板块资金净流出比例 ---
    rest_sectors = [s for s in sectors if s not in top_n]
    outflow_count = sum(1 for s in rest_sectors if s.net_inflow < 0)
    outflow_ratio = outflow_count / len(rest_sectors) if rest_sectors else 0  # [0, 1]
    
    # --- 三信号滚动 z-score 标准化后加权 ---
    # rolling_zscore 复用 §3.1⑨ 同款（维护滚动窗口历史序列）
    z_hhi = rolling_zscore(hhi_top_n, window)
    z_conc = rolling_zscore(inflow_concentration, window)
    z_outflow = rolling_zscore(outflow_ratio, window)
    
    # 加权合成（权重待 G05/G08 校准，初拟 HHI 0.4/集中度 0.35/流出比 0.25）
    w_hhi, w_conc, w_outflow = 0.4, 0.35, 0.25
    siphon_score = w_hhi * z_hhi + w_conc * z_conc + w_outflow * z_outflow
    
    # --- 触发判定（阈值待 G05/G08 校准，初拟 z > 1.5σ = 虹吸态）---
    is_siphon = siphon_score > 1.5
    
    return {
        "is_siphon": is_siphon,
        "siphon_score": siphon_score,
        "siphon_sectors": [s.name for s in top_n] if is_siphon else [],
    }
```

- **阈值依据**：z-score > 1.5σ 对应正态 ~93% 分位（极端分化）；5 状态用绝对阈值（hhi_top5 > 0.25/0.30），虹吸态用相对 z-score——虹吸态是"相对近期常态的极端分化"而非"绝对集中度高"。权重 HHI 0.4（集中度是核心）/净流入集中度 0.35/净流出比例 0.25（流出是虹吸的后果非原因）。N=5 与 §3.1⑨ hhi_top5 协同，window=20 与 §3.1⑨ rolling 窗口一致。**参数均待 G05/G08 实盘校准**——需 ≥3 个月虹吸态样本后标定（§6 待裁定）。
- **与 §3.1⑨ 5 状态分类的关系**：5 状态分类的 `RISK_ON`（hhi_top5 > 0.30 + up_ratio > 0.70）是虹吸态的一个特例（高集中+大面积上涨），但虹吸态更精确——5 状态用绝对阈值，虹吸态用 z-score 相对阈值，两者可串联（5 状态先判大类，虹吸态再精判极端分化）。

#### ⑥ 板块资金流 —— 复用现有字段，不新建

**裁定**：`sector_analyzer.SectorData` 已含 `net_inflow`（净流入，亿）字段（代码确认 [sector_analyzer.py L88](../../../../src/zephyr/signal_ashare/sector_analyzer.py)）。⚠️ 数据源注意：**snapshot 链路不含资金流字段**——`sector_snapshot` 表 18 采集字段无 inflow 类字段（schema 真源），且 analyzer 是纯函数库（数据装配调用方未落码）。板块级 `net_inflow` 的正确来源 = **`money_flow`（个股级五层净流入，production）× `sector_constituent`（SCD-2 成分股）聚合**——与 v1.8.0 `aggregate_capital_nature_to_sector` 同一聚合路径，该聚合器待施工（纯函数，无新数据源）。

- `evaluate_launch_conditions` 已用 `net_inflow > 0` 加分，`judge_continuity` 已用 `net_inflow ≥ 10亿` 判深度介入
- §3.1⑤ 虹吸态识别直接消费聚合后的板块级净流入，不新建资金流采集管道

#### ⑦ 板块→个股的传导映射 —— 待施工（G05 选股引擎消费），含龙头识别前置

**裁定**：传导分两步——① 龙头识别（板块内个股定位）→ ② 板块强度加权传导。

**步骤① 龙头识别**（板块内个股定位，[东方财富 2026-05](https://caifuhao.eastmoney.com/news/20260523093657718991640) + [55188 2026-04](https://www.55188.com/thread-38870280-1-1.html) 统一标准）：

| 定位 | 量化特征 | 传导权重 | 操作 |
|---|---|---|---|
| **板块龙头/市场总龙** | 涨停启动时间最早 + 封单厚度/流通市值比最大 + 带动后排跟涨（板块定价权） | ×1.5 | 优先建仓（打板/低吸） |
| **中军** | 市值大(200亿+) + 趋势上涨(非连板) + 成交额板块Top3 + 启动稍晚于龙头(2-3板后) | ×1.2 | 波段趋势跟随 |
| **跟风股** | 龙头涨停后被动拉升 + 封单不稳 + 概念边缘 | ×0.8 | 限仓参与 |
| **中位股（3-5板跟风）** | 既无龙头信仰也无低位优势 + 分歧时率先掉队 | ×0（强制规避） | **禁区，禁触**（[55188 2026](https://www.55188.com/thread-38870280-1-1.html) 明确"死亡区域"） |

- 龙头识别量化指标：① 涨停启动时间排序（最先封板=龙头首要特征）② 封单资金量与换手率（封单厚+换手合理=筹码锁定）③ 板块带动效应（龙头涨停→后排跟涨，[新浪 2026-05](https://www.sina.cn/news/detail/5294851223978344.html) 辨识度7标准）
- **中军 vs 情绪龙**（[东方财富 2026-05](https://caifuhao.eastmoney.com/news/20260523093657718991640)）：中军=大市值/趋势/10-20日线低吸（绝大多数投资者）；情绪龙=小市值(50亿-)/连板/打板（职业短线高风偏）—— G08 打板主做情绪龙，G05 选股引擎主做中军

**步骤② 板块强度加权传导**：
- 板块强度≥70（强）→ 板块内个股 score ×定位权重（龙头1.5/中军1.2/跟风0.8）
- 板块强度 40-70（中）→ 定位权重衰减（×0.9 系数）
- 板块强度<40（弱）/ 轮动预警 / 虹吸态缺血 → 板块内个股 score ×0.8（或扣分）
- **具体权重与乘数在 G05 选股引擎定型**，本 spec 声明传导方向（板块→个股，非反向）+ 龙头识别前置流程
- **hot_bonus 修正**（2026-08 整合）：§3.1⑦ 步骤② 的"板块强度加权传导"中，对"在当日 Top 热门列表"的板块有个 hot_bonus 加分（热门板块加成）。原拟 0.05，据 [WyckoffTradingAgent v2.1.x 2026-04 实证](https://github.com/YoungCan-Wang/WyckoffTradingAgent/wiki/04_Finance_Sector_Rotation_Regime)（§2.3 一日游约束）**降至 0.02**——85% 概率今天的热门明天就不热，0.05 加成会过度追高一日游板块

#### ⑧ 短周期动量 q3 增强（应对板块一日游）—— 待施工（BM-SEL-08 增强）

**裁定**：在 §3.1① 板块强度复合之上叠加**多时间框架动量加权**，新增 q3（3 日涨幅排名）作为快速轮动感知因子，不替换 production 双模块，作为下游"板块强度综合"层的加权增强。

**为何新增 q3（决策推理）**：
- 一日游实证（§2.3 约束末条，Top3 次日重合率 14.8%/完全不同 63.2%/领涨仅 1 天 46.6%）——纯 20 日/5 日动量在快速轮动期感知滞后
- 旧版 strength = 0.7×q20 + 0.3×q5 在"板块持续领涨"假设下成立，A 股一日游特征下 20 日权重过高会持续追"已经走完的领涨"
- 新版 strength = 0.4×q20 + 0.3×q5 + 0.3×q3：20 日权重从 0.7 降至 0.4（保留中期趋势锚定），q5 维持 0.3（短中期动量），q3 新增 0.3（3 日超短期动量，最快感知方向变化）
- **为何不直接用 q3 替代 q20**：纯 3 日动量会沦为"追涨杀跌"噪声，需 20 日锚定中期趋势；3 时间框架共读避免单一框架误判（与 §3.1④ RRG 21d/63d/252d 三时间框架同思路）

| 因子 | 时间窗 | 权重 | 性质 | 数据源 |
|---|---|---|---|---|
| q20 | 20 日涨幅排名 | 0.4 | 中期趋势锚定 | `market_kline_sector_880` 日K 收盘价计算 20 日累计涨跌幅（盘后批量） |
| q5 | 5 日涨幅排名 | 0.3 | 短中期动量 | `market_kline_sector_880` 日K 收盘价计算 5 日累计涨跌幅（盘后批量） |
| q3 | 3 日涨幅排名 | 0.3 | 超短期动量（**新增**） | `market_kline_sector_880` 日K 收盘价计算 3 日累计涨跌幅（盘后批量） |

- **q 因子计算算法（v1.6.0 补全公式级）**——qN 是截面百分位排名（0~1 归一化，消除量纲）：
  ```
  # 步骤 1：计算各板块 N 日累计涨跌幅
  ret_N(i, t) = (P_sector_i(t) / P_sector_i(t-N)) - 1

  # 步骤 2：截面百分位排名（全 460+ 板块横向比较）
  qN(i, t) = percentile_rank(ret_N(i, t), 全板块 ret_N(·, t))  # 输出 0~1

  # 步骤 3：多时间框架加权
  strength_momentum(i, t) = 0.4 × q20(i, t) + 0.3 × q5(i, t) + 0.3 × q3(i, t)
  ```
  - `percentile_rank` = 该板块涨跌幅在全板块中的分位（0=最弱，1=最强），与 `ranking_engine` 同归一化思路
  - 输出 `strength_momentum` ∈ [0, 1]，作为"板块强度综合"层第三维（多 TF 动量）输入
  - **数据源**：`market_kline_sector_880` 表（880xxx 板块日K，`sector_kline_downloader` 盘后采集 production）——N 日累计涨跌幅 `ret_N = close(t)/close(t-N) - 1` 从日K 收盘价直接计算，无需新增采集。注意 `sector_snapshot` 表为实时快照（18 采集字段，无多日累计涨跌幅字段）；快照表管实时截面，K 线表管多日序列，两表分工见 §2.5 盘点

- **与 production 双模块关系澄清**（防施工重复造轮子）：§3.1① `evaluate_strength`（涨停梯队+结构）+ `ranking_engine`（5 因子动量活跃度）输出"结构强度+动量活跃度"两维复合分；本项 q3/q5/q20 加权是"纯多时间框架动量"维度，作为前两者的**第三维补充**叠加到"板块强度综合"层（§3.2 架构图），不修改 production 模块本身
- **与 §3.1④ RRG 多时间框架关系澄清**：RRG 的 21d/63d/252d 是相对强度（RS-Ratio）的多时间框架，用于轮动序列追踪（领先/疲软/滞后/改善象限）；本项 q3/q5/q20 是绝对涨幅排名的多时间框架，用于板块强度综合打分。两者时间窗不同（RRG 更长）、基准不同（RRG 相对基准、q 绝对涨幅）、用途不同（RRG 追序列、q 打复合分），不重复计算
- **待施工**：q3 计算从 `market_kline_sector_880` 日K 收盘价取 3 日累计涨跌幅，加权公式落地到"板块强度综合"层；权重 0.4/0.3/0.3 为初拟，需 G05 回测校准（§6 待裁定）

#### ⑨ 板块轮动状态 5 分类（每日市场级状态）—— 待施工（BM-SEL-08 增强）

**裁定**：每日盘后根据各行业涨跌分布判定 1 个市场级板块轮动状态（5 选 1），输出 watch_score 加减分注入板块强度综合层。**与 §3.1⑤ 虹吸态关系**：虹吸态是结构性的极端分化状态（HHI 量化），5 状态是每日市场级快照分类——CONSENSUS_CLIMAX 含虹吸态但更广（多板块同时暴涨未必缺血分化），虹吸态识别独立保留用于板块内选股收紧，5 状态用于市场级 watch_score 调节。

| 状态 | 英文 | 特征 | watch_score | 实证依据 |
|---|---|---|---|---|
| 共识高潮 | CONSENSUS_CLIMAX | 多板块同时暴涨，市场亢奋 | **-0.08** | 后 3 日下跌>2% 概率 29.8% |
| 分歧回调 | DISAGREEMENT_PULLBACK | 涨跌严重分化，领涨板块回调 | +0.01 | 3 日平均收益 -0.51% 胜率 50% |
| 健康主线 | HEALTHY_MAINLINE | 一条明确主线持续领涨 | +0.03 | 主线持续领涨 = RRG 领先象限板块连续 3+ 日 |
| 派发风险 | DISTRIBUTION_RISK | 领涨板块高位放量滞涨 | **-0.10**（最危险） | 高位放量滞涨 = 机构派发 |
| 中性混沌 | NEUTRAL_MIXED | 各行业涨跌互现，无序 | 0.00 | 默认态 |

- **为何 5 分类而非二分类（热/冷）**：二分类丢失"健康主线 vs 共识高潮"的区别——两者都是"热"但前者应加分（主线持续）、后者应重扣（见顶风险）；5 分类与 §3.1④ RRG 四象限互补（RRG 追单板块序列、5 状态判市场级整体）
- **为何不直接复用 regime 12 态**：regime 12 态是指数级市场状态（Bull/Bear/Neutral/BREAKOUT/CRASH），不区分"板块结构"；5 状态专攻"板块间分布结构"（多板块同暴涨 vs 单主线 vs 分化），与 regime 正交（§1 正交性已声明）
- **判定算法（v1.6.0 补全公式级，原"待施工初拟"改为可执行）**——4 维输入 → 规则映射到 5 状态：

  **4 维输入**（盘后全 460+ 板块截面计算）：
  ```
  ① up_ratio    = 上涨板块数 / 全板块数                         # 上涨面广度
  ② hhi_top5    = HHI(头部5板块成交额份额) = Σ(share_i)²          # 集中度，[0,1]
  ③ lead_streak = 当前领涨板块连续领涨天数                        # 主线延续性
  ④ disp_signal = 领涨板块量价配合指标                            # 派发识别
                 = 1 if (领涨板块当日放量(成交额>5日均量×1.2) AND 涨幅<前日涨幅×0.5)
                 = 0 otherwise                                   # 放量滞涨=派发
  ```

  **规则映射（优先级从高到低，命中即定状态）**：
  ```
  if disp_signal == 1 and hhi_top5 > 0.25:
      state = DISTRIBUTION_RISK          # 高位放量滞涨+集中 → 派发风险（最危险）
  elif hhi_top5 > 0.30 and up_ratio > 0.70:
      state = CONSENSUS_CLIMAX           # 高集中+普涨 → 共识高潮（见顶风险）
  elif lead_streak >= 3 and hhi_top5 < 0.20:
      state = HEALTHY_MAINLINE           # 主线持续领涨3+日+未过度集中 → 健康主线
  elif up_ratio < 0.40 and hhi_top5 > 0.20:
      state = DISAGREEMENT_PULLBACK      # 涨跌严重分化+头部集中 → 分歧回调
  else:
      state = NEUTRAL_MIXED              # 默认中性混沌
  ```

  - **HHI 阈值依据**：[legulegu 2026-08-07](https://legulegu.com/stockdata/market-structure/industry-heat) 实证 HHI（前5%个股行业占比平方和）<0.15 分散 / 0.15-0.25 监控 / >0.25 预警；[rebuildingsociety 2026-06](https://www.rebuildingsociety.com/optimising-sme-loan-portfolios-key-concentration-indicators-for-investors/) 同阈值。本项目 hhi_top5 取头部 5 板块成交额份额平方和（与 §3.1⑤ 虹吸态 HHI 同源但 N 不同：5 状态用 N=5，虹吸态用 N=3/5/10 待标定）
  - **派发识别依据**：[华泰金工 2026-03](https://finance.sina.com.cn/wm/2026-03-17/doc-inhrfwqa9598438.shtml) 拥挤度模型用 4 量价指标 + 95% 分位门限，3/4 触发=高拥挤；本算法 disp_signal 简化为放量+滞涨二条件（个人项目轻量化，不建 4 指标门限体系）
  - **轮转速度辅助指标**（[legulegu 2026-08-07](https://legulegu.com/stockdata/market-structure/industry-heat)）：`rotation_speed = 0.5 × Σ|sector_i今日占比 − sector_i昨日占比|`，高轮转速度（>P90）= 快轮动期，5 状态判定时 CONSENSUS_CLIMAX 阈值放宽至 hhi_top5 > 0.35（快轮动期集中度天然偏高，避免误判）
  - **2026-08 实盘校准**：[中信证券 2026-08-10](https://36kr.com/newsflashes/3932984519146887) 指出 8 月初市场三种拥挤度类型（电子/通信/建材高位抱团 / 化工/电新/有色快速回落 / 持续低拥挤），印证 5 状态需动态追踪——CONSENSUS_CLIMAX → DISAGREEMENT_PULLBACK 转换在中报密集期（8 月中下旬）高频出现
- **watch_score 用途**：注入"板块强度综合"层作为市场级调节项（全板块强度分统一加减），不进仓位分配层（与 regime 边界一致）。例如 CONSENSUS_CLIMAX 时全板块强度分 -0.08，抑制追高
- **待施工**：状态判定规则阈值、watch_score 与板块强度综合层的叠加方式（加法 vs 乘法）需 G05 校准

#### ⑩ 三级放行门槛（板块→个股准入 gate）—— 待施工（G05 选股引擎消费）

**裁定**：在 §3.1⑦ 板块强度加权传导之前加一道**准入 gate**——个股须满足"板块归属 + 个股强度"双条件才进入打分。v2.1 阈值较 v2.0 降低，应对板块一日游（非热门启动板块好股票不应被高门槛拦截）。

| 级别 | 条件 | v2.0 阈值 | **v2.1 阈值** | 放行动作 |
|---|---|---|---|---|
| 核心热门板块 | 在当日 Top 热门板块列表中 | 直通 | **直通** | 进入打分（§3.1⑦ 加权传导） |
| 次优板块+个股强度 | 非核心热门（在保留板块集但非 Top） | 个股强度 ≥0.70 | **≥0.60** | 进入打分（§3.1⑦ 加权传导，定位权重衰减） |
| 超强个股通配 | 无视板块限制 | 个股强度 ≥0.90 | **≥0.80** | 进入打分（§3.1⑦ 加权传导，无板块加权） |
| 其余 | 不满足上述任一 | — | — | **拦截**（不进入打分） |

- **为何降低阈值（决策推理）**：一日游特征（Top3 次日重合率 14.8%，§2.3）下，对非热门板块要求过高（0.70/0.90）会错过大量"今日非热门、明日启动"的板块好股票；v2.1 降至 0.60/0.80 留出放行通道，靠 §3.1⑧ q3 短周期动量快速感知启动、§3.1⑨ 5 状态分类抑制高潮追高
- **与 §3.1⑦ 传导映射关系澄清**：⑩ 是"是否允许进入打分"（准入 gate，二元判定），⑦ 是"进入打分后如何加权"（连续乘数）；⑩ 在 ⑦ 之前，先 gate 后 weight
- **"个股强度"定义**：复用 G05 选股引擎的多因子综合分（0-1 归一化），非本 spec 定义；本 spec 只声明"板块归属 × 个股强度"的双条件 gate 结构
- **准入 gate 算法（v1.6.0 补全公式级）**——先 gate 后 weight（§3.1⑦ 加权传导）：
  ```
  # 输入：个股 i 的板块归属 sector_i，个股强度 score_i ∈ [0,1]，当日 Top 热门板块集合 top_sectors
  # 输出：gate_pass (bool), gate_level (str)

  if sector_i in top_sectors:                     # 级别1：核心热门板块直通
      gate_pass = True
      gate_level = "CORE_HOT"
  elif score_i >= 0.60:                           # 级别2：次优板块+个股强度≥0.60
      gate_pass = True
      gate_level = "SECONDARY"                    # §3.1⑦ 加权时定位权重衰减 ×0.9
  elif score_i >= 0.80:                           # 级别3：超强个股通配（无视板块）
      gate_pass = True
      gate_level = "WILDCARD"                     # §3.1⑦ 加权时无板块加权
  else:
      gate_pass = False                           # 拦截
      gate_level = "BLOCKED"
  ```
  - **动态阈值调整**（与 §3.1⑪ 水温响应联动）：水温 = CRASH 时全部 gate_pass = False（全拦截）；RISK_OFF 时仅 CORE_HOT + score_i≥0.80 放行（级别2 阈值升至 0.80）；PANIC_REPAIR 时级别2 阈值降至 0.50（超跌反弹期放宽，配合 §3.1④ RRG 改善象限优先放行）
- **超强个股通配为何保留**：板块一日游特征下，部分个股会领先板块启动（板块尚未进入 Top 但个股已超强），通配通道避免漏掉领涨个股；但阈值 0.80 仍高（v2.1 降低但非取消），避免无板块支撑的弱势个股混入
- **待施工**：阈值 0.60/0.80 为 v2.1 初拟，需 G05 回测验证（§6 待裁定）；"Top 热门板块列表"的 Top N（=3/5/10）需与 §3.1⑤ 虹吸态 HHI 的 N 协同

#### ⑪ 大盘水温→仓位控制映射（声明响应，不判水温）—— 待施工（与 regime 协同）

**裁定**：本 spec **不判定大盘水温**（水温判定归 regime [10_regime_detector_spec.md](10_regime_detector_spec.md) 12 态 + 情绪周期 [28_sentiment_cycle_trading.md](28_sentiment_cycle_trading.md) 5 阶段），只声明**板块信号对水温的响应映射**——不同水温下板块强度综合分的使用比例与放行门槛调整。

| 水温 | 仓位比例 | 板块信号响应 | 实证收益 |
|---|---|---|---|
| NEUTRAL | 100% | 全板块信号全权重，三级放行门槛 v2.1 标准执行 | 平均 +1.17%（唯一正收益） |
| RISK_ON | 50% | 板块信号权重 ×0.5，§3.1⑨ CONSENSUS_CLIMAX 时进一步抑制 | 平均 -1.54%（过热追高亏钱） |
| PANIC_REPAIR | 50% | 仅放行 §3.1④ RRG "改善"象限板块信号（超跌反弹候选） | 修复期，方向未确认 |
| RISK_OFF | 30% | 仅放行 §3.1⑦ 龙头识别×1.5 权重个股，其余拦截 | 弱市，质量优先 |
| CRASH | 0% | **全板块信号拦截**（不开仓） | 平均 -3.2%（空仓正确） |

- **核心结论**（[WyckoffTradingAgent 2026-04 实证](https://github.com/YoungCan-Wang/WyckoffTradingAgent/wiki/04_Finance_Sector_Rotation_Regime)）：选股选得好不如市场选得对，水温仓控是性价比最高的风控手段——NEUTRAL 唯一正收益（+1.17%）、RISK_ON 过热追高亏钱（-1.54%）、CRASH 空仓正确（-3.2%）
- **为何在本 spec 声明而非 regime spec**：水温→仓位比例归 regime/firm 层（[30_multi_strategy_concurrency §2.2](30_multi_strategy_concurrency.md) MOD-POS-021），水温→**板块信号响应**是板块 spec 的职责——regime 管总仓位，本 spec 管板块信号的水温适配（5 档而非 12 态的选型裁定见 §4.8）
- **水温 5 档与 regime 12 态映射**（待 G21/G30 校准，本 spec 不定）：NEUTRAL≈Bull-Medium/Neutral-Medium；RISK_ON≈Bull-Strong（过热）；PANIC_REPAIR≈BREAKOUT 失败/CRISIS 修复；RISK_OFF≈Bear-Weak/Medium；CRASH≈CRISIS。具体映射在 [10_regime_detector_spec.md](10_regime_detector_spec.md) §3 regime 12 态与本表 5 档的桥接需 G21 情绪周期×交易决策讨论
- **水温→板块信号响应算法（v1.6.0 补全公式级）**——将水温 5 档翻译为 3 类可执行调整：
  ```
  # 输入：水温档位 water_temp ∈ {NEUTRAL, RISK_ON, PANIC_REPAIR, RISK_OFF, CRASH}
  # 输出：signal_weight (float), gate_thresholds (dict), rrg_filter (str)

  if water_temp == NEUTRAL:
      signal_weight = 1.0                          # 全权重
      gate_thresholds = {"level2": 0.60, "level3": 0.80}   # v2.1 标准
      rrg_filter = "ALL"                           # 全象限放行
  elif water_temp == RISK_ON:
      signal_weight = 0.5                          # ×0.5 抑制
      gate_thresholds = {"level2": 0.60, "level3": 0.80}   # 阈值不变，靠权重抑制
      rrg_filter = "ALL"                           # 但 CONSENSUS_CLIMAX 时 watch_score 进一步抑制
  elif water_temp == PANIC_REPAIR:
      signal_weight = 0.5
      gate_thresholds = {"level2": 0.50, "level3": 0.70}   # 放宽（超跌反弹期）
      rrg_filter = "IMPROVING_ONLY"                # 仅放行 RRG 改善象限（超跌反弹候选）
  elif water_temp == RISK_OFF:
      signal_weight = 0.3
      gate_thresholds = {"level2": 0.80, "level3": 0.90}   # 收紧（仅强基本面个股）
      rrg_filter = "LEADING_ONLY"                  # 仅放行 RRG 领先象限 + 龙头×1.5
  elif water_temp == CRASH:
      signal_weight = 0.0                          # 全拦截
      gate_thresholds = {"level2": 1.01, "level3": 1.01}   # 不可达阈值=全拦截
      rrg_filter = "NONE"
  ```
  - **与 §3.1⑩ 三级门槛联动**：gate_thresholds 注入 §3.1⑩ 准入 gate 算法的动态阈值调整（§3.1⑩ 已声明联动关系，本算法给出具体阈值表）
  - **与 §3.1④ RRG 联动**：rrg_filter 在 RRG 象限→交易信号映射（§3.1④ 步骤4）的象限过滤层执行——PANIC_REPAIR 时仅"改善"象限板块信号放行，其余象限信号 weight=0
  - **与 §3.1⑨ 5 状态联动**：RISK_ON 档位下，若 5 状态 = CONSENSUS_CLIMAX，signal_weight 进一步 ×0.5（即 0.5×0.5=0.25，双重抑制过热追高）
  - **边界重申**：本算法只输出"板块信号响应"（signal_weight/gate_thresholds/rrg_filter），仓位比例（100%/50%/50%/30%/0%）归 regime/firm 层（[30_multi_strategy_concurrency §2.2](30_multi_strategy_concurrency.md) MOD-POS-021），两者分层不重叠
- **待施工**：水温 5 档与 regime 12 态的映射表（§7 待定问题）、本算法的实现（注入 §3.1⑩ 三级放行门槛的动态阈值 + §3.1④ RRG 象限过滤）

### 3.2 架构定义

```
sector_snapshot_collector (production) ──880xxx快照──┐
                                                     ├─→ sector_ranking_engine (production, 5因子排名Top99推送池)
                                                     │
                              sector_analyzer (production, 6维度结构强度)
                                                     │
                              [待施工] 轮动序列追踪(RRG) ──┤  ④
                              [待施工] 调整周期进度(扩散) ──┤  ③
                              [待施工] 虹吸态识别(HHI) ────┤  ⑤
                              [待施工] 短周期动量q3/q5/q20 ┤  ⑧ (多时间框架动量第三维)
                              [待施工] 5状态分类(watch_score)┤  ⑨ (市场级快照, 市场级加减分)
                                                     ▼
                              板块强度综合(三维: 结构+动量活跃+多TF动量 + watch_score调节)
                                                     │
                                                     ▼
                              [待施工] 三级放行门槛(准入gate) ──→ 回踩A/B/C+Fib+量能衰减 → BM-BUY-04买入优先级
                              (⑩ 核心热门直通/次优≥0.60/超强≥0.80)        ②
                                                     │
                                                     ▼
                              龙头识别(涨停时间/封单/带动) ──→ 板块→个股传导映射 → G05选股引擎
                              (龙头1.5×/中军1.2×/跟风0.8×/中位股0禁触, hot_bonus=0.02)  ⑦

  ===== 跨层协同（声明响应，不判水温） =====
  regime 12态 + 情绪周期5阶段 ──→ [待施工] 水温5档映射 ──→ 板块信号响应(全开/半开/修复/仅龙头/全关)  ⑪
                                  (NEUTRAL/RISK_ON/PANIC_REPAIR/RISK_OFF/CRASH)
```

板块信号只流向选股打分，**不进仓位分配层**（与 regime 边界一致，[30_multi_strategy_concurrency §2.2](30_multi_strategy_concurrency.md) MOD-POS-021 firm 层只做求和+裁剪，不读板块）。水温→仓位比例归 regime/firm 层，本 spec 只声明水温→板块信号响应映射（§3.1⑪）。

## 4. 考虑过的替代方案

### 4.1 460 板块全截面横向排名 vs 每板块独立趋势判断 —— 选混合
- **拒绝纯横向排名**：aminzheng/quant-sector-rotation 2026-06 实证"行业 ETF 驱动因素完全不同（政策/周期/技术/疫情），不可横向比较，只判断每个行业自身趋势方向"——纯横向排名在异质板块间失真
- **拒绝纯独立判断**：本项目需选 Top 99 推送池（实时性约束），必须横向比较
- **裁定混合**：`ranking_engine` 做横向排名选推送池（解决实时性），`analyzer` 做单板块结构判断（解决异质性）。两者不矛盾，分别服务不同决策

### 4.2 实时全量 460 板块强度 vs 盘后批量 + 实时 Top 99 —— 选后者
- **拒绝实时全量**：460 板块 × 6 维度实时计算是过载，且非情绪市多数板块无信号
- **裁定盘后批量 + 实时 Top 99**：`snapshot_collector` 已实现（推送 99 + 轮询全量 30 秒），`analyzer` 盘后批量算全量强度，实时预警只跑推送池 99 只。规避实时算 460×6 的过载

### 4.3 板块强度纯涨停梯队 vs 多因子复合 —— 选多因子复合
- **拒绝纯涨停梯队**：纯涨停数+梯队在非情绪市（震荡/冰点态）失效，主升态之外无信号
- **裁定多因子复合**：`analyzer` 结构强度（涨停梯队）+ `ranking_engine` 动量活跃度（成交额/涨跌幅/动量），覆盖结构+动量两维，全态适用

### 4.4 轮动序列：RRG vs 纯排名时序 vs lead-lag network —— 选 RRG
- **拒绝纯排名时序**：只看板块强弱排名变化，丢失"动量引领趋势"的领先信息，且转折点检测（CUSUM/变点）需额外选型、滞后
- **拒绝 lead-lag network（Granger/transfer entropy）**：追踪板块间信息流向更深刻，但需多板块两两因果检验、参数多、个人项目过重——列为第三阶段增强
- **裁定 RRG**：Julius de Kempenaer 2004-2005 专为板块轮动设计，RS-Ratio（趋势）+ RS-Momentum（动量领先）双轴四象限顺时针旋转即轮动序列，A股有实证（西部金工 2026-05 年化 20.60%）；RS-Momentum 天然提供领先信号，无需额外转折点检测

### 4.5 板块一日游应对：q3 短周期动量 vs 纯排名时序加速 vs 机器学习转折点检测 —— 选 q3 加权
- **拒绝纯排名时序加速**（缩短排名窗到 3 日）：纯 3 日排名会沦为噪声，丢失中期趋势锚定，且不解决"板块持续领涨"假设本身的问题
- **拒绝机器学习转折点检测**（CUSUM/变点/HMM）：[华泰金工 2026-03](https://finance.sina.com.cn/wm/2026-03-17/doc-inhrfwqa9598438.shtml) 残差动量+遗传规划样本外年化超额 25.39%，但需 GPU 加速 + 多目标体系 + 大样本训练，个人项目过重——列为第三阶段增强
- **裁定 q3 加权**（§3.1⑧）：在现有 strength = 0.7×q20 + 0.3×q5 基础上叠加 q3，新版 0.4×q20 + 0.3×q5 + 0.3×q3。[WyckoffTradingAgent v2.1.x 2026-04 实证](https://github.com/YoungCan-Wang/WyckoffTradingAgent/wiki/04_Finance_Sector_Rotation_Regime) Top3 次日重合率 14.8% 下，q3 是最快感知方向变化的因子；不替换 production 双模块，作为第三维补充叠加，工程量可控

### 4.6 轮动状态分类：5 状态 vs 二分类（热/冷）vs regime 12 态直接映射 —— 选 5 状态
- **拒绝二分类**：丢失"健康主线（应加分）vs 共识高潮（应重扣）"区别，两者都是"热"但 watch_score 方向相反
- **拒绝 regime 12 态直接映射**：regime 12 态是指数级市场状态（Bull/Bear/Neutral/BREAKOUT/CRASH），不区分"板块间分布结构"；5 状态专攻板块间分布（多板块同暴涨 vs 单主线 vs 分化），与 regime 正交不重叠
- **裁定 5 状态**（§3.1⑨）：CONSENSUS_CLIMAX / DISAGREEMENT_PULLBACK / HEALTHY_MAINLINE / DISTRIBUTION_RISK / NEUTRAL_MIXED——5 状态覆盖"主线持续/见顶风险/派发/分歧/混沌"5 种板块结构，watch_score 有正有负（+0.03 到 -0.10），[WyckoffTradingAgent 2026-04 实证](https://github.com/YoungCan-Wang/WyckoffTradingAgent/wiki/04_Finance_Sector_Rotation_Regime) CONSENSUS_CLIMAX 后 3 日下跌>2% 概率 29.8% 支撑重扣

### 4.7 板块→个股准入：三级放行门槛 vs 统一个股强度阈值 vs 纯板块白名单 —— 选三级放行
- **拒绝统一阈值**（不分板块归属，全市场按个股强度排序）：丢失板块alpha，个股强度高但板块弱势时易接飞刀
- **拒绝纯板块白名单**（只放行 Top 热门板块内个股）：板块一日游下（Top3 重合率 14.8%），纯白名单会错过"今日非热门、明日启动"的板块好股票
- **裁定三级放行**（§3.1⑩）：核心热门直通 + 次优板块+个股强度≥0.60 + 超强个股≥0.80——既保留板块 alpha（热门直通），又留出非热门启动通道（次优+强度），再加超强个股通配（领先板块启动的领涨个股）。v2.1 阈值较 v2.0 降低（0.70→0.60 / 0.90→0.80）应对一日游

### 4.8 水温仓控映射：5 档映射 vs regime 12 态直接映射 vs 连续比例 —— 选 5 档映射
- **拒绝 regime 12 态直接映射**：12 态过细，板块信号响应只需"全开/半开/修复/仅龙头/全关"5 档粒度；12 态直接映射会引入 12 套响应规则，过度工程
- **拒绝连续比例**（仓位比例 = f(regime 概率) 连续函数）：连续比例归因不清，亏钱时分不清是"水温判错"还是"响应函数调错"；离散 5 档便于 log 与复盘（[30 §1.3](30_multi_strategy_concurrency.md) 归因清晰度是生存项）
- **裁定 5 档映射**（§3.1⑪）：NEUTRAL 100% / RISK_ON 50% / PANIC_REPAIR 50% / RISK_OFF 30% / CRASH 0%——[WyckoffTradingAgent 2026-04 实证](https://github.com/YoungCan-Wang/WyckoffTradingAgent/wiki/04_Finance_Sector_Rotation_Regime) NEUTRAL 唯一正收益（+1.17%）、CRASH 空仓正确（-3.2%）。**边界声明**：水温判定归 regime（[10_regime_detector_spec.md](10_regime_detector_spec.md)），本 spec 只声明板块信号对水温的响应

## 5. 上限定义

### 5.1 系统上限
- **采集上限**：880xxx + 881xxx 全覆盖（实测 582 只 = 454 + 128），推送池 Top 99 实时，其余轮询 30 秒——已是 `snapshot_collector` production 事实
- **计算上限**：板块强度盘后批量全量 + 实时预警仅推送池 99 只
- **传导上限**：板块→个股单向（板块强度作为个股 score 加权维度），不做个股→板块反向推断

### 5.2 演进路径
- **第一阶段（立即）**：复用 production（`snapshot_collector` / `ranking_engine` / `analyzer`）提供板块强度 + 资金流 + 单板块轮动预警
- **第二阶段（G05 选股引擎施工前）**：补 BM-SEL-08 轮动序列 + 回踩 A/B/C、BM-SEL-09 调整周期进度；**叠加 §3.1⑧ q3 短周期动量**（一日游应对，从 `market_kline_sector_880` 日K 计算 3 日涨跌幅，工程量小）+ **§3.1⑨ 5 状态分类**（盘后规则判定，无需新数据源）
- **第三阶段（G05 施工中）**：补虹吸态识别 + 板块→个股传导映射 + **§3.1⑩ 三级放行门槛**（准入 gate，依赖 G05 个股强度分）+ **§3.1⑪ 水温响应映射**（依赖 regime 12 态与水温 5 档桥接，需 G21 协同）
- **第四阶段（增强，非必需）**：lead-lag network（Granger/transfer entropy）+ 机器学习转折点检测（华泰残差动量+遗传规划思路）+ **板块相关聚类**（v1.6.0 新增登记，原缺口"无板块相关性聚类算法"），个人项目过重，列为远期增强

#### 5.2.1 板块相关性聚类算法（v1.6.0 新增，第四阶段增强）

> **缺口背景**：v1.5.0 前无板块相关性聚类算法——[Amundi 2026-07-28](https://research-center.amundi.com/article/global-investment-views-august-2026) 实证"low cross-sector correlation"随轮动加剧（sector-specific drivers 主导），意味着轮动期板块间相关性下降、独立驱动增强；聚类算法可识别"同涨同跌板块簇"vs"独立驱动板块"，为 RRG 轮动序列提供结构化分组输入。

- **算法草案**（第四阶段，非首轮）：
  ```
  # 步骤 1：计算 460+ 板块两两收益率相关系数矩阵 C (460×460)
  C[i][j] = corr(ret_sector_i, ret_sector_j)  # 滚动窗口 60 日

  # 步骤 2：层次聚类（hierarchical clustering，ward linkage）
  clusters = hierarchical_clustering(C, method="ward", n_clusters=8~12)

  # 步骤 3：聚类输出用途
  # ① 同簇板块 = 同涨同跌候选（RRG 象限应同步，若不同步=轮动信号）
  # ② 跨簇板块 = 独立驱动（虹吸态切换的候选方向，§3.1⑤）
  # ③ 聚类稳定性 = 轮动节奏指标（聚类结构剧变=风格切换，§3.1⑨ 5 状态）
  ```
- **为何列为第四阶段而非首轮**：① 460×460 相关矩阵计算量较大（虽盘后批量可承受）② 聚类结果解释需人工校验 ③ 首轮 RRG+q3+5 状态+三级门槛已覆盖核心轮动感知，聚类是结构化增强非必需
- **与 lead-lag network 关系**：lead-lag network 追"信息流向"（谁领先谁），聚类追"同步性"（谁和谁同涨同跌）——两者互补，第四阶段共同实施

### 5.3 为何这是上限而非妥协
- 460 全覆盖是采集层已有事实（`snapshot_collector` production），**不是新增负担**——强度计算是纯函数盘后批量，460×6 维度秒级
- 实时只 Top 99 推送池，规避实时全量过载
- 对标国海 2026-07 只看 31 个申万一级行业，本项目 880xxx 细分到 454 是更细粒度，但采集层已解决、计算层按需，非过载

> **过度工程审查回执（v1.9.2，2026-08-12 第 5 轮，判定基准=[system_charter §2 硬边界](../../04_architecture_principles_decisions/system_charter.md)）**：
> ①**460 板块全覆盖是否过重（MVP 是否只需 50-100 个重点板块）**——**裁定：不过重，且"Top99 推送池动态选取"已是比静态 50-100 列表更优的答案**。582 只板块数据是 `sector_snapshot_collector` production 的存量事实（§2.5 盘点），盘后全量计算是纯函数秒级；实时计算只跑动态 Top99 推送池——推送池本质就是"重点板块"，但由 5 因子排名每日动态选出，比人工圈定 50-100 个静态名单更能适应轮动（§2.4 电风扇行情周度排名变化 12.75 下，静态名单一周即失效）
> ②**板块→个股传导多层逻辑是否过重**——**裁定：不过重，全部是规则层 if-else 无 ML**。§3.1⑦ 传导两步（龙头识别→加权传导）+ §3.1⑩ 准入 gate 共三层，每层都是阈值规则（涨停时间排序/封单量比/0.60/0.80 门槛），无模型训练、无 GPU 依赖、单机毫秒级；§5.2 已分层——MVP 第一阶段仅复用 production 三模块，⑩⑪ 依赖 G05/G21 就绪后才施工， staged 交付控制复杂度
> ③**重机制全部在第四阶段/暂缓**：lead-lag network（Granger/transfer entropy）、华泰残差动量+遗传规划 ML 转折点检测、板块相关性聚类（§5.2.1）、GRU/Transformer 行业预测（§8.4 对标但拒绝引入）——全部显式标注第四阶段增强或已拒绝，按审查规则"远期工程不算过度工程"予以保留

## 6. 待裁定

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| 回踩 A/B/C 剩余阈值 | Fib 回撤位+量能衰减已定（§3.1②），swing high/low 选取规则、量能衰减具体百分比、regime→风险预算映射表待校准 | G05/G08 施工时校准 |
| 龙头识别阈值 | 涨停启动时间/封单厚度/带动效应的量化阈值 + 龙头/中军/跟风/中位股分类边界待 2026 实盘标定 | G05/G08 施工时校准 |
| 板块→个股传导乘数 | 龙头1.5/中军1.2/跟风0.8/中位股0 为初拟，需回测验证 | G05 选股引擎回测阶段 |
| 轮动序列算法 | RRG 主算法已定（§3.1④），v1.6.0 已补全 JdK DualEma 公式级计算（10/26 EMA，最小62日）+ 象限→信号映射 + whipsaw 确认；EMA 短/长窗口（10/26 vs 西部金工 220+MA20）需本项目 880xxx 日频回测校准；lead-lag network 第四阶段增强 | 第二阶段施工时 |
| 虹吸态 HHI 参数 | 头部 N 板块数（N=3/5/10）、z-score 阈值、三者加权权重需 2026 实盘标定 | 有 ≥3 个月虹吸态样本后 |
| q3/q5/q20 权重标定 | §3.1⑧ 权重 0.4/0.3/0.3 为初拟（WyckoffTradingAgent v2.1.x 移植），需 G05 回测验证是否适配本项目 880xxx 细分板块（vs 申万 L1 31 行业） | G05 选股引擎回测阶段 |
| 5 状态判定阈值 | §3.1⑨ v1.6.0 已给初拟阈值（hhi_top5: 0.20/0.25/0.30，up_ratio: 0.40/0.70，lead_streak: 3，legulegu/rebuildingsociety 2026 依据），需 2026 实盘标定 | 有 ≥3 个月状态分类样本后 |
| 三级放行门槛 v2.1 阈值 | §3.1⑩ 阈值 0.60/0.80 为 v2.1 初拟，需 G05 回测验证（vs v2.0 的 0.70/0.90）；Top 热门板块 N 值需与虹吸态 HHI 的 N 协同 | G05 选股引擎回测阶段 |
| hot_bonus 0.02 标定 | §3.1⑦ hot_bonus 从 0.05 降至 0.02 为 WyckoffTradingAgent 移植值，需本项目 880xxx 板块回测验证 | G05 选股引擎回测阶段 |

## 7. 待定问题

| 开放问题 | 出处 | 决策状态 |
|---|---|---|
| 回踩 A/B/C 与 G08 打板情绪周期 4+1 阶段的边界 | 本 spec §3.1② / G21 | 待 G21 情绪周期×交易决策讨论 |
| 虹吸态与 regime 12 态的耦合（虹吸态是否只在主升/疯狂态出现） | 本 spec §3.1⑤ / [30 §1.3](30_multi_strategy_concurrency.md) | 待 2026 实盘数据验证 |
| 板块强度在 G05 选股引擎中的具体加权方式 | 本 spec §3.1⑦ / G05 | 待 G05 选股引擎架构讨论 |
| **水温 5 档与 regime 12 态的桥接映射** | 本 spec §3.1⑪ / [10_regime_detector_spec.md](10_regime_detector_spec.md) / [28_sentiment_cycle_trading.md](28_sentiment_cycle_trading.md) | 待 G21 情绪周期×交易决策讨论（regime 12 态 + 情绪周期 5 阶段 → 水温 5 档的聚合规则） |
| **5 状态分类与 regime 12 态的正交性验证** | 本 spec §3.1⑨ / [10_regime_detector_spec.md](10_regime_detector_spec.md) | 待 2026 实盘数据验证（5 状态是否在多个 regime 态下独立变化，还是强耦合） |
| **三级放行门槛与 G05 选股引擎漏斗的衔接** | 本 spec §3.1⑩ / G05 | 待 G05 选股引擎架构讨论（准入 gate 在漏斗哪一层执行） |
| **20 号 §2.5 差异化矩阵补"板块信号"维度行** | 本 spec §2.1 v1.9.0 审查发现：板块信号消费关系真实出处是 20 号 §2.2-2.4 各节 + §7.2，§2.5 矩阵 8 行维度无板块行；且 §7.4 下游交接列表（G05/G07/G08/G09/G10）未含 G06 | 待 20 号 owner 下次修订时补登（建议 §2.5 矩阵加"板块信号消费"行 + §7.4 交接列表补 G06）。按审查约束不越界改 20 号，登记于此 |
| **MOD-L00-004 blueprint 补板块采集节** | 本 spec §2.1 v1.9.0 审查发现：blueprint 无 §sector_snapshot/§sector_ranking 节（此前引用为假锚点），且 `sector_kline_downloader.py` 代码头 `# [BLUEPRINT] MOD-L00-004 ... §sector_kline` 同样指向不存在的节 | 待 MOD-L00-004 owner 补登板块采集三节（或代码头改引 11_d_data）。按审查约束不越界改，登记于此 |
| **41 号对 22 号两处引用过期/ID 笔误** | v1.9.2 第 6 轮一致性审查发现：[41_buy_flow](41_buy_flow.md) L130 将"调整周期到位（进度≥80%）"标为 **BM-SEL-03**（应为 **BM-SEL-09**，BM-SEL-03 是市场状态感知）；L44/L511 称回踩 A/B/C"目前是骨架"——v1.6.0 起 §3.1② 已是公式级量化算法（Fib+量能衰减+时间窗+regime 适配），"骨架"表述过期 | 待 41 号 owner（sess-37-41-review 活跃施工中）修正 BM-SEL ID 笔误并更新 A/B/C 状态表述。按审查约束不越界改 41 号，登记于此 |

## 8. 引用

### 8.1 相关设计备忘
- [20_first_batch_strategies.md](20_first_batch_strategies.md) §2.5 差异化矩阵（G04，三策略均消费板块信号）、§7.4 下游交接（G06 是 G08/G09/G10 前置）
- [21_stock_selection_engine.md](21_stock_selection_engine.md) G05 选股引擎（§3.1⑦ 板块→个股传导映射的消费方、§3.1⑩ 三级放行门槛的准入 gate 执行层、§3.1⑪ 水温响应的 signal_weight 注入点）——本 spec 声明板块信号方向与算法，G05 定义个股打分漏斗与具体加权方式
- [25_multifactor_strategy_detail.md](25_multifactor_strategy_detail.md) G09 多因子策略（§3.1⑩ "个股强度"= G05/G09 多因子综合分 0-1 归一化的来源；拥挤度因子与 §3.1⑤ 虹吸态 HHI / §3.1⑨ 5 状态 hhi_top5 概念同源但粒度不同——G09 拥挤度是因子级截面打分，本 spec HHI 是板块结构级集中度）——v1.6.0 新增引用，明确板块信号与多因子打分的边界
- [30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md) §1.3 情绪周期隐形驱动（虹吸态依据）、§2.2 firm 层不读板块（正交边界）
- [10_regime_detector_spec.md](10_regime_detector_spec.md) §3 regime 12 态（§3.1⑪ 水温 5 档映射的上游，本 spec 不判水温只声明响应）
- [28_sentiment_cycle_trading.md](28_sentiment_cycle_trading.md) §3.1 情绪周期 5 阶段（冰点/反核/主升/疯狂/退潮，§3.1⑪ 水温 5 档映射的另一个上游）
- [00_index_trading_decision.md](00_index_trading_decision.md) §3 G06 讨论框架

### 8.2 相关作战地图
- [battle_map_05_stock_selection.md](../battle_map/battle_map_05_stock_selection.md)
  - BM-SEL-08 板块轮动序列追踪（轮动序列 + 回踩 A/B/C，锚点 MOD-SIG-026 supplement production，序列逻辑缺失态-未实现）
  - BM-SEL-09 调整周期追踪（MOD-SIG-040 primary planned，进度≥80%激活分批）

### 8.3 depgraph 模块（引用稳定 path / blueprint_id）
| 模块 | blueprint_id | path | 本 spec 关系 | build_status |
|---|---|---|---|---|
| SectorAnalyzer | MOD-SIG-026 | `src/zephyr/signal_ashare/sector_analyzer.py` | 板块强度/轮动预警/资金流（复用） | production |
| SectorRankingEngine | MOD-L00-004 | `src/zephyr/data/sector_ranking_engine.py` | 5 因子排名选推送池（复用） | production |
| SectorSnapshotCollector | MOD-L00-004 | `src/zephyr/data/sector_snapshot_collector.py` | 880xxx 快照采集（复用，§3.1⑧ q3 数据源） | production |
| 调整周期进度追踪 | MOD-SIG-040 | `src/zephyr/signal_ashare/`（待施工） | BM-SEL-09 进度算法 | planned |
| 轮动序列/回踩A/B/C/虹吸态/传导映射 | — | 待登记 | BM-SEL-08 序列逻辑 + §3.1②⑤⑦ | proposed |
| 短周期动量 q3/q5/q20 加权 | — | 待登记（"板块强度综合"层内） | §3.1⑧ 多时间框架动量第三维 | proposed |
| 板块轮动状态 5 分类 | — | 待登记 | §3.1⑨ 市场级快照 + watch_score | proposed |
| 三级放行门槛（准入 gate） | — | 待登记（G05 选股引擎消费） | §3.1⑩ 板块→个股准入 | proposed |
| 水温→板块信号响应映射 | — | 待登记（与 regime 协同） | §3.1⑪ 声明响应，不判水温 | proposed |

### 8.4 开源实证参考（2026）
- [国海固收颜子琦 2026-07 — 转债行业景气度轮动选券策略](https://finance.sina.com.cn/wm/2026-07-12/doc-inihnhat4899827.shtml)：5 项量化指标月度景气度打分 TOP5-10，2020-2026 累计 134% 年化 23% 夏普 1.45；明确指出"AI 产业链对场内资金形成持续虹吸"——§3.1⑤ 虹吸态的 2026 实证依据
- [aminzheng/quant-sector-rotation 2026-06](https://github.com/aminzheng/quant-sector-rotation)：行业 ETF 各自独立 MA 趋势信号，不做截面排名，2026 +15.5% vs 等权 +2.4%——§4.1 拒绝纯横向排名的实证依据
- [dananalytics 2026-04 — Sector Rotation Strategies](https://dananalytics.com/en/sector-rotation/)：relative strength momentum ranking，1/3/6 月 lookback，buy top 2-4/11——§3.1 排名思路对标
- [vextorcapital 2026-06 — Sector Rotation Across Economic Cycle](https://vextorcapital.com/learn/macro/sector-rotation)：rotation 作为季度战术倾斜而非频繁交易——§5.1 实时只 Top 99 的频率依据
- [西部金工 2026-05 — RRG 框架下的行业和 ETF 轮动策略](https://finance.sina.com.cn/wm/2026-05-27/doc-inhziqxn8446705.shtml)：RRG（RS-Ratio+RS-Momentum 双轴四象限）+ 扩散指标做中信一级行业轮动，2018.12-2026.03 年化 20.60%（超额 9.49%），RRG 弥补扩散指标在震荡市/快轮动期滞后——§3.1④ RRG 主算法与 §3.1③ 扩散指标对应的 A 股实证依据
- [usanewsgroup 2026-08-04 — Sector Rotation](https://usanewsgroup.com/the-signal-savvy-investors-watch-more-than-any-stock-sector-rotation/)：RRG 四象限顺时针旋转捕捉板块领导力切换，rotation 领先经济数据数周——§3.1④ RRG 轮动序列可视化依据
- [closelook — Sector Relative Strength 2026-08-07](https://closelook.net/lab/patterns/sector-rs/)：RS-ratio 标准化到 100 + 21d/63d/252d 三时间框架独立排序 + Z-score 均值回归叠加（|Z|>2=反转候选，跨象限修正）——§3.1④ RRG 增强（Z-score+多时间框架）依据，2026-08-07 最新实践
- [kriterionquant — RRG Sector Rotation Study 2026-01](https://kriterionquant.com/wp-content/uploads/2026/01/RRG_Dashboard_Complete_11_January_2026.html)：whipsaw 假信号警告（象限间快速来回）+ transition matrix 量化象限转移概率——§3.1④ RRG whipsaw 风险+确认机制依据
- [State Street — Sector Momentum Map 2026-03](https://www.ssga.com/at/de/intermediary/insights/guide-to-sector-momentum-map)：JdK RS-Ratio/RS-Momentum 定义 + 强趋势半圆旋转例外（领先→疲软→领先，不经过滞后/改善）——§3.1④ RRG 旋转路径容错依据
- [eciks — Investors Rotate Out of Tech into Value/Financials 2026-08-05](https://eciks.org/18864-24486-invest-rotation-tech-value-financials)：2026-08 真实轮动（tech→financials/value/industrials，金融+10-14%/能源+22% YTD），"coiled spring"盘整后突破——§3.1④ RRG 轮动序列 2026-08 实盘验证
- [Amundi — Global Investment Views August 2026 2026-07-28](https://research-center.amundi.com/article/global-investment-views-august-2026)："low cross-sector correlation"随轮动加剧（sector-specific drivers 主导）——§3.1③ 扩散指标 + §3.1④ RRG 在低跨板块相关期更有效的实证
- [QuantStreet — Sector Rotation Continues 2026-08-05](https://www.advisorperspectives.com/commentaries/2026/08/05/quantstreet-sector-rotation)："Adding Dispersion to the Rotation Graph"——RRG + dispersion（=扩散指标）并用，与本项目 §3.1③ 扩散指标 + §3.1④ RRG 双模块架构一致，2026-08 机构实践验证
- [BreakoutBulletin — Pullback Trading Strategy 2026](https://breakoutbulletin.com/article/pullback-trading-strategy-fibonacci-guide-2026)：Fibonacci 38.2/50/61.8/78.6% 回撤位分级 + 量能衰减确认 + Grade A/B/C + regime 仓位适配（2026 selective risk-off 应瞄准 50/61.8%），n=934 回测——§3.1② 回踩 A/B/C 量化算法依据
- [Prodigy — Why Pullbacks Fail 2026](https://prodigytradingteam.com/blogs/trading-blog/why-pullbacks-fail-fake-dips-trend-traps-2026)：健康回踩=缩量递减+支撑有效，陷阱回踩=放量+破结构；量能衰减序列 Day6:80%→Day9:35%——§3.1② 量能衰减量化依据
- [东方财富 — 龙头股的确认 2026-05](https://caifuhao.eastmoney.com/news/20260523093657718991640)：龙头识别"两个领先"（涨幅+成交额）+ 率先启动/抗跌 + 中军 vs 情绪龙分类——§3.1⑦ 龙头识别前置流程依据
- [55188 — 龙头中军核心定义指标 2026-04](https://www.55188.com/thread-38870280-1-1.html)：龙头/中军/中位股/抱团票/核心 五类定位精确定义，中位股（3-5板跟风）明确为"死亡区域"禁触——§3.1⑦ 个股定位分级与中位股禁区依据
- [新浪 — 辨识度人气龙头7标准 2026-05](https://www.sina.cn/news/detail/5294851223978344.html)：标签单一/走势独立/成交Top3/情绪卡位/龙虎榜抱团/历史股性/关键位置——§3.1⑦ 龙头识别量化指标依据
- [雪球 — A股打板炸板率深度量化 2026-02](https://xueqiu.com/2118496927/376795876)：全市场平均炸板率 24.6%，龙头 8% vs 跟风 32% vs 孤板 58%；情绪亢奋期≤15%/平衡期15-30%/衰退期≥30%——§3.1① 板块内封板率情绪温度修正因子依据
- [东方财富 — A股情绪周期判断体系 2026-03](https://caifuhao.eastmoney.com/news/20260314093054692373420)：5 大核心指标（涨停家数+连板高度/跌停+核按钮/炸板率/赚钱效应/板块联动）+ 四周期判定——§3.1① 板块情绪温度与 G21 市场情绪温度边界划分依据
- [WyckoffTradingAgent wiki v2.1.x 2026-04 — 板块轮动与大盘水温](https://github.com/YoungCan-Wang/WyckoffTradingAgent/wiki/04_Finance_Sector_Rotation_Regime)：A 股板块一日游实证（申万 L1 31 行业 2025-10~2026-04，Top3 次日重合率 14.8%/Top3 完全不同 63.2%/领涨仅 1 天 46.6%）+ hot_bonus 0.05→0.02 + q3 短周期动量（strength 0.4×q20+0.3×q5+0.3×q3）+ 5 状态分类（CONSENSUS_CLIMAX/DISAGREEMENT_PULLBACK/HEALTHY_MAINLINE/DISTRIBUTION_RISK/NEUTRAL_MIXED）+ 三级放行门槛 v2.1（0.70→0.60 / 0.90→0.80）+ 水温 5 档仓控（NEUTRAL 100%/RISK_ON 50%/PANIC_REPAIR 50%/RISK_OFF 30%/CRASH 0%，NEUTRAL +1.17% 唯一正收益、CRASH -3.2% 空仓正确）——§2.3 一日游约束 + §3.1⑦ hot_bonus + §3.1⑧ q3 + §3.1⑨ 5 状态 + §3.1⑩ 三级门槛 + §3.1⑪ 水温仓控 的核心实证依据
- [华泰金工 2026-03 — 量化行业轮动的"崎岖之路"](https://finance.sina.com.cn/wm/2026-03-17/doc-inhrfwqa9598438.shtml)：残差动量因子（2017-2026 年化超额 12.90%）+ 拥挤度预警（4 量价指标门限，2026 初成功预警军工/工业金属/贵金属）+ 遗传规划动态因子挖掘（技术面样本外年化超额 25.39%，GPU 加速）——§4.5 拒绝机器学习转折点检测（个人项目过重）+ 第三阶段增强依据
- [国信证券 2026-06 — AI Agent 赋能开发行业轮动策略](https://pdf.dfcfw.com/pdf/H3_AP202606161823592020_1)：Codex 无监督开发行业轮动（60% 行业 40% 国债，2019-2026 年化 12.29% 夏普 1.04）+ Agent 共研 RRG（1000+ 风控规则网格搜索，2019 起年化 20.64% 夏普 1.339）——§3.1④ RRG 主算法的 AI Agent 实践验证 + §4.5 轻量化对照（国信用 1000+ 规则网格，本项目只用 RRG+Z-score+三时间框架）
- [东吴证券 2026-03 — 深度学习系列之二：技术形态专家模型](https://www.fxbaogao.com/detail/5316170)：GRU K 线专家模型，截面 IC 9.14%/时序 IC 10.25%，中信一级行业轮动 3 年化超额 12.60% 收益回撤比 2.12——§4.5 机器学习路径行业对标（个人项目不用 GRU，但多周期融合印证 §3.1⑧ q3/q5/q20 + §3.1④ RRG 三时间框架）
- [华泰金工 2026-06 — AI 行业轮动模型持续推荐金融](https://finance.sina.com.cn/wm/2026-06-15/doc-inicmsvf5192691.shtml)：全频段量价融合因子 32 行业周频调仓 5 行业等权，2017 初回测年化 26.43% 超额 19.96%，2026 YTD 10% 超额 12.75%——§3.1① ranking_engine 5 因子复合的行业对标（华泰用深度学习全频段融合，本项目用 5 因子线性复合，个人项目轻量化）
- [华泰金工 2026-07 — 全球风格轮动进行时](https://finance.sina.com.cn/wm/2026-07-05/doc-inifupeq2382499.shtml)：遗传规划行业轮动（33 中信行业，季频因子+周频调仓，2026 推荐 汽车/电新/有色/社服/通信）+ 大小盘均值回归动能较强（大盘拥挤度高位）——§2.4 2026-08 市场实证对照（高低切换、小盘弹性强于大盘）的行业研报依据
- [2026-08-10 十大券商看后市 — A 股仍处上行周期]：7 月大幅回调后单边行情难再现，板块/风格再平衡需求提升；超跌反弹有演绎空间，小盘弹性显著强于大盘；8 月中下旬中报密集期检验反弹成色；高低切换已成定局（科技兑现、周期加仓，煤炭/有色/化工/贵金属资金净流入前四）——§2.4 2026-08 A 股市场实证对照依据
- [国家统计局 2026-08-09 — PPI 数据]：PPI 连续三个月环比上行，工业产品价格底部确认；沪铜社会库存 7.8 万吨创五年新低，电解铝连续 11 周去库——§2.4 库存周期见底 + 周期板块进入 RRG "改善"象限的宏观依据
- [xkqg/MatPlotLibNet 2026-05 — RelativeRotationSeries]：RRG JdK DualEma 标准公式实现（RS=100×Asset/Bench，RS-Ratio=EMA(RS,10)/EMA(RS,26)×100，RS-Momentum=EMA(RS-Ratio,10)/EMA(RS-Ratio,26)×100，最小数据量 longPeriod×2+shortPeriod=62 bars，TailLength=8）+ Absorption/ENB overlay——§3.1④ RRG 计算算法（公式级）的核心实现依据
- [quantifiedtrader 2026 — RRG US Equity]：RRG 数学框架（z-score 归一化 RS-Ratio=100+z(RS,w=14)，RS-Momentum=100+z(ΔRS-Ratio,w=14)）+ 角度追踪（θ=atan2(y,x)，r=√(x²+y²) 衡量信号强度）+ 象限转移比静态象限更有信息量 + RS-Ratio 选股+RS-Momentum 定时的分离解耦——§3.1④ RRG Z-score 备选归一化 + 旋转路径追踪（步骤5）依据
- [stockwirex 2026-05-18 — Relative Rotation Graph Maps Sector Momentum]：RRG 四象限→配置权重量化映射（Leading 超配、Improving 早期超配）+ 200 日 MA 过滤器作为绝对趋势盲点 gate（RRG 是相对强度诊断，不保证绝对上涨）+ 2026-05 Technology 49.4%/Energy 13.2% 配置案例——§3.1④ RRG 象限→交易信号映射的实践依据
- [legulegu 2026-08-07 — 市场结构行业热度]：HHI（前5%个股行业占比平方和）+ 轮转速度（0.5×Σ|今日占比−昨日占比|）+ 行业超配率（前5%占比−全市场占比）三指标体系，P10/P90 分位参考线——§3.1⑨ 5 状态判定算法 hhi_top5/rotation_speed 指标与阈值依据，2026-08-07 最新
- [rebuildingsociety 2026-06 — SME Loan Portfolio Concentration]：HHI 阈值标准（<0.15 分散 / 0.15-0.25 监控 / >0.25 预警）+ Gini 系数 + Top-Borrower Exposure 三类集中度指标——§3.1⑨ 5 状态 hhi_top5 阈值（0.20/0.25/0.30）的产业经济学依据
- [Goldman Sachs 2026-08-03 — Momentum, rotation and the value in growth]：2026 市场参与度拓宽（S&P 等权 7 年来首次跑赢市值加权 7.3%）+ 动量 unwind 支持领导力轮动 + 收益增长成为回报主驱动（非估值扩张）——§2.4 2026-08 高低切换 + §3.1④ RRG 轮动序列 2026-08 全球宏观依据
- [中信建投 2026-08-02 — 行业轮动月报]：因子动量思想复合行业轮动（宏观/财务/分析师预期/ETF份额/基金仓位/事件动量 7 子维度），2012 年来多头年化超额 19.9% 月度胜率 70%，2026-08 推荐 电子/通信/机械/基础化工/计算机——§3.1① ranking_engine 5 因子复合的多子维度对标（中信建投用 7 子维度，本项目用 5 因子，个人项目轻量化）
- [中信证券 2026-08-10 — 超跌反弹阶段拥挤度三视角]：持仓成本（存续加权筹码模型，浮亏压力集中于科技成长与小微盘）+ 融资盘出清（领涨方向出清进度过半）+ 拥挤度（科技板块交投热度未回落）三视角量化评估热门板块修复进度——§3.1⑨ 5 状态 DISTRIBUTION_RISK 派发识别 + §3.1⑤ 虹吸态 2026-08 实盘校准依据
- [NikitaPatil7 2026 — AI Sector Rotation Portfolio Optimization]：LSTM vs Transformer 行业轮动预测对比（Transformer RMSE=0.0507 R²=0.9455 优于 LSTM RMSE=0.0825 R²=0.8479）+ Q-Learning 经济相位→板块超配 + MPT 夏普优化——§4.5 拒绝机器学习转折点检测（个人项目过重）的 AI 对标，第四阶段增强参考
- [ijicic 2022 — Attention LSTM Industry Rotation]：注意力 LSTM 多因子数据集（行业动量/成分股行为/盈利/港股资金流）行业轮动预测 77% 准确率——§4.5 机器学习路径行业对标（本项目不用 Attention LSTM，但多因子融合思路印证 §3.1① ranking_engine 5 因子复合）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G06 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 骨架→active 回填 | 7 项讨论要点逐项裁定：①板块强度复用 analyzer+ranking 双模块 ②回踩 A/B/C 待施工 ③调整周期 MOD-SIG-040 待施工 ④轮动序列待施工 ⑤虹吸态待施工（2026 国海实证 AI 虹吸）⑥资金流复用 ⑦传导映射待施工；过度工程审查（460 全覆盖=采集层 production 事实非新增，实时只 Top 99）；2026 开源实证（国海/aminzheng/dananalytics/vextor）；§4 三项替代方案裁定；§6 四项待裁定 |
| 2026-08-10 | 1.1.0 | 算法深化（2026-08 最新实践审查） | ④轮动序列主算法改为 RRG（相对旋转图，RS-Ratio+RS-Momentum 双轴四象限顺时针旋转=轮动序列可视化），替代原"排名时序+转折点检测"，西部金工 2026-05 A股实证年化20.60%支撑；③调整周期明确"扩散指标"对应+回撤深度备选；⑤虹吸态识别引入 HHI 赫芬达尔指数量化集中度；§4.4 新增 RRG vs 纯排名时序 vs lead-lag network 替代方案裁定；§8.4 加西部金工/usanewsgroup 2026-08 引用 |
| 2026-08-10 | 1.2.0 | 施工流程/算法量化补全 | ②回踩 A/B/C 从定性改量化（Fibonacci 38.2/50/61.8/78.6% 回撤位 + 量能衰减序列 Day6:80%→Day9:35% + regime 仓位适配，BreakoutBulletin/Prodigy 2026 依据）；⑦板块→个股传导补"龙头识别前置"环节（涨停启动时间/封单/带动效应 + 龙头1.5×/中军1.2×/跟风0.8×/中位股0禁触，东方财富/55188/新浪 2026 依据）；§3.2 架构图加龙头识别步骤；§6 待裁定加龙头识别阈值；§8.4 加 BreakoutBulletin/Prodigy/东方财富/55188/新浪引用 |
| 2026-08-10 | 1.3.0 | 施工细节/情绪温度补全 | ①板块强度加"情绪温度修正因子"（板块内封板率，雪球 2026-02 实证龙头炸板率8% vs 跟风32%，封板率<70%强度打折×0.8），明确边界（市场整体情绪温度归 G21/BM-SEL-23-B，板块内归 G06）；②回踩加"第4维度时间窗"（3-10交易日健康/>15失效/<2非真回踩）；§8.4 加雪球炸板率/东方财富情绪周期引用 |
| 2026-08-10 | 1.4.0 | RRG 增强+关系澄清（2026-08-07 最新） | ④RRG 补 4 项增强：Z-score 均值回归叠加（|Z|>2 跨象限反转修正，closelook 2026-08-07）+ 21d/63d/252d 多时间框架交叉（新轮动候选 vs 疲惫龙头）+ whipsaw 假信号确认（transition matrix，kriterionquant 2026-01）+ 强趋势半圆旋转例外（State Street 2026-03）；RS-Ratio 与 ranking_engine 第5因子关系澄清（截面快照选池 vs 时序变化率追轮动，不重复计算）；§8.4 加 closelook/kriterionquant/State Street 引用 |
| 2026-08-10 | 1.4.1 | 2026-08 实盘验证引用 | §8.4 加 eciks 2026-08-05（tech→financials 真实轮动）/ Amundi 2026-07-28（低跨板块相关=轮动有效期）/ QuantStreet 2026-08-05（RRG+dispersion 并用=本项目③扩散+④RRG 双模块架构机构验证）——无新算法，纯 2026-08 实盘验证 |
| 2026-08-10 | 1.4.2 | 结构审计修正 | §3.2 架构图笔误修正（v1.2.0 编辑遗留：`回踩A/B/Fib` → `回踩A/B/C+Fib`，漏"C"） |
| 2026-08-10 | 1.5.0 | 一日游应对+5状态分类+三级门槛+水温仓控（2026-08 最新研究整合） | 整合 WyckoffTradingAgent v2.1.x 2026-04 实证（板块一日游：Top3 次日重合率 14.8%）+ 华泰/国信/东吴 2026 行业研报 + 2026-08-10 十大券商看后市市场实证；§2.4 新增 2026-08 A 股市场实证对照；§3.1 新增 4 项：⑧ q3 短周期动量增强（strength 0.4×q20+0.3×q5+0.3×q3，应对一日游）⑨ 板块轮动状态 5 分类（CONSENSUS_CLIMAX/DISAGREEMENT_PULLBACK/HEALTHY_MAINLINE/DISTRIBUTION_RISK/NEUTRAL_MIXED + watch_score 加减分）⑩ 三级放行门槛 v2.1（阈值 0.70→0.60 / 0.90→0.80，应对非热门启动板块放行）⑪ 大盘水温→仓位控制映射（5 档：NEUTRAL 100%/RISK_ON 50%/PANIC_REPAIR 50%/RISK_OFF 30%/CRASH 0%，声明响应不判水温，水温判定归 regime）；§3.1⑦ hot_bonus 0.05→0.02（一日游下避免过度追高）；§3.2 架构图加新组件 + 跨层协同块；§4.5-4.8 新增 4 项替代方案裁定（q3 vs 机器学习/5状态 vs 二分类 vs regime/三级门槛 vs 统一阈值 vs 白名单/5档映射 vs 12态 vs 连续比例）；§5.2 演进路径补第二/三阶段新项 + 第四阶段增强；§6 待裁定加 4 项（q3权重/5状态阈值/三级门槛/hot_bonus）；§7 待定问题加 3 项（水温regime桥接/5状态正交性/三级门槛漏斗衔接）；§8.1 加 regime/情绪周期 spec 引用；§8.3 depgraph 加 4 项待登记模块；§8.4 加 WyckoffTradingAgent/华泰/国信/东吴/十大券商/国家统计局 6 条引用 |
| 2026-08-10 | 1.6.0 | 算法完整性补全+2026-08 最新研究（算法缺口审计） | 针对 v1.5.0 算法缺口审计：§3.1④ RRG 计算算法公式级补全（JdK DualEma 标准：RS=100×P_sector/P_bench，RS-Ratio=EMA(RS,10)/EMA(RS,26)×100，RS-Momentum=EMA(RS-Ratio,10)/EMA(RS-Ratio,26)×100，最小62日，xkqg/quantifiedtrader 2026 依据）+ 备选 Z-score 归一化 + 四象限落点伪代码 + 旋转路径追踪（θ/r 角度法）；§3.1④ RRG 象限→交易信号映射算法补全（原缺口"象限到信号转换未算法化"：四象限→板块强度加减分/三级门槛关系/水温响应关系 + whipsaw 确认规则 + Z-score 跨象限修正 + q3 协同）；§3.1⑧ q 因子计算算法公式级补全（percentile_rank 截面归一化 + 多TF加权伪代码）；§3.1⑨ 5 状态判定算法从"待施工初拟"改为可执行（4维输入 up_ratio/hhi_top5/lead_streak/disp_signal + 规则映射伪代码 + HHI 阈值 0.20/0.25/0.30 + 轮转速度辅助指标，legulegu/rebuildingsociety 2026 依据）；§3.1⑩ 准入 gate 算法公式级补全（三级 if-elif 伪代码 + 动态阈值调整与水温联动）；§3.1⑪ 水温→板块信号响应算法公式级补全（5档→signal_weight/gate_thresholds/rrg_filter 三类输出 + 与⑩⑨④联动）；§5.2.1 新增板块相关性聚类算法（原缺口"无板块相关性聚类算法"，层次聚类 ward linkage，第四阶段增强，Amundi 2026-07-28 依据）；§8.1 新增 21号 G05 选股引擎 + 25号 G09 多因子策略交叉引用（原缺口"与25号连接未明确"）；§8.4 加 10 条 2026-08 最新引用（xkqg/quantifiedtrader/stockwirex RRG 公式 + legulegu/rebuildingsociety HHI + Goldman Sachs 2026-08-03 + 中信建投/中信证券 2026-08 + NikitaPatil7/ijicic ML 对标） |
| 2026-08-10 | 1.8.0 | 板块涨停比归一化+资金流整合+regime-dependent轮动参考 | final_report_0724 交叉对照发现 2 项施工算法缺失：① §3.1① "涨停数"维度是绝对值，不同板块成分股数量差异大（电力设备 200 只 vs 油气 30 只），19 涨停跨板块不可比——补"板块涨停比=涨停数/成分股数"归一化算法，保持 40% 权重不变；② §3.1① 板块评分缺资金流维度，25号已有个股级资金性质 5 类分类但未上溯板块级——补 `aggregate_capital_nature_to_sector` 算法（成交额加权聚合个股资金性质→板块级得分+4 级标签），作为 evaluate_strength 修正因子（主力流入×1.1/对倒主导×0.8/主力流出×0.6）非新维度避免重构权重体系；③ 引用南京大学 2026 CDEMS regime-dependent 行业轮动框架（20 日波动率×20 日轮动速度定义 regime + regime-dependent risk parity）作为 10 号 regime 定义交叉验证，Phase 2+ 候选 | 用户要求再次审查施工环节流程算法缺失+final_report_0724 交叉对照。后台 agent 确认 22 号缺板块涨停比归一化指标（现有涨停绝对数不可跨板块比较）+缺资金流维度整合（25 号个股级资金性质未上溯板块级聚合） |
| 2026-08-12 | 1.9.0 | **已施工设施盘点节新增 + 数据源/引用真源修正（通用规则 #11 审查）** | 架构审查第 1-2 轮（读现状+代码侧/schema 真源审计+回填）：①新增 §2.5「已施工设施盘点」——10 项设施逐项核对代码/schema 真源（snapshot_collector/kline_downloader→market_kline_sector_880/ranking_engine/analyzer 6 方法落码确认/sector_constituent SCD-2/money_flow 五层净流入/sector_meta/list/concept_sector/market_sentiment_analyzer/intraday_buy_sell_point_analyzer），盘点结论：采集层全部 production，待施工 8 项全是计算/逻辑层纯函数无新增数据源需求；②**q 因子数据源错误修正**（§3.1⑧ 表+数据源注+待施工注+§5.2 共 4 处）：sector_snapshot 表无 change_pct_3d/5d/20d 字段（schema 真源确认仅 18 个实时快照采集字段）——q3/q5/q20 真正数据源是 market_kline_sector_880 日K 收盘价，两表分工"快照管实时截面、K线管多日序列"；③§2.1 交叉引用修正：MOD-L00-004 blueprint 无 §sector_snapshot/§sector_ranking 节（假锚点）→ 改引 11_d_data；"26 字段"声明与 schema 真源不符 → 修正为 18 采集字段（22 列含审计列）；④§2.1/§8.1 对 20 号引用精确化："§2.5 差异化矩阵已定三策略均消费板块信号"不精确（矩阵无板块维度行）→ 真实出处 §2.2-2.4 各节 + §7.2；"§7.4 下游交接（G06 前置）"不精确（列表未含 G06）；⑤§7 新增 2 项待定问题：20 号 §2.5 矩阵补板块维度行 + §7.4 补 G06（不越界改 20 号）、MOD-L00-004 blueprint 补板块采集节（含 sector_kline_downloader 代码头假锚点）；⑥sector_analyzer 6 维度声明经代码确认精确属实。⚠️ 本轮编辑在主工作区曾两次被并发 session git 操作回滚丢失，改用 session_worktree 物理隔离后重放恢复（#ARCH-GIT-CLEAN-GUARD-FIX 教训实证） |
| 2026-08-12 | 1.9.1 | **T+1 信号时序显式化 + 电风扇行情机构量化印证（第 3-4 轮）** | ①§2.3 新增信号→执行时序显式声明（盘后信号 T 日收盘后批量计算→T+1 日开盘 earliest 可执行→信号有效期须覆盖 T+1 全天；q3 超短因子 T→T+1 隔夜衰减是主要损耗源权重 0.3 已含折损；RRG 象限变化缓慢时滞可忽略；5 状态快照 T+1 盘中翻转滞后风险由 whipsaw 2-3 日确认规则对冲）；②§2.4 新增"电风扇"式再平衡量化确认（2026-08-10/11 最新）：国泰海通周度行业排名变化均值 12.75 > 历史 75 分位 11.75（电风扇式再平衡，科技反弹为拥挤出清后超跌修复非单边主升）+ 川观 2026-08-11 盘面（沪指六连阳终结跌 0.82% 报 3934 点缩量 2.34 万亿，机器人/MLCC/算力租赁/创新药轮动无持续性）+ 财信证券行业轮动周报 2026-08-10（高拥挤电子/食品饮料 + Beta/Alpha 区间 12/18 行业划分）——为一日游约束（Top3 次日重合率 14.8%）提供 2026-08 机构侧量化印证，支撑 q3 权重 0.3 与门槛 v2.1 降阈值裁定 |
| 2026-08-12 | 1.9.2 | **过度工程审查回执（第 5 轮）** | §5.3 新增过度工程审查回执，逐项对照 charter §2 硬边界判定：①460 板块全覆盖不过重——582 只板块是 snapshot_collector production 存量事实，且 Top99 推送池动态选取已是比静态 50-100 重点板块名单更优的答案（电风扇行情周度排名变化 12.75 下静态名单一周即失效）；②板块→个股传导多层逻辑不过重——⑦传导两步+⑩准入 gate 共三层全部是阈值规则 if-else 无 ML 无 GPU 依赖，§5.2 四阶段分层控制交付复杂度；③lead-lag network/ML 转折点检测/相关性聚类/GRU-Transformer 全部第四阶段或已拒绝，按"远期工程不算过度工程"规则保留 |
| 2026-08-12 | 1.9.3 | **一致性与交叉引用审查 + 文档质量复核（第 6-7 轮）** | 第 6 轮：①与 20 号一致性——v1.9.0 已修正§2.5 矩阵引用并登记板块维度行补登；②与 30 号一致性——§1 正交性声明与 30 §2.2 firm 层边界一致 ✅；③与 41 号一致性——发现 41 号 L130"调整周期到位"标 BM-SEL-03 应为 BM-SEL-09（ID 笔误）+ L44/L511 称回踩 A/B/C"目前是骨架"表述过期（v1.6.0 起已是公式级量化算法），登记 §7 待 41 号 owner 修正（不越界改）；④与 62 号一致性——strategy_registry 6 类含 sector_rotation ✅、62 号§4 引本 spec Top3 次日重合率 14.8% 作板块轮动校准依据 ✅；⑤BM-SEL-08/09 状态与 battle map 逐项核对（BM-SEL-08 有效状态运营态=锚点 MOD-SIG-026 production，代码映射缺失态-未实现；BM-SEL-09 MOD-SIG-040 planned）✅。第 7 轮：frontmatter 完整合法 ✅；§4.4 文档种类适配（spec 范式九段齐全）✅；两条硬约束 ✅；交叉引用全稳定相对 path（§8.3 depgraph 表 blueprint 目标验证存在）✅ |
| 2026-08-12 | 1.9.4 | **确认轮内部锚点审计修复** | 循环自检发现 §2.2/§3.1⑦ 两处"§2.4 一日游实证"锚点不精确——Top3 次日重合率 14.8% 的真源出处是 §2.3 约束末条（WyckoffTradingAgent 链接所在），§2.4 为 2026-08 市场实证对照节，修正为 §2.3 |
| 2026-08-12 | 1.9.5 | **确认轮 §3.1⑥ 资金流数据源精确化** | 循环自检深挖发现 §3.1⑥"板块资金流——复用现有字段"裁定含两处真源偏差：①"snapshot_collector 采集 26 字段含资金数据"——schema 真源确认 snapshot 表 18 采集字段且无 inflow 类字段，collector 不采集资金流；②全仓扫描无任何 `SectorData(` 实例化代码——analyzer 是纯函数库，数据装配调用方未落码。修正：板块级 net_inflow 正确来源 = money_flow（个股级五层净流入 production）× sector_constituent（SCD-2 成分股）聚合，与 v1.8.0 资金性质聚合同路径，聚合器待施工（纯函数无新数据源）；§2.5 盘点表 snapshot 行同步补"无资金流字段"注记。SectorData.net_inflow 字段本身存在（代码确认 L88），裁定结论"不新建资金流采集管道"不变，仅数据源路径精确化 |
| 2026-08-12 | 1.9.6 | 作战地图环节映射补强——锚定 BM-SEL-08-A 板块分析器（§2.5 末映射块：MOD-SIG-026 `sector_analyzer.py`，§2.5 盘点行 + §3.1① `evaluate_strength` 复用裁定，production） | 语义已覆盖但正文未显式编号的环节锚定到承载小节，实现环节级可追溯；不改既有正文 |
| 2026-08-15 | 1.9.7 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-07） | 版本修正过程叙述→当前态陈述（§2.1/§3.1⑥/§3.1⑧ 数据源）；§2.4 电风扇超长 bullet 要点化；一日游 14.8% 实证 5 处重复→真源（§2.3）+指针（§3.1⑧/§3.1⑩）；RRG 增强与象限确认规则重复项指针化；§3.1⑪ 与 §4.8 重复的"为何 5 档"合并；§8.4 三条长条目瘦身 + WyckoffTradingAgent 锚点残留修正（§2.4→§2.3）。标题编号/关键数值（强度权重 40/30/30、回踩 Fib 38.2-61.8%、调整周期 80%、RRG DualEma 10/26、虹吸 z>1.5、门槛 0.60/0.80、水温 5 档 100/50/50/30/0%）/裁定/开放问题/BM-XXX/跨文档链接零丢失 |

---

## 附录：数据资产消费登记（63 号审查批次 C，2026-08-20 登记）

> 来源：[63_data_utilization_audit](63_data_utilization_audit.md) §6.2 批次 C（板块轮动/行业分类）/ §7.2 第二波——消费层文档覆盖缺口施工。登记口径：每表 3-5 行（表名/内容/潜在消费场景/当前状态）；按收缩方案合并为本节表格汇总。当前状态统一为**未消费登记**（unconsumed registration）：数据已落库、代码层或有引用，但本消费方文档尚未将其作为显式数据源描述；后续实际消费接线后，按 63 号 §7.0.1 六字段模板改写为正文小节并更新状态。引用计数为 2026-08-20 工作区复扫（src/zephyr *.py，词边界匹配）。63 号 §7.0.3 拓扑序：`sector_list`（被依赖）先于 `sector_meta`/`concept_sector` 补。

| 表名 | 内容 | 潜在消费场景 | 当前状态 |
|---|---|---|---|
| `sector_list`（板块列表） | 板块基础清单（板块代码/名称/类别） | 板块轮动标的域基础表：板块强度评分（§3.1）的板块全集定义；板块推送池（880xxx/881xxx，§5.1）的候选来源 | **未消费登记**（2026-08-20 实证：src/zephyr 引用 3 次，代码活跃；消费语义未落本文档） |
| `sector_meta`（板块元数据） | 板块元数据（行业归属/成分数/编制规则） | 板块属性特征：行业/概念分类归并、板块间可比性校准（强度权重 40/30/30 的分组基准） | **未消费登记**（2026-08-20 实证：src/zephyr 引用 6 次，代码活跃；消费语义未落本文档） |
| `concept_sector`（概念板块映射） | 概念板块与个股/行业的映射关系 | 概念维度轮动信号：概念热度→成分股联动，与行业维度 RRG（Relative Rotation Graph，相对旋转图）象限确认互补 | **未消费登记**（2026-08-20 实证：src/zephyr 引用 5 次，代码活跃；消费语义未落本文档） |
| `index_constituent`（指数成分） | 指数成分股及权重（沪深300/中证500等） | 指数维度强弱参照：板块 vs 指数成分重叠度分析；指数调仓引发的板块资金被动流动预判 | **未消费登记**（2026-08-20 实证：src/zephyr 引用 22 次，代码活跃；消费语义未落本文档） |
