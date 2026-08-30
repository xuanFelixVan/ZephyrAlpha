---
title: S2 三事件 design_match 翻 true 失败调查与治本方案（校准专项第一步）
date: 2026-08-28
ttl: permanent
---

> **归档注记（2026-08-30）**：已闭环——治本方案（capitulation 三层修复 + 路 A 指数估值管道 + three_yang 指数适配）经 Owner 裁定施工落产（commit c5c23036），B4 验收完成（EVT-2024 design_match 翻 true，2015/2020 维持 false 补边界注记）。commit 2a16988d。

> **文档元信息**（_working 临时区豁免规范，EXEMPT-ZONE-FM）：doc_type=report · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.0.0 · date=2026-08-28 · topic=regime_s2_calibration_investigation · scope=07_trading_decision_architecture · completes_when=治本方案经 Owner 裁定并施工、S2 三事件 design_match 翻 true 验收后归档（归档不删除，保留审计链）。

# S2 三事件 design_match 翻 true 失败调查与治本方案（校准专项第一步）

> **出处**：[14_regime_s2_diagnosis](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/14_regime_s2_diagnosis.md) §4.5 walk-forward 校准路径 + B4 S2 重验注记（AI-WAVE1-001，2026-08-28，0/3 实证）；[13_regime_phase3_engineering_plan](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md) §3.5 P1-E9。
> **性质**：纯调查 + 方案设计文档，**不改任何生产代码**。调查人：session AI-S2-INVESTIGATE-001。方案待 Owner 裁定后再施工。
> **方法学红线**：本文全部参数候选族为**预注册草案**（14 号 §4.5 ②）；严禁简单降阈值凑分；严禁用三事件调参——候选筛选须在独立样本 walk-forward 上完成。

---

## 〇、执行摘要（结论先行）

**三事件翻 true 失败的根因不是单一阈值偏严，而是三层独立致死的结构性缺陷叠加**（capitulation），加一条未建设的数据管道（valuation 路 A），加两个对指数级不适用的判定维度（three_yang）：

| 维度 | 根因定量结论（ClickHouse 000300 全历史实证，生产函数逐行复核） |
|---|---|
| **capitulation** | **三层致死**：① 基础分档 z>1∧pct<-1.5% 在危机簇中结构性失真（簇内滚窗均量抬高 → 暴跌日中位 z=0.56，z>1 仅 32.5%；全历史 base>0 仅 74/4044=1.83%）；② 三过滤器中 wick>50% 与 A 股暴跌"光脚大阴线"形态根本冲突（跌幅≤-4% 日 wick 中位 4.8%，>50% 仅 2.5%），vol>2.0× 与涨跌停锁死/簇内高量冲突（暴跌日量比中位 1.12，>2× 仅 5.0%），唯 body>40%ATR 健康（95% 通过）；③ 归一化衰减加权（w₀≈0.089）数学上锁死——trigger≥60 需**最近 10 日连续满分 90**（3 日满分簇仅 22.5 分），**全历史 16 年 4044 个交易日 decayed 恒 0**（含无过滤器 what-if 也仅 max 6.2）。三层任一独立致死，叠加后该维度自落码起从未触发。 |
| **valuation 路 A** | `s2_valuation_score_fundamental` 函数已落码但**无数据源、无调用方**（overlay_signals_builder.py:349-350 仍走路 B）。daily_valuation 表存在但是**个股级** PE/PB/PS/PCF（百度源），覆盖仅 2026-08-01~08-26（provider 硬编码 period="近一年"），**无指数级估值表、无 CAPE/分位/破净率/ERP/巴菲特字段**（全库 system.columns 搜索零命中）、stock_valuation 表 0 行。路 B 实证：2015 pos=0.589→60 分有效，2020 pos=0.896→0 分、2024 pos=0.891→0 分（V 反转救不了，确证路 A 必要性）。 |
| **three_yang** | **非数据缺口，是 6 维联玩过严 + 两维对指数级不适用**：全历史 4044 日 flag 恒 0（连弱红三兵=1 都从未出现）。瓶颈维：d5「60 日跌幅>30%」全历史仅 20/4044=0.5% 满足（2020/2024 事件窗口 0/51——000300 危机级回撤仅 ~15%）；d4「第三根量≥前两根均量 2×」全历史仅 18/4044=0.4% 且与"量温和递增 1.1×"语义互斥。2024-09-24/09-30（924 真实红三兵）d1/d2/d3 均满足，仅被 d5/d4 卡死。 |

**治本方案要点**（详见 §四/§五/§六）：
1. **capitulation 三层修复**：基础分档改危机鲁棒口径（长期分位基准/跌幅主导复合）、过滤器本土化（删或替换 wick——"卖盘吸收"语义属 spring/flush 域，A 股 capitulation 形态是光脚大阴线实体宣泄）、聚合形式重设计（衰减峰值/非归一化和封顶/簇计数三候选族）——候选族 + walk-forward 验证设计见 §四，**严格按 14 号 §4.5 六层防过拟合栈执行**。
2. **路 A 四件套**：新建指数级 `c1_market.index_valuation_daily`（schema）+ akshare 中证官网/乐咕指数估值 provider（CAPE 自算近似）+ tasks.yaml 增量/回填任务 + feature_builder→builder 接线（路 B 保留降级）。分三期（PB/PE 分位 → 真 CAPE → ERP/破净率/巴菲特加分）。
3. **three_yang 指数适配**：d5 回撤门槛 30%→15%（或 250 日分位<20%）、d4 vol_surge 删除或降级为白武士加分项，结构改"核心维合取 + 辅助维分级"。

