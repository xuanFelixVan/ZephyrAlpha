---
ttl: task_bound
title: 经典指标算法疑点全网调查 v1（裁定#489① 复活条件调查面）
session: st-mx07-L1
completes_when: 裁定#489① 复议采信后随总包 promote 到 docs/03_modules/_domain_factor/ 或 Owner 例行归档窗口回收（_working 24h TTL 暂存面）
---

creation_token: classic-indicator-investigation-classic-indicator-investigation-v1-20261007
产出日: 2026-10-08
授权: 裁定#489① 复活条件调查面（Owner 质疑"这么经典，会不会是我们算法/考法有问题"）
TTL 自裁留痕: 任务卡要求文件头 [TTL] permanent；docs/_working 为 temporary zone，ttl_gate 契约强制 frontmatter ttl=task_bound（正文裸 [TTL] permanent 锚定系 ttl_gate 治本案例 2026-06-29 明令的自欺模式）——按门禁机械判定执行，promote 时升级 permanent。
红线遵守: 本车道只读代码+联网查证，零代码修改，零数据库写，未改 technical_indicator_registry 任何条目；唯一注册表写入=capability_canonical_file_registry.yaml 追加本文件 creation_token（门禁强制通道）。

# 经典指标算法疑点全网调查 v1（6 刚退役指标：算法 vs 考法三选一裁定）

## 0. 一句话结论

6 件中 **2 件实现有错**（MOM-036 SQUEEZE 三处偏离 LazyBear 声明口径、VOLUME-015 WAD 误读 Tulip 口径），**4 件实现等价或合法变体**（MOM-032 AC / VOL-016 CHOP / TREND-036 HighPass3 逐式等价、REV-003 MACD背离为合法 PIT 安全变体）；同时 **6 件全部叠加"考法错尺"问题**——横截面 5 日 rank IC 对状态/触发/零件类指标结构性趋零，|ic_5d|≈0.0004~0.0042 的考试结果不能证明"经典指标无 edge"，只能证明"它们在横截面 rank IC 尺下不是横截面 alpha 因子"。Owner 的两个怀疑各中一半：算法疑点集中在 2 件，考法疑点全员命中。

## 1. 结论总表

| ID | 指标 | 考分\|ic_5d\| | 三选一结论 | 一句话判据 |
|----|------|--------------|-----------|-----------|
| MOM-032 | 加速振荡器 AC | 0.0009 | **考法错** | 实现与 Bill Williams 官方口径逐式等价；AC 是择时零件（零轴+双色 bar 确认），本就不是横截面因子 |
| MOM-036 | Squeeze | 0.0004 | **实现有错** | KC 中轨 EMA≠参考 SMA、KC 通道 H−L≠TR、动量基座缺 Donchian 分量——三处偏离声明参考 LazyBear |
| REV-003 | MACD背离 | 0.0036 | **考法错** | PIT 安全峰谷背离是社区主流合法变体（TA-Lib 根本无背离函数）；0/±1 稀疏事件在 rank IC 下结构性趋零 |
| VOL-016 | 盘整指数 CHOP | 0.0029 | **考法错（维持退役）** | 公式与 pandas_ta 逐项等价；角色=体制状态零件（61.8/38.2 阈值），退役注记"与体制帘子重复"成立 |
| VOLUME-015 | Williams A/D | 0.0039 | **实现有错** | 我方 C−L_prev/C−H_prev ≠ Tulip 实码 C−min(昨收，今低)/C−max(昨收，今高)（=MetaStock TRH/TRL 原版）；合成数据两口径路径分叉，相对偏差中位 65%、永不收敛 |
| TREND-036 | 三阶高通 HighPass3 | 0.0030 | **实现等价（维持退役）** | 与 financial-hacker C 源码（TASC 8/24 Ehlers）逐系数一致；"三阶"系命名误读（HighPass3 名字来自 Zorro 已有三个高通，实为二极 IIR）；Ehlers 定位=PTREND 组件 |

考分证据锚点：`docs/_working/fexam/indicator_exam_scores_v1.yaml`（条目行号 L2598/L2862/L5851/L7738/L8657/L8980；prereg L1-49：干净窗 2025-10-09~2026-09-30，headline horizon=5d，及格线 |ic_5d|≥0.02，CPU pandas spearman 秩相关，n_obs=236 横截面日）。

