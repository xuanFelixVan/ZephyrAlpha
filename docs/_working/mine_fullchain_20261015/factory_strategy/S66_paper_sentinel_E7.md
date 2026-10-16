---
ttl: task_bound
---
# S66 FAC-E7 模拟盘前哨（骨架行 66）

> 挖矿工程=mine_fullchain_20261015；本件=FACTORY 段子文档（E7）。所有数字为 2026-10-15 实读。

## 1. 定义

模拟盘前哨（FAC-E7，stage，built）：registry 幸存者以 live 数据跑模拟盘 N 周，逐日对账预测 vs 实际（分布校准的实盘版）+滑点/容量实测；行业统计回测夸大实盘盈亏 30-60%，此门不可跳；不达标退回 E6 标 decayed；对应 lifecycle_status=sim/paper。方法论底座=机构四道门共识（R4）+QuantConnect 对账框架+IS 分解（Perold 1988）。23 节点=1 stage+22 mechanism，全部 built。

## 2. 六向台账

| 向 | 实证（文件路径证据） |
|---|---|
| 输入面 | 图 data_refs：`c1_market.realtime_snapshot`、`c1_market.execution_report`——后者在图12 五张待供表清单内（account_nav_daily/execution_report/factor_feature_value/factor_signal/reconciliation_differences，骨架 §2.5 实读转抄）→供料悬空（见三态）；行情侧由图13 D13-12 模拟盘会话拉起+D13-24 保活与成交回路供（当日运营段承接） |
| 输出面 | 前哨对账报告 `data/backtest_artifacts/runs/`（key=strategy_id+前哨批次，retention 永久，实存）；sim 台账三件输出（ledger/journal/memo） |
| SSOT 真源 | `config/strategy_production_map.yaml` E7 组 23 节点；换手上限门=`config/exam_scale_cost_gate.yaml` turnover_gate（cap_annual_x=8.0，推导注记 38.6pct/4.75年÷39x，days_basis=244） |
| 代码模块 | `scripts/backtest/sim_paper_ledger.py`、`sim_platform_journal.py`、`sim_promotion_memo.py`（实存）；league 五件=`league_judge/league_registry/league_archive/league_monthly_snapshot/league_restore.py`（实存）；`scripts/backtest/crisis_drill_monthly.py`；`src/zephyr/simulation`（23 py）、`src/zephyr/execution_simulation`（8 py，含 almgren_chriss_impact_model.py）、`src/zephyr/digital_twin`（8 py）；MOD-BT-225/083/094/199/201/222/223、MOD-SIM-002、MOD-TRADING-012、MOD-PF-008、`dir:_domain_infrastructure_runtime/strategy_canary_release` |
| 门禁约束 | E7 换手上限门 8x/年（v1 冻结块，改值=裁定通道）；"此门不可跳"（图注铁律）；不达标退回 E6 标 decayed（回退语义在册） |
| 自动化触发 | 图13 D13-12 模拟盘会话拉起+日历闸、D13-24 保活与成交回路、D13-45 做T双拍（骨架 §2.4 在册）；SIM_DAILY 事件正门（E8 图注：执行归 SIM_DAILY 事件正门） |

## 3. 自审闸三态（逐向）

| 向 | 态 | 理由 |
|---|---|---|
| 输入面 | warn | execution_report 属图12 待供五表——执行回报供料在数据链侧未闭环，前哨"逐日对账预测 vs 实际"的实账腿悬空；realtime_snapshot 供料由图13 承接（可用） |
| 输出面 | pass | 对账报告+三台账件落位实证 |
| SSOT 真源 | pass | 参数册 turnover_gate 冻结块+图层位一致 |
| 代码模块 | pass | 11 个脚本件+三包 39 py+canary 卡全实存 |
| 门禁约束 | pass | 8x/年预注册冻结+不可跳铁律+退回语义 |
| 自动化触发 | pass | 图13 三节点（D13-12/24/45）+SIM_DAILY 事件正门承接，链路在册 |

小计：5 pass / 1 warn / 0 fail。

## 4. 缺口与建议

1. 边分布：E7 仅 2 条边（E6→E7、E7→E8）；22 个 mechanism 零边。
2. 供料悬空：execution_report 写面在 `src/zephyr/ex_core/execution_report.py`+`execution_report_producer.py` 已建（实存），但数据链图12 仍将其列为待供表——建议图12 待供清单复核（写面已存在，可能是"表已建未入链"的登记滞后而非真缺口）。
3. "N 周"时长未参数化：前哨考核窗口 N 无预注册值（对比 E5 corr_threshold 已入册），建议入 exam_scale_cost_gate.yaml 或专册预注册，免临场拍脑袋（purpose_tag=新策略上岗先实习的量化判据缺一半）。
