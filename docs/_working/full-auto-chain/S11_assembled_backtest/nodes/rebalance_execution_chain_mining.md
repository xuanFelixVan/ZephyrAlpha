---
ttl: task_bound
title: T1-β 节点挖矿：调仓与再平衡执行链（换手预算/执行时点/PIT一致性/未接线产出）
session: st-qoder-t1b-h-20260916
date: 2026-09-16
parent: S11_assembled_backtest
lane: H
---

# 节点挖矿：调仓与再平衡执行链（父环节 S11_assembled_backtest）

> 范围：从"目标权重面板"进引擎到"成交落地"的执行链——执行时点/lag、再平衡频率、换手预算、
> PIT 一致性、清仓语义、以及**产出未接线**（算了但没人收的调仓相关量）。死成员 rescale/激活无效
> 已由 `decision_kernel_mining.md` 覆盖，本文不重复，只挖**执行语义**。实证锚点见 §1，数字来自
> 现网 `bt-fw-823d7fd7.json` + 探针（h_probe_costs2/h_probe_cap）。

## 1 现状盘点（file:line + 现网实证）

### 1.1 执行时点：T 执行 T-1 信号、次日开盘成交（防前视 OK）

- `execution_lag_days=1`（vectorized_engine.py:114，P0-1 前视防护 2026-09-14 整改）；
  取信号 `vectorized_engine.py:259-263`（T 日读 `dates[i-lag]`）；执行价 `:253-255`
  开盘优先、缺 open 回退收盘。→ **单日无前视**，语义正确。

### 1.2 换手：无任何换手预算/上限，满仓再平衡致现网年化 ≈52×

- **全仓 grep `turnover_budget/max_turnover/turnover_cap` = 零命中** → 执行链**根本没有换手
  约束这一环**。`max_single=0.10`（framework_composer.py:1434）只是单标的上限，不控换手。
- 引擎每日把实际持仓拉回"行归一满仓"目标：`_normalize_day_signals` 强制 Σ=1（承 §H4），
  `generate_fills` 每日对差额下单 → **即使目标权重周内不变（kebab W-FRI ffill），组合漂移仍
  触发每日再平衡**。
- **现网实证（h_probe_costs2.py）**：14,311 笔 / 242 交易日，总成交名义/avg NAV = **99×**，
  **年化单边换手 ≈52×**。这是把组合按在收益上的最重执行病灶（成本占亏 51.7%，见 §H2）。

### 1.3 调仓节奏内部不一致：kebab 周频 vs STR 日频

- kebab 成员：`rebalance_freq="W-FRI"`（framework_composer.py:1432，fw_backtest.py:241-244
  用默认）→ `_select_rebalance_dates` 每周最后交易日给权、其余 ffill（strategy_runner.py:423-435）；
  再叠加 `pit_shift=1`（因子[t-1]）→ **信号最陈旧可达 6–7 个交易日**。
- STR-* 翻译件成员：`translated_strategy_adapter` INVARIANT"weights[t]=≤t 收盘信息"，**日频、
  不 shift**（adapter docstring:24-31）→ 引擎 lag 1 → **1 个交易日**。
- 合成把两种陈旧度**混进同一张日频面板逐日满仓再平衡**（compose 行归一），等于**用日频执行
  去追一份混频信号** → 无谓换手 + 周频腿的真实意图（周五调一次）被抹平。
- **验收缺口**：产物/证据包**不披露有效信号年龄（age in days per leg）**，混频不可见。

### 1.4 清仓语义：符号缺失→清仓卖单（红队 2026-08-19）；但全零行→不交易（矛盾）

- 单标的从 target_weights 消失（值 0）→ `generate_fills` 对其下清仓卖单（承 summary）。
- **但整行全零**（现金日意图，compose 注释 framework_composer.py:1179"全零行保留=现金日"）→
  `_get_day_signals` 只收 weight>0（vectorized_engine.py:462）→ 空 dict →
  `:286 if target_weights:` 为假 → **当日完全不交易=持仓漂移，绝不清仓到现金**。
  → "现金日"在执行链里**不可表达**（承 §H4 现金语义）。