**残余依赖**（不在本方案范围，影响翻 true 验收，须统筹）：fund 维度 2015 窗口 MVP 实证=0（近/前 20 日均量比 max 0.87<1.0，跨 P1-E4 升级"融资余额+超大单+成交量"加权，14 号 §4.0/开放问题 10）；wyckoff V 反转盲区已由 E9d breadth_thrust 析取通路解决（波 1 实证 2024 有效）；2015 事件 trigger 时点与 capitulation 簇滞后 3 周的语义对齐（14 号开放问题 3，事件标注审视）。

---

## 一、调查方法与数据链（可复现性声明）

**数据**：ClickHouse（172.24.30.100，`c1_market`）`kline_index` 表 000300（沪深300，市场代理，regime_feature_builder.py:108 MARKET_PROXY）全历史日线 2005-01-04~2026-08-28 共 5259 行（open/high/low/close/volume/advance_count/decline_count）。

**方法**：以真实数据直接驱动**生产函数**（`src/zephyr/regime/features/overlay_features.py`），仪器化复制其内部子条件表达式并逐行断言一致：
- `_capitulation_daily` / `s2_capitulation_score`：仪器化复制输出 == 生产函数输出（断言通过）；
- `s2_three_yang_flag`：六维子条件复制 == 生产 flag（断言通过）；
- `vol_z` 用生产 `market_features.volume_anomaly(volume, 20)`（z=(v−rolling20.mean)/rolling20.std，与 regime_feature_builder.py:243 F5 同源）。

调查脚本（一次性，非生产码）：`.runtime/s2_inv/{ch_probe,capitulation_forensics,three_yang_forensics,base_stats}.py`。

**样本集**：
- 三事件 ±25 交易日窗口：EVT-2015-RECOVERY（2015-09-15，窗口 2015-08-07~10-27，51 交易日）/ EVT-2020-RECOVERY（2020-04-10，窗口 2020-03-05~05-20）/ EVT-2024-RECOVERY（2024-09-24，窗口 2024-08-16~11-05）；
- 扩展暴跌样本集：2010 年起 000300 单日跌幅 ≤-4% 的全部 40 个暴跌日各 ±10 交易日，窗口去重后 **545 个交易日**（覆盖 2010/2013 钱荒/2015 股灾 1.0+2.0/2016 熔断/2018/2019-05/2020-02~03/2022/2024-10/2025-04 等全部著名暴跌簇）。

---

## 二、capitulation 过滤器取证（E9a）

### 2.1 生产算法结构（overlay_features.py L218-335）

单日评分 = 基础分档（z>1∧pct<-1.5%→50 / z>1∧pct<-3%→70 / z>3∧pct<-4%→90）**且**三过滤器联玩全过（否则归 0）：
1. `vol_surge`：当日量 > 2.0×20 日均量；
2. `big_body`：|close−open| > 40%×ATR(14)；
3. `strong_wick`：(min(open,close)−low)/(high−low) > 0.5（下影线占比）。

过程化 = 近 20 日单日分的**归一化指数衰减加权和**（halflife=10，τ=14.43，w_newest≈0.0893，权重和=1）。trigger 门槛 capitulation≥60（regime_detector.py:399）。

### 2.2 三事件 ±25 交易日逐日取证（非零行全列）

**EVT-2015-RECOVERY**（窗口 51 交易日，base>0 仅 1 天，daily 全程 0，decayed max=0.00）：

| date | pct% | vol_z | base | vol_x | vol>2x | body/ATR | body>40% | wick% | wick>50% | daily |
|---|---|---|---|---|---|---|---|---|---|---|
| 2015-08-18 | -6.19 | 0.64 | 0 | 1.15 | ✗ | 1.66 | ✓ | 3.09 | ✗ | 0 |
| 2015-08-20 | -3.21 | -0.85 | 0 | 0.79 | ✗ | 0.55 | ✓ | 0.00 | ✗ | 0 |
| 2015-08-21 | -4.57 | -0.69 | 0 | 0.84 | ✗ | 0.78 | ✓ | 6.33 | ✗ | 0 |
| **2015-08-24** | **-8.75** | **0.04** | **0** | 1.01 | ✗ | 1.04 | ✓ | 4.45 | ✗ | **0** |
| 2015-08-25 | -7.10 | 0.64 | 0 | 1.11 | ✗ | 0.15 | ✗ | 12.94 | ✗ | 0 |
| 2015-09-07 | -3.43 | -1.44 | 0 | 0.75 | ✗ | 0.54 | ✓ | 5.63 | ✗ | 0 |
| 2015-09-15（事件日） | -3.93 | -1.43 | 0 | 0.59 | ✗ | 0.36 | ✗ | 18.73 | ✗ | 0 |
| 2015-10-21 | -2.92 | 2.54 | 50 | 1.91 | ✗ | 1.05 | ✓ | 30.38 | ✗ | 0 |

