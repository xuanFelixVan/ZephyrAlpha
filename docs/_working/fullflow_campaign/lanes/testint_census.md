---
ttl: task_bound
completes_when: 全仓测试自包含性普查完成且确证件全部修复或登记
---

# 测试仪器完整性车道 · 测试自包含性普查（T2/T3）

> 车道 = `st-ff-testint-20260918` · 总包 = `st-fullflow-20260918` · 生成日 = 2026-09-18
> **本表由生成器产出**（脚本 `.runtime/tmp/ff-testint/render_census.py`，
> 输入 `census_hits.jsonl` / `fn_probe.jsonl` / `proof_results.jsonl`），禁手工改计数。

## 0. 一句话结论

扫描 `tests/**/test_*.py` **3507** 件，
七类非自包含形态共命中 **1864** 条线索，其中
**确证不自包含（单跑实测失败）= 0 件**（另 1 件为账本 R-035 已实锤并本车道已修的 `tests/rule/test_rule_red_blue.py`）；**单跑实测判自包含（= 模式命中被推翻）= 92 件**；无法判定 0 件。

## 1. 分档口径（判据，不是形容词）

| 档 | 判据 | 处置 |
|---|---|---|
| **确证不自包含** | `pytest <file>::<node>` **只跑这一个**即失败，且整文件跑通过 | 必修（T4） |
| **可疑** | 模式命中，但单跑通过 / 未做单跑（外来 WIP、禁改区、耗时超预算） | 只登记，不猜、不改 |
| **假阳** | 模式命中且单跑通过，且人工读码确认机制无害（如纯时间戳、装饰器导入期注册） | 登记为判据噪声度量 |

⚠️ 收集失败**不计**任何档：`-p no:cacheprovider` 未与 `-W ignore::pytest.PytestConfigWarning` 成对 → 
`INTERNALERROR` → 整轮 0 收集；`pytest tests/` 单进程全量必 import mismatch（跨目录同名 test）。
这两种形态在实证表里显式标 `collect-mismatch(不作证据)` / `wall-timeout(不作证据)`，**不得当作顺序依赖证据**
（账本 R-034/R-035 教训：曾据一次收集失败把不存在的缺陷写进遗留清单）。

## 2. 七类形态命中分布

| 形态 | 命中条数 | 命中文件数 | 实测判自包含 | 说明 |
|---|---|---|---|---|
| 形1 模块级可变累积（跨测试写→读） | 1 | 1 | 4 | 跨测试副作用累积——**最危险**，并行/分片必爆红 |
| 形3 顺序敏感命名/注释 | 383 | 194 | 16 | 命名含数字/first/again 或注释写顺序；多数只是用例名，需实测才判 |
| 形4 真实时钟作窗口条件 | 363 | 149 | 88 | `now()` 出现在窗口语义行——须区分「now 只作时间戳」（无害）与「now 作过滤窗」（跨日漂移假红） |
| 形5 读外部产物而本地不建不删 | 299 | 105 | 16 | 读生产文件/表而自身不建不删——低置信，多为读测试内构造的假数据 |
| 形6 就地 mutate 生产单例 | 1 | 1 | 0 | 就地 mutate 全进程单例 |
| 形4b 真实时钟仅作时间戳（判无害） | 817 | 300 | — | 只作时间戳（本表判无害，不计缺陷） |

## 3. 确证不自包含（实测单跑失败）

本轮实证批次内：**0 件**（除下表已实锤件）。

### 3.1 账本 R-035 已实锤件（本车道 T1 已治）

| 文件:行 | 形态 | 修前单跑 | 修后单跑 | 整文件 | 倒序跑 | 反向变异 |
|---|---|---|---|---|---|---|
| `tests/rule/test_rule_red_blue.py:41→431` | 形1 模块级可变累积 `_results`（9 个 TestTRAE00x 追加，报告测试直读并 `assert len>=9`） | `1 failed: Expected at least 9 test results, got 0`（1.46s） | `1 passed`（122.37s） | `10 passed`（115.64s） | `10 passed`（114.08s，倒序插件） | 注释夹具记录步 → `1 failed, got 0`（rc=1） |

