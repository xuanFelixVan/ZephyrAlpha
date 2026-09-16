---
ttl: task_bound
title: T1-β 节点挖矿：S11 整装回测 runner 本体（回测引擎执行/估值/成本/产出内核）
session: st-qoder-t1b-h-20260916
date: 2026-09-16
parent: S11_assembled_backtest
lane: H
---

# 节点挖矿：S11 整装回测 runner 本体（父环节 S11_assembled_backtest）

> 边界声明：本节点挖 **runner 本体**——即合成层（`compose_weight_panels`/
> `verify_weight_panel_identity`/死成员 rescale）以外的全部内核：数据装载、日频事件循环、
> 撮合执行价、估值口径、成本应用、指标产出、产物落盘、自动触发验收。合成层与决策内核
> 算法（死成员 44.1% rescale、激活无效、regime 无迟滞）已由 `decision_kernel_mining.md`
> （st-qoder-t1a-20260915）覆盖，本文**不重复**，仅在与执行/成本/估值口径耦合处引用。
> 产出=数据，采纳裁定归主力会话施工班。**结论全部实证**：代码给 file:line，数字给真跑
> （CH 只读 + `data/backtest_artifacts/bt-fw-823d7fd7.json` 现网产物 + 探针
> `.runtime/tmp/h_probe_*.py`）。

## 1 现状盘点（逐条带 file:line 锚点 + 现网实证）

### 1.1 生产调用链（"production-identical config actually runs" 核验 = 是，且静默降级面广）

现网证据包 `data/backtest_artifacts/fw-auto/latest.json`（run `bt-fw-823d7fd7`，窗口
2025-09-16..2026-09-15，plan `fw-tdm-current`，fingerprint `fe90e5725901`）：

- 链路：`fw_backtest.py:245 run_framework_backtest()` →
  `framework_composer.py:1444 _build_member_panels()`（成员面板+行情 data）→
  `framework_composer.py:1403 compose_weight_panels()` → `:1408
  verify_weight_panel_identity()`（面板逐位 1e-9）→ `:1412-1415 DefaultBacktestEngine
  (config=BacktestConfig(initial_capital=...))` → `:1416 engine.run(data, signals)` →
  `:1418 _persist_framework_artifact()`。
- **引擎参数只有 initial_capital 被注入**（framework_composer.py:1413）：
  commission/slippage/impact/participation/execution_lag/PIT/sanity/strict_gate/
  benchmark **全部走 `BacktestConfig` 硬编码默认**（vectorized_engine.py:107-127）。
  `FrameworkBacktestConfig`（framework_composer.py:1412-1441）**根本没有成本/滞后/门禁
  字段**，故"生产可配置"= 假：任何成本与流动性口径都改不动，只能改源码。
- 现网实跑数字：total_return **-18.47%**、annual_return -19.08%、sharpe **-2.12**、
  max_dd 19.84%、win_rate（日频正收益占比，非逐笔，见 1.5）0.4298、trades **14,311**、
  **overfitting_flag=True**（见 §H5）、rescale_factor 1.2539、equity 1,000,000→815,347、
  duration 1989.7s（33 分钟）。acceptance.ok=**true**（`ok∧within_tolerance∧
  equity_points>0`，fw_backtest.py:249-255）——**overfitting=True 仍判过**。

### 1.2 行情装载：raw 未复权 close/open，adj_factor 恒=1 → 前复权/除权口径全线失真

- 装载 SQL `factor/core/evaluation/backtest.py:74`：`SELECT trade_date, symbol, open,
  high, low, close, volume, amount, adj_factor FROM c1_market.kline_daily`（**未复权原始价**）。
- 引擎估值/执行价取 `close`/`open` 原值：`vectorized_engine.py:253-255
  exec_prices`（开盘优先）、`:315 update_market_value(date, day_prices)`（收盘估值），
  二者皆 raw，**不乘 adj_factor**。
- `adj_factor` 仅在因子 IC 评估 `_adjusted_close_panel`（backtest.py:209+，"close×adj_factor"，
  tracker #197）被用，回测引擎根本不碰。
