---
ttl: task_bound
completes_when: 包13.1 落 HEAD——CREATE-GUARD 查功能关键词 helper 在管线内硬阻断+四条红证在册+L527 批量化百样本判据全等重放通过
---

# 包 13.1 · CREATE-GUARD 查功能关键词 · 乙道（st-p1-gate）案卷

turn_budget: 46/150（出口刷新；首版初稿=第 8 次工具调用）
verified: 见 §6（每条带可复跑命令）
assumed: 见 §0
input_set_disjoint_with: 见 §0（丙/丁/戊/己/庚 + 在途道，本道只写自身四件）
evidence_ref.cmd: 逐结论内联于 §6/§7

> Owner 原话授权范围："修 CREATE-GUARD 逻辑，从查文件名升级到查功能关键词"。
> 契约真源：`three_piece_infra/00_plan_and_ownership.md` §3 包 13.1 + §2.1 实测地基 + §2.2 净零约束 + §五 落地面纪律。

## 0. 头部四组字段

- `turn_budget:` 见文首 `turn_budget:` 行（used/allocated；frontmatter 依 §五.7 只留 ttl+completes_when）。
- `verified:`（本道亲手复现的读数，各带命令）——见 §6。
- `assumed:`（推断，未亲手复现）：
  - L527 实测 1519 runs / 19186s 的成本读数转述自总筹册 §2.1（本道未复测历史总量，仅复测单次 git grep 时延并线性外推）。
  - `CapabilityLookup.find()`  haystack 面（capability_id+description+canonical_file+module_id+aliases）读码确认于 `src/zephyr/governance/capability_lookup.py` L924-930（HEAD 3eeb935743）。
- `input_set_disjoint_with:` 丙道 st-p1b-libr（`src/zephyr/governance/audit/`、`src/zephyr/library/`、reconciler 清单行）、丁道 st-p2-cens（普查引擎/wiring_registry 生成器）、戊道 st-p3-matrix（连接矩阵/仪表盘）、己道 st-m1-leaf（mining 叶子簿）、庚道 st-m2-seal（seal_audit）、在途道 st-final-build-20260926（骨架册/波次表/total_command_closeout）。本道只写：`src/zephyr/gov_enforcement/commit_gates/create_guard.py`、`tests/gov_enforcement/` 新建件、`three_piece_infra/piece1_gate/`、`capability_overlap_gate.py` 纯注释一行（docstring 标注取代关系，不改行为）。
- `evidence_ref.cmd:` 每条结论旁注命令原文（§6/§7）。

## 1. 设计：查询面 → 复用 find() → 命中即红（终稿）

- 新 helper `_check_capability_keyword_overlap` 在 `_check` 管线的落点：
  `_run_file_registration_checks` **链尾**（creation_token → #375 warn → 字段头部 → basename 碰撞 → **查功能关键词**）。
  理由：①既有各步先后语义零改动（只在"登记全部合法"的新建 .py 上追加判重）；②无 token 文件先被既有硬阻断
  拦下，避免新尺改变既有阻断消息语义；③basename 检查已构造的 `CapabilityLookup` 实例与新尺**共享**
  （实测构造 ~73-86s/实例，双载不可接受——新增构造缝 `_build_capability_lookup()` 单点构造、两处消费）。
- 查询面（per 新建 .py）→ 探针（`_build_keyword_probes`，≤8 条，优先级 stem > 类名 > 函数名 > CJK 段 > ASCII bigram）：
  ①文件名 stem 切词（snake/camel 分词，≥2 词的 AND 查询）；②每个顶层 class/function 名同法切词；
  ③模块 docstring **首段** CJK 连续段（≥3 字，走 find() 的 `_CJK_MIN_SUBSTRING=3` 滑窗语义）；
  ④首段相邻 ASCII 词对 bigram（词长≥4 + 停用词表 `_BIGRAM_STOPWORDS` 去噪）。
  **守卫**：纯 ASCII 探针强制 ≥2 词——实测单词 `find("gate")` 命中 181/388=全库噪声（精确子串分支所致），
  单词查询一律弃投。逐探针调用既有 `CapabilityLookup.find()`（**不重写匹配器**，契约 §2.1 收编令）。
