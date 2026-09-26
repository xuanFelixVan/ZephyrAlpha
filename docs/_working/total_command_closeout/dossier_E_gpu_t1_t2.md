---
ttl: task_bound
---
# 案卷 E — GPU T1/T2 实况（机械核验，非裁定）

- 取证时间：2026-09-26（盘上实测 + `git show HEAD:` 落地面）
- 工作区：`D:\ZephyrAlpha`，分支 `dev`，HEAD=`54622bbbf4`
- 取数纪律：ClickHouse 侧仅用会抛错的 reader；未启停任何长跑进程；冻结判据件只读。
- 态标记：`实`=盘上/HEAD 实测；`不`=与声称不符；`缺`=拿不到原始记录；`半`=部分成立。

## 主表

| # | 声称出处 | 命令 | 实测读数 | 态 |
|---|---|---|---|---|
| 1a | 交接书：T1 全量粗扫已完赛 | `ls data/strategy_intake/grid_20260926-024947` | 存在，5 件：`manifest.csv`(2,239,062B)、`net_returns.parquet`(54,377,088B)、`negatives.csv`(971B)、`summary.json`(569B)、`handover_verdict.yaml`(9,881B)；目录 mtime 2026-09-26 08:00:52 | 实 |
| 1b | 3698/3700 评完 + 2 阴性 | `wc -l manifest.csv`；`cat summary.json` | manifest.csv=**3699 行**（含表头→3698 数据格）；summary：`n_raw=362880` `n_sampled=3700` `evaluated=3698` `eval_dead=0` `backtest_dead=2` `degraded_recipes=0`；`negatives.csv` 恰 2 数据行 | 实 |
| 1c | grid_result / 评分文件计数 | `find … -iname '*grid_result*' -o -iname '*score*'` | **0 件**：该目录无独立 grid_result/评分文件，评分只在 `manifest.csv` 列（`sharpe,ann_return,max_drawdown,avg_turnover,net_days`）+ `net_returns.parquet` | 不（产物形态与声称口径不同） |
| 1d | 更早 T0/T1 现场、仍在写目录 | `ls -d grid_*` + 逐目录 mtime | `data/strategy_intake/` 下 **25 个 grid_* 目录**（最早 `grid_20260915-051448`，含非时间戳名 `grid_gpu_sectorcond_20260924-0834`、`grid_t0_conditional_v1`）；最新 mtime = `grid_20260926-024947`(09-26 08:00:52)，其内文件 mtime 07:47，**晚于文件 13 分钟**＝目录被后续动作（哨兵）改写，非仍在回测写入 | 实 |
| 1e | handover_verdict.yaml 存在 + VERDICT 字段 | `grep -n -i verdict handover_verdict.yaml` | 文件存在。**无 `VERDICT:` 字段**（首行是 `schema: t1_t2_handover/verdict-1`）；判定语义落在 `blocking_criteria` / `all_green` | 不（字段名不符） |
| 2a | 哨兵 t1_t2_handover.py 在 HEAD | `git ls-tree -r HEAD \| grep t1_t2_handover` | HEAD 面**无** `scripts/backtest/t1_t2_handover.py`；仅 `docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/AUTO_t1_t2_handover.md` 在 HEAD（注：该 md 由 commit `830c3a5736` 入册） | 不 |
| 2b | 同上（盘面） | `ls -la scripts/backtest/t1_t2_handover.py`；`git status --porcelain scripts/backtest/` | 盘面存在 45,525B，mtime 09-26 07:53；`git status` = **`AM`**（已 add 进 index 的新增 + 工作区又有改动）＝**在 index、不在 HEAD** | 半（缓发＝未落地） |
| 3a | 引擎去重改造 commit `62898892` | `git rev-parse --verify 62898892` | 验真：`62898892edc1bf1daf0d104eca7548eca43dc69b`，标题 `[st-ddup-20260925][去重改造] 回测引擎三处重复计算治本…`（自述：等价证尺=真实库掩码逐位对拍 PASS + 合成面板双探针 + 10 套件 114 测试绿、新增 12 例；单格 35.33s→~5s） | 实（号真） |
| 11 | 备份护甲 `D:\zephyr_t1_backup\` | `du -sh` + `find -maxdepth 1 -printf %T@` | 存在；`du -sh`=**95M**；子目录 `strategy_intake/`(mtime 09-26 02:49) + `shield.log`(5,084B，mtime **09-26 14:26**＝仍在被写) | 实 |
| 10z | T2 / 做T 全量算是否仍在跑 | `tasklist` + `Get-CimInstance Win32_Process`（python+pythonw） | **10 个 python/pythonw 进程存活**，逐条命令行见「新增发现 A」。其中**无** factory_grid/t1_t2/做T 3/271 批相关命令行 | 待补（详见缺口） |

## 新增发现（非清单条目，实测顺带）

### A. 存活进程全列（只读数，未动任何进程）

| PID | 起 | 命令行摘要 |
|---|---|---|
| 27916 | 09-25 04:08 | `python -m zephyr.gov_enforcement.rule_bridge.write_audit_daemon D:\ZephyrAlpha --daemon` |
| 8240 | 09-25 10:02 | `scripts\ops\ch_health_probe.py` |
| 17376 | 09-25 16:25 | `pythonw -m …worktree_drift_watchdog D:\ZephyrAlpha --daemon` |
| 32180 | 09-25 22:05 | `python -m zephyr.data.tick_subscriber` |
| 5056 | 09-25 23:26 | `scripts\governance\evaporation_blackbox.py` |
| 37548 | 09-26 01:37 | `python -u -c` 会话保活循环：`SessionRegistry('D:/ZephyrAlpha').register('st-ddup-20260925', task_files=['scripts/backtest/factory_grid_executor.py','scripts/backtest/translated/_c4_engine.py','src/zephyr/backtest/regime_validation/exam_cost_gate.py'])`，`while True: … time.sleep(300)` |
| 30956 | 09-26 02:31 | `python -m zephyr.data.scheduler` |
| 22744 | 09-26 09:20 | `pythonw D:\ZephyrAlpha\scripts\data\board_index_realtime.py` |
| 33160 | 09-26 13:38 | `python -m …commit_belt_daemon D:\ZephyrAlpha` |
| 32312 | — | 未在 Get-CimInstance 输出中出现（tasklist 有、命令行查询未列出），待复核 |

注：37548 是 **sleep-loop 常驻进程**，占用 `st-ddup-20260925` 会话名并对 3 个业务文件持续持有 claim 语义——与宪法 §9.3「永久系统禁 cron/Timer/sleep-loop」是事实对撞，仅登记不裁定。

### B. 哨兵自判结论（`handover_verdict.yaml` 原文摘要，88 行起）

```
blocking_criteria:
- manifest_points
- dead_zero
- cost_gate_spot
garbage_hits: []
all_green: false
```
逐项实测（同文件 8-95 行）：
- `manifest_points`：measured **3698**，threshold `==3700±0`，pass **false**
- `dead_zero`：measured `eval_dead=0 / backtest_dead=2 / gate_dead=0`，threshold 三者=0，pass **false**
- `cost_gate_spot`：measured `source=replay, sampled=50, ok=22, bad=28`，threshold「抽查≥50 格五档全真跑；最高档(40bp) sharpe>=survival_floor(0)；逐档非增（容差 1e-09）」，pass **false**
- `degraded_zero` pass true（measured 0）；`negatives_discipline` pass true（`neg_rows=2, accounted=3700, n_sampled=3700`）
- `n_eff` pass true（measured 19，threshold >=12）
- `dsr` measured **null**，pass true，note 自述「deferred……此处 pass=True 仅指'不阻塞发车'，非'DSR 已完成'声明（诚实位）」
- garbage_lines 四项：completion_rate measured **1.0**（threshold >=0.95）、death_rate 0.000541、suspicious_sharpe_share 0.001352、condition_axis_zero_sample=`not_evaluable(归因件未生成，巡检脚本补位)`；全部 hit false
- 完整性锚：`manifest_sha256=311d64481ad2db20c9540a43200ae0de99c3b8f085cc90613d3a29a1973df0e6`，`prereg_sha256=da8fbbfb58dcaa56d620ee6bb0cda76cee795fad55606703c9dcf827b6b9d5af`，`generated_at: 2026-09-26T08:00:52+08:00`，`ranking_metric: sharpe`

**内部矛盾登记（只读数）**：`manifest_points` 判 false 的尺是「manifest 行数==3700」，而 `negatives_discipline` 用「manifest+negatives==送评格数(3700)」判 true；同一份产物在两处被要求不同分母。

### C. `negatives.csv` 两阴性格原文读数（对应清单 #6）

| recipe_id | death_layer | death_reason | detail |
|---|---|---|---|
| `d6759a48a594` | backtest | `backtest_fail:RuntimeError` | `insufficient_net:1622` |
| `4bdf3555a27d` | backtest | `backtest_fail:RuntimeError` | `insufficient_net:1622` |

两格配方共同点：`A2_combine_weight=halflife60`、`C_sizing=kelly_050`、`G_universe=all_a_ex_st`、`D1_rebalance_freq=weekly`、`I_cost_tier=frozen_l0`、`K_capital_ramp=lump`；差异在 `B_top_n`(top10/top20)、`E_single_cap`(cap10/cap5)。
两格均**不在** manifest.csv（3698 行）中＝无 sharpe/net_returns 读数（待 #6 复核）。

### D. `cost_gate_spot` bad_head 前 10 读数（40bp 档 sharpe，全为负）

`7a48794552a3:-2.9651`、`8fc499f3acb9:-0.3633`、`1749f2a5284f:-1.9137`、`f781b865fd75:-1.2565`、`4eb8141e74be:-1.1203`、`a18a77f6855a:-1.0329`、`9a00638fb301:-1.5472`、`e3b92a9cfca0:-1.7745`、`0052cce0c18c:-0.3649`、`f718ffcb4fe4:-3.0958`（`survival_floor=0`）
另有 `cost_replay.rows` 段（94 行起）给逐档 0/5/10/20/40bp 曲线样本，如 `31bd2b1aa480: 0.7445→0.695→0.6455→0.5466→0.3485`。`source: replay`＝抽查读数来自**重放**而非当轮真跑（与 threshold 文案「五档全真跑」用词不一致，登记）。

## 无法判定 / 缺口（v1）

- 清单 #2 复杂度门复算、#3 测试可跑性、#4 文档计数、#5 成本门口径原文、#6 阴性格对拍、#7 cmd_successor 13 件、#8 LEDGER、#9 冻结件审计、#10 T2 池基、#12 待裁池 8 条——**均未取数**，本卷仅覆盖 1、2a/2b、3a、11 及进程快照。

---

## 追加批次 2（清单 #2 复算 / #3 / #4 / #6 / #8 / #9）

| # | 声称出处 | 命令 | 实测读数 | 态 |
|---|---|---|---|---|
| 2c | 落地被复杂度门拦（"存量 52 层嵌套>上限15"） | 探针 `.runtime/tmp/total_command_closeout/probe_cc.py`（复用 gate 自家 `_cyclomatic_complexity`，`_MAX_COMPLEXITY=15`，源文件 `src/zephyr/gov_enforcement/commit_gates/high_complexity_gate.py:82,102`） | 该文件 36 个函数；**cc>15 的有 3 个**：`run_acceptance` line 358 **cc=52**、`run_handover` line 828 **cc=31**、`build_t2_subspace` line 630 **cc=16**。**"52" 是圈复杂度读数不是嵌套层数**——实测最大语句嵌套深度仅 5（run_acceptance/run_handover）；全文件最大 nest_depth=5 | 半（数值 52>15 真，"层嵌套"口径错） |
| 2d | 门是否真的会拦这个文件 | 读 `_check` 高复杂分支 L169-183 | 门只对 `node.lineno in added_lines` 且**函数名不在 HEAD 版本**的函数计分；`t1_t2_handover.py` **整文件为新增**（HEAD 无此路径）→ 36 函数全算新增 → 3 个违规必拦。聚合台 `COMPLEXITY-GUARD`(priority=92, L200-232) 另并 `NO-GOD-CLASS`/`NO-LONG-PARAM-LIST`（LEDGER 自述 `build_t2_subspace` 13 参亦属该族） | 实（拦得住） |
| 3b | commit 62898892 内容 | `git show --stat 62898892ed` | 8 文件 +659/-124：`scripts/backtest/factory_grid_executor.py` +196、`scripts/backtest/translated/_c4_engine.py` +202、`src/zephyr/backtest/regime_validation/exam_cost_gate.py` +44、测试 4 件（test_c4_batch_smoke +92 / test_c4_limit_gate +119 / test_exam_cost_gate +38 / test_factory_grid_executor +83）、`_domain_backtest/algo_flow/exam_cost_gate.yaml` +9。**是 HEAD 祖先**（`merge-base --is-ancestor`=YES），且这三个源件 `disk==HEAD` 零 diff（改造现役） | 实 |
| 3c | "原 628 行为语义逐位保持" | `git show <c>:<f> \| wc -l` 逐件 | 三件行数：executor 931→1095（HEAD 1095）、_c4_engine 570→700（HEAD 700）、exam_cost_gate 194→232（HEAD 232）。**无任何一件等于 628**；"628" 在 ddup commit 与其 stat 面均无对应读数（案卷未取到该数的实物锚） | 不（读数无锚） |
| 3d | 114 测试绿可跑性 | `pytest tests/backtest/test_factory_grid_executor.py -q -p no:cacheprovider --basetemp=.runtime/tmp/totcmd_basetemp` | **首跑 INTERNALERROR**：`pytest.PytestConfigWarning: Unknown config option: cache_dir`（`-p no:cacheprovider` 与 `pyproject.toml:171 cache_dir=…` 互斥；该陷阱在 `pyproject.toml:160-162` 注释里已自述，解法须 `-c` 精简 ini 或去掉该项）。补 `-W "ignore::pytest.PytestConfigWarning"` 后：**collected 37 items → `37 passed in 28.21s`**（该单文件 37 例，非 114） | 半（可跑，需绕行；单文件 37≠114） |
| 3e | 等价对拍产物在 HEAD | `git ls-tree -r HEAD \| grep -i EQUIVALENCE` | `docs/_working/decision_map_campaign_20260924/EQUIVALENCE_VERDICT_T0_200.md` **在 HEAD**（盘上另有多处 worktree 副本） | 实 |
| 4a | commit `16d58a652d` | `git rev-parse --verify` / `--is-ancestor` | `16d58a652d9d011daef656cedaa60bec14516382` 真，HEAD 祖先 | 实 |
| 4b | "quant_methodology 11 册" | `git ls-tree -r HEAD \| grep -c quant_methodology`；`git show --name-only --pretty=format: 16d58a652d \| grep -c` | **HEAD 面 = 10 件**（01-06 六册 + README + appendix_A/B/C）；commit 自身落盘面也=10 件；"11 册"只出现在 commit message 与 LEDGER §九 文字里（message 括号内列举主题数=9）。盘上同目录亦 10 件 | 不（10≠11） |
| 4c | "gpu_rewrite 十册" | `git ls-tree -r HEAD \| grep -c gpu_rewrite` | **10**，与盘上 `docs/_working/gpu_rewrite/` 10 件一一对应（compute_inventory/gpu_landscape/hotspot_census/industry_gpu_landscape/migration_roadmap/rewrite_architecture/rewrite_architecture_three_tiers/roadmap/validation_framework/verification_framework） | 实 |
| 4d | "战役目录 97 件修正面" | `git log` 四 commit 逐个计数 | LEDGER §九 点名的 4 件 commit 全部验真且均为 HEAD 祖先：`070a11d549`=20 文件、`93e55f2f46`=34、`75dcbbb0d1`=33、`870aa42fa6`=31（合计 118 文件，其中落在 `decision_map_campaign_20260924/` 的**去重后=69 件**）；另有 `51581acf00`=1 文件（token 先行批，真） | 不（69≠97，含全域 118≠97） |
| 4e | "AI 层三条暂禁 gate 已翻回 true" | `grep -n -A6 gate_id` 于 `docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`（盘与 `git show HEAD:` 同值） | 三条**均 `enabled: true`**，行号：`REAL-KEY-REFERENCE-SCAN` **:710-715**（true 在 :715）、`TASK-ORDER-DOCS-LOCK` **:716-721**（:721）、`CONSTITUTION-LINE-LIMIT` **:722-727**（:727）；注记原文"09-26 st-ddup 翻回（W4 看守项）：AI 层 245/678 件批已落 HEAD（30505c93f6），negative_list_gates 三工厂实测可导入，解封条件成立"。盘/HEAD 无差 | 实 |
| 4f | 上述注记引用的 commit | `git rev-parse --verify 30505c93f6` | `30505c93f6c195435bcda423d1394351609bc8c1` 真、HEAD 祖先；标题自述"AI层P1终局大单…678件v6 emergency通道"（**注：该标题含 `Owner批准B方案四门临时禁用+emergency_commit通道` 字样，属 commit message 自述，未经裁定册验证**）；名册该文件另含 `enabled: false` 计 5 条（非 ADJ 案卷所述 7 条），`total_gates: 103`（:40） | 实（号真）/待复核（件数口径） |
| 6a | 2 阴格在哪几行 | `grep -c` recipe_id 于 manifest | 两 recipe_id 在 `grid_20260926-024947/manifest.csv` 命中数 **0**（未评分，故无行）；只存在于同目录 `negatives.csv` 第 2-3 行（`d6759a48a594`、`4bdf3555a27d`） | 实 |
| 6b | "net_returns 真零方差" | 读 `factory_grid_executor.py:793-795` 哨兵源码 | 哨兵式：`if len(net.dropna()) < 60 or float(net.std()) == 0: raise RuntimeError(f"insufficient_net:{len(net)}")`。阴格 detail=`insufficient_net:1622`，而 1622=全窗交易日数（window 2019-01-04→2025-09-09）＝**打印的是 len(net) 而非 dropna 计数，两个触发分支不可分辨**；零方差为可行解释，非直读证据。`net_returns.parquet` shape=(1757, 3699)，两阴格不在列（无法从产物直读其方差） | 缺（口径不区分分支） |
| 6c | "同配方旧引擎同死" | `grep -rl d6759a48a594 data/strategy_intake/` | 全 `data/strategy_intake/` 仅 3 处命中：新 `negatives.csv` + **`grid_20260915-052749/manifest.csv`、`grid_20260915-060812/manifest.csv`**。该两跑是旧现场（window **2020-01-01→2023-12-31**、`n_sampled=2000`、`degraded_recipes=1753`），且 `d6759a48a594` **评出分了**：`sharpe=-0.153, ann_return=-0.0717, mdd=-0.4736, avg_turnover=0.0005, net_days=970, degraded=('C_sizing',)`——是"存活且负"，非"同死"。同配方在**同窗（1622 日）旧引擎**的现场：不存在——`grid_20260925-232032`、`grid_20260926-021530` 均为 200 格 n_sampled=200（不含该两格，negatives 0 行）；`grid_20260925-111219`/`grid_20260924-213246`/`grid_20260919-230009` 皆 0 文件 | 不（无同窗旧引擎对拍件） |
| 8a | LEDGER 在 HEAD | `git ls-tree … \| grep cmd_successor` | `.../cmd_successor_20260925/LEDGER.md` **在 HEAD**；盘上 205 行，`git status`=`MM`（index 与工作区各有未落改动） | 实 |
| 9a | 冻结判据件近期是否被改 | `git log --oneline -5 -- <file>`（分件查） | `config/search_space_prereg.yaml`：最近 3 次 = `102a3748fa`(裁定#413 GPU 点火三件套，**2026-09-24 21:39:36**)、`170aa0f569`(T0 标定回填 35.33，改 1 行)、`294b4d24fe`。`config/exam_scale_cost_gate.yaml`：最近 = `294b4d24fe probe-c4`、`0f08f7a06c`(池化终批 v3)、`80880932d4`(成本考尺修真批，**含 yaml 预注册档新增**)。**09-25/09-26 两夜无一键改动**；`git diff HEAD -- <两文件>` 为空（盘=HEAD） | 实（无近期改动） |
| 9b | 冻结件现役阈值 | `grep -n` `config/exam_scale_cost_gate.yaml` | `tiers_bp: [0, 5, 10, 20, 40]`(:11)、`survival_floor: 0.0`(:13)、`monotonic_tol: 1.0e-09`(:15)。`config/search_space_prereg.yaml`：`tier1_points: 3700`(:60)、`tier2_points: 900`(:61)、`cost_gate_in_every_tier: true`(:62)、`single_job_wall_clock_cap_hours: 12`(:67)、`wall_clock_hours: 59`(:55)、`per_point_seconds_measured: 35.33`(:57)、`grid_points_cap: 25000`(:58) | 实 |
| 5a | 17 号文成本门条款原文 | `git show HEAD:…17_quantified_acceptance.md \| sed -n '8,26p'` | 在 HEAD；条款在 **§一 表格 L17**（"抽查 ≥50 格五档全真跑；40bp 档 sharpe≥survival_floor(0)；五档单调非增（容差 1e-9）"），另 L9 "完成率＝manifest=3,700 格 ±0；backtest_dead=0/eval_dead=0/degraded=0"、L13 负结果纪律、L21 垃圾触发线、L24 解读纪律。**文面通读 §一：抽查样本面写的是"抽查 ≥50 格"，未见"从通过成本门的幸存者分层抽"限定语**（该分层口径见 LEDGER §五·补 R-2 的解释性澄清，非 17 号文原文） | 实（原文已贴，限定语缺） |

---

## 追加批次 3（清单 #5 复算 / #7 / #10 / #12）

| # | 声称出处 | 命令 | 实测读数 | 态 |
|---|---|---|---|---|
| 5b | "抽查 50 格 40bp 档 sharpe>=0" 条款 | `git show HEAD:docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md` | 原文 10 行（HEAD 面 §一，绝对行号 L15-L24）：<br>L15 `## 一、GPU 成绩单判据（垃圾判据——跑前对表）`<br>L16 (空)<br>L17 `| 判据 | 量化线 | 度量 |`<br>L18 `|---|---|---|`<br>L19 `| 完成率 | manifest=3,700 格 ±0；backtest_dead=0/eval_dead=0/degraded=0 | grid 产物 manifest.csv |`<br>L20 `| 成本门真实性 | 抽查 ≥50 格五档全真跑；40bp 档 sharpe≥survival_floor(0)；五档单调非增（容差 1e-9） | manifest cost 列+抽查重放 |`<br>L21 `| 有效样本 | N_eff≥12（T0 实测口径） | 报告头 |`<br>L22 `| DSR | e7_defense 浮动门槛（n_trial_ledger 累计口径，裁定#306） | 自动管线 |`<br>L23 `| 负结果纪律 | 主效应前 20% 外全部入 negatives.csv，行数≥(3700-740)× T1 占比推算 | negatives.csv 行数 |`<br>L24 `| **垃圾触发线**（任一命中即报 Owner） | 完成率<95%／死亡率>1%／sharpe>2 的格子占比>5%（好得可疑）／条件轴任一格零样本／prereg hash 变动 | 巡检脚本 |` | 实 |
| 5c | 两班"互证"33% 负 | 独立复算 csv 读 `grid_20260924-080309/manifest.csv` | **可复算**：200 格中 sharpe<=0 = **66 格 = 33.0%**，min(sharpe) = **-4.7830**——与 `AUTO_t1_t2_handover.md:127`（"33% 格点 sharpe<=0、最低 -4.78"）逐位吻合。旁证：旧引擎 T0 基线 `grid_20260925-232032` = 64/200 = 32.0%（min -4.1760），新引擎对拍 `grid_20260926-021530` = 64/200 = 32.0%（min -4.1760，与旧引擎同读数） | 实（可复算） |
| 5d | 本轮"56% 负" | 读 `handover_verdict.yaml` criteria.cost_gate_spot.measured | **可复算**：`sampled=50, ok=22` ⇒ `bad=28/50=56%`；`source: replay`（重放腿，非当轮真跑）。原始逐格记录两处：①同文件 `cost_replay.rows`（L97 起，每格 0/5/10/20/40bp 五值）②`.runtime/tmp/ddup/handover_dryrun.log`（74,119B，mtime 09-26 08:00:52；尾行 L432 `[VERDICT_RED] blocking=['manifest_points', 'dead_zero', 'cost_gate_spot'] garbage=[]`、L433 `STATUS=VERDICT_RED`） | 实 |
| 5e | 17 号文是否含"分层抽幸存者"限定 | 读 L20 原文与 LEDGER:72 | 17 号文原文写"抽查 ≥50 格五档全真跑"，**无**"从通过成本门的幸存者分层抽"字样；该限定语只出现在 LEDGER:72（§五·补 R-2，自标"解释性澄清（非改判据）"）；LEDGER:201 记"上轮实测 33% 负，本轮 56% 负" | 实（差异在文面） |
| 7a | 交接目录 13 件待入库 | `find -type f` vs `git ls-tree HEAD`，comm 差集；`git status --porcelain --untracked-files=all` | 盘 **51** 文件 == HEAD **51** 文件；差集双向**皆空**；该目录 status 输出仅 **1 行** = `MM .../LEDGER.md`。**盘面无 13 件未跟踪件** | 不（无 13 件缺口） |
| 7b | 13 件口径出处 | `grep -rn "13 件" campaign/` | 唯一命中 `EV_root_cause_and_cure.md` L65/L184/L231：把 LEDGER N-1 的"13 件不在 HEAD"定性为 **watchdog A1 卸 index 条目致 git 视野不可见**（`git reset HEAD --` 后 unlink），非从未入库；L231 另记该目录全史仅 2 commit（`8b8f494465` 增、`610f7da6d8` 改）。LEDGER N-1 原文口径实为"01~08、12 号文不在 HEAD（README 导航指向的九件缺失）" | 半（13 件系他班自述定性） |
| 7c | 编号号文在 HEAD 否（N-1 现状） | `git ls-tree -r HEAD \| grep -E 'campaign_20260924/[0-9]{2}_'` | HEAD 面共 **10 件**：09、10、11、13、14、15、16、17、18、19；**01~08 与 12 号文仍不在 HEAD**，且盘上同为这 10 件（即非"仅缺入库"，盘上亦无该 9 件） | 实（仍缺） |
| 7d | R5-DIGIT-SUFFIX 真源判定式 | `grep -n` on `src/zephyr/gov_enforcement/commit_gates/r5_digit_suffix_gate.py` | 正则 **L80**：`_DIGIT_SUFFIX_RE = re.compile(r"_\d+$")`（SSoT 同源 `src/zephyr/governance/rule_patterns.py:116` 同式）；判定式 **L97-105**：对 commit 内每个文件的 rel path 逐**父级目录名**（排除文件名）匹配，命中入 suspect_dirs；**L115-133**：`git ls-tree HEAD <dir>/` 有输出 ⇒ 判"历史违规"跳过，无输出 ⇒ new_violations ⇒ **L137-142 阻断**；名册 `in_process_gate_registry.yaml:142-148`（`enabled: true` :148，`files_trigger: docs/ scripts/ src/ data/` :143）；**豁免通道只有"目录已存在于 HEAD"一条**（progressive_convergence，L39 自述），无白名单、无逃生标记 | 实（新建时 `cmd_successor_20260925` 必被拦） |
| 7e | 该目录当初如何过门 | `git log --diff-filter=A -- .../LEDGER.md` + 相关 commit 标题 | 首次入 HEAD = **`30505c93f6`**（AI 层 678 件批；标题含 `[Owner批准B方案四门临时禁用+emergency_commit通道]`——commit message 自述，未经裁定册验证）。目录入 HEAD 后，后续任何触碰即被 7d 的"历史违规跳过"放行。**绕行先例在册**：`b3e308271d`、`f8ceb47ccd`、`75dcbbb0d1`、`870aa42fa6` 四标题均写"cmd_successor_20260925 目录 R5 待裁"；顶 commit `54622bbbf4` 记"**重投袋：目录去数字后缀过 R5**"；`bb09a39848` 记 `wo001_003→wo_intake_reconcile` 改名"治 R5 数字后缀目录" | 实 |
| 10a | 有无 T2 产物 | `ls -d data/strategy_intake/*t2* *tier2*`；`find -iname "*subspace*" -o -iname "*t2_handover_claim*"` | **无 T2 目录、无 T2 subspace JSON、无 `t2_handover_claim.yaml`**（哨兵 L216 以该文件作幂等认领位）；prereg `tier2_points: 900`（:61）现役 | 实（T2 未发车） |
| 10b | "池基悬空/合格名单未落主区"现状 | `grep -rln "qualified_list\|晋级池\|promotion_pool" src scripts config data` | 全仓命中仅 **1 个代码文件**：`scripts/backtest/exam_cost_reexam.py`（含 `qualified_list` 符号）；无名为 qualified/晋级 的数据件（同名噪声仅 `data/databases/governance_metadata/audit_governance_architecture_system_qualification_standard.json`，与本役无关）；构造路径 `build_t2_subspace()`（哨兵 L630，选层规则文档 `AUTO_t1_t2_handover.md` §四 L69 起）**产物面为空** | 实（无落主区件） |
| 10c | 做T 3/271 批长跑是否仍在跑 | `tasklist` + `Get-CimInstance Win32_Process`（含 pythonw） | **无**任何命令行含 `t0`/`271`/`factory_grid`/`t1_t2_handover` 的存活进程；LEDGER:13 旧 T1 `PID 3584`、§九 新 T1 `PID 33548` **均已不在进程表**；T1 目录末次写盘 07:47（产物）/08:00（裁决件）。存活进程见「新增发现 A」 | 实（无在飞长批） |
| 12-① | 方案①两轮制 prereg 重签 | `grep -c 两轮` 案卷件；`grep -n "两轮\|two_round" config/search_space_prereg.yaml`；`git log -3 -- <prereg>` | 案卷件在 HEAD（"两轮"8 处）；**prereg 内该二词命中 0**；prereg 最近改动仍是 `102a3748fa`(裁定#413, 09-24 21:39)、`170aa0f569`、`294b4d24fe`——**未重签**。裁定#413 原文（HEAD 册 L5701-5712）自述"方案①两轮制……改列下一窗口升级案……待建成+红蓝后实施" | 实（未做） |
| 12-② | t0 甲位三版本分叉 | `grep -c 甲位` 案卷件；`grep -rn 甲位 campaign/*.md` | 案卷件在 HEAD（"甲位"8 处）；战役根文档另有 10 处提及；该件最近改动 commit = `30505c93f6` | 待（案卷在册，未见分叉产物） |
| 12-③ | L09-C01 编排器收拢 | `grep -c L09-C01` 案卷件；`grep -rn L09-C01 _registry/catalogs/*.yaml \| wc -l` | 案卷件在 HEAD（3 处）；**全部 catalog 内 `L09-C01` 命中 0**（议题/模块未在册登记） | 实（未注册） |
| 12-④ | emoreplay 交接 | `grep -c emoreplay` 案卷件；`grep -rln emoreplay src scripts config` | 案卷件在 HEAD（9 处）；代码侧真文件 3 个：`src/zephyr/alt_data/emotion_index_replay.py`、`src/zephyr/backtest/regime_validation/condition_package.py`、`scripts/audit/t0_gpu_condition_pack.py`（另 2 个 pycache） | 实 |
| 12-⑤ | 修宪入口 | `grep -rn 修宪 campaign/`；`grep -rl 修宪 docs/ --include=*.md \| wc -l` | campaign 命中 2 件：`19_gpu_plan_and_master_backlog.md:94` 行内容 `| F6 | 修宪挂图书馆入口 / 12 项 AI 层批文 | 有空 |`、`HANDOVER.md`；全仓 docs md 含"修宪"共 **34 件**；`ADJ_rulings.md` 内命中 **0**（无专件） | 实（仅待办面） |
| 12-⑥ | `single_job_wall_clock_cap_hours=12` 口径 | `grep -rn <key> src scripts config` | **全仓仅 2 处且皆为配置文本自身**：`config/search_space_prereg.yaml:67`（12，注"schedule_gate_policy timebox gpu 键同值（超时=调度层中止）"）、`config/schedule_gate_policy.yaml:97 gpu: 12`；**src/ 与 scripts/ 内零消费点**＝无任何代码读该键（与 LEDGER:71 R-1"对 executor 零牙齿"自述相符；实测未见中止接线） | 实（无牙齿） |
| 12-⑦ | 清道三袋 ARCH 议题注册 | 读 `ADJ_qingdao_three_bags.md` §2.3；`grep -rn 清道 architecture_issue_registry.yaml` | 案卷件在 HEAD；其自述实测：议题册共 **804 条 entries**、`ARCH-RULES-CLEAN-410` **不存在** → "议题注册"是待办非已办；机制真源 `approval_resolver.py:70` marker 正则 `\[ARCH-APPROVAL:(#?ARCH-[A-Z0-9_-]+)\]`，`:140-149` `_id_in_entries` 要求 id 实存于议题册或裁定册，`:275` 伪造拒绝；议题册现有 #410 相关描述段（:22525） | 实（未注册） |
| 12-⑧ | EV-02~06 治本进度 | `ls/grep` 15 号文 + 16 号文 + `EV_root_cause_and_cure.md` | 三件均在 HEAD：`15_evaporation_cure_plan.md`(3,050B)、`16_missing22_recovery.md`(16,086B)（盘 mtime 均 09-26 13:25）、`EV_root_cause_and_cure.md`；后者 EV 标号出现次数 EV-01×11 / EV-02×9 / EV-03×3 / EV-04×1 / EV-05×2 / EV-06×2 / EV-07×2；**EV-06 自述"未落地"**（L184：A1 仍 `git reset HEAD --` 后 `snap.unlink()`，无回收站/refs 双存证）；两文最近改动 commit = `8b8f494465 chore(derived): watchdog 派生缓存自动收敛——B类白名单稳定漂移 44 件（零活跃会话，#ARCH-308 A2）`（16 号文另有 `610f7da6d8`） | 实（部分未完） |

## 引用裁定号核实（HEAD 面 `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`，条目格式 `- ruling_id: '裁定#NNN'`）

| 裁定号 | ruling_id 精确命中 | 备注 |
|---|---|---|
| #413 | 1 | L5701 起：title「GPU 点火三件套（方案②朴素重排+预注册签发+提前开考）+分钟/tick 口径立法」，`date: '2026-09-24'`、`status: decided`；summary 原文含"Owner 2026-09-24 晚对话连批……（对话内批准，本裁定=落正式通道）"（摘录，不作批准证据） |
| #306 / #375 / #215 / #214 / #351 / #410 | 各 1 | 均实存于 HEAD 裁定册 |

---

## 追加批次 4（清单 #1 补充 / 待裁池出处 / 收尾）

| # | 声称出处 | 命令 | 实测读数 | 态 |
|---|---|---|---|---|
| 1f | 哨兵测试件 | `ls tests/backtest/test_t1_t2_handover.py`；`git cat-file -e HEAD:...`；`git status --porcelain` | 盘上存在 14,329B（mtime 09-25 21:30），**不在 HEAD**，status=`??`（未跟踪）；哨兵 L15/L22 的 `[TESTS]` 声明指向它 | 不（测试件与实现件同处未落地） |
| 7f | 待裁池 ①~⑧ 原文出处 | `sed -n '88,90p' docs/_working/decision_map_campaign_20260924/HANDOVER.md` | §五 原文一行列全八项：`1. t0 甲位（三版本分叉待确认）2. 清道三袋 ARCH 议题注册 3. L09-C01 编排器收拢 4. emoreplay 交接确认 5. 方案① prereg 重签（红蓝达标触发）6. AI 层批文 7. 修宪入口 8. DU-07 consensus 补齐已批待执行`（**注**：本清单第 6、7 两项在本次任务书中被换成"时帽 12h 口径"与"EV-02~06 治本"，二者实为 LEDGER §五·补 R-1 与 N-4/AUTO §七 的登记项，出处不同） | 实（出处已锚定） |
| 12-⑥b | AI 层批文（HANDOVER 原第 6 项） | `ls`+`git cat-file` `docs/_working/ai_layer_vision/P1_full_construction_inventory.md` | 在 HEAD（盘 6,462B，mtime 09-25 00:30）；L92 原文 `⏸ 待 Owner：12 项（全部登记在夜报待批 11 项+R2 增项，禁代裁）`——**"12 项"至今只能枚举到 11+增项**（ADJ_ai_layer_gate_rearm.md §2.4 亦自述"实测枚举结果=只能枚举 11"） | 实（未批，登记态） |
| 12-⑧b | DU-07（HANDOVER 原第 8 项） | `grep -rn consensus_daily_value_cols_pit_broken docs/` | 在册 3 处：`decision_map_campaign/12_data_universe_census.md:160/209`（`known_data_gaps ... （open）`）、`archive/2026-09/dataqa_audit/gaps_registry_review.md:62`、`data_fix_campaign/p3_sentinel_registry_report_report` 同名件 :78；两处均记 **`open` 维持**，repaired 表 **2022-2025 仍 0 行**（1,563,996 行=2017-2021+2026 近窗）。`_registry/catalogs/*.yaml`、`config/` 内该键命中 **0**。17 号文 :56 立线要求"补齐或 Owner 明确不补（二选一，禁悬置）"。**未做 CH 直读复核**（避动生产库），以在册文档口径为准 | 实（未补，仍 open） |
| 4g | 战役根文档在 HEAD 否 | `git cat-file -e HEAD:.../HANDOVER.md`、`19_gpu_plan_and_master_backlog.md` | 两件均在 HEAD（由 `b3e308271d` 落地）；`docs/_working/decision_map_campaign/`（无日期后缀旧目录）另存同名 12 号文等件，即**两代战役目录并存** | 实 |

## 新增发现（续）

### E. T1 目录写序与"仍在写"判据

`grid_20260926-024947/` 内 4 个产物（manifest/negatives/net_returns/summary）mtime 全为 **07:47**，`handover_verdict.yaml` 与目录 mtime 为 **08:00:52**＝完赛落盘与验收裁决相隔 13 分钟，裁决后无任何新写。目录 mtime 晚于内件属哨兵写 verdict 所致，不构成"仍在跑"证据。哨兵 verdict 内 `generated_at: '2026-09-26T08:00:52+08:00'` 与该 mtime 一致。

### F. 备份护甲覆盖面实测

`D:\zephyr_t1_backup\` = 95M，两子项：`strategy_intake/`（mtime 09-26 02:49）+ `shield.log`（5,084B，mtime 09-26 **14:26**，仍在写）。LEDGER 六·补记 W5 口径为"10 分钟 robocopy 镜像 T1 产物，独立 powershell 进程，只镜像 T1 产物"。
**实测张力点（登记不裁定）**：备份侧 `strategy_intake` 目录 mtime（02:49）早于 T1 产物末次写盘（07:47）与裁决件（08:00）；`shield.log` 在 14:26 仍活动，但进程表内**无 robocopy/powershell 镜像进程可查**（本次仅查 python/pythonw，未查 powershell 面，属探针盲区）。

### G. 复杂度门复算口径细节

`_check` 的三道前置（L131-169）依次是：`is_test_exempt(f)` → own-scope 交集（`#ARCH-GATE-OWN-SCOPE-001`，外来 staged 降级 warn+审计）→ `node.lineno in added_lines` 且函数名不在 HEAD 版本（裁定#214）。
故：**新增整文件时"存量复杂度"会被全额计为新增**（LEDGER:188 自述"整文件新落=存量复杂度全算新增"与代码一致）；反之若同一文件已在 HEAD 且函数名已存在，则同样 52 复杂度的函数**不会**被拦——即"改老文件不拦、新建文件拦"是门的家法，实测复算支持该描述。聚合台 `COMPLEXITY-GUARD` 另并 `NO-GOD-CLASS`/`NO-LONG-PARAM-LIST`（LEDGER:188 提及 `build_t2_subspace` 13 参即后者面）。

## 无法判定 / 缺口

1. **"114 测试绿"未整体验**：本次只点名单文件跑（37 passed）。10 套件 114 例的构成未在 LEDGER/commit 中逐一点名，无清单可复算；若要终审需点名 10 件（可从 `62898892ed` 的 4 个测试件 + `tests/backtest/test_t1_t2_handover.py` 起步）。
2. **"单格 58s→10.5s（5.6x）/ 35.33s→~5s" 无实测件**：未在盘面找到计时台账（`.runtime/tmp/ddup/probe_engine_equivalence.py` 存在，是等价/计时探针脚本，其输出物未定位）。
3. **等价对拍"1 ULP max|Δ|=4.441e-16"未复算**：`EQUIVALENCE_VERDICT_T0_200.md` 在 HEAD，可作声称源；本案卷未执行 parquet 逐位对拍（清单未要求，且属重计算）。
4. **`grid_20260924-080309` 的 33% 读数是"冻结档单值 sharpe"**，非五档逐档表：manifest 列头无 cost 列（`recipe_id,prefix_key,degraded_dimensions,sharpe,ann_return,max_drawdown,avg_turnover,net_days,values_json`），17 号文度量列要求的"manifest cost 列"在**所有已跑产物中均不存在**（AUTO §七.3 亦自述 prereg 缺 `cost_gate_t1_tiers_bp` 致无 cost 列）。故"40bp 档 33% 负"实为"冻结档（`I_cost_tier=frozen_l0`）sharpe 33% 负"的转用，档位口径不可直读。
5. **powershell/robocopy 进程面未查**（F 项盲区）；GPU 侧未查 `nvidia-smi`（清单未要求，且属可能扰动面）。
6. **CH 直读零执行**：本案卷全部读数来自文件/产物/git，未向 ClickHouse 发起任何查询（含 #5 抽查原始档位的库面对账）。
7. **"做T 3/271 批"编号无实物锚**：`grep` 未在进程与产物中命中"271 批"对应件；LEDGER:13 记线 3（做T 多周期引擎）09-25 20:45 实测为"亡，links/L05_t0 无新产物（HEAD 内仅 r01-r04 卡+容量预检报告）"。

## 收尾（top 5 与交接书不符处）

1. **哨兵与其测试均未落地**：`scripts/backtest/t1_t2_handover.py` 在 index 不在 HEAD（`AM`），`tests/backtest/test_t1_t2_handover.py` 完全未跟踪（`??`）。拦它的是自家 COMPLEXITY-GUARD，实测复算 max cc=52（run_acceptance，非"52 层嵌套"，最大嵌套深度仅 5），cc>15 共 3 个函数——数值真、口径名错。
2. **"13 件待入库"已不成立**：`cmd_successor_20260925/` 盘 51 == HEAD 51，双向差集为空，仅 `LEDGER.md` 有 `MM` 未落。该目录当初经 `30505c93f6`（678 件批，标题自述四门临时禁用+emergency 通道）入 HEAD，R5  thereafter 走"历史违规跳过"；改名绕行先例在 `54622bbbf4`/`bb09a39848`。
3. **文档件数三处不符**：quant_methodology 实际 **10 件**（非 11）；gpu_rewrite 10 件（符）；战役修正面 4 commit 去重后 **69 件**（非 97）。编号号文 01~08+12 至今仍不在 HEAD（亦不在盘），N-1 缺失未补。AI 三条 gate 确已 `enabled: true`（名册 :715/:721/:727）。
4. **T1 "完赛"与"全绿"是两件事**：3,698/3,700 评完 + 2 阴格属实、垃圾三线全绿，但 verdict 自报 `all_green: false`，blocking 三项（manifest_points / dead_zero / cost_gate_spot 28/50 坏）。且 `manifest_points` 判据（==3700）与 `negatives_discipline` 判据（manifest+negatives==3700）在同文件内互相矛盾；`cost_gate_spot` 走 `source: replay` 重放腿，与 17 号文"五档全真跑"字面不同；T2 未发车（无 subspace JSON、无 claim 件、无 T2 目录）。
5. **成本门口径这次拿到了可复算底座**（与"不可复算"担忧相反）：33% = `grid_20260924-080309/manifest.csv` 内 66/200 sharpe≤0、min −4.7830，逐位吻合案卷引用；56% = verdict 内 28/50。但**所有已跑产物均无 17 号文要求的 manifest cost 列**，档位归属只能靠重放件读。两阴格死因为 `insufficient_net:1622`，而哨兵把"dropna<60"与"std==0"两分支合并打印 `len(net)`（=全窗 1622），**零方差结论不可直读**；"同配方旧引擎同死"无同窗对拍件（旧引擎 T0 两跑各 200 格不含该两格；仅 09-15 旧窗现场评出 sharpe=-0.153 存活负值）。
6. 另计一项：**引擎去重改造本身是真的**（`62898892ed` 验真且为 HEAD 祖先，三源件 disk==HEAD 零 diff；等价书在 HEAD；点名测试单文件 37 passed），但"原 628 行"在盘面无对应读数锚。冻结件 `search_space_prereg.yaml`/`exam_scale_cost_gate.yaml` 近两夜零改动（最近分别 09-24 21:39 `102a3748fa`/裁定#413 与 `294b4d24fe`）。待裁池 8 条：prereg 未重签、L09-C01 未注册、时帽键零消费点、ARCH 议题不存在、EV-06 自述未落地、DU-07 仍 open、AI 批文仍 ⏸、修宪仅在 backlog 面。

## 附：三条 gate 的真源定位（清单 #4 "读 config/flags.yaml 与门册"补测）

- `config/flags.yaml`（8,459B，mtime 09-26 02:31）内**无** `REAL-KEY-REFERENCE-SCAN`/`TASK-ORDER-DOCS-LOCK`/`CONSTITUTION-LINE-LIMIT` 任一键（该文件只挂 `gate_result_cache`/`gate_preflight`/`gate_precommit_run`/`commit_queue_interactive` 等提交通道旗；`: false` 位共 8 处，均在其它域：jsonl_export/immutable_tree/enabled/auto_escalation/strict_mode/dlq_enabled/blind_test_mode/constitution_auto_approve）。
- 主门册 `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml` 内对这三条 `gate_id:` **命中 0**。
- 唯一真源＝`docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`（`enabled: true` 三条，:715/:721/:727）。
- 该册 `R5-DIGIT-SUFFIX` 条目 :142-148 亦 `enabled: true`。