> 注：2015-08-24（股灾 2.0 黑色星期一，-8.75%）base=0——当日量仅 20 日均量 1.01×（2015-06 月均量 452 万手 → 08 月 254 万手，簇内滚窗均值被危机抬高 + 千股跌停锁死量能），z=0.04 远低于 z>1 门槛。**真实暴跌日在基础分档层即被归零**。

**EVT-2020-RECOVERY**（窗口 51 交易日，**base>0 天数=0**，daily/decayed 全程 0）：

| date | pct% | vol_z | base | vol_x | body/ATR | wick% | daily |
|---|---|---|---|---|---|---|---|
| 2020-03-09 | -3.42 | 0.39 | 0 | 1.08 | 0.78 ✓ | 2.94 | 0 |
| 2020-03-16 | -4.30 | -0.50 | 0 | 0.93 | 1.70 ✓ | 4.09 | 0 |
| 2020-03-23（真实底部） | -3.36 | -1.55 | 0 | 0.72 | 0.11 | 10.51 | 0 |

**EVT-2024-RECOVERY**（窗口 51 交易日，base>0 仅 2 天，daily 全程 0，decayed max=0.00）：

| date | pct% | vol_z | base | vol_x | vol>2x | body/ATR | body>40% | wick% | wick>50% | daily |
|---|---|---|---|---|---|---|---|---|---|---|
| 2024-09-02 | -1.70 | 1.68 | 50 | 1.42 | ✗ | 1.12 | ✓ | 0.58 | ✗ | 0 |
| **2024-10-09** | **-7.05** | **1.85** | **70** | **2.50** | **✓** | **1.74** | **✓** | **5.28** | **✗** | **0** |
| 2024-10-11 | -2.77 | 0.37 | 0 | 1.27 | ✗ | 0.64 | ✓ | 30.54 | ✗ | 0 |

> 2024-10-09（924 后首波暴跌 -7.05%）是三事件窗口中唯一过 2/3 过滤器的日——**仅被 wick>50% 单维卡死**（wick=5.28%）。

### 2.3 扩展暴跌样本集（545 日）过滤器通过率与失败原因分布

基础分>0 共 21 天（占样本 3.9%）。21 天的逐过滤器通过率：

| 过滤器 | 通过 | 通过率 | 结论 |
|---|---|---|---|
| vol > 2.0×均量 | 2/21 | **9.5%** | 与簇内高量/跌停锁死冲突，结构性过严 |
| body > 40%ATR | 19/21 | 90.5% | **健康**，保留 |
| wick > 50% | 1/21 | **4.8%** | 与 A 股暴跌形态根本冲突，结构性失效 |
| 三者联玩（现生产） | 0/21 | **0%** | 致死 |
| 2/3 表决 | 2/21 | 9.5% | 单改组合逻辑救不了（vol+wick 双残） |

失败原因分布（21 天，可重叠）：仅败 wick=2 天；败 2 项以上=19 天（vol+wick 双败为主）。**结论：wick 与 vol 两过滤器同时失效，任何"少一个条件"的组合微调都无法挽救。**

### 2.4 真实暴跌日形态分布（close≈low 实证，全历史 2010+）

| 样本 | 日数 | wick_ratio 分布 | wick>50% | wick<10% | vol_ratio 分布 | vol>2× | vol>1.3× | body/ATR 分布 | body>0.4 |
|---|---|---|---|---|---|---|---|---|---|
| 跌幅≤-3% | 56 | min 0 / p25 1.7 / **中位 6.1%** / p75 15.5 / max 53.6 | **1.8%** | 58.9% | 中位 1.06 / p75 1.20 / max 2.50 | **3.6%** | 17.9% | 中位 1.25 / p75 1.66 | 92.9% |
| 跌幅≤-4% | 40 | **中位 4.8%** / p75 12.5 | **2.5%** | **67.5%** | 中位 1.12 / p75 1.31 | **5.0%** | 25.0% | 中位 1.35 | 95.0% |
| 跌幅≤-5% | 24 | **中位 4.6%** / max 38.9 | **0%** | 66.7% | 中位 1.11 | 4.2% | 25.0% | 中位 1.41 | 91.7% |

> **A 股暴跌日的典型形态是"光脚大阴线"**（close≈low，2/3 的 ≤-4% 日 wick<10%）——恐慌尾盘无人承接，收盘即最低。下影线>50%（"卖盘被吸收"）是**见底确认日**的形态语义（spring/flush 域，14 号 §4.3/§4.6-6），混入"投降抛售日"判定是**语义错位**。量比维度同理：涨跌停制度下恐慌日量能被锁死（2020-02-03 三千股跌停量比仅 1.15），且危机簇内滚窗均值已抬高，>2× 在暴跌日仅 5% 达成。

