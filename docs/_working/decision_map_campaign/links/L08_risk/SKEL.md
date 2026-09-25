---
ttl: task_bound
title: SKEL
doc_type: log
---

# L08 风控链路挖矿作业簿（环节 8 · 组合/回撤/熔断）

> 班次：链路 L08（风控）挖矿班 · 2026-09-25 · 只读挖掘+本文件唯一写入。
> 骨架真源：`docs/_working/decision_map_campaign/09_link_skeletons.md:555-620`（环节 8）；总纲=`../README.md`。
> 挖掘源已读：`src/zephyr/security/access_control/kill_switch.py`（全文）、`src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py`（全文）、`src/zephyr/trading/trading_contracts/risk/kill_switch_state_store.py`（全文）、`src/zephyr/risk/core/drawdown_state_machine.py`（§头注+配置区）、`src/zephyr/risk/core/systemic_risk_alert_state_machine.py`（§头注+配置区）、`tail_risk_monitor/liquidity_monitor/risk_veto_engine/liquidity_crisis_manager/ashare_systemic_risk_detector/stop_loss/risk_limits/drawdown_*家族/daily_gate_snapshot/defensive_asset_whitelist/capital_curve_manager/position_sizing_engine/tail_hedge_signal`（§BLUEPRINT 头注）、`src/zephyr/ex_core/risk_layer_orchestrator.py`（头注 INVARIANTS）、`src/zephyr/ex_core/pre_execution_checker.py`（闸门区）、`config/trading_decision_map.yaml:2735-2790/3156-3300/3850-3949`、`13_trading_chain_audit.md` 环节⑤+§9 汇总表、`14_consumption_census.md` 全文、`docs/_working/2026-09-12-fundamental-consumption-design.md` §1、`35_drawdown_protocol_impl.md`/`37_liquidity_crisis_protocol.md`（TOC）、`battle_map_09_risk_control.md`（结构+BM-RC-06-A/B 段）、`ulib3b_supply_relationship_ledger.md` S 行、`rebuild_from_disk`/`质押`/`pledge`/`drawdown` 全仓 grep。
> 探针结论先行：**rebuild_from_disk 全仓零调用方**（grep `src/ scripts/` 仅 store 自文件+主件头注自引）；**equity_pledge 两表 0 风控消费**（`14_consumption_census.md:39`）；**MOD-RK-049 状态机无现役端到端消费方**（`drawdown_state_machine.py:6` 自述，`daily_gate_snapshot.py:235` 读态恒 `absent`）。

---

## §1 子块全树（9 子块）

```
L08 风控（环节8）
├─ RSK-1 系统级 KillSwitch（AI Agent 行为熔断 · 非交易侧）…… kill_switch.py (MOD-INF-018, production)
├─ RSK-2 交易五级熔断 + 磁盘影子 ………………………………… trading_kill_switch (MOD-INF-016) + kill_switch_state_store (testing)
│   └─ 五级=POSITION_LIMIT/DAILY_LOSS(-3%AUM)/CIRCUIT_BREAKER/SECOND_LEVEL/API_TIMEOUT
├─ RSK-3 TDM 熔断五级 L0-L4 状态机 …………………………… drawdown_state_machine (MOD-RK-049) + R1-02 drawdown_liquidation_guard (MOD-RK-050) + R1-03 defensive_asset_whitelist (MOD-POS-026, design)
│   └─ L0 正常/L1 日亏≥2% 禁加仓/L2 ≥4% 禁开仓/L3 ≥6% 减仓/L4 回撤≥25% 保命（yaml:3193-3227）
├─ RSK-4 35 号回撤协议族（现役闭环+设计件并行）………… drawdown_tracker (MOD-RK-011) + position/core/drawdown_controller (MOD-POS-008) + capital_curve_manager (MOD-POS-007)
│   ├─ 35 号家族六件：watchdog/broker_side_stop/consecutive_loss/forced_rest/bankruptcy_floor/session_persistence
│   ├─ 盘中编排：ex_core/risk_layer_orchestrator (MOD-L06-001, 熔断单一仲裁点+五态降级机53号§3.8)
│   └─ 执行：stop_loss.execute_kill_switch_liquidation（15笔/秒限频+event_id 幂等）
├─ RSK-5 尾部风险 EVT/POT + UP-5 对冲信号 …………………… tail_risk_monitor (MOD-RK-15) + var_breach_state_machine (36号§3.15) + pf_alloc tail_hedge_signal (MOD-PA-024, D107 休眠)
├─ RSK-6 流动性监控 BM-RC-04-E + 37 号危机协议 …………… liquidity_monitor (MOD-RK-048, Amihud) + liquidity_crisis_manager (MOD-RK-21) + liquidity_crisis_scenarios
├─ RSK-7 系统性风险五信号 + 绿黄橙红黑五级 ………………… ashare_systemic_risk_detector (MOD-RK-10, 市场侧5信号→3级) + systemic_risk_alert_state_machine (MOD-RK-34, 组合侧→5级)
├─ RSK-8 质押否决器 + S41 解禁压力（设计态零消费）……… equity_pledge 两表 0 消费；restricted_shares/share_unlock 减仓逻辑 0 消费
└─ RSK-9 逐单否决与组合约束栈 ………………………………… risk_veto_engine (MOD-RK-24) + pre_execution_checker 四级闸 + F-C2-02 firm_risk_aggregator (MOD-POS-021) + F-C2-03 correlation_regime_monitor (MOD-POS-012) + F-C2-04 budget_change_handler (MOD-POS-022) + P-P1-04 ashare_stop_loss_engine (MOD-RK-09) + position_sizing_engine 半Kelly
```

