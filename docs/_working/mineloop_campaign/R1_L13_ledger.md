---
ttl: task_bound
title: L13 挖矿车道独占台账（复挖 TDM-P-FLOW / TDM-P-P1-01 / TDM-P-P2-04，st-mineloop-20261010）
created: "2026-10-10"
sid: st-mineloop-20261010
lane: L13
family_id: MENELOOP-CAMPAIGN
---

# L13 台账：复挖车道（前役 L4 自报封矿 3 节点）

任务书=`D:/ZephyrAlpha/.runtime/tmp/st-mineloop-20261010/MINING_BRIEF_R1.md`（唯一作业口径真源）。
前役凭据=`docs/_working/nightmine_campaign/L4_ledger.md`（st-nightmine-20261010 L4，position_flow 18 节点）。
SOP=mining_sop v1.8.0 §2 复挖硬门：自报封矿不自证，默认结论不可信。

## 0. 复挖对象与卡输出目录（layer 照该节点现有骨架件所在目录抄，已实核）

| node_id | 现有骨架件（真源目录） | 前役 L4 已出卡 | 本车道输出目录 |
|---|---|---|---|
| TDM-P-FLOW | `docs/03_modules/_domain_backtest/exam_cards/position_flow/PFLOW/TDM-P-FLOW__ablation.yaml` | `TDM-P-FLOW__ablation__02_持仓叠层整链消融.yaml`（1 卡） | `.aidrafts/st-mineloop-20261010/docs/03_modules/_domain_backtest/exam_cards/position_flow/PFLOW/` |
| TDM-P-P1-01 | `.../position_flow/P1/TDM-P-P1-01__comparison.yaml` | `TDM-P-P1-01__comparison__02_复权口径对成本与生死线触发对照.yaml`（1 卡） | `.../position_flow/P1/` |
| TDM-P-P2-04 | `.../position_flow/P2/TDM-P-P2-04__comparison.yaml` | `__comparison__02_调仓频率与换手惩罚六臂对照.yaml`、`__ablation__03_置换两倍成本门与风控优先腿消融.yaml`（2 卡） | `.../position_flow/P2/` |

> 注：任务书提示"本仓已有 `exam_cards/portfolio_flow/` 目录"。实核结果：portfolio_flow 承载 TDM-F-* 节点（C1/C2/C3/CFLOW），
> TDM-P-* 三节点骨架件全在 `position_flow/`，故 flow 目录取 position_flow（判据=骨架件实际所在，非凭记忆）。

## 1. 六向复挖台账（逐节点一行，机读优先）

