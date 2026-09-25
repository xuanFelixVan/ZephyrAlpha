---
ttl: task_bound
---

# M7-02 · Kill Switch 交易面（T11）

> 挖矿班 st-commitspeed-tbl-20260924 ｜ 2026-09-25 ｜ 只读挖矿
> 边界（M0 裁定）：交易级→本册；kill_switch 注册表限额面（62 条）→M3；watchdog 常驻→M5。
> 交叉引用：13_trading_chain_audit.md 环节⑤（重臂断链/双五级仲裁已登）；本文给代码级全家福与两套持久化的合并判定。

## 一、环节定义与边界
交易资金安全侧的熔断/止损/限额执行面：触发→落盘→逐单拦截→（人工）复位。上游=风控计算件（drawdown/VaR/tail）、盘中评估；下游=OrderManager/TradingSession/pre_execution_checker 的拒单闸。

## 二、六向台账
| 向 | 内容与实证 |
|---|---|
| 上游输入 | risk_layer_orchestrator.evaluate_intraday（NAV 时序→回撤/VaR/尾部/系统性四链）；risk_manager_agent（确定性校验路径）；kill_switch_orchestrator.route_incident（BRK-078 保命动作唯一入口） |
| 下游消费 | trading_session._is_blocked_by_risk/risk_layer.allow_new_position（`trading_session.py:908/979`）；pre_execution_checker 闸门 1 熔断探针（`:176-206`，paper 侧=lambda: validator.kill_switch_active `start_paper_session.py:565`）；_LiquidationBrokerAdapter 清算发单（`risk_layer_orchestrator.py:365`） |
| 自动化触发 | 盘中=evaluate_intraday 由调仓线程调用（事件内嵌）；**无独立盘中风控 runner**（audit TRD-A07）；rebuild_from_disk 设计为进程启动重臂但**零调用方**（本班 `grep -rn rebuild_from_disk src scripts tests` 除定义外零命中，独立复证 audit 结论） |
| 真源与注册表 | 五级定义=trading_kill_switch.py:71-112（KILL_SWITCHES 唯一真源，内存态）；磁盘影子=data/runtime/trading_kill_switch_state.json（**实测存在**，2026-09-23T02:43Z 全 false=写路径走过真）；TDM L0-L4=drawdown_state_machine（日级，归 M2 挖） |
| 门禁与质量尺 | 触发/复位自动落盘 fail-open（`:119-127` 落盘失败 CRITICAL 不回滚熔断）；rebuild 纯加闸不加放（auto_reenable 且冷却过→不重臂）；KILL 态人工复位、降级机只迁移警报不解除闩锁（`risk_layer_orchestrator.py:8` INVARIANTS）；破产底线只判定不发单、唯一发单点=同一仲裁点 |
| 当前运行状态 | **黄**：触发/落盘/逐单拦截=绿（机制走过真实写路径）；重臂=红（休眠）；演练=红（HALT 拒单演练 0 次，live_admission R7） |

## 三、子模块清单（kill switch 全家福 11 件，find+grep 两源）
| 子模块 | 是什么 | 入口 file:line | 状态 |
|---|---|---|---|
| trading_kill_switch（五级） | POSITION_LIMIT(reduce_only,300s 自恢复)/DAILY_LOSS(-3%AUM,撤全单+禁新)/CIRCUIT_BREAKER(连5拒或偏离5%→断连)/SECOND_LEVEL(延迟>1s或成交率<50%→全停)/API_TIMEOUT(超时10s或心跳丢3→杀会话) | trading/trading_contracts/risk/trading_kill_switch.py:52-112 | production，逐单闸消费 |
| kill_switch_state_store（历史保险⑤：熔断态持久化） | 触发/复位原子落盘 tmp→os.replace；rebuild_from_disk 重臂 | trading_contracts/risk/kill_switch_state_store.py:60/93 | testing；**save 已接线（trigger/reset :130-145 自动落盘），rebuild 零生产调用=半接线** |
| RiskLayerOrchestrator | 盘中级联真源：重建完成前禁下单 fail-closed+熔断单一仲裁点+五态降级机+破产底线+VaR 回测定级单执行者 | ex_core/risk_layer_orchestrator.py:453（INVARIANTS :8） | production；start_paper_session 必装配 |
| access_control/kill_switch | **AI Agent 行为风控熔断器（非交易！）**，9 触发器纯进程内存态 | security/access_control/kill_switch.py:27-33（P1-2 边界自注"勿误用作交易熔断"） | production；M0 骨架 T11 把它列进交易面=锚点漂移，本册勘误 |
| kill_switch_orchestrator | 两级编排（系统级 MOD-INF-018+四域分开关），适配器包装不持状态，复位须 approver | autonomy_core/kill_switch_orchestrator.py（boot_hooks._init_kill_switch_orchestrator :595,684 开机注册） | production |
| rollback/kill_switch | 三级 L1 session/L2 skill/L3 global（token-gated） | infrastructure/rollback/kill_switch.py:31-34 | production，回滚域（治理面引 M3） |
| capacity_assurance/kill_switch | 容量保险丝单实例 | infrastructure/capacity_assurance/kill_switch.py | 在（编排器四域之一） |
| LiveSimulationSwitcher | 模拟→实盘一次性确认令牌 fail-closed（sha256 指纹留痕）；实盘→模拟免令牌 | ex_core/live_simulation_switcher.py:8（INVARIANTS） | production；三道锁之一 |
| pre_execution_checker 闸门 1.5（历史保险⑥：S-1） | live 档 blocks_live_trading=true→拒全部新单 fail-closed（纯加闸不加放） | ex_core/pre_execution_checker.py:259-274 | **已接线**（audit 七红 C2 已闭，本班代码复证） |
| DefaultRiskValidator kill_switch 外部化 | JsonStateStore 持久化+启动读（"启动即熔断态=禁任何新单"） | risk/implementations/default_risk_validator.py:75-157+start_paper_session.py:541 | production，**已接线**（paper 面） |
| sev_router / systemic_risk_alert_state_machine | SEV-2 资金异常路由到交易五级；BLACK 触发标记消费 | ai_layer/redline/sev_router.py:38；risk/core/systemic_risk_alert_state_machine.py:33 | 登记在案，执行接线归编排层 |