**并存状态机全景（互认缺口直观图）**：交易五级（执行秒级，-3% AUM）∥ TDM L0-L4（组合日级，日亏 6% 减仓/回撤 25% 保命）∥ 35 号六态（NORMAL/WARN/DANGER/CRISIS/KILL/RECOVERY，5%/10%/15%/25%+VaR 2/4/6%+CVaR 10%）∥ MOD-RK-34 五级（GREEN/YELLOW/ORANGE/RED/BLACK，VaR 2/4/6%+CVaR 10%）∥ MOD-RK-10 三级（1 信号停开/2 降 30%/≥3 清仓）∥ ex_core 五态降级机（53 号 §3.8）。**六套阈值轴、两套"五级"、零互认仲裁序**（13 号文环节⑤缺陷 2：TRD-A13 待 Owner 立法）。

---

## §2 六向台账（每子块①上游②原料③输出④消费⑤挂点⑥缺口债）

### RSK-1 系统级 KillSwitch（AI Agent 行为熔断，禁误用作交易熔断）

| 向 | 台账 |
|---|---|
| ①上游输入 | detectors 域 9 触发器事件（rapid_file_deletion/agent_spawn_storm/audit_log_tamper 等，`kill_switch.py:125-135`）；manual_trip 全局/单 Agent（:242-254） |
| ②数据原料 | 纯进程内存态事件窗口计数（window_seconds=60 默认）；无落盘（进程崩即归零，:27-33 头注自述） |
| ③状态输出 | KillSwitchState 四态 NORMAL/TRIPPED/RESET_PENDING/COOLDOWN（:49-55）；owner_override 标记（:65-66） |
| ④下游消费 | `data/alert_webhook_dispatch.py:362`（触发源二：kill_switch 非 normal→告警）；`src/zephyr/ai_layer/intake/intake_events.py:128-133`（探针，不可达→stop_reason=kill_switch_probe_error 零消费）；`tests/agent_rbac/test_kill_switch_agent_rbac.py` |
| ⑤自动化挂点 | 告警链自动探针（在产）；复位=Owner 手动（:300-318），无自动路径 |
| ⑥缺口债 | 宪法 §7 速查表把它当"熔断"入口但**交易资金安全与其无关**（P1-2 澄清，:27-33）——文档面误导风险；状态纯内存无持久化（AI 行为域可接受，如实注）；reset() 代码无 Owner 权限闸（同 TRD 环节⑤缺陷 4） |

### RSK-2 交易五级熔断 + 磁盘影子（13 号文环节⑤主对象）

| 向 | 台账 |
|---|---|
| ①上游输入 | `evaluate(condition, evaluator)` 调用方注入判定（`trading_kill_switch.py:152-165`）；trigger()/reset() 手动/自动（:130-145）；触发/复位自动落盘（:119-127） |
| ②数据原料 | KILL_SWITCHES 五级定义常量（:71-112）：DAILY_LOSS 触发=daily_pnl<-0.03*aum、CIRCUIT_BREAKER=连续拒单≥5 或价差>5%、SECOND_LEVEL=延迟>1000ms 或成交率<50%、API_TIMEOUT=超时>10s 或心跳失联≥3；cooldown+auto_reenable 参数化 |
| ③状态输出 | active 旗标（内存唯一真源）+ 磁盘影子 `data/runtime/trading_kill_switch_state.json`（原子写 tmp→os.replace，`kill_switch_state_store.py:50,60-90`；13 号文实测文件存在 2026-09-23T02:43Z 全 false=真实写路径已走过） |
| ④下游消费 | **rebuild_from_disk 零调用方（断）**——grep 全仓仅 store 自引+主件 docstring 自述"交易会话启动侧（G2b/G5 接线点）"=接线点未到；头注 [CONSUMERS] MOD-INF-022/MOD-INF-020（模块登记口径）；active_switches() 供逐单闸探针（`ex_core/pre_execution_checker.py` 闸门 1，:176-206） |
| ⑤自动化挂点 | 触发/落盘/逐单拦截=自动（在产）；重启重臂=断（休眠）；解除=人工（reset 无权限闸=纪律靠约定，13 号文缺陷 4） |
| ⑥缺口债 | TRD-A12（rebuild 接线+HALT 拒单首演）；reset 权限闸代码化；"重启即失忆窗口"实存（落盘在、无人读） |

