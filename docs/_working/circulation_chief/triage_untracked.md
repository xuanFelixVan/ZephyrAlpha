---
ttl: task_bound
---

# S6 untracked 考古定谳册（st-ffchief-20261001 / S6 车道）

> 车道：S6 脏面清零（untracked 277 件逐件考古）。产出时间：2026-10-01。
> 方法：`git ls-files --others --exclude-standard` 全量 277 件；HEAD 吸收核查=逐件 `git cat-file -e HEAD:<path>`（0 件同名在 HEAD）+ 全量 blob 哈希对 HEAD 19023 路径比对（19 件内容等价）；别名落地=`git log --all --oneline -- <path>`（全部代码件 0 历史）；归属证据=CCR token 册（capability_canonical_file_registry.yaml `creation_tokens`，12374 路径）+ 翻译册 + `.runtime/handoffs/*` + 战役册 + session_registry 存活面 + PID 核验。
> 铁律遵守：本册为唯一写产物；零 git 写操作；零文件移动/删除。
> 友军禁区（总包 §1 在册）：st-fullscore-20260930（心跳 2min 活跃）域内件标记「友军在飞-勿裁」；另 PID 18376=ZCode.exe 存活，其 `.tmp.18376.*` 同列勿裁；PID 28828 已死（总包 S1 已处方归档三件，实核得四件）。

## §1 五桶计数汇总

| 桶 | 件数 | 说明 |
|---|---|---|
| 落地候选 | 152 | 32 袋（L01–L32），见 §2 |
| 已吸收 | 1 | 内容=HEAD 等价残留，见 §3 |
| 归档 | 4 | CAS tmp 残留（PID 28828 已死），移 campaign_trash，见 §4 |
| 废弃 | 1 | 墓碑件 blob 封存销账，见 §4 |
| 数据产物 | 105 | 政策件按目录聚合（40 政策忽略建议 + 65 跑批产物落地建议），见 §5 |
| 友军在飞-勿裁 | 14 | fullscore 域 10 + PID 18376 tmp 4，不裁不清，见 §4 附 |
| **合计** | **277** | 对账平 |

## §2 落地候选清单（152 件 / 32 袋）

> token 状态标注：`T:n`=CCR creation_tokens 在册 n 件；`需补 n`=落地前须补 token（CREATE-GUARD 硬拦）。翻译册=module_translation_registry.yaml 词条（`词 n`=在册 / `需补 n`）。tests/ 豁免 token。

### 治理/登记批（scripts+config）

