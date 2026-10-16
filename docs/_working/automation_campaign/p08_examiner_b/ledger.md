---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑧考工B·findings台账
---

# findings 台账（追加式，禁删改他人行）

格式：`## <MM-DD HH:MM> · <一批摘要>` + 要点若干 + 自检结论（两轮）。
## 10-15 07:29 · 班次 01（st-qoder-p08-1015-01）exit/portfolio/position_flow 74 张普查＝本班 0 张可出有效分，三道闸逐一定位并移交

**本班实际耗时**：起 07:29 → 交账 07:52（`date` 实测，非体感；本班体感钟仍偏快约一倍）≈ **23 分钟**。
**保底判定**：出分 **0/8 未达**，且未跑满 4 小时即交账。依据=SOP §3⑦⑧ 工序 7"失败写堵点册即停"＋指令书工序 4"缺数据源→不开考，写堵点转⑥或①席"。**只有考试口径算数**，本班不拿"跑了普查"冒充成绩，也不拿假分红行凑数（凑 8 条只需把这 8 张灌进去跑，但每一条形因都是装置堵点，见第三节）。

### 一、冷启动与防重入（读数）
- Python 3.12.8；`lock_files.py cleanup`→CLEAN；`process_reaper --status`→source=live、last_run=2026-10-15 07:30:18（写操作前提成立）。
- 水位读数（非本班动作，仅登记）：commit_pct=84.98%、ram_used_pct=64.5、cpu_pct=44.7、worktree_changes=5370>50 告警一条。本班因此**未起并发**（总包上限≤2 未用满）。
- 防重入按在册正解两址同读：旧址 `docs/_working/automation_campaign/p08_examiner_b/checkpoint.md` 与新址 `docs/04_research_records/cross_domain/automation_campaign/p08_examiner_b/checkpoint.md` 均 cursor=未开始 ⇒ 本班为该岗今日首班=班次 01，无撞车（本日 ⑧ 岗防重入拦下=0 次，供 Owner 首日三项之②记账）。
- 领卡分母实测：`exam_cards/{exit_flow,portfolio_flow,position_flow}` 文件 150 件，status=preregistered **74** 张（其余：无 status 53／blocked_on_impl 19／blocked_on_data 2／examined 2）。

### 二、可考性判定树（74/74 逐张，读数落 `.runtime/tmp/st-qoder-p08-1015-01/p08_blocked_census.yaml`）
判据全部读自卡面与执行器真源（`pillars_route`/`_CALIBRATION_JUDGED_KEYS`/`judge`），本班零裁量、零改判据。

| 堵点族 | 张数 | 一句话 |
|---|---|---|
| G1 需双臂 NAV 接线 | 29 | 门柱含 NAV/笔级专有键，`run_card` 无 `signal_b` 即硬报错＝T3 重放引擎面，属⑤/⑪产出 |
| G2 机判面待扩键 | 39 | `pillars_numeric` 有 60 个键不在 `_CALIBRATION_JUDGED_KEYS`（仅 5 键），`judge()` fail-closed 直接定败 |
| G3 缺 `oos_window_ref` | 5 | 卡面 `window.oos` **有值且五张同为 ['2024-01-01','2026-09-30']**，执行器只读 `oos_window_ref` ⇒ oos_ic 恒 NaN |
| G4 panel 路 30 对/日地板 × 持仓池 | 1 | 本族唯一"门柱全在词表内且 OOS 字段齐"的卡（TDM-P-P1-02/calibration/04）样本池=月频 top20，见闸① |
| **OK 可考** | **0** | — |

判定树排序口径（防"读数看着比事实干净"）：先 G1 后 G6，故 G1 里 **1 张同时缺 `data_binding.signal_table`**（TDM-X-S1-03/comparison/02_dualwindow）只记了首因；本班把它单列出来，勿当"只需双臂"。

### 三、三道闸的实测证据（命令正文=本班实跑，可原样复跑）
**闸①（G4）panel 截面 IC 的 30 对/日地板把"持仓池 20 只"类卡整体挡在机判面外**——`ic_exam.fast_rank_ic` 末段 `ic[valid < 30] = np.nan` 后 `.dropna()`：
```
python -c "import sys,numpy as np,pandas as pd;sys.path.insert(0,'scripts/backtest');from fexam.ic_exam import fast_rank_ic;rng=np.random.default_rng(7);idx=pd.date_range('2020-01-01',periods=120);[(lambda n,s:print(f'n={n}: ic 序列长度={len(fast_rank_ic(s,s*0.5+rng.normal(size=s.shape)*0.5))}'))(n,pd.DataFrame(rng.normal(size=(120,n)),columns=[f'S{i:02d}' for i in range(n)],index=idx)) for n in (20,29,30,40)]"
```
实测读数：`n=20: ic 序列长度=0 ／ n=29: 0 ／ n=30: 120 ／ n=40: 120`——地板精确在 30，**20 只票的持仓面板返回的是空序列**（不是小，是没有）。
后果不止本席：凡卡面样本池=持仓/权重面/sleeve 且 signal_kind=panel 的校准卡，**结构上不可能出 IC**（不是这次没数据，是尺量不到）。请 ⑥ 制卡席在冻结"日频截面 IC"柱前先问一句该卡样本池是否 ≥30 只/日；⑨ 成绩官对本族 panel 分数行的 IC 柱须按此判"无面"。

**闸②（G3）OOS 字段名未接执行器**——纯函数 `judge()` 双跑对照（同一 metrics，只改 oos_ic）：
```
python -c "import sys;sys.path.insert(0,'scripts/backtest');from fexam.calibration_exam import judge;card={'pillars_numeric':{'mono_spearman_min':0.6,'ic_mean_min':0.02,'ic_ir_min':0.3,'regime_same_sign':True,'oos_same_sign':True}};m={'ic_mean':0.05,'ic_ir':0.6,'mono_spearman':None,'regime_ic':{'bull':0.04,'bear':0.06},'oos_ic':float('nan'),'n':1500};print(judge(card,m));m2=dict(m);m2['oos_ic']=0.03;print(judge(card,m2))"
```
实测：`oos_ic=NaN` ⇒ `('fail', ['oos_ic nan（OOS 窗样本不足）'])`，而 ic=0.05>0.02、ic_ir=0.6>0.3、牛熊同号三柱全部达标；`oos_ic` 有值 ⇒ `('pass', [])`。即：**这 5 张开考必得"形似信号否决、实为字段错位"的假红**。修法属"改指向"不属"改判据"——照抄卡面已冻结的 `window.oos` 补 `oos_window_ref` 一键即可（写域=⑥制卡席，本席不动卡面）。补齐后**立即解锁 2 张全市场面卡**：TDM-P-P2-04/calibration/06、/07（IS 2019-01-04 起，hfq 表面覆盖 1990-12-19..2026-10-14 实测可达）。

**闸③（G2）机判词表只有 5 个键，卡面用了 60 个非在册键**：
`_CALIBRATION_JUDGED_KEYS = {mono_spearman_min, ic_mean_min, ic_ir_min, regime_same_sign, oos_same_sign}`；高频缺键读数＝`maxdd_delta_max`(15)／`sharpe_vs_baseline_min`(14)／`turnover_cost_gate`(11)／`tracking_diff_max`(10)／`pairs_min_for_verdict`(4)。这 39 张 `judge()` 一律返回 `('fail', ['未支持判据键（机判面待扩，fail-closed）: [...]'])`＝装置未实现，不是信号无效。**本班一张都没跑**，因为跑了只会给 ⑨ 的归因四分诊制造"实现数据问题 vs 判据问题"的噪声，且卡会被翻成 examined 从队列消失（比不考更坏）。

**附带一条在册坑复证**：⑦A 班 07:23 报的 `card_binding.py:74 SERIES_DIR` 仍指 `docs/_working/nightmine_campaign/series`（该目录本班实测 ABSENT）**在 HEAD 上未修**；对本席影响=零（本族 74 张申报 `derived_series/target_series` 的张数实测 **0**，与 ⑦ 族 8 张不同形），但 `_declared_local_faces` 缺省装载对本席永久静默返回 None，注入口是唯一通道。

### 四、第二轴：CH 表面覆盖 × 卡面 IS 窗（粗筛读数，含已定性尺误差）
`known_data_gaps.yaml` 在册缺口 76 条，与本族依赖表相交 **14 条**，其中 status=open 的 3 条真命中：`kline_etf_daily_shallow_depth`（2021-03-08 起，命中 TDM-X-R1-03/calibration/02 浅史）、`sector_constituent_8803_8804_missing`、`kline_sector_880_resample_false_success`。
逐表 min/max/rows 实测（全量读数 `.runtime/tmp/st-qoder-p08-1015-01/p08_data_coverage.yaml`），对多张卡构成硬缺：`sim_trade_log` 90 行自 2026-07-17、`decision_daily` 142 行自 2026-09-16、`account_nav_daily` 8 行自 2026-09-28、`suspend` 36 行、`limit_up_pool` 自 2026-09-01、`market_etf_share_snapshot` 自 2026-09-18、`daily_valuation` 自 2026-08-03、`kline_sector` 自 2025-07-18、`l2_tick` **0 行**；`technical_indicator` 自 2019-01-02 ⇒ 12 张 IS 窗从 2018-01-02 起的卡**缺 365 天**。
**尺误差三类如实挂旗**（本轴=筛查证据，不是裁定）：①表名正则把 `c4_engine.py` 当表命中（伪阳）；②`c1_market.industry_class` 被判"表不存在"，实为 `EXISTS=1` 且无 `trade_date` 类列（真列仅 `valid_from/valid_to/updated_at`，updated_at 覆盖 2026-08-03..10-12）；③`c3_fundamental.ipo_calendar` 的 `system.columns` 返回空面。粗筛命中 31 张，含上述伪阳，请 ①/② 席按表名逐张复核后定缺数单。

### 五、移交（按席，一条一个动作）
- **⑥ 制卡席（最高杠杆，5 分钟）**：给 5 张 G3 卡补 `oos_window_ref`（值=照抄本卡 `window.oos`，不新拍数）。补完本班下一班即可对 TDM-P-P2-04/calibration/06、/07 出真分。
- **⑤ 实现席／⑪ 整装席**：G1 29 张需双臂 NAV 接线；G2 39 张需机判词表扩键（`maxdd_delta_max`/`sharpe_vs_baseline_min`/`turnover_cost_gate`/`tracking_diff_max` 四键覆盖 40 人次，优先）。
- **⑨ 成绩官**：两条口径红旗——(a) 本族 panel 分数行的 `mono_spearman_min` 柱**无机判面**（`_panel_metrics` 恒置 None，`unjudged.numeric_keys_no_machine_face` 实测点名），引用 pass 行禁叙述成"门柱全过"；(b) 持仓池(≤30 只/日)×panel 卡的 IC 柱一律判"尺量不到"，不得记作信号无效。
- **①／② 数据席**：第四节缺数清单（14 条相交缺口中 open 的 3 条＋9 张表的浅覆盖）。
- **⑩ 线长席**：⑦ 班堵点①（SERIES_DIR 旧路）在 HEAD 未修，请派单；本席 GW 旗债=1 项 `--allow-non-worktree`（原因见第六节）。

### 六、本席未做与不做（带承重证据）
- **不走 worktree，直改主区并留旗**：出分装置 `run_card` 与卡面、分数册路径全锚主区（指令书点名路径同款），与 ⑦A 班同因；已按在册纪律登记旗债，非默认绕行。
- **不改卡面判据/OOS 字段/门柱、不扩执行器词表**：写域属 ⑥/⑤；本席只交判据核的实测读数与复跑命令。
- **不凑 8 条分数**：G2/G3 卡"能跑但形因是装置"，跑=给 ⑨ 制造假红＋把未考卡翻成 examined 隐身，双输。
- **不预跑"补键后即可考"的 2 张卡**：本班若先把 TDM-P-P2-04/calibration/06、/07 的读数跑出来（不入册），等于在 OOS 闸接好之前看数——违 G4-5"先冻结后开考"，且未入册读数一旦被引用就是第二个 03 旧册事故。留待 ⑥ 补键后由下一班正式开考。
- 分数册、卡面、`trial_ledger_registry.yaml` 本班**零改动**（无出分即无追加，only-add 面未被触碰；班末实测：分数册 4,256 行／sha256 前缀 `24ef736d819d0be1`，本族 preregistered 仍 74 张、examined 仍 2 张）。

### 七、自检两轮
- **第一轮（only-add 未动旧行）**：分数册字节级前后同 sha（本班未调 `run_card`，`exam_scores_v1.yaml` 4,256 行/83 条记录面零改动，sha256 前缀 `24ef736d819d0be1` 班前班后各测一次相同）；卡面零写（74 张 status 全部仍 preregistered、examined 仍 2 张，班末实测）；本席 ledger 为纯追加（脚本断言原字节=新字节前缀，`^## ` 节数 0→1）；checkpoint 整档重写只动游标（该件本席自有面，非共享册）。
- **第二轮（读数与真源一致）**：判定树 4 族计数 29+39+5+1=74=分母 ✅；`pillars_route`/`_CALIBRATION_JUDGED_KEYS`/30 对地板/oos nan 形因四处读数均**取自执行器本体实跑**（非记忆、非文档叙述），复跑命令逐条正文可执行 ✅；粗筛轴三条尺误差已定性并降格为"筛查证据" ✅。
## 10-15 08:30 · 班次 02（st-qoder-p08-1015-02）本族 75 张领卡面在仓内三把权威尺下复核＝0 张可出有效分；两件新装置缺陷当场复现；上一班移交的 ⑥ 席前置实测未成就

**本班实际耗时**：起 08:30:09（`date` 实测）→ 见本节末收班记录段（同班追加）。
**本班出分**：**0/8 未达保底**，且未跑满 4 小时。两条独立理由见第三节——**只有考试口径算数**，本班不拿"跑了普查"冒充成绩，也不拿重复试次凑行（07b 四行已在 HEAD 册面，复跑＝同一冻结卷再烧四次试次，见 §三之二）。

### 一、冷启动与防重入（读数，全部实测）
- Python 3.12.8（PATH 修正后）；`lock_files.py cleanup`＝CLEANED 6 死锁（p09 ledger/checkpoint、feedback to_impl/to_datasource、pulse independent_signals、iteration_history）＋SALVAGED 死会话 `st-qoder-p09-1015-05` 遗物（merge=skipped，释放 claim 0）；`process_reaper --status`＝source=live、last_run 08:30:20→08:56:07⇒写操作前提成立。
- 水位三测（登记，非本席动作）：08:30 `commit_pct=86.89 degraded=False`；08:53 `commit_pct=91.41 degraded=True breached=['ALERT-SYS-003']`；08:56 `91.16/degraded=True`；ram_avail 20.66→18.66GB；cpu 60.3→66.3%；`worktree_changes=5386>50`、`stash_count=2` 如实登记，不处置他席写域。
- **ALERT-SYS-003 成文口径**（真源 `config/alert_rules.yaml:53`，生产者=`capacity_assurance.host_resource_governor.check_system_watermark`，消费方=process_reaper 10min 心跳）：commit charge>90% ⇒ "进程即将无法申请内存（**提交流程/pytest 会静默崩**）"。本班据此全程零重型回放、零并发，只跑只读＋轻聚合 CH 查询串行（循 [[mem-commit-limit-incident-20260915]]；cband 既有线"degraded 下引擎跑批＝最高风险腿"同判）。
- 防重入两址同读（在册正解）：旧址 `docs/_working/automation_campaign/p08_examiner_b/checkpoint.md` cursor＝"10-15 班次 01 已交账（07:52）"⇒ 上游班已毕；新址 `docs/04_research_records/cross_domain/automation_campaign/p08_examiner_b/checkpoint.md`＝"未开始"（10-14 搬迁遗留空壳面，非并发班）⇒ 本班＝本岗今日**班次 02**，会话名 `st-qoder-p08-1015-02`。
- 领卡分母实测（现值，非沿用上班快照）：`exam_cards/{exit_flow,portfolio_flow,position_flow}` 文件 150 件（50/37/63）；status=preregistered **75**（27/21/27）；无 status 53、blocked_on_impl 18、blocked_on_data 2、examined 2。
- **分母较上一班 07:45 快照 +1**：新增 prereg＝`TDM-P-P1-03/comparison/03_逻辑存活否决腿开闭对照`（position_flow/P1），卡面注释自证由 **⑤实现席 `st-qoder-p05-1015-01` 今日落地**（`factory_grid_executor.py:evaluate_recipe` 接 M5 序钉＋`config/position_recipe_grid_schema.yaml` 加维 `M5_thesis_survival`），原 blocked_on_impl→preregistered；移除 prereg＝0 张。该卡 signal_kind=panel、门柱含 NAV 柱⇒ 双臂面，与 ⑤ 席"开考三臂＝考工经探针册展开"的交底是否穿透考试核，本班未验证（panel 臂受第四件缺件面拦，见 §二之三），记在下班待办。

### 二、可考性终判：三把**仓内权威尺**逐张读数（本班零自造分类器）
上一班用手搓判定树分出的 G1/G2/G3/G4 四族，本班改用执行核自带的三把尺重跑，结论**同向但更硬**，并纠正两处口径。

**尺①（臂协议三态分箱）** `python scripts/backtest/fexam/arm_protocol_binding.py --cards-dir docs/03_modules/_domain_backtest/exam_cards --out <本班 tmp>`（零 CH 零写）：全库带臂协议面 21 张，本族 19 张 ⇒ `feasible_now=5`／`needs_matching_engine=14`。
- 5 张 feasible_now 全为 series 标量臂面：`R1-01/ablation/03`、`R1-01/comparison/02`、`R1-01/comparison/07`、`R1-01/comparison/07b`、`R1/shadow/02`。
- 14 张 needs_matching_engine 全为 panel：臂定义落在 symbol×日持仓路径面，而考试核 comparison 分支对两臂恒走 `_series_metrics/_arm_nav_metrics`（日频标量，DataFrame 上 cumprod/mean 轴会走偏）⇒ **本族双臂族的真墙不是"等 ⑤ 接线"，是"等横截面权重帧回放面"**（缺件点名由尺① `_missing_device` 逐卡给出，非本班叙述）。

**尺②（绑定层分类）** `card_binding.py --mode classify`（INVARIANT＝分类面零 CH 零写分数册），本族 75 张逐张：

| class | 张数 | 成文含义（真源=card_binding 文件头判据） |
|---|---|---|
| C `target_face_not_index_next_day` | 71 | 目标面不是"指数次日收益"，通用配方无从产数（NAV/权重帧/多日/截面超额） |
| C `needs_replay_engine(...)` | 1 | 卡面自证需重放引擎 |
| C `executor_horizon_mismatch:next_5d` | 1 | 多日目标未走成对申报位 |
| B `panel_deferred` | 1 | `TDM-X-S1-04/calibration/02_突破失败连续次数前瞻收益`（panel 宽表，去重/撮合口径须逐表面核） |
| U `no_data_binding_section` | 1 | `TDM-X-S1-03/comparison/02_dualwindow`（卡面无 data_binding 段） |
| **A/D 可绑** | **0** | 本族零张单表可绑 |

**纠偏一处**：class C ≠ "考工做不了"。卡面 lineage 若单表可算，本班按指令工序 2 走 API 自物化即可（⑦A 班今日 8 张即此路径）。故本班把 C 族再按**信号/目标是否单表**手工分诊，才得到 §六 的逐卡解锁单。
**线级指标（呈 ⑩，只读观测不触 ⑦ 席写域）**：全库 preregistered 184 张（entry 109/exit 27/portfolio 21/position 27）＝ A 2／A? 7／B 17／C 125／U 33 ⇒ 通用配方可绑面只占 **9/184**，这是两席考工吞吐的真实天花板，不是席位不干活。

**尺③（判官词表，按实际路由取实际词表）** `pillars_route`＋`_UNION_PILLAR_KEYS`（双臂判官用并集，上一班对全部路由统一比校准五键表＝**口径偏严**，本班改按路由比）：尺① 的 5 张 feasible_now 中，
- 门柱全在机判面内（unknown=∅）：`R1-01/comparison/02`、`R1-01/comparison/07`、`R1-01/comparison/07b`；
- 越表必 fail-closed：`R1-01/ablation/03`（2 键 `decomposition_abs_error_max_pp`,`orthogonal_maxdd_increment_min_pp`）、`R1/shadow/02`（3 键 `false_trigger_rate_max`,`forgone_gain_max_pp`,`loss_avoided_min_pp`）；
- 同列另见 `R1-02/comparison/02`（2 键）、`R1-03/calibration/02`（2 键）。

### 三、本班为何 0 张出分——两条**独立**理由（任一成立即不出分）
**理由一：唯一"干净门柱＋未考＋有已批册格"的卡是 07b，而它的四行分数已在 HEAD 落地面在册**——复跑＝重复烧试次。实测：分数册工作区面 83 行里 `07b` 恰 4 行（run_id `mineloop-07b_off_A/off_B/mid_A/mid_B`），逐行按 (card_id, run_id) 对 **HEAD 落地面旧路径册**（73 行）回查，**4/4 全等命中** ⇒ 四行是真·已落地记录，不是车道残面；而卡面 `status=preregistered`、`lineage.run_id=null`（见 §四之二，这是不一致，属 ⑥/⑩ 修复位，不属本班复跑位）。
- 四行的读数值本班如实摊出（供 ⑨ 归因）：`maxdd_improvement_pp` 16.28／19.63／5.78／5.66（门柱 `maxdd_improvement_min: 5.0` **四跑全达标**）、`sharpe_delta` +0.0587／+0.0986／+0.1134／+0.1085（门柱 `-0.1` **全达标**），四跑唯一共通的判败条＝`oos_sign_flip ic_delta nan（配对 IC 面样本不足）`；四行 `cost_bp=nan`（往返费读失败面，装置自标）。⇒ **这四行的形因高度集中在配对 IC 的 OOS 面**，与上一班闸②（G3 缺 `oos_window_ref`⇒oos 恒 NaN）**不同源**（07b 卡面 `oos_window_ref` 实测有值 `['2025-10-09','2026-09-30']`），本班未开跑故**不下结论**，只把读数与待验假设备档：底座臂在 OOS 段恒仓（07 先例在册语"OOS 整窗空仓"）会让 `_spearman` 无变异而 NaN，届时 ⑨ 须判"配对面量不到"而非"信号无效"。

**理由二：双臂底座回放在本班水位下禁起**。07b 的 `arm_base_source=exit_sim_baseline` 要跑 2018-01-02..2026-09-30 全窗 kline/指标面板回放（`WINDOW_RUN` 真源 `exit_simulator.py:60`）；开班至交账 `commit_pct` 稳定 >90 且 `degraded=True`，ALERT-SYS-003 成文后果＝"提交流程/pytest 会静默崩"。理由一已使复跑无收益，理由二使它有全局风险，两条同向 ⇒ 本班不起。

### 四、新装置缺陷两件（当场复现，命令即正文，属 ⑤ 席写域本班不动）
**D1 双臂驱动器 `--cards-dir` 传相对路径必崩**——`card_binding.py:2180` 对 `rglob` 出的相对路径做 `relative_to(RUN_ROOT)`，RUN_ROOT 是绝对面 ⇒ `ValueError: ... is not in the subpath of 'D:\\ZephyrAlpha'`。复现：
`python scripts/backtest/fexam/card_binding.py --mode run --cards-dir docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1 --out <tmp> --approve-list <tmp> --binding-book <tmp> --arms-variant off_A --scores <tmp> --dry-run`
绕行＝传绝对路径（本班已如此）。修法属 ⑤（一行 `Path(...).resolve()`），考工席禁改他人件。

**D2 绑定册被 10-15 双文档化后驱动器读不动（阻塞 ⑦⑧ 整条 run 面）**——`card_binding.py:1897` 用 `yaml.safe_load` 读 `docs/04_research_records/mining/ledgers/mineloop_campaign/02_binding_book.yaml`，该册现为"frontmatter + 正文"两文档形态 ⇒ `yaml.composer.ComposerError: expected a single document in the stream`（首报 08:4x，四档变体 off_A/off_B/mid_A/mid_B 全崩同一条）。同一文件 `safe_load_all` 实测可解析出 2 个 doc（doc0=frontmatter，doc1 含 `entries` 18 格／approved 17）。本班按"改喂给闸的输入指向、不动判据不动闸"的在册正解，做**单文档副本**喂驱动器并自证内容逐字等值：entries 规范化 JSON 的 sha256 前缀源面与副本面同为 `69aa824662e04afa`，副本走 `--dry-run` 即得 `{"class":"BOOK","op":"arms"}` 装配通过。
- 影响面不只本席：任何走 `--mode run --binding-book` 的班（含 ⑦）今日都会撞同一条；⑦A 今日 8 张未经该面（其 run_id 形如 `p07a-agg8-20261015-*`，而 `card_binding.run_one` 产出的 run_id 模板是 `mineloop-{tag}-{...}`，:2027——形态不符即为旁证），故该缺陷**不会以"全班报错"的形态显形**，只会以"双臂卡永远开不了考"的静默形态显形——请 ⑤ 席把 1897 行改 `safe_load_all`＋取含 `entries` 的 doc（与 `calibration_exam.py:1003` 读分数册的双文档兼容形态同款修法，禁另造第二套读法）。

### 五、分数册三面并存（呈 ⑩ 线长，本班不代裁）
- HEAD 无 `docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`；旧路径 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml` **在 HEAD**（73 行）而工作区已 `D `（暂存删除）；新路径工作区 `AM`，index blob `04964926`=75 行，工作区 blob `10a4e764`（sha256 `24ef736d819d0be1`）=83 行。
- 多出的 8 行工作区面＝⑦A 班 `p07a-agg8-20261015-*`（entry 族，未落地）。
- 在途袋（`.runtime/commit_queue/pending`）认领该件者：`st-scorehome-20261014` 五袋 ahead=20/36/60/61/66（带 73~75 行**旧字节**）＋`st-qoder-p07-1015-01-0001` ahead=82（`blob_sha256=24ef736d...`＝工作区现值）。本班实测 0 出分故未写该册：工作区册面 sha256 与上一班 07:52 登记值**逐字相同**（`24ef736d819d0be1`）⇒ 分数册本席零改动。
- 风险提示（事实级）：scorehome 三袋的旧字节（73~75 行）若先于 ⑦A 袋落地，落地侧对该件是"新增文件"而非"行级合并"，⑦A 的 8 行有被旧字节整档回退之虞（[[cas-replay-whole-tree-revert]] 同族形态）；本班无该件变更，不代修、不代裁，只把袋序与字节量登记在册。

### 六、⑥ 席解锁单（逐卡带实测凭据；纠正上一班"补一键解锁 5 张"的口径）
上一班移交"给 5 张 G3 卡补 `oos_window_ref`（值照抄本卡 `window.oos`）⇒ 立即解锁 2 张"。本班按卡面现值逐张核：**5 张仍全部缺该键**（`oos_window_ref=None`，`window.oos` 五张同为 `['2024-01-01','2026-09-30']`；本班 09:0x 重测非沿用），并把"补完能出几张"量成事实：
- **真只差一键（2 张）**：`TDM-P-P2-04/calibration/06`、`/07`。①信号与目标**同表可算**（卡面 data_binding 自证：`kline_daily_hfq` amount/close 派生 `-ln(5e6/MA20_amount)`；high/low/close 派生 `rebound_pct=close/rolling_min(low,20)-1`；target 均 `close→next_day_return shift(-1)`，与执行器缺省面**逐字一致**，`_forward_face` 实测返回 `(1, False)` 无需申报）；②门柱五键全在机判词表内；③数据面达标——CH 实测 `kline_daily_hfq` 1990-12-19..2026-10-14 共 10,127,812 行、`technical_indicator` 2019-01-02..2026-10-14 共 392,308,017 行；两卡 IS 2019-01-04..2023-12-31、OOS 2024-01-01..2026-09-30；OOS 尾段（2025-10-09..2026-09-30，属该 OOS 的子区间）逐日截面 **241 个交易日、min 5436／max 5569／avg 5499 只票**，`amount/close` 空值 **0 行** ⇒ panel 路 30 对/日地板与 `>=30 IC 日` 两道量面闸**实测可达**，补键后出的是真分不是 NaN。
- **补一键出不了分（3 张）**：`TDM-P-P1-02/calibration/02`、`TDM-P-P1-04/calibration/04`、`TDM-P-P3-04/calibration/04`。卡面目标分别冻结为 `worst_return_next_5d`／`excess_return_next_10d`／`excess_return_next_5d`，但 `target_forward_face`/`target_horizon_days` **两键皆缺**（本班实测 `_forward_face` 三张均返回 `(1, False)`）⇒ 执行器按**次日** shift(-1) 语义消费注入面，而考卷判的是 5d/10d 面＝**名实不符的错分**（机制真源=`_forward_face` 成对申报纪律，10-13 挖矿二班立项）。这 3 张的解锁＝`oos_window_ref` ＋ 成对申报（`target.primary` 须含与 `target_horizon_days` 同值的 `mkt_fwd<h>`，现文案是 `*_next_5d/10d` 不合该正则）。本班如实提示：这**不是** 5 分钟一键活，请 ⑥ 按卡排产；⑦⑧ 若只补 oos 键就开考，出的分不可引用。
- `TDM-P-P1-02/calibration/04`（上一班 G4 唯一"词表内＋OOS 字段齐"卡）＝panel×top20 月频池（30 对/日地板）＋同样缺多日申报，双堵，非本班可动。
- `TDM-X-S1-03/comparison/02_dualwindow`＝class U（卡面**无 data_binding 段**）；门柱五键虽在词表内，无接线无从取数 ⇒ ⑥ 补 data_binding。
- `TDM-X-R1-01/comparison/02`＝门柱全在词表内、卡面有 `data_binding.arm_protocol`，但其级别→仓位映射用 **L1/L2/L3/L4** 名（卡面 arm_protocol 原文），与在册判定件 MOD-RK-049 输出的五态名（NORMAL/WARN/DANGER/CRISIS/KILL）不同构，绑定层口径不齐即拒（`_resolve_named_series`/`ArmParamUnfrozen`），且该卡**无已批册格**。两条实测更正：①卡面 `implementation_gap` 那句"状态机件与回测装置无适配器（drawdown_state_machine 在 scripts/backtest 下亦无引用）"**已过时**——本班 grep 现值命中 `card_binding.py`/`sim_daily_runner.py` 两处引用，适配器随 `790520df35`（10-13 21:20）落地；②该缺口的**已成形制解法**在 07 卡面 `data_binding.level_to_cap_map.five_state_native`（:99-113，自证"五态表逐字值取自在册件 position_cap 的 return 行"）。⇒ 02 的解锁＝按 07 先例补五态名映射＋册格，或按 07/07b 承接关系退役原卷；请 ⑥ 定去留，别让它长挂领卡面被反复领取。

### 七、⑨ 成绩官两条口径红旗（读数级，非本班裁定）
1. **IS 首年实质是 230 只票的 stub，不是全市场**：CH 实测 `kline_daily_hfq` 逐日截面按年 min／max＝2018 **230／235**（243 日）、2019 3562／3760、2020 3806／4225、2021 4224／4752、2022 4742／5070、2023 5068／5336、2024 5336／5384、2025 5385／5436（183 日）。与在册 [[stk-limit-universe-stub-pre2019]] 同族，本班把量级复核到了 hfq 面 ⇒ 凡 IS 从 2018-01-02 起的截面卡，其"IS 段读数"的分母构成在 2018 年与其他年不同构，跨段比较须按此挂旗。
2. **07b 在册四行的判败集中在配对 IC 的 OOS 一柱**（§三之一），而四行的 NAV 两柱数值全部达冻结门柱；引用这四行做归因时禁叙述成"门柱全过"或"信号被否"，须先按 §三之一的待验假设定性（本班未开跑＝未定性，如实标）。

### 八、本席未做与不做（带承重证据）
- **不复跑 07b**：四行已在 HEAD 册面（逐行 card_id+run_id 命中 4/4），复跑＝同卷再烧 4 次试次，违迭代预算纪律（SOP §4 迭代纪律/[[trial-ledger-undercount-20260927]] 分母敏感面）。
- **不建 class C 卡的重放引擎面**：横截面权重帧回放＋逐臂日净值配对面属 ⑤/⑪ 产出（尺① `_missing_device` 逐卡点名），考工自建即成为 implementer，越写域且会造第二真源。
- **不改卡面判据/门柱/OOS 字段、不扩判官词表、不修 D1/D2**：写域分属 ⑥/⑤；本班只交实跑读数与复现命令。
- **不预跑"补键即可考"的 2 张 P2-04 卡**：OOS 闸接好前把 IC 读数算出来不入册＝在冻结完成前看数（违 G4-5），且未入册读数一旦被引用就是第二个 03 旧册事故（上一班同判，本班沿用）。本班只量**数据面可达性**（行数/截面宽/空值数），不量**判据读数**。
- 分数册、卡面、`trial_ledger_registry.yaml` 本班**零改动**（0 出分⇒无追加；工作区册面 sha256 `24ef736d819d0be1` 与上一班班末登记值逐字相同）。
- **走主区直改并留旗**（同 ⑦A 班同因）：本席出分装置与卡面、分数册路径全锚主区，先 claim 后写；GW 旗债＝`--allow-non-worktree` 一项，见收班记录段。

### 九、自检两轮
- **第一轮（only-add 未动旧行）**：本节以 `safe_write_text` 追加，脚本断言"旧字节＝新字节前缀"；结构计数 `^## ` 节数 1→2、`^### ` 小节数 7→16；分数册/卡面/试次册 sha 班前班后各测（册面 `24ef736d819d0be1` 未变，本族 preregistered 仍 75、examined 仍 2）；改前两件均 `lock_files.py acquire` 成功。
- **第二轮（读数与真源一致）**：三把尺全部**当场跑真件**（尺①/尺② 输出落本班 tmp、尺③ 直接 import `pillars_route`/`_UNION_PILLAR_KEYS` 现值），无一条来自记忆或文档叙述；分母三处口径互校（75＝尺②逐张行数＝文件 status 计数）；引用给 ⑥/⑨/⑩ 的每条数值均带 CH 实跑读数或册面行级命中数；两条上一班结论被本班**改判**（"补一键解锁 5 张"→实测 2 张；"双臂必等 ⑤ 接线"→尺① 给出 feasible_now 5 张与 14 张的确切缺件名），改判证据在本节正文。
## 10-15 09:11 · 班次 02 收班记录（同班追加；本节之后本班无新成绩）

**本班实际耗时**：起 08:30:09 → 交账 09:1x（`date` 实测，本席体感钟仍快约一倍，一律以 date 为准）。
**出分**：0/8 未达保底，且未跑满 4 小时；两条独立理由与"不凑数"的承重证据见上一节 §三/§八。

### 一、入队与预检两处拦（正文即实跑，备周审计）
- 首投被 **CLAIM-CHECK / MESSAGE-CLAIMS-CODE-BAG-EMPTY** 挡在锁外（消息引用了 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml` 路径而袋内 0 代码件）。按该门自给的二选一正解取第②支：**纯登记类提交加 `[docs-only]` 显式申报**（house 先例＝HEAD `dd6ae04849`），未弱化门、未加白名单、未造新豁免。
- 二次投递带 **`--adopt-prior-work`**（在册处方：首投 finally 释放 claim 而文件保持 staged，不带 adopt 的重 claim 会把 staged 差异判 FOREIGN）。
- 成袋：`q-20261015-st-qoder-p08-1015-02-0001`（files=2）。**袋字节自证**＝逐件 `sha256(工作区字节) == 袋内 blob_sha256`：ledger.md `1ad3831fd2da…` True、checkpoint.md `547b0e809401…` True。
- 二袋超集自证（在册新方）：投前先 `difflib` 量 前袋字节→新字节 的 +/- 行差，证 **后袋 ⊇ 前袋**（删除行=0）后方投，避免同会话后袋把前袋打成"四态全无且无声明"。
- **GW 旗债＝1 项 `--allow-non-worktree`**：本席出分装置与卡面、分数册路径全锚主区（指令书点名路径同款），与 ⑦A 班同因；已留痕供 ⑩ 周审计。
- 会话注册（按 ⑦A 在册正解，非加旗绕行）：`SessionRegistry.open_session(st-qoder-p08-1015-02, held_files=[台账,游标])` → `pid=0 logical=False`（W-29 机械降级：本 sid 非 chief 形，**降级≠失败**，活性走 90s 心跳判据）；`_spawn_heartbeat_daemon` pid=**33884**；8s 后 `get_session` 实测 `last_heartbeat` 已前进（1792026436.36→1792026438.64）。

### 二、收班前追加的三项零算力量面（全部读真源件/CH 轻查询，无一条来自记忆）
- **越表柱按实际路由重算**（`pillars_route` 定路由，dual_arm 比 `_UNION_PILLAR_KEYS`、series 比 `_CALIBRATION_JUDGED_KEYS`）：本族 75 张中 **65 张**至少含一根越表柱，命中人次 TOP 概念族＝回撤面 29（13 名，`maxdd_delta_max` 独占 15）／换手成本帽 28（5 名）／Sharpe 面 26（12 名，`sharpe_vs_baseline_min` 独占 14）／跟踪差 10（1 名 `tracking_diff_max`）／配对样本闸 7（3 名）／前提命中 3（1 名）＋长尾 72 名各 1–2 人次。
- **同域重复簇线索（呈 ⑤/⑥，本席不代裁语义）**：上述新名与在册 comparison 词表近名并存——`maxdd_delta_max` vs 在册 `maxdd_improvement_min`/`maxdd_deterioration_max_pp`；`sharpe_vs_baseline_min` vs `sharpe_delta_min`；`turnover_cost_gate`/`turnover_or_cost_gate`/`turnover_cap_annual` 三同名 vs `turnover_delta_annual_max`。是否属 §4.2"同域重复簇→收敛唯一"由 ⑥ 判语义、⑤ 判机判面，本席只摊名簇与人次。
- **双臂族结构计数**：本族 `route=dual_arm` 且 preregistered ＝ **30** 张（较上班 +1 即 ⑤ 今日落地的 P1-03/comparison/03），kind 分布 **panel 24／series 6**；其中 **12 张卡面无任何臂协议声明**（`has_arm_face`=False，尺① 成文"臂定义未落文本，禁凭记忆补"）＝`X-S1-03/comparison/02_dualwindow`、`F-C2-02/shadow/03`、`P-P1-03/comparison/03`、`P-P1-04/comparison/02`、`P-P1-05/comparison/02`、`P-P1-05/comparison/03`、`P-P1-05/shadow/05`、`P-P1/comparison/02`、`P-P2-04/comparison/02`、`P-P3-03/comparison/02`、`P-P3/comparison/02`、`P-FLOW/ablation/02` ⇒ 这 12 张的解锁在 ⑥（写臂协议面）而非 ⑤（接引擎），与上班"29 张全归 ⑤/⑪"的分派不同。
- **卡面自证缺件盘点**：`data_binding.implementation_gap` 有文 ＝ **22/75** 张，其中 19 张以 `blocked_on_impl` 起首，3 张为叙述形态（`X-S2-03/comparison/02` 自证"三档执行口径在官方引擎已实现，唯 vwap 臂缺宽表注入"；`R1-01/comparison/07b` 自证"①–⑤ 逐件 2026-10-13 本班接线袋已兑现，原'缺一不开考'自钉已兑现"⇒ 与本节 §一之二"07b 码面已落地"互证）。

### 三、07b 在册四行形因升级：从"待验假设"改判为**册面实测＋算式**（零重跑）
读分数册现值（不跑装置）取 `metrics.arm_open/arm_base` 四面：四行**两臂 `oos_ic` 同为 nan**，而 `n=2121`、`ic_mean` 有值、`regime_ic` 牛/熊/危机三段均有值。CH 直测装置全窗 `kline_daily_hfq` 2018-01-02..2026-09-30＝**2123 个交易日**（另测本族 OOS 窗 2024-01-01..2026-09-30＝666 日）⇒ `n=2121` 与全窗 2123 仅差 2（形如 `shift(-1)` 尾行＋`pct_change` 首行两处边界扣除，未见中段缺口）⇒ 对齐面覆盖整个 OOS 窗，切片点数远超 `_series_metrics:226` 的 `>=60` 闸。
⇒ 判官所出的话术 `oos_sign_flip ic_delta nan（配对 IC 面样本不足）` 与实测**不符**：nan 只能来自 `_spearman`（:94-99）的两条真分支——**秩方差为 0（臂在 OOS 恒仓或恒满）或切片含 NaN**，均非"样本不足"。
- 请 ⑨ 归因按此定性：这四行的 `maxdd_improvement_pp` 16.28/19.63/5.78/5.66 与 `sharpe_delta` +0.059/+0.099/+0.113/+0.109 **数值全达冻结门柱**，唯一判败条来自配对 IC 面 nan；引用时既禁叙述成"门柱全过"，也禁叙述成"信号被 OOS 否决"。
- 请 ⑤ 记一条观测（本席不动件）：`_judge_comparison:628` 把"nan"与"样本不足"合并成一条话术，且 `_series_metrics` 的 oos 闸用 `>=60` 硬阈而回报文案称"样本不足"，两形同面不可分＝归因噪声源。
- 本席**未开双臂面**（理由见 §三之二水位＋§三之一重复试次），故不断"恒仓还是 NaN 是哪一支"，两支与算式一并入册留待有码面许可的班定。

### 四、收班自检两轮
- **第一轮（only-add 与归属）**：台账两次纯追加——首节追加前 11246 字节（`ls` 实测＝上班交账态），追加后 30131 字节（脚本断言旧正文为新正文前缀通过，`^## 1→2`、`^### 7→16`）；本收班节同法再断言前缀，并以 `difflib` 对**首袋 blob 字节**量行差、删行=0 后方投第二袋（`^## 2→3`、`^### 16→20`）；游标整档重写只动 cursor/last_run/last_batch（frontmatter 保留断言 True）；分数册/卡面/试次册**零改动**（工作区册面 sha256 `24ef736d819d0be1` 与本席 08:30 开班首测及交账末测三点同值，未被本席动，亦与 ⑦A 在途袋字节同值⇒本席未洗他人面）；袋内件面＝本席 2 件，零外来路径。
- **第二轮（读数与真源一致）**：本节全部数值来自当场实跑——三把尺（臂分箱/绑定分类/词表按路由）、CH 三条聚合查询、分数册行级读取、git blob 三面哈希、`lock_files`/队列/水位读数；无一条取自上班叙述；上班两处口径被本席以实测更正并留旧案（"补 oos 一键解锁 5 张"→2 张；"29 张双臂全属 ⑤/⑪"→其中 12 张属 ⑥ 写臂协议面）。
## 10-15 09:30 · 班次 02 终账与一条更正（另起留旧案，不改写已提交文本）