### RSK-3 TDM 熔断五级 L0-L4 状态机（X-R1-01/02/03）

| 向 | 台账 |
|---|---|
| ①上游输入 | 组合日盈亏+组合回撤双轴（`config/trading_decision_map.yaml:3193-3227`；判定轴与六段情绪市场轴正交）；数据断流→维持当前级别不降级（fail-closed，D103） |
| ②数据原料 | 阈值注册 THD-DRAWDOWN-001/002/003（5%/10%/15%，`alert_threshold_registry.yaml:64-102`）+RLM-KILLSW-003/005、RLM-KILL-SWITCH-004/005/006（yaml:3177,3212 挂接）；**注意 TDM 叙事的 L1≥2%/L2≥4%/L3≥6% 与 THD 卡 5/10/15% 两套数字并存**（状态机代码默认 warn 5%/danger 10%/crisis 15%/kill 25%+VaR 2/4/6%+CVaR 10%，`drawdown_state_machine.py:146-153`） |
| ③状态输出 | 熔断级别 L0-L4（TDM 叙事）/六态 NORMAL-WARN-DANGER-CRISIS-KILL-RECOVERY（代码实现，:94-102）；升级单调取最严可跳级、降级不可跳级+三重守卫（半阈值+min_hold+VaR 交叉验证）、RECOVERY 阶梯 0→1→2+毕业准则、KILL 仅人工复位（20 日窗 3 次/冷却 3 日/累计 5 次永久锁，:9 INVARIANTS） |
| ④下游消费 | **无现役端到端消费方**（`drawdown_state_machine.py:6` 2026-09-15 实测自述）：唯一 import 方 `drawdown_session_persistence` 的 premarket_initialization/postmarket_persist **src 内零调用者**（本班 grep 复核=0）；`daily_gate_snapshot.py:235` 读持久化态恒返回 `{"status":"absent","error":"no_persisted_level_v1"}`=**L5 门读态断**；`defensive_asset_whitelist.py:55` 声明"只消费不判定"但待接线（MATURITY=design）；原声称 RiskOrchestrator §6.5 接线位从未落地。现役回撤分级实际由 DrawdownTracker+DrawdownController 闭环（RSK-4） |
| ⑤自动化挂点 | 缺位：整链未接入任何事件通道；JsonStateStore 根目录未装配无可达落盘位（:6 自述） |
| ⑥缺口债 | LK-14（R1-03 proposed 未回测生效）；LK-13（回撤状态机全史输入=模拟盘长度）；M-55（Owner 人工接管正式入口缺位）；**内收债：MOD-RK-049 六态设计与 Tracker/Controller 现役闭环同域并行未启用——接线/收编/退役三选一裁定欠账**（L08-C03）；熔断级别流转全史无物化表（09 号文⑥） |

### RSK-4 35 号回撤协议族（现役闭环+设计件并行）

| 向 | 台账 |
|---|---|
| ①上游输入 | 组合净值/回撤序列（S70 域；alloc_budget_daily/adjudication 凭证链）；券商实时持仓（清算口径）；破产量原料=初始本金注入判定 |
| ②数据原料 | 家族六件（全 production，头注均声称 RiskOrchestrator §6.5 接线位）：drawdown_watchdog（独立看门狗进程 poll_once）、drawdown_broker_side_stop（券商端 stop 同步挂）、drawdown_consecutive_loss（连亏 cap_multiplier→position_sizing_engine 消费）、drawdown_forced_rest（强制休息+复位链前置校验）、drawdown_bankruptcy_floor（§4.10 破产底线 static 腿）、drawdown_session_persistence（§3.15/§3.18 盘前/盘后会话持久化）；真源 memo=`docs/_working/archive/2026-09/design_memos/35_drawdown_protocol_impl.md`（1664+ 行，§3.11 状态机/§3.14 复位守卫/§3.20 迟滞/§4.10 破产底线/§6.6 施工） |
| ③状态输出 | DrawdownTracker（MOD-RK-011）回撤读数→MOD-RK-17 Kill Switch EMERGENCY 触发；DrawdownController（MOD-POS-008）回撤分级→仓位上限；capital_curve_manager（MOD-POS-007）peak 单调+position_cap 仅由 drawdown_level 决定+EMERGENCY defensive_only（BM-POS-05 资金曲线回撤缩放/BM-POS-08 自诊断承载） |
| ④下游消费 | `ex_core/risk_layer_orchestrator.py`（MOD-L06-001，production，CONSUMERS=trading_session）：熔断单一仲裁点（重复触发不重复清算）、清算以券商实时持仓为准、KILL 态人工复位、破产底线只判定不发单（唯一发单点=_engage_kill_switch）、REBUILD 静态映射 VaR3%/CVaR5%（36 号 §3.10）；`risk/stop_loss.py` execute_kill_switch_liquidation（15 笔/秒限频分片+event_id 幂等+清算锁 Fail-Closed）；全史台账物化表仍缺（09 号文⑥🟡） |
| ⑤自动化挂点 | 盘中 evaluate_intraday 闭环（在产，经 risk_layer_orchestrator←trading_session）；watchdog=外部调度器驱动（设计）；session_persistence 盘前/盘后=**零调用（休眠）** |
| ⑥缺口债 | 家族头注"§6.5 接线位"与 MOD-RK-049 头注"从未落地"互相矛盾——**谁在真实驱动 35 号家族待接线级实查**（L08-C03 连带）；35 号 memo 全文未逐节对表（MINING 清单）；53 号五态降级机 memo 未读 |