- **L01 F128 数据安全接线批（8 件）** `T:5` `词3` — created_by st-menu-w3h-20260930（token merge_evaluation：NB1-B2 裁定卡处方，继任 794f16569b DEPRECATED 包翻案接线，Owner 批文）。件：`src/zephyr/data_security/wiring/{__init__,audit_sink,data_exit_guard,lsg_masking_front}.py`、`config/data_masking_policy.yaml`、`tests/data_security/test_wiring_{audit_sink,data_exit_guard,lsg_masking_front}.py`。HEAD 无等价物。
- **L02 F127 数据质量批（5 件）** `T:3` `需补词2` — st-menu-t1b1-20260930（F127 退役包 salvaging 迁址，NB1-B1 裁定卡+Owner 本夜）。件：`src/zephyr/data/quality/{__init__,archive_sla_burnrate,sla_breach_predictor}.py`、`tests/zephyr/data/quality/{test_archive_sla_burnrate,test_sla_breach_predictor}.py`。翻译册旧词条挂 `src/zephyr/data_eng/quality_sla_breach_predictor.py` 旧路径，新路径词条需补 2。
- **L03 CN-MAC 宏观族批（3 件）** `T:2` `词1` — st-menu-t1b5-20260930（NB1-B5 R1/R2-R3 处方件，handoff 在册）。件：`config/macro_indicator_series_map.yaml`、`src/zephyr/regime/features/macro_regime_sensor.py`、`tests/regime/features/test_macro_regime_sensor.py`。
- **L05 registry_entry_counts_reconciler 批（2 件）** `T:1` `需补词1` — st-finaldel-ownr2-20260930（token 评注：reconciler 无 ROOR entry_count 回填处方法，CR-007 工具无自动触发，本件填空区；注意永久系统四要素=事件触发，禁 cron）。件：`src/zephyr/governance/audit/registry_entry_counts_reconciler.py`、`tests/governance/test_registry_entry_counts_reconciler.py`。
- **L07 st-final-build 治理波次批（17 件）** `T:14`（tests 豁免） — st-final-build-20260926（token 评注：唯一归档位，本役波次案卷与生成器）。件：`scripts/governance/d5_architecture/validators/{validate_construction_steps,validate_dev_delivery_map,validate_strategy_card_lifecycle_map}.py`、`scripts/governance/data_supply/{check_wave3_rulers,no_cache_endorsement,strict_truth_reader,supply_conservation}.py`、`scripts/governance/wave1a/store_liveness_probe.py`、`scripts/governance/wave1b/{claim_gate_repro,dead_letter_census,dead_letter_prescriptions}.py`、`scripts/governance/wave2/lane_inventory.py`、`scripts/governance/wave10/wave10_asset_base_audit.py`、`scripts/governance/wave11/w178_universe_facts_gen.py`、`tests/governance/data_supply/test_false_green_crosscheck.py`、`tests/governance/d5_architecture/test_{construction_workflow_map_adversarial,data_supply_chain_map_adversarial}.py`。
- **L08 mapbuild 图件四件套批（2 件）** `T:2` — st-mapbuild-20260924（图11/图13 纵轴图生成器；st-nightsweep2-nd-20260930 handoff 亦载 dev_delivery_map 重生成为 D11-G02 对账件）。件：`scripts/governance/d5_architecture/generators/{generate_dev_delivery_map,generate_trading_day_cycle_map}.py`。
- **L09 standards 家族册批（2 件）** `T:1` — st-ff-registry-20260918。`scripts/governance/standards_governance/__init__.py` 为 tracked 生成器 `generate_standard_family_registry.py` 的缺失包门面（无它 test 不可导入）。件：上者 + `tests/governance/standards_governance/test_generate_standard_family_registry.py`。
- **L10 metaq DDL 批（2 件）** `T:2` — st-chainpile-20260922（meta_question_registry；check 件替代原 check_w6_batch.py 未落地即迁，DCR 合规迁址）。件：`scripts/governance/{apply_meta_question_ddl,check_meta_question_batch}.py`。
- **L23 gate/门禁测试批（3 件）** tests 豁免 — 消费 tracked 门面（commit_queue_landing.py / gate 体系）。件：`tests/governance/{test_registry_write_guards,test_scan_scope_convergence_equivalence}.py`、`tests/governance/d1_structure/test_untracked_phantom_docs_guard.py`（此件即"幻影文档哨兵"，与本 S6 任务同域，落地后可作 S6 复用守门）。
- **L22 commit queue 测试批（2 件）** tests 豁免 — 件：`tests/governance/{test_commit_queue_compaction_registry_merge,test_commit_queue_contention_reroute}.py`。

### src 模块批

