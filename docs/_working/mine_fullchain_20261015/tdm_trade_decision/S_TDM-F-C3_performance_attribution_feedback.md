---
ttl: task_bound
doc_type: tdm_mining_note
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
skeleton_row: TDM-F-C3
flow: portfolio_flow
node_count: 6
session: mine-fullchain-tdm-20261015
---

# S_TDM-F-C3 绩效归因反馈（6 节点）

## 1. 定义

一句话：系统自我进化的发动机（PT-10"策略会过期"+PT-11"每个决策留证据"）——多维归因（哪赚哪亏为什么）→升降级评审（sleeve 维持/减半/清退/重审）→权重调权→参数校准→传感器可靠度反馈 L1，赚的加码亏的减码全部凭数据不凭感觉。

展开：C3-01 多维归因引擎（几何 Brinson 三因子：配置/选股/交互效应+做T vs 持仓盈亏二分+IS 三分解延迟/冲击/机会成本；月度跑）；C3-02 升降级管线（月度评审+季度 verdict 四选一评审制人工裁定不自动退役；THD-RETIRE 三线=滚动 20 日跑输基准 5%/60 日 Sharpe<0/回撤漂移 1.5×；单 sleeve 回撤 5% 自动减半、7.5% 冻结这条自动执行不等评审）；C3-03 sleeve 权重调权（月度公式新权重=normalize(基准权重×PerfScore×Shrinkage) 下限 5% 上限 40%；危机覆盖 WO-2a：is_crisis 或 crisis_floor_active→floor 0.09 降至 0.05，θ 真源 config/crisis_gate.yaml）；C3-04 参数校准闭环（四道 gate：CPCV+DSR+PBO<30%+参数平台期；WFE>60% 可用 <40% 禁上线；purge 窗=持仓半衰期 embargo≥5 日）；C3-05 可靠度养成（三档递进：等权起步→月度判准率加权下限 10%→粒子滤波远期；滚动 IC+半衰期拟合衰减>50% 报警反馈 L1-AGG 降权——大盘判定器自己也要被考核）。

## 2. 六向台账

### 2.1 输入面（有证）
- 入边 5 条：TDM-E-L3-08→C3-01（候选池归因）、TDM-E-L4-13→C3-01（容灾对账）、TDM-P-P2-03→C3-01（做T统计）、TDM-X-S2-06→C3-01（离场三率）、TDM-E-L9-E2→C3-02（验证结论回传）。
- 段外回灌：FACTORY E9 实盘归因（骨架 §2.1 行"TDM-F-C3 回流→E9"）经 feedback_loop 包承接（src/zephyr/feedback_loop 实存）。

### 2.2 输出面（有证）
- 出边 12 条：C3→TDM-E-L1-AGG（可靠度反馈）、C3→TDM-F-FLOW（流根）；C3-01→TDM-E-L0（昨日归因喂作战计划——跨日闭环正门）、C3-03→TDM-F-C1（月度调权——sleeve 资金流动唯一通道）、C3-04→TDM-E-L0（参数校准回喂）、C3-05→TDM-E-L1-AGG/TDM-E-L2（传感器降权广播）。
- 考试卡 13 张（portfolio_flow/C3/）。

### 2.3 SSOT 真源（有证）
- config/trading_decision_map.yaml#TDM-F-C3（line 5396）+C3-01..05（line 5623/5674/5734/5793/5854）。
- casebooks 挂 6 处（CASEBOOK-005#实盘衰减与归因/CASEBOOK-009#红证 族域——本环节为证据翻账主位）；goal 块 family=F14_组合反馈C3（output_contract="归因报告＋升降级管线"）。
- 阈值族（THD-RETIRE 三线/回撤 5% 减半 7.5% 冻结/floor 0.09→0.05）在册于节点 algo_note——散文化程度为全段最高（见 §4）。

### 2.4 代码模块（有证，5/5 子节点 ref 实存）
- pf_core/core/performance_attribution_engine.py（MOD-PF-007）；factor/governance/lifecycle_state_machine.py（MOD-L02-013）；pf_alloc/core/regime_meta_allocator.py（MOD-PA-007）；backtest/core/walk_forward.py（MOD-BT-001）；signal_quality/signal_degradation_monitor.py（MOD-SIGQC-004）。
- 协同包：src/zephyr/feedback_loop、reporting 实存（骨架行代码指针；未直接挂节点 module_ref，见 §4.3）。
- 父枢纽 TDM-F-C3 无 ref（结构枢纽，INV-1 允许）。

### 2.5 门禁约束（有证）
- 四门同前；C3-04 四道 gate（CPCV/DSR/PBO/平台期）=参数修改的前置学术门（对应 CASEBOOK-005#考试纪律 簇）。

### 2.6 自动化触发（有证）
- 全环节 activation=盘后 postmarket；月度批（C3-01/02/03）+滚动监控（C3-05）。
- dloop 链：三表结算后归因供数就绪（L4-13/P2-03/S2-06 盘后产物）；月度批宿主=盘后批群（图13-D13-35 骨架行）；FACTORY E9 消费 feedback_loop（骨架 §2.1）。

## 3. 自审闸三态

| 向 | 态 | 打分依据 |
|---|---|---|
| 输入面 | pass | 五源入边（候选池/对账/做T/离场/验证回传）全在册 |
| 输出面 | pass | 出边 12 条：回 L0/L1-AGG/C1 三闭环正门全接 |
| SSOT | pass | 节点行+casebooks 6 处+13 张考卡 |
| 代码模块 | pass | 5/5 实存；feedback_loop/reporting 包存在但未挂节点锚 |
| 门禁约束 | pass | 四门+C3-04 四道学术 gate |
| 自动化触发 | pass | postmarket+月度批+滚动监控三档 |

**总评：pass（6/6）**。

## 4. 缺口与建议

1. 阈值散文位全段最高：THD-RETIRE 三线/5% 减半/7.5% 冻结/floor 0.09→0.05/WFE 60%/PBO 30% 等关键门柱全在 algo_note 散文——按宪法 §4.5"静态清单禁手工维护+计数用字段"精神，建议参数册化（risk_params.yaml 或新建 attribution_thresholds 册，净零新增须声明替代），使月度评审有机械判据。
2. skeleton 代码指针"src/zephyr/feedback_loop、reporting"与地图节点锚（pf_core/pf_alloc/factor/backtest/signal_quality）不一致——feedback_loop 包实存但零节点引用，建议下批骨架修订或给 E9 补挂 feedback_loop 锚，消包级悬空。
3. C3-03 危机 floor 依赖 is_crisis（dominant==r10）判定——该判定在 pf_alloc.crisis_gate（θ 消费方）与 R1-01 五级状态机两处有状态语义，与 R1 册 §4.2 双轴对账议题合并收口。
4. 升降级评审（C3-02）为"评审制人工裁定不自动退役"——Owner 门位（业务资产概念级退役=轨 B Owner，宪法 §5）合规；但"回撤 5% 自动减半"与评审制的边界（自动腿/评审腿）建议在节点注记显式拆分防误读为全自动退役。
