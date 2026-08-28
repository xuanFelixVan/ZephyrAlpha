---
ttl: permanent
task_id: B-007
created: '2026-08-26'
owner_approval: 'Owner 2026-08-26 裁定全量转正（AI 施工资源 09-03 到期，须在此前完成转正，后续只跑验证）'
---

# B-007 全量模块转正 · 分批测试详细计划（2026-08-26）

> **定位**（doc_type=plan，EXEMPT-ZONE-FM 合规自 frontmatter 下移）：B-007（宪章：production 启用属 Owner 审批）全量转正的执行计划。Owner 已批准全量转正，
> 本计划把 depgraph 当前 `build_status=testing/stable` 的全部节点分 6 批转正到 `production`。
> **本文件只做盘点+计划，不执行任何状态迁移。**
> **快照口径**：本文数字为 2026-08-26 PG depgraph 活库快照；DIGEST P2 波次当日仍在飞（#ARCH-255/256/259 持续落地），
> 执行日必须按 §9.0 重新生成清单（脚本已备好），不得以本文静态数字为准。

---

## 0. 一句话方案

**先做一个一次性 Owner 窗口前置批（P0：build_status 词表 5→6 态 +production 的 schema/状态机/文档扩展），
再按"风险从低到高+依赖拓扑"分 6 批执行：数据/契约/基础设施 → 信号/因子 → 回测/组合/风控 → 执行/交易链路 → 治理/安全 → AI 层；
每批过三道门禁（相关测试全绿 → 全量 sweep 零新增红 → 适用批回测冒烟），用 `--transition-build-status` 两步法
（testing→stable→production）逐节点转正，批前快照、批后观察 24h。**

---

## 1. 全量盘点摘要（快照：2026-08-26）

**总量：2682 节点（testing=305，stable=2377），横跨 59 个域。**
另有 design_maturity=design 的节点 7 个在 testing（蓝图/目录粒度，见 §4.7 待裁定项）。
全量明细：`.runtime/b007_inventory.tsv`（2682 行：node_id/域/状态/蓝图号/路径/推断测试/测试数）、
`.runtime/b007_inventory_classified.json`（含建成批次归属）、`.runtime/b007_batches.json`（按转正批次分组）。

### 1.1 按建成批次分组

| 建成批次 | testing | stable | 合计 | 说明 |
|---|---:|---:|---:|---|
| 长城批（GP0+阶段二/三，08-21~23） | 84 | 205 | 289 | GP0 AI 层新件+44号文 M1/M2/M3+审查清单件+P0 总账批；6 节点已于 08-22 转 stable（tracker #257） |
| DIGEST P0（08-25，W1a~W3） | 0 | 34 | 34 | #ARCH-220~228；35 建成（1 件为既有文件增量，并入存量计） |
| DIGEST P1（08-25，R1~R7） | 0 | 105 | 105 | #ARCH-230~254：R1=19/R2=15/R3=16/R4=17/R5=18/R6=15/R7=5 |
| DIGEST P0/P1 配套测试节点（08-25） | 113 | 1 | 114 | 上两批模块的 tests/ 套件节点（多数落 D_AUDITTEST 及源域） |
| DIGEST P2（08-26，W01~W03+，**在飞**） | 89 | 38 | 127 | #ARCH-255/256/259：infra_runtime/infra_ops/knowledge/data_security 等新包；**执行前必须封波** |
| 存量（早于 08-21 的既有模块） | 19 | 1994 | 2013 | 前期已 stable 的老件为主体；19 个 testing 存量名单见 §4.8 |
| **合计** | **305** | **2377** | **2682** | |

> 批次归属方法：源码节点按 #ARCH-218~259 impact 清单精确路径匹配 + git 首次加文件日期兜底；
> tests/ 节点按目录归入源域批次。归属脚本：`.runtime/_b007_classify.py`（可重跑）。
> 注：DIGEST P0/P1 源模块已是 stable——08-25 后 depgraph 重生成器按"production+有测试→stable"机械推导自动晋升
> （`generate_project_depgraph.py::upgrade_tested_modules`），非人工转态。

### 1.2 按域分组（testing+stable 合计 Top 20）

