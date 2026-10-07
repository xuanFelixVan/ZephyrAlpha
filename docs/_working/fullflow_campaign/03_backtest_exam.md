---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# S3 回测与考试环节簿

> 战役: fullflow_20261008 ｜ 段: S3 回测与考试 ｜ 挖矿代理: B ｜ 日期: 2026-10-08
> 范围: config/search_space_prereg*.yaml + exam_scale_cost_gate.yaml（预注册冻结考卷）→ scripts/backtest/（88 件入口/引擎面）→ src/zephyr/backtest/（引擎域）+ src/zephyr/factor/analysis/layered_backtest.py → 计划任务自动化面（C4Exam/F06Grid/ModelExam）→ GPU 路由面（gpu_core/schedule_gate/gpu_survey）→ tests/backtest/（规模清点）
> 纪律: 只读调研 + `--help` 实测 + import 冒烟；未开正式考、未跑网格、未占 GPU、未写生产数据。**特别声明**：`sector_prereg_exam_runner.py` 无 `--help` 守卫，实测 `--help` 即触发全量板块预注册考试并改写 `docs/_working/sector_line/exam/prereg_exam_results_v1.yaml`——已当场 `git checkout` 还原至 HEAD（diff 核对=纯本次误触输出，无他会话内容损失），并在缺口面登记 [红]。

## 一、输入面