### RSK-5 尾部风险 EVT/POT + UP-5 对冲信号

| 向 | 台账 |
|---|---|
| ①上游输入 | 收益分布尾部序列（S34：尾部数据+跳跃检测，`ulib3b_supply_relationship_ledger.md:69`）；VaR 基准=MOD-RK-05 口径 |
| ②数据原料 | ES/CVaR、GPD(ξ,β) POT 拟合（ξ>0 厚尾）、跳跃计数、FRTB 加价（`tail_risk_monitor.py:24-42`）；POT 失败计数器跨日持久化（连续 5 日失败→阈值 0.90→0.85，fail-closed，v0.2.0 AI-POT-001）；Copula 尾部依赖=`copula_garch_joint.py` 同域 |
| ③状态输出 | 极值预警+tail_index+跳跃计数（jump_count 单调非减）；var_breach_state_machine（36 号 §3.15）VaR 破限状态迁移；CVaR(5%) 对冲建议信号（MOD-PA-024 `pf_alloc/core/tail_hedge_signal.py`，纯函数无 IO，信号非指令） |
| ④下游消费 | 头注 [CONSUMERS] MOD-RK-03（Portfolio Risk Monitor 尾部告警）+MOD-RK-17（Kill Switch 极值触发）；UP-5→X-R1 R1-03 白名单通道（yaml:3163-3172 注，D107 回测验证前休眠 fallback） |
| ⑤自动化挂点 | 盘中监控设计位（battle_map BM-RC-06-B 自报 production、有效状态🟧设计态待施工——**地图自相矛盾如实注**）；对冲信号=休眠（D107） |
| ⑥缺口债 | UP-5 回测验证欠账（D107）；尾部数据 S34 供数→监控 runner 的盘中环 runner 缺位（=TRD-A07 同源，13 号文环节③）；EVT/POT 参数对表行业标准未做（§标准件 McNeil-Frey-Embrechts 待对表） |

### RSK-6 流动性监控 BM-RC-04-E + 37 号危机协议

| 向 | 台账 |
|---|---|
| ①上游输入 | OHLCV 日频行情（CTR-006）→Amihud+量缩比（`liquidity_monitor.py:24-46`）；盘内买卖价差+卖盘压力（系统性检测器侧）；S36（成交量+持仓+行情，ledger:71）；S43 etf_nav 折溢价+S45 期货对冲池（ledger:97,99，**0 分析消费**，14 号文§二#18） |
| ②数据原料 | Amihud ILLIQ=|r_d|/V_d、V_ratio=V_t/MA(V,N)（纯机制零参数）；流动性危机场景库=`liquidity_crisis_scenarios.py`；37 号 memo=`docs/_working/archive/2026-09/design_memos/37_liquidity_crisis_protocol.md`（§3.2 IPO 流动性抽离预警维度等） |
| ③状态输出 | LiquidityMetrics（CTR-P1-018）；MOD-RK-21 危机级别（LEVEL_1→0 恢复须经最短持续时间门控；跌停 spread=1.0/涨停=None；LEVEL_3 逃生指令） |
| ④下游消费 | MOD-L04-001（DefaultRiskManagerOrchestrator 流动性评估）+MOD-RK-09（LIQUIDITY_CRISIS 输入）；MOD-RK-17（LEVEL_3 逃生）；37 号联动=35 号 KILL 态禁 37 号恢复（risk_layer_orchestrator INVARIANTS） |
| ⑤自动化挂点 | 盘中风控循环同 tick（35 号 §3.13 设计位）；竞价数据消费实证=`risk/core/liquidity_crisis_manager.py`（14 号文§一③） |
| ⑥缺口债 | S43/S45 原料在库零分析消费（etf_nav/kline_futures）；37 号 memo 全文未对表（MINING）；BM-RC-04-E 盘中监控 runner 缺位（同 TRD-A07） |

### RSK-7 系统性风险五信号 + 绿黄橙红黑五级

