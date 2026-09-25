---
ttl: task_bound
title: F37 L0 盘前作战计划——环节册（TD-A 前半）
session: st-ailayer-fullflow-td-a
creation_token: f37-l0-plan-book-tda-20260925
date: 2026-09-25
status: mined
---

# F37 L0 盘前作战计划——环节册

> **一句话**：消费昨日归因（C3-01）/参数校准（C3-04）/宏观态（L1-AGG），产出当日作战计划（总仓位建议档/分批预案/禁做清单/应急触发线）与明日边界；**计划是输入不是第二决策点——开闸唯一裁定权在 L1**（Owner 2026-09-09 定界）。
> 节点组：TDM-E-L0（gate）+ L0-01 计划生成 / L0-02 偏离监控 / L0-03 收盘复盘明日边界 / L0-04 明日情绪盘中滚动预测，共 5 节点。总册三态标 built｜P1｜T3。

## 一、环节定义与边界

- **供料方**：F50 C3-01 昨日归因 / C3-04 参数校准；F38 L1-AGG 宏观态与六段；F33 L9-V1 大盘快照；F39 候选池；F42 持仓台账。
- **消费方**：F38-F41（总闸/板块/个股/执行均受计划约束）；作战室前端"今日交易计划"卡；L0-02 盘中偏离监控消费 L2-09-2 冲击流；次日买卖融合消费明日边界（L3-06 环境开关/L4 执行/X 离场预案约束）。
- **跨日闭环**：盘后 L0-03 生成明日边界 → 次日盘前 premarket_constraint_loader 装载回 L0（DAG 不画跨日自环，语义记此，地图 L0 algo_note 自述）。

## 二、判定输入 / 输出

| 节点 | 判定输入 | 判定输出 |
|------|---------|---------|
| L0 gate | C3-01 归因、C3-04 校准、L1-AGG 宏观态、候选池、持仓 | 总仓位建议档/分批建仓预案/sit_out_list 三源合成/应急触发线 |
| L0-01 | 候选池×持仓×立场×仓位系数；情景概率=scenario_probability_model 九格（DAL-SCEN-PROB，MOD-PLAN-017，2026-09-20 final3 P5 接线） | 逐票计划（纯函数可单测）；firm 单票 8% 硬顶恒生效，A 股整手折算，不足一手跳过+notes 留痕 |
| L0-02 | 计划 vs 盘中实际走势；偏离超阈触发 boundary_revision_engine | 当日边界修订（仅当日有效，跨日/过期消费拒发）；计划外操作记执行不一致（作战室归因） |
| L0-03 | 收盘定案（closing_session_decision）→brier 校准回填（brier_calibration） | TomorrowBoundary=箱体上沿/下沿/加仓上限/禁加仓价位/必出止盈价位/突破验证条件；**边界层坏=致命暂停操作**（MOD-PLAN-001 不变量） |
| L0-04 | 盘中 10:00/11:00/13:30/14:30 四时点盘面；昨晚 8 态转移先验（next_day_8state_forecast）+相似日推理（similar_day_inference）+Brier 连错降权（brier_calibration）；昨日先验由 L0-03 盘后落库、本节点盘中读缓存 | "明日降档预警"（建议，修订权在 L0-02）：融合最可能态悲观档比先验最可能态悲观 ≥1 档（8 态全序，蓝图 §2）；只出概率不出点位 |

## 三、判定用离散状态集合

| 状态集 | 离散值 | 真源 | 备注 |
|--------|--------|------|------|
| 次日情绪 8 态（DAL-8STATE-FCST） | 8 态转移先验+悲观档位全序 | src/zephyr/plan_engine/next_day_8state_forecast.py；蓝图 §2 | L0-03/L0-04 共用 |
| 情景九格（DAL-SCEN-PROB） | 涨/跌/震荡 × 幅度档 = 9 格概率 | MOD-PLAN-017 scenario_probability_model | Σ=1；计划生成据此定当日立场档 |
| 明日边界（非枚举，区间约束组） | TomorrowBoundary 六字段 | tomorrow_boundary_planner.py:39-42（输入=BM-SEL-03/04/05/23+卖出侧边界） | 边界层坏→致命暂停，延迟开盘到加载成功或人工介入 |
| 降档预警判据 | 悲观档差 ≥1 档（0/1 出发） | intraday_tomorrow_forecast.py 节点注 | 纯函数核零 IO，三零件产出由调用方注入 |

