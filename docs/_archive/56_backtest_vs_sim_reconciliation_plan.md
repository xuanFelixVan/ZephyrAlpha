---
ttl: permanent
---

> **归档注记（2026-08-30）**：自 design_memos/implementation_plans 归档（候选核销批 greatwall_20260830——内容全量施工完毕核销，审计链保留，原位索引已同步标注）。
>
> **文档元信息**（_working 临时区豁免规范：EXEMPT-ZONE-FM）：completes_when=对账链路 G3/G4/G5/G7 施工完成且 G1/G6 Owner 裁定落地后归档（归档不删除，保留审计链） · doc_type=architecture_view · version=1.0.0 · created=2026-08-21 · owner=P0 批统筹代办，Owner 审批（含 DB 写操作窗口项）

# 56 · 回测 vs 模拟盘对账方案与对照清单（P0-1②）

> ## 结案报告（2026-08-28 全量审查批，代码实证）
> **实际开发**：G3 query_trades_today（miniqmt_broker 盘后兜底+Fill JSONL 落盘回放）；G4 broker_settlement_adapter.py（配对键 {symbol}|{seq:03d}）；G5 backtest_fills_adapter.py（回测 trade_log→Fill+持仓重放）；G7 recon_runner.py（L1/L2/L3 编排+归因三分类+落 reconciliation_differences）；G1 三套费率已统一（Owner 裁定回测以实盘万0.854 为准，8 处费率点统一）；G6 四表 DDL 已落 governance.db。
> **最终成果**：对账链路 AI 可施工项全闭环（2026-08-21，测试 39+45 件全绿），G1/G6 Owner 窗口项均已落地。
> **未做+原因**：①recon_runner 维持 testing 封顶（B-007 分期，production 启用挂起等 Owner）；②L3 期初持仓快照数据源=57 号文窗口项。

> **用途**：定义"同信号同窗口"下回测与 QMT 模拟盘的成交/持仓逐日 diff 机制与偏差归因口径，供 P0-5 日循环 SOP 的"当日回测跑批→对账 diff→异常登记"环节直接嵌入。
> **口径铁律**：对账比对以**数量与成交价为主键**，佣金/税费仅作参考列——仓内现存三套费率口径不一致（见 §4 风险 R1），费率统一未裁定前，费用差不得判为 drift。
> **不产生第二真源**：对账设计真源=54 号文，监控节奏真源=55 号文，本文只是两者在"回测 vs 模拟盘"场景的接线方案+任务清单。

---

## 1. 对账不变量（先决条件，不满足则对账无意义）

| # | 不变量 | 机制保证 | 证据 |
|---|---|---|---|
| I1 | **同信号**——回测与模拟盘跑同一策略实例 | 统一抽象 `StrategyBase.generate_target_weights() -> dict[str, float]`；三态共用（盘后回测/盘中模拟盘/实盘）复用同一 StrategyBase 实例 | strategy_base.py L62-79；strategy_runner.py L36-39 |
| I2 | **同撮合语义**——预成交校验规则一致 | 撮合层 `MatchingLogic` 回测/实盘共用（"回测=实盘一致性"显式不变量）；miniqmt_broker.submit_order 内置同款预成交校验 | matching_logic.py L17-21；miniqmt_broker.py L8/L27 |
| I3 | **同窗口**——同一交易日、同一 universe、同一行情快照源 | 回测用当日 bar 重放；模拟盘行情走 MiniQmtQuoteProvider（userdata_mini）；对账日 universe 快照两侧各存一份入对账输入 | qmt_environments.yaml L32-46 |
| I4 | **逐笔可得**——回测侧必须显式落 trade_log | `BacktestResult` 仅 15 个汇总字段无逐笔；跑批必须经 `backtest_result_sink`（TradeRecord 口径）落 `data/backtest_artifacts/{run_id}.json` | engine_base.py L86-103；backtest_result_sink.py L117-126 |

## 2. 对账架构（三层 diff，复用现有引擎，只补适配层）

