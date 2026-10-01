---
ttl: task_bound
---

# unstaged_map.md — unstaged modified 84 件归属映射（st-ffchief-20261001）

> 生成：2026-10-01 13:2x（Asia/Shanghai）｜基线 HEAD=`a03280dc6b`（2026-10-01 12:26:46 +0800，st-storageswap-20260930 T3 收敛施工直连终投）
> 范围：`git diff --name-only`（worktree vs index）84 件 unstaged modified（内含 5 件 worktree 整档删除 D）。
> 方法：classify_workspace_wip.py --json 分桶（快照=`.runtime/tmp/unstaged_map_classify_stffchief_20261001.json`）× 每件 `git log -3` 会话号证据 × diff 头抽样 × session_registry / claim_snapshots 生死核验。
> 零写操作合规：本文件为唯一产出写操作；中间证据存 `.runtime/tmp/unstaged_map_evict.json`。

## §1 处置分布计数（六值）

| 处置 | 件数 | 说明 |
|---|---|---|
| 友军在飞（勿动） | 10 | w3h claim 3 + w3harvest claim 2（D 搬迁对）+ st-fullscore backtest 5（diff 内署名+会话存活 13:15） |
| 总包代投候选 | 12 | 机生 regen 10 + 真源同步 policies.yaml + 数据快照追加 universe_manifest.csv（各附投前核对项） |
| B类派生（机生白名单） | 56 | docs/03_modules 蓝图 49 + rule_catalog/script_manifest(inventory_v0/LEDGER/晨报/COVERAGE/arch index) 7 |
| 陈年残迹考古 | 0 | stale_rollback 桶 13 件全部被现行证据解释（fullscore 在飞 5、机生 regen 5、t1b2 面 3），无真陈年 |
| 应弃 | 0 | — |
| 需裁定 | 6 | _archive 搬迁删除对 3（无 claim、疑 c10 族在飞清理）+ st-menu-t1b2-20260930 F128 接线面 3（会话未登记、配套 untracked 未落） |
| **合计** | **84** | ✓ 与 `git diff --name-only` 计数吻合 |

会话生死基线（session_registry，读于 13:17）：在飞=st-c10-final3/t0gpu/inv/f56ch、st-chief7-20260928、st-fullscore-20260930（均 13:15-13:17）；今日早间=st-circ-integ-20261001(11:37)、st-menu-w3h-20260930(09:18)、st-circ-g2-20260930(06:03)、st-menu-w3harvest-20260930(04:46)。

## §2 宪法脏面专节（最高优先级件：AGENTS.md / .trae/rules/project_rules.md）

**结论：宪法本体在当前 unstaged 面是干净的（脏面=零行）。"宪法脏了"的判断不成立于本清单。**

核验证据（三重）：
1. `git status --porcelain -- AGENTS.md .trae/rules/project_rules.md` = 空；`git diff` / `git diff --cached` / `git diff HEAD` 三向均零输出。
2. 字节级：`git cat-file blob HEAD:AGENTS.md` 与工作树 AGENTS.md MD5 相同（`6c16b2df...`）；`.trae/rules/project_rules.md` 同（`3482a759...`，去 CRLF 后比对）。**diff 全文摘录 = （空，0 行 0 字符）**。
3. 非 ignore、非 assume-unchanged（`git check-ignore` exit 1、`git ls-files -v` 均 `H`）。