- **L04 identifier_masking 批（1 件）** `T:1` `词1` — st-matrix-final-20260930（handoff 在册：identifier_masking 词条重登+map_family token 双册先行批）。件：`src/zephyr/shared/security/identifier_masking.py`。
- **L06 wave3 数据件批（6 件）** `T:3` `词3` — st-final-build-20260926（capability src_zephyr_data）。件：`src/zephyr/data/{date_normalize,dual_source_guard,miniqmt_caliber_sentinel}.py`、`tests/data/test_wave3_{date_normalize,dual_source_guard,miniqmt_caliber}.py`。
- **L12 l7 先验开启器批（3 件）** `T:2` `词1` — st-nightsweep-sw2-20260929（L1 施工项 9，L7 DESIGN design_final 解锁）。件：`src/zephyr/ai_layer/perceive/l7_prior_opener.py`、`docs/03_modules/_domain_ai_layer/algo_flow/l7_prior_opener.yaml`、`tests/ai_layer/perceive/test_l7_prior_opener.py`。
- **L13 emoreplay 复职批（2 件）** `T:1` `词1` — st-cmd-20260924（emoreplay_revival_l02c01，09-26 恢复轮补注册）。件：`src/zephyr/alt_data/emotion_index_replay.py`、`tests/alt_data/test_emotion_index_replay.py`。
- **L17 auction 强度批（4 件）** `需补T2` `需补词1` — 归属按 14 字段 CONSUMERS 注记（night_sweep SW14 案卷 / factor_registry FCT-INTRADAY-025 / CNS-11 取证面）。件：`src/zephyr/factor/auction_strength.py`、`scripts/backtest/eval_auction_strength_ic.py`、`tests/factor/{test_auction_strength,test_eval_auction_strength_ic}.py`。
- **L18 技术指标因子批（5 件）** `需补T4` `需补词1` — 归属=decision_map_campaign_20260924/cmd_successor CNS 接线（`CNS_wiring_accounting.md`、`landing/lane_cns.yaml` 在册提及）。件：`src/zephyr/factor/technical_indicator_factors/{__init__,bridge,daily_job,recipes}.py`、`tests/zephyr/factor/technical_indicator_factors/test_technical_indicator_factors.py`。
- **L20 closed_book/chart_cell 批（4 件）** `需补T2` `需补词2` — src 14 字段齐备（BLUEPRINT 指向 _domain_backtest blueprint），测试同名配对；无 handoff 直接锚（争议 §6-4 一并裁）。件：`src/zephyr/backtest/core/closed_book_gate.py`、`src/zephyr/backtest/regime_validation/chart_cell_materializer.py`、`tests/backtest/{test_closed_book_tick_gate,test_chart_cell_materializer}.py`。
- **L21 daily_gate_snapshot 测试批（2 件）** tests 豁免 — MOD-BT-213（trading_vision 编排 blueprint + decision_map L04_stock_wire LK-04），消费 tracked `src/zephyr/strategy_pipeline/daily_gate_snapshot.py`。件：`tests/strategy_pipeline/{test_daily_gate_snapshot_l5,test_daily_gate_snapshot_pool}.py`。**非** fullscore 友军件（其 staged tests 为 test_redblue/test_factory*/test_c4_cost_model_tiers/test_ibt_d01，无交集）。

### backtest 考试/重考批

- **L14 P1 条件表+做T材料线批（5 件）** `T:2 需补T1` — st-cmd-20260924（p1_conditional_tables_20260924 + t0_material_line_l05；conditional_tables 5 兄弟件已 tracked=部分落袋，本袋为收尾）。件：`scripts/backtest/{p1_conditional_tables,t0_material_line}.py`、`data/strategy_intake/conditional_tables/_cache_880.parquet`、`tests/backtest/{test_p1_conditional_tables,test_t0_material_line}.py`。p1_conditional_tables.py 本身无 token 需补 1。
- **L15 t0 规则引擎批（9 件）** `需补T2` + 数据 token `T:4` — decision_map_campaign L05-C03（预注册规则卡 frozen 在 docs/_working/decision_map_campaign_20260924/links/L05_t0/rule_cards/；翻译册 pg_only 词条在案——wm1-wave0 记录"他方在途三轮不收敛"）。件：`scripts/backtest/{t0_rule_engine,t0_state_match_matrix}.py`、`tests/backtest/{test_t0_rule_engine,test_t0_state_match_matrix,test_n_trial_ledger_t0_family}.py`、`data/strategy_intake/grid_t0_conditional_v1/`（negatives/cells/matrix/meta 4 件，token 在册 st-t0-matrix-20260924）。
- **L16 reexam CPCV 批（3 件）** `需补T1` — MOD-BT-IBT-REEXAM，docs/_working/reexam_strategy_lane/ 战役册在案。件：`scripts/backtest/reexam_cpcv_harness.py`、`tests/backtest/{test_reexam_cpcv_harness,test_c4_pit_red_injection}.py`。落地时机避让友军 `_c4_engine.py.tmp.18376`（§6-8）。
- **L25 x2 复权红证件（1 件）** tests 豁免 — 文件头自述"final3 战役 P4 预注册卡 §3"红证 v2 手动执行件（无 test_ 前缀不入 CI）。件：`tests/backtest/x2_adjfactor_red_proof.py`。