著名底部/暴跌日明细（全部 daily=0）：2015-06-26(-7.87%,z=0.04)、2015-07-08(-6.75%,z=1.34,base=70 但 body/ATR=0.04 败)、2015-07-27(-8.56%)、2015-08-24(-8.75%)、2016-01-04 熔断(-7.02%,body/ATR=3.05,wick=0.05%)、2018-06-19(-3.53%,z=3.96,base=70,vol=1.98×败,wick=29.4%败)、2018-10-11(-4.80%,z=2.51,base=70,vol=1.63×败,wick=22.7%败)、2020-02-03(-7.88%)、2022-03-15(-4.57%,z=2.13,base=70,wick=0%)、2022-04-25(-4.94%,z=2.25,base=70,wick=0%)——**无一通过**。

### 2.5 聚合层数学边界（第三层致死，独立于过滤器）

归一化衰减权重（halflife=10/lookback=20，w_newest=0.0893，Σw=1，即**加权平均**）下：

| 连续满分 90 天数 | 1 | 2 | 3 | 5 | 7 | 10 | 20 |
|---|---|---|---|---|---|---|---|
| decayed 得分 | 8.0 | 15.5 | 22.5 | 35.1 | 46.1 | **60.0** | 90.0 |

- **trigger≥60 需最近 10 个交易日连续 90 分**——A 股 capitulation 是 1-3 日现象，数学上不可达；
- 单日 90 分 15 个交易日后残留 2.8 分（2015 事件"capitulation 簇早于事件日 3 周"场景，衰减到事件日 ≈ 个位数）；
- **全历史实证：2010+ 4044 个交易日 decayed 恒 0**（max=0.00，p99=0.00）；
- what-if 上界扫描（仅改过滤器组合，衰减不变）：去 wick/2/3 表决/仅 vol>2× → 全历史 ≥60 天数均为 0，三事件窗口 max 仅 0/0/6.2；**完全无过滤器** → >0 天数 1226 但 ≥60 仍为 0（窗口 max 4.5/4.7/6.2）。

> **根因判定**：capitulation 失效是三层独立致死叠加——L1 基础分档（z 口径危机簇失真，base>0 仅 1.83% 天）、L2 过滤器（wick+vol 双双与 A 股形态冲突）、L3 聚合形式（加权平均把单日贡献压到 8%，trigger 需 10 日满分簇）。**只修任何一层都不够；任何"降阈值"式单点修补（如 wick 0.5→0.3、vol 2.0→1.5、trigger 60→40）都只是沿错误方向凑分，违反 14 号 §4.5 铁律。**

---

## 三、路 A CAPE 管道盘点（E9b，断点清单）

### 3.1 数据链现状（逐项实证）

| 环节 | 现状 | 实证 |
|---|---|---|
| 表（schema） | ✅ 存在但**口径不符**：`c1_market.daily_valuation` 为**个股级** PE/PB/PS/PCF 宽表（schemas/categories/market_daily_valuation.py，18 列，ReplacingMergeTree），无 CAPE/分位/破净率/ERP/巴菲特任何字段（全库 system.columns 按 cape/percentile/erp/buffett/broken 搜索**零命中**） | `DESCRIBE` + `system.columns` 实证 |
| 数据覆盖 | ❌ **仅 2026-08-01~2026-08-26**（85,362 行 / 5,548 只 / 全 2026 年只有 8 月）——provider 硬编码 `period="近一年"`（akshare_provider.py:1448，百度股市通源）且无历史回填 | CH `min/max(trade_date)` 实证 |
| provider | ⚠️ 存在但源受限：akshare `_fetch_daily_valuation`（个股级，L1309-1485）；ifind 已 2026-08-14 退役（tasks.yaml:69 注记）；**仓内无任何指数级估值 provider**（akshare/tushare provider 能力清单均无 index_valuation 能力） | 源码 + CapabilityContract 清单实证 |
| 任务 | ✅ 存在：`daily_valuation_incremental`（tasks.yaml:67-77，akshare 主源，DAG 依赖 kline_daily）+ `daily_valuation_full_refresh`（L1030）；但**无指数估值任务** | tasks.yaml 实证 |
| 孤儿表 | ❌ `c1_market.stock_valuation` 表存在但 **0 行**（schema 有 pe/pb/ps/pcf/dividend_yield，无任何任务/provider 写入）；`index_quote` 000300 **0 行**；`market_breadth_snapshot` 仅 2026-08-24 起 24 行（miniQMT 实时快照，无历史） | CH count 实证 |
| 接线点 | ❌ `s2_valuation_score_fundamental`（overlay_features.py:430）**已落码但无调用方**——overlay_signals_builder.py:349-350 仍调路 B `s2_valuation_score(close)`，注记"路 A CAPE 待 daily_valuation 管道，Step 0 ①" | 源码实证 |
| 治理登记 | ❌ known_data_gaps.yaml 无 valuation 相关条目（断点未入治理视野） | grep 实证 |

### 3.2 断点清单（四件套口径）

