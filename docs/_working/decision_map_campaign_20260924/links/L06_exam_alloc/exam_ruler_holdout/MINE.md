---
ttl: task_bound
title: L06-子模块 考尺与 HOLDOUT 闭卷（E4 三阶段三线裁决 / 三道成本门 / 四窗烧毁纪律）挖干
created: 2026-09-25
sid: st-qmine-20260925
lane: L06_exam_alloc
status: SEALED-CORE（六向内部反查全填、③向外部双源；冻结考尺件只登记不改）
skeleton_source: ../SKEL.md L06-C/L06-D；../../09_link_skeletons.md 环节6；判据 ../../17_quantified_acceptance.md §一
doc_role: L06 挖矿子模块 MINE（覆盖 SKEL L06-C 考尺 + L06-D HOLDOUT 闭卷）
---

# 子模块 · 考尺与 HOLDOUT 闭卷（exam_ruler_holdout）

> 考试机器"考"的半边：幸存者配方过 E4 三阶段正考（IS→WFA→OOS）+ 三道成本门 + 条件轴输入包；
> HOLDOUT 四窗制守样本外诚实。⚠ 冻结件 `config/exam_scale_cost_gate.yaml` 只实测现状、不改。

## ① 职责一句话
用预注册冻结考尺把幸存者配方判成"通过/存疑/不通过"三线裁决，成本焊进考尺（五档全真跑），
并以单次烧毁的闭卷窗守"成绩不是调出来的"。

## ② 现状实测（代码 file:line + 冻结件数值 + 数据可得性）

### E4 三阶段考尺（scripts/backtest/f06_e4_wfa_exam.py）
- INVARIANTS（:8）判定逻辑零重写：IS→WFA→OOS 三线裁决委托 `strategy_validation_pipeline`+`DecisionGate`+`OverfittingDetector`；折切分无泄露（`build_folds` 每折训练窗早于测试窗、测试窗互不重叠）；DSR 由 MOD-SIM-024 预计算注入 fail-closed（注入失败判不通过）。
- 三线 verdict 映射（:26-27,67-69）：通过=三阶段全过∧无过拟合；不通过=WFA 未过/灾难回撤/OOS 比率<0.70/DSR 否决带；存疑=DSR 中间带或 WFA 60% 稳定性边际未达而其余全过。
- **RB-STATS-01 证据充分性闸**（:8）：DSR 折减分母 N_eff 未从批次档案对账复算（非 verified）**或** 过拟合三维未评满 ⇒ **禁判"通过"（最多存疑）**；历史伤疤实证=*"实测纯噪声 N=1 时 DSR=0.9986 曾判通过，一列改字即放水"*。`OVERFIT_DIMENSIONS_TOTAL=3`（:57）——**SKEL L06-C ⑥：三维中仅评 1 维（参数扰动/跨时段维未评）** ⇒ 按 RB-STATS-01 现况全部只能落"存疑"（闸自洽，但等于考尺尚未能出"通过"，本块新立观察）。
- 消费面/触发：**回测侧在产**——正考档案 `data/backtest_artifacts/runs/E4-F06-38b453ca/`（verdict.md+summary.json，:5/:36）；`SURVIVORS_CSV=data/strategy_intake/f06_survivors.csv`（:59，实测存在）。

### 三道成本门（exam_cost_gate.py，MOD-BT-IBT-COSTGATE）
- 门①五档单调非增（逐档 sharpe 非增，`DEFAULT_MONOTONIC_TOL=1e-9` :46）；门②全成本档存活（最高档 40bp sharpe≥survival_floor 预注册 0.0 :22-23）；门③E7 换手上限门（年化单边换手≤8x/年，Owner 通宵令批 C 预注册档冻结后禁改 :24-26）。
- fail-closed（档位<3/天数<min_days=不通过非跳过）；裁定#325 口径出证禁"全绿"逐条如实（:8,:29）；扫描/判定两面分离（run_cost_tier_scan 子集仅供 T1 轻档扫描，判定恒全档证据）。照妖镜=4440 超短频繁交易必被拦（:28）。

