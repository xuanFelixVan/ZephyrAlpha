---
ttl: task_bound
title: 环节[6] condition_package 大盘腿接线——接口/不变量/升级点
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 该环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 1. 逐项台账（✅ 均为 2026-10-13 本车道 Read/grep 实查）

| 件名 | 仓内真源路径:行号 | 现状 | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| condition_package 本尊 | src/zephyr/backtest/regime_validation/condition_package.py 全文实读：:17 docstring"Owner 2026-09-23 夜裁决①分层口径"；:45 灰度五档边界冻结；:47-48 闭卷窗 [2019-01-04, 2025-09-09]；:49 30 日地板；:50 _MAX_STATES_IN_WINDOW=5；:51 _STATE_FAMILY="F4_BDI_MOMENTUM_Z20"；:52-53 两表（market_emotion_index/market_alt_regime_signal）；:8 INVARIANTS 全文 | ✅ 实查在产 | scripts/backtest/factory_grid_executor.py（T1 分层键/E0 输入包验收）；scripts/backtest/f06_e4_wfa_exam.py（两文件 ls 实据）；GPU 点火前 w3_w5_precheck | 大盘腿升级：状态轴从 F4 三态（neutral/risk_on/risk_off，:29-30 docstring 实读）换/并两态输出 | ②下游 |
| ConditionPack 数据契约 | condition_package.py:66-94 实读（frame/cells/closed_book_window/dropped_bands/states/provenance 六字段；lookup O(1) :81-87；eligible_cells=Owner 上限 18 格 :89-91） | ✅ 实查在产（frozen dataclass） | 执行器/考试卡 | 两态升级**保契约不动**：只换 state 列的值域来源 | ② |
| fail-closed 守卫族 | :151-156（窗内 state 去重>5 抛 ValueError）；:135-136（两轴零重叠抛）；:58-59（情绪值越界抛）；:97-101（空查询抛）实读 | ✅ 实查在产 | 同上 | 两态值域=4 枚举+灰度——守卫阈值（>5）对两态 4 态仍成立；灰度入包须新增越界守卫 | ④ |
| 选族铁规（F4 过滤） | :109-113 _SQL_STATE 按 signal_id='F4_BDI_MOMENTUM_Z20' 定族过滤实读；docstring :27-30 选族自纠史（uniqExact=5 系三族混合，F11 猪周期/F14 BTC 非市场状态） | ✅ 实查在产 | 状态轴查询 | 两态输出落表时的 signal_id 族名=P2 定（新族并行 or 原族升级，见 §3） | ⑥数据字段 |
| 做T条件包日链（t0 链同构先例） | src/zephyr/strategy_pipeline/t0_condition_pack.py:1-25 实读（MOD-BT-226：事件驱动禁 cron/幂等 marker/子进程隔离/失败留队重试；sixphase 物化=scripts/audit/t0_six_phase_materialize.py；条件包产出=t0_gpu_condition_pack.py） | ✅ 实查在产 | 做T GPU 链 | 两态条件包若入日常产线，接线模式照此（事件唤醒+marker 幂等+覆盖式重入） | ②+④ |
| 锚定态历史构建 CLI 先例 | scripts/ch/build_anchored_state_history.py（t0_condition_pack.py:9 消费者声明实读） | ✅ 实查在册 | t0 链步 0 | 两态逐日状态的 CH 构建脚本同款 | ④ |
| D 族接管声明挂点 | docs/_working/2026-10-12-d-family-qualification-freeze-draft.md 实读：:49（unrouted 762 日 41.9%）、:55（§3.1 r1/r2 不路由）、:57（§3.3 两源分歧 21.09%） | ✅ 实查在册（draft_for_ruling） | D 族资格冻结呈批 | 研究册 §13-8：两态层"全标的覆盖+唯一宏观轴"接管 3.1/3.3——接管声明随 P2 呈批，冻结稿同批改挂 | ①上游 |