## 2. 系统性发现：考场错尺（回答"横截面 5 日 rank IC 是否本就是错尺"）

**是——对其中 5 件（除修正后的 squeeze_mom 外全员）是错尺。** 机制分三类：

1. **稀疏事件信号（REV-003）**：输出 0/±1，绝大多数交易日全横截面为 0。spearman 秩相关在近常数向量上退化为并列秩噪声，|IC| 趋零是**结构性**的，与指标好坏无关。正确考法=事件研究：信号确认点后 N 日前瞻收益 vs 同期基准（含 hit rate、按体制分组），或转连续特征（距最近信号日衰减核）后再进 IC 考场。
2. **状态/体制零件（MOM-036 squeeze_on、VOL-016 CHOP）**：二元状态或有界体制读数（CHOP∈[0,100]，惯例 61.8/38.2 阈值）。正确考法=条件考试：状态 A vs 状态 B 分组下既有趋势/动量因子的 IC 条件化或波动率扩张命中率（squeeze 释放事件），而非状态值自身的横截面 IC。
3. **择时/零件与累积水平线（MOM-032 AC、TREND-036 HighPass3、VOLUME-015 WAD）**：AC 官方用法是零轴穿越+连续同色 bar 确认的**择时信号**（MQL5/TradingView 官方文档口径）；HighPass3 在 Ehlers 设计里是 PTREND=HP(250)−HP(40) 的**组件**（组件已在册 PTREND active 条目内受考核）；WAD 是**非平稳累积线**，每标的起点/量纲不同，横截面 rank IC 对水平值没有可解释含义。WAD 正确考法=斜率（N 日差分）或 WAD-价格背离事件——注册表退役注记"斜率/背离版可另立新条目重考"与本调查结论一致。

**处方（供 fexam v2 立项建议，本车道不落任何修改）**：指标考场按 `entry_role` 路由——`factor`（连续平稳值）→ rank IC；`trigger`（事件）→ 事件研究；`state`（状态/体制）→ 条件考试；`component`（零件）→ 并入其宿主复合指标考场。本轮 6 件的 `entry_role` 在册全为 `state`，却全部用因子尺（rank IC）考试——考试设计与注册表角色声明错位，是"经典指标全军覆没"的第一解释变量。

## 3. 逐指标档案

### 3.1 IND-MOM-032 加速振荡器 AC —— 考法错（实现等价）

- **我方实现**：`src/zephyr/factor/technical_indicators/momentum.py:1045-1054`（class AC L1031）。`mid=(H+L)/2`；`ao=SMA5(mid)−SMA34(mid)`；`ac=ao−SMA5(ao)`。
- **参考实现**：Bill Williams 官方口径（TradingView 内置 Accelerator Oscillator 文档：AC=AO−SMA(AO,5)，AO=SMA(HL2,5)−SMA(HL2,34)，https://www.tradingview.com/support/solutions/43000474441-accelerator-oscillator/ ；MQL5 iAC 文档同口径 https://www.mql5.com/en/docs/indicators/iac ）。**TA-Lib 0.7.1（本机 get_functions() 实测 161 函数）、tulip-indicators（本地 tiamalgamation.c 全清单）、pandas_ta 均不收录 AC**——该指标无三大库权威实现可对数，官方口径即上列公式。
- **技术判定**：逐项等价（中价、5/34、AO 差分再 SMA5，全部一致）。warmup 38=5+34−1 合理。
- **三选一结论**：**考法错**。AC 的官方用法是择时（零轴上方连续两根变色 bar→做多触发等），是单标的时序零件；其值绕零高频翻转，横截面排序无设计含义。|ic_5d|=0.0009 是"用尺子量温度"。
- **处方**：维持因子退役；若复活走**策略层触发件考场**（事件研究+择时 Sharpe 贡献），不改实现。

### 3.2 IND-MOM-036 Squeeze —— 实现有错（3 处偏离声明参考 LazyBear）