```
┌─基准侧（回测）─────────────┐   ┌─实盘侧（QMT 模拟盘）──────────┐
│ backtest_artifacts/{run_id} │   │ FillHandler 累计 Fill（内存）  │
│   .json → trade_log         │   │  +盘后 query_stock_trades 兜底 │
│   (TradeRecord/fill 明细)    │   │ get_positions() 持仓快照       │
└──────────┬─────────────────┘   └──────────────┬───────────────┘
           │ 【适配层 A：回测 fills→系统侧输入】   │ 【适配层 B：QMT 数据→BrokerSettlementRecord】
           ▼                                    ▼
┌──────────────────────────────────────────────────────────┐
│ L1 交易级：SettlementReconciler（价格/数量容差+双向缺失，5 类 DriftType）│
│ L2 持仓级：PositionReconciler（日终持仓逐标的 diff）                  │
│ L3 PnL 级：DailyAuditor PnL 对账（expected vs realized，0.1% 容差）   │
└──────────────────────────┬───────────────────────────────┘
                           ▼
        reconciliation_differences（recon_layer=trade/position/cash）
        偏差归因三分类 → 异常登记 tracker / 55 号日监控节奏
```

- **L1 交易级**（逐笔成交 diff）：复用 `trading/settlement_reconciliation.py` L203 `reconcile`（容差见 `ReconciliationConfig` L78-80；双向缺失检测=回测有实盘无/实盘有回测无）。
- **L2 持仓级**（日终持仓 diff）：复用 `ex_core/position_reconciler.py` 双源比对语义，基准侧持仓由回测 trade_log 重放推导（`Position`/`trades_log()`，portfolio.py L81/L315），实盘侧 `get_positions()`（miniqmt_broker.py L595）。
- **L3 PnL 级**：复用 `risk/core/daily_auditor.py` L286 `PnLReconciliation`（|gap_pct|≤0.001 容差）。
- 可选交叉验证：`simulation/divergence_attributor.py` 四因子门禁（signal_match≥99.9%/滑点<1bp/PnL 相关≥0.95）作严重度参考，不作判据主源。

## 3. 偏差归因三分类（异常登记口径）

| 归因类 | 判定特征（diff 形态） | 典型根因 | 处置 |
|---|---|---|---|
| **A 滑点** | 同标的同方向，数量一致、成交价偏差超容差 | 回测 `slippage_bps=1` 假设 vs 模拟盘真实撮合价差；行情快照口径差 | 累计入滑点样本池（slippage_analyzer），超 1bp 系统性偏离→触发 cost_model 校准评审（数据期 CAND 族） |
| **B 部分成交** | 同标的同方向，实盘数量 < 回测数量 | 模拟盘流动性/排队未成交；回测假设全量成交 | 单笔记差异不告警；同标的连续 2 日部分成交→登记 tracker 评估撮合假设 |
| **C 拒单/缺失** | 回测有实盘无（或反向）整笔缺失 | 预成交校验拦截（涨跌停/验资/T+1）、断线补单失败、QMT 离线 | **当日即告警**——目标态总开关失效信号，日循环 SOP 异常登记首查项 |

> 费用差（佣金/印花税/过户费）单独列示**不归类**——三套费率口径统一裁定前仅作参考列（§4 R1）。

## 4. 缺口清单与施工项（排序=依赖序）

| # | 缺口 | 施工项 | 量级 | 窗口/批准 |
|---|---|---|---|---|
| G1 | **三套费率口径不一致**：matching_logic（佣金万3/印花税千1）vs pnl_calculator（万2.5/万5）vs t0_cost_model（万3/万5） | 裁定唯一口径（建议以券商实际交割单费率为准回填 MatchingConfig），三处对齐 | 裁定+小改 | **Owner 裁定项**（影响全仓回测数值口径） |
| G2 | 回测逐笔无 DB 持久化，仅有 JSON 文件 | 短期：对账直读 JSON（G1 裁定前不动 DB）；长期：入 reconciliation_differences | 0（本期不建表） | — |
| G3 | QMT 成交无 `query_stock_trades` 封装（src 零调用，全靠 on_stock_trade 推送） | 补盘后同步查询兜底封装（严守 40 号戒律：回调内禁同步查询，仅盘后用）；补 Fill 落盘持久化（JSONL 追加，与 AppendOnlyDedupSet 同目录风格） | ~80-120 行 | 无 DB 写，AI 可做 |
| G4 | `BrokerSettlementRecord` 无券商侧适配器（唯一构造点在 docstring 示例） | 适配层 B：QMT trades/positions → BrokerSettlementRecord | ~60 行 | AI 可做 |
| G5 | 适配层 A：回测 trade_log → 系统侧 fills 输入 | 读 backtest_artifacts JSON → SettlementReconciler 系统侧输入 | ~60 行 | AI 可做 |
| G6 | `reconciliation_differences` 表 DDL 仅定义未执行（reconciliation_schema.py L26-27 自声明"不执行 DDL"） | 执行 DDL 落库 | — | **Owner 窗口项**（DB 写操作，随 #221 同批提请） |
| G7 | 对账编排器（串 L1/L2/L3 + 归因分类 + 异常登记） | 新模块 `recon_runner`（testing 态封顶，宪章 B-007） | ~150 行 | AI 可做，production 启用挂起等 Owner |

