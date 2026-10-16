---
ttl: task_bound
doc_type: tdm_mining_note
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
skeleton_row: TDM-X-R1
flow: exit_flow
node_count: 4
session: mine-fullchain-tdm-20261015
---

# S_TDM-X-R1 应急保命/熔断（4 节点）

## 1. 定义

一句话：系统的"拔电源"（PT-12"AI 交易人把关"）——kill switch 常驻任何档位不可移除，组合级回撤 25% 或单日 -6% 触发→无条件全清仓+冻结所有开仓通道，只能 Owner 手动解除；AI 熔断只降档不升档。

展开：横切面（cross_cutting）四节点：R1 本体=KillSwitch（MOD-INF-018，security/access_control）；R1-01 熔断五级状态机（L0 正常/L1 警戒日亏≥2% 禁加仓/L2 禁开仓+白名单窄门/L3 减仓日亏≥6% 梯度减/L4 保命回撤≥25% 清仓+Owner 人工接管；判定轴=组合日盈亏+组合回撤双轴与六段情绪市场轴正交；迟滞解除=当日无新低+修复跌幅 50% 才降一级，禁 V 型回满）；R1-02 熔断期减仓顺序（重亏仓→高波动仓→压舱石保留，L4 全清仓走 S1-06 绕过通道）；R1-03 护盘资产定向加仓白名单（三重门：L2/L3 状态+D110 超跌反转或国家队明牌信号+金字塔分批；宽基 ETF 优先，仓位上限总资金 5-10%；风险声明"政策底≠市场底"历史滞后 40 天~半年）。

## 2. 六向台账

### 2.1 输入面（有证）
- 图内入边：TDM-E-L0→TDM-X-R1（作战计划应急触发线）——图上唯一显式入边；实际触发源=风控事件（骨架行"上游=风控事件"）：R1-01 双轴判定读组合日盈亏+回撤（drawdown_state_machine 自身判定面）。
- 参数真源：config/crisis_gate.yaml（危机闸唯一配置真源，θ=warning_theta 0.5，CONSUMERS=zephyr.pf_alloc.crisis_gate 唯一读取方）+config/risk_params.yaml（风控参数真源 INV-002/003/013 三平面禁漂移）。

### 2.2 输出面（有证）
- 出边 10 条（横切广播面最广）：R1→F-C1-01（激活集清空=刹车接线，D125 注记）/→F-C2-01/→P2-01（禁做T）/→X-S1-06（强制清仓绕过）/→X-S2（全清）；R1-02→P2-04（减仓指令路由）；R1-03→E-L4（护盘加仓单）。
- 宪法 §7 速查入口：zephyr.security.access_control.kill_switch（系统级入口在册）。

### 2.3 SSOT 真源（有证）
- config/trading_decision_map.yaml#TDM-X-R1（line 4467-4520）+R1-01..03（line 4521/4573/4614）。
- config/crisis_gate.yaml（blueprint MOD-PA-CRISIS-GATE；缺文件=缺省值、解析失败/未知键/θ 越界=CrisisGateError 硬错禁静默降级）；config/risk_params.yaml（module_id=MOD-INF-002，canonical_source: true）。
- 考试卡 15 张（exit_flow/X1/ 实读——R1 考卡以 X1 目录承载）；UP-5 尾部对冲信号建议通道（2026-09-20 final3 P5：CVaR(5%) 破 -3% 日损阈值→对冲建议 DAL-TAIL-HEDGE，阈值冻结禁挪门柱）。

### 2.4 代码模块（有证，4/4 ref 实存）
- security/access_control/kill_switch.py（MOD-INF-018）；risk/core/drawdown_state_machine.py（MOD-RK-049 五级状态机）；risk/core/drawdown_liquidation_guard.py（MOD-RK-050）；position/core/defensive_asset_whitelist.py（MOD-POS-026）。
- 消费端实证：pf_alloc/crisis_gate（θ 唯一读取方）；宪法 §7 KillSwitch 速查行。

### 2.5 门禁约束（有证）
- 四门同前；本环节属 Owner 保留面直通位（宪法 §5：资金与实盘交易/L4 保命=Owner 人工接管，AI 熔断只降档不升档）。

### 2.6 自动化触发（有证）
- R1 本体/R1-01=continuous 常驻（kill switch 语义）；R1-02/03=intraday。
- 事件触发合规：熔断判定为事件驱动（双轴越限即触发），无常驻轮询线程（永久系统四要素）；宿主测试 tests/pf_alloc/test_crisis_gate.py、tests/ 域在册（crisis_gate.yaml TESTS 行）。

## 3. 自审闸三态

| 向 | 态 | 打分依据 |
|---|---|---|
| 输入面 | pass | L0 应急线入边+双轴自判+两参数册真源 |
| 输出面 | pass | 出边 10 条横切广播（刹车/禁做/清仓/减仓/护盘全接线） |
| SSOT | pass | 节点行+crisis_gate/risk_params 双册+15 张考卡 |
| 代码模块 | pass | 4/4 实存+消费端唯一读取方实证 |
| 门禁约束 | pass | 四门+Owner 人工接管门位 |
| 自动化触发 | pass | continuous 常驻+事件驱动合规 |

**总评：warn→pass 边界，判 pass（6/6，参数校准缺口见 §4）**。核心依据：六向证据链完整，θ 校准缺口属参数待定非缺证。

## 4. 缺口与建议

1. crisis_gate.yaml warning_theta=0.5 为"O1 待 Owner 校准（wo2_blackswan_workbook §2：建议 0.5 起步，月度演练回看误报率后定）"——参数校准议题在案未闭，建议入 Owner 月度演练排程。
2. R1 与 R1-01 双轴的职责分工（本体 kill_switch vs 五级状态机）在图上为父子但触发条件不同源（25%/-6% vs 五级日亏阶梯）——两套阈值的关系（谁先谁后/是否同一状态轴）未见对账注记，建议补一段映射声明防双轴打架。
3. 尾部对冲建议通道（UP-5，DAL-TAIL-HEDGE）挂在 R1 父节点 algo_note——但图上无对冲建议输出边（对冲工具本身缺位：PP-001 无对冲 sleeve 与 L1 euphoria 格禁用同源欠账 R2SIX）——建议与状态矩阵防御档议题合并立 Owner 议题。
