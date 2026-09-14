---
ttl: task_bound
---

> **文档元信息**（_working 临时区豁免规范，EXEMPT-ZONE-FM）：doc_type=design_memo_working · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.0.0 · date=2026-08-30 · topic=event_driven_six_factor_construction · scope=07_trading_decision_architecture · completes_when=六因子矩阵 event_impact_score 接线进 event_funnel/sleeve 且 G23 校准完成后归档。

# B4：事件驱动六因子矩阵——施工条件评估 + 施工分解框架

> **上游真源**：[26_event_driven_strategy_detail](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md) §2.4 六因子矩阵块（v1.5.0）+ §2.5 落地公式（event_impact_score = w1·ORJ_z + w2·dReport_z + w3·Jump_on_PEAD_z + w4·overnight_trend_z + PEAD_inversion_gate）。
> **评估结论（2026-08-30 实证）**：**具备施工条件，不登记 ARCH-299**。算法层已落码、数据管道实证就绪；残余为接线/校准类施工内容（非数据/前提缺口）。

---

## 1. 六因子矩阵构成与现状盘点

| 因子 | 定义 | 实证 | 算法状态 | 数据依赖 | 数据状态 |
|---|---|---|---|---|---|
| ORJ（隔夜跳空） | `open/pre_close - 1` | collinseow 2026-02 季度超额 6.78% | ✅ production（event_score.py overnight_return_jump） | OHLC | ✅ production |
| PEAD Inversion | \|reaction\|>3% 反转非延续 | Vortex Capital 2026-05 | ✅ production（event_score.py extreme_reaction_modifier / check_selling_pressure_absorbed） | OHLC | ✅ production |
| dReport（披露提前天数） | 法定披露截止日 − 实际披露日 | 招商证券 10 年年化超额 4.88%/Sharpe 1.44 | ✅ 已落码（intelligence/event_factor_matrix.py `compute_dreport`，MOD-INT-EVENT-FACTOR，MATURITY=design） | disclosure_plan（scheduled/actual_date） | ✅ **305,685 行，2018-2026 年度连续，actual_date 覆盖 99.6%**（本日 ClickHouse 实证）；provider akshare stock_report_disclosure + tasks.yaml `disclosure_plan_incremental`（daily_event）+ event_calendar_filler 消费链在位 |
| Jump on PEAD | 公告后 5 日窗口 CAR 跳跃分量（\|AR\|≥3% 保号求和） | 华泰金工 5 日 IC=10.96% | ✅ 已落码（`compute_jump_on_pead`） | 事件日（disclosure_plan）+ OHLC + 基准 | ✅ 同上 + 指数日K production |
| 隔夜趋势 | 隔夜收益率 20 日滚动均值 | 西部证券 Rank IC=-0.1687、中证2000 年化超额 7.97% | ✅ 已落码（`compute_overnight_trend`） | OHLC | ✅ production |
| AStockEvent Feed | 13+ 事件类型结构化 Feed | GitHub 2026-06-13 | ❌ **远期不做**（26 号 §2.4 登记 + 模块 INVARIANTS 双确认） | 外部 GitHub Feed | ❌ 外部依赖，既定延期 |

配套事件源管道（26 号 §1.4 已盘点 production，本日抽验）：新闻真源 `c3_fundamental.news_data` 8,129,795 行 ✅；`c1_market.dragon_tiger` 986 行（max 2026-08-28）✅；corporate_action_processor / market_event_integrator（EMERGENCY）/ ipo_calendar 均在位。

## 2. 施工前提裁定

- **数据前提**：✅ 就绪。dReport/Jump on PEAD 的关键数据源 disclosure_plan 本日实证在库且年度连续；OHLC/新闻/龙虎榜均 production。
- **算法前提**：✅ 就绪。三数值因子已落码且 tests/intelligence/test_event_factor_matrix.py 在位。
- **既定边界**：AStockEvent Feed 远期不做（不阻塞）；sentiment_score 不进截面排序（QLoRA 警示，26 号 §2.7）——六因子矩阵为数值 alpha 路径，不依赖 NLP 管道就绪。
- **结论**：走"产出施工分解框架"路径；**不登记 ARCH-299**（无数据/前提缺口可登记）。

## 3. 施工分解框架（剩余三步 + 校准）

| # | 施工项 | 内容 | 依赖/前置 | 验收 |
|---|---|---|---|---|
| S1 | 因子值产出接线 | event_factor_matrix 三因子接入事件驱动消费链：事件日锚定（disclosure_plan.actual_date/announce_date）→ dReport 法定截止日规则表（年报 4-30/半年报 8-31/Q1 4-30/Q3 10-31，交易所规则硬编码）→ Jump on PEAD 以事件日+5 交易日窗口取 OHLC 算 AR → 隔夜趋势逐日滚动 | disclosure_plan 读取层（event_calendar_filler 可复用）；基准收益序列 | 单测：三因子在三历史财报季样本上产出非空且符号方向符合实证（dReport 提前为正、Jump 保号、隔夜趋势负向 IC 口径归下游） |
| S2 | z-score 归一化 + event_impact_score 融合 | 截面 winsorize+zscore（归因子工厂口径），按 26 号 §2.5 公式融合 w1-w4 + PEAD_inversion_gate 门控（非加权项） | G10 权重校准（可先等权占位跑通，标注待校准） | 与 event_score 现有链路不双真源：event_impact_score 注入 BM-SEL-19 漏斗（event_funnel.py `run_event_funnel` 评分环节），复用 compute_event_score 不重复造公式 |
| S3 | sleeve/漏斗接线 | event_funnel.py 过滤层接入 event_impact_score；event_driven_sleeve_strategy 经漏斗层消费（当前 TYPE_CHECKING 声明待接线——26 号 2026-08-28 回填已登记） | S1/S2 | 端到端：事件→候选池→评分→漏斗截断链路跑通，无事件源时 skipped 直通不阻塞（既定降级） |
| S4 | G23 回测校准 | Jump 阈值 3% / 隔夜窗口 20 日 / dReport 分档映射的 A 股实证校准；PEAD Inversion 3% 阈值 A 股适配（26 号 §5 暂缓项 5 同批） | G23 回测框架 + 历史事件样本（披露季 reaction 分布） | 校准报告 + 参数终值回写 26 号 §2.4 |

**施工顺序**：S1→S2→S3 顺序依赖；S4 可与 S3 并行启动（样本准备先行）。**纪律**：权重/阈值终值须经 G23 校准回写，禁止以"跑通即定值"；dReport 法定截止日规则表改动属交易所规则变更域，单列配置不入代码常量。

## 4. 风险与边界

1. **披露数据质量**：disclosure_plan 存在 announce_date=1970-01-01 脏行（min 值实证），消费端须按 report_period/quality_flag 过滤。
2. **六因子与打板相关性**：施工前 G07 相关性实测为既有前置（26 号 §6 待定问题），若 >0.6 需重审 sleeve 组合。
3. **Jump on PEAD 的 5 日窗口 CAR 基准**：FF6 基准在 A 股的本土化口径需在 S1 落地时裁定（行业基准可降级）。
4. **远期项不进入本框架**：AStockEvent Feed / Hawkes / Janus-Q / CNN 可视化 / Data Funnel 双阶段均为 26 号 §5 既定暂缓。