# 2. 与既有资产的边界（不推倒重来清单）

1. **直接复用零改动**：ConditionPack 数据契约、grey_band 情绪腿、闭卷窗/地板/验收纪律、save_pack/load_pack 离线双核（:203-234）、INVARIANTS 全部继承。
2. **升级点（唯一动刀面）**：状态腿数据源——`_STATE_FAMILY` 从 F4_BDI_MOMENTUM_Z20 换/并两态新族；两途择一 P2 呈批：**a) 原地换族**（改 :51 常量+选族自纠文书，闭卷窗重跑）或 **b) 新族并行**（两态族 signal_id 新增，F4 族保留退路）。默认建议 b——净零可回退，与"flag 下放=shadow 制"（宪法 §5）同构。
3. **不另立平行条件轴**：研究册 §12.4 明裁——两态输出作为 condition_package 大盘腿升级，禁建第二个 condition 包模块（同域重复簇→收敛唯一，内收判据 w5_1）。
4. **禁触碰**：emotion_index v0.1.0 冻结公式（:8 INVARIANTS"本件只分档不改值，改公式=作废重开卡"）。

# 3. 施工要点（代码实读中的坑）

1. **列名不同名坑**：状态轴键列=signal_date，情绪轴=trade_date（:8 INVARIANTS 实录"与情绪轴 trade_date 不同名，实测 Code 47 坑"）——两态新族落表时键列名必须与所选消费口径同批对齐，merge on="date" 前先核列名。
2. **灰度入包是 schema 扩面**：现 frame 列=[date, grey_band, state, cell_id, cell_eligible]——灰度是情绪腿的五档标签不是连续值；两态灰度若要入包，新增列（如 state_confidence）是数据契约扩展，须过 MODIFY-GUARD（tests/backtest/test_condition_package.py 回归）+provenance 登记，禁静默加列。
3. **30 日地板与 18 格上限的联动**：eligible_cells=Owner 上限 18 格（:90 注释）=5 灰度档×≤4 状态档的约束面；两态 4 态×5 档=20 格**超上限**——P2 须呈批：或灰度降档（如三档）、或态减（横向+单边二态合并）、或上限调格。这是本环节唯一的**硬数值冲突**，先呈批后动工。
4. **闭卷窗冻结纪律**：窗外数据禁入（禁校正/调参/定档，:8/:48）——两态族的历史回填窗口若与 [2019-01-04, 2025-09-09] 不齐，缺头日数如实剔除（dropped 同款处理），禁拉窗凑数。
5. **fail-closed 三态守卫的语义**：去重>5 抛错的语义是"窗口越界或映射册缺失"（:153-156）——两态 4 枚举天然满足；但若灰度分档后 state 列复合（态×档字面量拼接）会膨胀字面量数触发守卫，复合键应走 cell_id 而非 state 列。
6. **provenance 是验收面**：GPU 路零 CH 依赖靠 provenance json 双核（:219 注释）——两态升级必须补 provenance 字段（族名/词表版本/灰度口径），否则离线验收无从判包。

# 4. 自审闸三态裁定

| 项 | 裁定 | 理由 |
|---|---|---|
| 大盘腿换/并两态族（shadow 并行） | **施工** | 41.9% unrouted 的治本接线点；shadow 并行可回退，边际成本=新族落表+查询族名 |
| 灰度入包（schema 扩列） | **挂起排期** | 终局有位（精细条件胞），但依赖 [3] 主轨 B1 首轮过线；解锁=灰度轨冻结后随 P2 呈批 schema 扩面 |
| 18 格上限调整呈批 | **施工**（P1 呈批件） | 硬数值冲突必须 Owner 裁（Owner 上限在 :90 铭刻），不可自决 |
| 另立平行条件包 | **方案封矿** | 同域重复簇内收判据唯一化；研究册 §12.4 已裁"不另立"，终局由单包多族承载 |