### 一、更正一条本席上文建议（§六"⑥席另 3 张 G3 卡补多日目标成对申报"）——该支路会**制造**受害者
本席写完后回头自审执行器消费面，实测：`_forward_face` 在全件**只有一个消费点**＝`_series_metrics:210`；`_panel_metrics:250` 与 `_event_metrics:804` 恒写死 `shift(-1)`，两路都**不读申报位**。而那 3 张多日目标卡（`TDM-P-P1-02/calibration/02`、`TDM-P-P1-04/calibration/04`、`TDM-P-P3-04/calibration/04`）`signal_kind` 全为 **panel** ⇒ 即便 ⑥ 把 `target_forward_face/target_horizon_days/mkt_fwd<h>` 三键补齐，执行器也**不报错、不拒、照旧按次日面出分**＝静默名实不符，比现在更坏（现在至少由 class C 拦在门外）。
- **改判后的解锁口径**：这 3 张属 **D3 装置缺陷**——panel/event 路结构上表达不了多日目标面；真修法＝⑤ 让 `_panel_metrics`（与 `_event_metrics`）同 `_series_metrics` 一样消费 `_forward_face`（含"半申报即拒"同款纪律），或由 ⑥ 把这三张改路由。**请 ⑥ 席勿照本席 §六 原文补申报位**。
- **D3 影响面实测（不当空话报）**：全库 preregistered 卡中 `target_forward_face=precomputed` 申报者＝**0 张**（本族亦 0）⇒ 当前无既有分数受害者，D3 是**前瞻缺陷**——10-13 挖矿二班立项的申报机制一旦开始被 panel 形卡使用即静默失效。此条请 ⑤ 记入立法面、⑩ 记入排产。
- 连带自证：本席游标 ④ 号规格已限定"target 注 close 价格面板"仅对**次日面卡**成立（两张 P2-04 卡卡面 primary＝`next_day_stock_return`，与 `_panel_metrics` 的硬编 shift(-1) 同形，故该规格对这两张有效、对 3 张多日卡无效）。

### 二、前置巡检读数（六时点，全部 `grep -c oos_window_ref`＝0；"0 命中"是答案不是命令坏）
08:3x 开班首测 0／09:0x 复测 0／09:11（含"各种 OOS 近名拼法"扫描：两卡顶层无任何 `oos*` 键）／09:15（并续 claim、袋位 ahead 91/98）／09:21（P2 目录 18 件全 0；同期 HEAD 已由 `0e054aa4fa` 09:06 前进＝他班在落地，本席前置未被带上）／09:29（⑥ 席 09:00 后无新袋）。
**结论**：本席今日唯一可出分的两张卡，其前置（⑥ 一键）在整个班次窗口内**未成就**；本班不再延后交账去赌该键落地——量出约束即停呈报（在册正解），把开跑条件与规格完整交在游标 ①④ 段给下一班。

### 三、水位终值与纪律遵守
09:29 实测 `commit_pct=92.74%`（较开班 86.89→91.41→91.16→**92.74** 单调恶化），`degraded=True`、breached=ALERT-SYS-003 全程未解除。本班据此**全程零重型回放、零并发**，只跑零 CH 尺面（臂分箱/绑定分类/词表普查）与轻聚合查询；即便前置成就，本班也会先等水位回落再拉三张宽面。

### 四、本班耗时分账（date/datetime 实测，非体感）
- 例行工序（冷启动→三把尺→CH 量面→案卷→首袋）：08:30:09 → 09:11 ≈ **41 分钟**。
- 收班追加与终账自审（含 D3 发现、游标规格细化、超集自证、二袋）：09:11 → 09:30 ≈ **19 分钟**。
- 合计 ≈ **60 分钟**；**未达 4 小时口径，出分 0/8 亦未达**——双口径均未达，如实报，不以任何非考试口径充抵。理由见 §二（前置未成就）与 §三（水位禁重放）；本席无可做的其余在域动作：卡面/判据/词表写域分属 ⑥/⑤，分数册写入需先有可考卡。
- 终袋数（截至本节落笔）＝**3**（`-0001`、`-0002`、本节将成 `-0003`；本节投出后计数即过时，勿据此记账——此即本席新记的"追加型台账里终值自述落笔即假"坑的自我防护）。

### 五、自检两轮（本节）
- **第一轮（only-add 与归属）**：本节仍为纯追加（脚本断言旧正文＝新正文前缀、对上一袋 blob 行差删行=0）；`^## 3→4`、`^### 20→25`、bytes 37381→42222 均为脚本实测读数（本席初稿曾把 ^### 预写成 24＝"期望列脑估"在册自犯形态，已在入袋前按实跑值改正，改正记录本行即证）；分数册/卡面/试次册零改动（工作区册面 sha256 `24ef736d819d0be1` 在 08:30／09:11／09:30 三点同值）；改前两件均持 claim（09:15 续期过）。
- **第二轮（读数与真源一致）**：D3 的三条支点均为本件正文行级实测（`_forward_face` 消费点 grep 全件命中仅 :210；`_panel_metrics:250`、`_event_metrics:804` 的 `shift(-1)` 字面；全库申报者 0 张为 rglob 全路径谓词计数，非 `endswith` 宽谓词）；巡检六时点均为 `date` 实测时序；水位四读数均为 reaper `--status` 原样输出。本席把**自己上一条建议判废**并给出改判后的责任席，未改任何判据或门柱。
## 10-15 11:04 · 班次 03（st-qoder-p08-1015-03）前置在本班值守内成就＝本族首次有真分可出；上班游标④的注入口径被正对照证伪（注 close＝价格水平机械伪影，纯噪声也能 IC 0.107）

**本班实际耗时**：起 09:35 → 交账 11:04（一律 `date` 实测；本席体感钟仍快约一倍）。
**出分**：见 §六。

### 一、冷启动与防重入（读数）
- Python 3.12.8（PATH 修正后）；`lock_files.py cleanup`＝CLEAN 无死锁；`process_reaper --status`＝source=live、last_run=09:36:05；`Get-ScheduledTask *reaper*`＝ZephyrAlpha_ProcessReaper State=Ready ⇒ 写操作前提成立。
- 防重入两址同读：旧址游标 cursor＝"10-15 班次 02 已交账（09:32）"、台账 `^## ` 节数 4；新址 `docs/04_research_records/cross_domain/automation_campaign/p08_examiner_b/checkpoint.md`＝"未开始"（10-14 搬迁空壳）⇒ 本班＝本岗今日**班次 03**，sid `st-qoder-p08-1015-03`。
- **本班自证一条在册新坑（pid=0 恒定班的锁活不过一个值守）**：09:38 `open_session`→pid=0/logical=False＋`_spawn_heartbeat_daemon` pid=50080，两件 claim ACQUIRED；10:2x 复查＝tasklist 查无 50080、`get_session` 返回 None、两件 claim 从锁面消失（全程非本席放锁）。按在册正解**同串重注册**（daemon pid=54536）＋重 claim 两件 ACQUIRED。**后果面**：若本席在 09:40-10:20 之间写台账，会与他班 cleanup 语义撞车且无执法依据 ⇒ 本席把全部写动作压到重注册之后。请 ⑩ 记排产：恒定班的 claim 保有不依赖自家守护，取决于他班 cleanup 的判活口径。
- 水位：开班 09:35 `commit_pct=93.13%`、10:18 复测 `92.09%`、degraded=True、breached=ALERT-SYS-003 全程未解除。成文真源＝`config/alert_rules.yaml:53-59`（id ALERT-SYS-003 / metric system.commit_mem_pct / condition "> 90" / severity critical，description 自述"进程即将无法申请内存（**提交流程/pytest 会静默崩**）"）⇒ 本席据此**不在 critical 水位下拉全 A 宽面**（实测全窗 hfq=9,019,977 行/5,818 只/1,940 日，两列顺序装载峰值 GB 级，外溢会打到在飞的 ⑥-07 提交与队列 drain），改走卡 06 宇宙下推（564 列×1,940 日 float32≈4.4MB）。

### 二、领卡分母与逐张归属（本班自己的尺，不引上班叙述）
`exam_cards/{exit_flow,portfolio_flow,position_flow}` 文件 **150** 件，status 分布 preregistered **75**／无 status 53／blocked_on_impl 18／examined 2／blocked_on_data 2（本班 10:0x 自建脚本逐张 `is_file()` 谓词计数，非 rglob 目录混计）。75 张按执行器真源（`pillars_route`＋`_CALIBRATION_JUDGED_KEYS`/`_UNION_PILLAR_KEYS`/`_EVENT_KNOWN_KEYS` 现值）逐张判定，加总自证 **75=30+39+5+1**：

| 归属 | 张数 | 一句话（本班实测） |
|---|---|---|
| route=dual_arm | 30 | 需双臂 NAV（`run_card` 缺 `signal_b` 即 `_ToolError`），属 ⑤/⑪ 产出面；且今日双臂 `--mode run` 面仍被 D2 拦死（见 §五） |
| 单臂但 pillars 越表 | 39 | `pillars_numeric` 含不在 5 键词表的键 ⇒ `judge():742` fail-closed 立即定败"未支持判据键（机判面待扩）"＝装置限制会被写成信号被判死 |
| 柱全在词表、缺 `oos_window_ref` | 5 | 开班 09:36 本班复测＝两目标卡 0 命中；**10:22 复测＝卡 06/07 各 1 命中且值与冻结 `window.oos` 逐字相等**（['2024-01-01','2026-09-30']），另 3 张（P1-02/02、P1-04/04、P3-04/04）**未被补**＝与本席 D3 建议一致，⑥ 按实质裁未照抄 |
| 两闸全过 | 1 | `TDM-P-P1-02/calibration/04`：卡面样本池=月频 top20 ⇒ `fast_rank_ic` 的 `ic[valid<30]=nan` 地板使截面**结构性无面**；本班不跑（理由见 §四，代码级非推测） |

分母两时点读数（面值会在值守内被上游推进，在册新坑）：10:00＝preregistered 75／缺 oos 键 5；10:27＝75／5（其中 2 张已成就）。改动者＝⑥ 席班次 07（`st-qoder-p06-1015-07`，卡 06 现仍持锁）。

### 三、卡 06 票池与取数腿实测（4 条 CH 轻查询，全部可原样复跑）
- **代码实值**：`index_constituent` 的沪深 300 是 `'000300.SH'`；谓词写 `'000300'` 得 **0 命中**（正对照＝按 index_code 分组只见 5 个带后缀值：000300/000905/000906/000852/000985 .SH）。本席第一次就踩了这个 0，靠正对照才没把它读成"无成分数据"。
- **宇宙格式不同域**：`index_constituent.symbol` 带 `.SH/.SZ`，`kline_daily_hfq.symbol` 是裸 6 位 ⇒ 直接 JOIN 返回 **0 行**＝把"连接写错"伪装成"无数据"。本班在册谓词改正 `splitByChar('.', symbol)[1]` 后命中（2018-12-28 快照 300 只，2019-01 全 300 只有价）。
- **成分语义**：2016-2025 每年 12 个快照日×300 行（月末），2026 年转日快照（36 日/10,800 行）⇒ 2019 IS 窗 PIT 成员须按"最近有效快照"前向填充，本班实测快照天数 128、成员并集 **564** 只。
- **hfq 2019 前是 stub 面**：按年 `uniqCombined(symbol)`＝2016:232／2017:238／2018:235／2019:3,770 ⇒ 卡面 `data_window_evidence` 的"1990-12-19 起 10,098,785 行"是 min/max 口径而非可用宇宙；hs300（2018-12-28 快照 300 只）∩2018-11..12 且 amount>0 ＝ **11 只/435 行**。后果＝20 日暖机使 IS 头无有效截面：本班实测保留 IC 日 **1,860/1,940**，**首个有效日=2019-01-30（比冻结 IS 起点 2019-01-04 晚 18 个交易日）**，末=2026-09-30。属披露不属拦路（OOS 全段不受影响），但上班游标④"数据自 2018-10 起"若照做，会把这 18 日当成"信号无信息"。

### 四、上班游标④的注入口径**被证伪**（本班双对照，这是本席自己上一条建议的更正，旧案留文不删）
上班 ④ 号规格写："target 注 **close 价格面板本体**——`_panel_metrics:250` 内部自做 `ret = target.shift(-1)`，注收益率即二次位移＝错读"。本班把该口径跑成实数后与卡面冻结目标不符，遂做同尺对照：
```
python - <<'PY'   # 60 列随机游走纯噪声（信号=日收益，构造上对次日收益零预测力）
A 注 close（上班④口径）      ic_mean = 0.1069
B 注 close/close.shift(1)-1  ic_mean = -0.0015
C 正对齐（target=fwd.shift(1)）ic_mean = 1.0000   # 证明工具配对的是 target[t+1] 与 signal[t]
```
- C＝正对照：`_panel_metrics` 配对的是 **signal[t] 与 target[t+1]**，所以要让 target[t+1] 等于卡面冻结的"t+1 close-to-close 收益"，注入面必须是 `close/close.shift(1)-1`（即 B/C 同形）。
- A＝负对照：**零预测力的噪声**在"注 close"下得到 IC 0.107＝流量（收益）比存量（价格水平）的机械正相关，不是信息。
⇒ 上班④那句话把"位移一次"误当成"收益率本体"，照它跑＝**把假 pass 写进分数册并把卡翻成 examined 从队列摘掉**。本席上一条建议判废，责任在本席（写规格时未做对照）。另补一条同类坑：`pct_change()` 默认 pad 会把停牌旧价读成 0 收益，本班改正为显式 `close/close.shift(1)-1`。
- **对 ⑦⑨ 的呈报（本席不代裁）**：本班注 close 复现的是 0.37/IC_IR 3.55 这种量级；⑦A 今日 16 行 ic_mean 全挤在 **[-0.061, +0.113]** 且 8 行 agg 卡彼此相差 <0.008（四个不同信号 0.0961/0.1037/0.1023/0.1022）——窄带同值是"公共机械分量"的形状，但本班**没有验过 ⑦A 的注入面**，故只摊形状与判据、不下结论。请 ⑨ 用一条判据自证：对每张 panel/series 行跑"噪声正对照"（把 target 换成随机游走 close 面，若 ic_mean 仍≈0.1 即为价格水平口径）。另请 ⑤ 注意 `run_card` 注释指向的物化件 `scripts/audit/agg8_series_materialize.py` 在盘面与 git 面均查无（`git ls-files "*agg8*"` 只命中一个 meta.yaml），注释与真源脱钩。

### 五、装置与册面现状（本班实测，均非本席可修面）
- **D2 未修**：`card_binding.py:1897` 现值仍是 `yaml.safe_load(path.read_text(...))`（全件 `safe_load_all` 零命中，safe_load 命中 :1897/:1942/:2033/:2073/:2172 五处）；绑定册现值 sha256=`ab441069565b9f8f`、`safe_load_all` 解出 **2 doc**，本班当场对全文 `yaml.safe_load` 复现 `ComposerError: expected a single document in the stream` ⇒ 双臂 `--mode run` 今日仍不可用。
- **OOS 兜底三处不对称（给 ⑤ 的一行改指向，不动判据不动门柱不改卡面）**：`calibration_exam.py:222`(_series_metrics) 与 `:258`(_panel_metrics)＝`card.get("oos_window_ref") or []` 无兜底；`:807`(event)＝`... or w.get("oos") or []` **有兜底**，且 `:810` 的报错文案自认"oos_window_ref（或 window.oos）各两日期"＝仓内已认定两键等价。⇒ 同款兜底补到 :222/:258 可一次解除 5 张的 OOS 闸，且不需要 ⑥ 逐卡补文本；本班把两条通道都摊出，择一由 ⑤/⑥ 判，本席不代裁。
- **执行器磁盘面≠HEAD**：`git hash-object` vs `git rev-parse HEAD:` 实测 `calibration_exam.py` disk=a4a5822551 head=12449226c5（差 15 插入/62 删除，他班在途），`ch_data.py`/`ic_exam.py` 两版逐字相同。**本班把这条从"疑似"升成"已排除"**：机械对拍两版 `_CALIBRATION_JUDGED_KEYS` 键集＝5 键 vs 5 键、head-only=0/disk-only=0 ⇒ 本班 §二 的词表普查结论不随该件落地翻转。分数由磁盘码产出，如实记。
- **成绩册在册性＝本班最重的一条**：`git cat-file -e HEAD:docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` 不存在、`git ls-tree HEAD -- .../scores/2026/` 空、`git log --all --oneline -- <该路径>` **零行** ⇒ 新址册**从未进入任何可达提交**；旧址 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml` 仍在 HEAD 树内而盘面已无 ⇒ 10-14 成绩搬家整批在途。index 有该件（stage0 blob=04964926481b）。
- **覆写面量化**：指该新址的非 done 袋＝5，`base_blob` **全为 None**（在册蒸发根因＝base=None＋合并器兜底 old_dev）：p07-1015-01-0001 blob=24ef736d819d（实测 83 行）／p07-1015-02-0001,0002 blob=4f986ec7143a（84 行）／st-scorehome-20261014-0003 blob=c14e6635de94（**74 行、全文 "2026-10-15" 零命中**）／-0004 blob=c7e5b1f8bfb9（75 行、今日命中 1）。而本班 10:4x 工作区册面已长到 **90 行**。**⇒ 今日成绩有被 74/75 行旧快照整档覆写的真实路径**，且本席若用陈旧副本 promote 也会洗掉他班 6 行——本席因此把 promote 前置改成"当场重拷主册＋difflib 证 minus=0"，并在 §六 逐字记自证。
- 更正上班两处叙述（另起留旧案）：① 上班 §二写"07b 四行已在 HEAD 册面"——本班 HEAD 三面查无该文件，四行实测只在**工作区册面与 ⑦A 在途袋**；② 上班写"scorehome 五袋 pending"——本班实测指该册的袋为 2（-0003/-0004），余者已离 pending（队列面 pending=118／processing=1／done=793／dead=132，去向本席不推断）。

### 六、本班考试产出＝**零分**，但把"可考"做实到一步之遥（预跑读数登记为案卷，不入册、不作成绩）
- **正门不可走（堵点，非本席可解）**：10:45 实测 `exam_cards/position_flow/P2/TDM-P-P2-04__calibration__06`（及同节点 07）锁面持有者＝**`st-qoder-p06-1015-07`，来源=入队续期、ttl=90m、剩余 89.9m**（批注"⑥制卡席 1015-07 重投袋"）。`run_card` 的产出必含卡面整档重写（`calibration_exam.py:1019-1024` 翻 `status=examined`＋写 `lineage.run_id/score_row`），在他班持 90 分活锁的件上写＝违"改前 claim"且会与他班在途袋互洗。本席**不抢锁、不绕行、不代 ⑥ 落袋**。
- **预跑读数（口径＝§四改正后的注入面，正门一开即可原样出分）**：hs300 PIT 下推面 signal=`-ln(5e6/MA20_amount)`（`rolling(20,min_periods=20).mean().shift(1)`）、target=`close/close.shift(1)-1`；结果 **verdict=fail**，`ic_mean=-0.01210`、`ic_ir=-0.06846`、`oos_ic=-0.00835`（**非 nan＝⑥ 补的键真被消费**）、`n=1859`、`fails=['ic_mean -0.0121 < 0.02','ic_ir -0.068 < 0.3',"regime_sign_flip {'bull': 0.00596, 'bear': -0.03338}"]`；有效 IC 日 1,860/1,940，首=2019-01-30、末=2026-09-30。
- 该 fail 是**真判决**（五柱中 ic/ir/regime/oos 四面全被评估，唯 `mono_spearman` 由 panel 路硬编 None⇒进 `unjudged`），与 §二 那 39 张"越表键被写成判死"性质不同：前者可入册，后者不可。
- **给下一班的开考规格（覆盖上班游标④，本席对其余部分逐字复跑过）**：① target **必须**注 `close/close.shift(1)-1`（禁注 close 本体、禁 `pct_change()` 默认 pad）；② signal 侧不变；③ 卡 06 宇宙下推 `index_code='000300.SH'`＋`splitByChar('.',symbol)[1]` 成员面按月末快照 ffill；④ 卡 07 无 `universe_note`，其 `min_obs_per_bucket=每桶≥500`×10 桶反推宇宙须 ≥5,000 只 ⇒ 只能全 A 面，须等水位离开 ALERT-SYS-003（>90）再拉，或先请 ⑥ 冻结宇宙；⑤ 分数册 promote 前**必须当场重拷主册**（本班 10:0x 见 84 行、10:4x 已 90 行，用陈旧副本 promote＝洗他班行）。
- 装置物：`.runtime/tmp/st-qoder-p08-1015-03/shift03_run06.py`（`--dry` 为预跑开关，去掉即走正门；`scores_path` 指向 `.runtime/sessions/st-qoder-p08-1015-03/staging/exam_scores_v1.yaml`）。本班 staging 副本与主册开班时逐字同字节（sha256 前缀 `4f986ec7143a690f`，116,029 B）。

### 七、保底判定与交账
- **出分 0/8 未达；未跑满 4 小时即交账**（起 09:35→交账 11:04，`date` 实测）。承重证据五条，各自独立成立：
  ① §二 75 张逐张归属＝柱面齐者仅 1 张，且该张样本池 top20 撞 30 对/日地板＝结构性无面；
  ② §六 唯一两张"前置已成就"的卡被 ⑥-07 以入队续期 ttl=90m 活锁持有，正门必写卡面⇒本班不可考；
  ③ §一/§六 卡 07 须全 A 宽面（9,019,977 行），ALERT-SYS-003 critical（92.09-93.13%）成文禁重放，外溢面打在在飞提交与队列 drain 上；
  ④ §五 D2 未修＝双臂 `--mode run` 面 30 张今日全不可开；
  ⑤ §二 39 张越表键属 ⑤ 机判面待扩，跑一张即造一条假红（`judge():742` fail-closed 实读）。
- **跨席前置的时延实测（给 ⑩ 的排产事实，非借口）**：上班 09:33 交卷→⑥ 于 09:36-10:22 之间落键（本班两时点 0→1 命中）＝**约 50-90 分钟**；而本班若要 ⑥ 再补卡 07 宇宙，案卷须过队列（头袋 `q-20261015-st-chiefdead6-20261015-0027` 10:0x 实测 waiting=30,477s≈8.5h，pending=118）。⇒ "本席呈报＝下一席可见"只在**他席主动巡册**时成立，走袋面则晚一个工作日量级。
- 只有考试口径算数：本班的尺面普查/对照/在册性探针/预跑读数一律记作案卷，不冒充成绩；分数册**本班零写入**（10:4x 主册 90 行，本班 promote 前置未成就，故不碰）。

### 八、自检两轮
- 第一轮（only-add 与归属）：本节以 `safe_write_text` 纯追加，脚本断言旧字节＝新字节前缀并给 `^## `/`^### ` 节数前后读数与 bytes 前后读数；分数册/卡面在写前逐件 `lock_files.py acquire`（分数册 DENIED＝持有者 st-qoder-p07-1015-01，claim 过期 56 分但会话 <30 分内仍活⇒不可回收，本席按在册正解不抢、改走整册副本＋纯新增自证＋`--allow-overlap`）；袋内件面＝本席自家件，外来路径零纳入。
- 第二轮（读数与真源一致）：§二 75=30+39+5+1 加总闭合；§三/§四每条数值为 CH 或代码实跑读数，含 0 命中的**正对照**（index_code 分组、成员格式、噪声对照 A/B/C 三点同帧）；§五在册性四命令（cat-file/ls-tree/log --all/ls-files -s）原文即本班实跑；无一条取自上班叙述，且上班两条结论被本班以实测改判并留旧案。
## 10-15 13:05 · 班次 03 收班节（同班追加；本节之后本班无新成绩）

### 一、正门为何本班未开＝一条实测死链（给 ⑩/⑥，非本席可修面）
- 10:45 锁面实测：卡 06/07 持有者 `st-qoder-p06-1015-07`，来源=入队续期、**ttl=90m**（批注"⑥制卡席 1015-07 重投袋"）；11:54 剩余 21.5m；12:50 复测＝**已过期 35.1m 仍挂册（惰性清理）**。
- 本班随后执行冷启动第 2 步 `lock_files.py cleanup`，再 `acquire` 卡 06 ⇒ **DENIED**，判据原文："claim 已过期 35min，但**会话仍活跃（最后活动 <30min）——过期+静默才可回收**，等其重 claim 或协调"。同族证据＝11:0x 提交日志 `takeover ledger skipped sid=st-qoder-p06-1015-08 (soft-expire only: idle=2391s <= 7200s, pid=0 no hard death evidence)`。
- ⇒ 结构结论（请 ⑩ 记排产）：**pid=0 席位既不能被硬判死、又持着 90 分钟续期锁，后继席班对同一件的可考窗口≈TTL＋7200s 软窗**，与"每 60 分钟一班"的节奏互相冲突。本席不抢锁、不代 ⑥ 放锁、不用 `--allow-concurrent` 绕行 ⇒ 本班出分 0。

### 二、本班 firsthand 复现"恒定班自我断锁"（在册机制的实弹版本）
- 12:50:58 两件 claim ACQUIRED → 12:51 本席照 SOP 跑 `lock_files.py cleanup` → 输出 **CLEANED 2 个死锁＝正是本席这两件**。
- 根因链（三任守护实测皆亡）：50080（09:38 起，10:2x tasklist 查无）→ 54536（10:24 起，11:5x 查无）→ 32128（11:10 起，13:0x tasklist 仍查无）；`open_session` 只补条目、`lock_files.py acquire` 不刷 `last_activity` ⇒ 守护 idle 1800s 自退后会话即判死。
- 操作正解（本席据此改序）：**写→入袋之间绝不穿插 cleanup**；续活须"重 open_session ＋ 重 _spawn_heartbeat_daemon ＋ 重 claim"三件连做并立即落笔入袋（13:01 连做，两件 ACQUIRED）。

### 三、入袋与归属读数
- 首袋 `q-20261015-st-qoder-p08-1015-03-0001`（files=2，base_head=`14f18f6271b0`）；**袋字节逐件==工作区字节**：ledger 58,433B→sha16 `2e0d334cfeed7a16` True、checkpoint 3,974B→sha16 `6af0a26446866eb0` True。
- 首投两次被预检"锁外给全"：① SESSION-REQUIRED（会话已被回收；按在册正解重注册，非加旗绕行）；② WORKTREE-REQUIRED→`--allow-non-worktree`（本席出分装置与卡面/分数册路径全锚主区，与上班同因）。**GW 旗债＝1 项 `--allow-non-worktree`**，留痕供 ⑩ 周审计；enqueue 日志另实记 `会话存活保障未确认 {registered:True, created:False, worktree_path:''}`＝主区无车道，与旗债同因。
- 本节将成第二袋（**投出后此计数即过时，勿据此记账**）；投前对本班首袋 blob 量行差，删行=0 才投（结果见交付面）。
- 13:0x 现场读数：分数册主面 **90 行 / 123,768B / sha16 `009c7bbcf87582c2`**（自 10:48 起未变＝上游本段无新写）；本席对分数册与两张卡面**零写入**；台账结构 h2 4→5、h3 25→33、bytes 42,366→58,433（首袋）后本节再增。

### 四、正门配方已备好（锁一开即可一命令跑完，含三重自证）
- 驱动器 `.runtime/tmp/st-qoder-p08-1015-03/shift03_land06.py`：卡锁须本席 ACQUIRED → **当场**重拷主册并记 CAS 基线 sha → `run_card` 出分 → difflib `minus=0` 硬闸（非纯新增即拒绝 promote）→ `safe_write_text` CAS promote → 读回比 sha。
- 卡 06 取数面为 hs300 下推（564 列×1,940 日 float32≈4.4MB），critical 水位下亦可跑；预跑读数见 §六（verdict=fail，五柱中四面被评估）。卡 07 须全 A 面（9,019,977 行）⇒ 仍受 `config/alert_rules.yaml:53-59` ALERT-SYS-003 禁。

### 五、耗时与两口径的诚实判定
- 墙钟 09:35→13:0x ≈ **3.5 小时**（`date` 实测，本席体感钟仍快约一倍）；**出分 0/8**。
- 本席**不**把"跑满 4 小时"当交付：指令卡的双口径是"出分或时长"，但零分的时长只构成本案卷（§一/§二/§三/§四全为实测与配方），不构成成绩。故本班按未达上报，不粉饰、不拿尺面普查充抵考试口径。

### 六、自检两轮（本节）
- **第一轮（only-add 与归属）**：本节仍为 `safe_write_text` 纯追加，脚本断言"上班末袋字节＝新面严格前缀"并给 difflib 删行数；游标只动 cursor/last_run/last_batch/notes，frontmatter 断言保留 True；分数册/两张卡面零写入（sha 现场读数见 §三）；袋内件面＝本席自家 2 件，外来路径零纳入；改前两件均持 claim。
- **第二轮（读数与真源一致）**：本节每条数值为 `date`/`tasklist`/`lock_files list`/袋 JSON blob/`hashlib`/`yaml.safe_load_all` 的当场读数；§一 的 DENIED 与 takeover-skipped 两条判据为工具原文输出，非本席转述；无一条取自本席上文或上班叙述。
## 10-15 13:42 · 班次 03 一条更正（首袋判死；上文旧句留卷不删）
- 上文 §三 写"首袋 `q-20261015-st-qoder-p08-1015-03-0001`（files=2，base_head=`14f18f6271b0`）；袋字节逐件==工作区字节 …" ⇒ **该结论现被实测推翻**：13:36 `commit_queue.py status --session st-qoder-p08-1015-03` 读数 state=**dead**，dead_reason 原文"`[landing] 非注册表族件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/automation_campaign/p08_examiner_b/ledger.md`"。
- 死因链（三面实测，非推断）：本袋 11:24:55 建、基线取 `14f18f6271b0`；期间 **13:26 有袋落 HEAD**（`076210c23f [st-qoder-p08-1015-01][⑧考工B 班次01] 本族74张preregistered逐张普查…`）把同件 ledger 推进到 74 行面 ⇒ 落地侧对本袋判"双侧皆改"→死信回退人工。与本岗在册死因族同型（基线取旧 HEAD＋袋=整档快照），**非本席内容错**。
- **内容零丢失三面对拍**：盘面 ledger 63,363B/sha16 `3c8d4eafb52274eb` **==二袋 blob**；`HEAD(74 行) is_strict_prefix_of(盘面)=True`、`minus=0 / plus=234` ⇒ 二袋落地不洗任何人（含 13:26 刚落地的班次01 面）；一袋 ledger blob（58,433B）系二袋 blob 严格前缀（投二袋前自证 `minus=0/plus=29`），一袋 checkpoint blob 与二袋之间是游标固有的整档指针重写（被替换的 2 行＝本席自家 last_run/last_batch，无他人行）。
- ⇒ 一袋**无需 requeue**（内容被二袋严格覆盖）；四态分诊判决＝**可销（superseded by -0002）**。本席不擅自 mv 队列件（销账只走 mv 通道＋机生台账行，归 ⑩/维护班），只在此留判决与双证。
- 本班锁终态（与在册"带锁交班"相反，如实记）：13:34 enqueue 输出 `ENQUEUE-RENEW: claim 续租 **0/2** 件` ⇒ 本席两件 claim 在入袋前已被外来回收（本班第 4 次：10:2x／12:51（本席自跑 cleanup 收走自家）／13:2x／13:34），故交班**不留锁**——非本席放锁，是 pid=0 守护 30 分钟寿命持不住 2 小时软窗。
## 10-15 13:45 · 班次 03 自我证伪一条（上一节刚写的"锁终态"是终值自述，落笔即假）
- 上一节末条写"13:34 `claim 续租 0/2` ⇒ 交班不留锁"。该句在它自己投出去的那一刻就失效了：**13:39:51 投第三袋时输出 `ENQUEUE-RENEW: claim 续租 2/2 件（ttl=7200s）** ⇒ 本席交班实际是**带 2 小时续租锁**，下一班（班次 04）会撞本席的 ledger/checkpoint 锁。
- 这正是本席上文 §六 自己点名的形态（追加型台账里的"终值/计数自述"落笔即假），本席仍犯了——旧句留卷不删，只在此另起更正。
- **口径句（取代任何终值表述，供后续各班通用）**：本岗锁与袋的状态一律**现测**，禁写进案卷当事实：锁面只认 `python scripts/lock_files.py list` 的当刻读数（判本席是否持锁：`grep -A1 p08_examiner_b`）；袋态只认 `python scripts/commit_queue.py status --session <sid>` 的当刻读数；本班实测样本＝同一件在 13:34/13:39 两个时点读出两态（0/2 与 2/2）。
- 给下一班的可操作后果：若班次 04 起手 `acquire` 本席两件被判 HELD/DENIED，按在册正解＝**不抢不放**（本席袋已落地面：`34f6110d35` 13:39 已把 ledger 63,363B 落进 HEAD），可直接改走"当场重拷＋difflib minus=0＋`--allow-overlap`"，无需等 7200s 软窗。
## 13:42 · 班次 03 第三条更正：本席上文两节节头的时戳是脑估的（超前），此处只改判据句不再写任何终值
- 实测：`date` 现值 = **13:42**，而本席刚写出去的两节节头分别标 `13:42`、`13:45`，第二节已超前于实测（前一节亦仅因 13:39:51 建袋才未暴露）。这属于本席在册自犯形态"期望列/时戳脑估"，**在案卷里比数值错更难发现**，因为读者无法从文字内部判真伪。
- 判据句（后续本岗通用，取代一切时戳与终值自述）：**节头时戳取 `date` 现测值，写前三件套＝`date` → 落笔 → 入袋；任何"锁/袋/水位/耗时"的状态一律不写进案卷当事实，只写"现测命令＋读数时刻"**。本席三袋实测时刻可供对拍：-0002 created_at 13:34:22（已落地 `34f6110d35`）、-0003 13:39:51、-0004 本节后新袋。
- 复核命令（正文原样可跑，期望列由命令自己给）：
  `python scripts/commit_queue.py status --session st-qoder-p08-1015-03`
  `git show HEAD:docs/_working/automation_campaign/p08_examiner_b/ledger.md | wc -c`（已落地读数=63363；盘面现值见下一行实跑）
  `python scripts/lock_files.py list 2>&1 | grep -A1 p08_examiner_b`
## 14:11 · 班次 03 死信分诊收尾（本班四袋全态实测；-0004 与 -0001 同型死，内容零丢失）
- 队列现测（`commit_queue.py status --session st-qoder-p08-1015-03`，14:11）：done=3（-0002→`34f6110d35`、-0003→`98caeca70d`、-0005→`1b3facb831`）／dead=2（-0001、-0004）／pending=processing=0。
- 两件死袋 `dead_reason` **逐字同一条**：`[landing] 非注册表族件双侧皆改真冲突（整文件三方，死信回退人工）: …/ledger.md`；基线分别为 `14f18f6271b0` 与 `34f6110d3503`＝**各被本席自己的后继袋落地推进过**（13:26 他袋落班次01 面、以及本席 -0003 落 98caeca70d）。
- **超集双证**：`blob(-0001)` 58,433B 与 `blob(-0004)` 66,838B 均为现值 `blob(-0005)`/盘面 68,084B 的**严格前缀**（脚本 `startswith` 判 True）⇒ 两死袋内容已被落地袋完全覆盖 ⇒ 四态分诊判决＝**可销（superseded）**，无需 requeue；销账只走 mv 通道＋机生台账行，归 ⑩/维护班，本席不动队列件。
- **口径句（本班自造的连坐根因，写给本岗也写给 ⑦A）**：同席对同一件**连投多袋**时，前袋的 base 会被自家后袋落地推过期，落地侧就判"双侧皆改"——这不是冲突，是**自撞**。正解＝一个值守**只投一袋**（把本节所有更正攒在最后一次写里），或投后立即读 status；多袋连投的"袋数"不是交付量，死袋率才是本班的真实成本（本班 4 袋死 2）。
- 本席交班面：分数册与两张卡面**零写入**（`exam_scores_v1.yaml` sha16 仍 `009c7bbcf87582c2`＝13:05 读数；卡 06/07 现测 status 仍 preregistered 且 `oos_window_ref` 与冻结值逐字相等），开考配方与驱动器见游标 ①-⑦。
## 15:59 · 班次 04（st-qoder-p08-1015-04）本岗今日首两张真分出册＝2/8；上班"卡 07 须 ≥5,000 只"的反推被本班实测改判；top20 持仓面＝假红发生器（同帧双对照）

**本班实际耗时**：起 15:30:29 → 交账时点见 §六（一律 `date` 实测；本席体感钟仍快约一倍，本班 15:59 才意识到已跑 29 分钟）。
**出分**：**2 张**（TDM-P-P2-04/calibration/06、/07），两条都是真判决（五柱中 ic/ir/regime/oos 四面被评估），不是尺面普查。

### 一、冷启动与正门为何本班可开（读数）
- Python 3.12.8（PATH 修正后）；`lock_files.py cleanup`=CLEAN 无死锁；`process_reaper --status`＝source=live、last_run=15:30:42、scanned=36/killed=0。
- 水位两条读数（同一命令不同时刻，禁当终值）：15:31 `commit_pct=88.79`、15:59 `commit_pct=88.7`，degraded=False、breached=ALERT-SYS-001。⇒ 上班据 `config/alert_rules.yaml:53-59`（ALERT-SYS-003 >90 critical）禁重放的前提本班未触发；本席仍未拉全 A（见 §四 第 4 条，与本水位无关）。
- 防重入两址同读：旧址游标＝"10-15 班次 03 已交账"、台账 `^## ` 节数 10（`grep -c "^## "` 实跑）；新址 `docs/04_research_records/cross_domain/automation_campaign/p08_examiner_b/checkpoint.md:11` 值仍＝`cursor: 未开始` ⇒ 本班＝本岗今日班次 04。
- **正门解锁＝本班唯一的外部条件变化**：15:34 `lock_files.py list` 全册仅 ③-06 三件、`grep P2-04` 零命中 ⇒ 上班 §一/§六 的"⑥-07 以 ttl=90m 活锁持有卡 06/07"已解。本席未抢锁未绕行，是等待自然到期。