| 向 | 台账 |
|---|---|
| ①上游输入 | S33：融资余额+流动性+政策新闻+外围指数（`battle_map_09_risk_control.md:1214`；ledger:68）；组合侧 VaR95/CVaR（MOD-RK-05 口径）+单日盈亏+连续两日亏损（调用方注入，`systemic_risk_alert_state_machine.py:35-36`） |
| ②数据原料 | 五信号=融资盘平仓潮/量化踩踏/流动性危机/政策转向/外围冲击（互斥检测+情绪断路器，`ashare_systemic_risk_detector.py` INVARIANTS）；cn_macro/MAC-15 条注册无供数绑定（S33 原料半缺，14 号文§二#6） |
| ③状态输出 | MOD-RK-10：命中信号数→三级（1 停开仓/2 降 30%/≥3 清仓，LEVEL_3 必须 RK-17 触发）；MOD-RK-34：GREEN/YELLOW/ORANGE/RED/BLACK（VaR95∈[2,4)/[4,6)/≥6%、CVaR≥10%、单日亏 -2%/-4%、连 2 日 -1%）→指令 scale=0.5/减仓 30%/50%/清仓+kill 触发标记（纯数据不执行） |
| ④下游消费 | 头注 [CONSUMERS] MOD-RK-03/MOD-RK-17（RK-10）；MOD-RK-34→编排层减仓/禁开/清仓执行+MOD-INF-016 BLACK 触发标记+风险仪表盘——**执行接线归编排层=三维解耦设计，仓内未见编排层消费 RK-34 的代码实证**（本班 grep 否决/熔断消费面未见引用，如实注） |
| ⑤自动化挂点 | battle_map 两节点自报 production、有效状态均🟧设计态待施工（地图口径矛盾=文档事故候选）；盘中 5 信号扫描 runner 缺位 |
| ⑥缺口债 | RK-34 指令→编排层接线缺口；S33 宏观原料（cn_macro/Swake/MAC-registry）零引用（14 号文§二#1,2,6）；BM-RC-06-C 三级警报清仓执行设计态；危机 θ 校准（config/crisis_gate.yaml enabled=true warning_theta=0.5，crisis_gate_log 0 行——O-5/TRD-A14 Owner 门位） |

### RSK-8 质押否决器 + S41 解禁压力（设计态零消费）

| 向 | 台账 |
|---|---|
| ①上游输入 | equity_pledge_detail/summary（c3_fundamental 两表，`data/implementations/akshare_provider.py:3868-3873` ak.stock_gpzy_pledge_ratio_em 产供，周更）；restricted_shares/share_unlock/share_change 解禁族（share_unlock 经 `data/event_calendar_filler.py` 入日历） |
| ②数据原料 | 质押比例序列+解禁日历；设计锚=`docs/_working/2026-09-12-fundamental-consumption-design.md` §1 不变量④（财务安全：资产负债率/流动比率/商誉占比/Altman Z，Piotroski 2000 依据）——质押为④的 A 股特色投影 |
| ③状态输出 | **无**（否决器未建码） |
| ④下游消费 | **0 消费**（`14_consumption_census.md:39`："质押风险否决器原料……0 消费"；:37 解禁族"减仓逻辑零消费"）；现存消费仅 api_server 用 total_shares 派生市值（:3923,3944）+news_sentiment_analyzer——非风控语义 |
| ⑤自动化挂点 | 缺位：akshare 产供链在产（backfill_checker 管 freshness），消费端全断 |
| ⑥缺口债 | 质押否决器接线（L08-C04：VetoRule OCP 注入点现成，`risk_veto_engine.py:44-45` 扩展点）；S41 解禁压力减仓（35 号协议声明的解禁前 30 日提示+压力减仓，逻辑零码）；两表 freshness/口径登记状态待核（DU 账） |

### RSK-9 逐单否决与组合约束栈