## 四、子模块清单与实件校验

5/5 module_ref 实测在盘（ls 校验 2026-09-25，零缺件）：daily_warroom_pipeline.py（MOD-PLAN-018，编排入口，stability=testing）/ daily_trade_plan.py / plan_deviation_monitor.py / tomorrow_boundary_planner.py（MOD-PLAN-001）/ intraday_tomorrow_forecast.py。关联件：scenario_probability_model.py、boundary_revision_engine、premarket_constraint_loader、closing_session_decision（与 L4-02 共件）。

## 五、触发链与当日闭环证据

- **dloop_post 16:45 日循环**（daily_loop_master_switch，Owner 2026-09-21 批挂特殊槽，总闸 data/runtime/daily_loop_master.disabled）：数据就绪门（fail-closed，行情缺日不出预案）→ regime 新鲜度体检 → **warroom scenario_plan 族（MOD-PLAN-018=唯一未挂事件链的棒，两段编排盘前 compute_and_record+盘后 writeback_outcome）** → 晨间预案（MOD-PLAN-030）→ 次日概率（MOD-PLAN-029）→ pf_alloc 分配。逐段 fail-open，幂等复用 prediction_log UNIQUE。
- **并列拍板体**：daily_decision_orchestrator（MOD-BT-214，experimental）由 daily_kline SUCCESS 事件链末棒唤醒（宪法 §9.3 事件触发，无 cron），S1-S7 产出 c1_backtest.decision_daily 一行=当日唯一放行凭证（无快照行=无新开仓令）；v1 首版分发=留痕+仪表盘零实盘变更（裁定#305 第 6 点）。
- **运行证据**：调度槽在 schedule.yaml:249（dloop_post）/178（nightly_sentiment）；观察/记录模式零下单。W0/W6 样本=scenario_plan+outcome 族日行落库积累（20 日窗口）。

## 六、验证欠账清单（REG-BTB 命中 6 件，全 untested）

| object_id | 对象 | 状态 | 欠什么 |
|-----------|------|------|--------|
| BT-P2-002 | L0 gate | untested，plan=None | 验收阈值未预注册——批次决策点填写并冻结前禁跑（SOP-B 护栏③） |
| BT-P2-003 | L0-01 计划生成 | untested，plan=None | 同上 |
| BT-P2-004 | L0-02 偏离监控 | untested，plan=None | 同上 |
| BT-P2-005 | L0-03 明日边界 | untested，plan=None | 同上 |
| BT-P2-006 | L0-04 盘中滚动预测 | untested，plan=None | 同上 |
| BT-P2-054 | model 批次占位 | untested | model_registry candidate→serving 的回测前置登记（逐模型 OOS 判据） |

补注：brier 校准回填的"连错降权"有运行语义但无验证对象登记；W0 校准样本窗（20 日）未满前九格概率均为 proposed 口径。

## 七、堵点与病灶

1. **L0 全族验证零开跑**（现象：6 件 backlog 全 plan=None）｜根因：阈值预注册是批次决策点前置工序，无人填｜修法：按 validation_method_registry 推导冻结（BT-P0-001/002 先例=夜班 AI 自裁授权路径）｜工作量：0.5-1 天/件｜本车道可修（走 S3 预检+冻结留痕）。
2. **两拍板体并存语义**：daily_warroom_pipeline（scenario_plan 族）与 daily_decision_orchestrator（decision_daily）并列，前者 testing 后者 experimental——两者对"今日立场档"的产出未声明谁是消费真源｜修法：在 L0 gate 注里钉死主从（orchestrator=放行凭证，warroom=计划卡+校准样本）｜0.5 天｜可修。
3. **L0-04 先验依赖 L0-03 落库链**：昨日先验缺失时四时点预测全退化——未见缺先验时的显式降级登记（消费侧 fail 语义待核）｜待核，非阻断。

## 八、三态自审

**挖干可施工**（验证欠账已逐件列明，施工=按 BT-P0 先例冻结阈值开跑 L0 族验证 + 两拍板体主从钉死）。

## 九、复核命令

```bash
sed -n '39,127p' <(python -c "解析 config/trading_decision_map.yaml L0 节点")  # 或直接读地图 L0 段
grep -n "dloop_post" src/zephyr/data/config/schedule.yaml          # 触发链
sed -n '1,60p' src/zephyr/plan_engine/daily_warroom_pipeline.py    # 编排件
grep -n "BT-P2-00[2-6]" docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml
```
