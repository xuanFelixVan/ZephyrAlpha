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
