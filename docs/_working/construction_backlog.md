---
ttl: task_bound
---

# 回测启动施工待办清单（construction backlog）

> 生成时间：2026-08-21 ｜ 目标态：全模块可启动 + 交易日模拟盘 + 收盘后回测对账
> 口径来源：57 号文日循环 SOP 彩排结论 + 注册表实测（universe 6/benchmark 8/cost_model 5 已 active；strategy 146 条/factor 140 条全 draft）
> 本文件为施工顺序总账，完成一项勾一项；Owner 窗口项已显式标注。

> **结案审查（2026-08-30 复核）**：阶段 A 已全量勾销闭环（2026-08-30 长城批实证）
> - 已实证：BTRUN/DVERIFY 首批实测报告在 `.runtime/construction_20260823/reports/`（momentum_20d IC=-0.0399 首份实测范式；factor IC 回填）；B 阶段 Owner 窗口项已转 `docs/_archive/2026-08-23-construction-order-master.md` 挂起登记（2026-08-28 归档）。
> - 2026-08-30 长城批：A1~A5 逐项 grep/查库实证后勾销（证据随各条目行尾注记，commit 2a16988d）；B 阶段 Owner 窗口项维持未勾不动；C 阶段另案执行不受影响。

---

## 阶段 A：纯历史回测启动（不依赖 QMT，无 Owner 窗口阻塞）

### A1. 行情数据追平（前置：无）
- [x] kline_daily 采集追平至最新交易日（现滞后至 2026-08-19） — ✅ 已核销（2026-08-30 实证：CH 实证 kline_daily/kline_index/stk_limit 三表 max(trade_date)=2026-08-28）
- [x] stk_limit 同步追平 — ✅ 已核销（2026-08-30 实证：stk_limit max=2026-08-28，随三表同批 CH 实证）
- [x] 追平后跑 `scripts/ch/_data_inventory.py` 实证 min/max(trade_date) 新鲜度 — ✅ 已核销（2026-08-30 实证：CH 直查三表 min/max 新鲜度达标）
- 验收：数据最新交易日 = 最近一个真实交易日

### A2. 北交所退市股 K线补缺（前置：A1）
- [x] 北交所退市标的清单盘点 — ✅ 已核销（2026-08-30 实证：北交所退市 5 只全有行情）
- [x] 历史 K线回填入库 — ✅ 已核销（2026-08-30 实证：5 只退市股行情在库，check_survivorship_bias 门禁在位可过）
- 验收：check_survivorship_bias 门禁可过；不补则回测有幸存者偏差

### A3. 历史指数成分股回填（前置：A1）
- [x] CSI300 / CSI800 等基准历史成分回填 — ✅ 已核销（2026-08-30 实证：index_constituent SCD-2 表在位，本批已补采 8 月末快照，五指数推进至 08-28，000300 版本链干净）
- 验收：universe PIT 可重建"当时股票池"，回测 universe_id 指向真历史成分

### A4. 首批被测策略激活（前置：无，可与 A1-A3 并行） ✅ 已核销（首批已激活，2026-08-30）
- [x] 从 strategy_registry 146 条 draft 中选定首批 3-5 条 — ✅ 已核销（2026-08-30 实证：首批 4 条 candidate→active——STR-VREV-017/018/019、STR-MULTIFACTOR-069）
- [x] 逐条 draft → active，显式绑定 universe_id + benchmark_id + cost_model_id 三件套 — ✅ 已核销（2026-08-30 实证：4 条 active 三件套绑定齐全）
- [x] 对应 factor_registry 条目补齐 IC 性能字段（跑实测回填） — ✅ 已核销（2026-08-30 实证：因子 IC code-anchored 4/4 回填，NL 143 条锚定裁定登记，见 .runtime/factor_ic_backfill/20260830_report.md）
- 验收：每条 active 策略三件套引用完整，C1 runner 可直接点名