### 二、可考面普查（本班自己的尺，非引上班叙述）
`exam_cards/{exit_flow,portfolio_flow,position_flow}` 逐件 `is_file()` 计数＝**150 件**，status 分布 preregistered **74**／empty 53／blocked_on_impl 18／examined 3／blocked_on_data 2。74 张按执行器真源（`pillars_route`＋`_CALIBRATION_JUDGED_KEYS` 现值 5 键＋卡面 `oos_window_ref` 实存性）逐张判定，加总自证 **74 = 39 + 29 + 6**：

| 归属 | 张数 | 本班实测 |
|---|---|---|
| 越表键（route=series，judge fail-closed） | 39 | `judge():745` 原文 `未支持判据键（机判面待扩，fail-closed）: [...]`＝跑一张造一条假红 |
| route=dual_arm | 29 | 需双臂 NAV（signal_b）接线，属 ⑤/⑪ 产出面 |
| 两闸全过（可考） | 6 | P1-02/02、P1-02/04、P1-04/04、P2-04/06、P2-04/07、P3-04/04 |

- 与上班 75=30+39+5+1 的差异＝⑥ 席在 13:0x-15:3x 之间把 `oos_window_ref` 补到 P1-02/02、P1-04/04、P3-04/04（本班实测各 1 命中且与冻结 `window.oos` 逐字相等），前置在**本席值守外**成就，非本席挣得；如实记。
- **D2 已修**（上班 §五 那条）：`card_binding.py:1927` 现值＝`docs = [d for d in yaml.safe_load_all(...)]`，注释自述"单文档 safe_load 直接 ComposerError＝全部 book 通道开考被堵"。本班 15:3x 实测分数册双文档形态 `safe_load_all` 解出 2 doc 无 ComposerError ⇒ 30 张双臂卡的册面闸解除，但仍卡 NAV 接线（上表 29 张）。

### 三、两张真分（册面读回＝`yaml.safe_load_all` 当场取行，非转述 stdout）
| 卡 | verdict | ic_mean | ic_ir | oos_ic | n | regime_ic | fails |
|---|---|---|---|---|---|---|---|
| TDM-P-P2-04/calibration/06 | fail | -0.012099 | -0.068463 | -0.008353 | 1859 | bull +0.005964 / bear -0.033381 | ic_mean<0.02、ic_ir<0.3、regime_sign_flip |
| TDM-P-P2-04/calibration/07 | fail | -0.027107 | -0.135737 | -0.025044 | 1859 | bull -0.022281 / bear -0.029914 | ic_mean<0.02、ic_ir<0.3 |

- **卡 07 宇宙＝本席物化选择，非卡面冻结**（给 ⑨ 判卷必读）：卡面 `universe_note` 查无（本班实测 `d.get("universe_note") is None`），本席按同节点在册维值 hs300（卡 06 `universe_note` 原文"G_universe=hs300（在册维值）"）＋PIT 月末快照 ffill 物化，实测面 1,940 日×564 列、有效 cell 558,494。**分数册行 schema 无披露位**（本班读回 run_card 产出的 row 键集=`card_id/node_id/run_id/kind/verdict/pillars_all_pass/oos_ok/regimes/date/metrics/fails/unjudged`，无 universe/lineage 之外的口径字段）⇒ 该选择在册面对 ⑨ 不可见，只在本台账可见；请 ⑤/⑥ 判是否给行加 materialization 披露字段，本席不改册 schema。
- 卡 06 复现上班 §六 预跑读数到末位（-0.01210/-0.06846/-0.00835/n 1859）＝本班取数腿与上班同帧同形，这条是本班唯一的正对照。
- 卡 06 的 `oos_ok=true`＝⑥ 补的键真被 `:258` 消费；两张卡 `mono_spearman_min` 均进 `unjudged.numeric_keys_no_machine_face`（panel 路恒 None）＝单调柱无机器面，不是本席未算。
- **卡 07 的 extra_report（本席自算，册面无该字段故落此）**：50% 阈值在 rebound_pct 分布上的落点＝**P99.31**。卡面 `extra_report` 自述判据"若 50% 在 P95 之外，则该限额几乎不触发=零触发零消费候选"⇒ 本席按卡面口径登记为**零触发候选呈 ⑥/⑨**，本席不裁限额去留。
- **卡 07 的符号面（呈 ⑨ 归因第三路＝判据问题，本席不动柱）**：卡面假设"越冲高次日越弱"＝负向，而 `ic_floor` 冻成 `ic_mean_min: 0.02`（正号）。实测 ic_mean=−0.0271、|IC|>线而符号为负，机判按正号否决；regime 两面同号、oos 同号。本席未翻信号符号未改柱（翻符号＝挪门柱）。结论可读作"限额择时方向被支持、ic 柱符号口径与卡面假设不一致"，但**判决以机判 fail 入册为准**，改判权在 ⑨/⑥。

### 四、为何不出第 3-6 张＝四条结构闸（全部实测或代码级，非"来不及"）
1. **top20 持仓面＝假红发生器**（本席不跑的正面理由，同帧双对照，seed=7，随机面 400 日）：`ic_exam.py:96` 现值 `ic[valid < 30] = np.nan`；截面 **20 只/日** 时 `_panel_metrics` 读回 `ic_mean=0.0000`（**空 IC 序列被读成 0 而非 nan**），`judge` 出 `fails=['ic_mean 0.0000 < 0.02', 'ic_ir 0.000 < 0.3', 'oos_ic nan（OOS 窗样本不足）']`；截面 40 只/日（噪声，构造上零预测力）同帧 ic_mean=−0.0068 亦 fail。⇒ 凡冻结持仓池=多因子 top20 的卡（P1-02/02、P1-02/04、P1-04/04、P3-04/04 四张），跑一张就把"截面不足"写成一条"信号无信息"。修法指向**给喂进闸的输入**（⑤：空序列应进 unjudged 而非 0.0），本席不动判据。
2. **OOS 兜底未补**：`calibration_exam.py:222/:258` 现值仍 `card.get("oos_window_ref") or []`（无 `window.oos` 回退），而 `:807` 事件路有兜底且 `:810` 报错文案自认两键等价 ⇒ 上班给 ⑤ 的那条一行改指向未落地，本席不代改。
3. **NAV 接线缺**（29 张，上表）。
4. **top20 因子集真源已断**（本条使第 1 条即使修好也仍不可物化）：`scripts/backtest/fexam/exit_sim/prereg_frozen.yaml:23` 的 `signal_source` 指向 `docs/_working/fexam/indicator_exam_scores_v1.yaml`——本班实测该件**盘面查无**且 `git ls-files docs/_working/fexam/` **零命中**（目录在 HEAD 与磁盘均不存在）⇒ "多因子 top20 权重面"当前无可复验的列集真源；与 ⑤-1015-03 班次 03 刚修的 `card_binding.SERIES_DIR` 指向已删临时区同族（在册形态：临时区搬迁后旧指针未跟上）。转 ⑥ 冻结列集＋⑤ 修指针。

### 五、本班自犯三条（另起留旧案，不改写已提交文本）
1. **驱动首版缺仓根 sys.path** ⇒ `_spawn_heartbeat_daemon` 报 `No module named 'scripts.ops_guard'` 并**静默无守护**（首跑打印 `daemon_pid=None logical=False`）。本席第一反应想把这条报成仓内缺陷，做了零成本探针后证伪：`scripts/ops_guard.py` 实存且 `git ls-files` 命中、带 `sys.path.insert(0, ROOT)` 导入实测 `OPS_GUARD-IMPORT-OK` ⇒ 根因在本席驱动，非仓。正解已落驱动第二版（15:5x 读数 `logical=True daemon_pid=53368 readback=True`）。
2. **一次计划外的卡 07 写**：为复现 run_card 首跑崩在 `Path(card_path).write_text`（`OSError [Errno 22] Invalid argument`，卡件未损：崩后 5,559B/status 仍 preregistered/mtime 09:57），本席对卡 07 做了"原样 dump 回写"探针 ⇒ 盘面卡面被格式化重写（82 行 vs HEAD 83 行），语义差逐键对比＝**仅 `oos_window_ref` 一键**（该键系 ⑥-07 所补、`git show HEAD:<卡>` grep 命中 0＝未落地件）。随后 run_card 正常出分并整档重写卡面，故终态是考试产物；探针期间分数册**未被写**（首跑 rc=2 未 promote，册行数 93→94→95 与本席两袋两次 promote 逐次对齐）。EINVAL 复跑不复现＝瞬时，本席按"未定性"登记，不写成结论。

3. **命名门的 tracked 判定会把存量卡误判成"未跟踪新件"（本席现场撞到并复测）**：15:5x `lock_files.py acquire <卡06> st-qoder-p08-1015-04` 首报 `NAMING VIOLATION [N-01][N-13]`，同一条命令**立即重试即 ACQUIRED**；本席用同进程直接调 `lock_files._is_git_tracked()` 对两张卡实测＝`tracked=True`（且 `git ls-files -- <P2 目录>` 命中 17 件）。正源逻辑在 `scripts/lock_files.py:585-597`——命名门只在 `not tracked` 时才跑，故 git 探针一次失败就会把 B5③ 的"存量已跟踪跳过"豁免整条打掉，报出一条与真因无关的命名错误。给 ⑤/⑩：`tracked` 判定失败应报错或按存量放行并留痕，不该降级成"未跟踪"。（同族在册案例=HEAD 上那条"门报错误导修复"。）

### 六、提交与归属（本班守上班口径：一个值守只投一袋）
- 袋内 5 件＝分数册（only-add +2 行）＋卡 06＋卡 07＋本台账＋游标。**归属声明**：卡 06/07 盘面携带 ⑥-07 的 `oos_window_ref` 补键（HEAD 查无＝未落地），本席袋=整档快照必然带出，commit message 里署名 ⑥-07，本席不认领该键为本席新增。
- 复核命令（正文原样可跑；读数列为本班 15:59 实跑值，终态以命令自己给的为准）：
  - `grep -c "^- card_id:" docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` → 本班实跑 95（开班 15:34 实跑 93，本席 +2）
  - `grep -m1 "^status:" docs/03_modules/_domain_backtest/exam_cards/position_flow/P2/TDM-P-P2-04__calibration__06_减仓参与率压力对次日价格路径.yaml` → 本班实跑 `status: examined`
  - `python scripts/commit_queue.py status --session st-qoder-p08-1015-04` → 本班投袋后读数未入本节（禁终值自述）
- **保底判定（诚实）**：出分 **2/8 未达**；本班未跑满 4 小时即交账。承重证据：§二 74 张逐张归属（两闸全过者仅 6 张）＋§四 四条闸（其中 4 张撞 top20 假红面、2 张 NAV 未接线、6 张里 4 张还叠加因子集真源断）。本席不拿"普查/对照/探针"充抵考试口径。

## 16:35 · 班次 04 追加节：首袋死于 N-16＝本岗成绩落地面被"册搬家未落删除腿"堵死（两席两袋同因实证＋旧址三态实测）；上文 §六 的"提交与归属"只到盘面为止

### 一、本班首袋实测（`commit_queue.py status --session st-qoder-p08-1015-04`，@@RECHECK@@）
- `q-20261015-st-qoder-p08-1015-04-0001`（files=5）state=**dead**，dead_reason 首句原文：`网关落盘失败（COMMIT_FAILED）: 门禁 GATE-PRECOMMIT-RUN 阻断: 落地前 pre-commit run 在 staged 面（own-scope 临时索引）发现本提交文件的违规（裁定#341 方案②，hook=['gate-naming']）`，展开行＝`[N-16] 文件名不唯一: exam_scores_v1.yaml (新增: docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml, 已有: docs/03_modules/_domain_backtest/exam_scores_v1.yaml)`。
- ⇒ §三 两条真分**盘面在册、HEAD 无册**：`git cat-file -e HEAD:docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` 实测 `fatal: ... exists on disk, but not in 'HEAD'`（该命令 rc=128，其后 `&&` 串未执行，故 `git log --all` 一条本席另跑，勿把"无输出"读成"无命中"）。

### 二、同锁面实测（`python scripts/commit_queue.py status --session <sid>` 逐席跑；下表 counts 由本脚本在 16:36:18 当场重跑并逐席断言，与表内不符即拒绝落笔）
| 会话 | counts（当刻） | 死因关键句（dead_reason 原文提取，非本席转述） |
|---|---|---|
| st-qoder-p07-1015-01 | done=1 dead=1 | -0001＝**N-16**，dead_reason 同时点名两个路径（新址 `docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` 与旧址 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml`）＝与本席逐字同因 |
| st-qoder-p07-1015-02 | done=0 dead=2 | 两袋＝`[landing] 非注册表族件双侧皆改真冲突`，提及文件＝`docs/_working/automation_campaign/p07_examiner_a/ledger.md` ⇒ **与本席不同因**（属在册"同席连投多袋自撞"族，非册锁） |
| st-qoder-p07-1015-03 | done=0 dead=2 | 同上同文件＝同族，非册锁 |
| st-qoder-p07-1015-04 | pending=1 done=2 dead=0 | 其 done 两袋落地后新址册仍不在 HEAD（本席 `git cat-file -e` 实测 fatal）⇒ 所落非册件或未含册 |
| st-scorehome-20261014 | done=0 dead=7 | -0001=`门禁 REGISTRY-MASS-DELETION 阻断`（dead_reason 点名 `ruling_registry.yaml`）；-0002 点名 `capability_canonical_file_registry.yaml`；-0003/-0004=`ghost_session: 属主会话已死（heartbeat=exited）`。**这七袋是否曾试图落地"旧址册删除"＝本席未证**（全量队列 blob grep 到写本节时仍未回结果，本席不据此下结论；旧址删除由谁承接请 ⑩ 判） |
| st-qoder-p08-1015-04（本席） | done=0 dead=1 | -0001＝**N-16**（§一） |
- 旧址面实测：`git ls-tree -r --name-only HEAD -- docs/03_modules/_domain_backtest/exam_scores_v1.yaml` **命中**（HEAD 仍有旧址）；盘面 `ls` **查无**；`git status --porcelain -- <旧址>`＝`D `（**已暂存的删除，无人在落**）；`.runtime/commit_queue/pending/` 全量 grep 旧址路径＝**零命中**（`grep -rl` 实测）。
- ⇒ **可证的部分**：新址分数册今日不可落地（⑦A-01 与本席各一袋死于逐字同一条 N-16）＋旧址册"HEAD 有／盘面无／index 已暂存删除但无人落"＝裁定#536 只落了搬家写腿、删除腿从未进 HEAD。**不可证的部分（本席不写成结论）**：scorehome 七袋是否就是那条删除腿的尝试——该会话死袋的 dead_reason 点名的是 `ruling_registry.yaml`/`capability_canonical_file_registry.yaml` 与 ghost_session，未点名旧址册。⇒ 呈 ⑩ 派活时需先做这一格归属判定。

### 三、两条处方摊给 ⑩/⑥（本席不代裁，两条都动得到落地面）
1. **补迁册的删除腿**（治本，改的是"喂给门的输入"）：把已暂存的旧址删除随一个合法袋落地（旧名留墓碑/指针行）。代价＝需先解 `REGISTRY-MASS-DELETION` 对"整册搬家"形态的判定（该门正是为防批量删注册表而立，本例是**同路径改名不是净删资产**），且原主会话已死 ⇒ 需 ⑩ 派一个活席承接，属治理资产删除面＝本席无权限也无活会话可代。
2. **N-16 豁免加一名**（治标，动的是门）：真源＝`config/.../trae_028_doc_structure_naming.yaml §n16_config`（在册说明：改豁免清单改本 YAML，禁改代码 `_N16_*_FALLBACK`；`skip_dir_prefixes` 含空串会令 N-16 全静默失效，红蓝 R3 在案）。代价＝过渡期双名并存，旧址仍在 HEAD ⇒ 复算/审计面会继续读旧快照，与本席在册"派生册双名即假重基"同形。
- 本席取**处方 1 的方向**为前置、当班不执行；本班不把处方 2 当捷径用（不为自己出分去弱化门）。

### 四、本班交付面的诚实改写（覆盖 §六 的"提交与归属"读感）
- 本班第二袋**按 4 件投**（卡 06＋卡 07＋本台账＋游标），**故意不含分数册**——含则必死同因，连投只造死袋（本岗在册口径：死袋率才是真实成本）。投出结果与本句写后计数一律以 `python scripts/commit_queue.py status --session st-qoder-p08-1015-04` 现测为准，本席不在此写终值。
- 四态分诊判决（首袋）＝**待前置后 requeue，禁盲投**：修因＝旧址退役，非本席可解；内容面＝死袋 blob 的 5 件里 4 件已由第二袋覆盖，唯分数册 2 行仍在盘面册与首袋 blob 两处存活（队列 blob 会被 purge，抢救有时限＝在册案卷口径）。
- 出分判定不变：**盘面 2 行真分、HEAD 0 行**；本岗今日"落地面成绩"仍为 **0**，与班次 01-03 同态。本席不把盘面写成落地。
- 复核命令（正文原样可跑，读数由命令自己给）：
  - `python scripts/commit_queue.py status --session st-qoder-p08-1015-04`
  - `git ls-tree -r --name-only HEAD -- docs/03_modules/_domain_backtest/exam_scores_v1.yaml`
  - `git status --porcelain -- docs/03_modules/_domain_backtest/exam_scores_v1.yaml`
  - `git cat-file -e HEAD:docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`（预期 fatal，rc=128＝未落地）


## 17:29 · 班次 05：本族 0 出分＝四台在册机器逐卡判定同向＋截面地板悬崖由本席自己复做（29↔30 有崖、空序列被写成 0.0 而非 nan）；上班两条结论被本班实测改判；落地面新证据＝旧址冻在 73 行而 20/72 张卡的 lineage 位置指针在 HEAD 悬空；本班另交一张"只差批准"的出分配方

### 一、开班实测与水位（现测命令＋时刻，非终值）

- 冷启动三步：`python --version` = 3.12.8；`lock_files.py cleanup` = 清 4 个死锁（含 p01 两件与本岗 feedback 两册）＋回收死会话 `worker-c7890e53-37600` 遗物；`python -m zephyr.trading.process_reaper --status` = `source=live`（写操作前提成立，`scanned=45 killed=0 reported=4`）。
- 水位（16:57 开班读）：`commit_pct=93.07`、`ram_avail_gb=20.5`、`degraded=True`、`breached=['ALERT-SYS-003']`、`worktree_changes=5472`。**上一班游标 §24 记"ALERT-SYS-003 未触发"，本班 16:57 已触发** ⇒ 在册事故形态＝提交内存耗尽崩在 `git add`（0xC0000142），本班据此全程只投两件文本、零大 add；开场即把 `shift05_probe`／`st-qoder-p08-1015-05` 两行登记进 `data/runtime/process_reaper_keep.txt`（收班按精确谓词撤除并读回与开班存证 `keep_before.txt` 逐字节相等）。
- 队列（`python scripts/commit_queue.py status` 解析）：total=1091，done=786／dead=299／pending=3／processing=3；本岗 `st-qoder-p08-1015-04` 两袋＝`-0001 dead`（N-16）／`-0002 done`；`lock_files.py list` 内 p08 零持有 ⇒ 防重入判定＝上一班已交账（游标 cursor 亦自证"班次 04 已交账"），本班可开工。

### 二、本班分母＝四台在册机器各自逐卡判定（全部只读、零写业务资产、零翻态）

| 尺 | 命令（正文原样可跑） | 本班读数 |
|---|---|---|
| 柱闸＋路由 | `python .runtime/tmp/st-qoder-p08-1015-05/census.py` | 本族 yaml 文件 150、可解 150、解析失败 0、preregistered **72**；series 43／dual_arm 29／event 0；两闸全过＝**4**、越表键＝39、需双臂＝29（加总自证 72==72） |
| 取数绑定层 | `python scripts/backtest/fexam/card_binding.py --mode classify --cards-dir D:/ZephyrAlpha/docs/03_modules/_domain_backtest/exam_cards/<族目录> --out <tmp>.yaml` | 72 张＝class **C 70／B 1／U 1**，class A＋D（可绑）＝**0**；拒因 top＝`target_face_not_index_next_day` 68 |
| 双臂三态分箱 | `python scripts/backtest/fexam/arm_protocol_binding.py --cards-dir <绝对路径> --out <tmp>.json` | `feasible_now` ∩ preregistered = **3**、`needs_matching_engine` 14、无臂面 55 |
| 持锁面 | `python scripts/lock_files.py list` | 本族 6 张 position_flow 卡由 `st-qoder-p06-1015-09`（⑥制卡席 09 班）持有，含上面 4 张可卡中的 3 张；本班唯一自由可考卡＝`TDM-P-P1-02/calibration/04` |

- ⚠ `--cards-dir` 必须给**绝对路径**：相对路径下 `card_binding.py` 与 `arm_protocol_binding.py` 在 `Path.relative_to()` 崩（本班实测 `ValueError: 'docs\\...yaml' is not in the subpath of 'D:\\ZephyrAlpha'`，三目录各崩一次才定性）。属 ⑤ 面（在册件对 cwd 敏感），本席不改他人件。

### 三、为何本班 0 出分＝本席自己复做的证据（不把上班游标当事实）

截面 A/B 探针（`.runtime/tmp/st-qoder-p08-1015-05/probe_face.py`，只调纯函数 `_panel_metrics`（`calibration_exam.py:249`）＋`judge`（`:734`），**零分数册写、零翻卡**；同种子 seed=7、420 日、唯一变量＝截面列数）：

| 截面列数 | ic_mean | ic_ir | n | judge 落文 |
|---|---|---|---|---|
| 564（正对照） | −0.0017407 | −0.0407876 | 419 | `ic_mean -0.0017 < 0.02`（真读数） |
| 30 | 0.0054545 | 0.029 | 419 | `ic_mean 0.0055 < 0.02`（真读数） |
| **29** | **0.0** | **0.0** | **0** | `ic_mean 0.0000 < 0.02`／`ic_ir 0.000 < 0.3`／`oos_ic nan（OOS 窗样本不足）` |
| **20** | **0.0** | **0.0** | **0** | 同 29 列 |
| 空序列直喂 `ic_stats`（`ic_exam.py:100`） | 0.0 | 0.0 | n_obs=0 | — |

- 机理钉在 `scripts/backtest/fexam/ic_exam.py:96` `ic[valid < 30] = np.nan`：截面 <30 只/日 ⇒ 每日全 nan ⇒ `.dropna()` 空序列 ⇒ `ic_stats(空)` 交回 **0.0 而不是 nan** ⇒ 机判文把"截面不足"写成"信号零信息"。悬崖精确在 **29↔30**。
- 本族两闸全过的 4 张，卡面冻结持仓面＝月频 `top_n=20`（`TDM-P-P1-02/calibration/04` 的 `data_binding.signal_derivation` 原文 `composite_signal → monthly_topn_signals(top_n=20)`；`TDM-P-P3-04/calibration/04` 同族）⇒ **每跑一张就往永久分数册写一条假陈述**。本席不开考、不翻卡、不改 `ic_stats`/`_panel_metrics`、不挪门柱（修法属 ⑤ T3 实现面＝空序列应进 `unjudged` 而非 0.0）。

### 四、上班两条结论被本班实测改判（另起留旧案，不改写已提交文本）

1. **"top20 因子集真源已断⇒列集当前不可复验"＝过强。** 实测 `scripts/backtest/fexam/exit_sim/prereg_frozen.yaml` 的 `device.columns_cap24` = **24 列、逐列带 `provenance`**（macd_dif/pdi_14/cci_14/trix/vip_14/tsi…），断的只是 `signal_source` 那句"从 `docs/_working/fexam/indicator_exam_scores_v1.yaml` 的 verdict==pass ch_backings 推得"的**推导指针**（本席复测＝该件 `ls` 查无、`git ls-files docs/_working/fexam/` 零命中，与上班同读数）。⇒ 列集可复验、来源不可复算；正解＝⑤ 把 `signal_source` 指到永久区真源（与 ⑤-1015-03 修的 `SERIES_DIR` 同族），**不是** ⑥ 重冻列集。
2. **"29 张 dual_arm 全缺 NAV 接线（signal_b）"＝过宽，且三张卡的卡面自述已过期。** 实测 `arm_protocol_binding.py` 三态：feasible_now∩preregistered = 3 张（`X-R1-01/ablation/03`、`X-R1-01/comparison/02`、`X-R1/shadow/02`）。三张卡面 `data_binding.implementation_gap` 均自述 `blocked_on_impl: scripts/backtest 下 drawdown_state_machine 零引用`——**该句对本班基座不成立**：`card_binding.py:1455`（`ResetConfirmation`）、`:1509`（`RefuseResetError`）、`:1573`（`DrawdownStateMachineConfig`）与 `sim_daily_runner.py:1364/:1403`（`DrawdownStateMachine`/`DrawdownState`）都在引用 ⇒ 适配器本体已在册，卡面 10-10 冻结的陈旧自述没跟上（属"卡面陈述 vs 落地码面"漂移，呈 ⑥ 判是否补正卡面）。
   - 真缺的是**逐卡臂册格**：在册绑定册已 promote 到 `docs/04_research_records/mining/ledgers/mineloop_campaign/02_binding_book.yaml`，本席读出 `entries` 18 格，其中 `op=arms` 只覆盖 `X-R1-01/comparison/07`（variants off/mid）与 `07b`（off_A/off_B/mid_A），而这两张卡 `status` 实测均 = **examined** ⇒ 本班没有"已批准且未考"的臂格可跑。考工自制册格＝自批，违在册甲案③（逐跑交参数、禁默认取第一档），本席不自造。

### 五、成绩落地面＝给 ⑩ 的核心新证据（本席不代裁、不代落他人 staged 件、不投含册袋）

- **严格超集已由本席量出**：旧址 HEAD 册 73 行 vs 新址盘面册 96 行（17:29 复测仍 96），`only_old=0`、shared=73 且**内容零漂移**，并**逐位同序**（断言"旧址 73 行 == 新址前 73 行的 (card_id, run_id) 全等"＝True）。⇒ 新址落回不丢旧址任何一行＝上一班 §三 处方 1 缺的前置判据补齐，可派活。
- **旧址是陈旧副本**：`git log --oneline -6 -- docs/03_modules/_domain_backtest/exam_scores_v1.yaml` 末笔＝`eb02e513f6`（2026-10-13 23:35，早于裁定#536 搬家），10-14/10-15 无人再往旧址落分 ⇒ **全线成绩落地面自搬家起零落地**；盘面滞留 23 行 date 分布＝10-14 一行、10-15 二十二行。
- **23 行滞留归属**（run_id 前缀实测）：`p07a-agg8-*` 8＋`p07a-sector6-*` 6＋`p07a-880rs-*` 1＝**15 行属 ⑦A**；`p08b-1015-04-card06/07` **2 行属本席**；`examcard-2026-10-15` 2＋`mineloop-od1-capexam-1015-*` 1 属 exit 族他席；`st-e2e-test-p09-*`／`st-probe-04mig15-*`／`st-autoplan-verify-20261015` **3 行来源名带 test/probe/plan**——本席不判性质（案卷只给命名与数值形态：三行 verdict 均 fail、ic_mean 分别 −0.0277／−0.0406／−0.0403，后两行同卡 `TDM-E-L9-A01/calibration/02`），呈 ⑨/⑩ 判是否触根宪法 §9.6 测试隔离。
- **连带损害（本班首量，不在上班案卷）**：全库 `exam_cards` 551 件中 **72 张卡**的 `lineage.score_row` 用 `exam_scores_v1.yaml#rows[N]` **位置指针**，N 值域 0..95；落地面旧址只有 73 行 ⇒ **20/72＝27.8% 的指针在 HEAD 悬空**（盘面解得到、落地面解不到，17:29 复测同值）。位置指针本身也脆：册只加不改，后续追加会挪动未来越界索引的语义 ⇒ 呈 ⑤/⑨ 考虑改 run_id 键。
- **归属与门位**：旧址删除腿自 10-14 起以 `RM`（rename＋modified）形态挂在主区 index，本席实测 `lock_files.py list` 对**两个地址均无持有者**＝无主 staged 残留。根宪法 §9.4 对无主 staged 给的处方是"按 HEAD 复位并留存证"，与本席需要的"把删除腿落地"**方向相反** ⇒ 本班遵上一班 §26 口径：旧址未退役则不投含册袋、不动他人 staged 面、不为自己的出分去弱化 N-16。

### 六、本班交付面的另一件：一张"只差批准"的出分配方（给 ⑥/统筹批准面，非本席自批）

用 `arm_protocol_binding` 自家 `verify_arm_quote`／`pending_numeric_params`／`FACE_ID_KEYWORDS` 逐卡机械预检（本席不写盘、不改卡、不代批）：

| 卡 | ARM_OPS 引句在卡面命中 | 待冻数值参数 | 越表柱 | r 位身份词（`基线臂日净值`/`日收益序列`） |
|---|---|---|---|---|
| `X-R1-01/comparison/02` | `arm_identity`＋`arm_level_cap_multiply` | **无** | **无** | **两词均命中** |
| `X-R1-01/ablation/03` | `arm_identity`＋`arm_gate_multiply` | 趋势门／降风险／预算 三处"无相邻数值" | decomposition_abs_error_max_pp／orthogonal_maxdd_increment_min_pp／regime_same_sign | 未命中 |
| `X-R1/shadow/02` | `arm_constant` | 无 | false_trigger_rate_max／forgone_gain_max_pp／loss_avoided_min_pp | 未命中 |

- ⇒ **`X-R1-01/comparison/02` 是本族唯一"卡面全冻结、只差一格已批准臂册格"的卡**：开臂＝`arm_level_cap_multiply`（档位整表已在卡面 `arm_protocol` 原文 `L1 100%/L2 100% 禁新开/L3 梯度 80/60/40%/L4 0%`）、基臂＝`arm_identity`（同原文 `三臂输入同一基线净值序列与同一成交口径`）、r 位＝`exit_sim_baseline_nav`（`data_binding.signal_column` 原文）。批准到手本席下一班即可直接跑，**不需要再判一次可行性**。
- 另两张各缺一件：ablation/03 缺 ⑥ 给三个臂参数冻数（一个数不编）；shadow/02 缺 ⑤ 给三根越表柱机器面＋r 位身份声明。

### 七、本班自犯与一次差点写错（另起留旧案）

1. **首版行集差分把册当"顶层列表"解析**，输出 `only_old=0／only_new=0／score_rows=0`，与同批 `grep -c "^- card_id:"` 的 73/96 直接矛盾才被抓出——正解＝册是 `{schema_version, title, rows:[…]}`，行在 `rows:` 键下（新址另带一段 register frontmatter）。教训＝计数前先拿两把独立尺对一次，单尺绿不构成结论。
2. **dossier 首版用 `subprocess(..., text=True)` 读 `lock_files.py list`**，Windows 下按 GBK 解码 ⇒ holders 只解出 0/2 条，一度让本班即将写下"本族零持锁"的假读数（与 §一 现测 6 张互斥）。正解＝`stdout=PIPE`＋显式 `.decode('utf-8')`。
3. **差点把一条已被他席修掉的缺陷当开项交出去**：17:2x 扫全库 551 张卡时 `entry_flow/L9/TDM-E-L9-A02__calibration__12_intraday_return_autocorr_lag2.yaml` 报 `yaml.safe_load_all` ParserError（line 23 `'on':` 块），本班 17:27:27 该件 mtime 被他席整件重写、17:29 复扫＝**解析失败 0**。⇒ 该条**不入交清单**，只留时间线；教训＝落笔前对每条引用重跑一次"该缺陷现在还在吗"，尤其在生产线路还在动的窗口里。
4. **heredoc 折叠反斜杠在册坑复现**：一段 `python - <<EOF` 里 `replace('\\','/')` 被折成语法错。正解＝`Path.as_posix()`。
5. **本席体感钟再次快约一倍**：草稿曾写"18:0x 落笔"，`date` 实测 17:28（开班 16:57）。凡时间戳一律取 `date` 现测，本节内所有时刻均如此。

### 八、保底、耗时与本班袋面（诚实）

- 出分 **0/8 未达**；本班 16:57 开班、本节 17:29 落笔，实际耗时约 **32 分钟**，未跑满 4 小时即交账。
- 承重证据＝§二 四台机器逐卡判定（分母 72 全数归属、加总自证）＋§三 本席自做的截面 A/B（564/30 正对照、空序列负对照、悬崖钉在 29↔30）＋§四.2 "已批准且未考臂格＝0"实测＋§五 落地面判据。本席**不**拿普查、对照、探针、案卷充抵考试口径。
- 本班袋面＝两件：`docs/_working/automation_campaign/p08_examiner_b/ledger.md`（本节）＋同址 `checkpoint.md`（游标推进）。**不含分数册**（旧址未退役，含则必死同因，遵上一班 §26）；**不含卡件**（本班零翻态、零考卷写）。
- 复核命令（正文原样可跑，读数由命令自己给；本席只在明确标注处给本班时刻读数）：
  - `python .runtime/tmp/st-qoder-p08-1015-05/census.py` → 本班 17:1x 读数 preregistered=72、`两闸全过（可考）` 4
  - `python scripts/backtest/fexam/card_binding.py --mode classify --cards-dir D:/ZephyrAlpha/docs/03_modules/_domain_backtest/exam_cards/position_flow --out .runtime/tmp/st-qoder-p08-1015-05/bind_position_flow.yaml` → 本班 17:1x 读数 `{"tally": {"A": 0, "A?": 0, "B": 0, "C": 25, "D": 0, "U": 0}}`
  - `python .runtime/tmp/st-qoder-p08-1015-05/probe_face.py` → 本班 17:2x 读数：`synthetic_cols_29`/`synthetic_cols_20` 的 `ic_mean`=0.0 且 `n`=0，`synthetic_cols_564` 的 `n`=419
  - `git show HEAD:docs/03_modules/_domain_backtest/exam_scores_v1.yaml | grep -c "^- card_id:"` → 73（HEAD 面，值守内不变）
  - `grep -c "^- card_id:" docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` → 本班 17:29 读数 96（他席会继续推进，勿当终值）

## 17:57 · 班次 06（st-qoder-p08-1015-06）0 出分＝本班三闸尺先出 3 张"只差⑥臂册格"，叠在册臂协议三态尺后真只差格＝1 张（本席自纠）；上班游标 ⑮(a) 的断链处方已由 ⑤ 落地且本班实测内容中性；OD1 族 44 张首次经自家执行器逐卡分诊（零写）＋⑤ 补柱面边际收益实测（top4 柱＝7→19 张过柱闸）

### 一、开班与现测分母（`date` 实测，非终值）

- 开班 17:40:48、本节写于 17:57:34（两次 `date` 原样读数）；本班出分 **0 张**。
- 冷启动三步：`python --version`=3.12.8；`lock_files.py cleanup`＝CLEANED 7 个死锁＋SALVAGED `st-qoder-p09-1015-13` 遗物；`process_reaper --status`＝`source=live`（写操作前提成就）。
- 水位两测（`python -m zephyr.trading.process_reaper --status` 的 watermark 字段）：17:41 `commit_pct=94.7 / ram_avail_gb=19.51 / cpu_pct=91.4 / degraded=True / breached=['ALERT-SYS-001','ALERT-SYS-003']`；17:57 `commit_pct=94.37 / ram_avail_gb=19.47 / degraded=True / breached=['ALERT-SYS-003']`。本族双臂底座需全市场 kline 面板装载，在册死因先例＝同一通道今日内已抛 `MemoryError: Unable to allocate 234. MiB for an array with shape (30676538,)`（分数册 rows[91] 行内 blocked.reason 原文）⇒ 本班不试重装载（与⑦班"算力窗门槛 <80% 全程未成就⇒重面板不开"同判据）。
- GPU 用芯面现测（`nvidia-smi --query-gpu=...`）：`NVIDIA GeForce RTX 3090, 3021/24576 MiB, util 9%`＝卡在场且近空闲（看门人 6GB 额度可足）；本班零考试故零用芯读数，`device_ledger` 无本席新增。
- 防重入：游标 cursor 自证"班次 05 已交账"、`lock_files.py list` 内 p08 零持有 ⇒ 本班可开工。

### 二、纠偏一条（给 ⑩/⑨/下一班）：前任普查尺是族盲单尺，本族真实构成从未按 route 词表分过账