| node_id | ①上游 | ②下游 | ③算法 | ④后端 | ⑤呈现 | ⑥数据 | 新卡数 | 族分布 | mined_out? | blocked 原因 |
|---|---|---|---|---|---|---|---|---|---|---|
| TDM-P-FLOW | ★漏 strategy_mounts 两支腿带在册 OOS 证据（098 IS0.518/OOS0.156、099 IS0.397/OOS0.404）→立卡；前役记"仅结构指向"不成立 | ★edges 全仓 grep：入边仅 1 条（L6378 P3→FLOW），P1/P2 未接入流根，与 algo_note_zh 三腿叙事冲突→立卡；出边零（与"终点"一致） | 同族近亲=PFLOW/ablation/02（overlay 维，对象不同不并）；机构三件套映射=响应(臂增益)/条件稳定(牛熊同号)/时滞(腿开闭即时性) | 后端实核：_apply_exit_overlay 调用点 L838、_apply_dd_breaker_overlay L841、_apply_capital_ramp_overlay L1058 且 K 受 DEFAULT_CONTEXT 折叠；grid schema 无 strategy_ref 腿开关维 | 只登记：持仓动作清单在 live 仪表盘呈现 | kline_daily_hfq 1990-12-19..2026-09-30/10,098,785 行（在册）；strategy_screen 全名/行数=待总包 22:30 后实测 | 2 | comparison×1 + ablation×1 | **否（推翻封矿）** | 两卡均 blocked_on_impl（缺策略腿开关维 + 缺做T 腿注入件） |
| TDM-P-P1-01 | ★漏入边 L6263 E-L4-10→P1-01（订单九态 feed），且 E-L4-10 invalidation 原文"必须以交易所回执为准"=第二套入账口径→立卡；★fallback"T-1 快照沿用"独立失真面前役未考 | 下游 edges：P1-01→{P1-02,P1-03,P1-04,P1-05} 四条（L6274-6277）+消费件 position_checkup_orchestrator.py:298、trading_day_cycle_map.yaml:2155（D13-27 与 TDM-E-L4-13 同格）——前役只记"依赖链"未记级联失真判据，已并入本车道卡 pillars | ★码内实读 position_state_machine.py:91-100 PositionState **七态**（NONE/BUILDING/ACTIVE/OBSERVING/REDUCING/EXITING/CLOSED）vs TDM 原文"状态机态（六态）"=口径冲突；灰度 5/20/50/100% 与冷却 5 日常数在册 | 后端：module_ref=position_state_machine.py(MOD-POS-002) 在码；X-R1-02 module_ref=drawdown_liquidation_guard.py 实读只有撤单率红线(0.12/0.15)+清仓超时 30s，**无台账重放/双臂口径件** | 只登记：不平账标红人工核对（运维面，判 D 类不进回测） | DS-009/DS-067=本地账务件非 CH（registry L1081/L3144，前役已证，本车道复核行号）；价格面 kline_daily/hfq/adj_factor 在册；回执表覆盖=待总包 22:30 后实测 | 2 | comparison×1 + calibration×1 | **否（推翻封矿）** | 两卡均 blocked_on_impl（缺双臂失真件——即前役在册清单点名项；另需态重放件） |
| TDM-P-P2-04 | ★漏入边 L6352 X-R1-02→P2-04（梯度减仓序"重亏→高波动→压舱石最后"+恢复"修复 50% 逐级加回、禁 V 型回满"，TDM L3777-3778/L3791-3792，裁定#227 D113 在册原文）；★漏 risk_limit_refs=[RLM-POSITION-011]（registry L777-793：反弹冲高减半转进攻仓，阈值 50%，param_origin=经验拍定，breach_action=warn） | 下游 edges 精确化：P2-04→X-S2（L6292）、→X-S2-01（L6293）；X-S2-01 原文三查（单笔≤买一档量/日量×10% 参与率/市值÷20 日均额>1% 禁市价）=减"多少"的可行性上界，前役未取 | DAL-GRADIENT-TRIM（decision_algo_registry.yaml L103-109，status=design、code_ref=null）＝算法册自认无代码锚；机构三件套=响应(排序键剂量)/时滞(减不到位的完成天数)/条件稳定(牛熊+流动性分层) | ★实现落点错位：梯度减仓序实现在 X 流 `sell_decision/services/exit_execution_orchestrator.py:8,32,797,803`（含 is_defensive_ballast 字段），而 P2-04 module_ref=rebalance_engine.py 只有 expected_improvement/transaction_cost/improvement_ratio 三字段（L126-128）；grid 无排序键维、无"回撤修复比例触发加回"档（K 仅 lump/linear_20d/60d/pyramid） | 只登记：减仓指令清单（人工确认降级通道=fallback 原文"再平衡引擎不可用→减仓指令降级人工确认"） | hfq amount（20 日均额可算）/technical_indicator 在册；TI 读取须 argMax/FINAL 去重（不去重=panel IC 放大 30 倍，任务书 §3）；宇宙口径雷（创业板 2026-08-14 起、北交所 2026-09-15 起）已入卡 | 4 | ablation×1 + comparison×1 + calibration×2 | **否（推翻封矿）** | ablation/comparison 两卡 blocked_on_impl（缺排序 overlay+修复比例加回档）；calibration 卡 preregistered |

### 1.1 复挖证据（逐向，前役"封矿不自证"的推翻凭据）

- **前役封矿理由原文**（L4_ledger.md §二）：TDM-P-FLOW="六向齐，长尾=本流日频做T平面归 P2，无他漏"；
  TDM-P-P1-01="D 类可考面已榨取：口径失真面已入卡，台账本体无回测平面"；
  TDM-P-P2-04="四条判据逐条入卡，其中两条落 blocked_on_impl；无剩余长尾"。
- **推翻点 1（P-FLOW）**：前役①上游句"无 data_refs/factor_refs"→据此判"仅结构指向"，但同一节点块的
  `strategy_mounts` 非空且带 IS/OOS Sharpe 证据；edges 面 P1/P2 根本没有边接入流根（前役未查 edges 入边完备性）。
  两处都是节点级未挖长尾，非扩档。
