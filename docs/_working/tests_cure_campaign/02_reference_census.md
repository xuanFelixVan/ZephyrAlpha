---
ttl: task_bound
completes_when: tests 治理战役收官随批归档
---
# tests/ 战役 02 — 引用面普查（reference census）

> 范围：tests/ 一级目录归并为 8 域（gov/data/trade/research/infra/ai/meta/legacy_zephyr）会破坏的全仓引用。
> 方法：只读挖矿。以 `ls -d tests/*/` 实测 129 个一级目录（不含 `__pycache__`；任务书背景数 148，实测以当日工作区为准）为枚举源，ERE 模式
> `tests[\/](<129 目录名交替>)([^A-Za-z0-9_]|$)` 全仓 grep（py/yaml/yml/toml/cfg/ps1/sh/json），另加引号字面量探针、pathlib 组合探针、f-string 探针、`import tests.` 探针交叉验证。
> 日期：2026-10-04。

---

## 0. 汇总（先看这个）

| 指标 | 数值 |
|---|---|
| P0 会炸（python 字符串路径用于 import/open/subprocess/exists 判定） | **10 活跃 + 3 休眠（目标已不存在）** |
| P1 需同步（CI/hook/配置/脚本参数/注册册/地图） | **≈277 文件**（其中 docs 机生 algo_flow 地图 180 个可再生成冲销） |
| P2 叙述（注释/docstring/文档散文） | 概数 ~2 万行（src+scripts+config 注释 ~3.4k 行；docs .md 17,329 行/1,548 文件；docs/_working yaml ~13k 行匹配） |
| conftest.py | **27 个**（tests/ 根 1 + 一级 14 + 二级 12） |
| pytest 配置件 | pyproject.toml `[tool.pytest.ini_options]` + py.ini `[pytest]` 段（裁定#278 精简跑法）；无 pytest.ini/setup.cfg/tox.ini |
| 代码侧引用总行数 | 3,511（src 2,666 / scripts 584 / config 146 / .github 14 / .trae 93 / architecture_model 3 / pyproject 3 / py.ini 2） |
| `import tests.*` / `from tests.*`（src+scripts） | **0** —— 代码侧无测试包导入，搬迁不炸 import |

**单一最高危点**：`src/zephyr/gov_enforcement/commit_gates/errcode_consistency_gate.py:79` 的
`_SSDOT_TEST_REL = "tests/governance/test_error_code_consistency.py"` 经 importlib 按路径加载判定逻辑 SSoT——
目标移动即 RuntimeError → **GATE-ERRCODE 在 GitCommitGateway 上硬阻断所有提交**。同文件路径还写死在
`.pre-commit-config.yaml:586` 的 hook entry（`python -m pytest tests/governance/test_error_code_consistency.py ...`）——
两处任一未同步 = commit 双通道皆断。**修复批必须最先处理这一对。**

---

## 1. pytest 配置面

### 1.1 pyproject.toml `[tool.pytest.ini_options]`（rootdir 真源）

| 项 | 值 | 对 8 域归并的影响 |
|---|---|---|
| testpaths | `["tests"]` | 根不动 → 不变 |
| python_files / classes / functions | `test_*.py` / `Test*` / `test_*` | 不变 |
| norecursedirs | `*.egg .* .runtime _darcs build CVS dist node_modules venv {arch}` | 8 个新域名（gov/data/trade/research/infra/ai/meta/legacy_zephyr）无一撞词条 → 不静默漏测。**注释里点名 `tests/data`、`tests/zephyr/data` 是真实测试目录（:133-135）**——归并后路径变 tests/<域>/data，注释需顺手改（P2） |
| addopts | `-v --tb=short --strict-markers --max-worker-restart=5` | 不变 |
| cache_dir | `.runtime/tmp/pytest_cache`（相对 rootdir） | 不变 |
| timeout | 120 | 不变 |
| markers（9 个） | slow / e2e / security / financial / filterwarnings / asyncio / silent_failure / quick / critical | 不变 |
| filterwarnings | `error` + Deprecation 豁免 + `#ARCH-084 会话级 tracked 区漂移` 前缀豁免 | 不变 |

### 1.2 py.ini `[pytest]` 段（裁定#278 精简跑法，仅显式 `-c py.ini` 生效）