1. **断点 A（口径/字段层）**：daily_valuation 是个股级原始估值表，S2 路 A 需要的是**指数级（沪深300/全市场聚合）估值分位序**（CAPE/PB 分位/破净率/ERP/巴菲特），字段与粒度双不符。
2. **断点 B（历史深度层）**：现源（百度股市通，period="近一年"）无 2010-2026 历史 → 历史分位无法计算；即使改 period 上限"近十年"，源稳定性与口径（静态 PE 冒充 PS 等）亦有风险。
3. **断点 C（provider/任务层）**：无指数估值 provider、无指数估值任务、无 CAPE 计算管道（5 年 EPS 通胀调整均值或 PE 中位平滑近似）。
4. **断点 D（接线层）**：路 A 函数无调用方；feature_builder 无估值透传方法（无 `get_index_valuation`）。

### 3.3 候选数据源（环境实证可用）

| 源 | 接口 | 口径 | 历史深度 | 评估 |
|---|---|---|---|---|
| akshare 1.18.75（已装） | `stock_zh_index_value_csindex` | 中证指数官网：沪深300 等 PE1/PE2/PB/股息率 | 深（中证官网披露全历史） | **推荐主源**（官方、免费、口径权威） |
| akshare 1.18.75（已装） | `stock_index_pe_lg` / `index_csindex_all` | 乐咕：指数 PE/PB 历史序列 | 长（1990s 起部分指数） | 推荐 fallback（交叉验证源） |
| tushare 1.4.29（已装） | `index_dailybasic` | 指数 PE/PB/换手率 | 全历史 | 备选（需 token+积分，治理成本高） |
| 内部计算（internal_compute_provider 模式） | 自算 | CAPE=5 年通胀调整 EPS 均值；简化版=5 年 PE_TTM 中位平滑（14 号 §4.2 认可"A 股简化 CAPE 普遍未严格通胀调整，不影响周期估值对比"） | 依赖主源序列长度 | CAPE 必经之路（任何外部源都不直接给 5 年 CAPE） |
| 破净率 | 个股 PB 聚合 | 全市场 PB<1 占比 | 需先补 daily_valuation 历史深度（换源：tushare daily_basic 全历史 PB）或东财/中证破净统计 | 二期加分项（缺失时路 A 降级运行，14 号 §4.2 已裁定非阻断） |

---

## 四、治本方案一：capitulation 重设计（候选族 + walk-forward 验证设计）

> 原则：三层根因三层修；候选族为**预注册草案**，最终选型由独立样本 walk-forward 决定；**严禁用三事件调参，严禁简单降阈值凑分**。

### 4.1 L1 基础分档重设计（危机簇鲁棒口径）

现 `z>1∧pct<-1.5%` 双门槛的失效机制：volume_anomaly 的 20 日滚窗均值/方差在危机簇内被危机自身抬高 → z 被结构性压低（暴跌日中位 z=0.56，z<0 占 37.5%）；同时千股跌停锁死量能。候选：

- **A1（长期分位基准）**：量能证据改用 250 日滚动分位 `vol_pct250 = volume.rolling(250).rank(pct=True)`（与 synthetic_vix_pct 同族口径，抗簇内失真）替代 z-score；分档锚定跌幅主导：`pct≤-3% ∧ vol_pct250>0.6 → 50 / pct≤-5% ∧ vol_pct250>0.5 → 70 / pct≤-7% → 90`（极端跌幅本身即投降证据，量能降级为佐证）。
- **A2（危机前基准 z）**：z 的均值/方差改用 60 日前~20 日前的"平静窗"（shift(20).rolling(40)）计算，衡量"相对危机前的放量"。
- 两候选均保留原 50/70/90 分档刻度不变（不动 trigger 语义）。

### 4.2 L2 过滤器本土化（A 股形态适配）

实证（§2.3/§2.4）：body>40%ATR 健康（保留）；wick>50% 与 vol>2.0× 双双失效。候选：

- **B1（删 wick，语义归位）**：下影线"卖盘被吸收"是见底确认语义，移交 spring/flush 域（14 号 §4.3 spring 主尾巴要素 + §4.6-6 flush 桥接信号已覆盖）；capitulation 只保留 vol+body 双过滤。
- **B2（wick 替换为本土形态）**：A 股投降抛售形态 = 光脚大阴线实体宣泄，改 `close_pos = (close-low)/(high-low) < 0.15`（收盘位置贴底）作为宣泄确认，与 wick 互补（非并列）；walk-forward 对比 B1/B2 的选择性。
- **B3（vol 过滤器口径联动 L1）**：vol>2.0× 改 `vol_pct250>0.8`（与 A1 联动）或 `vol>1.5×平静窗均量`（与 A2 联动）。
- 组合逻辑维持合取（capitulation 是极端事件，须保持 selective）；不接受 2/3 表决（实证仅 9.5% 且双残维度救不回）。

### 4.3 L3 聚合形式重设计（解开数学锁死）

现归一化加权平均 → trigger≥60 需 10 日连续满分（§2.5）。候选族（均保留"过程信号 + 随时间消退"的防粘滞语义）：