### sector_line / statreplay 批

- **L19 sector_line 批（11 件）** `T:2 需补T2` — st-pipeline-final-20260924（handoff 在册：GPU 输入包 token 三册批 v2 重投，DCR-005 整改迁移 scripts/sector_line/）+ docs/_working/sector_line/ 战役册全套在案。件：`scripts/sector_line/{build_gpu_input_pack,freeze_baseline}.py`、`data/strategy_intake/statreplay_baseline/{baseline_manifest_v0,v1}.json`（T:2）、`data/strategy_intake/grid_gpu_sectorcond_20260924-0834/`（README+npy×4+json，6 件 GPU 输入包产物）、`docs/03_modules/_domain_data/algo_flow/sector_line/index.md`。

### xhs/期权/巡检批

- **L11 xhs-full 期权统计+巡检批（5 件）** `T:5` — st-xhs-full-20260922（工单#3+#14 期权官方日统计历史回补唯一执行件）。件：`schemas/categories/market/market_option_daily_stats.py`、`scripts/backfill_option_daily_stats.py`、`scripts/ch/backfill_rzrq_history.py`、`scripts/audit/pcr_e4_exam.py`、`scripts/patrol/zcode_workspace_patrol.ps1`。

### metaq 数据册批（token 全在册）

- **L31 metaq 登记册数据批（7 件）** `T:7` — st-metaq-gc-20260924（283 问战役 WO-005/008 独占产物，"数字回指 PG/results 真源"）。件：`data/registers/metaq_io_2018/{china_2018_153,china_2020_153}.{matrix.json,rda}`（4）+ `io_2018_alignment_report.json`（1）+ `data/registers/metaq_product_synonyms/{ckg_edge_alignment.csv,product_synonym_links.csv}`（2）。
- **L32 grid 判决件收尾（1 件）** `T:1` — st-nightsweep-sw4-20260929（"哨兵机读判决件 t1_t2_handover 原子产出"）；同目录 manifest/negatives/summary 已 tracked=部分落袋收尾。件：`data/strategy_intake/grid_20260926-024947/net_returns.parquet`。

### 文档伴生批

- **L26 ALGO_FLOW 外部真源伴生册（8 件）** `T:8` — st-gpu-final7-20260929（gpu_core 1）+ st-nightsweep-sw2-20260929（fms 2）+ st-finaldel-cdocs-20260929 C97 补册（commit_gates 3 + deadref 基线 2，"清偿 born-dangling 锚"）。件：`docs/03_modules/_domain_backtest/algo_flow/gpu_core.yaml`、`_domain_gov_enforcement/algo_flow/{fms_hygiene_gate,fms_ref_extractor}.yaml`、`_domain_gov_enforcement/algo_flow/commit_gates/f/{fms_hygiene_gate,fms_ref_extractor}.yaml`、`.../commit_gates/r/read_side__init__.yaml`、`_domain_library/algo_flow/generators/{generate_fms_deadref_baseline.yaml,index.md}`。配对 src 全部 tracked（fms_hygiene_gate/fms_ref_extractor/gpu_core 已核 TRACKED）。
- **L27 模块/文档树目录索引批（16 件）** — 机生产物（生成器=`scripts/governance/d1_structure/generate_missing_index_md.py`，tracked；HEAD 同类 index.md 33+ 在册为先例）。件：`docs/index.md`、`docs/03_modules/MOD-CHAINPILE-METAQ/index.md`（chain_piling_campaign 配对）、`_domain_ai_layer/{index.md,algo_flow/index.md}`、`_domain_data/algo_flow/{data,implementations}/index.md`、`_domain_library/{index.md,algo_flow/index.md,algo_flow/collectors/index.md}`、`_domain_plan/{index.md,algo_flow/index.md}`、`_domain_portfolio_alloc/algo_flow/index.md`、`_domain_reporting/{report_archive_sink,review_trigger}/index.md`（配对 src 均 tracked）、`_domain_strategy_pipeline/{index.md,algo_flow/index.md}`。
- **L28 INFRA-STORE-003 存储地图（1 件）** — MOD-INF-043 永久手册，AGENTS.md §7 正引用此地图（"地图=INFRA-STORE-003"）——引用已发生而真源未落地，优先落地。件：`docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/storage_map.md`。