- testpaths=tests、同款 norecursedirs、timeout=120、同款 9 markers（linelist 每行一个）。
- **与 pyproject 由 `scripts/governance/d7_code/compare_pytest_configs.py` 看守（GATE-PYTEST-CONFIG-DRIFT）**：改 markers/timeout 必须双写。
- :46-47 注释同样点名 `tests/data`、`tests/zephyr/data`（P2 顺手改）。

### 1.3 相邻配置

- ruff `per-file-ignores`：`"tests/**"` glob —— 兼容下沉，无需改。
- mypy：files=src/zephyr，exclude 含 tests/ —— 无关。
- coverage：source=zephyr，omit `*/tests/*` —— 无关。
- 无 pytest.ini / setup.cfg / tox.ini；.github 无专门 test matrix workflow（测试都在 governance/dedup/lsg/deploy 四个 workflow 的步骤里，见 §4）。

---

## 2. conftest 链图谱（27 个）

| # | conftest | 一句话职责 | 相对路径依赖 / 搬迁风险 |
|---|---|---|---|
| 1 | tests/conftest.py | 全局：sys.path 注入 src/、公共 fixture（tmp_db 等）、UTF-8 保障、subprocess 脚本支援 | `parent.parent` 取 REPO 根——根不动，安全 |
| 2 | tests/agent_rbac/ | AgentIdentity/RbacConfig/rbac_roles.yaml 工厂 fixture | 无（tmp_path） |
| 3 | tests/ai_layer/cleaning/ | 加载 scripts/ai_layer/apply_ai_intake_ddl.py 建 PG 测试 schema | **`parents[3]` 取 REPO——下沉一级即失准（P0 级内部断链）** |
| 4 | tests/ai_layer/comparator/ | experiment_store DDL + PG 可达性探测（skip 而非假绿） | 无 |
| 5 | tests/ai_layer/heritage/ | 双 DDL（heritage+intake）加载 + 测试 schema | **`parents[3]`** |
| 6 | tests/ai_layer/intake/ | intake DDL 加载 + PG 探测 | **`parents[3]`** |
| 7 | tests/ai_layer/perceive/ | intake DDL + FIXED_NOW 时间冻结 | **`parents[3]`** |
| 8 | tests/ai_layer/redline/ | FakeGateway + 目录级隔离（OBJ_S 红线机检面） | 无 |
| 9 | tests/ai_layer/scheduling/ | 只读 config/schedule_gate_policy.yaml + Journal(tmp_path) | **`parents[3]`**（REPO 常量） |
| 10 | tests/ai_layer/switch_engine/ | SwitchRegistryStore sqlite(tmp_path) 工厂 | 无 |
| 11 | tests/ai_layer/tools/ | usage_stats DDL + PG 探测 | 无 |
| 12 | tests/audit/ | 事件循环泄漏治本：teardown 收割残留 ProactorEventLoop | 无 |
| 13 | tests/db/ | 收敛 governance.db 路径真源（DB_PATH SSoT 派生 fixture） | 无（SSoT 真源） |
| 14 | tests/drift/ | 已退役（stub 注入移除，靠根 conftest） | 无 |
| 15 | tests/escalation/ | 已退役（同上） | 无 |
| 16 | tests/frontend/ | 收集期 _ModuleLock 死锁防御：预导入争用终端模块 | 无 |
| 17 | tests/governance/ | repo_root/gov_dir/manifest 等 session fixture（REPO_ROOT SSoT） | 无 |
| 18 | tests/governance/commit_gates/ | 向 sys.path 注入本目录（恢复 `import gate_test_helpers` 直导） | 用 `parent` 自定位——随目录走，安全 |
| 19 | tests/governance/meta_question/ | 考试循环装配：importlib 复用上游夹具，零 PG | 头部注释引 tests/governance/meta_question/…（随迁即改注释） |
| 20 | tests/governance/red_blue_pkg14/ | fixture 转发层（实现真源=_common.py） | `from governance.red_blue_pkg14._common import …`——**包化绝对导入，governance 层移位后导入名变** |
| 21 | tests/governance/scripts_governance/ | 修复路径解析：注入 d3_metadata 到 sys.path | **`parents[3]` + 头注释逐级推演——下沉一级即失准** |
| 22 | tests/infrastructure/ | 子进程保收：基线快照→收敛等待→terminate/wait/kill 收割 MCP 集群 | 无 |
| 23 | tests/intelligence/switch_engine/ | SwitchRegistryStore sqlite(tmp_path) 工厂（#10 的镜像） | 无 |
| 24 | tests/pipeline/ | autouse 清 LLM API key 环境变量（强制 simulated 模式） | 无 |
| 25 | tests/rollback/ | 活库 gates 表 DDL 逐字照抄（结构断言以活库为准） | 无 |
| 26 | tests/strategy_factory/ | 合成面板 make_synthetic_panel（指数+ETF+regime） | 无 |
| 27 | tests/trading/ | event loop 每测试隔离（autouse 建/关 loop） | 无 |