- **C1（衰减峰值 decayed-max）**：`score_t = max_{i∈[t-20,t]} daily_i × exp(-(t-i)/τ)`。单日 90 → 当日 90（直接过 trigger），3 周后 90×exp(-15/14.4)=31.9。优点：信号强度保留、语义干净；代价：放弃 memo"单日不足以触发"意图（**该意图的前提——单日可高分且多日簇集——在 A 股指数数据上不成立**，base>0 全历史仅 1.83% 天，需 Owner 裁定意图修正）；2015 场景（簇早于事件日 3 周）需 halflife≥26 才能把 90 分簇带到事件日 ≥60（τ≥37），指向按 stage 分参数化（trigger halflife=10 / confirm halflife=30，memo §4.1 占位原设计）。
- **C2（非归一化加权和封顶）**：`score_t = min(100, Σ daily_i × w_i)`，w 不归一化（Σ≈11.2）。3 日簇 90/70/90 → ≈233→cap 100；单日 90 → 90。与 C1 近等价但奖励簇集密度。
- **C3（簇计数映射）**：近 20 日内 daily≥70 天数 n：`n=0→0 / 1→40 / 2→60 / ≥3→80`。优点：对"簇早于事件日 3 周"天然稳健（计数不衰减权重只衰减窗口）、参数最少、可解释；代价：粒度粗、窗口边沿不连续（可用 40 日窗+软边沿缓解）。
- **C4（滞回触发器，14 号 §4.6-3 演进方向）**：衰减信号带滞回（触发 60/解除 40），防阈值附近震荡——作为 C1/C2 的加装件，非独立候选。

**选型判据**（walk-forward 输出）：正样本簇命中率、负样本误触发率、事件日可达性、参数平移稳定性。推荐预注册 C1（主）+ C3（对照）。

### 4.4 walk-forward 验证设计（14 号 §4.5 六层栈实例化）

| 层 | 本专项实例化 |
|---|---|
| ① 事件研究法 | 正样本 = 危机簇窗口：S1 已验证事件（2015-08-24/2020-03-20/2024-02-05）+ 扩展 40 个 ≤-4% 暴跌日 ±10 交易日；判定"簇内至少 1 日 daily≥50"命中率。负样本 = 低波常态期（realized_vol_pct<0.5 区间）随机抽 500 日，判定误触发率（daily>0 或 decayed≥60）。 |
| ② 预注册 | 本文 §4.1-§4.3 候选族即预注册文档：A1/A2 × B1/B2/B3 × C1/C3 全组合 ≤ 12 组，施工前锁定；实现后一次性跑验证，**禁止看结果回头改参数**（违例则计入 DSR 试验次数并降置信）。 |
| ③ DSR | 记录全部试参/试组合次数 N（含本调查 what-if 已试 5 组）；DSR 校正后评估。 |
| ④ 样本切分（替代 CPCV 的时间版） | **IS = 2010-2018**（2010×5 簇/2013 钱荒/2015 股灾 1.0+2.0/2016 熔断/2018×2 簇，共 ~25 个暴跌日簇）；**OOS = 2019-2026**（2019-05/2020-02~03/2022-03~04/2024-01~02/2024-10/2025-04，共 ~15 簇）。严格时间先后；**三 S2 事件（2015-09-15/2020-04-10/2024-09-24）全程不参与选型**，仅作最终 B4 验收。 |
| ⑤ MinTRL | N(簇)≈40，统计置信度有限——诚实标注"低置信通过"，不作硬性通过门槛。 |
| ⑥ 验收门槛 | **WFE = OOS 命中率 / IS 命中率 ≥ 0.6**；负样本误触发率 < 1%；参数平移 ±10%（halflife 10→9/11、分位门槛 ±5pp、close_pos 0.15→0.135/0.165）命中率变化 < 20%（平滑高原）；Monte Carlo 置换（随机打乱信号日期 1000 次）原始命中为极端离群（p<0.01）。 |

**施工顺序**（TDD-first，13 号 §3.5.3 对齐）：tests/regime/features/test_s2_capitulation_score.py stub（数值边界/防粘滞/过滤器语义）→ 实现 → dump_s2_scores.py 复跑（算法层验收：三事件窗口不再恒 0）→ walk-forward 报告 → B4 design_match 翻 true（须 Owner 确认后由统筹执行）。

---

## 五、治本方案二：路 A daily_valuation（指数估值）管道建设四件套

> 分三期递进，每期独立可验收；第一期即可让三事件 valuation 不再恒 0（CAPE 近似+PB 分位危机期 <25% → 60 分过 confirm 门槛，14 号 §4.5-6 预估口径，非调参依据）。

### 5.1 schema（新建指数级估值表）

新建 `c1_market.index_valuation_daily`（不复用个股级 daily_valuation——粒度语义不符，14 号 §4.2 字段映射的"待 daily_valuation CAPE 管道"应理解为此新表）：

