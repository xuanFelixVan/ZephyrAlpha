---
ttl: task_bound
---

# B20 裁定书草稿：recon_runner L3 期初持仓快照数据源

> **议题**：56 号文 G7 recon_runner L3 PnL 对账的"期初持仓快照"数据源裁定——当前口径为期末市值 − 当日净买入现金流（隐含期初空仓假设），滚动持仓场景下产生系统性偏差。
> **触发条件**：日循环跑通后定（57 号文窗口项）；B6 启用冒烟 checklist 已将其列为 B6-1.3 前置。
> **Owner 窗口**：数据源选择影响对账精度与基础设施改动面，需 Owner 裁定后 AI 施工。
> **关联**：56_backtest_vs_sim_reconciliation_plan.md §5、construction_backlog.md B6、2026-08-30-b5b6-enable-checklist.md B6-1.3。

---

## 1. 问题陈述

recon_runner._compute_l3_pnl（src/zephyr/trading/recon_runner.py L286-321）当前模拟盘当日 PnL 代理公式：

```
sim_pnl = total_market_value(期末) - Σ(当日买入成交额)
```

该公式隐含**期初空仓**假设：若模拟盘滚动持仓（今日开盘前已有持仓），则期初持仓的浮盈/浮亏被错误计入当日 PnL，导致 L3 gap_pct 失真。56 号文 §5 原文登记："滚动持仓场景的期初快照数据源是窗口项（§7 GAP 表外追加项）"。

---

## 2. 候选数据源方案

### 方案 A：miniqmt 持仓快照（T-1 收盘后）

**机制**：T-1 日 15:30 结算单就绪后，调用 `MiniQmtBroker.get_positions()`（L595-637）取 PositionSnapshot（cash + holdings + market_values），序列化落 `tmp/position_snapshot_{trade_date}.json` 或 governance.db 新表；T 日对账时读 T-1 快照作为期初持仓，T 日 PnL = (T 期末市值 + T 日现金变动) - (T-1 期末市值 + T-1 现金)。

**优点**：
- **数据真源直接**：QMT 模拟盘官方持仓快照，与实盘终端完全一致，无推导误差。
- **复用现有接口**：`get_positions()` 已稳定运行，无需新增 QMT 查询逻辑。
- **现金+持仓双覆盖**：PositionSnapshot 同时含 cash 与 total_market_value，L3 PnL 可精确到分。

**缺点**：
- **依赖 T-1 日 QMT 在线**：若 T-1 日 QMT 未运行/未登录，快照缺失，T 日 L3 只能降级为 SKIPPED 或沿用旧口径。
- **新增持久化介质**：需新增 JSON 文件或 DB 表（schema 变更，Owner 窗口 DDL）。
- **跨日一致性风险**：若 T-1 快照后有人工干预（手动买卖/出入金），T 日对账会暴露非策略差异，需额外过滤规则。

### 方案 B：结算单反推期初持仓

**机制**：T 日 15:30 后从 `query_stock_trades(trade_date)`（G3 兜底）+ 历史成交回填推导：期初持仓 = 期末持仓 − 当日净买入 + 当日分红/拆股调整（如有）。以 `broker_settlement_adapter` 产出的 BrokerSettlementRecord 序列为基础，逐 symbol 反推数量。

**优点**：
- **零新增 QMT 依赖**：只依赖已施工的 G3 `query_trades_today` 与既有 settlement adapter，无额外快照任务。
- **无跨日持久化**：不新增文件/表，对账自包含。
- **与 L1/L2 同源**：期初持仓推导与 L1 交易级 diff、L2 持仓级 diff 共用同一批成交记录，口径一致性高。

**缺点**：
- **推导误差**：无法覆盖非交易事件（分红送股、合并拆分、T-1 盘后人工调仓），导致期初持仓反推偏差；QMT 模拟盘分红事件极少但非零。
- **无法获取期初现金**：现金变动需额外假设（如"现金变动=当日净买入"），不覆盖利息/费用/人工出入金，L3 PnL 现金侧精度低于方案 A。
- **断点放大**：若 T-1 日成交推送有缺漏（56 号文 R2），反推误差会累积到 T 日。

---

## 3. 推荐裁定

**推荐方案 A（miniqmt 持仓快照）为主数据源，方案 B（结算单反推）为降级兜底**。

理由：
1. **精度优先**：L3 对账的核心价值是验证"回测=实盘 PnL 一致性"，期初持仓误差直接污染 gap_pct 判定阈值（0.1%）。方案 A 的现金+持仓双字段精度是方案 B 无法达到的。
2. **QMT 常开已裁定**：57 号文 §1 已确立"QMT 常开（Owner 裁定，不手动关闭就不关闭）"，T-1 日在线是常态；若真离线，deadman_switch 与 57 号文 C1 检查项会先于对账暴露。
3. **改动面可控**：仅需在 post_settlement_pipeline（15:30）或独立日终任务中追加一次 `get_positions()` 落盘，JSON 文件即可起步（不重 DDL）；后续如需审计追踪再升级 governance.db 表。
4. **降级路径清晰**：T-1 快照缺失时自动降级为方案 B 反推 + 日志标注 "L3 降级：期初持仓快照缺失，使用成交反推口径"，不阻断对账主流程。

---

## 4. Owner 勾选位

| 选项 | 说明 | 勾选 |
|---|---|---|
| **A** | 采用方案 A（miniqmt 持仓快照）为主数据源；T-1 15:30 后自动落 `tmp/position_snapshot_{date}.json`；T 日对账读取；缺失时降级方案 B | ☐ |
| **B** | 采用方案 B（结算单反推）为唯一数据源；不新增快照任务；接受推导误差与现金侧精度损失 | ☐ |
| **C** | 维持现状（期初空仓假设）；仅在模拟盘明确每日 fresh 开仓的交易日启用 L3，滚动持仓日 L3=SKIPPED | ☐ |
| **其他** | Owner 补充：________________ | ☐ |

**Owner 签字/日期**：________________

---

## 5. 施工项（裁定后由 AI 执行）

若 Owner 勾选 A：
1. `scripts/run_post_settlement.py` 或 `post_settlement_pipeline` 追加 `--snapshot` 参数：15:30 结算后调用 `broker.get_positions()` 落 `tmp/position_snapshot_{trade_date}.json`（JSON 序列化 PositionSnapshot，含 cash/holdings/market_values/total_market_value/as_of_timestamp）。
2. `recon_runner._compute_l3_pnl` 改造：优先读取 T-1 快照计算期初权益；缺失时降级为成交反推 + 日志标注。
3. `deadman_switch.ps1` 可选第五路：T-1 快照缺失告警（盘中 09:30-15:00 检查 `tmp/position_snapshot_{T-1}.json` 存在性）。

若 Owner 勾选 B：
1. `recon_runner._compute_l3_pnl` 内实现成交反推逻辑（期初持仓 = 期末持仓 − 当日净买入）。
2. 日志显式标注 "L3 口径：结算单反推期初持仓（无现金变动修正）"。

若 Owner 勾选 C：
1. 零代码改动；B6 checklist B6-1.3 标记为 "Owner 裁定维持现状，滚动持仓日 L3 跳过"。

---

## 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-30 | 1.0.0 | 初版 | B20 数据源裁定无正式评估文档，补草稿供 Owner 勾选 |