**结构性风险（超出"外部引用"但必须记录）**：
- 6 个 conftest 用 `parents[3]` 锚定 REPO 根（#3/5/6/7/9/21）——目录下沉一级全部失准。
- tests/ 全树 **552 个 .py 文件**含 `parents[N]` 深度耦合（含测试文件本体），是分类批修复面的组成部分。
- **30 个一级目录带 `__init__.py`（包化）**（agent_rbac、governance、infrastructure、llm_security、trading、risk、fixtures…）——下沉后模块导入名整体变，影响 tests 内部互相 import（如 #20 的 `governance.red_blue_pkg14._common`）与 pytest rootdir/importmode 语义。
- tests/ 根层仅 3 个 .py（conftest.py、test_batch_creation_tokens_anchor.py、test_generate_governance_map.py）。

---

## 3. 硬引用普查（重点）

### 3.1 P0 — 会炸（python 字符串路径用于 import/open/subprocess/exists 判定）

**活跃（目标路径当前存在，搬迁即断）：**

| # | 位置 | 引用 | 用法 | 炸法 |
|---|---|---|---|---|
| 1 | src/zephyr/gov_enforcement/commit_gates/errcode_consistency_gate.py:79 | `tests/governance/test_error_code_consistency.py` | importlib 按路径加载 | RuntimeError → **GATE-ERRCODE 阻断所有 commit** |
| 2 | src/zephyr/governance/ops_governance/phase_check_registry.py:793,830-832,891 | `tests/governance/test_gct_integration.py`（实际在 tests/governance/drift/，见注）、`tests/governance/test_jsonl_pipeline.py`、`tests/governance/test_dependency_graph_acyclic.py`、`tests/infrastructure/drift/…`、`tests/infrastructure/escalation/…` | exists() + pytest subprocess | 相位门降 YELLOW / pytest 报 no tests ran |
| 3 | src/zephyr/integration/mcp/governance_server.py:500-507 | G-CT-001..008 → `tests/governance/test_gct_00X_*.py`（8 条映射） | REPO_ROOT/…exists() | MCP 契约校验返回 invalid（注：8 条中 6 条当前已失准——实际文件在 tests/governance/{security,audit,drift,governance_e2e,budget}/ 下） |
| 4 | src/zephyr/gov_enforcement/rule_enforcement/ai_capability_guard.py:261 | `"tests/architecture" in rel` 子串 | 能力分级判定 | 沉默语义漂移：豁免失效，测试文件能力级从 EXTEND 升 FULL（治理放宽，不崩溃） |
| 5 | scripts/governance/run_silent_failure_regression.py:138 | `project_root / "tests" / "governance"` | subprocess pytest 范围限定 | silent_failure 回归跑空目录 |
| 6 | scripts/governance/d6_security/run_adversarial_checks.py:56 | `PROJECT_ROOT / "tests" / "infrastructure" / "test_drift_red_blue_adversarial.py"` | subprocess pytest | 对抗检查 FileNotFoundError/收集 0 |
| 7 | scripts/governance/d5_architecture/check_drift_e2e.py:71 | `tests/infrastructructure/drift/test_drift_e2e_pipeline.py`（实测 tests/infrastructure/drift/…存在） | subprocess pytest（-x） | e2e 漂移检查失败 |
| 8 | scripts/ops/shadow_canary_deploy.py:195 | `["…","-m","pytest","tests/contracts/","-q"]` | consumer_expectations subprocess | 影子金丝雀部署验收失败 |
| 9 | src/zephyr/infrastructure/asset_inventory/trust_anchor.py:116 | `tests/asset-inventory/`（连字符） | subprocess pytest | **已休眠**（实际目录为 asset_inventory，现状已失准）——修复批顺手治 |
| 10 | scripts/governance/meta/mutation_test_post_sync_validator.py:78 | `_REPO_ROOT/"tests"/"unit"/"test_post_sync_validation.py"` | subprocess pytest（:252） | **已休眠**（tests/unit 不存在；docstring :30 指向 tests/governance/shared/test_post_sync_validation.py，代码与文档自相矛盾） |

