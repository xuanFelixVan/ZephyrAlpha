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