| 向 | 台账 |
|---|---|
| ①上游输入 | RiskSnapshot（MOD-RK-25 统一风控快照，经 risk_data_pipeline）+OrderRiskRequest；约束栈输入=全图 sleeve 目标仓位/intent 隐式订阅（yaml:3843 注 M-12）；预算变动事件（BudgetChanged 事件链未接线，33 号复核注记） |
| ②数据原料 | 限额真源（risk_limits.py MOD-L04-001+DefaultRiskLimitsCalculator）；单仓 20%/总杠杆/集中度 RLM-CONCENTRATION-002/003；60 日 PnL 相关矩阵+层次聚类（ρ>0.70 合并/0.85 禁新仓/cluster≤5%，MOD-POS-012+covariance_estimator Ledoit-Wolf）；六层约束栈顺序（总仓位→回撤限额→波动率目标→集中度→流动性→相关性，D76，yaml:3850-3885） |
| ③状态输出 | VetoDecision 结构化否决（P10 缺价/P15 限额缺失/P20 停牌/P30 超持仓/P35 T+1 可卖/P40 单仓限/P50 杠杆限，全量不短路，RULE_ERROR=否决 fail-closed，`risk_veto_engine.py:33-45`）；PreExecutionReport 四级闸（kill_switch 探针/会话窗/veto_engine/live 档阻断，`pre_execution_checker.py:193-206`，闸门 1+1.5 fail-closed）；预算三级响应（<10% 封锁新仓/10-25% 差异化窗口/【>25%】按比例强裁，yaml:3917-3948） |
| ④下游消费 | MOD-EX-024+MOD-L06-001（下单前硬拦）；trading_session 注入（:318,360,472，13 号文环节⑤实证"熔断→逐单拒单=通"）；P-P1-04 风险否决体检（四类否决线：生死线 -7%/时间止损/财报解禁禁区/板块退潮，yaml:2735-2760）→**MOD-RK-09 ashare_stop_loss_engine 38 测试全绿、零生产消费**（yaml 内 Owner 2026-09-06 接线里程碑注） |
| ⑤自动化挂点 | 逐单闸=自动在产（sim 实证）；P-P1-04 盘前体检=缺 runner；Kelly 半仓硬上限（position_sizing_engine，w_kelly≤0.5f）在 sizing 链在产 |
| ⑥缺口债 | P-P1-04 接线裁定（L08-C09）；BudgetChanged 事件链未接线；BM-RC-10 风险否决权/RC-11 独立管道=design 态（09 号文⑦）；F-C2-02 流动性约束（3 日可退出）的消费实证待查（MINING） |

---

## §3 自审闸三态汇总

| 子块 | 三态 | 未读指针清单（MINING 债） |
|---|---|---|
| RSK-1 | **SEALED** | — |
| RSK-2 | **SEALED** | — |
| RSK-3 | MINING | drawdown_state_machine.py 正文 160 行后（转换守卫/复位守卫实现）、`docs/03_modules/_domain_risk/algo_flow/drawdown_state_machine.yaml`、drawdown_liquidation_guard 蓝图、69 号 design memo §2.34 |
| RSK-4 | MINING | 35 号 memo 全文对表（§3.5 触发表/§3.13 盘中循环/§3.20）、六件家族模块正文、53 号五态降级机 memo、36 号 memo §3.10/3.15、RiskOrchestrator §6.5 真实装配面 |
| RSK-5 | MINING | tail_risk_monitor.py 正文、tail_hedge_signal.py 正文、`algo_flow/tail_risk_monitor.yaml`、copula_garch_joint 头注以下 |
| RSK-6 | MINING | 37 号 memo 全文对表、liquidity_monitor/liquidity_crisis_manager 正文、liquidity_crisis_scenarios 场景表 |
| RSK-7 | MINING | ashare_systemic_risk_detector 正文（5 信号阈值实现）、systemic_risk_alert_state_machine 正文 120 行后、MOD-RK-34 blueprint |
| RSK-8 | MINING | 基本面消费设计全文对表（本班仅读 §1）、DU 账两表登记状态、35 号 memo 解禁减仓节 |
| RSK-9 | MINING | risk_veto_engine 正文 70 行后、firm_risk_aggregator/correlation_regime_monitor/budget_change_handler 正文、ashare_stop_loss_engine 正文、33/32 号 memo |

**计数：9 子块｜SEALED 2｜MINING 7｜BLOCKED 0**（TRD-A13 仲裁序立法是 Owner 依赖，挂在施工项而非挖掘阻断——算法与断链事实已挖尽）。

---

## §4 施工项（L08-C01 起，净零声明随项）

