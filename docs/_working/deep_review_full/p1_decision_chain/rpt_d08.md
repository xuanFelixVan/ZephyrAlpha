---
ttl: task_bound
doc_type: report
title: 深度审查报告——合成VIX（D08）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：合成VIX（D08）

- 状态: **已审**
- 级别: P1｜类型: 算法（ATM IV 30 天插值+下行半偏差后备）
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/regime/features/synthetic_vix.py:106(compute_synthetic_vix)`（228 行全文通读）
- 生产调用方: **真实在链**——`overlay_signals_builder.py:606-638`（vix_pct→S1 vix_panic/S2 vix 维度，期权主路+下行半偏差后备双路）；risk_signal_builder 无消费（grep 空）
- 测试文件: `tests/regime/test_synthetic_vix.py`（11 测试）+ `tests/regime/test_synthetic_vix_iv_path.py`（66 测试，IV 路重点覆盖）

## 1 对象快照

- 审查范围：三函数全文件（ATM 筛选/30 天插值/双标的均值/分位化/下行半偏差后备）。排除项：option_iv_surface 进料管道（miniqmt_provider，SVX-1-P0 事故的进料侧，归数据域）；S1/S2 评分映射归 D11。
- 材料包缺项声明：IV 曲面真实数据画像（ATM 覆盖率/dte 分布）未取；"沪深300 期权 CBOE 方差互换法 2026 实证"（D01 S2 注释引）原文未回读。
- 测试覆盖概况：66+11 覆盖强（含 IV 路专项）；dte≤0 边界未见用例（按 grep）。
- 变更热力：6 次。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | F-A1 **dte≤0 行未过滤**：`near = dte<=30` 不含下界——到期日当天（dte=0）乃至数据滞后导致的负 DTE 行进入 near，iv_near 取均值被临到期极端 IV 污染（gamma/iv 尖峰），插值锚点失真；恐慌期近月合约 dte 恰小，最差时点最受伤 | synthetic_vix.py:64-68 | P2 | 造 dte=0, iv=80 行加入单日组，观察 iv_near 均值上抬 |
| A | F-A2 插值锚点不一致（轻度）：iv_near=全部 near 行均值，但 t1=near 最大 DTE——均值 IV 配单点期限做线性插值，期限结构斜率被平均化；标准做法取 t1 对应行 IV | :66-81 | P3 | 取 t1 行 IV 替代均值对拍 |
| A | F-A3 **方法基标注失准**：ATM IV 均值+30 天线性插值≈VIX-1993 旧法（8 档 ATM 平均），非 docstring 所称"CBOE VIX 简化公式"（现行 VIX=2003 方差互换无模型法，中国波指 iVX 同为方差互换原理）——ATM-only 漏掉 put skew，恐慌期系统性**低于** iVX/真 VIX；跨模块绝对阈值（D03 iv≥35/40、D01 S2 注释">25 即触发"引"CBOE 方差互换法实证"）与本模块水平基是否同源未对账 | :19-28 ↔ institutional_regime_scorer.py:96-97; regime_detector.py:320-324 | P2 | 用历史 iVX（000188）与本模块同日输出对拍水平差 |
| A | F-A4 **SVX-1-P0 消费纪律在位（正面确认）**：fake zero IV（iv≤0 剔除+warning）、null delta（不按 0 处理+warning）、ATM 池空（出声+事故签名区分进料口 vs 市场结构）——"plausible-but-wrong 比 None 更坏"的纪律落实，且有专项测试 66 件；这是 checklist#6 静默死亡的优秀修复样板 | :84-103,125-152 | 已查无 | tests/regime/test_synthetic_vix_iv_path.py |
| A | F-A5 下行半偏差后备（synthetic_vix_pct）数学正确：r.clip(upper=0)→半方差→√252 年化→250 日 rank 分位——Sortino 分母口径；**输出是分位非 VIX 点位**，与 vol_pct 接口兼容（只可用于分位型消费者；绝对阈值型消费者误喂会失义——接口文档已声明，需消费方自觉） | :191-228 | P3 | 同序列对照 realized_vol_pct 分位差 |
| B | F-B1 输入契约：MultiIndex(trade_date, underlying)+六列；空/None→空 Series（调用方回退 vol_pct）契约清晰；双标的均值 skipna（单缺用单标的）✓；dte 由 expiry-trade_date 现算（不信任进料列）✓ | :106-168 | 已查无 | — |
| C | F-C1 消费方接线核实：overlay_signals_builder :616-638 期权主路（compute_synthetic_vix→vix_pct_from_vix）+后备路（synthetic_vix_pct）双路接线真实在链；S1 vix_panic/S2 vix 维度消费形式归 D11 核 | overlay_signals_builder.py:606-638 | 已查无 | grep 已核 |
| D | F-D1 兄弟口径：vol_pct（realized）与 vix_pct（implied）双轨并存——S1 vix_panic 用哪个/如何融合归 D11；本模块与 D05 的 realized_vol_pct 无代码重复（不同函数） | :171-188 ↔ market_features.py:48-75 | 已查无 | — |
| E | F-E1 静默失败面：本模块所有降级路径均出声（F-A4 三道 warning）+空 Series 显式返回——域内静默死亡治理最佳；残余静默点=插值返回 NaN 后 dropna 静默缩序列（无计数日志） | :156-157 | P3 | dropna 前后长度差日志化建议 |
| E | F-E2 幂等/时序：纯函数无状态；PIT 声明由调用方 shift(1)（:37）——归 D11 核实落地 | :37 | 挂 D11 | — |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| # | 对照项 | 结论 | 来源 |
|---|---|---|---|
| 1 | 30 天隐含波动率指数编制 | **对等已有（实现为旧法）/立卡候选**——ATM 平均=VIX-1993 旧法，可用但非现行标准；现行 CBOE（2003 起）与上证 iVX（2015，上交所）均为方差互换无模型法（全 smile 聚合）；**立卡**：对标 iVX 编制方案改造（改造点=_interp_vix_for_date 扩 OTM 全 strike 聚合），或至少与 000188 对拍建立水平校准系数 | [CBOE VIX White Paper 2003](https://www.sfu.ca/~poitras/419_VIX.pdf)（CBOE，2003，SFU 存档）；[Cboe Volatility Index Mathematics Methodology](https://cdn.cboe.com/resources/indices/Cboe_Volatility_Index_Mathematics_Methodology.pdf)（Cboe，现行）；[iVX 编制方案](https://www.scribd.com/document/985764258/)（上交所，2015，方差互换原理） |
| 2 | 下行半偏差作恐慌代理 | **对等已有**——Sortino 下行偏差是公认下行风险度量；期权缺失时的后备选择合理（A 股期权历史短/断供常见） | 模块内依据声明 :211-212（Sortino 谱系）；CBOE/iVX 文献同上（恐慌指数族语境） |
| 3 | 隐含波动率微笑的风险信息 | **立卡候选（远期）**——上财研究实证 50ETF IV smile 倾斜对收益有预测力——若转 iVX 法全 smile 聚合，skew 信息免费获得（当前 ATM-only 丢弃） | [上证50ETF期权隐含波动率微笑形态的风险信息容量研究](https://qks.shufe.edu.cn/mv_html/j00001/202004/fa809fc9-8a85-47f9-92d3-ad7236677215_WEB.htm)（上海财经大学学报，2020） |

## 4 缺陷清单（按严重级）

- **F-A1（P2）dte≤0 行污染 near 池**：现状=无下界过滤 → 证据=:64 → 影响=到期日/滞后行极端 IV 拉偏插值，恐慌期最敏感；爆炸半径=S1/S2 恐慌维度假高/假低 → 建议修法=`dte>0` 下界（或 dte>=1）+ 过滤计数日志 → 验证法=dte=0 行构造复现。
- **F-A3（P2）方法基命名与阈值口径衔接**：现状=ATM 旧法自称"CBOE 简化公式"，跨模块绝对阈值（35/40/25）口径来源混用 → 证据=docstring vs CBOE/iVX 方法学 → 影响=恐慌阈值的第一性依据不明，可能系统性偏低（漏报）或与实证基错配；爆炸半径=S1 触发率与 D03 IV 维 → 建议修法=docstring 改口径标注+与 iVX 对拍记录校准系数；阈值复审归 D03/D11 收口 → 验证法=同日对拍。
- **F-A2/A5/E1（P3）**：插值锚点、后备接口声明、dropna 静默缩序列——常规队列。

## 5 挂起疑问

1. D01 S2 注释"沪深300 期权 CBOE 方差互换法 2026 实证，>25 即 8/8 胜率"的实证产物与本模块 ATM 法输出的关系——若实证基于方差互换法数值而消费的是本模块 ATM 法，阈值迁移有效性存疑（需实证原文对账，材料包缺项）。
2. 000188（中国波指）2018 后停发/复发现状与本项目是否可直接引用——历史序列可得性未核。

## 6 完备性自评

- 六轴全查：A（插值/分位/半偏差逐算法+dte 边界发现）、B（进料契约+SVX-1-P0 三道闸确认）、C（消费方双路接线核实）、D（与 realized 双轨口径）、E（静默面=域内最佳实践、PIT 挂 D11 核）、F（3 条带来源，方法学正源对齐）。
- 长尾清单：①IV 曲面进料管道（miniqmt_provider._compute_iv_rows）本体未审（SVX-1-P0 事故进料侧）；②66 件 IV 路测试未逐件审（信任判定=抽测通过+纪律注释一致）；③vega 列进料但未参与加权（等权 ATM 均值 vs vega 加权）——文档未声明取舍理由。
