---
ttl: task_bound
---

# LANE-PIT 案卷：tick 面闭卷闸 + t0 族 DSR 分母

车道：LANE-PIT（统计完整性修复）；总筹会话 st-qmine-20260925；本文只出案卷不出裁定，
需裁事项已在文末「交总筹裁」列明（引用形式=「总筹裁 Z-xx」）。
两件都是会静默污染成绩单可信度的实缺陷，未扩面。

## 0. 能力反查留痕（写第一行业务代码之前）

- Grep `enforce_closed_book` / `closed_book|CLOSED_BOOK`：定义真源
  = `scripts/backtest/t0_material_line.py:338`（消费方 t0_rule_engine /
  t0_state_match_matrix / t0_ceiling_capacity_exam / t0_gpu_condition_pack /
  t0_six_phase_materialize / wo004 / wo008 / reexam_cpcv_harness，共 9 件，全在
  日线/分钟面与治理件，**tick 读口零消费**）。
- Grep `tick_data` 于 `src/zephyr/**`（34 件）+ `scripts/**`：研究/回测实际读口=2 个
  （下节），其余为写入/派生/运维面。
- Grep `HOLDOUT|closed_book_cutoff|2025-09-09`：切点字面量在仓内散落 8+ 处
  （t0_material_line、t0_state_match_matrix、t0_ceiling_capacity_exam、
  t0_gpu_condition_pack、t0_six_phase_materialize、condition_package._CLOSED_BOOK_END、
  reexam/a06/panels.PIT_CUTOFF_DEFAULT、ibt W_HOLDOUT），
  **src 侧无单一可导入常数**；唯一可派生真源链=
  `docs/01_policies_and_standards/_registry/catalogs/validation_method_registry.yaml`
  `discipline.holdout_months: 12`（PB-08）+
  `zephyr.trading.validation.runner.ValidationConfig.finalized_at`（定稿锚点 D）+
  `runner.holdout_cutoff()`。派生值与分钟面实现同点，两处真源互证。
- Grep `n_trial|DSR|deflated` 于 src/scripts：分母真源=
  `zephyr.backtest.core.n_trial_ledger`（MOD-BT-200），判据真源=
  `config/search_space_prereg.yaml` e7_defense.dsr_denominator（"n_trial_ledger
  cumulative_trials 累计可审计口径"）+ 17 号文 §一。
- 内收结论：件一**不新建切点常数**（走派生），闸件本体新建为唯一必要新件；
  件二**不新建登记面**（扩既有 TrialLedger 自动发现面，复用 batch_records 形制）。

## 1. 件一：tick 面缺闭卷闸 —— 确认缺陷 + 已修 + 红绿双证

### 1.1 现状核实（确认无闸）

研究/回测的 tick 读取实际只有两个统一读口，二者读库前都只做 interval 校验：

- `src/zephyr/backtest/implementations/ch_tick_replay.py::fetch_historical`
  （TickReplayEngine / event_driven_engine 的 CH 替身，1 档降级）；
- `src/zephyr/governance/data_governance/ch_tick_provider.py::ChTickProvider.fetch_historical`
  （`scripts/run_backtest.py --mode tick` 与
  `zephyr.pf_core.strategy_engine.strategy_runner.run_tick_backtest` 的注入 provider）。

分钟/日线面早已有硬拦（`t0_material_line.enforce_closed_book(start,end)`：
`end > CLOSED_BOOK_CUTOFF` 即 SystemExit），tick 侧对应物=零。
DatabaseService 侧未见 tick 研究读法（tick 走 ClickHouse 客户端，日线/分钟研究件走
`get_registry().table(...)` + 显式窗参），故统一读口收敛在上述两处即覆盖实际路径。

边界（有意不为，非漏）：数据生产链（`zephyr.data.tick_subscriber` /
`wal_writer` / `implementations/ch_auction_derive` / `ch_tick_kline` /
`daban_board_event_deriver` / `sqlite_fallback` / `scripts/ch/*` / 仪表盘运维计数
`api_server`）必须能读切点后——闭卷保密区本身就是这条链造出来的，给它们加闸=自毁考卷。
本闸只落在「读进来就会进判据」的研究/回测读口。

### 1.2 修法

新件 `src/zephyr/backtest/core/closed_book_gate.py`（MOD-BT-201，草案级）：

- `closed_book_cutoff()`：派生切点（纪律册 holdout_months + finalized_at 锚点 +
  runner.holdout_cutoff），真源缺位/非法 → `ClosedBookConfigError`（宁拒不清，
  禁静默放宽为「全窗可读」）；本件源码内禁出现字面量切点（有测试钉住）。
