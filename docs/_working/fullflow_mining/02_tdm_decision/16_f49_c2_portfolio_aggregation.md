---
ttl: task_bound
title: F49 C2 组合聚合——TDM 组合流 C2 环节册（TD-B 后半）
session: st-ailayer-fullflow-td-b
date: 2026-09-25
status: mined
group: TD-B（F43-F52）
---

# F49 C2 组合聚合（TDM-F-C2 + C2-01..04）

> **一句话**：多策略并发时'每个策略各自的账'与'组合是一盘棋'在这里合流：净额轧平→约束栈→相关性聚类→budget 三级升级。
> **上游**：F-C1（sequence+feed）、全图 sleeve 目标仓位（隐式订阅，M-12 数据轴承载）。**下游**：F-C3 归因、E-L4/X-S2 下发净指令。

## 一、环节定义与边界
- 四节点：C2-01 净额轧平（aggregation）→C2-02 约束栈→C2-03 相关性聚类（feed 回 C2-02）→C2-04 budget 三级（C1 feed 回 C2-01）；C2-01 出边直发 E-L4（state）。
- 纯指令型声明（外审 M-59）：不触碰下单接口，一切下单经 E-L4/X-S2 paper 节点。

## 二、状态机血肉
| 节点 | 判定轴 | 离散状态/规则 |
|------|--------|--------------|
| C2-01 目标聚合与净额轧平 | intent netting 三步 | 收集各 sleeve 指令→同标的代数求和（买 1000+卖 600=净买 400）→净差单下发；成交按贡献比例分摊回账本（逐笔归因前提）；发单前价格交叉闸门（Cancel Newest 防跨策略自成交）；net<0 仅可减不可做空。D85 运行时五件：1min 批量窗（风险事件走即时通道）/intent TTL≤信号半衰期（短线 1-3 bar）/re-netting 循环（residual<0.5% NAV 不补、同 parent≤2 次）/强平插队三语义（先撤全挂单；kill switch 三态 ACTIVE/HALTED 禁新放平/REDUCING 只减不加）/exit 绕过削减闸但过价格保护（risk-reduction lane>normal lane）。做T 双腿配对 ID 穿透（D97）；sleeve 离线三态 D96=冻结最后目标；sleeve 冻结=作废全部未过期 intent+撤挂单（M-23） |
| C2-02 组合约束栈 | 六层顺序（D76 定稿） | 总仓位上限→回撤限额（资金曲线分级压缩 MOD-POS-007）→波动率目标→集中度（单票 20%）→流动性（3 日可退出）→相关性（cluster 5%）；过哪层裁哪层，非策略仓优先裁；D85 下发前资金校验：本地三态模拟账本镜像券商（可用/可取/冻结；当日可调出=min{调拨,期初}；9:20-9:25/14:57-15:00 不可撤窗）；**先卖后买**排序；买入额度=期初可用+当日计划卖回款−在途买单冻结−预扣费（D101：以成交回报为准释放防透支）；额度不足只削买入不削卖出；停牌/锁死仓单列不计入强裁基数（M-28） |
| C2-03 相关性聚类 | 三档+危机压测 | 60 日滚动 PnL 相关→层次聚类（Ledoit-Wolf 收缩 MOD-POS-011）→ρ>0.70 cluster 内减半/ρ>0.85 禁新仓/单 cluster≤5% 权益；月度再聚类+危机压测 ρ→0.9 |
| C2-04 budget 三级升级 | Tier1/2/3+防抖 | Tier1 降<10%=封锁新仓（撤买单留卖单）自然收敛；Tier2 10-25%=差异化窗口自主收敛（打板 2 日/事件 3 日/多因子 4 日，窗内加仓冻结 m-20）；Tier3 >25%=按比例强裁（基数=可卖口径 M-28）；防抖：日内<5% 忽略/连降>10% 强触/上调豁免 |

## 三、六向台账
- **上游输入**：C1 feed、X-R1 broadcast（governance）、各 sleeve intent。
- **下游消费**：C2-01→E-L4（净指令 state）、→X-S2-01；C2-04→C2-01；C2-02/03→C3 归因链。
- **自动化触发**：与 C1 同链——allocation_orchestrator 装配体一次性运行（regime→RegimeMetaAllocator→**BudgetChangeHandler**→StrategyBook→AdjudicationCenter，import 实测 allocation_orchestrator.py:108/1081）；夜批 09-14..09-22 零缺勤。
- **真源与注册表**：trading_decision_map.yaml:3759-3947；32 号 firm_risk_aggregator/33 号 budget_change_handler 设计备忘录在档；portfolio_model_refs PFM-HEU-002/PFM-RB-001/PFM-HEUR-009。
- **门禁与质量尺**：四节点全 auto；RLM-CONCENTRATION-002/003。
- **当前运行状态**：**黄偏绿（paper 域链路通、执行侧缺）**——四模块全 wired（firm_risk_aggregator 804 行被 batched_position_builder/boundary_revision_engine/single_name_cap_caliber/daily_gate_snapshot 消费；correlation_regime_monitor 182 行被 strategy_book/adaptive_risk_monitor 消费；budget_change_handler 1020 行被 allocation_orchestrator 消费）；但净指令下发 E-L4 执行侧=模拟域。

## 四、子模块清单
| 模块 | 行数 | 消费方（grep 实测） |
|------|------|--------------------|
| position/core/firm_risk_aggregator.py（MOD-POS-021，C2-01/02 共锚） | 804 | 4 处外部消费=wired |
| position/core/correlation_regime_monitor.py（MOD-POS-012） | 182 | strategy_book/adaptive_risk_monitor |
| position/core/budget_change_handler.py（MOD-POS-022） | 1020 | allocation_orchestrator |
| position/core/covariance_estimator.py（MOD-POS-011 底座） | 169 | 域内 |
| position/core/cross_strategy_position_merger.py（MOD-POS-005 底座） | 160 | 域内+rebalance_engine |

## 五、堵点与病灶
1. **BudgetChanged 事件链未接线**（33 号复核注记自认缺口，C2-04 的输入源未成事件；当前由 allocation_orchestrator 装配直调替代；修法=补事件发射或承认装配体直调为正源并回填 33 号；0.5-1 天）。
2. **C2-01 执行侧 netting 仍属三空白之一**（yaml 血肉阶段注记；聚合库成、但"净差单下发 E-L4"的真实撮合消费=模拟域 paper）。
3. **月度再聚类无调度登记**（C2-03 月度节拍未见 m5 计划任务；待 RC/M5 补挖波核对）。
4. **验证欠账**：BT-P3-039..042 四对象 plan=null；portfolio_attribution 未跑。

## 六、提速与合并机会
C2-02 资金三态账本与 cash_manager（MOD-POS-006）同源——禁第二本账；约束栈六层与 RLM 注册表同源查表，禁硬编码阈值。

## 七、自审闸三态
**挖干可施工**。

## 八、复核命令
```bash
grep -n "node_id: TDM-F-C2" config/trading_decision_map.yaml
grep -n "RegimeMetaAllocator\|budget_change_handler\|AdjudicationCenter" src/zephyr/pf_alloc/allocation_orchestrator.py | head -5
wc -l src/zephyr/position/core/firm_risk_aggregator.py src/zephyr/position/core/budget_change_handler.py
```