- 命中 > 0 ⇒ FAIL（阻断）；门文案逐条打印 capability_id / canonical_override（打印 find() 结果的 canonical_file
  派生面；canonical_override 是该派生的优先级 1 真源，`_entry_to_dict` L1461-1482 不暴露原始字段——诚实注记）/
  命中探针词 / 逃生标记确切字面量（§1.1）。**自引用豁免**：命中能力的 canonical 指向该新建文件本身或
  同批新建文件者不计违规（总筹预登记 canonical 的合法场景）。
- 命中 = 0 ⇒ PASS；漂移日志 = 既有审计 `.runtime/lookup_audit/<sid>.jsonl` 中 `result_count:0` 行
  （**不新建日志文件**；锚主仓，见 capability_lookup.py L109-111 LOOKUP_AUDIT_DIR=MAIN_REPO_ROOT；
  前提=session_id 可解析（gate kwargs 或 ZEPHYR_SESSION_ID 环境），无 session 时 find() 本就不写审计——
  既有行为，未改）。
- fail 语义：lookup 构造失败或 find 抛异常 ⇒ **fail-closed 阻断**（检测器失效禁放行，对标 token 检查哲学；
  语法错误/读不到的文件 fail-open，与字段头检测同语义）。

### 1.1 逃生标记 spec（本道定名）

```
# create-guard-not-dup: <一句话理由>
```

- 确切字面量：行首 `#` + 空格 + `create-guard-not-dup:` ，冒号后必须跟**非空理由**（正则
  `^#\s*create-guard-not-dup:\s*(\S.*)$` MULTILINE，常量真源=`_KEYWORD_DUP_MARKER`/`_KEYWORD_DUP_MARKER_RE`）；
  位置=该新建 .py 文件内任意注释行；作用域=**仅豁免该文件**的关键词查重命中（不豁免其余任何检测）；
  grep 审计面：`git grep -rn "create-guard-not-dup" -- "*.py"`。
- 门阻断文案内嵌该标记逐字格式 + 示例句，AI 照抄即可（红证①断言其逐字出现）。

## 2. L527 成本面批量化（CLASS-UNIQUENESS）

- 病根：`_check_class_uniqueness` 对每个新文件的每个 class 各跑一次全树 `git grep -l`（HEAD L527）。
- 治本：一次 `git grep -n -E "^class (A|B|C)\b" -- src/zephyr/` 批量取行级输出，按类名在 Python 侧归因（纯函数 `_attribute_class_grep_lines`）；非 ASCII 类名回退逐名 git grep（POSIX `\b` 与 Python `\b` 对非 ASCII 语义可能分叉，回退保判据全等）。
- 等价证明：≥100 样本重放（样本=git log --diff-filter=A 新增 .py），逐名版 vs 批量版 (文件,类名,同名文件清单) 与最终 (passed, detail) 字符串逐字节对比——结果见 §4 表。
- 另设 Windows 命令行上限护栏 `_chunk_class_names`（alternation pattern >6000 字符自动切批；CreateProcess 硬上限 32767）。本次 328 类名单批未触发（pattern 5177 字符）。
- 非 ASCII 类名走逐名 `git grep -l` 回退：本仓 328 类名 `non_ascii_names=[]` 零回退，等价性由批量路径独立自证。

## 3. 红证四条（R-5）——终态：4/4 绿跑在册，且每条自带判别力

测试文件：`tests/gov_enforcement/test_create_guard_keyword_overlap_canary.py`（新建，未改任何既有测试文件）。