| 域 | testing | stable | 合计 |
|---|---:|---:|---:|
| D_GOV_CODE_QUALITY | 0 | 163 | 163 |
| D_AUTONOMY_CORE | 9 | 145 | 154 |
| D_INFRA_RUNTIME | 11 | 141 | 152 |
| D_SHARED | 7 | 131 | 138 |
| D_AUDITTEST（测试套件域） | 127 | 1 | 128 |
| D_GOVERNANCE | 3 | 117 | 120 |
| D_FEEDBACK_LOOP | 0 | 110 | 110 |
| D_ASHARE_SIGNAL | 15 | 91 | 106 |
| D_SECURITY | 1 | 105 | 106 |
| D_DATA | 36 | 70 | 106 |
| D_GOV_AUDIT | 1 | 82 | 83 |
| D_GOV_OPS_RESILIENCE | 0 | 82 | 82 |
| D_GOV_DRIFT | 0 | 69 | 69 |
| D_FBL_DIAGNOSERS | 0 | 69 | 69 |
| D_FBL_VERIFICATION | 0 | 67 | 67 |
| D_FBL_DETECTORS | 0 | 60 | 60 |
| D_ORCHESTRATOR | 1 | 56 | 57 |
| D_RISK | 10 | 54 | 64 |
| D_EX_CORE | 0 | 48 | 48 |
| 其余 39 域 | 见 `.runtime/b007_inventory.tsv` | | |

> 完整 59 域明细见 TSV 与 `.runtime/b007_inventory.json::by_domain`。

### 1.3 测试覆盖推断

- 2088/2682 节点可推断出测试文件（路径启发式：`src/zephyr/<pkg>/foo.py` → `tests/<pkg>/test_foo.py`
  或 `tests/zephyr/<pkg>/test_foo.py`，失败再按文件名全局匹配），合计覆盖 **40,704 个测试用例**（`def test_*` 计数）。
- 594 节点未推断出测试：多为 `__init__.py`、docs/config/scripts 节点、目录粒度 design 节点及扫描衍生节点——
  其验证由全量 sweep（§5.2）兜底，不单独阻断。

---

## 2. 关键机制发现（决定整个方案形态）

**当前 depgraph 没有 `production` 这个 build_status。** 三层实证：

1. **DB CHECK 约束**（活库 `pg_constraint` 实测）：
   `nodes_build_status_check = CHECK (build_status IN ('planned','generated','testing','stable','deprecated'))`——写入 'production' 会被直接拒绝。
2. **状态机**：`apply_depgraph.py::transition_build_status` 合法转换仅
   `planned→generated / generated→testing / testing→stable / stable→deprecated`（裁定#178-183，单调推进禁跳态）。
3. **全景同步链**：`--transition-build-status` 成功后自动调 `sync_module_panorama`（ARCH-056），
   把 build_status UPSERT 进 `dataflow_jobs` 与 `decision_layers`——这两张表的 CHECK 同样只有 5 态，
   不同步扩展会在同步环节炸 CHECK。

**结论**：Owner 的"全量转正"要落地，必须先做一次 **schema 变更前置批（P0）**——这正是本计划 §3。
先例完备：#251（2026-08-22 Owner 窗口）domains.build_status 词表 5→6 态 +dormant，
走 `--fix-domains-build-status-vocab`（superuser DDL，先例 `migrations/add_acquisition_fields.py`）。

**有利机制**（复用即可，不要新造）：

- 重生成器状态保护：`generate_project_depgraph.py` 的 `[STATUS-PRESERVE]` 快照/恢复逻辑
  （L3597-3604 快照 + L3976-3986 恢复）保护 `testing/stable/deprecated` 不被全量重扫回退——
  **P0 词表扩展时必须把 `'production'` 加入这两处保护名单**，否则下一次 depgraph 重生成会把全部转正成果静默回滚成 stable/generated。
- 写入即自动备份：`apply_depgraph.py` 任何写入命令后自动 `backup_pg_architecture()`（节流 60s，保留 10 份，
  落 `tmp/runtime_backups/`）——回滚有基点。
- 生产环境写入守卫：`ZEPHYR_ENV=production` 时写入命令需 `ZEPHYR_DEPGRAPH_WRITE_ACK=1`（5.34.6 is_prod 守卫）。
- 既有 B-007 转态先例：tracker #257（2026-08-22）6 节点 `--transition-build-status` testing→stable 全 OK。

---

## 3. 前置批 P0：build_status 词表 5→6 态（一次性，Owner 窗口）

> 性质：schema 变更 + 代码/文档同步，**必须先于一切转正批次**。预计 0.5 个工作日。
> 授权：Owner 2026-08-26 全量转正裁定已含此隐含前置；执行前建议向 Owner 明示确认一次（DDL 属 superuser 窗口操作）。

### 3.1 DDL（superuser=postgres，先例 #251）

在 `apply_depgraph.py` 新增 CLI `--fix-nodes-build-status-vocab`（仿 `cmd_fix_domains_build_status_vocab`，L3597-3642），
对 **5 张表** 幂等扩展 CHECK（已含 'production' 则跳过）：