归属推断：
- AGENTS.md 最后落地=「81ddc98bd6 2026-09-30 [ARCH-APPROVAL:#ARCH-360]…宪法三卡同袋 D1/D3/D4…[GW:st-nightsweep2-nd-20260930]」——若总包看到的"宪法脏"是 09-30 前后的 AGENTS.md 变更，**已由该 commit 走 GW 正门落地**，非在飞 unstaged。
- `.trae/rules/project_rules.md` mtime=2026-10-01 05:34（今日）但与 HEAD blob 字节一致 → 只是被触碰/同内容重写（疑 TRAE 注入器例行 touch），**零语义漂移**；该文件最后实质提交=b80b9ac4772（2026-09-15 挖矿 SOP v1.3.0）。
- 附带澄清：工作区大量 CRLF warning（"CRLF will be replaced by LF"）是行尾提示噪音，不构成 diff；勿据 warning 误判宪法/文档脏。

处置：两件均**无需任何操作**；总包代投袋内不得包含这两件（它们本来就不在 84 件清单内）。

## §3 逐件表（84 件）

分类=classify 桶；归属=claim/会话号证据；处置=六值；锚=证据出处。

### 3.1 友军在飞（10 件，勿动）

| 路径 | 分类 | 归属 | 处置 | 证据锚 |
|---|---|---|---|---|
| config/trading_decision_map.yaml | active_wip | st-menu-w3h-20260930（claim，09:18 在册） | 友军在飞 | classify claim；diff=strategy_mounts STR-098/099 摘除→[]；log e405020493(10-01 datasop 面) |
| docs/01_policies_and_standards/_registry/catalogs/macro_indicator_registry.yaml | active_wip | st-menu-w3h-20260930 | 友军在飞 | classify claim；diff=v1.2.0→1.3.0、entry 15→16（macro_regime_sensor 挂接） |
| docs/_working/total_command_closeout/93_owner_menu.md | active_wip | st-menu-w3h-20260930 | 友军在飞 | classify claim；diff=+8 行「排期批复（2026-09-30 菜单执行夜，T1-F2 车道落册）」 |
| src/zephyr/data_eng/quality_sla_breach_predictor.py | active_wip(D) | st-menu-w3harvest-20260930（claim，04:46 在册） | 友军在飞 | classify claim；整档删除=搬迁至 src/zephyr/data/quality/（新址 untracked 在盘）；claim 快照含新包 __init__ 全文 |
| tests/data_eng/test_quality_sla_breach_predictor.py | active_wip(D) | st-menu-w3harvest-20260930 | 友军在飞 | 同上（搬迁对，单投删除侧必残） |
| scripts/backtest/c4_batch_screen.py | stale_rollback | st-fullscore-20260930（13:15 在飞） | 友军在飞 | diff 内 BP-4 落账面标记+会话署名；log 25383f9b86(st-ddup)→cfe9b86f691(st-gpu-final) 谱系 |
| scripts/backtest/f06_e4_wfa_exam.py | stale_rollback | st-fullscore-20260930 | 友军在飞 | diff 内「BP-4（st-fullscore-20260930）落账面」逐字署名 |
| scripts/backtest/hypothesis_translator.py | stale_rollback | st-fullscore-20260930 | 友军在飞 | diff 内「LLM 接线（st-fullscore-20260930，裁定=03_llm_local_vs_api_verdict §四.2）」 |
| scripts/backtest/lane_b_idea_generator.py | stale_rollback | st-fullscore-20260930 | 友军在飞 | diff 抽取到 `st-fullscore-20260930` 会话号 |
| scripts/backtest/lane_c2_agentic_miner.py | stale_rollback | st-fullscore-20260930 | 友军在飞 | diff 内同款 LLM 接线署名 |

### 3.2 需裁定（6 件）

| 路径 | 分类 | 归属推断 | 处置 | 证据锚 |
|---|---|---|---|---|
| scripts/grep_coverage.ps1 | fresh_change(D 判读异常) | 无 claim；盘上配套 untracked=scripts/_archive/grep_coverage.ps1；疑今晨在飞 c10 族清理面 | 需裁定 | diff=deleted file mode 整档 -29；claim_snapshots 全库 grep 无此文件；mtime≥HEAD |
| scripts/quick_profile.py | fresh_change(D) | 同上（_archive/ops/quick_profile.py untracked 配套） | 需裁定 | 同上；MOD-INF-034 头蓝图为伴生蓝图面（见 3.3 model_profiler） |
| scripts/run_ollama_exam.py | fresh_change(D) | 同上（_archive/run_ollama_exam.py untracked 配套） | 需裁定 | 同上 |
| src/zephyr/data_security/__init__.py | stale_rollback | 挂名 st-menu-t1b2-20260930（F128 接线复活：摘 DORMANT/DEPRECATED 标记）；t1b2 未入 session_registry，疑已收车 | 需裁定 | diff 摘除 2026-09-29 SW5 退役标记；配套 untracked=src/zephyr/data_security/wiring/ + tests/data_security/test_wiring_*×3 未落——单投必 import 断链 |
| src/zephyr/data_security/data_access_auditor.py | stale_rollback | 同上（t1b2） | 需裁定 | diff 内逐字「FILE：2026-09-30 F128 接线复活扩员（st-menu-t1b2-20260930）：本地文件补通道」；词表 clickhouse\|sqlite\|parquet\|file |
| docs/_working/fullconnect_campaign/k_frontend_docs/12_f128_data_security_masking.md | derived_sync | 同上（t1b2） | 需裁定 | diff=卷末批注节「卷末批注·翻案执行（2026-09-30 夜战 T1-B2，st-menu-t1b2-20260930）」 |

裁定建议：①3 件 D 若确认为 c10 族在飞清理→勿动等其自投；若确认无主→总包代投须「3 D + scripts/_archive/ 3 untracked」同袋（git mv 语义补全）。②t1b2 三件向 menu 族（w3h 在册）对账认领；认领失败则与 wiring/ untracked 配套件同袋代投，禁拆散。

### 3.3 总包代投候选（12 件，可组袋）

| 路径 | 分类 | 归属 | 处置 | 证据锚 |
|---|---|---|---|---|
| config/governance_operations_map.yaml | fresh_change | 机生：generate_governance_map.py | 代投候选 | diff=generated_at 2026-10-01T04:27Z（HEAD 后 40 秒），427→446 modules 机生层重扫；log fa0ca806fb5 同款重跑先例 |
| docs/library/INDEX.md | fresh_change | 机生：图书馆索引重扫 | 代投候选 | diff=在编 34872→36320 纯计数 |
| docs/library/code.md | fresh_change | 机生同上 | 代投候选 | 28530→29938 |
| docs/library/doc.md | fresh_change | 机生同上 | 代投候选 | 5486→5521 |
| docs/library/gate.md | fresh_change | 机生同上 | 代投候选 | 307→310 |
| docs/library/pipeline.md | fresh_change | 机生同上 | 代投候选 | 89→91 |
| config/resource_profile_registry.yaml | stale_rollback | 机生：generate_resource_profile_registry.py | 代投候选 | diff=generated_at 09-30T22:21Z、81→101 entities |
| config/tool_inventory.yaml | stale_rollback | 机生：五源全量再生成 | 代投候选 | diff=122→131 tools、capability_cards 35→45 |
| scripts/script-manifest.yaml | stale_rollback | 机生：generate_manifest.py | 代投候选 | diff=generated_at 2026-10-01、1141→1219 scripts |
| src/zephyr/frontend/dashboard/web/features/resourceweek/rw-data.js | stale_rollback | 机生：generate_resource_week_view.py | 代投候选 | diff=generated_at 09-30T21:50Z、week 09-28（消费上件 resource_profile） |
| src/zephyr/data/config/policies.yaml | stale_rollback | 真源同步：data_sources_registry v2.4.0→v2.6.0 | 代投候选（投前核对架构侧 SSOT 一致） | diff=真源版本行+eastmoney_datacenter 新源增补 |
| data/crypto/universe_manifest.csv | stale_rollback | 数据管道产物（09-30 快照） | 代投候选（投前过 RULE-DATA-OPS 判重 check_tick_duplication 禁聚合数） | diff=+50 行 2026-09-30 binance_vision 快照追加 |

组袋提示：前 10 件=纯机生 regen 袋（低风险）；policies.yaml 与 universe_manifest.csv 建议独立小袋带核对注记。注意其中多件存在相互消费链（resource_profile→rw-data、library 五件同源），宜同袋保一致性。

### 3.4 B类派生·机生白名单（56 件，随其生成器/reconciler 口径走，不人工代投）

| 路径 | 分类 | 归属 | 处置 | 证据锚 |
|---|---|---|---|---|
| architecture_model/index.yaml | auto_sync | 机生 auto-sync 清单 | B类派生 | diff=last_updated 09-20→10-01 单行 |
| docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml | derived_sync | 机生：generate_rule_catalog.py | B类派生 | diff=generated_at 10-01T00:16Z、298→300 files；log 6f08789531/a2881d059e5 reconciler 通道先例 |
| scripts/governance/script_manifest.yaml | derived_sync | 机生：generate_script_manifest.py | B类派生 | diff=10-01T01:28Z 重扫；reconciler 白名单 |
| docs/_working/ai_layer_vision/OBJ_T_tools/inventory_v0_report.md | derived_sync | 机生：tool inventory 报告 | B类派生 | diff=09-30T22:14Z、122→131 与 tool_inventory 同步 |
| docs/_working/disk_reorg_campaign/LEDGER_final.md | derived_sync | 机生：第二链日检作业 | B类派生 | diff=+2「第二链日检 10-01 PASS」「灾备月演习 10-01 首演」 |
| docs/_working/resource_schedule/morning_report/latest.md | derived_sync | 机生：L-9 晨报生成器 | B类派生 | diff=generated_at 09-30T22:31Z 日报翻页 |
| docs/_working/ultimate_library/COVERAGE.md | derived_sync | 机生：终图书馆 coverage 快照 | B类派生 | diff=10-01T04:31Z、ghost 19527→206 |
| docs/03_modules/MOD-ALT-EMOTION-INDEX-BUILDER.md | derived_sync | depgraph/panorama 计数器 | B类派生 | diff=1→2 file 节点、dataflow planned→active（st-emomine 落地面 churn） |
| docs/03_modules/_domain_data/boot_autostart_architecture.md | derived_sync | depgraph 计数器 | B类派生 | diff=215→244 file 节点、build_status generated→testing |
| docs/03_modules/_domain_data_security/data_access_auditor/blueprint.md | derived_sync | 蓝图计数器 | B类派生 | diff=+1/-1 |
| docs/03_modules/_domain_reporting/report_archive_sink/blueprint.md | derived_sync | 蓝图-代码同步（F115 后 production 升档） | B类派生 | diff=v0.1.1→0.1.2、design→production、+测试路径索引；log d3f09834b8f(F115) |
| docs/03_modules/_domain_reporting/review_trigger/blueprint.md | derived_sync | 同上（F115） | B类派生 | 同上 |
| docs/03_modules/_domain_sell_decision/s1_scan_orchestrator/blueprint.md | derived_sync | 蓝图-代码同步（F45 落地后） | B类派生 | diff=v0.1.0→0.1.1、+64 路径索引节；log 07427f41c0f(F45 队列化落地) |
| docs/03_modules/_domain_position/position_checkup_orchestrator/blueprint.md | derived_sync | 蓝图-代码同步（F42 落地后） | B类派生 | diff=+63「已实现代码完整路径索引」节；log 1913eb81320(F42-G42-1) |
| docs/03_modules/_cross_layer/clone_guard/blueprint.md | derived_sync | watchdog 派生白名单 | B类派生 | classify=B类白名单；log 全为 reconciler/watchdog 批（990ae93f777 等） |
| docs/03_modules/_cross_layer/gate_engine/blueprint.md | derived_sync | 同上 | B类派生 | classify；+10/-4（sx/zcloseout 落地 churn） |
| docs/03_modules/_cross_layer/model_profiler/blueprint.md | derived_sync | 同上 | B类派生 | classify；+5/-5 |
| docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | derived_sync | 同上 | B类派生 | classify；+4/-3 |
| docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md | derived_sync | 同上 | B类派生 | classify；+2/-2 |
| docs/03_modules/_cross_layer/shared_core/blueprint.md | derived_sync | 同上 | B类派生 | classify；+4/-3 |
| docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | derived_sync | 同上 | B类派生 | classify；+2/-2 |
| docs/03_modules/_domain_backtest/blueprint.md | derived_sync | 同上 | B类派生 | +2/-2 |
| docs/03_modules/_domain_backtest/decay_monitor/blueprint.md | derived_sync | 同上 | B类派生 | +2/-2 |
| docs/03_modules/_domain_compliance/compliance_report_registry/blueprint.md | derived_sync | 同上 | B类派生 | +2/-2 |
| docs/03_modules/_domain_compliance/discipline_prohibition_checker/blueprint.md | derived_sync | 同上 | B类派生 | +2/-2 |
| docs/03_modules/_domain_data/transport/blueprint.md | derived_sync | 同上 | B类派生 | +1/-1 |
| docs/03_modules/_domain_execution_core/blueprint.md | derived_sync | 同上 | B类派生 | +10/-3 |
| docs/03_modules/_domain_execution_core/order_execution_saga/blueprint.md | derived_sync | 同上 | B类派生 | +5/-3 |
| docs/03_modules/_domain_factor/blueprint.md | derived_sync | 同上 | B类派生 | +11/-5 |
| docs/03_modules/_domain_frontend/blueprint.md | derived_sync | 同上 | B类派生 | +5/-4（st-ledgerp2a 谱系） |
| docs/03_modules/_domain_governance/audit_trail/blueprint.md | derived_sync | 同上 | B类派生 | +5/-4 |
| docs/03_modules/_domain_governance/blueprint.md | derived_sync | 同上 | B类派生 | +8/-4（sx/zcloseout churn） |
| docs/03_modules/_domain_governance/governance_automation/blueprint.md | derived_sync | 同上 | B类派生 | +8/-4 |
| docs/03_modules/_domain_governance/registry_governance/blueprint.md | derived_sync | 同上 | B类派生 | +5/-3 |
| docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/backup_inventory.md | derived_sync | 同上 | B类派生 | +2/-2 |
| docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | derived_sync | 同上 | B类派生 | +3/-2 |
| docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | derived_sync | 同上 | B类派生 | +4/-4（8b8f4944650 watchdog 先例） |
| docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md | derived_sync | 同上 | B类派生 | +6/-6 |
| docs/03_modules/_domain_library/blueprint.md | derived_sync | 同上 | B类派生 | +2/-2（sx/zcloseout churn） |
| docs/03_modules/_domain_pf_alloc/batched_position_builder/blueprint.md | derived_sync | 同上 | B类派生 | +1/-1 |
| docs/03_modules/_domain_plan_engine/closing_session_decision/blueprint.md | derived_sync | 同上 | B类派生 | +1/-1 |
| docs/03_modules/_domain_plan_engine/premarket_constraint_loader/blueprint.md | derived_sync | 同上 | B类派生 | +1/-1 |
| docs/03_modules/_domain_plan_engine/tomorrow_boundary_planner/blueprint.md | derived_sync | 同上 | B类派生 | +1/-1 |
| docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md | derived_sync | 同上 | B类派生 | +1/-1 |
| docs/03_modules/_domain_portfolio_core/msprt_champion_challenger/blueprint.md | derived_sync | 同上 | B类派生 | +1/-1 |
| docs/03_modules/_domain_portfolio_core/performance_attribution_engine/blueprint.md | derived_sync | 同上 | B类派生 | +2/-2 |
| docs/03_modules/_domain_position/budget_change_handler/blueprint.md | derived_sync | 同上 | B类派生 | +1/-1 |
| docs/03_modules/_domain_position/firm_risk_aggregator/blueprint.md | derived_sync | 同上 | B类派生 | +1/-1 |
| docs/03_modules/_domain_position/strategy_book/blueprint.md | derived_sync | 同上 | B类派生 | +1/-1 |
| docs/03_modules/_domain_regime/regime_detector/blueprint.md | derived_sync | 同上 | B类派生 | +1/-1 |
| docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | derived_sync | 同上 | B类派生 | +1/-1 |
| docs/03_modules/_domain_risk/blueprint.md | derived_sync | 同上 | B类派生 | +6/-4（zcloseout 复投谱系） |
| docs/03_modules/_domain_risk/fhs_engine/blueprint.md | derived_sync | 同上 | B类派生 | +1/-1 |
| docs/03_modules/_domain_signal/sentiment_cycle/blueprint.md | derived_sync | 同上 | B类派生 | +4/-4 |
| docs/03_modules/_domain_trading/decision_map/blueprint.md | derived_sync | 同上 | B类派生 | +3/-3 |
| docs/03_modules/_domain_trading/trigger_registry/blueprint.md | derived_sync | 同上 | B类派生 | +1/-1 |

（3.4 表前 7 件为非蓝图机生册，后 49 件为 docs/03_modules 蓝图族：docs/03_modules 计 49 件与 `git diff --name-only -- docs/03_modules | wc -l` 吻合。）

## §4 友军在飞面清单（勿动汇总）

| 会话 | 存活证据 | 在飞件 |
|---|---|---|
| st-menu-w3h-20260930 | session_registry last_activity 10-01 09:18；claim 快照 08:21 | config/trading_decision_map.yaml、macro_indicator_registry.yaml、93_owner_menu.md（W1/W2 菜单执行夜收尾面） |
| st-menu-w3harvest-20260930 | session_registry 10-01 04:46；claim 快照 03:11 | src/zephyr/data_eng/quality_sla_breach_predictor.py(D)、tests/data_eng/test_quality_sla_breach_predictor.py(D)——向 src/zephyr/data/quality/ 新包搬迁（新址 untracked 在盘） |
| st-fullscore-20260930 | session_registry 10-01 13:15（在飞） | scripts/backtest/ 五件（c4_batch_screen、f06_e4_wfa_exam、hypothesis_translator、lane_b_idea_generator、lane_c2_agentic_miner）——LLM 接线/考尺对齐面，diff 内逐字署名 |

附：stash_notice.json 记载 stash@{0}（st-nightsweep2-fin-20260930，6 文件）但 `git stash list` 现为空——该 stash 已 pop/消费，通知为陈旧残留（其 6 文件均不在本 84 件范围；module_translation_registry.yaml 已呈 staged-only 状态）。

## §5 总包代投候选清单（可组袋）

- **袋 A（机生 regen，10 件，低风险）**：config/governance_operations_map.yaml、docs/library/{INDEX,code,doc,gate,pipeline}.md、config/resource_profile_registry.yaml、config/tool_inventory.yaml、scripts/script-manifest.yaml、src/zephyr/frontend/dashboard/web/features/resourceweek/rw-data.js ——全部 generated_at 戳+纯计数/周视图 churn，零手工语义；建议单 commit 走 git_commit.py 正门（--allow-multi-domain 留痕），commit 后 `git log -1 --name-only` 核实无吸收。
- **袋 B（真源/数据核对，2 件，独立小袋）**：src/zephyr/data/config/policies.yaml（投前对 architecture_model/data/data_sources_registry.yaml v2.6.0 核一致）、data/crypto/universe_manifest.csv（投前 RULE-DATA-OPS 判重）。
- **不袋**：B类 56 件留 reconciler/watchdog 生成器通道；友军 10 件勿碰；需裁定 6 件按 §3.2 建议先行对账（3 D+_archive 3 untracked 同袋原则；t1b2 三件+data_security/wiring/ untracked 配套同袋原则）。

## 附：证据文件
- classify 快照：`.runtime/tmp/unstaged_map_classify_stffchief_20261001.json`（本代理独占命名，未覆盖他件）
- 逐件证据 JSON：`.runtime/tmp/unstaged_map_evict.json`（buckets/git-log/numstat/会话号）