| 列 | 说明 |
|---|---|
| trade_date / symbol | 指数代码（000300/000905/399006/全市场聚合行 MARKET） |
| pe_ttm / pb_mrq / dividend_yield | 主源直采（中证官网口径） |
| cape_5y / cape_5y_pct | 5 年 CAPE 及其 250 日×全历史扩展窗分位（内部计算列） |
| pe_pct / pb_pct | PE_TTM/PB 历史分位（内部计算列；PE_TTM 分位仅辅助，14 号危机失真警告） |
| erp / erp_pct | 风险溢价 1/PE−10Y 国债收益率（10Y 收益率源：macro_data 已有或中债接口）及分位 |
| broken_net_ratio | 全市场 PB<1 占比（二期，由个股 PB 聚合） |
| buffett_ratio | 总市值/GDP（二期，总市值源 kline_daily×总股本聚合，GDP 源 macro_data） |
| data_source / ingest_ts | 治理列（对齐现有表惯例） |

DDL-as-Code：`schemas/categories/market_index_valuation_daily.py` + business_data_categories.yaml 登记（calc_mode=preload，frequency=日频，SLA L2，对齐 market_daily_valuation 条目格式）。

### 5.2 provider

- **主源**：akshare `stock_zh_index_value_csindex`（中证官网，000300/000905 等 PE1/PE2/PB/股息率全历史）——环境已装 1.18.75 实证接口在位；
- **fallback**：akshare `stock_index_pe_lg`（乐咕，长历史 PE/PB）作交叉验证源（cross_source_validator 复用）；
- **CAPE 内部计算**：internal_compute_provider 模式——一期用"5 年（1250 交易日）PE_TTM 中位数平滑"近似（A 股简化 CAPE 惯例）；二期升级真 CAPE（成分股 5 年 EPS 通胀调整，CPI 源 macro_data）；
- **破净率（二期）**：先补 daily_valuation 个股 PB 历史深度（源替换：tushare daily_basic 全历史 PB，或东财接口；现百度源 period 上限近十年且需全市场重跑回填，工期评估后裁定）。

### 5.3 任务

tasks.yaml 新增：
- `index_valuation_daily_incremental`（table=c1_market.index_valuation_daily，source=akshare，schedule=daily_kline，dependencies=["kline_index_incremental"]，capability=index_valuation_daily）；
- 一次性历史回填任务（2010-01-01 起，全刷新模式，回填后校验：2015-08/2020-03/2024-09 三时点分位值落区间 sanity check——危机期 CAPE/PB 分位应 <40%）。

### 5.4 接线点

- `regime_feature_builder` 新增 `get_index_valuation()` 透传（对齐 get_money_flow/get_news_sentiment 模式）；
- overlay_signals_builder.py:349-350 改造：`cache["valuation"] = s2_valuation_score_fundamental(cape_percentile=..., pb_percentile=..., erp_...=...)`（数据缺失时**降级回跑路 B** `s2_valuation_score(close)`，C1 不退化）；
- `s2_valuation_score_fundamental` 函数本身已落码（overlay_features.py:430），无需改动，仅接数据。

### 5.5 风险与开放点

- 中证官网接口反爬/限流策略未勘探（施工 Step 0 补速度测试，对齐 speed_tester 模式）；
- CAPE 近似口径（PE 中位平滑 vs 真 EPS 均值）需与 14 号 §4.2 雪球基准校验（沪深300 CAPE 分位 <10%≈CAPE<12）；
- 10Y 国债收益率源在位情况未勘探（macro_data 覆盖盘点属施工 Step 0）。

---

## 六、治本方案三：three_yang 指数适配修复

**归因**：非数据缺口（OHLCV 五序列在位，生产函数正常执行），是 6 维联玩过严 + 两维对指数级不适用——全历史 4044 日 flag 恒 0（连 weak=1 都从未出现），三事件窗口 base_mask=0。

逐维证据（全历史 2010+ 通过率 / 三事件窗口通过率）：

| 维度 | 全历史 | 2015 窗口 | 2020 窗口 | 2024 窗口 | 判定 |
|---|---|---|---|---|---|
| d1 三连阳 | 12.8% | 6/51 | 5/51 | 7/51 | 健康 |
| d1 实体递增（第三根≥第二根 1.5×） | 12.0% | 6/51 | 6/51 | 7/51 | 健康 |
| d2 开盘在前根实体内 | 19.5% | 9/51 | 5/51 | 9/51 | 健康（2024-09-24 跳空高开 +4.3% 合法不满足） |
| d2 收盘逐日新高 | 25.3% | 15/51 | 10/51 | 16/51 | 健康 |
| d3 上影≤实体 5% | 12.2% | 5/51 | 5/51 | 5/51 | 偏严，降级为分级条件 |
| d4 量温和递增 1.1× | 5.1% | 3/51 | **0/51** | 3/51 | 偏严但可保留 |
| d4 第三根量≥前两根均量 2× | **0.4%** | **0/51** | **0/51** | 1/51 | **过严 + 与"温和递增"语义互斥** |
| d4 禁巨量 | 99.9% | 51/51 | 51/51 | 51/51 | 形同虚设（保留作排除条件） |
| d5 60 日跌幅>30% | **0.5%** | 19/51 | **0/51** | **0/51** | **对指数级过严**（000300 危机级回撤 ~15%） |
| d6 总涨幅<15% | 100% | 51/51 | 51/51 | 51/51 | 形同虚设（保留作排除条件） |

