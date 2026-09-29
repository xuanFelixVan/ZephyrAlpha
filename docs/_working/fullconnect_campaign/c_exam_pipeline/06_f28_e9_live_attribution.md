---
ttl: task_bound
title: F28 E9 实盘归因（IS 分解/影子组合/回灌）——L03 接线矿道案卷
session: zc-l03-20260927
updated: 2026-09-29
---

# F28 · E9 实盘归因

> 挖矿基册=01_strategy_factory/b2_f28_e9_live_attribution.md（SF-B）。本卷=09-27 独立复核：sim 级日账绿至 09-26；IS FIELD-GAP 本日 DDL 复读维持；三缺件维持。

## 一、六向台账
| 向 | 实证锚点（09-27 实测） |
|----|------|
| 上游 | c1_market.execution_report DDL（schemas/categories/intraday/market_execution_report.py **本日复读：列族=order/symbol/execution_start/execution_end/ingest_ts（:91-97），无 decision_timestamp——FIELD-GAP 维持实锤**）（已过时，见刷新批注——decision_timestamp V2 契约扩展已落地）；c1_market.account_nav_daily；sim 级=c1_backtest.sim_pocket_daily/sim_trade_log |
| 下游 | c1_backtest.sim_attribution_daily 归因长表；D_REPORTING attribution_calculator；D_GOV_ENFORCEMENT 降级审计；MOD-PF-001 PC-01（激活度未核维持，跨组对账面）；回灌 E2 **无实件维持** |
| 自动触发 | attribution_daily=SIM_DAILY_KINDS FIFO 次段（:139 实证）；**marker 09-26T00:42:49（last_audit 实读）——sim 级日更绿至 09-26**；实盘级无（等 M7 Owner 门位） |
| 真源注册表 | 图 FAC-E9 partial；MOD-PF-007 performance_attribution_engine（excess=allocation+selection+interaction 守恒）；MOD-BT-215 sim_attribution_report（四段答案，成本铁律逐字 import）；TDM 17_f50 卷交叉：**C3 与 E9 共享 Brinson 引擎禁双算**+归因引擎自证验证欠账（portfolio_attribution 残差<1bp 对账未跑） |
| 门禁质量尺 | pnl 恒等式对平；ReplacingMergeTree 幂等回放；AttributionDataIncompleteError fail-closed；降级只建议不改权（OCP）；拥挤阈值复用 MOD-PA-004 |
| 运行状态 | **sim 级绿、实盘级红（数据缺位）维持**。attribution_daily 09-26 marker 在案；62 天存量回放口径维持；实盘账本在 M7 Owner 门后（本组零触维持） |

## 二、子模块三级枚举
1. **代码面**：src/zephyr/pf_core/core/performance_attribution_engine.py（MOD-PF-007，702 行）；scripts/backtest/sim_attribution_report.py（run_daily+--replay）；src/zephyr/reporting/attribution_calculator.py；src/zephyr/risk/core/performance_attribution_degradation.py。**IS 分解件/影子组合工作流/回灌 E2 接线三缺维持**（全仓 grep 维持基册结论；promotion_advisory.py 工作树在改属 F74 域与归因无涉）。
2. **注册表/文档面**：FAC-E9 节点 partial；execution_report DDL 头注（真源=shared/contracts/execution_report.py codegen frozen，SSoT=cross_layer_contracts.yaml——**即 FIELD-GAP 修复须走契约+DDL 双改+M7 产出侧回填，架构数据裁定路径**）；schemas verify_schema_truth 复跑判据在头注。
3. **数据面**：sim_attribution_daily 长表（marker 09-26）；runs/ 归因档案（SCR 系）；execution_report 实表数据到达率未核维持（M1/M7 域）。

