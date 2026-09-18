---
ttl: task_bound
completes_when: 全流通战役收官且验收仪 --crosscheck 可重跑复现
---

# 环节层面遗漏自检（验收仪 `--crosscheck` 实测产出，勿手改）

生成时间：2026-09-18 11:26:12.383388+00:00（生成件=`scripts/automation/flowthrough_verifier.py`）

资源自守：mem_avail_gb=34.4 cpu_pct=26.4 → 放行

## 1. 真源实测规模与新鲜度

| 真源 | 路径 | 实测对象数 | 词汇 | 真源龄 | sha256 |
|---|---|---|---|---|---|
| A_arch_model | `architecture_model/index.yaml` | **75** | D_* 域 | fresh(0.07d) | `04d50e2fd6772a32` |
| B_functional_domain_registry | `docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml` | **79** | D_* 域 | fresh(0.0d) | `6bbc396998a959c3` |
| | ↳ entries 94 | | | | |
| C_battle_map_domain_policy | `docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml` | **43** | D_* 域（11 flow_stage allowed 并集） | fresh(0.01d) | `48c26cd5a8624b13` |
| | ↳ flow_stage 数 11 | | | | |
| D_trading_decision_map | `config/trading_decision_map.yaml` | **138** | TDM 节点（flow/layer 词汇，与 D_* 异轴） | fresh(0.07d) | `69e5b174263208a1` |
| | ↳ layer 码 18 / 流 4 / 边 194 | | | | |
| E_data_tasks_and_schedule | `src/zephyr/data/config/tasks.yaml,src/zephyr/data/config/schedule.yaml` | **266** | task_id（运行视角）+ 落点表 | fresh(0.0d) | `a11bc4fcb40231e1` |
| | ↳ task 266 / 表 192 / 档期 24 / 无依赖声明 226 | | | | |
| F_docs_03_modules_dirs | `docs/03_modules/_domain_*/` | **52** | _domain_* 目录名→D_* 归一 | fresh(Noned) | `None` |
| | ↳ _domain_ 目录 52 / .md 570 / 空目录 ['_domain_red_blue_validator'] | | | | |
| G_depgraph_runtime | `depgraph PG nodes/edges/domains` | **75** | D_* 域（代码视角） | fresh(0.81d) | `n/a(实时查询)` |
| | ↳ nodes 12000 / edges 22845 / dataflow_runs 0 / jobs 1747 / steps 341 / 最后同步 2026-09-18T11:09:52.156319+00:00 | | | | |

## 2. 两两差集（域词汇真源，逐条列非零项）