- **推翻点 2（P1-01）**：edges L6263 有一条**跨流入边**（E-L4-10 订单九态）指到本节点，前役①②向均未记；
  该边的 payload 语义（回执 vs 本地终态）恰好是本节点"股数/成本"的地基口径，属可判失真面。
  另 fallback"T-1 快照沿用"与 TDM"六态"vs 码内七态两处未入册面。
- **推翻点 3（P2-04）**：前役记了三条判据（漂移越带/置换 1.5×/改善>2×成本/风控优先），但漏
  ①X-R1-02 路由来的**梯度减仓顺序**（D113/裁定#227 在册，且实现实际住在 X 流件里=路由断点）、
  ②**恢复节奏**（修复 50% 阶梯加回 vs 禁 V 型回满——引擎无该档）、
  ③唯一在册风险限额 RLM-POSITION-011（阈值 50%、经验拍定、只 warn）、
  ④下游 X-S2-01 参与率三查对"减多少"的可行性上界。四条皆新对象，非扩档。
- 在册清单点名的真缺口（据此把新卡标 blocked_on_impl 并写死缺什么）：
  P1-01/02=缺复权口径可切换的双臂失真件（本车道延伸为"缺入账口径双臂失真件"）、
  P1-02/03=缺双臂分级统计件、P2-04/03=缺按 improvement_ratio 裁剪动作+优先权开关。

## 2. 车道收尾账

- **本车道节点总数**：3（全部为复挖对象，前役 L4 自报 mined_out）。
- **复挖结论**：**三节点封矿全部推翻**（各条证据见 §1.1，均为"节点级未挖长尾"，非扩档）。
- **新卡总数**：8（全部只新建文件，零触碰已存在卡件/骨架件；NN 接续现有编号 PFLOW→03/04、P1→03/04、P2→04/05/06/07）。
  机检（本车道实跑，只读校验不写盘）：8/8 YAML 可解析，必填面齐
  （schema_version/card_id/node_id/family/title_zh/hypothesis/window 四件/buckets 三件/pillars/
  pillars_numeric/target.primary+secondary/status/lineage.confidence_writeback/signal_kind/
  executor/data_binding 四子项；无 `generated: true`；preregistered_by 全为 st-mineloop-20261010-L13；
  signal_derivation 零"或"字未择一）。
  - **族分布**：comparison 3 / ablation 2 / calibration 3。
  - **status 分布**：blocked_on_impl 6 / preregistered 2 / blocked_on_data 0。
  - 逐卡清单：
    | card_id | status |
    |---|---|
    | TDM-P-FLOW/comparison/03_挂载策略腿OOS强度分层对照 | blocked_on_impl |
    | TDM-P-FLOW/ablation/04_三段子环并入完备性消融 | blocked_on_impl |
    | TDM-P-P1-01/comparison/03_回执与本地台账入账口径双臂失真 | blocked_on_impl |
    | TDM-P-P1-01/calibration/04_状态机态序与滞留天数对次日收益预测 | blocked_on_impl |
    | TDM-P-P2-04/ablation/04_梯度减仓顺序与无排序双臂消融 | blocked_on_impl |
    | TDM-P-P2-04/comparison/05_熔断后回撤修复阶梯加回与即时回满对照 | blocked_on_impl |
    | TDM-P-P2-04/calibration/06_减仓参与率压力对次日价格路径 | preregistered |
    | TDM-P-P2-04/calibration/07_冲高反弹幅度对次日收益与减半阈值落点 | preregistered |
- **blocked_on_impl 缺件写死（每条含 needed_interface，禁"缺件"两字交差）**：
  1. 按 strategy_ref（TDM strategy_mounts）开闭信号腿的 grid 维 + 腿级 IS/OOS SR 重算器（SR 口径复用 window_metrics）。
  2. 做T 腿注入 grid 的重放开关（输入 S13 臂 NAV + 做T 命中日净 bp，输出 S123 NAV；成本复用 COMMISSION_RATE 与 t0 件 31.2bp）。
  3. **缺双臂失真件**（前役在册点名项的本车道延伸）：回执口径 vs 本地委托终态可切换的台账失真统计件 + T-1 快照沿用注入开关（三方对真值台账，禁两臂互比）。
  4. 日线平面台账态重放件（按 PositionStateMachine._transition 同一转移表产出 (symbol,date,state_ordinal,dwell_days)，禁另写一套）。
  5. 按排序键分配减仓动作集的 rebalance-order overlay（排序函数复用 exit_execution_orchestrator.py L803）+ 5 日前向窗口指标。
  6. 按回撤修复比例触发的阶梯加回档（recover-50% ladder）+ X_breaker 帽带逐级解除腿；K 维开闸属配置位。