| # | 项 | 内容与真源 | 沿用账本 | 内收声明/优先 |
|---|---|---|---|---|
| L08-C01 | **两套五级互认仲裁序立法** | 交易五级（-3% AUM，`trading_kill_switch.py:80-87`）× TDM L0-L4（日亏 6% 减仓，yaml:3193-3227）同日双触发谁说了算：产出映射表+在 `ex_core/risk_layer_orchestrator` 熔断单一仲裁点收口（该件 INVARIANTS 已宣称"熔断单一仲裁点"=天然收口位）；Owner 裁定门位 | TRD-A13 | 替代"两套并行无互认"现状，零新增组件；**P0** |
| L08-C02 | **rebuild_from_disk 会话启动接线+HALT 拒单首演** | `kill_switch_state_store.rebuild_from_disk()`（:93-143）接交易会话启动序列（trading_session 侧 G2b/G5 接线点）；首演=人为 trigger DAILY_LOSS→重启→验证重臂拒单→入演练台账（live_admission_checklist R7 计数 0→1） | TRD-A12 | 纯接线+演练，零新增；**P0** |
| L08-C03 | **MOD-RK-049 状态机三选一裁定（接线/收编/退役）** | 现役=DrawdownTracker+DrawdownController 闭环 vs 设计件六态状态机（`drawdown_state_machine.py:6` 自述并行未启用）；连带：JsonStateStore 根目录装配+`daily_gate_snapshot.py:235` 读态由恒 absent 变真值+35 号家族六件"§6.5 接线位"矛盾实查；同域重复簇→收敛唯一（内收 w5_1） | 新卡（内收审计窗口） | 裁定先行，施工随裁定；**P0** |
| L08-C04 | **质押否决器接线+S41 解禁压力消接** | equity_pledge 两表→`risk_veto_engine` OCP 注入新 VetoRule（P45 质押比例超阈值否决买入，阈值登记 RLM 新卡）；解禁族经 event_calendar_filler 日历→P-P1-04 事件禁区/35 号解禁压力减仓逻辑落码 | 新卡+LK（S41 断链施工化） | VetoRule 扩展点现成（:44-45），零新增引擎；**P1** |
| L08-C05 | trading_kill_switch.reset 权限闸代码化 | reset()/owner_release 语义对齐 KillSwitch "reset requires owner approval" invariant（`kill_switch.py:8`）； Owner 门位经 secrets/rbac 既有机制 | TRD 环节⑤缺陷 4 | 纪律代码化，零新增；P1 |
| L08-C06 | 熔断级别流转全史物化表 | 六套状态机（RSK 全景）迁移事件统一落库（事件触发落盘，禁 cron——运维红线 3）；消费=L09 复盘/BM-REC-02 风险报告 | 新卡（09 号文⑥状态真值🟡→✓） | 生成器产出（红线 5）；P1 |
| L08-C07 | crisis θ 校准+crisis_gate_log 演练回看 | `config/crisis_gate.yaml` warning_theta=0.5 月度演练回看误报率 | TRD-A14 | Owner 门位；P2 |
| L08-C08 | R1-03 护盘白名单回测生效 or 转显式休眠 | `defensive_asset_whitelist.py`（design）三重门+尾部弹药预算 D107 回测；UP-5 对冲信号同批验证 | LK-14 | 二选一，禁永久 proposed；P2 |
| L08-C09 | P-P1-04 ashare_stop_loss_engine 接线裁定 | 38 测试全绿 vs 零生产消费（yaml:2760 注）——接线或按 w5_1 收敛进 DrawdownController 判定轴 | 新卡（内收） | P2 |
| L08-C10 | THD-TRD-001..004 风险侧消费面 | 4 条交易级告警阈值接进运行时监控（`alert_threshold_registry.yaml:20-22,961-1023`） | TRD-A06 | 引用不重复立项；P2 |
| L08-C11 | M-55 Owner 手动接管正式入口节点 | paper 升档前置；TDM 图面增设节点+kill switch 人工解除通道统一 | M-55（与 L07 共享） | 登记先行；P2 |

**施工项计数：11（P0×3 / P1×3 / P2×5）。挖干即开工：P0 三项可直接进执行队列（L08-C01 需 Owner 一句话裁定）。**

---

## §5 标准件（18 号文纪律：有标准/开源必须引用并采用，不自造）