| 左真源 | 右真源 | 方向 | 非零项数 | 逐条清单 |
|---|---|---|---|---|
| A_arch_model | B_functional_domain_registry | 仅在 A_arch_model | **0** | 0 |
| A_arch_model | B_functional_domain_registry | 仅在 B_functional_domain_registry | **4** | `D_EXECUTION`, `D_ORDER`, `D_PORTFOLIO`, `D_SIGNAL` |
| A_arch_model | C_battle_map_domain_policy | 仅在 A_arch_model | **33** | `D_ARCHIVE_SCRIPTS`, `D_ARCH_GUARD`, `D_ARCH_SCRIPTS`, `D_AUDITTEST`, `D_AUTONOMY_CORE`, `D_AUTONOMY_PERM`, `D_CODE_SCRIPTS`, `D_COMPLIANCE_SCRIPTS`, `D_CONTRACTS`, `D_DATA_SCRIPTS`, `D_FRONTEND`, `D_GOVERNANCE`, `D_GOV_AUDIT`, `D_GOV_CODE_QUALITY`, `D_GOV_DOCS`, `D_GOV_DRIFT`, `D_GOV_ENFORCEMENT`, `D_GOV_OPS_RESILIENCE`, `D_GOV_REPAIR`, `D_GOV_RULE`, `D_GOV_SCRIPTS`, `D_INFRASTRUCTURE`, `D_INFRA_A2A`, `D_INFRA_OPS`, `D_INFRA_RECOVERY`, `D_INFRA_TELEMETRY`, `D_INTEGRATION_GATEWAY`, `D_META_SCRIPTS`, `D_SECURITY_LLM`, `D_SEC_SCRIPTS`, `D_SIGLEGACY`, `D_STRUCT_SCRIPTS`, `D_TEST` |
| A_arch_model | C_battle_map_domain_policy | 仅在 C_battle_map_domain_policy | **1** | `D_SIGNAL` |
| A_arch_model | F_docs_03_modules_dirs | 仅在 A_arch_model | **36** | `D_ARCHIVE_SCRIPTS`, `D_ARCH_GUARD`, `D_ARCH_SCRIPTS`, `D_ASHARE_SIGNAL`, `D_AUDITTEST`, `D_CODE_SCRIPTS`, `D_COMPLIANCE_SCRIPTS`, `D_CROSS_ASSET`, `D_DATA_GOV`, `D_DATA_SCRIPTS`, `D_DATA_SEC`, `D_EXEC_SIM`, `D_EX_CORE`, `D_FBL_DIAGNOSERS`, `D_FBL_VERIFICATION`, `D_GOV_CODE_QUALITY`, `D_GOV_DOCS`, `D_GOV_OPS_RESILIENCE`, `D_GOV_REPAIR`, `D_GOV_SCRIPTS`, `D_INFRA_A2A`, `D_INFRA_OPS`, `D_INFRA_RECOVERY`, `D_INFRA_RUNTIME`, `D_INFRA_TELEMETRY`, `D_INTEGRATION_GATEWAY`, `D_META_SCRIPTS`, `D_ML_TRAIN`, `D_OPS`, `D_PF_CORE`, `D_PLAN`, `D_SEC_SCRIPTS`, `D_SIGLEGACY`, `D_SIGQC`, `D_STRUCT_SCRIPTS`, `D_TEST` |
| A_arch_model | F_docs_03_modules_dirs | 仅在 F_docs_03_modules_dirs | **13** | `D_DATA_GOVERNANCE`, `D_DATA_SECURITY`, `D_EXECUTION_CORE`, `D_EXECUTION_SIM`, `D_INFRASTRUCTURE_OPERATIONS`, `D_INFRASTRUCTURE_RUNTIME`, `D_MACHINE_LEARNING_TRAIN`, `D_PLAN_ENGINE`, `D_PORTFOLIO_ALLOC`, `D_PORTFOLIO_CORE`, `D_RED_BLUE_VALIDATOR`, `D_SIGNAL`, `D_SIGNAL_QUALITY` |
| A_arch_model | G_depgraph_runtime | 仅在 A_arch_model | **0** | 0 |
| A_arch_model | G_depgraph_runtime | 仅在 G_depgraph_runtime | **0** | 0 |
| B_functional_domain_registry | C_battle_map_domain_policy | 仅在 B_functional_domain_registry | **36** | `D_ARCHIVE_SCRIPTS`, `D_ARCH_GUARD`, `D_ARCH_SCRIPTS`, `D_AUDITTEST`, `D_AUTONOMY_CORE`, `D_AUTONOMY_PERM`, `D_CODE_SCRIPTS`, `D_COMPLIANCE_SCRIPTS`, `D_CONTRACTS`, `D_DATA_SCRIPTS`, `D_EXECUTION`, `D_FRONTEND`, `D_GOVERNANCE`, `D_GOV_AUDIT`, `D_GOV_CODE_QUALITY`, `D_GOV_DOCS`, `D_GOV_DRIFT`, `D_GOV_ENFORCEMENT`, `D_GOV_OPS_RESILIENCE`, `D_GOV_REPAIR`, `D_GOV_RULE`, `D_GOV_SCRIPTS`, `D_INFRASTRUCTURE`, `D_INFRA_A2A`, `D_INFRA_OPS`, `D_INFRA_RECOVERY`, `D_INFRA_TELEMETRY`, `D_INTEGRATION_GATEWAY`, `D_META_SCRIPTS`, `D_ORDER`, `D_PORTFOLIO`, `D_SECURITY_LLM`, `D_SEC_SCRIPTS`, `D_SIGLEGACY`, `D_STRUCT_SCRIPTS`, `D_TEST` |
| B_functional_domain_registry | C_battle_map_domain_policy | 仅在 C_battle_map_domain_policy | **0** | 0 |
| B_functional_domain_registry | F_docs_03_modules_dirs | 仅在 B_functional_domain_registry | **39** | `D_ARCHIVE_SCRIPTS`, `D_ARCH_GUARD`, `D_ARCH_SCRIPTS`, `D_ASHARE_SIGNAL`, `D_AUDITTEST`, `D_CODE_SCRIPTS`, `D_COMPLIANCE_SCRIPTS`, `D_CROSS_ASSET`, `D_DATA_GOV`, `D_DATA_SCRIPTS`, `D_DATA_SEC`, `D_EXECUTION`, `D_EXEC_SIM`, `D_EX_CORE`, `D_FBL_DIAGNOSERS`, `D_FBL_VERIFICATION`, `D_GOV_CODE_QUALITY`, `D_GOV_DOCS`, `D_GOV_OPS_RESILIENCE`, `D_GOV_REPAIR`, `D_GOV_SCRIPTS`, `D_INFRA_A2A`, `D_INFRA_OPS`, `D_INFRA_RECOVERY`, `D_INFRA_RUNTIME`, `D_INFRA_TELEMETRY`, `D_INTEGRATION_GATEWAY`, `D_META_SCRIPTS`, `D_ML_TRAIN`, `D_OPS`, `D_ORDER`, `D_PF_CORE`, `D_PLAN`, `D_PORTFOLIO`, `D_SEC_SCRIPTS`, `D_SIGLEGACY`, `D_SIGQC`, `D_STRUCT_SCRIPTS`, `D_TEST` |
| B_functional_domain_registry | F_docs_03_modules_dirs | 仅在 F_docs_03_modules_dirs | **12** | `D_DATA_GOVERNANCE`, `D_DATA_SECURITY`, `D_EXECUTION_CORE`, `D_EXECUTION_SIM`, `D_INFRASTRUCTURE_OPERATIONS`, `D_INFRASTRUCTURE_RUNTIME`, `D_MACHINE_LEARNING_TRAIN`, `D_PLAN_ENGINE`, `D_PORTFOLIO_ALLOC`, `D_PORTFOLIO_CORE`, `D_RED_BLUE_VALIDATOR`, `D_SIGNAL_QUALITY` |
| B_functional_domain_registry | G_depgraph_runtime | 仅在 B_functional_domain_registry | **4** | `D_EXECUTION`, `D_ORDER`, `D_PORTFOLIO`, `D_SIGNAL` |
| B_functional_domain_registry | G_depgraph_runtime | 仅在 G_depgraph_runtime | **0** | 0 |
| C_battle_map_domain_policy | F_docs_03_modules_dirs | 仅在 C_battle_map_domain_policy | **14** | `D_ASHARE_SIGNAL`, `D_CROSS_ASSET`, `D_DATA_GOV`, `D_DATA_SEC`, `D_EXEC_SIM`, `D_EX_CORE`, `D_FBL_DIAGNOSERS`, `D_FBL_VERIFICATION`, `D_INFRA_RUNTIME`, `D_ML_TRAIN`, `D_OPS`, `D_PF_CORE`, `D_PLAN`, `D_SIGQC` |
| C_battle_map_domain_policy | F_docs_03_modules_dirs | 仅在 F_docs_03_modules_dirs | **23** | `D_AUTONOMY_CORE`, `D_AUTONOMY_PERM`, `D_CONTRACTS`, `D_DATA_GOVERNANCE`, `D_DATA_SECURITY`, `D_EXECUTION_CORE`, `D_EXECUTION_SIM`, `D_FRONTEND`, `D_GOVERNANCE`, `D_GOV_AUDIT`, `D_GOV_DRIFT`, `D_GOV_ENFORCEMENT`, `D_GOV_RULE`, `D_INFRASTRUCTURE`, `D_INFRASTRUCTURE_OPERATIONS`, `D_INFRASTRUCTURE_RUNTIME`, `D_MACHINE_LEARNING_TRAIN`, `D_PLAN_ENGINE`, `D_PORTFOLIO_ALLOC`, `D_PORTFOLIO_CORE`, `D_RED_BLUE_VALIDATOR`, `D_SECURITY_LLM`, `D_SIGNAL_QUALITY` |
| C_battle_map_domain_policy | G_depgraph_runtime | 仅在 C_battle_map_domain_policy | **1** | `D_SIGNAL` |
| C_battle_map_domain_policy | G_depgraph_runtime | 仅在 G_depgraph_runtime | **33** | `D_ARCHIVE_SCRIPTS`, `D_ARCH_GUARD`, `D_ARCH_SCRIPTS`, `D_AUDITTEST`, `D_AUTONOMY_CORE`, `D_AUTONOMY_PERM`, `D_CODE_SCRIPTS`, `D_COMPLIANCE_SCRIPTS`, `D_CONTRACTS`, `D_DATA_SCRIPTS`, `D_FRONTEND`, `D_GOVERNANCE`, `D_GOV_AUDIT`, `D_GOV_CODE_QUALITY`, `D_GOV_DOCS`, `D_GOV_DRIFT`, `D_GOV_ENFORCEMENT`, `D_GOV_OPS_RESILIENCE`, `D_GOV_REPAIR`, `D_GOV_RULE`, `D_GOV_SCRIPTS`, `D_INFRASTRUCTURE`, `D_INFRA_A2A`, `D_INFRA_OPS`, `D_INFRA_RECOVERY`, `D_INFRA_TELEMETRY`, `D_INTEGRATION_GATEWAY`, `D_META_SCRIPTS`, `D_SECURITY_LLM`, `D_SEC_SCRIPTS`, `D_SIGLEGACY`, `D_STRUCT_SCRIPTS`, `D_TEST` |
| F_docs_03_modules_dirs | G_depgraph_runtime | 仅在 F_docs_03_modules_dirs | **13** | `D_DATA_GOVERNANCE`, `D_DATA_SECURITY`, `D_EXECUTION_CORE`, `D_EXECUTION_SIM`, `D_INFRASTRUCTURE_OPERATIONS`, `D_INFRASTRUCTURE_RUNTIME`, `D_MACHINE_LEARNING_TRAIN`, `D_PLAN_ENGINE`, `D_PORTFOLIO_ALLOC`, `D_PORTFOLIO_CORE`, `D_RED_BLUE_VALIDATOR`, `D_SIGNAL`, `D_SIGNAL_QUALITY` |
| F_docs_03_modules_dirs | G_depgraph_runtime | 仅在 G_depgraph_runtime | **36** | `D_ARCHIVE_SCRIPTS`, `D_ARCH_GUARD`, `D_ARCH_SCRIPTS`, `D_ASHARE_SIGNAL`, `D_AUDITTEST`, `D_CODE_SCRIPTS`, `D_COMPLIANCE_SCRIPTS`, `D_CROSS_ASSET`, `D_DATA_GOV`, `D_DATA_SCRIPTS`, `D_DATA_SEC`, `D_EXEC_SIM`, `D_EX_CORE`, `D_FBL_DIAGNOSERS`, `D_FBL_VERIFICATION`, `D_GOV_CODE_QUALITY`, `D_GOV_DOCS`, `D_GOV_OPS_RESILIENCE`, `D_GOV_REPAIR`, `D_GOV_SCRIPTS`, `D_INFRA_A2A`, `D_INFRA_OPS`, `D_INFRA_RECOVERY`, `D_INFRA_RUNTIME`, `D_INFRA_TELEMETRY`, `D_INTEGRATION_GATEWAY`, `D_META_SCRIPTS`, `D_ML_TRAIN`, `D_OPS`, `D_PF_CORE`, `D_PLAN`, `D_SEC_SCRIPTS`, `D_SIGLEGACY`, `D_SIGQC`, `D_STRUCT_SCRIPTS`, `D_TEST` |

