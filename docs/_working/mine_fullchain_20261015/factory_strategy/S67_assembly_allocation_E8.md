---
ttl: task_bound
---
# S67 FAC-E8 组装与资金分配（骨架行 67）

> 挖矿工程=mine_fullchain_20261015；本件=FACTORY 段子文档（E8）。所有数字为 2026-10-15 实读。

## 1. 定义

组装与资金分配（FAC-E8，stage，partial）：多策略 sleeve 装配+资金分配与轮动——regime 切换选 sleeve+风险平价/等风险贡献+IC_IR 加权禁朴素等权+资金渐进爬坡（drawdown 控制）。"钱跟着确定性走"（purpose_tag，Owner 2026-10-03 冻结）。35 节点=1 stage+34 mechanism（33 built、1 pending、stage partial）。

## 2. 六向台账

| 向 | 实证（文件路径证据） |
|---|---|
| 输入面 | 图 data_refs：`c1_market.account_nav_daily`（在图12 待供五表清单）；上游双源=E7 前哨幸存者+图15-S12 graduated（skeleton §2.1/§2.2 衔接声明）；钱包额度读 `sim_paper_ledger` allocated_capital（图注已闭） |
| 输出面 | `c1_backtest.alloc_budget_daily`（key=trade_date+run_id+strategy_id，retention 永久；2026-09-27 st-chief4x 批：sleeve 语义落库已闭——plan/条目/相位三件套入 batch_plan_json.sleeve，读面=SQL_SLEEVE_DAY_SLICE） |
| SSOT 真源 | `config/strategy_production_map.yaml` E8 组 35 节点；`config/position_recipe_grid_schema.yaml`（dimensions 实读=**17 维**，与骨架"仓位配方 17 维"一致）；`docs/01_policies_and_standards/_registry/catalogs/portfolio_model_registry.yaml`（portfolio_models=11 实读）；MOD-PA 号段净零登记（跳号 005/008-012/016-019 永不复用，裁定#485） |
| 代码模块 | `src/zephyr/pf_alloc`（29 py）：core 四件 `forward_stop_loss/risk_budget_allocator/sector_distribution_comparator/tail_hedge_signal.py`+`rebalance_check_runner.py`（scheduler 行 320 import 实证）全实存；`src/zephyr/pf_core`（38 py）；`scripts/backtest/weight_ssot.py`；MOD-PA-002..024 族（多策略资金分配 003/regime 元分配 007 消费 MOD-REGIME-001/风险预算 022/回撤限额 013/相关性闸 004/三维筛选 014/BMA 加权 015）；MOD-PF-001/002/003/006/008；`dir:_domain_portfolio_core/` 五卡、`dir:_domain_regime/` 四卡 |
| 门禁约束 | 组合流运行时消费欠账仍归 TD 组（partial 维持=图注 2026-09-27 推进后口径）；再平衡巡检=只读+Advisory 告警，执行仍归 SIM_DAILY 事件正门（scheduler.py 行 309-313 实读：执行不让巡检代行） |
| 自动化触发 | scheduler 槽 `pf_alloc_rebalance_check`（05:45 巡检槽，`src/zephyr/data/scheduler.py` 行 314-334：总闸 `data/runtime/pf_alloc_rebalance_check.disabled` 存在=停用；run_rebalance_check 事件触发非 cron 本体） |

## 3. 自审闸三态（逐向）

| 向 | 态 | 理由 |
|---|---|---|
| 输入面 | warn | account_nav_daily 在图12 待供五表（与 E9 共用缺口）；graduated 毕业包→E8 挂图无机械边（骨架 §3.13） |
| 输出面 | pass | alloc_budget_daily.sleeve 三件套落库已闭（2026-09-27 批实证） |
| SSOT 真源 | pass | 17 维配方+11 模型册实读吻合；MOD-PA 跳号净零登记合规 |
| 代码模块 | warn | core 件族/29 py 全实存，但装配线聚合节点 FAC-E8-M-001（件族本体聚合条目）build_status=pending——件 built 而聚合账 pending，账面与实物错位 |
| 门禁约束 | pass | 只读巡检+SIM_DAILY 正门分工清晰，无越权执行 |
| 自动化触发 | pass | 05:45 槽+disabled 总闸+事件正门三层实证（scheduler.py 行号实读） |

小计：4 pass / 2 warn / 0 fail。

## 4. 缺口与建议

1. 边分布：E8 仅 2 条边（E7→E8、E8→E9）；34 个 mechanism 零边。
2. 跨图断缝：E8→TDM-F-C1（预算切分）为骨架 §2.1 声明的下游，两图（strategy_production_map/trading_decision_map）间零机械边——组合流运行时消费欠账归 TD 组（图注），与骨架 §3.13 闭环对账缺失同案。
3. M-001 聚合节点 pending：建议把件族聚合条目转 built（件全在，纯账面动作）或注明 pending 理由。
4. account_nav_daily 供料：同 E7 建议复核图12 待供清单时效性。
