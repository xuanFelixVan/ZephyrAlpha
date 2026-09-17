---
ttl: task_bound
title: T1-β 节点挖矿：现金与席位管理（闲置现金/席位与保证金占用/现金-净值一致性）
session: st-qoder-t1b-h-20260916
date: 2026-09-16
parent: S11_assembled_backtest
lane: H
---

# 节点挖矿：现金与席位管理（父环节 S11_assembled_backtest）

> 范围：回测账户里的**现金腿**——闲置现金来源与拖累、现金 vs 净值（NAV）是否可核、A股 T+1/资金
> 可用规则、以及"席位/保证金/融资融券"占用是否被建模。死成员把现金吞进 rescale、行归一吞现金
> 由 `decision_kernel_mining.md` 提出；本文从**账户内核**处实证并给出可核/不可核判据。实证锚点
> file:line + 现网产物 `bt-fw-823d7fd7.json`（顶层键与 equity/trade_log）+ 探针。

## 1 现状盘点（file:line + 现网实证）

### 1.1 账户内核：现金无利息、NAV=现金+市值、停牌错价防御 OK

- `Portfolio._cash = initial_capital`（portfolio.py:153），**全程无计息**（grep interest/ accrual=
  无）→ 闲置机会成本按 0 收益记（低估现金腿回报，但方向保守）。
- T+1 持仓规则正确：`_apply_sell` 拒当日买入卖出（`pos.buy_date == fill.date`，承 summary）；
  当日卖得现金先回账（portfolio.py:252 `self._cash += fill.total_cost`）再供买入 → **A股"资金
  T+0 可用不可取"语义正确**（记功）。
- 估值防停牌幻视：`_resolve_price`（portfolio.py 停牌/缺价沿用 last-known-price，:335 红队注释）
  避免 -100%/复牌幻视恢复污染 NAV ✓。
- `total_nav = cash + market_value`（portfolio.py:344）。

### 1.2 闲置现金只能由"摩擦"被动产生，且不可表达为决策

- 现金的三个来源，**全部是摩擦残差不是意图**：
  1. 参与率/成交量钳位丢弃的买单量（§H1-A `cap_qty`；`_clamp_buys_to_projected_cash`
     matching_engine.py:582-634 把买量压到投影现金内）；
  2. skipped fills（现金缺口/T+1/持仓不足，vectorized_engine.py:301-312，`skipped_fills++`）；
  3. **不可成交腿**（translated_strategy_adapter docstring:37：hfq 宇宙里的代码（如 000300）
     不在 raw `kline_daily` → 该腿 fill 无法成交 → 资金留现金）。
- **主动持现金不可达**：
  - 全零行 = 不交易（`_get_day_signals` 只收 >0，vectorized_engine.py:462 → `if target_weights:`
    :286 假），即"想空仓"做不到（§H3-C）；
  - 翻译件成员"行合计≤1，余量=现金"（adapter docstring:26,37）被 compose 行归一至 1
    （decision_kernel）+ 引擎 `_normalize_day_signals` 强制 Σ=1 双吞 → **成员的现金缓冲被抹平、
    被顶成满仓** → 放大换手（§H3-A）。
- → 现金既不能主动持有、又不能主动清零（全零行只冻结不卖），账户的现金腿处于**不可表达**态。

### 1.3 现金-净值一致性：**当前不可事后核**（产物无现金序列 + 对账函数零消费者）

- 产物顶层键（bt-fw-823d7fd7.json）= `run_id/strategy_id/benchmark_curve/created_at/
  drawdown_curve/equity_curve/metrics/schema_version/tick_replay_data/trade_log` ——
  **无 cash 序列、无 positions 序列、无 turnover**。
- 根因：`_collect_timeseries`（framework_composer.py:1645-1665）**只收 equity/trade_log/
  drawdown**，benchmark 引擎层无通道留 None；`Portfolio.cash` 属性存在（portfolio.py:288）但
  **不被收集** → 唯一能从外部核"现金+市值=净值"的证据不存在。
- `reconcile_composed_nav`（framework_composer.py:1261）本做"组合净值 vs Σα_i·nav_i"对账，
  **src 内零调用方**（grep：仅 def + `__all__`:1705 + docstring:44）→ 唯一内建的对账**从不运行**。
- skipped_fills 计数（vectorized_engine.py:302）只在日志 WARNING，**不进 metrics/产物** →
  现金缺口被拒的成交量、从而被留下的现金，在证据包里不可见。
- **实证**：equity 1,000,000→815,347（-18.5%）无法拆成"市值 vs 现金"两腿复核；trade_log 名义
  合计（买 45,289,779 + 卖 44,739,308）与 NAV 变动之间的现金残差**无法闭合验证**（这正是
  reconcile_composed_nav 该做而被跳过的活）。