- **实证（CH 只读，探针 h_probe_af3.py）**：窗口内 `c1_market.kline_daily` 共 **1,329,245
  行，adj_factor 全部=1.0（NULL=0、≠1=0、distinct=1）**。→ #197 "×adj_factor" 修正**恒为
  ×1（惰性）**，除权缺口无人纠正，因子 IC 与 NAV 同时暴露除权。
- **实证（h_probe_af2.py）**：600036 同窗口 raw 收盘均值 ~41、hfq 表 ~185 → **raw 确为
  不复权交易价**。
- **除权幻影量化（h_probe_exrights2.py）**：619 只现网成交标的、148,673 对齐日对中，
  raw 跌>2% 而 hfq 口径≈平（纯除权被记成亏损）**63 次，平均 -7.66%**；全篮 raw-vs-hfq
  端点收益差 **1.90pp**（一年股息+送转未捕获），占该 run 亏损绝对值 ~10%。

### 1.3 成交量单位：volume 列实为「手」（100 股），撮合按「股」读 → 流动性参与率上限被夹到 0.1%

- **单位实证（h_probe_volume.py / h_probe_cap.py）**：`amount/(close×volume)` 中位数
  **99.8**（p10 98.4 / p90 100.8，n=1052）→ volume 单位=手，amount=元。
- 全仓无 手→股 换算（grep `volume*100` 于 backtest 核心=空命中）。
- 参与率上限 `matching_engine.py:655 cap_qty = vol * cap_rate`，`vol` 即手、`order["quantity"]`
  为股 → 实际上限 = 0.10×volume_手 股 = 0.10×(真实股量/100) = **0.1% 真实日量**（100× 过严）。
- 冲击 `matching_engine.py:711 model.quote(order_qty_股, vol_手)` → 参与率=股/手=100×真实，
  `_validate_participation`（almgren_chriss_impact_model.py:184-185）p>1 抛错 → 被
  `matching_engine.py:712-714` 捕获"该标的按无冲击成交"**静默旁路**（真实参与率>1% 时冲击直接归零）。
- **现网成交反证（h_probe_cap.py）**：引擎所见 p 中位 0.0013、p99 0.028、max **0.0997**；
  **真实 p=qty/(vol×100) max 恰=0.00100** —— 0.1% 上限的钳位签名（无一笔越过 0.1% 真量）。

### 1.4 成交/费用：费率编码正确，但 5 元最低佣金在微额仓位上支配实际成本

- 大额成交（notional>6 万）边际费率实证（h_probe_costs2.py）：买 **9.54e-5**（=万0.854+万0.1
  过户）、卖 **5.954e-4**（+万5 印花税）——`matching_logic.py:62-66` 常量与 #233/法定口径一致，**编码无误**。
- **但现网 98.9% 买单（7078/7158）低于最低佣金阈值**：单笔中位名义 **¥2280**（1M 资金 ×
  行归一满仓 × 3290 标的 → 碎股），`MIN_COMMISSION=5`（matching_logic.py:66，"不免五"Owner
  2026-08-22）**1382 笔顶到 5 元地板**。
- 实际佣金率中位 **万21.5**、p90 万72.6、max 万350 = 名义万0.854 的 **25–410×**。
- **全 run 佣金合计 ¥95,529 = 总 NAV 亏损 ¥184,653 的 51.7%**（h_probe_costs.py）。

### 1.5 指标产出：口径错位与违约

- win_rate 语义=日度正收益占比，非逐笔胜率（vectorized_engine.py:346 注释 P1-3；产物字段名
  仍叫 win_rate → 下游易误读）。
- `calculate_full_metrics` 调用**未传 n_trials**（vectorized_engine.py:328-332）→ 走
  `DEFAULT_N_TRIALS=10`（metrics.py:239），violates metrics 契约"调用方 MUST 传入实际试错次数"
  （归 §H5 门禁线）。
- benchmark 恒缺：产物 `benchmark_curve=None`，metrics.benchmark_symbol="000300" 但无曲线 →
  无超额/IR。