| 输入物 | 真源路径 | 实测状态/说明 |
|---|---|---|
| 预注册主册（E7 GPU 三路） | `config/search_space_prereg.yaml`（schema 2.0.0，83 行） | **frozen_at=2026-09-24T22:00:00+08:00，frozen_by=裁定#413，owner_signoff=裁定#413**（对话批"全部同意+现在就考试"）；目标函数=cost_adjusted_sharpe；三轨 f06_grid/e1c/llm_agent 全 enabled；T0 标定 200/T1 3700/T2 900，grid_points_cap=25000，wall_clock 59h；cost_gate_in_every_tier=true（任何阶段禁跳成本门） |
| T3a 开闸考冻结卡 | `config/search_space_prereg_t3a.yaml`（98 行） | frozen_at=2026-10-05T00:00:00+08:00，frozen_by=总包工单T3a（Owner 常设授权），**owner_ruling_id=null（回填位空）**；考卷=J_regime_switch 双腿×all_a_ex_st 域，n_raw_expected=725,760（G 过滤后 241,920），IS 窗 2020-01-01..2023-12-31，seed=20260915；防御腿 registered=true/**enabled=false**（D114 休眠铁律，Owner 门位） |
| T3b 加离场考冻结卡 | `config/search_space_prereg_t3b.yaml`（93 行） | frozen_at=2026-10-07T11:00:00+08:00，frozen_by=Owner chat 批令（2026-10-07"批"），owner_ruling_id=null；新增 X_stop(3档)×X_breaker(2档) 离场轴（phase>=3 门控），n_raw_expected=4,354,560，overlay_order 序钉=[J_regime_caps, X_stop, X_breaker]；新判据 exit_gain（5pp 沿 T3a 同款门值语义） |
| 图形共振预注册卡 | `config/chart_resonance_prereg.yaml`（91 行） | frozen_at=2026-10-07T05:30:00+08:00，**status=READY_NOT_FIRED（禁点火）**，正式跑推迟波 12 G-D.4 Owner 门位；纪律首行=图形信号只作条件轴禁作独立信号（Marshall 2006 证伪基线）；消费 grid_stats_engine 的 SPA/StepM |
| 成本门参数面 | `config/exam_scale_cost_gate.yaml`（107 行） | v1 冻结：五档滑点 tiers_bp=[0,5,10,20,40]、survival_floor=0、单调容差 1e-9、min_days=60、换手帽 8x/年、规模维 participation_ref=0.05 开方律（cap 2x）；**B 案追加块 breakeven_cost_gate v2.0.0（裁定#435，2026-09-30）**：判据对象=盈亏平衡成本 c*，声明件=docs/_working/night_sweep/c_exam/flag2_declaration_b.md |
| 考试政策（判据真源） | `docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md`（active v1.0.0，裁定#365） | 准入四条（prereg 冻结/封闭族 N_eff/沙箱三关/试验台账先行）、执行口径（执行器只可运行不可改、DSR 喂全部留痕试验）、成本双口径声明纪律、复权链断供=暂定档、负结果台账五条 |
| 工具考试考纲 | `config/tool_exam_policy.yaml`（47 行） | **status=draft 提案稿**（OBJ_T-#1 避让：未经 OBJ_R 四步流水线正式化，禁当正式考纲消费，产物带 policy_status=draft 痕）；Tier B 有限样本判据（N=5-10，±10pp，红线一票否决） |
| 条件分层输入 | `zephyr.backtest.regime_validation.condition_package` + `c1_backtest.regime_snapshot_history` | T1 分层键=emotion_grey_band×market_state_F4（实测 9 胞达标）；J 调度数据缺失=整格阴性 fail-closed |
| 因子面 | T3a 卡 exam_definition.factor_surface=v1_value | v1 三因子+f_ep/f_bp/f_np_yoy；exec_caliber=close（T3a 主判据冻结收盘口径） |
| 考试对象名单 | strategy/factor/technical_indicator 三注册表 + 分配器 5 套（`docs/01_policies_and_standards/_registry/catalogs/`） | fexam roster 批0 机生（零手工挑题；prereg 窗口/及格线在 roster 模块冻结，考试器禁改） |
| 数据面 | CH 健康表（kline_daily_hfq/kline_index/kline_etf_daily/stk_limit/index_constituent/stock_basic），经 DatabaseService | 引擎成本=冻结土规（佣金 2.5bp 双边+印花 10bp 卖+滑点 5bp，_c4_engine COMMISSION_BP/STAMP_BP 常量钉死）；涨跌停可成交性闸默认开 |
| N 账本（试验台账） | `docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml`（TrialLedger CAS 更新） | DSR 分母=累计可审计口径（裁定#306）；每次尝试必经 record_run（e7_defense.ledger_required=true） |

## 二、输出面

| 输出物 | 形态 | 下游/消费者 |
|---|---|---|
| 网格产物出生证 | `data/strategy_intake/grid_<run_ts>/`：manifest.csv + negatives.csv + summary.json + net_returns.parquet | 现存 **57 个 grid run 目录**（含分片 _s0of3/_s1of3/_s2of3 与 grid_t0_conditional_v1/grid_gpu_sectorcond_20260924-0834）；factory_grid_anova/E2 四车道消费 |
| 阴性库 | negatives.csv（gate 层死/eval 死/调度缺失整格阴性，逐行 fail-closed 落盘禁崩批丢证据） | 负结果台账（exam_policy §5）；prereg 主册 negative_result_promise：禁删改 |
| 试验次数账本 | trial_ledger_registry.yaml（screen_runs 段，cumulative_trials 口径） | Deflated Sharpe 校正原料（缺原料=结论降级）；c4_batch_screen/factory_grid_executor 均接线 |
| C4 双窗台账 | 冻结 IS 批 + oos_tested 行（幂等键=batch/strategy_id/verdict/source_file）；c4_batch_completed 事件仅由 OOS 段发射 | intake 消费（要求双窗齐备方可 promote） |
| 注册表回写 | strategy_registry/factor_registry 判定回写（走 GitCommitGateway）；复权断供期一律带"暂定档"标签 | 组队备料/晋升链（league_judge、promotion_combo_gate） |
| 考试报告 | `docs/_working/<campaign>/<lane>/` 全量 results 件（如 sector_line/exam/prereg_exam_results_v1.yaml） | 战役台账行 + 三态出口（sop_b ⑦对齐） |
| 运行日志 | `.runtime/logs/c4_exam.log`、`f06_grid.log`（append-only） | 最近证据：c4_exam.log 末行=OOS batch exit code 0（zero_pending，批 C4-translated-20260912）；f06_grid.log=09-19/09-26/10-03 三次 23:00 点火 |
| 资源采样 | `.runtime/logs/resource_samples/sch_c4_exam.jsonl` 等 | 实测 sch_c4_exam p90 时长 3 分钟、峰值内存 0.08GB（2026-10-01 样本，多为零新件快退） |

## 三、入口面（逐个：命令 + 实测绿/黄/红）

| 入口命令 | 实测 | 参数面/说明 |
|---|---|---|
| `python scripts/backtest/factory_grid_executor.py --help` | **绿** | 工厂网格总执行器（2157 行）。参数：`--smoke`(8 格联通)/`--n-samples`/`--seed`/`--start/--end`/`--stratify-dims`/`--subspace-json`/`--stage {,t0,t1,t2,t3,t3-t1,t3-t2,t3b,t3b-t1,t3b-t2}`(t0 标定 200/t1 粗扫 17100/t2 细化 13000；t3 家族=冻结册钳制，help 原文)/`--skip-compute-gate`(仅 smoke 允许)/`--engine {cpu,gpu,auto}`(L2-C 三态)/`--verify-counts`(只读对账尺，禁任何写)/`--shard-idx/--num-shards`(i::k 轮转切片，须串行=vram concurrency 1)/`--context-json`。prereg 接线：_load_prereg_caps/_apply_prereg_budget/_resolve_stage_cost_tiers/_load_t3a_exam_card/_validate_defensive_whitelist_registration 全链 fail-closed |
| `python scripts/backtest/c4_batch_screen.py --help` | **绿** | C4 快筛批测。`--limit`(冒烟)/`--dry-run`(不落库)/`--start/--end`(给 start 即 OOS 复测批)/`--batch/--verdict`/`--only`/`--auto-only`(增量 IS)/`--auto-oos-pending`(S06-G1 双窗补测)/`--defer-emit`(双窗编排事件抑制) |
| `python scripts/backtest/f06_e4_wfa_exam.py --help` | **绿** | F-06 E4 完整三阶段正考（IS→WFA→OOS）。`--recipe-id/--start/--end/--train-months/--test-months/--step-months/--oos-start/--out-dir/--survivors-csv`；exam_policy §2 钉为正考执行器（只可运行不可改） |
| `python scripts/backtest/fexam/run_fexam.py --help` | **绿** | 全量考试套件单入口，9 子命令：roster/factor/strategy/indicator/allocator/summary/inventory/metaq/**selftest**(零 DB 纯函数自证)+`--session`/`--writeback`；prereg 窗口/判据只读自 roster 禁 CLI 覆盖（防挪门柱）；EXIT 0/1/2 契约在册 |
| `python -m zephyr.intelligence.model_profiling.cli --help` | **黄** | 打印"未知命令: --help"（无 argparse）；且 CLI 仅 discover/quick/benchmark/drift/best/history 七命令，**不存在 register_model_exam_task.ps1 引用的 `exam` 子命令**（详见缺口面） |
| `python scripts/backtest/sector_prereg_exam_runner.py --help` | **红** | 无 argparse 守卫：`--help` 被当普通参数**直接开考全量板块预注册考试**（读 CH 真库 1589 日×729 板块面板）并改写 `docs/_working/sector_line/exam/prereg_exam_results_v1.yaml`。本次实测踩中，已还原 HEAD；FutureWarning×4（pct_change pad 弃用）附带实录 |
| import 冒烟（12 模块） | **绿 12/12** | zephyr.backtest / core.engine_base / core.n_trial_ledger / core.cpcv / core.walk_forward / core.closed_book_gate / core.decision_gate / gpu_core / regime_validation.exam_cost_gate / regime_validation.condition_package / services.layered_validation_pipeline / factor.analysis.layered_backtest 全部 import 成功（Python 3.12.8） |

## 四、模块面

| 簇 | 路径 | 实测规模/要点 |
|---|---|---|
| 回测引擎域 | `src/zephyr/backtest/` | core 23 件（engine_base=BacktestEngineBase/LookaheadExecutionError/结果可信度界；cpcv/purged_kfold/walk_forward；closed_book_gate 闭卷闸；pit_manager；matching_engine/matching_logic 成本段；decision_gate；n_trial_ledger；overfitting_detector/adjudicator）；regime_validation 15 件（exam_cost_gate/c4_deflated_sharpe_runner/condition_package/e2_stationary_bootstrap/e3_param_sensitivity/e4_cost_sensitivity/chart_* 族）；services 8 件（layered_validation_pipeline/scheduler 等）；accel/bootstrap_kernel.py；run_archive.py；gpu_core.py |
| 统计引擎 | `scripts/backtest/grid_stats_engine.py`（601 行） | 四件套+White(2000) RC/Hansen(2005) SPA 简版+Romano-Wolf(2005) StepM 简版+分半窗（chart_resonance 卡指定消费方） |
| 共享批测引擎 | `scripts/backtest/translated/_c4_engine.py`（1001 行，MOD-BT-039） | PIT（T 日信号用 ≤T-1 数据，T+1 收盘起算）+冻结土规成本+涨跌停可成交闸+DSR；gpu_rewrite P1 接线（ZEPHYR_COMPUTE_BACKEND，等形格点走 FP64 张量核，非 close 执行口径恒 CPU+guard_reason 披露）；批级 LRU+单趟共享（st-ddup 去重改造）；translated/ 目录共 **98 件**考卷（c4_*.py） |
| 分层回测 | `src/zephyr/factor/analysis/layered_backtest.py`（319 行） | layered_returns/compute_layer_spread/parity_grid（分箱逐位对拍）；gpu_survey 定性 B（逐日 qcut，小件顺手 GPU 化候选） |
| 成本门判定 | `src/zephyr/backtest/regime_validation/exam_cost_gate.py`（635 行） | CostGateConfig/CostGateVerdict + B 案 BreakevenGateConfig/evaluate_breakeven_cost_gate/solve_breakeven_cost_star/monotonic_grid_violations |
| N 账本 | `src/zephyr/backtest/core/n_trial_ledger.py`（652 行） | TrialLedger：load_registry(fail-closed)/cumulative_trials/record_run/set_effective_trials/set_watermark，CAS 更新+safe_write_text；T0 做T族 kind 口径（C216，2026-10-07） |
| fexam 套件簇 | `scripts/backtest/fexam/`（8 件） | roster（批0 四册名单机生）/ic_exam（fast_rank_ic/judge）/strategy_exam/allocator_shadow/campaign_report/run_fexam/ch_data/exit_sim；gpu_ic/（含 smoke_gpu.py，头部明示"今晚不执行——GPU 被 st-t3series 车道占用"）与 bootstrap_gpu/（bench+parity 对拍） |
| 联赛/晋升/复考 | `scripts/backtest/league_{judge,registry,archive,restore,monthly_snapshot}.py`、`promotion_combo_gate.py`、`exam_cost_reexam.py`、`reexam_cpcv_harness.py`、`f06_e4_wfa_exam.py` | 考后流转面（晋升门/判死归档/CPCV 复考） |
| 计划任务脚本 | `scripts/tasks/register/register_{c4_exam,f06_grid,model_exam}_task.ps1`；`scripts/tasks/run/run_{c4_exam,f06_grid}.ps1` | 注意：register_c4_exam_task.ps1 内部仍指向旧路径 `scripts\run_c4_exam.ps1`，而实际注册任务指向 `scripts\tasks\run\run_c4_exam.ps1`（登记漂移，见缺口面） |

## 五、自动化面

| 自动化 | 实测状态（schtasks/PowerShell 实查） | 编排细节 |
|---|---|---|
| ZephyrAlpha_C4Exam | **Ready**，每周六 14:00（StartBoundary 2026-10-02T14:00+08:00） | → `scripts/tasks/run/run_c4_exam.ps1` 两段式：Stage1 IS `--auto-only --defer-emit` → Stage2 OOS `--auto-oos-pending`（双窗齐备才发射 c4_batch_completed 事件供 intake 消费）；PS5.1 stderr 地雷修复在册（cmd.exe 重定向）；heavy 池 exclusive_group=[mine_vs_exam]；上游=ZephyrAlpha_FactoryLaneC（周六 10:00 挖矿，考在挖后） |
| ZephyrAlpha_F06Grid | **Ready**，每周六 23:00 | → `run_f06_grid.ps1` 顺序批 A census-extend + 批 B subspace；纪律在管线内（执行器逐批查数据可用性；summary 时自动登记 N 账本 MOD-BT-200）；与 C4Exam 同周六错峰（resource_schedule_gate 注释实证曾同 cron 14:00 相撞，现已错开） |
| ZephyrAlpha_ModelExam | **未注册**（本机实查 0 个匹配任务；C4Exam_Full0916/FactoryLaneC_Full0916 为 Disabled 遗留） | register 脚本在册但引用不存在的 `cli exam --quick` 子命令；resource_profile_registry 将 sch_model_exam/sch_model_intel_scan 标 orphaned_source"真源消失待 Owner 裁定删除" |
| 事件触发型模型考试 | `zephyr.intelligence.model_profiling.exam_trigger_scheduler`（433 行） | CLI=`scan-new-models [--dry-run]`（盘中守卫拒跑真实模式）；runtime_assembly 的 task_gate_dispatch_hook 接 dispatch 硬门但 **opt-in 默认不启用**；作为 event_model_exam_trigger 排班真源被资源注册表生成器读取 |
| 资源调度闸 | `src/zephyr/gov_enforcement/commit_gates/resource_schedule_gate.py`（928 行）+ `config/schedule_gate_policy.yaml` | 池并发/overlap 组/mem 上限/E0 交易日闸/truth drift 五查；exclusive_group 词表含 mine_vs_exam、gpu_default（GPU 单卡禁共存）；timebox_by_class_hours：**gpu=12h**（与 prereg single_job_wall_clock_cap_hours 同值）；本地 GPU 归 cpu_heavy 类（C4 双窗批测/DSR/门禁重放受闸） |
| GPU 路由面 | `src/zephyr/backtest/gpu_core.py`（503 行）+ `ZEPHYR_COMPUTE_BACKEND=gpu|cpu|auto` | resolve_backend（显式入参>env>auto）；后端显式不可用→fail-closed 降级 CPU 并记 degraded 台账（禁静默）；FP64 张量核 tensor_core+RawKernel fillability gate scan；prereg vram：物理 24GB/训练配额 18GB/concurrency=1；实测回填 0.53s/格暖态（RTX 3090，合成面）；GPU 化全景=`docs/_working/matrix_campaign/gpu_survey_v1.md`（22 行可行性矩阵：仅 #1 gpu_core+_c4_engine+factory_grid_executor 已接，#20 ml_train 钉死 CPU=Owner 门位，交易引擎 vectorized_engine 全件禁动） |

## 六、缺口面（[绿|黄|红]）

- **[红] sector_prereg_exam_runner.py 无 --help 守卫**：`--help` 即开考+改写 results yaml（本次实测触发并已还原 HEAD）。建议：argparse 化或首行 dry-run 守卫；修复属他车道（板块线），本簿只登记不代修。
- **[黄] model_exam 自动化链三重断**：任务未注册（实查 0）+ register 脚本引用不存在的 `cli exam` 子命令（cli.py 实读仅七命令）+ 资源注册表 orphaned_source 待 Owner 裁定删除。整链处休眠，无静默失败风险（fail-loud），但登记面与实况漂移。
- **[黄] 计划任务登记漂移**：register_c4_exam_task.ps1 文本指向 `scripts\run_c4_exam.ps1`（不存在），实际任务指向 `scripts\tasks\run\run_c4_exam.ps1`（存在且在跑）；resource_profile_registry 对 sch_c4_exam 标 orphaned_source 与实况矛盾（任务 Ready 且有 2026-10-01 采样）。重注册脚本若被原样执行会注册一个指向不存在文件的坏任务。
- **[黄] T3a/T3b 冻结卡 owner_ruling_id=null**：两卡均留"裁定号回填位"，T3b 已冻结窗过（2026-10-07 11:00 点火窗），回填动作未见踪影（卡内自述属允许的登记位补全）。
- **[黄] 成本门判据双轨过渡期**：exam_scale_cost_gate v1 四块冻结 + B 案 breakeven v2.0.0 追加块并存，卡内自述"T2 判定书/成绩单生成器按波次接线；接线前哨兵 t1_t2_handover.py 判据面仍走 v1 键"——双口径并存期引用结论须连口径声明（exam_policy §3 纪律，非缺陷但易踩）。
- **[绿] chart_resonance_prereg READY_NOT_FIRED**：按设计未点火（禁手滑，正式跑待波 12 Owner 门位），冻结语义同 E7 模板（diff==0）。
- **[绿] tool_exam_policy draft 避让完整**：draft_reason 在册、消费方产物带 policy_status=draft 痕、正式化路径（OBJ_R 四步流水线）已钉。
- **[绿] GPU 纪律闭环**：单卡 concurrency=1 + mine_vs_exam/gpu_default 互斥组 + gpu timebox 12h + fail-closed 降级台账 + smoke_gpu.py 头部车道占用明示；executor 分片须串行与 vram 纪律同源。
- **[绿] 主考场测试守护**：tests/backtest 实测 **12 个测试文件（顶层 5+fexam 7）、92 个测试用例（顶层 56+fexam 36）**；_c4_engine 的 MODIFY-GUARD 钉 4 个测试件（含幽灵引用自纠记录 S1-A8）。

## 七、自审闸（三态总裁定）

**总裁定：绿（主链健康可用，带 1 红 4 黄局部点名，无一阻断主考链）。**

- **绿面**：预注册冻结链完整（四卡 frozen_at/frozen_by/授权链齐全，改空间=作废重开语义统一）；入口主链 factory_grid_executor/c4_batch_screen/f06_e4_wfa_exam/run_fexam `--help` 实测全绿且参数面与冻结卡消费关系（_apply_prereg_budget 等 fail-closed 全链）对得上；引擎 import 冒烟 12/12 绿；成本门（五档+单调+换手+规模维）→ DSR（N 账本累计口径）→ SPA/StepM → 负结果台账 的判据闭环有真源、有消费者、有测试守护（92 用例）；自动化主链 C4Exam/F06Grid Ready 且有 2026-10 初运行日志证据；GPU 路由纪律全链钉死。
- **黄面**：model_exam 链休眠且登记漂移、register ps1 旧路径陷阱、T3 系裁定号回填位空、成本判据双轨过渡——均属登记/过渡期债，fail-loud 不静默。
- **红面**：仅 sector_prereg_exam_runner.py 无守卫一件（本次实证+当场还原，未丢他会话数据；修复归板块线车道）。
- **纪律自证**：本次未开正式考、未跑网格、未占 GPU、未写生产数据；`--help` 冒烟共 6 条命令，其中 sector runner 意外触发 1 次并已还原；本簿=本次唯一新增文件，另零文件改动（git status 复核仅本簿为新增）。