### 1.4 席位/保证金/两融占用：**完全未建模**（对现货多头长仓是设计选择，但须披露）

- 全 portfolio/backtest 无 `席位/seat/margin/信用/融资/融券/冻结` 概念（grep 命中仅"可用{cash}"
  字样，无席位/保证金）。
- 含义：引擎是**单账户、现货、纯多头、无杠杆、无保证金占用**模型。
  - 对当前长仓策略自洽；
  - 但**无法回测**任何依赖两融/多席位/融券占用/保证金率的策略 → 属**能力缺口的静默**：
    blueprint 若宣称覆盖信用交易，生产内核不兑现（零生产者→需在能力声明处划界，非施工 bug）。

## 2 六向挖矿日志表

| 方向 | 矿点 | 锚点 | 实证 | 结论 |
|------|------|------|------|------|
| ③机制 | 现金利息 | portfolio.py:153 | 无 accrual | 保守低估（P2） |
| ③机制 | 主动持现金 | adapter:26,37 vs compose/engine 归一 | 余量被吞 | 不可表达（P1） |
| ③机制 | 全零行=现金日 | vectorized_engine.py:462,286 | 冻结不卖 | 不可清零（P1） |
| ②下游 | 现金对账 | reconcile_composed_nav:1261 | 零调用 | 未接线（P1） |
| ⑥数据 | 产物现金序列 | _collect_timeseries:1645-1665 | 无 cash/positions | 不可事后核（P1） |
| ④后端 | skipped fills 计数 | vectorized_engine.py:302 | 仅日志不入产物 | 现金缺口不可见（P1） |
| ③机制 | 席位/保证金 | grep 无 | 现货无杠杆 | 能力缺须披露（P2） |
| ③机制 | A股资金T+0可用 | portfolio.py:252 | 卖得先回账再买 | 正确✓（记功） |

## 3 业界与开源对照（四闸）

- **现金腿可核**：Zipline/qlib 回测账户每日落 `portfolio.cash`/positions，可重算 NAV=cash+Σqty·px。
  本项目产物**不落现金/持仓序列**（§1.3）→ 违反"可回测+可对账"。四闸：来源✓≥2✓可得✓（内存
  Portfolio.cash 已有）→ **接线即得**。
- **闲置现金计息**：机构回测常以 repo/货基利率给现金计息。本项目 0 息=保守偏差，方向不致命，
  但应在成本归因里显式（与 §H2 cost_attribution 合并）。
- **主动现金/目标现金**：主流可 `order_target_percent` 令 Σ<1 持现金（业界基线，见 §H3）。
  本项目满仓强制 → 与契约相悖（§1.2）。
- **席位/保证金**：券商级回测（CTP/两融）建模席位与保证金占用；本引擎明确现货无杠杆，若蓝图
  含信用策略则不兑现 → 四闸"可得性"层面须核对蓝图宣称。

## 4 堵点与欠账清单（文件/函数/验收标准）

| ID | 级别 | 病灶类 | 堵点 | 可施工验收标准 |
|----|------|--------|------|----------------|
| H4-A | **P1** | 零消费者 | `reconcile_composed_nav`（framework_composer.py:1261）从不被调用 | 在 `run_framework_backtest` 收尾调用并把结果并进 `panel_reconciliation`/acceptance；验收：现金腿残差>阈值（如 NAV 的 1e-4）时 acceptance.ok=false |
| H4-B | **P1** | 未接线/证据缺 | `_collect_timeseries`（:1645）不收 cash/positions，产物无现金序列 | 产物新增 `cash_curve`+`positions_curve`（Portfolio 已有数据源）；验收：任一时点 `cash+Σqty×px≈equity`（<1e-6）可事后复核 |
| H4-C | **P1** | 语义 | 主动持现金不可达：全零行=不交易、成员余量被行归一吞 | 使引擎区分"空信号"与"目标 Σ<1"；验收：Σ=0.6 面板→账户留 40% 现金、换手相应下降 |
| H4-D | **P1** | 静默降级 | skipped fills（现金缺口/不可成交腿）不入产物 | `skipped_fills` 计数+原因分类（现金/T+1/持仓/不可成交腿）进 metrics；验收：证据包可见"因现金/流动性留下的量" |
| H4-E | **P2** | 能力缺披露 | 席位/保证金/两融未建模（现货无杠杆长仓） | 在回测能力声明处划界；验收：蓝图信用/多席位宣称与引擎能力对齐（否则标 not-supported） |
| H4-F | **P2** | 保守偏差 | 闲置现金 0 息 | 可选按风险利率计息并披露；验收：现金腿机会成本单列 |

## 4.1 清偿状态与验收机证（2026-09-17 复跑）