- 产物无 cash/positions/turnover 序列（bt-fw-823d7fd7.json 顶层仅 run_id/strategy_id/
  benchmark_curve/created_at/drawdown_curve/equity_curve/metrics/schema_version/
  tick_replay_data/trade_log）→ 现金-净值事后不可对账（归 §H4）。

### 1.6 自动触发验收与幂等

- 验收判据（fw_backtest.py:249-255）= `ok ∧ panel_recon.within_tolerance ∧ equity_points>0`
  —— 纯"权重数学+有没有净值点"，**不含成本合理性/换手/现金/过拟合/冲击**。
- 幂等闸（fw_backtest.py:220-232）按 **plan 指纹**（非数据/窗口年龄）判重，同指纹上次 ok 即
  skip → 数据老化后证据不自刷新（`force=true` 才重跑）。
- regime 新鲜度闸（:218 ensure_regime_snapshot）仅告警不阻断（现网 stale_days=5，
  freshness_guard=stale_alert_only）。

## 2 六向挖矿日志表

| 方向 | 追到的矿点 | 锚点 | 实证 | 结论 |
|------|-----------|------|------|------|
| ①上游 | 引擎参数只透传 initial_capital | framework_composer.py:1412-1415；FrameworkBacktestConfig:1412-1441 | 配置类无成本/滞后字段 | 成本口径不可配置（P1） |
| ①上游 | 行情源=raw kline_daily | backtest.py:74 | adj_factor 恒=1（1,329,245 行） | 除权全线失真（P0） |
| ②下游 | 产物喂给谁 | fw_backtest.py:249-255 / api_server.py:1015 | 验收不查 overfitting/cash/turnover | 信号产而不消（→H5） |
| ②下游 | 估值用 raw close | vectorized_engine.py:253-255,315 | 篮收益 raw-vs-hfq 差 1.9pp | 幻影除权 63 次（P0/P1） |
| ③算法/机制 | 参与率钳位 | matching_engine.py:655 | 真实 p max=0.001=0.1% | 手/股单位错 100×（P0） |
| ③算法/机制 | 冲击报价 | matching_engine.py:711；impact:184 | 成交 slip 恒 ±1.000bp | 冲击实际为 0（P1→H2） |
| ④后端 | volume 单位 | grep 无 *100 | amount/(close·vol)=99.8 | 手为量纲基准（P0 根因） |
| ⑤前端 | 面板 data=首个非空成员 | framework_composer.py:1264-1265 | 全市场权重共用一份行情 | 行情覆盖脆耦合（P2） |
| ⑥数据字段 | adj_factor 列 | backtest.py:74；#197 :209 | 全窗口 distinct=1 | 修正件惰性（P1） |

## 3 业界与开源对照（四闸：来源可溯 / 交叉验证≥2 / A股适配 / 可回测+数据可得）

- **复权价回测**（qlib `get_adjust="hfq"`、backtrader `reversed`/`cfactor`、Zipline 复权因子）：
  业界一致用复权价做 NAV，除权事件不得进收益。四闸：来源可溯（qlib docs 2023/backtrader docs
  2022）✓≥2✓A股适配✓（本项目 adj_factor 列**在但恒=1**→数据不可得，触发"字段在≠数据可得"
  铁律反面）→ **须走 hfq 表或补真 adj_factor**。
- **成交量单位为手**（Tushare `vol` 单位=手、akshare 东财=手；QMT `volume` 手）：业界参与率
  公式一律 `order_shares / (volume_lots×100)`。四闸：来源✓≥2✓A股✓可得✓ → 本 runner 缺 ×100
  归一，属**量纲错**。
- **最低佣金地板建模**（IB/券商回测多以 notional×rate 无地板，A股"最低 5 元"是本地特有约束，
  qlib/国产聚宽均实现为 `max(5, notional×rate)`）：本项目已正确实现地板，但**未把"地板支配"
  作为容量结论披露** → A股适配✓但报告缺容量归因（P1）。

## 4 堵点与欠账清单（具体 文件/函数/验收标准）