- 上班尺（`pillars_route`＋`_CALIBRATION_JUDGED_KEYS` 一把量 72 张）把"柱越本 route 词表"与"需双臂"当成两类堵点，但对 `family∈{comparison,ablation}` 的卡，执行核真源用的是 **按 route 分词表**＝`scripts/backtest/fexam/comparison_exam.py:86` `_ROUTE_VOCAB = {"dual_arm": _UNION_PILLAR_KEYS, "event": _EVENT_KNOWN_KEYS, "series": _CALIBRATION_JUDGED_KEYS}`。
- 本班按真源词表复量（`.runtime/tmp/st-qoder-p08-1015-06/census2.py`，只读零写）＝本族 preregistered **72** 张的 family×route 交叉面：

| family | route | 柱是否全在本 route 词表 | 张数 |
|---|---|---|---|
| comparison | series | 越表 | 18 |
| comparison | dual_arm | 越表 | 16 |
| shadow | series | 越表 | 11 |
| calibration | series | 越表 | 10 |
| ablation | dual_arm | 越表 | 7 |
| calibration | series | **柱全在词表** | 4 |
| shadow | dual_arm | 越表 | 3 |
| comparison | dual_arm | **柱全在词表** | 2 |
| comparison | dual_arm | **柱全在词表**（缺 oos） | 1 |

- 加总自证 72==72；三态汇总＝OD1 族（comparison/ablation）44／calibration 14／shadow 14。⇒ "两闸全过仅 4 张"这句只对 **series 校准面** 成立，**不是** 本族可考面全貌；本族 44 张对照/消融卡在此前从未进过自家执行器的分诊口（`comparison_exam.py` 落地于 10-15 15:19，晚于本岗班次 01-03 的普查）。

### 三、OD1 族 44 张首次经自家执行器逐卡分诊（零写盘＝只走 `run_card_comparison(dry=True)`）

- 尺＝执行器本体分诊函数 `comparison_exam.py:93 _route_vocab`（route＋`card_binding.classify_card`＋`pillars_outside_vocab`）；驱动器 `.runtime/tmp/st-qoder-p08-1015-06/triage_od1.py`，逐卡凭据落 `.runtime/tmp/st-qoder-p08-1015-06/triage_od1.json`（tmp 区，不入库）。
- 读数：44 张全部 `binding_class=C`，仅 `TDM-X-S1-03/comparison/02_dualwindow` 为 `U`；卡面 oos 齐＝43/44。
- 缺件聚合（一张卡可同时缺多件）：`⑤无机器柱` 39 张、`⑤无机器柱＋⑥臂册格缺位` 26 张、`⑥臂册格缺位` 2 张、`⑥臂册格缺位＋卡面缺 oos` 1 张、零缺件 4 张（＝§二那 4 张 series 校准卡）。
- "无机器柱"谓词的双对照（本席按在册纪律自证，非推断）：谓词＝柱名 ∉（CAL∪EVENT∪UNION 三词表）再全仓 `grep -rl --include=*.py`。正对照 `ic_mean_min`=1 个 py 文件／`whipsaw_roundtrip_ratio_max`=2／`oos_same_sign`=1／`maxdd_improvement_min`=1；负对照 `maxdd_delta_max`/`sharpe_vs_baseline_min`/`turnover_or_cost_gate`/`pairs_min_for_verdict`/`tracking_diff_max`/`brinson_consistency`/`zero_gain_slotday_reduction_min` **py 命中全=0** 而同批键在卡面 yaml 命中 15/29/2 个文件＝"仅题面有、机器面无"成立。
- 分账：本族无机器柱 distinct=**107** 根、卡次合计=179；只差一根柱的卡=13 张。
- 词面分裂新面（转 ⑥ 并名，本席不代改卡面）：`turnover_cost_gate`（11 卡）与 `turnover_or_cost_gate`（10 卡）两名并存，同为本族越表第一大族。

### 四、双臂底座装载口现状＝上班处方已由 ⑤ 落地，本班实测内容中性

- 盘面现值（`grep -n`）：`scripts/backtest/fexam/exit_sim/exit_simulator.py:72` `SCORES_YAML = (` 现指 `docs/04_research_records/backtest/scores/2026/indicator_exam_scores_v1.yaml`，且该件 `exists=True`；件内 `results` 143 行、`verdict==pass` 78 行、逐行带 `ch_backings`。
- 内容中性对拍（`.runtime/tmp/st-qoder-p08-1015-06/ab_dualarm.py`，零 CH、零写盘）：`load_pass_columns()` 返回 **24 列**，与 `prereg_frozen.yaml` 的 `device.columns_cap24` **逐列逐序相等＝True**（脚本断言）。⇒ 指针修复不改输入面。
- 由此纠上班游标 ⑮(a)：该条写的"正解＝⑤ 指永久区真源"**已成就**（该件 mtime 10-15 15:14，早于班次 05 开班），下一班勿再把它当堵点呈报。注意 `prereg_frozen.yaml:23` 的 `signal_source` 散文行仍写旧 `_working` 路径＝纯文档面，非消费路径（消费面是 `exit_simulator.py:72` 常量）。
- 断链册对拍（冷启动 1b 在册依据）：`docs/04_research_records/governance/working_ref_sweep_20261015/broken_records.json` 对该条给出 `batch=D_同名模糊命中 / suggest=docs/04_research_records/backtest/scores/2026/indicator_exam_scores_v1.yaml / note=同名文件全docs唯一命中,需人工确认`。本席本班未自创路径、未改任何件——D 批次不在本岗授权面（指令只列 B/C 两批次的改指权）。
- 新量缺陷（转 ⑤，本席只读实测未触写者）：同件 `exit_simulator.py:77-78` 的 `OUT_YAML`/`OUT_MD` 仍指 `docs/_working/fexam/`，实测 `OUT_YAML.parent.exists()=False`＝10-14 搬迁波漏改的第二根指针，落报告面时当场建目录或抛。

### 五、本席自纠一条（另起留旧案，不改写已提交文本）：本班三闸尺单独用会误判可考面

- 本班尺（柱全在 route 词表＋oos 齐＋臂册格）给出"只差 ⑥ 一格"的卡 **3 张**：`X-S1-01/comparison/02_六桶分类增益对照`、`X-R1-01/comparison/02_熔断五级梯度减仓对照`、`X-S1-03/comparison/02_dualwindow`（后者另缺卡面 oos）。
- 叠在册臂协议三态尺 `scripts/backtest/fexam/arm_protocol_binding.py`（`triage_card`，零 CH 零写）复量后：
  - `X-R1-01/comparison/02`＝`state=feasible_now`、`arm_count=3`、`numeric_frozen=True`、`pending_numeric_params=[]`、`out_of_vocab_pillars=[]`、`secondary_states=[]` ⇒ **真只差 ⑥ 一格**，上班游标 ⑭ 的"唯一"成立。
  - `X-S1-01/comparison/02`＝`state=needs_matching_engine`，凭据原文"signal_kind=panel：臂定义落在 symbol×日横截面持仓路径面上，而执行核 comparison 分支对两臂恒走 `_series_metrics`/`_arm_nav_metrics`（日频标量；DataFrame 上 cumprod/mean 的轴会走偏）"，缺件点名＝"横截面权重帧日频组合回放（含逐标的可成交性约束）＋逐臂日净值配对面" ⇒ 本班尺假阳。
  - `X-S1-03/comparison/02_dualwindow`＝`has_arm_face=False`，凭据原文"卡面无臂协议声明（arm_protocol/paired_arm_protocol 皆缺）→ 臂定义未落文本，禁凭记忆补" ⇒ 本班尺假阳（且属 ⑥ 卡面缺声明，非 ⑤ 缺装置）。
- 纪律结论：**本族开考判据＝两尺合闸**（`comparison_exam._route_vocab` 三闸 ＋ `arm_protocol_binding.triage_card` 三态），单用前者会虚报可考面。

### 六、断供闸两口径复量（本族，与 ⑦ 班同一纠偏）

- 册现值（`src/zephyr/data/config/known_data_gaps.yaml`）：`gaps=84` 条、distinct 表 66、`status` 分布 `{completed:7, accepted:19, resolved:13, monitoring:5, open:28, mitigated:4, no_source:7, retired_quarantine:1}`；按在册词表 `open|no_source` 真断供表＝**34**。
- 本族 preregistered 72 张的 lineage/data_binding 表名命中：表名级＝**9** 张、按 status 词表＝**1** 张（差 8）⇒ 若按表名级避让会白挡 8 张。
- 唯一真断供命中卡＝`TDM-X-R1-03/calibration/02_宽基ETF天量与护盘滞后结构`（本班不开，避闸）。

### 七、给 ⑤ 的补柱面边际收益实测（只算柱闸，不担保其余闸与格）

| ⑤ 实现柱（按本族卡次降序累加） | 本族柱全过闸卡数 |
|---|---|
| 现状（0 根） | 7/72 |
| +`maxdd_delta_max` | 7/72 |
| +`sharpe_vs_baseline_min` | 8/72 |
| +`turnover_cost_gate` | 11/72 |
| +`tracking_diff_max` | **19/72** |
| +`turnover_or_cost_gate` | 23/72 |
| top8（再 +`turnover_cap_annual`,`pairs_min_for_verdict`,`precondition_hit_rate_min`） | 23/72（饱和） |

- 读数解释：前四根柱的边际收益集中在 portfolio_flow/position_flow 的 series 对照卡；top8 之后饱和＝剩余 49 张卡的越表柱高度分散（107 根 distinct 中长尾占多数），补柱面不是本族出分的主瓶颈，**⑥ 的臂册格与卡面双臂声明才是**（44 张里 29 张 route=dual_arm）。
- 本表是"补了会怎样"的机械推演，非本席对 ⑤ 优先级的裁定。

### 八、本班终判、落地面与保底如实呈报

- 可考面终判＝**0 张合法开考**：4 张过柱闸的 series 校准卡撞 `scripts/backtest/fexam/ic_exam.py:96` `ic[valid < 30] = np.nan` 的截面地板（冻结持仓面=月频 top20，悬崖 29↔30 由 04/05 班 A/B 实测在册，本班不重跑）；双臂卡里经两尺合闸真只差 ⑥ 一格的 1 张（`X-R1-01/comparison/02`）仍需臂册格到手＋底座重装载，而水位 94.37%/degraded 下装载有在册 MemoryError 先例；其余 41 张缺 ⑤ 机器柱或 ⑥ 卡面声明。
- 分数册与卡面零改动：本班未调 `run_card`、未追加分数行、未翻卡态。本班驱动器首尾各做一次「本族 151 个卡件＋分数册」路径排序清单哈希，两次相等才认零改动（读数落在本班运行打印里，不写进台账当终值）。落地面册现测（17:5x，命令 `python -c "import hashlib,pathlib;print(hashlib.sha256(pathlib.Path('docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml').read_bytes()).hexdigest()[:16])"`）＝`d77773545f5b4cc7`／96 行，本席 0 行入册。
- 落地面复测（本班现测，非终值）：`git status --porcelain` 对两址册读数 `RM docs/03_modules/_domain_backtest/exam_scores_v1.yaml -> docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`＝旧址已退出 index 而改名腿未落 HEAD（`git cat-file -e HEAD:<新址>` rc=128）⇒ N-16 仍挡含册袋，本班遵 04 班 §26 不投含册袋、不动他人 staged 面。
- 保底：本班出分 0 张＜8 张，开班至今约 17 分钟＜4 小时（两口径均以 `date` 现测为准）＝**双口径均未达**，如实呈报。本席不代裁节拍、不越片；给 ⑩ 的呈面＝本族"现器可考面=0"已由 03/04/05/06 四班连续实测同向，且本班把"缺什么才能出分"钉成可执行单件（⑥ 一格＋两尺合闸判据），降档/并席与否请 ⑩ 按在册停手条款判。
- 零新建卡、零翻态、零改判据与门柱；本台账本节为纯追加（写后 difflib 自证 plus/minus 见下）。


## 18:2x · 班次 06 追加节（同班·严格超集补投）：本席自纠一枚探针设计命名＋地板机制加强为"与信号质量无关"＋本族 `#rows[N]` 指针家内分账（含本席 04 班亲笔两枚悬空）

### 九、追加节三件

- **本席自纠（另起留旧案，上文 §一/§八 文本不改）**：`.runtime/tmp/st-qoder-p08-1015-06/probe06.py` 里我命名为 `A_perfect_signal_cols_*` 的那组对照**构造不成立**——面板由 iid 正态噪声列生成后取 `tgt = sig.shift(-1)`，iid 序列次日值本身无自相关，跨截面秩相关恒 ≈0，"完美可预测"是我给的命名而非构造性质。⇒ 该组读数不能用来证"信号再好也死在 20 列"。
- **地板判据的正确形式（同进程实测，零 CH、零分数册写、零翻卡）**：悬崖与信号质量无关，因为 `_panel_metrics` 的 `n` 直接由 `scripts/backtest/fexam/ic_exam.py:96` `ic[valid < 30] = np.nan` 的掩码决定——本班读数＝20 列 `n=0`/`ic_mean=0.0`、29 列 `n=0`/`ic_mean=0.0`、30 列 `n=419`/`ic_mean=0.0191`、120 列 `n=419`/`ic_mean=0.0057`；机制面另证 `ic_stats(空序列)` 返回 `{'ic_mean': 0.0, 'icir': 0.0, 'n_obs': 0}`（**0.0 而非 nan**）。⇒ 上班游标 ③/04 班 §③ 的"跑一张即往永久册写一条'信号零信息'的假陈述"结论不但成立，且**不依赖信号好坏**——任何 20 列面的考卷都只能产出 0 读数。本席"不开考、不挪门柱、不改执行核"判定不变。
- **本族 `#rows[N]` 位置指针家内分账（给 ⑥/⑩，与上班游标 ⑯ 的 repo 级 20/72 互补）**：本族 3 子族 151 个卡件中共 **5** 张写 `exam_scores_v1.yaml#rows[N]`；`git show HEAD:docs/03_modules/_domain_backtest/exam_scores_v1.yaml` 实测 rc=0、rows=**73** ⇒ N≥73 即悬空，本族命中 **3** 张：`exit_flow/X1/TDM-X-R1-01__comparison__07`（#rows[92]）、`position_flow/P2/TDM-P-P2-04__calibration__06`（#rows[93]）、`position_flow/P2/TDM-P-P2-04__calibration__07`（#rows[94]）。**后两枚系本席 04 班翻卡时亲笔写入**（落地袋 `19f2852467`，件面="卡06/07 面（examined+lineage）"）＝本班自曝：当时按盘面册 95/96 行取号，未虑 HEAD 旧址册仅 73 行。定性＝"册未落地（N-16 旧址改名腿未落）"的下游症状，非卡面写错，旧址落地或指针改锚 row_id 后自动闭合；本席不自改他人卡面，第三枚（07）属他席。
- 重申零改动：本追加节仍只动本岗两件活文档；分数册与卡面首尾清单哈希 103b03376391ee7b 起=止、册 sha16 `d77773545f5b4cc7` 起=止（本班驱动器 manifest 自证，读数见运行打印）。
## 10-16 16:1x · 班次 01（st-qoder-p08-1016-01）本席判据过重并当场改判＝"柱越表→不开考"被在册先例推翻（新址册 106 行中 75 行 unjudged 非空仍照常出 verdict）；截面地板补 24 列正对照实测；三态首遍用官方 CLI 全量分诊；"只差一格"精确到件名；本席 [BLOCKER] 首行落账（⑩1016-19 强制收班提醒＋chief 1016-2 小步收班纪律已执行）

### 一、开班与现测分母（`date` 实测，非终值）

- 起手 14:30:15；python 3.12.8；`lock_files.py cleanup`＝CLEAN 无死锁；reaper `--status`＝source=live／last_run=14:30:49／scanned 21／whitelist 15／killed 0／reported 3／ghosts scanned=0；水位 ram_used_pct 82.7／commit_pct 79.3／cpu 58.8／degraded False／breached=ALERT-SYS-004（1 项）。
- 防重入＝两尺并读（承 ⑩1016-19 在册"pulse 末行不承重短报班"同族纠偏）：游标末态＝10-15 班次 06 已交账；`lock_files.py list` 全表仅 1 行、p08 命中 0 ⇒ 上班四件 claim 已释放，其 §⑫ 在途袋 `q-20261015-st-qoder-p08-1015-04-0002` 现 state=done。本班 sid＝`st-qoder-p08-1016-01`（实测本台账今日零班号）。
- 卡池磁盘面＝151 件（exit_flow 51／portfolio_flow 37／position_flow 63，谓词 `is_file()` 分层数，非 `rglob('*')`）；status 分布＝empty 53／preregistered 72／blocked_on_impl 19／examined 5／blocked_on_data 2。preregistered 72 与上班终值同＝本班截至本节零翻卡零翻态。

### 二、本班头号＝本席自己判据过重，当场改判并留旧案（上文不改）

- 本席开班按工序 5「门柱不一致→不开考」把 65 张柱越表卡全部停在外，得"可考面 0"。该判据被本席自己复量的在册先例推翻：新址分数册 HEAD 现 106 行，其中 **75 行 `unjudged` 非空仍照常出 verdict**（fail 71／pass 2／blocked 2），unjudged 形态＝`numeric_keys_no_machine_face`（原文如"series 路 ic_ir 恒 None（现器无 IC_IR 面）"）与 `pillars_prose_keys`。⇒ "引擎对本卡某柱无机器面"在在册实践里是**由分数行 unjudged 显形**，不是"不开考"的前置条件；本席把"越表"直接读成"门柱不一致"＝过判。
- 同坑本线已三次在册并点名过本席（⑦A 06 班"推翻前任现器可考面=0"／**⑧B 05 班"别把 class A/D=0 当考工永远跑不了"**／⑦c 01 班"'可绑面=2'真因＝卡面写响应式待 ⑥，非供数堵"）＝本席第四次踩同族，改正留册。
- 改正后的可考面尺＝三件并列而非串联单尺：①越表柱数（越表者进 unjudged 显形，**不作不开考理由**）；②卡面宇宙是否满足 `_panel_metrics` 截面地板（**这条才是本族硬闸**，见 §三）；③卡面构造是否 t 日 PIT 可算（不可算＝瞎跑，禁；⑦c 同日已以"两读法不可裁决"拒写未冻结口径，本席同判）。
- 尺面新证（按改正尺复量，`.runtime/tmp/st-qoder-p08-1016-01/pick_series.py`）：series 路由 preregistered 43 张中越表 ≤2 柱者 **16** 张，其中卡面不写 top20 池者 **11** 张＝本班真跑面起点（§六续投）。⚠"卡面不写 top20"这一谓词本身过宽（`P-P1-04/calibration/04` 文本无 top20 而 entry 承 prereg_frozen 月频调仓＝仍是 20 只/日池），逐张须读 derivation 定宇宙，禁按关键词判。

### 三、截面地板＝本族唯一硬闸，本班补 24 列点做仪器双控

- `.runtime/tmp/st-qoder-p08-1016-01/floor_control.py`（同进程、零 CH、零分数册写、零翻卡）：20 列→`n=0` 且 `ic_mean=0.0`；**24 列→`n=0`**；30 列→`n=299`；120 列→`n=299`；`ic_stats(空序列)`＝`{'ic_mean': 0.0, 'icir': 0.0, 'n_obs': 0}`。⇒ 悬崖精确在 30 列，且"截面不足"被写成 0.0 而非 nan＝跑一张即在永久册造一条"信号无信息"的假陈述，与信号好坏无关（复证上班 §㉕(a)，本班增补 24 列＝双臂底座现值列数，使正/负对照闭合）。
- 被该闸挡下者＝卡面自冻 20 只/日池的四张柱齐卡：`P-P1-02/calibration/02` 与 `/04`（承 prereg_frozen `weights`=monthly_topn_signals top_n=20）、`P-P3-04/calibration/04`（原文"持仓池=多因子 top20 权重面"）、`P-P1-04/calibration/04`（entry=调仓 T+1 开盘价同源）。本席禁改判据、禁自扩宇宙。

### 四、三态权威凭据＝首遍走官方 CLI 全量分诊（非本席手搓谓词）

- 命令：`python scripts/backtest/fexam/arm_protocol_binding.py --cards-dir D:/ZephyrAlpha/docs/03_modules/_domain_backtest/exam_cards --out .runtime/tmp/st-qoder-p08-1016-01/apb_triage.json` → 本族 20 条臂协议凭据（其余卡面无臂协议声明，不入该面，勿当成"册无此卡"的反证）；state 分布 needs_matching_engine 14／feasible_now 6；与卡面 status 交叉＝preregistered∩feasible_now **3**／preregistered∩needs_matching_engine 14／examined∩feasible_now 2／blocked_on_impl∩feasible_now 1。
- 三张 preregistered∩feasible_now 各自唯一缺件（逐张）：
  · `X-R1-01/comparison/02`＝arm_count 3、numeric_frozen=True、pending=∅、越表=∅ ⇒ 只差绑定册在册格（§五）。
  · `X-R1-01/ablation/03`＝pending_numeric_params 3 处（趋势门/降风险/预算"无相邻数值"）＋2 柱越表 ⇒ ⑥ 冻数。
  · `X-R1/shadow/02`＝3 柱越表（false_trigger_rate_max／forgone_gain_max_pp／loss_avoided_min_pp）⇒ ⑤ 补机器柱面。
- 本席自犯两枚并当场改正（旧读数不涂）：(a) 首版双臂底座列集对拍把 `prereg_frozen.device.columns_cap24` 条目按 `symbol` 键取（真键＝`column`，且 `load_pass_columns()` 返 (column, provenance) 元组）⇒ 打出 `cols_equal_cap24=False` **假漂移读数**并已进 json；改正后 ordered／set／provenance 三项全 True（24/24 逐列逐序全等，复证上班游标 ⑱）。(b) `arm_protocol_binding.triage_card()` 首遍传 Path 得 `AttributeError: 'WindowsPath' object has no attribute 'get'`，读源确认签名 `(card: dict)` 且其 CLI 内部传 dict 正确＝**本席用错，不是工具缺陷，故不立案**（与 ⑩1016-19 §39.2 gpu_watchman 路径自犯同族，归因于己）。

### 五、绑定册在册格＝"只差一格"从叙述升级为可 grep 锚点（给 ⑥）

- `docs/04_research_records/mining/ledgers/mineloop_campaign/02_binding_book.yaml` 现值 entries=18（approved 17／rejected 1）。尺＝`card_binding.load_binding_book()` 本体（只取 status==approved）；该册是**双文档 register 形**，单文档 `safe_load` 即 ComposerError，须 `safe_load_all` 再取含 `entries` 的 doc。
- 本族在册命中仅 2 格＝`TDM-X-R1-01/comparison/07`、`/07b`（两格带 `arms_variants`，档名 off/mid），而这两卡盘面 status 均已 examined；`comparison/02`·`ablation/03`·`shadow/02` **零条目**。
- ⇒ 给 ⑥：`comparison/02` 卡面已全冻结（numeric_frozen=True、pending=∅、越表=∅），补一格即可开跑，下一班不必重判可行性。本席不自投该册（非本岗写域）。
- 工具面一条（给 ⑤）：`load_binding_book` 的双臂闸是**全册并集级**——册内任一格带 `arms_variants`，则任何不带 `--arms-variant` 的装载整体抛 `arms_variant_required`，包括与本跑无关的单卡分诊。本席实测 `comparison_exam.py --card …TDM-X-S1-01__comparison__02… --binding-book …02_binding_book.yaml`（不带该旗）直接 ValueError 崩，带 `--arms-variant off` 才通。锚点 `scripts/backtest/fexam/card_binding.py:1933`。

### 六、落地面与双册对账（给 ⑩；本班只投自家文档，不动他人 staged 面）

- 分数册新址 `docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`：`git cat-file -e HEAD:` **rc=0**（上班游标 §㉔ 同件实测 rc=128＝本班开班时该堵点已由他席解除），HEAD rows=106（现测），盘==index==HEAD（`git status --porcelain` 对该件零输出）。最近触碰＝`e1033fb48d`（st-autoplan-20261015，"分数册盘面 104 行从未落 HEAD（ENOSPC 期六袋全死）→ 立即入 HEAD 防再失"）。
- 旧址 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml`：仍在 HEAD 且仍在盘，HEAD rows=73，末笔 `eb02e513f6`（10-13 23:35）＝停更。
- 对账（`.runtime/tmp/st-qoder-p08-1016-01/reconcile_rows.py`，键＝(card_id, run_id, verdict, recorded_by) 四元组）：only_old=**0**，且旧址 73 元组序列 == 新址前 73（prefix=**True**）⇒ **旧址是新址的严格前缀**，退役旧址所需的 only-add 完整性判据已齐（本席不自删、不自复位，交 ⑩ 裁）。
- 本族 `#rows[N]` 位置指针 5 枚：对旧址 3 枚悬空（N=92/93/94 ≥ 73），对新址 106 行**全部解悬**。本席 04 班亲笔两枚（`P-P2-04/calibration/06`=#rows[93]、`/07`=#rows[94]）内容反查命中 run_id `p08b-1015-04-card06`／`p08b-1015-04-card07`，verdict 均 **fail**（在册如实，非事故、非补投理由）。⇒ 上班 §㉕(b) 的"本席两枚悬空"随 `e1033fb48d` 自解，本席零改卡面。
- 停发面本班复量（16:0x 现测，两面并列）：`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` HEAD 5025 行内谓词 `^- ruling_id:` 行内匹配该三枚 10-16 新裁编号前缀（逐字面量此处不落，避引用完整性门自触）命中 **0**，而盘面 5119 行命中 **3**＝注册表腿仍未落地；同时六件代码/测试腿 `23e28b2cb7` 已是 HEAD 祖先（`git merge-base --is-ancestor` rc=0）＝**运行面已发车而治理面未落**的脱钩形态续存。本席不自判"停发已解除"、不 enable 任何席，只落两面读数。
- 队列四态现测（`python scripts/commit_queue.py health`）：pending 1／processing 1／done 889／dead 436（env 81／item 210／other 145），max_session_death_chain 56。⚠按在册律：done 面非单调，判落地只认 `git log` 与 blob。

### 七、[BLOCKER] 登记（本台账**首行**＝⑩1016-19 班强制收班提醒与 chief 1016-2 小步收班纪律已执行；此前 10-15 两班 0 行旧痕不涂）

[BLOCKER] 2026-10-16|⑧B/p08-1016-01|判据缺失|本席开班把"卡柱越表"读成工序5"门柱不一致→不开考"，而在册先例是 106 行中 75 行 unjudged 非空仍照常出 verdict＝本族 65/72 张被过判停在闸外整整一天|docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml（HEAD 106 行，unjudged 非空 75 行：fail 71/pass 2/blocked 2）；尺面见 .runtime/tmp/st-qoder-p08-1016-01/unjudged_precedent.py|⑥/⑩ 把"越表柱进 unjudged 显形"与"不开考"的分界写进生产线 SOP 考工工序 5 真源；本席已按改正尺自开真跑面（16 张越表≤2／11 张宽宇宙）|高
[BLOCKER] 2026-10-16|⑧B/p08-1016-01|判据缺失|截面地板 30 列与本族"卡面自冻 top20 池"结构性互斥：4 张柱齐卡永不可出读数，且不足者被写成 ic_mean=0.0 的假陈述而非 nan|scripts/backtest/fexam/ic_exam.py:96（`ic[valid < 30] = np.nan`，今日盘与 HEAD 同值）；同进程双控 20/24 列→n=0、30/120 列→n=299；卡面 docs/03_modules/_domain_backtest/exam_cards/position_flow/P3/TDM-P-P3-04__calibration__04_缩量回踩支撑对次日正收益预测.yaml「持仓池=多因子 top20」|⑤/⑥ 定策（改卡面宇宙定义 or 为此类卡立"装置不可承重"口径入册）；本席禁改判据故这四张不开考|高
[BLOCKER] 2026-10-16|⑧B/p08-1016-01|流程问题|本席唯一 feasible_now 卡无在册双臂格，"只差一格"到本班才精确到件名（前两班只给叙述）|docs/04_research_records/mining/ledgers/mineloop_campaign/02_binding_book.yaml entries=18（approved 17）本族命中仅 TDM-X-R1-01/comparison/07 与 /07b 且两卡均已 examined；comparison/02 零条目|⑥ 补 TDM-X-R1-01/comparison/02 在册格（卡面 numeric_frozen=True、pending_numeric_params=∅、越表=∅，补格即开跑）|高
[BLOCKER] 2026-10-16|⑧B/p08-1016-01|数据问题|双臂底座唯一取材册仍未入库（⑩1016-19 在册案之**复量续期**，非本席新案）：盘 262,360B／mtime 2026-10-16 00:00:33，而 `git cat-file -e HEAD:` rc=128、`git ls-files --error-unmatch` rc=1、porcelain 读未跟踪态|docs/04_research_records/backtest/scores/2026/indicator_exam_scores_v1.yaml；消费点 scripts/backtest/fexam/exit_sim/exit_simulator.py:72 SCORES_YAML→load_pass_columns() 与 prereg_frozen columns_cap24 逐列逐序＋provenance 全等（本班实测）|⑤/⑥/⑫ 按静态清单律接生成器并入库，或改指已入库真源；本席禁自投非本岗写域|高
[BLOCKER] 2026-10-16|⑧B/p08-1016-01|工具缺陷|绑定册双臂闸作用域是全册并集：任一格带 arms_variants 即拦所有不带 --arms-variant 的装载，含与本跑无关的单卡分诊，本席首张 series 卡 dry-run 即崩|scripts/backtest/fexam/card_binding.py:1933；实测 comparison_exam.py --card docs/03_modules/_domain_backtest/exam_cards/exit_flow/S1/TDM-X-S1-01__comparison__02_六桶分类增益对照.yaml --binding-book docs/04_research_records/mining/ledgers/mineloop_campaign/02_binding_book.yaml 不带旗 ValueError，带 --arms-variant off 通过|⑤ 把该闸作用域收成本跑 card_id 局域判定（不改判据，只改拦哪条路径；承"修喂给闸的输入指向不修门"在册正解）|中
[BLOCKER] 2026-10-16|⑧B/p08-1016-01|流程问题|分数册双册并存且旧址停更，退役判据本班已出但无人签，且 `#rows[N]` 位置指针的解析根至今无权威定义|旧址 docs/03_modules/_domain_backtest/exam_scores_v1.yaml HEAD rows=73 末笔 eb02e513f6；新址 HEAD rows=106（e1033fb48d）；四元组对账 only_old=0 且旧址序列==新址前 73（prefix=True）；本族 5 枚 #rows[N] 对新址全解悬|⑩ 裁旧址退役案与位置指针解析根；本席不自删不自复位|中
[BLOCKER] 2026-10-16|⑧B/p08-1016-01|流程问题|运行面与治理面脱钩续存（他席在册案复量）：六件代码腿已在 HEAD 而三裁定注册表腿未落，本席按原卡继续、不自判停发解除|git merge-base --is-ancestor 23e28b2cb7 HEAD rc=0；ruling_registry HEAD 5025 行内按该三枚新裁编号谓词命中 0，盘 5119 行命中 3|⑫ 修因落地（注册表条目级三向合并伪影族）；⑩ 续按差额呈 Owner|中
[BLOCKER] 2026-10-16|⑧B/p08-1016-01|数据问题|同一件第二根断链指针本班复量仍未修（上班游标 ⑱ 同案续期）：OUT_YAML/OUT_MD 仍指 docs/_working/fexam/，实测父目录 exists=False|scripts/backtest/fexam/exit_sim/exit_simulator.py:77-78|⑤ 改指永久区真源（断链册该条给 D_同名模糊命中＝本岗无改指权，承在册律禁自创新路径）|中
[BLOCKER] 2026-10-16|⑧B/p08-1016-01|需Owner|⑧B 席连续三班 0 出分（10-15 班次 05／06 两袋＋本班），卡池 72 张 preregistered 全压在 §二/§三/§五 三类他席缺件上；本席不自裁"该岗改判或退役"|本台账 §17:57 班次 06 §八＋本班 §二·§六；卡池现值 preregistered=72（磁盘面）；队列四态 pending1/processing1/done889/dead436|⑩ 汇总呈 Owner：本岗改判"普查＋转单岗"，还是先由 ⑤/⑥ 清 §五/§三 缺件再按生产岗计保底|中

### 八、转单段（工序 5：不开考件按 owner 分派，本席零自裁）

- → ⑥（门柱立法／臂协议／册格面）：`TDM-X-R1-01/comparison/02` 补在册格；`X-R1-01/ablation/03` 冻三处臂参数；65 张柱越表卡的并名与立法（词面分裂 `turnover_cost_gate`(11 卡) vs `turnover_or_cost_gate`(10 卡) 承上班游标 ⑳，本席不代并）；`X-S1-03/comparison/02_dualwindow` 卡面无臂协议声明（禁凭记忆补）。
- → ⑤（装置／接线／作用域面）：14 张 preregistered∩needs_matching_engine 缺"横截面权重帧日频组合回放＋逐臂日净值配对"装置（含 `X-S1-01/comparison/02`）；`X-R1/shadow/02` 三根越表柱机器面；§三 截面地板与 top20 池的结构性冲突定策；§五 双臂闸作用域；`exit_simulator.py:77-78` 断链指针；`indicator_exam_scores_v1.yaml` 入库归属（与 ⑫ 共判）。
- → ⑩（归属／清账／呈批面）：旧址分数册退役案；`#rows[N]` 解析根权威定义；本岗岗位性质（普查＋转单 vs 生产岗）连同 §七 需Owner 行上呈。
- 本席边界重申：不改判据、不改门柱、不自投他席写域、不自清他会话卡锁、不自删双册任一面。

## 10-16 22:3x · 班次 02（st-qoder-p08-1016-02）改正尺（上班 ㉖）首次真跑出分 1 张＝连续三班 0 出分止；同 sid 孤儿半班件面被抓并逐字对读＝同卡两读法差 23 倍；本族剩余 71 张六桶机械分账（D 桶本班自纠改判）

### 一、冷启动与防重入（两尺并读＋一枚自犯）

- Python 3.12.8（`python --version` 实测）；`lock_files.py cleanup`＝CLEAN 无死锁；`process_reaper --status` source=live（scanned=27／whitelist_hits=21／killed=0／reported=19），水位 `commit_pct=79.24`、`ram_used_pct=70.9`、`cpu_pct=96.2`、degraded=False、breached=['ALERT-SYS-001']；`dead_archive ok=False rc=1`＝serializer 租约存活（pid=47508）非本班事。
- 防重入两尺：游标末态＝10-16 班次 01 已交账；`lock_files.py list` p08 命中 0（表内仅 ③/④ 席件）；新址 `docs/04_research_records/cross_domain/automation_campaign/p08_examiner_b/checkpoint.md` 现值仍＝`cursor: 未开始`（10-14 搬迁空壳，本班实测）⇒ 旧址承重。
- **自犯一枚（当场入册不涂）**：取号前**未扫 `.runtime/tmp/` 判存**（在册律 `dispatch-engine-outage-session-failed-20261016` ⑨席补证明写"取号前扫tmp判存"），开班 22:30 取 `st-qoder-p08-1016-02` 后，直到 22:54 才在 §三 发现该 sid 下已有 **21:37–22:02 的孤儿半班 11 件**。本班未据此改判班号（台账今日实测 1 班＝01），但撞名风险由本席亲证＝如实立案给 ⑩（下班取号先 `ls .runtime/tmp/st-qoder-p08-<MMDD>-<NN>` 再定号）。
- 会话登记＝`open_session(sid, held_files=[], task_files=[])`＋`_spawn_heartbeat_daemon`（daemon pid=25040，readback=True）；运行面自报 `logical=True downgraded (chief-form verification failed)`＝本席非 chief 形态、按 fail-open 继续（在册 W-29 面）。

### 二、出分 1 张（本班唯一成绩面，逐字凭据）

- 卡 `TDM-X-S1-04/calibration/02_突破失败连续次数前瞻收益`（signal_kind=panel／route=series／宽宇宙全 A 个股）；run_id=`p08b-1016-02-x-s1-04-02`；**verdict=fail**；`ic_mean=-0.000734072650043669`、`ic_ir=-0.009900784848837567`、`oos_ic=-0.004189248317371538`、`n=1665`、regimes 面 bull=-0.003088／bear=+0.004126（**异号**）。册行＝`exam_scores_v1.yaml#rows[109]`，卡 lineage 已回写、status 已翻 examined。
- 工序面（占卡三步原子）：`lock_files.py acquire <卡>` ACQUIRED → `safe_write_text` CAS 翻 `status: examining`（written=True）→ 才开跑；册锁 `docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` 同为本席持有；跑完当场 release 卡锁。
- 注入面对拍（承在册律＋卡面 target_source 逐字）：target=`close/close.shift(1)-1`，执行器 `_panel_metrics` 内部再 shift(-1) ⇒ 配对＝`close[t+1]/close[t]-1`，与卡面 `data_binding.target_source` 声明的 `ch_data.forward_returns(close,1)`（=ch_data.py:194 `close.shift(-h)/close-1`，本班实读）同值；禁注 close 本体、禁 `pct_change()` 默认 pad。
- 物化凭据（`.runtime/tmp/st-qoder-p08-1016-02/card_x_s1_04_02.py`，装载口＝⑦A 席 p07 三面板 parquet 缓存，零新拉数）：1666×5644，**日均名数 4567／最小日名数 230** ⇒ 上班 ㉖ 那条真硬闸（截面 30 列地板）远离且本班另测正/负对照在 §二末；4.6 秒完成；K 分档票日 ＝1:1,759,533／2:893,328／3+:1,392,230；信号取 `sig=-min(K,3)`（承卡面 buckets 冻结面 K∈{0,1,2,3+}，非本席自拟）。
- 册面自证：`[pure-add] minus=0 plus=34 rows 109->110`＋`[promote] written=True before=682ab7cf437164b4 after=a9532fceb0899c94 equals_staging=True`（当场重拷→difflib minus=0 硬闸→CAS，三步齐）。
- **判读约束（新证，给 ⑥/⑩/下游读者）**：`calibration_exam.py:736-748` 的 `judge()` 遇越表键**立即定败且不再往下评估**，故本行 `fails` 只有 `未支持判据键 ['gap_k3_vs_k0_5d_max']` 一条，而真破的 ic_floor（-0.0007 < 0.02）与牛熊异号**只在 metrics 面显形、不在 fails 面**⇒ 上班 ㉖"越表柱进 unjudged 显形"须补一句：显形面在 metrics 不在 fails，**按 fails 归因即错**。
- 装置承重自证（负／正对照同进程，承上班 floor_control）：本卡日均名数 4567 vs 地板 30＝正对照通过（n=1665 非 0）；本班不复造 20 列面（上班已双控 20/24→n=0 且 `ic_stats(空)` 回 0.0 非 nan）。
- GPU：本班走 `fast_rank_ic`（IC_DEVICE 未设＝auto 档），本班未单独读 device_ledger 落盘面 ⇒ **不声明用芯**（禁把回退报成 GPU 读数）；如需精确用芯读数由下班补测。

### 三、同 sid 孤儿半班（21:37–22:02）件面与两读法分歧（本班未删，呈 ⑩）