### 归档迁移收尾批

- **L29 _archive 迁移收尾（5 件）** `T:2` — ①`scripts/_archive/ops/quick_profile.py`（T:1 st-auction-bridge-20260917；内容=HEAD `scripts/quick_profile.py` 等价 → 落地归档位须同批删根位）②`scripts/_archive/grep_coverage.ps1`（T:1 st-commitfix-20261001"git mv 原样迁移"；内容=HEAD `_archive/ops/grep_coverage.ps1` 等价；HEAD 另有 `scripts/grep_coverage.ps1` 根位 → 迁移方向三分叉，见 §6-2）③`scripts/_archive/ops/register_belt_daemon_task.ps1`、④`serve_docs_http.bat`（原根位已 ABSENT，此为唯一残本，14 字段齐全 → 直接落地归档位）⑤`scripts/_archive/run_ollama_exam.py`（HEAD 根位 tracked 且内容**不等**，见 §6-3）。

### 会话证据链批

- **L30 session_logs 起点批（4 件）** — `scripts/record_session_start_commit.py`（tracked）的机生输出；session_logs/ 为 gitignore 白名单根，历史 retrospective 33 件在册=入库先例；本 S6 考古即消费了 st-c9-close4 件。件：`session_logs/{st-c9-close4,st-flashbiz-20260918,st-menu-t1b2-20260930,st-nightsweep2-nb2-20260930}/session_start_commit.txt`。政策裁定见 §6-6。
- **L24 杂项测试批（3 件）** tests 豁免 — `tests/blueprint/test_no_stale_agents_numbered_refs_in_scripts.py`、`tests/scripts/test_start_paper_session_wiring.py`（配对 tracked `scripts/start_paper_session.py`）、`tests/zephyr/data/test_akshare_daily_valuation_resume.py`。

## §3 已吸收清单（1 件，附 HEAD 锚）

| 路径 | HEAD 锚 | 处置 |
|---|---|---|
| `docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml.bak_pre_one_question` | blob 级等于 HEAD `candidate_module_registry.yaml`（哈希比对实证） | .bak 残留可清（总包 S1 处方"**.bak 同**"→ 移 campaign_trash 即可，零信息损失） |

## §4 归档/废弃清单

**归档（4 件，移 .runtime/tmp/campaign_trash）**——均为 `safe_write_text` CAS 中断残片，PID 28828 已核死（tasklist 无匹配），总包 S1 处方在案（"`.tmp.28828.*` 三件 PID 已死→移 campaign_trash"，实核为四件，处方顺延覆盖）：

1. `scripts/governance/_tasks/session_closeout_reconciler.py.tmp.28828.ef7854bc7450`（内容≠HEAD 目标，被 tracked 版取代）
2. `scripts/governance/d3_metadata/check_registry_consistency.py.tmp.28828.3c2f026a7405`（同上）
3. `scripts/governance/d3_metadata/inventory_blanked_canonical_fields.py.tmp.28828.98a77e028a66`（同上）
4. `scripts/governance/d6_security/detect_vague_terms.py.tmp.28828.ef767c657e0d`（内容=HEAD 等价，零损失）

**废弃（1 件，blob 封存销账）**：