- **我方实现**：`src/zephyr/factor/technical_indicators/momentum.py:1165-1194`（class SQUEEZE L1151）。三处关键行：
  - L1175 `tr = data["high"] - data["low"]` ——KC 通道用**普通振幅**；
  - L1176 `kc_mid = close.ewm(span=n, adjust=False).mean()` ——KC 中轨用 **EMA**；
  - L1180-1193 动量=`linreg(close,20,外推末bar) − kc_mid` ——回归基座只有 close 自身。
- **参考实现**：LazyBear《Squeeze Momentum Indicator [LazyBear]》Pine 原文（2014，镜像 https://github.com/czarcrab/tv-indicators-strategies/blob/master/squeeze%20momentum%20histogram.tv ，作者头 `@author LazyBear`；官方发布页 https://www.tradingview.com/scripts/squeezemomentumind/ ）：
  ```pine
  ma = sma(source, lengthKC)                        // KC 中轨 = SMA(20)
  range = useTrueRange ? tr : (high - low)          // 默认 useTrueRange=true → 真实波幅
  rangema = sma(range, lengthKC)
  sqzOn = (lowerBB > lowerKC) and (upperBB < upperKC)
  x = source - avg(avg(highest(high,lengthKC), lowest(low,lengthKC)), sma(close,lengthKC))
  val = linreg(x, lengthKC, 0)                      // 动量 = close 对"唐奇安中点与 SMA 混合基座"的 linreg
  ```
  pandas_ta 0.4.71b0 `pandas_ta/momentum/squeeze.py`（PyPI 官方 wheel 源码核对：L96-100 BB/KC 用 sma+`tr=True` 默认；L106-111 lazybear 分支 `linreg(close − avg_, kc_length)`、`avg_=0.5*(0.5*(highest+lowest)+kc_basis)`）与 LazyBear 同口径。
- **技术判定**：**三处实质偏离**。① KC 中轨 EMA20 vs SMA20——EMA 贴价更紧，squeeze_on 判定带整体移位；② 通道 H−L vs TR——TR=max(H−L,|H−Cp|,|L−Cp|)≥H−L，我方 KC 系统性偏窄（跳空日差更大），squeeze_on 触发率被压低；③ squeeze_mom 缺 Donchian 中点分量且基座口径不同（`linreg(close−avg_)`≠`linreg(close)−avg`，因 avg 随窗变化）。另注：LazyBear 原版 BB 倍率有一处知名 bug（`dev = multKC * stdev` 即 1.5 而非 2.0），我方按注册表声明 BB(20,2) 用 2.0 是对原版 bug 的修正、与 pandas_ta/TTM 规格一致——这一处我方更合理，但也就与 TV 原版不逐 bit 相同。squeeze_on 判定式本身（BB 完全嵌入 KC）与我方 L1179 一致。
- **三选一结论**：**实现有错**。相对其注册表声明与别名（"LazyBear 口径"）不成立。
- **处方**：修复三处——L1175 改用真实波幅（可复用 volatility.py `_true_range`）、L1176 改 `close.rolling(n).mean()`、动量改 `linreg(close − avg((HH20+LL20)/2, SMA20(close)), 20, 0)`；或保留现实现但在注册表 formula 字段明示变体名（EMA-KC/H-L-range/linreg-close）并摘除 "LazyBear 口径" 声明。修复后 **squeeze_mom 可重考因子 IC**（连续值，考法合法）；squeeze_on 仍按状态零件走事件/条件考试。修复与重考须另立施工单（本车道零代码修改）。

### 3.3 IND-REV-003 MACD背离 —— 考法错（实现为合法变体）