## 3. 未归入任何环节的对象数（§4.1 判据：应为 0）

| 真源 | 对象数 | 字面未匹配 | 异名机械归一 | 归一后仍未归属 | 逐条 / 说明 |
|---|---|---|---|---|---|
| A_arch_model | 75 | 0 | — | **0** | — |
| B_functional_domain_registry | 79 | 3 | `D_EXECUTION`→`D_EXEC_SIM` | **2** | `D_ORDER`, `D_PORTFOLIO` |
| C_battle_map_domain_policy | 43 | 0 | — | **0** | — |
| F_docs_03_modules_dirs | 52 | 12 | `D_MACHINE_LEARNING_TRAIN`→`D_ML_TRAIN`; `D_PORTFOLIO_ALLOC`→`D_PF_ALLOC` | **10** | `D_DATA_GOVERNANCE`, `D_DATA_SECURITY`, `D_EXECUTION_CORE`, `D_EXECUTION_SIM`, `D_INFRASTRUCTURE_OPERATIONS`, `D_INFRASTRUCTURE_RUNTIME`, `D_PLAN_ENGINE`, `D_PORTFOLIO_CORE`, `D_RED_BLUE_VALIDATOR`, `D_SIGNAL_QUALITY` |
| G_depgraph_runtime | 75 | 0 | — | **0** | — |
| E_data_tasks_and_schedule | 266 | 0 | — | **0** | task_id=266 落点表=192 档期=24 无 dependencies 声明=226——全部为 FF-01 内部节拍（异词汇：任务不是域） |
| D_trading_decision_map | 138 | 0 | — | **0** | 异词汇：138 节点 / 4 流 / 18 layer 码 / 194 边——决策点级颗粒，归 FF-06..FF-12 子索引，不上升为环节 |