```sql
-- nodes（主目标）
ALTER TABLE nodes DROP CONSTRAINT nodes_build_status_check;
ALTER TABLE nodes ADD CONSTRAINT nodes_build_status_check
  CHECK (build_status IN ('planned','generated','testing','stable','deprecated','production'));
-- dataflow_jobs / decision_layers（ARCH-056 全景同步目标，必须同步扩展）
ALTER TABLE dataflow_jobs DROP CONSTRAINT dataflow_jobs_build_status_check;
ALTER TABLE dataflow_jobs ADD CONSTRAINT dataflow_jobs_build_status_check
  CHECK (build_status IN ('planned','generated','testing','stable','deprecated','production'));
ALTER TABLE decision_layers DROP CONSTRAINT decision_layers_build_status_check;
ALTER TABLE decision_layers ADD CONSTRAINT decision_layers_build_status_check
  CHECK (build_status IN ('planned','generated','testing','stable','deprecated','production'));
-- dataflow_datasets / decision_nodes / decision_edges（词表一致性，建议同批；sync 不写它们，但防手工写炸 CHECK）
ALTER TABLE dataflow_datasets DROP CONSTRAINT dataflow_datasets_build_status_check;
ALTER TABLE dataflow_datasets ADD CONSTRAINT dataflow_datasets_build_status_check
  CHECK (build_status IN ('planned','generated','testing','stable','deprecated','production'));
ALTER TABLE decision_nodes DROP CONSTRAINT decision_nodes_build_status_check;
ALTER TABLE decision_nodes ADD CONSTRAINT decision_nodes_build_status_check
  CHECK (build_status IN ('planned','generated','testing','stable','deprecated','production'));
ALTER TABLE decision_edges DROP CONSTRAINT decision_edges_build_status_check;
ALTER TABLE decision_edges ADD CONSTRAINT decision_edges_build_status_check
  CHECK (build_status IN ('planned','generated','testing','stable','deprecated','production'));
```

验证（只读）：
```powershell
python .runtime/_b007_constraint_scan.py   # 全部 6 行应含 'production'
```

### 3.2 状态机代码修改（`scripts/governance/apply_depgraph.py`）

1. `transition_build_status` 的 `valid_transitions` 增加 `("stable", "production")`（**不加** testing→production，
   保持单调不跳态——testing 节点走两步法，见 §6.1）。同步更新 docstring 转换规则注释（L1689-1695）。
2. `generate_project_depgraph.py` 两处 `[STATUS-PRESERVE]` 名单
   （L3602 快照 SQL 与 L3590 注释）：`IN ('testing','stable','deprecated')` → `IN ('testing','stable','deprecated','production')`。
   **漏此步 = 下次重生成全部回滚，本前置批最高风险点。**
3. `apply_depgraph.py` 头部 §12.6 引用注释（L1019/L1055 的 5 态表述）与 `valid_status` 集合（L1055）同步加 'production'
   （`# noqa: gate-vocab` 注释同步改 6 态口径）。

### 3.3 SSoT 文档/词表同步（Grep 命中清单，全改）

- `src/zephyr/governance/depgraph_schema.py`：L279/L404/L609 三处 nodes CHECK DDL 模板
- `src/zephyr/governance/persistence/decisiongraph_schema.py`：L179/L215/L246 CHECK + L42/L94/L301-303 注释
- `scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql:252`、`03_create_dataflow_schema.sql:35/61`、`03_create_decision_schema.sql:55/86/107/129`
- `docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml`（L61/101/148 词表段）
- `docs/01_policies_and_standards/rules/trae_061_decisiongraph_access_protocol.yaml:78`（状态机表述）
- `docs/01_policies_and_standards/sop/construction_workflow_sop.md:462`
- `docs/01_policies_and_standards/_registry/catalogs/terminology_glossary.yaml:22`
- `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml:287`（追加 6 态演进注记，不改历史裁定原文）
- `docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/dependency_path_panorama.md`（§12.6，L254/275/281/443/839/845）
- `scripts/governance/apply_decisiongraph.py`（L45/176/770）与 `apply_dataflowgraph.py`（L305）的 5 态注释
  ——**只改注释词表；decision/dataflow 两图的 transition 函数本体是否开放 stable→production 属另案裁定，B-007 不动**
- `scripts/governance/d5_architecture/validators/lifecycle/validate_module_lifecycle.py` 等生命周期校验器：
  执行时先 `Grep "planned.*generated.*testing.*stable"` 复扫一遍，凡枚举 5 态的校验器同步加 'production'

