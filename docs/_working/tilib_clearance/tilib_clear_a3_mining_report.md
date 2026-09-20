---
ttl: task_bound
session: st-tilib-clear-20260920
title: 波3 M-L6 学术自适应指标挖矿报告（2024-2026 论文新指标，mining SOP）
---

# 波3 M-L6 挖矿报告（2026-09-20 · tilib 清欠班）

> 母节点：技术指标库（133 条时点）。矿脉：M-L6 学术自适应指标（批4 挖矿 R5 受阻项，本轮复挖）。
> 方法：WebSearch 定向检索 TASC（Technical Analysis of Stocks & Commodities）2024-2026 论文+官方实现镜像，公式可验证性为唯一准入闸。

## 1. 挖矿日志

| 轮 | 矿脉方向 | 判定 | 关键产出 |
|---|---|---|---|
| R1 | Ehlers TASC 2024-2026 论文谱系 | **signal** | Precision Trend（2024-09）/ Linear Predictive Filters+Griffiths 预测器（2025-01）/ 双高通去滞后 Lag Removal（2025-04）/ Adaptive SuperSmoother Improved Filter（MESA）/ Continuation Index（2025-09）/ Auto Tune Filter（2026-05） |
| R2 | Precision Trend 公式源考古 | **signal** | financial-hacker.com（Ehlers 技术博客）C 转译全文到手：HighPass3 三阶高通差分方程+TROC 确认项，系数逐一验证 |
| R3 | Griffiths 预测器/Continuation Index 公式源 | **受阻** | traders.com 403、mesasoftware 需 PDF 解析、GitHub 镜像搜索超时——30 分钟时盒到点按 §8 停，立卡登记不施工 |
| R4 | 防噪音闸：库内同义扫描 | **signal** | SuperSmoother/HighPass 均为库缺位（hma/zlema/kama 不覆盖其口径）；ht_dcperiod 已有→瞬时频率族不重复立条 |

## 2. 立卡（≤3）

### 卡 1：Ehlers Precision Trend（TASC 2024-09）——本波施工 ✅
- why：2024 新论文正主；谱带分解趋势线（HP3(250)−HP3(40)）+TROC 确认，纯 OHLCV，公式逐行可验证
- 产出：ptrend_250_40 + ptrend_roc 两列；工时半批

### 卡 2：SuperSmoother（论文原生滤波组件）——本波施工 ✅
- why：Precision Trend 论文的滤波基元（Ehlers 正典二极低通），库内缺位、与既有均线族口径不重复；2024-2026 论文族的原语依赖
- 产出：supersmoother_10 一列

### 卡 3：HighPass3（论文原生滤波组件）——本波施工 ✅
- why：同上，三阶高通是 2024-09 论文双滤波的另一半；TradeStation/TradingView 平台标准指标
- 产出：highpass_40 一列

### 登记后续（不立卡不施工，防重复挖登记）
- **Griffiths Predictor + Instantaneous Frequency（TASC 2025-01）**：Griffiths 格型自适应预测，公式在 mesasoftware PDF；施工前置=PDF 公式提取（下一班可做）
- **Continuation Index（TASC 2025-09）/ Auto Tune Filter（TASC 2026-05）**：发表过新，公式镜像未到位；挂观察

## 3. 防噪音四闸结论

- 来源可溯：TASC 期号/年月+financial-hacker C 源 URL 全部落档 ✓
- 交叉验证：HighPass3 系数与 Ehlers Cycle Analytics 正典式一致（exp(−1.414π/L) 族）✓
- A 股适配：纯单标的 OHLCV 确定性变换，T+1/涨跌停不影响口径 ✓
- 可回测+数据可得：只需 close，kline_daily 在位 ✓

## 4. 34 缺口对账

批4 清单 34 项 − 3 项同义剔除（LINEARREG_BAR=linearreg、PSL=PSY、MSW=ht_sine）= 31 项已施工；波3 现挖 +3（Precision Trend/SuperSmoother/HighPass3）= **合计 34，注册表 102→136 达标**。

## 引用源

- financial-hacker.com Ehlers Precision Trend C 转译（公式权威源，本波施工依据）
- TASC 2024-09 "Precision Trend Analysis"（Ehlers）；TASC 2025-01 "Linear Predictive Filters and Instantaneous Frequency"；TradingView TASC 2024.09/2025.01 官方 Pine 移植（存在性核对）
- 检索轮 R3 受阻记录：traders.com 403 / mesasoftware PDF 未解析 / GitHub 镜像搜索超时（60000ms）