| ID | 状态 | 落点 / 验收机证 |
|----|------|-----------------|
| H4-A | ✅ 闭环 | `framework_composer._cash_ledger_reconciliation` 进 `chain` → 产物 `metrics` **且** `_assemble_run_warn`（**缺键也判破**，禁静默通过）+ acceptance 硬闸。端到端真数据探针（未经 monkeypatch，150 标的 / 2026-07-01~09-15，产物写会话 staging；临时件收尾清理）：`samples=55 within_tolerance=True max_abs_residual=5.24e-11 worst_date=2026-08-13` |
| H4-B | ✅ 本轮补完（此前半落地） | **坑**：`_collect_timeseries` 造的 `cash_curve` 只随内存 `ts` 返回，`sink_backtest_result` 只收 equity/trade/drawdown/benchmark → 落盘 JSON **无现金腿**（端到端探针实测 `persisted cash_curve points: 0`）。旧测试只断 `ts["cash_curve"]`，故对此回归全盲——正是"验收断内存对象、产物却丢字段"的同族自欺（见 `gate_self_deception_mining.md`）。修法：`metrics["cash_curve"]` 落盘（`BacktestRunArtifact` 顶层受 `[MODIFY-GUARD]` 结构冻结，不加键），测试 `test_artifact_metrics_carry_chain_evidence` 升级为**读盘断言**（落盘==内存、与 `equity_curve` 等长、点结构含 timestamp/cash）。<br>**残余 R-H4B-p**：`positions_curve` 未加——引擎无逐日持仓快照序列（`Portfolio` 只有 `nav_series`/`cash_history`/`trades_log`），市值只能由 `equity−cash` 反推，故"任一时点 `cash+Σqty×px≈equity` 独立复算"仍需真独立量（要引擎侧新增逐日持仓快照），非产物侧可补 |
| H4-C | ✅ 通道已建 + 语义划界 | 持现金意图经 `ShrinkageBacktestEngine`（`config.shrinkage_by_date`，裁定#270）；`vectorized_engine.py:93/451/473/575` 四处 docstring 明示"全零行=当日不下单≠清仓"，`target_weight_renormalization.rows_all_zero` 在产物侧计数披露 |
| H4-D | ✅ 闭环 | `skipped_fills`（含 `by_reason` 分类）进 `metrics`；端到端实测窗口 `by_reason={}`（无被拒腿，属正常而非缺键——键恒在） |
| H4-E | ✅ 闭环 | `execution_model_disclosure`（`schema=execution_model_capability/v1`）落产物，能力划界随产物走 |
| H4-F | ⏳ 未做（P2 排期） | 闲置现金仍 0 息（保守偏差），机会成本未单列 |

## 5 子节点清单

- H4.a 现金/持仓序列入产物（与 §H1 产物 schema、§H2 cost_attribution 共批）。
- H4.b reconcile_composed_nav 接线 + 成为验收项（H4-A）。
- H4.c 目标现金/满仓语义统一（与 §H3-C 同一 `_normalize_day_signals`/`_get_day_signals`）。
- H4.d 不可成交腿（000300 类）清点：raw vs hfq 表差集 census，量化留下的现金。
- H4.e 席位/保证金能力划界（治理车道）。

## 6 封矿判定

**部分封矿**。现金腿实证：无计息✓（保守）、A股资金 T+0 可用/ T+1 持仓✓（正确）、停牌错价防御✓；
但**现金-净值一致性当前不可事后核**（产物无现金序列 + reconcile_composed_nav 零消费者）判 **P1**；
**主动现金不可表达**判 P1；skipped fills 不入证据判 P1；席位/保证金未建模=能力缺须披露（P2）。
**未封子脉**：不可成交腿的现金沉淀量化（需 raw/hfq 表差集 census，本探针未做全量）、reconcile
接线后的残差归因。建议 H4-A/H4-B/H4-C/H4-D 移交施工班，与 §H2/§H3 同批（同一批产物字段）。

## 修复优先级裁定建议

| 编号 | 一句话 | 级别 | 建议归属 |
|------|--------|------|----------|
| H4-A | 现金-净值对账函数零消费者，一致性从不可核 | **P1** | 施工班 |
| H4-B | 产物不落现金/持仓序列，事后无法复算 NAV | **P1** | 施工班（schema 扩展） |
| H4-C | 满仓强制致现金腿不可主动表达 | **P1** | 施工班（与 H3-C 同修） |
| H4-D | 被拒成交/不可成交腿的现金沉淀不可见 | **P1** | 施工班 |
| H4-E | 席位/保证金/两融未建模，能力须划界 | **P2** | 治理/蓝图 |
| H4-F | 闲置现金 0 息（保守偏差） | **P2** | 排期 |
