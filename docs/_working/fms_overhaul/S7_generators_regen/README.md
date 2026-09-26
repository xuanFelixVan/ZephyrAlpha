---
ttl: task_bound
title: "S7 生成器与 regen-clean 挖矿簿"
created: 2026-09-27
sid: st-fms-chief-20260927
lane: S7
status: 挖干（自审三态见 §5）
---

# S7 挖矿簿 — 生成器普查 + regen-clean 检查器 + 门挂接

## ① 职责一句话

摸清全仓生成器/生成物家底，设计"凡生成物必有 regenerate && diff 机械验证"（骨架五支柱③）的落地件：`regen_clean_check.py` 检查器 + FMS-REGEN-CLEAN 门，堵住"宪法 9.5 立法了静态清单禁手工维护、但无机械验证保证生成物与盘面一致"的缺口。

## ② 现状实测

### 2.0 结论先行（五条硬事实）

1. **regen-clean 缺席已实锤**：`registry_master_index.yaml --check` 当场报 `DRIFT: 磁盘 58 张登记表 ≠ 生成 61 张`（2026-09-27 本会话实测，`scripts/governance/generators/generate_registry_master_index.py:248` check 通道）——真源已前进而生成物未再生，无任何门拦住。
2. **index.md 全族 1,125 个是写一次就烂的一次性生成物**：归属 `scripts/governance/d1_structure/generate_missing_index_md.py`（只补缺失、永不更新既有文件；模板嵌 `created/updated: "{today}"`，`generate_missing_index_md.py:90-91`）；当前 249 个目录缺 index.md（`--dry-run` 实测，集中在 `docs/_working/`）。
3. **GATE-21 对 AI 提交形同虚设**：`src/zephyr/gov_enforcement/commit_gates/derived_file_deletion_gate.py:26-28` 白纸黑字——"GitCommitGateway 用 --no-verify 系统性绕过全部 pre-commit hook——GATE-21 对 AI commit 形同虚设"。新门必须走 in-process CommitGate，不能只挂 pre-commit。
4. **AI 提交主链的真门位是 in-process CommitGate**（`GateSpec(gate_id=..., check=closure, priority=N)`，同族先例 `derived_file_deletion_gate.py:172` priority=46）；own-scope 共享原语在 `src/zephyr/gov_enforcement/commit_gates/_diff_helpers.py:536`。
5. **抽查 3/3 全漂移**（方法与结果见 2.2）：生成物陈旧不是理论风险，是今日盘面。

### 2.1 生成器普查（58 台 generate_*，归档件已剔除）

名单来源：`git ls-files 'scripts/*generate*.py'`（剔除 `_archive`，58 台；另 apply_* 50 台，见 2.1.3）。

#### 2.1.1 分级总表

副作用分级：**绿**=纯函数读仓库文件、可安全重跑；**黄**=写文件但可 `--output` tmp 隔离；**红**=动 DB/外部，禁自动跑。