### 条件轴输入包（condition_package.py，MOD-BT-COND-PACKAGE，stability=experimental :16）
- 情绪灰度五档边界冻结 (0.2,0.4,0.6,0.8]=冰点/降温/温和/升温/沸点；**实测冰点 0 日⇒闭卷窗内实为四档**（空档如实剔除 :8）。
- 状态轴真源=c1_market.alt_regime_signal（键 `signal_date`，与情绪轴 `trade_date` 不同名，实测 Code 47 坑）；选族 `signal_id='F4_BDI_MOMENTUM_Z20'`（neutral/risk_on/risk_off 三态；自纠 uniqExact=5 系三族混合 F11 猪周期/F14 BTC 非市场状态，:28-30）。
- 条件胞=灰度档×状态档，30 交易日地板；**闭卷窗 1,622 交易日**（:24），band5 分布 cooling 120/mild 594/warming 654/boiling 253；搜索窗=闭卷 [2019-01-04,2025-09-09] 窗外禁入（closed_book :48）。
- **板块轴 observational-only 禁入统计判据**（实测仅 17 交易日，`columns_forbidden=[capital_score,net_inflow_pct]` 以"不加载"执行 :8）——条件轴板块维数据不可得实锤。

### HOLDOUT 四窗制（真源=IBT-PROTOCOL-V1.md §3）
- W_IS 可多次 / W_OOS 准样本外 / W_HOLDOUT [2025-09-09 冻结单次烧毁] / W_POSTD 前向（SKEL L06-D ①）；D=2026-09-09 切点。
- 首跑 W_HOLDOUT 已单次烧毁 IBT-A -12.24%/Sharpe -1.389→C 门不过（IBT-CAMPAIGN-LEDGER.md §3，SKEL L06-D ③）；批 D 用掉原 HOLDOUT 后"最终盲窗=2026-09 之后前向段"。
- **grep `W_HOLDOUT` 于 backtest_system_sop 目录 = 查无**（四窗定义在 IBT-PROTOCOL-V1.md，非 exam_policy 域，记查法）。

### 冻结件数值实测（config/exam_scale_cost_gate.yaml，只读）
- `tiers_bp:[0,5,10,20,40]`、`survival_floor:0.0`、`min_days:60`、`turnover_gate cap 8x`、`primary:cost_adjusted_sharpe`、`cost_adjusted_sharpe`、`turnover 8x/244 日`（:11-26）——**判据件，禁擅改**。

## ③ 六向台账（内部 + 全网双动作）

| 向 | 内部反查发现 | 全网外部反查 |
|---|---|---|
| ①上游 | 幸存者配方（f06_survivors.csv / recipe-id 缺省 38b453ca3683）；考试政策准入四条 exam_policy §1；预注册参数 exam_scale_cost_gate.yaml；条件包输入 | 机构对照=Walk-Forward（Pardo WFE≥0.5 行业线，17 §三.2 已锁）；DSR/haircut/PBO 判据族（见 `../search_executor_prereg` ③，不重引） |
| ②下游 | C4→注册表升降级（strategy_registry 161=19active+139candidate+3deprecated，SKEL L06-C ④）；TDM-E-L9-E2 结论回传（red_reason=pending_gate）；C3-02 退役评审；成本合格名单→整装 v2 池基（IBT-B04）；`exam_cost_reexam.py`（批 D 新鲜窗重过成本门，consumers :5） | 待外部（升降级/上岗消费链见 onboarding 块） |
| ③算法/机制 | E4=IS/WFA/OOS 三线 + OverfittingDetector 三维（仅评 1 维现状）；RB-STATS-01 自洽闸；条件轴=情绪灰度×大盘状态双层（Owner 2026-09-23 夜裁决①分层口径 :17）；30 日地板禁凑 n | **≥2 源**：① MDPI Mathematics 2026 "Point-in-Time Backtesting of Momentum-Trend Equity Strategies"（mdpi.com/2227-7390/14/12/2182）——PIT 无泄露回测=E4 build_folds 无泄露 + w.shift(1) T+1 因果同构；② arXiv 2406.09578 regime-switching（2024）——条件状态分层对表。A 股适配闸：E4 回测口径复用 _c4_engine 冻结土规 T+1（w.shift(1)）+ 五档成本含滑点/印花税，适配通过 |
| ④后端 | 治理级考试循环零样本=IBT-E01（exam_result 写入/reexam/三取二，→ `../exam_result_writeback` 块）；WFA 三维仅评 1 维未补（参数扰动/跨时段维）；批 D 新鲜名单产物仓内未见（IBT-F01，池基悬空） | 开源对表（SKEL §9）：skfolio CombinatorialPurgedCV/pypbo（CPCV/PBO，LK-08 接线，本块登记）；mlfinlab（AFML ch.12 语义对照，零引入） |
| ⑤前端 | E4 verdict.md/summary.json 为人读产物，无看板；成本门逐条证据无 UI（登记边界） | 已查无：考尺结果无 dashboard 源；不越界 |
| ⑥数据字段 | **两处"字段在≠可得"实锤**：情绪冰点档边界在、闭卷窗内 0 日（四档非五档，:8）；板块轴列在、仅 17 交易日被 `columns_forbidden` 禁加载（:8）⇒ 条件胞网格的冰点行/板块维无数据；alt_regime_signal 键 `signal_date` vs emotion `trade_date` 不同名（Code 47 坑已修） | 待外部反查（条件胞地板 n 阈值业界口径，记"已查无标准+查法=对比策略容量 n 门文献"） |