| # | 判据 | 实现 | 实测 |
|---|---|---|---|
| ① | 与在册能力关键词同义的新建 .py ⇒ 门必 FAIL | 全管线 `gate.check`（tmp 仓+tmp 真源册+小型在册集注入缝 `_build_capability_lookup`）断言 passed is False 且文案含 capability_id/canonical_override=/命中词=/逃生标记字面量；另加重件 `TestRealRegistrySynonymHit` 用**真实注册表**（"capability lookup"→capability_lookup 能力）走 helper | 通过（真实册件 114.9s） |
| ② | find 结果清空 ⇒ 门放行 + 既有审计出现 result_count=0 行 | 小型在册集置 `capabilities: []`——find() 走**真实代码**自然返回 []（纯 stub find 不产审计行，故用零能力在册集等价达成契约两要件）；LOOKUP_AUDIT_DIR 重定向 tmp（测试隔离），断言 jsonl 每行 result_count==0 且 tool==capability_lookup.find | 通过 |
| ③ | 批量化前后 verdict 全等 | 读提交证据 `create_guard_batch_replay_evidence.json`（§4 重放）：n_samples≥100、old.detail 含≥1 真实违规、(passed,detail) 逐字节全等、纯函数 `_attribute_class_grep_lines` 对存储原始 -n 输出复算 per-name 归因 == 逐名 -l 清单（≥100 类名）、新 grep 调用数 < 旧 | 通过 + 另加 tmp 小仓正向对照（真实撞名必红） |
| ④ | 人为清空命中集 ⇒ ①的断言必红（判别力自证） | 与①同构 fixture，把注入 lookup 的 find 清污为 []：先断言门放行（红与命中集因果绑定），再 `pytest.raises(AssertionError)` 复跑①同款断言强制变红；不红则本测试翻红 | 通过 |

- 附带：逃生标记端到端豁免件（标记入文件→①场景翻绿）、lookup=None fail-closed 件。
- 回归共存面实测：`tests/governance/commit_gates/test_create_guard.py` 31 passed（不改动）；
  `tests/governance/commit_gates/` 全目录 **2601 passed**；`tests/gov_enforcement/` 全目录 **58 passed, 1 deselected**（慢件单跑通过）。
  复跑命令：`python -m pytest tests/gov_enforcement/ tests/governance/commit_gates/ -q -k "not RealRegistry"`。
- 诚实申报：无任何阈值/断言/skip/xfail 被修改使绿；①②④的小型在册集是**注入缝替身**，真实在册面由重件
  `TestRealRegistrySynonymHit` 独立覆盖；无未达项。

## 4. 百样本重放表（CLASS-UNIQUENESS 批量化判据全等）

样本口径：`git log --diff-filter=A --name-only -- src/zephyr`（HEAD `3eeb935743`）中
现存且含类定义的真实新增 .py，取 120 个（≥100）；每样本按其取证面类名集
（AST 全量 ClassDef，剔除 `# class-name-alias` 豁免），逐样本对比逐名版 vs 批量版
`(passed, detail)` **整串逐字节全等**（verdict=对全 120 样本一次性调用的整体判定，
非逐行独立，故“IDENTICAL”=该样本纳入整批后总判定与逐名版全等）。

- 汇总：`verdict_byte_equal=True` / `attribution_mismatch=[]` /
  真实同名违规 6 条（下批 ★viol 样本）。
- 证据文件（可复算，pytest 红证③直接读取）：`tests/gov_enforcement/create_guard_batch_replay_evidence.json`
- 复跑：`python tests/gov_enforcement/create_guard_batch_replay.py`

### 6 条真实违规（批量版与逐名版逐字一致）

| 新建文件 | 撞名 class |
|---|---|
| src/zephyr/ex_sor/risk_redline.py | Action |
| src/zephyr/infra_runtime/runtime_admission.py | AdmissionResult |
| src/zephyr/backtest/core/cost_attribution.py | CostAttribution |
| src/zephyr/pf_alloc/allocation_config.py | AllocationConfig |
| src/zephyr/pf_alloc/allocation_orchestrator.py | StrategyAllocation |
| src/zephyr/regime/validation/wyckoff_walkforward.py | LayerResult |

（逐名版 detail 原文与批量版 detail 原文逐字节相同，存于证据 JSON 的 old.detail / new.detail）

### 计时（before / after，本机 worktree 实测）

| 实现 | git grep 调用次数 | 累计耗时 |
|---|---|---|
| 旧·逐名 `git grep -l` | 328 | 34.639s |
| 新·批量 `git grep -n -E`（1 批，pattern 5177 字符，n_chunks=1） | 1 | 0.838s |

⇒ 单次 commit 成本降 ~41×（本机 0.1s/grep 热缓存读数）；
总筹册 §2.1 记录的历史实测 1519 次/19186s 即此逐名面的规模外推。

### 全 120 样本表

