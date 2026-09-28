---
ttl: task_bound
title: "F60 回撤状态机与熔断——回撤分级状态机+清算守卫+券商端止损双保险"
session: zc-l07-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F60 · 回撤状态机与熔断（总册状态 built/P0；本卷复核=判定件 built wired（paper 日链），减仓编排/盘中常驻两缺）

## 一、六向台账（实证锚点）

| 向 | 实证（本日实勘） |
|---|---|
| 上游输入 | F63 NAV 记录（live_nav_recorder 253 行，读不到券商实时净值=拒装配 exit 1）；组合日盈亏（R1-01 判定轴）；TDM-E-L0 broadcast |
| 下游消费 | F47 R1 熔断分级（同一文件双登记，f47 册已声明"勿双登记"）；P2-04 减仓/S1-06 强清/P3-01 禁加期（TDM 边）；本日消费者 grep 实测 4：position/core/defensive_asset_whitelist.py、risk/core/drawdown_session_persistence.py、risk/core/var_breach_state_machine.py、strategy_pipeline/daily_gate_snapshot.py |
| 自动化触发 | paper 日链内运行（daily_gate_snapshot 日快照+session_persistence 会话持久化）；**盘中 continuous 保命扫描无常驻载体**（f47 册 §五-2 同判，M7/RC+M5 域） |
| 真源与注册表 | 判定件=src/zephyr/risk/core/drawdown_state_machine.py（773 行实测，MOD-RK-049，DAL-CIRCUIT-5 code_ref）；TDM 判据=trading_decision_map.yaml:3156-3289（f47 册实锚）；algo_flow yaml 外迁件=docs/03_modules/_domain_risk/algo_flow/drawdown_state_machine.yaml+drawdown_liquidation_guard.yaml（f47 册实锚）；离散态 L0-L4+迟滞解除+L4 Owner 人工=f47 册 §二全表 |
| 门禁与质量尺 | tests/risk/test_drawdown_state_machine.py 在盘（f47 册实证）；KILL 态人工复位/降级机只迁移警报不解除闩锁（risk_layer_orchestrator.py:8 INVARIANTS，M7-02 实锚） |
| 当前运行状态 | **黄（判定绿/编排红）**：状态机落码+测试+paper 日链 4 消费=绿；drawdown_liquidation_guard（209 行实测，MOD-RK-050）**零外部消费方**（f47 册 grep 实证）=判了没人执行 |

## 二、子模块三级枚举（risk/core 回撤族本日实扫 9 件）

- drawdown_state_machine.py（773 行，分级判定真源，4 消费者）
- drawdown_liquidation_guard.py（209 行，清算守卫，零消费=挂机）
- drawdown_broker_side_stop.py（241 行，券商端止损双保险，F60 面归 M7 管——f47 册边界声明）
- drawdown_bankruptcy_floor.py（破产底线：只判定不发单，唯一发单点=仲裁点，M7-02 实锚）
- drawdown_consecutive_loss.py / drawdown_forced_rest.py（连亏强制休整族）
- drawdown_tracker.py（DrawdownTracker，基线=券商实时净值）
- drawdown_watchdog.py（守望件）
- drawdown_attribution.py（回撤归因）
- drawdown_session_persistence.py（会话持久化，消费状态机）

## 三、接线四态独立复核

| 面 | 四态判定 | 复核证据 |
|---|---|---|
| 状态机判定 | **已接线（paper 日链）** | 4 消费者本日 grep 复测（较 f47 册 3 消费者多出 var_breach_state_machine 一方，补录） |
| 清算守卫 R1-02 | **码在零消费（半接线）** | 209 行 guard 零外部消费（f47 册+本卷 wc 复核）；减仓编排缺=判了没人执行 |
| 券商端双保险 | 引用态 | 241 行在盘；执行接线归编排层（f47 册边界+M7-02 五级族） |
| 盘中保命扫描 | **缺位** | 无常驻 runner（f47 册 §五-2；audit TRD-A07 同判） |

### 骨架勘误
- 无锚点级勘误；补充：var_breach_state_machine 亦消费状态机（总册/f47 册消费者清单外第 4 方）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | liquidation_guard 零消费（R1-02 减仓编排断） | 接 P2-04/X-S2 编排工单（与 F43/F46 同批；f47 册判"本车道可修"） | P0 |
| 2 | 盘中 continuous 保命扫描无常驻 | RC/M7 车道+M5 常驻族施工；须登记 process_reaper_keep | P0 |
| 3 | 双五级无互认（交易五级 -3%AUM 秒级 vs TDM L0-L4 日级 4%/6%，同日双触发仲裁序未立法） | Owner 门位（M7-02 B2/TRD-A13 在案） | P1（Owner） |
| 4 | M-55 paper 升档前 Owner 人工接管入口缺位 | 治理面欠账，Owner 门位（f47 册 §五-3） | P1（Owner） |
| 5 | R1-03 护盘白名单数据地基缺（ETF 天量检测需 ETF 日线登记 D109） | 休眠是正确态，勿提前激活（f47 册 §五-4） | P2 |

## 五、自审闸三态
**挖干可施工**（9 件回撤族全实扫+4 消费者复测+编排缺口处置明确；缺口 3/4 归 Owner 门位挂 99 台账）。

## 六、复跑命令
```bash
wc -l src/zephyr/risk/core/drawdown_state_machine.py src/zephyr/risk/core/drawdown_liquidation_guard.py src/zephyr/risk/core/drawdown_broker_side_stop.py   # 773/209/241
grep -rln "drawdown_state_machine\|DrawdownStateMachine" src/zephyr --include="*.py" | grep -v __pycache__ | grep -v core/drawdown_state_machine   # 4 消费者
grep -rln "drawdown_liquidation_guard" src/zephyr --include="*.py" | grep -v __pycache__   # 仅自身=零消费
grep -n "node_id: TDM-X-R1" config/trading_decision_map.yaml | head -4
```
