---
ttl: task_bound
doc_type: tdm_mining_note
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
skeleton_row: TDM-F-C2
flow: portfolio_flow
node_count: 5
session: mine-fullchain-tdm-20261015
---

# S_TDM-F-C2 组合聚合（5 节点）

## 1. 定义

一句话：多策略并发时"每个策略各自的账"与"组合是一盘棋"在这里合流——各 sleeve 目标仓位求和轧平（对冲净额）→组合约束栈全检→相关性聚类去扎堆→输出组合净指令流。

展开：四子节点+枢纽：C2-01 目标聚合与净额轧平（intent netting 三步：收集各 sleeve 指令→同标的代数求和（买 1000+卖 600=净买 400 省 600 股手续费）→净差单下发；成交按贡献比例分摊回各 sleeve 账本否则逐笔归因做不了；批量窗口 1 分钟一拍防信号抖动）；C2-02 组合约束栈六层顺序过（总仓位上限→回撤限额→波动率目标→集中度单票 20%→流动性 3 日可退出→相关性 cluster 5%；过哪层裁哪层按非策略仓优先裁）；C2-03 相关性聚类（60 日滚动 PnL 相关矩阵→层次聚类；ρ>0.70 合并敞口/ρ>0.85 禁新仓/单 cluster≤5% 权益；月度再聚类+危机期压测）；C2-04 budget 变动三级升级（Tier1 降<10% 封锁新仓自然收敛/Tier2 10-25% 差异化窗口打板 2 日事件 3 日多因子 4 日/Tier3>25% 按比例强裁；防抖日内<5% 忽略）。

## 2. 六向台账

### 2.1 输入面（有证）
- 入边：TDM-F-C1→C2/C2-04（预算与预算变动）；TDM-X-R1→C2-01（熔断期组合收缩）。
- 隐式输入：各 sleeve 目标仓位（经 C1 分配后账本面）；PP-001 aggregator 三约束（max_total_position 1.0/max_single_sleeve 0.25/correlation_cap 0.7）为本环节约束栈的地图侧镜像真源。

### 2.2 输出面（有证）
- 出边 7 条：C2→C3（sequence）；C2-01→TDM-E-L4（组合净指令流进执行）、C2-01→TDM-X-S2-01（净卖指令进离场路由）。
- goal 块（挂 TDM-F-FLOW 流根：钱怎么分、明天怎么调）；考试卡 12 张（portfolio_flow/C2/）。

### 2.3 SSOT 真源（有证）
- config/trading_decision_map.yaml#TDM-F-C2（line 5363）+C2-01..04（line 5438/5488/5536/5579）。
- casebooks 挂 1 处（CASEBOOK 审批族域，C2-04 升级流=DCS#审批 翻账位——casebooks_legend_zh line 93"「001#审批」落 DCS#审批"实读）。
- 骨架总纲写 C2=6 节点、地图实读 5（漂移记录于 §4）。

### 2.4 代码模块（有证，4/4 子节点 ref 实存）
- position/core/firm_risk_aggregator.py（MOD-POS-021，C2-01/C2-02 双节点同锚：净额轧平与约束栈同聚合器两入口）。
- position/core/correlation_regime_monitor.py（MOD-POS-012）；position/core/budget_change_handler.py（MOD-POS-022）。
- 父枢纽 TDM-F-C2 无 ref（结构枢纽，INV-1 允许）。

### 2.5 门禁约束（有证）
- 四门同前；C2-04 三级升级含"紧急态（X-R1/RK-41）例外允许硬切"（C1-03 注记互文）——熔断期预算强制收敛路径双册互证。

### 2.6 自动化触发（有证）
- 四子节点 activation 全=continuous（组合态持续监控）；C2-01 批量窗口 1 分钟一拍=节拍事件驱动。
- 下游执行联动：净指令流→L4 条件队列/local_order_queue 横切件；月度再聚类归 C3-03 盘后批（C2-03 注记）。

## 3. 自审闸三态

| 向 | 态 | 打分依据 |
|---|---|---|
| 输入面 | pass | 预算/熔断入边+PP-001 aggregator 镜像约束 |
| 输出面 | pass | →C3+→L4/→X-S2-01 双执行口 |
| SSOT | pass | 节点行+12 张考卡+审批翻账位 |
| 代码模块 | pass | 4/4 实存（firm_risk_aggregator 双节点同锚=两入口设计） |
| 门禁约束 | pass | 四门+熔断硬切例外互文 |
| 自动化触发 | pass | continuous+1 分钟节拍+月度聚类 |

**总评：pass（6/6，附漂移注记）**。

## 4. 缺口与建议

1. 骨架总纲写 C2=6 节点、地图实读 5——建议随骨架批对齐（同族漂移 L1/L2/L3/L4）。
2. C2-01"成交按贡献比例分摊回各 sleeve 账本否则逐笔归因做不了"——分摊算法在 firm_risk_aggregator 内部，其正确性无独立验证方法学条目（REG-VALM-001 组合归因对账方法应覆盖此处）——建议在归因对账验证批显式纳入净额分摊核对。
3. correlation_cap 0.7（PP-001 aggregator）与 C2-03 ρ>0.70 合并敞口阈值数值一致但出处两处（地图 portfolio_plan vs C2-03 algo_note）——真源方向建议声明（规则数据=YAML 判向：两处均在同一 YAML 属同册，低风险，但仍建议 C2-03 注记标"同 PP-001 aggregator"防单侧改参漂移）。