- `src/zephyr/ex_core/bridge_instruction_kernel.py` — 证据链：CCR token（st-zchief8-20260928）merge_evaluation 自带墓碑"**已退役(墓碑)：被 B7 实现 qmt_file_bridge_broker 完全取代（判定 commit 78982c4c81）**"；handoff_st-zc9-lane-s2-20260929 复证（"已葬 bridge_instruction_kernel 同一把尺，禁第二套解析"→ ghost_order_sentinel 内联）。从未落地（`git log --all` 0 条）。**注意**：翻译册该模块词条（"QMT桥接指令内核"）仍在册活性态，销账时须同步墓碑化（§6-1）。

**附：友军在飞-勿裁（14 件，本册不裁不清，收官复核）**

- fullscore 域（10）：`data/strategy_intake/promotion_advisories/ADV-20260930-STR-VREV-025.json`、`data/strategy_intake/grid_20261001-051901/`（4 件）、`docs/_working/integrated_backtest/artifacts_v2/{W_HOLDOUT,W_IS,W_OOS,_regression/ab_neutral_root/W_OOS,_regression/legacyflat_W_OOS/W_OOS}/composed_panel.pkl`（5 pkl；其同目录 csv/yaml 已被该会话 staged）。
- PID 18376（ZCode.exe 存活）tmp（4）：`scripts/commit_queue.py.tmp.18376.0486a91925ee`、`scripts/backtest/f06_e4_wfa_exam.py.tmp.18376.ef6844d6fa56`、`scripts/backtest/translated/_c4_engine.py.tmp.18376.0778f70f85b8`（三者内容均≠HEAD 目标=可能在飞写）、`scripts/governance/commit_queue_landing.py.tmp.18376.b68dcdb5b8c7`（内容=HEAD 等价，PID 复核后即可清，零损失）。

## §5 数据产物政策建议（105 件，按目录聚合）

> 原则沿 .gitignore 既有"运行时/派生产物边界收口（AI-AUDIT03）"判例：机生可再生日志/状态→gitignore+理由；有 token 或 tracked 先例的→落地。

| 目录 | 件数 | 性质 | 建议 |
|---|---|---|---|
| `data/backup/`（alt_regime_f23_weekend_20260917、stock_indicator_circmv_20260916） | 6 | 一次性数据修复备份（README+TSV，操作发生于 0916-0917） | **不入库**：gitignore `data/backup/`；盘面保留待数据核验后由 Owner 定清理 |
| `data/backups/`（c1_market_limit_up_down pre_ghostclean + manifest） | 2 | 同上（ghostclean 前置备份） | **不入库**：gitignore `data/backups/`；盘面保留 |
| `data/local_fallback_quarantine/` | 21 | 本地回退隔离区（TSV 隔离件，_README 说明政策） | gitignore 整目录；**特例**：`_README.txt` 建议入库（政策说明件）→ 计 1 件落地候选随 L 系列批 |
| `data/cleaning_gate/`、`data/cleaning_anomaly_gate/`、`data/quality_sentinel/` | 6 | 清洗门/质量哨兵日机生报告与状态账（消费方=cleaning_engines/cleaning_anomaly_hosting 等 tracked 模块） | **不入库**：gitignore 日期模式报告+状态账（运行时自建，判例=watchdog_state.json） |
| `data/compliance_log/checklist/` | 2 | checklist_evidence.py 取证输出 | **不入库**：gitignore（盘面留档即审计留存） |
| `data/divergence_stats/` | 1 | divergence_stats.py 派生 jsonl | **不入库**：gitignore |
| `data/databases/rolling_archive_state.json` | 1 | rolling_archive_reconciler 运行时状态 | **不入库**：gitignore（判例=data/databases/depgraph_dirty.flag） |
| `data/reports/morning_digest.md` | 1 | 日报机生（该目录 tracked 先例均为一次性诊断报告，非日报） | **不入库**：gitignore `data/reports/morning_digest.md` |
| `data/strategy_intake/grid_2026{0915..0926}-*`（13 个跑批目录） | 65 | intake 跑批产物（manifest/negatives/summary/net_returns/structure_knowledge 等） | **建议落地**（首选）：同目录 tracked 先例在案（grid_20260929-040003/040141 已 tracked），且 E4 重考/复盘证据链引用；整袋批号 **DATA-GRID-BACKFILL**。次选：有裁定后 gitignore `data/strategy_intake/grid_2*/`（机生可再生）——两路线取舍见 §6-5 |