| # | 样本文件 | 类名数 | 判据对比 |
|---|---|---|---|
| 1 | src/zephyr/governance/meta_question/exam_loop/event_codes.py | 1 | IDENTICAL |
| 2 | src/zephyr/governance/meta_question/exam_loop/exam_lifecycle.py | 1 | IDENTICAL |
| 3 | src/zephyr/governance/meta_question/exam_loop/exam_plan.py | 2 | IDENTICAL |
| 4 | src/zephyr/governance/meta_question/exam_loop/ledger.py | 1 | IDENTICAL |
| 5 | src/zephyr/governance/meta_question/exam_loop/reexam_scheduler.py | 1 | IDENTICAL |
| 6 | src/zephyr/governance/meta_question/exam_loop/writeback.py | 4 | IDENTICAL |
| 7 | src/zephyr/governance/meta_question/exam_ops.py | 4 | IDENTICAL |
| 8 | src/zephyr/governance/meta_question/meta_question_registry.py | 1 | IDENTICAL |
| 9 | src/zephyr/ai_layer/cleaning/auditor.py | 6 | IDENTICAL |
| 10 | src/zephyr/ai_layer/cleaning/local_prefill.py | 2 | IDENTICAL |
| 11 | src/zephyr/ai_layer/cleaning/policy.py | 2 | IDENTICAL |
| 12 | src/zephyr/ai_layer/cleaning/spec_store.py | 4 | IDENTICAL |
| 13 | src/zephyr/ai_layer/cleaning/washer.py | 9 | IDENTICAL |
| 14 | src/zephyr/ai_layer/comparator/__init__.py | 3 | IDENTICAL |
| 15 | src/zephyr/ai_layer/comparator/compare_events.py | 2 | IDENTICAL |
| 16 | src/zephyr/ai_layer/comparator/executor.py | 3 | IDENTICAL |
| 17 | src/zephyr/ai_layer/comparator/experiment_store.py | 6 | IDENTICAL |
| 18 | src/zephyr/ai_layer/comparator/fairness.py | 2 | IDENTICAL |
| 19 | src/zephyr/ai_layer/comparator/policy.py | 1 | IDENTICAL |
| 20 | src/zephyr/ai_layer/comparator/too_good.py | 5 | IDENTICAL |
| 21 | src/zephyr/ai_layer/heritage/closure_check.py | 2 | IDENTICAL |
| 22 | src/zephyr/ai_layer/heritage/forget.py | 2 | IDENTICAL |
| 23 | src/zephyr/ai_layer/heritage/heritage_events.py | 3 | IDENTICAL |
| 24 | src/zephyr/ai_layer/heritage/policy.py | 7 | IDENTICAL |
| 25 | src/zephyr/ai_layer/heritage/priors.py | 2 | IDENTICAL |
| 26 | src/zephyr/ai_layer/heritage/store.py | 7 | IDENTICAL |
| 27 | src/zephyr/ai_layer/perceive/search_orders.py | 4 | IDENTICAL |
| 28 | src/zephyr/ai_layer/perceive/source_registry.py | 4 | IDENTICAL |
| 29 | src/zephyr/ai_layer/perceive/translator.py | 5 | IDENTICAL |
| 30 | src/zephyr/ai_layer/redline/annual_review.py | 2 | IDENTICAL |
| 31 | src/zephyr/ai_layer/redline/dashboard_pipeline.py | 5 | IDENTICAL |
| 32 | src/zephyr/ai_layer/redline/freedom_weekly_report.py | 1 | IDENTICAL |
| 33 | src/zephyr/ai_layer/redline/no_delete_manifest.py | 1 | IDENTICAL |
| 34 | src/zephyr/ai_layer/redline/session_env_guard.py | 1 | IDENTICAL |
| 35 | src/zephyr/ai_layer/redline/sev_router.py | 2 | IDENTICAL |
| 36 | src/zephyr/ai_layer/scheduling/dispatcher.py | 2 | IDENTICAL |
| 37 | src/zephyr/ai_layer/scheduling/maturity.py | 2 | IDENTICAL |
| 38 | src/zephyr/ai_layer/scheduling/order_daemon.py | 2 | IDENTICAL |
| 39 | src/zephyr/ai_layer/scheduling/router.py | 1 | IDENTICAL |
| 40 | src/zephyr/ai_layer/scheduling/scheduling_events.py | 2 | IDENTICAL |
| 41 | src/zephyr/ai_layer/scheduling/seed_writer.py | 2 | IDENTICAL |
| 42 | src/zephyr/ai_layer/switch_engine/approval_router.py | 2 | IDENTICAL |
| 43 | src/zephyr/ai_layer/switch_engine/rollout_tiers.py | 2 | IDENTICAL |
| 44 | src/zephyr/ai_layer/tools/__init__.py | 1 | IDENTICAL |
| 45 | src/zephyr/ai_layer/tools/inventory_generator.py | 2 | IDENTICAL |
| 46 | src/zephyr/ai_layer/tools/scoring.py | 3 | IDENTICAL |
| 47 | src/zephyr/ai_layer/tools/suite.py | 1 | IDENTICAL |
| 48 | src/zephyr/ai_layer/tools/usage_stats.py | 2 | IDENTICAL |
| 49 | src/zephyr/governance/standards_governance/standard_checkup.py | 1 | IDENTICAL |
| 50 | src/zephyr/intelligence/budget_analyzer.py | 1 | IDENTICAL |
| 51 | src/zephyr/intelligence/model_intel/intel_card.py | 7 | IDENTICAL |
| 52 | src/zephyr/intelligence/model_intel/scanner.py | 2 | IDENTICAL |
| 53 | src/zephyr/intelligence/model_profiling/dual_run.py | 2 | IDENTICAL |
| 54 | src/zephyr/intelligence/switch_engine/criteria.py | 1 | IDENTICAL |
| 55 | src/zephyr/intelligence/switch_engine/shadow_runner.py | 6 | IDENTICAL |
| 56 | src/zephyr/intelligence/switch_engine/switch_engine.py | 3 | IDENTICAL |
| 57 | src/zephyr/intelligence/switch_engine/switch_registry.py | 2 | IDENTICAL |
| 58 | src/zephyr/gov_enforcement/commit_gates/_tree_view.py | 9 | IDENTICAL |
| 59 | src/zephyr/governance/registry_projection/model.py | 3 | IDENTICAL |
| 60 | src/zephyr/governance/registry_projection/pg_source.py | 1 | IDENTICAL |
| 61 | src/zephyr/governance/registry_projection/projection_generator.py | 1 | IDENTICAL |
| 62 | src/zephyr/governance/registry_projection/renderer.py | 1 | IDENTICAL |
| 63 | src/zephyr/governance/registry_projection/state.py | 1 | IDENTICAL |
| 64 | src/zephyr/governance/registry_ledger/api.py | 2 | IDENTICAL |
| 65 | src/zephyr/infrastructure/duckdb_runtime_gate.py | 3 | IDENTICAL |
| 66 | src/zephyr/gov_enforcement/commit_gates/approval_resolver.py | 1 | IDENTICAL |
| 67 | src/zephyr/signal_ashare/sector/sector_state_aggregator.py | 4 | IDENTICAL |
| 68 | src/zephyr/backtest/regime_validation/condition_package.py | 1 | IDENTICAL |
| 69 | src/zephyr/backtest/regime_validation/exam_cost_gate.py | 2 | IDENTICAL |
| 70 | src/zephyr/gov_enforcement/commit_gates/library/tag_vocab_gate.py | 1 | IDENTICAL |
| 71 | src/zephyr/alt_data/cohort_daily_writer.py | 1 | IDENTICAL |
| 72 | src/zephyr/alt_data/emotion_index_builder.py | 1 | IDENTICAL |
| 73 | src/zephyr/ex_sor/services/rl_trainer/td3_agent.py | 1 | IDENTICAL |
| 74 | src/zephyr/ex_sor/services/rl_trainer/trainer.py | 2 | IDENTICAL |
| 75 | src/zephyr/library/librarian.py | 3 | IDENTICAL |
| 76 | src/zephyr/factor/technical_indicators/chips.py | 8 | IDENTICAL |
| 77 | src/zephyr/data/calendar_coverage_checker.py | 2 | IDENTICAL |
| 78 | src/zephyr/ai_layer/intake/card_store.py | 3 | IDENTICAL |
| 79 | src/zephyr/ai_layer/intake/dedup.py | 3 | IDENTICAL |
| 80 | src/zephyr/ai_layer/intake/gate.py | 3 | IDENTICAL |
| 81 | src/zephyr/ai_layer/intake/intake_events.py | 2 | IDENTICAL |
| 82 | src/zephyr/ai_layer/intake/kpi.py | 3 | IDENTICAL |
| 83 | src/zephyr/risk/paper_hedge_leg.py | 4 | IDENTICAL |
| 84 | src/zephyr/data/alert_webhook_dispatch.py | 4 | IDENTICAL |
| 85 | src/zephyr/strategy_factory/owner_regime_switcher/engine.py | 2 | IDENTICAL |
| 86 | src/zephyr/strategy_factory/owner_regime_switcher/exam.py | 1 | IDENTICAL |
| 87 | src/zephyr/strategy_factory/owner_regime_switcher/switcher.py | 2 | IDENTICAL |
| 88 | src/zephyr/pf_alloc/crisis_gate.py | 7 | IDENTICAL |
| 89 | src/zephyr/ex_core/execution_report_producer.py | 3 | IDENTICAL |
| 90 | src/zephyr/governance/resilience_governance/emergency_track_guardian.py | 6 | IDENTICAL |
| 91 | src/zephyr/data/quality_sentinel.py | 5 | IDENTICAL |
| 92 | src/zephyr/data/implementations/irm_provider.py | 1 | IDENTICAL |
| 93 | src/zephyr/data/implementations/hyperliquid_provider.py | 1 | IDENTICAL |
| 94 | src/zephyr/governance/standards_governance/rule_replay.py | 6 | IDENTICAL |
| 95 | src/zephyr/data/supply_sentinel.py | 1 | IDENTICAL |
| 96 | src/zephyr/infra_ops/config_effect_checker.py | 3 | IDENTICAL |
| 97 | src/zephyr/data/implementations/fx_ecb_provider.py | 1 | IDENTICAL |
| 98 | src/zephyr/strategy_pipeline/daily_decision_orchestrator.py | 2 | IDENTICAL |
| 99 | src/zephyr/plan_engine/close_verifier.py | 1 | IDENTICAL |
| 100 | src/zephyr/plan_engine/daily_plan.py | 4 | IDENTICAL |
| 101 | src/zephyr/plan_engine/scenario_classifier.py | 1 | IDENTICAL |
| 102 | src/zephyr/plan_engine/intraday_l1_tracker.py | 2 | IDENTICAL |
| 103 | src/zephyr/plan_engine/next_day_forecaster.py | 1 | IDENTICAL |
| 104 | src/zephyr/infrastructure/system_telemetry/measure_calibration.py | 1 | IDENTICAL |
| 105 | src/zephyr/ex_sor/risk_redline.py | 3 | IDENTICAL★viol |
| 106 | src/zephyr/plan_engine/judgment_ledger.py | 4 | IDENTICAL |
| 107 | src/zephyr/plan_engine/judgment_settler.py | 2 | IDENTICAL |
| 108 | src/zephyr/infra_runtime/runtime_admission.py | 5 | IDENTICAL★viol |
| 109 | src/zephyr/strategy_factory/owner_band_t/engine.py | 2 | IDENTICAL |
| 110 | src/zephyr/backtest/core/cost_attribution.py | 3 | IDENTICAL★viol |
| 111 | src/zephyr/backtest/core/cost_model_calibration.py | 3 | IDENTICAL |
| 112 | src/zephyr/pf_alloc/allocation_config.py | 2 | IDENTICAL★viol |
| 113 | src/zephyr/pf_alloc/allocation_inputs.py | 6 | IDENTICAL |
| 114 | src/zephyr/pf_alloc/allocation_orchestrator.py | 8 | IDENTICAL★viol |
| 115 | src/zephyr/pf_alloc/allocation_persistence.py | 1 | IDENTICAL |
| 116 | src/zephyr/ex_core/daban_load_producer.py | 5 | IDENTICAL |
| 117 | src/zephyr/shared/utils/market_units.py | 2 | IDENTICAL |
| 118 | src/zephyr/regime/validation/wyckoff_walkforward.py | 2 | IDENTICAL★viol |
| 119 | src/zephyr/data/implementations/breadth_freshness_alerts.py | 1 | IDENTICAL |
| 120 | src/zephyr/data/implementations/index_breadth_compute.py | 1 | IDENTICAL |