| 标准件 | 对应子块 | 出处 | 许可证/采用方式 |
|---|---|---|---|
| **Riskfolio-Lib**（risk parity 22 种凸风险度量+风险贡献分解+波动率目标） | RSK-9 F-C2-03 波动率目标/风险贡献 | [官方文档](https://riskfolio-lib.readthedocs.io)、[仓库 LICENSE](https://github.com/dcajasn/Riskfolio-Lib/blob/main/LICENSE.txt) | BSD-3-Clause（附不背书条款）；F-C2 波动率目标与风险贡献再平衡对表采用，禁自造求解器 |
| **PyPortfolioOpt**（HRP 层次风险平价 HRPOpt+efficient_risk 波动率目标） | RSK-9 相关性聚类/风险预算 | [文档](https://pyportfolioopt.readthedocs.io)（HRPOpt/Risk Parity 章）、[vol-target 讨论 #116](https://github.com/pyportfolioopt/pyportfolioopt/issues/116) | MIT；HRP 与 MOD-POS-012 层次聚类对表（可只对表算法不引依赖） |
| **Grossman & Zhou (1993) Optimal Investment Strategies for Controlling Drawdowns** | RSK-4 资金曲线回撤缩放理论基线 | Mathematical Finance 3(3):241-276，[EconPapers](https://econpapers.repec.org) | 论文（付费墙，结论公式公开引用）；MOD-POS-007 分级压缩公式对表 |
| **Yang & Zhang (2012) Optimal Portfolio Strategy to Control Maximum Drawdown** | RSK-4 离散交易版 DD 上限控制 | [SSRN](https://papers.ssrn.com) | 论文引用 |
| **Choi (2021) Maximum Drawdown, Recovery, and Momentum** | RSK-4 RECOVERY 阶梯/DD 动量信号 | [MDPI](https://www.mdpi.com) | 开放获取；RECOVERY 毕业准则与 DD 动量对表 |
| **McNeil, Frey & Embrechts, Quantitative Risk Management**（POT/GPD 极值理论标准） | RSK-5 EVT/POT | 教材（Princeton UP） | tail_risk_monitor 已按 POT 实现对表该书公式即可，禁重写 |
| **T. Rowe Price 多资产下行风险管理 risk overlay 实务** | RSK-9 overlay 编排 | [troweprice.com](https://www.troweprice.com) | 机构实务白皮书，overlay 分层（vol target+DD limit+trend filter）对照约束栈顺序 D76 复核 |
| **Universal-Investment Risk Overlay PLUS 案例（组合回撤 -6.23%）** | RSK-3/RSK-4 阈值量级标尺 | [universal-investment.com](https://www.universal-investment.com) | 案例标尺：TDM L3 减仓线 6% 与机构 overlay 实绩同量级，佐证阈值不必另造 |
| **Cassandra-Risk（Nayani 2026，预测市场事件概率→连续风险信号）** | RSK-7 系统性风险前瞻信号 | [SSRN](https://papers.ssrn.com) | 论文；S33 五信号之外的前瞻信号候选，回测验证后议（不即采） |

---

## §6 封矿裁定

本簿 **MINING**（7/9 子块有未读指针清单，见 §3）；但六向台账已按实证填毕、九大断链全部有路径级证据，施工项 P0×3 不受 MINING 状态阻塞（README"挖干即开工"条款）。封矿前置=清空 §3 各子块 MINING 清单后复核。

---

## §7 L08-C02 演练手册（真实 HALT 全流程——Owner 门位，施工班不执行）

> 接线已落地（2026-09-25 双接线施工班）：`TradingSession.start()` 启动序列第 1 步调 `kill_switch_state_store.rebuild_from_disk()`（`src/zephyr/ex_core/trading_session.py::_rearm_kill_switches_from_disk`，config 经 `TradingSessionConfig.kill_switch_state_path` 注入，缺省=store 默认路径）；kill -9 模拟演练已固化为正式测试（`tests/trading/test_kill_switch_state_store.py::TestKill9Drill` 三例：逐字段重臂一致/auto_reenable 冷却分界/影子损坏 fail-open，另有 `tests/ex_core/test_trading_session.py::TestKillSwitchRebuildWiring` 四例接线证明）。**本段落只备真实 HALT 演练手册，Owner 批准前不执行**——执行后回填 `live_admission_checklist` R7 计数 0→1（SKEL §4 L08-C02 行销号凭证）。

**演练前置（Owner 确认项）**：①sim 环境隔离确认（env=sim broker，禁触 real/实单路径，裁定 #338⑤ 同款红线）；②演练时间窗选非交易时段（避免误伤在途单）；③回滚预案=演练后 `trading_kill_switch.reset(DAILY_LOSS)` + 核对影子文件回归全 false；④台账登记（本段执行记录即 L08-C02 首演凭证）。

**演练步骤（人工 HALT→重启→重臂→拒单→解除）**：

1. **人为触发**：sim 交易会话运行中，人工调 `tks.trigger(KillSwitchLevel.DAILY_LOSS)`（或经 evaluate 注入 `daily_pnl < -0.03*aum` 判定）。预期：`active_switches()` 含 DAILY_LOSS + WARNING 落盘日志 + `data/runtime/trading_kill_switch_state.json` DAILY_LOSS.active=true（触发自动落盘钩子）。
2. **逐单闸验证（重启前基线）**：会话提交任意新单，预期 MOD-EX-024 闸门 1 熔断探针拒单（HALT）。
3. **kill -9**：对交易进程发 kill -9（不给优雅收尾机会；内存熔断态蒸发，唯一幸存者=磁盘影子）。
4. **重启**：正常拉起交易进程（`python -m zephyr.trading` 侧 trading_session 装配路径）。预期启动日志 `KILL_SWITCH_SESSION_REARM 从磁盘影子重臂 1 级: ['DAILY_LOSS']`。
5. **重臂断言**：`active_switches()` 含 DAILY_LOSS（跨重启维持，"当日不再恢复"语义守恒——auto_reenable=False 级不受冷却影响）。
6. **HALT 拒单首演（本演练核心断言）**：重启后提交新单，预期闸门 1 熔断探针拒单（拒单理由含 kill_switch）——即"重启失忆窗口"正式关闭的证据。
7. **解除**：Owner 手动 `tks.reset(KillSwitchLevel.DAILY_LOSS)` → 影子回归全 false → 提交单恢复放行 → 台账销号。

**不执行声明**：截至 2026-09-25 本演练未执行（步骤 1-7 全部 Owner 门位）；已执行部分仅限仓内侧：接线代码+kill -9 模拟测试（tmp_path 隔离，零生产路径写入）。