## 四、堵点与病灶
| # | 现象/根因/修法/工作量/归属 |
|---|---|
| B1 | **重启=熔断失忆窗（TRD-A12 同判，本班加细）**：两套持久化并存——tks state_store（save 通/rebuild 断）与 DefaultRiskValidator JsonStateStore（读写全通）。修法双轨：①rebuild_from_disk 一行接入 TradingSession.start 或 boot_hooks（0.5 天）；②长期按内收判据"同真源可派生→必并"把五级状态并入 JsonStateStore 家族（1 天，待裁归并方向） |
| B2 | **双五级无互认**（audit TRD-A13 已呈）：交易五级（-3%AUM 秒级）vs TDM L0-L4（日级 4% 禁开/6% 减仓）阈值口径不一，同日双触发仲裁序未立法。待裁（Owner） |
| B3 | **reset 无代码门位**：trading_kill_switch.reset(level) 任何调用方可调，权限靠约定（audit 环节⑤-4 同判）；对照系统级 KillSwitch 的 Owner 批准语义。修法=reset 加 approver 参数对齐编排器；0.5 天；可施工 |
| B4 | **演练 0**：所有拒单闸未经过一次实弹证明（G5 HALT 拒单演练进度 0）。修法=sim 环境注入假 validator 触发 DAILY_LOSS→验证拒单+落盘+rebuild 重臂全链并入台账；0.5 天+台账；G5 前置必做 |
| B5 | stop_gate（trading/stop_gate.py）名字像交易止损实为"AI 不干活就退出"质量闸（MOD-INF-035，auto_runtime_core）——M0 T11 锚点漂移第二例，本册勘误：交易止损真源=sell_decision/stop_hunting_protector+position/core/drawdown_controller（见 03 册） |

## 五、提速与合并机会
- 五套"kill switch"（access_control/trading/rollback/capacity/orchestrator）+Lite（discipline_prohibition_checker.py:124 KillSwitchLite）=6 个同名族。编排器已用适配器统一入口；下一步合并方向=查询面统一走 orchestrator.is_tripped（支配语义已实现），各域本体保留执行语义。属治理面优化，与 M3 合议。
- 交易五级与 TDM 门槛值同源化：两套阈值出处不同（硬码 vs 注册表），合并进 alert_threshold_registry 一处（TRD-A06 顺带）。

## 六、自审闸三态
**挖干可施工**（B1①/B3/B4 可直接施工；B1②/B2 待裁挂 pending_rulings 由总筹转 Owner）。

## 七、复核命令（10 分钟）
```bash
sed -n "52,112p" src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py   # 五级全定义
cat data/runtime/trading_kill_switch_state.json                                      # 磁盘影子实测
grep -rn "rebuild_from_disk" src scripts --include="*.py" | grep -v state_store.py   # 零调用=B1 实证
sed -n "259,274p" src/zephyr/ex_core/pre_execution_checker.py                        # S-1 闸门 1.5
sed -n "27,33p" src/zephyr/security/access_control/kill_switch.py                    # 非-交易边界自注
```
