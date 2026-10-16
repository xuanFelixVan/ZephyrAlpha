---
ttl: task_bound
---
# S68 FAC-E9 实盘归因（骨架行 68）

> 挖矿工程=mine_fullchain_20261015；本件=FACTORY 段子文档（E9）。所有数字为 2026-10-15 实读。

## 1. 定义

实盘归因（FAC-E9，stage，partial）：实盘每分赚亏拆开来源——影子组合工作流（实盘账本旁跑信号复刻影子组合对照，复用 C4 引擎）+IS 分解（Perold 1988：延迟/执行/机会/费用）+Brinson-Fachler（配置/选股）+Barra 式因子归因（风格/beta/alpha 分离）；归因回灌 E2 假说库完成价值链闭环（"赚亏拆开看"+“病历有人翻”）。9 节点=1 stage+8 mechanism（8 built、stage partial）。

## 2. 六向台账

| 向 | 实证（文件路径证据） |
|---|---|
| 输入面 | 图 data_refs：`c1_market.execution_report`+`c1_market.account_nav_daily`（双双在图12 待供五表清单）；decision_timestamp 字段链已落（CTR-P1-007 V2：codegen+execution_report DDL 列+producer 写入点=Order.created_at），线上表 ALTER 待 CH 迁移窗（图注施工单登记） |
| 输出面 | 归因报告落位=图 store_refs 自注"**待定（E9 施工时定）**"（key=portfolio_id+期间，retention 永久）；net_bucket_medians 等读数经 calibration_exam（E4 侧，exam_scale_cost_gate.yaml net_fee 节） |
| SSOT 真源 | `config/strategy_production_map.yaml` E9 组 9 节点；上游=TDM-F-C3 绩效归因反馈（trading_decision_map.yaml#TDM-F-C3，回流声明）；feedback_loops 第 1 条 E9→E2（RD-Agent 式闭环，**已在 edges 第 10 条落边**） |
| 代码模块 | `src/zephyr/pf_core/core/shadow_portfolio.py`（实存，Perold 四分解守恒+契约/sim 双适配器，只读零订单路径）；`scripts/backtest/condition_attribution.py`（实存）；MOD-PF-007 绩效归因（Brinson-Fachler 三因子+因子归因+风险归因复用 MOD-RK-16，图注 813 行）；`src/zephyr/reporting`（38 py：attribution.py/attribution_calculator.py/deviation_attribution_decomposer.py/default_attribution_engine.py 等 8 件归因族实存）；`src/zephyr/feedback_loop`（340 py） |
| 门禁约束 | 只读零订单路径（影子组合安全语义）；net_fee 判罚面=metrics_only 不进 judge()（裁定#506，存量卡零影响）；归因回灌 E2 为声明环（有边） |
| 自动化触发 | 日账管线与持久化表=施工单移交（图注 partial 维持）；日度拍板/结算由图13 C 段（D13-28/29/34）承接，本层无独立调度槽 |

## 3. 自审闸三态（逐向）

| 向 | 态 | 理由 |
|---|---|---|
| 输入面 | warn | 两张输入表在图12 待供清单；decision_timestamp 线上 ALTER 未迁（字段链已落、库列未落=半程） |
| 输出面 | warn | store_refs location="待定"——输出落位显式未定，交付面悬空（图自报欠账非矛盾，故 warn 不 fail） |
| SSOT 真源 | pass | 图层位+TDM-F-C3 回流声明+E9→E2 已落边（三条边证据齐） |
| 代码模块 | pass | 影子组合/条件归因/8 件归因族全实存 |
| 门禁约束 | pass | 只读路径+metrics_only 判罚面界定清晰 |
| 自动化触发 | warn | 日账管线=施工单移交未收口；本层零自有触发槽（依赖图13 C 段供事件） |

小计：3 pass / 3 warn / 0 fail。

## 4. 缺口与建议

1. 边分布：E9 仅 2 条边（E8→E9 主干+E9→E2 回流，后者是全图唯一落边的反馈环）；8 个 mechanism 零边。
2. 归因报告落位待定：E9 施工时需定 store location——建议比照 E7 用 data/backtest_artifacts/runs/（key=portfolio_id+期间），一句 store_refs 补记即可消除悬空。
3. 跨图断缝：TDM-F-C3→E9 回流为声明衔接，trading_decision_map 与本图零机械边（同 E8→C1 案）。
4. 线上表迁移窗：decision_timestamp 的 execution_report ALTER 排 CH 迁移窗执行（在册施工单），勿裸改生产表（RULE-DATA-OPS）。