## ④ 缺口清单（沿用 + 续编）

| 编号 | 缺口 | 册内可见性 | 状态/解锁 |
|---|---|---|---|
| IBT-E01 | 治理级考试循环零样本（exam_result 写入/reexam/三取二） | SKEL L06-C ⑤ | 挂起；→ exam_result_writeback 块，解锁=考卷 exam_plan 结构化冻结 |
| IBT-F01（P0） | 批 D 新鲜窗重考产 fresh 名单（现网搜旧 15 员族） | SKEL L06-D ⑥ | 挂起→施工；解锁=exam_cost_reexam.py 跑通产新名单，池基前置 IBT-C08 |
| IBT-F02（P1） | 窗口状态账本机械化（哪段已烧/在烧/未开全靠文档纪律） | SKEL L06-D ⑤⑥ | 施工；纯治理件，禁文档口传 |
| **L06-C18（新，册内未见）** | **WFA 过拟合三维仅评 1 维 + RB-STATS-01 自洽⇒现况 E4 全落"存疑"不可"通过"**：参数扰动/跨时段两维未接（OVERFIT_DIMENSIONS_TOTAL=3 :57） | 本块新立 | 施工→补二维后考尺方能出"通过"；属考尺能力面非判据变更，可起手 |
| **L06-C19（新，册内未见）** | **条件轴冰点档/板块维数据不可得**：情绪冰点 0 日（四档）、板块 observational-only 17 日 ⇒ 条件共振格该二维无统计判据支撑，填格须避开或另补数据源 | 本块新立 | 挂起→数据面（DU/情绪链，本块登记边界不越界补数） |

## ⑤ 自审闸三态裁定（mining_sop §6）

- **终局定位**：考尺是"策略能不能上岗"的裁判咽喉，终局必全自动判档 ⇒ **不封矿**。
- 三态分布：
  - **施工**：L06-C18（补 WFA 二维）、IBT-F02（窗口状态账本）、L06-C19（登记后数据面补洞，属 DU 链）。
  - **挂起排期（解锁明确）**：IBT-F01（批 D 收口需 GPU 第一轮条件骨架）；IBT-E01（考卷结构化冻结前置）。
  - **登记不擅改**：exam_scale_cost_gate.yaml/考尺参数（批 C 冻结后禁改）、红蓝对拍判据（LANE-RB）——只标"谁该改=裁定通道"。
- **矿脉判读**：E4 三线+三道门+条件包闭卷+HOLDOUT 四窗均 file:line/冻结件数值实测；两处"数据可得≠字段在"新实锤（冰点 0 日、板块 17 日）为结构级发现。**外部双源锚定 PIT/WFE**。矿脉未枯但本块见底。

## ⑥ 挖矿日志（mining_sop §7）

| 轮 | 矿脉 | 动作 | 判定 | 归因 |
|---|---|---|---|---|
| R1 | E4+成本门+条件包+HOLDOUT+冻结件 | grep f06/exam_cost_gate/condition_package 头注 INVARIANTS + grep exam_scale_cost_gate.yaml 数值 + grep HOLDOUT 四窗（backtest_sop 域） | **signal**（RB-STATS-01 自洽闸使三维仅一维=全落存疑新洞；冰点 0 日/板块 17 日两处数据不可得实锤；HOLDOUT 定义在 IBT-PROTOCOL 非 exam_policy） | — |
| R2 | ③算法向外（PIT/WFE 对表） | WebSearch PIT backtesting（MDPI 2026 命中）+ 沿用 17 §三 Pardo WFE 在册线 | **signal** | — |
| R3 | 四窗定义域归属 | grep backtest_system_sop（查无）→ 定位真源 IBT-PROTOCOL-V1.md §3 | **查无（他域）** | 归因=真源不在检索目录，已定位正确真源，非方向无矿 |

> 本块无 noise 轮。邻块边界：搜索/预注册/多重检验判据族 → `../search_executor_prereg/MINE.md`；治理级考试循环落库 → `../exam_result_writeback/MINE.md`；成绩单上岗消费 → `../onboarding_rules_matrix/MINE.md`。
