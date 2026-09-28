---
ttl: task_bound
title: F37 L0 盘前作战计划——全流通挖干案卷（矿道 L05）
session: zc-l05-20260927
creation_token: fc-f37-l0-plan-20260927
---

# F37 L0 盘前作战计划——挖干案卷

> 一句话：消费昨日归因（C3-01/C3-04）+宏观态（L1-AGG），产出当日作战计划与明日边界；**计划是输入不是第二决策点——开闸唯一裁定权在 L1**。节点组=TDM-E-L0 gate+L0-01..04 共 5 节点（今日 yaml:129-265 机数=5，零漂移）。总册三态 built｜P1｜T3；上游 F33/F50，下游 F38-F41。

## 一、六向台账（实证锚点）

| 向 | 内容（锚点） |
|---|---|
| ①上游输入 | C3-01 归因/C3-04 校准/F33 L9-V1 快照/候选池/持仓台账（册引 f37 册 §一，2026-09-25）；L1-AGG 宏观态（yaml E-L1-AGG :511） |
| ②数据原料 | scenario_plan 族日行（prediction_log UNIQUE 幂等复用）、closing_session_decision、8 态转移先验落库缓存（册引 f37 册 §二） |
| ③状态输出 | 总仓位建议档/分批预案/sit_out_list/应急触发线；TomorrowBoundary 六字段（tomorrow_boundary_planner.py:39-42，册引）；边界层坏=致命暂停操作（MOD-PLAN-001 不变量） |
| ④下游消费 | F38-F41 全链受计划约束；作战室"今日交易计划"卡；L0-02 消费 L2-09-2 冲击流（册引 f37 册 §一） |
| ⑤自动化触发 | dloop_post 16:45 日循环（schedule.yaml:249 今日实锚）+nightly_sentiment（:178 册引）；daily_warroom_pipeline=唯一未挂事件链的棒（两段编排盘前 compute_and_record+盘后 writeback_outcome，册引）；并列拍板体 daily_decision_orchestrator 由 daily_kline SUCCESS 事件链末棒唤醒（宪法 §9.3 无 cron，册引） |
| ⑥缺口债 | 6 件验证 backlog 全 plan=None（BT-P2-002..006+054，册引 f37 册 §六）；两拍板体主从未钉死；L0-04 先验缺 L0-03 落库时降级语义待核 |

## 二、子模块三级枚举（2026-09-27 实扫）

- 域 `src/zephyr/plan_engine/`：37 件 .py（实扫）。
  - 编排/循环层：daily_warroom_pipeline.py（L0 gate 锚，yaml:145）、daily_loop_master_switch.py、premarket_workflow.py、premarket_workflow_engine.py。
  - 节点件（TDM module_ref 全 5/5 在盘，今日 sed 实锚）：daily_trade_plan.py（L0-01，yaml:170）、plan_deviation_monitor.py（L0-02，yaml:194）、tomorrow_boundary_planner.py（L0-03，yaml:219）、intraday_tomorrow_forecast.py（L0-04）+daily_warroom_pipeline.py（gate）。
  - 关联件：scenario_probability_model.py（MOD-PLAN-017）、brier_calibration.py、next_day_forecaster.py、similar_day_evaluator.py、sit_out_list.py、closing_session_decision.py（与 L4-02 共件）、boundary_revision_engine.py、premarket_constraint_loader.py、overnight_boundary_reviser.py、judgment_ledger.py/judgment_settler.py、thesis_survival.py（P1-03 跨域挂载锚，yaml:2720）等。
  - 枚举外延件（册未逐一列）：auction_hit_recorder.py、batch_boundary_runner.py、close_verifier.py、evidence_chain_decision.py、execution_deviation_attributor.py、intraday_l1_tracker.py、llm_premarket_analysis.py、scenario_*（attribution_stats/classifier/plan_recorder/planner/playbook）、track_fusion.py、trading_analyst_agents.py、trading_debate.py——共 37 件与册引"4 件+关联件"口径兼容，册面"等 4 件"为节点锚口径非全目录口径。

## 三、接线四态独立复核（2026-09-27）

| 件 | 四态判定 | 独立证据 |
|---|---|---|
| L0 gate+L0-01..04 五节点 | **编排接线（半）**：模块全在盘+日循环槽在，但 warroom 棒"未挂事件链"与 orchestrator 并列双拍板 | schedule.yaml:249 dloop_post 实锚；双拍板体并存=册引 f37 册 §五/§七-2 |
| L0-03→次日 L0 跨日自环 | **接线（声明态）** | premarket_constraint_loader 装载回 L0（册引，地图 L0 algo_note 自述） |
| L0-04 盘中四时点挂点 | **存疑** | L02 SKEL I 块判"挂点缺位（audit 覆盖未接电）"与 f37 册"三零件产出由调用方注入"并读=调用方接线未见实证 |
| 验证面 | **零开跑** | BT-P2-002..006 全 untested plan=None（册引） |

**骨架勘误**：无（总册 built 判与实证一致；但"built"未含 warroom 棒事件链缺口与验证零开跑两处保留意见，见缺口清单）。

## 四、缺口清单（处置+优先级）

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| G37-1 | L0 族 6 件验证全 plan=None | 按 BT-P0-001 先例批量冻结阈值开跑（S3 预检+冻结留痕），0.5-1 天/件 | P1 |
| G37-2 | 双拍板体主从未声明 | L0 gate 注钉死：orchestrator=放行凭证（decision_daily），warroom=计划卡+校准样本 | P1 |
| G37-3 | L0-04 缺先验降级语义待核+盘中四时点挂点缺位（L02 SKEL D7） | 考古 sim_paper_ledger/AutoRuntime 事件链；缺则挂点施工 | P2 |
| G37-4 | W0 校准样本窗 20 日未满前九格概率=proposed 口径 | 随 dloop 样本积累自然到期复核 | P2 |

## 五、自审闸三态

**挖干可施工**（节点锚 5/5 今日实锚在盘；六向有实证；缺口有修法；两处保留意见已列 P1/P2，不阻施工）。

### 待裁
- 双拍板体谁是"今日立场档"消费真源：本卷按册引建议钉主从，最终措辞归 D 裁定（S4 场景）。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"
grep -c "node_id: TDM-E-L0" config/trading_decision_map.yaml            # =5
sed -n '145p;170p;194p;219p' config/trading_decision_map.yaml           # 4 节点 module_ref
grep -n "dloop_post" src/zephyr/data/config/schedule.yaml               # :249
ls src/zephyr/plan_engine/*.py | wc -l                                  # =38 含 __init__（37 件非 init）
grep -n "BT-P2-00[2-6]" docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml
```