## 三、接线四态独立复核
- 总册 partial → **维持 partial**，无态变。
- **骨架勘误**：无新勘误；基册 FIELD-GAP 判定本日 DDL 复读**维持成立**（L02 P0 交叉一致）。补充锚点精度：基册引":52-97 列族"，本日复读时间戳族集中在 :91-97（execution_start/execution_end/ingest_ts），无决策列。
- TDM 交叉增量：C3（F50）与 E9 同引擎禁双算+归因引擎自身验证欠账两条，总册 F50 行未见记载——归 TDM 域勘误，本卷登记转呈。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | IS 分解 FIELD-GAP（无决策时间戳） | DDL :91-97 复读 | schema 契约+DDL 增列走裁定+M7 回填规则；M 级；非本车道可修 | **P0** |
| 2 | 影子组合工作流未建 | 全仓无实件 | 前置=M7 合规门 Owner 报送（绝对前置禁自动施工）；届时最小件=C4 引擎复刻对照 | P0（门位后） |
| 3 | 回灌 E2 环断（FL1 无实件） | grep hypothesis_precheck 消费=空 | decay_cause 回写 E6 台账+假说先验标签，与 FL2 同案立项；S-M | P1 |
| 4 | 归因引擎自证验证欠账 | TDM 17_f50 卷堵点 5 | portfolio_attribution 残差对账补跑（TDM 域） | P1 |
| 5 | 风险贡献占位 1/N | detail 占位标记 | 挂 M-11 登记不施工 | P2 |

## 五、自审闸三态
**挖干（复核维持）**。FIELD-GAP 实锤复读；sim 级日账连续性本日再证（09-26 marker）；三缺件定性不变；实盘级红线维持零触。

## 六、复跑命令
```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
sed -n '85,100p' schemas/categories/intraday/market_execution_report.py   # 无 decision_timestamp
cat .runtime/strategy_pipeline/last_audit.json | tr ',' '\n' | grep attribution
grep -rn "hypothesis_precheck" src/zephyr/pf_core src/zephyr/reporting --include="*.py" | wc -l  # 0=回灌断
python -m pytest tests/pf_core/test_performance_attribution_engine.py -q
```

## 七、刷新批注（2026-09-29 st-finaldel-fresha）

### 9/28 后变更
- `a349ddc1fe`（09-28 E8/E9袋复活·21 件，同 F27 批）：**F28 影子组合对照+IS 决策时间戳链**——src/zephyr/pf_core/core/shadow_portfolio.py（389 行新件）+algo_flow/shadow_portfolio.yaml+tests/pf_core/test_shadow_portfolio.py（200 行）；schemas/categories/intraday/market_execution_report.py（+23）+src/zephyr/ex_core/execution_report.py（+1）+execution_report_producer.py（+10）+tests/ex_core/test_execution_report_decision_timestamp.py（154 行）。
- `7c3da698df0`（09-29 DEFECT-1 治愈·75 红根因）：decision_timestamp 契约三件收口。
- HEAD 复读：DDL :46/:103 `decision_timestamp DateTime64(3,'UTC') NULL` 在码（=Order.created_at 决策时刻；NULL=上游未布点；DDL 头 :129-134 有线上表 ALTER 前显式列清单护栏注记）。

### 缺口清单状态修订
- 缺口 1（IS 分解 FIELD-GAP）：**翻面**——schema 契约+DDL 双改已落（V2 契约扩展 2026-09-27 起）；M7 产出侧实数据回填状态未核（历史行 NULL 属设计允许）。
- 缺口 2（影子组合工作流未建）：**最小件已翻面**——shadow_portfolio 389 行+C4 引擎复刻对照形态落地（a349ddc1fe）；实盘前置=M7 合规门 Owner 报送维持（报送面 broker_ack 已回填 true×6，见 F62 卷批注）。
- 缺口 3（回灌 E2 环断）／4（归因自证对账）／5（1/N 占位）：未见施工证据，维持。

### 自审闸三态
- **挖干（维持）**；§一"FIELD-GAP 维持实锤"与 §四缺口 1/2 两大 P0 断言**已过时**（双 P0 均有施工落地，见上）——三缺件中两件翻面，实盘级红线维持零触。