- **我方实现**：`src/zephyr/factor/technical_indicators/reversal.py:146-174`（class MACDDivergence L146）；峰谷核心 `_divergence_signal` L80-113、`_local_extrema` L59-77；HIST 计算 L169-171 `hist=2*(dif−dea)`。信号标在极值确认点（极值+peak_order=3，居中窗但确认点因果，PIT 安全 L93-94 注释）。
- **参考实现**：TA-Lib 0.7.1（本机数值验证 `hist≡macd−signal`，max|差|=0.0；函数全集 162 个仅 MACD/MACDEXT/MACDFIX，**无任何背离检测函数**，https://github.com/TA-Lib/ta-lib ）；pandas_ta 无内置背离；社区主流（TradingView Divergence Indicator、各开源背离脚本）均为"价格极值 vs 指标同点位值"的枢轴比较法——与我方同型。
- **技术判定**：等价合法变体。HIST 的 ×2 是通达信口径（TA-Lib 无 ×2），对背离判定无影响（×2 为正标度变换，不改变峰谷序关系）；lookback=20 限相邻极值跨度、居中窗+确认点平移保证无前视——比多数社区实现（常用未来函数）更严格。
- **三选一结论**：**考法错**。0/±1 稀疏事件列在 236 个横截面日的 spearman 秩相关下结构性趋零；rank IC 度量不了"背离信号后 5 日反转命中率"这类事件语义。
- **处方**：维持因子退役；复活走**事件研究考场**（信号确认点后 1/5/20 日前瞻收益 vs 基准，按体制分组 hit rate），或以衰减核转连续特征重考 IC。不改实现。

### 3.4 IND-VOL-016 盘整指数 CHOP —— 考法错（实现等价，维持退役）

- **我方实现**：`src/zephyr/factor/technical_indicators/volatility.py:493-522`（class CHOP L494）；TR 复用 `_true_range` L52-60（=max(H−L,|H−Cp|,|L−Cp|)，首根 H−L，与 TA-Lib TRANGE 口径同）。
- **参考实现**：pandas_ta 0.4.71b0 `pandas_ta/trend/chop.py` L69-78（PyPI wheel 源码核对）：`100×(log10(ΣTR_N)−log10(HH_N−LL_N))/log10(N)`，其中 `atr_length=1` 默认即朴素真实波幅——与我方逐项等价。Dreiss 官方口径同（TradingView/motivewave 文档）。TA-Lib、tulip 均无 chop（tulip master 全清单核对无此函数）。
- **技术判定**：**逐项等价**（含 0/0 保护：我方分母≤0→NaN，pandas_ta 未保护——我方更稳健）。
- **三选一结论**：**考法错（维持退役）**。CHOP 是体制状态读数（>61.8 盘整/<38.2 趋势），注册表退役注记"与体制帘子功能重复"成立——体制判别已有专职帘子，CHOP 作为横截面因子无设计意图。
- **处方**：维持退役；如未来体制帘子重构需要连续体制读数，以**条件考试**（高/低 CHOP 分组下趋势因子 IC 条件化）复核，不改实现。

### 3.5 IND-VOLUME-015 Williams A/D —— 实现有错（误读 Tulip 口径）

- **我方实现**：`src/zephyr/factor/technical_indicators/volume.py:484-517`（class WAD L484），关键 L511-515：`tad = C>Lp ? C−L.shift(1) : (C<Lp ? C−H.shift(1) : 0)`，即 **C−昨低/C−昨高**；docstring（L487-501）自称"Tulip 权威口径"。首行 TAD=0。
- **参考实现**：Tulip Indicators 0.9.2 官方源码 `tiamalgamation.c` L4162-4189（https://github.com/TulipCharts/tulipindicators/blob/master/tiamalgamation.c ）：
  ```c
  if (c > yc) { sum += c - MIN(yc, low[i]);  }   // C − min(昨收, 今低) = C − TRL
  else if (c < yc) { sum += c - MAX(yc, high[i]); } // C − max(昨收, 今高) = C − TRH
  ```
  即 **C−min(昨收，今低)/C−max(昨收，今高)**——与 Williams 原版 MetaStock TRH/TRL 口径一致（TRH=max(昨收，今高)，TRL=min(昨收，今低)；True Range High/Low 定义见 IncredibleCharts/TC2000 帮助：https://www.incrediblecharts.com/indicators/williams_accumulation_distribution.php ）。官方用法=与价格做背离（社区文档一致）。