## 5. 日循环嵌入点（与 P0-5 SOP 对接）

1. **09:15 开盘前**：人工确认 QMT 在线（Owner 窗口项，常开口径）+ 数据就绪检查；
2. **盘中**：模拟盘运行，FillHandler 累计当日 Fill（G3 落盘后持久化）；
3. **15:30 收盘后**：① G3 兜底封装拉 `query_stock_trades` 补全推送缺漏 → ② 当日同信号回测跑批（同 universe 快照）→ ③ L1/L2/L3 三层 diff → ④ 归因三分类，C 类当日告警 → ⑤ 异常登记 construction_progress_tracker；
4. **节奏对接**：上述 ③④ 即 55 号监控"日自动"件，周报汇总进"周人工"。

## 6. 对账对照清单（每日跑批勾选表）

| # | 检查项 | 通过判据 | 失败处置 |
|---|---|---|---|
| C1 | QMT 模拟盘在线且当日有登录态 | get_positions() 正常返回 | 记 C 类异常，当日对账标记 SKIP 并人工查 QMT |
| C2 | 同信号：回测与模拟盘策略实例/参数/universe 快照哈希一致 | 两侧快照哈希相等 | 记 C 类，查信号链路断点 |
| C3 | 回测 trade_log 非空且落盘完整 | JSON 存在且 TradeRecord 数=trades_count | 记 C 类，查 I4 不变量 |
| C4 | 成交笔数 diff | \|回测笔数-实盘笔数\| / 回测笔数 ≤ 5% | 超限按 B/C 归因逐笔分类 |
| C5 | 成交价 diff（L1 容差） | SettlementReconciler 价格容差内 | 超差→A 类滑点登记 |
| C6 | 成交数量 diff | 数量一致率 ≥ 95% | 不足→B 类部分成交登记 |
| C7 | 日终持仓 diff（L2） | 逐标的持仓数量完全一致（T+1 口径对齐后） | 差异标的冻结并登记 |
| C8 | PnL 对账（L3） | \|gap_pct\| ≤ 0.001 | 超限→DailyAuditor 日终五件套流程 |
| C9 | 费用参考列 | 仅记录不判定 | 系统性偏差>20% 提示 G1 裁定紧迫性 |
| C10 | 异常登记闭环 | 当日全部 A/B/C 类差异有 tracker 条目或豁免理由 | 未闭环→次日 SOP 首查 |

## 7. 风险登记

- **R1（口径噪音淹没真实 drift）**：三套费率不一致使佣金差必然存在——已由"数量/成交价为主键"口径隔离，治本=G1 Owner 裁定。
- **R2（推送缺漏误判为拒单）**：on_stock_trade 推送在断线重连窗口可能漏——G3 盘后 `query_stock_trades` 兜底补齐后才得判 C 类。
- **R3（模拟盘撮合≠实盘撮合）**：QMT 模拟盘撮合规则与真实交易所存在差异，本对账验证的是"系统链路一致性"，不代表实盘成交率——实盘过渡时另走 paper_live_transition 门禁（paper_live_signal_match）。

---

> 本文 ttl=permanent + completes_when 归档条件（DCR-003 口径），随 P0-1②/P0-5 施工滚动更新；G1/G6 两个 Owner 窗口项已登记总账 §7 通道提请。