| 生成器（scripts/ 下省略前缀） | 产出物 | check/dry-run | --output | 时间戳 | 副作用级 | 证据 |
|---|---|---|---|---|---|---|
| governance/generators/generate_gate_registry.py | docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | --check（仅比对 total_gates 计数，弱校验） | 有 | generated_at（写侧 volatile 豁免） | 绿 | :29,:56,:758,:774,:794 |
| governance/generators/generate_script_manifest.py | scripts/governance/script_manifest.yaml | --check | 有 | generated_at | 绿 | :309-310,:294 |
| governance/generators/generate_registry_master_index.py | catalogs/registry_master_index.yaml | --check（计数比对，**今日实报 DRIFT 58≠61**） | 有 | generated_at+`# 自动生成于` | 绿 | :227-228,:248-249 |
| governance/generators/generate_library_index.py | docs/library/ 7 馆页+INDEX.md 共 8 页 | 无 | 无 | built_at 来自 DB | **红**（pg:lib_assets 只读 PG） | :18-25,_OUT_DIR:35 |
| governance/d1_structure/generate_missing_index_md.py | 全仓缺失的 index.md（写一次不更新） | --dry-run / --warn-only | 无（--root 指树） | created/updated=today | 绿（但只补缺，无法全量 regen 比对） | :26-27,:90-91 |
| governance/d3_metadata/auto_generate_index.py | index.md frontmatter 计数+文件表（外科式） | --check / --apply | 无 | 无 | 绿 | :37-40 |
| **【本台是坏的】** 同上 | — | 直接运行即 `ModuleNotFoundError: No module named '_shared'`（:39 import 先于 :63 sys.path 注入，顺序倒挂） | — | — | — | 实测 traceback 2026-09-27 |
| generate_manifest.py（scripts 根） | scripts/script-manifest.yaml（全树清单） | **无 --check 无 --dry-run** | 无 | date.today（:125） | 黄 | :24,:125 |
| governance/generate_project_depgraph.py | depgraph PG 库 + .runtime/depgraph_scan_cache.json | --check --dry-run | — | saved_at（:1887,:2487） | **红**（psycopg2 写 PG，:59-62；且是"真源写入方"非派生，generator_registry.yaml:26-28 列入禁止注册清单） | :59-77 |
| governance/generate_project_path_tree.py | architecture_model 树 YAML | --check | — | :201 | 黄（真源写入方，禁登记触发） | generator_registry.yaml:29 |
| governance/generate_decision_graph.py | YAML→PG sync | --dry-run | — | — | **红**（psycopg2 :89；同为真源写入方） | :89,generator_registry.yaml:27 |
| governance/generate_governance_map.py | config/governance_operations_map.yaml | --dry-run | — | — | 红（input db:depgraph） | generator_registry.yaml:383 段 |
| governance/generate_chain_registry.py | docs 链册 | --dry-run | — | — | 绿 | grep :特征表 |
| governance/generate_asset_index.py | data/asset_index/unified-asset-index.yaml | 无 | 无 | :170 | 黄（写 data/ 业务目录） | :170 |
| d5_architecture/generators/ 26 台（navigation_index / panorama_registry / asset_catalog / capability_heatmap / contract_catalog / cross_domain_matrix / integration_topology / path_tree / domain_doc / domain_index / candidate_module_report / capacity_report / constraint_violations / design_vs_production / code_wiki_stats / blueprint_panorama / dataflow_diagram / data_acquisition_flow / data_inventory / decision_diagram / battle_map_diagram / trading_map_diagram / contracts / policies / module_algorithm_overview / frontend_gap_views） | docs/02_enterprise_architecture/ 各视图 md / architecture_model | 2 台有 --dry-run（blueprint_panorama / contracts） | 个别 | **d5 族已治幂等**：用"最近 git commit 日期"替代时钟（generate_code_wiki_stats.py:91、generate_domain_doc.py:1643、generate_decision_diagram.py:429、generate_integration_topology.py:117、generate_navigation_index.py:134、generate_path_tree.py:723、generate_data_acquisition_flow.py:79） | **红**（多数只读 PG depgraph；data_inventory 读 CH 元数据；code_wiki_stats 读 PG+SQLite:499；frontend_gap_views 仍嵌 now:85） | generator_registry.yaml:33-383 各条 output_globs |
| governance/generators/generate_importlinter.py | import-linter 配置 | --check | — | — | 绿 | 特征表 |
| governance/generators/generate_commit_guide.py | docs/01.../governance_sop/commit_navigation_playbook.md | --check | 有（--output 旗标 :80 附近） | — | 绿 | 特征表 |
| governance/generators/generate_path_ownership_map.py | 路径属主册 | --check | — | :294 | 绿 | 特征表 |
| governance/generators/generate_rule_ai_perception_index.py | catalogs/rule_ai_perception_index.yaml | --check | — | :141 | 绿 | 特征表 |
| governance/generators/generate_resource_profile_registry.py / generate_resource_morning_report.py / generate_resource_week_view.py | 资源册/晨报/周视图 | 1 台 --check | — | 多处 now | 绿/黄 | 特征表 |
| governance/d7_code/generate_fail_open_register.py | fail-open 登记册 | --check | — | 走 now_utc（:51） | 绿 | 特征表 |
| governance/standards_governance/generate_standard_family_registry.py | 标准族册 | --check | — | — | 绿 | 特征表 |
| governance/d3_metadata/generate_derived_files.py | 多派生件分发器 | --check --diff | — | — | 黄 | :220 原子写 |
| governance/d3_metadata/generate_rule_catalog.py | catalogs/rule_catalog_registry.yaml | 无（幂等跳写内置） | — | :244 gen_ts | 绿（内容零变跳写，:INVARIANTS 2026-09-13 Owner 令） | 头部 INVARIANTS |
| governance/d3_metadata/generate_data_asset_coverage.py | data_asset_registry.yaml datasets 段 | --check | — | now_utc | **红**（DatabaseService CH 只读，INVARIANTS 明示零写库） | 头部 |
| context/generate_architecture_context.py | src/zephyr/context-engine/architecture-context.json | 无 | — | :85 | 黄 | :113 |
| backtest/generate_backtest_backlog.py | 回测 backlog 册 | --check | — | :265 | 黄 | :265 |
| backtest/generate_framework_plan_from_tdm.py | config/framework_plans.yaml | --check | — | — | 绿 | 头部 CONSUMERS |
| generate_pathway_registry.py（scripts 根） | pathway 册 | --check | — | — | 黄 | :244 |
| mcp/generate_ide_config.py | config/ IDE 配置 | 无 | — | — | 黄 | 特征表 |
| governance/meta_question/wo008/generate_product_synonym_register.py | data/registers/... | 无 | — | — | 黄 | 特征表 |