- **技术判定**：**实现有错，且是 docstring 声明与实码的双重错误**——把 tulip 的 `MIN(yc, low[i])` 误读为"昨低"（`yc` 是昨收、`low[i]` 是今低；正确语义=min(昨收， 今低)）。量级实测（可复现生成器：n=500 合成 bar，np.random.seed(42)，close=100·exp(cumsum(randn)×0.01)，high/low=close×(1±|randn|×0.5%)；2026-10-08 复跑）：两口径 WAD 水平序列相关 **0.98**、相对偏差中位 **65%**（路径依赖尾部可达数千个百分点）——cumsum 路径从此分叉且永不收敛；方向增量符号零分歧（0/499），错在幅度不在方向。前稿曾记 corr=0.775（生成器未随档、不可复现），本轮已替换为上列可随档复现口径。
- **三选一结论**：**实现有错**。考试所用特征本身不是 Williams A/D。
- **处方**：修复两行——L513 改 `c - np.minimum(l.shift(1), l)`、L514 改 `c - np.maximum(h.shift(1), h)`（即 min/max 两个候选里取"昨收"与"今低/今高"较小/较大者）；同步修 docstring。但注意：**即使修复，累积水平值在横截面 rank IC 下仍是错尺**（非平稳、逐标的不同量纲）——复活路径=修复后以 **WAD 斜率（N 日差分）或 WAD-价格背离事件**另立新条目重考（注册表退役注记已预留此路径）。修复须另立施工单。

### 3.6 IND-TREND-036 三阶高通 HighPass3 —— 实现等价（维持退役；命名/出处勘误两条）

- **我方实现**：`src/zephyr/factor/technical_indicators/trend.py:1665-1683`（`_highpass3`，HIGHPASS/PTREND 共用）。
- **参考实现**：financial-hacker（Zorro 作者）对 TASC 8/24 John Ehlers《Precision Trend Analysis》的官方复刻 C 源码（https://financial-hacker.com/ehlers-precision-trend-analysis ，逐行引用核对）：
  ```c
  var f = 1.414*PI/Length;  var a1 = exp(-f);
  var c2 = 2*a1*cos(f/2);   var c3 = -a1*a1;   var c1 = (1+c2-c3)/4;
  return HP[0] = c1*(Data[0] - 2*Data[1] + Data[2]) + c2*HP[1] + c3*HP[2];  // series(0,4) 零种子
  ```
- **技术判定**：**逐系数、逐递推、逐种子完全一致**（f=1.414π/N、a1=exp(−f)、c2=2a1·cos(f/2)、c3=−a1²、c1=(1+c2−c3)/4、二阶差分输入+双反馈 tap、hp[0]=hp[1]=0）。两条勘误：① **"三阶"系命名误读**——financial-hacker 原文明示 "HighPass3 因 Zorro 已有三个高通滤波器得名"，该滤波器实为**二极（2-pole）IIR 高通**（递推仅 2 个反馈 tap）；注册表 formula 字段与中文名"三阶高通滤波"应理解为序号非阶数（本车道不改注册表，留勘误记录）。② 出处月份：原文标注 TASC **8/24**（2024-08），注册表写 "TASC 2024-09"，差一期（以原文为准，留痕不改）。
- **三选一结论**：**实现等价（维持退役）**。Ehlers 设计意图中它是 PTREND=HP(250)−HP(40) 的**组件**，单件本就无独立因子语义；其宿主 PTREND（IND-TREND-037）在册 active，组件语义已由宿主考场覆盖。
- **处方**：维持退役（零件身份保留，与裁定#489 注记一致）；注册表 formula"三阶"措辞与 TASC 月份建议下一张注册表维护单顺带勘误（非紧急、零代码）。

## 4. 处方汇总

| 类别 | 件 | 动作 | 载体 |
|------|----|------|------|
| 修复件 | MOM-036 SQUEEZE | 三处实现修复（或明示变体改名），修复后 squeeze_mom 重考因子 IC | 另立施工单 |
| 修复件 | VOLUME-015 WAD | 两行口径修复+docstring 修正，修复后以斜率/背离版新条目重考 | 另立施工单 |
| 重考件 | REV-003 MACD背离 | 事件研究考场（不改实现） | fexam v2 立项建议 |
| 重考件 | MOM-032 AC | 择时触发件考场（不改实现） | fexam v2 立项建议 |
| 维持件 | VOL-016 CHOP | 维持退役（实现等价、与体制帘子重复） | 无 |
| 维持件 | TREND-036 HighPass3 | 维持退役（组件身份在 PTREND 考场覆盖）+注册表勘误两条 | 注册表维护单（低优） |
| 体系建议 | fexam v2 | 指标考场按 entry_role 路由：factor→rank IC / trigger→事件研究 / state→条件考试 / component→宿主考场 | 立项建议 |