### 3.4 P0 验收门禁

1. `python .runtime/_b007_constraint_scan.py` → 6 表 CHECK 全含 'production'
2. 单点试转：任选 1 个 stable 节点 `--transition-build-status <id> production`，再 §7 回滚恢复——验证状态机+CHECK+全景同步三链全通
3. `python scripts/governance/extract_depgraph.py --summary` 正常；`python scripts/governance/run_all.py --diff-ref HEAD~1` 零新增阻断
4. depgraph 全量重生成空转验证（证明 STATUS-PRESERVE 生效）：
   `python scripts/governance/generate_project_depgraph.py --output-db depgraph` 后试转节点状态仍为 production

---

## 4. 转正批次划分（6 批，风险从低到高+依赖拓扑）

排序逻辑：数据层/契约层先行（被依赖最多、断链影响面最大但交易风险最低）→ 信号/因子（消费数据层）→
回测/组合/风控（消费信号）→ 执行/交易链路（B-007 风险最高面，最后）→ 治理/安全（元设施，依赖全库状态稳定）→
AI 层（自治/ML/知识，依赖治理层门禁就位）。测试套件节点（D_AUDITTEST 及 tests/ 路径）**随源域批次**同步转正。

| 批次 | 范围 | 域清单 | testing | stable | 合计 |
|---|---|---|---:|---:|---:|
| **批1** 数据+契约+基础设施 | L0/L1 地基 | D_DATA, D_DATA_ENG, D_DATA_GOV, D_DATA_SEC, D_MKT_DATA, D_CONTRACTS, D_SHARED, D_INTEGRATION, D_INTEGRATION_GATEWAY, D_INFRASTRUCTURE, D_INFRA_A2A, D_INFRA_RUNTIME, D_INFRA_TELEMETRY, D_INFRA_OPS, D_INFRA_RECOVERY + tests/data*/tests/zephyr/data/tests/market_data | 82 | 542 | **624** |
| **批2** 信号+因子 | 策略信号面 | D_ASHARE_SIGNAL, D_FACTOR, D_FUNDAMENTAL_SIGNAL, D_ALT_DATA, D_SIGQC + tests/signal_ashare/tests/factor/tests/alt_data/tests/signal_fundamental/tests/signal_quality | 63 | 153 | **216** |
| **批3** 回测+组合+风控 | 决策中枢 | D_BACKTEST, D_SIMULATION, D_PF_ALLOC, D_PF_CORE, D_POSITION, D_PLAN, D_REGIME, D_RISK + tests/backtest/tests/pf_core/tests/pf_alloc/tests/position/tests/plan_engine/tests/regime/tests/risk/tests/simulation | 47 | 206 | **253** |
| **批4** 执行+交易链路 | B-007 最高风险面 | D_EXEC_SIM, D_EX_CORE, D_EX_SOR, D_TRADING, D_SELL_DECISION, D_FRONTEND + tests/ex_core/tests/ex_sor/tests/boundary/tests/trading/tests/sell_decision/tests/frontend/tests/task | 11 | 143 | **154** |
| **批5** 治理+安全+合规 | 元设施 | D_GOVERNANCE, D_GOV_AUDIT, D_GOV_CODE_QUALITY, D_GOV_DRIFT, D_GOV_ENFORCEMENT, D_GOV_OPS_RESILIENCE, D_GOV_REPAIR, D_GOV_RULE, D_GOV_SCRIPTS, D_COMPLIANCE, D_SECURITY, D_SECURITY_LLM + 治理向 tests/ 余量 | 14 | 718 | **732** |
| **批6** AI 层 | 自治/ML/知识/反馈 | D_AUTONOMY_CORE, D_AUTONOMY_PERM, D_ORCHESTRATOR, D_INTELLIGENCE, D_ML_SERVE, D_ML_TRAIN, D_NLP, D_KNOWLEDGE, D_REPORTING, D_DIGITAL_TWIN, D_FEEDBACK_LOOP, D_FBL_DETECTORS, D_FBL_DIAGNOSERS, D_FBL_VERIFICATION, D_OPS + tests/autonomy_core/tests/intelligence/tests/ml_train/tests/ml_serve/tests/nlp/tests/knowledge/tests/research/tests/ce 及 P2 新包 tests | 88 | 615 | **703** |
| | **合计** | | **305** | **2377** | **2682** |

每批的节点级清单（node_id+域+路径+蓝图号+推断测试）：`.runtime/b007_batches.json`；
纯 node_id 列表：`.runtime/b007_manifests/batch{N}_testing_node_ids.txt` / `batch{N}_stable_node_ids.txt`。

