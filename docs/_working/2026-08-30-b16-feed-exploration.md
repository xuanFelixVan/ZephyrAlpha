---
ttl: task_bound
---

# B16 勘探裁定：dReport / Jump on PEAD 数据可得性评估

- 日期：2026-08-30
- 任务：勘探 26 号文 §2.4 六因子矩阵中"待施工"两因子（dReport / Jump on PEAD）的输入数据可得性
- 方法：grep 实证 daily_event 调度族 + ClickHouse DDL-as-Code 真源 + 计算件落码状态（不连库实测行数）
- 依据文档：`docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md` §2.4 事件驱动六因子矩阵（v1.5.0）

## 1. 因子输入需求拆解

| 因子 | 定义（26 号文 §2.4） | 所需输入 | 实证依据 |
|---|---|---|---|
| dReport | `dReport = 法定披露截止日 − 实际披露日`（正值=提前） | ① 法定披露截止日（报告期→截止日规则）② 实际披露日（逐股逐报告期） | 招商证券 10 年回测年化超额 4.88%/Sharpe 1.44 |
| Jump on PEAD | 公告后 5 日窗口 CAR 的跳跃分量（\|AR\|≥3% 保号求和） | ① 事件日（实际披露日/快报公告日）② 日频 OHLC（事件窗 ±5 日）③ 基准收益（CAR 的市场/行业基准） | 华泰金工 5 日 IC=10.96% |

## 2. grep 实证：daily_event 族在仓情况

### 2.1 已在仓（数据源+表+调度三齐）

| 输入项 | 证据 | 状态 |
|---|---|---|
| **实际披露日** | `c3_fundamental.disclosure_plan.actual_date`（DDL 真源 `schemas/categories/fundamental_disclosure_plan.py` L43：`actual_date Nullable(Date) COMMENT '实际披露日期'`）；采集任务 `disclosure_plan_incremental`（`src/zephyr/data/config/tasks.yaml` L1775-1785，source=akshare `stock_report_disclosure`，schedule=daily_event，P1 百度云历史持续更新批次 2026-07-11）；provider 落码 `akshare_provider._fetch_disclosure_plan`（L5067-5146，"实际披露"字段 → actual_date） | ✅ production |
| **预约披露日**（辅助） | 同表 `scheduled_date`（"首次预约"字段） | ✅ production |
| **法定披露截止日** | `src/zephyr/data/implementations/calendar_event_derivations.py` `derive_earnings_deadline`（EARNINGS_DEADLINE_DATES=(4/30, 8/31, 10/31)，遇非交易日取前一交易日）——确定性日历规则，无需外部数据 | ✅ 已落码 |
| **业绩快报公告日** | `c3_fundamental.express_report`，任务 `express_report_incremental`（tasks.yaml L591-601，source=miniqmt QMT Performance 表，date_col=announce_date，schedule=daily_event） | ✅ 已登记 enabled |
| **业绩预告**（辅助） | `c3_fundamental.earnings_forecast`，任务 `earnings_forecast_incremental`（tasks.yaml L579-589，QMT ProfitForecast，announce_date） | ✅ 已登记 enabled |
| **日频 OHLC** | `market_kline_daily`（`schemas/categories/market_kline_daily.py`，daily_kline 时段） | ✅ production |

### 2.2 计算件落码状态

| 件 | 路径 | 状态 |
|---|---|---|
| `compute_dreport(statutory_deadline, actual_disclosure_date)` | `src/zephyr/intelligence/event_factor_matrix.py` L78 | ✅ 已实现（MATURITY=design，纯函数） |
| `compute_jump_on_pead`（5 日窗口 AR 跳跃/漂移分解） | 同模块（F2） | ✅ 已实现 |
| `PeadEventModel`（SUE/漂移窗口，MOD-SIG-110） | `src/zephyr/signal_fundamental/pead_event_model.py` | ✅ production（DI 注入式，不直接读披露表） |

**关键结论：两因子的"采集层+计算层"都已在仓/已落码，缺口只在装配层**——grep `dReport|jump_on_pead` 全 src 仅命中 `event_factor_matrix.py` 本体与无关文件，无任何"从 disclosure_plan/kline 读数 → 喂计算件 → 出因子值"的装配代码。

### 2.3 缺口清单（需外部源或待裁定）

| 缺口 | 说明 | 性质 |
|---|---|---|
| dReport 装配批 | disclosure_plan.actual_date + 报告期→法定截止日映射（复用 derive_earnings_deadline 规则）→ compute_dreport → 因子表 | 仓内可闭合，无需外部源 |
| Jump on PEAD 装配批 | 事件日（disclosure_plan.actual_date 或 express_report.announce_date）+ kline 日收益 → compute_jump_on_pead | 仓内可闭合 |
| CAR 基准口径 | 公告后 5 日 AR 的基准（大盘指数/行业指数/市场均值）未在 26 号文裁定 | **待裁定**（非数据缺口——`market_kline_index`/`market_kline_sector_880` 均在仓可选） |
| 实际披露日填充率 | akshare `stock_report_disclosure` 的"实际披露"字段在披露完成前为 None（provider 已容错 `actual_date or None`）；历史报告期填充率未实测 | 待 ClickHouse 实测（`scripts/ch/_data_inventory.py`） |
| actual_date 时点语义 | 披露日 vs 披露时刻（盘前/盘后）——A 股财报多盘后披露，事件日归入 T 还是 T+1 影响 Jump 窗口起点 | 待裁定（26 号文未定义时刻粒度） |

## 3. 建议裁定

**裁定：GO——两因子均可立即施工装配层，无需引入新外部数据源。**

1. **dReport（优先，4.88% 年化实证最强）**：输入三件齐（截止日历 ✅ + 实际披露日在仓 ✅ + 计算件 ✅）。施工 = 装配批一只：按 (symbol, report_period) 读 disclosure_plan.actual_date + derive_earnings_deadline 推截止日 → compute_dreport → 落因子表。注意 None 过滤（未披露报告期）。
2. **Jump on PEAD**：输入齐（事件日 ✅ + 日K ✅ + 计算件 ✅）。施工前置一个小裁定：CAR 基准口径（建议沪深300/中证500 双跑，G23 回测标定）。
3. **与 event_factor_matrix 的关系**：两因子计算件 MATURITY=design，装配批落地时应同步把模块成熟度推进并对账 tests/intelligence/test_event_factor_matrix.py。
4. **数据质量前置验证（施工第 0 步）**：跑 `scripts/ch/_data_inventory.py` 确认 disclosure_plan 近 3 年 actual_date 非空率（asset_index 显示该任务 2026-07 有两次增量失败记录，需确认已恢复）；若非空率不足，降级方案 = 用 express_report.announce_date（QMT 源）兜底事件日。
5. **时点语义裁定建议**：财报盘后披露口径下，事件日统一取"实际披露日的次一交易日"（与 T+1 可交易性一致），与 ORJ（次日开盘跳空）口径自洽。