- `enforce_closed_book_read(start, end, surface=..., exam_ticket=..., audit_path=...)`：
  研究态（exam_ticket=None）`end > cutoff` → `ClosedBookViolation`，且**在查库之前**
  （测试断言 execute 调用次数=0）；比较口径与既有实现同规（切点当日放行）。
  闭卷考试态：必须显式非空白 `exam_ticket`，放行同时 CAS 追加一行审计
  （工单/读口/窗口/切点/UTC 时刻）到
  `data/backtest_artifacts/closed_book_exam_audit.jsonl`；裸 flag 不给工单=同样拒
  （无审计痕迹的考试等于泄露口子）。
- 两个读口各加带默认值的关键字参数 `exam_ticket/audit_path`（旧调用零改动，
  duck-typed 契约不破），并在 interval 校验之后、构造 SQL 之前调用闸。
- 连带如实修的旧文档缺陷：`scripts/run_backtest.py` 用法示例原为
  `--start 2026-05-01 --end 2026-08-31`（tick 模式=直接踩闭卷区），已改到研究语料段并留注。
- 受影响既有测试：`tests/zephyr/backtest/test_ch_tick_replay.py` 原窗 2026-09-08
  （加闸后正确地被拦，实测 4 条红），已把窗移入切点前研究段=语义修正而非放宽。

### 1.3 证尺（红绿双证，逐条实跑）

红证一（旧代码上「读切点后静默成功」，`.runtime/tmp/pit_lane/probe_leak_pre_fix.py`，
CH 交互全 mock，未触生产库）：

```text
A ch_tick_replay.fetch_historical 切点后窗 -> rows=1 cols=30 报错=无 SQL次数=1
B ChTickProvider.fetch_historical 切点后窗 -> rows=2 cols=31 报错=无 SQL次数=2
```

同一探针在加闸后重跑（反向自证，读的是同一行调用代码）：

```text
zephyr.backtest.core.closed_book_gate.ClosedBookViolation: FAIL: 读取窗终点 2026-09-08
越闭卷切点 2025-09-09（读口=ch_tick_replay）——禁闭卷数据入研究（17 号文 §三.5 HOLDOUT 纪律）
```

红证二（新测试在未加闸代码上跑：`python -m pytest tests/backtest/test_closed_book_tick_gate.py -q`）：

```text
11 failed in 26.70s
```

如实标注该红的成分：11 条全部死在 `ModuleNotFoundError: zephyr.backtest.core.closed_book_gate`
（闸件不存在，测试首步即取不到异常类），因此**这条只证「无件」不证「无拦」**；
「旧代码读切点后静默成功、零报错」由红证一（探针，走到 SQL 并返回行）承担。
两证合看才成立，单看红证二会高估其信息量——件二不存在这个问题
（其红是 `assert 100 == (100 + 280)` 的口径级红，直接证漏计）。

绿证（加闸后，同一命令 + 受影响既有测试）：

```text
tests/backtest/test_closed_book_tick_gate.py ...........        11 passed
tests/zephyr/backtest/test_ch_tick_replay.py .....               5 passed
tests/backtest/test_tick_replay_data_handler.py .......          7 passed
tests/pf_core/test_strategy_runner_tick.py .......               7 passed
tests/backtest/test_event_driven_engine.py ...                   3 passed
```

覆盖：切点派生（含「源码禁字面量」自证）/真源缺位 fail-closed/两读口研究态拦截且不触库/
考试态放行+落审计/缺工单拒/切点当日边界放行/次日拦/在窗内正常读。

## 2. 件二：t0 族试验数不入 DSR 分母 —— 确认遗漏 + 已补分母 + 红绿双证

### 2.1 扫描面核实

在册扫描面（`zephyr.backtest.core.n_trial_ledger`）三条来源：
`screen_runs`（c1_backtest.strategy_screen 的 is_sharpe 非空行，SQL 自动同步）、
`batch_records`（自动发现 `data/strategy_intake/grid_*/summary.json` +
显式 `record_run`）、`manual_population`（只入 known_floor 披露，永不入 count）。
做T（t0）族三类都不沾：规则引擎对集在
`data/backtest_artifacts/t0_rule_engine/t0_rule_manifest_<tag>.yaml`，
状态匹配矩阵在 `docs/_working/.../L05_t0/`。

### 2.2 遗漏还是刻意？（凭据，不猜）

判定=**分母漏计属遗漏**，但仓内确有一条**方向相反的刻意纪律**，两者不冲突：