### 4.1 批1（624）构成亮点
长城批 25（数据专项/SEC-01/02/M1-④）+ DIGEST P0 12（storage_tiering/cleaning/data_service/failover 等）+
DIGEST P1 22（format_transformer/sina_tencent/announcement/auto_backfiller/reference_data_manager/lineage 族/ctr002 契约对等）+
DIGEST P2 72（infra_runtime/infra_ops/data_governance/data_security/shared 新包，**在飞**）+ 存量 461 + 长城批存量混合。

### 4.2 批2（216）构成亮点
DIGEST P1 信号族 39（MOD-SIG-087~109 五波）+ 因子族（factor_factory/wq_alpha_87/bma/ufl/offline_store）+
长城批 75（sector_divergence/sector_leader/mainline/lhb/futures_basis/option_sentiment/similar_day/market_sentiment 等 44号文族）+
配套测试 39 + 存量 59。

### 4.3 批3（253）构成亮点
DIGEST P0 风控 10（MOD-RK-28~37 两波）+ DIGEST P1 19（strategy_cpcv_matrix/scenario_playbook/track_fusion/
position_adjudication_center/core_satellite/cash_manager/calendar_constraint/factor_exposure/manipulation/post_entry/
funnel_adjudicator/exposure_manager/capacity_estimator/strategy_factory）+ 长城批 55（index_regime_panel/cross_sectional/
boundary_revision/overnight_reviser/scenario_planner/llm_premarkat 等）+ 存量 143。

### 4.4 批4（154）构成亮点
长城批 30（premarket_checker 接线 boot_hooks/commit_queue 相关 trading 件/eod 族）+ DIGEST P0 2
（strategy_abnormal_exit_orchestrator/premarket_checker）+ DIGEST P1 6（eod_processor/manual_instruction_channel/
trading_order_aggregate/settlement_record_aggregate/sor_agent/alert_center）+ 存量 108 + P2 在飞 6（strategy_canary_release 等）。

### 4.5 批5（732）构成亮点
几乎全部存量 stable（702）——governance/gov_enforcement/gov_drift/gov_audit/security 等治理面老件；
testing 仅 14（threshold_split_detector/key_hierarchy/agents_cheatsheet_reconciler 等及治理向测试）。

### 4.6 批6（703）构成亮点
存量 537（autonomy_core 110/intelligence/reflexion/model_profiling/feedback_loop 305 等）+
长城批 84（CE 39 文件/evidence 4 件/agents 4 入口/reflexion/kill_switch_orchestrator/autonomy_boundary_gate 等 GP0 族）+
DIGEST P1 19（api_llm_pool/llm_market_interpreter/llm_fundamental/agent_memory/llm_agent_router/episodic/
local_llm_pool/non_ai_boundary_guard/ai_ops_card/model_version_registry/qnn/patchtst/model_drift_monitor/layered_command_chain）+
P2 在飞 42（knowledge 14 件等）。

### 4.7 待裁定项：design_maturity=design 的 7 节点
`src/zephyr/data/connectors/`（MOD-L00-005）、`src/zephyr/data/normalizers/`（MOD-L00-006）、
`src/zephyr/intelligence/model_routing/`（MOD-MODEL_ROUTER_ORCH）、`src/zephyr/ml_train/{ai_operator,training_dataset_manager,training_pipeline}/`（MOD-ML-001/002/003）、
`tests/ml_train/test_density_quantile_trainer.py`（MOD-ML-DENSITY）。
这些是蓝图/目录粒度 design 节点（非物理文件），其 build_status 语义是"设计生命周期"。
**建议：不随 B-007 转 production，维持 testing；其物理实现文件已在各批覆盖。** 执行前请 Owner 一句话裁定。

### 4.8 存量 testing 19 节点名单（逐一审定后随批转正）
MOD-NLP-PIPELINE 族 5（scripts/ml/{accept_nlp_pipeline,run_sentiment_batch,run_sft_train}.py + tests/scripts 2 件）、
MOD-REGIME-P2-E8 族 2（scripts/scan_forward_days.py + tests/scripts/test_scan_forward_days.py）、
MOD-REGIME-002 s2 测试 5（tests/regime/features/test_s2_*.py）、tests/risk/test_daily_auditor_var_backtest.py、
以及 §4.7 的 7 个 design 节点。除 design 节点外 12 件均为正常代码/测试节点，随其域批次两步法转正。

---

## 5. 每批验证门禁（三道，全过才转态）

### 5.1 门禁一：批内相关测试全绿

从 `.runtime/b007_batches.json` 提取该批 `inferred_tests` 并集（脚本已含），串行跑：

