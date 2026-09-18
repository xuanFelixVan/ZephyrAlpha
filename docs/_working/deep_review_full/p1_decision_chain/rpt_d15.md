---
ttl: task_bound
doc_type: report
title: 深度审查报告——波动率告警器（D15）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：波动率告警器（D15）

- 状态: **已审**
- 级别: P1｜类型: 算法（GARCH(1,1) 预测+RV 压缩+突变告警）
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/regime/volatility_regime_alerter.py:112(VolatilityRegimeAlerter.assess:171)`（223 行全文通读）
- 生产调用方: **零消费（查无）**——全仓 grep `VolatilityRegimeAlerter/VolRegimeSignal/vol_compression/vol_shift_alert/vol_forecast_score` 无生产接线；`overlay_dims()` 契约声明的消费方 overlay_signals_builder **不消费**（其 32 维契约无 vol_* 键，D11 已枚举核实）；头栏自认"运行时装配批接线"未落地，但 `MATURITY=production` 与零消费矛盾（注册表漂移，同 D04/D07 家族）
- 测试文件: `tests/regime/test_volatility_regime_alerter.py`（10 测试）

## 1 对象快照

- 审查范围：三件套（GARCH 预测/RV 压缩/突变告警）+overlay_dims 映射+降级路径。排除项：`risk/core/fhs_engine` 本体（MOD-RK-26，P0 钱路径对象归其域审——本模块只核消费面契约：garch_converged/sigma_forecast/fallback 标志）；`volatility_squeeze_breakout.py`（兄弟模块，自判其域）。
- 材料包缺项声明：fhs_engine 的 sigma_forecast 口径（次日条件波动年化前）未回读源码核对；GARCH 在 A 股指数上的拟合质量画像未取。
- 测试覆盖概况：10 测试（配置校验/降级/映射）。
- 变更热力：3 次。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | F-A1 **MATURITY=production 与零消费矛盾**：三件套全部产出无下游；overlay_dims 三键不在 D01 8 转换契约内——"告警"当前告给空气；与 D04/D07 同族成熟度漂移（头栏自洽性缺陷非代码缺陷） | 头栏 :5-8 vs grep 结果; overlay_signals_builder.py:95-126（32 维无 vol_*） | P2 | grep 复核（本审查已做） |
| A | F-A2 RV 口径与边界正确：5/20 日 std×√252 年化、rv_ratio 短/长比、长窗零波动→inf（compression_flag 恒 0 不误报压缩）——死数据语义安全；ddof=1 样本方差 | volatility_regime_alerter.py:192-196 | 已查无 | 常数序列跑 assess |
| A | F-A3 shift_ratio 语义自洽：GARCH 条件波动预测/RV_20d≥1.5=波动扩张预警（前瞻vs后视的比）；overlay_dims 线性映射 1.0→0 分、1.5→100 分、clip 截断——连续分+布尔 flag 双通道设计合规 overlay_dims 契约；shift_ratio<1（预测低于近期实现=波动衰减）→0 分不告警 ✓ 方向正确 | :139-150 | 已查无 | shift_ratio=1.2/1.5/2.0 三点映射手算 |
| A | F-A4 GARCH 消费面契约：仅当 `garch_converged 且 garch_params 非空`才采信 sigma_forecast，fallback 路径有 warning+garch_available=False 留痕——不静默吃 fallback 值当真值；FHS 异常两类型捕获降级（其余异常会炸出——assess 无兜底 except，比同域"降级不抛错"声明略弱：非 FHS 类型异常（如内存/类型错误）将上抛破坏"降级不抛错"承诺） | :202-213 vs 头栏 :8 | P3 | mock fhs.compute 抛 RuntimeError 观察上抛 |
| A | F-A5 配置校验完备（窗口序/阈值域/最小样本/模拟次数下限）Fail-Closed ✓；random_seed 固定 42 可复现 ✓ | :92-108 | 已查无 | — |
| B | F-B1 输入非有限值预过滤（:179）+FHS 内部 Fail-Closed 双层；过滤后计数参与 min_history 判定——NaN 占比高时样本缩水走降级 ✓；但过滤比例未记录（无声缩水） | :178-190 | P3 | 半 NaN 输入观察无告警降级 |
| C | F-C1 消费方=0（F-A1）；兄弟模块 volatility_squeeze_breakout 另有**自己的 overlay_dims()**（:161）同样未见消费方——模块 51 与本模块是"压缩早标记 vs 突破确认"的分工设计（docstring :27-28 声明联动），两件套双双未接线 | volatility_squeeze_breakout.py:161 | P2(同 F-A1) | grep 复核 |
| D | F-D1 与 fhs_engine 的复用纪律（自研不引 arch 库，AI-FHS-001 #1 裁定）——单点实现无第二 GARCH（grep 无 arch 库 import）✓；与 D15/D01 的 realized_vol_pct（分位口径）三套波动率度量并存（std 比/GARCH 条件波动/HV 分位）——口径分工未在单一文档对照（轻度） | 头栏 :8; 全仓 grep | P3 | 波动率度量清单表建议 |
| E | F-E1 静默失败面：降级全带 warning/degrade_reason；残余静默=①F-B1 过滤无声②F-A4 非 FHS 异常上抛（与降级声明不符，但 fail-loud 方向无害） | :178-213 | 已查无（P3 级） | — |
| E | F-E2 幂等：seed 固定+纯函数式 assess（FHSEngine 实例复用但 compute 无状态假设依赖 fhs_engine 侧——其无状态性归 P0 域审） | :156-165 | 已查无 | 双跑对拍 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| # | 对照项 | 结论 | 来源 |
|---|---|---|---|
| 1 | GARCH(1,1) 波动预测 | **对等已有**——GARCH(1,1) QMLE 是波动预测基准模型（Bollerslev 1986 谱系）；自研 L-BFGS-B 复用+fallback_to_historical 是合理工程化；业界亦有 GJR/EGARCH 非对称扩展（杠杆效应）可作后续立卡 | 模型谱系=Bollerslev 1986（Journal of Econometrics，公共引用面如实记）；阈值告警语境=[Finance Research Letters 2022: VIX predictability with dynamic thresholds](https://www.sciencedirect.com/science/article/abs/pii/S1544612322001696)（ScienceDirect，2022） |
| 2 | 波动压缩→突破（vol squeeze） | **对等已有**——低波压缩后扩张是波动聚集（volatility clustering）文献与实务（Bollinger Squeeze 谱系）标准信号；rv_ratio<0.8 早标记+模块 51 突破确认的分工设计合理 | 实务谱系=Bollinger Band squeeze（公共域，无单一定源如实记）；[Intellectia: VIX threshold bands 实务口径](https://intellectia.ai/blog/bear-market-vix-pattern)（2024-2025） |
| 3 | 突变告警阈值（预测/实现≥1.5） | **立卡候选**——1.5 倍阈值的依据未标定（docstring 无出处）；建议接线前用 A 股指数历史回放统计触发率/假阳率定标（同 D11 OVB-4 ledger 模式） | 本报告建议（改造点=VolAlerterConfig.shift_threshold 默认值定标） |

## 4 缺陷清单（按严重级）

- **F-A1/C1（P2）零消费+成熟度漂移**：建议=①MATURITY 改 trial/design 或登记接线批次；②接线时把 vol_shift_alert/vol_forecast_score 纳入 D01 8 转换契约（需扩展 TRANSITION_CONFIG 或并入 S1 的 vix_panic 复合分——接线设计评审议题）；③与 volatility_squeeze_breakout 同批决策（两件套一起接或一起冻结）→ 验证法=grep 复核。
- **F-A4（P3）非 FHS 异常上抛与"降级不抛错"声明不符**：建议 assess 加兜底 except 记 warning 返回 degraded（对齐声明）或改声明 → 验证法=mock 异常复现。
- **F-B1/D1（P3）**：过滤无声、三套波动率度量口径清单——常规队列。

## 5 挂起疑问

1. fhs_engine.sigma_forecast 的确切口径（GARCH 条件方差次日开方×√252？是否含均值方程残差调整）——本审查只验了年化乘子，口径归 fhs_engine（P0 域）审计。
2. shift_threshold=1.5 与 D01 S2 vix 门槛 30、D03 IV 35/40 的阈值族缺乏统一标定台账——regime 域阈值治理散点（跨对象挂疑问，建议收口并案建台账）。

## 6 完备性自评

- 六轴全查：A（RV/GARCH 消费面/映射/边界逐项）、B（输入过滤双层）、C（零消费核实+兄弟模块双孤儿）、D（自研单点+三度量口径）、E（降级面+幂等+异常路径）、F（3 条带来源，其中 Bollerslev/Bollinger 谱系无单一定源如实记）。
- 长尾清单：①fhs_engine 本体（P0 域）；②GARCH 在沪深300 的拟合质量画像；③shift_threshold 定标回放。