| ID | 级别 | 病灶类 | 堵点（文件:行） | 下一施工验收标准（可施工） |
|----|------|--------|-----------------|--------------------------|
| H1-A | **P0** | 量纲错 | `matching_engine.py:655`/`:711` volume 读手当股；参与率钳到 0.1% | 加 `volume×100` 归一（或统一股口径）；新增单测：注入 qty=真实ADV 8% 的单，断言不被 0.1% 误砍、参与率报价 p∈[0,1] 不抛错；现网重跑 max 真实 p 应 >1% 不再钉 0.001 |
| H1-B | **P0** | 未校准/静默 | `backtest.py:74` raw 价 + adj_factor 恒=1，除权进 NAV | runner 改读复权价（hfq 表或真 adj_factor）；验收：600036 类高分红篮一年 raw-vs-hfq 端点差应<0.2%（现 1.90pp）；除权幻影计数（现 63）归 0 |
| H1-C | **P1** | 零消费者/配置 | `FrameworkBacktestConfig` 无成本/滞后/门禁字段（framework_composer.py:1412-1441） | 增补 cost/slippage/participation/execution_lag/strict_gate 透传至 BacktestConfig；验收：改 config 即改现网成交费率（单测锁） |
| H1-D | **P1** | 静默降级 | volume 缺失旁路记 INFO（vectorized_engine.py:246-249，注释却写 warn） | 提升为 WARNING + 计数进 metrics；涨跌停/PIT fail-open 计数披露进产物 |
| H1-E | **P1** | 指标违约 | n_trials 未传（vectorized_engine.py:328）→DSR 用默认 10 | 见 §H5（overfitting 门禁）统一处理；本节点最低验收：n_trials 从 plan 实际试错次数注入 |
| H1-F | **P2** | 脆耦合 | 全市场共用"首个非空成员 data"（framework_composer.py:1264） | 独立装载统一价格面板；验收：任一成员 data 缺列不改变其他成员成交 |
| H1-G | **P2** | 报告缺项 | benchmark_curve 恒 None | 装载 000300 基准，产出超额/IR（可得：index_daily） |

## 5 子节点清单

- H1.a 单位真源治理：volume 手/股、amount 元 的单一口径声明 + 撮合层断言（与 §H2 共挖）。
- H1.b 复权价改造：raw / hfq 表二选一，联动 #197/#209② adj_factor 混存遗留（与数据车道共挖）。
- H1.c FrameworkBacktestConfig→BacktestConfig 参数透传全表补齐。
- H1.d 产物 schema 扩展：cash/positions/turnover/benchmark/静默降级计数（与 §H4/H5 共挖）。
- H1.e 现网 run 归因复盘：-18.5% 中 51.7% 是佣金地板 + 1.9pp 除权 → "策略是否真亏 alpha"待重估。

## 6 封矿判定

**未封矿**。runner 本体已挖通并给出现网量化（单位错→0.1% 钳位、adj_factor 惰性→1.9pp 除权
失真、min-fee→51.7% 亏损占比、config 不可透传），但以下子脉待深挖：复权价改造的字段级可得性
（hfq 表覆盖度 vs raw 表差集）、FrameworkBacktestConfig 透传的施工面回归、产物 schema 扩展的
消费端联动。建议：H1-A/H1-B 两 P0 移交施工班优先；本轮记矿未竭（复权/单位子脉延伸至 H2/H4）。

## 修复优先级裁定建议

| 编号 | 一句话 | 级别 | 建议归属 |
|------|--------|------|----------|
| H1-A | 流动性参与率被手/股单位错夹到 0.1%（100×） | **P0** | 本仓 AI 施工班（撮合层单点，可测） |
| H1-B | 引擎用未复权价+adj_factor 恒=1，除权进 NAV | **P0** | 数据+回测联合 |
| H1-C | 成本/流动性/门禁全不可配置 | **P1** | 施工班 |
| H1-D | 静默降级以 INFO 记（注释说 warn） | **P1** | 施工班 |
| H1-E | n_trials 违约进 DSR | **P1** | 并 §H5 |
| H1-F/G | data 共用脆耦合 / benchmark 缺 | **P2** | 排期 |