## 4. 漏报界定（主扫描器覆盖面）

用更宽口径的独立探针（`.runtime/tmp/ff-testint/probe_fn.py`，把「≥2 个测试写同一模块级容器」「断言 `len(容器) >= N≥2`」「模块级读取容器」都算命中）复扫：

| 弱信号 | 文件数 |
|---|---|
| 同一模块级容器被 ≥2 个测试写 | 0 |
| 测试断言 `len(模块级容器) >= 2` 量级 | 5 |
| 模块级语句读取该容器（parametrize 等收集期依赖） | 12 |
| 一处写 + 另一处读（含非测试函数） | 3 |

→ 逐条人工读码：`cross_read` 三件中 `tests/alpha_signal/test_adversarial_alpha_signal.py` 与 
`tests/ml_experiment/test_adversarial_ml.py` 的 `_ATTACKS` 由**装饰器在导入期**注册（非测试期写），
无害；`tests/rule/test_rule_red_blue.py` 即已实锤件。`count_assert` 五件的被断言容器均为
**静态字面量表**（攻击向量/契约清单），非跨测试累积 → 假阳。

## 5. 可疑登记（模式命中但未确证，禁猜改）

| 文件 | 形态 | 为何不判确证 |
|---|---|---|
| — | — | 本轮实证批次无「无法判定」记录 |

登记不猜的外来件（工作区有他人未提交改动，本车道不改）：
`tests/plan_engine/test_judgment_ledger.py`（unstaged `M`，形1 弱信号 `_VALID_PAYLOADS`）——按宪法 §3.4 owner 责任制只登记。

## 6. 单跑实证明细（T3）

实证文件数 = **23**，nodeid 单跑次数 = **92**。