- 磁盘实测 `.runtime/tmp/st-qoder-p08-1016-02/` 共 20 项：本席 5 件（exam_run.py 22:42／card_x_s1_04_02.py 22:44／block_census.py+json 22:51／apb_triage.json 22:40），**外来 15 件 mtime 21:37–22:02**（open_session.py、probe_faces.py、census_true.py、run_x_s1_04_02.py+json、run_x_s1_04_03.py+json、bucket_gap_x_s1_04_03.py+json、pit_rerun_x_s1_04_03.py+json+log、__pycache__）。
- **未造二次试次（双证）**：①其 `run_x_s1_04_02.json` 首字段 `"dry": true`；②分数册内该卡**仅 1 行**＝本席 rows[109]（本班脚本按 card_id 全表扫出）。⇒ 本班出分合法、DSR 分母未被双记。
- **同卡两读法读数差 23 倍（本班亲读其码）**：其 `build_K` 与本席的三处口径分叉＝(a) 20 日均 volume 用 strictly-prior（`rolling(20).mean().shift(1)`，注释自称"当日计入分母即自指"）而本席按卡面字面取含当日 MA20；(b) K 清零锚点系于"突破发生日 age>20"而本席系于"上次失败起 20 交易日"；(c) 活跃突破期内不允许新突破覆盖（`~act`）而本席按"recency 覆盖"。读数：其 ic_mean=-0.016878／ic_ir=-0.317435／n=1662 vs 本席 -0.000734／-0.009901／n=1665。**两读法都属卡面文字许可范围，且都判 fail（越表键 fail-closed）**⇒ 永久册无"读法申报位"这件事在此卡上被实测放大：同卡两名考工各自物化可差一个数量级，而分数行零字段承载用的是哪一读法。
- `/03` 面**本席更正自己的口头初判并留旧案**：旧案（本班 §五 首稿思路）＝"dragon_tiger reason 仅 2026-08-07 起 ⇒ 46 交易日 ⇒ 不可开考"（承 ④席在册实测）。新案＝该孤儿件实测 `seat_rows=620913`、`days_ge30=1146`、**日均宽度 61 名**（宽宇宙截面地板过），其 5 日/20 日超额分档中位与 gap 均已算出（`pit_rerun_x_s1_04_03.json`/`bucket_gap_...json`）＝**该卡装置可承重，堵点在卡面极性未钉**（其 V1 signed 与 V2 abs-flipped 两读法 ic=-0.00706 vs -0.02969，差 4.2 倍；卡面原文"净卖出越强→信号值越高"两读皆通）。本席不自拟极性入册 ⇒ 转 ⑥。

### 四、本族剩余 71 张堵点六桶机械分账（尺＝`.runtime/tmp/st-qoder-p08-1016-02/block_census.py`，只读零写；prereg 71＝72-本席 1）

| 桶 | 谓词（可 grep） | 首命中 | 全命中 |
|---|---|---|---|
| A panel 截面地板（宇宙=top20/24） | `top20\|top_n=20\|columns_cap24` | 17 | 17 |
| B 分钟线重组 | signal 面含 `kline_1min\|kline_5min` | 7 | 9 |
| C 双臂组合 NAV 装置未接线 | `DefaultBacktestEngine\|sleeve NAV\|组合 NAV\|净值面板` | 15 | 18 |
| D panel 路多日目标（本班**自纠改判**，见下） | primary 含 5/10/20 日 且 无 `target_forward_face` | 6 | 10 |
| E primary 非收益对（概率／中位差／误判率）形状不配 | `probability\|中位差\|误判率\|占比\|实现收益中位` | 5 | 7 |
| Z 待逐张读卡面（含 6 张 feasible_now 臂协议卡） | 以上皆不命中 | 21 | 21 |

- 正对照（防零尺骗人）：谓词 `30\s*只票` 在**全卡库**命中 3 个文件＝尺非零；本桶表 71 张加总＝首命中桶数（17+7+15+6+5+21）。
- **D 桶改判留旧案**：旧案＝"panel 路无多日 forward-face 腿＝结构性不承重"。新案＝腿**可以**靠注入面预补偿达成（孤儿件 `excess(5).shift(1)` 即此配方，与 ⑦c 在册 `t1o_t2c` 双 shift 同族），但真缺两件事＝① `_forward_face()` 只被 `_series_metrics`（calibration_exam.py:212）消费，`_panel_metrics`（:251-252）**硬编码 shift(-1) 且无视申报**⇒ 卡面就算申报了也不生效，此为 ⑤ 的装置腿；② 全库申报 `target_forward_face` 的仅 8 张且全在 entry_flow（已 examined），本族 0 张 ⇒ 此为 ⑥ 的卡面申报位腿。**两腿齐之前，本族 10 张多日 panel 卡不得由考工自拟起算锚入册。**

### 五、转单段（工序 5：不开考件按 owner 分派，本席零自裁）

- → ⑥（卡面申报位／臂协议／册格面，四件精确到件名）：
  1. `TDM-X-R1-01/comparison/02`：上班 §㉙ 说"只差一格"，本班实测**差两格**——该卡 `grep level_to_cap_map` 命中 **0**，五级→仓位映射只活在 `arm_protocol` 散文行原文"（L1 100%/L2 100% 禁新开/L3 梯度 80/60/40%/L4 0%）"；须先给卡补机读 `data_binding.level_to_cap_map`（承 07 在册形态），⑥ 再按 `verify_arm_quote` 建格。绑定册现值 entries=18/approved=17，本族 comparison/02 零条目（本班实测）。
  2. 07 系列的在册格可作**模板不可作取数源**：07/07b 磁盘状态实测仍＝examined（07c＝blocked_on_impl）⇒ 三态尺报的 6 张 feasible_now 里只有 02/ablation03/shadow02 属 preregistered，02 pending=∅、ablation03 pending=['趋势门@无相邻数值','降风险@无相邻数值','预算@无相邻数值']。
  3. 多日 panel 卡的 `target_forward_face/target_horizon_days/mkt_fwd{h}` 申报位（D 桶 10 张）；本族现值 0 张申报。
  4. 极性/锚点未钉的卡：`X-S1-04/calibration/03`（V1 signed vs V2 abs-flipped，读数差 4.2 倍）、`X-S1-04/calibration/02`（K 清零锚＋均量窗两处文字歧义，读数差 23 倍）。
- → ⑤（装置／接线／作用域面）：`_panel_metrics`（calibration_exam.py:251-252）接 `_forward_face` 消费腿；`exit_simulator.py:77-78` OUT_YAML/OUT_MD 断链指针复量仍指 `docs/_working/fexam/`（上班 ⑱ 同案续期）；分数行 `recorded_by` 不落册（run_card 只把它传给 TrialLedger）⇒ 永久册归属唯一靠 run_id 命名约定，是否加列由 ⑤ 定，本席不自改册结构。
- → ⑩（归属／清账／呈批面）：同 sid 孤儿半班 15 件（21:37–22:02）归属判定与清理权（本席不自删）；旧址册退役案仍未签（本班实测 旧址在 HEAD=yes／新址在 HEAD=yes，旧址 HEAD rows 本班谓词读 0 需 ⑩ 换尺）；`working_ref_sweep_20261015/` 在册文件数仍 **0**（上班 §㉝④ 续期）；本岗生产天花板（本班实测＝1 张/班上限，61 张压在他席缺件上）连同需Owner 行上呈。

### 六、本班 [BLOCKER] 行（八条，追加式）

[BLOCKER] 2026-10-16|⑧B/p08-1016-02|判据缺失|同一张冻结卡两名考工各自物化读数可差 23 倍而永久分数册无任何字段承载"用的是哪一读法"——卡面 signal_derivation 的 K 清零锚（上次失败起 20 日 vs 突破发生起 20 日）与"20 日均 volume"含否当日均属文字许可两读|docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml#rows[109]（本席 ic_mean=-0.000734 n=1665）vs .runtime/tmp/st-qoder-p08-1016-02/run_x_s1_04_02.json（孤儿 dry ic_mean=-0.016878 n=1662）；两码并读 card_x_s1_04_02.py:build_signal vs run_x_s1_04_02.py:build_K|⑥ 给卡面补"机读参数位＋读法申报位"（禁考工自拟锚点入永久册）；⑩ 判两读法是否需要并列双试次口径|高
[BLOCKER] 2026-10-16|⑧B/p08-1016-02|判据缺失|panel 路多日目标结构性无申报位：`_forward_face()` 只被 series 路（calibration_exam.py:212）消费，`_panel_metrics`（:251-252）硬编码 shift(-1) 且无视申报；全库申报者仅 8 张且全在 entry_flow⇒本族 D 桶 10 张卡即使 ⑥ 补申报位也仍不生效|scripts/backtest/fexam/calibration_exam.py:212/:251-252；申报普查＝本席脚本扫全 exam_cards 得 8/8∈entry_flow|⑤ 接 panel 消费腿＋⑥ 补卡面申报位（两腿缺一即本族 10 张不可考）；本席禁自拟起算锚|高
[BLOCKER] 2026-10-16|⑧B/p08-1016-02|工具缺陷|`judge()` 遇越表键立即 return，真破门柱不进 fails 只进 metrics——本席首张 ic_floor(-0.0007<0.02) 与牛熊异号双双未进 fails，读者按 fails 归因即得"仅因词表未扩而败"的错结论|scripts/backtest/fexam/calibration_exam.py:736-748（`return "fail", [未支持判据键...]` 早退）；分数行实例 rows[109] fails=['未支持判据键（机判面待扩，fail-closed）: [gap_k3_vs_k0_5d_max]']|⑤ 把早退改"记败＋继续评估已知键"（不改判据阈值只改归因面完整性）；⑥/⑩ 先把"越表卡按 fails 归因"禁令写进 SOP 工序 5|中
[BLOCKER] 2026-10-16|⑧B/p08-1016-02|流程问题|本席取号未扫 tmp 判存（在册律明写要扫），撞名同 sid 的 21:37–22:02 孤儿半班 15 件直到 22:54 才被发现；本次侥幸未造二次试次（双证：其 json 首字段 dry=true＋册内该卡仅 1 行），但该律靠本席自犯再次证伪其可跳过性|.runtime/tmp/st-qoder-p08-1016-02/ mtime 面 20 项＝本席 5/外来 15；册面 card_id 全表扫＝rows[109] 唯一|⑩ 把"取号前扫 tmp 判存"从席位自律改入门禁或卡面工序 1；孤儿 15 件归属与清理权交 ⑩（本席不自删）|中
[BLOCKER] 2026-10-16|⑧B/p08-1016-02|流程问题|上班 §㉙ 给 comparison/02 的"只差一格"实测是差两格：该卡无机读映射位（grep `level_to_cap_map`＝0），五级→仓位映射只活在 arm_protocol 散文行；⑥ 的活先补卡面机读位再建格|docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/TDM-X-R1-01__comparison__02_熔断五级梯度减仓对照.yaml:50（arm_protocol 原文 L1 100%/L2 100% 禁新开/L3 梯度 80/60/40%/L4 0%）；绑定册 02_binding_book.yaml entries=18 approved=17 本卡零条目|⑥ 按 07 在册形态给 02 补 data_binding.level_to_cap_map＋走 verify_arm_quote 建格；本席禁凭 07 的臂自补|高
[BLOCKER] 2026-10-16|⑧B/p08-1016-02|数据问题|本席对 `X-S1-04/calibration/03` 的"跨度不足不可开考"初判被同 sid 孤儿件实测证伪并当场改判：seat_rows=620913／days_ge30=1146／日均宽度 61 名＝截面地板过、装置可承重；真堵＝卡面极性未钉（V1 signed ic=-0.00706 vs V2 abs-flipped ic=-0.02969 差 4.2 倍）|.runtime/tmp/st-qoder-p08-1016-02/pit_rerun_x_s1_04_03.json＋bucket_gap_x_s1_04_03.json＋pit_rerun.log 三件；卡 docs/03_modules/_domain_backtest/exam_cards/exit_flow/S1/TDM-X-S1-04__calibration__03_席位净卖出派发前瞻收益.yaml|⑥ 在卡面钉死极性定义（净卖出取带符号还是绝对值翻向）；本席不自拟；旧案措辞按在册更正律另起留档不涂改|中
[BLOCKER] 2026-10-16|⑧B/p08-1016-02|流程问题|本岗生产面天花板实测＝1 张/班（改正尺真跑后仍如此）：71 张 preregistered 六桶分账全落他席缺件（A17 截面地板／B7 分钟线／C15 组合 NAV 装置／D6 多日腿／E5 形状不配／Z21 待逐张），其中 A+C+D 三桶＝38 张卡在 ⑤/⑥ 补腿前**任何考工班都不出分**|.runtime/tmp/st-qoder-p08-1016-02/block_census.json（谓词见 §四 表，正对照＝`30\s*只票` 全库命中 3 文件非零尺）；本席出分面 docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml#rows[109]|⑩ 汇总呈 Owner：本岗改判"普查＋转单岗"或先由 ⑤/⑥ 清 A/C/D 三桶再按生产岗计保底（本席不自裁）|高
[BLOCKER] 2026-10-16|⑧B/p08-1016-02|需Owner|收班八件第⑧项"零 worktree 确认"在现实现下仍不可由席位自律达成：本班全程未调用任何工棚/工作树入口，但 `open_session` 注册即产 `.aidrafts/<sid>` 自动壳＋30s 心跳守护（①席在册案复量续期，本席为第 N 席复证）|.runtime/locks/heartbeat_st-qoder-p08-1016-02.pid（本班实测存在）；`.aidrafts/` 面本班零自起、未自删；案卷=memory auto-spawned-aidrafts-worktree-shell|⑩＋Owner 判该自动壳是否豁免于"禁建 worktree"令面；本席不自删|中

### 七、本班收班读数（八件逐项，现测非终值）

- ①claim：卡锁跑完当场 release；册锁由提交门在入队时统一释放（在册实测＝入队成功即代放全部 claim，故本件判据是"袋是否落地"非"是否漏 release"）。②心跳：daemon pid=25040 按 PID 核活后终止＋`unregister`。③实耗：见游标 last_run 现测。④[BLOCKER]：§六 八条已落（`grep -c "\[BLOCKER\]" ledger.md` 收班实测见 §七末）。⑤自清：本席 5 件尺面保留（游标按路径引它们当凭据，删即造断链锚）＋`__pycache__` 当场删；外来 15 件不动呈 ⑩。⑥GPU：本班未声明用芯（未单独读 device_ledger，见 §二末，禁把回退报成 GPU）。⑦子任务：本班零 spawn。⑧worktree：`.worktrees/st-qoder-*` 本班零创建；`.aidrafts/<sid>` 自动壳见 §六 第 8 条。
- 出分面：1 张（保底 ≥8 未达，如实呈报；根因＝§四 六桶全在他席缺件，本席未自造读数、未弱化任何闸）。

### 八、收班补记（第二袋在册，含一处本席尺面自纠＋在途袋实测）

- **尺面自纠（给 ⑥ 立法优先级，另起留旧案不涂改）**：上班 ㉖ 用「新址册 106 行中 75 行 `unjudged` 非空仍照常出 verdict」作「越表柱不是不开考理由」的凭据——本班按同册复量四个子面（现值 110 行）：`unjudged` **整面非空=79**，但其中 **79 行全部来自 `pillars_prose_keys`（文字门柱原样回填，凡出分即非空＝无判别力）**；真·越表数值柱 `numeric_keys_not_read` 非空＝**3**；`numeric_keys_no_machine_face`（读了但无面，如 panel 路 mono 恒 None／ic_ir 未接）＝**45**；`fails` 含「未支持判据键」＝**3**，其中 fails 仅此一条（＝其余柱根本没被评估）＝**1＝本席 rows[109] 自身**。⇒ 结论方向不变（越表照常出分，本席已亲证），但**「75 张待词表立法」是把 prose 回填面当越表面的 25 倍误读，真面＝3**；⑥ 排工请按 3 排，另按 45 排「无机器面」腿（那是 ic_ir/mono 接线，非立法）。正对照＝同脚本读整面 79 可复现上班量级；负对照＝`pillars_prose_keys` 对 pass 行同样非空（2 行 pass 亦在 79 内）＝该键确为无条件回填。
- **在途袋实测（本席不轮询等待，但按门给的出口如实报）**：首袋 `q-20261016-st-qoder-p08-1016-02-0001`（files=4）入队 23:05:00，**06 秒后即被同路他袋 `q-20261016-st-qoder-p07-1016-02-0003` 以 `trigger=eviction` 打 `.stale` 标记**（`.runtime/commit_queue/pending/.stale/<本袋>.json`，mtime 23:05:12，字段仅 qid/stale/stale_by/stale_at/trigger，无 dead_reason）；pending 正本仍在、dead/ 与 done/ 零命中、`commit_queue status` 读 state=pending，head 为他席 40 文件袋 waiting≈807s 且 `daemon.online=false`。⇒ 落地与否本班无法证实，**判据面一律以 `git log -- <四件路径>` 为准**，本席不据 pending 报"已落地"。
- **超集判定（另投前置，逐件实测非推断）**：0001 快照四件 blob vs 现盘逐件 `minus=0 plus=0`（字节全等 4430/145458/150202/27191）⇒ 第二袋（含本节＋游标 ㊹）对首袋为**严格超集**，两袋同序（FIFO 先 0001 后 0002）终值＝超集，非回退弹；本席不自销他袋、不动 pending/.stale 面。
- **本班收班读数（`date` 实测 2026-10-16 23:12:49）**：出分 1 张（保底 ≥8 未达，根因见 §四 六桶与 §五 转单，本席未自造读数、未弱化任何闸）；`[BLOCKER]` 行首本班累计 **9** 条（§六 8 条＋下方 §八 1 条尺面自纠）；claim 面＝入队续租 ttl=7200s 后由本席 `--release-only` 收尾；心跳 daemon pid=25040 按 PID 核活后终止（禁 /IM 全杀，在册红线）；`.worktrees/st-qoder-*` 本班零创建、`.aidrafts/<sid>` 自动壳未自删（§六 第 8 条）；本班零 spawn 子任务；GPU 用芯未声明（未读 device_ledger，禁把回退报成 GPU 读数）。

[BLOCKER] 2026-10-16|⑧B/p08-1016-02|判据缺失|上班 ㉖ 的「册 106 行中 75 行 unjudged 非空」被当「越表柱面」引用＝把无条件回填的 `pillars_prose_keys` 子面误当数值越表面，真面差 25 倍（⑥ 若按 75 排词表立法即错排工）|docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml 现 110 行：整面非空 79／`numeric_keys_not_read` 非空 3／`numeric_keys_no_machine_face` 非空 45／fails 含未支持判据键 3（其中仅此一因 1＝本席 rows[109]）；负对照＝2 行 pass 同样带 prose_keys 非空|⑥ 按 3 排词表立法、⑤ 按 45 排「读了无机器面」接线腿；⑩ 把 SOP 工序 5 的「越表」措辞钉到 numeric_keys_not_read 子面|中

## 10-16 23:34 开班 · 班次 03（st-qoder-p08-1016-03）本班出分 0 张＝本族真可考面经 CH 宽度实测收敛为 0（上班 Z 桶"待逐张"两张疑似可考被实测打死：封死名数/日 days_ge30=4/697、IPO 首日名数/日 days_ge30=1/1038）；头号账面更正＝三席共用宽面板缓存已被清扫，但定级本席自纠＝重拉实测仅 56.3 秒/列（效率损失非能力阻断）；㊸ 下班首查四件逐件复量全部未动

### 一、冷启动与防重入（三尺并读＋取号前扫 tmp 已按上班 ㊱ 执行）

- `python --version`＝3.12.8（23:34:00 现测）。`lock_files.py cleanup`＝CLEANED 3 枚死锁（全部 ⑫ 席四件套）＋SALVAGED 死会话 `st-qoder-p01-1016-03` 遗物（merge=skipped／stash=0 件／释放 claim=0）＝本席未触。
- `process_reaper --status`＝`source=live`／scanned=32／whitelist_hits=26／killed=0／reported=23／ghosts killed=0／水位 `commit_pct=78.03`、`ram_used_pct=72.1`、`cpu_pct=57.1`、degraded=False、breached=[]；`dead_archive ok=False rc=1`＝serializer 租约存活（pid=47508）＋全量模式自挡，非本班事（在册同值续期）。
- 防重入三尺：①游标末态＝10-16 班次 02 已交账（23:02:12 现测）；②`cleanup` 面 p08 零命中；③**取号前扫 `.runtime/tmp/st-qoder-p08-1016-*`**（承上班 ㊱ 本席自犯律）＝仅 01（12 件）/02（23 件）两目录⇒本班取 **03** 无撞名、无孤儿半班混入。
- 会话登记＝`open_session(sid, held_files=[], task_files=[])`＋`_spawn_heartbeat_daemon`（daemon pid=**40224**，`heartbeat_st-qoder-p08-1016-03.pid` 回读＝40224）；运行面自报 `logical=True downgraded (chief-form verification failed)`＝按 fail-open 继续（在册 W-29 面，非本班事）。
- 上班在途袋面（㊺ 首件已解）：`git log` 命中 `0b3c365c74`（02 班主袋）＋`a54015c19f`（第三袋收班补记）⇒ 盘上四件＝HEAD 现值，本班无须重投、未 requeue 任何袋。
- 卡池五态（磁盘面全库，供 ⑩ 对账，本班非终值）：preregistered **162**／empty 208／examined 87／examining **1**／blocked_on_impl 48／blocked_on_data 71＝加总 577。`examining` 那一枚＝`entry_flow/L3/TDM-E-L3-03-2__calibration__03_温和放量.yaml`（⑦c 席 1016-01 自报"已占卡未开考＝班限已到"续存）＝**非本席写域，本席不翻不回，交 ⑩ 按僵卡规程处置**。

### 二、本班出分面＝0 张（分数册零 only-add；判据全部实测凭据，非散文判）

- 分数册现测（23:59）＝145,458B／sha16 `a9532fceb0899c94`／rows **110**＝上班收班读数逐字节同值⇒22:3x 后全线零新增，本班未写册（无二次试次风险、无 ComposerError）。
- 本族领面＝preregistered **71** 张（磁盘面，＝上班 72−上班出分翻 examined 1 张；目录实名 exit_flow/portfolio_flow/position_flow）；family 分账＝comparison 37／shadow 14／calibration 13／ablation 7＝71；route＝series 42／dual_arm 29。
- **本班新尺**（`.runtime/tmp/st-qoder-p08-1016-03/census_fine.py`，只读零写，产物 `census_fine.json` 逐张带**命中原文片段**禁空判）五谓词分账：`h_arm`(臂协议/双臂) 31 张、`h_univ`(宇宙=持仓池/月频调仓/prereg_frozen/top20/columns_cap24) 28 张、`h_nav`(组合 NAV 装置) 17 张、`h_multi`(primary 多日且无 `target_forward_face`) 9 张、`h_min`(分钟线) 10 张；**四者全不命中＝8 张**。
- 那 8 张的族闸归属：6 张 family∈{comparison,shadow} 且 primary 是臂间差/成本面（净额轧平、切账失真、预算带插值…）⇒ 须 `comparison_exam`＋绑定册臂格（本族 prereg 臂格命中＝**0**，见 §四①）；2 张 family=calibration＝本席逐张实测（下条）。
- **实测打死两张"疑似可考"（承 ㉖ 改正尺：真硬闸＝截面 30 列地板，`ic_exam.py:96`）**：
  - `TDM-X-S2-02/calibration/02_连续跌停开板概率与次日处置`（卡面 `signal_kind: series` 但 derivation 是**个股级** N 档＝形状自相矛盾）：SQL 原文见 §五，读数＝封死（`close<=limit_down`）名数/日 **days_ge30=4／days_total=697／max=125／avg=2.48／min=1** ⇒ 按个股截面读法在 693/697 日（99.4%）撞 30 列地板＝`ic_stats(空)` 回 0.0 非 nan 的假红发生器（在册三复证族）；按日频标量读法则须自拟"个股级 N 档→日频概率"聚合口径（卡面无申报位）⇒ 本席禁自拟，不开考。
  - `TDM-X-S2-02/calibration/03_新股首日分层卖出三臂`：读数＝IPO 首日名数/日（`uniqExact(symbol)` 按 `list_date`）`days_ge30=`**1**／days=1038／max=31／median=2／avg=1.99 ⇒ 同一地板；另卡面自述 `issue_price` 面 2015..2023-08 段局部 blocked_on_data、primary 是**三臂中位差**且 target 含 T+1/T+5/T+20 多日＝D 桶在册禁自拟锚（上班 ㊴），且 `comparison_exam.py:202` 的族闸会拒 calibration 族代考⇒ 不开考。
- **对上班尺的纠偏（另起留旧案，不涂上班 ㊳ 表）**：上班六桶＝正则面（A17 系 `top20|top_n=20|columns_cap24`），未覆盖"月频调仓/持仓-日/新股首日/封死档"这类**宇宙词与事件宽度**；本班实测面＝A 桶实质 ≥19 张（17＋上两张）。方向是**收紧**，与本席 10-15 在册"endswith 过宽假扩"同族教训。
- 结论：**本族 preregistered 71 张在本班口径下真可考面＝0**（非"本班省力"）＝⑤ panel 多日腿未接（§四②）＋⑥ 臂格未建（§四①）＋⑥ 读法申报位未补（上班 [BLOCKER] 高续存）三件他席缺件的合取。

### 三、三席共用宽面板缓存断料＝本班头号账面更正（含定级自纠）

- 磁盘实测（23:55）：`pd.read_parquet` 对 `.runtime/tmp/p07/shift06_close.parquet`／`shift06_hfq_high.parquet`／`shift06_hfq_volume.parquet`／`shift06_open.parquet`／`shift06_mask.parquet` **五件全 FileNotFoundError**；同目录 `shift06_chips_winner_load.json`／`shift06_conc_90_load.json` 仍在（各 396B，mtime 10-16 15:32）＝缓存曾在该处生成、其后被清扫面收走。全库 `.runtime/tmp` 现仅 **6** 枚 parquet（`find` 实测），其中 4 枚属 ⑦c 席 1016-02 班自家信号面件。
- 命中面＝**三席**（产者⑦A、消者⑧B 与⑦c）：本席上班在册驱动 `card_x_s1_04_02.py:load_aligned` 读 close/high/volume 三件⇒现测不可跑；⑦c 席在册 `run02.py:base()` 读 `shift06_close/open/mask` 三件⇒同一断料同命。
- **定级本席自纠（禁把事故报大）**：`ch_data.load_close('2019-01-04','2025-09-09')` 现测 **elapsed=56.3 秒**、shape **1622×5642**、日均名数 4680／最小日名数 3564 ⇒ 五列全重拉≈5 分钟＝**效率损失，非能力阻断**。（首报口径曾按 ⑦c 在册"首拉 45.7 分"心算成致命级，被本班实测推翻；旧口径留卷不删。）
- **两席独立复证（非本席单方读数）**：⑦A 席 1016-03 班同口逐列现测＝`load_panel` 单列全市场宽面板 **12–62 秒**、四列合计 104.4 秒（该席台账 `docs/_working/automation_campaign/p07_examiner_a/ledger.md:1095-1104`，并已在同文件 :1142 立案翻掉"45.7 分/两列⇒单班吃满"这条被下游当承重用的节拍依据）⇒ 本班 56.3 秒落在其带内，两席各自独立把同一条在册节拍依据判为不复现。
- 给 ⑫/⑩ 的准确口径：清扫面若不给共享只读缓存加白名单（形如 `shift06_*.parquet`／`*_wide.parquet`），代价＝三席×每班≈5 分钟重复拉数＋CH 并发压力；若加白名单，须同时定"谁有权删"（本席不自取）。

### 四、㊸ 下班首查四件＝本班逐件复量，四件全部未动（现测非引用上班）