```powershell
# 生成批 N 测试清单（PowerShell）
python -c "import json;d=json.load(open('.runtime/b007_batches.json'));ts=sorted({t for n in d['<N>'] for t in n['inferred_tests']});open('.runtime/b007_manifests/batch<N>_tests.txt','w').write('\n'.join(ts))"
# 执行（串行 -n 0，对齐 sweep 拓扑纪律；结果留档）
python -m pytest -n 0 -q --tb=short -rf -p no:cacheprovider --color=no (Get-Content .runtime/b007_manifests/batch<N>_tests.txt) | Tee-Object .runtime/b007_manifests/batch<N>_pytest.txt
```
通过线：**零 failed/errors**（存量 flake 单文件 standalone 复跑绿可豁免，豁免项记入批次报告）。

### 5.2 门禁二：全量 sweep 一轮零新增红

复用 AI-RESIDUAL-001 实证设施（拓扑纪律：簇内串行 -n 0、三桶 LPT 负载均衡）：

```powershell
python .runtime/test_sweep/_plan.py                                   # 重新分簇生成 manifest_A/B/C
python .runtime/test_sweep/sweep_runner.py .runtime/test_sweep/manifest_A.txt
python .runtime/test_sweep/sweep_runner.py .runtime/test_sweep/manifest_B.txt
python .runtime/test_sweep/sweep_runner.py .runtime/test_sweep/manifest_C.txt
python .runtime/test_sweep/_aggregate.py                              # 汇总 results/*.txt
```
通过线：**较基线零新增红**。基线锚 = 转正版首轮执行前先跑一轮全量 sweep 作为 B-007 基线
（历史锚：2026-08-21 基线 49 项分簇口径，清单 `.runtime/_b5_failed_list.txt` + AI-RESIDUAL-001 结案口径；
xdist worker 崩溃/WMI 假死族按 #ARCH-XDIST-WORKER-CRASH-001 豁免口径处理，standalone 复跑绿即核销）。
预计耗时：三桶串行约 3-6h（可三进程并行，见 §9）。

### 5.3 门禁三：回测冒烟（仅批3/批4 适用）

批3（回测/组合/风控）与批4（执行/交易链路）转态后各跑一次 57 号文 §4 向量化日频冒烟：

```powershell
python -c "import sys;sys.path.insert(0,'src');from zephyr.pf_core.strategy_engine.strategy_runner import StrategyRunner,StrategyRunnerConfig;from zephyr.backtest.io.backtest_result_sink import sink_backtest_result;from zephyr.backtest.io.result_repository import build_artifact_from_data,save_artifact;r=StrategyRunner().run_backtest(['600519','000001'],'2026-05-26','2026-08-26',StrategyRunnerConfig(strategy_id='topn-momentum',factor_ids=('momentum_20d',),rebalance_freq='W',top_n=2));p=save_artifact(build_artifact_from_data(sink_backtest_result(r)));print(p)"
```
通过线：进程 exit 0 + artifact JSON 落盘 `data/backtest_artifacts/{run_id}.json`（对照 P0-5 彩排先例 trades/return 字段非空）。
批4 追加交易会话冒烟：`python scripts/tests/smoke_test_trading_session.py`（mock 信号、限价不成交设计，零实盘风险）。

---

## 6. 每批 depgraph 状态迁移操作

### 6.1 两步法（保持单调状态机不跳态）

- 该批 **testing** 节点：先 `testing→stable`（既有合法边），再 `stable→production`（P0 新边）
- 该批 **stable** 节点：直接 `stable→production`

### 6.2 执行命令（每批同一套路，N=批次号）

```powershell
# 0. 前置确认：P0 已完成（§3.4 四项验收过）+ 本批三道门禁全绿（§5）
# 1. 批前快照（回滚基点；已随计划生成，执行日需按 §9.0 重新生成）
python .runtime/_b007_emit_manifests.py
# 2. 手动触发一次架构库备份（双保险，事件触发备份之外的显式基点）
python scripts/governance/meta/backup_runtime_state.py
# 3. 生产环境写入确认（dev 环境可省）
$env:ZEPHYR_DEPGRAPH_WRITE_ACK = "1"
# 4a. testing 节点第一步：testing→stable（逐节点，带 ARCH-056 全景自动同步）
foreach ($id in (Get-Content .runtime/b007_manifests/batch<N>_testing_node_ids.txt)) {
  python scripts/governance/apply_depgraph.py --transition-build-status $id stable
}
# 4b. 全部节点（testing 已转 stable 的 + 原 stable）：stable→production
foreach ($id in (Get-Content .runtime/b007_manifests/batch<N>_testing_node_ids.txt)) {
  python scripts/governance/apply_depgraph.py --transition-build-status $id production
}
foreach ($id in (Get-Content .runtime/b007_manifests/batch<N>_stable_node_ids.txt)) {
  python scripts/governance/apply_depgraph.py --transition-build-status $id production
}
# 5. 批后核验（应输出：本批 production=批总量，testing/stable=0）
python .runtime/_b007_verify_batch.py <N>     # 脚本见 §9.0，执行日生成
# 6. 全景一致性核验（WARN 可接受，ERROR 需归账）
python scripts/governance/d5_architecture/generators/align_all.py --no-report
```