- `links/L05_t0/SKEL.md:193` 与 `links/L05_t0/t0_state_match_readme.md:52`：
  做T 产物「禁落 summary.json」，理由明写 "n_trial_ledger glob grid_*/summary.json
  计 DSR 分母=科学污染，src/zephyr/backtest/core/n_trial_ledger.py:421"——
  这条禁的是**把 GPU 输入包（非试验）喂给 glob 造成虚增**，不是「t0 试验不该入账」。
- `links/L05_t0/state_match_downstream_surface/MINE.md:33,73,83`（L05-DS-G3）：
  把「做T 族不入 DSR/PBO 分母」记为**新矿**（"本矿新矿，非在册"）、
  归类「新登 LK 类（科学记账）」，并明确 "两头都要显式声明，禁靠 glob 侧碰运气"。
  其挂起条件是「与 L05-C14 搜索空间裁定同窗处理（否则 n_trials 与预算双改互相污染）」，
  不是「t0 永久豁免分母」。
- 账本自身口径（`trial_ledger_registry.yaml` counting_rule + 模块头注）=
  「只算可审计的机器回测次数」。t0 规则引擎每批在 manifest 里逐批登记 n_symbols，
  出生证可复核 ⇒ 满足入账边界。

结论：无任何登记凭据主张「t0 试验排除于分母」；在册凭据反而一致指向应入账。
故按「补分母、阈值一字不动」处置，不开 summary.json 侧门（守住上一条刻意纪律）。

### 2.3 修法

`n_trial_ledger.py` 扩既有自动发现面（不新建登记件）：

- 新纯函数 `discover_t0_rule_engine_batches(root=None)`：吃
  `t0_rule_manifest_*.yaml`，一格=一次机器回测，
  `n_trials = Σ_{batches_done} n_symbols × len(rules) × len(periods)`；
  **只认 batches_done 实跑批**（`created_batch_run` 是计划数，禁充数=禁虚增），
  单批缺 `n_symbols` 跳过该批并告警（不猜补值），非 manifest 命名产物不计。
- `sync_screen_counts(..., t0_root=None)` 把发现结果并入既有 batch_records 登记通路
  （kind=`t0_rule_engine`，note=manifest 出生证仓内路径），返回体加 `t0_added`；
  幂等沿用既有 batch_id 唯一跳过逻辑。
- 阈值/判据面零改动（本卷实测在册线：`DSR_SIGNIFICANCE_THRESHOLD=0.95`、
  `DSR_OVERFITTING_FLOOR=0.5`、`promotion_combo_gate.THRESHOLDS["dsr_min"]=0.0`、
  搜索空间封顶 grid_points_cap 等，全部未触碰；新测试里显式钉住 0.5 一条防手滑）。
- 连带修的测试卫生缺陷：`tests/backtest/test_n_trial_ledger.py` 4 个 sync 用例（5 处调用）
  原只钉 `grid_root`，新增发现面后会被生产在飞 t0 manifest 污染（实测多出 +300 假账），
  已逐处显式钉 `t0_root=tmp_path/"_no_t0"`。教训入卷：**多一个自动发现面就必须多钉一个入参**。

### 2.4 后果如实披露（补分母→历史 DSR 全部变小=更严）

当前在册读数与纳入后的增量（只读探针 `TrialLedger().snapshot()` +
`discover_t0_rule_engine_batches()`，未写生产账本）：

```text
在册 n_trials_raw = 20632（screen_runs 269 + batch_records 8 条 20363）
t0 待登记         = 300（t0_rule_engine_r01_grid100bp_full_v1，实跑 3 批 × 20 标的 × 1 规则 × 5 周期）
新分母            = 20932（×1.015）
该 manifest 计划 271 批 → 全量跑完 t0 单批族 ≈ 27,100 → 分母 ≈ 47,732（×2.31）
```

要点：现在增量小只因为做T 全量跑在飞（3/271 批）；跑完即分母翻倍量级。
账本不落第二次 sync 就永远停在 300——所以**再 sync 是本件的落地动作**（见 §4），
而落地时机须与 L05 全量跑收尾同窗，否则分母停在半程（偏松）而非终值（偏严）。

受影响结论清单（要重算/重出的面，按类给数，禁凭记忆）：