#### 2.1.2 关键横切事实

- **--check 已有 16 台、--dry-run 8 台、--output 旗标至少 4 台**（gate_registry / script_manifest / registry_master_index / commit_guide）——隔离重生成的基础设施半成品存在，缺的是统一调度与机械比对。
- **时间戳双态**：d5 族已用"幂等日期源"（git commit 日期）治好再生噪音；D1/D3 清单族仍嵌墙钟但写侧用 `atomic_write_if_changed(volatile_line_pattern=...)` 豁免（`generate_gate_registry.py:794`、`generate_registry_master_index.py:248-249`）——**归一化先例已立，直接复用该模式**。
- **弱校验**：`generate_gate_registry.py --check` 只比对 `total_gates` 计数（:785-789），门数相同但单门字段被手改不报——全量 diff 比对是净增量。
- **generate_manifest.py 无 --check**：全树清单 `scripts/script-manifest.yaml` 完全在 regen 验证之外，且现场遗留原子写残渣 `scripts/script-manifest.yaml.35456.tmp`（09-24）与 `.40056.tmp`（09-23）+ 工作树 `M` 状态（本会话 `git status` 实测；残渣清偿归 S2，此处登记证据）。

#### 2.1.3 apply_* 族（50 台）定位

`scripts/ch/apply_*_ddl.py`（约 30 台 ClickHouse DDL）、`ai_layer/` `entity_graph/` `industry_graph/` DDL、`governance/apply_depgraph|dataflowgraph|decisiongraph|battle_map|resource_plan.py`、`ch/apply_rbac.py`——全部是 **RULE-SSOT"架构=DB"的真源写入工具，不是派生生成器**，一律划出 regen-clean 范围（红级，禁自动跑）；其中 `apply_depgraph.py --add-design-node` 是宪法 §0.5 施工前置仪式，属另一条链。`generator_registry.yaml:21-29` 的"禁止注册清单"判据（产出真源者禁登记）与本分级一致。

### 2.2 生成物普查与陈旧度抽查（3/3 漂移）

**归属判定**：`git ls-files '*.md' | grep index.md` = **1,125 个**；含 `generate_missing_index_md` 标记的 md = **1,128 个**（grep -rl 实测）→ index.md 全族唯一生成者=该台。另有第二层更新者 `auto_generate_index.py`（GATE-INDEX，--apply 外科式更新计数+文件表），但该台**当前直接运行即崩**（import 顺序倒挂，2.1.1 表），等于第二层维护实际停摆。

**抽查方法（可复现）**：取 index.md 中可机械核验的声明（计数/文件表行），与 `ls`/`find` 盘面逐项对；生成物对"删了重生成会得到什么"做思维实验核对模板。

