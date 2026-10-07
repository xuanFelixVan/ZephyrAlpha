---
ttl: task_bound
completes_when: 五项二源对表复核（研究班带宽窗）或逐项采納裁定落册
created: 2026-10-07
sid: st-mastertc-l9
status: 思想摘要+仓内对表首版（禁联网，凭仓内案卷+通识；外仓只学思想不引代码）
card: C189（总包夜战 master_tc_night L9 车道；承接 st-finaldel-cdocs3 defer 项）
---

# L08 · 外部对表 5 项（external_benchmark_5）

> 上游=L08_risk/SKEL.md §5 标准件表 9 行（出处/许可证在册）；本件按 C189 处方补五项**思想摘要+仓内模块指针**。纪律：外仓禁商用只学思想，无代码面可机械核实（defer 原话），故每项只给「思想五八字+指针」，采纳与否归研究班二源对表。

## 1. 熔断双签（dual-sign reset）

- 思想：熔断触发可自动化，**解除必须双人/双通道确认**——单点 reset 权=单点故障面（攻击者或 bug 一次调用即复活风险敞口）；机构实务（交易所断路器+交易所外风控双通道）与内核安全双人多签同构。
- 仓内对表：交易侧 `trading_kill_switch`（MOD-INF-016）+ 磁盘影子 `kill_switch_state_store`（testing）；SKEL RSK-2 ⑥已登记 reset 链缺陷（同 TRD 环节⑤缺陷 4「reset() 无 Owner 权限闸」）——**双签处方=reset 须 owner-ruling 引用+第二通道确认**，与 S9 retire_module 的「--execute 缺 owner-ruling 硬拒」同构，可复用其参数校验骨架。
- 指针：`src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py`、`ex_core/risk_layer_orchestrator.py`（熔断单一仲裁点 INVARIANTS）。

## 2. Grossman & Zhou (1993) 回撤控制最优策略

- 思想：给定最大回撤上限 d，最优解=按「当前净值相对历史高点的比例」线性缩放风险敞口（proportional strategy），跌破线强制降杠杆——回撤预算制的理论基线，证明「分级压缩」不是经验主义而是受约束最优。
- 仓内对表：SKEL §5 已在册（RSK-4 理论基线，付费墙结论公式公开引用）；落点=MOD-POS-007 分级压缩公式 + `capital_curve_manager`/`drawdown_state_machine`（MOD-RK-049）的分级缩放比对表对象。
- 指针：`src/zephyr/risk/core/drawdown_state_machine.py`、`docs/_working/decision_map_campaign_20260924/links/L08_risk/s4_drawdown_protocol_family/`。

## 3. Amihud ILLIQ + VPIN（流动性两尺）

- 思想：Amihud（2002）|r|/成交额=价格冲击比（日频低频尺）；VPIN（Easley/O'Hara 2012）=成交量同步知情交易概率（高频毒性尺，量桶订单流不平衡）——两者互补覆盖「慢流动性枯竭」与「快毒性流失」两态。
- 仓内对表：Amihud **已实现**（`liquidity_monitor.py:24-46`，|r_d|/V_d + V_ratio 量缩比，纯机制零参数）；VPIN 仓内**未见实现**——候选增量（需 tick 级买卖方向标注，S36 成交量原料在库），按 SKEL RSK-6 ⑥缺口债「S43/S45 零分析消费」同批议。
- 指针：`src/zephyr/risk/core/liquidity_monitor.py`、`liquidity_crisis_scenarios.py`、37 号 memo §3.2（IPO 流动性抽离预警维度）。

## 4. Riskfolio-Lib（组合风险度量库）

- 思想：22 种凸风险度量（CVaR/CDaR/最坏情形优化等）+ 风险贡献分解统一求解框架——「风险预算」不唯方差，尾部度量可进同一凸优化；BSD-3 在册。
- 仓内对表：SKEL §5 首行（RSK-9 F-C2-03 波动率目标/风险贡献，**禁自造求解器**）；本仓对表方式=对表算法思想不引依赖（与 PyPortfolioOpt 同款纪律），落点=position_sizing_engine 波动率目标 + MOD-POS-012 层次聚类。
- 指针：`docs/_working/decision_map_campaign_20260924/links/L08_risk/`（RSK-9 子块）、`src/zephyr/portfolio`（F-C2 消费面）。

## 5. Agent 行为熔断（非交易侧）

- 思想：AI Agent 的异常行为（批量删文件/进程风暴/审计日志篡改）与交易熔断同构——异常检测器→状态机→硬拦截，但**资金面与行为面必须分域**（行为熔断不禁交易，交易熔断不由行为域误触）。
- 仓内对表：RSK-1 系统级 KillSwitch（MOD-INF-018，production）9 触发器（rapid_file_deletion/agent_spawn_storm/audit_log_tamper 等，kill_switch.py:125-135）；在案缺口债=宪法 §7 速查表曾把它当交易熔断入口（P1-2 澄清已纠）+状态纯内存无持久化（行为域可接受已注）。
- 指针：`src/zephyr/security/access_control/kill_switch.py`、`data/alert_webhook_dispatch.py:362`（告警联动）、`tests/agent_rbac/test_kill_switch_agent_rbac.py`。

## 对表节律

五项均入 L10 裁定台观察面；二源对表（外仓研究窗）复核后逐项出采纳裁定，本件只登记思想与指针，不落代码面。
