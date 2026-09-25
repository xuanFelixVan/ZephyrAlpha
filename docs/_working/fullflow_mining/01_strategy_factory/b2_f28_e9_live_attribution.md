---
ttl: task_bound
session: st-ailayer-fullflow-sf-b
title: F28 E9 实盘归因——六向台账与三态结论（SF-B 后半）
date: 2026-09-25
status: mined
---

# F28 · E9 实盘归因

> 组 SF·策略工厂供给链 B 后半册 6/7。上游=实盘账本（execution_report/account_nav_daily），下游 F50/E2 回灌（feedback_loops：FAC-E9→FAC-E2）。
> 环节真源：config/strategy_production_map.yaml FAC-E9（build_status: partial 非 built——IS 分解时间戳 FIELD-GAP 未落+影子组合工作流未建）。

## 一、环节定义与边界

一句话：实盘赚/亏的钱来自哪里——影子组合对照（实盘旁跑信号复刻，可复用 C4 引擎）+IS 分解（Perold 1988：延迟/执行/机会/费用）+Brinson-Fachler（配置/选股/交互）+Barra 式因子归因；归因回灌 E2 假说库完成价值链闭环。
边界：引擎层（MOD-PF-007）built；**sim 级归因日账已日更投产**；实盘级归因=缺数据面（依赖 M7，绝对禁触真实交易——本组零触）+两差件。

## 二、六向台账

| 向 | 实证 |
|----|------|
| 上游输入 | ①实盘面：c1_market.execution_report（DDL 真源=schemas/categories/intraday/market_execution_report.py，**实测无决策时间戳列**——IS 分解 FIELD-GAP 证实，:52-97 列族只有 order/symbol/ingest_ts 族）、c1_market.account_nav_daily；②sim 级：c1_backtest.sim_pocket_daily/sim_trade_log（钱包链键=(strategy_id,mode)） |
| 下游消费 | ①c1_backtest.sim_attribution_daily 归因长表（DDL=schemas/categories/sim_attribution_daily.py）；②D_REPORTING（attribution_calculator）报告路由；③D_GOV_ENFORCEMENT 降级检测审计；④MOD-PF-001 PC-01 策略引擎消费降级/拥挤建议（消费侧登记，PC-01 实件激活度未核——归 TD/TDM 组对账）；⑤回灌 E2：**无实件**（feedback_loops 声明性，全仓无 attribution→hypothesis_precheck 消费者） |
| 自动化触发 | sim 级已投产：attribution_daily=SIM_DAILY_KINDS FIFO 末位（pipeline_events.py:147，deps=sim 账本当日行，无行=执行体抛错进 attempts），执行体=sim_attribution_report.py run_daily（900s 有界），marker 实测 2026-09-24T00:43:09；实盘级：无（等实盘账本） |
| 真源与注册表 | 图节点 FAC-E9；MOD-PF-007 performance_attribution_engine（src/zephyr/pf_core/core/performance_attribution_engine.py，excess=allocation+selection+interaction 守恒不变量）；MOD-BT-215 sim_attribution_report（WO-1 四段答案：策略分解/成本/基准超额 000852 主+000300 次/风险贡献）；成本口径铁律=逐字 import sim_paper_ledger BUY/SELL 常量（差>0.01 元 fail-closed 上报） |
| 门禁与质量尺 | pnl 恒等式 pnl_gross=pnl_net+pnl_cost 对平；ReplacingMergeTree 同键新 ingest_ts 回放幂等；归因引擎守恒不变量+AttributionDataIncompleteError fail-closed；降级检测只标记建议不改权重（OCP 契约）；拥挤 ρ>0.8 减半/>0.9 归零复用 MOD-PA-004 阈值 |
| 当前运行状态 | **sim 级绿、实盘级红（数据缺位）**。证据：①attribution_daily marker 09-24 在案；②62 天存量全量回放+对账=--replay 交付口径（sim_attribution_report.py 头注）；③实盘级零运行=实盘账本本身在 M7 Owner 门位后（合规门零注入未解），非本组可动 |

## 三、子模块清单

| 模块 | 是什么 | 入口 | 状态 |
|------|--------|------|------|
| MOD-PF-007 performance_attribution_engine | Brinson-Fachler 三因子+因子归因+风险归因（复用 MOD-RK-16）+降级/拥挤检测 | src/zephyr/pf_core/core/performance_attribution_engine.py | built（maturity=production；tests/pf_core/test_performance_attribution_engine.py） |
| MOD-BT-215 sim_attribution_report | sim 级四段归因日账（WO-1） | scripts/backtest/sim_attribution_report.py | built（日链已接，09-24 marker） |
| attribution_calculator | D_REPORTING 归因计算面 | src/zephyr/reporting/attribution_calculator.py | built（报告域，M6 册收编面） |
| performance_attribution_degradation | 降级检测审计面 | src/zephyr/risk/core/performance_attribution_degradation.py | built |
| **IS 分解件** | Perold 延迟/执行/机会/费用四分解 | **无**——前置字段 decision_timestamp 在 execution_report DDL 缺位 | **缺（FIELD-GAP 证实）** |
| **影子组合工作流** | 实盘账本旁信号复刻对照 | **无** | **缺** |
| **回灌 E2 接线** | attribution 结论→假说库先验 | **无** | **缺** |

## 四、堵点与病灶

1. **IS 分解 FIELD-GAP**（现象/根因=schema 列族无决策时间戳，Perold 四分解无锚点；修法=execution_report DDL 增列+M7 产出侧回填规则，属 schema 变更=架构数据走裁定；工作量=M；本车道不可修=产出侧在 M7/ex_core 域）。
2. **影子组合依赖实盘在跑**（根因=M7 合规门 Owner 报送未完成；修法=等 Owner 门位，届时最小件=C4 引擎复刻信号对照实盘 NAV，口径复用 sim_attribution 成本铁律；工作量=M；不可自动施工=Owner 门位）。
3. **回灌环断**（现象=feedback_loops 两行均无实件；修法=E9 归因结论落 decay_cause 枚举回写 E6 衰减台账+假说库先验标签，与 E6 反馈环合并立项；工作量=S-M；可修=是但建议与 E6 反馈环同案）。
4. **风险贡献占位**：sim 归因 risk_contrib 单策略期=1.0、多策略期占位 1/N（占位标记入 detail）——波动贡献升级挂 M-11，登记不施工。

## 五、提速与合并机会

- attribution_daily 与 sim_observe/sim_journal 同 FIFO 班次（已合并，正例）。
- IS 分解四项中"费用"半件已被 sim_attribution 成本段覆盖（pnl_cost），实盘件施工时可直接映射，勿重算。

## 六、自审闸三态

**挖干**。引擎与 sim 级日账全实证；三项缺件定性完成+施工前置齐（§B-E9 六项）；实盘级红线=M7 Owner 门位，本组零触。partial 判定维持，差件清单齐。

## 七、复核命令（10 分钟）

```bash
sed -n '50,100p' schemas/categories/intraday/market_execution_report.py   # 无决策时间戳列=FIELD-GAP
grep -n "ATTRIBUTION_DAILY" src/zephyr/strategy_pipeline/pipeline_events.py | head -4
cat .runtime/strategy_pipeline/last_audit.json | tr ',' '\n' | grep attribution  # 09-24 marker
sed -n '1,45p' scripts/backtest/sim_attribution_report.py                  # 四段+成本铁律
grep -rn "hypothesis_precheck" src/zephyr/pf_core src/zephyr/reporting --include="*.py"  # 回灌环=空
```