说明：
- **不用 `--batch`**：batch 的 `update` op 直写字段、绕过 transition 合法边校验，且不触发逐节点 ARCH-056 全景同步
  （`--transition-build-status` CLI 分支才挂 `_sync_panorama_after_transition`）。逐节点循环保留完整合规链。
  单节点约 1-2s，最大批（批5，732）约 25-45 分钟可接受。
- 每次写入自动触发 `backup_pg_architecture`（60s 节流），并在 stderr 打 `[OK] node_id=...` 留痕；
  建议 `Tee-Object` 落 `.runtime/b007_manifests/batch<N>_transition.log`。
- design 节点（§4.7）不在清单内，无需操作。

### 6.3 批次顺序与依赖

严格按 批1→批2→批3→批4→批5→批6 串行；每批：门禁（§5）→ 转态（§6.2）→ 监控期（§8）→ 下一批。
**批4（交易链路）建议单独约 Owner 窗口执行**（B-007 最高风险面，与 57 号文 SOP 交易日错峰，收盘后跑）。

---

## 7. 回滚方案（单批粒度）

### 7.1 手术式回滚（首选）：按批前快照反向 UPDATE

状态机单调无逆向边，回滚不走 CLI，用快照直接恢复（快照文件 = `.runtime/b007_manifests/batch<N>_pre_snapshot.json`，
执行日由 `_b007_emit_manifests.py` 重新生成）：

```powershell
# 生成/复用回滚脚本（只恢复 batch<N>_pre_snapshot.json 里登记过的 node_id）
python .runtime/_b007_rollback_batch.py <N>     # 脚本见 §9.0；逻辑=逐行 UPDATE nodes SET build_status=<快照值> WHERE node_id=<id>
# 回滚后同步全景（对齐数据流/决策图）
python scripts/governance/d5_architecture/generators/align_all.py --no-report
# 核验：本批节点 build_status 分布应回到快照值
python .runtime/_b007_verify_batch.py <N>
```
注意：快照 JSON 同时是**防越权护栏**——回滚脚本必须只 UPDATE 快照内 node_id，禁止全表扫。
回滚后该批打"回退"标记，问题修复后按 §6 重跑该批（production 节点已含在快照里，重转无重复副作用）。

### 7.2 核选项（整库恢复，仅在手术式失效时）

- 数据面：`tmp/runtime_backups/` 取批前最近一份 `backup_pg_architecture` 快照（保留 10 份），
  按 `tests/dr/test_restore_from_backup.py` 的恢复路径回灌；或 pg_dump/PITR（DR 真源 `config/dr_policy.yaml`）。
- 代码面：P0 前置批的代码改动（状态机/SSoT 文档）走 git revert；DDL 扩展可保留（词表扩大无害，无节点引用即空集）。

### 7.3 回滚触发判据（任一命中即回滚该批）

- 批后 24h 监控期内 reconciler `critical_warn` 未消音增量 > 0 且归因指向该批节点
- 批后全量 sweep 出现可归因该批的新增红（standalone 复跑仍红）
- 回测冒烟（批3/4）失败或 artifact 缺关键字段
- 调度器关键任务（kline_daily_incremental/stk_limit_premarket/post_settlement）连续 2 次非环境因失败

---

## 8. 监控期安排（每批转态后 24h 观察窗）

