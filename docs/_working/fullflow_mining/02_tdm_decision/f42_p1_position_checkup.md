---
ttl: task_bound
title: F42 P1 持仓体检——环节册（TD-A 前半）
session: st-ailayer-fullflow-td-a
creation_token: f42-p1-checkup-book-tda-20260925
date: 2026-09-25
status: mined
---

# F42 P1 持仓体检——环节册

> **一句话**：持仓流首环——六子环节（对账快照/分级监控/逻辑存活/风险否决/组合级/结论汇总）盘前并行跑一遍+盘中持续，输出每只持仓的当日动作清单；单票看对错，组合看结构。
> 节点组：TDM-P-P1 + 01~06，共 7 节点。总册三态标 built｜P1｜T6。

## 一、环节定义与边界

- **供料方**：F57 结算对账（盘后四步对账先行，P1 盘前对账消费其产物）；QMT 桥持仓文件（Stock.csv）；L1 六段（板块退潮判据）、F39 板块生命周期。
- **消费方**：F43 P2 做T（资格门——被 P1-04 冻结）、F44 P3 加仓（资格门）；X 流 S1（失效仓转离场评估——thesis_survival 节点注"[CONSUMERS] X 流离场评估（失效→转离场评估，待接线）"）；P2-04 减仓指令（组合漂移越带下发）；作战室前端。

## 二、判定输入 / 输出

| 子环节 | 判定输入 | 判定输出 |
|--------|---------|---------|
| 01 对账与台账快照 | QMT 桥 Stock.csv vs 本地 strategy_book 逐笔 | 富台账：代码/股数/成本/归属策略/开仓日/状态机态；**不平账标红人工核对** |
| 02 分级与监控频率 | 盈亏态+ATR 距止损距离 | WATCH（距止损<1.5×ATR 或浮亏>3%，秒级盯）/MONITOR（±3% 内，5 分钟）/HOLD（深度浮盈>3×ATR，事件驱动）；ATR 缺失降级 MONITOR（最保守）；**已破止损线直接判 WATCH（rpt_e05 2026-09-18 修正：旧码 abs 对称化曾误判 MONITOR）**；threshold_delta ≤0.10 |
| 03 买入逻辑存活 | 四类 thesis 逐仓回查：打板查情绪梯队/多因子查因子暴露漂移/事件查衰减（利好兑现没）/做T查趋势 | 三态：ALIVE/WEAKENED/DEAD；**DEAD=转离场评估（X 流信号）；证据缺失(None)→WEAKENED 不武断判死；DEAD 只来自明确证伪**（梯队断/漂移超阈/兑现超阈/趋势破）；阈值 config 注入=proposed |
| 04 风险否决体检 | 节点判据四类：生死线（-7% 破位）/时间止损（盈利仓 5 日不涨/亏损仓 3 日不回）/事件禁区（财报前 1 日、解禁前 3 日）/板块退潮 | 触发任一=标记转 X 流离场+**冻结做T/加仓资格**；码面 StopLossTriggerType 7 种+Severity 4 态+亏损限额三级（见状态集表）——判据与码面为并集非一一对应 |
| 05 组合级体检 | 组合权重 | 三查：单票>20% 总仓（超集中）/实际权重偏离目标>25%（漂移越带→下发 P2-04 减仓指令）/同题材>3 只（扎堆） |
| 06 结论与动作清单 | 五路体检汇总（对账/分级/逻辑/风险/组合） | 每持仓一条当日动作（维持/可做T/可加仓/减仓/转离场）；**过裁决中心（position_adjudication_center）+落审计；任一子项异常=该持仓置"人工确认"默认态** |

## 三、判定用离散状态集合

| 状态集 | 离散值 | 真源 file:line | 判据-码面差异 |
|--------|--------|---------------|--------------|
| 持仓状态机 | 码面 **7 态**：NONE/BUILDING（含灰度 4 阶段）/ACTIVE/OBSERVING/REDUCING/EXITING/CLOSED（进冷却） | position_state_machine.py:91-100 | 节点散文写"六态"（不含 NONE）；OBSERVING 三因：SOFT_STOP/ABNORMAL_OPEN/PLUNGE（:103-108）；GraduationStage 灰度 5%→20%→50%→100% 满仓转 ACTIVE（:111-118） |
| 分级三档 | WATCH/MONITOR/HOLD；倍数 1.5×/3.0×ATR | position_triage.py:62-64 | 一致（rpt_e05 修正已回填注） |
| 逻辑存活三态 | ALIVE/WEAKENED/DEAD；ThesisType 四类 | thesis_survival.py:46-59 | 一致；fail 语义=缺证据不判死 |
| 止损触发类型 | 码面 **7 种**：FIXED_PCT（-7%）/SUPPORT_BREAK/LOGIC_INVALIDATION/AUCTION_DISAPPOINT（竞价不及预期）/INTRADAY_BREAK（分时破位）/SECTOR_EBB（板块退潮）+LOSS_LIMIT | ashare_stop_loss_engine.py:86-95 | 节点判据四类（生死线/时间止损/事件禁区/板块退潮）中"时间止损/事件禁区"未见码面对应枚举——码面多出 SUPPORT_BREAK/AUCTION_DISAPPOINT/INTRADAY_BREAK |
| 止损严重级 | NONE/WARNING 软止损/CRITICAL 硬止损/EMERGENCY（Kill Switch 联动） | ashare_stop_loss_engine.py:98-105 | 一致 |
| 亏损限额三级 | 日亏-2%→停盘 1 天/周亏-5%→2 天/月亏-10%→3 天 | ashare_stop_loss_engine.py:107-115 | 一致（INV-003） |
| 裁决意图四态 | OPEN/ADD/REDUCE/EXIT（四层裁决语义对齐 MOD-POS-010） | position_adjudication_center.py:80-86 | 节点散文"五动作+人工确认默认态"——IntendedAction 只 OPEN/ADD/REDUCE/EXIT 四意图；"维持/人工确认"承载层未见码面枚举 |