## 5. 净零与取代申报（#ARCH-310 §4）

- 净新增门禁台数 = 0（CREATE-GUARD 既有 gate_id，不翻 CAPABILITY-OVERLAP enabled 旗——Owner 门位）。
- 取代申报：新查功能关键词命中即红 **取代** (a) `create_guard.py` L827-848 fail-open basename 碰撞检测的"判重尺"角色（其降为冗余后备，本道不删）；(b) `capability_overlap_gate.py` `_check_py_overlap` stage-1 文件名词元启发式（该 gate 整体 disabled，代码内注释标注取代关系，防两处执法同一病=第二真源）。

## 6. verified（本道亲手复现，各带命令）

- HEAD = `3eeb935743`，分支 `ai/st-p1-gate/piece-one-guard`；命令：`git log --oneline -3` + `git branch --show-current`。
- 裁定号现值（**本案卷不引用任何裁定号**，仅登记现值）：
  `git show HEAD:docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | grep -oE "裁定#[0-9]+" | sort -V | tail -1`
  → `裁定#413`。（00 册给的命令路径缺 `catalogs/` 段，实际路径以 `git ls-files "*ruling_registry*"` 为准。）
- find() 检索面与审计通道：读码 `src/zephyr/governance/capability_lookup.py` L892-949（haystack L924-930）、
  L109-111（LOOKUP_AUDIT_DIR 锚 MAIN_REPO_ROOT）、L297-356（write_lookup_audit_log，result_count 字段）、
  L1461-1482（`_entry_to_dict` 暴露 canonical_file 不暴露原始 canonical_override；派生优先级 1=override，L599-601）。