### 1.5 PIT 一致性：universe 过滤 fail-open + 候选池幸存者偏差

- `enable_pit_universe_filter=True`、`exclude_st=True`、`min_listing_age_days=120`
  （vectorized_engine.py:120-122）：`_get_day_signals` 后按当日 PIT 池过滤（:265-284）。
  CH 不可达/registry 空 → **provider 返回 None=fail-open 不过滤**（:156,:271,:732+，warn 一次）。
- 但**候选标的池本身**来自 `fw_backtest.py:126-137 _hs300_symbols`——
  `valid_to IS NULL` **当前**成分快照回灌历史窗口（:119-123 rolling 12m）→ **幸存者偏差**：
  用"今天还在 HS300"的股票去回看一年，剔掉了期间被剔除/退市的（PIT 过滤只保证"当时可交易"，
  救不了"选股池按未来成员"）。
- 现网 symbols_total=3290（latest.json），STR-DABAN-023 贡献 3195 列（宽表腿）——池是"HS300
  当前成分 ∪ STR 列"，混合口径，幸存者风险面不清。

### 1.6 执行产出未接线（算了没被下游吃）

- `reconcile_composed_nav`（framework_composer.py:1261）：净值-现金对账，**src 内零调用方**
  （仅 def + `__all__`:1705 + docstring:44）→ 再平衡后的 NAV 一致性**从不校验**（详 §H4）。
- `verify_weight_panel_identity`（:1129）**只验权重数学**（1e-9），docstring 自陈"NAV 层残差
  不进容差"（:1141-1143）→ 执行链产出的成交/现金/换手层**无任何绊线**。
- `evaluate_decision_gate`（vectorized_engine.py:562）**零调用**（详 §H5）→ 决策门控不在执行链生效。
- 面板 data 只取"首个非空成员"（framework_composer.py:1264-1265）：执行用的价格/成交量随成员
  顺序而定，属**隐式契约**（换成员顺序→换行情覆盖→换成交，P2 脆耦合，见 §H1-F）。

## 2 六向挖矿日志表

| 方向 | 矿点 | 锚点 | 实证 | 结论 |
|------|------|------|------|------|
| ②下游 | 换手预算 | grep turnover_*=空 | 现网 52×/yr | 无换手约束（P0/P1） |
| ③机制 | 再平衡节奏 | W-FRI vs STR 日频；compose 混频 | 有效年龄 7d vs 1d | 混频不一致（P1） |
| ③机制 | 满仓每日拉回 | _normalize_day_signals；generate_fills | 99×名义/242d | 漂移触发每日churn（P1） |
| ③机制 | 清仓语义 | :462 vs :1179 | 全零行不交易 | 现金日不可表达（P1，承H4） |
| ⑥数据 | 候选池 PIT | fw_backtest.py:126-137 | valid_to IS NULL 当前快照 | 幸存者偏差（P1） |
| ④后端 | PIT 过滤可用性 | vectorized_engine.py:156,271 | CH 不可达 fail-open | 静默降级（P1） |
| ②下游 | 执行对账 | reconcile_composed_nav:1261 | 零调用 | 未接线（P1） |
| ③机制 | 执行时点 | :114,:253-263 | 单日前视=0 | 正确✓（记功不施工） |

## 3 业界与开源对照（四闸）

- **换手预算/调仓节流**：qlib `TopkDropoutStrategy`（每日只换 n 只，控换手）、Zipline 调仓
  间隔、机构再平衡多设 buffer/no-trade band。本项目无 → 52× 换手直接落地。四闸：来源✓≥2✓
  A股适配✓（涨跌停/整手已在撮合层）可得✓ → **须补 band/dropout 或再平衡触发条件**。
- **PIT 成分池**：合规回测须用"当日成分"（point-in-time index membership），业界严禁用当前
  快照回灌（幸存者偏差是回测头号坑，Talbot & Marcelo / 券商金工反复强调）。本项目 `_hs300_symbols`
  用当前快照（§1.5）→ 违反"数据可得+时点一致"闸。四闸：A股成分历史表**数据可得**
  （`market_index_constituent` 有 valid_to，见 registry）→ **须改按日 valid 过滤**。