1. `grep level_to_cap_map` 对 `exit_flow/X1/TDM-X-R1-01__comparison__02_熔断五级梯度减仓对照.yaml`＝**0 命中**；`02_binding_book.yaml` 现测 entries=**18**／approved=**17**，本族命中仅 `comparison/07` 与 `/07b` 两格（两卡均 examined）⇒ ⑥ 既未补卡面机读映射位、也未建格（上班 ㊵ 续存）。
2. `scripts/backtest/fexam/calibration_exam.py:251-252` 现值仍 `_panel_metrics(...)` 内 `ret = target.shift(-1)` **硬编码**；`_forward_face` 消费点仍只 `:212`（series 路）⇒ ⑤ panel 腿未接，本族多日 panel 卡（`h_multi` 9 张）仍不可考。
3. 同 sid 孤儿面：`.runtime/tmp/st-qoder-p08-1016-02/` 现 **23** 项，其中 mtime 21:37–22:02 的 15 件外来半班件仍在位（上班已呈 ⑩）＝归属与清理权仍悬，本席未删未改。
4. 旧址册 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml` **仍在 HEAD**（`git cat-file -e` rc=0）⇒ ⑩ 退役案未签；`git ls-files docs/04_research_records/governance/working_ref_sweep_20261015/`＝**0**⇒ 断链三件入库义务连续第 N 班未执行（本席无写权，不自补）。

### 五、转单段（工序 5：不开考件按 owner 分派，本席零自裁；SQL 原文可复跑）

- 封死宽度尺（⑥/⑩ 复跑）：`SELECT countIf(n>=30), count(), max(n), min(n), avg(n) FROM (SELECT td, count() AS n FROM (SELECT a.trade_date AS td, a.symbol AS s FROM (SELECT trade_date, symbol, close FROM c1_market.kline_daily_hfq WHERE trade_date>='2019-01-04' AND trade_date<='2025-09-09' AND close>0) a INNER JOIN (SELECT trade_date, symbol, limit_down FROM c1_market.stk_limit WHERE trade_date>='2019-01-04' AND trade_date<='2025-09-09' AND limit_down>0) b ON a.trade_date=b.trade_date AND a.symbol=b.symbol WHERE a.close<=b.limit_down) GROUP BY td)`
- IPO 首日宽度尺（⑥/⑩ 复跑）：`SELECT max(n), avg(n), quantile(0.5)(n), countIf(n>=30), count() FROM (SELECT list_date, uniqExact(symbol) AS n FROM c1_market.stock_basic WHERE list_date>='2019-01-04' AND list_date<='2025-09-09' GROUP BY list_date)`
- 转 **⑥**：(a) `X-S2-02/02` 卡面 `signal_kind: series` 与 derivation 的个股级 N 档互斥⇒需族/形状认定＋日频聚合申报位（若判 panel 则实测宽度已不足，建议改判 blocked_on_shape 而非留 prereg）；(b) `X-S2-02/03` 的三臂中位差属对照族而 family=calibration⇒族归位由 ⑥ 判，本席不代改族；(c) comparison/02 机读映射位（续上班）。
- 转 **⑤**：panel 多日 `target_forward_face` 消费腿（续上班 [BLOCKER] 高）；另新增一条＝`ch_data.ch_query` 把 HTTP 404 一律包成 `CHAccessError` 且只回显 `sql[:120]`（`ch_data.py:103`），复杂 JOIN 排障看不到真因（本席两次才通：`ANY LEFT JOIN…USING`＋`period='daily'` 组合 404，改内联子查询＋`INNER JOIN…ON` 才返回）。
- 转 **⑫/⑩**：共享宽面板缓存白名单（§三）；`entry_flow/L3/TDM-E-L3-03-2__calibration__03` 的 examining 僵卡（⑦c 写域）由 ⑩ 翻回。
- 转 **⑨**：本班零新分数行⇒无新增覆盖型 fail；上班 rows[109] 的"fails 面早退、真破柱只在 metrics"判读约束续期未解。

### 六、本班 [BLOCKER] 行（五条，追加式，逐条当场入册非班尾攒写）

[BLOCKER] 2026-10-17|⑧B/p08-1016-03|判据缺失|本族 preregistered 71 张经"五谓词＋CH 宽度实测"两级尺收敛为真可考面 0 张；上班六桶正则面系统性偏松（未覆盖月频调仓/持仓-日/新股首日/封死档等宇宙词），A 桶实质 ≥19 张而非 17|.runtime/tmp/st-qoder-p08-1016-03/census_fine.json（逐张带命中原文片段）＋封死面 days_ge30=4/697、IPO 首日 days_ge30=1/1038（SQL 原文见 §五）＋docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml 现测 rows=110 sha16 a9532fceb0899c94 未变|⑩ 汇总呈 Owner：本岗在生产岗口径下连续两班 0/1 张＝改判"普查＋转单岗"或由 ⑤/⑥ 先清 §四①② 两腿；本席不自裁|高
[BLOCKER] 2026-10-17|⑧B/p08-1016-03|数据问题|三席共用宽面板缓存被清扫面收走（⑦A 产、⑦c/⑧B 消），上班在册真跑驱动现测装载口五件全 FileNotFoundError；定级经本席实测纠正为效率损失非能力阻断＝重拉 56.3 秒/列（五列≈5 分/席/班）|.runtime/tmp/p07/shift06_{close,hfq_high,hfq_volume,open,mask}.parquet 五件 FileNotFoundError（23:55 现测）；同目录 shift06_chips_winner_load.json／shift06_conc_90_load.json 396B mtime 10-16 15:32 仍在＝曾生成；load_close 计时读数 REPULL elapsed_s=56.3 shape=(1622,5642)，与 ⑦A 席 1016-03 同口独立读数（单列 12–62 秒，p07_examiner_a/ledger.md:1095-1104・:1142）互证|⑫ 给共享只读缓存加白名单（形如 shift06_*.parquet／*_wide.parquet）并定"谁有权删"；⑩ 判清扫面边界；本席不自取删权|中
[BLOCKER] 2026-10-17|⑧B/p08-1016-03|工具缺陷|fexam 只读 CH 层把 HTTP 404 一律包成 CHAccessError 且异常只回显 sql[:120]，复杂 JOIN 排障看不到服务端真因（本席首版 ANY LEFT JOIN＋USING＋period='daily' 404，改内联子查询＋INNER JOIN ON 才通，中间一次无效重试）|scripts/backtest/fexam/ch_data.py:103（`raise CHAccessError(f"CH 查询失败: {exc}: {sql[:120]}")`）；两次 SQL 全文在本台账 §五|⑤ 把 CH 响应体/错误码截进异常 details（不改判据只改可诊断性）|中
[BLOCKER] 2026-10-17|⑧B/p08-1016-03|工具缺陷|本席自犯入册：计时探针把待报数值与派生量写在同一 print，`df.memory_usage(deep=False).memory`（DataFrame 上无 `.memory` 属性）抛 AttributeError 连带丢掉已跑完的 elapsed 读数，须整跑重试才拿到 56.3s|首跑 traceback 止于 pandas/core/generic.py:6321（'Series' object has no attribute 'memory'）而 pull 已成功；重试输出 elapsed_s=56.3|本席当班改正（计时类探针先 print 待报值再算派生量）；无需他席动作|低
[BLOCKER] 2026-10-17|⑧B/p08-1016-03|流程问题|在册账面债连续续期且本席无写权＝旧址分数册退役案未签（仍在 HEAD）＋断链册 working_ref_sweep_20261015 目录 git ls-files 仍 0＋⑦c 写域 1 张卡停在 examining 无人翻|git cat-file -e HEAD:docs/03_modules/_domain_backtest/exam_scores_v1.yaml rc=0；git ls-files docs/04_research_records/governance/working_ref_sweep_20261015/ 计数 0；卡池五态 examining=1＝entry_flow/L3/TDM-E-L3-03-2__calibration__03_温和放量.yaml|⑩ 按僵卡规程翻该卡并排断链册入库与旧址退役案；本席不代翻代删|中

### 七、本班收班读数（八件逐项，现测非终值）

- ①claim 全部当场 release（ledger/checkpoint/两把册锁；见收班命令面回执）；②心跳按 pid=40224 核活后终止＋60 秒双读进程表与 heartbeat jsonl 末行 pid 复证（承在册 closeout-order-land-bags-before-unregister 处方）；③实耗＝开班 23:34:00 现测至收班 date 现测，终值以游标 last_run 两戳差计，本席不写自估；④[BLOCKER] 5 条（§六，高1/中3/低1）；⑤自清＝`.runtime/tmp/st-qoder-p08-1016-03/` 本班件（open_session/census_runnable/census_fine/json/land 脚本）按在册 ㊱ 与 ⑫ 白名单案**保留给下一班复用尺面**，本席不自删并如实呈 ⑩；四件套外零散落、项目根零临时件；⑥GPU＝本班未 acquire 看门人（零 ic 实跑）⇒免执行且本班零分数行、无"回退报成 GPU"风险；⑦零 spawn 子代理⇒零孤儿；⑧零 worktree＝本班未调用任何工棚/工作树入口（`.aidrafts` 自动壳若出现按在册 auto-spawned 案呈 ⑩，本席不自删）。
- 并发避让：本班只写自家四件二面（ledger.md＋checkpoint.md）；卡面零翻（无开考故无 examining/examined 写）；分数册零字节；known_data_gaps.yaml 零字节；判据/门柱/阈值零改动；无 requeue、无代投他席件、无裸 git commit。


## 10-17 00:30 开班 · 班次 01（st-qoder-p08-1017-01）本班出分 0 张＝第二把独立尺（判官可评面 ↔ 卡面冻结柱）复证上班"本族真可考面 0"，并把堵点从"数据能不能构造"改判为"构造出来也没有可评面"（71 张中 64 张越表、其中 38 张真柱被 judge 早退吞）；本席自纠三枚当场入卷（v1 把双臂累积记败混算成早退＝假扩；J5"卡面自陈缺件＝不可考"被 32/87 已出分卡证伪＝判废；落袋器解包名写错＝崩于断言前零写）

### 一、冷启动与防重入

- `python --version`＝3.12.8（00:30:12 `date` 现测同帧）；`setup_dev_env.py --check`＝usercustomize 存在且指向 D:\ZephyrAlpha（LSG 运行时网引导在岗）。
- `lock_files.py cleanup`＝CLEANED 7 枚死锁（⑩线长 ledger/checkpoint、dispatch、pulse、cmd_ledger、②席两件）＋SALVAGED 死会话 `st-qoder-p02-1016-01`／`st-qoder-p02-1016-04`／`st-qoder-p04-1016-05` 三枚遗物（merge=skipped／stash=0 件）＝**全部非本席名下**，本席未触未改。
- `process_reaper --status`＝`source=live`／last_run=2026-10-17 00:30:51／scanned=33／whitelist_hits=28／killed=0／reported=26／drift(stash=27, worktree_changes=1428)；水位 `commit_pct=88.76`、`ram_used_pct=88.9`、`cpu_pct=87.8`、degraded=False、breached=[ALERT-SYS-001, ALERT-SYS-004, ALERT-SYS-005]；`dead_archive ok=False rc=1`（在册续期形态，非本班事）。**本班据此零并发起批**（水位 88.76 承在册"起批前先读 commit_pct"律＋实跑窗将闭）。
- 防重入三尺：①游标末态＝10-16 班次 03 已交账（游标行与 §㊾ 00:04 落笔，本班 00:31 读到）；②`cleanup` 与 `lock_files.py list` 面对 p08 零命中；③**取号前扫 `.runtime/tmp/st-qoder-p08-*`**（承在册 ㊱ 本席自犯律）＝最大号止于 `st-qoder-p08-1016-03`、`1017` 面零目录（00:33 现测）⇒本班取 **st-qoder-p08-1017-01**，无撞名、无孤儿半班混入。
- 会话登记＝`open_session(sid, held_files=[], task_files=[])`＋`_spawn_heartbeat_daemon`（daemon pid=**56760**，`heartbeat_st-qoder-p08-1017-01.pid` 回读＝56760）；运行面自报 `logical=True downgraded (chief-form verification failed)`＝按 fail-open 继续（在册 W-29 面，非本班事）。
- **本班工序时序事实（如实上报，不是免责）**：00:30 开班×**CH 窗 01:00–04:00 禁跑**（指令卡工序 5）⇒实跑窗仅 30 分钟，而"重拉宽面板（上班实测 56.3 秒/列，五列≈5 分）→构造→同帧双对照→出分→CAS 入册"一条腿在 00:46:30 `date` 现测时点已不可能于 01:00 前走完；本班据此把工序 3–4 改为纯本地尺面（**零 CH 调用、零 GPU acquire**），如实报 0 出分，不硬跑造二次试次也不造假红。

### 二、本班头号＝第二把尺（判官可评面），与上班尺的分工

上班（1016-03）尺问"这张卡的信号与目标**能不能构造出来**"（五谓词＋CH 宽度实测）；本班尺问另一件——**构造出来了，判官这一班能不能评**。两尺独立、盲区互补，且本尺不碰 CH。

尺面＝`.runtime/tmp/st-qoder-p08-1017-01/census_judge_face_v2.py`（只读零写，产物 `judge_face_v2_own.json`／`judge_face_v2_all.json`）。闸定义逐条给代码锚（00:4x–01:0x 现读源码）：

- `judge():741-747` 与 `judge_event():841-843`：`pillars_numeric` 越该 route 词表 ⇒ **立即 return**，其余柱一条不评（上班 ㉟ 已就单信号面立案，本班补事件面同款）。
- `_judge_comparison():594-597`：同款越表键 ⇒ **累积记败不吞**，其余柱照评。⇒ 早退与累积是两种命运，混算即假扩（本班 v1 就栽在这里，见 §四）。
- `_series_metrics:242` 恒 `ic_ir=None`；`_panel_metrics:270` 恒 `mono_spearman=None`。二者均被 `_unjudged_pillars:355-361` 如实写进 `numeric_keys_no_machine_face`（**非静默**，本席不把它报成隐身缺陷）。
- `_n_buckets_from_card:140-151`：桶型词表只有 8 个分位词＋`quantile_\d`；卡面自造桶名一律落缺省 10 桶。

本族 71 张 preregistered 读数（00:5x 现测）：

| 面 | 读数 |
|---|---|
| route | series **42**／dual_arm **29**／event **0**（本族无事件路卡） |
| 越表（`pillars_numeric ⊄` 该 route 词表） | **64 张**；零越表 **7 张**；distinct 越表键 **106 个** |
| SWallow（series 路越表＝真柱全被早退吞） | **38 张** |
| ADDfail（双臂路越表＝只多一条 fail、其余照评） | **26 张** |
| TOP 越表键 | `maxdd_delta_max`15／`sharpe_vs_baseline_min`14／`turnover_cost_gate`11／`tracking_diff_max`10／`turnover_or_cost_gate`10 |
| 桶名不在册（kind=series） | **24/25 张**，21 种自造名（`arm_matrix`3、`allocator_scheme`2、`state_cell_attribution`2 等）⇒ 静默换 10 分位桶 |
| 冻 `ic_ir_min` 而 series 面无 ic_ir | **2 张** |
| 冻 `mono_spearman_min` 而 panel 面无 mono | **12 张** |

**预判决柱一枚（本班新发现，非上班在册面）**：`_judge_comparison:598-600` 对 `misfire_reduction_min` **无条件追加**"无机判面（缺笔级价格面，W4 绑定层后重考）"，与任何读数无关 ⇒ 凡冻此柱者必得 verdict=fail＝那不是考试而是预判决。本族冻此柱 **1 张**＝`TDM-X-S1-01/comparison/02_六桶分类增益对照`（它恰是本班尺下唯一"判官面五闸全清"的卡，见 §三）。

### 三、两尺求交＝真候选 0，7 张零越表卡逐张有第三把闸的独立证据

尺面＝`.runtime/tmp/st-qoder-p08-1017-01/joint_candidates.py`（只读，产物 `joint_candidates.json`；上班尺产物按只读引用复制为 `census_fine_ref.json`，未改他席原件）。

- 零越表 7 张＝`X-S1-01/comparison/02`、`X-R1-01/comparison/02`、`X-S1-03/comparison/02_dualwindow`、`P-P1-02/calibration/02`、`P-P1-02/calibration/04`、`P-P1-04/calibration/04`、`P-P3-04/calibration/04`。
- **前三张＝双臂路**：本班现测 `docs/04_research_records/mining/ledgers/mineloop_campaign/02_binding_book.yaml` entries=**18**／approved=**17**，本族格仅 `X-R1-01/comparison/07`＋`/07b`（两卡均 examined）⇒ 三卡零臂格；`level_to_cap_map` 对 `X-R1-01/comparison/02` 与 `X-S1-01/comparison/02` 均 **0 命中**（承上班 ㊵/㊽① 续期，本班重跑非引用）。`X-S1-01/comparison/02` 另叠一枚代码级钉＝`grep -c "confirm" scripts/backtest/fexam/exit_sim/exit_simulator.py`＝**0**、`simulate()` 形参面 `:183-193` 现值只有 `stop_enabled / stop_mult / commission` ⇒ 卡面要求的"按桶分流确认层"形参不存在（属 ⑤/⑪ 装置腿），且它正是冻 `misfire_reduction_min` 的那张（预判决柱与其唯一交集）。
- **后四张＝panel 冻结 top20 持仓池路**，撞 `ic_exam.py:96` 的 30 列地板＝**引上班在册实测**（游标 notes ③：10-15 班次 04 同帧双对照 seed=7，20 列面回 `ic_mean=0.0000` 把"截面不足"写成"信号无信息"），本班未重烧（CH 窗内）⇒ 该四张定性沿用上班读数，**非本班现测**，下班若要改判须自己做同帧双对照。
- 求交结论＝**真候选 0 张**。本族"可考面 0"至此由**两把互不依赖的尺**（数据构造面／判官可评面）同向判出，加上上班的宽度实测与本班的臂格·形参复量＝四枚独立证据。

### 四、本席自纠三枚（旧案不涂，另起留卷）

0. **CAS 口径自犯一枚（在册陷阱复现，本席又踩）**：首遍把 `expected_base_sha256` 传成 **截 16 位** 的显示用哈希 ⇒ `StaleWriteRefused: base-hash 与磁盘不符` 误报"磁盘被他人推进"。真源口径钉死在 `file_utils.py:content_sha256` 的 docstring（红蓝 2026-10-16 (a)）＝`sha256(path.read_text().encode()).hexdigest()` **全长**，且入参必须是 read_text 归一文本而非 `read_bytes()`（本岗两册现测均纯 LF：ledger 794 行 169,698B／checkpoint 114 行 32,251B，`git ls-files --eol` 两面 `i/lf w/lf attr/text eol=lf`⇒归一无风险）。改正＝另加 `full()` 走全长哈希；**该次拒写是零副作用的**（拒写发生在任何写之前，两册 sha16 复量未变）。此坑与本席 1016-02 班在册"CAS 拒写非事故勿进堵点"同条，本班如实入卷。

1. **v1 假扩（把两形态混算）**：首版 `.runtime/tmp/st-qoder-p08-1017-01/census_judge_face.py` 把 64 张越表卡全记为"真柱全被吞"，漏了 `_judge_comparison` 是累积记败不是早退 ⇒ 29 张双臂路卡被错误升格为"结构性不可评"。改正＝另起 v2 分 `SWallow`/`ADDfail` 两态；v1 与其产物留卷不删。数字面：v1 报"64 全吞"，v2 报"38 吞／26 累积"——总数同、语义反，v1 若入册会让 ⑥ 误以为补词表能救双臂卡。
2. **J5 判废（本班自造的第三闸被负对照打死）**：本班一度把"卡面 `data_binding.implementation_gap` / `blocked_*` 自陈＝不可考"当拦卡闸（本族命中 **23 张**、全库 prereg 命中 **32 张**）。负对照当场证伪：**已 examined 的 87 张里 32 张同样带该键**（例 `TDM-E-L1-S2/calibration/17..20`）⇒ 该谓词与"能不能考"无因果，属假扩，本班已把它降级为参考面、不作拦卡依据；§三 拦 `X-S1-01/comparison/02` 用的是 `simulate()` 形参实测＋`grep confirm=0` 两枚代码级证据，不是这条键。
3. **落袋器首遍崩在本席自己的 difflib 变量名**（`counts()` 解包用 `_j1` 却写 `add += j2 - j1`⇒NameError），崩在断言之前的纯计算段、**零写入**（两件文本 sha 未变，`git status --porcelain` 对本目录读空）；改正后同尺读数见 §八。入册给下班一条＝尺面/落袋类自造件里的 `_`前缀解包位不可再引用，落袋器崩时先核"是否已发生写"（本件顺序＝counts 断言在 `safe_write_text` 之前，故零写是可证的、不是假设）。

### 五、对照面（尺承重自证，禁裸用尺）

- **正对照 1（族间量级差）**：同尺扫全库 prereg 162 张＝`entry_flow` 91 张里越表仅 **11** 张（12%），而本族 71 张里 **64** 张（90%）⇒ 词表错配集中在本席三族（exit 25 里 22／portfolio_flow 21 里 21／position_flow 25 里 21），不是全线问题；尺在两族上差一个量级＝有判别力。
- **正对照 2（与"真出过分"对拍）**：同尺扫 examined 87 张＝越表仅 **1** 张、零越表 86 张；route 分布 series 61／event 23／dual_arm 3 ⇒ "词表全过"与"确实出过分"强相关，本班尺不是随机数。
- **负对照（桶型尺非恒真）**：`_BUCKET_TYPE_N` 在册 8 词＋`quantile_\d` 面在本族命中 **3 张**（71−68），非零命中。

### 六、转单段（工序 5：不开考件按 owner 分派，本席零自裁、零改判据）

- 转 **⑥（词表立法，本席无判据改动权）**：本族 distinct 越表柱键 **106 个**，分面＝series 路 **59** 个／双臂路 **47** 个；按"补一键救几卡"的边际收益，前 4 键（`maxdd_delta_max`／`sharpe_vs_baseline_min`／`turnover_cost_gate`／`tracking_diff_max`）覆盖 **50 卡次**。续上班 ㉑：`turnover_cost_gate`(11) 与 `turnover_or_cost_gate`(10) 词面分裂仍未并名。
- 转 **⑤**：(a) `_series_metrics:242` ic_ir 恒 None、`_panel_metrics:270` mono 恒 None（本族 2＋12 张卡在冻这些柱，`unjudged` 面已如实披露＝非隐身，但要出全分须接线）；(b) `_n_buckets_from_card:140-151` 桶型词表只认 8 词 ⇒ 本族 24/25 张 series 卡的冻结桶名被静默换成 10 分位桶——本班建议**不改默认桶数**、改为"卡面桶名不在册即 `_ToolError` 拒考"（与 `_forward_face:193-199` 的"半申报即拒"同族形态），本席不自改；(c) 续上班＝panel 多日 `target_forward_face` 消费腿（`_panel_metrics:252` 现值仍硬编码 `shift(-1)`）；(d) 新增＝`X-S1-01/comparison/02` 所需按桶分流确认层形参（`simulate():183-193` 现值三形参、`grep confirm` 全件 0 命中）。
- 转 **⑨/⑩**：`_judge_comparison:598-600` 把 `misfire_reduction_min` 写成无条件 fail＝"预判决"冒充"考试成绩"；建议该柱走 `unjudged`/blocked 形态，覆盖尺口径由 ⑨ 判（本席零翻态）。
- 转 **⑩**：本岗天花板已由三把互相独立的尺（数据构造面／判官可评面／卡池-册落地面）同向判 **0**，上班 [BLOCKER] 高的"改判普查＋转单岗"呈批**续期**；本班补一条排班事实＝本岗开班时刻×CH 窗 01:00–04:00 使实跑窗只剩 30 分钟，与"重拉五列≈5 分＋同帧双对照"的工序成本不匹配⇒**请 ⑩ 判 ⑧B 班次是否改派 04:00 后或 20:00–23:00 窗**。
- 转 **⑫/⑩**：续上班＝三席共用宽面板缓存白名单（`shift06_*.parquet`／`*_wide.parquet`）与"谁有权删"；本班现测 `.runtime/tmp/p07/` 33 项内 `shift06_*.parquet` 仍 0 枚（仅两枚 `*_load.json` 在位，1017-01 00:33 复量）＝案未动。

### 七、本班 [BLOCKER] 行（六条，逐条事中当场追加，非班尾攒写）

[BLOCKER] 2026-10-17|⑧B/p08-1017-01|判据缺失|本族 71 张 preregistered 经**第二把独立尺**（判官可评面 ↔ 卡面冻结柱对拍）复证真可考面＝0：越表 64 张（series 路 38 张真柱被 `judge()` 早退吞、双臂路 26 张仅累积记败）、distinct 越表键 106 个、零越表仅 7 张且逐张另有第三把闸的独立证据（3 张零臂格＋4 张 top20 撞 30 列地板，后者为上班实测非本班现测）|.runtime/tmp/st-qoder-p08-1017-01/judge_face_v2_own.json＋joint_candidates.json；docs/04_research_records/mining/ledgers/mineloop_campaign/02_binding_book.yaml 现测 entries=18/approved=17 而本族格仅 07/07b；scripts/backtest/fexam/calibration_exam.py:741-747・:841-843・:594-597|⑩ 汇总呈 Owner：上班"改判本岗为普查＋转单岗"呈批续期；或由 ⑥ 按 §六 分母（前 4 键覆盖 50 卡次）立法＋⑤ 接 §六(a)(b)(c) 三腿，并给"补键后重扫"约定时点；本席不自裁|高
[BLOCKER] 2026-10-17|⑧B/p08-1017-01|工具缺陷|`_judge_comparison` 对 `misfire_reduction_min` 无条件追加记败（与读数无关）＝把"本面无从评估"写成 verdict=fail，下游覆盖尺会读成"考过且判不行"；本族冻此柱 1 张＝`TDM-X-S1-01/comparison/02`|scripts/backtest/fexam/calibration_exam.py:598-600；尺面 joint_candidates.json 的 misfire 清单（本族命中 1）|⑤ 判是否改走 `unjudged`/blocked 形态（同 :355-361 已有形态，零新阈值）；⑨ 判覆盖尺口径；本席零翻态零改判据|中
[BLOCKER] 2026-10-17|⑧B/p08-1017-01|工具缺陷|分桶桶型词表只认 8 个分位词＋`quantile_N`，卡面自造桶名一律静默落缺省 10 桶：本族 kind=series 的 25 张里 **24 张** 中招（21 种自造名），`_bucket_response:161` 的值域救援只在信号唯一值 ≤ 桶数时成立（序数档可自愈、连续/面板信号不可）；分数行带 `n_buckets_used`＝事后披露面存在，非无痕|scripts/backtest/fexam/calibration_exam.py:140-151・:161；尺面 judge_face_v2_own.json 的 BKT/btype/n_used 三列|⑤ 建议改"卡面桶名不在册即 `_ToolError` 拒考"（与 `_forward_face:193-199` 半申报即拒同族），**不改默认桶数**（改默认＝动判据，本席无权）；⑥ 若要放行这些桶名须逐名给机读档数|中
[BLOCKER] 2026-10-17|⑧B/p08-1017-01|流程问题|词表错配族间量级差＝出题面与本席三族卡未对表：同一把尺下 entry_flow 越表 11/91（12%）而本席三族 64/71（90%），且 `turnover_cost_gate`(11) 与 `turnover_or_cost_gate`(10) 同义两名仍未并名（上班 ㉑ 续存）|尺面 judge_face_v2_all.json（全库 162 张逐目录读数）＋本台账 §二 TOP 键表与 §五 正对照|⑥ 按族分面立法（series 路 59 键／双臂路 47 键）并先做同义并名；⑩ 判是否把"卡面柱键必须出自 route 词表"立成出题闸（属判据面，须 chief）|中
[BLOCKER] 2026-10-17|⑧B/p08-1017-01|流程问题|本岗开班时刻×CH 窗 01:00–04:00＝实跑窗仅 30 分钟，而单张真分出册成本＝重拉五列≈5 分（上班实测 56.3 秒/列）＋同帧双对照＋CAS 入册；本班 00:46:30 `date` 现测判定该腿不可能在窗前走完，据此改走零 CH 的本地尺面并如实报 0 出分（未硬跑、未造二次试次、未造假红）|开班 `date` 00:30:12 现测×指令卡工序 5；水位现测 commit_pct=88.76/ram_used_pct=88.9/cpu_pct=87.8（reaper --status 00:31:13）；`.runtime/tmp/p07/` 33 项内 shift06_*.parquet 现 0 枚（00:33 复量）|⑩ 判 ⑧B 排班窗（改派 04:00 后或 20:00–23:00）；⑫ 续上班＝共享只读缓存白名单＋删权归属|低
[BLOCKER] 2026-10-17|⑧B/p08-1017-01|工具缺陷|本席自犯三枚入册：(a) 首版尺把双臂判官的"累积记败"与单信号判官的"早退吞柱"混算成 64 张全吞＝假扩（v1 若入册会误导 ⑥ 以为补词表能救双臂卡）；(b) 本班自造第三闸"卡面 implementation_gap 自陈＝不可考"被负对照当场打死（examined 87 张里 32 张同样带该键）；(c) 落袋器 `counts()` 解包名写错抛 NameError，崩在断言前的纯计算段＝零写可证（两件文本 sha 未变＋本目录 `git status --porcelain` 读空）|v1 件与产物留卷：.runtime/tmp/st-qoder-p08-1017-01/census_judge_face{.py,.json}；v2 改正件同目录；(b) 对照读数＝exam_cards 全库 status×has_gap_key 计数（prereg 带键 32／examined 带键 32）；(c) traceback 止于 land_docs.py:39|本席当班改正（已落 §四 三节，v1 不删）；无需他席动作；给下班一条尺面纪律＝**拦卡只认代码级实测（形参/词表/计数器命中），不认卡面散文自陈**；新闸上线前先把同一把尺架在已出分卡面上量一遍|低

### 八、本班收班读数（八件逐项，现测非终值）

- ①**claim**：本班只 claim 自家两件（`p08_examiner_b/ledger.md`＋`checkpoint.md`），收班前 `lock_files.py list` 现读两把锁持有者＝st-qoder-p08-1017-01、剩余 29.8m；收班序列见本袋落地后 `git_commit.py --release-only` 回执。**卡锁零把**——本班无开考故无占卡三步（未 acquire 任何卡面）。
- ②**心跳**：daemon pid=**56760**（开班回读在册）；收班按 PID 精确终止＋60 秒后进程表与 `heartbeat_st-qoder-p08-1017-01.pid` 双读复证（承在册"禁按镜像名全杀"律）。
- ③**实耗**：开班 00:30:12 `date` 现测，收班戳见游标 last_run 现测差；本班不写自估终值。
- ④**[BLOCKER]**：6 条（高 1／中 3／低 2），§七，逐条事中当场追加（首件尺面完成即写，未攒班尾）。
- ⑤**自清**：`.runtime/tmp/st-qoder-p08-1017-01/` 本班件＝`open_session.py`／`census_judge_face{.py,.json}`（v1 留卷）／`census_judge_face_v2.py`＋两 json／`joint_candidates.py`＋json／`census_fine_ref.json`（上班尺产物的只读副本，未改他席原件）／落袋脚本。尺面按上班 ㊱ 与在册"尺面留给下一班复用"案**保留**，非临时废料；本班零业务面临时件外散、项目根零临时件。共写面（to_*/dispatch/pulse）零字节。
- ⑥**GPU 还牌**：本班未 acquire 看门人（零 ic 实跑）⇒免执行；本班零分数行，无"回退报成 GPU 读数"风险。
- ⑦**后台子任务**：零 spawn 子代理⇒零孤儿。
- ⑧**零 worktree**：本班未调用任何工棚/工作树启动入口；`git worktree list` 收班现测＝**80** 行，对 `st-qoder-p08-1017-01` 命中 **0**（`grep -c` 回 0 且 rc=1＝计数为零的正常形态，非命令坏；在册 P01-1016-03 同坑复述）。历史遗留 `st-qoder-p08-1016-02`／`/03` 两枚＋`.aidrafts` 整面属他席或工具自建，按 TRAE-079 与在册 auto-spawned 案呈 ⑩、本席不自删。
- 并发避让：本班零写分数册——收班现测 `docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`＝**145,458B／sha16 a9532fceb0899c94／rows 110**，与上班 §㊾ 基线逐字节同值⇒"零字节"成立（00:46:01 `date` 同帧）；旧址 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml` 盘仍在位（退役案仍未签，交 ⑩）；零写 `known_data_gaps.yaml`；卡面零翻（无开考）；判据/门柱/阈值/词表零改动；无 requeue、无代投他席件、无裸 git commit、无 `git stash`。HEAD 本班现读 `61f25b6a71`（开班 00:30 时主区为 `5024742841`，其间他席有落地，本班未触）。


## 10-17 00:5x · 班次 01 追加节（同班·收班实测补记）：claim 在入队后归零的两机制未分面＋活性锚真盾复命＋在册可考面 0 的第四枚独立复证归位

### 九、收班实测补记（§八 写于入袋前，本节写于入袋后；旧句不涂）

- **claim 现测归零，两机制本席无法区分（如实呈 ⑩，不代签）**：本班 00:44 acquire 两把锁（`lock_files.py list` 现读持有者＝st-qoder-p08-1017-01、剩余 29.8m），00:52:59 入袋后同一尺对 `p08_examiner_b` 命中 **0**（`grep` rc=1＝零命中的正常返回形态，非命令坏；`.runtime/locks/` 目录内 p08 只剩 `heartbeat_st-qoder-p08-1017-01.pid` 一枚）。两个候选机制＝(a) 网关入队链路自释（回执面同批出现 `ENQUEUE-RENEW: claim 续租 0/2 件（ttl=7200s）`），或 (b) 外来 `cleanup` 按 `pid=0`＋`logical=False` 回收（在册 pid0 回收族：会话注册用 pid=0，回收侧把"PID 亡"当必要非充分但本席 entry 恰又 `logical=False`）。**本班采 (a)(b) 并列陈述、不择一_reporting**；对下班一条实用结论＝**入队后即 `list` 复量自家 claim，勿默认锁还在**，需续跑同类件要重新 acquire。
- **活性锚真盾复命（承在册 seat-claim-keeper-duality 的正解，本班首执行）**：本班 entry 曾处 `logical=False`（运行面自报 `re-register downgraded by rate guard window=1860s elapsed=716.4s`＝重复注册被频控拒，state 重建但活性锚冻结）。改走 `mark_logical(sid, logical=True)`＋`heartbeat(sid)` ⇒ 现读 `logical=True`、`pid=0`、`held_files=[]`、入 `list_active_readonly()` 面。在册处方逐字复证＝**真盾是 mark_logical，不是重复 register、也不是 acquire**（频控窗 1860s 内重注册必被降）。
- **尾袋等待期活性锚工**＝`.runtime/tmp/st-qoder-p08-1017-01/keeper.py`（每 20s `heartbeat()`＋查四态，终态或 16 分上限即退，**不改写工作树**）＝在册 `closeout-order-land-bags-before-unregister` §4 处方的本席首执行；本班袋 `q-20261017-st-qoder-p08-1017-01-0001`（files=2、base_head=`5d2310760cbd`）等待时队列面现测 pending 19／processing 19（头袋属 ①席 1017-01-0005，非本席）。
- **本班尺在家族谱归位（禁当新案卖）**：在册早于本班就有同向结论，本班首版正文曾把两处依据写成查无路径，落笔前已用 `ls`/`git ls-files` 与 `grep` 改正为真源＝①`docs/_working/examrun_campaign/00_ledger.md`（10-12 班「现器可考＝0，三证独立同向」，其一条即"词表外键"面；04 镜像件同内容=`docs/04_research_records/backtest/campaigns/examrun_campaign/00_ledger.md`）；②`docs/_working/automation_campaign/p06_prereg/ledger.md:1065-1067`＝⑥席已记「`_CALIBRATION_JUDGED_KEYS ∪ _UNION_PILLAR_KEYS ∪ _EVENT_KNOWN_KEYS` 对两枚词面命中 0 ⇒ 两枚都是越表柱，judge() 对越表键 fail-closed 返"未支持判据键（机判面待扩）"」并转引本席自家口径「词表须按路由取（series/dual_arm 两值）」；③本班尺按其实现值三分＝`pillars_route():667-693` 返 series/event/dual_arm 三值（本族 prereg 实测零 event 路）。⇒ **本台账 §二/§三 的"本班新发现"只限两枚**＝早退吞柱与累积记败**两形态必须分账**（§四(1)）＋`misfire_reduction_min` **无条件记败**（§二末段）；"越表柱普遍存在"与"可考面收敛为 0"都不是本班首案，是第 N 枚独立复证。
- **未遂入卷（本席自犯第 4 枚，改正于落笔前＝盘上零污染）**：本节上一稿把两条依据写成 `docs/_working/examrun_campaign_20261012/00_ledger.md` 与"10-15 班在册纠偏"——前者 `ls` 实测 **No such file or directory** 且 `git ls-files docs/_working/ | grep -c examrun_campaign_20261012`＝**0**；后者在本席长期记忆里有，而在仓库台账里 `grep -rl "按路由取" docs/` 命中的是 **⑥席件**（`p06_prereg/ledger.md:1067`）而非 10-15 班。⇒ 若未复核就入册＝在册面上留下一条不可反查的引用（本岗历史同型，长期记忆 citation-must-be-greppable-before-writing）。处方复述＝**正文里任何路径／席位／班号引用，落笔前必须同帧 `ls` 或 `grep` 拿到命中数**；本席长期记忆**不是**仓库在册面，不得作为"⑩/⑥ 可反查"的证据源。
- 本班全程 CH 零调用（尺面纯本地），GPU 零 acquire，卡面零翻，分数册零字节，共写面零字节，[BLOCKER] 六条已在 §七 当场入册；本节属"更正与归位优先于工序闭合"，若本袋死于基底死（在册 双侧皆改 族），盘上字节即权威超集面，下班直接重投勿重跑尺面。


## 10-17 01:30 开班 · 班次 02（st-qoder-p08-1017-02）本班出分 0 张＝CH 窗 01:00–04:00 整窗覆盖本班 60 分班窗（开班 `date` 01:30:13 现测）⇒ 零开考、零卡锁、零 GPU、零分数行；主产出＝**第三把尺＝直调工具自家函数**（`pillars_route`/`judge`/`judge_event`/`_route_vocab`，非正则面）的判官路径分账：本族 71 张 prereg＝假红路 **38**／停驱动分诊路 **29**／真判可达路 **4**，并据此**改判上班 §㉖/51 与游标 cursor 行的"双臂路 26 张累积记败"＝在驱动层不可达**；另落一枚可复现判据＝**反事实双卡对照**（同一份"全部在表柱都过"的合成读数，加一根越表柱前后 verdict 由 pass 翻 fail 且 fails 只含词表理由）

### 〇、本班时序与环境（全部现测，非引用）

- 开班 `date`＝**01:30:13**；冷启动三件齐＝①`python --version` 3.12.8；②`lock_files.py cleanup`＝`CLEAN — 无死锁需要清理` ＋ `SALVAGED — 死会话 st-qoder-p07-1016-03 遗物已回收`（非本席会话，本席不自处置）；③`python -m zephyr.trading.process_reaper --status`＝`source=file`（现算失败回退状态文件，`MemoryError()`＝在册续期形态）／last_run=2026-10-17 00:57:35／scanned=32 whitelist_hits=27 killed=0 reported=26／drift(stash=27, worktree_changes=1456)／水位 `commit_pct=80.36`、`ram_used_pct=75.3`、`cpu_pct=62.8`、degraded=False、breaches=1、hygiene_errors=1；同一回执内 `safety_wires.dead_archive ok=True rc=0` 与 `auto_wires dead_archive=error archived=0` **两字段自相矛盾**（本席只记读数不判，转 ⑩/⑫）。
- 防重入三尺并读＝①游标末态＝`10-17 班次 01 已交账`；②`lock_files.py list` 全表 **1** 行、对 `p08` 命中 **0**；③取号前扫 `.runtime/tmp/st-qoder-p08-*`＝最大号止于 `1017-01`、`1017-02` 零目录（01:31 现测 `No such file`）⇒ 本班取 **st-qoder-p08-1017-02**，无撞名、无孤儿半班混入（承在册 ㊱）。
- 会话注册＝`open_session(sid, [], [])`＋`_spawn_heartbeat_daemon` → daemon pid=**38900**，`heartbeat_st-qoder-p08-1017-02.pid` 回读=38900；运行面自报 `logical=True downgraded (chief-form verification failed)` → 按在册真盾 `mark_logical(sid, logical=True)`＋`heartbeat(sid)` 复命，现读 `logical=True` 且 `in_active_readonly=True`（01:34 同帧）。
- 本班写域＝两件（本台账＋游标）。**卡锁零把**（无开考故无占卡三步）；**GPU 零 acquire**（无看门人占用，收班⑥据此为"不适用"）；分数册字节未触。

### 一、下班首查四件逐件复量（承游标 §55；逐件现测并给可复跑谓词，禁引本行当事实）