**修复建议**（预注册候选，walk-forward 同 §4.4 框架验证）：
1. **d5 位置维度指数适配**：`drawdown < -30%` → `drawdown < -15%`（000300 危机级实证：2020 新冠底 -15%、2024 924 前 -15%），或改为"close 处于 250 日区间下 20% 分位"（与 spring/valuation 的位置口径同族）；备选保留双通道（个股 -30% / 指数 -15%）由 market_proxy 类型切换——**推荐单一口径 -15%**，指数是本维度唯一消费场景。
2. **d4 vol_surge（第三根 2×）删除或降级**：与"温和递增 1.1×"数学互斥（全历史 0.4%），且 14 号 §4.4b 引用的八源标准中该条疑似"巨量排除"语义的误抄（"第三根≥前两根均量 2×"与"禁止巨量>2×"同文并存，逻辑上后者才是排除条件）——**施工前回源核对原文**；候选：删除该维（推荐）或移入白武士（=3）加分条件。
3. **结构改"核心维合取定级 + 辅助维分级"**（最小改动）：weak(=1)=三连阳∧实体递增∧收盘新高∧位置（d5 修复后）；standard(=2)=weak∧量温和递增∧¬巨量；warrior(=3)=standard∧上影≤5%∧实体显著放大。strong_confirm 门槛 three_yang≥2 不变（regime_detector.py:383）。
4. 修复后预期（实证推演，非调参依据）：2024-09-24（d1✓实体递增✓d2 收盘新高✓d3✓，d5 修复后✓）可达 weak；2024-09-30 前后簇可达 standard——924 红三兵可识别；2020-04-29/30 同理可覆盖。

---

## 七、验收路径与统筹事项

1. **本方案**（本文档）→ Owner 裁定候选族选型与意图修正（重点裁定项：① memo"单日不足以触发"意图是否随 A 股实证修正；② d5 回撤口径；③ 路 A 新表 vs 复用；④ CAPE 近似口径）。
2. 裁定后施工（TDD-first）→ walk-forward 验证（§4.4）→ `dump_s2_scores.py` 复跑（三事件窗口不再恒 0）→ B4 三事件 design_match 翻 true → Phase 2 全量重跑（A1+B4+A2+B1）。
3. **统筹依赖**（非本方案范围）：fund 升级（P1-E4，2015 confirm 必要条件的最后缺口）；known_data_gaps.yaml 补登记 valuation/指数估值断点；14 号开放问题 3（2015 事件标注/阶段期望审视）随 B4 结果一并裁定。
4. 治理联动：施工落定后回写 14 号 §4.1/§4.2/§4.4b（参数终值 + walk-forward 报告链接）、13 号 §3.5.4 验收清单、`#ARCH-REGIME-S2-ALGORITHM-001` fix_phase。

---

## 附录 A：关键代码锚点

- `src/zephyr/regime/features/overlay_features.py`：`_atr` L197 / `s2_capitulation_score` L218 / `_capitulation_daily` L287 / `s2_valuation_score` L403 / `s2_valuation_score_fundamental` L430 / `s2_spring_flag` L559 / `s2_three_yang_flag` L628 / `s2_breadth_thrust_score` L692
- `src/zephyr/regime/overlay_signals_builder.py`：S2 维度调用链 L322-390（capitulation L334 / valuation L349-350 / three_yang L362 / breadth_thrust L367）
- `src/zephyr/regime/core/regime_detector.py`：`TRANSITION_CONFIG["S2"]` L377-409（trigger capitulation≥60∧vix≥30∧bad_news_flat≥40 / confirm keys_or_gte{wyckoff:60, breadth_thrust:60}+keys_gte{policy:40, valuation:40, fund:50} / strong_confirm total≥250∧spring≥1∧three_yang≥2）
- `src/zephyr/regime/validation/phase2/historical_events.yaml` L75-100（三事件 design_match=false）
- `src/zephyr/data/implementations/akshare_provider.py` L1309-1485（_fetch_daily_valuation，period="近一年" @L1448）
- `src/zephyr/data/config/tasks.yaml` L67-77（daily_valuation_incremental）/ L1030+（full_refresh）
- `schemas/categories/market_daily_valuation.py`（个股级表 DDL 真源）

## 附录 B：调查产物清单

- 一次性调查脚本（非生产码，task_bound）：`d:\ZephyrAlpha\.runtime\s2_inv\ch_probe.py`（CH 连接+表盘点）、`ch_probe2.py`/`ch_probe3.py`（覆盖实证）、`capitulation_forensics.py`（§二全部数据）、`three_yang_forensics.py`（§六+路 B pos+fund 实证）、`base_stats.py`（§2.5 数学边界）
- 原始输出：`.runtime\s2_inv\cap_out.txt` / `ty_out.txt`
