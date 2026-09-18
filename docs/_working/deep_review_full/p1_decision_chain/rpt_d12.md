---
ttl: task_bound
doc_type: report
title: 深度审查报告——风险信号构建（D12）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：风险信号构建（D12）

- 状态: **已审**
- 级别: P0｜类型: 信号组装（13 参数风险系数→RiskSignal→Shrinkage）
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/regime/risk_signal_builder.py:71(RiskSignalConstructor)`（344 行全文通读）+ 底座 `features/risk_features.py` 头部与全部系数函数签名核对
- 生产调用方: `regime_feature_builder.py:405-415`（enable_full_risk=True 时 build_shrinkage_schedule 消费 build_for_date → D01 `_compute_risk_signal`）；D01 overlay 危机门控读其 params[1]
- 测试文件: `tests/regime/test_risk_signal_builder.py`

## 1 对象快照

- 审查范围：13 参数组装/PIT 预计算/降级纪律/#8 虹吸/#9 多分时共振。排除项：`risk_features.py` 10 个系数函数的分档映射逐档数值复算（抽审 #1 全档+其余签名/不变量级）；D01 聚合公式归 rpt_d01。
- 材料包缺项声明：10 号 spec §5.3.3 十三参数定义原文未回读；各系数触发率的真实数据画像未取。
- 测试覆盖概况：builder 层专项测试在册。
- 与 D11 同范式（预计算+切片+降级 WARN），事故密度低于 D11。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | F-A1 **#1 危机地板双实现（checklist#4）**：`risk_features.realized_vol_coef` 与 `RegimeFeatureBuilder._build_feature_risk` 是同一 0.90/0.75×slope 交集映射的两份代码承载（docstring 自称"逐档对齐"——当前值一致，但无双份一致性保障）；Phase 2a 启用时走前者，Phase 1 简化版走后者，开关切换即换实现 | risk_features.py:71-96 ↔ regime_feature_builder.py:742-785 | P2 | 两函数喂同一序列对拍（当前应逐位相等）；合并建议=单一真源函数 |
| A | F-A2 **#8 虹吸 HHI 第二份实现（checklist#4）**：`_compute_siphon_inputs` 的板块 HHI（|ret| 份额平方和）与 D11 `_compute_sector_metrics` 的 sector_hhi 逐行同构、各自缓存——同一概念两处算，板块集/日期窗不一致时结果分叉且无对账 | risk_signal_builder.py:303-310 ↔ overlay_signals_builder.py:740-746 | P2 | 同 sector_df 喂两处对拍 hhi 序列；合并建议=抽公共函数 |
| A | F-A3 降级哲学的系统性方向（跨对象聚合，本对象为关键节点）：全部参数缺失→1.0→RiskSignal=1.0→D01 危机门控同步失效（overlay 屏蔽）——**每处局部"保守不误杀"全局合成"满部署"**；数据断供日的风险机制全链静默失效（有逐参数 WARN 无聚合告警）。此为 rpt_d01 F-E1/rpt_d05 F-A2 的第三处印证 | risk_signal_builder.py:31-32,134-147 | P1(聚合口径) | 断供日构造全 None feature_builder 跑全链对照 Shrinkage |
| A | F-A4 #1 NaN 语义保守正确：slope NaN→0.0（未跌）、vol_pct NaN→不触发（1.0）——不会因 NaN 误杀；分档 severe 覆盖 mild 的赋值顺序正确（mild→severe 顺序赋值） | risk_features.py:88-96 | 已查无 | NaN/边界值用例 |
| A | F-A5 PIT 链通过：末尾统一 shift(1)（:269-271）+build_for_date 切片（:139-144）+NaN→1.0；pct_change 从 raw close 现算后进系数再 shift——无前视 | :269-271,139-144 | 已查无 | 抽查 #2/#9 时序 |
| B | F-B1 C1 修正遗产在位：close 与 high/low 分离加载（high 缺失不再连累 #2/#3/#5）——历史 bug 修复留痕完整（:178-193） | :178-193 | 已查无 | — |
| B | F-B2 #9 多分时聚合：`groupby(level=df.index.name)`——分钟表 index 名缺失（None）时 groupby(level=None) 行为异常→except→降级单分时（有 WARN）；依赖上游 index 命名契约未文档化 | :328-341 | P3 | index.name=None 构造复现 |
| B | F-B3 #4 time_incubation/#12 chip_structure stub=1.0 如实登记；#12 的"Phase 2c 接"未兑现（与 D06 孤儿态互证——chip 引擎零消费端，接线计划悬置） | :39-40,86-88 | P3 | 对照 D06 状态 |
| C | F-C1 下游传导：params → D01 `_compute_risk_signal`（#1 门控+min 聚合+共振+opportunity 抵消）→ Shrinkage；**opportunity 通道生产恒死**：#11/#13 stub 恒 0.0 → D01 机会恢复项永为 0（声明式 stub，非静默）——"利空不跌抵消"能力未接线 | :145-147 ↔ regime_detector.py:903-908 | P3 | 对照 D01 机会恢复逻辑 |
| C | F-C2 爆炸半径：RiskSignal 直接乘 Shrinkage（D01 :927）=全账户仓位节流；#1 门控同时决定 overlay 生效（D01 :539-542）——本对象是风险链的**双重开关**（节流+门控），正确性权重高于 D11 | :5-6; regime_detector.py:539-542,927 | P1(口径，随 F-A3) | — |
| D | F-D1 与 D11 兄弟对称性核查：同范式/同降级哲学/同 _fb_call 兼容层（两份 _fb_call 逐行同构=第三处轻度双承载，风格级） | :278-290 ↔ overlay_signals_builder.py:548-560 | P3 | 抽公共 mixin 建议 |
| E | F-E1 静默失败面：全参数降级分支带 WARN；`_compute_multi_tf_divergence`/`_compute_siphon_inputs` 失败降级带 WARN——静默点仅剩 stub 类（已声明）；无 except 吞噬新类型 | :243-261,311-313,339-341 | 已查无 | — |
| E | F-E2 幂等：预计算缓存+纯切片，重放一致；HMM 特征复用 builder 缓存（同源） | :117,158 | 已查无 | — |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| # | 对照项 | 结论 | 来源 |
|---|---|---|---|
| 1 | 多指标危机仪表盘（波动分位+相关性飙升+广度+量能） | **对等已有**——跨资产相关性飙升作危机信号、波动分位、广度极端是 regime/crisis 检测文献的标准成分（本项目 13 参数与其同族，加 A 股特有广度/虹吸维度）；min 聚合+主信号门控是保守工程化 | [LSEG: Statistical & ML Market Regime Detection](https://developers.lseg.com/en/article-catalog/article/market-regime-detection)（LSEG，多模型危机检测综述）；[QuantStart: HMM regime filter](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/)（风险态过滤语境） |
| 2 | KDJ/技术指标顶背离 | **对等已有（公共域）**——KDJ 为 A 股常用技术指标（随机指标stochastics 变体），顶背离判定属技术分析公共域谱系；多分时共振是本土实务增强 | KDJ=Stochastic Oscillator 谱系（George Lane，公共域教程体系，无单一定源 URL 如实记） |
| 3 | HHI 集中度作虹吸/拥挤代理 | **对等已有（概念）/立卡候选（口径）**——Herfindahl 指数是标准集中度度量；但本项目用 |ret| 份额（含跌幅）非涨幅份额——与"虹吸=资金抱团上涨板块"的语义有偏差，建议改用涨幅份额或收益为正板块的份额（改造点=risk_features.py 与 overlay 双处同步） | HHI=Herfindahl-Hirschman 指数（产业组织经济学标准，教科书谱系如实记） |

## 4 缺陷清单（按严重级）

- **F-A3/C2（P1，聚合口径）断供日风险机制全链失效**：现状=逐参数 1.0 降级（局部保守）×D01 门控=min 聚合——全局合成满部署且仅散点 WARN → 证据=三对象交叉（rpt_d01 F-E1/rpt_d05 F-A2/本条）→ 影响=数据管道事故日恰逢市场危机时风险节流与危机门控同时失效；爆炸半径=全账户 → 建议修法=①RisksignalConstructor 输出附 available_params 计数，D01 侧对"有效参数<半数"日降级为最近有效 risk 或地板值（需 Owner 裁定方向）；②最低成本=聚合告警（连续 N 日有效参数不足即出声）→ 验证法=全 None 构造跑链对照。
- **F-A1/A2（P2）两处双承载**：#1 映射与 #8 HHI 各两份实现 → 建议各抽单一真源函数（与 D05/D11 收口合并处理）→ 验证法=对拍当前相等后重构。
- **F-B2/B3/C1/D1（P3）**：index 命名契约、#12 接线悬置、opportunity 通道死、_fb_call 副本——常规队列。

## 5 挂起疑问

1. #1 双实现的行为锁：若未来 Phase 2a 系数微调（如 0.75→0.70），Phase 1 简化版是否同步——两路等价性的守护测试缺失，建议收口补对拍测试。
2. 10 号 spec §5.3.3 的 #4 time_incubation"主观无数据"——是否曾有主观规则草案（如时间周期计分），或永久 stub，归 Owner。

## 6 完备性自评

- 六轴全查：A（#1 全档+NaN 语义+PIT+双实现）、B（close/high 分离加载遗产+#9 聚合契约）、C（双重开关地位+opportunity 通道）、D（与 D11 三处同构/副本）、E（降级分支全带 WARN、幂等）、F（3 条带来源，其中 KDJ/HHI 谱系无单一定源如实记）。
- 长尾清单：①risk_features 其余 9 个系数函数的分档映射数值未逐档复算（抽审 #1）；②10 号 spec 十三参数原文对账；③各参数历史触发率画像（#7 广度 12.7%、#3 破前低 5.3% 等数字引自 D01 注释未复算）。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P1 危机地板/HHI 双实现: 挂起登记（合并裁定）。参数缺失→1.0 归断供语义批。
- 修复提交: q-0021（D03/D04 NaN 防御）。