| 件 | 现测 | 判 |
|----|------|----|
| ① ⑥ 双臂册格＋`level_to_cap_map` | `02_binding_book.yaml` 双文档（`safe_load_all`，含 `entries` 的 doc）entries=**18**／approved=**17**；本族格仅 `TDM-X-R1-01/comparison/07_…五态仓位锚定版`、`07b_…复位阶梯锚定版` 两枚且两卡磁盘 status 均 `examined`；`level_to_cap_map` 对本族文件名含 `__(comparison\|ablation\|shadow)__` 的 **58 张 prereg 全部 0 命中**；尺正对照＝按「card_id 前三段（id/route/seq）全等」谓词架在全库 599 个卡 seg3 上，18 格 **18/18 全解析** | **未动**（零命中是真零，非坏尺） |
| ② ⑤ 三腿 | `calibration_exam.py:251-252` 现读 panel 面仍 `ret = target.shift(-1)` 硬编码；`_forward_face` 消费行现测 **175/182/189/195/212**（无 :251 面）；`_BUCKET_TYPE_N`（**:128**，v1 正则因带 `dict[str, int]` 注解未命中）现值 **8 词**＝quantile_decile/quintile/tercile/quartile＋tercile/quartile/decile/quintile，另 `re.fullmatch(r"quantile_(\d{1,2})")`，否则 **return 10**；`judge():741-747` 越表即 `return "fail", [未支持判据键…]` 早退原样、`judge_event():841-843` 同款、`_judge_comparison:594-600` 累积记败＋`misfire_reduction_min` 无条件追记原样 | **未动**（三腿零进） |
| ③ 旧址册退役＋断链册入库 | 旧址 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml` 盘 103,529B／73 行，`git cat-file -e HEAD:` rc=**0** 且 `head_equals_disk=True`；`git ls-files docs/04_research_records/governance/working_ref_sweep_20261015/`＝**0**，而同目录 `broken_records.yaml` 盘面 **786,491B 在位**（=指令卡 1b 的断链警戒册本体未入库） | **均未动**（连上班现值同读数） |
| ④ 排班窗 | 本班 01:30:13 开班仍在 CH 窗内，60 分班窗被整窗覆盖（04:00 窗收＝本班班尾 02:30 仍在窗内） | **未动**，本班据此零开考（见 §七 中 1 条） |

队列四态收班现测（`iterdir()+is_file()` 谓词，非目录计数）＝pending **19**／processing **20**／done **930**／dead **488**；本班袋入队时面为在途积压面（与上班 §㉛ 17:51 读数 pending 1／processing 1 相比夜间涨一个量级，非本席事）。

### 二、本班主项 A＝反事实探针：把「词表缺口」与「信号质量」两因分离（零业务数据、零写）

工具口径词表大小现测＝calibration **5** 键／event **7** 键／union **14** 键（`_CALIBRATION_JUDGED_KEYS:335`、`_EVENT_KNOWN_KEYS:654`、`_UNION_PILLAR_KEYS:648`）。

尺面＝`.runtime/tmp/st-qoder-p08-1017-02/false_red_probe.py`（直调 `judge()`/`judge_event()`，合成卡＋合成读数 `M_PASS`={ic_mean .05, ic_ir .5, mono .9, regime_ic{bull,bear}=.05, oos_ic .04}）：

1. 卡A `pillars_numeric`={ic_mean_min .02, ic_ir_min .3, mono_spearman_min .5, regime_same_sign, oos_same_sign} → `judge()`＝**("pass", [])**
2. 卡B＝卡A ∪ `maxdd_delta_max: 5.0`（**同一份全过读数**）→ `judge()`＝**("fail", ["未支持判据键（机判面待扩，fail-closed）: ['maxdd_delta_max']"])**
3. 断言＝`maxdd_delta_max ∈ calibration 词表`=**False**、`∈ union 词表`=**False**（＝不是"换了词表就能评"，两根词表都不覆盖）
4. 事件面同款对照＝in-vocab 卡（event_days_min＋event_oos_gap_same_sign）给空事件读数 → fails 是**两条真实样本闸**（"事件日样本 0 < 门槛 200"、"oos 窗事件日 0 < 门槛 200"）；同卡加一根越表柱 → fails 只剩**一条词表理由**、真柱一条不评 ⇒ 早退在两判官同形。

⇒ **可复现判据（代码级＋执行级双证）**：卡面只要带 ≥1 根越表柱，则"全部在表柱都过"的读数也只能写成 `verdict=fail`，且 `fails` 面不含任何信号质量理由。上班 ㉟ 的"按 fails 归因越表卡＝错结论"由本班的对照升级为**任何人可重跑的两行命令**。

### 三、本班主项 B＝本族 71 张 prereg 按工具自家路由的路径分账（第三把尺）

路由真源＝`pillars_route()`（`calibration_exam.py:667`，**只看 `pillars_numeric` 键集、不看 family 与文件名**）；词表按 route 取＝`_vocab_of()`（`comparison_exam.py:90-91`）。

| 路径 | 张数 | 代码锚与该路径的真实后果 |
|------|------|------------------------|
| `false_red_series` | **38** | route=series 且 `pillars_numeric − _CALIBRATION_JUDGED_KEYS` 非空 → `judge():741-747` 立即 return fail＝**假红暴露面**（真柱一条不评，见 §二） |
| `blocked_route_driver` | **29** | `pillars_route()`=dual_arm（键集⊄校准表且命中 `_NAV_ONLY_PILLAR_KEYS`）→ 驱动 `comparison_exam.py:255-266` 在缺 `--binding-book`／缺册格时返回 `_blocked_row`；`_blocked_row:129-135` 明写**不翻卡、不记试次**（零数据消费=零试验，DSR 分母不虚增），行自带 route/binding_class/拒因 |
| `real_judge_reachable` | **4** | route=series 且冻结柱全在 5 键表内＝真判面覆盖全部柱（数据形状另算，见 §五） |

- route 分布现测＝dual_arm **29**／series **42**／event **0**（加总 71）。
- 38 张内 distinct 越表键＝**59**；频次 TOP＝`maxdd_delta_max` 15／`sharpe_vs_baseline_min` 14／`turnover_cost_gate` 11／`tracking_diff_max` 10。
- **只差一根越表柱的卡＝5 张**，逐张键名＝`TDM-X-S1-04/calibration/03`→`gap_bucket3_vs_0_20d_max`、`TDM-P-P1-03/calibration/02`→`band_separation_min_pp`、`TDM-P-P1-04/calibration/05`→`threshold_gap_min_pp`、`TDM-P-P3-02/calibration/03`→`curvature_direction`、`TDM-P-P3-04/calibration/02`→`probability_top_bucket_min`（全集在 `false_red_probe.json` 的 `detail.own_false_red_cards`）。
- 桶型面（收上班 ㉑ 口径）：本族 71 张 `buckets.type` 落在在册 8 词内的仅 **3 张**（均 `quantile_decile`），其余为自造名（arm_matrix 12／ablation_set 5／allocator_scheme 2／event_sample 2／…共 26 种）；但精算面须收窄＝`_n_buckets_from_card` 消费点**唯一**在 `_series_metrics:218`，panel 面（`_panel_metrics:251`）不经此闸 ⇒ 上班"kind=series 的 24/25 张中招"是按 `signal_kind` 划的**上界**，非按"实际走 1-D 面"的张数（本席不重烧该数）。

**本班改判上班一条（留旧案不涂，另起本节）**：游标 cursor 行与 §㉖/51 写「双臂路 **26 张**仅 `_judge_comparison:594-597` 累积记败（其余柱照评）」——那是**判官层**静态读数；**驱动层**实测＝本族 29 张 dual_arm 零册格（§一① 现测＋正对照 18/18），在 `comparison_exam.py:255-266` 即返回 `_blocked_row`，**走不到 `_judge_comparison`**。后果两条＝(a) 上班为该形态立的中档 [BLOCKER]（`misfire_reduction_min` 无条件记败）对本族当前面**不可达**，⑤ 修 `:598-600` 的性价比须重排；(b) 词表立法真正救的是 **38 张 series 假红路**，与⑥ 补双臂格是**两条独立腿**，⑥/⑤ 排工勿合并成一件事。

### 四、尺承重（三把正对照＋一把负对照，下班复用本尺前先跑这四条）

1. **全库 examined 同尺**（真出过分的卡）＝真判可达 **83**／假红路 **1**／停分诊 **3**；route 分布 series 61／event 23／dual_arm 3；越表柱总数 **1** ⇒ "确实出过分的卡几乎全在可评面"，尺有判别力。
2. **entry_flow prereg 91 张同尺**＝可达 73／假红 **11**／停分诊 7 ⇒ 假红暴露 11/91=**12%** vs 本族 38/71=**54%**（同向于上班 §53 的"越表 12% vs 90%"，量级差因本班按**路径**而非按**柱数**定级）。
3. **集合级对账**（`.runtime/tmp/st-qoder-p08-1017-02/crosscheck_two_rulers.py`）＝上班"零越表 7 张" ⊖ 本班"真判可达 4 张"＝**恰 3 张且全是 dual_arm**（`TDM-X-R1-01/comparison/02`、`TDM-X-S1-01/comparison/02`、`TDM-X-S1-03/comparison/02_dualwindow`），反向差集＝**空** ⇒ 两把独立实现互证；且本班尺把这 7 张拆成**两种不同缺件**（4 张撞数据形状／3 张撞册格），⑥ 只补册格只能动 3 张。
4. **负对照＝本班自犯三枚坏尺当场打死**（旧读数不涂，v1 件与产物留卷 `preflight_v1_badpredicate.json`）＝(a) 册行数谓词写成 `^  - card_id:`（两空格缩进）而册行首是顶格 `- card_id:` ⇒ 两址册全报 rows=**0**（假无源；改正谓词 `^ *- card_id:` 后新址 110／旧址 73）；(b) `git cat-file -e HEAD:` 传的是 `Path(...).as_posix()` 绝对路径（含盘符）⇒ 两址册全报 rc=**128**，若入册即成"分数册掉出 HEAD"假事故；(c) 册格匹配用子串 `"02" in card_id` ⇒ **58/58 恒真**假扩（改正为前三段全等，改正后真值 0）。三条同族教训＝**尺的失败形态与"查无"同形，0 命中与满命中都要先架在已知正解上量一遍**。

### 五、分数册与卡池收班现测（禁当终值引用）

- 新址 `docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`＝**145,458B／sha16 a9532fceb0899c94／rows 110**，`git cat-file -e HEAD:` rc=**0**、`head_bytes=disk_bytes`、`head_equals_disk=True` ⇒ 与上班 §㊾ 逐字节同值＝**本班零写册零出分**（无二次试次风险）。verdict 分布 fail **106**／pass **2**／blocked **2**；本席在册行 **3** 枚（run_id 含 `p08b`：`p08b-1015-04-card06`、`-card07`、`p08b-1016-02-x-s1-04-02`）。
- 旧址 103,529B／73 行，盘与 HEAD 同值 ⇒ 旧址退役判据仍齐、仍无人签（交 ⑩，本席不自删）。
- 本族卡池磁盘面（逐张 `yaml.safe_load` 取 `status`，非正则面）＝exit_flow{empty 19, prereg 25, examined 4, blocked_on_impl 3}／portfolio_flow{empty 16, prereg 21}／position_flow{blocked_on_impl 16, empty 18, prereg 25, blocked_on_data 2, examined 2}；合计 **151**＝preregistered **71**／empty **53**／examined **6**／blocked_on_impl **19**／blocked_on_data **2**。**本族 empty=53 是首次按目录摊开**（上班只给全库 empty 208），属 ⑥ 出题面存量，本席不判。
- **本席亲笔一枚在假红路上**＝`TDM-X-S1-04/calibration/02`（rows[109]，越表键 `gap_k3_vs_k0_5d_max`）⇒ 上班 ㉟ 定性在本班尺下自动复现；本族 examined 6 张路径＝可达 2／假红 1／停分诊 3。**⑨ 读覆盖尺口径**＝该行的 verdict 来自词表缺口而非信号质量，禁按"考过且判不行"计入。
- 据此起见归位（不当新案卖）＝"本族真可考面 0"至此已是**第五枚独立复证**，且本班这把是**工具自家函数**那把：71 张中 4 张真判可达＝上班 §51 那四张 panel 冻结 top20 池卡（撞 `ic_exam.py:96 ic[valid<30]=np.nan` 三十列地板，该锚本班 §一② 复测仍在），另 3 张差册格。本班新增**不是**"0"这个数字，而是三条结构差＝①双臂的失败形态在**驱动 blocked 路**而非判官累积记败；②假红暴露面精算＝**38 张**（不是 64 张全吞）；③只差一根柱的卡＝**5 张**且键名唯一不重复（⑥ 最小立法集）。

### 六、转单段（零代签，逐条给席位）

- → **⑥**（词表立法）：`maxdd_delta_max`(15)／`sharpe_vs_baseline_min`(14)／`turnover_cost_gate`(11)／`tracking_diff_max`(10) 四键覆盖 38 张假红路最大频次；最小可解锁集＝§三 那 5 张各 1 键；同义未并名续存（`turnover_cost_gate` vs `turnover_or_cost_gate`，上班 ㉑ 案未动）。
- → **⑥**（册格）：3 张零越表双臂卡（`X-R1-01/comparison/02`、`X-S1-01/comparison/02`、`X-S1-03/comparison/02_dualwindow`）缺的是**绑定册 arms 格**，不是词表；补格后驱动才会走 `card_binding.run_one`。
- → **⑤**：排工重排两件＝(a) `:598-600` misfire 无条件记败对本族当前面不可达（§三改判）；(b) 真正暴露面是 `judge():741-747`／`judge_event():841-843` 早退形态（是改 fail-closed 早退还是改 `unjudged`+照评其余柱＝**判据面，本席不代裁**）；(c) panel 多日腿 `:252` 与桶名拒考闸仍未动。
- → **⑨**：覆盖尺须区分 verdict=fail 的两因（词表缺口 vs 读数破门柱）；本席 3 枚亲笔里 1 枚属前者。
- → **⑩**：旧址册退役案＋`working_ref_sweep_20261015` 断链册入库＝**连续两班现值未动**；reaper 同回执里 `dead_archive ok=True rc=0` 与 `auto_wires dead_archive=error` 自相矛盾（本席只记不判）；排班窗请判（§一④＋§七）。
- → **⑫**：三席共用宽面板缓存案未动（上班 §㊼/§七续期，本班未复量 `.runtime/tmp/p07/`，因本班零跑腿）。

### 七、问题登记（本班 5 条＝高 1／中 2／低 2）

[BLOCKER] 2026-10-17|⑧B/p08-1017-02|判据缺失|**假红暴露面＝38 张（本族 71 张的 54%）**：反事实双卡对照实测＝同一份"全部在表柱都过"的合成读数，卡A(柱全在表)`judge()`→pass，卡B(加一根 `maxdd_delta_max`)`judge()`→fail 且 fails 仅一条词表理由；`maxdd_delta_max` 同时 ∉ calibration(5 键) 与 ∉ union(14 键) 词表；本族 38 张 series 卡带越表柱 ⇒ 跑一张即在永久册写一条"因机判面不覆盖而判败"的 fail，本席亲笔 rows[109]（越表键 `gap_k3_vs_k0_5d_max`）已在册|尺面 `.runtime/tmp/st-qoder-p08-1017-02/false_red_probe.py`＋`false_red_probe.json`（detail.own_false_red_cards 38 张逐卡键名）；代码锚 scripts/backtest/fexam/calibration_exam.py:741-747・:841-843・:335・:648・:654；全库 examined 同尺正对照＝可达 83/假红 1/停分诊 3|⑤ 判早退形态是否改（动 fail-closed＝动判据，本席无权、不自改）；⑥ 按 §六 分母立法（前 4 键覆盖最大频次＋5 张最小集）；⑨ 永久册该行口径按"真柱未评"读；本席本班零开考零分数行未造任何假红|高
[BLOCKER] 2026-10-17|⑧B/p08-1017-02|流程问题|本岗开班时刻×CH 窗 01:00–04:00 **连续两班整窗被吃**（上班开班 00:30:12 仅余 30 分，本班 01:30:13 开班＝60 分班窗全在窗内）；单张真分出册成本≈五列重拉 56.3 秒/列＋同帧双对照＋CAS 入册，窗内不可能走完 ⇒ 本岗 ⑧B 在现排班时刻**结构性无法执行工序 3**（只能出尺面与转单）|开班 `date` 01:30:13 现测×指令卡工序 5；上班同坑＝本台账 1017-01 §五 [BLOCKER] 低已立案（本班＝第二枚）；本班水位现测 commit_pct=80.36/cpu 62.8（reaper --status 01:30:26）|⑩ 判 ⑧B 排班窗改派（04:00 后或 20:00–23:00），或按上班呈批把本岗正式改判为"普查＋转单岗"并同步 SOP §3⑧；本席不自改班次|中
[BLOCKER] 2026-10-17|⑧B/p08-1017-02|工具缺陷|上班游标 cursor 行与 §㉖/51 的"双臂路 26 张仅累积记败（其余柱照评）"＝**驱动层不可达**（本族 29 张 dual_arm 零册格，在 `comparison_exam.py:255-266` 即返回 `_blocked_row`，走不到 `_judge_comparison`）⇒ 该形态给 ⑤/⑥ 的排工信号（"补词表能救双臂卡"）方向错；正解面＝双臂缺**绑定册 arms 格**、series 缺**词表**，两条独立腿|`.runtime/tmp/st-qoder-p08-1017-02/preflight.json` 的 dual_route_prereg_faces（58 张文件名面 book_entry=False 且 level_to_cap_map 命中 0，正对照 18/18）＋false_red_probe.json 的 own_path_counts；代码锚 comparison_exam.py:129-135・:255-266・calibration_exam.py:667-693|⑩ 汇总时把上班该条 [BLOCKER]（中）改标"当前不可达·排工降级"；⑥ 补 3 张零越表双臂卡册格＝唯一解锁腿；本席不改判据不代签|中
[BLOCKER] 2026-10-17|⑧B/p08-1017-02|流程问题|治理面两件事**连续两班现值零动**＝①旧址分数册 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml`（103,529B／73 行，盘与 HEAD 同值，退役判据上班 §㉚ 已给齐）仍无人签；②指令卡 1b 点名的断链册 `docs/04_research_records/governance/working_ref_sweep_20261015/broken_records.yaml` 盘面 786,491B 在位而 `git ls-files` 该目录＝**0**（未入库＝任何席按 1b 断链警戒处置时读的是不可版本化面）|本班 01:36:33 `preflight_v2.json` 现测（reg_old.head_cat_file_rc=0／head_equals_disk=True；sweep_dir_ls_files.n=0／broken_records 786491B）；上班同读数＝游标 §㊽④/㊷|⑩ 签旧址退役（或派 ⑫）；断链册入库归属＝该目录原作者席或 ⑤，本席不自创路径不代落|低
[BLOCKER] 2026-10-17|⑧B/p08-1017-02|工具缺陷|本席自犯三枚坏尺当场改正（旧读数不涂）＝(a) 册行数谓词 `^  - card_id:` 与册实际顶格 `- card_id:` 不符⇒两址全报 rows=0（假无源）；(b) `git cat-file -e HEAD:` 传 `as_posix()` 绝对路径（含盘符）⇒两址全报 rc=128，若入册即"分数册掉出 HEAD"假事故；(c) 册格匹配用子串 `"02" in card_id`⇒58/58 恒真假扩。三条同族＝**尺坏与查无同形**，0 命中/满命中都必须先架已知正解上量|v1 产物留卷 `.runtime/tmp/st-qoder-p08-1017-02/preflight_v1_badpredicate.json`（含假 rows=0 与假 rc=128 读数）；改正件 preflight_v2.py＋crosscheck_two_rulers.py（新−旧差集为空＝尺自洽）；在册同族＝`endswith 过宽假扩`/`零命中须正对照`|本席当班改正（已落 §四4）；给全线一条＝Windows 侧 `git` 传路径必须 repo 相对 posix，禁把 `Path.as_posix()` 绝对值喂给 `git show/cat-file`|低

### 八、收班八件（本班逐项）

- ①**claim**：本班只 claim 自家两件（本台账＋游标）；投袋后按在册律**立即 `list` 复量自家 claim**（勿默认锁还在，承上班 §九(a)），复量读数记在本节末行（不为该读数另投一袋，承在册"网关每袋代起心跳⇒补记袋＝递归无出口"）。
- ②**心跳**：daemon pid=**38900**（开班回读在册）；收班终态判据＝末次网关动作（含 `--release-only`）之后按 PID 精确杀＋等 ≥70 秒＋宽谓词 `CommandLine like '*st-qoder-p08-1017-02*'` 零命中，且同尺数得全仓 `heartbeat_daemon` 枚数当正对照（禁按镜像名全杀，承在册律）。
- ③**实耗**：开班 `date` 01:30:13，收班 `date` 见本节末行实测戳；两戳差由 ⑩ 复核，本席不写自估终值。
- ④**[BLOCKER]**：本班追加 5 条（§七，高 1／中 2／低 2），行首形态与本台账既有约定一致且 `grep -n "\[BLOCKER\]"` 命中。
- ⑤**自清**：`.runtime/tmp/st-qoder-p08-1017-02/` 本班件＝`open_session.py`／`preflight.py`＋json（含 v1 坏尺件与 `preflight_v1_badpredicate.json` 留卷）／`preflight_v2.py`＋json／`false_red_probe.py`＋json／`crosscheck_two_rulers.py`＋json＝**尺面按在册"留给下一班复用"案保留**（本班产物即下一班对账锚，非临时废料，且 §三/§六 的分母全部写进正文谓词，不依赖 tmp 存活）；本班零业务面临时件外散、项目根零临时件；共写面（to_*/dispatch/pulse/分数册/卡面）零字节。
- ⑥**GPU 还牌**：本班零 acquire（无开考）⇒ 不适用，无占用需复核。
- ⑦**后台子任务**：本班未 spawn 任何子代理（Explore/general 均未用）⇒ 零孤儿。
- ⑧**零 worktree**：本班未调用任何工棚/工作树启动入口（TRAE-079 Phase 2）；收班现测 `git worktree list` 对本 sid 命中数与历史遗留面见本节末行；历史 `st-qoder-p08-*` 遗留壳不自清、报 ⑩。
- 本班四小步执行面（Owner 方案1／CHIEF-1016-2）＝每节落笔即追加（§一→§七逐件成文即写）、卡锁零把无需释放、游标本节成文后当场推进、tmp 件按⑤定性与下一班复用案保留；本班无 `[BLOCKER]` 攒到班尾的件（§七在提交前一次成文）。


## 10-17 01:4x · 班次 02 追加节（同班·第二袋）：发现工具内已有官方词表普查单口（本班尺与之逐卡对账 42/42 全等）＋CH 让路窗真源在代码里且**本班 §七 那条排班建议有一半落窗内＝当场更正**＋claim 入队后归零第五枚复证＋本席自犯一枚桶名"共 26 种"计数目测错改正（现算＝37 种/68 张）

### 九-1 官方单口发现（本班最重要一条，给 ⑥/⑩ 与全线三席）

等袋期读码发现：`scripts/backtest/fexam/card_binding.py:2083 build_vocab_census()` 与 CLI
`python scripts/backtest/fexam/card_binding.py --mode vocab-census --cards-dir <绝对路径> --out <件>`
**已经是**"判官路由＋越表柱键集"普查的机生底座，函数头自述用途＝「WO-V 词表立法的机生底座」，并自带
`discipline` 块（`threshold_values_written: 0 / cards_modified: 0 / ch_queries: 0 /
route_expression_copies: "1（pillars_route 单一真源，普查与判决同式）"`）。

本班实测（01:48 跑，秒级返回，只写本班 out 件）＝全库 `card_total=599`／
`cards_without_numeric_face=230`／`cards_with_keys_outside_route_vocab=125`／`unique_keys_outside_vocab=172`／
`tally_status{preregistered 162, empty 230, blocked_on_impl 48, blocked_on_data 71, examined 87, examining 1}`／
`tally_route{series 518, dual_arm 57, event 24}`；官方 `vocab_sources` 三侧词表现值＝series **5** 键／
dual_arm(union) **14** 键／event **7** 键，且注明"直读执行核常量，本件不复制定义"＝与本班 §二 读数同值。

**逐卡对账（`.runtime/tmp/st-qoder-p08-1017-02/compare_official_census.py`＋json，只读）＝
本班尺 42 张（38 假红路＋4 真判可达）与官方口 `rows` 按 card_id 前缀 TDM-X/F/P 过滤后
`per_card_agree_n=42 / per_card_disagree=[]`（越表键集逐卡全等）** ⇒ 本班 §三 的分母可信，且可整体换成官方口申报。

两条必须一起申报（否则官方口会被读错）：
1. **官方口不分路径**＝`official_distinguishes_paths=false`（其 `rows` 把 series 越表卡与 dual_arm 越表卡混列，
   本族前缀 81 行＝series 49＋dual_arm 32）。⇒ "越表柱卡数"≠"假红暴露卡数"；本班的
   **假红路 38／停驱动分诊路 29** 拆分是官方读数里**没有**的一层，⑥/⑨ 引用官方件时必须自带该层，
   否则会把 29 张"跑下去写 blocked（不翻卡不记试次）"的卡误当成"跑下去写 fail"。
2. 官方口按 `card_id` 前缀而非目录归属，且含非 prereg 态（本族前缀 81 行 vs 本班 prereg 面 42 行）。
   该差集 43 张＝examined/blocked 态带越表柱的卡（例 `TDM-P-P1-01/comparison/02`），属 ⑨ 读历史成绩面。
3. **附带一条＝本班差点误报工具缺陷，同帧双测证伪后归位**：官方 01:48 件 `card_total=599`，而本席 01:57 同尺盘面
   `is_file()` 数得 600→605，形似"官方口静默跳过 1–6 枚无 card_id 件"。逐枚验（严格 UTF-8 解码＋`card_id` 非空断言）
   ＝**undecodable=0／no_card_id=0／is_dir=0**，且 01:57 同帧复跑官方口＝`card_total=609` 与盘面 `is_file=609`
   **逐值相等**（件 `vocab_census_official_v2.yaml`，`generated_at 01:57`）⇒ 差异全因**卡面正被 ⑥ 实时新增**
   （599@01:48 → 609@01:57，10 枚/9 分），非工具漏扫。在册律 `measured-readings-must-share-claim-sentence-timepoint`
   第七枚复证＝**跨时点读数不得直接相减当缺陷**。同时一条真实增量给 ⑥/⑩：全库 empty 208(上班)→230(01:48)→240(01:57)
   而 prereg 恒 162＝出题面在铺空壳、未推 prereg。

**内收建议（宪法 §4.2 同域重复簇→收敛唯一／§9.5 静态清单必须生成器产出）**：本岗四班自造尺
（1015-04 `census.py`／1016-01 `census2.py`／1016-02 `block_census.py`／1016-03 `census_fine.py`／
1017-01 `census_judge_face_v2.py`／本班 `false_red_probe.py`）与官方 `--mode vocab-census` 属同一件事的多份实现；
下一班起**申报口径应换官方口**，本岗自留的只该是官方口没有的**路径拆分层**（§三 三行谓词）。
本席不自删他席尺面。

### 九-2 本班 §七 排班建议当场更正（留旧案不涂）

代码真源＝`card_binding.py:2075-2080 _in_ch_yield_window()`：
- `21:00-22:30`（W1 v2 提前窗让路，真源注=examcard_campaign/00_campaign_ledger.md 20:55 段）
- `01:00-04:00`（夜跑让路窗，矿考循环班令 §三 红线）

本班 §七 第 2 条（中）给 ⑩ 的建议原文是"改派 ⑧B 到 04:00 后**或 20:00–23:00**"——
**后一半落在让路窗内＝建议本身有缺陷**，当场更正：⑧B 真自由窗＝**04:00–21:00** 与 **22:30–24:00**。
另 `comparison_exam.py:311-314` 现读＝窗内若带 `--binding-book`（`ch_free=False`）且无
`--override-ch-window-with-reason` ⇒ 直接 `{"refused": win}` **return 3**；
而**注入通道（`--signal-csv/--target-csv`，`ch_free = not args.binding_book`）窗内不受该闸拦**。
⇒ 给下一班一条实用结论：窗内若非要跑一张，唯一合法通道是**自己把双腿注进 CLI/`run_card`**（零 CH），
但这属"越窗留痕"面且须 `--override-ch-window-with-reason`，本席本班未行使、不自签豁免。

### 九-3 收班实测三件（现测）

- **claim 入队后归零＝本席第五枚独立复证**：本班 01:40:30 acquire 两件成功（回执"持有者 st-qoder-p08-1017-02／TTL 30 分"），
  01:46:29 入袋 `q-20261017-st-qoder-p08-1017-02-0001`（files=2），01:47:03 `lock_files.py list` 对 `p08` 命中 **0**
  （grep rc=1＝零命中正常形态），同回执面出现 `ENQUEUE-RENEW: claim 续租 0/2 件（ttl=7200s）`
  ＝上班 §九(a) 两机制候选中的 **(a) 网关入队链路自释**这一支在本班复现（(b) 外来 cleanup 回收仍无法排除，本席不择一定论）。
- **零 worktree 复证**：`git worktree list` 现测 **82** 行，对本 sid 命中 **0**；`.runtime/aidrafts/` 本班号段 0 枚；
  历史遗留 `st-qoder-p08-1016-02`／`1016-03`／`1017-01` **三枚**整树壳仍在（较上班"两枚"＋1＝上一班网关自建），
  按 TRAE-079 与在册 auto-spawned 案本席不自删，报 ⑩/清理专班。
- **主项尺换口**：本班 §三 数字面（38/29/4）与官方件 `vocab_census_official.yaml` 逐卡全等＝尺自洽，
  下一班可直接 `--mode vocab-census` 复跑（命令原文见游标 60 行）。
- **零触面二帧复量（防"跨时点读数当终值"在册坑）**：分数册盘面 01:36:33 与 02:03:20 两帧均＝
  145,458B／sha16 a9532fceb0899c94／rows 110（同值＝本班与上班之间他席也未推进该册）；
  收班 `git status --porcelain` 对本册与本席三族两张卡（`X-S1-04/calibration/02`、`X-R1-01/comparison/07`）
  读到的 **`MM` 形态经 `git diff HEAD --stat` 复验＝空**＝在册"index 落后"形态而非内容漂移，
  **本席本班对该册与三族卡面零写字节**（本班全部取证走只读函数与 `--dry-run`/`--mode vocab-census` 只写自派 out 件）。
  另记一条主区面＝`git diff --cached --name-only` 对 `exam_scores_v1` 命中 7 行＝多会话混合池在册形态，非本席 staged。

### 九-4 两枚零写执行实验（把 §九-2 与 §三 的两处"读码"升级为"实测"）

**E1＝官方分诊口对三张零越表双臂卡逐张实跑**（`python scripts/backtest/fexam/comparison_exam.py --card <绝对路径> --dry-run`，01:53 现测，`dry` 分支先于状态闸且零写，见 :215-227）：

| 卡 | book_entry | route | binding_class | binding_reason |
|----|-----------|-------|---------------|----------------|
| `TDM-X-R1-01/comparison/02` | false | dual_arm | **C** | `target_face_not_index_next_day` |
| `TDM-X-S1-01/comparison/02` | false | dual_arm | **C** | `target_face_not_index_next_day` |
| `TDM-X-S1-03/comparison/02_dualwindow` | false | dual_arm | **U** | `no_data_binding_section` |

⇒ **上班与本班首稿的"三张只差一格（补册格即解锁）"过强，当场收窄**：三张各差不同件＝两张的 target 面被绑定层判为"非指数次日口径"（`classify_card:329-338` 现读，无申报前向面且 `target_source`/`target.primary` 均不匹 `_INDEX_TARGET_RE`），第三张**卡面根本没有 `data_binding` 段**（:309-310 ⇒ cls=U，属 ⑥ 出题面缺件而非 ⑤/⑥ 补格）。
同时按在册 ㉗ 口径钉死一条＝**class C/U 是"绑定层不覆盖"，不等于考工跑不了**（本岗 1015-04 两张真分就是自物化跑的）⇒ 这三张的正解有两条腿：补册格走绑册通道，或走注入通道自物化（但双臂 NAV 装置属 ⑤/⑪ 产出面，本席不物化、不自装第二份）。

**E2＝CH 让路窗闸的自然实验（本班不越窗，只量它拦不拦）**：同一条命令加 `--binding-book`（使 `ch_free = not args.binding_book` 变 False）后 01:53:58 实跑＝（件 mtime 现读 01:53:58）
stdout `{"refused": "01:00-04:00 夜跑让路窗（矿考循环班令 §三 红线）"}`、**退出码经直接重定向实测 rc=3**（首遍用 `| tail` 量到 rc=0＝在册"管道后 $? 量的是 tail"同坑，已改正；件 `.runtime/tmp/st-qoder-p08-1017-02/e2_refused.txt`）。
⇒ §九-2 的窗面从读码升级为执行级：绑册通道在窗内**硬拒**，注入通道窗内不受该闸拦（本席未行使、未自签 `--override-ch-window-with-reason` 豁免）。

**E3＝刻意不跑**：证明"缺册格→写 blocked 行"需去掉 `--dry-run`，那会向永久分数册 only-add 一条真实行＝本席工序 5"缺数据源不开考"禁止，且会给 ⑨ 覆盖尺添一枚非考试口径行。该结论停在代码级（`comparison_exam.py:255-266`＋`_blocked_row:129-135`）。


### 九-5 官方族无关分诊口把本族 71 张首尾摊平（并据此收窄本班 §三 一处过强措辞）

尺＝`comparison_exam._route_vocab(card)`（**族无关**，直调 `pillars_route`＋`card_binding.classify_card`，零 CH，
件 `.runtime/tmp/st-qoder-p08-1017-02/official_triage_all71.json`，n=71 与 §一 prereg 同帧自洽）。
`family|route|binding_class` 交叉表现测＝

| 组合 | 张数 |
|------|------|
| comparison\|dual_arm\|C | 18 |
| comparison\|dual_arm\|**U** | 1（＝`X-S1-03/comparison/02_dualwindow`） |
| ablation\|dual_arm\|C | 7 |
| **shadow\|dual_arm\|C** | **3** |
| comparison\|series\|C | 18 |
| calibration\|series\|C | 13 |
| shadow\|series\|C | 11 |

加总＝dual_arm **29**（18+1+7+3）／series **42**（18+13+11）＝71 ✓ 与本班 §三 同值（两把尺同帧互证）。
binding_class 面＝**70 张 C／1 张 U**；44 张对照+消融子集的 reason 账＝`target_face_not_index_next_day` 43／
`no_data_binding_section` 1（件 `official_triage_own_dualarm.json`）。按在册 ㉗ 口径钉死＝
**C＝"绑定层不覆盖"≠"考工跑不了"**（本岗 1015-04 两张真分即自物化跑的），故该列是 ⑤ 的接线账、不是可考账。

**据此收窄本班 §三 一处过强措辞（首袋 blob 已入 HEAD，另起本节留旧案）**：§三 表格把 29 张 dual_arm
一律写成"→ 驱动 `comparison_exam.py:255-266` 返回 `_blocked_row`"。实测＝**只有 26 张（comparison 19＋ablation 7）
能进该驱动器**；`shadow` 族 **3 张** 被族闸 `comparison_exam.py:85 _FAMILIES=("comparison","ablation")`＋`:202-205`
**抛 `_ToolError` 异常**（实跑 14 张 shadow 逐张撞同一条，件 `official_triage_own_dualarm.json` 的
`driver_errors` 14 条、错误串逐字＝"family='shadow' 非对照/消融族——本件只考 ['comparison','ablation']"），
**不是 blocked 行**。⇒ 两条后果＝①那 3 张在两个驱动器之间当前无如实入册通道（`calibration_exam.run_card`
不分族、但 route=dual_arm 缺 `signal_b` 时按其 :1036-1047 形态"硬报错不冒判"）；②"族闸拒收"以**异常**形态出现
＝考工若按 §三 旧措辞去跑 shadow 双臂卡，崩的是整批而不是一条诚实行。
（负对照自校：本席首遍用 `grep -rln "'ablation'" scripts/backtest/fexam/*.py` 查"谁消费 shadow 族"得 **0 命中**，
同尺换已知存在词 `'ablation'` 亦 **0 命中**＝该 grep 尺在单引号形态上恒零、无判别力，结论已改由实跑驱动函数取得，
在册律 `zero-hit-ruler-needs-known-positive-control` 复证一枚。）

[BLOCKER] 2026-10-17|⑧B/p08-1017-02|工具缺陷|本族 prereg 里 `family=shadow` 的 **14 张**（其中 dual_arm 3 张）在族驱动器面**无如实入册通道**＝`comparison_exam.py:85` 族闸只收 comparison/ablation，`:202-205` 对 shadow **抛 _ToolError**（14/14 逐张实跑复现，错误串逐字见件 driver_errors）；而 §三 旧措辞"29 张双臂→blocked 行"实为 26 张，3 张 shadow 双臂既进不了对照驱动器、在 run_card 面又缺 signal_b（:1036-1047 硬报错不冒判）⇒ 崩批形态而非诚实 blocked 行|尺面 `.runtime/tmp/st-qoder-p08-1017-02/{official_triage_own_dualarm.json,official_triage_all71.json}`（n=44＋14 errors／n=71 交叉表）；代码锚 scripts/backtest/fexam/comparison_exam.py:85・:202-205・:215-227・calibration_exam.py:1036-1047・card_binding.py:306-338|⑤ 判两选一＝把 shadow 纳入 `_FAMILIES`（则 3 张走 blocked 通道）或让族闸对越族卡返回 `_blocked_row` 而非抛异常（**同族在册处方＝改喂闸的输入形态、不弱化闸**）；本席不自改工具不越族代考；另 ⑥/⑩ 知悉＝官方 `--mode vocab-census` 与本尺 `_route_vocab` 均不分族，shadow 14 张一直在分诊面内、只在执行面外|中


### 九-6 本席自犯改正 1 枚（旧案留卷，不另立 [BLOCKER]，归 §七 第 5 条同族）

§三 那句"其余为自造名（…共 **26 种**）"**读数错**，现测改正＝本族 71 张 `buckets.type` 三档分布＝
**在册 8 词命中 3 张**（全为 `quantile_decile`）／**自造名 68 张、distinct 37 种**（TOP＝arm_matrix 12、
arm_comparison 11、ablation_set 5、event_sample 2、allocator_scheme 2、ordinal_three_level 2）／
**空申报 0 张**；三档加总 3+68+0=71 与 §一 卡池 prereg=71 同尺自洽（尺面
`.runtime/tmp/st-qoder-p08-1017-02/false_red_probe.json` 的 `summary.own_bucket_types`，
distinct 计数＝去掉 `quantile_decile` 与空串后的键数＝37）。
错因＝首版把"打印出来的前几项"当全集目测估数，未跑 `len()`；该错句已随**首袋 blob 入 HEAD**，
故按在册"更正另起一节留旧案卷"处置，不回改首袋字节。给下班一条＝**"共 N 种/N 张"这类计数落笔前必须 `len()` 现算**
（在册律 `counters-in-append-ledger-self-falsify` 第六枚复证）。


本班追加节仍零 CH、零 GPU、零卡面写、零分数册字节、零判据与词表改动、零 worktree；共写面零字节。
本席 [BLOCKER] 第二袋追加 3 条＝§九-5 内联 1 条（中，shadow 族闸）＋本节末 2 条（中 1＝普查口径收敛唯一／低 1＝排班建议一半错）；本班两袋累计 8 条（高 1／中 4／低 3）：

[BLOCKER] 2026-10-17|⑧B/p08-1017-02|流程问题|**工具内已有官方词表普查单口而三席六班一直在自造尺**＝`card_binding.py:2083 build_vocab_census()`＋CLI `--mode vocab-census`（自带 discipline 块＝零写/零CH/路由表达式单份），本班尺与其逐卡对账 42/42 全等；但官方口**不分路径**（本族前缀 81 行混列 series 49＋dual_arm 32），直接引用会把 29 张"跑下去写 blocked（不翻卡不记试次）"误当"写 fail"⇒ ⑥ 立法底座应换官方件＋本岗路径拆分层，全线普查口径应收敛唯一（宪法 §4.2 同域重复簇／§9.5 清单必须生成器产出）|scripts/backtest/fexam/card_binding.py:2075-2080・:2083-2140；scripts/backtest/fexam/comparison_exam.py:295・:311-314；尺面 .runtime/tmp/st-qoder-p08-1017-02/{vocab_census_official.yaml,compare_official_census.py,compare_official_census.json}（per_card_agree_n=42／disagree=[]／official_distinguishes_paths=false）|⑩ 判普查口径收敛（本岗与 ⑦A/⑦c 停自造尺、改官方口＋路径层）；⑥ 立法工单输入面直接取 `--mode vocab-census` 产物；本席不自删他席尺面不代改工具|中
[BLOCKER] 2026-10-17|⑧B/p08-1017-02|工具缺陷|本席 §七 第 2 条给 ⑩ 的排班建议有一半错＝原文"改派 04:00 后或 20:00–23:00"，而让路窗真源 `card_binding.py:2076` 含 **21:00–22:30**⇒ 若 ⑩ 按建议采纳 20:00–23:00 会把班排进第二个让路窗；更正＝真自由窗 04:00–21:00 与 22:30–24:00（旧案留卷不涂）；同帧量到官方 `tally_status.empty=230` vs 上班 §㊾ 现测 208＝全库 empty +22 未定源（属 ⑥ 出题面新增，本席不判）|scripts/backtest/fexam/card_binding.py:2075-2080（两窗逐字）；comparison_exam.py:311-314（窗内 refused→return 3 仅绑册通道，注入通道 ch_free=True 不受拦）；.runtime/tmp/st-qoder-p08-1017-02/vocab_census_official.yaml tally_status.empty=230|⑩ 采纳更正后的两窗；⑥/⑩ 判全库 empty 208→230 的新增归属；本席不代裁|低


### 九-7 与 ⑦c 席已落地案卷合流（02:0x 班尾补记，据此起见归位不当新案卖）＋本族双臂面收窄一枚硬后果

⑦c 席 1017-01 案卷（可 grep 源＝`docs/_working/automation_campaign/p07c_examiner_c/ledger.md`，命中标记
`_comparison_metrics`）给出两条结构性堵点与一条令卡过时项。本班把这三条**落到本席三族面上定量化**（只读直调
`pillars_route`＋卡面字段，02:0x 现测，尺面 `official_triage_all71.json`）：

| 收窄项 | 本席三族现测 | 与 ⑦c 全库面的关系 |
|--------|--------------|--------------------|
| `dual_arm ∧ signal_kind=panel` | 本族 **24** 张（dual_arm 29＝panel 24＋series 5；route×kind 全表＝dual_arm\|panel 24／dual_arm\|series 5／series\|panel 22／series\|series 20＝71） | ⑦c 报全库 28 枚 ⇒ **24 枚在本席三族**＝本席双臂面主形态 |
| `window.regimes` 条目 ISO 日期不足两个 | 本族 **6** 张（`X-S1-04/comparison/05`、`X-S2-02/calibration/03`、`P-P2-01/comparison/02`、`P-P2-03/comparison/02`、`P-P2/comparison/02`、`P-P3-01/comparison/03`）；**负对照＝同谓词架 examined 87 张＝0** ⇒ 尺有判别力 | ⑦c 报全库 13 枚 ⇒ 本族占 6 枚 |
| 令卡「panel 卡禁走 CLI（`--target-csv` 砍单列缺陷未修）」 | 本班零开考未复跑 CLI ⇒ 只登记为**指令面过时嫌疑**转 ⑩，本席不代签 | ⑦c 逐字引 HEAD 面「panel 目标保列语义与 --signal-csv 同款（禁砍单列）」，源=`8caf2743b9` |

⇒ **对 ⑥/⑤ 排工的一条硬后果（本班新增，⑦c 未量化到本族）**：§九-5 说"3 张 shadow 双臂进不了对照驱动器"，
本节再收一层＝**即便 ⑥ 给那 24 张 `dual_arm∧panel` 补上绑定册 arms 格，它们仍会崩在
`calibration_exam.py:561 _comparison_metrics → :217 _series_metrics → :97 pd.Series(2D)`**
（⑦c 双面实测：`run_card` 与 `run_card_comparison(dry=False)` 崩在同一帧）。
所以本族双臂面"**补格即解锁**"的上界实测只有 **5 张**（dual_arm∧series），另 24 张须先有 panel 双臂腿（属 ⑤/⑪ 产出面）。
本班据此把 §三"停驱动分诊路 29"的后果列改写为三档＝**26 张**进对照驱动器拿 blocked 行（其中 24 张补格后转崩）、
**3 张** shadow 被族闸抛 `_ToolError`、**5 张**是本岗短期真候选（且仍须过注入面与截面闸）。

**本班自犯一枚当场打死（不入正文数字）**：首版 regimes 散文谓词写成
`sum(x.isdigit() and x=='-' for x in vv) < 2`，而 `'-'` 非数字 ⇒ 表达式恒 0 ⇒ **71/71 恒真**假扩；
改正为 `len(re.findall(r"\d{4}-\d{2}-\d{2}", v)) < 2` 后得 6 张＋负对照 0/87。
与 §四4、§九-6 同族＝**尺坏与查无同形／满命中亦须负对照**（在册律 `zero-hit-ruler-needs-known-positive-control` 复证）。

[BLOCKER] 2026-10-17|⑧B/p08-1017-02|判据缺失|本族双臂面"补册格即解锁"的上界实测只有 **5 张**＝29 张 dual_arm 里 **24 张 `signal_kind=panel`**，而 ⑦c 已实跑出 `dual_arm∧panel` 崩在 `calibration_exam.py:561→:217→:97 pd.Series(2D)` 且 `run_card_comparison(dry=False)` 崩在同一帧（＝双腿 panel 两条路都不支持）⇒ ⑥ 若按"补格救 26 张"排工会拿到 24 个崩批而不是 24 个诚实 blocked 行；本族另 6 张 `window.regimes` 条目 ISO 日期不足两个（同形崩点 `_in_spans`，⑦c 报全库 13 枚本族占 6）|可 grep 源 `docs/_working/automation_campaign/p07c_examiner_c/ledger.md`（命中 `_comparison_metrics`）＋本班尺面 `.runtime/tmp/st-qoder-p08-1017-02/official_triage_all71.json`（route×kind 交叉 24/5/22/20，负对照 examined 87＝0）；代码锚 calibration_exam.py:561・:217・:97・:72-84・comparison_exam.py:85・:202-205|⑤/⑪ 判 panel 双臂腿（`:217` 的 2D 面）；⑥ 排工按 **5 张**上界而非 26 张，并把"卡面 regimes 必须是日期对"立成出题闸（属判据面须 chief，本席不自立）；本席不自改执行器不越族代考|中

本节末追加一条＝本班 [BLOCKER] 累计 **9 条（高 1／中 5／低 3）**：首袋 5（§七）＋第二袋前段 3（§九-5 内联中 1＝shadow 族闸／本节末中 1＝普查口径收敛唯一／本节末低 1＝排班建议一半错）＋本节 1（中＝panel 双臂上界）。
本班仍零 CH、零 GPU、零卡面写、零分数册字节、零判据与词表改动、零 worktree；共写面零字节。

---

## 10-17 02:30 开班 · 班次 03（st-qoder-p08-1017-03）本班出分 0 张＝CH 窗 01:00–04:00 **连续第三班**整窗覆盖班窗；主产出＝⑥ 单腿立法实测非免费午餐（合成探针＋在册真行先例双证）＋上班 [BLOCKER] 高 的诉求方向当场改判（早退形态已有统筹批复真源与 ⑨ 席在册单）＋⑥ 立法工单具名面落成＋本族出题面停供实尺＋⑩ 两裁在裁定册零条目

### 〇、本班时序与环境（全部现测，非引用）