## 4. 环节清单：推导 vs 骨架对照（不静默采信任何一方）

- 机械推导脊柱（源 C 的 flow_stage）：11 段 = backtest_validation, buy_flow, execution, model_training, position_management, reconciliation, research_incubation, risk_control, sell_flow, simulation_validation, stock_selection
- 未被任何 flow_stage 允许的 depgraph 域：**33** → 按域名前缀机械归口为 4 个横切环节
- 骨架声称环节数：16

- 差异 `stage_count`：{"kind": "stage_count", "derived": 14, "skeleton": 16}
- 差异 `cross_bucket`：{"kind": "cross_bucket", "stage": "X_AI_RUNTIME", "domains": ["D_AUTONOMY_CORE", "D_AUTONOMY_PERM", "D_INFRA_A2A", "D_INTEGRATION_GATEWAY", "D_SECURITY_LLM"]}
- 差异 `cross_bucket`：{"kind": "cross_bucket", "stage": "X_DELIVERY", "domains": ["D_FRONTEND", "D_INFRA_TELEMETRY"]}
- 差异 `cross_bucket`：{"kind": "cross_bucket", "stage": "X_GOV_SUBSTRATE", "domains": ["D_ARCHIVE_SCRIPTS", "D_ARCH_GUARD", "D_ARCH_SCRIPTS", "D_AUDITTEST", "D_CODE_SCRIPTS", "D_COMPLIANCE_SCRIPTS", "D_CONTRACTS", "D_DATA_SCRIPTS", "D_GOVERNANCE", "D_GOV_AUDIT", "D_GOV_CODE_QUALITY", "D_GOV_DOCS", "D_GOV_DRIFT", "D_GOV_ENFORCEMENT", "D_GOV_OPS_RESILIENCE", "D_GOV_REPAIR", "D_GOV_RULE", "D_GOV_SCRIPTS", "D_META_SCRIPTS", "D_SEC_SCRIPTS", "D_STRUCT_SCRIPTS", "D_TEST"]}
- 差异 `cross_bucket`：{"kind": "cross_bucket", "stage": "X_UNCLASSIFIED", "domains": ["D_INFRASTRUCTURE", "D_INFRA_OPS", "D_INFRA_RECOVERY", "D_SIGLEGACY"]}
- 差异 `cross_bucket`：{"kind": "cross_bucket", "stage": "backtest_validation", "domains": ["D_EXEC_SIM"]}
- 差异 `cross_bucket`：{"kind": "cross_bucket", "stage": "buy_flow", "domains": ["D_COMPLIANCE", "D_ORCHESTRATOR"]}
- 差异 `cross_bucket`：{"kind": "cross_bucket", "stage": "execution", "domains": ["D_EX_CORE", "D_EX_SOR"]}
- 差异 `cross_bucket`：{"kind": "cross_bucket", "stage": "position_management", "domains": ["D_PF_ALLOC", "D_PF_CORE", "D_PLAN"]}
- 差异 `cross_bucket`：{"kind": "cross_bucket", "stage": "reconciliation", "domains": ["D_FBL_DETECTORS", "D_FBL_DIAGNOSERS", "D_FBL_VERIFICATION", "D_FEEDBACK_LOOP", "D_OPS"]}
- 差异 `cross_bucket`：{"kind": "cross_bucket", "stage": "research_incubation", "domains": ["D_DATA_ENG", "D_DATA_GOV", "D_DATA_SEC", "D_RESEARCH"]}
- 差异 `cross_bucket`：{"kind": "cross_bucket", "stage": "risk_control", "domains": ["D_REPORTING", "D_SECURITY"]}
- 差异 `cross_bucket`：{"kind": "cross_bucket", "stage": "sell_flow", "domains": ["D_POSITION", "D_SELL_DECISION", "D_TRADING"]}
- 差异 `cross_bucket`：{"kind": "cross_bucket", "stage": "simulation_validation", "domains": ["D_BACKTEST", "D_DIGITAL_TWIN", "D_RISK", "D_SIMULATION"]}
- 差异 `cross_bucket`：{"kind": "cross_bucket", "stage": "stock_selection", "domains": ["D_ALT_DATA", "D_ASHARE_SIGNAL", "D_CROSS_ASSET", "D_DATA", "D_FACTOR", "D_FUNDAMENTAL_SIGNAL", "D_INFRA_RUNTIME", "D_INTEGRATION", "D_INTELLIGENCE", "D_KNOWLEDGE", "D_MKT_DATA", "D_ML_SERVE", "D_ML_TRAIN", "D_REGIME", "D_SHARED", "D_SIGNAL", "D_SIGQC"]}
- **X_AI_RUNTIME**（5 域）：`D_AUTONOMY_CORE`, `D_AUTONOMY_PERM`, `D_INFRA_A2A`, `D_INTEGRATION_GATEWAY`, `D_SECURITY_LLM`
- **X_DELIVERY**（2 域）：`D_FRONTEND`, `D_INFRA_TELEMETRY`
- **X_GOV_SUBSTRATE**（22 域）：`D_ARCHIVE_SCRIPTS`, `D_ARCH_GUARD`, `D_ARCH_SCRIPTS`, `D_AUDITTEST`, `D_CODE_SCRIPTS`, `D_COMPLIANCE_SCRIPTS`, `D_CONTRACTS`, `D_DATA_SCRIPTS`, `D_GOVERNANCE`, `D_GOV_AUDIT`, `D_GOV_CODE_QUALITY`, `D_GOV_DOCS`, `D_GOV_DRIFT`, `D_GOV_ENFORCEMENT`, `D_GOV_OPS_RESILIENCE`, `D_GOV_REPAIR`, `D_GOV_RULE`, `D_GOV_SCRIPTS`, `D_META_SCRIPTS`, `D_SEC_SCRIPTS`, `D_STRUCT_SCRIPTS`, `D_TEST`
- **X_UNCLASSIFIED**（4 域）：`D_INFRASTRUCTURE`, `D_INFRA_OPS`, `D_INFRA_RECOVERY`, `D_SIGLEGACY`

## 5. 对骨架『未归属=0』声明的独立复核

**推翻/补强**：以下真源存在未归属对象，骨架『未归属=0』不成立（或依赖人工裁定兜底）：
- `B_functional_domain_registry` 未归属 2 项：`D_ORDER`, `D_PORTFOLIO`
- `F_docs_03_modules_dirs` 未归属 10 项：`D_DATA_GOVERNANCE`, `D_DATA_SECURITY`, `D_EXECUTION_CORE`, `D_EXECUTION_SIM`, `D_INFRASTRUCTURE_OPERATIONS`, `D_INFRASTRUCTURE_RUNTIME`, `D_PLAN_ENGINE`, `D_PORTFOLIO_CORE`, `D_RED_BLUE_VALIDATOR`, `D_SIGNAL_QUALITY`
- 骨架 §5.1 表第 3/4 行已自记 19 域未被 policy 分类、FDR 与 depgraph 互缺，本轮实测复现（见 §2 差集行），故骨架的 0 是**人工兜底后的 0**，非机械派生的 0。