| 类 | 面 | 条数 | 重算入口 |
|---|---|---|---|
| 1 | run 档案 summary.json 含 dsr/deflated 字段 | 34 | `python scripts/backtest/dsr_recalc_backfill.py`（A3 存量重算件，正是为这件事存在） |
| 2 | 网格候选/存活名单 CSV（f06_survivors.csv、grid_20260916-123551/dual_dsr_candidates.csv） | 2 | 同上重算后由 `c4_batch_screen.py` 重出 |
| 3 | 台账表 `c1_backtest.strategy_screen` 逐行 DSR 列（is_sharpe 非空 269 行在册） | 269 行 | `dsr_recalc_backfill.py` 写回；判据行留 n_trials_source |
| 4 | 自动管线消费件（下次跑即自动收紧，无需改码）：`c4_batch_screen.py`、`dsr_recalc_backfill.py`、`decision_gate.py`（三线裁决 0.95/0.5）、`promotion_combo_gate.py`（dsr>0 钱闸）、`strategy_validation_pipeline.py`、`metrics.calculate_full_metrics`、`fw_backtest.py`、两引擎 `vectorized_engine`/`event_driven_engine` | 9 件 | 复跑 |
| 5 | 本战役案卷内引用 DSR 结论的 md（需在下轮引用处标注「旧分母口径」） | 20 篇（`grep -rl "DSR\|deflated_sharpe" docs/_working/decision_map_campaign_20260924 --include=*.md`） | 人工复核，不自动改 |
| 6 | 晋级/钱闸历史判定：凡按旧 20632 分母出过 DSR 且 0.95>DSR_new 的候选，其「通过」结论待重算（新分母下 DSR 单调变小，故只可能从通过变不通过，不可能反向） | 待类 1/3 重算后回填 | — |

（类 5 的 20 篇含本文与 L05 采矿卷，实际需改判的以数值结论所在卷为准；此处给可复现口径不写死名单。）

未纳入并如实声明的 t0 侧相邻面：`state_match_matrix` 的格点统计=同一批 pairs 的再聚合
（再计=双重计数，禁），`material_precapacity_sample20_stats.yaml`（在 docs/_working
工作区、20 标的×5 周期的 M0 预容量样本，与 r01 全量同模型同面，计了会重复），
`t0_gpu_condition_pack`（输入包，非试验——正是上一条刻意纪律保护的对象）。
因此 t0 侧入账数仍是**下界**，与账本 known_floor 语义一致。

### 2.5 证尺（红绿双证）

红证（未纳 t0 的旧代码，`python -m pytest tests/backtest/test_n_trial_ledger_t0_family.py -q`）：

```text
FAILED test_t0_family_enters_cumulative_denominator
  assert 100 == (100 + 280)      # t0 族 280 次机器回测不在分母
FAILED test_t0_registration_is_idempotent            assert 0 == 2
FAILED test_partial_run_counts_only_completed_batches  KeyError: 'batch:t0_rule_engine_x'
FAILED test_t0_inclusion_lowers_dsr_for_same_trial   assert 100 > 100   # 补分母前后同数 ⇒ DSR 不可能变小
4 failed, 3 passed in 3.18s
```

绿证（补分母后，同一命令 + 既有账本测试 + 相邻消费面）：

```text
tests/backtest/test_n_trial_ledger.py .....................             21 passed
tests/backtest/test_n_trial_ledger_t0_family.py .......                  7 passed
tests/backtest/test_closed_book_tick_gate.py ...........                11 passed
tests/backtest/test_c4_deflated_sharpe_runner.py ........                8 passed
```

单调性钉法（7 条之 2 条）：
`test_dsr_monotone_nonincreasing_in_n_trials` 对 n∈{10,100,1k,10k,100k} 扫 DSR，
断言非增且首尾严格变小；`test_t0_inclusion_lowers_dsr_for_same_trial` 用同一净值序列、
同一账本真源，仅差 t0 发现面，断言 `n_trials` 严格变大且 `dsr` 严格变小，
并钉 `DSR_OVERFITTING_FLOOR==0.5`（阈值未随本件动）。测试全 `tmp_path` 注入，
零写生产 `data/`，零触在飞 CH 库。

## 3. 净零与内收声明

本车道真实改动面（`git diff --stat HEAD` + untracked 核对，只核不提交）：

```text
 M scripts/run_backtest.py                              |   4 +-   （仅示例窗注释）
 M src/zephyr/backtest/core/n_trial_ledger.py           | 100 ++-   （发现面 + 头注）
 M src/zephyr/backtest/implementations/ch_tick_replay.py |  18 ++-
 M src/zephyr/governance/data_governance/ch_tick_provider.py | 20 ++-
 M tests/backtest/test_n_trial_ledger.py                 |  10 +--  （hermetic 钉参）
 M tests/zephyr/backtest/test_ch_tick_replay.py          |   8 +-   （窗移入研究段）
 ?? src/zephyr/backtest/core/closed_book_gate.py         （新逻辑件）
 ?? tests/backtest/test_closed_book_tick_gate.py        （新证尺件）
 ?? tests/backtest/test_n_trial_ledger_t0_family.py     （新证尺件）
 ?? docs/_working/.../PIT_closed_book_and_dsr.md + landing/lane_pit.yaml
```

