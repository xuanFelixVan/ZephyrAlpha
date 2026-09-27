---
ttl: task_bound
completes_when: lane_inventory.yaml 与本册对全部波2点名现场的三态计数、袋序列、冲突预警口径一致且经进程外复跑复核
---

# 波 2 车道清点与装袋方案（数据面=同目录 lane_inventory.yaml，机生禁手改）

> 施工执行队出品（只读取证+机生清单，不定真源、不自赋裁定号、不承诺"Owner 已批准"）。
> 清点范围以 `10_wave_plan.md` 波 2 表（2.1–2.4）+ 任务点名补列（lane_ff_single_writer / lane_ff_snapself /
> lane_reland_final / lane_snapself_land / lane_w17_only）为准；处方引 `11_rescue_playbook.md` R-1/R-2/R-3/R-4。
> 三态分箱一律对**落地基底 dev HEAD**（=主仓 `5701fb99c8`）判定；车道自身 HEAD 只作身份对照（lane_head_in 字段）。

## 案卷头部（四字段）

- **turn_budget**：≤6 次/块调研、第 8 次工具调用内出骨架、后期只落盘——骨架（本文件 v0）在 Write#2 落盘，达标。
- **verified（E1 直读，本包亲跑可复算）**：
  1) 主仓 dev=`5701fb99c8`；`git worktree list` 实测 73 条注册 worktree（与 X-09"73 vs 目录项 52 两口径勿混谈"一致）。
  2) 14 个现场逐个过 R-4 守卫：`git -C <dir> rev-parse --show-toplevel` == 目录本身才算真 worktree。
     结果：**12 条真 worktree 车道全部通过**；`.runtime/tmp/campaign_hold` 为普通目录（不采信其 git 读数，按 `/`→`__` 编码反查 dev 树清账）；主区点名件（2.4）按主仓现场登记。
  3) 自检红旗未触发：各道 porcelain/三态指纹两两不同（R-4"多条车道读数全同≈守卫漏"）。
  4) 逐件 sha256（CRLF→LF 归一，R-6-1 权威口径）、dev 命中、等值判定全部见 `lane_inventory.yaml`；`??` 计数只来自 `status --porcelain --untracked-files=all`（X-54）。
- **assumed（E3/E4 转述，未独立复验，禁作施工依据）**：
  1) C 册"272 脏项（238 M+34 ??）"为彼班时点读数，**本包现读 319（238 tracked + 81 ??）**——tracked 相符、untracked 34→81 增长，按 R-0 令以盘面现读为准并在此登记差异。
  2) D 册"169 件"现读相符（169 porcelain），但其"三态"按本包 dev 基线重切为 等值2/要投82/新建85。
  3) "灾备线"（2.4 点名无路径）与 `t1_t2_handover` 之"其测试"按 A/E 册转述列入，实存与否以 yaml 为准（测试实存：`tests/backtest/test_t1_t2_handover.py` 盘上 `??`）。
  4) campaign_hold 目标路径 = 文件名按 `/`→`__` 编码反查 dev 树所得；2 件反查不中系其目标在 dev 查无（本就是新建件）。
