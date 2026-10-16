---
ttl: task_bound
doc_type: tdm_mining_note
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
skeleton_row: TDM-F-C1
flow: portfolio_flow
node_count: 4
session: mine-fullchain-tdm-20261015
---

# S_TDM-F-C1 预算切分（4 节点）

## 1. 定义

一句话：Millennium pod 模式——总仓位预算（L1 预算带）按 sleeve 权重切分（PP-001 配置），各 sleeve 账本独立、风险独立核算、互不挪用，sleeve 间资金流动只通过月度调权（C3-03）。

展开：本环节=组合流入口 gate，四节点：C1 本体=multi_strategy_capital_allocator（MOD-PA-003，含 UP-3 前瞻风险预算建议通道：各 sleeve 预测 VaR(5%)/CVaR 作带内再分配）；C1-01 策略路由判定（D125 2026-10-05 Owner 批：输入=L1-AGG 体制态+state_matrix 格子+fitness，cells=路由查表真源，X-R1 熔断触发时激活集清空=刹车接线）；C1-02 权重分配（D125 分配器治理=冠军-挑战者：在位冠军=三层栈 RK-08 风险预算地板+PA-015 体制倾斜+SIG-131 步长运动学，影子挑战者=集成平均版/单算法简化版，PF-008 序贯统计晋升）；C1-03 灰度切换管理（D125：双向 weight_band 爬坡步长上限 step_cap 0.2+紧急态硬切例外）。PP-001=16 sleeve 权重表（打板 0.0945/多因子 0.126/事件 0.063…合计 1.0，aggregator 三约束 max_total_position=1.0/max_single_sleeve=0.25/correlation_cap=0.7 实读）。

## 2. 六向台账

### 2.1 输入面（有证）
- 入边：TDM-E-L1-AGG→C1/C1-01（预算带+体制态）；TDM-X-R1→C1-01（熔断清激活集）；TDM-F-C3-03→C1（月度调权回写——sleeve 间资金流动唯一通道）。
- 上游段外：FAC-E8 组装（骨架行"上游=E8 组装"）经 graduated 卡与 position_recipe_grid_schema.yaml 仓位配方衔接（骨架 §2.1 行+E8 行）。

### 2.2 输出面（有证）
- 出边 4 条：C1→C2（sequence）、C1→C2-04（budget 变动三级升级入口）。
- portfolio_plan PP-001：16 sleeve+aggregator 三约束在地图 portfolio_plan 块实读；C1-01 路由查表真源=state_matrix cells（24 格）。

### 2.3 SSOT 真源（有证）
- config/trading_decision_map.yaml#TDM-F-C1（line 5225）+C1-01..03（line 5270/5301/5332）；portfolio_plan 块（plan_id=PP-001，name_zh=整装仿真组合 V0，confidence=proposed）。
- 参数册：config/position_recipe_grid_schema.yaml（schema_id=position_recipe_grid_v2，17 维条件参数空间，名义 N_raw=362,880/全激活 11,612,160 实读）——sleeve 级考卷面真源。
- 考试卡 10 张（portfolio_flow/C1/）；goal 挂 F14_组合反馈C3 系。

### 2.4 代码模块（有证 1/4，缺口 3 节点）
- C1 本体：src/zephyr/pf_alloc/core/multi_strategy_capital_allocator.py（MOD-PA-003）实存。
- C1-01/02/03：module_ref=None——地图 INV-1 明文 null=缺口节点（warning 级），三节点为 D125 治理设计已裁（Owner 2026-10-05）但实现锚未挂：策略路由/权重分配/灰度切换当前散在 pf_alloc 包（allocation_inputs.py load_pp001_plan、regime_meta_allocator.py 等）无节点级锚。

### 2.5 门禁约束（有证）
- 四门同前；D125 三子节点落地时受 TDM-MOUNT-COVERAGE 强制（新 .py 须挂载裁决）；预算变动走 C2-04 三级升级（防踩踏纪律在 C2 册）。

### 2.6 自动化触发（有证）
- C1/C1-01/02=premarket；C1-03=intraday（灰度爬坡盘中步进）。
- dloop 链明文：zephyr.pf_alloc.allocation_inputs(load_pp001_plan)+pipeline_events(maybe_emit_pf_alloc_daily)——分配随日循环自动圈；月度调权归 C3-03 盘后批。

## 3. 自审闸三态

| 向 | 态 | 打分依据 |
|---|---|---|
| 输入面 | pass | 预算带/体制态/熔断刹车/月度调权四路入边+E8 衔接 |
| 输出面 | pass | →C2 双边+PP-001 16 sleeve 权重表+aggregator 三约束 |
| SSOT | pass | 节点行+PP-001 块+grid v2 参数册+10 张考卡 |
| 代码模块 | fail | 3/4 节点 module_ref=None 地图声明缺口节点（C1-01/02/03 D125 设计已裁未落锚）——本环境唯一空壳簇 |
| 门禁约束 | pass | 四门+落地时强制挂载 |
| 自动化触发 | pass | dloop 双挂点+月度调权通道 |

**总评：warn（本体有锚有边非断链；代码模块向存在 3 节点空壳簇=地图在册声明缺口）**。

## 4. 缺口与建议

1. 【本段最大实现缺口】C1-01 策略路由判定/C1-02 权重分配/C1-03 灰度切换管理三节点无 module_ref——D125（2026-10-05 Owner 批）只裁了治理设计未落实现锚；建议立施工工单：三层栈冠军分配器（RK-08+PA-015+SIG-131）+PF-008 序贯晋升检验器落 pf_alloc 包并回挂三节点 MOD 锚。
2. PP-001 confidence=proposed 且 name_zh=整装仿真组合 V0——组合本体仍在仿真档，实盘预算切分未启用（与 D13-34 毕业包恒空→无实盘同族）；建议保持 proposed 不冒充 verified（宪法 §7 纪律）。
3. C1-01 路由 fitness 与 P3-01 门③策略亲和度是否同一算法未对账（见 P3 册 §4.3）——D125 落地批统一。
4. 骨架总纲写 C1=4 节点与实读一致；但骨架写 C2=6 实读 5（漂移在 C2 册记录）。