### A5. 第一份回测报告（前置：A1-A4 全齐）
- [x] C1 向量化回测全量跑批（彩排已实证 trades=17 落盘链路通） — ✅ 已核销（2026-08-30 实证：BTRUN_report.md 首份回测报告 bt-790d8a95，净值/夏普/回撤/超额 vs benchmark 四指标齐全）
- [x] sink 落盘 + 结果归档 — ✅ 已核销（2026-08-30 实证：bt-790d8a95 落盘 data/backtest_artifacts/，报告在 .runtime/construction_20260823/reports/BTRUN_report.md）
- 验收：产出成立以来第一份真回测报告（净值/夏普/回撤/超额 vs benchmark）

---

## 阶段 B：回测=实盘对账闭环（依赖 QMT + Owner 窗口）

### B1. QMT 常开保活（Owner 人工，每个交易日）
- [ ] 开盘前人工启动 QMT + 手动输密码登录（无法自动登录，P0-1 已裁定）
- [ ] 日循环 SOP 开盘前检查项确认"QMT 在线"
- 验收：C1 探活过（同 tracker #243 口径）

### B2. reconciliation_differences 表 DDL 执行（Owner 窗口，tracker #234）
- [ ] Owner 批准后执行 DDL
- 验收：对账 diff 可落库；不执行则对账跑了不落库

### B3. audit_fn 接真源（前置：B2）
- [ ] DailyAuditor.audit 持仓/净值/限额真源接线（现为空快照）
- [ ] SettlementReconciler.reconcile 注入 post_settlement 管线
- 验收：结算管线跑真实件而非空快照五件套

### B4. LiveStrategyAdapter 真信号源施工（前置：A4，GAP-2 残余）
- [ ] 模拟盘信号源从空转接真策略信号
- [ ] start_paper_session.py 交易日 09:25 前拉起（当前手动形态）
- 验收：模拟盘产生可对账的真实信号成交

### B5. post_settlement 挂调度（Owner 窗口，GAP-3 残余）
- [ ] cron 30 15 * * * 规格已备好，Owner 批准后接线
- 验收：15:30 收盘结算自动化，不再手动 dry-run

### B6. 首次对账跑通（前置：A5 + B1-B4）
- [ ] 同信号同窗口：回测 vs 模拟盘 成交/持仓逐日 diff
- [ ] 偏差归因登记（滑点/部分成交/拒单）
- 验收：产出第一份回测=实盘对账报告，偏差可归因

---

## 阶段 C：贯穿安全网（另案执行，不阻塞 A/B，但约束改动自由度）

### C1. 测试债专项批（P0-3 / 63 号，「残余四项专项批」另案执行中）
- [ ] 56 存量红逐条归因清零
- [ ] 785 failed / 17 errors 分包清偿（cross 22/autonomy 22/external 21/semantic 19/escalation 17 簇）
- 验收：回归网可信——回测异常数字可快速区分"策略亏" vs "代码 bug"
- 📌 **2026-08-23 全量实测已覆盖本项旧账**：190 簇 2659 文件全扫，46,786 通过 / 仅 7 失败（真红 4 + flaky 3）+ 1 已知假死豁免。**施工修复以 `.runtime/construction_backlog.md`（模块单元测试状态总账）为准**，下面两行旧数字仅作历史参照

### C2. P0-2 残余（另案执行中，不阻塞回测）
- [ ] FLE gates 启用评估（#61 CAND 另案裁定）
- [ ] trend_analyzer 库处置（残余四项专项批）
- [ ] Dashboard 死数据"数据截至"提示（残余四项专项批）

---

## 施工顺序总览

```
A1 数据追平 ─┬─ A2 北交所补缺 ─┐
             └─ A3 指数成分回填 ─┴─ A5 首份回测报告
A4 策略激活（可并行）──────────┘         │
B2 DDL（Owner 窗口）─ B3 audit_fn 接线 ─┤
B1 QMT 常开（Owner 每日）─ B4 真信号源 ─┴─ B6 首次对账
B5 结算挂调度（Owner 窗口）──────────────┘
C1 测试债 / C2 P0-2 残余：并行另案，不阻塞主线
```

## 下一交易日最小动作
1. Owner：开盘前手动启动 QMT（B1，5 分钟）
2. AI：A1 数据追平 + 新鲜度实证
3. AI：A4 首批策略激活（不等数据补齐即可先做）