- **input_set_disjoint_with**：本包与被清点对象（.aidrafts/*、.worktrees/*、.runtime/tmp/campaign_hold）**零写交集**（只读+读 git 对象库）；
  写入仅本目录三件交付物；不复用 91/94 册未回笼读数；不采信主区脏面代替车道脏面。
- **evidence_ref.cmd**：
  `python docs/_working/total_command_closeout/wave2/lane_inventory.py [--print-md-bags]`（产出/复算 lane_inventory.yaml；运行日志 `.runtime/tmp/wave2_inv_run3.log`）；
  守卫抽验 `git -C .aidrafts/st-mapbuild-20260924 rev-parse --show-toplevel`；
  三态抽验 `git cat-file blob dev:<path>` 归一 sha vs `python -c` 盘上归一 sha。

## 一、现场总览（A 身份 + B/C 三态）

三态口径：**等值=免投**（盘上字节==dev 归一字节）；**要投=dev 有该路径但盘上更新**（热册必走 R-1 块级纯插入）；**新建=dev 查无此路径**（R-2 三件套）。`deleted=0` 全数无"dev 有而盘上删"件（禁任何删除性落地）。

| 现场 | 波包 | 真worktree | 分支 | 车道HEAD | 落后dev | 自有commit | porcelain(trk+??) | 免投 | 要投 | 新建 | 备注 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `.aidrafts/st-mapbuild-20260924` | 2.1 | ✅ | session/st-mapbuild-20260924 | cb6b4bfc0e | **245** | 0 | 319(238+81) | 1 | 238 | 80 | C 册 272→现读 319（?? 34→81，已登记） |
| `.worktrees/st-ailayer-final-20260924` | 2.2 | ✅ | ai/st-ailayer-final-20260924/fullflow-closure | f3cac8b95c | 63 | 0 | 169(169+0) | 2 | 82 | 85 | 脏面全显 tracked 因基底老；R5 嫌疑 2 件见 §三 |
| `.aidrafts/lane_ff_door` | 2.3 | ✅ | detached | 8c44d62dfe | 174 | 0 | 6(4+2) | 0 | 4 | 2 | |
| `.aidrafts/lane_ff_books` | 2.3 | ✅ | detached | 8c44d62dfe | 174 | 0 | 11(9+2) | 0 | 9 | 2 | 与 door 同基底 |
| `.aidrafts/lane_ff_replay` | 2.3 | ✅ | detached | 1e9b34999d | 172 | 0 | 3(0+3) | 0 | 0 | 3 | |
| `.aidrafts/st-audit-fix-20260924` | 2.3 | ✅ | session/st-audit-fix-20260924 | 69752057c0 | 76 | 0 | 27(27+0) | 1 | 15 | 11 | |
| `.runtime/tmp/campaign_hold/` | 2.3 | ❌普通目录 | — | — | — | — | 15 文件 | 1 | 12 | 2 | 系各道版本混合快照（§四逐件等值关系） |
| `.aidrafts/lane_ff_chfail` | 2.4 | ✅ | detached | 30505c93f6 | 71 | 0 | 7(5+2) | 0 | 5 | 2 | 该 HEAD 即 X-11 绕门审计涉案 commit（数据上报，不定性） |
| `.aidrafts/lane_ff_single_writer` | SUPP | ✅ | detached | 563bdfd716 | 78 | 0 | 1(0+1) | 0 | 0 | 1 | |
| `.aidrafts/lane_ff_snapself` | SUPP | ✅ | detached | ec0dd4f43a | 59 | 0 | 4(3+1) | 2 | 2 | 0 | 2 件测试已等值=免投（X-48 同族） |
| `.aidrafts/lane_reland_final` | SUPP | ✅ | detached | 830c3a5736 | 10 | 0 | 37(37+0) | **19** | 2 | 16 | 16 新建件系 `chain_fullflow_20260926/` 目录，同名内容已在 dev `chain_fullflow_closeout/`——**第二真源风险，先核后投**（§五-2） |
| `.aidrafts/lane_snapself_land` | SUPP | ✅ | detached | ec0dd4f43a | 59 | 0 | 5(5+0) | 3 | 2 | 0 | |
| `.aidrafts/lane_w17_only` | SUPP | ✅ | detached | c014f958fc | 53 | 0 | 2(2+0) | 1 | 1 | 0 | |
| 主区点名件（2.4） | 2.4 | 主仓 | dev | 5701fb99c8 | 0 | 0 | 2 | 0 | 0 | 2 | `t1_t2_handover.py`=AM：index 字节 c15a8b399add ≠ 盘上 635f2569276a ⇒ 门禁读 index（R-6-1），投前须由施工方以盘上字节重 add（本包未动） |

**合计**：免投 30 ／ 要投 372 ／ 新建 206 ／ 删除态 0 ⇒ **待投 608 件，切 88 袋，最大袋 38 件**（袋≤38 铁律满额），冲突预警 11 组（§四）。

## 二、袋序列（D 装袋方案；机生日志=同目录 lane_inventory.py --print-md-bags）

规则：一袋一域；袋≤38；门禁代码+它读的册+本体包同袋；本体与其测试同袋（ORPHAN-MODULE 处方）；热册/规则册/旗标一律**独立小袋**（R-1"该册变更单独成袋，勿 requeue 硬闯"）；token/翻译/depgraph 与件同袋（R-2）。
状态标：**B**=路径在 dev、内容更新（要投）；**C**=dev 查无（新建件，R-2 三件套）。

### 2.1 六图役（st-mapbuild-20260924，20 袋 318 件）

投序建议：先 C 域袋（10→11→12→09），再 B 域文档袋批量走，**HOTREG 8 袋最后且逐册单投**（R-1 三态分诊先行）。

- **2.1-DOCS-01..06**（B×227，docs/01_sop+02_handbook+03_modules 蓝图族）：
  construction_workflow_policy.md、alignment_checklist.md、project_handbook/01~07、MOD-ALT-EMOTION-INDEX-BUILDER.md、_cross_layer 蓝图 21 件（vector_memory_service_interface…shared_core/dashboard）、_domain_autonomy_core/perm、_domain_backtest 10、_domain_compliance 8、_domain_contracts 2、_domain_data 7、_domain_ex_sor 5、_domain_execution_core 10、_domain_factor/frontend/fundamental_signal/gov_enforcement、_domain_governance 9、_domain_infrastructure_operations 9、_domain_infrastructure_runtime 6、_domain_integration/library/machine_learning_train、_domain_mkt_data 7、_domain_plan_engine 2、_domain_portfolio_* 8、_domain_position 15、_domain_regime 4、_domain_reporting 9、_domain_research/risk 39、_domain_sell_decision 11、_domain_signal 11、_domain_simulation 9、_domain_trading 8（完整 38×5+37 清单见 yaml `bags[domain=DOCS]`）。
- **2.1-DOCSWORK-07**（C×38）：`docs/_working/map_build/` 六图交付面——00_campaign_brief、01_lane_workplan、03_final_blueprint_and_schema、99_pending_owner、fig11_delivery/00~08（9件）、fig12_datachain/00~05,11,12,90（9件）、fig13_daycycle/00~10（11件）、fig14_construction/00~03,90（6件）。
- **2.1-DOCSWORK-08**（C×9）：fig14/91_step_anchor_block_proposal.yaml、fig15_cardlife 00~03+90+91（6件）、fig16_ruling 00+91（2件）。
- **2.1-OTHER-09**（C5+B1）：config/construction_workflow_map.yaml C、data_supply_chain_map.yaml C、dev_delivery_map.yaml C、strategy_card_lifecycle_map.yaml C、trading_day_cycle_map.yaml C、governance_operations_map.yaml B。
- **2.1-SCRIPTS-governance-10**（C12+B2，本体+生成器+取号器+配对测试同袋）：check_registry_consistency.py B、align_all.py B、generate_{construction_workflow,data_supply_chain,dev_delivery,strategy_card_lifecycle,trading_day_cycle}_map.py C×5、validate_{construction_steps,data_supply_chain_map,dev_delivery_map,strategy_card_lifecycle_map,trading_day_cycle_map}.py C×5、next_ruling_id.py C、tests/governance/test_next_ruling_id.py C。
- **2.1-SRC-gov_enforcement-11**（C9+B1，五门本体+各自测试同袋）：commit_gates/{construction_workflow_map,data_supply_chain_map,dev_delivery_map,strategy_card_lifecycle_map,trading_day_cycle_map}_gate.py C×5 + tests/governance/commit_gates/test_ 同 5 件 C + panorama_alignment_gate.py B。
- **2.1-TEST-12**（C×5）：tests/governance/d5_architecture/test_*_adversarial.py 5 件（对应 5 验证器，投时并入 10/11 袋亦可，禁零消费者单飞——`git grep` 只认 src/ 引用）。
- **2.1-HOTREG-13..20**（B7+C1，逐册单袋）：capability_canonical_file_registry.yaml B、experiment_registry.yaml B、in_process_gate_registry.yaml B、module_translation_registry.yaml B、**ruling_registry.yaml B（悬空号 414/415 在本道盘上，RULING-REFERENCE 处方先改文字，dead 0040 实例）**、_registry/vocabularies/card_state_vocabulary.yaml C、_registry/vocabularies/index.md B、registry_of_registries.yaml B。

### 2.2 AI 层波2役（st-ailayer-final-20260924，22 袋 167 件）

- **2.2-DATA-01**（B×1）：data/audit-trail/rolling_archive_plan_shadow.jsonl ⚠X-15/X-20 夹具污染处置在册——追加 correction 记录，禁删历史行。
- **2.2-DOCS-02**（B×1）：sop/review_sop/defect_pattern_checklist.md。
- **2.2-DOCSWORK-03/04/05**（B13+C72，85 件）：ai_layer_vision（DESIGN×4 B + OBJ_R/OBJ_T/closure_wave2 C×11）、fullflow_mining（00_skeleton 总册 B + 91~95 C、02_tdm B? wiring_F C、05_missing_p0 C×17、93/94/96 C、m1~m7 各章 B/C 混布、backfill_wave2 C×8、sim-memos json+md B×2）。⚠其中 `92_coverage_triage_20260926.md`、`93_true_gap_list_20260926.md` 触 **R5-DIGIT-SUFFIX**（`_\d+$` 命中文件名尾 `_20260926`，无白名单无逃生标）⇒ 投前改名+重绑 token，否则一件拖死整袋（R-3 行 R5）。
- **2.2-OTHER-06**（B5+C1，配置政策册+各自测试同袋）：config/cleaning_rules.yaml C、comparison_policy.yaml B+test、model_routing_policy.yaml B、model_scoring_policy.yaml B+test、schedule_gate_policy.yaml B+test。
- **2.2-SCRIPTS-ai_layer-07**（B1+C2）：gen_intake_ref_snapshots.py B、gen_obj_r_s3_threshold_census.py C、run_ai_l1_scan_tick.py C。
- **2.2-SCRIPTS-backtest-08**（B1+C1）：auto_mount.py B、weight_ssot.py C（X-29 点名 31 件之一）。
- **2.2-SCRIPTS-governance-09**（B1+C2）：validate_static_manifest_drift.py B（**冲突件，§四-6**）、fullflow/__init__.py C、generate_fullflow_crosscheck.py C（X-14 悬空登记随件落地即消）。
- **2.2-SCRIPTS-misc-10**（B3+C1+test配对2）：register_ai_l1_scan_task.ps1 C（X-32：全机无 AI-L1 外扫任务，随本体投）、run_post_settlement.py B+test、start_paper_session.py B+test。
- **2.2-SRC-ai_layer-11**（B6+C6，含 D 册三雷本体+测试同袋）：comparator/experiment_store.py B+test、policy.py B、too_good.py B+test、redline/ai_secret_exposure.py C+test、scheduling/confirm_gate.py C+test、switch_engine/rollout_tiers.py B、tombstone_ttl_proposer.py C+test。
- **2.2-SRC-data-12**（B2+C1+test）：cleaning_rule_engine.py B、cleaning_rules_hosting.py C+tests/zephyr/data/ C、supply_sentinel.py B。
- **2.2-SRC-ex_core-13**（B×5）：miniqmt_broker.py、qmt_file_bridge_broker.py、fill_handler.py（J 项单写者线，与 SUPP-single_writer 袋对表）、position_reconciler.py、price_cage.py（X-30：两枚旗标是模块常量不在 flags.yaml）。
- **2.2-SRC-gov_enforcement-14**（B2+C1）：blueprint_format_gate.py B、state_vocab_registry_gate.py B、test_state_vocab_registry_gate.py C。⚠X-02：本道 priority 77/130 互换 hunk 必须先剔除再投（以 HEAD 为准），列入 W-11 前置排雷。
- **2.2-SRC-intelligence-15**（B×4）：criteria.py+test、switch_engine.py+test。
- **2.2-SRC-position-16**（B×1）：position_reconciler.py。
- **2.2-SRC-shared-17**（B1+C4）：lifecycle/registry_state_vocab.py C+test、security/secrets.py B ⚠（密钥三门触发面案 X-50 在途，投时按 own-diff 预跑）、vocab/__init__.py C、vocab/market_state.py C。
- **2.2-SRC-trading-18**（B×1）：decision_map.py。
- **2.2-TEST-19**（B11+C10，21 件独立测试袋）：conftest×5 B、test_snapshot_regen/test_maturity/test_evolution_chain_e2e/test_model_library_ddl B、SSOT 族+跨面新测试 C×10（test_comparison_ssot、test_rollout_tiers_ssot、test_c6_ai_layer_routes、test_obj_r_s3_threshold_census、test_weight_ssot_single_authority、test_fill_jsonl_single_writer、test_price_cage_bf6_wiring、test_fullflow_crosscheck_generator、test_switch_criteria_ssot、test_run_post_settlement_disclosure、test_tdm_false_auto_census）。⚠"零消费者新件必与接线同袋"⇒ 本袋内 C 件投前逐个反查其本体袋，能并则并。
- **2.2-HOTREG-20/21/22**（B×3 单册袋）：capability_canonical_file_registry.yaml（**冲突，§四-1**）、in_process_gate_registry.yaml（**冲突，§四-2**）、scripts/governance/script_manifest.yaml（**冲突，§四-8**）。
- 免投 2 件：state_vocabulary_registry.yaml、92_chief_command_wave2.md（盘==dev，勿动）。

### 2.3 全流通成品（door/books/replay/audit-fix/campaign_hold，31 袋 60 件）

- **2.3-campaign_hold-01..08**（B12+C2）：audit_fix_ledger.md B（§十一~十三热台账追加 ⇒ 键集合差自证删除集==∅）、tests__governance__ 两件 C（目标=tests/governance/test_commit_door_provenance.py / test_derived_books_parity.py，与 lane 袋同题**三处并版**，§四-11）、commit 链脚本 7 件 B（commit_queue.py、git_commit.py、commit_queue_landing.py、_shared/yaml_utils.py、validate_static_manifest_drift.py、generate_fail_open_register.py、generate_gate_registry.py、script_manifest.yaml、git_commit_gateway.py 中取 hold 版）、HOTREG：gate_registry.yaml B、rule_catalog_registry.yaml B、script_manifest.yaml B。hold=各道版本混合快照（§四给出等值对象），**单袋走 R-1 前先与来源车道对版**。
- **2.3-lane_ff_door-01..05**（B4+C2）：lane_gate_door_provenance.md C、commit_queue_landing.py B、commit_queue.py+git_commit.py B、git_commit_gateway.py B、test_commit_door_provenance.py C。
- **2.3-lane_ff_books-01..07**（B9+C2）：lane_gate_derived_books.md C、books 版 yaml_utils（scripts/_shared + src/shared/io）B、commit_queue_landing.py B、validate_static_manifest_drift.py B、generate_fail_open_register.py B、generate_gate_registry.py B、gate_registry.yaml B、rule_catalog_registry.yaml B、script_manifest.yaml B、test_derived_books_parity.py C。
- **2.3-lane_ff_replay-01..02**（C×3）：lane_gate_replay_selfproof.md C、gate_replay_selfproof.py C+test C（本体+测试同袋已并）。
- **2.3-st-audit-fix-01..09**（B15+C11）：audit_fix_ledger.md B（hold 同件**并版**）、chain_fullflow_campaign/ 骨架+6 lane 册 C、commit 链脚本 B 族（yaml_utils×2、commit_queue_landing、generate_fail_open_register、generate_gate_registry、commit_queue.py、git_commit.py、git_commit_gateway.py、test_commit_queue.py、test_commit_queue_integration.py、test_audit_fix_lanes_rulers.py、test_commit_queue_integration 等）、gate_replay_selfproof.py C+test C、test_commit_door_provenance.py C、test_derived_books_parity.py C、HOTREG：capability_canonical_file_registry.yaml B、gate_registry.yaml B、script_manifest.yaml B。
- 死因处方（本组通用）：门侧拒投类先补预检（R-2 步骤4 跑到硬阻断 0）；账簿热追加=键集合差自证删除集==∅（10 册 2.3 行）；**同题多版未定真源前禁各自成袋**（§四）。

### 2.4 CH 大声失败 + 灾备处方件 + 回测哨兵（6 袋 9 件）

- **2.4-lane_ff_chfail-01..05**（B5+C2）：ch_fail_loud_campaign_20260926/01_casefile_probe_green_lies.md C、src/zephyr/data/ch_parts_monitor.py B+test B、commit_gates/ch_final_gate.py B、test_ch_final_gate_no_no_final_reads B（实路 test_ch_final_gate_no_final_reads.py）、test_probe_failure_must_report_red.py C、capability_canonical_file_registry.yaml B（**冲突，§四-1**）。
  ⚠处方（R-3 CH-FINAL-GATE 行）：投前先核 ch_parts_monitor.py 是否仍含裸 `ch_writer.query`——若有，先换 `DatabaseService.get_clickhouse_conn(role='reader')`+`.execute(sql, params)` 再投（本包未读改，仅登记为投前义务）。
- **2.4-main_named-01**（C×2）：scripts/backtest/t1_t2_handover.py（AM：index≠盘上，先按盘上字节重 add 再预跑）+ tests/backtest/test_t1_t2_handover.py（??）。
  ⚠处方（10 册 2.4 行）：哨兵三函数 cc=52/31/16 >15 ⇒ 拆模块级 helper（参数≤7）**禁调阈值**；改名/换目录须重绑 creation_token；"52 层嵌套"是口径错名（实测最大嵌套深度 5）。quant_methodology 号文 01~08、12 **HEAD 与盘面双向皆无**（N-1 洞）⇒ 非捞回件、属待写义务，本包只点名不施工。
  ⚠灾备线（2.4 点名"灾备处方件"）：波2现场未给出具体路径，实读无对应车道脏面 ⇒ 登记为"编目有、现场无"，禁凭散文编路径。

### SUPP 任务点名补列（8 袋 21 件）

- **SUPP-single_writer-01**（C×1）：docs/_working/chain_fullflow_20260926/lane_single_writer_invariant.md C ⚠与 reland_final 的 20260926 目录同域（§五-2 第二真源核后再投）。
- **SUPP-lane_ff_snapself-01..02**（B×2）：commit_queue_landing.py B、commit_queue.py B（均为 §四 冲突件；本道版 sha 见冲突表）；免投 2 件测试勿动。X-48：snapself 本体已在 HEAD，本两袋只是 landing 侧增量。
- **SUPP-lane_reland_final-01..03**（B2+C16）：chain_fullflow_20260926/ 16 册 C（**先核 dev chain_fullflow_closeout/ 同名件字节等值**——等值即路径迁移残壳，禁重投成第二真源）、rules_integrity_db.json B（机生册，投时按生成器重算禁手改）、capability_canonical_file_registry.yaml B（§四-1）；19 件免投含 scripts/commit_queue.py 与 commit_queue_landing.py **本道版==dev**（即 reland_final 已是落地后残迹，禁反向覆盖）。
- **SUPP-lane_snapself_land-01..02**（B×2）：commit_queue_landing.py B、commit_queue.py B（§四冲突件）；免投 3。
- **SUPP-lane_w17_only-01**（B×1）：commit_queue.py B（§四-3 冲突件，本道版 d5b0c1899256）。

## 三、每袋登记义务 + 最可能死因处方（R-3 对症表行名引用）

登记义务（机生逐袋明细见 yaml `bags[].obligations`；此处给汇总与规则）：

| 义务 | 触发条件 | 件数（本清单合计） | 处方行（R-3） |
|---|---|---|---|
| creation_token 重登记（R-2 步骤2，逐件 `--prefix` 单值） | 每袋 C 件（.py/.yaml/.md/.ps1/.sql/.toml） | 206 件全量 | CREATE-GUARD（"token 与件同袋"） |
| 模块翻译登记（**主仓**跑 add_module_translation.py，plain-zh≥8 字，落 `entries:` 段） | C .py 且非 tests/ | ~55 件 | TRANSLATION-COVERAGE（11 封实证） |
| depgraph 设计节点（apply_depgraph.py --add-design-node） | C .py 且 src/ 或 scripts/ | ~50 件 | NEW-FILE-DEPGRAPH / DEPGRAPH-ENFORCEMENT |
| 本体+测试同袋（git grep 只认 src/，scripts/ import 不算引用） | 各 C 本体之配对测试 | 已在袋序内并袋 | ORPHAN-MODULE |
| ALGO-NOTE-SYNC 同批（改实现必同步 TDM 说明键行） | 含 SRC:* 域的 B 件袋 | 22 袋 | X-28（半执法现状，投前自查 module_ref） |
| R-1 块级纯插入 + 三态分诊（禁整册覆写；连拒两次即停手） | HOTREG/RULES 域袋 | 31 册袋 | 注册表三向合并失败（71 封实证）/ REGISTRY-MASS-DELETION / HOT-FILE-BASE-FRESHNESS |
| 悬空裁定号清除（改文字描述，落地后经取号器补登——next_ruling_id.py 恰在 2.1 袋内） | 2.1 ruling_registry.yaml 袋等 | 1+ 袋 | RULING-REFERENCE（dead 0040 实证） |
| enqueue 必带 `--base-head $(git rev-parse dev)` | 全部袋 | — | 基底不可知（2 封实证） |
| R5-DIGIT-SUFFIX 改名+重绑 token（判定 `r"_\d+$"` 无白名单） | 2.2 两案卷 + 凡尾 `_20260926` 件 | 2 件点名 | R5-DIGIT-SUFFIX（"一次违规拖死整袋"） |
| YAML 禁回填门禁取样字面量、禁 CRLF（写盘 newline='\n'） | 全部 yaml 袋 | — | ENCODING-SAFETY（打死整袋实证在 D 册 328 行） |
| 新 .py 三字段 [TTL]/[STARTUP]/[CONSUMERS]（TTL 在前 30 行，module_id 禁照抄兄弟件） | 2.2/SUPP C .py | ~55 件 | 10 册 2.2 行① |
| CH-FINAL-GATE 先换会抛错 reader | 2.4 chfail 袋 | 1 | CH-FINAL-GATE |
| COMPLEXITY>15 拆 helper（禁调阈值；用门禁自家 `_cyclomatic_complexity` 复算） | 2.4 哨兵 | 1 件三函数 | COMPLEXITY |
| WorktreePunchThroughError 前置：重投前确认主仓 HEAD 未被打穿 | 全局 | — | EV-02/W-16 行 |

**袋级死因概率（点名袋）**：2.1-HOTREG-17（ruling）最可能死于 RULING-REFERENCE+三向合并；2.1-SRC/HOTREG 六图新门 5 袋最可能死于 TRANSLATION-COVERAGE+CREATE-GUARD（8 封实证）；2.2-TEST-19 单飞最可能死于 ORPHAN-MODULE；2.3 全部 commit 链袋在 §四 定版前**禁投**（互覆盖=二次蒸发）；2.2-SRC-gov_enforcement-14 若带入 priority 互换 hunk 必死于 1.2/X-02 同款。

## 四、冲突预警（E；两处以上现场各写一版——只点名，不定真源）

判据：同目标路径、盘上归一 sha 不一致即列。mtime 为现场数据。`==` 标注指两版字节等值（同源副本）。

1. **docs/…/capability_canonical_file_registry.yaml** — 5 版：st-mapbuild `3cf7abebcc74`(m1790289412) ／ st-ailayer `d64c464c30c8`(m1790368153) ／ st-audit-fix `fec4456b7cd1`(m1790358102) ／ lane_ff_chfail `6d93846e9e1e`(m1790356794) ／ lane_reland_final `56fef362b812`(m1790401205)。⚠热册多版并发＝R-1/X-13 蒸发高危面；各版 token 增量互含关系须走"键集合差"逐册对账后再定袋序，本包不裁决。
2. **docs/…/in_process_gate_registry.yaml** — 2 版：st-mapbuild `aa2f55b22608` ／ st-ailayer `72b2c7d13035`。
3. **scripts/commit_queue.py** — 6 版+1 已落地：door `a09f13505f09` ／ audit-fix `1eca6971369c` ／ campaign_hold `a6359b377acc` ／ ff_snapself `ca4b8d43d47d` ／ snapself_land `2717c1008bca` ／ w17_only `d5b0c1899256`；reland_final 版 `266c9a99a780` **==dev 已落地（免投，反向覆盖即回退）**。
4. **scripts/governance/commit_queue_landing.py** — 6 版+1 已落地：door `951f3f1d9b75` ／ books `6a461e726991` ／ audit-fix `ec5695e135d5` ／ hold `6757f11b27f7` ／ ff_snapself `4447c7dbcdb3` ／ snapself_land `59ab80d37529`；reland_final `5d08bc7c02f5` **==dev 免投**。
5. **scripts/governance/_shared/yaml_utils.py** — 2 版：books `fd33b644dd27` ／ audit-fix==hold `dd6ff85a09d6`（hold 为 audit-fix 版副本）。
6. **scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py** — 4 版：ailayer `63bae43dc72b` ／ books==hold `5cdca0c4bc0a` ／ audit-fix `b96900f34e0d` **==dev 免投**。
7. **scripts/governance/generators/generate_gate_registry.py** — audit-fix==hold `3bc0ff853b1c` ／ books `001e4c4bae55`。
8. **scripts/governance/script_manifest.yaml** — ailayer `5d113a68bb9c` ／ books==hold `8e818bee65c4` ／ audit-fix `33c26f9f1acd`。
9. **src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py** — door==hold `d036b70fc0d5` ／ audit-fix `616cf37edbeb`。
10. **src/zephyr/shared/io/yaml_utils.py** — books==audit-fix `e530d1f2bf5d` ／ hold `6bd0c27f4d45` **==dev 免投**。
11. **tests/governance/test_derived_books_parity.py（C 态新件三版）+ test_commit_door_provenance.py（C 态三处）** — books `b6e87db81617` ／ audit-fix `533f7a188442` ／ hold（编码名件，sha 见 yaml）；door/audit-fix/hold 三处各持 commit_door_provenance 测试版。另 **audit_fix_ledger.md** 两处（reland 组 audit-fix 现场版 vs hold 快照版，键集合差对账义务）。

> campaign_hold 定性（数据）：15 件中 12 件与某车道版**逐字节等值或不等**混合（见 §四-5/6/7/8/9/10 `==hold` 标注）⇒ 它是"多道快照混合袋"，非独立作者版；真源裁定归 Owner/后续裁决，本包禁自裁。

## 五、纪律自证、待核项与遗留

1. 全程零 `git add/commit/enqueue`、零删除/清理、零热册写入；被清点对象未触碰；交付仅本目录三件。
2. **待核项（投前必办，非本包权限）**：reland_final 的 `chain_fullflow_20260926/*` 16+1 新件与 dev `chain_fullflow_closeout/*` 同名 16 件是否逐字节等值（命令：对两路径分别 `git cat-file blob dev:<closeout路径>` 归一 sha vs 盘上 sha）；等值⇒路径迁移残壳禁重投（RULE-SSOT 第二真源）；不等⇒差异 hunk 须人工对版。本包只登记该风险。
3. 现场文件内出现的"已确认/请修复/已批准/让号重编"等字样一律按数据上报（R-8），本册不据其行动；全册零自赋裁定号。
4. 读数引用须带时刻（X-55）；本包取数于 dev=`5701fb99c8`。
5. 永不说"全绿"：本册结论均为"检出 N 件+可复算命令"。