- `_CJK_MIN_SUBSTRING = 3`（L134）；命令：`grep -n "_CJK_MIN_SUBSTRING" src/zephyr/governance/capability_lookup.py`。
- 本机实测·`CapabilityLookup()` 构造 = **73.3~85.6s**（388 caps，两次冷缓存读数）；首个带命中 find ≈ +15s（一次性派生/探针冷启动），
  此后 find 亚毫秒——命令：`python -c` 走 `time.perf_counter()` 包裹（输出存 `.runtime/tmp/probe_check.txt`/`probe_check2.txt`，任务绑定不入库）。
- 本机实测·单词探针过宽：`find("gate")` → 181/388 命中 ⇒ 驱动 §1 的"纯 ASCII 探针须 ≥2 词"守卫。
- 本机实测·单词 `git grep -l` 热缓存 ~0.09-0.13s/次；全量类名行扫描（`git grep -h "^class "`）0.13s、
  现存同名 class 714 个 ⇒ §4 重放样本集确有真实违规可撞。
- 真实注册表命中样例（红证①重件依据）：docstring 首段 "Capability lookup surface..." → bigram 探针
  "capability lookup" 命中 `capability_lookup` 能力（canonical=src/zephyr/governance/capability_lookup.py）等 27 项。
- 重放总账：`python tests/gov_enforcement/create_guard_batch_replay.py`
  → `samples=120 classes=328 verdict_byte_equal=True attr_mismatch=0 old_greps=328(34.6s) new_greps=1(0.8s) violations_old=6`。

