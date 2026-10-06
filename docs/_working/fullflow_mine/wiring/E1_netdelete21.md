---
ttl: task_bound
title: "净删21条执行报告（抽查前置）"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-05
---

# E1 净删 21 条执行报告（抽查前置）

> 授权=Owner 2026-10-04"全部执行"批复（0-3 净删 21 条候退役指标/因子：指标 15+因子 6）。
> 名单真源=docs/_working/fullflow_mine/verify/D2_formula_mining.md（§修订后三态分布+§六 33 行赋值表，已 commit）+ technical_indicator_registry.yaml + factor_registry.yaml。
> 执行会话=st-datasop-20260930（EXEC-E1，重派）；禁碰项（capability 投影册/A 队互斥清单/config/*map*.yaml/CH 侧 214 列数据）零触碰。

## 一、抽查结论（5 条，三判定类全覆盖——零翻案）

| # | 条目 | 判定类 | 册内定义复核 | D2 结论 | 全仓独立消费扫描 | 结论 |
|---|---|---|---|---|---|---|
| 1 | FCT-EVENT-003 催化分级 | 无公式 | formula=信源层级叙事（S>A>B>C），params/inputs/outputs 全空、code_path 空、candidate | §二：查无"按信源采信权重分级"量化公式标准→迁规则册 | 零代码引用；非归档引用 3 处均非消费（lifecycle JSON=probation 状态缓存、metaq e1c=generator 产枚举快照 hand_edit:forbidden、passed_candidates=PIT 审计叙事引用） | 维持删除 |
| 2 | FCT-LIQ-060 Spoofing | 无公式（弱式） | formula=CER>90-95% 经验阈值叙事，全空字段、candidate | §二：CER 90-95% 无正式监管/行业标准→迁 risk_rule | 同上零消费 | 维持删除 |
| 3 | IND-MOM-028 APO | 确认重复 | formula=APO=EMA12−EMA26 {fast:12,slow:26} | §四#1：≡MACD.DIF 同参同式，归一代表=PPO 在册 | 册内实读 IND-TREND-005 MACD DIF=EMA12−EMA26 {fast:12,slow:26} 严格同参同式；src/scripts/tests 零 ID 引用；输出列 apo 零模块外消费 | 维持删除 |
| 4 | IND-MOM-013 LWR | 确认重复 | formula=RSV=(HH9−C)/(HH9−LL9)×100=100−KDJ.RSV，参数同 {9,3,3} | §四#2：KDJ 仿射双射信号等价，WR(14) 快速版在册 | 册内实读 IND-MOM-001 KDJ RSV=(C−LL9)/(HH9−LL9)×100 同参→仿射关系成立；零 ID/列消费 | 维持删除 |
| 5 | IND-TREND-003 WMA | 融合收编 | formula=线性加权平均（权重 1..N） | §四#7：与 SMA 同低通目标仅权形异→公式收编 MA 族变体注记 | host IND-TREND-001 MA 在册（已加 absorption 注记）；零 ID/列消费 | 维持删除（host 注记落） |

抽查 5/5 维持 D2 判定，无翻案项，按批文进入全量执行。

## 二、删除执行与机核断言

- technical_indicator_registry.yaml：删 15 条整块（TREND-003/004/018/020/022/023/024/026/028/029/030/031/032+MOM-013/028），逐处 Edit，删除前原文全文存本报告 §六附表。
- factor_registry.yaml：删 6 条整块（EVENT-003/017、SENT-014、LIQ-059/060/041），同上。
- 节注释归属处置：TREND-028 块尾"M-L2 价格变换族"节注释随块删（该节 4 条全退役）；TREND-032 块尾"M-L3 回归族"节注释保留（描述的在册 STAT 条目不受本次净删影响）。
- 机核断言（yaml.safe_load，全绿）：IND 条目 143→**128**（entry_count 字段同步=128）；FCT 条目 175→**169**（本册无 entry_count 字段，断言走解析）；删除 ID 零残留；保有条目（MA/HMA/ZLEMA/KAMA/SuperSmoother/MAMA/FRAMA/KDJ/WR/PPO/MACD/SENT-023/MOM-002/EVENT-008）全数在册；全册解析态零指向删除 ID 的交叉引用（variant_of/used_by_factors 等）；ID 唯一性保持。
- diff 形态：两册合计 934 行删除/24 行插入（删除块+接缝空行收拢 3 处；插入=册头修订注记+注记行）。

## 三、册头同步

| 册 | version | 计数 | last_updated | 修订注记 |
|---|---|---|---|---|
| REG-IND-001 technical_indicator_registry | 1.6.1→1.7.0 | entry_count 143→128 | 2026-09-21→2026-10-05 | 头部注释块新增修订 2026-10-05 五行（名单/留痕指针/融合收编/转考试/CH 数据不动声明）；description 内"注册 143 条含退役 1"→"注册 128 条含退役 1，2026-10-05 D2 净删 15 条见头部修订注记" |
| REG-FCT-001 factor_registry | 1.3.1→1.4.0 | 条目数 175→169（无 entry_count 字段） | 2026-08-28→2026-10-05 | 头部注释块新增修订 2026-10-05 五行（同构） |

## 四、融合收编注记（6 host 承载 7 条，YAML 注释行，不改 schema）

| host | 收编内容 |
|---|---|
| IND-TREND-001 MA | WMA(003 线性加权)/TRIMA(023 双 SMA 级联)=SMA 低通族变体 |
| IND-TREND-012 HMA | DEMA(004)/TEMA(022)=零滞后同目标簇变体（与 ZLEMA 共同承载） |
| IND-TREND-013 ZLEMA | DEMA(004)/TEMA(022)=零滞后同目标簇变体（与 HMA 共同承载） |
| IND-TREND-035 SuperSmoother | T3(024 Tillson 六重 EMA vfactor 0.7)=低通平滑同目标簇变体 |
| IND-TREND-014 KAMA | VIDYA(026 CMO 效率驱动)=ER 同族变体 |
| FCT-SENT-023 guard_ratio | FCT-LIQ-041：510300/510050 清单+"托底非进攻"语义（复活时并入 usage） |

JMA 官方式专有无正典公式可收编，仅近似口径留痕于 D2 §二，不列融合（D2 §七同口径）。

## 五、转考试标注（4 条，exam_queue 注释行）

| 条目 | 考试轴 |
|---|---|
| IND-TREND-025 MAMA | S2：对 KAMA 基线正交性/IC 增量（Hilbert 周期驱动机制异族；TA-Lib 黄金对照可得） |
| IND-TREND-027 FRAMA | S2 同轴并考（分形维数 D 驱动，机制异族边界情形） |
| FCT-MOM-002 半导体带指数 | 公式已找回：板块/宽基 RS+12 月相对高点回撤≥15% 预警（[A股,美股]） |
| FCT-EVENT-008 黄金避险因子 | 公式已找回：Baur-Lucey 阈值回归（518880×宽基；[A股,美股,期货,币圈]） |

## 六、移交与边界声明

1. CH 侧 214 列历史数据不动（本次零数据操作）；停止新增计算的产线工单另批。
2. 非消费态引用留盘不清洗（机生/历史件）：data/runtime/factor_lifecycle_state.json（probation 状态缓存，随运行时自愈）、data/registers/metaq_e1c/e1c_space_cmb_e1c_v1.yaml（generator 产枚举快照 v1.0.0，hand_edit: forbidden，重生成时自然收敛）、docs/_working 归档与战役件（历史留痕）。
3. 字段方案落册（application_markets/usage_note 三册 schema v2.2+605 条生成器回填）=D2 §五待批工单，本批未触碰。
4. 全仓其他引用扫描口径：src/scripts/tests 零 ID 引用；docs/config 命中仅册本身+D2/L12 战役件+2026-09 归档 prereview.csv+decision_map 连接矩阵（历史战役件）。
5. 本报告文件留盘移交（未随净删批 commit）：batch_creation_tokens.py 首跑成功插入 capability_canonical_file_registry.yaml（token=e1-netdelete-e1-netdelete21-20261004），但主区该册正处于多会话陈旧快照覆写战争（st-mapcb-survey-20261005 commit 8ceaf27dce 披露同型事故：插针两度蒸发+staged 陈旧快照 vs HEAD 缺 4040 行）——本会话插针同样被覆写蒸发（实证：git diff 零残留），且当前 index 停留陈旧快照态，无安全落针窗口。按批文"投影册拒收则留盘移交"条款处置：净删两册先行落地，本报告+token 补登（文件已正名 snake_case 避 N-01/N-13 命名门）移交继任会话，待热册战争平息后重跑 batch_creation_tokens.py + 内容批。

## 七、附表：21 条删除前原文（逐字存档）

### 七.1 指标册 15 条

```yaml
- indicator_id: IND-TREND-003
  name: WMA
  name_zh: 加权移动平均
  aliases: []
  indicator_class: trend
  formula: WMA=N 日收盘价线性加权平均（权重 1..N，近期权重高）
  params: {period: 10}
  inputs: [close]
  outputs: [wma_10]
  warmup_period: 10
  computation_mode: vectorized
  module_id: MOD-L02-021
  doc_ref: 16_technical_indicator_catalog.md §6.1
  code_path: src/zephyr/factor/technical_indicators/trend.py
  used_by_factors: []
  status: active
  version: 1.0.0
  created_at: '2026-08-13'
  updated_at: '2026-08-13'
  owner: MOD-GOVERNANCE
  primary_timeframe: "daily"
  applicable_timeframes: ["1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "state"
  applies_to: []
  tags: ["趋势", "均线", "组合"]
  algorithm_status: "quantized"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- indicator_id: IND-TREND-004
  name: DEMA
  name_zh: 双指数移动平均
  aliases: []
  indicator_class: trend
  formula: DEMA=2×EMA−EMA(EMA)，减少 EMA 滞后，adjust=False 对齐通达信
  params: {period: 12}
  inputs: [close]
  outputs: [dema_12]
  warmup_period: 24
  computation_mode: vectorized
  module_id: MOD-L02-021
  doc_ref: 16_technical_indicator_catalog.md §6.1
  code_path: src/zephyr/factor/technical_indicators/trend.py
  used_by_factors: []
  status: active
  version: 1.0.0
  created_at: '2026-08-13'
  updated_at: '2026-08-13'
  owner: MOD-GOVERNANCE
  primary_timeframe: "daily"
  applicable_timeframes: ["1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "state"
  applies_to: ["index"]
  tags: ["趋势", "均线", "指数"]
  algorithm_status: "quantized"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- indicator_id: IND-TREND-018
  name: BBI
  name_zh: 多空指数
  aliases: ["Bull and Bear Index"]
  indicator_class: trend
  formula: BBI=(MA3+MA6+MA12+MA24)/4
  params: {periods: [3, 6, 12, 24]}
  inputs: [close]
  outputs: [bbi]
  warmup_period: 24
  computation_mode: vectorized
  module_id: MOD-L02-021
  doc_ref: 16_technical_indicator_catalog.md §6.1
  code_path: src/zephyr/factor/technical_indicators/trend.py
  used_by_factors: []
  status: active
  version: 1.0.0
  created_at: '2026-09-14'
  updated_at: '2026-09-14'
  owner: MOD-GOVERNANCE
  primary_timeframe: "daily"
  applicable_timeframes: ["1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "state"
  applies_to: []
  tags: ["趋势", "均线", "指标"]
  algorithm_status: "quantized"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- indicator_id: IND-TREND-020
  name: GMMA
  name_zh: 顾比复合均线
  aliases: ["Guppy Multiple MA"]
  indicator_class: trend
  formula: 短期组 EMA3-15 与长期组 EMA30-60 共 12 条；组收敛/发散判趋势
  params: {short: [3, 5, 8, 10, 12, 15], long: [30, 35, 40, 45, 50, 60]}
  inputs: [close]
  outputs: [gmma_s3, gmma_s5, gmma_s8, gmma_s10, gmma_s12, gmma_s15, gmma_l30, gmma_l35, gmma_l40, gmma_l45, gmma_l50, gmma_l60]
  warmup_period: 60
  computation_mode: vectorized
  module_id: MOD-L02-021
  doc_ref: 16_technical_indicator_catalog.md §6.1
  code_path: src/zephyr/factor/technical_indicators/trend.py
  used_by_factors: []
  status: active
  version: 1.0.0
  created_at: '2026-09-15'
  updated_at: '2026-09-15'
  owner: MOD-GOVERNANCE
  primary_timeframe: "daily"
  applicable_timeframes: ["1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "state"
  applies_to: []
  tags: ["趋势", "均线", "指标"]
  algorithm_status: "quantized"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- indicator_id: IND-TREND-022
  name: Triple Exponential Moving Average
  name_zh: 三重指数移动平均
  aliases: ["TEMA", "Triple EMA"]
  indicator_class: trend
  formula: e1=EMA(C,N)；e2=EMA(e1,N)；e3=EMA(e2,N)；TEMA=3e1−3e2+e3（EMA adjust=False 种子=首值）
  params: {period: 10}
  inputs: [close]
  outputs: [tema_10]
  warmup_period: 1
  computation_mode: vectorized
  module_id: MOD-L02-021
  doc_ref: 16_technical_indicator_catalog.md §6.1
  code_path: src/zephyr/factor/technical_indicators/trend.py
  used_by_factors: []
  status: active
  version: 1.0.0
  created_at: '2026-09-20'
  updated_at: '2026-09-20'
  owner: MOD-GOVERNANCE
  primary_timeframe: "daily"
  applicable_timeframes: ["1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "state"
  applies_to: []
  tags: ["趋势", "均线", "指标"]
  algorithm_status: "quantized"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- indicator_id: IND-TREND-023
  name: Triangular Moving Average
  name_zh: 三角移动平均
  aliases: ["TRIMA"]
  indicator_class: trend
  formula: 偶窗 N=10：SMA(SMA(C,N/2),N/2+1)=SMA(SMA(C,5),6)；奇窗：双 (N+1)/2 级联（TA-Lib 口径，实测 lookback=9 一致）
  params: {period: 10}
  inputs: [close]
  outputs: [trima_10]
  warmup_period: 10
  computation_mode: vectorized
  module_id: MOD-L02-021
  doc_ref: 16_technical_indicator_catalog.md §6.1
  code_path: src/zephyr/factor/technical_indicators/trend.py
  used_by_factors: []
  status: active
  version: 1.0.0
  created_at: '2026-09-20'
  updated_at: '2026-09-20'
  owner: MOD-GOVERNANCE
  primary_timeframe: "daily"
  applicable_timeframes: ["1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "state"
  applies_to: []
  tags: ["趋势", "均线", "指标"]
  algorithm_status: "quantized"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- indicator_id: IND-TREND-024
  name: Tillson T3
  name_zh: T3均线
  aliases: ["T3", "Tillson Moving Average"]
  indicator_class: trend
  formula: e1..e6=六重 EMA(C,N) 链；c1=−a³,c2=3a²+3a³,c3=−6a²−3a−3a³,c4=1+3a+a³+3a²；T3=c1e6+c2e5+c3e4+c4e3（Tillson，a=vfactor=0.7）
  params: {period: 10, vfactor: 0.7}
  inputs: [close]
  outputs: [t3_10]
  warmup_period: 1
  computation_mode: vectorized
  module_id: MOD-L02-021
  doc_ref: 16_technical_indicator_catalog.md §6.1
  code_path: src/zephyr/factor/technical_indicators/trend.py
  used_by_factors: []
  status: active
  version: 1.0.0
  created_at: '2026-09-20'
  updated_at: '2026-09-20'
  owner: MOD-GOVERNANCE
  primary_timeframe: "daily"
  applicable_timeframes: ["1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "state"
  applies_to: []
  tags: ["趋势", "均线", "指标"]
  algorithm_status: "quantized"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- indicator_id: IND-TREND-026
  name: Variable Index Dynamic Average
  name_zh: 可变指数动态均线
  aliases: ["VIDYA", "Chande VIDYA"]
  indicator_class: trend
  formula: alpha=|CMO(C,cmo_period)|/100×2/(N+1)；VIDYA=alpha·C+(1−alpha)·VIDYA_prev（Chande；种子=首个 CMO 有效当根收盘）
  params: {period: 14, cmo_period: 9}
  inputs: [close]
  outputs: [vidya_14]
  warmup_period: 10
  computation_mode: vectorized
  module_id: MOD-L02-021
  doc_ref: 16_technical_indicator_catalog.md §6.1
  code_path: src/zephyr/factor/technical_indicators/trend.py
  used_by_factors: []
  status: active
  version: 1.0.0
  created_at: '2026-09-20'
  updated_at: '2026-09-20'
  owner: MOD-GOVERNANCE
  primary_timeframe: "daily"
  applicable_timeframes: ["1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "state"
  applies_to: []
  tags: ["趋势", "均线", "指标"]
  algorithm_status: "quantized"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- indicator_id: IND-TREND-028
  name: Jurik Moving Average
  name_zh: Jurik自适应均线
  aliases: ["JMA", "Jurik JMA"]
  indicator_class: trend
  formula: Jurik 开源移植（pandas-ta 经典口径）：beta=0.45(N−1)/(0.45+2(N−1))，alpha=beta^phaseRatio 递推平滑+波动压缩链（phase=50, power=2 默认）
  params: {period: 7, phase: 50, power: 2}
  inputs: [close]
  outputs: [jma_7]
  warmup_period: 7
  computation_mode: vectorized
  module_id: MOD-L02-021
  doc_ref: 16_technical_indicator_catalog.md §6.1
  code_path: src/zephyr/factor/technical_indicators/trend.py
  used_by_factors: []
  status: active
  version: 1.0.0
  created_at: '2026-09-20'
  updated_at: '2026-09-20'
  owner: MOD-GOVERNANCE
  primary_timeframe: "daily"
  applicable_timeframes: ["1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "state"
  applies_to: []
  tags: ["趋势", "均线", "指标"]
  algorithm_status: "quantized"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

# ══════════════ 趋势类扩充批9-1：M-L2 价格变换族（4 指标/4 列，2026-09-20 tilib 清欠班）══════════════

- indicator_id: IND-TREND-029
  name: Average Price
  name_zh: 四价均价
  aliases: ["AVGPRICE", "ohlc4"]
  indicator_class: trend
  formula: AVGPRICE=(O+H+L+C)/4（TA-Lib Price Transform 组）
  params: {}
  inputs: [open, high, low, close]
  outputs: [avgprice]
  warmup_period: 1
  computation_mode: vectorized
  module_id: MOD-L02-021
  doc_ref: 16_technical_indicator_catalog.md §6.1
  code_path: src/zephyr/factor/technical_indicators/trend.py
  used_by_factors: []
  status: active
  version: 1.0.0
  created_at: '2026-09-20'
  updated_at: '2026-09-20'
  owner: MOD-GOVERNANCE
  primary_timeframe: "daily"
  applicable_timeframes: ["1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "state"
  applies_to: []
  tags: ["基准", "趋势", "指标"]
  algorithm_status: "quantized"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- indicator_id: IND-TREND-030
  name: Median Price
  name_zh: 中价
  aliases: ["MEDPRICE", "hl2"]
  indicator_class: trend
  formula: MEDPRICE=(H+L)/2（TA-Lib Price Transform 组）
  params: {}
  inputs: [high, low]
  outputs: [medprice]
  warmup_period: 1
  computation_mode: vectorized
  module_id: MOD-L02-021
  doc_ref: 16_technical_indicator_catalog.md §6.1
  code_path: src/zephyr/factor/technical_indicators/trend.py
  used_by_factors: []
  status: active
  version: 1.0.0
  created_at: '2026-09-20'
  updated_at: '2026-09-20'
  owner: MOD-GOVERNANCE
  primary_timeframe: "daily"
  applicable_timeframes: ["1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "state"
  applies_to: []
  tags: ["基准", "趋势", "指标"]
  algorithm_status: "quantized"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- indicator_id: IND-TREND-031
  name: Typical Price
  name_zh: 典型价格
  aliases: ["TYPPRICE", "hlc3"]
  indicator_class: trend
  formula: TYPPRICE=(H+L+C)/3（TA-Lib Price Transform 组）
  params: {}
  inputs: [high, low, close]
  outputs: [typprice]
  warmup_period: 1
  computation_mode: vectorized
  module_id: MOD-L02-021
  doc_ref: 16_technical_indicator_catalog.md §6.1
  code_path: src/zephyr/factor/technical_indicators/trend.py
  used_by_factors: []
  status: active
  version: 1.0.0
  created_at: '2026-09-20'
  updated_at: '2026-09-20'
  owner: MOD-GOVERNANCE
  primary_timeframe: "daily"
  applicable_timeframes: ["1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "state"
  applies_to: []
  tags: ["基准", "趋势", "指标"]
  algorithm_status: "quantized"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- indicator_id: IND-TREND-032
  name: Weighted Close Price
  name_zh: 加权收盘价
  aliases: ["WCPRICE", "WCLPRICE"]
  indicator_class: trend
  formula: WCPRICE=(H+L+2×C)/4（收盘双倍权重；TA-Lib WCLPRICE 同义）
  params: {}
  inputs: [high, low, close]
  outputs: [wcprice]
  warmup_period: 1
  computation_mode: vectorized
  module_id: MOD-L02-021
  doc_ref: 16_technical_indicator_catalog.md §6.1
  code_path: src/zephyr/factor/technical_indicators/trend.py
  used_by_factors: []
  status: active
  version: 1.0.0
  created_at: '2026-09-20'
  updated_at: '2026-09-20'
  owner: MOD-GOVERNANCE
  primary_timeframe: "daily"
  applicable_timeframes: ["1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "state"
  applies_to: []
  tags: ["基准", "趋势", "指标"]
  algorithm_status: "quantized"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

# ══════════════ 统计族扩充批9-1：M-L3 回归族（4 指标/4 列，2026-09-20 tilib 清欠班）══════════════
# 立条裁定：M-L3 清单"LINEARREG_BAR"与既有 IND-STAT-003 LINEARREG 本体同义不重复立条；STDERR 除数 N−2 经 talib 对照实测钉死

- indicator_id: IND-MOM-013
  name: LWR
  name_zh: 慢速威廉
  aliases: ["LWR", "LW&R"]
  indicator_class: momentum
  formula: RSV=(HH9−C)/(HH9−LL9)×100；LWR1=SMA(RSV,3,1)；LWR2=SMA(LWR1,3,1)（威廉口径，方向与KDJ相反）
  params: {period: 9, k_smooth: 3, d_smooth: 3}
  inputs: [high, low, close]
  outputs: [lwr_1, lwr_2]
  warmup_period: 15
  computation_mode: vectorized
  module_id: MOD-L02-019
  doc_ref: 16_technical_indicator_catalog.md §6.2
  code_path: src/zephyr/factor/technical_indicators/momentum.py
  used_by_factors: []
  status: active
  version: 1.0.0
  created_at: '2026-09-14'
  updated_at: '2026-09-14'
  owner: MOD-GOVERNANCE
  primary_timeframe: "daily"
  applicable_timeframes: ["1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "state"
  applies_to: []
  tags: ["动量", "超买", "超跌", "指标"]
  algorithm_status: "quantized"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- indicator_id: IND-MOM-028
  name: APO
  name_zh: 绝对价格振荡器
  aliases: ["Absolute Price Oscillator"]
  indicator_class: momentum
  formula: APO=EMA12−EMA26（绝对差值）
  params: {fast: 12, slow: 26}
  inputs: [close]
  outputs: [apo]
  warmup_period: 26
  computation_mode: vectorized
  module_id: MOD-L02-019
  doc_ref: 16_technical_indicator_catalog.md §6.2
  code_path: src/zephyr/factor/technical_indicators/momentum.py
  used_by_factors: []
  status: active
  version: 1.0.0
  created_at: '2026-09-14'
  updated_at: '2026-09-14'
  owner: MOD-GOVERNANCE
  primary_timeframe: "daily"
  applicable_timeframes: ["1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "state"
  applies_to: []
  tags: ["动量", "趋势", "指标"]
  algorithm_status: "quantized"
  evidence: ""
  code_symbol: null
  code_fingerprint: null
```

### 七.2 因子册 6 条

```yaml
- factor_id: "FCT-EVENT-003"
  name: "催化分级"
  name_zh: "催化分级"
  aliases: ["S>A>B>C", "政策行政级别分级"]
  factor_class: "event"
  formula: "消息面催化分级采信——S 级（新华社/官方公告）>A 级（交易所公告/业绩）>B 级（券商研报）>C 级（自媒体）。低级别消息需高级别消息确认。"
  params: {}
  inputs: []
  outputs: []
  alpha_source: "消息源可信度分级=事件质量的标准分层（官方>交易所>研报>自媒体），与 F6.52 行政级别分级构成双维。"
  frequency: "daily"
  lookback_period: 1
  universe: "UNI-RULE-001"
  benchmark_id: "BMK-INDEX-001"
  neutralization: "none"
  pit_policy: "price_only"
  module_id: "MOD-L02-001"
  doc_ref: "29_factor_strategy_extraction.md §F6.19（吸收 F6.52）"
  code_path: ""
  belongs_to_strategies: []
  variant_of: null
  status: "candidate"
  version: "1.0.0"
  created_at: "2026-08-15"
  updated_at: "2026-08-15"
  owner: "MOD-GOVERNANCE"
  ic: null
  ir: null
  decay_halflife: null
  decay_detection_method: null
  last_decay_scan_at: null
  turnover: null
  capacity: null
  last_evaluated_at: null
  data_quality_policy:
    null_rate: {threshold: 0.02, window: "1d"}
    drift_method: "psi"
    drift_threshold: 0.2
    freshness: {staleness_sla: "2d"}
    semantic_contract:
      null_semantics: "null=未计算/未产生（非零值），禁止零填充"
      default_fill_policy: "none"
  null_rate: null
  drift_psi: null
  drift_ks_pvalue: null
  last_quality_scan_at: null
  correlation_group: null
  redundancy_status: null
  causal_graph: null
  causal_structure: null
  attribution_stability: null
  lib_audit: null
  ex_post_filter_audit: null
  schema_plan: null
  liquidity_metric: null
  llm_safety_stack: null
  version_pin: null
  code_commit: null
  range_bounds: {}
  rmt_denoised: {"applicable": false, "reason": "low_factor_count"}
  discovery_agent: "human"
  primary_timeframe: "daily"
  applicable_timeframes: ["daily"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "ranking"
  applies_to: ["stock"]
  tags: ["事件"]
  algorithm_status: "pending_backtest"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- factor_id: "FCT-EVENT-017"
  name: "事件因果图与贝叶斯网络推断"
  name_zh: "事件因果图与贝叶斯网络推断"
  aliases: ["产业证据链交叉"]
  factor_class: "event"
  formula: "用 DAG 建模事件间因果关系——事件 A→事件 B 的 Granger 因果性检验+P(B|A) 贝叶斯网络条件概率推断，替代\"征兆推理\"直觉。为 F6.21 产业证据链交叉的学术框架（方法论框架条目）。"
  params: {}
  inputs: []
  outputs: []
  alpha_source: "DAG+Granger 因果+贝叶斯网络=事件因果推断的学术框架，方法论级条目。"
  frequency: "daily"
  lookback_period: 1
  universe: "UNI-RULE-001"
  benchmark_id: "BMK-INDEX-001"
  neutralization: "none"
  pit_policy: "price_only"
  module_id: "MOD-L02-001"
  doc_ref: "29_factor_strategy_extraction.md §F6.55（吸收 F6.21）"
  code_path: ""
  belongs_to_strategies: []
  variant_of: null
  status: "candidate"
  version: "1.0.0"
  created_at: "2026-08-15"
  updated_at: "2026-08-15"
  owner: "MOD-GOVERNANCE"
  ic: null
  ir: null
  decay_halflife: null
  decay_detection_method: null
  last_decay_scan_at: null
  turnover: null
  capacity: null
  last_evaluated_at: null
  data_quality_policy:
    null_rate: {threshold: 0.02, window: "1d"}
    drift_method: "psi"
    drift_threshold: 0.2
    freshness: {staleness_sla: "2d"}
    semantic_contract:
      null_semantics: "null=未计算/未产生（非零值），禁止零填充"
      default_fill_policy: "none"
  null_rate: null
  drift_psi: null
  drift_ks_pvalue: null
  last_quality_scan_at: null
  correlation_group: null
  redundancy_status: null
  causal_graph: null
  causal_structure: null
  attribution_stability: null
  lib_audit: null
  ex_post_filter_audit: null
  schema_plan: null
  liquidity_metric: null
  llm_safety_stack: null
  version_pin: null
  code_commit: null
  range_bounds: {}
  rmt_denoised: {"applicable": false, "reason": "low_factor_count"}
  discovery_agent: "human"
  primary_timeframe: "daily"
  applicable_timeframes: ["daily"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "ranking"
  applies_to: ["stock"]
  tags: ["事件"]
  algorithm_status: "pending_backtest"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- factor_id: "FCT-SENT-014"
  name: "逼空检测量化"
  name_zh: "逼空检测量化"
  aliases: ["个股口径", "逼空行情盘面三特征与应对"]
  factor_class: "sentiment"
  formula: "Utilization>80%+Days to Cover>5 天=高逼空前提；Squeeze Score>10 且 Utilization>30%=Alert（标的平均最大涨幅 33%）；尾盘拉升幅度>全天 50% 且量能集中=疑似逼空平仓；区分真启动：真实启动开盘 30min 量能占比>30%+板块广度>60%，逼空尾盘量能占比>30%+广度<30%。与 F7.25（指数/盘面口径）并列。"
  params: {}
  inputs: []
  outputs: []
  alpha_source: "逼空检测=美股做空指标口径（Utilization 借券利用率/Days to Cover 回补天数/Squeeze Score，IHS Markit 模型同源）；A股无个股做空数据，需用融券余额/融券卖出量代理——数据可得性标注。"
  frequency: "daily"
  lookback_period: 1
  universe: "UNI-RULE-001"
  benchmark_id: "BMK-INDEX-001"
  neutralization: "none"
  pit_policy: "price_only"
  module_id: "MOD-L02-001"
  doc_ref: "29_factor_strategy_extraction.md §F7.37（吸收 F7.25）"
  code_path: ""
  belongs_to_strategies: []
  variant_of: null
  status: "candidate"
  version: "1.0.0"
  created_at: "2026-08-15"
  updated_at: "2026-08-15"
  owner: "MOD-GOVERNANCE"
  ic: null
  ir: null
  decay_halflife: null
  decay_detection_method: null
  last_decay_scan_at: null
  turnover: null
  capacity: null
  last_evaluated_at: null
  data_quality_policy:
    null_rate: {threshold: 0.02, window: "1d"}
    drift_method: "psi"
    drift_threshold: 0.2
    freshness: {staleness_sla: "2d"}
    semantic_contract:
      null_semantics: "null=未计算/未产生（非零值），禁止零填充"
      default_fill_policy: "none"
  null_rate: null
  drift_psi: null
  drift_ks_pvalue: null
  last_quality_scan_at: null
  correlation_group: null
  redundancy_status: null
  causal_graph: null
  causal_structure: null
  attribution_stability: null
  lib_audit: null
  ex_post_filter_audit: null
  schema_plan: null
  liquidity_metric: null
  llm_safety_stack: null
  version_pin: null
  code_commit: null
  range_bounds: {}
  rmt_denoised: {"applicable": false, "reason": "low_factor_count"}
  discovery_agent: "human"
  primary_timeframe: "daily"
  applicable_timeframes: ["daily"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "ranking"
  applies_to: ["stock"]
  tags: ["尾盘", "指数"]
  algorithm_status: "pending_backtest"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- factor_id: "FCT-LIQ-041"
  name: "ETF 成交异动"
  name_zh: "ETF 成交异动"
  aliases: ["国家队护盘识别", "国家队震仓行为", "外力尾盘 V 反 vs 自发企稳区分", "护盘式诱多", "护盘识别"]
  factor_class: "liquidity"
  formula: "510300/510050 ETF 分钟级成交异动识别国家队护盘。异常放量柱+拉抬时段对应=国家队在场。护盘驱动的反弹蓝筹继续强，但护盘蓝筹是\"托底工具\"不是\"进攻标的\"。"
  params: {}
  inputs: []
  outputs: []
  alpha_source: "护盘识别=宽基 ETF 分钟级异常放量+时段对应，与 F7.15（外力 V 反）互为印证。震仓/洗盘识别采五维证伪框架（洗盘不可证实只能证伪）：位置（首波上涨后中低位）/量能（回调缩量≤均量1/2）/支撑（关键位不破或破位快速收回）/筹码峰（底部峰稳定不动）/资金（大单流出不持续）；震仓可量化判据=振幅>5% 且 |收盘变化|<1% 且底部筹码峰不动。（v1.3.0 补写）"
  frequency: "daily"
  lookback_period: 1
  universe: "UNI-RULE-001"
  benchmark_id: "BMK-INDEX-001"
  neutralization: "none"
  pit_policy: "price_only"
  module_id: "MOD-L02-001"
  doc_ref: "29_factor_strategy_extraction.md §F8.17（吸收 F7.15/F8.9/F8.18/F8.47）"
  code_path: ""
  belongs_to_strategies: []
  variant_of: null
  status: "candidate"
  version: "1.0.0"
  created_at: "2026-08-15"
  updated_at: "2026-08-15"
  owner: "MOD-GOVERNANCE"
  ic: null
  ir: null
  decay_halflife: null
  decay_detection_method: null
  last_decay_scan_at: null
  turnover: null
  capacity: null
  last_evaluated_at: null
  data_quality_policy:
    null_rate: {threshold: 0.02, window: "1d"}
    drift_method: "psi"
    drift_threshold: 0.2
    freshness: {staleness_sla: "2d"}
    semantic_contract:
      null_semantics: "null=未计算/未产生（非零值），禁止零填充"
      default_fill_policy: "none"
  null_rate: null
  drift_psi: null
  drift_ks_pvalue: null
  last_quality_scan_at: null
  correlation_group: null
  redundancy_status: null
  causal_graph: null
  causal_structure: null
  attribution_stability: null
  lib_audit: null
  ex_post_filter_audit: null
  schema_plan: null
  liquidity_metric: null
  llm_safety_stack: null
  version_pin: null
  code_commit: null
  range_bounds: {}
  rmt_denoised: {"applicable": false, "reason": "low_factor_count"}
  discovery_agent: "human"
  primary_timeframe: "daily"
  applicable_timeframes: ["daily"]
  regime_valid: ["high_vol"]
  regime_invalid: []
  direction: "long"
  entry_role: "ranking"
  applies_to: ["stock"]
  tags: ["成交", "持续", "支撑", "放量", "缩量", "资金"]
  algorithm_status: "pending_backtest"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- factor_id: "FCT-LIQ-059"
  name: "协同交易监管级检测阈值"
  name_zh: "协同交易监管级检测阈值"
  aliases: []
  factor_class: "liquidity"
  formula: "幌骗=偏离≥2%+申报量≥10%+5 秒内撤单≥80%；对敲=间隔≤5 秒+偏离≤1%+占比≥5%；关联账户=同步报撤单≥60%+方向一致≥80%；异常波动=2 分钟涨跌≥2%+程序化占比≥50%（沪深北 2025.7 细则）；护盘=整数关口买一挂单>日均成交 5% 且持续>30 分钟；买五/卖五挂单>日均成交 10% 且 5 分钟未成交=信号释放；政策响应<2 小时=预期管理。"
  params: {}
  inputs: []
  outputs: []
  alpha_source: "监管级检测阈值（对标沪深北 2025.7 程序化交易细则）=操纵检测的合规口径参数。"
  frequency: "daily"
  lookback_period: 1
  universe: "UNI-RULE-001"
  benchmark_id: "BMK-INDEX-001"
  neutralization: "none"
  pit_policy: "price_only"
  module_id: "MOD-L02-001"
  doc_ref: "29_factor_strategy_extraction.md §F8.59"
  code_path: ""
  belongs_to_strategies: []
  variant_of: null
  status: "candidate"
  version: "1.0.0"
  created_at: "2026-08-15"
  updated_at: "2026-08-15"
  owner: "MOD-GOVERNANCE"
  ic: null
  ir: null
  decay_halflife: null
  decay_detection_method: null
  last_decay_scan_at: null
  turnover: null
  capacity: null
  last_evaluated_at: null
  data_quality_policy:
    null_rate: {threshold: 0.02, window: "1d"}
    drift_method: "psi"
    drift_threshold: 0.2
    freshness: {staleness_sla: "2d"}
    semantic_contract:
      null_semantics: "null=未计算/未产生（非零值），禁止零填充"
      default_fill_policy: "none"
  null_rate: null
  drift_psi: null
  drift_ks_pvalue: null
  last_quality_scan_at: null
  correlation_group: null
  redundancy_status: null
  causal_graph: null
  causal_structure: null
  attribution_stability: null
  lib_audit: null
  ex_post_filter_audit: null
  schema_plan: null
  liquidity_metric: null
  llm_safety_stack: null
  version_pin: null
  code_commit: null
  range_bounds: {}
  rmt_denoised: {"applicable": false, "reason": "low_factor_count"}
  discovery_agent: "human"
  primary_timeframe: "daily"
  applicable_timeframes: ["daily"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "ranking"
  applies_to: ["stock"]
  tags: ["信号", "成交", "持续"]
  algorithm_status: "pending_backtest"
  evidence: ""
  code_symbol: null
  code_fingerprint: null

- factor_id: "FCT-LIQ-060"
  name: "Spoofing 检测指标"
  name_zh: "Spoofing 检测指标"
  aliases: []
  factor_class: "liquidity"
  formula: "CER（撤单/成交比）>90-95%（100ms 窗口）=幌骗嫌疑；大单存续<100ms-1 秒即撤=虚假挂单；Spoof 概率>85%→暂停追涨。"
  params: {}
  inputs: []
  outputs: []
  alpha_source: "幌骗检测（Spoofing）=撤单率+挂单存续时长的标准微观结构检测。"
  frequency: "daily"
  lookback_period: 1
  universe: "UNI-RULE-001"
  benchmark_id: "BMK-INDEX-001"
  neutralization: "none"
  pit_policy: "price_only"
  module_id: "MOD-L02-001"
  doc_ref: "29_factor_strategy_extraction.md §F8.60"
  code_path: ""
  belongs_to_strategies: []
  variant_of: null
  status: "candidate"
  version: "1.0.0"
  created_at: "2026-08-15"
  updated_at: "2026-08-15"
  owner: "MOD-GOVERNANCE"
  ic: null
  ir: null
  decay_halflife: null
  decay_detection_method: null
  last_decay_scan_at: null
  turnover: null
  capacity: null
  last_evaluated_at: null
  data_quality_policy:
    null_rate: {threshold: 0.02, window: "1d"}
    drift_method: "psi"
    drift_threshold: 0.2
    freshness: {staleness_sla: "2d"}
    semantic_contract:
      null_semantics: "null=未计算/未产生（非零值），禁止零填充"
      default_fill_policy: "none"
  null_rate: null
  drift_psi: null
  drift_ks_pvalue: null
  last_quality_scan_at: null
  correlation_group: null
  redundancy_status: null
  causal_graph: null
  causal_structure: null
  attribution_stability: null
  lib_audit: null
  ex_post_filter_audit: null
  schema_plan: null
  liquidity_metric: null
  llm_safety_stack: null
  version_pin: null
  code_commit: null
  range_bounds: {}
  rmt_denoised: {"applicable": false, "reason": "low_factor_count"}
  discovery_agent: "human"
  primary_timeframe: "daily"
  applicable_timeframes: ["daily"]
  regime_valid: []
  regime_invalid: []
  direction: "neutral"
  entry_role: "ranking"
  applies_to: ["stock"]
  tags: ["成交"]
  algorithm_status: "pending_backtest"
  evidence: ""
  code_symbol: null
  code_fingerprint: null
```