**休眠（路径形态在代码内运行期使用，但目标目录当前已不存在——搬迁不新增伤害，但分类批应一并治）：**

| # | 位置 | 引用 | 说明 |
|---|---|---|---|
| 11 | src/zephyr/gov_code_quality/code_dedup/canary_manager.py:76-84 | `tests/canary/{a,b,b2,near}.py` | CloneGuard canary 注册键（tests/canary 目录存在，但 a/b/b2/near.py 已不存在） |
| 12 | src/zephyr/gov_code_quality/code_dedup/file_creator.py:97 | `Path("tests/test_code_dedup_engine")` | verify_all 存在性校验默认值（dedup-test.yml 注释证实测试已迁 tests/governance/code_quality/） |
| 13 | src/zephyr/shared/utils/testing.py:182 | `scan_target: str = "tests/factory-scan-target/"` | AuditReport 构造默认参（目标目录不存在） |

**P0 修复面结论：10 活跃位 + 3 休眠位，集中在 8 个 src 文件 + 4 个 scripts 文件。** 全部是逐字面路径，无一处经配置/注册表间接解析——分类批需逐个改写为新域路径，其中 #2/#3/#10 在搬迁前就已部分失准（深一层目录漂移），建议同批以"实测锚定"方式修正而非字符串替换。

### 3.2 P1 — 需同步（配置/CI/hook/脚本参数/注册册/地图）

**A. 提交与 CI 门禁（高危，先修）**

| 位置 | 引用 | 影响 |
|---|---|---|
| .pre-commit-config.yaml:586（另 :580,:591 注释） | hook entry `python -m pytest tests/governance/test_error_code_consistency.py -q …` | **每次 commit 的 hook 失败**（与 P0#1 同文件同批修） |
| .github/workflows/dedup-test.yml:6,8,14,20,36 | `tests/governance/code_quality/test_code_dedup_engine*.py` + 触发路径 | CI 步骤炸 + 触发器失配静默不跑 |
| .github/workflows/lsg_security_gate.yml:19,26,46,51,57,61 | `tests/llm_security/**` + 具体测试文件（test_lsg_self_regression.py、test_l5_performance_guard.py） | 同上 |
| .github/workflows/governance.yml:353,406 | `tests/governance/test_battle_map_simulation_validation.py`、`tests/architecture/` | 同上 |
| .github/workflows/deploy.yml:71 | `tests/contracts/` | 部署前置验收炸 |
| scripts/governance/d7_code/detect_private_key.py:68-71 | 私钥白名单：`tests/fix/test_auto_fix_core.py`、`tests/llm_security/test_secrets.py`（另 2 条根级已失准） | 白名单失配 → commit 门禁误报测试含私钥 |
| config/ai_capability_matrix.yaml:76 | `scope: "tests/architecture/**"` | 能力矩阵扫描范围失效（静默漏扫） |

**B. scripts/ 里的路径参数/映射/白名单（8 文件）**

- scripts/governance/d5_architecture/syncers/sync_blueprint_code_index.py（~50 条 test_patterns 映射，写入 blueprint 索引；多条根级 tests/test_*.py 已失准——**再生成器产物，建议重跑生成而非手改**）
- scripts/governance/d7_code/validate_test_coverage.py:143（约定模板 `f"tests/{{domain}}/test_{stem}.py"`——8 域归并改变目录约定层级本身）
- scripts/governance/fix_depgraph_module_id.py:108-112,141,143（7 条 tests/ 路径→module_id 映射，oneoff）
- scripts/governance/meta/validate_rules_integrity.py:150,155（2 条 tests/governance/{generators,shared}/ 路径）
- scripts/governance/wave1b/dead_letter_census.py:49-50（2 条 tests/governance/ 映射）
- scripts/governance/oneoff/data_domain_design_state_complete.py:93-94（tests/data/、tests/zephyr/data/ → DATA-TEST 标签）
- scripts/governance/oneoff/_fix_remaining_en.py:102（tests/data/… → 中文简介）
- scripts/governance/repair/apply_verification_results.py（28 条 tests/X→tests/Y 重写规则，历史迁移脚本=已执行完的变更记录，归 P2 更准，列此备查）