| 观察项 | 命令/位置 | 通过线 |
|---|---|---|
| reconciler critical_warn 增量 | 查治理库：`sqlite3 data/databases/governance.db "SELECT gate_id,COUNT(*) FROM reconcile_execution_log WHERE action='critical_warn' AND logged_at > '<批转态时刻>' AND acknowledged_at IS NULL GROUP BY gate_id"`（治理库路径真源=DB_PATH，tracker #234 口径） | 增量=0（或全部可归因环境族并已 ack） |
| commit 网关 banner | 下次任意 commit 时 `_print_critical_warn_banner` 不浮现新告警 | 无新增 banner |
| 调度器任务成功率 | `python -m zephyr.data status`（57号文 §1 C2 口径）：kline_daily_incremental/stk_limit 系 SUCCESS | 关键任务无连续失败 |
| 数据质量门禁 | `python scripts/ch/_data_inventory.py`（关键表 min/max 新鲜度）+ `python -m pytest tests/data/test_data_quality.py -q` | 新鲜度不退化、质量测试绿 |
| 十源健康 | `python -c "import sys;sys.path.insert(0,'src');from zephyr.data.source_health_check import run_source_health_check as f;print(f())"` | miniqmt connect_ok，无新增连续fail源 |
| depgraph 重生成抗性 | 批后择机跑一次 `generate_project_depgraph.py --output-db depgraph`，复核该批 production 未被回退（§3.4-4 同法） | production 数量不变 |
| 自治/告警面（批5/6 加查） | `.runtime/autonomy_gate/alerts.jsonl`、`.runtime/audit/agentic_drift_guard_alerts.jsonl` 批后增量 | 无 severity=critical 新增 |

观察窗满 24h 且全绿 → 该批闭环，在 tracker（`construction_progress_tracker.md` 最新小节）登记批次行，开下一批。

---

## 9. 执行组织（给后续施工批的照单）

### 9.0 执行日清单再生（DIGEST P2 在飞，必须重生成，勿用静态数字）

```powershell
python .runtime/_b007_inventory.py      # 重拉 testing/stable 全量 + 测试推断
python .runtime/_b007_classify.py       # 建成批次归属
python .runtime/_b007_plan_data.py      # 6 批分组 + 交叉表
python .runtime/_b007_emit_manifests.py # 批次 node_id 清单 + 批前快照
# 另需生成两个小工具（逻辑见 §6.2-5 与 §7.1，各 <40 行）：
#   .runtime/_b007_verify_batch.py   — 批后 build_status 分布核验
#   .runtime/_b007_rollback_batch.py — 快照内 node_id 反向 UPDATE（带快照白名单护栏）
```

### 9.1 封波前提

- DIGEST P2 波次（#ARCH-255/256/259+）全部闭环、ARCH 登记静止 ≥ 半天，才启动 P0 前置批；
  否则把执行日清单再生时刻作为冻结点，P2 后续波次成果挂"B-007 补充批"随批6 一并处理。

### 9.2 并发组织建议

- **P0 前置批：单会话串行**（DDL+代码+文档，强一致要求，禁并发）。
- **门禁验证（每批）：可 3 路并行**——sweep 三桶（A/B/C manifest）天然三路；批内 pytest 与 sweep 互不依赖可同时开；
  但同一时刻只跑一批的门禁，避免 flake 归因混乱。
- **状态迁移：单会话串行**——`_db_write_lock` 本就把 DB 写串行化，多会话并发只有锁竞争无收益；
  批内 4a/4b 顺序不能乱（testing 先转 stable）。
- **批次间：严格串行**（批1→…→批6），监控期可重叠：批 N 转态完成进入 24h 观察窗的同时，
  可并行跑批 N+1 的门禁一/二（pytest+sweep 只读），但批 N+1 的**转态**必须等批 N 观察窗闭环。
  按此排程，6 批总周期约 4-6 个工作日（门禁重跑是大头），09-03 前可完工。
- **批4 单独约窗**：收盘后+非交易日窗口，Owner 在场可一键回滚。

### 9.3 每批闭环登记格式（写 construction_progress_tracker.md）

`| B007-批N | <范围> | 转态节点数 testing→stable→production X/Y、stable→production Z | 门禁：pytest 全绿/sweep 零新增红(基线锚)/回测冒烟(批3/4) | 监控 24h 结论 | ✅/⏳ |`

---

## 10. 风险与边界声明

1. **本计划不触碰 design_maturity**（ARCH-MM-002 两态=物理存在性，已全部 production/design 各安其位）；
   B-007 只动 build_status 生命周期态。
2. **flag/运行时启用不在本计划范围**：production 转态 ≠ 功能翻开（commit_queue flag、trading watchdog、
   NSSM 注册、redis.conf、核亲和等系统级启用仍属各专项 Owner 窗口，见 #ARCH-225/57号文口径）。
3. **运行时接线不在本计划范围**：DIGEST 各波"生产接线留运行时装配批"的注入点（broker/调度/Alerter 等）
   是独立后续批；本计划只完成 depgraph 状态面转正+验证。
4. 数字快照漂移：DIGEST P2 在飞，本文全部数字以 §9.0 重生成口径为准。
