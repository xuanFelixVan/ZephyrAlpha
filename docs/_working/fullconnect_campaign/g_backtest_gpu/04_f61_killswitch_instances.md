---
ttl: task_bound
title: "F61 KillSwitch 三实例族——交易级/容量级/回滚级+状态存储"
session: zc-l07-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F61 · KillSwitch 三实例族（总册状态 built（M3：持久化待裁）/P0；本卷复核=机制绿/重臂红，同名族实为 6 件）

## 一、六向台账（实证锚点）

| 向 | 实证（本日实勘） |
|---|---|
| 上游输入 | risk_layer_orchestrator.evaluate_intraday（四链风控）；kill_switch_orchestrator.route_incident（BRK-078 保命动作唯一入口）；F59 限额面 |
| 下游消费 | trading_session._is_blocked_by_risk（trading_session.py:908/979，M7-02 实锚）；pre_execution_checker 闸门 1 熔断探针（:176-206）+闸门 1.5 blocks_live_trading（:259-274，已接线）；全交易面拒单 |
| 自动化触发 | 盘中评估=调仓线程内嵌；**rebuild_from_disk 设计为进程启动重臂但零生产调用**（M7-02 grep 复证在案）；无独立常驻 |
| 真源与注册表 | 五级唯一真源=src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py:52-112（KILL_SWITCHES，本日 wc=165 行）；磁盘影子=data/runtime/trading_kill_switch_state.json（**本日实测存在**：saved_at 2026-09-25T03:49Z，5 开关全 false=写路径走过真）；kill_switch_state_store.py 143 行（save :60/rebuild :93） |
| 门禁与质量尺 | 触发/复位自动落盘 fail-open（:119-127 落盘失败 CRITICAL 不回滚熔断）；rebuild 纯加闸不加放；KILL 态人工复位；DefaultRiskValidator JsonStateStore 启动读"启动即熔断=禁新单"（risk/implementations/default_risk_validator.py:75-157+start_paper_session.py:541） |
| 当前运行状态 | **黄**：触发/落盘/逐单拦截=绿（state file 实证）；**重臂=红**（rebuild 零调用=重启失忆窗）；演练=红（HALT 拒单演练 0 次，M7-02 B4） |

## 二、子模块三级枚举（同名族 6 件全实扫，本日 wc）

| 件 | 行数 | 语义 | 态 |
|---|---|---|---|
| trading/trading_contracts/risk/trading_kill_switch.py | 165 | 交易五级（POSITION_LIMIT/DAILY_LOSS -3%AUM/CIRCUIT_BREAKER/SECOND_LEVEL/API_TIMEOUT） | production，逐单闸消费 |
| trading/trading_contracts/risk/kill_switch_state_store.py | 143 | 熔断态持久化（save 通/rebuild 断） | **半接线** |
| security/access_control/kill_switch.py | 341 | **AI Agent 行为风控熔断（非交易！）**：27-33 P1-2 边界自注 | production；M0 锚点漂移源 |
| infrastructure/capacity_assurance/kill_switch.py | 145 | 容量保险丝 | 在（编排器四域之一） |
| infrastructure/rollback/kill_switch.py | 218 | 三级 L1 session/L2 skill/L3 global（token-gated） | production（治理面归 M3） |
| autonomy_core/kill_switch_orchestrator.py | — | 两级编排统一入口（boot_hooks :595/:684 开机注册）+ex_core/LiveSimulationSwitcher 三道锁之一 | production |

## 三、接线四态独立复核

| 面 | 四态判定 | 复核证据 |
|---|---|---|
| 五级触发/拦截 | 已接线（production） | state file 2026-09-25 实证+RiskLayerOrchestrator 单一仲裁点 |
| 状态持久化 | **半接线**（save 通/rebuild 断） | M7-02 B1 本班独立复证；两套持久化并存（tks store vs JsonStateStore） |
| 容量级/回滚级 | built（编排器域） | capacity 145 行/rollback 218 行在盘，经 orchestrator 适配 |
| 演练面 | **缺位** | 拒单链零次实弹证明（G5 前置必做） |

### 骨架勘误
- **总册 F61 锚点"三实例"列 access_control/kill_switch.py 为交易面实例=锚点漂移**（M7-02 B5 已勘误，本卷复核维持）：access_control=AI 行为熔断非交易；且漏列 rollback/kill_switch（第三真实例）。建议总册锚点改为 trading_kill_switch/capacity_assurance/rollback 三件+orchestrator。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 重启=熔断失忆窗（rebuild 零调用） | ①rebuild_from_disk 一行接入 TradingSession.start/boot_hooks（0.5 天）②长期并入 JsonStateStore 家族（1 天，归并方向待裁 Owner） | P0 |
| 2 | 双五级阈值口径不一+仲裁序未立法 | Owner 门位（与 F60 缺口 3 同案） | P1（Owner） |
| 3 | reset 无代码门位（任何调用方可调） | reset 加 approver 参数对齐编排器（0.5 天） | P1 |
| 4 | 拒单演练 0 次 | sim 注入假 validator 触发 DAILY_LOSS→拒单+落盘+重臂全链演练入台账（0.5 天，G5 前置） | P0 |
| 5 | 6 同名族查询面分散 | 查询统一走 orchestrator.is_tripped（M7-02 合并方向，M3 合议） | P2 |

## 五、自审闸三态
**挖干可施工**（6 件同名族+state file+持久化双轨全实证；缺口 1①/3/4 可直接施工，1②/2 Owner 门位）。

## 六、复跑命令
```bash
wc -l src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py src/zephyr/trading/trading_contracts/risk/kill_switch_state_store.py src/zephyr/security/access_control/kill_switch.py src/zephyr/infrastructure/capacity_assurance/kill_switch.py src/zephyr/infrastructure/rollback/kill_switch.py   # 165/143/341/145/218
cat data/runtime/trading_kill_switch_state.json     # saved_at 2026-09-25T03:49Z，5 开关
grep -rn "rebuild_from_disk" src scripts --include="*.py" | grep -v state_store.py | grep -v test   # 零生产调用
sed -n '27,33p' src/zephyr/security/access_control/kill_switch.py   # 非-交易边界自注
```