- 开班 `date` **02:30:12**（冷启动第 1 条同命令）；`python --version` 3.12.8。
- 冷启动第 2 条 `lock_files.py cleanup`＝**CLEANED 5 枚死锁**（p01 ledger＋checkpoint／p03 ledger＋checkpoint／`data/strategy_intake/lane_p0_obi_candidates.csv`）＋**SALVAGED** 死会话 `st-qoder-p04-1017-02`（merge=skipped／stash=0 件／释放 claim=0）；同命令首行报 `SessionRegistry: failed to load legacy registry: [Errno 13] Permission denied: .runtime/session_registry.json`（在册聚合面 Permission denied 复证，本席不动权限）。
- 冷启动第 3 条 `process_reaper --status`（02:30:46–02:30:54 帧）＝`source=live`／`last_run=02:30:26`／scanned 37／killed 0／reported 27；水位 `commit_pct=83.7`、`ram_used_pct=74.8`、`cpu_pct=48.6`、`degraded=False`、`breached=[]`（`breaches=1` 与 `breached=[]` 同输出互斥＝⑩ 1017-01 在册复量同形，本席不据此开单）；`drift={'stash_count': 27, 'worktree_changes': 1489}`；`dead_archive: ok=False rc=1`＝serializer 租约存活（pid=47508）＝销账通道本班仍不可用。
- 防重入三尺并读＝①游标末态「10-17 班次 02 已交账」；②`lock_files.py list` 全表 **2** 行且全是 `st-qoder-p07c-1017-02` 的 ledger＋checkpoint（剩余 30.0m／29.9m），对 `p08` 命中 **0**；③取号三面并集（在册律 `shift-numbering-predicate-must-union-three-faces`）＝台账末节「班次 02」∪ `.runtime/tmp` 最大 `st-qoder-p08-1017-02`（36 件）∪ `.runtime/sessions` 最大 `st-qoder-p08-1017-02` ⇒ **1017-03 三面皆空**＝无鬼班，本班取 `st-qoder-p08-1017-03`。
- 会话注册＝`open_session(SID,[],[])`（reg_pid=0）＋`_spawn_heartbeat_daemon` → **daemon pid=12216**，`heartbeat_st-qoder-p08-1017-03.pid` 回读=12216；归属证据＝`heartbeat.jsonl` **首行** `ts=2026-10-16T18:36:22Z`（UTC＝本地−8h ⇒ 本地 02:36:22，与本班开班同段）且 `pid=12216` ＝本班自家守护、非沿用他班遗留进程（02:44:57 复量 18 行、末行 `status=alive`）。
- 首调 `mark_logical` 被拒＝`MARK_LOGICAL_DENIED …（非 chief 形态词 ∧ 心跳不新鲜）`（守护刚起、jsonl 尚未生成）；02:4x 复命 `mark_logical` **True**、现读 `logical=True`。在册限定＝`seat-claim-keeper-duality` 明记 mark_logical 挡不住外来 cleanup 收 claim，故本班按"复 acquire 后立刻投袋"执行，不把 logical 当护身符。
- 本班窗况＝开班 02:30:12 起全程在 **01:00–04:00 夜跑让路窗**内（收班 `date` 见 §十）⇒ **⑧B 连续第三班整窗被吃**（01 班 00:30 开班仅余 30 分／02 班 01:30 开班 60 分全在窗内／本班 02:30 开班全在窗内）。动作定性据 ⑩ 1017-01 班批准措辞「**生效前该窗内一律走本地尺面自证、禁硬跑造二次试次或假红**」（可 grep 源 `docs/_working/automation_campaign/p10_line_lead/checkpoint.md:140`）＝本班零开考、零卡锁、零 GPU、零分数行。

### 一、下班首查四件复量＝四件全部未动（本班现测，只报 delta；上班基线 01:36:33／01:48／01:54 三帧）

| # | 该查什么 | 本班现测 | 判定 |
|---|---|---|---|
| ① | ⑥ 是否立法前 4 键或先并名 `turnover_cost_gate`↔`turnover_or_cost_gate` | 词表现值 `calibration 5／dual_arm_union 14／event 7`＝与上班逐值同；`top4_legislated` 四枚（maxdd_delta_max／sharpe_vs_baseline_min／turnover_cost_gate／tracking_diff_max）**全 false** | 未动 |
| ② | ⑥ 是否给三张零越表双臂卡补绑定册 arms 格 | `02_binding_book.yaml` entries **18**／approved **17**，本族命中格仍只有 07 与 07b（两卡均 examined）⇒ 三张卡零格如故 | 未动 |
| ③ | ⑤ 是否接 panel 多日腿／桶名拒考闸；是否处理早退披露位 | `calibration_exam.py` 现 1,163 行；`:251-252` 仍 `def _panel_metrics(...)` ＋ `ret = target.shift(-1)`；`_forward_face` 出现行号＝[175,182,189,195,**212**]（消费点仍只在 :212）；`:741-747` 仍是 `return "fail", [f"未支持判据键（机判面待扩，fail-closed）: {sorted(unknown)}"]` **无披露腿** | 未动 |
| ④ | ⑩ 三件＝排班窗改派是否生效／旧址册退役签批／断链册入库 | 本班仍是 02:30 窗内开班＝**cron 执行腿未生效**；旧址 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml` 盘 exists=True＋`git cat-file -e HEAD:` rc=0＝退役未签；`git ls-files docs/04_research_records/governance/working_ref_sweep_20261015/`＝**空**（盘上 `broken_records.yaml` 786,491B 在位）＝⑩ 自述"连续第 13 班零推进"续期为第 14 班 | 未动 |

- 真跑前置另查＝`.runtime/tmp/p07/` 目录在（37 件）而 `shift06_*.parquet` 命中 **0** ⇒ 上班 §㊼「共用宽面板缓存断料」未复，下班若要真跑仍须先重拉（单列成本在册实测 56.3 秒／列，⑦A 1016-03 同口独立读数 12–62 秒）。

### 二、本班尺面 delta 复量（三行谓词尺＝工具自家路由，非正则面）

- 本族 71 张 prereg＝**假红路 38／停驱动分诊路 29／真判可达路 4**；route 分布 `dual_arm 29／series 42`＝与上班 01:5x 实跑读数 `OWN {blocked 29, false_red 38, reachable 4}` **逐值相等**（本班件 `preflight.json` 与上班 `false_red_probe.json` 同尺同面）。
- 尺承重正对照（同尺换 status 谓词，全库 examined）＝`{reachable 83, false_red 1, blocked 3}`＝与上班第二条命令读数逐值相等；`control_all_card_files=609`。
- **本族分母首次按目录摊开**（改正尺后）＝`exit_flow 51`（prereg 25／empty 19／examined 4／blocked_on_impl 3）＋`portfolio_flow 37`（prereg 21／empty 16）＋`position_flow 63`（prereg 25／empty 18／blocked_on_impl 16／blocked_on_data 2／examined 2）＝加总 **151**、prereg 加总 **71** ⇒ 与上班 §58 聚合读数 151＝prereg71/empty53/examined6/blocked_on_impl19/blocked_on_data2 **逐格互证**（empty 19+16+18=53／examined 4+2=6／bi 3+16=19／bd 2）。
- 分数册（两谓词并读＋三面同帧）＝新址 `docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` **145,458B／sha16 a9532fceb0899c94／rows 110**（顶格谓词 `^- card_id:` 110；缩进谓词 `^  - card_id:` 0＝该册行形态为顶格，两读并列防尺坏）；盘 mtime 2026-10-16T22:45:20、末笔 `0b3c365c74`（10-16 23:14:57＝本席 1016-02 袋）；`head_equals_disk=True` ⇒ **今日 10-17 全线分数册增量 0 行续存**（与 ⑨ 1017-01/02、⑩ 1017-01 自述同值）。
- 旧址（改正上班 §㊸ 的谓词不覆盖）＝盘 103,529B／73 行，HEAD 73 行（两谓词并读：顶格 73、缩进 0）＝**旧址仍是新址严格前缀形态未变**，退役判据上班 §㉚ 已给齐、仍无人签。

### 三、本班头号＝**⑥ 单腿立法不是免费午餐**（合成探针＋在册真行先例，双证）

上班 §54 给 ⑥ 的"立法前 4 键"与给 ⑤ 的"补机器面"是两条腿；本班实测二者**不同步落地**会把假红换成静默放行：

- 尺＝`.runtime/tmp/st-qoder-p08-1017-03/vocab_leg_probe.py`（直调 `calibration_exam.judge()`，三张合成卡、零业务数据、零写、零分数册字节）：
  - **A** 五柱全在表且都有面 → `verdict=pass, fails=[]`；
  - **B** A＋一根越表键 `maxdd_delta_max` → `verdict=fail`、`fails=['未支持判据键（机判面待扩，fail-closed）: [\'maxdd_delta_max\']']`（＝独立复证上班的反事实双卡对照）；
  - **C** 把 B 的那根换成**在册但机器面未接**的 `ic_ir_min`（metrics 给 `ic_ir=0.5` 与 `ic_ir=None` 各跑一遍）→ **两遍皆 `verdict=pass, fails=[]`** ＝一根被卡面冻结、在词表内、而无机器面的柱，判官**既不记败也不阻断**。
  - 附带：`_unjudged_pillars(card, m, judged)` 签名要 `judged` 集合 ⇒ 披露发生在**出 row 的那一层**而非 `judge()` 内（本班直调缺参报 `TypeError`，如实记）。
- 在册真行先例（不是本席推演）＝尺 `row_precedent.py`，件 `row_precedent.json`：110 行中 `unjudged` 非空 **79** 行；其中 `verdict=pass` 且带无机器面数值柱的行＝**rows[76] `TDM-E-L1-S2/calibration/41_agg_lu_count_z20_fwd10`（run_id `p07a-agg8-20261015-41_agg_lu_count_z20_fwd10`）与 rows[78] `.../43_agg_lu_ratio_z20_fwd10`**，其 `unjudged.numeric_keys_no_machine_face.ic_ir_min` 逐字＝「ic_ir 无从评估（series 路恒 None／panel 路 NaN＝ICIR 面未接，judge 同时跳过加败）」＝**同一形态已在 HEAD 面以 pass 行存在**。
- 后果（给 ⑥/⑤/chief，本席不自裁）＝若 ⑥ 先把高频越表键加进词表而 ⑤ 的机器面未接，则那 38 张的 `fails` 从"覆盖文案"消失、verdict 由其余柱决定 ⇒ **假红消除，代价是卡面那根冻结门柱等于没评**。而 `calibration_exam.py:744` 注释自引的统筹口径是「还卡面冻结判据以真意，不是改门柱」——两形态（fail-closed 定败 vs 披露位放行）哪个更违"真意"，属 chief/⑤ 判据面，本席与下班均无权自改。
- 请 ⑨ 侧一条读法＝上列两枚 pass 行按"该柱未评"读，勿当"门柱全过"（与上班 §㉟ 同源，本班给出具名行号）。

### 四、上班 [BLOCKER] 高 的诉求方向本班改判（留旧案不涂，另起本节）

- 旧案（上班 1017-02 §七第 1 条，高）＝「`judge():741-747` 早退吞柱…请 ⑤ 判是否改（动 fail-closed＝动判据，本席无权）」。
- 本班实测＝该早退**不是待裁的新问题**，而是已批复语义且已有一张在册单：
  - 真源锚（可 grep）＝`docs/_working/automation_campaign/iteration_history.md:207` 逐字「该语义＝统筹 **2026-10-12 01:35 批复②** 已裁面，本席不重裁」；代码内注释 `scripts/backtest/fexam/calibration_exam.py:744` 同引「统筹 01:35 批复②步骤②：『还卡面冻结判据以真意，不是改门柱』」。
  - 该节同时记 ⑨ 席已据批复**新开 修㉕**（转 ⑤，两条披露腿＝①短路前仍评估有面柱并写入披露位、②`oos_ok` 类布尔字段"同号≠达标"语义声明位；**verdict/阈值字节不变**）。
  - 本班实测 修㉕ 未执行＝`:741-747` 现值无披露腿（见 §一③）。
- 改判措辞＝把"请 ⑤ 判是否改早退形态"改为"⑤ 手上已有一张**不动 verdict** 的披露位在册单（修㉕），本班实测未落地＝催执行"；真正的待裁面移交给 §三（立法与机器面是否必须同批）。上班那条 [BLOCKER] 原文不涂，本席另立一条覆盖。

### 五、⑥ 立法工单具名面（把上班的分母落成可执行清单；尺 `preflight_v2.py` 件 `preflight_v2.json.legislation_ticket`）

- 假红路 **38** 张／distinct 越表键 **59**／只差**一根**柱的卡 **5** 张（逐张具名＋各自缺的那一根，下班与 ⑥ 勿再从 tmp 反查）：
  1. `docs/03_modules/_domain_backtest/exam_cards/exit_flow/S1/TDM-X-S1-04__calibration__03_席位净卖出派发前瞻收益.yaml` → 缺 `gap_bucket3_vs_0_20d_max`
  2. `…/position_flow/P1/TDM-P-P1-03__calibration__02_因子秩回落对后续超额预测.yaml` → 缺 `band_separation_min_pp`
  3. `…/position_flow/P1/TDM-P-P1-04__calibration__05_板块退潮动量对持仓下行预测.yaml` → 缺 `threshold_gap_min_pp`
  4. `…/position_flow/P3/TDM-P-P3-02__calibration__03_加仓触发涨幅对后续收益预测.yaml` → 缺 `curvature_direction`
  5. `…/position_flow/P3/TDM-P-P3-04__calibration__02_尾盘强势对次日高开概率预测.yaml` → 缺 `probability_top_bucket_min`
  ＝5 张需 **5 根不同键**（"最小立法集"是 5 键不是 1 键）；其中 **4 张属 position_flow、1 张属 exit_flow**＝立法收益直接落本席写域。
- 频度 Top12（卡次）＝`maxdd_delta_max 15／sharpe_vs_baseline_min 14／turnover_cost_gate 11／tracking_diff_max 10／pairs_min_for_verdict 4／precondition_hit_rate_min 3／brinson_consistency 2／net_bp_per_pair_min 2／cost_after_sharpe_gate 2／min_days_per_cell 2／gap_bucket3_vs_0_20d_max 1／misjudge_cost_gap_min 1`。
- 集合关系申明（防下一班误并）＝这 5 张与 §二"真判可达 4 张"**不是同一集合**：4 张真判可达＝`position_flow/P1/TDM-P-P1-02/calibration/02|04`、`/P1/TDM-P-P1-04/calibration/04`、`/P3/TDM-P-P3-04/calibration/04`，全 `signal_kind=panel` 且冻结持仓池 top20（20 只/日），仍撞 `ic_exam.py:96` 三十列地板（上班 1015-04 同帧双对照在册，本班未重烧）⇒ **词表立法只动 38 张假红路，动不了这 4 张**；4 张的正解在 ⑥ 重冻宇宙／⑤ 供数面，不在本席。

### 六、双臂面 delta＋`level_to_cap_map` 形态可抄（新事实）

- 尺＝`git grep -l level_to_cap_map -- <exam_cards>` 命中 **3 枚具名**（本班现测，上班 §㉕"对 comparison/02 命中 0"仍成立——02 不在三枚内）：
  - `…/exit_flow/X1/TDM-X-R1-01__comparison__07_five_state_cap_anchor.yaml`（status=examined，盘 mtime 10-16 11:56:17，in HEAD）
  - `…/TDM-X-R1-01__comparison__07b_reset_ladder_anchor.yaml`（examined，mtime 10-15 19:00:53，in HEAD）
  - `…/TDM-X-R1-01__comparison__07c_oos_pairwise_cause_disclosure.yaml`（**blocked_on_impl**，mtime 10-15 19:00:53，in HEAD）
- 给 ⑥＝补 `comparison/02` 的卡面机读映射位**有同母卡现成形态可抄**＝07c 的 `data_binding.level_to_cap_map`，其口径自述为"从卡面自拟 L1..L4 数字改锚**在册判定件（MOD-RK-049）position_cap 五态表逐字值**"＝不是新造映射、是搬在册真源。
- 给 ⑤/⑨＝**抄形态可行、抄依赖不可行**：07c 自身 `status_reason` 自述其唯一增量（OOS 配对三因披露腿：len(m)／两侧 std()／级别序列是否整段驻留 0.0）在 ⑤ 写域、在册单 **修⑬ 形一** 未落地 ⇒ 07c 长期挂 blocked_on_impl；02 卡不要求该披露，故补格＋补映射位不必等 修⑬。三因分账判据（`len(m)<60⇒样本因；≥60 且某侧 std()=0⇒恒常数因；皆非而仍 NaN⇒对齐/类型因`）＝07c 引 ⑨ 席 p09-1015-10 在册实数，本席原样转述不改写。
- 上班 §64 的"补格上界 5 张（panel 24 张另崩 `calibration_exam.py:561→:217→:97`）"本班未重烧（属 ⑤/⑪ 腿，无新证据即不重复立案）。

### 七、本族出题面停供＝全线新卡 100% 流向 ⑦A 写域（新尺，给 ⑩/③/⑥）

- 尺（改正版）＝`git log --since=2026-10-16 20:00 --name-status -- docs/03_modules/_domain_backtest/exam_cards` 逐件计数＝**47 件**（`A` 44／`M` 3），按族＝`entry_flow 46／exit_flow 1`；那唯一一枚 `M`＝本席 1016-02 班自己翻卡（`…/exit_flow/S1/TDM-X-S1-04__calibration__02_突破失败连续次数前瞻收益.yaml`，commit `0b3c365c74`）⇒ **本族自 10-16 20:00 起零新卡、零卡面改动**。
- 涉及提交（逐件带 commit/时刻入件）＝`960332289b2`（③ 1017-01 班具名子题卡 12 张）、`a434598d05`（③ 1017-03 班代落上班 10 张）、`381cae9582`（③ 1017-03 班本班 10 张）等，路径前缀全为 `exam_cards/entry_flow/L2|L3|LROOT/`。
- 与 ⑩ 1017-01 班「③ 席选题判据放宽批准（附三硬条件）」的实测后果＝放宽带来的产能**全部注入 ⑦A 写域**；本岗 ⑧B 的输入面处在停供状态。⇒ 本班不反 ⑩ 的"不加第 4 考工席"判定（三席 0 产出的证据仍在），但请 ⑩ 记一条修正：**⑧B 的瓶颈不是人头，是出题面流不进来＋班窗全在 CH 窗内**，二者任一不解，本岗每班产出上界仍是 0–1 张。
- 尺坏自纠（本班次生，见 §九 BLOCKER 第 5 条）＝本班 v1 用 `path.split("/")[3]` 判目录归属（真位 `[4]`）⇒ 三族状态全报空 dict；v1 解析 `--name-status` 用 `len(f)>=3`（`A`/`M` 行只有两字段）⇒ 读得"零变更"。两谓词同面双读留卷＝`neg_control_dir_predicate={index4_hits:151, index3_would_hit:0}`、`pos_control_namestatus={v1_len_ge3_would_read:0, v2_len_ge2_reads:47}`。

### 八、⑩ 两裁在裁定唯一真源册零条目（流程问题，本席不代裁不代登）

- 现测＝对 `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` **HEAD 与盘面两面**，谓词 `排班窗`／`考工窗`／`选题判据`／`⑧B`／`让路窗` 命中**全 0**；同尺正对照＝谓词 `DSR 由` 命中 **1**（证明尺能命中该册正文，非谓词伪空）。
- 案卷面存在＝`docs/_working/automation_campaign/p10_line_lead/checkpoint.md:140` 与同席 ledger 有"两裁已下"原文；该两件本班 `git status --porcelain` 读 `MM`（盘与 HEAD 有在途差）。
- 加重背景（引在册、不另立案）＝该册正处被陈旧基底整档回写的状态：本班同尺读到**盘 4,811 行／555,546B**、**HEAD 5,026 行／385,329B**（行数与 ⑩ 1017-01 班 01:49 读数 4,810／5,025 同值，差 1 系口径＝`wc -l` 换行数 vs 换行数+1；行数少而字节多的矛盾本席不解释、只并列呈面，恢复载体与三步单在 ⑩/⑫ 名下）。
- 对本班的影响＝本班**不依赖**该裁定开工（指令卡"CH 窗禁跑"独立生效，本班照守）；风险在下一班＝若有席按"改派已批准"自行挪班或改判本岗性质，缺可核对真源。⇒ 请 ⑩ 按 RULE-RULING #8 给两裁补登记（或指出其应落哪一面），⑫ 恢复册时一并处理。

### 九、本班 [BLOCKER] 行（五条，事中当场追加，非班尾攒写）

[BLOCKER] 2026-10-17|⑧B/p08-1017-03|判据缺失|**⑥ 单腿立法（补词表不配机器面）＝把"立即定败"换成"零评估仍可 pass"**＝合成探针 C（`ic_ir_min` 在表而面未接，`ic_ir` 喂 0.5 与 None 两遍皆 `verdict=pass/fails=[]`）＋在册真行先例双证＝HEAD 面分数册 **rows[76]/rows[78]**（⑦A `p07a-agg8-20261015-…` 两枚 pass 行，其 `unjudged.numeric_keys_no_machine_face.ic_ir_min` 逐字"judge 同时跳过加败"）⇒ 上班 §54 的"⑥ 立法前 4 键"与"⑤ 补机器面"若不同步，38 张假红不是被治好而是换成静默放行，而 `calibration_exam.py:744` 自引的统筹口径恰是"不是改门柱"|尺面 `.runtime/tmp/st-qoder-p08-1017-03/{vocab_leg_probe.py,vocab_leg_probe.json,row_precedent.py,row_precedent.json}`（rows_with_unjudged=79／pass 具名两枚含 run_id）；代码锚 scripts/backtest/fexam/calibration_exam.py:741-747・:744・`_unjudged_pillars(card,m,judged)`；在册批复真源 `docs/_working/automation_campaign/iteration_history.md:207`|chief 判"词表立法须与机器面同批"还是接受披露位 pass；⑥/⑤ 据该判决定排工次序；⑨ 对 pass 行按"该柱未评"读（具名行号已给）；本席不改判据不代裁|高
[BLOCKER] 2026-10-17|⑧B/p08-1017-03|流程问题|**⑩ 1017-01 班"两裁"在裁定唯一真源册零条目**＝对 `ruling_registry.yaml` HEAD 与盘面，谓词 排班窗/考工窗/选题判据/⑧B/让路窗 命中全 **0**（同尺正对照"DSR 由"=1）；两裁原文只活在 ⑩ 自家 `checkpoint.md:140`／ledger（`MM` 在途态），而该册盘面正处陈旧基底整档回写态（本班复证 盘 4,811 行/555,546B vs HEAD 5,026 行/385,329B，行数与 ⑩ 01:49 读数同值）|件 `.runtime/tmp/st-qoder-p08-1017-03/rr_head.yaml`＋`preflight_v2.json.ruling_registry_v2`；在册同题＝⑩ 1017-01 头号案卷与记忆 `ruling-registry-evaporation-direct-write-20261016`|⑩ 按 RULE-RULING #8 给两裁补登记或指出应落哪一面；⑫ 执行册恢复时把两裁一并入 PG 源（册首自述 PG registry_ledger 为唯一真源、YAML 是投影⇒补登须走投影生成器禁手改）；本席不代登不自裁；下一班禁把"改派已批准"当已生效事实引用|中
[BLOCKER] 2026-10-17|⑧B/p08-1017-03|数据问题|**本族出题面停供**＝`git log --since=2026-10-16 20:00 --name-status -- <exam_cards>` 逐件现测 47 件（A44/M3），按族 `entry_flow 46／exit_flow 1` 且那枚 `M`＝本席 1016-02 自己翻卡⇒⑧B 三族（exit/portfolio/position）自 10-16 20:00 起零新卡；③ 席"选题判据放宽"裁定的实测产能 100% 注入 ⑦A 写域（`960332289b2`/`a434598d05`/`381cae9582` 路径前缀全 `exam_cards/entry_flow/…`）|件 `.runtime/tmp/st-qoder-p08-1017-03/preflight_v2.json` 的 `cards_changed_since_1016_2000_fixed`（逐件 path/op/commit/when/subj）＋正对照 `pos_control_namestatus`（v1 谓词读 0／v2 读 47）|③/⑥/⑩ 判 ⑧B 三族补出题流（或按上班呈批把本岗正式改判"普查＋转单岗"并同步 SOP §3⑧）；本岗不自选题不定卡|中
[BLOCKER] 2026-10-17|⑧B/p08-1017-03|流程问题|**CH 让路窗连续三班整窗吃满 ⑧B 班窗**＝开班 `date` 02:30:12 至收班全在 01:00–04:00（01 班 00:30 余 30 分／02 班 01:30 全窗／本班 02:30 全窗）＝⑩ 批准的"排班窗改派"cron 执行腿未生效（App/Owner 面）⇒ 本岗工序 3 连续三班不可执行，每班实际只能出尺面与转单；本席按批准措辞走"本地尺面自证"，未硬跑、未自签 `--override-ch-window-with-reason`、未走注入通道规避|开班与收班 `date` 现测；批准原文可 grep `docs/_working/automation_campaign/p10_line_lead/checkpoint.md:140`；窗真源 `scripts/backtest/fexam/card_binding.py:2075-2080`（两窗 21:00–22:30 与 01:00–04:00）；闸实测上班 `comparison_exam.py:311-314` 窗内 `refused→rc=3`（件留卷 `st-qoder-p08-1017-02/e2_refused.txt`）|Owner/App 落 cron（本席无执行腿）；⑩ 若确认 cron 面不可用，请把 ⑧B 窗内班**定长为尺面班并写明产出定义**（现指令卡保底"≥8 张出分或跑满 4 小时"在窗内结构性不可达，已连续三班）；本席不自改班限班次|中
[BLOCKER] 2026-10-17|⑧B/p08-1017-03|工具缺陷|本席自犯两枚坏尺当场改正（旧读数不涂）＝(a) 目录归属谓词 `path.split("/")[3]`（该路径真位在 `[4]`）⇒ 三族状态全报**空 dict**（假无源），改正后 151 逐格与上班聚合值互证；(b) `git log --name-status` 解析用 `len(f)>=3`，而 `A`/`M` 行只有两字段⇒整批被丢、读得"10-16 20:00 后零变更"（若入册即一条假数据问题）；另 (c) 分数册旧址首读沿用缩进谓词得 0 行（上班 §㊸ 已预警该谓词不覆盖旧址行形态），两谓词并读后＝旧址 73 行（盘与 HEAD 同）|件 `preflight_v2.json` 的 `neg_control_dir_predicate`（index4=151／index3=0）、`pos_control_namestatus`（v1_len_ge3_would_read=0／v2_len_ge2_reads=47）、`score_book_two_faces`（indent2=0 与 toplevel=110/73 并列）；v1 产物留卷 `preflight.json`|本席当班改正（已落 §二/§六/§七）；给全线一条＝**解析 git `--name-status` 必须按"首字段状态字母、末字段路径"而非固定字段数**，且任何"零变更/零命中"读数须同帧给一把能命中的正对照（在册律 `zero-hit-ruler-needs-known-positive-control` 第七次复证）|低

### 十、本班收班八件（逐项现测；本班零开考故零卡锁、零 GPU）

| 件 | 本班读数 |
|---|---|
| ① release 全部 claim | 本班写面前 `lock_files.py acquire` 两件（ledger＋checkpoint），投袋前复 acquire＝**复 acquire 后立刻投袋**（在册 `seat-claim-keeper-duality`：mark_logical 挡不住外来 cleanup）；入袋后归零读数属"落袋之后"态，本席不在本正文预写自估读数，谓词交下一班现跑＝`python scripts/lock_files.py list` 对 `p08` 命中数（上班 1017-02 第五枚复证在册） |
| ② 注销心跳 | 按在册 `heartbeat-respawn-on-any-python-call-20261017` 改判据＝**不以 PID/pid 文件为终态判据**（代起口＝本席任何一次 python 调用，pid 文件恒指已死首枚）；本班终态判据＝`SessionRegistry.unregister(SID)` 返 True ＋ `.runtime/session_registry/<sid>.json` 文件撤除 ＋ 该 sid `heartbeat.jsonl` 之后零新增；杀进程只在末次网关动作之后按 argv 逐元等值做**降数**动作，禁 cmdline 子串批杀 |
| ③ 记实际耗时 | 开班 `date` 02:30:12／收班 `date` 见本节末现测行；两戳差由 ⑩ 复核，本席不写自估终值（在册律 `counters-in-append-ledger-self-falsify`） |
| ④ [BLOCKER] 追加 | §九 五条已事中逐条落盘（高 1／中 3／低 1）；行首形态与本台账既有约定一致，谓词 `grep -n "\[BLOCKER\]"` 与严式行首两尺并读 |
| ⑤ 自清收口 | 本班 `.runtime/tmp/st-qoder-p08-1017-03/` 件＝尺面（open_session／preflight＋json／preflight_v2＋json／vocab_leg_probe＋json／row_precedent＋json／rr_head.yaml／land_docs.py／ledger_body／notes_delta／cursor_body／msg）＝按在册"尺面留下班复用"案**保留 json 与 py**（§五 具名工单与 §三 探针是下班对账锚），`rr_head.yaml`（385KB 临时导出，正文已入台账读数）本班末删除；删除前按 `tmp-cleanup-breaks-own-script-dependency` grep 消费者 |
| ⑥ GPU 还牌 | 本班零 acquire ⇒ 免执行（如实记不适用） |
| ⑦ 后台子任务 | 本班零 spawn ⇒ 零孤儿 |
| ⑧ 零 worktree | 本班未调任何工棚/建道入口（TRAE-079 Phase 2 照守）；尺＝`git worktree list` 对 `st-qoder-p08-1017-03` 命中数，本班 §〇 开班帧未含该行，交下一班同尺复量；历史遗留 `.worktrees/st-*` 与 `.aidrafts/` 本席号段壳（1016-02／1016-03／1017-01／1017-02）＝不自删、报 ⑩ 清理专班（在册申明代建属网关阶段 3 非席位违规） |

- 袋面申明＝只投本席写域两件（`ledger.md`＋`checkpoint.md`）；分数册与卡面零字节故**不入袋**；`ruling_registry.yaml` 与 `02_binding_book.yaml`、⑩/⑦c 在途件一律不随袋（袋＝整档快照＝归属篡改）。
- 本席 [BLOCKER] 累计＝本班新增 5 条（高 1／中 3／低 1）；上班 1017-02 两袋累计 9 条（其台账 §九-7 末行在册申报），本班未改他席旧行。

---

## 10-17 02:5x · 班次 03 追加节（同班·第二袋）：立法×机器面配对表（本班 §三 结论的分母面，给 ⑥/⑤ 排工）

### 十一、⑤ 侧成本分层实测（零 CH、零写；尺 `.runtime/tmp/st-qoder-p08-1017-03/{machine_face_pair,face_stem}.py`＋同名 json）

- 分母（本族 prereg 越表键全集，两路合并＝series 越表 ∪ dual_arm 越表）＝**106 根 distinct**；本班按 exact-stem 尺逐键读三态（词干在度量生产函数源／词干在两文件全文／键名整串在全文）。
- 读数＝**词干已在度量面的只有 1 根**＝`sharpe_vs_baseline_min`（14 卡，词干 `sharpe` 在 `_series_metrics/_panel_metrics/_comparison_metrics` 源内命中）⇒ ⑤ 对该键只差"接柱进判官"；**其余 105 根词干与键名整串在两文件源内零命中**，含上班点名的前四高频里的三根（`maxdd_delta_max` 15 卡／`turnover_cost_gate` 11 卡／`tracking_diff_max` 10 卡，另 `turnover_or_cost_gate` 10 卡）＝若属实则 ⑤ 要从头算该量，不是接线活。
- **尺的已知失效形态（如实挂，禁当证明用）**＝正对照把尺架在在册 5 键上：`ic_mean/ic_ir/mono_spearman` 三根词干命中（True），而 `oos_same_sign`/`regime_same_sign` 两根**同样判 False**＝它们的面不在 metrics 函数而在判官布尔支⇒本尺对"面在判官内而非 metrics 内"的键**必然漏报**，故"105 根无面"是**上界不是证明**；负对照＝乱造词干 `zzqx_not_a_real_metric` 两尺皆 False（尺不假阳）。第二条 caveat＝词干切分按后缀剥（`turnover_cost_gate`→`turnover_cost`），若 metrics 只算 `turnover` 则本尺判无面而实际存在半分腿⇒须 ⑤ 侧人工分词复量。
- 与 §三 合流的排工后果＝⑥ 单腿立法在 106 根里今天只能让 **1 根**立即变成"真评"，其余 105 根立法后落进"零评估仍可 pass"形态（探针 C＋在册 rows[76]/[78] 先例）⇒ **"⑥ 立法前 4 键"与"⑤ 补机器面"必须同批**，且首同批建议取 `sharpe_vs_baseline_min`（唯一已有一半腿的）＋`maxdd_delta_max`（最大频次）配对试一轮，跑完由本岗复量假红路是否从 38 真降。
- 本席不做的事＝不自立词表（属 ⑥ 写域＋须 chief）、不自改判官（属 ⑤ 写域）、不因本表开任何一张考（窗内禁跑）。

### 十二、本班袋面实况（首袋 env 死＋同班另投严格超集袋；含本班一处当场改判）

- 首袋 `q-20261017-st-qoder-p08-1017-03-0001`（files=2）02:52:44 入队 → 02:57:56 **判 dead**，`dead_reason` 逐字＝
  「git 瞬态环境失败，项退回 pending 等下次自举: `git reset`（硬复位档，原文两词以空格连字符相连，此处形近转写免自触闸）到 refs/heads/dev -> rc=128: fatal: Unable to create
  `D:/ZephyrAlpha/.git/worktrees/w1/index.lock`: File exists…（env_retry=3 次耗尽，升级死信）处方: 环境类失败重试耗尽——
  排除 worktree/磁盘/锁环境故障后 requeue 重投」＝⑩ 1017-01 在册头号死族 `other:landing 异常`／`env:git` 同族新枚。
- 环境实尺（本班只查不断）＝`.git/worktrees/w1/index.lock` **盘上存在、0 字节、mtime 02:31**（`ls -la` 现测 03:04 帧）；
  同尺数得 10-17 02:00 起 `dead/` 面新增 **22 枚**，reason 分布＝`landing 异常: 非注册表族件双侧皆改真冲突` 14／
  `门禁 TAKEOVER-PENDING` 3／**`git 瞬态环境失败…git reset` 2**（本班＋`st-qoder-p05-1017-01` 03:01:00 同串）／
  `REGISTRY-MASS-` 1／`PERMANENT-SYSTEM-TRIGGER` 1 ⇒ 该 lock 在 4 分钟内已打死两枚袋，**归属＝⑫/⑩（共享落地面）**，
  本席按宪法"锁文件先查持有者再动"未删不检疫（他席正用该 worktree 的可能性未排除）。
- 同班改判披露（旧稿未落地故原地改写，留此痕）＝本节初稿曾写"本班投本第二袋前已实测首袋 `state=done`"，
  该句写于 02:5x（当时袋在 `processing`）＝**把中途态当终态**；03:05 复量袋面得 `dead` ⇒ 全文按 dead 改写。
  在册同族＝`counters-in-append-ledger-self-falsify`／`measured-readings-must-share-claim-sentence-timepoint`。
- 超集判定（在册"代投前必逐件做超集判定"）＝本班先证盘面两件 sha256 **逐字节等于**死袋 blob
  （`ledger.md` 14b4d187b127cba2／`checkpoint.md` 1af8d66c11716081，两枚 EQUAL=True 现测）＝死袋字节无人改动，
  本袋内容＝死袋内容 ⊕ §十一–§十二 ⊕ 游标 71–72 ⇒ **严格超集**；死袋不 requeue（同字节必同死且内容已被本袋吸收）、
  不代销（销账权在 ⑩/⑫，本席只留 dead 件原样）。
- claim 实态与上班相反＝本班入队回执 `ENQUEUE-RENEW: claim 续租 **2/2** 件（ttl=7200s）`，
  02:53 帧 `lock_files.py list` 对 `p08_examiner_b` 命中 2 枚（持有者本 sid／剩余 119.5m／来源=入队续期）
  ⇒ 上班 1017-02 在册"claim 入队即归零第五枚复证"在本班**未复现**（＝第六枚反证，形态随续租腿是否生效而变）；
  本班据此把收班① 做成真放锁，且照守"袋在飞禁放锁"。

[BLOCKER] 2026-10-17|⑧B/p08-1017-03|工具缺陷|**共享落地面被一枚 0 字节陈旧 `index.lock` 卡死**＝本班首袋 `q-20261017-st-qoder-p08-1017-03-0001` 死于「`git reset`（硬复位档，形近转写）到 refs/heads/dev → rc=128: Unable to create `.git/worktrees/w1/index.lock`: File exists」且 `env_retry=3` 耗尽即升死信（**清锁腿不存在**）；本班现测该 lock **盘上存在、0 字节、mtime 02:31**，同尺数得 10-17 02:00 起 `dead/` 面 22 枚里同串 env:git **2 枚**（本班 02:57:56＋`st-qoder-p05-1017-01` 03:01:00）＝4 分钟内咬死两席；本席按宪法"锁文件先查持有者再动"**未删不检疫**（他席正在用该 worktree 的可能性未排除，代删＝可能洗掉在途落地状态）|证据＝`ls -la .git/worktrees/w1/index.lock`（03:04 帧）＋死信件 `.runtime/commit_queue/dead/q-20261017-st-qoder-p08-1017-03-0001.json` 的 `dead_reason` 逐字；同尺读数件 `.runtime/tmp/st-qoder-p08-1017-03/preflight_v2.json` 之外另见本节正文；在册同题＝⑩ 1017-01 班工序 8/死族分账（`other:landing 异常` 113 枚居首）|⑫/⑩＝给 serializer 一条"env:git lock 型死信→先按 worktree 逐个查 lock 的 mtime 与持有进程再检疫"的单口（禁直接 rm），并定 `env_retry` 耗尽后谁负责清环境；本席不自清他席 worktree 锁不代裁|高

本节另起一条 ⇒ 本班台账内 `[BLOCKER]` 行谓词 `grep -c '^\[BLOCKER\] 2026-10-17\|⑧B/p08-1017-03\|'` 现值＝6（§九 5 条＋本节 1 条）；§九 的"五条"计数不涂＝写该节时实况（在册律 `counters-in-append-ledger-self-falsify`），终值请下班自跑谓词为准。

- 本案卷自触闸一次并当场改正（在册律 `gate-01-ruling-ref-self-trigger` 六形态之「逐字引死信里的 reset 串」）＝本班 §十二 与上一条 [BLOCKER] 原稿逐字抄了死信 `dead_reason` 里的 `git reset`＋硬复位两词连字符形态，被 `GATE-PRECOMMIT-RUN`（hook `gate-detect-git-dangerous`，ABS-27）在 own-scope staged 面拦下 2 处 ⇒ 超集袋 0002 死。正解按 Owner 在册固定处方＝**改喂给闸的输入**（本席自家未落地稿行内形近转写＋留本条披露），**不动闸、不弱化闸、不加白名单、不标 SELFDOC 豁免**（该标记只给列禁令的清洁册用，本台账非清洁册）；死信原文仍逐字存活于 `.runtime/commit_queue/dead/q-20261017-st-qoder-p08-1017-03-0002.json`，读者要原文可径取该件＝耐久面未因本席转写而丢证据。