| # | 受检件 | 声明 | 盘面实况 | 判定 |
|---|---|---|---|---|
| 1 | docs/01_policies_and_standards/_registry/catalogs/index.md（summary, date 2026-08-17） | "实测 64 份登记表 YAML" | `find catalogs -maxdepth 1 -name '*.yaml'` = **76** | 陈旧（差 12） |
| 2 | docs/index.md（updated 2026-09-20） | 文件表列 6 个目录（01/02/03/_audit/_working/ROOR） | docs/ 下实有 **7** 个目录——**library/ 整目录缺席表外** | 陈旧 |
| 3 | catalogs/registry_master_index.yaml | 生成器 --check 自证 | `DRIFT: 磁盘 58 张登记表 ≠ 生成 61 张` | **活漂移**（当场复现） |

另：`generate_missing_index_md.py --dry-run --warn-only` 实报 **249 个目录缺 index.md**（docs/_working/ 为主）——补缺语义下"缺失"是常态输入，不算漂移，但说明该族只能"补缺"不能"保鲜"。

**--check 实跑记录（全部只读模式）**：gate_registry `OK: 门禁登记表与三源一致`（exit 0）；script_manifest `OK: 脚本清单与实际一致（516 个脚本）`+`WARNING: 104/516 缺 __manifest__ 块`；registry_master_index `DRIFT 58≠61`（如上）。

### 2.3 门挂接现状（GATE-21 家族）