小计：政策忽略 40 + 跑批落地建议 65 = 105。

## §6 争议件（需总包裁定）

1. **bridge_instruction_kernel 墓碑同步**：文件判废弃（§4），但 CCR token 条目与翻译册词条均未同步墓碑。裁定点：blob 封存销账同 commit 是否一并把 CCR/翻译册条目打墓碑（RULE-RULING 同 commit 原子）。
2. **grep_coverage.ps1 三位去留**：token（st-commitfix-20261001，会话已不在册=无主）处方"平铺迁移至 _archive/ 根"；现状=HEAD 有 `_archive/ops/` 位 + `scripts/` 根位，盘面另有 _archive/ 根位 untracked。裁定点：落地 untracked 位并同批删两旧位（净零），或放弃迁移仅清 untracked 残留。
3. **run_ollama_exam.py 归档副本分歧**：`scripts/_archive/run_ollama_exam.py` 与 HEAD `scripts/run_ollama_exam.py` **内容不等**（blob 比对非等价）。裁定点：diff 定版后要么归档位覆盖落地+删根位，要么判旧版残本归档销账。
4. **closed_book/chart_cell 无主模块**：14 字段齐备但 0 token、0 翻译册词条、0 handoff 锚。裁定点：补 token+词条后随 L20 落地，或联系创建会话（疑 c9/close4 族）确认后处置。
5. **grid 跑批产物路线**（65 件）：落地（先例在案，DATA-GRID-BACKFILL）vs gitignore 政策件。裁定点二选一；本册建议落地。
6. **session_start_commit.txt 入库与否**（4 件）：无 tracked 同类先例（仅生成脚本在册）。建议入库（考古证据链现用），或 gitignore `session_logs/*/session_start_commit.txt` 判运行时件。
7. **commit_queue_landing.py.tmp.18376**：内容=HEAD 等价本可直接归档，因 PID 存活按勿裁。裁定点：总包收官时 PID 复核后清理（零损失）。
8. **test_c4_pit_red_injection.py 落地时机**：消费 tracked `_c4_engine`，但同族 `_c4_engine.py.tmp.18376` 在友军 PID 手里在飞。裁定点：L16 落地是否等 fullscore 收官。
9. **t0_rule_engine/t0_state_match_matrix token 缺位**：翻译册 pg_only 词条在案（wm1-wave0 记录"他方在途改动三轮稳定不收敛"），但 0 CREATE-GUARD token。裁定点：补 token 落地（L15），词条 pg_only 态一并收口。
10. **auction_strength 族无主**（L17）：14 字段+CONSUMERS 注记（SW14/FCT-INTRADAY-025）但 0 token、0 词条、0 handoff 锚。裁定点：按注记归属补册落地，或退回 night_sweep 归档。

## 附：证据锚速查

- token 册：`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml` L5161 起 creation_tokens（12374 路径）。
- 翻译册：`docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml`（工作区含 staged 增量；l7/emoreplay/wave3/wiring/identifier/macro 均已 OK，quality 新路径/ reconciler/ tif/ auction/ closed_book/ chart_cell 共 7 词条需补）。
- PID 核验：28828 死（tasklist 无匹配）；18376=ZCode.exe 存活。
- blob 等价比对：19 件命中（14 空 negatives.csv→数据产物、.bak、grep_coverage、quick_profile、2 tmp 等价）。
- 会话存活：st-fullscore（2min）、st-c10-*×4、st-chief7 心跳活跃；st-menu-w3h（249min）其 L01 批为完整 handoff 态产物。