- **未挖长尾明列（本车道三节点，不作封矿）**：
  1. P-FLOW：流根出边=零（全仓 grep 确认），"持仓动作清单→交易员采纳"的呈现面判为不可回测平面，只登记。
  2. P-FLOW：若边表补 P1→FLOW、P2→FLOW 两条入边，本车道 ablation/04 的臂语义须重定义（治理前置，考卡不代改图）。
  3. P-FLOW：strategy_screen 表全名/覆盖窗/行数、两 CAND（CAND-5301c5d9d7c8 / CAND-8664521af1a0）在册面=
     `data_window_evidence: 待总包 22:30 后实测`（21:00–22:30 禁 CH 重查询，本车道未跑）。
  4. P1-01：六态（TDM 原文）vs 七态（码内 PositionState 七成员）口径冲突已作为卡的治理产出登记，
     但"文档-代码一致性"本身属治理门，未立考卡。
  5. P1-01：module_mounts 四件（MOD-POS-006/009/020、MOD-TRADING-002）逐件能力核查未做（本车道只实读主 module_ref）。
  6. P1-01：真要考"对账"本体需 QMT 桥文件可得性日志入仓（本地账务面 data 侧立项），非考卡可解。
  7. P2-04：减半**比例** 50% 的剂量双臂卡（25/50/75% 三臂）未立——与 ablation/04 同一缺件位；本车道 calibration/07
     明确只考择时面，不代拍比例。
  8. P2-04：/07 卡用 ATR% 三分位代理"弱 beta"，真 beta 计算件未核（已在卡内 ballast_subgroup_gate 如实披露）。
  9. P2-04：X-R1-02"逐级"档数本卡按引擎既有三档钉死；live 侧若另有定义须先对齐再开考。
  10. 跨节点：P2-04↔P1-05 漂移带口径冲突（TDM 25% vs 引擎 thr=0.10*2.0）沿用前役在册卡，本车道不重复立卡。
- **交叉复挖建议（20%≈1 节点，另附 1 条跨流路由项）**：
  1. **TDM-P-P1-06 / TDM-P-P1**（前役亦自报封矿）：本车道查明 edges 面 `TDM-P-FLOW` 的唯一入边来自 P3，
     而 P1-06→P3-01 有边、P1→FLOW 无边 ⇒ P1 汇总结论的第二条出路未查清，建议 P1 族复挖者按六向重查
     （与本车道 TDM-P-FLOW/ablation/04 直接互证）。
  2. **TDM-X-R1-02**（X 流）：梯度减仓序的实现在 `sell_decision/services/exit_execution_orchestrator.py:8,32,797,803`，
     而算法册 DAL-GRADIENT-TRIM 自记 `code_ref: null / status: design`，且 X-R1-02 的 module_ref
     `risk/core/drawdown_liquidation_guard.py` 实读只有撤单率红线（0.12/0.15）与清仓超时 30s
     ——三处说法不一，建议 X 流复挖者裁"实现归 X、叙述归 P2-04"的路由断点该改哪一侧。
- **假绿风险自报（禁报"全部完成"）**：
  1. 本车道两张 preregistered 卡的 primary 都是"次日收益"（现器 shift(-1) 能力面），
     显著≠执行失真/限额有效为真——两卡各写了 proxy_honesty / 不代拍比例的前置，仍须防读数时被当成结论。
  2. 在册背景=已考 18 行全 fail（任务书 §3）⇒ 持仓面新卡大概率 fail；
     fail 是考出来的结果，不得被读成"矿已挖尽"，三节点的未挖长尾已逐条明列。
  3. 六张 blocked_on_impl 卡若被误当 preregistered 送考，run_card 硬读 status 会拒（前役实读），
     但台账与分数册须按 status 面统计，防"8 张全可考"的假绿。