## 四、子模块清单与实件校验

6/6 module_ref 在盘（零缺件）：position_state_machine.py / position_triage.py（IND-VOL-001）/ thesis_survival.py（MOD-PLAN-024）/ ashare_stop_loss_engine.py / position_drift_monitor.py / position_adjudication_center.py。关联：sell_decision 族（P1-02 归 sell_decision 域而非 position 域——跨域挂载正常）。

## 五、触发链与当日闭环证据

- 节点判据：盘前并行跑一遍+盘中持续（01/03/04/06 盘前；02/05 continuous）。
- **已证接线（P1-06 裁决中心）**：pf_alloc/allocation_orchestrator.py（MOD-PA-007 五模块链 G15→G14 装配体，挖矿 PFA-1 判"链从未被组装"的治本件）消费 PositionAdjudicationCenter——链路 regime → RegimeMetaAllocator → BudgetChangeHandler → StrategyBook → AdjudicationCenter（allocation_orchestrator.py:9-18,117-122,539,919）；该装配体在 dloop_post 的 pf_alloc 分配棒内运转，下游=sim_paper_ledger 纸面盘日账（AutoRuntime 事件链）。**裁决中心有真消费方，但走的是分配语义（OPEN/ADD/REDUCE/EXIT 意图裁决），不是"盘前五路体检汇总"语义。**
- **触发挂点证据缺口（其余五件）**：dloop_post 日循环棒清单与 daily_decision_orchestrator S1-S7 均无 P1 体检棒；position_state_machine 对账/position_triage 分级/thesis_survival 存活/ashare_stop_loss 否决/position_drift 组合体检五件的日循环编排入口零命中（grep 实证 2026-09-25）——"盘前并行跑一遍"无排程证据，与 M5"order_daemon 建成未接线"同型。
- 对账上游：F57 盘后四步对账（built P0）先行，P1 盘前对账消费其台账——两段衔接的排程证据同样待核。

## 六、验证欠账清单（命中 7 件，全 untested——P1 全族零验证运行）

| object_id | 对象 | 状态 |
|-----------|------|------|
| BT-P3-004 | P1 枢纽 | untested，testable=False |
| BT-P3-007 | 对账快照 | untested，plan=None（阈值未预注册禁跑） |
| BT-P3-008 | 分级监控 | untested，plan=None |
| BT-P3-009 | 逻辑存活 | untested，plan=None |
| BT-P3-010 | 风险否决 | untested，plan=None |
| BT-P3-011 | 组合级 | untested，plan=None |
| BT-P3-012 | 结论裁决 | untested，plan=None |

补注：P1 属 position_flow，backlog 批次前缀 P3=低优先登记；但 P1-04 止损引擎同时被 F59（risk_limit 家族，M7 P0）消费——验证优先级登记与实际风险权重不匹配，建议提升。

## 七、堵点与病灶

1. **盘前体检五件编排入口悬空（本环节头号病灶）**：P1-06 裁决中心已经 pf_alloc 装配体接入日循环（分配语义），但体检五件（对账/分级/存活/否决/组合）无任何排程证据证明每天真的跑——"体检结论喂裁决"的体检侧半环悬空｜修法：a) 考古 sim_paper_ledger/AutoRuntime 事件链是否隐式驱动（0.5 天）b) 无则立施工单：P1 体检棒挂 dloop 链（1-2 天）。
2. **X 流转离场评估待接线**（thesis_survival 节点注自认"待接线"）：DEAD 判定产出了但离场评估消费链未闭合——体检结论停在"标记"｜修法：X 流 S1 输入接线（TD-B 组 F45 交界，移交）。
3. **判据-码面差异两处**：P1-04"时间止损/事件禁区"vs 码面 7 触发类型；P1-06"五动作+人工确认"vs IntendedAction 四意图｜修法：S4 场景对齐（改注或补枚举，各 0.5 天）。
4. **P3 批次优先级与风险权重错配**：止损引擎验证登记为 P3 低优先｜修法：提级申请（晨报列 Owner 清单）。

## 八、三态自审

**待挖（窄口）**：状态机血肉与验证欠账已挖干，但**运行证据缺最后一向**——六件的日循环编排入口未取证（谁调、何时调、跑没跑），按挖干判据"每向有实证"标准本册在触发链向欠 P1 棒证据；补证后即可翻挖干可施工。

## 九、复核命令

```bash
sed -n '91,118p' src/zephyr/position/core/position_state_machine.py   # 7 态+灰度
sed -n '86,115p' src/zephyr/risk/core/ashare_stop_loss_engine.py     # 触发类型/严重级/限额
sed -n '80,86p' src/zephyr/position/core/position_adjudication_center.py  # 四意图
grep -rn "position_triage\|thesis_survival\|position_drift" src/zephyr/plan_engine/daily_loop_master_switch.py src/zephyr/strategy_pipeline/pipeline_events.py  # 堵点1（预期零命中）
grep -n "AdjudicationCenter" src/zephyr/pf_alloc/allocation_orchestrator.py | head -4  # 已证接线
grep -n "待接线" src/zephyr/plan_engine/thesis_survival.py            # 堵点2 自认注
```
