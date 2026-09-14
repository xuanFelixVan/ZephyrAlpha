---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：证据不足，保守处理。处置=**保留**。**
>
> **✅ 已完成**：无显式完成信号
>
> **⚠️ 未完成**：无待办信号
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 0 个，其中判废弃 0、路径漂移 0）+ commit 提及 1 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# 技术指标库 批 4 挖矿报告（mining_sop 首次应用于指标域）

> 触发：Owner 指令"用病菌寻路 SOP 再搜下还有没有更多指标"。SOP 真源=mining_sop_policy.md v1.0.0。
> 母节点：技术指标库（f5df04f80a 时点=78 指标/116 列/8 大类）。
> 终止状态：**三连 signal + 候选池>20 → 按 SOP §7 强制停挖转施工**（未到双噪音，矿脉层面未挖干，长尾见 §4）。

## 1. 挖矿日志表

| 轮 | 矿脉 | 方向 | 判定 | 关键产出 |
|---|------|------|------|---------|
| R1 | TA-Lib 全集剩余缺口 | ③算法+⑥字段 | **signal** | 官方 README 拉取（github.com/ta-lib/ta-lib-python master，2026 现行）；对照出 TA-Lib 函数族缺口≈30 函数（扣除数学算子/CDL 蜡烛[图形域]/已实现） |
| R2 | Tulip Indicators 官方 104 函数清单 | ④后端 | **signal** | tulipindicators.org/list 全量拉取解析；交叉验证 R1 缺口+新增 MSW/QStick/CVI/WAD/FOSC/MarketFI/StdErr 族 |
| R3 | 经典交易者指标族（Bill Williams/Elder/Coppock） | ③算法 | **signal** | Alligator/AC/Fractals（Investopedia/AvaTrade/MetaTrader5，2024-2025 现行）；Elder-Ray 牛熊力（Investopedia）；Force Index（IncredibleCharts）；Coppock（TrendSpider/StockCharts ChartSchool） |
| R4 | A 股通达信特有族（BRAR/CR） | ⑥字段（纯 OHLC 适配） | **signal** | BRAR 人气意愿（百度百科/国投证券/富途）；CR 能量指标（富途/Moomoo 帮助中心，公式确认纯 OHLC）；通达信官方公式文档（help.tdx.com.cn） |
| R5 | 学术/自适应指标新算法（2024-2026） | ③机制 | **受阻** | 搜索限流 429 连发+时间盒到期，本轮记受阻不算查无；登记长尾 §4-M6 |

## 2. 防噪音四闸过滤结论

- 来源可溯：R2/R3/R4 全部 URL+发布方+年份 ✓（见 §3 各条）；R1 TA-Lib 官方仓库 ✓
- 交叉验证：STOCH/Aroon/PPO 等 TA-Lib 缺口由 Tulip 清单独立交叉印证 ✓；BRAR/CR 双源（百科+券商帮助中心）✓
- A 股适配：全部候选为单标的 OHLCV 确定性变换，T+1/涨跌停不影响计算口径 ✓；BRAR/CR 本身就是 A 股行情软件标配
- 可回测+数据可得：全部只需 OHLCV，c1_market.kline_* 已在位 ✓；筹码族（SCR/CYQ）需换手率/流通股本=维持挂裁定不变

## 3. 立卡（单批 ≤3，优先级裁定）

### 卡 1：STOCH 经典慢速随机（%K/%D 本体）
- why：库内 KDJ 是 A 股口径变体（RSV→SMA），国际标准 Stoch %K(SMA)/%D/SLOW%K 缺位——跨策略翻译（C4 车道）读国外策略时第一高频依赖
- 产出：stoch_k/stoch_d/stoch_slow_k/stoch_slow_d 4 列；工时≈0.5 班内小批

### 卡 2：TA-Lib 动量组清偿批（Aroon/AroonOsc/BOP/PPO/APO/DX）
- why：TA-Lib momentum 组最后缺口一次清完；Aroon 是趋势强度主流件、PPO/APO 是 MACD 的百分比/绝对变体（因子化常用输入）
- 产出：约 8-10 列；工时≈1 批

### 卡 3：BRAR+CR 能量族（A 股标配，纯 OHLC）
- why：A 股行情软件标配但纯 OHLC 实现（区别于筹码族不涉及换手率），通达信公式现成（§R4 引文）；与既有 PSY/VR 组成完整 A 股情绪能量组
- 产出：ar_26/br_26/cr_26 3 列；工时≈半批

## 4. 长尾矿脉清单（未挖/未排期，防重复挖登记）

- **M-L1 均线自适应族第二批**：TEMA/TRIMA/T3/MAMA+FAMA/VIDYA/FRAMA/JMA（Tulip+TA-Lib 双源确认存在）
- **M-L2 价格变换族**：AVGPRICE/MEDPRICE/TYPPRICE/WCPRICE（TA-Lib price transform 组，实现简单）
- **M-L3 统计回归族扩展**：LINEARREG_ANGLE/SLOPE/INTERCEPT/BAR/STDERR（TA-Lib statistic 组余量）
- **M-L4 经典交易者族**：Alligator 三线/AC 加速器/Fractals/Elder 牛熊力/Force Index/Coppock/Guppy GMMA/Gann HiLo/Squeeze/WaveTrend（R3 引文）
- **M-L5 社区热门扩展**：CHOP/VHF/CTI/ER/EBSW/Inertia/RMI/PSL/PFE/MSW/QStick/CVI/WAD/VO/FOSC/MarketFI/Ulcer/Zscore（Tulip+pandas-ta 系）
- **M-L6 学术自适应指标**（R5 受阻未挖）：ML 自适应参数、2024-2026 论文新指标
- **不做边界（留痕）**：Volume Profile（结构性另立）；跨标的相对强度/PRS（破单标的 OHLCV 契约）；ZigZag/分形形态（图形域=REG-PAT-001 会话职权）；SCR/CYQ 筹码族（需换手率契约扩张，挂 Owner 裁定）；生活化指数永不采纳

## 5. 建议

候选池 30+，按 SOP 停挖转施工。建议施工顺序=立卡 1/2/3 一批（合计约 15-17 列，1 班量），长尾 M-L1/L2/L3 一批收尾，M-L4 视消费端需要再启。