（同窗另有 `docs/_working/fullflow_mining/…`、`links/L05_t0/news_dimension_pit/`、
`tests/backtest/test_c4_pit_red_injection.py` 等他人条目在主区，本车道未触碰、未纳入待落清单。）

- 新建件 3 个：`src/zephyr/backtest/core/closed_book_gate.py`（唯一新逻辑件）、
  `tests/backtest/test_closed_book_tick_gate.py`、
  `tests/backtest/test_n_trial_ledger_t0_family.py`。
- 规则/gate/注册表/配置册新增=0（分母口径、闭卷判据全部复用既有真源）；
  切点常数新增=0（派生）；登记面新增=0（扩 batch_records）。
- 合并替代关系：`closed_book_gate` 是 tick 面的闭卷执行口，与
  `t0_material_line.enforce_closed_book`（分钟面 CLI 参数级拦口）**不同对象不并**——
  后者拦「命令行传错窗」，前者拦「任何读口取到闭卷数据」；两者共用同一派生切点。
  登记为后续收敛候选（scripts 侧那 8 处字面量切点宜改为派生，属另一车道面，本卷不扩面）。
- 无文件改名，无 depgraph 重建义务（但登记依赖仍需按 §4 走）。

## 4. 交总筹裁 / 待落清单

待落清单已出：`docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/landing/lane_pit.yaml`。

需裁三件（本车道不自行处置）：

1. 做T 全量跑（r01，271 批）收尾后何时再跑一次 `sync_screen_counts()` 落终值分母
   （早落=停在 300 偏松，晚落=已按半程分母出过结论）。建议与 L05-C14 搜索空间裁定同窗。
2. `t0_material_line` 等 scripts 侧 8 处切点字面量是否统一改吃
   `closed_book_gate.closed_book_cutoff()`（跨车道面）。
3. 类 6 重算后若出现「此前通过、现不通过」的晋级件，走哪条复核程序（钱闸历史判定回滚面）。

已知遗留（非本车道缺陷，登记不修）：`TrialLedger._cas_update` 重试时
`state["added"]` 列表会累加重复（返回体噪声，不影响账本内容幂等）；
`sync_screen_counts` 无 `t0_root` 参数时读生产面（设计上如此，测试必须显式钉参，
已在本卷把 4 个既有用例补齐）。

## 5. 复核命令（逐目录、显式路径，禁全量套件）

邻域合批实测（本车道终态，一次跑完 8 件）：

```text
python -m pytest tests/backtest/test_closed_book_tick_gate.py \
  tests/backtest/test_n_trial_ledger_t0_family.py \
  tests/backtest/test_n_trial_ledger.py \
  tests/zephyr/backtest/test_ch_tick_replay.py \
  tests/backtest/test_tick_replay_data_handler.py \
  tests/pf_core/test_strategy_runner_tick.py \
  tests/backtest/test_event_driven_engine.py \
  tests/backtest/test_c4_deflated_sharpe_runner.py -q
=> 69 passed in 6.03s

DSR 消费侧回归（分母面改动的连坐检查，全绿）：

```text
python -m pytest tests/backtest/test_metrics.py tests/backtest/test_metrics_dsr.py \
  tests/backtest/test_decision_gate.py tests/backtest/test_overfitting_adjudicator.py \
  tests/backtest/test_layered_validation_pipeline.py -q
=> 160 passed in 6.71s
```
```

红证复现（**禁在本区 git stash/checkout**——主区 index 是多会话混合池，动它=连坐他人成果；
本车道红证是在补丁写入之前实跑捕获的，非事后用 git 回滚制造）：

1. 先落两件测试件（未碰实现）→ 跑 → 记 §1.3 红证二 / §2.5 红证 → 再落实现 → 跑 → 绿。
2. 免回滚的红证通道=探针脚本 `.runtime/tmp/pit_lane/probe_leak_pre_fix.py`：
   它调的是被闸保护的同两行读口，旧代码上打印「rows=N 报错=无 SQL次数≥1」，
   新代码上抛 ClosedBookViolation——同一命令双向可读，不需要动 git。
3. 若要在新代码上复核「旧行为」，走闸自带的考试态（`exam_ticket="EXAM-REPRO-<sid>"`
   + `audit_path=<tmp>`）即可看到放行路径，同时留审计，禁绕过闸。