| node | 单跑 | 整文件 | 判定 |
|---|---|---|---|
| `tests/rule/test_rule_red_blue.py::TestRedBlueReport::test_generate_report` | rc=0 | rc=0 | 自包含 |
| `tests/rule/test_rule_red_blue.py::TestTRAE001CreateWithoutLock::test_create_file_without_lock` | rc=0 | rc=0 | 自包含 |
| `tests/rule/test_rule_red_blue.py::TestTRAE002CreateWithoutRegister::test_create_py_without_register` | rc=0 | rc=0 | 自包含 |
| `tests/rule/test_rule_red_blue.py::TestTRAE008ImportWithoutVerify::test_import_without_verify` | rc=0 | rc=0 | 自包含 |
| `tests/governance/audit/test_reconcile_async.py::TestStatusFileIO::test_stale_detection` | rc=0 | rc=0 | 自包含 |
| `tests/governance/audit/test_reconcile_async.py::TestStatusFileIO::test_running_within_threshold_not_stale` | rc=0 | rc=0 | 自包含 |
| `tests/governance/audit/test_reconcile_async.py::TestLaunchLockInflightGate::test_inflight_counts_fresh_pending_without_pid` | rc=0 | rc=0 | 自包含 |
| `tests/governance/audit/test_reconcile_async.py::TestLaunchLockInflightGate::test_inflight_excludes_stale_pending` | rc=0 | rc=0 | 自包含 |
| `tests/safety/test_game_day_scheduler.py::TestShouldRun::test_should_run_true_when_past_daily_interval` | rc=0 | rc=0 | 自包含 |
| `tests/safety/test_game_day_scheduler.py::TestShouldRun::test_should_run_false_when_within_per_commit_interval` | rc=0 | rc=0 | 自包含 |
| `tests/safety/test_game_day_scheduler.py::TestShouldRun::test_should_run_true_when_past_per_commit_interval` | rc=0 | rc=0 | 自包含 |
| `tests/safety/test_game_day_scheduler.py::TestShouldRun::test_should_run_false_when_within_weekly_interval` | rc=0 | rc=0 | 自包含 |
| `tests/dependency/test_dependency_freshness_monitor.py::TestCheckFreshness::test_fresh_dependency_no_alerts` | rc=0 | rc=0 | 自包含 |
| `tests/dependency/test_dependency_freshness_monitor.py::TestOverallHealthScore::test_fresh_dependencies_high_score` | rc=0 | rc=0 | 自包含 |
| `tests/dependency/test_dependency_freshness_monitor.py::TestRegister::test_register_dependency` | rc=0 | rc=0 | 自包含 |
| `tests/dependency/test_dependency_freshness_monitor.py::TestRegister::test_register_with_cves` | rc=0 | rc=0 | 自包含 |
| `tests/governance/trading/test_phase_e_main_flow.py::TestPhaseEFullPipelineE2E::test_p0_pipeline_l00_to_l07_full_flow` | rc=0 | rc=0 | 自包含 |
| `tests/governance/trading/test_phase_e_main_flow.py::TestPhaseEFullPipelineE2E::test_pipeline_universe_has_no_data_gaps` | rc=0 | rc=0 | 自包含 |
| `tests/governance/trading/test_phase_e_main_flow.py::TestPhaseEL02ToL03::test_aggregator_filters_low_confidence_signals` | rc=0 | rc=0 | 自包含 |
| `tests/governance/trading/test_phase_e_main_flow.py::TestPhaseEL02ToL03::test_aggregator_rejects_invalid_signals` | rc=0 | rc=0 | 自包含 |
| `tests/utils/test_utils_time_utils.py::TestSecondsSince::test_positive` | rc=0 | rc=0 | 自包含 |
| `tests/utils/test_utils_time_utils.py::TestSecondsSince::test_future_negative` | rc=0 | rc=0 | 自包含 |
| `tests/utils/test_utils_time_utils.py::TestSecondsUntil::test_past_negative` | rc=0 | rc=0 | 自包含 |
| `tests/utils/test_utils_time_utils.py::TestNowUtc::test_returns_utc_datetime` | rc=0 | rc=0 | 自包含 |
| `tests/governance/rule_bridge/test_session_worktree.py::test_sweep_skips_when_active_lockfile_fresh` | rc=0 | rc=0 | 自包含 |
| `tests/governance/rule_bridge/test_session_worktree.py::test_sweep_proceeds_when_lockfile_stale` | rc=0 | rc=0 | 自包含 |
| `tests/governance/rule_bridge/test_session_worktree.py::TestRetirePatchEvidence::test_abort_classifies_crlf_phantom` | rc=0 | rc=0 | 自包含 |
| `tests/governance/rule_bridge/test_session_worktree.py::test_sweep_cleans_stale_orphan` | rc=0 | rc=0 | 自包含 |
| `tests/trading/pipeline/test_phase_f_layers.py::TestPhaseFL08::test_approval_request_frozen_dataclass` | rc=0 | rc=1 | 自包含 |
| `tests/trading/pipeline/test_phase_f_layers.py::TestPhaseFP1Contracts::test_ctr_p1_007_execution_report` | rc=0 | rc=1 | 自包含 |
| `tests/trading/pipeline/test_phase_f_layers.py::TestPhaseFP1Contracts::test_ctr_p1_014_experiment_result` | rc=0 | rc=1 | 自包含 |
| `tests/trading/pipeline/test_phase_f_layers.py::TestPhaseFL09::test_backtest_result_resource` | rc=0 | rc=1 | 自包含 |
| `tests/trading/pipeline/test_phase_g_perf.py::TestPhaseGLatencyByLayer::test_l00_data_acquisition_latency` | rc=0 | rc=1 | 自包含 |
| `tests/trading/pipeline/test_phase_g_perf.py::TestPhaseGLatencyByLayer::test_l02_factor_computation_latency` | rc=0 | rc=1 | 自包含 |
| `tests/trading/pipeline/test_phase_g_perf.py::TestPhaseGFullPipelineThroughput::test_pipeline_single_symbol_end_to_end` | rc=0 | rc=1 | 自包含 |
| `tests/trading/pipeline/test_phase_g_perf.py::TestPhaseGFullPipelineThroughput::test_throughput_batch_n_symbols` | rc=0 | rc=1 | 自包含 |
| `tests/zephyr/data/test_kline_resampler.py::TestGetDateRange::test_7_days_range` | rc=0 | rc=0 | 自包含 |
| `tests/zephyr/data/test_kline_resampler.py::TestGetDateRange::test_30_days_range` | rc=0 | rc=0 | 自包含 |
| `tests/zephyr/data/test_kline_resampler.py::TestSynthMap::test_15m_from_1m` | rc=0 | rc=0 | 自包含 |
| `tests/zephyr/data/test_kline_resampler.py::TestSynthMap::test_30m_from_1m` | rc=0 | rc=0 | 自包含 |
| `tests/asset_inventory/test_lifecycle_asset_inventory.py::TestTimeDecay::test_active_to_stale` | rc=0 | rc=0 | 自包含 |
| `tests/asset_inventory/test_lifecycle_asset_inventory.py::TestTimeDecay::test_stale_to_deprecated` | rc=0 | rc=0 | 自包含 |
| `tests/asset_inventory/test_lifecycle_asset_inventory.py::TestTimeDecay::test_recent_active_no_trigger` | rc=0 | rc=0 | 自包含 |
| `tests/asset_inventory/test_lifecycle_asset_inventory.py::TestTimeDecay::test_deprecated_skips_time_decay` | rc=0 | rc=0 | 自包含 |
| `tests/audit/quality_static/test_absence_manager.py::TestCheckAbsence::test_absent_owner` | rc=0 | rc=0 | 自包含 |
| `tests/audit/quality_static/test_absence_manager.py::TestCheckAbsence::test_exactly_at_threshold` | rc=0 | rc=0 | 自包含 |
| `tests/audit/quality_static/test_absence_manager.py::TestCheckAbsence::test_one_day_below_threshold` | rc=0 | rc=0 | 自包含 |
| `tests/audit/quality_static/test_absence_manager.py::TestDetectOwnerReturn::test_recent_activity` | rc=0 | rc=0 | 自包含 |
| `tests/governance/commit_gates/test_depgraph_freshness_gate.py::TestCheckDualThreshold::test_fresh_passes` | rc=0 | rc=0 | 自包含 |
| `tests/governance/commit_gates/test_depgraph_freshness_gate.py::TestCheckDualThreshold::test_warn_passes_with_warning` | rc=0 | rc=0 | 自包含 |
| `tests/governance/commit_gates/test_depgraph_freshness_gate.py::TestCheckDualThreshold::test_block_blocks` | rc=0 | rc=0 | 自包含 |
| `tests/governance/commit_gates/test_depgraph_freshness_gate.py::TestCheckDualThreshold::test_future_timestamp_passes` | rc=0 | rc=0 | 自包含 |
| `tests/governance/test_commit_queue.py::TestSerializerLease::test_renew_refreshes_acquired_at_and_keeps_owner` | rc=0 | rc=0 | 自包含 |
| `tests/governance/test_commit_queue.py::TestDoneTtlCleanup::test_dead_never_cleaned_invariant` | rc=0 | rc=0 | 自包含 |
| `tests/governance/test_commit_queue.py::TestConcurrentEnqueue::test_3_sessions_50_items_zero_loss_zero_dup_fifo` | rc=0 | rc=0 | 自包含 |
| `tests/governance/test_commit_queue.py::TestDeadLetterTaskBoardLinkage::test_dead_letter_tags_task_board` | rc=0 | rc=0 | 自包含 |
| `tests/position/test_budget_change_handler.py::test_tier3_on_timeout` | rc=0 | rc=0 | 自包含 |
| `tests/position/test_budget_change_handler.py::test_tier3_trim_ratio_calculation` | rc=0 | rc=0 | 自包含 |
| `tests/position/test_budget_change_handler.py::test_tier3_zero_exposure_converged` | rc=0 | rc=0 | 自包含 |
| `tests/position/test_budget_change_handler.py::test_tier3_already_converged_no_trim` | rc=0 | rc=0 | 自包含 |
| `tests/audit/drift_integrity/test_cascade_detector.py::TestDetectCascade::test_events_outside_window_no_alert` | rc=0 | rc=0 | 自包含 |
| `tests/audit/drift_integrity/test_cascade_detector.py::TestIsAutoFixPaused::test_paused_module_returns_true` | rc=0 | rc=0 | 自包含 |
| `tests/audit/drift_integrity/test_cascade_detector.py::TestIsAutoFixPaused::test_expired_pause_returns_false` | rc=0 | rc=0 | 自包含 |
| `tests/audit/drift_integrity/test_cascade_detector.py::TestCascadeEvent::test_instantiation_with_optional_fields` | rc=0 | rc=0 | 自包含 |
| `tests/governance/data_layer/test_s3_snapshot_lifecycle.py::TestClassifySnapshots::test_expired_snapshot` | rc=0 | rc=0 | 自包含 |
| `tests/governance/data_layer/test_s3_snapshot_lifecycle.py::TestS3SnapshotLifecycleInit::test_default_snapshot_dir` | rc=0 | rc=0 | 自包含 |
| `tests/governance/data_layer/test_s3_snapshot_lifecycle.py::TestClassifySnapshots::test_hot_snapshot` | rc=0 | rc=0 | 自包含 |
| `tests/governance/data_layer/test_s3_snapshot_lifecycle.py::TestClassifySnapshots::test_warm_snapshot` | rc=0 | rc=0 | 自包含 |
| `tests/memory/test_vms_adversarial_hijack.py::TestKnowledgePollution::test_rrf_fusion_pollution_robustness` | rc=0 | rc=0 | 自包含 |
| `tests/memory/test_vms_adversarial_hijack.py::TestRetrievalHijack::test_future_timestamp_decay_should_be_capped` | rc=0 | rc=0 | 自包含 |
| `tests/memory/test_vms_adversarial_hijack.py::TestRetrievalHijack::test_time_decay_collection_specific_rates` | rc=0 | rc=0 | 自包含 |
| `tests/memory/test_vms_adversarial_hijack.py::TestKnowledgePollution::test_pollution_provenance_traceable` | rc=0 | rc=0 | 自包含 |
| `tests/zephyr/data/test_tick_subscriber.py::TestBizHeartbeat::test_payload_contract_fields` | rc=0 | rc=0 | 自包含 |
| `tests/zephyr/data/test_tick_subscriber.py::TestBizHeartbeat::test_first_frame_last_tick_null` | rc=0 | rc=0 | 自包含 |
| `tests/zephyr/data/test_tick_subscriber.py::TestBizHeartbeat::test_day_rollover_resets_today_rows` | rc=0 | rc=0 | 自包含 |
| `tests/zephyr/data/test_tick_subscriber.py::TestBizWatchdog::test_stale_intraday_triggers_resubscribe` | rc=0 | rc=0 | 自包含 |
| `tests/alt_data/test_research_report_collector.py::TestCollect::test_collect_ok` | rc=0 | rc=0 | 自包含 |
| `tests/alt_data/test_research_report_collector.py::TestRatingDiff::test_rating_change_event_to_bus` | rc=0 | rc=0 | 自包含 |
| `tests/alt_data/test_research_report_collector.py::TestRatingDiff::test_same_rating_no_event` | rc=0 | rc=0 | 自包含 |
| `tests/alt_data/test_research_report_collector.py::TestRatingDiff::test_out_of_order_report_ignored` | rc=0 | rc=0 | 自包含 |
| `tests/cross/test_cross_module_score.py::TestCrossModuleScorer::test_compute_rustiness_with_old_resolution` | rc=0 | rc=0 | 自包含 |
| `tests/cross/test_cross_module_score.py::TestCrossModuleScorer::test_compute_rustiness_recent_gives_zero` | rc=0 | rc=0 | 自包含 |
| `tests/cross/test_cross_module_score.py::TestCrossModuleScorer::test_compute_rustiness_cap_at_one` | rc=0 | rc=0 | 自包含 |
| `tests/cross/test_cross_module_score.py::TestModuleScore::test_custom_fields` | rc=0 | rc=0 | 自包含 |
| `tests/data/test_source_sla_tracker.py::TestAggregate::test_availability_and_counts` | rc=0 | rc=0 | 自包含 |
| `tests/data/test_source_sla_tracker.py::TestAggregate::test_percentiles_nearest_rank` | rc=0 | rc=0 | 自包含 |
| `tests/data/test_source_sla_tracker.py::TestAggregate::test_failure_reason_distribution_sorted` | rc=0 | rc=0 | 自包含 |
| `tests/data/test_source_sla_tracker.py::TestAggregate::test_window_filters_records` | rc=0 | rc=0 | 自包含 |
| `tests/escalation/test_owner_absence_escalation.py::TestSubmitDecision::test_prune_stale_decisions` | rc=0 | rc=0 | 自包含 |
| `tests/escalation/test_owner_absence_escalation.py::TestCheckAbsence::test_present_within_warning_timeout` | rc=0 | rc=0 | 自包含 |
| `tests/escalation/test_owner_absence_escalation.py::TestCheckAbsence::test_unresponsive_after_warning_timeout` | rc=0 | rc=0 | 自包含 |
| `tests/escalation/test_owner_absence_escalation.py::TestCheckAbsence::test_absent_after_critical_timeout` | rc=0 | rc=0 | 自包含 |

