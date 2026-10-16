---
ttl: task_bound
doc_type: tdm_mining_note
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
skeleton_row: TDM-P-P2
flow: position_flow
node_count: 5
session: mine-fullchain-tdm-20261015
---

# S_TDM-P-P2 做T与加减仓（5 节点）

## 1. 定义

一句话：做T=在底仓上高抛低吸赚差价降成本，不改变底仓股数——资格前置→策略调度→闭环判定三步，加减仓归 P3（与做T是三件事）；持有仓位跌了怎么办的"进攻半场"（PT-07 防守先于进攻设计，本环节为其中活性管理件）。

展开：做T资格三道门（P2-01：状态门=大盘吸筹/扩张段才做+振幅门=20 日均振幅≥3% 盖住双边成本 0.15%+成本门=预期价差≥0.3% 正期望线 CST-T0-001）；三策略并发扫描（P2-02：冲高回落 intraday-surge-fall/盘口失衡 orderbook-imbalance/VWAP 回归 vwap-reversion，单次做T量≤底仓 30%）；闭环判定（P2-03：每 5 分钟核对闭环、14:50 未闭环无条件平敞口不留隔夜 T、成功=股数不变+总成本降）；减仓再平衡（P2-04：漂移越带+置换机会两路触发，风控减仓优先级高于做T）。

## 2. 六向台账

### 2.1 输入面（有证）
- 入边（外部 4 条）：TDM-E-L0-04→TDM-P-P2（明日悲观预警）；TDM-E-L1-AGG→TDM-P-P2-01（状态门供数）；TDM-X-R1→TDM-P-P2-01（熔断禁做）；TDM-X-R1-02→TDM-P-P2-04（熔断减仓指令路由）。
- 内部入边：P1-04/P1-05/P1-06→P2 系（资格冻结/减仓指令/动作清单）。

### 2.2 输出面（有证）
- 出边 9 条：P2→P3（sequence）、P2→X-S1；P2-03→F-C3-01（做T盈亏统计喂归因）/→P3-01/→X-S2-01；P2-04→X-S2/X-S2-01。
- 状态矩阵 6 格挂 TDM-P-P2（accumulation/expansion/capitulation/ignition/euphoria/distribution 全六态实读）。
- 策略挂载 2 节点：intraday-surge-fall/orderbook-imbalance/vwap-reversion（PP-001 sleeve 03/06/07 同名，weight 0.063/0.04725/0.04725，activation_state=["accumulation","expansion"] 实读 portfolio_plan）。

### 2.3 SSOT 真源（有证）
- config/trading_decision_map.yaml#TDM-P-P2（line 3696-3769 区段）+P2-01..04（line 4032/4080/4133/4180）。
- 做T正期望线 CST-T0-001（P2-01 algo_note）；casebooks 挂 1 处；考试卡 17 张（position_flow/P2/）。
- 双拍供数：图13-D13-45 盘中模拟盘桥（做T双拍，骨架 §2.4 行）=本环节模拟面供数挂点。

### 2.4 代码模块（有证，4/4 子节点 ref 实存）
- position/core/t1_sellable.py（MOD-POS-028，T+1 可卖额度，与 X-S2-02 共锚双节点）、rebalance_engine.py（MOD-POS-004）。
- sell_decision/core/t_trade_coordinator.py（MOD-SELL-018 三策略调度）；signal_ashare/intraday_t0/t0_trading_pipeline.py（MOD-SIG-090 闭环）。
- 父枢纽 TDM-P-P2 无 ref（结构枢纽，INV-1 允许）。

### 2.5 门禁约束（有证）
- 四门同前；P2-03"14:50 无条件平敞口"属硬时点纪律，与图13-D13-28 盘后结算 T+1 硬时点同族（骨架 §2.4 行）。

### 2.6 自动化触发（有证）
- P2-01 盘前资格、P2-02/03/04 盘中 intraday；5 分钟闭环节拍+14:50 硬时点事件驱动。
- dloop 链无独立做T棒——做T执行经 t0_trading_pipeline 盘中自驱+X-R1 熔断事件打断。

## 3. 自审闸三态

| 向 | 态 | 打分依据 |
|---|---|---|
| 输入面 | pass | 总闸/熔断/体检三路外部入边+资格门供数在册 |
| 输出面 | pass | 出边 9 条+状态矩阵 6 格+PP-001 三 sleeve 同名挂接 |
| SSOT | pass | 节点行+CST-T0-001+17 张考卡+D13-45 供数挂点 |
| 代码模块 | pass | 4/4 子节点实存（t1_sellable 双锚复用） |
| 门禁约束 | pass | 四门+硬时点纪律同族 |
| 自动化触发 | pass | 盘中自驱+熔断打断+模拟盘桥 |

**总评：pass（6/6）**。

## 4. 缺口与建议

1. 做T三策略（surge-fall/orderbook-imbalance/vwap-reversion）在 PP-001 有 sleeve 权重但策略实现挂载点在 P2-02 散文（t_trade_coordinator 调度），map 无 strategy_ref 直挂 P2 节点——建议给 P2-02 补 strategy_mounts 使 sleeve↔节点机械对上（现挂载关系靠同名人工对读）。
2. P2-03 做T成功/失败/损耗统计喂 C3-01 有边，但"做T是降成本工具不是独立盈利来源"的口径无独立验证方法学条目（REG-VALM-001 五类方法中无做T专项）——建议挂执行质量维子项。
3. 14:50 强平底敞口与券商通道断线场景的交互（断线时平不掉）未见兜底节点——X-R1 横切覆盖面声明建议补一句（现 R1 只写全清仓/降档）。