## 7. 施工日志与已知风险处置

- 共存面风险（预案命中）：新尺在既有测试的全管线跑批中可能误拦唯一名文件——实测既有
  `test_create_guard.py` 31 件全绿（tests/ 豁免 + 探针须 ≥2 词 + 单词全库噪声守卫 + 自引用豁免共同兜底）。
- 双载成本风险（预案命中）：初版 helper 自建 `CapabilityLookup()` ⇒ 与 basename 检查各 86s；已收敛为
  `_run_file_registration_checks` 内单点构造共享（缝 `_build_capability_lookup`），basename 检查增
  `lookup=` 可选参（默认 None 保持原独立构造语义，外部调用不破）。
- 行为变更登记：CREATE-GUARD 新面（查功能关键词 fail-closed + CLASS-UNIQUENESS 批量化）需进
  `gate_registry.yaml` 行为变更注记与 capability 名册 merge_evaluation——**热册单写手制，转总筹**
  （见 `register_manifest.md`）。
- 脏文件基线（施工前）：worktree 起自 `3eeb935743` 全干净；出口脏面 = 本道交付物（见 final report）。
- 案卷纪律：`.runtime/tmp/probe_check*.txt` 为任务绑定临时输出（不入库，24h TTL 区）；正式证据只认
  `create_guard_batch_replay_evidence.json`（生成器产出，未手工改）。