## 5. 证据与来源清单

- 我方实现：momentum.py:1045-1054（AC）、momentum.py:1165-1194（SQUEEZE）、reversal.py:59-113+146-174（MACD背离）、volatility.py:52-60+493-522（CHOP）、volume.py:484-517（WAD）、trend.py:1665-1683（HighPass3）。
- 注册表条目：`docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml` L1169/L1301/L2769/L3440/L3904/L4072。
- 考分：`docs/_working/fexam/indicator_exam_scores_v1.yaml` L2598/L2862/L5851/L7738/L8657/L8980 + prereg L1-49。
- 外部参考（联网核对，2026-10-08）：
  - LazyBear Squeeze Pine 原文镜像：https://github.com/czarcrab/tv-indicators-strategies/blob/master/squeeze%20momentum%20histogram.tv （官方页 https://www.tradingview.com/scripts/squeezemomentumind/ ）
  - pandas_ta 0.4.71b0（PyPI 官方 wheel 源码）：momentum/squeeze.py、trend/chop.py
  - Tulip Indicators 官方源码：https://github.com/TulipCharts/tulipindicators/blob/master/tiamalgamation.c （ti_wad L4162-4189；全清单无 chop/AC）
  - Ehlers HighPass3 官方复刻 C 源码：https://financial-hacker.com/ehlers-precision-trend-analysis （TASC 8/24 "Precision Trend Analysis"）
  - Williams A/D TRH/TRL 官方口径：https://www.incrediblecharts.com/indicators/williams_accumulation_distribution.php （同口径：TC2000 help、cTrader help）
  - AC 官方口径：https://www.tradingview.com/support/solutions/43000474441-accelerator-oscillator/ 、https://www.mql5.com/en/docs/indicators/iac
  - TA-Lib：本机 0.7.1 全函数枚举（get_functions()=161，无 AC/CHOP/SQUEEZE/背离；MACD hist≡macd−signal 数值验证 max|差|=0.0）+ https://github.com/TA-Lib/ta-lib
  - Tulip Indicators 本地副本：.runtime/tmp/tiamalgamation.c（ti_wad 函数体 L4166-4188 逐行核对）；pandas_ta 0.4.71b0 wheel 本地副本：.runtime/tmp/pta_pkg/extracted/pandas_ta/（squeeze.py L90-102、chop.py L61-74）

## 6. 边界与自裁记录

- 本车道零代码修改、零数据库写、零 technical_indicator_registry 修改；仅新建本文件+按门禁通道登记本文件 creation_token（capability_canonical_file_registry.yaml 追加一条）。
- 自裁 1：batch_creation_tokens 按目录前缀扫描会扫入他会话 3 个未登记文件，改用**精确文件路径前缀**只登记本车道文件（避免代领会话成果留痕）。
- 自裁 2：WAD 量级差异以合成随机游走（生成器已随档写明于 §3.5：seed=42, n=500，2026-10-08 三发复跑 corr=0.98、相对偏差中位 65%、符号分歧 0/499），非生产数据——证明力为"存在系统性口径差"，非考窗内真实 IC 影响测算（后者需重考才有答案）；前稿 0.775 系未随档生成器产物，不可复现，已替换。
- 自裁 3：任务卡文件头 [TTL] permanent 与 temporary zone ttl_gate 契约冲突，按门禁机械判定登记 frontmatter ttl=task_bound（正文永久锚自欺模式系 ttl_gate 2026-06-29 治本案例明令禁止），promote 时升级 permanent。
- 遗留：SQUEEZE/WAD 修复施工单、fexam v2 entry_role 路由立项、TREND-036 注册表勘误三条移交总包。
- 三发复核（2026-10-08，st-mx07-L1 第三次派发）：全文 6 节实现行号/注册表 formula/考分锚点（L2598/2862/5851/7738/8657/8980 六处 |ic_5d| 逐一对上）全部复验吻合；本地参考源三件复验在位（TA-Lib 0.7.1、tulip tiamalgamation.c、pandas_ta 0.4.71b0 wheel）；修正两处精度问题（TA-Lib 函数数 162→161、WAD 量级实测换可复现口径），结论三选一判定全部不变。