**C. config/ 地图类 yaml（5 文件真需同步；另 8 文件为 [TESTS] 注释锚点归 P2）**

- config/strategy_production_map.yaml（~10 处 consumers/叙述，如 tests/backtest/test_cpcv.py、tests/model/test_exam_trigger_scheduler.py）
- config/trading_decision_map.yaml、config/dev_delivery_map.yaml、config/dr_policy.yaml:52（verify_method 引 tests/dr/…）

**D. docs/ 需同步册（256 文件）**

| 组 | 数量 | 性质 |
|---|---|---|
| docs/registry_of_registries.yaml | 1 | ROOR 真源 |
| docs/01_policies_and_standards/_registry/catalogs/*.yaml | 18 | 注册册（gate_registry、test_suite_registry、module_translation_registry、capability_canonical_file_registry、ruling_registry、risk_tier_registry、infrastructure_registry、fms_deadref_baseline、depgraph_scan_exclusions 等） |
| docs/01_policies_and_standards/rules/trae_0{28,74,76,77,78,79,86}*.yaml | 7 | 规则 YAML |
| docs/01_policies_and_standards/sop/governance_sop/commit_guide_sources/gate_digest_registry.yaml | 1 | 门禁摘要册 |
| docs/03_modules/path_ownership_map.yaml | 1 | 路径所有权地图 |
| docs/03_modules/_cross_layer/database/business_data_categories.yaml | 1 | 跨层地图 |
| docs/03_modules/**/algo_flow/*.yaml | 180 | **机生模块算法地图（sync_blueprint_code_index/生成器产物——重跑再生成即可冲销，勿手改）** |
| docs/03_modules/_domain_frontend/acceptance/ACC-F-*.yaml | 47 | 验收卡（引 tests/frontend/ 等） |
| architecture_model/（contracts/consumer_registry.yaml、contracts/error_code_registry.yaml:3903、layers/b_mcp.yaml:21） | 3 | 契约注册册 |

**P1 总计 ≈277 文件**（7 门禁/hook + 8 scripts + 5 config + 256 docs/architecture_model；其中 180 机生可再生成，净手改 ≈97）。

### 3.3 P2 — 叙述（文档/注释，低危）

- src/ 2,666 行匹配中绝大多数为 docstring/`[TESTS]`/`[MODIFY-GUARD]` 头部元数据与设计叙述（如 src/zephyr/research/evidence/*.py、gov_audit/*.py 各 3-5 条注释）。
- scripts/ 584 行：**lane/ruler 族（scripts/backtest/cost_accounting_ruler.py、lane_f_grid_adapter.py、lane_e_enhanced.py、lane_b_idea_generator.py 等）全部仅头注释 [TESTS]/[MODIFY-GUARD] 引用，无运行期硬路径**。
- config/ 8 文件的 `[TESTS]` 注释锚点（alert_webhook、crisis_gate、cleaning_rules、cleaning_expectations、cleaning_anomaly_rules、model_scoring_policy、paper_hedge、emergency_track）。
- docs/：.md 叙述 17,329 行 / 1,548 文件；docs/_working/ 归档 yaml ~13,062 行匹配（历史战役工件，不修）。
- .trae/：93 行（rules/documents；其中 3 个非 .md 件：_arch_issue_full_backup.yaml、_algo_flow_script_backup/ 2 个 .py 备份件）。
- pyproject.toml:133,157,172 + py.ini:46,47 注释（norecursedirs 理据、复验留痕）。
- sitecustomize.py:12（[TESTS] 注释）。
- 根 README/CONTRIBUTING/AGENTS/llms.txt：0 匹配。

### 3.4 被引最多的 tests/ 一级目录（代码侧 src+scripts+config+.github Top）

governance 727 ｜ backtest 298 ｜ trae_rules 204 ｜ zephyr 171 ｜ signal_ashare 159 ｜ agent_rbac 114 ｜ infrastructure 100 ｜ ai_layer 90 ｜ audit 88 ｜ risk 84 ｜ ex_core 78 ｜ factor 75 ｜ autonomy 65 ｜ trading 61 ｜ regime 57 ｜ config 55 ｜ scripts 54 ｜ intelligence 52 ｜ fixtures 52 ｜ strategy_pipeline 51 ｜ plan_engine 46 ｜ pf_core 42 ｜ strategy_factory 37 ｜ position 34 ｜ data 34

（trae_rules 的高位主要来自 tests/trae_rules 自身相关规则册叙述——该目录在 129 实测清单内。）

---

## 4. 脚本/工具调用面（pytest 调用者）

**写死测试路径的调用者（=P0/P1 已列，此处汇总）：**

| 调用者 | 目标 | 分级 |
|---|---|---|
| GitCommitGateway→errcode_consistency_gate | tests/governance/test_error_code_consistency.py | P0#1 |
| pre-commit hook（.pre-commit-config.yaml:586） | 同上 | P1-A |
| phase_check_registry（src） | tests/governance/*.py、tests/infrastructure/{drift,escalation}/… | P0#2 |
| governance_server MCP（src） | tests/governance/test_gct_00X（8 映射） | P0#3 |
| trust_anchor（src） | tests/asset-inventory/（连字符，已休眠） | P0#9 |
| run_silent_failure_regression | tests/governance（pathlib 组合） | P0#5 |
| run_adversarial_checks（d6_security） | tests/infrastructure/test_drift_red_blue_adversarial.py | P0#6 |
| check_drift_e2e（d5_architecture） | tests/infrastructure/drift/test_drift_e2e_pipeline.py | P0#7 |
| mutation_test_post_sync_validator（meta） | tests/unit/…（已休眠，与 docstring 矛盾） | P0#10 |
| shadow_canary_deploy（ops） | tests/contracts/ | P0#8 |
| .github 四 workflow | 见 §3.2A | P1-A |

**通用 pytest 调用者（目标可注入/根限定，搬迁不炸，列出备查）：**
fix_safety.run_pytest（src，target 可传参）、run_gate_chain.py（经门注册表聚合，无 tests 字面量）、
validate_config_integrity.py（REPO_ROOT/"tests" 根限定）、check_test_symbol_validity / check_naming_convention /
domain_header_maint / check_module_id_consistency / rewrite_imports / validate_test_assertion_depth /
validate_test_coverage / pre_op_check / validate_nested_flat_dirs / validate_target_layer（均 root/"tests" 根限定，rglob 全树）、
chaos_injector / drift_result_types / test_fixture_checker（src，root/"tests"）、
compare_pytest_configs（配置对齐看守）、ollama_version_guard / verified_promotion_check / wave1b 系（仅注释）。
**-k 表达式经查无目录名硬编码**（-k 皆用 marker/测试名，无 tests/<dir> 依赖）。

---

## 5. 修复批建议（供分类批接续）

1. **第一批（commit 通道保命）**：P0#1 + .pre-commit-config.yaml:586 同批修——两者指向同一文件，任一滞后即全仓 commit 阻断。
2. **第二批（CI/门禁）**：§3.2A 其余（4 workflow、detect_private_key、ai_capability_matrix scope）。
3. **第三批（P0 其余 + 休眠位顺手治）**：§3.1 全表；#2/#3/#10 建议以实测文件位置锚定重写（搬迁前已部分失准）。
4. **再生成冲销**：algo_flow 180 yaml + sync_blueprint_code_index 数据走生成器重跑，禁手改（静态清单禁手工维护铁律）。
5. **注册册同步**：18 catalogs + ROOR + 7 rules + gate_digest——改 YAML 同步 DB（RULE-SSOT 方向）。
6. **内部结构面**：6 个 parents[3] conftest、552 个 parents[N] 文件、30 个包化目录的 __init__.py 导入名——属分类批施工面，本普查仅计量。

## 附：方法与口径备注

- 目录名交替含单字母目录（e、ba、ce、dr…），ERE 以 `[^A-Za-z0-9_]|$` 收边防 tests/e 误吞 tests/escalation。
- Windows 反斜杠路径（.ps1/输出字符串）以 `tests[\/]` 双向覆盖。
- docs/_working 与 .trae 历史工件计为 P2 不修；tests/ 自身内部引用不在本普查范围（另见 01_structure_census.md）。
- "148" vs 实测 129：以普查当日 `ls -d tests/*/` 为准（__pycache__ 未计）。