## 7. 本车道另案（仪器诚实性附注，非顺序依赖）

- **A1 红蓝注入面不闭合**：`tests/rule/test_rule_red_blue.py` 的 TRAE-001/002 把违规文件写进
  pytest `tmp_path`，但被检的 `scripts/governance/d11_compliance/audit_registration.py` 以
  `cwd=REPO_ROOT` 扫**真仓**（实测本仓报 25 个 orphan → rc=1 且含 orphan → 判 GREEN）。
  → **它测的是「仓库现在脏不脏」，不是「注入的违规能不能被检出」**。本车道只登记不擅改
  （改法=把审计指向 scratch 副本，属判据重设，须总包定；已按原样保留语义，未降级任何断言）。
- **A2 探针耗时=CI flake 源**：TRAE-005 的 `diagnose_depgraph.py` 单进程实测 **108s**
  （`real 1m48.0s`，2026-09-18），而 `pyproject.toml` 全局 `timeout = 120` → 有负载时该用例
  直接被 pytest-timeout 打死（本车道首轮实测即复现：`+ Timeout +` traceback 打在 `subprocess.run` 上）。
  已按仓库既有约定加 `@pytest.mark.timeout(300/600)`，**未改任何断言**。
- **A3 原 `_probe_trae005` 等价体在脚本缺失时会记两条 RED**（旧代码 `if not script.exists(): _record(...)`
  后无 `return`，随后 `subprocess.run` 抛 `FileNotFoundError` 再记一条）。该分支当前不可达
  （脚本在盘，已实测运行），本车道补 `return` 收敛为一条证据，不影响判定方向。

## 8. 复跑命令（Max 验真用）

```bash
python .runtime/tmp/ff-testint/scan_test_selfcontain.py        # 主扫描（形态1-7）
python .runtime/tmp/ff-testint/probe_fn.py                     # 漏报界定（宽口径）
python .runtime/tmp/ff-testint/build_candidates.py             # 候选清单
python .runtime/tmp/ff-testint/prove_isolated.py \\
  --candidates .runtime/tmp/ff-testint/candidates.jsonl \\
  --out .runtime/tmp/ff-testint/proof_results.jsonl --limit 33 --per-test-max 4
python .runtime/tmp/ff-testint/render_census.py                # 本表重渲染
```