- **满仓 vs 现金目标**：主流框架（Zipline `order_target_percent`、qlib）支持目标权重含现金
  （Σ<1 即持现金）。本项目执行链强制 Σ=1 且全零行=不动（§1.4）→ 与业界"可表达现金"契约相悖。

## 4 堵点与欠账清单（文件/函数/验收标准）

| ID | 级别 | 病灶类 | 堵点 | 可施工验收标准 |
|----|------|--------|------|----------------|
| H3-A | **P1** | 机制缺（零产出/零约束） | 无换手预算/再平衡节流；现网 52×/yr | 引入换手上限或 no-trade band（如 Σ|Δw|>band 才调）；验收：现网重跑年化换手降入配置区间（如<12×），成本占亏比例相应回落 |
| H3-B | **P1** | 未接线 | 混频信号（kebab W-FRI vs STR 日频）被当同频日频执行 | 按腿记录有效信号年龄并进产物；或按腿对齐调仓日历；验收：证据包披露每腿 lag，混频偏差可见 |
| H3-C | **P1** | 语义矛盾 | 全零"现金日"行在执行链=不交易（:462/:286） | 让 Σ=0 表达"清仓到现金"（区分"空信号"与"满仓意图=0"）；验收：构造全零行 → 断言持仓被清、进现金 |
| H3-D | **P1** | 幸存者偏差 | `fw_backtest.py:126-137` 当前成分回灌历史 | 候选池按 `index_constituent` 当日 valid 过滤；验收：窗口内被剔除/退市标的在其 in-index 期仍被纳入 |
| H3-E | **P1** | 静默降级 | PIT/ST 过滤 CH 不可达 fail-open（:156,271） | fail-open 计数与原因进产物并 WARNING（现仅 INFO/warn 一次）；验收：不可达运行的 metrics 带 `pit_degraded=true` |
| H3-F | **P1** | 零消费者 | `reconcile_composed_nav`（:1261）无人调 | 在 run 收尾调用并入 acceptance（详 §H4）；验收：NAV-现金对账误差>阈值即 acceptance=false |
| H3-G | **P2** | 脆耦合 | data=首个非空成员行情（:1264） | 独立统一价格/成交量面板；验收：成员顺序打乱不改变成交 |

## 5 子节点清单

- H3.a 换手预算/band 机制设计（与 §H2 资金规模缩放共挖）。
- H3.b 每腿执行时点与信号年龄归因披露（B3/混频）。
- H3.c PIT 成分池按日 valid 改造（数据车道联动）。
- H3.d 现金日清仓语义（与 §H4 共挖，同一 `_normalize_day_signals`/`_get_day_signals`）。
- H3.e 再平衡 NAV-现金对账接线（reconcile_composed_nav，§H4 主战场）。

## 6 封矿判定

**未封矿**。执行链挖出：换手无预算（52×现网实证）、混频信号当同频执行、现金日不可表达、
候选池幸存者偏差、PIT fail-open 静默降级、NAV-现金对账零消费者。执行时点（lag1+开盘）本身正确
（记功）。**待深挖**：换手治理的 band 阈值标定、成分历史表可得性（H3-D）、清仓语义的引擎改造面。
P1 群建议移交施工班；H3-A/H3-B/H3-C 与 §H2/§H4 强耦合，宜同批施工。

## 修复优先级裁定建议

| 编号 | 一句话 | 级别 | 建议归属 |
|------|--------|------|----------|
| H3-A | 无换手预算，现网年化 52× 把成本顶成亏损主因 | **P1** | 施工班（执行链节流） |
| H3-D | 当前成分回灌历史 → 幸存者偏差 | **P1** | 施工班+数据 |
| H3-C | 全零"现金日"被执行链吞成"不交易" | **P1** | 施工班（与 H4 同修） |
| H3-E | PIT/ST 过滤不可达 fail-open 静默 | **P1** | 施工班（可观测性） |
| H3-F | NAV-现金对账函数零消费者 | **P1** | 并 §H4 |
| H3-B | 混频信号被当同频日频执行 | **P1** | 排期（先披露后治理） |
| H3-G | 行情面板随成员顺序漂移 | **P2** | 排期 |