- pre-commit 侧：`.pre-commit-config.yaml:688-694` `gate-21-manifest-drift`，entry=`python scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py --check`，`files:` 正则触发（script_manifest.yaml + catalogs/*.yaml + .pre-commit-config.yaml + commit_gates/*.py）——**触发面设计正确，可直接抄**。
- 但该链两个断点：a) pre-commit 被 gateway `--no-verify` 系统性绕过（2.0 事实 3）；b) GATE-21 的 --check 只串了 2 台生成器（`validate_static_manifest_drift.py` 头部 docstring：script_manifest + gate_registry），且 gate_registry 侧是计数级弱校验。
- reconciler 侧：`src/zephyr/gov_drift/_detector_registry.yaml:26-30` `static_manifest_drift`（severity HIGH，category generators）经 `_VALIDATOR_SCRIPT_MAP`（`src/zephyr/gov_drift/reconciler.py:52-57`）事件触发同台——修生不修检。
- 既有自愈证据：`generate_gate_registry.py:23-25` post-commit reconciler（priority=830）自动重生成 + auto_commit——**"生成侧自动化"已有，缺的正是独立的"验证侧机械对账"（regen-clean），即本线要补的那半环**。

## ③ 六向台账

| 向 | 内容 | 证据 |
|---|---|---|
| **真源** | 每台生成器吃自己的真源：gate_registry←.pre-commit-config.yaml+commit_gates/*.py+MANUAL_GATES 三源（generate_gate_registry.py:20-25,99）；script_manifest←`__manifest__` 块（generate_script_manifest.py:19-44）；registry_master_index←catalogs 各册 frontmatter；library 8 页←pg:lib_assets（generator_registry.yaml:355-370）；index.md 族←目录盘面+ttl_vocabulary.yaml 判定树（generate_missing_index_md.py:63-79）。**判真源方向铁律**：d5 族与 depgraph/path_tree 是"真源写入方"，非派生（generator_registry.yaml:21-29 禁止注册清单） | 各 file:line |
| **写者** | 正常写=生成器自身（经 reconciler 事件触发或人工）；非法写=任何手工 Edit 生成物（宪法 9.5"静态清单禁手工维护"+骨架公理③"手写即漂移"）。删生成物受 `derived_file_deletion_gate.py`（gate_id="DERIVED-FILE-DELETION-PROTECTION"，`_PROTECTED_DERIVED_FILES` frozenset，:45-52）硬拦，逃生=--allow-derived-deletion | derived_file_deletion_gate.py:8,:45-52 |
| **消费者** | gate_registry.yaml←run_gate_chain/各门自描述（:75-92 CATEGORY_MAP）；script_manifest.yaml←GATE-19/21 validate_static_manifest_drift + generate_script_manifest.py:47-56 双清单分工注记（governance 子集 vs 全树，消费链不同，**禁以"统一 SSoT"为由合并**——已立法）；script-manifest.yaml←GitCommitGateway _post_commit_reconcile+audit_registration；registry_master_index.yaml←catalogs/index.md 导航声明（catalogs/index.md:"权威清单不手写"段）；library 8 页←AI 冷冷启动链（AGENTS.md→docs/library） | 各 file:line |
| **漂移史** | ①今日活漂移 registry_master_index 58≠61；②catalogs/index.md 26 条 vs 实测 64 条的 v2.3 手写清单事故（catalogs/index.md summary 自述"漂移率 63%"，促成 v2.4 废手写）；③GATE-21 三断点史：blueprint_registry.yaml 三次被误删（derived_file_deletion_gate.py:23-27）→ 催生删除保护门；④auto_generate_index.py import 倒挂致 GATE-INDEX 停摆；⑤script-manifest.yaml 原子写残渣 tmp×2 | 各 file:line+本会话实测 |
| **冲突面** | a) st-p1b-libr 正改 library reconciler 族——**本线 regen-clean 落独立检查器 `scripts/governance/d1_structure/regen_clean_check.py`，不碰 library_regen_reconciler.py / reconciliation_registry.py**（骨架 §五避让图）；b) generator_registry.yaml 是 reconcile_generators 的读侧表——本线只**追加** regen 字段与 trigger_sources:[] 条目，不改既有字段语义（该表 :13-19 声明"只读此表禁止反向写入"指 reconcile 不回写，人/施工增条是其正常进化方式）；c) 主区 511 脏文件不 claim（骨架 §五）；d) 与 GATE-21 分工：GATE-21 管"真源变了忘再生"（input 侧），FMS-REGEN-CLEAN 管"生成物被手改"（output 侧），零重叠 | generator_registry.yaml:13-19,:21-29 |
| **净零方案** | 不新建对账配置册：**受检对清单收敛进既有 `generator_registry.yaml`**（该表本就是"生成器→输入/输出"唯一真源，regen 字段是同域扩展非同域重复）；同时承接 `derived_file_deletion_gate.py:8` P1.5 待办"受保护清单迁移 YAML 真源"——一处 YAML 两台消费（检查器+删除门），登记为"合并了 derived_file_deletion_gate._PROTECTED_DERIVED_FILES frozenset 的未来迁移位"；检查器复用 `_shared/file_utils.py` volatile_line_pattern 归一化先例与 `_diff_helpers.py` own-scope 原语，零新原语 | generator_registry.yaml:1-19;derived_file_deletion_gate.py:8;_diff_helpers.py:536 |

## ④ 施工处方（B4 施工批照此落码）

### 4.1 受检对清单（数据先行，合 generator_registry.yaml）

`docs/01_policies_and_standards/_registry/catalogs/generator_registry.yaml` 每条目追加可选 `regen:` 节；首批入库对（P1 波次只收绿/黄 + 首批即产生棘轮基线）：

```yaml
  - name: gate_registry            # 追加字段示例（既有条目若登记则补 regen 节）
    regen:
      tier: green                  # green=纯读仓文件 | yellow=写文件可 --output 隔离 | red=DB/外部禁自动跑
      invoke: "scripts/governance/generators/generate_gate_registry.py --output {iso_out}"
      normalize: ["volatile_lines", "yaml_canonical"]   # 归一化策略键（§4.3）
      timeout_seconds: 10
      enabled: true
```

首批 6 对：gate_registry（绿）、governance/script_manifest（绿）、registry_master_index（绿）、rule_catalog_registry（绿，幂等跳写内置）、commit_navigation_playbook（绿）、script-manifest.yaml（黄，无 --check 无 --output，需施工时补 --output 旗标或首批评为 `enabled: false` + 登记）；library 8 页与 d5 族全部登记为 `tier: red, enabled: false, skip_reason: pg-depgraph`。同批把 index.md 族登记为**结构对账型**（`mode: structural`，见 4.4）。

### 4.2 检查器规格：`scripts/governance/d1_structure/regen_clean_check.py`

- **定位**：只读盘面 + 隔离重生成 + 比对报告；**绝不改盘面、绝不改工作树**（唯一写动作=报告落 `.runtime/gate_audit/regen_clean/`）。D1 域，14 字段头部标注 + `__manifest__` 块 + creation_token 先行批 + add_module_translation 登记 + depgraph 设计节点登记（骨架 §六仪式链 2-5）。
- **输入**：generator_registry.yaml 中带 `regen:` 节的条目；CLI 触发的子集过滤。
- **执行序（每对）**：① 触发判定（staged 文件 ∩ 该对 input_sources∪output_globs∪生成器自身路径）→ ② red 或 enabled:false → 跳过并登记 skip 记录 → ③ subprocess 执行 invoke，`{iso_out}` 替换为 `.runtime/tmp/regen_clean/<run_id>/<output名>`（运行前清该 run 目录；.runtime/tmp 卫生位符合宪法 9.4）→ ④ 产出与盘面正本各走归一化（§4.3）→ ⑤ unified diff → ⑥ 判定 + 落 jsonl。
- **CLI 契约**：

```
python scripts/governance/d1_structure/regen_clean_check.py \
  --check                          # 门模式：只报不写盘面（默认）
  --staged <f1,f2,...>             # 触发过滤（pre-commit 传 staged 清单）
  --pairs nameA,nameB              # 显式指定受检对（调试/全量巡检用 --pairs '*'）
  --baseline <yaml>                # 棘轮基线（默认 catalogs/regen_clean_baseline.yaml）
  --jsonl <path>                   # 机器可读报告（默认 .runtime/gate_audit/regen_clean/<ts>.jsonl）
  --budget-ms 8000                 # 单对 subprocess 上限；超时=该对 fail-open 记 timeout
  --auto-fix                       # 【人工 CLI 专用】把隔离产出拷回正本位；门模式永不含此参
退出码：0=净/全跳过；1=检出漂移；2=基建故障（生成器崩/超时，配合 fail-open 语义）
```

- **输出**：jsonl 每行 `{run_id, pair, tier, verdict: clean|drift|skip|error, diff_hash, diff_excerpt[<=20 行], elapsed_ms}`；人读摘要打印 drift 对清单+修复指令（`--auto-fix` 或裸跑生成器）。

### 4.3 归一化策略（时间戳噪音治理）

1. **volatile 行剔除**（复用 `atomic_write_if_changed` 的 volatile_line_pattern 先例，generate_registry_master_index.py:249 已双模式 `^# 自动生成于 .*$|^generated_at: .*$`）：全局默认剔除 `^generated_at:`、`^# 自动生成于`、`^updated:`、`^created:`、`^saved_at:`、`^date:` 行，对级可增删。
2. **YAML 规范形比对**：双方 `yaml.safe_load` → 删 volatile 键（generated_at/saved_at 等声明于 regen.normalize）→ `json.dumps(sort_keys=True, ensure_ascii=False)` 比对——天然免疫键序与行序漂移，比行 diff 严。
3. **MD 行比对**：CRLF→LF、去 volatile 行后逐行比；BOM 剥离。
4. **结构性对账**（index.md 族用，`mode: structural`）：不重生成正本（该族只补缺、无法重现已存在文件），改为核验"每文件表行 ∩ 盘面条目"双向覆盖——即把 `auto_generate_index.py --check` 的设计意图（:42-47 "Compare index.md facts against disk reality"）收编为本检查器的一个 mode，顺手修好其 import 倒挂（:39 import 移到 :63 sys.path 注入之后，一行序修复）。
5. **棘轮基线**：`catalogs/regen_clean_baseline.yaml` 存 {pair: diff_hash} 已知漂移指纹，**只减不增**（骨架公理①）；baseline 外 drift=硬拦，baseline 内=warn+审计。首批基线数据由施工批首跑 `--pairs '*'`（仅绿/黄）生成。

### 4.4 门挂接处方：FMS-REGEN-CLEAN（双轨）

**轨 A（主 enforcement）in-process CommitGate**：`src/zephyr/gov_enforcement/commit_gates/regen_clean_gate.py`，`GateSpec(gate_id="FMS-REGEN-CLEAN", check=closure, priority=47)`（46=删除保护之后、50=HELD-OVERLAP 之前，同层"commit 安全性"带，derived_file_deletion_gate.py:139-142 同款论证）。check 闭包：

1. own-scope 取范围：`_diff_helpers._build_own_scope(gateway, files, session_id)`（:536，含 held_files 并集与 fail-open 红线）；
2. 范围 ∩ 各对 output_globs（模块级缓存读 generator_registry.yaml，进程内 <50ms）——**只对"本次 diff 触碰了生成物正本"的对触发**（input 侧"忘再生"归 GATE-21+reconciler，零重叠）；
3. 空交集 → `(True, "")` 直通（典型 AI 提交 0 对触发，门开销 <0.3s）；
4. 非空 → subprocess 调 regen_clean_check.py `--staged <own_scope 交集>` `--budget-ms 8000`；
5. ERROR_CONTRACT（照家族成文法，derived_file_deletion_gate.py:13 + depgraph_freshness_gate.py:8）：检出 baseline 外 drift → fail-closed；生成器崩溃/超时/registry 读失败 → **fail-open + jsonl 审计**（家族先例："git diff 不可达 fail-open"、"cache 缺失放行"——基建故障不卡死工作流，但留痕进棘轮周审）；红级对永不触发。
6. 外来 staged 命中 → `_audit_foreign_staged` 同款 warn+审计，不阻断无辜提交人（宪法 §3.1）。

**轨 B（人工 git 流）pre-commit entry**：照抄 GATE-21 形态（.pre-commit-config.yaml:688-694），`files:` 正则只指生成物正本（首批：`^(scripts/governance/script_manifest.yaml|scripts/script-manifest.yaml|docs/01_policies_and_standards/_registry/catalogs/(gate_registry|registry_master_index|rule_catalog_registry)\.yaml|docs/library/(INDEX|code|data|doc|rule|gate|pipeline|backup)\.md)$`——注意 library md 属红级对，pre-commit 轨对它做 structural 覆盖校验而非 PG 重生成）。

**耗时预算（对宪法门禁链 P50 43s 红线，本门 <10s）**：0 对触发（>95% 提交）≈0.3s（registry 缓存解析+交集）；1 对绿级 2-8s（gate_registry 实测秒级、script_manifest 全树扫描实测约 3-5s）；硬顶=--budget-ms 8000 超时即 fail-open；>2 对同时触发按 elapsed 估算升序跑、溢出对降级 warn+审计（不静默）。

### 4.5 施工序（骨架 §六仪式链映射）

creation_token 批（batch_creation_tokens.py）→ 落 `regen_clean_check.py` + `regen_clean_gate.py` + generator_registry.yaml regen 节 + baseline.yaml（4 新件各登记）→ add_module_translation ×2 → apply_depgraph --add-design-node → gate_registry.yaml 由 reconciler 自动再生（禁手改，骨架 §六.6）→ pre-commit entry 与 in-process gate 同批 → 自测（tests/ 豁免 creation_token）：红=夹具（手改 gate_registry 单字段——专杀 2.1.2 弱校验盲区；时间戳-only 差异应判 clean）、蓝=净提交必过。提交走 `git_commit.py --session st-fms-chief-20260927`。

## ⑤ 自审闸三态

- **挖干**：58 台生成器全名单+分级表（2.1）、生成物归属+3/3 抽查漂移实证（2.2）、检查器完整规格+CLI 契约（4.2-4.3）、双轨门挂接含触发正则与耗时预算（4.4）、净零方案（③）、仪式链映射（4.5）齐备；施工代理拿簿可直接开工。
- **留痕缺口（不影响开工，施工批内消解）**：① 26 台 d5 红级对的逐台 output_globs 未逐条誊抄——已在 generator_registry.yaml 在册，施工时按表读取即可（本簿 2.1.1 只给族级判定）；② generate_manifest.py 缺 --output 旗标，施工批需补旗标或首批评 enabled:false（4.1 已列两案）；③ 104/516 缺 __manifest__ 警告的清偿属 S4 计数回填域，本线只登记不扩权。
- **无受阻项**：避让面（library reconciler 族、511 脏文件、幻影引用队）已全部绕开（③冲突面向）。
