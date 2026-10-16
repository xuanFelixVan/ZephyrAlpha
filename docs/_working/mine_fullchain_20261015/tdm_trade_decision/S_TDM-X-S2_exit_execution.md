---
ttl: task_bound
doc_type: tdm_mining_note
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
skeleton_row: TDM-X-S2
flow: exit_flow
node_count: 7
session: mine-fullchain-tdm-20261015
---

# S_TDM-X-S2 离场执行（7 节点）

## 1. 定义

一句话："卖不卖"定了之后管"怎么卖"——方式路由（一次性/分批/竞价/尾盘）→T+1 与涨跌停约束→时段路由→本地条件单/分批执行→闭环复盘，把离场决策落成柜台回报并回测退出效率。

展开：S2-01 执行方式路由（紧迫度>0.8 或小仓<2%→一次性市价；中等+大仓→3 批间隔 5 分钟；不急+流动性差→尾盘集中；隔夜风险单→竞价挂跌停价逃命；卖出前三查=单笔≤买一档挂单量/日量×10% 等）；S2-02 跌停处置三步（17:30 夜市委托第一时间挂跌停价排队→封单骤减>20% 撤旧改买一重挂→次日竞价处理残余）；S2-03 时段路由（深市 14:57 后集合竞价不可撤、沪市尾盘可撤、竞价逃命单 9:15 挂）；S2-04 本地条件单（vn.py 范式：触发器存本地不预占仓位、每根 K 线收盘 cancel 重挂、OCO 双停止单）；S2-05 Exit Ladder 阶梯（+1R 减 50% 保本/+2R 再减 25%/尾仓 25% 跟踪止盈，MFE 捕获率<50%=卖太早）；S2-06 卖出闭环三率（卖飞率>30%=止损太紧/避损率/MFE 捕获率+六分类复盘）。

## 2. 六向台账

### 2.1 输入面（有证）
- 外部入边 5 条：TDM-P-P2-03→X-S2-01（做T敞口平仓）、TDM-P-P2-04→X-S2/X-S2-01（减仓指令）、TDM-F-C2-01→X-S2-01（组合净卖指令）、TDM-X-R1→X-S2（熔断全清）。
- 内部：X-S1→X-S2、X-S1-05→X-S2-01、X-S1-06→X-S2-01（双通道进单）。

### 2.2 输出面（有证）
- 出边 12 条：X-S2→TDM-X-FLOW（流根）；X-S2-06→TDM-F-C3-01（离场结果喂归因）、X-S2-06→TDM-E-L4-12（卖出质量反馈回订单预检——执行面闭环边）。
- goal 块（挂 TDM-X-FLOW）：出场效率读数（回撤保护率/假信号率）；考试卡 16 张（exit_flow/S2/）。

### 2.3 SSOT 真源（有证）
- config/trading_decision_map.yaml#TDM-X-S2（line 4435）+S2-01..06（line 4935/4986/5034/5084/5128/5170）。
- casebooks 0 挂（无翻账语义环节，图例明文不硬凑）；策略挂载经流根 STR-VREV-001（proposed）。
- 监管合规面：REG-EXA-001 执行合规 8 字段（骨架 §3 缺口 11 注记）。

### 2.4 代码模块（有证，6/6 子节点 ref 实存）
- sell_decision/core/：sell_execution_planner.py（MOD-SELL-019）、scaling_out.py（MOD-SELL-017）、sell_execution_quality_tracker.py（MOD-SELL-012）。
- position/core/t1_sellable.py（MOD-POS-028，与 P2-01 双锚共用）；ex_sor/core/sell_session_router.py（MOD-XS-016）；ex_core/local_order_queue.py（MOD-L06-001，与 L4-07 双锚共用）。
- 父枢纽 TDM-X-S2 无 ref（结构枢纽，INV-1 允许）。

### 2.5 门禁约束（有证）
- 四门同前；卖出为资金出域动作=交易核心域 high（risk_tier_registry REG-RISK-TIER-001），live 通道默认 paper（S1 宿主 mode 默认 paper 纪律同构覆盖 S2）。

### 2.6 自动化触发（有证）
- S2-01/02/03/05=intraday；S2-04=continuous（tick 驱动）；S2-06=盘后。
- 消费方实证：s1_scan_orchestrator CONSUMERS 明文"TDM-X-S2-01 路由口（f46 卷 S2-01 入口消费方）"；硬时点 17:30 夜市委托/14:57 深市撤单闸/14:50 做T强平联动。

## 3. 自审闸三态

| 向 | 态 | 打分依据 |
|---|---|---|
| 输入面 | pass | 四源入边（做T/减仓/组合/熔断）+S1 双通道 |
| 输出面 | pass | →流根+→归因+→L4 预检反馈闭环边 |
| SSOT | pass | 节点行+16 张考卡+EXA 合规面；casebooks 0 挂=图例明文 |
| 代码模块 | pass | 6/6 实存（三处双锚复用为设计性共享） |
| 门禁约束 | pass | 四门+high 风险域+paper 默认 |
| 自动化触发 | pass | intraday/continuous/盘后分档+消费方实证 |

**总评：pass（6/6）**。

## 4. 缺口与建议

1. S2-06 三率（卖飞率/避损率/MFE 捕获率）的 N 日跟踪窗口参数未成册（散文"N 日"）——建议参数册化并与 REG-VALM-001 离场反事实方法对齐。
2. 跌停处置依赖 17:30 夜市委托通道——QMT 夜市委托能力是否在所有备援通道可用未见声明（D13-07 看门狗只保终端活）——建议在执行链图议题（骨架 §3 缺口 11）中一并收口。
3. casebooks 0 挂与 P3/S2/R1/C1 同簇——若"卖出执行滑点异常"需翻账，现无章可翻；建议评估 CASEBOOK-001#alert 是否补挂 S2-06。
